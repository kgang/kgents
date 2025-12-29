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
  formingDuration: number;
  silenceDuration: number;
  constrictDuration: number;
  initialRadius: number;
  finalRadius: number;
  minBeesForBall: number;
  minWaveForBall: number;
  // Multi-ball dynamics
  formationCooldown: number;        // Min time between ball formation attempts (ms)
  beeCooldownAfterDisperse: number; // How long bees can't join another ball (ms)
  secondBallProbability: number;    // Chance for second ball when first is active
  secondBallRadiusMultiplier: number; // How much bigger the second ball is
  secondBallMinBeesExtra: number;   // Extra bees needed for second ball
}

export const BALL_PHASE_CONFIG: BallPhaseConfig = {
  // Timing (from T1: Timing Constants)
  formingDuration: 6000,     // 6s - fast enough to see frequently
  silenceDuration: 2000,     // 2s - dramatic pause
  constrictDuration: 2500,   // 2.5s - escape window

  // Formation geometry
  initialRadius: 200,        // Starting sphere radius (px)
  finalRadius: 55,           // Cooking radius (tight around player)

  // Trigger conditions
  minBeesForBall: 6,         // Need 6+ bees
  minWaveForBall: 3,         // Can trigger from wave 3+

  // Multi-ball dynamics
  formationCooldown: 2000,          // 2s between ball formation attempts
  beeCooldownAfterDisperse: 4000,   // 4s before dispersed bees can join new ball
  secondBallProbability: 0.15,      // 15% chance for second ball per 2s
  secondBallRadiusMultiplier: 1.4,  // Second ball is 40% larger
  secondBallMinBeesExtra: 4,        // Need 4 more bees for second ball (10 total)
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
  // Gap size
  initialGapDegrees: 50,     // Starting gap (generous)
  finalGapDegrees: 25,       // Final gap (tight but fair)

  // Rotation speed (radians/second)
  rotationSpeedMin: 0.3,
  rotationSpeedMax: 1.2,

  // Random changes
  directionChangeInterval: 1500,  // How often direction CAN change (ms)
  speedChangeInterval: 800,       // How often speed CAN change (ms)
  directionChangeChance: 0.3,     // 30% chance when interval elapses
  speedChangeChance: 0.4,         // 40% chance when interval elapses
} as const;

// =============================================================================
// Lunge Configuration (BALANCE CHANGES APPLIED)
// =============================================================================

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
  overshoot: number;         // How far past player the bee lunges
  // Combat
  knockbackForce: number;
  damage: number;
  hitRadius: number;
  // Timing
  intervalMin: number;
  intervalMax: number;
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
  overshoot: 25,             // How far past player the bee lunges (px)

  // Hit detection
  hitRadius: 45,             // Bee must be within 45px of player to hit
                             // (bee ~15px radius + player ~12px radius + 18px forgiveness)

  // Lunge frequency
  intervalMin: 500,          // Minimum time between lunges (ms)
  intervalMax: 1000,         // Maximum time between lunges (ms)
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
// Outside Punch Configuration (BALANCE CHANGES APPLIED)
// =============================================================================

export interface BallOutsidePunchConfig {
  knockbackForce: number;
  cooldown: number;
  range: number;
}

export const BALL_OUTSIDE_PUNCH_CONFIG: BallOutsidePunchConfig = {
  // ==========================================================================
  // RUN 037 BALANCE CHANGES - Between boundary and lunge
  // ==========================================================================

  // Knockback - REDUCED
  knockbackForce: 50,        // 50px (was 80px) - moderate

  // Timing
  cooldown: 2000,            // Cooldown per bee (ms)
  range: 40,                 // Range at which outside bees can punch (px)
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

  // Lunge attacks (RUN 037 BALANCE)
  lungeIntervalMin: BALL_LUNGE_CONFIG.intervalMin,
  lungeIntervalMax: BALL_LUNGE_CONFIG.intervalMax,
  lungeKnockbackForce: BALL_LUNGE_CONFIG.knockbackForce,       // 80px (was 200px)
  lungeDamage: BALL_LUNGE_CONFIG.damage,
  lungeWindupDuration: BALL_LUNGE_CONFIG.windupDuration,       // 600ms (was 350ms)
  lungeDuration: BALL_LUNGE_CONFIG.attackDuration,             // 400ms (was 150ms)
  lungeOvershoot: BALL_LUNGE_CONFIG.overshoot,

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

  // Outside punches (RUN 037 BALANCE)
  outsidePunchCooldown: BALL_OUTSIDE_PUNCH_CONFIG.cooldown,
  outsidePunchRange: BALL_OUTSIDE_PUNCH_CONFIG.range,
  outsidePunchKnockback: BALL_OUTSIDE_PUNCH_CONFIG.knockbackForce, // 50px (was 80px)
} as const;

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
