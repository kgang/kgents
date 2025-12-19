"""
Value Tensor: Multi-Dimensional Resource Ontology

Implements the Value Tensor from spec/b-gents/value-tensor.md:
- Four dimensions: Physical, Semantic, Economic, Ethical
- Exchange rate matrix for dimension translation
- Conservation laws and anti-delusion protection
- Tensor algebra operations

The Value Tensor formalizes the insight that "Cost is a point. Value is a manifold."
Traditional metering tracks only tokens, but value flows through multiple dimensions:
- Physical: tokens, time, memory, energy
- Semantic: complexity, structure, meaning
- Economic: cost, revenue, profit, debt
- Ethical: risk, virtue, externalities

This module provides:
1. Dimension dataclasses for each value type
2. Exchange rates for dimension translation (with loss tracking)
3. Conservation laws that must hold
4. Anti-delusion checks for cross-dimensional consistency
5. Tensor algebra (add, scale, project)
"""

from __future__ import annotations

import zlib
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, ClassVar, Literal, Optional

# =============================================================================
# Dimension 1: Physical Resources
# =============================================================================


@dataclass
class PhysicalDimension:
    """
    Physical resources consumed or produced.

    These are directly measurable and fungible within type.
    The ground truth of compute cost.
    """

    # Token-based
    input_tokens: int = 0
    output_tokens: int = 0

    # Time-based
    wall_clock_ms: float = 0.0
    compute_time_ms: float = 0.0
    queue_time_ms: float = 0.0

    # Memory-based
    peak_memory_bytes: int = 0
    context_window_used: int = 0

    # Energy-based (if available)
    estimated_joules: Optional[float] = None

    # Model-specific multipliers
    model_id: str = "unknown"
    cost_multiplier: float = 1.0  # opus=15x, sonnet=3x, haiku=1x

    @property
    def total_tokens(self) -> int:
        """Total tokens consumed."""
        return self.input_tokens + self.output_tokens

    @property
    def normalized_tokens(self) -> float:
        """Tokens normalized by model cost."""
        return self.total_tokens * self.cost_multiplier

    def __add__(self, other: "PhysicalDimension") -> "PhysicalDimension":
        """Add two physical dimensions."""
        return PhysicalDimension(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            wall_clock_ms=self.wall_clock_ms + other.wall_clock_ms,
            compute_time_ms=self.compute_time_ms + other.compute_time_ms,
            queue_time_ms=self.queue_time_ms + other.queue_time_ms,
            peak_memory_bytes=max(self.peak_memory_bytes, other.peak_memory_bytes),
            context_window_used=max(self.context_window_used, other.context_window_used),
            estimated_joules=(
                (self.estimated_joules or 0) + (other.estimated_joules or 0)
                if self.estimated_joules or other.estimated_joules
                else None
            ),
            model_id=self.model_id,  # Keep first model
            cost_multiplier=max(self.cost_multiplier, other.cost_multiplier),
        )


# =============================================================================
# Dimension 2: Semantic Quality
# =============================================================================


