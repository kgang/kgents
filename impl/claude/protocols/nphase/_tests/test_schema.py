"""
Tests for N-Phase Schema.

Law tests verify structural invariants that must always hold.
"""

import pytest
from protocols.nphase.schema import (
    Blocker,
    Classification,
    Component,
    Decision,
    Effort,
    EntropyBudget,
    FileRef,
    Invariant,
    PhaseOverride,
    PhaseStatus,
    ProjectDefinition,
    ProjectScope,
    Wave,
)


class TestProjectScope:
    """Tests for ProjectScope dataclass."""

    def test_to_dict_roundtrip(self) -> None:
        """Law: from_dict(to_dict(x)) == x."""
        scope = ProjectScope(
            goal="Build the thing",
            non_goals=("Don't build other thing",),
            parallel_tracks={"T1": "Track one"},
        )
        restored = ProjectScope.from_dict(scope.to_dict())
        assert restored == scope

    def test_empty_optional_fields(self) -> None:
        """Empty optional fields should serialize cleanly."""
        scope = ProjectScope(goal="Just the goal")
        d = scope.to_dict()
        assert d["goal"] == "Just the goal"
        assert d["non_goals"] == []
        assert d["parallel_tracks"] == {}


class TestDecision:
    """Tests for Decision dataclass."""

    def test_to_dict_roundtrip(self) -> None:
        """Law: from_dict(to_dict(x)) == x."""
        dec = Decision(id="D1", choice="Use Python", rationale="Best fit")
        restored = Decision.from_dict(dec.to_dict())
        assert restored == dec


class TestFileRef:
    """Tests for FileRef dataclass."""

    def test_to_dict_roundtrip(self) -> None:
        """Law: from_dict(to_dict(x)) == x."""
        ref = FileRef(path="src/main.py", lines="10-20", purpose="Entry point")
        restored = FileRef.from_dict(ref.to_dict())
        assert restored == ref

    def test_str_with_lines(self) -> None:
        """String representation includes lines when present."""
        ref = FileRef(path="src/main.py", lines="10-20")
        assert str(ref) == "src/main.py:10-20"

    def test_str_without_lines(self) -> None:
        """String representation omits lines when absent."""
        ref = FileRef(path="src/main.py")
        assert str(ref) == "src/main.py"


class TestBlocker:
    """Tests for Blocker dataclass."""

    def test_to_dict_roundtrip(self) -> None:
        """Law: from_dict(to_dict(x)) == x."""
        blocker = Blocker(
            id="B1",
            description="No schema",
            evidence="schema.py:1",
            resolution="Define schema",
            status="resolved",
        )
        restored = Blocker.from_dict(blocker.to_dict())
        assert restored == blocker


class TestComponent:
    """Tests for Component dataclass."""

    def test_to_dict_roundtrip(self) -> None:
        """Law: from_dict(to_dict(x)) == x."""
        comp = Component(
            id="C1",
            name="Schema",
            location="schema.py",
            effort=Effort.M,
            dependencies=("C0",),
            description="The schema",
        )
        restored = Component.from_dict(comp.to_dict())
        assert restored == comp


class TestWave:
    """Tests for Wave dataclass."""

    def test_to_dict_roundtrip(self) -> None:
        """Law: from_dict(to_dict(x)) == x."""
        wave = Wave(
            name="Wave 1",
            components=("C1", "C2"),
            strategy="Foundation first",
        )
        restored = Wave.from_dict(wave.to_dict())
        assert restored == wave


class TestEntropyBudget:
    """Tests for EntropyBudget dataclass."""

    def test_remaining_calculation(self) -> None:
        """Remaining entropy is total minus spent."""
        budget = EntropyBudget(
            total=0.75,
            allocation={"PLAN": 0.10, "RESEARCH": 0.10},
            spent={"PLAN": 0.05},
        )
        assert budget.remaining() == 0.70

    def test_validate_allocation_mismatch(self) -> None:
        """Law: Allocation must sum to total."""
        budget = EntropyBudget(
            total=0.75,
            allocation={"PLAN": 0.10, "RESEARCH": 0.10},  # Sum = 0.20 != 0.75
        )
        errors = budget.validate()
        assert any("Allocation" in e for e in errors)

    def test_validate_overspent(self) -> None:
        """Law: Cannot spend more than allocated per phase."""
        budget = EntropyBudget(
            total=0.75,
            allocation={"PLAN": 0.10},
            spent={"PLAN": 0.15},  # Overspent!
        )
        errors = budget.validate()
        assert any("overspent" in e for e in errors)

    def test_validate_no_allocation_is_ok(self) -> None:
        """Empty allocation is valid (not yet planned)."""
        budget = EntropyBudget(total=0.75)
        errors = budget.validate()
        assert errors == []


