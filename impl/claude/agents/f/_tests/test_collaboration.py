"""
Tests for Collaboration Flow (Phase 5).

Tests multi-agent blackboard collaboration including:
- Blackboard post and read operations
- Contribution ordering (round-robin, priority, free-form)
- Consensus mechanisms (voting, moderator)
- Role-based permissions
- Round limits and termination
"""

import asyncio
from datetime import datetime
from typing import Any

import pytest

from agents.f.config import FlowConfig
from agents.f.flow import Flow
from agents.f.modalities.blackboard import (
    AgentRole,
    Blackboard,
    Contribution,
    Decision,
    Proposal,
    Query,
    Vote,
)
from agents.f.modalities.collaboration import (
    CollaborationFlow,
    FreeFormOrder,
    PriorityOrder,
    RoundRobinOrder,
)
from agents.f.state import ContributionType, Permission

# ============================================================================
# Mock Agents
# ============================================================================


class MockAgent:
    """Mock agent for testing."""

    def __init__(self, agent_id: str, response: str | dict[str, Any] | Contribution):
        self.agent_id = agent_id
        self.response = response
        self.name = f"MockAgent({agent_id})"

    async def invoke(self, input):
        """Return mock response."""
        return self.response


# ============================================================================
# Test Blackboard Operations
# ============================================================================


class TestBlackboard:
    """Test basic blackboard operations."""

    def test_blackboard_creation(self) -> None:
        """Test creating a blackboard."""
        board = Blackboard(problem="Test problem")
        assert board.problem == "Test problem"
        assert len(board.contributions) == 0
        assert len(board.proposals) == 0
        assert len(board.decisions) == 0
        assert board.current_round == 0

    def test_post_contribution(self) -> None:
        """Test posting a contribution."""
        board = Blackboard(problem="Test")
        contrib = Contribution(
            agent_id="agent1",
            agent_role="Analyst",
            content="My contribution",
            contribution_type=ContributionType.IDEA,
            confidence=0.8,
            round=1,
        )
        board.post(contrib)
        assert len(board.contributions) == 1
        assert board.contributions[0] == contrib

    def test_read_all_contributions(self) -> None:
        """Test reading all contributions."""
        board = Blackboard(problem="Test")
        contrib1 = Contribution(agent_id="agent1", content="First", round=1)
        contrib2 = Contribution(agent_id="agent2", content="Second", round=1)
        board.post(contrib1)
        board.post(contrib2)

        results = board.read()
        assert len(results) == 2

    def test_read_with_query_agent_id(self) -> None:
        """Test reading contributions filtered by agent ID."""
        board = Blackboard(problem="Test")
        contrib1 = Contribution(agent_id="agent1", content="First", round=1)
        contrib2 = Contribution(agent_id="agent2", content="Second", round=1)
        board.post(contrib1)
        board.post(contrib2)

        query = Query(agent_id="agent1")
        results = board.read(query)
        assert len(results) == 1
        assert results[0].agent_id == "agent1"

    def test_read_with_query_type(self) -> None:
        """Test reading contributions filtered by type."""
        board = Blackboard(problem="Test")
        contrib1 = Contribution(
            agent_id="agent1",
            content="Idea",
            contribution_type=ContributionType.IDEA,
            round=1,
        )
        contrib2 = Contribution(
            agent_id="agent2",
            content="Critique",
            contribution_type=ContributionType.CRITIQUE,
            round=1,
        )
        board.post(contrib1)
        board.post(contrib2)

        query = Query(contribution_type=ContributionType.IDEA)
        results = board.read(query)
        assert len(results) == 1
        assert results[0].contribution_type == ContributionType.IDEA

    def test_read_with_query_confidence(self) -> None:
        """Test reading contributions filtered by confidence."""
        board = Blackboard(problem="Test")
        contrib1 = Contribution(
            agent_id="agent1", content="Low confidence", confidence=0.3, round=1
        )
        contrib2 = Contribution(
            agent_id="agent2", content="High confidence", confidence=0.9, round=1
        )
        board.post(contrib1)
        board.post(contrib2)

        query = Query(min_confidence=0.7)
        results = board.read(query)
        assert len(results) == 1
        assert results[0].confidence == 0.9

    def test_read_with_query_round(self) -> None:
        """Test reading contributions filtered by round."""
        board = Blackboard(problem="Test")
        contrib1 = Contribution(agent_id="agent1", content="Round 1", round=1)
        contrib2 = Contribution(agent_id="agent2", content="Round 2", round=2)
        contrib3 = Contribution(agent_id="agent3", content="Round 3", round=3)
        board.post(contrib1)
        board.post(contrib2)
        board.post(contrib3)

        query = Query(min_round=2, max_round=2)
        results = board.read(query)
        assert len(results) == 1
        assert results[0].round == 2

    def test_propose_and_decide(self) -> None:
        """Test proposing and deciding."""
        board = Blackboard(problem="Test")
        proposal = Proposal(
            id="prop1",
            title="Test proposal",
            description="Description",
            proposed_by="agent1",
            round=1,
        )
        board.propose(proposal)
        assert len(board.proposals) == 1

        decision = Decision(
            proposal_id="prop1",
            outcome="approved",
            method="vote",
        )
        board.decide("prop1", decision)
        assert len(board.decisions) == 1
        assert len(board.proposals) == 0  # Removed from pending


