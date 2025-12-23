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

Teaching:
    gotcha: setup_providers() MUST be called before any AGENTESE invocation.
            Nodes that declare dependencies will get None injected if the
            container isn't populated. Call in startup (FastAPI lifespan, main).
            (Evidence: test_bootstrap.py::TestBootstrapServices::test_get_service_after_bootstrap)

    gotcha: Services are CACHED after first instantiation. If you inject a mock,
            it replaces the cached instance. To restore original behavior, call
            reset_services() in test teardown.
            (Evidence: test_bootstrap.py::TestAllSevenServices::test_services_are_cached)

    gotcha: Provider function naming convention: get_{service_name}() where
            {service_name} matches EXACTLY what's passed to @node(dependencies=(...)).
            Example: @node(dependencies=("brain_persistence",)) requires
            get_brain_persistence() in this file.
            (Evidence: test_bootstrap.py::TestBackwardCompatibleProviders::test_provider_getters)

AGENTESE: services.providers
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from protocols.agentese.container import get_container

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

    from agents.d import DgentProtocol, TableAdapter
    from agents.k.soul import KgentSoul
    from agents.l.embedders import SentenceTransformerEmbedder
    from models.brain import Crystal
    from protocols.agentese.logos import Logos
    from services import witnessed_graph
    from services.ashc.persistence import PostgresLemmaDatabase
    from services.brain import BrainPersistence
    from services.conductor import Summarizer, WindowPersistence
    from services.conductor.file_guard import FileEditGuard
    from services.conductor.swarm import SwarmSpawner
    from services.explorer import UnifiedQueryService
    from services.foundry import AgentFoundry
    from services.fusion import FusionService
    from services.hypergraph_editor import HypergraphEditorService
    from services.interactive_text.service import InteractiveTextService
    from services.k_block.core import Cosmos, FileOperadHarness
    from services.liminal.coffee.core import CoffeeService
    from services.metabolism.persistence import MetabolismPersistence
    from services.morpheus.persistence import MorpheusPersistence
    from services.principles import PrincipleLoader
    from services.proxy import ProxyHandleStore
    from services.sovereign.store import SovereignStore
    from services.tooling import ToolExecutor, ToolRegistry
    from services.verification import VerificationPersistence
    from services.witness import WitnessPersistence

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


async def get_kgent_soul() -> "KgentSoul":
    """Get the KgentSoul service (Middleware of Consciousness)."""
    return await get_service("kgent_soul")


async def get_morpheus_persistence() -> "MorpheusPersistence":
    """
    Get the MorpheusPersistence service (LLM gateway).

    Creates a new MorpheusPersistence with default gateway.
    """
    from services.morpheus.persistence import MorpheusPersistence

    return MorpheusPersistence()


# Note: get_mark_store removed in Crown Jewel Cleanup 2025-12-21
# Tracing infrastructure (witness service) was pruned


async def get_logos() -> "Logos":
    """
    Get the Logos resolver for cross-jewel invocation.

    Used by WitnessNode and WorldWitnessNode for invoking other jewels
    via AGENTESE paths. Creates a Logos instance with standard configuration.
    """
    from protocols.agentese.logos import create_logos

    return create_logos()


async def get_principle_loader() -> "PrincipleLoader":
    """
    Get the PrincipleLoader for concept.principles node.

    Used by PrinciplesNode to load principle files from spec/principles/.
    """
    from services.principles import create_principle_loader

    return create_principle_loader()


# =============================================================================
# Conductor Crown Jewel (CLI v7 Phase 2: Deep Conversation)
# =============================================================================


async def get_window_persistence() -> "WindowPersistence":
    """
    Get the WindowPersistence service for ConversationWindow state.

    CLI v7 Phase 2: Enables window state to survive across sessions.
    Used by ChatMorpheusComposer for D-gent-backed conversation memory.
    """
    from services.conductor import get_window_persistence as get_persistence

    return get_persistence()


async def get_summarizer() -> "Summarizer":
    """
    Get the Summarizer service for context compression.

    CLI v7 Phase 2: LLM-powered summarization with circadian modulation.
    Used by ConversationWindow to compress history when context grows.
    """
    from services.conductor import create_summarizer

    # Get morpheus for LLM calls
    try:
        morpheus = await get_service("morpheus_persistence")
    except Exception:
        morpheus = None

    return create_summarizer(morpheus=morpheus)


