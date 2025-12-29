# Experience Quality Operad

> *"Quality of experience is measurable, composable, and witnessable."*

**Version**: 2.0
**Status**: Canonical Specification
**Date**: 2025-12-27
**Principles**: Composable, Generative, Joy-Inducing, Ethical
**Layer**: L4 (Specification)

---

## Abstract

The Experience Quality Operad (EQO) provides a **categorical framework for measuring and composing experiential quality** in any interactive system. It unifies four orthogonal quality dimensions—Contrast, Arc, Voice, and Floor—into a single operad where quality metrics compose algebraically.

**Core Insight**: Experience quality is not a single number but a **structured object** with composition laws. Two experiences compose, and their combined quality is derivable from their individual qualities plus interaction terms.

**Domain Independence**: This spec defines the UNIVERSAL framework. Domain-specific instantiations (games, productivity tools, learning systems, etc.) define their own **QualityAlgebra** that maps abstract categories to concrete measurements. See `spec/theory/domains/` for domain bindings.

---

## Part I: Universal Quality Tetrad

### 1.1 The Tetrad Schema

Experience quality decomposes into four orthogonal dimensions:

| Dimension | Symbol | Question | Type | Semantics |
|-----------|--------|----------|------|-----------|
| **Contrast** | C | "Does this experience have variety?" | [0, 1] | Continuous measurement of variation across time |
| **Arc** | A | "Does this experience have shape?" | [0, 1] | Coverage of emotional/engagement phases |
| **Voice** | V | "Does this experience satisfy multiple quality perspectives?" | {0,1}^n | Boolean vector of n voice approvals |
| **Floor** | F | "Is this experience worth having?" | {0, 1} | Gate: all must-haves present |

**Key Properties**:

- **Contrast** measures VARIANCE — high contrast means the experience changes significantly over time
- **Arc** measures COVERAGE — full arc means the experience visits expected phases (domain defines phases)
- **Voice** measures ALIGNMENT — multiple perspectives (domain defines which voices) approve
- **Floor** is a GATE — if floor fails, quality is zero regardless of other dimensions

### 1.2 QualityAlgebra Pattern

A **QualityAlgebra** is a domain-specific instantiation that defines:

```python
@dataclass
class QualityAlgebra:
    """
    A domain instantiation of the Experience Quality Operad.

    Every domain (games, learning, productivity, etc.) defines its own algebra
    that maps the abstract Tetrad to concrete measurements.
    """

    # METADATA
    name: str                           # e.g., "WASM_SURVIVORS", "DAILY_LAB", "LEARNING"
    description: str

    # CONTRAST: What dimensions vary in this domain?
    contrast_dimensions: tuple[ContrastDimension, ...]

    # ARC: What phases does this domain's experience traverse?
    arc_phases: tuple[ArcPhase, ...]
    canonical_transitions: tuple[tuple[ArcPhase, ArcPhase], ...]

    # VOICE: What quality perspectives matter in this domain?
    voices: tuple[VoiceDefinition, ...]

    # FLOOR: What are the non-negotiable must-haves?
    floor_checks: tuple[FloorCheckDefinition, ...]

    # EXPERIENCE TYPES: What are the nesting levels?
    experience_types: tuple[str, ...]   # e.g., ("Moment", "Wave", "Run", "Session")

    # WEIGHTS: How do dimensions combine?
    contrast_weight: float = 0.35       # alpha
    arc_weight: float = 0.35            # beta
    voice_weight: float = 0.30          # gamma

    def validate(self) -> list[str]:
        """Validate algebra consistency."""
        errors = []
        if not self.contrast_dimensions:
            errors.append("Algebra must define at least one contrast dimension")
        if not self.arc_phases:
            errors.append("Algebra must define at least one arc phase")
        if not self.voices:
            errors.append("Algebra must define at least one voice")
        if abs(self.contrast_weight + self.arc_weight + self.voice_weight - 1.0) > 0.001:
            errors.append("Weights must sum to 1.0")
        return errors


@dataclass(frozen=True)
class ContrastDimension:
    """A single dimension of contrast in a domain."""
    name: str               # e.g., "breath", "tempo", "stakes"
    description: str        # What this dimension measures
    curve_extractor: str    # How to extract this curve from experience
    weight: float = 1.0     # Relative importance


@dataclass(frozen=True)
class ArcPhase:
    """A single phase in the domain's emotional/engagement arc."""
    name: str               # e.g., "HOPE", "FLOW", "CRISIS"
    description: str        # What this phase feels like
    classifier: str         # How to classify a moment into this phase
    required: bool = False  # Must this phase be visited for full coverage?


@dataclass(frozen=True)
class VoiceDefinition:
    """A single quality perspective/voice."""
    name: str               # e.g., "adversarial", "creative", "advocate"
    question: str           # What this voice asks
    checker: str            # Function to check this voice
    weight: float = 1.0     # Relative importance


@dataclass(frozen=True)
class FloorCheckDefinition:
    """A single floor check."""
    name: str               # e.g., "input_latency", "feedback_density"
    description: str
    threshold: float
    comparison: str         # "<=", ">=", "=="
    unit: str               # e.g., "ms", "ratio", "bool"
```

