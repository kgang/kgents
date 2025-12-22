"""
Tests for self.collaboration AGENTESE node.

Phase 5C: Collaborative Editing

Verifies the AGENTESE node correctly exposes:
- self.collaboration.manifest - Collaboration status
- self.collaboration.propose - Create proposals
- self.collaboration.respond - Accept/reject proposals
- self.collaboration.keystroke - Record keystrokes
- self.collaboration.pending - Get pending proposals
- self.collaboration.status - Get turn state
"""

import pytest
from datetime import datetime, timedelta

from protocols.agentese.contexts.self_collaboration import (
    CollaborationNode,
    COLLABORATION_AFFORDANCES,
)
from protocols.context.collaboration import (
    get_collaboration_protocol,
    reset_collaboration_protocol,
)


# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def collaboration_node():
    """Create a fresh collaboration node."""
    reset_collaboration_protocol()
    node = CollaborationNode()
    return node


@pytest.fixture
def mock_observer():
    """Create a minimal mock observer."""
    class MockObserver:
        pass
    return MockObserver()


# =============================================================================
# Registration Tests
# =============================================================================


class TestRegistration:
    """Test node registration."""

    def test_affordances_declared(self, collaboration_node):
        """Should declare all expected affordances.

        Note: affordances() is a METHOD on BaseLogosNode that combines
        _base_affordances with _get_affordances_for_archetype().
        COLLABORATION_AFFORDANCES should be a subset of the result.
        """
        from protocols.agentese.node import AgentMeta

        observer = AgentMeta(name="test", archetype="developer")
        all_affordances = collaboration_node.affordances(observer)

        # Collaboration affordances should be included
        for aff in COLLABORATION_AFFORDANCES:
            assert aff in all_affordances, f"Missing affordance: {aff}"

        # Base affordances should also be present
        assert "manifest" in all_affordances
        assert "witness" in all_affordances
        assert "help" in all_affordances

    def test_node_registered(self):
        """Should be registered in the AGENTESE registry."""
        from protocols.agentese.registry import get_registry
        from protocols.agentese.contexts import self_collaboration  # trigger import  # noqa: F401

        registry = get_registry()
        assert "self.collaboration" in registry._nodes


# =============================================================================
# Manifest Tests
# =============================================================================


class TestManifest:
    """Test manifest aspect."""

    @pytest.mark.asyncio
    async def test_manifest_returns_status(self, collaboration_node, mock_observer):
        """Manifest should return collaboration status."""
        result = await collaboration_node.manifest(mock_observer)

        assert result is not None
        assert result.summary == "Collaboration Protocol Active"
        assert "pending_count" in result.metadata
        assert "auto_accept_delay_ms" in result.metadata
        assert "features" in result.metadata


# =============================================================================
# Propose Tests
# =============================================================================


class TestPropose:
    """Test propose aspect."""

    @pytest.mark.asyncio
    async def test_propose_creates_proposal(self, collaboration_node, mock_observer):
        """Propose should create a new proposal."""
        result = await collaboration_node.propose(
            mock_observer,
            agent_id="test-agent",
            agent_name="Test Agent",
            location="test/file.py",
            original="old code",
            proposed="new code",
            description="Refactor function",
        )

        assert result is not None
        assert result.metadata["success"] is True
        assert result.metadata["proposal_id"] is not None

    @pytest.mark.asyncio
    async def test_propose_requires_location(self, collaboration_node, mock_observer):
        """Propose should fail without location."""
        result = await collaboration_node.propose(
            mock_observer,
            agent_id="test-agent",
            agent_name="Test Agent",
        )

        assert result.metadata["success"] is False
        assert "location" in result.metadata["error"]

    @pytest.mark.asyncio
    async def test_propose_blocked_while_typing(self, collaboration_node, mock_observer):
        """Propose should be blocked when human is typing."""
        # Record keystroke first
        await collaboration_node.keystroke(
            mock_observer,
            location="test/file.py",
        )

        # Try to propose - should be blocked
        result = await collaboration_node.propose(
            mock_observer,
            agent_id="test-agent",
            agent_name="Test Agent",
            location="test/file.py",
            description="Should be blocked",
        )

        assert result.metadata["success"] is False
        assert result.metadata["error"] == "human_typing"


# =============================================================================
# Respond Tests
# =============================================================================


