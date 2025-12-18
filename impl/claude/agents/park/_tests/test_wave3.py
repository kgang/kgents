"""
Wave 3 Tests: Park-Domain Integration and Dialogue Masks.

Tests for:
- DomainToBrainHandler: Drill results → Brain capture
- ParkToBrainHandler: Scenario results → Brain capture
- ParkDomainBridge: Integrated scenarios with timers
- DialogueMask: Eigenvector transforms

See: plans/crown-jewels-enlightened.md (Wave 3)
"""

from __future__ import annotations

from datetime import datetime

import pytest

from agents.domain.drills import (
    CrisisPhase,
    TimerStatus,
    TimerType,
)
from agents.park import (
    # Masks
    ARCHITECT_MASK,
    CHILD_MASK,
    DREAMER_MASK,
    HEALER_MASK,
    MASK_DECK,
    SAGE_MASK,
    SKEPTIC_MASK,
    TRICKSTER_MASK,
    WARRIOR_MASK,
    DialogueMask,
    EigenvectorTransform,
    # Domain Bridge
    IntegratedScenarioType,
    MaskArchetype,
    MaskedSessionState,
    ParkDomainBridge,
    create_data_breach_practice,
    create_masked_state,
    create_service_outage_practice,
    get_mask,
    list_masks,
)

# =============================================================================
# Dialogue Mask Tests
# =============================================================================


class TestEigenvectorTransform:
    """Tests for EigenvectorTransform."""

    def test_apply_positive_delta(self) -> None:
        """Test applying positive delta to eigenvectors."""
        transform = EigenvectorTransform(creativity_delta=0.3)
        base = {"creativity": 0.5}
        result = transform.apply(base)
        assert result["creativity"] == pytest.approx(0.8)

    def test_apply_negative_delta(self) -> None:
        """Test applying negative delta to eigenvectors."""
        transform = EigenvectorTransform(trust_delta=-0.2)
        base = {"trust": 0.6}
        result = transform.apply(base)
        assert result["trust"] == pytest.approx(0.4)

    def test_clamp_to_max(self) -> None:
        """Test that values are clamped to 1.0 max."""
        transform = EigenvectorTransform(creativity_delta=0.5)
        base = {"creativity": 0.8}
        result = transform.apply(base)
        assert result["creativity"] == 1.0

    def test_clamp_to_min(self) -> None:
        """Test that values are clamped to -1.0 min."""
        transform = EigenvectorTransform(trust_delta=-0.5)
        base = {"trust": -0.8}
        result = transform.apply(base)
        assert result["trust"] == -1.0

    def test_default_value(self) -> None:
        """Test that missing values default to 0.5."""
        transform = EigenvectorTransform(creativity_delta=0.2)
        base = {}  # No creativity key
        result = transform.apply(base)
        assert result["creativity"] == pytest.approx(0.7)  # 0.5 + 0.2

    def test_multiple_deltas(self) -> None:
        """Test applying multiple deltas."""
        transform = EigenvectorTransform(
            creativity_delta=0.3,
            trust_delta=-0.2,
            empathy_delta=0.1,
        )
        base = {"creativity": 0.4, "trust": 0.6, "empathy": 0.5}
        result = transform.apply(base)
        assert result["creativity"] == pytest.approx(0.7)
        assert result["trust"] == pytest.approx(0.4)
        assert result["empathy"] == pytest.approx(0.6)

    def test_to_dict(self) -> None:
        """Test conversion to dictionary."""
        transform = EigenvectorTransform(creativity_delta=0.3, trust_delta=-0.2)
        d = transform.to_dict()
        assert d["creativity"] == 0.3
        assert d["trust"] == -0.2
        assert d["empathy"] == 0.0  # Default


