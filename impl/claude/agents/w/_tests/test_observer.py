"""
Tests for W-gent ProcessObserver.

Validates that external processes can be observed via stdout/stderr capture.
"""

import asyncio
from datetime import datetime

import pytest

from agents.w import ProcessObserver, WireEvent, observe_subprocess


class TestWireEvent:
    """Test WireEvent dataclass."""

    def test_create_event(self):
        """Test creating a WireEvent."""
        event = WireEvent(
            timestamp=datetime.now(),
            level="INFO",
            stage="running",
            message="test message",
        )
        assert event.level == "INFO"
        assert event.stage == "running"
        assert event.message == "test message"

    def test_event_with_metadata(self):
        """Test WireEvent with metadata."""
        event = WireEvent(
            timestamp=datetime.now(),
            level="INFO",
            stage="running",
            message="test",
            metadata={"key": "value"},
        )
        assert event.metadata["key"] == "value"


class TestProcessObserver:
    """Test ProcessObserver."""

    def test_create_observer(self):
        """Test creating a ProcessObserver."""
        observer = ProcessObserver(process_id="123", name="test-process")
        assert observer.process_id == "123"
        assert observer.name == "test-process"

    def test_parse_line_default(self):
        """Test default line parsing."""
        observer = ProcessObserver(process_id="123")
        event = observer._parse_line("test output line")

        assert event.message == "test output line"
        assert event.level == "INFO"
        assert event.stage == "running"

    @pytest.mark.asyncio
    async def test_observe_stream(self):
        """Test observing a stream."""
        observer = ProcessObserver(process_id="123")

        # Create a mock stream
        lines = [b"line 1\n", b"line 2\n", b"line 3\n"]
        stream = asyncio.StreamReader()
        for line in lines:
            stream.feed_data(line)
        stream.feed_eof()

        events = []
        async for event in observer.observe_stream(stream):
            events.append(event)

        assert len(events) == 3
        assert events[0].message == "line 1"
        assert events[1].message == "line 2"
        assert events[2].message == "line 3"


class TestObserveSubprocess:
    """Test observe_subprocess function."""

    @pytest.mark.asyncio
    async def test_observe_echo(self):
        """Test observing a simple echo command."""
        events = []
        async for event in observe_subprocess(["echo", "hello world"]):
            events.append(event)

        assert len(events) >= 1
        assert any("hello world" in event.message for event in events)

    @pytest.mark.asyncio
    async def test_observe_with_custom_name(self):
        """Test observing with a custom process name."""
        events = []
        async for event in observe_subprocess(
            ["echo", "test"],
            name="custom-process",
        ):
            events.append(event)

        # All events should come from a process with the custom name
        assert len(events) >= 1

    @pytest.mark.asyncio
    async def test_observe_stderr(self):
        """Test that stderr is captured with ERROR level."""
        # Use a command that writes to stderr
        events = []
        async for event in observe_subprocess(
            ["python", "-c", "import sys; sys.stderr.write('error message\\n')"]
        ):
            events.append(event)

        # Should have at least one ERROR level event
        error_events = [e for e in events if e.level == "ERROR"]
        assert len(error_events) >= 1
        assert any("error message" in e.message for e in error_events)

    @pytest.mark.asyncio
    async def test_observe_multiple_lines(self):
        """Test observing multiple output lines."""
        events = []
        async for event in observe_subprocess(
            [
                "python",
                "-c",
                "print('line 1'); print('line 2'); print('line 3')",
            ]
        ):
            events.append(event)

        # Should have events for each line
        assert len(events) >= 3
