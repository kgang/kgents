"""
Semantic Routing: Legacy stub for deleted module.

DEPRECATED: Use AssociativeMemory with embeddings instead.
"""

from dataclasses import dataclass, field
from typing import Any, Generic, TypeVar

T = TypeVar("T")


@dataclass
class LocalityConfig:
    """DEPRECATED: Old locality configuration."""

    threshold: float = 0.8
    max_distance: float = 1.0


@dataclass
class PrefixSimilarity:
    """DEPRECATED: Old prefix similarity calculator."""

    prefix_weight: float = 0.5

    def calculate(self, a: str, b: str) -> float:
        """Calculate prefix-based similarity."""
        common = 0
        for i, (ca, cb) in enumerate(zip(a, b)):
            if ca == cb:
                common = i + 1
            else:
                break
        return common / max(len(a), len(b)) if a and b else 0.0


@dataclass
class SemanticRouter(Generic[T]):
    """DEPRECATED: Old semantic router."""

    locality: LocalityConfig = field(default_factory=LocalityConfig)
    _routes: dict[str, T] = field(default_factory=dict, repr=False)

    def register(self, key: str, value: T) -> None:
        self._routes[key] = value

    def route(self, query: str) -> T | None:
        """Route a query to the best matching value."""
        best_key = None
        best_score = 0.0
        similarity = PrefixSimilarity()

        for key in self._routes:
            score = similarity.calculate(query, key)
            if score > best_score:
                best_score = score
                best_key = key

        if best_key and best_score >= self.locality.threshold:
            return self._routes[best_key]
        return None


def create_semantic_router() -> SemanticRouter[Any]:
    """Create a semantic router (DEPRECATED)."""
    return SemanticRouter()
