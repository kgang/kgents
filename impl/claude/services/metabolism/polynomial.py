"""
Metabolic Session Polynomial: State machine for the developer day.

Checkpoint 0.3 of Metabolic Development Protocol.

The Session polynomial models the complete development cycle:
- Positions: {DORMANT, GREETING, HYDRATED, WORKING, COMPOSTING, REFLECTING}
- Directions: Valid commands at each position
- Transition: State × Command → (NewState, Output)

Key Design Principles:
1. GREETING subsumes Coffee (Coffee is a phase, not a separate system)
2. HYDRATION integrates Living Docs + Brain vectors
3. COMPOSTING captures learnings for future hydration
4. REFLECTING closes the loop for next morning

Teaching:
    gotcha: Unlike Coffee which is strictly linear, Session allows
            jumping back (WORKING → HYDRATED for re-contextualization).
            This models the real workflow: deep work → stuck → re-hydrate.
            (Evidence: test_polynomial.py::test_rehydrate_during_work)

AGENTESE: time.metabolism.session
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, FrozenSet

from agents.poly.protocol import PolyAgent

from .types import (
    CompostEntry,
    EnergyLevel,
    SessionEvent,
    SessionMetadata,
    SessionOutput,
    SessionState,
    WorkMode,
)

# =============================================================================
# Direction Functions (Valid Commands per State)
# =============================================================================


def session_directions(state: SessionState) -> FrozenSet[Any]:
    """
    Valid commands for each Session state.

    Law: "abort" is valid in every non-DORMANT state (graceful exit).
    Law: "status" is valid everywhere (introspection).
    """
    base_cmds: frozenset[str] = frozenset({"abort", "status"})

    match state:
        case SessionState.DORMANT:
            # Can begin a new session or quick-start
            return base_cmds | frozenset({"begin", "quick_start"})

        case SessionState.GREETING:
            # Coffee ritual commands + skip to hydrate
            return base_cmds | frozenset(
                {
                    "complete_greeting",  # Coffee ritual done
                    "skip_to_hydrate",  # Skip Coffee
                    "coffee_continue",  # Delegate to Coffee polynomial
                }
            )

        case SessionState.HYDRATED:
            # Ready to work or need more context
            return base_cmds | frozenset(
                {
                    "start_work",  # Begin working phase
                    "rehydrate",  # Need more context
                    "set_task",  # Set/change task focus
                }
            )

        case SessionState.WORKING:
            # Deep work state
            return base_cmds | frozenset(
                {
                    "checkpoint",  # Save progress
                    "rehydrate",  # Need context refresh
                    "compost",  # Ready to end session
                    "log_energy",  # Track energy level
                }
            )

        case SessionState.COMPOSTING:
            # Capturing learnings
            return base_cmds | frozenset(
                {
                    "add_learning",  # Add a gotcha/insight
                    "finish_compost",  # Done capturing
                    "skip_reflect",  # Skip reflection, end session
                }
            )

        case SessionState.REFLECTING:
            # Session review
            return base_cmds | frozenset(
                {
                    "complete",  # Finish reflection, return to dormant
                    "linger",  # Stay in reflection
                }
            )

    return base_cmds


# =============================================================================
# Transition Function
# =============================================================================


def session_transition(
    state: SessionState,
    input: Any,
) -> tuple[SessionState, SessionOutput]:
    """
    Session state transition function.

    transition: State × Input → (NewState, Output)

    This is the heart of the Metabolic Session polynomial.
    """
    cmd = _extract_command(input)
    data = _extract_data(input)

    # Universal commands
    if cmd == "abort":
        return SessionState.DORMANT, SessionOutput(
            status="aborted",
            state=SessionState.DORMANT,
            message="Session aborted. Rest well.",
        )

    if cmd == "status":
        return state, SessionOutput(
            status="ok",
            state=state,
            message=f"Current state: {state.name}",
        )

    # State-specific transitions
    match state:
        case SessionState.DORMANT:
            return _handle_dormant(cmd, data)

        case SessionState.GREETING:
            return _handle_greeting(cmd, data)

        case SessionState.HYDRATED:
            return _handle_hydrated(cmd, data)

        case SessionState.WORKING:
            return _handle_working(cmd, data)

        case SessionState.COMPOSTING:
            return _handle_composting(cmd, data)

        case SessionState.REFLECTING:
            return _handle_reflecting(cmd, data)

    return state, SessionOutput(
        status="error",
        state=state,
        message=f"Unknown command: {cmd}",
    )


# =============================================================================
# State Handlers
# =============================================================================


def _handle_dormant(cmd: str, data: dict[str, Any]) -> tuple[SessionState, SessionOutput]:
    """Handle DORMANT state transitions."""
    if cmd == "begin":
        # Start with Morning Coffee
        metadata = SessionMetadata(started_at=datetime.now())
        return SessionState.GREETING, SessionOutput(
            status="ok",
            state=SessionState.GREETING,
            metadata=metadata,
            message="☕ Good morning. Let's begin with Coffee...",
        )

    if cmd == "quick_start":
        # Skip greeting, go straight to hydration
        metadata = SessionMetadata(started_at=datetime.now())
        return SessionState.HYDRATED, SessionOutput(
            status="ok",
            state=SessionState.HYDRATED,
            metadata=metadata,
            message="⚡ Quick start. What are we working on?",
        )

    return SessionState.DORMANT, SessionOutput(
        status="error",
        state=SessionState.DORMANT,
        message=f"Unknown command in DORMANT: {cmd}",
    )


def _handle_greeting(cmd: str, data: dict[str, Any]) -> tuple[SessionState, SessionOutput]:
    """Handle GREETING state transitions."""
    if cmd == "complete_greeting":
        # Coffee done, move to hydration
        task_focus = data.get("task_focus")
        voice_captured = data.get("voice_captured", False)

        metadata = SessionMetadata(
            started_at=datetime.now(),
            task_focus=task_focus,
            voice_captured=voice_captured,
            stigmergy_active=voice_captured,
        )

        return SessionState.HYDRATED, SessionOutput(
            status="ok",
            state=SessionState.HYDRATED,
            metadata=metadata,
            message=f"🌿 Coffee complete. Hydrating context for: {task_focus or 'exploration'}",
        )

    if cmd == "skip_to_hydrate":
        # Skip coffee
        metadata = SessionMetadata(started_at=datetime.now())
        return SessionState.HYDRATED, SessionOutput(
            status="skipped",
            state=SessionState.HYDRATED,
            metadata=metadata,
            message="⏭️ Skipping Coffee. What are we working on?",
        )

    if cmd == "coffee_continue":
        # Delegate to Coffee polynomial (stay in GREETING)
        return SessionState.GREETING, SessionOutput(
            status="delegated",
            state=SessionState.GREETING,
            message="☕ Coffee ritual continues...",
            data={"coffee_command": data.get("coffee_command")},
        )

    return SessionState.GREETING, SessionOutput(
        status="error",
        state=SessionState.GREETING,
        message=f"Unknown command in GREETING: {cmd}",
    )


def _handle_hydrated(cmd: str, data: dict[str, Any]) -> tuple[SessionState, SessionOutput]:
    """Handle HYDRATED state transitions."""
    if cmd == "start_work":
        work_mode = WorkMode(data.get("mode", "deep"))
        # Preserve existing metadata
        existing_meta = data.get("metadata")
        if isinstance(existing_meta, SessionMetadata):
            metadata = SessionMetadata(
                started_at=existing_meta.started_at,
                work_mode=work_mode,
                task_focus=existing_meta.task_focus,
                voice_captured=existing_meta.voice_captured,
                stigmergy_active=existing_meta.stigmergy_active,
            )
        else:
            metadata = SessionMetadata(
                started_at=datetime.now(),
                work_mode=work_mode,
            )

        return SessionState.WORKING, SessionOutput(
            status="ok",
            state=SessionState.WORKING,
            metadata=metadata,
            message=f"🔥 Entering {work_mode.value} work mode...",
        )

    if cmd == "rehydrate":
        # Re-contextualize
        task = data.get("task")
        return SessionState.HYDRATED, SessionOutput(
            status="ok",
            state=SessionState.HYDRATED,
            message=f"🌿 Re-hydrating context for: {task or 'current task'}",
            data={"task": task},
        )

    if cmd == "set_task":
        task = data.get("task")
        return SessionState.HYDRATED, SessionOutput(
            status="ok",
            state=SessionState.HYDRATED,
            message=f"🎯 Task set: {task}",
            data={"task_focus": task},
        )

    return SessionState.HYDRATED, SessionOutput(
        status="error",
        state=SessionState.HYDRATED,
        message=f"Unknown command in HYDRATED: {cmd}",
    )


def _handle_working(cmd: str, data: dict[str, Any]) -> tuple[SessionState, SessionOutput]:
    """Handle WORKING state transitions."""
    if cmd == "checkpoint":
        # Save progress, stay in working
        return SessionState.WORKING, SessionOutput(
            status="ok",
            state=SessionState.WORKING,
            message="💾 Checkpoint saved.",
            data={"checkpointed_at": datetime.now().isoformat()},
        )

    if cmd == "rehydrate":
        # Need more context
        task = data.get("task")
        return SessionState.HYDRATED, SessionOutput(
            status="ok",
            state=SessionState.HYDRATED,
            message=f"🌿 Stepping back to re-hydrate: {task or 'current context'}",
            data={"from_working": True},
        )

    if cmd == "compost":
        # Ready to end session, capture learnings
        return SessionState.COMPOSTING, SessionOutput(
            status="ok",
            state=SessionState.COMPOSTING,
            message="🥬 Time to compost. What did you learn?",
        )

    if cmd == "log_energy":
        level = EnergyLevel(data.get("level", "medium"))
        return SessionState.WORKING, SessionOutput(
            status="ok",
            state=SessionState.WORKING,
            message=f"⚡ Energy logged: {level.value}",
            data={"energy_level": level.value},
        )

    return SessionState.WORKING, SessionOutput(
        status="error",
        state=SessionState.WORKING,
        message=f"Unknown command in WORKING: {cmd}",
    )


def _handle_composting(cmd: str, data: dict[str, Any]) -> tuple[SessionState, SessionOutput]:
    """Handle COMPOSTING state transitions."""
    if cmd == "add_learning":
        # Capture a learning
        insight = data.get("insight", "")
        severity = data.get("severity", "info")
        task_context = data.get("task_context")
        evidence = data.get("evidence")

        entry = CompostEntry(
            insight=insight,
            severity=severity,
            task_context=task_context,
            evidence=evidence,
        )

        return SessionState.COMPOSTING, SessionOutput(
            status="ok",
            state=SessionState.COMPOSTING,
            message=f"🌱 Learning captured: {insight[:50]}...",
            compost=[entry],
        )

    if cmd == "finish_compost":
        # Done capturing, move to reflection
        return SessionState.REFLECTING, SessionOutput(
            status="ok",
            state=SessionState.REFLECTING,
            message="🪷 Composting complete. Time to reflect...",
        )

    if cmd == "skip_reflect":
        # Skip reflection, end session
        return SessionState.DORMANT, SessionOutput(
            status="ok",
            state=SessionState.DORMANT,
            message="🌙 Session complete. Rest well.",
        )

    return SessionState.COMPOSTING, SessionOutput(
        status="error",
        state=SessionState.COMPOSTING,
        message=f"Unknown command in COMPOSTING: {cmd}",
    )


def _handle_reflecting(cmd: str, data: dict[str, Any]) -> tuple[SessionState, SessionOutput]:
    """Handle REFLECTING state transitions."""
    if cmd == "complete":
        # Done reflecting, end session
        accomplishment = data.get("accomplished", False)
        return SessionState.DORMANT, SessionOutput(
            status="ok",
            state=SessionState.DORMANT,
            message="🌙 Reflection complete. Rest well."
            if not accomplishment
            else "🎉 Session accomplished! Rest well.",
            data={"accomplished": accomplishment},
        )

    if cmd == "linger":
        # Stay in reflection
        return SessionState.REFLECTING, SessionOutput(
            status="ok",
            state=SessionState.REFLECTING,
            message="🪷 Taking a moment to reflect...",
        )

    return SessionState.REFLECTING, SessionOutput(
        status="error",
        state=SessionState.REFLECTING,
        message=f"Unknown command in REFLECTING: {cmd}",
    )


# =============================================================================
# Helper Functions
# =============================================================================


def _extract_command(input: Any) -> str:
    """Extract command from various input formats."""
    if isinstance(input, str):
        return input
    if isinstance(input, SessionEvent):
        return input.command
    if isinstance(input, dict):
        cmd = input.get("command") or input.get("cmd") or "unknown"
        return str(cmd)
    return "unknown"


def _extract_data(input: Any) -> dict[str, Any]:
    """Extract data from various input formats."""
    if isinstance(input, str):
        return {}
    if isinstance(input, SessionEvent):
        return dict(input.data)
    if isinstance(input, dict):
        return {k: v for k, v in input.items() if k not in ("command", "cmd")}
    return {}


# =============================================================================
# The Polynomial Agent
# =============================================================================


SESSION_POLYNOMIAL: PolyAgent[SessionState, Any, SessionOutput] = PolyAgent(
    name="MetabolicSessionPolynomial",
    positions=frozenset(SessionState),
    _directions=session_directions,
    _transition=session_transition,
)
"""
The Metabolic Session polynomial agent.

This maps the developer day to a polynomial state machine:
- positions: 6 states from DORMANT to REFLECTING
- directions: valid commands per state
- transition: command → state change + output

Usage:
    state = SessionState.DORMANT
    state, output = SESSION_POLYNOMIAL.transition(state, "begin")
    # state is now GREETING, output contains session metadata
"""


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "session_directions",
    "session_transition",
    "SESSION_POLYNOMIAL",
]