async def get_file_guard() -> "FileEditGuard":
    """
    Get the FileEditGuard for safe file manipulation.

    CLI v7 Phase 1: Enforces Claude Code's read-before-edit pattern.
    Used by world.file AGENTESE node for agent-safe file I/O.
    """
    from services.conductor.file_guard import get_file_guard as get_guard

    return get_guard()


async def get_swarm_spawner() -> "SwarmSpawner":
    """
    Get the SwarmSpawner for agent swarm coordination.

    CLI v7 Phase 6: Multi-agent collaboration.
    Used by self.conductor.swarm AGENTESE node for spawning agents.
    """
    from services.conductor.swarm import SwarmSpawner

    return SwarmSpawner()


# =============================================================================
# U-gent Tool Infrastructure (Phase 0)
# =============================================================================


async def get_tool_registry() -> "ToolRegistry":
    """
    Get the ToolRegistry singleton for tool discovery.

    Used by ToolsNode for tool listing and trust-gated discovery.
    """
    from services.tooling import get_registry

    return get_registry()


async def get_tool_executor() -> "ToolExecutor":
    """
    Get the ToolExecutor with full integration.

    Wires:
    - WitnessPersistence for trust gating
    - DifferanceStore for trace recording
    - SynergyBus for event emission

    Used by ToolsNode for executing tools with observability.
    """
    from services.tooling import ToolExecutor

    # Note: witness and differance integrations removed in Crown Jewel Cleanup 2025-12-21

    return ToolExecutor()


async def get_verification_persistence() -> "VerificationPersistence":
    """Get the VerificationPersistence service (Formal Verification Crown Jewel)."""
    return await get_service("verification_persistence")


async def get_coffee_service() -> "CoffeeService":
    """
    Get the CoffeeService for Morning Coffee ritual.

    The liminal transition protocol from rest to work.
    Used by CoffeeNode for ritual orchestration.
    """
    from services.liminal.coffee.core import CoffeeService

    return CoffeeService()


async def get_foundry_service() -> "AgentFoundry":
    """
    Get the AgentFoundry service (JIT Agent Synthesis Crown Jewel).

    The Foundry synthesizes J-gent JIT intelligence with Alethic Projection.
    Used by FoundryNode for agent forging, inspection, and caching.
    """
    from services.foundry import AgentFoundry

    return AgentFoundry()


async def get_metabolism_persistence() -> "MetabolismPersistence":
    """
    Get the MetabolismPersistence service for metabolic state.

    This wires the persistence layer for:
    - BackgroundEvidencing (evidence patterns, causal insights)
    - VoiceStigmergy (pheromone traces)

    Falls back to JSON files if D-gent is unavailable.
    """
    from services.metabolism.persistence import MetabolismPersistence

    try:
        dgent = await get_dgent_router()
        return MetabolismPersistence(dgent=dgent)
    except Exception as e:
        logger.debug(f"D-gent unavailable for metabolism persistence: {e}")
        # Graceful fallback to JSON-only persistence
        return MetabolismPersistence()


async def get_witness_persistence() -> "WitnessPersistence":
    """
    Get the WitnessPersistence service for Witness Crown Jewel.

    Wires the dual-track storage:
    - TableAdapter for fast queries (thoughts, actions, trust)
    - D-gent for semantic search

    Used by WitnessNode for self.witness.* AGENTESE paths.
    """
    from services.witness import WitnessPersistence

    session_factory = await get_session_factory()
    dgent = await get_dgent_router()

    return WitnessPersistence(
        session_factory=session_factory,
        dgent=dgent,
    )


# =============================================================================
# Interactive Text Crown Jewel (Phase 2.2: Documents as Control Surfaces)
# =============================================================================


async def get_interactive_text_service() -> "InteractiveTextService":
    """
    Get the InteractiveTextService for document parsing and task toggling.

    Phase 2.2: Interactive Text as live control surfaces.
    Used by InteractiveTextNode for self.document.* AGENTESE paths.
    """
    from services.interactive_text.service import InteractiveTextService

    return InteractiveTextService()


