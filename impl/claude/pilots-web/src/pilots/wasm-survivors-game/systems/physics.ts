/**
 * Hornet Siege - Physics System
 *
 * Handles position updates, velocity, and collision detection.
 * Budget: < 5ms for physics, < 3ms for collisions
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import type {
  GameState,
  Vector2,
  Enemy,
  Projectile,
  EnemyType,
} from '../types';
import type { ActiveUpgrades } from './upgrades';
import { updateBeeBehavior, getBeeMovement, type TelegraphData, getBeeTelegraph } from './enemies';

// =============================================================================
// Constants
// =============================================================================

// Game arena bounds (relative to canvas)
export const ARENA_WIDTH = 800;
export const ARENA_HEIGHT = 600;
export const ARENA_PADDING = 20;

// Physics constants
const ENEMY_CHASE_SPEED_FACTOR = 0.5; // Enemies move toward player (increased for challenge)
// DD-36: Player projectiles removed - Mandible Reaver melee only
// Enemy projectile speed remains for bee attacks
const ENEMY_PROJECTILE_SPEED = 400;

// =============================================================================
// Catch-Up / Self-Healing System Constants
// Prevents enemies from getting "stuck" far from the action
// =============================================================================

/** Distance threshold beyond which enemies are considered "too far" */
const CATCH_UP_DISTANCE_THRESHOLD = 500;

/** Time an enemy can be "too far" before catch-up kicks in (ms) */
const CATCH_UP_TIME_THRESHOLD = 5000; // 5 seconds

/** Speed boost multiplier when enemy is in catch-up mode */
const CATCH_UP_SPEED_BOOST = 3.0;

/** If enemy is THIS far away, teleport them closer (hard limit) */
const TELEPORT_DISTANCE_THRESHOLD = 800;

/** Teleport target distance from player (places enemy just outside normal range) */
const TELEPORT_TARGET_DISTANCE = 350;

/** Minimum speed to consider enemy "moving" (prevents velocity=0 stuck state) */
const MINIMUM_MOVEMENT_SPEED = 10;

// =============================================================================
// Catch-Up / Self-Healing Helper Functions
// =============================================================================

/**
 * Apply catch-up logic to an enemy that might be "stuck" far from action.
 *
 * This system prevents frustrating scenarios where one enemy spawns far away
 * and takes forever to reach the player, blocking wave completion.
 *
 * Three tiers of intervention:
 * 1. ACCELERATION: After 5s far away, enemy gets 3x speed boost
 * 2. TELEPORT: If >800px away, teleport to ~350px from player
 * 3. STUCK FIX: If velocity is near-zero, force movement toward player
 *
 * @param enemy - The enemy to check
 * @param playerPos - Player's current position
 * @param deltaTime - Time since last frame (ms)
 * @returns Updated enemy with catch-up state applied
 */
