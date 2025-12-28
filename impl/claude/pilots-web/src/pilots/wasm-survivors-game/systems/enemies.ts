/**
 * WASM Survivors - Enemy Behavior System
 *
 * DD-21: Pattern-Based Enemy Behaviors
 *
 * Each enemy type has a signature attack pattern:
 * - Shambler: Lunge (short-range burst)
 * - Rusher: Charge (long-range dash, locked direction)
 * - Tank: Stomp (AOE at current position)
 * - Spitter: Projectile (ranged attack)
 * - Boss: Combo (multi-phase attack sequence)
 *
 * State Machine: CHASE → TELEGRAPH → ATTACK → RECOVERY
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 * @see pilots/wasm-survivors-game/runs/run-028/coordination/.outline.md
 */

import type {
  Enemy,
  EnemyType,
  EnemyBehaviorState,
  Vector2,
  Projectile,
} from '@kgents/shared-primitives';

// =============================================================================
// Configuration (DD-22, DD-23)
// =============================================================================

export interface EnemyBehaviorConfig {
  attackRange: number;           // Distance to trigger attack
  telegraphDuration: number;     // Warning time (ms)
  attackDuration: number;        // Commit time (ms)
  recoveryDuration: number;      // Vulnerable time (ms)
  attackType: 'lunge' | 'charge' | 'stomp' | 'projectile' | 'combo';
  attackDamage: number;
  attackParams: {
    distance?: number;           // For lunge/charge
    radius?: number;             // For stomp
    speedMultiplier?: number;    // Speed during attack
    projectileSpeed?: number;    // For projectile
    projectileCount?: number;    // For spread attacks
  };
  colors: {
    telegraph: string;
    attack: string;
  };
}

// DD-23: Attack Timing Constants
export const ENEMY_BEHAVIORS: Record<EnemyType, EnemyBehaviorConfig> = {
  basic: {
    // Shambler: Lunge attack
    attackRange: 30,
    telegraphDuration: 300,
    attackDuration: 100,
    recoveryDuration: 500,
    attackType: 'lunge',
    attackDamage: 15,
    attackParams: {
      distance: 50,
      speedMultiplier: 2,
    },
    colors: {
      telegraph: '#FF4444',  // Red glow
      attack: '#FF0000',
    },
  },
  fast: {
    // Rusher: Charge attack
    attackRange: 100,
    telegraphDuration: 400,
    attackDuration: 300,
    recoveryDuration: 800,
    attackType: 'charge',
    attackDamage: 20,
    attackParams: {
      distance: 200,
      speedMultiplier: 3,
    },
    colors: {
      telegraph: '#FF8800',  // Orange line
      attack: '#FFAA00',
    },
  },
  tank: {
    // Tank: Stomp attack
    attackRange: 50,
    telegraphDuration: 600,
    attackDuration: 200,
    recoveryDuration: 1000,
    attackType: 'stomp',
    attackDamage: 25,
    attackParams: {
      radius: 60,
    },
    colors: {
      telegraph: '#FF2222',  // Red circle
      attack: '#CC0000',
    },
  },
  spitter: {
    // Spitter: Projectile attack (DD-24)
    attackRange: 150,  // Prefers distance
    telegraphDuration: 500,
    attackDuration: 50,
    recoveryDuration: 2000,
    attackType: 'projectile',
    attackDamage: 15,
    attackParams: {
      projectileSpeed: 300,
      projectileCount: 1,
    },
    colors: {
      telegraph: '#AA44FF',  // Purple aim
      attack: '#CC88FF',
    },
  },
  boss: {
    // Boss: Combo attack (DD-25)
    attackRange: 80,
    telegraphDuration: 800,
    attackDuration: 500,
    recoveryDuration: 500,
    attackType: 'combo',
    attackDamage: 30,
    attackParams: {
      distance: 150,
      radius: 80,
      projectileSpeed: 250,
      projectileCount: 3,
    },
    colors: {
      telegraph: '#FFD700',  // Gold
      attack: '#FF6600',
    },
  },
  colossal_tide: {
    // DD-030-4: THE TIDE Colossal - Inexorable Advance
    attackRange: 60,
    telegraphDuration: 1000,  // Long telegraph, gives player time
    attackDuration: 800,
    recoveryDuration: 300,    // Short recovery - relentless
    attackType: 'stomp',      // Area damage
    attackDamage: 40,
    attackParams: {
      radius: 100,  // Large AOE for "Gravity Well" effect
    },
    colors: {
      telegraph: '#880000',  // Deep crimson
      attack: '#FF0000',     // Bright red
    },
  },
};