class TestDialogueMask:
    """Tests for DialogueMask."""

    def test_trickster_mask_exists(self) -> None:
        """Test that trickster mask is properly defined."""
        assert TRICKSTER_MASK is not None
        assert TRICKSTER_MASK.archetype == MaskArchetype.TRICKSTER
        assert TRICKSTER_MASK.name == "The Trickster"

    def test_all_masks_in_deck(self) -> None:
        """Test that all 8 canonical masks are in the deck."""
        assert len(MASK_DECK) == 8
        assert "trickster" in MASK_DECK
        assert "dreamer" in MASK_DECK
        assert "skeptic" in MASK_DECK
        assert "architect" in MASK_DECK
        assert "child" in MASK_DECK
        assert "sage" in MASK_DECK
        assert "warrior" in MASK_DECK
        assert "healer" in MASK_DECK

    def test_mask_has_special_abilities(self) -> None:
        """Test that masks have special abilities."""
        assert len(TRICKSTER_MASK.special_abilities) > 0
        assert "provoke_admission" in TRICKSTER_MASK.special_abilities

    def test_mask_has_restrictions(self) -> None:
        """Test that masks have restrictions."""
        assert len(TRICKSTER_MASK.restrictions) > 0
        assert "formal_request" in TRICKSTER_MASK.restrictions

    def test_apply_mask_to_eigenvectors(self) -> None:
        """Test applying mask transform to eigenvectors."""
        base = {"creativity": 0.5, "trust": 0.5}
        result = TRICKSTER_MASK.apply_to_eigenvectors(base)

        # Trickster: +30% creativity (scaled by 0.7 intensity)
        # 0.5 + (0.3 * 0.7) = 0.5 + 0.21 = 0.71
        assert result["creativity"] > 0.5

        # Trickster: -20% trust (scaled by 0.7 intensity)
        # 0.5 + (-0.2 * 0.7) = 0.5 - 0.14 = 0.36
        assert result["trust"] < 0.5

    def test_mask_intensity_scales_transform(self) -> None:
        """Test that intensity scales the transform."""
        # Child mask has 0.7 intensity
        base = {"playfulness": 0.5}
        result = CHILD_MASK.apply_to_eigenvectors(base)

        # +40% playfulness * 0.7 intensity = +0.28
        assert result["playfulness"] == pytest.approx(0.78, rel=0.01)

    def test_mask_to_dict(self) -> None:
        """Test mask serialization."""
        d = TRICKSTER_MASK.to_dict()
        assert d["archetype"] == "TRICKSTER"
        assert d["name"] == "The Trickster"
        assert "transform" in d
        assert "special_abilities" in d
        assert "restrictions" in d


class TestMaskHelpers:
    """Tests for mask helper functions."""

    def test_get_mask_found(self) -> None:
        """Test getting a mask by name."""
        mask = get_mask("trickster")
        assert mask is not None
        assert mask.name == "The Trickster"

    def test_get_mask_case_insensitive(self) -> None:
        """Test that get_mask is case-insensitive."""
        mask1 = get_mask("Trickster")
        mask2 = get_mask("TRICKSTER")
        assert mask1 is not None
        assert mask2 is not None

    def test_get_mask_not_found(self) -> None:
        """Test getting a non-existent mask."""
        mask = get_mask("nonexistent")
        assert mask is None

    def test_list_masks(self) -> None:
        """Test listing all masks."""
        masks = list_masks()
        assert len(masks) == 8
        names = [m["name"] for m in masks]
        assert "The Trickster" in names
        assert "The Dreamer" in names

    def test_create_masked_state(self) -> None:
        """Test creating a masked session state."""
        base = {"creativity": 0.5, "trust": 0.6}
        state = create_masked_state("trickster", base, "session-123")

        assert state is not None
        assert state.mask.name == "The Trickster"
        assert state.session_id == "session-123"
        assert state.base_eigenvectors == base

    def test_create_masked_state_invalid_mask(self) -> None:
        """Test creating state with invalid mask returns None."""
        state = create_masked_state("nonexistent", {}, "session-123")
        assert state is None


class TestMaskedSessionState:
    """Tests for MaskedSessionState."""

    def test_transformed_eigenvectors(self) -> None:
        """Test that transformed eigenvectors are computed."""
        state = create_masked_state(
            "trickster",
            {"creativity": 0.5, "trust": 0.5},
            "session-123",
        )
        assert state is not None

        transformed = state.transformed_eigenvectors
        assert transformed["creativity"] > 0.5
        assert transformed["trust"] < 0.5

    def test_can_use_ability(self) -> None:
        """Test checking ability availability."""
        state = create_masked_state("trickster", {}, "session-123")
        assert state is not None

        assert state.can_use_ability("provoke_admission") is True
        assert state.can_use_ability("nonexistent_ability") is False

    def test_is_restricted(self) -> None:
        """Test checking restrictions."""
        state = create_masked_state("trickster", {}, "session-123")
        assert state is not None

        assert state.is_restricted("formal_request") is True
        assert state.is_restricted("casual_chat") is False

    def test_record_ability_use(self) -> None:
        """Test recording ability usage."""
        state = create_masked_state("trickster", {}, "session-123")
        assert state is not None

        state.record_ability_use("provoke_admission")
        assert state.abilities_used["provoke_admission"] == 1
        assert state.interactions_count == 1

        state.record_ability_use("provoke_admission")
        assert state.abilities_used["provoke_admission"] == 2
        assert state.interactions_count == 2


# =============================================================================
# Park-Domain Bridge Tests
# =============================================================================


