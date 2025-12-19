"""
Collaboration Flow: Multi-Agent Blackboard.

Enables multiple agents to collaborate on shared problems via blackboard pattern.

See: spec/f-gents/collaboration.md
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, AsyncIterator

from agents.f.config import FlowConfig
from agents.f.flow import AgentProtocol, FlowAgent, FlowEvent
from agents.f.modalities.blackboard import (
    AgentRole,
    Blackboard,
    Contribution,
    Decision,
    Proposal,
    Query,
    Vote,
)
from agents.f.state import ContributionType, FlowState, Permission

if TYPE_CHECKING:
    pass


# ============================================================================
# Contribution Order
# ============================================================================


class RoundRobinOrder:
    """Each agent contributes once per round, in fixed order."""

    def __init__(self, agents: list[AgentRole]):
        self.agents = sorted(agents, key=lambda a: a.priority)
        self.current_index = 0

    def next_agent(self) -> AgentRole:
        """Get the next agent in round-robin order."""
        agent = self.agents[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.agents)
        return agent

    def is_round_complete(self) -> bool:
        """Check if a full round is complete."""
        return self.current_index == 0

    def agents_for_round(self) -> list[AgentRole]:
        """Get all agents for a round."""
        return self.agents


class PriorityOrder:
    """Agents with pending high-priority contributions go first."""

    def __init__(self, agents: list[AgentRole]):
        self.agents = agents
        self.pending_priorities: dict[str, float] = {}

    def set_priority(self, agent_id: str, priority: float) -> None:
        """Set the priority for an agent."""
        self.pending_priorities[agent_id] = priority

    def next_agent(self) -> AgentRole:
        """Get the agent with highest pending priority."""
        # Highest priority first
        sorted_agents = sorted(
            self.agents,
            key=lambda a: self.pending_priorities.get(a.id, 0),
            reverse=True,
        )
        return sorted_agents[0]

    def agents_for_round(self) -> list[AgentRole]:
        """Get all agents for a round, sorted by priority."""
        return sorted(
            self.agents,
            key=lambda a: self.pending_priorities.get(a.id, 0),
            reverse=True,
        )


class FreeFormOrder:
    """Any agent can contribute at any time."""

    def __init__(self, agents: list[AgentRole]):
        self.agents = agents
        self.contribution_queue: asyncio.Queue[AgentRole] = asyncio.Queue()

    async def request_contribution(self, agent: AgentRole) -> None:
        """Request a contribution from an agent."""
        await self.contribution_queue.put(agent)

    async def next_agent(self) -> AgentRole:
        """Get the next agent from the queue."""
        return await self.contribution_queue.get()

    def agents_for_round(self) -> list[AgentRole]:
        """Get all agents (order doesn't matter in free-form)."""
        return self.agents


# ============================================================================
# Collaboration Flow
# ============================================================================


@dataclass
class ContributionRequest:
    """Request for an agent to contribute."""

    problem: str
    context: list[Contribution]
    round: int
    role: str
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ModeratorInput:
    """Input for moderator decision."""

    proposal: Proposal
    context: list[Contribution]
    guidelines: str | None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class CollaborationResult:
    """Final result from collaboration."""

    problem: str
    decisions: list[Decision]
    contributions: list[Contribution]
    rounds_completed: int
    final_synthesis: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class CollaborationFlow:
    """
    Multi-agent collaboration via blackboard.

    This class wraps a FlowAgent and implements collaboration-specific logic:
    - Contribution ordering (round-robin, priority, free-form)
    - Consensus mechanisms (voting, moderator, timestamp)
    - Role-based permissions
    """

    def __init__(
        self,
        flow_agent: FlowAgent,
        agents: dict[str, AgentProtocol],
        roles: list[AgentRole],
        config: FlowConfig,
    ):
        self.flow_agent = flow_agent
        self.agents = agents
        self.roles = {role.id: role for role in roles}
        self.config = config

        # Create contribution order
        if config.contribution_order == "round_robin":
            self.order = RoundRobinOrder(roles)
        elif config.contribution_order == "priority":
            self.order = PriorityOrder(roles)
        elif config.contribution_order == "free":
            self.order = FreeFormOrder(roles)
        else:
            msg = f"Unknown contribution order: {config.contribution_order}"
            raise ValueError(msg)

        # Blackboard
        self.blackboard: Blackboard | None = None
        self._state = FlowState.DORMANT

    def _get_agent(self, agent_id: str) -> AgentProtocol:
        """Get an agent by ID."""
        if agent_id not in self.agents:
            msg = f"Agent not found: {agent_id}"
            raise ValueError(msg)
        return self.agents[agent_id]

    def _get_role(self, agent_id: str) -> AgentRole:
        """Get an agent's role."""
        if agent_id not in self.roles:
            msg = f"Role not found for agent: {agent_id}"
            raise ValueError(msg)
        return self.roles[agent_id]

    def _get_moderator(self) -> AgentProtocol:
        """Get the moderator agent."""
        if self.config.moderator_id is None:
            msg = "No moderator configured"
            raise ValueError(msg)
        return self._get_agent(self.config.moderator_id)

    def _check_permission(self, agent_id: str, permission: Permission) -> bool:
        """Check if agent has permission."""
        role = self._get_role(agent_id)
        return permission in role.permissions

    async def start(self, problem: str) -> None:
        """
        Initialize collaboration with problem statement.

        Args:
            problem: The problem to solve collaboratively.
        """
        self.blackboard = Blackboard(problem=problem)
        self._state = FlowState.STREAMING

    async def run_round(self) -> AsyncIterator[Contribution]:
        """
        Execute one round of contributions.

        Yields:
            Contributions as they are posted.
        """
        if self.blackboard is None:
            msg = "Blackboard not initialized. Call start() first."
            raise RuntimeError(msg)

        self.blackboard.current_round += 1
        contributions_this_round = 0

        for agent_role in self.order.agents_for_round():
            # Check round limits
            if contributions_this_round >= self.config.max_contributions_per_round:
                break

            # Agent reads board (permission check)
            if Permission.READ_ALL in agent_role.permissions:
                context = self.blackboard.read()
            elif Permission.READ_OWN in agent_role.permissions:
                context = self.blackboard.read(Query(agent_id=agent_role.id))
            else:
                context = []

            # Agent generates contribution
            agent = self._get_agent(agent_role.id)

            # Create contribution request
            request = ContributionRequest(
                problem=self.blackboard.problem,
                context=context,
                round=self.blackboard.current_round,
                role=agent_role.name,
            )

            try:
                # Invoke agent (with timeout)
                result = await asyncio.wait_for(
                    agent.invoke(request),
                    timeout=self.config.contribution_timeout,
                )

                # Parse result into contribution
                contribution = self._parse_contribution(
                    result, agent_role, self.blackboard.current_round
                )

                if contribution and self._check_permission(agent_role.id, Permission.POST):
                    self.blackboard.post(contribution)
                    contributions_this_round += 1
                    yield contribution

                    # Check for proposals
                    if contribution.contribution_type == ContributionType.DECISION:
                        await self._handle_proposal(contribution)

            except asyncio.TimeoutError:
                # Agent didn't respond in time, skip
                continue
            except Exception:
                # Agent error, skip
                continue

    def _parse_contribution(
        self, result: Any, agent_role: AgentRole, round: int
    ) -> Contribution | None:
        """
        Parse agent result into a Contribution.

        This is a simple implementation. In production, you'd want more
        sophisticated parsing of LLM outputs.
        """
        if isinstance(result, Contribution):
            return result

        # If result is a string, create a simple contribution
        if isinstance(result, str):
            return Contribution(
                agent_id=agent_role.id,
                agent_role=agent_role.name,
                content=result,
                contribution_type=ContributionType.IDEA,
                confidence=0.5,
                round=round,
            )

        # If result is a dict, extract fields
        if isinstance(result, dict):
            return Contribution(
                agent_id=agent_role.id,
                agent_role=agent_role.name,
                content=result.get("content", ""),
                contribution_type=ContributionType(result.get("type", "idea")),
                confidence=result.get("confidence", 0.5),
                references=result.get("references", []),
                round=round,
            )

        return None

    async def _handle_proposal(self, contribution: Contribution) -> None:
        """Handle a contribution that is a proposal."""
        if self.blackboard is None:
            return

        proposal = Proposal(
            contribution_id=contribution.id,
            title=f"Proposal from {contribution.agent_role}",
            description=contribution.content,
            proposed_by=contribution.agent_id,
            round=contribution.round,
        )
        self.blackboard.propose(proposal)

    async def build_consensus(self) -> AsyncIterator[Decision]:
        """
        Resolve pending proposals.

        Yields:
            Decisions as they are made.
        """
        if self.blackboard is None:
            msg = "Blackboard not initialized"
            raise RuntimeError(msg)

        self._state = FlowState.CONVERGING

        for proposal in list(self.blackboard.proposals):
            decision = await self._resolve_proposal(proposal)
            self.blackboard.decide(proposal.id, decision)
            yield decision

    async def _resolve_proposal(self, proposal: Proposal) -> Decision:
        """Resolve a proposal using configured conflict strategy."""
        if self.blackboard is None:
            msg = "Blackboard not initialized"
            raise RuntimeError(msg)

        if self.config.conflict_strategy == "vote":
            # Get voters
            voters = [
                role
                for role in self.order.agents_for_round()
                if Permission.VOTE in role.permissions
            ]
            return await self.resolve_by_vote(proposal, voters)
        elif self.config.conflict_strategy == "moderator":
            context = self.blackboard.read()
            return await self.resolve_by_moderator(proposal, context)
        elif self.config.conflict_strategy == "timestamp":
            # For timestamp, just approve based on earliest
            return Decision(
                proposal_id=proposal.id,
                outcome="approved",
                method="timestamp",
                reasoning="First proposal wins",
            )
        else:
            msg = f"Unknown conflict strategy: {self.config.conflict_strategy}"
            raise ValueError(msg)

    async def resolve_by_vote(
        self,
        proposal: Proposal,
        voters: list[AgentRole],
    ) -> Decision:
        """Resolve proposal via agent voting."""
        votes: dict[str, Vote] = {}

        for voter in voters:
            vote = await self._get_vote(voter, proposal)
            votes[voter.id] = vote

        # Count votes
        approve_weight = sum(v.weight for v in votes.values() if v.choice == "approve")
        reject_weight = sum(v.weight for v in votes.values() if v.choice == "reject")
        total_weight = sum(v.weight for v in votes.values())

        if total_weight == 0:
            # No votes, defer
            return Decision(
                proposal_id=proposal.id,
                outcome="deferred",
                method="vote",
                reasoning="No votes received",
            )

        if approve_weight / total_weight >= self.config.consensus_threshold:
            return Decision(
                proposal_id=proposal.id,
                outcome="approved",
                method="vote",
                evidence={"votes": votes},
                reasoning=f"Approved with {approve_weight}/{total_weight} votes",
            )
        else:
            return Decision(
                proposal_id=proposal.id,
                outcome="rejected",
                method="vote",
                evidence={"votes": votes},
                reasoning=f"Rejected with {reject_weight}/{total_weight} votes",
            )

    async def _get_vote(self, voter: AgentRole, proposal: Proposal) -> Vote:
        """
        Get a vote from an agent.

        This is simplified - in production you'd invoke the agent with
        the proposal and parse their vote response.
        """
        # For now, return a simple mock vote
        # In production, invoke agent with proposal details
        return Vote(
            voter_id=voter.id,
            voter_role=voter.name,
            proposal_id=proposal.id,
            choice="approve",  # Mock: always approve
            weight=1.0,
        )

    async def resolve_by_moderator(
        self,
        proposal: Proposal,
        context: list[Contribution],
    ) -> Decision:
        """Moderator agent makes final decision."""
        moderator = self._get_moderator()

        # Create moderator input
        moderator_input = ModeratorInput(
            proposal=proposal,
            context=context,
            guidelines=self.config.moderation_guidelines,
        )

        # Invoke moderator
        try:
            result = await moderator.invoke(moderator_input)

            # Parse result
            if isinstance(result, dict):
                return Decision(
                    proposal_id=proposal.id,
                    outcome=result.get("outcome", "deferred"),
                    method="moderator",
                    reasoning=result.get("reasoning", ""),
                )
            else:
                # Default to approved
                return Decision(
                    proposal_id=proposal.id,
                    outcome="approved",
                    method="moderator",
                    reasoning=str(result),
                )
        except Exception as e:
            # Moderator error, defer
            return Decision(
                proposal_id=proposal.id,
                outcome="deferred",
                method="moderator",
                reasoning=f"Moderator error: {e}",
            )

    async def resolve_by_timestamp(
        self,
        conflicting: list[Contribution],
    ) -> Contribution:
        """Earliest contribution wins conflicts."""
        return min(conflicting, key=lambda c: c.timestamp)

    async def harvest(self) -> CollaborationResult:
        """
        Extract final result from blackboard.

        Returns:
            CollaborationResult containing all decisions and contributions.
        """
        if self.blackboard is None:
            msg = "Blackboard not initialized"
            raise RuntimeError(msg)

        self._state = FlowState.COLLAPSED

        # Synthesize outcome (simplified)
        synthesis = await self._synthesize_outcome()

        return CollaborationResult(
            problem=self.blackboard.problem,
            decisions=self.blackboard.decisions,
            contributions=self.blackboard.contributions,
            rounds_completed=self.blackboard.current_round,
            final_synthesis=synthesis,
        )

    async def _synthesize_outcome(self) -> str | None:
        """
        Synthesize final outcome from contributions.

        This is a placeholder. In production, you'd use a synthesizer agent
        or more sophisticated aggregation.
        """
        if self.blackboard is None:
            return None

        # Find synthesizer agent if available
        synthesizer_role = None
        for role in self.roles.values():
            if Permission.DECIDE in role.permissions:
                synthesizer_role = role
                break

        if synthesizer_role is None:
            return None

        # Simple synthesis: concatenate high-confidence contributions
        high_confidence = [c for c in self.blackboard.contributions if c.confidence > 0.7]

        if not high_confidence:
            return "No high-confidence contributions"

        return "\n".join(c.content for c in high_confidence[:5])


__all__ = [
    "RoundRobinOrder",
    "PriorityOrder",
    "FreeFormOrder",
    "ContributionRequest",
    "ModeratorInput",
    "CollaborationResult",
    "CollaborationFlow",
]
