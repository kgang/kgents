"""
Tests for Drill Templates: Pre-configured Crisis Simulations.

Verifies:
1. Template specifications (ServiceOutage, DataBreach)
2. Drill instance lifecycle (setup, start, tick, advance, end)
3. GDPR 72h timer integration for data breach
4. Success criteria evaluation
5. Audit logging
"""

from datetime import datetime, timedelta

import pytest

from agents.domain.drills.archetypes import CrisisArchetype
from agents.domain.drills.polynomial import CrisisInput, CrisisPhase
from agents.domain.drills.templates import (
    DATA_BREACH_SPEC,
    DATA_BREACH_SUCCESS_CRITERIA,
    DRILL_TEMPLATES,
    SERVICE_OUTAGE_SPEC,
    SERVICE_OUTAGE_SUCCESS_CRITERIA,
    DrillDifficulty,
    DrillError,
    DrillInstance,
    DrillStateError,
    DrillStatus,
    DrillTemplateSpec,
    DrillType,
    DrillValidationError,
    SuccessCriterion,
    create_data_breach_drill,
    create_drill,
    create_service_outage_drill,
    get_drill_template,
    list_drill_types,
)
from agents.domain.drills.timers import TimerType


class TestDrillType:
    """Tests for DrillType enum."""

    def test_has_six_types(self) -> None:
        """All drill types exist."""
        assert len(DrillType) == 6
        assert DrillType.SERVICE_OUTAGE is not None
        assert DrillType.DATA_BREACH is not None
        assert DrillType.PR_CRISIS is not None
        assert DrillType.ROGUE_AI is not None
        assert DrillType.VENDOR_FAILURE is not None
        assert DrillType.INSIDER_THREAT is not None


class TestDrillDifficulty:
    """Tests for DrillDifficulty enum."""

    def test_has_four_difficulties(self) -> None:
        """All difficulty levels exist."""
        assert len(DrillDifficulty) == 4
        assert DrillDifficulty.TRAINING is not None
        assert DrillDifficulty.STANDARD is not None
        assert DrillDifficulty.ADVANCED is not None
        assert DrillDifficulty.CHAOS is not None


class TestDrillStatus:
    """Tests for DrillStatus enum."""

    def test_has_six_statuses(self) -> None:
        """All drill statuses exist."""
        assert len(DrillStatus) == 6
        assert DrillStatus.DRAFT is not None
        assert DrillStatus.READY is not None
        assert DrillStatus.RUNNING is not None
        assert DrillStatus.PAUSED is not None
        assert DrillStatus.COMPLETED is not None
        assert DrillStatus.ABORTED is not None


class TestSuccessCriteria:
    """Tests for success criteria."""

    def test_service_outage_criteria(self) -> None:
        """Service outage has correct success criteria."""
        criteria = SERVICE_OUTAGE_SUCCESS_CRITERIA

        assert len(criteria) >= 4
        names = [c.name for c in criteria]
        assert "service_restored" in names
        assert "commander_notified" in names
        assert "customer_communication" in names
        assert "postmortem_scheduled" in names

    def test_data_breach_criteria(self) -> None:
        """Data breach has correct success criteria."""
        criteria = DATA_BREACH_SUCCESS_CRITERIA

        assert len(criteria) >= 5
        names = [c.name for c in criteria]
        assert "breach_contained" in names
        assert "legal_assessment" in names
        assert "gdpr_notification" in names
        assert "media_statement" in names
        assert "forensics_preserved" in names