# ============================================================================
# Test Contribution Ordering
# ============================================================================


class TestContributionOrdering:
    """Test contribution ordering mechanisms."""

    def test_round_robin_creation(self) -> None:
        """Test creating round-robin order."""
        roles = [
            AgentRole(id="a1", name="Agent 1", priority=1),
            AgentRole(id="a2", name="Agent 2", priority=2),
            AgentRole(id="a3", name="Agent 3", priority=0),
        ]
        order = RoundRobinOrder(roles)
        assert len(order.agents) == 3
        # Should be sorted by priority
        assert order.agents[0].id == "a3"  # priority 0
        assert order.agents[1].id == "a1"  # priority 1
        assert order.agents[2].id == "a2"  # priority 2

    def test_round_robin_next_agent(self) -> None:
        """Test round-robin cycles through agents correctly."""
        roles = [
            AgentRole(id="a1", name="Agent 1", priority=1),
            AgentRole(id="a2", name="Agent 2", priority=2),
        ]
        order = RoundRobinOrder(roles)

        # First round
        agent1 = order.next_agent()
        assert agent1.id == "a1"
        assert not order.is_round_complete()

        agent2 = order.next_agent()
        assert agent2.id == "a2"
        assert order.is_round_complete()

        # Second round (cycles back)
        agent3 = order.next_agent()
        assert agent3.id == "a1"
        assert not order.is_round_complete()

    def test_priority_order_creation(self) -> None:
        """Test creating priority order."""
        roles = [
            AgentRole(id="a1", name="Agent 1"),
            AgentRole(id="a2", name="Agent 2"),
        ]
        order = PriorityOrder(roles)
        assert len(order.agents) == 2

    def test_priority_order_respects_priorities(self) -> None:
        """Test priority order respects priorities."""
        roles = [
            AgentRole(id="a1", name="Agent 1"),
            AgentRole(id="a2", name="Agent 2"),
            AgentRole(id="a3", name="Agent 3"),
        ]
        order = PriorityOrder(roles)

        # Set priorities
        order.set_priority("a1", 0.5)
        order.set_priority("a2", 0.9)
        order.set_priority("a3", 0.2)

        # Highest priority first
        agent = order.next_agent()
        assert agent.id == "a2"  # 0.9

    def test_free_form_order_creation(self) -> None:
        """Test creating free-form order."""
        roles = [
            AgentRole(id="a1", name="Agent 1"),
            AgentRole(id="a2", name="Agent 2"),
        ]
        order = FreeFormOrder(roles)
        assert len(order.agents) == 2

    @pytest.mark.asyncio
    async def test_free_form_order_queue(self) -> None:
        """Test free-form order uses queue."""
        roles = [
            AgentRole(id="a1", name="Agent 1"),
            AgentRole(id="a2", name="Agent 2"),
        ]
        order = FreeFormOrder(roles)

        # Request contribution from a2
        await order.request_contribution(roles[1])

        # Should get a2 first
        agent = await order.next_agent()
        assert agent.id == "a2"


# ============================================================================
# Test Consensus Mechanisms
# ============================================================================


