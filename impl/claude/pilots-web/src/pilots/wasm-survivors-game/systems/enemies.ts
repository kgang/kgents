/**
 * Hornet Siege - Bee Behavior System
 *
 * Per PROTO_SPEC S6: Each bee type has signature behavior patterns.
 *
 * Bee Types (per spec):
 * - Worker: Swarms toward player (basic kiting)
 * - Scout: Fast, alerts others via pheromones
 * - Guard: Slow, high HP, blocks player
 * - Propolis: Ranged sticky attacks, slows player
 * - Royal: Elite patterns, THE BALL anchor
 *
 * State Machine: CHASE → TELEGRAPH → ATTACK → RECOVERY
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import type { Enemy, EnemyType, Vector2 } from '../types';

// =============================================================================
// Bee Behavior Configuration (Per PROTO_SPEC S6)
// =============================================================================

export interface BeeBehaviorConfig {
  attackRange: number;           // Distance to trigger attack
  telegraphDuration: number;     // Warning time (ms)
  attackDuration: number;        // Commit time (ms)
  recoveryDuration: number;      // Vulnerable time (ms)
  attackType: 'swarm' | 'sting' | 'block' | 'sticky' | 'combo';
  attackDamage: number;
  attackParams: {
    distance?: number;           // For sting/swarm
    radius?: number;             // For block/sticky
    speedMultiplier?: number;    // Speed during attack
    projectileSpeed?: number;    // For sticky projectile
    slowDuration?: number;       // Propolis slow effect
  };
  colors: {
    telegraph: string;
    attack: string;
  };
  // Bee-specific coordination behavior
  pheromoneEmission: number;     // How much this bee contributes to coordination
  coordinationRole: 'swarm' | 'alert' | 'anchor' | 'ranged' | 'elite';
}

// Bee behavior state machine
export type BeeBehaviorState = 'chase' | 'telegraph' | 'attack' | 'recovery';

// Per PROTO_SPEC S6: Bee Taxonomy
export const BEE_BEHAVIORS: Record<EnemyType, BeeBehaviorConfig> = {
  worker: {
    // Swarm behavior: Quick attacks, low damage, numbers game
    attackRange: 25,
    telegraphDuration: 400,      // Run 036: Increased from 200ms for readable counterplay
    attackDuration: 100,
    recoveryDuration: 400,
    attackType: 'swarm',
    attackDamage: 8,
    attackParams: {
      distance: 40,
      speedMultiplier: 1.5,
    },
    colors: {
      telegraph: '#F4D03F',      // Yellow warning
      attack: '#E67E22',         // Orange impact
    },
    pheromoneEmission: 0.1,
    coordinationRole: 'swarm',
  },

  scout: {
    // Alert behavior: Fast movement, triggers alarm pheromones
    attackRange: 60,             // Prefers to stay back
    telegraphDuration: 300,      // Run 036: Increased from 150ms for readable counterplay
    attackDuration: 80,
    recoveryDuration: 600,
    attackType: 'sting',
    attackDamage: 5,
    attackParams: {
      distance: 80,
      speedMultiplier: 2.0,      // Very fast
    },
    colors: {
      telegraph: '#F39C12',      // Orange warning
      attack: '#FF6B00',         // Bright orange
    },
    pheromoneEmission: 0.3,      // High coordination contribution
    coordinationRole: 'alert',
  },

  guard: {
    // Block behavior: Slow, stands ground, high HP
    attackRange: 40,
    telegraphDuration: 500,      // Slow but powerful
    attackDuration: 300,
    recoveryDuration: 800,
    attackType: 'block',
    attackDamage: 15,
    attackParams: {
      radius: 50,                // Area blocking
    },
    colors: {
      telegraph: '#E74C3C',      // Red warning
      attack: '#C0392B',         // Dark red
    },
    pheromoneEmission: 0.2,
    coordinationRole: 'anchor',
  },

  propolis: {
    // Sticky behavior: Ranged, slows player
    attackRange: 120,            // Prefers distance
    telegraphDuration: 400,
    attackDuration: 100,
    recoveryDuration: 1500,
    attackType: 'sticky',
    attackDamage: 10,
    attackParams: {
      projectileSpeed: 200,
      slowDuration: 2000,        // 2 second slow
    },
    colors: {
      telegraph: '#9B59B6',      // Purple aim
      attack: '#8E44AD',         // Dark purple
    },
    pheromoneEmission: 0.15,
    coordinationRole: 'ranged',
  },

  royal: {
    // Elite behavior: Complex patterns, THE BALL anchor
    attackRange: 70,
    telegraphDuration: 600,
    attackDuration: 400,
    recoveryDuration: 500,
    attackType: 'combo',
    attackDamage: 25,
    attackParams: {
      distance: 100,
      radius: 60,
      projectileSpeed: 180,
    },
    colors: {
      telegraph: '#3498DB',      // Blue warning (royal)
      attack: '#2980B9',         // Dark blue
    },
    pheromoneEmission: 0.5,      // Highest coordination
    coordinationRole: 'elite',
  },
  // Legacy type aliases (for backwards compatibility)
  basic: {
    attackRange: 25,
    telegraphDuration: 200,
    attackDuration: 100,
    recoveryDuration: 400,
    attackType: 'swarm',
    attackDamage: 8,
    attackParams: { distance: 40, speedMultiplier: 1.5 },
    colors: { telegraph: '#F4D03F', attack: '#E67E22' },
    pheromoneEmission: 0.1,
    coordinationRole: 'swarm',
  },
  fast: {
    attackRange: 60,
    telegraphDuration: 150,
    attackDuration: 80,
    recoveryDuration: 600,
    attackType: 'sting',
    attackDamage: 5,
    attackParams: { distance: 80, speedMultiplier: 2.0 },
    colors: { telegraph: '#F39C12', attack: '#FF6B00' },
    pheromoneEmission: 0.3,
    coordinationRole: 'alert',
  },
  tank: {
    attackRange: 40,
    telegraphDuration: 500,
    attackDuration: 300,
    recoveryDuration: 800,
    attackType: 'block',
    attackDamage: 15,
    attackParams: { radius: 50 },
    colors: { telegraph: '#E74C3C', attack: '#C0392B' },
    pheromoneEmission: 0.2,
    coordinationRole: 'anchor',
  },
  spitter: {
    attackRange: 120,
    telegraphDuration: 400,
    attackDuration: 100,
    recoveryDuration: 1500,
    attackType: 'sticky',
    attackDamage: 10,
    attackParams: { projectileSpeed: 200, slowDuration: 2000 },
    colors: { telegraph: '#9B59B6', attack: '#8E44AD' },
    pheromoneEmission: 0.15,
    coordinationRole: 'ranged',
  },
  boss: {
    attackRange: 70,
    telegraphDuration: 600,
    attackDuration: 400,
    recoveryDuration: 500,
    attackType: 'combo',
    attackDamage: 25,
    attackParams: { distance: 100, radius: 60, projectileSpeed: 180 },
    colors: { telegraph: '#3498DB', attack: '#2980B9' },
    pheromoneEmission: 0.5,
    coordinationRole: 'elite',
  },
  colossal_tide: {
    attackRange: 80,
    telegraphDuration: 700,
    attackDuration: 500,
    recoveryDuration: 600,
    attackType: 'combo',
    attackDamage: 30,
    attackParams: { distance: 120, radius: 80, projectileSpeed: 150 },
    colors: { telegraph: '#2C3E50', attack: '#1A252F' },
    pheromoneEmission: 0.8,
    coordinationRole: 'elite',
  },
};

// =============================================================================
// Telegraph Data (for rendering)
// =============================================================================

export interface TelegraphData {
  type: 'swarm' | 'sting' | 'block' | 'sticky' | 'elite';
  enemyId: string;
  position: Vector2;
  direction?: Vector2;           // For directional attacks
  targetPosition?: Vector2;      // Target location
  radius?: number;               // For AOE attacks
  progress: number;              // 0-1, for animation
  color: string;
}

// =============================================================================
// Projectile Type (for propolis)
// =============================================================================

export interface StickyProjectile {
  id: string;
  position: Vector2;
  velocity: Vector2;
  radius: number;
  ownerId: string;
  damage: number;
  slowDuration: number;
  lifetime: number;
  color: string;
}

// =============================================================================
// State Machine
// =============================================================================

/**
 * Get the current behavior state duration
 */
