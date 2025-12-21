"""
Session-Walk Bridge: Connects CLI Sessions to WARP Walks.

This module bridges two distinct primitives:
- CLISession: Tracks CLI session state (interactive, flow, script)
- Walk: Tracks WARP work stream with Marks and N-Phase

Philosophy:
    Not every CLI session needs a Walk. A simple `kg check` doesn't need
    workflow tracking. But when a session involves sustained work (interactive
    REPL, flow execution, multi-step tasks), a Walk provides:
    - Mark history for complete audit trail
    - N-Phase tracking for workflow awareness
    - Forest binding for plan correlation

Design (Constitution-Aligned):
- **Tasteful**: Optional binding—simple commands don't require Walks
- **Composable**: Walk is infrastructure; any Crown Jewel can use it
- **Heterarchical**: Walk can start/pause/resume independently of session

Laws:
- Law 1 (Session Owns Walk): A CLI session can have at most one active Walk
- Law 2 (Walk Outlives Session): Walk persists after session ends (for audit)
- Law 3 (Optional Binding): CLI sessions work without Walks

See: protocols/cli/instance_db/cli_session.py
See: services/witness/walk.py
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .mark import Mark, PlanPath, WalkId
from .walk import Walk, WalkIntent, WalkStatus, WalkStore, get_walk_store

if TYPE_CHECKING:
    from protocols.cli.instance_db import CLISession

logger = logging.getLogger("kgents.witness.session_walk")


# =============================================================================
# Session-Walk Binding
# =============================================================================


@dataclass
class SessionWalkBinding:
    """
    Binding between a CLI session and its Walk.

    Law 1: A CLI session can have at most one active Walk.
    """

    cli_session_id: str
    walk_id: str
    bound_at: str  # ISO timestamp
    unbound_at: str | None = None  # ISO timestamp when unbound
    metadata: dict[str, Any] = field(default_factory=dict)


# =============================================================================
# Session-Walk Bridge
# =============================================================================


class SessionWalkBridge:
    """
    Bridge for connecting CLI sessions to WARP Walks.

    Usage:
        bridge = SessionWalkBridge()

        # Start session with Walk
        walk = bridge.start_walk_for_session(
            cli_session_id="cli_abc123",
            goal="Implement Mark feature",
            root_plan="plans/warp-servo.md",
        )

        # Record work
        bridge.advance_walk(cli_session_id, trace_node)

        # End session (Walk persists for audit)
        bridge.end_session(cli_session_id)
    """

    def __init__(self, walk_store: WalkStore | None = None) -> None:
        """
        Initialize bridge.

        Args:
            walk_store: Optional WalkStore (defaults to global)
        """
        self._walk_store = walk_store or get_walk_store()
        self._bindings: dict[str, SessionWalkBinding] = {}  # session_id -> binding

    # =========================================================================
    # Walk Lifecycle
    # =========================================================================

    def start_walk_for_session(
        self,
        cli_session_id: str,
        goal: str,
        *,
        root_plan: str | PlanPath | None = None,
        session_name: str = "",
    ) -> Walk:
        """
        Create and bind a Walk to a CLI session.

        Law 1: A CLI session can have at most one active Walk.

        Args:
            cli_session_id: CLI session ID
            goal: Goal description for the Walk
            root_plan: Optional Forest plan path
            session_name: Optional name override

        Returns:
            The created Walk

        Raises:
            ValueError: If session already has an active Walk
        """
        # Check existing binding
        existing = self.get_walk_for_session(cli_session_id)
        if existing and existing.is_active:
            raise ValueError(f"Session {cli_session_id} already has active Walk {existing.id}")

        # Create Walk
        plan_path = PlanPath(root_plan) if isinstance(root_plan, str) else root_plan
        walk = Walk.create(
            goal=goal,
            root_plan=plan_path,
            name=session_name or f"Session-{cli_session_id[:8]}",
        )

        # Store and bind
        self._walk_store.add(walk)
        self._bindings[cli_session_id] = SessionWalkBinding(
            cli_session_id=cli_session_id,
            walk_id=str(walk.id),
            bound_at=walk.started_at.isoformat(),
            metadata={"goal": goal},
        )

        logger.info(f"Created Walk {walk.id} for session {cli_session_id}")
        return walk

    def get_walk_for_session(self, cli_session_id: str) -> Walk | None:
        """
        Get the Walk bound to a CLI session.

        Law 3: CLI sessions work without Walks—returns None if no Walk.
        """
        binding = self._bindings.get(cli_session_id)
        if binding is None:
            return None

        return self._walk_store.get(WalkId(binding.walk_id))

    def has_walk(self, cli_session_id: str) -> bool:
        """Check if a CLI session has a Walk bound."""
        return cli_session_id in self._bindings

    # =========================================================================
    # Walk Operations
    # =========================================================================

    def advance_walk(self, cli_session_id: str, trace_node: Mark) -> bool:
        """
        Add a Mark to the session's Walk.

        Returns False if session has no Walk (Law 3: optional binding).
        """
        walk = self.get_walk_for_session(cli_session_id)
        if walk is None:
            logger.debug(f"No Walk for session {cli_session_id}—trace not recorded")
            return False

        if not walk.is_active:
            logger.warning(f"Walk {walk.id} is not active—trace not recorded")
            return False

        walk.advance(trace_node)
        return True

    def transition_phase_for_session(
        self,
        cli_session_id: str,
        to_phase: str,
    ) -> bool:
        """
        Transition the Walk's N-Phase.

        Args:
            cli_session_id: CLI session ID
            to_phase: Target phase name (e.g., "SENSE", "ACT", "REFLECT")

        Returns:
            True if transition succeeded, False if no Walk or invalid
        """
        from .mark import NPhase

        walk = self.get_walk_for_session(cli_session_id)
        if walk is None:
            return False

        try:
            phase = NPhase(to_phase)
        except ValueError:
            logger.warning(f"Invalid phase: {to_phase}")
            return False

        return walk.transition_phase(phase)

    # =========================================================================
    # Session Lifecycle
    # =========================================================================

    def pause_walk(self, cli_session_id: str) -> bool:
        """Pause the Walk when session pauses."""
        walk = self.get_walk_for_session(cli_session_id)
        if walk is None or not walk.is_active:
            return False

        walk.pause()
        logger.info(f"Paused Walk {walk.id} for session {cli_session_id}")
        return True

    def resume_walk(self, cli_session_id: str) -> bool:
        """Resume a paused Walk."""
        walk = self.get_walk_for_session(cli_session_id)
        if walk is None or walk.status != WalkStatus.PAUSED:
            return False

        walk.resume()
        logger.info(f"Resumed Walk {walk.id} for session {cli_session_id}")
        return True

    def end_session(self, cli_session_id: str, *, complete: bool = True) -> Walk | None:
        """
        Handle CLI session end.

        Law 2: Walk persists after session ends for audit.

        Args:
            cli_session_id: CLI session ID
            complete: If True, mark Walk as complete; if False, mark as abandoned

        Returns:
            The Walk if one existed, None otherwise
        """
        walk = self.get_walk_for_session(cli_session_id)
        if walk is None:
            return None

        # Mark Walk
        if complete:
            walk.complete()
        else:
            walk.abandon(reason="Session ended without completion")

        # Update binding
        from datetime import datetime

        binding = self._bindings.get(cli_session_id)
        if binding:
            self._bindings[cli_session_id] = SessionWalkBinding(
                cli_session_id=binding.cli_session_id,
                walk_id=binding.walk_id,
                bound_at=binding.bound_at,
                unbound_at=datetime.now().isoformat(),
                metadata=binding.metadata,
            )

        logger.info(
            f"Ended session {cli_session_id} with Walk {walk.id} ({walk.trace_count()} traces)"
        )
        return walk

    # =========================================================================
    # Statistics
    # =========================================================================

    def active_sessions_with_walks(self) -> list[str]:
        """Get CLI session IDs that have active Walks."""
        active = []
        for session_id, binding in self._bindings.items():
            walk = self.get_walk_for_session(session_id)
            if walk and walk.is_active:
                active.append(session_id)
        return active


# =============================================================================
# Global Bridge
# =============================================================================

_global_bridge: SessionWalkBridge | None = None


def get_session_walk_bridge() -> SessionWalkBridge:
    """Get the global session-walk bridge."""
    global _global_bridge
    if _global_bridge is None:
        _global_bridge = SessionWalkBridge()
    return _global_bridge


def reset_session_walk_bridge() -> None:
    """Reset the global bridge (for testing)."""
    global _global_bridge
    _global_bridge = None


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    "SessionWalkBinding",
    "SessionWalkBridge",
    "get_session_walk_bridge",
    "reset_session_walk_bridge",
]