### 1.3 ExperienceQuality Type

The fundamental quality measurement, parameterized by a domain algebra:

```python
@dataclass(frozen=True)
class ExperienceQuality[A: QualityAlgebra]:
    """
    The fundamental quality measurement.

    Parameterized by a QualityAlgebra that defines domain-specific
    dimensions, phases, voices, and checks.
    """

    # Continuous metrics
    contrast: float                     # C in [0, 1]
    arc_coverage: float                 # A in [0, 1]

    # Discrete metrics (length determined by algebra)
    voice_verdicts: tuple[bool, ...]    # V = (v_1, v_2, ..., v_n)

    # Gate
    floor_passed: bool                  # F in {0, 1}

    # Reference to algebra
    algebra_name: str

    @property
    def voice_alignment(self) -> float:
        """Voice alignment as continuous signal."""
        if not self.voice_verdicts:
            return 1.0  # No voices defined = trivially aligned
        return sum(self.voice_verdicts) / len(self.voice_verdicts)

    @property
    def overall(self) -> float:
        """
        Overall quality score.

        Q = F * (alpha*C + beta*A + gamma*V)

        Floor is multiplicative (gate), others are weighted sum.
        Default weights: alpha=0.35, beta=0.35, gamma=0.30
        """
        if not self.floor_passed:
            return 0.0

        # Note: Weights can be retrieved from algebra if needed
        alpha, beta, gamma = 0.35, 0.35, 0.30
        return alpha * self.contrast + beta * self.arc_coverage + gamma * self.voice_alignment

    @classmethod
    def unit(cls, algebra_name: str, num_voices: int) -> "ExperienceQuality":
        """The unit quality (identity element)."""
        return cls(
            contrast=1.0,
            arc_coverage=1.0,
            voice_verdicts=tuple([True] * num_voices),
            floor_passed=True,
            algebra_name=algebra_name,
        )

    @classmethod
    def zero(cls, algebra_name: str, num_voices: int) -> "ExperienceQuality":
        """The zero quality (floor failed)."""
        return cls(
            contrast=0.0,
            arc_coverage=0.0,
            voice_verdicts=tuple([False] * num_voices),
            floor_passed=False,
            algebra_name=algebra_name,
        )
```

### 1.4 Detailed Measurement Types

