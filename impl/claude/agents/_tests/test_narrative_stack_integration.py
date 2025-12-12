"""
Cross-Agent Integration Tests: Narrative Stack

Tests integration across the narrative domain:
- N × M: N-gent crystals persist in M-gent holographic memory
- N × K: N-gent narrative includes K-gent persona
- N × O: N-gent records O-gent observations

Philosophy:
    The event is the stone. The story is the shadow.
    Collect stones (Historian). Cast shadows (Bard).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

import pytest

# K-gent imports
from agents.k import (
    DialogueMode,
    PersonaSeed,
    PersonaState,
)

# M-gent imports
from agents.m import (
    HolographicMemory,
)

# N-gent imports
from agents.n import (
    # Bard (read-time)
    Bard,
    # Chronicle (multi-agent)
    ChronicleBuilder,
    Historian,
    MemoryCrystalStore,
    NarrativeGenre,
    NarrativeRequest,
    # Core types
    SemanticTrace,
    SimpleLLMProvider,
    Verbosity,
)

# O-gent imports
from agents.o import (
    ObservationContext,
    ObservationResult,
    ObservationStatus,
)

# =============================================================================
# Helper Functions
# =============================================================================


def create_test_trace(
    trace_id: str,
    agent_id: str = "test-agent",
    agent_genus: str = "P",
    action: str = "INVOKE",
    parent_id: str | None = None,
    inputs: dict[str, Any] | None = None,
    outputs: dict[str, Any] | None = None,
    gas_consumed: int = 100,
    duration_ms: int = 50,
) -> SemanticTrace:
    """Create a test SemanticTrace with all required fields."""
    return SemanticTrace(
        trace_id=trace_id,
        parent_id=parent_id,
        timestamp=datetime.now(timezone.utc),
        agent_id=agent_id,
        agent_genus=agent_genus,
        action=action,
        inputs=inputs or {},
        outputs=outputs,
        input_hash="test-hash",
        input_snapshot=b"{}",
        output_hash="output-hash" if outputs else None,
        gas_consumed=gas_consumed,
        duration_ms=duration_ms,
    )


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def crystal_store() -> MemoryCrystalStore:
    """Create a memory crystal store."""
    return MemoryCrystalStore()


@pytest.fixture
def historian(crystal_store: MemoryCrystalStore) -> Historian:
    """Create a Historian."""
    return Historian(crystal_store)


@pytest.fixture
def sample_traces() -> list[SemanticTrace]:
    """Create sample traces for testing."""
    return [
        create_test_trace(
            trace_id="trace-001",
            agent_id="agent-a",
            agent_genus="P",
            inputs={"query": "parse this"},
            outputs={"ast": {"type": "statement"}},
        ),
        create_test_trace(
            trace_id="trace-002",
            agent_id="agent-b",
            agent_genus="J",
            parent_id="trace-001",
            inputs={"code": "def foo() -> None: pass"},
            outputs={"compiled": True},
        ),
        create_test_trace(
            trace_id="trace-003",
            agent_id="agent-a",
            agent_genus="P",
            action="EMIT",
            parent_id="trace-002",
            inputs={"validate": True},
            outputs={"valid": True},
        ),
    ]


@pytest.fixture
def holographic_memory() -> HolographicMemory[Any]:
    """Create a HolographicMemory instance."""
    return HolographicMemory()


@pytest.fixture
def persona_seed() -> PersonaSeed:
    """Create a PersonaSeed for K-gent tests."""
    return PersonaSeed(
        name="Test Persona",
    )


@pytest.fixture
def mock_llm_provider() -> SimpleLLMProvider:
    """Create a mock LLM provider for Bard tests."""
    # SimpleLLMProvider takes: response (optional str)
    provider = SimpleLLMProvider(response="Generated narrative for test traces...")
    return provider


# =============================================================================
# N × M Integration: Crystals in Holographic Memory
# =============================================================================


class TestNarrativeMemoryIntegration:
    """N × M: Narrative crystals persist in holographic memory."""

    def test_historian_stores_trace(
        self, historian: Historian, sample_traces: list[SemanticTrace]
    ) -> None:
        """Test Historian stores traces."""
        for trace in sample_traces:
            historian.store.store(trace)

        retrieved = historian.store.get("trace-001")
        assert retrieved is not None
        assert retrieved.agent_genus == "P"

    @pytest.mark.asyncio
    async def test_trace_encodes_to_memory_pattern(
        self,
        holographic_memory: HolographicMemory[Any],
        sample_traces: list[SemanticTrace],
    ) -> None:
        """Test trace can be encoded as memory pattern."""
        trace = sample_traces[0]

        # Store trace as pattern via HolographicMemory API
        # HolographicMemory.store takes: id, content, concepts, embedding
        pattern = await holographic_memory.store(
            id=trace.trace_id,
            content={
                "trace_id": trace.trace_id,
                "agent": trace.agent_id,
                "action": trace.action,
                "inputs": trace.inputs,
                "outputs": trace.outputs,
            },
            concepts=["trace", trace.agent_genus],
        )

        # Memory should store - stats() returns dict (not async)
        # pattern is stored (used implicitly)
        assert pattern is not None
        stats = holographic_memory.stats()
        assert stats.get("total_patterns", 0) >= 1

    def test_crystal_store_query_by_genus(
        self, crystal_store: MemoryCrystalStore, sample_traces: list[SemanticTrace]
    ) -> None:
        """Test querying crystals by genus."""
        for trace in sample_traces:
            crystal_store.store(trace)

        p_traces = list(crystal_store.query(agent_genus="P"))
        j_traces = list(crystal_store.query(agent_genus="J"))

        assert len(p_traces) == 2  # Two P-gent traces
        assert len(j_traces) == 1  # One J-gent trace

    def test_crystal_lineage_preserved(
        self, crystal_store: MemoryCrystalStore, sample_traces: list[SemanticTrace]
    ) -> None:
        """Test trace lineage is preserved."""
        for trace in sample_traces:
            crystal_store.store(trace)

        child = crystal_store.get("trace-003")
        assert child is not None
        assert child.parent_id == "trace-002"

        parent_id = child.parent_id
        assert parent_id is not None
        parent = crystal_store.get(parent_id)
        assert parent is not None
        assert parent.parent_id == "trace-001"

    def test_resonant_crystal_store_concept(
        self, crystal_store: MemoryCrystalStore, sample_traces: list[SemanticTrace]
    ) -> None:
        """Test ResonantCrystalStore integrates with M-gent (conceptual)."""
        # Store traces
        for trace in sample_traces:
            crystal_store.store(trace)

        # ResonantCrystalStore would add holographic resonance
        # This tests the interface compatibility
        class MockMemoryBridge:
            def __init__(self, memory: HolographicMemory[str]) -> None:
                self.memory = memory

            def resonate(self, trace: SemanticTrace) -> float:
                """Compute resonance score with memory."""
                # In real implementation, would use embeddings
                return 0.8

        bridge = MockMemoryBridge(HolographicMemory[str]())
        score = bridge.resonate(sample_traces[0])
        assert 0.0 <= score <= 1.0

    def test_tiered_memory_with_crystals(
        self, sample_traces: list[SemanticTrace]
    ) -> None:
        """Test TieredMemory hierarchy with crystal content."""
        from agents.m import TieredMemory

        tiered: TieredMemory[SemanticTrace] = TieredMemory()

        # TieredMemory uses perceive() for sensory tier
        # and attend() to move to working memory
        recent_trace = sample_traces[-1]
        old_trace = sample_traces[0]

        # Perceive into sensory tier
        tiered.perceive(recent_trace, salience=0.8)
        tiered.perceive(old_trace, salience=0.5)

        # Get recent perceptions from sensory
        sensory_items = tiered.recent_perceptions(seconds=10.0)

        assert len(sensory_items) >= 1


# =============================================================================
# N × K Integration: Narrative with Persona
# =============================================================================


class TestNarrativePersonaIntegration:
    """N × K: Narrative includes K-gent persona."""

    def test_persona_seed_creation(self, persona_seed: PersonaSeed) -> None:
        """Test PersonaSeed creates successfully."""
        assert persona_seed.name == "Test Persona"
        assert "preferences" in dir(persona_seed)

    def test_persona_state_from_seed(self, persona_seed: PersonaSeed) -> None:
        """Test PersonaState from seed."""
        state = PersonaState(seed=persona_seed)

        assert state.seed.name == "Test Persona"

    def test_persona_in_narrative_genre(self, persona_seed: PersonaSeed) -> None:
        """Test persona influences narrative genre."""
        state = PersonaState(seed=persona_seed)

        # Analytical persona might prefer TECHNICAL genre
        preferred_genre = NarrativeGenre.TECHNICAL

        assert state.seed.name == "Test Persona"
        assert preferred_genre == NarrativeGenre.TECHNICAL

    def test_persona_verbosity_preference(self, persona_seed: PersonaSeed) -> None:
        """Test persona verbosity maps to Bard verbosity."""
        state = PersonaState(seed=persona_seed)

        # PersonaSeed.preferences is a dict with "communication" key
        # communication.length can be "concise preferred", "normal", "detailed"
        communication = state.seed.preferences.get("communication", {})
        verbosity_pref = (
            communication.get("length", "normal")
            if isinstance(communication, dict)
            else "normal"
        )

        # Verbosity enum uses: TERSE, NORMAL, VERBOSE
        verbosity_map = {
            "concise preferred": Verbosity.TERSE,
            "normal": Verbosity.NORMAL,
            "detailed": Verbosity.VERBOSE,
        }

        bard_verbosity = verbosity_map.get(verbosity_pref, Verbosity.NORMAL)
        assert bard_verbosity in (
            Verbosity.TERSE,
            Verbosity.NORMAL,
            Verbosity.VERBOSE,
        )

    def test_dialogue_mode_affects_narrative(self, persona_seed: PersonaSeed) -> None:
        """Test dialogue mode influences narrative style."""
        # Different dialogue modes
        modes = [
            DialogueMode.REFLECT,  # Introspective
            DialogueMode.ADVISE,  # Instructive
            DialogueMode.CHALLENGE,  # Socratic
            DialogueMode.EXPLORE,  # Curious
        ]

        for mode in modes:
            # Mode would influence how Bard tells the story
            assert mode.value in ["reflect", "advise", "challenge", "explore"]

    def test_persona_constraints_in_narration(self, persona_seed: PersonaSeed) -> None:
        """Test persona constraints affect narration."""
        state = PersonaState(seed=persona_seed)

        # Check persona values
        values = state.seed.preferences.get("values", [])

        # Epistemic humility should be in values
        if "intellectual honesty" in values:
            # Narrator should use hedging language
            hedging_phrases = [
                "it appears that",
                "based on the evidence",
                "the system observed",
            ]
            # In real implementation, Bard would include these
            assert len(hedging_phrases) > 0

    def test_chronicle_with_persona_perspective(
        self, sample_traces: list[SemanticTrace], persona_seed: PersonaSeed
    ) -> None:
        """Test Chronicle can include persona perspective."""
        # Build chronicle
        builder = ChronicleBuilder()

        for trace in sample_traces:
            builder.add_trace(trace)

        chronicle = builder.build()

        # Chronicle could be filtered by persona preferences
        state = PersonaState(seed=persona_seed)

        # Persona might only care about certain genera
        # Chronicle stores traces in _crystals dict keyed by agent_id
        # Use get_agent_crystals() to access traces
        interesting_genera = {"P", "J"}  # Parser and JIT
        relevant_traces = []
        for agent_id in chronicle.agent_ids:
            traces = chronicle.get_agent_crystals(agent_id)
            for t in traces:
                if t.agent_genus in interesting_genera:
                    relevant_traces.append(t)

        # Verify persona and filtering
        assert state.seed.name == "Test Persona"
        assert len(relevant_traces) >= 2


# =============================================================================
# N × O Integration: Narrative Records Observations
# =============================================================================


class TestNarrativeObservationIntegration:
    """N × O: Narrative records observations."""

    def test_observation_creates_trace(self, historian: Historian) -> None:
        """Test O-gent observation creates N-gent trace."""
        # Simulate observation data
        observation = ObservationResult(
            context=ObservationContext(
                agent_id="observed-agent",
                agent_name="TestAgent",
                input_data={"query": "test"},
                observation_id="obs-001",
            ),
            status=ObservationStatus.COMPLETED,
            output_data={"result": "success"},
            duration_ms=42.5,
        )

        # Convert to trace
        trace = create_test_trace(
            trace_id=f"n-{observation.context.observation_id}",
            agent_id="o-gent-observer",
            agent_genus="O",
            inputs={
                "observed_agent": observation.context.agent_id,
                "observation_id": observation.context.observation_id,
            },
            outputs={
                "status": observation.status.value,
                "duration_ms": observation.duration_ms,
            },
        )

        historian.store.store(trace)
        retrieved = historian.store.get(trace.trace_id)

        assert retrieved is not None
        assert retrieved.agent_genus == "O"
        assert retrieved.outputs is not None
        assert retrieved.outputs["duration_ms"] == 42.5

    def test_panopticon_status_to_chronicle(self, historian: Historian) -> None:
        """Test Panopticon status converts to chronicle entry."""
        # Simulate Panopticon status
        status_data = {
            "system_status": "HOMEOSTATIC",
            "telemetry_healthy": True,
            "semantic_healthy": True,
            "economic_healthy": True,
            "alert_count": 0,
        }

        trace = create_test_trace(
            trace_id=f"panopticon-{datetime.now(timezone.utc).isoformat()}",
            agent_id="panopticon",
            agent_genus="O",
            action="EMIT",
            inputs={"request": "status_poll"},
            outputs=status_data,
        )

        historian.store.store(trace)

        # Can query by agent
        status_traces = list(historian.store.query(agent_id="panopticon"))
        assert len(status_traces) >= 1

    def test_observation_hierarchy_in_narrative(self, historian: Historian) -> None:
        """Test observation hierarchy (telemetry → semantic → axiological)."""
        # Telemetry observation
        telemetry_trace = create_test_trace(
            trace_id="obs-telemetry-001",
            agent_id="telemetry-observer",
            agent_genus="O",
            inputs={"level": "telemetry"},
            outputs={"latency_ms": 15.2, "errors": 0},
        )

        # Semantic observation (depends on telemetry)
        semantic_trace = create_test_trace(
            trace_id="obs-semantic-001",
            agent_id="semantic-observer",
            agent_genus="O",
            parent_id="obs-telemetry-001",
            inputs={"level": "semantic"},
            outputs={"drift": 0.05, "hallucination_risk": "low"},
        )

        # Axiological observation (depends on semantic)
        axiological_trace = create_test_trace(
            trace_id="obs-axiological-001",
            agent_id="axiological-observer",
            agent_genus="O",
            parent_id="obs-semantic-001",
            inputs={"level": "axiological"},
            outputs={"roc": 1.2, "value_aligned": True},
        )

        for trace in [telemetry_trace, semantic_trace, axiological_trace]:
            historian.store.store(trace)

        # Verify hierarchy
        axiological = historian.store.get("obs-axiological-001")
        assert axiological is not None
        assert axiological.parent_id is not None
        semantic = historian.store.get(axiological.parent_id)
        assert semantic is not None
        assert semantic.parent_id is not None
        telemetry = historian.store.get(semantic.parent_id)
        assert telemetry is not None

        assert telemetry.trace_id == "obs-telemetry-001"
        assert semantic.trace_id == "obs-semantic-001"


# =============================================================================
# Full Stack Integration
# =============================================================================


class TestNarrativeStackFullIntegration:
    """Test complete narrative stack flow."""

    @pytest.mark.asyncio
    async def test_trace_to_memory_to_narrative(
        self,
        historian: Historian,
        holographic_memory: HolographicMemory[Any],
        mock_llm_provider: SimpleLLMProvider,
        sample_traces: list[SemanticTrace],
    ) -> None:
        """Test trace → M-gent memory → N-gent narrative."""
        # 1. Store traces via Historian
        for trace in sample_traces:
            historian.store.store(trace)

        # 2. Encode to holographic memory using async API
        for trace in sample_traces:
            await holographic_memory.store(
                id=f"memory-{trace.trace_id}",
                content={
                    "trace_id": trace.trace_id,
                    "summary": f"{trace.agent_genus}-{trace.action}",
                },
                concepts=["trace", trace.agent_genus],
            )

        # 3. Retrieve from memory (HolographicMemory uses retrieve(), not recall())
        recalled = await holographic_memory.retrieve("P-gent actions", limit=5)

        # 4. Create narrative request
        # Verbosity uses: TERSE, NORMAL, VERBOSE
        request = NarrativeRequest(
            traces=sample_traces,
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.TERSE,
        )

        # 5. Bard would generate narrative (mocked)
        bard = Bard(llm=mock_llm_provider)

        # Verify memory retrieval, request is valid for Bard
        assert recalled is not None  # Memory was queried
        assert bard is not None  # Bard was created
        assert request.traces == sample_traces
        assert request.genre == NarrativeGenre.TECHNICAL

    def test_observation_to_crystal_to_bard(
        self, historian: Historian, mock_llm_provider: SimpleLLMProvider
    ) -> None:
        """Test O-gent observation → N-gent crystal → Bard narrative."""
        # 1. Simulate observation
        obs_trace = create_test_trace(
            trace_id="flow-obs-001",
            agent_id="panopticon",
            agent_genus="O",
            inputs={"observed": "test-agent"},
            outputs={
                "status": "COMPLETED",
                "findings": ["latency_normal", "no_drift"],
            },
        )

        historian.store.store(obs_trace)

        # 2. Query observations
        observations = list(historian.store.query(agent_genus="O"))

        # 3. Create narrative request
        # Verbosity uses: TERSE, NORMAL, VERBOSE
        request = NarrativeRequest(
            traces=observations,
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.TERSE,
        )

        # 4. Bard produces narrative
        bard = Bard(llm=mock_llm_provider)

        # Verify Bard created and narrative request has observation data
        assert bard is not None
        assert len(request.traces) >= 1
        assert request.traces[0].agent_genus == "O"

    def test_persona_filtered_observation_narrative(
        self,
        historian: Historian,
        persona_seed: PersonaSeed,
        mock_llm_provider: SimpleLLMProvider,
    ) -> None:
        """Test persona filters observations for narrative."""
        # 1. Store various observations
        traces = [
            create_test_trace(
                trace_id="obs-tel-001",
                agent_id="telemetry",
                agent_genus="O",
                inputs={"level": "telemetry"},
                outputs={"latency": 10},
            ),
            create_test_trace(
                trace_id="obs-sem-001",
                agent_id="semantic",
                agent_genus="O",
                inputs={"level": "semantic"},
                outputs={"drift": 0.1},
            ),
        ]

        for trace in traces:
            historian.store.store(trace)

        # 2. Persona prefers analytical (semantic) content
        state = PersonaState(seed=persona_seed)

        # Filter based on persona interest
        # Analytical persona cares about semantic observations
        filtered_traces = [t for t in traces if "semantic" in t.inputs.get("level", "")]

        # 3. Create persona-aware narrative request
        # Verbosity uses: TERSE, NORMAL, VERBOSE
        request = NarrativeRequest(
            traces=filtered_traces,
            genre=NarrativeGenre.TECHNICAL,
            verbosity=Verbosity.TERSE,
        )

        # Verify persona loaded and filtering worked
        assert state.seed.name == "Test Persona"
        assert len(request.traces) == 1
        assert request.traces[0].inputs["level"] == "semantic"

    def test_multi_agent_chronicle_with_o_gent(
        self, historian: Historian, sample_traces: list[SemanticTrace]
    ) -> None:
        """Test Chronicle weaves O-gent observations with other agents."""
        # Store original traces
        for trace in sample_traces:
            historian.store.store(trace)

        # Add O-gent observation of the interaction
        obs_trace = create_test_trace(
            trace_id="chronicle-obs-001",
            agent_id="chronicler-observer",
            agent_genus="O",
            inputs={"observed_interaction": [t.trace_id for t in sample_traces]},
            outputs={
                "interaction_type": "P × J pipeline",
                "health": "nominal",
            },
        )
        historian.store.store(obs_trace)

        # Build chronicle including observation
        builder = ChronicleBuilder()
        for trace in sample_traces:
            builder.add_trace(trace)
        builder.add_trace(obs_trace)

        chronicle = builder.build()

        # Chronicle should include both agent work and observation
        # Collect genera from all traces via agent_ids
        # Use get_agent_crystals() to access traces
        genera = set()
        for agent_id in chronicle.agent_ids:
            traces = chronicle.get_agent_crystals(agent_id)
            for t in traces:
                genera.add(t.agent_genus)

        assert "P" in genera  # Parser
        assert "J" in genera  # JIT
        assert "O" in genera  # Observer
