/**
 * WASM Survivors - Bumper-Rail Combo System (DD-039)
 *
 * Transforms bees into environmental elements during apex strike:
 * - BUMPER BEES: Pinball bumpers that give speed boost + redirect
 * - RAIL CHAINS: Consecutive hits form "grind rails" to surf through
 * - FLOW STATE: Extended chains unlock predator flow
 *
 * DESIGN PHILOSOPHY:
 * > "Bees are not obstacles. Bees are terrain."
 *
 * COUNTERPLAY (Critical for A1/A2):
 * - Charged bees damage player if hit again
 * - Guards break rail chains
 * - Propolis creates slow zones
 * - Formations lock out bumper effect
 *
 * @see pilots/wasm-survivors-game/runs/run-039/DD-039-BUMPER-RAIL.md
 */

import type { Vector2, Enemy } from '../types';

// =============================================================================
// Types
// =============================================================================

/**
 * Bumper state for individual bees
 */
export type BumperState = 'neutral' | 'bumpered' | 'charged' | 'recovering' | 'locked';

/**
 * Result of a bumper hit
 */
export interface BumperHitResult {
  /** Speed multiplier to apply (1.3 = 30% boost) */
  speedBoost: number;

  /** Direction nudge toward next target (normalized, 15° max) */
  directionNudge: Vector2;

  /** Additional chain window time (ms) */
  chainWindowExtension: number;

  /** Additional i-frames (ms) */
  iFramesExtension: number;

  /** Current combo count */
  comboCount: number;

  /** Whether this triggered a charged bee (damage to player) */
  hitChargedBee: boolean;

  /** Damage dealt to player if hit charged bee */
  chargedBeeDamage: number;

  /** Whether this should break the current chain */
  chainBroken: boolean;

  /** Reason chain was broken (for feedback) */
  chainBreakReason?: 'charged_bee' | 'guard' | 'formation' | 'propolis';
}

/**
 * Rail chain state - tracks consecutive hit combos
 */
export interface RailChainState {
  /** Whether rail chain is currently active */
  active: boolean;

  /** Number of consecutive hits */
  chainLength: number;

  /** IDs of bees hit in this chain (to prevent re-hitting) */
  hitBeeIds: Set<string>;

  /** Auto-targeted next bee (null if none in range) */
  railTarget: Enemy | null;

  /** Speed multiplier from chain (1.0 → 1.5 over 5 hits) */
  speedMultiplier: number;

  /** Damage bonus from chain (+10% per hit) */
  damageBonus: number;

  /** Time of last hit (for chain timeout) */
  lastHitTime: number;

  /** Position of last hit (for rail visual) */
  lastHitPosition: Vector2 | null;

  /** Positions of all hits in chain (for rail line visual) */
  hitPositions: Vector2[];
}

/**
 * Flow state - activated after 4+ consecutive hits
 */
export interface FlowState {
  /** Whether flow state is active */
  active: boolean;

  /** When flow state was activated (gameTime) */
  activatedAt: number;

  /** Current combo multiplier (1.0 → 2.0) */
  comboMultiplier: number;

  /** Whether i-frames are extended */
  iFramesExtended: boolean;

  /** Whether flow state can pierce formations */
  canPierceFormation: boolean;
}

// =============================================================================
// Constants
// =============================================================================

/**
 * Bumper system configuration
 */
