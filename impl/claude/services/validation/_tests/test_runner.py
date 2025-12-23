"""
Tests for validation runner (pure functions).

Verifies:
- Threshold checking for all directions
- Proposition result creation
- Gate evaluation for all conditions
"""

from __future__ import annotations

from datetime import datetime, timezone

import pytest

from services.validation.runner import (
    calculate_gap,
    check_gate,
    check_proposition,
    check_threshold,
    validate_initiative_flat,
    validate_phase,
)
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
)

# =============================================================================
# Threshold Checking Tests
# =============================================================================


class TestCheckThreshold:
    """Tests for threshold checking."""

    def test_greater_than(self) -> None:
        """Test > comparison."""
        assert check_threshold(0.5, 0.3, Direction.GT) is True
        assert check_threshold(0.3, 0.3, Direction.GT) is False
        assert check_threshold(0.2, 0.3, Direction.GT) is False

    def test_greater_than_or_equal(self) -> None:
        """Test >= comparison."""
        assert check_threshold(0.5, 0.3, Direction.GTE) is True
        assert check_threshold(0.3, 0.3, Direction.GTE) is True
        assert check_threshold(0.2, 0.3, Direction.GTE) is False

    def test_less_than(self) -> None:
        """Test < comparison."""
        assert check_threshold(0.2, 0.3, Direction.LT) is True
        assert check_threshold(0.3, 0.3, Direction.LT) is False
        assert check_threshold(0.5, 0.3, Direction.LT) is False

    def test_less_than_or_equal(self) -> None:
        """Test <= comparison."""
        assert check_threshold(0.2, 0.3, Direction.LTE) is True
        assert check_threshold(0.3, 0.3, Direction.LTE) is True
        assert check_threshold(0.5, 0.3, Direction.LTE) is False

    def test_equal(self) -> None:
        """Test = comparison (approximate equality)."""
        assert check_threshold(1.0, 1.0, Direction.EQ) is True
        assert check_threshold(1.0000000001, 1.0, Direction.EQ) is True  # Within tolerance
        assert check_threshold(0.9, 1.0, Direction.EQ) is False


# =============================================================================
# Proposition Checking Tests
# =============================================================================


class TestCheckProposition:
    """Tests for proposition checking."""

    def test_passing_proposition(self) -> None:
        """Proposition passes when value meets threshold."""
        prop = Proposition(
            id=PropositionId("accuracy"),
            description="Accuracy > 0.8",
            metric=MetricType.ACCURACY,
            threshold=0.8,
            direction=Direction.GT,
        )

        result = check_proposition(prop, 0.85)

        assert result.passed is True
        assert result.value == 0.85
        assert result.proposition_id == "accuracy"

    def test_failing_proposition(self) -> None:
        """Proposition fails when value doesn't meet threshold."""
        prop = Proposition(
            id=PropositionId("accuracy"),
            description="Accuracy > 0.8",
            metric=MetricType.ACCURACY,
            threshold=0.8,
            direction=Direction.GT,
        )

        result = check_proposition(prop, 0.7)

        assert result.passed is False
        assert result.value == 0.7

    def test_none_value_fails(self) -> None:
        """Proposition fails when value is None (not measured)."""
        prop = Proposition(
            id=PropositionId("accuracy"),
            description="Accuracy > 0.8",
            metric=MetricType.ACCURACY,
            threshold=0.8,
            direction=Direction.GT,
        )

        result = check_proposition(prop, None)

        assert result.passed is False
        assert result.value is None

    def test_binary_proposition(self) -> None:
        """Binary proposition (1 = pass, 0 = fail)."""
        prop = Proposition(
            id=PropositionId("tests_pass"),
            description="Tests pass",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
        )

        assert check_proposition(prop, 1.0).passed is True
        assert check_proposition(prop, 0.0).passed is False

    def test_timestamp_is_set(self) -> None:
        """Result has timestamp."""
        prop = Proposition(
            id=PropositionId("test"),
            description="Test",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
        )

        result = check_proposition(prop, 1.0)

        assert result.timestamp is not None
        assert isinstance(result.timestamp, datetime)