export function getStateDuration(enemy: Enemy, state: BeeBehaviorState): number {
  const config = BEE_BEHAVIORS[enemy.type];
  switch (state) {
    case 'telegraph': return config.telegraphDuration;
    case 'attack': return config.attackDuration;
    case 'recovery': return config.recoveryDuration;
    default: return Infinity;
  }
}

/**
 * Check if bee should start attacking (in range)
 */
function shouldStartAttack(enemy: Enemy, playerPos: Vector2): boolean {
  const config = BEE_BEHAVIORS[enemy.type];
  const dx = playerPos.x - enemy.position.x;
  const dy = playerPos.y - enemy.position.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Propolis and scouts prefer to stay at range
  if (enemy.type === 'propolis' || enemy.type === 'scout') {
    return distance >= 60 && distance <= config.attackRange;
  }

  return distance <= config.attackRange;
}

/**
 * Calculate direction to player
 */
function getDirectionToPlayer(enemy: Enemy, playerPos: Vector2): Vector2 {
  const dx = playerPos.x - enemy.position.x;
  const dy = playerPos.y - enemy.position.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  if (distance === 0) return { x: 1, y: 0 };
  return { x: dx / distance, y: dy / distance };
}

// Extended Enemy type for behavior state tracking
export interface EnemyWithBehavior extends Enemy {
  behaviorState?: BeeBehaviorState;
  stateStartTime?: number;
  attackDirection?: Vector2;
  targetPosition?: Vector2;
}