class TestProjectDefinition:
    """Tests for ProjectDefinition validation."""

    @pytest.fixture
    def minimal_project(self) -> ProjectDefinition:
        """Minimal valid project."""
        return ProjectDefinition(
            name="test-project",
            classification=Classification.STANDARD,
            scope=ProjectScope(goal="Test goal"),
        )

    def test_minimal_is_valid(self, minimal_project: ProjectDefinition) -> None:
        """Minimal project should be valid (with warnings)."""
        result = minimal_project.validate()
        assert result.is_valid
        # Should have warnings about missing file_map, invariants, etc.
        assert len(result.warnings) > 0

    def test_component_ids_unique(self) -> None:
        """Law: Component IDs must be unique."""
        project = ProjectDefinition(
            name="test",
            classification=Classification.STANDARD,
            scope=ProjectScope(goal="test"),
            components=(
                Component(id="C1", name="foo", location="x.py"),
                Component(id="C1", name="bar", location="y.py"),  # Duplicate!
            ),
        )
        result = project.validate()
        assert not result.is_valid
        assert any("Duplicate component" in e for e in result.errors)

    def test_wave_references_valid_components(self) -> None:
        """Law: Wave components must reference valid component IDs."""
        project = ProjectDefinition(
            name="test",
            classification=Classification.STANDARD,
            scope=ProjectScope(goal="test"),
            components=(Component(id="C1", name="foo", location="x.py"),),
            waves=(Wave(name="Wave 1", components=("C1", "C99")),),  # C99 invalid
        )
        result = project.validate()
        assert not result.is_valid
        assert any("C99" in e for e in result.errors)

    def test_dependency_references_valid_components(self) -> None:
        """Law: Component dependencies must reference valid IDs."""
        project = ProjectDefinition(
            name="test",
            classification=Classification.STANDARD,
            scope=ProjectScope(goal="test"),
            components=(
                Component(
                    id="C1", name="foo", location="x.py", dependencies=("C99",)
                ),  # C99 invalid
            ),
        )
        result = project.validate()
        assert not result.is_valid
        assert any("C99" in e for e in result.errors)

    def test_yaml_roundtrip(self, minimal_project: ProjectDefinition) -> None:
        """Law: from_yaml(to_yaml(x)) == x."""
        yaml_str = minimal_project.to_yaml()
        restored = ProjectDefinition.from_yaml(yaml_str)
        assert restored == minimal_project

    def test_yaml_roundtrip_full(self) -> None:
        """Law: YAML roundtrip preserves all fields."""
        project = ProjectDefinition(
            name="full-project",
            classification=Classification.CROWN_JEWEL,
            scope=ProjectScope(
                goal="Full test",
                non_goals=("Not this",),
                parallel_tracks={"T1": "Track one"},
            ),
            decisions=(Decision(id="D1", choice="Python", rationale="Best"),),
            file_map=(FileRef(path="main.py", lines="1-10", purpose="Entry"),),
            invariants=(
                Invariant(name="I1", requirement="Must work", verification="Run tests"),
            ),
            blockers=(
                Blocker(id="B1", description="Issue", evidence="file:1", status="open"),
            ),
            components=(
                Component(id="C1", name="Comp", location="comp.py", effort=Effort.L),
            ),
            waves=(Wave(name="W1", components=("C1",), strategy="Do it"),),
            entropy=EntropyBudget(total=0.75, allocation={}, spent={}),
            n_phases=11,
            phase_ledger={"PLAN": PhaseStatus.TOUCHED},
            phase_overrides={"PLAN": PhaseOverride(investigations=("Look at this",))},
            session_notes="Notes here",
        )

        yaml_str = project.to_yaml()
        restored = ProjectDefinition.from_yaml(yaml_str)

        assert restored.name == project.name
        assert restored.classification == project.classification
        assert restored.scope == project.scope
        assert restored.decisions == project.decisions
        assert restored.file_map == project.file_map
        assert restored.invariants == project.invariants
        assert restored.blockers == project.blockers
        assert restored.components == project.components
        assert restored.waves == project.waves
        assert restored.entropy == project.entropy
        assert restored.n_phases == project.n_phases
        assert restored.session_notes == project.session_notes
