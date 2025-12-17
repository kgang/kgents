"""
StateFunctor: The State Monad as a Universal Functor.

This module implements S-gent's core abstraction: lifting agents into
stateful computation where state is transparently loaded and saved.

Category-theoretic insight:
    StateFunctor[S]: Agent[A, B] → StatefulAgent[S, A, B]

    The lifted agent:
    1. Loads state S before invoking the inner agent
    2. Threads state through the computation
    3. Saves new state after invocation
    4. Returns output B

Functor Laws:
    Identity:    StateFunctor.lift(Id) ≅ Id
    Composition: lift(f >> g) ≅ lift(f) >> lift(g)

Relationship to Symbiont:
    StateFunctor.lift_logic(f) ≡ Symbiont(logic=f, memory=backend)
    StateFunctor is the general form; Symbiont is the ergonomic pattern.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Any,
    Awaitable,
    Callable,
    Generic,
    TypeVar,
    Union,
    cast,
)

from agents.a.functor import FunctorRegistry, UniversalFunctor
from agents.poly.types import Agent

from .config import StateConfig
from .protocol import StateBackend

if TYPE_CHECKING:
    from agents.flux.agent import FluxAgent

# Type variables
S = TypeVar("S")  # State type
A = TypeVar("A")  # Input type
B = TypeVar("B")  # Output type
C = TypeVar("C")  # For composition


# =============================================================================
# StatefulAgent: The Lifted Agent
# =============================================================================


@dataclass
class StatefulAgent(Agent[A, B], Generic[S, A, B]):
    """
    An agent with transparent state threading.

    StatefulAgent wraps an inner agent and provides automatic state
    management: load before invoke, save after invoke.

    The inner agent can be:
    1. A logic function: (A, S) → (B, S) - pure state transformation
    2. A regular agent: A → B - state passed but not modified

    State lifecycle per invocation:
        1. Load: state = await backend.load()
        2. Invoke: result = await inner.invoke((input, state)) or inner.invoke(input)
        3. Parse: extract (output, new_state) or (output, state)
        4. Save: await backend.save(new_state)
        5. Return: output

    Example:
        # With logic function
        def counter(input: str, state: int) -> tuple[str, int]:
            return f"Count: {state}", state + 1

        agent = StatefulAgent(
            inner=_LogicAgent(counter),
            backend=MemoryStateBackend(initial=0),
            config=StateConfig(),
        )
        result = await agent.invoke("tick")  # "Count: 0"
        result = await agent.invoke("tick")  # "Count: 1"
    """

    inner: Agent[Any, Any]
    backend: StateBackend[S]
    config: StateConfig = field(default_factory=StateConfig)

    @property
    def name(self) -> str:
        """Human-readable name for composition chains."""
        inner_name = getattr(self.inner, "name", "agent")
        return f"Stateful({inner_name})"

    async def invoke(self, input_data: A) -> B:
        """
        Invoke with state threading.

        Handles both:
        - Logic functions that expect (input, state) and return (output, new_state)
        - Regular agents that just process input (state unchanged)
        """
        # 1. Load current state
        if self.config.auto_load:
            state = await self.backend.load()
        else:
            state = None  # Caller manages state

        # 2. Invoke inner agent
        try:
            # Try invoking with (input, state) tuple
            result = await self.inner.invoke((input_data, state))

            # 3. Parse result
            if isinstance(result, tuple) and len(result) == 2:
                output, new_state = result
            else:
                # Inner agent doesn't return state tuple
                output = result
                new_state = state
        except TypeError:
            # Inner agent doesn't accept tuple, invoke with just input
            output = await self.inner.invoke(input_data)
            new_state = state

        # 4. Save new state
        if self.config.auto_save and new_state is not None:
            # Skip save if state unchanged (optimization)
            if state is None or not self.config.equality_check(state, new_state):
                await self.backend.save(new_state)

        # 5. Return output
        return cast(B, output)

    def __rshift__(self, other: Agent[B, C]) -> "StatefulAgent[S, A, C]":
        """
        Compose with another agent: stateful >> other.

        The composed agent threads state through self, then passes
        output to other (which doesn't see state).
        """
        from agents.poly.types import ComposedAgent

        # Compose the inner agents
        composed_inner = ComposedAgent(self.inner, other)
        return StatefulAgent(
            inner=composed_inner,
            backend=self.backend,
            config=self.config,
        )


# =============================================================================
# Internal: Logic Function Wrapper
# =============================================================================


@dataclass
class _LogicAgent(Agent[tuple[A, S], tuple[B, S]], Generic[A, B, S]):
    """
    Wraps a pure logic function as an Agent.

    The logic function has signature: (A, S) → (B, S)
    This agent expects input as (A, S) tuple and returns (B, S) tuple.
    """

    logic: Union[
        Callable[[A, S], tuple[B, S]],
        Callable[[A, S], Awaitable[tuple[B, S]]],
    ]

    @property
    def name(self) -> str:
        return f"Logic({getattr(self.logic, '__name__', 'fn')})"

    async def invoke(self, input_data: tuple[A, S]) -> tuple[B, S]:
        """Execute the logic function."""
        a, s = input_data

        # Handle both sync and async logic
        if asyncio.iscoroutinefunction(self.logic):
            return await self.logic(a, s)
        else:
            sync_logic = cast(Callable[[A, S], tuple[B, S]], self.logic)
            return sync_logic(a, s)


# =============================================================================
# StateFunctor: The Universal Functor
# =============================================================================


class StateFunctor(UniversalFunctor["StatefulAgent[Any, Any, Any]"], Generic[S]):
    """
    State Monad as a Universal Functor.

    Lifts agents into stateful computation:
        StateFunctor[S]: Agent[A, B] → StatefulAgent[S, A, B]

    The lifted agent automatically:
    - Loads state before each invocation
    - Threads state through computation
    - Saves state after each invocation

    Functor Laws:
        Identity:    lift(Id) ≅ Id (modulo state overhead)
        Composition: lift(f >> g) ≅ lift(f) >> lift(g)

    Example:
        # Create functor with backend
        state_functor = StateFunctor.create(
            backend=MemoryStateBackend(initial={"count": 0}),
        )

        # Lift an agent
        stateful = state_functor.lift(process_agent)

        # Or lift pure logic directly
        stateful = state_functor.lift_logic(
            lambda input, state: (f"count={state['count']}", {**state, 'count': state['count']+1})
        )
    """

    # Instance configuration (for lift_logic and compose_flux)
    _backend: StateBackend[S] | None = None
    _config: StateConfig | None = None

    def __init__(
        self,
        backend: StateBackend[S] | None = None,
        config: StateConfig | None = None,
    ) -> None:
        """
        Initialize StateFunctor with optional backend and config.

        Args:
            backend: State backend for persistence
            config: Configuration for state threading
        """
        self._backend = backend
        self._config = config or StateConfig()

    @staticmethod
    def lift(
        agent: Agent[A, B],
        backend: StateBackend[S] | None = None,
        config: StateConfig | None = None,
    ) -> StatefulAgent[S, A, B]:
        """
        Lift an agent into stateful computation.

        Args:
            agent: The agent to lift
            backend: State backend (required)
            config: Optional configuration

        Returns:
            StatefulAgent that threads state through the inner agent

        Raises:
            ValueError: If backend is not provided
        """
        if backend is None:
            raise ValueError("StateFunctor.lift() requires a backend")

        return StatefulAgent(
            inner=agent,
            backend=backend,
            config=config or StateConfig(),
        )

    def lift_logic(
        self,
        logic: Union[
            Callable[[A, S], tuple[B, S]],
            Callable[[A, S], Awaitable[tuple[B, S]]],
        ],
    ) -> StatefulAgent[S, A, B]:
        """
        Lift a pure logic function into a StatefulAgent.

        This is the Symbiont pattern: transform pure state logic
        into a composable agent with automatic persistence.

        Args:
            logic: Pure function (A, S) → (B, S)

        Returns:
            StatefulAgent wrapping the logic

        Example:
            def chat_logic(msg: str, history: list) -> tuple[str, list]:
                response = f"Echo: {msg}"
                return response, history + [msg, response]

            chat = state_functor.lift_logic(chat_logic)
            await chat.invoke("Hello")  # "Echo: Hello"
        """
        if self._backend is None:
            raise ValueError("StateFunctor requires backend for lift_logic()")

        logic_agent: _LogicAgent[A, B, S] = _LogicAgent(logic=logic)
        return StatefulAgent(
            inner=logic_agent,
            backend=self._backend,
            config=self._config or StateConfig(),
        )

    @staticmethod
    def unlift(agent: StatefulAgent[S, A, B]) -> Agent[A, B]:
        """
        Extract the inner agent from a StatefulAgent.

        Satisfies the symmetric lifting law:
            unlift(lift(agent)) ≅ agent

        Note: The extracted agent loses state threading.
        """
        return agent.inner

    @staticmethod
    def pure(value: A) -> tuple[A, None]:
        """
        Embed a value as an identity state computation.

        Returns (value, None) - the value with no state change.
        """
        return (value, None)

    @classmethod
    def create(
        cls,
        backend: StateBackend[S],
        config: StateConfig | None = None,
    ) -> "StateFunctor[S]":
        """
        Create a StateFunctor instance with configured backend.

        This is the preferred way to create StateFunctor for lift_logic.

        Example:
            functor = StateFunctor.create(
                backend=MemoryStateBackend(initial=0),
            )
            counter = functor.lift_logic(lambda x, s: (s, s + 1))
        """
        return cls(backend=backend, config=config)

    @staticmethod
    def compose_flux(
        backend: StateBackend[S],
        config: StateConfig | None = None,
    ) -> Callable[[Agent[A, B]], "FluxAgent[A, B]"]:
        """
        Compose State functor with Flux functor.

        Returns: Flux ∘ State

        The composed functor creates an agent that:
        1. Processes events as a stream (Flux)
        2. Threads state through each event (State)

        Example:
            FluxState = StateFunctor.compose_flux(backend)
            flux_stateful = FluxState(process_agent)

            async for result in flux_stateful.start(events):
                print(result)  # Each event processed with state
        """
        from agents.flux import Flux

        def composed_lift(agent: Agent[A, B]) -> "FluxAgent[A, B]":
            stateful = StateFunctor.lift(agent, backend=backend, config=config)
            return Flux.lift(stateful)

        return composed_lift


# =============================================================================
# Registration
# =============================================================================


def _register_state_functor() -> None:
    """Register StateFunctor with the universal registry."""
    FunctorRegistry.register("State", StateFunctor)


# Auto-register on import
_register_state_functor()


__all__ = [
    "StateFunctor",
    "StatefulAgent",
]
