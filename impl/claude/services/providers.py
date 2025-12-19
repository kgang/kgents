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
    from typing import Callable

    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from agents.d import DgentProtocol, TableAdapter
    from agents.differance import DifferanceStore
    from agents.k.soul import KgentSoul
    from agents.town.sheaf import TownSheaf
    from models.brain import Crystal
    from models.town import CitizenView
    from services.brain import BrainPersistence
    from services.chat import ChatPersistence, ChatServiceFactory, ChatSessionFactory
    from services.coalition import CoalitionPersistence
    from services.forge import ForgePersistence
    from services.forge.commission import CommissionService
    from services.gardener import GardenerPersistence
    from services.gestalt import GestaltPersistence
    from services.morpheus.persistence import MorpheusPersistence
    from services.park import ParkPersistence
    from services.park.scenario_service import ScenarioService
    from services.town import TownPersistence
    from services.town.bus_wiring import TownBusManager
    from services.town.coalition_service import CoalitionService
    from services.town.inhabit_service import InhabitService
    from services.town.workshop_service import WorkshopService
    from services.witness.persistence import WitnessPersistence

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


async def get_session_factory() -> "async_sessionmaker[AsyncSession]":
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
        model=Crystal,
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


async def get_forge_persistence() -> "ForgePersistence":
    """Get the ForgePersistence service."""
    return await get_service("forge_persistence")


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


async def get_inhabit_service() -> "InhabitService":
    """
    Get the InhabitService for INHABIT mode session management.

    Used by InhabitNode to manage user-citizen merge sessions with
    consent tracking and force mechanics.
    """
    from services.town.inhabit_service import InhabitService

    return InhabitService()


async def get_chat_persistence() -> "ChatPersistence":
    """Get the ChatPersistence service."""
    from services.chat import get_persistence

    return get_persistence()


async def get_chat_factory() -> "ChatServiceFactory":
    """
    Get the ChatSessionFactory service with Morpheus integration.

    Uses ChatServiceFactory which properly wires the Morpheus composer
    for real LLM responses instead of stub fallbacks.
    """
    from services.chat import ChatServiceFactory, set_chat_factory

    # Get morpheus_persistence from bootstrap - it has ClaudeCLIAdapter registered
    morpheus = await get_service("morpheus_persistence")
    factory = ChatServiceFactory(morpheus=morpheus)

    # Set as global factory so ChatNode uses it too
    set_chat_factory(factory)

    return factory


async def get_kgent_soul() -> "KgentSoul":
    """Get the KgentSoul service (Middleware of Consciousness)."""
    return await get_service("kgent_soul")


async def get_differance_store() -> "DifferanceStore":
    """Get the DifferanceStore service (trace heritage persistence)."""
    from agents.differance import DifferanceStore

    return await get_service("differance_store")


async def get_morpheus_persistence() -> "MorpheusPersistence":
    """
    Get the MorpheusPersistence service (LLM gateway).

    Creates a new MorpheusPersistence with default gateway.
    """
    from services.morpheus.persistence import MorpheusPersistence

    return MorpheusPersistence()


async def get_commission_service() -> "CommissionService":
    """
    Get the CommissionService for the Metaphysical Forge.

    Optionally injects KgentSoul for governance if available.
    """
    from services.forge.commission import CommissionService

    # Try to get KgentSoul for governance
    try:
        soul = await get_service("kgent_soul")
    except Exception:
        soul = None

    return CommissionService(kgent_soul=soul)


async def get_witness_persistence() -> "WitnessPersistence":
    """Get the WitnessPersistence service (8th Crown Jewel)."""
    return await get_service("witness_persistence")


async def get_scenario_service() -> "ScenarioService":
    """
    Get the ScenarioService for Punchdrunk Park.

    Used by ParkNode for scenario template management and session orchestration.
    """
    from services.park.scenario_service import ScenarioService

    return ScenarioService()


async def get_workshop_service() -> "WorkshopService":
    """
    Get the WorkshopService for Agent Town builder coordination.

    Used by WorkshopNode for task assignment and builder collaboration.
    """
    from services.town.workshop_service import WorkshopService

    return WorkshopService()


async def get_town_sheaf() -> "TownSheaf":
    """
    Get the TownSheaf for collective emergence detection.

    Used by CollectiveNode for gossip propagation and emergence metrics.
    Creates a fresh sheaf with all region contexts.
    """
    from agents.town.sheaf import create_town_sheaf

    return create_town_sheaf()


async def get_bus_manager() -> "TownBusManager":
    """
    Get the TownBusManager for cross-jewel event coordination.

    Used by CollectiveNode for DataBus → SynergyBus → EventBus wiring.
    Wires all buses on creation.
    """
    from services.town.bus_wiring import TownBusManager

    manager = TownBusManager()
    manager.wire_all()
    return manager


