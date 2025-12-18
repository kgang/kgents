"""
Service Providers: Dependency Injection for AGENTESE services.

This module provides backward-compatible access to the new bootstrap system.
The bootstrap module is the canonical source for all Crown Jewel services.

The Metaphysical Fullstack Pattern (AD-009):
- Services declare dependencies via @node decorator
- Container resolves dependencies at instantiation time
- D-gent, TableAdapters, LLM clients are all injectable

Usage:
    # Preferred: Use bootstrap module directly
    from services.bootstrap import bootstrap_services, get_service

    async def on_startup():
        await bootstrap_services()

    # Backward-compatible: Use providers module
    from services.providers import setup_providers

    async def on_startup():
        await setup_providers()
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from protocols.agentese.container import get_container

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import async_sessionmaker

    from agents.d import DgentProtocol, TableAdapter
    from models.brain import Crystal
    from services.atelier import AtelierPersistence
    from services.brain import BrainPersistence
    from services.chat import ChatPersistence, ChatSessionFactory
    from services.coalition import CoalitionPersistence
    from services.gardener import GardenerPersistence
    from services.gestalt import GestaltPersistence
    from services.park import ParkPersistence
    from services.town import TownPersistence
    from services.town.coalition_service import CoalitionService

logger = logging.getLogger(__name__)


# =============================================================================
# Re-export from bootstrap (canonical source)
# =============================================================================

from services.bootstrap import (
    ServiceRegistry,
    bootstrap_services,
    get_registry,
    get_service,
    inject_service,
    reset_registry,
    reset_services,
)

# =============================================================================
# Backward-Compatible Provider Functions
# =============================================================================


async def get_session_factory() -> "async_sessionmaker":
    """
    Get the SQLAlchemy async session factory.

    Delegates to the bootstrap registry.
    """
    registry = get_registry()
    if not registry.is_initialized():
        await registry.initialize()
    return registry.session_factory


async def get_dgent_router() -> "DgentProtocol":
    """
    Get the D-gent router for semantic storage.

    Delegates to the bootstrap registry.
    """
    registry = get_registry()
    if not registry.is_initialized():
        await registry.initialize()
    return registry.dgent


async def get_brain_table_adapter() -> "TableAdapter[Crystal]":
    """
    Get the TableAdapter for Crystal table.

    Note: This creates a new adapter. Prefer using the full persistence service.
    """
    from agents.d import TableAdapter
    from models.brain import Crystal

    session_factory = await get_session_factory()

    return TableAdapter(
        model_class=Crystal,
        session_factory=session_factory,
    )


async def get_brain_persistence() -> "BrainPersistence":
    """Get the BrainPersistence service."""
    return await get_service("brain_persistence")


async def get_town_persistence() -> "TownPersistence":
    """Get the TownPersistence service."""
    return await get_service("town_persistence")


async def get_gardener_persistence() -> "GardenerPersistence":
    """Get the GardenerPersistence service."""
    return await get_service("gardener_persistence")


async def get_gestalt_persistence() -> "GestaltPersistence":
    """Get the GestaltPersistence service."""
    return await get_service("gestalt_persistence")


async def get_atelier_persistence() -> "AtelierPersistence":
    """Get the AtelierPersistence service."""
    return await get_service("atelier_persistence")


async def get_coalition_persistence() -> "CoalitionPersistence":
    """Get the CoalitionPersistence service."""
    return await get_service("coalition_persistence")


async def get_park_persistence() -> "ParkPersistence":
    """Get the ParkPersistence service."""
    return await get_service("park_persistence")


async def get_coalition_service() -> "CoalitionService":
    """
    Get the CoalitionService for coalition detection and reputation.

    This is separate from CoalitionPersistence - it's the in-memory
    service used by CoalitionNode for detection algorithms.
    """
    from services.town.coalition_service import CoalitionService

    return CoalitionService()


async def get_chat_persistence() -> "ChatPersistence":
    """Get the ChatPersistence service."""
    from services.chat import get_persistence

    return get_persistence()


async def get_chat_factory() -> "ChatSessionFactory":
    """Get the ChatSessionFactory service."""
    from services.chat import get_chat_factory as get_factory

    return get_factory()


# =============================================================================
# Setup Function
# =============================================================================


async def setup_providers() -> None:
    """
    Register all service providers with the global container.

    This now delegates to bootstrap_services() and registers with the
    AGENTESE container for backward compatibility.
    """
    # Initialize bootstrap registry (canonical source)
    await bootstrap_services()

    # Register with AGENTESE container for backward compatibility
    container = get_container()

    # Register all 7 Crown Jewel persistence services
    container.register("session_factory", get_session_factory, singleton=True)
    container.register("dgent", get_dgent_router, singleton=True)
    container.register("brain_persistence", get_brain_persistence, singleton=True)
    container.register("town_persistence", get_town_persistence, singleton=True)
    container.register("gardener_persistence", get_gardener_persistence, singleton=True)
    container.register("gestalt_persistence", get_gestalt_persistence, singleton=True)
    container.register("atelier_persistence", get_atelier_persistence, singleton=True)
    container.register("coalition_persistence", get_coalition_persistence, singleton=True)
    container.register("park_persistence", get_park_persistence, singleton=True)
    container.register("chat_persistence", get_chat_persistence, singleton=True)
    container.register("chat_factory", get_chat_factory, singleton=True)

    # Town sub-services (for CoalitionNode, WorkshopNode, etc.)
    container.register("coalition_service", get_coalition_service, singleton=True)

    logger.info("All 8 Crown Jewel persistence services registered")

    # Import service nodes to trigger @node registration
    try:
        from services.brain import BrainNode  # noqa: F401

        logger.info("BrainNode registered with AGENTESE registry")
    except ImportError as e:
        logger.debug(f"BrainNode not available: {e}")

    try:
        from services.town import TownNode  # noqa: F401

        logger.info("TownNode registered with AGENTESE registry")
    except ImportError as e:
        logger.debug(f"TownNode not available: {e}")

    try:
        from services.chat import ChatNode  # noqa: F401

        logger.info("ChatNode registered with AGENTESE registry")
    except ImportError as e:
        logger.debug(f"ChatNode not available: {e}")

    try:
        from services.park import ParkNode  # noqa: F401

        logger.info("ParkNode registered with AGENTESE registry")
    except ImportError as e:
        logger.debug(f"ParkNode not available: {e}")

    try:
        from services.atelier import AtelierNode  # noqa: F401

        logger.info("AtelierNode registered with AGENTESE registry")
    except ImportError as e:
        logger.debug(f"AtelierNode not available: {e}")

    try:
        from services.gestalt import GestaltNode  # noqa: F401

        logger.info("GestaltNode registered with AGENTESE registry")
    except ImportError as e:
        logger.debug(f"GestaltNode not available: {e}")

    # Log registry stats
    from protocols.agentese.registry import get_registry as get_agentese_registry

    agentese_registry = get_agentese_registry()
    stats = agentese_registry.stats()
    logger.info(f"AGENTESE registry: {stats['registered_nodes']} nodes registered")


def setup_providers_sync() -> None:
    """
    Synchronous provider setup for import-time registration.

    Registers only sync providers. Call setup_providers() for async ones.
    """
    _ = get_container()  # Ensure container is initialized
    logger.debug("Sync providers registered (no-op, use setup_providers for async)")


# =============================================================================
# Exports
# =============================================================================

__all__ = [
    # Bootstrap (canonical)
    "ServiceRegistry",
    "get_registry",
    "reset_registry",
    "bootstrap_services",
    "get_service",
    "inject_service",
    "reset_services",
    # Setup
    "setup_providers",
    "setup_providers_sync",
    # Infrastructure
    "get_session_factory",
    "get_dgent_router",
    # Primary Crown Jewels
    "get_brain_table_adapter",
    "get_brain_persistence",
    "get_town_persistence",
    "get_gardener_persistence",
    # Secondary Crown Jewels
    "get_gestalt_persistence",
    "get_atelier_persistence",
    "get_coalition_persistence",
    "get_park_persistence",
    # Chat Crown Jewel
    "get_chat_persistence",
    "get_chat_factory",
    # Town sub-services
    "get_coalition_service",
]
