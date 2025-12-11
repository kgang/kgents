"""
L-gent Semantic Registry: Registry + Semantic Search Integration.

This module extends the Registry with semantic search capabilities,
completing the "three-brain" architecture:
- Brain 1: Keyword search (BM25) - implemented in Registry.find()
- Brain 2: Semantic search (Embeddings) - implemented here
- Brain 3: Graph search (Traversal) - via Lineage + Lattice layers

Phase 5 Implementation:
- SemanticRegistry: Registry with automatic embedding indexing
- Hybrid search: Combine keyword + semantic results
- Auto-indexing: Embeddings updated on register/delete
"""

from __future__ import annotations

from typing import Any

from .registry import Registry
from .semantic import Embedder, SemanticBrain, SemanticResult, SimpleEmbedder
from .types import Catalog, CatalogEntry, EntityType, SearchResult


class SemanticRegistry(Registry):
    """
    Registry with semantic search capabilities.

    Extends Registry with:
    - Automatic embedding indexing on register/delete
    - Semantic search via find_semantic()
    - Hybrid search combining keyword + semantic results

    Example:
        registry = SemanticRegistry()
        await registry.register(entry)  # Auto-indexed
        results = await registry.find_semantic("analyze sentiment")
    """

    def __init__(
        self,
        catalog: Catalog | None = None,
        embedder: Embedder | None = None,
        auto_index: bool = True,
    ) -> None:
        """Initialize semantic registry.

        Args:
            catalog: Optional existing catalog
            embedder: Optional custom embedder (defaults to SimpleEmbedder)
            auto_index: Whether to auto-index on register/delete
        """
        super().__init__(catalog)

        self.embedder = embedder or SimpleEmbedder()
        self.auto_index = auto_index
        self.semantic_brain = SemanticBrain(self.embedder)

        # Track if brain has been fitted
        self._fitted = False

    async def fit(self) -> None:
        """Build semantic index from current catalog entries.

        Call this manually if auto_index=False, or after bulk operations.
        """
        await self.semantic_brain.fit(self.catalog.entries)
        self._fitted = True

    async def register(self, entry: CatalogEntry) -> str:
        """Register entry and auto-index for semantic search.

        Args:
            entry: Catalog entry to register

        Returns:
            Entry ID
        """
        # Register with parent class
        entry_id = await super().register(entry)

        # Auto-index for semantic search
        if self.auto_index:
            # Fit on first registration
            if not self._fitted:
                await self.fit()
            else:
                # Incremental index update
                updated_entry = self.catalog.entries[entry_id]
                await self.semantic_brain.add_entry(updated_entry)

        return entry_id

    async def delete(self, id: str) -> bool:
        """Delete entry and remove from semantic index.

        Args:
            id: Entry ID to delete

        Returns:
            True if deleted, False if not found
        """
        # Delete from semantic index first
        if self.auto_index and self._fitted:
            await self.semantic_brain.remove_entry(id)

        # Delete from parent registry
        return await super().delete(id)

    async def find_semantic(
        self,
        intent: str,
        filters: dict[str, Any] | None = None,
        threshold: float = 0.5,
        limit: int = 10,
    ) -> list[SemanticResult]:
        """Search by semantic similarity to intent.

        This is "Brain 2" - semantic search via embeddings.

        Args:
            intent: Natural language description of what user wants
            filters: Optional filters (entity_type, status, etc.)
            threshold: Minimum similarity score (0.0 to 1.0)
            limit: Maximum number of results

        Returns:
            List of semantic results, ranked by similarity

        Example:
            results = await registry.find_semantic(
                "analyze financial documents",
                filters={"entity_type": EntityType.AGENT},
                threshold=0.7
            )
        """
        # Ensure brain is fitted
        if not self._fitted:
            await self.fit()

        return await self.semantic_brain.search(
            intent=intent,
            filters=filters,
            threshold=threshold,
            limit=limit,
        )

    async def find_hybrid(
        self,
        query: str,
        entity_type: EntityType | None = None,
        semantic_weight: float = 0.5,
        limit: int = 10,
    ) -> list[SearchResult]:
        """Hybrid search combining keyword + semantic results.

        Combines:
        - Brain 1 (Keyword): Registry.find() - exact matches
        - Brain 2 (Semantic): SemanticBrain.search() - intent matching

        Args:
            query: Search query (used for both keyword and semantic search)
            entity_type: Optional entity type filter
            semantic_weight: Weight for semantic scores (0.0 to 1.0)
                            0.0 = pure keyword, 1.0 = pure semantic
            limit: Maximum number of results

        Returns:
            List of search results with combined scores

        Example:
            # Balanced hybrid search
            results = await registry.find_hybrid("text processing", semantic_weight=0.5)

            # Keyword-heavy search
            results = await registry.find_hybrid("agent_007", semantic_weight=0.2)

            # Semantic-heavy search
            results = await registry.find_hybrid("summarize documents", semantic_weight=0.8)
        """
        # Validate weight
        if not 0.0 <= semantic_weight <= 1.0:
            raise ValueError("semantic_weight must be between 0.0 and 1.0")

        keyword_weight = 1.0 - semantic_weight

        # Run both searches
        keyword_results = await self.find(
            query=query, entity_type=entity_type, limit=limit * 2
        )

        filters = {"entity_type": entity_type} if entity_type else None
        semantic_results = await self.find_semantic(
            intent=query, filters=filters, threshold=0.0, limit=limit * 2
        )

        # Combine results
        combined: dict[str, tuple[float, CatalogEntry, str]] = {}

        # Add keyword results
        for result in keyword_results:
            entry_id = result.entry.id
            score = result.score * keyword_weight
            combined[entry_id] = (score, result.entry, f"Keyword: {result.explanation}")

        # Add/update with semantic results
        for semantic_result in semantic_results:
            entry_id = semantic_result.entry.id
            semantic_score = semantic_result.similarity * semantic_weight

            if entry_id in combined:
                # Combine scores
                existing_score, entry, existing_explanation = combined[entry_id]
                total_score = existing_score + semantic_score
                explanation = (
                    f"{existing_explanation} | Semantic: {semantic_result.explanation}"
                )
                combined[entry_id] = (total_score, entry, explanation)
            else:
                # Add semantic-only result
                combined[entry_id] = (
                    semantic_score,
                    semantic_result.entry,
                    f"Semantic: {semantic_result.explanation}",
                )

        # Convert to SearchResult and sort
        final_results = [
            SearchResult(
                entry=entry,
                score=score,
                match_type="hybrid",
                explanation=explanation,
            )
            for score, entry, explanation in combined.values()
        ]

        final_results.sort(key=lambda r: r.score, reverse=True)

        return final_results[:limit]

    # -------------------------------------------------------------------
    # F-gent Integration: Artifact Forging with Duplicate Detection
    # -------------------------------------------------------------------

    async def find_for_forging(
        self,
        intent: str,
        threshold: float = 0.9,
        limit: int = 5,
    ) -> list[SemanticResult]:
        """Find existing artifacts before forging new ones (F-gent integration).

        Before forging a new artifact, check if similar ones already exist.
        This prevents ecosystem bloat and encourages reuse.

        Args:
            intent: User's intent for the artifact to be forged
            threshold: Similarity threshold (default 0.9 = 90% similar)
            limit: Maximum number of duplicates to return

        Returns:
            List of similar existing artifacts, ranked by similarity

        Example:
            # Before forging, check for duplicates
            existing = await registry.find_for_forging(
                intent="Agent that summarizes research papers to JSON",
                threshold=0.9
            )
            if existing:
                # Present alternatives to user
                print(f"Found {len(existing)} similar artifacts:")
                for result in existing:
                    print(f"  - {result.entry.name} ({result.similarity:.2%})")
        """
        return await self.find_semantic(
            intent=intent,
            filters={"entity_type": EntityType.AGENT},  # Focus on agents
            threshold=threshold,
            limit=limit,
        )

    async def register_forged_artifact(
        self,
        entry: CatalogEntry,
        forged_by: str = "F-gent",
    ) -> str:
        """Register newly forged artifact with F-gent metadata.

        After successfully forging an artifact, register it in the catalog
        with proper metadata tracking.

        Args:
            entry: Catalog entry for the forged artifact
            forged_by: Name of the forging agent (default: "F-gent")

        Returns:
            Entry ID

        Example:
            # After forging: Register new artifact
            artifact_id = await registry.register_forged_artifact(
                artifact,
                forged_by="F-gent"
            )
        """
        # Add F-gent metadata
        if "forged_by" not in entry.relationships:
            entry.relationships["forged_by"] = []
        entry.relationships["forged_by"].append(forged_by)

        # Register with standard flow (includes auto-indexing)
        return await self.register(entry)

    # -------------------------------------------------------------------
    # J-gent Integration: JIT Runtime Agent Selection
    # -------------------------------------------------------------------

    async def find_for_jit_selection(
        self,
        intent: str,
        runtime_constraints: dict[str, Any] | None = None,
        threshold: float = 0.7,
        limit: int = 3,
    ) -> list[SemanticResult]:
        """Find candidate agents for JIT runtime selection (J-gent integration).

        J-gent needs to select the right agent at runtime based on intent
        and runtime constraints (entropy budget, performance requirements, etc.).

        Args:
            intent: What the user wants to accomplish
            runtime_constraints: Optional filters (e.g., {"status": Status.STABLE})
            threshold: Minimum similarity (default 0.7 = 70%)
            limit: Maximum candidates to return (default 3)

        Returns:
            List of candidate agents, ranked by relevance

        Example:
            # J-gent runtime decision backed by L-gent
            candidates = await registry.find_for_jit_selection(
                intent="Parse JSON logs and extract errors",
                runtime_constraints={"status": Status.STABLE},
                threshold=0.7
            )
            # J-gent selects best candidate based on entropy budget
            best_agent = j_gent.select_within_budget(candidates)
        """
        # Build filters from runtime constraints
        filters = runtime_constraints.copy() if runtime_constraints else {}
        filters["entity_type"] = EntityType.AGENT  # Only agents

        return await self.find_semantic(
            intent=intent,
            filters=filters,
            threshold=threshold,
            limit=limit,
        )

    async def register_jit_execution(
        self,
        agent_id: str,
        intent: str,
        success: bool,
        entropy_used: float | None = None,
    ) -> None:
        """Record JIT agent execution for feedback loop (J-gent integration).

        Track which agents were selected for which intents and how they
        performed. This creates a feedback loop for improving selection.

        Args:
            agent_id: ID of the agent that was executed
            intent: Intent it was selected for
            success: Whether execution succeeded
            entropy_used: Optional entropy budget consumed

        Example:
            # After J-gent executes selected agent
            await registry.register_jit_execution(
                agent_id="parser_v3",
                intent="Parse JSON logs",
                success=True,
                entropy_used=0.05
            )
        """
        # Update usage metrics (parent class method)
        await self.update_usage(agent_id, success=success)

        # Add JIT metadata
        entry = self.catalog.entries.get(agent_id)
        if entry:
            # Track intents this agent has handled
            if "handled_intents" not in entry.relationships:
                entry.relationships["handled_intents"] = []
            if intent not in entry.relationships["handled_intents"]:
                entry.relationships["handled_intents"].append(intent)

            # Track entropy usage if provided
            if entropy_used is not None:
                if "entropy_history" not in entry.relationships:
                    entry.relationships["entropy_history"] = []
                entry.relationships["entropy_history"].append(str(entropy_used))


# Convenience functions


async def create_semantic_registry(
    catalog: Catalog | None = None, embedder: Embedder | None = None
) -> SemanticRegistry:
    """Create semantic registry and fit embeddings.

    Args:
        catalog: Optional existing catalog
        embedder: Optional custom embedder

    Returns:
        SemanticRegistry instance with fitted embeddings
    """
    registry = SemanticRegistry(catalog=catalog, embedder=embedder)

    if catalog and catalog.entries:
        await registry.fit()

    return registry