class TestServiceOutageSpec:
    """Tests for ServiceOutageSpec."""

    def test_service_outage_spec_properties(self) -> None:
        """SERVICE_OUTAGE spec has correct properties."""
        spec = SERVICE_OUTAGE_SPEC

        assert spec.drill_type == DrillType.SERVICE_OUTAGE
        assert spec.name == "Critical Service Outage"
        assert "database" in spec.scenario_trigger.lower()
        assert spec.target_duration_minutes == 45

    def test_service_outage_archetypes(self) -> None:
        """SERVICE_OUTAGE has correct citizen archetypes."""
        spec = SERVICE_OUTAGE_SPEC

        assert len(spec.citizen_archetypes) == 4
        assert CrisisArchetype.ON_CALL_ENGINEER in spec.citizen_archetypes
        assert CrisisArchetype.INCIDENT_COMMANDER in spec.citizen_archetypes
        assert CrisisArchetype.EXECUTIVE in spec.citizen_archetypes
        assert CrisisArchetype.CUSTOMER_SUCCESS in spec.citizen_archetypes

    def test_service_outage_escalation_path(self) -> None:
        """SERVICE_OUTAGE has correct escalation path."""
        spec = SERVICE_OUTAGE_SPEC

        assert len(spec.escalation_path) == 3
        assert "On-Call Engineer" in spec.escalation_path
        assert "Incident Commander" in spec.escalation_path
        assert "Executive" in spec.escalation_path

    def test_service_outage_no_timers(self) -> None:
        """SERVICE_OUTAGE has no compliance timers."""
        spec = SERVICE_OUTAGE_SPEC
        assert len(spec.timers) == 0


class TestDataBreachSpec:
    """Tests for DataBreachSpec."""

    def test_data_breach_spec_properties(self) -> None:
        """DATA_BREACH spec has correct properties."""
        spec = DATA_BREACH_SPEC

        assert spec.drill_type == DrillType.DATA_BREACH
        assert spec.name == "Data Breach Response"
        assert "data" in spec.scenario_trigger.lower()  # "data transfer" or "exfiltration"
        assert spec.target_duration_minutes == 60
        # Higher stress for breach
        assert spec.default_stress_level > SERVICE_OUTAGE_SPEC.default_stress_level

    def test_data_breach_archetypes(self) -> None:
        """DATA_BREACH has correct citizen archetypes."""
        spec = DATA_BREACH_SPEC

        assert len(spec.citizen_archetypes) == 4
        assert CrisisArchetype.SECURITY_ANALYST in spec.citizen_archetypes
        assert CrisisArchetype.LEGAL_COUNSEL in spec.citizen_archetypes
        assert CrisisArchetype.PR_DIRECTOR in spec.citizen_archetypes
        assert CrisisArchetype.CISO in spec.citizen_archetypes

    def test_data_breach_has_gdpr_timer(self) -> None:
        """DATA_BREACH has GDPR 72h timer."""
        spec = DATA_BREACH_SPEC

        assert len(spec.timers) == 1
        assert TimerType.GDPR_72H in spec.timers


class TestDrillTemplateRegistry:
    """Tests for drill template registry."""

    def test_templates_in_registry(self) -> None:
        """Both templates are in registry."""
        assert DrillType.SERVICE_OUTAGE in DRILL_TEMPLATES
        assert DrillType.DATA_BREACH in DRILL_TEMPLATES

    def test_get_drill_template(self) -> None:
        """get_drill_template returns correct spec."""
        spec = get_drill_template(DrillType.SERVICE_OUTAGE)
        assert spec == SERVICE_OUTAGE_SPEC

    def test_list_drill_types(self) -> None:
        """list_drill_types returns available types."""
        types = list_drill_types()
        assert "SERVICE_OUTAGE" in types
        assert "DATA_BREACH" in types


