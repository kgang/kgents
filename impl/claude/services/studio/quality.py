"""
S-gent Studio Quality Algebra.

Domain-specific instantiation of the Experience Quality Operad for
the Creative Production Studio (S-gent).

Philosophy:
    "The proof IS the decision. The mark IS the witness.
     The asset IS the vision made manifest."

This algebra defines:
- C1-C3 contrast dimensions for creative variety
- Discovery -> Exploration -> Commitment -> Execution -> Polish arc
- Three voices: Adversarial (correct), Creative (novel), Advocate (delightful)
- F1-F4 floor checks (the sacred Quality Floor)

See: spec/s-gents/studio.md Part V
See: spec/theory/experience-quality-operad.md
"""

from __future__ import annotations

from typing import Any

from ..experience_quality.algebras import register_algebra, register_algebra_overwrite
from ..experience_quality.types import (
    ContrastDimension,
    FloorCheckDefinition,
    PhaseDefinition,
    QualityAlgebra,
    VoiceDefinition,
)

# =============================================================================
# C1-C3: Contrast Dimensions
# =============================================================================

STUDIO_CONTRAST_DIMS = (
    ContrastDimension(
        name="expression",
        description="C1: Range of creative expression",
        measurement_hint="Track uniqueness vs. derivativeness of outputs",
        curve_key="expression_curve",
    ),
    ContrastDimension(
        name="consistency",
        description="C2: Adherence to style guide",
        measurement_hint="Measure deviation from vision across outputs",
        curve_key="consistency_curve",
    ),
    ContrastDimension(
        name="surprise",
        description="C3: Unexpected but justified choices",
        measurement_hint="Track novel elements that still fit the vision",
        curve_key="surprise_curve",
    ),
)


# =============================================================================
# Arc Phases (The Five)
# =============================================================================

STUDIO_ARC_PHASES = (
    PhaseDefinition(
        name="discovery",
        description="Finding the seed - excavating raw materials, patterns emerging",
        triggers=("archaeology_started", "sources_loaded", "first_pattern_found"),
    ),
    PhaseDefinition(
        name="exploration",
        description="Expanding possibilities - divergent thinking, many options",
        triggers=("multiple_directions", "options_generated", "vision_alternatives"),
    ),
    PhaseDefinition(
        name="commitment",
        description="Narrowing to vision - convergent selection, style crystallized",
        triggers=("vision_selected", "style_guide_generated", "direction_committed"),
    ),
    PhaseDefinition(
        name="execution",
        description="Producing assets - creation in flow, vision made manifest",
        triggers=("asset_production_started", "batch_in_progress", "pipeline_active"),
    ),
    PhaseDefinition(
        name="polish",
        description="Refining to completion - iteration, quality gates, final touches",
        triggers=("review_feedback", "refinement_cycle", "export_ready"),
    ),
)

STUDIO_ARC_TRANSITIONS = (
    ("discovery", "exploration"),  # Patterns found, explore possibilities
    ("exploration", "commitment"),  # Options weighed, vision crystallized
    ("exploration", "discovery"),  # Need more material, back to archaeology
    ("commitment", "execution"),  # Vision locked, begin production
    ("commitment", "exploration"),  # Vision rejected, explore alternatives
    ("execution", "polish"),  # Assets produced, refine quality
    ("execution", "commitment"),  # Execution reveals vision flaw
    ("polish", "execution"),  # Refinement requires new assets
    ("polish", "discovery"),  # Complete reset, new archaeological phase
)


# =============================================================================
# Voice Definitions (The Three)
# =============================================================================

STUDIO_VOICES = (
    VoiceDefinition(
        name="adversarial",
        question="Is this technically correct?",
        checks=(
            "format_valid",  # Asset meets format specs
            "dimensions_correct",  # Size/resolution requirements met
            "palette_compliant",  # Colors within defined palette
            "accessibility_met",  # WCAG requirements satisfied
        ),
    ),
    VoiceDefinition(
        name="creative",
        question="Is this interesting and novel?",
        checks=(
            "not_derivative",  # Not a simple copy
            "unexpected_element",  # Contains surprise
            "style_coherent",  # Fits the vision
            "aesthetic_quality",  # Meets taste threshold
        ),
    ),
    VoiceDefinition(
        name="advocate",
        question="Would Kent be delighted?",
        checks=(
            "joy_inducing",  # Sparks delight
            "tasteful",  # Daring but not gaudy
            "on_brand",  # Fits kgents philosophy
            "mirror_test",  # Feels like Kent on his best day
        ),
    ),
)


