"""
Tests for the Reflector module.

Tests cover:
- Event types and factories
- InvocationContext with FD3 support
- HeadlessReflector capturing
- TerminalReflector output
- Prompt state management
"""

from __future__ import annotations

import json
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from protocols.cli.reflector import (
    CommandEndEvent,
    CommandStartEvent,
    EventType,
    HeadlessReflector,
    InvocationContext,
    Invoker,
    PromptInfo,
    PromptState,
    RuntimeEvent,
    TerminalReflector,
    agent_health,
    agent_registered,
    close_invocation_context,
    command_end,
    command_start,
    create_invocation_context,
    create_test_reflector,
    error_event,
    proposal_added,
)

# =============================================================================
# Event Tests
# =============================================================================


class TestEventFactories:
    """Test event factory functions."""

    def test_command_start_factory(self) -> None:
        """Test command_start factory creates proper event."""
        event = command_start("status", args=["--full"], invoker=Invoker.HUMAN)

        assert event.event_type == EventType.COMMAND_START
        assert event.command == "status"
        assert event.args == ("--full",)
        assert event.invoker == Invoker.HUMAN
        assert event.source == "cli"

    def test_command_end_factory(self) -> None:
        """Test command_end factory creates proper event."""
        event = command_end(
            "status",
            exit_code=0,
            duration_ms=100,
            human_output="[CORTEX] OK",
            semantic_output={"health": "healthy"},
        )

        assert event.event_type == EventType.COMMAND_END
        assert event.command == "status"
        assert event.exit_code == 0
        assert event.duration_ms == 100
        assert event.human_output == "[CORTEX] OK"
        assert event.semantic_output == {"health": "healthy"}

    def test_agent_health_factory(self) -> None:
        """Test agent_health factory creates proper event."""
        event = agent_health(
            agent_id="abc123",
            agent_name="d-gent",
            health={"x": 0.9, "y": 0.8, "z": 0.7},
            phase="active",
            activity=0.5,
        )

        assert event.event_type == EventType.AGENT_HEALTH_UPDATE
        assert event.agent_id == "abc123"
        assert event.health == {"x": 0.9, "y": 0.8, "z": 0.7}
        assert event.phase == "active"

    def test_agent_registered_factory(self) -> None:
        """Test agent_registered factory creates proper event."""
        event = agent_registered(
            agent_id="abc123",
            agent_name="d-gent",
            genus="d-gent",
            capabilities=["memory", "persistence"],
        )

        assert event.event_type == EventType.AGENT_REGISTERED
        assert event.agent_name == "d-gent"
        assert event.capabilities == ("memory", "persistence")

    def test_proposal_added_factory(self) -> None:
        """Test proposal_added factory creates proper event."""
        event = proposal_added(
            proposal_id="prop-1",
            from_agent="d-gent",
            action="kgents dream --run",
            reason="5 days since last REM cycle",
            priority="high",
            confidence=0.85,
        )

        assert event.event_type == EventType.PROPOSAL_ADDED
        assert event.from_agent == "d-gent"
        assert event.priority == "high"
        assert event.confidence == 0.85

    def test_error_event_factory(self) -> None:
        """Test error_event factory creates proper event."""
        event = error_event(
            error_code="PARSE_ERROR",
            message="Invalid JSON",
            recoverable=True,
            suggestions=["Check syntax", "Use --help"],
        )

        assert event.event_type == EventType.ERROR
        assert event.error_code == "PARSE_ERROR"
        assert event.recoverable is True
        assert event.suggestions == ("Check syntax", "Use --help")


class TestEventSequencing:
    """Test event sequence number handling."""

    def test_event_with_sequence(self) -> None:
        """Test adding sequence number to event."""
        event = RuntimeEvent(event_type=EventType.INFO, source="test")
        sequenced = event.with_sequence(42)

        assert sequenced.sequence == 42
        assert event.sequence == 0  # Original unchanged


# =============================================================================
# InvocationContext Tests
# =============================================================================


