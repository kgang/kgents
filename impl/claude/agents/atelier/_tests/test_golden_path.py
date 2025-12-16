"""
Golden Path Smoke Test for Tiny Atelier.

Tests the complete happy path:
1. Seed gallery with samples
2. Commission an artisan
3. View the piece in gallery
4. Check lineage

This test validates Phase 1 usability requirements from
plans/atelier-remetabolize-extension.md.

Run with:
    uv run pytest impl/claude/agents/atelier/_tests/test_golden_path.py -v
"""

from __future__ import annotations

import pytest

from agents.atelier.artisan import AtelierEventType, Commission, Piece
from agents.atelier.artisans import ARTISAN_REGISTRY, get_artisan
from agents.atelier.gallery.lineage import LineageGraph
from agents.atelier.gallery.seeds import clear_seeds, create_sample_pieces, seed_gallery
from agents.atelier.gallery.store import Gallery


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def temp_gallery(tmp_path):
    """Create a temporary gallery for testing."""
    return Gallery(storage_path=tmp_path / "gallery")


# =============================================================================
# Golden Path Tests
# =============================================================================


class TestGoldenPath:
    """
    Golden path smoke tests for Atelier.

    Exit criteria: New user can run one command to see streaming piece +
    gallery entry + lineage tree.
    """

    async def test_01_seed_gallery(self, temp_gallery):
        """Step 1: Seed gallery with sample pieces."""
        # Seed should add 3 sample pieces
        added = await seed_gallery(temp_gallery)
        assert len(added) == 3, f"Expected 3 seeds, got {len(added)}"

        # Verify pieces are retrievable
        for piece_id in added:
            piece = await temp_gallery.get(piece_id)
            assert piece is not None, f"Seed piece {piece_id} not found"
            assert piece.provenance is not None
            assert piece.provenance.interpretation, "Seed should have interpretation"

    async def test_02_seed_idempotent(self, temp_gallery):
        """Seeding twice without force should be idempotent."""
        # First seed
        added1 = await seed_gallery(temp_gallery)
        assert len(added1) == 3

        # Second seed without force
        added2 = await seed_gallery(temp_gallery)
        assert len(added2) == 0, "Second seed should add nothing"

        # Count should still be 3
        count = await temp_gallery.count()
        assert count == 3

    async def test_03_seed_with_force(self, temp_gallery):
        """Seeding with force should overwrite."""
        # First seed
        await seed_gallery(temp_gallery)

        # Force seed
        added = await seed_gallery(temp_gallery, force=True)
        assert len(added) == 3, "Force seed should re-add all"

    async def test_04_clear_seeds(self, temp_gallery):
        """Clear seeds should remove sample pieces."""
        # Seed first
        await seed_gallery(temp_gallery)
        assert await temp_gallery.count() == 3

        # Clear
        removed = await clear_seeds(temp_gallery)
        assert len(removed) == 3
        assert await temp_gallery.count() == 0

    async def test_05_commission_artisan(self, temp_gallery):
        """Step 2: Commission an artisan and receive events."""
        from agents.atelier.workshop import get_workshop

        # Use the default workshop (it uses the global gallery)
        workshop = get_workshop()

        # Commission the calligrapher
        events = []
        piece: Piece | None = None

        async for event in workshop.flux.commission(
            artisan_name="calligrapher",
            request="a haiku about testing",
            patron="pytest",
        ):
            events.append(event)
            if event.event_type == AtelierEventType.PIECE_COMPLETE:
                piece = Piece.from_dict(event.data["piece"])

        # Verify event sequence
        event_types = [e.event_type for e in events]
        assert AtelierEventType.COMMISSION_RECEIVED in event_types
        assert AtelierEventType.CONTEMPLATING in event_types
        assert AtelierEventType.PIECE_COMPLETE in event_types

        # Verify piece
        assert piece is not None, "Should have created a piece"
        # Artisan name in piece uses display name (e.g., "The Calligrapher")
        assert "calligrapher" in piece.artisan.lower()
        assert piece.provenance is not None

    async def test_06_view_gallery(self, temp_gallery):
        """Step 3: View pieces in gallery."""
        # Seed gallery
        await seed_gallery(temp_gallery)

        # List pieces
        pieces = await temp_gallery.list_pieces()
        assert len(pieces) == 3

        # Verify each piece has required fields
        for piece in pieces:
            assert piece.id
            assert piece.artisan
            assert piece.content
            assert piece.provenance

    async def test_07_view_piece_with_provenance(self, temp_gallery):
        """View a specific piece with full provenance."""
        await seed_gallery(temp_gallery)

        # Get a specific piece
        piece = await temp_gallery.get("seed001")
        assert piece is not None

        # Verify provenance
        assert piece.provenance.interpretation
        assert len(piece.provenance.considerations) > 0
        assert len(piece.provenance.choices) > 0

        # Verify choice structure
        choice = piece.provenance.choices[0]
        assert choice.decision
        assert choice.reason

    async def test_08_lineage_graph(self, temp_gallery):
        """Step 4: Build and traverse lineage graph."""
        await seed_gallery(temp_gallery)

        # Build lineage graph
        pieces = await temp_gallery.list_pieces()
        graph = LineageGraph.from_pieces(pieces)

        # Each seed piece should be a root (no inspirations)
        for piece in pieces:
            ancestors = graph.get_ancestors(piece.id)
            assert len(ancestors) == 0, f"Seed {piece.id} should have no ancestors"

    async def test_09_search_content(self, temp_gallery):
        """Search should find pieces by content."""
        await seed_gallery(temp_gallery)

        # Search for content in the haiku seed
        results = await temp_gallery.search_content("persistence")
        assert len(results) > 0, "Should find the haiku about persistence"

        # Verify the found piece
        assert any(p.id == "seed001" for p in results)

    async def test_10_artisan_registry(self):
        """Verify artisan registry is populated."""
        # Should have at least 3 artisans
        assert len(ARTISAN_REGISTRY) >= 3

        # Core artisans should exist
        assert "calligrapher" in ARTISAN_REGISTRY
        assert "cartographer" in ARTISAN_REGISTRY
        assert "archivist" in ARTISAN_REGISTRY

        # Each artisan should be instantiable
        for name, cls in ARTISAN_REGISTRY.items():
            artisan = cls()
            assert artisan.name
            assert artisan.specialty


