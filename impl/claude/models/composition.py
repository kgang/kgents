"""
Composition Model: Database persistence for kg compose operations.

Tables for storing named compositions and their execution history.

AGENTESE: concept.compose.history.*
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, TimestampMixin


class CompositionRow(TimestampMixin, Base):
    """
    A stored composition in the database.

    Compositions are named sequences of kg commands that can be:
    - Saved for reuse
    - Tracked with execution history
    - Shared across sessions

    The dual-track pattern:
    - This table: Fast queries by name, recency
    - Trace marks: Full execution history via witness system
    """

    __tablename__ = "compositions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    author: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Composition definition
    commands: Mapped[list[str]] = mapped_column(JSON, default=list)
    dependencies: Mapped[dict[str, list[int]]] = mapped_column(JSON, default=dict)

    # Latest execution state
    last_status: Mapped[str | None] = mapped_column(String(32), nullable=True)
    last_trace_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_executed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_duration_ms: Mapped[float | None] = mapped_column(Float, nullable=True)
    last_success_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    last_failure_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Aggregate stats
    execution_count: Mapped[int] = mapped_column(Integer, default=0)

    def __repr__(self) -> str:
        return f"CompositionRow(id={self.id!r}, name={self.name!r}, commands={len(self.commands)})"
