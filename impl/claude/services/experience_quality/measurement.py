"""
Experience Quality Operad: Measurement Functions.

Measurement operations for the four quality dimensions:
- Contrast: Variance across seven dimensions
- Arc: Emotional phase coverage and shape
- Voice: Three-voice quality check (adversarial, creative, advocate)
- Floor: Minimum quality gate

These are the atomic measurement operations of the operad.

Algebra-Aware Measurement:
    All measurement functions accept an optional QualityAlgebra parameter.
    If provided, domain-specific dimensions, phases, and checks are used.
    If not provided, falls back to default/legacy behavior.

Philosophy:
    "Experience quality is measurable, composable, and witnessable."

See: spec/theory/experience-quality-operad.md
"""

from __future__ import annotations

import math
from typing import TYPE_CHECKING, Any

from .algebras import get_algebra
from .types import (
    ArcMeasurement,
    ContrastMeasurement,
    EmotionalPhase,
    Experience,
    ExperienceQuality,
    FloorCheck,
    FloorMeasurement,
    QualityAlgebra,
    Spec,
    VoiceMeasurement,
    VoiceVerdict,
)

if TYPE_CHECKING:
    pass


# =============================================================================
# Domain-Specific Floor Checks (Legacy - for backward compatibility)
# =============================================================================

# Default floor checks for different domains
# Note: Domain-specific checks should be registered via QualityAlgebra at runtime.
# These are only fallback defaults for generic domain types.
DOMAIN_FLOOR_CHECKS: dict[str, list[tuple[str, float, str, str]]] = {
    # (name, threshold, comparison, unit)
    "game": [
        ("input_latency_ms", 16.0, "<=", "ms"),
        ("feedback_ratio", 0.9, ">=", "ratio"),
        ("death_readable", 0.8, ">=", "ratio"),
        ("restart_time_s", 3.0, "<=", "seconds"),
    ],
    "session": [
        ("engagement_duration", 60.0, ">=", "seconds"),
        ("interaction_count", 5.0, ">=", "count"),
    ],
    "default": [
        ("engagement", 0.5, ">=", "ratio"),
    ],
}


# =============================================================================
# Utility Functions
# =============================================================================


def variance_normalized(values: list[float]) -> float:
    """
    Compute normalized variance of a signal.

    Returns a value in [0, 1] where:
    - 0 = no variance (monotonous)
    - 1 = maximum variance (high contrast)
    """
    if len(values) < 2:
        return 0.0

    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)

    # Normalize: variance of 0.25 (for [0,1] range) maps to 1.0
    # This is the maximum variance for a signal oscillating between 0 and 1
    normalized = min(1.0, variance / 0.25)
    return normalized


def cosine_distance(a: list[float], b: list[float]) -> float:
    """
    Compute cosine distance between two vectors.

    Returns value in [0, 1] where:
    - 0 = identical direction
    - 1 = opposite direction
    """
    if len(a) != len(b) or not a:
        return 0.0

    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))

    if mag_a == 0 or mag_b == 0:
        return 0.0

    similarity = dot / (mag_a * mag_b)
    # Convert similarity [-1, 1] to distance [0, 1]
    return (1 - similarity) / 2


def experience_vector(quality: ExperienceQuality) -> list[float]:
    """Convert quality to a vector for distance calculations."""
    return [
        quality.contrast,
        quality.arc_coverage,
        1.0 if quality.voice_adversarial else 0.0,
        1.0 if quality.voice_creative else 0.0,
        1.0 if quality.voice_advocate else 0.0,
        1.0 if quality.floor_passed else 0.0,
    ]


def chain_arc_coverage(a: float, b: float) -> float:
    """
    Chain two arc coverages sequentially.

    When experiences chain, arc coverage can exceed individual parts
    if they complement each other (e.g., A has HOPE->FLOW, B has CRISIS->TRIUMPH).
    """
    # Complementary chaining: if both are partial, combined can be more complete
    # But never exceed 1.0
    combined = (a + b) / 2 + 0.1 * min(a, b)  # Bonus for having both
    return min(1.0, combined)


# =============================================================================
# Contrast Measurement
# =============================================================================


