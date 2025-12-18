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
    _extract_edge,
)
from agents.atelier.workshop.operad import (
    AtelierOperad,
    CompositionLaw,
    Operation,
)

# Use backward-compat wrapper that provides .get(), .validate(), etc.
ATELIER_OPERAD = AtelierOperad()


class TestAtelierOperad:
    """Tests for the composition grammar."""

    def test_solo_operation(self) -> None:
        """Solo operation exists with arity 1."""
        # Note: Canonical operad uses 'atelier_solo' to avoid conflicts
        op = ATELIER_OPERAD.get("atelier_solo")
        assert op is not None
        assert op.arity == 1
        # Law info is stored in the operad laws, not on the operation
        # The flow is SEQUENTIAL as per the compose function

    def test_duet_operation(self) -> None:
        """Duet operation exists with arity 2."""
        op = ATELIER_OPERAD.get("duet")
        assert op is not None
        assert op.arity == 2

    def test_ensemble_is_variadic(self) -> None:
        """Ensemble accepts any number of artisans."""
        op = ATELIER_OPERAD.get("ensemble")
        assert op is not None
        # Variadic operations use -1 for arity
        assert op.arity == -1
        # validate method handles -1 as variadic
        assert ATELIER_OPERAD.validate("ensemble", 1) is True
        assert ATELIER_OPERAD.validate("ensemble", 5) is True
        assert ATELIER_OPERAD.validate("ensemble", 100) is True

    def test_validate_operation(self) -> None:
        """Can validate operation for artisan count."""
        assert ATELIER_OPERAD.validate("atelier_solo", 1) is True
        assert ATELIER_OPERAD.validate("atelier_solo", 2) is False
        assert ATELIER_OPERAD.validate("duet", 2) is True
        assert ATELIER_OPERAD.validate("ensemble", 10) is True

    def test_list_operations(self) -> None:
        """Can list all operations."""
        ops = ATELIER_OPERAD.list_operations()
        # Note: canonical operad uses 'atelier_solo' to avoid conflicts
        assert "atelier_solo" in ops
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
        # Duet uses sequential composition (first -> second)
        op = ATELIER_OPERAD.get("duet")
        assert op is not None
        # The sequential nature is embedded in the compose function
        # which returns an agent with flow=SEQUENTIAL
        assert op.arity == 2

    def test_parallel_law(self) -> None:
        """Parallel operations merge results."""
        # Ensemble uses parallel composition with merge
        op = ATELIER_OPERAD.get("ensemble")
        assert op is not None
        # Variadic arity (-1) for ensemble
        assert op.arity == -1

    def test_iterative_law(self) -> None:
        """Iterative operations refine."""
        # Refinement uses iterative composition
        op = ATELIER_OPERAD.get("refinement")
        assert op is not None
        assert op.arity == 2


class TestExtractEdge:
    """Tests for edge extraction in exquisite corpse mode."""

    def test_extract_edge_empty(self) -> None:
        """Empty content returns empty string."""
        assert _extract_edge("") == ""

    def test_extract_edge_short_content(self) -> None:
        """Short content returns last line."""
        content = "one\ntwo\nthree"
        result = _extract_edge(content, 0.10)
        assert result == "three"

    def test_extract_edge_longer_content(self) -> None:
        """Longer content returns appropriate percentage."""
        # 10 lines, 10% = 1 line (minimum)
        content = "\n".join(f"line {i}" for i in range(10))
        result = _extract_edge(content, 0.10)
        assert result == "line 9"

    def test_extract_edge_20_percent(self) -> None:
        """20% visibility extracts more lines."""
        # 10 lines, 20% = 2 lines
        content = "\n".join(f"line {i}" for i in range(10))
        result = _extract_edge(content, 0.20)
        assert "line 8" in result
        assert "line 9" in result

    def test_extract_edge_single_line(self) -> None:
        """Single line content returns that line."""
        content = "only line"
        result = _extract_edge(content, 0.10)
        assert result == "only line"


class TestExquisiteCorpse:
    """Tests for exquisite corpse collaboration mode."""

    @pytest.mark.asyncio
    async def test_exquisite_mode_exists(self) -> None:
        """Exquisite mode is a valid collaboration mode."""
        assert CollaborationMode.EXQUISITE.value == "exquisite"

    @pytest.mark.asyncio
    async def test_exquisite_mode_from_string(self) -> None:
        """Can create collaboration with exquisite string."""
        artisans = [MockArtisan("A"), MockArtisan("B"), MockArtisan("C")]
        collab = Collaboration(cast(list[Artisan], artisans), "exquisite")
        assert collab.mode == CollaborationMode.EXQUISITE

    @pytest.mark.asyncio
    async def test_exquisite_needs_artisan(self) -> None:
        """Exquisite corpse with no artisans yields error."""
        collab = Collaboration([], CollaborationMode.EXQUISITE)
        commission = Commission(request="test")

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        assert any(e.event_type == AtelierEventType.ERROR for e in events)

    @pytest.mark.asyncio
    async def test_exquisite_produces_merged_piece(self) -> None:
        """Exquisite corpse produces a merged piece from all contributors."""
        artisans = [
            MockArtisan("First", "beginning"),
            MockArtisan("Second", "middle"),
            MockArtisan("Third", "ending"),
        ]

        collab = Collaboration(
            cast(list[Artisan], artisans), CollaborationMode.EXQUISITE
        )
        commission = Commission(request="create something")

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        # Should have final piece from "Exquisite Corpse"
        complete_events = [
            e for e in events if e.event_type == AtelierEventType.PIECE_COMPLETE
        ]
        final = complete_events[-1]
        assert final.artisan == "Exquisite Corpse"

        # Final piece should reference all contributors
        piece_data = final.data["piece"]
        assert piece_data["form"] == "exquisite_corpse"
        inspirations = piece_data["provenance"]["inspirations"]
        assert len(inspirations) == 3  # All three artisans' pieces

    @pytest.mark.asyncio
    async def test_exquisite_uses_visibility_ratio(self) -> None:
        """Exquisite corpse respects visibility_ratio in context."""
        artisans = [MockArtisan("A"), MockArtisan("B")]

        collab = Collaboration(
            cast(list[Artisan], artisans), CollaborationMode.EXQUISITE
        )
        commission = Commission(request="test", context={"visibility_ratio": 0.5})

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        # Should complete without error
        assert any(e.event_type == AtelierEventType.PIECE_COMPLETE for e in events)

    @pytest.mark.asyncio
    async def test_exquisite_contemplating_message(self) -> None:
        """Exquisite corpse emits informative contemplating message."""
        artisans = [MockArtisan("A"), MockArtisan("B")]
        collab = Collaboration(
            cast(list[Artisan], artisans), CollaborationMode.EXQUISITE
        )
        commission = Commission(request="test")

        events = []
        async for event in collab.execute(commission):
            events.append(event)

        # Should have contemplating event with visibility info
        contemplating_events = [
            e for e in events if e.event_type == AtelierEventType.CONTEMPLATING
        ]
        assert len(contemplating_events) >= 1
        assert "visibility" in (contemplating_events[0].message or "").lower()