# =============================================================================
# Gate Checking Tests
# =============================================================================


class TestCheckGate:
    """Tests for gate checking."""

    def test_all_required_pass(self) -> None:
        """Gate passes when all required propositions pass."""
        prop1 = Proposition(
            id=PropositionId("p1"),
            description="P1",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
            required=True,
        )
        prop2 = Proposition(
            id=PropositionId("p2"),
            description="P2",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
            required=True,
        )

        gate = Gate(
            id=GateId("gate"),
            name="Gate",
            condition=GateCondition.ALL_REQUIRED,
            proposition_ids=(PropositionId("p1"), PropositionId("p2")),
        )

        results = {
            PropositionId("p1"): PropositionResult(
                proposition_id=PropositionId("p1"), value=1.0, passed=True
            ),
            PropositionId("p2"): PropositionResult(
                proposition_id=PropositionId("p2"), value=1.0, passed=True
            ),
        }
        props = {PropositionId("p1"): prop1, PropositionId("p2"): prop2}

        gate_result = check_gate(gate, results, props)

        assert gate_result.passed is True

    def test_all_required_fail(self) -> None:
        """Gate fails when any required proposition fails."""
        prop1 = Proposition(
            id=PropositionId("p1"),
            description="P1",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
            required=True,
        )
        prop2 = Proposition(
            id=PropositionId("p2"),
            description="P2",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
            required=True,
        )

        gate = Gate(
            id=GateId("gate"),
            name="Gate",
            condition=GateCondition.ALL_REQUIRED,
            proposition_ids=(PropositionId("p1"), PropositionId("p2")),
        )

        results = {
            PropositionId("p1"): PropositionResult(
                proposition_id=PropositionId("p1"), value=1.0, passed=True
            ),
            PropositionId("p2"): PropositionResult(
                proposition_id=PropositionId("p2"), value=0.0, passed=False
            ),
        }
        props = {PropositionId("p1"): prop1, PropositionId("p2"): prop2}

        gate_result = check_gate(gate, results, props)

        assert gate_result.passed is False

    def test_optional_proposition_doesnt_block(self) -> None:
        """Optional propositions don't block gate."""
        prop1 = Proposition(
            id=PropositionId("p1"),
            description="P1",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
            required=True,
        )
        prop2 = Proposition(
            id=PropositionId("p2"),
            description="P2",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
            required=False,  # Optional
        )

        gate = Gate(
            id=GateId("gate"),
            name="Gate",
            condition=GateCondition.ALL_REQUIRED,
            proposition_ids=(PropositionId("p1"), PropositionId("p2")),
        )

        results = {
            PropositionId("p1"): PropositionResult(
                proposition_id=PropositionId("p1"), value=1.0, passed=True
            ),
            PropositionId("p2"): PropositionResult(
                proposition_id=PropositionId("p2"), value=0.0, passed=False
            ),
        }
        props = {PropositionId("p1"): prop1, PropositionId("p2"): prop2}

        gate_result = check_gate(gate, results, props)

        assert gate_result.passed is True  # Optional p2 doesn't block

    def test_any_condition(self) -> None:
        """Gate passes when any proposition passes."""
        gate = Gate(
            id=GateId("gate"),
            name="Gate",
            condition=GateCondition.ANY,
            proposition_ids=(PropositionId("p1"), PropositionId("p2")),
        )

        results = {
            PropositionId("p1"): PropositionResult(
                proposition_id=PropositionId("p1"), value=0.0, passed=False
            ),
            PropositionId("p2"): PropositionResult(
                proposition_id=PropositionId("p2"), value=1.0, passed=True
            ),
        }
        props: dict[PropositionId, Proposition] = {}

        gate_result = check_gate(gate, results, props)

        assert gate_result.passed is True

    def test_quorum_condition(self) -> None:
        """Gate passes when quorum is met."""
        gate = Gate(
            id=GateId("gate"),
            name="Gate",
            condition=GateCondition.QUORUM,
            proposition_ids=(PropositionId("p1"), PropositionId("p2"), PropositionId("p3")),
            quorum_n=2,  # 2 of 3 must pass
        )

        results = {
            PropositionId("p1"): PropositionResult(
                proposition_id=PropositionId("p1"), value=1.0, passed=True
            ),
            PropositionId("p2"): PropositionResult(
                proposition_id=PropositionId("p2"), value=1.0, passed=True
            ),
            PropositionId("p3"): PropositionResult(
                proposition_id=PropositionId("p3"), value=0.0, passed=False
            ),
        }
        props: dict[PropositionId, Proposition] = {}

        gate_result = check_gate(gate, results, props)

        assert gate_result.passed is True

    def test_quorum_not_met(self) -> None:
        """Gate fails when quorum is not met."""
        gate = Gate(
            id=GateId("gate"),
            name="Gate",
            condition=GateCondition.QUORUM,
            proposition_ids=(PropositionId("p1"), PropositionId("p2"), PropositionId("p3")),
            quorum_n=2,  # 2 of 3 must pass
        )

        results = {
            PropositionId("p1"): PropositionResult(
                proposition_id=PropositionId("p1"), value=1.0, passed=True
            ),
            PropositionId("p2"): PropositionResult(
                proposition_id=PropositionId("p2"), value=0.0, passed=False
            ),
            PropositionId("p3"): PropositionResult(
                proposition_id=PropositionId("p3"), value=0.0, passed=False
            ),
        }
        props: dict[PropositionId, Proposition] = {}

        gate_result = check_gate(gate, results, props)

        assert gate_result.passed is False

    def test_missing_result_fails(self) -> None:
        """Missing proposition result counts as fail."""
        prop1 = Proposition(
            id=PropositionId("p1"),
            description="P1",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
            required=True,
        )

        gate = Gate(
            id=GateId("gate"),
            name="Gate",
            condition=GateCondition.ALL_REQUIRED,
            proposition_ids=(PropositionId("p1"),),
        )

        results: dict[PropositionId, PropositionResult] = {}  # Missing p1
        props = {PropositionId("p1"): prop1}

        gate_result = check_gate(gate, results, props)

        assert gate_result.passed is False
        assert len(gate_result.proposition_results) == 1
        assert gate_result.proposition_results[0].passed is False

    def test_custom_condition_raises(self) -> None:
        """Custom condition raises (must be handled by engine)."""
        gate = Gate(
            id=GateId("gate"),
            name="Gate",
            condition=GateCondition.CUSTOM,
            proposition_ids=(PropositionId("p1"),),  # Need at least one prop
            custom_fn="my_custom_fn",
        )

        # Provide a result so the gate actually evaluates the condition
        results = {
            PropositionId("p1"): PropositionResult(
                proposition_id=PropositionId("p1"), value=1.0, passed=True
            ),
        }

        with pytest.raises(ValueError, match="Custom gate condition"):
            check_gate(gate, results, {})


