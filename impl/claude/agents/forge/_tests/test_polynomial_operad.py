"""
Tests for ForgeTask Polynomial and Operad.

Tests cover:
1. TaskPolynomial state machine behavior
2. TASK_OPERAD composition laws
3. Coalition compatibility checking
4. Projection protocol
5. Property-based tests for categorical laws

Run with: pytest impl/claude/agents/forge/_tests/test_polynomial_operad.py -v
"""

from __future__ import annotations

import pytest
from agents.forge.operad import (
    TASK_OPERAD,
    CoalitionCompatibility,
    check_coalition_compatibility,
)
from agents.forge.polynomial import (
    TASK_POLYNOMIAL,
    ApproveInput,
    CancelInput,
    CoalitionFormedInput,
    FailInput,
    OutputReadyInput,
    ProgressInput,
    RejectInput,
    RetryInput,
    StartInput,
    TaskPhase,
    task_directions,
    task_transition,
)
from agents.forge.templates import (
    CODE_REVIEW_TEMPLATE,
    RESEARCH_REPORT_TEMPLATE,
    TASK_TEMPLATES,
)
from hypothesis import given, settings
from hypothesis import strategies as st

# =============================================================================
# TaskPolynomial Tests
# =============================================================================


class TestTaskPhase:
    """Tests for TaskPhase enum."""

    def test_has_expected_phases(self) -> None:
        """All expected phases exist."""
        assert TaskPhase.PENDING
        assert TaskPhase.FORMING
        assert TaskPhase.EXECUTING
        assert TaskPhase.REVIEWING
        assert TaskPhase.COMPLETED
        assert TaskPhase.FAILED
        assert TaskPhase.CANCELLED

    def test_phase_count(self) -> None:
        """Correct number of phases."""
        assert len(TaskPhase) == 7


class TestTaskDirections:
    """Tests for phase-dependent valid inputs."""

    def test_pending_accepts_start_and_cancel(self) -> None:
        """PENDING phase accepts StartInput and CancelInput."""
        directions = task_directions(TaskPhase.PENDING)
        assert StartInput in directions
        assert CancelInput in directions

    def test_forming_accepts_coalition_formed(self) -> None:
        """FORMING phase accepts CoalitionFormedInput."""
        directions = task_directions(TaskPhase.FORMING)
        assert CoalitionFormedInput in directions
        assert CancelInput in directions
        assert FailInput in directions

    def test_executing_accepts_progress_and_output(self) -> None:
        """EXECUTING phase accepts progress and output."""
        directions = task_directions(TaskPhase.EXECUTING)
        assert ProgressInput in directions
        assert OutputReadyInput in directions
        assert FailInput in directions
        assert CancelInput in directions

    def test_reviewing_accepts_approve_and_reject(self) -> None:
        """REVIEWING phase accepts approval/rejection."""
        directions = task_directions(TaskPhase.REVIEWING)
        assert ApproveInput in directions
        assert RejectInput in directions
        assert CancelInput in directions

    def test_completed_is_terminal(self) -> None:
        """COMPLETED phase has no valid inputs."""
        directions = task_directions(TaskPhase.COMPLETED)
        assert len(directions) == 0

    def test_failed_accepts_retry(self) -> None:
        """FAILED phase accepts retry."""
        directions = task_directions(TaskPhase.FAILED)
        assert RetryInput in directions
        assert CancelInput in directions


