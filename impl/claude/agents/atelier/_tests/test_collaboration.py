"""
Tests for collaboration and composition.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, AsyncIterator, cast
from unittest.mock import AsyncMock, patch

import pytest

if TYPE_CHECKING:
    from collections.abc import Sequence

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
from agents.atelier.workshop.collaboration import (
    Collaboration,
    CollaborationMode,
)
from agents.atelier.workshop.operad import (
    ATELIER_OPERAD,
    AtelierOperad,
    CompositionLaw,
    Operation,
)


class TestAtelierOperad:
    """Tests for the composition grammar."""

    def test_solo_operation(self) -> None:
        """Solo operation exists with arity 1."""
        op = ATELIER_OPERAD.get("solo")
        assert op is not None
        assert op.arity == 1
        assert op.law == CompositionLaw.SEQUENTIAL

    def test_duet_operation(self) -> None:
        """Duet operation exists with arity 2."""
        op = ATELIER_OPERAD.get("duet")
        assert op is not None
        assert op.arity == 2

    def test_ensemble_is_variadic(self) -> None:
        """Ensemble accepts any number of artisans."""
        op = ATELIER_OPERAD.get("ensemble")
        assert op is not None
        assert op.arity == "*"
        assert op.accepts_arity(1)
        assert op.accepts_arity(5)
        assert op.accepts_arity(100)

    def test_validate_operation(self) -> None:
        """Can validate operation for artisan count."""
        assert ATELIER_OPERAD.validate("solo", 1) is True
        assert ATELIER_OPERAD.validate("solo", 2) is False
        assert ATELIER_OPERAD.validate("duet", 2) is True
        assert ATELIER_OPERAD.validate("ensemble", 10) is True

    def test_list_operations(self) -> None:
        """Can list all operations."""
        ops = ATELIER_OPERAD.list_operations()
        assert "solo" in ops
        assert "duet" in ops
        assert "ensemble" in ops
        assert "refinement" in ops
        assert "chain" in ops


class MockArtisan(Artisan):
    """Mock artisan for testing collaborations."""

    name: str  # Override class attribute with instance attribute

    def __init__(self, name: str = "Mock", content: str = "mock content") -> None:
        super().__init__()
        self.name = name
        self._content = content

    async def work(self) -> AsyncIterator[AtelierEvent]:
        """Simple mock work that yields a piece."""
        if not self.current_commission:
            yield AtelierEvent(
                event_type=AtelierEventType.ERROR,
                artisan=self.name,
                commission_id=None,
                message="No commission",
            )
            return

        self.state = ArtisanState.WORKING

        yield AtelierEvent(
            event_type=AtelierEventType.WORKING,
            artisan=self.name,
            commission_id=self.current_commission.id,
            message="working...",
        )

        piece = Piece(
            content=f"{self._content} (based on: {self.current_commission.request[:20]})",
            artisan=self.name,
            commission_id=self.current_commission.id,
            form="test",
            provenance=Provenance(
                interpretation=self.current_commission.request,
                considerations=["mock consideration"],
                choices=[
                    Choice(decision="mock choice", reason="mock", alternatives=[])
                ],
                inspirations=[],
            ),
        )

        self.memory.append(piece)
        self.state = ArtisanState.READY
        self.current_commission = None

        yield AtelierEvent(
            event_type=AtelierEventType.PIECE_COMPLETE,
            artisan=self.name,
            commission_id=piece.commission_id,
            message="complete",
            data={"piece": piece.to_dict()},
        )


class TestCollaboration:
    """Tests for multi-artisan collaboration."""

    @pytest.mark.asyncio
    async def test_duet_mode(self) -> None:
        """Duet produces piece with both artisans involved."""
        artisan_a = MockArtisan("Alice", "alice's work")
        artisan_b = MockArtisan("Bob", "bob's work")

        collab = Collaboration([artisan_a, artisan_b], CollaborationMode.DUET)
        commission = Commission(request="test duet")

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        # Should have events from both artisans
        artisan_names = {e.artisan for e in events}
        assert "Alice" in artisan_names
        assert "Bob" in artisan_names

        # Should have piece complete
        complete_events = [
            e for e in events if e.event_type == AtelierEventType.PIECE_COMPLETE
        ]
        assert len(complete_events) >= 1

    @pytest.mark.asyncio
    async def test_duet_requires_two_artisans(self) -> None:
        """Duet with one artisan yields error."""
        collab = Collaboration([MockArtisan()], CollaborationMode.DUET)
        commission = Commission(request="test")

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        assert any(e.event_type == AtelierEventType.ERROR for e in events)

    @pytest.mark.asyncio
    async def test_ensemble_parallel_work(self) -> None:
        """Ensemble runs artisans in parallel."""
        artisans = [
            MockArtisan("A", "content A"),
            MockArtisan("B", "content B"),
            MockArtisan("C", "content C"),
        ]

        collab = Collaboration(
            cast(list[Artisan], artisans), CollaborationMode.ENSEMBLE
        )
        commission = Commission(request="test ensemble")

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        # Final piece should be from "Ensemble"
        complete_events = [
            e for e in events if e.event_type == AtelierEventType.PIECE_COMPLETE
        ]
        final = complete_events[-1]
        assert final.artisan == "Ensemble"

        # Final piece should contain all artisans' work
        piece_data = final.data["piece"]
        assert "A" in piece_data["content"]
        assert "B" in piece_data["content"]
        assert "C" in piece_data["content"]

    @pytest.mark.asyncio
    async def test_refinement_mode(self) -> None:
        """Refinement has second artisan improve first's work."""
        artisan_a = MockArtisan("First", "initial work")
        artisan_b = MockArtisan("Refiner", "refined work")

        collab = Collaboration(
            cast(list[Artisan], [artisan_a, artisan_b]), CollaborationMode.REFINEMENT
        )
        commission = Commission(request="test refinement")

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        # Should have refinement in provenance
        complete_events = [
            e for e in events if e.event_type == AtelierEventType.PIECE_COMPLETE
        ]
        final = complete_events[-1]
        choices = final.data["piece"]["provenance"]["choices"]
        assert any("Refined" in c.get("decision", "") for c in choices)

    @pytest.mark.asyncio
    async def test_chain_mode(self) -> None:
        """Chain mode passes output through multiple artisans."""
        artisans = [
            MockArtisan("First", "first"),
            MockArtisan("Second", "second"),
            MockArtisan("Third", "third"),
        ]

        collab = Collaboration(cast(list[Artisan], artisans), CollaborationMode.CHAIN)
        commission = Commission(request="start the chain")

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        # Should have piece complete events from all artisans
        complete_events = [
            e for e in events if e.event_type == AtelierEventType.PIECE_COMPLETE
        ]
        assert len(complete_events) == 3

    @pytest.mark.asyncio
    async def test_collaboration_mode_from_string(self) -> None:
        """Can create collaboration with string mode."""
        collab = Collaboration([MockArtisan(), MockArtisan()], "duet")
        assert collab.mode == CollaborationMode.DUET


class TestOperationLaws:
    """Tests for operad composition laws."""

    def test_sequential_law(self) -> None:
        """Sequential operations chain outputs to inputs."""
        op = ATELIER_OPERAD.get("duet")
        assert op is not None
        assert op.law == CompositionLaw.SEQUENTIAL

    def test_parallel_law(self) -> None:
        """Parallel operations merge results."""
        op = ATELIER_OPERAD.get("ensemble")
        assert op is not None
        assert op.law == CompositionLaw.PARALLEL_MERGE

    def test_iterative_law(self) -> None:
        """Iterative operations refine."""
        op = ATELIER_OPERAD.get("refinement")
        assert op is not None
        assert op.law == CompositionLaw.ITERATIVE
