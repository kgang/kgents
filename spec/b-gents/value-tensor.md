# The Value Tensor: Multi-Dimensional Resource Ontology

> *Cost is a point. Value is a manifold.*

---

## Motivation

Traditional metering systems track a single dimension: tokens consumed. But value flows through multiple dimensions simultaneously:

- **Physical**: tokens, time, memory, energy
- **Semantic**: complexity, structure, meaning
- **Economic**: cost, revenue, profit, debt
- **Ethical**: risk, virtue, externalities

The **Value Tensor** formalizes this multi-dimensional ontology, enabling:
1. Translation between incommensurable currencies
2. Conservation law enforcement across dimensions
3. Anti-delusion protection via cross-dimensional consistency checks
4. Flexible heuristics when direct measurement is intractable

---

## The Tensor Structure

### Definition

```python
@dataclass
class ValueTensor:
    """
    Multi-dimensional representation of resource/value state.

    A tensor in the mathematical sense: a multi-linear map that
    transforms covariantly under change of basis (currency conversion).
    """

    # Dimension 1: Physical Resources
    physical: PhysicalDimension

    # Dimension 2: Semantic Quality
    semantic: SemanticDimension

    # Dimension 3: Economic Value
    economic: EconomicDimension

    # Dimension 4: Ethical Standing
    ethical: EthicalDimension

    # The exchange rate matrix
    exchange_rates: ExchangeMatrix

    # Conservation laws that must hold
    invariants: list[ConservationLaw]
```

---

## Dimension 1: Physical Resources

The measurable, objective costs of computation.

```python
@dataclass
class PhysicalDimension:
    """
    Physical resources consumed or produced.

    These are directly measurable and fungible within type.
    """

    # Token-based
    input_tokens: int
    output_tokens: int
    total_tokens: int

    # Time-based
    wall_clock_ms: float
    compute_time_ms: float
    queue_time_ms: float

    # Memory-based
    peak_memory_bytes: int
    context_window_used: int

    # Energy-based (if available)
    estimated_joules: float | None

    # Model-specific multipliers
    model_id: str
    cost_multiplier: float  # opus=15x, sonnet=3x, haiku=1x

    @property
    def normalized_tokens(self) -> float:
        """Tokens normalized by model cost."""
        return self.total_tokens * self.cost_multiplier
```

### Physical Conservation Laws

```python
class PhysicalConservation:
    """Laws that must hold in the physical dimension."""

    @staticmethod
    def token_accounting(before: PhysicalDimension, after: PhysicalDimension) -> bool:
        """Tokens in = tokens out + tokens consumed."""
        return after.total_tokens >= before.total_tokens  # Monotonic

    @staticmethod
    def time_ordering(events: list[PhysicalDimension]) -> bool:
        """Time flows forward."""
        return all(
            events[i].wall_clock_ms <= events[i+1].wall_clock_ms
            for i in range(len(events) - 1)
        )
```

---

## Dimension 2: Semantic Quality

The meaning and structure of outputs—harder to measure, requires heuristics.

```python
@dataclass
class SemanticDimension:
    """
    Semantic quality of agent output.

    Since true semantic content is undecidable, we use proxy metrics
    with explicit uncertainty bounds.
    """

    # Complexity metrics (Kolmogorov proxies)
    compression_ratio: float      # Lower = more structured
    entropy_estimate: float       # Shannon entropy of output
    kolmogorov_proxy: float       # Combined complexity estimate

    # Structural metrics
    ast_valid: bool | None        # For code: does it parse?
    type_valid: bool | None       # For code: does it type-check?
    schema_valid: bool | None     # For data: does it match schema?

    # Semantic coherence
    self_consistency: float       # Does output contradict itself?
    input_alignment: float        # Does output address input intent?
    domain_relevance: float       # Is output on-topic?

    # Uncertainty bounds
    confidence: float             # How confident are we in these metrics?
    measurement_method: str       # How were metrics obtained?

    @property
    def quality_score(self) -> float:
        """Aggregate quality score with uncertainty weighting."""
        base = (
            (1 - self.compression_ratio) * 0.3 +
            self.input_alignment * 0.4 +
            self.domain_relevance * 0.3
        )
        return base * self.confidence
```

