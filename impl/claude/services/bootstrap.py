"""
Crown Jewel Bootstrap: Dependency Injection for Core Crown Jewels.

This module provides a clean, centralized dependency injection layer that:
1. Creates the session_factory + dgent_router at app startup
2. Wires core Crown Jewel persistence services (Brain, Witness, Morpheus)
3. Enables clean testing via reset() and injection points

The Metaphysical Fullstack Pattern (AD-009):
- Services own domain semantics (WHEN, WHY)
- TableAdapter + D-gent compose storage (HOW)
- Bootstrap wires everything together at startup

Usage:
    # At app startup (api/app.py or CLI entry)
    from services.bootstrap import bootstrap_services, get_service

    async def startup():
        await bootstrap_services()

    # In handlers
    brain = await get_service("brain_persistence")
    result = await brain.capture("Hello world")

    # For testing
    from services.bootstrap import reset_services, inject_service
    reset_services()
    inject_service("brain_persistence", mock_brain)
"""

from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from threading import Lock
from typing import TYPE_CHECKING, Any, Callable, TypeVar

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from agents.d import DgentProtocol, TableAdapter
    from services.brain import BrainPersistence
    from services.morpheus import MorpheusPersistence
    from services.witness import WitnessPersistence

logger = logging.getLogger(__name__)

T = TypeVar("T")


# =============================================================================
# Service Registry
# =============================================================================


@dataclass
class ServiceRegistry:
    """
    Central registry for all Crown Jewel services.

    Provides:
    - Lazy initialization (services created on first access)
    - Singleton semantics (one instance per service)
    - Injection points for testing
    - Thread-safe access
    """

    # Core infrastructure (created first)
    _session_factory: "async_sessionmaker[AsyncSession] | None" = None
    _dgent_router: "DgentProtocol | None" = None

    # Crown Jewel persistence services (created on demand)
    _services: dict[str, Any] = field(default_factory=dict)

    # Factory functions for services
    _factories: dict[str, Callable[[], Any]] = field(default_factory=dict)

    # Thread safety
    _lock: Lock = field(default_factory=Lock)

    # Initialization state
    _initialized: bool = False

    def is_initialized(self) -> bool:
        """Check if the registry is initialized."""
        return self._initialized

    async def initialize(
        self,
        database_url: str | None = None,
        dgent_backend: str = "memory",
    ) -> None:
        """
        Initialize core infrastructure.

        Args:
            database_url: Optional database URL override
            dgent_backend: D-gent backend type ("memory", "sqlite", "postgres")
        """
        with self._lock:
            if self._initialized:
                logger.debug("ServiceRegistry already initialized")
                return

            # Create session factory
            self._session_factory = await self._create_session_factory(database_url)

            # Create D-gent router
            self._dgent_router = await self._create_dgent_router(dgent_backend)

            self._initialized = True
            logger.info("ServiceRegistry initialized")

    async def _create_session_factory(
        self, url: str | None = None
    ) -> "async_sessionmaker[AsyncSession]":
        """Create the SQLAlchemy async session factory."""
        from sqlalchemy.ext.asyncio import (
            AsyncSession,
            async_sessionmaker,
            create_async_engine,
        )

        # Get database URL from environment or parameter
        db_url = url or os.environ.get(
            "KGENTS_DATABASE_URL",
            "sqlite+aiosqlite:///~/.local/share/kgents/membrane.db",
        )

        # Expand ~ in path
        if "~" in db_url:
            parts = db_url.split("///")
            if len(parts) == 2:
                db_url = f"{parts[0]}///{os.path.expanduser(parts[1])}"

        # Ensure directory exists for SQLite
        if db_url.startswith("sqlite"):
            db_path = db_url.split("///")[-1]
            os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)

        # Create engine
        engine = create_async_engine(
            db_url,
            echo=False,
            future=True,
        )

        # Create session factory
        factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )

        logger.info(f"Session factory created for: {db_url.split('://')[0]}")
        return factory

    async def _create_dgent_router(self, backend: str = "memory") -> "DgentProtocol":
        """Create the D-gent router."""
        from agents.d import DgentRouter
        from agents.d.router import Backend

        # Map string to Backend enum
        backend_map = {
            "memory": Backend.MEMORY,
            "sqlite": Backend.SQLITE,
            "jsonl": Backend.JSONL,
            "postgres": Backend.POSTGRES,
        }
        preferred = backend_map.get(backend, Backend.MEMORY)

        # DgentRouter auto-selects based on availability, with preferred hint
        router = DgentRouter(
            namespace="kgents",
            preferred=preferred,
        )

        logger.info(f"D-gent router created with preferred backend: {backend}")
        return router

    @property
    def session_factory(self) -> "async_sessionmaker[AsyncSession]":
        """Get the session factory (raises if not initialized)."""
        if self._session_factory is None:
            raise RuntimeError("ServiceRegistry not initialized. Call initialize() first.")
        return self._session_factory

    @property
    def dgent(self) -> "DgentProtocol":
        """Get the D-gent router (raises if not initialized)."""
        if self._dgent_router is None:
            raise RuntimeError("ServiceRegistry not initialized. Call initialize() first.")
        return self._dgent_router

    async def get(self, name: str) -> Any:
        """
        Get a service by name.

        Creates the service on first access (lazy initialization).

        Args:
            name: Service name (e.g., "brain_persistence")

        Returns:
            Service instance

        Raises:
            KeyError: If service not found
            RuntimeError: If registry not initialized
        """
        if not self._initialized:
            raise RuntimeError("ServiceRegistry not initialized. Call initialize() first.")

        with self._lock:
            # Return cached service if exists
            if name in self._services:
                return self._services[name]

            # Create service via factory
            if name in self._factories:
                service = await self._factories[name]()
                self._services[name] = service
                return service

        # Try default factory
        service = await self._create_default_service(name)
        if service is not None:
            with self._lock:
                self._services[name] = service
            return service

        raise KeyError(f"Unknown service: {name}")

    async def _create_default_service(self, name: str) -> Any | None:
        """Create a service using default factories."""
        from agents.d import TableAdapter

        # Brain persistence
        if name == "brain_persistence":
            from models.brain import Crystal
            from services.brain import BrainPersistence

            adapter = TableAdapter(
                model=Crystal,
                session_factory=self.session_factory,
            )
            return BrainPersistence(
                table_adapter=adapter,
                dgent=self.dgent,
            )

        # Morpheus persistence (no database - wraps LLM gateway)
        if name == "morpheus_persistence":
            from services.morpheus import MorpheusGateway, MorpheusPersistence
            from services.morpheus.adapters import ClaudeCLIAdapter

            gateway = MorpheusGateway()
            gateway.register_provider(
                name="claude-cli",
                adapter=ClaudeCLIAdapter(),
                prefix="claude-",
            )
            return MorpheusPersistence(gateway=gateway)

        # K-gent Soul (Middleware of Consciousness - no database needed)
        if name == "kgent_soul":
            from agents.k.soul import KgentSoul

            return KgentSoul(auto_llm=True)

        # Differance Store (trace heritage persistence)
        if name == "differance_store":
            from agents.d.bus import get_data_bus
            from agents.differance import DifferanceStore

            # Use the dgent router's backend directly
            bus = get_data_bus()
            store = DifferanceStore(backend=self.dgent, bus=bus)
            return store

        # Witness persistence (8th Crown Jewel)
        if name == "witness_persistence":
            from services.witness.persistence import WitnessPersistence

            return WitnessPersistence(
                session_factory=self.session_factory,
                dgent=self.dgent,
            )

        return None

    def register_factory(self, name: str, factory: Callable[[], Any]) -> None:
        """Register a custom factory for a service."""
        with self._lock:
            self._factories[name] = factory

    def inject(self, name: str, service: Any) -> None:
        """
        Inject a service directly (for testing).

        Args:
            name: Service name
            service: Service instance to inject
        """
        with self._lock:
            self._services[name] = service

    def reset(self) -> None:
        """Reset the registry (for testing)."""
        with self._lock:
            self._services.clear()
            self._factories.clear()
            self._session_factory = None
            self._dgent_router = None
            self._initialized = False
        logger.debug("ServiceRegistry reset")

    def list_services(self) -> list[str]:
        """List all available service names."""
        return [
            "brain_persistence",
            "witness_persistence",
            "morpheus_persistence",
            "kgent_soul",
            "differance_store",
        ]

    def stats(self) -> dict[str, Any]:
        """Get registry statistics."""
        with self._lock:
            return {
                "initialized": self._initialized,
                "cached_services": list(self._services.keys()),
                "custom_factories": list(self._factories.keys()),
            }