class TestTaskTransition:
    """Tests for task state transitions."""

    def test_pending_to_forming(self) -> None:
        """StartInput transitions PENDING → FORMING."""
        input = StartInput(
            task_id="t1", template_id="research_report", credits_authorized=50
        )
        new_phase, output = task_transition(TaskPhase.PENDING, input)

        assert new_phase == TaskPhase.FORMING
        assert output.success
        assert output.metadata["template_id"] == "research_report"

    def test_forming_to_executing(self) -> None:
        """CoalitionFormedInput transitions FORMING → EXECUTING."""
        input = CoalitionFormedInput(coalition_id="c1", builders=("Scout", "Sage"))
        new_phase, output = task_transition(TaskPhase.FORMING, input)

        assert new_phase == TaskPhase.EXECUTING
        assert output.success
        assert output.metadata["builders"] == ("Scout", "Sage")

    def test_executing_progress(self) -> None:
        """ProgressInput stays in EXECUTING."""
        input = ProgressInput(
            progress_pct=0.5, message="Halfway done", current_builder="Scout"
        )
        new_phase, output = task_transition(TaskPhase.EXECUTING, input)

        assert new_phase == TaskPhase.EXECUTING
        assert output.success
        assert output.metadata["progress"] == 0.5

    def test_executing_to_reviewing(self) -> None:
        """OutputReadyInput transitions EXECUTING → REVIEWING."""
        input = OutputReadyInput(output={"result": "done"}, confidence=0.8)
        new_phase, output = task_transition(TaskPhase.EXECUTING, input)

        assert new_phase == TaskPhase.REVIEWING
        assert output.success
        assert output.metadata["confidence"] == 0.8

    def test_reviewing_approve(self) -> None:
        """ApproveInput transitions REVIEWING → COMPLETED."""
        new_phase, output = task_transition(TaskPhase.REVIEWING, ApproveInput())

        assert new_phase == TaskPhase.COMPLETED
        assert output.success

    def test_reviewing_reject_loops_back(self) -> None:
        """RejectInput transitions REVIEWING → EXECUTING."""
        input = RejectInput(reason="Need more detail")
        new_phase, output = task_transition(TaskPhase.REVIEWING, input)

        assert new_phase == TaskPhase.EXECUTING
        assert output.success
        assert output.metadata["rejection_reason"] == "Need more detail"

    def test_failure_to_retry(self) -> None:
        """RetryInput transitions FAILED → FORMING."""
        new_phase, output = task_transition(TaskPhase.FAILED, RetryInput())

        assert new_phase == TaskPhase.FORMING
        assert output.success
        assert output.metadata.get("retry") is True

    def test_cancel_from_any_phase(self) -> None:
        """CancelInput works from any non-terminal phase."""
        input = CancelInput(reason="User changed mind")

        for phase in [
            TaskPhase.PENDING,
            TaskPhase.FORMING,
            TaskPhase.EXECUTING,
            TaskPhase.REVIEWING,
            TaskPhase.FAILED,
        ]:
            new_phase, output = task_transition(phase, input)
            assert new_phase == TaskPhase.CANCELLED
            assert output.success

    def test_invalid_input_stays_in_phase(self) -> None:
        """Invalid input stays in current phase."""
        # Can't start from EXECUTING
        input = StartInput(task_id="t1", template_id="x", credits_authorized=10)
        new_phase, output = task_transition(TaskPhase.EXECUTING, input)

        # Should fail gracefully
        assert not output.success or new_phase == TaskPhase.EXECUTING


class TestTaskPolynomial:
    """Tests for the TASK_POLYNOMIAL agent."""

    def test_polynomial_has_correct_positions(self) -> None:
        """Polynomial has all phases as positions."""
        assert len(TASK_POLYNOMIAL.positions) == len(TaskPhase)
        for phase in TaskPhase:
            assert phase in TASK_POLYNOMIAL.positions

    def test_polynomial_name(self) -> None:
        """Polynomial has correct name."""
        assert TASK_POLYNOMIAL.name == "TaskPolynomial"


# =============================================================================
# TASK_OPERAD Tests
# =============================================================================