export const BUMPER_CONFIG = {
  // Bumper hit effects
  SPEED_BOOST: 1.3,                 // 30% speed increase
  DIRECTION_NUDGE_DEGREES: 15,      // Max degrees toward next target
  CHAIN_WINDOW_EXTENSION: 150,      // +150ms chain window
  IFRAMES_EXTENSION: 50,            // +50ms invincibility
  TIME_DILATION: 0.7,               // 30% slowmo for 50ms on hit

  // Bumper state timings (ms)
  BUMPERED_DURATION: 100,           // Grace period after hit
  CHARGED_DURATION: 2000,           // Danger window
  RECOVERY_DURATION: 500,           // Cooldown before can be hit again

  // Charged bee damage
  CHARGED_BEE_DAMAGE: 15,           // Damage to player for hitting charged bee

  // Rail chain
  CHAIN_TIMEOUT: 1200,              // ms between hits before chain breaks (generous for combo building)
  RAIL_TARGET_RADIUS: 150,          // px radius to find next target
  RAIL_PREFER_ANGLE: 45,            // degrees from dash direction to prefer
  SPEED_MULTIPLIER_PER_HIT: 0.1,    // +10% speed per hit
  SPEED_MULTIPLIER_MAX: 1.5,        // Cap at 50% bonus
  DAMAGE_BONUS_PER_HIT: 0.1,        // +10% damage per hit

  // Flow state
  FLOW_THRESHOLD: 4,                // Hits needed to activate flow
  FLOW_COMBO_MULTIPLIER_MAX: 2.0,   // Max combo multiplier
  FLOW_FORMATION_PIERCE_THRESHOLD: 6, // Hits needed to pierce formations

  // Propolis slow zone
  PROPOLIS_SLOW_RADIUS: 80,         // px
  PROPOLIS_SLOW_FACTOR: 0.5,        // 50% speed in zone
  PROPOLIS_RAIL_SPEED_CAP: 1.0,     // Can't gain speed in zone

  // Elastic/Inelastic collision physics
  COLLISION_ELASTIC_RATIO: 0.7,     // 70% elastic (bounce), 30% inelastic (pass through)
  PLAYER_MASS: 20,                  // Player mass for collision calculation
  BEE_MASS_PER_RADIUS: 1.0,         // Bee mass = radius * this factor
} as const;

// =============================================================================
// State Factory
// =============================================================================

/**
 * Create initial rail chain state
 */
export function createInitialRailChainState(): RailChainState {
  return {
    active: false,
    chainLength: 0,
    hitBeeIds: new Set(),
    railTarget: null,
    speedMultiplier: 1.0,
    damageBonus: 0,
    lastHitTime: 0,
    lastHitPosition: null,
    hitPositions: [],
  };
}

/**
 * Create initial flow state
 */
export function createInitialFlowState(): FlowState {
  return {
    active: false,
    activatedAt: 0,
    comboMultiplier: 1.0,
    iFramesExtended: false,
    canPierceFormation: false,
  };
}

// =============================================================================
// Bumper State Management (Individual Bees)
// =============================================================================

/**
 * Get default bumper state for a bee (based on type and formation status)
 */
export function getDefaultBumperState(enemy: Enemy): BumperState {
  // Bees in formation can't be bumpered
  if (enemy.coordinationState === 'ball' || enemy.coordinationState === 'coordinating') {
    return 'locked';
  }

  // Guards are always locked (anti-rail)
  if (enemy.type === 'guard') {
    return 'locked';
  }

  return 'neutral';
}

/**
 * Check if bee can be bumpered (gives boost on hit)
 */
export function canBeBumpered(enemy: Enemy): boolean {
  const state = enemy.bumperState ?? getDefaultBumperState(enemy);
  return state === 'neutral';
}

/**
 * Check if hitting bee will damage player (charged bee)
 */
export function isChargedBee(enemy: Enemy): boolean {
  return enemy.bumperState === 'charged';
}

/**
 * Check if hitting bee will break chain (guard or formation)
 */
export function willBreakChain(enemy: Enemy): boolean {
  if (enemy.type === 'guard') return true;
  if (enemy.bumperState === 'locked') return true;
  if (enemy.bumperState === 'charged') return true;
  return false;
}

/**
 * Update bumper state for a bee (call each frame)
 */
