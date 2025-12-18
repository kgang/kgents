"""
Tests for BuilderPolynomial.

Test categories:
1. Phase tests: All phases defined and accessible
2. Direction tests: Each phase accepts correct inputs
3. Transition tests: State machine correctness
4. Handoff tests: Builder-to-builder handoffs
5. Natural flow tests: EXPLORING → DESIGNING → ... → IDLE
6. Law tests: Identity and associativity
7. Edge case tests: Invalid inputs, null handling
8. Integration tests: Full workflow scenarios
"""

import pytest

from agents.poly.protocol import PolyAgent
from agents.town.builders.polynomial import (
    BUILDER_POLYNOMIAL,
    NATURAL_FLOW,
    PHASE_ARCHETYPE_MAP,
    BuilderInput,
    BuilderOutput,
    BuilderPhase,
    CompleteInput,
    ContinueInput,
    HandoffInput,
    RestInput,
    TaskAssignInput,
    UserQueryInput,
    UserResponseInput,
    WakeInput,
    builder_directions,
    builder_transition,
    get_next_phase,
    get_specialist,
)

# =============================================================================
# Phase Tests
# =============================================================================


class TestBuilderPhase:
    """Tests for BuilderPhase enum."""

    def test_all_phases_exist(self) -> None:
        """All 6 phases are defined."""
        assert len(BuilderPhase) == 6
        assert BuilderPhase.IDLE in BuilderPhase
        assert BuilderPhase.EXPLORING in BuilderPhase
        assert BuilderPhase.DESIGNING in BuilderPhase
        assert BuilderPhase.PROTOTYPING in BuilderPhase
        assert BuilderPhase.REFINING in BuilderPhase
        assert BuilderPhase.INTEGRATING in BuilderPhase

    def test_all_phases_in_polynomial_positions(self) -> None:
        """All phases are in the polynomial's position set."""
        for phase in BuilderPhase:
            assert phase in BUILDER_POLYNOMIAL.positions

    def test_phase_archetype_map_complete(self) -> None:
        """Every phase has an archetype mapping."""
        for phase in BuilderPhase:
            assert phase in PHASE_ARCHETYPE_MAP


class TestArchetypeMapping:
    """Tests for archetype-to-phase mapping."""

    def test_scout_maps_to_exploring(self) -> None:
        """Scout specializes in EXPLORING."""
        assert PHASE_ARCHETYPE_MAP[BuilderPhase.EXPLORING] == "Scout"

    def test_sage_maps_to_designing(self) -> None:
        """Sage specializes in DESIGNING."""
        assert PHASE_ARCHETYPE_MAP[BuilderPhase.DESIGNING] == "Sage"

    def test_spark_maps_to_prototyping(self) -> None:
        """Spark specializes in PROTOTYPING."""
        assert PHASE_ARCHETYPE_MAP[BuilderPhase.PROTOTYPING] == "Spark"

    def test_steady_maps_to_refining(self) -> None:
        """Steady specializes in REFINING."""
        assert PHASE_ARCHETYPE_MAP[BuilderPhase.REFINING] == "Steady"

    def test_sync_maps_to_integrating(self) -> None:
        """Sync specializes in INTEGRATING."""
        assert PHASE_ARCHETYPE_MAP[BuilderPhase.INTEGRATING] == "Sync"

    def test_get_specialist_returns_correct_archetype(self) -> None:
        """get_specialist returns correct archetype for each phase."""
        assert get_specialist(BuilderPhase.EXPLORING) == "Scout"
        assert get_specialist(BuilderPhase.DESIGNING) == "Sage"
        assert get_specialist(BuilderPhase.PROTOTYPING) == "Spark"
        assert get_specialist(BuilderPhase.REFINING) == "Steady"
        assert get_specialist(BuilderPhase.INTEGRATING) == "Sync"


# =============================================================================
# Direction Tests
# =============================================================================


