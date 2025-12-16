"""
Tests for Phase 4: Session Unification.

Tests that GardenState properly embeds GardenerSession and that
Phase → Season synergy hooks work correctly.

See: plans/gardener-logos-enactment.md Phase 4
"""

from __future__ import annotations

import pytest
from agents.gardener.session import (
    GardenerSession,
    SessionArtifact,
    SessionIntent,
    SessionPhase,
)
from protocols.gardener_logos.agentese.context import (
    GardenerLogosNode,
    create_gardener_logos_node,
)
from protocols.gardener_logos.garden import (
    GardenSeason,
    GardenState,
    create_garden,
)

# =============================================================================
# Session Embedding Tests
# =============================================================================


class TestSessionEmbedding:
    """Tests for session embedding in GardenState."""

    def test_garden_starts_without_session(self) -> None:
        """Garden should start without an active session."""
        garden = create_garden("Test Garden")
        assert garden.session is None
        assert garden.session_id is None

    def test_get_or_create_session_creates_new(self) -> None:
        """get_or_create_session should create a new session."""
        garden = create_garden("Test Garden")

        session = garden.get_or_create_session(name="Test Session")

        assert session is not None
        assert session.name == "Test Session"
        assert garden.session is session
        assert garden.session_id == session.session_id

    def test_get_or_create_session_returns_existing(self) -> None:
        """get_or_create_session should return existing session."""
        garden = create_garden("Test Garden")

        session1 = garden.get_or_create_session(name="Test Session")
        session2 = garden.get_or_create_session(name="Different Name")

        # Should return the same session
        assert session1 is session2
        assert session1.name == "Test Session"  # Original name preserved

    def test_get_or_create_session_with_plan_path(self) -> None:
        """get_or_create_session should accept plan_path."""
        garden = create_garden("Test Garden")

        session = garden.get_or_create_session(
            name="Plan Session",
            plan_path="plans/test.md",
        )

        assert session.plan_path == "plans/test.md"

    def test_get_or_create_session_auto_names(self) -> None:
        """get_or_create_session should auto-name if not provided."""
        garden = create_garden("My Garden")

        session = garden.get_or_create_session()

        assert session.name.startswith("My Garden-")

    def test_session_property_setter(self) -> None:
        """session setter should update session_id."""
        from agents.gardener.session import create_gardener_session

        garden = create_garden("Test Garden")
        session = create_gardener_session(name="External Session")

        garden.session = session

        assert garden.session is session
        assert garden.session_id == session.session_id

    def test_clear_session(self) -> None:
        """clear_session should remove session without season transition."""
        garden = create_garden("Test Garden")
        garden.get_or_create_session(name="Test Session")
        original_season = garden.season

        garden.clear_session()

        assert garden.session is None
        assert garden.season == original_season  # No transition

    def test_creating_session_transitions_dormant_to_sprouting(self) -> None:
        """Creating a session when DORMANT should transition to SPROUTING."""
        garden = create_garden("Test Garden", season=GardenSeason.DORMANT)
        assert garden.season == GardenSeason.DORMANT

        garden.get_or_create_session(name="Test Session")

        assert garden.season == GardenSeason.SPROUTING


# =============================================================================
# Phase → Season Synergy Tests
# =============================================================================


