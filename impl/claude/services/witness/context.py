"""
Context Budget System: Budget-Aware Crystal Context Queries.

Agents need context but have limited budgets. Crystals solve this.

The Core Insight:
    "Executive summaries instead of raw marks."

    When a subagent starts, it doesn't need 600 marks from the past month.
    It needs the most relevant crystals that fit within its context budget.
    This module provides budget-aware retrieval with recency/relevance scoring.

The Algorithm:
1. Start with highest-level crystals (most compressed)
2. Score by recency × relevance
3. Fill budget greedily by score
4. Return ordered list with cumulative token counts

Philosophy:
    "The budget IS the constraint that forces compression."

AGENTESE: self.witness.context
CLI: kg witness context --budget 2000 --query "topic" --json

See: spec/protocols/witness-crystallization.md
See: docs/skills/witness-for-agents.md
"""

from __future__ import annotations

import logging
import math
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from typing import Any, Callable

from .crystal import Crystal, CrystalLevel
from .crystal_store import CrystalStore, get_crystal_store

logger = logging.getLogger("kgents.witness.context")


# =============================================================================
# Context Result
# =============================================================================


@dataclass(frozen=True)
class ContextItem:
    """
    A crystal with budget metadata for context retrieval.

    Includes score and cumulative token tracking for budget decisions.
    """

    crystal: Crystal
    score: float  # Combined recency + relevance score
    recency_score: float  # How recent (0.0 to 1.0)
    relevance_score: float  # How relevant to query (0.0 to 1.0)
    tokens: int  # This crystal's token estimate
    cumulative_tokens: int  # Running total including this crystal