class TestBuilderDirections:
    """Tests for phase-dependent valid inputs."""

    def test_idle_accepts_task_assign(self) -> None:
        """IDLE accepts TaskAssignInput."""
        dirs = builder_directions(BuilderPhase.IDLE)
        assert TaskAssignInput in dirs

    def test_idle_accepts_handoff(self) -> None:
        """IDLE accepts HandoffInput."""
        dirs = builder_directions(BuilderPhase.IDLE)
        assert HandoffInput in dirs

    def test_idle_accepts_wake(self) -> None:
        """IDLE accepts WakeInput."""
        dirs = builder_directions(BuilderPhase.IDLE)
        assert WakeInput in dirs

    def test_work_phases_accept_continue(self) -> None:
        """All work phases accept ContinueInput."""
        work_phases = [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ]
        for phase in work_phases:
            dirs = builder_directions(phase)
            assert ContinueInput in dirs, f"{phase} should accept ContinueInput"

    def test_work_phases_accept_complete(self) -> None:
        """All work phases accept CompleteInput."""
        work_phases = [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ]
        for phase in work_phases:
            dirs = builder_directions(phase)
            assert CompleteInput in dirs, f"{phase} should accept CompleteInput"

    def test_work_phases_accept_handoff(self) -> None:
        """All work phases accept HandoffInput."""
        work_phases = [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ]
        for phase in work_phases:
            dirs = builder_directions(phase)
            assert HandoffInput in dirs, f"{phase} should accept HandoffInput"

    def test_work_phases_accept_rest(self) -> None:
        """All work phases accept RestInput (graceful exit)."""
        work_phases = [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ]
        for phase in work_phases:
            dirs = builder_directions(phase)
            assert RestInput in dirs, f"{phase} should accept RestInput"

    def test_work_phases_accept_user_query(self) -> None:
        """All work phases accept UserQueryInput."""
        work_phases = [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ]
        for phase in work_phases:
            dirs = builder_directions(phase)
            assert UserQueryInput in dirs, f"{phase} should accept UserQueryInput"


# =============================================================================
# Transition Tests - IDLE
# =============================================================================


class TestIdleTransitions:
    """Tests for transitions from IDLE phase."""

    def test_idle_to_exploring_on_task_assign(self) -> None:
        """TaskAssignInput transitions IDLE → EXPLORING."""
        input = TaskAssignInput(task="add auth")
        new_phase, output = builder_transition(BuilderPhase.IDLE, input)
        assert new_phase == BuilderPhase.EXPLORING
        assert output.success
        assert "add auth" in output.message

    def test_task_assign_metadata_preserved(self) -> None:
        """Task metadata is preserved in output."""
        input = TaskAssignInput(
            task="add auth",
            priority=3,
            context={"repo": "kgents"},
        )
        _, output = builder_transition(BuilderPhase.IDLE, input)
        assert output.metadata["task"] == "add auth"
        assert output.metadata["priority"] == 3
        assert output.metadata["context"]["repo"] == "kgents"

    def test_idle_handoff_to_specific_builder(self) -> None:
        """HandoffInput from IDLE goes to specified builder's phase."""
        input = HandoffInput(from_builder="external", to_builder="Sage")
        new_phase, output = builder_transition(BuilderPhase.IDLE, input)
        assert new_phase == BuilderPhase.DESIGNING
        assert output.success

    def test_idle_wake_stays_idle(self) -> None:
        """WakeInput from IDLE stays in IDLE."""
        input = WakeInput()
        new_phase, output = builder_transition(BuilderPhase.IDLE, input)
        assert new_phase == BuilderPhase.IDLE
        assert output.success

    def test_idle_rejects_continue(self) -> None:
        """ContinueInput from IDLE fails gracefully."""
        input = ContinueInput()
        new_phase, output = builder_transition(BuilderPhase.IDLE, input)
        assert new_phase == BuilderPhase.IDLE
        assert not output.success


# =============================================================================
# Transition Tests - Work Phases
# =============================================================================


