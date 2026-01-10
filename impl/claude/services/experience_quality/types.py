"""
Experience Quality Operad: Core Types.

The fundamental dataclasses for measuring and composing experiential quality.

The Quality Tetrad:
- Contrast (C): Does this experience have variety? [0, 1]
- Arc (A): Does this experience have shape? [0, 1]
- Voice (V): Is this correct, interesting, AND fun? {0, 1}^3
- Floor (F): Is this experience worth having? {0, 1}

Philosophy:
    "Quality of experience is measurable, composable, and witnessable."

    Experience quality is not a single number but a structured object
    with composition laws. Two experiences compose, and their combined
    quality is derivable from their individual qualities plus interaction terms.

See: spec/theory/experience-quality-operad.md
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any

# =============================================================================
# EmotionalPhase Enum (for Arc measurement)
# =============================================================================


class EmotionalPhase(Enum):
    """
    The five phases of the emotional arc.

    A complete emotional journey visits:
    - HOPE -> FLOW -> CRISIS -> (TRIUMPH or GRIEF)

    TRIUMPH and GRIEF are mutually exclusive endpoints.
    """

    HOPE = "hope"  # "I can do this"
    FLOW = "flow"  # "I'm unstoppable"
    CRISIS = "crisis"  # "Oh no, maybe not"
    TRIUMPH = "triumph"  # "I DID IT!"
    GRIEF = "grief"  # "So close..."


# =============================================================================
# ContrastMeasurement: The Seven Contrast Dimensions
# =============================================================================


@dataclass(frozen=True)
class ContrastMeasurement:
    """
    Detailed contrast breakdown across seven dimensions.

    Each dimension measures the variance of a signal over time.
    High variance = high contrast = good.
    Low variance = monotony = bad.

    Derived from WASM Survivors C1-C7.
    """

    breath: float = 0.5  # C1: Intensity oscillation (crescendo <-> silence)
    scarcity: float = 0.5  # C2: Resource oscillation (feast <-> famine)
    tempo: float = 0.5  # C3: Speed oscillation (fast <-> slow)
    stakes: float = 0.5  # C4: Risk oscillation (safe <-> lethal)
    anticipation: float = 0.5  # C5: Tension oscillation (calm <-> dread)
    reward: float = 0.5  # C6: Gratification oscillation (drought <-> burst)
    identity: float = 0.5  # C7: Choice oscillation (exploration <-> commitment)

    def __post_init__(self) -> None:
        """Validate all dimensions are in [0, 1]."""
        for dim in (
            "breath",
            "scarcity",
            "tempo",
            "stakes",
            "anticipation",
            "reward",
            "identity",
        ):
            value = getattr(self, dim)
            if not 0.0 <= value <= 1.0:
                object.__setattr__(self, dim, max(0.0, min(1.0, value)))

    @property
    def overall(self) -> float:
        """Aggregate contrast score (mean of all dimensions)."""
        dimensions = [
            self.breath,
            self.scarcity,
            self.tempo,
            self.stakes,
            self.anticipation,
            self.reward,
            self.identity,
        ]
        return sum(dimensions) / len(dimensions)

    @property
    def weakest_dimension(self) -> str:
        """Identify the contrast bottleneck."""
        dims = {
            "breath": self.breath,
            "scarcity": self.scarcity,
            "tempo": self.tempo,
            "stakes": self.stakes,
            "anticipation": self.anticipation,
            "reward": self.reward,
            "identity": self.identity,
        }
        return min(dims, key=lambda k: dims[k])

    @property
    def strongest_dimension(self) -> str:
        """Identify the highest contrast dimension."""
        dims = {
            "breath": self.breath,
            "scarcity": self.scarcity,
            "tempo": self.tempo,
            "stakes": self.stakes,
            "anticipation": self.anticipation,
            "reward": self.reward,
            "identity": self.identity,
        }
        return max(dims, key=lambda k: dims[k])

    def to_dict(self) -> dict[str, float | str]:
        """Convert to dictionary for serialization."""
        return {
            "breath": self.breath,
            "scarcity": self.scarcity,
            "tempo": self.tempo,
            "stakes": self.stakes,
            "anticipation": self.anticipation,
            "reward": self.reward,
            "identity": self.identity,
            "overall": self.overall,
            "weakest_dimension": self.weakest_dimension,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContrastMeasurement:
        """Create from dictionary."""
        return cls(
            breath=data.get("breath", 0.5),
            scarcity=data.get("scarcity", 0.5),
            tempo=data.get("tempo", 0.5),
            stakes=data.get("stakes", 0.5),
            anticipation=data.get("anticipation", 0.5),
            reward=data.get("reward", 0.5),
            identity=data.get("identity", 0.5),
        )

    @classmethod
    def neutral(cls) -> ContrastMeasurement:
        """Return a neutral contrast measurement (all 0.5)."""
        return cls()

    def __repr__(self) -> str:
        """Concise representation."""
        return f"ContrastMeasurement(overall={self.overall:.2f}, weakest={self.weakest_dimension})"


# =============================================================================
# ArcMeasurement: Emotional Arc Coverage
# =============================================================================


@dataclass(frozen=True)
class ArcMeasurement:
    """
    Emotional arc coverage measurement.

    Tracks which phases of the emotional journey were visited,
    how long was spent in each, and the quality of transitions.

    A good arc visits HOPE -> FLOW -> CRISIS -> (TRIUMPH or GRIEF).
    """

    phases_visited: frozenset[EmotionalPhase] = field(default_factory=frozenset)
    phase_durations: dict[EmotionalPhase, float] = field(
        default_factory=dict
    )  # Seconds in each phase
    transitions: tuple[tuple[EmotionalPhase, EmotionalPhase], ...] = ()

    @property
    def has_crisis(self) -> bool:
        """Critical: every good experience has a crisis."""
        return EmotionalPhase.CRISIS in self.phases_visited

    @property
    def has_resolution(self) -> bool:
        """Ends in TRIUMPH or GRIEF, not stuck in FLOW."""
        endpoints = {EmotionalPhase.TRIUMPH, EmotionalPhase.GRIEF}
        return bool(endpoints & self.phases_visited)

    @property
    def coverage(self) -> float:
        """
        Arc coverage score.

        Full coverage = visited HOPE, FLOW, CRISIS, and (TRIUMPH or GRIEF)
        """
        required = {EmotionalPhase.HOPE, EmotionalPhase.FLOW, EmotionalPhase.CRISIS}
        endpoint = {EmotionalPhase.TRIUMPH, EmotionalPhase.GRIEF}

        required_coverage = len(required & self.phases_visited) / len(required)
        has_endpoint = bool(endpoint & self.phases_visited)

        return required_coverage * 0.7 + (0.3 if has_endpoint else 0.0)

    @property
    def shape_quality(self) -> float:
        """
        Quality of the arc shape.

        Good arcs: HOPE -> FLOW -> CRISIS -> TRIUMPH/GRIEF
        Bad arcs: Random phase jumps, no crisis, stuck in middle
        """
        canonical = [
            (EmotionalPhase.HOPE, EmotionalPhase.FLOW),
            (EmotionalPhase.FLOW, EmotionalPhase.CRISIS),
            (EmotionalPhase.CRISIS, EmotionalPhase.TRIUMPH),
            (EmotionalPhase.CRISIS, EmotionalPhase.GRIEF),
        ]

        if not self.transitions:
            return 0.0

        canonical_count = sum(1 for t in self.transitions if t in canonical)
        return canonical_count / len(self.transitions)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "phases_visited": [p.value for p in self.phases_visited],
            "phase_durations": {p.value: d for p, d in self.phase_durations.items()},
            "transitions": [(a.value, b.value) for a, b in self.transitions],
            "has_crisis": self.has_crisis,
            "has_resolution": self.has_resolution,
            "coverage": self.coverage,
            "shape_quality": self.shape_quality,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ArcMeasurement:
        """Create from dictionary."""
        phases = frozenset(EmotionalPhase(p) for p in data.get("phases_visited", []))
        durations = {
            EmotionalPhase(k): v for k, v in data.get("phase_durations", {}).items()
        }
        transitions = tuple(
            (EmotionalPhase(a), EmotionalPhase(b))
            for a, b in data.get("transitions", [])
        )
        return cls(
            phases_visited=phases,
            phase_durations=durations,
            transitions=transitions,
        )

    @classmethod
    def empty(cls) -> ArcMeasurement:
        """Return an empty arc measurement."""
        return cls()

    def __repr__(self) -> str:
        """Concise representation."""
        phases = ",".join(p.value[:4] for p in sorted(self.phases_visited, key=lambda p: p.value))
        return f"ArcMeasurement(phases=[{phases}], coverage={self.coverage:.2f})"


# =============================================================================
# VoiceVerdict and VoiceMeasurement
# =============================================================================


@dataclass(frozen=True)
class VoiceVerdict:
    """A single voice's verdict on an experience."""

    passed: bool
    confidence: float  # [0, 1]
    reasoning: str
    violations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "passed": self.passed,
            "confidence": self.confidence,
            "reasoning": self.reasoning,
            "violations": list(self.violations),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VoiceVerdict:
        """Create from dictionary."""
        return cls(
            passed=data.get("passed", False),
            confidence=data.get("confidence", 0.0),
            reasoning=data.get("reasoning", ""),
            violations=tuple(data.get("violations", [])),
        )

    @classmethod
    def pass_verdict(cls, reasoning: str, confidence: float = 1.0) -> VoiceVerdict:
        """Create a passing verdict."""
        return cls(passed=True, confidence=confidence, reasoning=reasoning)

    @classmethod
    def fail_verdict(
        cls, reasoning: str, violations: tuple[str, ...], confidence: float = 1.0
    ) -> VoiceVerdict:
        """Create a failing verdict."""
        return cls(
            passed=False,
            confidence=confidence,
            reasoning=reasoning,
            violations=violations,
        )