def _measure_contrast_default(experience: Experience) -> ContrastMeasurement:
    """
    Default contrast measurement using hardcoded dimensions.

    Used when no algebra is provided or algebra has no contrast_dims.
    """
    data = experience.data

    # Extract curves from data if available, else use defaults
    intensity_curve = data.get("intensity_curve", [0.5])
    resource_curve = data.get("resource_curve", [0.5])
    tempo_curve = data.get("tempo_curve", [0.5])
    stakes_curve = data.get("stakes_curve", [0.5])
    anticipation_curve = data.get("anticipation_curve", [0.5])
    reward_curve = data.get("reward_curve", [0.5])
    choice_curve = data.get("choice_breadth_curve", [0.5])

    return ContrastMeasurement(
        breath=variance_normalized(intensity_curve),
        scarcity=variance_normalized(resource_curve),
        tempo=variance_normalized(tempo_curve),
        stakes=variance_normalized(stakes_curve),
        anticipation=variance_normalized(anticipation_curve),
        reward=variance_normalized(reward_curve),
        identity=variance_normalized(choice_curve),
    )


def measure_contrast(
    experience: Experience,
    algebra: QualityAlgebra | None = None,
) -> ContrastMeasurement:
    """
    Measure contrast across an experience using domain-specific dimensions.

    If no algebra provided, uses the algebra for experience.domain.
    If still None or algebra has no dimensions, uses default measurement.

    For each dimension, we measure the VARIANCE of the signal over time.
    High variance = high contrast = good.
    Low variance = monotony = bad.

    Args:
        experience: The experience to measure
        algebra: Optional domain-specific algebra

    Returns:
        ContrastMeasurement with variance scores for each dimension
    """
    if algebra is None:
        algebra = get_algebra(experience.domain)

    # If still None or no contrast dims, use default measurement
    if algebra is None or not algebra.contrast_dims:
        return _measure_contrast_default(experience)

    # Use algebra's contrast dimensions
    data = experience.data
    measurements: dict[str, float] = {}

    for dim in algebra.contrast_dims:
        curve = data.get(dim.curve_key, [dim.default_value])
        measurements[dim.name] = variance_normalized(curve)

    # Map to ContrastMeasurement
    # The standard seven dimensions map directly; custom dimensions use fallbacks
    return ContrastMeasurement(
        breath=measurements.get(
            "breath", measurements.get("energy", measurements.get("intensity", 0.5))
        ),
        scarcity=measurements.get("scarcity", measurements.get("resource", 0.5)),
        tempo=measurements.get("tempo", measurements.get("speed", 0.5)),
        stakes=measurements.get(
            "stakes", measurements.get("difficulty", measurements.get("risk", 0.5))
        ),
        anticipation=measurements.get(
            "anticipation", measurements.get("tension", measurements.get("focus", 0.5))
        ),
        reward=measurements.get(
            "reward", measurements.get("progress", measurements.get("mood", 0.5))
        ),
        identity=measurements.get(
            "identity",
            measurements.get(
                "creativity", measurements.get("choice", measurements.get("social", 0.5))
            ),
        ),
    )


# =============================================================================
# Arc Measurement
# =============================================================================


def classify_emotional_phase(moment_data: dict[str, Any]) -> EmotionalPhase:
    """
    Classify a moment into an emotional phase.

    This is a placeholder implementation using heuristics.
    In production, this could use sentiment analysis or domain-specific rules.
    """
    health_ratio = moment_data.get("health_ratio", 1.0)
    intensity = moment_data.get("intensity", 0.5)
    is_victory = moment_data.get("is_victory", False)
    is_death = moment_data.get("is_death", False)
    phase_hint = moment_data.get("phase", None)

    # If phase is explicitly provided, use it
    if phase_hint:
        try:
            return EmotionalPhase(phase_hint)
        except ValueError:
            pass

    # Heuristic classification
    if is_victory:
        return EmotionalPhase.TRIUMPH
    if is_death:
        return EmotionalPhase.GRIEF
    if health_ratio < 0.3 or intensity > 0.8:
        return EmotionalPhase.CRISIS
    if intensity > 0.5 and health_ratio > 0.5:
        return EmotionalPhase.FLOW
    if health_ratio > 0.8:
        return EmotionalPhase.HOPE

    return EmotionalPhase.FLOW  # Default


