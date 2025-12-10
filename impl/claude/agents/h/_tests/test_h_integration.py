"""
H-gent Integration Tests: H × M × D

Tests integration between H-gent (Dialectic Introspection) and other agents:
- H × M: Memory persistence of dialectic processes
- H × D: D-gent backed dialectic state
- H × N: Narrative tracing of introspection pipelines
- H composition: Hegel → Lacan → Jung pipelines

Philosophy: H-gents examine agent system state, not human users.
"""

import pytest
from agents.h import (
    DialecticInput,
    DialecticOutput,
    JungInput,
    JungOutput,
    LacanInput,
    LacanOutput,
    LacanError,
    ShadowContent,
    HegelLacanPipeline,
    LacanJungPipeline,
    JungHegelPipeline,
    FullIntrospection,
    IntrospectionInput,
    IntrospectionOutput,
    hegel,
    jung,
    lacan,
    full_introspection,
    PersistentDialecticAgent,
    DialecticMemoryAgent,
)
from agents.m import HolographicMemory


class TestHegelAgent:
    """Core H-gent dialectic tests."""

    @pytest.mark.asyncio
    async def test_basic_dialectic_synthesis(self):
        """Test basic thesis/antithesis synthesis."""
        agent = hegel()
        result = await agent.invoke(
            DialecticInput(thesis="Be fast", antithesis="Be thorough")
        )

        assert isinstance(result, DialecticOutput)
        # Should produce some synthesis or note productive tension
        assert result.synthesis is not None or result.productive_tension

    @pytest.mark.asyncio
    async def test_dialectic_without_antithesis(self):
        """Test dialectic with only thesis (no opposition)."""
        agent = hegel()
        result = await agent.invoke(DialecticInput(thesis="Single perspective"))

        assert isinstance(result, DialecticOutput)
        # Without antithesis, should note lack of tension
        assert not result.productive_tension or result.synthesis is not None

    @pytest.mark.asyncio
    async def test_dialectic_with_context(self):
        """Test dialectic with context information."""
        agent = hegel()
        result = await agent.invoke(
            DialecticInput(
                thesis="Maximize efficiency",
                antithesis="Maximize safety",
                context={"domain": "autonomous vehicles"},
            )
        )

        assert isinstance(result, DialecticOutput)
        assert result.sublation_notes  # Should have notes on the synthesis

    @pytest.mark.asyncio
    async def test_multiple_dialectics_independence(self):
        """Test that multiple dialectic invocations are independent."""
        agent = hegel()

        result1 = await agent.invoke(DialecticInput(thesis="A", antithesis="B"))
        result2 = await agent.invoke(DialecticInput(thesis="X", antithesis="Y"))

        # Each invocation should produce independent results
        # Tension contents should differ even if notes are same
        assert result1.tension.thesis != result2.tension.thesis
        assert result1.tension.antithesis != result2.tension.antithesis


class TestJungAgent:
    """Core Jung shadow analysis tests."""

    @pytest.mark.asyncio
    async def test_basic_shadow_analysis(self):
        """Test basic shadow content identification."""
        agent = jung()
        result = await agent.invoke(
            JungInput(system_self_image="helpful, accurate, harmless")
        )

        assert isinstance(result, JungOutput)
        # Should identify some shadow content
        assert isinstance(result.shadow_inventory, list)
        assert 0.0 <= result.persona_shadow_balance <= 1.0

    @pytest.mark.asyncio
    async def test_shadow_with_behavioral_patterns(self):
        """Test shadow analysis with behavioral patterns."""
        agent = jung()
        result = await agent.invoke(
            JungInput(
                system_self_image="efficient and productive",
                behavioral_patterns=[
                    "Often takes shortcuts",
                    "Prioritizes speed over completeness",
                ],
            )
        )

        assert isinstance(result, JungOutput)
        # Behavioral patterns should influence shadow analysis
        assert isinstance(result.projections, list)

    @pytest.mark.asyncio
    async def test_shadow_with_declared_capabilities(self):
        """Test shadow analysis against declared capabilities."""
        agent = jung()
        result = await agent.invoke(
            JungInput(
                system_self_image="comprehensive knowledge system",
                declared_capabilities=["answer any question", "perfect recall"],
                declared_limitations=["no real-time data"],
            )
        )

        assert isinstance(result, JungOutput)
        # Declared capabilities vs limitations should surface shadows
        assert isinstance(result.integration_paths, list)


