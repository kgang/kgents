"""
Multi-tenant infrastructure for kgents SaaS.

This module provides:
- Tenant management (CRUD operations)
- User management within tenants
- API key management
- Tenant context for RLS
- Usage tracking

AGENTESE: self.tenant.*
"""

from protocols.tenancy.api_keys import (
    ApiKeyService,
    generate_api_key,
    hash_api_key,
    validate_api_key_format,
)
from protocols.tenancy.context import (
    TenantContext,
    clear_tenant_context,
    get_current_tenant,
    require_tenant,
    set_tenant_context,
)
from protocols.tenancy.models import (
    ApiKey,
    Session,
    SubscriptionStatus,
    SubscriptionTier,
    Tenant,
    TenantUser,
    UsageEvent,
    UserRole,
)
from protocols.tenancy.service import (
    TenantService,
    TenantServiceProtocol,
)

__all__ = [
    # Context
    "TenantContext",
    "get_current_tenant",
    "set_tenant_context",
    "clear_tenant_context",
    "require_tenant",
    # Models
    "Tenant",
    "TenantUser",
    "ApiKey",
    "Session",
    "UsageEvent",
    "SubscriptionTier",
    "SubscriptionStatus",
    "UserRole",
    # Service
    "TenantService",
    "TenantServiceProtocol",
    # API Keys
    "ApiKeyService",
    "generate_api_key",
    "hash_api_key",
    "validate_api_key_format",
]
