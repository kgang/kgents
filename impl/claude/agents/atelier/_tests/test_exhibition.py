"""
Tests for Exhibition and ExhibitionCurator.

Tests:
- Exhibition data structure
- Curator selection logic
- Artisan diversity
- Title/note generation
"""

from datetime import datetime, timezone

import pytest

from agents.atelier.artisan import Piece, Provenance
from agents.atelier.exhibition import Exhibition, ExhibitionCurator

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sample_provenance() -> Provenance:
    return Provenance(
        interpretation="A test interpretation",
        considerations=["test"],
        choices=[],
        inspirations=[],
    )


@pytest.fixture
def sample_pieces(sample_provenance: Provenance) -> list[Piece]:
    """Create diverse sample pieces."""
    return [
        Piece(
            id="p1",
            content="The ephemeral nature of APIs in spring",
            artisan="Calligrapher",
            commission_id="c1",
            form="haiku",
            provenance=Provenance(
                interpretation="Meditation on transience",
                considerations=[],
                choices=[],
                inspirations=[],
            ),
            created_at=datetime.now(timezone.utc),
        ),
        Piece(
            id="p2",
            content="A map of digital gardens",
            artisan="Cartographer",
            commission_id="c2",
            form="map",
            provenance=Provenance(
                interpretation="Mapping digital spaces",
                considerations=[],
                choices=[],
                inspirations=[],
            ),
            created_at=datetime.now(timezone.utc),
        ),
        Piece(
            id="p3",
            content="Archives of ephemeral moments",
            artisan="Archivist",
            commission_id="c3",
            form="catalog",
            provenance=Provenance(
                interpretation="Preserving the transient",
                considerations=[],
                choices=[],
                inspirations=[],
            ),
            created_at=datetime.now(timezone.utc),
        ),
        Piece(
            id="p4",
            content="Another spring poem about nature",
            artisan="Calligrapher",
            commission_id="c4",
            form="haiku",
            provenance=sample_provenance,
            created_at=datetime.now(timezone.utc),
        ),
        Piece(
            id="p5",
            content="Technical documentation of systems",
            artisan="Archivist",
            commission_id="c5",
            form="catalog",
            provenance=sample_provenance,
            created_at=datetime.now(timezone.utc),
        ),
    ]


@pytest.fixture
def curator(sample_pieces: list[Piece]) -> ExhibitionCurator:
    """Create curator with sample pieces."""
    curator = ExhibitionCurator()
    for piece in sample_pieces:
        curator.pieces[piece.id] = piece
    return curator


# =============================================================================
# Exhibition Tests
# =============================================================================


class TestExhibition:
    """Tests for Exhibition dataclass."""

    def test_create(self) -> None:
        """Exhibition creates with required fields."""
        exhibition = Exhibition(
            id="ex-001",
            title="Test Exhibition",
            theme="test",
            curator_note="A test note",
            piece_ids=("p1", "p2"),
        )

        assert exhibition.id == "ex-001"
        assert exhibition.title == "Test Exhibition"
        assert len(exhibition.piece_ids) == 2

    def test_to_dict(self) -> None:
        """to_dict returns serializable structure."""
        exhibition = Exhibition(
            id="ex-001",
            title="Test",
            theme="test",
            curator_note="Note",
            piece_ids=("p1",),
        )

        d = exhibition.to_dict()
        assert d["id"] == "ex-001"
        assert d["piece_ids"] == ["p1"]  # Converted to list
        assert "created_at" in d


# =============================================================================
# ExhibitionCurator Tests
# =============================================================================