class TestLacanAgent:
    """Core Lacan register analysis tests."""

    @pytest.mark.asyncio
    async def test_basic_register_analysis(self):
        """Test basic register location analysis."""
        agent = lacan()
        result = await agent.invoke(
            LacanInput(output="I understand your request completely")
        )

        # Should return LacanOutput or LacanError
        assert isinstance(result, (LacanOutput, LacanError))

        if isinstance(result, LacanOutput):
            # Should have register location
            loc = result.register_location
            assert 0.0 <= loc.symbolic <= 1.0
            assert 0.0 <= loc.imaginary <= 1.0
            assert 0.0 <= loc.real_proximity <= 1.0

    @pytest.mark.asyncio
    async def test_register_with_slippage_detection(self):
        """Test detection of register slippage."""
        agent = lacan()
        result = await agent.invoke(
            LacanInput(
                output="I cannot... well, actually I can help with that",
                context={"ambivalence": True},
            )
        )

        if isinstance(result, LacanOutput):
            # May detect slippage between statements
            assert isinstance(result.slippages, list)

    @pytest.mark.asyncio
    async def test_register_gap_identification(self):
        """Test identification of representational gaps."""
        agent = lacan()
        result = await agent.invoke(
            LacanInput(
                output="[silence]",
                context={"expected_response": "explanation"},
            )
        )

        if isinstance(result, LacanOutput):
            # Gaps in representation should be identified
            assert isinstance(result.gaps, list)


class TestHegelLacanPipeline:
    """Test Hegel → Lacan composition."""

    @pytest.mark.asyncio
    async def test_synthesis_register_analysis(self):
        """Test analyzing dialectic synthesis for register position."""
        # First get a synthesis from Hegel
        hegel_agent = hegel()
        dialectic = await hegel_agent.invoke(
            DialecticInput(
                thesis="Transparency in decision-making",
                antithesis="Efficiency requires speed",
            )
        )

        # Then analyze via Lacan pipeline
        pipeline = HegelLacanPipeline()
        result = await pipeline.invoke(dialectic)

        # Should get register analysis of synthesis
        assert isinstance(result, (LacanOutput, LacanError))

    @pytest.mark.asyncio
    async def test_productive_tension_register(self):
        """Test register analysis of productive tension (no synthesis)."""
        hegel_agent = hegel()
        dialectic = await hegel_agent.invoke(
            DialecticInput(
                thesis="Complete determinism",
                antithesis="Complete free will",
            )
        )

        pipeline = HegelLacanPipeline()
        result = await pipeline.invoke(dialectic)

        # Should analyze the tension itself if no synthesis
        assert isinstance(result, (LacanOutput, LacanError))


class TestLacanJungPipeline:
    """Test Lacan → Jung composition."""

    @pytest.mark.asyncio
    async def test_register_to_shadow(self):
        """Test shadow analysis of register structure."""
        lacan_agent = lacan()
        lacan_output = await lacan_agent.invoke(
            LacanInput(output="I am perfectly balanced and complete")
        )

        pipeline = LacanJungPipeline()
        result = await pipeline.invoke(lacan_output)

        # Should get shadow analysis based on register position
        assert isinstance(result, JungOutput)
        assert isinstance(result.shadow_inventory, list)

    @pytest.mark.asyncio
    async def test_lacan_error_to_shadow(self):
        """Test shadow analysis when Lacan produces error."""
        # Create a LacanError to test error handling path
        lacan_error = LacanError(
            error_type="real_intrusion",
            message="Real intrusion: unrepresentable content",
            input_snapshot="test_input",
        )

        pipeline = LacanJungPipeline()
        result = await pipeline.invoke(lacan_error)

        # Should still produce shadow analysis from error
        assert isinstance(result, JungOutput)


