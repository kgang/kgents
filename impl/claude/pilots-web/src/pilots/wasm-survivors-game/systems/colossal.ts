/**
 * WASM Survivors - Colossal System (Run 030)
 *
 * Implements THE TIDE Colossal behavior:
 * - Inexorable Advance: 0.5x speed but CANNOT be slowed
 * - Absorption: Heals when nearby enemies die
 * - Fission: At 25% HP, splits into 5 shamblers
 * - Gravity Well: Nearby enemies accelerate toward player
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md §5 (The Five Colossals)
 * @see pilots/wasm-survivors-game/runs/run-030/coordination/.outline.md
 */

import type { Enemy, Vector2, Player } from '../types';
// Re-export TIDE_CONFIG for physics and rendering use
export { TIDE_CONFIG } from './metamorphosis';

// =============================================================================
// Types
// =============================================================================

export type ColossalMoveState = 'advancing' | 'absorbing' | 'fissioning' | 'gravity_well';

export interface ColossalState {
  moveState: ColossalMoveState;
  lastAbsorptionTime: number;
  gravityWellLastActivation: number;
  gravityWellEverActivated: boolean;
  hasFissioned: boolean;
}

export interface ColossalUpdate {
  colossal: Enemy;
  colossalState: ColossalState;
  fissionedEnemies: Enemy[];
  absorbedEnemyIds: string[];
}

// =============================================================================
// Configuration
// =============================================================================

export const COLOSSAL_CONFIG = {
  // Inexorable Advance
  ADVANCE_SPEED: 30,           // 0.5x normal enemy speed (60)
  IMMUNE_TO_SLOW: true,

  // Absorption
  ABSORPTION_RADIUS: 80,       // Pixel radius to detect dying enemies
  ABSORPTION_HEAL: 20,         // HP healed per absorbed enemy
  ABSORPTION_COOLDOWN: 500,    // ms between absorptions

  // Fission
  FISSION_THRESHOLD: 0.25,     // 25% HP triggers fission
  FISSION_SHAMBLER_COUNT: 5,

  // Gravity Well
  GRAVITY_RADIUS: 120,         // Pixel radius of gravity effect
  GRAVITY_ACCELERATION: 1.5,   // Multiplier on enemy speed toward player
  GRAVITY_COOLDOWN: 3000,      // ms between gravity activations
  GRAVITY_DURATION: 2000,      // ms gravity well is active

  // Fissioned shambler stats
  SHAMBLER_HEALTH: 20,
  SHAMBLER_RADIUS: 12,
  SHAMBLER_DAMAGE: 10,
  SHAMBLER_XP: 10,
} as const;

// =============================================================================
// State Management
// =============================================================================

const colossalStates = new Map<string, ColossalState>();

/**
 * Get or create colossal state for an enemy
 */
export function getColossalState(colossalId: string): ColossalState {
  if (!colossalStates.has(colossalId)) {
    colossalStates.set(colossalId, {
      moveState: 'advancing',
      lastAbsorptionTime: 0,
      gravityWellLastActivation: 0,
      gravityWellEverActivated: false,
      hasFissioned: false,
    });
  }
  return colossalStates.get(colossalId)!;
}

/**
 * Clear colossal state (when colossal dies)
 */
export function clearColossalState(colossalId: string): void {
  colossalStates.delete(colossalId);
}

// =============================================================================
// Movement: Inexorable Advance
// =============================================================================

/**
 * Calculate movement for THE TIDE
 * Always moves toward player at 0.5x speed, immune to slow effects
 */
export function getColossalMovement(
  colossal: Enemy,
  playerPos: Vector2,
  _slowPercent: number // Ignored - immune to slow
): Vector2 {
  const dx = playerPos.x - colossal.position.x;
  const dy = playerPos.y - colossal.position.y;
  const dist = Math.sqrt(dx * dx + dy * dy);

  if (dist === 0) return { x: 0, y: 0 };

  // Inexorable Advance: constant speed, no slow allowed
  return {
    x: (dx / dist) * COLOSSAL_CONFIG.ADVANCE_SPEED,
    y: (dy / dist) * COLOSSAL_CONFIG.ADVANCE_SPEED,
  };
}

