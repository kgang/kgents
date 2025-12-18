"""
Tests for CrisisPolynomial: Crisis Response State Machine.

Verifies:
1. Phase transitions (NORMAL → INCIDENT → RESPONSE → RECOVERY → NORMAL)
2. Direction validation (correct inputs per phase)
3. Audit flag behavior
4. Error cases (invalid transitions)
"""

from datetime import datetime

import pytest

from agents.domain.drills.polynomial import (
    CRISIS_POLYNOMIAL,
    CloseInput,
    CommunicateInput,
    ContainInput,
    CrisisInput,
    CrisisOutput,
    CrisisPhase,
    DetectInput,
    EscalateInput,
    InvestigateInput,
    RecoverInput,
    ResolveInput,
    crisis_directions,
    crisis_transition,
)


class TestCrisisPhase:
    """Tests for CrisisPhase enum."""

    def test_has_four_phases(self) -> None:
        """Verify all four phases exist."""
        assert CrisisPhase.NORMAL is not None
        assert CrisisPhase.INCIDENT is not None
        assert CrisisPhase.RESPONSE is not None
        assert CrisisPhase.RECOVERY is not None
        assert len(CrisisPhase) == 4

    def test_phases_are_distinct(self) -> None:
        """Each phase is unique."""
        phases = list(CrisisPhase)
        assert len(phases) == len(set(phases))


class TestCrisisInput:
    """Tests for CrisisInput factory."""

    def test_detect_creates_detect_input(self) -> None:
        """Factory creates DetectInput correctly."""
        detect = CrisisInput.detect(
            description="Database cluster down",
            severity="critical",
            source="monitoring",
        )
        assert isinstance(detect, DetectInput)
        assert detect.description == "Database cluster down"
        assert detect.severity == "critical"
        assert detect.source == "monitoring"

    def test_escalate_creates_escalate_input(self) -> None:
        """Factory creates EscalateInput correctly."""
        escalate = CrisisInput.escalate(
            target_role="incident_commander",
            reason="Severity requires escalation",
            urgency="critical",
        )
        assert isinstance(escalate, EscalateInput)
        assert escalate.target_role == "incident_commander"
        assert escalate.reason == "Severity requires escalation"
        assert escalate.urgency == "critical"

    def test_contain_creates_contain_input(self) -> None:
        """Factory creates ContainInput correctly."""
        contain = CrisisInput.contain(
            action="isolate",
            target="DB-PROD-03",
            scope="targeted",
        )
        assert isinstance(contain, ContainInput)
        assert contain.action == "isolate"
        assert contain.target == "DB-PROD-03"
        assert contain.scope == "targeted"

    def test_communicate_creates_communicate_input(self) -> None:
        """Factory creates CommunicateInput correctly."""
        comm = CrisisInput.communicate(
            message_type="customer",
            audience="all_customers",
            content="We are investigating an issue...",
            approved_by="PR Director",
        )
        assert isinstance(comm, CommunicateInput)
        assert comm.message_type == "customer"
        assert comm.audience == "all_customers"
        assert comm.approved_by == "PR Director"

    def test_recover_creates_recover_input(self) -> None:
        """Factory creates RecoverInput correctly."""
        recover = CrisisInput.recover(
            containment_confirmed=True,
            systems_stable=True,
        )
        assert isinstance(recover, RecoverInput)
        assert recover.containment_confirmed is True
        assert recover.systems_stable is True

    def test_close_creates_close_input(self) -> None:
        """Factory creates CloseInput correctly."""
        close = CrisisInput.close(
            postmortem_scheduled=True,
            documentation_complete=True,
            lessons=["Improve monitoring", "Add redundancy"],
        )
        assert isinstance(close, CloseInput)
        assert close.postmortem_scheduled is True
        assert close.documentation_complete is True
        assert "Improve monitoring" in close.lessons_captured


class TestCrisisDirections:
    """Tests for phase-dependent valid inputs."""

    def test_normal_accepts_detect(self) -> None:
        """NORMAL phase accepts DetectInput."""
        directions = crisis_directions(CrisisPhase.NORMAL)
        assert DetectInput in directions

    def test_normal_rejects_escalate(self) -> None:
        """NORMAL phase doesn't directly accept EscalateInput."""
        directions = crisis_directions(CrisisPhase.NORMAL)
        assert EscalateInput not in directions

    def test_incident_accepts_escalate(self) -> None:
        """INCIDENT phase accepts EscalateInput."""
        directions = crisis_directions(CrisisPhase.INCIDENT)
        assert EscalateInput in directions

    def test_incident_accepts_contain(self) -> None:
        """INCIDENT phase accepts ContainInput."""
        directions = crisis_directions(CrisisPhase.INCIDENT)
        assert ContainInput in directions

    def test_response_accepts_resolve(self) -> None:
        """RESPONSE phase accepts ResolveInput."""
        directions = crisis_directions(CrisisPhase.RESPONSE)
        assert ResolveInput in directions

    def test_recovery_accepts_close(self) -> None:
        """RECOVERY phase accepts CloseInput."""
        directions = crisis_directions(CrisisPhase.RECOVERY)
        assert CloseInput in directions