# =============================================================================
# Gap Calculation Tests
# =============================================================================


class TestCalculateGap:
    """Tests for gap calculation."""

    def test_gap_for_gt(self) -> None:
        """Gap for > direction (how much to increase)."""
        prop = Proposition(
            id=PropositionId("accuracy"),
            description="Accuracy > 0.8",
            metric=MetricType.ACCURACY,
            threshold=0.8,
            direction=Direction.GT,
        )

        # Failing: need 0.1 more
        assert calculate_gap(prop, 0.7) == pytest.approx(0.1)
        # Passing: exceeded by 0.1
        assert calculate_gap(prop, 0.9) == pytest.approx(-0.1)

    def test_gap_for_lt(self) -> None:
        """Gap for < direction (how much to decrease)."""
        prop = Proposition(
            id=PropositionId("latency"),
            description="Latency < 100ms",
            metric=MetricType.DURATION_MS,
            threshold=100,
            direction=Direction.LT,
        )

        # Failing: need to reduce by 50
        assert calculate_gap(prop, 150) == 50
        # Passing: under by 20
        assert calculate_gap(prop, 80) == -20

    def test_gap_for_eq(self) -> None:
        """Gap for = direction (absolute distance)."""
        prop = Proposition(
            id=PropositionId("binary"),
            description="Must be 1",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
        )

        assert calculate_gap(prop, 0.0) == 1.0
        assert calculate_gap(prop, 1.0) == 0.0

    def test_gap_none_value(self) -> None:
        """Gap is None when value is None."""
        prop = Proposition(
            id=PropositionId("test"),
            description="Test",
            metric=MetricType.BINARY,
            threshold=1.0,
            direction=Direction.EQ,
        )

        assert calculate_gap(prop, None) is None


