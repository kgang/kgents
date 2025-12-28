"""
WASM Survivors Quality Algebra.

Domain-specific instantiation of the Experience Quality Operad for
the WASM Survivors: Witnessed Run Lab pilot.

Philosophy:
    "The run is the proof. The build is the claim. The ghost is the road not taken."

This algebra defines:
- C1-C7 contrast dimensions for gameplay variety
- HOPE → FLOW → CRISIS → TRIUMPH/GRIEF emotional arc
- Three voices: Adversarial (correct), Creative (bold), Advocate (fun)
- F1-F10 floor checks (the sacred Fun Floor)

See: pilots/wasm-survivors-witnessed-run-lab/PROTO_SPEC.md
See: spec/theory/domains/wasm-survivors-quality.md
"""

from __future__ import annotations

from ..types import (
    ContrastDimension,
    PhaseDefinition,
    VoiceDefinition,
    FloorCheckDefinition,
    QualityAlgebra,
)
from ..algebras import register_algebra, register_algebra_overwrite

# =============================================================================
# C1-C7: Contrast Dimensions
# =============================================================================

WASM_CONTRAST_DIMS = (
    ContrastDimension(
        name="breath",
        description="C1: Intensity oscillation (crescendo <-> silence)",
        measurement_hint="Track combat intensity over time, compute variance",
        curve_key="intensity_curve",
    ),
    ContrastDimension(
        name="scarcity",
        description="C2: Resource oscillation (feast <-> famine)",
        measurement_hint="Track XP gain rate and health over time",
        curve_key="resource_curve",
    ),
    ContrastDimension(
        name="tempo",
        description="C3: Speed oscillation (fast combat <-> slow choices)",
        measurement_hint="Track actions-per-second over time",
        curve_key="tempo_curve",
    ),
    ContrastDimension(
        name="stakes",
        description="C4: Risk oscillation (safe <-> lethal)",
        measurement_hint="Track health_fraction * threat_density",
        curve_key="stakes_curve",
    ),
    ContrastDimension(
        name="anticipation",
        description="C5: Tension oscillation (calm <-> dread)",
        measurement_hint="Track silence_duration before boss/elite",
        curve_key="anticipation_curve",
    ),
    ContrastDimension(
        name="reward",
        description="C6: Gratification oscillation (drought <-> burst)",
        measurement_hint="Track xp_gained per second",
        curve_key="reward_curve",
    ),
    ContrastDimension(
        name="identity",
        description="C7: Choice oscillation (exploration <-> commitment)",
        measurement_hint="Track build_diversity_index over waves",
        curve_key="identity_curve",
    ),
)

# =============================================================================
# Arc Phases
# =============================================================================

WASM_ARC_PHASES = (
    PhaseDefinition(
        name="hope",
        description="'I can do this' — Early game optimism",
        triggers=("wave < 3", "health > 0.7", "no_recent_damage"),
    ),
    PhaseDefinition(
        name="flow",
        description="'I'm unstoppable' — In the zone",
        triggers=("kill_streak > 10", "combo_active", "health > 0.5"),
    ),
    PhaseDefinition(
        name="crisis",
        description="'Oh no, maybe not' — Tension peak",
        triggers=("health < 0.3", "surrounded", "boss_active"),
    ),
    PhaseDefinition(
        name="triumph",
        description="'I DID IT!' — Victory moment",
        triggers=("boss_defeated", "wave_survived_at_critical"),
    ),
    PhaseDefinition(
        name="grief",
        description="'So close...' — Defeat with clarity",
        triggers=("death", "game_over"),
    ),
)

WASM_ARC_TRANSITIONS = (
    ("hope", "flow"),  # Natural progression
    ("flow", "crisis"),  # Challenge ramp
    ("crisis", "triumph"),  # Successful survival
    ("crisis", "grief"),  # Death
    ("triumph", "hope"),  # Reset for next challenge
    ("hope", "crisis"),  # Sudden threat (boss spawn)
    ("flow", "hope"),  # Lull after intensity
)

# =============================================================================
# Voice Definitions
# =============================================================================

WASM_VOICES = (
    VoiceDefinition(
        name="adversarial",
        question="Is this technically correct and fair?",
        checks=(
            "no_impossible_deaths",  # Every death is avoidable
            "clear_feedback",  # No silent failures
            "consistent_rules",  # Physics/collision work
            "death_attribution",  # Player knows why they died
        ),
    ),
    VoiceDefinition(
        name="creative",
        question="Is this interesting and novel?",
        checks=(
            "build_diversity",  # Multiple viable builds
            "emergent_synergies",  # 1+1 > 2 somewhere
            "contrast_variety",  # Not monotonous
            "ghost_alternatives",  # Real choices, not illusion
        ),
    ),
    VoiceDefinition(
        name="advocate",
        question="Is this fun and engaging?",
        checks=(
            "retry_rate",  # > 80% immediate retry
            "one_more_run",  # Player says it
            "emotional_peaks",  # Moments worth clipping
            "input_responsiveness",  # < 16ms response
        ),
    ),
)

