"""
Tests for Target Selection (Foundry Phase 2).

Tests the mapping from (Reality, Context, Stability) → Target.

The key safety invariant:
    CHAOTIC reality OR unstable code → WASM (forced, unconditional)

This is the zero-trust safety net. All other target selection is
context-dependent and can be overridden.
"""

from __future__ import annotations

import pytest

from agents.j.chaosmonger import StabilityMetrics, StabilityResult
from agents.j.reality import Reality
from agents.j.target_selector import (
    Target,
    TargetSelectionOutput,
    is_sandbox_required,
    recommend_target_for_code,
    select_target,
    select_target_with_reason,
)

# --- Fixtures ---


@pytest.fixture
def stable_result() -> StabilityResult:
    """A stable Chaosmonger result."""
    return StabilityResult(
        is_stable=True,
        metrics=StabilityMetrics(
            cyclomatic_complexity=5,
            branching_factor=2,
            import_risk=0.1,
            has_unbounded_recursion=False,
            estimated_runtime="O(n)",
            import_count=2,
            function_count=3,
            max_nesting_depth=2,
        ),
        violations=(),
    )


@pytest.fixture
def unstable_result() -> StabilityResult:
    """An unstable Chaosmonger result."""
    return StabilityResult(
        is_stable=False,
        metrics=StabilityMetrics(
            cyclomatic_complexity=50,
            branching_factor=10,
            import_risk=0.9,
            has_unbounded_recursion=True,
            estimated_runtime="unbounded",
            import_count=15,
            function_count=20,
            max_nesting_depth=8,
        ),
        violations=(
            "Cyclomatic complexity (50) exceeds threshold (20)",
            "Unbounded recursion detected",
            "Import risk (0.9) exceeds threshold",
        ),
    )


# --- Core Safety Tests ---


class TestChaoticRealityForcesWASM:
    """CHAOTIC reality ALWAYS forces WASM sandbox."""

    def test_chaotic_with_empty_context(self) -> None:
        """CHAOTIC + empty context → WASM."""
        target = select_target(Reality.CHAOTIC, {})
        assert target == Target.WASM

    def test_chaotic_with_production_context(self) -> None:
        """CHAOTIC + production=True → still WASM (safety first)."""
        target = select_target(Reality.CHAOTIC, {"production": True})
        assert target == Target.WASM

    def test_chaotic_with_interactive_context(self) -> None:
        """CHAOTIC + interactive=True → still WASM."""
        target = select_target(Reality.CHAOTIC, {"interactive": True})
        assert target == Target.WASM

    def test_chaotic_with_explicit_local_override(self) -> None:
        """CHAOTIC + target='local' → still WASM (cannot bypass safety)."""
        # The explicit override should be IGNORED for chaotic reality
        target = select_target(Reality.CHAOTIC, {"target": "local"})
        assert target == Target.WASM

    def test_chaotic_forces_flag(self) -> None:
        """CHAOTIC selection should have forced=True."""
        result = select_target_with_reason(Reality.CHAOTIC, {})
        assert result.forced is True
        assert "CHAOTIC" in result.reason
        assert "WASM" in result.reason


class TestUnstableCodeForcesWASM:
    """Unstable code (per Chaosmonger) ALWAYS forces WASM sandbox."""

    def test_deterministic_but_unstable(self, unstable_result: StabilityResult) -> None:
        """DETERMINISTIC + unstable → WASM (safety overrides)."""
        target = select_target(Reality.DETERMINISTIC, {}, unstable_result)
        assert target == Target.WASM

    def test_probabilistic_but_unstable(self, unstable_result: StabilityResult) -> None:
        """PROBABILISTIC + unstable → WASM."""
        target = select_target(Reality.PROBABILISTIC, {}, unstable_result)
        assert target == Target.WASM

    def test_unstable_with_production(self, unstable_result: StabilityResult) -> None:
        """Unstable + production=True → still WASM."""
        target = select_target(Reality.PROBABILISTIC, {"production": True}, unstable_result)
        assert target == Target.WASM

    def test_unstable_forces_flag(self, unstable_result: StabilityResult) -> None:
        """Unstable selection should have forced=True."""
        result = select_target_with_reason(Reality.DETERMINISTIC, {}, unstable_result)
        assert result.forced is True
        assert "Unstable" in result.reason
        # Should include violation info
        assert "complexity" in result.reason.lower() or "recursion" in result.reason.lower()


