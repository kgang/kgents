"""
Tests for CoalitionPersistence - Agent collaboration with voting persistence.

Verifies:
- Coalition CRUD operations (forge, dissolve)
- Member management (join, leave)
- Proposal workflow (propose, start_voting, vote, conclude)
- Output creation
- Health manifest
"""

from dataclasses import dataclass
from unittest.mock import AsyncMock, MagicMock

import pytest


@pytest.fixture
def mock_session():
    """Create a mock async session."""
    session = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.get = AsyncMock(return_value=None)
    session.execute = AsyncMock()
    return session


@pytest.fixture
def mock_session_factory(mock_session):
    """Create a mock session factory."""
    factory = AsyncMock()
    factory.__aenter__ = AsyncMock(return_value=mock_session)
    factory.__aexit__ = AsyncMock(return_value=None)
    return MagicMock(return_value=factory)


@pytest.fixture
def mock_dgent():
    """Create a mock D-gent."""
    dgent = AsyncMock()
    dgent.put = AsyncMock(return_value="datum-123")
    dgent.get = AsyncMock(return_value=None)
    return dgent


@pytest.fixture
def mock_coalition_adapter(mock_session_factory):
    """Create a mock coalition adapter."""
    adapter = MagicMock()
    adapter.session_factory = mock_session_factory
    return adapter


@pytest.fixture
def mock_member_adapter(mock_session_factory):
    """Create a mock member adapter."""
    adapter = MagicMock()
    adapter.session_factory = mock_session_factory
    return adapter


class TestCoalitionPersistenceInit:
    """Test CoalitionPersistence initialization."""

    def test_init_stores_dependencies(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent
    ):
        """Should store adapters and dgent."""
        from services.coalition import CoalitionPersistence

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        assert persistence.coalitions is mock_coalition_adapter
        assert persistence.members is mock_member_adapter
        assert persistence.dgent is mock_dgent


