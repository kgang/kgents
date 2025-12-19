"""
SaaS Client Management for kgents API.

Provides singleton lifecycle management for SaaS infrastructure clients:
- OpenMeterClient: Usage-based billing
- NATSBridge: Event streaming

Usage with FastAPI lifespan (preferred, no deprecation warnings):
    from contextlib import asynccontextmanager
    from fastapi import FastAPI

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await get_saas_clients().start()
        yield
        await get_saas_clients().stop()

    app = FastAPI(lifespan=lifespan)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Optional

from .saas import SaaSConfig, get_cached_saas_config

logger = logging.getLogger(__name__)


@dataclass
class SaaSClients:
    """
    Singleton container for SaaS service clients.

    Manages lifecycle of:
    - OpenMeterClient (usage billing)
    - NATSBridge (event streaming)

    Thread-safe via single event loop assumption (FastAPI).
    """

    config: SaaSConfig

    # Client instances (lazy-initialized)
    _openmeter: Any = field(default=None, init=False, repr=False)
    _nats: Any = field(default=None, init=False, repr=False)

    # State
    _started: bool = field(default=False, init=False)

    @property
    def openmeter(self) -> Any:
        """Get OpenMeter client (may be None if not configured)."""
        return self._openmeter

    @property
    def nats(self) -> Any:
        """Get NATS bridge (may be None if not configured)."""
        return self._nats

    @property
    def is_started(self) -> bool:
        """Check if clients have been started."""
        return self._started

    async def start(self) -> None:
        """
        Start all configured SaaS clients.

        Safe to call multiple times (idempotent).
        """
        if self._started:
            logger.debug("SaaS clients already started")
            return

        logger.info("Starting SaaS infrastructure clients...")

        # Initialize OpenMeter
        if self.config.is_openmeter_configured:
            try:
                from protocols.billing.openmeter_client import (
                    OpenMeterClient,
                    OpenMeterConfig,
                )

                openmeter_config = OpenMeterConfig(
                    api_key=self.config.openmeter_api_key,
                    base_url=self.config.openmeter_base_url,
                    enabled=self.config.openmeter_enabled,
                    batch_size=self.config.openmeter_batch_size,
                    flush_interval_seconds=self.config.openmeter_flush_interval,
                )
                self._openmeter = OpenMeterClient(config=openmeter_config)
                await self._openmeter.start()
                logger.info("OpenMeter client started")
            except ImportError as e:
                logger.warning(f"OpenMeter client unavailable: {e}")
            except Exception as e:
                logger.error(f"Failed to start OpenMeter client: {e}")
        else:
            logger.info("OpenMeter not configured, skipping")

        # Initialize NATS
        if self.config.is_nats_configured:
            try:
                from protocols.streaming.nats_bridge import (
                    NATSBridge,
                    NATSBridgeConfig,
                )

                nats_config = NATSBridgeConfig(
                    servers=list(self.config.nats_servers),
                    stream_name=self.config.nats_stream_name,
                    max_reconnect_attempts=self.config.nats_max_reconnect,
                    enabled=self.config.nats_enabled,
                )
                self._nats = NATSBridge(config=nats_config)
                await self._nats.connect()
                logger.info("NATS bridge started")
            except ImportError as e:
                logger.warning(f"NATS bridge unavailable: {e}")
            except Exception as e:
                logger.error(f"Failed to start NATS bridge: {e}")
        else:
            logger.info("NATS not configured, skipping")

        self._started = True
        logger.info("SaaS infrastructure clients started")

    async def stop(self) -> None:
        """
        Stop all SaaS clients and flush pending data.

        Safe to call multiple times (idempotent).
        """
        if not self._started:
            logger.debug("SaaS clients not started, nothing to stop")
            return

        logger.info("Stopping SaaS infrastructure clients...")

        # Stop OpenMeter (flushes pending events)
        if self._openmeter is not None:
            try:
                await self._openmeter.stop()
                logger.info("OpenMeter client stopped")
            except Exception as e:
                logger.error(f"Error stopping OpenMeter client: {e}")
            finally:
                self._openmeter = None

        # Stop NATS
        if self._nats is not None:
            try:
                await self._nats.disconnect()
                logger.info("NATS bridge stopped")
            except Exception as e:
                logger.error(f"Error stopping NATS bridge: {e}")
            finally:
                self._nats = None

        self._started = False
        logger.info("SaaS infrastructure clients stopped")

    async def health_check(self) -> dict[str, Any]:
        """
        Get health status of all SaaS clients.

        Returns:
            Dictionary with health status for each client.
        """
        status: dict[str, Any] = {
            "started": self._started,
            "openmeter": {"configured": self.config.is_openmeter_configured},
            "nats": {"configured": self.config.is_nats_configured},
        }

        # OpenMeter health
        if self._openmeter is not None:
            try:
                om_health = await self._openmeter.health_check()
                status["openmeter"]["status"] = om_health.get("status", "unknown")
                status["openmeter"]["metrics"] = self._openmeter.get_metrics()
            except Exception as e:
                status["openmeter"]["status"] = "error"
                status["openmeter"]["error"] = str(e)
        elif self.config.is_openmeter_configured:
            status["openmeter"]["status"] = "not_started"
        else:
            status["openmeter"]["status"] = "disabled"

        # NATS health
        if self._nats is not None:
            try:
                nats_health = await self._nats.health_check()
                status["nats"]["status"] = nats_health.get("status", "unknown")
                status["nats"]["mode"] = nats_health.get("mode", "unknown")
            except Exception as e:
                status["nats"]["status"] = "error"
                status["nats"]["error"] = str(e)
        elif self.config.is_nats_configured:
            status["nats"]["status"] = "not_started"
        else:
            status["nats"]["status"] = "disabled"

        return status


# Singleton instance
_clients_instance: Optional[SaaSClients] = None


def get_saas_clients() -> SaaSClients:
    """
    Get singleton SaaS clients instance.

    Creates instance on first call using cached config.
    Thread-safe via Python GIL (single event loop).

    Returns:
        SaaSClients singleton instance.

    Example:
        clients = get_saas_clients()
        if clients.openmeter:
            await clients.openmeter.record_request(...)
    """
    global _clients_instance
    if _clients_instance is None:
        config = get_cached_saas_config()
        _clients_instance = SaaSClients(config=config)
    return _clients_instance


def reset_saas_clients() -> None:
    """
    Reset singleton instance.

    For testing only. Does NOT stop running clients.
    """
    global _clients_instance
    _clients_instance = None


async def init_saas_clients() -> SaaSClients:
    """
    Initialize and start SaaS clients.

    Convenience function for FastAPI startup.

    Returns:
        Started SaaSClients instance.
    """
    clients = get_saas_clients()
    await clients.start()
    return clients


async def shutdown_saas_clients() -> None:
    """
    Shutdown SaaS clients.

    Convenience function for FastAPI shutdown.
    """
    clients = get_saas_clients()
    await clients.stop()