class TestPhaseSeasonSynergy:
    """Tests for Phase → Season synergy hooks."""

    @pytest.mark.asyncio
    async def test_sense_to_act_triggers_sprouting(self) -> None:
        """SENSE → ACT should trigger DORMANT → SPROUTING."""
        garden = create_garden("Test Garden", season=GardenSeason.DORMANT)
        # Create session without auto-transition (set directly)
        from agents.gardener.session import create_gardener_session

        session = create_gardener_session(name="Test")
        garden._session = session
        garden.session_id = session.session_id
        # Reset to DORMANT for test
        garden.season = GardenSeason.DORMANT

        new_season = await garden.on_session_phase_advance(
            SessionPhase.SENSE, SessionPhase.ACT
        )

        assert new_season == GardenSeason.SPROUTING
        assert garden.season == GardenSeason.SPROUTING

    @pytest.mark.asyncio
    async def test_act_to_reflect_triggers_blooming(self) -> None:
        """ACT → REFLECT should trigger SPROUTING → BLOOMING."""
        garden = create_garden("Test Garden", season=GardenSeason.SPROUTING)
        from agents.gardener.session import create_gardener_session

        session = create_gardener_session(name="Test")
        garden._session = session
        garden.session_id = session.session_id

        new_season = await garden.on_session_phase_advance(
            SessionPhase.ACT, SessionPhase.REFLECT
        )

        assert new_season == GardenSeason.BLOOMING
        assert garden.season == GardenSeason.BLOOMING

    @pytest.mark.asyncio
    async def test_composting_to_sprouting_on_new_work(self) -> None:
        """SENSE → ACT should trigger COMPOSTING → SPROUTING."""
        garden = create_garden("Test Garden", season=GardenSeason.COMPOSTING)
        from agents.gardener.session import create_gardener_session

        session = create_gardener_session(name="Test")
        garden._session = session
        garden.session_id = session.session_id

        new_season = await garden.on_session_phase_advance(
            SessionPhase.SENSE, SessionPhase.ACT
        )

        assert new_season == GardenSeason.SPROUTING
        assert garden.season == GardenSeason.SPROUTING

    @pytest.mark.asyncio
    async def test_no_transition_when_not_matching(self) -> None:
        """Transitions should be context-dependent."""
        garden = create_garden("Test Garden", season=GardenSeason.HARVEST)
        from agents.gardener.session import create_gardener_session

        session = create_gardener_session(name="Test")
        garden._session = session
        garden.session_id = session.session_id

        # HARVEST doesn't transition on SENSE → ACT
        new_season = await garden.on_session_phase_advance(
            SessionPhase.SENSE, SessionPhase.ACT
        )

        assert new_season is None
        assert garden.season == GardenSeason.HARVEST

    @pytest.mark.asyncio
    async def test_session_complete_transitions_to_harvest(self) -> None:
        """Session completion should transition to HARVEST."""
        garden = create_garden("Test Garden", season=GardenSeason.BLOOMING)
        from agents.gardener.session import create_gardener_session

        session = create_gardener_session(name="Test")
        garden._session = session
        garden.session_id = session.session_id

        new_season = await garden.on_session_complete()

        assert new_season == GardenSeason.HARVEST
        assert garden.season == GardenSeason.HARVEST
        assert garden.session is None  # Session cleared

    @pytest.mark.asyncio
    async def test_multiple_cycles_trigger_harvest(self) -> None:
        """Multiple REFLECT cycles should trigger BLOOMING → HARVEST."""
        garden = create_garden("Test Garden", season=GardenSeason.BLOOMING)
        from agents.gardener.session import create_gardener_session

        session = create_gardener_session(name="Test")
        garden._session = session
        garden.session_id = session.session_id

        # Simulate 3 reflect cycles
        session._state.reflect_count = 3

        new_season = await garden.on_session_phase_advance(
            SessionPhase.REFLECT, SessionPhase.SENSE
        )

        assert new_season == GardenSeason.HARVEST


# =============================================================================
# AGENTESE Session Handler Tests
# =============================================================================


