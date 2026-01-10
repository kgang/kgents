/**
 * WASM Survivors - Apex Strike Dash System
 *
 * The hornet's signature predator dash: LOCK -> STRIKE -> HIT/MISS
 *
 * DESIGN PHILOSOPHY:
 * > "The hornet doesn't dash - it HUNTS. The strike is commitment."
 *
 * The Apex Strike replaces generic dashing with a precision predator lunge
 * that rewards positioning, timing, and chaining kills. Miss and you're
 * vulnerable. Hit and you become unstoppable.
 *
 * KEY FEATURES:
 * - LOCK (0.12s): Aim with WASD, vulnerable
 * - STRIKE (0.15s): Explosive 12x speed thrust, unstoppable
 * - HIT: Grip moment (0.05s), chain window (0.2s), build bloodlust
 * - MISS: Recovery (0.25s), vulnerable, full cooldown
 *
 * BLOODLUST SYSTEM:
 * - Gain +20 per hit (max 100)
 * - At max: 2x strike damage
 * - Decays 15/second when not striking
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import type { Vector2, Enemy } from '../types';

// =============================================================================
// Types
// =============================================================================

/**
 * Apex Strike phase states
 * - ready: Can initiate strike
 * - lock: Aiming, vulnerable
 * - strike: Moving at high speed, unstoppable
 * - hit: Brief grip after impact, chain window open
 * - miss_recovery: Vulnerable after missing
 */
export type ApexPhase = 'ready' | 'lock' | 'strike' | 'hit' | 'miss_recovery';

/**
 * Miss penalty phases (DD-038-5)
 * - stumble: 0.3s, 50% move speed, can't attack
 * - vulnerable: 0.4s, take 1.5x damage
 * - recovery: 0.8s, normal but on cooldown
 */
export type MissPenaltyPhase = 'stumble' | 'vulnerable' | 'recovery';

/**
 * Complete Apex Strike state
 */
export interface ApexStrikeState {
  /** Current phase of the strike */
  phase: ApexPhase;

  /** Direction locked during LOCK phase (normalized) */
  lockDirection: Vector2 | null;

  /** Time spent in lock phase (ms) */
  lockTimer: number;

  /** Position when strike was launched */
  strikeStartPos: Vector2 | null;

  /** Current strike target position */
  strikeEndPos: Vector2 | null;

  /** Distance remaining in strike (pixels) */
  strikeDistanceRemaining: number;

  /** Chain window countdown after hit (ms) */
  chainWindow: number;

  /** Whether a chain is available */
  canChain: boolean;

  /** Bloodlust meter (0-100) */
  bloodlust: number;

  /** Cooldown remaining (ms) */
  cooldownRemaining: number;

  /** ID of the last enemy hit (for chaining) */
  lastHitEnemyId: string | null;

  /** Time spent in current phase (for animations) */
  phaseTimer: number;

  /** Total strike damage dealt this chain */
  chainDamageDealt: number;

  /** Number of hits in current chain */
  chainHits: number;

  // --- Charge System Fields (DD-038-2) ---

  /** Charge level (0-1), affects distance and damage */
  chargeLevel: number;

  /** Time held in charge (ms) */
  chargeTime: number;

  /** Aim mode: 'cursor' | 'wasd' (DD-038-1) */
  aimMode: 'cursor' | 'wasd';

  /** Cursor position at charge start (for cursor aim) */
  chargeStartCursor: Vector2 | null;

  // --- Miss Penalty Fields (DD-038-5) ---

  /** Miss penalty phase: 'stumble' | 'vulnerable' | 'recovery' | null */
  missPenaltyPhase: MissPenaltyPhase | null;

  /** Miss penalty timer (ms remaining) */
  missPenaltyTimer: number;

  // --- Stumble Momentum (instant kinesthetic feedback on miss) ---

  /** Direction of stumble (locked at miss) */
  stumbleDirection: Vector2 | null;

  /** Remaining stumble distance to travel (px) */
  stumbleMomentum: number;

  /** Wave phase for chaotic motion (radians) */
  stumbleWavePhase: number;

  /** Original stumble distance for decay calculation */
  stumbleStartMomentum: number;

  // --- Hit Boost (burst through enemies on hit) ---

  /** Direction of hit boost (same as strike direction) */
  hitBoostDirection: Vector2 | null;

  /** Remaining hit boost momentum (decays quickly) */
  hitBoostMomentum: number;

  /** Original hit boost momentum for decay calculation */
  hitBoostStartMomentum: number;

  /** Timer for hit boost decay (ms) */
  hitBoostTimer: number;

  // --- Rocket Boost Dash State ---

  /** Current dash speed (decays over time) */
  dashCurrentSpeed: number;

  /** Current steering control (0 = locked direction, 1 = full control) */
  dashSteerControl: number;

  /** Current blended direction (starts as lock, blends with input) */
  dashCurrentDirection: Vector2 | null;

  /** Total boost duration for this dash (based on charge time) */
  boostDuration: number;

  // --- Run 038: Multi-Hit Stop System ---

  /** Remaining hit stop frames (game pauses briefly on multi-hit) */
  hitStopFrames: number;

  /** Number of enemies hit in current multi-hit (for visual effect) */
  multiHitCount: number;

  /** Position where multi-hit occurred (for visual effect) */
  multiHitPosition: Vector2 | null;

  // --- Run 038: Combo Batching System ---

  /** Total kills accumulated during this apex strike */
  comboKills: number;

  /** When the combo display should appear (performance.now timestamp) */
  comboDisplayTime: number;

  /** When the combo window ends (performance.now timestamp, 200ms after dash ends) */
  comboWindowEnd: number;

  /** Whether the combo has been displayed yet */
  comboDisplayed: boolean;

  // --- Ghost Trail (visual afterimages during dash) ---

  /** Active ghost afterimages for trail effect */
  ghostTrail: GhostAfterimage[];

  /** Time since last ghost was spawned (ms) */
  lastGhostSpawnTime: number;
}

/**
 * Configuration for Apex Strike
 */
export interface ApexStrikeConfig {
  /** Duration of lock phase (ms) */
  lockDuration: number;

  /** Minimum speed multiplier at 0% charge (relative to base 200 px/s) */
  minStrikeSpeedMult: number;

  /** Maximum speed multiplier at 100% charge (relative to base 200 px/s) */
  maxStrikeSpeedMult: number;

  /** Speed multiplier during strike (legacy, not used) */
  strikeSpeed: number;

  /** Maximum duration of strike phase (ms) */
  strikeDuration: number;

  /** Maximum strike distance (pixels) */
  strikeDistance: number;

  /** Base damage on hit */
  strikeDamage: number;

  /** Chain window duration after hit (ms) */
  chainWindow: number;

  /** Grip moment duration after hit (ms) */
  gripDuration: number;

  /** Recovery duration after miss (ms) */
  missRecovery: number;

  /** Base cooldown after miss (ms) */
  baseCooldown: number;

  /** Bloodlust gain per hit */
  bloodlustGain: number;

  /** Maximum bloodlust value */
  bloodlustMax: number;

  /** Bloodlust decay per second */
  bloodlustDecay: number;

  /** Damage bonus at max bloodlust (multiplier) */
  bloodlustDamageBonus: number;

  /** Player hitbox radius for collision detection */
  playerRadius: number;

  /** Hitbox multiplier during apex strike (slightly larger than visual) */
  strikeHitboxMultiplier: number;

  // --- Charge Scaling (DD-038-2) ---

  /** Minimum charge duration for scaling (ms) */
  minChargeDuration: number;

  /** Maximum charge duration for scaling (ms) - adjusted from 800ms to 500ms */
  maxChargeDuration: number;

  /** Minimum strike distance at 0% charge (pixels) */
  minDistance: number;

  /** Maximum strike distance at 100% charge (pixels) */
  maxDistance: number;

  /** Minimum damage multiplier at 0% charge */
  minDamageMultiplier: number;

  /** Maximum damage multiplier at 100% charge */
  maxDamageMultiplier: number;

  // --- Miss Penalty Phases (DD-038-5) ---

  /** Stumble phase duration (ms) */
  stumbleDuration: number;

  /** Speed multiplier during stumble (0.5 = 50% speed) */
  stumbleSpeedMult: number;

  /** Vulnerable phase duration (ms) */
  vulnerableDuration: number;

  /** Damage multiplier during vulnerable phase */
  vulnerableDamageMult: number;

  /** Recovery phase duration (ms) */
  recoveryDuration: number;

  // --- Stumble Momentum (instant feedback on miss) ---

  /** Stumble distance as percentage of dash distance (0.25 = 25%) */
  stumbleMomentumPercent: number;

  /** Wave frequency for chaotic motion (Hz) */
  stumbleWaveFrequency: number;

  /** Wave amplitude for perpendicular oscillation (radians) */
  stumbleWaveAmplitude: number;

  /** Exponential decay rate per second */
  stumbleDecayRate: number;

  /** Player steering influence during stumble (0-1) - base value */
  stumblePlayerControl: number;

  /** Maximum player control at end of stumble (0-1). Control scales inversely with momentum. */
  stumbleMaxPlayerControl: number;

  /** Initial velocity impulse multiplier (e.g., 2.5 = 2.5x base speed at start) */
  stumbleImpulseMultiplier: number;

  // --- Hit Boost (burst through on hit) ---

  /** Hit boost initial speed (px/s) - burst speed on hit */
  hitBoostSpeed: number;

  /** Hit boost duration (ms) - how long the boost lasts */
  hitBoostDuration: number;

  /** Hit boost decay rate - exponential decay per second */
  hitBoostDecayRate: number;

  /** Enemy knockback force (px) - how far enemy is pushed */
  enemyKnockbackForce: number;

  // --- Rocket Boost Dash (progressive control) ---

  /** Total dash duration including glide (ms) */
  dashTotalDuration: number;

  /** Duration of initial burst phase with no steering (ms) */
  dashBurstDuration: number;

  /** How fast steering control is gained during glide (0-1 per second) */
  dashSteerGainRate: number;

  /** Speed decay rate during glide (exponential decay per second) */
  dashSpeedDecayRate: number;

  /** Minimum speed during glide before returning to normal (px/s) */
  dashMinSpeed: number;

  /** Normal player speed to ease into (px/s) */
  normalSpeed: number;

  /** Minimum boost duration for quick taps (ms) */
  minBoostDuration: number;

  // --- Run 038: Multi-Hit Stop (freeze frames) ---

  /** Hit stop duration (ms) for 2 enemies (small) */
  hitStopMsSmall: number;

  /** Hit stop duration (ms) for 3 enemies (medium) */
  hitStopMsMedium: number;

