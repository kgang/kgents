"""
Tool Events: SynergyBus Event Definitions for Tool Lifecycle.

Events emitted during tool execution for UI streaming and audit.

Pattern (from crown-jewel-patterns.md):
- Pattern 6: Async-Safe Event Emission

See: spec/services/tooling.md §7
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any

# =============================================================================
# Event Types
# =============================================================================


class ToolEventType(str, Enum):
    """Tool lifecycle event types."""

    INVOKED = "tool.invoked"  # Tool execution started
    COMPLETED = "tool.completed"  # Tool execution succeeded
    FAILED = "tool.failed"  # Tool execution failed
    TIMEOUT = "tool.timeout"  # Tool execution timed out
    TRUST_DENIED = "tool.trust_denied"  # Trust gate denied
    CONFIRMATION_REQUIRED = "tool.confirmation_required"  # L2 awaiting confirm
    CONFIRMATION_RECEIVED = "tool.confirmation_received"  # L2 confirmed


# =============================================================================
# Event Payloads
# =============================================================================


@dataclass
class ToolEventPayload:
    """Payload for tool lifecycle events."""

    execution_id: str
    tool_path: str
    tool_name: str
    observer_id: str | None = None
    trust_level: int = 0
    duration_ms: float | None = None
    success: bool | None = None
    error: str | None = None
    input_summary: str = ""  # Truncated input
    output_summary: str = ""  # Truncated output
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))


# =============================================================================
# Event Constructors
# =============================================================================


def create_tool_event(
    event_type: ToolEventType,
    payload: ToolEventPayload,
) -> dict[str, Any]:
    """
    Create a SynergyBus event for tool lifecycle.

    Returns dict suitable for SynergyBus.emit().
    """
    return {
        "event_type": event_type.value,
        "source": f"world.tools.{payload.tool_name}",
        "payload": {
            "execution_id": payload.execution_id,
            "tool_path": payload.tool_path,
            "tool_name": payload.tool_name,
            "observer_id": payload.observer_id,
            "trust_level": payload.trust_level,
            "duration_ms": payload.duration_ms,
            "success": payload.success,
            "error": payload.error,
            "input_summary": payload.input_summary,
            "output_summary": payload.output_summary,
            "timestamp": payload.timestamp.isoformat(),
        },
    }


def tool_invoked_event(
    execution_id: str,
    tool_name: str,
    input_summary: str = "",
    observer_id: str | None = None,
    trust_level: int = 0,
) -> dict[str, Any]:
    """Create a tool.invoked event."""
    return create_tool_event(
        ToolEventType.INVOKED,
        ToolEventPayload(
            execution_id=execution_id,
            tool_path=f"world.tools.{tool_name}",
            tool_name=tool_name,
            observer_id=observer_id,
            trust_level=trust_level,
            input_summary=input_summary,
        ),
    )


def tool_completed_event(
    execution_id: str,
    tool_name: str,
    duration_ms: float,
    output_summary: str = "",
) -> dict[str, Any]:
    """Create a tool.completed event."""
    return create_tool_event(
        ToolEventType.COMPLETED,
        ToolEventPayload(
            execution_id=execution_id,
            tool_path=f"world.tools.{tool_name}",
            tool_name=tool_name,
            duration_ms=duration_ms,
            success=True,
            output_summary=output_summary,
        ),
    )


def tool_failed_event(
    execution_id: str,
    tool_name: str,
    error: str,
    duration_ms: float = 0.0,
) -> dict[str, Any]:
    """Create a tool.failed event."""
    return create_tool_event(
        ToolEventType.FAILED,
        ToolEventPayload(
            execution_id=execution_id,
            tool_path=f"world.tools.{tool_name}",
            tool_name=tool_name,
            duration_ms=duration_ms,
            success=False,
            error=error,
        ),
    )


def tool_trust_denied_event(
    execution_id: str,
    tool_name: str,
    required_trust: int,
    current_trust: int,
) -> dict[str, Any]:
    """Create a tool.trust_denied event."""
    return create_tool_event(
        ToolEventType.TRUST_DENIED,
        ToolEventPayload(
            execution_id=execution_id,
            tool_path=f"world.tools.{tool_name}",
            tool_name=tool_name,
            trust_level=current_trust,
            success=False,
            error=f"Trust L{current_trust} insufficient (requires L{required_trust})",
        ),
    )


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    "ToolEventType",
    "ToolEventPayload",
    "create_tool_event",
    "tool_invoked_event",
    "tool_completed_event",
    "tool_failed_event",
    "tool_trust_denied_event",
]
