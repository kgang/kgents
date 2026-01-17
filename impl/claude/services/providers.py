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
    from agents.d.universe import Universe
    from agents.k.soul import KgentSoul
    from agents.l.embedders import SentenceTransformerEmbedder
    from models.brain import Crystal
    from protocols.agentese.logos import Logos
    from services import witnessed_graph
    from services.ashc.persistence import PostgresLemmaDatabase
    from services.brain import BrainPersistence
    from services.chat.persistence import ChatPersistence
    from services.code import CodeService
    from services.conductor import Summarizer, WindowPersistence
    from services.conductor.file_guard import FileEditGuard
    from services.conductor.swarm import SwarmSpawner
    from services.director.director import DocumentDirector
    from services.explorer import UnifiedQueryService
    from services.feed.service import FeedService
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
    from services.witness.bus import WitnessSynergyBus
    from services.zero_seed.ashc_self_awareness import ASHCSelfAwareness
    from services.zero_seed.galois import GaloisLossComputer

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


async def get_universe() -> "Universe":
    """
    Get the Universe for D-gent Crystal storage.

    Universe is D-gent's domain - unified data management.
    Auto-selects best available backend (Postgres > SQLite > Memory).

    Used by ChatPersistence, WitnessPersistence, and other services
    that work with typed data (Crystal, Mark, etc.).
    """
    from agents.d.universe import get_universe as _get_universe

    return _get_universe()


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


