"""Tests for the Flux Functor."""

import pytest
from agents.flux import Flux, FluxAgent, FluxConfig, FluxLifter, is_flux
from agents.poly.types import Agent


# Test fixtures
class EchoAgent(Agent[str, str]):
    """Simple agent that returns input unchanged."""

    @property
    def name(self) -> str:
        return "Echo"

    async def invoke(self, input: str) -> str:
        return input


class DoubleAgent(Agent[int, int]):
    """Agent that doubles input."""

    @property
    def name(self) -> str:
        return "Double"

    async def invoke(self, input: int) -> int:
        return input * 2


class TestFluxLift:
    """Test Flux.lift() operation."""

    def test_lift_creates_flux_agent(self):
        agent = EchoAgent()
        flux_agent = Flux.lift(agent)

        assert isinstance(flux_agent, FluxAgent)

    def test_lift_preserves_inner(self):
        agent = EchoAgent()
        flux_agent = Flux.lift(agent)

        assert flux_agent.inner is agent

    def test_lift_with_default_config(self):
        agent = EchoAgent()
        flux_agent = Flux.lift(agent)

        assert flux_agent.config.entropy_budget == 1.0
        assert flux_agent.config.buffer_size == 100

    def test_lift_with_custom_config(self):
        agent = EchoAgent()
        config = FluxConfig(entropy_budget=5.0, buffer_size=50)
        flux_agent = Flux.lift(agent, config)

        assert flux_agent.config.entropy_budget == 5.0
        assert flux_agent.config.buffer_size == 50


class TestFluxUnlift:
    """Test Flux.unlift() operation."""

    def test_unlift_returns_inner(self):
        agent = EchoAgent()
        flux_agent = Flux.lift(agent)
        unlifted = Flux.unlift(flux_agent)

        assert unlifted is agent

    def test_unlift_type(self):
        agent = EchoAgent()
        flux_agent = Flux.lift(agent)
        unlifted = Flux.unlift(flux_agent)

        assert isinstance(unlifted, EchoAgent)


class TestIsFlux:
    """Test Flux.is_flux() / is_flux()."""

    def test_flux_agent_is_flux(self):
        agent = EchoAgent()
        flux_agent = Flux.lift(agent)

        assert Flux.is_flux(flux_agent) is True
        assert is_flux(flux_agent) is True

    def test_regular_agent_is_not_flux(self):
        agent = EchoAgent()

        assert Flux.is_flux(agent) is False
        assert is_flux(agent) is False

    def test_other_types_are_not_flux(self):
        assert is_flux("string") is False
        assert is_flux(123) is False
        assert is_flux(None) is False
        assert is_flux({}) is False


class TestFluxLiftWithConfig:
    """Test Flux.lift_with_config() factory."""

    def test_creates_lifter(self):
        lifter = Flux.lift_with_config(entropy_budget=2.0)

        assert isinstance(lifter, FluxLifter)

    def test_lifter_applies_config(self):
        lifter = Flux.lift_with_config(entropy_budget=2.0, buffer_size=50)
        agent = EchoAgent()
        flux_agent = lifter(agent)

        assert flux_agent.config.entropy_budget == 2.0
        assert flux_agent.config.buffer_size == 50

    def test_lifter_reusable(self):
        lifter = Flux.lift_with_config(entropy_budget=3.0)

        flux_a = lifter(EchoAgent())
        flux_b = lifter(DoubleAgent())

        assert flux_a.config.entropy_budget == 3.0
        assert flux_b.config.entropy_budget == 3.0

    def test_lifter_config_property(self):
        lifter = Flux.lift_with_config(entropy_budget=2.0)

        assert lifter.config.entropy_budget == 2.0


class TestFluxLifterWithConfig:
    """Test FluxLifter.with_config() method."""

    def test_with_config_creates_new_lifter(self):
        lifter1 = Flux.lift_with_config(entropy_budget=2.0)
        lifter2 = lifter1.with_config(buffer_size=50)

        assert lifter1 is not lifter2

    def test_with_config_overrides_value(self):
        lifter1 = Flux.lift_with_config(entropy_budget=2.0, buffer_size=100)
        lifter2 = lifter1.with_config(buffer_size=50)

        # Original unchanged
        assert lifter1.config.buffer_size == 100
        # New lifter has override
        assert lifter2.config.buffer_size == 50
        # Other values preserved
        assert lifter2.config.entropy_budget == 2.0

    def test_with_config_multiple_values(self):
        lifter = Flux.lift_with_config(entropy_budget=2.0)
        modified = lifter.with_config(
            buffer_size=50,
            drop_policy="drop_oldest",
            feedback_fraction=0.3,
        )

        assert modified.config.buffer_size == 50
        assert modified.config.drop_policy == "drop_oldest"
        assert modified.config.feedback_fraction == 0.3
        assert modified.config.entropy_budget == 2.0  # Preserved


class TestFluxAgentName:
    """Test FluxAgent name property."""

    def test_flux_agent_name(self):
        agent = EchoAgent()
        flux_agent = Flux.lift(agent)

        assert flux_agent.name == "Flux(Echo)"

    def test_double_agent_name(self):
        agent = DoubleAgent()
        flux_agent = Flux.lift(agent)

        assert flux_agent.name == "Flux(Double)"


class TestFluxAgentId:
    """Test FluxAgent id generation."""

    def test_auto_generated_id(self):
        flux_agent = Flux.lift(EchoAgent())

        assert flux_agent.id.startswith("flux-")
        assert len(flux_agent.id) == 13  # "flux-" + 8 hex chars

    def test_custom_id(self):
        config = FluxConfig(agent_id="my-custom-id")
        flux_agent = Flux.lift(EchoAgent(), config)

        assert flux_agent.id == "my-custom-id"

    def test_unique_ids(self):
        flux_a = Flux.lift(EchoAgent())
        flux_b = Flux.lift(EchoAgent())

        assert flux_a.id != flux_b.id


class TestFluxAgentInitialState:
    """Test FluxAgent initial state."""

    def test_initial_state_dormant(self):
        from agents.flux import FluxState

        flux_agent = Flux.lift(EchoAgent())

        assert flux_agent.state == FluxState.DORMANT

    def test_initial_events_processed(self):
        flux_agent = Flux.lift(EchoAgent())

        assert flux_agent.events_processed == 0

    def test_initial_entropy_remaining(self):
        config = FluxConfig(entropy_budget=5.0)
        flux_agent = Flux.lift(EchoAgent(), config)

        assert flux_agent.entropy_remaining == 5.0

    def test_is_running_initially_false(self):
        flux_agent = Flux.lift(EchoAgent())

        assert flux_agent.is_running is False
