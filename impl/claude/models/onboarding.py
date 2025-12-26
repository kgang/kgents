"""
Onboarding Session Persistence.

Stores onboarding sessions for the Genesis FTUE (First Time User Experience).
Persists sessions across server restarts.

The Pattern:
- Dual-track: SQL for session lifecycle queries
- Postgres/SQLite compatibility with JSONB/JSON variant

FTUE Axiom Tracking (from spec/protocols/ftue-axioms.md):
- F1: Identity Seed (first K-Block) - tracked as first_kblock_id
- F2: Connection Pattern (first edge) - tracked as f2_edge_id
- F3: Judgment Experience (first judgment) - tracked as f3_judgment_id
- FG: Growth Witness (witnessed emergence) - tracked as fg_witness_id

AGENTESE: world.onboarding.*
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import JSON

# Use JSON with JSONB variant for PostgreSQL (enables GIN index).
# Falls back to plain JSON for SQLite.
JSONBCompat = JSON().with_variant(JSONB(), "postgresql")

from .base import Base, TimestampMixin


class OnboardingSession(TimestampMixin, Base):
    """
    Onboarding session for Genesis FTUE flow.

    Tracks user progress through first-time onboarding via FTUE axioms:

    FTUE Axioms (from spec/protocols/ftue-axioms.md):
    - F1: Identity Seed - User's first K-Block establishes "I exist in this system"
    - F2: Connection Pattern - User's first edge establishes "Things I create can relate"
    - F3: Judgment Experience - User's first judgment establishes "I can shape this system"
    - FG: Growth Witness - User witnesses something grow from their seeds

    Sessions are automatically cleaned up after 24 hours of inactivity.

    Philosophy:
        "The act of declaring, capturing, and auditing your decisions
         is itself a radical act of self-transformation."

    See: spec/protocols/ftue-axioms.md
    """

    __tablename__ = "onboarding_sessions"

    # Primary key
    id: Mapped[str] = mapped_column(String(64), primary_key=True)

    # User context (optional - for multi-user future)
    user_id: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)

    # Progress tracking
    current_step: Mapped[str] = mapped_column(
        String(32), default="started", nullable=False
    )  # started, f1_complete, f2_complete, f3_complete, fg_complete, completed
    completed: Mapped[bool] = mapped_column(default=False, nullable=False)

    # Completion timestamp (null until completed)
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ==========================================================================
    # FTUE Axiom Tracking
    # ==========================================================================

    # F1: Identity Seed (first K-Block)
    # Tracks: first_kblock_id (existing field, renamed conceptually to f1)
    first_kblock_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    f1_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # F2: Connection Pattern (first edge)
    f2_edge_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    f2_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # F3: Judgment Experience (first judgment)
    f3_judgment_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    f3_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # FG: Growth Witness (witnessed emergence)
    fg_witness_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    fg_completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # The user's first declaration text (preserved for history)
    first_declaration: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ==========================================================================
    # Helper Properties
    # ==========================================================================

    @property
    def f1_complete(self) -> bool:
        """Check if F1 (Identity Seed) axiom is complete."""
        return self.first_kblock_id is not None

    @property
    def f2_complete(self) -> bool:
        """Check if F2 (Connection Pattern) axiom is complete."""
        return self.f2_edge_id is not None

    @property
    def f3_complete(self) -> bool:
        """Check if F3 (Judgment Experience) axiom is complete."""
        return self.f3_judgment_id is not None

    @property
    def fg_complete(self) -> bool:
        """Check if FG (Growth Witness) axiom is complete."""
        return self.fg_witness_id is not None

    @property
    def all_axioms_complete(self) -> bool:
        """Check if all FTUE axioms are complete."""
        return self.f1_complete and self.f2_complete and self.f3_complete and self.fg_complete

    def __repr__(self) -> str:
        axioms = f"F1={self.f1_complete}, F2={self.f2_complete}, F3={self.f3_complete}, FG={self.fg_complete}"
        return f"<OnboardingSession(id={self.id!r}, step={self.current_step!r}, {axioms})>"


__all__ = ["OnboardingSession"]