// =============================================================================
// Telegraph Data (for rendering)
// =============================================================================

export interface TelegraphData {
  type: 'lunge' | 'charge' | 'stomp' | 'aim';
  enemyId: string;
  position: Vector2;
  direction?: Vector2;           // For directional attacks
  targetPosition?: Vector2;      // Target location
  radius?: number;               // For AOE attacks
  progress: number;              // 0-1, for animation
  color: string;
}

// =============================================================================
// State Machine
// =============================================================================

/**
 * Get the current behavior state duration
 * @internal Used for testing and debugging
 */
export function getStateDuration(enemy: Enemy, state: EnemyBehaviorState): number {
  const config = ENEMY_BEHAVIORS[enemy.type];
  switch (state) {
    case 'telegraph': return config.telegraphDuration;
    case 'attack': return config.attackDuration;
    case 'recovery': return config.recoveryDuration;
    default: return Infinity;
  }
}

/**
 * Check if enemy should start attacking (in range)
 */
function shouldStartAttack(enemy: Enemy, playerPos: Vector2): boolean {
  const config = ENEMY_BEHAVIORS[enemy.type];
  const dx = playerPos.x - enemy.position.x;
  const dy = playerPos.y - enemy.position.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  // Spitter wants to be at range, not close
  if (enemy.type === 'spitter') {
    return distance >= 80 && distance <= config.attackRange;
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

/**
 * Update enemy behavior state machine
 * Returns updated enemy and any spawned projectiles
 */
export function updateEnemyBehavior(
  enemy: Enemy,
  playerPos: Vector2,
  gameTime: number,
  deltaTime: number
): { enemy: Enemy; projectiles: Projectile[]; damageDealt: number } {
  const config = ENEMY_BEHAVIORS[enemy.type];
  const projectiles: Projectile[] = [];
  let damageDealt = 0;

  // Initialize state if not set
  const currentState = enemy.behaviorState ?? 'chase';
  const stateStartTime = enemy.stateStartTime ?? gameTime;
  const timeInState = gameTime - stateStartTime;

  let newState: EnemyBehaviorState = currentState;
  let newEnemy = { ...enemy };

  switch (currentState) {
    case 'chase': {
      // Check if should start attack
      if (shouldStartAttack(enemy, playerPos)) {
        newState = 'telegraph';
        newEnemy.stateStartTime = gameTime;
        // Lock attack direction for charges
        newEnemy.attackDirection = getDirectionToPlayer(enemy, playerPos);
        newEnemy.targetPosition = { ...playerPos };
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
      // Execute attack based on type
      const attackProgress = timeInState / config.attackDuration;

      if (config.attackType === 'lunge') {
        // Lunge: Quick burst toward target
        if (newEnemy.attackDirection && attackProgress <= 1) {
          const lungeSpeed = (config.attackParams.distance ?? 50) / (config.attackDuration / 1000);
          newEnemy.position = {
            x: enemy.position.x + newEnemy.attackDirection.x * lungeSpeed * (deltaTime / 1000),
            y: enemy.position.y + newEnemy.attackDirection.y * lungeSpeed * (deltaTime / 1000),
          };
        }
      } else if (config.attackType === 'charge') {
        // Charge: Fast dash in locked direction
        if (newEnemy.attackDirection && attackProgress <= 1) {
          const chargeSpeed = (config.attackParams.distance ?? 200) / (config.attackDuration / 1000);
          newEnemy.position = {
            x: enemy.position.x + newEnemy.attackDirection.x * chargeSpeed * (deltaTime / 1000),
            y: enemy.position.y + newEnemy.attackDirection.y * chargeSpeed * (deltaTime / 1000),
          };
        }
      } else if (config.attackType === 'stomp') {
        // Stomp: Check if player is in AOE radius at end of attack
        if (attackProgress >= 0.9 && attackProgress < 1.0) {
          const dx = playerPos.x - enemy.position.x;
          const dy = playerPos.y - enemy.position.y;
          const distance = Math.sqrt(dx * dx + dy * dy);
          if (distance <= (config.attackParams.radius ?? 60)) {
            damageDealt = config.attackDamage;
          }
        }
      } else if (config.attackType === 'projectile') {
        // Projectile: Fire at start of attack phase
        if (attackProgress === 0 || (timeInState < deltaTime * 2)) {
          const dir = getDirectionToPlayer(enemy, playerPos);
          projectiles.push({
            id: `enemy-proj-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
            position: { ...enemy.position },
            velocity: {
              x: dir.x * (config.attackParams.projectileSpeed ?? 300),
              y: dir.y * (config.attackParams.projectileSpeed ?? 300),
            },
            radius: 8,
            health: 1,
            maxHealth: 1,
            ownerId: enemy.id,
            damage: config.attackDamage,
            lifetime: 3000,
            color: config.colors.attack,
          });
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

  return { enemy: newEnemy, projectiles, damageDealt };
}

/**
 * Get telegraph data for an enemy (for rendering)
 */
export function getEnemyTelegraph(enemy: Enemy, gameTime: number): TelegraphData | null {
  if (enemy.behaviorState !== 'telegraph') return null;

  const config = ENEMY_BEHAVIORS[enemy.type];
  const stateStartTime = enemy.stateStartTime ?? gameTime;
  const progress = Math.min(1, (gameTime - stateStartTime) / config.telegraphDuration);

  const baseData = {
    enemyId: enemy.id,
    position: enemy.position,
    progress,
    color: config.colors.telegraph,
  };

  switch (config.attackType) {
    case 'lunge':
      return {
        ...baseData,
        type: 'lunge',
        direction: enemy.attackDirection,
      };

    case 'charge':
      return {
        ...baseData,
        type: 'charge',
        direction: enemy.attackDirection,
        targetPosition: enemy.targetPosition,
      };

    case 'stomp':
      return {
        ...baseData,
        type: 'stomp',
        radius: config.attackParams.radius,
      };

    case 'projectile':
      return {
        ...baseData,
        type: 'aim',
        direction: enemy.attackDirection,
        targetPosition: enemy.targetPosition,
      };

    default:
      return null;
  }
}

/**
 * Update enemy movement based on current behavior state
 * Called by physics system instead of simple chase
 */
export function getEnemyMovement(
  enemy: Enemy,
  playerPos: Vector2,
  baseSpeed: number,
  _deltaTime: number  // Reserved for future animation timing
): Vector2 {
  const currentState = enemy.behaviorState ?? 'chase';

  switch (currentState) {
    case 'chase': {
      // Normal chase behavior
      const dir = getDirectionToPlayer(enemy, playerPos);

      // Spitter maintains distance
      if (enemy.type === 'spitter') {
        const dx = playerPos.x - enemy.position.x;
        const dy = playerPos.y - enemy.position.y;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance < 80) {
          // Too close, move away
          return { x: -dir.x * baseSpeed, y: -dir.y * baseSpeed };
        } else if (distance > 150) {
          // Too far, move closer
          return { x: dir.x * baseSpeed, y: dir.y * baseSpeed };
        } else {
          // Good range, strafe
          return { x: -dir.y * baseSpeed * 0.5, y: dir.x * baseSpeed * 0.5 };
        }
      }

      return { x: dir.x * baseSpeed, y: dir.y * baseSpeed };
    }

    case 'telegraph':
      // Stop moving during telegraph (except slight shake for intensity)
      return { x: 0, y: 0 };

    case 'attack': {
      // Movement handled by updateEnemyBehavior for attacks
      // Return zero here to avoid double movement
      return { x: 0, y: 0 };
    }

    case 'recovery':
      // Slow movement during recovery (vulnerable)
      const dir = getDirectionToPlayer(enemy, playerPos);
      return { x: dir.x * baseSpeed * 0.3, y: dir.y * baseSpeed * 0.3 };

    default:
      return { x: 0, y: 0 };
  }
}

/**
 * Check if enemy is in a vulnerable state (for bonus damage)
 */
export function isEnemyVulnerable(enemy: Enemy): boolean {
  return enemy.behaviorState === 'recovery';
}

/**
 * Check if enemy is currently attacking (for damage calculation)
 */
export function isEnemyAttacking(enemy: Enemy): boolean {
  return enemy.behaviorState === 'attack';
}