@dataclass
class SemanticDimension:
    """
    Semantic quality of agent output.

    Since true semantic content is undecidable, we use proxy metrics
    with explicit uncertainty bounds. Kolmogorov complexity approximated
    via compression ratio.
    """

    # Complexity metrics (Kolmogorov proxies)
    compression_ratio: float = 0.5  # Lower = more structured
    entropy_estimate: float = 0.0  # Shannon entropy of output
    kolmogorov_proxy: float = 0.0  # Combined complexity estimate

    # Structural metrics
    ast_valid: Optional[bool] = None  # For code: does it parse?
    type_valid: Optional[bool] = None  # For code: does it type-check?
    schema_valid: Optional[bool] = None  # For data: does it match schema?

    # Semantic coherence
    self_consistency: float = 0.0  # Does output contradict itself?
    input_alignment: float = 0.0  # Does output address input intent?
    domain_relevance: float = 0.0  # Is output on-topic?

    # Uncertainty bounds
    confidence: float = 0.5  # How confident are we in these metrics?
    measurement_method: str = "unknown"  # How were metrics obtained?

    @property
    def quality_score(self) -> float:
        """Aggregate quality score with uncertainty weighting."""
        base = (
            (1 - self.compression_ratio) * 0.3
            + self.input_alignment * 0.4
            + self.domain_relevance * 0.3
        )
        return base * self.confidence

    @classmethod
    def from_compression(cls, text: str) -> "SemanticDimension":
        """
        Create semantic dimension from compression analysis.

        Better proxy than word count: compression ratio reveals structure.
        Reliability: MEDIUM
        """
        if not text:
            return cls(
                compression_ratio=1.0,
                confidence=0.1,
                measurement_method="compression_heuristic_empty",
            )

        original = len(text.encode("utf-8"))
        compressed = len(zlib.compress(text.encode("utf-8")))
        ratio = compressed / original if original > 0 else 1.0

        return cls(
            compression_ratio=ratio,
            entropy_estimate=ratio * 8,  # Bits per byte
            kolmogorov_proxy=1.0 - ratio,
            confidence=0.5,
            measurement_method="compression_heuristic",
        )

    @classmethod
    def from_validation(
        cls,
        text: str,
        validators: list[Callable[[str], bool]],
    ) -> "SemanticDimension":
        """
        Create semantic dimension from validation checks.

        Best proxy: actual validation (AST, types, tests).
        Reliability: HIGH
        """
        if not validators:
            return cls.from_compression(text)

        passed = sum(1 for v in validators if v(text))
        total = len(validators)
        pass_rate = passed / total if total > 0 else 0

        return cls(
            compression_ratio=0.3,  # Assume structured if validating
            entropy_estimate=2.0,  # Low entropy if structured
            kolmogorov_proxy=pass_rate,
            ast_valid=passed > 0,
            confidence=0.8,
            measurement_method="validation_heuristic",
        )


# =============================================================================
# Dimension 3: Economic Value
# =============================================================================


class ImpactTier(str, Enum):
    """DORA-inspired value tiers."""

    SYNTACTIC = "syntactic"  # Valid syntax only
    FUNCTIONAL = "functional"  # Tests pass
    DEPLOYMENT = "deployment"  # Successfully deployed
    ETHICAL = "ethical"  # Policy compliant + positive externalities


@dataclass
class EconomicDimension:
    """
    Economic value in monetary terms.

    Tracks both costs (Gas) and value created (Impact).
    Implements dual-currency architecture from UVP.
    """

    # Cost side (Gas)
    gas_cost_usd: float = 0.0  # Direct API costs
    opportunity_cost_usd: float = 0.0  # What else could we have done?
    infrastructure_cost_usd: float = 0.0  # Servers, storage, etc.

    # Value side (Impact)
    impact_value: float = 0.0  # Dimensionless impact units
    impact_tier: ImpactTier = ImpactTier.SYNTACTIC
    realized_revenue_usd: float = 0.0  # If we can measure it

    # Derived
    @property
    def total_cost(self) -> float:
        """Total cost including opportunity cost."""
        return self.gas_cost_usd + self.opportunity_cost_usd + self.infrastructure_cost_usd

    @property
    def profit_usd(self) -> float:
        """Value - Cost (may be negative)."""
        return self.impact_value - self.total_cost

    @property
    def roc(self) -> float:
        """Return on Compute."""
        if self.total_cost <= 0:
            return 0.0
        return self.impact_value / self.total_cost

    # Uncertainty
    value_confidence: float = 0.5  # How confident in impact estimate?
    cost_confidence: float = 0.9  # How confident in cost estimate?

    @property
    def net_present_value(self) -> float:
        """NPV accounting for uncertainty."""
        expected_value = self.impact_value * self.value_confidence
        expected_cost = self.gas_cost_usd * self.cost_confidence
        return expected_value - expected_cost