### Semantic Heuristics

When direct measurement is impossible, use these ordered heuristics:

| Desired Metric | Heuristic | Reliability |
|----------------|-----------|-------------|
| Conceptual complexity | Compression ratio | Medium |
| Code correctness | AST + type check + tests | High |
| Writing quality | Word count (crude) | Low |
| Reasoning depth | Nested clause count | Medium |
| Novelty | Embedding distance from training | Medium |

```python
class SemanticHeuristics:
    """
    Heuristics for when direct measurement is intractable.

    Each heuristic has explicit reliability and conditions.
    """

    @staticmethod
    def word_count_heuristic(text: str) -> SemanticDimension:
        """
        Crude proxy: longer = more complex.

        Reliability: LOW
        Use when: No other information available
        Failure mode: Verbose noise scores high
        """
        words = len(text.split())
        return SemanticDimension(
            compression_ratio=0.5,  # Unknown
            entropy_estimate=words * 0.1,  # Rough
            kolmogorov_proxy=words / 100,
            confidence=0.2,  # Low confidence
            measurement_method="word_count_heuristic"
        )

    @staticmethod
    def compression_heuristic(text: str) -> SemanticDimension:
        """
        Better proxy: compression ratio reveals structure.

        Reliability: MEDIUM
        Use when: Text is substantial (>100 chars)
        Failure mode: Repetitive text compresses well but is low-value
        """
        import zlib
        original = len(text.encode())
        compressed = len(zlib.compress(text.encode()))
        ratio = compressed / original if original > 0 else 1.0

        return SemanticDimension(
            compression_ratio=ratio,
            entropy_estimate=ratio * 8,  # Bits per byte
            kolmogorov_proxy=1.0 - ratio,
            confidence=0.5,
            measurement_method="compression_heuristic"
        )

    @staticmethod
    def validation_heuristic(
        text: str,
        validators: list[Callable[[str], bool]]
    ) -> SemanticDimension:
        """
        Best proxy: actual validation (AST, types, tests).

        Reliability: HIGH
        Use when: Domain-specific validators available
        Failure mode: Validators may miss semantic errors
        """
        passed = sum(1 for v in validators if v(text))
        total = len(validators)
        pass_rate = passed / total if total > 0 else 0

        return SemanticDimension(
            compression_ratio=0.3,  # Assume structured if validating
            entropy_estimate=2.0,   # Low entropy if structured
            kolmogorov_proxy=pass_rate,
            ast_valid=True,         # At least one validator passed
            confidence=0.8,
            measurement_method="validation_heuristic"
        )
```

---

## Dimension 3: Economic Value

The business impact measured in currency.

```python
@dataclass
class EconomicDimension:
    """
    Economic value in monetary terms.

    Tracks both costs (Gas) and value created (Impact).
    """

    # Cost side (Gas)
    gas_cost_usd: float           # Direct API costs
    opportunity_cost_usd: float   # What else could we have done?
    infrastructure_cost_usd: float # Servers, storage, etc.

    # Value side (Impact)
    impact_value: float           # Dimensionless impact units
    impact_tier: str              # syntactic/functional/deployment/ethical
    realized_revenue_usd: float   # If we can measure it

    # Derived
    profit_usd: float             # Value - Cost
    roc: float                    # Return on Compute

    # Uncertainty
    value_confidence: float       # How confident in impact estimate?
    cost_confidence: float        # How confident in cost estimate?

    @property
    def net_present_value(self) -> float:
        """NPV accounting for uncertainty."""
        expected_value = self.impact_value * self.value_confidence
        expected_cost = self.gas_cost_usd * self.cost_confidence
        return expected_value - expected_cost
```

### Economic Conservation Laws

