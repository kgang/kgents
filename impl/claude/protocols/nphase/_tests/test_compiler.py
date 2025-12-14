"""
Tests for N-Phase Prompt Compiler.

Law tests verify compilation invariants.
"""

from pathlib import Path

import pytest
from protocols.nphase.compiler import NPhasePromptCompiler, compiler
from protocols.nphase.schema import (
    Classification,
    Component,
    Decision,
    Effort,
    EntropyBudget,
    FileRef,
    Invariant,
    ProjectDefinition,
    ProjectScope,
    Wave,
)


@pytest.fixture
def sample_project() -> ProjectDefinition:
    """A fully-populated sample project for testing."""
    return ProjectDefinition(
        name="sample-project",
        classification=Classification.STANDARD,
        scope=ProjectScope(
            goal="Build the N-Phase compiler",
            non_goals=("Don't build runtime",),
            parallel_tracks={"T1": "Core", "T2": "CLI"},
        ),
        decisions=(
            Decision(id="D1", choice="Python dataclasses", rationale="Type safety"),
        ),
        file_map=(
            FileRef(path="schema.py", lines="1-100", purpose="Schema definitions"),
            FileRef(path="compiler.py", purpose="Compiler logic"),
        ),
        invariants=(
            Invariant(name="Idempotent", requirement="compile(x) == compile(x)"),
        ),
        components=(
            Component(id="C1", name="Schema", location="schema.py", effort=Effort.M),
            Component(
                id="C2",
                name="Compiler",
                location="compiler.py",
                effort=Effort.M,
                dependencies=("C1",),
            ),
        ),
        waves=(
            Wave(name="Wave 1", components=("C1",), strategy="Foundation"),
            Wave(name="Wave 2", components=("C2",), strategy="Build on foundation"),
        ),
        entropy=EntropyBudget(
            total=0.75,
            allocation={},  # No allocation means validation skipped
            spent={"PLAN": 0.03},
        ),
    )


class TestNPhasePromptCompiler:
    """Tests for the compiler."""

    def test_compile_produces_markdown(self, sample_project: ProjectDefinition) -> None:
        """Compiled output is markdown."""
        prompt = compiler.compile(sample_project)
        content = str(prompt)
        assert content.startswith("# sample-project: N-Phase Meta-Prompt")

    def test_compile_includes_project_name(
        self, sample_project: ProjectDefinition
    ) -> None:
        """Output includes project name."""
        prompt = compiler.compile(sample_project)
        assert "sample-project" in str(prompt)

    def test_compile_includes_scope(self, sample_project: ProjectDefinition) -> None:
        """Output includes project scope."""
        prompt = compiler.compile(sample_project)
        assert "Build the N-Phase compiler" in str(prompt)

    def test_compile_includes_file_map(self, sample_project: ProjectDefinition) -> None:
        """Law: compile(project) contains all file_map entries."""
        prompt = compiler.compile(sample_project)
        content = str(prompt)
        for file_ref in sample_project.file_map:
            assert file_ref.path in content

    def test_compile_includes_invariants(
        self, sample_project: ProjectDefinition
    ) -> None:
        """Law: compile(project) contains all invariants."""
        prompt = compiler.compile(sample_project)
        content = str(prompt)
        for inv in sample_project.invariants:
            assert inv.name in content

    def test_compile_includes_components(
        self, sample_project: ProjectDefinition
    ) -> None:
        """Law: compile(project) contains all components."""
        prompt = compiler.compile(sample_project)
        content = str(prompt)
        for comp in sample_project.components:
            assert comp.id in content

    def test_compile_includes_waves(self, sample_project: ProjectDefinition) -> None:
        """Law: compile(project) contains all waves."""
        prompt = compiler.compile(sample_project)
        content = str(prompt)
        for wave in sample_project.waves:
            assert wave.name in content

    def test_compile_includes_all_11_phases(
        self, sample_project: ProjectDefinition
    ) -> None:
        """11-phase mode includes all phases."""
        prompt = compiler.compile(sample_project)
        content = str(prompt)
        phases = [
            "PLAN",
            "RESEARCH",
            "DEVELOP",
            "STRATEGIZE",
            "CROSS-SYNERGIZE",
            "IMPLEMENT",
            "QA",
            "TEST",
            "EDUCATE",
            "MEASURE",
            "REFLECT",
        ]
        for phase in phases:
            assert f"Phase: {phase}" in content

    def test_compile_3_phase_mode(self) -> None:
        """3-phase mode uses compressed phases."""
        project = ProjectDefinition(
            name="quick",
            classification=Classification.QUICK_WIN,
            scope=ProjectScope(goal="Quick win"),
            n_phases=3,
        )
        prompt = compiler.compile(project)
        content = str(prompt)
        # Should have SENSE, ACT, REFLECT
        assert "Phase: SENSE" in content
        assert "Phase: ACT" in content
        assert "Phase: REFLECT" in content
        # Should NOT have individual phases
        assert "Phase: PLAN" not in content

    def test_compile_idempotent(self) -> None:
        """Law: Compiling same project twice yields same result."""
        project = ProjectDefinition(
            name="test",
            classification=Classification.STANDARD,
            scope=ProjectScope(goal="test goal"),
        )
        prompt1 = str(compiler.compile(project))
        prompt2 = str(compiler.compile(project))
        assert prompt1 == prompt2

    def test_compile_rejects_invalid(self) -> None:
        """Compiler rejects invalid projects."""
        invalid = ProjectDefinition(
            name="invalid",
            classification=Classification.STANDARD,
            scope=ProjectScope(goal="test"),
            waves=(Wave(name="W1", components=("NONEXISTENT",)),),
        )
        with pytest.raises(ValueError):
            compiler.compile(invalid)

    def test_compile_from_yaml(self) -> None:
        """compile_from_yaml works."""
        yaml_content = """
name: yaml-test
classification: standard
scope:
  goal: Test from YAML
"""
        prompt = compiler.compile_from_yaml(yaml_content)
        assert "yaml-test" in str(prompt)
        assert "Test from YAML" in str(prompt)


class TestNPhasePrompt:
    """Tests for NPhasePrompt output."""

    def test_str_returns_content(self, sample_project: ProjectDefinition) -> None:
        """str(prompt) returns the content."""
        prompt = compiler.compile(sample_project)
        assert str(prompt) == prompt.content

    def test_save_writes_file(
        self, sample_project: ProjectDefinition, tmp_path: Path
    ) -> None:
        """save() writes to file."""
        prompt = compiler.compile(sample_project)
        output_path = tmp_path / "output.md"
        prompt.save(output_path)
        assert output_path.exists()
        assert output_path.read_text() == prompt.content
