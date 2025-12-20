"""
N-gent Phase 5 Integrations: D/L/M/I/B-gent.

This module provides integration points between N-gent (Narrative)
and other agent genera:

- D-gent: Crystal persistence via UnifiedMemory (already in dgent_store.py)
- L-gent: Crystal indexing via semantic embeddings
- M-gent: Crystal resonance in holographic memory
- I-gent: Narrative visualization
- B-gent: Narration budgeting

Philosophy:
    | Integration | Direction | Purpose |
    |-------------|-----------|---------|
    | Historian ← W-gent | W → N | Wire tap feeds Historian |
    | Historian → D-gent | N → D | Crystals persist via D-gent |
    | Historian → L-gent | N → L | Crystals indexed for search |
    | Historian → M-gent | N → M | Crystals resonate in memory |
    | Bard → I-gent | N → I | Stories visualized |
    | Bard → B-gent | N ↔ B | Narration budgeted |
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Protocol, runtime_checkable

from .bard import Bard, LLMProvider, Narrative, NarrativeRequest
from .store import CrystalStore
from .types import Determinism, SemanticTrace

# =============================================================================
# L-gent Integration: Crystal Indexing
# =============================================================================


@runtime_checkable
class Embedder(Protocol):
    """Protocol for embedding providers (L-gent)."""

    async def embed(self, text: str) -> list[float]:
        """Generate embedding for text."""
        ...


@runtime_checkable
class VectorIndex(Protocol):
    """Protocol for vector indices (L-gent VectorBackend)."""

    async def add(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Add embedding to index."""
        ...

    async def search(
        self,
        query: list[float],
        limit: int = 10,
    ) -> list[tuple[str, float]]:
        """Search for similar embeddings. Returns (id, score) pairs."""
        ...

    async def delete(self, id: str) -> None:
        """Remove embedding from index."""
        ...


