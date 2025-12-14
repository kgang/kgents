"""
API Key management for kgents SaaS.

Provides secure API key generation, validation, and management:
- Key generation with secure random prefix
- SHA-256 hashing (never store plaintext)
- Prefix-based lookup for identification
- Scope validation
"""

from __future__ import annotations

import hashlib
import secrets
import string
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Protocol
from uuid import UUID

from protocols.tenancy.models import ApiKey

# Key format: kg_{random_prefix}_{random_secret}
# Example: kg_abc12_x7Kp9mQ3nR5tY2wZ
KEY_PREFIX_CHARS = string.ascii_lowercase + string.digits
KEY_PREFIX_LENGTH = 5
KEY_SECRET_LENGTH = 32


def generate_api_key() -> tuple[str, str, str]:
    """
    Generate a new API key.

    Returns:
        Tuple of (full_key, key_prefix, key_hash)
        - full_key: The complete key to give to the user (store only once!)
        - key_prefix: The prefix for identification (kg_xxxxx)
        - key_hash: SHA-256 hash for storage
    """
    # Generate random prefix (for identification)
    prefix = "".join(secrets.choice(KEY_PREFIX_CHARS) for _ in range(KEY_PREFIX_LENGTH))

    # Generate random secret
    secret = secrets.token_urlsafe(KEY_SECRET_LENGTH)

    # Full key format
    full_key = f"kg_{prefix}_{secret}"

    # Key prefix for lookup
    key_prefix = f"kg_{prefix}"

    # Hash for storage
    key_hash = hash_api_key(full_key)

    return full_key, key_prefix, key_hash


def hash_api_key(key: str) -> str:
    """
    Hash an API key for secure storage.

    Uses SHA-256 for consistent, irreversible hashing.

    Args:
        key: The full API key

    Returns:
        Hex-encoded SHA-256 hash
    """
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def validate_api_key_format(key: str) -> bool:
    """
    Validate API key format.

    Valid format: kg_{5_chars}_{secret}

    Args:
        key: The API key to validate

    Returns:
        True if format is valid
    """
    if not key.startswith("kg_"):
        return False

    parts = key.split("_")
    if len(parts) < 3:
        return False

    prefix = parts[1]
    if len(prefix) != KEY_PREFIX_LENGTH:
        return False

    if not all(c in KEY_PREFIX_CHARS for c in prefix):
        return False

    return True


def extract_key_prefix(key: str) -> Optional[str]:
    """
    Extract the prefix from an API key.

    Args:
        key: The full API key

    Returns:
        The key prefix (kg_xxxxx) or None if invalid
    """
    if not validate_api_key_format(key):
        return None

    parts = key.split("_")
    return f"kg_{parts[1]}"


class ApiKeyServiceProtocol(Protocol):
    """Protocol for API key service operations."""

    async def create_key(
        self,
        tenant_id: UUID,
        name: str,
        scopes: list[str] | None = None,
        user_id: UUID | None = None,
        expires_at: datetime | None = None,
    ) -> tuple[ApiKey, str]:
        """Create a new API key. Returns (key_model, full_key)."""
        ...

    async def validate_key(self, full_key: str) -> Optional[ApiKey]:
        """Validate and return API key if valid."""
        ...

    async def revoke_key(self, key_id: UUID, revoked_by: UUID | None = None) -> bool:
        """Revoke an API key."""
        ...

    async def list_keys(self, tenant_id: UUID) -> list[ApiKey]:
        """List all API keys for a tenant."""
        ...


@dataclass
class ApiKeyValidation:
    """Result of API key validation."""

    is_valid: bool
    key: Optional[ApiKey] = None
    error: Optional[str] = None

    @classmethod
    def valid(cls, key: ApiKey) -> "ApiKeyValidation":
        """Create a valid result."""
        return cls(is_valid=True, key=key)

    @classmethod
    def invalid(cls, error: str) -> "ApiKeyValidation":
        """Create an invalid result."""
        return cls(is_valid=False, error=error)


class ApiKeyService:
    """
    API key service for creating and validating keys.

    This is a minimal in-memory implementation for development.
    Production should use the database-backed version.
    """

    def __init__(self) -> None:
        """Initialize with empty key store."""
        self._keys: dict[str, ApiKey] = {}  # key_hash -> ApiKey
        self._prefixes: dict[str, str] = {}  # key_prefix -> key_hash

    async def create_key(
        self,
        tenant_id: UUID,
        name: str,
        scopes: list[str] | None = None,
        user_id: UUID | None = None,
        expires_at: datetime | None = None,
    ) -> tuple[ApiKey, str]:
        """
        Create a new API key.

        Args:
            tenant_id: Tenant that owns the key
            name: Human-readable name
            scopes: Permission scopes
            user_id: Optional user that created the key
            expires_at: Optional expiration time

        Returns:
            Tuple of (ApiKey model, full key string)
        """
        import uuid

        full_key, key_prefix, key_hash = generate_api_key()

        key = ApiKey(
            id=uuid.uuid4(),
            tenant_id=tenant_id,
            key_prefix=key_prefix,
            name=name,
            scopes=scopes or ["read", "write"],
            user_id=user_id,
            expires_at=expires_at,
            created_at=datetime.utcnow(),
        )

        # Store in memory
        self._keys[key_hash] = key
        self._prefixes[key_prefix] = key_hash

        return key, full_key

    async def validate_key(self, full_key: str) -> Optional[ApiKey]:
        """
        Validate an API key.

        Args:
            full_key: The complete API key

        Returns:
            ApiKey if valid, None otherwise
        """
        if not validate_api_key_format(full_key):
            return None

        key_hash = hash_api_key(full_key)
        key = self._keys.get(key_hash)

        if key is None:
            return None

        if not key.is_valid:
            return None

        return key

    async def revoke_key(self, key_id: UUID, revoked_by: UUID | None = None) -> bool:
        """
        Revoke an API key.

        Args:
            key_id: ID of key to revoke
            revoked_by: User who revoked (optional)

        Returns:
            True if key was revoked
        """
        # Find key by ID
        for key_hash, key in self._keys.items():
            if key.id == key_id:
                # Create new key with is_active=False
                # (ApiKey is immutable, so we replace it)
                revoked_key = ApiKey(
                    id=key.id,
                    tenant_id=key.tenant_id,
                    key_prefix=key.key_prefix,
                    name=key.name,
                    scopes=key.scopes,
                    user_id=key.user_id,
                    rate_limit_rpm=key.rate_limit_rpm,
                    tokens_limit_request=key.tokens_limit_request,
                    expires_at=key.expires_at,
                    last_used_at=key.last_used_at,
                    use_count=key.use_count,
                    is_active=False,
                    created_at=key.created_at,
                )
                self._keys[key_hash] = revoked_key
                return True

        return False

    async def list_keys(self, tenant_id: UUID) -> list[ApiKey]:
        """
        List all API keys for a tenant.

        Args:
            tenant_id: Tenant ID

        Returns:
            List of API keys
        """
        return [key for key in self._keys.values() if key.tenant_id == tenant_id]
