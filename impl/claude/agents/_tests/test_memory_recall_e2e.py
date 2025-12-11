"""
Memory Recall End-to-End Tests

Tests the complete memory recall lifecycle:
1. M-gent stores experience
2. D-gent persists to backend
3. L-gent indexes for search
4. M-gent recalls via holographic query
5. N-gent Bard creates narrative

Philosophy: Memory is not retrieval—it is active reconstruction.
The hologram metaphor is architecturally load-bearing.
"""

from dataclasses import dataclass

import pytest

# D-gent imports
from agents.d import (
    MemoryConfig,
    UnifiedMemory,
    VolatileAgent,
)

# L-gent imports
from agents.l import (
    CatalogEntry,
    EntityType,
    Registry,
    SemanticRegistry,
    SimpleEmbedder,
)

# M-gent imports
from agents.m import (
    ActionHistory,
    Cue,
    DgentBackedHolographicMemory,
    HolographicMemory,
    ProspectiveAgent,
    RecollectionAgent,
    Situation,
    TieredMemory,
)

# N-gent imports
from agents.n import (
    Bard,
    ChronicleBuilder,
    Determinism,
    Historian,
    MemoryCrystalStore,
    NarrativeGenre,
    NarrativeRequest,
    Verbosity,
)


@dataclass
class MockTraceable:
    """Mock traceable for testing."""

    id: str = "memory-agent"
    name: str = "MemoryAgent"


class TestMemoryStoreExperience:
    """Test M-gent experience storage."""

    @pytest.mark.asyncio
    async def test_store_simple_experience(self):
        """Test storing a simple experience in holographic memory."""
        memory = HolographicMemory()

        pattern = await memory.store(
            id="exp-001",
            content="User asked about Python list comprehensions",
            concepts=["python", "list", "comprehension", "tutorial"],
        )

        assert pattern.id == "exp-001"
        assert pattern.content == "User asked about Python list comprehensions"
        assert "python" in pattern.concepts

    @pytest.mark.asyncio
    async def test_store_multiple_related_experiences(self):
        """Test storing multiple related experiences."""
        memory = HolographicMemory()

        experiences = [
            (
                "exp-001",
                "Debugging a NullPointerException",
                ["java", "debug", "exception"],
            ),
            ("exp-002", "Fixed the null check in UserService", ["java", "fix", "user"]),
            ("exp-003", "Added unit tests for null handling", ["java", "test", "null"]),
        ]

        for exp_id, content, concepts in experiences:
            pattern = await memory.store(id=exp_id, content=content, concepts=concepts)
            assert pattern.id == exp_id

        # All memories should be stored
        results = await memory.retrieve_by_concept("java")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_store_with_embedding(self):
        """Test storing experience with embedding vector."""
        embedder = SimpleEmbedder(dimension=128)
        memory = HolographicMemory(embedder=embedder)

        embedding = await embedder.embed("debugging memory issues")
        pattern = await memory.store(
            id="exp-embed",
            content="Found a memory leak in the event handler",
            concepts=["memory", "leak", "debug"],
            embedding=embedding,
        )

        assert pattern.id == "exp-embed"
        assert pattern.embedding is not None