@dataclass(frozen=True)
class VoiceMeasurement:
    """
    The three voices of quality.

    - Adversarial: Is this correct?
    - Creative: Is this interesting?
    - Advocate: Is this fun?
    """

    adversarial: VoiceVerdict
    creative: VoiceVerdict
    advocate: VoiceVerdict

    @property
    def aligned(self) -> bool:
        """All three voices approve."""
        return self.adversarial.passed and self.creative.passed and self.advocate.passed

    @property
    def alignment_score(self) -> float:
        """Continuous alignment score weighted by confidence."""
        scores = [
            self.adversarial.confidence if self.adversarial.passed else 0.0,
            self.creative.confidence if self.creative.passed else 0.0,
            self.advocate.confidence if self.advocate.passed else 0.0,
        ]
        return sum(scores) / 3

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "adversarial": self.adversarial.to_dict(),
            "creative": self.creative.to_dict(),
            "advocate": self.advocate.to_dict(),
            "aligned": self.aligned,
            "alignment_score": self.alignment_score,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VoiceMeasurement:
        """Create from dictionary."""
        return cls(
            adversarial=VoiceVerdict.from_dict(data.get("adversarial", {})),
            creative=VoiceVerdict.from_dict(data.get("creative", {})),
            advocate=VoiceVerdict.from_dict(data.get("advocate", {})),
        )

    @classmethod
    def all_pass(cls) -> VoiceMeasurement:
        """Create a measurement where all voices pass."""
        return cls(
            adversarial=VoiceVerdict.pass_verdict("All laws satisfied"),
            creative=VoiceVerdict.pass_verdict("Novel and surprising"),
            advocate=VoiceVerdict.pass_verdict("Engaging and fun"),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        status = "aligned" if self.aligned else "misaligned"
        return f"VoiceMeasurement({status}, score={self.alignment_score:.2f})"


# =============================================================================
# FloorCheck and FloorMeasurement
# =============================================================================


@dataclass(frozen=True)
class FloorCheck:
    """A single floor check (minimum quality gate)."""

    name: str
    passed: bool
    measurement: float  # The actual value
    threshold: float  # The required value
    unit: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "passed": self.passed,
            "measurement": self.measurement,
            "threshold": self.threshold,
            "unit": self.unit,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FloorCheck:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            passed=data.get("passed", False),
            measurement=data.get("measurement", 0.0),
            threshold=data.get("threshold", 0.0),
            unit=data.get("unit", ""),
        )


