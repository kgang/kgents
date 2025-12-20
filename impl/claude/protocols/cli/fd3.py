"""
FD3 - The Semantic Channel.

FD3 is the structured data channel for machine-readable output.
While FD1 (stdout) shows pretty text for humans, FD3 emits JSON
for agents, TUIs, and programmatic consumption.

Architecture:
    ┌─────────────┐       ┌─────────────┐       ┌─────────────┐
    │  CLI (FD1)  │       │   Runtime   │       │  I-gent TUI │
    │  (human)    │◄──────│   (FD3)     │──────►│  (visual)   │
    └─────────────┘       └─────────────┘       └─────────────┘
                                │
                                ▼
                          JSON over file/pipe

Usage:
    # Emit a message
    channel = FD3Channel()
    channel.emit(FD3Message(
        type="agent_update",
        payload={"agent_id": "robin", "phase": "ACTIVE"},
    ))

    # Subscribe to messages
    async for msg in channel.subscribe():
        print(f"Got {msg.type}: {msg.payload}")

Environment:
    KGENTS_FD3 - Path to FD3 output file (optional)
"""

from __future__ import annotations

import asyncio
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Literal

# Environment variable for FD3 output path
FD3_ENV_VAR = "KGENTS_FD3"


class FD3MessageType(Enum):
    """Types of FD3 messages."""

    AGENT_UPDATE = "agent_update"
    HEALTH = "health"
    AGENTESE_INVOKE = "agentese_invoke"
    ERROR = "error"
    STATUS = "status"
    EVENT = "event"