// =============================================================================
// Absorption
// =============================================================================

/**
 * Check for nearby dying enemies to absorb and heal
 * Called when an enemy dies - returns heal amount if within absorption radius
 */
export function checkAbsorption(
  colossal: Enemy,
  deadEnemyPos: Vector2,
  gameTime: number
): { shouldHeal: boolean; healAmount: number } {
  const state = getColossalState(colossal.id);

  // Check cooldown
  if (gameTime - state.lastAbsorptionTime < COLOSSAL_CONFIG.ABSORPTION_COOLDOWN) {
    return { shouldHeal: false, healAmount: 0 };
  }

  // Check distance
  const dx = deadEnemyPos.x - colossal.position.x;
  const dy = deadEnemyPos.y - colossal.position.y;
  const dist = Math.sqrt(dx * dx + dy * dy);

  if (dist <= COLOSSAL_CONFIG.ABSORPTION_RADIUS) {
    state.lastAbsorptionTime = gameTime;
    state.moveState = 'absorbing';
    return { shouldHeal: true, healAmount: COLOSSAL_CONFIG.ABSORPTION_HEAL };
  }

  return { shouldHeal: false, healAmount: 0 };
}

/**
 * Apply absorption healing to colossal
 */
export function applyAbsorption(colossal: Enemy, healAmount: number): Enemy {
  return {
    ...colossal,
    health: Math.min(colossal.health + healAmount, colossal.maxHealth),
  };
}

// =============================================================================
// Fission
// =============================================================================

/**
 * Check if colossal should fission (at 25% HP)
 */
export function shouldFission(colossal: Enemy): boolean {
  const state = getColossalState(colossal.id);
  if (state.hasFissioned) return false;

  const healthPercent = colossal.health / colossal.maxHealth;
  return healthPercent <= COLOSSAL_CONFIG.FISSION_THRESHOLD;
}

/**
 * Perform fission - spawn 5 shamblers and mark colossal as fissioned
 * Returns the spawned shamblers (colossal should be removed from game)
 */
