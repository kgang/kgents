/**
 * THE BALL Formation System - Configuration
 *
 * All timing, damage, and tuning values in one place.
 * Balance changes from Run 037:
 * - Reduced knockback across the board (feels fairer)
 * - Increased lunge windup/travel time (dodgeable)
 * - Knockback hierarchy: boundary < punch < lunge
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part XI Phase 1)
 */

// =============================================================================
// Phase Configuration
// =============================================================================

export interface BallPhaseConfig {
  // RUN 039: Gathering phase (pre-formation telegraph)
  gatheringDuration: number;        // How long bees travel to positions
  gatheringBeeSpeed: number;        // Speed bees travel during gathering (px/sec)
  // Main phases
  formingDuration: number;
  silenceDuration: number;
  constrictDuration: number;
  initialRadius: number;
  finalRadius: number;
  minBeesForBall: number;
  minBeesToMaintain: number;        // Ball dissolves if bees drop below this
  minWaveForBall: number;
  // Multi-ball dynamics
  // RUN 039: Dynamic formation cooldown
  formationCooldownMax: number;       // Cooldown at early waves (ms)
  formationCooldownMin: number;       // Cooldown at late waves (ms)
  formationCooldownWaveStart: number; // Wave where cooldown starts decreasing
  formationCooldownWaveEnd: number;   // Wave where cooldown reaches minimum
  formationCooldown: number;          // Legacy fallback (ms)
  beeCooldownAfterDisperse: number;   // How long bees can't join another ball (ms)
  secondBallProbability: number;    // Chance for second ball when first is active
  secondBallRadiusMultiplier: number; // How much bigger the second ball is
  secondBallMinBeesExtra: number;   // Extra bees needed for second ball
  secondBallMinWave: number;         // Minimum wave for second ball to spawn
  secondBallHasKnockback: boolean;   // Whether second ball boundary has knockback
  // RUN 042: Ball promotion dynamics
  promotionConstrictSpeedMultiplier: number;  // How much faster promoted ball constricts
  promotionSkipGatheringPhase: boolean;       // Whether promoted ball skips gathering
}

export const BALL_PHASE_CONFIG: BallPhaseConfig = {
  // ==========================================================================
  // RUN 039: Gathering Phase - Pre-formation telegraph
  // ==========================================================================
  // Bees visibly travel to their formation positions before the ball "forms"
  // This gives players time to see it coming and react
  // NOTE: gatheringDuration is the BASE value - actual duration scales with wave
  // Use getGatheringDuration(wave) for the actual value
  gatheringDuration: 3500,   // Base: 3.5s at wave 3, scales down to 2s at wave 7+
  gatheringBeeSpeed: 45,     // 45 px/sec - slower than normal chase speed (80)

  // ==========================================================================
  // Main Phase Timing (from T1: Timing Constants)
  // ==========================================================================
  formingDuration: 4000,     // 4s (reduced from 6s since gathering adds 2.5s)
  silenceDuration: 2000,     // 2s - dramatic pause
  constrictDuration: 2500,   // 2.5s - escape window

  // Formation geometry
  initialRadius: 200,        // Starting sphere radius (px)
  finalRadius: 55,           // Cooking radius (tight around player)

  // Trigger conditions
  minBeesForBall: 6,         // Need 6+ bees to START formation
  minBeesToMaintain: 4,      // Ball dissolves if bees drop below this - reward aggressive play!
  minWaveForBall: 3,         // Can trigger from wave 3+

  // Multi-ball dynamics
  // RUN 039: Dynamic formation cooldown - starts high, decreases with wave
  formationCooldownMax: 10000,      // 10s at wave 1-2 (forgiving early game)
  formationCooldownMin: 0,          // 0s by wave 7+ (relentless late game)
  formationCooldownWaveStart: 3,    // Cooldown starts decreasing at wave 3
  formationCooldownWaveEnd: 7,      // Cooldown reaches minimum by wave 7
  // Legacy (for backwards compat - use getFormationCooldown() instead)
  formationCooldown: 2000,          // Fallback if wave not available
  beeCooldownAfterDisperse: 6000,   // 6s before dispersed bees can join new ball (was 4s)
  secondBallProbability: 0.60,      // 60% chance for second ball per check
  secondBallRadiusMultiplier: 1.6,  // Second ball is 60% larger (notably bigger)
  secondBallMinBeesExtra: -2,       // Second ball needs FEWER bees (6 - 2 = 4 bees)
  secondBallMinWave: 7,             // Second ball can only spawn from wave 7+
  secondBallHasKnockback: false,    // Second ball has NO knockback (visual warning only)
  // RUN 042: Ball promotion dynamics
  promotionConstrictSpeedMultiplier: 1.8,  // 80% faster constriction after promotion
  promotionSkipGatheringPhase: true,       // Promoted ball skips gathering, goes straight to forming
} as const;