class TestSessionAgentese:
    """Tests for session.* AGENTESE handlers."""

    @pytest.fixture
    def node(self) -> GardenerLogosNode:
        """Create a fresh GardenerLogosNode for testing."""
        return create_gardener_logos_node()

    @pytest.fixture
    def mock_observer(self) -> dict:
        """Create a mock observer umwelt."""
        return {"archetype": "developer", "name": "Test Observer"}

    @pytest.mark.asyncio
    async def test_session_create(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.create should create embedded session."""
        result = await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
            intent="Implement feature X",
        )

        assert "SESSION CREATED" in result.content
        assert result.metadata["status"] == "created"
        assert node._garden is not None
        assert node._garden.session is not None
        assert node._garden.session.name == "Test Session"

    @pytest.mark.asyncio
    async def test_session_manifest_no_session(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.manifest should handle no session gracefully."""
        result = await node._invoke_aspect("session.manifest", mock_observer)

        assert result.metadata["status"] == "no_session"
        assert "No active session" in result.content

    @pytest.mark.asyncio
    async def test_session_manifest_with_session(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.manifest should show session details."""
        # Create session first
        await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
        )

        result = await node._invoke_aspect("session.manifest", mock_observer)

        assert result.metadata["status"] == "manifest"
        assert "Test Session" in result.content
        assert "SENSE" in result.content  # Initial phase

    @pytest.mark.asyncio
    async def test_session_advance(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.advance should advance phase and trigger synergy."""
        # Create session (starts in SENSE)
        await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
        )

        # Advance SENSE → ACT
        result = await node._invoke_aspect("session.advance", mock_observer)

        assert result.metadata["status"] == "advanced"
        assert result.metadata["from_phase"] == "SENSE"
        assert result.metadata["to_phase"] == "ACT"
        # Should have triggered season change
        assert node._garden.season == GardenSeason.SPROUTING

    @pytest.mark.asyncio
    async def test_session_sense(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.sense should gather context."""
        await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
        )

        result = await node._invoke_aspect(
            "session.sense",
            mock_observer,
            context_type="forest",
        )

        assert "SENSE COMPLETE" in result.content

    @pytest.mark.asyncio
    async def test_session_artifact(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.artifact should record artifacts."""
        await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
        )
        # Advance to ACT for artifact recording
        await node._invoke_aspect("session.advance", mock_observer)

        result = await node._invoke_aspect(
            "session.artifact",
            mock_observer,
            artifact_type="code",
            path="test.py",
            description="Test file",
        )

        assert "code" in result.summary.lower() or "artifact" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_session_learn(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.learn should record learnings."""
        await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
        )
        # Advance to ACT
        await node._invoke_aspect("session.advance", mock_observer)
        # Advance to REFLECT
        await node._invoke_aspect("session.advance", mock_observer)

        result = await node._invoke_aspect(
            "session.learn",
            mock_observer,
            learning="Pattern X works well for Y",
        )

        assert "Learned" in result.summary or "learning" in result.summary.lower()

    @pytest.mark.asyncio
    async def test_session_complete(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.complete should complete session and transition to HARVEST."""
        await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
        )
        # Advance to ACT
        await node._invoke_aspect("session.advance", mock_observer)
        # Advance to REFLECT
        await node._invoke_aspect("session.advance", mock_observer)

        result = await node._invoke_aspect("session.complete", mock_observer)

        assert result.metadata["status"] == "completed"
        assert node._garden.season == GardenSeason.HARVEST
        assert node._garden.session is None

    @pytest.mark.asyncio
    async def test_session_abort(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.abort should abort session."""
        await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
        )

        result = await node._invoke_aspect("session.abort", mock_observer)

        assert result.metadata["status"] == "aborted"
        assert node._garden.session is None

    @pytest.mark.asyncio
    async def test_session_rollback(
        self, node: GardenerLogosNode, mock_observer: dict
    ) -> None:
        """session.rollback should rollback from ACT to SENSE."""
        await node._invoke_aspect(
            "session.create",
            mock_observer,
            name="Test Session",
        )
        # Advance to ACT
        await node._invoke_aspect("session.advance", mock_observer)
        assert node._garden.session.phase == SessionPhase.ACT

        result = await node._invoke_aspect("session.rollback", mock_observer)

        assert result.metadata["status"] == "rolled_back"
        assert node._garden.session.phase == SessionPhase.SENSE


# =============================================================================
# Integration Tests
# =============================================================================


class TestSessionIntegration:
    """Integration tests for session unification."""

    @pytest.mark.asyncio
    async def test_full_session_lifecycle(self) -> None:
        """Test a complete session lifecycle with synergy."""
        garden = create_garden("Integration Test", season=GardenSeason.DORMANT)

        # 1. Create session (triggers DORMANT → SPROUTING)
        session = garden.get_or_create_session(name="Feature Implementation")
        assert garden.season == GardenSeason.SPROUTING

        # 2. Gather context in SENSE
        await session.sense("all")
        await session.set_intent(SessionIntent(description="Implement feature X"))

        # 3. Advance to ACT
        old_phase = session.phase
        await session.advance()
        # This would be called by a coordinating layer:
        await garden.on_session_phase_advance(old_phase, session.phase)
        # Season should still be SPROUTING

        # 4. Record artifacts
        await session.record_artifact(
            SessionArtifact(artifact_type="code", path="feature.py")
        )

        # 5. Advance to REFLECT (triggers SPROUTING → BLOOMING)
        old_phase = session.phase
        await session.advance()
        await garden.on_session_phase_advance(old_phase, session.phase)
        assert garden.season == GardenSeason.BLOOMING

        # 6. Record learnings
        await session.learn("The approach worked well")

        # 7. Complete session (triggers → HARVEST)
        await session.complete()
        await garden.on_session_complete()
        assert garden.season == GardenSeason.HARVEST
        assert garden.session is None

    @pytest.mark.asyncio
    async def test_session_with_plots(self) -> None:
        """Test session interaction with garden plots."""
        from protocols.gardener_logos.plots import create_plot

        garden = create_garden("Plot Test")
        garden.plots["test-plot"] = create_plot(
            name="test-plot",
            path="concept.project.test",
            plan_path="plans/test.md",
        )
        garden.active_plot = "test-plot"

        # Create session linked to the plot's plan
        session = garden.get_or_create_session(
            name="Plot Work",
            plan_path="plans/test.md",
        )

        assert session.plan_path == "plans/test.md"
        assert garden.active_plot == "test-plot"