def measure_arc(
    experience: Experience,
    algebra: QualityAlgebra | None = None,
) -> ArcMeasurement:
    """
    Measure emotional arc across an experience using domain-specific phases.

    Uses heuristics to classify moments into phases and track transitions.

    If algebra is provided, may use domain-specific phase definitions
    (though current implementation uses standard EmotionalPhase enum).

    Args:
        experience: The experience to measure
        algebra: Optional domain-specific algebra

    Returns:
        ArcMeasurement with phase coverage and transition information
    """
    if algebra is None:
        algebra = get_algebra(experience.domain)

    # Note: Current implementation uses standard EmotionalPhase enum.
    # Future enhancement: Support custom phase definitions from algebra.
    # For now, algebra is used for metadata/weights only.

    data = experience.data
    moments = data.get("moments", [])

    if not moments:
        # No moments data - return basic arc based on overall signals
        has_crisis = data.get("had_crisis", False)
        has_resolution = data.get("had_resolution", False)

        phases = set()
        if data.get("started_hopeful", True):
            phases.add(EmotionalPhase.HOPE)
        if data.get("had_flow", True):
            phases.add(EmotionalPhase.FLOW)
        if has_crisis:
            phases.add(EmotionalPhase.CRISIS)
        if data.get("is_victory", False):
            phases.add(EmotionalPhase.TRIUMPH)
        if data.get("is_death", False):
            phases.add(EmotionalPhase.GRIEF)

        return ArcMeasurement(
            phases_visited=frozenset(phases),
            phase_durations={},
            transitions=(),
        )

    # Process moments
    phases_visited: set[EmotionalPhase] = set()
    phase_durations: dict[EmotionalPhase, float] = {}
    transitions: list[tuple[EmotionalPhase, EmotionalPhase]] = []

    current_phase: EmotionalPhase | None = None
    for moment in moments:
        phase = classify_emotional_phase(moment)
        phases_visited.add(phase)

        # Track duration
        duration = moment.get("duration", 1.0)
        phase_durations[phase] = phase_durations.get(phase, 0.0) + duration

        # Track transitions
        if current_phase and phase != current_phase:
            transitions.append((current_phase, phase))
        current_phase = phase

    return ArcMeasurement(
        phases_visited=frozenset(phases_visited),
        phase_durations=phase_durations,
        transitions=tuple(transitions),
    )


# =============================================================================
# Voice Checks
# =============================================================================


def check_adversarial(experience: Experience, spec: Spec) -> VoiceVerdict:
    """
    ADVERSARIAL: Is this correct?

    Checks:
    - Laws are satisfied
    - Invariants hold
    - No undefined behavior

    This is a placeholder. In production, this would run actual law checks.
    """
    violations: list[str] = []
    data = experience.data

    # Check if laws are satisfied (placeholder: check data flags)
    for law in spec.laws:
        law_key = f"law_{law}_satisfied"
        if not data.get(law_key, True):
            violations.append(f"Law {law} violated")

    # Check invariants
    for invariant in spec.invariants:
        inv_key = f"invariant_{invariant}_holds"
        if not data.get(inv_key, True):
            violations.append(f"Invariant {invariant} broken")

    if violations:
        confidence = 1.0 - (len(violations) / max(len(spec.laws) + len(spec.invariants), 1))
        return VoiceVerdict.fail_verdict(
            reasoning=f"{len(violations)} violations found",
            violations=tuple(violations),
            confidence=max(0.0, confidence),
        )

    return VoiceVerdict.pass_verdict(
        reasoning="All laws and invariants satisfied",
        confidence=1.0,
    )


def check_creative(experience: Experience, spec: Spec) -> VoiceVerdict:
    """
    CREATIVE: Is this interesting?

    Checks:
    - Novelty (not repetitive)
    - Surprise (unexpected moments)
    - Aesthetic coherence

    This is a placeholder. In production, this could use LLM analysis.
    """
    data = experience.data

    # Extract or compute creative metrics
    novelty = data.get("novelty", 0.5)
    surprise = data.get("surprise", 0.5)
    coherence = data.get("aesthetic_coherence", 0.5)

    score = (novelty + surprise + coherence) / 3

    if score > 0.5:
        return VoiceVerdict.pass_verdict(
            reasoning=f"Novelty: {novelty:.2f}, Surprise: {surprise:.2f}, Coherence: {coherence:.2f}",
            confidence=score,
        )
    else:
        return VoiceVerdict.fail_verdict(
            reasoning=f"Low creative score: Novelty: {novelty:.2f}, Surprise: {surprise:.2f}, Coherence: {coherence:.2f}",
            violations=("Low novelty/surprise/coherence",),
            confidence=1.0 - score,
        )


def check_advocate(experience: Experience, spec: Spec) -> VoiceVerdict:
    """
    PLAYER ADVOCATE: Is this fun?

    Checks:
    - Engagement (not boring)
    - Agency (player feels in control)
    - Satisfaction (rewards feel earned)

    This is a placeholder. In production, this could use player feedback data.
    """
    data = experience.data

    # Extract or compute advocate metrics
    engagement = data.get("engagement", 0.5)
    agency = data.get("agency", 0.5)
    satisfaction = data.get("satisfaction", 0.5)

    score = (engagement + agency + satisfaction) / 3

    if score > 0.5:
        return VoiceVerdict.pass_verdict(
            reasoning=f"Engagement: {engagement:.2f}, Agency: {agency:.2f}, Satisfaction: {satisfaction:.2f}",
            confidence=score,
        )
    else:
        return VoiceVerdict.fail_verdict(
            reasoning=f"Low fun score: Engagement: {engagement:.2f}, Agency: {agency:.2f}, Satisfaction: {satisfaction:.2f}",
            violations=("Low engagement/agency/satisfaction",),
            confidence=1.0 - score,
        )