@dataclass(frozen=True)
class FloorMeasurement:
    """
    The fun floor gate.

    All floor checks must pass for the experience to be worth having.
    """

    checks: tuple[FloorCheck, ...]

    @property
    def passed(self) -> bool:
        """All floor checks must pass."""
        if not self.checks:
            return True  # No checks = pass by default
        return all(check.passed for check in self.checks)

    @property
    def failures(self) -> tuple[str, ...]:
        """Which checks failed."""
        return tuple(c.name for c in self.checks if not c.passed)

    @property
    def pass_rate(self) -> float:
        """Proportion of checks that passed."""
        if not self.checks:
            return 1.0
        return sum(1 for c in self.checks if c.passed) / len(self.checks)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "checks": [c.to_dict() for c in self.checks],
            "passed": self.passed,
            "failures": list(self.failures),
            "pass_rate": self.pass_rate,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FloorMeasurement:
        """Create from dictionary."""
        checks = tuple(FloorCheck.from_dict(c) for c in data.get("checks", []))
        return cls(checks=checks)

    @classmethod
    def empty(cls) -> FloorMeasurement:
        """Return an empty floor measurement (passes by default)."""
        return cls(checks=())

    def __repr__(self) -> str:
        """Concise representation."""
        status = "passed" if self.passed else f"failed({len(self.failures)})"
        return f"FloorMeasurement({status}, {len(self.checks)} checks)"