// =============================================================================
// Gap Configuration
// =============================================================================

export interface BallGapConfig {
  initialGapDegrees: number;
  finalGapDegrees: number;
  rotationSpeedMin: number;
  rotationSpeedMax: number;
  directionChangeInterval: number;
  speedChangeInterval: number;
  directionChangeChance: number;
  speedChangeChance: number;
}

export const BALL_GAP_CONFIG: BallGapConfig = {
  // Gap size - RUN 039: 30% larger for more generous escape window
  initialGapDegrees: 65,     // Starting gap (was 50, now 30% larger)
  finalGapDegrees: 33,       // Final gap (was 25, now 30% larger)

  // Rotation speed (radians/second) - RUN 039: More dynamic range
  rotationSpeedMin: 0.2,     // Can slow down to a crawl (suspense!)
  rotationSpeedMax: 2.2,     // Can speed up dramatically

  // Random changes - RUN 039: More frequent and likely changes
  directionChangeInterval: 800,   // Check every 0.8s (was 1.5s)
  speedChangeInterval: 500,       // Check every 0.5s (was 0.8s)
  directionChangeChance: 0.5,     // 50% chance (was 30%) - more reversals
  speedChangeChance: 0.6,         // 60% chance (was 40%) - more speed variation
} as const;

// RUN 039: Near-miss punishment config
export const BALL_NEAR_MISS_CONFIG = {
  // How close to gap edge triggers near-miss (as % of gap size)
  nearMissThreshold: 0.05,       // 5% of gap size
  // Extra hard knockback toward center
  knockbackMultiplier: 3.0,      // 3x normal boundary knockback
  // Freeze frame duration
  freezeFrames: 8,               // ~133ms at 60fps
  // Circle inversion duration
  inversionDuration: 120,        // ms
} as const;

// =============================================================================
// Lunge Configuration (RUN 039: Enhanced Telegraph + Chain Lunges)
// =============================================================================
// Lunges now have punch-style visual telegraphs and can chain to other bees.
// Lunge distance is 120% of the distance to player (20% overshoot).

export interface BallLungeConfig {
  // RUN 040: Split windup into pullback + charge
  pullbackDuration: number;  // Bee moves backward at normal speed
  chargeDuration: number;    // Bee holds and accelerates
  attackDuration: number;    // Bee dashes toward player
  returnDuration: number;    // Bee returns to formation
  // Legacy (for backwards compat)
  windupDuration: number;    // Total windup = pullback + charge
  // Movement
  pullbackDistance: number;  // How far bee moves back during pullback
  pullbackSpeed: number;     // Speed during pullback (px/sec)
  overshootPercent: number;  // RUN 039: Lunge goes this % farther than player distance (0.2 = 20%)
  // Combat
  knockbackForce: number;
  damage: number;
  hitRadius: number;
  // Timing
  intervalMin: number;
  intervalMax: number;
  // RUN 039: Chain lunge mechanic
  chainLungeChance: number;  // Chance for lunge to trigger another bee (0.1 = 10%)
  chainLungeDelay: number;   // Delay before chain lunge starts (ms)
}

// =============================================================================
// RUN 042: Lunge Scaling by Enemy Tier
// =============================================================================
// Higher tier enemies have:
// - Larger hit radius (harder to dodge)
// - More damage
// - FASTER windup (more dangerous - less reaction time)
//
// This makes elite bees feel genuinely threatening while basic bees are manageable.

export interface LungeScalingConfig {
  hitRadiusMultiplier: number;    // Scales the base hit radius
  damageMultiplier: number;       // Scales the base damage
  windupSpeedMultiplier: number;  // > 1 = faster windup (MORE dangerous)
}

