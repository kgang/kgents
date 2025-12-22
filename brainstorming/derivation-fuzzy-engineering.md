# Fuzzy Engineering for Agent Derivations

> *"The bootstrap is Boolean. Everything else is Bayesian."*

**Status:** Exploratory
**Date:** 2025-12-22
**Companion to:** `spec/protocols/derivation-framework.md`

---

## The Problem

Bootstrap agents have categorical proofs:
```
Id(x) = x                           ✓ Proven
(f >> g) >> h ≡ f >> (g >> h)       ✓ Proven
```

Derived agents can't have categorical proofs:
```
K-gent produces persona-aligned output    ??? How do you prove this?
Brain stores memories ethically           ??? What does "ethically" even mean?
```

This document explores the **fuzzy engineering** layer—the statistical and evidential machinery that fills the gap between axiom and application.

---

## The Evidence Hierarchy (Expanded)

### Tier 1: Categorical (Indefeasible)

```python
class CategoricalEvidence:
    """
    Mathematical proofs that don't decay.

    Sources:
    - Composition law tests
    - Identity law tests
    - Type system guarantees
    - Verified lemmas (Dafny, Lean4, Verus)
    """

    @property
    def confidence(self) -> float:
        return 1.0  # Always certain

    @property
    def decays(self) -> bool:
        return False
```

### Tier 2: Statistical (ASHC)

```python
@dataclass
class StatisticalEvidence:
    """
    Evidence from repeated observation.

    Key insight: The more runs, the tighter the confidence interval.
    """

    runs: int
    successes: int
    failures: int

    @property
    def point_estimate(self) -> float:
        """Maximum likelihood estimate."""
        return self.successes / self.runs if self.runs > 0 else 0.5

    @property
    def confidence_interval(self) -> tuple[float, float]:
        """
        95% Wilson score interval.

        Better than naive proportion for small n.
        """
        from scipy.stats import norm

        n = self.runs
        p = self.point_estimate
        z = norm.ppf(0.975)  # 95% CI

        denominator = 1 + z**2 / n
        center = (p + z**2 / (2 * n)) / denominator
        spread = z * math.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denominator

        return (max(0, center - spread), min(1, center + spread))

    @property
    def confidence(self) -> float:
        """
        Confidence based on interval width.

        Narrow interval = high confidence.
        """
        low, high = self.confidence_interval
        width = high - low

        # Map width to confidence: width=0 → conf=1.0, width=1 → conf=0.0
        return 1.0 - width

    def decay(self, days: float, rate: float = 0.01) -> "StatisticalEvidence":
        """
        Statistical evidence decays slowly.

        Old runs matter less than recent runs.
        """
        decay_factor = (1 - rate) ** days
        effective_runs = int(self.runs * decay_factor)
        effective_successes = int(self.successes * decay_factor)
        effective_failures = self.runs - effective_successes

        return StatisticalEvidence(
            runs=max(1, effective_runs),
            successes=max(0, effective_successes),
            failures=max(0, effective_failures),
        )
```

### Tier 3: Aesthetic (Hardy Criteria)

```python
@dataclass
class AestheticEvidence:
    """
    Evidence from beauty judgment.

    Hardy's criteria:
    - Inevitability: "It couldn't have been otherwise"
    - Unexpectedness: "Surprising yet fitting"
    - Economy: "No wasted motion"
    """

    inevitability_score: float   # 0.0-1.0
    unexpectedness_score: float  # 0.0-1.0
    economy_score: float         # 0.0-1.0

    # Who judged and when
    judge: str  # "kent", "claude", "community"
    judged_at: datetime

    @property
    def confidence(self) -> float:
        """
        Hardy's formula: inevitable AND (unexpected OR economical).
        """
        return self.inevitability_score * max(
            self.unexpectedness_score,
            self.economy_score,
        )

    def decay(self, days: float, rate: float = 0.03) -> "AestheticEvidence":
        """
        Aesthetic judgments decay faster than statistical.

        Taste evolves.
        """
        factor = (1 - rate) ** days
        return AestheticEvidence(
            inevitability_score=self.inevitability_score * factor,
            unexpectedness_score=self.unexpectedness_score * factor,
            economy_score=self.economy_score * factor,
            judge=self.judge,
            judged_at=self.judged_at,
        )
```

### Tier 4: Genealogical (Pattern Archaeology)