# =============================================================================
# ExperienceQuality: The Fundamental Quality Measurement
# =============================================================================


@dataclass(frozen=True)
class ExperienceQuality:
    """
    The fundamental quality measurement.

    Quality Tetrad:
    - Contrast (C): Variety [0, 1]
    - Arc (A): Shape [0, 1]
    - Voice (V): Correct, Interesting, Fun {0, 1}^3
    - Floor (F): Worth having {0, 1}

    The overall quality formula:
        Q = F * (alpha*C + beta*A + gamma*V)

    Floor is multiplicative (gate), others are weighted sum.
    """

    # Continuous metrics
    contrast: float = 0.5  # C in [0, 1]
    arc_coverage: float = 0.5  # A in [0, 1]

    # Discrete metrics (voice triple)
    voice_adversarial: bool = True  # V_a: Is it correct?
    voice_creative: bool = True  # V_c: Is it interesting?
    voice_advocate: bool = True  # V_p: Is it fun?

    # Gate
    floor_passed: bool = True  # F: Worth having?

    # Default weights (tunable per domain)
    _alpha: float = field(default=0.35, repr=False)
    _beta: float = field(default=0.35, repr=False)
    _gamma: float = field(default=0.30, repr=False)

    def __post_init__(self) -> None:
        """Validate ranges."""
        if not 0.0 <= self.contrast <= 1.0:
            object.__setattr__(self, "contrast", max(0.0, min(1.0, self.contrast)))
        if not 0.0 <= self.arc_coverage <= 1.0:
            object.__setattr__(
                self, "arc_coverage", max(0.0, min(1.0, self.arc_coverage))
            )

    @property
    def voice_alignment(self) -> float:
        """Voice alignment as continuous signal."""
        return (
            sum([self.voice_adversarial, self.voice_creative, self.voice_advocate]) / 3
        )

    @property
    def overall(self) -> float:
        """
        Overall quality score.

        Q = F * (alpha*C + beta*A + gamma*V)

        Floor is multiplicative (gate), others are weighted sum.
        """
        if not self.floor_passed:
            return 0.0

        return (
            self._alpha * self.contrast
            + self._beta * self.arc_coverage
            + self._gamma * self.voice_alignment
        )

    @property
    def bottleneck(self) -> str:
        """Identify the quality bottleneck."""
        if not self.floor_passed:
            return "floor"
        if not self.voice_adversarial:
            return "voice_adversarial"
        if not self.voice_advocate:
            return "voice_advocate"
        if not self.voice_creative:
            return "voice_creative"
        if self.contrast < self.arc_coverage:
            return "contrast"
        return "arc"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "contrast": self.contrast,
            "arc_coverage": self.arc_coverage,
            "voice_adversarial": self.voice_adversarial,
            "voice_creative": self.voice_creative,
            "voice_advocate": self.voice_advocate,
            "floor_passed": self.floor_passed,
            "voice_alignment": self.voice_alignment,
            "overall": self.overall,
            "bottleneck": self.bottleneck,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ExperienceQuality:
        """Create from dictionary."""
        return cls(
            contrast=data.get("contrast", 0.5),
            arc_coverage=data.get("arc_coverage", 0.5),
            voice_adversarial=data.get("voice_adversarial", True),
            voice_creative=data.get("voice_creative", True),
            voice_advocate=data.get("voice_advocate", True),
            floor_passed=data.get("floor_passed", True),
        )

    @classmethod
    def unit(cls) -> ExperienceQuality:
        """Return the identity quality (for composition laws)."""
        return cls(
            contrast=1.0,
            arc_coverage=1.0,
            voice_adversarial=True,
            voice_creative=True,
            voice_advocate=True,
            floor_passed=True,
        )

    @classmethod
    def zero(cls) -> ExperienceQuality:
        """Return the zero quality (floor failed)."""
        return cls(
            contrast=0.0,
            arc_coverage=0.0,
            voice_adversarial=False,
            voice_creative=False,
            voice_advocate=False,
            floor_passed=False,
        )

    def with_weights(
        self, alpha: float = 0.35, beta: float = 0.35, gamma: float = 0.30
    ) -> ExperienceQuality:
        """Return new quality with custom weights."""
        return ExperienceQuality(
            contrast=self.contrast,
            arc_coverage=self.arc_coverage,
            voice_adversarial=self.voice_adversarial,
            voice_creative=self.voice_creative,
            voice_advocate=self.voice_advocate,
            floor_passed=self.floor_passed,
            _alpha=alpha,
            _beta=beta,
            _gamma=gamma,
        )

    def __repr__(self) -> str:
        """Concise representation."""
        if not self.floor_passed:
            return "ExperienceQuality(floor_failed, Q=0.00)"
        return f"ExperienceQuality(Q={self.overall:.2f}, C={self.contrast:.2f}, A={self.arc_coverage:.2f})"


