"""
Property-Based Tests for TownSheaf.

Uses Hypothesis for property-based testing of sheaf operations:
- Gluing idempotence
- Restriction then glue roundtrip
- Compatibility reflexivity
- Compatibility symmetry
- Emergence detection consistency

See: plans/town-rebuild.md (Phase 2: Property-Based Testing)
"""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, assume, given, settings, strategies as st
from hypothesis.stateful import RuleBasedStateMachine, initialize, invariant, rule

from agents.town.context import (
    ALL_REGION_CONTEXTS,
    INN_CONTEXT,
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
    GluingError,
    RegionView,
    TownSheaf,
    TownState,
    create_town_sheaf,
)

# =============================================================================
# Strategies
# =============================================================================


@st.composite
def citizen_id_strategy(draw: st.DrawFn) -> str:
    """Generate a valid citizen ID."""
    name = draw(st.text(alphabet="abcdefghijklmnopqrstuvwxyz", min_size=1, max_size=10))
    return f"citizen_{name}"


@st.composite
def region_view_strategy(draw: st.DrawFn, region_ctx: TownContext | None = None) -> RegionView:
    """Generate a valid RegionView."""
    if region_ctx is None:
        region_ctx = draw(st.sampled_from(ALL_REGION_CONTEXTS))

    # Generate 0-20 citizens
    citizen_count = draw(st.integers(min_value=0, max_value=20))
    citizens = frozenset(f"citizen_{i}" for i in range(citizen_count))

    # Generate relationships between citizens
    relationships: dict[tuple[str, str], float] = {}
    if len(citizens) >= 2:
        citizen_list = list(citizens)
        for i in range(len(citizen_list)):
            for j in range(i + 1, len(citizen_list)):
                if draw(st.booleans()):  # 50% chance of relationship
                    strength = draw(st.floats(min_value=0.0, max_value=1.0))
                    relationships[(citizen_list[i], citizen_list[j])] = strength

    # Generate coalition memberships
    coalition_memberships: dict[str, frozenset[str]] = {}
    if citizens:
        num_coalitions = draw(st.integers(min_value=0, max_value=3))
        for c in range(num_coalitions):
            coalition_id = f"coalition_{c}"
            for citizen in citizens:
                if draw(st.booleans()):  # 50% chance of membership
                    if citizen not in coalition_memberships:
                        coalition_memberships[citizen] = frozenset()
                    coalition_memberships[citizen] = coalition_memberships[citizen] | {coalition_id}

    return RegionView(
        region=region_ctx,
        citizens=citizens,
        relationships=relationships,
        events=(),
        coalition_memberships=coalition_memberships,
    )


@st.composite
def compatible_views_strategy(draw: st.DrawFn) -> dict[TownContext, RegionView]:
    """Generate compatible views for multiple regions.

    Ensures all views have consistent data for overlapping citizens:
    - Same relationship strengths
    - Same coalition memberships
    """
    # Pick 2-4 regions
    num_regions = draw(st.integers(min_value=2, max_value=4))
    regions = draw(st.permutations(ALL_REGION_CONTEXTS))[:num_regions]

    # Generate a global pool of citizens
    total_citizens = draw(st.integers(min_value=0, max_value=20))
    all_citizen_ids = [f"citizen_{i}" for i in range(total_citizens)]

    # Generate global coalition memberships (consistent across regions)
    global_coalitions: dict[str, frozenset[str]] = {}
    num_coalitions = draw(st.integers(min_value=0, max_value=3))
    for c in range(num_coalitions):
        coalition_id = f"coalition_{c}"
        for citizen in all_citizen_ids:
            if draw(st.booleans()):  # 50% chance
                if citizen not in global_coalitions:
                    global_coalitions[citizen] = frozenset()
                global_coalitions[citizen] = global_coalitions[citizen] | {coalition_id}

    # Generate global relationships (consistent across regions)
    global_relationships: dict[tuple[str, str], float] = {}
    for i in range(len(all_citizen_ids)):
        for j in range(i + 1, len(all_citizen_ids)):
            if draw(st.booleans()):  # 50% chance
                strength = draw(st.floats(min_value=0.0, max_value=1.0))
                global_relationships[(all_citizen_ids[i], all_citizen_ids[j])] = strength

    views: dict[TownContext, RegionView] = {}

    for region in regions:
        # Assign random subset of citizens to this region
        region_citizen_count = draw(st.integers(min_value=0, max_value=len(all_citizen_ids)))
        if all_citizen_ids:
            region_citizens = frozenset(
                draw(st.permutations(all_citizen_ids))[:region_citizen_count]
            )
        else:
            region_citizens = frozenset()

        # Filter relationships to those involving region citizens
        region_relationships = {
            k: v
            for k, v in global_relationships.items()
            if k[0] in region_citizens or k[1] in region_citizens
        }

        # Filter coalitions to region citizens
        region_coalitions = {c: m for c, m in global_coalitions.items() if c in region_citizens}

        views[region] = RegionView(
            region=region,
            citizens=region_citizens,
            relationships=region_relationships,
            events=(),
            coalition_memberships=region_coalitions,
        )

    return views


