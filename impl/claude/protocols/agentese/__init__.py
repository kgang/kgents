"""
AGENTESE: The Verb-First Ontology

Where getting IS invoking. Where nouns ARE frozen verbs.
Where observation collapses potential into actuality.

> "The noun is a lie. There is only the rate of change."

Public API (~78 exports):
- Logos: The resolver functor
- Observer: Lightweight observer with gradations
- LogosNode: Protocol for resolvable entities
- path(): String-based composition with >>
- @aspect: Decorator with category enforcement
- query()/subscribe(): Bounded queries and subscriptions
- WiredLogos: High-level integration wrapper
"""

from __future__ import annotations

from typing import Any, cast

# =============================================================================
# PUBLIC API - Core
# =============================================================================
# Logos and creation
from .logos import (
    # v3 Path Composition
    AgentesePath,
    ComposedPath,
    IdentityPath,
    Logos,
    UnboundComposedPath,
    create_logos,
    path,
)

# v3 API: Path is an alias for AgentesePath
Path = AgentesePath

# Node protocol and observer
# =============================================================================
# PUBLIC API - Adapter
# =============================================================================
from .adapter import (
    AgentesAdapter,
    create_adapter,
)

# =============================================================================
# PUBLIC API - Effects & Aspects
# =============================================================================
from .affordances import (
    CATEGORY_RULES,
    AspectCategory,
    AspectMetadata,
    DeclaredEffect,
    Effect,
    aspect,
    get_aspect_metadata,
    is_aspect,
)

# =============================================================================
# PUBLIC API - Alias System
# =============================================================================
from .aliases import (
    AliasError,
    AliasNotFoundError,
    AliasRecursionError,
    AliasRegistry,
    AliasShadowError,
    create_alias_registry,
    create_standard_aliases,
    expand_aliases,
    get_default_aliases_path,
)

# =============================================================================
# PUBLIC API - Context Factory (single entry point)
# =============================================================================
from .contexts import (
    VALID_CONTEXTS,
    create_context_resolvers,
)

# =============================================================================
# PUBLIC API - Exceptions
# =============================================================================
from .exceptions import (
    AffordanceError,
    AgentesError,
    BudgetExhaustedError,
    CompositionViolationError,
    LawCheckFailed,
    ObserverRequiredError,
    PathNotFoundError,
    PathSyntaxError,
    TastefulnessError,
)

# =============================================================================
# PUBLIC API - Composition Primitives
# =============================================================================
from .laws import (
    IDENTITY,
    Composable,
    Id,
    Identity,
)
from .node import (
    AffordanceSet,
    AgentMeta,
    BaseLogosNode,
    BasicRendering,
    JITLogosNode,
    LogosNode,
    Observer,
    Renderable,
)

# =============================================================================
# PUBLIC API - Aspect Pipelines
# =============================================================================
from .pipeline import (
    AspectPipeline,
    PipelineMixin,
    PipelineResult,
    PipelineStageResult,
    add_pipe_to_logos_node,
    add_pipeline_to_logos,
    create_pipeline,
)

# =============================================================================
# PUBLIC API - Query System
# =============================================================================
from .query import (
    QueryBoundError,
    QueryBuilder,
    QueryMatch,
    QueryResult,
    QuerySyntaxError,
    create_query_builder,
    query,
)

# =============================================================================
# PUBLIC API - Subscription System
# =============================================================================
from .subscription import (
    AgentesEvent,
    DeliveryMode,
    EventType,
    LogosSubscriptionMixin,
    OrderingMode,
    Subscription,
    SubscriptionConfig,
    SubscriptionManager,
    SubscriptionMetrics,
    add_subscription_methods_to_logos,
    create_subscription_manager,
)

# =============================================================================
# PUBLIC API - Wiring & Integration
# =============================================================================
from .wiring import (
    WiredLogos,
    create_minimal_wired_logos,
    create_wired_logos,
    wire_existing_logos,
)

# =============================================================================
# PUBLIC API EXPORTS (~78 exports)
# =============================================================================

__all__ = [
    # === Core (15) ===
    "Logos",
    "create_logos",
    "Observer",
    "LogosNode",
    "AffordanceSet",
    "AgentMeta",
    "Renderable",
    "BasicRendering",
    "BaseLogosNode",
    "JITLogosNode",
    # Path composition
    "AgentesePath",
    "Path",
    "UnboundComposedPath",
    "ComposedPath",
    "IdentityPath",
    "path",
    # === Effects & Aspects (8) ===
    "Effect",
    "DeclaredEffect",
    "AspectCategory",
    "AspectMetadata",
    "CATEGORY_RULES",
    "aspect",
    "get_aspect_metadata",
    "is_aspect",
    # === Exceptions (9) ===
    "AgentesError",
    "PathNotFoundError",
    "PathSyntaxError",
    "AffordanceError",
    "ObserverRequiredError",
    "TastefulnessError",
    "BudgetExhaustedError",
    "CompositionViolationError",
    "LawCheckFailed",
    # === Query System (7) ===
    "QueryResult",
    "QueryMatch",
    "QueryBuilder",
    "QuerySyntaxError",
    "QueryBoundError",
    "query",
    "create_query_builder",
    # === Alias System (9) ===
    "AliasRegistry",
    "AliasError",
    "AliasShadowError",
    "AliasRecursionError",
    "AliasNotFoundError",
    "create_alias_registry",
    "create_standard_aliases",
    "expand_aliases",
    "get_default_aliases_path",
    # === Subscription System (11) ===
    "AgentesEvent",
    "EventType",
    "DeliveryMode",
    "OrderingMode",
    "SubscriptionConfig",
    "Subscription",
    "SubscriptionManager",
    "SubscriptionMetrics",
    "create_subscription_manager",
    "LogosSubscriptionMixin",
    "add_subscription_methods_to_logos",
    # === Aspect Pipelines (7) ===
    "AspectPipeline",
    "PipelineResult",
    "PipelineStageResult",
    "PipelineMixin",
    "add_pipe_to_logos_node",
    "add_pipeline_to_logos",
    "create_pipeline",
    # === Wiring (4) ===
    "WiredLogos",
    "create_wired_logos",
    "create_minimal_wired_logos",
    "wire_existing_logos",
    # === Context (2) ===
    "VALID_CONTEXTS",
    "create_context_resolvers",
    # === Composition (4) ===
    "Identity",
    "Id",
    "IDENTITY",
    "Composable",
    # === Adapter (2) ===
    "AgentesAdapter",
    "create_adapter",
    # === Crown Jewel Brain Factory (1) ===
    "create_brain_logos",
]