# =============================================================================
# Floor Checks (F1-F4)
# =============================================================================

STUDIO_FLOOR_CHECKS = (
    FloorCheckDefinition(
        name="provenance",
        threshold=1.0,
        comparison="==",
        unit="bool",
        description="F1: All elements have traceable source. No orphan assets.",
    ),
    FloorCheckDefinition(
        name="format_compliance",
        threshold=1.0,
        comparison="==",
        unit="bool",
        description="F2: Assets meet technical specifications (dimensions, format, encoding).",
    ),
    FloorCheckDefinition(
        name="style_coherence",
        threshold=0.8,
        comparison=">=",
        unit="ratio",
        description="F3: 80%+ alignment with style guide. Vision preserved.",
    ),
    FloorCheckDefinition(
        name="accessibility",
        threshold=1.0,
        comparison="==",
        unit="bool",
        description="F4: WCAG AA contrast ratios met. Inclusive by design.",
    ),
)


# =============================================================================
# Complete Algebra
# =============================================================================

STUDIO_QUALITY_ALGEBRA = QualityAlgebra(
    domain="creative_studio",
    description="Quality algebra for S-gent Creative Production Studio",
    contrast_dims=STUDIO_CONTRAST_DIMS,
    arc_phases=STUDIO_ARC_PHASES,
    arc_canonical_transitions=STUDIO_ARC_TRANSITIONS,
    voices=STUDIO_VOICES,
    floor_checks=STUDIO_FLOOR_CHECKS,
    # Weights: Voice-emphasized (creative decisions matter most)
    contrast_weight=0.25,
    arc_weight=0.25,
    voice_weight=0.50,
)


# =============================================================================
# Algorithm Constants
# =============================================================================

# Style coherence threshold (from F3)
STYLE_COHERENCE_THRESHOLD = 0.8

# Expression variance target (good balance of creativity vs. consistency)
EXPRESSION_TARGET_VARIANCE = 0.4

# Surprise ratio target (novel elements should be ~20% of output)
SURPRISE_RATIO_TARGET = 0.2


# =============================================================================
# Runtime Measurement Functions
# =============================================================================


def detect_arc_phase(
    sources_loaded: bool = False,
    patterns_found: int = 0,
    alternatives_generated: int = 0,
    vision_committed: bool = False,
    assets_produced: int = 0,
    in_review: bool = False,
    export_ready: bool = False,
) -> str:
    """
    Detect current creative arc phase based on studio state.

    Returns one of: discovery, exploration, commitment, execution, polish

    From studio.md Part V (arc phases).
    """
    if export_ready or in_review:
        return "polish"

    if assets_produced > 0 and vision_committed:
        return "execution"

    if vision_committed:
        return "commitment"

    if alternatives_generated > 1:
        return "exploration"

    if sources_loaded or patterns_found > 0:
        return "discovery"

    # Default to discovery if nothing started
    return "discovery"


def calculate_style_coherence(
    asset_style_scores: list[float],
    vision_style: dict[str, float],
) -> float:
    """
    Calculate style coherence between assets and vision.

    Returns coherence score 0-1 where 1 is perfect alignment.

    From studio.md F3: 80%+ alignment with style guide.
    """
    if not asset_style_scores:
        return 1.0  # No assets = vacuously coherent

    # Average style score across assets
    mean_score = sum(asset_style_scores) / len(asset_style_scores)
    return max(0.0, min(1.0, mean_score))


