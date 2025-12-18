"""
Tests for Algebraic Cost Functions

Tests verify:
1. Cost algebra (addition, multiplication)
2. Standard cost factors behave correctly
3. Composed costs compute correctly
"""

from __future__ import annotations

import math

import pytest
from hypothesis import given, settings, strategies as st

from shared.costs import (
    BASE_COST,
    BYPASS_COST,
    JUDGMENT_DEFICIT,
    RESOURCE_PENALTY,
    RISK_PREMIUM,
    CostContext,
    CostFactor,
    constant_cost,
    linear_risk,
    threshold_cost,
)

# === Fixtures ===


@pytest.fixture
def low_risk_context() -> CostContext:
    """Context with low risk, high judgment."""
    return CostContext(risk=0.1, judgment_score=0.9, resources_ok=True)


@pytest.fixture
def high_risk_context() -> CostContext:
    """Context with high risk, low judgment."""
    return CostContext(risk=0.9, judgment_score=0.3, resources_ok=False)


# === Cost Algebra Tests ===


def test_cost_addition() -> None:
    """Costs add algebraically: (A + B)(ctx) = A(ctx) + B(ctx)."""
    a = CostFactor("a", lambda _: 0.1)
    b = CostFactor("b", lambda _: 0.2)
    combined = a + b

    ctx = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)
    assert combined(ctx) == pytest.approx(0.3)


def test_cost_multiplication() -> None:
    """Costs scale: (k * A)(ctx) = k * A(ctx)."""
    a = CostFactor("a", lambda _: 0.5)
    scaled = 0.5 * a

    ctx = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)
    assert scaled(ctx) == pytest.approx(0.25)


def test_cost_right_multiplication() -> None:
    """Right multiplication works: A * k."""
    a = CostFactor("a", lambda _: 0.5)
    scaled = a * 2.0

    ctx = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)
    assert scaled(ctx) == pytest.approx(1.0)


def test_cost_composition_name() -> None:
    """Composed costs have readable names."""
    a = CostFactor("a", lambda _: 0.1)
    b = CostFactor("b", lambda _: 0.2)

    combined = a + b
    assert "a" in combined.name
    assert "b" in combined.name

    scaled = 0.5 * a
    assert "0.5" in scaled.name
    assert "a" in scaled.name


def test_cost_callable() -> None:
    """CostFactor is callable."""
    factor = CostFactor("test", lambda ctx: ctx.risk * 2)
    ctx = CostContext(risk=0.3, judgment_score=0.5, resources_ok=True)

    assert factor(ctx) == pytest.approx(0.6)


# === Standard Cost Factor Tests ===


def test_base_cost_is_constant() -> None:
    """BASE_COST is a flat fee regardless of context."""
    ctx_low = CostContext(risk=0.1, judgment_score=0.9, resources_ok=True)
    ctx_high = CostContext(risk=0.9, judgment_score=0.1, resources_ok=False)

    assert BASE_COST(ctx_low) == BASE_COST(ctx_high) == 0.1


def test_risk_premium_scales_exponentially() -> None:
    """RISK_PREMIUM scales exponentially with risk."""
    ctx_low = CostContext(risk=0.0, judgment_score=0.5, resources_ok=True)
    ctx_med = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)
    ctx_high = CostContext(risk=1.0, judgment_score=0.5, resources_ok=True)

    premium_low = RISK_PREMIUM(ctx_low)
    premium_med = RISK_PREMIUM(ctx_med)
    premium_high = RISK_PREMIUM(ctx_high)

    # Exponential: low < med < high
    assert premium_low < premium_med < premium_high

    # Check formula: exp(risk * 2) - 1
    assert premium_low == pytest.approx(math.exp(0.0 * 2) - 1)
    assert premium_med == pytest.approx(math.exp(0.5 * 2) - 1)
    assert premium_high == pytest.approx(math.exp(1.0 * 2) - 1)


def test_judgment_deficit_scales_with_missing_approval() -> None:
    """JUDGMENT_DEFICIT is 0.8 - score when score < 0.8."""
    # High judgment: no deficit
    ctx_high = CostContext(risk=0.5, judgment_score=0.9, resources_ok=True)
    assert JUDGMENT_DEFICIT(ctx_high) == 0.0

    # Exactly at threshold
    ctx_threshold = CostContext(risk=0.5, judgment_score=0.8, resources_ok=True)
    assert JUDGMENT_DEFICIT(ctx_threshold) == 0.0

    # Below threshold
    ctx_low = CostContext(risk=0.5, judgment_score=0.3, resources_ok=True)
    assert JUDGMENT_DEFICIT(ctx_low) == pytest.approx(0.5)