/**
 * Lunge scaling factors by bee type
 *
 * Philosophy:
 * - Workers (basic): Standard scaling, most forgiving
 * - Scouts (fast): Slightly larger radius, faster windup (agile attackers)
 * - Guards (tank): Large radius, high damage, but slow windup (telegraphed but powerful)
 * - Propolis (ranged): Moderate scaling (they prefer ranged combat)
 * - Royal (elite): Maximum threat - fast, damaging, hard to dodge
 */
export const LUNGE_SCALING_BY_TYPE: Record<string, LungeScalingConfig> = {
  // Workers - baseline, forgiving
  worker: {
    hitRadiusMultiplier: 1.0,
    damageMultiplier: 1.0,
    windupSpeedMultiplier: 1.0,
  },
  basic: {  // Legacy alias
    hitRadiusMultiplier: 1.0,
    damageMultiplier: 1.0,
    windupSpeedMultiplier: 1.0,
  },

  // Scouts - agile, quick strikes
  scout: {
    hitRadiusMultiplier: 1.15,      // 15% larger hit zone
    damageMultiplier: 0.8,          // Lower damage (hit-and-run style)
    windupSpeedMultiplier: 1.4,     // 40% faster windup! Quick strikes
  },
  fast: {  // Legacy alias
    hitRadiusMultiplier: 1.15,
    damageMultiplier: 0.8,
    windupSpeedMultiplier: 1.4,
  },

  // Guards - heavy hitters, well-telegraphed
  guard: {
    hitRadiusMultiplier: 1.5,       // 50% larger - hard to dodge position-wise
    damageMultiplier: 1.8,          // 80% more damage - punishing if hit
    windupSpeedMultiplier: 0.7,     // 30% SLOWER windup - highly telegraphed
  },
  tank: {  // Legacy alias
    hitRadiusMultiplier: 1.5,
    damageMultiplier: 1.8,
    windupSpeedMultiplier: 0.7,
  },

  // Propolis - ranged focus, moderate melee
  propolis: {
    hitRadiusMultiplier: 1.1,       // 10% larger
    damageMultiplier: 1.0,          // Standard damage
    windupSpeedMultiplier: 1.0,     // Standard speed (they prefer range)
  },
  spitter: {  // Legacy alias
    hitRadiusMultiplier: 1.1,
    damageMultiplier: 1.0,
    windupSpeedMultiplier: 1.0,
  },

  // Royal - elite threat, fast and dangerous
  royal: {
    hitRadiusMultiplier: 1.6,       // 60% larger - huge threat zone
    damageMultiplier: 2.0,          // Double damage!
    windupSpeedMultiplier: 1.3,     // 30% faster - quick for their size
  },
  boss: {  // Legacy alias
    hitRadiusMultiplier: 1.6,
    damageMultiplier: 2.0,
    windupSpeedMultiplier: 1.3,
  },

  // Colossal Tide - massive, devastating
  colossal_tide: {
    hitRadiusMultiplier: 2.0,       // Double hit radius!
    damageMultiplier: 2.5,          // 150% more damage
    windupSpeedMultiplier: 0.6,     // 40% SLOWER - very telegraphed but deadly
  },
};

/**
 * Get lunge scaling for an enemy type
 * Returns default (worker) scaling if type not found
 */
export function getLungeScaling(enemyType: string): LungeScalingConfig {
  return LUNGE_SCALING_BY_TYPE[enemyType] ?? LUNGE_SCALING_BY_TYPE.worker;
}

/**
 * Calculate scaled lunge parameters for a specific enemy
 */
export function getScaledLungeParams(enemyType: string): {
  hitRadius: number;
  damage: number;
  pullbackDuration: number;
  chargeDuration: number;
  windupDuration: number;
} {
  const scaling = getLungeScaling(enemyType);

  // Apply scaling to base values
  const hitRadius = BALL_LUNGE_CONFIG.hitRadius * scaling.hitRadiusMultiplier;
  const damage = Math.round(BALL_LUNGE_CONFIG.damage * scaling.damageMultiplier);

  // Windup speed multiplier > 1 = faster = shorter duration
  const pullbackDuration = Math.round(BALL_LUNGE_CONFIG.pullbackDuration / scaling.windupSpeedMultiplier);
  const chargeDuration = Math.round(BALL_LUNGE_CONFIG.chargeDuration / scaling.windupSpeedMultiplier);
  const windupDuration = pullbackDuration + chargeDuration;

  return {
    hitRadius,
    damage,
    pullbackDuration,
    chargeDuration,
    windupDuration,
  };
}

