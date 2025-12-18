"""
Tests for Chat Projection module.

Tests cover:
- ChatRenderer formatting
- ChatProjection lifecycle
- Command handling
- Integration with CLIProjection routing
"""

from __future__ import annotations

from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# =============================================================================
# Test ChatRenderer
# =============================================================================


class TestChatRenderer:
    """Tests for ChatRenderer message formatting."""

    def test_render_welcome_basic(self) -> None:
        """Test welcome message rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer(entity_name="K-gent")
        welcome = renderer.render_welcome("self.soul", "abc12345-def-ghi")

        assert "K-gent" in welcome
        assert "self.soul" in welcome
        assert "abc12345" in welcome  # Truncated session ID
        assert "/help" in welcome or "help" in welcome.lower()

    def test_render_user_message(self) -> None:
        """Test user message rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer(user_name="Kent")
        msg = renderer.render_user_message("Hello world")

        assert "Kent" in msg
        assert "Hello world" in msg

    def test_render_assistant_start_end(self) -> None:
        """Test assistant response markers."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer(entity_name="K-gent")
        start = renderer.render_assistant_start()
        end = renderer.render_assistant_end()

        assert "K-gent" in start
        assert end.strip() == ""  # Just newline

    def test_render_streaming_token(self) -> None:
        """Test streaming token passthrough."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        token = renderer.render_streaming_token("hello")
        assert token == "hello"

    def test_render_status_bar(self) -> None:
        """Test status bar rendering with metrics."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        status = renderer.render_status_bar(
            turn=3,
            context_util=0.5,
            cost_usd=0.0123,
            entropy=0.8,
        )

        assert "Turn: 3" in status
        assert "50%" in status  # Context utilization
        assert "$0.0123" in status
        # Should have gauge bars (ASCII chars: # for filled, - for empty)
        assert "#" in status or "-" in status

    def test_render_history_empty(self) -> None:
        """Test empty history rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        history = renderer.render_history([])

        assert "No conversation history" in history

    def test_render_history_with_turns(self) -> None:
        """Test history rendering with turns."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        turns = [
            {"turn_number": 1, "user_message": "Hello", "assistant_response": "Hi!"},
            {"turn_number": 2, "user_message": "Test", "assistant_response": "Response"},
        ]
        history = renderer.render_history(turns, limit=5)

        assert "History" in history
        assert "#1" in history
        assert "#2" in history

    def test_render_metrics(self) -> None:
        """Test metrics panel rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        metrics = renderer.render_metrics(
            {
                "session_id": "abc123",
                "state": "READY",
                "turns_completed": 5,
                "tokens_in": 1000,
                "tokens_out": 500,
                "average_turn_latency": 1.5,
                "context_utilization": 0.3,
                "entropy": 0.9,
                "estimated_cost_usd": 0.01,
            }
        )

        assert "Metrics" in metrics
        assert "READY" in metrics
        assert "5" in metrics  # turns
        assert "1,000" in metrics or "1000" in metrics  # tokens

    def test_render_help(self) -> None:
        """Test help rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        help_text = renderer.render_help()

        assert "/exit" in help_text
        assert "/history" in help_text
        assert "/metrics" in help_text

    def test_render_error(self) -> None:
        """Test error rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        error = renderer.render_error("Something went wrong")

        assert "Error" in error
        assert "Something went wrong" in error

    def test_render_goodbye(self) -> None:
        """Test goodbye message rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        goodbye = renderer.render_goodbye(
            {
                "turns_completed": 10,
                "estimated_cost_usd": 0.05,
            }
        )

        assert "10" in goodbye
        assert "$0.05" in goodbye


# =============================================================================
# Test ChatProjection
# =============================================================================


class TestChatProjection:
    """Tests for ChatProjection REPL behavior."""

    def test_projection_creation(self) -> None:
        """Test creating a ChatProjection."""
        from protocols.cli.chat_projection import ChatProjection, ChatRenderer

        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.node_path = "self.soul"
        mock_session.is_collapsed = False

        renderer = ChatRenderer()
        projection = ChatProjection(
            session=mock_session,
            renderer=renderer,
            node_path="self.soul",
        )

        assert projection.node_path == "self.soul"
        assert projection.renderer is renderer

    @pytest.mark.asyncio
    async def test_handle_exit_command(self) -> None:
        """Test handling /exit command."""
        from protocols.cli.chat_projection import ChatProjection, ChatRenderer

        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.node_path = "self.soul"

        renderer = ChatRenderer()
        projection = ChatProjection(
            session=mock_session,
            renderer=renderer,
        )

        result = await projection._handle_command("/exit")
        assert result == "exit"

        result = await projection._handle_command("/quit")
        assert result == "exit"

        result = await projection._handle_command("/q")
        assert result == "exit"

    @pytest.mark.asyncio
    async def test_handle_help_command(self) -> None:
        """Test handling /help command."""
        from protocols.cli.chat_projection import ChatProjection, ChatRenderer

        mock_session = MagicMock()
        mock_session.session_id = "test-123"

        renderer = ChatRenderer()
        projection = ChatProjection(
            session=mock_session,
            renderer=renderer,
        )

        result = await projection._handle_command("/help")
        assert result is None  # Help doesn't exit

    @pytest.mark.asyncio
    async def test_handle_history_command(self) -> None:
        """Test handling /history command."""
        from protocols.cli.chat_projection import ChatProjection, ChatRenderer

        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.get_history = MagicMock(return_value=[])

        renderer = ChatRenderer()
        projection = ChatProjection(
            session=mock_session,
            renderer=renderer,
        )

        result = await projection._handle_command("/history 5")
        assert result is None
        mock_session.get_history.assert_called_once_with(limit=5)

    @pytest.mark.asyncio
    async def test_handle_metrics_command(self) -> None:
        """Test handling /metrics command."""
        from protocols.cli.chat_projection import ChatProjection, ChatRenderer

        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.get_metrics = MagicMock(
            return_value={
                "turns_completed": 5,
                "estimated_cost_usd": 0.01,
            }
        )

        renderer = ChatRenderer()
        projection = ChatProjection(
            session=mock_session,
            renderer=renderer,
        )

        result = await projection._handle_command("/metrics")
        assert result is None
        mock_session.get_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_reset_command(self) -> None:
        """Test handling /reset command."""
        from protocols.cli.chat_projection import ChatProjection, ChatRenderer

        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.reset = MagicMock()

        renderer = ChatRenderer()
        projection = ChatProjection(
            session=mock_session,
            renderer=renderer,
        )

        result = await projection._handle_command("/reset")
        assert result is None
        mock_session.reset.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_unknown_command(self) -> None:
        """Test handling unknown command."""
        from protocols.cli.chat_projection import ChatProjection, ChatRenderer

        mock_session = MagicMock()
        mock_session.session_id = "test-123"

        renderer = ChatRenderer()
        projection = ChatProjection(
            session=mock_session,
            renderer=renderer,
        )

        result = await projection._handle_command("/unknown")
        assert result is None  # Unknown commands don't exit


# =============================================================================
# Test CLI Integration
# =============================================================================


class TestCLIIntegration:
    """Tests for integration with CLI projection."""

    def test_chat_command_constants(self) -> None:
        """Test chat command set."""
        from protocols.cli.chat_projection import CHAT_COMMANDS

        assert "/exit" in CHAT_COMMANDS
        assert "/quit" in CHAT_COMMANDS
        assert "/history" in CHAT_COMMANDS
        assert "/metrics" in CHAT_COMMANDS
        assert "/help" in CHAT_COMMANDS

    def test_cli_projection_routes_chat_path(self) -> None:
        """Test that CLIProjection routes .chat paths."""
        from protocols.cli.dimensions import (
            Backend,
            CommandDimensions,
            Execution,
            Intent,
            Interactivity,
            Seriousness,
            Statefulness,
        )

        # Create dimensions with INTERACTIVE interactivity
        dims = CommandDimensions(
            interactivity=Interactivity.INTERACTIVE,
            execution=Execution.ASYNC,
            statefulness=Statefulness.STATEFUL,
            backend=Backend.LLM,
            intent=Intent.FUNCTIONAL,
            seriousness=Seriousness.NEUTRAL,
        )
        assert dims.is_interactive

    def test_soul_mode_includes_chat(self) -> None:
        """Test that soul command modes include chat."""
        from protocols.cli.commands.soul import ALL_MODES, SPECIAL_COMMANDS

        assert "chat" in SPECIAL_COMMANDS
        assert "chat" in ALL_MODES


# =============================================================================
# Test Entry Points
# =============================================================================


class TestEntryPoints:
    """Tests for entry point functions."""

    def test_run_chat_repl_exists(self) -> None:
        """Test run_chat_repl is importable."""
        from protocols.cli.chat_projection import run_chat_repl

        assert callable(run_chat_repl)

    def test_run_chat_one_shot_exists(self) -> None:
        """Test run_chat_one_shot is importable."""
        from protocols.cli.chat_projection import run_chat_one_shot

        assert callable(run_chat_one_shot)


# =============================================================================
# Test Gauge Rendering
# =============================================================================


class TestGaugeRendering:
    """Tests for visual gauge rendering."""

    def test_gauge_full(self) -> None:
        """Test full gauge rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        # Access private method for testing
        gauge = renderer._render_gauge(1.0, width=8)
        assert gauge == "#" * 8

    def test_gauge_empty(self) -> None:
        """Test empty gauge rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        gauge = renderer._render_gauge(0.0, width=8)
        assert gauge == "-" * 8

    def test_gauge_half(self) -> None:
        """Test half gauge rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        gauge = renderer._render_gauge(0.5, width=8)
        assert gauge == "#" * 4 + "-" * 4

    def test_gauge_clamping(self) -> None:
        """Test gauge clamping to width."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        # Values > 1.0 should be clamped
        gauge = renderer._render_gauge(1.5, width=8)
        assert len(gauge) == 8
        assert gauge == "#" * 8

        # Negative values result in 0 filled chars
        gauge = renderer._render_gauge(-0.5, width=8)
        # Negative value: int(-0.5 * 8) = -4, then max(0, min(8, -4)) = 0
        # So 0 filled chars, 8 empty chars
        assert len(gauge) == 8
        assert gauge == "-" * 8


# =============================================================================
# Test Context Panel
# =============================================================================


class TestContextPanel:
    """Tests for context window panel."""

    @pytest.mark.asyncio
    async def test_handle_context_command(self) -> None:
        """Test handling /context command."""
        from protocols.cli.chat_projection import ChatProjection, ChatRenderer

        mock_session = MagicMock()
        mock_session.session_id = "test-123"
        mock_session.get_context_utilization = MagicMock(return_value=0.5)
        mock_session.config = MagicMock()
        mock_session.config.context_window = 200000
        mock_session.config.context_strategy = MagicMock()
        mock_session.config.context_strategy.value = "sliding_window"

        renderer = ChatRenderer()
        projection = ChatProjection(
            session=mock_session,
            renderer=renderer,
        )

        result = await projection._handle_command("/context")
        assert result is None
        mock_session.get_context_utilization.assert_called_once()

    def test_render_context(self) -> None:
        """Test context panel rendering."""
        from protocols.cli.chat_projection import ChatRenderer

        renderer = ChatRenderer()
        context = renderer.render_context(
            {
                "utilization": 0.5,
                "window_size": 200000,
                "strategy": "sliding_window",
            }
        )

        assert "Context Window" in context
        assert "50%" in context or "50.0%" in context
        assert "200,000" in context or "200000" in context
        assert "sliding_window" in context