  /** Hit stop duration (ms) for 4+ enemies (heavy) */
  hitStopMsHeavy: number;

  /** Time window after dash to batch kills into combo (ms) */
  comboBatchWindow: number;
}

/**
 * Events emitted by the Apex Strike system
 */
export type ApexEvent =
  | { type: 'lock_started'; position: Vector2; timestamp: number }
  | { type: 'lock_direction_updated'; direction: Vector2 }
  | { type: 'strike_launched'; direction: Vector2; bloodlust: number; timestamp: number }
  | { type: 'strike_hit'; enemyId: string; damage: number; chainAvailable: boolean; position: Vector2; timestamp: number }
  | { type: 'strike_miss'; position: Vector2; timestamp: number }
  | { type: 'chain_started'; fromEnemyId: string; direction: Vector2; timestamp: number }
  | { type: 'chain_ended'; totalHits: number; totalDamage: number; timestamp: number }
  | { type: 'bloodlust_max'; position: Vector2; timestamp: number }
  | { type: 'bloodlust_depleted'; timestamp: number }
  | { type: 'cooldown_started'; duration: number; timestamp: number }
  | { type: 'cooldown_ended'; timestamp: number }
  | { type: 'grip_moment'; enemyId: string; position: Vector2; timestamp: number }
  // Run 038: Multi-hit event
  | { type: 'multi_hit'; hitCount: number; position: Vector2; hitStopFrames: number; timestamp: number };

/**
 * Result of checking for strike hit
 */
export interface StrikeHitResult {
  /** Updated state */
  state: ApexStrikeState;
  /** Enemy that was hit, if any (first/primary hit) */
  hitEnemy: Enemy | null;
  /** All enemies hit (Run 038: multi-hit support) */
  hitEnemies: Enemy[];
  /** Damage dealt (per enemy) */
  damage: number;
  /** Events generated */
  events: ApexEvent[];
}

/**
 * Result of updating apex strike
 */
export interface ApexUpdateResult {
  /** Updated state */
  state: ApexStrikeState;
  /** Events generated */
  events: ApexEvent[];
  /** Velocity to apply to player (null if not in strike) */
  velocity: Vector2 | null;
}

/**
 * Minimal enemy data needed for hit detection
 */
export interface ApexTarget {
  id: string;
  position: Vector2;
  radius: number;
  health: number;
}

/**
 * Ghost trail afterimage for apex strike dash
 * Each ghost captures player position at a moment in time
 */
export interface GhostAfterimage {
  /** Position where ghost was spawned */
  position: Vector2;
  /** Direction player was facing (for rotation) */
  direction: Vector2;
  /** Timestamp when ghost was created (game time) */
  spawnTime: number;
  /** Opacity when spawned (1.0 = full) */
  initialOpacity: number;
}

/**
 * Configuration for ghost trail effect
 */