class TestParkDomainBridge:
    """Tests for ParkDomainBridge."""

    def test_create_bridge(self) -> None:
        """Test creating a bridge."""
        bridge = ParkDomainBridge()
        assert bridge is not None

    def test_create_crisis_scenario(self) -> None:
        """Test creating a crisis scenario."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Test Crisis",
            description="A test crisis scenario",
        )

        assert state is not None
        assert state.config.name == "Test Crisis"
        assert state.config.scenario_type == IntegratedScenarioType.CRISIS_PRACTICE

    def test_create_scenario_with_timer(self) -> None:
        """Test creating a scenario with a timer."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Timed Crisis",
            timer_type=TimerType.GDPR_72H,
        )

        assert len(state.timers) == 1
        assert state.timers[0].config.timer_type == TimerType.GDPR_72H
        assert state.timers[0].status == TimerStatus.PENDING

    def test_start_timers(self) -> None:
        """Test starting timers."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Timed Crisis",
            timer_type=TimerType.INTERNAL_SLA,
        )

        assert state.timers[0].status == TimerStatus.PENDING
        bridge.start_timers(state)
        assert state.timers[0].status == TimerStatus.ACTIVE

    def test_tick_timers(self) -> None:
        """Test ticking timers."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Timed Crisis",
            timer_type=TimerType.INTERNAL_SLA,
        )

        bridge.start_timers(state)
        changed = bridge.tick(state)
        # Timer just started, no change expected
        assert len(changed) == 0

    def test_use_force(self) -> None:
        """Test using force mechanic."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Test",
        )

        assert state.forces_used == 0
        assert state.consent_debt == 0.0

        success = bridge.use_force(state)
        assert success is True
        assert state.forces_used == 1
        assert state.consent_debt == 0.2

    def test_force_limit(self) -> None:
        """Test force mechanic limit (3 per session)."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Test",
        )

        # Use all 3 forces
        assert bridge.use_force(state) is True
        assert bridge.use_force(state) is True
        assert bridge.use_force(state) is True

        # Fourth should fail
        assert bridge.use_force(state) is False
        assert state.forces_used == 3

    def test_transition_crisis_phase(self) -> None:
        """Test polynomial phase transition."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Test",
        )

        assert state.crisis_phase == CrisisPhase.NORMAL

        result = bridge.transition_crisis_phase(state, CrisisPhase.INCIDENT)
        assert result["success"] is True
        assert state.crisis_phase == CrisisPhase.INCIDENT

    def test_invalid_phase_transition(self) -> None:
        """Test invalid polynomial transition."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Test",
        )

        # Try to jump from NORMAL to RECOVERY (invalid)
        result = bridge.transition_crisis_phase(state, CrisisPhase.RECOVERY)
        assert result["success"] is False
        assert "Invalid transition" in result["error"]

    def test_complete_scenario(self) -> None:
        """Test completing a scenario."""
        bridge = ParkDomainBridge()
        state = bridge.create_crisis_scenario(
            scenario_type=IntegratedScenarioType.CRISIS_PRACTICE,
            name="Test",
            timer_type=TimerType.INTERNAL_SLA,
        )

        bridge.start_timers(state)
        state.consent_debt = 0.3
        state.forces_used = 1

        result = bridge.complete_scenario(state, outcome="success")

        assert result["outcome"] == "success"
        assert result["consent_debt_final"] == 0.3
        assert result["forces_used"] == 1
        assert "timer_outcomes" in result


class TestIntegratedScenarioTemplates:
    """Tests for pre-built scenario templates."""

    def test_create_data_breach_practice(self) -> None:
        """Test creating data breach practice scenario."""
        bridge = ParkDomainBridge()
        state = create_data_breach_practice(bridge)

        assert state.config.name == "Data Breach Response Practice"
        assert state.config.scenario_type == IntegratedScenarioType.CRISIS_PRACTICE
        assert len(state.timers) == 1
        assert state.timers[0].config.timer_type == TimerType.GDPR_72H

    def test_create_service_outage_practice(self) -> None:
        """Test creating service outage practice scenario."""
        bridge = ParkDomainBridge()
        state = create_service_outage_practice(bridge)

        assert state.config.name == "Service Outage Response Practice"
        assert len(state.timers) == 1
        assert state.timers[0].config.timer_type == TimerType.INTERNAL_SLA


# =============================================================================
# Synergy Handler Tests
# =============================================================================


