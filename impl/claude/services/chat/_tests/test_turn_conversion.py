"""
Test Turn conversion between API and service layers.

Verifies:
- Service Turn -> API Turn conversion
- API Turn -> Service Turn conversion
- Round-trip conversion preserves data
"""

from datetime import datetime

import pytest

from protocols.api.chat import EvidenceDelta, Message, ToolUse
from protocols.api.chat import Turn as ApiTurn
from services.chat.context import LinearityTag
from services.chat.context import Turn as ServiceTurn


def test_service_to_api_conversion():
    """Test converting service Turn to API Turn."""
    # Create service turn
    service_turn = ServiceTurn(
        turn_number=1,
        user_message="Hello, world!",
        assistant_response="Hi there!",
        linearity_tag=LinearityTag.REQUIRED,
        tools_used=["Read", "Write"],
        started_at=datetime(2025, 1, 1, 12, 0, 0),
        completed_at=datetime(2025, 1, 1, 12, 0, 5),
        metadata={"confidence": 0.9},
    )

    # Convert to API turn
    api_turn = service_turn.to_api_turn()

    # Verify structure
    assert isinstance(api_turn, ApiTurn)
    assert api_turn.turn_number == 1

    # Verify user message
    assert isinstance(api_turn.user_message, Message)
    assert api_turn.user_message.role == "user"
    assert api_turn.user_message.content == "Hello, world!"
    assert api_turn.user_message.linearity_tag == "required"
    assert api_turn.user_message.mentions == []

    # Verify assistant message
    assert isinstance(api_turn.assistant_response, Message)
    assert api_turn.assistant_response.role == "assistant"
    assert api_turn.assistant_response.content == "Hi there!"
    assert api_turn.assistant_response.linearity_tag == "required"

    # Verify evidence delta
    assert isinstance(api_turn.evidence_delta, EvidenceDelta)
    assert api_turn.evidence_delta.tools_executed == 2  # Two tools
    assert api_turn.evidence_delta.tools_succeeded == 2  # Assume success

    # Verify metadata
    assert api_turn.confidence == 0.9
    assert api_turn.started_at == "2025-01-01T12:00:00"
    assert api_turn.completed_at == "2025-01-01T12:00:05"


def test_api_to_service_conversion():
    """Test converting API Turn to service Turn."""
    # Create API turn
    api_turn = ApiTurn(
        turn_number=2,
        user_message=Message(
            role="user",
            content="What is the meaning of life?",
            mentions=[],
            linearity_tag="preserved",
        ),
        assistant_response=Message(
            role="assistant",
            content="42, of course!",
            mentions=[],
            linearity_tag="preserved",
        ),
        tools_used=[
            ToolUse(
                name="WebSearch",
                input={"query": "meaning of life"},
                output="...",
                success=True,
                duration_ms=100.0,
            )
        ],
        evidence_delta=EvidenceDelta(
            tools_executed=1,
            tools_succeeded=1,
            confidence_change=0.1,
        ),
        confidence=0.85,
        started_at="2025-01-01T13:00:00",
        completed_at="2025-01-01T13:00:10",
    )

    # Convert to service turn
    service_turn = ServiceTurn.from_api_turn(api_turn)

    # Verify structure
    assert isinstance(service_turn, ServiceTurn)
    assert service_turn.turn_number == 2

    # Verify messages extracted
    assert service_turn.user_message == "What is the meaning of life?"
    assert service_turn.assistant_response == "42, of course!"

    # Verify linearity tag
    assert service_turn.linearity_tag == LinearityTag.PRESERVED

    # Verify tools
    assert service_turn.tools_used == ["WebSearch"]

    # Verify timestamps
    assert service_turn.started_at == datetime(2025, 1, 1, 13, 0, 0)
    assert service_turn.completed_at == datetime(2025, 1, 1, 13, 0, 10)

    # Verify metadata
    assert service_turn.metadata["confidence"] == 0.85


def test_round_trip_conversion():
    """Test round-trip conversion preserves content."""
    # Start with service turn
    original_service = ServiceTurn(
        turn_number=3,
        user_message="Test message",
        assistant_response="Test response",
        linearity_tag=LinearityTag.DROPPABLE,
        tools_used=["Grep"],
        started_at=datetime(2025, 1, 2, 10, 0, 0),
        completed_at=datetime(2025, 1, 2, 10, 0, 3),
        metadata={"confidence": 0.75},
    )

    # Convert to API and back
    api_turn = original_service.to_api_turn()
    round_trip_service = ServiceTurn.from_api_turn(api_turn)

    # Verify content preserved
    assert round_trip_service.turn_number == original_service.turn_number
    assert round_trip_service.user_message == original_service.user_message
    assert round_trip_service.assistant_response == original_service.assistant_response
    assert round_trip_service.linearity_tag == original_service.linearity_tag
    assert round_trip_service.tools_used == original_service.tools_used
    assert round_trip_service.started_at == original_service.started_at
    assert round_trip_service.completed_at == original_service.completed_at
    assert round_trip_service.metadata["confidence"] == original_service.metadata["confidence"]


def test_linearity_tag_conversion():
    """Test all linearity tag values convert correctly."""
    for tag in [LinearityTag.REQUIRED, LinearityTag.PRESERVED, LinearityTag.DROPPABLE]:
        service_turn = ServiceTurn(
            user_message="test",
            assistant_response="test",
            linearity_tag=tag,
        )

        api_turn = service_turn.to_api_turn()
        assert api_turn.user_message.linearity_tag == tag.value

        round_trip = ServiceTurn.from_api_turn(api_turn)
        assert round_trip.linearity_tag == tag


def test_empty_tools_conversion():
    """Test conversion with no tools used."""
    service_turn = ServiceTurn(
        user_message="test",
        assistant_response="test",
        tools_used=[],
    )

    api_turn = service_turn.to_api_turn()
    assert api_turn.evidence_delta.tools_executed == 0
    assert api_turn.evidence_delta.tools_succeeded == 0
    assert api_turn.tools_used == []

    round_trip = ServiceTurn.from_api_turn(api_turn)
    assert round_trip.tools_used == []


def test_default_completed_at():
    """Test conversion handles missing completed_at."""
    service_turn = ServiceTurn(
        user_message="test",
        assistant_response="test",
        started_at=datetime(2025, 1, 1, 12, 0, 0),
        completed_at=None,  # Not completed yet
    )

    api_turn = service_turn.to_api_turn()
    # Should use current time
    assert api_turn.completed_at is not None
    assert isinstance(api_turn.completed_at, str)