def check_voice(experience: Experience, spec: Spec) -> VoiceMeasurement:
    """
    Check experience against the three voices.

    Returns a VoiceMeasurement with verdicts from all three perspectives.
    """
    return VoiceMeasurement(
        adversarial=check_adversarial(experience, spec),
        creative=check_creative(experience, spec),
        advocate=check_advocate(experience, spec),
    )


# =============================================================================
# Floor Check
# =============================================================================


def get_floor_checks_for_domain(domain: str) -> list[tuple[str, float, str, str]]:
    """Get floor checks for a domain (legacy format)."""
    return DOMAIN_FLOOR_CHECKS.get(domain, DOMAIN_FLOOR_CHECKS["default"])


def meets_threshold(value: float, threshold: float, comparison: str) -> bool:
    """Check if a value meets a threshold."""
    if comparison == "<=":
        return value <= threshold
    elif comparison == ">=":
        return value >= threshold
    elif comparison == "==":
        return value == threshold
    elif comparison == "<":
        return value < threshold
    elif comparison == ">":
        return value > threshold
    return False


def _check_floor_legacy(experience: Experience, domain: str) -> FloorMeasurement:
    """
    Legacy floor check using DOMAIN_FLOOR_CHECKS dict.

    Used when no algebra is provided.
    """
    check_defs = get_floor_checks_for_domain(domain)
    data = experience.data

    evaluated: list[FloorCheck] = []
    for name, threshold, comparison, unit in check_defs:
        # Get measurement from experience data (default to threshold to pass)
        measurement = data.get(name, threshold)

        # Handle boolean flags
        if unit == "bool":
            measurement = 1.0 if data.get(name, True) else 0.0

        passed = meets_threshold(measurement, threshold, comparison)

        evaluated.append(
            FloorCheck(
                name=name,
                passed=passed,
                measurement=measurement,
                threshold=threshold,
                unit=unit,
            )
        )

    return FloorMeasurement(checks=tuple(evaluated))


def check_floor(
    experience: Experience,
    domain: str | None = None,
    algebra: QualityAlgebra | None = None,
) -> FloorMeasurement:
    """
    Check if experience passes the fun floor using domain-specific checks.

    The floor is a boolean gate - if any check fails, the experience
    is not worth having (quality = 0).

    If algebra is provided, uses algebra's floor_checks.
    Otherwise, falls back to legacy DOMAIN_FLOOR_CHECKS dict.

    Args:
        experience: The experience to check
        domain: Optional domain override
        algebra: Optional domain-specific algebra

    Returns:
        FloorMeasurement with all check results
    """
    if algebra is None:
        domain = domain or experience.domain
        algebra = get_algebra(domain)

    # If still no algebra, use legacy behavior
    if algebra is None:
        return _check_floor_legacy(experience, domain or experience.domain)

    # Use algebra's floor checks
    data = experience.data
    evaluated: list[FloorCheck] = []

    for check_def in algebra.floor_checks:
        # Get measurement from experience data (default to threshold to pass)
        measurement = data.get(check_def.name, check_def.threshold)

        # Handle boolean flags
        if check_def.unit == "bool":
            measurement = 1.0 if data.get(check_def.name, True) else 0.0

        # Use FloorCheckDefinition.check() method if available, else fallback
        passed = check_def.check(measurement)

        evaluated.append(
            FloorCheck(
                name=check_def.name,
                passed=passed,
                measurement=measurement,
                threshold=check_def.threshold,
                unit=check_def.unit,
            )
        )

    return FloorMeasurement(checks=tuple(evaluated))


# =============================================================================
# Unified Quality Measurement
# =============================================================================