# =============================================================================
# Experience: Abstract container for quality measurement
# =============================================================================


@dataclass
class Experience:
    """
    Abstract container representing an experience to be measured.

    This is a minimal interface that domain-specific experiences
    (games, sessions, runs, etc.) can implement or wrap.
    """

    id: str
    type: str  # "moment", "wave", "run", "session", etc.
    domain: str  # "wasm_survivors", "daily_lab", etc.
    duration: float = 0.0  # Duration in seconds

    # Raw data for measurement (domain-specific)
    data: dict[str, Any] = field(default_factory=dict)

    # Cached measurements
    _contrast: ContrastMeasurement | None = field(default=None, repr=False)
    _arc: ArcMeasurement | None = field(default=None, repr=False)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "type": self.type,
            "domain": self.domain,
            "duration": self.duration,
            "data": self.data,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Experience:
        """Create from dictionary."""
        return cls(
            id=data.get("id", ""),
            type=data.get("type", "unknown"),
            domain=data.get("domain", "unknown"),
            duration=data.get("duration", 0.0),
            data=data.get("data", {}),
        )


# =============================================================================
# Spec: Abstract container for specification (for voice checks)
# =============================================================================


@dataclass
class Spec:
    """
    Abstract specification for voice checks.

    Contains laws and invariants that the experience must satisfy.
    """

    name: str
    laws: tuple[str, ...] = ()  # Law names that must be satisfied
    invariants: tuple[str, ...] = ()  # Invariant names that must hold

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "laws": list(self.laws),
            "invariants": list(self.invariants),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Spec:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            laws=tuple(data.get("laws", [])),
            invariants=tuple(data.get("invariants", [])),
        )

    @classmethod
    def empty(cls) -> Spec:
        """Return an empty spec (all checks pass by default)."""
        return cls(name="empty")


# =============================================================================
# Quality Algebra: Domain Parameterization
# =============================================================================


@dataclass(frozen=True)
class ContrastDimension:
    """
    Definition of a contrast dimension for a domain.

    Each domain has its own set of contrast dimensions that measure
    variance along different experiential axes.

    Example:
        ContrastDimension(
            name="breath",
            description="Intensity oscillation (crescendo <-> silence)",
            measurement_hint="Track intensity values over time, compute variance"
        )
    """

    name: str
    description: str
    measurement_hint: str = ""  # How to measure this dimension
    curve_key: str = ""  # Key in experience.data for time series (defaults to {name}_curve)
    default_value: float = 0.5  # Default value if no data found

    def __post_init__(self) -> None:
        """Set curve_key default if not provided."""
        if not self.curve_key:
            # Use name_curve as the default key
            object.__setattr__(self, "curve_key", f"{self.name}_curve")

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "measurement_hint": self.measurement_hint,
            "curve_key": self.curve_key,
            "default_value": self.default_value,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ContrastDimension:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            measurement_hint=data.get("measurement_hint", ""),
            curve_key=data.get("curve_key", ""),
            default_value=data.get("default_value", 0.5),
        )