function applyCatchUpLogic(
  enemy: Enemy,
  playerPos: Vector2,
  deltaTime: number
): { enemy: Enemy; catchUpMultiplier: number; wasTeleported: boolean } {
  // Calculate distance to player
  const dx = playerPos.x - enemy.position.x;
  const dy = playerPos.y - enemy.position.y;
  const distanceToPlayer = Math.sqrt(dx * dx + dy * dy);

  let updatedEnemy = { ...enemy };
  let catchUpMultiplier = 1.0;
  let wasTeleported = false;

  // ==========================================================================
  // TIER 3: TELEPORT - Enemy is extremely far away (>800px)
  // This is a hard reset to prevent indefinite stalling
  // ==========================================================================
  if (distanceToPlayer > TELEPORT_DISTANCE_THRESHOLD) {
    // Teleport enemy to ~350px from player in a random direction
    const angle = Math.random() * Math.PI * 2;
    const teleportX = playerPos.x + Math.cos(angle) * TELEPORT_TARGET_DISTANCE;
    const teleportY = playerPos.y + Math.sin(angle) * TELEPORT_TARGET_DISTANCE;

    // Clamp to arena bounds (with some padding)
    const clampedX = Math.max(50, Math.min(ARENA_WIDTH - 50, teleportX));
    const clampedY = Math.max(50, Math.min(ARENA_HEIGHT - 50, teleportY));

    updatedEnemy.position = { x: clampedX, y: clampedY };
    updatedEnemy.farAwayTime = 0;
    updatedEnemy.inCatchUpMode = false;
    wasTeleported = true;

    console.log(`[CATCH-UP] Teleported ${enemy.type} from ${Math.round(distanceToPlayer)}px to ${TELEPORT_TARGET_DISTANCE}px from player`);

    return { enemy: updatedEnemy, catchUpMultiplier: 1.0, wasTeleported };
  }

  // ==========================================================================
  // TIER 1 & 2: TRACK TIME FAR AWAY + ACCELERATION
  // ==========================================================================
  if (distanceToPlayer > CATCH_UP_DISTANCE_THRESHOLD) {
    // Enemy is far - accumulate time
    const currentFarTime = enemy.farAwayTime ?? 0;
    updatedEnemy.farAwayTime = currentFarTime + deltaTime;

    // After threshold time, enable catch-up mode
    if (updatedEnemy.farAwayTime >= CATCH_UP_TIME_THRESHOLD) {
      updatedEnemy.inCatchUpMode = true;
      catchUpMultiplier = CATCH_UP_SPEED_BOOST;
    }
  } else {
    // Enemy is within normal range - reset catch-up state
    updatedEnemy.farAwayTime = 0;
    updatedEnemy.inCatchUpMode = false;
  }

  // ==========================================================================
  // TIER 2.5: STUCK FIX - Velocity near zero but enemy still alive
  // This handles edge cases where behaviorState causes movement to stop
  // ==========================================================================
  const velocityMagnitude = Math.sqrt(
    enemy.velocity.x * enemy.velocity.x +
    enemy.velocity.y * enemy.velocity.y
  );

  if (
    velocityMagnitude < MINIMUM_MOVEMENT_SPEED &&
    distanceToPlayer > 100 && // Not already near player
    enemy.behaviorState !== 'telegraph' && // Not intentionally stopped
    enemy.behaviorState !== 'attack'
  ) {
    // Force movement toward player with base speed
    const dirX = dx / distanceToPlayer;
    const dirY = dy / distanceToPlayer;
    const baseSpeed = getEnemySpeed(enemy.type);

    updatedEnemy.velocity = {
      x: dirX * baseSpeed,
      y: dirY * baseSpeed,
    };

    // Also enable catch-up mode to speed this up
    updatedEnemy.inCatchUpMode = true;
    catchUpMultiplier = Math.max(catchUpMultiplier, CATCH_UP_SPEED_BOOST * 0.5); // 1.5x minimum
  }

  return { enemy: updatedEnemy, catchUpMultiplier, wasTeleported };
}

// =============================================================================
// Types
// =============================================================================

export interface PhysicsResult {
  state: GameState;
  telegraphs: TelegraphData[];  // DD-21: Telegraph data for rendering
  enemyDamageDealt: number;     // DD-21: Damage from enemy attacks
}

export interface CollisionEvent {
  type: 'enemy_killed' | 'player_hit' | 'xp_collected' | 'shield_broken';
  position: Vector2;
  // DD-21: Track which attack type caused the hit (bee attacks)
  attackType?: 'swarm' | 'sting' | 'block' | 'sticky' | 'combo';
  enemyType?: EnemyType;
  xpValue?: number;
  damage?: number;
}

export interface CollisionResult {
  state: GameState;
  events: CollisionEvent[];
}

// =============================================================================
// Physics Update
// =============================================================================

/**
 * Update physics for all entities
 * Budget: < 5ms
 *
 * @param state - Current game state
 * @param playerVelocity - Player velocity in pixels per second
 * @param deltaTime - Time since last frame in MILLISECONDS (frame-rate independent)
 * @param enemySlowFactor - Global enemy speed multiplier from abilities (1.0 = normal, 0.8 = 20% slower)
 */
