"""
Grammar Insurance: Volatility Hedging for Language Stability

Phase 5 of Structural Economics (B-gent × G-gent Integration).

Core insight: Grammars are volatile assets. They can fail, change, or become obsolete.
Insurance mechanisms provide stability guarantees and fallback strategies.

Key concepts:
1. Grammar Volatility: Measure stability of grammar usage (parse failures, version changes)
2. Insurance Policies: Coverage for grammar failures with fallback strategies
3. Premium Pricing: Cost of insurance based on grammar risk profile
4. Claims Processing: Automatic fallback when insured grammar fails
5. Hedging Strategies: Portfolio diversification across grammar complexity levels

The Grammar Insurance Formula:
    Premium = BaseRate × VolatilityScore × CoverageFactor × (1 - ReserveDiscount)

Hedging strategies:
1. FALLBACK: Downgrade to simpler grammar on failure
2. REDUNDANT: Maintain multiple parsers for critical grammars
3. VERSIONED: Keep N versions of grammar, rollback on failure
4. ENSEMBLE: Use multiple grammars, vote on parse results
5. GRACEFUL: Partial parsing with best-effort recovery

Integration:
- Works with syntax_tax.py for complexity-based risk assessment
- Works with G-gent Tongue for grammar fallback synthesis
- Works with B-gent CentralBank for premium/claim accounting
- Works with W-gent for failure observation and alerting
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Any, Callable
from collections import deque

from .metered_functor import CentralBank
from .syntax_tax import ChomskyLevel, GrammarClassifier

if TYPE_CHECKING:
    pass


# =============================================================================
# Volatility Measurement
# =============================================================================


class VolatilityCategory(Enum):
    """
    Categories of grammar volatility.

    Based on standard deviation of failure rates over time.
    """

    STABLE = "stable"  # < 0.1 failure rate, < 10% variation
    LOW = "low"  # < 0.2 failure rate, < 20% variation
    MODERATE = "moderate"  # < 0.4 failure rate, < 40% variation
    HIGH = "high"  # < 0.6 failure rate, < 60% variation
    EXTREME = "extreme"  # >= 0.6 failure rate or >= 60% variation

    @property
    def risk_multiplier(self) -> float:
        """Risk multiplier for premium calculation."""
        return {
            VolatilityCategory.STABLE: 0.5,
            VolatilityCategory.LOW: 1.0,
            VolatilityCategory.MODERATE: 2.0,
            VolatilityCategory.HIGH: 4.0,
            VolatilityCategory.EXTREME: 10.0,
        }[self]

    @property
    def requires_hedge(self) -> bool:
        """Whether this volatility level requires hedging."""
        return self in (
            VolatilityCategory.HIGH,
            VolatilityCategory.EXTREME,
        )


@dataclass
class ParseEvent:
    """
    Record of a single parse attempt.

    Used to track grammar stability over time.
    """

    grammar_id: str
    timestamp: datetime
    success: bool
    input_hash: str  # Hash of input, not full input (privacy)
    duration_ms: float
    error_type: str | None = None  # Type of error if failed
    fallback_used: str | None = None  # Fallback grammar if used
    version: str = "1.0.0"

    @classmethod
    def success_event(
        cls,
        grammar_id: str,
        input_text: str,
        duration_ms: float,
        version: str = "1.0.0",
    ) -> "ParseEvent":
        """Create a successful parse event."""
        return cls(
            grammar_id=grammar_id,
            timestamp=datetime.now(),
            success=True,
            input_hash=hashlib.sha256(input_text.encode()).hexdigest()[:16],
            duration_ms=duration_ms,
            version=version,
        )

    @classmethod
    def failure_event(
        cls,
        grammar_id: str,
        input_text: str,
        duration_ms: float,
        error_type: str,
        version: str = "1.0.0",
        fallback_used: str | None = None,
    ) -> "ParseEvent":
        """Create a failed parse event."""
        return cls(
            grammar_id=grammar_id,
            timestamp=datetime.now(),
            success=False,
            input_hash=hashlib.sha256(input_text.encode()).hexdigest()[:16],
            duration_ms=duration_ms,
            error_type=error_type,
            version=version,
            fallback_used=fallback_used,
        )


@dataclass
class VolatilityWindow:
    """
    Sliding window for volatility calculation.

    Tracks parse events within a time window to calculate
    volatility metrics.
    """

    window_size: timedelta = field(default_factory=lambda: timedelta(hours=24))
    max_events: int = 10000
    events: deque[ParseEvent] = field(default_factory=deque)

    def add_event(self, event: ParseEvent) -> None:
        """Add an event to the window."""
        self.events.append(event)
        if len(self.events) > self.max_events:
            self.events.popleft()
        self._prune_old_events()

    def _prune_old_events(self) -> None:
        """Remove events outside the window."""
        cutoff = datetime.now() - self.window_size
        while self.events and self.events[0].timestamp < cutoff:
            self.events.popleft()

    @property
    def failure_rate(self) -> float:
        """Current failure rate in the window."""
        if not self.events:
            return 0.0
        failures = sum(1 for e in self.events if not e.success)
        return failures / len(self.events)

    @property
    def event_count(self) -> int:
        """Number of events in the window."""
        self._prune_old_events()
        return len(self.events)

    @property
    def avg_duration_ms(self) -> float:
        """Average parse duration in the window."""
        if not self.events:
            return 0.0
        return sum(e.duration_ms for e in self.events) / len(self.events)


@dataclass
class VolatilityMetrics:
    """
    Comprehensive volatility metrics for a grammar.

    Used for risk assessment and premium calculation.
    """

    grammar_id: str
    measurement_period: timedelta

    # Core metrics
    failure_rate: float  # 0.0-1.0
    failure_rate_stddev: float  # Standard deviation over time
    avg_latency_ms: float
    latency_variance: float

    # Error analysis
    unique_error_types: int
    most_common_error: str | None
    error_concentration: float  # How concentrated are errors (0=uniform, 1=single type)

    # Trend analysis
    trend: str  # "improving", "stable", "degrading"
    trend_slope: float  # Rate of change

    # Sample size
    event_count: int

    @property
    def volatility_score(self) -> float:
        """
        Combined volatility score (0.0-1.0).

        Higher = more volatile = higher risk.
        """
        # Weighted combination of factors
        base_volatility = self.failure_rate * 0.4
        stddev_factor = min(self.failure_rate_stddev * 2, 0.3)  # Cap at 0.3
        error_diversity = (
            self.unique_error_types / 10
        ) * 0.15  # More error types = more volatile
        trend_factor = 0.15 if self.trend == "degrading" else 0.0

        return min(
            base_volatility + stddev_factor + error_diversity + trend_factor, 1.0
        )

    @property
    def category(self) -> VolatilityCategory:
        """Categorize volatility level."""
        score = self.volatility_score
        if score < 0.1:
            return VolatilityCategory.STABLE
        elif score < 0.2:
            return VolatilityCategory.LOW
        elif score < 0.4:
            return VolatilityCategory.MODERATE
        elif score < 0.6:
            return VolatilityCategory.HIGH
        else:
            return VolatilityCategory.EXTREME


class VolatilityMonitor:
    """
    Monitors grammar volatility over time.

    Tracks parse events, calculates volatility metrics,
    and triggers alerts when thresholds are exceeded.
    """

    def __init__(
        self,
        window_size: timedelta = timedelta(hours=24),
        alert_threshold: float = 0.3,
    ):
        self.window_size = window_size
        self.alert_threshold = alert_threshold
        self.windows: dict[str, VolatilityWindow] = {}
        self.historical_rates: dict[str, list[tuple[datetime, float]]] = {}
        self.alerts: list[dict[str, Any]] = []

    def record_parse(self, event: ParseEvent) -> None:
        """Record a parse event."""
        grammar_id = event.grammar_id

        if grammar_id not in self.windows:
            self.windows[grammar_id] = VolatilityWindow(window_size=self.window_size)

        self.windows[grammar_id].add_event(event)

        # Record hourly failure rate for trend analysis
        if grammar_id not in self.historical_rates:
            self.historical_rates[grammar_id] = []

        # Sample rate every hour
        rates = self.historical_rates[grammar_id]
        if not rates or (datetime.now() - rates[-1][0]).seconds >= 3600:
            rates.append((datetime.now(), self.windows[grammar_id].failure_rate))
            # Keep only last 168 hours (1 week)
            if len(rates) > 168:
                rates.pop(0)

        # Check for alerts
        self._check_alerts(grammar_id)

    def _check_alerts(self, grammar_id: str) -> None:
        """Check if grammar needs an alert."""
        window = self.windows.get(grammar_id)
        if not window or window.event_count < 10:
            return

        if window.failure_rate >= self.alert_threshold:
            self.alerts.append(
                {
                    "grammar_id": grammar_id,
                    "timestamp": datetime.now(),
                    "failure_rate": window.failure_rate,
                    "event_count": window.event_count,
                    "severity": "high" if window.failure_rate >= 0.5 else "medium",
                }
            )

    def get_metrics(self, grammar_id: str) -> VolatilityMetrics | None:
        """Get volatility metrics for a grammar."""
        window = self.windows.get(grammar_id)
        if not window or window.event_count == 0:
            return None

        # Calculate failure rate standard deviation from historical
        rates = self.historical_rates.get(grammar_id, [])
        if len(rates) >= 2:
            rate_values = [r[1] for r in rates]
            mean_rate = sum(rate_values) / len(rate_values)
            variance = sum((r - mean_rate) ** 2 for r in rate_values) / len(rate_values)
            stddev = variance**0.5
        else:
            stddev = 0.0

        # Analyze errors
        errors = [e.error_type for e in window.events if e.error_type]
        unique_errors = len(set(errors))
        most_common = max(set(errors), key=errors.count) if errors else None
        error_concentration = errors.count(most_common) / len(errors) if errors else 0.0

        # Calculate latency variance
        durations = [e.duration_ms for e in window.events]
        avg_duration = sum(durations) / len(durations)
        latency_variance = sum((d - avg_duration) ** 2 for d in durations) / len(
            durations
        )

        # Determine trend
        trend, slope = self._calculate_trend(grammar_id)

        return VolatilityMetrics(
            grammar_id=grammar_id,
            measurement_period=self.window_size,
            failure_rate=window.failure_rate,
            failure_rate_stddev=stddev,
            avg_latency_ms=avg_duration,
            latency_variance=latency_variance,
            unique_error_types=unique_errors,
            most_common_error=most_common,
            error_concentration=error_concentration,
            trend=trend,
            trend_slope=slope,
            event_count=window.event_count,
        )

    def _calculate_trend(self, grammar_id: str) -> tuple[str, float]:
        """Calculate failure rate trend."""
        rates = self.historical_rates.get(grammar_id, [])
        if len(rates) < 3:
            return "stable", 0.0

        # Simple linear regression
        n = len(rates)
        x_vals = list(range(n))
        y_vals = [r[1] for r in rates]

        x_mean = sum(x_vals) / n
        y_mean = sum(y_vals) / n

        numerator = sum((x - x_mean) * (y - y_mean) for x, y in zip(x_vals, y_vals))
        denominator = sum((x - x_mean) ** 2 for x in x_vals)

        slope = numerator / denominator if denominator > 0 else 0.0

        if slope > 0.01:
            return "degrading", slope
        elif slope < -0.01:
            return "improving", slope
        else:
            return "stable", slope

    def get_all_alerts(self, clear: bool = False) -> list[dict[str, Any]]:
        """Get all pending alerts."""
        alerts = list(self.alerts)
        if clear:
            self.alerts.clear()
        return alerts


# =============================================================================
# Insurance Policies and Hedging
# =============================================================================


class HedgeStrategy(Enum):
    """
    Hedging strategies for grammar volatility.

    Each strategy provides different risk/cost trade-offs.
    """

    FALLBACK = "fallback"  # Downgrade to simpler grammar on failure
    REDUNDANT = "redundant"  # Maintain multiple parsers
    VERSIONED = "versioned"  # Keep N versions, rollback on failure
    ENSEMBLE = "ensemble"  # Multiple grammars, vote on results
    GRACEFUL = "graceful"  # Partial parsing with recovery

    @property
    def cost_multiplier(self) -> float:
        """Cost multiplier for maintaining this hedge."""
        return {
            HedgeStrategy.FALLBACK: 1.2,  # 20% overhead for fallback maintenance
            HedgeStrategy.REDUNDANT: 2.0,  # Double cost for redundancy
            HedgeStrategy.VERSIONED: 1.5,  # 50% for version management
            HedgeStrategy.ENSEMBLE: 3.0,  # Triple for ensemble
            HedgeStrategy.GRACEFUL: 1.1,  # 10% for graceful degradation
        }[self]

    @property
    def coverage_factor(self) -> float:
        """How much risk this strategy covers."""
        return {
            HedgeStrategy.FALLBACK: 0.7,  # Covers 70% of failures
            HedgeStrategy.REDUNDANT: 0.9,  # Covers 90% of failures
            HedgeStrategy.VERSIONED: 0.8,  # Covers 80% of failures
            HedgeStrategy.ENSEMBLE: 0.95,  # Covers 95% of failures
            HedgeStrategy.GRACEFUL: 0.5,  # Covers 50% (partial recovery)
        }[self]


@dataclass
class GrammarHedge:
    """
    A hedge position for a grammar.

    Defines how to handle failures for a specific grammar.
    """

    grammar_id: str
    strategy: HedgeStrategy

    # Fallback configuration
    fallback_grammar_ids: list[str] = field(default_factory=list)
    fallback_level: ChomskyLevel = ChomskyLevel.REGULAR  # Simplest fallback

    # Version configuration
    versions_to_keep: int = 3
    current_version: str = "1.0.0"

    # Ensemble configuration
    ensemble_grammar_ids: list[str] = field(default_factory=list)
    vote_threshold: float = 0.5  # Majority vote

    # Graceful degradation
    min_recovery_tokens: int = 10  # Minimum tokens to attempt recovery
    max_recovery_attempts: int = 3

    @property
    def is_configured(self) -> bool:
        """Whether this hedge is properly configured."""
        if self.strategy == HedgeStrategy.FALLBACK:
            return len(self.fallback_grammar_ids) > 0
        elif self.strategy == HedgeStrategy.REDUNDANT:
            return len(self.fallback_grammar_ids) >= 2
        elif self.strategy == HedgeStrategy.VERSIONED:
            return self.versions_to_keep >= 2
        elif self.strategy == HedgeStrategy.ENSEMBLE:
            return len(self.ensemble_grammar_ids) >= 3
        else:  # GRACEFUL
            return True


@dataclass
class InsurancePolicy:
    """
    An insurance policy for a grammar.

    Specifies coverage, premium, and claim conditions.
    """

    policy_id: str
    grammar_id: str
    holder_id: str  # Agent who holds the policy

    # Coverage
    hedge: GrammarHedge
    coverage_limit_tokens: int  # Max tokens covered per claim
    deductible_tokens: int = 0  # Tokens holder pays first

    # Premium
    premium_tokens_per_day: int  # Daily premium cost
    premium_paid_through: datetime = field(default_factory=datetime.now)

    # Policy terms
    created_at: datetime = field(default_factory=datetime.now)
    expires_at: datetime | None = None
    auto_renew: bool = True

    # Status
    active: bool = True
    claims_count: int = 0
    total_claimed_tokens: int = 0

    @property
    def is_valid(self) -> bool:
        """Whether the policy is valid and active."""
        if not self.active:
            return False
        if self.expires_at and datetime.now() > self.expires_at:
            return False
        if datetime.now() > self.premium_paid_through:
            return False
        return True

    @property
    def remaining_coverage(self) -> int:
        """Remaining coverage for this period."""
        return max(0, self.coverage_limit_tokens - self.total_claimed_tokens)


@dataclass
class InsuranceClaim:
    """
    A claim against an insurance policy.

    Filed when a grammar failure occurs and coverage is invoked.
    """

    claim_id: str
    policy_id: str
    grammar_id: str

    # Failure details
    failure_timestamp: datetime
    error_type: str
    input_hash: str

    # Resolution
    fallback_used: str | None = None
    tokens_recovered: int = 0
    tokens_claimed: int = 0

    # Status
    status: str = "pending"  # pending, approved, denied, paid
    resolution_timestamp: datetime | None = None
    denial_reason: str | None = None

    @property
    def is_resolved(self) -> bool:
        """Whether the claim has been resolved."""
        return self.status in ("approved", "denied", "paid")


# =============================================================================
# Premium Calculator
# =============================================================================


@dataclass
class PremiumQuote:
    """
    A quote for insurance premium.

    Shows breakdown of how premium is calculated.
    """

    grammar_id: str
    holder_id: str
    strategy: HedgeStrategy
    coverage_limit_tokens: int

    # Base calculation
    base_rate_tokens: int
    volatility_multiplier: float
    complexity_multiplier: float
    strategy_multiplier: float

    # Adjustments
    reserve_discount: float  # Discount for maintaining reserve
    claims_history_adjustment: float  # +/- based on claims history
    volume_discount: float  # Discount for high coverage

    # Final premium
    daily_premium_tokens: int
    monthly_premium_tokens: int

    @property
    def annual_premium_tokens(self) -> int:
        """Annual premium estimate."""
        return self.daily_premium_tokens * 365

    @property
    def effective_rate(self) -> float:
        """Effective premium rate as percentage of coverage."""
        if self.coverage_limit_tokens == 0:
            return 0.0
        return (self.annual_premium_tokens / self.coverage_limit_tokens) * 100


class PremiumCalculator:
    """
    Calculates insurance premiums based on risk factors.

    Uses volatility, complexity, claims history, and hedge strategy
    to determine fair premium pricing.
    """

    # Base rates per 1000 tokens of coverage (per day)
    BASE_RATES = {
        ChomskyLevel.REGULAR: 0.1,  # 0.01% per day
        ChomskyLevel.CONTEXT_FREE: 0.3,  # 0.03% per day
        ChomskyLevel.CONTEXT_SENSITIVE: 0.8,  # 0.08% per day
        ChomskyLevel.TURING_COMPLETE: 2.0,  # 0.2% per day
    }

    def __init__(
        self,
        volatility_monitor: VolatilityMonitor,
        grammar_classifier: GrammarClassifier,
    ):
        self.volatility_monitor = volatility_monitor
        self.classifier = grammar_classifier
        self.claims_history: dict[str, list[InsuranceClaim]] = {}

    def quote(
        self,
        grammar_id: str,
        grammar_spec: str,
        holder_id: str,
        strategy: HedgeStrategy,
        coverage_limit_tokens: int,
        reserve_tokens: int = 0,
    ) -> PremiumQuote:
        """
        Generate a premium quote for grammar insurance.

        Args:
            grammar_id: Unique identifier for the grammar
            grammar_spec: Grammar specification for classification
            holder_id: Agent requesting insurance
            strategy: Hedging strategy to use
            coverage_limit_tokens: Maximum tokens covered per period
            reserve_tokens: Tokens holder has in reserve (for discount)

        Returns:
            PremiumQuote with full breakdown
        """
        # Classify grammar complexity
        analysis = self.classifier.classify(grammar_spec)
        complexity_level = analysis.level

        # Get volatility metrics
        volatility_metrics = self.volatility_monitor.get_metrics(grammar_id)
        volatility_multiplier = (
            volatility_metrics.category.risk_multiplier
            if volatility_metrics
            else 1.0  # Default to low risk for new grammars
        )

        # Calculate base rate
        base_rate = self.BASE_RATES.get(complexity_level, 1.0)
        base_rate_tokens = int(base_rate * coverage_limit_tokens / 1000)

        # Complexity multiplier (higher complexity = higher risk)
        complexity_multiplier = {
            ChomskyLevel.REGULAR: 1.0,
            ChomskyLevel.CONTEXT_FREE: 1.5,
            ChomskyLevel.CONTEXT_SENSITIVE: 3.0,
            ChomskyLevel.TURING_COMPLETE: 5.0,
        }.get(complexity_level, 2.0)

        # Strategy multiplier (more coverage = higher cost)
        strategy_multiplier = strategy.cost_multiplier

        # Reserve discount (up to 20% discount for 10x coverage in reserve)
        reserve_ratio = reserve_tokens / max(coverage_limit_tokens, 1)
        reserve_discount = min(reserve_ratio / 10, 0.2)  # Max 20%

        # Claims history adjustment
        claims = self.claims_history.get(holder_id, [])
        recent_claims = [
            c for c in claims if (datetime.now() - c.failure_timestamp).days < 365
        ]
        claims_adjustment = len(recent_claims) * 0.1  # 10% increase per claim

        # Volume discount (up to 15% for high coverage)
        if coverage_limit_tokens >= 1_000_000:
            volume_discount = 0.15
        elif coverage_limit_tokens >= 100_000:
            volume_discount = 0.10
        elif coverage_limit_tokens >= 10_000:
            volume_discount = 0.05
        else:
            volume_discount = 0.0

        # Calculate final premium
        raw_premium = (
            base_rate_tokens
            * volatility_multiplier
            * complexity_multiplier
            * strategy_multiplier
        )

        adjusted_premium = raw_premium * (
            1.0 - reserve_discount + claims_adjustment - volume_discount
        )

        daily_premium = max(1, int(adjusted_premium))
        monthly_premium = daily_premium * 30

        return PremiumQuote(
            grammar_id=grammar_id,
            holder_id=holder_id,
            strategy=strategy,
            coverage_limit_tokens=coverage_limit_tokens,
            base_rate_tokens=base_rate_tokens,
            volatility_multiplier=volatility_multiplier,
            complexity_multiplier=complexity_multiplier,
            strategy_multiplier=strategy_multiplier,
            reserve_discount=reserve_discount,
            claims_history_adjustment=claims_adjustment,
            volume_discount=volume_discount,
            daily_premium_tokens=daily_premium,
            monthly_premium_tokens=monthly_premium,
        )

    def record_claim(self, holder_id: str, claim: InsuranceClaim) -> None:
        """Record a claim for history tracking."""
        if holder_id not in self.claims_history:
            self.claims_history[holder_id] = []
        self.claims_history[holder_id].append(claim)


# =============================================================================
# Grammar Insurance Manager
# =============================================================================


@dataclass
class ClaimResult:
    """Result of processing an insurance claim."""

    claim: InsuranceClaim
    fallback_grammar_id: str | None
    tokens_paid: int
    success: bool
    message: str


class GrammarInsurance:
    """
    Manages grammar insurance policies and claims.

    Provides:
    1. Policy creation and management
    2. Premium collection
    3. Claims processing
    4. Fallback invocation
    5. Risk portfolio analysis
    """

    def __init__(
        self,
        central_bank: CentralBank | None = None,
        volatility_monitor: VolatilityMonitor | None = None,
    ):
        self.bank = central_bank
        self.volatility_monitor = volatility_monitor or VolatilityMonitor()
        self.classifier = GrammarClassifier()
        self.premium_calculator = PremiumCalculator(
            self.volatility_monitor,
            self.classifier,
        )

        # Policy storage
        self.policies: dict[str, InsurancePolicy] = {}
        self.claims: dict[str, InsuranceClaim] = {}
        self.hedges: dict[str, GrammarHedge] = {}

        # Counters
        self._policy_counter = 0
        self._claim_counter = 0

    def _generate_policy_id(self) -> str:
        """Generate unique policy ID."""
        self._policy_counter += 1
        return f"POL-{self._policy_counter:06d}"

    def _generate_claim_id(self) -> str:
        """Generate unique claim ID."""
        self._claim_counter += 1
        return f"CLM-{self._claim_counter:06d}"

    def create_hedge(
        self,
        grammar_id: str,
        strategy: HedgeStrategy,
        fallback_grammar_ids: list[str] | None = None,
        ensemble_grammar_ids: list[str] | None = None,
        versions_to_keep: int = 3,
    ) -> GrammarHedge:
        """
        Create a hedge configuration for a grammar.

        Args:
            grammar_id: Grammar to hedge
            strategy: Hedging strategy
            fallback_grammar_ids: Grammars to fall back to
            ensemble_grammar_ids: Grammars for ensemble voting
            versions_to_keep: Number of versions for versioned strategy

        Returns:
            Configured GrammarHedge
        """
        hedge = GrammarHedge(
            grammar_id=grammar_id,
            strategy=strategy,
            fallback_grammar_ids=fallback_grammar_ids or [],
            ensemble_grammar_ids=ensemble_grammar_ids or [],
            versions_to_keep=versions_to_keep,
        )

        self.hedges[grammar_id] = hedge
        return hedge

    def quote_policy(
        self,
        grammar_id: str,
        grammar_spec: str,
        holder_id: str,
        strategy: HedgeStrategy,
        coverage_limit_tokens: int,
        reserve_tokens: int = 0,
    ) -> PremiumQuote:
        """Get a quote for a new policy."""
        return self.premium_calculator.quote(
            grammar_id=grammar_id,
            grammar_spec=grammar_spec,
            holder_id=holder_id,
            strategy=strategy,
            coverage_limit_tokens=coverage_limit_tokens,
            reserve_tokens=reserve_tokens,
        )

    def create_policy(
        self,
        grammar_id: str,
        grammar_spec: str,
        holder_id: str,
        strategy: HedgeStrategy,
        coverage_limit_tokens: int,
        deductible_tokens: int = 0,
        duration_days: int = 30,
        auto_renew: bool = True,
    ) -> InsurancePolicy:
        """
        Create a new insurance policy.

        Args:
            grammar_id: Grammar to insure
            grammar_spec: Grammar specification
            holder_id: Agent taking out policy
            strategy: Hedging strategy
            coverage_limit_tokens: Maximum coverage
            deductible_tokens: Amount holder pays first
            duration_days: Policy duration
            auto_renew: Whether to auto-renew

        Returns:
            New InsurancePolicy
        """
        # Create or retrieve hedge
        if grammar_id not in self.hedges:
            self.create_hedge(grammar_id, strategy)
        hedge = self.hedges[grammar_id]

        # Get premium quote
        quote = self.quote_policy(
            grammar_id=grammar_id,
            grammar_spec=grammar_spec,
            holder_id=holder_id,
            strategy=strategy,
            coverage_limit_tokens=coverage_limit_tokens,
        )

        # Create policy
        policy = InsurancePolicy(
            policy_id=self._generate_policy_id(),
            grammar_id=grammar_id,
            holder_id=holder_id,
            hedge=hedge,
            coverage_limit_tokens=coverage_limit_tokens,
            deductible_tokens=deductible_tokens,
            premium_tokens_per_day=quote.daily_premium_tokens,
            premium_paid_through=datetime.now() + timedelta(days=duration_days),
            expires_at=(
                datetime.now() + timedelta(days=duration_days)
                if not auto_renew
                else None
            ),
            auto_renew=auto_renew,
        )

        self.policies[policy.policy_id] = policy
        return policy

    def file_claim(
        self,
        policy_id: str,
        error_type: str,
        input_hash: str,
    ) -> InsuranceClaim | None:
        """
        File a claim against a policy.

        Args:
            policy_id: Policy to claim against
            error_type: Type of parse failure
            input_hash: Hash of failed input

        Returns:
            InsuranceClaim if policy is valid, None otherwise
        """
        policy = self.policies.get(policy_id)
        if not policy or not policy.is_valid:
            return None

        claim = InsuranceClaim(
            claim_id=self._generate_claim_id(),
            policy_id=policy_id,
            grammar_id=policy.grammar_id,
            failure_timestamp=datetime.now(),
            error_type=error_type,
            input_hash=input_hash,
        )

        self.claims[claim.claim_id] = claim
        return claim

    def process_claim(
        self,
        claim_id: str,
        fallback_parser: Callable[[str, str], tuple[bool, int]] | None = None,
    ) -> ClaimResult:
        """
        Process a pending claim.

        Args:
            claim_id: Claim to process
            fallback_parser: Function to parse with fallback grammar
                            (grammar_id, input) -> (success, tokens_used)

        Returns:
            ClaimResult with outcome
        """
        claim = self.claims.get(claim_id)
        if not claim:
            return ClaimResult(
                claim=InsuranceClaim(
                    claim_id=claim_id,
                    policy_id="",
                    grammar_id="",
                    failure_timestamp=datetime.now(),
                    error_type="",
                    input_hash="",
                    status="denied",
                    denial_reason="Claim not found",
                ),
                fallback_grammar_id=None,
                tokens_paid=0,
                success=False,
                message="Claim not found",
            )

        policy = self.policies.get(claim.policy_id)
        if not policy:
            claim.status = "denied"
            claim.denial_reason = "Policy not found"
            claim.resolution_timestamp = datetime.now()
            return ClaimResult(
                claim=claim,
                fallback_grammar_id=None,
                tokens_paid=0,
                success=False,
                message="Policy not found",
            )

        if not policy.is_valid:
            claim.status = "denied"
            claim.denial_reason = "Policy not valid"
            claim.resolution_timestamp = datetime.now()
            return ClaimResult(
                claim=claim,
                fallback_grammar_id=None,
                tokens_paid=0,
                success=False,
                message="Policy expired or inactive",
            )

        # Try fallback based on hedge strategy
        hedge = policy.hedge
        fallback_used = None
        tokens_recovered = 0

        if fallback_parser and hedge.fallback_grammar_ids:
            for fallback_id in hedge.fallback_grammar_ids:
                success, tokens = fallback_parser(fallback_id, claim.input_hash)
                if success:
                    fallback_used = fallback_id
                    tokens_recovered = tokens
                    break

        # Calculate payout
        if fallback_used:
            # Successful fallback - pay for tokens saved
            tokens_to_pay = min(
                tokens_recovered,
                policy.remaining_coverage,
            )
            tokens_to_pay = max(0, tokens_to_pay - policy.deductible_tokens)
        else:
            # No successful fallback - pay coverage limit
            tokens_to_pay = min(
                policy.coverage_limit_tokens,
                policy.remaining_coverage,
            )
            tokens_to_pay = max(0, tokens_to_pay - policy.deductible_tokens)

        # Update claim
        claim.fallback_used = fallback_used
        claim.tokens_recovered = tokens_recovered
        claim.tokens_claimed = tokens_to_pay
        claim.status = "paid"
        claim.resolution_timestamp = datetime.now()

        # Update policy
        policy.claims_count += 1
        policy.total_claimed_tokens += tokens_to_pay

        # Record for premium adjustment
        self.premium_calculator.record_claim(policy.holder_id, claim)

        return ClaimResult(
            claim=claim,
            fallback_grammar_id=fallback_used,
            tokens_paid=tokens_to_pay,
            success=True,
            message=(
                f"Claim paid: {tokens_to_pay} tokens"
                + (f" (fallback: {fallback_used})" if fallback_used else "")
            ),
        )

    def get_policy(self, policy_id: str) -> InsurancePolicy | None:
        """Get a policy by ID."""
        return self.policies.get(policy_id)

    def get_policies_for_grammar(self, grammar_id: str) -> list[InsurancePolicy]:
        """Get all policies for a grammar."""
        return [p for p in self.policies.values() if p.grammar_id == grammar_id]

    def get_policies_for_holder(self, holder_id: str) -> list[InsurancePolicy]:
        """Get all policies for a holder."""
        return [p for p in self.policies.values() if p.holder_id == holder_id]

    def renew_policy(self, policy_id: str, days: int = 30) -> bool:
        """Renew a policy for additional days."""
        policy = self.policies.get(policy_id)
        if not policy:
            return False

        policy.premium_paid_through = max(
            policy.premium_paid_through,
            datetime.now(),
        ) + timedelta(days=days)

        if policy.expires_at:
            policy.expires_at = policy.premium_paid_through

        # Reset claims counter for new period
        policy.total_claimed_tokens = 0

        return True

    def cancel_policy(self, policy_id: str) -> bool:
        """Cancel a policy."""
        policy = self.policies.get(policy_id)
        if not policy:
            return False

        policy.active = False
        return True


# =============================================================================
# Portfolio Analysis
# =============================================================================


@dataclass
class PortfolioRisk:
    """
    Risk analysis for a portfolio of insured grammars.

    Helps B-gent understand overall exposure and diversification.
    """

    total_policies: int
    total_coverage_tokens: int
    total_daily_premiums: int

    # Risk distribution
    regular_coverage: int
    context_free_coverage: int
    context_sensitive_coverage: int
    turing_coverage: int

    # Diversification score (0-1, higher = more diversified)
    diversification_score: float

    # Concentration risk (highest single grammar % of total)
    concentration_risk: float

    # Expected claims per day
    expected_daily_claims: float
    expected_daily_payout: int

    # Loss ratio (claims / premiums)
    loss_ratio: float

    @property
    def is_profitable(self) -> bool:
        """Whether portfolio is expected to be profitable."""
        return self.loss_ratio < 1.0

    @property
    def reserve_recommendation(self) -> int:
        """Recommended reserve to hold."""
        # 3x expected daily payout as reserve
        return self.expected_daily_payout * 3


class PortfolioAnalyzer:
    """
    Analyzes risk across a portfolio of grammar insurance policies.

    Helps B-gent:
    1. Understand total exposure
    2. Ensure adequate reserves
    3. Identify concentration risks
    4. Optimize premium pricing
    """

    def __init__(
        self,
        insurance: GrammarInsurance,
        classifier: GrammarClassifier | None = None,
    ):
        self.insurance = insurance
        self.classifier = classifier or GrammarClassifier()

    def analyze(
        self,
        grammar_specs: dict[str, str] | None = None,
    ) -> PortfolioRisk:
        """
        Analyze the current portfolio.

        Args:
            grammar_specs: Map of grammar_id -> spec for classification

        Returns:
            PortfolioRisk analysis
        """
        policies = list(self.insurance.policies.values())
        active_policies = [p for p in policies if p.is_valid]

        if not active_policies:
            return PortfolioRisk(
                total_policies=0,
                total_coverage_tokens=0,
                total_daily_premiums=0,
                regular_coverage=0,
                context_free_coverage=0,
                context_sensitive_coverage=0,
                turing_coverage=0,
                diversification_score=0.0,
                concentration_risk=0.0,
                expected_daily_claims=0.0,
                expected_daily_payout=0,
                loss_ratio=0.0,
            )

        # Calculate totals
        total_coverage = sum(p.coverage_limit_tokens for p in active_policies)
        total_premiums = sum(p.premium_tokens_per_day for p in active_policies)

        # Classify coverage by complexity
        coverage_by_level: dict[ChomskyLevel, int] = {
            ChomskyLevel.REGULAR: 0,
            ChomskyLevel.CONTEXT_FREE: 0,
            ChomskyLevel.CONTEXT_SENSITIVE: 0,
            ChomskyLevel.TURING_COMPLETE: 0,
        }

        grammar_coverage: dict[str, int] = {}

        for policy in active_policies:
            grammar_id = policy.grammar_id
            coverage = policy.coverage_limit_tokens

            # Track per-grammar coverage
            grammar_coverage[grammar_id] = (
                grammar_coverage.get(grammar_id, 0) + coverage
            )

            # Classify if spec available
            if grammar_specs and grammar_id in grammar_specs:
                analysis = self.classifier.classify(grammar_specs[grammar_id])
                coverage_by_level[analysis.level] += coverage
            else:
                # Default to context-free if unknown
                coverage_by_level[ChomskyLevel.CONTEXT_FREE] += coverage

        # Calculate diversification
        if total_coverage > 0:
            # Herfindahl-Hirschman Index (lower = more diversified)
            hhi = sum((c / total_coverage) ** 2 for c in grammar_coverage.values())
            diversification_score = 1.0 - hhi

            # Concentration risk
            max_coverage = max(grammar_coverage.values())
            concentration_risk = max_coverage / total_coverage
        else:
            diversification_score = 0.0
            concentration_risk = 0.0

        # Estimate expected claims
        # Base rate: 1% of policies claim per day
        expected_claims = len(active_policies) * 0.01

        # Adjust for volatility
        for policy in active_policies:
            metrics = self.insurance.volatility_monitor.get_metrics(policy.grammar_id)
            if metrics:
                expected_claims += metrics.failure_rate * 0.1

        # Estimate payout (50% of coverage limit on average)
        avg_coverage = total_coverage / len(active_policies) if active_policies else 0
        expected_payout = int(expected_claims * avg_coverage * 0.5)

        # Loss ratio
        loss_ratio = expected_payout / total_premiums if total_premiums > 0 else 0.0

        return PortfolioRisk(
            total_policies=len(active_policies),
            total_coverage_tokens=total_coverage,
            total_daily_premiums=total_premiums,
            regular_coverage=coverage_by_level[ChomskyLevel.REGULAR],
            context_free_coverage=coverage_by_level[ChomskyLevel.CONTEXT_FREE],
            context_sensitive_coverage=coverage_by_level[
                ChomskyLevel.CONTEXT_SENSITIVE
            ],
            turing_coverage=coverage_by_level[ChomskyLevel.TURING_COMPLETE],
            diversification_score=diversification_score,
            concentration_risk=concentration_risk,
            expected_daily_claims=expected_claims,
            expected_daily_payout=expected_payout,
            loss_ratio=loss_ratio,
        )


# =============================================================================
# Convenience Functions
# =============================================================================


def create_fallback_hedge(
    grammar_id: str,
    fallback_ids: list[str],
) -> GrammarHedge:
    """
    Create a simple fallback hedge.

    Falls back to simpler grammars on failure.
    """
    return GrammarHedge(
        grammar_id=grammar_id,
        strategy=HedgeStrategy.FALLBACK,
        fallback_grammar_ids=fallback_ids,
    )


def create_versioned_hedge(
    grammar_id: str,
    versions_to_keep: int = 3,
) -> GrammarHedge:
    """
    Create a versioned hedge.

    Keeps N versions and rolls back on failure.
    """
    return GrammarHedge(
        grammar_id=grammar_id,
        strategy=HedgeStrategy.VERSIONED,
        versions_to_keep=versions_to_keep,
    )


def create_ensemble_hedge(
    grammar_id: str,
    ensemble_ids: list[str],
    vote_threshold: float = 0.5,
) -> GrammarHedge:
    """
    Create an ensemble hedge.

    Uses multiple grammars and votes on results.
    """
    return GrammarHedge(
        grammar_id=grammar_id,
        strategy=HedgeStrategy.ENSEMBLE,
        ensemble_grammar_ids=ensemble_ids,
        vote_threshold=vote_threshold,
    )


def estimate_annual_premium(
    grammar_spec: str,
    coverage_tokens: int,
    strategy: HedgeStrategy = HedgeStrategy.FALLBACK,
) -> int:
    """
    Quick estimate of annual premium for a grammar.

    Useful for budgeting before creating a policy.
    """
    classifier = GrammarClassifier()
    analysis = classifier.classify(grammar_spec)

    # Base rates (simplified)
    base_rates = {
        ChomskyLevel.REGULAR: 0.001,
        ChomskyLevel.CONTEXT_FREE: 0.003,
        ChomskyLevel.CONTEXT_SENSITIVE: 0.01,
        ChomskyLevel.TURING_COMPLETE: 0.03,
    }

    base_rate = base_rates.get(analysis.level, 0.005)
    daily_premium = coverage_tokens * base_rate * strategy.cost_multiplier

    return int(daily_premium * 365)


def calculate_hedge_cost(
    strategy: HedgeStrategy,
    base_operation_cost: int,
) -> int:
    """
    Calculate the additional cost of maintaining a hedge.

    Returns additional tokens per operation for the hedge overhead.
    """
    return int(base_operation_cost * (strategy.cost_multiplier - 1.0))
