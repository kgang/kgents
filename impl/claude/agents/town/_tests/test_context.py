"""Tests for Town Context module."""

from __future__ import annotations

import pytest

from agents.town.context import (
    ALL_REGION_CONTEXTS,
    GARDEN_CONTEXT,
    INN_CONTEXT,
    LIBRARY_CONTEXT,
    MARKET_CONTEXT,
    PLAZA_CONTEXT,
    REGION_ADJACENCY,
    RUMOR_DISTANCE,
    TEMPLE_CONTEXT,
    TOWN_CONTEXT,
    WORKSHOP_CONTEXT,
    ContextLevel,
    RegionType,
    TownContext,
    create_citizen_context,
    create_region_context,
)


class TestContextLevel:
    """Tests for ContextLevel enum."""

    def test_all_levels_exist(self) -> None:
        """Verify all context levels are defined."""
        assert ContextLevel.TOWN
        assert ContextLevel.REGION
        assert ContextLevel.CITIZEN

    def test_levels_are_unique(self) -> None:
        """Each level should have a unique value."""
        levels = [ContextLevel.TOWN, ContextLevel.REGION, ContextLevel.CITIZEN]
        values = [l.value for l in levels]
        assert len(values) == len(set(values))


class TestRegionType:
    """Tests for RegionType enum."""

    def test_all_region_types_exist(self) -> None:
        """Verify all expected region types are defined."""
        expected = ["inn", "workshop", "plaza", "market", "library", "temple", "garden"]
        actual = [r.value for r in RegionType]
        assert set(expected) == set(actual)

    def test_region_adjacency_is_symmetric(self) -> None:
        """If A is adjacent to B, B should be adjacent to A."""
        for region, neighbors in REGION_ADJACENCY.items():
            for neighbor in neighbors:
                assert region in REGION_ADJACENCY[neighbor], (
                    f"{region.value} -> {neighbor.value} but not reverse"
                )

    def test_rumor_distance_coverage(self) -> None:
        """Each region should have rumor distance defined."""
        for region in RegionType:
            assert region in RUMOR_DISTANCE, f"{region.value} missing from RUMOR_DISTANCE"


class TestTownContext:
    """Tests for TownContext dataclass."""

    def test_town_context_is_global(self) -> None:
        """Town context should be marked as global."""
        assert TOWN_CONTEXT.is_global
        assert not TOWN_CONTEXT.is_region
        assert not TOWN_CONTEXT.is_citizen

    def test_region_contexts_are_regions(self) -> None:
        """Region contexts should be marked as regions."""
        assert INN_CONTEXT.is_region
        assert not INN_CONTEXT.is_global
        assert not INN_CONTEXT.is_citizen

    def test_citizen_context_is_citizen(self) -> None:
        """Citizen contexts should be marked as citizens."""
        ctx = create_citizen_context("alice", "inn")
        assert ctx.is_citizen
        assert not ctx.is_global
        assert not ctx.is_region

    def test_context_hashable(self) -> None:
        """Contexts should be hashable for use as dict keys."""
        contexts = {TOWN_CONTEXT: "town", INN_CONTEXT: "inn"}
        assert contexts[TOWN_CONTEXT] == "town"
        assert contexts[INN_CONTEXT] == "inn"

    def test_context_equality(self) -> None:
        """Equal contexts should compare equal."""
        ctx1 = create_region_context(RegionType.INN)
        ctx2 = create_region_context(RegionType.INN)
        assert ctx1 == ctx2

    def test_context_inequality(self) -> None:
        """Different contexts should not be equal."""
        assert INN_CONTEXT != WORKSHOP_CONTEXT

    def test_is_ancestor_of_self(self) -> None:
        """A context is an ancestor of itself."""
        assert TOWN_CONTEXT.is_ancestor_of(TOWN_CONTEXT)
        assert INN_CONTEXT.is_ancestor_of(INN_CONTEXT)

    def test_town_is_ancestor_of_region(self) -> None:
        """Town context is ancestor of all regions."""
        assert TOWN_CONTEXT.is_ancestor_of(INN_CONTEXT)
        assert TOWN_CONTEXT.is_ancestor_of(WORKSHOP_CONTEXT)

    def test_region_is_ancestor_of_citizen(self) -> None:
        """Region context is ancestor of its citizens."""
        citizen = create_citizen_context("alice", "inn")
        assert INN_CONTEXT.is_ancestor_of(citizen)

    def test_region_not_ancestor_of_other_region_citizen(self) -> None:
        """Region is not ancestor of citizens in other regions."""
        citizen = create_citizen_context("alice", "workshop")
        assert not INN_CONTEXT.is_ancestor_of(citizen)

    def test_is_sibling_of(self) -> None:
        """Regions with same parent are siblings."""
        assert INN_CONTEXT.is_sibling_of(WORKSHOP_CONTEXT)
        assert WORKSHOP_CONTEXT.is_sibling_of(INN_CONTEXT)

    def test_citizens_in_same_region_are_siblings(self) -> None:
        """Citizens in the same region are siblings."""
        alice = create_citizen_context("alice", "inn")
        bob = create_citizen_context("bob", "inn")
        assert alice.is_sibling_of(bob)

    def test_citizens_in_different_regions_not_siblings(self) -> None:
        """Citizens in different regions are not siblings."""
        alice = create_citizen_context("alice", "inn")
        bob = create_citizen_context("bob", "workshop")
        assert not alice.is_sibling_of(bob)