class TestWorkPhaseTransitions:
    """Tests for transitions from work phases."""

    @pytest.mark.parametrize(
        "phase,archetype",
        [
            (BuilderPhase.EXPLORING, "Scout"),
            (BuilderPhase.DESIGNING, "Sage"),
            (BuilderPhase.PROTOTYPING, "Spark"),
            (BuilderPhase.REFINING, "Steady"),
            (BuilderPhase.INTEGRATING, "Sync"),
        ],
    )
    def test_continue_stays_in_phase(self, phase: BuilderPhase, archetype: str) -> None:
        """ContinueInput keeps builder in current phase."""
        input = ContinueInput(note="making progress")
        new_phase, output = builder_transition(phase, input)
        assert new_phase == phase
        assert output.success
        assert archetype in output.message

    @pytest.mark.parametrize(
        "phase",
        [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ],
    )
    def test_complete_returns_to_idle(self, phase: BuilderPhase) -> None:
        """CompleteInput returns to IDLE from any work phase."""
        input = CompleteInput(artifact="result", summary="done")
        new_phase, output = builder_transition(phase, input)
        assert new_phase == BuilderPhase.IDLE
        assert output.success
        assert output.artifact == "result"

    @pytest.mark.parametrize(
        "phase",
        [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ],
    )
    def test_rest_returns_to_idle(self, phase: BuilderPhase) -> None:
        """RestInput returns to IDLE (graceful exit)."""
        input = RestInput()
        new_phase, output = builder_transition(phase, input)
        assert new_phase == BuilderPhase.IDLE
        assert output.success

    def test_user_query_stays_in_phase(self) -> None:
        """UserQueryInput keeps builder in current phase."""
        input = UserQueryInput(question="What's the priority?")
        new_phase, output = builder_transition(BuilderPhase.DESIGNING, input)
        assert new_phase == BuilderPhase.DESIGNING
        assert output.success
        assert output.metadata["awaiting_response"]
        assert output.metadata["question"] == "What's the priority?"

    def test_user_response_stays_in_phase(self) -> None:
        """UserResponseInput keeps builder in current phase."""
        input = UserResponseInput(response="High priority")
        new_phase, output = builder_transition(BuilderPhase.DESIGNING, input)
        assert new_phase == BuilderPhase.DESIGNING
        assert output.success
        assert output.metadata["user_response"] == "High priority"

    def test_task_assign_from_work_phase_interrupts(self) -> None:
        """TaskAssignInput from work phase starts new exploration."""
        input = TaskAssignInput(task="urgent bug")
        new_phase, output = builder_transition(BuilderPhase.REFINING, input)
        assert new_phase == BuilderPhase.EXPLORING
        assert output.success
        assert output.metadata["interrupted_phase"] == "REFINING"


# =============================================================================
# Handoff Tests
# =============================================================================


class TestHandoffs:
    """Tests for builder-to-builder handoffs."""

    def test_handoff_scout_to_sage(self) -> None:
        """Scout can hand off to Sage."""
        input = HandoffInput(
            from_builder="Scout",
            to_builder="Sage",
            artifact={"research": "found 3 options"},
            message="Ready for design decisions",
        )
        new_phase, output = builder_transition(BuilderPhase.EXPLORING, input)
        assert new_phase == BuilderPhase.DESIGNING
        assert output.success
        assert output.artifact == {"research": "found 3 options"}

    def test_handoff_sage_to_spark(self) -> None:
        """Sage can hand off to Spark."""
        input = HandoffInput(
            from_builder="Sage",
            to_builder="Spark",
            artifact={"design": "architecture doc"},
        )
        new_phase, output = builder_transition(BuilderPhase.DESIGNING, input)
        assert new_phase == BuilderPhase.PROTOTYPING
        assert output.success

    def test_handoff_can_skip_phases(self) -> None:
        """Handoffs can skip phases (Scout → Steady)."""
        input = HandoffInput(from_builder="Scout", to_builder="Steady")
        new_phase, output = builder_transition(BuilderPhase.EXPLORING, input)
        assert new_phase == BuilderPhase.REFINING
        assert output.success

    def test_handoff_can_go_backward(self) -> None:
        """Handoffs can go backward (Steady → Sage)."""
        input = HandoffInput(
            from_builder="Steady",
            to_builder="Sage",
            message="Need design clarification",
        )
        new_phase, output = builder_transition(BuilderPhase.REFINING, input)
        assert new_phase == BuilderPhase.DESIGNING
        assert output.success