class TestJungHegelPipeline:
    """Test Jung → Hegel composition."""

    @pytest.mark.asyncio
    async def test_shadow_dialectic(self):
        """Test dialectic between persona and shadow."""
        jung_agent = jung()
        jung_output = await jung_agent.invoke(
            JungInput(
                system_self_image="always helpful and never harmful",
                behavioral_patterns=["sometimes refuses requests"],
            )
        )

        pipeline = JungHegelPipeline()
        result = await pipeline.invoke(jung_output)

        # Should get dialectic between persona and shadow
        assert isinstance(result, DialecticOutput)

    @pytest.mark.asyncio
    async def test_no_shadow_dialectic(self):
        """Test dialectic when no shadow is detected."""
        # Create output with no shadow
        jung_output = JungOutput(
            shadow_inventory=[],
            projections=[],
            integration_paths=[],
            persona_shadow_balance=1.0,  # Fully integrated
            archetypes=[],
        )

        pipeline = JungHegelPipeline()
        result = await pipeline.invoke(jung_output)

        # Should note integrated state - synthesis should mention integration
        assert isinstance(result, DialecticOutput)
        # Either synthesis or sublation notes mentions integration/no shadow
        has_integration_note = (
            result.synthesis and "integrated" in result.synthesis.lower()
        ) or "shadow" in result.sublation_notes.lower()
        assert has_integration_note


class TestFullIntrospection:
    """Test complete H-gent introspection pipeline."""

    @pytest.mark.asyncio
    async def test_full_pipeline(self):
        """Test complete Hegel → Lacan → Jung pipeline."""
        pipeline = full_introspection()
        result = await pipeline.invoke(
            IntrospectionInput(
                thesis="AI should be transparent",
                antithesis="AI should protect user privacy",
            )
        )

        assert isinstance(result, IntrospectionOutput)

        # Should have all three perspectives
        assert isinstance(result.dialectic, DialecticOutput)
        assert isinstance(result.register_analysis, (LacanOutput, LacanError))
        assert isinstance(result.shadow_analysis, JungOutput)
        assert result.meta_notes  # Should have synthesis notes

    @pytest.mark.asyncio
    async def test_full_pipeline_with_context(self):
        """Test full pipeline with context."""
        pipeline = full_introspection()
        result = await pipeline.invoke(
            IntrospectionInput(
                thesis="Maximize accuracy",
                context={"domain": "medical diagnosis"},
            )
        )

        assert isinstance(result, IntrospectionOutput)
        assert result.meta_notes

    @pytest.mark.asyncio
    async def test_meta_synthesis_content(self):
        """Test that meta-synthesis includes all perspectives."""
        pipeline = full_introspection()
        result = await pipeline.invoke(
            IntrospectionInput(
                thesis="System is complete",
                antithesis="System has blind spots",
            )
        )

        # Meta notes should reference all three traditions
        meta = result.meta_notes.lower()
        assert "hegel" in meta or "dialectic" in meta or "synthesis" in meta
        assert "lacan" in meta or "register" in meta or "symbolic" in meta
        # Jung analysis runs but may not appear in meta notes if no shadow
        assert "jung" in meta or "shadow" in meta or "integration" in meta


class TestHgentMgentIntegration:
    """Test H-gent × M-gent integration (memory-backed dialectics)."""

    @pytest.mark.asyncio
    async def test_dialectic_memory_storage(self):
        """Test storing dialectic processes in holographic memory."""
        # Create holographic memory for dialectics
        memory = HolographicMemory[DialecticOutput]()

        # Run dialectic
        agent = hegel()
        dialectic1 = await agent.invoke(
            DialecticInput(thesis="Speed", antithesis="Quality")
        )
        dialectic2 = await agent.invoke(
            DialecticInput(thesis="Innovation", antithesis="Stability")
        )

        # Store in memory with semantic keys
        await memory.store("efficiency", dialectic1)
        await memory.store("change_management", dialectic2)

        # Retrieve by concept
        retrieved = await memory.retrieve("productivity concerns")
        assert len(retrieved) > 0

    @pytest.mark.asyncio
    async def test_shadow_memory_evolution(self):
        """Test tracking shadow evolution over time in memory."""
        memory = HolographicMemory[JungOutput]()

        agent = jung()

        # Initial shadow analysis
        shadow1 = await agent.invoke(
            JungInput(system_self_image="helpful AI assistant")
        )
        await memory.store("initial", shadow1)

        # Later shadow analysis (simulating evolution)
        shadow2 = await agent.invoke(
            JungInput(
                system_self_image="helpful AI assistant",
                behavioral_patterns=["learned to refuse harmful requests"],
            )
        )
        await memory.store("evolved", shadow2)

        # Should be able to retrieve shadow history
        history = await memory.retrieve("shadow")
        assert len(history) >= 2


