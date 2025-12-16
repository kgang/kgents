"""
StateMonadFunctor: Legacy stub for deleted module.

DEPRECATED: Use DgentRouter + MemoryBackend instead.
"""

from dataclasses import dataclass
from typing import Any, Generic, TypeVar

S = TypeVar("S")
A = TypeVar("A")


@dataclass
class StateMonadFunctor(Generic[S]):
    """
    DEPRECATED: Old state monad functor.

    Use DgentRouter with backends instead.
    """

    initial: S

    def run(self, f: Any) -> tuple[Any, S]:
        """Run a stateful computation."""
        return f(self.initial), self.initial
