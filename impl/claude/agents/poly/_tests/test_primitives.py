"""
Tests for Polynomial Primitives.

These tests verify:
1. All 17 primitives are registered
2. Each primitive has valid state/transition structure
3. Bootstrap primitives compose correctly
4. Perception primitives handle observer-dependent behavior
5. Entropy primitives interface with void.*
6. Memory primitives (D-gent) handle persistence
7. Teleological primitives (E-gent, N-gent) handle evolution and narrative
"""

import pytest
from agents.poly import (
    # Primitives
    COMPOSE,
    CONTRADICT,
    DEFINE,
    EVOLVE,
    FIX,
    FORGET,
    GROUND,
    ID,
    JUDGE,
    LENS,
    MANIFEST,
    NARRATE,
    PRIMITIVES,
    REMEMBER,
    SIP,
    SUBLATE,
    TITHE,
    WITNESS,
    # Types - Bootstrap
    Antithesis,
    Claim,
    ContradictState,
    Definition,
    # Types - Entropy
    EntropyGrant,
    EntropyRequest,
    # Types - Teleological (E-gent, N-gent)
    Evolution,
    EvolveState,
    FixState,
    # Types - Memory (D-gent)
    ForgetState,
    GroundState,
    # Types - Perception
    Handle,
    JudgeState,
    Memory,
    MemoryResult,
    NarrateState,
    Offering,
    Organism,
    RememberState,
    SipState,
    Spec,
    Story,
    SublateState,
    Synthesis,
    Thesis,
    TitheState,
    Umwelt,
    Verdict,
    WitnessState,
    # Registry
    all_primitives,
    get_primitive,
    primitive_names,
)


class TestPrimitiveRegistry:
    """Tests for primitive registry."""

    def test_all_17_primitives_registered(self) -> None:
        """All 17 primitives are registered."""
        assert len(PRIMITIVES) == 17

    def test_primitive_names(self) -> None:
        """All primitive names are lowercase."""
        names = primitive_names()
        assert len(names) == 17
        for name in names:
            assert name.islower()

    def test_get_primitive_by_name(self) -> None:
        """Can retrieve primitive by name."""
        assert get_primitive("id") is ID
        assert get_primitive("ground") is GROUND
        assert get_primitive("judge") is JUDGE
        assert get_primitive("remember") is REMEMBER
        assert get_primitive("evolve") is EVOLVE

    def test_get_primitive_case_insensitive(self) -> None:
        """get_primitive is case insensitive."""
        assert get_primitive("ID") is ID
        assert get_primitive("Ground") is GROUND
        assert get_primitive("REMEMBER") is REMEMBER

    def test_get_primitive_unknown(self) -> None:
        """Unknown primitive returns None."""
        assert get_primitive("unknown") is None

    def test_all_primitives_list(self) -> None:
        """all_primitives returns list of all primitives."""
        primitives = all_primitives()
        assert len(primitives) == 17
        assert ID in primitives
        assert GROUND in primitives
        assert REMEMBER in primitives
        assert EVOLVE in primitives


