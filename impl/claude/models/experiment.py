"""
Experiment Model: Database persistence for kg experiment operations.

Tables for storing experiments and their trial history.

AGENTESE: concept.experiment.history.*
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class ExperimentModel(TimestampMixin, Base):
    """
    A stored experiment in the database.

    Experiments are evidence-gathering sessions that can be:
    - Tracked with trial history
    - Analyzed for patterns
    - Resumed across sessions

    The dual-track pattern:
    - This table: Fast queries by type, recency
    - Witness marks: Full trial history via witness system
    """

    __tablename__ = "experiments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)

    # Experiment configuration (JSON serialized)
    config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Trial data (JSON array of trial dicts)
    trials: Mapped[list] = mapped_column(JSON, default=list)

    # Evidence summary (JSON serialized)
    evidence: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Witness mark references
    mark_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    # Timing
    started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Summary stats for fast queries
    trials_total: Mapped[int] = mapped_column(Integer, default=0)
    trials_success: Mapped[int] = mapped_column(Integer, default=0)
    success_rate: Mapped[float] = mapped_column(Float, default=0.0)

    def __repr__(self) -> str:
        return f"ExperimentModel(id={self.id!r}, type={self.type!r}, status={self.status!r})"
