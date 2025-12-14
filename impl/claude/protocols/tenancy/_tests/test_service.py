"""Tests for tenant service."""

from __future__ import annotations

from uuid import uuid4

import pytest
from protocols.tenancy.models import (
    SubscriptionTier,
    UsageEventType,
    UserRole,
)
from protocols.tenancy.service import TenantService


class TestTenantService:
    """Tests for TenantService."""

    @pytest.fixture
    def service(self) -> TenantService:
        """Create fresh service for each test."""
        return TenantService()

    @pytest.mark.asyncio
    async def test_default_tenant_exists(self, service: TenantService) -> None:
        """Test that default dev tenant is created."""
        tenant = await service.get_tenant_by_slug("dev")

        assert tenant is not None
        assert tenant.name == "Development Tenant"
        assert tenant.subscription_tier == SubscriptionTier.ENTERPRISE

    @pytest.mark.asyncio
    async def test_create_tenant(self, service: TenantService) -> None:
        """Test creating a new tenant."""
        tenant = await service.create_tenant(
            name="Acme Corp",
            slug="acme",
            tier=SubscriptionTier.PRO,
        )

        assert tenant.name == "Acme Corp"
        assert tenant.slug == "acme"
        assert tenant.subscription_tier == SubscriptionTier.PRO
        assert tenant.tokens_limit_month == SubscriptionTier.PRO.tokens_limit

    @pytest.mark.asyncio
    async def test_create_tenant_duplicate_slug(self, service: TenantService) -> None:
        """Test creating tenant with duplicate slug fails."""
        await service.create_tenant(name="First", slug="unique")

        with pytest.raises(ValueError, match="already exists"):
            await service.create_tenant(name="Second", slug="unique")

    @pytest.mark.asyncio
    async def test_get_tenant_by_id(self, service: TenantService) -> None:
        """Test getting tenant by ID."""
        created = await service.create_tenant(name="Test", slug="test-id")
        fetched = await service.get_tenant(created.id)

        assert fetched is not None
        assert fetched.id == created.id

    @pytest.mark.asyncio
    async def test_get_nonexistent_tenant(self, service: TenantService) -> None:
        """Test getting nonexistent tenant returns None."""
        tenant = await service.get_tenant(uuid4())

        assert tenant is None

    @pytest.mark.asyncio
    async def test_update_tenant(self, service: TenantService) -> None:
        """Test updating tenant properties."""
        created = await service.create_tenant(name="Original", slug="update-test")

        updated = await service.update_tenant(
            created.id,
            name="Updated Name",
            settings={"feature_x": True},
        )

        assert updated is not None
        assert updated.name == "Updated Name"
        assert updated.settings["feature_x"] is True

    @pytest.mark.asyncio
    async def test_increment_usage(self, service: TenantService) -> None:
        """Test incrementing token usage."""
        created = await service.create_tenant(name="Usage Test", slug="usage")
        assert created.tokens_used_month == 0

        updated = await service.increment_usage(created.id, 1000)

        assert updated is not None
        assert updated.tokens_used_month == 1000


class TestUserManagement:
    """Tests for user management."""

    @pytest.fixture
    def service(self) -> TenantService:
        return TenantService()

    @pytest.mark.asyncio
    async def test_create_user(self, service: TenantService) -> None:
        """Test creating a user."""
        tenant = await service.create_tenant(name="User Test", slug="user-test")

        user = await service.create_user(
            tenant_id=tenant.id,
            email="user@example.com",
            name="Test User",
            role=UserRole.ADMIN,
        )

        assert user.email == "user@example.com"
        assert user.tenant_id == tenant.id
        assert user.role == UserRole.ADMIN

    @pytest.mark.asyncio
    async def test_create_user_invalid_tenant(self, service: TenantService) -> None:
        """Test creating user with invalid tenant fails."""
        with pytest.raises(ValueError, match="does not exist"):
            await service.create_user(
                tenant_id=uuid4(),
                email="user@example.com",
            )

    @pytest.mark.asyncio
    async def test_get_user_by_email(self, service: TenantService) -> None:
        """Test getting user by email within tenant."""
        tenant = await service.create_tenant(name="Email Test", slug="email-test")
        await service.create_user(tenant.id, "find@example.com")

        found = await service.get_user_by_email(tenant.id, "find@example.com")

        assert found is not None
        assert found.email == "find@example.com"

    @pytest.mark.asyncio
    async def test_list_users(self, service: TenantService) -> None:
        """Test listing users in a tenant."""
        tenant = await service.create_tenant(name="List Test", slug="list-test")
        await service.create_user(tenant.id, "user1@example.com")
        await service.create_user(tenant.id, "user2@example.com")

        users = await service.list_users(tenant.id)

        assert len(users) == 2