export const BALL_LUNGE_CONFIG: BallLungeConfig = {
  // ==========================================================================
  // RUN 040: Expanded Windup - Pullback + Charge phases
  // ==========================================================================

  // Timing - Split windup for more readable telegraph
  pullbackDuration: 500,     // 500ms - bee moves backward at normal speed
  chargeDuration: 350,       // 350ms - bee holds, accelerating/charging
  attackDuration: 400,       // 400ms - see the bee coming!
  returnDuration: 200,       // 200ms - quick return to formation

  // Legacy (total windup for backwards compat)
  windupDuration: 850,       // 500 + 350 = 850ms total windup

  // ==========================================================================
  // RUN 037 BALANCE CHANGES - Maintained
  // ==========================================================================

  // Knockback - REDUCED for fairness
  knockbackForce: 80,        // 80px (was 200px) - significant but fair

  // Damage
  damage: 5,

  // Movement
  pullbackDistance: 40,      // How far bee pulls back (px)
  pullbackSpeed: 80,         // Speed during pullback (px/sec) - normal bee speed
  overshootPercent: 0.2,     // RUN 039: Lunge goes 20% farther than player distance

  // Hit detection
  hitRadius: 45,             // Bee must be within 45px of player to hit
                             // (bee ~15px radius + player ~12px radius + 18px forgiveness)

  // Lunge frequency
  intervalMin: 500,          // Minimum time between lunges (ms)
  intervalMax: 1000,         // Maximum time between lunges (ms)

  // ==========================================================================
  // RUN 039: Chain Lunge Mechanic
  // ==========================================================================
  // When a lunge completes, there's a chance another bee will immediately lunge
  // This creates exciting "flurry" moments that test player reflexes

  chainLungeChance: 0.1,     // 10% chance to trigger chain lunge
  chainLungeDelay: 150,      // 150ms delay before chain lunge (slight stagger)
} as const;

// =============================================================================
// Boundary Configuration (BALANCE CHANGES APPLIED)
// =============================================================================

export interface BallBoundaryConfig {
  knockbackForce: number;
  damagePerTick: number;
  tickInterval: number;
  touchMargin: number;
}

export const BALL_BOUNDARY_CONFIG: BallBoundaryConfig = {
  // ==========================================================================
  // RUN 037 BALANCE CHANGES - Gentler boundary
  // ==========================================================================

  // Knockback - REDUCED (should be weakest)
  knockbackForce: 30,        // 30px (was 60px) - gentle push

  // Damage
  damagePerTick: 3,
  tickInterval: 200,         // How often boundary damage ticks (ms)

  // Detection
  touchMargin: 15,           // How close counts as "touching" (px)
} as const;

// =============================================================================
// Outside Punch Configuration (RUN 039: TELEGRAPH SYSTEM)
// =============================================================================
// Outside bees now telegraph their punches, giving player time to dodge.
// Flow: idle → windup (bee glows) → punch → recovery → idle
//
// Player can dodge by moving away during the 400ms windup window.
// If player exits hitRange before punch lands, attack whiffs.

export interface BallOutsidePunchConfig {
  knockbackForce: number;
  cooldown: number;
  detectionRange: number;    // When bee starts considering punching
  hitRange: number;          // Must be within this at punch time to connect
  windupDuration: number;    // Telegraph duration (dodgeable window)
  punchDuration: number;     // Actual attack duration (quick)
  recoveryDuration: number;  // Post-punch cooldown animation
  maxActivePunches: number;  // Max simultaneous punches (readability)
}

