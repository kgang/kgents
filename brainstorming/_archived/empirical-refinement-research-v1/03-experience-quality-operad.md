# Experience Quality Operad: Empirical Refinement

> *"Quality is not a number. It is a structure. The structure composes."*

**Related Spec**: `spec/theory/experience-quality-operad.md`
**Priority**: MEDIUM
**Status**: Ready for Validation

---

## 1. Current State Analysis

### 1.1 What You Have

Your Experience Quality Tetrad:

| Dimension | Symbol | Measurement | Type |
|-----------|--------|-------------|------|
| **Contrast** | C | Variance across time | [0, 1] |
| **Arc** | A | Phase coverage | [0, 1] |
| **Voice** | V | Multi-perspective approval | {0,1}^n |
| **Floor** | F | Must-haves present | {0, 1} |

**Overall Quality**: Q = F × (αC + βA + γV)

Default weights: α=0.35, β=0.35, γ=0.30

### 1.2 What's Missing

1. **Empirical Weight Calibration**: Are α=0.35, β=0.35, γ=0.30 optimal?
2. **Attitudinal Metrics**: Current Floor is behavioral; no satisfaction measures
3. **Benchmark Validation**: No comparison to established UX frameworks
4. **Cross-Domain Testing**: Only WASM Survivors algebra exists

---

## 2. Research Findings

### 2.1 HEART Framework (Google)