class TestDrillInstanceSetup:
    """Tests for DrillInstance setup."""

    def test_initial_state_is_draft(self) -> None:
        """New drill instance is in DRAFT status."""
        drill = DrillInstance(id="test", spec=SERVICE_OUTAGE_SPEC)
        assert drill.status == DrillStatus.DRAFT
        assert len(drill.citizens) == 0

    def test_setup_creates_citizens(self) -> None:
        """Setup creates all citizens from spec."""
        drill = DrillInstance(id="test", spec=SERVICE_OUTAGE_SPEC)
        drill.setup()

        assert drill.status == DrillStatus.READY
        assert len(drill.citizens) == 4
        assert CrisisArchetype.ON_CALL_ENGINEER in drill.citizens
        assert CrisisArchetype.INCIDENT_COMMANDER in drill.citizens

    def test_setup_with_custom_names(self) -> None:
        """Setup uses custom names when provided."""
        drill = DrillInstance(id="test", spec=SERVICE_OUTAGE_SPEC)
        drill.setup(names={CrisisArchetype.ON_CALL_ENGINEER: "CustomEngineer"})

        assert drill.citizens[CrisisArchetype.ON_CALL_ENGINEER].name == "CustomEngineer"

    def test_setup_creates_timers(self) -> None:
        """Setup creates timers from spec."""
        drill = DrillInstance(id="test", spec=DATA_BREACH_SPEC)
        drill.setup()

        assert len(drill.timers) == 1
        assert drill.timers[0].config.timer_type == TimerType.GDPR_72H

    def test_setup_creates_injects(self) -> None:
        """Setup creates inject sequence."""
        drill = DrillInstance(id="test", spec=SERVICE_OUTAGE_SPEC)
        drill.setup()

        assert len(drill.injects.injects) > 0

    def test_setup_creates_evaluations(self) -> None:
        """Setup creates success evaluations."""
        drill = DrillInstance(id="test", spec=SERVICE_OUTAGE_SPEC)
        drill.setup()

        assert len(drill.evaluations) == len(SERVICE_OUTAGE_SUCCESS_CRITERIA)


class TestDrillInstanceLifecycle:
    """Tests for DrillInstance lifecycle."""

    def test_start_transitions_to_running(self) -> None:
        """Starting drill transitions to RUNNING."""
        drill = create_service_outage_drill()
        output = drill.start()

        assert drill.status == DrillStatus.RUNNING
        assert drill.started_at is not None
        assert drill.phase == CrisisPhase.INCIDENT  # Detect triggered
        assert output.success is True

    def test_start_triggers_incident(self) -> None:
        """Starting drill triggers initial incident."""
        drill = create_service_outage_drill()
        drill.start()

        # Should be in INCIDENT phase after detection
        assert drill.phase == CrisisPhase.INCIDENT

    def test_start_starts_timers(self) -> None:
        """Starting drill starts all timers."""
        drill = create_data_breach_drill()
        drill.start()

        for timer in drill.timers:
            assert timer.is_active

    def test_cannot_start_draft_drill(self) -> None:
        """Cannot start a drill that hasn't been set up."""
        drill = DrillInstance(id="test", spec=SERVICE_OUTAGE_SPEC)

        with pytest.raises(DrillStateError, match="Cannot start"):
            drill.start()

    def test_advance_with_valid_input(self) -> None:
        """Can advance drill with valid input."""
        drill = create_service_outage_drill()
        drill.start()

        # Escalate to incident commander
        output = drill.advance(CrisisInput.escalate("commander", "Need help", "high"))

        assert output.success is True
        assert drill.phase == CrisisPhase.INCIDENT  # Still in INCIDENT

    def test_advance_phase_transition(self) -> None:
        """Advance can transition phases."""
        drill = create_service_outage_drill()
        drill.start()

        # Advance to RESPONSE
        output = drill.advance(
            CrisisInput.recover(containment_confirmed=True, systems_stable=False)
        )

        assert drill.phase == CrisisPhase.RESPONSE

    def test_tick_updates_timers_and_injects(self) -> None:
        """Tick method updates timers and checks injects."""
        drill = create_service_outage_drill()
        drill.start()

        changes = drill.tick()

        assert "triggered_injects" in changes
        assert "timer_updates" in changes

    def test_end_transitions_to_completed(self) -> None:
        """Ending drill transitions to COMPLETED."""
        drill = create_service_outage_drill()
        drill.start()

        report = drill.end()

        assert drill.status == DrillStatus.COMPLETED
        assert drill.ended_at is not None
        assert "success" in report
        assert "score" in report

    def test_abort_transitions_to_aborted(self) -> None:
        """Aborting drill transitions to ABORTED."""
        drill = create_service_outage_drill()
        drill.start()
        drill.abort(reason="User requested abort")

        assert drill.status == DrillStatus.ABORTED