# =============================================================================
# Global Registry Singleton
# =============================================================================

_registry: ServiceRegistry | None = None
_registry_lock = Lock()


def get_registry() -> ServiceRegistry:
    """Get the global service registry."""
    global _registry
    if _registry is None:
        with _registry_lock:
            if _registry is None:
                _registry = ServiceRegistry()
    return _registry


def reset_registry() -> None:
    """Reset the global registry (for testing)."""
    global _registry
    with _registry_lock:
        if _registry is not None:
            _registry.reset()
        _registry = None


# =============================================================================
# Convenience Functions
# =============================================================================


async def bootstrap_services(
    database_url: str | None = None,
    dgent_backend: str = "memory",
) -> ServiceRegistry:
    """
    Bootstrap all Crown Jewel services.

    Call this at application startup.

    Args:
        database_url: Optional database URL override
        dgent_backend: D-gent backend type

    Returns:
        The initialized ServiceRegistry
    """
    registry = get_registry()
    await registry.initialize(database_url, dgent_backend)
    return registry


async def get_service(name: str) -> Any:
    """
    Get a Crown Jewel service by name.

    Args:
        name: Service name (e.g., "brain_persistence")

    Returns:
        Service instance
    """
    registry = get_registry()
    return await registry.get(name)


def inject_service(name: str, service: Any) -> None:
    """
    Inject a service for testing.

    Args:
        name: Service name
        service: Mock or test service instance
    """
    registry = get_registry()
    registry.inject(name, service)


def reset_services() -> None:
    """Reset all services (for testing)."""
    reset_registry()


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Registry
    "ServiceRegistry",
    "get_registry",
    "reset_registry",
    # Convenience
    "bootstrap_services",
    "get_service",
    "inject_service",
    "reset_services",
]