# =============================================================================
# K-Block Crown Jewel (Transactional Hyperdimensional Editing)
# =============================================================================


async def get_harness() -> "FileOperadHarness":
    """
    Get the K-Block FileOperadHarness.

    The harness provides transactional file operations:
    - lift(): Enter isolation
    - save(): Commit to cosmos
    - discard(): Abandon changes
    """
    from services.k_block.core import get_harness as kblock_get_harness

    return kblock_get_harness()


async def get_cosmos() -> "Cosmos":
    """
    Get the K-Block Cosmos (version store).

    The cosmos stores all committed versions:
    - Append-only log
    - Semantic indexing
    - Time travel
    """
    from services.k_block.core import get_cosmos as kblock_get_cosmos

    return kblock_get_cosmos()


# =============================================================================
# ASHC Crown Jewel (Proof-Generating Self-Hosting Compiler)
# =============================================================================


async def get_lemma_database() -> "PostgresLemmaDatabase":
    """
    Get the PostgresLemmaDatabase for verified lemma storage.

    Phase 4: Postgres-backed lemma database with stigmergic reinforcement.
    Used by ProofSearcher for hint retrieval and by proof verification
    pipeline for storing verified lemmas.

    The lemma database implements stigmergic cognition:
    - pheromone = usage_count (more-used lemmas rank higher)
    - find_related() increments usage for returned lemmas
    - emergent paths form as proofs reuse successful hints
    """
    from services.ashc.persistence import PostgresLemmaDatabase

    session_factory = await get_session_factory()
    return PostgresLemmaDatabase(session_factory)


# =============================================================================
# Fusion Crown Jewel (Symmetric Supersession)
# =============================================================================


async def get_fusion_service() -> "FusionService":
    """
    Get the FusionService for Symmetric Supersession.

    The fusion service operationalizes the Symmetric Supersession doctrine:
    - Kent and AI are symmetric agents
    - Either can propose, either can be superseded
    - Synthesis emerges from dialectical challenge
    - The disgust veto is absolute

    Used by FusionNode for self.fusion.* AGENTESE paths.

    See: brainstorming/2025-12-21-symmetric-supersession.md
    """
    from services.fusion import FusionService

    # Get witness persistence for recording fusion events
    try:
        witness = await get_witness_persistence()
    except Exception:
        witness = None

    return FusionService(witness=witness)


# =============================================================================
# Trail Intelligence (Visual Trail Graph Session 3)
# =============================================================================


async def get_sovereign_store() -> "SovereignStore":
    """
    Get the SovereignStore for inbound sovereignty.

    Manages sovereign copies of ingested entities.
    """
    from services.sovereign.store import SovereignStore

    return SovereignStore()


async def get_embedder() -> "SentenceTransformerEmbedder | None":
    """
    Get SentenceTransformer embedder for semantic similarity.

    Uses all-MiniLM-L6-v2 (384-dim, local, no API key).
    Lazy-loads to avoid startup delay.

    Used by TrailNode.suggest for finding semantically similar trails.

    Returns None if sentence-transformers is not installed.
    """
    try:
        from agents.l.embedders import SentenceTransformerEmbedder

        return SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
    except ImportError:
        logger.warning("sentence-transformers not installed, trail suggestions disabled")
        return None
    except Exception as e:
        logger.warning(f"Embedder initialization failed: {e}")
        return None


async def get_editor_service() -> "HypergraphEditorService":
    """
    Get the HypergraphEditorService for typed-hypergraph editing.

    The editor service wraps the EditorPolynomial state machine
    for modal editing of the spec-impl graph.
    Used by EditorNode for self.editor.* AGENTESE paths.
    """
    from services.hypergraph_editor.service import HypergraphEditorService

    return HypergraphEditorService()