# =============================================================================
# Floor Checks (F1-F10)
# =============================================================================

WASM_FLOOR_CHECKS = (
    FloorCheckDefinition(
        name="input_latency",
        threshold=16.0,
        comparison="<=",
        unit="ms",
        description="F1: < 16ms response. WASD feels tight.",
    ),
    FloorCheckDefinition(
        name="kill_feedback",
        threshold=1.0,
        comparison="==",
        unit="bool",
        description="F2: Death = particles + sound + XP burst. No silent kills.",
    ),
    FloorCheckDefinition(
        name="levelup_moment",
        threshold=1.0,
        comparison="==",
        unit="bool",
        description="F3: Pause + choice + fanfare. A moment, not a stat bump.",
    ),
    FloorCheckDefinition(
        name="death_clarity",
        threshold=2.0,
        comparison="<=",
        unit="seconds",
        description="F4: 'I died because X' in < 2 seconds.",
    ),
    FloorCheckDefinition(
        name="restart_speed",
        threshold=3.0,
        comparison="<=",
        unit="seconds",
        description="F5: < 3 seconds from death to new run. No menus.",
    ),
    FloorCheckDefinition(
        name="build_identity",
        threshold=5,
        comparison="<=",
        unit="waves",
        description="F6: By wave 5, player can name their build.",
    ),
    FloorCheckDefinition(
        name="synergy_exists",
        threshold=1.0,
        comparison=">=",
        unit="count",
        description="F7: 2+ upgrades combine for emergent power. 1+1 > 2 somewhere.",
    ),
    FloorCheckDefinition(
        name="escalation_visible",
        threshold=1.0,
        comparison="==",
        unit="bool",
        description="F8: Wave 10 is obviously harder than wave 1. Visually, sonically.",
    ),
    FloorCheckDefinition(
        name="boss_moment",
        threshold=1.0,
        comparison=">=",
        unit="count",
        description="F9: At least one 'oh shit' enemy per run.",
    ),
    FloorCheckDefinition(
        name="health_visible",
        threshold=1.0,
        comparison="==",
        unit="bool",
        description="F10: Always know your health. Bar, not number.",
    ),
)

# =============================================================================
# Complete Algebra
# =============================================================================

WASM_QUALITY_ALGEBRA = QualityAlgebra(
    domain="wasm_survivors",
    description="Quality algebra for WASM Survivors witnessed runs",
    contrast_dims=WASM_CONTRAST_DIMS,
    arc_phases=WASM_ARC_PHASES,
    arc_canonical_transitions=WASM_ARC_TRANSITIONS,
    voices=WASM_VOICES,
    floor_checks=WASM_FLOOR_CHECKS,
    # Weights: C=0.35, A=0.35, V=0.30 (balanced)
    contrast_weight=0.35,
    arc_weight=0.35,
    voice_weight=0.30,
)

# =============================================================================
# Algorithm Constants
# =============================================================================

# From spec Part I
CONTRAST_ADAPTATION_THRESHOLD = 0.3
CONTRAST_TARGET = 0.6

# From spec Part V Section 5.2
GALOIS_LOSS_THRESHOLD = 0.4

# From spec Part V Section 5.1
BUILD_SHIFT_THRESHOLD = 0.3


# =============================================================================
# Runtime Measurement Functions
# =============================================================================


def detect_arc_phase(
    health_fraction: float,
    wave: int,
    threats: int,
    kill_streak: int,
    combo_active: bool,
    boss_active: bool,
    boss_just_defeated: bool = False,
    just_died: bool = False,
) -> str:
    """
    Detect current emotional arc phase based on game state.

    Returns one of: hope, flow, crisis, triumph, grief

    From PROTO_SPEC.md E1:
    - HOPE: wave < 3 AND health > 0.7 AND no_recent_damage
    - FLOW: kill_streak > 10 AND combo_active AND health > 0.5
    - CRISIS: health < 0.3 AND (threats > 5 OR boss_active)
    - TRIUMPH: boss_defeated OR wave_survived_at_critical
    - GRIEF: death
    """
    if just_died:
        return "grief"

    if boss_just_defeated or (health_fraction < 0.3 and threats == 0):
        return "triumph"

    if health_fraction < 0.3 and (threats > 5 or boss_active):
        return "crisis"

    if kill_streak > 10 and combo_active and health_fraction > 0.5:
        return "flow"

    if wave < 3 and health_fraction > 0.7:
        return "hope"

    # Default based on situation
    if health_fraction < 0.4:
        return "crisis"
    if combo_active:
        return "flow"
    return "hope"


def calculate_galois_loss(
    principle_weights: dict[str, float],
    target_style: dict[str, float],
) -> float:
    """
    Calculate Galois loss (style drift) between current weights and target.

    From PROTO_SPEC.md L4:
    galois_loss = sum((principle_weight - target_weight)^2 for each principle) / n

    Lower is better. Threshold at 0.4 indicates major drift.
    """
    if not principle_weights or not target_style:
        return 0.0

    total_squared_diff = 0.0
    n = 0

    for key in principle_weights:
        if key in target_style:
            diff = principle_weights[key] - target_style[key]
            total_squared_diff += diff * diff
            n += 1

    return total_squared_diff / n if n > 0 else 0.0


