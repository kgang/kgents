"""
Tests for API key authentication.

Tests:
- API key validation
- User tier management
- Rate limiting metadata
- FastAPI dependency integration
"""

from __future__ import annotations

from typing import Generator

import pytest

pytest.importorskip("fastapi")

from protocols.api.auth import (
    ApiKeyData,
    can_use_budget_tier,
    clear_api_keys,
    get_budget_tier_for_user,
    lookup_api_key,
    register_api_key,
    validate_api_key_format,
)


@pytest.fixture
def clean_api_keys() -> Generator[None, None, None]:
    """Clean API keys before each test and restore dev keys after."""
    from uuid import UUID

    # Store original dev keys with tenant support
    dev_keys = {
        "kg_dev_alice": ApiKeyData(
            key="kg_dev_alice",
            user_id="user_alice",
            tier="FREE",
            rate_limit=100,
            monthly_token_limit=10000,
            tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
            scopes=("read",),
        ),
        "kg_dev_bob": ApiKeyData(
            key="kg_dev_bob",
            user_id="user_bob",
            tier="PRO",
            rate_limit=1000,
            monthly_token_limit=100000,
            tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
            scopes=("read", "write"),
        ),
        "kg_dev_carol": ApiKeyData(
            key="kg_dev_carol",
            user_id="user_carol",
            tier="ENTERPRISE",
            rate_limit=10000,
            monthly_token_limit=0,
            tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
            scopes=("read", "write", "admin"),
        ),
    }

    clear_api_keys()
    yield
    # Restore dev keys after test
    clear_api_keys()
    for key_data in dev_keys.values():
        register_api_key(key_data)


class TestApiKeyFormat:
    """Tests for API key format validation."""

    def test_valid_format(self) -> None:
        """Test valid API key formats."""
        assert validate_api_key_format("kg_dev_alice")
        assert validate_api_key_format("kg_prod_12345")
        assert validate_api_key_format("kg_test")

    def test_invalid_format(self) -> None:
        """Test invalid API key formats."""
        assert not validate_api_key_format("invalid_key")
        assert not validate_api_key_format("api_key_123")
        assert not validate_api_key_format("")
        assert not validate_api_key_format("kg")  # Too short but technically valid


class TestApiKeyLookup:
    """Tests for API key lookup."""

    def test_lookup_existing_key(self) -> None:
        """Test looking up existing API key."""
        # Development keys should exist by default
        data = lookup_api_key("kg_dev_alice")

        assert data is not None
        assert data.key == "kg_dev_alice"
        assert data.user_id == "user_alice"
        assert data.tier == "FREE"

    def test_lookup_nonexistent_key(self) -> None:
        """Test looking up nonexistent API key."""
        data = lookup_api_key("kg_nonexistent")

        assert data is None

    def test_lookup_all_dev_keys(self) -> None:
        """Test all development keys are present."""
        dev_keys = ["kg_dev_alice", "kg_dev_bob", "kg_dev_carol"]

        for key in dev_keys:
            data = lookup_api_key(key)
            assert data is not None
            assert data.key == key


class TestApiKeyRegistration:
    """Tests for API key registration."""

    def test_register_new_key(self, clean_api_keys: None) -> None:
        """Test registering a new API key."""
        key_data = ApiKeyData(
            key="kg_test_user",
            user_id="test_123",
            tier="PRO",
            rate_limit=500,
        )

        register_api_key(key_data)

        # Look it up
        found = lookup_api_key("kg_test_user")
        assert found is not None
        assert found.user_id == "test_123"
        assert found.tier == "PRO"

    def test_register_overwrites_existing(self, clean_api_keys: None) -> None:
        """Test registering overwrites existing key."""
        key1 = ApiKeyData(
            key="kg_test",
            user_id="user1",
            tier="FREE",
            rate_limit=100,
        )
        key2 = ApiKeyData(
            key="kg_test",
            user_id="user2",
            tier="PRO",
            rate_limit=500,
        )

        register_api_key(key1)
        register_api_key(key2)

        found = lookup_api_key("kg_test")
        assert found is not None
        assert found.user_id == "user2"
        assert found.tier == "PRO"


class TestUserTiers:
    """Tests for user tier functionality."""

    def test_free_tier_budget(self) -> None:
        """Test FREE tier gets whisper budget."""
        budget = get_budget_tier_for_user("FREE")
        assert budget == "whisper"

    def test_pro_tier_budget(self) -> None:
        """Test PRO tier gets dialogue budget."""
        budget = get_budget_tier_for_user("PRO")
        assert budget == "dialogue"

    def test_enterprise_tier_budget(self) -> None:
        """Test ENTERPRISE tier gets deep budget."""
        budget = get_budget_tier_for_user("ENTERPRISE")
        assert budget == "deep"

    def test_unknown_tier_budget(self) -> None:
        """Test unknown tier defaults to whisper."""
        budget = get_budget_tier_for_user("UNKNOWN")
        assert budget == "whisper"


