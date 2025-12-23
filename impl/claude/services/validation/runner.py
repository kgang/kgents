"""
Validation Runner: Pure threshold validation functions.

No side effects, no persistence—just comparisons.

Design Philosophy:
- Pure functions (no IO, no state)
- Proposition → value → result
- Gate → results → decision
"""

from __future__ import annotations

from datetime import datetime, timezone

from .schema import (
    Direction,
    Gate,
    GateCondition,
    GateResult,
    Initiative,
    Phase,
    Proposition,
    PropositionId,
    PropositionResult,
)

# =============================================================================
# Proposition Checking
# =============================================================================


def check_threshold(value: float, threshold: float, direction: Direction) -> bool:
    """
    Check if a value meets a threshold in the given direction.

    Pure comparison function.
    """
    match direction:
        case Direction.GT:
            return value > threshold
        case Direction.GTE:
            return value >= threshold
        case Direction.LT:
            return value < threshold
        case Direction.LTE:
            return value <= threshold
        case Direction.EQ:
            # Use approximate equality for floats
            return abs(value - threshold) < 1e-9


def check_proposition(
    proposition: Proposition,
    value: float | None,
    timestamp: datetime | None = None,
) -> PropositionResult:
    """
    Check if a measured value satisfies a proposition.

    Args:
        proposition: The proposition to check
        value: The measured value (None if not measured)
        timestamp: When the check was performed (defaults to now)

    Returns:
        PropositionResult with pass/fail status
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    # If not measured, it fails
    if value is None:
        return PropositionResult(
            proposition_id=proposition.id,
            value=None,
            passed=False,
            timestamp=timestamp,
        )

    # Check threshold
    passed = check_threshold(value, proposition.threshold, proposition.direction)

    return PropositionResult(
        proposition_id=proposition.id,
        value=value,
        passed=passed,
        timestamp=timestamp,
    )


# =============================================================================
# Gate Checking
# =============================================================================


def check_gate(
    gate: Gate,
    proposition_results: dict[PropositionId, PropositionResult],
    propositions: dict[PropositionId, Proposition],
    timestamp: datetime | None = None,
) -> GateResult:
    """
    Evaluate a gate based on proposition results.

    Args:
        gate: The gate to evaluate
        proposition_results: Map of proposition ID to result
        propositions: Map of proposition ID to proposition (for required flag)
        timestamp: When the check was performed

    Returns:
        GateResult with pass/fail status
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    # Collect results for propositions in this gate
    results: list[PropositionResult] = []
    for prop_id in gate.proposition_ids:
        if prop_id in proposition_results:
            results.append(proposition_results[prop_id])
        else:
            # Missing result = fail
            results.append(
                PropositionResult(
                    proposition_id=prop_id,
                    value=None,
                    passed=False,
                    timestamp=timestamp,
                )
            )

    # Evaluate gate condition
    passed = _evaluate_gate_condition(gate, results, propositions)

    return GateResult(
        gate_id=gate.id,
        proposition_results=tuple(results),
        passed=passed,
        timestamp=timestamp,
    )


def _evaluate_gate_condition(
    gate: Gate,
    results: list[PropositionResult],
    propositions: dict[PropositionId, Proposition],
) -> bool:
    """
    Evaluate gate condition based on results.

    Internal function—no timestamp handling.
    """
    if not results:
        # Empty gate passes (vacuous truth)
        # Note: This is flagged as an anti-pattern in the spec
        return True

    match gate.condition:
        case GateCondition.ALL_REQUIRED:
            # All required propositions must pass
            for result in results:
                prop = propositions.get(result.proposition_id)
                if prop and prop.required and not result.passed:
                    return False
            return True

        case GateCondition.ANY:
            # Any proposition passes
            return any(r.passed for r in results)

        case GateCondition.QUORUM:
            # N of M must pass
            passed_count = sum(1 for r in results if r.passed)
            return passed_count >= gate.quorum_n

        case GateCondition.CUSTOM:
            # Custom function not implemented in runner
            # Should be handled by engine
            raise ValueError(f"Custom gate condition '{gate.custom_fn}' must be handled by engine")


# =============================================================================
# Initiative/Phase Validation
# =============================================================================


def validate_phase(
    phase: Phase,
    measurements: dict[str, float],
    timestamp: datetime | None = None,
) -> GateResult:
    """
    Validate a phase with provided measurements.

    Args:
        phase: The phase to validate
        measurements: Map of proposition ID to measured value
        timestamp: When the validation was performed

    Returns:
        GateResult for the phase's gate
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    # Check each proposition
    proposition_results: dict[PropositionId, PropositionResult] = {}
    propositions: dict[PropositionId, Proposition] = {}

    for prop in phase.propositions:
        propositions[prop.id] = prop
        value = measurements.get(str(prop.id))
        proposition_results[prop.id] = check_proposition(prop, value, timestamp)

    # Check gate
    return check_gate(phase.gate, proposition_results, propositions, timestamp)


def validate_initiative_flat(
    initiative: Initiative,
    measurements: dict[str, float],
    timestamp: datetime | None = None,
) -> GateResult:
    """
    Validate a flat (non-phased) initiative.

    Args:
        initiative: The initiative to validate
        measurements: Map of proposition ID to measured value
        timestamp: When the validation was performed

    Returns:
        GateResult for the initiative's gate
    """
    if timestamp is None:
        timestamp = datetime.now(timezone.utc)

    if initiative.is_phased:
        raise ValueError(f"Initiative {initiative.id} is phased, use validate_phase")

    if initiative.gate is None:
        raise ValueError(f"Initiative {initiative.id} has no gate")

    # Check each proposition
    proposition_results: dict[PropositionId, PropositionResult] = {}
    propositions: dict[PropositionId, Proposition] = {}

    for prop in initiative.propositions:
        propositions[prop.id] = prop
        value = measurements.get(str(prop.id))
        proposition_results[prop.id] = check_proposition(prop, value, timestamp)

    # Check gate
    return check_gate(initiative.gate, proposition_results, propositions, timestamp)


# =============================================================================
# Gap Calculation
# =============================================================================


def calculate_gap(proposition: Proposition, value: float | None) -> float | None:
    """
    Calculate how far a value is from the threshold.

    Returns:
        - Positive if failing (still needs to improve)
        - Negative if passing (exceeded threshold)
        - None if value is None
    """
    if value is None:
        return None

    match proposition.direction:
        case Direction.GT | Direction.GTE:
            # Need to go higher
            return proposition.threshold - value
        case Direction.LT | Direction.LTE:
            # Need to go lower
            return value - proposition.threshold
        case Direction.EQ:
            return abs(value - proposition.threshold)