# =============================================================================
# SSE Resilience Tests
# =============================================================================


class TestSSEResilience:
    """Tests for SSE streaming resilience features."""

    def test_heartbeat_event_type_exists(self):
        """Verify HEARTBEAT event type is defined."""
        assert hasattr(AtelierEventType, "HEARTBEAT")
        assert AtelierEventType.HEARTBEAT.value == "heartbeat"

    async def test_commission_status_tracking(self, temp_gallery):
        """Verify commission status is tracked for fallback polling."""
        from protocols.api.atelier import (
            _get_commission_status,
            _update_commission_status,
        )

        # Simulate status updates
        _update_commission_status("test-123", "pending")
        status = _get_commission_status("test-123")
        assert status is not None
        assert status["status"] == "pending"

        # Update to complete
        _update_commission_status("test-123", "complete", piece={"id": "piece-1"})
        status = _get_commission_status("test-123")
        assert status is not None
        assert status["status"] == "complete"
        assert status["piece"]["id"] == "piece-1"


# =============================================================================
# Empty/Error State Tests
# =============================================================================


class TestEmptyErrorStates:
    """Tests for friendly empty and error states."""

    async def test_empty_gallery(self, temp_gallery):
        """Empty gallery should return empty list, not error."""
        pieces = await temp_gallery.list_pieces()
        assert pieces == []

        count = await temp_gallery.count()
        assert count == 0

    async def test_piece_not_found(self, temp_gallery):
        """Missing piece should return None, not error."""
        piece = await temp_gallery.get("nonexistent-id")
        assert piece is None

    async def test_empty_search(self, temp_gallery):
        """Search with no results should return empty list."""
        results = await temp_gallery.search_content("xyznonexistent123")
        assert results == []

    def test_unknown_artisan(self):
        """Unknown artisan should return None."""
        artisan = get_artisan("nonexistent-artisan")
        assert artisan is None


# =============================================================================
# Sample Pieces Validation
# =============================================================================


class TestSamplePieces:
    """Validate the sample pieces are well-formed."""

    def test_sample_pieces_structure(self):
        """All sample pieces should have required fields."""
        pieces = create_sample_pieces()
        assert len(pieces) == 3

        for piece in pieces:
            assert piece.id.startswith("seed")
            assert piece.artisan in ARTISAN_REGISTRY
            assert piece.content
            assert piece.form
            assert piece.provenance
            assert piece.provenance.interpretation
            assert len(piece.provenance.considerations) > 0
            assert len(piece.provenance.choices) > 0

    def test_sample_pieces_variety(self):
        """Sample pieces should showcase different artisans."""
        pieces = create_sample_pieces()
        artisans = {p.artisan for p in pieces}

        # Should have at least 3 different artisans
        assert len(artisans) >= 3

        # Should have variety in forms
        forms = {p.form for p in pieces}
        assert len(forms) >= 3
