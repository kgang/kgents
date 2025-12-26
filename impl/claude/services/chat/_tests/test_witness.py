"""
Tests for Chat PolicyTrace (Witness Walk) integration.

Tests:
1. ChatMark creation and serialization
2. ChatPolicyTrace adding marks (immutability)
3. Round-trip serialization
4. Mark retrieval by turn number
5. Recent marks retrieval
6. Evidence snapshot preservation
7. Tools tracking
"""

from datetime import datetime, timezone

import pytest

from services.chat.witness import ChatMark, ChatPolicyTrace

# =============================================================================
# ChatMark Tests
# =============================================================================


class TestChatMark:
    """Test ChatMark creation and behavior."""

    def test_minimal_creation(self) -> None:
        """Test creating ChatMark with minimal fields."""
        mark = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="Hello",
            assistant_response="Hi there!",
        )

        assert mark.session_id == "sess-123"
        assert mark.turn_number == 1
        assert mark.user_message == "Hello"
        assert mark.assistant_response == "Hi there!"
        assert mark.tools_used == ()
        assert mark.constitutional_scores is None
        assert mark.evidence_snapshot == {}
        assert mark.reasoning == ""
        assert isinstance(mark.timestamp, datetime)

    def test_full_creation(self) -> None:
        """Test creating ChatMark with all fields."""
        ts = datetime.now(timezone.utc)
        mark = ChatMark(
            session_id="sess-123",
            turn_number=2,
            user_message="What's 2+2?",
            assistant_response="4",
            tools_used=("calculator",),
            constitutional_scores=None,  # Would be PrincipleScore in real usage
            evidence_snapshot={"context_length": 100, "model": "opus-4"},
            reasoning="Simple arithmetic calculation",
            timestamp=ts,
        )

        assert mark.session_id == "sess-123"
        assert mark.turn_number == 2
        assert mark.tools_used == ("calculator",)
        assert mark.evidence_snapshot == {"context_length": 100, "model": "opus-4"}
        assert mark.reasoning == "Simple arithmetic calculation"
        assert mark.timestamp == ts

    def test_summary(self) -> None:
        """Test summary generation."""
        mark = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="Hello",
            assistant_response="Hi there!",
        )

        summary = mark.summary
        assert "Turn 1" in summary
        assert "Hello" in summary
        assert "Hi there!" in summary

    def test_summary_truncates_long_messages(self) -> None:
        """Test that summary truncates very long messages."""
        long_message = "x" * 100
        mark = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message=long_message,
            assistant_response=long_message,
        )

        summary = mark.summary
        assert "..." in summary
        assert len(summary) < 150  # Should be truncated

    def test_immutability(self) -> None:
        """Test that ChatMark is immutable (frozen)."""
        mark = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="Hello",
            assistant_response="Hi",
        )

        with pytest.raises(AttributeError):
            mark.user_message = "Changed"  # type: ignore

    def test_serialization(self) -> None:
        """Test ChatMark serialization to dict."""
        ts = datetime.now(timezone.utc)
        mark = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="Hello",
            assistant_response="Hi",
            tools_used=("search", "calculator"),
            evidence_snapshot={"context": "test"},
            reasoning="Test response",
            timestamp=ts,
        )

        data = mark.to_dict()

        assert data["session_id"] == "sess-123"
        assert data["turn_number"] == 1
        assert data["user_message"] == "Hello"
        assert data["assistant_response"] == "Hi"
        assert data["tools_used"] == ["search", "calculator"]
        assert data["evidence_snapshot"] == {"context": "test"}
        assert data["reasoning"] == "Test response"
        assert data["timestamp"] == ts.isoformat()

    def test_deserialization(self) -> None:
        """Test ChatMark deserialization from dict."""
        ts = datetime.now(timezone.utc)
        data = {
            "session_id": "sess-123",
            "turn_number": 1,
            "user_message": "Hello",
            "assistant_response": "Hi",
            "tools_used": ["search"],
            "evidence_snapshot": {"context": "test"},
            "reasoning": "Test",
            "timestamp": ts.isoformat(),
        }

        mark = ChatMark.from_dict(data)

        assert mark.session_id == "sess-123"
        assert mark.turn_number == 1
        assert mark.user_message == "Hello"
        assert mark.assistant_response == "Hi"
        assert mark.tools_used == ("search",)
        assert mark.evidence_snapshot == {"context": "test"}
        assert mark.reasoning == "Test"
        assert mark.timestamp == ts

    def test_round_trip_serialization(self) -> None:
        """Test that to_dict() -> from_dict() preserves data."""
        original = ChatMark(
            session_id="sess-123",
            turn_number=5,
            user_message="Original message",
            assistant_response="Original response",
            tools_used=("tool1", "tool2"),
            evidence_snapshot={"key": "value"},
            reasoning="Original reasoning",
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = ChatMark.from_dict(data)

        # Check all fields match (except constitutional_scores which is always None in deserialization)
        assert restored.session_id == original.session_id
        assert restored.turn_number == original.turn_number
        assert restored.user_message == original.user_message
        assert restored.assistant_response == original.assistant_response
        assert restored.tools_used == original.tools_used
        assert restored.evidence_snapshot == original.evidence_snapshot
        assert restored.reasoning == original.reasoning
        assert restored.timestamp == original.timestamp


# =============================================================================
# ChatPolicyTrace Tests
# =============================================================================


class TestChatPolicyTrace:
    """Test ChatPolicyTrace behavior."""

    def test_empty_trace(self) -> None:
        """Test creating empty trace."""
        trace = ChatPolicyTrace(session_id="sess-123")

        assert trace.session_id == "sess-123"
        assert trace.marks == ()
        assert trace.turn_count == 0
        assert trace.latest_mark is None

    def test_add_mark(self) -> None:
        """Test adding a mark to trace (immutable append)."""
        trace = ChatPolicyTrace(session_id="sess-123")

        mark1 = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="Hello",
            assistant_response="Hi",
        )

        # Add mark (returns new trace)
        trace2 = trace.add_mark(mark1)

        # Original unchanged
        assert trace.turn_count == 0
        assert len(trace.marks) == 0

        # New trace has mark
        assert trace2.turn_count == 1
        assert len(trace2.marks) == 1
        assert trace2.marks[0] == mark1

    def test_add_multiple_marks(self) -> None:
        """Test adding multiple marks."""
        trace = ChatPolicyTrace(session_id="sess-123")

        mark1 = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="First",
            assistant_response="Response 1",
        )

        mark2 = ChatMark(
            session_id="sess-123",
            turn_number=2,
            user_message="Second",
            assistant_response="Response 2",
        )

        # Add marks sequentially
        trace2 = trace.add_mark(mark1)
        trace3 = trace2.add_mark(mark2)

        assert trace3.turn_count == 2
        assert trace3.marks[0] == mark1
        assert trace3.marks[1] == mark2

    def test_immutability(self) -> None:
        """Test that ChatPolicyTrace is immutable."""
        trace = ChatPolicyTrace(session_id="sess-123")

        with pytest.raises(AttributeError):
            trace.marks = ()  # type: ignore

    def test_get_marks(self) -> None:
        """Test retrieving all marks."""
        trace = ChatPolicyTrace(session_id="sess-123")
        mark1 = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="First",
            assistant_response="R1",
        )
        mark2 = ChatMark(
            session_id="sess-123",
            turn_number=2,
            user_message="Second",
            assistant_response="R2",
        )

        trace = trace.add_mark(mark1).add_mark(mark2)
        marks = trace.get_marks()

        assert len(marks) == 2
        assert marks[0] == mark1
        assert marks[1] == mark2

    def test_get_mark_by_turn_number(self) -> None:
        """Test retrieving specific mark by turn number."""
        trace = ChatPolicyTrace(session_id="sess-123")
        mark1 = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="First",
            assistant_response="R1",
        )
        mark2 = ChatMark(
            session_id="sess-123",
            turn_number=2,
            user_message="Second",
            assistant_response="R2",
        )

        trace = trace.add_mark(mark1).add_mark(mark2)

        # Get by turn number
        retrieved = trace.get_mark(2)
        assert retrieved is not None
        assert retrieved.turn_number == 2
        assert retrieved.user_message == "Second"

        # Non-existent turn
        missing = trace.get_mark(99)
        assert missing is None

    def test_get_recent_marks(self) -> None:
        """Test retrieving N most recent marks."""
        trace = ChatPolicyTrace(session_id="sess-123")

        # Add 5 marks
        for i in range(1, 6):
            mark = ChatMark(
                session_id="sess-123",
                turn_number=i,
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
            )
            trace = trace.add_mark(mark)

        # Get recent 3
        recent = trace.get_recent_marks(3)
        assert len(recent) == 3
        assert recent[0].turn_number == 3
        assert recent[1].turn_number == 4
        assert recent[2].turn_number == 5

        # Get more than available
        all_marks = trace.get_recent_marks(10)
        assert len(all_marks) == 5

    def test_latest_mark(self) -> None:
        """Test getting the latest mark."""
        trace = ChatPolicyTrace(session_id="sess-123")
        assert trace.latest_mark is None

        mark1 = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="First",
            assistant_response="R1",
        )
        mark2 = ChatMark(
            session_id="sess-123",
            turn_number=2,
            user_message="Second",
            assistant_response="R2",
        )

        trace = trace.add_mark(mark1)
        assert trace.latest_mark == mark1

        trace = trace.add_mark(mark2)
        assert trace.latest_mark == mark2

    def test_serialization(self) -> None:
        """Test ChatPolicyTrace serialization."""
        trace = ChatPolicyTrace(session_id="sess-123")
        mark1 = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="Hello",
            assistant_response="Hi",
        )
        trace = trace.add_mark(mark1)

        data = trace.to_dict()

        assert data["session_id"] == "sess-123"
        assert data["turn_count"] == 1
        assert len(data["marks"]) == 1
        assert data["marks"][0]["turn_number"] == 1

    def test_deserialization(self) -> None:
        """Test ChatPolicyTrace deserialization."""
        ts = datetime.now(timezone.utc)
        data = {
            "session_id": "sess-123",
            "turn_count": 2,
            "marks": [
                {
                    "session_id": "sess-123",
                    "turn_number": 1,
                    "user_message": "First",
                    "assistant_response": "R1",
                    "tools_used": [],
                    "evidence_snapshot": {},
                    "reasoning": "",
                    "timestamp": ts.isoformat(),
                },
                {
                    "session_id": "sess-123",
                    "turn_number": 2,
                    "user_message": "Second",
                    "assistant_response": "R2",
                    "tools_used": ["search"],
                    "evidence_snapshot": {"context": "test"},
                    "reasoning": "Test",
                    "timestamp": ts.isoformat(),
                },
            ],
        }

        trace = ChatPolicyTrace.from_dict(data)

        assert trace.session_id == "sess-123"
        assert trace.turn_count == 2
        assert trace.marks[0].turn_number == 1
        assert trace.marks[1].turn_number == 2
        assert trace.marks[1].tools_used == ("search",)

    def test_round_trip_serialization(self) -> None:
        """Test that to_dict() -> from_dict() preserves trace."""
        original = ChatPolicyTrace(session_id="sess-123")

        for i in range(1, 4):
            mark = ChatMark(
                session_id="sess-123",
                turn_number=i,
                user_message=f"Message {i}",
                assistant_response=f"Response {i}",
                tools_used=(f"tool{i}",),
                evidence_snapshot={"turn": i},
                reasoning=f"Reasoning {i}",
            )
            original = original.add_mark(mark)

        # Serialize and deserialize
        data = original.to_dict()
        restored = ChatPolicyTrace.from_dict(data)

        # Check structure matches
        assert restored.session_id == original.session_id
        assert restored.turn_count == original.turn_count
        assert len(restored.marks) == len(original.marks)

        # Check each mark
        for orig_mark, rest_mark in zip(original.marks, restored.marks):
            assert rest_mark.session_id == orig_mark.session_id
            assert rest_mark.turn_number == orig_mark.turn_number
            assert rest_mark.user_message == orig_mark.user_message
            assert rest_mark.assistant_response == orig_mark.assistant_response
            assert rest_mark.tools_used == orig_mark.tools_used
            assert rest_mark.evidence_snapshot == orig_mark.evidence_snapshot
            assert rest_mark.reasoning == orig_mark.reasoning

    def test_repr(self) -> None:
        """Test string representation."""
        trace = ChatPolicyTrace(session_id="sess-123")
        mark = ChatMark(
            session_id="sess-123",
            turn_number=1,
            user_message="Test",
            assistant_response="Response",
        )
        trace = trace.add_mark(mark)

        repr_str = repr(trace)
        assert "sess-123" in repr_str
        assert "turns=1" in repr_str


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Test integration scenarios."""

    def test_multi_turn_conversation_trace(self) -> None:
        """Test a realistic multi-turn conversation trace."""
        trace = ChatPolicyTrace(session_id="conversation-001")

        # Turn 1: Greeting
        trace = trace.add_mark(
            ChatMark(
                session_id="conversation-001",
                turn_number=1,
                user_message="Hello, I need help with Python",
                assistant_response="Hi! I'd be happy to help with Python. What specifically do you need?",
                reasoning="Friendly greeting and clarification",
            )
        )

        # Turn 2: Question with tool use
        trace = trace.add_mark(
            ChatMark(
                session_id="conversation-001",
                turn_number=2,
                user_message="How do I read a file?",
                assistant_response="You can use the built-in open() function...",
                tools_used=("documentation_search",),
                evidence_snapshot={"docs_version": "3.12"},
                reasoning="Provided standard file I/O pattern",
            )
        )

        # Turn 3: Follow-up
        trace = trace.add_mark(
            ChatMark(
                session_id="conversation-001",
                turn_number=3,
                user_message="What about binary files?",
                assistant_response="For binary files, use mode 'rb'...",
                tools_used=("documentation_search", "code_example_generator"),
                evidence_snapshot={"docs_version": "3.12", "context_turns": 2},
                reasoning="Extended previous answer with binary mode",
            )
        )

        # Verify trace structure
        assert trace.turn_count == 3
        assert trace.latest_mark is not None
        assert trace.latest_mark.turn_number == 3

        # Get recent conversation (last 2 turns)
        recent = trace.get_recent_marks(2)
        assert len(recent) == 2
        assert recent[0].turn_number == 2
        assert recent[1].turn_number == 3

        # Verify evidence accumulation
        turn3 = trace.get_mark(3)
        assert turn3 is not None
        assert turn3.evidence_snapshot["context_turns"] == 2

    def test_trace_persistence_simulation(self) -> None:
        """Test simulated persistence (serialize -> deserialize)."""
        # Build trace
        trace = ChatPolicyTrace(session_id="persist-test")
        for i in range(1, 6):
            mark = ChatMark(
                session_id="persist-test",
                turn_number=i,
                user_message=f"User message {i}",
                assistant_response=f"Assistant response {i}",
                tools_used=(f"tool_{i}",) if i % 2 == 0 else (),
                evidence_snapshot={"turn": i, "total_tokens": i * 100},
                reasoning=f"Turn {i} reasoning",
            )
            trace = trace.add_mark(mark)

        # "Save" to dict (simulating DB persistence)
        saved_data = trace.to_dict()

        # "Load" from dict (simulating DB retrieval)
        loaded_trace = ChatPolicyTrace.from_dict(saved_data)

        # Verify identical structure
        assert loaded_trace.session_id == trace.session_id
        assert loaded_trace.turn_count == trace.turn_count

        # Verify each mark preserved
        for original_mark, loaded_mark in zip(trace.marks, loaded_trace.marks):
            assert loaded_mark.turn_number == original_mark.turn_number
            assert loaded_mark.user_message == original_mark.user_message
            assert loaded_mark.assistant_response == original_mark.assistant_response
            assert loaded_mark.tools_used == original_mark.tools_used
            assert loaded_mark.evidence_snapshot == original_mark.evidence_snapshot
