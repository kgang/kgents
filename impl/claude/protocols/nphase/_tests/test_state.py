"""
Tests for N-Phase State Management.

Law tests verify state update invariants.
"""

import json
from pathlib import Path

import pytest
from protocols.nphase.schema import (
    Blocker,
    Classification,
    EntropyBudget,
    PhaseStatus,
    ProjectDefinition,
    ProjectScope,
)
from protocols.nphase.state import (
    CumulativeState,
    Handle,
    NPhaseStateUpdater,
    PhaseOutput,
    state_updater,
)


class TestHandle:
    """Tests for Handle dataclass."""

    def test_creation(self) -> None:
        """Handle can be created."""
        handle = Handle(name="schema.md", location="plans/", phase="DEVELOP")
        assert handle.name == "schema.md"
        assert handle.location == "plans/"
        assert handle.phase == "DEVELOP"


class TestPhaseOutput:
    """Tests for PhaseOutput dataclass."""

    def test_to_dict_roundtrip(self) -> None:
        """Law: from_dict(to_dict(x)) == x."""
        output = PhaseOutput(
            phase="PLAN",
            handles=(Handle(name="scope.md", location="plans/", phase="PLAN"),),
            entropy_spent=0.03,
            notes="Started planning",
            blocker_resolutions={"B1": "Resolved with schema"},
        )
        restored = PhaseOutput.from_dict(output.to_dict())
        assert restored.phase == output.phase
        assert len(restored.handles) == len(output.handles)
        assert restored.entropy_spent == output.entropy_spent
        assert restored.notes == output.notes
        assert restored.blocker_resolutions == output.blocker_resolutions


class TestCumulativeState:
    """Tests for CumulativeState dataclass."""

    def test_empty_factory(self) -> None:
        """empty() creates valid empty state."""
        state = CumulativeState.empty()
        assert state.handles == []
        assert state.entropy_spent == {}
        assert state.phase_outputs == []

    def test_to_dict_roundtrip(self) -> None:
        """Law: from_dict(to_dict(x)) == x."""
        state = CumulativeState(
            handles=[Handle(name="x.md", location="plans/", phase="PLAN")],
            entropy_spent={"PLAN": 0.05},
            phase_outputs=[PhaseOutput(phase="PLAN", entropy_spent=0.05)],
        )
        restored = CumulativeState.from_dict(state.to_dict())
        assert len(restored.handles) == len(state.handles)
        assert restored.entropy_spent == state.entropy_spent
        assert len(restored.phase_outputs) == len(state.phase_outputs)

    def test_save_load_roundtrip(self, tmp_path: Path) -> None:
        """Law: load(save(x)) == x."""
        state = CumulativeState(
            handles=[Handle(name="x.md", location="plans/", phase="PLAN")],
            entropy_spent={"PLAN": 0.05},
            phase_outputs=[],
        )
        path = tmp_path / "state.json"
        state.save(path)
        loaded = CumulativeState.load(path)
        assert len(loaded.handles) == len(state.handles)
        assert loaded.entropy_spent == state.entropy_spent


