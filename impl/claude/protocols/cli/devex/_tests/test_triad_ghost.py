"""
Tests for TriadGhostCollector.

TriadGhostCollector projects Database Triad health to .kgents/ghost/ files
for developer visibility.
"""

from __future__ import annotations

import json
import tempfile
from collections.abc import Generator
from datetime import datetime, timezone
from pathlib import Path

import pytest
from protocols.cli.devex.triad_ghost import (
    TriadGhostCollector,
    TriadProjection,
    create_triad_collector,
    format_triad_status_cli,
)

# =============================================================================
# TriadProjection Tests
# =============================================================================


class TestTriadProjection:
    """Tests for TriadProjection dataclass."""

    def test_default_values(self) -> None:
        """Test default projection values."""
        proj = TriadProjection()

        assert proj.durability == 0.0
        assert proj.resonance == 0.0
        assert proj.reflex == 0.0
        assert proj.postgres_connected is False

    def test_overall_calculation(self) -> None:
        """Test overall health calculation."""
        proj = TriadProjection(
            durability=0.9,
            resonance=0.8,
            reflex=0.7,
        )

        assert proj.overall == pytest.approx(0.8, abs=0.01)

    def test_coherency_perfect(self) -> None:
        """Test coherency at 0ms lag."""
        proj = TriadProjection(cdc_lag_ms=0.0)
        assert proj.coherency_with_truth == 1.0

    def test_coherency_threshold(self) -> None:
        """Test coherency at threshold."""
        proj = TriadProjection(cdc_lag_ms=5000.0)
        assert proj.coherency_with_truth == 0.0

    def test_coherency_partial(self) -> None:
        """Test coherency at partial lag."""
        proj = TriadProjection(cdc_lag_ms=2500.0)
        assert proj.coherency_with_truth == pytest.approx(0.5, abs=0.01)

    def test_status_line_connected(self) -> None:
        """Test status line when all connected."""
        proj = TriadProjection(
            durability=0.9,
            resonance=0.8,
            reflex=0.7,
            postgres_connected=True,
            qdrant_connected=True,
            redis_connected=True,
            synapse_active=True,
        )

        status = proj.status_line

        assert "D:●" in status
        assert "R:●" in status
        assert "F:●" in status
        assert "cdc:" in status

    def test_status_line_disconnected(self) -> None:
        """Test status line when disconnected."""
        proj = TriadProjection(
            postgres_connected=False,
            qdrant_connected=False,
            redis_connected=False,
        )

        status = proj.status_line

        assert "D:○" in status
        assert "R:○" in status
        assert "F:○" in status

    def test_status_line_outbox_warning(self) -> None:
        """Test status line shows outbox warning."""
        proj = TriadProjection(outbox_pending=50)
        status = proj.status_line
        assert "outbox:50" in status

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        proj = TriadProjection(
            durability=0.9,
            resonance=0.8,
            reflex=0.7,
            postgres_connected=True,
        )

        d = proj.to_dict()

        assert d["durability"] == 0.9
        assert d["resonance"] == 0.8
        assert d["reflex"] == 0.7
        assert d["postgres_connected"] is True
        assert "overall" in d
        assert "status_line" in d


# =============================================================================
# TriadGhostCollector Tests
# =============================================================================


