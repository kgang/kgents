"""
Tests for dynamics - the state transition function.

These tests verify:
- S × A → S × B structure
- State always changes (even for observations)
- Output reflects state changes
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Type

import pytest

from ..interface import (
    BasePolyInterface,
    HouseState,
    InhabitHouse,
    ObserveHouse,
    RenovateHouse,
    WorldHouse,
)


class TestDynamicsStructure:
    """Tests for the S × A → S × B structure."""

    def test_dynamics_takes_state_and_input(self) -> None:
        """dynamics() takes state and input as separate args."""
        house = WorldHouse()

        # Can call with explicit state
        result = house.dynamics(
            HouseState(observation_count=5),  # Custom state
            ObserveHouse("test", "test"),
        )

        assert result is not None

    def test_dynamics_returns_tuple(self) -> None:
        """dynamics() returns (new_state, output) tuple."""
        house = WorldHouse()
        result = house.dynamics(house.state, ObserveHouse("test", "test"))

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_dynamics_new_state_correct_type(self) -> None:
        """First element of result is new state."""
        house = WorldHouse()
        new_state, _ = house.dynamics(house.state, ObserveHouse("test", "test"))

        assert isinstance(new_state, HouseState)

    def test_dynamics_output_correct_type(self) -> None:
        """Second element of result is output."""
        house = WorldHouse()
        _, output = house.dynamics(house.state, ObserveHouse("test", "test"))

        from ..interface import HouseOutput

        assert isinstance(output, HouseOutput)


class TestStateTransitionGuarantees:
    """Tests verifying state always transitions."""

    def test_observe_changes_observation_count(self) -> None:
        """Observe always increments observation_count."""
        house = WorldHouse()

        state1, _ = house.dynamics(house.state, ObserveHouse("a", "x"))
        assert state1.observation_count == 1

        state2, _ = house.dynamics(state1, ObserveHouse("b", "y"))
        assert state2.observation_count == 2

    def test_observe_changes_version(self) -> None:
        """Every operation increments version."""
        house = WorldHouse()

        state1, _ = house.dynamics(house.state, ObserveHouse("a", "x"))
        assert state1.version == 1

        state2, _ = house.dynamics(state1, RenovateHouse({}))
        assert state2.version == 2

        state3, _ = house.dynamics(state2, InhabitHouse(1.0))
        assert state3.version == 3

    def test_observe_tracks_last_observer(self) -> None:
        """Observe tracks last_observer_archetype."""
        house = WorldHouse()

        state1, _ = house.dynamics(house.state, ObserveHouse("architect", "view"))
        assert state1.last_observer_archetype == "architect"

        state2, _ = house.dynamics(state1, ObserveHouse("poet", "view"))
        assert state2.last_observer_archetype == "poet"


class TestStatelessDynamics:
    """Tests for using dynamics without stateful interface."""

    def test_can_use_dynamics_functionally(self) -> None:
        """dynamics() is pure function of state and input."""
        house = WorldHouse()

        # Same state + input = same result
        state = HouseState(observation_count=0)
        input1 = ObserveHouse("architect", "view")

        result1 = house.dynamics(state, input1)
        result2 = house.dynamics(state, input1)

        # States are equal (not same object due to frozenset)
        assert result1[0].observation_count == result2[0].observation_count
        assert result1[0].version == result2[0].version

    def test_dynamics_from_arbitrary_state(self) -> None:
        """Can call dynamics with any valid state."""
        house = WorldHouse()

        # Start from non-initial state
        custom_state = HouseState(
            observation_count=100,
            last_observer_archetype="previous",
            reified_properties=frozenset(["existing_property"]),
            version=50,
        )

        new_state, _ = house.dynamics(
            custom_state,
            ObserveHouse("architect", "view"),
        )

        assert new_state.observation_count == 101
        assert "existing_property" in new_state.reified_properties
        assert new_state.version == 51


class TestDynamicsIdempotence:
    """Tests for non-idempotent dynamics (observation counts)."""

    def test_repeated_observation_increases_count(self) -> None:
        """Multiple observations increase count (not idempotent)."""
        house = WorldHouse()
        state = house.state

        for i in range(5):
            state, _ = house.dynamics(state, ObserveHouse("test", "view"))
            assert state.observation_count == i + 1

    def test_observation_always_changes_state(self) -> None:
        """Even identical observations change state."""
        house = WorldHouse()

        input1 = ObserveHouse("same", "same")

        state1, _ = house.dynamics(house.state, input1)
        state2, _ = house.dynamics(state1, input1)

        # States are different (count increased)
        assert state2.observation_count != state1.observation_count


class TestOutputDelta:
    """Tests for output state delta."""

    def test_observe_delta_contains_observed(self) -> None:
        """Observe output contains 'observed': True."""
        house = WorldHouse()
        _, output = house.dynamics(house.state, ObserveHouse("test", "view"))

        assert output.state_delta["observed"] is True

    def test_observe_delta_contains_reified(self) -> None:
        """Observe output contains list of reified properties."""
        house = WorldHouse()
        _, output = house.dynamics(
            house.state,
            ObserveHouse("architect", "view"),
        )

        assert "reified" in output.state_delta
        assert isinstance(output.state_delta["reified"], list)

    def test_renovate_delta_contains_changes(self) -> None:
        """Renovate output contains the changes."""
        house = WorldHouse()
        changes = {"color": "blue", "roof": "new"}

        _, output = house.dynamics(house.state, RenovateHouse(changes=changes))

        assert output.state_delta == changes

    def test_inhabit_delta_contains_duration(self) -> None:
        """Inhabit output contains duration."""
        house = WorldHouse()
        _, output = house.dynamics(house.state, InhabitHouse(duration=30.5))

        assert output.state_delta["inhabited_duration"] == 30.5


class TestCustomDynamics:
    """Tests for creating custom dynamics interfaces."""

    def test_custom_interface_dynamics(self) -> None:
        """Custom interfaces implement dynamics correctly."""

        @dataclass
        class StackState:
            items: tuple[int, ...] = ()

        class StackInput:
            pass

        @dataclass
        class Push(StackInput):
            value: int

        @dataclass
        class Pop(StackInput):
            pass

        @dataclass
        class StackOutput:
            result: int | None
            size: int

        @dataclass
        class Stack(BasePolyInterface[StackState, StackInput, StackOutput]):
            state: StackState = field(default_factory=StackState)

            def scope(self, s: StackState) -> Type[StackInput]:
                return StackInput

            def dynamics(self, s: StackState, input: StackInput) -> tuple[StackState, StackOutput]:
                if isinstance(input, Push):
                    new_items = s.items + (input.value,)
                    return StackState(new_items), StackOutput(None, len(new_items))
                elif isinstance(input, Pop):
                    if s.items:
                        new_items = s.items[:-1]
                        return StackState(new_items), StackOutput(s.items[-1], len(new_items))
                    return s, StackOutput(None, 0)
                return s, StackOutput(None, len(s.items))

        stack = Stack()

        # Push
        state1, out1 = stack.dynamics(stack.state, Push(1))
        assert state1.items == (1,)
        assert out1.size == 1

        # Push more
        state2, out2 = stack.dynamics(state1, Push(2))
        state3, out3 = stack.dynamics(state2, Push(3))
        assert state3.items == (1, 2, 3)

        # Pop
        state4, out4 = stack.dynamics(state3, Pop())
        assert state4.items == (1, 2)
        assert out4.result == 3


class TestDynamicsComposition:
    """Tests for composing dynamics calls."""

    def test_chain_dynamics_calls(self) -> None:
        """Can chain multiple dynamics calls."""
        house = WorldHouse()
        state = house.state

        # Chain of operations
        state, _ = house.dynamics(state, ObserveHouse("architect", "view"))
        state, _ = house.dynamics(state, RenovateHouse({"room": "added"}))
        state, _ = house.dynamics(state, ObserveHouse("poet", "view"))
        state, _ = house.dynamics(state, InhabitHouse(10.0))

        assert state.observation_count == 2
        assert state.version == 4
        assert "structural_integrity" in state.reified_properties
        assert "atmosphere" in state.reified_properties
        assert "inhabited" in state.reified_properties

    def test_dynamics_threading_state(self) -> None:
        """State threads through dynamics calls correctly."""
        house = WorldHouse()

        # Explicit state threading
        s0 = house.state
        s1, _ = house.dynamics(s0, ObserveHouse("a", "x"))
        s2, _ = house.dynamics(s1, ObserveHouse("b", "y"))
        s3, _ = house.dynamics(s2, ObserveHouse("c", "z"))

        # Original unchanged
        assert s0.observation_count == 0

        # Each step incremented
        assert s1.observation_count == 1
        assert s2.observation_count == 2
        assert s3.observation_count == 3
