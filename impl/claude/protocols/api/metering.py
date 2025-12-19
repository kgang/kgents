"""
Usage Metering Middleware for Soul API.

Tracks:
- Request counts per user
- Token usage per user
- Rate limiting
- Monthly quota enforcement

Architecture:
    - Middleware intercepts all requests
    - Tracks usage in-memory for rate limiting (synchronous, low-latency)
    - Records to OpenMeter for billing (async, batched)
    - Provides usage statistics endpoint
"""

from __future__ import annotations

import asyncio
import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional

# Graceful FastAPI import
try:
    from fastapi import Request, Response
    from starlette.middleware.base import BaseHTTPMiddleware

    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    # Stubs
    Request = Any  # type: ignore[misc, assignment]
    Response = Any  # type: ignore[misc, assignment]
    BaseHTTPMiddleware = object  # type: ignore[misc, assignment]

# SaaS infrastructure (optional)
try:
    from protocols.config import get_saas_clients

    HAS_SAAS_CONFIG = True
except ImportError:
    HAS_SAAS_CONFIG = False
    get_saas_clients = None  # type: ignore[assignment]

logger = logging.getLogger(__name__)


# --- Usage Tracking ---


@dataclass
class UsageStats:
    """Usage statistics for a user."""

    user_id: str
    requests_today: int = 0
    tokens_today: int = 0
    tokens_month: int = 0
    last_request: Optional[datetime] = None
    first_request_today: Optional[datetime] = None
    endpoints_hit: dict[str, int] = field(default_factory=lambda: defaultdict(int))


# In-memory usage store
# Production would use Redis or database
_USAGE_STORE: dict[str, UsageStats] = {}


def get_usage_stats(user_id: str) -> UsageStats:
    """
    Get usage stats for a user.

    Args:
        user_id: User identifier

    Returns:
        UsageStats for the user
    """
    if user_id not in _USAGE_STORE:
        _USAGE_STORE[user_id] = UsageStats(user_id=user_id)
    return _USAGE_STORE[user_id]


def reset_daily_stats(user_id: str) -> None:
    """
    Reset daily statistics for a user.

    Called when a new day is detected.

    Args:
        user_id: User identifier
    """
    stats = get_usage_stats(user_id)
    stats.requests_today = 0
    stats.tokens_today = 0
    stats.first_request_today = None


def record_request(
    user_id: str,
    endpoint: str,
    tokens_used: int = 0,
) -> None:
    """
    Record a request for usage tracking.

    Args:
        user_id: User identifier
        endpoint: Endpoint path
        tokens_used: Number of tokens used in this request
    """
    stats = get_usage_stats(user_id)

    # Check if it's a new day
    now = datetime.now()
    if stats.first_request_today is None:
        stats.first_request_today = now
    elif stats.first_request_today.date() != now.date():
        # New day - reset daily stats
        reset_daily_stats(user_id)
        stats.first_request_today = now

    # Update stats
    stats.requests_today += 1
    stats.tokens_today += tokens_used
    stats.tokens_month += tokens_used
    stats.last_request = now
    stats.endpoints_hit[endpoint] = stats.endpoints_hit.get(endpoint, 0) + 1


def check_rate_limit(user_id: str, rate_limit: int) -> tuple[bool, Optional[str]]:
    """
    Check if user has exceeded rate limit.

    Note: This check assumes request was already recorded via record_request()
    BEFORE this check is called. So we use > instead of >= since the current
    request is already counted.

    Args:
        user_id: User identifier
        rate_limit: Maximum requests per day

    Returns:
        Tuple of (is_allowed, error_message)
        is_allowed: True if request is allowed
        error_message: None if allowed, error message if not
    """
    stats = get_usage_stats(user_id)

    # Use > because current request is already counted
    if stats.requests_today > rate_limit:
        return False, f"Rate limit exceeded. {rate_limit} requests per day allowed."

    return True, None