class TestCrisisTransitions:
    """Tests for state transitions."""

    def test_normal_to_incident_on_detect(self) -> None:
        """NORMAL + DetectInput → INCIDENT."""
        detect = CrisisInput.detect("Database down", "critical", "monitoring")
        new_phase, output = crisis_transition(CrisisPhase.NORMAL, detect)

        assert new_phase == CrisisPhase.INCIDENT
        assert output.success is True
        assert output.audit_required is True
        assert "Database down" in output.message

    def test_incident_stays_on_escalate(self) -> None:
        """INCIDENT + EscalateInput → INCIDENT (stays in phase)."""
        escalate = CrisisInput.escalate("commander", "Need help", "high")
        new_phase, output = crisis_transition(CrisisPhase.INCIDENT, escalate)

        assert new_phase == CrisisPhase.INCIDENT
        assert output.success is True
        assert output.audit_required is True

    def test_incident_stays_on_contain(self) -> None:
        """INCIDENT + ContainInput → INCIDENT (stays in phase)."""
        contain = CrisisInput.contain("isolate", "system", "targeted")
        new_phase, output = crisis_transition(CrisisPhase.INCIDENT, contain)

        assert new_phase == CrisisPhase.INCIDENT
        assert output.success is True
        assert output.audit_required is True

    def test_incident_to_response_on_recover(self) -> None:
        """INCIDENT + RecoverInput → RESPONSE."""
        recover = CrisisInput.recover(containment_confirmed=True, systems_stable=True)
        new_phase, output = crisis_transition(CrisisPhase.INCIDENT, recover)

        assert new_phase == CrisisPhase.RESPONSE
        assert output.success is True
        assert output.audit_required is True

    def test_response_to_recovery_on_recover(self) -> None:
        """RESPONSE + RecoverInput (confirmed) → RECOVERY."""
        recover = CrisisInput.recover(containment_confirmed=True, systems_stable=True)
        new_phase, output = crisis_transition(CrisisPhase.RESPONSE, recover)

        assert new_phase == CrisisPhase.RECOVERY
        assert output.success is True
        assert output.audit_required is True

    def test_response_stays_if_not_confirmed(self) -> None:
        """RESPONSE + RecoverInput (not confirmed) → stays in RESPONSE."""
        recover = CrisisInput.recover(containment_confirmed=False, systems_stable=True)
        new_phase, output = crisis_transition(CrisisPhase.RESPONSE, recover)

        assert new_phase == CrisisPhase.RESPONSE
        assert output.success is False

    def test_recovery_to_normal_on_close(self) -> None:
        """RECOVERY + CloseInput → NORMAL."""
        close = CrisisInput.close(postmortem_scheduled=True, documentation_complete=True)
        new_phase, output = crisis_transition(CrisisPhase.RECOVERY, close)

        assert new_phase == CrisisPhase.NORMAL
        assert output.success is True
        assert output.audit_required is True

    def test_recovery_stays_if_no_postmortem(self) -> None:
        """RECOVERY + CloseInput (no postmortem) → stays in RECOVERY."""
        close = CrisisInput.close(postmortem_scheduled=False)
        new_phase, output = crisis_transition(CrisisPhase.RECOVERY, close)

        assert new_phase == CrisisPhase.RECOVERY
        assert output.success is False

    def test_normal_rejects_escalate(self) -> None:
        """NORMAL + EscalateInput → failure."""
        escalate = CrisisInput.escalate("commander", "reason", "high")
        new_phase, output = crisis_transition(CrisisPhase.NORMAL, escalate)

        assert new_phase == CrisisPhase.NORMAL
        assert output.success is False


class TestFullIncidentLifecycle:
    """Test complete incident lifecycle."""

    def test_full_outage_lifecycle(self) -> None:
        """
        Test full lifecycle:
        NORMAL → INCIDENT → RESPONSE → RECOVERY → NORMAL
        """
        phase = CrisisPhase.NORMAL

        # Detect incident
        detect = CrisisInput.detect("DB cluster down", "critical", "monitoring")
        phase, _ = crisis_transition(phase, detect)
        assert phase == CrisisPhase.INCIDENT

        # Escalate
        escalate = CrisisInput.escalate("commander", "Need help", "critical")
        phase, _ = crisis_transition(phase, escalate)
        assert phase == CrisisPhase.INCIDENT

        # Contain
        contain = CrisisInput.contain("isolate", "DB-PROD-03", "targeted")
        phase, _ = crisis_transition(phase, contain)
        assert phase == CrisisPhase.INCIDENT

        # Move to RESPONSE
        recover1 = CrisisInput.recover(containment_confirmed=True, systems_stable=False)
        phase, _ = crisis_transition(phase, recover1)
        assert phase == CrisisPhase.RESPONSE

        # Resolve issues
        resolve = CrisisInput.resolve("restore", "DB-PROD-03", "health check passed")
        phase, _ = crisis_transition(phase, resolve)
        assert phase == CrisisPhase.RESPONSE

        # Move to RECOVERY
        recover2 = CrisisInput.recover(containment_confirmed=True, systems_stable=True)
        phase, _ = crisis_transition(phase, recover2)
        assert phase == CrisisPhase.RECOVERY

        # Close incident
        close = CrisisInput.close(
            postmortem_scheduled=True,
            documentation_complete=True,
            lessons=["Add monitoring", "Improve failover"],
        )
        phase, output = crisis_transition(phase, close)
        assert phase == CrisisPhase.NORMAL
        assert output.success is True


class TestPolynomialAgent:
    """Tests for CRISIS_POLYNOMIAL agent."""

    def test_polynomial_has_four_positions(self) -> None:
        """CRISIS_POLYNOMIAL has 4 positions."""
        assert len(CRISIS_POLYNOMIAL.positions) == 4

    def test_polynomial_name(self) -> None:
        """CRISIS_POLYNOMIAL has correct name."""
        assert CRISIS_POLYNOMIAL.name == "CrisisPolynomial"

    def test_polynomial_transition_works(self) -> None:
        """Can invoke transition through polynomial."""
        detect = CrisisInput.detect("Issue detected", "high", "automated")
        new_phase, output = CRISIS_POLYNOMIAL.transition(CrisisPhase.NORMAL, detect)

        assert new_phase == CrisisPhase.INCIDENT
        assert isinstance(output, CrisisOutput)