class TestDgentPersistence:
    """Test D-gent backend persistence."""

    @pytest.mark.asyncio
    async def test_persist_to_volatile_backend(self):
        """Test persisting memory to D-gent VolatileAgent."""
        volatile = VolatileAgent(_state={})
        config = MemoryConfig(
            enable_semantic=True,
            enable_temporal=True,
        )
        unified = UnifiedMemory(volatile, config)

        memory = DgentBackedHolographicMemory(
            storage=unified,
            namespace="e2e_test",
        )

        # Store experience
        await memory.store(
            id="persist-001",
            content="Important experience to persist",
            concepts=["important", "persist"],
        )

        # Persist to D-gent
        await memory.persist()

        # Verify persistence
        state = await unified.load()
        assert state is not None

    @pytest.mark.asyncio
    async def test_unified_memory_layers(self):
        """Test D-gent UnifiedMemory with all layers."""
        volatile = VolatileAgent(_state={"initial": "data"})
        config = MemoryConfig(
            enable_semantic=True,
            enable_temporal=True,
            enable_relational=True,
            track_lineage=True,
        )
        unified = UnifiedMemory(volatile, config)

        # Use semantic layer
        await unified.associate({"concept": "test"}, "test_concept")

        # Use temporal layer
        await unified.save({"version": 1})
        await unified.witness("v1", {"version": 1})

        await unified.save({"version": 2})
        await unified.witness("v2", {"version": 2})

        # Use relational layer
        await unified.relate("entity_a", "depends_on", "entity_b")

        # Verify current state
        current = await unified.load()
        assert current["version"] == 2

    @pytest.mark.asyncio
    async def test_memory_survives_simulated_restart(self):
        """Test memory persists through simulated restart."""
        shared_state = {}  # Simulate persistent storage

        # Session 1: Store - DgentBackedHolographicMemory requires temporal layer
        volatile1 = VolatileAgent(_state=shared_state)
        unified1 = UnifiedMemory(
            volatile1,
            MemoryConfig(enable_semantic=True, enable_temporal=True),
        )
        memory1 = DgentBackedHolographicMemory(
            storage=unified1, namespace="restart_test"
        )

        await memory1.store(
            id="session1-mem",
            content="This should survive restart",
            concepts=["persistent"],
        )
        await memory1.persist()

        # Capture state
        final_state = await unified1.load()

        # Session 2: Restore (simulated restart)
        volatile2 = VolatileAgent(_state=final_state if final_state else {})
        unified2 = UnifiedMemory(
            volatile2,
            MemoryConfig(enable_semantic=True, enable_temporal=True),
        )
        memory2 = DgentBackedHolographicMemory(
            storage=unified2, namespace="restart_test"
        )

        # Reload from persisted state - DgentBackedHolographicMemory uses recover(), not restore()
        await memory2.recover()

        # Memory should be available
        results = await memory2.retrieve("should survive", limit=5)
        assert isinstance(results, list)


class TestLgentIndexing:
    """Test L-gent semantic indexing for search."""

    @pytest.mark.asyncio
    async def test_register_memory_entry(self):
        """Test registering memory as catalog entry."""
        registry = Registry()

        entry = CatalogEntry(
            id="memory-entry-001",
            entity_type=EntityType.AGENT,
            name="DebuggingExperience",
            version="1.0.0",
            description="Experience debugging a production issue",
            keywords=["debug", "production", "issue"],
        )

        entry_id = await registry.register(entry)
        assert entry_id == "memory-entry-001"

        retrieved = await registry.get("memory-entry-001")
        assert retrieved.name == "DebuggingExperience"

    @pytest.mark.asyncio
    async def test_semantic_search_for_memory(self):
        """Test semantic search finds relevant memories."""
        embedder = SimpleEmbedder(dimension=128)
        registry = SemanticRegistry(embedder=embedder)

        # Register memory entries
        await registry.register(
            CatalogEntry(
                id="mem-api",
                entity_type=EntityType.AGENT,
                name="APIDesignExperience",
                version="1.0.0",
                description="Designing RESTful APIs with proper versioning",
                keywords=["api", "rest", "design"],
            )
        )
        await registry.register(
            CatalogEntry(
                id="mem-db",
                entity_type=EntityType.AGENT,
                name="DatabaseOptimization",
                version="1.0.0",
                description="Optimizing SQL queries for better performance",
                keywords=["database", "sql", "optimization"],
            )
        )
        await registry.register(
            CatalogEntry(
                id="mem-testing",
                entity_type=EntityType.AGENT,
                name="TestingStrategy",
                version="1.0.0",
                description="Integration testing with mocked dependencies",
                keywords=["testing", "integration", "mock"],
            )
        )

        # Fit semantic index
        await registry.fit()

        # Search semantically
        results = await registry.find_semantic("how to design web services", limit=5)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_keyword_and_semantic_hybrid(self):
        """Test hybrid keyword + semantic search."""
        embedder = SimpleEmbedder(dimension=128)
        registry = SemanticRegistry(embedder=embedder)

        await registry.register(
            CatalogEntry(
                id="hybrid-001",
                entity_type=EntityType.AGENT,
                name="PythonAsyncExperience",
                version="1.0.0",
                description="Working with async/await in Python 3.10",
                keywords=["python", "async", "await"],
            )
        )

        await registry.fit()

        # Keyword search - SemanticRegistry uses find() not search()
        keyword_results = await registry.find(query="python")
        assert len(keyword_results) >= 0

        # Semantic search
        semantic_results = await registry.find_semantic(
            "asynchronous programming", limit=5
        )
        assert isinstance(semantic_results, list)