class TestConsensusMechanisms:
    """Test consensus mechanisms."""

    @pytest.mark.asyncio
    async def test_voting_consensus_approved(self) -> None:
        """Test voting consensus mechanism - approved."""
        # Create roles with voting permission
        roles = [
            AgentRole(
                id="voter1",
                name="Voter 1",
                permissions={Permission.VOTE},
            ),
            AgentRole(
                id="voter2",
                name="Voter 2",
                permissions={Permission.VOTE},
            ),
            AgentRole(
                id="voter3",
                name="Voter 3",
                permissions={Permission.VOTE},
            ),
        ]

        # Create mock agents
        agents = {
            "voter1": MockAgent("voter1", "approve"),
            "voter2": MockAgent("voter2", "approve"),
            "voter3": MockAgent("voter3", "reject"),
        }

        config = FlowConfig(
            modality="collaboration",
            consensus_threshold=0.66,  # 2/3 = 0.6666... > 0.66
            conflict_strategy="vote",
        )

        # Create collaboration flow
        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        # Create proposal
        proposal = Proposal(
            id="test_prop",
            title="Test",
            proposed_by="voter1",
        )

        # Resolve by vote (mock the _get_vote method)
        async def mock_get_vote(voter, prop):
            if voter.id in ["voter1", "voter2"]:
                return Vote(
                    voter_id=voter.id,
                    voter_role=voter.name,
                    proposal_id=prop.id,
                    choice="approve",
                    weight=1.0,
                )
            else:
                return Vote(
                    voter_id=voter.id,
                    voter_role=voter.name,
                    proposal_id=prop.id,
                    choice="reject",
                    weight=1.0,
                )

        collab._get_vote = mock_get_vote  # type: ignore[method-assign]

        decision = await collab.resolve_by_vote(proposal, roles)
        assert decision.outcome == "approved"
        assert decision.method == "vote"

    @pytest.mark.asyncio
    async def test_voting_consensus_rejected(self) -> None:
        """Test voting consensus mechanism - rejected."""
        roles = [
            AgentRole(
                id="voter1",
                name="Voter 1",
                permissions={Permission.VOTE},
            ),
            AgentRole(
                id="voter2",
                name="Voter 2",
                permissions={Permission.VOTE},
            ),
        ]

        agents = {
            "voter1": MockAgent("voter1", "reject"),
            "voter2": MockAgent("voter2", "reject"),
        }

        config = FlowConfig(
            modality="collaboration",
            consensus_threshold=0.67,
            conflict_strategy="vote",
        )

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        proposal = Proposal(
            id="test_prop",
            title="Test",
            proposed_by="voter1",
        )

        async def mock_get_vote(voter, prop):
            return Vote(
                voter_id=voter.id,
                voter_role=voter.name,
                proposal_id=prop.id,
                choice="reject",
                weight=1.0,
            )

        collab._get_vote = mock_get_vote  # type: ignore[method-assign]

        decision = await collab.resolve_by_vote(proposal, roles)
        assert decision.outcome == "rejected"
        assert decision.method == "vote"

    @pytest.mark.asyncio
    async def test_moderator_decision(self) -> None:
        """Test moderator decision mechanism."""
        moderator_role = AgentRole(
            id="moderator",
            name="Moderator",
            permissions={Permission.MODERATE, Permission.DECIDE},
        )

        # Mock moderator that approves
        moderator_agent = MockAgent(
            "moderator",
            {"outcome": "approved", "reasoning": "Looks good"},
        )

        agents = {"moderator": moderator_agent}

        config = FlowConfig(
            modality="collaboration",
            moderator_id="moderator",
            conflict_strategy="moderator",
        )

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, [moderator_role], config)  # type: ignore[arg-type]

        proposal = Proposal(
            id="test_prop",
            title="Test",
            proposed_by="agent1",
        )

        decision = await collab.resolve_by_moderator(proposal, [])
        assert decision.outcome == "approved"
        assert decision.method == "moderator"
        assert decision.reasoning == "Looks good"


# ============================================================================
# Test Collaboration Flow
# ============================================================================


