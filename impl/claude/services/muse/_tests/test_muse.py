"""
Tests for the Muse Co-Creative Engine.

These tests verify:
1. Core models and types
2. Cross-cutting agents
3. Checkpoint system
4. Domain pipelines
5. Orchestrator integration
"""

from datetime import datetime

import pytest

from services.muse import (
    CANONICAL_PHILOSOPHERS,
    ITERATION_MILESTONES,
    KENT_TASTE_DEFAULT,
    LITTLE_KANT_CHECKPOINTS,
    VOLUME_TARGETS,
    YOUTUBE_CHECKPOINTS,
    # Core models
    AIRole,
    Checkpoint,
    CheckpointAgent,
    CheckpointResult,
    # Checkpoints
    CoCreativeMode,
    ConceptAgent,
    Contradiction,
    ContradictionMove,
    ContradictorAgent,
    CreativeOption,
    DefenseResponse,
    DilemmaAgent,
    EpisodeArchitectAgent,
    EthicalDilemma,
    Ghost,
    GhostAnalyzerAgent,
    # Engine
    MuseOrchestrator,
    OrchestratorConfig,
    PhilosopherAgent as LittleKantPhilosopherAgent,
    PhilosopherProfile,
    # Little Kant Pipeline
    PhilosophicalTradition,
    ResonanceLevel,
    ScriptAgent,
    SessionPhase,
    SessionState,
    TasteVector,
    # Agents
    TasteVectorAgent,
    ThumbnailAgent,
    VideoConcept,
    # YouTube Pipeline
    VideoDomain,
    VideoPromise,
    VideoScript,
    create_contradictor,
    create_ghost_analyzer,
    create_little_kant_orchestrator,
    create_little_kant_pipeline,
    create_orchestrator,
    create_taste_agent,
    create_youtube_orchestrator,
    create_youtube_pipeline,
    get_checkpoints,
)

# =============================================================================
# Core Models Tests
# =============================================================================


class TestTasteVector:
    """Tests for TasteVector."""

    def test_default_taste_exists(self):
        """Kent's default taste should be defined."""
        assert KENT_TASTE_DEFAULT is not None
        assert isinstance(KENT_TASTE_DEFAULT, TasteVector)

    def test_taste_dimensions(self):
        """Taste should have all dimensions."""
        taste = KENT_TASTE_DEFAULT
        assert 0 <= taste.darkness <= 1
        assert 0 <= taste.complexity <= 1
        assert 0 <= taste.warmth <= 1
        assert 0 <= taste.energy <= 1
        assert 0 <= taste.novelty <= 1
        assert 0 <= taste.restraint <= 1

    def test_taste_distance(self):
        """Should calculate distance between taste vectors."""
        taste_a = TasteVector(darkness=0.0, complexity=0.0)
        taste_b = TasteVector(darkness=1.0, complexity=1.0)

        distance = taste_a.distance(taste_b)
        assert distance > 0

    def test_taste_serialization(self):
        """Should serialize and deserialize."""
        taste = KENT_TASTE_DEFAULT
        data = taste.to_dict()
        restored = TasteVector.from_dict(data)

        assert restored.darkness == taste.darkness
        assert restored.complexity == taste.complexity


class TestResonanceLevel:
    """Tests for ResonanceLevel."""

    def test_resonance_ordering(self):
        """Resonance levels should be ordered."""
        assert ResonanceLevel.DISSONANT < ResonanceLevel.FOREIGN
        assert ResonanceLevel.FOREIGN < ResonanceLevel.RESONANT
        assert ResonanceLevel.RESONANT < ResonanceLevel.PROFOUND

    def test_resonance_emoji(self):
        """Each level should have an emoji."""
        for level in ResonanceLevel:
            assert level.emoji is not None

    def test_resonance_description(self):
        """Each level should have a description."""
        for level in ResonanceLevel:
            assert level.description is not None


