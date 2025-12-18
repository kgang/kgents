"""
Gestalt Crown Jewel: Living Garden Where Code Breathes.

Tables for the Gestalt's code topology visualization.
Tracks code blocks, their relationships, and visualization state.

AGENTESE: self.data.table.topology.*, self.data.table.codeblock.*
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, TimestampMixin

if TYPE_CHECKING:
    from typing import Optional


class Topology(TimestampMixin, Base):
    """
    A code topology snapshot.

    Topologies represent:
    - A view of code structure at a point in time
    - Grouped code blocks with spatial layout
    - Breathing/animation state
    """

    __tablename__ = "gestalt_topologies"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Source information
    repo_path: Mapped[str | None] = mapped_column(String(512), nullable=True)
    git_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)  # branch/commit

    # Layout state (JSON for flexibility)
    layout: Mapped[dict] = mapped_column(JSON, default=dict)
    viewport: Mapped[dict] = mapped_column(JSON, default=dict)  # zoom, pan, etc.

    # Analysis metadata
    block_count: Mapped[int] = mapped_column(Integer, default=0)
    link_count: Mapped[int] = mapped_column(Integer, default=0)
    complexity_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Code blocks in this topology
    blocks: Mapped[list["CodeBlock"]] = relationship(
        "CodeBlock",
        back_populates="topology",
        cascade="all, delete-orphan",
    )

    # Links between blocks
    links: Mapped[list["CodeLink"]] = relationship(
        "CodeLink",
        back_populates="topology",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_gestalt_topologies_name", "name"),
        Index("idx_gestalt_topologies_repo", "repo_path"),
    )


class CodeBlock(TimestampMixin, Base):
    """
    A code block in the topology.

    Represents:
    - A function, class, module, or file
    - Position in the visualization
    - Health/breathing state
    """

    __tablename__ = "gestalt_code_blocks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    topology_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("gestalt_topologies.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Code identity
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    block_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "function", "class", "module", "file"
    file_path: Mapped[str] = mapped_column(String(512), nullable=False)
    line_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    line_end: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Visualization position
    x: Mapped[float] = mapped_column(Float, default=0.0)
    y: Mapped[float] = mapped_column(Float, default=0.0)
    z: Mapped[float] = mapped_column(Float, default=0.0)

    # Health metrics (for breathing intensity)
    test_coverage: Mapped[float | None] = mapped_column(Float, nullable=True)
    complexity: Mapped[float | None] = mapped_column(Float, nullable=True)
    churn_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Content hash for change detection
    content_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    topology: Mapped["Topology"] = relationship("Topology", back_populates="blocks")

    __table_args__ = (
        Index("idx_gestalt_blocks_topology", "topology_id"),
        Index("idx_gestalt_blocks_file", "file_path"),
        Index("idx_gestalt_blocks_type", "block_type"),
    )


class CodeLink(TimestampMixin, Base):
    """
    A link between code blocks.

    Links represent:
    - Import relationships
    - Call relationships
    - Inheritance
    - Data flow
    """

    __tablename__ = "gestalt_code_links"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    topology_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("gestalt_topologies.id", ondelete="CASCADE"),
        nullable=False,
    )
    source_block_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("gestalt_code_blocks.id", ondelete="CASCADE"),
        nullable=False,
    )
    target_block_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("gestalt_code_blocks.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Link type
    link_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "import", "call", "inherit", "data_flow"
    strength: Mapped[float] = mapped_column(Float, default=1.0)

    # Optional metadata
    call_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    topology: Mapped["Topology"] = relationship("Topology", back_populates="links")

    __table_args__ = (
        Index("idx_gestalt_links_topology", "topology_id"),
        Index("idx_gestalt_links_source", "source_block_id"),
        Index("idx_gestalt_links_target", "target_block_id"),
    )


class TopologySnapshot(TimestampMixin, Base):
    """
    Historical snapshot of topology state.

    Enables:
    - Viewing code evolution over time
    - Comparing complexity before/after refactors
    - Tracking health trends
    """

    __tablename__ = "gestalt_topology_snapshots"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    topology_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("gestalt_topologies.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Snapshot metadata
    git_ref: Mapped[str | None] = mapped_column(String(128), nullable=True)
    block_count: Mapped[int] = mapped_column(Integer, default=0)
    link_count: Mapped[int] = mapped_column(Integer, default=0)
    complexity_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Full state (compressed JSON)
    state_json: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("idx_gestalt_snapshots_topology", "topology_id"),
        Index("idx_gestalt_snapshots_created", "created_at"),
    )
