"""
Tests for F-gent Phase 4: Validate

Focused tests covering core validation functionality.
"""

import pytest
from agents.f.contract import Contract, Invariant
from agents.f.intent import Example, Intent
from agents.f.prototype import SourceCode, StaticAnalysisReport
from agents.f.validate import (
    SandboxExecutionError,
    TestResult,
    TestResultStatus,
    ValidationConfig,
    VerdictStatus,
    _compute_code_similarity,
    _execute_in_sandbox,
    run_test,
    validate,
    validate_with_self_healing,
    verify_invariant,
)

# ============================================================================
# Test Helpers
# ============================================================================


def _make_source(code: str, is_valid: bool = True) -> SourceCode:
    """Create SourceCode for testing."""
    report = StaticAnalysisReport()
    report.passed = is_valid
    return SourceCode(code=code, analysis_report=report)


# ============================================================================
# Test Sandbox Execution
# ============================================================================


def test_sandbox_simple() -> None:
    """Test sandbox execution of simple agent."""
    code = """
class DoublerAgent:
    def invoke(self, x):
        return x * 2
"""
    result = _execute_in_sandbox(code, 5, "DoublerAgent")
    assert result == 10


def test_sandbox_missing_class() -> None:
    """Test sandbox with missing class."""
    code = "class Foo: pass"
    with pytest.raises(SandboxExecutionError, match="not found"):
        _execute_in_sandbox(code, 5, "Bar")


def test_sandbox_runtime_error() -> None:
    """Test sandbox with runtime error."""
    code = """
class BuggyAgent:
    def invoke(self, x):
        raise ValueError("bug")
"""
    with pytest.raises(SandboxExecutionError, match="ValueError"):
        _execute_in_sandbox(code, 5, "BuggyAgent")


# ============================================================================
# Test run_test
# ============================================================================


def test_run_test_passing() -> None:
    """Test run_test with passing test."""
    source = _make_source("""
class Agent:
    def invoke(self, x):
        return x * 2
""")
    example = Example(input=5, expected_output=10)
    result = run_test(source, example, "Agent")
    assert result.status == TestResultStatus.PASS


def test_run_test_failing() -> None:
    """Test run_test with failing test."""
    source = _make_source("""
class Agent:
    def invoke(self, x):
        return x * 3
""")
    example = Example(input=5, expected_output=10)
    result = run_test(source, example, "Agent")
    assert result.status == TestResultStatus.FAIL


# ============================================================================
# Test verify_invariant
# ============================================================================


def test_verify_invariant_deterministic() -> None:
    """Test deterministic invariant."""
    inv = Invariant("deterministic", "f(x) == f(x)", "behavioral")
    source = _make_source("pass")
    result = verify_invariant(inv, source, [])
    assert result.passed


def test_verify_invariant_length_pass() -> None:
    """Test length constraint (passing)."""
    inv = Invariant("concise", "len(output) < 100", "performance")
    source = _make_source("pass")
    tests = [TestResult(Example("x", "short"), TestResultStatus.PASS, "short", "short")]
    result = verify_invariant(inv, source, tests)
    assert result.passed


def test_verify_invariant_length_fail() -> None:
    """Test length constraint (failing)."""
    inv = Invariant("concise", "len(output) < 10", "performance")
    source = _make_source("pass")
    tests = [
        TestResult(
            Example("x", "short"),
            TestResultStatus.PASS,
            "this is way too long",
            "short",
        )
    ]
    result = verify_invariant(inv, source, tests)
    assert not result.passed


# ============================================================================
# Test validate
# ============================================================================


def test_validate_all_passing() -> None:
    """Test validate with all passing."""
    source = _make_source("""
class Agent:
    def invoke(self, x):
        return x * 2
""")
    examples = [Example(input=5, expected_output=10)]
    contract = Contract(
        agent_name="Agent",
        input_type="int",
        output_type="int",
        invariants=[Invariant("det", "f(x)==f(x)", "behavioral")],
        composition_rules=[],
        semantic_intent="double",
    )
    report = validate(source, examples, contract)
    assert report.verdict == VerdictStatus.PASS


def test_validate_test_failure() -> None:
    """Test validate with test failure."""
    source = _make_source("""
class Agent:
    def invoke(self, x):
        return x * 3
""")
    examples = [Example(input=5, expected_output=10)]
    contract = Contract(
        agent_name="Agent",
        input_type="int",
        output_type="int",
        invariants=[],
        composition_rules=[],
        semantic_intent="double",
    )
    report = validate(source, examples, contract)
    assert report.verdict == VerdictStatus.FAIL


# ============================================================================
# Test Self-Healing
# ============================================================================


@pytest.mark.asyncio
async def test_self_healing_success() -> None:
    """Test self-healing succeeds on retry."""
    buggy = _make_source("""
class Agent:
    def invoke(self, x):
        return x * 3
""")
    fixed = _make_source("""
class Agent:
    def invoke(self, x):
        return x * 2
""")

    async def regenerate(failures: list[str]) -> SourceCode:
        return fixed

    intent = Intent("double", ["multiply by 2"], [], examples=[Example(5, 10)])
    contract = Contract("Agent", "int", "int", [], [], "double")

    report = await validate_with_self_healing(
        intent, contract, buggy, regenerate_fn=regenerate
    )
    assert report.verdict == VerdictStatus.PASS


@pytest.mark.asyncio
async def test_self_healing_max_attempts() -> None:
    """Test self-healing reaches max attempts or convergence."""
    buggy = _make_source("""
class Agent:
    def invoke(self, x):
        return x * 3
""")

    async def regenerate(failures: list[str]) -> SourceCode:
        return buggy

    intent = Intent("double", ["multiply by 2"], [], examples=[Example(5, 10)])
    contract = Contract("Agent", "int", "int", [], [], "double")

    report = await validate_with_self_healing(
        intent,
        contract,
        buggy,
        config=ValidationConfig(max_heal_attempts=3),
        regenerate_fn=regenerate,
    )
    assert report.verdict == VerdictStatus.ESCALATE
    # Should escalate due to max attempts OR convergence
    assert (
        "Max heal attempts" in report.failure_summary
        or "Convergence failure" in report.failure_summary
    )


# ============================================================================
# Test Code Similarity
# ============================================================================


def test_code_similarity_identical() -> None:
    """Test identical codes."""
    c1 = "def foo(): return 42"
    c2 = "def foo(): return 42"
    assert _compute_code_similarity([c1, c2]) == 1.0


def test_code_similarity_different() -> None:
    """Test different codes."""
    c1 = "def foo(): return 42"
    c2 = "class Bar: pass"
    assert _compute_code_similarity([c1, c2]) < 0.5
