"""
Tests for Builder's Workshop: The Five Builders.

Test categories:
1. Builder creation - Each builder has correct properties
2. Specialty tests - Builders know their specialty phase
3. Voice pattern tests - speak() prepends characteristic patterns
4. State transitions - builder_transition() works correctly
5. Handoff tests - Builders can hand off to each other
6. Integration with Citizen - Builders inherit Citizen behavior
7. Serialization tests - to_dict/from_dict round-trip
8. Workshop team tests - All 5 builders collaborating

See: plans/agent-town/builders-workshop-chunk5.md
"""

from __future__ import annotations

import random

import pytest

from agents.town.builders import (
    ARCHITECTURE,
    BUILDER_POLYNOMIAL,
    CRAFTSMANSHIP,
    DISCOVERY,
    EXPERIMENTATION,
    ORCHESTRATION,
    SAGE_EIGENVECTORS,
    SAGE_VOICE_PATTERNS,
    SCOUT_EIGENVECTORS,
    SCOUT_VOICE_PATTERNS,
    SPARK_EIGENVECTORS,
    SPARK_VOICE_PATTERNS,
    STEADY_EIGENVECTORS,
    STEADY_VOICE_PATTERNS,
    SYNC_EIGENVECTORS,
    SYNC_VOICE_PATTERNS,
    Builder,
    BuilderInput,
    BuilderPhase,
    create_sage,
    create_scout,
    create_spark,
    create_steady,
    create_sync,
)
from agents.town.polynomial import CitizenPhase

# =============================================================================
# Fixtures
# =============================================================================


@pytest.fixture
def sage() -> Builder:
    """Create a Sage builder for testing."""
    return create_sage("Ada")


@pytest.fixture
def spark() -> Builder:
    """Create a Spark builder for testing."""
    return create_spark("Turing")


@pytest.fixture
def steady() -> Builder:
    """Create a Steady builder for testing."""
    return create_steady("Knuth")


@pytest.fixture
def scout() -> Builder:
    """Create a Scout builder for testing."""
    return create_scout("Curie")


@pytest.fixture
def sync() -> Builder:
    """Create a Sync builder for testing."""
    return create_sync("Grace")


@pytest.fixture
def workshop_team(
    sage: Builder, spark: Builder, steady: Builder, scout: Builder, sync: Builder
) -> list[Builder]:
    """Create a full workshop team."""
    return [sage, spark, steady, scout, sync]


# =============================================================================
# Builder Creation Tests
# =============================================================================


class TestBuilderCreation:
    """Test that each builder is created with correct properties."""

    def test_sage_creation(self, sage: Builder) -> None:
        """Sage has correct properties."""
        assert sage.name == "Ada"
        assert sage.archetype == "Sage"
        assert sage.region == "workshop"
        assert sage.cosmotechnics == ARCHITECTURE
        assert sage.specialty == BuilderPhase.DESIGNING
        assert sage.voice_patterns == SAGE_VOICE_PATTERNS
        assert sage.eigenvectors == SAGE_EIGENVECTORS

    def test_spark_creation(self, spark: Builder) -> None:
        """Spark has correct properties."""
        assert spark.name == "Turing"
        assert spark.archetype == "Spark"
        assert spark.cosmotechnics == EXPERIMENTATION
        assert spark.specialty == BuilderPhase.PROTOTYPING
        assert spark.voice_patterns == SPARK_VOICE_PATTERNS
        assert spark.eigenvectors == SPARK_EIGENVECTORS

    def test_steady_creation(self, steady: Builder) -> None:
        """Steady has correct properties."""
        assert steady.name == "Knuth"
        assert steady.archetype == "Steady"
        assert steady.cosmotechnics == CRAFTSMANSHIP
        assert steady.specialty == BuilderPhase.REFINING
        assert steady.voice_patterns == STEADY_VOICE_PATTERNS
        assert steady.eigenvectors == STEADY_EIGENVECTORS

    def test_scout_creation(self, scout: Builder) -> None:
        """Scout has correct properties."""
        assert scout.name == "Curie"
        assert scout.archetype == "Scout"
        assert scout.cosmotechnics == DISCOVERY
        assert scout.specialty == BuilderPhase.EXPLORING
        assert scout.voice_patterns == SCOUT_VOICE_PATTERNS
        assert scout.eigenvectors == SCOUT_EIGENVECTORS

    def test_sync_creation(self, sync: Builder) -> None:
        """Sync has correct properties."""
        assert sync.name == "Grace"
        assert sync.archetype == "Sync"
        assert sync.cosmotechnics == ORCHESTRATION
        assert sync.specialty == BuilderPhase.INTEGRATING
        assert sync.voice_patterns == SYNC_VOICE_PATTERNS
        assert sync.eigenvectors == SYNC_EIGENVECTORS

    def test_custom_name_and_region(self) -> None:
        """Builders can have custom names and regions."""
        sage = create_sage("CustomSage", region="lab")
        assert sage.name == "CustomSage"
        assert sage.region == "lab"

    def test_all_builders_start_idle(self, workshop_team: list[Builder]) -> None:
        """All builders start in IDLE builder phase."""
        for builder in workshop_team:
            assert builder.builder_phase == BuilderPhase.IDLE


