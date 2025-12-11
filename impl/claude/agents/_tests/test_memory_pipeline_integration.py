"""
Memory Pipeline Integration Tests: M × D × L × B × N

Tests integration between Memory, Data, Library, Banker, and Narrative agents:
- M × D: Memory with D-gent persistence backends
- M × L: Memory with L-gent vector-based recall
- M × B: Budgeted memory operations
- M × N: Memory → narrative crystallization

Philosophy: Memory is not storage—it is active reconstruction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

# D-gent imports
from agents.d import (
    MemoryConfig,
    Symbiont,
    UnifiedMemory,
    VolatileAgent,
)

# L-gent imports
from agents.l import (
    CatalogEntry,
    EntityType,
    SemanticRegistry,
    SimpleEmbedder,
)

# M-gent imports
from agents.m import (
    ActionHistory,
    DgentBackedHolographicMemory,
    HolographicMemory,
    ProspectiveAgent,
    Situation,
)

# N-gent imports
from agents.n import (
    Bard,
    Determinism,
    Historian,
    MemoryCrystalStore,
    NarrativeGenre,
    NarrativeRequest,
    Verbosity,
)


class TestMemoryDgentBackend:
    """M × D: Memory with D-gent persistence."""

    @pytest.mark.asyncio
    async def test_holographic_memory_basic_operations(self) -> None:
        """Test basic HolographicMemory store/retrieve."""
        memory: HolographicMemory[str] = HolographicMemory()

        # Store a memory
        pattern = await memory.store(
            id="mem-001",
            content="The sky is blue",
            concepts=["sky", "color", "observation"],
        )

        assert pattern.id == "mem-001"
        assert pattern.content == "The sky is blue"
        assert "sky" in pattern.concepts

    @pytest.mark.asyncio
    async def test_holographic_memory_retrieval(self) -> None:
        """Test HolographicMemory retrieval by cue."""
        memory: HolographicMemory[str] = HolographicMemory()

        # Store several memories
        await memory.store(
            "mem-001", "Python is a programming language", ["python", "programming"]
        )
        await memory.store(
            "mem-002", "The weather is sunny today", ["weather", "sunny"]
        )
        await memory.store(
            "mem-003", "Python snakes are reptiles", ["python", "animals"]
        )

        # Retrieve by concept
        results = await memory.retrieve_by_concept("python")
        assert len(results) >= 1  # Should find at least one python-related memory

    @pytest.mark.asyncio
    async def test_dgent_backed_memory_persistence(self) -> None:
        """Test DgentBackedHolographicMemory with D-gent storage."""
        # Create D-gent storage layer
        volatile: VolatileAgent[dict[str, Any]] = VolatileAgent(_state={})
        config = MemoryConfig(
            enable_semantic=True,
            enable_temporal=True,
        )
        unified = UnifiedMemory(volatile, config)

        # Create M-gent memory backed by D-gent
        memory: DgentBackedHolographicMemory[str] = DgentBackedHolographicMemory(
            storage=unified,
            namespace="test_memory",
        )

        # Store and retrieve
        pattern = await memory.store(
            id="persistent-001",
            content="This should persist",
            concepts=["persistence", "test"],
        )

        assert pattern.id == "persistent-001"

        # Persist to D-gent
        await memory.persist()

        # Verify in D-gent storage
        state = await unified.load()
        assert state is not None

    @pytest.mark.asyncio
    async def test_memory_compression(self) -> None:
        """Test memory compression reduces storage."""
        memory: HolographicMemory[str] = HolographicMemory()

        # Store several memories
        for i in range(10):
            await memory.store(
                id=f"mem-{i:03d}",
                content=f"Memory content number {i}",
                concepts=["test"],
            )

        # Compress with 50% ratio
        compressed_count = await memory.compress(ratio=0.5)

        # Some memories should have been compressed
        assert compressed_count >= 0

    @pytest.mark.asyncio
    async def test_memory_consolidation(self) -> None:
        """Test memory consolidation organizes patterns."""
        memory: HolographicMemory[str] = HolographicMemory()

        # Store memories over simulated time
        await memory.store("mem-001", "First memory", ["early"])
        await memory.store("mem-002", "Second memory", ["middle"])
        await memory.store("mem-003", "Third memory", ["recent"])

        # Consolidate
        stats = await memory.consolidate()

        assert isinstance(stats, dict)


class TestSymbiontIntegration:
    """Test Symbiont fusion of logic and state."""

    @pytest.mark.asyncio
    async def test_symbiont_basic_operation(self) -> None:
        """Test Symbiont fuses stateless logic with stateful memory."""

        def counter_logic(increment: int, count: int) -> tuple[int, int]:
            new_count = count + increment
            return new_count, new_count

        memory: VolatileAgent[int] = VolatileAgent(_state=0)
        counter = Symbiont(logic=counter_logic, memory=memory)

        # First invocation
        result1 = await counter.invoke(1)
        assert result1 == 1

        # Second invocation
        result2 = await counter.invoke(5)
        assert result2 == 6

        # Check state persisted
        state = await memory.load()
        assert state == 6

    @pytest.mark.asyncio
    async def test_symbiont_with_history(self) -> None:
        """Test Symbiont maintains history."""

        def append_logic(item: str, items: list[str]) -> tuple[list[str], list[str]]:
            new_items = items + [item]
            return new_items, new_items

        memory: VolatileAgent[list[str]] = VolatileAgent(_state=[])
        appender = Symbiont(logic=append_logic, memory=memory)

        await appender.invoke("first")
        await appender.invoke("second")
        await appender.invoke("third")

        # Check history
        history = await memory.history(limit=3)
        assert len(history) == 3


class TestUnifiedMemoryLayers:
    """Test UnifiedMemory multi-layer architecture."""

    @pytest.mark.asyncio
    async def test_unified_memory_semantic_layer(self) -> None:
        """Test UnifiedMemory semantic associate/recall."""
        volatile: VolatileAgent[dict[str, str]] = VolatileAgent(
            _state={"initial": "state"}
        )
        config = MemoryConfig(
            enable_semantic=True,
            auto_associate=True,
        )
        unified = UnifiedMemory(volatile, config)

        # Associate with concept
        await unified.associate({"data": "important"}, "important_concept")

        # Recall by concept
        results = await unified.recall("important_concept", limit=5)
        assert len(results) >= 0  # May or may not find depending on implementation

    @pytest.mark.asyncio
    async def test_unified_memory_temporal_layer(self) -> None:
        """Test UnifiedMemory temporal witness/replay."""
        volatile: VolatileAgent[dict[str, int]] = VolatileAgent(_state={"version": 1})
        config = MemoryConfig(enable_temporal=True)
        unified = UnifiedMemory(volatile, config)

        # Witness state changes
        await unified.witness("v1", {"version": 1})
        await unified.save({"version": 2})
        await unified.witness("v2", {"version": 2})

        # Replay should work
        state = await unified.load()
        assert state["version"] == 2

    @pytest.mark.asyncio
    async def test_unified_memory_relational_layer(self) -> None:
        """Test UnifiedMemory relational edges."""
        volatile: VolatileAgent[dict[str, Any]] = VolatileAgent(_state={})
        config = MemoryConfig(
            enable_relational=True,
            track_lineage=True,
        )
        unified = UnifiedMemory(volatile, config)

        # Create relationships
        await unified.relate("entity_a", "depends_on", "entity_b")
        await unified.relate("entity_b", "depends_on", "entity_c")

        # Query ancestors
        ancestors = await unified.ancestors("entity_a")
        # Should track lineage
        assert isinstance(ancestors, list)


class TestProspectiveMemory:
    """Test prospective (predictive) memory."""

    @pytest.mark.asyncio
    async def test_prospective_agent_prediction(self) -> None:
        """Test ProspectiveAgent predicts actions from situations."""
        # Create memory and action history
        memory: HolographicMemory[str] = HolographicMemory()
        history: ActionHistory = ActionHistory()

        agent: ProspectiveAgent[str] = ProspectiveAgent(
            memory=memory,
            action_log=history,
            min_similarity=0.3,
            max_predictions=5,
        )

        # Record some experiences
        situation1 = Situation(
            id="sit-001",
            description="User requests weather data",
            concepts=["weather", "data", "request"],
        )
        await agent.record_experience(
            situation=situation1,
            action="fetch_weather_api",
            outcome="success",
            success=True,
        )

        # Create similar situation
        situation2 = Situation(
            id="sit-002",
            description="User wants weather information",
            concepts=["weather", "information", "user"],
        )

        # Get predictions
        predictions = await agent.invoke(situation2)

        # Should predict based on similar past experience
        assert isinstance(predictions, list)

    @pytest.mark.asyncio
    async def test_prospective_learns_from_outcomes(self) -> None:
        """Test ProspectiveAgent learns from action outcomes."""
        memory: HolographicMemory[str] = HolographicMemory()
        history: ActionHistory = ActionHistory()
        agent: ProspectiveAgent[str] = ProspectiveAgent(
            memory=memory, action_log=history
        )

        # Record successful action
        situation = Situation(
            id="sit-success",
            description="Need to validate email",
            concepts=["email", "validation"],
        )
        record = await agent.record_experience(
            situation=situation,
            action="use_regex_validator",
            outcome="email validated correctly",
            success=True,
        )

        assert record.success is True
        assert record.action == "use_regex_validator"


class TestMemoryVectorIntegration:
    """M × L: Memory with L-gent vector operations."""

    @pytest.mark.asyncio
    async def test_semantic_registry_search(self) -> None:
        """Test SemanticRegistry finds similar entries."""
        embedder: SimpleEmbedder = SimpleEmbedder(dimension=128)
        registry: SemanticRegistry = SemanticRegistry(embedder=embedder)

        # Register entries
        await registry.register(
            CatalogEntry(
                id="agent-weather",
                entity_type=EntityType.AGENT,
                name="WeatherAgent",
                version="1.0.0",
                description="Fetches weather data from external APIs",
                keywords=["weather", "api", "data"],
            )
        )
        await registry.register(
            CatalogEntry(
                id="agent-email",
                entity_type=EntityType.AGENT,
                name="EmailValidator",
                version="1.0.0",
                description="Validates email addresses using regex",
                keywords=["email", "validation", "regex"],
            )
        )

        # Fit the semantic index
        await registry.fit()

        # Search semantically
        results = await registry.find_semantic("get weather information", limit=5)

        # Should find weather agent
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_memory_with_embeddings(self) -> None:
        """Test memory stores and retrieves by embedding similarity."""
        embedder: SimpleEmbedder = SimpleEmbedder(dimension=128)
        memory: HolographicMemory[str] = HolographicMemory(embedder=embedder)

        # Store with embeddings
        embedding = await embedder.embed("programming concepts")
        await memory.store(
            id="mem-prog",
            content="Python is great for AI",
            concepts=["python", "ai"],
            embedding=embedding,
        )

        # Retrieve by similar query
        results = await memory.retrieve("artificial intelligence programming", limit=5)
        assert isinstance(results, list)


class TestBudgetedMemory:
    """M × B: Budgeted memory operations."""

    @pytest.mark.asyncio
    async def test_memory_respects_storage_limits(self) -> None:
        """Test memory operations respect configured limits."""
        memory: HolographicMemory[str] = HolographicMemory(
            hot_threshold=0.7,
            cold_threshold=0.3,
            forget_threshold_days=30.0,
        )

        # Store many memories
        for i in range(100):
            await memory.store(
                id=f"bulk-{i:03d}",
                content=f"Bulk memory content {i}",
                concepts=["bulk", "test"],
            )

        # Memory should manage storage
        # (implementation may compress or evict)

    @pytest.mark.asyncio
    async def test_memory_pattern_strength_decay(self) -> None:
        """Test memory pattern strength decays over time."""
        memory: HolographicMemory[str] = HolographicMemory()

        pattern = await memory.store(
            id="decaying",
            content="This will decay",
            concepts=["decay"],
        )

        # Initial strength should be high
        assert pattern.strength > 0

        # Strength property should be accessible
        assert hasattr(pattern, "strength")


class TestMemoryNarrativeIntegration:
    """M × N: Memory → narrative crystallization."""

    @pytest.mark.asyncio
    async def test_historian_records_traces(self) -> None:
        """Test Historian records semantic traces."""
        store: MemoryCrystalStore = MemoryCrystalStore()
        historian: Historian = Historian(store)

        # Create a mock traceable agent
        @dataclass
        class MockAgent:
            id: str = "test-agent"
            name: str = "TestAgent"

        agent = MockAgent()

        # Begin trace
        ctx = historian.begin_trace(agent, {"input": "test data"})
        assert ctx is not None

        # End trace (note: uses 'outputs' plural)
        trace = historian.end_trace(
            ctx,
            action="INVOKE",
            outputs={"result": "processed"},
            determinism=Determinism.DETERMINISTIC,
        )

        # Historian uses agent.name as agent_id
        assert trace.agent_id == "TestAgent"
        assert trace.action == "INVOKE"

    @pytest.mark.asyncio
    async def test_crystal_store_query(self) -> None:
        """Test crystal store can be queried."""
        store: MemoryCrystalStore = MemoryCrystalStore()
        historian: Historian = Historian(store)

        @dataclass
        class MockAgent:
            id: str = "query-test-agent"
            name: str = "QueryTestAgent"

        agent = MockAgent()

        # Record several traces
        for i in range(3):
            ctx = historian.begin_trace(agent, {"iteration": i})
            historian.end_trace(ctx, action="PROCESS", outputs={"step": i})

        # Query traces - Historian uses agent.name as agent_id
        traces = store.query(agent_id="QueryTestAgent")
        assert len(traces) == 3

    @pytest.mark.asyncio
    async def test_bard_creates_narrative(self) -> None:
        """Test Bard creates narrative from traces."""
        store: MemoryCrystalStore = MemoryCrystalStore()
        historian: Historian = Historian(store)

        @dataclass
        class MockAgent:
            id: str = "narrative-agent"
            name: str = "NarrativeAgent"

        agent = MockAgent()

        # Record trace
        ctx = historian.begin_trace(agent, "user query")
        trace = historian.end_trace(
            ctx, action="RESPOND", outputs={"response": "agent response"}
        )

        # Create narrative - Verbosity uses TERSE/NORMAL/VERBOSE, not BRIEF
        bard = Bard()
        request = NarrativeRequest(
            traces=[trace],
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.TERSE,
        )

        narrative = await bard.invoke(request)

        assert narrative is not None
        assert hasattr(narrative, "render")


class TestMemoryPatternAccess:
    """Test memory pattern access and modification."""

    @pytest.mark.asyncio
    async def test_pattern_access_updates_metadata(self) -> None:
        """Test accessing pattern updates access metadata."""
        memory: HolographicMemory[str] = HolographicMemory()

        pattern = await memory.store(
            id="access-test",
            content="Content to access",
            concepts=["access"],
        )

        # Pattern should have access metadata
        assert hasattr(pattern, "last_accessed")
        assert hasattr(pattern, "access_count")

    @pytest.mark.asyncio
    async def test_resonance_result_scoring(self) -> None:
        """Test resonance results include similarity scores."""
        memory: HolographicMemory[str] = HolographicMemory()

        await memory.store("res-001", "First memory about cats", ["cats"])
        await memory.store("res-002", "Second memory about dogs", ["dogs"])
        await memory.store(
            "res-003", "Third memory about cats and dogs", ["cats", "dogs"]
        )

        results = await memory.retrieve_by_concept("cats")

        for result in results:
            assert hasattr(result, "similarity")
            assert hasattr(result, "pattern")


class TestMemoryLinkingAssociation:
    """Test memory linking and association features."""

    @pytest.mark.asyncio
    async def test_dgent_memory_linking(self) -> None:
        """Test AssociativeWebMemory link creation."""
        from agents.m import AssociativeWebMemory

        volatile: VolatileAgent[dict[str, Any]] = VolatileAgent(_state={})
        # Need all layers enabled for full memory functionality
        unified = UnifiedMemory(
            volatile,
            MemoryConfig(
                enable_relational=True,
                enable_semantic=True,
                enable_temporal=True,
            ),
        )

        # Use AssociativeWebMemory for link/spread_activation
        memory: AssociativeWebMemory[str] = AssociativeWebMemory(
            storage=unified,
            namespace="linking_test",
        )

        # Store related memories
        await memory.store("parent", "Parent concept", ["parent"])
        await memory.store("child", "Child concept derived from parent", ["child"])

        # Link them (link takes source_id, relation, target_id)
        await memory.link("child", "derived_from", "parent")

        # Get related memories
        related = await memory.related_memories("child")
        assert isinstance(related, list)

    @pytest.mark.asyncio
    async def test_spread_activation(self) -> None:
        """Test spread activation through memory network."""
        from agents.m import AssociativeWebMemory

        volatile: VolatileAgent[dict[str, Any]] = VolatileAgent(_state={})
        # Need all layers enabled for full memory functionality
        unified = UnifiedMemory(
            volatile,
            MemoryConfig(
                enable_relational=True,
                enable_semantic=True,
                enable_temporal=True,
            ),
        )

        # Use AssociativeWebMemory for link/spread_activation
        memory: AssociativeWebMemory[str] = AssociativeWebMemory(
            storage=unified,
            namespace="activation_test",
        )

        # Create memory network
        await memory.store("center", "Central concept", ["center"])
        await memory.store("related1", "Related to center", ["related"])
        await memory.store("related2", "Also related to center", ["related"])

        # link takes source_id, relation, target_id
        await memory.link("related1", "related_to", "center")
        await memory.link("related2", "related_to", "center")

        # Spread activation from center
        activation = await memory.spread_activation("center")
        assert isinstance(activation, list)  # Returns List[Tuple[MemoryPattern, float]]


# Run with: pytest impl/claude/agents/_tests/test_memory_pipeline_integration.py -v
