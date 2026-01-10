/**
 * WASM Survivors - Metamorphosis System (Run 030)
 *
 * Implements the metamorphosis mechanic:
 * - Enemies accumulate survival time
 * - At thresholds, they transition through pulsing → seeking → combining
 * - When seeking enemies collide, they form Colossals
 *
 * Design Decisions:
 * - DD-030-1: Survival timer per enemy (10s/15s/20s thresholds)
 * - DD-030-2: Four-state enemy lifecycle
 * - DD-030-3: Visual pulsing = unmistakable warning
 * - DD-030-4: THE TIDE as sole Colossal
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md §4 (Metamorphosis System)
 * @see pilots/wasm-survivors-game/runs/run-030/coordination/.outline.md
 */

import type { Enemy, PulsingState, Vector2 } from '../types';

// =============================================================================
// Configuration (DD-030-1)
// =============================================================================

export const METAMORPHOSIS_CONFIG = {
  /** Seconds until enemy starts pulsing */
  PULSE_THRESHOLD: 10,
  /** Seconds until enemy starts seeking other pulsing enemies */
  SEEK_THRESHOLD: 15,
  /** Seconds until enemy can combine with others */
  COMBINE_THRESHOLD: 20,
  /** Speed bonus when seeking (+25%) */
  SEEK_SPEED_BONUS: 0.25,
  /** Pixel radius for combination collision check */
  COMBINE_RADIUS: 40,
  /** Pixel radius for timer reset when pulsing enemy dies (M-3) */
  TIMER_RESET_RADIUS: 100,
} as const;

// THE TIDE configuration (DD-030-4)
export const TIDE_CONFIG = {
  radius: 36,           // 3x normal (12)
  health: 100,          // 5x normal (20)
  maxHealth: 100,
  speed: 30,            // 0.5x normal (60) - but immune to slow
  color: '#880000',     // Deep crimson
  xpValue: 300,         // Big reward (+50% XP boost)
  damage: 25,
  immuneToSlow: true,
} as const;

// =============================================================================
// Survival Time Management
// =============================================================================

/**
 * Update enemy's survival time by deltaTime
 * Pure function - returns new enemy with updated survivalTime
 */
export function updateSurvivalTime(enemy: Enemy, deltaTime: number): Enemy {
  const currentTime = enemy.survivalTime ?? 0;
  return {
    ...enemy,
    survivalTime: currentTime + deltaTime,
  };
}

/**
 * Calculate pulsing state based on survival time
 * Note: 'combining' state is set by checkCombineCollision, not by time alone
 */
export function calculatePulsingState(enemy: Enemy): PulsingState {
  // survivalTime and thresholds are both in seconds
  const survivalSeconds = enemy.survivalTime ?? 0;

  // Combining state is set externally when collision detected
  if (enemy.pulsingState === 'combining') {
    return 'combining';
  }

  if (survivalSeconds >= METAMORPHOSIS_CONFIG.SEEK_THRESHOLD) {
    return 'seeking';
  }

  if (survivalSeconds >= METAMORPHOSIS_CONFIG.PULSE_THRESHOLD) {
    return 'pulsing';
  }

  return 'normal';
}

/**
 * Update all enemies' pulsing states based on survival time
 */
export function updatePulsingStates(enemies: Enemy[]): Enemy[] {
  return enemies.map(enemy => ({
    ...enemy,
    pulsingState: calculatePulsingState(enemy),
  }));
}

// =============================================================================
// Seeking Behavior
// =============================================================================

/**
 * Find the nearest pulsing/seeking enemy to seek toward
 * Returns enemy ID or null if no valid target
 */
export function findSeekTarget(seeker: Enemy, allEnemies: Enemy[]): string | null {
  const validTargets = allEnemies.filter(enemy => {
    // Don't target self
    if (enemy.id === seeker.id) return false;
    // Only target pulsing or seeking enemies
    const state = enemy.pulsingState;
    return state === 'pulsing' || state === 'seeking';
  });

  if (validTargets.length === 0) return null;

  // Find nearest
  let nearestId: string | null = null;
  let nearestDist = Infinity;

  for (const target of validTargets) {
    const dx = target.position.x - seeker.position.x;
    const dy = target.position.y - seeker.position.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < nearestDist) {
      nearestDist = dist;
      nearestId = target.id;
    }
  }

  return nearestId;
}

/**
 * Calculate seeking velocity (direction toward target with speed bonus)
 */
export function getSeekingVelocity(
  seeker: Enemy,
  target: Enemy,
  baseSpeed: number
): Vector2 {
  const dx = target.position.x - seeker.position.x;
  const dy = target.position.y - seeker.position.y;
  const dist = Math.sqrt(dx * dx + dy * dy);

  if (dist === 0) return { x: 0, y: 0 };

  const speed = baseSpeed * (1 + METAMORPHOSIS_CONFIG.SEEK_SPEED_BONUS);
  return {
    x: (dx / dist) * speed,
    y: (dy / dist) * speed,
  };
}

// =============================================================================
// Combination Detection
// =============================================================================

/**
 * Check for collisions between seeking enemies that can combine
 * Returns arrays of enemies that should combine, or null if none
 */