@dataclass(frozen=True)
class PhaseDefinition:
    """
    Definition of an emotional/temporal phase for a domain.

    Phases define the emotional arc structure for a domain.
    Different domains may have different phase vocabularies.

    Example:
        PhaseDefinition(
            name="flow",
            description="Player is in the zone, unstoppable feeling",
            triggers=("high_score_streak", "no_damage_taken", "combo_active")
        )
    """

    name: str
    description: str
    triggers: tuple[str, ...] = ()  # What triggers entry to this phase

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "description": self.description,
            "triggers": list(self.triggers),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> PhaseDefinition:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            triggers=tuple(data.get("triggers", [])),
        )


@dataclass(frozen=True)
class VoiceDefinition:
    """
    Definition of a quality voice for a domain.

    Voices ask questions about quality from different perspectives.
    The standard three voices are adversarial, creative, and advocate,
    but domains can define custom voices.

    Example:
        VoiceDefinition(
            name="adversarial",
            question="Is this technically correct and fair?",
            checks=("no_impossible_deaths", "clear_feedback", "consistent_rules")
        )
    """

    name: str
    question: str  # What this voice asks
    checks: tuple[str, ...] = ()  # What it checks

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "question": self.question,
            "checks": list(self.checks),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> VoiceDefinition:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            question=data.get("question", ""),
            checks=tuple(data.get("checks", [])),
        )


@dataclass(frozen=True)
class FloorCheckDefinition:
    """
    Definition of a floor check for a domain.

    Floor checks define minimum quality gates that must be passed.
    These are binary (pass/fail) checks that gate overall quality.

    Example:
        FloorCheckDefinition(
            name="input_latency_ms",
            threshold=16.0,
            comparison="<=",
            unit="ms",
            description="Input latency must be under 16ms for responsive feel"
        )
    """

    name: str
    threshold: float
    comparison: str  # "<=", ">=", "==", "<", ">"
    unit: str
    description: str = ""

    def check(self, value: float) -> bool:
        """
        Check if a value passes this floor check.

        Args:
            value: The measured value to check.

        Returns:
            True if the check passes, False otherwise.
        """
        if self.comparison == "<=":
            return value <= self.threshold
        elif self.comparison == ">=":
            return value >= self.threshold
        elif self.comparison == "==":
            return abs(value - self.threshold) < 1e-9
        elif self.comparison == "<":
            return value < self.threshold
        elif self.comparison == ">":
            return value > self.threshold
        else:
            return False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "threshold": self.threshold,
            "comparison": self.comparison,
            "unit": self.unit,
            "description": self.description,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> FloorCheckDefinition:
        """Create from dictionary."""
        return cls(
            name=data.get("name", ""),
            threshold=data.get("threshold", 0.0),
            comparison=data.get("comparison", ">="),
            unit=data.get("unit", ""),
            description=data.get("description", ""),
        )