# =============================================================================
# Specialty Tests
# =============================================================================


class TestSpecialty:
    """Test that builders know their specialty phase."""

    def test_sage_specialty_is_designing(self, sage: Builder) -> None:
        """Sage's specialty is DESIGNING."""
        assert sage.specialty == BuilderPhase.DESIGNING
        assert sage.specialty_name == "Designing"

    def test_spark_specialty_is_prototyping(self, spark: Builder) -> None:
        """Spark's specialty is PROTOTYPING."""
        assert spark.specialty == BuilderPhase.PROTOTYPING
        assert spark.specialty_name == "Prototyping"

    def test_steady_specialty_is_refining(self, steady: Builder) -> None:
        """Steady's specialty is REFINING."""
        assert steady.specialty == BuilderPhase.REFINING
        assert steady.specialty_name == "Refining"

    def test_scout_specialty_is_exploring(self, scout: Builder) -> None:
        """Scout's specialty is EXPLORING."""
        assert scout.specialty == BuilderPhase.EXPLORING
        assert scout.specialty_name == "Exploring"

    def test_sync_specialty_is_integrating(self, sync: Builder) -> None:
        """Sync's specialty is INTEGRATING."""
        assert sync.specialty == BuilderPhase.INTEGRATING
        assert sync.specialty_name == "Integrating"

    def test_is_in_specialty_false_when_idle(self, sage: Builder) -> None:
        """Builder not in specialty when IDLE."""
        assert not sage.is_in_specialty

    def test_is_in_specialty_true_when_in_specialty_phase(self, sage: Builder) -> None:
        """Builder is in specialty when in their specialty phase."""
        # Move sage to DESIGNING via handoff
        sage.builder_transition(
            BuilderInput.handoff(
                from_builder="Scout",
                to_builder="Sage",
                message="Design this",
            )
        )
        assert sage.builder_phase == BuilderPhase.DESIGNING
        assert sage.is_in_specialty


# =============================================================================
# Voice Pattern Tests
# =============================================================================


class TestVoicePatterns:
    """Test that speak() prepends characteristic voice patterns."""

    def test_sage_speak_prepends_pattern(self, sage: Builder) -> None:
        """Sage speak prepends a sage voice pattern."""
        random.seed(42)
        speech = sage.speak("we need authentication")
        assert any(pattern in speech for pattern in SAGE_VOICE_PATTERNS)
        assert "we need authentication" in speech

    def test_spark_speak_prepends_pattern(self, spark: Builder) -> None:
        """Spark speak prepends a spark voice pattern."""
        random.seed(42)
        speech = spark.speak("we could try WebSockets")
        assert any(pattern in speech for pattern in SPARK_VOICE_PATTERNS)
        assert "we could try WebSockets" in speech

    def test_steady_speak_prepends_pattern(self, steady: Builder) -> None:
        """Steady speak prepends a steady voice pattern."""
        random.seed(42)
        speech = steady.speak("the tests are passing")
        assert any(pattern in speech for pattern in STEADY_VOICE_PATTERNS)
        assert "the tests are passing" in speech

    def test_scout_speak_prepends_pattern(self, scout: Builder) -> None:
        """Scout speak prepends a scout voice pattern."""
        random.seed(42)
        speech = scout.speak("there's a library for this")
        assert any(pattern in speech for pattern in SCOUT_VOICE_PATTERNS)
        assert "there's a library for this" in speech

    def test_sync_speak_prepends_pattern(self, sync: Builder) -> None:
        """Sync speak prepends a sync voice pattern."""
        random.seed(42)
        speech = sync.speak("we're ready to merge")
        assert any(pattern in speech for pattern in SYNC_VOICE_PATTERNS)
        assert "we're ready to merge" in speech

    def test_speak_without_patterns_returns_content_unchanged(self) -> None:
        """Builder with no voice patterns returns content unchanged."""
        builder = Builder(
            name="Silent",
            archetype="Silent",
            region="workshop",
            voice_patterns=(),
        )
        assert builder.speak("hello") == "hello"