# --- Deterministic Reality Tests ---


class TestDeterministicReality:
    """DETERMINISTIC reality → LOCAL (fast in-process execution)."""

    def test_deterministic_default(self) -> None:
        """DETERMINISTIC + empty context → LOCAL."""
        target = select_target(Reality.DETERMINISTIC, {})
        assert target == Target.LOCAL

    def test_deterministic_stable(self, stable_result: StabilityResult) -> None:
        """DETERMINISTIC + stable → LOCAL."""
        target = select_target(Reality.DETERMINISTIC, {}, stable_result)
        assert target == Target.LOCAL

    def test_deterministic_reason(self) -> None:
        """DETERMINISTIC selection includes reasoning."""
        result = select_target_with_reason(Reality.DETERMINISTIC, {})
        assert result.target == Target.LOCAL
        assert result.forced is False
        assert "DETERMINISTIC" in result.reason
        assert "LOCAL" in result.reason


# --- Probabilistic Reality Tests ---


class TestProbabilisticReality:
    """PROBABILISTIC reality → context-dependent target."""

    def test_probabilistic_default(self) -> None:
        """PROBABILISTIC + empty context → CLI (default)."""
        target = select_target(Reality.PROBABILISTIC, {})
        assert target == Target.CLI

    def test_probabilistic_interactive(self) -> None:
        """PROBABILISTIC + interactive → MARIMO."""
        target = select_target(Reality.PROBABILISTIC, {"interactive": True})
        assert target == Target.MARIMO

    def test_probabilistic_production(self) -> None:
        """PROBABILISTIC + production → K8S."""
        target = select_target(Reality.PROBABILISTIC, {"production": True})
        assert target == Target.K8S

    def test_probabilistic_container(self) -> None:
        """PROBABILISTIC + container → DOCKER."""
        target = select_target(Reality.PROBABILISTIC, {"container": True})
        assert target == Target.DOCKER

    def test_probabilistic_interactive_reason(self) -> None:
        """PROBABILISTIC + interactive includes MARIMO reasoning."""
        result = select_target_with_reason(Reality.PROBABILISTIC, {"interactive": True})
        assert result.target == Target.MARIMO
        assert "MARIMO" in result.reason
        assert "exploration" in result.reason.lower()


# --- Explicit Override Tests ---


class TestExplicitOverride:
    """Explicit target overrides (when allowed)."""

    def test_explicit_k8s_override(self) -> None:
        """Explicit target='k8s' overrides default."""
        target = select_target(Reality.PROBABILISTIC, {"target": "k8s"})
        assert target == Target.K8S

    def test_explicit_docker_override(self) -> None:
        """Explicit target='docker' overrides default."""
        target = select_target(Reality.PROBABILISTIC, {"target": "docker"})
        assert target == Target.DOCKER

    def test_explicit_wasm_override(self) -> None:
        """Explicit target='wasm' is allowed."""
        target = select_target(Reality.DETERMINISTIC, {"target": "wasm"})
        assert target == Target.WASM

    def test_invalid_target_string_ignored(self) -> None:
        """Invalid target string falls through to default."""
        # Invalid target should be ignored, fall to default
        target = select_target(Reality.PROBABILISTIC, {"target": "invalid"})
        assert target == Target.CLI  # Default for PROBABILISTIC


# --- is_sandbox_required Tests ---


class TestIsSandboxRequired:
    """Tests for the is_sandbox_required helper."""

    def test_chaotic_requires_sandbox(self) -> None:
        """CHAOTIC requires sandbox."""
        assert is_sandbox_required(Reality.CHAOTIC) is True

    def test_deterministic_no_sandbox(self) -> None:
        """DETERMINISTIC does not require sandbox."""
        assert is_sandbox_required(Reality.DETERMINISTIC) is False

    def test_probabilistic_no_sandbox(self) -> None:
        """PROBABILISTIC does not require sandbox by itself."""
        assert is_sandbox_required(Reality.PROBABILISTIC) is False

    def test_unstable_requires_sandbox(self, unstable_result: StabilityResult) -> None:
        """Unstable code requires sandbox."""
        assert is_sandbox_required(Reality.DETERMINISTIC, unstable_result) is True

    def test_stable_no_sandbox(self, stable_result: StabilityResult) -> None:
        """Stable code does not require sandbox."""
        assert is_sandbox_required(Reality.DETERMINISTIC, stable_result) is False