def check_token_quota(
    user_id: str, monthly_limit: int, tokens_needed: int = 0
) -> tuple[bool, Optional[str]]:
    """
    Check if user has exceeded monthly token quota.

    Args:
        user_id: User identifier
        monthly_limit: Maximum tokens per month (0 = unlimited)
        tokens_needed: Estimated tokens needed for this request

    Returns:
        Tuple of (is_allowed, error_message)
    """
    if monthly_limit == 0:
        # Unlimited
        return True, None

    stats = get_usage_stats(user_id)

    if stats.tokens_month + tokens_needed > monthly_limit:
        return False, (
            f"Monthly token quota exceeded. "
            f"{monthly_limit} tokens per month allowed, "
            f"{stats.tokens_month} used."
        )

    return True, None


def clear_usage_stats() -> None:
    """Clear all usage stats. For testing only."""
    _USAGE_STORE.clear()


# --- Middleware ---


class MeteringMiddleware(BaseHTTPMiddleware):
    """
    Middleware for tracking API usage.

    Tracks requests, tokens, and enforces rate limits.
    Records to OpenMeter for billing when configured.
    """

    async def dispatch(
        self, request: "Request", call_next: Callable[["Request"], Any]
    ) -> "Response":
        """
        Process request with usage tracking.

        Args:
            request: The incoming request
            call_next: Next middleware/handler

        Returns:
            Response with usage headers added
        """
        if not HAS_FASTAPI:
            raise ImportError("FastAPI is required for metering middleware")

        # Track start time
        start_time = time.time()

        # Get user_id and tenant_id from request state (set by auth middleware)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)

        # Process request
        response: Response = await call_next(request)

        # Track end time
        duration_ms = int((time.time() - start_time) * 1000)

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        # If we have a user, track usage
        if user_id:
            # Get tokens from response (if available)
            tokens_used = getattr(request.state, "tokens_used", 0)

            # Record request to in-memory store (for rate limiting)
            record_request(
                user_id=user_id,
                endpoint=request.url.path,
                tokens_used=tokens_used,
            )

            # Get stats
            stats = get_usage_stats(user_id)

            # Add usage headers
            response.headers["X-RateLimit-Requests-Today"] = str(stats.requests_today)
            response.headers["X-Tokens-Today"] = str(stats.tokens_today)
            response.headers["X-Tokens-Month"] = str(stats.tokens_month)

            # Record to OpenMeter for billing (async, non-blocking)
            if HAS_SAAS_CONFIG and get_saas_clients is not None:
                asyncio.create_task(
                    self._record_to_openmeter(
                        tenant_id=str(tenant_id) if tenant_id else user_id,
                        endpoint=request.url.path,
                        method=request.method,
                        status_code=response.status_code,
                    )
                )

        return response

    async def _record_to_openmeter(
        self,
        tenant_id: str,
        endpoint: str,
        method: str,
        status_code: int,
    ) -> None:
        """Record request to OpenMeter for billing."""
        try:
            clients = get_saas_clients()
            if clients.openmeter is not None:
                await clients.openmeter.record_request(
                    tenant_id=tenant_id,
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                )
        except Exception as e:
            # Non-blocking - log and continue
            logger.warning(f"Failed to record to OpenMeter: {e}")


# --- Usage Endpoint Helpers ---


def get_all_usage_stats() -> dict[str, dict[str, Any]]:
    """
    Get usage stats for all users.

    Returns:
        Dictionary mapping user_id to stats dict
    """
    return {
        user_id: {
            "user_id": stats.user_id,
            "requests_today": stats.requests_today,
            "tokens_today": stats.tokens_today,
            "tokens_month": stats.tokens_month,
            "last_request": (stats.last_request.isoformat() if stats.last_request else None),
            "endpoints_hit": dict(stats.endpoints_hit),
        }
        for user_id, stats in _USAGE_STORE.items()
    }