class TestBootstrapPrimitives:
    """Tests for the 7 bootstrap primitives."""

    def test_id_passthrough(self) -> None:
        """ID passes input through unchanged."""
        state, output = ID.invoke("ready", "hello")
        assert state == "ready"
        assert output == "hello"

    def test_id_works_with_any_type(self) -> None:
        """ID works with any input type."""
        _, output = ID.invoke("ready", 42)
        assert output == 42

        _, output = ID.invoke("ready", {"key": "value"})
        assert output == {"key": "value"}

    def test_ground_grounded_state(self) -> None:
        """GROUND produces grounded result for valid input."""
        state, output = GROUND.invoke(GroundState.FLOATING, "some content")
        assert state == GroundState.GROUNDED
        assert output["grounded"] is True
        assert output["content"] == "some content"

    def test_ground_floating_state(self) -> None:
        """GROUND stays floating for empty input."""
        state, output = GROUND.invoke(GroundState.FLOATING, "")
        assert state == GroundState.FLOATING
        assert output["grounded"] is False

    def test_judge_accepts_claim(self) -> None:
        """JUDGE accepts claims with high confidence."""
        claim = Claim(content="test claim", confidence=0.8)
        state, verdict = JUDGE.invoke(JudgeState.DELIBERATING, claim)

        assert state == JudgeState.DECIDED
        assert isinstance(verdict, Verdict)
        assert verdict.accepted is True

    def test_judge_rejects_claim(self) -> None:
        """JUDGE rejects claims with low confidence."""
        claim = Claim(content="test claim", confidence=0.2)
        state, verdict = JUDGE.invoke(JudgeState.DELIBERATING, claim)

        assert state == JudgeState.DECIDED
        assert verdict.accepted is False

    def test_contradict_produces_antithesis(self) -> None:
        """CONTRADICT produces antithesis for thesis."""
        thesis = Thesis(content="All agents are pure functions")
        state, antithesis = CONTRADICT.invoke(ContradictState.SEEKING, thesis)

        assert state == ContradictState.FOUND
        assert isinstance(antithesis, Antithesis)
        assert antithesis.thesis == thesis
        assert "Contrary" in antithesis.contradiction

    def test_sublate_synthesizes(self) -> None:
        """SUBLATE synthesizes thesis and antithesis."""
        thesis = Thesis(content="Agents are functions")
        antithesis = Antithesis(thesis=thesis, contradiction="Agents have state")

        state, synthesis = SUBLATE.invoke(SublateState.ANALYZING, (thesis, antithesis))

        assert state == SublateState.SYNTHESIZED
        assert isinstance(synthesis, Synthesis)
        assert synthesis.thesis == thesis
        assert synthesis.antithesis == antithesis
        assert "Aufhebung" in synthesis.resolution

    def test_compose_identity_on_pairs(self) -> None:
        """COMPOSE is identity on pairs (actual composition in operad)."""
        state, output = COMPOSE.invoke("ready", ("a", "b"))
        assert output == ("a", "b")

    def test_fix_succeeds_with_value(self) -> None:
        """FIX succeeds when given non-None value."""
        state, output = FIX.invoke(FixState.TRYING, ("result", 0))
        assert state == FixState.SUCCEEDED
        assert output["succeeded"] is True
        assert output["value"] == "result"

    def test_fix_fails_after_retries(self) -> None:
        """FIX fails after too many retries."""
        state, output = FIX.invoke(FixState.TRYING, (None, 5))
        assert state == FixState.FAILED
        assert output["failed"] is True


class TestPerceptionPrimitives:
    """Tests for the 3 perception primitives."""

    def test_manifest_with_umwelt(self) -> None:
        """MANIFEST produces observer-dependent perception."""
        handle = Handle(path="world.house")
        umwelt = Umwelt(observer_type="architect")

        state, manifestation = MANIFEST.invoke("observing", (handle, umwelt))

        assert state == "observing"
        assert "[architect]" in manifestation.perception
        assert "world.house" in manifestation.perception

    def test_manifest_different_observers(self) -> None:
        """MANIFEST produces different results for different observers."""
        handle = Handle(path="concept.beauty")

        _, m1 = MANIFEST.invoke("observing", (handle, Umwelt(observer_type="artist")))
        _, m2 = MANIFEST.invoke("observing", (handle, Umwelt(observer_type="engineer")))

        assert "[artist]" in m1.perception
        assert "[engineer]" in m2.perception
        assert m1.perception != m2.perception

    def test_witness_records_trace(self) -> None:
        """WITNESS records events to trace."""
        state, trace = WITNESS.invoke(WitnessState.RECORDING, "event1")

        assert state == WitnessState.RECORDING
        assert "event1" in trace.events
        assert trace.timestamp > 0

    def test_witness_replay_command(self) -> None:
        """WITNESS enters replay mode on 'replay' command."""
        state, trace = WITNESS.invoke(WitnessState.RECORDING, "replay")
        assert state == WitnessState.REPLAYING

    def test_lens_passthrough(self) -> None:
        """LENS passes selector through (real impl extracts sub-agent)."""
        state, output = LENS.invoke("ready", "selector.path")
        assert output == "selector.path"


