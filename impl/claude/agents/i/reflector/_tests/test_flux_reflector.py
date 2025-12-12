"""
Tests for FluxReflector - the bridge between CLI events and FluxApp TUI.

Tests cover:
- FluxReflector creation and configuration
- Event handling (command start/end, agent health, pheromone, error)
- Thread-safe event queuing
- Output buffering
- ProcessingWaveform.pulse() integration
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from agents.i.reflector import FluxReflector, create_flux_reflector
from agents.i.widgets.waveform import OperationType, ProcessingWaveform
from protocols.cli.reflector.events import (
    AgentHealthEvent,
    CommandEndEvent,
    CommandStartEvent,
    ErrorEvent,
    EventType,
    Invoker,
    PheromoneEvent,
    ProposalAddedEvent,
)

# =============================================================================
# FluxReflector Creation Tests
# =============================================================================


class TestFluxReflectorCreation:
    """Test FluxReflector instantiation."""

    def test_create_without_app(self) -> None:
        """Test creating a reflector without an app."""
        reflector = create_flux_reflector()
        assert reflector.app is None

    def test_set_app_after_creation(self) -> None:
        """Test setting app after reflector creation."""
        reflector = create_flux_reflector()
        mock_app = MagicMock()

        reflector.set_app(mock_app)

        assert reflector.app is mock_app

    def test_create_with_app(self) -> None:
        """Test creating reflector with app reference."""
        mock_app = MagicMock()
        reflector = create_flux_reflector(mock_app)

        assert reflector.app is mock_app

    def test_reflector_has_event_queue(self) -> None:
        """Test reflector has async event queue."""
        reflector = create_flux_reflector()
        assert isinstance(reflector._event_queue, asyncio.Queue)


# =============================================================================
# Event Handling Tests (No App)
# =============================================================================


class TestEventHandlingWithoutApp:
    """Test event handling when no app is connected."""

    def test_handle_event_without_app_is_safe(self) -> None:
        """Test that handling events without app doesn't crash."""
        reflector = create_flux_reflector()

        event = CommandStartEvent(
            event_type=EventType.COMMAND_START,
            source="cli",
            command="status",
            args=(),
            invoker=Invoker.HUMAN,
        )

        # Should not raise
        reflector._handle_event(event)

    def test_process_event_without_app_is_safe(self) -> None:
        """Test that processing events without app doesn't crash."""
        reflector = create_flux_reflector()

        event = CommandStartEvent(
            event_type=EventType.COMMAND_START,
            source="cli",
            command="status",
            args=(),
            invoker=Invoker.HUMAN,
        )

        # Should not raise
        reflector._process_event(event)


# =============================================================================
# Command Event Tests
# =============================================================================


class TestCommandEvents:
    """Test command start/end event handling."""

    def test_command_start_without_app_does_not_queue(self) -> None:
        """Test command start without app doesn't queue (no-op)."""
        reflector = create_flux_reflector()

        event = CommandStartEvent(
            event_type=EventType.COMMAND_START,
            source="cli",
            command="status",
            args=("--full",),
            invoker=Invoker.HUMAN,
        )

        reflector._handle_event(event)

        # Without app, event is not queued (early return)
        assert reflector._event_queue.empty()

    def test_command_end_with_error_exit_code(self) -> None:
        """Test command end with non-zero exit code."""
        mock_app = MagicMock()
        mock_app.screen = MagicMock()
        mock_app.screen.invoke_agentese = MagicMock()

        reflector = create_flux_reflector(mock_app)

        event = CommandEndEvent(
            event_type=EventType.COMMAND_END,
            source="cli",
            command="status",
            exit_code=1,
            duration_ms=100,
        )

        reflector._process_event(event)

        # Should notify with warning
        mock_app.notify.assert_called_once()
        call_args = mock_app.notify.call_args
        assert "failed" in call_args[0][0]
        assert call_args[1]["severity"] == "warning"

    def test_command_end_success_long_running(self) -> None:
        """Test command end for long-running successful command."""
        mock_app = MagicMock()
        mock_app.screen = MagicMock()
        mock_app.screen.invoke_agentese = MagicMock()

        reflector = create_flux_reflector(mock_app)

        event = CommandEndEvent(
            event_type=EventType.COMMAND_END,
            source="cli",
            command="dream",
            exit_code=0,
            duration_ms=2000,  # > 1000ms
        )

        reflector._process_event(event)

        # Should notify about completion
        mock_app.notify.assert_called_once()
        assert "completed" in mock_app.notify.call_args[0][0]