class TestSessionManagement:
    """Tests for session management."""

    @pytest.fixture
    def service(self) -> TenantService:
        return TenantService()

    @pytest.mark.asyncio
    async def test_create_session(self, service: TenantService) -> None:
        """Test creating a session."""
        tenant = await service.create_tenant(name="Session Test", slug="session-test")

        session = await service.create_session(
            tenant_id=tenant.id,
            title="Test Session",
        )

        assert session.tenant_id == tenant.id
        assert session.title == "Test Session"
        assert session.is_active

    @pytest.mark.asyncio
    async def test_list_sessions(self, service: TenantService) -> None:
        """Test listing sessions."""
        tenant = await service.create_tenant(name="Sessions", slug="sessions")
        await service.create_session(tenant.id, title="Session 1")
        await service.create_session(tenant.id, title="Session 2")

        sessions = await service.list_sessions(tenant.id)

        assert len(sessions) == 2

    @pytest.mark.asyncio
    async def test_update_session_stats(self, service: TenantService) -> None:
        """Test updating session statistics."""
        tenant = await service.create_tenant(name="Stats", slug="stats")
        session = await service.create_session(tenant.id)

        updated = await service.update_session(
            session.id,
            tokens_used=500,
            message_count=5,
        )

        assert updated is not None
        assert updated.tokens_used == 500
        assert updated.message_count == 5


class TestUsageTracking:
    """Tests for usage tracking."""

    @pytest.fixture
    def service(self) -> TenantService:
        return TenantService()

    @pytest.mark.asyncio
    async def test_record_usage(self, service: TenantService) -> None:
        """Test recording usage event."""
        tenant = await service.create_tenant(name="Usage", slug="usage-track")

        event = await service.record_usage(
            tenant_id=tenant.id,
            event_type=UsageEventType.AGENTESE_INVOKE,
            source="api",
            tokens_in=100,
            tokens_out=50,
            agentese_path="self.soul.challenge",
        )

        assert event.tenant_id == tenant.id
        assert event.total_tokens == 150
        assert event.agentese_path == "self.soul.challenge"

    @pytest.mark.asyncio
    async def test_record_usage_updates_tenant(self, service: TenantService) -> None:
        """Test that recording usage updates tenant counter."""
        tenant = await service.create_tenant(name="Counter", slug="counter")
        initial_usage = tenant.tokens_used_month

        await service.record_usage(
            tenant_id=tenant.id,
            event_type=UsageEventType.KGENT_MESSAGE,
            source="api",
            tokens_in=100,
            tokens_out=200,
        )

        updated = await service.get_tenant(tenant.id)
        assert updated is not None
        assert updated.tokens_used_month == initial_usage + 300

    @pytest.mark.asyncio
    async def test_get_usage_summary(self, service: TenantService) -> None:
        """Test getting usage summary."""
        tenant = await service.create_tenant(name="Summary", slug="summary")

        # Record multiple events
        await service.record_usage(
            tenant.id, UsageEventType.AGENTESE_INVOKE, "api", 100, 50
        )
        await service.record_usage(
            tenant.id, UsageEventType.KGENT_MESSAGE, "api", 200, 100
        )

        summary = await service.get_usage_summary(tenant.id)

        assert summary["tokens_in"] == 300
        assert summary["tokens_out"] == 150
        assert summary["total_tokens"] == 450
        assert summary["event_count"] == 2