class TestEntropyPrimitives:
    """Tests for the 3 entropy primitives."""

    def test_sip_grants_entropy(self) -> None:
        """SIP grants entropy from the void."""
        request = EntropyRequest(amount=1.0)
        state, grant = SIP.invoke(SipState.THIRSTY, request)

        assert state == SipState.SATED
        assert isinstance(grant, EntropyGrant)
        assert 0 <= grant.value <= 1.0
        assert "void" in grant.source

    def test_sip_respects_amount(self) -> None:
        """SIP respects requested entropy amount."""
        small_request = EntropyRequest(amount=0.1)
        _, small_grant = SIP.invoke(SipState.THIRSTY, small_request)

        # Value should be scaled by amount
        assert small_grant.value <= 0.1

    def test_tithe_accepts_offering(self) -> None:
        """TITHE accepts offerings to the void."""
        offering = Offering(content="gratitude", gratitude_level=0.8)
        state, result = TITHE.invoke(TitheState.OWING, offering)

        assert state == TitheState.PAID
        assert result["tithed"] is True
        assert result["gratitude"] == 0.8

    def test_define_creates_definition(self) -> None:
        """DEFINE autopoietically creates new definition."""
        spec = Spec(
            name="NewAgent",
            signature="str -> int",
            behavior="count characters",
        )
        state, definition = DEFINE.invoke("creating", spec)

        assert state == "creating"
        assert isinstance(definition, Definition)
        assert definition.created is True
        assert "NewAgent" in definition.message


class TestPrimitiveComposition:
    """Tests for composing primitives."""

    def test_dialectic_pipeline(self) -> None:
        """Thesis → Contradict → Sublate composition."""
        from agents.poly import sequential

        # This would be: thesis >> contradict >> sublate
        # But we need type-compatible versions

        thesis = Thesis(content="Pure functions are sufficient")

        # Step 1: Contradict
        _, antithesis = CONTRADICT.invoke(ContradictState.SEEKING, thesis)

        # Step 2: Sublate
        _, synthesis = SUBLATE.invoke(SublateState.ANALYZING, (thesis, antithesis))

        assert isinstance(synthesis, Synthesis)
        assert synthesis.thesis == thesis

    def test_ground_then_judge(self) -> None:
        """Ground → Judge pipeline."""
        # Ground a claim
        _, grounded = GROUND.invoke(GroundState.FLOATING, "test content")

        # Create claim from grounded result
        claim = Claim(
            content=grounded["content"],
            confidence=0.9 if grounded["grounded"] else 0.1,
        )

        # Judge the claim
        _, verdict = JUDGE.invoke(JudgeState.DELIBERATING, claim)

        assert verdict.accepted is True  # High confidence grounded claim

    def test_sip_then_tithe(self) -> None:
        """Sip → Tithe: the gratitude loop."""
        # Sip from the void
        _, grant = SIP.invoke(SipState.THIRSTY, EntropyRequest(amount=0.5))

        # Tithe back with gratitude
        offering = Offering(content=grant, gratitude_level=grant.value)
        _, result = TITHE.invoke(TitheState.OWING, offering)

        assert result["tithed"] is True


class TestPrimitiveProperties:
    """Property-based tests for primitives."""

    def test_all_primitives_have_positions(self) -> None:
        """All primitives have non-empty position sets."""
        for name, primitive in PRIMITIVES.items():
            assert len(primitive.positions) > 0, f"{name} has no positions"

    def test_all_primitives_have_directions(self) -> None:
        """All primitives have directions function."""
        for name, primitive in PRIMITIVES.items():
            for pos in primitive.positions:
                # Should not raise
                dirs = primitive.directions(pos)
                assert dirs is not None, f"{name} directions returned None"

    def test_all_primitives_have_transition(self) -> None:
        """All primitives have transition function."""
        for name, primitive in PRIMITIVES.items():
            # All primitives should have a transition
            assert hasattr(primitive, "_transition"), f"{name} missing transition"

    def test_primitive_names_unique(self) -> None:
        """All primitive names are unique."""
        names = [p.name for p in all_primitives()]
        assert len(names) == len(set(names))


