"""
Test ChatSession integration with FlowPolynomial.

Verifies:
- ChatSession uses CHAT_POLYNOMIAL for state validation
- Invalid actions raise InvalidAction errors
- State transitions work correctly
- Backward compatibility with ChatState
- Round-trip serialization preserves flow state
"""

import pytest

from agents.f.state import FlowState
from services.chat.session import ChatSession, ChatState, InvalidAction


class TestFlowPolynomialIntegration:
    """Test FlowPolynomial integration in ChatSession."""

    def test_session_starts_in_dormant(self):
        """New session should start in DORMANT state."""
        session = ChatSession.create()

        assert session.flow_state == FlowState.DORMANT
        assert session.state == ChatState.IDLE  # Backward compat

    def test_first_message_transitions_to_streaming(self):
        """Adding first turn should transition DORMANT -> STREAMING."""
        session = ChatSession.create()

        session.add_turn("Hello", "Hi there!")

        assert session.flow_state == FlowState.STREAMING
        assert session.turn_count == 1

    def test_message_in_streaming_stays_streaming(self):
        """Adding messages in STREAMING should stay in STREAMING."""
        session = ChatSession.create()
        session.add_turn("First", "Response 1")

        session.add_turn("Second", "Response 2")

        assert session.flow_state == FlowState.STREAMING
        assert session.turn_count == 2

    def test_fork_creates_branches(self):
        """Forking should create two independent branches."""
        session = ChatSession.create()
        session.add_turn("Message", "Response")

        left, right = session.fork("test-branch")

        # Both branches remain in STREAMING (fork is K-Block level)
        assert left.flow_state == FlowState.STREAMING
        assert right.flow_state == FlowState.STREAMING
        # Right is a separate session
        assert right.id != left.id
        assert right.node.parent_id == left.id

    def test_invalid_action_raises_error(self):
        """Invalid actions should raise InvalidAction with helpful message."""
        session = ChatSession.create()

        # Can't send message in DORMANT (must start first)
        # Actually, add_turn handles this internally, so test _transition directly
        with pytest.raises(InvalidAction) as exc_info:
            session._transition("invalid_action")

        assert "invalid_action" in str(exc_info.value)
        assert "DORMANT" in str(exc_info.value)
        assert "Valid actions:" in str(exc_info.value)

    def test_validate_action_shows_valid_actions(self):
        """Validation error should show what actions are valid."""
        session = ChatSession.create()

        with pytest.raises(InvalidAction) as exc_info:
            session._validate_action("branch")  # Can't branch from DORMANT

        error_msg = str(exc_info.value)
        # DORMANT allows "start" and "configure"
        assert "start" in error_msg or "configure" in error_msg

    def test_flow_state_property_reads_correctly(self):
        """flow_state property should return current state."""
        session = ChatSession.create()

        assert session.flow_state == FlowState.DORMANT

        session.add_turn("Test", "Response")
        assert session.flow_state == FlowState.STREAMING

    def test_awaiting_tool_flag(self):
        """awaiting_tool flag should be accessible."""
        session = ChatSession.create()

        assert session.awaiting_tool is False

        # Manually set the flag
        session._awaiting_tool = True
        assert session.awaiting_tool is True

    def test_compressing_flag(self):
        """is_compressing flag should be accessible."""
        session = ChatSession.create()

        assert session.is_compressing is False

        # Manually set the flag
        session._compressing = True
        assert session.is_compressing is True

    def test_backward_compat_state_updates(self):
        """ChatState should update based on FlowState and flags."""
        session = ChatSession.create()
        session.add_turn("Test", "Response")

        # STREAMING with no flags -> IDLE
        assert session.state == ChatState.IDLE

        # Set awaiting_tool flag
        session._awaiting_tool = True
        session._transition("message")
        assert session.state == ChatState.AWAITING_TOOL

        # Set compressing flag
        session._awaiting_tool = False
        session._compressing = True
        session._transition("message")
        assert session.state == ChatState.COMPRESSING

    def test_to_dict_includes_flow_state(self):
        """to_dict should include flow state and flags."""
        session = ChatSession.create()
        session.add_turn("Test", "Response")
        session._awaiting_tool = True
        session._compressing = False

        data = session.to_dict()

        assert data["flow_state"] == "streaming"
        assert data["awaiting_tool"] is True
        assert data["compressing"] is False

    def test_from_dict_restores_flow_state(self):
        """from_dict should restore flow state and flags."""
        session = ChatSession.create()
        session.add_turn("Test", "Response")
        session._awaiting_tool = True
        session._compressing = True

        data = session.to_dict()
        restored = ChatSession.from_dict(data)

        assert restored.flow_state == FlowState.STREAMING
        assert restored.awaiting_tool is True
        assert restored.is_compressing is True

    def test_round_trip_preserves_flow_state(self):
        """Round-trip serialization should preserve flow state."""
        original = ChatSession.create()
        original.add_turn("Message 1", "Response 1")
        original.add_turn("Message 2", "Response 2")

        data = original.to_dict()
        restored = ChatSession.from_dict(data)

        assert restored.flow_state == original.flow_state
        assert restored.turn_count == original.turn_count

    def test_polynomial_class_variable(self):
        """ChatSession should have CHAT_POLYNOMIAL as class variable."""
        from agents.f.polynomial import CHAT_POLYNOMIAL

        assert ChatSession.polynomial is CHAT_POLYNOMIAL
        assert ChatSession.polynomial.name == "ChatPolynomial"

    def test_valid_actions_in_dormant(self):
        """DORMANT state should allow start and configure."""
        session = ChatSession.create()

        valid_actions = session.polynomial.directions(FlowState.DORMANT)

        assert "start" in valid_actions
        assert "configure" in valid_actions

    def test_valid_actions_in_streaming(self):
        """STREAMING state should allow message, perturb, stop, branch."""
        session = ChatSession.create()
        session.add_turn("Test", "Response")

        valid_actions = session.polynomial.directions(FlowState.STREAMING)

        assert "message" in valid_actions
        assert "perturb" in valid_actions
        assert "stop" in valid_actions
        assert "branch" in valid_actions

    def test_transition_returns_output(self):
        """_transition should return output dict."""
        session = ChatSession.create()

        output = session._transition("start")

        assert isinstance(output, dict)
        assert "event" in output
        assert output["event"] == "started"

    def test_multiple_messages_maintain_streaming(self):
        """Multiple messages should maintain STREAMING state."""
        session = ChatSession.create()

        for i in range(5):
            session.add_turn(f"Message {i}", f"Response {i}")

        assert session.flow_state == FlowState.STREAMING
        assert session.turn_count == 5

    def test_chatstate_to_flowstate_conversion(self):
        """ChatState should have to_flow_state() method."""
        assert ChatState.IDLE.to_flow_state() == FlowState.STREAMING
        assert ChatState.PROCESSING.to_flow_state() == FlowState.STREAMING
        assert ChatState.AWAITING_TOOL.to_flow_state() == FlowState.STREAMING
        assert ChatState.BRANCHING.to_flow_state() == FlowState.BRANCHING
        assert ChatState.COMPRESSING.to_flow_state() == FlowState.STREAMING


