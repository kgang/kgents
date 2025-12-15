"""
Configuration module for kgents SaaS infrastructure.

Provides centralized configuration for:
- NATS streaming
- OpenMeter usage billing
- Other SaaS service integrations
"""

from .clients import (
    SaaSClients,
    get_saas_clients,
    init_saas_clients,
    reset_saas_clients,
    shutdown_saas_clients,
)
from .saas import (
    SaaSConfig,
    get_cached_saas_config,
    get_saas_config,
    reset_cached_config,
)

__all__ = [
    # Config
    "SaaSConfig",
    "get_saas_config",
    "get_cached_saas_config",
    "reset_cached_config",
    # Clients
    "SaaSClients",
    "get_saas_clients",
    "init_saas_clients",
    "shutdown_saas_clients",
    "reset_saas_clients",
]
