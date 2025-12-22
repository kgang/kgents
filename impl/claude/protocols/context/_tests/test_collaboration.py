"""
Tests for Collaboration Protocol: Turn-taking and agent proposals.

Phase 4C: Agent Collaboration Layer.

Verifies:
- Keystroke tracking and grace period
- Agent turn-taking logic
- Proposal creation and lifecycle
- Auto-accept timing
- Callback invocation
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

import pytest

from protocols.context.collaboration import (
    AUTO_ACCEPT_DELAY,
    PROPOSAL_COOLDOWN,
    TYPING_GRACE_PERIOD,
    CollaborationProtocol,
    KeystrokeTracker,
    ProposalStatus,
    ProposedEdit,
    TurnState,
    get_collaboration_protocol,
    reset_collaboration_protocol,
)

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    """Reset singleton before each test."""
    reset_collaboration_protocol()


@pytest.fixture
def protocol() -> CollaborationProtocol:
    """Create a fresh protocol for each test."""
    return CollaborationProtocol()


@pytest.fixture
def tracker() -> KeystrokeTracker:
    """Create a fresh keystroke tracker."""
    return KeystrokeTracker()


# =============================================================================
# KeystrokeTracker Tests
# =============================================================================


class TestKeystrokeTracker:
    """Tests for keystroke tracking."""

    @pytest.mark.asyncio
    async def test_no_keystrokes_means_not_typing(self, tracker: KeystrokeTracker) -> None:
        """Without keystrokes, is_human_typing returns False."""
        assert await tracker.is_human_typing() is False
        assert await tracker.is_human_typing("/path/to/file") is False

    @pytest.mark.asyncio
    async def test_recent_keystroke_means_typing(self, tracker: KeystrokeTracker) -> None:
        """Recent keystroke means human is typing."""
        await tracker.record_keystroke("/path/to/file.py")
        assert await tracker.is_human_typing() is True
        assert await tracker.is_human_typing("/path/to/file.py") is True

    @pytest.mark.asyncio
    async def test_location_specific_typing(self, tracker: KeystrokeTracker) -> None:
        """Typing at one location doesn't affect another."""
        await tracker.record_keystroke("/file1.py")

        assert await tracker.is_human_typing("/file1.py") is True
        assert await tracker.is_human_typing("/file2.py") is False

    @pytest.mark.asyncio
    async def test_get_active_locations(self, tracker: KeystrokeTracker) -> None:
        """Should return all locations with recent keystrokes."""
        await tracker.record_keystroke("/file1.py")
        await tracker.record_keystroke("/file2.py")

        locations = await tracker.get_active_locations()
        assert "/file1.py" in locations
        assert "/file2.py" in locations

    @pytest.mark.asyncio
    async def test_clear_stale_removes_old_entries(self, tracker: KeystrokeTracker) -> None:
        """clear_stale removes entries older than 2x grace period."""
        # Record keystroke
        await tracker.record_keystroke("/old_file.py")

        # Manually make it old
        async with tracker._lock:
            tracker.typing_locations["/old_file.py"] = datetime.now() - timedelta(seconds=10)

        cleared = await tracker.clear_stale()
        assert cleared == 1
        assert "/old_file.py" not in tracker.typing_locations


# =============================================================================
# ProposedEdit Tests
# =============================================================================


class TestProposedEdit:
    """Tests for ProposedEdit dataclass."""

    def test_auto_accept_at_computed_correctly(self) -> None:
        """auto_accept_at should be created_at + AUTO_ACCEPT_DELAY."""
        proposal = ProposedEdit(
            id="test-1",
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )

        expected = proposal.created_at + AUTO_ACCEPT_DELAY
        assert proposal.auto_accept_at == expected

    def test_time_remaining_positive(self) -> None:
        """time_remaining should be positive for new proposal."""
        proposal = ProposedEdit(
            id="test-2",
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )

        assert proposal.time_remaining > timedelta(0)
        assert proposal.time_remaining <= AUTO_ACCEPT_DELAY

    def test_should_auto_accept_false_initially(self) -> None:
        """New proposal should not auto-accept."""
        proposal = ProposedEdit(
            id="test-3",
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )

        assert proposal.should_auto_accept is False

    def test_accept_changes_status(self) -> None:
        """accept() should change status to ACCEPTED."""
        proposal = ProposedEdit(
            id="test-4",
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )

        proposal.accept()
        assert proposal.status == ProposalStatus.ACCEPTED
        assert proposal.resolved_at is not None

    def test_reject_changes_status(self) -> None:
        """reject() should change status to REJECTED."""
        proposal = ProposedEdit(
            id="test-5",
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )

        proposal.reject()
        assert proposal.status == ProposalStatus.REJECTED
        assert proposal.resolved_at is not None

    def test_to_dict_serialization(self) -> None:
        """to_dict should serialize all fields."""
        proposal = ProposedEdit(
            id="test-6",
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old code",
            proposed="new code",
            description="Refactoring",
        )

        data = proposal.to_dict()
        assert data["id"] == "test-6"
        assert data["agent_id"] == "k-gent"
        assert data["location"] == "/file.py"
        assert data["status"] == "pending"
        assert "auto_accept_at" in data
        assert "time_remaining_ms" in data


# =============================================================================
# CollaborationProtocol Tests
# =============================================================================


