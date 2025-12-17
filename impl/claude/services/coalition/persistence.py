"""
Coalition Persistence: TableAdapter + D-gent integration for Coalition Crown Jewel.

Owns domain semantics for Coalition storage:
- WHEN to persist (coalition formation, member joins, proposals, votes, outputs)
- WHY to persist (collaborative decision-making + transparent process + visible outputs)
- HOW to compose (TableAdapter for structure, D-gent for discussion content)

AGENTESE aspects exposed:
- manifest: Show coalition landscape
- forge: Form a new coalition
- join: Join existing coalition
- propose: Submit a proposal
- vote: Cast a vote
- deliberate: View discussion thread

k-clique foundation: Mathematical graph theory for emergent group formation.

See: docs/skills/metaphysical-fullstack.md
"""

from __future__ import annotations

import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agents.d import Datum, DgentProtocol, TableAdapter
from models.coalition import (
    Coalition,
    CoalitionMember,
    CoalitionOutput,
    CoalitionProposal,
    ProposalVote,
)

if TYPE_CHECKING:
    pass


@dataclass
class CoalitionView:
    """View of a coalition."""

    id: str
    name: str
    goal: str
    description: str | None
    status: str
    member_count: int
    proposal_count: int
    output_count: int
    consensus_threshold: float
    formed_at: str | None
    created_at: str


@dataclass
class MemberView:
    """View of a coalition member."""

    id: str
    coalition_id: str
    agent_id: str
    agent_name: str
    agent_type: str
    role: str
    voting_power: float
    is_active: bool
    contribution_count: int
    joined_at: str


@dataclass
class ProposalView:
    """View of a coalition proposal."""

    id: str
    coalition_id: str
    proposer_name: str | None
    title: str
    description: str
    proposal_type: str
    status: str
    votes_for: int
    votes_against: int
    votes_abstain: int
    approval_score: float | None
    created_at: str


@dataclass
class VoteView:
    """View of a proposal vote."""

    id: str
    proposal_id: str
    member_name: str
    vote: str
    weight: float
    rationale: str | None
    created_at: str


@dataclass
class OutputView:
    """View of a coalition output."""

    id: str
    coalition_id: str
    output_type: str
    title: str
    content: str
    contributor_ids: list[str]
    created_at: str


@dataclass
class CoalitionStatus:
    """Coalition landscape status."""

    total_coalitions: int
    active_coalitions: int
    total_members: int
    total_proposals: int
    total_outputs: int
    storage_backend: str