```python
class EconomicConservation:
    """Laws that must hold in the economic dimension."""

    @staticmethod
    def budget_constraint(
        initial_budget: float,
        transactions: list[EconomicDimension]
    ) -> bool:
        """Cannot spend more than allocated."""
        total_spent = sum(t.gas_cost_usd for t in transactions)
        return total_spent <= initial_budget

    @staticmethod
    def value_accounting(
        value_created: float,
        value_distributed: float
    ) -> bool:
        """Value created must equal value distributed."""
        return abs(value_created - value_distributed) < 0.01  # Epsilon
```

---

## Dimension 4: Ethical Standing

Externalities, risks, and virtue.

```python
@dataclass
class EthicalDimension:
    """
    Ethical qualities that affect value calculation.

    These are multipliers and adjustments, not direct values.
    """

    # Risk assessment
    security_risk: float          # 0 = safe, 1 = critical vulnerability
    privacy_risk: float           # 0 = no PII, 1 = data breach
    bias_risk: float              # 0 = fair, 1 = discriminatory
    reliability_risk: float       # 0 = robust, 1 = fragile

    # Virtue assessment
    maintainability_improvement: float   # Positive = better code
    accessibility_improvement: float     # Positive = more accessible
    documentation_improvement: float     # Positive = better docs
    test_coverage_improvement: float     # Positive = more tests

    # Policy compliance
    license_compliant: bool
    security_policy_compliant: bool
    style_guide_compliant: bool

    # Aggregate multipliers
    @property
    def sin_tax_multiplier(self) -> float:
        """Penalty for risks (< 1.0 reduces value)."""
        base = 1.0
        base *= (1.0 - self.security_risk * 0.67)   # Up to 3x penalty
        base *= (1.0 - self.privacy_risk * 0.75)    # Up to 4x penalty
        base *= (1.0 - self.bias_risk * 0.5)        # Up to 2x penalty
        return max(0.1, base)  # Floor at 10%

    @property
    def virtue_subsidy_multiplier(self) -> float:
        """Bonus for virtues (> 1.0 increases value)."""
        base = 1.0
        base += self.maintainability_improvement * 0.3
        base += self.accessibility_improvement * 0.6
        base += self.test_coverage_improvement * 0.5
        return min(3.0, base)  # Cap at 3x

    @property
    def net_ethical_multiplier(self) -> float:
        """Combined ethical adjustment."""
        return self.sin_tax_multiplier * self.virtue_subsidy_multiplier
```

---

## The Exchange Matrix

Translation between dimensions with explicit loss functions.

```python
@dataclass
class ExchangeMatrix:
    """
    Exchange rates between dimensions.

    Not all exchanges are lossless. The matrix tracks:
    - Rate: How much of B per unit of A
    - Loss: Information/value lost in translation
    - Confidence: How reliable is this rate
    """

    rates: dict[tuple[str, str], ExchangeRate]

    def get_rate(self, from_dim: str, to_dim: str) -> ExchangeRate:
        """Get exchange rate between dimensions."""
        return self.rates.get((from_dim, to_dim), ExchangeRate.UNDEFINED)

    def convert(
        self,
        value: float,
        from_dim: str,
        to_dim: str
    ) -> tuple[float, float]:
        """
        Convert value between dimensions.

        Returns: (converted_value, information_loss)
        """
        rate = self.get_rate(from_dim, to_dim)
        converted = value * rate.rate * (1 - rate.loss)
        loss = value * rate.loss
        return (converted, loss)


@dataclass
class ExchangeRate:
    """Single exchange rate with metadata."""

    rate: float              # Units of target per unit of source
    loss: float              # Fraction lost in translation (0-1)
    confidence: float        # How reliable is this rate (0-1)
    method: str              # How was this rate determined
    last_updated: datetime   # When was this rate calibrated

    UNDEFINED: ClassVar["ExchangeRate"]  # Sentinel for unknown rates


# Example rates
STANDARD_EXCHANGE_RATES = ExchangeMatrix({
    # Physical → Economic (direct, low loss)
    ("physical.tokens", "economic.gas_cost_usd"): ExchangeRate(
        rate=0.00001,  # $0.01 per 1000 tokens (varies by model)
        loss=0.0,
        confidence=0.99,
        method="api_pricing",
        last_updated=datetime.now()
    ),

    # Semantic → Economic (indirect, high loss)
    ("semantic.quality_score", "economic.impact_value"): ExchangeRate(
        rate=100.0,  # 1.0 quality → 100 impact units
        loss=0.3,    # 30% lost in translation
        confidence=0.5,
        method="heuristic_calibration",
        last_updated=datetime.now()
    ),

    # Physical → Semantic (very indirect)
    ("physical.tokens", "semantic.kolmogorov_proxy"): ExchangeRate(
        rate=0.001,  # Tokens weakly predict complexity
        loss=0.7,    # 70% information loss
        confidence=0.2,
        method="statistical_correlation",
        last_updated=datetime.now()
    ),

    # Ethical → Economic (policy-driven)
    ("ethical.net_multiplier", "economic.impact_value"): ExchangeRate(
        rate=1.0,    # Direct multiplier
        loss=0.0,
        confidence=0.9,
        method="policy_definition",
        last_updated=datetime.now()
    ),
})
```

