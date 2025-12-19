"""
Reflector Protocol - The observer between Runtime and User.

The Reflector manages the "Space Between" - it doesn't execute logic,
it mediates how runtime events reach different surfaces (CLI, TUI, web).

Category Theory:
  The Reflector is a natural transformation from the Runtime functor
  to the Display functor. Multiple Reflector implementations represent
  different choices of Display.

AGENTESE:
  The Reflector maps runtime events to AGENTESE paths:
  - command_start -> time.trace.birth
  - command_end -> time.trace.witness
  - agent_health -> self.*.manifest
  - proposal -> self.intent.propose
"""

from __future__ import annotations

import json
import os
import sys
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import IO, Any, Callable, Protocol, runtime_checkable

from .events import (
    CommandEndEvent,
    CommandStartEvent,
    EventType,
    Invoker,
    RuntimeEvent,
)

# =============================================================================
# Prompt State
# =============================================================================


class PromptState(Enum):
    """Current state of the prompt."""

    QUIET = "quiet"  # Normal: kgents >
    PENDING = "pending"  # Has proposals: kgents [2] >
    CRITICAL = "critical"  # Alert: kgents [! DRIFT] >
    TYPING = "typing"  # Agent typing: kgents [d-gent...] >


@dataclass
class PromptInfo:
    """Information for rendering the prompt."""

    state: PromptState = PromptState.QUIET
    proposal_count: int = 0
    critical_message: str | None = None
    typing_agent: str | None = None

    def render(self) -> str:
        """Render prompt string."""
        if self.state == PromptState.CRITICAL and self.critical_message:
            return f"kgents [! {self.critical_message}] > "
        elif self.state == PromptState.PENDING and self.proposal_count > 0:
            s = "s" if self.proposal_count > 1 else ""
            return f"kgents [{self.proposal_count} proposal{s}] > "
        elif self.state == PromptState.TYPING and self.typing_agent:
            return f"kgents [{self.typing_agent}...] > "
        else:
            return "kgents > "


# =============================================================================
# Invocation Context
# =============================================================================


@dataclass
class InvocationContext:
    """
    Rich context for command invocation.

    This is passed to handlers and carries:
    - Command identity and arguments
    - Who invoked (human, agent, scheduled)
    - Budget tracking
    - Output channels (FD3 for semantic output)
    - Reflector reference for event emission
    """

    # Command identity
    command: str = ""
    args: list[str] = field(default_factory=list)
    invoker: Invoker = Invoker.HUMAN
    trace_id: str = ""

    # Timing
    started_at: datetime = field(default_factory=datetime.now)

    # Channels (FD3 Protocol)
    fd3: IO[str] | None = None  # Semantic side-channel

    # Reflector reference (set by hollow.py)
    reflector: "Reflector | None" = None

    # Accumulated output
    _human_output: list[str] = field(default_factory=list)
    _semantic_output: dict[str, Any] = field(default_factory=dict)

    def emit_human(self, text: str) -> None:
        """
        Write to human channel (FD1/stdout).

        If a reflector is attached, it handles the output.
        Otherwise, prints directly.
        """
        self._human_output.append(text)
        if self.reflector:
            self.reflector.emit_human(text)
        else:
            print(text)

    def emit_semantic(self, data: dict[str, Any]) -> None:
        """
        Write to semantic channel (FD3) if available.

        This is the structured data that agents can parse.
        """
        self._semantic_output.update(data)
        if self.fd3:
            self.fd3.write(json.dumps(data) + "\n")
            self.fd3.flush()
        if self.reflector:
            self.reflector.emit_semantic(data)

    def output(self, human: str, semantic: dict[str, Any]) -> None:
        """
        Emit to both channels atomically.

        This is the preferred way for handlers to output data:
        - human: Pretty text for the terminal user
        - semantic: Structured data for agents/scripts
        """
        self.emit_human(human)
        self.emit_semantic(semantic)

    def get_human_output(self) -> str:
        """Get accumulated human output."""
        return "\n".join(self._human_output)

    def get_semantic_output(self) -> dict[str, Any]:
        """Get accumulated semantic output."""
        return dict(self._semantic_output)

    def elapsed_ms(self) -> int:
        """Get elapsed time in milliseconds."""
        delta = datetime.now() - self.started_at
        return int(delta.total_seconds() * 1000)


# =============================================================================
# Reflector Protocol
# =============================================================================


@runtime_checkable
class Reflector(Protocol):
    """
    The observer between Runtime and User.

    Multiple implementations render to different surfaces:
    - TerminalReflector: stdout + FD3 for CLI
    - FluxReflector: Textual widgets for TUI
    - HeadlessReflector: Memory buffer for tests

    The Reflector does NOT execute logic - it mediates the "Space Between."
    """

    # Event handling
    def on_event(self, event: RuntimeEvent) -> None:
        """Handle any runtime event."""
        ...

    # Output channels
    def emit_human(self, text: str) -> None:
        """Emit human-readable output."""
        ...

    def emit_semantic(self, data: dict[str, Any]) -> None:
        """Emit structured semantic output."""
        ...

    # Prompt management
    def get_prompt_info(self) -> PromptInfo:
        """Get current prompt state information."""
        ...

    def render_prompt(self) -> str:
        """Render the current prompt string."""
        ...

    # Subscription
    def subscribe(self, callback: Callable[[RuntimeEvent], None]) -> None:
        """Subscribe to events (for multi-listener scenarios)."""
        ...

    def unsubscribe(self, callback: Callable[[RuntimeEvent], None]) -> None:
        """Unsubscribe from events."""
        ...


