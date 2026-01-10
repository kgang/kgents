"""
Feed Core: Primitives for algorithmic K-Block discovery.

This module defines the core types for the Feed system:
- Feed: A stream definition with sources, filters, ranking, and feedback
- FeedSource: Where K-Blocks come from (all, layer, author, tag, custom)
- FeedFilter: How to filter K-Blocks (layer, loss, author, principle, time)
- FeedRanking: Weighted scoring (attention, principles, recency, coherence)
- FeedFeedback: User interaction callbacks for personalization

Philosophy:
    "The feed is a primitive, not a component."
    Like Text, View, Button — Feed is foundational.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Literal, Protocol

from services.k_block.core.kblock import KBlock

# =============================================================================
# Protocols
# =============================================================================


class User(Protocol):
    """User protocol for type hints."""

    id: str
    principles: tuple[str, ...]


# =============================================================================
# Feed Source
# =============================================================================


@dataclass(frozen=True)
class FeedSource:
    """
    Defines where K-Blocks enter a feed.

    Types:
    - 'all': All K-Blocks (cosmos)
    - 'layer': Filter by Zero Seed layer (1-7)
    - 'author': Filter by author ID
    - 'tag': Filter by tag
    - 'custom': Custom predicate function
    """

    type: Literal["all", "layer", "author", "tag", "custom"]
    value: str | int | tuple[int, ...] | Callable[[KBlock], bool] | None = None

    def matches(self, kblock: KBlock) -> bool:
        """Check if a K-Block matches this source."""
        match self.type:
            case "all":
                return True
            case "layer":
                # K-Block stores layer as zero_seed_layer
                layer = getattr(kblock, "zero_seed_layer", None)
                if layer is None:
                    return False
                if isinstance(self.value, int):
                    return bool(layer == self.value)
                elif isinstance(self.value, tuple):
                    return layer in self.value
                return False
            case "author":
                # K-Block doesn't have created_by yet - TODO
                return False
            case "tag":
                # K-Block doesn't have tags yet - TODO
                return False
            case "custom":
                if callable(self.value):
                    return self.value(kblock)
                return False
            case _:
                return False


# =============================================================================
# Feed Filter
# =============================================================================


@dataclass(frozen=True)
class FeedFilter:
    """
    Defines how to filter K-Blocks in a feed.

    Fields:
    - layer: Zero Seed layer (1-7)
    - loss: Galois loss (coherence)
    - author: Created by
    - principle: Referenced in proof
    - time: Created at
    - custom: Custom predicate

    Operators:
    - eq: Equal
    - lt: Less than
    - gt: Greater than
    - between: Between two values
    - contains: Contains (for strings/lists)
    """

    field: Literal["layer", "loss", "author", "principle", "time", "custom"]
    operator: Literal["eq", "lt", "gt", "between", "contains"]
    value: Any

    def matches(self, kblock: KBlock) -> bool:
        """Check if a K-Block passes this filter."""
        match self.field:
            case "layer":
                layer = getattr(kblock, "zero_seed_layer", None)
                if layer is None:
                    return False
                return self._compare(layer, self.value)
            case "loss":
                # K-Block doesn't store Galois loss yet - TODO
                loss = 0.0
                return self._compare(loss, self.value)
            case "author":
                # K-Block doesn't have created_by yet - TODO
                return False
            case "principle":
                # Check if principle is referenced in proof
                proof = getattr(kblock, "toulmin_proof", None)
                if proof and isinstance(proof, dict):
                    principles = proof.get("principles", [])
                    return self._compare(principles, self.value, is_collection=True)
                return False
            case "time":
                return self._compare(kblock.created_at, self.value)
            case "custom":
                if callable(self.value):
                    return bool(self.value(kblock))
                return False
            case _:
                return False

    def _compare(self, field_value: Any, filter_value: Any, is_collection: bool = False) -> bool:
        """Helper to compare values based on operator."""
        match self.operator:
            case "eq":
                return bool(field_value == filter_value)
            case "lt":
                return bool(field_value < filter_value)
            case "gt":
                return bool(field_value > filter_value)
            case "between":
                if isinstance(filter_value, tuple) and len(filter_value) == 2:
                    return bool(filter_value[0] <= field_value <= filter_value[1])
                return False
            case "contains":
                if is_collection:
                    return filter_value in field_value
                elif isinstance(field_value, str):
                    return filter_value in field_value
                return False
            case _:
                return False


# =============================================================================
# Feed Ranking
# =============================================================================


@dataclass(frozen=True)
class FeedRanking:
    """
    Defines how to rank K-Blocks in a feed.

    Four scoring dimensions:
    1. Attention: What has the user engaged with?
    2. Principles: How well does this match user's declared values?
    3. Recency: Newer = higher (temporal bias)
    4. Coherence: Lower Galois loss = higher (epistemic quality)

    Weights:
    - Set to 0.0 to disable a dimension
    - Set to 1.0 for primary ranking
    - Set to negative to invert (e.g., -1.0 for highest loss first)
    - Custom function can override all

    Total score = (attention_weight * attention_score +
                   principles_weight * principles_score +
                   recency_weight * recency_score +
                   coherence_weight * coherence_score)
                  OR custom(kblock, user)
    """

    attention_weight: float = 0.0
    principles_weight: float = 0.0
    recency_weight: float = 1.0  # Default: chronological
    coherence_weight: float = 0.0
    custom: Callable[[KBlock, User], float] | None = None

    def __post_init__(self) -> None:
        """Validate weights."""
        # Allow negative weights (for inversion)
        # No other validation needed


# =============================================================================
# Feed Feedback
# =============================================================================


@dataclass
class FeedFeedback:
    """
    User interaction callbacks for feed personalization.

    The recursive power of feeds: users create feedback systems WITH feeds.

    Callbacks:
    - on_view: Track attention (passive)
    - on_engage: Track interaction (active)
    - on_dismiss: Learn negative preference
    - on_contradict: Surface conflicts for synthesis
    """

    on_view: Callable[[KBlock], None] | None = None
    on_engage: Callable[[KBlock], None] | None = None
    on_dismiss: Callable[[KBlock], None] | None = None
    on_contradict: Callable[[KBlock, KBlock], None] | None = None


# =============================================================================
# Feed
# =============================================================================


@dataclass
class Feed:
    """
    A filtered, ranked stream of K-Blocks.

    The feed IS the primary interface. Not a view of data, but THE interface.

    A feed without filters is the raw cosmos.
    A feed with filters is a perspective.
    Multiple feeds = multiple selves.

    Attributes:
        id: Unique identifier
        name: Display name
        description: What this feed shows
        sources: Where K-Blocks enter
        filters: How K-Blocks are filtered
        ranking: How K-Blocks are ranked
        feedback: User interaction callbacks (optional)
    """

    id: str
    name: str
    description: str = ""
    sources: tuple[FeedSource, ...] = field(default_factory=tuple)
    filters: tuple[FeedFilter, ...] = field(default_factory=tuple)
    ranking: FeedRanking = field(default_factory=FeedRanking)
    feedback: FeedFeedback | None = None

    def matches_source(self, kblock: KBlock) -> bool:
        """Check if K-Block matches any source."""
        if not self.sources:
            return True  # No sources = all K-Blocks
        return any(source.matches(kblock) for source in self.sources)

    def passes_filters(self, kblock: KBlock) -> bool:
        """Check if K-Block passes all filters."""
        if not self.filters:
            return True  # No filters = all K-Blocks pass
        return all(f.matches(kblock) for f in self.filters)

    def should_include(self, kblock: KBlock) -> bool:
        """Check if K-Block should be included in this feed."""
        return self.matches_source(kblock) and self.passes_filters(kblock)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "sources": [
                {
                    "type": s.type,
                    "value": s.value if not callable(s.value) else "<custom>",
                }
                for s in self.sources
            ],
            "filters": [
                {
                    "field": f.field,
                    "operator": f.operator,
                    "value": f.value if not callable(f.value) else "<custom>",
                }
                for f in self.filters
            ],
            "ranking": {
                "attention_weight": self.ranking.attention_weight,
                "principles_weight": self.ranking.principles_weight,
                "recency_weight": self.ranking.recency_weight,
                "coherence_weight": self.ranking.coherence_weight,
                "custom": "<custom>" if self.ranking.custom else None,
            },
        }


__all__ = [
    "Feed",
    "FeedSource",
    "FeedFilter",
    "FeedRanking",
    "FeedFeedback",
    "User",
]
