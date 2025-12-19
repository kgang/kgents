"""
Tests for Commission Service.

Tests the commission workflow - the heart of the Metaphysical Forge.

See: spec/protocols/metaphysical-forge.md
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from services.forge.commission import (
    COMMISSION_TRANSITIONS,
    ArtisanOutput,
    ArtisanType,
    Commission,
    CommissionService,
    CommissionStatus,
)

# === Test Fixtures ===


@pytest.fixture
def mock_soul():
    """Create a mock KgentSoul."""
    soul = MagicMock()
    soul.eigenvectors = MagicMock()
    soul.eigenvectors.to_dict.return_value = {
        "curiosity": 0.8,
        "playfulness": 0.7,
        "precision": 0.6,
        "empathy": 0.9,
        "boldness": 0.75,
        "pragmatism": 0.5,
    }

    # Default: approve everything
    intercept_result = MagicMock()
    intercept_result.recommendation = "allow"
    intercept_result.annotation = "Looks good!"
    intercept_result.matching_principles = []
    soul.intercept = AsyncMock(return_value=intercept_result)

    return soul


@pytest.fixture
def service():
    """Create a CommissionService without soul (auto-approve mode)."""
    return CommissionService(kgent_soul=None)


@pytest.fixture
def governed_service(mock_soul):
    """Create a CommissionService with K-gent governance."""
    return CommissionService(kgent_soul=mock_soul)


# === Commission Creation Tests ===


class TestCommissionCreation:
    """Test commission creation."""

    @pytest.mark.asyncio
    async def test_create_commission(self, service):
        """Test creating a basic commission."""
        commission = await service.create(
            intent="Build an agent that manages user preferences",
        )

        assert commission.id.startswith("commission-")
        assert commission.intent == "Build an agent that manages user preferences"
        assert commission.name is None
        assert commission.status == CommissionStatus.PENDING
        assert commission.soul_approved is False
        assert commission.paused is False

    @pytest.mark.asyncio
    async def test_create_commission_with_name(self, service):
        """Test creating a commission with a name."""
        commission = await service.create(
            intent="Build a preference manager",
            name="PreferenceAgent",
        )

        assert commission.name == "PreferenceAgent"

    @pytest.mark.asyncio
    async def test_commission_timestamps(self, service):
        """Test that commissions have proper timestamps."""
        commission = await service.create(intent="Test agent")

        assert commission.created_at is not None
        assert commission.updated_at is not None
        assert commission.created_at <= commission.updated_at


# === Commission Retrieval Tests ===


class TestCommissionRetrieval:
    """Test commission retrieval operations."""

    @pytest.mark.asyncio
    async def test_get_commission(self, service):
        """Test getting a commission by ID."""
        created = await service.create(intent="Test agent")
        retrieved = await service.get(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.intent == created.intent

    @pytest.mark.asyncio
    async def test_get_nonexistent_commission(self, service):
        """Test getting a commission that doesn't exist."""
        result = await service.get("nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_commissions(self, service):
        """Test listing commissions."""
        await service.create(intent="Agent 1")
        await service.create(intent="Agent 2")
        await service.create(intent="Agent 3")

        commissions = await service.list()
        assert len(commissions) == 3

    @pytest.mark.asyncio
    async def test_list_commissions_with_status_filter(self, service):
        """Test filtering commissions by status."""
        c1 = await service.create(intent="Agent 1")
        await service.create(intent="Agent 2")

        # Start one to change its status
        await service.start_review(c1.id)

        pending = await service.list(status=CommissionStatus.PENDING)
        assert len(pending) == 1  # Only Agent 2 is pending

        designing = await service.list(status=CommissionStatus.DESIGNING)
        assert len(designing) == 1  # Agent 1 is now designing


# === K-gent Review Tests ===


class TestKgentReview:
    """Test K-gent governance in commission workflow."""

    @pytest.mark.asyncio
    async def test_start_review_without_soul(self, service):
        """Test starting review without K-gent (auto-approve)."""
        commission = await service.create(intent="Test agent")
        reviewed = await service.start_review(commission.id)

        assert reviewed is not None
        assert reviewed.status == CommissionStatus.DESIGNING
        assert reviewed.soul_approved is True
        assert reviewed.soul_annotation == "K-gent not configured - auto-approved"

    @pytest.mark.asyncio
    async def test_start_review_with_approval(self, governed_service, mock_soul):
        """Test K-gent approving a commission."""
        commission = await governed_service.create(intent="Build a preference manager")
        reviewed = await governed_service.start_review(commission.id)

        assert reviewed.status == CommissionStatus.DESIGNING
        assert reviewed.soul_approved is True
        assert reviewed.soul_annotation == "Looks good!"
        mock_soul.intercept.assert_called_once()

    @pytest.mark.asyncio
    async def test_start_review_with_rejection(self, governed_service, mock_soul):
        """Test K-gent rejecting a commission."""
        # Configure soul to reject
        mock_soul.intercept.return_value.recommendation = "escalate"
        mock_soul.intercept.return_value.annotation = "This violates privacy principles"

        commission = await governed_service.create(intent="Build a surveillance agent")
        reviewed = await governed_service.start_review(commission.id)

        assert reviewed.status == CommissionStatus.REJECTED
        assert reviewed.soul_approved is False
        assert "privacy principles" in reviewed.soul_annotation

    @pytest.mark.asyncio
    async def test_start_review_with_soul_error(self, governed_service, mock_soul):
        """Test graceful degradation when K-gent fails."""
        mock_soul.intercept.side_effect = Exception("Soul connection failed")

        commission = await governed_service.create(intent="Test agent")
        reviewed = await governed_service.start_review(commission.id)

        # Should proceed anyway (graceful degradation)
        assert reviewed.status == CommissionStatus.DESIGNING
        assert reviewed.soul_approved is True
        assert "K-gent review skipped" in reviewed.soul_annotation


# === Commission Advancement Tests ===


class TestCommissionAdvancement:
    """Test advancing commissions through artisan stages."""

    @pytest.mark.asyncio
    async def test_advance_through_stages(self, service):
        """Test advancing a commission through all stages."""
        commission = await service.create(intent="Test agent")
        await service.start_review(commission.id)

        # Advance through each stage
        expected_stages = [
            (CommissionStatus.DESIGNING, ArtisanType.ARCHITECT, CommissionStatus.IMPLEMENTING),
            (CommissionStatus.IMPLEMENTING, ArtisanType.SMITH, CommissionStatus.EXPOSING),
            (CommissionStatus.EXPOSING, ArtisanType.HERALD, CommissionStatus.PROJECTING),
            (CommissionStatus.PROJECTING, ArtisanType.PROJECTOR, CommissionStatus.SECURING),
            (CommissionStatus.SECURING, ArtisanType.SENTINEL, CommissionStatus.VERIFYING),
            (CommissionStatus.VERIFYING, ArtisanType.WITNESS, CommissionStatus.REVIEWING),
            (CommissionStatus.REVIEWING, ArtisanType.KGENT, CommissionStatus.COMPLETE),
        ]

        for from_status, artisan, to_status in expected_stages:
            commission = await service.get(commission.id)
            assert commission.status == from_status

            commission = await service.advance(commission.id)
            assert commission.status == to_status
            assert artisan.value in commission.artisan_outputs

    @pytest.mark.asyncio
    async def test_cannot_advance_pending(self, service):
        """Test that PENDING commissions cannot be advanced directly."""
        commission = await service.create(intent="Test agent")

        # Should not be able to advance without starting
        result = await service.advance(commission.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_cannot_advance_complete(self, service):
        """Test that COMPLETE commissions cannot be advanced."""
        commission = await service.create(intent="Test agent")
        await service.start_review(commission.id)

        # Advance to complete
        for _ in range(7):  # 7 advancement stages
            commission = await service.advance(commission.id)

        assert commission.status == CommissionStatus.COMPLETE

        # Should not be able to advance further
        result = await service.advance(commission.id)
        assert result is None


# === Intervention Tests ===


class TestCommissionInterventions:
    """Test commission pause/resume/cancel interventions."""

    @pytest.mark.asyncio
    async def test_pause_commission(self, service):
        """Test pausing a commission."""
        commission = await service.create(intent="Test agent")
        await service.start_review(commission.id)

        paused = await service.pause(commission.id)
        assert paused.paused is True
        assert len(paused.interventions) == 1
        assert paused.interventions[0]["type"] == "pause"

    @pytest.mark.asyncio
    async def test_resume_commission(self, service):
        """Test resuming a paused commission."""
        commission = await service.create(intent="Test agent")
        await service.start_review(commission.id)
        await service.pause(commission.id)

        resumed = await service.resume(commission.id)
        assert resumed.paused is False
        assert len(resumed.interventions) == 2
        assert resumed.interventions[1]["type"] == "resume"

    @pytest.mark.asyncio
    async def test_cannot_advance_paused(self, service):
        """Test that paused commissions cannot be advanced."""
        commission = await service.create(intent="Test agent")
        await service.start_review(commission.id)
        await service.pause(commission.id)

        result = await service.advance(commission.id)
        assert result is None

    @pytest.mark.asyncio
    async def test_cancel_commission(self, service):
        """Test cancelling a commission."""
        commission = await service.create(intent="Test agent")
        await service.start_review(commission.id)

        success = await service.cancel(commission.id, reason="Changed my mind")
        assert success is True

        commission = await service.get(commission.id)
        assert commission.status == CommissionStatus.REJECTED
        assert commission.interventions[-1]["type"] == "cancel"
        assert commission.interventions[-1]["reason"] == "Changed my mind"

    @pytest.mark.asyncio
    async def test_cannot_cancel_complete(self, service):
        """Test that completed commissions cannot be cancelled."""
        commission = await service.create(intent="Test agent")
        await service.start_review(commission.id)

        # Advance to complete
        for _ in range(7):
            await service.advance(commission.id)

        success = await service.cancel(commission.id)
        assert success is False


# === State Machine Tests ===


class TestCommissionStateMachine:
    """Test commission state transitions."""

    def test_valid_transitions(self):
        """Test that valid transitions are defined correctly."""
        # PENDING can go to DESIGNING or REJECTED
        assert CommissionStatus.DESIGNING in COMMISSION_TRANSITIONS[CommissionStatus.PENDING]
        assert CommissionStatus.REJECTED in COMMISSION_TRANSITIONS[CommissionStatus.PENDING]

        # Terminal states have no transitions
        assert COMMISSION_TRANSITIONS[CommissionStatus.COMPLETE] == []
        assert COMMISSION_TRANSITIONS[CommissionStatus.REJECTED] == []
        assert COMMISSION_TRANSITIONS[CommissionStatus.FAILED] == []

    def test_all_statuses_have_transitions(self):
        """Test that all statuses have transition definitions."""
        for status in CommissionStatus:
            assert status in COMMISSION_TRANSITIONS


# === Serialization Tests ===


class TestCommissionSerialization:
    """Test commission serialization."""

    @pytest.mark.asyncio
    async def test_commission_to_dict(self, service):
        """Test commission serialization to dict."""
        commission = await service.create(intent="Test agent", name="TestAgent")
        await service.start_review(commission.id)

        data = commission.to_dict()

        assert data["id"] == commission.id
        assert data["intent"] == "Test agent"
        assert data["name"] == "TestAgent"
        assert data["status"] == "designing"
        assert "created_at" in data
        assert "artisan_outputs" in data

    @pytest.mark.asyncio
    async def test_artisan_output_serialization(self, service):
        """Test artisan output serialization."""
        commission = await service.create(intent="Test agent")
        await service.start_review(commission.id)
        await service.advance(commission.id)

        data = commission.to_dict()
        architect_output = data["artisan_outputs"].get("architect")

        assert architect_output is not None
        assert architect_output["artisan"] == "architect"
        assert architect_output["status"] == "complete"
