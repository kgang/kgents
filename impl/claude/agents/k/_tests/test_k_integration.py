"""
K-gent Integration Tests: K × M × N × D

Tests integration between K-gent (Persona) and other agents:
- K × M: Memory-backed persona preferences
- K × N: Narrative tracing of persona dialogues
- K × D: Persistent persona state
- K × H: H-gent introspection of persona

Philosophy: K-gent is Ground projected through persona schema.
"""

import pytest

from agents.k import (
    KgentAgent,
    PersonaQueryAgent,
    PersonaState,
    PersonaSeed,
    PersonaQuery,
    PersonaResponse,
    DialogueInput,
    DialogueOutput,
    DialogueMode,
    kgent,
    query_persona,
)
from agents.k.persistent_persona import (
    PersistentPersonaAgent,
)
from agents.m import HolographicMemory
from agents.n import Chronicle, SemanticTrace
from datetime import datetime


class TestKgentDialogue:
    """Core K-gent dialogue tests."""

    @pytest.mark.asyncio
    async def test_reflect_mode(self):
        """Test reflect dialogue mode."""
        agent = kgent()
        result = await agent.invoke(
            DialogueInput(
                message="I'm thinking about code quality",
                mode=DialogueMode.REFLECT,
            )
        )

        assert isinstance(result, DialogueOutput)
        assert result.mode == DialogueMode.REFLECT
        assert result.response  # Should have reflection response

    @pytest.mark.asyncio
    async def test_advise_mode(self):
        """Test advise dialogue mode."""
        agent = kgent()
        result = await agent.invoke(
            DialogueInput(
                message="Should I use TypeScript or Python?",
                mode=DialogueMode.ADVISE,
            )
        )

        assert isinstance(result, DialogueOutput)
        assert result.mode == DialogueMode.ADVISE
        assert result.response

    @pytest.mark.asyncio
    async def test_challenge_mode(self):
        """Test challenge dialogue mode."""
        agent = kgent()
        result = await agent.invoke(
            DialogueInput(
                message="I'm going to add lots of features",
                mode=DialogueMode.CHALLENGE,
            )
        )

        assert isinstance(result, DialogueOutput)
        assert result.mode == DialogueMode.CHALLENGE
        # Challenge mode should push back on feature creep
        assert result.response

    @pytest.mark.asyncio
    async def test_explore_mode(self):
        """Test explore dialogue mode."""
        agent = kgent()
        result = await agent.invoke(
            DialogueInput(
                message="What if we approach this differently?",
                mode=DialogueMode.EXPLORE,
            )
        )

        assert isinstance(result, DialogueOutput)
        assert result.mode == DialogueMode.EXPLORE
        assert result.response

    @pytest.mark.asyncio
    async def test_preference_reference(self):
        """Test that dialogue references relevant preferences."""
        # Create persona with specific preferences
        state = PersonaState(
            seed=PersonaSeed(
                preferences={
                    "values": ["composability", "simplicity"],
                    "dislikes": ["complexity", "over-engineering"],
                }
            )
        )
        agent = KgentAgent(state=state)

        result = await agent.invoke(
            DialogueInput(
                message="Let me think about composability",
                mode=DialogueMode.REFLECT,
            )
        )

        # Should reference composability preference
        assert (
            any(
                "composability" in pref.lower() or "composable" in pref.lower()
                for pref in result.referenced_preferences
            )
            or "composab" in result.response.lower()
        )


class TestPersonaQuery:
    """Test PersonaQueryAgent."""

    @pytest.mark.asyncio
    async def test_query_all_preferences(self):
        """Test querying all preferences."""
        agent = query_persona()
        result = await agent.invoke(PersonaQuery(aspect="preference"))

        assert isinstance(result, PersonaResponse)
        assert result.preferences  # Should have some preferences
        assert result.confidence > 0

    @pytest.mark.asyncio
    async def test_query_patterns(self):
        """Test querying patterns."""
        agent = query_persona()
        result = await agent.invoke(PersonaQuery(aspect="pattern"))

        assert isinstance(result, PersonaResponse)
        assert result.patterns  # Should have some patterns

    @pytest.mark.asyncio
    async def test_query_topic_filter(self):
        """Test querying with topic filter."""
        agent = query_persona()
        result = await agent.invoke(PersonaQuery(aspect="all", topic="communication"))

        assert isinstance(result, PersonaResponse)
        # Should filter to communication-related items

    @pytest.mark.asyncio
    async def test_query_for_agent(self):
        """Test querying with for_agent context."""
        agent = query_persona()
        result = await agent.invoke(PersonaQuery(aspect="all", for_agent="robin"))

        assert isinstance(result, PersonaResponse)
        # Should have style suggestions for robin agent
        assert result.suggested_style

    @pytest.mark.asyncio
    async def test_invoke_safe(self):
        """Test safe query method that returns Maybe."""
        agent = query_persona()
        maybe_result = agent.invoke_safe(PersonaQuery(aspect="all"))

        assert maybe_result.is_just
        result = maybe_result.value_or(None)
        assert result is not None
        assert isinstance(result, PersonaResponse)