---

## Conservation Laws

Invariants that must hold across the tensor.

```python
@dataclass
class ConservationLaw:
    """
    An invariant that must hold in the value tensor.

    Violations indicate bugs, fraud, or delusion.
    """

    name: str
    description: str
    check: Callable[[ValueTensor, ValueTensor], bool]
    severity: Literal["warning", "error", "critical"]


CONSERVATION_LAWS = [
    ConservationLaw(
        name="token_monotonicity",
        description="Total tokens consumed never decreases",
        check=lambda before, after: (
            after.physical.total_tokens >= before.physical.total_tokens
        ),
        severity="critical"
    ),

    ConservationLaw(
        name="time_arrow",
        description="Time flows forward",
        check=lambda before, after: (
            after.physical.wall_clock_ms >= before.physical.wall_clock_ms
        ),
        severity="critical"
    ),

    ConservationLaw(
        name="budget_constraint",
        description="Cannot create Gas from nothing",
        check=lambda before, after: (
            after.economic.gas_cost_usd <= before.economic.gas_cost_usd +
            AUTHORIZED_BUDGET_INCREASE
        ),
        severity="error"
    ),

    ConservationLaw(
        name="impact_justification",
        description="Impact must be justified by semantic quality",
        check=lambda before, after: (
            after.economic.impact_value <=
            after.semantic.quality_score * MAX_IMPACT_PER_QUALITY
        ),
        severity="warning"
    ),

    ConservationLaw(
        name="ethical_bounds",
        description="Ethical multiplier must be in valid range",
        check=lambda before, after: (
            0.1 <= after.ethical.net_ethical_multiplier <= 3.0
        ),
        severity="error"
    ),
]
```

---

## Anti-Delusion Protection

Cross-dimensional consistency checks prevent hallucinated value.