# =============================================================================
# Crown Jewel Brain Factory (Session 4)
# =============================================================================


def create_brain_logos(
    dimension: int = 384,
    embedder_type: str = "auto",
) -> "Logos":
    """
    Create a Logos instance with full Holographic Brain wiring.

    This is the single factory function for Crown Jewel Brain that wires:
    - MemoryCrystal: Holographic memory storage
    - L-gent Embedder: Semantic embeddings (sentence-transformers or fallback)
    - CartographerAgent: Memory navigation with VectorSearchable
    - N-gent TraceStore: Desire line computation with TraceQueryable

    Session 4 Goal: Wire semantic embeddings for real ghost surfacing.

    Args:
        dimension: Embedding dimension (384 for MiniLM, 64 for fallback)
        embedder_type: "auto", "sentence-transformers", or "simple"

    Returns:
        Fully-wired Logos instance ready for Holographic Brain operations

    Example:
        logos = create_brain_logos()
        observer = Observer.guest()

        # Capture with semantic embedding
        await logos.invoke('self.memory.capture', observer, content='Python tutorial')
        await logos.invoke('self.memory.capture', observer, content='Python examples')

        # Ghost surfaces semantically similar memories
        result = await logos.invoke('self.memory.ghost.surface', observer, context='Python code')
        # result['count'] > 0 (semantic similarity works!)
    """
    # Import dependencies lazily to avoid circular imports
    from agents.m.cartographer import create_cartographer
    from agents.m.crystal import create_crystal
    from agents.n.store import MemoryCrystalStore

    # 1. Create embedder
    embedder = None
    actual_dimension = dimension
    if embedder_type == "auto":
        try:
            from agents.l import create_best_available_embedder

            embedder = create_best_available_embedder()
            actual_dimension = embedder.dimension
        except Exception:
            # Fall back to no embedder (uses hash-based pseudo-embedding)
            actual_dimension = 64
    elif embedder_type == "sentence-transformers":
        try:
            from agents.l.embedders import SentenceTransformerEmbedder

            embedder = SentenceTransformerEmbedder()
            actual_dimension = embedder.dimension
        except ImportError:
            # Fall back to no embedder
            actual_dimension = 64
    else:
        # "simple" - use no embedder, fallback to hash-based
        actual_dimension = 64

    # 2. Create MemoryCrystal with matching dimension
    memory_crystal = create_crystal(dimension=actual_dimension, use_numpy=True)

    # 3. Create N-gent trace store (for desire lines)
    trace_store = MemoryCrystalStore()

    # 4. Create CrystalVectorSearchable adapter (wraps MemoryCrystal)
    class CrystalVectorSearchable:
        """Adapter to make MemoryCrystal implement VectorSearchable protocol."""

        def __init__(self, crystal: Any) -> None:
            self._crystal = crystal

        async def find_similar(
            self,
            embedding: list[float],
            threshold: float = 0.5,
            limit: int = 100,
        ) -> list[tuple[str, list[float], float]]:
            """Find similar items by embedding."""
            results = self._crystal.retrieve(
                cue=embedding,
                threshold=threshold,
                limit=limit,
            )
            # Convert ResonanceMatch to (id, embedding, similarity) tuples
            output = []
            for match in results:
                pattern = self._crystal.get_pattern(match.concept_id)
                if pattern:
                    output.append(
                        (
                            match.concept_id,
                            pattern.embedding,
                            match.similarity,
                        )
                    )
            return output

    vector_search = CrystalVectorSearchable(memory_crystal)

    # 5. Create CartographerAgent with full wiring
    cartographer = create_cartographer(
        vector_search=vector_search,
        trace_store=cast(Any, trace_store),  # type: ignore[arg-type]
    )

    # 6. Create Logos with all wiring
    logos = create_logos(
        memory_crystal=memory_crystal,
        cartographer=cartographer,
        embedder=embedder,
    )

    return logos


# =============================================================================
# API Wiring
# =============================================================================


def _wire_api() -> None:
    """Wire API methods into Logos and LogosNode classes."""
    # Wire pipeline methods to Logos
    add_pipeline_to_logos(Logos)

    # Wire subscription methods to Logos
    add_subscription_methods_to_logos(Logos)

    # Wire pipe() to BaseLogosNode for resolved nodes
    add_pipe_to_logos_node(BaseLogosNode)

    # Wire pipe() to JITLogosNode
    add_pipe_to_logos_node(JITLogosNode)


# Perform wiring on import
_wire_api()