class TestCollaborationFlow:
    """Test full collaboration flow."""

    @pytest.mark.asyncio
    async def test_collaboration_start(self) -> None:
        """Test starting collaboration."""
        roles = [
            AgentRole(id="agent1", name="Agent 1", permissions={Permission.POST}),
        ]
        agents = {"agent1": MockAgent("agent1", "response")}
        config = FlowConfig(modality="collaboration")

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        await collab.start("Test problem")
        assert collab.blackboard is not None
        assert collab.blackboard.problem == "Test problem"

    @pytest.mark.asyncio
    async def test_run_round_basic(self) -> None:
        """Test running a basic contribution round."""
        roles = [
            AgentRole(
                id="agent1",
                name="Agent 1",
                permissions={Permission.POST, Permission.READ_ALL},
            ),
        ]
        agents = {"agent1": MockAgent("agent1", "My contribution")}
        config = FlowConfig(modality="collaboration")

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        await collab.start("Test problem")

        contributions = []
        async for contrib in collab.run_round():
            contributions.append(contrib)

        assert len(contributions) == 1
        assert contributions[0].content == "My contribution"
        assert contributions[0].agent_id == "agent1"
        assert collab.blackboard is not None
        assert collab.blackboard.current_round == 1

    @pytest.mark.asyncio
    async def test_run_round_multiple_agents(self) -> None:
        """Test round with multiple agents."""
        roles = [
            AgentRole(
                id="agent1",
                name="Agent 1",
                permissions={Permission.POST, Permission.READ_ALL},
                priority=1,
            ),
            AgentRole(
                id="agent2",
                name="Agent 2",
                permissions={Permission.POST, Permission.READ_ALL},
                priority=2,
            ),
        ]
        agents = {
            "agent1": MockAgent("agent1", "First contribution"),
            "agent2": MockAgent("agent2", "Second contribution"),
        }
        config = FlowConfig(modality="collaboration")

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        await collab.start("Test problem")

        contributions = []
        async for contrib in collab.run_round():
            contributions.append(contrib)

        assert len(contributions) == 2
        assert contributions[0].agent_id == "agent1"
        assert contributions[1].agent_id == "agent2"

    @pytest.mark.asyncio
    async def test_round_limit_enforcement(self) -> None:
        """Test that round limits are enforced."""
        roles = [
            AgentRole(
                id="agent1",
                name="Agent 1",
                permissions={Permission.POST, Permission.READ_ALL},
            ),
            AgentRole(
                id="agent2",
                name="Agent 2",
                permissions={Permission.POST, Permission.READ_ALL},
            ),
        ]
        agents = {
            "agent1": MockAgent("agent1", "contrib1"),
            "agent2": MockAgent("agent2", "contrib2"),
        }
        config = FlowConfig(
            modality="collaboration",
            max_contributions_per_round=1,  # Only 1 per round
        )

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        await collab.start("Test problem")

        contributions = []
        async for contrib in collab.run_round():
            contributions.append(contrib)

        # Should only get 1 contribution (limit)
        assert len(contributions) == 1

    @pytest.mark.asyncio
    async def test_permissions_checking(self) -> None:
        """Test that permissions are checked."""
        roles = [
            AgentRole(
                id="agent1",
                name="Agent 1",
                permissions={Permission.READ_ALL},  # No POST permission
            ),
        ]
        agents = {"agent1": MockAgent("agent1", "contribution")}
        config = FlowConfig(modality="collaboration")

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        await collab.start("Test problem")

        contributions = []
        async for contrib in collab.run_round():
            contributions.append(contrib)

        # Should get no contributions (no POST permission)
        assert len(contributions) == 0

    @pytest.mark.asyncio
    async def test_contribution_type_handling(self) -> None:
        """Test handling different contribution types."""
        roles = [
            AgentRole(
                id="agent1",
                name="Agent 1",
                permissions={Permission.POST, Permission.READ_ALL},
            ),
        ]

        # Return a contribution with DECISION type
        contribution = Contribution(
            agent_id="agent1",
            agent_role="Agent 1",
            content="Final decision",
            contribution_type=ContributionType.DECISION,
            confidence=0.9,
            round=1,
        )
        agents = {"agent1": MockAgent("agent1", contribution)}
        config = FlowConfig(modality="collaboration")

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        await collab.start("Test problem")

        contributions = []
        async for contrib in collab.run_round():
            contributions.append(contrib)

        # Should have created a proposal
        assert len(contributions) == 1
        assert collab.blackboard is not None
        assert len(collab.blackboard.proposals) == 1

    @pytest.mark.asyncio
    async def test_harvest(self) -> None:
        """Test harvesting results."""
        roles = [
            AgentRole(
                id="agent1",
                name="Agent 1",
                permissions={Permission.POST, Permission.READ_ALL, Permission.DECIDE},
            ),
        ]
        agents = {"agent1": MockAgent("agent1", "contribution")}
        config = FlowConfig(modality="collaboration")

        flow_agent: Any = Flow.lift_multi(agents, config)  # type: ignore[arg-type]
        collab = CollaborationFlow(flow_agent, agents, roles, config)  # type: ignore[arg-type]

        await collab.start("Test problem")

        # Run a round
        async for _ in collab.run_round():
            pass

        # Harvest results
        result = await collab.harvest()
        assert result.problem == "Test problem"
        assert result.rounds_completed == 1
        assert len(result.contributions) == 1