# =============================================================================
# Dimension 4: Ethical Standing
# =============================================================================


@dataclass
class EthicalDimension:
    """
    Ethical qualities that affect value calculation.

    These are multipliers and adjustments, not direct values.
    Implements Sin Tax / Virtue Subsidy from UVP.
    """

    # Risk assessment (0 = safe, 1 = critical)
    security_risk: float = 0.0
    privacy_risk: float = 0.0
    bias_risk: float = 0.0
    reliability_risk: float = 0.0

    # Virtue assessment (positive = improvement)
    maintainability_improvement: float = 0.0
    accessibility_improvement: float = 0.0
    documentation_improvement: float = 0.0
    test_coverage_improvement: float = 0.0

    # Policy compliance
    license_compliant: bool = True
    security_policy_compliant: bool = True
    style_guide_compliant: bool = True

    @property
    def sin_tax_multiplier(self) -> float:
        """Penalty for risks (< 1.0 reduces value)."""
        base = 1.0
        base *= 1.0 - self.security_risk * 0.67  # Up to 3x penalty
        base *= 1.0 - self.privacy_risk * 0.75  # Up to 4x penalty
        base *= 1.0 - self.bias_risk * 0.5  # Up to 2x penalty
        base *= 1.0 - self.reliability_risk * 0.3  # Up to 1.4x penalty
        return max(0.1, base)  # Floor at 10%

    @property
    def virtue_subsidy_multiplier(self) -> float:
        """Bonus for virtues (> 1.0 increases value)."""
        base = 1.0
        base += self.maintainability_improvement * 0.3
        base += self.accessibility_improvement * 0.6
        base += self.documentation_improvement * 0.2
        base += self.test_coverage_improvement * 0.5
        return min(3.0, base)  # Cap at 3x

    @property
    def net_ethical_multiplier(self) -> float:
        """Combined ethical adjustment."""
        base = self.sin_tax_multiplier * self.virtue_subsidy_multiplier

        # Policy compliance bonus/penalty
        if not self.license_compliant:
            base *= 0.2  # 5x penalty for license violation
        if not self.security_policy_compliant:
            base *= 0.5  # 2x penalty

        return base


# =============================================================================
# Exchange Rate System
# =============================================================================


@dataclass
class ExchangeRate:
    """Single exchange rate with metadata."""

    rate: float  # Units of target per unit of source
    loss: float  # Fraction lost in translation (0-1)
    confidence: float  # How reliable is this rate (0-1)
    method: str  # How was this rate determined
    last_updated: datetime = field(default_factory=datetime.now)

    # Sentinel for unknown rates
    UNDEFINED: ClassVar["ExchangeRate"]


ExchangeRate.UNDEFINED = ExchangeRate(
    rate=0.0,
    loss=1.0,
    confidence=0.0,
    method="undefined",
)


@dataclass
class ExchangeMatrix:
    """
    Exchange rates between dimensions.

    Not all exchanges are lossless. The matrix tracks:
    - Rate: How much of B per unit of A
    - Loss: Information/value lost in translation
    - Confidence: How reliable is this rate
    """

    rates: dict[tuple[str, str], ExchangeRate] = field(default_factory=dict)

    def get_rate(self, from_dim: str, to_dim: str) -> ExchangeRate:
        """Get exchange rate between dimensions."""
        return self.rates.get((from_dim, to_dim), ExchangeRate.UNDEFINED)

    def set_rate(self, from_dim: str, to_dim: str, rate: ExchangeRate) -> None:
        """Set exchange rate between dimensions."""
        self.rates[(from_dim, to_dim)] = rate

    def convert(
        self,
        value: float,
        from_dim: str,
        to_dim: str,
    ) -> tuple[float, float]:
        """
        Convert value between dimensions.

        Returns: (converted_value, information_loss)
        """
        rate = self.get_rate(from_dim, to_dim)
        converted = value * rate.rate * (1 - rate.loss)
        loss = value * rate.loss
        return (converted, loss)