async def get_chat_persistence() -> "ChatPersistence":
    """
    Get the ChatPersistence service for Chat Crown Jewel.

    Uses Universe for crystal-based storage.

    Used by Chat API for session persistence.
    """
    from services.chat.persistence import ChatPersistence

    return ChatPersistence()


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

    Uses Universe for crystal-based storage.

    Used by WitnessNode for self.witness.* AGENTESE paths.
    """
    from services.witness import WitnessPersistence

    return WitnessPersistence()


async def get_daily_lab():
    """
    Get the DailyLab service for Daily Lab Crown Jewel.

    The Daily Lab provides WARMTH-calibrated daily journaling:
    - Low-friction mark capture
    - Trail navigation by date
    - Crystal compression with honesty disclosure
    - Export to markdown/JSON

    Used by DailyLabNode for witness.daily_lab.* AGENTESE paths.
    """
    from services.witness.daily_lab import DailyLab

    return DailyLab()


# Alias for nodes that declare dependency as "witness" instead of "witness_persistence"
async def get_witness() -> "WitnessPersistence":
    """Alias for get_witness_persistence (for nodes declaring 'witness' dependency)."""
    return await get_witness_persistence()


# Alias for nodes that declare dependency as "brain" instead of "brain_persistence"
async def get_brain() -> "BrainPersistence":
    """Alias for get_brain_persistence (for nodes declaring 'brain' dependency)."""
    return await get_brain_persistence()


async def get_bus() -> "WitnessSynergyBus":
    """
    Get the WitnessSynergyBus for cross-jewel event publishing.

    Used by DocumentDirectorNode and other nodes requiring event emission.
    """
    from services.witness.bus import get_synergy_bus

    return get_synergy_bus()


async def get_director() -> "DocumentDirector":
    """
    Get the DocumentDirector service for document lifecycle orchestration.

    The director composes:
    - SovereignStore: Entity storage
    - WitnessPersistence: Witness marks
    - WitnessSynergyBus: Event publishing

    Used by DocumentDirectorNode for concept.document.* AGENTESE paths.
    """
    from services.director.director import DocumentDirector

    store = await get_sovereign_store()
    witness = await get_witness_persistence()
    bus = await get_bus()

    return DocumentDirector(store=store, witness=witness, bus=bus)


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
# Zero Seed Crown Jewel (Galois-Grounded Constitutional Evaluation)
# =============================================================================


async def get_galois_service() -> "GaloisLossComputer":
    """
    Get the GaloisLossComputer for constitutional evaluation.

    The Galois loss service implements the core formula:
        L(P) = d(P, C(R(P)))

    Where:
    - R: Prompt -> ModularPrompt (restructure via LLM)
    - C: ModularPrompt -> Prompt (reconstitute via LLM)
    - d: Prompt x Prompt -> [0,1] (semantic distance)

    Used by:
    - Constitutional evaluator for evidence tier classification
    - Zero Seed bootstrap verification
    - Proof coherence validation

    Evidence tiers (Kent-calibrated thresholds):
    - CATEGORICAL: L < 0.10 (near-lossless, deductive)
    - EMPIRICAL: L < 0.38 (moderate loss, inductive)
    - AESTHETIC: L < 0.45 (taste-based judgment)
    - SOMATIC: L < 0.65 (intuitive, embodied)
    - CHAOTIC: L >= 0.65 (high entropy, unreliable)

    See: spec/protocols/zero-seed1/galois.md
    """
    from services.zero_seed.galois import GaloisLossComputer

    return GaloisLossComputer()


async def get_ashc_self_awareness() -> "ASHCSelfAwareness":
    """
    Get the ASHCSelfAwareness service for Constitutional introspection.

    ASHC Self-Awareness enables kgents to answer "Why does this file exist?"
    by providing five introspection APIs:

    1. am_i_grounded(block_id) - Returns bool + derivation path to L0
    2. what_principle_justifies(action) - Returns principle + loss score
    3. verify_self_consistency() - Returns consistency report
    4. get_derivation_ancestors(block_id) - Returns full lineage to L0
    5. get_downstream_impact(block_id) - Returns dependent blocks

    Philosophy:
        "The compiler that knows itself is the compiler that trusts itself."

    Used by:
    - Constitutional introspection queries
    - ASHC derivation verification
    - Self-reflective OS components

    See: services/zero_seed/ashc_self_awareness.py
    """
    from services.zero_seed.ashc_self_awareness import get_ashc_self_awareness as get_service

    return get_service()


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


async def get_dialectic_service():
    """
    Get the DialecticalFusionService for Kent+Claude dialectical synthesis.

    The dialectic service operationalizes Chapter 17 (Dialectical Fusion):
    - thesis: Kent's position
    - antithesis: Claude's position
    - synthesis: A fusion better than either alone (categorical cocone)

    The Emerging Constitution (7 articles) governs the fusion:
        I.   Symmetric Agency
        II.  Adversarial Cooperation
        III. Supersession Rights
        IV.  The Disgust Veto (Kent's absolute)
        V.   Trust Accumulation
        VI.  Fusion as Goal
        VII. Amendment

    Used by DialecticNode for self.dialectic.* AGENTESE paths.
    Used by FusionConceptNode for concept.fusion.* AGENTESE paths.

    See: docs/theory/17-dialectic.md
    See: plans/theory-operationalization/05-co-engineering.md (E3)
    """
    from services.dialectic import DialecticalFusionService

    return DialecticalFusionService()


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

    Composes two edge sources:
    - Sovereign: Code structure edges (imports, calls, inherits)
    - Witness: Mark-based edges (evidence, decisions, gotchas)

    Usage:
        graph = await container.get("witnessed_graph_service")
        result = await graph.neighbors("spec/agents/d-gent.md")
    """
    from services.witnessed_graph import (
        SovereignSource,
        WitnessedGraphService,
        WitnessSource,
    )

    # Get dependencies
    sovereign_store = await get_sovereign_store()
    witness_persistence = await get_witness_persistence()

    # Create sources (SpecLedgerSource removed - frontend support dropped)
    sovereign_source = SovereignSource(sovereign_store)
    witness_source = WitnessSource(witness_persistence)

    # Compose into unified graph
    service = WitnessedGraphService(
        sovereign_source=sovereign_source,
        witness_source=witness_source,
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
    from agents.d.universe import get_universe
    from services.explorer import UnifiedQueryService

    # Use Universe for data access (new Crystal architecture)
    universe = get_universe()
    return UnifiedQueryService(universe)


# =============================================================================
# CLI Tool Use Services (Phases 1-5)
# =============================================================================


async def get_audit_store():
    """
    Get the AuditStore for spec audit result persistence.

    Phase 1: Spec audit results with principle scores, drift detection,
    and witness marking.

    Used by audit service for database-backed audit history.
    """
    from services.audit.store import get_audit_store

    return get_audit_store()


async def get_annotation_store():
    """
    Get the AnnotationStore for spec ↔ impl annotations.

    Phase 2: Bidirectional annotations linking spec to principles,
    implementations, gotchas, and design decisions.

    Used by annotate service for database-backed annotation storage.
    """
    from services.annotate.store import AnnotationStore

    return AnnotationStore()


async def get_probe_store():
    """
    Get the ProbeStore for categorical law probe results.

    Phase 3: Probe results for identity, associativity, coherence,
    trust, health, and budget checks. Stores failures by default.

    Used by probe service for database-backed probe history.
    """
    from services.probe.store import get_probe_store

    return get_probe_store()


async def get_experiment_store():
    """
    Get the ExperimentStore for evidence-gathering experiments.

    Phase 4: Experiment persistence for trials, evidence bundles,
    and historical analysis.

    Used by experiment service for database-backed experiment storage.
    """
    from services.experiment.store import get_experiment_store

    return get_experiment_store()


async def get_composition_store():
    """
    Get the CompositionStore for named command compositions.

    Phase 5: Composition persistence for reusable kg command sequences.

    Used by compose service for database-backed composition storage.
    """
    from services.compose.store import get_composition_store

    return get_composition_store()


# =============================================================================
# Code Crown Jewel (Function-Level Artifact Tracking)
# =============================================================================


async def get_code_service() -> "CodeService":
    """
    Get the CodeService for function-level code artifact tracking.

    The Code Crown Jewel tracks Python code at function granularity:
    - Functions as atomic crystals
    - K-Blocks as file-level boundaries
    - Ghosts as spec placeholders
    - Call graphs as semantic edges

    Used by CodeNode for world.code.* AGENTESE paths.
    """
    from services.code import CodeService

    # Get Universe for storage
    universe = await get_universe()

    return CodeService(universe=universe)


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


async def get_feed_service():
    """
    Get the FeedService for algorithmic K-Block discovery.

    Feed is a primitive, not a component. Provides filtered, ranked streams
    of K-Blocks with pagination support.

    Example:
        service = await get_feed_service()
        result = await service.get_cosmos(user, offset=0, limit=20)
    """
    from services.feed.service import get_feed_service as get_service

    return get_service()


async def get_feed_feedback_persistence():
    """
    Get the FeedFeedbackPersistence for user interaction tracking.

    Records user interactions (views, engagements, dismissals) with K-Blocks
    to enable personalized ranking and analytics.

    Example:
        persistence = await get_feed_feedback_persistence()
        await persistence.record_interaction(user_id, kblock_id, FeedbackAction.VIEW)
    """
    from services.feed.persistence import FeedFeedbackPersistence

    # Get session factory for database access
    session_factory = await get_session_factory()

    return FeedFeedbackPersistence(session_factory=session_factory)


async def get_reflection_service():
    """
    Get the SelfReflectionService for Constitutional introspection.

    Provides access to the 22 Constitutional K-Blocks that form the
    axiomatic foundation of kgents. Supports querying, navigation,
    and derivation chain inspection.

    Example:
        service = await get_reflection_service()
        graph = await service.get_constitution()
        chain = await service.get_derivation_chain("ASHC")
    """
    from services.self.reflection_service import get_reflection_service as get_service

    return get_service()


async def get_codebase_scanner():
    """
    Get the CodebaseScanner for codebase introspection.

    The scanner uses Python's ast module to extract structure from source files:
    - Module docstrings
    - Class and function definitions
    - Import statements (for derivation edges)

    Used by CodebaseNode for self.codebase.* AGENTESE paths.

    Example:
        scanner = await get_codebase_scanner()
        graph = await scanner.scan_to_graph(Path("services"))
    """
    from pathlib import Path

    from services.self.scanner import CodebaseScanner

    # Default to impl/claude as project root
    project_root = Path(__file__).parent.parent
    return CodebaseScanner(project_root=project_root)


async def get_git_service():
    """
    Get the GitHistoryService for git history integration.

    Provides comprehensive git history access:
    - Recent commits with metadata
    - File history with blame
    - Commit diffs
    - Commit search
    - Spec/impl pair detection

    Used by GitNode for self.git.* AGENTESE paths.

    Example:
        service = await get_git_service()
        commits = await service.get_recent_commits(limit=50)
        blame = await service.get_file_blame("services/self/node.py")
    """
    from services.self.git_service import get_git_service as get_service

    return get_service()


async def get_decisions_service():
    """
    Get the DecisionsService for kg decide history.

    Aggregates decisions from multiple sources:
    - FusionService (symmetric supersession decisions)
    - WitnessPersistence (marks with decision tags)

    Used by DecisionsNode for self.decisions.* AGENTESE paths.

    Example:
        service = await get_decisions_service()
        decisions = await service.list_decisions(limit=100)
        matched = await service.search_decisions("LangChain")
    """
    from services.self.decisions_service import get_decisions_service as get_service

    return get_service()


async def get_witness_timeline_service():
    """
    Get the WitnessTimelineService for development timeline view.

    Provides unified access to all witness activity:
    - Marks (execution artifacts)
    - Crystals (compressed memory)
    - Decisions (dialectical fusions)

    Used by WitnessTimelineNode for self.timeline.* AGENTESE paths.

    Example:
        service = await get_witness_timeline_service()
        events = await service.view(limit=50)
        results = await service.search("refactoring")

    See: services/self/witness_timeline_service.py
    """
    from services.self.witness_timeline_service import (
        get_witness_timeline_service as get_service,
    )

    return get_service()


async def get_inspection_service():
    """
    Get the InspectionService for universal deep inspection.

    Provides deep inspection of any system element:
    - Files (Python modules, specs, plans)
    - K-Blocks (Constitutional and codebase)
    - Marks and Crystals

    Used by InspectionNode for self.inspect.* AGENTESE paths.

    Example:
        service = await get_inspection_service()
        result = await service.inspect_file("services/witness/mark.py")
        kblock = await service.inspect_kblock("COMPOSABLE")

    See: services/self/inspection_service.py
    """
    from services.self.inspection_service import get_inspection_service as get_service

    return get_service()


async def get_pilot_registry():
    """
    Get the PilotRegistry for tangible endeavor pilots.

    The registry scans pilots/*/PROTO_SPEC.md files and provides
    structured access to pilot metadata.

    Example:
        registry = await get_pilot_registry()
        pilots = await registry.list_pilots(tier="core")
        spec = await registry.get_pilot_spec("trail-to-crystal-daily-lab")

    See: services/pilots/registry.py
    """
    from services.pilots import get_pilot_registry as get_registry

    return get_registry()


async def get_axiom_discovery_service():
    """
    Get the AxiomDiscoveryService for endeavor axiom extraction.

    Implements a 5-turn structured dialogue to extract endeavor axioms:
    - A1: Success Definition
    - A2: Feeling Target
    - A3: Constraints
    - A4: Verification

    Example:
        service = await get_axiom_discovery_service()
        session = await service.start_discovery("I want to build a daily habit")
        turn = await service.process_turn(session.session_id, "Feel present")

    See: services/endeavor/discovery.py
    """
    from services.endeavor import get_axiom_discovery_service as get_service

    return get_service()


async def get_pilot_bootstrap_service():
    """
    Get the PilotBootstrapService for pilot matching and creation.

    Given EndeavorAxioms, this service:
    - Matches existing pilots
    - Creates custom pilots
    - Sets up witness infrastructure

    Example:
        service = await get_pilot_bootstrap_service()
        match = await service.match_pilot(axioms)
        if not match:
            pilot = await service.bootstrap_pilot(axioms, "my-lab")

    See: services/endeavor/bootstrap.py
    """
    from services.endeavor import get_pilot_bootstrap_service as get_service

    return get_service()


async def get_kgames_kernel():
    """
    Get the GameKernel for game generation and verification.

    The GameKernel holds the four constitutional axioms for game quality:
    - A1: AGENCY (L=0.02) - Player choices determine outcomes
    - A2: ATTRIBUTION (L=0.05) - Outcomes trace to identifiable causes
    - A3: MASTERY (L=0.08) - Skill development is externally observable
    - A4: COMPOSITION (L=0.03) - Moments compose algebraically into arcs

    Example:
        kernel = await get_kgames_kernel()
        result = kernel.validate_implementation(my_game)
    """
    from services.kgames import create_kernel

    return create_kernel()


async def get_amendment_service():
    """
    Get the AmendmentWorkflowService for constitutional evolution.

    The amendment service enables kgents to evolve its own constitution
    through a formal, witnessed amendment process (Week 11-12 of Self-Reflective OS).

    Lifecycle:
        DRAFT -> PROPOSED -> UNDER_REVIEW -> APPROVED/REJECTED -> APPLIED/REVERTED

    All transitions are witnessed, creating an auditable trail of constitutional evolution.

    Example:
        service = await get_amendment_service()
        amendment = await service.create_draft(
            title="Refine TASTEFUL",
            description="Add anti-patterns",
            amendment_type=AmendmentType.PRINCIPLE_MODIFICATION,
            ...
        )
        await service.propose(amendment.id)
        await service.approve(amendment.id, "Clear improvement")
        await service.apply(amendment.id)

    See: services/amendment/workflow.py
    See: plans/self-reflective-os/ (Week 11-12)
    """
    from services.amendment import AmendmentWorkflowService
    from services.witness import WitnessCrystalAdapter

    # Get witness crystal adapter for recording amendment events
    try:
        witness = WitnessCrystalAdapter()
    except Exception:
        witness = None

    return AmendmentWorkflowService(witness=witness)


# =============================================================================
# Skill Injection Crown Jewel (JIT Skill Surfacing)
# =============================================================================


async def get_skill_registry():
    """
    Get the SkillRegistry for JIT skill injection.

    The SkillRegistry holds all available skills with their activation conditions.
    Skills surface exactly when needed based on task context.

    Philosophy:
        "Skills surface exactly when needed, not before."
        "Context-aware activation based on task patterns."

    Example:
        registry = await get_skill_registry()
        skills = registry.list_skills()
        match = registry.find_by_keywords(["agent", "state machine"])

    See: services/skill_injection/registry.py
    """
    from services.skill_injection import get_skill_registry as get_registry

    return get_registry()


async def get_jit_injector():
    """
    Get the JITInjector for runtime skill content injection.

    The JITInjector orchestrates:
    - Skill activation based on task context
    - Content injection with gotchas
    - Usage outcome recording for learning

    Philosophy:
        "Learn from what worked, forget what didn't."

    Example:
        injector = await get_jit_injector()
        result = await injector.inject_for_task(
            task="Add a Crown Jewel service",
            active_files=["services/foo/node.py"],
        )

    See: services/skill_injection/jit_injector.py
    """
    from services.skill_injection import get_jit_injector as get_injector

    return get_injector()


async def get_axiom_discovery_pipeline():
    """
    Get the AxiomDiscoveryPipeline for personal axiom discovery.

    Discovers personal axioms from decision history:
    - L < 0.05 fixed points Kent never violates
    - Pattern extraction from decision marks
    - Contradiction detection between axioms

    Philosophy:
        "Axioms are not stipulated but discovered.
         They are the fixed points of your decision landscape."

    Example:
        pipeline = await get_axiom_discovery_pipeline()
        result = await pipeline.discover_axioms(
            user_id="kent",
            days=30,
            max_candidates=5,
        )

    See: services/zero_seed/axiom_discovery_pipeline.py
    """
    from services.zero_seed import AxiomDiscoveryPipeline

    return AxiomDiscoveryPipeline()


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
    container.register(
        "universe", get_universe, singleton=True
    )  # D-gent Universe (Crystal persistence)
    container.register("brain_persistence", get_brain_persistence, singleton=True)
    container.register("chat_persistence", get_chat_persistence, singleton=True)
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
    container.register(
        "witness", get_witness, singleton=True
    )  # Alias for nodes declaring "witness"
    container.register(
        "brain", get_brain, singleton=True
    )  # Alias for nodes declaring "brain" (maps to brain_persistence)
    container.register("bus", get_bus, singleton=True)  # WitnessSynergyBus
    container.register(
        "daily_lab", get_daily_lab, singleton=True
    )  # Daily Lab (witness.daily_lab.*)

    # Document Director Crown Jewel (Spec-to-Code Lifecycle)
    container.register("director", get_director, singleton=True)

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

    # Zero Seed Crown Jewel (Galois-Grounded Constitutional Evaluation)
    container.register("galois_service", get_galois_service, singleton=True)

    # ASHC Self-Awareness Crown Jewel (Constitutional Introspection)
    container.register("ashc_self_awareness", get_ashc_self_awareness, singleton=True)

    # Fusion Crown Jewel (Symmetric Supersession)
    container.register("fusion_service", get_fusion_service, singleton=True)

    # Dialectic Crown Jewel (Thesis-Antithesis-Synthesis)
    container.register("dialectic_service", get_dialectic_service, singleton=True)

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

    # Feed Primitive (Algorithmic K-Block Discovery)
    container.register("feed_service", get_feed_service, singleton=True)
    container.register("feed_feedback_persistence", get_feed_feedback_persistence, singleton=True)

    # Self-Reflective OS (Constitutional Introspection + Codebase Scanning + Git + Decisions)
    container.register("reflection_service", get_reflection_service, singleton=True)
    container.register("codebase_scanner", get_codebase_scanner, singleton=True)
    container.register("git_service", get_git_service, singleton=True)
    container.register("decisions_service", get_decisions_service, singleton=True)
    container.register("witness_timeline_service", get_witness_timeline_service, singleton=True)
    container.register("inspection_service", get_inspection_service, singleton=True)

    # Explorer Crown Jewel (Unified Data Explorer)
    container.register("unified_query_service", get_unified_query_service, singleton=True)

    # CLI Tool Use Services (Phases 1-5)
    container.register("audit_store", get_audit_store, singleton=True)
    container.register("annotation_store", get_annotation_store, singleton=True)
    container.register("probe_store", get_probe_store, singleton=True)
    container.register("experiment_store", get_experiment_store, singleton=True)
    container.register("composition_store", get_composition_store, singleton=True)

    # Code Crown Jewel (Function-Level Artifact Tracking)
    container.register("code_service", get_code_service, singleton=True)

    # KGames Crown Jewel (Game Generation from Axioms)
    container.register("kgames_kernel", get_kgames_kernel, singleton=True)

    # Pilots Tangibility (Self-Reflective OS: Endeavor Actualization)
    container.register("pilot_registry", get_pilot_registry, singleton=True)
    container.register("axiom_discovery_service", get_axiom_discovery_service, singleton=True)
    container.register("pilot_bootstrap_service", get_pilot_bootstrap_service, singleton=True)

    # Amendment Crown Jewel (Self-Reflective OS: Constitutional Evolution)
    container.register("amendment_service", get_amendment_service, singleton=True)

    # Skill Injection Crown Jewel (JIT Skill Surfacing)
    container.register("skill_registry", get_skill_registry, singleton=True)
    container.register("jit_injector", get_jit_injector, singleton=True)

    # Axiom Discovery Pipeline (Zero Seed Personal Governance)
    container.register("axiom_discovery_pipeline", get_axiom_discovery_pipeline, singleton=True)

    logger.info(
        "Core services registered (Brain + Witness + Conductor + Tooling + Verification + Foundry + Interactive Text + K-Block + ASHC + Fusion + CLI Tool Use + Code + KGames + Pilots + Amendment + Skill Injection + Axiom Discovery)"
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

    # Dialectic Crown Jewel (Thesis-Antithesis-Synthesis)
    try:
        from services.dialectic.node import DialecticNode, FusionConceptNode  # noqa: F401

        logger.info("DialecticNode + FusionConceptNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"Dialectic nodes not available: {e}")

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

    # Code Crown Jewel (Function-Level Artifact Tracking)
    try:
        from services.code.node import CodeNode  # noqa: F401

        logger.info("CodeNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"CodeNode not available: {e}")

    # Daily Lab (Trail-to-Crystal Journaling with WARMTH Calibration)
    try:
        from services.witness.daily_lab import DailyLabNode  # noqa: F401

        logger.info("DailyLabNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"DailyLabNode not available: {e}")

    # Self-Reflective OS (Constitution + Codebase + Drift + Git + Decisions)
    try:
        from services.self.node import (
            CodebaseNode,  # noqa: F401
            ConstitutionNode,  # noqa: F401
            DecisionsNode,  # noqa: F401
            DriftNode,  # noqa: F401
            GitNode,  # noqa: F401
        )

        logger.info("Self-Reflective OS nodes registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"Self-Reflective OS nodes not available: {e}")

    # KGames Crown Jewel (Game Generation from Axioms)
    try:
        from services.kgames import KGamesNode  # noqa: F401

        logger.info("KGamesNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"KGamesNode not available: {e}")

    # Pilots Tangibility (Self-Reflective OS: Endeavor Actualization)
    try:
        from services.endeavor.node import EndeavorNode, PilotsNode  # noqa: F401

        logger.info("PilotsNode + EndeavorNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"Pilots Tangibility nodes not available: {e}")

    # Amendment Crown Jewel (Self-Reflective OS: Constitutional Evolution)
    try:
        from services.amendment import AmendmentNode  # noqa: F401

        logger.info("AmendmentNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"AmendmentNode not available: {e}")

    # Skill Injection Crown Jewel (JIT Skill Surfacing)
    try:
        from services.skill_injection import SkillNode  # noqa: F401

        logger.info("SkillNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"SkillNode not available: {e}")

    # Axiom Discovery Crown Jewel (Zero Seed Personal Governance)
    try:
        from services.zero_seed import AxiomNode  # noqa: F401

        logger.info("AxiomNode registered with AGENTESE registry")
    except ImportError as e:
        logger.warning(f"AxiomNode not available: {e}")

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
    "get_universe",
    # Brain Crown Jewel
    "get_brain_table_adapter",
    "get_brain_persistence",
    # Chat Crown Jewel
    "get_chat_persistence",
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
    # Zero Seed Crown Jewel
    "get_galois_service",
    # ASHC Self-Awareness Crown Jewel
    "get_ashc_self_awareness",
    # Fusion Crown Jewel
    "get_fusion_service",
    # Dialectic Crown Jewel
    "get_dialectic_service",
    # Trail Intelligence
    "get_embedder",
    # Sovereign Crown Jewel
    "get_sovereign_store",
    # Document Director Crown Jewel
    "get_director",
    "get_witness",
    "get_brain",
    "get_bus",
    # Daily Lab Crown Jewel
    "get_daily_lab",
    # Hypergraph Editor Crown Jewel
    "get_editor_service",
    # Explorer Crown Jewel
    "get_unified_query_service",
    # CLI Tool Use Services
    "get_audit_store",
    "get_annotation_store",
    "get_probe_store",
    "get_experiment_store",
    "get_composition_store",
    # Code Crown Jewel
    "get_code_service",
    # Feed Feedback
    "get_feed_feedback_persistence",
    # Self-Reflective OS
    "get_reflection_service",
    "get_codebase_scanner",
    "get_git_service",
    "get_decisions_service",
    "get_witness_timeline_service",
    "get_inspection_service",
    # KGames Crown Jewel
    "get_kgames_kernel",
    # Amendment Crown Jewel (Self-Reflective OS: Constitutional Evolution)
    "get_amendment_service",
    # Skill Injection Crown Jewel
    "get_skill_registry",
    "get_jit_injector",
    # Axiom Discovery Pipeline
    "get_axiom_discovery_pipeline",
]