```python
@dataclass
class GenealogicalEvidence:
    """
    Evidence from historical patterns.

    Mining git history, decision traces, and usage patterns.
    """

    pattern: str                  # "Kent tends to X when Y"
    occurrences: int              # How many times observed
    consistency: float            # How consistent across occurrences
    timespan_days: int            # Over what period
    source: str                   # "git", "witness_marks", "usage_logs"

    @property
    def confidence(self) -> float:
        """
        More occurrences + higher consistency + longer timespan = more confident.
        """
        occurrence_factor = min(1.0, math.log10(max(1, self.occurrences)) / 2)
        timespan_factor = min(1.0, self.timespan_days / 365)  # 1 year = full credit

        return occurrence_factor * self.consistency * (0.5 + 0.5 * timespan_factor)

    def decay(self, days: float, rate: float = 0.005) -> "GenealogicalEvidence":
        """
        Genealogical evidence decays very slowly.

        Established patterns persist.
        """
        factor = (1 - rate) ** days
        return replace(self, consistency=self.consistency * factor)
```

### Tier 5: Somatic (The Mirror Test)

```python
class SomaticEvidence:
    """
    Evidence from felt sense.

    "Does this feel like me on my best day?"

    This tier is NEVER computed programmatically.
    It exists to document what Kent does when he reviews.

    The system can prompt for somatic evidence but cannot generate it.
    """

    @staticmethod
    def request(agent_name: str) -> str:
        """Generate a prompt for Kent to evaluate."""
        return f"""
        🪞 MIRROR TEST for {agent_name}

        Does this agent feel like you on your best day?
        - Daring?
        - Bold?
        - Creative?
        - Opinionated but not gaudy?

        Rate 0-10, or describe your felt sense:
        """

    @staticmethod
    def parse_response(response: str) -> float | None:
        """
        Parse Kent's somatic response.

        Returns confidence 0.0-1.0, or None if unparseable.
        """
        # Try to extract number
        import re
        match = re.search(r'\b(\d+)\b', response)
        if match:
            score = int(match.group(1))
            return min(1.0, score / 10.0)

        # Sentiment analysis fallback
        positive = any(word in response.lower() for word in
                      ["yes", "good", "right", "feels", "love", "perfect"])
        negative = any(word in response.lower() for word in
                      ["no", "wrong", "off", "bad", "hate", "ugh"])

        if positive and not negative:
            return 0.8
        if negative and not positive:
            return 0.2
        return None  # Ambiguous
```

---

## Principle Archaeology

### Mining Git History

```python
async def mine_principle_patterns(
    repo_path: Path,
    principles: list[str],
    since_days: int = 365,
) -> dict[str, GenealogicalEvidence]:
    """
    Analyze git history to find principle usage patterns.

    Searches commit messages, code comments, and spec changes.
    """
    results = {}

    for principle in principles:
        # Find commits mentioning this principle
        commits = await git_log_grep(
            repo_path,
            pattern=principle.lower(),
            since_days=since_days,
        )

        # Analyze consistency
        if commits:
            consistency = analyze_principle_consistency(commits, principle)

            results[principle] = GenealogicalEvidence(
                pattern=f"Kent applies {principle} principle",
                occurrences=len(commits),
                consistency=consistency,
                timespan_days=since_days,
                source="git",
            )

    return results


def analyze_principle_consistency(
    commits: list[Commit],
    principle: str,
) -> float:
    """
    How consistently is the principle applied?

    Checks:
    - Are commits about this principle mostly positive? (adding, not removing)
    - Do they cluster or spread evenly?
    - Are there reversals?
    """
    positive = sum(1 for c in commits if "add" in c.message.lower() or
                                          "implement" in c.message.lower() or
                                          "enable" in c.message.lower())
    negative = sum(1 for c in commits if "remove" in c.message.lower() or
                                          "revert" in c.message.lower() or
                                          "disable" in c.message.lower())

    if positive + negative == 0:
        return 0.5

    return positive / (positive + negative)
```

### Mining Witness Marks

```python
async def mine_principle_from_marks(
    marks: list[Mark],
    principle: str,
) -> GenealogicalEvidence:
    """
    Analyze witness marks for principle adherence patterns.

    Marks include reasoning and principles fields.
    """
    relevant_marks = [
        m for m in marks
        if principle in m.principles
    ]

    if not relevant_marks:
        return GenealogicalEvidence(
            pattern=f"No {principle} marks found",
            occurrences=0,
            consistency=0.0,
            timespan_days=0,
            source="witness_marks",
        )

    # Calculate timespan
    timestamps = [m.timestamp for m in relevant_marks]
    timespan = (max(timestamps) - min(timestamps)).days

    # Calculate consistency from alternatives
    # If alternatives were rarely considered, principle was strongly applied
    alternatives_considered = sum(
        len(m.alternatives) for m in relevant_marks
    )
    avg_alternatives = alternatives_considered / len(relevant_marks)
    consistency = 1.0 / (1.0 + avg_alternatives * 0.2)

    return GenealogicalEvidence(
        pattern=f"{principle} applied in {len(relevant_marks)} decisions",
        occurrences=len(relevant_marks),
        consistency=consistency,
        timespan_days=timespan,
        source="witness_marks",
    )
```