export function performFission(colossal: Enemy, wave: number): Enemy[] {
  const state = getColossalState(colossal.id);
  state.hasFissioned = true;
  state.moveState = 'fissioning';

  const shamblers: Enemy[] = [];
  const angleStep = (2 * Math.PI) / COLOSSAL_CONFIG.FISSION_SHAMBLER_COUNT;

  // Scale stats with wave
  const healthMultiplier = 1 + wave * 0.1;

  for (let i = 0; i < COLOSSAL_CONFIG.FISSION_SHAMBLER_COUNT; i++) {
    const angle = i * angleStep;
    const spawnDist = colossal.radius + 20; // Spawn just outside colossal radius

    const shambler: Enemy = {
      id: `shambler-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      type: 'basic',
      position: {
        x: colossal.position.x + Math.cos(angle) * spawnDist,
        y: colossal.position.y + Math.sin(angle) * spawnDist,
      },
      velocity: { x: 0, y: 0 },
      radius: COLOSSAL_CONFIG.SHAMBLER_RADIUS,
      health: Math.floor(COLOSSAL_CONFIG.SHAMBLER_HEALTH * healthMultiplier),
      maxHealth: Math.floor(COLOSSAL_CONFIG.SHAMBLER_HEALTH * healthMultiplier),
      damage: COLOSSAL_CONFIG.SHAMBLER_DAMAGE,
      xpValue: COLOSSAL_CONFIG.SHAMBLER_XP,
      color: '#FF3366',
      speed: 80, // Shambler speed
      coordinationState: 'idle',
      behaviorState: 'chase',
      stateStartTime: 0,
      survivalTime: 0,
      pulsingState: 'normal',
    };

    shamblers.push(shambler);
  }

  // Clear colossal state since it's dying
  clearColossalState(colossal.id);

  return shamblers;
}

// =============================================================================
// Gravity Well
// =============================================================================

/**
 * Check if gravity well should activate
 */
export function shouldActivateGravityWell(colossalId: string, gameTime: number): boolean {
  const state = getColossalState(colossalId);
  // First activation is always allowed
  if (!state.gravityWellEverActivated) return true;
  // For subsequent activations, check if enough time has passed
  return gameTime - state.gravityWellLastActivation >= COLOSSAL_CONFIG.GRAVITY_COOLDOWN;
}

/**
 * Activate gravity well for a colossal
 */
export function activateGravityWell(colossalId: string, gameTime: number): void {
  const state = getColossalState(colossalId);
  state.gravityWellLastActivation = gameTime;
  state.gravityWellEverActivated = true;
  state.moveState = 'gravity_well';
}

/**
 * Apply gravity well effect to nearby enemies
 * Makes them accelerate toward the player
 */
export function applyGravityWell(
  enemies: Enemy[],
  colossalPos: Vector2,
  playerPos: Vector2
): Enemy[] {
  return enemies.map((enemy: Enemy) => {
    // Don't affect the colossal itself or other colossals
    if (enemy.type === 'colossal_tide') return enemy;

    // Check if within gravity radius
    const dx = enemy.position.x - colossalPos.x;
    const dy = enemy.position.y - colossalPos.y;
    const distToColossal = Math.sqrt(dx * dx + dy * dy);

    if (distToColossal > COLOSSAL_CONFIG.GRAVITY_RADIUS) return enemy;

    // Accelerate toward player
    const pdx = playerPos.x - enemy.position.x;
    const pdy = playerPos.y - enemy.position.y;
    const pdist = Math.sqrt(pdx * pdx + pdy * pdy);

    if (pdist === 0) return enemy;

    // Apply acceleration
    const accel = COLOSSAL_CONFIG.GRAVITY_ACCELERATION;
    return {
      ...enemy,
      velocity: {
        x: enemy.velocity.x + (pdx / pdist) * accel,
        y: enemy.velocity.y + (pdy / pdist) * accel,
      },
      isLinked: true, // Mark as linked for visual effect
    };
  });
}

// =============================================================================
// Main Update Function
// =============================================================================

/**
 * Update all colossal behavior for the current frame
 */
export function updateColossalBehavior(
  colossal: Enemy,
  _enemies: Enemy[],  // Reserved for future absorption logic
  player: Player,
  gameTime: number,
  deltaTime: number
): ColossalUpdate {
  const state = getColossalState(colossal.id);
  let updatedColossal = { ...colossal };
  let fissionedEnemies: Enemy[] = [];
  const absorbedEnemyIds: string[] = [];

  // Reset move state to advancing (default)
  state.moveState = 'advancing';

  // 1. Check for fission
  if (shouldFission(updatedColossal)) {
    fissionedEnemies = performFission(updatedColossal, 1); // TODO: pass actual wave
    // Colossal is destroyed - return empty update
    return {
      colossal: { ...updatedColossal, health: 0 }, // Mark for removal
      colossalState: state,
      fissionedEnemies,
      absorbedEnemyIds,
    };
  }

  // 2. Check for gravity well activation (periodic)
  if (shouldActivateGravityWell(colossal.id, gameTime)) {
    activateGravityWell(colossal.id, gameTime);
  }

  // 3. Update movement (Inexorable Advance)
  const movement = getColossalMovement(updatedColossal, player.position, 0);
  updatedColossal = {
    ...updatedColossal,
    position: {
      x: updatedColossal.position.x + movement.x * (deltaTime / 1000),
      y: updatedColossal.position.y + movement.y * (deltaTime / 1000),
    },
    velocity: movement,
  };

  return {
    colossal: updatedColossal,
    colossalState: state,
    fissionedEnemies,
    absorbedEnemyIds,
  };
}

/**
 * Check if an enemy is a colossal
 */
export function isColossal(enemy: Enemy): boolean {
  return enemy.type === 'colossal_tide';
}

/**
 * Get all colossals from enemy list
 */
export function getColossals(enemies: Enemy[]): Enemy[] {
  return enemies.filter(isColossal);
}