@dataclass
class ContextResult:
    """
    Result of a budget-aware context query.

    Contains the selected crystals and query metadata.
    """

    items: list[ContextItem]
    total_tokens: int
    budget: int
    budget_remaining: int
    query: str | None
    recency_weight: float

    @property
    def crystals(self) -> list[Crystal]:
        """Get just the crystals (for simple use cases)."""
        return [item.crystal for item in self.items]

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON output."""
        return {
            "items": [
                {
                    "id": str(item.crystal.id),
                    "level": item.crystal.level.name,
                    "insight": item.crystal.insight,
                    "significance": item.crystal.significance,
                    "topics": list(item.crystal.topics),
                    "score": round(item.score, 3),
                    "recency_score": round(item.recency_score, 3),
                    "relevance_score": round(item.relevance_score, 3),
                    "tokens": item.tokens,
                    "cumulative_tokens": item.cumulative_tokens,
                    "crystallized_at": item.crystal.crystallized_at.isoformat(),
                }
                for item in self.items
            ],
            "total_tokens": self.total_tokens,
            "budget": self.budget,
            "budget_remaining": self.budget_remaining,
            "query": self.query,
            "recency_weight": self.recency_weight,
        }


# =============================================================================
# Scoring Functions
# =============================================================================


def compute_recency_score(
    crystallized_at: datetime,
    now: datetime | None = None,
    half_life_days: float = 7.0,
) -> float:
    """
    Compute recency score using exponential decay.

    Returns 1.0 for crystals created now, decaying to 0.5 after half_life_days.

    Args:
        crystallized_at: When the crystal was created
        now: Current time (defaults to UTC now)
        half_life_days: Days until score reaches 0.5 (default 7)

    Returns:
        Float in [0, 1] where 1.0 is most recent
    """
    if now is None:
        now = datetime.now(UTC)

    # Ensure timezone awareness
    if crystallized_at.tzinfo is None:
        crystallized_at = crystallized_at.replace(tzinfo=UTC)
    if now.tzinfo is None:
        now = now.replace(tzinfo=UTC)

    age = now - crystallized_at
    age_days = max(0, age.total_seconds() / 86400)

    # Exponential decay: score = 2^(-age/half_life)
    decay = math.pow(2, -age_days / half_life_days)
    return max(0.0, min(1.0, decay))


def compute_relevance_score(
    crystal: Crystal,
    query: str | None,
) -> float:
    """
    Compute relevance score based on keyword matching.

    For now, uses simple keyword matching. Future: embedding similarity via Brain.

    Args:
        crystal: The crystal to score
        query: Optional query string for relevance

    Returns:
        Float in [0, 1] where 1.0 is most relevant
    """
    if not query:
        # No query = all equally relevant
        return 0.5

    query_lower = query.lower()
    query_terms = query_lower.split()

    # Fields to search
    searchable = [
        crystal.insight.lower(),
        crystal.significance.lower(),
        " ".join(crystal.principles).lower(),
        " ".join(crystal.topics).lower(),
    ]
    full_text = " ".join(searchable)

    # Count matching terms
    matches = sum(1 for term in query_terms if term in full_text)

    if not query_terms:
        return 0.5

    # Normalize to [0, 1]
    match_ratio = matches / len(query_terms)

    # Boost for exact phrase match
    if query_lower in full_text:
        match_ratio = min(1.0, match_ratio + 0.3)

    return match_ratio


def compute_combined_score(
    recency_score: float,
    relevance_score: float,
    recency_weight: float = 0.7,
) -> float:
    """
    Combine recency and relevance scores.

    Args:
        recency_score: Score from compute_recency_score()
        relevance_score: Score from compute_relevance_score()
        recency_weight: Weight for recency (relevance gets 1 - recency_weight)

    Returns:
        Combined score in [0, 1]
    """
    return recency_weight * recency_score + (1 - recency_weight) * relevance_score


# =============================================================================
# Budget-Aware Context Retrieval
# =============================================================================


async def get_context(
    budget_tokens: int = 2000,
    recency_weight: float = 0.7,
    relevance_query: str | None = None,
    store: CrystalStore | None = None,
    now: datetime | None = None,
) -> ContextResult:
    """
    Get the best crystals that fit within token budget.

    Strategy:
    1. Score all crystals by recency × relevance
    2. Sort by score (highest first)
    3. Greedily fill budget
    4. Return ordered list with metadata

    This gives agents "executive summaries" instead of raw marks.

    Args:
        budget_tokens: Maximum tokens to return (default 2000)
        recency_weight: Weight for recency vs relevance (default 0.7)
        relevance_query: Optional query string for relevance scoring
        store: Crystal store to query (defaults to global store)
        now: Current time for recency calculation

    Returns:
        ContextResult with crystals that fit within budget

    Example:
        >>> result = await get_context(budget_tokens=1500, relevance_query="extinction")
        >>> for item in result.items:
        ...     print(f"{item.crystal.insight[:50]} ({item.tokens} tokens)")
    """
    if store is None:
        store = get_crystal_store()

    if now is None:
        now = datetime.now(UTC)

    # Score all crystals
    scored: list[tuple[Crystal, float, float, float]] = []

    for crystal in store.all():
        recency = compute_recency_score(crystal.crystallized_at, now)
        relevance = compute_relevance_score(crystal, relevance_query)
        combined = compute_combined_score(recency, relevance, recency_weight)
        scored.append((crystal, combined, recency, relevance))

    # Sort by score (highest first)
    scored.sort(key=lambda x: x[1], reverse=True)

    # Greedily fill budget
    items: list[ContextItem] = []
    cumulative = 0

    for crystal, score, recency, relevance in scored:
        tokens = crystal.token_estimate or 50  # Default estimate if missing

        if cumulative + tokens > budget_tokens:
            # Would exceed budget - skip this crystal
            # But keep looking for smaller ones that might fit
            continue

        cumulative += tokens
        items.append(
            ContextItem(
                crystal=crystal,
                score=score,
                recency_score=recency,
                relevance_score=relevance,
                tokens=tokens,
                cumulative_tokens=cumulative,
            )
        )

    return ContextResult(
        items=items,
        total_tokens=cumulative,
        budget=budget_tokens,
        budget_remaining=budget_tokens - cumulative,
        query=relevance_query,
        recency_weight=recency_weight,
    )


def get_context_sync(
    budget_tokens: int = 2000,
    recency_weight: float = 0.7,
    relevance_query: str | None = None,
    store: CrystalStore | None = None,
    now: datetime | None = None,
) -> ContextResult:
    """
    Synchronous version of get_context for CLI use.

    Same algorithm as get_context, but doesn't require async.
    """
    if store is None:
        store = get_crystal_store()

    if now is None:
        now = datetime.now(UTC)

    # Score all crystals
    scored: list[tuple[Crystal, float, float, float]] = []

    for crystal in store.all():
        recency = compute_recency_score(crystal.crystallized_at, now)
        relevance = compute_relevance_score(crystal, relevance_query)
        combined = compute_combined_score(recency, relevance, recency_weight)
        scored.append((crystal, combined, recency, relevance))

    # Sort by score (highest first)
    scored.sort(key=lambda x: x[1], reverse=True)

    # Greedily fill budget
    items: list[ContextItem] = []
    cumulative = 0

    for crystal, score, recency, relevance in scored:
        tokens = crystal.token_estimate or 50

        if cumulative + tokens > budget_tokens:
            continue

        cumulative += tokens
        items.append(
            ContextItem(
                crystal=crystal,
                score=score,
                recency_score=recency,
                relevance_score=relevance,
                tokens=tokens,
                cumulative_tokens=cumulative,
            )
        )

    return ContextResult(
        items=items,
        total_tokens=cumulative,
        budget=budget_tokens,
        budget_remaining=budget_tokens - cumulative,
        query=relevance_query,
        recency_weight=recency_weight,
    )


# =============================================================================
# Formatting for Context Injection
# =============================================================================


def format_context_for_prompt(result: ContextResult) -> str:
    """
    Format context result for injection into an LLM prompt.

    Produces a compact representation suitable for agent context windows.

    Args:
        result: The context query result

    Returns:
        Formatted string for prompt injection
    """
    if not result.items:
        return "[No relevant context found]"

    lines = ["[CONTEXT - Recent Witness Crystals]"]

    for item in result.items:
        crystal = item.crystal
        level_badge = f"[L{crystal.level.value}]"

        # Format time
        dt = crystal.crystallized_at
        if dt.date() == datetime.now(UTC).date():
            time_str = dt.strftime("%H:%M")
        else:
            time_str = dt.strftime("%m/%d %H:%M")

        # Build line
        line = f"{level_badge} {time_str}: {crystal.insight}"
        if crystal.significance:
            line += f" | {crystal.significance[:50]}"

        lines.append(line)

    lines.append(f"[{result.total_tokens}/{result.budget} tokens]")

    return "\n".join(lines)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Types
    "ContextItem",
    "ContextResult",
    # Scoring
    "compute_recency_score",
    "compute_relevance_score",
    "compute_combined_score",
    # Retrieval
    "get_context",
    "get_context_sync",
    # Formatting
    "format_context_for_prompt",
]