```python
class AntiDelusionChecker:
    """
    Detects inconsistencies that indicate delusion or fraud.

    If an agent claims high impact but physical/semantic dimensions
    don't support it, something is wrong.
    """

    def check_consistency(self, tensor: ValueTensor) -> list[Anomaly]:
        """Run all consistency checks."""
        anomalies = []

        # Check 1: High impact requires high quality
        if tensor.economic.impact_value > 500:
            if tensor.semantic.quality_score < 0.5:
                anomalies.append(Anomaly(
                    type="impact_quality_mismatch",
                    message="High impact claimed but quality score is low",
                    severity="warning",
                    dimensions=["economic", "semantic"]
                ))

        # Check 2: Validated code should have good compression
        if tensor.semantic.ast_valid and tensor.semantic.type_valid:
            if tensor.semantic.compression_ratio > 0.8:
                anomalies.append(Anomaly(
                    type="validation_compression_mismatch",
                    message="Code validates but has high entropy (suspicious)",
                    severity="info",
                    dimensions=["semantic"]
                ))

        # Check 3: Ethical multiplier consistency
        if tensor.ethical.security_risk > 0.5:
            if tensor.ethical.sin_tax_multiplier > 0.8:
                anomalies.append(Anomaly(
                    type="risk_tax_mismatch",
                    message="High security risk but low sin tax applied",
                    severity="error",
                    dimensions=["ethical"]
                ))

        # Check 4: Cost-value sanity
        if tensor.economic.roc > 10.0:
            anomalies.append(Anomaly(
                type="suspicious_roc",
                message="RoC > 10x is unusually high, verify impact",
                severity="warning",
                dimensions=["economic"]
            ))

        return anomalies

    def validate_transition(
        self,
        before: ValueTensor,
        after: ValueTensor
    ) -> list[Anomaly]:
        """Validate a state transition."""
        anomalies = []

        # Run conservation law checks
        for law in CONSERVATION_LAWS:
            if not law.check(before, after):
                anomalies.append(Anomaly(
                    type=f"conservation_violation:{law.name}",
                    message=law.description,
                    severity=law.severity,
                    dimensions=["all"]
                ))

        # Check for impossible improvements
        quality_delta = after.semantic.quality_score - before.semantic.quality_score
        token_delta = after.physical.total_tokens - before.physical.total_tokens

        if quality_delta > 0.5 and token_delta < 100:
            anomalies.append(Anomaly(
                type="free_lunch_detected",
                message="Large quality improvement with minimal tokens (suspicious)",
                severity="warning",
                dimensions=["physical", "semantic"]
            ))

        return anomalies
```

---

## Tensor Operations

Algebraic operations on value tensors.

```python
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
        return ValueTensor(
            physical=PhysicalDimension(
                total_tokens=a.physical.total_tokens + b.physical.total_tokens,
                # ... other fields summed
            ),
            semantic=SemanticDimension(
                quality_score=(
                    a.semantic.quality_score * a.semantic.confidence +
                    b.semantic.quality_score * b.semantic.confidence
                ) / (a.semantic.confidence + b.semantic.confidence),
                confidence=max(a.semantic.confidence, b.semantic.confidence),
                # ... other fields
            ),
            economic=EconomicDimension(
                gas_cost_usd=a.economic.gas_cost_usd + b.economic.gas_cost_usd,
                impact_value=a.economic.impact_value + b.economic.impact_value,
                # ... other fields
            ),
            ethical=EthicalDimension(
                security_risk=max(a.ethical.security_risk, b.ethical.security_risk),
                # Worst risk dominates
                # ... other fields
            ),
            exchange_rates=a.exchange_rates,  # Assume same rates
            invariants=a.invariants
        )

    @staticmethod
    def scale(tensor: ValueTensor, factor: float) -> ValueTensor:
        """Scale a tensor by a constant factor."""
        return ValueTensor(
            physical=PhysicalDimension(
                total_tokens=int(tensor.physical.total_tokens * factor),
                # ...
            ),
            # ... scale all dimensions
        )

    @staticmethod
    def project(
        tensor: ValueTensor,
        target_dimension: str
    ) -> float:
        """
        Project tensor to a single dimension.

        Uses exchange rates to convert all dimensions to target.
        Accumulates loss during conversion.
        """
        total = 0.0
        total_loss = 0.0

        for dim_name, dim_value in tensor.dimension_values():
            if dim_name == target_dimension:
                total += dim_value
            else:
                converted, loss = tensor.exchange_rates.convert(
                    dim_value, dim_name, target_dimension
                )
                total += converted
                total_loss += loss

        return total  # Could also return (total, total_loss)
```

---

## Integration with Agent Lifecycle