class TestNPhaseStateUpdater:
    """Tests for NPhaseStateUpdater."""

    @pytest.fixture
    def project(self) -> ProjectDefinition:
        """Sample project with entropy."""
        return ProjectDefinition(
            name="test",
            classification=Classification.STANDARD,
            scope=ProjectScope(goal="test"),
            entropy=EntropyBudget(
                total=0.75,
                allocation={"PLAN": 0.10, "RESEARCH": 0.15},
                spent={},
            ),
            blockers=(
                Blocker(id="B1", description="Issue", evidence="file:1", status="open"),
            ),
        )

    def test_update_adds_handles(self, project: ProjectDefinition) -> None:
        """Law: Update adds handles to state."""
        state = CumulativeState.empty()
        output = PhaseOutput(
            phase="PLAN",
            handles=(Handle(name="scope.md", location="plans/", phase="PLAN"),),
        )
        _, new_state = state_updater.update(project, state, output)
        assert len(new_state.handles) == 1
        assert new_state.handles[0].name == "scope.md"

    def test_update_accumulates_handles(self, project: ProjectDefinition) -> None:
        """Law: State only grows (handles accumulate)."""
        state = CumulativeState.empty()

        # First update
        output1 = PhaseOutput(
            phase="PLAN",
            handles=(Handle(name="scope.md", location="plans/", phase="PLAN"),),
        )
        project1, state1 = state_updater.update(project, state, output1)

        # Second update
        output2 = PhaseOutput(
            phase="RESEARCH",
            handles=(Handle(name="files.md", location="plans/", phase="RESEARCH"),),
        )
        _, state2 = state_updater.update(project1, state1, output2)

        # All handles preserved
        assert len(state2.handles) == 2
        assert state2.handles[0].name == "scope.md"
        assert state2.handles[1].name == "files.md"

    def test_update_tracks_entropy(self, project: ProjectDefinition) -> None:
        """Law: Entropy spent is tracked correctly."""
        state = CumulativeState.empty()
        output = PhaseOutput(phase="PLAN", entropy_spent=0.03)
        new_project, new_state = state_updater.update(project, state, output)

        # State tracks entropy
        assert new_state.entropy_spent["PLAN"] == 0.03

        # Project entropy updated
        assert new_project.entropy is not None
        assert new_project.entropy.spent["PLAN"] == 0.03

    def test_update_accumulates_entropy(self, project: ProjectDefinition) -> None:
        """Law: Entropy accumulates across updates."""
        state = CumulativeState.empty()

        output1 = PhaseOutput(phase="PLAN", entropy_spent=0.02)
        project1, state1 = state_updater.update(project, state, output1)

        output2 = PhaseOutput(phase="PLAN", entropy_spent=0.03)
        project2, state2 = state_updater.update(project1, state1, output2)

        assert state2.entropy_spent["PLAN"] == 0.05
        assert project2.entropy is not None
        assert project2.entropy.spent["PLAN"] == 0.05

    def test_update_marks_phase_touched(self, project: ProjectDefinition) -> None:
        """Law: Phase ledger updates on completion."""
        state = CumulativeState.empty()
        output = PhaseOutput(phase="PLAN")
        new_project, _ = state_updater.update(project, state, output)

        assert new_project.phase_ledger["PLAN"] == PhaseStatus.TOUCHED

    def test_update_resolves_blockers(self, project: ProjectDefinition) -> None:
        """Law: Blocker resolutions are applied."""
        state = CumulativeState.empty()
        output = PhaseOutput(
            phase="DEVELOP",
            blocker_resolutions={"B1": "Fixed with new schema"},
        )
        new_project, _ = state_updater.update(project, state, output)

        # Blocker should be resolved
        assert len(new_project.blockers) == 1
        assert new_project.blockers[0].status == "resolved"
        assert new_project.blockers[0].resolution == "Fixed with new schema"

    def test_state_monotonic(self, project: ProjectDefinition) -> None:
        """Law: State only grows, never shrinks."""
        state = CumulativeState.empty()

        # First update
        output1 = PhaseOutput(
            phase="PLAN",
            handles=(Handle(name="scope.md", location="plans/", phase="PLAN"),),
            entropy_spent=0.03,
        )
        project1, state1 = state_updater.update(project, state, output1)

        # Second update
        output2 = PhaseOutput(
            phase="RESEARCH",
            handles=(Handle(name="files.md", location="plans/", phase="RESEARCH"),),
            entropy_spent=0.04,
        )
        project2, state2 = state_updater.update(project1, state1, output2)

        # Verify monotonicity
        assert len(state2.handles) >= len(state1.handles)
        assert len(state2.phase_outputs) >= len(state1.phase_outputs)
        assert sum(state2.entropy_spent.values()) >= sum(state1.entropy_spent.values())
