"""
Tests for PolyInterface - the core polynomial functor interface.

These tests verify:
- State transitions on ALL operations
- Type system enforcement
- The WorldHouse example
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type

import pytest

from ..interface import (
    BasePolyInterface,
    HouseInput,
    HouseOutput,
    HouseState,
    InhabitHouse,
    ObservationTrackedState,
    ObserveHouse,
    PolyInterface,
    RenovateHouse,
    VersionedState,
    WorldHouse,
)


class TestPolyInterfaceProtocol:
    """Tests for the PolyInterface protocol."""

    def test_worldhouse_implements_protocol(self) -> None:
        """WorldHouse implements PolyInterface."""
        house = WorldHouse()
        assert isinstance(house, PolyInterface)

    def test_custom_interface_implements_protocol(self) -> None:
        """Custom interfaces can implement PolyInterface."""

        @dataclass
        class CounterState:
            count: int = 0

        class CounterInput:
            pass

        @dataclass
        class Increment(CounterInput):
            amount: int = 1

        @dataclass
        class CounterOutput:
            value: int

        @dataclass
        class Counter(BasePolyInterface[CounterState, CounterInput, CounterOutput]):
            state: CounterState = field(default_factory=CounterState)

            def scope(self, s: CounterState) -> Type[CounterInput]:
                return CounterInput

            def dynamics(
                self,
                s: CounterState,
                input: CounterInput,
            ) -> tuple[CounterState, CounterOutput]:
                if isinstance(input, Increment):
                    new_count = s.count + input.amount
                    return CounterState(new_count), CounterOutput(new_count)
                return s, CounterOutput(s.count)

        counter = Counter()
        assert isinstance(counter, PolyInterface)


class TestWorldHouse:
    """Tests for the WorldHouse example."""

    def test_initial_state(self) -> None:
        """WorldHouse starts with clean state."""
        house = WorldHouse()
        assert house.state.observation_count == 0
        assert house.state.last_observer_archetype is None
        assert house.state.reified_properties == frozenset()
        assert house.state.version == 0

    def test_observation_changes_state(self) -> None:
        """Observation MUST change state."""
        house = WorldHouse()

        # Observe
        new_state, output = house.dynamics(
            house.state,
            ObserveHouse(observer_archetype="architect", intent="view"),
        )

        # State MUST have changed
        assert new_state.observation_count == 1
        assert new_state.last_observer_archetype == "architect"
        assert new_state.version == 1

    def test_observation_reifies_properties(self) -> None:
        """Observation reifies properties based on archetype."""
        house = WorldHouse()

        # Architect observation
        new_state, _ = house.dynamics(
            house.state,
            ObserveHouse(observer_archetype="architect", intent="inspect"),
        )

        assert "structural_integrity" in new_state.reified_properties
        assert "load_bearing_walls" in new_state.reified_properties
        assert "foundation_type" in new_state.reified_properties

    def test_different_observers_reify_different_properties(self) -> None:
        """Different archetypes reify different properties."""
        house = WorldHouse()

        # Architect
        arch_state, _ = house.dynamics(
            house.state,
            ObserveHouse(observer_archetype="architect", intent="view"),
        )

        # Poet (starting from initial state)
        house2 = WorldHouse()
        poet_state, _ = house2.dynamics(
            house2.state,
            ObserveHouse(observer_archetype="poet", intent="view"),
        )

        # Economist (starting from initial state)
        house3 = WorldHouse()
        econ_state, _ = house3.dynamics(
            house3.state,
            ObserveHouse(observer_archetype="economist", intent="view"),
        )

        # Different properties
        assert "structural_integrity" in arch_state.reified_properties
        assert "atmosphere" in poet_state.reified_properties
        assert "market_value" in econ_state.reified_properties

    def test_multiple_observations_accumulate(self) -> None:
        """Multiple observations accumulate properties."""
        house = WorldHouse()

        # First observation (architect)
        state1, _ = house.dynamics(
            house.state,
            ObserveHouse(observer_archetype="architect", intent="view"),
        )

        # Second observation (poet)
        state2, _ = house.dynamics(
            state1,
            ObserveHouse(observer_archetype="poet", intent="view"),
        )

        # Both sets of properties present
        assert "structural_integrity" in state2.reified_properties
        assert "atmosphere" in state2.reified_properties
        assert state2.observation_count == 2

    def test_renovation_changes_state(self) -> None:
        """Renovation changes state."""
        house = WorldHouse()

        new_state, output = house.dynamics(
            house.state,
            RenovateHouse(changes={"color": "blue"}),
        )

        assert new_state.version == 1
        assert output.state_delta == {"color": "blue"}

    def test_inhabitation_changes_state(self) -> None:
        """Inhabitation changes state."""
        house = WorldHouse()

        new_state, output = house.dynamics(
            house.state,
            InhabitHouse(duration=30.0),
        )

        assert "inhabited" in new_state.reified_properties
        assert new_state.version == 1
        assert output.state_delta["inhabited_duration"] == 30.0

    def test_output_contains_view(self) -> None:
        """Observation output contains rendered view."""
        house = WorldHouse()

        _, output = house.dynamics(
            house.state,
            ObserveHouse(observer_archetype="architect", intent="view"),
        )

        assert "blueprint" in output.view
        assert output.view["observation_count"] == 1

    def test_step_convenience_method(self) -> None:
        """step() method updates internal state."""
        house = WorldHouse()

        # Before
        assert house.state.observation_count == 0

        # Step
        output = house.step(ObserveHouse(observer_archetype="poet", intent="view"))

        # After - state updated in place
        assert house.state.observation_count == 1
        assert "metaphor" in output.view


class TestBasePolyInterface:
    """Tests for BasePolyInterface base class."""

    def test_step_updates_state(self) -> None:
        """step() updates internal state."""

        @dataclass
        class SimpleState:
            value: int = 0

        @dataclass
        class SimpleInput:
            delta: int

        @dataclass
        class SimpleOutput:
            new_value: int

        @dataclass
        class SimpleInterface(BasePolyInterface[SimpleState, SimpleInput, SimpleOutput]):
            state: SimpleState = field(default_factory=SimpleState)

            def scope(self, s: SimpleState) -> Type[SimpleInput]:
                return SimpleInput

            def dynamics(
                self, s: SimpleState, input: SimpleInput
            ) -> tuple[SimpleState, SimpleOutput]:
                new_val = s.value + input.delta
                return SimpleState(new_val), SimpleOutput(new_val)

        iface = SimpleInterface()
        assert iface.state.value == 0

        output = iface.step(SimpleInput(delta=5))
        assert iface.state.value == 5
        assert output.new_value == 5

        output = iface.step(SimpleInput(delta=3))
        assert iface.state.value == 8

    def test_valid_input(self) -> None:
        """valid_input() checks input type."""
        house = WorldHouse()

        assert house.valid_input(ObserveHouse("x", "y"))
        assert house.valid_input(RenovateHouse({}))
        assert house.valid_input(InhabitHouse(1.0))


class TestStatePatterns:
    """Tests for common state patterns."""

    def test_observation_tracked_state(self) -> None:
        """ObservationTrackedState tracks observations."""
        state = ObservationTrackedState()
        assert state.observation_count == 0
        assert state.last_observer is None

    def test_versioned_state(self) -> None:
        """VersionedState tracks versions."""
        state = VersionedState()
        assert state.version == 0


class TestNoPassiveObservation:
    """Tests verifying no passive observation is possible."""

    def test_dynamics_signature_requires_state_output(self) -> None:
        """dynamics() always returns new state."""
        house = WorldHouse()

        # Call dynamics
        result = house.dynamics(
            house.state,
            ObserveHouse("test", "test"),
        )

        # Must return tuple with state
        assert isinstance(result, tuple)
        assert len(result) == 2
        new_state, _ = result
        assert isinstance(new_state, HouseState)

    def test_cannot_read_without_state_change(self) -> None:
        """Every operation changes state (at least version)."""
        house = WorldHouse()
        initial_version = house.state.version

        # Any observation
        new_state, _ = house.dynamics(
            house.state,
            ObserveHouse("test", "test"),
        )

        # Version must increase
        assert new_state.version > initial_version

    def test_scope_returns_type_not_list(self) -> None:
        """scope() returns a Type, not a list of strings."""
        house = WorldHouse()
        scope = house.scope(house.state)

        # Must be a type
        assert isinstance(scope, type)

        # Should be HouseInput or subclass
        assert issubclass(scope, HouseInput) or scope is HouseInput


class TestImmutability:
    """Tests for state immutability."""

    def test_dynamics_returns_new_state(self) -> None:
        """dynamics() returns new state, doesn't mutate."""
        house = WorldHouse()
        original_state = house.state

        new_state, _ = house.dynamics(
            house.state,
            ObserveHouse("test", "test"),
        )

        # Original state unchanged
        assert original_state.observation_count == 0

        # New state different
        assert new_state.observation_count == 1

    def test_frozen_properties(self) -> None:
        """Reified properties are frozenset (immutable)."""
        house = WorldHouse()

        new_state, _ = house.dynamics(
            house.state,
            ObserveHouse("architect", "view"),
        )

        assert isinstance(new_state.reified_properties, frozenset)