def measure_quality(
    experience: Experience,
    spec: Spec | None = None,
    domain: str | None = None,
    algebra: QualityAlgebra | None = None,
) -> ExperienceQuality:
    """
    Measure the complete quality of an experience using domain-specific algebra.

    Combines all four dimensions:
    - Contrast (from timeline variance)
    - Arc (from emotional phase coverage)
    - Voice (from three-voice check)
    - Floor (from domain-specific gates)

    If algebra is provided, uses domain-specific:
    - Contrast dimensions
    - Arc phases
    - Floor checks
    - Quality weights

    Args:
        experience: The experience to measure
        spec: Optional specification for voice checks
        domain: Optional domain override
        algebra: Optional domain-specific algebra

    Returns:
        ExperienceQuality object with all metrics
    """
    spec = spec or Spec.empty()
    domain = domain or experience.domain

    # Get algebra if not provided
    if algebra is None:
        algebra = get_algebra(domain)

    # Measure each dimension (passing algebra for domain-specific behavior)
    contrast = measure_contrast(experience, algebra)
    arc = measure_arc(experience, algebra)
    voice = check_voice(experience, spec)
    floor = check_floor(experience, algebra=algebra)

    # Use algebra weights if available, else defaults
    if algebra is not None:
        alpha = algebra.contrast_weight
        beta = algebra.arc_weight
        gamma = algebra.voice_weight
    else:
        alpha, beta, gamma = 0.35, 0.35, 0.30

    return ExperienceQuality(
        contrast=contrast.overall,
        arc_coverage=arc.coverage,
        voice_adversarial=voice.adversarial.passed,
        voice_creative=voice.creative.passed,
        voice_advocate=voice.advocate.passed,
        floor_passed=floor.passed,
        _alpha=alpha,
        _beta=beta,
        _gamma=gamma,
    )


def identify_bottleneck(
    quality: ExperienceQuality,
    contrast: ContrastMeasurement,
    arc: ArcMeasurement,
    voice: VoiceMeasurement,
    floor: FloorMeasurement,
) -> str:
    """
    Identify the primary quality bottleneck.

    Returns a string describing what most needs improvement.
    """
    # Floor is the gate - if it fails, that's the bottleneck
    if not floor.passed:
        failures = floor.failures
        if failures:
            return f"floor:{failures[0]}"
        return "floor:unknown"

    # Voice failures are next priority
    if not voice.adversarial.passed:
        return "voice:adversarial"
    if not voice.advocate.passed:
        return "voice:advocate"
    if not voice.creative.passed:
        return "voice:creative"

    # Check continuous dimensions
    if contrast.overall < arc.coverage:
        return f"contrast:{contrast.weakest_dimension}"

    if not arc.has_crisis:
        return "arc:no_crisis"
    if not arc.has_resolution:
        return "arc:no_resolution"

    return f"arc:coverage({arc.coverage:.2f})"


def generate_recommendation(bottleneck: str) -> str:
    """
    Generate a recommendation based on the bottleneck.

    Returns actionable advice for improving quality.
    """
    recommendations = {
        # Floor failures
        "floor:input_latency_ms": "Reduce input latency to under 16ms for responsive feel",
        "floor:feedback_ratio": "Add more visual/audio feedback for player actions",
        "floor:death_readable": "Make death causes clearer - player should understand why they died",
        "floor:restart_time_s": "Speed up restart loop - under 3 seconds",
        # Voice failures
        "voice:adversarial": "Fix law violations and broken invariants",
        "voice:advocate": "Improve engagement, agency, and satisfaction scores",
        "voice:creative": "Add more novelty, surprise, or aesthetic coherence",
        # Contrast dimensions
        "contrast:breath": "Add intensity oscillation - vary between crescendo and silence",
        "contrast:scarcity": "Vary resource availability - feast and famine moments",
        "contrast:tempo": "Vary pacing - fast action and slow recovery",
        "contrast:stakes": "Vary risk level - safe exploration and lethal danger",
        "contrast:anticipation": "Build tension with anticipation cycles",
        "contrast:reward": "Vary reward density - drought and burst patterns",
        "contrast:identity": "Vary choice breadth - exploration and commitment phases",
        # Arc issues
        "arc:no_crisis": "Add a crisis moment - every good arc needs tension",
        "arc:no_resolution": "Ensure clear resolution - triumph or grief, not stuck",
    }

    # Direct match
    if bottleneck in recommendations:
        return recommendations[bottleneck]

    # Partial match
    for key, rec in recommendations.items():
        if bottleneck.startswith(key.split(":")[0]):
            return rec

    return f"Improve {bottleneck} dimension for higher quality"


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Contrast
    "measure_contrast",
    "variance_normalized",
    # Arc
    "measure_arc",
    "classify_emotional_phase",
    # Voice
    "check_voice",
    "check_adversarial",
    "check_creative",
    "check_advocate",
    # Floor
    "check_floor",
    "get_floor_checks_for_domain",
    # Unified
    "measure_quality",
    "identify_bottleneck",
    "generate_recommendation",
    # Utilities
    "cosine_distance",
    "experience_vector",
    "chain_arc_coverage",
]
