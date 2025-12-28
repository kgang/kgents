# WASM Survivors Quality Algebra

> *"The run is the proof. The build is the claim. The ghost is the road not taken."*

**Version**: 1.0
**Status**: Draft
**Date**: 2025-12-27
**Parent**: `spec/theory/experience-quality-operad.md`
**Pilot**: `pilots/wasm-survivors-witnessed-run-lab/PROTO_SPEC.md`

---

## Abstract

This document defines the **WASM Survivors Quality Algebra** — a domain-specific instantiation of the Experience Quality Operad for the WASM Survivors game. It maps the abstract Tetrad (Contrast, Arc, Voice, Floor) to concrete game mechanics and measurements.

---

## Part I: Contrast Dimensions (C1-C7)

### Definition

WASM Survivors contrast is measured across seven dimensions, each tracking variance over time:

```python
WASM_CONTRAST_DIMS = (
    ContrastDimension(
        name="breath",
        description="C1: Intensity oscillation (crescendo <-> silence)",
        measurement_hint="Track spawn_rate * enemy_count over time",
        curve_key="intensity_curve",
    ),
    ContrastDimension(
        name="scarcity",
        description="C2: Resource oscillation (feast <-> famine)",
        measurement_hint="Track xp_available / xp_needed ratio",
        curve_key="resource_curve",
    ),
    ContrastDimension(
        name="tempo",
        description="C3: Speed oscillation (fast <-> slow choices)",
        measurement_hint="Track time_between_decisions",
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
```

### Measurement Algorithm

For each dimension, contrast is the normalized variance of the signal:

```python
def measure_contrast_dimension(curve: list[float]) -> float:
    """
    Measure contrast for a single dimension.

    High variance = high contrast = good.
    Normalize to [0, 1] using expected range.
    """
    if len(curve) < 2:
        return 0.5  # Neutral if insufficient data

    mean = sum(curve) / len(curve)
    variance = sum((x - mean) ** 2 for x in curve) / len(curve)
    std_dev = variance ** 0.5

    # Normalize: we expect std_dev in [0, 0.5] range for good contrast
    # Map [0, 0.5] -> [0, 1]
    normalized = min(1.0, std_dev * 2)
    return normalized
```

### Contrast Threshold

From PROTO_SPEC: `contrast < 0.3` triggers adaptation.

```python
CONTRAST_ADAPTATION_THRESHOLD = 0.3
CONTRAST_TARGET = 0.6  # Ideal contrast level
```

---

## Part II: Arc Phases

### Definition

WASM Survivors uses the standard five-phase emotional arc:

```python
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
    ("hope", "flow"),      # Natural progression
    ("flow", "crisis"),    # Challenge ramp
    ("crisis", "triumph"), # Successful survival
    ("crisis", "grief"),   # Death
    ("triumph", "hope"),   # Reset for next challenge
    ("hope", "crisis"),    # Sudden threat (boss spawn)
    ("flow", "hope"),      # Lull after intensity
)
```

### Phase Detection Algorithm

```python
def detect_phase(game_state: GameState) -> EmotionalPhase:
    """
    Classify current game state into emotional phase.

    Priority: grief > crisis > triumph > flow > hope
    """
    if game_state.is_dead:
        return EmotionalPhase.GRIEF

    if game_state.boss_just_defeated:
        return EmotionalPhase.TRIUMPH

    # Crisis detection
    is_crisis = (
        game_state.health_fraction < 0.3
        or game_state.threat_count > 20
        or game_state.boss_active
    )
    if is_crisis:
        return EmotionalPhase.CRISIS

    # Flow detection
    is_flow = (
        game_state.kill_streak > 10
        or game_state.combo_multiplier > 2
    ) and game_state.health_fraction > 0.5
    if is_flow:
        return EmotionalPhase.FLOW

    # Default: hope
    return EmotionalPhase.HOPE
```

---

## Part III: Voice Definitions

### The Three Voices

```python
WASM_VOICES = (
    VoiceDefinition(
        name="adversarial",
        question="Is this technically correct and fair?",
        checks=(
            "no_impossible_deaths",      # Every death is avoidable
            "clear_feedback",            # No silent failures
            "consistent_rules",          # Physics/collision work
            "death_attribution",         # Player knows why they died
        ),
    ),
    VoiceDefinition(
        name="creative",
        question="Is this interesting and novel?",
        checks=(
            "build_diversity",           # Multiple viable builds
            "emergent_synergies",        # 1+1 > 2 somewhere
            "contrast_variety",          # Not monotonous
            "ghost_alternatives",        # Real choices, not illusion
        ),
    ),
    VoiceDefinition(
        name="advocate",
        question="Is this fun and engaging?",
        checks=(
            "retry_rate",                # > 80% immediate retry
            "one_more_run",              # Player says it
            "emotional_peaks",           # Moments worth clipping
            "input_responsiveness",      # < 16ms response
        ),
    ),
)
```

### Voice Check Implementation