async def get_citizen_resolver() -> "Callable[..., CitizenView | None]":
    """
    Get the citizen resolver callable for InhabitNode.

    Returns a function that can resolve citizens by ID or name using TownPersistence.
    Used by InhabitNode to find citizens for INHABIT sessions.
    """
    # Get TownPersistence to create the resolver
    persistence = await get_service("town_persistence")

    async def resolve_citizen(
        citizen_id: str | None = None,
        name: str | None = None,
    ) -> "CitizenView | None":
        """Resolve citizen by ID or name."""
        if citizen_id:
            return await persistence.get_citizen(citizen_id)
        elif name:
            return await persistence.get_citizen_by_name(name)
        return None

    return resolve_citizen


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
    container.register("forge_persistence", get_forge_persistence, singleton=True)
    container.register("coalition_persistence", get_coalition_persistence, singleton=True)
    container.register("park_persistence", get_park_persistence, singleton=True)
    container.register("chat_persistence", get_chat_persistence, singleton=True)
    container.register("chat_factory", get_chat_factory, singleton=True)
    container.register("witness_persistence", get_witness_persistence, singleton=True)

    # Town sub-services (for CoalitionNode, WorkshopNode, InhabitNode, etc.)
    container.register("coalition_service", get_coalition_service, singleton=True)
    container.register("inhabit_service", get_inhabit_service, singleton=True)
    container.register("workshop_service", get_workshop_service, singleton=True)
    container.register("citizen_resolver", get_citizen_resolver, singleton=True)
    container.register("town_sheaf", get_town_sheaf, singleton=True)
    container.register("bus_manager", get_bus_manager, singleton=True)

    # K-gent Soul (Middleware of Consciousness)
    container.register("kgent_soul", get_kgent_soul, singleton=True)

    # Differance Store (trace heritage persistence)
    container.register("differance_store", get_differance_store, singleton=True)

    # Morpheus LLM Gateway
    container.register("morpheus_persistence", get_morpheus_persistence, singleton=True)

    # Commission Service (Metaphysical Forge)
    container.register("commission_service", get_commission_service, singleton=True)

    # Park Services (Punchdrunk Park scenarios)
    container.register("scenario_service", get_scenario_service, singleton=True)

    logger.info(
        "All Crown Jewel services registered (8 persistence + Town sub-services + Park scenarios)"
    )

    # Import Witness node to trigger @node registration
    try:
        from services.witness import WitnessNode  # noqa: F401

        logger.info("WitnessNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"WitnessNode not available: {e}")

    # Import service nodes to trigger @node registration
    # FAIL-FAST: Crown Jewel import failures are WARNING level (visible)
    try:
        from services.brain import BrainNode  # noqa: F401

        logger.info("BrainNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"BrainNode not available: {e}")

    try:
        from services.town import TownNode  # noqa: F401

        logger.info("TownNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"TownNode not available: {e}")

    try:
        from services.chat import ChatNode  # noqa: F401

        logger.info("ChatNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"ChatNode not available: {e}")

    try:
        from services.park import ParkNode  # noqa: F401

        logger.info("ParkNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"ParkNode not available: {e}")

    try:
        from services.forge import ForgeNode  # noqa: F401

        logger.info("ForgeNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"ForgeNode not available: {e}")

    try:
        from services.gestalt import GestaltNode  # noqa: F401

        logger.info("GestaltNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"GestaltNode not available: {e}")

    try:
        from services.morpheus.node import MorpheusNode  # noqa: F401

        logger.info("MorpheusNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"MorpheusNode not available: {e}")

    try:
        from services.forge.commission_node import CommissionNode  # noqa: F401

        logger.info("CommissionNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"CommissionNode not available: {e}")

    # Wire DifferanceStore to DifferanceTraceNode
    try:
        from agents.differance import DifferanceStore
        from agents.differance.integration import set_differance_store
        from protocols.agentese.contexts.time_differance import get_differance_node

        store = await get_service("differance_store")
        if isinstance(store, DifferanceStore):
            # Wire to the AGENTESE node
            differance_node = get_differance_node()
            differance_node.set_store(store)

            # Also set global integration store
            set_differance_store(store)

            logger.info("DifferanceStore wired to DifferanceTraceNode")
    except Exception as e:
        logger.debug(f"DifferanceStore wiring skipped: {e}")

    # Wire KgentSoul to SoulNode
    try:
        from agents.k.soul import KgentSoul
        from protocols.agentese.contexts.self_soul import set_soul

        soul = await get_service("kgent_soul")
        if isinstance(soul, KgentSoul):
            set_soul(soul)
            logger.info("KgentSoul wired to SoulNode")
    except Exception as e:
        logger.debug(f"KgentSoul wiring skipped: {e}")

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
    "get_forge_persistence",
    "get_coalition_persistence",
    "get_park_persistence",
    # Chat Crown Jewel
    "get_chat_persistence",
    "get_chat_factory",
    # Town sub-services
    "get_coalition_service",
    "get_inhabit_service",
    "get_workshop_service",
    "get_citizen_resolver",
    "get_town_sheaf",
    "get_bus_manager",
    # Park services
    "get_scenario_service",
    # K-gent Soul
    "get_kgent_soul",
    # Differance Engine
    "get_differance_store",
    # Morpheus LLM Gateway
    "get_morpheus_persistence",
    # Metaphysical Forge
    "get_commission_service",
    # 8th Crown Jewel (Witness)
    "get_witness_persistence",
]