class TestDrillInstanceCriteria:
    """Tests for success criteria evaluation."""

    def test_evaluate_criterion(self) -> None:
        """Can evaluate a success criterion."""
        drill = create_service_outage_drill()
        # Factory already calls setup(), so drill is READY

        drill.evaluate_criterion("service_restored", met=True, evidence="Health check passed")

        evaluation = next(e for e in drill.evaluations if e.criterion.name == "service_restored")
        assert evaluation.met is True
        assert evaluation.evidence == "Health check passed"
        assert evaluation.evaluated_at is not None

    def test_evaluate_unknown_criterion_raises(self) -> None:
        """Evaluating unknown criterion raises error."""
        drill = create_service_outage_drill()
        # Factory already calls setup()

        with pytest.raises(DrillValidationError, match="Unknown criterion"):
            drill.evaluate_criterion("nonexistent", met=True)

    def test_score_calculation(self) -> None:
        """Score is calculated from evaluations."""
        drill = create_service_outage_drill()
        # Factory already calls setup()
        drill.start()

        # Evaluate some criteria as met
        drill.evaluate_criterion("service_restored", met=True, evidence="Restored")
        drill.evaluate_criterion("commander_notified", met=True, evidence="Notified")

        report = drill.end()

        assert report["score"] > 0


class TestDrillInstanceAudit:
    """Tests for audit logging."""

    def test_setup_logs_event(self) -> None:
        """Setup is logged to audit log."""
        drill = DrillInstance(id="test", spec=SERVICE_OUTAGE_SPEC)
        drill.setup()

        assert len(drill.audit_log) > 0
        assert any(e["event_type"] == "setup" for e in drill.audit_log)

    def test_start_logs_event(self) -> None:
        """Start is logged to audit log."""
        drill = create_service_outage_drill()
        drill.start()

        assert any(e["event_type"] == "start" for e in drill.audit_log)
        assert any(e["event_type"] == "phase_transition" for e in drill.audit_log)

    def test_advance_logs_auditable_actions(self) -> None:
        """Auditable actions are logged."""
        drill = create_service_outage_drill()
        drill.start()

        drill.advance(CrisisInput.escalate("commander", "Need help", "high"))

        assert any("auditable_action" in e.get("event_type", "") for e in drill.audit_log)


class TestDrillInstanceManifest:
    """Tests for drill manifest/display."""

    def test_manifest_lod_0(self) -> None:
        """LOD 0 manifest has basic info."""
        drill = create_service_outage_drill()
        drill.start()

        manifest = drill.manifest(lod=0)

        assert "id" in manifest
        assert "name" in manifest
        assert "status" in manifest
        assert "phase" in manifest
        assert "elapsed_minutes" in manifest

    def test_manifest_lod_1(self) -> None:
        """LOD 1 manifest has citizens and timers."""
        drill = create_service_outage_drill()
        drill.start()

        manifest = drill.manifest(lod=1)

        assert "citizens" in manifest
        assert "timers" in manifest
        assert len(manifest["citizens"]) == 4

    def test_manifest_lod_2(self) -> None:
        """LOD 2 manifest has injects and evaluations."""
        drill = create_service_outage_drill()
        drill.start()

        manifest = drill.manifest(lod=2)

        assert "active_injects" in manifest
        assert "pending_injects" in manifest
        assert "evaluations" in manifest

    def test_manifest_lod_3(self) -> None:
        """LOD 3 manifest has full audit log."""
        drill = create_service_outage_drill()
        drill.start()

        manifest = drill.manifest(lod=3)

        assert "audit_log" in manifest
        assert "scenario" in manifest