class TestCoalitionManagement:
    """Test coalition CRUD operations."""

    @pytest.mark.asyncio
    async def test_forge_coalition(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should forge coalition with generated ID."""
        from services.coalition import CoalitionPersistence

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.forge(
            name="Feature Team",
            goal="Ship feature X by Q1",
            description="Cross-functional team",
            consensus_threshold=0.75,
        )

        assert result.name == "Feature Team"
        assert result.goal == "Ship feature X by Q1"
        assert result.status == "forming"
        assert result.consensus_threshold == 0.75
        assert result.id.startswith("coalition-")

    @pytest.mark.asyncio
    async def test_dissolve_coalition(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should dissolve coalition and deactivate members."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockCoalition:
            id: str = "coalition-123"
            status: str = "active"
            dissolved_at = None

        @dataclass
        class MockMember:
            id: str = "member-1"
            is_active: bool = True
            left_at = None

        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = [MockMember()]
        mock_session.get = AsyncMock(return_value=MockCoalition())
        mock_session.execute = AsyncMock(return_value=mock_result)

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.dissolve("coalition-123")

        assert result is True


class TestMemberManagement:
    """Test coalition member operations."""

    @pytest.mark.asyncio
    async def test_join_coalition(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should add member to forming coalition."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockCoalition:
            id: str = "coalition-123"
            status: str = "forming"
            min_members: int = 2
            max_members: int | None = None

        mock_count = MagicMock()
        mock_count.scalar.return_value = 0
        mock_session.get = AsyncMock(return_value=MockCoalition())
        mock_session.execute = AsyncMock(return_value=mock_count)

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.join(
            coalition_id="coalition-123",
            agent_name="Alice",
            agent_type="citizen",
            role="member",
            voting_power=1.0,
        )

        assert result is not None
        assert result.agent_name == "Alice"
        assert result.role == "member"
        assert result.id.startswith("member-")

    @pytest.mark.asyncio
    async def test_join_dissolved_coalition(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should reject joining dissolved coalition."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockCoalition:
            id: str = "coalition-123"
            status: str = "dissolved"
            max_members: int | None = None

        mock_session.get = AsyncMock(return_value=MockCoalition())

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.join(
            coalition_id="coalition-123",
            agent_name="Alice",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_leave_coalition(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should mark member as inactive."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockMember:
            id: str = "member-123"
            is_active: bool = True
            left_at = None

        mock_session.get = AsyncMock(return_value=MockMember())

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.leave("member-123")

        assert result is True


class TestProposalWorkflow:
    """Test proposal operations."""

    @pytest.mark.asyncio
    async def test_propose(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should create proposal and store in D-gent."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockCoalition:
            id: str = "coalition-123"
            status: str = "active"
            proposal_count: int = 0

        @dataclass
        class MockMember:
            id: str = "member-123"
            agent_name: str = "Alice"
            is_active: bool = True
            can_propose: bool = True

        mock_session.get = AsyncMock(side_effect=[MockCoalition(), MockMember()])

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.propose(
            coalition_id="coalition-123",
            proposer_id="member-123",
            title="Add new feature",
            description="Implement dark mode",
            proposal_type="action",
        )

        assert result is not None
        assert result.title == "Add new feature"
        assert result.status == "draft"
        assert result.proposer_name == "Alice"
        mock_dgent.put.assert_called_once()

    @pytest.mark.asyncio
    async def test_propose_inactive_coalition(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should reject proposal to inactive coalition."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockCoalition:
            id: str = "coalition-123"
            status: str = "forming"  # Not active

        mock_session.get = AsyncMock(return_value=MockCoalition())

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.propose(
            coalition_id="coalition-123",
            proposer_id="member-123",
            title="Test",
            description="Test",
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_start_voting(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should transition proposal to voting status."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockProposal:
            id: str = "proposal-123"
            status: str = "draft"
            voting_started_at = None

        mock_session.get = AsyncMock(return_value=MockProposal())

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.start_voting("proposal-123")

        assert result is True

    @pytest.mark.asyncio
    async def test_vote(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should record vote and update counts."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockProposal:
            id: str = "proposal-123"
            coalition_id: str = "coalition-123"
            status: str = "voting"
            votes_for: int = 0
            votes_against: int = 0
            votes_abstain: int = 0
            approval_score: float | None = None
            created_at = None

        @dataclass
        class MockMember:
            id: str = "member-123"
            coalition_id: str = "coalition-123"
            agent_name: str = "Alice"
            is_active: bool = True
            can_vote: bool = True
            voting_power: float = 1.0

        mock_existing = MagicMock()
        mock_existing.scalar_one_or_none.return_value = None

        mock_session.get = AsyncMock(side_effect=[MockProposal(), MockMember()])
        mock_session.execute = AsyncMock(return_value=mock_existing)

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.vote(
            proposal_id="proposal-123",
            member_id="member-123",
            vote="for",
            rationale="Good idea",
        )

        assert result is not None
        assert result.vote == "for"
        assert result.member_name == "Alice"


class TestOutputManagement:
    """Test output creation operations."""

    @pytest.mark.asyncio
    async def test_create_output(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should create output and store in D-gent."""
        from services.coalition import CoalitionPersistence

        @dataclass
        class MockCoalition:
            id: str = "coalition-123"
            status: str = "active"

        mock_session.get = AsyncMock(return_value=MockCoalition())

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.create_output(
            coalition_id="coalition-123",
            output_type="decision",
            title="Feature approved",
            content="Dark mode will be implemented",
            contributor_ids=["member-1", "member-2"],
        )

        assert result is not None
        assert result.title == "Feature approved"
        assert result.output_type == "decision"
        assert len(result.contributor_ids) == 2
        mock_dgent.put.assert_called_once()


class TestCoalitionManifest:
    """Test manifest (health status) operation."""

    @pytest.mark.asyncio
    async def test_manifest_returns_status(
        self, mock_coalition_adapter, mock_member_adapter, mock_dgent, mock_session
    ):
        """Should return coalition landscape status."""
        from services.coalition import CoalitionPersistence

        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        mock_session.execute = AsyncMock(return_value=mock_result)

        persistence = CoalitionPersistence(
            coalition_adapter=mock_coalition_adapter,
            member_adapter=mock_member_adapter,
            dgent=mock_dgent,
        )

        result = await persistence.manifest()

        assert hasattr(result, "total_coalitions")
        assert hasattr(result, "active_coalitions")
        assert hasattr(result, "total_members")
        assert hasattr(result, "total_proposals")
        assert hasattr(result, "total_outputs")


class TestViewDataclasses:
    """Test view dataclasses."""

    def test_coalition_view_fields(self):
        """CoalitionView should have expected fields."""
        from services.coalition import CoalitionView

        view = CoalitionView(
            id="test",
            name="Test",
            goal="Test goal",
            description=None,
            status="forming",
            member_count=0,
            proposal_count=0,
            output_count=0,
            consensus_threshold=0.66,
            formed_at=None,
            created_at="",
        )

        assert view.status == "forming"
        assert view.consensus_threshold == 0.66

    def test_member_view_fields(self):
        """MemberView should have expected fields."""
        from services.coalition import MemberView

        view = MemberView(
            id="test",
            coalition_id="coalition",
            agent_id="agent",
            agent_name="Alice",
            agent_type="citizen",
            role="member",
            voting_power=1.0,
            is_active=True,
            contribution_count=0,
            joined_at="",
        )

        assert view.role == "member"
        assert view.voting_power == 1.0

    def test_proposal_view_fields(self):
        """ProposalView should have expected fields."""
        from services.coalition import ProposalView

        view = ProposalView(
            id="test",
            coalition_id="coalition",
            proposer_name="Alice",
            title="Test",
            description="Test desc",
            proposal_type="action",
            status="draft",
            votes_for=0,
            votes_against=0,
            votes_abstain=0,
            approval_score=None,
            created_at="",
        )

        assert view.proposal_type == "action"
        assert view.status == "draft"

    def test_vote_view_fields(self):
        """VoteView should have expected fields."""
        from services.coalition import VoteView

        view = VoteView(
            id="test",
            proposal_id="proposal",
            member_name="Alice",
            vote="for",
            weight=1.0,
            rationale="Good idea",
            created_at="",
        )

        assert view.vote == "for"
        assert view.weight == 1.0

    def test_output_view_fields(self):
        """OutputView should have expected fields."""
        from services.coalition import OutputView

        view = OutputView(
            id="test",
            coalition_id="coalition",
            output_type="decision",
            title="Test",
            content="Content",
            contributor_ids=["member-1"],
            created_at="",
        )

        assert view.output_type == "decision"
        assert len(view.contributor_ids) == 1