class TestBudgetTierPermissions:
    """Tests for budget tier permissions."""

    def test_free_tier_permissions(self) -> None:
        """Test FREE tier budget permissions."""
        assert can_use_budget_tier("FREE", "dormant")
        assert can_use_budget_tier("FREE", "whisper")
        assert not can_use_budget_tier("FREE", "dialogue")
        assert not can_use_budget_tier("FREE", "deep")

    def test_pro_tier_permissions(self) -> None:
        """Test PRO tier budget permissions."""
        assert can_use_budget_tier("PRO", "dormant")
        assert can_use_budget_tier("PRO", "whisper")
        assert can_use_budget_tier("PRO", "dialogue")
        assert not can_use_budget_tier("PRO", "deep")

    def test_enterprise_tier_permissions(self) -> None:
        """Test ENTERPRISE tier budget permissions."""
        assert can_use_budget_tier("ENTERPRISE", "dormant")
        assert can_use_budget_tier("ENTERPRISE", "whisper")
        assert can_use_budget_tier("ENTERPRISE", "dialogue")
        assert can_use_budget_tier("ENTERPRISE", "deep")

    def test_unknown_tier_permissions(self) -> None:
        """Test unknown tier has minimal permissions."""
        assert can_use_budget_tier("UNKNOWN", "dormant")
        assert not can_use_budget_tier("UNKNOWN", "whisper")
        assert not can_use_budget_tier("UNKNOWN", "dialogue")
        assert not can_use_budget_tier("UNKNOWN", "deep")


class TestApiKeyData:
    """Tests for ApiKeyData dataclass."""

    def test_api_key_data_creation(self) -> None:
        """Test ApiKeyData creation."""
        data = ApiKeyData(
            key="kg_test",
            user_id="user_123",
            tier="PRO",
            rate_limit=1000,
        )

        assert data.key == "kg_test"
        assert data.user_id == "user_123"
        assert data.tier == "PRO"
        assert data.rate_limit == 1000
        assert data.monthly_token_limit == 0  # Default
        assert data.tokens_used_month == 0  # Default

    def test_api_key_data_with_token_limits(self) -> None:
        """Test ApiKeyData with token limits."""
        data = ApiKeyData(
            key="kg_test",
            user_id="user_123",
            tier="FREE",
            rate_limit=100,
            monthly_token_limit=10000,
            tokens_used_month=5000,
        )

        assert data.monthly_token_limit == 10000
        assert data.tokens_used_month == 5000


class TestFastAPIIntegration:
    """Tests for FastAPI dependency integration."""

    @pytest.mark.asyncio
    async def test_get_api_key_dependency_valid(self) -> None:
        """Test get_api_key dependency with valid key."""
        from protocols.api.auth import get_api_key

        # Simulate valid key
        key_data = await get_api_key(x_api_key="kg_dev_alice")

        assert key_data.key == "kg_dev_alice"
        assert key_data.user_id == "user_alice"
        assert key_data.tier == "FREE"

    @pytest.mark.asyncio
    async def test_get_api_key_dependency_invalid_format(self) -> None:
        """Test get_api_key dependency with invalid format."""
        from fastapi import HTTPException
        from protocols.api.auth import get_api_key

        with pytest.raises(HTTPException) as exc_info:
            await get_api_key(x_api_key="invalid_key")

        assert exc_info.value.status_code == 401
        assert "format" in str(exc_info.value.detail).lower()

    @pytest.mark.asyncio
    async def test_get_api_key_dependency_nonexistent(self) -> None:
        """Test get_api_key dependency with nonexistent key."""
        from fastapi import HTTPException
        from protocols.api.auth import get_api_key

        with pytest.raises(HTTPException) as exc_info:
            await get_api_key(x_api_key="kg_nonexistent")

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_optional_api_key_none(self) -> None:
        """Test get_optional_api_key with no key."""
        from protocols.api.auth import get_optional_api_key

        key_data = await get_optional_api_key(x_api_key=None)

        assert key_data is None

    @pytest.mark.asyncio
    async def test_get_optional_api_key_invalid(self) -> None:
        """Test get_optional_api_key with invalid key."""
        from protocols.api.auth import get_optional_api_key

        key_data = await get_optional_api_key(x_api_key="invalid")

        assert key_data is None

    @pytest.mark.asyncio
    async def test_get_optional_api_key_valid(self) -> None:
        """Test get_optional_api_key with valid key."""
        from protocols.api.auth import get_optional_api_key

        key_data = await get_optional_api_key(x_api_key="kg_dev_alice")

        assert key_data is not None
        assert key_data.user_id == "user_alice"