export interface GhostTrailConfig {
  /** Time between spawning ghost afterimages (ms) */
  spawnInterval: number;
  /** How long each ghost persists before fully fading (ms) */
  fadeDuration: number;
  /** Maximum number of ghosts in trail */
  maxGhosts: number;
  /** Initial opacity for new ghosts (0-1) */
  initialOpacity: number;
  /** Whether to spawn ghosts only during strike phase */
  strikePhaseOnly: boolean;
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Default Apex Strike configuration
 * Tuned for "commitment with reward" feel
 */
export const APEX_CONFIG: ApexStrikeConfig = {
  // Lock phase - brief aim window
  lockDuration: 120,            // 0.12s - quick but readable

  // Strike phase - explosive thrust (speed scales with charge)
  minStrikeSpeedMult: 3.0,      // 3x normal at 0% charge = 600 px/s
  maxStrikeSpeedMult: 5.5,      // 5.5x normal at 100% charge = 1100 px/s
  strikeSpeed: 18,              // Legacy, not used (kept for compatibility)
  strikeDuration: 150,          // Legacy, not used
  strikeDistance: 360,          // Legacy, not used

  // Damage
  strikeDamage: 25,             // Hefty base damage

  // Hit response
  chainWindow: 200,             // 0.2s to chain
  gripDuration: 50,             // 0.05s grip moment

  // Miss penalty
  missRecovery: 250,            // 0.25s vulnerability
  baseCooldown: 1500,           // 1.5s cooldown on miss

  // Bloodlust system
  bloodlustGain: 20,            // +20 per hit
  bloodlustMax: 100,            // Cap
  bloodlustDecay: 15,           // Decay per second
  bloodlustDamageBonus: 2,      // 2x damage at max

  // Collision
  playerRadius: 15,
  strikeHitboxMultiplier: 1.08,  // 8% larger hitbox during strike (feels generous)

  // --- Charge Scaling (DD-038-2) ---
  minChargeDuration: 200,       // 0.2s minimum charge
  maxChargeDuration: 500,       // 0.5s maximum charge
  minDistance: 70,              // Short hop at minimum charge (halved for more control)
  maxDistance: 220,             // Full distance at max charge (halved for more control)
  minDamageMultiplier: 1.0,     // 1x damage at minimum charge
  maxDamageMultiplier: 2.0,     // 2x damage at max charge

  // --- Miss Penalty Phases (DD-038-5) ---
  stumbleDuration: 300,         // 0.3s stumble
  stumbleSpeedMult: 0.5,        // 50% move speed during stumble
  vulnerableDuration: 400,      // 0.4s vulnerable
  vulnerableDamageMult: 1.5,    // 1.5x damage taken during vulnerable
  recoveryDuration: 800,        // 0.8s recovery (on cooldown)

  // --- Stumble Momentum (instant kinesthetic feedback on miss) ---
  stumbleMomentumPercent: 0.25,  // 25% of dash distance
  stumbleWaveFrequency: 2,       // Slower wobble for readable feedback (Hz)
  stumbleWaveAmplitude: 0.4,     // ~23 degrees perpendicular wave
  stumbleDecayRate: 4.0,         // Rapid exponential decay (e^-4/s)
  stumblePlayerControl: 0.3,     // Base value (not used directly anymore)
  stumbleMaxPlayerControl: 0.9,  // 90% control at end of stumble (inverse scaling)
  stumbleImpulseMultiplier: 2.5, // Sharp 2.5x velocity kick at start

  // --- Hit Boost (burst through on hit) ---
  hitBoostSpeed: 800,            // 4x base speed burst on hit
  hitBoostDuration: 120,         // 0.12s quick burst
  hitBoostDecayRate: 8.0,        // Very fast decay (e^-8/s)
  enemyKnockbackForce: 80,       // Push enemy 80px in collision normal direction

  // --- Run 038: Impact Stop (freeze on satisfying hits) ---
  hitStopMsSmall: 175,           // 175ms freeze for 2 enemies (small)
  hitStopMsMedium: 225,          // 225ms freeze for 3 enemies (medium)
  hitStopMsHeavy: 285,           // 285ms freeze for 4+ enemies (heavy)

  // --- Run 038: Combo Batching ---
  comboBatchWindow: 200,         // 200ms after dash ends to batch kills into combo

  // --- Rocket Boost Dash (progressive control) ---
  dashTotalDuration: 600,        // Legacy max (now uses charge time)
  dashBurstDuration: 80,         // 0.08s initial burst (shorter commitment)
  dashSteerGainRate: 5.0,        // Gain full steering faster after burst
  dashSpeedDecayRate: 2.0,       // Slower speed decay (momentum lasts longer)
  dashMinSpeed: 250,             // Below this, return to normal movement
  normalSpeed: 200,              // Base player speed to ease into
  minBoostDuration: 150,         // Minimum boost duration for quick taps (ms)
};

/**
 * Ghost trail configuration for apex strike dash
 * Creates quickly fading afterimages during the strike phase
 */
export const GHOST_TRAIL_CONFIG: GhostTrailConfig = {
  spawnInterval: 25,        // Spawn ghost every 25ms (~40 ghosts/sec during dash)
  fadeDuration: 650,        // Each ghost fades over 650ms (smooth, lingering trail)
  maxGhosts: 24,            // Keep max 24 ghosts (650ms / 25ms ≈ 26)
  initialOpacity: 0.6,      // Start at 60% opacity
  strikePhaseOnly: true,    // Only during active strike
};

/**
 * Base player speed for velocity calculation (px/s)
 */
const BASE_PLAYER_SPEED = 200;

// =============================================================================
// State Factory
// =============================================================================

/**
 * Create initial Apex Strike state (ready to strike)
 */
export function createInitialApexState(): ApexStrikeState {
  return {
    phase: 'ready',
    lockDirection: null,
    lockTimer: 0,
    strikeStartPos: null,
    strikeEndPos: null,
    strikeDistanceRemaining: 0,
    chainWindow: 0,
    canChain: false,
    bloodlust: 0,
    cooldownRemaining: 0,
    lastHitEnemyId: null,
    phaseTimer: 0,
    chainDamageDealt: 0,
    chainHits: 0,
    // Charge system defaults
    chargeLevel: 0,
    chargeTime: 0,
    aimMode: 'cursor',
    chargeStartCursor: null,
    // Miss penalty defaults
    missPenaltyPhase: null,
    missPenaltyTimer: 0,
    // Stumble momentum defaults
    stumbleDirection: null,
    stumbleMomentum: 0,
    stumbleWavePhase: 0,
    stumbleStartMomentum: 0,
    // Hit boost defaults
    hitBoostDirection: null,
    hitBoostMomentum: 0,
    hitBoostStartMomentum: 0,
    hitBoostTimer: 0,
    // Rocket boost dash defaults
    dashCurrentSpeed: 0,
    dashSteerControl: 0,
    dashCurrentDirection: null,
    boostDuration: 0,
    // Run 038: Multi-hit stop defaults
    hitStopFrames: 0,
    multiHitCount: 0,
    multiHitPosition: null,
    // Run 038: Combo batching defaults
    comboKills: 0,
    comboDisplayTime: 0,
    comboWindowEnd: 0,
    comboDisplayed: false,
    // Ghost trail defaults
    ghostTrail: [],
    lastGhostSpawnTime: 0,
  };
}

// =============================================================================
// Phase Transitions
// =============================================================================

/**
 * Check if apex strike can be initiated
 * @param state Current apex state
 * @returns Whether strike can be initiated
 */
export function canApex(state: ApexStrikeState): boolean {
  // Can strike if ready and off cooldown
  return state.phase === 'ready' && state.cooldownRemaining <= 0;
}

/**
 * Check if in chain window and can chain
 * @param state Current apex state
 * @returns Whether chain is available
 */
export function canChain(state: ApexStrikeState): boolean {
  return state.phase === 'hit' && state.canChain && state.chainWindow > 0;
}

/**
 * Initiate LOCK phase - player starts aiming
 * @param state Current apex state
 * @param aimDirection Initial aim direction
 * @param playerPos Current player position
 * @param timestamp Current game time
 * @param cursorPos Optional cursor position for hybrid aim mode (DD-038-1)
 * @returns Updated state and events
 */
export function initiateLock(
  state: ApexStrikeState,
  aimDirection: Vector2,
  playerPos: Vector2,
  timestamp: number,
  cursorPos?: Vector2
): { state: ApexStrikeState; events: ApexEvent[] } {
  if (!canApex(state)) {
    return { state, events: [] };
  }

  const normalizedDir = normalizeVector(aimDirection);

  const newState: ApexStrikeState = {
    ...state,
    phase: 'lock',
    lockDirection: normalizedDir,
    lockTimer: 0,
    phaseTimer: 0,
    strikeStartPos: { ...playerPos },
    // Reset chain stats on new lock
    chainDamageDealt: 0,
    chainHits: 0,
    // Initialize charge system (DD-038-2)
    chargeLevel: 0,
    chargeTime: 0,
    aimMode: 'cursor',
    chargeStartCursor: cursorPos ? { ...cursorPos } : null,
  };

  const events: ApexEvent[] = [
    { type: 'lock_started', position: playerPos, timestamp },
  ];

  return { state: newState, events };
}

/**
 * Update aim direction during LOCK phase
 * @param state Current apex state
 * @param aimDirection New aim direction
 * @returns Updated state and events
 */
export function updateLockDirection(
  state: ApexStrikeState,
  aimDirection: Vector2
): { state: ApexStrikeState; events: ApexEvent[] } {
  if (state.phase !== 'lock') {
    return { state, events: [] };
  }

  const normalizedDir = normalizeVector(aimDirection);

  // Only emit event if direction actually changed significantly
  const dirChanged = !state.lockDirection ||
    Math.abs(normalizedDir.x - state.lockDirection.x) > 0.1 ||
    Math.abs(normalizedDir.y - state.lockDirection.y) > 0.1;

  const events: ApexEvent[] = dirChanged
    ? [{ type: 'lock_direction_updated', direction: normalizedDir }]
    : [];

  return {
    state: {
      ...state,
      lockDirection: normalizedDir,
    },
    events,
  };
}

/**
 * Execute the strike - launch from LOCK to STRIKE phase
 * Now uses charge-scaled distance based on charge level (DD-038-2)
 *
 * @param state Current apex state
 * @param playerPos Current player position
 * @param aimDirection Final aim direction (uses lock direction if null)
 * @param timestamp Current game time
 * @param config Configuration
 * @returns Updated state and events
 */
export function executeStrike(
  state: ApexStrikeState,
  playerPos: Vector2,
  aimDirection: Vector2 | null,
  timestamp: number,
  config: ApexStrikeConfig = APEX_CONFIG
): { state: ApexStrikeState; events: ApexEvent[] } {
  if (state.phase !== 'lock') {
    return { state, events: [] };
  }

  const direction = normalizeVector(aimDirection || state.lockDirection || { x: 1, y: 0 });

  // Calculate charge-scaled distance (DD-038-2)
  // Distance: 60px (0% charge) → 360px (100% charge)
  const chargeScaledDistance = config.minDistance +
    (config.maxDistance - config.minDistance) * state.chargeLevel;

  // Calculate end position based on charge-scaled distance
  const endPos: Vector2 = {
    x: playerPos.x + direction.x * chargeScaledDistance,
    y: playerPos.y + direction.y * chargeScaledDistance,
  };

  // Calculate initial dash speed based on charge level
  // Speed scales from 3x (0% charge) to 5.5x (100% charge)
  const speedMultiplier = config.minStrikeSpeedMult +
    (config.maxStrikeSpeedMult - config.minStrikeSpeedMult) * state.chargeLevel;
  const initialDashSpeed = BASE_PLAYER_SPEED * speedMultiplier;

  // Calculate boost duration based on charge time
  // Duration = charge time, with a minimum for quick taps
  const boostDuration = Math.max(config.minBoostDuration, state.chargeTime);

  // DEBUG: Log charge scaling values
  console.log('[APEX STRIKE] Charge:', {
    chargeLevel: state.chargeLevel.toFixed(2),
    chargeTime: state.chargeTime.toFixed(0) + 'ms',
    boostDuration: boostDuration.toFixed(0) + 'ms',
    distance: chargeScaledDistance.toFixed(0) + 'px',
    speed: initialDashSpeed.toFixed(0) + 'px/s',
    speedMult: speedMultiplier.toFixed(1) + 'x',
  });

  // Run 038: Calculate combo timing based on boost duration
  const now = performance.now();
  const comboDisplayTime = now + Math.min(config.dashBurstDuration, boostDuration * 0.5);
  const comboWindowEnd = now + boostDuration + config.comboBatchWindow;

  console.log(`[APEX STRIKE] Combo timing: displayAt=${(comboDisplayTime - now).toFixed(0)}ms, windowEnd=${(comboWindowEnd - now).toFixed(0)}ms, boostDuration=${boostDuration.toFixed(0)}ms`);

  const newState: ApexStrikeState = {
    ...state,
    phase: 'strike',
    lockDirection: direction,
    strikeStartPos: { ...playerPos },
    strikeEndPos: endPos,
    strikeDistanceRemaining: chargeScaledDistance,
    phaseTimer: 0,
    // Initialize rocket boost dash state
    dashCurrentSpeed: initialDashSpeed,
    dashSteerControl: 0,  // No steering at start
    dashCurrentDirection: { ...direction },
    boostDuration,  // Store for time-based completion check
    // Run 038: Combo batching - reset and set timers
    comboKills: 0,
    comboDisplayTime,
    comboWindowEnd,
    comboDisplayed: false,
  };

  const events: ApexEvent[] = [
    {
      type: 'strike_launched',
      direction,
      bloodlust: state.bloodlust,
      timestamp,
    },
  ];

  return { state: newState, events };
}

/**
 * Handle successful hit - transition to HIT phase
 * Now uses charge-scaled damage multiplier (DD-038-2)
 *
 * @param state Current apex state
 * @param enemy Enemy that was hit
 * @param playerPos Position where hit occurred
 * @param timestamp Current game time
 * @param config Configuration
 * @returns Updated state and events
 */
export function onStrikeHit(
  state: ApexStrikeState,
  enemy: ApexTarget,
  playerPos: Vector2,
  timestamp: number,
  config: ApexStrikeConfig = APEX_CONFIG
): { state: ApexStrikeState; events: ApexEvent[]; damage: number } {
  if (state.phase !== 'strike') {
    return { state, events: [], damage: 0 };
  }

  // ==========================================================================
  // APEX STRIKE BASE DAMAGE CALCULATION (Run 050: Documented)
  // ==========================================================================
  //
  // This calculates the BASE damage before ability bonuses are applied.
  // Ability bonuses (trophy_scent, territorial_mark, corpse_heat, sawtooth,
  // melittin_traces, histamine_burst, chitin_crack) are applied in useGameLoop.ts
  // using the calculateApexStrikeDamage() function.
  //
  // Formula: base_damage * bloodlust_multiplier * charge_multiplier
  // - Base: 25 (config.strikeDamage)
  // - Bloodlust: 1.0x (0) to 2.0x (100)
  // - Charge: 1.0x (0%) to 2.0x (100%)
  // ==========================================================================

  // Calculate charge-scaled damage multiplier (DD-038-2)
  // Damage: 1.0x (0% charge) → 2.0x (100% charge)
  const chargeDamageMultiplier = config.minDamageMultiplier +
    (config.maxDamageMultiplier - config.minDamageMultiplier) * state.chargeLevel;

  // Calculate damage with bloodlust bonus AND charge scaling
  const bloodlustMultiplier = 1 + (state.bloodlust / config.bloodlustMax) * (config.bloodlustDamageBonus - 1);
  const damage = Math.floor(config.strikeDamage * bloodlustMultiplier * chargeDamageMultiplier);

  // Debug logging for apex strike base damage
  console.log('[APEX STRIKE BASE DAMAGE]', {
    base: config.strikeDamage,
    bloodlust: `${state.bloodlust}/${config.bloodlustMax} → ${bloodlustMultiplier.toFixed(2)}x`,
    charge: `${(state.chargeLevel * 100).toFixed(0)}% → ${chargeDamageMultiplier.toFixed(2)}x`,
    result: damage,
    note: 'Ability bonuses applied in useGameLoop.ts',
  });

  // Add bloodlust
  const newBloodlust = Math.min(state.bloodlust + config.bloodlustGain, config.bloodlustMax);
  const hitMaxBloodlust = newBloodlust >= config.bloodlustMax && state.bloodlust < config.bloodlustMax;

  // Hit boost: burst through in strike direction
  const hitBoostDir = state.lockDirection || { x: 1, y: 0 };

  const newState: ApexStrikeState = {
    ...state,
    phase: 'hit',
    chainWindow: config.chainWindow,
    canChain: true,
    bloodlust: newBloodlust,
    lastHitEnemyId: enemy.id,
    phaseTimer: 0,
    chainDamageDealt: state.chainDamageDealt + damage,
    chainHits: state.chainHits + 1,
    // Stop at enemy position
    strikeDistanceRemaining: 0,
    // Hit boost: burst through with quick decay
    hitBoostDirection: hitBoostDir,
    hitBoostMomentum: config.hitBoostSpeed,
    hitBoostStartMomentum: config.hitBoostSpeed,
    hitBoostTimer: config.hitBoostDuration,
    // Clear ghost trail when strike ends
    ghostTrail: [],
  };

  const events: ApexEvent[] = [
    { type: 'grip_moment', enemyId: enemy.id, position: playerPos, timestamp },
    {
      type: 'strike_hit',
      enemyId: enemy.id,
      damage,
      chainAvailable: true,
      position: playerPos,
      timestamp,
    },
  ];

  if (hitMaxBloodlust) {
    events.push({ type: 'bloodlust_max', position: playerPos, timestamp });
  }

  return { state: newState, events, damage };
}

/**
 * Handle miss - stumble forward with chaotic momentum for 0.75s
 *
 * Player stumbles forward with wavey motion for a fixed duration,
 * locked out from dashing again until stumble completes.
 *
 * @param state Current apex state
 * @param playerPos Position where miss occurred
 * @param timestamp Current game time
 * @param config Configuration
 * @returns Updated state and events
 */
export function onStrikeMiss(
  state: ApexStrikeState,
  playerPos: Vector2,
  timestamp: number,
  config: ApexStrikeConfig = APEX_CONFIG
): { state: ApexStrikeState; events: ApexEvent[] } {
  if (state.phase !== 'strike') {
    return { state, events: [] };
  }

  // End chain if we had one
  const chainEvents: ApexEvent[] = state.chainHits > 0
    ? [{
        type: 'chain_ended' as const,
        totalHits: state.chainHits,
        totalDamage: state.chainDamageDealt,
        timestamp,
      }]
    : [];

  // Calculate stumble momentum = 25% of original dash distance
  const chargeScaledDistance = config.minDistance +
    (config.maxDistance - config.minDistance) * state.chargeLevel;
  const stumbleMomentum = chargeScaledDistance * config.stumbleMomentumPercent;

  // Stumble duration: 0.75 seconds locked out from dashing
  const stumbleDuration = 750;

  const newState: ApexStrikeState = {
    ...state,
    phase: 'miss_recovery',
    cooldownRemaining: stumbleDuration,  // Locked out for stumble duration
    phaseTimer: 0,
    canChain: false,
    chainWindow: 0,
    // Reset chain stats
    chainDamageDealt: 0,
    chainHits: 0,
    // Use missPenaltyTimer as stumble duration timer
    missPenaltyPhase: 'stumble',
    missPenaltyTimer: stumbleDuration,
    // Initialize stumble momentum (instant feedback on miss)
    stumbleDirection: state.lockDirection,
    stumbleMomentum: stumbleMomentum,
    stumbleStartMomentum: stumbleMomentum,
    stumbleWavePhase: 0,
    // Clear ghost trail when strike ends
    ghostTrail: [],
  };

  const events: ApexEvent[] = [
    ...chainEvents,
    { type: 'strike_miss', position: playerPos, timestamp },
  ];

  return { state: newState, events };
}

/**
 * Attempt to chain from HIT phase
 * @param state Current apex state
 * @param aimDirection Direction for new strike
 * @param playerPos Current player position
 * @param timestamp Current game time
 * @returns Updated state and events
 */
export function attemptChain(
  state: ApexStrikeState,
  aimDirection: Vector2,
  playerPos: Vector2,
  timestamp: number
): { state: ApexStrikeState; events: ApexEvent[] } {
  if (!canChain(state)) {
    return { state, events: [] };
  }

  const fromEnemyId = state.lastHitEnemyId || 'unknown';

  // Chain immediately goes to LOCK phase (can be instant with quick input)
  const lockResult = initiateLock(
    {
      ...state,
      phase: 'ready',
      cooldownRemaining: 0,
      // Preserve chain stats
      chainDamageDealt: state.chainDamageDealt,
      chainHits: state.chainHits,
    },
    aimDirection,
    playerPos,
    timestamp
  );

  const events: ApexEvent[] = [
    { type: 'chain_started', fromEnemyId, direction: normalizeVector(aimDirection), timestamp },
    ...lockResult.events,
  ];

  return { state: lockResult.state, events };
}

// =============================================================================
// Charge System (DD-038-2)
// =============================================================================

/**
 * Clamp a value between min and max
 */
function clamp(value: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, value));
}

