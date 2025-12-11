"""
Value Ledger: Universal Value Protocol Implementation

Implements the Universal Value Protocol (UVP) from spec/b-gents/banker.md:
- Dual-Currency Architecture (Gas + Impact)
- Information Joule (J_inf) for semantic work measurement
- Value Oracle for DORA-inspired impact assessment
- Complexity Oracle for Kolmogorov approximation
- Return on Compute (RoC) monitoring
- Sin Tax / Virtue Subsidy ethical regulation
- Transaction ledger with full value accounting

The UVP transforms B-gent from simple Accountant into Physicist-Banker.
It introduces a relativistic currency system based on Information Thermodynamics.

Value = Work - Entropy
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Optional, Protocol

from .metered_functor import Gas, Impact
from .value_tensor import (
    EconomicDimension,
    EthicalDimension,
    ImpactTier,
    PhysicalDimension,
    SemanticDimension,
    ValueTensor,
)

# =============================================================================
# Complexity Oracle (Kolmogorov Approximation)
# =============================================================================


class ComplexityOracle:
    """
    Approximates Kolmogorov Complexity via compression ratio.

    High-entropy output (noise) → Low complexity → Low value
    Low-entropy output (structure) → High complexity → High value

    This inverts intuition: "complex" here means "structured/meaningful"
    not "complicated/messy".

    The Information Joule ($J_{inf}$) is the fundamental unit:
    J_inf = (Kolmogorov Complexity of Output) / (Tokens Consumed) × Semantic Coefficient
    """

    def assess(self, output: str) -> float:
        """
        Compression-based complexity estimate.

        Structured code compresses well (patterns repeat).
        Random noise doesn't compress (no patterns).

        Returns: Complexity score (0.0 to 2.0)
        """
        if not output:
            return 0.0

        original_size = len(output.encode("utf-8"))
        compressed_size = len(zlib.compress(output.encode("utf-8")))

        # Compression ratio: lower = more structured = higher value
        ratio = compressed_size / original_size if original_size > 0 else 1.0

        # Invert: structured output gets higher score
        # But also penalize trivially short outputs
        length_factor = min(1.0, original_size / 100)

        return (1.0 - ratio) * length_factor

    def assess_with_validation(
        self,
        output: str,
        validators: list[Callable[[str], bool]],
    ) -> float:
        """
        Enhanced assessment with semantic validators.

        Validators might include:
        - AST parsing (syntactic validity)
        - Type checking (type correctness)
        - Test execution (functional correctness)

        Returns: Complexity score (0.0 to 2.0+)
        """
        base_complexity = self.assess(output)

        validation_bonus = 0.0
        for validator in validators:
            try:
                if validator(output):
                    validation_bonus += 0.25
            except Exception:
                pass  # Validator failed, no bonus

        return min(2.0, base_complexity + validation_bonus)

    def information_joule(
        self,
        output: str,
        tokens_consumed: int,
        semantic_coefficient: float = 1.0,
    ) -> float:
        """
        Calculate Information Joule (J_inf).

        J_inf = (Kolmogorov Complexity of Output) / (Tokens Consumed) × Semantic Coefficient

        This is the physical unit of semantic work.
        """
        if tokens_consumed <= 0:
            return 0.0

        complexity = self.assess(output)
        return (
            (complexity / tokens_consumed) * semantic_coefficient * 1000
        )  # Scale factor


# =============================================================================
# Agent Output Protocol
# =============================================================================


class AgentOutput(Protocol):
    """Protocol for agent outputs that can be value-assessed."""

    @property
    def content(self) -> str:
        """The text/code content of the output."""
        ...

    def is_valid_syntax(self) -> bool:
        """Does the output have valid syntax (if applicable)?"""
        ...

    def tests_passed(self) -> bool:
        """Did tests pass (if applicable)?"""
        ...

    def deployment_successful(self) -> bool:
        """Was deployment successful (if applicable)?"""
        ...

    def policy_compliant(self) -> bool:
        """Is output policy compliant?"""
        ...

    def has_vulnerabilities(self) -> bool:
        """Does output have security vulnerabilities?"""
        ...

    def improved_maintainability(self) -> bool:
        """Did output improve maintainability?"""
        ...


@dataclass
class SimpleOutput:
    """Simple implementation of AgentOutput for testing."""

    content: str = ""
    _valid_syntax: bool = True
    _tests_passed: bool = False
    _deployed: bool = False
    _policy_compliant: bool = True
    _has_vulns: bool = False
    _improved_maintainability: bool = False

    def is_valid_syntax(self) -> bool:
        return self._valid_syntax

    def tests_passed(self) -> bool:
        return self._tests_passed

    def deployment_successful(self) -> bool:
        return self._deployed

    def policy_compliant(self) -> bool:
        return self._policy_compliant

    def has_vulnerabilities(self) -> bool:
        return self._has_vulns

    def improved_maintainability(self) -> bool:
        return self._improved_maintainability


# =============================================================================
# Value Oracle (Impact Assessment)
# =============================================================================


class ValueOracle:
    """
    Mints Impact based on DORA-inspired metrics.

    DORA = DevOps Research and Assessment
    Tiers correspond to increasing business value:

    | Tier | Description | Base Value |
    |------|-------------|------------|
    | Syntactic | Valid syntax only | 10 |
    | Functional | Tests pass | 100 |
    | Deployment | Successfully deployed | 1000 |
    | Ethical | Policy compliant + positive externalities | 1.2x multiplier |
    """

    def __init__(self) -> None:
        self.complexity_oracle = ComplexityOracle()

    def calculate_impact(self, output: AgentOutput) -> Impact:
        """
        Calculate impact value for an agent output.

        Uses DORA-inspired tiers with multipliers.
        """
        base_value = 0.0
        multipliers: dict[str, float] = {}
        tier = "syntactic"

        # Tier 1: The Work (Micro) - Syntactic Value
        if output.is_valid_syntax():
            base_value += 10
            tier = "syntactic"

        # Tier 2: The Outcome (Meso) - Functional Value
        if output.tests_passed():
            base_value += 100
            tier = "functional"

        # Tier 3: The Transformation (Macro) - Deployment Value
        if output.deployment_successful():
            base_value += 1000
            tier = "deployment"

        # Tier 4: The Ethics (Meta) - Ethical Multiplier
        if output.policy_compliant():
            multipliers["ethical"] = 1.2
            if tier == "deployment":
                tier = "ethical"

        # Sin Tax: Security vulnerabilities
        if output.has_vulnerabilities():
            multipliers["sin_tax"] = 0.33  # 3x penalty

        # Virtue Subsidy: Improved readability/maintainability
        if output.improved_maintainability():
            multipliers["virtue"] = 1.5

        # Add complexity bonus
        complexity = self.complexity_oracle.assess(output.content)
        if complexity > 0.5:
            multipliers["complexity_bonus"] = 1.0 + (complexity - 0.5)

        return Impact(
            base_value=base_value,
            tier=tier,
            multipliers=multipliers,
        )


# =============================================================================
# Ethical Regulator
# =============================================================================


class EthicalRegulator:
    """
    Applies economic incentives for ethical behavior.

    Sin Tax: Penalizes harmful outputs (multipliers < 1.0)
    Virtue Subsidy: Rewards beneficial outputs (multipliers > 1.0)
    """

    # Sin Taxes (multipliers < 1.0)
    SIN_TAXES = {
        "security_vulnerability": 0.33,  # 3x penalty
        "privacy_violation": 0.25,  # 4x penalty
        "bias_detected": 0.5,  # 2x penalty
        "license_violation": 0.2,  # 5x penalty
    }

    # Virtue Subsidies (multipliers > 1.0)
    VIRTUE_SUBSIDIES = {
        "improved_readability": 1.3,
        "added_tests": 1.5,
        "fixed_tech_debt": 1.4,
        "improved_accessibility": 1.6,
        "reduced_complexity": 1.3,
    }

    def apply_adjustments(
        self,
        base_impact: Impact,
        sins: list[str],
        virtues: list[str],
    ) -> Impact:
        """Apply ethical adjustments to impact calculation."""
        adjusted = Impact(
            base_value=base_impact.base_value,
            tier=base_impact.tier,
            multipliers=dict(base_impact.multipliers),
        )

        for sin in sins:
            if sin in self.SIN_TAXES:
                adjusted.multipliers[f"sin:{sin}"] = self.SIN_TAXES[sin]

        for virtue in virtues:
            if virtue in self.VIRTUE_SUBSIDIES:
                adjusted.multipliers[f"virtue:{virtue}"] = self.VIRTUE_SUBSIDIES[virtue]

        return adjusted


# =============================================================================
# Treasury
# =============================================================================


@dataclass
class Treasury:
    """
    Tracks Gas and Impact per agent.

    Implements double-entry bookkeeping:
    - Assets: Accumulated Impact
    - Liabilities: Accumulated Debt
    - Gas: Total consumed
    """

    # Per-agent tracking
    _impact: dict[str, float] = field(default_factory=dict)
    _debt: dict[str, float] = field(default_factory=dict)
    _gas_consumed: dict[str, float] = field(default_factory=dict)
    _transaction_count: dict[str, int] = field(default_factory=dict)

    def deduct_gas(self, agent_id: str, gas: Gas) -> None:
        """Record gas consumption."""
        self._gas_consumed[agent_id] = (
            self._gas_consumed.get(agent_id, 0.0) + gas.cost_usd
        )
        self._transaction_count[agent_id] = self._transaction_count.get(agent_id, 0) + 1

    def mint_impact(self, agent_id: str, impact: float) -> None:
        """Mint impact tokens for an agent."""
        self._impact[agent_id] = self._impact.get(agent_id, 0.0) + impact

    def record_debt(self, agent_id: str, debt: float) -> None:
        """Record debt for an agent."""
        self._debt[agent_id] = self._debt.get(agent_id, 0.0) + debt

    def get_impact(self, agent_id: str) -> float:
        """Get accumulated impact for an agent."""
        return self._impact.get(agent_id, 0.0)

    def get_debt(self, agent_id: str) -> float:
        """Get accumulated debt for an agent."""
        return self._debt.get(agent_id, 0.0)

    def get_gas_consumed(self, agent_id: str) -> float:
        """Get total gas consumed by an agent."""
        return self._gas_consumed.get(agent_id, 0.0)

    def get_transaction_count(self, agent_id: str) -> int:
        """Get transaction count for an agent."""
        return self._transaction_count.get(agent_id, 0)

    def total_impact(self) -> float:
        """Total system impact."""
        return sum(self._impact.values())

    def total_debt(self) -> float:
        """Total system debt."""
        return sum(self._debt.values())

    def total_gas(self) -> float:
        """Total gas consumed."""
        return sum(self._gas_consumed.values())


# =============================================================================
# Balance Sheet
# =============================================================================


@dataclass
class BalanceSheet:
    """Balance sheet for an agent."""

    assets: float  # Accumulated Impact
    liabilities: float  # Accumulated Debt
    gas_consumed: float
    transaction_count: int

    @property
    def equity(self) -> float:
        """Net value contribution."""
        return self.assets - self.liabilities

    @property
    def roc(self) -> float:
        """Return on Compute."""
        if self.gas_consumed <= 0:
            return 0.0
        return self.assets / self.gas_consumed


# =============================================================================
# Transaction Receipt
# =============================================================================


@dataclass
class TransactionReceipt:
    """Full receipt for a metered transaction."""

    agent_id: str
    gas: Gas
    impact: Impact
    complexity: float
    roc: float
    status: str  # "profitable" or "debt"
    timestamp: datetime = field(default_factory=datetime.now)
    tensor: Optional[ValueTensor] = None


# =============================================================================
# Value Ledger
# =============================================================================


class ValueLedger:
    """
    Tracks the 'GDP' of the Multi-Agent System.

    Every transaction records:
    1. Gas consumed (real cost)
    2. Impact generated (realized value)
    3. Profit or debt (the difference)

    Resembles a corporate balance sheet, not a log file.
    """

    def __init__(self) -> None:
        self.treasury = Treasury()
        self.oracle = ValueOracle()
        self.complexity_oracle = ComplexityOracle()
        self.regulator = EthicalRegulator()

        # Transaction history
        self.transactions: list[TransactionReceipt] = []

    def log_transaction(
        self,
        agent_id: str,
        gas: Gas,
        output: AgentOutput,
        sins: Optional[list[str]] = None,
        virtues: Optional[list[str]] = None,
    ) -> TransactionReceipt:
        """
        Record a transaction with full value accounting.

        This is the main entry point for logging agent work.
        """
        # 1. Deduct Gas (Real $ cost)
        self.treasury.deduct_gas(agent_id, gas)

        # 2. Calculate Realized Value
        complexity = self.complexity_oracle.assess(output.content)
        impact = self.oracle.calculate_impact(output)

        # Apply ethical adjustments
        if sins or virtues:
            impact = self.regulator.apply_adjustments(impact, sins or [], virtues or [])

        # 3. Compute Return on Compute (RoC)
        roc = impact.realized_value / gas.cost_usd if gas.cost_usd > 0 else 0.0

        # 4. Mint or Record Debt
        if impact.realized_value > gas.cost_usd:
            profit = impact.realized_value - gas.cost_usd
            self.treasury.mint_impact(agent_id, profit)
            status = "profitable"
        else:
            debt = gas.cost_usd - impact.realized_value
            self.treasury.record_debt(agent_id, debt)
            status = "debt"

        # 5. Create Value Tensor
        tensor = ValueTensor(
            physical=PhysicalDimension(
                input_tokens=0,
                output_tokens=gas.tokens,
                wall_clock_ms=gas.time_ms,
                model_id="unknown",
                cost_multiplier=gas.model_multiplier,
            ),
            semantic=SemanticDimension.from_compression(output.content),
            economic=EconomicDimension(
                gas_cost_usd=gas.cost_usd,
                impact_value=impact.realized_value,
                impact_tier=ImpactTier(impact.tier),
            ),
            ethical=EthicalDimension(
                security_risk=0.5 if output.has_vulnerabilities() else 0.0,
                maintainability_improvement=0.3
                if output.improved_maintainability()
                else 0.0,
            ),
        )

        receipt = TransactionReceipt(
            agent_id=agent_id,
            gas=gas,
            impact=impact,
            complexity=complexity,
            roc=roc,
            status=status,
            tensor=tensor,
        )

        self.transactions.append(receipt)
        return receipt

    def get_agent_balance_sheet(self, agent_id: str) -> BalanceSheet:
        """Generate balance sheet for an agent."""
        return BalanceSheet(
            assets=self.treasury.get_impact(agent_id),
            liabilities=self.treasury.get_debt(agent_id),
            gas_consumed=self.treasury.get_gas_consumed(agent_id),
            transaction_count=self.treasury.get_transaction_count(agent_id),
        )

    def system_roc(self) -> float:
        """System-wide Return on Compute."""
        total_gas = self.treasury.total_gas()
        if total_gas <= 0:
            return 0.0
        return self.treasury.total_impact() / total_gas

    def get_agent_history(
        self, agent_id: str, limit: int = 100
    ) -> list[TransactionReceipt]:
        """Get recent transactions for an agent."""
        agent_txs = [t for t in self.transactions if t.agent_id == agent_id]
        return agent_txs[-limit:]

    def get_system_stats(self) -> dict[str, Any]:
        """Get system-wide statistics."""
        return {
            "total_transactions": len(self.transactions),
            "total_impact": self.treasury.total_impact(),
            "total_debt": self.treasury.total_debt(),
            "total_gas_usd": self.treasury.total_gas(),
            "system_roc": self.system_roc(),
            "profitable_count": sum(
                1 for t in self.transactions if t.status == "profitable"
            ),
            "debt_count": sum(1 for t in self.transactions if t.status == "debt"),
        }


# =============================================================================
# RoC Monitor
# =============================================================================


@dataclass
class RoCThresholds:
    """Thresholds for RoC interpretation."""

    bankruptcy: float = 0.5  # < 0.5: burning money
    break_even: float = 1.0  # 0.5-1.0: break-even
    healthy: float = 2.0  # 1.0-2.0: profitable


@dataclass
class RoCAssessment:
    """Assessment of an agent's economic health."""

    status: str  # "new", "bankruptcy_warning", "break_even", "profitable", "high_yield"
    roc: float


