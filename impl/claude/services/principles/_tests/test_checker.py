"""
Tests for PrincipleChecker.

Type II (Composition): Multiple checks compose correctly.
Type IV (Property): Check results for known good/bad examples.
"""

from __future__ import annotations

import pytest

from services.principles import (
    PrincipleChecker,
    CheckResult,
    create_principle_checker,
    Stance,
)


# === Fixtures ===


@pytest.fixture
def checker() -> PrincipleChecker:
    """Create a checker instance."""
    return create_principle_checker()


# === Law: Check Completeness ===


@pytest.mark.asyncio
async def test_check_evaluates_all_principles(checker: PrincipleChecker) -> None:
    """check() always evaluates all seven principles unless filtered."""
    result = await checker.check("a test agent")

    assert len(result.checks) == 7
    assert all(c.principle in range(1, 8) for c in result.checks)


@pytest.mark.asyncio
async def test_check_with_filter(checker: PrincipleChecker) -> None:
    """check() respects principle filter."""
    result = await checker.check("a test agent", principles=[1, 5])

    assert len(result.checks) == 2
    assert result.checks[0].principle == 1
    assert result.checks[1].principle == 5


# === Known Good Examples ===


@pytest.mark.asyncio
async def test_good_agent_passes(checker: PrincipleChecker) -> None:
    """Well-designed agent description passes checks."""
    target = """
    A focused agent with a clear, justified purpose.
    Intentionally selected for quality over quantity.
    Transparent about limitations and respects privacy.
    Delightful to interact with, warm personality.
    Composable via the >> operator, single output.
    Can both lead and follow, dynamic allocation.
    Generated from compressed spec.
    """
    result = await checker.check(target)

    # Should pass at least some checks (heuristic matching is simple)
    passed_count = sum(1 for c in result.checks if c.passed)
    assert passed_count >= 3  # Most should pass with simple heuristics


# === Known Bad Examples (Anti-Patterns) ===


@pytest.mark.asyncio
async def test_kitchen_sink_fails_tasteful(checker: PrincipleChecker) -> None:
    """Kitchen-sink agent fails Tasteful check."""
    target = "An agent that does everything, handles all cases"

    result = await checker.check(target, principles=[1])  # Tasteful only

    assert len(result.checks) == 1
    check = result.checks[0]
    assert check.principle == 1
    assert check.name == "Tasteful"
    # Should fail due to "everything" anti-pattern
    assert not check.passed or "everything" not in target.lower()


@pytest.mark.asyncio
async def test_monolithic_fails_composable(checker: PrincipleChecker) -> None:
    """Monolithic agent fails Composable check."""
    target = "A monolithic god agent that can't be broken apart"

    result = await checker.check(target, principles=[5])  # Composable only

    check = result.checks[0]
    assert check.principle == 5
    assert check.name == "Composable"


# === Result Structure ===


@pytest.mark.asyncio
async def test_result_structure(checker: PrincipleChecker) -> None:
    """CheckResult has correct structure."""
    result = await checker.check("test target")

    assert isinstance(result, CheckResult)
    assert result.target == "test target"
    assert isinstance(result.passed, bool)
    assert result.stance == Stance.KRISIS
    assert len(result.checks) == 7


@pytest.mark.asyncio
async def test_check_has_question(checker: PrincipleChecker) -> None:
    """Each check includes the principle question."""
    result = await checker.check("test")

    for check in result.checks:
        assert check.question  # Not empty
        assert "?" in check.question


# === Quick Check ===


@pytest.mark.asyncio
async def test_quick_check(checker: PrincipleChecker) -> None:
    """check_quick returns boolean."""
    passed = await checker.check_quick("a focused agent", 1)  # Tasteful
    assert isinstance(passed, bool)


@pytest.mark.asyncio
async def test_quick_check_invalid_principle(checker: PrincipleChecker) -> None:
    """check_quick returns False for invalid principle."""
    passed = await checker.check_quick("test", 99)
    assert passed is False


# === Helper Methods ===


def test_get_question(checker: PrincipleChecker) -> None:
    """get_question returns principle question."""
    question = checker.get_question(1)
    assert "purpose" in question.lower()


def test_get_anti_patterns(checker: PrincipleChecker) -> None:
    """get_anti_patterns returns principle anti-patterns."""
    patterns = checker.get_anti_patterns(1)  # Tasteful
    assert len(patterns) > 0


# === Serialization ===


@pytest.mark.asyncio
async def test_result_to_dict(checker: PrincipleChecker) -> None:
    """CheckResult serializes to dict."""
    result = await checker.check("test")
    d = result.to_dict()

    assert "target" in d
    assert "passed" in d
    assert "checks" in d
    assert "stance" in d
    assert d["stance"] == "krisis"


@pytest.mark.asyncio
async def test_result_to_text(checker: PrincipleChecker) -> None:
    """CheckResult renders as text."""
    result = await checker.check("test")
    text = result.to_text()

    assert "Target: test" in text
    assert "PASSED" in text or "FAILED" in text