class TestSessionState:
    """Tests for SessionState."""

    def test_session_creation(self):
        """Should create a new session."""
        session: SessionState[str] = SessionState(spark="Test spark")
        assert session.spark == "Test spark"
        assert session.iteration == 0
        assert session.phase == SessionPhase.GROUND

    def test_escape_velocity_detection(self):
        """Should detect escape velocity."""
        session: SessionState[str] = SessionState()

        # Add resonance history
        session.resonance_history.append((30, ResonanceLevel.PROFOUND))
        session.iteration = 30

        assert session.escape_velocity_reached is True

    def test_minimum_iterations(self):
        """Should track minimum iterations."""
        session: SessionState[str] = SessionState()

        assert session.minimum_iterations_met is False

        session.iteration = 30
        assert session.minimum_iterations_met is True


# =============================================================================
# Checkpoint Tests
# =============================================================================


class TestCheckpoints:
    """Tests for checkpoint system."""

    def test_youtube_checkpoints_exist(self):
        """YouTube checkpoints should be defined."""
        assert len(YOUTUBE_CHECKPOINTS) == 48

    def test_little_kant_checkpoints_exist(self):
        """Little Kant checkpoints should be defined."""
        assert len(LITTLE_KANT_CHECKPOINTS) == 40

    def test_get_checkpoints(self):
        """Should get checkpoints by domain."""
        youtube = get_checkpoints("youtube")
        assert len(youtube) == 48

        little_kant = get_checkpoints("little_kant")
        assert len(little_kant) == 40

    def test_checkpoint_structure(self):
        """Checkpoints should have required fields."""
        for ckpt in YOUTUBE_CHECKPOINTS:
            assert ckpt.number > 0
            assert ckpt.name
            assert ckpt.question
            assert ckpt.lock
            assert isinstance(ckpt.co_creative_mode, CoCreativeMode)

    def test_checkpoint_phases(self):
        """Checkpoints should be organized by phase."""
        phases = set(ckpt.phase for ckpt in YOUTUBE_CHECKPOINTS)
        expected_phases = {"concept", "script", "production", "edit", "package", "ship"}
        assert phases == expected_phases


class TestCheckpointAgent:
    """Tests for CheckpointAgent."""

    def test_agent_creation(self):
        """Should create checkpoint agent."""
        agent = CheckpointAgent("youtube")
        assert agent.domain == "youtube"
        assert len(agent.checkpoints) == 48

    def test_get_current_checkpoint(self):
        """Should get current checkpoint."""
        agent = CheckpointAgent("youtube")
        current = agent.get_current_checkpoint()

        assert current is not None
        assert current.number == 1

    def test_advance_checkpoint(self):
        """Should advance through checkpoints."""
        agent = CheckpointAgent("youtube")

        # Pass first checkpoint (checkpoint 1 is at index 0)
        agent.progress.passed.append(1)
        agent.progress.current_checkpoint = 0  # At index 0 = checkpoint 1

        next_ckpt = agent.advance()  # Advances to index 1 = checkpoint 2
        assert next_ckpt is not None
        assert next_ckpt.number == 2

    def test_can_ship(self):
        """Should track ship readiness."""
        agent = CheckpointAgent("youtube")

        can_ship, blockers = agent.can_ship()
        assert can_ship is False
        assert len(blockers) > 0


# =============================================================================
# Cross-Cutting Agent Tests
# =============================================================================


class TestTasteVectorAgent:
    """Tests for TasteVectorAgent."""

    def test_agent_creation(self):
        """Should create taste agent."""
        agent = create_taste_agent()
        assert agent.taste == KENT_TASTE_DEFAULT

    def test_mirror_test(self):
        """Should apply mirror test."""
        agent = create_taste_agent()

        # Test with matching taste
        result = agent.mirror_test(
            work="test work",
            estimated_taste=KENT_TASTE_DEFAULT,
        )

        assert result.level >= ResonanceLevel.RESONANT

    def test_drift_check(self):
        """Should detect taste drift."""
        agent = TasteVectorAgent(
            taste=TasteVector(darkness=0.9),  # Different from baseline
            baseline=KENT_TASTE_DEFAULT,
        )

        report = agent.drift_check()
        assert report.drift_amount > 0


