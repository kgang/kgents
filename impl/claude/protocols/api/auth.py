"""
API Key Authentication for Soul API.

Implements:
- API key validation via tenancy module
- User tier management (FREE, PRO, ENTERPRISE)
- Rate limiting metadata
- Tenant context injection
- Graceful FastAPI dependency handling
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import UUID

# Graceful FastAPI import
try:
    from fastapi import Header, HTTPException, Request
    from starlette.middleware.base import BaseHTTPMiddleware

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    # Stubs for when FastAPI is not installed
    Header = None  # type: ignore[assignment]
    Request = None  # type: ignore[assignment, misc]
    BaseHTTPMiddleware = object  # type: ignore[assignment, misc]

    class HTTPException(Exception):  # type: ignore[no-redef]
        """Stub HTTPException."""

        def __init__(self, status_code: int, detail: str) -> None:
            self.status_code = status_code
            self.detail = detail
            super().__init__(detail)


# --- Tenant-Aware User Tier System ---


@dataclass
class ApiKeyData:
    """
    Validated API key data.

    Contains user identity, tier, and rate limit information.
    Now integrated with tenancy module for multi-tenant support.
    """

    key: str  # The API key itself
    user_id: str  # Unique user identifier
    tier: str  # User tier: FREE, PRO, ENTERPRISE
    rate_limit: int  # Requests per day
    monthly_token_limit: int = 0  # Monthly token budget (0 = unlimited)
    tokens_used_month: int = 0  # Tokens used this month
    # Tenant-aware fields
    tenant_id: Optional[UUID] = None  # Multi-tenant support
    scopes: tuple[str, ...] = ("read", "write")  # Permission scopes


# --- API Key Validation ---

# In-memory store for development/testing
# Production uses TenantService + ApiKeyService from protocols/tenancy/
_API_KEY_STORE: dict[str, ApiKeyData] = {
    # Development keys with tenant support
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
        monthly_token_limit=0,  # Unlimited
        tenant_id=UUID("00000000-0000-0000-0000-000000000001"),
        scopes=("read", "write", "admin"),
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

    In production, this uses ApiKeyService from tenancy module.

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
    from fastapi import Query

    async def get_api_key(
        x_api_key: str = Header(None, alias="X-API-Key"),
        api_key_query: str = Query(None, alias="api_key"),
    ) -> ApiKeyData:
        """
        FastAPI dependency for API key authentication.

        Supports both header and query param for API key:
        - Header: X-API-Key (preferred for regular requests)
        - Query: ?api_key=... (needed for SSE/EventSource which can't send headers)

        Validates the API key from header or query param.

        Args:
            x_api_key: API key from X-API-Key header (preferred)
            api_key_query: API key from query param (for SSE/EventSource)

        Returns:
            Validated ApiKeyData

        Raises:
            HTTPException: 401 if key is invalid or missing
        """
        # Use header if present, otherwise fall back to query param
        api_key = x_api_key or api_key_query

        if api_key is None:
            raise HTTPException(
                status_code=401,
                detail="API key required. Provide via X-API-Key header or api_key query param.",
            )

        # Validate format
        if not validate_api_key_format(api_key):
            raise HTTPException(
                status_code=401,
                detail="Invalid API key format. Keys must start with 'kg_'",
            )

        # Look up key
        key_data = lookup_api_key(api_key)
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


def has_scope(api_key: ApiKeyData, scope: str) -> bool:
    """
    Check if API key has a specific scope.

    Args:
        api_key: The API key data
        scope: Required scope (read, write, admin)

    Returns:
        True if key has the scope
    """
    return scope in api_key.scopes


# --- Tenant Context Middleware ---

if HAS_FASTAPI:
    from typing import Any, Callable

    class TenantContextMiddleware(BaseHTTPMiddleware):
        """
        Middleware that sets tenant context from API key.

        Flow:
        1. Extract API key from X-API-Key header
        2. Validate key and get tenant_id
        3. Set tenant context for the request
        4. Clear context after request completes
        """

        async def dispatch(self, request: "Request", call_next: Callable[["Request"], Any]) -> Any:
            """Process request with tenant context."""
            from protocols.tenancy.context import (
                clear_tenant_context,
                set_tenant_context,
            )
            from protocols.tenancy.models import Tenant
            from protocols.tenancy.service import TenantService

            # Get API key from header
            api_key_header = request.headers.get("X-API-Key")

            if api_key_header and validate_api_key_format(api_key_header):
                key_data = lookup_api_key(api_key_header)

                if key_data and key_data.tenant_id:
                    # Set request state for downstream handlers
                    request.state.user_id = key_data.user_id
                    request.state.tenant_id = key_data.tenant_id
                    request.state.api_key_data = key_data

                    # Get tenant from service (in-memory for now)
                    service = TenantService()
                    tenant = await service.get_tenant(key_data.tenant_id)

                    if tenant:
                        # Set tenant context
                        set_tenant_context(tenant)

            try:
                response = await call_next(request)
                return response
            finally:
                # Always clear context
                clear_tenant_context()

else:

    class TenantContextMiddleware:  # type: ignore[no-redef]
        """Stub middleware when FastAPI is not installed."""

        pass