export function updateBumperState(
  enemy: Enemy,
  deltaTime: number,
  gameTime: number
): Enemy {
  const currentState = enemy.bumperState ?? getDefaultBumperState(enemy);

  // Locked bees don't transition
  if (currentState === 'locked') {
    // Check if they should unlock (left formation)
    if (enemy.coordinationState !== 'ball' && enemy.coordinationState !== 'coordinating' && enemy.type !== 'guard') {
      return {
        ...enemy,
        bumperState: 'neutral',
        bumperStateTimer: 0,
      };
    }
    return enemy;
  }

  // Check for formation entry (should lock)
  if (enemy.coordinationState === 'ball' || enemy.coordinationState === 'coordinating') {
    return {
      ...enemy,
      bumperState: 'locked',
      bumperStateTimer: 0,
    };
  }

  // Guards are always locked (we already returned above if locked, so this is for guards
  // that somehow got a non-locked state)
  if (enemy.type === 'guard') {
    return {
      ...enemy,
      bumperState: 'locked',
      bumperStateTimer: 0,
    };
  }

  // Update timer-based transitions
  const timer = (enemy.bumperStateTimer ?? 0) - deltaTime;

  if (timer <= 0) {
    switch (currentState) {
      case 'bumpered':
        // Bumpered → Charged (danger!)
        return {
          ...enemy,
          bumperState: 'charged',
          bumperStateTimer: BUMPER_CONFIG.CHARGED_DURATION,
          bumperStateChangeTime: gameTime,
        };

      case 'charged':
        // Charged → Recovering
        return {
          ...enemy,
          bumperState: 'recovering',
          bumperStateTimer: BUMPER_CONFIG.RECOVERY_DURATION,
          bumperStateChangeTime: gameTime,
        };

      case 'recovering':
        // Recovering → Neutral
        return {
          ...enemy,
          bumperState: 'neutral',
          bumperStateTimer: 0,
          bumperStateChangeTime: gameTime,
        };

      default:
        return enemy;
    }
  }

  // Timer still running
  return {
    ...enemy,
    bumperStateTimer: timer,
  };
}

/**
 * Transition bee to bumpered state (after being hit)
 */
export function transitionToBumpered(enemy: Enemy, gameTime: number): Enemy {
  return {
    ...enemy,
    bumperState: 'bumpered',
    bumperStateTimer: BUMPER_CONFIG.BUMPERED_DURATION,
    bumperStateChangeTime: gameTime,
    hitDuringCurrentChain: true,
  };
}

// =============================================================================
// Elastic/Inelastic Collision Physics
// =============================================================================

/**
 * Calculate bumper collision direction using 70/30 elastic/inelastic physics.
 *
 * Elastic collision: Player bounces off bee like a pinball bumper.
 * Inelastic collision: Player passes through maintaining original direction.
 * The blend creates a satisfying "deflection" feel.
 *
 * Bee mass is proportional to radius - larger bees deflect more.
 *
 * @param playerPos Player position at collision
 * @param beePos Bee position at collision
 * @param beeRadius Bee radius (used as mass)
 * @param incomingDirection Normalized player dash direction
 * @returns Collision result with bounced direction and deflection amount
 */
export function calculateBumperCollision(
  playerPos: Vector2,
  beePos: Vector2,
  beeRadius: number,
  incomingDirection: Vector2
): { bouncedDirection: Vector2; deflectionAmount: number } {
  // Calculate collision normal (from player to bee center)
  const dx = beePos.x - playerPos.x;
  const dy = beePos.y - playerPos.y;
  const dist = Math.sqrt(dx * dx + dy * dy);

  // If positions overlap, use incoming direction as normal
  if (dist < 1) {
    return { bouncedDirection: incomingDirection, deflectionAmount: 0 };
  }

  // Collision normal (points from player toward bee)
  const normal: Vector2 = { x: dx / dist, y: dy / dist };

  // Calculate masses
  const playerMass = BUMPER_CONFIG.PLAYER_MASS;
  const beeMass = beeRadius * BUMPER_CONFIG.BEE_MASS_PER_RADIUS;

  // Velocity component along collision normal
  const vDotN = incomingDirection.x * normal.x + incomingDirection.y * normal.y;

  // If moving away from bee, no bounce
  if (vDotN <= 0) {
    return { bouncedDirection: incomingDirection, deflectionAmount: 0 };
  }

  // Elastic collision formula: v' = v - 2 * (m2 / (m1 + m2)) * (v · n) * n
  // For partial elasticity, we compute the fully elastic result then blend
  const massRatio = (2 * beeMass) / (playerMass + beeMass);
  const elasticFactor = massRatio * vDotN;

  // Fully elastic bounced direction
  const elasticDir: Vector2 = {
    x: incomingDirection.x - elasticFactor * normal.x,
    y: incomingDirection.y - elasticFactor * normal.y,
  };

  // Normalize elastic direction
  const elasticMag = Math.sqrt(elasticDir.x * elasticDir.x + elasticDir.y * elasticDir.y);
  const normalizedElastic: Vector2 = elasticMag > 0.001
    ? { x: elasticDir.x / elasticMag, y: elasticDir.y / elasticMag }
    : incomingDirection;

  // Blend: 70% elastic (bounce) + 30% inelastic (pass through)
  const elasticRatio = BUMPER_CONFIG.COLLISION_ELASTIC_RATIO;
  const inelasticRatio = 1 - elasticRatio;

  const blendedDir: Vector2 = {
    x: elasticRatio * normalizedElastic.x + inelasticRatio * incomingDirection.x,
    y: elasticRatio * normalizedElastic.y + inelasticRatio * incomingDirection.y,
  };

  // Normalize final direction
  const blendedMag = Math.sqrt(blendedDir.x * blendedDir.x + blendedDir.y * blendedDir.y);
  const finalDirection: Vector2 = blendedMag > 0.001
    ? { x: blendedDir.x / blendedMag, y: blendedDir.y / blendedMag }
    : incomingDirection;

  // Calculate deflection amount (how much direction changed, 0-1)
  const deflectionDot = incomingDirection.x * finalDirection.x + incomingDirection.y * finalDirection.y;
  const deflectionAmount = (1 - deflectionDot) / 2; // 0 = no change, 1 = 180° flip

  return { bouncedDirection: finalDirection, deflectionAmount };
}

