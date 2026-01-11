"""Tests for TownSheaf module."""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings, strategies as st

from agents.town.context import (
    ALL_REGION_CONTEXTS,
    INN_CONTEXT,
    MARKET_CONTEXT,
    PLAZA_CONTEXT,
    TOWN_CONTEXT,
    WORKSHOP_CONTEXT,
    ContextLevel,
    RegionType,
    TownContext,
    create_citizen_context,
    create_region_context,
)
from agents.town.sheaf import (
    TOWN_SHEAF,
    GluingError,
    RegionView,
    RestrictionError,
    TownSheaf,
    TownState,
    create_town_sheaf,
)

# =============================================================================
# RegionView Tests
# =============================================================================


class TestRegionView:
    """Tests for RegionView dataclass."""

    def test_empty_region_view(self) -> None:
        """Empty region view should be valid."""
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(),
        )
        assert view.citizen_count() == 0
        assert view.relationship_density() == 0.0

    def test_region_view_with_citizens(self) -> None:
        """Region view with citizens."""
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice", "bob", "carol"]),
        )
        assert view.citizen_count() == 3

    def test_region_view_hashable(self) -> None:
        """Region views should be hashable."""
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice"]),
        )
        views = {view}
        assert len(views) == 1

    def test_restrict_to_citizens(self) -> None:
        """restrict_to_citizens should filter appropriately."""
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice", "bob", "carol"]),
            relationships={("alice", "bob"): 0.8, ("bob", "carol"): 0.6},
            coalition_memberships={"alice": frozenset(["c1"]), "bob": frozenset(["c1", "c2"])},
        )

        restricted = view.restrict_to_citizens(frozenset(["alice", "bob"]))

        assert restricted.citizens == frozenset(["alice", "bob"])
        assert ("alice", "bob") in restricted.relationships
        assert ("bob", "carol") in restricted.relationships  # bob is in restricted set
        assert "alice" in restricted.coalition_memberships
        assert "bob" in restricted.coalition_memberships
        assert "carol" not in restricted.coalition_memberships

    def test_relationship_density_calculation(self) -> None:
        """Relationship density should be ratio of actual to possible."""
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["a", "b", "c"]),  # 3 citizens = 3 possible pairs
            relationships={("a", "b"): 0.5, ("b", "c"): 0.7},  # 2 actual
        )
        # Density = 2 / 3 = 0.666...
        assert abs(view.relationship_density() - 2 / 3) < 0.01

    def test_relationship_density_single_citizen(self) -> None:
        """Single citizen should have 0 density (no possible relationships)."""
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice"]),
        )
        assert view.relationship_density() == 0.0


# =============================================================================
# TownState Tests
# =============================================================================


class TestTownState:
    """Tests for TownState dataclass."""

    def test_empty_town_state(self) -> None:
        """Empty town state should be valid."""
        state = TownState(
            citizens=frozenset(),
            relationships={},
            citizen_locations={},
            coalitions={},
        )
        assert state.total_citizens == 0
        assert state.total_relationships == 0
        assert state.total_coalitions == 0

    def test_town_state_counts(self) -> None:
        """Town state should count correctly."""
        state = TownState(
            citizens=frozenset(["a", "b", "c"]),
            relationships={("a", "b"): 0.5},
            citizen_locations={"a": "inn", "b": "workshop", "c": "plaza"},
            coalitions={"c1": frozenset(["a", "b"])},
        )
        assert state.total_citizens == 3
        assert state.total_relationships == 1
        assert state.total_coalitions == 1


# =============================================================================
# TownSheaf Tests
# =============================================================================


class TestTownSheafInit:
    """Tests for TownSheaf initialization."""

    def test_default_init(self) -> None:
        """Default init should have town context."""
        sheaf = TownSheaf()
        assert TOWN_CONTEXT in sheaf.contexts

    def test_custom_contexts(self) -> None:
        """Custom contexts should be stored."""
        contexts = {TOWN_CONTEXT, INN_CONTEXT}
        sheaf = TownSheaf(contexts=contexts)
        assert len(sheaf.contexts) == 2

    def test_add_context(self) -> None:
        """add_context should add context to sheaf."""
        sheaf = TownSheaf()
        sheaf.add_context(INN_CONTEXT)
        assert INN_CONTEXT in sheaf.contexts

    def test_get_context(self) -> None:
        """get_context should retrieve by name."""
        sheaf = create_town_sheaf()
        assert sheaf.get_context("inn") == INN_CONTEXT
        assert sheaf.get_context("nonexistent") is None


