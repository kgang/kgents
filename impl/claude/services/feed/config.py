"""
Feed Configuration: Configurable ranking weights for algorithmic discovery.

Environment variables:
- KGENTS_FEED_ATTENTION_WEIGHT: Weight for attention scoring (default: 0.4)
- KGENTS_FEED_PRINCIPLES_WEIGHT: Weight for principles alignment (default: 0.3)
- KGENTS_FEED_RECENCY_WEIGHT: Weight for temporal freshness (default: 0.2)
- KGENTS_FEED_COHERENCE_WEIGHT: Weight for Galois loss (default: 0.1)

Philosophy:
    "The algorithm adapts to the user, not the user to the algorithm."
    (Linear Adaptation principle)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Any


@dataclass(frozen=True)
class FeedConfig:
    """
    Configuration for feed ranking algorithm.

    Default weights (sum to 1.0):
    - attention: 0.4 (what the user engages with)
    - principles: 0.3 (alignment with user values)
    - recency: 0.2 (temporal freshness)
    - coherence: 0.1 (epistemic quality via Galois loss)

    These defaults prioritize user engagement patterns while still
    respecting the user's declared values and maintaining some
    attention to recency and quality.
    """

    attention_weight: float = 0.4
    principles_weight: float = 0.3
    recency_weight: float = 0.2
    coherence_weight: float = 0.1

    # Personalization settings
    enable_personalization: bool = True
    min_interactions_for_personalization: int = 5  # Require N interactions before personalizing

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary for API responses."""
        return {
            "attention_weight": self.attention_weight,
            "principles_weight": self.principles_weight,
            "recency_weight": self.recency_weight,
            "coherence_weight": self.coherence_weight,
            "enable_personalization": self.enable_personalization,
            "min_interactions_for_personalization": self.min_interactions_for_personalization,
        }

    @property
    def total_weight(self) -> float:
        """Sum of all weights (should ideally be 1.0)."""
        return (
            self.attention_weight
            + self.principles_weight
            + self.recency_weight
            + self.coherence_weight
        )


def _parse_float_env(key: str, default: float) -> float:
    """Parse a float from environment variable with fallback."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _parse_bool_env(key: str, default: bool) -> bool:
    """Parse a boolean from environment variable with fallback."""
    value = os.environ.get(key)
    if value is None:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def _parse_int_env(key: str, default: int) -> int:
    """Parse an integer from environment variable with fallback."""
    value = os.environ.get(key)
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


@lru_cache(maxsize=1)
def get_feed_config() -> FeedConfig:
    """
    Get the global feed configuration.

    Reads from environment variables with fallback to defaults.
    Result is cached for performance.

    Environment variables:
    - KGENTS_FEED_ATTENTION_WEIGHT: Weight for attention (default: 0.4)
    - KGENTS_FEED_PRINCIPLES_WEIGHT: Weight for principles (default: 0.3)
    - KGENTS_FEED_RECENCY_WEIGHT: Weight for recency (default: 0.2)
    - KGENTS_FEED_COHERENCE_WEIGHT: Weight for coherence (default: 0.1)
    - KGENTS_FEED_ENABLE_PERSONALIZATION: Enable personal feeds (default: true)
    - KGENTS_FEED_MIN_INTERACTIONS: Min interactions for personalization (default: 5)
    """
    return FeedConfig(
        attention_weight=_parse_float_env("KGENTS_FEED_ATTENTION_WEIGHT", 0.4),
        principles_weight=_parse_float_env("KGENTS_FEED_PRINCIPLES_WEIGHT", 0.3),
        recency_weight=_parse_float_env("KGENTS_FEED_RECENCY_WEIGHT", 0.2),
        coherence_weight=_parse_float_env("KGENTS_FEED_COHERENCE_WEIGHT", 0.1),
        enable_personalization=_parse_bool_env("KGENTS_FEED_ENABLE_PERSONALIZATION", True),
        min_interactions_for_personalization=_parse_int_env("KGENTS_FEED_MIN_INTERACTIONS", 5),
    )


def reset_feed_config() -> None:
    """
    Reset the cached feed configuration.

    Call this after changing environment variables to pick up new values.
    Primarily useful for testing.
    """
    get_feed_config.cache_clear()


# Default config for reference (useful for tests and documentation)
DEFAULT_CONFIG = FeedConfig()


__all__ = [
    "FeedConfig",
    "get_feed_config",
    "reset_feed_config",
    "DEFAULT_CONFIG",
]