// =============================================================================
// Rail Chain Management
// =============================================================================

/**
 * Process a bumper hit and update rail chain state
 */
export function processBumperHit(
  enemy: Enemy,
  railState: RailChainState,
  flowState: FlowState,
  playerPos: Vector2,
  dashDirection: Vector2,
  allEnemies: Enemy[],
  gameTime: number
): {
  result: BumperHitResult;
  newRailState: RailChainState;
  newFlowState: FlowState;
  updatedEnemy: Enemy;
} {
  const bumperState = enemy.bumperState ?? getDefaultBumperState(enemy);

  // === CHARGED BEE: Damage player, break chain ===
  if (bumperState === 'charged') {
    return {
      result: {
        speedBoost: 1.0, // No boost
        directionNudge: { x: 0, y: 0 },
        chainWindowExtension: 0,
        iFramesExtension: 0,
        comboCount: 0,
        hitChargedBee: true,
        chargedBeeDamage: BUMPER_CONFIG.CHARGED_BEE_DAMAGE,
        chainBroken: true,
        chainBreakReason: 'charged_bee',
      },
      newRailState: createInitialRailChainState(),
      newFlowState: createInitialFlowState(),
      updatedEnemy: enemy,
    };
  }

  // === LOCKED BEE (Guard or Formation): Break chain, no boost ===
  if (bumperState === 'locked') {
    const breakReason = enemy.type === 'guard' ? 'guard' : 'formation';
    return {
      result: {
        speedBoost: 1.0,
        directionNudge: { x: 0, y: 0 },
        chainWindowExtension: 0,
        iFramesExtension: 0,
        comboCount: 0,
        hitChargedBee: false,
        chargedBeeDamage: 0,
        chainBroken: true,
        chainBreakReason: breakReason,
      },
      newRailState: createInitialRailChainState(),
      newFlowState: createInitialFlowState(),
      updatedEnemy: enemy,
    };
  }

  // === Already hit in this chain ===
  if (railState.hitBeeIds.has(enemy.id)) {
    // No bonus, but don't break chain
    return {
      result: {
        speedBoost: 1.0,
        directionNudge: { x: 0, y: 0 },
        chainWindowExtension: 0,
        iFramesExtension: 0,
        comboCount: railState.chainLength,
        hitChargedBee: false,
        chargedBeeDamage: 0,
        chainBroken: false,
      },
      newRailState: railState,
      newFlowState: flowState,
      updatedEnemy: enemy,
    };
  }

  // === NEUTRAL BEE: Give bumper boost! ===

  // Update chain state
  const newChainLength = railState.chainLength + 1;
  const newHitBeeIds = new Set(railState.hitBeeIds);
  newHitBeeIds.add(enemy.id);

  // Calculate new speed multiplier (+10% per hit, cap at 1.5x)
  const newSpeedMultiplier = Math.min(
    1.0 + newChainLength * BUMPER_CONFIG.SPEED_MULTIPLIER_PER_HIT,
    BUMPER_CONFIG.SPEED_MULTIPLIER_MAX
  );

  // Calculate damage bonus
  const newDamageBonus = newChainLength * BUMPER_CONFIG.DAMAGE_BONUS_PER_HIT;

  // === ELASTIC/INELASTIC COLLISION PHYSICS ===
  // Calculate bounced direction based on 70/30 elastic/inelastic collision
  // Bee mass is proportional to radius - larger bees deflect more
  const beeRadius = enemy.radius ?? 15;
  const collision = calculateBumperCollision(
    playerPos,
    enemy.position,
    beeRadius,
    dashDirection
  );

  // Find next target for rail auto-aim
  const nextTarget = findRailTarget(
    enemy.position,
    collision.bouncedDirection, // Use bounced direction to find targets in new path
    allEnemies,
    newHitBeeIds,
    flowState.canPierceFormation
  );

  // Calculate direction nudge: collision bounce + rail targeting
  // Start with the collision-bounced direction as the base
  // Then nudge toward next target if one exists
  let directionNudge: Vector2;
  if (nextTarget) {
    // Blend bounced direction with targeting nudge
    const targetNudge = calculateDirectionNudge(
      collision.bouncedDirection,
      enemy.position,
      nextTarget.position
    );
    // Final nudge is mostly collision physics with some target pull
    // Higher deflection = more physics, lower = more targeting
    const physicsWeight = 0.6 + collision.deflectionAmount * 0.3; // 60-90% physics
    const targetWeight = 1 - physicsWeight;
    directionNudge = {
      x: physicsWeight * (collision.bouncedDirection.x - dashDirection.x) + targetWeight * targetNudge.x,
      y: physicsWeight * (collision.bouncedDirection.y - dashDirection.y) + targetWeight * targetNudge.y,
    };
  } else {
    // No next target - pure collision physics
    directionNudge = {
      x: collision.bouncedDirection.x - dashDirection.x,
      y: collision.bouncedDirection.y - dashDirection.y,
    };
  }

  // Update hit positions for rail visual
  const newHitPositions = [...railState.hitPositions, { ...enemy.position }];

  // Build new rail state
  const newRailState: RailChainState = {
    active: newChainLength >= 2,
    chainLength: newChainLength,
    hitBeeIds: newHitBeeIds,
    railTarget: nextTarget,
    speedMultiplier: newSpeedMultiplier,
    damageBonus: newDamageBonus,
    lastHitTime: gameTime,
    lastHitPosition: { ...enemy.position },
    hitPositions: newHitPositions,
  };

  // Check for flow state activation (4+ hits)
  let newFlowState = flowState;
  if (newChainLength >= BUMPER_CONFIG.FLOW_THRESHOLD && !flowState.active) {
    newFlowState = {
      active: true,
      activatedAt: gameTime,
      comboMultiplier: Math.min(1.0 + (newChainLength - 3) * 0.2, BUMPER_CONFIG.FLOW_COMBO_MULTIPLIER_MAX),
      iFramesExtended: true,
      canPierceFormation: newChainLength >= BUMPER_CONFIG.FLOW_FORMATION_PIERCE_THRESHOLD,
    };
  } else if (flowState.active) {
    // Update flow state
    newFlowState = {
      ...flowState,
      comboMultiplier: Math.min(1.0 + (newChainLength - 3) * 0.2, BUMPER_CONFIG.FLOW_COMBO_MULTIPLIER_MAX),
      canPierceFormation: newChainLength >= BUMPER_CONFIG.FLOW_FORMATION_PIERCE_THRESHOLD,
    };
  }

  // Transition enemy to bumpered state
  const updatedEnemy = transitionToBumpered(enemy, gameTime);

  return {
    result: {
      speedBoost: BUMPER_CONFIG.SPEED_BOOST,
      directionNudge,
      chainWindowExtension: BUMPER_CONFIG.CHAIN_WINDOW_EXTENSION,
      iFramesExtension: BUMPER_CONFIG.IFRAMES_EXTENSION,
      comboCount: newChainLength,
      hitChargedBee: false,
      chargedBeeDamage: 0,
      chainBroken: false,
    },
    newRailState,
    newFlowState,
    updatedEnemy,
  };
}

