"""
Feed Ranking: Algorithmic scoring for K-Block discovery.

Four dimensions of ranking:
1. Attention: User engagement patterns
2. Principles: Alignment with user values
3. Recency: Temporal freshness
4. Coherence: Galois loss (epistemic quality)

Philosophy:
    "The algorithm adapts to the user, not the user to the algorithm."
    (Linear Adaptation principle)
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Protocol

from services.k_block.core.kblock import KBlock

# =============================================================================
# Protocols
# =============================================================================


class User(Protocol):
    """User protocol for type hints."""

    id: str
    principles: tuple[str, ...]


class AttentionStore(Protocol):
    """Protocol for attention tracking storage."""

    async def get_attention_score(self, user_id: str, kblock_id: str) -> float:
        """Get attention score for a K-Block (0.0 to 1.0)."""
        ...


# =============================================================================
# Score Components
# =============================================================================


@dataclass(frozen=True)
class AttentionScore:
    """
    Attention-based score: what has the user engaged with?

    Score components:
    - views: Passive attention (low weight)
    - engagements: Active interaction (high weight)
    - dismissals: Negative signal (penalty)

    Score range: 0.0 (never seen) to 1.0 (highly engaged)
    """

    views: int = 0
    engagements: int = 0
    dismissals: int = 0

    def compute(self) -> float:
        """
        Compute attention score.

        Formula: (engagements * 2 + views * 0.5 - dismissals) / (total + 1)
        Normalized to [0, 1] range.
        """
        total = self.views + self.engagements + self.dismissals
        if total == 0:
            return 0.0

        raw_score = (self.engagements * 2.0 + self.views * 0.5 - self.dismissals) / (total + 1)
        # Normalize to [0, 1]
        return max(0.0, min(1.0, raw_score / 2.0))


@dataclass(frozen=True)
class PrinciplesScore:
    """
    Principles alignment score: how well does K-Block match user values?

    Checks if K-Block proof references principles declared by user.

    Score range: 0.0 (no match) to 1.0 (perfect alignment)
    """

    user_principles: tuple[str, ...]
    kblock_principles: tuple[str, ...]

    def compute(self) -> float:
        """
        Compute principles alignment score.

        Formula: (matched principles) / (user principles)
        If user has no principles, return 0.5 (neutral).
        """
        if not self.user_principles:
            return 0.5  # Neutral when user hasn't declared principles

        if not self.kblock_principles:
            return 0.0  # K-Block doesn't reference any principles

        matched = sum(
            1 for p in self.kblock_principles if p in self.user_principles
        )
        return matched / len(self.user_principles)


@dataclass(frozen=True)
class RecencyScore:
    """
    Recency score: newer K-Blocks rank higher.

    Uses exponential decay with configurable half-life.

    Score range: 0.0 (very old) to 1.0 (just created)
    """

    created_at: datetime
    now: datetime | None = None
    half_life_days: float = 7.0  # Half-life: 7 days default

    def compute(self) -> float:
        """
        Compute recency score with exponential decay.

        Formula: 2^(-age_days / half_life_days)
        """
        now = self.now or datetime.now(timezone.utc)
        age_seconds = (now - self.created_at).total_seconds()
        age_days = age_seconds / 86400.0  # Convert to days

        # Exponential decay: score halves every half_life_days
        import math
        score = math.pow(2.0, -age_days / self.half_life_days)
        return max(0.0, min(1.0, score))


@dataclass(frozen=True)
class CoherenceScore:
    """
    Coherence score: lower Galois loss = higher epistemic quality.

    Converts Galois loss to a score (inverted: low loss = high score).

    Score range: 0.0 (incoherent, loss > 1.0) to 1.0 (perfect, loss = 0.0)
    """

    galois_loss: float

    def compute(self) -> float:
        """
        Compute coherence score.

        Formula: 1.0 - min(galois_loss, 1.0)
        Loss > 1.0 is clamped to give score of 0.0.
        """
        return 1.0 - min(self.galois_loss, 1.0)


# =============================================================================
# Feed Scoring
# =============================================================================


async def compute_feed_score(
    kblock: KBlock,
    user: User,
    attention_weight: float = 0.0,
    principles_weight: float = 0.0,
    recency_weight: float = 1.0,
    coherence_weight: float = 0.0,
    attention_store: AttentionStore | None = None,
) -> float:
    """
    Compute weighted feed score for a K-Block.

    Args:
        kblock: The K-Block to score
        user: The user viewing the feed
        attention_weight: Weight for attention score
        principles_weight: Weight for principles alignment
        recency_weight: Weight for recency
        coherence_weight: Weight for coherence (Galois loss)
        attention_store: Optional attention tracking store

    Returns:
        Weighted score (can be negative if weights are negative)
    """
    score = 0.0

    # Attention component
    if attention_weight != 0.0 and attention_store:
        attention_score = await attention_store.get_attention_score(user.id, kblock.id)
        score += attention_weight * attention_score

    # Principles component
    if principles_weight != 0.0:
        kblock_principles = ()
        proof = getattr(kblock, "toulmin_proof", None)
        if proof and isinstance(proof, dict):
            kblock_principles = tuple(proof.get("principles", []))

        principles_score = PrinciplesScore(
            user_principles=user.principles,
            kblock_principles=kblock_principles,
        ).compute()
        score += principles_weight * principles_score

    # Recency component
    if recency_weight != 0.0:
        recency_score = RecencyScore(created_at=kblock.created_at).compute()
        score += recency_weight * recency_score

    # Coherence component
    if coherence_weight != 0.0:
        # K-Block doesn't store Galois loss yet - TODO
        # For now, assume perfect coherence (loss = 0.0)
        galois_loss = 0.0
        coherence_score = CoherenceScore(galois_loss=galois_loss).compute()
        score += coherence_weight * coherence_score

    return score


async def rank_kblocks(
    kblocks: list[KBlock],
    user: User,
    attention_weight: float = 0.0,
    principles_weight: float = 0.0,
    recency_weight: float = 1.0,
    coherence_weight: float = 0.0,
    attention_store: AttentionStore | None = None,
) -> list[tuple[KBlock, float]]:
    """
    Rank K-Blocks by weighted score.

    Args:
        kblocks: List of K-Blocks to rank
        user: The user viewing the feed
        attention_weight: Weight for attention score
        principles_weight: Weight for principles alignment
        recency_weight: Weight for recency
        coherence_weight: Weight for coherence (Galois loss)
        attention_store: Optional attention tracking store

    Returns:
        List of (KBlock, score) tuples, sorted by score descending
    """
    # Compute scores for all K-Blocks
    scored_kblocks = []
    for kblock in kblocks:
        score = await compute_feed_score(
            kblock=kblock,
            user=user,
            attention_weight=attention_weight,
            principles_weight=principles_weight,
            recency_weight=recency_weight,
            coherence_weight=coherence_weight,
            attention_store=attention_store,
        )
        scored_kblocks.append((kblock, score))

    # Sort by score descending (highest first)
    scored_kblocks.sort(key=lambda x: x[1], reverse=True)

    return scored_kblocks


__all__ = [
    "AttentionScore",
    "PrinciplesScore",
    "RecencyScore",
    "CoherenceScore",
    "compute_feed_score",
    "rank_kblocks",
    "User",
    "AttentionStore",
]
