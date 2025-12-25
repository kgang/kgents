"""
Tests for O-gent Observer Functor.

Minimal tests for the core observation abstraction.
"""

import pytest

from agents.o import (
    Agent,
    BaseObserver,
    ObservationStatus,
    ObserverFunctor,
    observe,
)


class SimpleAgent:
    """Simple test agent."""

    def __init__(self, name: str = "test"):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    async def invoke(self, input: int) -> int:
        """Double the input."""
        return input * 2


@pytest.mark.asyncio
async def test_observer_functor_basic():
    """Test that ObserverFunctor lifts an agent correctly."""
    import asyncio

    agent = SimpleAgent("doubler")
    observer = BaseObserver("test_observer")
    functor = ObserverFunctor(observer)

    # Lift the agent
    observed = functor.lift(agent)

    # Should behave identically
    result = await observed.invoke(5)
    assert result == 10

    # Wait for async observation to complete
    await asyncio.sleep(0.1)

    # Should have recorded observation
    assert len(observer.observations) == 1
    obs = observer.observations[0]
    assert obs.status == ObservationStatus.COMPLETED
    assert obs.output_data == 10
    assert obs.context.input_data == 5


@pytest.mark.asyncio
async def test_observe_convenience():
    """Test the observe() convenience function."""
    agent = SimpleAgent("doubler")

    # Use convenience function
    observed = observe(agent)

    # Should work
    result = await observed.invoke(3)
    assert result == 6


@pytest.mark.asyncio
async def test_observation_on_error():
    """Test that observation records errors correctly."""

    class FailingAgent:
        """Agent that always fails."""

        @property
        def name(self) -> str:
            return "failer"

        async def invoke(self, input: int) -> int:
            raise ValueError("Intentional failure")

    agent = FailingAgent()
    observer = BaseObserver("error_observer")
    observed = observe(agent, observer)

    # Should raise the error
    with pytest.raises(ValueError, match="Intentional failure"):
        await observed.invoke(1)

    # Should have recorded failed observation
    assert len(observer.observations) == 1
    obs = observer.observations[0]
    assert obs.status == ObservationStatus.FAILED
    assert obs.error == "Intentional failure"
    assert obs.telemetry.get("exception_type") == "ValueError"