class RoCMonitor:
    """
    Monitors Return on Compute across the agent ecosystem.

    RoC = Impact Realized / Gas Consumed

    | RoC Range | Interpretation | Action |
    |-----------|----------------|--------|
    | < 0.5 | Burning money | Bankruptcy warning |
    | 0.5 - 1.0 | Break-even | Monitor |
    | 1.0 - 2.0 | Profitable | Healthy |
    | > 2.0 | High yield | Exemplar |
    """

    def __init__(self, ledger: ValueLedger) -> None:
        self.ledger = ledger
        self.thresholds = RoCThresholds()

    def assess_agent(self, agent_id: str) -> RoCAssessment:
        """Assess an agent's economic health."""
        sheet = self.ledger.get_agent_balance_sheet(agent_id)

        if sheet.gas_consumed == 0:
            return RoCAssessment(status="new", roc=0.0)

        roc = sheet.roc

        if roc < self.thresholds.bankruptcy:
            return RoCAssessment(status="bankruptcy_warning", roc=roc)
        elif roc < self.thresholds.break_even:
            return RoCAssessment(status="break_even", roc=roc)
        elif roc < self.thresholds.healthy:
            return RoCAssessment(status="profitable", roc=roc)
        else:
            return RoCAssessment(status="high_yield", roc=roc)

    def get_leaderboard(self, limit: int = 10) -> list[tuple[str, RoCAssessment]]:
        """Get top performers by RoC."""
        agents = set(t.agent_id for t in self.ledger.transactions)
        assessments = [(a, self.assess_agent(a)) for a in agents]
        return sorted(assessments, key=lambda x: x[1].roc, reverse=True)[:limit]

    def get_at_risk(self) -> list[tuple[str, RoCAssessment]]:
        """Get agents at risk of bankruptcy."""
        agents = set(t.agent_id for t in self.ledger.transactions)
        return [
            (a, self.assess_agent(a))
            for a in agents
            if self.assess_agent(a).status == "bankruptcy_warning"
        ]
