"""
Headless Reflector - Test-friendly implementation.

Captures all events and output in memory for inspection.
Used for unit tests, integration tests, and CI environments.

This reflector does NOT output anything to stdout/stderr,
making it ideal for automated testing.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from io import StringIO
from typing import Any

from .events import (
    CommandEndEvent,
    CommandStartEvent,
    EventType,
    RuntimeEvent,
)
from .protocol import BaseReflector, PromptInfo, PromptState


@dataclass
class CapturedOutput:
    """A single captured output record."""

    channel: str  # "human" or "semantic"
    timestamp: datetime
    content: str | dict[str, Any]


class HeadlessReflector(BaseReflector):
    """
    Reflector that captures everything in memory.

    Perfect for testing because:
    - No stdout/stderr output
    - All events captured and inspectable
    - All output captured and inspectable
    - Can assert on exact event sequences
    """

    def __init__(self) -> None:
        super().__init__()
        self._events: list[RuntimeEvent] = []
        self._human_output: list[str] = []
        self._semantic_output: list[dict[str, Any]] = []
        self._captured: list[CapturedOutput] = []

    def _handle_event(self, event: RuntimeEvent) -> None:
        """Capture event to memory."""
        self._events.append(event)

    def emit_human(self, text: str) -> None:
        """Capture human output."""
        self._human_output.append(text)
        self._captured.append(
            CapturedOutput(
                channel="human",
                timestamp=datetime.now(),
                content=text,
            )
        )

    def emit_semantic(self, data: dict[str, Any]) -> None:
        """Capture semantic output."""
        self._semantic_output.append(data)
        self._captured.append(
            CapturedOutput(
                channel="semantic",
                timestamp=datetime.now(),
                content=data,
            )
        )

    # =========================================================================
    # Test Helpers
    # =========================================================================

    @property
    def events(self) -> list[RuntimeEvent]:
        """Get all captured events."""
        return list(self._events)

    @property
    def human_output(self) -> list[str]:
        """Get all captured human output."""
        return list(self._human_output)

    @property
    def semantic_output(self) -> list[dict[str, Any]]:
        """Get all captured semantic output."""
        return list(self._semantic_output)

    @property
    def captured(self) -> list[CapturedOutput]:
        """Get all captured output in order."""
        return list(self._captured)

    def get_human_text(self) -> str:
        """Get all human output as a single string."""
        return "\n".join(self._human_output)

    def get_merged_semantic(self) -> dict[str, Any]:
        """Get all semantic output merged into one dict."""
        merged: dict[str, Any] = {}
        for d in self._semantic_output:
            merged.update(d)
        return merged

    def get_events_by_type(self, event_type: EventType) -> list[RuntimeEvent]:
        """Filter events by type."""
        return [e for e in self._events if e.event_type == event_type]

    def get_command_events(self) -> list[CommandStartEvent | CommandEndEvent]:
        """Get all command-related events."""
        return [
            e
            for e in self._events
            if isinstance(e, (CommandStartEvent, CommandEndEvent))
        ]

    def has_event(self, event_type: EventType) -> bool:
        """Check if an event of the given type was captured."""
        return any(e.event_type == event_type for e in self._events)

    def has_human_output(self, substring: str) -> bool:
        """Check if human output contains the given substring."""
        return substring in self.get_human_text()

    def has_semantic_key(self, key: str) -> bool:
        """Check if any semantic output contains the given key."""
        return any(key in d for d in self._semantic_output)

    def get_semantic_value(self, key: str) -> Any:
        """Get a value from semantic output by key (searches all outputs)."""
        for d in self._semantic_output:
            if key in d:
                return d[key]
        return None

    def clear(self) -> None:
        """Clear all captured data."""
        self._events.clear()
        self._human_output.clear()
        self._semantic_output.clear()
        self._captured.clear()
        self._sequence = 0
        self._prompt_info = PromptInfo()
        self._proposal_count = 0
        self._critical_alerts.clear()

    def assert_event_count(self, expected: int, event_type: EventType | None = None) -> None:
        """Assert the number of captured events."""
        if event_type:
            actual = len(self.get_events_by_type(event_type))
            assert actual == expected, f"Expected {expected} {event_type.value} events, got {actual}"
        else:
            actual = len(self._events)
            assert actual == expected, f"Expected {expected} events, got {actual}"

    def assert_human_contains(self, substring: str) -> None:
        """Assert that human output contains the substring."""
        text = self.get_human_text()
        assert substring in text, f"Expected '{substring}' in human output, got: {text}"

    def assert_semantic_has(self, key: str, value: Any | None = None) -> None:
        """Assert that semantic output has the given key (and optionally value)."""
        assert self.has_semantic_key(key), f"Expected key '{key}' in semantic output"
        if value is not None:
            actual = self.get_semantic_value(key)
            assert actual == value, f"Expected {key}={value}, got {key}={actual}"


# =============================================================================
# Factory Functions
# =============================================================================


def create_test_reflector() -> HeadlessReflector:
    """Create a fresh HeadlessReflector for testing."""
    return HeadlessReflector()