/**
 * Update bee behavior state machine
 * Returns updated enemy and any spawned projectiles
 */
export function updateBeeBehavior(
  enemy: EnemyWithBehavior,
  playerPos: Vector2,
  gameTime: number,
  deltaTime: number
): { enemy: EnemyWithBehavior; projectiles: StickyProjectile[]; damageDealt: number; pheromoneEmitted: number } {
  const config = BEE_BEHAVIORS[enemy.type];
  const projectiles: StickyProjectile[] = [];
  let damageDealt = 0;
  let pheromoneEmitted = 0;

  // Initialize state if not set
  const currentState = enemy.behaviorState ?? 'chase';
  const stateStartTime = enemy.stateStartTime ?? gameTime;
  const timeInState = gameTime - stateStartTime;

  let newState: BeeBehaviorState = currentState;
  let newEnemy = { ...enemy };

  switch (currentState) {
    case 'chase': {
      // Check if should start attack
      if (shouldStartAttack(enemy, playerPos)) {
        newState = 'telegraph';
        newEnemy.stateStartTime = gameTime;
        newEnemy.attackDirection = getDirectionToPlayer(enemy, playerPos);
        newEnemy.targetPosition = { ...playerPos };

        // Scouts emit alarm pheromones when attacking
        if (enemy.type === 'scout') {
          pheromoneEmitted = config.pheromoneEmission * 2; // Double during attack
        }
      }
      break;
    }

    case 'telegraph': {
      // Wait for telegraph duration, then attack
      if (timeInState >= config.telegraphDuration) {
        newState = 'attack';
        newEnemy.stateStartTime = gameTime;
      }
      break;
    }

    case 'attack': {
      // Execute attack based on bee type
      const attackProgress = timeInState / config.attackDuration;

      if (config.attackType === 'swarm') {
        // Worker swarm: Quick burst toward target
        if (newEnemy.attackDirection && attackProgress <= 1) {
          const swarmSpeed = (config.attackParams.distance ?? 40) / (config.attackDuration / 1000);
          newEnemy.position = {
            x: enemy.position.x + newEnemy.attackDirection.x * swarmSpeed * (deltaTime / 1000),
            y: enemy.position.y + newEnemy.attackDirection.y * swarmSpeed * (deltaTime / 1000),
          };
        }
      } else if (config.attackType === 'sting') {
        // Scout sting: Fast dash in locked direction
        if (newEnemy.attackDirection && attackProgress <= 1) {
          const stingSpeed = (config.attackParams.distance ?? 80) / (config.attackDuration / 1000);
          newEnemy.position = {
            x: enemy.position.x + newEnemy.attackDirection.x * stingSpeed * (deltaTime / 1000),
            y: enemy.position.y + newEnemy.attackDirection.y * stingSpeed * (deltaTime / 1000),
          };
        }
      } else if (config.attackType === 'block') {
        // Guard block: Check if player is in AOE radius at end of attack
        if (attackProgress >= 0.9 && attackProgress < 1.0) {
          const dx = playerPos.x - enemy.position.x;
          const dy = playerPos.y - enemy.position.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (distance <= (config.attackParams.radius ?? 50)) {
            damageDealt = config.attackDamage;
          }
        }
      } else if (config.attackType === 'sticky') {
        // Propolis: Fire sticky projectile at start of attack phase
        if (attackProgress === 0 || (timeInState < deltaTime * 2)) {
          const dir = getDirectionToPlayer(enemy, playerPos);
          projectiles.push({
            id: `sticky-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
            position: { ...enemy.position },
            velocity: {
              x: dir.x * (config.attackParams.projectileSpeed ?? 200),
              y: dir.y * (config.attackParams.projectileSpeed ?? 200),
            },
            radius: 12,
            ownerId: enemy.id,
            damage: config.attackDamage,
            slowDuration: config.attackParams.slowDuration ?? 2000,
            lifetime: 3000,
            color: config.colors.attack,
          });
        }
      } else if (config.attackType === 'combo') {
        // Royal combo: Multi-phase attack
        // Phase 1 (0-0.3): Charge
        // Phase 2 (0.3-0.6): AOE
        // Phase 3 (0.6-1.0): Projectiles
        if (attackProgress < 0.3 && newEnemy.attackDirection) {
          const chargeSpeed = (config.attackParams.distance ?? 100) / (config.attackDuration * 0.3 / 1000);
          newEnemy.position = {
            x: enemy.position.x + newEnemy.attackDirection.x * chargeSpeed * (deltaTime / 1000),
            y: enemy.position.y + newEnemy.attackDirection.y * chargeSpeed * (deltaTime / 1000),
          };
        } else if (attackProgress >= 0.3 && attackProgress < 0.35) {
          // AOE check
          const dx = playerPos.x - enemy.position.x;
          const dy = playerPos.y - enemy.position.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (distance <= (config.attackParams.radius ?? 60)) {
            damageDealt = config.attackDamage;
          }
        }
      }

      // Transition to recovery after attack duration
      if (timeInState >= config.attackDuration) {
        newState = 'recovery';
        newEnemy.stateStartTime = gameTime;
      }
      break;
    }

    case 'recovery': {
      // Wait for recovery duration, then return to chase
      if (timeInState >= config.recoveryDuration) {
        newState = 'chase';
        newEnemy.stateStartTime = gameTime;
        newEnemy.attackDirection = undefined;
        newEnemy.targetPosition = undefined;
      }
      break;
    }
  }

  newEnemy.behaviorState = newState;

  // Passive pheromone emission
  pheromoneEmitted += config.pheromoneEmission * (deltaTime / 1000);

  return { enemy: newEnemy, projectiles, damageDealt, pheromoneEmitted };
}

/**
 * Get telegraph data for a bee (for rendering)
 */
export function getBeeTelegraph(enemy: EnemyWithBehavior, gameTime: number): TelegraphData | null {
  if (enemy.behaviorState !== 'telegraph') return null;

  const config = BEE_BEHAVIORS[enemy.type];
  const stateStartTime = enemy.stateStartTime ?? gameTime;
  const progress = Math.min(1, (gameTime - stateStartTime) / config.telegraphDuration);

  const baseData = {
    enemyId: enemy.id,
    position: enemy.position,
    progress,
    color: config.colors.telegraph,
  };

  switch (config.attackType) {
    case 'swarm':
      return {
        ...baseData,
        type: 'swarm',
        direction: enemy.attackDirection,
      };

    case 'sting':
      return {
        ...baseData,
        type: 'sting',
        direction: enemy.attackDirection,
        targetPosition: enemy.targetPosition,
      };

    case 'block':
      return {
        ...baseData,
        type: 'block',
        radius: config.attackParams.radius,
      };

    case 'sticky':
      return {
        ...baseData,
        type: 'sticky',
        direction: enemy.attackDirection,
        targetPosition: enemy.targetPosition,
      };

    case 'combo':
      return {
        ...baseData,
        type: 'elite',
        direction: enemy.attackDirection,
        radius: config.attackParams.radius,
      };

    default:
      return null;
  }
}

/**
 * Update bee movement based on current behavior state
 */
export function getBeeMovement(
  enemy: EnemyWithBehavior,
  playerPos: Vector2,
  baseSpeed: number,
  _deltaTime: number
): Vector2 {
  const currentState = enemy.behaviorState ?? 'chase';
  const config = BEE_BEHAVIORS[enemy.type];

  switch (currentState) {
    case 'chase': {
      const dir = getDirectionToPlayer(enemy, playerPos);

      // Propolis maintains distance
      if (enemy.type === 'propolis') {
        const dx = playerPos.x - enemy.position.x;
        const dy = playerPos.y - enemy.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 80) {
          // Too close, move away
          return { x: -dir.x * baseSpeed, y: -dir.y * baseSpeed };
        } else if (distance > 120) {
          // Too far, move closer
          return { x: dir.x * baseSpeed, y: dir.y * baseSpeed };
        } else {
          // Good range, strafe
          return { x: -dir.y * baseSpeed * 0.5, y: dir.x * baseSpeed * 0.5 };
        }
      }

      // Scout: Fast, erratic movement
      if (enemy.type === 'scout') {
        const wobble = Math.sin(Date.now() / 100) * 0.3;
        return {
          x: (dir.x + wobble) * baseSpeed * (config.attackParams.speedMultiplier ?? 1),
          y: (dir.y - wobble) * baseSpeed * (config.attackParams.speedMultiplier ?? 1),
        };
      }

      // Guard: Slow, deliberate
      if (enemy.type === 'guard') {
        return { x: dir.x * baseSpeed * 0.5, y: dir.y * baseSpeed * 0.5 };
      }

      // Default chase
      return { x: dir.x * baseSpeed, y: dir.y * baseSpeed };
    }

    case 'telegraph':
      // Stop moving during telegraph (except slight shake for intensity)
      return { x: 0, y: 0 };

    case 'attack':
      // Movement handled by updateBeeBehavior for attacks
      return { x: 0, y: 0 };

    case 'recovery': {
      // Slow movement during recovery (vulnerable)
      const dir = getDirectionToPlayer(enemy, playerPos);
      return { x: dir.x * baseSpeed * 0.3, y: dir.y * baseSpeed * 0.3 };
    }

    default:
      return { x: 0, y: 0 };
  }
}

/**
 * Check if bee is in a vulnerable state (for bonus damage)
 */
export function isBeeVulnerable(enemy: EnemyWithBehavior): boolean {
  return enemy.behaviorState === 'recovery';
}

/**
 * Check if bee is currently attacking (for damage calculation)
 */
export function isBeeAttacking(enemy: EnemyWithBehavior): boolean {
  return enemy.behaviorState === 'attack';
}

/**
 * Get the pheromone emission rate for a bee type
 */
export function getPheromoneEmission(type: EnemyType): number {
  return BEE_BEHAVIORS[type].pheromoneEmission;
}

/**
 * Get the coordination role for a bee type
 */
export function getCoordinationRole(type: EnemyType): BeeBehaviorConfig['coordinationRole'] {
  return BEE_BEHAVIORS[type].coordinationRole;
}