class TestFlowStateValidation:
    """Test flow state validation edge cases."""

    def test_cannot_branch_from_dormant(self):
        """Cannot branch before starting session."""
        session = ChatSession.create()

        with pytest.raises(InvalidAction):
            session._transition("branch")

    def test_cannot_message_before_start(self):
        """Cannot send message before starting (handled by add_turn)."""
        session = ChatSession.create()

        # This would fail, but add_turn calls start first
        with pytest.raises(InvalidAction):
            session._transition("message")

    def test_start_transitions_correctly(self):
        """Start action should transition DORMANT -> STREAMING."""
        session = ChatSession.create()

        output = session._transition("start")

        assert session.flow_state == FlowState.STREAMING
        assert output["event"] == "started"

    def test_configure_stays_in_dormant(self):
        """Configure action should keep session in DORMANT."""
        session = ChatSession.create()

        output = session._transition("configure")

        assert session.flow_state == FlowState.DORMANT
        assert output["event"] == "configured"


class TestBackwardCompatibility:
    """Test backward compatibility with old ChatState API."""

    def test_state_property_accessible(self):
        """state property should still be accessible."""
        session = ChatSession.create()

        assert hasattr(session, "state")
        assert session.state == ChatState.IDLE

    def test_old_code_still_works(self):
        """Old code using ChatState should still work."""
        session = ChatSession.create()

        # Old code might check state directly
        if session.state == ChatState.IDLE:
            session.add_turn("Test", "Response")

        assert session.turn_count == 1

    def test_from_dict_handles_missing_flow_state(self):
        """from_dict should handle old data without flow_state."""
        old_data = {
            "id": "test-123",
            "node": {
                "id": "test-123",
                "parent_id": None,
                "fork_point": None,
                "branch_name": "main",
                "created_at": "2025-01-01T12:00:00",
                "last_active": "2025-01-01T12:00:00",
                "turn_count": 0,
                "is_merged": False,
                "merged_into": None,
                "evidence": {
                    "prior": {"alpha": 1.0, "beta": 1.0},
                    "observations": {"success": 0, "failure": 0},
                },
            },
            "state": "idle",
            # No flow_state, awaiting_tool, or compressing
            "context": {"turns": [], "context_window": 8000},
            "evidence": {
                "prior": {"alpha": 1.0, "beta": 1.0},
                "observations": {"success": 0, "failure": 0},
            },
        }

        session = ChatSession.from_dict(old_data)

        # Should default to DORMANT
        assert session.flow_state == FlowState.DORMANT
        assert session.awaiting_tool is False
        assert session.is_compressing is False