export const BALL_OUTSIDE_PUNCH_CONFIG: BallOutsidePunchConfig = {
  // ==========================================================================
  // RUN 039: Telegraph System - Readable & Dodgeable Punches
  // ==========================================================================

  // Knockback - Same as RUN 037
  knockbackForce: 50,        // 50px - moderate push toward ball center

  // Cooldown
  cooldown: 2500,            // 2.5s cooldown per bee (slightly longer for fairness)

  // Range - Split into detection and hit
  detectionRange: 60,        // Bee starts windup when player within 60px
  hitRange: 35,              // Player must be within 35px at punch time to get hit
                             // (This creates a ~25px "dodge window")

  // Timing - THE TELEGRAPH
  windupDuration: 400,       // 400ms windup - clear visual telegraph, dodgeable
  punchDuration: 100,        // 100ms punch - quick strike
  recoveryDuration: 200,     // 200ms recovery - bee resets

  // Readability
  maxActivePunches: 2,       // Max 2 punches at once (prevents visual chaos)
} as const;

// =============================================================================
// Movement Configuration
// =============================================================================

export interface BallMovementConfig {
  moveSpeed: number;
  recruitmentRadius: number;
  maxBeesInBall: number;
  targetUpdateRate: number;
}

export const BALL_MOVEMENT_CONFIG: BallMovementConfig = {
  moveSpeed: 40,             // Pixels per second - similar to bee chase speed
  recruitmentRadius: 150,    // Bees within this radius can be recruited
  maxBeesInBall: 20,         // Maximum bees in formation
  targetUpdateRate: 0.02,    // How fast ball tracks player (0 = never, 1 = instant)
} as const;

// =============================================================================
// Dissipation Configuration
// =============================================================================

export interface BallDissipationConfig {
  escapeGracePeriod: number;
  lingerDuration: number;      // NEW: How long ball lingers (can revive)
  dissipationDuration: number; // Final fade-out once linger expires
  fadeSpeed: number;           // How fast opacity drops per second
  reviveSpeed: number;         // How fast opacity recovers when player returns
}

export const BALL_DISSIPATION_CONFIG: BallDissipationConfig = {
  escapeGracePeriod: 1500,   // 1.5s outside before fade starts (reduced from 3s)
  lingerDuration: 3000,      // 3s linger period where ball can revive
  dissipationDuration: 800,  // Final fade-out animation (ms)
  fadeSpeed: 0.4,            // Lose 40% opacity per second during linger
  reviveSpeed: 0.8,          // Recover 80% opacity per second when returning
} as const;

// =============================================================================
// Cooking (Heat Damage) Configuration
// =============================================================================

export interface BallCookingConfig {
  damagePerTick: number;
  tickInterval: number;
}

export const BALL_COOKING_CONFIG: BallCookingConfig = {
  damagePerTick: 25,         // 25 damage per tick
  tickInterval: 400,         // Damage every 0.4s (faster = more urgency)
} as const;

// =============================================================================
// Audio Configuration
// =============================================================================

export interface BallAudioConfig {
  buzzVolumeStart: number;
  buzzVolumePeak: number;
  silenceDuration: number;
}

export const BALL_AUDIO_CONFIG: BallAudioConfig = {
  buzzVolumeStart: 0.3,
  buzzVolumePeak: 1.0,
  silenceDuration: 2000,     // ms of dread (matches silenceDuration)
} as const;

// =============================================================================
// Combined Config (Legacy Compatibility)
// =============================================================================

/**
 * Combined config object matching the legacy BALL_CONFIG shape
 * Used during migration for backwards compatibility
 */
