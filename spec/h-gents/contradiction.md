# Contradiction Detection

**How H-gents identify tensions between stated and actual.**

---

## Philosophy

> "Contradiction is the root of all movement and vitality; it is only in so far as something has a contradiction within it that it moves, has an urge and activity."
> — Hegel

A contradiction is not an error to fix—it is a signal of life, growth, and potential transformation. The goal is not to eliminate contradictions but to **surface** them so they can drive change.

---

## The Contradict Operation

```python
@dataclass(frozen=True)
class ContradictInput:
    """Input to the Contradict operation."""
    thesis: Thesis           # Stated principle/value
    observation: Observation # Observed behavior/pattern

@dataclass(frozen=True)
class ContradictOutput:
    """Output from the Contradict operation."""
    tension: Tension | None  # None if no contradiction found
    confidence: float        # 0-1 how confident we are
    evidence: list[str]      # Supporting observations

async def contradict(
    thesis: Thesis,
    observation: Observation,
    sensitivity: float = 0.5,  # 0-1, higher = more strict
) -> ContradictOutput:
    """
    Detect if observation contradicts thesis.

    The operation is asymmetric: thesis is the standard,
    observation is measured against it.
    """
    ...
```

---

## Detection Strategies

### 1. Structural Analysis (Fast, Shallow)

Analyze observable metrics without semantic interpretation.

**For Obsidian vaults:**

| Metric | Indicates |
|--------|-----------|
| Link density | Connection behavior |
| Note length distribution | Depth of engagement |
| Update frequency | Maintenance patterns |
| Orphan count | Integration behavior |
| Tag usage | Classification behavior |

**For organizational tools:**

| Metric | Indicates |
|--------|-----------|
| Response latency | Async vs sync culture |
| Decision document ratio | Documentation behavior |
| Meeting frequency | Collaboration patterns |
| Channel topology | Information flow |
| Edit attribution | Ownership patterns |

**Implementation:**

```python
async def structural_contradiction(
    thesis: Thesis,
    metrics: dict[str, float],
) -> ContradictOutput:
    """
    Detect structural contradictions without semantic analysis.

    Example:
    - Thesis: "We value asynchronous communication"
    - Metric: avg_response_time_minutes = 8
    - Contradiction: Fast response expectation contradicts async claim
    """
    ...
```

### 2. Semantic Analysis (Slow, Deep)

Analyze content meaning against stated principles.

**Process:**
1. Extract semantic intent from thesis
2. Extract semantic patterns from observations
3. Measure semantic divergence
4. Generate interpretation

**Implementation:**

```python
async def semantic_contradiction(
    thesis: Thesis,
    content: list[Document],
    llm_func: Callable[[str], str],
) -> ContradictOutput:
    """
    Detect semantic contradictions using LLM analysis.

    Example:
    - Thesis: "Daily notes are for reflection"
    - Content: 80% of daily notes are task lists
    - Contradiction: Task-focus contradicts reflection intent
    """
    prompt = f"""
    Principle stated: "{thesis.content}"
    Source: {thesis.source}

    Observed content patterns:
    {summarize_patterns(content)}

    Question: Does the observed behavior align with the stated principle?
    If not, describe the specific contradiction.

    Return JSON:
    {{
        "aligned": true/false,
        "divergence": 0.0-1.0,
        "contradiction": "description if not aligned",
        "evidence": ["specific observations"]
    }}
    """
    ...
```

### 3. Temporal Analysis (Drift Detection)

Detect how alignment changes over time.

**Patterns:**
- **Decay**: Alignment decreases over time
- **Recovery**: Alignment increases after low point
- **Oscillation**: Alignment varies cyclically
- **Stability**: Alignment remains constant

**Implementation:**

```python
async def temporal_contradiction(
    thesis: Thesis,
    observations: list[tuple[datetime, Observation]],
) -> ContradictOutput:
    """
    Detect temporal drift in principle adherence.

    Example:
    - Thesis: "We document all major decisions"
    - Pattern: Documentation rate drops 40% during crunch
    - Contradiction: Time pressure reveals real vs stated priority
    """
    ...
```

---

## The Divergence Score

Divergence measures how far behavior is from stated principle.

```python
@dataclass(frozen=True)
class DivergenceScore:
    """Quantified gap between thesis and antithesis."""

    value: float  # 0.0 = perfect alignment, 1.0 = direct contradiction

    # Component scores
    structural: float  # From metrics analysis
    semantic: float    # From content analysis
    temporal: float    # From drift analysis

    # Interpretation thresholds
    @property
    def severity(self) -> str:
        if self.value < 0.2:
            return "aligned"       # Minor variance, not concerning
        elif self.value < 0.4:
            return "tension"       # Worth noting, not urgent
        elif self.value < 0.6:
            return "contradiction" # Clear gap requiring attention
        elif self.value < 0.8:
            return "significant"   # Major divergence
        else:
            return "crisis"        # Fundamental integrity issue
```

---

## Common Contradiction Patterns

### The Aspiration Gap