def create_standard_exchange_rates() -> ExchangeMatrix:
    """Create standard exchange rates for common conversions."""
    matrix = ExchangeMatrix()

    # Physical → Economic (direct, low loss)
    matrix.set_rate(
        "physical.tokens",
        "economic.gas_cost_usd",
        ExchangeRate(
            rate=0.00001,  # $0.01 per 1000 tokens (varies by model)
            loss=0.0,
            confidence=0.99,
            method="api_pricing",
        ),
    )

    # Semantic → Economic (indirect, high loss)
    matrix.set_rate(
        "semantic.quality_score",
        "economic.impact_value",
        ExchangeRate(
            rate=100.0,  # 1.0 quality → 100 impact units
            loss=0.3,  # 30% lost in translation
            confidence=0.5,
            method="heuristic_calibration",
        ),
    )

    # Physical → Semantic (very indirect)
    matrix.set_rate(
        "physical.tokens",
        "semantic.kolmogorov_proxy",
        ExchangeRate(
            rate=0.001,  # Tokens weakly predict complexity
            loss=0.7,  # 70% information loss
            confidence=0.2,
            method="statistical_correlation",
        ),
    )

    # Ethical → Economic (policy-driven)
    matrix.set_rate(
        "ethical.net_multiplier",
        "economic.impact_value",
        ExchangeRate(
            rate=1.0,  # Direct multiplier
            loss=0.0,
            confidence=0.9,
            method="policy_definition",
        ),
    )

    return matrix


# =============================================================================
# Conservation Laws
# =============================================================================


@dataclass
class ConservationLaw:
    """
    An invariant that must hold in the value tensor.

    Violations indicate bugs, fraud, or delusion.
    """

    name: str
    description: str
    check: Callable[["ValueTensor", "ValueTensor"], bool]
    severity: Literal["warning", "error", "critical"]


# Pre-defined conservation laws
TOKEN_MONOTONICITY = ConservationLaw(
    name="token_monotonicity",
    description="Total tokens consumed never decreases",
    check=lambda before, after: (after.physical.total_tokens >= before.physical.total_tokens),
    severity="critical",
)

TIME_ARROW = ConservationLaw(
    name="time_arrow",
    description="Time flows forward",
    check=lambda before, after: (after.physical.wall_clock_ms >= before.physical.wall_clock_ms),
    severity="critical",
)

BUDGET_CONSTRAINT = ConservationLaw(
    name="budget_constraint",
    description="Cannot create Gas from nothing",
    check=lambda before, after: (
        after.economic.gas_cost_usd
        <= before.economic.gas_cost_usd + 1000  # 1000 = max budget increase
    ),
    severity="error",
)

IMPACT_JUSTIFICATION = ConservationLaw(
    name="impact_justification",
    description="Impact must be justified by semantic quality",
    check=lambda before, after: (
        after.economic.impact_value
        <= after.semantic.quality_score * 1000  # Max 1000 impact per quality
    ),
    severity="warning",
)

ETHICAL_BOUNDS = ConservationLaw(
    name="ethical_bounds",
    description="Ethical multiplier must be in valid range",
    check=lambda before, after: (0.1 <= after.ethical.net_ethical_multiplier <= 3.0),
    severity="error",
)

DEFAULT_CONSERVATION_LAWS = [
    TOKEN_MONOTONICITY,
    TIME_ARROW,
    BUDGET_CONSTRAINT,
    IMPACT_JUSTIFICATION,
    ETHICAL_BOUNDS,
]


# =============================================================================
# Anomaly Detection
# =============================================================================