# =============================================================================
# Base Reflector Implementation
# =============================================================================


class BaseReflector(ABC):
    """
    Base implementation of the Reflector protocol.

    Provides common functionality for event sequencing,
    subscription management, and prompt state tracking.
    """

    def __init__(self) -> None:
        self._sequence = 0
        self._subscribers: list[Callable[[RuntimeEvent], None]] = []
        self._prompt_info = PromptInfo()
        self._proposal_count = 0
        self._critical_alerts: list[str] = []

    def _next_sequence(self) -> int:
        """Get next event sequence number."""
        self._sequence += 1
        return self._sequence

    def on_event(self, event: RuntimeEvent) -> None:
        """Handle any runtime event."""
        # Assign sequence number
        event = event.with_sequence(self._next_sequence())

        # Update prompt state based on event
        self._update_prompt_state(event)

        # Dispatch to implementation
        self._handle_event(event)

        # Notify subscribers
        for callback in self._subscribers:
            try:
                callback(event)
            except Exception:
                pass  # Don't let subscriber errors break the reflector

    def _update_prompt_state(self, event: RuntimeEvent) -> None:
        """Update prompt state based on event."""
        if event.event_type == EventType.PROPOSAL_ADDED:
            self._proposal_count += 1
            priority = event.data.get("priority", "normal")
            if priority == "critical":
                msg = event.data.get("action", "ALERT")[:20]
                self._critical_alerts.append(msg)
        elif event.event_type == EventType.PROPOSAL_RESOLVED:
            self._proposal_count = max(0, self._proposal_count - 1)
        elif event.event_type == EventType.ERROR:
            if not event.data.get("recoverable", True):
                self._critical_alerts.append(event.data.get("error_code", "ERROR")[:20])

        # Update prompt info
        if self._critical_alerts:
            self._prompt_info = PromptInfo(
                state=PromptState.CRITICAL,
                critical_message=self._critical_alerts[0],
            )
        elif self._proposal_count > 0:
            self._prompt_info = PromptInfo(
                state=PromptState.PENDING,
                proposal_count=self._proposal_count,
            )
        else:
            self._prompt_info = PromptInfo(state=PromptState.QUIET)

    @abstractmethod
    def _handle_event(self, event: RuntimeEvent) -> None:
        """Implementation-specific event handling."""
        ...

    @abstractmethod
    def emit_human(self, text: str) -> None:
        """Emit human-readable output."""
        ...

    @abstractmethod
    def emit_semantic(self, data: dict[str, Any]) -> None:
        """Emit structured semantic output."""
        ...

    def get_prompt_info(self) -> PromptInfo:
        """Get current prompt state information."""
        return self._prompt_info

    def render_prompt(self) -> str:
        """Render the current prompt string."""
        return self._prompt_info.render()

    def subscribe(self, callback: Callable[[RuntimeEvent], None]) -> None:
        """Subscribe to events."""
        if callback not in self._subscribers:
            self._subscribers.append(callback)

    def unsubscribe(self, callback: Callable[[RuntimeEvent], None]) -> None:
        """Unsubscribe from events."""
        if callback in self._subscribers:
            self._subscribers.remove(callback)

    def clear_alerts(self) -> None:
        """Clear critical alerts (after user acknowledgment)."""
        self._critical_alerts.clear()
        self._update_prompt_state(RuntimeEvent(event_type=EventType.INFO, source="reflector"))


# =============================================================================
# Context Factory
# =============================================================================


def create_invocation_context(
    command: str,
    args: list[str] | None = None,
    invoker: Invoker = Invoker.HUMAN,
    reflector: Reflector | None = None,
    fd3_path: str | None = None,
) -> InvocationContext:
    """
    Create an InvocationContext with optional FD3 channel.

    Args:
        command: The command being invoked
        args: Command arguments
        invoker: Who invoked the command
        reflector: Reflector to attach
        fd3_path: Path for FD3 semantic output (or from KGENTS_FD3 env var)
    """
    import uuid

    # Check for FD3 env var
    fd3_path = fd3_path or os.environ.get("KGENTS_FD3")
    fd3: IO[str] | None = None

    if fd3_path:
        try:
            fd3 = open(fd3_path, "w")  # noqa: SIM115
        except OSError:
            pass  # Silently fail if can't open FD3

    return InvocationContext(
        command=command,
        args=args or [],
        invoker=invoker,
        trace_id=str(uuid.uuid4())[:8],
        reflector=reflector,
        fd3=fd3,
    )


def close_invocation_context(ctx: InvocationContext) -> None:
    """Close resources associated with an InvocationContext."""
    if ctx.fd3:
        try:
            ctx.fd3.close()
        except Exception:
            pass