---

## Confidence Aggregation

### The Aggregation Formula

```python
def aggregate_confidence(
    categorical: list[CategoricalEvidence],
    statistical: list[StatisticalEvidence],
    aesthetic: list[AestheticEvidence],
    genealogical: list[GenealogicalEvidence],
    somatic: float | None,
) -> float:
    """
    Aggregate evidence from all tiers into overall confidence.

    Weighting:
    - Categorical: 0.40 (if any present, otherwise redistributed)
    - Statistical: 0.25
    - Aesthetic: 0.15
    - Genealogical: 0.10
    - Somatic: 0.10 (Kent's override power)
    """
    weights = {
        "categorical": 0.40,
        "statistical": 0.25,
        "aesthetic": 0.15,
        "genealogical": 0.10,
        "somatic": 0.10,
    }

    # Compute tier averages
    cat_avg = mean([e.confidence for e in categorical]) if categorical else None
    stat_avg = mean([e.confidence for e in statistical]) if statistical else None
    aes_avg = mean([e.confidence for e in aesthetic]) if aesthetic else None
    gen_avg = mean([e.confidence for e in genealogical]) if genealogical else None

    # Redistribute weights for missing tiers
    present = {
        "categorical": cat_avg,
        "statistical": stat_avg,
        "aesthetic": aes_avg,
        "genealogical": gen_avg,
        "somatic": somatic,
    }

    active_weights = {k: v for k, v in weights.items() if present[k] is not None}
    total_active = sum(active_weights.values())

    if total_active == 0:
        return 0.5  # No evidence at all

    # Normalize weights
    normalized = {k: v / total_active for k, v in active_weights.items()}

    # Weighted average
    result = sum(
        normalized[k] * present[k]
        for k in normalized
    )

    # Somatic override: Kent's felt sense can cap or boost
    if somatic is not None:
        # Strong negative somatic response caps confidence
        if somatic < 0.3:
            result = min(result, 0.5)
        # Strong positive response provides floor
        elif somatic > 0.8:
            result = max(result, 0.6)

    return result
```

### The Somatic Veto

```python
class SomaticVeto:
    """
    Kent's somatic response is an absolute veto.

    From the constitution:
    "Kent's somatic disgust is an absolute veto.
     It cannot be argued away or evidence'd away.
     It is the ethical floor beneath which no decision may fall."
    """

    @staticmethod
    def check(somatic: float | None, agent_name: str) -> tuple[bool, str]:
        """
        Check if somatic response vetoes the agent.

        Returns (vetoed, reason).
        """
        if somatic is None:
            return False, "No somatic response recorded"

        if somatic < 0.2:
            return True, f"Somatic veto: {agent_name} feels wrong (score: {somatic:.2f})"

        if somatic < 0.4:
            return False, f"Somatic warning: {agent_name} is borderline (score: {somatic:.2f})"

        return False, f"Somatic approval: {agent_name} passes mirror test (score: {somatic:.2f})"
```

---

## Confidence Propagation Models

### Product Model (Default)

```python
def propagate_product(
    ancestor_confidences: list[float],
    tier_factor: float,
) -> float:
    """
    Inherited confidence = product of ancestors × tier factor.

    Conservative: errors compound.
    """
    if not ancestor_confidences:
        return tier_factor

    product = 1.0
    for c in ancestor_confidences:
        product *= c

    return max(0.3, product * tier_factor)  # Floor of 0.3
```

### Weakest Link Model

```python
def propagate_weakest_link(
    ancestor_confidences: list[float],
    tier_factor: float,
) -> float:
    """
    Inherited confidence = min of ancestors × tier factor.

    A chain is only as strong as its weakest link.
    """
    if not ancestor_confidences:
        return tier_factor

    return min(ancestor_confidences) * tier_factor
```

### Weighted Average Model

```python
def propagate_weighted_average(
    ancestor_confidences: list[float],
    ancestor_weights: list[float],
    tier_factor: float,
) -> float:
    """
    Inherited confidence = weighted average of ancestors × tier factor.

    Some ancestors matter more than others.
    """
    if not ancestor_confidences:
        return tier_factor

    if len(ancestor_weights) != len(ancestor_confidences):
        # Default to equal weights
        ancestor_weights = [1.0 / len(ancestor_confidences)] * len(ancestor_confidences)

    weighted_sum = sum(c * w for c, w in zip(ancestor_confidences, ancestor_weights))
    weight_total = sum(ancestor_weights)

    return (weighted_sum / weight_total) * tier_factor
```