export function updatePhysics(
  state: GameState,
  playerVelocity: Vector2,
  deltaTime: number,
  enemySlowFactor: number = 1.0
): PhysicsResult {
  const dt = deltaTime / 1000; // Convert to seconds for velocity calculations

  // Update player position
  let playerX = state.player.position.x + playerVelocity.x * dt;
  let playerY = state.player.position.y + playerVelocity.y * dt;

  // Clamp player to arena bounds
  const playerRadius = state.player.radius ?? 15;
  playerX = Math.max(
    ARENA_PADDING + playerRadius,
    Math.min(ARENA_WIDTH - ARENA_PADDING - playerRadius, playerX)
  );
  playerY = Math.max(
    ARENA_PADDING + playerRadius,
    Math.min(ARENA_HEIGHT - ARENA_PADDING - playerRadius, playerY)
  );

  // DD-15: Slow Field - get active upgrades for slow field check
  const activeUpgrades = state.player.activeUpgrades as ActiveUpgrades | undefined;
  const slowRadius = activeUpgrades?.slowRadius ?? 0;
  const slowPercent = activeUpgrades?.slowPercent ?? 0;

  // DD-21: Track telegraphs and enemy attack damage
  const telegraphs: TelegraphData[] = [];
  let enemyDamageDealt = 0;
  const enemyProjectiles: Projectile[] = [];

  // Update enemy behaviors and positions (DD-21: Pattern-Based)
  const updatedEnemies = state.enemies.map((enemy) => {
    const playerPos = { x: playerX, y: playerY };

    // ==========================================================================
    // Run 038: CATCH-UP / SELF-HEALING SYSTEM
    // Prevents enemies from getting stuck far from the action
    // Applied FIRST so teleported enemies get proper behavior updates
    // ==========================================================================
    const catchUpResult = applyCatchUpLogic(enemy, playerPos, deltaTime);
    let updatedEnemy = catchUpResult.enemy;
    const catchUpMultiplier = catchUpResult.catchUpMultiplier;

    // If enemy was teleported, skip normal behavior update this frame
    // (they just need to start moving toward player)
    if (catchUpResult.wasTeleported) {
      // Reset behavior state to chase
      updatedEnemy.behaviorState = 'chase';
      updatedEnemy.stateStartTime = state.gameTime;
      updatedEnemy.attackDirection = undefined;
      updatedEnemy.targetPosition = undefined;
    }

    // DD-21: Update behavior state machine (Bee FSM)
    // Pass enemySlowFactor to apply Bullet Time slowdown to attack movements
    const behaviorResult = updateBeeBehavior(updatedEnemy, playerPos, state.gameTime, deltaTime, enemySlowFactor);
    updatedEnemy = behaviorResult.enemy;
    enemyDamageDealt += behaviorResult.damageDealt;

    // Collect enemy projectiles (Spitter)
    enemyProjectiles.push(...behaviorResult.projectiles);

    // Collect telegraph data for rendering
    const telegraph = getBeeTelegraph(updatedEnemy, state.gameTime);
    if (telegraph) {
      telegraphs.push(telegraph);
    }

    // DD-21: Get movement based on current behavior state
    const baseSpeed = getEnemySpeed(enemy.type);
    const movement = getBeeMovement(updatedEnemy, playerPos, baseSpeed, deltaTime);

    // DD-15: Slow Field - reduce enemy speed if within slow radius
    const dx = playerPos.x - updatedEnemy.position.x;
    const dy = playerPos.y - updatedEnemy.position.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    // Calculate total speed multiplier from all sources
    // 1. Start with global enemySlowFactor from Bullet Time ability (1.0 = normal, 0.8 = 20% slower)
    // 2. Apply DD-15 Slow Field if enemy is within radius
    // 3. Apply Run 043 Movement Trail slow (thermal_wake + rally_scent)
    // 4. Apply Run 038 Catch-Up boost (3x) if enemy has been far away too long
    let speedMultiplier = enemySlowFactor * catchUpMultiplier;
    if (slowRadius > 0 && distance < slowRadius) {
      speedMultiplier *= (1.0 - slowPercent / 100);
    }

    // Run 043: Apply trail slow from thermal_wake + rally_scent abilities
    // trailSlowPercent is set by processMovementTrail in useGameLoop
    if (updatedEnemy.trailSlowPercent && updatedEnemy.trailSlowPercent > 0) {
      speedMultiplier *= (1.0 - updatedEnemy.trailSlowPercent / 100);
    }

    // Apply movement (only if not in attack state - attack movement handled in behavior)
    // Movement is frame-rate independent: velocity * speedMultiplier * dt (where dt = deltaTime/1000)
    if (updatedEnemy.behaviorState !== 'attack') {
      const newX = updatedEnemy.position.x + movement.x * speedMultiplier * ENEMY_CHASE_SPEED_FACTOR * dt;
      const newY = updatedEnemy.position.y + movement.y * speedMultiplier * ENEMY_CHASE_SPEED_FACTOR * dt;

      updatedEnemy = {
        ...updatedEnemy,
        position: { x: newX, y: newY },
        velocity: { x: movement.x * speedMultiplier, y: movement.y * speedMultiplier },
      };
    }

    return updatedEnemy;
  });

  // DD-9: Orbit - damage enemies within orbit radius
  let orbitDamagedEnemies = updatedEnemies;
  if (activeUpgrades?.orbitActive && activeUpgrades.orbitRadius > 0) {
    const orbitDamagePerSecond = activeUpgrades.orbitDamage ?? 15;
    const orbitDamageThisFrame = orbitDamagePerSecond * dt;

    orbitDamagedEnemies = updatedEnemies.map((enemy) => {
      const dx = enemy.position.x - playerX;
      const dy = enemy.position.y - playerY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < activeUpgrades.orbitRadius) {
        // Enemy is within orbit - apply damage
        const newHealth = enemy.health - orbitDamageThisFrame;
        return { ...enemy, health: newHealth };
      }
      return enemy;
    });
  }

  // Update projectile positions
  const updatedProjectiles = state.projectiles
    .map((proj) => {
      const newX = proj.position.x + proj.velocity.x * dt;
      const newY = proj.position.y + proj.velocity.y * dt;
      const newLifetime = proj.lifetime - deltaTime;

      return {
        ...proj,
        position: { x: newX, y: newY },
        lifetime: newLifetime,
      };
    })
    .filter((proj) => {
      // Remove projectiles that are out of bounds or expired
      return (
        proj.lifetime > 0 &&
        proj.position.x > 0 &&
        proj.position.x < ARENA_WIDTH &&
        proj.position.y > 0 &&
        proj.position.y < ARENA_HEIGHT
      );
    });

  // DD-36: Auto-attack REMOVED - Player uses Mandible Reaver melee only
  // Enemy projectiles still exist for enemy attacks
  const allProjectiles = [...updatedProjectiles, ...enemyProjectiles];

  return {
    state: {
      ...state,
      player: {
        ...state.player,
        position: { x: playerX, y: playerY },
        velocity: playerVelocity,
      },
      enemies: orbitDamagedEnemies,
      projectiles: allProjectiles,
    },
    telegraphs,        // DD-21: For rendering
    enemyDamageDealt,  // DD-21: Attack damage (separate from contact)
  };
}