async def get_witnessed_graph_service() -> "witnessed_graph.WitnessedGraphService":
    """
    Get the WitnessedGraphService for unified graph queries.

    Composes three edge sources:
    - Sovereign: Code structure edges (imports, calls, inherits)
    - Witness: Mark-based edges (evidence, decisions, gotchas)
    - SpecLedger: Spec relation edges (harmony, contradiction, dependency)

    Usage:
        graph = await container.get("witnessed_graph_service")
        result = await graph.neighbors("spec/agents/d-gent.md")
    """
    from services.witnessed_graph import (
        SovereignSource,
        SpecLedgerSource,
        WitnessedGraphService,
        WitnessSource,
    )

    # Get dependencies
    sovereign_store = await get_sovereign_store()
    witness_persistence = await get_witness_persistence()

    # Create sources
    sovereign_source = SovereignSource(sovereign_store)
    witness_source = WitnessSource(witness_persistence)
    # SpecLedgerSource loads report lazily
    spec_source = SpecLedgerSource()

    # Compose into unified graph
    service = WitnessedGraphService(
        sovereign_source=sovereign_source,
        witness_source=witness_source,
        spec_source=spec_source,
    )

    # Wire bus for live updates (closes the loop: save → witness → graph → UI)
    await service.wire_bus()

    # Wire sovereign listeners (closes the loop: K-Block save → Cosmos → SovereignStore)
    await _wire_sovereign_listeners_once(sovereign_store)

    return service


# Global flag to ensure we only wire sovereign listeners once
_sovereign_listeners_wired = False


async def _wire_sovereign_listeners_once(sovereign_store: "SovereignStore") -> None:
    """
    Wire sovereign event listeners to the bus.

    Only wires once globally to avoid duplicate subscriptions.
    This closes the loop: K-Block save → Cosmos commit → Reingest to SovereignStore
    """
    global _sovereign_listeners_wired

    if _sovereign_listeners_wired:
        return

    try:
        from services.sovereign import wire_sovereign_listeners
        from services.witness.bus import get_synergy_bus

        bus = get_synergy_bus()
        await wire_sovereign_listeners(bus, sovereign_store)

        _sovereign_listeners_wired = True
        logger.info("[providers] Sovereign listeners wired to bus")

    except ImportError:
        logger.warning("[providers] Witness bus not available - sovereign listeners not wired")
    except Exception as e:
        logger.error(f"[providers] Failed to wire sovereign listeners: {e}", exc_info=True)


# =============================================================================
# Explorer Crown Jewel (Unified Data Explorer)
# =============================================================================


async def get_unified_query_service() -> "UnifiedQueryService":
    """
    Get the UnifiedQueryService for unified data exploration.

    The explorer aggregates ALL kgents data constructs into a unified stream:
    - Marks (witnessed behavior)
    - Crystals (crystallized knowledge)
    - Trails (exploration journeys)
    - Evidence (verification graphs, trace witnesses, violations)
    - Teachings (ancestral wisdom from deleted code)
    - Lemmas (ASHC verified proofs)

    Used by:
    - BrainPage for unified event stream
    - ExplorerNode for self.explorer.* AGENTESE paths
    - SSE stream for real-time updates

    Example:
        service = await get_unified_query_service()
        response = await service.list_events(ListEventsRequest(limit=50))
    """
    from services.explorer import UnifiedQueryService

    session_factory = await get_session_factory()
    return UnifiedQueryService(session_factory)


# =============================================================================
# Proxy Handle Store (AD-015: Epistemic Hygiene for Computed Data)
# =============================================================================