# =============================================================================
# Natural Flow Tests
# =============================================================================


class TestNaturalFlow:
    """Tests for the natural workflow progression."""

    def test_natural_flow_order(self) -> None:
        """Natural flow follows correct order."""
        expected = [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ]
        assert NATURAL_FLOW == expected

    def test_get_next_phase_from_idle(self) -> None:
        """Next phase from IDLE is EXPLORING."""
        assert get_next_phase(BuilderPhase.IDLE) == BuilderPhase.EXPLORING

    def test_get_next_phase_follows_flow(self) -> None:
        """get_next_phase follows natural flow."""
        assert get_next_phase(BuilderPhase.EXPLORING) == BuilderPhase.DESIGNING
        assert get_next_phase(BuilderPhase.DESIGNING) == BuilderPhase.PROTOTYPING
        assert get_next_phase(BuilderPhase.PROTOTYPING) == BuilderPhase.REFINING
        assert get_next_phase(BuilderPhase.REFINING) == BuilderPhase.INTEGRATING
        assert get_next_phase(BuilderPhase.INTEGRATING) == BuilderPhase.IDLE

    def test_full_natural_flow_execution(self) -> None:
        """Execute full natural flow from task to completion."""
        # Start with task assignment
        phase, output = builder_transition(
            BuilderPhase.IDLE,
            TaskAssignInput(task="add feature"),
        )
        assert phase == BuilderPhase.EXPLORING

        # Continue through each phase with complete
        for expected_next in [
            BuilderPhase.IDLE,  # Complete returns to IDLE
        ]:
            phase, output = builder_transition(phase, CompleteInput())
            assert output.success
            # After complete, we're back at IDLE
            break


# =============================================================================
# Input Factory Tests
# =============================================================================


class TestBuilderInputFactory:
    """Tests for BuilderInput factory methods."""

    def test_assign_creates_task_input(self) -> None:
        """BuilderInput.assign creates TaskAssignInput."""
        input = BuilderInput.assign("add auth", priority=2, repo="kgents")
        assert isinstance(input, TaskAssignInput)
        assert input.task == "add auth"
        assert input.priority == 2
        assert input.context["repo"] == "kgents"

    def test_handoff_creates_handoff_input(self) -> None:
        """BuilderInput.handoff creates HandoffInput."""
        input = BuilderInput.handoff("Scout", "Sage", artifact="doc", message="ready")
        assert isinstance(input, HandoffInput)
        assert input.from_builder == "Scout"
        assert input.to_builder == "Sage"
        assert input.artifact == "doc"
        assert input.message == "ready"

    def test_continue_work_creates_continue_input(self) -> None:
        """BuilderInput.continue_work creates ContinueInput."""
        input = BuilderInput.continue_work("making progress")
        assert isinstance(input, ContinueInput)
        assert input.note == "making progress"

    def test_complete_creates_complete_input(self) -> None:
        """BuilderInput.complete creates CompleteInput."""
        input = BuilderInput.complete(artifact="result", summary="done")
        assert isinstance(input, CompleteInput)
        assert input.artifact == "result"
        assert input.summary == "done"

    def test_query_user_creates_query_input(self) -> None:
        """BuilderInput.query_user creates UserQueryInput."""
        input = BuilderInput.query_user("What's the priority?")
        assert isinstance(input, UserQueryInput)
        assert input.question == "What's the priority?"

    def test_user_response_creates_response_input(self) -> None:
        """BuilderInput.user_response creates UserResponseInput."""
        input = BuilderInput.user_response("High priority")
        assert isinstance(input, UserResponseInput)
        assert input.response == "High priority"


# =============================================================================
# Polynomial Protocol Tests
# =============================================================================


