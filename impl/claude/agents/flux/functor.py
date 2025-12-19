"""
Flux Functor: The lift mechanism.

The Flux Functor lifts agents from the domain of Discrete State to the
domain of Continuous Flow:

    Flux: Agent[A, B] → Agent[Flux[A], Flux[B]]

Where Flux[T] = AsyncIterator[T]

Functor Laws:
    Identity:    Flux(Id) ≅ Id_Flux
    Composition: Flux(f >> g) ≅ Flux(f) >> Flux(g)

Universal Functor Integration (Alethic Algebra Phase 3):
    FluxFunctor implements UniversalFunctor[FluxAgent], enabling:
    - Law verification via verify_functor()
    - Registry integration with other functors
    - Functor composition: compose_functors(FluxFunctor, MaybeFunctor)
"""

from typing import Any, AsyncIterator, TypeVar

from agents.poly.types import Agent

from .agent import FluxAgent
from .config import FluxConfig

A = TypeVar("A")
B = TypeVar("B")


class Flux:
    """
    The Flux Functor: Agent[A, B] → Agent[Flux[A], Flux[B]]

    Lifts an agent from Discrete State to Continuous Flow.

    Functor Laws:
        Identity:    Flux(Id) ≅ Id_Flux
        Composition: Flux(f >> g) ≅ Flux(f) >> Flux(g)

    Usage:
        >>> flux_agent = Flux.lift(my_agent)
        >>> async for result in flux_agent.start(source):
        ...     process(result)

    The lift operation transforms an agent that processes single
    inputs into one that processes streams of inputs and produces
    streams of outputs.

    Key Insight:
        "The noun is a lie. There is only the rate of change."

        Static:  Agent: A → B           (a point transformation)
        Dynamic: Flux(Agent): dA/dt → dB/dt  (a continuous flow)
    """

    @staticmethod
    def lift(
        agent: Agent[A, B],
        config: FluxConfig | None = None,
    ) -> FluxAgent[A, B]:
        """
        Lift agent to flux domain.

        This is the core functor operation. It takes a discrete agent
        (one that processes single inputs) and lifts it to the streaming
        domain (one that processes and produces streams).

        Args:
            agent: The discrete agent to lift
            config: Optional configuration for flux behavior

        Returns:
            FluxAgent wrapping the input agent

        Example:
            >>> from agents.poly import Id
            >>> flux_id = Flux.lift(Id())
            >>> # flux_id now maps AsyncIterator[A] → AsyncIterator[A]
        """
        return FluxAgent(
            inner=agent,
            config=config or FluxConfig(),
        )

    @staticmethod
    def unlift(flux_agent: FluxAgent[A, B]) -> Agent[A, B]:
        """
        Extract inner agent from flux.

        Note: Does NOT stop a running flux.
        Call flux_agent.stop() first if needed.

        This is useful when you need to access the original
        discrete agent for single invocations or inspection.

        Args:
            flux_agent: The FluxAgent to extract from

        Returns:
            The inner discrete agent
        """
        return flux_agent.inner

    @staticmethod
    def is_flux(agent: Any) -> bool:
        """
        Check if agent is a FluxAgent.

        Args:
            agent: Any object to check

        Returns:
            True if agent is a FluxAgent instance
        """
        return isinstance(agent, FluxAgent)

    @staticmethod
    def lift_with_config(
        entropy_budget: float = 1.0,
        entropy_decay: float = 0.01,
        buffer_size: int = 100,
        drop_policy: str = "block",
        feedback_fraction: float = 0.0,
    ) -> "FluxLifter":
        """
        Create a configured lifter for lifting multiple agents.

        This is useful when you want to apply the same configuration
        to multiple agents.

        Args:
            entropy_budget: Initial entropy budget
            entropy_decay: Entropy consumed per event
            buffer_size: Output buffer size
            drop_policy: Backpressure policy
            feedback_fraction: Ouroboric feedback fraction

        Returns:
            FluxLifter configured with the given parameters

        Example:
            >>> lifter = Flux.lift_with_config(buffer_size=50)
            >>> flux_a = lifter(agent_a)
            >>> flux_b = lifter(agent_b)
        """
        config = FluxConfig(
            entropy_budget=entropy_budget,
            entropy_decay=entropy_decay,
            buffer_size=buffer_size,
            drop_policy=drop_policy,
            feedback_fraction=feedback_fraction,
        )
        return FluxLifter(config)