**Pattern**: Stated principle is aspirational, behavior is pragmatic.

**Example**:
- Thesis: "We value work-life balance"
- Antithesis: Emails sent at 11pm regularly
- Diagnosis: Aspiration exceeds practice

**Resolution paths**:
- Revise principle to be realistic
- Change behavior to match aspiration
- Make aspiration explicit ("we aspire to...")

### The Decay Pattern

**Pattern**: Principle was followed but eroded over time.

**Example**:
- Thesis: "Every feature has tests"
- Antithesis: Test coverage dropped from 90% to 60%
- Diagnosis: Entropy eroding practice

**Resolution paths**:
- Reinstate enforcement mechanisms
- Acknowledge changed priority
- Implement automated safeguards

### The Context Collapse

**Pattern**: Principle applies in one context but not another.

**Example**:
- Thesis: "We ship incrementally"
- Antithesis: Platform rewrites with 6-month cycles
- Diagnosis: Rule has implicit exceptions

**Resolution paths**:
- Make context explicit ("for user features...")
- Split into multiple principles
- Accept contextual variation

### The Shadow Contradiction

**Pattern**: Stated principle has hidden opposite that's also true.

**Example**:
- Thesis: "Move fast and break things"
- Antithesis: Critical path code never changes
- Diagnosis: Speed has unstated limits

**Resolution paths**:
- Acknowledge the shadow principle
- Integrate both into richer statement
- Map where each applies

### The Performative Contradiction

**Pattern**: The way a principle is stated contradicts its content.

**Example**:
- Thesis: "We communicate simply and directly"
- Source: 40-page communication guidelines document
- Diagnosis: Meta-level contradiction

**Resolution paths**:
- Practice what you preach
- Reduce principle statement complexity
- Acknowledge the irony

---

## Detection Quality Metrics

### Precision
**Question**: Of detected contradictions, how many are real?

High precision = few false positives = trust the detector.

### Recall
**Question**: Of real contradictions, how many are detected?

High recall = few false negatives = comprehensive coverage.

### Sensitivity Calibration

```python
class SensitivityProfile:
    """Tuning for contradiction detection."""

    CONSERVATIVE = 0.3   # Only surface clear contradictions
    BALANCED = 0.5       # Default: reasonable threshold
    SENSITIVE = 0.7      # Surface subtle tensions
    PARANOID = 0.9       # Flag everything that might diverge
```

**Guidance**:
- Start CONSERVATIVE for new systems (build trust)
- Move to BALANCED as calibration improves
- Use SENSITIVE during explicit reflection periods
- Avoid PARANOID except for audits

---

## Implementation Notes

### Bootstrap Derivation

`Contradict` is a **bootstrap primitive**, not an agent:

```python
# In spec/bootstrap.md
Contradict: (Statement, Observation) → Tension | None

# Properties:
# - Deterministic given inputs
# - No side effects
# - Composable with other primitives
```

### Performance Considerations

| Strategy | Latency | Cost | When to Use |
|----------|---------|------|-------------|
| Structural | <100ms | Free | Always (baseline) |
| Semantic | 1-5s | $ | Deep analysis needed |
| Temporal | 100ms-1s | Free | Historical patterns |

**Recommendation**: Run structural analysis continuously, semantic analysis on demand.

### Privacy Boundaries

```python
@dataclass
class ContradictConfig:
    """Privacy-respecting detection configuration."""

    # What to analyze
    structural_analysis: bool = True   # Metrics only
    semantic_analysis: bool = False    # Requires content access

    # What to ignore
    sanctuary_channels: set[str] = field(default_factory=set)
    private_documents: set[str] = field(default_factory=set)

    # How to report
    blind_mode: bool = False  # If true, report divergence without content
```

---

## Composition with Other Operations

### With Sublation

```python
tension = await contradict(thesis, observation)
if tension and tension.divergence > THRESHOLD:
    synthesis = await sublate(tension)
```

### With Kairos

```python
tension = await contradict(thesis, observation)
if tension and tension.divergence > THRESHOLD:
    kairos = await wait_for_kairos(tension)
    # Only surface tension when timing is right
```

### With W-gent (Witness)

```python
# W-gent feeds observations to contradiction detection
observations = await W_gent.observe(system)
for obs in observations:
    tension = await contradict(principle, obs)
```

---

## Anti-Patterns

1. **Contradiction Hunting**: Looking for contradictions to prove a point
2. **Perfectionism**: Expecting 0.0 divergence (unrealistic)
3. **Context Blindness**: Ignoring legitimate situational variance
4. **Recency Bias**: Over-weighting recent behavior
5. **Metric Worship**: Trusting numbers over judgment
6. **Adversarial Detection**: Using detection punitively

---

## See Also

- [sublation.md](sublation.md) — How tensions resolve
- [kairos.md](kairos.md) — When to surface tensions
- [README.md](README.md) — H-gent overview
- [hegel.md](hegel.md) — Hegelian dialectics

---

*"The goal is not to catch the organization in hypocrisy, but to help it see itself more clearly."*
