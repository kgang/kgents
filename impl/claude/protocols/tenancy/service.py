"""
Tenant service for kgents SaaS.

Provides CRUD operations for tenants, users, sessions, and usage tracking.
All operations respect RLS through tenant context.

AGENTESE: self.tenant.{manifest|create|update|delete}
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Optional, Protocol
from uuid import UUID, uuid4

from protocols.tenancy.models import (
    Session,
    SubscriptionStatus,
    SubscriptionTier,
    Tenant,
    TenantUser,
    UsageEvent,
    UsageEventType,
    UserRole,
)


class TenantServiceProtocol(Protocol):
    """Protocol for tenant service operations."""

    async def create_tenant(
        self,
        name: str,
        slug: str,
        tier: SubscriptionTier = SubscriptionTier.FREE,
    ) -> Tenant:
        """Create a new tenant."""
        ...

    async def get_tenant(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        ...

    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        ...

    async def update_tenant(
        self,
        tenant_id: UUID,
        name: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Optional[Tenant]:
        """Update tenant properties."""
        ...

    async def create_user(
        self,
        tenant_id: UUID,
        email: str,
        name: str | None = None,
        role: UserRole = UserRole.MEMBER,
    ) -> TenantUser:
        """Create a user in a tenant."""
        ...

    async def get_user(self, user_id: UUID) -> Optional[TenantUser]:
        """Get user by ID."""
        ...

    async def create_session(
        self,
        tenant_id: UUID,
        user_id: UUID | None = None,
        agent_type: str = "kgent",
    ) -> Session:
        """Create a new session."""
        ...

    async def record_usage(
        self,
        tenant_id: UUID,
        event_type: UsageEventType,
        source: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        session_id: UUID | None = None,
        agentese_path: str | None = None,
    ) -> UsageEvent:
        """Record a usage event."""
        ...


class TenantService:
    """
    In-memory tenant service for development.

    Production should use database-backed implementation with
    connection pooling and proper RLS context setting.
    """

    def __init__(self) -> None:
        """Initialize with empty stores."""
        self._tenants: dict[UUID, Tenant] = {}
        self._tenants_by_slug: dict[str, UUID] = {}
        self._users: dict[UUID, TenantUser] = {}
        self._sessions: dict[UUID, Session] = {}
        self._usage_events: list[UsageEvent] = []

        # Create default dev tenant
        self._create_default_tenant()

    def _create_default_tenant(self) -> None:
        """Create default development tenant."""
        dev_tenant = Tenant(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            name="Development Tenant",
            slug="dev",
            subscription_tier=SubscriptionTier.ENTERPRISE,
            subscription_status=SubscriptionStatus.ACTIVE,
            tokens_limit_month=1_000_000,
            rate_limit_rpm=1000,
            created_at=datetime.utcnow(),
        )
        self._tenants[dev_tenant.id] = dev_tenant
        self._tenants_by_slug[dev_tenant.slug] = dev_tenant.id

        # Create dev user
        dev_user = TenantUser(
            id=UUID("00000000-0000-0000-0000-000000000001"),
            tenant_id=dev_tenant.id,
            email="dev@kgents.local",
            name="Developer",
            role=UserRole.OWNER,
            is_active=True,
            email_verified=True,
            created_at=datetime.utcnow(),
        )
        self._users[dev_user.id] = dev_user

    async def create_tenant(
        self,
        name: str,
        slug: str,
        tier: SubscriptionTier = SubscriptionTier.FREE,
    ) -> Tenant:
        """
        Create a new tenant.

        Args:
            name: Display name
            slug: URL-safe identifier (must be unique)
            tier: Subscription tier

        Returns:
            Created Tenant

        Raises:
            ValueError: If slug already exists
        """
        if slug in self._tenants_by_slug:
            raise ValueError(f"Tenant with slug '{slug}' already exists")

        tenant = Tenant(
            id=uuid4(),
            name=name,
            slug=slug,
            subscription_tier=tier,
            subscription_status=SubscriptionStatus.ACTIVE,
            tokens_limit_month=tier.tokens_limit,
            rate_limit_rpm=tier.rate_limit_rpm,
            created_at=datetime.utcnow(),
        )

        self._tenants[tenant.id] = tenant
        self._tenants_by_slug[tenant.slug] = tenant.id

        return tenant

    async def get_tenant(self, tenant_id: UUID) -> Optional[Tenant]:
        """Get tenant by ID."""
        return self._tenants.get(tenant_id)

    async def get_tenant_by_slug(self, slug: str) -> Optional[Tenant]:
        """Get tenant by slug."""
        tenant_id = self._tenants_by_slug.get(slug)
        if tenant_id is None:
            return None
        return self._tenants.get(tenant_id)

    async def update_tenant(
        self,
        tenant_id: UUID,
        name: str | None = None,
        settings: dict[str, Any] | None = None,
    ) -> Optional[Tenant]:
        """
        Update tenant properties.

        Args:
            tenant_id: Tenant to update
            name: New name (optional)
            settings: New settings to merge (optional)

        Returns:
            Updated Tenant or None if not found
        """
        tenant = self._tenants.get(tenant_id)
        if tenant is None:
            return None

        # Create updated tenant (immutable dataclass)
        new_settings = {**tenant.settings}
        if settings:
            new_settings.update(settings)

        updated = Tenant(
            id=tenant.id,
            name=name or tenant.name,
            slug=tenant.slug,
            subscription_tier=tenant.subscription_tier,
            subscription_status=tenant.subscription_status,
            stripe_customer_id=tenant.stripe_customer_id,
            tokens_used_month=tenant.tokens_used_month,
            tokens_limit_month=tenant.tokens_limit_month,
            rate_limit_rpm=tenant.rate_limit_rpm,
            settings=new_settings,
            created_at=tenant.created_at,
            updated_at=datetime.utcnow(),
        )

        self._tenants[tenant_id] = updated
        return updated

    async def increment_usage(
        self,
        tenant_id: UUID,
        tokens: int,
    ) -> Optional[Tenant]:
        """
        Increment token usage for a tenant.

        Args:
            tenant_id: Tenant to update
            tokens: Number of tokens to add

        Returns:
            Updated Tenant or None if not found
        """
        tenant = self._tenants.get(tenant_id)
        if tenant is None:
            return None

        updated = Tenant(
            id=tenant.id,
            name=tenant.name,
            slug=tenant.slug,
            subscription_tier=tenant.subscription_tier,
            subscription_status=tenant.subscription_status,
            stripe_customer_id=tenant.stripe_customer_id,
            tokens_used_month=tenant.tokens_used_month + tokens,
            tokens_limit_month=tenant.tokens_limit_month,
            rate_limit_rpm=tenant.rate_limit_rpm,
            settings=tenant.settings,
            created_at=tenant.created_at,
            updated_at=datetime.utcnow(),
        )

        self._tenants[tenant_id] = updated
        return updated

    async def create_user(
        self,
        tenant_id: UUID,
        email: str,
        name: str | None = None,
        role: UserRole = UserRole.MEMBER,
    ) -> TenantUser:
        """
        Create a user in a tenant.

        Args:
            tenant_id: Tenant the user belongs to
            email: User email
            name: Display name
            role: User role

        Returns:
            Created TenantUser

        Raises:
            ValueError: If tenant doesn't exist
        """
        if tenant_id not in self._tenants:
            raise ValueError(f"Tenant {tenant_id} does not exist")

        user = TenantUser(
            id=uuid4(),
            tenant_id=tenant_id,
            email=email,
            name=name,
            role=role,
            is_active=True,
            created_at=datetime.utcnow(),
        )

        self._users[user.id] = user
        return user

    async def get_user(self, user_id: UUID) -> Optional[TenantUser]:
        """Get user by ID."""
        return self._users.get(user_id)

    async def get_user_by_email(
        self, tenant_id: UUID, email: str
    ) -> Optional[TenantUser]:
        """Get user by email within a tenant."""
        for user in self._users.values():
            if user.tenant_id == tenant_id and user.email == email:
                return user
        return None

    async def list_users(self, tenant_id: UUID) -> list[TenantUser]:
        """List all users in a tenant."""
        return [u for u in self._users.values() if u.tenant_id == tenant_id]

    async def create_session(
        self,
        tenant_id: UUID,
        user_id: UUID | None = None,
        agent_type: str = "kgent",
        title: str | None = None,
    ) -> Session:
        """
        Create a new session.

        Args:
            tenant_id: Tenant that owns the session
            user_id: User who created the session
            agent_type: Type of agent (kgent, agentese, custom)
            title: Session title

        Returns:
            Created Session
        """
        session = Session(
            id=uuid4(),
            tenant_id=tenant_id,
            user_id=user_id,
            title=title,
            agent_type=agent_type,
            created_at=datetime.utcnow(),
        )

        self._sessions[session.id] = session
        return session

    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Get session by ID."""
        return self._sessions.get(session_id)

    async def list_sessions(
        self, tenant_id: UUID, user_id: UUID | None = None
    ) -> list[Session]:
        """List sessions for a tenant, optionally filtered by user."""
        sessions = [s for s in self._sessions.values() if s.tenant_id == tenant_id]
        if user_id:
            sessions = [s for s in sessions if s.user_id == user_id]
        return sorted(sessions, key=lambda s: s.created_at or datetime.min, reverse=True)

    async def update_session(
        self,
        session_id: UUID,
        tokens_used: int | None = None,
        message_count: int | None = None,
    ) -> Optional[Session]:
        """Update session statistics."""
        session = self._sessions.get(session_id)
        if session is None:
            return None

        updated = Session(
            id=session.id,
            tenant_id=session.tenant_id,
            user_id=session.user_id,
            title=session.title,
            agent_type=session.agent_type,
            status=session.status,
            context=session.context,
            message_count=(
                message_count
                if message_count is not None
                else session.message_count
            ),
            tokens_used=(
                tokens_used if tokens_used is not None else session.tokens_used
            ),
            last_message_at=datetime.utcnow(),
            created_at=session.created_at,
        )

        self._sessions[session_id] = updated
        return updated

    async def record_usage(
        self,
        tenant_id: UUID,
        event_type: UsageEventType,
        source: str,
        tokens_in: int = 0,
        tokens_out: int = 0,
        session_id: UUID | None = None,
        agentese_path: str | None = None,
    ) -> UsageEvent:
        """
        Record a usage event for billing.

        Args:
            tenant_id: Tenant that incurred usage
            event_type: Type of billable event
            source: Where the event originated
            tokens_in: Input tokens consumed
            tokens_out: Output tokens consumed
            session_id: Associated session
            agentese_path: AGENTESE path invoked

        Returns:
            Created UsageEvent
        """
        now = datetime.utcnow()
        billing_period = now.strftime("%Y-%m")

        event = UsageEvent(
            id=uuid4(),
            tenant_id=tenant_id,
            event_type=event_type,
            source=source,
            billing_period=billing_period,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            session_id=session_id,
            agentese_path=agentese_path,
            created_at=now,
        )

        self._usage_events.append(event)

        # Update tenant usage counter
        await self.increment_usage(tenant_id, tokens_in + tokens_out)

        return event

    async def get_usage_summary(
        self,
        tenant_id: UUID,
        billing_period: str | None = None,
    ) -> dict[str, int]:
        """
        Get usage summary for a tenant.

        Args:
            tenant_id: Tenant to get usage for
            billing_period: Optional period filter (YYYY-MM)

        Returns:
            Dict with usage totals
        """
        if billing_period is None:
            billing_period = datetime.utcnow().strftime("%Y-%m")

        events = [
            e
            for e in self._usage_events
            if e.tenant_id == tenant_id and e.billing_period == billing_period
        ]

        return {
            "tokens_in": sum(e.tokens_in for e in events),
            "tokens_out": sum(e.tokens_out for e in events),
            "total_tokens": sum(e.total_tokens for e in events),
            "event_count": len(events),
        }
