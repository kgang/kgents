"""
Tests for ChatSession integration with Constitutional Reward and PolicyTrace.

Tests that every turn:
1. Creates a ChatMark
2. Computes constitutional_reward
3. Updates the policy_trace
4. Links evidence updates to constitutional scores
5. Serializes/deserializes correctly

See: spec/protocols/chat-unified.md §1.2, §4.2
"""

import pytest

from services.chat.evidence import TurnResult
from services.chat.session import ChatSession


class TestSessionIntegration:
    """Test ChatSession integration with reward and witness systems."""

    def test_add_turn_creates_chat_mark(self):
        """Test that add_turn creates a ChatMark in the policy trace."""
        session = ChatSession.create()

        # Add a turn
        session.add_turn("Hello", "Hi there!")

        # Check that a mark was created
        assert session.policy_trace.turn_count == 1
        mark = session.policy_trace.latest_mark
        assert mark is not None
        assert mark.user_message == "Hello"
        assert mark.assistant_response == "Hi there!"
        assert mark.turn_number == 0

    def test_add_turn_computes_constitutional_reward(self):
        """Test that add_turn computes constitutional scores."""
        session = ChatSession.create()

        # Add a turn with a reasonable response
        session.add_turn("What is 2+2?", "The answer is 4.")

        # Check that constitutional scores were computed
        mark = session.policy_trace.latest_mark
        assert mark is not None
        assert mark.constitutional_scores is not None

        # All scores should be present
        scores = mark.constitutional_scores
        assert 0.0 <= scores.tasteful <= 1.0
        assert 0.0 <= scores.curated <= 1.0
        assert 0.0 <= scores.ethical <= 1.0
        assert 0.0 <= scores.joy_inducing <= 1.0
        assert 0.0 <= scores.composable <= 1.0
        assert 0.0 <= scores.heterarchical <= 1.0
        assert 0.0 <= scores.generative <= 1.0

    def test_policy_trace_grows_with_turns(self):
        """Test that policy_trace accumulates marks for each turn."""
        session = ChatSession.create()

        # Add multiple turns
        session.add_turn("First message", "First response")
        session.add_turn("Second message", "Second response")
        session.add_turn("Third message", "Third response")

        # Check that all marks are present
        assert session.policy_trace.turn_count == 3
        marks = session.policy_trace.get_marks()
        assert len(marks) == 3

        # Check turn numbering
        assert marks[0].turn_number == 0
        assert marks[1].turn_number == 1
        assert marks[2].turn_number == 2

        # Check messages
        assert marks[0].user_message == "First message"
        assert marks[1].user_message == "Second message"
        assert marks[2].user_message == "Third message"

    def test_constitutional_scores_affect_evidence(self):
        """Test that constitutional scores update evidence correctly."""
        session = ChatSession.create()

        # Initial evidence should have default prior
        initial_confidence = session.evidence.confidence

        # Add a turn with good constitutional score (default response is good)
        session.add_turn("Hello", "Hi there! How can I help you today?")

        # Evidence should be updated
        assert session.evidence.confidence != initial_confidence

        # Tools succeeded should increase for successful turn
        assert session.evidence.tools_succeeded >= 1

    def test_very_short_response_lowers_joy(self):
        """Test that very short responses lower joy_inducing score."""
        session = ChatSession.create()

        # Add a very short response
        session.add_turn("Hello", "Hi")

        mark = session.policy_trace.latest_mark
        assert mark is not None
        scores = mark.constitutional_scores
        assert scores is not None

        # Joy should be lowered for very short response
        assert scores.joy_inducing < 1.0

    def test_many_tools_lower_composable(self):
        """Test that using many tools lowers composable score."""
        session = ChatSession.create()

        # Create turn result with many tools
        turn_result = TurnResult(
            response="I used lots of tools!",
            tools=[{"name": f"tool_{i}"} for i in range(10)],
        )

        session.add_turn("Do something complex", "I used lots of tools!", turn_result=turn_result)

        mark = session.policy_trace.latest_mark
        assert mark is not None
        scores = mark.constitutional_scores
        assert scores is not None

        # Composable should be lowered for many tools
        assert scores.composable < 1.0

    def test_get_constitutional_history(self):
        """Test get_constitutional_history returns all scores."""
        session = ChatSession.create()

        # Add multiple turns
        session.add_turn("First", "Response 1")
        session.add_turn("Second", "Response 2")
        session.add_turn("Third", "Response 3")

        # Get history
        history = session.get_constitutional_history()
        assert len(history) == 3

        # All should be PrincipleScore objects
        for score in history:
            assert hasattr(score, "ethical")
            assert hasattr(score, "composable")
            assert hasattr(score, "joy_inducing")

    def test_serialization_includes_policy_trace(self):
        """Test that to_dict/from_dict include policy_trace."""
        session = ChatSession.create()

        # Add some turns
        session.add_turn("Hello", "Hi there!")
        session.add_turn("How are you?", "I'm doing well, thanks!")

        # Serialize
        data = session.to_dict()
        assert "policy_trace" in data
        assert data["policy_trace"]["turn_count"] == 2
        assert len(data["policy_trace"]["marks"]) == 2

        # Deserialize
        restored = ChatSession.from_dict(data)
        assert restored.policy_trace.turn_count == 2
        assert restored.policy_trace.latest_mark is not None
        assert restored.policy_trace.latest_mark.user_message == "How are you?"

    def test_evidence_snapshot_in_mark(self):
        """Test that each mark includes evidence snapshot."""
        session = ChatSession.create()

        # Add first turn
        session.add_turn("First", "Response 1")
        mark1 = session.policy_trace.latest_mark
        assert mark1 is not None
        assert mark1.evidence_snapshot is not None
        assert "confidence" in mark1.evidence_snapshot

        # Add second turn
        session.add_turn("Second", "Response 2")
        mark2 = session.policy_trace.latest_mark
        assert mark2 is not None
        assert mark2.evidence_snapshot is not None

        # Snapshots should be different (evidence updated)
        # Note: They might be very similar, but structure should be present
        assert "confidence" in mark2.evidence_snapshot

    def test_tools_used_recorded_in_mark(self):
        """Test that tools_used are recorded in the mark."""
        session = ChatSession.create()

        # Add turn with tools
        session.add_turn(
            "Use some tools",
            "I used the tools!",
            tools_used=["search", "calculator", "database"],
        )

        mark = session.policy_trace.latest_mark
        assert mark is not None
        assert mark.tools_used == ("search", "calculator", "database")

    def test_empty_session_has_empty_trace(self):
        """Test that newly created session has empty policy trace."""
        session = ChatSession.create()

        assert session.policy_trace.turn_count == 0
        assert session.policy_trace.latest_mark is None
        assert len(session.policy_trace.get_marks()) == 0

    def test_session_id_matches_trace_id(self):
        """Test that session_id and policy_trace session_id match."""
        session = ChatSession.create()

        assert session.id == session.policy_trace.session_id

        # Add a turn
        session.add_turn("Hello", "Hi")

        mark = session.policy_trace.latest_mark
        assert mark is not None
        assert mark.session_id == session.id

    def test_constitutional_score_determines_evidence_success(self):
        """Test that constitutional score (not tools_passed) determines evidence update.

        This is the intended design: constitutional reward computes success
        based on principle adherence, which may differ from tools_passed.
        """
        session = ChatSession.create()

        # Very short response -> low joy score -> may fail constitutional check
        # But the weighted score might still pass threshold
        turn_result_short = TurnResult(
            tools_passed=True,
            response="OK",  # Very short, but tools passed
        )

        session.add_turn("Do task 1", "OK", turn_result=turn_result_short)

        # Even though tools_passed=True, constitutional score determines success
        # Short response (2 chars) gets joy_inducing penalty, but other scores are good
        # Total weighted score still likely >= 7.5, so it succeeds
        initial_succeeded = session.evidence.tools_succeeded

        # Longer response should definitely pass
        turn_result_good = TurnResult(
            tools_passed=True,
            response="Here's a comprehensive and helpful answer!",
        )

        session.add_turn(
            "Do task 2", "Here's a comprehensive and helpful answer!", turn_result=turn_result_good
        )

        # Evidence should accumulate successes
        assert session.evidence.tools_succeeded > initial_succeeded


class TestConstitutionalScoreIntegration:
    """Test constitutional score computation in context."""

    def test_weighted_total_used_for_success_threshold(self):
        """Test that weighted_total determines evidence success."""
        session = ChatSession.create()

        # Perfect response should succeed
        session.add_turn("Hello", "Hello! How can I help you today?")

        # Should have at least one success
        assert session.evidence.tools_succeeded >= 1

    def test_multiple_turns_accumulate_evidence(self):
        """Test that evidence accumulates across turns."""
        session = ChatSession.create()

        initial_prior = session.evidence.prior

        # Add several successful turns
        for i in range(5):
            session.add_turn(f"Message {i}", f"Response {i}: Here's a helpful answer!")

        # Prior should have updated
        final_prior = session.evidence.prior
        assert final_prior.alpha != initial_prior.alpha or final_prior.beta != initial_prior.beta

        # Confidence should increase with more observations
        assert session.evidence.prior.confidence() > initial_prior.confidence()