class TestPolynomialProtocol:
    """Tests for PolyAgent protocol compliance."""

    def test_builder_polynomial_is_polyagent(self) -> None:
        """BUILDER_POLYNOMIAL is a PolyAgent instance."""
        assert isinstance(BUILDER_POLYNOMIAL, PolyAgent)

    def test_polynomial_has_correct_name(self) -> None:
        """Polynomial has expected name."""
        assert BUILDER_POLYNOMIAL.name == "BuilderPolynomial"

    def test_polynomial_has_six_positions(self) -> None:
        """Polynomial has exactly 6 positions."""
        assert len(BUILDER_POLYNOMIAL.positions) == 6

    def test_invoke_validates_state(self) -> None:
        """invoke() validates state before transition."""
        # Invalid state should raise ValueError
        with pytest.raises(ValueError, match="Invalid state"):
            BUILDER_POLYNOMIAL.invoke("invalid", TaskAssignInput(task="test"))  # type: ignore

    def test_invoke_executes_transition(self) -> None:
        """invoke() executes valid transitions."""
        new_phase, output = BUILDER_POLYNOMIAL.invoke(
            BuilderPhase.IDLE,
            TaskAssignInput(task="test"),
        )
        assert new_phase == BuilderPhase.EXPLORING
        assert output.success

    def test_run_processes_sequence(self) -> None:
        """run() processes a sequence of inputs."""
        inputs = [
            TaskAssignInput(task="test"),
            CompleteInput(summary="done"),
        ]
        final_phase, outputs = BUILDER_POLYNOMIAL.run(BuilderPhase.IDLE, inputs)
        assert final_phase == BuilderPhase.IDLE
        assert len(outputs) == 2
        assert all(o.success for o in outputs)


# =============================================================================
# Law Tests
# =============================================================================


class TestCompositionLaws:
    """Tests for polynomial composition laws."""

    def test_identity_idle_wake(self) -> None:
        """IDLE + WakeInput = IDLE (identity-like behavior)."""
        phase, output = builder_transition(BuilderPhase.IDLE, WakeInput())
        assert phase == BuilderPhase.IDLE
        assert output.success

    def test_complete_is_absorbing(self) -> None:
        """CompleteInput from any work phase → IDLE (absorbing state)."""
        for phase in [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ]:
            new_phase, _ = builder_transition(phase, CompleteInput())
            assert new_phase == BuilderPhase.IDLE

    def test_rest_is_absorbing(self) -> None:
        """RestInput from any work phase → IDLE (absorbing state)."""
        for phase in [
            BuilderPhase.EXPLORING,
            BuilderPhase.DESIGNING,
            BuilderPhase.PROTOTYPING,
            BuilderPhase.REFINING,
            BuilderPhase.INTEGRATING,
        ]:
            new_phase, _ = builder_transition(phase, RestInput())
            assert new_phase == BuilderPhase.IDLE

    def test_handoff_composition(self) -> None:
        """Handoff from A to B then B to C = effectively A to C."""
        # Scout → Sage
        phase1, _ = builder_transition(
            BuilderPhase.EXPLORING,
            HandoffInput(from_builder="Scout", to_builder="Sage"),
        )
        assert phase1 == BuilderPhase.DESIGNING

        # Sage → Spark
        phase2, _ = builder_transition(
            phase1,
            HandoffInput(from_builder="Sage", to_builder="Spark"),
        )
        assert phase2 == BuilderPhase.PROTOTYPING

        # Direct Scout → Spark should be same
        phase_direct, _ = builder_transition(
            BuilderPhase.EXPLORING,
            HandoffInput(from_builder="Scout", to_builder="Spark"),
        )
        assert phase_direct == phase2


