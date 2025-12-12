"""
State Monad Functor: Composable Stateful Computation.

The State Monad lifts agents into a context where state is threaded
through computation automatically:

    StateMonad: Agent[A, B] → StatefulAgent[A, B, S]

Where each invocation:
1. Loads state from memory
2. Makes state available to the computation
3. Saves updated state after computation
4. Returns the result

This enables composition with Flux and other functors:
    Flux.lift(StateMonad.lift(agent))  # Streaming + State

Mathematical Properties:
    - State Monad: StateT s m a = s → m (a, s)
    - Functor Laws: StateMonad(id) ≅ id, StateMonad(g >> f) ≅ StateMonad(g) >> StateMonad(f)
    - Symmetric Lifting: unlift(lift(agent)) ≅ agent

See: plans/architecture/categorical-consolidation.md Phase 3
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Generic, TypeVar

from agents.a.functor import FunctorRegistry, UniversalFunctor
from bootstrap.types import Agent, ComposedAgent

from .protocol import DataAgent
from .volatile import VolatileAgent

A = TypeVar("A")
B = TypeVar("B")
S = TypeVar("S")


# =============================================================================
# State Context: Thread state through computation
# =============================================================================


@dataclass
class StateContext(Generic[S]):
    """
    Context for stateful computation.

    Wraps the current state and provides access patterns.
    The state is immutable within a computation step.
    """

    state: S
    metadata: dict[str, Any] = field(default_factory=dict)

    def with_state(self, new_state: S) -> "StateContext[S]":
        """Create new context with updated state."""
        return StateContext(state=new_state, metadata=self.metadata.copy())


# =============================================================================
# Stateful Agent: The Lifted Agent
# =============================================================================


class StatefulAgent(Generic[A, B, S]):
    """
    An agent with automatically threaded state.

    Wraps an inner agent and a memory (DataAgent). Each invocation:
    1. Loads current state from memory
    2. Invokes the inner agent (state available via accessor)
    3. Saves any state updates
    4. Returns the result

    The state is transparent to composition—StatefulAgent implements
    the Agent[A, B] interface and can be composed via >>.
    """

    def __init__(
        self,
        inner: Agent[A, B],
        memory: DataAgent[S],
        state_accessor: Callable[[A, S], A] | None = None,
        state_extractor: Callable[[B, S], tuple[B, S]] | None = None,
    ) -> None:
        """
        Create a stateful agent.

        Args:
            inner: The agent to lift
            memory: Where to load/save state
            state_accessor: Optional function to inject state into input
            state_extractor: Optional function to extract new state from output
        """
        self._inner = inner
        self._memory = memory
        self._state_accessor = state_accessor
        self._state_extractor = state_extractor
        self._last_state: S | None = None

    @property
    def name(self) -> str:
        """Name of the stateful agent."""
        return f"State({self._inner.name})"

    @property
    def inner(self) -> Agent[A, B]:
        """Access the inner (unlifted) agent."""
        return self._inner

    @property
    def memory(self) -> DataAgent[S]:
        """Access the memory (state storage)."""
        return self._memory

    @property
    def last_state(self) -> S | None:
        """Last loaded state (for inspection)."""
        return self._last_state

    async def invoke(self, input: A) -> B:
        """
        Invoke the agent with automatic state threading.

        The state is loaded before invocation and can be updated
        by the state_extractor after invocation.
        """
        # 1. Load current state
        current_state = await self._memory.load()
        self._last_state = current_state

        # 2. Optionally inject state into input
        actual_input = input
        if self._state_accessor:
            actual_input = self._state_accessor(input, current_state)

        # 3. Invoke inner agent
        result = await self._inner.invoke(actual_input)

        # 4. Optionally extract and save new state
        if self._state_extractor:
            result, new_state = self._state_extractor(result, current_state)
            await self._memory.save(new_state)
            self._last_state = new_state

        return result

    def __rshift__(self, other: Agent[B, Any]) -> Any:
        """Compose with another agent."""
        return ComposedAgent(self, other)  # type: ignore[arg-type]


# =============================================================================
# State Monad Functor
# =============================================================================


class StateMonadFunctor(UniversalFunctor[StatefulAgent[Any, Any, Any]]):
    """
    State Monad Functor: Lifts agents to thread state through computation.

    This functor transforms Agent[A, B] → StatefulAgent[A, B, S] where
    state is automatically loaded before and saved after each invocation.

    Satisfies functor laws:
    - Identity: lift(id) behaves like identity (with state threading)
    - Composition: lift(g >> f) ≅ lift(g) >> lift(f)

    Usage:
        # Basic: state is loaded/available but not transformed
        stateful = StateMonadFunctor.lift(agent, memory=my_memory)

        # With state injection (state added to input)
        stateful = StateMonadFunctor.lift(
            agent,
            memory=my_memory,
            state_accessor=lambda input, state: {"data": input, "ctx": state}
        )

        # With state extraction (state updated from output)
        stateful = StateMonadFunctor.lift(
            agent,
            memory=my_memory,
            state_extractor=lambda output, _: (output["result"], output["new_state"])
        )

        # Compose with Flux for streaming + state
        flux_stateful = Flux.lift(stateful)
    """

    # Default memory factory
    _default_memory_factory: Callable[[], DataAgent[Any]] | None = None

    @classmethod
    def set_default_memory_factory(cls, factory: Callable[[], DataAgent[Any]]) -> None:
        """Set the default memory factory for stateful agents."""
        cls._default_memory_factory = factory

    @staticmethod
    def lift(
        agent: Agent[A, B],
        memory: DataAgent[S] | None = None,
        initial_state: S | None = None,
        state_accessor: Callable[[A, S], A] | None = None,
        state_extractor: Callable[[B, S], tuple[B, S]] | None = None,
    ) -> Agent[Any, Any]:
        """
        Lift an agent to thread state through computation.

        Args:
            agent: The agent to lift
            memory: State storage (defaults to VolatileAgent with initial_state)
            initial_state: Initial state if creating default memory
            state_accessor: Optional function to inject state into input
            state_extractor: Optional function to extract new state from output

        Returns:
            StatefulAgent wrapping the input agent
        """
        # Create default memory if not provided
        actual_memory: DataAgent[Any]
        if memory is not None:
            actual_memory = memory
        elif StateMonadFunctor._default_memory_factory:
            actual_memory = StateMonadFunctor._default_memory_factory()
        else:
            actual_memory = VolatileAgent(
                _state=initial_state if initial_state is not None else {}
            )

        result = StatefulAgent(
            inner=agent,
            memory=actual_memory,
            state_accessor=state_accessor,
            state_extractor=state_extractor,
        )
        return result  # type: ignore[return-value]

    @staticmethod
    def unlift(agent: Agent[Any, Any]) -> Agent[Any, Any]:
        """
        Extract inner agent from StatefulAgent.

        Args:
            agent: A StatefulAgent to unwrap

        Returns:
            The inner discrete agent

        Raises:
            TypeError: If agent is not a StatefulAgent
        """
        if not isinstance(agent, StatefulAgent):
            raise TypeError(
                f"Cannot unlift {type(agent).__name__} - not a StatefulAgent"
            )
        return agent.inner

    @staticmethod
    def pure(value: A) -> A:
        """State monad functor is an endofunctor; pure returns value unchanged."""
        return value

    @staticmethod
    def get_memory(agent: Agent[Any, Any]) -> DataAgent[Any] | None:
        """
        Extract memory from a StatefulAgent.

        Args:
            agent: A StatefulAgent to inspect

        Returns:
            The memory (DataAgent) or None if not a StatefulAgent
        """
        if isinstance(agent, StatefulAgent):
            return agent.memory
        return None


# =============================================================================
# Convenience Functions
# =============================================================================


def stateful(
    agent: Agent[A, B],
    memory: DataAgent[S] | None = None,
    initial_state: S | None = None,
    state_accessor: Callable[[A, S], A] | None = None,
    state_extractor: Callable[[B, S], tuple[B, S]] | None = None,
) -> StatefulAgent[A, B, S]:
    """
    Lift an agent to be stateful.

    Convenience function for StateMonadFunctor.lift().

    Args:
        agent: The agent to lift
        memory: State storage (defaults to VolatileAgent)
        initial_state: Initial state if creating default memory
        state_accessor: Optional function to inject state into input
        state_extractor: Optional function to extract new state from output

    Returns:
        StatefulAgent that threads state through computation
    """
    actual_memory: DataAgent[Any]
    if memory is not None:
        actual_memory = memory
    else:
        actual_memory = VolatileAgent(
            _state=initial_state if initial_state is not None else {}
        )

    return StatefulAgent(
        inner=agent,
        memory=actual_memory,
        state_accessor=state_accessor,
        state_extractor=state_extractor,
    )


def unstateful(agent: StatefulAgent[A, B, S]) -> Agent[A, B]:
    """
    Extract inner agent from stateful wrapper.

    Convenience function for StateMonadFunctor.unlift().
    """
    return agent.inner


# =============================================================================
# Registry
# =============================================================================


def _register_state_monad_functor() -> None:
    """Register StateMonadFunctor with the universal registry."""
    FunctorRegistry.register("State", StateMonadFunctor)


# Auto-register on import
_register_state_monad_functor()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Core types
    "StateContext",
    "StatefulAgent",
    "StateMonadFunctor",
    # Convenience functions
    "stateful",
    "unstateful",
]