class TestTownSheafOverlap:
    """Tests for TownSheaf.overlap method."""

    def test_same_region_full_overlap(self) -> None:
        """Same region should fully overlap."""
        sheaf = create_town_sheaf()
        locations = {"alice": "inn", "bob": "inn"}
        overlap = sheaf.overlap(INN_CONTEXT, INN_CONTEXT, locations)
        assert overlap == {"alice", "bob"}

    def test_town_context_overlaps_all(self) -> None:
        """Town context overlaps with all regions."""
        sheaf = create_town_sheaf()
        locations = {"alice": "inn", "bob": "workshop"}
        overlap = sheaf.overlap(TOWN_CONTEXT, INN_CONTEXT, locations)
        assert "alice" in overlap
        assert "bob" in overlap

    def test_adjacent_regions_can_overlap(self) -> None:
        """Adjacent regions can overlap (citizens travel between)."""
        sheaf = create_town_sheaf()
        # Inn and Plaza are adjacent
        overlap = sheaf.overlap(INN_CONTEXT, PLAZA_CONTEXT)
        # Returns empty without location data, but doesn't raise
        assert isinstance(overlap, set)

    def test_non_adjacent_regions_no_overlap(self) -> None:
        """Non-adjacent regions should not overlap."""
        sheaf = create_town_sheaf()
        # Inn and Library are not adjacent
        overlap = sheaf.overlap(INN_CONTEXT, create_region_context(RegionType.LIBRARY))
        assert len(overlap) == 0


class TestTownSheafRestrict:
    """Tests for TownSheaf.restrict method."""

    def test_restrict_to_region(self) -> None:
        """Restricting to region should return region view."""
        sheaf = create_town_sheaf()
        state = TownState(
            citizens=frozenset(["alice", "bob", "carol"]),
            relationships={("alice", "bob"): 0.8},
            citizen_locations={"alice": "inn", "bob": "inn", "carol": "workshop"},
            coalitions={"c1": frozenset(["alice", "bob"])},
        )

        view = sheaf.restrict(state, INN_CONTEXT)

        assert view.region == INN_CONTEXT
        assert view.citizens == frozenset(["alice", "bob"])
        assert ("alice", "bob") in view.relationships

    def test_restrict_to_global(self) -> None:
        """Restricting to global should return full view."""
        sheaf = create_town_sheaf()
        state = TownState(
            citizens=frozenset(["alice", "bob"]),
            relationships={("alice", "bob"): 0.5},
            citizen_locations={"alice": "inn", "bob": "workshop"},
            coalitions={},
        )

        view = sheaf.restrict(state, TOWN_CONTEXT)

        assert view.citizens == state.citizens
        assert view.relationships == state.relationships

    def test_restrict_to_citizen_raises(self) -> None:
        """Restricting to citizen context should raise."""
        sheaf = create_town_sheaf()
        state = TownState(
            citizens=frozenset(["alice"]),
            relationships={},
            citizen_locations={"alice": "inn"},
            coalitions={},
        )
        citizen_ctx = create_citizen_context("alice", "inn")

        with pytest.raises(RestrictionError):
            sheaf.restrict(state, citizen_ctx)

    def test_restrict_empty_region(self) -> None:
        """Restricting to empty region should return empty view."""
        sheaf = create_town_sheaf()
        state = TownState(
            citizens=frozenset(["alice"]),
            relationships={},
            citizen_locations={"alice": "inn"},
            coalitions={},
        )

        view = sheaf.restrict(state, WORKSHOP_CONTEXT)

        assert view.citizens == frozenset()
        assert len(view.relationships) == 0