class TestBoundaries:
    """Tests for region boundaries."""

    def test_inn_shares_boundary_with_plaza(self) -> None:
        """Inn should share boundary with plaza."""
        assert INN_CONTEXT.shares_boundary(PLAZA_CONTEXT)

    def test_inn_shares_boundary_with_market(self) -> None:
        """Inn should share boundary with market."""
        assert INN_CONTEXT.shares_boundary(MARKET_CONTEXT)

    def test_inn_not_boundary_with_library(self) -> None:
        """Inn should not share boundary with library."""
        assert not INN_CONTEXT.shares_boundary(LIBRARY_CONTEXT)

    def test_town_context_no_boundaries(self) -> None:
        """Town context doesn't share boundaries (not a region)."""
        assert not TOWN_CONTEXT.shares_boundary(INN_CONTEXT)

    def test_boundary_is_symmetric(self) -> None:
        """Boundaries should be symmetric."""
        for ctx1 in ALL_REGION_CONTEXTS:
            for ctx2 in ALL_REGION_CONTEXTS:
                if ctx1.shares_boundary(ctx2):
                    assert ctx2.shares_boundary(ctx1), f"{ctx1.name} -> {ctx2.name} but not reverse"


class TestRumorDistance:
    """Tests for rumor distance."""

    def test_inn_in_rumor_distance_of_plaza(self) -> None:
        """Inn should be in rumor distance of plaza."""
        assert INN_CONTEXT.in_rumor_distance(PLAZA_CONTEXT)

    def test_inn_in_rumor_distance_of_workshop(self) -> None:
        """Inn gossip reaches workshop."""
        assert INN_CONTEXT.in_rumor_distance(WORKSHOP_CONTEXT)

    def test_library_not_in_rumor_distance_of_inn(self) -> None:
        """Library is quieter, gossip doesn't reach inn directly."""
        # Library -> Inn is not in RUMOR_DISTANCE
        assert not LIBRARY_CONTEXT.in_rumor_distance(INN_CONTEXT)

    def test_town_context_no_rumor_distance(self) -> None:
        """Town context doesn't participate in rumor distance."""
        assert not TOWN_CONTEXT.in_rumor_distance(INN_CONTEXT)


class TestFactoryFunctions:
    """Tests for context factory functions."""

    def test_create_region_context(self) -> None:
        """create_region_context should create valid region."""
        ctx = create_region_context(RegionType.INN)
        assert ctx.name == "inn"
        assert ctx.level == ContextLevel.REGION
        assert ctx.parent == "town"
        assert ctx.region_type == RegionType.INN

    def test_create_region_context_custom_parent(self) -> None:
        """create_region_context should accept custom parent."""
        ctx = create_region_context(RegionType.INN, parent="custom")
        assert ctx.parent == "custom"

    def test_create_citizen_context(self) -> None:
        """create_citizen_context should create valid citizen."""
        ctx = create_citizen_context("alice-123", "inn")
        assert ctx.name == "citizen_alice-123"
        assert ctx.level == ContextLevel.CITIZEN
        assert ctx.parent == "inn"
        assert ctx.region_type is None


class TestPrebuiltContexts:
    """Tests for pre-built context constants."""

    def test_all_region_contexts_count(self) -> None:
        """Should have 7 region contexts."""
        assert len(ALL_REGION_CONTEXTS) == 7

    def test_all_region_contexts_are_regions(self) -> None:
        """All pre-built region contexts should be regions."""
        for ctx in ALL_REGION_CONTEXTS:
            assert ctx.is_region, f"{ctx.name} should be a region"

    def test_all_region_contexts_have_town_parent(self) -> None:
        """All regions should have town as parent."""
        for ctx in ALL_REGION_CONTEXTS:
            assert ctx.parent == "town", f"{ctx.name} should have town parent"

    def test_all_region_contexts_have_region_type(self) -> None:
        """All regions should have region_type set."""
        for ctx in ALL_REGION_CONTEXTS:
            assert ctx.region_type is not None, f"{ctx.name} should have region_type"
