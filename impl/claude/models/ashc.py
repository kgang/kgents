"""
ASHC Crown Jewel: Proof-Generating Agentic Self-Hosting Compiler.

Tables for verified lemmas with stigmergic reinforcement.
The lemma database is a knowledge base that grows with each successful proof.

Stigmergic Design (§13):
    pheromone = usage_count (more-used lemmas rank higher)
    decay = age-based relevance (verified_at for freshness)
    reinforcement = increment_usage() on successful hint
    emergent path = tactic selection evolves with corpus

AGENTESE: concept.ashc.lemma.*
"""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    Index,
    Integer,
    JSON,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class VerifiedLemmaModel(TimestampMixin, Base):
    """
    A proven fact in the lemma database.

    Once verified by a proof checker, lemmas are immutable facts that can be:
    - Retrieved as hints for future proof searches
    - Composed with other lemmas
    - Reinforced through usage (stigmergic pheromone)

    The dual-track pattern mirrors Brain:
    - This table: Fast queries by statement keywords, usage ranking
    - Stigmergic reinforcement: usage_count increases on successful hint

    Laws:
        1. Monotonicity: lemmas(t+1) ⊇ lemmas(t)
        2. Soundness: verified(lemma) → property_holds(lemma.statement)
        3. Compositionality: compose(lemma_a, lemma_b) → valid_proof

    Teaching:
        gotcha: usage_count is the pheromone. Higher count = stronger trace.
                Increment on hint retrieval, not on proof verification.
                (Evidence: test_lemma_db.py::test_stigmergic_reinforcement)

        gotcha: dependencies is JSON array of LemmaIds. Use for composition
                tracking but don't enforce referential integrity (lemmas may
                come from external sources).
                (Evidence: test_persistence.py::test_store_with_dependencies)
    """

    __tablename__ = "ashc_verified_lemmas"

    # Primary key matches LemmaId from contracts.py
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # The proven statement (formal syntax)
    statement: Mapped[str] = mapped_column(Text, nullable=False)

    # The complete proof source
    proof: Mapped[str] = mapped_column(Text, nullable=False)

    # Which checker verified this ("dafny", "lean4", "verus")
    checker: Mapped[str] = mapped_column(String(32), nullable=False)

    # Origin obligation that spawned this lemma
    obligation_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Lemmas this builds on (for composition tracking)
    # JSON works with both Postgres and SQLite
    dependencies: Mapped[list[str]] = mapped_column(
        JSON,
        default=list,
        nullable=False,
    )

    # Stigmergic pheromone: how often this lemma has been used as a hint
    usage_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    # When the proof was verified (distinct from created_at)
    verified_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(UTC),
        nullable=False,
    )

    __table_args__ = (  # type: ignore[assignment]
        # Usage ranking for stigmergic retrieval
        Index("idx_ashc_lemmas_usage", "usage_count"),
        # Recency for temporal queries
        Index("idx_ashc_lemmas_verified", "verified_at"),
        # Note: Full-text search index created via Alembic migration
        # for Postgres only (gin_trgm_ops not portable to SQLite)
    )

    def increment_usage(self) -> None:
        """
        Increment usage count (stigmergic reinforcement).

        Called when this lemma is used as a hint for a successful proof.
        The pheromone grows stronger with each use.
        """
        self.usage_count += 1

    def to_dict(self) -> dict[str, object]:
        """Serialize to dictionary for API/JSON."""
        return {
            "id": self.id,
            "statement": self.statement,
            "proof": self.proof,
            "checker": self.checker,
            "obligation_id": self.obligation_id,
            "dependencies": self.dependencies,
            "usage_count": self.usage_count,
            "verified_at": self.verified_at.isoformat() if self.verified_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


__all__ = ["VerifiedLemmaModel"]
