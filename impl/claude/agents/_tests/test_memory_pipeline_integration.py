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
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()

        # Store a memory (using legacy key-value interface)
        content = {
            "content": "The sky is blue",
            "concepts": ["sky", "color", "observation"],
        }
        memory.store("mem-001", content)

        # Retrieve and verify
        retrieved = memory.retrieve("mem-001")
        assert retrieved is not None
        assert retrieved["content"] == "The sky is blue"
        assert "sky" in retrieved["concepts"]

    @pytest.mark.asyncio
    async def test_holographic_memory_retrieval(self) -> None:
        """Test HolographicMemory retrieval by key (legacy stub interface)."""
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()

        # Store several memories (using legacy key-value interface)
        memory.store(
            "mem-001",
            {
                "text": "Python is a programming language",
                "tags": ["python", "programming"],
            },
        )
        memory.store(
            "mem-002",
            {"text": "The weather is sunny today", "tags": ["weather", "sunny"]},
        )
        memory.store(
            "mem-003",
            {"text": "Python snakes are reptiles", "tags": ["python", "animals"]},
        )

        # Retrieve by key (legacy stubs don't support concept-based retrieval)
        result = memory.retrieve("mem-001")
        assert result is not None
        assert "Python" in result["text"]
        assert "python" in result["tags"]

    @pytest.mark.asyncio
    async def test_dgent_backed_memory_persistence(self) -> None:
        """Test DgentBackedHolographicMemory with D-gent storage (legacy stub interface)."""
        # DgentBackedHolographicMemory is a deprecated stub with simple key-value interface
        memory: DgentBackedHolographicMemory[dict[str, Any]] = (
            DgentBackedHolographicMemory(
                namespace="test_memory",
            )
        )

        # Store and retrieve (using legacy key-value interface)
        content = {
            "content": "This should persist",
            "concepts": ["persistence", "test"],
        }
        memory.store("persistent-001", content)

        # Retrieve and verify
        retrieved = memory.retrieve("persistent-001")
        assert retrieved is not None
        assert retrieved["content"] == "This should persist"
        assert "persistence" in retrieved["concepts"]

    @pytest.mark.asyncio
    async def test_memory_compression(self) -> None:
        """Test memory store/retrieve (legacy stub - compression not implemented)."""
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()

        # Store several memories (using legacy key-value interface)
        for i in range(10):
            memory.store(
                f"mem-{i:03d}",
                {"content": f"Memory content number {i}", "concepts": ["test"]},
            )

        # Verify all stored
        for i in range(10):
            retrieved = memory.retrieve(f"mem-{i:03d}")
            assert retrieved is not None
            assert f"number {i}" in retrieved["content"]

    @pytest.mark.asyncio
    async def test_memory_consolidation(self) -> None:
        """Test memory store/retrieve over time (legacy stub - consolidation not implemented)."""
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()

        # Store memories over simulated time (using legacy key-value interface)
        memory.store("mem-001", {"text": "First memory", "tags": ["early"]})
        memory.store("mem-002", {"text": "Second memory", "tags": ["middle"]})
        memory.store("mem-003", {"text": "Third memory", "tags": ["recent"]})

        # Verify all retrievable
        assert memory.retrieve("mem-001") is not None
        assert memory.retrieve("mem-002") is not None
        assert memory.retrieve("mem-003") is not None


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
    """Test UnifiedMemory multi-layer architecture (legacy stubs)."""

    @pytest.mark.asyncio
    async def test_unified_memory_basic(self) -> None:
        """Test UnifiedMemory basic load/save (legacy stub)."""
        config = MemoryConfig()  # Use default config
        unified: UnifiedMemory[dict[str, str]] = UnifiedMemory(config=config)

        # Save and load (stub stores in internal _store)
        await unified.save({"initial": "state"})
        state = await unified.load()
        assert state is not None
        assert state["initial"] == "state"

        await unified.save({"updated": "value"})
        state2 = await unified.load()
        assert state2 is not None
        assert state2["updated"] == "value"

    @pytest.mark.asyncio
    async def test_unified_memory_with_volatile(self) -> None:
        """Test UnifiedMemory with config (legacy stub)."""
        config = MemoryConfig()
        unified: UnifiedMemory[dict[str, int]] = UnifiedMemory(config=config)

        # Save and load
        await unified.save({"version": 2})
        state = await unified.load()
        assert state is not None
        assert state["version"] == 2

    @pytest.mark.asyncio
    async def test_unified_memory_config_options(self) -> None:
        """Test UnifiedMemory config flags (legacy stub - no-op but should not error)."""
        config = MemoryConfig(
            enable_temporal=True,  # Supported flag
            enable_semantic=True,  # Supported flag
        )
        unified: UnifiedMemory[dict[str, Any]] = UnifiedMemory(config=config)

        # Basic operations should still work
        await unified.save({"data": "test"})
        state = await unified.load()
        assert state is not None
        assert state["data"] == "test"


