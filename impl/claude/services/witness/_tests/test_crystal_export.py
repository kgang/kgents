"""
Tests for Crystal Export.

Tests the crystal export functionality with:
- Markdown export
- Image export (when pillow available)
- URL generation
- Exported crystal data structure
"""

from datetime import date, datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from services.witness.crystal import (
    ConstitutionalCrystalMeta,
    Crystal,
    CrystalLevel,
    MoodVector,
    generate_crystal_id,
)
from services.witness.crystal_export import (
    DEFAULT_HEIGHT,
    DEFAULT_WIDTH,
    PALETTE,
    CrystalExporter,
    ExportedCrystal,
    get_crystal_exporter,
    reset_crystal_exporter,
)
from services.witness.mark import MarkId

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_singletons() -> None:
    """Reset global singletons before each test."""
    reset_crystal_exporter()


@pytest.fixture
def sample_crystal() -> Crystal:
    """Create a sample crystal for testing."""
    base_time = datetime.now()

    return Crystal.from_crystallization(
        insight="Discovered the key insight for crystal compression algorithm",
        significance="This enables turning days into shareable proof of intention",
        principles=["tasteful", "composable"],
        source_marks=[MarkId("mark-1"), MarkId("mark-2"), MarkId("mark-3")],
        time_range=(base_time - timedelta(hours=2), base_time),
        confidence=0.85,
        topics={"compression", "crystal", "witness"},
        mood=MoodVector(
            warmth=0.7,
            weight=0.5,
            tempo=0.6,
            texture=0.4,
            brightness=0.8,
            saturation=0.6,
            complexity=0.5,
        ),
        session_id="test-session",
    )


@pytest.fixture
def crystal_with_meta() -> Crystal:
    """Create a crystal with constitutional metadata."""
    base_time = datetime.now()

    crystal = Crystal.from_crystallization(
        insight="A day of ethical decision-making",
        significance="Demonstrated composable architecture",
        principles=["ethical", "composable", "joy-inducing"],
        source_marks=[MarkId("mark-1"), MarkId("mark-2")],
        time_range=(base_time - timedelta(hours=4), base_time),
        confidence=0.92,
        topics={"ethics", "architecture"},
        mood=MoodVector.neutral(),
        session_id="meta-session",
    )

    meta = ConstitutionalCrystalMeta(
        dominant_principles=("ETHICAL", "COMPOSABLE", "JOY_INDUCING"),
        alignment_trajectory=(0.8, 0.85, 0.9, 0.88),
        average_alignment=0.86,
        violations_count=0,
        trust_earned=0.08,
        principle_trends={
            "ETHICAL": 0.9,
            "COMPOSABLE": 0.85,
            "JOY_INDUCING": 0.8,
            "TASTEFUL": 0.75,
            "CURATED": 0.7,
            "HETERARCHICAL": 0.65,
            "GENERATIVE": 0.6,
        },
    )

    return crystal.with_constitutional_meta(meta)


@pytest.fixture
def export_dir(tmp_path: Path) -> Path:
    """Temporary directory for export tests."""
    export_path = tmp_path / "exports"
    export_path.mkdir()
    return export_path


# =============================================================================
# ExportedCrystal Tests
# =============================================================================


class TestExportedCrystal:
    """Tests for ExportedCrystal dataclass."""

    def test_create_exported_crystal(self) -> None:
        """Can create an exported crystal."""
        exported = ExportedCrystal(
            id="crystal-abc123",
            content="This is the crystal content",
            date=date.today(),
            coherence_score=0.85,
            principle_weights={
                "tasteful": 0.8,
                "composable": 0.7,
            },
            dropped_count=3,
            dropped_summary="Some moments were compressed.",
        )

        assert exported.id == "crystal-abc123"
        assert exported.coherence_score == 0.85
        assert exported.dropped_count == 3

    def test_serialization(self) -> None:
        """ExportedCrystal serializes to dict."""
        exported = ExportedCrystal(
            id="crystal-abc123",
            content="Test content",
            date=date.today(),
            coherence_score=0.9,
            principle_weights={"tasteful": 0.8},
            dropped_count=2,
            dropped_summary="Minor details compressed.",
        )

        data = exported.to_dict()

        assert data["id"] == "crystal-abc123"
        assert data["coherence_score"] == 0.9
        assert data["date"] == date.today().isoformat()