# --- recommend_target_for_code Tests ---


class TestRecommendTargetForCode:
    """Tests for the complete pipeline function."""

    def test_simple_code_deterministic(self) -> None:
        """Simple, safe code → LOCAL."""
        result = recommend_target_for_code(
            source_code="def greet(name: str) -> str:\n    return f'Hello {name}'",
            intent="greet the user",
        )
        assert result.target == Target.LOCAL
        assert result.forced is False

    def test_chaotic_intent(self) -> None:
        """Chaotic intent → WASM (regardless of code)."""
        result = recommend_target_for_code(
            source_code="x = 1",
            intent="do everything forever",  # Contains chaotic keyword
        )
        assert result.target == Target.WASM
        assert result.forced is True

    def test_complex_intent_default(self) -> None:
        """Complex intent → CLI (default for PROBABILISTIC)."""
        result = recommend_target_for_code(
            source_code="def process(data): return data",
            intent="analyze the data",  # Complex keyword
        )
        assert result.target == Target.CLI

    def test_complex_intent_interactive(self) -> None:
        """Complex intent + interactive → MARIMO."""
        result = recommend_target_for_code(
            source_code="def process(data): return data",
            intent="analyze the data",
            context={"interactive": True},
        )
        assert result.target == Target.MARIMO

    def test_unstable_code_forces_wasm(self) -> None:
        """Unstable code forces WASM even with simple intent."""
        # Code with dangerous imports (will fail stability check)
        dangerous_code = """
import subprocess
import os

def run_command(cmd):
    return subprocess.run(cmd, shell=True)
"""
        result = recommend_target_for_code(
            source_code=dangerous_code,
            intent="run a command",
        )
        assert result.target == Target.WASM
        assert result.forced is True

    def test_empty_code_uses_intent(self) -> None:
        """Empty code still classifies by intent."""
        result = recommend_target_for_code(
            source_code="",
            intent="fetch data",  # Atomic keyword
        )
        # Empty code = no stability issues, intent is DETERMINISTIC
        assert result.target == Target.LOCAL


# --- Target Enum Tests ---


class TestTargetEnum:
    """Tests for Target enum values."""

    def test_all_targets_have_string_value(self) -> None:
        """All Target enum members have string values."""
        for target in Target:
            assert isinstance(target.value, str)

    def test_target_values_unique(self) -> None:
        """All Target values are unique."""
        values = [t.value for t in Target]
        assert len(values) == len(set(values))

    def test_expected_targets_exist(self) -> None:
        """All expected targets exist."""
        expected = {"local", "cli", "docker", "k8s", "wasm", "marimo"}
        actual = {t.value for t in Target}
        assert expected == actual


# --- Property-Based Tests ---


class TestTargetSelectionProperties:
    """Property-based tests for target selection invariants."""

    @pytest.mark.parametrize(
        "context",
        [
            {},
            {"interactive": True},
            {"production": True},
            {"container": True},
            {"target": "local"},
            {"target": "cli"},
        ],
    )
    def test_chaotic_always_wasm(self, context: dict) -> None:
        """Property: CHAOTIC → WASM regardless of context."""
        target = select_target(Reality.CHAOTIC, context)
        assert target == Target.WASM

    @pytest.mark.parametrize("reality", [Reality.DETERMINISTIC, Reality.PROBABILISTIC])
    def test_unstable_always_wasm(self, reality: Reality, unstable_result: StabilityResult) -> None:
        """Property: unstable → WASM regardless of reality (except CHAOTIC)."""
        target = select_target(reality, {}, unstable_result)
        assert target == Target.WASM

    @pytest.mark.parametrize("reality", [Reality.DETERMINISTIC, Reality.PROBABILISTIC])
    def test_stable_respects_reality(
        self, reality: Reality, stable_result: StabilityResult
    ) -> None:
        """Property: stable code respects reality classification."""
        target = select_target(reality, {}, stable_result)
        # Should not be WASM (not forced)
        result = select_target_with_reason(reality, {}, stable_result)
        assert result.forced is False
