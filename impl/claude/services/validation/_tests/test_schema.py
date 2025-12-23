"""
Tests for validation schema types.

Verifies:
- Enum values and parsing
- Dataclass immutability (frozen)
- YAML loading utilities
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from services.validation.schema import (
    Direction,
    Gate,
    GateCondition,
    GateId,
    Initiative,
    InitiativeId,
    MetricType,
    Phase,
    PhaseId,
    Proposition,
    PropositionId,
    PropositionResult,
    gate_from_dict,
    initiative_from_dict,
    phase_from_dict,
    proposition_from_dict,
)

# =============================================================================
# Enum Tests
# =============================================================================


class TestMetricType:
    """Tests for MetricType enum."""

    def test_all_quantitative_metrics(self) -> None:
        """Verify all quantitative metric types exist."""
        assert MetricType.ACCURACY.value == "accuracy"
        assert MetricType.RECALL.value == "recall"
        assert MetricType.PRECISION.value == "precision"
        assert MetricType.F1.value == "f1"
        assert MetricType.AUC.value == "auc"
        assert MetricType.PEARSON_R.value == "pearson_r"
        assert MetricType.COUNT.value == "count"
        assert MetricType.PERCENT.value == "percent"
        assert MetricType.DURATION_MS.value == "duration_ms"

    def test_all_qualitative_metrics(self) -> None:
        """Verify all qualitative metric types exist."""
        assert MetricType.BINARY.value == "binary"
        assert MetricType.ORDINAL.value == "ordinal"
        assert MetricType.JUDGMENT.value == "judgment"

    def test_parse_from_string(self) -> None:
        """Enum can be constructed from string value."""
        assert MetricType("accuracy") == MetricType.ACCURACY
        assert MetricType("binary") == MetricType.BINARY


class TestDirection:
    """Tests for Direction enum."""

    def test_all_directions(self) -> None:
        """Verify all direction types exist."""
        assert Direction.GT.value == ">"
        assert Direction.GTE.value == ">="
        assert Direction.LT.value == "<"
        assert Direction.LTE.value == "<="
        assert Direction.EQ.value == "="

    def test_parse_from_string(self) -> None:
        """Enum can be constructed from string value."""
        assert Direction(">") == Direction.GT
        assert Direction(">=") == Direction.GTE


class TestGateCondition:
    """Tests for GateCondition enum."""

    def test_all_conditions(self) -> None:
        """Verify all gate conditions exist."""
        assert GateCondition.ALL_REQUIRED.value == "all_required"
        assert GateCondition.ANY.value == "any"
        assert GateCondition.QUORUM.value == "quorum"
        assert GateCondition.CUSTOM.value == "custom"


# =============================================================================
# Proposition Tests
# =============================================================================


class TestProposition:
    """Tests for Proposition dataclass."""

    def test_basic_creation(self) -> None:
        """Create a basic proposition."""
        prop = Proposition(
            id=PropositionId("tests_pass"),
            description="All tests pass",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
        )

        assert prop.id == "tests_pass"
        assert prop.description == "All tests pass"
        assert prop.metric == MetricType.BINARY
        assert prop.threshold == 1.0
        assert prop.direction == Direction.EQ
        assert prop.required is True  # default

    def test_frozen(self) -> None:
        """Propositions are immutable."""
        prop = Proposition(
            id=PropositionId("test"),
            description="Test",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
        )

        with pytest.raises(FrozenInstanceError):
            prop.threshold = 0.5  # type: ignore[misc]

    def test_judgment_auto_sets_required(self) -> None:
        """Judgment metrics automatically set judgment_required=True."""
        prop = Proposition(
            id=PropositionId("ui_feels_right"),
            description="The UI feels right",
            metric=MetricType.JUDGMENT,
            threshold=1.0,
            direction=Direction.EQ,
            judgment_required=False,  # Should be auto-corrected
        )

        assert prop.judgment_required is True


# =============================================================================
# Gate Tests
# =============================================================================


class TestGate:
    """Tests for Gate dataclass."""

    def test_basic_creation(self) -> None:
        """Create a basic gate."""
        gate = Gate(
            id=GateId("tests_gate"),
            name="Tests Gate",
            condition=GateCondition.ALL_REQUIRED,
            proposition_ids=(PropositionId("tests_pass"), PropositionId("test_count")),
        )

        assert gate.id == "tests_gate"
        assert gate.name == "Tests Gate"
        assert gate.condition == GateCondition.ALL_REQUIRED
        assert len(gate.proposition_ids) == 2

    def test_frozen(self) -> None:
        """Gates are immutable."""
        gate = Gate(
            id=GateId("test"),
            name="Test",
            condition=GateCondition.ALL_REQUIRED,
        )

        with pytest.raises(FrozenInstanceError):
            gate.name = "Modified"  # type: ignore[misc]

    def test_quorum_gate(self) -> None:
        """Create a quorum gate."""
        gate = Gate(
            id=GateId("quorum_gate"),
            name="Quorum Gate",
            condition=GateCondition.QUORUM,
            proposition_ids=(PropositionId("p1"), PropositionId("p2"), PropositionId("p3")),
            quorum_n=2,
        )

        assert gate.condition == GateCondition.QUORUM
        assert gate.quorum_n == 2


# =============================================================================
# Initiative Tests
# =============================================================================


class TestInitiative:
    """Tests for Initiative dataclass."""

    def test_flat_initiative(self) -> None:
        """Create a flat (non-phased) initiative."""
        props = (
            Proposition(
                id=PropositionId("tests_pass"),
                description="Tests pass",
                metric=MetricType.BINARY,
                threshold=1.0,
                direction=Direction.EQ,
            ),
        )
        gate = Gate(
            id=GateId("brain_gate"),
            name="Brain Gate",
            condition=GateCondition.ALL_REQUIRED,
            proposition_ids=(PropositionId("tests_pass"),),
        )

        initiative = Initiative(
            id=InitiativeId("brain"),
            name="Brain Crown Jewel",
            description="The spatial cathedral",
            propositions=props,
            gate=gate,
        )

        assert initiative.is_phased is False
        assert len(initiative.get_all_propositions()) == 1

    def test_phased_initiative(self) -> None:
        """Create a phased initiative."""
        phase1 = Phase(
            id=PhaseId("foundations"),
            name="Phase 1: Foundations",
            gate=Gate(
                id=GateId("foundations_gate"),
                name="Foundations Gate",
                condition=GateCondition.ALL_REQUIRED,
            ),
            propositions=(
                Proposition(
                    id=PropositionId("correlation"),
                    description="Correlation exists",
                    metric=MetricType.PEARSON_R,
                    threshold=0.3,
                    direction=Direction.GT,
                ),
            ),
        )
        phase2 = Phase(
            id=PhaseId("integration"),
            name="Phase 2: Integration",
            gate=Gate(
                id=GateId("integration_gate"),
                name="Integration Gate",
                condition=GateCondition.ALL_REQUIRED,
            ),
            depends_on=(PhaseId("foundations"),),
        )

        initiative = Initiative(
            id=InitiativeId("categorical"),
            name="Categorical Reasoning",
            description="Research initiative",
            phases=(phase1, phase2),
        )

        assert initiative.is_phased is True
        assert len(initiative.phases) == 2
        assert initiative.get_phase(PhaseId("foundations")) == phase1

    def test_get_proposition(self) -> None:
        """Get proposition by ID."""
        prop = Proposition(
            id=PropositionId("tests_pass"),
            description="Tests pass",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
        )
        initiative = Initiative(
            id=InitiativeId("test"),
            name="Test",
            description="Test",
            propositions=(prop,),
            gate=Gate(
                id=GateId("gate"),
                name="Gate",
                condition=GateCondition.ALL_REQUIRED,
            ),
        )

        assert initiative.get_proposition(PropositionId("tests_pass")) == prop
        assert initiative.get_proposition(PropositionId("nonexistent")) is None


# =============================================================================
# YAML Loading Tests
# =============================================================================


class TestYAMLLoading:
    """Tests for YAML loading utilities."""

    def test_proposition_from_dict(self) -> None:
        """Load proposition from dict."""
        data = {
            "id": "tests_pass",
            "description": "All tests pass",
            "metric": "binary",
            "threshold": 1,
            "direction": "=",
            "required": True,
        }

        prop = proposition_from_dict(data)

        assert prop.id == "tests_pass"
        assert prop.metric == MetricType.BINARY
        assert prop.direction == Direction.EQ
        assert prop.threshold == 1.0

    def test_gate_from_dict(self) -> None:
        """Load gate from dict."""
        data = {
            "id": "brain_gate",
            "name": "Brain Gate",
            "condition": "all_required",
        }

        gate = gate_from_dict(data, (PropositionId("p1"), PropositionId("p2")))

        assert gate.id == "brain_gate"
        assert gate.condition == GateCondition.ALL_REQUIRED
        assert len(gate.proposition_ids) == 2

    def test_phase_from_dict(self) -> None:
        """Load phase from dict."""
        data = {
            "id": "foundations",
            "name": "Phase 1: Foundations",
            "description": "Establish foundations",
            "gate": {
                "id": "foundations_gate",
                "condition": "all_required",
            },
            "propositions": [
                {
                    "id": "correlation",
                    "description": "Correlation exists",
                    "metric": "pearson_r",
                    "threshold": 0.3,
                    "direction": ">",
                }
            ],
            "depends_on": [],
        }

        phase = phase_from_dict(data)

        assert phase.id == "foundations"
        assert len(phase.propositions) == 1
        assert phase.gate.condition == GateCondition.ALL_REQUIRED

    def test_flat_initiative_from_dict(self) -> None:
        """Load flat initiative from dict."""
        data = {
            "id": "brain",
            "name": "Brain Crown Jewel",
            "description": "The spatial cathedral",
            "propositions": [
                {
                    "id": "tests_pass",
                    "description": "All tests pass",
                    "metric": "binary",
                    "threshold": 1,
                    "direction": "=",
                }
            ],
            "gate": {
                "id": "brain_gate",
                "condition": "all_required",
            },
            "witness_tags": ["validation", "brain"],
        }

        initiative = initiative_from_dict(data)

        assert initiative.id == "brain"
        assert initiative.is_phased is False
        assert len(initiative.propositions) == 1
        assert initiative.witness_tags == ("validation", "brain")

    def test_phased_initiative_from_dict(self) -> None:
        """Load phased initiative from dict."""
        data = {
            "id": "categorical",
            "name": "Categorical Reasoning",
            "description": "Research",
            "phases": [
                {
                    "id": "foundations",
                    "name": "Phase 1",
                    "gate": {"condition": "all_required"},
                    "propositions": [
                        {
                            "id": "correlation",
                            "metric": "pearson_r",
                            "threshold": 0.3,
                            "direction": ">",
                        }
                    ],
                },
                {
                    "id": "integration",
                    "name": "Phase 2",
                    "gate": {"condition": "all_required"},
                    "depends_on": ["foundations"],
                    "propositions": [],
                },
            ],
        }

        initiative = initiative_from_dict(data)

        assert initiative.id == "categorical"
        assert initiative.is_phased is True
        assert len(initiative.phases) == 2
        assert initiative.phases[1].depends_on == (PhaseId("foundations"),)