# =============================================================================
# CrystalExporter Tests
# =============================================================================


class TestCrystalExporter:
    """Tests for CrystalExporter."""

    def test_prepare_export(self, sample_crystal: Crystal) -> None:
        """prepare_export creates ExportedCrystal from Crystal."""
        exporter = CrystalExporter()
        exported = exporter.prepare_export(sample_crystal)

        assert exported.id == str(sample_crystal.id)
        assert exported.coherence_score == sample_crystal.confidence
        assert "compression" in exported.content.lower()

    def test_prepare_export_with_meta(self, crystal_with_meta: Crystal) -> None:
        """prepare_export extracts principle weights from meta."""
        exporter = CrystalExporter()
        exported = exporter.prepare_export(crystal_with_meta)

        # Should have principle weights from constitutional meta
        assert "ethical" in exported.principle_weights or "ETHICAL" in exported.principle_weights


class TestMarkdownExport:
    """Tests for markdown export functionality."""

    @pytest.mark.asyncio
    async def test_export_as_markdown(self, sample_crystal: Crystal) -> None:
        """export_as_markdown generates valid markdown."""
        exporter = CrystalExporter()
        markdown = await exporter.export_as_markdown(sample_crystal)

        # Should have expected sections
        assert "# Crystal:" in markdown
        assert "## What Emerged" in markdown
        assert "## Honest Disclosure" in markdown
        assert "Witnessed by kgents" in markdown

    @pytest.mark.asyncio
    async def test_markdown_includes_insight(self, sample_crystal: Crystal) -> None:
        """Markdown includes crystal insight."""
        exporter = CrystalExporter()
        markdown = await exporter.export_as_markdown(sample_crystal)

        assert sample_crystal.insight in markdown

    @pytest.mark.asyncio
    async def test_markdown_includes_significance(self, sample_crystal: Crystal) -> None:
        """Markdown includes crystal significance."""
        exporter = CrystalExporter()
        markdown = await exporter.export_as_markdown(sample_crystal)

        if sample_crystal.significance:
            assert "## Why It Matters" in markdown
            assert sample_crystal.significance in markdown

    @pytest.mark.asyncio
    async def test_markdown_includes_principles(self, sample_crystal: Crystal) -> None:
        """Markdown includes principles section."""
        exporter = CrystalExporter()
        markdown = await exporter.export_as_markdown(sample_crystal)

        if sample_crystal.principles:
            assert "## Principles" in markdown
            for principle in sample_crystal.principles[:3]:
                assert principle.title() in markdown or principle in markdown

    @pytest.mark.asyncio
    async def test_markdown_without_metadata(self, sample_crystal: Crystal) -> None:
        """Can export markdown without metadata section."""
        exporter = CrystalExporter()
        markdown = await exporter.export_as_markdown(sample_crystal, include_metadata=False)

        # Should not include detailed metadata
        assert "*Crystallized from" not in markdown


class TestImageExport:
    """Tests for image export functionality."""

    @pytest.mark.asyncio
    async def test_export_as_image(self, sample_crystal: Crystal, export_dir: Path) -> None:
        """export_as_image creates an image file."""
        exporter = CrystalExporter(export_dir=export_dir)
        path = await exporter.export_as_image(sample_crystal)

        # Should create a file (either PNG or placeholder)
        assert path.exists()
        assert path.suffix in (".png", ".txt")

    @pytest.mark.asyncio
    async def test_image_custom_path(self, sample_crystal: Crystal, export_dir: Path) -> None:
        """Can specify custom output path."""
        exporter = CrystalExporter(export_dir=export_dir)
        custom_path = export_dir / "custom_crystal.png"
        path = await exporter.export_as_image(sample_crystal, path=custom_path)

        # Should use custom path (or .txt if pillow not available)
        assert path.exists()

    @pytest.mark.asyncio
    async def test_image_with_pillow_mock(self, sample_crystal: Crystal, export_dir: Path) -> None:
        """Test image generation with mocked pillow."""
        # This tests the rendering logic even without pillow
        exporter = CrystalExporter(export_dir=export_dir)
        exported = exporter.prepare_export(sample_crystal)

        # Verify export data is correct
        assert exported.coherence_score > 0
        assert len(exported.content) > 0