```python
def check_adversarial(run: RunTrace, spec: Spec) -> VoiceVerdict:
    """Check adversarial voice: Is it correct?"""
    violations = []

    # Check death attribution
    if run.death_cause is None and run.ended_in_death:
        violations.append("death_without_attribution")

    # Check feedback density
    silent_actions = count_silent_actions(run)
    if silent_actions > 0:
        violations.append(f"silent_actions:{silent_actions}")

    passed = len(violations) == 0
    confidence = 1.0 - (len(violations) * 0.2)

    return VoiceVerdict(
        passed=passed,
        confidence=max(0.0, confidence),
        reasoning="All laws satisfied" if passed else f"Violations: {violations}",
        violations=tuple(violations),
    )
```

---

## Part IV: Floor Checks (F1-F10)

### The Fun Floor

From PROTO_SPEC, these are non-negotiable:

```python
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
```

---

## Part V: Algorithm Specifications

### 5.1 Major Build Shift Detection (L1)

A "major build shift" occurs when the build's primary principle changes:

```python
def detect_build_shift(
    prev_weights: PrincipleWeights,
    curr_weights: PrincipleWeights,
    threshold: float = 0.3,
) -> bool:
    """
    Detect if a major build shift occurred.

    A shift is major if ANY principle changes by more than threshold
    AND the primary principle changes.
    """
    # Check primary principle change
    prev_primary = max(
        [("aggression", prev_weights.aggression),
         ("consistency", prev_weights.consistency),
         ("risk_tolerance", prev_weights.risk_tolerance),
         ("synergy_seeking", prev_weights.synergy_seeking)],
        key=lambda x: x[1]
    )[0]

    curr_primary = max(
        [("aggression", curr_weights.aggression),
         ("consistency", curr_weights.consistency),
         ("risk_tolerance", curr_weights.risk_tolerance),
         ("synergy_seeking", curr_weights.synergy_seeking)],
        key=lambda x: x[1]
    )[0]

    primary_changed = prev_primary != curr_primary

    # Check magnitude of change
    deltas = [
        abs(curr_weights.aggression - prev_weights.aggression),
        abs(curr_weights.consistency - prev_weights.consistency),
        abs(curr_weights.risk_tolerance - prev_weights.risk_tolerance),
        abs(curr_weights.synergy_seeking - prev_weights.synergy_seeking),
    ]

    significant_change = any(d > threshold for d in deltas)

    return primary_changed and significant_change
```

### 5.2 Galois Loss Threshold (L2)

```python
GALOIS_LOSS_THRESHOLD = 0.4  # Above this = significant drift

def compute_galois_loss(
    current_weights: PrincipleWeights,
    target_style: PrincipleWeights,
) -> float:
    """
    Compute Galois loss between current build and target style.

    Loss is the Euclidean distance in principle space, normalized to [0, 1].
    """
    deltas = [
        (current_weights.aggression - target_style.aggression) ** 2,
        (current_weights.consistency - target_style.consistency) ** 2,
        (current_weights.risk_tolerance - target_style.risk_tolerance) ** 2,
        (current_weights.synergy_seeking - target_style.synergy_seeking) ** 2,
    ]

    # Max possible distance is sqrt(4) = 2 (all dimensions from 0 to 1)
    raw_distance = sum(deltas) ** 0.5
    normalized = raw_distance / 2.0

    return normalized
```

### 5.3 High-Risk Classification (L4)

```python
def classify_risk(game_state: GameState) -> Literal["low", "medium", "high", "critical"]:
    """
    Classify current risk level.

    Risk = health_factor * threat_factor * situation_factor
    """
    # Health factor (lower health = higher risk)
    health_factor = 1.0 - game_state.health_fraction

    # Threat factor (more threats = higher risk)
    threat_factor = min(1.0, game_state.threat_count / 30)

    # Situation factor (boss, surrounded, etc.)
    situation_factor = 0.0
    if game_state.boss_active:
        situation_factor += 0.5
    if game_state.surrounded:
        situation_factor += 0.3
    situation_factor = min(1.0, situation_factor)

    # Combined risk score
    risk = (health_factor * 0.4 + threat_factor * 0.3 + situation_factor * 0.3)

    if risk >= 0.8:
        return "critical"
    elif risk >= 0.5:
        return "high"
    elif risk >= 0.2:
        return "medium"
    else:
        return "low"
```

### 5.4 Player Skill Estimation (D1)