# =============================================================================
# Agent Health Tests
# =============================================================================


class TestAgentHealthEvents:
    """Test agent health event handling."""

    def test_agent_health_converts_xyz(self) -> None:
        """Test XYZ health dict is converted properly."""
        mock_screen = MagicMock()
        mock_screen.invoke_agentese = MagicMock()
        mock_screen.update_health = MagicMock()
        mock_screen.query_one = MagicMock(side_effect=Exception("Not found"))

        mock_app = MagicMock()
        mock_app.screen = mock_screen

        # Make hasattr check pass for invoke_agentese
        type(mock_screen).invoke_agentese = MagicMock()

        reflector = create_flux_reflector(mock_app)

        event = AgentHealthEvent(
            event_type=EventType.AGENT_HEALTH_UPDATE,
            source="agent",
            agent_id="abc123",
            agent_name="d-gent",
            health={"x": 0.9, "y": 0.8, "z": 0.7},
            phase="active",
            activity=0.5,
        )

        reflector._process_event(event)

        # Should call update_health with XYZHealth
        mock_screen.update_health.assert_called_once()
        call_args = mock_screen.update_health.call_args
        assert call_args[0][0] == "abc123"  # agent_id
        health_obj = call_args[0][1]
        assert health_obj.x_telemetry == 0.9
        assert health_obj.y_semantic == 0.8
        assert health_obj.z_economic == 0.7


# =============================================================================
# Pheromone Event Tests
# =============================================================================


class TestPheromoneEvents:
    """Test pheromone event handling and waveform pulse."""

    def test_pheromone_triggers_waveform_pulse(self) -> None:
        """Test pheromone event triggers waveform.pulse()."""
        mock_waveform = MagicMock()
        mock_waveform.pulse = MagicMock()

        mock_screen = MagicMock()
        mock_screen.invoke_agentese = MagicMock()
        mock_screen.query_one = MagicMock(return_value=mock_waveform)

        mock_app = MagicMock()
        mock_app.screen = mock_screen

        reflector = create_flux_reflector(mock_app)

        event = PheromoneEvent(
            event_type=EventType.PHEROMONE_EMITTED,
            source="agent",
            pheromone_type="signal",
            level=0.8,
            agent_id="abc123",
        )

        reflector._process_event(event)

        # Should call pulse with intensity
        mock_waveform.pulse.assert_called_once_with(intensity=0.8)


# =============================================================================
# Error Event Tests
# =============================================================================


class TestErrorEvents:
    """Test error event handling."""

    def test_error_triggers_glitch(self) -> None:
        """Test error event triggers glitch controller."""
        mock_app = MagicMock()
        mock_app.screen = MagicMock()
        mock_app.screen.invoke_agentese = MagicMock()

        reflector = create_flux_reflector(mock_app)

        event = ErrorEvent(
            event_type=EventType.ERROR,
            source="cli",
            error_code="PARSE_ERROR",
            message="Invalid syntax",
            recoverable=True,
        )

        # Patch where the function is imported from (inside _handle_error)
        with patch("agents.i.widgets.glitch.get_glitch_controller") as mock_get:
            mock_controller = MagicMock()
            mock_get.return_value = mock_controller

            with patch("asyncio.create_task"):
                reflector._process_event(event)

            # Should call glitch controller
            mock_get.assert_called_once()

    def test_error_notifies_with_severity(self) -> None:
        """Test error notification has correct severity."""
        mock_app = MagicMock()
        mock_app.screen = MagicMock()
        mock_app.screen.invoke_agentese = MagicMock()

        reflector = create_flux_reflector(mock_app)

        # Non-recoverable error
        event = ErrorEvent(
            event_type=EventType.ERROR,
            source="cli",
            error_code="FATAL",
            message="Critical failure",
            recoverable=False,
        )

        # Patch where the function is imported from (inside _handle_error)
        with patch("agents.i.widgets.glitch.get_glitch_controller") as mock_get:
            mock_controller = MagicMock()
            mock_get.return_value = mock_controller

            with patch("asyncio.create_task"):
                reflector._process_event(event)

        # Should notify with error severity
        mock_app.notify.assert_called_once()
        assert mock_app.notify.call_args[1]["severity"] == "error"


# =============================================================================
# Output Buffer Tests
# =============================================================================


