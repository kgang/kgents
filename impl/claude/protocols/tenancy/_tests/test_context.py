"""Tests for tenant context management."""

from __future__ import annotations

from uuid import uuid4

import pytest

from protocols.tenancy.context import (
    InsufficientPermissionError,
    TenantContext,
    TenantNotSetError,
    clear_tenant_context,
    get_current_api_key,
    get_current_tenant,
    get_current_user,
    get_tenant_context,
    require_scope,
    require_tenant,
    set_tenant_context,
    tenant_context,
)
from protocols.tenancy.models import (
    ApiKey,
    SubscriptionTier,
    Tenant,
    TenantUser,
    UserRole,
)


@pytest.fixture
def sample_tenant() -> Tenant:
    """Create a sample tenant for testing."""
    return Tenant(
        id=uuid4(),
        name="Test Tenant",
        slug="test",
        subscription_tier=SubscriptionTier.PRO,
    )


@pytest.fixture
def sample_user(sample_tenant: Tenant) -> TenantUser:
    """Create a sample user for testing."""
    return TenantUser(
        id=uuid4(),
        tenant_id=sample_tenant.id,
        email="test@example.com",
        role=UserRole.MEMBER,
    )


@pytest.fixture
def sample_api_key(sample_tenant: Tenant) -> ApiKey:
    """Create a sample API key for testing."""
    return ApiKey(
        id=uuid4(),
        tenant_id=sample_tenant.id,
        key_prefix="kg_test1",
        name="Test Key",
        scopes=["read", "write"],
    )


@pytest.fixture(autouse=True)
def clear_context() -> None:
    """Clear context before and after each test."""
    clear_tenant_context()
    yield  # type: ignore
    clear_tenant_context()


class TestTenantContext:
    """Tests for TenantContext dataclass."""

    def test_context_properties(
        self,
        sample_tenant: Tenant,
        sample_user: TenantUser,
        sample_api_key: ApiKey,
    ) -> None:
        """Test TenantContext properties."""
        ctx = TenantContext(
            tenant=sample_tenant,
            user=sample_user,
            api_key=sample_api_key,
        )

        assert ctx.tenant_id == sample_tenant.id
        assert ctx.user_id == sample_user.id
        assert ctx.is_authenticated
        assert ctx.can_write  # API key has write scope

    def test_context_without_user(self, sample_tenant: Tenant) -> None:
        """Test context without user."""
        ctx = TenantContext(tenant=sample_tenant)

        assert ctx.user_id is None
        assert not ctx.is_authenticated
        assert not ctx.can_write

    def test_context_with_readonly_user(self, sample_tenant: Tenant) -> None:
        """Test context with readonly user."""
        readonly_user = TenantUser(
            id=uuid4(),
            tenant_id=sample_tenant.id,
            email="readonly@example.com",
            role=UserRole.READONLY,
        )
        ctx = TenantContext(tenant=sample_tenant, user=readonly_user)

        assert ctx.is_authenticated
        assert not ctx.can_write

    def test_can_admin_with_admin_key(self, sample_tenant: Tenant) -> None:
        """Test admin check with admin-scoped key."""
        admin_key = ApiKey(
            id=uuid4(),
            tenant_id=sample_tenant.id,
            key_prefix="kg_admin",
            name="Admin Key",
            scopes=["read", "write", "admin"],
        )
        ctx = TenantContext(tenant=sample_tenant, api_key=admin_key)

        assert ctx.can_admin


class TestContextFunctions:
    """Tests for context getter/setter functions."""

    def test_set_and_get_tenant(self, sample_tenant: Tenant) -> None:
        """Test setting and getting tenant context."""
        assert get_current_tenant() is None

        set_tenant_context(sample_tenant)

        assert get_current_tenant() == sample_tenant

    def test_set_full_context(
        self,
        sample_tenant: Tenant,
        sample_user: TenantUser,
        sample_api_key: ApiKey,
    ) -> None:
        """Test setting full context."""
        ctx = set_tenant_context(
            sample_tenant,
            user=sample_user,
            api_key=sample_api_key,
        )

        assert get_current_tenant() == sample_tenant
        assert get_current_user() == sample_user
        assert get_current_api_key() == sample_api_key
        assert get_tenant_context() == ctx

    def test_clear_context(self, sample_tenant: Tenant) -> None:
        """Test clearing context."""
        set_tenant_context(sample_tenant)
        assert get_current_tenant() is not None

        clear_tenant_context()

        assert get_current_tenant() is None
        assert get_tenant_context() is None


class TestRequireTenantDecorator:
    """Tests for require_tenant decorator."""

    def test_require_tenant_with_context(self, sample_tenant: Tenant) -> None:
        """Test decorated function with context set."""

        @require_tenant
        def protected_function() -> str:
            return "success"

        set_tenant_context(sample_tenant)
        result = protected_function()

        assert result == "success"

    def test_require_tenant_without_context(self) -> None:
        """Test decorated function without context."""

        @require_tenant
        def protected_function() -> str:
            return "success"

        with pytest.raises(TenantNotSetError) as exc_info:
            protected_function()

        assert "protected_function" in str(exc_info.value)


class TestRequireScopeDecorator:
    """Tests for require_scope decorator."""

    def test_require_scope_with_valid_scope(
        self,
        sample_tenant: Tenant,
        sample_api_key: ApiKey,
    ) -> None:
        """Test with valid scope."""

        @require_scope("write")
        def write_operation() -> str:
            return "written"

        set_tenant_context(sample_tenant, api_key=sample_api_key)
        result = write_operation()

        assert result == "written"

    def test_require_scope_missing_scope(
        self,
        sample_tenant: Tenant,
    ) -> None:
        """Test with missing scope."""
        limited_key = ApiKey(
            id=uuid4(),
            tenant_id=sample_tenant.id,
            key_prefix="kg_read1",
            name="Read Only Key",
            scopes=["read"],
        )

        @require_scope("admin")
        def admin_operation() -> str:
            return "admin action"

        set_tenant_context(sample_tenant, api_key=limited_key)

        with pytest.raises(InsufficientPermissionError) as exc_info:
            admin_operation()

        assert "admin" in str(exc_info.value)


class TestTenantContextManager:
    """Tests for tenant_context context manager."""

    def test_context_manager_sets_context(self, sample_tenant: Tenant) -> None:
        """Test context manager sets and clears context."""
        assert get_current_tenant() is None

        with tenant_context(sample_tenant) as ctx:
            assert get_current_tenant() == sample_tenant
            assert ctx.tenant == sample_tenant

        # Context should be cleared after exiting
        assert get_current_tenant() is None

    def test_context_manager_restores_previous(
        self,
        sample_tenant: Tenant,
    ) -> None:
        """Test context manager restores previous context."""
        other_tenant = Tenant(
            id=uuid4(),
            name="Other Tenant",
            slug="other",
        )

        set_tenant_context(other_tenant)

        with tenant_context(sample_tenant):
            assert get_current_tenant() == sample_tenant

        # Should restore previous context
        assert get_current_tenant() == other_tenant

    @pytest.mark.asyncio
    async def test_async_context_manager(self, sample_tenant: Tenant) -> None:
        """Test async context manager."""
        assert get_current_tenant() is None

        async with tenant_context(sample_tenant) as ctx:
            assert get_current_tenant() == sample_tenant
            assert ctx.tenant_id == sample_tenant.id

        assert get_current_tenant() is None