/**
 * Find next target for rail auto-aim
 */
export function findRailTarget(
  fromPos: Vector2,
  dashDirection: Vector2,
  allEnemies: Enemy[],
  excludeIds: Set<string>,
  canPierceFormation: boolean = false
): Enemy | null {
  let bestTarget: Enemy | null = null;
  let bestScore = -Infinity;

  for (const enemy of allEnemies) {
    // Skip already-hit enemies
    if (excludeIds.has(enemy.id)) continue;

    // Skip charged bees
    if (enemy.bumperState === 'charged') continue;

    // Skip formation bees unless flow can pierce
    if (enemy.bumperState === 'locked' && !canPierceFormation) continue;

    // Skip guards (they break chains)
    if (enemy.type === 'guard') continue;

    // Calculate distance
    const dx = enemy.position.x - fromPos.x;
    const dy = enemy.position.y - fromPos.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Skip if out of range
    if (distance > BUMPER_CONFIG.RAIL_TARGET_RADIUS) continue;
    if (distance < 1) continue; // Too close (probably current bee)

    // Calculate angle from dash direction
    const toTargetDir = { x: dx / distance, y: dy / distance };
    const dot = dashDirection.x * toTargetDir.x + dashDirection.y * toTargetDir.y;
    const angleDeg = Math.acos(Math.min(1, Math.max(-1, dot))) * (180 / Math.PI);

    // Skip if too far off-angle
    if (angleDeg > BUMPER_CONFIG.RAIL_PREFER_ANGLE * 2) continue;

    // Score: prefer closer + more aligned
    // Score = (1 - distance/maxDist) + (1 - angle/maxAngle)
    const distanceScore = 1 - distance / BUMPER_CONFIG.RAIL_TARGET_RADIUS;
    const angleScore = 1 - angleDeg / (BUMPER_CONFIG.RAIL_PREFER_ANGLE * 2);
    const score = distanceScore + angleScore * 1.5; // Weight angle slightly more

    if (score > bestScore) {
      bestScore = score;
      bestTarget = enemy;
    }
  }

  return bestTarget;
}