// =============================================================================
// Collision Detection
// =============================================================================

/**
 * Check all collisions and return events
 * Budget: < 3ms
 */
export function checkCollisions(state: GameState): CollisionResult {
  const events: CollisionEvent[] = [];
  let remainingEnemies = [...state.enemies];
  let remainingProjectiles = [...state.projectiles];
  const chainProjectiles: Projectile[] = []; // DD-13: Chain projectiles to spawn

  // DD-13: Get chain settings from active upgrades
  const activeUpgrades = state.player.activeUpgrades as ActiveUpgrades | undefined;
  const chainBounces = activeUpgrades?.chainBounces ?? 0;
  const chainRange = activeUpgrades?.chainRange ?? 80;

  // Check projectile-enemy collisions
  for (const projectile of state.projectiles) {
    // Track enemies hit by this projectile this frame
    const hitEnemies = new Set(projectile.hitEnemies || []);

    for (const enemy of remainingEnemies) {
      // Skip if already hit this enemy
      if (hitEnemies.has(enemy.id)) continue;

      if (circleCollision(projectile, enemy)) {
        // Hit!
        const newHealth = enemy.health - projectile.damage;
        hitEnemies.add(enemy.id);

        if (newHealth <= 0) {
          // Enemy killed
          events.push({
            type: 'enemy_killed',
            position: enemy.position,
            enemyType: enemy.type,
            xpValue: enemy.xpValue,
          });

          // Remove enemy
          remainingEnemies = remainingEnemies.filter((e) => e.id !== enemy.id);
        } else {
          // Enemy damaged
          remainingEnemies = remainingEnemies.map((e) =>
            e.id === enemy.id ? { ...e, health: newHealth } : e
          );
        }

        // DD-13: Chain - spawn bounce projectile to nearby enemy
        const projChainBounces = (projectile as { chainBounces?: number }).chainBounces ?? chainBounces;
        if (projChainBounces > 0) {
          // Find nearest un-hit enemy within chain range
          let nearestChainTarget: Enemy | null = null;
          let nearestChainDist = Infinity;

          for (const potentialTarget of remainingEnemies) {
            if (hitEnemies.has(potentialTarget.id)) continue;
            const dx = potentialTarget.position.x - enemy.position.x;
            const dy = potentialTarget.position.y - enemy.position.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < chainRange && dist < nearestChainDist && dist > 0) {
              nearestChainDist = dist;
              nearestChainTarget = potentialTarget;
            }
          }

          if (nearestChainTarget) {
            // Spawn chain projectile
            const dx = nearestChainTarget.position.x - enemy.position.x;
            const dy = nearestChainTarget.position.y - enemy.position.y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            const chainProjectile: Projectile = {
              id: `chain-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
              position: { ...enemy.position },
              velocity: {
                x: (dx / dist) * ENEMY_PROJECTILE_SPEED,
                y: (dy / dist) * ENEMY_PROJECTILE_SPEED,
              },
              radius: 5,
              health: 1,
              ownerId: projectile.ownerId,
              damage: projectile.damage,
              lifetime: 1000,
              color: '#8844FF', // Purple for chain
              pierceRemaining: 0,
              hitEnemies: new Set(hitEnemies),
            };
            chainProjectiles.push(chainProjectile);
          }
        }

        // DD-6: Pierce support - decrement pierce count or remove projectile
        const pierceRemaining = projectile.pierceRemaining ?? 0;
        if (pierceRemaining > 0) {
          // Projectile continues through (update hit list and pierce count)
          remainingProjectiles = remainingProjectiles.map((p) =>
            p.id === projectile.id
              ? { ...p, pierceRemaining: pierceRemaining - 1, hitEnemies: new Set(hitEnemies) }
              : p
          );
          // Continue checking other enemies (don't break)
        } else {
          // No pierce remaining - remove projectile
          remainingProjectiles = remainingProjectiles.filter(
            (p) => p.id !== projectile.id
          );
          break; // Projectile destroyed
        }
      }
    }
  }

  // Check player-enemy collisions
  // DD-21: Contact damage only during ATTACK state (enemies must commit to hurt you)
  for (const enemy of remainingEnemies) {
    const isAttacking = enemy.behaviorState === 'attack';

    // Create player collision object with default radius
    const playerCollider = {
      position: state.player.position,
      radius: state.player.radius ?? 15,
    };

    if (circleCollision(playerCollider, enemy) && isAttacking) {
      events.push({
        type: 'player_hit',
        position: enemy.position,
        enemyType: enemy.type,
        damage: enemy.damage,
        // DD-21: Track that this was a bee attack
        attackType: enemy.type === 'worker' ? 'swarm'
          : enemy.type === 'scout' ? 'sting'
          : enemy.type === 'guard' ? 'block'
          : enemy.type === 'propolis' ? 'sticky'
          : 'combo',
      });

      // Push enemy back slightly to prevent continuous damage
      const dx = enemy.position.x - state.player.position.x;
      const dy = enemy.position.y - state.player.position.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > 0) {
        const pushDistance = (state.player.radius ?? 15) + enemy.radius + 5;
        remainingEnemies = remainingEnemies.map((e) =>
          e.id === enemy.id
            ? {
                ...e,
                position: {
                  x: state.player.position.x + (dx / distance) * pushDistance,
                  y: state.player.position.y + (dy / distance) * pushDistance,
                },
              }
            : e
        );
      }
    }
  }

  return {
    state: {
      ...state,
      enemies: remainingEnemies,
      projectiles: [...remainingProjectiles, ...chainProjectiles], // DD-13: Include chain projectiles
    },
    events,
  };
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Circle-circle collision detection
 */
function circleCollision(
  a: { position: Vector2; radius: number },
  b: { position: Vector2; radius: number }
): boolean {
  const dx = a.position.x - b.position.x;
  const dy = a.position.y - b.position.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  return distance < a.radius + b.radius;
}

/**
 * Get base speed for bee type
 * Per PROTO_SPEC S6: Bee Taxonomy
 */
function getEnemySpeed(type: EnemyType): number {
  switch (type) {
    case 'worker':
      return 80;     // Swarms, moderate speed
    case 'scout':
      return 120;    // Fast alerters
    case 'propolis':
      return 50;     // Ranged, stays back
    case 'guard':
      return 48;     // Slow defenders (+20% faster for more pressure)
    case 'royal':
      return 60;     // Elite, deliberate
    default:
      return 80;
  }
}

/**
 * Create initial player entity
 */
export function createInitialPlayer(): GameState['player'] {
  return {
    position: { x: ARENA_WIDTH / 2, y: ARENA_HEIGHT / 2 },
    velocity: { x: 0, y: 0 },
    radius: 15,
    health: 100,
    maxHealth: 100,
    level: 1,
    xp: 0,
    xpToNextLevel: 250,  // Tuned for balanced progression
    upgrades: [],
    damage: 7,
    attackSpeed: 1,
    moveSpeed: 200,
    attackRange: 150,
    attackCooldown: 500,
    lastAttackTime: 0,
    dashCooldown: 1000,
    lastDashTime: 0,
    invincible: false,
    invincibilityEndTime: 0,
  };
}

/**
 * Create initial game state
 */
export function createInitialGameState(): GameState {
  return {
    // Core state
    status: 'menu',
    gameTime: 0,
    wave: 0,
    waveTimer: 0,
    waveEnemiesRemaining: 0,

    // Entities
    player: createInitialPlayer(),
    enemies: [],
    projectiles: [],
    particles: [],
    xpOrbs: [],

    // Stats
    score: 0,
    totalEnemiesKilled: 0,
    killCount: 0,
    comboCount: 0,
    lastKillTime: 0,

    // Visual effects
    screenShake: null,

    // THE BALL system
    activeFormation: null,
    ballPhase: null,
    ballsFormed: 0,
    colonyCoordination: 0,

    // Emotional system
    contrastState: {
      enemyDensity: 0,
      playerHealthPercent: 1,
      killsPerSecond: 0,
      timeSinceLastKill: 0,
      coordinationLevel: 0,
    },
    currentMood: 'flow',

    // Upgrades
    upgradeChoices: null,
    activeUpgrades: {
      upgrades: [],
      damageMultiplier: 1,
      attackSpeedMultiplier: 1,
      moveSpeedMultiplier: 1,
      pierceCount: 0,
      orbitActive: false,
      orbitDamage: 0,
    },
  };
}