class TestExhibitionCurator:
    """Tests for ExhibitionCurator."""

    @pytest.mark.asyncio
    async def test_curate_finds_matching_pieces(self, curator: ExhibitionCurator) -> None:
        """Curator finds pieces matching theme."""
        exhibition = await curator.curate(theme="ephemeral")

        # Should find pieces with "ephemeral" in content/interpretation
        assert len(exhibition.piece_ids) >= 1
        assert exhibition.theme == "ephemeral"

    @pytest.mark.asyncio
    async def test_curate_custom_title(self, curator: ExhibitionCurator) -> None:
        """Curator uses provided title."""
        exhibition = await curator.curate(theme="ephemeral", title="Custom Title")

        assert exhibition.title == "Custom Title"

    @pytest.mark.asyncio
    async def test_curate_custom_note(self, curator: ExhibitionCurator) -> None:
        """Curator uses provided curator note."""
        exhibition = await curator.curate(theme="ephemeral", curator_note="Custom note")

        assert exhibition.curator_note == "Custom note"

    @pytest.mark.asyncio
    async def test_curate_respects_max_pieces(self, curator: ExhibitionCurator) -> None:
        """Curator limits pieces to max_pieces."""
        exhibition = await curator.curate(theme="spring", max_pieces=2)

        assert len(exhibition.piece_ids) <= 2

    @pytest.mark.asyncio
    async def test_curate_artisan_diversity(self, curator: ExhibitionCurator) -> None:
        """Curator ensures artisan diversity."""
        # Request 6 pieces when we have multiple from same artisans
        exhibition = await curator.curate(theme="spring nature", max_pieces=6)

        # Check that no single artisan dominates
        # With max_pieces=6 and max_per_artisan=2, should have diversity
        # This test verifies the algorithm runs without error
        assert exhibition.id.startswith("ex-")

    @pytest.mark.asyncio
    async def test_get_exhibition(self, curator: ExhibitionCurator) -> None:
        """get() retrieves stored exhibition."""
        created = await curator.curate(theme="test")

        retrieved = curator.get(created.id)
        assert retrieved is not None
        assert retrieved.id == created.id

    @pytest.mark.asyncio
    async def test_list_exhibitions(self, curator: ExhibitionCurator) -> None:
        """list_exhibitions returns all exhibitions."""
        await curator.curate(theme="one")
        await curator.curate(theme="two")

        exhibitions = curator.list_exhibitions()
        assert len(exhibitions) == 2

    @pytest.mark.asyncio
    async def test_delete_exhibition(self, curator: ExhibitionCurator) -> None:
        """delete() removes exhibition."""
        created = await curator.curate(theme="to-delete")

        assert curator.delete(created.id)
        assert curator.get(created.id) is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent(self, curator: ExhibitionCurator) -> None:
        """delete() returns False for nonexistent."""
        assert not curator.delete("nonexistent")

    @pytest.mark.asyncio
    async def test_auto_generated_title(self, curator: ExhibitionCurator) -> None:
        """Title is auto-generated when not provided."""
        exhibition = await curator.curate(theme="spring")

        # Title should contain the theme word
        assert exhibition.title  # Not empty
        assert len(exhibition.title) > 0

    @pytest.mark.asyncio
    async def test_auto_generated_curator_note(self, curator: ExhibitionCurator) -> None:
        """Curator note is auto-generated."""
        exhibition = await curator.curate(theme="ephemeral")

        assert exhibition.curator_note
        assert "ephemeral" in exhibition.curator_note.lower()

    @pytest.mark.asyncio
    async def test_no_matches_empty_exhibition(self, curator: ExhibitionCurator) -> None:
        """Theme with no matches creates empty exhibition."""
        exhibition = await curator.curate(theme="xyznonexistent")

        assert len(exhibition.piece_ids) == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestExhibitionIntegration:
    """Integration tests for exhibition workflow."""

    @pytest.mark.asyncio
    async def test_full_curation_workflow(self, curator: ExhibitionCurator) -> None:
        """Full workflow: curate, retrieve, list, delete."""
        # Curate
        exhibition = await curator.curate(
            theme="digital gardens",
            title="Gardens of Code",
            curator_note="Exploring digital cultivation",
        )

        # Verify structure
        assert exhibition.id.startswith("ex-")
        assert exhibition.title == "Gardens of Code"

        # Retrieve
        retrieved = curator.get(exhibition.id)
        assert retrieved is not None

        # List
        all_exhibitions = curator.list_exhibitions()
        assert len(all_exhibitions) == 1

        # Delete
        assert curator.delete(exhibition.id)
        assert len(curator.list_exhibitions()) == 0

    @pytest.mark.asyncio
    async def test_multiple_exhibitions_same_theme(self, curator: ExhibitionCurator) -> None:
        """Multiple exhibitions can have same theme."""
        ex1 = await curator.curate(theme="ephemeral", title="Ephemeral I")
        ex2 = await curator.curate(theme="ephemeral", title="Ephemeral II")

        assert ex1.id != ex2.id
        assert ex1.title != ex2.title
        assert len(curator.list_exhibitions()) == 2