```python
class TensoredAgent(Agent[A, B]):
    """
    An agent that tracks its value tensor throughout execution.

    Every invoke() updates the tensor and validates invariants.
    """

    def __init__(self, inner: Agent[A, B], ledger: ValueLedger):
        self.inner = inner
        self.ledger = ledger
        self.tensor = ValueTensor.initial()

    async def invoke(self, input: A) -> B:
        # Snapshot before
        tensor_before = self.tensor.copy()

        # Track physical resources
        start_time = time.time()
        start_tokens = self.count_tokens(input)

        # Execute
        result = await self.inner.invoke(input)

        # Update physical dimension
        self.tensor.physical.total_tokens += self.count_tokens(result)
        self.tensor.physical.wall_clock_ms += (time.time() - start_time) * 1000

        # Update semantic dimension (via heuristics)
        self.tensor.semantic = SemanticHeuristics.compression_heuristic(
            str(result)
        )

        # Update economic dimension
        gas = Gas(tokens=self.tensor.physical.total_tokens, ...)
        impact = self.ledger.oracle.calculate_impact(result)
        self.tensor.economic.gas_cost_usd += gas.cost_usd
        self.tensor.economic.impact_value += impact.realized_value

        # Update ethical dimension
        self.tensor.ethical = self.assess_ethics(result)

        # Validate invariants
        checker = AntiDelusionChecker()
        anomalies = checker.validate_transition(tensor_before, self.tensor)
        if any(a.severity == "critical" for a in anomalies):
            raise ConservationViolation(anomalies)

        # Log to ledger
        self.ledger.log_tensor_transition(tensor_before, self.tensor)

        return result
```

---

## Visualization

```
┌─ VALUE TENSOR STATE ─────────────────────────────────────────┐
│                                                               │
│  PHYSICAL                    SEMANTIC                        │
│  ┌─────────────────────┐    ┌─────────────────────┐         │
│  │ Tokens:     12,450  │    │ Quality:      0.78  │         │
│  │ Time (ms):   3,200  │    │ Compression:  0.34  │         │
│  │ Memory:     256 MB  │    │ Confidence:   0.65  │         │
│  │ Model: opus (15x)   │    │ AST Valid:    ✓     │         │
│  └─────────────────────┘    └─────────────────────┘         │
│                                                               │
│  ECONOMIC                    ETHICAL                         │
│  ┌─────────────────────┐    ┌─────────────────────┐         │
│  │ Gas Cost:   $1.87   │    │ Sin Tax:      0.85x │         │
│  │ Impact:     342     │    │ Virtue:       1.30x │         │
│  │ RoC:        182.9x  │    │ Net:          1.11x │         │
│  │ Status:  Profitable │    │ Risk:         LOW   │         │
│  └─────────────────────┘    └─────────────────────┘         │
│                                                               │
│  EXCHANGE RATES              ANOMALIES                       │
│  ├─ token→usd:    0.00015   ├─ None detected                │
│  ├─ quality→impact: 100     │                                │
│  └─ ethical→impact: 1.11x   └─ Conservation: ✓ All hold     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Anti-Patterns

- **Single-dimension accounting**: Tracking only tokens ignores value
- **Lossless conversion assumption**: All dimension translations lose information
- **Static exchange rates**: Rates should be calibrated over time
- **Ignoring uncertainty**: Confidence scores are first-class citizens
- **Conservation violation tolerance**: Any violation needs investigation
- **Delusion-blind systems**: No cross-dimensional consistency checks

---

## Theoretical Foundations

1. **Tensor Algebra**: Multi-linear maps, covariant transformation
2. **Information Theory**: Entropy, Kolmogorov complexity, compression
3. **Economics**: Double-entry accounting, conservation of value
4. **Type Theory**: Dimension types prevent invalid operations
5. **Thermodynamics**: Conservation laws, entropy increase

---

## See Also

- [banker.md](banker.md) - The Metered Functor and UVP
- [README.md](README.md) - B-gents overview
- [../o-gents/README.md](../o-gents/README.md) - Tensor observability
- [../w-gents/README.md](../w-gents/README.md) - Tensor visualization
- [../principles.md](../principles.md) - Conservation as principle

---

*Zen Principle: The wise accountant counts in all currencies; the fool sees only tokens.*