class TestDomainToBrainHandler:
    """Tests for DomainToBrainHandler."""

    @pytest.mark.asyncio
    async def test_handle_drill_complete_dry_run(self) -> None:
        """Test handling drill complete event (dry run)."""
        from protocols.synergy.events import Jewel, SynergyEvent, SynergyEventType
        from protocols.synergy.handlers import DomainToBrainHandler

        handler = DomainToBrainHandler(auto_capture=False)  # Dry run

        event = SynergyEvent(
            source_jewel=Jewel.DOMAIN,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.DRILL_COMPLETE,
            source_id="drill-123",
            payload={
                "drill_type": "data_breach",
                "drill_name": "Q4 Data Breach Drill",
                "difficulty": "medium",
                "team_size": 6,
                "duration_seconds": 2700,
                "outcome": "success",
                "score": 85,
                "grade": "B+",
                "timer_outcomes": {"GDPR 72h": {"status": "COMPLETED", "elapsed_seconds": 2400}},
                "decisions": [{"time": "00:05", "actor": "Alice", "action": "Contained breach"}],
                "recommendations": ["Improve escalation speed"],
            },
        )

        result = await handler.handle(event)
        assert result.success is True
        assert "Dry run" in result.message
        assert result.metadata["drill_type"] == "data_breach"

    @pytest.mark.asyncio
    async def test_skip_non_drill_events(self) -> None:
        """Test that handler skips non-drill events."""
        from protocols.synergy.events import Jewel, SynergyEvent, SynergyEventType
        from protocols.synergy.handlers import DomainToBrainHandler

        handler = DomainToBrainHandler(auto_capture=False)

        event = SynergyEvent(
            source_jewel=Jewel.GESTALT,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.ANALYSIS_COMPLETE,
            source_id="analysis-123",
            payload={},
        )

        result = await handler.handle(event)
        assert result.success is True
        assert "Skipped" in result.message


class TestParkToBrainHandler:
    """Tests for ParkToBrainHandler."""

    @pytest.mark.asyncio
    async def test_handle_scenario_complete_dry_run(self) -> None:
        """Test handling scenario complete event (dry run)."""
        from protocols.synergy.events import Jewel, SynergyEvent, SynergyEventType
        from protocols.synergy.handlers import ParkToBrainHandler

        handler = ParkToBrainHandler(auto_capture=False)

        event = SynergyEvent(
            source_jewel=Jewel.PARK,
            target_jewel=Jewel.BRAIN,
            event_type=SynergyEventType.SCENARIO_COMPLETE,
            source_id="session-456",
            payload={
                "scenario_name": "Board Presentation Practice",
                "scenario_type": "practice",
                "duration_seconds": 1800,
                "consent_debt_final": 0.4,
                "forces_used": 1,
                "key_moments": [{"time": "00:12:34", "description": "Force used", "marker": "⚠️"}],
                "feedback": {
                    "strengths": ["Good adaptability"],
                    "growth_areas": ["Escalation speed"],
                    "suggestions": ["Practice with harder difficulty"],
                },
                "skill_changes": {"persuasion": {"before": "COMPETENT", "after": "PROFICIENT"}},
            },
        )

        result = await handler.handle(event)
        assert result.success is True
        assert "Dry run" in result.message
        assert result.metadata["scenario_name"] == "Board Presentation Practice"


# =============================================================================
# Event Factory Tests
# =============================================================================


class TestWave3EventFactories:
    """Tests for Wave 3 event factory functions."""

    def test_create_drill_complete_event(self) -> None:
        """Test creating drill complete event."""
        from protocols.synergy.events import create_drill_complete_event

        event = create_drill_complete_event(
            drill_id="drill-123",
            drill_type="data_breach",
            drill_name="Q4 Drill",
            difficulty="medium",
            team_size=6,
            duration_seconds=2700,
            outcome="success",
            score=85,
            grade="B+",
        )

        assert event.source_jewel.value == "domain"
        assert event.target_jewel.value == "brain"
        assert event.event_type.value == "drill_complete"
        assert event.payload["drill_type"] == "data_breach"

    def test_create_scenario_complete_event(self) -> None:
        """Test creating scenario complete event."""
        from protocols.synergy.events import create_scenario_complete_event

        event = create_scenario_complete_event(
            session_id="session-456",
            scenario_name="Test Scenario",
            scenario_type="practice",
            duration_seconds=1800,
            consent_debt_final=0.3,
            forces_used=1,
        )

        assert event.source_jewel.value == "park"
        assert event.target_jewel.value == "brain"
        assert event.event_type.value == "scenario_complete"
        assert event.payload["consent_debt_final"] == 0.3

    def test_create_force_used_event(self) -> None:
        """Test creating force used event."""
        from protocols.synergy.events import create_force_used_event

        event = create_force_used_event(
            force_id="force-789",
            session_id="session-456",
            target_citizen="Sarah",
            request="approve the budget",
            consent_debt_before=0.2,
            consent_debt_after=0.4,
            forces_remaining=2,
        )

        assert event.event_type.value == "force_used"
        assert event.payload["target_citizen"] == "Sarah"
        assert event.payload["forces_remaining"] == 2