export const BALL_CONFIG = {
  // Phase timing
  formingDuration: BALL_PHASE_CONFIG.formingDuration,
  silenceDuration: BALL_PHASE_CONFIG.silenceDuration,
  constrictDuration: BALL_PHASE_CONFIG.constrictDuration,

  // Gap
  initialGapDegrees: BALL_GAP_CONFIG.initialGapDegrees,
  finalGapDegrees: BALL_GAP_CONFIG.finalGapDegrees,

  // Formation geometry
  initialRadius: BALL_PHASE_CONFIG.initialRadius,
  finalRadius: BALL_PHASE_CONFIG.finalRadius,
  minBeesForBall: BALL_PHASE_CONFIG.minBeesForBall,

  // Cooking
  cookingDamagePerTick: BALL_COOKING_CONFIG.damagePerTick,
  cookingTickInterval: BALL_COOKING_CONFIG.tickInterval,

  // Audio
  audio: BALL_AUDIO_CONFIG,

  // Trigger conditions
  minWaveForBall: BALL_PHASE_CONFIG.minWaveForBall,

  // Ball movement
  ballMoveSpeed: BALL_MOVEMENT_CONFIG.moveSpeed,
  recruitmentRadius: BALL_MOVEMENT_CONFIG.recruitmentRadius,
  maxBeesInBall: BALL_MOVEMENT_CONFIG.maxBeesInBall,

  // Lunge attacks (RUN 039: Enhanced telegraph + chain lunges)
  lungeIntervalMin: BALL_LUNGE_CONFIG.intervalMin,
  lungeIntervalMax: BALL_LUNGE_CONFIG.intervalMax,
  lungeKnockbackForce: BALL_LUNGE_CONFIG.knockbackForce,       // 80px (was 200px)
  lungeDamage: BALL_LUNGE_CONFIG.damage,
  lungeWindupDuration: BALL_LUNGE_CONFIG.windupDuration,       // 850ms total windup
  lungeDuration: BALL_LUNGE_CONFIG.attackDuration,             // 400ms
  lungeOvershootPercent: BALL_LUNGE_CONFIG.overshootPercent,   // 0.2 = 20% farther
  lungeChainChance: BALL_LUNGE_CONFIG.chainLungeChance,        // 10% chain chance
  lungeChainDelay: BALL_LUNGE_CONFIG.chainLungeDelay,          // 150ms stagger

  // Boundary knockback (RUN 037 BALANCE)
  boundaryKnockbackForce: BALL_BOUNDARY_CONFIG.knockbackForce, // 30px (was 60px)
  boundaryDamagePerTick: BALL_BOUNDARY_CONFIG.damagePerTick,
  boundaryTickInterval: BALL_BOUNDARY_CONFIG.tickInterval,

  // Gap rotation
  gapRotationSpeedMin: BALL_GAP_CONFIG.rotationSpeedMin,
  gapRotationSpeedMax: BALL_GAP_CONFIG.rotationSpeedMax,
  gapDirectionChangeInterval: BALL_GAP_CONFIG.directionChangeInterval,
  gapSpeedChangeInterval: BALL_GAP_CONFIG.speedChangeInterval,

  // Dissipation
  escapeGracePeriod: BALL_DISSIPATION_CONFIG.escapeGracePeriod,
  dissipationDuration: BALL_DISSIPATION_CONFIG.dissipationDuration,

  // Outside punches (RUN 039: Telegraph system)
  outsidePunchCooldown: BALL_OUTSIDE_PUNCH_CONFIG.cooldown,
  outsidePunchDetectionRange: BALL_OUTSIDE_PUNCH_CONFIG.detectionRange,
  outsidePunchHitRange: BALL_OUTSIDE_PUNCH_CONFIG.hitRange,
  outsidePunchWindupDuration: BALL_OUTSIDE_PUNCH_CONFIG.windupDuration,
  outsidePunchKnockback: BALL_OUTSIDE_PUNCH_CONFIG.knockbackForce, // 50px
} as const;

// =============================================================================
// Wave-Scaled Duration Functions
// =============================================================================

/**
 * Get gathering phase duration based on wave number
 * - Wave 3: 3500ms (3.5s) - forgiving at start
 * - Wave 7+: 2000ms (2s) - challenging at higher waves
 * - Linear interpolation between
 */
export function getGatheringDuration(wave: number): number {
  const START_WAVE = 3;
  const END_WAVE = 7;
  const MAX_DURATION = 3500;  // 3.5s at wave 3
  const MIN_DURATION = 2000;  // 2s at wave 7+

  if (wave <= START_WAVE) return MAX_DURATION;
  if (wave >= END_WAVE) return MIN_DURATION;

  // Linear interpolation
  const progress = (wave - START_WAVE) / (END_WAVE - START_WAVE);
  return MAX_DURATION - (MAX_DURATION - MIN_DURATION) * progress;
}

// =============================================================================
// Knockback Hierarchy Summary
// =============================================================================
//
// RUN 037 Balance - From weakest to strongest:
//
// 1. Boundary touch:    30px  (gentle push back into ball)
// 2. Outside bee punch: 50px  (moderate, feels like a bump)
// 3. Lunge attack:      80px  (significant, but now dodgeable)
//
// Total lunge cycle: 600ms windup + 400ms travel + 200ms return = 1200ms
// This gives players clear windows to read and react.
// =============================================================================