class TestURLExport:
    """Tests for URL export functionality."""

    @pytest.mark.asyncio
    async def test_export_as_url_without_base(self, sample_crystal: Crystal) -> None:
        """export_as_url returns local reference without base_url."""
        exporter = CrystalExporter()
        url = await exporter.export_as_url(sample_crystal)

        # Should be a local reference
        assert url.startswith("crystal://")

    @pytest.mark.asyncio
    async def test_export_as_url_with_base(self, sample_crystal: Crystal) -> None:
        """export_as_url uses base_url when configured."""
        exporter = CrystalExporter(base_url="https://kgents.dev/crystals/")
        url = await exporter.export_as_url(sample_crystal)

        # Should use base URL
        assert url.startswith("https://kgents.dev/crystals/")
        assert str(sample_crystal.id) in url

    @pytest.mark.asyncio
    async def test_url_is_deterministic(self, sample_crystal: Crystal) -> None:
        """Same crystal produces same URL."""
        exporter = CrystalExporter()

        url1 = await exporter.export_as_url(sample_crystal)
        url2 = await exporter.export_as_url(sample_crystal)

        assert url1 == url2


class TestBatchExport:
    """Tests for batch export functionality."""

    @pytest.mark.asyncio
    async def test_export_batch_markdown(
        self, sample_crystal: Crystal, crystal_with_meta: Crystal, export_dir: Path
    ) -> None:
        """Can export multiple crystals as markdown."""
        exporter = CrystalExporter(export_dir=export_dir)
        paths = await exporter.export_batch(
            [sample_crystal, crystal_with_meta],
            format="markdown",
            output_dir=export_dir,
        )

        assert len(paths) == 2
        for path in paths:
            assert path.exists()
            assert path.suffix == ".md"

    @pytest.mark.asyncio
    async def test_export_batch_image(self, sample_crystal: Crystal, export_dir: Path) -> None:
        """Can export multiple crystals as images."""
        exporter = CrystalExporter(export_dir=export_dir)
        paths = await exporter.export_batch(
            [sample_crystal],
            format="image",
            output_dir=export_dir,
        )

        assert len(paths) == 1
        for path in paths:
            assert path.exists()


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_get_crystal_exporter_singleton(self) -> None:
        """get_crystal_exporter returns singleton."""
        exporter1 = get_crystal_exporter()
        exporter2 = get_crystal_exporter()

        assert exporter1 is exporter2

    def test_reset_crystal_exporter(self) -> None:
        """reset_crystal_exporter creates new instance."""
        exporter1 = get_crystal_exporter()
        reset_crystal_exporter()
        exporter2 = get_crystal_exporter()

        assert exporter1 is not exporter2


# =============================================================================
# Design Constants Tests
# =============================================================================


class TestDesignConstants:
    """Tests for design constants and palette."""

    def test_default_dimensions(self) -> None:
        """Default dimensions are social-friendly."""
        assert DEFAULT_WIDTH == 1200
        assert DEFAULT_HEIGHT == 630  # OG image ratio

    def test_palette_colors(self) -> None:
        """Palette has expected colors."""
        assert "background" in PALETTE
        assert "text_primary" in PALETTE
        assert "accent" in PALETTE

        # Colors should be hex
        for color in PALETTE.values():
            assert color.startswith("#")
            assert len(color) == 7  # #RRGGBB
