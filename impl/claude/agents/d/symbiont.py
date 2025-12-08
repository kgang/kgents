"""
Symbiont: Fuses stateless logic with stateful memory.

The Symbiont pattern embodies endosymbiotic composition where pure logic
(the "host") gains memory through integration with a D-gent (the "organelle").
"""

from typing import TypeVar, Generic, Callable, Union, Awaitable, Any
from dataclasses import dataclass
import asyncio

from bootstrap.types import Agent
from .protocol import DataAgent

S = TypeVar("S")  # State
I = TypeVar("I")  # Input
O = TypeVar("O")  # Output


@dataclass
class Symbiont(Agent[I, O], Generic[I, O, S]):
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
        Callable[[I, S], tuple[O, S]],
        Callable[[I, S], Awaitable[tuple[O, S]]],
    ]
    memory: DataAgent[S]

    @property
    def name(self) -> str:
        """Name for composition chains."""
        return f"Symbiont({getattr(self.logic, '__name__', 'logic')})"

    async def invoke(self, input_data: I) -> O:
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
        if asyncio.iscoroutinefunction(self.logic):
            output, new_state = await self.logic(input_data, current_state)
        else:
            output, new_state = self.logic(input_data, current_state)

        # 3. Persist side effects
        await self.memory.save(new_state)

        # 4. Return output
        return output