class TestKgentMemoryIntegration:
    """Test K-gent × M-gent integration."""

    @pytest.mark.asyncio
    async def test_dialogue_history_storage(self):
        """Test storing dialogue history in holographic memory."""
        memory = HolographicMemory[DialogueOutput]()
        agent = kgent()

        # Have several dialogues
        dialogue1 = await agent.invoke(
            DialogueInput(
                message="What about design patterns?", mode=DialogueMode.EXPLORE
            )
        )
        dialogue2 = await agent.invoke(
            DialogueInput(
                message="I want to add more features", mode=DialogueMode.CHALLENGE
            )
        )

        # Store in memory
        await memory.store("design_discussion", dialogue1)
        await memory.store("feature_discussion", dialogue2)

        # Retrieve by concept
        retrieved = await memory.retrieve("patterns")
        assert len(retrieved) > 0

    @pytest.mark.asyncio
    async def test_preference_memory(self):
        """Test storing preference updates in memory."""
        memory = HolographicMemory[PersonaResponse]()
        agent = query_persona()

        # Query preferences
        response = await agent.invoke(
            PersonaQuery(aspect="preference", topic="communication")
        )

        # Store preference response
        await memory.store("communication_prefs", response)

        # Should be retrievable
        retrieved = await memory.retrieve("style")
        assert len(retrieved) > 0


def _make_trace(
    agent_id: str, action: str, inputs: dict, outputs: dict, mode: str = None
) -> SemanticTrace:
    """Helper to create SemanticTrace with required fields."""
    import hashlib
    import uuid

    input_bytes = str(inputs).encode()
    return SemanticTrace(
        trace_id=str(uuid.uuid4()),
        parent_id=None,
        timestamp=datetime.now(),
        agent_id=agent_id,
        agent_genus="K",
        action=action,
        inputs=inputs,
        outputs=outputs,
        input_hash=hashlib.sha256(input_bytes).hexdigest()[:16],
        input_snapshot=input_bytes,
        output_hash=hashlib.sha256(str(outputs).encode()).hexdigest()[:16]
        if outputs
        else None,
        gas_consumed=100,
        duration_ms=10,
        metadata={"mode": mode} if mode else {},
    )


class TestKgentNarrativeIntegration:
    """Test K-gent × N-gent integration."""

    @pytest.mark.asyncio
    async def test_dialogue_tracing(self):
        """Test tracing K-gent dialogues with N-gent Chronicle."""
        chronicle = Chronicle()
        agent = kgent()

        # Have dialogue
        result = await agent.invoke(
            DialogueInput(message="Let's think about ethics", mode=DialogueMode.REFLECT)
        )

        # Create trace using proper SemanticTrace API
        trace = _make_trace(
            agent_id="K-gent",
            action="DIALOGUE",
            inputs={"message": "ethics reflection request"},
            outputs={"response": result.response[:50] if result.response else ""},
            mode=result.mode.value,
        )

        chronicle.add_crystal(trace)

        # Verify trace recorded
        timeline = chronicle.weave()
        assert len(timeline) == 1
        assert timeline[0].agent_id == "K-gent"

    @pytest.mark.asyncio
    async def test_multi_mode_dialogue_chronicle(self):
        """Test chronicling dialogues across multiple modes."""
        chronicle = Chronicle()
        agent = kgent()

        for mode in DialogueMode:
            result = await agent.invoke(
                DialogueInput(message=f"Testing {mode.value} mode", mode=mode)
            )

            trace = _make_trace(
                agent_id="K-gent",
                action=f"DIALOGUE_{mode.value.upper()}",
                inputs={"message": f"Testing {mode.value} mode"},
                outputs={"response": result.response[:50] if result.response else ""},
                mode=mode.value,
            )
            chronicle.add_crystal(trace)

        # Should have 4 traces (one per mode)
        assert len(chronicle.get_agent_crystals("K-gent")) == 4

    @pytest.mark.asyncio
    async def test_query_tracing(self):
        """Test tracing persona queries."""
        chronicle = Chronicle()
        agent = query_persona()

        # Make several queries
        await agent.invoke(PersonaQuery(aspect="preference"))
        await agent.invoke(PersonaQuery(aspect="pattern"))
        await agent.invoke(PersonaQuery(aspect="all", for_agent="robin"))

        # Record traces
        for i, query_type in enumerate(["preference", "pattern", "all"]):
            trace = _make_trace(
                agent_id="K-gent",
                action="QUERY",
                inputs={"aspect": query_type},
                outputs={"status": "preferences_returned"},
            )
            chronicle.add_crystal(trace)

        assert len(chronicle.get_agent_crystals("K-gent")) == 3