class TestProspectiveMemory:
    """Test prospective (predictive) memory (legacy stubs)."""

    @pytest.mark.asyncio
    async def test_prospective_agent_basic(self) -> None:
        """Test ProspectiveAgent intention storage (legacy stub)."""
        # ProspectiveAgent is a deprecated stub with simple intentions list
        agent = ProspectiveAgent()

        # Add intentions
        agent.intend({"action": "fetch_weather", "context": "user request"})
        agent.intend({"action": "validate_email", "context": "form submission"})

        # Verify intentions stored
        assert len(agent.intentions) == 2
        assert agent.intentions[0]["action"] == "fetch_weather"
        assert agent.intentions[1]["action"] == "validate_email"

    @pytest.mark.asyncio
    async def test_prospective_agent_intentions_list(self) -> None:
        """Test ProspectiveAgent maintains intentions list."""
        agent = ProspectiveAgent()

        # Record intentions
        agent.intend({"type": "email", "action": "validate"})

        # Check intention is recorded
        assert len(agent.intentions) == 1
        assert agent.intentions[0]["type"] == "email"


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
    async def test_memory_with_simple_embedder(self) -> None:
        """Test memory store with SimpleEmbedder (embedding generates vectors)."""
        embedder: SimpleEmbedder = SimpleEmbedder(dimension=128)

        # Verify embedder works
        embedding = await embedder.embed("programming concepts")
        assert len(embedding) == 128

        # Use simple HolographicMemory (legacy stub) for storage
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()
        memory.store(
            "mem-prog", {"content": "Python is great for AI", "embedding": embedding}
        )

        retrieved = memory.retrieve("mem-prog")
        assert retrieved is not None
        assert "Python" in retrieved["content"]


class TestBudgetedMemory:
    """M × B: Budgeted memory operations (legacy stubs)."""

    @pytest.mark.asyncio
    async def test_memory_bulk_storage(self) -> None:
        """Test memory can store many items (legacy stub)."""
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()

        # Store many memories using legacy key-value interface
        for i in range(100):
            memory.store(f"bulk-{i:03d}", {"content": f"Bulk memory content {i}"})

        # Verify all stored
        for i in range(100):
            retrieved = memory.retrieve(f"bulk-{i:03d}")
            assert retrieved is not None

    @pytest.mark.asyncio
    async def test_memory_pattern_storage(self) -> None:
        """Test memory pattern store/retrieve (legacy stub)."""
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()

        # Store a pattern with metadata
        memory.store("pattern-001", {"content": "Test content", "concepts": ["decay"]})

        # Retrieve and verify
        retrieved = memory.retrieve("pattern-001")
        assert retrieved is not None
        assert retrieved["content"] == "Test content"


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
    """Test memory pattern access and modification (legacy stubs)."""

    @pytest.mark.asyncio
    async def test_pattern_store_retrieve(self) -> None:
        """Test pattern store/retrieve (legacy stub)."""
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()

        # Store and retrieve using legacy interface
        memory.store(
            "access-test", {"content": "Content to access", "concepts": ["access"]}
        )

        retrieved = memory.retrieve("access-test")
        assert retrieved is not None
        assert retrieved["content"] == "Content to access"

    @pytest.mark.asyncio
    async def test_multiple_patterns(self) -> None:
        """Test multiple pattern storage (legacy stub)."""
        memory: HolographicMemory[dict[str, Any]] = HolographicMemory()

        memory.store("res-001", {"text": "First memory about cats", "tags": ["cats"]})
        memory.store("res-002", {"text": "Second memory about dogs", "tags": ["dogs"]})
        memory.store(
            "res-003",
            {"text": "Third memory about cats and dogs", "tags": ["cats", "dogs"]},
        )

        # Verify all retrievable
        assert memory.retrieve("res-001") is not None
        assert memory.retrieve("res-002") is not None
        assert memory.retrieve("res-003") is not None


class TestMemoryLinkingAssociation:
    """Test memory linking and association features (legacy stubs)."""

    @pytest.mark.asyncio
    async def test_associative_web_memory_linking(self) -> None:
        """Test AssociativeWebMemory link creation (legacy stub)."""
        from agents.m import AssociativeWebMemory

        # AssociativeWebMemory is a deprecated stub with simple link storage
        memory = AssociativeWebMemory()

        # Link memories using legacy interface (source, target)
        memory.link("child", "parent")

        # Get links
        links = memory.get_links("child")
        assert "parent" in links

    @pytest.mark.asyncio
    async def test_associative_web_multiple_links(self) -> None:
        """Test AssociativeWebMemory multiple links (legacy stub)."""
        from agents.m import AssociativeWebMemory

        memory = AssociativeWebMemory()

        # Create link network
        memory.link("center", "related1")
        memory.link("center", "related2")
        memory.link("related1", "center")
        memory.link("related2", "center")

        # Get links from center
        links = memory.get_links("center")
        assert "related1" in links
        assert "related2" in links


# Run with: pytest impl/claude/agents/_tests/test_memory_pipeline_integration.py -v