/**
 * Calculate direction nudge toward next target (max 15 degrees)
 */
function calculateDirectionNudge(
  currentDir: Vector2,
  fromPos: Vector2,
  targetPos: Vector2
): Vector2 {
  // Direction to target
  const dx = targetPos.x - fromPos.x;
  const dy = targetPos.y - fromPos.y;
  const dist = Math.sqrt(dx * dx + dy * dy);
  if (dist < 1) return { x: 0, y: 0 };

  const toTargetDir = { x: dx / dist, y: dy / dist };

  // Calculate angle between current and target direction
  const dot = currentDir.x * toTargetDir.x + currentDir.y * toTargetDir.y;
  const cross = currentDir.x * toTargetDir.y - currentDir.y * toTargetDir.x;
  const angleDeg = Math.acos(Math.min(1, Math.max(-1, dot))) * (180 / Math.PI);

  // If already aligned, no nudge needed
  if (angleDeg < 1) return { x: 0, y: 0 };

  // Cap nudge at max degrees
  const maxNudgeDeg = BUMPER_CONFIG.DIRECTION_NUDGE_DEGREES;
  const nudgeDeg = Math.min(angleDeg, maxNudgeDeg);
  const nudgeRad = nudgeDeg * (Math.PI / 180);

  // Determine rotation direction
  const rotationSign = cross >= 0 ? 1 : -1;

  // Rotate current direction
  const cos = Math.cos(nudgeRad * rotationSign);
  const sin = Math.sin(nudgeRad * rotationSign);

  return {
    x: currentDir.x * cos - currentDir.y * sin - currentDir.x,
    y: currentDir.x * sin + currentDir.y * cos - currentDir.y,
  };
}

/**
 * Check if chain has timed out
 */
export function hasChainTimedOut(railState: RailChainState, gameTime: number): boolean {
  if (!railState.active) return false;
  return gameTime - railState.lastHitTime > BUMPER_CONFIG.CHAIN_TIMEOUT;
}

/**
 * Reset chain state (on timeout or break)
 */
export function resetChainState(): RailChainState {
  return createInitialRailChainState();
}

/**
 * Reset flow state
 */
export function resetFlowState(): FlowState {
  return createInitialFlowState();
}

// =============================================================================
// Propolis Slow Zone
// =============================================================================

/**
 * Check if position is in a propolis slow zone
 */