@dataclass(frozen=True)
class QualityAlgebra:
    """
    Domain-specific quality measurement algebra.

    The universal Experience Quality Operad defines abstract dimensions:
    Contrast, Arc, Voice, Floor. A QualityAlgebra instantiates these
    for a specific domain.

    Philosophy:
        The operad is the universal grammar of quality measurement.
        An algebra is a domain-specific interpretation of that grammar.
        Different domains (games, sessions, runs) share the same structure
        but have different vocabularies and thresholds.

    Example domains: wasm_survivors, rap_coach, disney_portal, daily_lab

    Usage:
        >>> algebra = QualityAlgebra(
        ...     domain="wasm_survivors",
        ...     description="Quality algebra for WASM Survivors game",
        ...     contrast_dims=(...),
        ...     arc_phases=(...),
        ...     voices=(...),
        ...     floor_checks=(...),
        ... )
        >>> dim = algebra.get_contrast_dim("breath")
        >>> phase = algebra.get_phase("flow")
    """

    # Required fields (no defaults) must come first
    domain: str
    description: str

    # Contrast dimension specification
    contrast_dims: tuple[ContrastDimension, ...]

    # Arc phase specification
    arc_phases: tuple[PhaseDefinition, ...]

    # Voice specification
    voices: tuple[VoiceDefinition, ...]

    # Floor specification
    floor_checks: tuple[FloorCheckDefinition, ...]

    # Optional fields (with defaults) must come after required fields
    arc_canonical_transitions: tuple[tuple[str, str], ...] = ()  # Valid phase transitions
    voice_combination: str = "AND"  # "AND", "OR", "WEIGHTED"

    # Weights for overall quality calculation
    contrast_weight: float = 0.35
    arc_weight: float = 0.35
    voice_weight: float = 0.30

    def get_contrast_dim(self, name: str) -> ContrastDimension | None:
        """Get a contrast dimension by name."""
        for dim in self.contrast_dims:
            if dim.name == name:
                return dim
        return None

    def get_phase(self, name: str) -> PhaseDefinition | None:
        """Get a phase by name."""
        for phase in self.arc_phases:
            if phase.name == name:
                return phase
        return None

    def get_voice(self, name: str) -> VoiceDefinition | None:
        """Get a voice by name."""
        for voice in self.voices:
            if voice.name == name:
                return voice
        return None

    def get_floor_check(self, name: str) -> FloorCheckDefinition | None:
        """Get a floor check by name."""
        for check in self.floor_checks:
            if check.name == name:
                return check
        return None

    @property
    def contrast_dim_names(self) -> tuple[str, ...]:
        """Get all contrast dimension names."""
        return tuple(dim.name for dim in self.contrast_dims)

    @property
    def phase_names(self) -> tuple[str, ...]:
        """Get all phase names."""
        return tuple(phase.name for phase in self.arc_phases)

    @property
    def voice_names(self) -> tuple[str, ...]:
        """Get all voice names."""
        return tuple(voice.name for voice in self.voices)

    @property
    def floor_check_names(self) -> tuple[str, ...]:
        """Get all floor check names."""
        return tuple(check.name for check in self.floor_checks)

    def is_valid_transition(self, from_phase: str, to_phase: str) -> bool:
        """Check if a phase transition is valid according to canonical transitions."""
        if not self.arc_canonical_transitions:
            return True  # No constraints defined
        return (from_phase, to_phase) in self.arc_canonical_transitions

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "domain": self.domain,
            "description": self.description,
            "contrast_dims": [d.to_dict() for d in self.contrast_dims],
            "arc_phases": [p.to_dict() for p in self.arc_phases],
            "arc_canonical_transitions": [
                list(t) for t in self.arc_canonical_transitions
            ],
            "voices": [v.to_dict() for v in self.voices],
            "voice_combination": self.voice_combination,
            "floor_checks": [f.to_dict() for f in self.floor_checks],
            "contrast_weight": self.contrast_weight,
            "arc_weight": self.arc_weight,
            "voice_weight": self.voice_weight,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> QualityAlgebra:
        """Create from dictionary."""
        return cls(
            domain=data.get("domain", ""),
            description=data.get("description", ""),
            contrast_dims=tuple(
                ContrastDimension.from_dict(d)
                for d in data.get("contrast_dims", [])
            ),
            arc_phases=tuple(
                PhaseDefinition.from_dict(p)
                for p in data.get("arc_phases", [])
            ),
            arc_canonical_transitions=tuple(
                tuple(t) for t in data.get("arc_canonical_transitions", [])
            ),
            voices=tuple(
                VoiceDefinition.from_dict(v)
                for v in data.get("voices", [])
            ),
            voice_combination=data.get("voice_combination", "AND"),
            floor_checks=tuple(
                FloorCheckDefinition.from_dict(f)
                for f in data.get("floor_checks", [])
            ),
            contrast_weight=data.get("contrast_weight", 0.35),
            arc_weight=data.get("arc_weight", 0.35),
            voice_weight=data.get("voice_weight", 0.30),
        )

    def __repr__(self) -> str:
        """Concise representation."""
        return (
            f"QualityAlgebra(domain={self.domain!r}, "
            f"contrast={len(self.contrast_dims)}, "
            f"phases={len(self.arc_phases)}, "
            f"voices={len(self.voices)}, "
            f"floors={len(self.floor_checks)})"
        )


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Enums
    "EmotionalPhase",
    # Contrast
    "ContrastMeasurement",
    # Arc
    "ArcMeasurement",
    # Voice
    "VoiceVerdict",
    "VoiceMeasurement",
    # Floor
    "FloorCheck",
    "FloorMeasurement",
    # Quality
    "ExperienceQuality",
    # Containers
    "Experience",
    "Spec",
    # Quality Algebra (Domain Parameterization)
    "ContrastDimension",
    "PhaseDefinition",
    "VoiceDefinition",
    "FloorCheckDefinition",
    "QualityAlgebra",
]