class TestRespond:
    """Test respond aspect."""

    @pytest.mark.asyncio
    async def test_accept_proposal(self, collaboration_node, mock_observer):
        """Accept should mark proposal as accepted."""
        # Create proposal first
        propose_result = await collaboration_node.propose(
            mock_observer,
            agent_id="test-agent",
            agent_name="Test Agent",
            location="test/file.py",
            description="Test change",
        )
        proposal_id = propose_result.metadata["proposal_id"]

        # Accept it
        result = await collaboration_node.respond(
            mock_observer,
            proposal_id=proposal_id,
            action="accept",
        )

        assert result.metadata["success"] is True
        assert result.metadata["status"] == "accepted"

    @pytest.mark.asyncio
    async def test_reject_proposal(self, collaboration_node, mock_observer):
        """Reject should mark proposal as rejected."""
        # Create proposal first
        propose_result = await collaboration_node.propose(
            mock_observer,
            agent_id="test-agent",
            agent_name="Test Agent",
            location="test/file.py",
            description="Test change",
        )
        proposal_id = propose_result.metadata["proposal_id"]

        # Reject it
        result = await collaboration_node.respond(
            mock_observer,
            proposal_id=proposal_id,
            action="reject",
        )

        assert result.metadata["success"] is True
        assert result.metadata["status"] == "rejected"

    @pytest.mark.asyncio
    async def test_respond_requires_proposal_id(self, collaboration_node, mock_observer):
        """Respond should fail without proposal_id."""
        result = await collaboration_node.respond(
            mock_observer,
            action="accept",
        )

        assert result.metadata["success"] is False
        assert "proposal_id" in result.metadata["error"]

    @pytest.mark.asyncio
    async def test_respond_requires_valid_action(self, collaboration_node, mock_observer):
        """Respond should fail with invalid action."""
        result = await collaboration_node.respond(
            mock_observer,
            proposal_id="some-id",
            action="invalid",
        )

        assert result.metadata["success"] is False
        assert "accept" in result.metadata["error"]


# =============================================================================
# Keystroke Tests
# =============================================================================


class TestKeystroke:
    """Test keystroke aspect."""

    @pytest.mark.asyncio
    async def test_keystroke_recorded(self, collaboration_node, mock_observer):
        """Keystroke should be recorded."""
        result = await collaboration_node.keystroke(
            mock_observer,
            location="test/file.py",
        )

        assert result.metadata["recorded"] is True
        assert result.metadata["location"] == "test/file.py"

    @pytest.mark.asyncio
    async def test_keystroke_requires_location(self, collaboration_node, mock_observer):
        """Keystroke should fail without location."""
        result = await collaboration_node.keystroke(mock_observer)

        assert result.metadata["recorded"] is False


# =============================================================================
# Pending Tests
# =============================================================================


class TestPending:
    """Test pending aspect."""

    @pytest.mark.asyncio
    async def test_pending_empty_initially(self, collaboration_node, mock_observer):
        """Pending should return empty list initially."""
        result = await collaboration_node.pending(mock_observer)

        assert result.metadata["count"] == 0
        assert result.metadata["proposals"] == []

    @pytest.mark.asyncio
    async def test_pending_shows_proposals(self, collaboration_node, mock_observer):
        """Pending should show created proposals."""
        # Create proposal
        await collaboration_node.propose(
            mock_observer,
            agent_id="test-agent",
            agent_name="Test Agent",
            location="test/file.py",
            description="Test change",
        )

        # Check pending
        result = await collaboration_node.pending(mock_observer)

        assert result.metadata["count"] == 1
        assert len(result.metadata["proposals"]) == 1


# =============================================================================
# Status Tests
# =============================================================================


class TestStatus:
    """Test status aspect."""

    @pytest.mark.asyncio
    async def test_status_open_initially(self, collaboration_node, mock_observer):
        """Status should be 'open' initially."""
        result = await collaboration_node.status(mock_observer)

        assert result.metadata["turn_state"] == "open"
        assert result.metadata["is_human_typing"] is False
        assert result.metadata["pending_proposal_count"] == 0

    @pytest.mark.asyncio
    async def test_status_human_when_typing(self, collaboration_node, mock_observer):
        """Status should be 'human' when typing."""
        # Record keystroke
        await collaboration_node.keystroke(
            mock_observer,
            location="test/file.py",
        )

        result = await collaboration_node.status(mock_observer)

        assert result.metadata["turn_state"] == "human"
        assert result.metadata["is_human_typing"] is True

    @pytest.mark.asyncio
    async def test_status_agent_when_proposal_pending(self, collaboration_node, mock_observer):
        """Status should be 'agent' when proposal pending."""
        # Create proposal
        await collaboration_node.propose(
            mock_observer,
            agent_id="test-agent",
            agent_name="Test Agent",
            location="test/file.py",
            description="Test change",
        )

        result = await collaboration_node.status(mock_observer)

        assert result.metadata["turn_state"] == "agent"
        assert result.metadata["pending_proposal_count"] == 1