def is_major_build_shift(
    old_weights: dict[str, float],
    new_weights: dict[str, float],
    threshold: float = 0.3,
) -> tuple[bool, str | None]:
    """
    Detect if a build shift has occurred (D3).

    Returns (is_shift, dominant_change)

    A shift occurs when the dominant principle changes OR
    when any single weight changes by more than threshold.
    """
    if not old_weights or not new_weights:
        return False, None

    # Check for dominant change
    old_dominant = max(old_weights.items(), key=lambda x: x[1])[0]
    new_dominant = max(new_weights.items(), key=lambda x: x[1])[0]

    if old_dominant != new_dominant:
        return True, new_dominant

    # Check for threshold breach
    for key in old_weights:
        if key in new_weights:
            if abs(old_weights[key] - new_weights[key]) > threshold:
                return True, key

    return False, None


def calculate_clutch_intensity(
    health_fraction: float,
    threat_count: int,
) -> tuple[float, str]:
    """
    Calculate clutch moment intensity based on game state.

    From PROTO_SPEC.md S3:
    - FULL CLUTCH: health < 0.15 AND threats > 3
    - MEDIUM CLUTCH: health < 0.25 AND threats > 5
    - CRITICAL: health < 0.10

    Returns (intensity 0-1, mode_name)
    """
    # Full clutch
    if health_fraction < 0.15 and threat_count > 3:
        return 1.0, "full"

    # Medium clutch
    if health_fraction < 0.25 and threat_count > 5:
        return 0.7, "medium"

    # Critical
    if health_fraction < 0.10:
        return 0.9, "critical"

    # Low tension
    if health_fraction < 0.30:
        return 0.4, "tense"

    return 0.0, "normal"


def calculate_contrast_score(
    intensity_history: list[float],
    window_size: int = 10,
) -> float:
    """
    Calculate contrast score from intensity history.

    Good contrast = oscillation between highs and lows.
    Poor contrast = flat line or random noise.

    Returns score 0-1 where 1 is optimal contrast.
    """
    if len(intensity_history) < window_size:
        return 0.5  # Neutral if not enough data

    window = intensity_history[-window_size:]

    # Calculate variance (we want some, but not too much)
    mean = sum(window) / len(window)
    variance = sum((x - mean) ** 2 for x in window) / len(window)

    # Optimal variance is around 0.15 (good oscillation)
    # Too low = flat, too high = chaotic
    optimal_variance = 0.15
    deviation = abs(variance - optimal_variance)

    # Score: 1.0 at optimal, decreasing as we deviate
    score = max(0.0, 1.0 - deviation * 3)

    return score


def measure_escalation_effectiveness(
    wave: int,
    juice_multiplier: float,
    expected_base: float = 1.0,
) -> float:
    """
    Measure how well escalation is working.

    From S2: juice_intensity = base * wave_factor * combo_factor * stakes_factor

    Returns effectiveness 0-1 where 1 means escalation is scaling properly.
    """
    # Expected multiplier at this wave (roughly 1 + wave * 0.05)
    expected_multiplier = expected_base + wave * 0.05

    # How close are we to expected?
    ratio = juice_multiplier / expected_multiplier if expected_multiplier > 0 else 1.0

    # Perfect if ratio is 1.0, penalty for deviation
    effectiveness = max(0.0, 1.0 - abs(ratio - 1.0) * 0.5)

    return effectiveness


# =============================================================================
# Registration
# =============================================================================


def register_wasm_algebra(overwrite: bool = False) -> None:
    """
    Register the WASM Survivors algebra with the central registry.

    Args:
        overwrite: If True, replace existing registration.

    Example:
        >>> from services.experience_quality.domains.wasm_survivors import register_wasm_algebra
        >>> register_wasm_algebra()
    """
    if overwrite:
        register_algebra_overwrite(WASM_QUALITY_ALGEBRA)
    else:
        register_algebra(WASM_QUALITY_ALGEBRA)


# =============================================================================
# Module Exports
# =============================================================================

__all__ = [
    # Dimensions
    "WASM_CONTRAST_DIMS",
    "WASM_ARC_PHASES",
    "WASM_ARC_TRANSITIONS",
    "WASM_VOICES",
    "WASM_FLOOR_CHECKS",
    # Algebra
    "WASM_QUALITY_ALGEBRA",
    # Constants
    "CONTRAST_ADAPTATION_THRESHOLD",
    "CONTRAST_TARGET",
    "GALOIS_LOSS_THRESHOLD",
    "BUILD_SHIFT_THRESHOLD",
    # Runtime functions
    "detect_arc_phase",
    "calculate_galois_loss",
    "is_major_build_shift",
    "calculate_clutch_intensity",
    "calculate_contrast_score",
    "measure_escalation_effectiveness",
    # Registration
    "register_wasm_algebra",
]