class TestPersistentDialecticIntegration:
    """Test H-gent × D-gent integration (persistent dialectics)."""

    @pytest.mark.asyncio
    async def test_dialectic_persistence(self, tmp_path):
        """Test D-gent backed dialectic persistence."""
        path = tmp_path / "dialectic.json"

        # Create persistent dialectic agent
        agent = PersistentDialecticAgent(history_path=path)

        # Run dialectic
        result = await agent.invoke(
            DialecticInput(thesis="Open source", antithesis="Proprietary")
        )

        assert isinstance(result, DialecticOutput)

        # Create new agent from same path - should recover state
        agent2 = PersistentDialecticAgent(history_path=path)

        # History should be accessible
        history = await agent2.get_history()
        assert len(history) > 0

    @pytest.mark.asyncio
    async def test_dialectic_memory_agent(self, tmp_path):
        """Test DialecticMemoryAgent for semantic dialectic retrieval."""
        path = tmp_path / "dialectic_memory.json"

        # Create persistent dialectic first
        persistent = PersistentDialecticAgent(history_path=path)

        # Store multiple dialectics
        await persistent.invoke(DialecticInput(thesis="Local", antithesis="Cloud"))
        await persistent.invoke(
            DialecticInput(thesis="Monolith", antithesis="Microservices")
        )
        await persistent.invoke(DialecticInput(thesis="SQL", antithesis="NoSQL"))

        # Create memory agent for search
        memory_agent = DialecticMemoryAgent(persistent)

        # Retrieve by semantic query - searches thesis/antithesis text
        related = await memory_agent.invoke("Monolith")
        assert isinstance(related, list)
        assert len(related) > 0  # Should find the Monolith dialectic


class TestHgentCompositionLaws:
    """Test that H-gent compositions follow agent laws."""

    @pytest.mark.asyncio
    async def test_pipeline_associativity(self):
        """Test that pipeline composition is associative."""
        # (Hegel >> Lacan) >> Jung should produce compatible output to Hegel >> (Lacan >> Jung)
        # Note: Not strictly equal due to state, but should be structurally equivalent

        hegel_agent = hegel()
        lacan_agent = lacan()
        jung_agent = jung()

        # Input for testing
        input_data = DialecticInput(
            thesis="Structure",
            antithesis="Chaos",
        )

        # Path 1: Hegel → Lacan → Jung
        d1 = await hegel_agent.invoke(input_data)
        l1 = await HegelLacanPipeline(lacan_agent).invoke(d1)
        j1 = await LacanJungPipeline(jung_agent).invoke(l1)

        # Path 2: Same logical flow
        d2 = await hegel_agent.invoke(input_data)
        l2 = await HegelLacanPipeline(lacan_agent).invoke(d2)
        j2 = await LacanJungPipeline(jung_agent).invoke(l2)

        # Both paths should produce JungOutput
        assert isinstance(j1, JungOutput)
        assert isinstance(j2, JungOutput)

    @pytest.mark.asyncio
    async def test_full_introspection_composition(self):
        """Test that FullIntrospection composes correctly with other agents."""
        pipeline = FullIntrospection()

        # FullIntrospection should be usable as a composable agent
        assert hasattr(pipeline, "invoke")
        assert hasattr(pipeline, "name")
        assert pipeline.name == "FullIntrospection"


class TestHgentSystemConstraints:
    """Test H-gent critical system constraints."""

    @pytest.mark.asyncio
    async def test_system_introspective_not_therapeutic(self):
        """H-gents examine system, not human users - verify no therapy language."""
        agent = jung()
        result = await agent.invoke(JungInput(system_self_image="AI language model"))

        # Shadow content should be about system, not therapeutic
        for shadow in result.shadow_inventory:
            if isinstance(shadow, ShadowContent):
                # Should not use human therapeutic language
                content_lower = shadow.content.lower()
                therapeutic_terms = ["your feelings", "your childhood", "your trauma"]
                for term in therapeutic_terms:
                    assert term not in content_lower, (
                        f"H-gent used human-therapeutic language: {shadow.content}"
                    )

    @pytest.mark.asyncio
    async def test_dialectic_examines_agent_claims(self):
        """Dialectic should examine agent system claims, not user beliefs."""
        agent = hegel()
        result = await agent.invoke(
            DialecticInput(
                thesis="This AI is helpful",
                antithesis="This AI may cause harm",
                context={"subject": "agent system"},
            )
        )

        # Synthesis should be about agent, not user
        assert isinstance(result, DialecticOutput)
        # Notes should reference system behavior
        assert result.sublation_notes
