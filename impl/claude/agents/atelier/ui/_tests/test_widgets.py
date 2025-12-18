"""
Tests for Atelier reactive widgets.

Tests:
- PieceWidget: State management and multi-target projection
- GalleryWidget: Collection management and filtering
- AtelierWidget: Dashboard status updates
"""

import pytest

from agents.atelier.ui.widgets import (
    AtelierState,
    AtelierWidget,
    GalleryState,
    GalleryWidget,
    PieceState,
    PieceWidget,
)

# =============================================================================
# PieceWidget Tests
# =============================================================================


class TestPieceWidget:
    """Tests for the PieceWidget."""

    @pytest.fixture
    def sample_piece(self) -> PieceState:
        return PieceState(
            id="piece-001",
            artisan="Calligrapher",
            form="haiku",
            content="APIs in spring\nJSON flows like cherry blooms\nErrors fade away",
            interpretation="A meditation on the ephemeral beauty of well-crafted interfaces",
            created_at="2025-01-01T00:00:00Z",
            inspirations=("piece-000",),
        )

    def test_init(self, sample_piece: PieceState) -> None:
        """Widget initializes with state."""
        widget = PieceWidget(sample_piece)
        assert widget.state.value == sample_piece

    def test_to_cli(self, sample_piece: PieceState) -> None:
        """CLI projection renders ASCII art."""
        widget = PieceWidget(sample_piece)
        cli = widget.to_cli()

        assert "haiku" in cli
        assert "Calligrapher" in cli
        assert "APIs in spring" in cli
        assert "piece-00" in cli  # ID is truncated in CLI

    def test_to_json(self, sample_piece: PieceState) -> None:
        """JSON projection returns serializable dict."""
        widget = PieceWidget(sample_piece)
        json_out = widget.to_json()

        assert json_out["type"] == "piece"
        assert json_out["id"] == "piece-001"
        assert json_out["artisan"] == "Calligrapher"
        assert json_out["form"] == "haiku"
        assert "inspirations" in json_out
        assert json_out["inspirations"] == ["piece-000"]

    def test_to_marimo(self, sample_piece: PieceState) -> None:
        """Marimo projection returns HTML string."""
        widget = PieceWidget(sample_piece)
        html = widget.to_marimo()

        assert "<div" in html
        assert "Calligrapher" in html
        assert "APIs in spring" in html


# =============================================================================
# GalleryWidget Tests
# =============================================================================


class TestGalleryWidget:
    """Tests for the GalleryWidget."""

    @pytest.fixture
    def sample_pieces(self) -> tuple[PieceState, ...]:
        return (
            PieceState(
                id="p1",
                artisan="Calligrapher",
                form="haiku",
                content="First poem",
                interpretation="Interpretation 1",
                created_at="2025-01-01",
            ),
            PieceState(
                id="p2",
                artisan="Cartographer",
                form="map",
                content="A map of data",
                interpretation="Interpretation 2",
                created_at="2025-01-02",
            ),
            PieceState(
                id="p3",
                artisan="Calligrapher",
                form="prose",
                content="A story",
                interpretation="Interpretation 3",
                created_at="2025-01-03",
            ),
        )

    def test_init_empty(self) -> None:
        """Empty gallery initializes correctly."""
        widget = GalleryWidget()
        assert widget.state.value.pieces == ()
        assert widget.state.value.total == 0

    def test_init_with_state(self, sample_pieces: tuple[PieceState, ...]) -> None:
        """Gallery initializes with provided state."""
        state = GalleryState(pieces=sample_pieces, total=len(sample_pieces))
        widget = GalleryWidget(state)
        assert len(widget.state.value.pieces) == 3

    def test_add_piece(self) -> None:
        """add_piece appends to gallery."""
        widget = GalleryWidget()
        piece = PieceState(
            id="new",
            artisan="Test",
            form="test",
            content="Content",
            interpretation="Interp",
            created_at="now",
        )
        widget.add_piece(piece)

        assert len(widget.state.value.pieces) == 1
        assert widget.state.value.total == 1

    def test_filter_by_artisan(self, sample_pieces: tuple[PieceState, ...]) -> None:
        """Filtering by artisan works in projection."""
        state = GalleryState(pieces=sample_pieces, total=3)
        widget = GalleryWidget(state)
        widget.set_filter(artisan="Calligrapher")

        json_out = widget.to_json()
        assert json_out["displayed"] == 2  # Two Calligrapher pieces

    def test_filter_by_form(self, sample_pieces: tuple[PieceState, ...]) -> None:
        """Filtering by form works in projection."""
        state = GalleryState(pieces=sample_pieces, total=3)
        widget = GalleryWidget(state)
        widget.set_filter(form="haiku")

        json_out = widget.to_json()
        assert json_out["displayed"] == 1

    def test_empty_cli(self) -> None:
        """Empty gallery shows placeholder."""
        widget = GalleryWidget()
        cli = widget.to_cli()
        assert "awaits its first piece" in cli

    def test_cli_with_pieces(self, sample_pieces: tuple[PieceState, ...]) -> None:
        """CLI shows piece previews."""
        state = GalleryState(pieces=sample_pieces, total=3)
        widget = GalleryWidget(state)
        cli = widget.to_cli()

        assert "Gallery" in cli
        assert "3" in cli
        assert "Calligrapher" in cli

    def test_json_structure(self, sample_pieces: tuple[PieceState, ...]) -> None:
        """JSON has correct structure."""
        state = GalleryState(pieces=sample_pieces, total=3)
        widget = GalleryWidget(state)
        json_out = widget.to_json()

        assert json_out["type"] == "gallery"
        assert len(json_out["pieces"]) == 3
        assert json_out["total"] == 3