class TestInvocationContext:
    """Test InvocationContext."""

    def test_basic_context_creation(self) -> None:
        """Test creating a basic context."""
        ctx = InvocationContext(command="status", args=["--full"])

        assert ctx.command == "status"
        assert ctx.args == ["--full"]
        assert ctx.invoker == Invoker.HUMAN

    def test_emit_human_without_reflector(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test emit_human falls back to print without reflector."""
        ctx = InvocationContext(command="test")
        ctx.emit_human("Hello, human!")

        captured = capsys.readouterr()
        assert "Hello, human!" in captured.out

    def test_emit_human_with_reflector(self) -> None:
        """Test emit_human uses reflector when available."""
        reflector = HeadlessReflector()
        ctx = InvocationContext(command="test", reflector=reflector)

        ctx.emit_human("Hello, human!")

        assert "Hello, human!" in reflector.human_output

    def test_emit_semantic_without_fd3(self) -> None:
        """Test emit_semantic without FD3 still accumulates."""
        ctx = InvocationContext(command="test")
        ctx.emit_semantic({"key": "value"})

        assert ctx.get_semantic_output() == {"key": "value"}

    def test_emit_semantic_with_fd3(self) -> None:
        """Test emit_semantic writes to FD3 file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fd3_path = f.name

        try:
            ctx = create_invocation_context("test", fd3_path=fd3_path)
            ctx.emit_semantic({"health": "healthy"})
            close_invocation_context(ctx)

            # Read FD3 output
            with open(fd3_path) as f:
                line = f.readline()
                data = json.loads(line)
                assert data == {"health": "healthy"}
        finally:
            os.unlink(fd3_path)

    def test_output_dual_channel(self) -> None:
        """Test output() emits to both channels."""
        reflector = HeadlessReflector()
        ctx = InvocationContext(command="test", reflector=reflector)

        ctx.output(human="[STATUS] OK", semantic={"status": "ok"})

        assert "[STATUS] OK" in reflector.human_output
        assert reflector.get_semantic_value("status") == "ok"

    def test_elapsed_ms(self) -> None:
        """Test elapsed_ms calculation."""
        import time

        ctx = InvocationContext(command="test")
        time.sleep(0.1)
        elapsed = ctx.elapsed_ms()

        assert elapsed >= 100
        assert elapsed < 500  # Sanity check

    def test_factory_with_env_fd3(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Test factory reads KGENTS_FD3 from environment."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fd3_path = f.name

        try:
            monkeypatch.setenv("KGENTS_FD3", fd3_path)
            ctx = create_invocation_context("test")

            assert ctx.fd3 is not None
            close_invocation_context(ctx)
        finally:
            os.unlink(fd3_path)


# =============================================================================
# HeadlessReflector Tests
# =============================================================================


class TestHeadlessReflector:
    """Test HeadlessReflector for testing scenarios."""

    def test_captures_events(self) -> None:
        """Test that events are captured."""
        reflector = HeadlessReflector()

        reflector.on_event(command_start("status"))
        reflector.on_event(command_end("status", exit_code=0))

        assert len(reflector.events) == 2
        assert reflector.has_event(EventType.COMMAND_START)
        assert reflector.has_event(EventType.COMMAND_END)

    def test_captures_human_output(self) -> None:
        """Test that human output is captured."""
        reflector = HeadlessReflector()

        reflector.emit_human("Line 1")
        reflector.emit_human("Line 2")

        assert reflector.human_output == ["Line 1", "Line 2"]
        assert reflector.get_human_text() == "Line 1\nLine 2"

    def test_captures_semantic_output(self) -> None:
        """Test that semantic output is captured."""
        reflector = HeadlessReflector()

        reflector.emit_semantic({"key1": "value1"})
        reflector.emit_semantic({"key2": "value2"})

        assert reflector.semantic_output == [{"key1": "value1"}, {"key2": "value2"}]
        merged = reflector.get_merged_semantic()
        assert merged == {"key1": "value1", "key2": "value2"}

    def test_get_events_by_type(self) -> None:
        """Test filtering events by type."""
        reflector = HeadlessReflector()

        reflector.on_event(command_start("status"))
        reflector.on_event(agent_health("a", "d-gent", {"x": 0.9}))
        reflector.on_event(command_end("status", exit_code=0))

        health_events = reflector.get_events_by_type(EventType.AGENT_HEALTH_UPDATE)
        assert len(health_events) == 1

    def test_assertion_helpers(self) -> None:
        """Test assertion helper methods."""
        reflector = HeadlessReflector()

        reflector.emit_human("Hello, world!")
        reflector.emit_semantic({"status": "ok"})

        # These should not raise
        reflector.assert_human_contains("Hello")
        reflector.assert_semantic_has("status")
        reflector.assert_semantic_has("status", "ok")

    def test_assertion_failures(self) -> None:
        """Test assertion helpers fail appropriately."""
        reflector = HeadlessReflector()
        reflector.emit_human("Hello")
        reflector.emit_semantic({"a": 1})

        with pytest.raises(AssertionError):
            reflector.assert_human_contains("Goodbye")

        with pytest.raises(AssertionError):
            reflector.assert_semantic_has("missing")

        with pytest.raises(AssertionError):
            reflector.assert_semantic_has("a", 999)

    def test_clear(self) -> None:
        """Test clearing captured data."""
        reflector = HeadlessReflector()

        reflector.on_event(command_start("status"))
        reflector.emit_human("test")
        reflector.emit_semantic({"key": "value"})

        reflector.clear()

        assert len(reflector.events) == 0
        assert len(reflector.human_output) == 0
        assert len(reflector.semantic_output) == 0

    def test_factory_function(self) -> None:
        """Test create_test_reflector factory."""
        reflector = create_test_reflector()
        assert isinstance(reflector, HeadlessReflector)


# =============================================================================
# TerminalReflector Tests
# =============================================================================


class TestTerminalReflector:
    """Test TerminalReflector for CLI output."""

    def test_emit_human_to_stdout(self, capsys: pytest.CaptureFixture[str]) -> None:
        """Test emit_human outputs to stdout."""
        reflector = TerminalReflector()
        reflector.emit_human("Hello, terminal!")

        captured = capsys.readouterr()
        assert "Hello, terminal!" in captured.out

    def test_fd3_output(self) -> None:
        """Test FD3 semantic output."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fd3_path = f.name

        try:
            reflector = TerminalReflector(fd3_path=fd3_path)
            reflector.emit_semantic({"health": "healthy"})
            reflector.close()

            with open(fd3_path) as f:
                line = f.readline()
                data = json.loads(line)
                assert data == {"health": "healthy"}
        finally:
            os.unlink(fd3_path)

    def test_semantic_buffer(self) -> None:
        """Test semantic output is buffered."""
        reflector = TerminalReflector()
        reflector.emit_semantic({"a": 1})
        reflector.emit_semantic({"b": 2})

        buffer = reflector.get_semantic_buffer()
        assert buffer == [{"a": 1}, {"b": 2}]

    def test_context_manager(self) -> None:
        """Test context manager properly closes resources."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fd3_path = f.name

        try:
            with TerminalReflector(fd3_path=fd3_path) as reflector:
                reflector.emit_semantic({"test": True})
            # File should be closed after exiting context
        finally:
            os.unlink(fd3_path)


# =============================================================================
# Prompt State Tests
# =============================================================================


class TestPromptState:
    """Test prompt state management."""

    def test_quiet_prompt(self) -> None:
        """Test quiet state renders simple prompt."""
        info = PromptInfo(state=PromptState.QUIET)
        assert info.render() == "kgents > "

    def test_pending_prompt_singular(self) -> None:
        """Test pending state with one proposal."""
        info = PromptInfo(state=PromptState.PENDING, proposal_count=1)
        assert info.render() == "kgents [1 proposal] > "

    def test_pending_prompt_plural(self) -> None:
        """Test pending state with multiple proposals."""
        info = PromptInfo(state=PromptState.PENDING, proposal_count=3)
        assert info.render() == "kgents [3 proposals] > "

    def test_critical_prompt(self) -> None:
        """Test critical state renders alert."""
        info = PromptInfo(state=PromptState.CRITICAL, critical_message="INFRA DRIFT")
        assert info.render() == "kgents [! INFRA DRIFT] > "

    def test_typing_prompt(self) -> None:
        """Test typing state shows agent."""
        info = PromptInfo(state=PromptState.TYPING, typing_agent="d-gent")
        assert info.render() == "kgents [d-gent...] > "


class TestPromptStateUpdates:
    """Test that reflector updates prompt state correctly."""

    def test_proposal_updates_prompt(self) -> None:
        """Test proposal events update prompt state."""
        reflector = HeadlessReflector()

        # Add proposal
        reflector.on_event(proposal_added("p1", "d-gent", "test"))

        prompt = reflector.render_prompt()
        assert "[1 proposal]" in prompt

    def test_critical_proposal_shows_alert(self) -> None:
        """Test critical proposals show as alerts."""
        reflector = HeadlessReflector()

        # Add critical proposal with data in event.data
        proposal_event = proposal_added(
            proposal_id="p1",
            from_agent="d-gent",
            action="URGENT",
            priority="critical",
        )
        # Update data field for prompt detection
        runtime_event = RuntimeEvent(
            event_type=EventType.PROPOSAL_ADDED,
            source=proposal_event.source,
            data={"priority": "critical", "action": "URGENT"},
        )
        reflector.on_event(runtime_event)

        info = reflector.get_prompt_info()
        assert info.state == PromptState.CRITICAL


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full workflows."""

    def test_full_command_workflow(self) -> None:
        """Test a complete command execution workflow."""
        reflector = HeadlessReflector()
        ctx = create_invocation_context("status", reflector=reflector)

        # Emit command start
        reflector.on_event(command_start(ctx.command, list(ctx.args)))

        # Handler does work
        ctx.output(
            human="[CORTEX] OK HEALTHY | instance:abc123",
            semantic={"health": "healthy", "instance_id": "abc123"},
        )

        # Emit command end
        reflector.on_event(
            command_end(
                ctx.command,
                exit_code=0,
                duration_ms=ctx.elapsed_ms(),
                human_output=ctx.get_human_output(),
                semantic_output=ctx.get_semantic_output(),
            )
        )

        # Verify
        assert reflector.has_event(EventType.COMMAND_START)
        assert reflector.has_event(EventType.COMMAND_END)
        reflector.assert_human_contains("[CORTEX] OK HEALTHY")
        reflector.assert_semantic_has("health", "healthy")

    def test_fd3_end_to_end(self) -> None:
        """Test FD3 output end-to-end."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            fd3_path = f.name

        try:
            # Create reflector with FD3
            reflector = TerminalReflector(fd3_path=fd3_path)
            ctx = create_invocation_context("status", reflector=reflector, fd3_path=fd3_path)

            # Handler emits dual output
            ctx.output(
                human="[CORTEX] OK",
                semantic={"health": "ok", "agents": 5},
            )

            # Cleanup
            close_invocation_context(ctx)
            reflector.close()

            # Read FD3 file
            with open(fd3_path) as f:
                lines = f.readlines()

            # Should have semantic output
            assert len(lines) >= 1
            data = json.loads(lines[0])
            assert data["health"] == "ok"
        finally:
            os.unlink(fd3_path)