def measure_expression_contrast(
    outputs: list[dict[str, Any]],
    uniqueness_threshold: float = 0.3,
) -> float:
    """
    Measure expression contrast across outputs.

    Good contrast = variety within coherence.
    Poor contrast = either too uniform or too chaotic.

    Returns score 0-1 where 1 is optimal contrast.
    """
    if len(outputs) < 2:
        return 0.5  # Neutral if insufficient data

    # Calculate pairwise uniqueness scores
    uniqueness_scores = []
    for i, out1 in enumerate(outputs):
        for out2 in outputs[i + 1 :]:
            score = _compute_output_difference(out1, out2)
            uniqueness_scores.append(score)

    if not uniqueness_scores:
        return 0.5

    mean_uniqueness = sum(uniqueness_scores) / len(uniqueness_scores)

    # Optimal: moderate uniqueness (not clones, not chaos)
    optimal_uniqueness = EXPRESSION_TARGET_VARIANCE
    deviation = abs(mean_uniqueness - optimal_uniqueness)

    # Score: 1.0 at optimal, decreasing as we deviate
    score = max(0.0, 1.0 - deviation * 2)
    return score


def _compute_output_difference(out1: dict[str, Any], out2: dict[str, Any]) -> float:
    """Compute difference score between two outputs."""
    # Simple implementation: compare keys present
    keys1 = set(out1.keys())
    keys2 = set(out2.keys())

    if not keys1 and not keys2:
        return 0.0

    common = keys1 & keys2
    union = keys1 | keys2

    if not union:
        return 0.0

    # Basic Jaccard-based difference
    return 1.0 - len(common) / len(union)


def measure_surprise_ratio(
    outputs: list[dict[str, Any]],
    style_guide: dict[str, Any],
) -> float:
    """
    Measure surprise ratio: novel elements that still fit.

    Returns ratio 0-1 where SURPRISE_RATIO_TARGET is optimal.
    """
    if not outputs:
        return SURPRISE_RATIO_TARGET  # Neutral

    surprise_count = 0
    total_elements = 0

    for output in outputs:
        elements = output.get("elements", [])
        for element in elements:
            total_elements += 1
            if element.get("novel", False) and element.get("fits_style", False):
                surprise_count += 1

    if total_elements == 0:
        return SURPRISE_RATIO_TARGET

    actual_ratio = surprise_count / total_elements

    # Score based on closeness to target
    deviation = abs(actual_ratio - SURPRISE_RATIO_TARGET)
    score = max(0.0, 1.0 - deviation * 3)
    return score


def check_provenance(assets: list[dict[str, Any]]) -> bool:
    """
    Check F1: All assets have traceable source.

    Returns True if all assets have valid provenance.
    """
    for asset in assets:
        if not asset.get("source_id") and not asset.get("provenance"):
            return False
    return True


def check_format_compliance(
    assets: list[dict[str, Any]],
    requirements: dict[str, dict[str, Any]],
) -> bool:
    """
    Check F2: Assets meet technical specifications.

    Returns True if all assets meet format requirements.
    """
    for asset in assets:
        asset_type = asset.get("type", "unknown")
        type_reqs = requirements.get(asset_type, {})

        # Check dimensions if specified
        if "width" in type_reqs:
            if asset.get("width", 0) != type_reqs["width"]:
                return False
        if "height" in type_reqs:
            if asset.get("height", 0) != type_reqs["height"]:
                return False

        # Check format if specified
        if "format" in type_reqs:
            if asset.get("format") != type_reqs["format"]:
                return False

    return True


def check_accessibility(
    colors: list[tuple[int, int, int]],
    background: tuple[int, int, int] = (255, 255, 255),
    min_contrast_ratio: float = 4.5,  # WCAG AA
) -> bool:
    """
    Check F4: WCAG AA contrast ratios met.

    Returns True if all foreground colors meet minimum contrast.
    """
    for color in colors:
        ratio = _compute_contrast_ratio(color, background)
        if ratio < min_contrast_ratio:
            return False
    return True


def _compute_contrast_ratio(
    fg: tuple[int, int, int],
    bg: tuple[int, int, int],
) -> float:
    """Compute WCAG contrast ratio between foreground and background."""

    def relative_luminance(rgb: tuple[int, int, int]) -> float:
        r, g, b = [x / 255.0 for x in rgb]
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)

    lighter = max(l1, l2)
    darker = min(l1, l2)

    return (lighter + 0.05) / (darker + 0.05)


