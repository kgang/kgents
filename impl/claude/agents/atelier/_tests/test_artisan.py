"""
Tests for artisan infrastructure.
"""

from __future__ import annotations

from datetime import datetime

import pytest
from agents.atelier.artisan import (
    Artisan,
    ArtisanState,
    AtelierEvent,
    AtelierEventType,
    Choice,
    Commission,
    Piece,
    Provenance,
)


class TestCommission:
    """Tests for Commission dataclass."""

    def test_create_default(self) -> None:
        """Can create a commission with defaults."""
        comm = Commission(request="test request")
        assert comm.request == "test request"
        assert comm.patron == "wanderer"
        assert len(comm.id) == 8
        assert isinstance(comm.created_at, datetime)

    def test_create_with_patron(self) -> None:
        """Can specify patron."""
        comm = Commission(request="test", patron="alice")
        assert comm.patron == "alice"

    def test_to_dict(self) -> None:
        """Can serialize to dict."""
        comm = Commission(request="test", patron="bob")
        data = comm.to_dict()

        assert data["request"] == "test"
        assert data["patron"] == "bob"
        assert "id" in data
        assert "created_at" in data

    def test_from_dict(self) -> None:
        """Can deserialize from dict."""
        comm = Commission(request="test", patron="bob")
        data = comm.to_dict()

        restored = Commission.from_dict(data)
        assert restored.id == comm.id
        assert restored.request == comm.request
        assert restored.patron == comm.patron


class TestProvenance:
    """Tests for Provenance dataclass."""

    def test_create_basic(self) -> None:
        """Can create basic provenance."""
        prov = Provenance(
            interpretation="understood the request",
            considerations=["thought about this", "and that"],
            choices=[],
        )
        assert prov.interpretation == "understood the request"
        assert len(prov.considerations) == 2

    def test_with_choices(self) -> None:
        """Can include choices."""
        prov = Provenance(
            interpretation="test",
            considerations=[],
            choices=[
                Choice(
                    decision="chose haiku", reason="felt right", alternatives=["sonnet"]
                ),
            ],
        )
        assert len(prov.choices) == 1
        assert prov.choices[0].decision == "chose haiku"

    def test_round_trip(self) -> None:
        """Can serialize and deserialize."""
        prov = Provenance(
            interpretation="test",
            considerations=["a", "b"],
            choices=[Choice(decision="x", reason="y", alternatives=["z"])],
            inspirations=["abc123"],
        )

        restored = Provenance.from_dict(prov.to_dict())
        assert restored.interpretation == prov.interpretation
        assert restored.inspirations == prov.inspirations


class TestPiece:
    """Tests for Piece dataclass."""

    def test_create_basic(self) -> None:
        """Can create a piece."""
        piece = Piece(
            content="a haiku about tests",
            artisan="The Calligrapher",
            commission_id="abc123",
            provenance=Provenance(
                interpretation="test",
                considerations=[],
                choices=[],
            ),
        )
        assert piece.content == "a haiku about tests"
        assert piece.form == "reflection"  # default
        assert len(piece.id) == 8

    def test_round_trip(self) -> None:
        """Can serialize and deserialize."""
        piece = Piece(
            content="test content",
            artisan="Test Artisan",
            commission_id="comm123",
            form="haiku",
            provenance=Provenance(
                interpretation="test",
                considerations=["a"],
                choices=[],
                inspirations=["prev1"],
            ),
        )

        restored = Piece.from_dict(piece.to_dict())
        assert restored.id == piece.id
        assert restored.content == piece.content
        assert restored.form == "haiku"
        assert restored.provenance.inspirations == ["prev1"]


class TestAtelierEvent:
    """Tests for AtelierEvent dataclass."""

    def test_create_event(self) -> None:
        """Can create an event."""
        event = AtelierEvent(
            event_type=AtelierEventType.WORKING,
            artisan="Test",
            commission_id="abc",
            message="working on it",
        )
        assert event.event_type == AtelierEventType.WORKING
        assert event.artisan == "Test"

    def test_to_dict(self) -> None:
        """Can serialize to dict."""
        event = AtelierEvent(
            event_type=AtelierEventType.PIECE_COMPLETE,
            artisan="Test",
            commission_id="abc",
            data={"piece": {"id": "123"}},
        )
        data = event.to_dict()

        assert data["event_type"] == "piece_complete"
        assert data["data"]["piece"]["id"] == "123"


class TestArtisanState:
    """Tests for artisan state machine."""

    def test_states_exist(self) -> None:
        """All expected states exist."""
        assert ArtisanState.IDLE
        assert ArtisanState.CONTEMPLATING
        assert ArtisanState.WORKING
        assert ArtisanState.READY


class TestBaseArtisan:
    """Tests for base Artisan class."""

    def test_has_required_attributes(self) -> None:
        """Base artisan has required attributes."""
        artisan = Artisan()
        assert hasattr(artisan, "name")
        assert hasattr(artisan, "specialty")
        assert hasattr(artisan, "state")
        assert artisan.state == ArtisanState.IDLE

    @pytest.mark.asyncio
    async def test_receive_changes_state(self) -> None:
        """Receiving a commission changes state."""
        artisan = Artisan()
        comm = Commission(request="test")

        events = []
        async for event in artisan.receive(comm):
            events.append(event)

        assert artisan.state == ArtisanState.CONTEMPLATING
        assert artisan.current_commission == comm
        assert len(events) >= 2  # received + contemplating

    @pytest.mark.asyncio
    async def test_receive_when_busy_errors(self) -> None:
        """Cannot receive commission when busy."""
        artisan = Artisan()
        artisan.state = ArtisanState.WORKING

        events = []
        async for event in artisan.receive(Commission(request="test")):
            events.append(event)

        assert len(events) == 1
        assert events[0].event_type == AtelierEventType.ERROR

    @pytest.mark.asyncio
    async def test_work_not_implemented(self) -> None:
        """Base artisan work() raises NotImplementedError."""
        artisan = Artisan()
        artisan.state = ArtisanState.CONTEMPLATING
        artisan.current_commission = Commission(request="test")

        # work() raises NotImplementedError immediately when called
        with pytest.raises(NotImplementedError):
            await artisan.work()  # type: ignore