# =============================================================================
# Phase/Initiative Validation Tests
# =============================================================================


class TestValidatePhase:
    """Tests for phase validation."""

    def test_validate_phase_passes(self) -> None:
        """Phase validation passes when all required props pass."""
        phase = Phase(
            id=PhaseId("foundations"),
            name="Phase 1",
            gate=Gate(
                id=GateId("gate"),
                name="Gate",
                condition=GateCondition.ALL_REQUIRED,
                proposition_ids=(PropositionId("p1"),),
            ),
            propositions=(
                Proposition(
                    id=PropositionId("p1"),
                    description="P1",
                    metric=MetricType.BINARY,
                    threshold=1.0,
                    direction=Direction.EQ,
                ),
            ),
        )

        result = validate_phase(phase, {"p1": 1.0})

        assert result.passed is True

    def test_validate_phase_fails(self) -> None:
        """Phase validation fails when required prop fails."""
        phase = Phase(
            id=PhaseId("foundations"),
            name="Phase 1",
            gate=Gate(
                id=GateId("gate"),
                name="Gate",
                condition=GateCondition.ALL_REQUIRED,
                proposition_ids=(PropositionId("p1"),),
            ),
            propositions=(
                Proposition(
                    id=PropositionId("p1"),
                    description="P1",
                    metric=MetricType.BINARY,
                    threshold=1.0,
                    direction=Direction.EQ,
                ),
            ),
        )

        result = validate_phase(phase, {"p1": 0.0})

        assert result.passed is False


class TestValidateInitiativeFlat:
    """Tests for flat initiative validation."""

    def test_validate_flat_initiative(self) -> None:
        """Validate a flat initiative."""
        initiative = Initiative(
            id=InitiativeId("brain"),
            name="Brain",
            description="Test",
            propositions=(
                Proposition(
                    id=PropositionId("tests_pass"),
                    description="Tests pass",
                    metric=MetricType.BINARY,
                    threshold=1.0,
                    direction=Direction.EQ,
                ),
            ),
            gate=Gate(
                id=GateId("gate"),
                name="Gate",
                condition=GateCondition.ALL_REQUIRED,
                proposition_ids=(PropositionId("tests_pass"),),
            ),
        )

        result = validate_initiative_flat(initiative, {"tests_pass": 1.0})

        assert result.passed is True

    def test_phased_initiative_raises(self) -> None:
        """Phased initiative raises error."""
        initiative = Initiative(
            id=InitiativeId("phased"),
            name="Phased",
            description="Test",
            phases=(
                Phase(
                    id=PhaseId("p1"),
                    name="P1",
                    gate=Gate(
                        id=GateId("gate"),
                        name="Gate",
                        condition=GateCondition.ALL_REQUIRED,
                    ),
                ),
            ),
        )

        with pytest.raises(ValueError, match="is phased"):
            validate_initiative_flat(initiative, {})