### Hybrid Model (Recommended)

```python
def propagate_hybrid(
    ancestor_confidences: list[float],
    tier_factor: float,
    product_weight: float = 0.6,
    min_weight: float = 0.4,
) -> float:
    """
    Hybrid of product and weakest-link models.

    Balances error compounding with single-point-of-failure detection.
    """
    product = propagate_product(ancestor_confidences, tier_factor=1.0)
    weakest = propagate_weakest_link(ancestor_confidences, tier_factor=1.0)

    hybrid = product * product_weight + weakest * min_weight

    return hybrid * tier_factor
```

---

## Decay Models

### Exponential Decay (Default)

```python
def exponential_decay(
    confidence: float,
    days: float,
    half_life: float = 90.0,  # 90 days to halve
) -> float:
    """
    Confidence decays exponentially over time.

    half_life = days for confidence to halve.
    """
    decay_rate = math.log(2) / half_life
    return confidence * math.exp(-decay_rate * days)
```

### Stepped Decay

```python
def stepped_decay(
    confidence: float,
    days: float,
    thresholds: list[tuple[int, float]] = [(30, 0.95), (90, 0.85), (180, 0.70), (365, 0.50)],
) -> float:
    """
    Confidence decays in steps at thresholds.

    More interpretable than exponential.
    """
    factor = 1.0
    for threshold_days, threshold_factor in thresholds:
        if days >= threshold_days:
            factor = threshold_factor

    return confidence * factor
```

### Evidence-Type-Specific Decay

```python
DECAY_RATES = {
    EvidenceType.CATEGORICAL: 0.0,      # Never decays
    EvidenceType.EMPIRICAL: 0.01,       # Slow decay
    EvidenceType.AESTHETIC: 0.03,       # Medium decay
    EvidenceType.GENEALOGICAL: 0.005,   # Very slow decay
    EvidenceType.SOMATIC: 0.02,         # Medium decay
}

def apply_decay(
    draw: PrincipleDraw,
    days: float,
) -> PrincipleDraw:
    """Apply appropriate decay based on evidence type."""
    rate = DECAY_RATES.get(draw.evidence_type, 0.01)

    if rate == 0.0:
        return draw

    new_strength = draw.draw_strength * (1 - rate) ** days
    return replace(draw, draw_strength=max(0.1, new_strength))
```

---

## Refresh Strategies

### Periodic ASHC Refresh

```python
async def periodic_refresh(
    registry: DerivationRegistry,
    agent_name: str,
    ashc: AdaptiveCompiler,
) -> Derivation:
    """
    Periodically re-run ASHC to refresh evidence.

    Triggered by:
    - Evidence age > threshold
    - Usage count increase
    - Dependency confidence change
    """
    current = registry.get(agent_name)

    # Check if refresh needed
    age = (datetime.now() - current.last_refreshed).days
    if age < 30 and current.empirical_confidence > 0.8:
        return current  # Skip refresh

    # Run ASHC with adaptive stopping
    spec = load_spec(agent_name)
    output = await ashc.compile(spec)

    # Update derivation
    return registry.update_evidence(agent_name, ashc_evidence=output.evidence)
```

### Usage-Triggered Refresh

```python
async def usage_triggered_refresh(
    registry: DerivationRegistry,
    agent_name: str,
    usage_milestone: int,
) -> Derivation:
    """
    Refresh evidence when usage hits milestones.

    Milestones: 100, 500, 1000, 5000, 10000, ...
    """
    current = registry.get(agent_name)
    current_usage = registry.get_usage_count(agent_name)

    # Check if milestone crossed
    milestones = [100, 500, 1000, 5000, 10000, 50000]
    for milestone in milestones:
        if current_usage >= milestone and current.last_refresh_usage < milestone:
            # Milestone crossed, refresh
            return await periodic_refresh(registry, agent_name, ashc)

    return current
```

---

## Open Questions

1. **Optimal decay rates?** The rates above are guesses. Need empirical data from real usage.

2. **Propagation model selection?** Should different agent types use different models?

3. **Somatic evidence collection?** How do we prompt Kent without being annoying?

4. **Cross-session learning?** How does evidence transfer between Claude instances?

5. **Adversarial evidence?** What if someone tries to game the evidence system?

---

## The Vision

The derivation framework turns kgents into a **self-evidencing system**:

- Every agent knows its lineage
- Every agent can justify its confidence
- Confidence flows through the DAG
- Evidence accumulates, decays, and refreshes
- Kent's somatic sense is the ultimate arbiter

> *"Bootstrap confidence is given. Derived confidence is earned."*

---

**Filed:** 2025-12-22
**Status:** Exploratory — informing Phase 1 implementation
