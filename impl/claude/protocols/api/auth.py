"""
API Key Authentication for Soul API.

Implements:
- API key validation
- User tier management (FREE, PRO, ENTERPRISE)
- Rate limiting metadata
- Graceful FastAPI dependency handling
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Graceful FastAPI import
try:
    from fastapi import Header, HTTPException

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    # Stubs for when FastAPI is not installed
    Header = None  # type: ignore[assignment]

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


# --- User Tier System ---


@dataclass
class ApiKeyData:
    """
    Validated API key data.

    Contains user identity, tier, and rate limit information.
    In production, this would be loaded from a database.
    """

    key: str  # The API key itself
    user_id: str  # Unique user identifier
    tier: str  # User tier: FREE, PRO, ENTERPRISE
    rate_limit: int  # Requests per day
    monthly_token_limit: int = 0  # Monthly token budget (0 = unlimited)
    tokens_used_month: int = 0  # Tokens used this month


# --- API Key Validation ---

# In-memory store for development/testing
# In production, this would be a database
_API_KEY_STORE: dict[str, ApiKeyData] = {
    # Development keys
    "kg_dev_alice": ApiKeyData(
        key="kg_dev_alice",
        user_id="user_alice",
        tier="FREE",
        rate_limit=100,
        monthly_token_limit=10000,
    ),
    "kg_dev_bob": ApiKeyData(
        key="kg_dev_bob",
        user_id="user_bob",
        tier="PRO",
        rate_limit=1000,
        monthly_token_limit=100000,
    ),
    "kg_dev_carol": ApiKeyData(
        key="kg_dev_carol",
        user_id="user_carol",
        tier="ENTERPRISE",
        rate_limit=10000,
        monthly_token_limit=0,  # Unlimited
    ),
}


def validate_api_key_format(key: str) -> bool:
    """
    Validate API key format.

    Args:
        key: The API key to validate

    Returns:
        True if format is valid (starts with kg_)
    """
    return key.startswith("kg_")


def lookup_api_key(key: str) -> Optional[ApiKeyData]:
    """
    Look up API key in store.

    In production, this would query a database.

    Args:
        key: The API key to look up

    Returns:
        ApiKeyData if found, None otherwise
    """
    return _API_KEY_STORE.get(key)


def register_api_key(data: ApiKeyData) -> None:
    """
    Register a new API key.

    For testing/development only.

    Args:
        data: API key data to register
    """
    _API_KEY_STORE[data.key] = data


def clear_api_keys() -> None:
    """Clear all API keys. For testing only."""
    _API_KEY_STORE.clear()


# --- FastAPI Dependency ---


if HAS_FASTAPI:

    async def get_api_key(
        x_api_key: str = Header(..., alias="X-API-Key"),
    ) -> ApiKeyData:
        """
        FastAPI dependency for API key authentication.

        Validates the API key from the X-API-Key header.

        Args:
            x_api_key: API key from request header

        Returns:
            Validated ApiKeyData

        Raises:
            HTTPException: 401 if key is invalid or missing
        """
        # Validate format
        if not validate_api_key_format(x_api_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key format. Keys must start with 'kg_'",
            )

        # Look up key
        key_data = lookup_api_key(x_api_key)
        if key_data is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid API key. Please check your credentials.",
            )

        return key_data

    async def get_optional_api_key(
        x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    ) -> Optional[ApiKeyData]:
        """
        FastAPI dependency for optional API key authentication.

        Like get_api_key but returns None instead of raising 401.
        Useful for endpoints that have different behavior for authenticated users.

        Args:
            x_api_key: API key from request header (optional)

        Returns:
            ApiKeyData if valid key provided, None otherwise
        """
        if x_api_key is None:
            return None

        if not validate_api_key_format(x_api_key):
            return None

        return lookup_api_key(x_api_key)

else:
    # Stub functions when FastAPI is not available

    async def get_api_key(  # type: ignore[misc]
        x_api_key: str,
    ) -> ApiKeyData:
        """Stub for when FastAPI is not installed."""
        raise ImportError("FastAPI is required for API key authentication")

    async def get_optional_api_key(
        x_api_key: Optional[str] = None,
    ) -> Optional[ApiKeyData]:
        """Stub for when FastAPI is not installed."""
        raise ImportError("FastAPI is required for API key authentication")


# --- Tier Helpers ---


def get_budget_tier_for_user(tier: str) -> str:
    """
    Get default budget tier for user tier.

    Args:
        tier: User tier (FREE, PRO, ENTERPRISE)

    Returns:
        Budget tier string (dormant, whisper, dialogue, deep)
    """
    tier_map = {
        "FREE": "whisper",  # Limited to quick responses
        "PRO": "dialogue",  # Full conversation
        "ENTERPRISE": "deep",  # Council of Ghosts access
    }
    return tier_map.get(tier, "whisper")


def can_use_budget_tier(user_tier: str, requested_tier: str) -> bool:
    """
    Check if user tier allows requested budget tier.

    Args:
        user_tier: User's subscription tier
        requested_tier: Requested budget tier

    Returns:
        True if user can use the requested tier
    """
    # Tier hierarchy
    tier_levels = {
        "FREE": ["dormant", "whisper"],
        "PRO": ["dormant", "whisper", "dialogue"],
        "ENTERPRISE": ["dormant", "whisper", "dialogue", "deep"],
    }

    allowed_tiers = tier_levels.get(user_tier, ["dormant"])
    return requested_tier in allowed_tiers