# =============================================================================
# State Transition Tests
# =============================================================================


class TestStateTransitions:
    """Test builder state transitions."""

    def test_start_task_moves_to_exploring(self, sage: Builder) -> None:
        """Starting a task moves builder to EXPLORING."""
        output = sage.start_task("add authentication")
        assert sage.builder_phase == BuilderPhase.EXPLORING
        assert output.success
        assert "authentication" in output.message

    def test_continue_work_stays_in_phase(self, sage: Builder) -> None:
        """Continue work keeps builder in current phase."""
        sage.start_task("design API")
        initial_phase = sage.builder_phase
        output = sage.continue_work("still working")
        assert sage.builder_phase == initial_phase
        assert output.success

    def test_complete_work_returns_to_idle(self, sage: Builder) -> None:
        """Complete work returns builder to IDLE."""
        sage.start_task("design API")
        output = sage.complete_work(artifact={"schema": "..."}, summary="API designed")
        assert sage.builder_phase == BuilderPhase.IDLE
        assert output.success
        assert "API designed" in output.message

    def test_builder_rest_returns_to_idle(self, sage: Builder) -> None:
        """Builder rest returns to IDLE."""
        sage.start_task("design API")
        output = sage.builder_rest()
        assert sage.builder_phase == BuilderPhase.IDLE
        assert output.success

    def test_query_user_stays_in_phase(self, sage: Builder) -> None:
        """Query user keeps builder in current phase."""
        sage.start_task("design API")
        initial_phase = sage.builder_phase
        output = sage.query_user("REST or GraphQL?")
        assert sage.builder_phase == initial_phase
        assert output.success
        assert "REST or GraphQL?" in output.message

    def test_receive_response_stays_in_phase(self, sage: Builder) -> None:
        """Receive response keeps builder in current phase."""
        sage.start_task("design API")
        sage.query_user("REST or GraphQL?")
        initial_phase = sage.builder_phase
        output = sage.receive_response("REST please")
        assert sage.builder_phase == initial_phase
        assert output.success


# =============================================================================
# Handoff Tests
# =============================================================================