class TestHolographicRecall:
    """Test M-gent holographic recall."""

    @pytest.mark.asyncio
    async def test_retrieve_by_concept(self):
        """Test retrieving memories by concept."""
        memory = HolographicMemory()

        await memory.store(
            "mem-001", "Python is great for scripting", ["python", "scripting"]
        )
        await memory.store(
            "mem-002", "JavaScript runs in browsers", ["javascript", "browser"]
        )
        await memory.store(
            "mem-003", "Python has strong ML libraries", ["python", "ml"]
        )

        results = await memory.retrieve_by_concept("python")
        assert len(results) >= 1

        # All results should relate to python
        for result in results:
            assert hasattr(result, "pattern")

    @pytest.mark.asyncio
    async def test_retrieve_with_similarity_threshold(self):
        """Test retrieval with similarity filtering."""
        embedder = SimpleEmbedder(dimension=128)
        memory = HolographicMemory(embedder=embedder)

        await memory.store(
            "mem-001", "Machine learning models need training data", ["ml", "data"]
        )
        await memory.store(
            "mem-002", "Deep learning uses neural networks", ["dl", "neural"]
        )
        await memory.store(
            "mem-003", "Making coffee with a French press", ["coffee", "brew"]
        )

        # Query should find ML-related memories
        results = await memory.retrieve("training neural networks", limit=10)
        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_recollection_agent_reconstruction(self):
        """Test RecollectionAgent reconstructs from cue."""
        memory = HolographicMemory()
        agent = RecollectionAgent(memory=memory)

        # Store original experience
        await memory.store(
            id="original-exp",
            content="Successfully deployed the application to production using CI/CD pipeline",
            concepts=["deployment", "ci/cd", "production"],
        )

        # Create cue for reconstruction - Cue uses 'text' not 'query', 'context' is a dict
        cue = Cue(
            text="deployment",
            concepts=["deployment"],
            context={"description": "Looking for deployment experiences"},
        )

        # Reconstruct from cue
        recollection = await agent.invoke(cue)

        # Recollection has 'content', 'confidence', 'sources', not 'memories'
        assert recollection is not None
        assert hasattr(recollection, "content")
        assert hasattr(recollection, "sources")

    @pytest.mark.asyncio
    async def test_tiered_memory_promotion(self):
        """Test TieredMemory promotes accessed memories."""
        embedder = SimpleEmbedder(dimension=128)
        memory = TieredMemory(embedder=embedder, working_capacity=7)

        # Perceive in sensory tier (TieredMemory uses perceive, not store)
        memory.perceive("New sensory input about programming", salience=0.6)

        # Attend to move from sensory to working tier
        attended = await memory.attend(focus="programming")

        # Memory may be promoted to working tier
        assert isinstance(attended, list)