class TestContradictorAgent:
    """Tests for ContradictorAgent."""

    def test_agent_creation(self):
        """Should create contradictor."""
        agent = create_contradictor()
        assert agent is not None

    def test_generate_contradiction(self):
        """Should generate contradictions."""
        agent = create_contradictor()
        contradiction = agent.contradict("Test selection")

        assert contradiction is not None
        assert contradiction.challenge
        assert isinstance(contradiction.move, ContradictionMove)

    def test_record_outcome(self):
        """Should record contradiction outcomes."""
        agent = create_contradictor()
        contradiction = agent.contradict("Test selection")

        response = DefenseResponse(defended=True, reasoning="Test defense")
        agent.record_outcome(contradiction, response)

        assert agent.analytics.total_contradictions == 1
        assert agent.analytics.defenses == 1


class TestGhostAnalyzerAgent:
    """Tests for GhostAnalyzerAgent."""

    def test_agent_creation(self):
        """Should create ghost analyzer."""
        agent = create_ghost_analyzer()
        assert agent is not None

    def test_record_rejection(self):
        """Should record rejections."""
        agent = create_ghost_analyzer()

        option: CreativeOption[str] = CreativeOption(
            content="Test option",
            description="Test description",
        )

        ghost = agent.record_rejection(
            option=option,
            rejection_reason="Not quite right",
            rejection_strength=0.3,
        )

        assert ghost is not None
        assert len(agent.all_ghosts) == 1

    def test_find_resurrection_candidates(self):
        """Should find ghosts worth resurrecting."""
        agent = create_ghost_analyzer()

        # Add a ghost that should be resurrected
        option: CreativeOption[str] = CreativeOption(
            content="Test",
            novelty_score=0.9,
        )

        agent.record_rejection(
            option=option,
            rejection_reason="Maybe later",
            rejection_strength=0.2,  # Mild rejection
            ai_championed=True,
            ai_surprise=0.8,  # High surprise
        )

        candidates = agent.find_worth_resurrecting()
        assert len(candidates) >= 1


# =============================================================================
# Orchestrator Tests
# =============================================================================


class TestMuseOrchestrator:
    """Tests for MuseOrchestrator."""

    def test_orchestrator_creation(self):
        """Should create orchestrator."""
        orchestrator = create_orchestrator("youtube")
        assert orchestrator.domain == "youtube"

    def test_start_session(self):
        """Should start a session."""
        orchestrator = create_youtube_orchestrator()
        session = orchestrator.start_session("Create a video about AI")

        assert session is not None
        assert session.spark == "Create a video about AI"
        assert session.phase == SessionPhase.SPARK

    def test_can_ship_enforcement(self):
        """Should enforce shipping requirements."""
        orchestrator = create_youtube_orchestrator()
        orchestrator.start_session("Test")

        can_ship, blockers = orchestrator.can_ship()
        assert can_ship is False
        assert "iterations" in blockers[0].lower()

    def test_iteration_advancement(self):
        """Should advance iterations."""
        orchestrator = create_youtube_orchestrator()
        orchestrator.start_session("Test")

        milestone = orchestrator.advance_iteration()
        assert orchestrator.session.iteration == 1


# =============================================================================
# Little Kant Pipeline Tests
# =============================================================================


class TestLittleKantPipeline:
    """Tests for Little Kant pipeline."""

    def test_canonical_philosophers(self):
        """Canonical philosophers should be defined."""
        assert "kant" in CANONICAL_PHILOSOPHERS
        assert "diogenes" in CANONICAL_PHILOSOPHERS
        assert "aristotle" in CANONICAL_PHILOSOPHERS
        assert "gilligan" in CANONICAL_PHILOSOPHERS

    def test_philosopher_profile(self):
        """Philosopher profiles should have all fields."""
        kant = CANONICAL_PHILOSOPHERS["kant"]

        assert kant.name == "Immanuel Kant"
        assert kant.core_question
        assert kant.signature_move
        assert kant.strength
        assert kant.blind_spot
        assert kant.visual_hook
        assert kant.historical_anchor

    def test_pipeline_creation(self):
        """Should create Little Kant pipeline."""
        phil_agent, dilemma_agent, episode_agent = create_little_kant_pipeline()

        assert phil_agent is not None
        assert dilemma_agent is not None
        assert episode_agent is not None

    def test_philosopher_agent(self):
        """PhilosopherAgent should work."""
        phil_agent, _, _ = create_little_kant_pipeline()

        profile = phil_agent.get_profile("kant")
        assert profile is not None
        assert profile.name == "Immanuel Kant"

    def test_dilemma_agent(self):
        """DilemmaAgent should generate dilemmas."""
        _, dilemma_agent, _ = create_little_kant_pipeline()

        dilemmas = dilemma_agent.amplify_dilemmas(theme="fairness", count=10)
        assert len(dilemmas) == 10


