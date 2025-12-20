"""
Semantic Inflation: Complexity → Verbosity Pressure Economics

Phase 4 of Structural Economics (B-gent × G-gent Integration).

Core insight: Complexity creates pressure to be verbose. But verbosity costs tokens.

The Inflation Formula:
    Inflation_Pressure = Complexity × Audience_Gap × Novelty

When complexity is high, agents need more tokens to:
1. Explain what they're doing (transparency tax)
2. Justify why (reasoning tax)
3. Handle edge cases (robustness tax)
4. Provide context (audience gap tax)

This creates "semantic inflation" - the purchasing power of a token decreases
as complexity increases (need more tokens to express the same meaning).

Key features:
1. ComplexityMetrics: Measure inherent complexity of an operation
2. InflationPressure: Calculate verbosity pressure from complexity
3. InflationBudget: Allocate tokens between content and explanation
4. DeflationStrategy: Compress verbose explanations when budget constrained
5. SemanticCPI: Track "Consumer Price Index" for semantic operations

Anti-patterns prevented:
- Infinite explanation regress (explaining explanations)
- Complexity hiding (under-explaining high-complexity ops)
- Audience mismatch (over-explaining to experts, under-explaining to novices)

Integration:
- Works with G-gent for compression via pidgins
- Works with B-gent CentralBank for metering
- Works with Syntax Tax for complexity pricing synergy
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any

from .metered_functor import CentralBank

# =============================================================================
# Complexity Metrics
# =============================================================================


class ComplexityDimension(Enum):
    """
    Dimensions of complexity that drive verbosity pressure.

    Each dimension represents a different "inflation force" that
    pushes toward more verbose explanations.
    """

    # Structural complexity (how many moving parts)
    STRUCTURAL = auto()

    # Temporal complexity (how many steps/states)
    TEMPORAL = auto()

    # Conceptual complexity (how many abstractions)
    CONCEPTUAL = auto()

    # Relational complexity (how many dependencies)
    RELATIONAL = auto()

    # Novelty (how unfamiliar to audience)
    NOVELTY = auto()

    # Risk (how dangerous if misunderstood)
    RISK = auto()


@dataclass
class ComplexityVector:
    """
    Multi-dimensional complexity measurement.

    Each dimension scores 0.0-1.0 representing normalized complexity.
    """

    structural: float = 0.0  # Cyclomatic complexity, nesting depth
    temporal: float = 0.0  # State transitions, async flows
    conceptual: float = 0.0  # Abstraction layers, type complexity
    relational: float = 0.0  # Dependencies, coupling
    novelty: float = 0.0  # Unfamiliarity to audience
    risk: float = 0.0  # Consequence of misunderstanding

    def __post_init__(self) -> None:
        """Clamp all values to [0.0, 1.0]."""
        self.structural = max(0.0, min(1.0, self.structural))
        self.temporal = max(0.0, min(1.0, self.temporal))
        self.conceptual = max(0.0, min(1.0, self.conceptual))
        self.relational = max(0.0, min(1.0, self.relational))
        self.novelty = max(0.0, min(1.0, self.novelty))
        self.risk = max(0.0, min(1.0, self.risk))

    @property
    def magnitude(self) -> float:
        """Overall complexity magnitude (L2 norm normalized to [0,1])."""
        raw = math.sqrt(
            self.structural**2
            + self.temporal**2
            + self.conceptual**2
            + self.relational**2
            + self.novelty**2
            + self.risk**2
        )
        # Normalize: max possible is sqrt(6) ≈ 2.45
        return min(1.0, raw / math.sqrt(6))

    @property
    def dominant_dimension(self) -> ComplexityDimension:
        """Which dimension contributes most to complexity."""
        values = {
            ComplexityDimension.STRUCTURAL: self.structural,
            ComplexityDimension.TEMPORAL: self.temporal,
            ComplexityDimension.CONCEPTUAL: self.conceptual,
            ComplexityDimension.RELATIONAL: self.relational,
            ComplexityDimension.NOVELTY: self.novelty,
            ComplexityDimension.RISK: self.risk,
        }
        return max(values, key=lambda d: values[d])

    def weighted_sum(self, weights: dict[ComplexityDimension, float] | None = None) -> float:
        """
        Calculate weighted sum of complexity dimensions.

        Default weights emphasize risk and novelty (audience-critical).
        """
        if weights is None:
            weights = {
                ComplexityDimension.STRUCTURAL: 1.0,
                ComplexityDimension.TEMPORAL: 1.0,
                ComplexityDimension.CONCEPTUAL: 1.2,
                ComplexityDimension.RELATIONAL: 0.8,
                ComplexityDimension.NOVELTY: 1.5,  # Novelty drives most explanation need
                ComplexityDimension.RISK: 2.0,  # Risk demands explanation
            }

        total = (
            self.structural * weights.get(ComplexityDimension.STRUCTURAL, 1.0)
            + self.temporal * weights.get(ComplexityDimension.TEMPORAL, 1.0)
            + self.conceptual * weights.get(ComplexityDimension.CONCEPTUAL, 1.0)
            + self.relational * weights.get(ComplexityDimension.RELATIONAL, 1.0)
            + self.novelty * weights.get(ComplexityDimension.NOVELTY, 1.0)
            + self.risk * weights.get(ComplexityDimension.RISK, 1.0)
        )

        weight_sum = sum(weights.values())
        return total / weight_sum if weight_sum > 0 else 0.0


class AudienceLevel(Enum):
    """
    Audience sophistication level.

    Determines the "audience gap" that drives explanation verbosity.
    """

    EXPERT = 0  # Domain expert, minimal explanation needed
    PRACTITIONER = 1  # Working professional, some context needed
    INTERMEDIATE = 2  # Familiar with basics, moderate explanation
    NOVICE = 3  # Learning, detailed explanation needed
    LAYPERSON = 4  # No domain knowledge, extensive explanation

    @property
    def explanation_multiplier(self) -> float:
        """How much explanation this audience needs (1.0 = baseline)."""
        return {
            AudienceLevel.EXPERT: 0.2,
            AudienceLevel.PRACTITIONER: 0.5,
            AudienceLevel.INTERMEDIATE: 1.0,
            AudienceLevel.NOVICE: 2.0,
            AudienceLevel.LAYPERSON: 3.0,
        }[self]


@dataclass
class AudienceProfile:
    """
    Profile of the target audience for an explanation.

    Used to calculate the "audience gap" inflation multiplier.
    """

    level: AudienceLevel = AudienceLevel.INTERMEDIATE
    domain_familiarity: float = 0.5  # 0.0-1.0 familiarity with specific domain
    context_available: float = 0.5  # 0.0-1.0 how much context already provided
    patience: float = 0.5  # 0.0-1.0 tolerance for longer explanations

    @property
    def audience_gap(self) -> float:
        """
        Calculate audience gap multiplier.

        Higher gap = more explanation needed.
        """
        base = self.level.explanation_multiplier

        # Familiarity reduces gap
        familiarity_factor = 1.0 - (0.5 * self.domain_familiarity)

        # Available context reduces gap
        context_factor = 1.0 - (0.3 * self.context_available)

        return base * familiarity_factor * context_factor

    @property
    def verbosity_tolerance(self) -> float:
        """How much verbosity the audience will tolerate (0.0-1.0)."""
        # Novices have more patience for explanation
        base_tolerance = {
            AudienceLevel.EXPERT: 0.2,
            AudienceLevel.PRACTITIONER: 0.4,
            AudienceLevel.INTERMEDIATE: 0.6,
            AudienceLevel.NOVICE: 0.8,
            AudienceLevel.LAYPERSON: 0.9,
        }[self.level]

        return base_tolerance * (0.5 + 0.5 * self.patience)


# =============================================================================
# Inflation Pressure Types
# =============================================================================


@dataclass
class InflationPressure:
    """
    Quantified pressure to be verbose.

    Inflation Pressure = Complexity × Audience_Gap × Novelty_Factor
    """

    complexity: ComplexityVector
    audience: AudienceProfile
    base_tokens: int  # Tokens for the core operation (no explanation)

    @property
    def pressure_score(self) -> float:
        """
        Calculate inflation pressure (0.0 = no pressure, 1.0+ = high pressure).

        Score > 1.0 indicates strong pressure to exceed base token count.
        """
        complexity_factor = self.complexity.weighted_sum()
        audience_factor = self.audience.audience_gap

        # Risk amplifies everything
        risk_amplifier = 1.0 + self.complexity.risk

        return complexity_factor * audience_factor * risk_amplifier

    @property
    def recommended_explanation_tokens(self) -> int:
        """
        Calculate recommended tokens for explanation.

        Based on pressure score and base tokens.
        """
        return int(self.base_tokens * self.pressure_score)

    @property
    def total_recommended_tokens(self) -> int:
        """Total tokens: base + explanation."""
        return self.base_tokens + self.recommended_explanation_tokens

    @property
    def inflation_rate(self) -> float:
        """
        Inflation rate: how many additional tokens per base token.

        Like economic inflation: 0.5 = 50% more tokens needed.
        """
        return self.pressure_score

    @property
    def explanation_ratio(self) -> float:
        """Ratio of explanation tokens to total tokens."""
        total = self.total_recommended_tokens
        if total == 0:
            return 0.0
        return self.recommended_explanation_tokens / total


class InflationCategory(Enum):
    """
    Categories of inflation based on pressure score.
    """

    DEFLATIONARY = auto()  # < 0.2: Can compress, minimal explanation
    STABLE = auto()  # 0.2-0.5: Normal explanation overhead
    MODERATE = auto()  # 0.5-1.0: Significant explanation needed
    HIGH = auto()  # 1.0-2.0: Heavy explanation burden
    HYPERINFLATION = auto()  # > 2.0: Explanation dominates content

    @classmethod
    def from_pressure(cls, pressure: float) -> "InflationCategory":
        """Categorize inflation pressure."""
        if pressure < 0.2:
            return cls.DEFLATIONARY
        elif pressure < 0.5:
            return cls.STABLE
        elif pressure < 1.0:
            return cls.MODERATE
        elif pressure < 2.0:
            return cls.HIGH
        else:
            return cls.HYPERINFLATION


@dataclass
class InflationReport:
    """
    Full inflation analysis for an operation.
    """

    pressure: InflationPressure
    category: InflationCategory
    dominant_driver: ComplexityDimension
    warnings: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @classmethod
    def analyze(cls, pressure: InflationPressure) -> "InflationReport":
        """Generate full inflation report."""
        category = InflationCategory.from_pressure(pressure.pressure_score)
        dominant = pressure.complexity.dominant_dimension

        warnings: list[str] = []
        recommendations: list[str] = []

        # Generate warnings
        if category == InflationCategory.HYPERINFLATION:
            warnings.append(
                "Hyperinflation detected: explanation would dominate content. "
                "Consider simplifying operation or using pidgin."
            )

        if pressure.complexity.risk > 0.8:
            warnings.append(
                "High-risk operation requires detailed explanation regardless of budget."
            )

        if (
            pressure.audience.level == AudienceLevel.LAYPERSON
            and pressure.complexity.magnitude > 0.7
        ):
            warnings.append("Complex operation for lay audience: consider staged explanation.")

        # Generate recommendations
        if category in (InflationCategory.HIGH, InflationCategory.HYPERINFLATION):
            if dominant == ComplexityDimension.CONCEPTUAL:
                recommendations.append("Define key abstractions upfront to reduce conceptual load.")
            elif dominant == ComplexityDimension.TEMPORAL:
                recommendations.append("Use step-by-step breakdown with clear state transitions.")
            elif dominant == ComplexityDimension.STRUCTURAL:
                recommendations.append("Consider diagram or structural overview before details.")
            elif dominant == ComplexityDimension.NOVELTY:
                recommendations.append("Anchor novel concepts to familiar analogies.")

        if category == InflationCategory.DEFLATIONARY:
            recommendations.append(
                "Expert audience + low complexity: minimal explanation acceptable."
            )

        return cls(
            pressure=pressure,
            category=category,
            dominant_driver=dominant,
            warnings=warnings,
            recommendations=recommendations,
        )


# =============================================================================
# Inflation Budget
# =============================================================================


@dataclass
class TokenAllocation:
    """
    Allocation of tokens between content and explanation.
    """

    content_tokens: int  # Tokens for actual operation
    explanation_tokens: int  # Tokens for explanation/context
    buffer_tokens: int = 0  # Reserve for unexpected complexity

    @property
    def total(self) -> int:
        """Total allocated tokens."""
        return self.content_tokens + self.explanation_tokens + self.buffer_tokens

    @property
    def explanation_ratio(self) -> float:
        """Ratio of explanation to total."""
        if self.total == 0:
            return 0.0
        return self.explanation_tokens / self.total


@dataclass
class AllocationDecision:
    """
    Decision from inflation budget evaluation.
    """

    approved: bool
    allocation: TokenAllocation
    reason: str
    inflation_report: InflationReport
    deficit: int = 0  # How many tokens short if not approved
    deflation_required: bool = False  # If compression is needed
    suggested_audience_level: AudienceLevel | None = None  # If audience adjustment recommended


class InflationBudget:
    """
    Budget that accounts for semantic inflation.

    Key behaviors:
    1. Calculate inflation pressure for operations
    2. Allocate tokens between content and explanation
    3. Enforce minimum explanation for high-risk operations
    4. Suggest deflation strategies when budget constrained
    """

    def __init__(
        self,
        central_bank: CentralBank | None = None,
        default_audience: AudienceProfile | None = None,
        min_explanation_ratio: float = 0.1,  # Minimum 10% for explanation
        max_explanation_ratio: float = 0.7,  # Maximum 70% for explanation
        risk_floor_ratio: float = 0.3,  # High-risk ops need at least 30% explanation
    ):
        """
        Initialize inflation budget.

        Args:
            central_bank: Bank for token metering
            default_audience: Default audience profile
            min_explanation_ratio: Minimum explanation ratio (even for experts)
            max_explanation_ratio: Maximum explanation ratio (cap)
            risk_floor_ratio: Minimum explanation for high-risk operations
        """
        self.bank = central_bank or CentralBank()
        self.default_audience = default_audience or AudienceProfile()
        self.min_explanation_ratio = min_explanation_ratio
        self.max_explanation_ratio = max_explanation_ratio
        self.risk_floor_ratio = risk_floor_ratio

        # Per-agent audience profiles
        self._agent_audiences: dict[str, AudienceProfile] = {}

        # Track inflation history
        self._inflation_history: list[tuple[datetime, float]] = []

    def set_agent_audience(self, agent_id: str, audience: AudienceProfile) -> None:
        """Set audience profile for an agent."""
        self._agent_audiences[agent_id] = audience

    def get_agent_audience(self, agent_id: str) -> AudienceProfile:
        """Get audience profile for agent (defaults to instance default)."""
        return self._agent_audiences.get(agent_id, self.default_audience)

    def calculate_pressure(
        self,
        complexity: ComplexityVector,
        base_tokens: int,
        audience: AudienceProfile | None = None,
    ) -> InflationPressure:
        """
        Calculate inflation pressure for an operation.

        Args:
            complexity: Complexity vector of the operation
            base_tokens: Tokens for core operation (no explanation)
            audience: Target audience (uses default if None)

        Returns:
            InflationPressure with all calculations
        """
        if audience is None:
            audience = self.default_audience

        return InflationPressure(
            complexity=complexity,
            audience=audience,
            base_tokens=base_tokens,
        )

    def evaluate(
        self,
        agent_id: str,
        complexity: ComplexityVector,
        base_tokens: int,
        available_budget: int | None = None,
        audience: AudienceProfile | None = None,
    ) -> AllocationDecision:
        """
        Evaluate an operation and allocate tokens.

        Args:
            agent_id: Agent requesting the operation
            complexity: Complexity vector
            base_tokens: Tokens for core operation
            available_budget: Available token budget (uses bank balance if None)
            audience: Target audience (uses agent default if None)

        Returns:
            AllocationDecision with approval status and allocation
        """
        if audience is None:
            audience = self.get_agent_audience(agent_id)

        if available_budget is None:
            available_budget = self.bank.get_balance()

        # Calculate pressure
        pressure = self.calculate_pressure(complexity, base_tokens, audience)
        report = InflationReport.analyze(pressure)

        # Calculate ideal allocation
        ideal_explanation = pressure.recommended_explanation_tokens

        # Apply constraints
        min_explanation = int(base_tokens * self.min_explanation_ratio)
        max_explanation = int(
            base_tokens * self.max_explanation_ratio / (1 - self.max_explanation_ratio)
        )

        # Risk floor: high-risk operations need more explanation
        if complexity.risk > 0.7:
            min_explanation = max(min_explanation, int(base_tokens * self.risk_floor_ratio))

        # Clamp to constraints
        explanation_tokens = max(min_explanation, min(max_explanation, ideal_explanation))

        # Add buffer for hyperinflation cases
        buffer = (
            int(base_tokens * 0.1) if report.category == InflationCategory.HYPERINFLATION else 0
        )

        total_needed = base_tokens + explanation_tokens + buffer

        # Check budget
        if total_needed <= available_budget:
            allocation = TokenAllocation(
                content_tokens=base_tokens,
                explanation_tokens=explanation_tokens,
                buffer_tokens=buffer,
            )
            return AllocationDecision(
                approved=True,
                allocation=allocation,
                reason=f"Inflation budget approved: {report.category.name} inflation "
                f"({explanation_tokens} explanation tokens)",
                inflation_report=report,
            )

        # Budget insufficient - try to deflate
        deficit = total_needed - available_budget

        # Can we fit with minimal explanation?
        minimal_total = base_tokens + min_explanation
        if minimal_total <= available_budget:
            # Deflate to fit
            available_for_explanation = available_budget - base_tokens - buffer
            allocation = TokenAllocation(
                content_tokens=base_tokens,
                explanation_tokens=max(min_explanation, available_for_explanation),
                buffer_tokens=0,
            )
            return AllocationDecision(
                approved=True,
                allocation=allocation,
                reason=f"Inflation budget approved with deflation: reduced from "
                f"{explanation_tokens} to {allocation.explanation_tokens} explanation tokens",
                inflation_report=report,
                deflation_required=True,
            )

        # Cannot fit even with minimal explanation
        # Suggest different audience level
        suggested_level = self._find_affordable_audience(complexity, base_tokens, available_budget)

        allocation = TokenAllocation(
            content_tokens=base_tokens,
            explanation_tokens=min_explanation,
        )
        return AllocationDecision(
            approved=False,
            allocation=allocation,
            reason=f"Insufficient budget for {report.category.name} inflation "
            f"(need {total_needed}, have {available_budget})",
            inflation_report=report,
            deficit=deficit,
            deflation_required=True,
            suggested_audience_level=suggested_level,
        )

    def _find_affordable_audience(
        self,
        complexity: ComplexityVector,
        base_tokens: int,
        available_budget: int,
    ) -> AudienceLevel | None:
        """Find an audience level that fits the budget."""
        for level in AudienceLevel:
            audience = AudienceProfile(level=level)
            pressure = self.calculate_pressure(complexity, base_tokens, audience)

            explanation = pressure.recommended_explanation_tokens
            min_exp = int(base_tokens * self.min_explanation_ratio)
            explanation = max(min_exp, explanation)

            if base_tokens + explanation <= available_budget:
                return level

        return None

    def record_inflation(self, rate: float) -> None:
        """Record inflation rate for history tracking."""
        self._inflation_history.append((datetime.now(), rate))
        # Keep last 1000 entries
        if len(self._inflation_history) > 1000:
            self._inflation_history = self._inflation_history[-1000:]

    def get_cpi(self, window_size: int = 100) -> float:
        """
        Get Semantic Consumer Price Index.

        Average inflation rate over recent operations.
        """
        if not self._inflation_history:
            return 0.0

        recent = self._inflation_history[-window_size:]
        return sum(r for _, r in recent) / len(recent)

    def get_inflation_trend(self) -> str:
        """Get inflation trend direction."""
        if len(self._inflation_history) < 20:
            return "insufficient_data"

        recent = self._inflation_history[-10:]
        older = self._inflation_history[-20:-10]

        recent_avg = sum(r for _, r in recent) / len(recent)
        older_avg = sum(r for _, r in older) / len(older)

        diff = recent_avg - older_avg
        if diff > 0.1:
            return "rising"
        elif diff < -0.1:
            return "falling"
        else:
            return "stable"


# =============================================================================
# Deflation Strategies
# =============================================================================


class DeflationStrategy(Enum):
    """
    Strategies for reducing verbosity when budget constrained.
    """

    COMPRESS = auto()  # Use pidgin/DSL for communication
    SUMMARIZE = auto()  # High-level summary instead of details
    DEFER = auto()  # Defer explanation to follow-up
    REFERENCE = auto()  # Reference external docs instead of inline
    AUDIENCE_SHIFT = auto()  # Target more expert audience
    CHUNK = auto()  # Break into smaller, cheaper operations


@dataclass
class DeflationProposal:
    """
    Proposal for reducing semantic inflation.
    """

    strategy: DeflationStrategy
    original_tokens: int
    proposed_tokens: int
    savings_ratio: float  # 0.0-1.0, how much reduction
    trade_offs: list[str]
    implementation_hint: str


class DeflationNegotiator:
    """
    Negotiates deflation strategies when budget is constrained.

    Works with G-gent for compression, and provides strategies
    for reducing explanation verbosity.
    """

    # Strategy descriptions
    STRATEGY_HINTS = {
        DeflationStrategy.COMPRESS: "Use domain-specific pidgin instead of natural language",
        DeflationStrategy.SUMMARIZE: "Provide high-level summary, omit implementation details",
        DeflationStrategy.DEFER: "Explain core concept now, details available on request",
        DeflationStrategy.REFERENCE: "Point to documentation: 'See X for details'",
        DeflationStrategy.AUDIENCE_SHIFT: "Assume higher expertise level in explanations",
        DeflationStrategy.CHUNK: "Break operation into smaller sub-operations",
    }

    # Trade-offs for each strategy
    STRATEGY_TRADEOFFS = {
        DeflationStrategy.COMPRESS: [
            "Requires pidgin to exist or be synthesized",
            "Loses natural language expressiveness",
        ],
        DeflationStrategy.SUMMARIZE: [
            "May miss important details",
            "Requires follow-up for full understanding",
        ],
        DeflationStrategy.DEFER: [
            "Creates explanation debt",
            "User may not request follow-up",
        ],
        DeflationStrategy.REFERENCE: [
            "Requires external docs to exist",
            "Breaks flow of explanation",
        ],
        DeflationStrategy.AUDIENCE_SHIFT: [
            "May confuse actual audience",
            "Assumes expertise that may not exist",
        ],
        DeflationStrategy.CHUNK: [
            "Loses big-picture view",
            "May need more total tokens across chunks",
        ],
    }

    # Estimated savings for each strategy
    STRATEGY_SAVINGS = {
        DeflationStrategy.COMPRESS: 0.7,  # 70% reduction with pidgin
        DeflationStrategy.SUMMARIZE: 0.5,  # 50% reduction with summary
        DeflationStrategy.DEFER: 0.4,  # 40% reduction by deferring
        DeflationStrategy.REFERENCE: 0.3,  # 30% reduction with references
        DeflationStrategy.AUDIENCE_SHIFT: 0.3,  # 30% reduction with expert audience
        DeflationStrategy.CHUNK: 0.2,  # 20% per-operation reduction
    }

    def __init__(self, budget: InflationBudget):
        """Initialize with inflation budget."""
        self.budget = budget

    def propose_deflation(
        self,
        inflation_report: InflationReport,
        target_reduction: float = 0.3,  # Target 30% reduction
    ) -> list[DeflationProposal]:
        """
        Propose deflation strategies for an operation.

        Args:
            inflation_report: Analysis of the inflation
            target_reduction: Desired token reduction ratio

        Returns:
            List of deflation proposals, ordered by effectiveness
        """
        proposals: list[DeflationProposal] = []
        original = inflation_report.pressure.total_recommended_tokens

        for strategy in DeflationStrategy:
            savings = self.STRATEGY_SAVINGS[strategy]

            # Adjust savings based on dominant complexity dimension
            adjusted_savings = self._adjust_savings(
                strategy,
                savings,
                inflation_report.dominant_driver,
            )

            proposed = int(original * (1 - adjusted_savings))

            proposals.append(
                DeflationProposal(
                    strategy=strategy,
                    original_tokens=original,
                    proposed_tokens=proposed,
                    savings_ratio=adjusted_savings,
                    trade_offs=self.STRATEGY_TRADEOFFS[strategy].copy(),
                    implementation_hint=self.STRATEGY_HINTS[strategy],
                )
            )

        # Sort by effectiveness (highest savings first)
        proposals.sort(key=lambda p: p.savings_ratio, reverse=True)

        return proposals

    def _adjust_savings(
        self,
        strategy: DeflationStrategy,
        base_savings: float,
        dominant_driver: ComplexityDimension,
    ) -> float:
        """Adjust savings based on complexity dimension."""
        # Some strategies work better for certain complexity types
        bonuses = {
            (DeflationStrategy.COMPRESS, ComplexityDimension.STRUCTURAL): 0.1,
            (DeflationStrategy.SUMMARIZE, ComplexityDimension.TEMPORAL): 0.1,
            (DeflationStrategy.CHUNK, ComplexityDimension.STRUCTURAL): 0.15,
            (DeflationStrategy.REFERENCE, ComplexityDimension.CONCEPTUAL): 0.1,
            (DeflationStrategy.AUDIENCE_SHIFT, ComplexityDimension.NOVELTY): 0.2,
        }

        penalties = {
            (
                DeflationStrategy.SUMMARIZE,
                ComplexityDimension.RISK,
            ): -0.2,  # Can't summarize high-risk
            (DeflationStrategy.AUDIENCE_SHIFT, ComplexityDimension.RISK): -0.3,
        }

        adjustment = bonuses.get((strategy, dominant_driver), 0.0)
        adjustment += penalties.get((strategy, dominant_driver), 0.0)

        return max(0.0, min(1.0, base_savings + adjustment))

    def recommend_strategy(
        self,
        inflation_report: InflationReport,
        constraints: dict[str, Any] | None = None,
    ) -> DeflationStrategy | None:
        """
        Recommend best deflation strategy.

        Args:
            inflation_report: Analysis of the inflation
            constraints: Optional constraints (e.g., {"no_pidgin": True})

        Returns:
            Best strategy, or None if none suitable
        """
        constraints = constraints or {}
        proposals = self.propose_deflation(inflation_report)

        for proposal in proposals:
            # Check constraints
            if constraints.get("no_pidgin") and proposal.strategy == DeflationStrategy.COMPRESS:
                continue
            if constraints.get("no_defer") and proposal.strategy == DeflationStrategy.DEFER:
                continue
            if constraints.get("no_reference") and proposal.strategy == DeflationStrategy.REFERENCE:
                continue

            # Check if strategy is viable for this risk level
            if inflation_report.pressure.complexity.risk > 0.8 and proposal.strategy in (
                DeflationStrategy.SUMMARIZE,
                DeflationStrategy.AUDIENCE_SHIFT,
            ):
                continue  # Can't skimp on explanation for high-risk ops

            return proposal.strategy

        return None


# =============================================================================
# Complexity Analyzer
# =============================================================================


class ComplexityAnalyzer:
    """
    Analyzes operations to determine complexity vector.

    Uses heuristics to estimate complexity from:
    - Code metrics (if code)
    - Natural language analysis (if text)
    - Operation metadata
    """

    def analyze_code(self, code: str) -> ComplexityVector:
        """
        Analyze code for complexity metrics.

        Uses simple heuristics:
        - Nesting depth → structural
        - async/await → temporal
        - class/type hints → conceptual
        - imports → relational
        """
        structural = self._code_structural_complexity(code)
        temporal = self._code_temporal_complexity(code)
        conceptual = self._code_conceptual_complexity(code)
        relational = self._code_relational_complexity(code)

        # Novelty and risk are context-dependent, estimate from code patterns
        novelty = 0.3  # Default moderate novelty
        risk = self._code_risk_estimate(code)

        return ComplexityVector(
            structural=structural,
            temporal=temporal,
            conceptual=conceptual,
            relational=relational,
            novelty=novelty,
            risk=risk,
        )

    def _code_structural_complexity(self, code: str) -> float:
        """Estimate structural complexity from code."""
        lines = code.split("\n")

        # Count nesting indicators
        max_indent = 0
        current_indent = 0
        for line in lines:
            stripped = line.lstrip()
            if not stripped:
                continue
            indent = len(line) - len(stripped)
            current_indent = indent
            max_indent = max(max_indent, current_indent)

        # Normalize: 4 spaces per level, max 10 levels = 40 spaces
        nesting_score = min(1.0, max_indent / 40)

        # Count control flow
        control_keywords = [
            "if",
            "else",
            "elif",
            "for",
            "while",
            "try",
            "except",
            "with",
            "match",
            "case",
        ]
        control_count = sum(
            1
            for word in control_keywords
            if f" {word} " in f" {code} " or code.strip().startswith(word)
        )
        control_score = min(1.0, control_count / 10)

        return (nesting_score + control_score) / 2

    def _code_temporal_complexity(self, code: str) -> float:
        """Estimate temporal complexity from code."""
        async_count = code.count("async ") + code.count("await ")
        yield_count = code.count("yield ")
        callback_count = code.count("callback") + code.count("on_")

        temporal_indicators = async_count + yield_count + callback_count
        return min(1.0, temporal_indicators / 5)

    def _code_conceptual_complexity(self, code: str) -> float:
        """Estimate conceptual complexity from code."""
        class_count = code.count("class ")
        type_hints = code.count("->") + code.count(": ")
        generic_count = code.count("[") + code.count("Generic")
        protocol_count = code.count("Protocol") + code.count("ABC")

        conceptual_indicators = (
            class_count + type_hints / 10 + generic_count / 5 + protocol_count * 2
        )
        return min(1.0, conceptual_indicators / 10)

    def _code_relational_complexity(self, code: str) -> float:
        """Estimate relational complexity from code."""
        import_count = code.count("import ") + code.count("from ")
        dot_access = code.count(".")

        relational_indicators = import_count + dot_access / 20
        return min(1.0, relational_indicators / 10)

    def _code_risk_estimate(self, code: str) -> float:
        """Estimate risk level from code patterns."""
        high_risk_patterns = [
            "eval(",
            "exec(",
            "os.system",
            "subprocess",
            "delete",
            "drop",
            "truncate",
            "rm ",
            "password",
            "secret",
            "token",
            "credential",
        ]

        moderate_risk_patterns = [
            "write",
            "update",
            "modify",
            "change",
            "api",
            "http",
            "request",
            "send",
        ]

        code_lower = code.lower()
        high_risk_count = sum(1 for p in high_risk_patterns if p in code_lower)
        moderate_risk_count = sum(1 for p in moderate_risk_patterns if p in code_lower)

        risk = high_risk_count * 0.3 + moderate_risk_count * 0.1
        return min(1.0, risk)

    def analyze_text(self, text: str, is_technical: bool = True) -> ComplexityVector:
        """
        Analyze text for complexity metrics.

        Uses simple heuristics based on:
        - Sentence complexity
        - Technical term density
        - Reference density
        """
        words = text.split()
        sentences = text.split(".")

        # Structural: sentence length
        avg_sentence_len = len(words) / max(1, len(sentences))
        structural = min(1.0, avg_sentence_len / 30)

        # Temporal: sequence indicators
        temporal_words = [
            "then",
            "next",
            "after",
            "before",
            "finally",
            "first",
            "second",
            "step",
        ]
        temporal_count = sum(1 for w in words if w.lower() in temporal_words)
        temporal = min(1.0, temporal_count / 5)

        # Conceptual: technical density
        if is_technical:
            # Look for technical patterns: camelCase, snake_case, acronyms
            import re

            camel_case = len(re.findall(r"[a-z][A-Z]", text))
            snake_case = text.count("_")
            acronyms = len(re.findall(r"\b[A-Z]{2,}\b", text))
            conceptual = min(1.0, (camel_case + snake_case / 5 + acronyms) / 10)
        else:
            conceptual = 0.2

        # Relational: reference indicators
        reference_patterns = ["see also", "refer to", "depends on", "requires", "uses"]
        reference_count = sum(1 for p in reference_patterns if p in text.lower())
        relational = min(1.0, reference_count / 3)

        # Novelty: assume moderate for text
        novelty = 0.4

        # Risk: look for warning patterns
        risk_patterns = [
            "warning",
            "caution",
            "important",
            "critical",
            "danger",
            "careful",
        ]
        risk_count = sum(1 for p in risk_patterns if p in text.lower())
        risk = min(1.0, risk_count / 3)

        return ComplexityVector(
            structural=structural,
            temporal=temporal,
            conceptual=conceptual,
            relational=relational,
            novelty=novelty,
            risk=risk,
        )

    def from_metadata(
        self,
        structural: float = 0.3,
        temporal: float = 0.2,
        conceptual: float = 0.3,
        relational: float = 0.2,
        novelty: float = 0.3,
        risk: float = 0.2,
    ) -> ComplexityVector:
        """Create complexity vector from explicit metadata."""
        return ComplexityVector(
            structural=structural,
            temporal=temporal,
            conceptual=conceptual,
            relational=relational,
            novelty=novelty,
            risk=risk,
        )


# =============================================================================
# Semantic CPI Monitor
# =============================================================================


@dataclass
class CPISnapshot:
    """
    Snapshot of Semantic Consumer Price Index.
    """

    timestamp: datetime
    cpi: float  # Current CPI (average inflation rate)
    trend: str  # "rising", "falling", "stable"
    sample_size: int
    category_breakdown: dict[str, float]  # CPI by inflation category


class SemanticCPIMonitor:
    """
    Monitor semantic inflation across the system.

    Like economic CPI, tracks the "cost" of semantic operations
    over time, detecting inflation trends.
    """

    def __init__(self) -> None:
        """Initialize CPI monitor."""
        self._observations: list[tuple[datetime, InflationCategory, float]] = []
        self._snapshots: list[CPISnapshot] = []

    def observe(self, report: InflationReport) -> None:
        """Record an inflation observation."""
        self._observations.append(
            (
                datetime.now(),
                report.category,
                report.pressure.inflation_rate,
            )
        )

        # Prune old observations (keep last 10000)
        if len(self._observations) > 10000:
            self._observations = self._observations[-10000:]

    def get_current_cpi(self, window_size: int = 100) -> float:
        """Get current CPI (average inflation rate)."""
        if not self._observations:
            return 0.0

        recent = self._observations[-window_size:]
        return sum(r for _, _, r in recent) / len(recent)

    def get_category_breakdown(self, window_size: int = 100) -> dict[str, float]:
        """Get CPI breakdown by inflation category."""
        if not self._observations:
            return {}

        recent = self._observations[-window_size:]

        by_category: dict[InflationCategory, list[float]] = {}
        for _, cat, rate in recent:
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(rate)

        return {cat.name: sum(rates) / len(rates) for cat, rates in by_category.items()}

    def get_trend(self, window_size: int = 50) -> str:
        """Get inflation trend."""
        if len(self._observations) < window_size * 2:
            return "insufficient_data"

        recent = self._observations[-window_size:]
        older = self._observations[-window_size * 2 : -window_size]

        recent_avg = sum(r for _, _, r in recent) / len(recent)
        older_avg = sum(r for _, _, r in older) / len(older)

        diff = recent_avg - older_avg
        if diff > 0.1:
            return "rising"
        elif diff < -0.1:
            return "falling"
        else:
            return "stable"

    def snapshot(self) -> CPISnapshot:
        """Take a CPI snapshot."""
        snap = CPISnapshot(
            timestamp=datetime.now(),
            cpi=self.get_current_cpi(),
            trend=self.get_trend(),
            sample_size=len(self._observations),
            category_breakdown=self.get_category_breakdown(),
        )
        self._snapshots.append(snap)
        return snap

    def get_history(self, limit: int = 10) -> list[CPISnapshot]:
        """Get recent CPI snapshots."""
        return self._snapshots[-limit:]


# =============================================================================
# Convenience Functions
# =============================================================================


def create_inflation_budget(
    central_bank: CentralBank | None = None,
    default_audience: AudienceProfile | None = None,
) -> InflationBudget:
    """
    Create an InflationBudget with default configuration.

    Args:
        central_bank: Optional central bank (creates default if None)
        default_audience: Optional default audience (creates intermediate if None)

    Returns:
        Configured InflationBudget
    """
    return InflationBudget(
        central_bank=central_bank,
        default_audience=default_audience,
    )


def analyze_complexity(
    content: str,
    is_code: bool = False,
) -> ComplexityVector:
    """
    Analyze content for complexity.

    Args:
        content: Code or text to analyze
        is_code: Whether content is code (True) or text (False)

    Returns:
        ComplexityVector with all dimensions
    """
    analyzer = ComplexityAnalyzer()
    if is_code:
        return analyzer.analyze_code(content)
    return analyzer.analyze_text(content)


def calculate_inflation_pressure(
    complexity: ComplexityVector,
    base_tokens: int,
    audience_level: AudienceLevel = AudienceLevel.INTERMEDIATE,
) -> InflationPressure:
    """
    Calculate inflation pressure for an operation.

    Args:
        complexity: Complexity vector
        base_tokens: Tokens for core operation
        audience_level: Target audience level

    Returns:
        InflationPressure with all calculations
    """
    audience = AudienceProfile(level=audience_level)
    return InflationPressure(
        complexity=complexity,
        audience=audience,
        base_tokens=base_tokens,
    )


def get_deflation_recommendations(
    pressure: InflationPressure,
    target_reduction: float = 0.3,
) -> list[DeflationProposal]:
    """
    Get deflation recommendations for an operation.

    Args:
        pressure: Inflation pressure
        target_reduction: Target reduction ratio

    Returns:
        List of deflation proposals
    """
    report = InflationReport.analyze(pressure)
    budget = InflationBudget()
    negotiator = DeflationNegotiator(budget)
    return negotiator.propose_deflation(report, target_reduction)


def estimate_explanation_tokens(
    complexity: ComplexityVector,
    base_tokens: int,
    audience_level: AudienceLevel = AudienceLevel.INTERMEDIATE,
) -> int:
    """
    Estimate how many explanation tokens are needed.

    Args:
        complexity: Complexity of the operation
        base_tokens: Tokens for core operation
        audience_level: Target audience level

    Returns:
        Recommended explanation tokens
    """
    pressure = calculate_inflation_pressure(complexity, base_tokens, audience_level)
    return pressure.recommended_explanation_tokens
