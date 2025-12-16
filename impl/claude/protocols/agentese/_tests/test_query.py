"""
AGENTESE Query System Tests (v3)

Tests for the query system:
- Query syntax validation
- Pattern matching
- Bounds enforcement
- Pagination
- Capability checking
- Edge cases
"""

from __future__ import annotations

import pytest
from protocols.agentese import (
    Logos,
    Observer,
    QueryBoundError,
    QueryBuilder,
    QueryMatch,
    QueryResult,
    QuerySyntaxError,
    create_logos,
    create_query_builder,
    query,
)
from protocols.agentese.logos import PlaceholderNode


@pytest.fixture
def logos() -> Logos:
    """Create a Logos instance with registered nodes."""
    logos = create_logos()

    # Register some test nodes
    logos.register("world.garden", PlaceholderNode("world.garden"))
    logos.register("world.house", PlaceholderNode("world.house"))
    logos.register("world.town", PlaceholderNode("world.town"))
    logos.register("self.memory", PlaceholderNode("self.memory"))
    logos.register("self.soul", PlaceholderNode("self.soul"))
    logos.register("concept.truth", PlaceholderNode("concept.truth"))
    logos.register("void.entropy", PlaceholderNode("void.entropy"))
    logos.register("time.trace", PlaceholderNode("time.trace"))

    return logos


class TestQuerySyntax:
    """Tests for query syntax validation."""

    def test_query_requires_prefix(self, logos: Logos) -> None:
        """Query pattern must start with '?'."""
        with pytest.raises(QuerySyntaxError) as exc_info:
            logos.query("world.*")

        assert "must start with '?'" in str(exc_info.value)

    def test_empty_pattern_raises(self, logos: Logos) -> None:
        """Empty pattern after '?' raises."""
        with pytest.raises(QuerySyntaxError) as exc_info:
            logos.query("?")

        assert "Empty query pattern" in str(exc_info.value)

    def test_too_deep_pattern_raises(self, logos: Logos) -> None:
        """Pattern with more than 3 parts raises."""
        with pytest.raises(QuerySyntaxError) as exc_info:
            logos.query("?world.house.room.door")

        assert "too deep" in str(exc_info.value)


class TestQueryBounds:
    """Tests for query bounds enforcement."""

    def test_default_limit(self, logos: Logos) -> None:
        """Default limit is 100."""
        result = logos.query("?world.*")
        assert result.limit == 100

    def test_custom_limit(self, logos: Logos) -> None:
        """Custom limit is respected."""
        result = logos.query("?world.*", limit=50)
        assert result.limit == 50

    def test_max_limit_enforced(self, logos: Logos) -> None:
        """Limit cannot exceed 1000."""
        with pytest.raises(QueryBoundError) as exc_info:
            logos.query("?world.*", limit=1001)

        assert "Max limit is 1000" in str(exc_info.value)

    def test_limit_1000_allowed(self, logos: Logos) -> None:
        """Limit of exactly 1000 is allowed."""
        result = logos.query("?world.*", limit=1000)
        assert result.limit == 1000

    def test_negative_offset_normalized(self, logos: Logos) -> None:
        """Negative offset is normalized to 0."""
        result = logos.query("?world.*", offset=-5)
        assert result.offset == 0


class TestQueryPatternMatching:
    """Tests for pattern matching."""

    def test_context_wildcard(self, logos: Logos) -> None:
        """?world.* matches all world nodes."""
        result = logos.query("?world.*")

        paths = result.paths
        assert "world.garden" in paths
        assert "world.house" in paths
        assert "world.town" in paths
        assert "self.memory" not in paths

    def test_single_context(self, logos: Logos) -> None:
        """?world matches all world nodes."""
        result = logos.query("?world")

        paths = result.paths
        assert any("world." in p for p in paths)

    def test_all_contexts_wildcard(self, logos: Logos) -> None:
        """?*.* matches all nodes."""
        result = logos.query("?*.*")

        paths = result.paths
        assert len(paths) >= 8  # We registered 8 nodes
        assert "world.garden" in paths
        assert "self.memory" in paths
        assert "concept.truth" in paths
        assert "void.entropy" in paths
        assert "time.trace" in paths

    def test_specific_holon(self, logos: Logos) -> None:
        """?world.garden matches only garden."""
        result = logos.query("?world.garden")

        paths = result.paths
        assert "world.garden" in paths
        assert len(paths) == 1


class TestQueryPagination:
    """Tests for query pagination."""

    def test_offset_skips_results(self, logos: Logos) -> None:
        """Offset skips the first N results."""
        # First, get all results
        all_results = logos.query("?world.*")
        total = all_results.total_count

        # Then query with offset
        result = logos.query("?world.*", offset=1)

        assert result.offset == 1
        assert len(result) == total - 1

    def test_limit_restricts_results(self, logos: Logos) -> None:
        """Limit restricts the number of results."""
        result = logos.query("?world.*", limit=2)

        assert len(result) == 2
        assert result.has_more  # We have 3 world nodes

    def test_has_more_flag(self, logos: Logos) -> None:
        """has_more indicates more results available."""
        # Query with limit smaller than total
        result = logos.query("?world.*", limit=1)
        assert result.has_more

        # Query with limit larger than total
        result = logos.query("?world.*", limit=100)
        assert not result.has_more

    def test_total_count_unaffected_by_pagination(self, logos: Logos) -> None:
        """total_count reflects all matches, not paginated."""
        all_results = logos.query("?world.*")
        paginated = logos.query("?world.*", limit=1, offset=0)

        assert paginated.total_count == all_results.total_count


