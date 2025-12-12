"""
Terminal Reflector - CLI-specific implementation.

Renders events to stdout (FD1) for humans and optionally
to FD3 (semantic channel) for agents/scripts.

This is the default Reflector used by hollow.py when running
in a terminal environment.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import IO, Any, TextIO

from .events import (
    CommandEndEvent,
    CommandStartEvent,
    EventType,
    RuntimeEvent,
)
from .protocol import BaseReflector, PromptInfo


class TerminalReflector(BaseReflector):
    """
    Reflector for terminal/CLI output.

    Features:
    - Human output to stdout (FD1)
    - Optional semantic output to file (FD3 protocol)
    - Event logging to stderr in verbose mode
    - Prompt state management
    """

    def __init__(
        self,
        stdout: TextIO | None = None,
        stderr: TextIO | None = None,
        fd3_path: str | None = None,
        verbose: bool = False,
    ) -> None:
        """
        Initialize the terminal reflector.

        Args:
            stdout: Output stream for human text (default: sys.stdout)
            stderr: Output stream for diagnostics (default: sys.stderr)
            fd3_path: Path for FD3 semantic output (or from KGENTS_FD3 env var)
            verbose: If True, emit event diagnostics to stderr
        """
        super().__init__()
        self._stdout = stdout or sys.stdout
        self._stderr = stderr or sys.stderr
        self._verbose = verbose

        # FD3 setup
        self._fd3_path = fd3_path or os.environ.get("KGENTS_FD3")
        self._fd3: IO[str] | None = None
        self._fd3_buffer: list[dict[str, Any]] = []

        if self._fd3_path:
            try:
                self._fd3 = open(self._fd3_path, "w")  # noqa: SIM115
            except OSError as e:
                if self._verbose:
                    print(f"[reflector] Failed to open FD3 at {self._fd3_path}: {e}", file=self._stderr)

    def _handle_event(self, event: RuntimeEvent) -> None:
        """Handle runtime events."""
        if self._verbose:
            self._log_event(event)

        # Write to FD3 if available
        if self._fd3:
            self._write_fd3_event(event)

    def _log_event(self, event: RuntimeEvent) -> None:
        """Log event to stderr in verbose mode."""
        timestamp = event.timestamp.strftime("%H:%M:%S.%f")[:-3]
        print(
            f"\033[90m[{timestamp}] {event.event_type.value} from {event.source}\033[0m",
            file=self._stderr,
        )

    def _write_fd3_event(self, event: RuntimeEvent) -> None:
        """Write event to FD3 semantic channel."""
        if not self._fd3:
            return

        record: dict[str, Any] = {
            "event": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "source": event.source,
            "sequence": event.sequence,
            "data": event.data,
        }

        # Add type-specific fields
        if isinstance(event, CommandStartEvent):
            record["command"] = event.command
            record["args"] = list(event.args)
            record["invoker"] = event.invoker.value
            record["trace_id"] = event.trace_id
        elif isinstance(event, CommandEndEvent):
            record["command"] = event.command
            record["exit_code"] = event.exit_code
            record["duration_ms"] = event.duration_ms
            record["trace_id"] = event.trace_id
            record["semantic"] = event.semantic_output

        try:
            self._fd3.write(json.dumps(record) + "\n")
            self._fd3.flush()
        except Exception:
            pass  # Don't let FD3 errors break the reflector

    def emit_human(self, text: str) -> None:
        """
        Emit human-readable output to stdout.

        This is the primary output channel for terminal users.
        """
        print(text, file=self._stdout)

    def emit_semantic(self, data: dict[str, Any]) -> None:
        """
        Emit structured semantic output.

        If FD3 is configured, writes to the semantic channel.
        Also buffers for later retrieval.
        """
        self._fd3_buffer.append(data)

        if self._fd3:
            try:
                self._fd3.write(json.dumps(data) + "\n")
                self._fd3.flush()
            except Exception:
                pass

    def get_semantic_buffer(self) -> list[dict[str, Any]]:
        """Get all buffered semantic output."""
        return list(self._fd3_buffer)

    def clear_semantic_buffer(self) -> None:
        """Clear the semantic buffer."""
        self._fd3_buffer.clear()

    def close(self) -> None:
        """Close the reflector and any open resources."""
        if self._fd3:
            try:
                self._fd3.close()
            except Exception:
                pass
            self._fd3 = None

    def __enter__(self) -> "TerminalReflector":
        """Context manager entry."""
        return self

    def __exit__(self, *args: Any) -> None:
        """Context manager exit."""
        self.close()


# =============================================================================
# Factory Functions
# =============================================================================


def create_terminal_reflector(
    verbose: bool = False,
    fd3_path: str | None = None,
) -> TerminalReflector:
    """
    Create a TerminalReflector with standard configuration.

    Args:
        verbose: Enable verbose event logging
        fd3_path: Override FD3 path (otherwise uses KGENTS_FD3 env var)
    """
    return TerminalReflector(
        verbose=verbose,
        fd3_path=fd3_path,
    )


def get_default_reflector() -> TerminalReflector:
    """
    Get the default reflector for CLI use.

    Checks KGENTS_FD3 env var for semantic output path.
    Checks KGENTS_VERBOSE for verbose mode.
    """
    verbose = os.environ.get("KGENTS_VERBOSE", "").lower() in ("1", "true", "yes")
    return create_terminal_reflector(verbose=verbose)