```python
@dataclass(frozen=True)
class ContrastMeasurement:
    """
    Detailed contrast breakdown.

    Dimensions are determined by the QualityAlgebra.
    """

    dimension_scores: dict[str, float]  # dimension_name -> score in [0, 1]

    @property
    def overall(self) -> float:
        """Aggregate contrast score (mean of dimensions)."""
        if not self.dimension_scores:
            return 0.0
        return sum(self.dimension_scores.values()) / len(self.dimension_scores)

    @property
    def weakest_dimension(self) -> str | None:
        """Identify the contrast bottleneck."""
        if not self.dimension_scores:
            return None
        return min(self.dimension_scores, key=self.dimension_scores.get)

    def weighted_overall(self, weights: dict[str, float]) -> float:
        """Weighted aggregate contrast score."""
        if not self.dimension_scores:
            return 0.0
        total_weight = sum(weights.get(d, 1.0) for d in self.dimension_scores)
        return sum(
            self.dimension_scores[d] * weights.get(d, 1.0)
            for d in self.dimension_scores
        ) / total_weight


@dataclass(frozen=True)
class ArcMeasurement:
    """
    Emotional/engagement arc coverage.

    Phases are determined by the QualityAlgebra.
    """

    phases_visited: frozenset[str]              # Phase names visited
    phase_durations: dict[str, float]           # Phase -> seconds spent
    transitions: tuple[tuple[str, str], ...]    # (from_phase, to_phase) sequence

    required_phases: frozenset[str]             # Phases required for full coverage
    endpoint_phases: frozenset[str]             # Valid ending phases
    canonical_transitions: frozenset[tuple[str, str]]  # Expected transitions

    @property
    def coverage(self) -> float:
        """
        Arc coverage score.

        Full coverage = visited all required phases and ended properly.
        """
        if not self.required_phases:
            return 1.0  # No requirements = full coverage

        required_coverage = len(self.required_phases & self.phases_visited) / len(self.required_phases)
        has_endpoint = bool(self.endpoint_phases & self.phases_visited)

        return required_coverage * 0.7 + (0.3 if has_endpoint else 0.0)

    @property
    def shape_quality(self) -> float:
        """
        Quality of the arc shape.

        Good arcs follow canonical transitions.
        """
        if not self.transitions:
            return 0.0

        canonical_count = sum(1 for t in self.transitions if t in self.canonical_transitions)
        return canonical_count / len(self.transitions)


@dataclass(frozen=True)
class VoiceVerdict:
    """A single voice's verdict."""
    voice_name: str
    passed: bool
    confidence: float       # [0, 1]
    reasoning: str
    violations: tuple[str, ...]


@dataclass(frozen=True)
class VoiceMeasurement:
    """
    Multi-voice quality assessment.

    Voices are determined by the QualityAlgebra.
    """

    verdicts: tuple[VoiceVerdict, ...]

    @property
    def aligned(self) -> bool:
        """All voices approve."""
        return all(v.passed for v in self.verdicts)

    @property
    def alignment_score(self) -> float:
        """Continuous alignment score."""
        if not self.verdicts:
            return 1.0
        return sum(v.confidence * v.passed for v in self.verdicts) / len(self.verdicts)

    def get_verdict(self, voice_name: str) -> VoiceVerdict | None:
        """Get verdict for a specific voice."""
        for v in self.verdicts:
            if v.voice_name == voice_name:
                return v
        return None


@dataclass(frozen=True)
class FloorCheck:
    """A single floor check result."""
    name: str
    passed: bool
    measurement: float      # The actual value
    threshold: float        # The required value
    comparison: str         # "<=", ">=", "=="
    unit: str


@dataclass(frozen=True)
class FloorMeasurement:
    """The floor gate assessment."""

    checks: tuple[FloorCheck, ...]

    @property
    def passed(self) -> bool:
        """All floor checks must pass."""
        return all(check.passed for check in self.checks)

    @property
    def failures(self) -> tuple[str, ...]:
        """Which checks failed."""
        return tuple(c.name for c in self.checks if not c.passed)

    @property
    def pass_ratio(self) -> float:
        """Proportion of checks that passed."""
        if not self.checks:
            return 1.0
        return sum(1 for c in self.checks if c.passed) / len(self.checks)
```

---

## Part II: Composition Laws

The Experience Quality Operad defines three fundamental composition operations.

### 2.1 Sequential Composition (A >> B)

When experience A is followed by experience B:

```python
def sequential_compose(
    q_a: ExperienceQuality,
    q_b: ExperienceQuality,
    transition_contrast: float = 0.0,  # Measured contrast between A and B
) -> ExperienceQuality:
    """
    Sequential composition: A then B.

    SEMANTICS:
    - Contrast: INCREASES with variety between A and B (transition adds contrast)
    - Arc: Phases CHAIN (A's arc + B's arc + transition)
    - Voice: Both must pass for most voices (AND); some voices use OR (one saves)
    - Floor: Both must pass (AND)

    LAW: (A >> B) >> C = A >> (B >> C) [Associative]
    """
    assert q_a.algebra_name == q_b.algebra_name, "Cannot compose different algebras"

    # Contrast includes transition variety
    combined_contrast = (q_a.contrast + q_b.contrast + transition_contrast) / 3

    # Arc phases chain
    combined_arc = chain_arc_coverage(q_a.arc_coverage, q_b.arc_coverage)

    # Voices: AND for required voices, OR for at-least-one voices
    # Default: AND for all except "creative" type voices
    combined_voices = tuple(
        q_a.voice_verdicts[i] and q_b.voice_verdicts[i]
        for i in range(len(q_a.voice_verdicts))
    )

    return ExperienceQuality(
        contrast=combined_contrast,
        arc_coverage=combined_arc,
        voice_verdicts=combined_voices,
        floor_passed=q_a.floor_passed and q_b.floor_passed,
        algebra_name=q_a.algebra_name,
    )


def chain_arc_coverage(a: float, b: float) -> float:
    """
    Chain two arc coverages.

    Not simple averaging: if both arcs are partial but complementary,
    the combined coverage can exceed either individual coverage.
    """
    # Optimistic chaining: if A covers 50% and B covers 50% of DIFFERENT phases,
    # combined could be up to 100%
    return min(1.0, a + b * (1 - a))
```

### 2.2 Parallel Composition (A || B)

When experiences A and B happen simultaneously:

```python
def parallel_compose(
    q_a: ExperienceQuality,
    q_b: ExperienceQuality,
) -> ExperienceQuality:
    """
    Parallel composition: A and B simultaneously.

    USE CASES: Multi-track experiences, layered systems, simultaneous activities.

    SEMANTICS:
    - Contrast: MAX (dominant track determines variety)
    - Arc: Weighted mean (both contribute to journey)
    - Voice: AND (both must satisfy voices)
    - Floor: AND (both must pass floor)

    LAW: (A || B) || C = A || (B || C) [Associative]
    LAW: A || B = B || A [Commutative]
    """
    assert q_a.algebra_name == q_b.algebra_name, "Cannot compose different algebras"

    return ExperienceQuality(
        contrast=max(q_a.contrast, q_b.contrast),
        arc_coverage=q_a.arc_coverage * q_b.arc_coverage,
        voice_verdicts=tuple(
            q_a.voice_verdicts[i] and q_b.voice_verdicts[i]
            for i in range(len(q_a.voice_verdicts))
        ),
        floor_passed=q_a.floor_passed and q_b.floor_passed,
        algebra_name=q_a.algebra_name,
    )
    # NOTE: Product composition ensures strict associativity
    # while preserving floor gate semantics (0 × x = 0).
    # See: brainstorming/empirical-refinement-v2/discoveries/02-associativity-fix.md
```

### 2.3 Nested Composition (A[B])

When experience B is nested inside experience A:

```python
def nested_compose(
    q_outer: ExperienceQuality,
    q_inner: ExperienceQuality,
    outer_weight: float = 0.7,  # How much outer dominates
) -> ExperienceQuality:
    """
    Nested composition: B inside A.

    USE CASES:
    - Runs inside sessions
    - Waves inside runs
    - Moments inside waves
    - Tasks inside projects

    SEMANTICS:
    - Contrast: Weighted blend (outer dominates)
    - Arc: Weighted blend (outer dominates)
    - Voice: Outer decides "structural" voices, inner decides "granular" voices
    - Floor: Both must pass

    NOTE: The outer_weight parameter allows tuning how much the container
    vs contained experience determines quality.
    """
    assert q_outer.algebra_name == q_inner.algebra_name, "Cannot compose different algebras"

    alpha = outer_weight

    return ExperienceQuality(
        contrast=alpha * q_outer.contrast + (1-alpha) * q_inner.contrast,
        arc_coverage=alpha * q_outer.arc_coverage + (1-alpha) * q_inner.arc_coverage,
        voice_verdicts=tuple(
            # First voice: outer decides, last voice: inner decides
            # Middle voices: AND
            q_outer.voice_verdicts[i] if i == 0
            else q_inner.voice_verdicts[i] if i == len(q_outer.voice_verdicts) - 1
            else q_outer.voice_verdicts[i] and q_inner.voice_verdicts[i]
            for i in range(len(q_outer.voice_verdicts))
        ),
        floor_passed=q_outer.floor_passed and q_inner.floor_passed,
        algebra_name=q_outer.algebra_name,
    )
```

### 2.4 Operad Laws

The composition operations satisfy these laws:

```python
EXPERIENCE_QUALITY_OPERAD = Operad(
    name="ExperienceQualityOperad",
    operations={
        "sequential": sequential_compose,
        "parallel": parallel_compose,
        "nested": nested_compose,
    },
    laws=[
        # IDENTITY
        Law(
            "identity",
            "measure(Id) = Quality.unit()",
            "Identity experience has unit quality",
        ),

        # ASSOCIATIVITY
        Law(
            "assoc_seq",
            "(A >> B) >> C = A >> (B >> C)",
            "Sequential composition is associative",
        ),
        Law(
            "assoc_par",
            "(A || B) || C = A || (B || C)",
            "Parallel composition is strictly associative (product semantics for arc)",
        ),

        # COMMUTATIVITY
        Law(
            "commut_par",
            "A || B = B || A",
            "Parallel composition is commutative",
        ),

        # FLOOR GATE
        Law(
            "floor_gate",
            "F=0 => Q=0",
            "Floor failure zeros quality",
        ),

        # CONTRAST PRESERVATION
        Law(
            "contrast_mono",
            "C(A >> B) >= max(C(A), C(B)) - epsilon",
            "Composition preserves contrast (approximately)",
        ),

        # ARC CHAINING
        Law(
            "arc_chain",
            "A(X >> Y) = chain(A(X), A(Y))",
            "Arcs chain, not average",
        ),

        # DISTRIBUTIVITY
        Law(
            "distrib_nested_seq",
            "(A >> B)[C] = A[C] >> B",
            "Nested distributes over sequential (partially)",
            note="Only when C affects all of A >> B uniformly",
        ),
    ],
)
```

---

## Part III: Witness Integration

### 3.1 Quality Marks

Every quality measurement creates a witness mark:

```python
@dataclass(frozen=True)
class QualityMark(Mark):
    """
    A witness mark for experience quality.

    Extends the standard Mark with quality-specific fields.
    """

    # Standard mark fields
    origin: str = "experience-quality-operad"

    # Quality measurement
    quality: ExperienceQuality
    contrast_detail: ContrastMeasurement
    arc_detail: ArcMeasurement
    voice_detail: VoiceMeasurement
    floor_detail: FloorMeasurement

    # Experience metadata
    experience_id: str
    experience_type: str            # From algebra's experience_types
    algebra_name: str
    duration_seconds: float

    # Diagnosis
    bottleneck: str                 # Which dimension is weakest
    recommendation: str             # How to improve


async def witness_quality[A: QualityAlgebra](
    experience: Experience,
    algebra: A,
    spec: Spec | None = None,
) -> QualityMark:
    """
    Witness the quality of an experience.

    Creates an immutable mark that records:
    - What the quality was
    - Why it was that quality (detailed measurements)
    - How to improve (recommendation)

    The algebra determines how to measure each dimension.
    """
    # Measure each dimension using algebra-specific methods
    contrast = measure_contrast(experience, algebra)
    arc = measure_arc(experience, algebra)
    voice = check_voice(experience, algebra, spec)
    floor = check_floor(experience, algebra)

    # Build the composite quality
    quality = ExperienceQuality(
        contrast=contrast.overall,
        arc_coverage=arc.coverage,
        voice_verdicts=tuple(v.passed for v in voice.verdicts),
        floor_passed=floor.passed,
        algebra_name=algebra.name,
    )

    # Identify bottleneck and generate recommendation
    bottleneck = identify_bottleneck(quality, contrast, arc, voice, floor)
    recommendation = generate_recommendation(bottleneck, algebra)

    mark = QualityMark(
        quality=quality,
        contrast_detail=contrast,
        arc_detail=arc,
        voice_detail=voice,
        floor_detail=floor,
        experience_id=experience.id,
        experience_type=experience.type,
        algebra_name=algebra.name,
        duration_seconds=experience.duration,
        bottleneck=bottleneck,
        recommendation=recommendation,
    )

    await emit_mark(mark)
    return mark


def identify_bottleneck(
    quality: ExperienceQuality,
    contrast: ContrastMeasurement,
    arc: ArcMeasurement,
    voice: VoiceMeasurement,
    floor: FloorMeasurement,
) -> str:
    """
    Identify the primary quality bottleneck.

    Priority: Floor > Voice > Arc > Contrast
    """
    # Floor failures are critical
    if not floor.passed:
        failures = floor.failures
        return f"floor:{failures[0]}" if failures else "floor:unknown"

    # Voice alignment issues
    if not voice.aligned:
        failed_voices = [v.voice_name for v in voice.verdicts if not v.passed]
        return f"voice:{failed_voices[0]}" if failed_voices else "voice:unknown"

    # Arc coverage
    if arc.coverage < 0.5:
        return "arc:incomplete"

    # Contrast dimensions
    if contrast.overall < 0.3:
        weak = contrast.weakest_dimension
        return f"contrast:{weak}" if weak else "contrast:flat"

    return "none"  # No significant bottleneck
```

### 3.2 Quality Crystals

Quality marks crystallize into quality crystals:

```python
@dataclass(frozen=True)
class QualityCrystal(Crystal):
    """
    Compressed quality proof for a collection of experiences.

    Crystals aggregate multiple marks into actionable insight.
    """

    # Algebra reference
    algebra_name: str

    # Summary metrics
    overall_quality: float
    quality_trend: Literal["improving", "stable", "declining"]

    # Dimension summaries (human-readable)
    contrast_summary: str
    arc_summary: str
    voice_summary: str
    floor_summary: str

    # Key moments
    quality_peaks: tuple[QualityMoment, ...]      # Best moments
    quality_troughs: tuple[QualityMoment, ...]    # Worst moments

    # Recommendations (prioritized)
    primary_recommendation: str
    secondary_recommendations: tuple[str, ...]

    # Compression metadata
    source_mark_count: int
    compression_ratio: float
    time_span_seconds: float


@dataclass(frozen=True)
class QualityMoment:
    """A significant moment in the quality timeline."""
    experience_id: str
    quality_score: float
    timestamp: float
    description: str


async def crystallize_quality(
    marks: list[QualityMark],
    algebra: QualityAlgebra,
) -> QualityCrystal:
    """
    Compress quality marks into a crystal.

    The crystal provides:
    - Aggregate quality assessment
    - Trend analysis
    - Key moments (peaks and troughs)
    - Prioritized recommendations
    """
    if not marks:
        raise ValueError("Cannot crystallize empty mark list")

    # Aggregate quality
    qualities = [m.quality for m in marks]
    overall = sum(q.overall for q in qualities) / len(qualities)

    # Trend analysis
    trend = compute_quality_trend(qualities)

    # Find peaks and troughs
    sorted_by_quality = sorted(marks, key=lambda m: m.quality.overall)
    troughs = sorted_by_quality[:3]
    peaks = sorted_by_quality[-3:]

    # Generate summaries
    contrast_summary = summarize_contrast_marks([m.contrast_detail for m in marks], algebra)
    arc_summary = summarize_arc_marks([m.arc_detail for m in marks], algebra)
    voice_summary = summarize_voice_marks([m.voice_detail for m in marks], algebra)
    floor_summary = summarize_floor_marks([m.floor_detail for m in marks], algebra)

    # Generate recommendations from bottleneck analysis
    primary, secondary = generate_crystal_recommendations(marks, algebra)

    return QualityCrystal(
        algebra_name=algebra.name,
        overall_quality=overall,
        quality_trend=trend,
        contrast_summary=contrast_summary,
        arc_summary=arc_summary,
        voice_summary=voice_summary,
        floor_summary=floor_summary,
        quality_peaks=tuple(to_quality_moment(m) for m in peaks),
        quality_troughs=tuple(to_quality_moment(m) for m in troughs),
        primary_recommendation=primary,
        secondary_recommendations=secondary,
        source_mark_count=len(marks),
        compression_ratio=len(marks) / 1,
        time_span_seconds=compute_time_span(marks),
    )


def compute_quality_trend(qualities: list[ExperienceQuality]) -> Literal["improving", "stable", "declining"]:
    """
    Compute the quality trend over time.
    """
    if len(qualities) < 3:
        return "stable"

    third = len(qualities) // 3
    early = sum(q.overall for q in qualities[:third]) / third
    late = sum(q.overall for q in qualities[-third:]) / third

    if late > early + 0.05:
        return "improving"
    elif late < early - 0.05:
        return "declining"
    else:
        return "stable"
```

---

## Part IV: Domain Algebra Schema

### 4.1 Defining a Domain Algebra

To instantiate the EQO for a specific domain, define a QualityAlgebra:

```python
# Example: A minimal learning domain algebra

LEARNING_QUALITY_ALGEBRA = QualityAlgebra(
    name="LEARNING",
    description="Quality algebra for educational experiences",

    # Contrast: What varies in learning?
    contrast_dimensions=(
        ContrastDimension("difficulty", "Oscillation between easy and challenging", "difficulty_curve"),
        ContrastDimension("novelty", "New concepts vs. reinforcement", "novelty_curve"),
        ContrastDimension("modality", "Different learning modes (read/watch/do)", "modality_curve"),
    ),

    # Arc: What phases does learning traverse?
    arc_phases=(
        ArcPhase("curiosity", "Initial interest", "detect_curiosity", required=True),
        ArcPhase("struggle", "Productive difficulty", "detect_struggle", required=True),
        ArcPhase("insight", "Aha moment", "detect_insight", required=False),
        ArcPhase("mastery", "Successful application", "detect_mastery", required=True),
        ArcPhase("plateau", "Boredom or frustration", "detect_plateau", required=False),
    ),
    canonical_transitions=(
        ("curiosity", "struggle"),
        ("struggle", "insight"),
        ("insight", "mastery"),
        ("struggle", "plateau"),
        ("plateau", "curiosity"),  # Recovery
    ),

    # Voice: What perspectives matter?
    voices=(
        VoiceDefinition("pedagogical", "Is it teaching effectively?", "check_pedagogical"),
        VoiceDefinition("engaging", "Is it holding attention?", "check_engaging"),
        VoiceDefinition("applicable", "Is it practically useful?", "check_applicable"),
    ),

    # Floor: Non-negotiables for learning
    floor_checks=(
        FloorCheckDefinition("comprehension_possible", "Can the learner understand?", 0.6, ">=", "ratio"),
        FloorCheckDefinition("feedback_latency", "Feedback within timeout?", 30.0, "<=", "seconds"),
        FloorCheckDefinition("progress_visible", "Is progress trackable?", 1.0, "==", "bool"),
    ),

    experience_types=("moment", "lesson", "module", "course"),
)
```

### 4.2 Algebra Registry Pattern

Algebras are registered globally for discovery and composition:

```python
class AlgebraRegistry:
    """
    Registry of domain-specific quality algebras.

    Allows:
    - Discovery of available algebras
    - Cross-domain quality comparison (when algebras are compatible)
    - Composition of multi-domain experiences
    """

    _algebras: dict[str, QualityAlgebra] = {}

    @classmethod
    def register(cls, algebra: QualityAlgebra) -> None:
        """Register an algebra."""
        errors = algebra.validate()
        if errors:
            raise ValueError(f"Invalid algebra {algebra.name}: {errors}")
        cls._algebras[algebra.name] = algebra

    @classmethod
    def get(cls, name: str) -> QualityAlgebra:
        """Get an algebra by name."""
        if name not in cls._algebras:
            raise KeyError(f"Unknown algebra: {name}. Available: {list(cls._algebras.keys())}")
        return cls._algebras[name]

    @classmethod
    def list_algebras(cls) -> list[str]:
        """List all registered algebras."""
        return list(cls._algebras.keys())

    @classmethod
    def compatible(cls, a: str, b: str) -> bool:
        """
        Check if two algebras are compatible for cross-domain comparison.

        Algebras are compatible if they have the same number of voices
        and similar floor check structures.
        """
        alg_a = cls.get(a)
        alg_b = cls.get(b)
        return len(alg_a.voices) == len(alg_b.voices)


# Registration happens at module load
AlgebraRegistry.register(LEARNING_QUALITY_ALGEBRA)
# AlgebraRegistry.register(WASM_QUALITY_ALGEBRA)  # See domains/wasm-survivors-quality.md
# AlgebraRegistry.register(PRODUCTIVITY_QUALITY_ALGEBRA)
# etc.
```

### 4.3 Domain-Specific Measurement Functions

Each algebra provides its own measurement implementations:

```python
def measure_contrast(experience: Experience, algebra: QualityAlgebra) -> ContrastMeasurement:
    """
    Measure contrast using algebra-defined dimensions.

    For each dimension, measure the VARIANCE of the signal over time.
    High variance = high contrast = good.
    Low variance = monotony = bad.
    """
    timeline = experience.to_timeline()

    dimension_scores = {}
    for dim in algebra.contrast_dimensions:
        curve = extract_curve(timeline, dim.curve_extractor)
        dimension_scores[dim.name] = variance_normalized(curve) * dim.weight

    # Normalize weights
    total_weight = sum(d.weight for d in algebra.contrast_dimensions)
    dimension_scores = {k: v / total_weight for k, v in dimension_scores.items()}

    return ContrastMeasurement(dimension_scores=dimension_scores)


def measure_arc(experience: Experience, algebra: QualityAlgebra) -> ArcMeasurement:
    """
    Measure arc coverage using algebra-defined phases.
    """
    timeline = experience.to_timeline()

    phases_visited = set()
    phase_durations = defaultdict(float)
    transitions = []

    current_phase = None
    for moment in timeline.moments:
        phase = classify_phase(moment, algebra)
        phases_visited.add(phase)
        phase_durations[phase] += moment.duration

        if current_phase and phase != current_phase:
            transitions.append((current_phase, phase))
        current_phase = phase

    required = frozenset(p.name for p in algebra.arc_phases if p.required)
    endpoints = frozenset(p.name for p in algebra.arc_phases if not p.required)

    return ArcMeasurement(
        phases_visited=frozenset(phases_visited),
        phase_durations=dict(phase_durations),
        transitions=tuple(transitions),
        required_phases=required,
        endpoint_phases=endpoints,
        canonical_transitions=frozenset(algebra.canonical_transitions),
    )


def check_voice(
    experience: Experience,
    algebra: QualityAlgebra,
    spec: Spec | None = None,
) -> VoiceMeasurement:
    """
    Check experience against algebra-defined voices.
    """
    verdicts = []
    for voice_def in algebra.voices:
        checker = get_voice_checker(voice_def.checker)
        verdict = checker(experience, spec)
        verdicts.append(VoiceVerdict(
            voice_name=voice_def.name,
            passed=verdict.passed,
            confidence=verdict.confidence,
            reasoning=verdict.reasoning,
            violations=verdict.violations,
        ))

    return VoiceMeasurement(verdicts=tuple(verdicts))


def check_floor(experience: Experience, algebra: QualityAlgebra) -> FloorMeasurement:
    """
    Check experience against algebra-defined floor checks.
    """
    checks = []
    for check_def in algebra.floor_checks:
        measurement = measure_floor_dimension(experience, check_def.name)
        passed = meets_threshold(measurement, check_def.threshold, check_def.comparison)
        checks.append(FloorCheck(
            name=check_def.name,
            passed=passed,
            measurement=measurement,
            threshold=check_def.threshold,
            comparison=check_def.comparison,
            unit=check_def.unit,
        ))

    return FloorMeasurement(checks=tuple(checks))
```

### 4.4 Cross-References to Domain Files

Domain-specific algebras are defined in:

| Domain | File | Status |
|--------|------|--------|
| WASM Survivors | `spec/theory/domains/wasm-survivors-quality.md` | Active |
| Daily Lab | `spec/theory/domains/daily-lab-quality.md` | Planned |
| Learning | `spec/theory/domains/learning-quality.md` | Planned |
| Productivity | `spec/theory/domains/productivity-quality.md` | Planned |