class TestOutputBuffers:
    """Test human and semantic output buffering."""

    def test_emit_human_buffers_output(self) -> None:
        """Test emit_human adds to buffer."""
        reflector = create_flux_reflector()

        reflector.emit_human("Line 1")
        reflector.emit_human("Line 2")

        assert reflector.get_human_output() == "Line 1\nLine 2"

    def test_emit_semantic_buffers_output(self) -> None:
        """Test emit_semantic adds to buffer."""
        reflector = create_flux_reflector()

        reflector.emit_semantic({"key1": "value1"})
        reflector.emit_semantic({"key2": "value2"})

        output = reflector.get_semantic_output()
        assert output == {"key1": "value1", "key2": "value2"}

    def test_clear_buffers(self) -> None:
        """Test clearing buffers."""
        reflector = create_flux_reflector()

        reflector.emit_human("test")
        reflector.emit_semantic({"key": "value"})

        reflector.clear_buffers()

        assert reflector.get_human_output() == ""
        assert reflector.get_semantic_output() == {}


# =============================================================================
# Event Queue Tests
# =============================================================================


class TestEventQueue:
    """Test async event queue management."""

    @pytest.mark.asyncio
    async def test_drain_queue(self) -> None:
        """Test draining event queue."""
        reflector = create_flux_reflector()

        # Add some events to queue
        event1 = CommandStartEvent(
            event_type=EventType.COMMAND_START,
            source="cli",
            command="status",
            args=(),
            invoker=Invoker.HUMAN,
        )
        event2 = CommandEndEvent(
            event_type=EventType.COMMAND_END,
            source="cli",
            command="status",
            exit_code=0,
            duration_ms=100,
        )

        reflector._event_queue.put_nowait(event1)
        reflector._event_queue.put_nowait(event2)

        events = await reflector.drain_queue()

        assert len(events) == 2
        assert reflector._event_queue.empty()


# =============================================================================
# ProcessingWaveform.pulse() Tests
# =============================================================================


class TestProcessingWaveformPulse:
    """Test the ProcessingWaveform.pulse() method directly."""

    def test_pulse_increases_offset(self) -> None:
        """Test pulse increases animation offset."""
        waveform = ProcessingWaveform()
        initial_offset = waveform.animation_offset

        waveform.pulse(intensity=0.5)

        assert waveform.animation_offset > initial_offset

    def test_pulse_intensity_affects_offset(self) -> None:
        """Test higher intensity causes larger offset bump."""
        waveform1 = ProcessingWaveform()
        waveform2 = ProcessingWaveform()

        waveform1.pulse(intensity=0.1)
        offset1 = waveform1.animation_offset

        waveform2.pulse(intensity=1.0)
        offset2 = waveform2.animation_offset

        assert offset2 > offset1

    def test_pulse_creative_mode_extra_bump(self) -> None:
        """Test creative mode gets extra offset bump."""
        waveform_waiting = ProcessingWaveform(operation_type=OperationType.WAITING)
        waveform_creative = ProcessingWaveform(operation_type=OperationType.CREATIVE)

        waveform_waiting.pulse(intensity=0.5)
        waveform_creative.pulse(intensity=0.5)

        # Creative should have larger offset due to extra bump
        assert waveform_creative.animation_offset > waveform_waiting.animation_offset


# =============================================================================
# Integration Tests
# =============================================================================


class TestFluxReflectorIntegration:
    """Integration tests for FluxReflector."""

    def test_full_event_workflow(self) -> None:
        """Test a complete event workflow."""
        mock_screen = MagicMock()
        mock_screen.invoke_agentese = MagicMock()

        mock_app = MagicMock()
        mock_app.screen = mock_screen

        reflector = create_flux_reflector(mock_app)

        # Simulate command start
        start_event = CommandStartEvent(
            event_type=EventType.COMMAND_START,
            source="cli",
            command="status",
            args=("--full",),
            invoker=Invoker.HUMAN,
            trace_id="trace-123",
        )
        reflector._process_event(start_event)

        # Should have invoked agentese on screen
        mock_screen.invoke_agentese.assert_called_once()
        call_kwargs = mock_screen.invoke_agentese.call_args[1]
        assert call_kwargs["path"] == "cmd.status"
        assert call_kwargs["sub_path"] == "trace.trace-123"

        # Simulate command end
        end_event = CommandEndEvent(
            event_type=EventType.COMMAND_END,
            source="cli",
            command="status",
            exit_code=0,
            duration_ms=50,
        )
        reflector._process_event(end_event)

        # Short commands don't notify (< 1000ms)
        # Only start notification should be present
        assert mock_app.notify.call_count == 1