class TestTownSheafCompatible:
    """Tests for TownSheaf.compatible method."""

    def test_empty_views_compatible(self) -> None:
        """Empty views are compatible."""
        sheaf = create_town_sheaf()
        assert sheaf.compatible({})

    def test_single_view_compatible(self) -> None:
        """Single view is always compatible."""
        sheaf = create_town_sheaf()
        view = RegionView(region=INN_CONTEXT, citizens=frozenset(["alice"]))
        assert sheaf.compatible({INN_CONTEXT: view})

    def test_non_overlapping_views_compatible(self) -> None:
        """Non-overlapping views are compatible."""
        sheaf = create_town_sheaf()
        view1 = RegionView(region=INN_CONTEXT, citizens=frozenset(["alice"]))
        view2 = RegionView(region=WORKSHOP_CONTEXT, citizens=frozenset(["bob"]))
        assert sheaf.compatible({INN_CONTEXT: view1, WORKSHOP_CONTEXT: view2})

    def test_consistent_overlapping_views_compatible(self) -> None:
        """Overlapping views with consistent data are compatible."""
        sheaf = create_town_sheaf()
        view1 = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice", "bob"]),
            relationships={("alice", "bob"): 0.8},
            coalition_memberships={"alice": frozenset(["c1"])},
        )
        view2 = RegionView(
            region=PLAZA_CONTEXT,
            citizens=frozenset(["alice", "carol"]),
            relationships={("alice", "carol"): 0.6},
            coalition_memberships={"alice": frozenset(["c1"])},
        )
        assert sheaf.compatible({INN_CONTEXT: view1, PLAZA_CONTEXT: view2})

    def test_inconsistent_relationships_incompatible(self) -> None:
        """Views with inconsistent relationship strengths are incompatible."""
        sheaf = create_town_sheaf()
        view1 = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice", "bob"]),
            relationships={("alice", "bob"): 0.8},
        )
        view2 = RegionView(
            region=PLAZA_CONTEXT,
            citizens=frozenset(["alice", "bob"]),  # Same citizens
            relationships={("alice", "bob"): 0.3},  # Different strength
        )
        assert not sheaf.compatible({INN_CONTEXT: view1, PLAZA_CONTEXT: view2})

    def test_inconsistent_coalitions_incompatible(self) -> None:
        """Views with inconsistent coalition memberships are incompatible."""
        sheaf = create_town_sheaf()
        view1 = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice"]),
            coalition_memberships={"alice": frozenset(["c1"])},
        )
        view2 = RegionView(
            region=PLAZA_CONTEXT,
            citizens=frozenset(["alice"]),
            coalition_memberships={"alice": frozenset(["c2"])},  # Different coalition
        )
        assert not sheaf.compatible({INN_CONTEXT: view1, PLAZA_CONTEXT: view2})


class TestTownSheafGlue:
    """Tests for TownSheaf.glue method."""

    def test_glue_empty_views(self) -> None:
        """Gluing empty views returns empty state."""
        sheaf = create_town_sheaf()
        state = sheaf.glue({})
        assert state.total_citizens == 0

    def test_glue_single_view(self) -> None:
        """Gluing single view returns that view's data."""
        sheaf = create_town_sheaf()
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice", "bob"]),
            relationships={("alice", "bob"): 0.8},
        )
        state = sheaf.glue({INN_CONTEXT: view})
        assert state.citizens == frozenset(["alice", "bob"])

    def test_glue_multiple_views(self) -> None:
        """Gluing multiple views merges citizens."""
        sheaf = create_town_sheaf()
        view1 = RegionView(region=INN_CONTEXT, citizens=frozenset(["alice"]))
        view2 = RegionView(region=WORKSHOP_CONTEXT, citizens=frozenset(["bob"]))
        state = sheaf.glue({INN_CONTEXT: view1, WORKSHOP_CONTEXT: view2})
        assert "alice" in state.citizens
        assert "bob" in state.citizens

    def test_glue_merges_relationships(self) -> None:
        """Gluing averages overlapping relationship strengths."""
        sheaf = TownSheaf(relationship_epsilon=0.5)  # High epsilon for this test
        view1 = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice", "bob"]),
            relationships={("alice", "bob"): 0.8},
        )
        view2 = RegionView(
            region=PLAZA_CONTEXT,
            citizens=frozenset(["alice", "bob"]),
            relationships={("alice", "bob"): 0.6},
        )
        state = sheaf.glue({INN_CONTEXT: view1, PLAZA_CONTEXT: view2})

        # Should average: (0.8 + 0.6) / 2 = 0.7
        # Key is normalized to (min, max)
        assert abs(state.relationships[("alice", "bob")] - 0.7) < 0.01

    def test_glue_detects_emergence(self) -> None:
        """Gluing should detect emergent patterns."""
        sheaf = create_town_sheaf()
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["a", "b", "c"]),
            relationships={("a", "b"): 0.9, ("b", "c"): 0.9, ("a", "c"): 0.9},
        )
        state = sheaf.glue({INN_CONTEXT: view})

        assert "culture_motifs" in state.emergence
        assert "trust_density" in state.emergence
        assert "region_balance" in state.emergence

    def test_glue_incompatible_raises(self) -> None:
        """Gluing incompatible views should raise GluingError."""
        sheaf = create_town_sheaf()
        view1 = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["alice"]),
            coalition_memberships={"alice": frozenset(["c1"])},
        )
        view2 = RegionView(
            region=PLAZA_CONTEXT,
            citizens=frozenset(["alice"]),
            coalition_memberships={"alice": frozenset(["c2"])},
        )

        with pytest.raises(GluingError):
            sheaf.glue({INN_CONTEXT: view1, PLAZA_CONTEXT: view2})


