"""
StateConfig: Configuration for StateFunctor and StatefulAgent.

Provides configuration options for state threading behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, TypeVar

S = TypeVar("S")


@dataclass(frozen=True)
class StateConfig:
    """
    Configuration for state threading.

    Attributes:
        auto_save: Whether to automatically save state after each invoke.
            Default True. Set to False for batched operations.
        auto_load: Whether to automatically load state before each invoke.
            Default True. Set to False when state is passed explicitly.
        namespace: Namespace for state isolation. Different namespaces
            have independent state even with same backend.
        equality_check: Function to check if two states are equal.
            Used for optimization (skip save if unchanged).
            Default is structural equality (==).

    Example:
        # Default config: auto-save, auto-load
        config = StateConfig()

        # Batch mode: manual save control
        batch_config = StateConfig(auto_save=False)

        # Custom equality for complex state
        config = StateConfig(
            equality_check=lambda a, b: a.id == b.id
        )
    """

    auto_save: bool = True
    auto_load: bool = True
    namespace: str = "default"
    equality_check: Callable[[Any, Any], bool] = field(default_factory=lambda: lambda a, b: a == b)

    def with_namespace(self, namespace: str) -> "StateConfig":
        """Create a copy with different namespace."""
        return StateConfig(
            auto_save=self.auto_save,
            auto_load=self.auto_load,
            namespace=namespace,
            equality_check=self.equality_check,
        )


__all__ = [
    "StateConfig",
]