class TestHandoffs:
    """Test builder handoffs."""

    def test_handoff_to_sage_moves_to_designing(self, scout: Builder, sage: Builder) -> None:
        """Handoff to Sage moves to DESIGNING phase."""
        scout.start_task("research auth")
        output = scout.handoff_to(sage, artifact={"research": "..."}, message="Ready to design")
        assert scout.builder_phase == BuilderPhase.DESIGNING
        assert output.success
        assert "Sage" in output.message

    def test_handoff_to_spark_moves_to_prototyping(self, sage: Builder, spark: Builder) -> None:
        """Handoff to Spark moves to PROTOTYPING phase."""
        sage.builder_transition(BuilderInput.handoff(from_builder="Scout", to_builder="Sage"))
        output = sage.handoff_to(spark, artifact={"design": "..."})
        assert sage.builder_phase == BuilderPhase.PROTOTYPING
        assert output.success

    def test_handoff_to_steady_moves_to_refining(self, spark: Builder, steady: Builder) -> None:
        """Handoff to Steady moves to REFINING phase."""
        spark.builder_transition(BuilderInput.handoff(from_builder="Sage", to_builder="Spark"))
        output = spark.handoff_to(steady, artifact={"prototype": "..."})
        assert spark.builder_phase == BuilderPhase.REFINING
        assert output.success

    def test_handoff_to_sync_moves_to_integrating(self, steady: Builder, sync: Builder) -> None:
        """Handoff to Sync moves to INTEGRATING phase."""
        steady.builder_transition(BuilderInput.handoff(from_builder="Spark", to_builder="Steady"))
        output = steady.handoff_to(sync, artifact={"refined": "..."})
        assert steady.builder_phase == BuilderPhase.INTEGRATING
        assert output.success

    def test_handoff_chain_follows_natural_flow(self, workshop_team: list[Builder]) -> None:
        """Full handoff chain follows natural flow."""
        scout, sage, spark, steady, sync = (
            workshop_team[3],  # Scout
            workshop_team[0],  # Sage
            workshop_team[1],  # Spark
            workshop_team[2],  # Steady
            workshop_team[4],  # Sync
        )

        # Scout starts
        scout.start_task("add auth")
        assert scout.builder_phase == BuilderPhase.EXPLORING

        # Scout → Sage
        scout.handoff_to(sage)
        assert scout.builder_phase == BuilderPhase.DESIGNING  # type: ignore[comparison-overlap]

        # Simulate handoff chain (each builder transitions the previous)
        # Sage → Spark
        output = sage.builder_transition(
            BuilderInput.handoff(from_builder="Sage", to_builder="Spark")
        )
        assert sage.builder_phase == BuilderPhase.PROTOTYPING

        # Spark → Steady
        output = spark.builder_transition(
            BuilderInput.handoff(from_builder="Spark", to_builder="Steady")
        )
        assert spark.builder_phase == BuilderPhase.REFINING

        # Steady → Sync
        output = steady.builder_transition(
            BuilderInput.handoff(from_builder="Steady", to_builder="Sync")
        )
        assert steady.builder_phase == BuilderPhase.INTEGRATING


# =============================================================================
# Citizen Integration Tests
# =============================================================================