def test_resource_penalty_when_violated() -> None:
    """RESOURCE_PENALTY is 0.1 when resources_ok is False."""
    ctx_ok = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)
    ctx_violated = CostContext(risk=0.5, judgment_score=0.5, resources_ok=False)

    assert RESOURCE_PENALTY(ctx_ok) == 0.0
    assert RESOURCE_PENALTY(ctx_violated) == 0.1


# === Composed Cost Tests ===


def test_bypass_cost_low_risk(low_risk_context: CostContext) -> None:
    """BYPASS_COST is cheap for low-risk, well-judged operations."""
    cost = BYPASS_COST(low_risk_context)

    # Should be close to base cost
    assert cost < 0.2  # Base (0.1) + small premium


def test_bypass_cost_high_risk(high_risk_context: CostContext) -> None:
    """BYPASS_COST is expensive for high-risk, poorly-judged operations."""
    cost = BYPASS_COST(high_risk_context)

    # Should be significantly higher
    assert cost > 0.3  # Base + risk + judgment + resource


def test_bypass_cost_components(high_risk_context: CostContext) -> None:
    """BYPASS_COST is sum of its component factors."""
    ctx = high_risk_context

    expected = (
        BASE_COST(ctx)
        + 0.1 * RISK_PREMIUM(ctx)
        + 0.1 * JUDGMENT_DEFICIT(ctx)
        + RESOURCE_PENALTY(ctx)
    )

    assert BYPASS_COST(ctx) == pytest.approx(expected)


# === Factory Function Tests ===


def test_constant_cost() -> None:
    """constant_cost creates a fixed cost factor."""
    factor = constant_cost(0.42, "my_const")

    ctx = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)
    assert factor(ctx) == 0.42
    assert "0.42" in factor.name


def test_linear_risk() -> None:
    """linear_risk creates a linearly-scaled risk factor."""
    factor = linear_risk(scale=2.0)

    ctx = CostContext(risk=0.3, judgment_score=0.5, resources_ok=True)
    assert factor(ctx) == pytest.approx(0.6)


def test_threshold_cost() -> None:
    """threshold_cost creates a step function."""
    factor = threshold_cost(threshold=0.5, above_cost=1.0, below_cost=0.0, field="risk")

    ctx_below = CostContext(risk=0.3, judgment_score=0.5, resources_ok=True)
    ctx_above = CostContext(risk=0.7, judgment_score=0.5, resources_ok=True)

    assert factor(ctx_below) == 0.0
    assert factor(ctx_above) == 1.0


# === Property-Based Tests ===


@given(
    st.floats(min_value=0, max_value=1),
    st.floats(min_value=0, max_value=1),
)
@settings(max_examples=100)
def test_cost_addition_is_commutative(val_a: float, val_b: float) -> None:
    """Cost addition is commutative: A + B = B + A."""
    a = CostFactor("a", lambda _: val_a)
    b = CostFactor("b", lambda _: val_b)

    ctx = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)

    ab = (a + b)(ctx)
    ba = (b + a)(ctx)

    assert ab == pytest.approx(ba)


@given(
    st.floats(min_value=0, max_value=1),
    st.floats(min_value=0, max_value=1),
    st.floats(min_value=0, max_value=1),
)
@settings(max_examples=100)
def test_cost_addition_is_associative(val_a: float, val_b: float, val_c: float) -> None:
    """Cost addition is associative: (A + B) + C = A + (B + C)."""
    a = CostFactor("a", lambda _: val_a)
    b = CostFactor("b", lambda _: val_b)
    c = CostFactor("c", lambda _: val_c)

    ctx = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)

    left = ((a + b) + c)(ctx)
    right = (a + (b + c))(ctx)

    assert left == pytest.approx(right)


@given(
    st.floats(min_value=0.1, max_value=10),
    st.floats(min_value=0.1, max_value=10),
    st.floats(min_value=0, max_value=1),
)
@settings(max_examples=100)
def test_scalar_multiplication_distributes(k1: float, k2: float, val: float) -> None:
    """Scalar multiplication distributes: k1 * (k2 * A) = (k1 * k2) * A."""
    a = CostFactor("a", lambda _: val)

    ctx = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)

    left = (k1 * (k2 * a))(ctx)
    right = ((k1 * k2) * a)(ctx)

    assert left == pytest.approx(right, rel=1e-5)


@given(st.floats(min_value=0, max_value=1))
@settings(max_examples=50)
def test_zero_scalar_gives_zero(val: float) -> None:
    """Multiplying by zero gives zero cost."""
    a = CostFactor("a", lambda _: val)

    ctx = CostContext(risk=0.5, judgment_score=0.5, resources_ok=True)

    assert (0 * a)(ctx) == 0.0