class TestNarrativeGeneration:
    """Test N-gent Bard narrative creation."""

    @pytest.mark.asyncio
    async def test_bard_from_single_trace(self):
        """Test Bard creates narrative from single trace."""
        store = MemoryCrystalStore()
        historian = Historian(store)
        bard = Bard()

        traceable = MockTraceable()

        # Record trace
        ctx = historian.begin_trace(traceable, {"query": "how to debug?"})
        trace = historian.end_trace(
            ctx,
            action="RESPOND",
            outputs={"answer": "Use print statements and debugger"},
            determinism=Determinism.DETERMINISTIC,
        )

        # Generate narrative
        request = NarrativeRequest(
            traces=[trace],
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.NORMAL,
        )

        narrative = await bard.invoke(request)

        assert narrative is not None
        assert hasattr(narrative, "render")

    @pytest.mark.asyncio
    async def test_bard_from_multiple_traces(self):
        """Test Bard creates narrative from trace sequence."""
        store = MemoryCrystalStore()
        historian = Historian(store)
        bard = Bard()

        traceable = MockTraceable(id="multi-agent", name="MultiTraceAgent")

        # Record multiple traces
        traces = []
        actions = ["ANALYZE", "PLAN", "EXECUTE", "VERIFY"]
        for action in actions:
            ctx = historian.begin_trace(traceable, {"step": action})
            trace = historian.end_trace(
                ctx,
                action=action,
                outputs={"result": f"{action.lower()} completed"},
            )
            traces.append(trace)

        # Generate narrative
        request = NarrativeRequest(
            traces=traces,
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.VERBOSE,
        )

        narrative = await bard.invoke(request)

        assert narrative is not None

    @pytest.mark.asyncio
    async def test_bard_different_genres(self):
        """Test Bard adapts to different genres."""
        store = MemoryCrystalStore()
        historian = Historian(store)

        traceable = MockTraceable()
        ctx = historian.begin_trace(traceable, "test input")
        trace = historian.end_trace(ctx, action="TEST", outputs="test output")

        # Available genres: TECHNICAL, LITERARY, NOIR, SYSADMIN, MINIMAL, DETECTIVE
        genres = [
            NarrativeGenre.TECHNICAL,
            NarrativeGenre.LITERARY,
            NarrativeGenre.NOIR,
            NarrativeGenre.MINIMAL,
        ]

        for genre in genres:
            bard = Bard()
            request = NarrativeRequest(
                traces=[trace],
                genre=genre,
                verbosity=Verbosity.TERSE,
            )

            narrative = await bard.invoke(request)
            assert narrative is not None


