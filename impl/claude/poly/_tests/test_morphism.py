"""
Tests for PolyMorphism - composable interface transformations.

These tests verify:
- Category laws (identity, associativity)
- Morphism composition
- Various morphism types
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Type

import pytest

from ..interface import (
    BasePolyInterface,
    HouseState,
    ObserveHouse,
    WorldHouse,
)
from ..morphism import (
    ComposedMorphism,
    FilterMorphism,
    IdentityMorphism,
    LiftMorphism,
    MapMorphism,
    PolyMorphism,
    filter_input,
    identity,
    map_output,
    verify_associativity,
    verify_identity_law_left,
    verify_identity_law_right,
)


class TestIdentityMorphism:
    """Tests for identity morphism."""

    def test_identity_on_states(self) -> None:
        """Identity maps state to itself."""
        id_morphism: IdentityMorphism[Any, Any] = IdentityMorphism()
        state = HouseState(observation_count=5)

        assert id_morphism.on_states(state) == state

    def test_identity_on_directions(self) -> None:
        """Identity maps direction to itself."""
        id_morphism: IdentityMorphism[Any, Any] = IdentityMorphism()
        state = HouseState()
        direction = ObserveHouse("test", "view")

        assert id_morphism.on_directions(state, direction) == direction

    def test_identity_apply(self) -> None:
        """Identity apply passes through."""
        id_morphism: IdentityMorphism[Any, Any] = IdentityMorphism()
        house = WorldHouse()
        input_val = ObserveHouse("test", "view")

        new_state, output = id_morphism.apply(house, input_val)

        assert new_state.observation_count == 1


class TestComposedMorphism:
    """Tests for composed morphisms."""

    def test_compose_two_identities(self) -> None:
        """Two identities compose to identity."""
        id1: IdentityMorphism[Any, Any] = IdentityMorphism()
        id2: IdentityMorphism[Any, Any] = IdentityMorphism()
        composed = id1 >> id2

        assert isinstance(composed, ComposedMorphism)

        state = HouseState()
        assert composed.on_states(state) == state

    def test_rshift_operator(self) -> None:
        """>> operator composes morphisms."""
        id1: IdentityMorphism[Any, Any] = IdentityMorphism()
        id2: IdentityMorphism[Any, Any] = IdentityMorphism()

        composed = id1 >> id2

        assert isinstance(composed, ComposedMorphism)
        assert composed.first is id1
        assert composed.second is id2


class TestMapMorphism:
    """Tests for MapMorphism."""

    def test_map_state(self) -> None:
        """MapMorphism maps states."""

        @dataclass
        class DoubledState:
            count: int

        def double_count(s: HouseState) -> DoubledState:
            return DoubledState(count=s.observation_count * 2)

        morphism: MapMorphism[Any, Any, Any, Any] = MapMorphism(
            state_map=double_count,
            direction_map=lambda s, d: d,
        )

        state = HouseState(observation_count=5)
        mapped = morphism.on_states(state)

        assert isinstance(mapped, DoubledState)
        assert mapped.count == 10

    def test_map_output(self) -> None:
        """MapMorphism can transform outputs."""
        morphism: MapMorphism[Any, Any, Any, Any] = MapMorphism(
            state_map=lambda s: s,
            direction_map=lambda s, d: d,
            output_map=lambda o: {"wrapped": o},
        )

        house = WorldHouse()
        _, output = morphism.apply(house, ObserveHouse("test", "view"))

        assert "wrapped" in output


class TestFilterMorphism:
    """Tests for FilterMorphism."""

    def test_filter_allows_valid_input(self) -> None:
        """Filter allows inputs passing predicate."""

        def allow_architects(s: Any, inp: Any) -> bool:
            if isinstance(inp, ObserveHouse):
                return inp.observer_archetype == "architect"
            return True

        morphism = FilterMorphism(predicate=allow_architects)

        house = WorldHouse()
        new_state, output = morphism.apply(
            house,
            ObserveHouse("architect", "view"),
        )

        assert new_state.observation_count == 1

    def test_filter_blocks_invalid_input(self) -> None:
        """Filter blocks inputs failing predicate."""

        def allow_architects(s: Any, inp: Any) -> bool:
            if isinstance(inp, ObserveHouse):
                return inp.observer_archetype == "architect"
            return True

        morphism = FilterMorphism(
            predicate=allow_architects,
            default_output={"blocked": True},
        )

        house = WorldHouse()
        new_state, output = morphism.apply(
            house,
            ObserveHouse("poet", "view"),
        )

        # State unchanged
        assert new_state.observation_count == 0
        assert output == {"blocked": True}


class TestLiftMorphism:
    """Tests for LiftMorphism."""

    def test_lift_transforms_output(self) -> None:
        """LiftMorphism transforms outputs."""
        morphism: LiftMorphism[Any, Any] = LiftMorphism(transform=lambda o: o.view)

        house = WorldHouse()
        _, output = morphism.apply(house, ObserveHouse("architect", "view"))

        # Output is now just the view dict
        assert isinstance(output, dict)
        assert "blueprint" in output


class TestCategoryLaws:
    """Tests for category laws."""

    def test_left_identity(self) -> None:
        """Id >> f = f (left identity)."""
        f: LiftMorphism[Any, Any] = LiftMorphism(transform=lambda o: o)
        house = WorldHouse()
        input_val = ObserveHouse("test", "view")

        # Id >> f
        composed = identity() >> f
        result1 = composed.apply(house, input_val)

        # f alone
        house2 = WorldHouse()  # Fresh house
        result2 = f.apply(house2, input_val)

        # Should be equivalent
        assert result1[0].observation_count == result2[0].observation_count

    def test_right_identity(self) -> None:
        """f >> Id = f (right identity)."""
        f: LiftMorphism[Any, Any] = LiftMorphism(transform=lambda o: o)
        house = WorldHouse()
        input_val = ObserveHouse("test", "view")

        # f >> Id
        composed = f >> identity()
        result1 = composed.apply(house, input_val)

        # f alone
        house2 = WorldHouse()
        result2 = f.apply(house2, input_val)

        assert result1[0].observation_count == result2[0].observation_count


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_identity_function(self) -> None:
        """identity() creates IdentityMorphism."""
        id_m = identity()
        assert isinstance(id_m, IdentityMorphism)

    def test_map_output_function(self) -> None:
        """map_output() creates LiftMorphism."""
        m = map_output(lambda x: x * 2)
        assert isinstance(m, LiftMorphism)

    def test_filter_input_function(self) -> None:
        """filter_input() creates FilterMorphism."""
        m = filter_input(lambda s, i: True)
        assert isinstance(m, FilterMorphism)


class TestMorphismChaining:
    """Tests for chaining multiple morphisms."""

    def test_chain_three_morphisms(self) -> None:
        """Can chain multiple morphisms."""
        m1 = identity()
        m2: LiftMorphism[Any, Any] = LiftMorphism(transform=lambda o: o)
        m3 = identity()

        chained = m1 >> m2 >> m3

        assert isinstance(chained, ComposedMorphism)

    def test_chain_filters(self) -> None:
        """Can chain filter morphisms."""
        # First filter: only architects
        f1: FilterMorphism[Any, Any] = FilterMorphism(
            predicate=lambda s, i: (
                isinstance(i, ObserveHouse) and i.observer_archetype == "architect"
            ),
            default_output=None,
        )

        # Second filter: only "view" intent
        f2: FilterMorphism[Any, Any] = FilterMorphism(
            predicate=lambda s, i: (isinstance(i, ObserveHouse) and i.intent == "view"),
            default_output=None,
        )

        # Both filters
        chained = f1 >> f2

        house = WorldHouse()

        # Architect viewing - passes both
        new_state, output = f1.apply(house, ObserveHouse("architect", "view"))
        assert output is not None

        # Poet - fails first filter
        house2 = WorldHouse()
        _, output2 = f1.apply(house2, ObserveHouse("poet", "view"))
        assert output2 is None


class TestMorphismStateHandling:
    """Tests for morphism state handling."""

    def test_morphism_preserves_state_type(self) -> None:
        """Morphisms can change state type."""

        @dataclass
        class EnrichedState:
            original: HouseState
            enriched_at: str = "test"

        def enrich(s: HouseState) -> EnrichedState:
            return EnrichedState(original=s, enriched_at="now")

        morphism: MapMorphism[Any, Any, Any, Any] = MapMorphism(
            state_map=enrich,
            direction_map=lambda s, d: d,
        )

        state = HouseState()
        enriched = morphism.on_states(state)

        assert isinstance(enriched, EnrichedState)
        assert enriched.original is state
