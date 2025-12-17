"""
Symbiont: Fuses stateless logic with stateful memory.

The Symbiont pattern embodies endosymbiotic composition where pure logic
(the "host") gains memory through integration with a D-gent (the "organelle").

Category-theoretic insight:
    Symbiont IS StateFunctor.lift_logic with a state backend.
    It's the canonical composition of S-gent (state threading) and D-gent (persistence).

Relationship to S-gent:
    Symbiont(logic, memory) ≡ StateFunctor.create(backend=memory).lift_logic(logic)

    Symbiont is the ergonomic pattern; StateFunctor is the formal functor.
    Use Symbiont for direct usage; use StateFunctor when you need:
    - Flux composition (StateFunctor.compose_flux)
    - Law verification
    - Functor registry integration

See Also:
    - agents.s.StateFunctor — The formal State functor
    - agents.s.StatefulAgent — The lifted agent type
    - spec/s-gents/README.md — S-gent specification
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import TYPE_CHECKING, Awaitable, Callable, Generic, TypeVar, Union, cast

from agents.poly.types import Agent

if TYPE_CHECKING:
    from agents.s.protocol import StateBackend

from .protocol import DataAgent

S = TypeVar("S")  # State
In = TypeVar("In")  # Input
Out = TypeVar("Out")  # Output

# Type alias: Symbiont accepts any object with load/save methods
# This includes DataAgent[S], StateBackend[S], VolatileAgent, etc.
MemoryProtocol = Union[DataAgent[S], "StateBackend[S]"]


@dataclass
class Symbiont(Agent[In, Out], Generic[In, Out, S]):
    """
    Fuses stateless logic with stateful memory.

    The logic function is pure: (Input, CurrentState) → (Output, NewState)
    The memory backend handles persistence transparently.

    This makes Symbiont a valid bootstrap Agent, composable via >>.

    Symbiont IS the canonical S >> D pattern:
    - S-gent: State threading (via logic function)
    - D-gent: Persistence (via memory backend)

    Example:
        >>> def chat_logic(msg: str, history: list) -> tuple[str, list]:
        ...     history.append(("user", msg))
        ...     response = "Echo: " + msg
        ...     history.append(("bot", response))
        ...     return response, history
        ...
        >>> memory = VolatileAgent(_state=[])
        >>> chatbot = Symbiont(logic=chat_logic, memory=memory)
        >>> await chatbot.invoke("Hello")  # Returns "Echo: Hello"

    Equivalent to:
        >>> from agents.s import StateFunctor, MemoryStateBackend
        >>> backend = MemoryStateBackend(initial=[])
        >>> functor = StateFunctor.create(backend=backend)
        >>> chatbot = functor.lift_logic(chat_logic)
    """

    logic: Union[
        Callable[[In, S], tuple[Out, S]],
        Callable[[In, S], Awaitable[tuple[Out, S]]],
    ]
    memory: DataAgent[S]  # Also accepts StateBackend[S] via duck typing

    @property
    def name(self) -> str:
        """Name for composition chains."""
        return f"Symbiont({getattr(self.logic, '__name__', 'logic')})"

    async def invoke(self, input_data: In) -> Out:
        """
        Execute the stateful computation.

        Steps:
        1. Load current state from memory
        2. Run pure logic: (input, state) → (output, new_state)
        3. Save new state to memory
        4. Return output

        The logic function can be sync or async - we detect and adapt.
        """
        # 1. Load current context
        current_state = await self.memory.load()

        # 2. Pure computation (detect sync vs async)
        result: tuple[Out, S]
        if asyncio.iscoroutinefunction(self.logic):
            result = await self.logic(input_data, current_state)
        else:
            # Type narrowing: we know logic is sync here
            sync_logic = cast(Callable[[In, S], tuple[Out, S]], self.logic)
            result = sync_logic(input_data, current_state)

        output, new_state = result

        # 3. Persist side effects
        await self.memory.save(new_state)

        # 4. Return output
        return output