@dataclass
class Anomaly:
    """Detected anomaly in value tensor."""

    type: str
    message: str
    severity: Literal["info", "warning", "error", "critical"]
    dimensions: list[str]
    timestamp: datetime = field(default_factory=datetime.now)


class AntiDelusionChecker:
    """
    Detects inconsistencies that indicate delusion or fraud.

    If an agent claims high impact but physical/semantic dimensions
    don't support it, something is wrong.
    """

    def check_consistency(self, tensor: "ValueTensor") -> list[Anomaly]:
        """Run all consistency checks."""
        anomalies = []

        # Check 1: High impact requires high quality
        if tensor.economic.impact_value > 500:
            if tensor.semantic.quality_score < 0.5:
                anomalies.append(
                    Anomaly(
                        type="impact_quality_mismatch",
                        message="High impact claimed but quality score is low",
                        severity="warning",
                        dimensions=["economic", "semantic"],
                    )
                )

        # Check 2: Validated code should have good compression
        if tensor.semantic.ast_valid and tensor.semantic.type_valid:
            if tensor.semantic.compression_ratio > 0.8:
                anomalies.append(
                    Anomaly(
                        type="validation_compression_mismatch",
                        message="Code validates but has high entropy (suspicious)",
                        severity="info",
                        dimensions=["semantic"],
                    )
                )

        # Check 3: Ethical multiplier consistency
        if tensor.ethical.security_risk > 0.5:
            if tensor.ethical.sin_tax_multiplier > 0.8:
                anomalies.append(
                    Anomaly(
                        type="risk_tax_mismatch",
                        message="High security risk but low sin tax applied",
                        severity="error",
                        dimensions=["ethical"],
                    )
                )

        # Check 4: Cost-value sanity
        if tensor.economic.roc > 10.0:
            anomalies.append(
                Anomaly(
                    type="suspicious_roc",
                    message="RoC > 10x is unusually high, verify impact",
                    severity="warning",
                    dimensions=["economic"],
                )
            )

        # Check 5: Zero-cost high impact
        if tensor.economic.gas_cost_usd == 0 and tensor.economic.impact_value > 0:
            anomalies.append(
                Anomaly(
                    type="free_lunch_detected",
                    message="Impact generated with zero gas cost",
                    severity="warning",
                    dimensions=["economic"],
                )
            )

        return anomalies

    def validate_transition(
        self,
        before: "ValueTensor",
        after: "ValueTensor",
    ) -> list[Anomaly]:
        """Validate a state transition."""
        anomalies = []

        # Run conservation law checks
        for law in after.invariants:
            if not law.check(before, after):
                anomalies.append(
                    Anomaly(
                        type=f"conservation_violation:{law.name}",
                        message=law.description,
                        severity=law.severity,
                        dimensions=["all"],
                    )
                )

        # Check for impossible improvements
        quality_delta = after.semantic.quality_score - before.semantic.quality_score
        token_delta = after.physical.total_tokens - before.physical.total_tokens

        if quality_delta > 0.5 and token_delta < 100:
            anomalies.append(
                Anomaly(
                    type="free_lunch_detected",
                    message="Large quality improvement with minimal tokens (suspicious)",
                    severity="warning",
                    dimensions=["physical", "semantic"],
                )
            )

        return anomalies


# =============================================================================
# The Value Tensor
# =============================================================================