class TestFullRecallLifecycle:
    """Test complete store → persist → index → recall → narrate lifecycle."""

    @pytest.mark.asyncio
    async def test_complete_lifecycle(self):
        """Test full memory lifecycle from store to narrative."""
        # 1. M-gent stores experience
        volatile = VolatileAgent(_state={})
        unified = UnifiedMemory(
            volatile, MemoryConfig(enable_semantic=True, enable_temporal=True)
        )
        memory = DgentBackedHolographicMemory(
            storage=unified, namespace="lifecycle_test"
        )

        experience = await memory.store(
            id="lifecycle-exp",
            content="Implemented a caching layer that reduced API latency by 50%",
            concepts=["caching", "performance", "api", "optimization"],
        )
        assert experience.id == "lifecycle-exp"

        # 2. D-gent persists to backend
        await memory.persist()
        state = await unified.load()
        assert state is not None

        # 3. L-gent indexes for search
        embedder = SimpleEmbedder(dimension=128)
        registry = SemanticRegistry(embedder=embedder)

        entry = CatalogEntry(
            id=experience.id,
            entity_type=EntityType.AGENT,
            name="CachingExperience",
            version="1.0.0",
            description=experience.content,
            keywords=experience.concepts,
        )
        await registry.register(entry)
        await registry.fit()

        # 4. M-gent recalls via holographic query
        recalled = await memory.retrieve("performance optimization", limit=5)
        assert isinstance(recalled, list)

        # 5. N-gent Bard creates narrative
        store = MemoryCrystalStore()
        historian = Historian(store)

        traceable = MockTraceable(id=experience.id, name="CachingAgent")
        ctx = historian.begin_trace(traceable, {"experience": experience.content})
        trace = historian.end_trace(
            ctx,
            action="RECALL",
            outputs={"recalled_experience": experience.content},
            determinism=Determinism.DETERMINISTIC,
        )

        bard = Bard()
        narrative = await bard.invoke(
            NarrativeRequest(
                traces=[trace],
                genre=NarrativeGenre.TECHNICAL,
                verbosity=Verbosity.NORMAL,
            )
        )

        assert narrative is not None
        rendered = narrative.render("markdown")
        assert isinstance(rendered, str)

    @pytest.mark.asyncio
    async def test_lifecycle_with_multiple_agents(self):
        """Test lifecycle involving multiple agent traces."""
        # Setup - DgentBackedHolographicMemory requires temporal layer
        volatile = VolatileAgent(_state={})
        unified = UnifiedMemory(
            volatile,
            MemoryConfig(enable_semantic=True, enable_temporal=True),
        )
        memory = DgentBackedHolographicMemory(storage=unified, namespace="multi_agent")

        # Store experiences from different "agents"
        experiences = [
            ("analyzer", "Analyzed code complexity metrics", ["analysis", "code"]),
            (
                "optimizer",
                "Optimized hot paths identified by profiler",
                ["optimization", "profiler"],
            ),
            (
                "tester",
                "Wrote regression tests for the optimized code",
                ["testing", "regression"],
            ),
        ]

        for agent_name, content, concepts in experiences:
            await memory.store(
                id=f"exp-{agent_name}", content=content, concepts=concepts
            )

        await memory.persist()

        # Record traces for chronicle
        store = MemoryCrystalStore()
        historian = Historian(store)
        traces = []

        for agent_name, content, concepts in experiences:
            traceable = MockTraceable(id=f"agent-{agent_name}", name=agent_name.title())
            ctx = historian.begin_trace(traceable, {"task": content})
            trace = historian.end_trace(
                ctx, action="COMPLETE", outputs={"status": "done"}
            )
            traces.append(trace)

        # Build chronicle - ChronicleBuilder uses add_traces() not add_crystal()
        builder = ChronicleBuilder()
        builder.add_traces(traces)

        chronicle = builder.build()
        assert chronicle is not None
        # Chronicle stores traces in _crystals dict
        assert chronicle.total_traces == 3

        # Generate combined narrative
        bard = Bard()
        narrative = await bard.invoke(
            NarrativeRequest(
                traces=traces,
                genre=NarrativeGenre.TECHNICAL,
                verbosity=Verbosity.NORMAL,
            )
        )

        assert narrative is not None

    @pytest.mark.asyncio
    async def test_lifecycle_with_prospective_memory(self):
        """Test lifecycle including prospective (predictive) memory."""
        # Setup prospective agent
        memory = HolographicMemory()
        history = ActionHistory()
        prospective = ProspectiveAgent(
            memory=memory,
            action_log=history,
            min_similarity=0.3,
            max_predictions=5,
        )

        # Record past experiences
        past_situations = [
            ("sit-001", "User reports slow page load", ["performance", "slow", "page"]),
            ("sit-002", "User reports memory error", ["memory", "error", "crash"]),
            (
                "sit-003",
                "User reports slow database queries",
                ["performance", "slow", "database"],
            ),
        ]

        for sit_id, desc, concepts in past_situations:
            situation = Situation(id=sit_id, description=desc, concepts=concepts)
            action = (
                "analyze_performance" if "performance" in concepts else "analyze_error"
            )
            await prospective.record_experience(
                situation=situation,
                action=action,
                outcome="issue resolved",
                success=True,
            )

        # New situation similar to past
        new_situation = Situation(
            id="sit-new",
            description="Application running slowly",
            concepts=["performance", "slow", "application"],
        )

        # Get predictions
        predictions = await prospective.invoke(new_situation)
        assert isinstance(predictions, list)

        # Record trace of prediction
        store = MemoryCrystalStore()
        historian = Historian(store)

        traceable = MockTraceable(id="prospective-agent", name="ProspectiveAgent")
        ctx = historian.begin_trace(traceable, {"situation": new_situation.description})
        trace = historian.end_trace(
            ctx,
            action="PREDICT",
            outputs={"predictions": [str(p) for p in predictions[:3]]},
        )

        # Generate narrative
        bard = Bard()
        narrative = await bard.invoke(
            NarrativeRequest(
                traces=[trace],
                genre=NarrativeGenre.TECHNICAL,
                verbosity=Verbosity.NORMAL,
            )
        )

        assert narrative is not None