export function isInPropolisSlowZone(
  pos: Vector2,
  enemies: Enemy[]
): { inZone: boolean; slowFactor: number } {
  for (const enemy of enemies) {
    if (enemy.type !== 'propolis') continue;

    const dx = pos.x - enemy.position.x;
    const dy = pos.y - enemy.position.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance < BUMPER_CONFIG.PROPOLIS_SLOW_RADIUS) {
      return {
        inZone: true,
        slowFactor: BUMPER_CONFIG.PROPOLIS_SLOW_FACTOR,
      };
    }
  }

  return { inZone: false, slowFactor: 1.0 };
}

/**
 * Apply propolis slow to rail speed multiplier
 */
export function applyPropolisSlow(
  railState: RailChainState,
  inSlowZone: boolean
): RailChainState {
  if (!inSlowZone) return railState;

  return {
    ...railState,
    speedMultiplier: Math.min(railState.speedMultiplier, BUMPER_CONFIG.PROPOLIS_RAIL_SPEED_CAP),
  };
}

// =============================================================================
// Visual Helpers
// =============================================================================

/**
 * Get bumper visual state for rendering
 */
export function getBumperVisualState(enemy: Enemy, gameTime: number): {
  color: string;
  pulseIntensity: number;
  glowRadius: number;
  isWarning: boolean;
} {
  const state = enemy.bumperState ?? 'neutral';
  // Timer values available for future animation enhancements
  const _timer = enemy.bumperStateTimer ?? 0;
  const _changeTime = enemy.bumperStateChangeTime ?? 0;
  void _timer; void _changeTime;  // Suppress unused warnings

  switch (state) {
    case 'neutral':
      // Gold pulse when ready
      const pulse = Math.sin(gameTime * 0.005) * 0.5 + 0.5;
      return {
        color: '#FFD700',
        pulseIntensity: pulse,
        glowRadius: 4 + pulse * 4,
        isWarning: false,
      };

    case 'bumpered':
      // Bright flash
      return {
        color: '#FFFFFF',
        pulseIntensity: 1.0,
        glowRadius: 12,
        isWarning: false,
      };

    case 'charged':
      // Red pulsing danger
      const dangerPulse = Math.sin(gameTime * 0.01) * 0.5 + 0.5;
      return {
        color: '#FF4444',
        pulseIntensity: 0.5 + dangerPulse * 0.5,
        glowRadius: 6 + dangerPulse * 6,
        isWarning: true,
      };

    case 'recovering':
      // Dim recovery
      return {
        color: '#888888',
        pulseIntensity: 0.3,
        glowRadius: 2,
        isWarning: false,
      };

    case 'locked':
      // No visual (locked)
      return {
        color: 'transparent',
        pulseIntensity: 0,
        glowRadius: 0,
        isWarning: false,
      };

    default:
      return {
        color: 'transparent',
        pulseIntensity: 0,
        glowRadius: 0,
        isWarning: false,
      };
  }
}

/**
 * Get rail line points for rendering
 */
export function getRailLinePoints(railState: RailChainState): Vector2[] {
  if (!railState.active || railState.hitPositions.length < 2) {
    return [];
  }
  return railState.hitPositions;
}

/**
 * Get flow state visual intensity (0-1)
 */
export function getFlowIntensity(flowState: FlowState, gameTime: number): number {
  if (!flowState.active) return 0;

  // Pulse effect
  const timeSinceActivation = gameTime - flowState.activatedAt;
  const pulse = Math.sin(timeSinceActivation * 0.008) * 0.3 + 0.7;

  return pulse;
}

// =============================================================================
// Exports
// =============================================================================

export default {
  // Config
  BUMPER_CONFIG,

  // State creation
  createInitialRailChainState,
  createInitialFlowState,

  // Bumper state management
  getDefaultBumperState,
  canBeBumpered,
  isChargedBee,
  willBreakChain,
  updateBumperState,
  transitionToBumpered,

  // Rail chain
  processBumperHit,
  findRailTarget,
  hasChainTimedOut,
  resetChainState,
  resetFlowState,

  // Propolis
  isInPropolisSlowZone,
  applyPropolisSlow,

  // Visual
  getBumperVisualState,
  getRailLinePoints,
  getFlowIntensity,
};