@dataclass
class ValueTensor:
    """
    Multi-dimensional representation of resource/value state.

    A tensor in the mathematical sense: a multi-linear map that
    transforms covariantly under change of basis (currency conversion).

    The Value Tensor formalizes multi-dimensional value accounting:
    - Physical: tokens, time, memory (measurable)
    - Semantic: quality, complexity, structure (heuristic)
    - Economic: cost, value, profit (derived)
    - Ethical: risk, virtue, compliance (multipliers)
    """

    physical: PhysicalDimension = field(default_factory=PhysicalDimension)
    semantic: SemanticDimension = field(default_factory=SemanticDimension)
    economic: EconomicDimension = field(default_factory=EconomicDimension)
    ethical: EthicalDimension = field(default_factory=EthicalDimension)

    # Exchange rates for dimension conversion
    exchange_rates: ExchangeMatrix = field(default_factory=create_standard_exchange_rates)

    # Conservation laws that must hold
    invariants: list[ConservationLaw] = field(
        default_factory=lambda: DEFAULT_CONSERVATION_LAWS.copy()
    )

    # Timestamp
    timestamp: datetime = field(default_factory=datetime.now)

    @classmethod
    def initial(cls) -> "ValueTensor":
        """Create initial (zero) value tensor."""
        return cls()

    def copy(self) -> "ValueTensor":
        """Create a deep copy of this tensor."""
        import copy as copy_module

        return copy_module.deepcopy(self)

    def dimension_values(self) -> list[tuple[str, float]]:
        """Get all dimension values as (name, value) pairs."""
        return [
            ("physical.tokens", float(self.physical.total_tokens)),
            ("physical.time_ms", self.physical.wall_clock_ms),
            ("semantic.quality_score", self.semantic.quality_score),
            ("semantic.compression_ratio", self.semantic.compression_ratio),
            ("economic.gas_cost_usd", self.economic.gas_cost_usd),
            ("economic.impact_value", self.economic.impact_value),
            ("ethical.net_multiplier", self.ethical.net_ethical_multiplier),
        ]

    def project_to_usd(self) -> float:
        """
        Project tensor to USD value.

        Uses exchange rates to convert all dimensions to economic.
        """
        # Start with direct economic value
        total = self.economic.impact_value * self.ethical.net_ethical_multiplier

        # Subtract costs
        total -= self.economic.gas_cost_usd

        return total

    def validate(self) -> list[Anomaly]:
        """Run anti-delusion checks on current state."""
        checker = AntiDelusionChecker()
        return checker.check_consistency(self)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "physical": {
                "input_tokens": self.physical.input_tokens,
                "output_tokens": self.physical.output_tokens,
                "wall_clock_ms": self.physical.wall_clock_ms,
                "compute_time_ms": self.physical.compute_time_ms,
                "model_id": self.physical.model_id,
                "cost_multiplier": self.physical.cost_multiplier,
            },
            "semantic": {
                "compression_ratio": self.semantic.compression_ratio,
                "entropy_estimate": self.semantic.entropy_estimate,
                "quality_score": self.semantic.quality_score,
                "confidence": self.semantic.confidence,
                "measurement_method": self.semantic.measurement_method,
            },
            "economic": {
                "gas_cost_usd": self.economic.gas_cost_usd,
                "impact_value": self.economic.impact_value,
                "impact_tier": self.economic.impact_tier.value,
                "roc": self.economic.roc,
            },
            "ethical": {
                "security_risk": self.ethical.security_risk,
                "privacy_risk": self.ethical.privacy_risk,
                "sin_tax_multiplier": self.ethical.sin_tax_multiplier,
                "virtue_subsidy_multiplier": self.ethical.virtue_subsidy_multiplier,
                "net_multiplier": self.ethical.net_ethical_multiplier,
            },
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ValueTensor":
        """Deserialize from dictionary."""
        physical = PhysicalDimension(
            input_tokens=data.get("physical", {}).get("input_tokens", 0),
            output_tokens=data.get("physical", {}).get("output_tokens", 0),
            wall_clock_ms=data.get("physical", {}).get("wall_clock_ms", 0.0),
            compute_time_ms=data.get("physical", {}).get("compute_time_ms", 0.0),
            model_id=data.get("physical", {}).get("model_id", "unknown"),
            cost_multiplier=data.get("physical", {}).get("cost_multiplier", 1.0),
        )

        semantic = SemanticDimension(
            compression_ratio=data.get("semantic", {}).get("compression_ratio", 0.5),
            entropy_estimate=data.get("semantic", {}).get("entropy_estimate", 0.0),
            confidence=data.get("semantic", {}).get("confidence", 0.5),
            measurement_method=data.get("semantic", {}).get("measurement_method", "unknown"),
        )

        economic = EconomicDimension(
            gas_cost_usd=data.get("economic", {}).get("gas_cost_usd", 0.0),
            impact_value=data.get("economic", {}).get("impact_value", 0.0),
            impact_tier=ImpactTier(data.get("economic", {}).get("impact_tier", "syntactic")),
        )

        ethical = EthicalDimension(
            security_risk=data.get("ethical", {}).get("security_risk", 0.0),
            privacy_risk=data.get("ethical", {}).get("privacy_risk", 0.0),
        )

        timestamp = datetime.now()
        if "timestamp" in data:
            try:
                timestamp = datetime.fromisoformat(data["timestamp"])
            except (ValueError, TypeError):
                pass

        return cls(
            physical=physical,
            semantic=semantic,
            economic=economic,
            ethical=ethical,
            timestamp=timestamp,
        )