class CoalitionPersistence:
    """
    Persistence layer for Coalition Crown Jewel.

    Composes:
    - TableAdapter[Coalition]: Coalition state and configuration
    - TableAdapter[CoalitionMember]: Membership and roles
    - D-gent: Discussion content, proposal rationale

    Domain Semantics:
    - Coalitions form around shared goals
    - Members have roles and voting power
    - Proposals go through transparent voting
    - Outputs are the tangible results

    k-Clique Pattern:
    - Coalitions are emergent groups
    - Formation requires minimum connectivity
    - Dissolution when goal achieved or consensus fails

    Example:
        persistence = CoalitionPersistence(
            coalition_adapter=TableAdapter(Coalition, session_factory),
            member_adapter=TableAdapter(CoalitionMember, session_factory),
            dgent=dgent_router,
        )

        coalition = await persistence.forge("Build Feature X", goal="Ship by Q1")
        await persistence.join(coalition.id, "Alice", agent_type="citizen")
    """

    def __init__(
        self,
        coalition_adapter: TableAdapter[Coalition],
        member_adapter: TableAdapter[CoalitionMember],
        dgent: DgentProtocol,
    ) -> None:
        self.coalitions = coalition_adapter
        self.members = member_adapter
        self.dgent = dgent

    # =========================================================================
    # Coalition Management
    # =========================================================================

    async def forge(
        self,
        name: str,
        goal: str,
        description: str | None = None,
        min_members: int = 2,
        max_members: int | None = None,
        consensus_threshold: float = 0.66,
    ) -> CoalitionView:
        """
        Forge a new coalition.

        AGENTESE: world.coalition.forge

        Args:
            name: Coalition name
            goal: Shared goal
            description: Optional description
            min_members: Minimum members to activate
            max_members: Maximum members (None for unlimited)
            consensus_threshold: Required approval percentage

        Returns:
            CoalitionView of the new coalition
        """
        coalition_id = f"coalition-{uuid.uuid4().hex[:12]}"

        async with self.coalitions.session_factory() as session:
            coalition = Coalition(
                id=coalition_id,
                name=name,
                goal=goal,
                description=description,
                status="forming",
                formed_at=None,
                dissolved_at=None,
                min_members=min_members,
                max_members=max_members,
                config={},
                proposal_count=0,
                consensus_threshold=consensus_threshold,
            )
            session.add(coalition)
            await session.commit()

            return CoalitionView(
                id=coalition_id,
                name=name,
                goal=goal,
                description=description,
                status="forming",
                member_count=0,
                proposal_count=0,
                output_count=0,
                consensus_threshold=consensus_threshold,
                formed_at=None,
                created_at=coalition.created_at.isoformat()
                if coalition.created_at
                else "",
            )

    async def get_coalition(self, coalition_id: str) -> CoalitionView | None:
        """Get a coalition by ID."""
        async with self.coalitions.session_factory() as session:
            coalition = await session.get(Coalition, coalition_id)
            if coalition is None:
                return None

            # Count members
            member_count = await session.execute(
                select(func.count())
                .select_from(CoalitionMember)
                .where(CoalitionMember.coalition_id == coalition_id)
                .where(CoalitionMember.is_active == True)
            )

            # Count outputs
            output_count = await session.execute(
                select(func.count())
                .select_from(CoalitionOutput)
                .where(CoalitionOutput.coalition_id == coalition_id)
            )

            return CoalitionView(
                id=coalition.id,
                name=coalition.name,
                goal=coalition.goal,
                description=coalition.description,
                status=coalition.status,
                member_count=member_count.scalar() or 0,
                proposal_count=coalition.proposal_count,
                output_count=output_count.scalar() or 0,
                consensus_threshold=coalition.consensus_threshold,
                formed_at=coalition.formed_at.isoformat()
                if coalition.formed_at
                else None,
                created_at=coalition.created_at.isoformat()
                if coalition.created_at
                else "",
            )

    async def list_coalitions(
        self,
        status: str | None = None,
        limit: int = 20,
    ) -> list[CoalitionView]:
        """List coalitions with optional status filter."""
        async with self.coalitions.session_factory() as session:
            stmt = select(Coalition)

            if status:
                stmt = stmt.where(Coalition.status == status)

            stmt = stmt.order_by(Coalition.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            coalitions = result.scalars().all()

            views = []
            for c in coalitions:
                member_count = await session.execute(
                    select(func.count())
                    .select_from(CoalitionMember)
                    .where(CoalitionMember.coalition_id == c.id)
                    .where(CoalitionMember.is_active == True)
                )
                views.append(
                    CoalitionView(
                        id=c.id,
                        name=c.name,
                        goal=c.goal,
                        description=c.description,
                        status=c.status,
                        member_count=member_count.scalar() or 0,
                        proposal_count=c.proposal_count,
                        output_count=0,
                        consensus_threshold=c.consensus_threshold,
                        formed_at=c.formed_at.isoformat() if c.formed_at else None,
                        created_at=c.created_at.isoformat() if c.created_at else "",
                    )
                )

            return views

    async def dissolve(self, coalition_id: str, reason: str | None = None) -> bool:
        """
        Dissolve a coalition.

        AGENTESE: world.coalition.dissolve
        """
        async with self.coalitions.session_factory() as session:
            coalition = await session.get(Coalition, coalition_id)
            if coalition is None:
                return False

            coalition.status = "dissolved"
            coalition.dissolved_at = datetime.utcnow()

            # Deactivate all members
            members_stmt = select(CoalitionMember).where(
                CoalitionMember.coalition_id == coalition_id
            )
            result = await session.execute(members_stmt)
            members = result.scalars().all()
            for m in members:
                m.is_active = False
                m.left_at = datetime.utcnow()

            await session.commit()
            return True

    # =========================================================================
    # Member Management
    # =========================================================================

    async def join(
        self,
        coalition_id: str,
        agent_name: str,
        agent_id: str | None = None,
        agent_type: str = "citizen",
        role: str = "member",
        voting_power: float = 1.0,
    ) -> MemberView | None:
        """
        Join a coalition.

        AGENTESE: world.coalition.join

        Args:
            coalition_id: Coalition to join
            agent_name: Display name
            agent_id: Link to Town citizen or external ID
            agent_type: Type ("citizen", "external", "human")
            role: Role ("leader", "member", "observer")
            voting_power: Voting weight

        Returns:
            MemberView or None if coalition not found/closed
        """
        async with self.members.session_factory() as session:
            coalition = await session.get(Coalition, coalition_id)
            if coalition is None:
                return None

            # Check if coalition accepts new members
            if coalition.status in ("complete", "dissolved"):
                return None

            # Check max members
            if coalition.max_members:
                member_count = await session.execute(
                    select(func.count())
                    .select_from(CoalitionMember)
                    .where(CoalitionMember.coalition_id == coalition_id)
                    .where(CoalitionMember.is_active == True)
                )
                if (member_count.scalar() or 0) >= coalition.max_members:
                    return None

            member_id = f"member-{uuid.uuid4().hex[:12]}"
            agent_id = agent_id or f"agent-{uuid.uuid4().hex[:8]}"

            member = CoalitionMember(
                id=member_id,
                coalition_id=coalition_id,
                agent_id=agent_id,
                agent_name=agent_name,
                agent_type=agent_type,
                role=role,
                voting_power=voting_power,
                can_propose=role != "observer",
                can_vote=role != "observer",
                is_active=True,
                contribution_count=0,
            )
            session.add(member)

            # Check if coalition should activate
            member_count = await session.execute(
                select(func.count())
                .select_from(CoalitionMember)
                .where(CoalitionMember.coalition_id == coalition_id)
                .where(CoalitionMember.is_active == True)
            )
            current_members = (member_count.scalar() or 0) + 1  # Include new member

            if coalition.status == "forming" and current_members >= coalition.min_members:
                coalition.status = "active"
                coalition.formed_at = datetime.utcnow()

            await session.commit()

            return MemberView(
                id=member_id,
                coalition_id=coalition_id,
                agent_id=agent_id,
                agent_name=agent_name,
                agent_type=agent_type,
                role=role,
                voting_power=voting_power,
                is_active=True,
                contribution_count=0,
                joined_at=member.joined_at.isoformat() if member.joined_at else "",
            )

    async def leave(self, member_id: str) -> bool:
        """Leave a coalition."""
        async with self.members.session_factory() as session:
            member = await session.get(CoalitionMember, member_id)
            if member is None or not member.is_active:
                return False

            member.is_active = False
            member.left_at = datetime.utcnow()
            await session.commit()
            return True

    async def list_members(
        self,
        coalition_id: str,
        role: str | None = None,
        active_only: bool = True,
    ) -> list[MemberView]:
        """List members of a coalition."""
        async with self.members.session_factory() as session:
            stmt = select(CoalitionMember).where(
                CoalitionMember.coalition_id == coalition_id
            )

            if role:
                stmt = stmt.where(CoalitionMember.role == role)
            if active_only:
                stmt = stmt.where(CoalitionMember.is_active == True)

            stmt = stmt.order_by(CoalitionMember.joined_at)
            result = await session.execute(stmt)
            members = result.scalars().all()

            return [self._member_to_view(m) for m in members]

    # =========================================================================
    # Proposal Management
    # =========================================================================

    async def propose(
        self,
        coalition_id: str,
        proposer_id: str,
        title: str,
        description: str,
        proposal_type: str = "action",
    ) -> ProposalView | None:
        """
        Submit a proposal.

        AGENTESE: world.coalition.propose

        Args:
            coalition_id: Coalition to propose to
            proposer_id: Member submitting the proposal
            title: Proposal title
            description: Full description
            proposal_type: Type ("action", "decision", "resource", "membership")

        Returns:
            ProposalView or None
        """
        async with self.members.session_factory() as session:
            coalition = await session.get(Coalition, coalition_id)
            member = await session.get(CoalitionMember, proposer_id)

            if coalition is None or coalition.status != "active":
                return None
            if member is None or not member.is_active or not member.can_propose:
                return None

            proposal_id = f"proposal-{uuid.uuid4().hex[:12]}"

            # Store discussion content in D-gent
            datum = Datum(
                id=f"coalition-{proposal_id}",
                content=f"# {title}\n\n{description}".encode("utf-8"),
                created_at=time.time(),
                causal_parent=None,
                metadata={
                    "type": "coalition_proposal",
                    "coalition_id": coalition_id,
                    "proposer_id": proposer_id,
                },
            )
            datum_id = await self.dgent.put(datum)

            proposal = CoalitionProposal(
                id=proposal_id,
                coalition_id=coalition_id,
                proposer_id=proposer_id,
                title=title,
                description=description,
                proposal_type=proposal_type,
                status="draft",
                voting_started_at=None,
                voting_ended_at=None,
                votes_for=0,
                votes_against=0,
                votes_abstain=0,
                approval_score=None,
                datum_id=datum_id,
            )
            session.add(proposal)

            # Update coalition proposal count
            coalition.proposal_count += 1

            await session.commit()

            return ProposalView(
                id=proposal_id,
                coalition_id=coalition_id,
                proposer_name=member.agent_name,
                title=title,
                description=description,
                proposal_type=proposal_type,
                status="draft",
                votes_for=0,
                votes_against=0,
                votes_abstain=0,
                approval_score=None,
                created_at=proposal.created_at.isoformat()
                if proposal.created_at
                else "",
            )

    async def start_voting(self, proposal_id: str) -> bool:
        """Start voting on a proposal."""
        async with self.members.session_factory() as session:
            proposal = await session.get(CoalitionProposal, proposal_id)
            if proposal is None or proposal.status != "draft":
                return False

            proposal.status = "voting"
            proposal.voting_started_at = datetime.utcnow()
            await session.commit()
            return True

    async def vote(
        self,
        proposal_id: str,
        member_id: str,
        vote: str,
        rationale: str | None = None,
    ) -> VoteView | None:
        """
        Cast a vote on a proposal.

        AGENTESE: world.coalition.vote

        Args:
            proposal_id: Proposal to vote on
            member_id: Voting member
            vote: Vote ("for", "against", "abstain")
            rationale: Optional reasoning

        Returns:
            VoteView or None
        """
        async with self.members.session_factory() as session:
            proposal = await session.get(CoalitionProposal, proposal_id)
            member = await session.get(CoalitionMember, member_id)

            if proposal is None or proposal.status != "voting":
                return None
            if member is None or not member.is_active or not member.can_vote:
                return None
            if member.coalition_id != proposal.coalition_id:
                return None

            # Check for existing vote
            existing = await session.execute(
                select(ProposalVote)
                .where(ProposalVote.proposal_id == proposal_id)
                .where(ProposalVote.member_id == member_id)
            )
            if existing.scalar_one_or_none():
                return None  # Already voted

            vote_id = f"vote-{uuid.uuid4().hex[:12]}"

            vote_record = ProposalVote(
                id=vote_id,
                proposal_id=proposal_id,
                member_id=member_id,
                vote=vote,
                weight=member.voting_power,
                rationale=rationale,
            )
            session.add(vote_record)

            # Update vote counts
            if vote == "for":
                proposal.votes_for += 1
            elif vote == "against":
                proposal.votes_against += 1
            else:
                proposal.votes_abstain += 1

            # Calculate approval score
            total_votes = proposal.votes_for + proposal.votes_against
            if total_votes > 0:
                proposal.approval_score = proposal.votes_for / total_votes

            await session.commit()

            return VoteView(
                id=vote_id,
                proposal_id=proposal_id,
                member_name=member.agent_name,
                vote=vote,
                weight=member.voting_power,
                rationale=rationale,
                created_at=vote_record.created_at.isoformat()
                if vote_record.created_at
                else "",
            )

    async def conclude_voting(self, proposal_id: str) -> str | None:
        """
        Conclude voting and determine outcome.

        Returns:
            New proposal status ("approved", "rejected") or None
        """
        async with self.members.session_factory() as session:
            proposal = await session.get(CoalitionProposal, proposal_id)
            if proposal is None or proposal.status != "voting":
                return None

            coalition = await session.get(Coalition, proposal.coalition_id)
            if coalition is None:
                return None

            proposal.voting_ended_at = datetime.utcnow()

            # Determine outcome
            if (
                proposal.approval_score is not None
                and proposal.approval_score >= coalition.consensus_threshold
            ):
                proposal.status = "approved"
            else:
                proposal.status = "rejected"

            await session.commit()
            return proposal.status

    async def list_proposals(
        self,
        coalition_id: str,
        status: str | None = None,
        limit: int = 20,
    ) -> list[ProposalView]:
        """List proposals for a coalition."""
        async with self.members.session_factory() as session:
            stmt = (
                select(CoalitionProposal, CoalitionMember.agent_name)
                .outerjoin(
                    CoalitionMember, CoalitionProposal.proposer_id == CoalitionMember.id
                )
                .where(CoalitionProposal.coalition_id == coalition_id)
            )

            if status:
                stmt = stmt.where(CoalitionProposal.status == status)

            stmt = stmt.order_by(CoalitionProposal.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            rows = result.all()

            return [
                ProposalView(
                    id=p.id,
                    coalition_id=p.coalition_id,
                    proposer_name=name,
                    title=p.title,
                    description=p.description,
                    proposal_type=p.proposal_type,
                    status=p.status,
                    votes_for=p.votes_for,
                    votes_against=p.votes_against,
                    votes_abstain=p.votes_abstain,
                    approval_score=p.approval_score,
                    created_at=p.created_at.isoformat() if p.created_at else "",
                )
                for p, name in rows
            ]

    # =========================================================================
    # Output Management
    # =========================================================================

    async def create_output(
        self,
        coalition_id: str,
        output_type: str,
        title: str,
        content: str,
        proposal_id: str | None = None,
        contributor_ids: list[str] | None = None,
    ) -> OutputView | None:
        """
        Create a coalition output.

        AGENTESE: world.coalition.output.create

        Args:
            coalition_id: Source coalition
            output_type: Type ("decision", "artifact", "action", "report")
            title: Output title
            content: Output content
            proposal_id: Linked proposal (if any)
            contributor_ids: Contributing members

        Returns:
            OutputView or None
        """
        async with self.coalitions.session_factory() as session:
            coalition = await session.get(Coalition, coalition_id)
            if coalition is None or coalition.status not in ("active", "complete"):
                return None

            output_id = f"output-{uuid.uuid4().hex[:12]}"

            # Store content in D-gent
            datum = Datum(
                id=f"coalition-output-{output_id}",
                content=content.encode("utf-8"),
                created_at=time.time(),
                causal_parent=None,
                metadata={
                    "type": "coalition_output",
                    "coalition_id": coalition_id,
                    "output_type": output_type,
                },
            )
            datum_id = await self.dgent.put(datum)

            output = CoalitionOutput(
                id=output_id,
                coalition_id=coalition_id,
                proposal_id=proposal_id,
                output_type=output_type,
                title=title,
                content=content,
                metadata_json={},
                contributor_ids=contributor_ids or [],
                datum_id=datum_id,
            )
            session.add(output)
            await session.commit()

            return OutputView(
                id=output_id,
                coalition_id=coalition_id,
                output_type=output_type,
                title=title,
                content=content,
                contributor_ids=contributor_ids or [],
                created_at=output.created_at.isoformat() if output.created_at else "",
            )

    async def list_outputs(
        self,
        coalition_id: str,
        output_type: str | None = None,
        limit: int = 20,
    ) -> list[OutputView]:
        """List outputs from a coalition."""
        async with self.coalitions.session_factory() as session:
            stmt = select(CoalitionOutput).where(
                CoalitionOutput.coalition_id == coalition_id
            )

            if output_type:
                stmt = stmt.where(CoalitionOutput.output_type == output_type)

            stmt = stmt.order_by(CoalitionOutput.created_at.desc()).limit(limit)
            result = await session.execute(stmt)
            outputs = result.scalars().all()

            return [
                OutputView(
                    id=o.id,
                    coalition_id=o.coalition_id,
                    output_type=o.output_type,
                    title=o.title,
                    content=o.content,
                    contributor_ids=o.contributor_ids or [],
                    created_at=o.created_at.isoformat() if o.created_at else "",
                )
                for o in outputs
            ]

    # =========================================================================
    # Health Status
    # =========================================================================

    async def manifest(self) -> CoalitionStatus:
        """
        Get coalition landscape status.

        AGENTESE: world.coalition.manifest
        """
        async with self.coalitions.session_factory() as session:
            # Count coalitions
            total_coalitions_result = await session.execute(
                select(func.count()).select_from(Coalition)
            )
            total_coalitions = total_coalitions_result.scalar() or 0

            active_coalitions_result = await session.execute(
                select(func.count())
                .select_from(Coalition)
                .where(Coalition.status == "active")
            )
            active_coalitions = active_coalitions_result.scalar() or 0

            # Count members
            total_members_result = await session.execute(
                select(func.count())
                .select_from(CoalitionMember)
                .where(CoalitionMember.is_active == True)
            )
            total_members = total_members_result.scalar() or 0

            # Count proposals
            total_proposals_result = await session.execute(
                select(func.count()).select_from(CoalitionProposal)
            )
            total_proposals = total_proposals_result.scalar() or 0

            # Count outputs
            total_outputs_result = await session.execute(
                select(func.count()).select_from(CoalitionOutput)
            )
            total_outputs = total_outputs_result.scalar() or 0

        return CoalitionStatus(
            total_coalitions=total_coalitions,
            active_coalitions=active_coalitions,
            total_members=total_members,
            total_proposals=total_proposals,
            total_outputs=total_outputs,
            storage_backend="postgres"
            if "postgres" in str(self.coalitions.session_factory).lower()
            else "sqlite",
        )

    # =========================================================================
    # Helper Methods
    # =========================================================================

    def _member_to_view(self, member: CoalitionMember) -> MemberView:
        """Convert CoalitionMember model to MemberView."""
        return MemberView(
            id=member.id,
            coalition_id=member.coalition_id,
            agent_id=member.agent_id,
            agent_name=member.agent_name,
            agent_type=member.agent_type,
            role=member.role,
            voting_power=member.voting_power,
            is_active=member.is_active,
            contribution_count=member.contribution_count,
            joined_at=member.joined_at.isoformat() if member.joined_at else "",
        )


__all__ = [
    "CoalitionPersistence",
    "CoalitionView",
    "MemberView",
    "ProposalView",
    "VoteView",
    "OutputView",
    "CoalitionStatus",
]