class TestTriadGhostCollector:
    """Tests for TriadGhostCollector."""

    @pytest.fixture
    def temp_ghost_dir(self) -> Generator[Path, None, None]:
        """Create a temporary ghost directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    def test_collector_creation(self, temp_ghost_dir: Path) -> None:
        """Test creating a collector."""
        collector = TriadGhostCollector(ghost_dir=temp_ghost_dir)

        assert collector.ghost_dir == temp_ghost_dir
        assert collector.postgres_url is None

    def test_configure(self, temp_ghost_dir: Path) -> None:
        """Test configuring connection URLs."""
        collector = TriadGhostCollector(ghost_dir=temp_ghost_dir)

        collector.configure(
            postgres_url="postgres://test",
            qdrant_url="http://qdrant:6333",
            redis_url="redis://redis:6379",
        )

        assert collector.postgres_url == "postgres://test"
        assert collector.qdrant_url == "http://qdrant:6333"
        assert collector.redis_url == "redis://redis:6379"

    @pytest.mark.asyncio
    async def test_project_creates_files(self, temp_ghost_dir: Path) -> None:
        """Test that project creates ghost files."""
        collector = TriadGhostCollector(ghost_dir=temp_ghost_dir)

        projection = TriadProjection(
            durability=0.9,
            resonance=0.8,
            reflex=0.7,
            postgres_connected=True,
            qdrant_connected=True,
            redis_connected=True,
            collected_at=datetime.now(timezone.utc).isoformat(),
        )

        await collector.project(projection)

        # Check files exist
        assert (temp_ghost_dir / "triad.status").exists()
        assert (temp_ghost_dir / "triad.json").exists()

    @pytest.mark.asyncio
    async def test_project_status_content(self, temp_ghost_dir: Path) -> None:
        """Test status file content."""
        collector = TriadGhostCollector(ghost_dir=temp_ghost_dir)

        projection = TriadProjection(
            postgres_connected=True,
            qdrant_connected=True,
            redis_connected=False,
        )

        await collector.project(projection)

        content = (temp_ghost_dir / "triad.status").read_text()
        assert "D:●" in content
        assert "R:●" in content
        assert "F:○" in content

    @pytest.mark.asyncio
    async def test_project_json_content(self, temp_ghost_dir: Path) -> None:
        """Test JSON file content."""
        collector = TriadGhostCollector(ghost_dir=temp_ghost_dir)

        projection = TriadProjection(
            durability=0.95,
            resonance=0.85,
            reflex=0.75,
            collected_at="2025-01-01T00:00:00Z",
        )

        await collector.project(projection)

        content = (temp_ghost_dir / "triad.json").read_text()
        data = json.loads(content)

        assert data["durability"] == 0.95
        assert data["resonance"] == 0.85
        assert data["reflex"] == 0.75

    def test_update_from_vitals(self, temp_ghost_dir: Path) -> None:
        """Test updating from AGENTESE vitals."""
        collector = TriadGhostCollector(ghost_dir=temp_ghost_dir)

        collector.update_from_vitals(
            durability=0.9,
            resonance=0.8,
            reflex=0.7,
        )

        assert collector._last_projection is not None
        assert collector._last_projection.durability == 0.9
        assert collector._last_projection.resonance == 0.8
        assert collector._last_projection.reflex == 0.7

    def test_update_from_vitals_partial(self, temp_ghost_dir: Path) -> None:
        """Test partial update from vitals."""
        collector = TriadGhostCollector(ghost_dir=temp_ghost_dir)

        collector.update_from_vitals(durability=0.9)
        collector.update_from_vitals(resonance=0.8)

        assert collector._last_projection is not None
        assert collector._last_projection.durability == 0.9
        assert collector._last_projection.resonance == 0.8


# =============================================================================
# CLI Formatting Tests
# =============================================================================


class TestCLIFormatting:
    """Tests for CLI output formatting."""

    def test_format_connected(self) -> None:
        """Test formatting when all connected."""
        proj = TriadProjection(
            durability=0.95,
            resonance=0.85,
            reflex=0.75,
            postgres_connected=True,
            qdrant_connected=True,
            redis_connected=True,
            synapse_active=True,
            cdc_lag_ms=100.0,
            outbox_pending=5,
            collected_at="2025-01-01T00:00:00Z",
        )

        output = format_triad_status_cli(proj)

        assert "Database Triad Status" in output
        assert "CONNECTED" in output
        assert "95%" in output
        assert "CDC Coherency" in output

    def test_format_disconnected(self) -> None:
        """Test formatting when disconnected."""
        proj = TriadProjection(
            postgres_connected=False,
            qdrant_connected=False,
            redis_connected=False,
            collected_at="2025-01-01T00:00:00Z",
        )

        output = format_triad_status_cli(proj)

        assert "DISCONNECTED" in output
        assert "CDC:                      INACTIVE" in output

    def test_format_cdc_inactive(self) -> None:
        """Test formatting when CDC inactive."""
        proj = TriadProjection(
            postgres_connected=True,
            synapse_active=False,
            collected_at="2025-01-01T00:00:00Z",
        )

        output = format_triad_status_cli(proj)

        assert "INACTIVE" in output


# =============================================================================
# Factory Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_triad_collector(self) -> None:
        """Test creating collector with factory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = create_triad_collector(
                project_root=Path(tmpdir),
                postgres_url="postgres://test",
            )

            assert collector.postgres_url == "postgres://test"
            assert collector.ghost_dir == Path(tmpdir) / ".kgents" / "ghost"


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests."""

    @pytest.mark.asyncio
    async def test_collect_and_project_without_services(self) -> None:
        """Test collect_and_project works without actual services."""
        with tempfile.TemporaryDirectory() as tmpdir:
            collector = TriadGhostCollector(ghost_dir=Path(tmpdir))

            # Should not raise even without service connections
            projection = await collector.collect_and_project()

            assert projection.postgres_connected is False
            assert projection.qdrant_connected is False
            assert projection.redis_connected is False

            # Files should still be created
            assert (Path(tmpdir) / "triad.status").exists()
            assert (Path(tmpdir) / "triad.json").exists()