class IndexedCrystalStore(CrystalStore):
    """
    Crystal store with L-gent semantic indexing.

    Wraps any CrystalStore and adds semantic search via embeddings.
    Crystals are indexed by their semantic content for retrieval.

    Usage:
        from agents.l import SentenceTransformerEmbedder, create_vector_backend

        base_store = MemoryCrystalStore()
        embedder = SentenceTransformerEmbedder()
        index = await create_vector_backend("chromadb")

        store = IndexedCrystalStore(base_store, embedder, index)

        # Store (automatically indexed)
        store.store(crystal)

        # Semantic search
        results = await store.search_semantic("error handling logic")
    """

    def __init__(
        self,
        base_store: CrystalStore,
        embedder: Embedder,
        index: VectorIndex,
    ):
        """
        Initialize indexed store.

        Args:
            base_store: Underlying crystal storage
            embedder: L-gent embedder for semantic indexing
            index: L-gent vector index for search
        """
        self.base = base_store
        self.embedder = embedder
        self.index = index

    def store(self, crystal: SemanticTrace) -> None:
        """Store crystal and add to semantic index."""
        # Store in base
        self.base.store(crystal)
        # Note: Index update happens async via index_crystal()

    async def store_and_index(self, crystal: SemanticTrace) -> None:
        """Store crystal and immediately index it."""
        self.base.store(crystal)
        await self.index_crystal(crystal)

    async def index_crystal(self, crystal: SemanticTrace) -> None:
        """Add crystal to semantic index."""
        # Create searchable text from crystal
        text = self._make_searchable_text(crystal)

        # Embed
        embedding = await self.embedder.embed(text)

        # Index with metadata
        metadata = {
            "agent_id": crystal.agent_id,
            "agent_genus": crystal.agent_genus,
            "action": crystal.action,
            "timestamp": crystal.timestamp.isoformat(),
        }

        await self.index.add(crystal.trace_id, embedding, metadata)

        # Note: Crystal is frozen, so we can't update it in base store.
        # The vector is available in the index for semantic search.

    async def search_semantic(
        self,
        query: str,
        limit: int = 10,
    ) -> list[tuple[SemanticTrace, float]]:
        """
        Search crystals by semantic similarity.

        Args:
            query: Natural language query
            limit: Max results

        Returns:
            List of (crystal, similarity_score) pairs
        """
        # Embed query
        query_embedding = await self.embedder.embed(query)

        # Search index
        results = await self.index.search(query_embedding, limit)

        # Fetch crystals
        crystal_results: list[tuple[SemanticTrace, float]] = []
        for trace_id, score in results:
            crystal = self.base.get(trace_id)
            if crystal:
                crystal_results.append((crystal, score))

        return crystal_results

    def _make_searchable_text(self, crystal: SemanticTrace) -> str:
        """Create searchable text from crystal."""
        parts = [
            f"Agent: {crystal.agent_id}",
            f"Action: {crystal.action}",
        ]

        if crystal.inputs:
            inputs_str = " ".join(f"{k}={v}" for k, v in crystal.inputs.items())
            parts.append(f"Inputs: {inputs_str}")

        if crystal.outputs:
            outputs_str = " ".join(f"{k}={v}" for k, v in crystal.outputs.items())
            parts.append(f"Outputs: {outputs_str}")

        return " | ".join(parts)

    # Delegate remaining methods to base store
    def get(self, trace_id: str) -> SemanticTrace | None:
        return self.base.get(trace_id)

    def query(
        self,
        agent_id: str | None = None,
        agent_genus: str | None = None,
        action: str | None = None,
        determinism: Determinism | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[SemanticTrace]:
        return self.base.query(
            agent_id=agent_id,
            agent_genus=agent_genus,
            action=action,
            determinism=determinism,
            start_time=start_time,
            end_time=end_time,
            limit=limit,
            offset=offset,
        )

    def get_children(self, trace_id: str) -> list[SemanticTrace]:
        return self.base.get_children(trace_id)

    def count(self) -> int:
        return self.base.count()


# =============================================================================
# M-gent Integration: Crystal Resonance
# =============================================================================


@runtime_checkable
class HolographicMemoryProtocol(Protocol):
    """Protocol for M-gent HolographicMemory."""

    async def store(self, pattern: Any) -> None:
        """Store a pattern in holographic memory."""
        ...

    async def resonate(self, query: Any, threshold: float = 0.5) -> Any:
        """Find resonating patterns."""
        ...


@dataclass
class CrystalMemoryPattern:
    """
    A crystal encoded as a memory pattern for M-gent.

    Crystals become patterns that can resonate with queries
    in the holographic memory field.
    """

    trace_id: str
    agent_id: str
    action: str
    vector: list[float]
    timestamp: datetime
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_crystal(
        cls,
        crystal: SemanticTrace,
        vector: list[float] | None = None,
    ) -> CrystalMemoryPattern:
        """Create memory pattern from crystal."""
        return cls(
            trace_id=crystal.trace_id,
            agent_id=crystal.agent_id,
            action=crystal.action,
            vector=vector or list(crystal.vector or []),
            timestamp=crystal.timestamp,
            metadata={
                "inputs": crystal.inputs,
                "outputs": crystal.outputs,
                "determinism": crystal.determinism.value,
            },
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert to dict for storage."""
        return {
            "trace_id": self.trace_id,
            "agent_id": self.agent_id,
            "action": self.action,
            "vector": self.vector,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
        }


class ResonantCrystalStore:
    """
    Crystal store that resonates with M-gent holographic memory.

    Crystals stored here create "echoes" in holographic memory
    that can be recalled via associative queries.

    Usage:
        from agents.m import create_holographic_memory

        base_store = MemoryCrystalStore()
        memory = create_holographic_memory()

        store = ResonantCrystalStore(base_store, memory, embedder)

        # Store (creates memory pattern)
        await store.store(crystal)

        # Recall via resonance
        patterns = await store.resonate_query("debugging session")
    """

    def __init__(
        self,
        base_store: CrystalStore,
        memory: HolographicMemoryProtocol,
        embedder: Embedder | None = None,
    ):
        """
        Initialize resonant store.

        Args:
            base_store: Underlying crystal storage
            memory: M-gent holographic memory
            embedder: Optional embedder for query vectors
        """
        self.base = base_store
        self.memory = memory
        self.embedder = embedder
        self._pattern_cache: dict[str, CrystalMemoryPattern] = {}

    async def store(self, crystal: SemanticTrace) -> None:
        """Store crystal and create memory pattern."""
        # Store in base
        self.base.store(crystal)

        # Create memory pattern
        vector = list(crystal.vector) if crystal.vector else []
        if not vector and self.embedder:
            # Generate embedding if not present
            text = f"{crystal.agent_id} {crystal.action} {crystal.inputs}"
            vector = await self.embedder.embed(text)

        pattern = CrystalMemoryPattern.from_crystal(crystal, vector)
        self._pattern_cache[crystal.trace_id] = pattern

        # Store in holographic memory
        await self.memory.store(pattern)

    async def resonate_query(
        self,
        query: str,
        threshold: float = 0.5,
    ) -> list[CrystalMemoryPattern]:
        """
        Find crystals that resonate with a query.

        Uses M-gent's holographic resonance for associative recall.
        """
        if self.embedder:
            query_vector = await self.embedder.embed(query)
            query_pattern = CrystalMemoryPattern(
                trace_id="query",
                agent_id="user",
                action="QUERY",
                vector=query_vector,
                timestamp=datetime.now(timezone.utc),
            )
        else:
            # Text-based query - use a proper pattern with empty vector
            query_pattern = CrystalMemoryPattern(
                trace_id="query",
                agent_id="user",
                action="QUERY",
                vector=[],
                timestamp=datetime.now(timezone.utc),
                metadata={"query": query},
            )

        result = await self.memory.resonate(query_pattern, threshold)

        # Extract patterns from result
        if isinstance(result, list):
            return result
        return []

    def get(self, trace_id: str) -> SemanticTrace | None:
        """Get crystal by ID."""
        return self.base.get(trace_id)

    def get_pattern(self, trace_id: str) -> CrystalMemoryPattern | None:
        """Get the memory pattern for a crystal."""
        return self._pattern_cache.get(trace_id)


# =============================================================================
# I-gent Integration: Narrative Visualization
# =============================================================================


@dataclass
class NarrativeVisualization:
    """
    Visualization data for a narrative.

    Provides structured data for I-gent TUI rendering.
    """

    narrative: Narrative
    timeline_events: list[dict[str, Any]]
    agent_swimlanes: dict[str, list[dict[str, Any]]]
    interaction_graph: dict[str, list[str]]
    summary_stats: dict[str, Any]

    def to_timeline_data(self) -> list[dict[str, Any]]:
        """Format for timeline visualization."""
        return self.timeline_events

    def to_swimlane_data(self) -> dict[str, Any]:
        """Format for swimlane visualization."""
        return {
            "agents": list(self.agent_swimlanes.keys()),
            "lanes": self.agent_swimlanes,
        }

    def to_graph_data(self) -> dict[str, Any]:
        """Format for graph visualization."""
        nodes = list(self.interaction_graph.keys())
        edges = []
        for from_agent, to_agents in self.interaction_graph.items():
            for to_agent in to_agents:
                edges.append({"from": from_agent, "to": to_agent})
        return {"nodes": nodes, "edges": edges}


class VisualizableBard(Bard):
    """
    Bard with I-gent visualization support.

    Extends Bard to produce visualization data alongside narratives.

    Usage:
        bard = VisualizableBard(llm)
        result = await bard.invoke_with_viz(request)

        # Use in I-gent TUI
        timeline_data = result.to_timeline_data()
    """

    async def invoke_with_viz(
        self,
        request: NarrativeRequest,
    ) -> NarrativeVisualization:
        """
        Generate narrative with visualization data.
        """
        # Generate narrative
        narrative = await self.invoke(request)

        # Build visualization data
        traces = request.filtered_traces()

        # Timeline events
        timeline_events = [
            {
                "timestamp": t.timestamp.isoformat(),
                "agent": t.agent_id,
                "action": t.action,
                "duration_ms": t.duration_ms,
                "is_error": t.action == "ERROR",
            }
            for t in traces
        ]

        # Agent swimlanes
        agent_swimlanes: dict[str, list[dict[str, Any]]] = {}
        for t in traces:
            if t.agent_id not in agent_swimlanes:
                agent_swimlanes[t.agent_id] = []
            agent_swimlanes[t.agent_id].append(
                {
                    "trace_id": t.trace_id,
                    "action": t.action,
                    "timestamp": t.timestamp.isoformat(),
                    "duration_ms": t.duration_ms,
                }
            )

        # Interaction graph (based on parent-child relationships)
        interaction_graph: dict[str, list[str]] = {}
        for t in traces:
            if t.agent_id not in interaction_graph:
                interaction_graph[t.agent_id] = []

            # Find children to build edges
            for other in traces:
                if other.parent_id == t.trace_id and other.agent_id != t.agent_id:
                    if other.agent_id not in interaction_graph[t.agent_id]:
                        interaction_graph[t.agent_id].append(other.agent_id)

        # Summary stats
        summary_stats = {
            "total_traces": len(traces),
            "unique_agents": len(agent_swimlanes),
            "total_duration_ms": sum(t.duration_ms for t in traces),
            "total_gas": sum(t.gas_consumed for t in traces),
            "error_count": sum(1 for t in traces if t.action == "ERROR"),
            "chapters": len(narrative.chapters),
        }

        return NarrativeVisualization(
            narrative=narrative,
            timeline_events=timeline_events,
            agent_swimlanes=agent_swimlanes,
            interaction_graph=interaction_graph,
            summary_stats=summary_stats,
        )


# =============================================================================
# B-gent Integration: Narration Budgeting
# =============================================================================


@runtime_checkable
class TokenBudget(Protocol):
    """Protocol for B-gent token budget."""

    def can_afford(self, tokens: int) -> bool:
        """Check if budget can afford tokens."""
        ...

    def consume(self, tokens: int) -> bool:
        """Consume tokens from budget."""
        ...

    @property
    def available(self) -> int:
        """Get available tokens."""
        ...


@dataclass
class NarrationCost:
    """Cost breakdown for a narration request."""

    estimated_input_tokens: int
    estimated_output_tokens: int
    total_estimated: int
    actual_tokens: int | None = None

    @property
    def estimate(self) -> int:
        return self.total_estimated

    def with_actual(self, actual: int) -> NarrationCost:
        """Return new cost with actual tokens filled in."""
        return NarrationCost(
            estimated_input_tokens=self.estimated_input_tokens,
            estimated_output_tokens=self.estimated_output_tokens,
            total_estimated=self.total_estimated,
            actual_tokens=actual,
        )


class BudgetedBard(Bard):
    """
    Bard with B-gent token budgeting.

    Checks token budget before narration and tracks actual consumption.

    Usage:
        from agents.b import TokenBucket

        budget = TokenBucket(max_balance=10000, initial=5000)
        bard = BudgetedBard(llm, budget)

        # Check if can afford
        cost = bard.estimate_cost(request)
        if budget.can_afford(cost.estimate):
            narrative = await bard.invoke(request)
    """

    def __init__(
        self,
        llm: LLMProvider | None = None,
        budget: TokenBudget | None = None,
        tokens_per_trace: int = 50,
        tokens_per_output_word: int = 2,
    ):
        """
        Initialize budgeted Bard.

        Args:
            llm: LLM provider
            budget: Token budget to use
            tokens_per_trace: Estimated tokens per trace in prompt
            tokens_per_output_word: Estimated tokens per output word
        """
        super().__init__(llm)
        self.budget = budget
        self.tokens_per_trace = tokens_per_trace
        self.tokens_per_output_word = tokens_per_output_word

    def estimate_cost(self, request: NarrativeRequest) -> NarrationCost:
        """
        Estimate token cost for a narration request.
        """
        traces = request.filtered_traces()

        # Input cost: prompt + traces
        base_prompt_tokens = 200  # System prompt
        trace_tokens = len(traces) * self.tokens_per_trace
        input_tokens = base_prompt_tokens + trace_tokens

        # Output cost: depends on verbosity and genre
        verbosity_multiplier = {
            "terse": 0.5,
            "normal": 1.0,
            "verbose": 2.0,
        }.get(request.verbosity.value, 1.0)

        # Estimate ~50 words per trace for normal verbosity
        words_per_trace = 50
        estimated_words = int(len(traces) * words_per_trace * verbosity_multiplier)
        output_tokens = estimated_words * self.tokens_per_output_word

        return NarrationCost(
            estimated_input_tokens=input_tokens,
            estimated_output_tokens=output_tokens,
            total_estimated=input_tokens + output_tokens,
        )

    async def invoke(self, request: NarrativeRequest) -> Narrative:
        """
        Generate narrative with budget checking.

        Raises:
            InsufficientBudgetError: If budget cannot afford narration
        """
        cost = self.estimate_cost(request)

        # Check budget
        if self.budget and not self.budget.can_afford(cost.estimate):
            raise InsufficientBudgetError(
                f"Insufficient budget: need {cost.estimate}, have {self.budget.available}"
            )

        # Consume estimated tokens
        if self.budget:
            self.budget.consume(cost.estimate)

        # Generate narrative
        narrative = await super().invoke(request)

        # Track actual consumption in metadata
        narrative.metadata["budget"] = {
            "estimated": cost.estimate,
            "input_tokens": cost.estimated_input_tokens,
            "output_tokens": cost.estimated_output_tokens,
        }

        return narrative

    async def invoke_if_affordable(
        self,
        request: NarrativeRequest,
    ) -> Narrative | None:
        """
        Generate narrative only if affordable.

        Returns None if budget insufficient instead of raising.
        """
        cost = self.estimate_cost(request)

        if self.budget and not self.budget.can_afford(cost.estimate):
            return None

        return await self.invoke(request)


class InsufficientBudgetError(Exception):
    """Raised when budget is insufficient for narration."""

    pass


# =============================================================================
# Unified Integration: NarrativeOrchestrator
# =============================================================================


class NarrativeOrchestrator:
    """
    Orchestrates all N-gent integrations.

    Provides a single interface for:
    - Storing crystals (with D/L/M-gent integration)
    - Generating narratives (with I/B-gent integration)
    - Searching and resonating

    Usage:
        orchestrator = NarrativeOrchestrator(
            store=indexed_store,
            bard=budgeted_bard,
            memory=holographic_memory,
        )

        # Full pipeline
        await orchestrator.record_and_narrate(traces, genre=NarrativeGenre.NOIR)
    """

    def __init__(
        self,
        store: CrystalStore,
        bard: Bard | None = None,
        memory: HolographicMemoryProtocol | None = None,
        embedder: Embedder | None = None,
        budget: TokenBudget | None = None,
    ):
        """
        Initialize orchestrator.

        Args:
            store: Crystal store (may be indexed or resonant)
            bard: Bard for narration (defaults to BudgetedBard if budget provided)
            memory: Optional M-gent holographic memory
            embedder: Optional L-gent embedder
            budget: Optional B-gent token budget
        """
        self.store = store
        self.memory = memory
        self.embedder = embedder

        if bard:
            self.bard = bard
        elif budget:
            self.bard = BudgetedBard(budget=budget)
        else:
            self.bard = Bard()

    async def record(self, crystal: SemanticTrace) -> None:
        """
        Record a crystal with all integrations.

        - Stores in crystal store
        - Indexes via L-gent (if available)
        - Creates memory pattern in M-gent (if available)
        """
        # Store
        if hasattr(self.store, "store_and_index"):
            await self.store.store_and_index(crystal)
        else:
            self.store.store(crystal)

        # Create memory pattern
        if self.memory and self.embedder:
            vector = list(crystal.vector) if crystal.vector else []
            if not vector:
                text = f"{crystal.agent_id} {crystal.action}"
                vector = await self.embedder.embed(text)

            pattern = CrystalMemoryPattern.from_crystal(crystal, vector)
            await self.memory.store(pattern)

    async def record_many(self, crystals: list[SemanticTrace]) -> None:
        """Record multiple crystals."""
        for crystal in crystals:
            await self.record(crystal)

    async def narrate(
        self,
        traces: list[SemanticTrace] | None = None,
        query: str | None = None,
        **kwargs: Any,
    ) -> Narrative:
        """
        Generate a narrative from traces or a query.

        Args:
            traces: Specific traces to narrate
            query: If no traces, search for relevant ones
            **kwargs: Passed to NarrativeRequest

        Returns:
            Generated Narrative
        """
        if not traces and query:
            # Search for relevant traces
            if hasattr(self.store, "search_semantic"):
                results = await self.store.search_semantic(query, limit=50)
                traces = [t for t, _ in results]
            else:
                # Fall back to recent traces
                traces = self.store.query(limit=50)

        if not traces:
            traces = []

        request = NarrativeRequest(traces=traces, **kwargs)

        if isinstance(self.bard, VisualizableBard):
            viz = await self.bard.invoke_with_viz(request)
            return viz.narrative

        return await self.bard.invoke(request)

    async def search(
        self,
        query: str,
        limit: int = 10,
    ) -> list[SemanticTrace]:
        """
        Search crystals semantically.
        """
        if hasattr(self.store, "search_semantic"):
            results = await self.store.search_semantic(query, limit)
            return [t for t, _ in results]
        return []

    async def resonate(
        self,
        query: str,
        threshold: float = 0.5,
    ) -> list[CrystalMemoryPattern]:
        """
        Find resonating patterns in holographic memory.
        """
        if hasattr(self.store, "resonate_query"):
            result: list[CrystalMemoryPattern] = await self.store.resonate_query(query, threshold)
            return result
        return []

    def get_stats(self) -> dict[str, Any]:
        """Get orchestrator statistics."""
        return {
            "crystal_count": self.store.count(),
            "has_memory": self.memory is not None,
            "has_embedder": self.embedder is not None,
            "bard_type": type(self.bard).__name__,
        }
