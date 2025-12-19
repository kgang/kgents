"""
SaaS Configuration for kgents API.

Centralized configuration for SaaS infrastructure:
- NATS streaming (event distribution)
- OpenMeter (usage-based billing)

Follows project patterns:
- Frozen dataclasses for immutability
- Factory functions for loading from environment
- Validation via properties
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class SaaSConfig:
    """
    SaaS infrastructure configuration.

    Loaded from environment variables via get_saas_config().

    Environment Variables:
        NATS_SERVERS: Comma-separated NATS server URLs
        NATS_ENABLED: Enable NATS streaming (true/false)
        NATS_STREAM_NAME: JetStream stream name
        NATS_MAX_RECONNECT: Max reconnection attempts

        OPENMETER_API_KEY: OpenMeter API key
        OPENMETER_BASE_URL: OpenMeter API base URL
        OPENMETER_ENABLED: Enable OpenMeter billing (true/false)
        OPENMETER_BATCH_SIZE: Events before auto-flush
        OPENMETER_FLUSH_INTERVAL: Seconds between flushes
    """

    # NATS Configuration
    nats_servers: tuple[str, ...]
    nats_enabled: bool
    nats_stream_name: str
    nats_max_reconnect: int

    # OpenMeter Configuration
    openmeter_api_key: str
    openmeter_base_url: str
    openmeter_enabled: bool
    openmeter_batch_size: int
    openmeter_flush_interval: float

    @property
    def is_nats_configured(self) -> bool:
        """Check if NATS is properly configured and enabled."""
        return self.nats_enabled and len(self.nats_servers) > 0

    @property
    def is_openmeter_configured(self) -> bool:
        """Check if OpenMeter is properly configured and enabled."""
        return self.openmeter_enabled and bool(self.openmeter_api_key)


def _parse_bool(value: str, default: bool = False) -> bool:
    """Parse boolean from environment variable string."""
    if not value:
        return default
    return value.lower() in ("true", "1", "yes", "on")


def _parse_servers(value: str, default: str = "nats://localhost:4222") -> tuple[str, ...]:
    """Parse comma-separated server list."""
    if not value:
        return (default,)
    return tuple(s.strip() for s in value.split(",") if s.strip())


def get_saas_config() -> SaaSConfig:
    """
    Load SaaS configuration from environment variables.

    Returns:
        SaaSConfig instance with values from environment.

    Example:
        >>> config = get_saas_config()
        >>> if config.is_openmeter_configured:
        ...     client = create_openmeter_client(config)
    """
    return SaaSConfig(
        # NATS
        nats_servers=_parse_servers(os.environ.get("NATS_SERVERS", "")),
        nats_enabled=_parse_bool(os.environ.get("NATS_ENABLED", ""), default=False),
        nats_stream_name=os.environ.get("NATS_STREAM_NAME", "kgent-events"),
        nats_max_reconnect=int(os.environ.get("NATS_MAX_RECONNECT", "10")),
        # OpenMeter
        openmeter_api_key=os.environ.get("OPENMETER_API_KEY", ""),
        openmeter_base_url=os.environ.get("OPENMETER_BASE_URL", "https://openmeter.cloud"),
        openmeter_enabled=_parse_bool(os.environ.get("OPENMETER_ENABLED", ""), default=False),
        openmeter_batch_size=int(os.environ.get("OPENMETER_BATCH_SIZE", "100")),
        openmeter_flush_interval=float(os.environ.get("OPENMETER_FLUSH_INTERVAL", "1.0")),
    )


# Cached config instance (lazy-loaded)
_config_instance: Optional[SaaSConfig] = None


def get_cached_saas_config() -> SaaSConfig:
    """
    Get cached SaaS configuration.

    Use this for repeated access to avoid re-parsing environment.
    Call reset_cached_config() to reload.

    Returns:
        Cached SaaSConfig instance.
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = get_saas_config()
    return _config_instance


def reset_cached_config() -> None:
    """Reset cached configuration. For testing."""
    global _config_instance
    _config_instance = None