class TestMemoryPrimitives:
    """Tests for the 2 memory primitives (D-gent)."""

    def test_remember_stores_memory(self) -> None:
        """REMEMBER stores memory with key."""
        memory = Memory(key="test_key", content="test_content")
        state, result = REMEMBER.invoke(RememberState.IDLE, memory)

        assert state == RememberState.STORED
        assert isinstance(result, MemoryResult)
        assert result.success is True
        assert result.key == "test_key"
        assert result.content == "test_content"

    def test_remember_with_any_content(self) -> None:
        """REMEMBER works with various content types."""
        memory = Memory(key="dict_key", content={"nested": "data"})
        _, result = REMEMBER.invoke(RememberState.IDLE, memory)

        assert result.success is True
        assert result.content == {"nested": "data"}

    def test_forget_removes_memory(self) -> None:
        """FORGET removes memory by key."""
        state, result = FORGET.invoke(ForgetState.IDLE, "test_key")

        assert state == ForgetState.FORGOTTEN
        assert isinstance(result, MemoryResult)
        assert result.success is True
        assert result.key == "test_key"
        assert result.content is None

    def test_remember_forget_cycle(self) -> None:
        """REMEMBER then FORGET cycle."""
        # Remember
        memory = Memory(key="ephemeral", content="temporary data")
        _, remember_result = REMEMBER.invoke(RememberState.IDLE, memory)
        assert remember_result.success is True

        # Forget
        _, forget_result = FORGET.invoke(ForgetState.IDLE, "ephemeral")
        assert forget_result.success is True
        assert forget_result.key == "ephemeral"


class TestTeleologicalPrimitives:
    """Tests for the 2 teleological primitives (E-gent, N-gent)."""

    def test_evolve_mutates_organism(self) -> None:
        """EVOLVE applies mutation to organism."""
        organism = Organism(genome=(1.0, 2.0, 3.0), fitness=0.5, generation=0)
        state, evolution = EVOLVE.invoke(EvolveState.DORMANT, organism)

        assert state in (
            EvolveState.MUTATING,
            EvolveState.SELECTING,
            EvolveState.CONVERGED,
        )
        assert isinstance(evolution, Evolution)
        assert evolution.organism.generation == 1
        assert len(evolution.organism.genome) == 3

    def test_evolve_increments_generation(self) -> None:
        """EVOLVE increments generation count."""
        organism = Organism(genome=(0.5,), fitness=0.7, generation=5)
        _, evolution = EVOLVE.invoke(EvolveState.MUTATING, organism)

        assert evolution.organism.generation == 6

    def test_evolve_clamps_fitness(self) -> None:
        """EVOLVE keeps fitness in [0, 1] range."""
        organism = Organism(genome=(0.5,), fitness=0.99, generation=0)
        _, evolution = EVOLVE.invoke(EvolveState.DORMANT, organism)

        assert 0 <= evolution.organism.fitness <= 1

    def test_narrate_constructs_story(self) -> None:
        """NARRATE constructs story from events."""
        events = ("awakening", "journey", "return")
        state, story = NARRATE.invoke(NarrateState.LISTENING, events)

        assert state == NarrateState.TOLD
        assert isinstance(story, Story)
        assert len(story.events) == 3
        assert "3 moments" in story.title

    def test_narrate_single_event(self) -> None:
        """NARRATE handles single event gracefully."""
        events = ("solitary moment",)
        _, story = NARRATE.invoke(NarrateState.LISTENING, events)

        assert len(story.events) == 1
        assert story.narrator == "witness"

    def test_narrate_extracts_moral(self) -> None:
        """NARRATE extracts moral from first and last events."""
        events = ("beginning", "middle", "end")
        _, story = NARRATE.invoke(NarrateState.LISTENING, events)

        assert "beginning" in story.moral
        assert "end" in story.moral

    def test_evolve_narrate_composition(self) -> None:
        """EVOLVE then NARRATE: evolution as narrative."""
        # Evolve an organism
        organism = Organism(genome=(0.5, 0.5), fitness=0.5, generation=0)
        _, evolution1 = EVOLVE.invoke(EvolveState.DORMANT, organism)
        _, evolution2 = EVOLVE.invoke(EvolveState.MUTATING, evolution1.organism)
        _, evolution3 = EVOLVE.invoke(EvolveState.SELECTING, evolution2.organism)

        # Narrate the evolution as a story
        events = (
            f"Gen {evolution1.organism.generation}: {evolution1.message}",
            f"Gen {evolution2.organism.generation}: {evolution2.message}",
            f"Gen {evolution3.organism.generation}: {evolution3.message}",
        )
        _, story = NARRATE.invoke(NarrateState.LISTENING, events)

        assert "3 moments" in story.title
        assert story.narrator == "witness"