# =============================================================================
# AtelierWidget Tests
# =============================================================================


class TestAtelierWidget:
    """Tests for the AtelierWidget."""

    @pytest.fixture
    def sample_status(self) -> AtelierState:
        return AtelierState(
            total_commissions=42,
            total_pieces=36,
            pending_queue=3,
            artisans=("Calligrapher", "Cartographer", "Archivist"),
            status="idle",
        )

    def test_init_empty(self) -> None:
        """Empty workshop status."""
        widget = AtelierWidget()
        assert widget.state.value.status == "idle"
        assert widget.state.value.total_commissions == 0

    def test_init_with_state(self, sample_status: AtelierState) -> None:
        """Initialize with status."""
        widget = AtelierWidget(sample_status)
        assert widget.state.value.total_commissions == 42

    def test_update_status(self, sample_status: AtelierState) -> None:
        """update_status modifies state."""
        widget = AtelierWidget(sample_status)
        widget.update_status(total_commissions=50, status="busy")

        assert widget.state.value.total_commissions == 50
        assert widget.state.value.status == "busy"
        # Other fields preserved
        assert widget.state.value.total_pieces == 36

    def test_cli_output(self, sample_status: AtelierState) -> None:
        """CLI shows dashboard."""
        widget = AtelierWidget(sample_status)
        cli = widget.to_cli()

        assert "Tiny Atelier" in cli
        assert "42" in cli  # commissions
        assert "36" in cli  # pieces
        assert "Calligrapher" in cli

    def test_json_output(self, sample_status: AtelierState) -> None:
        """JSON has correct structure."""
        widget = AtelierWidget(sample_status)
        json_out = widget.to_json()

        assert json_out["type"] == "atelier_status"
        assert json_out["total_commissions"] == 42
        assert json_out["artisans"] == ["Calligrapher", "Cartographer", "Archivist"]

    def test_marimo_output(self, sample_status: AtelierState) -> None:
        """Marimo returns HTML."""
        widget = AtelierWidget(sample_status)
        html = widget.to_marimo()

        assert "<div" in html
        assert "Tiny Atelier" in html
        assert "42" in html


# =============================================================================
# Integration Tests
# =============================================================================


class TestWidgetIntegration:
    """Integration tests for widget composition."""

    def test_gallery_from_pieces(self) -> None:
        """Build gallery from individual pieces."""
        gallery = GalleryWidget()

        for i in range(5):
            piece = PieceState(
                id=f"piece-{i}",
                artisan="Calligrapher" if i % 2 == 0 else "Cartographer",
                form="haiku" if i % 3 == 0 else "map",
                content=f"Content {i}",
                interpretation=f"Interp {i}",
                created_at=f"2025-01-0{i + 1}",
            )
            gallery.add_piece(piece)

        assert gallery.state.value.total == 5

        # Filter and verify
        gallery.set_filter(artisan="Calligrapher")
        json_out = gallery.to_json()
        assert json_out["displayed"] == 3  # pieces 0, 2, 4

    def test_atelier_status_updates(self) -> None:
        """Atelier widget tracks status changes."""
        atelier = AtelierWidget(AtelierState(artisans=("Calligrapher", "Cartographer")))

        # Simulate commission flow
        atelier.update_status(total_commissions=1, status="busy")
        assert atelier.state.value.status == "busy"

        atelier.update_status(total_pieces=1, status="idle")
        assert atelier.state.value.total_pieces == 1
        assert atelier.state.value.total_commissions == 1  # Preserved

    def test_all_widgets_json_have_type(self) -> None:
        """All widget JSON outputs have type field."""
        piece = PieceWidget(
            PieceState(
                id="p",
                artisan="A",
                form="f",
                content="c",
                interpretation="i",
                created_at="t",
            )
        )
        gallery = GalleryWidget()
        atelier = AtelierWidget()

        assert "type" in piece.to_json()
        assert "type" in gallery.to_json()
        assert "type" in atelier.to_json()