class TestAffordanceQuery:
    """Tests for affordance queries (?self.memory.?)."""

    def test_affordance_query_returns_aspects(self, logos: Logos) -> None:
        """?self.memory.? returns available aspects."""
        result = logos.query("?self.memory.?")

        # PlaceholderNode provides: manifest, witness, affordances
        paths = result.paths
        assert any("manifest" in p for p in paths)


class TestQueryResult:
    """Tests for QueryResult behavior."""

    def test_result_is_iterable(self, logos: Logos) -> None:
        """QueryResult can be iterated."""
        result = logos.query("?world.*")

        matches = list(result)
        assert all(isinstance(m, QueryMatch) for m in matches)

    def test_result_bool_true_when_matches(self, logos: Logos) -> None:
        """QueryResult is truthy when matches exist."""
        result = logos.query("?world.*")
        assert result  # truthy

    def test_result_bool_false_when_empty(self, logos: Logos) -> None:
        """QueryResult is falsy when no matches."""
        result = logos.query("?nonexistent.*")
        assert not result  # falsy

    def test_result_len(self, logos: Logos) -> None:
        """len(QueryResult) returns match count."""
        result = logos.query("?world.*")
        assert len(result) == 3  # garden, house, town


class TestQueryBuilder:
    """Tests for the QueryBuilder fluent API."""

    def test_builder_basic_query(self, logos: Logos) -> None:
        """QueryBuilder executes basic query."""
        result = QueryBuilder(logos).pattern("?world.*").execute()

        assert len(result) > 0
        assert all("world." in m.path for m in result)

    def test_builder_with_limit(self, logos: Logos) -> None:
        """QueryBuilder respects limit."""
        result = QueryBuilder(logos).pattern("?world.*").limit(1).execute()

        assert len(result) == 1

    def test_builder_with_offset(self, logos: Logos) -> None:
        """QueryBuilder respects offset."""
        all_results = QueryBuilder(logos).pattern("?world.*").execute()

        offset_result = QueryBuilder(logos).pattern("?world.*").offset(1).execute()

        assert len(offset_result) == len(all_results) - 1

    def test_builder_dry_run(self, logos: Logos) -> None:
        """QueryBuilder dry_run returns cost estimate."""
        result = QueryBuilder(logos).pattern("?world.*").dry_run().execute()

        assert result.cost_estimate is not None
        assert result.cost_estimate > 0
        assert len(result) == 0  # dry run doesn't return matches

    def test_builder_requires_pattern(self, logos: Logos) -> None:
        """QueryBuilder raises without pattern."""
        with pytest.raises(QuerySyntaxError):
            QueryBuilder(logos).execute()

    def test_create_query_builder_factory(self, logos: Logos) -> None:
        """create_query_builder factory works."""
        builder = create_query_builder(logos)
        result = builder.pattern("?world.*").execute()

        assert len(result) > 0


class TestLogosQueryMethod:
    """Tests for Logos.query() method directly."""

    def test_logos_query_method(self, logos: Logos) -> None:
        """Logos.query() method works."""
        result = logos.query("?world.*")

        assert isinstance(result, QueryResult)
        assert len(result) > 0

    def test_logos_query_with_observer(self, logos: Logos) -> None:
        """Logos.query() accepts observer."""
        observer = Observer.from_archetype("developer")
        result = logos.query("?world.*", observer=observer)

        assert isinstance(result, QueryResult)

    def test_logos_query_with_all_kwargs(self, logos: Logos) -> None:
        """Logos.query() accepts all kwargs."""
        observer = Observer.from_archetype("developer")
        result = logos.query(
            "?world.*",
            limit=50,
            offset=0,
            observer=observer,
            capability_check=True,
            dry_run=False,
        )

        assert result.limit == 50
        assert result.offset == 0


class TestQueryEdgeCases:
    """Tests for edge cases."""

    def test_empty_registry_query(self) -> None:
        """Query on empty registry returns empty result."""
        logos = create_logos()
        result = logos.query("?world.*")

        assert len(result) == 0
        assert result.total_count == 0

    def test_query_nonexistent_context(self, logos: Logos) -> None:
        """Query for nonexistent context returns empty."""
        result = logos.query("?nonexistent.*")

        assert len(result) == 0

    def test_query_preserves_match_order(self, logos: Logos) -> None:
        """Query results are sorted consistently."""
        result1 = logos.query("?world.*")
        result2 = logos.query("?world.*")

        assert result1.paths == result2.paths

    def test_query_match_has_context(self, logos: Logos) -> None:
        """QueryMatch includes context."""
        result = logos.query("?world.garden")

        assert len(result) == 1
        match = result.matches[0]
        assert match.context == "world"

    def test_aspect_pattern_matching(self, logos: Logos) -> None:
        """?*.*.manifest matches manifest aspects."""
        result = logos.query("?*.*.manifest")

        # All matches should have manifest in the path
        for match in result:
            assert "manifest" in match.path


class TestQueryFunctional:
    """Functional tests using the query function directly."""

    def test_query_function_works(self, logos: Logos) -> None:
        """query() function works directly."""
        result = query(logos, "?world.*")

        assert isinstance(result, QueryResult)
        assert len(result) > 0

    def test_query_function_with_kwargs(self, logos: Logos) -> None:
        """query() function accepts all kwargs."""
        result = query(
            logos,
            "?world.*",
            limit=10,
            offset=0,
            capability_check=False,
        )

        assert result.limit == 10
