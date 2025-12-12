"""
Algebraic Cost Functions

Composable cost functions for capital operations.

Design Insight: Cost functions should compose algebraically:
- Addition: cost_a + cost_b (factors sum)
- Scaling: 0.5 * cost_a (factor scales)

This allows building complex cost models from simple primitives.

Principle Alignment:
- Composable: Costs are morphisms that compose
- Joy-Inducing: Pythonic operator overloading
- Generative: New costs derived from existing factors
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

# === Cost Context ===


@dataclass
class CostContext:
    """
    Context for cost calculation.

    Provides the parameters that cost factors use to compute their contribution.
    """

    risk: float  # 0.0 to 1.0 (from RiskCalculator)
    judgment_score: float  # 0.0 to 1.0 (from T-gent)
    resources_ok: bool  # Resource constraints satisfied


# === Algebraic Cost Factor ===


@dataclass
class CostFactor:
    """
    A composable cost function component.

    Costs compose algebraically:
    - Addition: cost_a + cost_b (factors sum)
    - Scaling: 0.5 * cost_a (factor scales)

    Example:
        BYPASS_COST = BASE_COST + 0.1 * RISK_PREMIUM + 0.1 * JUDGMENT_DEFICIT
        cost = BYPASS_COST(ctx)  # Algebraically computed
    """

    name: str
    compute: Callable[[CostContext], float]

    def __call__(self, ctx: CostContext) -> float:
        """Evaluate this cost factor in the given context."""
        return self.compute(ctx)

    def __add__(self, other: CostFactor) -> CostFactor:
        """
        Costs add.

        (A + B)(ctx) = A(ctx) + B(ctx)
        """
        return CostFactor(
            name=f"({self.name}+{other.name})",
            compute=lambda ctx: self.compute(ctx) + other.compute(ctx),
        )

    def __mul__(self, scalar: float) -> CostFactor:
        """
        Scale a cost.

        (k * A)(ctx) = k * A(ctx)
        """
        return CostFactor(
            name=f"{scalar}*{self.name}",
            compute=lambda ctx: scalar * self.compute(ctx),
        )

    def __rmul__(self, scalar: float) -> CostFactor:
        """Support scalar * CostFactor syntax."""
        return self.__mul__(scalar)


# === Standard Cost Factors ===


BASE_COST = CostFactor(
    name="base",
    compute=lambda _: 0.1,
)
"""Base cost for any bypass operation (flat fee)."""


RISK_PREMIUM = CostFactor(
    name="risk",
    compute=lambda ctx: math.exp(ctx.risk * 2) - 1,  # Exponential scaling
)
"""
Risk-based cost premium.

Exponential scaling: low risk is cheap, high risk is expensive.
- risk=0.0 → 0.0 premium
- risk=0.5 → ~1.72 premium
- risk=1.0 → ~6.39 premium
"""


JUDGMENT_DEFICIT = CostFactor(
    name="judgment",
    compute=lambda ctx: max(0, 0.8 - ctx.judgment_score),
)
"""
Cost for bypassing without T-gent approval.

High judgment score (>0.8) means no deficit.
Low judgment score means paying for the uncertainty.
"""


RESOURCE_PENALTY = CostFactor(
    name="resource",
    compute=lambda ctx: 0.1 if not ctx.resources_ok else 0,
)
"""Penalty when resource constraints are violated."""


# === Composed Cost Functions ===


BYPASS_COST = BASE_COST + 0.1 * RISK_PREMIUM + 0.1 * JUDGMENT_DEFICIT + RESOURCE_PENALTY
"""
Standard bypass cost function.

Combines:
- Base cost (0.1)
- 10% of risk premium (scales with risk)
- 10% of judgment deficit (scales with missing approval)
- Resource penalty (0.1 if constraints violated)
"""


# === Factory Functions ===


def constant_cost(value: float, name: str = "const") -> CostFactor:
    """Create a constant cost factor."""
    return CostFactor(name=f"{name}({value})", compute=lambda _: value)


def linear_risk(scale: float = 1.0) -> CostFactor:
    """Create a linear (not exponential) risk factor."""
    return CostFactor(
        name=f"linear_risk({scale})",
        compute=lambda ctx: ctx.risk * scale,
    )


def threshold_cost(
    threshold: float,
    above_cost: float,
    below_cost: float = 0.0,
    field: str = "risk",
) -> CostFactor:
    """Create a threshold-based cost factor."""

    def compute(ctx: CostContext) -> float:
        value = getattr(ctx, field, 0.0)
        return above_cost if value > threshold else below_cost

    return CostFactor(
        name=f"threshold({field}>{threshold})",
        compute=compute,
    )
