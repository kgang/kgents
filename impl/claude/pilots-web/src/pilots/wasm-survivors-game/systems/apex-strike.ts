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
}

/**
 * Configuration for Apex Strike
 */
export interface ApexStrikeConfig {
  /** Duration of lock phase (ms) */
  lockDuration: number;

  /** Speed multiplier during strike (relative to base 200 px/s) */
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
  | { type: 'grip_moment'; enemyId: string; position: Vector2; timestamp: number };

/**
 * Result of checking for strike hit
 */
export interface StrikeHitResult {
  /** Updated state */
  state: ApexStrikeState;
  /** Enemy that was hit, if any */
  hitEnemy: Enemy | null;
  /** Damage dealt */
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

  // Strike phase - explosive thrust
  strikeSpeed: 12,              // 12x normal = 2400 px/s
  strikeDuration: 150,          // 0.15s max
  strikeDistance: 360,          // Max distance (~2400 * 0.15)

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
 * @returns Updated state and events
 */
export function initiateLock(
  state: ApexStrikeState,
  aimDirection: Vector2,
  playerPos: Vector2,
  timestamp: number
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

  // Calculate end position based on strike distance
  const endPos: Vector2 = {
    x: playerPos.x + direction.x * config.strikeDistance,
    y: playerPos.y + direction.y * config.strikeDistance,
  };

  const newState: ApexStrikeState = {
    ...state,
    phase: 'strike',
    lockDirection: direction,
    strikeStartPos: { ...playerPos },
    strikeEndPos: endPos,
    strikeDistanceRemaining: config.strikeDistance,
    phaseTimer: 0,
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

  // Calculate damage with bloodlust bonus
  const bloodlustMultiplier = 1 + (state.bloodlust / config.bloodlustMax) * (config.bloodlustDamageBonus - 1);
  const damage = Math.floor(config.strikeDamage * bloodlustMultiplier);

  // Add bloodlust
  const newBloodlust = Math.min(state.bloodlust + config.bloodlustGain, config.bloodlustMax);
  const hitMaxBloodlust = newBloodlust >= config.bloodlustMax && state.bloodlust < config.bloodlustMax;

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
 * Handle miss - transition to MISS_RECOVERY phase
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

  const newState: ApexStrikeState = {
    ...state,
    phase: 'miss_recovery',
    cooldownRemaining: config.baseCooldown,
    phaseTimer: 0,
    canChain: false,
    chainWindow: 0,
    // Reset chain stats
    chainDamageDealt: 0,
    chainHits: 0,
  };

  const events: ApexEvent[] = [
    ...chainEvents,
    { type: 'strike_miss', position: playerPos, timestamp },
    { type: 'cooldown_started', duration: config.baseCooldown, timestamp },
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
// Hit Detection
// =============================================================================

/**
 * Check for strike hit against enemies
 * @param state Current apex state
 * @param playerPos Current player position
 * @param enemies List of potential targets
 * @param timestamp Current game time
 * @param config Configuration
 * @returns Hit result with updated state
 */
export function checkStrikeHit(
  state: ApexStrikeState,
  playerPos: Vector2,
  enemies: ApexTarget[],
  timestamp: number,
  config: ApexStrikeConfig = APEX_CONFIG
): StrikeHitResult {
  if (state.phase !== 'strike') {
    return { state, hitEnemy: null, damage: 0, events: [] };
  }

  // Check collision with each enemy
  for (const enemy of enemies) {
    const dx = enemy.position.x - playerPos.x;
    const dy = enemy.position.y - playerPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const collisionDistance = config.playerRadius + enemy.radius;

    if (distance <= collisionDistance) {
      // HIT! Stop at enemy
      const hitResult = onStrikeHit(state, enemy, playerPos, timestamp, config);
      return {
        state: hitResult.state,
        hitEnemy: enemy as Enemy,
        damage: hitResult.damage,
        events: hitResult.events,
      };
    }
  }

  // No hit yet
  return { state, hitEnemy: null, damage: 0, events: [] };
}

// =============================================================================
// Per-Frame Update
// =============================================================================

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
  config: ApexStrikeConfig = APEX_CONFIG
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
      // Calculate movement this frame
      const strikeSpeed = BASE_PLAYER_SPEED * config.strikeSpeed;
      const moveDistance = (strikeSpeed * deltaTime) / 1000;

      // Update remaining distance
      newState.strikeDistanceRemaining = Math.max(
        0,
        newState.strikeDistanceRemaining - moveDistance
      );

      // Check if strike is complete (ran out of distance or time)
      const strikeComplete = newState.strikeDistanceRemaining <= 0 ||
        newState.phaseTimer >= config.strikeDuration;

      if (strikeComplete) {
        // Miss - didn't hit anything
        const missResult = onStrikeMiss(newState, playerPos, timestamp, config);
        newState = missResult.state;
        events.push(...missResult.events);
        return { state: newState, events, velocity: null };
      }

      // Calculate velocity for this frame
      const velocity = getStrikeVelocity(newState, config);
      return { state: newState, events, velocity };
    }

    case 'hit': {
      // Update chain window
      if (newState.chainWindow > 0) {
        newState.chainWindow = Math.max(0, newState.chainWindow - deltaTime);
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
        // No cooldown on successful hit!
      }
      return { state: newState, events, velocity: null };
    }

    case 'miss_recovery': {
      // Wait for recovery to complete
      if (newState.phaseTimer >= config.missRecovery) {
        newState.phase = 'ready';
      }
      return { state: newState, events, velocity: null };
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

  // Input helpers
  getAimFromInput,
};