async def get_proxy_handle_store() -> "ProxyHandleStore":
    """
    Get the ProxyHandleStore for explicit computation lifecycle.

    AD-015: Proxy Handles & Transparent Batch Processes.

    Every expensive computation produces a proxy handle—an independent artifact
    with its own identity, lifecycle, and provenance. This makes staleness,
    computation state, and refresh mechanics explicit and transparent.

    Used by:
    - LedgerNode for spec corpus analysis
    - WitnessedGraphService for graph summaries
    - AGENTESE self.proxy.* paths

    Example:
        store = await get_proxy_handle_store()
        handle = await store.compute(
            source_type=SourceType.SPEC_CORPUS,
            compute_fn=analyze_corpus,
            human_label="Spec corpus analysis",
        )
    """
    from services.proxy import get_proxy_handle_store as get_store

    # Use the singleton factory
    return get_store()


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

    # Register core infrastructure services
    container.register("session_factory", get_session_factory, singleton=True)
    container.register("dgent", get_dgent_router, singleton=True)
    container.register("brain_persistence", get_brain_persistence, singleton=True)
    # Note: trace_store removed in Crown Jewel Cleanup 2025-12-21

    # K-gent Soul (Middleware of Consciousness)
    container.register("kgent_soul", get_kgent_soul, singleton=True)

    # Morpheus LLM Gateway
    container.register("morpheus_persistence", get_morpheus_persistence, singleton=True)

    # Principles Service (concept.principles node)
    container.register("principle_loader", get_principle_loader, singleton=True)

    # Conductor Crown Jewel (CLI v7 Phase 2: Deep Conversation, Phase 6: Swarms)
    container.register("window_persistence", get_window_persistence, singleton=True)
    container.register("summarizer", get_summarizer, singleton=True)
    container.register("file_guard", get_file_guard, singleton=True)
    container.register("swarm_spawner", get_swarm_spawner, singleton=True)

    # Logos (cross-jewel invocation)
    container.register("logos", get_logos, singleton=True)

    # U-gent Tool Infrastructure (Phase 0)
    container.register("tool_registry", get_tool_registry, singleton=True)
    container.register("tool_executor", get_tool_executor, singleton=True)

    # Verification Crown Jewel (Formal Verification Metatheory)
    container.register("verification_persistence", get_verification_persistence, singleton=True)

    # Witness Crown Jewel (8th Jewel - The Ghost That Watches)
    container.register("witness_persistence", get_witness_persistence, singleton=True)

    # Liminal Protocols (Morning Coffee, etc.)
    container.register("coffee_service", get_coffee_service, singleton=True)

    # Agent Foundry Crown Jewel (JIT Agent Synthesis + Alethic Projection)
    container.register("foundry_service", get_foundry_service, singleton=True)

    # Metabolism Persistence (Evidence + Stigmergy)
    container.register("metabolism_persistence", get_metabolism_persistence, singleton=True)

    # Interactive Text Crown Jewel (Documents as Control Surfaces)
    container.register("interactive_text_service", get_interactive_text_service, singleton=True)

    # K-Block Crown Jewel (Transactional Hyperdimensional Editing)
    container.register("harness", get_harness, singleton=True)
    container.register("cosmos", get_cosmos, singleton=True)

    # ASHC Crown Jewel (Proof-Generating Self-Hosting Compiler)
    container.register("lemma_database", get_lemma_database, singleton=True)

    # Fusion Crown Jewel (Symmetric Supersession)
    container.register("fusion_service", get_fusion_service, singleton=True)

    # Trail Intelligence (Visual Trail Graph Session 3)
    container.register("embedder", get_embedder, singleton=True)

    # Sovereign Crown Jewel (Inbound Sovereignty)
    container.register("sovereign_store", get_sovereign_store, singleton=True)

    # WitnessedGraph Crown Jewel (Unified Edge Composition)
    container.register("witnessed_graph_service", get_witnessed_graph_service, singleton=True)

    # Hypergraph Editor Crown Jewel (Modal Graph Editing)
    container.register("editor_service", get_editor_service, singleton=True)

    # Proxy Handle Store (AD-015: Epistemic Hygiene)
    container.register("proxy_handle_store", get_proxy_handle_store, singleton=True)

    # Explorer Crown Jewel (Unified Data Explorer)
    container.register("unified_query_service", get_unified_query_service, singleton=True)

    logger.info(
        "Core services registered (Brain + Witness + Conductor + Tooling + Verification + Foundry + Interactive Text + K-Block + ASHC + Fusion)"
    )

    # Import service nodes to trigger @node registration
    # FAIL-FAST: Crown Jewel import failures are WARNING level (visible)
    try:
        from services.brain import BrainNode  # noqa: F401

        logger.info("BrainNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"BrainNode not available: {e}")

    try:
        from services.morpheus.node import MorpheusNode  # noqa: F401

        logger.info("MorpheusNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"MorpheusNode not available: {e}")

    try:
        from protocols.agentese.contexts.concept_principles import (
            PrinciplesNode,  # noqa: F401
        )

        logger.info("PrinciplesNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"PrinciplesNode not available: {e}")

    # Note: ConductorNode removed 2025-12-21 (Crown Jewel Cleanup)

    # CLI v7 Phase 1: File Node (Safe File I/O)
    try:
        from protocols.agentese.contexts.world_file import FileNode  # noqa: F401

        logger.info("FileNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"FileNode not available: {e}")

    # CLI v7 Phase 6: Swarm Node (Multi-Agent Coordination)
    try:
        from protocols.agentese.contexts.self_swarm import SwarmNode  # noqa: F401

        logger.info("SwarmNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"SwarmNode not available: {e}")

    # Agent Foundry Crown Jewel (JIT Agent Synthesis)
    try:
        from services.foundry import FoundryNode  # noqa: F401

        logger.info("FoundryNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"FoundryNode not available: {e}")

    # Fusion Crown Jewel (Symmetric Supersession)
    try:
        from services.fusion import FusionNode  # noqa: F401

        logger.info("FusionNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"FusionNode not available: {e}")

    # Sovereign Crown Jewel (Inbound Sovereignty)
    try:
        from services.sovereign import SovereignNode  # noqa: F401

        logger.info("SovereignNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"SovereignNode not available: {e}")

    # WitnessedGraph Crown Jewel (Unified Edge Composition)
    try:
        from services.witnessed_graph.node import GraphNode  # noqa: F401

        logger.info("GraphNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"GraphNode not available: {e}")

    # Hypergraph Editor Crown Jewel (Modal Graph Editing)
    try:
        from services.hypergraph_editor import EditorNode  # noqa: F401

        logger.info("EditorNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"EditorNode not available: {e}")

    # Living Docs Crown Jewel (Docs as Projection)
    try:
        from services.living_docs.node import LivingDocsNode, SelfDocsNode  # noqa: F401

        logger.info("LivingDocsNode + SelfDocsNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"LivingDocsNode not available: {e}")

    # Explorer Crown Jewel (Unified Data Explorer for Brain Page)
    try:
        from services.explorer import ExplorerNode  # noqa: F401

        logger.info("ExplorerNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"ExplorerNode not available: {e}")

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
    Synchronous provider setup for CLI projection.

    Runs the async setup_providers() to ensure all services are registered
    before AGENTESE invocations. Uses asyncio.run() to bootstrap async
    providers in a sync context.

    Teaching:
        gotcha: CLI projection calls this BEFORE invoking via registry.
                If providers aren't wired, nodes fall through to JIT fallback.
                This was the cause of `kg graph` returning "Concept: graph" instead
                of actual graph data.
                (Evidence: kg graph now returns WitnessedGraph output)
    """
    import asyncio

    try:
        # Check if event loop is already running
        asyncio.get_running_loop()
        # If we get here, we're in an async context - can't use asyncio.run()
        # The caller should have already called setup_providers()
        logger.debug("Event loop already running, skipping sync setup")
    except RuntimeError:
        # No running event loop - safe to bootstrap
        asyncio.run(setup_providers())
        logger.debug("Providers bootstrapped synchronously for CLI")


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
    # Brain Crown Jewel
    "get_brain_table_adapter",
    "get_brain_persistence",
    # Principles
    "get_principle_loader",
    # Conductor (CLI v7 Phase 1, 2 & 6)
    "get_window_persistence",
    "get_summarizer",
    "get_file_guard",
    "get_swarm_spawner",
    # K-gent Soul
    "get_kgent_soul",
    # Morpheus LLM Gateway
    "get_morpheus_persistence",
    # Note: get_mark_store removed in Crown Jewel Cleanup 2025-12-21
    # Logos (cross-jewel invocation)
    "get_logos",
    # U-gent Tool Infrastructure
    "get_tool_registry",
    "get_tool_executor",
    # Verification Crown Jewel
    "get_verification_persistence",
    # Liminal Protocols
    "get_coffee_service",
    # Foundry Crown Jewel
    "get_foundry_service",
    # Metabolism Persistence
    "get_metabolism_persistence",
    # Interactive Text Crown Jewel
    "get_interactive_text_service",
    # ASHC Crown Jewel
    "get_lemma_database",
    # Fusion Crown Jewel
    "get_fusion_service",
    # Trail Intelligence
    "get_embedder",
    # Sovereign Crown Jewel
    "get_sovereign_store",
    # Hypergraph Editor Crown Jewel
    "get_editor_service",
    # Explorer Crown Jewel
    "get_unified_query_service",
]