class TestTaskOperad:
    """Tests for TASK_OPERAD."""

    def test_operad_has_expected_operations(self) -> None:
        """Operad has seq, par, cond, retry operations."""
        assert "seq" in TASK_OPERAD.operations
        assert "par" in TASK_OPERAD.operations
        assert "cond" in TASK_OPERAD.operations
        assert "retry" in TASK_OPERAD.operations

    def test_operad_has_laws(self) -> None:
        """Operad has expected laws."""
        law_names = {law.name for law in TASK_OPERAD.laws}
        assert "associativity" in law_names
        assert "identity" in law_names
        assert "parallel_commutativity" in law_names

    def test_seq_operation_arity(self) -> None:
        """Sequential operation has arity 2."""
        assert TASK_OPERAD.operations["seq"].arity == 2

    def test_retry_operation_arity(self) -> None:
        """Retry operation has arity 1."""
        assert TASK_OPERAD.operations["retry"].arity == 1


# =============================================================================
# Coalition Compatibility Tests
# =============================================================================


class TestCoalitionCompatibility:
    """Tests for coalition compatibility checking."""

    def test_compatible_coalition(self) -> None:
        """Compatible builders pass check."""
        required = ("Scout", "Sage")
        available = [
            {"archetype": "Scout", "eigenvectors": {"analytical": 0.8}},
            {"archetype": "Sage", "eigenvectors": {"analytical": 0.9}},
        ]

        result = check_coalition_compatibility(required, available)

        assert result.compatible
        assert len(result.missing_archetypes) == 0

    def test_missing_archetype_fails(self) -> None:
        """Missing required archetype fails check."""
        required = ("Scout", "Sage", "Spark")
        available = [
            {"archetype": "Scout", "eigenvectors": {}},
            {"archetype": "Sage", "eigenvectors": {}},
        ]

        result = check_coalition_compatibility(required, available)

        assert not result.compatible
        assert "Spark" in result.missing_archetypes

    def test_eigenvector_threshold_warning(self) -> None:
        """Low eigenvector generates warning."""
        required = ("Scout",)
        available = [{"archetype": "Scout", "eigenvectors": {"analytical": 0.3}}]
        thresholds = {"analytical": 0.7}

        result = check_coalition_compatibility(required, available, thresholds)

        assert result.compatible  # Still compatible
        assert len(result.eigenvector_warnings) > 0
        assert result.score < 1.0

    def test_compatibility_score_calculation(self) -> None:
        """Compatibility score is calculated correctly."""
        required = ("Scout",)
        available = [{"archetype": "Scout", "eigenvectors": {"analytical": 0.9}}]

        result = check_coalition_compatibility(required, available)

        assert result.compatible
        assert result.score == 1.0  # Perfect match


# =============================================================================
# Projection Protocol Tests
# =============================================================================


class TestProjectionProtocol:
    """Tests for template projection methods."""

    def test_to_cli_returns_string(self) -> None:
        """to_cli() returns string."""
        result = RESEARCH_REPORT_TEMPLATE.to_cli()
        assert isinstance(result, str)
        assert "Research Report" in result
        assert "Scout" in result

    def test_to_web_returns_dict(self) -> None:
        """to_web() returns structured dict."""
        result = RESEARCH_REPORT_TEMPLATE.to_web()
        assert isinstance(result, dict)
        assert result["type"] == "task_template"
        assert result["id"] == "research_report"
        assert "coalition" in result

    def test_to_json_matches_to_web(self) -> None:
        """to_json() returns same as to_web()."""
        web_result = RESEARCH_REPORT_TEMPLATE.to_web()
        json_result = RESEARCH_REPORT_TEMPLATE.to_json()
        assert web_result == json_result

    def test_project_routes_correctly(self) -> None:
        """project() routes to correct method."""
        cli_result = RESEARCH_REPORT_TEMPLATE.project("cli")
        web_result = RESEARCH_REPORT_TEMPLATE.project("web")
        json_result = RESEARCH_REPORT_TEMPLATE.project("json")

        assert isinstance(cli_result, str)
        assert isinstance(web_result, dict)
        assert isinstance(json_result, dict)

    def test_project_default_fallback(self) -> None:
        """project() with unknown target falls back to JSON."""
        result = RESEARCH_REPORT_TEMPLATE.project("unknown")
        assert isinstance(result, dict)

    def test_all_templates_have_projections(self) -> None:
        """All templates support projection."""
        for template in TASK_TEMPLATES.values():
            cli = template.to_cli()
            web = template.to_web()

            assert isinstance(cli, str)
            assert isinstance(web, dict)
            assert "id" in web