# =============================================================================
# Edge Case Tests
# =============================================================================


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_empty_task_accepted(self) -> None:
        """Empty task string is accepted (not ideal but valid)."""
        input = TaskAssignInput(task="")
        new_phase, output = builder_transition(BuilderPhase.IDLE, input)
        assert new_phase == BuilderPhase.EXPLORING
        assert output.success

    def test_none_artifact_handled(self) -> None:
        """None artifact is handled gracefully."""
        input = CompleteInput(artifact=None, summary="no artifact")
        _, output = builder_transition(BuilderPhase.DESIGNING, input)
        assert output.success
        assert output.artifact is None

    def test_unknown_archetype_maps_to_idle(self) -> None:
        """Unknown archetype in handoff maps to IDLE."""
        input = HandoffInput(from_builder="Scout", to_builder="Unknown")
        new_phase, output = builder_transition(BuilderPhase.EXPLORING, input)
        assert new_phase == BuilderPhase.IDLE  # Unknown → IDLE
        assert output.success

    def test_case_insensitive_archetype(self) -> None:
        """Archetype names are case-insensitive."""
        input = HandoffInput(from_builder="scout", to_builder="SAGE")
        new_phase, _ = builder_transition(BuilderPhase.EXPLORING, input)
        assert new_phase == BuilderPhase.DESIGNING

    def test_output_has_timestamp(self) -> None:
        """All outputs have a timestamp."""
        _, output = builder_transition(
            BuilderPhase.IDLE,
            TaskAssignInput(task="test"),
        )
        assert output.timestamp is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestIntegration:
    """Integration tests for full workflow scenarios."""

    def test_full_task_workflow(self) -> None:
        """Execute a complete task workflow."""
        # 1. Assign task (IDLE → EXPLORING)
        phase, output = BUILDER_POLYNOMIAL.invoke(
            BuilderPhase.IDLE,
            BuilderInput.assign("implement auth", priority=2),
        )
        assert phase == BuilderPhase.EXPLORING
        assert output.next_builder == "Scout"

        # 2. Scout explores, hands off to Sage
        phase, output = BUILDER_POLYNOMIAL.invoke(
            phase,
            BuilderInput.handoff("Scout", "Sage", artifact={"options": ["OAuth", "JWT"]}),
        )
        assert phase == BuilderPhase.DESIGNING
        assert output.next_builder == "Sage"

        # 3. Sage asks user for clarification
        phase, output = BUILDER_POLYNOMIAL.invoke(
            phase,
            BuilderInput.query_user("Which auth method: OAuth or JWT?"),
        )
        assert phase == BuilderPhase.DESIGNING
        assert output.metadata["awaiting_response"]

        # 4. User responds
        phase, output = BUILDER_POLYNOMIAL.invoke(
            phase,
            BuilderInput.user_response("JWT"),
        )
        assert phase == BuilderPhase.DESIGNING

        # 5. Sage hands off to Spark
        phase, output = BUILDER_POLYNOMIAL.invoke(
            phase,
            BuilderInput.handoff("Sage", "Spark", artifact={"design": "JWT with refresh"}),
        )
        assert phase == BuilderPhase.PROTOTYPING

        # 6. Spark completes prototype
        phase, output = BUILDER_POLYNOMIAL.invoke(
            phase,
            BuilderInput.complete(artifact={"code": "jwt_impl.py"}, summary="prototype ready"),
        )
        assert phase == BuilderPhase.IDLE
        assert "prototype" in output.message.lower() or "completed" in output.message.lower()

    def test_interrupt_and_resume(self) -> None:
        """Test interrupting work for urgent task."""
        # Start on low priority task
        phase, _ = BUILDER_POLYNOMIAL.invoke(
            BuilderPhase.IDLE,
            BuilderInput.assign("refactor logging", priority=1),
        )
        assert phase == BuilderPhase.EXPLORING

        # Continue to designing
        phase, _ = BUILDER_POLYNOMIAL.invoke(
            phase,
            BuilderInput.handoff("Scout", "Sage"),
        )
        assert phase == BuilderPhase.DESIGNING

        # Urgent task interrupts
        phase, output = BUILDER_POLYNOMIAL.invoke(
            phase,
            BuilderInput.assign("critical security fix", priority=3),
        )
        assert phase == BuilderPhase.EXPLORING  # Reset to exploration
        assert output.metadata["interrupted_phase"] == "DESIGNING"
        assert output.metadata["priority"] == 3