export function checkCombineCollision(enemies: Enemy[]): Enemy[][] | null {
  // Filter to only seeking enemies that have reached COMBINE_THRESHOLD
  const eligibleEnemies = enemies.filter(enemy => {
    if (enemy.pulsingState !== 'seeking') return false;
    // survivalTime is already in seconds
    const survivalSeconds = enemy.survivalTime ?? 0;
    return survivalSeconds >= METAMORPHOSIS_CONFIG.COMBINE_THRESHOLD;
  });

  if (eligibleEnemies.length < 2) return null;

  const combinations: Enemy[][] = [];
  const usedIds = new Set<string>();

  // Find colliding pairs/groups
  for (let i = 0; i < eligibleEnemies.length; i++) {
    if (usedIds.has(eligibleEnemies[i].id)) continue;

    const group: Enemy[] = [eligibleEnemies[i]];
    usedIds.add(eligibleEnemies[i].id);

    for (let j = i + 1; j < eligibleEnemies.length; j++) {
      if (usedIds.has(eligibleEnemies[j].id)) continue;

      const e1 = eligibleEnemies[i];
      const e2 = eligibleEnemies[j];

      const dx = e2.position.x - e1.position.x;
      const dy = e2.position.y - e1.position.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const combinedRadius = e1.radius + e2.radius;

      // Check if within combine radius or actually colliding
      if (dist <= Math.max(combinedRadius, METAMORPHOSIS_CONFIG.COMBINE_RADIUS)) {
        group.push(e2);
        usedIds.add(e2.id);
      }
    }

    if (group.length >= 2) {
      combinations.push(group);
    }
  }

  return combinations.length > 0 ? combinations : null;
}

// =============================================================================
// Timer Reset (M-3: Interruptible)
// =============================================================================

/**
 * Reset survival timers for enemies near a killed pulsing enemy
 * Implements M-3: Killing ANY pulsing enemy resets nearby enemies' timers
 */
export function resetNearbyTimers(enemies: Enemy[], killedPosition: Vector2): Enemy[] {
  return enemies.map(enemy => {
    const dx = enemy.position.x - killedPosition.x;
    const dy = enemy.position.y - killedPosition.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist <= METAMORPHOSIS_CONFIG.TIMER_RESET_RADIUS) {
      return {
        ...enemy,
        survivalTime: 0,
        pulsingState: 'normal' as PulsingState,
        seekTarget: undefined,
      };
    }

    return enemy;
  });
}

// =============================================================================
// Colossal Creation (DD-030-4)
// =============================================================================

/**
 * Create THE TIDE Colossal from combining enemies
 * Spawns at centroid of the combining enemies
 */
export function createColossalTide(combiningEnemies: Enemy[]): Enemy {
  // Calculate centroid
  const centroidX = combiningEnemies.reduce((sum, e) => sum + e.position.x, 0) / combiningEnemies.length;
  const centroidY = combiningEnemies.reduce((sum, e) => sum + e.position.y, 0) / combiningEnemies.length;

  return {
    id: `colossal-tide-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    type: 'colossal_tide',
    position: { x: centroidX, y: centroidY },
    velocity: { x: 0, y: 0 },
    radius: TIDE_CONFIG.radius,
    health: TIDE_CONFIG.health,
    maxHealth: TIDE_CONFIG.maxHealth,
    damage: TIDE_CONFIG.damage,
    xpValue: TIDE_CONFIG.xpValue,
    color: TIDE_CONFIG.color,
    speed: 40, // Colossal is slow but inexorable
    coordinationState: 'idle',
    behaviorState: 'chase',
    stateStartTime: 0,
    survivalTime: 0,
    pulsingState: 'normal', // Colossals don't metamorphose further
  };
}

// =============================================================================
// Main Update Function
// =============================================================================

export interface MetamorphosisResult {
  enemies: Enemy[];
  colossals: Enemy[];
  metamorphosisTriggered: boolean;
  isFirstMetamorphosis: boolean;
}

/**
 * Update all metamorphosis-related state for the current frame
 */
export function updateMetamorphosis(
  enemies: Enemy[],
  deltaTime: number,
  hasWitnessedFirst: boolean
): MetamorphosisResult {
  // 1. Update survival times
  let updatedEnemies = enemies.map(enemy => {
    // Colossals don't accumulate survival time
    if (enemy.type === 'colossal_tide') return enemy;
    return updateSurvivalTime(enemy, deltaTime);
  });

  // 2. Update pulsing states
  updatedEnemies = updatePulsingStates(updatedEnemies);

  // 3. Update seek targets for seeking enemies
  updatedEnemies = updatedEnemies.map(enemy => {
    if (enemy.pulsingState === 'seeking') {
      const target = findSeekTarget(enemy, updatedEnemies);
      return { ...enemy, seekTarget: target ?? undefined };
    }
    return enemy;
  });

  // 4. Check for combinations
  const combinations = checkCombineCollision(updatedEnemies);
  const colossals: Enemy[] = [];
  let metamorphosisTriggered = false;

  if (combinations) {
    for (const group of combinations) {
      // Mark combining enemies for removal
      const combiningIds = new Set(group.map(e => e.id));
      updatedEnemies = updatedEnemies.filter(e => !combiningIds.has(e.id));

      // Create Colossal
      const colossal = createColossalTide(group);
      colossals.push(colossal);
      metamorphosisTriggered = true;
    }

    // Add new colossals to enemy list
    updatedEnemies = [...updatedEnemies, ...colossals];
  }

  return {
    enemies: updatedEnemies,
    colossals,
    metamorphosisTriggered,
    isFirstMetamorphosis: metamorphosisTriggered && !hasWitnessedFirst,
  };
}