The [HEART framework](https://dl.acm.org/doi/abs/10.1145/1753326.1753687) is Google's validated UX measurement approach:

| Dimension | Description | Your Analog |
|-----------|-------------|-------------|
| **Happiness** | Satisfaction, NPS | Voice (attitudinal) |
| **Engagement** | Usage patterns, depth | Contrast (behavioral) |
| **Adoption** | New user acquisition | N/A (different scope) |
| **Retention** | Return rate | Arc (completion) |
| **Task Success** | Completion, errors | Floor (must-haves) |

**Key Insight**: HEART separates **behavioral** (Engagement, Adoption, Retention, Task Success) from **attitudinal** (Happiness). Your framework conflates these.

### 2.2 User Experience Questionnaire (UEQ)

The [UEQ](https://link.springer.com/chapter/10.1007/978-3-540-89350-9_6) was developed with 80 bipolar items and validated empirically:

**Two Quality Types**:
- **Pragmatic Quality**: Efficiency, effectiveness, goal-achievement
- **Hedonic Quality**: Aesthetics, joy-of-use, attractiveness

**Implication**: Your Arc and Floor are pragmatic. Contrast and Voice lean hedonic. Consider explicit separation.

### 2.3 Systematic UX Review

A [comprehensive review](https://www.tandfonline.com/doi/full/10.1080/10447318.2024.2394724?af=R) of 96 UX methods found:

- Methods vary by: origin (academia/industry), data type (quant/qual), location (lab/field/online)
- 116 UX instruments identified
- Strong emphasis on **mixed methods** (quantitative + qualitative)

**Implication**: Your operad is purely quantitative. Consider qualitative integration.

### 2.4 UX Metric Categories

Standard [UX metric taxonomy](https://userpilot.com/blog/how-to-measure-user-experience/):

| Category | Metrics | Your Coverage |
|----------|---------|---------------|
| **Behavioral** | Task success, error rate, time on task | Floor, Arc |
| **Attitudinal** | NPS, CSAT, SUS | Voice (partial) |
| **Performance** | Load time, latency | Floor (partial) |

---

## 3. Refinement Recommendations

### 3.1 Add Attitudinal Dimension to Voice

**Current**: Voice checks boolean approval from different perspectives.

**Refined**: Add attitudinal sub-dimension.

```python
@dataclass(frozen=True)
class VoiceDefinition:
    """A single quality perspective/voice."""
    name: str
    question: str
    checker: str
    weight: float = 1.0

    # NEW: Attitudinal vs. Behavioral
    voice_type: Literal["behavioral", "attitudinal"] = "behavioral"


@dataclass(frozen=True)
class VoiceMeasurement:
    """Multi-voice quality assessment with attitudinal metrics."""

    verdicts: tuple[VoiceVerdict, ...]

    # NEW: Attitudinal scores (continuous, not boolean)
    nps_score: float | None = None          # Net Promoter Score [-100, 100]
    satisfaction_score: float | None = None  # [0, 1]
    effort_score: float | None = None        # Customer Effort Score [0, 1]

    @property
    def aligned(self) -> bool:
        """All voices approve."""
        return all(v.passed for v in self.verdicts)

    @property
    def alignment_score(self) -> float:
        """Continuous alignment incorporating attitudinal metrics."""
        base = sum(v.confidence * v.passed for v in self.verdicts) / len(self.verdicts) if self.verdicts else 1.0

        # Blend in attitudinal if available
        attitudinal_scores = [
            s for s in [self.nps_score, self.satisfaction_score, self.effort_score]
            if s is not None
        ]

        if attitudinal_scores:
            # Normalize NPS to [0, 1]
            if self.nps_score is not None:
                attitudinal_scores[0] = (self.nps_score + 100) / 200

            attitudinal_mean = sum(attitudinal_scores) / len(attitudinal_scores)
            # 70% behavioral, 30% attitudinal
            return 0.7 * base + 0.3 * attitudinal_mean

        return base
```

### 3.2 Integrate HEART Dimensions

**Map your Tetrad to HEART for cross-validation**:

```python
@dataclass
class HEARTMapping:
    """Map Experience Quality Tetrad to HEART framework."""

    # Your dimensions
    contrast: float
    arc: float
    voice: VoiceMeasurement
    floor: FloorMeasurement

    def to_heart(self) -> HEARTScore:
        """Convert to HEART framework for benchmarking."""
        return HEARTScore(
            # Happiness = Voice attitudinal components
            happiness=self.voice.satisfaction_score or self.voice.alignment_score,

            # Engagement = Contrast (variety drives engagement)
            engagement=self.contrast,

            # Adoption = N/A for single-experience measurement
            adoption=None,

            # Retention = Arc coverage (complete experiences retain)
            retention=self.arc,

            # Task Success = Floor pass rate
            task_success=1.0 if self.floor.passed else self.floor.pass_ratio,
        )

    def validate_against_heart(self, heart_benchmark: HEARTScore) -> ValidationResult:
        """Compare to HEART benchmark for calibration."""
        mine = self.to_heart()

        return ValidationResult(
            happiness_delta=abs(mine.happiness - heart_benchmark.happiness),
            engagement_delta=abs(mine.engagement - heart_benchmark.engagement),
            retention_delta=abs(mine.retention - heart_benchmark.retention),
            task_success_delta=abs(mine.task_success - heart_benchmark.task_success),
            overall_correlation=self._compute_correlation(mine, heart_benchmark),
        )
```

### 3.3 Empirical Weight Calibration

**Current**: α=0.35, β=0.35, γ=0.30 (arbitrary)

**Proposed Calibration Protocol**:

```python
@dataclass
class WeightCalibrationExperiment:
    """Calibrate Tetrad weights using regression on user satisfaction."""

    experiences: list[Experience]
    human_quality_ratings: list[float]  # Ground truth

    async def calibrate(self) -> CalibratedWeights:
        """
        Find optimal weights via regression.

        Model: user_rating = α*C + β*A + γ*V (given F=1)

        Constraints:
        - α + β + γ = 1
        - α, β, γ > 0
        """
        # Measure each dimension
        measurements = []
        for exp in self.experiences:
            m = await measure_all(exp)
            if m.floor_passed:  # Only calibrate on passing experiences
                measurements.append({
                    "contrast": m.contrast,
                    "arc": m.arc,
                    "voice": m.voice_alignment,
                    "rating": self.human_quality_ratings[exp.id],
                })

        # Fit constrained linear regression
        from scipy.optimize import minimize

        def loss(weights):
            alpha, beta, gamma = weights
            predictions = [
                alpha * m["contrast"] + beta * m["arc"] + gamma * m["voice"]
                for m in measurements
            ]
            actuals = [m["rating"] for m in measurements]
            return sum((p - a) ** 2 for p, a in zip(predictions, actuals))

        result = minimize(
            loss,
            x0=[0.33, 0.33, 0.34],
            constraints=[
                {"type": "eq", "fun": lambda w: sum(w) - 1},
            ],
            bounds=[(0.1, 0.6)] * 3,
        )

        return CalibratedWeights(
            alpha=result.x[0],
            beta=result.x[1],
            gamma=result.x[2],
            r_squared=1 - result.fun / self._total_variance(measurements),
        )
```

### 3.4 Pragmatic/Hedonic Separation

Following UEQ research, explicitly separate quality types:

```python
@dataclass(frozen=True)
class ExperienceQualityExtended:
    """Extended quality with pragmatic/hedonic separation."""

    # Pragmatic Quality (goal-achievement)
    arc_coverage: float      # Did I complete the journey?
    floor_passed: bool       # Did the basics work?

    # Hedonic Quality (joy, aesthetics)
    contrast: float          # Was it varied and interesting?
    voice_alignment: float   # Did it resonate with my values?

    @property
    def pragmatic_quality(self) -> float:
        """Goal-achievement score."""
        if not self.floor_passed:
            return 0.0
        return self.arc_coverage

    @property
    def hedonic_quality(self) -> float:
        """Joy and resonance score."""
        return 0.5 * self.contrast + 0.5 * self.voice_alignment

    @property
    def overall(self) -> float:
        """
        Combined quality.

        Research suggests pragmatic is baseline, hedonic is differentiator.
        """
        if not self.floor_passed:
            return 0.0

        # Pragmatic as multiplier (baseline)
        # Hedonic as additive (differentiator)
        return 0.6 * self.pragmatic_quality + 0.4 * self.hedonic_quality
```

---

## 4. Floor Dimension Enrichment

### 4.1 Current Floor Checks

Your Floor checks are primarily technical:
- `input_latency <= threshold`
- `feedback_density >= threshold`

### 4.2 Add Psychological Floor Checks

Based on UX research, add these floor checks:

```python
UNIVERSAL_FLOOR_CHECKS = [
    # Technical (your current)
    FloorCheckDefinition("latency", "Response within acceptable time", 200.0, "<=", "ms"),
    FloorCheckDefinition("error_rate", "Low error occurrence", 0.05, "<=", "ratio"),

    # Psychological (new)
    FloorCheckDefinition("perceived_control", "User feels in control", 0.7, ">=", "ratio"),
    FloorCheckDefinition("progress_visible", "Progress is trackable", 1.0, "==", "bool"),
    FloorCheckDefinition("recovery_possible", "Errors are recoverable", 1.0, "==", "bool"),

    # Cognitive (new)
    FloorCheckDefinition("cognitive_load", "Mental effort is manageable", 0.7, "<=", "ratio"),
    FloorCheckDefinition("clarity", "Purpose and state are clear", 0.8, ">=", "ratio"),
]
```

---

## 5. Validation Protocol

### 5.1 Weight Calibration Study

**Goal**: Determine optimal α, β, γ.

**Protocol**:
1. Collect 100 experiences across 3 domains (games, productivity, learning)
2. Measure Contrast, Arc, Voice for each
3. Collect user quality ratings (1-10 scale)
4. Fit regression, extract weights
5. Validate on held-out 20%

**Success Criteria**:
- R² > 0.70 (weights explain majority of variance)
- Weights stable across domains (±0.10)

### 5.2 HEART Correlation Study

**Goal**: Validate Tetrad against established HEART framework.

**Protocol**:
1. Collect 50 experiences with both Tetrad and HEART measurements
2. Compute correlation between mapped dimensions
3. Identify systematic biases

**Success Criteria**:
- Pearson r > 0.75 for each dimension pair
- No dimension with r < 0.60

### 5.3 Operad Law Verification

**Goal**: Verify composition laws hold empirically.

**Protocol**:
1. Measure quality of 50 experiences A
2. Measure quality of 50 experiences B
3. Measure quality of A >> B compositions
4. Check: |Q(A >> B) - sequential_compose(Q(A), Q(B))| < ε

**Success Criteria**:
- Mean absolute error < 0.05
- 95% of compositions within ±0.10

---

## 6. Research Contribution Opportunity

**Title**: "The Experience Quality Operad: Compositional Metrics for Interactive Systems"

**Venue**: CHI 2025/2026, CSCW, or DIS

**Novel Contributions**:
1. Categorical framework for experience quality
2. Compositional laws for quality (sequential, parallel, nested)
3. Empirical validation against HEART

**Positioning**:
- Extends HEART with mathematical composition
- Extends UEQ with operadic structure
- First algebraic treatment of UX metrics

---

## Pilot Integration

**Goal**: Convert quality operad metrics into actionable PLAYER evidence.

### Prompt Hooks (Minimal Insertions)
Add a PLAYER scorecard block to `.player.feedback.md` (iterations 8-10):

```
## Experience Quality Scorecard
Contrast (C): [0.0-1.0] — evidence: [screenshot/test id]
Arc (A): [0.0-1.0] — evidence: [session notes]
Voice (V): [pass/fail + 1-7 rating] — evidence: [quote]
Floor (F): [pass/fail] — evidence: [basic checks]
```

### Aggregation Artifact
Add a `CRYSTAL.md` section:

```
## Experience Quality Summary
Q = F × (0.35*C + 0.35*A + 0.30*V)
Notes: [one sentence on weakest dimension]
```

### Outcome Target
- Make PLAYER judgment comparable across runs.
- Enable post-run tuning of C/A/V weights using actual pilot evidence.

---

## 7. References

1. **Rodden, K., Hutchinson, H., & Fu, X.** (2010). Measuring the User Experience on a Large Scale. *CHI 2010*. https://dl.acm.org/doi/abs/10.1145/1753326.1753687

2. **Laugwitz, B., Held, T., & Schrepp, M.** (2008). Construction and Evaluation of a User Experience Questionnaire. *HCI and Usability*. https://link.springer.com/chapter/10.1007/978-3-540-89350-9_6

3. **Ogunyemi, A., & Kapros, E.** (2024). Usability and User Experience Evaluation in Intelligent Environments: A Review. *IJHCI*. https://www.tandfonline.com/doi/full/10.1080/10447318.2024.2394724

4. **Stanford Medicine.** Experience Metrics Framework. https://improvement.stanford.edu/resources/experience-metrics

5. **Userpilot.** (2024). How to Measure User Experience: 12 UX Metrics That Matter Most. https://userpilot.com/blog/how-to-measure-user-experience/

---

*"Joy is the serious business of Heaven." — C.S. Lewis*