# =============================================================================
# Tensor Algebra
# =============================================================================


class TensorAlgebra:
    """
    Operations on value tensors.

    These operations respect dimension structure and conservation laws.
    """

    @staticmethod
    def add(a: ValueTensor, b: ValueTensor) -> ValueTensor:
        """
        Add two tensors (e.g., combining two agent outputs).

        Physical: Sum (tokens add up)
        Semantic: Weighted average (quality doesn't simply add)
        Economic: Sum (costs and values add)
        Ethical: Min (worst risk dominates)
        """
        # Physical: sum
        physical = a.physical + b.physical

        # Semantic: weighted average by confidence
        total_conf = a.semantic.confidence + b.semantic.confidence
        if total_conf > 0:
            semantic = SemanticDimension(
                compression_ratio=(
                    a.semantic.compression_ratio * a.semantic.confidence
                    + b.semantic.compression_ratio * b.semantic.confidence
                )
                / total_conf,
                entropy_estimate=(
                    a.semantic.entropy_estimate * a.semantic.confidence
                    + b.semantic.entropy_estimate * b.semantic.confidence
                )
                / total_conf,
                kolmogorov_proxy=(
                    a.semantic.kolmogorov_proxy * a.semantic.confidence
                    + b.semantic.kolmogorov_proxy * b.semantic.confidence
                )
                / total_conf,
                input_alignment=(
                    a.semantic.input_alignment * a.semantic.confidence
                    + b.semantic.input_alignment * b.semantic.confidence
                )
                / total_conf,
                domain_relevance=(
                    a.semantic.domain_relevance * a.semantic.confidence
                    + b.semantic.domain_relevance * b.semantic.confidence
                )
                / total_conf,
                confidence=max(a.semantic.confidence, b.semantic.confidence),
                measurement_method="tensor_add",
            )
        else:
            semantic = SemanticDimension()

        # Economic: sum
        economic = EconomicDimension(
            gas_cost_usd=a.economic.gas_cost_usd + b.economic.gas_cost_usd,
            opportunity_cost_usd=a.economic.opportunity_cost_usd + b.economic.opportunity_cost_usd,
            infrastructure_cost_usd=a.economic.infrastructure_cost_usd
            + b.economic.infrastructure_cost_usd,
            impact_value=a.economic.impact_value + b.economic.impact_value,
            impact_tier=max(
                a.economic.impact_tier,
                b.economic.impact_tier,
                key=lambda t: list(ImpactTier).index(t),
            ),
            realized_revenue_usd=a.economic.realized_revenue_usd + b.economic.realized_revenue_usd,
            value_confidence=max(a.economic.value_confidence, b.economic.value_confidence),
            cost_confidence=min(a.economic.cost_confidence, b.economic.cost_confidence),
        )

        # Ethical: worst risk dominates
        ethical = EthicalDimension(
            security_risk=max(a.ethical.security_risk, b.ethical.security_risk),
            privacy_risk=max(a.ethical.privacy_risk, b.ethical.privacy_risk),
            bias_risk=max(a.ethical.bias_risk, b.ethical.bias_risk),
            reliability_risk=max(a.ethical.reliability_risk, b.ethical.reliability_risk),
            maintainability_improvement=a.ethical.maintainability_improvement
            + b.ethical.maintainability_improvement,
            accessibility_improvement=a.ethical.accessibility_improvement
            + b.ethical.accessibility_improvement,
            documentation_improvement=a.ethical.documentation_improvement
            + b.ethical.documentation_improvement,
            test_coverage_improvement=a.ethical.test_coverage_improvement
            + b.ethical.test_coverage_improvement,
            license_compliant=a.ethical.license_compliant and b.ethical.license_compliant,
            security_policy_compliant=a.ethical.security_policy_compliant
            and b.ethical.security_policy_compliant,
            style_guide_compliant=a.ethical.style_guide_compliant
            and b.ethical.style_guide_compliant,
        )

        return ValueTensor(
            physical=physical,
            semantic=semantic,
            economic=economic,
            ethical=ethical,
            exchange_rates=a.exchange_rates,
            invariants=a.invariants,
        )

    @staticmethod
    def scale(tensor: ValueTensor, factor: float) -> ValueTensor:
        """Scale a tensor by a constant factor."""
        return ValueTensor(
            physical=PhysicalDimension(
                input_tokens=int(tensor.physical.input_tokens * factor),
                output_tokens=int(tensor.physical.output_tokens * factor),
                wall_clock_ms=tensor.physical.wall_clock_ms * factor,
                compute_time_ms=tensor.physical.compute_time_ms * factor,
                queue_time_ms=tensor.physical.queue_time_ms * factor,
                peak_memory_bytes=int(tensor.physical.peak_memory_bytes * factor),
                context_window_used=int(tensor.physical.context_window_used * factor),
                model_id=tensor.physical.model_id,
                cost_multiplier=tensor.physical.cost_multiplier,
            ),
            semantic=SemanticDimension(
                compression_ratio=tensor.semantic.compression_ratio,
                entropy_estimate=tensor.semantic.entropy_estimate * factor,
                kolmogorov_proxy=tensor.semantic.kolmogorov_proxy * factor,
                input_alignment=tensor.semantic.input_alignment,
                domain_relevance=tensor.semantic.domain_relevance,
                confidence=tensor.semantic.confidence,
                measurement_method=tensor.semantic.measurement_method,
            ),
            economic=EconomicDimension(
                gas_cost_usd=tensor.economic.gas_cost_usd * factor,
                opportunity_cost_usd=tensor.economic.opportunity_cost_usd * factor,
                impact_value=tensor.economic.impact_value * factor,
                impact_tier=tensor.economic.impact_tier,
                value_confidence=tensor.economic.value_confidence,
                cost_confidence=tensor.economic.cost_confidence,
            ),
            ethical=tensor.ethical,  # Ethical dimension doesn't scale
            exchange_rates=tensor.exchange_rates,
            invariants=tensor.invariants,
        )

    @staticmethod
    def project(
        tensor: ValueTensor,
        target_dimension: str,
    ) -> tuple[float, float]:
        """
        Project tensor to a single dimension.

        Uses exchange rates to convert all dimensions to target.
        Returns (total_value, total_loss).
        """
        total = 0.0
        total_loss = 0.0

        for dim_name, dim_value in tensor.dimension_values():
            if dim_name.startswith(target_dimension.split(".")[0]):
                total += dim_value
            else:
                converted, loss = tensor.exchange_rates.convert(
                    dim_value, dim_name, target_dimension
                )
                total += converted
                total_loss += loss

        return (total, total_loss)
