"""
Symbiont: Fuses stateless logic with stateful memory.

The Symbiont pattern embodies endosymbiotic composition where pure logic
(the "host") gains memory through integration with a D-gent (the "organelle").
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Awaitable, Callable, Generic, TypeVar, Union, cast

from bootstrap.types import Agent

from .protocol import DataAgent

S = TypeVar("S")  # State
In = TypeVar("In")  # Input
Out = TypeVar("Out")  # Output


@dataclass
class Symbiont(Agent[In, Out], Generic[In, Out, S]):
    """
    Fuses stateless logic with stateful memory.

    The logic function is pure: (Input, CurrentState) → (Output, NewState)
    The D-gent handles persistence transparently.

    This makes Symbiont a valid bootstrap Agent, composable via >>.

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
    """

    logic: Union[
        Callable[[In, S], tuple[Out, S]],
        Callable[[In, S], Awaitable[tuple[Out, S]]],
    ]
    memory: DataAgent[S]

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