# =============================================================================
# Property-Based Tests (Hypothesis)
# =============================================================================


class TestPropertyBasedLaws:
    """Property-based tests for operad laws."""

    @given(st.sampled_from(list(TaskPhase)))
    @settings(max_examples=20)
    def test_cancel_always_terminates(self, start_phase: TaskPhase) -> None:
        """Cancel from any non-terminal phase results in CANCELLED."""
        if start_phase in (TaskPhase.COMPLETED, TaskPhase.CANCELLED):
            return  # Skip terminal phases

        input = CancelInput(reason="test")
        new_phase, output = task_transition(start_phase, input)
        assert new_phase == TaskPhase.CANCELLED

    @given(
        st.floats(min_value=0.0, max_value=1.0),
        st.text(min_size=0, max_size=100),
    )
    @settings(max_examples=20)
    def test_progress_preserves_executing(self, progress: float, message: str) -> None:
        """Progress input preserves EXECUTING phase."""
        input = ProgressInput(progress_pct=progress, message=message)
        new_phase, output = task_transition(TaskPhase.EXECUTING, input)
        assert new_phase == TaskPhase.EXECUTING

    @given(st.sampled_from(list(TaskPhase)))
    @settings(max_examples=20)
    def test_directions_are_frozen(self, phase: TaskPhase) -> None:
        """Directions for any phase return immutable set."""
        directions = task_directions(phase)
        assert isinstance(directions, frozenset)


class TestTaskLifecycleProperties:
    """Property tests for complete task lifecycle."""

    def test_happy_path_lifecycle(self) -> None:
        """Complete happy path: PENDING → ... → COMPLETED."""
        phase = TaskPhase.PENDING

        # Start
        phase, _ = task_transition(phase, StartInput("t", "research", 50))
        assert phase == TaskPhase.FORMING

        # Form coalition
        phase, _ = task_transition(phase, CoalitionFormedInput("c", ("Scout",)))
        assert phase == TaskPhase.EXECUTING

        # Progress
        phase, _ = task_transition(phase, ProgressInput(0.5, "half"))
        assert phase == TaskPhase.EXECUTING

        # Output ready
        phase, _ = task_transition(phase, OutputReadyInput("result", 0.9))
        assert phase == TaskPhase.REVIEWING

        # Approve
        phase, _ = task_transition(phase, ApproveInput())
        assert phase == TaskPhase.COMPLETED

    def test_retry_loop(self) -> None:
        """Retry loop: FAILED → FORMING → ... → FAILED → retry."""
        # Get to FAILED state
        phase = TaskPhase.FAILED

        # Retry
        phase, _ = task_transition(phase, RetryInput())
        assert phase == TaskPhase.FORMING

        # Form again
        phase, _ = task_transition(phase, CoalitionFormedInput("c", ("Scout",)))
        assert phase == TaskPhase.EXECUTING

    def test_review_revision_loop(self) -> None:
        """Review loop: REVIEWING → EXECUTING → REVIEWING."""
        phase = TaskPhase.REVIEWING

        # Reject
        phase, _ = task_transition(phase, RejectInput("needs work"))
        assert phase == TaskPhase.EXECUTING

        # New output
        phase, _ = task_transition(phase, OutputReadyInput("v2", 0.95))
        assert phase == TaskPhase.REVIEWING

        # Approve
        phase, _ = task_transition(phase, ApproveInput())
        assert phase == TaskPhase.COMPLETED