/**
 * WASD input for aim mode detection
 */
export interface WASDInput {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

/**
 * Check if any WASD key is pressed
 */
function hasWASDInput(input: WASDInput): boolean {
  return input.up || input.down || input.left || input.right;
}

/**
 * Update charge level during lock phase (DD-038-1, DD-038-2)
 *
 * Implements hybrid control schema:
 * - If mouse moved since charge start: use cursor direction
 * - If any WASD pressed during charge: switch to WASD direction
 * - Direction locks on release
 *
 * @param state Current apex state
 * @param deltaTime Time since last update (ms)
 * @param cursorPos Current cursor position (for cursor aim)
 * @param wasdInput Current WASD input state
 * @param config Configuration
 * @returns Updated state
 */
export function updateCharge(
  state: ApexStrikeState,
  deltaTime: number,
  cursorPos?: Vector2,
  wasdInput?: WASDInput,
  config: ApexStrikeConfig = APEX_CONFIG
): ApexStrikeState {
  if (state.phase !== 'lock') {
    return state;
  }

  const newState = { ...state };

  // Update charge time
  newState.chargeTime = state.chargeTime + deltaTime;

  // Calculate charge level: 0 at minChargeDuration, 1 at maxChargeDuration
  // chargePercent = clamp((chargeTime - 200) / 300, 0, 1)  // 300ms = 500-200
  const chargeDurationRange = config.maxChargeDuration - config.minChargeDuration;
  newState.chargeLevel = clamp(
    (newState.chargeTime - config.minChargeDuration) / chargeDurationRange,
    0,
    1
  );

  // Handle hybrid aim mode (DD-038-1)
  if (wasdInput && hasWASDInput(wasdInput)) {
    // WASD overrides cursor
    newState.aimMode = 'wasd';
    newState.lockDirection = getAimFromInput(wasdInput);
  } else if (cursorPos && state.chargeStartCursor) {
    // Check if cursor moved since charge start
    const dx = cursorPos.x - state.chargeStartCursor.x;
    const dy = cursorPos.y - state.chargeStartCursor.y;
    const cursorMoved = Math.abs(dx) > 5 || Math.abs(dy) > 5; // 5px deadzone

    if (cursorMoved && state.aimMode === 'cursor') {
      // Update direction towards cursor (relative to some reference - typically player position)
      // Note: The actual direction calculation depends on player position
      // which should be passed in or calculated externally
      // For now, we keep the lock direction but mark as cursor mode
      newState.aimMode = 'cursor';
    }
  }

  return newState;
}

/**
 * Get charge-scaled strike distance (DD-038-2)
 * Distance: 60px (0% charge) → 360px (100% charge)
 *
 * @param state Current apex state
 * @param config Configuration
 * @returns Scaled distance in pixels
 */
export function getChargeScaledDistance(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  const distanceRange = config.maxDistance - config.minDistance;
  return config.minDistance + distanceRange * state.chargeLevel;
}

/**
 * Get charge-scaled damage multiplier (DD-038-2)
 * Damage: 1.0x (0% charge) → 2.0x (100% charge)
 *
 * @param state Current apex state
 * @param config Configuration
 * @returns Damage multiplier
 */
export function getChargeScaledDamage(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  const damageRange = config.maxDamageMultiplier - config.minDamageMultiplier;
  return config.minDamageMultiplier + damageRange * state.chargeLevel;
}

/**
 * Get charge level as a percentage (0-1)
 * @param state Current apex state
 * @returns Charge percentage
 */
export function getChargePercent(state: ApexStrikeState): number {
  return state.chargeLevel;
}

// =============================================================================
// Miss Penalty System (DD-038-5)
// =============================================================================

/**
 * Check if player is in any miss penalty phase
 * @param state Current apex state
 * @returns Whether player is in miss penalty
 */
export function isInMissPenalty(state: ApexStrikeState): boolean {
  return state.missPenaltyPhase !== null;
}

/**
 * Get speed multiplier during miss penalty (DD-038-5)
 * - Stumble: 50% speed
 * - Vulnerable/Recovery: normal speed
 *
 * @param state Current apex state
 * @param config Configuration
 * @returns Speed multiplier (1.0 = normal)
 */
export function getMissPenaltySpeedMult(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  if (state.missPenaltyPhase === 'stumble') {
    return config.stumbleSpeedMult;
  }
  return 1.0;
}

/**
 * Get damage multiplier during miss penalty (DD-038-5)
 * - Vulnerable: 1.5x damage taken
 * - Other phases: normal damage
 *
 * @param state Current apex state
 * @param config Configuration
 * @returns Damage multiplier for incoming damage
 */
export function getMissPenaltyDamageMult(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  if (state.missPenaltyPhase === 'vulnerable') {
    return config.vulnerableDamageMult;
  }
  return 1.0;
}

/**
 * Check if player can attack (not in stumble)
 * @param state Current apex state
 * @returns Whether player can attack
 */
export function canAttackDuringMissPenalty(state: ApexStrikeState): boolean {
  return state.missPenaltyPhase !== 'stumble';
}

/**
 * Update miss penalty phase transitions (DD-038-5)
 * Stumble (0.3s) → Vulnerable (0.4s) → Recovery (0.8s) → Ready
 *
 * @param state Current apex state
 * @param deltaTime Time since last update (ms)
 * @param config Configuration
 * @returns Updated state
 */
export function updateMissPenalty(
  state: ApexStrikeState,
  deltaTime: number,
  config: ApexStrikeConfig = APEX_CONFIG
): ApexStrikeState {
  if (state.missPenaltyPhase === null) {
    return state;
  }

  const newState = { ...state };
  newState.missPenaltyTimer = Math.max(0, state.missPenaltyTimer - deltaTime);

  // Transition to next phase when timer expires
  if (newState.missPenaltyTimer <= 0) {
    switch (state.missPenaltyPhase) {
      case 'stumble':
        // Stumble → Vulnerable
        newState.missPenaltyPhase = 'vulnerable';
        newState.missPenaltyTimer = config.vulnerableDuration;
        break;
      case 'vulnerable':
        // Vulnerable → Recovery
        newState.missPenaltyPhase = 'recovery';
        newState.missPenaltyTimer = config.recoveryDuration;
        break;
      case 'recovery':
        // Recovery → Ready
        newState.missPenaltyPhase = null;
        newState.missPenaltyTimer = 0;
        newState.phase = 'ready';
        break;
    }
  }

  return newState;
}

/**
 * Initiate miss penalty sequence (DD-038-5)
 * Called when strike misses - starts stumble phase
 *
 * @param state Current apex state
 * @param config Configuration
 * @returns Updated state with stumble phase initiated
 */
export function initiateMissPenalty(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): ApexStrikeState {
  return {
    ...state,
    missPenaltyPhase: 'stumble',
    missPenaltyTimer: config.stumbleDuration,
  };
}

/**
 * Get total miss penalty duration (all three phases)
 * @param config Configuration
 * @returns Total duration in ms
 */
export function getTotalMissPenaltyDuration(
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  return config.stumbleDuration + config.vulnerableDuration + config.recoveryDuration;
}

/**
 * Get miss penalty progress (0 = just started, 1 = about to end)
 * @param state Current apex state
 * @param config Configuration
 * @returns Progress percentage
 */
export function getMissPenaltyProgress(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  if (state.missPenaltyPhase === null) {
    return 0;
  }

  const totalDuration = getTotalMissPenaltyDuration(config);
  let elapsed = 0;

  switch (state.missPenaltyPhase) {
    case 'stumble':
      elapsed = config.stumbleDuration - state.missPenaltyTimer;
      break;
    case 'vulnerable':
      elapsed = config.stumbleDuration + (config.vulnerableDuration - state.missPenaltyTimer);
      break;
    case 'recovery':
      elapsed = config.stumbleDuration + config.vulnerableDuration + (config.recoveryDuration - state.missPenaltyTimer);
      break;
  }

  return clamp(elapsed / totalDuration, 0, 1);
}

// =============================================================================
// Hit Detection
// =============================================================================

/**
 * Check for strike hit against enemies
 * Run 038: Now supports multi-hit detection with hit stop frames
 * @param state Current apex state
 * @param playerPos Current player position
 * @param enemies List of potential targets
 * @param timestamp Current game time
 * @param config Configuration
 * @returns Hit result with updated state and all hit enemies
 */
export function checkStrikeHit(
  state: ApexStrikeState,
  playerPos: Vector2,
  enemies: ApexTarget[],
  timestamp: number,
  config: ApexStrikeConfig = APEX_CONFIG
): StrikeHitResult {
  if (state.phase !== 'strike') {
    return { state, hitEnemy: null, hitEnemies: [], damage: 0, events: [] };
  }

  // Run 038: Check collision with ALL enemies (multi-hit support)
  // Apply strike hitbox multiplier (slightly larger than visual for generous feel)
  const strikeRadius = config.playerRadius * config.strikeHitboxMultiplier;

  const hitEnemies: Enemy[] = [];
  for (const enemy of enemies) {
    const dx = enemy.position.x - playerPos.x;
    const dy = enemy.position.y - playerPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const collisionDistance = strikeRadius + enemy.radius;

    if (distance <= collisionDistance) {
      hitEnemies.push(enemy as Enemy);
    }
  }

  // No enemies hit
  if (hitEnemies.length === 0) {
    return { state, hitEnemy: null, hitEnemies: [], damage: 0, events: [] };
  }

  // Process hit(s) - use first enemy as primary for existing logic
  const primaryEnemy = hitEnemies[0];
  const hitResult = onStrikeHit(state, primaryEnemy, playerPos, timestamp, config);
  const events = [...hitResult.events];

  // Run 038: Calculate hit stop duration for multi-hit (ms)
  // Small: 2 enemies, Medium: 3 enemies, Heavy: 4+ enemies
  let hitStopMs = 0;
  if (hitEnemies.length >= 4) {
    hitStopMs = config.hitStopMsHeavy;    // 285ms for 4+
  } else if (hitEnemies.length === 3) {
    hitStopMs = config.hitStopMsMedium;   // 225ms for 3
  } else if (hitEnemies.length === 2) {
    hitStopMs = config.hitStopMsSmall;    // 175ms for 2
  }

  // Calculate center position of all hits for visual effect
  const avgX = hitEnemies.reduce((sum, e) => sum + e.position.x, 0) / hitEnemies.length;
  const avgY = hitEnemies.reduce((sum, e) => sum + e.position.y, 0) / hitEnemies.length;
  const multiHitPosition = { x: avgX, y: avgY };

  // Add multi-hit event if 2+ enemies
  if (hitEnemies.length >= 2) {
    events.push({
      type: 'multi_hit',
      hitCount: hitEnemies.length,
      position: multiHitPosition,
      hitStopFrames: hitStopMs, // Now in ms directly
      timestamp,
    });
  }

  // Update state with hit stop info
  // IMPORTANT: hitStopFrames stores the END TIME using performance.now() (wall-clock time)
  // This ensures the freeze ends correctly even though gameTime doesn't advance during freeze
  const hitStopEndTime = hitStopMs > 0 ? performance.now() + hitStopMs : hitResult.state.hitStopFrames;
  if (hitStopMs > 0) {
    console.log(`[MULTI-HIT SET] duration=${hitStopMs}ms, endTime=${hitStopEndTime.toFixed(0)}, now=${performance.now().toFixed(0)}`);
  }
  const updatedState: ApexStrikeState = {
    ...hitResult.state,
    hitStopFrames: hitStopEndTime,
    multiHitCount: hitEnemies.length >= 2 ? hitEnemies.length : hitResult.state.multiHitCount,
    multiHitPosition: hitEnemies.length >= 2 ? multiHitPosition : hitResult.state.multiHitPosition,
  };

  return {
    state: updatedState,
    hitEnemy: primaryEnemy,
    hitEnemies,
    damage: hitResult.damage,
    events,
  };
}

// =============================================================================
// Per-Frame Update
// =============================================================================

/**
 * Filter out expired ghost afterimages
 */
function cleanupGhostTrail(
  ghosts: GhostAfterimage[],
  currentTime: number,
  fadeDuration: number
): GhostAfterimage[] {
  return ghosts.filter(ghost => currentTime - ghost.spawnTime < fadeDuration);
}

/**
 * Get current opacity for a ghost afterimage (0 = fully faded, 1 = full opacity)
 *
 * Sequential fade: oldest ghosts (lower index) fade out first while newer ones stay visible.
 * Opacity is based on position in the trail, not individual age.
 *
 * @param index - Ghost's position in the array (0 = oldest)
 * @param totalGhosts - Total number of ghosts in the trail
 * @param config - Ghost trail configuration
 */
export function getGhostOpacity(
  index: number,
  totalGhosts: number,
  config: GhostTrailConfig = GHOST_TRAIL_CONFIG
): number {
  if (totalGhosts === 0) return 0;

  // Position ratio: 0 (oldest) to 1 (newest)
  // index 0 → ratio close to 0 (faded)
  // index (totalGhosts-1) → ratio = 1 (full opacity)
  const positionRatio = (index + 1) / totalGhosts;

  // Apply ease-in curve so oldest fades faster
  const easedRatio = positionRatio * positionRatio;

  return config.initialOpacity * easedRatio;
}

/**
 * Update Apex Strike state each frame
 * @param state Current apex state
 * @param deltaTime Time since last update (ms)
 * @param playerPos Current player position
 * @param timestamp Current game time
 * @param config Configuration
 * @returns Update result with state, events, and velocity
 */
export function updateApexStrike(
  state: ApexStrikeState,
  deltaTime: number,
  playerPos: Vector2,
  timestamp: number,
  config: ApexStrikeConfig = APEX_CONFIG,
  playerInputDirection?: Vector2  // Optional: player's desired direction for steering during dash
): ApexUpdateResult {
  const events: ApexEvent[] = [];
  let newState = { ...state };

  // Update phase timer
  newState.phaseTimer += deltaTime;

  // Update cooldown
  if (newState.cooldownRemaining > 0) {
    newState.cooldownRemaining = Math.max(0, newState.cooldownRemaining - deltaTime);
    if (newState.cooldownRemaining <= 0 && state.cooldownRemaining > 0) {
      events.push({ type: 'cooldown_ended', timestamp });
    }
  }

  // Decay bloodlust when not in active strike
  if (newState.phase === 'ready' || newState.phase === 'miss_recovery') {
    const decay = (config.bloodlustDecay * deltaTime) / 1000;
    const oldBloodlust = newState.bloodlust;
    newState.bloodlust = Math.max(0, newState.bloodlust - decay);
    if (oldBloodlust > 0 && newState.bloodlust <= 0) {
      events.push({ type: 'bloodlust_depleted', timestamp });
    }
  }

  // Phase-specific updates
  switch (newState.phase) {
    case 'lock': {
      // Update lock timer (for animation/UI purposes only)
      // Strike is ONLY triggered by space release in the game loop
      // The hornet can hold the lock as long as they want to aim
      newState.lockTimer += deltaTime;
      return { state: newState, events, velocity: null };
    }

    case 'strike': {
      // === ROCKET BOOST DASH: Progressive steering and speed decay ===

      const deltaSeconds = deltaTime / 1000;

      // --- Phase 1: Burst (no steering) ---
      const inBurstPhase = newState.phaseTimer < config.dashBurstDuration;

      // --- Phase 2: Glide (progressive steering, speed decay) ---
      if (!inBurstPhase) {
        // Increase steering control over time
        newState.dashSteerControl = Math.min(1, newState.dashSteerControl + config.dashSteerGainRate * deltaSeconds);

        // Decay speed exponentially
        const speedDecay = Math.exp(-config.dashSpeedDecayRate * deltaSeconds);
        newState.dashCurrentSpeed = Math.max(config.dashMinSpeed, newState.dashCurrentSpeed * speedDecay);

        // Blend direction with player input if available
        if (playerInputDirection && newState.dashCurrentDirection) {
          const inputMag = Math.sqrt(playerInputDirection.x ** 2 + playerInputDirection.y ** 2);
          if (inputMag > 0.1) {
            // Normalize input
            const normalizedInput = {
              x: playerInputDirection.x / inputMag,
              y: playerInputDirection.y / inputMag,
            };

            // Blend: (1 - steerControl) * lockDir + steerControl * inputDir
            const blendedX = (1 - newState.dashSteerControl) * newState.dashCurrentDirection.x +
                            newState.dashSteerControl * normalizedInput.x;
            const blendedY = (1 - newState.dashSteerControl) * newState.dashCurrentDirection.y +
                            newState.dashSteerControl * normalizedInput.y;

            // Normalize the blended direction
            const blendedMag = Math.sqrt(blendedX ** 2 + blendedY ** 2);
            if (blendedMag > 0) {
              newState.dashCurrentDirection = {
                x: blendedX / blendedMag,
                y: blendedY / blendedMag,
              };
            }
          }
        }
      }

      // Track distance traveled
      const moveDistance = (newState.dashCurrentSpeed * deltaTime) / 1000;
      newState.strikeDistanceRemaining = Math.max(0, newState.strikeDistanceRemaining - moveDistance);

      // --- Ghost trail: spawn afterimages during strike ---
      const ghostConfig = GHOST_TRAIL_CONFIG;
      if (timestamp - newState.lastGhostSpawnTime >= ghostConfig.spawnInterval) {
        const newGhost: GhostAfterimage = {
          position: { ...playerPos },
          direction: newState.dashCurrentDirection || newState.lockDirection || { x: 1, y: 0 },
          spawnTime: timestamp,
          initialOpacity: ghostConfig.initialOpacity,
        };

        // Add to trail, keeping max count
        newState.ghostTrail = [...newState.ghostTrail, newGhost].slice(-ghostConfig.maxGhosts);
        newState.lastGhostSpawnTime = timestamp;
      }

      // Clean up expired ghosts
      newState.ghostTrail = cleanupGhostTrail(newState.ghostTrail, timestamp, ghostConfig.fadeDuration);

      // --- Check for dash completion ---
      // Complete when: distance exhausted OR boost duration exceeded OR speed dropped to normal
      // Boost duration = charge time, so longer charge = longer boost
      const distanceExhausted = newState.strikeDistanceRemaining <= 0;
      const timeExhausted = newState.phaseTimer >= newState.boostDuration;
      const speedDecayed = newState.dashCurrentSpeed <= config.normalSpeed * 1.1;
      const dashComplete = distanceExhausted || timeExhausted || speedDecayed;

      if (dashComplete) {
        // Smoothly return to ready state (no penalty on "miss")
        newState.phase = 'ready';
        newState.dashCurrentSpeed = 0;
        newState.dashSteerControl = 0;
        newState.dashCurrentDirection = null;
        newState.lockDirection = null;
        // Clear ghost trail when dash ends
        newState.ghostTrail = [];
        // Small cooldown to prevent spam
        newState.cooldownRemaining = 200;
        return { state: newState, events, velocity: null };
      }

      // --- Calculate velocity for this frame ---
      const currentDir = newState.dashCurrentDirection || newState.lockDirection || { x: 1, y: 0 };
      const velocity: Vector2 = {
        x: currentDir.x * newState.dashCurrentSpeed,
        y: currentDir.y * newState.dashCurrentSpeed,
      };

      return { state: newState, events, velocity };
    }

    case 'hit': {
      // Update chain window
      if (newState.chainWindow > 0) {
        newState.chainWindow = Math.max(0, newState.chainWindow - deltaTime);
      }

      // --- HIT BOOST: Apply decaying burst velocity ---
      let hitBoostVelocity: Vector2 | null = null;

      if (newState.hitBoostTimer > 0 && newState.hitBoostDirection && newState.hitBoostMomentum > 0) {
        // Decay hit boost exponentially
        const decayFactor = Math.exp(-config.hitBoostDecayRate * deltaTime / 1000);
        newState.hitBoostMomentum *= decayFactor;
        newState.hitBoostTimer = Math.max(0, newState.hitBoostTimer - deltaTime);

        // Calculate velocity from current momentum
        if (newState.hitBoostMomentum > 10) { // Threshold to stop tiny movements
          hitBoostVelocity = {
            x: newState.hitBoostDirection.x * newState.hitBoostMomentum,
            y: newState.hitBoostDirection.y * newState.hitBoostMomentum,
          };
        }

        // Clear boost when timer expires
        if (newState.hitBoostTimer <= 0) {
          newState.hitBoostDirection = null;
          newState.hitBoostMomentum = 0;
        }
      }

      // After grip duration, start chain window countdown
      if (newState.phaseTimer >= config.gripDuration && newState.canChain) {
        // Chain window is already counting down
      }

      // If chain window expires, transition to ready
      if (newState.phaseTimer >= config.gripDuration + config.chainWindow) {
        // Chain ended
        if (newState.chainHits > 0) {
          events.push({
            type: 'chain_ended',
            totalHits: newState.chainHits,
            totalDamage: newState.chainDamageDealt,
            timestamp,
          });
        }

        newState.phase = 'ready';
        newState.canChain = false;
        newState.chainHits = 0;
        newState.chainDamageDealt = 0;
        // Clear hit boost
        newState.hitBoostDirection = null;
        newState.hitBoostMomentum = 0;
        // Clear any lingering ghost trail
        newState.ghostTrail = [];
        // No cooldown on successful hit!
      }
      return { state: newState, events, velocity: hitBoostVelocity };
    }

    case 'miss_recovery': {
      // Stumble momentum for 0.75s - locked out from dashing
      // Momentum decays rapidly but player keeps moving forward with wavey motion

      let stumbleVelocity: Vector2 | null = null;
      const deltaSeconds = deltaTime / 1000;

      // Count down the stumble timer
      newState.missPenaltyTimer = Math.max(0, newState.missPenaltyTimer - deltaTime);

      // While we have stumble momentum, apply wavey, decaying motion
      if (newState.stumbleMomentum > 0 && newState.stumbleDirection) {
        // Update wave phase for chaotic oscillation
        newState.stumbleWavePhase += config.stumbleWaveFrequency * Math.PI * 2 * deltaSeconds;

        // Calculate velocity BEFORE decaying (so we move this frame)
        stumbleVelocity = getStumbleVelocity(newState, null, config);

        // Rapid decay - momentum decays quickly over the 0.75s duration
        // Using decay rate of 6.0 means ~99% decay over 0.75s
        const rapidDecayRate = 6.0;
        const decayMultiplier = Math.exp(-rapidDecayRate * deltaSeconds);
        newState.stumbleMomentum *= decayMultiplier;

        // Clear momentum when negligible
        if (newState.stumbleMomentum < 1) {
          newState.stumbleMomentum = 0;
          newState.stumbleDirection = null;
        }
      }

      // Only return to ready when timer expires (locked out until then)
      if (newState.missPenaltyTimer <= 0) {
        newState.phase = 'ready';
        newState.missPenaltyPhase = null;
        newState.stumbleMomentum = 0;
        newState.stumbleDirection = null;
        // Clear any lingering ghost trail
        newState.ghostTrail = [];
      }

      return { state: newState, events, velocity: stumbleVelocity };
    }

    default:
      return { state: newState, events, velocity: null };
  }
}

/**
 * Get velocity during strike phase
 * @param state Current apex state
 * @param config Configuration
 * @returns Velocity vector or zero if not striking
 */
export function getStrikeVelocity(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): Vector2 {
  if (state.phase !== 'strike' || !state.lockDirection) {
    return { x: 0, y: 0 };
  }

  const strikeSpeed = BASE_PLAYER_SPEED * config.strikeSpeed;

  return {
    x: state.lockDirection.x * strikeSpeed,
    y: state.lockDirection.y * strikeSpeed,
  };
}

/**
 * Get velocity during stumble phase (chaotic, decaying motion)
 *
 * Creates a wavey, uncontrolled feel by:
 * 1. Sharp velocity impulse at start (2.5x) that decays with momentum
 * 2. Adding perpendicular oscillation (wobble)
 * 3. Rapidly decaying the speed
 * 4. Player control scales INVERSELY with momentum (0% at start → 90% at end)
 *
 * @param state Current apex state
 * @param playerInput Optional player WASD input to blend in
 * @param config Configuration
 * @returns Velocity vector for stumble movement
 */
export function getStumbleVelocity(
  state: ApexStrikeState,
  playerInput: Vector2 | null = null,
  config: ApexStrikeConfig = APEX_CONFIG
): Vector2 {
  // Only apply when we have stumble momentum
  if (!state.stumbleDirection || state.stumbleMomentum <= 0) {
    return { x: 0, y: 0 };
  }

  // Calculate decay factor (how much momentum is left as 0-1)
  // decayFactor = 1 at start (full momentum), 0 at end (no momentum)
  const decayFactor = state.stumbleMomentum / state.stumbleStartMomentum;

  // Sharp velocity impulse: starts at impulseMultiplier (e.g., 2.5x), decays to 1.0x
  // impulseBoost = 1.0 + (impulseMultiplier - 1.0) * decayFactor
  // At start (decayFactor=1): impulseBoost = impulseMultiplier (2.5x)
  // At end (decayFactor=0): impulseBoost = 1.0x
  const impulseBoost = 1.0 + (config.stumbleImpulseMultiplier - 1.0) * decayFactor;

  // Base stumble speed with impulse boost
  // Speed = decayFactor * impulseBoost * base_player_speed * 2
  const stumbleSpeed = decayFactor * impulseBoost * BASE_PLAYER_SPEED * 2;

  // Calculate perpendicular direction for wobble
  // Perpendicular = rotate 90 degrees: (x, y) → (-y, x)
  const perpDir: Vector2 = {
    x: -state.stumbleDirection.y,
    y: state.stumbleDirection.x,
  };

  // Wavey offset: sin(phase) * amplitude
  // Minimum angle change of 7.5 degrees = tan(7.5°) ≈ 0.1317
  const MIN_WAVE_OFFSET = 0.1317;
  let waveOffset = Math.sin(state.stumbleWavePhase) * config.stumbleWaveAmplitude;

  // Ensure the wave is always at least 7.5° off-center in either direction
  // This prevents the wave from passing through center (no deflection)
  if (Math.abs(waveOffset) < MIN_WAVE_OFFSET) {
    waveOffset = waveOffset >= 0 ? MIN_WAVE_OFFSET : -MIN_WAVE_OFFSET;
  }

  // Combine forward direction with perpendicular wobble
  const stumbleDirX = state.stumbleDirection.x + perpDir.x * waveOffset;
  const stumbleDirY = state.stumbleDirection.y + perpDir.y * waveOffset;

  // Normalize the combined direction
  const combinedMag = Math.sqrt(stumbleDirX * stumbleDirX + stumbleDirY * stumbleDirY);
  const normDirX = combinedMag > 0 ? stumbleDirX / combinedMag : state.stumbleDirection.x;
  const normDirY = combinedMag > 0 ? stumbleDirY / combinedMag : state.stumbleDirection.y;

  // Calculate stumble velocity
  let velocityX = normDirX * stumbleSpeed;
  let velocityY = normDirY * stumbleSpeed;

  // Player control scales INVERSELY with momentum:
  // At start (decayFactor=1): 0% player control (stumble takes over)
  // At end (decayFactor=0): maxPlayerControl (e.g., 90%) - player regains control
  const effectivePlayerControl = (1.0 - decayFactor) * config.stumbleMaxPlayerControl;

  if (playerInput && (playerInput.x !== 0 || playerInput.y !== 0)) {
    const playerMag = Math.sqrt(playerInput.x * playerInput.x + playerInput.y * playerInput.y);
    if (playerMag > 0) {
      const playerDirX = playerInput.x / playerMag;
      const playerDirY = playerInput.y / playerMag;
      // Player speed scales with effective control (more control = more influence)
      const playerSpeed = BASE_PLAYER_SPEED * effectivePlayerControl;

      velocityX += playerDirX * playerSpeed;
      velocityY += playerDirY * playerSpeed;
    }
  }

  return { x: velocityX, y: velocityY };
}

/**
 * Get stumble momentum progress (1 = just missed, 0 = momentum exhausted)
 * @param state Current apex state
 * @returns Stumble momentum as 0-1
 */
export function getStumbleMomentumProgress(state: ApexStrikeState): number {
  if (state.stumbleStartMomentum <= 0) return 0;
  return state.stumbleMomentum / state.stumbleStartMomentum;
}

/**
 * Check if currently stumbling with momentum
 * @param state Current apex state
 * @returns Whether stumble momentum is active
 */
export function hasStumbleMomentum(state: ApexStrikeState): boolean {
  return state.stumbleMomentum > 0 && state.stumbleDirection !== null;
}

// =============================================================================
// Query Functions
// =============================================================================

/**
 * Check if player is vulnerable (can take knockback)
 * @param state Current apex state
 * @returns Whether player is vulnerable
 */
export function isVulnerable(state: ApexStrikeState): boolean {
  return state.phase === 'lock' || state.phase === 'miss_recovery';
}

/**
 * Check if player is unstoppable (takes damage but no knockback)
 * @param state Current apex state
 * @returns Whether player is unstoppable
 */
export function isUnstoppable(state: ApexStrikeState): boolean {
  return state.phase === 'strike';
}

/**
 * Check if player is in active strike
 * @param state Current apex state
 * @returns Whether currently striking
 */
export function isStriking(state: ApexStrikeState): boolean {
  return state.phase === 'strike';
}

/**
 * Check if player is in lock phase
 * @param state Current apex state
 * @returns Whether currently locking
 */
export function isLocking(state: ApexStrikeState): boolean {
  return state.phase === 'lock';
}

/**
 * Check if in grip moment after hit
 * @param state Current apex state
 * @param config Configuration
 * @returns Whether in grip moment
 */
export function isInGripMoment(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): boolean {
  return state.phase === 'hit' && state.phaseTimer < config.gripDuration;
}

/**
 * Get bloodlust as normalized value (0-1)
 * @param state Current apex state
 * @param config Configuration
 * @returns Bloodlust percentage
 */
export function getBloodlustPercent(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  return state.bloodlust / config.bloodlustMax;
}

/**
 * Get current damage multiplier from bloodlust
 * @param state Current apex state
 * @param config Configuration
 * @returns Damage multiplier
 */
export function getBloodlustDamageMultiplier(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  const percent = getBloodlustPercent(state, config);
  return 1 + percent * (config.bloodlustDamageBonus - 1);
}

/**
 * Get cooldown progress (0 = ready, 1 = full cooldown)
 * @param state Current apex state
 * @param config Configuration
 * @returns Cooldown progress
 */
export function getCooldownProgress(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  if (state.cooldownRemaining <= 0) return 0;
  return state.cooldownRemaining / config.baseCooldown;
}

/**
 * Get chain window progress (0 = expired, 1 = full)
 * @param state Current apex state
 * @param config Configuration
 * @returns Chain window progress
 */
export function getChainWindowProgress(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  if (!state.canChain || state.chainWindow <= 0) return 0;
  return state.chainWindow / config.chainWindow;
}

/**
 * Get lock progress (0-1)
 * @param state Current apex state
 * @param config Configuration
 * @returns Lock progress
 */
export function getLockProgress(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  if (state.phase !== 'lock') return 0;
  return Math.min(1, state.lockTimer / config.lockDuration);
}

/**
 * Get strike progress (0-1)
 * @param state Current apex state
 * @param config Configuration
 * @returns Strike progress
 */
export function getStrikeProgress(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): number {
  if (state.phase !== 'strike') return 0;
  return 1 - (state.strikeDistanceRemaining / config.strikeDistance);
}

// =============================================================================
// Visual Helper Functions
// =============================================================================

/**
 * Get color for bloodlust meter
 * @param state Current apex state
 * @param config Configuration
 * @returns Hex color string
 */
export function getBloodlustColor(
  state: ApexStrikeState,
  config: ApexStrikeConfig = APEX_CONFIG
): string {
  const percent = getBloodlustPercent(state, config);
  if (percent >= 1) return '#FF0000';       // Max: pure red
  if (percent >= 0.75) return '#FF4400';    // High: orange-red
  if (percent >= 0.5) return '#FF8800';     // Medium: orange
  if (percent >= 0.25) return '#FFCC00';    // Low: yellow
  return '#888888';                          // Empty: gray
}

/**
 * Get strike trail points for rendering
 * @param state Current apex state
 * @param playerPos Current player position
 * @returns Array of points for trail
 */
export function getStrikeTrailPoints(
  state: ApexStrikeState,
  playerPos: Vector2
): Vector2[] {
  if (state.phase !== 'strike' || !state.strikeStartPos) {
    return [];
  }

  return [
    { ...state.strikeStartPos },
    { ...playerPos },
  ];
}

/**
 * Get aim indicator end point
 * @param state Current apex state
 * @param playerPos Current player position
 * @param config Configuration
 * @returns End point of aim indicator
 */
export function getAimIndicatorEnd(
  state: ApexStrikeState,
  playerPos: Vector2,
  config: ApexStrikeConfig = APEX_CONFIG
): Vector2 | null {
  if (state.phase !== 'lock' || !state.lockDirection) {
    return null;
  }

  // Show indicator at 50% of strike distance
  const indicatorLength = config.strikeDistance * 0.5;

  return {
    x: playerPos.x + state.lockDirection.x * indicatorLength,
    y: playerPos.y + state.lockDirection.y * indicatorLength,
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Normalize a vector to unit length
 * @param v Vector to normalize
 * @returns Normalized vector (or right direction if zero)
 */
function normalizeVector(v: Vector2): Vector2 {
  const mag = Math.sqrt(v.x * v.x + v.y * v.y);
  if (mag === 0) {
    return { x: 1, y: 0 };
  }
  return {
    x: v.x / mag,
    y: v.y / mag,
  };
}

/**
 * Get aim direction from WASD input
 * @param input Input state with up/down/left/right
 * @returns Aim direction vector
 */
export function getAimFromInput(input: {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}): Vector2 {
  let x = 0;
  let y = 0;

  if (input.left) x -= 1;
  if (input.right) x += 1;
  if (input.up) y -= 1;
  if (input.down) y += 1;

  // Return normalized, or default right if no input
  if (x === 0 && y === 0) {
    return { x: 1, y: 0 };
  }

  return normalizeVector({ x, y });
}

// =============================================================================
// APEX STRIKE DAMAGE CALCULATION SYSTEM (Run 050)
// =============================================================================
//
// This system provides:
// 1. Centralized damage calculation with ALL ability bonuses
// 2. Damage preview for UI display during charge
// 3. Debug logging for verification
// 4. Clear documentation of how each ability affects damage
//
// ABILITY → DAMAGE MAPPING:
// ┌─────────────────────────────────────────────────────────────────────────┐
// │ CATEGORY    │ ABILITY            │ HOW IT AFFECTS APEX STRIKE DAMAGE   │
// ├─────────────┼────────────────────┼─────────────────────────────────────┤
// │ MANDIBLE    │ serration          │ Bleed DoT (1% HP/2s)                │
// │             │ scissor_grip       │ Stun chance (indirect DPS boost)    │
// │             │ chitin_crack       │ Armor reduction → +damage           │
// │             │ resonant_strike    │ Knockback (positioning, no damage)  │
// │             │ sawtooth           │ Every 5th hit +30%                  │
// │             │ nectar_sense       │ Marks (tactical, no direct damage)  │
// ├─────────────┼────────────────────┼─────────────────────────────────────┤
// │ VENOM       │ trace_venom        │ Slow stacks (indirect, no damage)   │
// │             │ lingering_sting    │ Healing delay (no direct damage)    │
// │             │ melittin_traces    │ +5% to poisoned/slowed enemies      │
// │             │ pheromone_tag      │ Damage redirect (no direct damage)  │
// │             │ paralytic_microdose│ Freeze chance (indirect)            │
// │             │ histamine_burst    │ +8% to slowed enemies               │
// ├─────────────┼────────────────────┼─────────────────────────────────────┤
// │ WING        │ draft              │ Pull enemies (positioning)          │
// │             │ buzz_field         │ Stationary DPS aura                 │
// │             │ thermal_wake       │ Trail slow (no damage)              │
// │             │ scatter_dust       │ Vision obscure (defensive)          │
// │             │ updraft            │ Speed boost on kill (mobility)      │
// │             │ hover_pressure     │ Proximity DPS aura                  │
// ├─────────────┼────────────────────┼─────────────────────────────────────┤
// │ PREDATOR    │ feeding_efficiency │ Attack speed (cooldown, not damage) │
// │             │ territorial_mark   │ +10% in kill zones                  │
// │             │ trophy_scent       │ +1% permanent per unique enemy type │
// │             │ pack_signal        │ Enemy hesitation (indirect)         │
// │             │ corpse_heat        │ +5% near corpses                    │
// │             │ clean_kill         │ Explosion on one-hit kill           │
// ├─────────────┼────────────────────┼─────────────────────────────────────┤
// │ PHEROMONE   │ threat_aura        │ Enemy damage reduction (defensive)  │
// │             │ confusion_cloud    │ Enemy miss chance (defensive)       │
// │             │ rally_scent        │ Trail slow (no damage)              │
// │             │ death_marker       │ Corpse slow zone (no damage)        │
// │             │ aggro_pulse        │ Aggro control (no damage)           │
// │             │ bitter_taste       │ Enemy damage reduction (defensive)  │
// ├─────────────┼────────────────────┼─────────────────────────────────────┤
// │ CHITIN      │ barbed_chitin      │ Touch damage on contact             │
// │             │ ablative_shell     │ First hit reduction (defensive)     │
// │             │ heat_retention     │ Speed below 50% HP (mobility)       │
// │             │ compound_eyes      │ Telegraph advance (tactical)        │
// │             │ antenna_sensitivity│ Offscreen warning (tactical)        │
// │             │ molting_burst      │ Emergency invuln + burst            │
// └─────────────┴────────────────────┴─────────────────────────────────────┘
//
// DIRECT DAMAGE MULTIPLIERS (stackable):
// - Base: config.strikeDamage (25)
// - Bloodlust: 1.0x → 2.0x (0-100 bloodlust)
// - Charge: 1.0x → 2.0x (0-1 charge level)
// - Trophy Scent: +1% per unique enemy type killed
// - Territorial Mark: +10% when in kill zone
// - Corpse Heat: +5% when near corpse
// - Sawtooth: +30% every 5th hit
// - Melittin Traces: +5% to poisoned enemies
// - Histamine Burst: +8% to slowed enemies
// - Chitin Crack: Up to +50% from armor reduction
//
// Formula: final_damage = base * bloodlust * charge * (1 + sum_of_bonuses)
// =============================================================================

/**
 * Input parameters for apex strike damage calculation
 */
export interface ApexDamageInput {
  // Apex strike state
  bloodlust: number;
  chargeLevel: number;

  // Ability bonuses (from computeAbilityEffects)
  trophyScentBonus: number;          // % from unique kills (0-100+)
  inTerritorialZone: boolean;        // Is player in a kill zone?
  territorialBonus: number;          // % bonus in zone (typically 10)
  nearCorpse: boolean;               // Is player near a corpse?
  corpseHeatBonus: number;           // % bonus near corpse (typically 5)
  sawtoothTriggered: boolean;        // Is this the 5th hit?
  sawtoothBonus: number;             // % bonus on 5th hit (typically 30)

  // Enemy-specific bonuses (venom)
  enemyIsPoisoned: boolean;          // Does enemy have venom status?
  poisonedDamageAmp: number;         // % bonus to poisoned (typically 5)
  enemyIsSlowed: boolean;            // Does enemy have slow stacks?
  histamineDamageAmp: number;        // % bonus to slowed (typically 8)

  // Armor reduction
  enemyArmorReduced: number;         // Armor already reduced by chitin_crack (0-100)

  // Bumper/rail bonus (from bumper system)
  bumperDamageBonus: number;         // Flat damage bonus from chains
}

/**
 * Output of apex strike damage calculation
 */
export interface ApexDamageResult {
  // Final damage value
  finalDamage: number;

  // Breakdown for UI/debugging
  baseDamage: number;
  bloodlustMultiplier: number;
  chargeMultiplier: number;
  abilityBonusPercent: number;       // Total % from abilities
  armorBonusPercent: number;         // % from armor reduction
  flatBonus: number;                 // Flat bonus (bumper)

  // Ability flags (for visual feedback)
  bonuses: {
    trophyScent: boolean;
    territorial: boolean;
    corpseHeat: boolean;
    sawtooth: boolean;
    melittin: boolean;
    histamine: boolean;
    armorCrack: boolean;
  };
}

/**
 * Calculate apex strike damage with ALL ability bonuses
 *
 * This is the single source of truth for apex strike damage calculation.
 * Use this for:
 * 1. Actual damage application in combat
 * 2. Damage preview UI during charge
 * 3. Debug logging
 *
 * @param input - All parameters affecting damage
 * @param config - Apex strike config
 * @param debug - Whether to log calculation details
 * @returns Damage result with breakdown
 */
export function calculateApexStrikeDamage(
  input: ApexDamageInput,
  config: ApexStrikeConfig = APEX_CONFIG,
  debug: boolean = false
): ApexDamageResult {
  // --- BASE DAMAGE ---
  const baseDamage = config.strikeDamage;

  // --- MULTIPLIERS (from apex-strike system) ---
  // Bloodlust: 1.0x at 0, 2.0x at max
  const bloodlustMultiplier = 1 + (input.bloodlust / config.bloodlustMax) * (config.bloodlustDamageBonus - 1);

  // Charge: 1.0x at min, 2.0x at max
  const chargeMultiplier = config.minDamageMultiplier +
    (config.maxDamageMultiplier - config.minDamageMultiplier) * input.chargeLevel;

  // --- ABILITY BONUSES (additive percentage) ---
  let abilityBonusPercent = 0;
  const bonuses = {
    trophyScent: false,
    territorial: false,
    corpseHeat: false,
    sawtooth: false,
    melittin: false,
    histamine: false,
    armorCrack: false,
  };

  // Trophy Scent: +1% per unique enemy type
  if (input.trophyScentBonus > 0) {
    abilityBonusPercent += input.trophyScentBonus;
    bonuses.trophyScent = true;
  }

  // Territorial Mark: +10% in kill zones
  if (input.inTerritorialZone && input.territorialBonus > 0) {
    abilityBonusPercent += input.territorialBonus;
    bonuses.territorial = true;
  }

  // Corpse Heat: +5% near corpses
  if (input.nearCorpse && input.corpseHeatBonus > 0) {
    abilityBonusPercent += input.corpseHeatBonus;
    bonuses.corpseHeat = true;
  }

  // Sawtooth: +30% every 5th hit
  if (input.sawtoothTriggered && input.sawtoothBonus > 0) {
    abilityBonusPercent += input.sawtoothBonus;
    bonuses.sawtooth = true;
  }

  // Melittin Traces: +5% to poisoned enemies
  if (input.enemyIsPoisoned && input.poisonedDamageAmp > 0) {
    abilityBonusPercent += input.poisonedDamageAmp;
    bonuses.melittin = true;
  }

  // Histamine Burst: +8% to slowed enemies
  if (input.enemyIsSlowed && input.histamineDamageAmp > 0) {
    abilityBonusPercent += input.histamineDamageAmp;
    bonuses.histamine = true;
  }

  // --- ARMOR REDUCTION BONUS ---
  // Chitin Crack: Up to +50% bonus from armor reduction
  // Formula: bonus = (1 - reducedArmor/100) * 0.5
  // At 0 armor remaining: +50% bonus
  // At 50 armor remaining: +25% bonus
  let armorBonusPercent = 0;
  if (input.enemyArmorReduced > 0) {
    armorBonusPercent = input.enemyArmorReduced * 0.5; // 1% armor reduction = 0.5% damage bonus
    bonuses.armorCrack = true;
  }

  // --- FLAT BONUS ---
  const flatBonus = input.bumperDamageBonus;

  // --- FINAL CALCULATION ---
  // Formula: (base * bloodlust * charge * (1 + ability% + armor%)) + flat
  const totalMultiplier = 1 + (abilityBonusPercent + armorBonusPercent) / 100;
  const finalDamage = Math.floor(
    baseDamage * bloodlustMultiplier * chargeMultiplier * totalMultiplier + flatBonus
  );

  // --- DEBUG LOGGING ---
  if (debug) {
    console.log('[APEX DAMAGE CALC]', {
      base: baseDamage,
      bloodlust: `${input.bloodlust}/${config.bloodlustMax} → ${bloodlustMultiplier.toFixed(2)}x`,
      charge: `${(input.chargeLevel * 100).toFixed(0)}% → ${chargeMultiplier.toFixed(2)}x`,
      abilities: `+${abilityBonusPercent.toFixed(1)}%`,
      armor: `+${armorBonusPercent.toFixed(1)}%`,
      flat: flatBonus,
      final: finalDamage,
      bonuses,
    });
  }

  return {
    finalDamage,
    baseDamage,
    bloodlustMultiplier,
    chargeMultiplier,
    abilityBonusPercent,
    armorBonusPercent,
    flatBonus,
    bonuses,
  };
}

/**
 * Calculate PREVIEW damage for UI display during charge
 *
 * This shows the player what damage they'll deal WITHOUT enemy-specific bonuses.
 * Used for the charge UI indicator.
 *
 * @param state - Current apex state
 * @param trophyScentBonus - Current trophy scent bonus %
 * @param inTerritorialZone - Is player in a kill zone?
 * @param territorialBonus - Territorial zone bonus %
 * @param nearCorpse - Is player near a corpse?
 * @param corpseHeatBonus - Corpse heat bonus %
 * @param config - Apex strike config
 * @returns Preview damage and breakdown
 */
export function getApexDamagePreview(
  state: ApexStrikeState,
  trophyScentBonus: number = 0,
  inTerritorialZone: boolean = false,
  territorialBonus: number = 10,
  nearCorpse: boolean = false,
  corpseHeatBonus: number = 5,
  config: ApexStrikeConfig = APEX_CONFIG
): ApexDamageResult {
  return calculateApexStrikeDamage({
    bloodlust: state.bloodlust,
    chargeLevel: state.chargeLevel,
    trophyScentBonus,
    inTerritorialZone,
    territorialBonus,
    nearCorpse,
    corpseHeatBonus,
    // Enemy-specific bonuses unknown at preview time
    sawtoothTriggered: false,
    sawtoothBonus: 30,
    enemyIsPoisoned: false,
    poisonedDamageAmp: 5,
    enemyIsSlowed: false,
    histamineDamageAmp: 8,
    enemyArmorReduced: 0,
    bumperDamageBonus: 0,
  }, config, false);
}

/**
 * Get a human-readable damage range string for UI
 * Shows: "XX - YY dmg (+N% abilities)"
 *
 * @param preview - Preview damage result
 * @returns Formatted damage string
 */
export function formatDamagePreview(preview: ApexDamageResult): string {
  const minDamage = preview.finalDamage;
  // Max includes potential sawtooth (+30%) and enemy debuffs (+13%)
  const maxDamage = Math.floor(minDamage * 1.43);

  const bonusCount = Object.values(preview.bonuses).filter(Boolean).length;

  if (bonusCount > 0) {
    return `${minDamage}-${maxDamage} (+${preview.abilityBonusPercent.toFixed(0)}%)`;
  }
  return `${minDamage}-${maxDamage}`;
}

/**
 * Get active damage bonus names for UI tooltips
 *
 * @param preview - Preview damage result
 * @returns Array of active bonus names
 */
export function getActiveDamageBonuses(preview: ApexDamageResult): string[] {
  const names: string[] = [];

  if (preview.bonuses.trophyScent) names.push('Trophy Scent');
  if (preview.bonuses.territorial) names.push('Territorial Mark');
  if (preview.bonuses.corpseHeat) names.push('Corpse Heat');
  if (preview.bonuses.sawtooth) names.push('Sawtooth');
  if (preview.bonuses.melittin) names.push('Melittin Traces');
  if (preview.bonuses.histamine) names.push('Histamine Burst');
  if (preview.bonuses.armorCrack) names.push('Chitin Crack');

  return names;
}

// =============================================================================
// Exports
// =============================================================================

export default {
  // Config
  APEX_CONFIG,

  // State
  createInitialApexState,

  // Phase checks
  canApex,
  canChain,
  isVulnerable,
  isUnstoppable,
  isStriking,
  isLocking,
  isInGripMoment,

  // Phase transitions
  initiateLock,
  updateLockDirection,
  executeStrike,
  onStrikeHit,
  onStrikeMiss,
  attemptChain,

  // Hit detection
  checkStrikeHit,

  // Update
  updateApexStrike,
  getStrikeVelocity,
  getStumbleVelocity,
  getStumbleMomentumProgress,
  hasStumbleMomentum,

  // Progress getters
  getBloodlustPercent,
  getBloodlustDamageMultiplier,
  getCooldownProgress,
  getChainWindowProgress,
  getLockProgress,
  getStrikeProgress,

  // Visual helpers
  getBloodlustColor,
  getStrikeTrailPoints,
  getAimIndicatorEnd,
  getGhostOpacity,

  // Input helpers
  getAimFromInput,

  // Charge system (DD-038-2)
  updateCharge,
  getChargeScaledDistance,
  getChargeScaledDamage,
  getChargePercent,

  // Miss penalty system (DD-038-5)
  isInMissPenalty,
  getMissPenaltySpeedMult,
  getMissPenaltyDamageMult,
  canAttackDuringMissPenalty,
  updateMissPenalty,
  initiateMissPenalty,
  getTotalMissPenaltyDuration,
  getMissPenaltyProgress,

  // Damage calculation system (Run 050)
  calculateApexStrikeDamage,
  getApexDamagePreview,
  formatDamagePreview,
  getActiveDamageBonuses,
};