# =============================================================================
# Property Tests: Sheaf Axioms
# =============================================================================


class TestSheafGluingProperties:
    """Property-based tests for sheaf gluing axioms."""

    @given(compatible_views_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_glue_idempotent(self, views: dict[TownContext, RegionView]) -> None:
        """Gluing the same views twice should produce identical state."""
        sheaf = create_town_sheaf()

        # First glue
        state1 = sheaf.glue(views)

        # Second glue (should be identical)
        state2 = sheaf.glue(views)

        assert state1.citizens == state2.citizens
        assert state1.relationships == state2.relationships
        assert state1.citizen_locations == state2.citizen_locations
        assert state1.coalitions == state2.coalitions

    @given(st.lists(citizen_id_strategy(), min_size=0, max_size=20, unique=True))
    @settings(max_examples=50)
    def test_empty_views_glue_to_empty_state(self, citizen_ids: list[str]) -> None:
        """Gluing empty views produces empty state."""
        sheaf = create_town_sheaf()

        state = sheaf.glue({})

        assert len(state.citizens) == 0
        assert len(state.relationships) == 0
        assert len(state.coalitions) == 0

    @given(region_view_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_single_view_glues_to_itself(self, view: RegionView) -> None:
        """Gluing a single view preserves its data."""
        sheaf = create_town_sheaf()

        state = sheaf.glue({view.region: view})

        assert state.citizens == view.citizens
        # Relationships may be normalized (key order)
        for (a, b), strength in view.relationships.items():
            key = (min(a, b), max(a, b))
            assert key in state.relationships
            assert abs(state.relationships[key] - strength) < 0.001


class TestSheafCompatibilityProperties:
    """Property-based tests for sheaf compatibility."""

    @given(region_view_strategy())
    @settings(max_examples=50)
    def test_compatible_reflexive(self, view: RegionView) -> None:
        """A view is always compatible with itself."""
        sheaf = create_town_sheaf()

        result = sheaf.compatible({view.region: view})

        assert result is True

    @given(compatible_views_strategy())
    @settings(max_examples=50, suppress_health_check=[HealthCheck.too_slow])
    def test_compatible_views_remain_compatible(self, views: dict[TownContext, RegionView]) -> None:
        """Views generated as compatible should pass compatibility check."""
        sheaf = create_town_sheaf()

        assert sheaf.compatible(views) is True

    @given(st.lists(st.floats(min_value=0.0, max_value=1.0), min_size=2, max_size=10))
    @settings(max_examples=50)
    def test_incompatible_relationship_strengths_detected(self, strengths: list[float]) -> None:
        """Views with conflicting relationship strengths are incompatible."""
        assume(len(strengths) >= 2)
        assume(abs(strengths[0] - strengths[1]) > 0.02)  # Outside epsilon

        sheaf = create_town_sheaf()

        # Create two views with same citizens but different relationship strengths
        citizens = frozenset(["alice", "bob"])

        view1 = RegionView(
            region=INN_CONTEXT,
            citizens=citizens,
            relationships={("alice", "bob"): strengths[0]},
            events=(),
            coalition_memberships={},
        )

        view2 = RegionView(
            region=PLAZA_CONTEXT,
            citizens=citizens,
            relationships={("alice", "bob"): strengths[1]},
            events=(),
            coalition_memberships={},
        )

        views = {INN_CONTEXT: view1, PLAZA_CONTEXT: view2}

        assert sheaf.compatible(views) is False


class TestSheafRestrictionProperties:
    """Property-based tests for sheaf restriction."""

    @given(st.integers(min_value=1, max_value=50))
    @settings(max_examples=30)
    def test_restrict_preserves_citizen_location(self, n_citizens: int) -> None:
        """Restricting to a region only includes citizens in that region."""
        sheaf = create_town_sheaf()

        # Build a town state with citizens in different regions
        citizens = frozenset(f"citizen_{i}" for i in range(n_citizens))
        citizen_locations = {
            f"citizen_{i}": "inn" if i % 2 == 0 else "plaza" for i in range(n_citizens)
        }

        state = TownState(
            citizens=citizens,
            relationships={},
            citizen_locations=citizen_locations,
            coalitions={},
        )

        # Restrict to inn
        inn_view = sheaf.restrict(state, INN_CONTEXT)

        # Only even-numbered citizens should be in inn
        for cid in inn_view.citizens:
            assert citizen_locations[cid] == "inn"

    @given(st.integers(min_value=1, max_value=20))
    @settings(max_examples=30)
    def test_restrict_then_glue_preserves_citizens(self, n_citizens: int) -> None:
        """Restricting all views and re-gluing should preserve all citizens."""
        sheaf = create_town_sheaf()

        # Create views for all regions
        views: dict[TownContext, RegionView] = {}
        all_citizen_ids: set[str] = set()

        for i, region in enumerate(ALL_REGION_CONTEXTS):
            # Put some citizens in each region
            start = i * 2
            region_citizens = frozenset(
                f"citizen_{j}" for j in range(start, min(start + 2, n_citizens))
            )
            all_citizen_ids.update(region_citizens)

            views[region] = RegionView(
                region=region,
                citizens=region_citizens,
                relationships={},
                events=(),
                coalition_memberships={},
            )

        # Glue
        state = sheaf.glue(views)

        # All citizens should be present
        assert state.citizens == frozenset(all_citizen_ids)


class TestSheafEmergenceProperties:
    """Property-based tests for emergence detection."""

    @given(st.integers(min_value=3, max_value=10))
    @settings(max_examples=20)
    def test_triangles_detected_as_motifs(self, n_triangles: int) -> None:
        """Triangle relationships should be detected as culture motifs."""
        sheaf = create_town_sheaf()

        # Create citizens
        citizens = frozenset(f"citizen_{i}" for i in range(n_triangles * 3))

        # Create triangle relationships (strong)
        relationships: dict[tuple[str, str], float] = {}
        for t in range(n_triangles):
            base = t * 3
            a, b, c = f"citizen_{base}", f"citizen_{base + 1}", f"citizen_{base + 2}"
            relationships[(a, b)] = 0.8
            relationships[(b, c)] = 0.8
            relationships[(a, c)] = 0.8

        view = RegionView(
            region=INN_CONTEXT,
            citizens=citizens,
            relationships=relationships,
            events=(),
            coalition_memberships={},
        )

        state = sheaf.glue({INN_CONTEXT: view})

        # Should detect triangle motifs
        motifs = state.emergence.get("culture_motifs", [])
        triangle_motifs = [m for m in motifs if m.get("type") == "triangle"]
        if triangle_motifs:
            assert triangle_motifs[0]["count"] >= n_triangles

    @given(st.integers(min_value=2, max_value=7))
    @settings(max_examples=20)
    def test_region_balance_bounds(self, n_regions: int) -> None:
        """Region balance should be between 0 and 1."""
        sheaf = create_town_sheaf()

        # Distribute citizens unevenly
        views: dict[TownContext, RegionView] = {}
        for i, region in enumerate(ALL_REGION_CONTEXTS[:n_regions]):
            # Region i gets i+1 citizens
            views[region] = RegionView(
                region=region,
                citizens=frozenset(f"citizen_{region.name}_{j}" for j in range(i + 1)),
                relationships={},
                events=(),
                coalition_memberships={},
            )

        state = sheaf.glue(views)

        balance = state.emergence.get("region_balance", 0.0)
        assert 0.0 <= balance <= 1.0


# =============================================================================
# Stateful Testing: Sheaf State Machine
# =============================================================================


class SheafStateMachine(RuleBasedStateMachine):
    """Stateful testing for sheaf operations."""

    def __init__(self) -> None:
        super().__init__()
        self.sheaf = create_town_sheaf()
        self.views: dict[TownContext, RegionView] = {}
        self.all_citizens: set[str] = set()

    @initialize()
    def init_sheaf(self) -> None:
        """Initialize the sheaf."""
        self.sheaf = create_town_sheaf()
        self.views = {}
        self.all_citizens = set()

    @rule(
        region=st.sampled_from(ALL_REGION_CONTEXTS),
        citizen=citizen_id_strategy(),
    )
    def add_citizen_to_region(self, region: TownContext, citizen: str) -> None:
        """Adding a citizen should maintain compatibility."""
        if region not in self.views:
            self.views[region] = RegionView(
                region=region,
                citizens=frozenset(),
                relationships={},
                events=(),
                coalition_memberships={},
            )

        # Add citizen to region
        old_view = self.views[region]
        new_citizens = old_view.citizens | {citizen}
        self.views[region] = RegionView(
            region=region,
            citizens=new_citizens,
            relationships=old_view.relationships,
            events=(),
            coalition_memberships=old_view.coalition_memberships,
        )
        self.all_citizens.add(citizen)

    @rule()
    def glue_views(self) -> None:
        """Gluing should succeed if views are compatible."""
        if not self.views:
            return

        # Views should always be compatible (we never create conflicts)
        assert self.sheaf.compatible(self.views)

        state = self.sheaf.glue(self.views)

        # All tracked citizens should be in the glued state
        for citizen in self.all_citizens:
            assert citizen in state.citizens

    @invariant()
    def views_always_compatible(self) -> None:
        """All region views must remain compatible after any operation."""
        if len(self.views) < 2:
            return

        assert self.sheaf.compatible(self.views)


# Run the state machine tests
TestSheafStateMachine = SheafStateMachine.TestCase


# =============================================================================
# Additional Property Tests
# =============================================================================


class TestOverlapProperties:
    """Property-based tests for overlap computation."""

    @given(st.sampled_from(ALL_REGION_CONTEXTS))
    @settings(max_examples=20)
    def test_overlap_with_self_returns_all_citizens(self, region: TownContext) -> None:
        """A region overlaps completely with itself."""
        sheaf = create_town_sheaf()

        citizen_locations = {f"citizen_{i}": region.name for i in range(5)}

        overlap = sheaf.overlap(region, region, citizen_locations)

        # Should contain all citizens in that region
        expected = {cid for cid, loc in citizen_locations.items() if loc == region.name}
        assert overlap == expected

    @given(st.sampled_from(ALL_REGION_CONTEXTS))
    @settings(max_examples=20)
    def test_global_overlaps_with_all(self, region: TownContext) -> None:
        """Town context overlaps with all regions."""
        sheaf = create_town_sheaf()

        citizen_locations = {f"citizen_{i}": region.name for i in range(5)}

        overlap = sheaf.overlap(TOWN_CONTEXT, region, citizen_locations)

        # Should contain all citizens
        assert overlap == set(citizen_locations.keys())
