"""Tests for AgentChatPanel."""

from __future__ import annotations

import pytest

from ..chat import (
    AgentChatPanel,
    ChatMessage,
    ExplanationContext,
    MessageRole,
)


class TestMessageRole:
    """Tests for MessageRole enum."""

    def test_all_roles_exist(self) -> None:
        """Test all expected roles exist."""
        roles = list(MessageRole)
        assert MessageRole.USER in roles
        assert MessageRole.AGENT in roles
        assert MessageRole.SYSTEM in roles


class TestChatMessage:
    """Tests for ChatMessage dataclass."""

    def test_message_creation(self) -> None:
        """Test basic message creation."""
        msg = ChatMessage(
            role=MessageRole.USER,
            content="Hello, agent!",
        )
        assert msg.role == MessageRole.USER
        assert msg.content == "Hello, agent!"
        assert msg.timestamp is not None
        assert msg.turn_refs == []

    def test_message_with_turn_refs(self) -> None:
        """Test message with turn references."""
        msg = ChatMessage(
            role=MessageRole.AGENT,
            content="Based on turn-001...",
            turn_refs=["turn-001", "turn-002"],
        )
        assert len(msg.turn_refs) == 2
        assert "turn-001" in msg.turn_refs

    def test_format_for_display_user(self) -> None:
        """Test formatting user message."""
        msg = ChatMessage(role=MessageRole.USER, content="Test message")
        formatted = msg.format_for_display()

        assert "You" in formatted
        assert "Test message" in formatted

    def test_format_for_display_agent(self) -> None:
        """Test formatting agent message."""
        msg = ChatMessage(role=MessageRole.AGENT, content="Response")
        formatted = msg.format_for_display()

        assert "Agent" in formatted
        assert "Response" in formatted

    def test_format_for_display_system(self) -> None:
        """Test formatting system message."""
        msg = ChatMessage(role=MessageRole.SYSTEM, content="Info")
        formatted = msg.format_for_display()

        assert "System" in formatted


class TestExplanationContext:
    """Tests for ExplanationContext dataclass."""

    def test_context_creation(self) -> None:
        """Test context creation."""
        context = ExplanationContext(
            recent_turns=[
                {"id": "turn-001", "type": "ACTION", "content": "Did something"},
            ],
            causal_cone=["turn-001"],
            current_state={"mode": "DELIBERATING"},
        )
        assert len(context.recent_turns) == 1
        assert len(context.causal_cone) == 1
        assert context.current_state["mode"] == "DELIBERATING"

    def test_context_with_focus_turn(self) -> None:
        """Test context with focus turn."""
        context = ExplanationContext(
            recent_turns=[],
            causal_cone=[],
            current_state={},
            focus_turn_id="turn-005",
        )
        assert context.focus_turn_id == "turn-005"


class TestAgentChatPanel:
    """Tests for AgentChatPanel.

    Note: Many tests are simplified because the panel requires
    an active Textual app to function fully.
    """

    def test_message_role_values(self) -> None:
        """Test message roles have correct values."""
        assert MessageRole.USER.value == 1
        assert MessageRole.AGENT.value == 2
        assert MessageRole.SYSTEM.value == 3

    def test_chat_message_timestamp(self) -> None:
        """Test message has auto timestamp."""
        msg = ChatMessage(
            role=MessageRole.USER,
            content="Test",
        )
        assert msg.timestamp is not None

    def test_explanation_context_fields(self) -> None:
        """Test context has all expected fields."""
        context = ExplanationContext(
            recent_turns=[{"id": "t1"}],
            causal_cone=["t1"],
            current_state={"mode": "IDLE"},
            focus_turn_id="t1",
        )
        assert context.focus_turn_id == "t1"
        assert len(context.recent_turns) == 1
        assert len(context.causal_cone) == 1