---

## Part V: API Surface

### 5.1 Core Functions

```python
# Algebra management
def register_algebra(algebra: QualityAlgebra) -> None
def get_algebra(name: str) -> QualityAlgebra
def list_algebras() -> list[str]

# Measurement
async def measure_quality[A: QualityAlgebra](experience: Experience, algebra: A) -> ExperienceQuality
async def measure_contrast[A: QualityAlgebra](experience: Experience, algebra: A) -> ContrastMeasurement
async def measure_arc[A: QualityAlgebra](experience: Experience, algebra: A) -> ArcMeasurement
async def check_voice[A: QualityAlgebra](experience: Experience, algebra: A, spec: Spec | None) -> VoiceMeasurement
async def check_floor[A: QualityAlgebra](experience: Experience, algebra: A) -> FloorMeasurement

# Witnessing
async def witness_quality[A: QualityAlgebra](experience: Experience, algebra: A, spec: Spec | None) -> QualityMark
async def crystallize_quality(marks: list[QualityMark], algebra: QualityAlgebra) -> QualityCrystal

# Composition
def sequential_compose(q1: ExperienceQuality, q2: ExperienceQuality) -> ExperienceQuality
def parallel_compose(q1: ExperienceQuality, q2: ExperienceQuality) -> ExperienceQuality
def nested_compose(outer: ExperienceQuality, inner: ExperienceQuality) -> ExperienceQuality

# Utilities
def identify_bottleneck(quality: ExperienceQuality, ...) -> str
def generate_recommendation(bottleneck: str, algebra: QualityAlgebra) -> str
```

### 5.2 AGENTESE Paths

```
# Algebra management
concept.quality.algebra.list                    # List registered algebras
concept.quality.algebra.{name}                  # Get algebra definition

# Measurement (parameterized by algebra)
concept.quality.measure.{algebra}.{experience_type}     # Measure quality
concept.quality.contrast.{algebra}.{experience_type}    # Measure contrast
concept.quality.arc.{algebra}.{experience_type}         # Measure arc
concept.quality.voice.{algebra}.{experience_type}       # Check voices
concept.quality.floor.{algebra}.{experience_type}       # Check floor

# Witnessing
self.quality.witness.{algebra}.{experience_id}          # Witness quality
self.quality.crystallize.{algebra}.{experience_id}      # Crystallize marks

# Domain-specific (registered by domain modules)
world.wasm.quality.monitor                              # WASM Survivors monitor
world.learning.quality.assess                           # Learning assessment
# etc.
```

---

## Appendix A: Mathematical Foundations

### A.1 Operad Category

The EQO is an operad in the category **Exp** of experiences:

- **Objects**: Experience types (parameterized by algebra: Moment, Segment, Session, ...)
- **Morphisms**: Experience transformations
- **Composition**: Sequential (>>), Parallel (||), Nested ([])

### A.2 Quality as Functor

Quality measurement is a functor:

```
Q: Exp -> Qual

where:
  Q(experience) = ExperienceQuality
  Q(f >> g) = sequential_compose(Q(f), Q(g))
  Q(f || g) = parallel_compose(Q(f), Q(g))
  Q(f[g]) = nested_compose(Q(f), Q(g))
```

This functoriality ensures that quality measurement is compositional.

### A.3 Algebra as Natural Transformation

A QualityAlgebra is a natural transformation:

```
alpha: Id_Domain -> Q_Universal

For each domain D with algebra A:
  alpha_A: D -> Qual

  Such that for any domain morphism f: D -> D':
    Q_Universal . f = alpha_A' . f
```

This ensures that domain algebras are consistent with the universal framework.

### A.4 Fixed Points

The quality of a self-referential experience (one that measures its own quality) is a Lawvere fixed point:

```
Q(measure(Q(e))) = Q(e)
```

This ensures quality measurement doesn't change quality — measurement is observation without interference.

### A.5 Floor as Monoidal Unit

The floor dimension acts as a monoidal unit:

```
F = 0 => Q = 0 (annihilation)
F = 1 => Q = alpha*C + beta*A + gamma*V (identity modulo floor)
```

This gives the quality space a semiring structure where floor is the multiplicative zero.

---

## Cross-References

- `spec/principles/CONSTITUTION.md` — The seven principles
- `spec/protocols/witness-primitives.md` — Mark and Crystal structures
- `spec/theory/analysis-operad.md` — Four-mode analysis
- `spec/theory/domains/wasm-survivors-quality.md` — WASM Survivors domain binding
- `docs/skills/metaphysical-fullstack.md` — Architecture patterns

---

*"Quality is not a number. It is a structure. The structure composes. The algebra instantiates."*