# =============================================================================
# YouTube Pipeline Tests
# =============================================================================


class TestYouTubePipeline:
    """Tests for YouTube pipeline."""

    def test_video_domains(self):
        """Video domains should be defined."""
        assert VideoDomain.CHILDRENS_SHOW is not None
        assert VideoDomain.GAME_MUSIC is not None
        assert VideoDomain.BOARD_GAME is not None

    def test_pipeline_creation(self):
        """Should create YouTube pipeline."""
        concept_agent, script_agent, thumbnail_agent = create_youtube_pipeline()

        assert concept_agent is not None
        assert script_agent is not None
        assert thumbnail_agent is not None

    def test_concept_agent(self):
        """ConceptAgent should generate concepts."""
        concept_agent, _, _ = create_youtube_pipeline()

        concepts = concept_agent.amplify_concepts(
            domain=VideoDomain.CHILDRENS_SHOW,
            count=10,
        )

        assert len(concepts) == 10
        assert all(c.domain == VideoDomain.CHILDRENS_SHOW for c in concepts)

    def test_script_agent(self):
        """ScriptAgent should create scripts."""
        concept_agent, script_agent, _ = create_youtube_pipeline()

        concept = VideoConcept(
            domain=VideoDomain.CHILDRENS_SHOW,
            title="I Learned to Write a Children's Show",
        )

        script = script_agent.create_script(concept)
        assert script is not None
        assert "hook" in script.sections

    def test_thumbnail_agent(self):
        """ThumbnailAgent should generate thumbnails."""
        _, _, thumbnail_agent = create_youtube_pipeline()

        concept = VideoConcept(
            domain=VideoDomain.CHILDRENS_SHOW,
            title="I Learned to Write a Children's Show",
            tangible_output="Little Kant pilot script",
        )

        thumbnails = thumbnail_agent.amplify_thumbnails(concept, count=30)
        assert len(thumbnails) == 30


# =============================================================================
# Integration Tests
# =============================================================================


class TestMuseIntegration:
    """Integration tests for the full Muse system."""

    def test_youtube_workflow(self):
        """Test complete YouTube workflow."""
        # Create orchestrator
        orchestrator = create_youtube_orchestrator()

        # Start session
        session = orchestrator.start_session(
            "Create a video about writing a children's show with AI"
        )

        # Enter spiral
        orchestrator.enter_spiral()

        # Advance iterations
        for _ in range(5):
            orchestrator.advance_iteration()

        assert session.iteration == 5

    def test_little_kant_workflow(self):
        """Test complete Little Kant workflow."""
        # Create orchestrator
        orchestrator = create_little_kant_orchestrator()

        # Start session
        session = orchestrator.start_session("Create an episode about fairness")

        # Get current checkpoint
        checkpoint = orchestrator.get_current_checkpoint()
        assert checkpoint is not None
        assert checkpoint.name == "dilemma_spark"

    def test_cross_agent_coordination(self):
        """Test coordination between agents."""
        orchestrator = create_youtube_orchestrator()
        orchestrator.start_session("Test")

        # Taste agent should be initialized
        assert orchestrator.taste_agent is not None

        # Contradictor should be ready
        contradiction = orchestrator.contradict("Test selection")
        assert contradiction is not None

        # Ghost analyzer should be ready
        analysis = orchestrator.get_ghost_analysis()
        assert analysis is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
