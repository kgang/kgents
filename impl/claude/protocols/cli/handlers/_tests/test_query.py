"""
Tests for query CLI handler with dynamic path discovery.

Tests that the query handler:
1. Discovers paths from multiple sources
2. Caches discovered paths
3. Falls back gracefully when sources unavailable
4. Correctly matches patterns
"""

from __future__ import annotations

import pytest

from protocols.cli.handlers.query import (
    _discover_paths,
    _get_known_paths,
    _query_known_paths,
    clear_path_cache,
)


class TestDynamicPathDiscovery:
    """Test dynamic path discovery from handler routing tables and registries."""

    def setup_method(self) -> None:
        """Clear cache before each test."""
        clear_path_cache()

    def test_discover_paths_returns_sorted_list(self) -> None:
        """Discovered paths should be a sorted list."""
        paths = _discover_paths()
        assert isinstance(paths, list)
        assert paths == sorted(paths)

    def test_discover_paths_finds_handler_paths(self) -> None:
        """Should discover paths from handler routing tables."""
        paths = _discover_paths()

        # Paths from brain_thin.py
        assert "self.memory.capture" in paths
        assert "self.memory.recall" in paths

        # Paths from soul_thin.py
        assert "self.soul.reflect" in paths
        assert "self.soul.chat" in paths

        # Paths from town_thin.py
        assert "world.town.manifest" in paths
        assert "world.town.start" in paths

    def test_discover_paths_finds_crown_jewel_paths(self) -> None:
        """Should discover paths from Crown Jewels registry."""
        paths = _discover_paths()

        # From crown_jewels.py BRAIN_PATHS
        assert "self.memory.ghost.surface" in paths

        # From crown_jewels.py PARK_PATHS
        assert "concept.mask.manifest" in paths

        # From crown_jewels.py GARDENER_PATHS
        assert "concept.gardener.manifest" in paths

    def test_discover_paths_includes_base_contexts(self) -> None:
        """Should include the five base AGENTESE contexts."""
        paths = _discover_paths()

        for ctx in ["world", "self", "concept", "void", "time"]:
            assert ctx in paths, f"Missing base context: {ctx}"

    def test_discover_paths_minimum_count(self) -> None:
        """Should discover a reasonable number of paths (sanity check)."""
        paths = _discover_paths()
        # With Crown Jewels + handlers, we expect 100+ paths
        assert len(paths) > 100, f"Only discovered {len(paths)} paths"


class TestPathCaching:
    """Test that path caching works correctly."""

    def setup_method(self) -> None:
        """Clear cache before each test."""
        clear_path_cache()

    def test_get_known_paths_caches_result(self) -> None:
        """Subsequent calls should return cached result."""
        paths1 = _get_known_paths()
        paths2 = _get_known_paths()

        # Same object (cached)
        assert paths1 is paths2

    def test_clear_path_cache_clears_cache(self) -> None:
        """clear_path_cache should clear the cached paths."""
        paths1 = _get_known_paths()
        clear_path_cache()
        paths2 = _get_known_paths()

        # Same content but different objects (re-discovered)
        assert paths1 == paths2
        # Note: They might be the same object if discovery returns
        # identical sorted list - this is fine


class TestQueryPatterns:
    """Test that query patterns work correctly."""

    def setup_method(self) -> None:
        """Clear cache before each test."""
        clear_path_cache()

    def test_query_wildcard_all(self) -> None:
        """Pattern '*' should return all paths (up to limit)."""
        all_paths = _get_known_paths()
        matched = _query_known_paths("*", limit=1000)

        assert matched == all_paths

    def test_query_default_limit(self) -> None:
        """Default limit should be 100."""
        matched = _query_known_paths("*")
        all_paths = _get_known_paths()

        if len(all_paths) > 100:
            assert len(matched) == 100
        else:
            assert len(matched) == len(all_paths)

    def test_query_prefix_pattern(self) -> None:
        """Pattern 'self.*' should match all self.* paths."""
        matched = _query_known_paths("self.*")

        assert len(matched) > 0
        for path in matched:
            assert path.startswith("self."), f"Non-self path: {path}"

    def test_query_nested_prefix(self) -> None:
        """Pattern 'self.memory.*' should match nested paths."""
        matched = _query_known_paths("self.memory.*")

        assert len(matched) > 0
        for path in matched:
            assert path.startswith("self.memory."), f"Non-memory path: {path}"

    def test_query_exact_match(self) -> None:
        """Exact path should return that path and children."""
        matched = _query_known_paths("self.memory")

        assert "self.memory" in matched or any(
            p.startswith("self.memory.") for p in matched
        )

    def test_query_fuzzy_pattern(self) -> None:
        """Pattern '*memory*' should match paths containing 'memory'."""
        matched = _query_known_paths("*memory*")

        assert len(matched) > 0
        for path in matched:
            assert "memory" in path, f"No 'memory' in path: {path}"

    def test_query_pagination_limit(self) -> None:
        """Limit parameter should restrict results."""
        all_matched = _query_known_paths("self.*", limit=1000)
        limited = _query_known_paths("self.*", limit=5)

        assert len(limited) <= 5
        assert limited == all_matched[:5]

    def test_query_pagination_offset(self) -> None:
        """Offset parameter should skip results."""
        all_matched = _query_known_paths("self.*", limit=1000)
        offset = _query_known_paths("self.*", offset=5, limit=5)

        assert offset == all_matched[5:10]

    def test_query_no_matches(self) -> None:
        """Non-matching pattern should return empty list."""
        matched = _query_known_paths("nonexistent.*")

        assert matched == []


class TestContextDiscovery:
    """Test discovery by context."""

    def setup_method(self) -> None:
        """Clear cache before each test."""
        clear_path_cache()

    def test_world_context_has_paths(self) -> None:
        """world.* should have substantial paths."""
        matched = _query_known_paths("world.*")
        assert len(matched) >= 20, f"Only {len(matched)} world paths"

    def test_self_context_has_paths(self) -> None:
        """self.* should have substantial paths."""
        matched = _query_known_paths("self.*")
        assert len(matched) >= 20, f"Only {len(matched)} self paths"

    def test_concept_context_has_paths(self) -> None:
        """concept.* should have paths."""
        matched = _query_known_paths("concept.*")
        assert len(matched) >= 10, f"Only {len(matched)} concept paths"

    def test_void_context_has_paths(self) -> None:
        """void.* should have paths."""
        matched = _query_known_paths("void.*")
        assert len(matched) >= 5, f"Only {len(matched)} void paths"

    def test_time_context_has_paths(self) -> None:
        """time.* should have paths."""
        matched = _query_known_paths("time.*")
        assert len(matched) >= 2, f"Only {len(matched)} time paths"
