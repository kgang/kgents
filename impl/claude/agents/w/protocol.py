"""
W-gent Wire Protocol Compatibility Layer (Deprecated)

DEPRECATION NOTICE (2025-12):
    This module exists solely for backward compatibility with O-gent.

    The old W-gent wire protocol (file-based .wire/ directories, IPC sockets,
    etc.) has been replaced by:

    - AGENTESE protocol for agent communication
    - Witness marks for traceability
    - K-Block for structured observability

    New code should NOT use WireObservable. Instead:
    - For AGENTESE agents: Use @node decorator + Witness protocol
    - For external processes: Use ProcessObserver from agents.w.observer

    This compatibility shim provides minimal WireObservable functionality
    to keep existing O-gent code working during migration.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class WireObservable:
    """
    Compatibility shim for deprecated wire protocol.

    Provides no-op implementations of old wire protocol methods.
    Exists only to prevent import errors in O-gent during migration.

    DO NOT USE IN NEW CODE.
    """

    def __init__(
        self,
        agent_name: str,
        wire_base: Path | None = None,
    ):
        """
        Initialize wire observability (minimal compatibility mode).

        Args:
            agent_name: Unique identifier for this agent
            wire_base: Base directory for .wire files
        """
        self.agent_name = agent_name
        self.wire_base = wire_base or Path(".wire") / agent_name
        self._state: dict[str, Any] = {}

        # Create directories if wire_base is explicitly set (for tests)
        if wire_base is not None:
            self.wire_base.mkdir(parents=True, exist_ok=True)

    def update_state(self, **kwargs: Any) -> None:
        """
        Update state snapshot (minimal compatibility).

        Old behavior: Write to .wire/{agent}/state.json
        New behavior: Writes minimal state file for test compatibility only
        """
        self._state.update(kwargs)
        self._state["timestamp"] = datetime.now(timezone.utc).isoformat() + "Z"

        # Only write file if wire_base was explicitly set (test mode)
        if self.wire_base.exists():
            state_file = self.wire_base / "state.json"
            with open(state_file, "w") as f:
                json.dump(
                    {
                        "agent": self.agent_name,
                        "timestamp": self._state["timestamp"],
                        "metadata": self._state,
                    },
                    f,
                    indent=2,
                )

    def log_event(self, level: str, stage: str, message: str) -> None:
        """
        Log an event (minimal compatibility).

        Old behavior: Append to .wire/{agent}/stream.log
        New behavior: Appends to stream.log for test compatibility only
        """
        # Only write file if wire_base was explicitly set (test mode)
        if self.wire_base.exists():
            stream_file = self.wire_base / "stream.log"
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            log_line = f"[{timestamp}] [{level}] [{stage}] {message}\n"
            with open(stream_file, "a") as f:
                f.write(log_line)

    def write_metrics(self, **metrics: Any) -> None:
        """
        Write metrics (no-op).

        Old behavior: Write to .wire/{agent}/metrics.json
        New behavior: Nothing (use Witness marks instead)
        """
        pass

    def update_metrics(self, **metrics: Any) -> None:
        """
        Update metrics (no-op).

        Old behavior: Update .wire/{agent}/metrics.json
        New behavior: Nothing (use Witness marks instead)
        """
        pass

    def get_history(self) -> list[dict[str, Any]]:
        """
        Get event history (compatibility shim).

        Returns empty list since we no longer track wire history.
        Use Witness service for observability instead.
        """
        return []

    def emit_snapshot(self, snapshot: Any) -> None:
        """
        Emit a status snapshot (no-op).

        Old behavior: Write snapshot to wire protocol
        New behavior: Nothing (use Witness marks instead)
        """
        pass

    def should_emit(self, snapshot: Any) -> bool:
        """
        Check if snapshot should be emitted (compatibility shim).

        Always returns False since wire protocol is deprecated.
        """
        return False
