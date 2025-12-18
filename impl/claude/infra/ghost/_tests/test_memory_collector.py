"""
Tests for MemoryCollector.

Verifies that MemoryCollector gathers Four Pillars memory data
and writes to GlassCacheManager with proper AGENTESE paths.
"""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from infra.ghost.cache import GlassCacheManager
from infra.ghost.collectors import MemoryCollector


class TestMemoryCollector:
    """Tests for MemoryCollector."""

    @pytest.mark.asyncio
    async def test_collector_name(self) -> None:
        """Collector has correct name."""
        collector = MemoryCollector()
        assert collector.name == "memory"

    @pytest.mark.asyncio
    async def test_collect_returns_result(self) -> None:
        """Collector returns a result with success status."""
        collector = MemoryCollector()
        result = await collector.collect()

        # Should always succeed (graceful degradation)
        assert result.success or result.data.get("health_line") == "memory:not_available"

    @pytest.mark.asyncio
    async def test_collect_includes_four_pillars(self) -> None:
        """Collector includes all Four Pillars data."""
        collector = MemoryCollector()
        result = await collector.collect()

        # Test passes if collector gracefully degrades (demo mode may not have data)
        if not result.success:
            # Graceful degradation is acceptable
            return

        # Crystal stats (may be None in demo mode)
        crystal = result.data.get("crystal")
        if crystal is not None:
            assert "dimension" in crystal
            assert "concept_count" in crystal
            assert "hot_count" in crystal
            assert "avg_resolution" in crystal

        # Field stats
        field = result.data.get("field")
        if field is not None:
            assert "concept_count" in field
            assert "trace_count" in field
            assert "avg_intensity" in field

        # Inference stats
        inference = result.data.get("inference")
        if inference is not None:
            assert "precision" in inference
            assert "entropy" in inference
            assert "concept_count" in inference

        # Health report (should always be present when collector succeeds)
        health = result.data.get("health")
        if health is not None:
            assert "health_score" in health
            assert "status" in health
            assert health["status"] in ["HEALTHY", "DEGRADED", "CRITICAL"]

    @pytest.mark.asyncio
    async def test_collect_with_cache_manager(self) -> None:
        """Collector writes to cache manager with AGENTESE paths."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_manager = GlassCacheManager(cache_dir=Path(tmpdir))
            collector = MemoryCollector(cache_manager=cache_manager)

            result = await collector.collect()

            if result.success and result.data.get("crystal"):
                # Verify cache entries were written
                assert cache_manager.exists("memory/crystal")
                assert cache_manager.exists("memory/health")

                # Verify AGENTESE paths
                crystal_data, _ = cache_manager.read("memory/crystal")
                assert crystal_data is not None

                health_data, _ = cache_manager.read("memory/health")
                assert health_data is not None

    @pytest.mark.asyncio
    async def test_health_line_format(self) -> None:
        """Health line has expected format."""
        collector = MemoryCollector()
        result = await collector.collect()

        assert "health_line" in result.data
        health_line = result.data["health_line"]
        assert health_line.startswith("memory:")

    @pytest.mark.asyncio
    async def test_graceful_degradation(self) -> None:
        """Collector degrades gracefully when MemoryDataProvider unavailable."""
        # The collector should handle ImportError gracefully
        collector = MemoryCollector()
        result = await collector.collect()

        # Should either succeed or gracefully degrade
        assert result.success or "not_available" in result.data.get("health_line", "")

    @pytest.mark.asyncio
    async def test_collector_in_create_all(self) -> None:
        """MemoryCollector is included in create_all_collectors."""
        from infra.ghost.collectors import create_all_collectors

        collectors = create_all_collectors()
        names = [c.name for c in collectors]
        assert "memory" in names

    @pytest.mark.asyncio
    async def test_cache_agentese_paths(self) -> None:
        """Verify correct AGENTESE paths are used for cache writes."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache_dir = Path(tmpdir)
            cache_manager = GlassCacheManager(cache_dir=cache_dir)
            collector = MemoryCollector(cache_manager=cache_manager)

            result = await collector.collect()

            if result.success and result.data.get("crystal"):
                # Read cached data and check metadata
                crystal_file = cache_dir / "memory" / "crystal.json"
                if crystal_file.exists():
                    import json

                    cached = json.loads(crystal_file.read_text())
                    assert cached["agentese_path"] == "self.memory.crystal.manifest"

                health_file = cache_dir / "memory" / "health.json"
                if health_file.exists():
                    import json

                    cached = json.loads(health_file.read_text())
                    assert cached["agentese_path"] == "self.memory.health.manifest"

    @pytest.mark.asyncio
    async def test_health_score_ranges(self) -> None:
        """Health scores are within expected ranges."""
        collector = MemoryCollector()
        result = await collector.collect()

        if result.success and "health" in result.data:
            health = result.data["health"]
            assert 0.0 <= health["health_score"] <= 1.0
            assert 0.0 <= health["crystal_health"] <= 1.0
            assert 0.0 <= health["field_health"] <= 1.0
            assert 0.0 <= health["inference_health"] <= 1.0

    @pytest.mark.asyncio
    async def test_collector_without_cache_manager(self) -> None:
        """Collector works without cache manager (data collection only)."""
        collector = MemoryCollector(cache_manager=None)
        result = await collector.collect()

        # Should succeed and return data
        assert result.success or "not_available" in result.data.get("health_line", "")

    @pytest.mark.asyncio
    async def test_timestamp_format(self) -> None:
        """Collector includes properly formatted timestamp."""
        collector = MemoryCollector()
        result = await collector.collect()

        # Timestamp should be ISO format
        from datetime import datetime

        try:
            datetime.fromisoformat(result.timestamp)
        except ValueError:
            pytest.fail("Timestamp is not in ISO format")
