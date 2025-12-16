"""
Tests for GrowthCortex - Bicameral Persistence Layer.

Tests cover:
- Proposal storage and retrieval
- Nursery holon lifecycle
- Rollback token management
- Budget persistence
- Schema initialization

AGENTESE: self.grow.* persistence tests
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from ..cortex import (
    GrowthCortex,
    _deserialize_holon,
    _deserialize_proposal,
    _deserialize_token,
    _serialize_holon,
    _serialize_proposal,
    _serialize_token,
    create_growth_cortex,
)
from ..schemas import (
    GerminatingHolon,
    GrowthBudget,
    HolonProposal,
    NurseryConfig,
    RollbackToken,
    ValidationResult,
)

# === Fixtures ===


@pytest.fixture
def sample_proposal() -> HolonProposal:
    """Create a sample proposal for testing."""
    return HolonProposal(
        proposal_id=str(uuid.uuid4()),
        entity="paperclip",
        context="world",
        version="0.1.0",
        why_exists="A paperclip exists for holding papers together.",
        proposed_by="kent",
        proposed_at=datetime.now(),
        affordances={
            "default": ["manifest", "witness"],
            "gardener": ["manifest", "witness", "bend"],
        },
        behaviors={
            "manifest": "Show the paperclip",
            "bend": "Bend into new shape",
        },
    )


@pytest.fixture
def sample_holon(sample_proposal: HolonProposal) -> GerminatingHolon:
    """Create a sample germinating holon for testing."""
    return GerminatingHolon(
        germination_id=str(uuid.uuid4()),
        proposal=sample_proposal,
        validation=ValidationResult(passed=True, scores={"tasteful": 0.8}),
        jit_source="# Generated code",
        jit_source_hash="abc123",
        usage_count=10,
        success_count=8,
        failure_patterns=["timeout"],
        germinated_at=datetime.now(),
        germinated_by="kent",
    )


@pytest.fixture
def sample_token() -> RollbackToken:
    """Create a sample rollback token for testing."""
    return RollbackToken.create(
        handle="world.paperclip",
        spec_path=Path("spec/world/paperclip.md"),
        impl_path=Path("impl/contexts/world/paperclip.py"),
        spec_content="# world.paperclip spec",
        impl_content="# world.paperclip impl",
    )


@pytest.fixture
def mock_relational() -> AsyncMock:
    """Create a mock relational store."""
    mock = AsyncMock()
    mock.execute = AsyncMock(return_value=1)
    mock.fetch_one = AsyncMock(return_value=None)
    mock.fetch_all = AsyncMock(return_value=[])
    return mock


# === Serialization Tests ===


class TestSerialization:
    """Tests for serialization/deserialization helpers."""

    def test_serialize_proposal(self, sample_proposal: HolonProposal) -> None:
        """Test proposal serialization."""
        data = _serialize_proposal(sample_proposal)

        assert data["proposal_id"] == sample_proposal.proposal_id
        assert data["entity"] == "paperclip"
        assert data["context"] == "world"
        assert data["why_exists"] == sample_proposal.why_exists
        assert data["affordances"] == sample_proposal.affordances
        assert "gap" in data  # Should be None (not persisted)

    def test_deserialize_proposal(self, sample_proposal: HolonProposal) -> None:
        """Test proposal deserialization roundtrip."""
        data = _serialize_proposal(sample_proposal)
        restored = _deserialize_proposal(data)

        assert restored.proposal_id == sample_proposal.proposal_id
        assert restored.entity == sample_proposal.entity
        assert restored.context == sample_proposal.context
        assert restored.why_exists == sample_proposal.why_exists
        assert restored.affordances == sample_proposal.affordances

    def test_serialize_holon(self, sample_holon: GerminatingHolon) -> None:
        """Test holon serialization."""
        data = _serialize_holon(sample_holon)

        assert data["germination_id"] == sample_holon.germination_id
        assert data["usage_count"] == 10
        assert data["success_count"] == 8
        assert data["failure_patterns"] == ["timeout"]
        assert data["jit_source"] == "# Generated code"

    def test_deserialize_holon(self, sample_holon: GerminatingHolon) -> None:
        """Test holon deserialization roundtrip."""
        data = _serialize_holon(sample_holon)
        restored = _deserialize_holon(data, sample_holon.proposal)

        assert restored.germination_id == sample_holon.germination_id
        assert restored.usage_count == sample_holon.usage_count
        assert restored.success_count == sample_holon.success_count
        assert restored.failure_patterns == sample_holon.failure_patterns

    def test_serialize_token(self, sample_token: RollbackToken) -> None:
        """Test rollback token serialization."""
        data = _serialize_token(sample_token)

        assert data["token_id"] == sample_token.token_id
        assert data["handle"] == "world.paperclip"
        assert "spec_content" in data
        assert "impl_content" in data

    def test_deserialize_token(self, sample_token: RollbackToken) -> None:
        """Test rollback token deserialization roundtrip."""
        data = _serialize_token(sample_token)
        restored = _deserialize_token(data)

        assert restored.token_id == sample_token.token_id
        assert restored.handle == sample_token.handle
        assert restored.spec_content == sample_token.spec_content


# === GrowthCortex Tests ===


class TestGrowthCortexProposals:
    """Tests for proposal operations."""

    @pytest.mark.asyncio
    async def test_store_proposal_relational(
        self,
        mock_relational: AsyncMock,
        sample_proposal: HolonProposal,
    ) -> None:
        """Test storing proposal with relational backend."""
        cortex = create_growth_cortex(relational=mock_relational)

        result = await cortex.store_proposal(sample_proposal)

        assert result == sample_proposal.proposal_id
        mock_relational.execute.assert_called_once()

        # Verify the SQL contains expected values
        call_args = mock_relational.execute.call_args
        assert "INSERT INTO self_grow_proposals" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_fetch_proposal_found(
        self,
        mock_relational: AsyncMock,
        sample_proposal: HolonProposal,
    ) -> None:
        """Test fetching an existing proposal."""
        data = _serialize_proposal(sample_proposal)
        mock_relational.fetch_one.return_value = {"data": json.dumps(data)}

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.fetch_proposal(sample_proposal.proposal_id)

        assert result is not None
        assert result.proposal_id == sample_proposal.proposal_id
        assert result.entity == "paperclip"

    @pytest.mark.asyncio
    async def test_fetch_proposal_not_found(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test fetching a non-existent proposal."""
        mock_relational.fetch_one.return_value = None

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.fetch_proposal("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_list_proposals(
        self,
        mock_relational: AsyncMock,
        sample_proposal: HolonProposal,
    ) -> None:
        """Test listing proposals."""
        data = _serialize_proposal(sample_proposal)
        mock_relational.fetch_all.return_value = [{"data": json.dumps(data)}]

        cortex = create_growth_cortex(relational=mock_relational)
        results = await cortex.list_proposals()

        assert len(results) == 1
        assert results[0].entity == "paperclip"

    @pytest.mark.asyncio
    async def test_list_proposals_with_filters(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test listing proposals with status and context filters."""
        mock_relational.fetch_all.return_value = []

        cortex = create_growth_cortex(relational=mock_relational)
        await cortex.list_proposals(status="draft", context="world")

        call_args = mock_relational.fetch_all.call_args
        sql = call_args[0][0]
        params = call_args[0][1]

        assert "status = :status" in sql
        assert "context = :context" in sql
        assert params["status"] == "draft"
        assert params["context"] == "world"

    @pytest.mark.asyncio
    async def test_update_proposal_status(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test updating proposal status."""
        mock_relational.execute.return_value = 1

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.update_proposal_status("proposal-123", "validated")

        assert result is True
        call_args = mock_relational.execute.call_args
        assert "UPDATE self_grow_proposals" in call_args[0][0]

    @pytest.mark.asyncio
    async def test_delete_proposal(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test deleting a proposal."""
        mock_relational.execute.return_value = 1

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.delete_proposal("proposal-123")

        assert result is True


class TestGrowthCortexNursery:
    """Tests for nursery operations."""

    @pytest.mark.asyncio
    async def test_store_holon(
        self,
        mock_relational: AsyncMock,
        sample_holon: GerminatingHolon,
    ) -> None:
        """Test storing a germinating holon."""
        cortex = create_growth_cortex(relational=mock_relational)

        result = await cortex.store_holon(sample_holon)

        assert result == sample_holon.germination_id
        mock_relational.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_holon_found(
        self,
        mock_relational: AsyncMock,
        sample_holon: GerminatingHolon,
    ) -> None:
        """Test fetching an existing holon."""
        holon_data = _serialize_holon(sample_holon)
        proposal_data = _serialize_proposal(sample_holon.proposal)

        mock_relational.fetch_one.return_value = {
            "data": json.dumps(holon_data),
            "proposal_id": sample_holon.proposal.proposal_id,
            "proposal_data": json.dumps(proposal_data),
        }

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.fetch_holon(sample_holon.germination_id)

        assert result is not None
        assert result.germination_id == sample_holon.germination_id
        assert result.usage_count == 10

    @pytest.mark.asyncio
    async def test_fetch_holon_by_handle(
        self,
        mock_relational: AsyncMock,
        sample_holon: GerminatingHolon,
    ) -> None:
        """Test fetching holon by handle."""
        holon_data = _serialize_holon(sample_holon)
        proposal_data = _serialize_proposal(sample_holon.proposal)

        mock_relational.fetch_one.return_value = {
            "data": json.dumps(holon_data),
            "proposal_id": sample_holon.proposal.proposal_id,
            "proposal_data": json.dumps(proposal_data),
        }

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.fetch_holon_by_handle("world.paperclip")

        assert result is not None
        assert result.proposal.entity == "paperclip"

    @pytest.mark.asyncio
    async def test_list_nursery(
        self,
        mock_relational: AsyncMock,
        sample_holon: GerminatingHolon,
    ) -> None:
        """Test listing nursery holons."""
        holon_data = _serialize_holon(sample_holon)
        proposal_data = _serialize_proposal(sample_holon.proposal)

        mock_relational.fetch_all.return_value = [
            {
                "data": json.dumps(holon_data),
                "proposal_id": sample_holon.proposal.proposal_id,
                "proposal_data": json.dumps(proposal_data),
            }
        ]

        cortex = create_growth_cortex(relational=mock_relational)
        results = await cortex.list_nursery()

        assert len(results) == 1
        assert results[0].usage_count == 10

    @pytest.mark.asyncio
    async def test_update_usage(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test updating usage statistics."""
        mock_relational.fetch_one.return_value = {
            "usage_count": 10,
            "success_count": 8,
            "failure_patterns": "[]",
        }
        mock_relational.execute.return_value = 1

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.update_usage("holon-123", success=True)

        assert result is True

    @pytest.mark.asyncio
    async def test_update_usage_with_failure(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test updating usage with failure pattern."""
        mock_relational.fetch_one.return_value = {
            "usage_count": 10,
            "success_count": 8,
            "failure_patterns": '["timeout"]',
        }
        mock_relational.execute.return_value = 1

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.update_usage(
            "holon-123",
            success=False,
            failure_pattern="connection_error",
        )

        assert result is True
        call_args = mock_relational.execute.call_args
        params = call_args[0][1]
        patterns = json.loads(params["failure_patterns"])
        assert "connection_error" in patterns

    @pytest.mark.asyncio
    async def test_mark_promoted(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test marking holon as promoted."""
        mock_relational.execute.return_value = 1
        mock_relational.fetch_one.return_value = {"proposal_id": "prop-123"}

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.mark_promoted("holon-123", "token-456")

        assert result is True

    @pytest.mark.asyncio
    async def test_mark_pruned(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test marking holon as pruned."""
        mock_relational.execute.return_value = 1
        mock_relational.fetch_one.return_value = {"proposal_id": "prop-123"}

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.mark_pruned("holon-123")

        assert result is True


class TestGrowthCortexRollback:
    """Tests for rollback token operations."""

    @pytest.mark.asyncio
    async def test_store_rollback_token(
        self,
        mock_relational: AsyncMock,
        sample_token: RollbackToken,
    ) -> None:
        """Test storing a rollback token."""
        cortex = create_growth_cortex(relational=mock_relational)

        result = await cortex.store_rollback_token(sample_token)

        assert result == sample_token.token_id
        mock_relational.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_fetch_rollback_token(
        self,
        mock_relational: AsyncMock,
        sample_token: RollbackToken,
    ) -> None:
        """Test fetching a rollback token."""
        data = _serialize_token(sample_token)
        # Add the 'id' field as it would be in the row
        data["id"] = data["token_id"]
        mock_relational.fetch_one.return_value = data

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.fetch_rollback_token("world.paperclip")

        assert result is not None
        assert result.handle == "world.paperclip"

    @pytest.mark.asyncio
    async def test_delete_rollback_token(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test deleting a rollback token."""
        mock_relational.execute.return_value = 1

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.delete_rollback_token("token-123")

        assert result is True

    @pytest.mark.asyncio
    async def test_cleanup_expired_tokens(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test cleaning up expired tokens."""
        mock_relational.execute.return_value = 3

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.cleanup_expired_tokens()

        assert result == 3


class TestGrowthCortexBudget:
    """Tests for budget operations."""

    @pytest.mark.asyncio
    async def test_load_budget_default(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test loading budget when none exists."""
        mock_relational.fetch_one.return_value = None

        cortex = create_growth_cortex(relational=mock_relational)
        budget = await cortex.load_budget()

        assert budget.remaining == 1.0
        assert budget.config.max_entropy_per_run == 1.0

    @pytest.mark.asyncio
    async def test_load_budget_existing(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test loading an existing budget."""
        mock_relational.fetch_one.return_value = {
            "remaining": 0.5,
            "spent_this_run": 0.3,
            "spent_by_operation": '{"recognize": 0.25}',
            "last_regeneration": datetime.now().isoformat(),
            "config": '{"max_entropy_per_run": 1.0}',
        }

        cortex = create_growth_cortex(relational=mock_relational)
        budget = await cortex.load_budget()

        # Note: remaining may be > 0.5 due to regeneration
        assert budget.spent_by_operation.get("recognize") == 0.25

    @pytest.mark.asyncio
    async def test_save_budget(
        self,
        mock_relational: AsyncMock,
    ) -> None:
        """Test saving budget."""
        budget = GrowthBudget()
        budget.remaining = 0.7
        budget.spend("recognize")

        cortex = create_growth_cortex(relational=mock_relational)
        result = await cortex.save_budget(budget)

        assert result is True
        mock_relational.execute.assert_called_once()


class TestGrowthCortexFactory:
    """Tests for factory function."""

    def test_create_with_relational(self, mock_relational: AsyncMock) -> None:
        """Test creating cortex with relational store."""
        cortex = create_growth_cortex(relational=mock_relational)

        assert cortex._relational is mock_relational
        assert cortex._bicameral is None

    def test_create_with_bicameral(self) -> None:
        """Test creating cortex with bicameral memory."""
        mock_bicameral = MagicMock()

        cortex = create_growth_cortex(bicameral=mock_bicameral)

        assert cortex._bicameral is mock_bicameral
        assert cortex._relational is None

    def test_create_empty(self) -> None:
        """Test creating cortex with no stores."""
        cortex = create_growth_cortex()

        assert cortex._bicameral is None
        assert cortex._relational is None