```python
@dataclass
class PlayerSkillEstimate:
    """Estimated player skill level for adaptive difficulty."""

    reaction_score: float      # 0-1: Based on dodge success rate
    positioning_score: float   # 0-1: Based on damage avoidance
    decision_score: float      # 0-1: Based on build coherence
    overall: float             # Weighted combination

def estimate_player_skill(
    run_history: list[RunTrace],
    window_size: int = 5,
) -> PlayerSkillEstimate:
    """
    Estimate player skill from recent runs.

    Uses the last `window_size` runs to compute skill estimate.
    """
    if not run_history:
        return PlayerSkillEstimate(0.5, 0.5, 0.5, 0.5)

    recent = run_history[-window_size:]

    # Reaction: waves survived / average enemy count
    reaction_scores = [
        r.final_wave / max(1, sum(m.context.get("enemy_count", 1) for m in r.marks) / len(r.marks))
        for r in recent
    ]
    reaction = min(1.0, sum(reaction_scores) / len(reaction_scores))

    # Positioning: average health at death (or 1.0 for victory)
    health_scores = [
        1.0 if not r.ended_in_death else r.final_health_fraction
        for r in recent
    ]
    positioning = sum(health_scores) / len(health_scores)

    # Decision: build coherence (Galois loss inverted)
    decision_scores = [
        1.0 - r.galois_loss for r in recent
    ]
    decision = sum(decision_scores) / len(decision_scores)

    overall = reaction * 0.4 + positioning * 0.35 + decision * 0.25

    return PlayerSkillEstimate(
        reaction_score=reaction,
        positioning_score=positioning,
        decision_score=decision,
        overall=overall,
    )
```

### 5.5 Juice Scaling Curve (S2)

```python
def compute_juice_multiplier(wave: int, combo: int, stakes: float) -> float:
    """
    Compute juice multiplier for visual/audio feedback.

    Juice scales with wave, combo, and stakes (exponential).
    """
    # Wave contribution (1.0 at wave 1, 2.0 at wave 10)
    wave_factor = 1.0 + (wave - 1) * 0.11

    # Combo contribution (1.0 at combo 1, up to 1.5 at combo 10+)
    combo_factor = 1.0 + min(0.5, combo * 0.05)

    # Stakes contribution (critical stakes = 1.5x)
    stakes_factor = 1.0 + stakes * 0.5

    return wave_factor * combo_factor * stakes_factor
```

---

## Part VI: Complete Algebra Definition

```python
from services.experience_quality.types import (
    QualityAlgebra,
    ContrastDimension,
    PhaseDefinition,
    VoiceDefinition,
    FloorCheckDefinition,
)

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

# Registration at game initialization
from services.experience_quality.algebras import register_algebra
register_algebra(WASM_QUALITY_ALGEBRA)
```

---

## Part VII: Integration Points

### 7.1 Game Loop Integration

```python
class WASMWitnessLayer:
    """
    Non-blocking witness layer for WASM Survivors.

    Maintains < 1ms overhead per mark emission.
    """

    def __init__(self):
        self.mark_queue: asyncio.Queue[GameMark] = asyncio.Queue(maxsize=1000)
        self.quality_buffer: SharedBuffer[ExperienceQuality] = SharedBuffer()
        self.trace: list[GameMark] = []

    async def emit_mark(self, mark: GameMark) -> None:
        """
        Non-blocking mark emission.

        If queue is full, drops oldest mark (better than blocking game loop).
        """
        try:
            self.mark_queue.put_nowait(mark)
        except asyncio.QueueFull:
            # Drop oldest, add new
            try:
                self.mark_queue.get_nowait()
                self.mark_queue.put_nowait(mark)
            except asyncio.QueueEmpty:
                pass

    async def process_marks(self) -> None:
        """Background worker: processes marks, updates quality."""
        while True:
            mark = await self.mark_queue.get()
            self.trace.append(mark)

            # Measure quality periodically (not every mark)
            if len(self.trace) % 10 == 0:
                experience = Experience(
                    id=f"run_{mark.run_id}",
                    type="run",
                    domain="wasm_survivors",
                    data=self._extract_curves(),
                )
                quality = measure_quality(experience, WASM_QUALITY_ALGEBRA)
                self.quality_buffer.write(quality)
```

### 7.2 Crystal Compression

```python
async def crystallize_run(trace: RunTrace) -> RunCrystal:
    """
    Compress a run trace into a crystal.

    The crystal is a proof of the run's meaning.
    """
    # Find pivots (major build shifts)
    pivots = find_pivots(trace)

    # Record ghosts (unchosen paths)
    ghosts = extract_ghosts(trace)

    # Compute final weights
    weights = compute_final_weights(trace)

    # Generate claim (one-sentence description)
    claim = generate_claim(pivots, weights, ghosts)

    return RunCrystal(
        run_id=trace.run_id,
        claim=claim,
        pivots=pivots,
        ghosts=ghosts,
        weights=weights,
        compression_ratio=len(trace.marks) / (len(pivots) + 1),
        shareable=True,
    )
```

---

## Cross-References

- `spec/theory/experience-quality-operad.md` — Parent operad specification
- `pilots/wasm-survivors-witnessed-run-lab/PROTO_SPEC.md` — Pilot specification
- `impl/claude/services/experience_quality/` — Implementation
- `impl/claude/services/witness/` — Witness infrastructure

---

*"The run is the proof. The build is the claim. The ghost is the road not taken."*
