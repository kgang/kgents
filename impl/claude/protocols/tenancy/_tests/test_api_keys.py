"""Tests for API key management."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from protocols.tenancy.api_keys import (
    ApiKeyService,
    extract_key_prefix,
    generate_api_key,
    hash_api_key,
    validate_api_key_format,
)


class TestKeyGeneration:
    """Tests for API key generation."""

    def test_generate_api_key_format(self) -> None:
        """Test generated key format."""
        full_key, key_prefix, key_hash = generate_api_key()

        # Full key format: kg_{prefix}_{secret}
        assert full_key.startswith("kg_")
        parts = full_key.split("_")
        assert len(parts) == 3
        assert len(parts[1]) == 5  # Prefix length

        # Key prefix format: kg_{prefix}
        assert key_prefix.startswith("kg_")
        assert len(key_prefix) == 8  # "kg_" + 5 chars

        # Hash is 64 chars (SHA-256 hex)
        assert len(key_hash) == 64

    def test_generate_api_key_uniqueness(self) -> None:
        """Test that generated keys are unique."""
        keys = [generate_api_key()[0] for _ in range(100)]
        assert len(set(keys)) == 100

    def test_hash_api_key_consistency(self) -> None:
        """Test that hashing is consistent."""
        key = "kg_abc12_secrettoken"

        hash1 = hash_api_key(key)
        hash2 = hash_api_key(key)

        assert hash1 == hash2

    def test_hash_api_key_different_keys(self) -> None:
        """Test that different keys produce different hashes."""
        key1 = "kg_abc12_secrettoken1"
        key2 = "kg_abc12_secrettoken2"

        assert hash_api_key(key1) != hash_api_key(key2)


class TestKeyValidation:
    """Tests for API key format validation."""

    def test_valid_key_format(self) -> None:
        """Test valid key formats."""
        assert validate_api_key_format("kg_abc12_longsecretherewithlots")
        assert validate_api_key_format("kg_12345_x")

    def test_invalid_key_formats(self) -> None:
        """Test invalid key formats."""
        # Wrong prefix
        assert not validate_api_key_format("api_abc12_secret")
        assert not validate_api_key_format("key_abc12_secret")

        # Missing parts
        assert not validate_api_key_format("kg_abc12")
        assert not validate_api_key_format("kg_")

        # Wrong prefix length
        assert not validate_api_key_format("kg_abcd_secret")  # 4 chars
        assert not validate_api_key_format("kg_abcdef_secret")  # 6 chars

        # Invalid prefix characters
        assert not validate_api_key_format("kg_ABC12_secret")  # Uppercase
        assert not validate_api_key_format("kg_ab-12_secret")  # Dash


class TestExtractPrefix:
    """Tests for prefix extraction."""

    def test_extract_valid_prefix(self) -> None:
        """Test extracting prefix from valid key."""
        key = "kg_abc12_verylongsecrethere"
        prefix = extract_key_prefix(key)

        assert prefix == "kg_abc12"

    def test_extract_invalid_key(self) -> None:
        """Test extracting prefix from invalid key."""
        assert extract_key_prefix("invalid_key") is None
        assert extract_key_prefix("") is None


class TestApiKeyService:
    """Tests for ApiKeyService."""

    @pytest.fixture
    def service(self) -> ApiKeyService:
        """Create fresh service for each test."""
        return ApiKeyService()

    @pytest.fixture
    def tenant_id(self) -> uuid4:
        """Sample tenant ID."""
        return uuid4()

    @pytest.mark.asyncio
    async def test_create_key(
        self,
        service: ApiKeyService,
        tenant_id: uuid4,
    ) -> None:
        """Test creating an API key."""
        key_model, full_key = await service.create_key(
            tenant_id=tenant_id,
            name="Test Key",
        )

        assert key_model.tenant_id == tenant_id
        assert key_model.name == "Test Key"
        assert key_model.is_valid
        assert validate_api_key_format(full_key)

    @pytest.mark.asyncio
    async def test_create_key_with_scopes(
        self,
        service: ApiKeyService,
        tenant_id: uuid4,
    ) -> None:
        """Test creating key with custom scopes."""
        key_model, _ = await service.create_key(
            tenant_id=tenant_id,
            name="Admin Key",
            scopes=["read", "write", "admin"],
        )

        assert key_model.has_scope("admin")
        assert key_model.has_scope("read")
        assert not key_model.has_scope("billing")

    @pytest.mark.asyncio
    async def test_validate_key(
        self,
        service: ApiKeyService,
        tenant_id: uuid4,
    ) -> None:
        """Test validating a key."""
        key_model, full_key = await service.create_key(
            tenant_id=tenant_id,
            name="Test Key",
        )

        validated = await service.validate_key(full_key)

        assert validated is not None
        assert validated.id == key_model.id

    @pytest.mark.asyncio
    async def test_validate_invalid_key(
        self,
        service: ApiKeyService,
    ) -> None:
        """Test validating an invalid key."""
        validated = await service.validate_key("kg_abc12_nonexistent")

        assert validated is None

    @pytest.mark.asyncio
    async def test_validate_malformed_key(
        self,
        service: ApiKeyService,
    ) -> None:
        """Test validating a malformed key."""
        validated = await service.validate_key("not_a_valid_key")

        assert validated is None

    @pytest.mark.asyncio
    async def test_revoke_key(
        self,
        service: ApiKeyService,
        tenant_id: uuid4,
    ) -> None:
        """Test revoking a key."""
        key_model, full_key = await service.create_key(
            tenant_id=tenant_id,
            name="To Revoke",
        )

        # Key should be valid initially
        assert (await service.validate_key(full_key)) is not None

        # Revoke it
        revoked = await service.revoke_key(key_model.id)
        assert revoked

        # Key should no longer validate
        assert (await service.validate_key(full_key)) is None

    @pytest.mark.asyncio
    async def test_revoke_nonexistent_key(
        self,
        service: ApiKeyService,
    ) -> None:
        """Test revoking a nonexistent key."""
        revoked = await service.revoke_key(uuid4())

        assert not revoked

    @pytest.mark.asyncio
    async def test_list_keys(
        self,
        service: ApiKeyService,
        tenant_id: uuid4,
    ) -> None:
        """Test listing keys for a tenant."""
        # Create multiple keys
        await service.create_key(tenant_id, "Key 1")
        await service.create_key(tenant_id, "Key 2")
        await service.create_key(tenant_id, "Key 3")

        # Create key for different tenant
        other_tenant = uuid4()
        await service.create_key(other_tenant, "Other Key")

        keys = await service.list_keys(tenant_id)

        assert len(keys) == 3
        assert all(k.tenant_id == tenant_id for k in keys)

    @pytest.mark.asyncio
    async def test_key_with_expiration(
        self,
        service: ApiKeyService,
        tenant_id: uuid4,
    ) -> None:
        """Test key with expiration date."""
        key_model, _ = await service.create_key(
            tenant_id=tenant_id,
            name="Expiring Key",
            expires_at=datetime.utcnow() + timedelta(days=30),
        )

        assert not key_model.is_expired
        assert key_model.is_valid
