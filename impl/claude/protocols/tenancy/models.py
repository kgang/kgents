"""
Tenant data models for kgents SaaS.

These models represent the core multi-tenancy entities:
- Tenant: Organization/customer
- TenantUser: User belonging to a tenant
- ApiKey: Programmatic access credential
- Session: K-Gent conversation session
- UsageEvent: Billable usage record

All models are immutable dataclasses for safety and clarity.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import UUID


class SubscriptionTier(Enum):
    """Subscription tier levels."""

    FREE = "free"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    CUSTOM = "custom"

    @property
    def tokens_limit(self) -> int:
        """Default monthly token limit for this tier."""
        limits = {
            SubscriptionTier.FREE: 10_000,
            SubscriptionTier.PRO: 100_000,
            SubscriptionTier.ENTERPRISE: 1_000_000,
            SubscriptionTier.CUSTOM: 0,  # Custom = unlimited or configured
        }
        return limits[self]

    @property
    def rate_limit_rpm(self) -> int:
        """Default requests per minute for this tier."""
        limits = {
            SubscriptionTier.FREE: 60,
            SubscriptionTier.PRO: 600,
            SubscriptionTier.ENTERPRISE: 6000,
            SubscriptionTier.CUSTOM: 10000,
        }
        return limits[self]


class SubscriptionStatus(Enum):
    """Subscription status from billing provider."""

    ACTIVE = "active"
    PAST_DUE = "past_due"
    CANCELED = "canceled"
    TRIALING = "trialing"
    PAUSED = "paused"

    @property
    def is_active(self) -> bool:
        """Check if subscription allows API access."""
        return self in {
            SubscriptionStatus.ACTIVE,
            SubscriptionStatus.TRIALING,
            SubscriptionStatus.PAST_DUE,  # Grace period
        }


class UserRole(Enum):
    """User role within a tenant."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    READONLY = "readonly"

    @property
    def can_manage_users(self) -> bool:
        """Check if role can manage other users."""
        return self in {UserRole.OWNER, UserRole.ADMIN}

    @property
    def can_manage_billing(self) -> bool:
        """Check if role can manage billing."""
        return self == UserRole.OWNER

    @property
    def can_create_api_keys(self) -> bool:
        """Check if role can create API keys."""
        return self in {UserRole.OWNER, UserRole.ADMIN, UserRole.MEMBER}


class SessionStatus(Enum):
    """Session status values."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    CLOSED = "closed"


@dataclass(frozen=True)
class Tenant:
    """
    Represents a tenant (organization/customer) in kgents SaaS.

    This is the root entity for multi-tenancy. All resources
    (users, sessions, API keys, etc.) belong to a tenant.
    """

    id: UUID
    name: str
    slug: str
    subscription_tier: SubscriptionTier = SubscriptionTier.FREE
    subscription_status: SubscriptionStatus = SubscriptionStatus.ACTIVE
    stripe_customer_id: Optional[str] = None
    tokens_used_month: int = 0
    tokens_limit_month: int = 10_000
    rate_limit_rpm: int = 60
    settings: dict[str, Any] = field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @property
    def is_active(self) -> bool:
        """Check if tenant can use the API."""
        return self.subscription_status.is_active

    @property
    def tokens_remaining(self) -> int:
        """Tokens remaining this billing period."""
        if self.tokens_limit_month == 0:  # Unlimited
            return float("inf")  # type: ignore
        return max(0, self.tokens_limit_month - self.tokens_used_month)

    @property
    def usage_percentage(self) -> float:
        """Percentage of token quota used."""
        if self.tokens_limit_month == 0:
            return 0.0
        return min(100.0, (self.tokens_used_month / self.tokens_limit_month) * 100)

    def can_use_tokens(self, count: int) -> bool:
        """Check if tenant can use specified number of tokens."""
        if self.tokens_limit_month == 0:  # Unlimited
            return True
        return self.tokens_used_month + count <= self.tokens_limit_month


@dataclass(frozen=True)
class TenantUser:
    """
    Represents a user within a tenant.

    Users belong to exactly one tenant and have a role
    that determines their permissions.
    """

    id: UUID
    tenant_id: UUID
    email: str
    name: Optional[str] = None
    role: UserRole = UserRole.MEMBER
    is_active: bool = True
    email_verified: bool = False
    external_auth_id: Optional[str] = None
    external_auth_provider: Optional[str] = None
    last_login_at: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass(frozen=True)
class ApiKey:
    """
    Represents an API key for programmatic access.

    Keys are scoped to a tenant and optionally a user.
    The actual key is never stored - only a hash.
    """

    id: UUID
    tenant_id: UUID
    key_prefix: str  # First 8 chars for identification
    name: str
    scopes: list[str] = field(default_factory=lambda: ["read", "write"])
    user_id: Optional[UUID] = None
    rate_limit_rpm: Optional[int] = None  # Override tenant default
    tokens_limit_request: Optional[int] = None
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    use_count: int = 0
    is_active: bool = True
    created_at: Optional[datetime] = None

    @property
    def is_expired(self) -> bool:
        """Check if key has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at

    @property
    def is_valid(self) -> bool:
        """Check if key can be used."""
        return self.is_active and not self.is_expired

    def has_scope(self, scope: str) -> bool:
        """Check if key has specified scope."""
        return scope in self.scopes


@dataclass(frozen=True)
class Session:
    """
    Represents a K-Gent conversation session.

    Sessions track conversation state and usage.
    """

    id: UUID
    tenant_id: UUID
    user_id: Optional[UUID] = None
    title: Optional[str] = None
    agent_type: str = "kgent"
    status: Optional["SessionStatus"] = None  # Set to ACTIVE in __post_init__
    context: dict[str, Any] = field(default_factory=dict)
    message_count: int = 0
    tokens_used: int = 0
    last_message_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    def __post_init__(self) -> None:
        # Handle status default
        if self.status is None:
            object.__setattr__(self, "status", SessionStatus.ACTIVE)
        elif isinstance(self.status, str):
            object.__setattr__(self, "status", SessionStatus(self.status))

    @property
    def is_active(self) -> bool:
        """Check if session is active."""
        return self.status == SessionStatus.ACTIVE


class UsageEventType(Enum):
    """Types of billable usage events."""

    AGENTESE_INVOKE = "agentese_invoke"
    KGENT_MESSAGE = "kgent_message"
    SESSION_CREATE = "session_create"
    LLM_CALL = "llm_call"
    STORAGE_WRITE = "storage_write"
    STORAGE_READ = "storage_read"
    EMBEDDING = "embedding"
    API_CALL = "api_call"


@dataclass(frozen=True)
class UsageEvent:
    """
    Represents a billable usage event.

    These feed into OpenMeter/Lago for usage-based billing.
    """

    id: UUID
    tenant_id: UUID
    event_type: UsageEventType
    source: str  # api, playground, sdk
    billing_period: str  # YYYY-MM format
    tokens_in: int = 0
    tokens_out: int = 0
    storage_bytes: int = 0
    compute_ms: int = 0
    session_id: Optional[UUID] = None
    api_key_id: Optional[UUID] = None
    agentese_path: Optional[str] = None
    created_at: Optional[datetime] = None

    @property
    def total_tokens(self) -> int:
        """Total tokens consumed by this event."""
        return self.tokens_in + self.tokens_out