class TestCitizenIntegration:
    """Test that Builder inherits Citizen behavior."""

    def test_builder_has_citizen_phase(self, sage: Builder) -> None:
        """Builder has citizen phase (from Citizen)."""
        assert sage.phase == CitizenPhase.IDLE
        assert hasattr(sage, "_phase")

    def test_builder_has_eigenvectors(self, sage: Builder) -> None:
        """Builder has eigenvectors (from Citizen)."""
        assert sage.eigenvectors.warmth == 0.7
        assert sage.eigenvectors.patience == 0.9

    def test_builder_has_memory(self, sage: Builder) -> None:
        """Builder has memory agent (from Citizen)."""
        assert sage.memory is not None

    def test_builder_has_relationships(self, sage: Builder) -> None:
        """Builder has relationships dict (from Citizen)."""
        assert isinstance(sage.relationships, dict)
        sage.update_relationship("test-id", 0.5)
        assert sage.get_relationship("test-id") == 0.5

    def test_builder_can_transition_citizen_phase(self, sage: Builder) -> None:
        """Builder can use citizen transitions."""
        output = sage.work("designing architecture", 120)
        assert sage.phase == CitizenPhase.WORKING
        assert output.success

    def test_builder_has_nphase_state(self, sage: Builder) -> None:
        """Builder has N-Phase state (from Citizen)."""
        assert sage.nphase_state is not None
        from protocols.nphase.operad import NPhase

        assert sage.nphase_phase == NPhase.SENSE

    def test_builder_can_advance_nphase(self, sage: Builder) -> None:
        """Builder can advance N-Phase."""
        from protocols.nphase.operad import NPhase

        record = sage.advance_nphase(NPhase.ACT, payload={"action": "design"})
        assert record["to"] == "ACT"
        assert sage.nphase_phase == NPhase.ACT


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Test builder serialization."""

    def test_to_dict_includes_builder_data(self, sage: Builder) -> None:
        """to_dict includes builder-specific data."""
        data = sage.to_dict()
        assert "builder" in data
        assert data["builder"]["phase"] == "IDLE"
        assert data["builder"]["specialty"] == "DESIGNING"
        assert "voice_patterns" in data["builder"]

    def test_from_dict_restores_builder(self, sage: Builder) -> None:
        """from_dict restores builder correctly."""
        sage.start_task("test task")
        data = sage.to_dict()
        restored = Builder.from_dict(data)

        assert restored.name == sage.name
        assert restored.archetype == sage.archetype
        assert restored.specialty == sage.specialty
        assert restored.builder_phase == sage.builder_phase
        assert restored.cosmotechnics.name == sage.cosmotechnics.name

    def test_manifest_includes_builder_at_lod_1(self, sage: Builder) -> None:
        """manifest() includes builder data at LOD 1+."""
        manifest = sage.manifest(lod=1)
        assert "builder" in manifest
        assert manifest["builder"]["specialty"] == "DESIGNING"

    def test_manifest_includes_voice_patterns_at_lod_2(self, sage: Builder) -> None:
        """manifest() includes voice patterns at LOD 2+."""
        manifest = sage.manifest(lod=2)
        assert "voice_patterns" in manifest["builder"]


# =============================================================================
# Cosmotechnics Tests
# =============================================================================


class TestCosmotechnics:
    """Test builder cosmotechnics."""

    def test_architecture_cosmotechnics(self) -> None:
        """ARCHITECTURE cosmotechnics has correct properties."""
        assert ARCHITECTURE.name == "architecture"
        assert ARCHITECTURE.metaphor == "Life is architecture"
        assert "blueprints" in ARCHITECTURE.opacity_statement

    def test_experimentation_cosmotechnics(self) -> None:
        """EXPERIMENTATION cosmotechnics has correct properties."""
        assert EXPERIMENTATION.name == "experimentation"
        assert EXPERIMENTATION.metaphor == "Life is experimentation"
        assert "experiments" in EXPERIMENTATION.opacity_statement

    def test_craftsmanship_cosmotechnics(self) -> None:
        """CRAFTSMANSHIP cosmotechnics has correct properties."""
        assert CRAFTSMANSHIP.name == "craftsmanship"
        assert CRAFTSMANSHIP.metaphor == "Life is craftsmanship"
        assert "details" in CRAFTSMANSHIP.opacity_statement

    def test_discovery_cosmotechnics(self) -> None:
        """DISCOVERY cosmotechnics has correct properties."""
        assert DISCOVERY.name == "discovery"
        assert DISCOVERY.metaphor == "Life is discovery"
        assert "territories" in DISCOVERY.opacity_statement

    def test_orchestration_cosmotechnics(self) -> None:
        """ORCHESTRATION cosmotechnics has correct properties."""
        assert ORCHESTRATION.name == "orchestration"
        assert ORCHESTRATION.metaphor == "Life is orchestration"
        assert "rhythms" in ORCHESTRATION.opacity_statement


# =============================================================================
# Eigenvector Tests
# =============================================================================


class TestEigenvectors:
    """Test builder eigenvector profiles."""

    def test_sage_eigenvectors_high_patience(self) -> None:
        """Sage has high patience."""
        assert SAGE_EIGENVECTORS.patience == 0.9

    def test_spark_eigenvectors_high_creativity(self) -> None:
        """Spark has very high creativity."""
        assert SPARK_EIGENVECTORS.creativity == 0.95

    def test_spark_eigenvectors_low_patience(self) -> None:
        """Spark has low patience."""
        assert SPARK_EIGENVECTORS.patience == 0.3

    def test_steady_eigenvectors_high_resilience(self) -> None:
        """Steady has high resilience."""
        assert STEADY_EIGENVECTORS.resilience == 0.9

    def test_scout_eigenvectors_high_curiosity(self) -> None:
        """Scout has very high curiosity."""
        assert SCOUT_EIGENVECTORS.curiosity == 0.95

    def test_sync_eigenvectors_high_warmth(self) -> None:
        """Sync has very high warmth."""
        assert SYNC_EIGENVECTORS.warmth == 0.9

    def test_eigenvectors_are_bounded(self) -> None:
        """All eigenvector values are in [0, 1]."""
        for eigenvectors in [
            SAGE_EIGENVECTORS,
            SPARK_EIGENVECTORS,
            STEADY_EIGENVECTORS,
            SCOUT_EIGENVECTORS,
            SYNC_EIGENVECTORS,
        ]:
            for key, value in eigenvectors.to_dict().items():
                assert 0.0 <= value <= 1.0, f"{key} out of bounds: {value}"


# =============================================================================
# Workshop Team Tests
# =============================================================================


class TestWorkshopTeam:
    """Test all 5 builders working together."""

    def test_all_builders_have_unique_specialties(self, workshop_team: list[Builder]) -> None:
        """All builders have unique specialty phases."""
        specialties = [b.specialty for b in workshop_team]
        assert len(set(specialties)) == 5

    def test_all_builders_have_unique_cosmotechnics(self, workshop_team: list[Builder]) -> None:
        """All builders have unique cosmotechnics."""
        cosmotechnics = [b.cosmotechnics.name for b in workshop_team]
        assert len(set(cosmotechnics)) == 5

    def test_all_builders_have_unique_archetypes(self, workshop_team: list[Builder]) -> None:
        """All builders have unique archetypes."""
        archetypes = [b.archetype for b in workshop_team]
        assert len(set(archetypes)) == 5

    def test_eigenvector_diversity(self, workshop_team: list[Builder]) -> None:
        """Builders have diverse eigenvector profiles."""
        # Check that no two builders have identical eigenvectors
        for i, b1 in enumerate(workshop_team):
            for b2 in workshop_team[i + 1 :]:
                drift = b1.eigenvectors.drift(b2.eigenvectors)
                assert drift > 0.1, f"{b1.archetype} and {b2.archetype} too similar"

    def test_team_can_collaborate_on_task(self, workshop_team: list[Builder]) -> None:
        """Team can collaborate through the full development cycle."""
        scout, sage, spark, steady, sync = (
            workshop_team[3],  # Scout
            workshop_team[0],  # Sage
            workshop_team[1],  # Spark
            workshop_team[2],  # Steady
            workshop_team[4],  # Sync
        )

        # 1. Scout explores
        scout.start_task("implement user dashboard")
        assert scout.builder_phase == BuilderPhase.EXPLORING
        scout.continue_work("Found existing patterns in codebase")

        # 2. Scout hands off to Sage
        scout.handoff_to(sage, artifact={"research": "patterns found"})

        # 3. Sage designs
        sage.builder_transition(BuilderInput.handoff(from_builder="Scout", to_builder="Sage"))
        assert sage.builder_phase == BuilderPhase.DESIGNING
        sage.continue_work("Designing component architecture")

        # 4. Sage hands off to Spark
        sage.handoff_to(spark, artifact={"design": "component arch"})

        # 5. Spark prototypes
        spark.builder_transition(BuilderInput.handoff(from_builder="Sage", to_builder="Spark"))
        assert spark.builder_phase == BuilderPhase.PROTOTYPING
        spark.continue_work("Quick prototype with React")

        # 6. Spark hands off to Steady
        spark.handoff_to(steady, artifact={"prototype": "MVP working"})

        # 7. Steady refines
        steady.builder_transition(BuilderInput.handoff(from_builder="Spark", to_builder="Steady"))
        assert steady.builder_phase == BuilderPhase.REFINING
        steady.continue_work("Adding tests, fixing edge cases")

        # 8. Steady hands off to Sync
        steady.handoff_to(sync, artifact={"refined": "production ready"})

        # 9. Sync integrates
        sync.builder_transition(BuilderInput.handoff(from_builder="Steady", to_builder="Sync"))
        assert sync.builder_phase == BuilderPhase.INTEGRATING
        output = sync.complete_work(summary="Dashboard shipped!")

        assert output.success
        assert sync.builder_phase == BuilderPhase.IDLE  # type: ignore[comparison-overlap]


# =============================================================================
# Repr Tests
# =============================================================================


class TestRepr:
    """Test builder string representation."""

    def test_builder_repr(self, sage: Builder) -> None:
        """Builder has informative repr."""
        repr_str = repr(sage)
        assert "Builder" in repr_str
        assert "Ada" in repr_str
        assert "Sage" in repr_str
        assert "IDLE" in repr_str

    def test_builder_repr_shows_current_phase(self, sage: Builder) -> None:
        """Builder repr shows current builder phase."""
        sage.start_task("test")
        repr_str = repr(sage)
        assert "EXPLORING" in repr_str