@dataclass
class FD3Message:
    """
    Structured message for the semantic channel.

    Attributes:
        type: Message type (agent_update, health, agentese_invoke, error, etc.)
        payload: Message-specific data
        timestamp: When the message was created
        source: What component emitted this message
        correlation_id: Optional ID for tracking related messages
    """

    type: Literal["agent_update", "health", "agentese_invoke", "error", "status", "event"]
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)
    source: str = ""
    correlation_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to JSON-serializable dict."""
        return {
            "type": self.type,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "correlation_id": self.correlation_id,
        }

    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "FD3Message":
        """Create from dict."""
        return cls(
            type=data["type"],
            payload=data.get("payload", {}),
            timestamp=datetime.fromisoformat(data["timestamp"])
            if "timestamp" in data
            else datetime.now(),
            source=data.get("source", ""),
            correlation_id=data.get("correlation_id", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "FD3Message":
        """Create from JSON string."""
        return cls.from_dict(json.loads(json_str))


# Callback type for FD3 messages
FD3Callback = Callable[[FD3Message], None]


class FD3Channel:
    """
    Reads/writes FD3 messages.

    Supports file-based output for simplicity.
    Future: Can be extended to named pipes for live updates.
    """

    def __init__(self, path: str | Path | None = None) -> None:
        """
        Initialize the FD3 channel.

        Args:
            path: Path to FD3 output file. If None, uses KGENTS_FD3 env var.
                  If neither is set, FD3 output is disabled.
        """
        self._path: Path | None = None
        self._callbacks: list[FD3Callback] = []
        self._file_handle: Any = None
        self._watch_task: asyncio.Task[None] | None = None
        self._last_position: int = 0

        # Resolve path from argument or environment
        if path:
            self._path = Path(path)
        elif FD3_ENV_VAR in os.environ:
            self._path = Path(os.environ[FD3_ENV_VAR])

    @property
    def is_enabled(self) -> bool:
        """Check if FD3 output is enabled."""
        return self._path is not None

    @property
    def path(self) -> Path | None:
        """Get the FD3 output path."""
        return self._path

    def emit(self, msg: FD3Message) -> None:
        """
        Emit a message to FD3.

        Writes JSON line to the output file if enabled.
        Also notifies any local subscribers.
        """
        # Notify local callbacks
        for callback in self._callbacks:
            try:
                callback(msg)
            except Exception:
                pass

        # Write to file if enabled
        if self._path:
            try:
                # Ensure parent directory exists
                self._path.parent.mkdir(parents=True, exist_ok=True)

                # Append JSON line
                with open(self._path, "a") as f:
                    f.write(msg.to_json() + "\n")
            except Exception:
                pass  # Silently fail on write errors

    def subscribe(self, callback: FD3Callback) -> None:
        """Subscribe to FD3 messages (local only)."""
        self._callbacks.append(callback)

    def unsubscribe(self, callback: FD3Callback) -> None:
        """Unsubscribe from FD3 messages."""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    async def read_all(self) -> list[FD3Message]:
        """
        Read all messages from the FD3 file.

        Returns an empty list if file doesn't exist or is empty.
        """
        if not self._path or not self._path.exists():
            return []

        messages: list[FD3Message] = []
        try:
            with open(self._path, "r") as f:
                for line in f:
                    line = line.strip()
                    if line:
                        try:
                            messages.append(FD3Message.from_json(line))
                        except json.JSONDecodeError:
                            pass
        except Exception:
            pass

        return messages

    async def watch(self, poll_interval: float = 0.5) -> AsyncIterator[FD3Message]:
        """
        Watch for new messages (tail -f style).

        Yields new messages as they appear in the file.

        Args:
            poll_interval: How often to check for new messages (seconds)
        """
        if not self._path:
            return

        # Ensure file exists
        if not self._path.exists():
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.touch()

        # Start from current end of file
        with open(self._path, "r") as f:
            f.seek(0, 2)  # Seek to end
            self._last_position = f.tell()

        while True:
            try:
                with open(self._path, "r") as f:
                    f.seek(self._last_position)
                    for line in f:
                        line = line.strip()
                        if line:
                            try:
                                yield FD3Message.from_json(line)
                            except json.JSONDecodeError:
                                pass
                    self._last_position = f.tell()
            except Exception:
                pass

            await asyncio.sleep(poll_interval)

    def clear(self) -> None:
        """Clear the FD3 file."""
        if self._path and self._path.exists():
            try:
                self._path.unlink()
            except Exception:
                pass


# Convenience functions for common message types


def emit_agent_update(
    channel: FD3Channel,
    agent_id: str,
    phase: str,
    activity: float = 0.0,
    summary: str = "",
    source: str = "",
) -> None:
    """Emit an agent update message."""
    channel.emit(
        FD3Message(
            type="agent_update",
            payload={
                "agent_id": agent_id,
                "phase": phase,
                "activity": activity,
                "summary": summary,
            },
            source=source,
        )
    )


def emit_health(
    channel: FD3Channel,
    agent_id: str,
    x_telemetry: float,
    y_semantic: float,
    z_economic: float,
    source: str = "",
) -> None:
    """Emit a health update message."""
    channel.emit(
        FD3Message(
            type="health",
            payload={
                "agent_id": agent_id,
                "x_telemetry": x_telemetry,
                "y_semantic": y_semantic,
                "z_economic": z_economic,
            },
            source=source,
        )
    )


def emit_agentese_invoke(
    channel: FD3Channel,
    agent_id: str,
    agent_name: str,
    path: str,
    args: str = "",
    sub_path: str = "",
    source: str = "",
) -> None:
    """Emit an AGENTESE invocation message."""
    channel.emit(
        FD3Message(
            type="agentese_invoke",
            payload={
                "agent_id": agent_id,
                "agent_name": agent_name,
                "path": path,
                "args": args,
                "sub_path": sub_path,
            },
            source=source,
        )
    )


def emit_error(
    channel: FD3Channel,
    error_type: str,
    message: str,
    agent_id: str = "",
    source: str = "",
) -> None:
    """Emit an error message."""
    channel.emit(
        FD3Message(
            type="error",
            payload={
                "error_type": error_type,
                "message": message,
                "agent_id": agent_id,
            },
            source=source,
        )
    )


def emit_status(
    channel: FD3Channel,
    status: str,
    details: dict[str, Any] | None = None,
    source: str = "",
) -> None:
    """Emit a status message."""
    channel.emit(
        FD3Message(
            type="status",
            payload={
                "status": status,
                "details": details or {},
            },
            source=source,
        )
    )


# Singleton channel for app-wide FD3 access
_global_channel: FD3Channel | None = None


def get_fd3_channel() -> FD3Channel:
    """Get the global FD3 channel."""
    global _global_channel
    if _global_channel is None:
        _global_channel = FD3Channel()
    return _global_channel


def set_fd3_channel(channel: FD3Channel) -> None:
    """Set the global FD3 channel."""
    global _global_channel
    _global_channel = channel