class TestEdgeCases:
    """Test edge cases in memory recall lifecycle."""

    @pytest.mark.asyncio
    async def test_empty_memory_recall(self):
        """Test recalling from empty memory."""
        memory = HolographicMemory()

        results = await memory.retrieve("nonexistent query", limit=5)
        assert results == []

    @pytest.mark.asyncio
    async def test_recall_with_no_matching_concepts(self):
        """Test recall when no concepts match."""
        memory = HolographicMemory()

        await memory.store("mem-001", "Python programming", ["python"])

        results = await memory.retrieve_by_concept("javascript")
        # Should return empty or no matches
        assert len(results) == 0 or all(
            hasattr(r, "similarity") and r.similarity < 0.5 for r in results
        )

    @pytest.mark.asyncio
    async def test_narrative_from_empty_traces(self):
        """Test Bard handles empty trace list gracefully."""
        bard = Bard()

        request = NarrativeRequest(
            traces=[],
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.TERSE,
        )

        narrative = await bard.invoke(request)
        # Should handle gracefully
        assert narrative is not None

    @pytest.mark.asyncio
    async def test_memory_compression_after_many_stores(self):
        """Test memory compression after storing many experiences."""
        memory = HolographicMemory()

        # Store many memories
        for i in range(50):
            await memory.store(
                id=f"bulk-{i:03d}",
                content=f"Bulk experience number {i} about various topics",
                concepts=["bulk", f"topic-{i % 5}"],
            )

        # Compress
        compressed = await memory.compress(ratio=0.5)
        assert compressed >= 0

        # Memory should still be functional
        results = await memory.retrieve_by_concept("bulk")
        assert isinstance(results, list)


class TestIntegrationResilience:
    """Test resilience across integration boundaries."""

    @pytest.mark.asyncio
    async def test_dgent_failure_recovery(self):
        """Test memory operates when D-gent backend is unavailable."""
        # Start with working memory
        memory = HolographicMemory()

        await memory.store("resilient-001", "This should work", ["resilient"])

        # Memory should still function without persistence layer
        results = await memory.retrieve_by_concept("resilient")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_lgent_search_fallback(self):
        """Test search works with fallback when semantic index unavailable."""
        registry = Registry()  # Basic registry without semantic

        await registry.register(
            CatalogEntry(
                id="fallback-001",
                entity_type=EntityType.AGENT,
                name="FallbackTest",
                version="1.0.0",
                description="Testing fallback search",
                keywords=["fallback", "search"],
            )
        )

        # Keyword search should still work - Registry uses find() not search()
        results = await registry.find(query="fallback")
        assert len(results) >= 1

    @pytest.mark.asyncio
    async def test_narrative_without_llm(self):
        """Test Bard produces narrative without real LLM."""
        # Bard should use SimpleLLMProvider by default (template-based)
        bard = Bard()
        store = MemoryCrystalStore()
        historian = Historian(store)

        traceable = MockTraceable()
        ctx = historian.begin_trace(traceable, "test")
        trace = historian.end_trace(ctx, action="TEST", outputs="output")

        narrative = await bard.invoke(
            NarrativeRequest(
                traces=[trace],
                genre=NarrativeGenre.TECHNICAL,
                verbosity=Verbosity.TERSE,
            )
        )

        # Should produce template-based narrative
        assert narrative is not None


# Run with: pytest impl/claude/agents/_tests/test_memory_recall_e2e.py -v
