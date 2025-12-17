"""
Blackboard: Shared state for multi-agent collaboration.

The Blackboard pattern enables multiple agents to contribute to shared state,
with contributions, proposals, decisions, and queries.

See: spec/f-gents/collaboration.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable
from uuid import uuid4

from agents.f.state import ContributionType, Permission


@dataclass
class Contribution:
    """A single agent's contribution to the blackboard."""

    id: str = field(default_factory=lambda: str(uuid4()))
    agent_id: str = ""
    agent_role: str = ""
    content: str = ""
    contribution_type: ContributionType = ContributionType.IDEA
    references: list[str] = field(default_factory=list)
    """IDs of contributions this responds to."""
    confidence: float = 0.5
    """Agent's confidence in this contribution (0.0-1.0)."""
    round: int = 0
    """Which contribution round."""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Vote:
    """A vote on a proposal."""

    voter_id: str
    voter_role: str
    proposal_id: str
    choice: str  # "approve" | "reject" | "abstain"
    weight: float = 1.0
    reasoning: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class Proposal:
    """An item requiring group decision."""

    id: str = field(default_factory=lambda: str(uuid4()))
    contribution_id: str | None = None
    """The contribution that triggered this proposal."""
    title: str = ""
    description: str = ""
    proposed_by: str = ""
    """Agent ID who proposed."""
    round: int = 0
    votes: list[Vote] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Decision:
    """A resolved proposal."""

    proposal_id: str
    outcome: str  # "approved" | "rejected" | "deferred"
    method: str  # "vote" | "moderator" | "timestamp"
    evidence: dict[str, Any] = field(default_factory=dict)
    """Votes, reasoning, or other evidence."""
    reasoning: str | None = None
    decided_at: datetime = field(default_factory=datetime.now)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Query:
    """Query for reading contributions."""

    agent_id: str | None = None
    """Filter by contributor."""
    agent_role: str | None = None
    """Filter by role."""
    contribution_type: ContributionType | None = None
    """Filter by type."""
    min_confidence: float | None = None
    """Minimum confidence threshold."""
    min_round: int | None = None
    """Minimum round number."""
    max_round: int | None = None
    """Maximum round number."""
    references: list[str] | None = None
    """Filter by referenced contribution IDs."""
    custom_filter: Callable[[Contribution], bool] | None = None
    """Custom filter function."""

    def matches(self, contribution: Contribution) -> bool:
        """Check if contribution matches this query."""
        if self.agent_id is not None and contribution.agent_id != self.agent_id:
            return False
        if self.agent_role is not None and contribution.agent_role != self.agent_role:
            return False
        if (
            self.contribution_type is not None
            and contribution.contribution_type != self.contribution_type
        ):
            return False
        if (
            self.min_confidence is not None
            and contribution.confidence < self.min_confidence
        ):
            return False
        if self.min_round is not None and contribution.round < self.min_round:
            return False
        if self.max_round is not None and contribution.round > self.max_round:
            return False
        if self.references is not None:
            # Check if any of the query references are in the contribution's references
            if not any(ref in contribution.references for ref in self.references):
                return False
        if self.custom_filter is not None and not self.custom_filter(contribution):
            return False
        return True


@dataclass
class AgentRole:
    """Definition of an agent's role in collaboration."""

    id: str
    name: str
    """Human-readable name."""
    description: str = ""
    """What this role does."""
    permissions: set[Permission] = field(default_factory=set)
    """What actions allowed."""
    priority: int = 0
    """Order in round-robin (lower = higher priority)."""
    specialization: str = ""
    """Area of expertise."""


@dataclass
class Blackboard:
    """Shared state for multi-agent collaboration."""

    problem: str
    """Original problem statement."""
    contributions: list[Contribution] = field(default_factory=list)
    """All posted contributions."""
    proposals: list[Proposal] = field(default_factory=list)
    """Items requiring decision."""
    decisions: list[Decision] = field(default_factory=list)
    """Resolved proposals."""
    current_round: int = 0
    """Current contribution round."""
    metadata: dict[str, Any] = field(default_factory=dict)
    """Arbitrary shared state."""

    def post(self, contribution: Contribution) -> None:
        """Add a contribution to the board."""
        self.contributions.append(contribution)

    def read(self, query: Query | None = None) -> list[Contribution]:
        """
        Read contributions matching query.

        Args:
            query: Optional query to filter contributions. If None, returns all.

        Returns:
            List of matching contributions.
        """
        if query is None:
            return list(self.contributions)
        return [c for c in self.contributions if query.matches(c)]

    def propose(self, proposal: Proposal) -> None:
        """Submit something for group decision."""
        self.proposals.append(proposal)

    def decide(self, proposal_id: str, decision: Decision) -> None:
        """Record a decision on a proposal."""
        self.decisions.append(decision)
        # Remove from pending
        self.proposals = [p for p in self.proposals if p.id != proposal_id]

    def get_proposal(self, proposal_id: str) -> Proposal | None:
        """Get a proposal by ID."""
        for proposal in self.proposals:
            if proposal.id == proposal_id:
                return proposal
        return None


__all__ = [
    "Contribution",
    "Vote",
    "Proposal",
    "Decision",
    "Query",
    "AgentRole",
    "Blackboard",
]
