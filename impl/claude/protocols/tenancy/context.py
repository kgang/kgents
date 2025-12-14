"""
Tenant context management for RLS (Row-Level Security).

This module provides the tenant context that flows through the application:
1. API Gateway extracts tenant from JWT/API key
2. Context is set at the start of each request
3. All database queries are automatically tenant-filtered via RLS
4. Context is cleared when request completes

Thread-safe via contextvars for async compatibility.
"""

from __future__ import annotations

from contextvars import ContextVar
from dataclasses import dataclass
from functools import wraps
from typing import TYPE_CHECKING, Any, Callable, Optional, TypeVar
from uuid import UUID

if TYPE_CHECKING:
    from protocols.tenancy.models import ApiKey, Tenant, TenantUser

# Context variables for tenant state
_current_tenant: ContextVar[Optional["Tenant"]] = ContextVar(
    "current_tenant", default=None
)
_current_user: ContextVar[Optional["TenantUser"]] = ContextVar(
    "current_user", default=None
)
_current_api_key: ContextVar[Optional["ApiKey"]] = ContextVar(
    "current_api_key", default=None
)


@dataclass
class TenantContext:
    """
    Immutable context for the current request's tenant.

    Contains all information needed for tenant-scoped operations:
    - tenant: The organization
    - user: The authenticated user (if any)
    - api_key: The API key used (if any)
    """

    tenant: "Tenant"
    user: Optional["TenantUser"] = None
    api_key: Optional["ApiKey"] = None

    @property
    def tenant_id(self) -> UUID:
        """Get the tenant ID."""
        return UUID(str(self.tenant.id))

    @property
    def user_id(self) -> Optional[UUID]:
        """Get the user ID if present."""
        return self.user.id if self.user else None

    @property
    def is_authenticated(self) -> bool:
        """Check if request is authenticated."""
        return self.user is not None or self.api_key is not None

    @property
    def can_write(self) -> bool:
        """Check if context has write permission."""
        if self.api_key:
            return bool(self.api_key.has_scope("write"))
        if self.user:
            return bool(self.user.role.value != "readonly")
        return False

    @property
    def can_admin(self) -> bool:
        """Check if context has admin permission."""
        if self.api_key:
            return bool(self.api_key.has_scope("admin"))
        if self.user:
            return bool(self.user.role.can_manage_users)
        return False


def set_tenant_context(
    tenant: "Tenant",
    user: Optional["TenantUser"] = None,
    api_key: Optional["ApiKey"] = None,
) -> TenantContext:
    """
    Set the tenant context for the current request.

    Called by middleware/dependency injection at request start.

    Args:
        tenant: The authenticated tenant
        user: The authenticated user (optional)
        api_key: The API key used (optional)

    Returns:
        The TenantContext that was set
    """
    _current_tenant.set(tenant)
    _current_user.set(user)
    _current_api_key.set(api_key)
    return TenantContext(tenant=tenant, user=user, api_key=api_key)


def get_current_tenant() -> Optional["Tenant"]:
    """
    Get the current tenant from context.

    Returns:
        The current Tenant, or None if no tenant is set
    """
    return _current_tenant.get()


def get_current_user() -> Optional["TenantUser"]:
    """
    Get the current user from context.

    Returns:
        The current TenantUser, or None if no user is set
    """
    return _current_user.get()


def get_current_api_key() -> Optional["ApiKey"]:
    """
    Get the current API key from context.

    Returns:
        The current ApiKey, or None if no API key is set
    """
    return _current_api_key.get()


def get_tenant_context() -> Optional[TenantContext]:
    """
    Get the full tenant context.

    Returns:
        TenantContext if tenant is set, None otherwise
    """
    tenant = _current_tenant.get()
    if tenant is None:
        return None
    return TenantContext(
        tenant=tenant,
        user=_current_user.get(),
        api_key=_current_api_key.get(),
    )


def clear_tenant_context() -> None:
    """
    Clear the tenant context.

    Called at the end of each request to prevent context leaking.
    """
    _current_tenant.set(None)
    _current_user.set(None)
    _current_api_key.set(None)


class TenantNotSetError(Exception):
    """Raised when tenant context is required but not set."""

    def __init__(self, operation: str = "this operation"):
        self.operation = operation
        super().__init__(f"Tenant context required for {operation}")


class InsufficientPermissionError(Exception):
    """Raised when user lacks required permission."""

    def __init__(self, required: str, operation: str = "this operation"):
        self.required = required
        self.operation = operation
        super().__init__(f"Permission '{required}' required for {operation}")


F = TypeVar("F", bound=Callable[..., Any])


def require_tenant(func: F) -> F:
    """
    Decorator that requires tenant context.

    Raises TenantNotSetError if called without tenant context.

    Example:
        @require_tenant
        def get_sessions(tenant_id: UUID) -> list[Session]:
            ...
    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if get_current_tenant() is None:
            raise TenantNotSetError(func.__name__)
        return func(*args, **kwargs)

    return wrapper  # type: ignore


def require_scope(scope: str) -> Callable[[F], F]:
    """
    Decorator that requires specific API key scope.

    Args:
        scope: Required scope (read, write, admin, billing)

    Raises:
        TenantNotSetError: If no tenant context
        InsufficientPermissionError: If scope not present

    Example:
        @require_scope("admin")
        def delete_user(user_id: UUID) -> None:
            ...
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            ctx = get_tenant_context()
            if ctx is None:
                raise TenantNotSetError(func.__name__)
            if ctx.api_key and not ctx.api_key.has_scope(scope):
                raise InsufficientPermissionError(scope, func.__name__)
            return func(*args, **kwargs)

        return wrapper  # type: ignore

    return decorator


class tenant_context:
    """
    Context manager for setting tenant context.

    Useful for background jobs, tests, and CLI operations.

    Example:
        async with tenant_context(tenant):
            await process_batch()
    """

    def __init__(
        self,
        tenant: "Tenant",
        user: Optional["TenantUser"] = None,
        api_key: Optional["ApiKey"] = None,
    ):
        self.tenant = tenant
        self.user = user
        self.api_key = api_key
        self._previous_tenant: Optional["Tenant"] = None
        self._previous_user: Optional["TenantUser"] = None
        self._previous_api_key: Optional["ApiKey"] = None

    def __enter__(self) -> TenantContext:
        # Save previous context
        self._previous_tenant = _current_tenant.get()
        self._previous_user = _current_user.get()
        self._previous_api_key = _current_api_key.get()
        # Set new context
        return set_tenant_context(self.tenant, self.user, self.api_key)

    def __exit__(self, *args: Any) -> None:
        # Restore previous context
        _current_tenant.set(self._previous_tenant)
        _current_user.set(self._previous_user)
        _current_api_key.set(self._previous_api_key)

    async def __aenter__(self) -> TenantContext:
        return self.__enter__()

    async def __aexit__(self, *args: Any) -> None:
        self.__exit__(*args)