class TestCollaborationProtocol:
    """Tests for CollaborationProtocol."""

    @pytest.mark.asyncio
    async def test_agent_can_edit_when_idle(self, protocol: CollaborationProtocol) -> None:
        """Agent can edit when human is not typing."""
        can_edit = await protocol.agent_can_edit("k-gent", "/file.py")
        assert can_edit is True

    @pytest.mark.asyncio
    async def test_agent_waits_for_human_typing(self, protocol: CollaborationProtocol) -> None:
        """Agent cannot edit when human is typing."""
        await protocol.record_keystroke("/file.py")
        can_edit = await protocol.agent_can_edit("k-gent", "/file.py")
        assert can_edit is False

    @pytest.mark.asyncio
    async def test_typing_grace_period(self, protocol: CollaborationProtocol) -> None:
        """Agent waits for grace period after last keystroke."""
        await protocol.record_keystroke("/file.py")

        # Immediately after - should wait
        assert await protocol.agent_can_edit("k-gent", "/file.py") is False

        # This test would need time manipulation for full coverage
        # For now, we verify the grace period constant exists
        assert TYPING_GRACE_PERIOD.total_seconds() == 2.0

    @pytest.mark.asyncio
    async def test_propose_edit_creates_proposal(self, protocol: CollaborationProtocol) -> None:
        """propose_edit should create and return a proposal."""
        proposal = await protocol.propose_edit(
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )

        assert proposal is not None
        assert proposal.agent_id == "k-gent"
        assert proposal.status == ProposalStatus.PENDING

    @pytest.mark.asyncio
    async def test_proposal_cooldown(self, protocol: CollaborationProtocol) -> None:
        """Agent cannot propose twice within cooldown period."""
        # First proposal succeeds
        p1 = await protocol.propose_edit(
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file1.py",
            original="old1",
            proposed="new1",
            description="Edit 1",
        )
        assert p1 is not None

        # Second proposal within cooldown fails
        p2 = await protocol.propose_edit(
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file2.py",
            original="old2",
            proposed="new2",
            description="Edit 2",
        )
        assert p2 is None

    @pytest.mark.asyncio
    async def test_accept_proposal(self, protocol: CollaborationProtocol) -> None:
        """accept_proposal should change status."""
        proposal = await protocol.propose_edit(
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )
        assert proposal is not None

        result = await protocol.accept_proposal(proposal.id)
        assert result is not None
        assert result.status == ProposalStatus.ACCEPTED

    @pytest.mark.asyncio
    async def test_reject_proposal(self, protocol: CollaborationProtocol) -> None:
        """reject_proposal should change status."""
        proposal = await protocol.propose_edit(
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )
        assert proposal is not None

        result = await protocol.reject_proposal(proposal.id)
        assert result is not None
        assert result.status == ProposalStatus.REJECTED

    @pytest.mark.asyncio
    async def test_get_pending_proposals(self, protocol: CollaborationProtocol) -> None:
        """get_pending_proposals returns only pending ones."""
        p1 = await protocol.propose_edit(
            agent_id="agent-1",
            agent_name="Agent 1",
            location="/file1.py",
            original="old1",
            proposed="new1",
            description="Edit 1",
        )
        assert p1 is not None

        # Accept one
        await protocol.accept_proposal(p1.id)

        # Check pending (should be empty after accept)
        pending = await protocol.get_pending_proposals()
        assert p1 not in pending

    @pytest.mark.asyncio
    async def test_callbacks_on_accept(self, protocol: CollaborationProtocol) -> None:
        """on_accept callback should be called."""
        accepted_ids: list[str] = []

        async def on_accept(proposal: ProposedEdit) -> None:
            accepted_ids.append(proposal.id)

        protocol.on_accept(on_accept)

        proposal = await protocol.propose_edit(
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )
        assert proposal is not None

        await protocol.accept_proposal(proposal.id)
        assert proposal.id in accepted_ids

    @pytest.mark.asyncio
    async def test_callbacks_on_reject(self, protocol: CollaborationProtocol) -> None:
        """on_reject callback should be called."""
        rejected_ids: list[str] = []

        async def on_reject(proposal: ProposedEdit) -> None:
            rejected_ids.append(proposal.id)

        protocol.on_reject(on_reject)

        proposal = await protocol.propose_edit(
            agent_id="k-gent",
            agent_name="K-gent",
            location="/file.py",
            original="old",
            proposed="new",
            description="Test edit",
        )
        assert proposal is not None

        await protocol.reject_proposal(proposal.id)
        assert proposal.id in rejected_ids


# =============================================================================
# Singleton Tests
# =============================================================================


class TestSingleton:
    """Tests for singleton pattern."""

    def test_get_returns_same_instance(self) -> None:
        """get_collaboration_protocol returns same instance."""
        p1 = get_collaboration_protocol()
        p2 = get_collaboration_protocol()
        assert p1 is p2

    def test_reset_creates_new_instance(self) -> None:
        """reset_collaboration_protocol creates new instance."""
        p1 = get_collaboration_protocol()
        reset_collaboration_protocol()
        p2 = get_collaboration_protocol()
        assert p1 is not p2


# =============================================================================
# Constants Tests
# =============================================================================


class TestConstants:
    """Tests for protocol constants."""

    def test_typing_grace_period_is_2_seconds(self) -> None:
        """TYPING_GRACE_PERIOD should be 2 seconds."""
        assert TYPING_GRACE_PERIOD == timedelta(seconds=2)

    def test_auto_accept_delay_is_5_seconds(self) -> None:
        """AUTO_ACCEPT_DELAY should be 5 seconds."""
        assert AUTO_ACCEPT_DELAY == timedelta(seconds=5)

    def test_proposal_cooldown_is_1_second(self) -> None:
        """PROPOSAL_COOLDOWN should be 1 second."""
        assert PROPOSAL_COOLDOWN == timedelta(seconds=1)