def compute_voice_verdict(
    asset: dict[str, Any],
    style_guide: dict[str, Any],
    voice: str,
) -> tuple[bool, float, str]:
    """
    Compute voice verdict for an asset.

    Returns (passed, confidence, reasoning).
    """
    if voice == "adversarial":
        # Technical correctness
        format_ok = asset.get("format_valid", True)
        dims_ok = asset.get("dimensions_correct", True)
        palette_ok = asset.get("palette_compliant", True)
        access_ok = asset.get("accessibility_met", True)

        passed = all([format_ok, dims_ok, palette_ok, access_ok])
        confidence = sum([format_ok, dims_ok, palette_ok, access_ok]) / 4
        violations = []
        if not format_ok:
            violations.append("format_invalid")
        if not dims_ok:
            violations.append("dimensions_wrong")
        if not palette_ok:
            violations.append("off_palette")
        if not access_ok:
            violations.append("accessibility_failed")

        reasoning = "Technically correct" if passed else f"Violations: {violations}"
        return passed, confidence, reasoning

    elif voice == "creative":
        # Novelty and interest
        not_derivative = asset.get("originality_score", 0.5) > 0.3
        has_surprise = asset.get("surprise_score", 0.0) > 0.1
        style_coherent = asset.get("style_score", 0.5) > 0.6
        aesthetic_ok = asset.get("aesthetic_score", 0.5) > 0.5

        passed = all([not_derivative, style_coherent]) and (has_surprise or aesthetic_ok)
        confidence = (
            asset.get("originality_score", 0.5) * 0.3
            + asset.get("style_score", 0.5) * 0.4
            + asset.get("aesthetic_score", 0.5) * 0.3
        )
        reasoning = "Creative and novel" if passed else "Lacks creative merit"
        return passed, confidence, reasoning

    elif voice == "advocate":
        # Kent's delight
        joy = asset.get("joy_score", 0.5) > 0.6
        tasteful = asset.get("taste_score", 0.5) > 0.5
        on_brand = asset.get("brand_score", 0.5) > 0.6
        mirror = asset.get("mirror_test_score", 0.5) > 0.5

        passed = sum([joy, tasteful, on_brand, mirror]) >= 3
        confidence = (
            asset.get("joy_score", 0.5) * 0.3
            + asset.get("taste_score", 0.5) * 0.2
            + asset.get("brand_score", 0.5) * 0.25
            + asset.get("mirror_test_score", 0.5) * 0.25
        )
        reasoning = "Kent would be delighted" if passed else "Does not spark joy"
        return passed, confidence, reasoning

    return False, 0.0, f"Unknown voice: {voice}"


# =============================================================================
# Registration
# =============================================================================


def register_studio_algebra(overwrite: bool = False) -> None:
    """
    Register the Studio algebra with the central registry.

    Args:
        overwrite: If True, replace existing registration.

    Example:
        >>> from services.studio.quality import register_studio_algebra
        >>> register_studio_algebra()
    """
    if overwrite:
        register_algebra_overwrite(STUDIO_QUALITY_ALGEBRA)
    else:
        register_algebra(STUDIO_QUALITY_ALGEBRA)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Dimensions
    "STUDIO_CONTRAST_DIMS",
    "STUDIO_ARC_PHASES",
    "STUDIO_ARC_TRANSITIONS",
    "STUDIO_VOICES",
    "STUDIO_FLOOR_CHECKS",
    # Algebra
    "STUDIO_QUALITY_ALGEBRA",
    # Constants
    "STYLE_COHERENCE_THRESHOLD",
    "EXPRESSION_TARGET_VARIANCE",
    "SURPRISE_RATIO_TARGET",
    # Runtime functions
    "detect_arc_phase",
    "calculate_style_coherence",
    "measure_expression_contrast",
    "measure_surprise_ratio",
    "check_provenance",
    "check_format_compliance",
    "check_accessibility",
    "compute_voice_verdict",
    # Registration
    "register_studio_algebra",
]