class TestEmergenceDetection:
    """Tests for emergence detection in TownSheaf."""

    def test_find_triangle_motifs(self) -> None:
        """Should detect triangle motifs in relationships."""
        sheaf = create_town_sheaf()
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["a", "b", "c", "d"]),
            relationships={
                ("a", "b"): 0.9,
                ("b", "c"): 0.9,
                ("a", "c"): 0.9,  # Triangle: a-b-c
                ("c", "d"): 0.9,  # d is not in triangle
            },
        )
        state = sheaf.glue({INN_CONTEXT: view})

        motifs = state.emergence.get("culture_motifs", [])
        triangle_motif = next((m for m in motifs if m["type"] == "triangle"), None)
        assert triangle_motif is not None
        assert triangle_motif["count"] >= 1

    def test_trust_density(self) -> None:
        """Should compute trust density correctly."""
        sheaf = create_town_sheaf()
        view = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["a", "b", "c"]),  # 3 possible pairs
            relationships={("a", "b"): 0.9, ("b", "c"): 0.9},  # 2 strong
        )
        state = sheaf.glue({INN_CONTEXT: view})

        # 2 strong out of 3 possible
        assert state.emergence["trust_density"] > 0.5

    def test_region_balance(self) -> None:
        """Should compute region balance."""
        sheaf = create_town_sheaf()
        view1 = RegionView(region=INN_CONTEXT, citizens=frozenset(["a", "b"]))
        view2 = RegionView(region=WORKSHOP_CONTEXT, citizens=frozenset(["c", "d"]))
        state = sheaf.glue({INN_CONTEXT: view1, WORKSHOP_CONTEXT: view2})

        # Perfect balance between 2 regions
        assert state.emergence["region_balance"] > 0.9


class TestFactoryFunctions:
    """Tests for sheaf factory functions."""

    def test_create_town_sheaf(self) -> None:
        """create_town_sheaf should create sheaf with all regions."""
        sheaf = create_town_sheaf()
        assert len(sheaf.contexts) >= len(ALL_REGION_CONTEXTS)
        for ctx in ALL_REGION_CONTEXTS:
            assert ctx in sheaf.contexts

    def test_global_town_sheaf(self) -> None:
        """TOWN_SHEAF should be pre-initialized."""
        assert TOWN_SHEAF is not None
        assert isinstance(TOWN_SHEAF, TownSheaf)


# =============================================================================
# Property-Based Tests (Hypothesis)
# =============================================================================


class TestSheafProperties:
    """Property-based tests using Hypothesis."""

    @given(
        citizens=st.lists(
            st.text(min_size=1, max_size=10, alphabet="abcdefghij"),
            min_size=0,
            max_size=10,
            unique=True,
        )
    )
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_glue_preserves_citizens(self, citizens: list[str]) -> None:
        """Gluing should preserve all citizens."""
        sheaf = create_town_sheaf()
        view = RegionView(region=INN_CONTEXT, citizens=frozenset(citizens))
        state = sheaf.glue({INN_CONTEXT: view})
        assert state.citizens == frozenset(citizens)

    @given(strength=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    @settings(max_examples=30)
    def test_compatible_same_strength(self, strength: float) -> None:
        """Views with identical strengths should be compatible."""
        sheaf = create_town_sheaf()
        view1 = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["a", "b"]),
            relationships={("a", "b"): strength},
        )
        view2 = RegionView(
            region=PLAZA_CONTEXT,
            citizens=frozenset(["a", "b"]),
            relationships={("a", "b"): strength},
        )
        assert sheaf.compatible({INN_CONTEXT: view1, PLAZA_CONTEXT: view2})

    @given(epsilon=st.floats(min_value=0.001, max_value=0.1, allow_nan=False))
    @settings(max_examples=20)
    def test_epsilon_threshold(self, epsilon: float) -> None:
        """Strengths within epsilon should be compatible."""
        sheaf = TownSheaf(relationship_epsilon=epsilon)
        view1 = RegionView(
            region=INN_CONTEXT,
            citizens=frozenset(["a", "b"]),
            relationships={("a", "b"): 0.5},
        )
        view2 = RegionView(
            region=PLAZA_CONTEXT,
            citizens=frozenset(["a", "b"]),
            relationships={("a", "b"): 0.5 + epsilon * 0.9},  # Within epsilon
        )
        assert sheaf.compatible({INN_CONTEXT: view1, PLAZA_CONTEXT: view2})


class TestSheafRepr:
    """Tests for TownSheaf representation."""

    def test_repr_shows_region_count(self) -> None:
        """Repr should show region count."""
        sheaf = create_town_sheaf()
        repr_str = repr(sheaf)
        assert "TownSheaf" in repr_str
        assert "regions=" in repr_str