class FluxLifter:
    """
    A configured lifter that can lift multiple agents with the same config.

    Created via Flux.lift_with_config().
    """

    def __init__(self, config: FluxConfig):
        self._config = config

    def __call__(self, agent: Agent[A, B]) -> FluxAgent[A, B]:
        """
        Lift an agent using this lifter's configuration.

        Args:
            agent: The agent to lift

        Returns:
            FluxAgent with this lifter's configuration
        """
        return Flux.lift(agent, self._config)

    @property
    def config(self) -> FluxConfig:
        """The configuration used by this lifter."""
        return self._config

    def with_config(self, **kwargs: Any) -> "FluxLifter":
        """
        Create a new lifter with modified configuration.

        Args:
            **kwargs: Configuration parameters to override

        Returns:
            New FluxLifter with modified configuration
        """
        # Build new config from current + overrides
        config_dict = {
            "entropy_budget": self._config.entropy_budget,
            "entropy_decay": self._config.entropy_decay,
            "max_events": self._config.max_events,
            "buffer_size": self._config.buffer_size,
            "drop_policy": self._config.drop_policy,
            "feedback_fraction": self._config.feedback_fraction,
            "feedback_transform": self._config.feedback_transform,
            "feedback_queue_size": self._config.feedback_queue_size,
            "emit_pheromones": self._config.emit_pheromones,
            "trace_enabled": self._config.trace_enabled,
            "agent_id": self._config.agent_id,
            "perturbation_timeout": self._config.perturbation_timeout,
            "perturbation_priority": self._config.perturbation_priority,
        }
        config_dict.update(kwargs)
        return FluxLifter(FluxConfig(**config_dict))  # type: ignore[arg-type]


# Convenience aliases
lift = Flux.lift
unlift = Flux.unlift
is_flux = Flux.is_flux


# =============================================================================
# Universal Functor Protocol Integration (Alethic Algebra Phase 3)
# =============================================================================

from agents.a.functor import FunctorRegistry, UniversalFunctor


class FluxFunctor(UniversalFunctor[FluxAgent[Any, Any]]):
    """
    Universal Functor for Flux (stream processing) context.

    Lifts agents from the discrete domain (Agent[A, B]) to the streaming
    domain (FluxAgent[A, B]) where streams are AsyncIterator[T].

    Satisfies functor laws:
    - Identity: FluxFunctor.lift(id)(stream) processes identity on each element
    - Composition: FluxFunctor.lift(g . f) = FluxFunctor.lift(g) . FluxFunctor.lift(f)

    Note on Law Verification:
        FluxFunctor operates on streams (AsyncIterator), not discrete values.
        Law verification requires special handling because:
        1. start() returns AsyncIterator[B], not a single value
        2. Testing must collect stream outputs for comparison
        3. The identity/composition laws hold per-element across the stream

    Example:
        >>> flux_agent = FluxFunctor.lift(my_agent)
        >>> async for result in flux_agent.start(source):
        ...     process(result)
    """

    @staticmethod
    def lift(agent: Agent[A, B]) -> Any:
        """
        Lift an agent to the streaming domain.

        Args:
            agent: Discrete agent to lift

        Returns:
            FluxAgent that processes streams through the inner agent

        Note:
            Returns FluxAgent[A, B] at runtime. The return type is Any because
            FluxAgent is not an Agent subclass (it represents stream processing,
            not discrete invocation). This matches the UniversalFunctor protocol
            while preserving the actual FluxAgent behavior.
        """
        return Flux.lift(agent)

    @staticmethod
    def pure(value: A) -> AsyncIterator[A]:
        """
        Embed a value as a single-element stream.

        In the Flux context, pure creates an async iterator that yields
        exactly one value. This satisfies the Pointed functor requirement.

        Args:
            value: The value to embed

        Returns:
            An AsyncIterator yielding only this value
        """

        async def single_value_stream() -> AsyncIterator[A]:
            yield value

        return single_value_stream()


def _register_flux_functor() -> None:
    """Register FluxFunctor with the universal registry."""
    FunctorRegistry.register("Flux", FluxFunctor)


# Auto-register on import
_register_flux_functor()