class TestDrillFactories:
    """Tests for drill factory functions."""

    def test_create_service_outage_drill(self) -> None:
        """create_service_outage_drill creates ready drill."""
        drill = create_service_outage_drill()

        assert drill.spec == SERVICE_OUTAGE_SPEC
        assert drill.status == DrillStatus.READY
        assert len(drill.citizens) == 4

    def test_create_data_breach_drill(self) -> None:
        """create_data_breach_drill creates ready drill with timer."""
        drill = create_data_breach_drill()

        assert drill.spec == DATA_BREACH_SPEC
        assert drill.status == DrillStatus.READY
        assert len(drill.citizens) == 4
        assert len(drill.timers) == 1

    def test_create_drill_generic(self) -> None:
        """create_drill works for any drill type."""
        drill = create_drill(DrillType.SERVICE_OUTAGE)

        assert drill.spec == SERVICE_OUTAGE_SPEC
        assert drill.status == DrillStatus.READY

    def test_create_drill_with_difficulty(self) -> None:
        """create_drill respects difficulty parameter."""
        drill = create_drill(
            DrillType.SERVICE_OUTAGE,
            difficulty=DrillDifficulty.CHAOS,
        )

        assert drill.difficulty == DrillDifficulty.CHAOS

    def test_create_drill_with_names(self) -> None:
        """create_drill respects names parameter."""
        drill = create_drill(
            DrillType.SERVICE_OUTAGE,
            names={CrisisArchetype.ON_CALL_ENGINEER: "Alice"},
        )

        assert drill.citizens[CrisisArchetype.ON_CALL_ENGINEER].name == "Alice"


class TestFullDrillLifecycle:
    """Integration tests for full drill lifecycle."""

    def test_service_outage_full_lifecycle(self) -> None:
        """Test complete service outage drill lifecycle."""
        # Setup
        drill = create_service_outage_drill()
        assert drill.status == DrillStatus.READY

        # Start
        output = drill.start()
        assert drill.status == DrillStatus.RUNNING
        assert drill.phase == CrisisPhase.INCIDENT

        # Escalate
        drill.advance(CrisisInput.escalate("commander", "Major outage", "critical"))

        # Contain
        drill.advance(CrisisInput.contain("isolate", "DB-PROD-03", "targeted"))

        # Tick to check injects
        drill.tick()

        # Transition to RESPONSE
        drill.advance(CrisisInput.recover(containment_confirmed=True, systems_stable=False))
        assert drill.phase == CrisisPhase.RESPONSE

        # Resolve
        drill.advance(CrisisInput.resolve("restore", "DB-PROD-03", "verified"))

        # Transition to RECOVERY
        drill.advance(CrisisInput.recover(containment_confirmed=True, systems_stable=True))
        assert drill.phase == CrisisPhase.RECOVERY

        # Evaluate criteria
        drill.evaluate_criterion("service_restored", met=True, evidence="All systems operational")
        drill.evaluate_criterion("commander_notified", met=True, evidence="Within 5 minutes")
        drill.evaluate_criterion("customer_communication", met=True, evidence="Email sent")
        drill.evaluate_criterion(
            "postmortem_scheduled", met=True, evidence="Scheduled for tomorrow"
        )

        # Close
        drill.advance(CrisisInput.close(postmortem_scheduled=True, documentation_complete=True))
        assert drill.phase == CrisisPhase.NORMAL

        # End
        report = drill.end()
        assert drill.status == DrillStatus.COMPLETED
        assert report["success"] is True
        assert report["score"] > 0.5

    def test_data_breach_with_gdpr_timer(self) -> None:
        """Test data breach drill with GDPR timer running."""
        drill = create_data_breach_drill()

        # Start - GDPR timer should start
        drill.start()

        assert drill.status == DrillStatus.RUNNING
        assert len(drill.timers) == 1
        timer = drill.timers[0]
        assert timer.is_active
        assert timer.config.timer_type == TimerType.GDPR_72H

        # Timer should show ~72 hours remaining
        manifest = timer.manifest()
        assert manifest["remaining_seconds"] > 0
        assert manifest["remaining_seconds"] <= 72 * 3600

        # Tick the drill
        changes = drill.tick()

        # End drill
        drill.end()
        assert drill.status == DrillStatus.COMPLETED