class TestPersistentPersona:
    """Test K-gent × D-gent integration (persistent persona)."""

    @pytest.mark.asyncio
    async def test_persona_persistence(self, tmp_path):
        """Test persistent persona state."""
        path = tmp_path / "persona.json"

        # Create persona with custom state
        initial_state = PersonaState(
            seed=PersonaSeed(name="TestKent"),
            current_focus="testing",
        )

        agent = PersistentPersonaAgent(
            path=path,
            initial_state=initial_state,
        )

        # Have dialogue
        result = await agent.invoke(
            DialogueInput(message="Testing persistence", mode=DialogueMode.REFLECT)
        )
        assert result.response

        # Create new agent from same path
        agent2 = PersistentPersonaAgent(path=path)
        await agent2.load_state()

        # State should be preserved
        assert agent2.state.current_focus == "testing"

    @pytest.mark.asyncio
    async def test_preference_evolution(self, tmp_path):
        """Test tracking preference changes over time."""
        path = tmp_path / "persona_evolution.json"

        agent = PersistentPersonaAgent(path=path)

        # Update preferences
        agent.update_preference(
            category="communication",
            key="style",
            value="very concise",
            confidence=0.95,
            source="explicit",
        )

        # Save
        await agent.save_state()

        # Verify history
        history = await agent.get_evolution_history(limit=5)
        # Should have at least initial state
        assert isinstance(history, list)


class TestKgentCrossAgentIntegration:
    """Test K-gent integration with other agents."""

    @pytest.mark.asyncio
    async def test_kgent_provides_personalization(self):
        """Test that K-gent provides personalization for other agents."""
        query_agent = query_persona()

        # Query preferences for robin agent
        robin_prefs = await query_agent.invoke(
            PersonaQuery(aspect="all", for_agent="robin")
        )

        # Should have robin-specific style
        assert robin_prefs.suggested_style
        assert any(
            "direct" in style.lower() or "uncertain" in style.lower()
            for style in robin_prefs.suggested_style
        )

    @pytest.mark.asyncio
    async def test_kgent_state_access(self):
        """Test that K-gent state is accessible."""
        state = PersonaState(
            seed=PersonaSeed(
                name="TestUser",
                roles=["developer", "designer"],
            ),
            current_focus="testing",
            recent_interests=["testing", "quality"],
        )

        agent = KgentAgent(state=state)

        # State should be accessible
        assert agent.state.seed.name == "TestUser"
        assert "developer" in agent.state.seed.roles
        assert agent.state.current_focus == "testing"


class TestKgentMaybe:
    """Test K-gent's Maybe monad for graceful degradation."""

    def test_maybe_just(self):
        """Test Maybe.just creation and value extraction."""
        from agents.k.persona import Maybe

        maybe = Maybe.just(42)
        assert maybe.is_just
        assert not maybe.is_nothing
        assert maybe.value_or(0) == 42

    def test_maybe_nothing(self):
        """Test Maybe.nothing creation."""
        from agents.k.persona import Maybe

        maybe = Maybe.nothing("No value available")
        assert not maybe.is_just
        assert maybe.is_nothing
        assert maybe.value_or(0) == 0
        assert maybe.error == "No value available"

    def test_maybe_map(self):
        """Test Maybe.map for transformation."""
        from agents.k.persona import Maybe

        maybe = Maybe.just(21)
        result = maybe.map(lambda x: x * 2)
        assert result.is_just
        assert result.value_or(0) == 42

    def test_maybe_map_nothing(self):
        """Test Maybe.map on Nothing propagates."""
        from agents.k.persona import Maybe

        maybe = Maybe.nothing("No value")
        result = maybe.map(lambda x: x * 2)
        assert result.is_nothing

    @pytest.mark.asyncio
    async def test_safe_query_failure(self):
        """Test safe query with uninitialized state."""
        # Create agent with minimal state
        agent = PersonaQueryAgent(state=None)
        # Should still work with defaults
        result = await agent.invoke(PersonaQuery(aspect="all"))
        assert isinstance(result, PersonaResponse)


class TestKgentComposition:
    """Test K-gent composition patterns."""

    @pytest.mark.asyncio
    async def test_kgent_as_morphism(self):
        """Test K-gent follows agent morphism pattern."""
        agent = kgent()

        # K-gent is a morphism: DialogueInput → DialogueOutput
        assert hasattr(agent, "invoke")
        assert hasattr(agent, "name")
        assert agent.name == "K-gent"

        result = await agent.invoke(
            DialogueInput(message="Test", mode=DialogueMode.REFLECT)
        )
        assert isinstance(result, DialogueOutput)

    @pytest.mark.asyncio
    async def test_query_agent_as_morphism(self):
        """Test PersonaQueryAgent follows agent morphism pattern."""
        agent = query_persona()

        # PersonaQueryAgent is a morphism: PersonaQuery → PersonaResponse
        assert hasattr(agent, "invoke")
        assert agent.name == "PersonaQuery"

        result = await agent.invoke(PersonaQuery(aspect="all"))
        assert isinstance(result, PersonaResponse)

    @pytest.mark.asyncio
    async def test_dialogue_modes_complete(self):
        """Test all dialogue modes are implemented."""
        agent = kgent()

        for mode in DialogueMode:
            result = await agent.invoke(
                DialogueInput(message=f"Test {mode.value}", mode=mode)
            )
            assert result.mode == mode
            assert result.response  # Each mode should generate a response
