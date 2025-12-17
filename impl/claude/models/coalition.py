"""
Coalition Crown Jewel: Workshop Where Agents Collaborate Visibly.

Tables for Coalition formation, membership, and proposals.
Enables dynamic multi-agent collaboration with transparent process.

AGENTESE: self.data.table.coalition.*, self.data.table.proposal.*
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
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base, CausalMixin, TimestampMixin

if TYPE_CHECKING:
    from typing import Optional


class Coalition(TimestampMixin, Base):
    """
    A coalition of agents working together.

    Coalitions:
    - Form around a shared goal/task
    - Have visible membership and roles
    - Produce collaborative outputs
    - Dissolve when goal is achieved
    """

    __tablename__ = "coalition_coalitions"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(256), nullable=False)
    goal: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # State
    status: Mapped[str] = mapped_column(
        String(32), default="forming"
    )  # "forming", "active", "complete", "dissolved"
    formed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    dissolved_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Configuration
    min_members: Mapped[int] = mapped_column(Integer, default=2)
    max_members: Mapped[int | None] = mapped_column(Integer, nullable=True)
    config: Mapped[dict] = mapped_column(JSON, default=dict)

    # Metrics
    proposal_count: Mapped[int] = mapped_column(Integer, default=0)
    consensus_threshold: Mapped[float] = mapped_column(Float, default=0.66)

    # Relationships
    members: Mapped[list["CoalitionMember"]] = relationship(
        "CoalitionMember",
        back_populates="coalition",
        cascade="all, delete-orphan",
    )
    proposals: Mapped[list["CoalitionProposal"]] = relationship(
        "CoalitionProposal",
        back_populates="coalition",
        cascade="all, delete-orphan",
    )
    outputs: Mapped[list["CoalitionOutput"]] = relationship(
        "CoalitionOutput",
        back_populates="coalition",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_coalition_status", "status"),
        Index("idx_coalition_formed", "formed_at"),
    )


class CoalitionMember(TimestampMixin, Base):
    """
    A member of a coalition.

    Members have:
    - Role in the coalition
    - Voting power
    - Contribution history
    """

    __tablename__ = "coalition_members"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    coalition_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("coalition_coalitions.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Agent identity (link to Town citizen or external)
    agent_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    agent_name: Mapped[str] = mapped_column(String(128), nullable=False)
    agent_type: Mapped[str] = mapped_column(
        String(32), default="citizen"
    )  # "citizen", "external", "human"

    # Role and permissions
    role: Mapped[str] = mapped_column(
        String(32), default="member"
    )  # "leader", "member", "observer"
    voting_power: Mapped[float] = mapped_column(Float, default=1.0)
    can_propose: Mapped[bool] = mapped_column(Boolean, default=True)
    can_vote: Mapped[bool] = mapped_column(Boolean, default=True)

    # State
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    joined_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())
    left_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    contribution_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationship
    coalition: Mapped["Coalition"] = relationship("Coalition", back_populates="members")
    votes: Mapped[list["ProposalVote"]] = relationship(
        "ProposalVote",
        back_populates="member",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_coalition_member_agent", "agent_id"),
        Index("idx_coalition_member_coalition", "coalition_id"),
        Index("idx_coalition_member_role", "role"),
    )


class CoalitionProposal(TimestampMixin, CausalMixin, Base):
    """
    A proposal within a coalition.

    Proposals:
    - Are submitted by members
    - Go through voting
    - Result in coalition outputs
    """

    __tablename__ = "coalition_proposals"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    coalition_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("coalition_coalitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    proposer_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("coalition_members.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Content
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    proposal_type: Mapped[str] = mapped_column(
        String(32), default="action"
    )  # "action", "decision", "resource", "membership"

    # State
    status: Mapped[str] = mapped_column(
        String(32), default="draft"
    )  # "draft", "voting", "approved", "rejected", "implemented"
    voting_started_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    voting_ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Voting results
    votes_for: Mapped[int] = mapped_column(Integer, default=0)
    votes_against: Mapped[int] = mapped_column(Integer, default=0)
    votes_abstain: Mapped[int] = mapped_column(Integer, default=0)
    approval_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # D-gent link for full discussion
    datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationships
    coalition: Mapped["Coalition"] = relationship("Coalition", back_populates="proposals")
    votes: Mapped[list["ProposalVote"]] = relationship(
        "ProposalVote",
        back_populates="proposal",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        Index("idx_coalition_proposal_coalition", "coalition_id"),
        Index("idx_coalition_proposal_status", "status"),
        Index("idx_coalition_proposal_type", "proposal_type"),
    )


class ProposalVote(TimestampMixin, Base):
    """
    A vote on a coalition proposal.

    Votes are transparent and attributable.
    """

    __tablename__ = "coalition_proposal_votes"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    proposal_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("coalition_proposals.id", ondelete="CASCADE"),
        nullable=False,
    )
    member_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("coalition_members.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Vote
    vote: Mapped[str] = mapped_column(
        String(16), nullable=False
    )  # "for", "against", "abstain"
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    proposal: Mapped["CoalitionProposal"] = relationship(
        "CoalitionProposal", back_populates="votes"
    )
    member: Mapped["CoalitionMember"] = relationship(
        "CoalitionMember", back_populates="votes"
    )

    __table_args__ = (
        Index("idx_proposal_vote_proposal", "proposal_id"),
        Index("idx_proposal_vote_member", "member_id"),
    )


class CoalitionOutput(TimestampMixin, CausalMixin, Base):
    """
    An output produced by a coalition.

    Outputs are the tangible results of coalition work.
    """

    __tablename__ = "coalition_outputs"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    coalition_id: Mapped[str] = mapped_column(
        String(64),
        ForeignKey("coalition_coalitions.id", ondelete="CASCADE"),
        nullable=False,
    )
    proposal_id: Mapped[str | None] = mapped_column(
        String(64),
        ForeignKey("coalition_proposals.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Output content
    output_type: Mapped[str] = mapped_column(
        String(32), nullable=False
    )  # "decision", "artifact", "action", "report"
    title: Mapped[str] = mapped_column(String(256), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)

    # Attribution
    contributor_ids: Mapped[list[str]] = mapped_column(JSON, default=list)

    # D-gent link
    datum_id: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # Relationship
    coalition: Mapped["Coalition"] = relationship("Coalition", back_populates="outputs")

    __table_args__ = (
        Index("idx_coalition_output_coalition", "coalition_id"),
        Index("idx_coalition_output_type", "output_type"),
    )
