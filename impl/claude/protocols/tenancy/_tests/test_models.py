"""Tests for tenancy models."""

from __future__ import annotations

from datetime import datetime, timedelta
from uuid import uuid4

import pytest

from protocols.tenancy.models import (
    ApiKey,
    Session,
    SubscriptionStatus,
    SubscriptionTier,
    Tenant,
    TenantUser,
    UsageEvent,
    UsageEventType,
    UserRole,
)


class TestSubscriptionTier:
    """Tests for SubscriptionTier enum."""

    def test_free_tier_limits(self) -> None:
        """Test FREE tier default limits."""
        assert SubscriptionTier.FREE.tokens_limit == 10_000
        assert SubscriptionTier.FREE.rate_limit_rpm == 60

    def test_pro_tier_limits(self) -> None:
        """Test PRO tier default limits."""
        assert SubscriptionTier.PRO.tokens_limit == 100_000
        assert SubscriptionTier.PRO.rate_limit_rpm == 600

    def test_enterprise_tier_limits(self) -> None:
        """Test ENTERPRISE tier default limits."""
        assert SubscriptionTier.ENTERPRISE.tokens_limit == 1_000_000
        assert SubscriptionTier.ENTERPRISE.rate_limit_rpm == 6000


class TestSubscriptionStatus:
    """Tests for SubscriptionStatus enum."""

    def test_active_statuses(self) -> None:
        """Test which statuses allow API access."""
        assert SubscriptionStatus.ACTIVE.is_active
        assert SubscriptionStatus.TRIALING.is_active
        assert SubscriptionStatus.PAST_DUE.is_active  # Grace period

    def test_inactive_statuses(self) -> None:
        """Test which statuses block API access."""
        assert not SubscriptionStatus.CANCELED.is_active
        assert not SubscriptionStatus.PAUSED.is_active


class TestUserRole:
    """Tests for UserRole enum."""

    def test_owner_permissions(self) -> None:
        """Test OWNER has all permissions."""
        assert UserRole.OWNER.can_manage_users
        assert UserRole.OWNER.can_manage_billing
        assert UserRole.OWNER.can_create_api_keys

    def test_admin_permissions(self) -> None:
        """Test ADMIN permissions."""
        assert UserRole.ADMIN.can_manage_users
        assert not UserRole.ADMIN.can_manage_billing
        assert UserRole.ADMIN.can_create_api_keys

    def test_member_permissions(self) -> None:
        """Test MEMBER permissions."""
        assert not UserRole.MEMBER.can_manage_users
        assert not UserRole.MEMBER.can_manage_billing
        assert UserRole.MEMBER.can_create_api_keys

    def test_readonly_permissions(self) -> None:
        """Test READONLY permissions."""
        assert not UserRole.READONLY.can_manage_users
        assert not UserRole.READONLY.can_manage_billing
        assert not UserRole.READONLY.can_create_api_keys


class TestTenant:
    """Tests for Tenant model."""

    def test_tenant_creation(self) -> None:
        """Test basic tenant creation."""
        tenant = Tenant(
            id=uuid4(),
            name="Test Corp",
            slug="test-corp",
        )

        assert tenant.name == "Test Corp"
        assert tenant.slug == "test-corp"
        assert tenant.subscription_tier == SubscriptionTier.FREE
        assert tenant.is_active

    def test_tenant_is_active(self) -> None:
        """Test is_active property."""
        active = Tenant(
            id=uuid4(),
            name="Active",
            slug="active",
            subscription_status=SubscriptionStatus.ACTIVE,
        )
        assert active.is_active

        canceled = Tenant(
            id=uuid4(),
            name="Canceled",
            slug="canceled",
            subscription_status=SubscriptionStatus.CANCELED,
        )
        assert not canceled.is_active

    def test_tokens_remaining(self) -> None:
        """Test tokens_remaining calculation."""
        tenant = Tenant(
            id=uuid4(),
            name="Test",
            slug="test",
            tokens_used_month=3000,
            tokens_limit_month=10000,
        )

        assert tenant.tokens_remaining == 7000

    def test_tokens_remaining_unlimited(self) -> None:
        """Test tokens_remaining with unlimited plan."""
        tenant = Tenant(
            id=uuid4(),
            name="Enterprise",
            slug="enterprise",
            tokens_limit_month=0,  # Unlimited
        )

        assert tenant.tokens_remaining == float("inf")

    def test_usage_percentage(self) -> None:
        """Test usage_percentage calculation."""
        tenant = Tenant(
            id=uuid4(),
            name="Test",
            slug="test",
            tokens_used_month=5000,
            tokens_limit_month=10000,
        )

        assert tenant.usage_percentage == 50.0

    def test_can_use_tokens(self) -> None:
        """Test can_use_tokens method."""
        tenant = Tenant(
            id=uuid4(),
            name="Test",
            slug="test",
            tokens_used_month=9000,
            tokens_limit_month=10000,
        )

        assert tenant.can_use_tokens(1000)  # Exactly at limit
        assert not tenant.can_use_tokens(1001)  # Over limit


class TestTenantUser:
    """Tests for TenantUser model."""

    def test_user_creation(self) -> None:
        """Test basic user creation."""
        tenant_id = uuid4()
        user = TenantUser(
            id=uuid4(),
            tenant_id=tenant_id,
            email="user@example.com",
            name="Test User",
            role=UserRole.MEMBER,
        )

        assert user.email == "user@example.com"
        assert user.tenant_id == tenant_id
        assert user.role == UserRole.MEMBER
        assert user.is_active


class TestApiKey:
    """Tests for ApiKey model."""

    def test_api_key_creation(self) -> None:
        """Test basic API key creation."""
        key = ApiKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_prefix="kg_abc12",
            name="Test Key",
        )

        assert key.name == "Test Key"
        assert key.is_valid
        assert key.has_scope("read")
        assert key.has_scope("write")

    def test_api_key_expiration(self) -> None:
        """Test API key expiration."""
        # Not expired
        key = ApiKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_prefix="kg_abc12",
            name="Valid Key",
            expires_at=datetime.utcnow() + timedelta(days=30),
        )
        assert not key.is_expired
        assert key.is_valid

        # Expired
        expired_key = ApiKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_prefix="kg_def34",
            name="Expired Key",
            expires_at=datetime.utcnow() - timedelta(days=1),
        )
        assert expired_key.is_expired
        assert not expired_key.is_valid

    def test_api_key_scopes(self) -> None:
        """Test API key scope checking."""
        key = ApiKey(
            id=uuid4(),
            tenant_id=uuid4(),
            key_prefix="kg_abc12",
            name="Limited Key",
            scopes=["read"],
        )

        assert key.has_scope("read")
        assert not key.has_scope("write")
        assert not key.has_scope("admin")


class TestSession:
    """Tests for Session model."""

    def test_session_creation(self) -> None:
        """Test basic session creation."""
        session = Session(
            id=uuid4(),
            tenant_id=uuid4(),
        )

        assert session.agent_type == "kgent"
        assert session.status == "active"
        assert session.is_active
        assert session.message_count == 0


class TestUsageEvent:
    """Tests for UsageEvent model."""

    def test_usage_event_creation(self) -> None:
        """Test basic usage event creation."""
        event = UsageEvent(
            id=uuid4(),
            tenant_id=uuid4(),
            event_type=UsageEventType.AGENTESE_INVOKE,
            source="api",
            billing_period="2025-12",
            tokens_in=100,
            tokens_out=50,
        )

        assert event.total_tokens == 150
        assert event.billing_period == "2025-12"
