/**
 * WASM Survivors - Physics System
 *
 * Handles position updates, velocity, and collision detection.
 * Budget: < 5ms for physics, < 3ms for collisions
 *
 * @see pilots/wasm-survivors-witnessed-run-lab/.outline.md
 */

import type {
  GameState,
  Vector2,
  Enemy,
  Projectile,
  EnemyType,
} from '@kgents/shared-primitives';
import type { ActiveUpgrades } from './upgrades';

// =============================================================================
// Constants
// =============================================================================

// Game arena bounds (relative to canvas)
export const ARENA_WIDTH = 800;
export const ARENA_HEIGHT = 600;
export const ARENA_PADDING = 20;

// Physics constants
const ENEMY_CHASE_SPEED_FACTOR = 0.5; // Enemies move toward player (increased for challenge)
const PROJECTILE_SPEED = 400;
const AUTO_ATTACK_COOLDOWN = 500; // ms between attacks

// =============================================================================
// Types
// =============================================================================

export interface PhysicsResult {
  state: GameState;
}

export interface CollisionEvent {
  type: 'enemy_killed' | 'player_hit' | 'xp_collected';
  position: Vector2;
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
 */
export function updatePhysics(
  state: GameState,
  playerVelocity: Vector2,
  deltaTime: number
): PhysicsResult {
  const dt = deltaTime / 1000; // Convert to seconds

  // Update player position
  let playerX = state.player.position.x + playerVelocity.x * dt;
  let playerY = state.player.position.y + playerVelocity.y * dt;

  // Clamp player to arena bounds
  playerX = Math.max(
    ARENA_PADDING + state.player.radius,
    Math.min(ARENA_WIDTH - ARENA_PADDING - state.player.radius, playerX)
  );
  playerY = Math.max(
    ARENA_PADDING + state.player.radius,
    Math.min(ARENA_HEIGHT - ARENA_PADDING - state.player.radius, playerY)
  );

  // DD-15: Slow Field - get active upgrades for slow field check
  const activeUpgrades = state.player.activeUpgrades as ActiveUpgrades | undefined;
  const slowRadius = activeUpgrades?.slowRadius ?? 0;
  const slowPercent = activeUpgrades?.slowPercent ?? 0;

  // Update enemy positions (chase player)
  const updatedEnemies = state.enemies.map((enemy) => {
    const dx = state.player.position.x - enemy.position.x;
    const dy = state.player.position.y - enemy.position.y;
    const distance = Math.sqrt(dx * dx + dy * dy);

    if (distance > 0) {
      const normalizedDx = dx / distance;
      const normalizedDy = dy / distance;

      // DD-15: Slow Field - reduce enemy speed if within slow radius
      let speedMultiplier = 1.0;
      if (slowRadius > 0 && distance < slowRadius) {
        speedMultiplier = 1.0 - slowPercent / 100;
      }

      const baseSpeed = getEnemySpeed(enemy.type);
      const effectiveSpeed = baseSpeed * speedMultiplier;
      const newX =
        enemy.position.x + normalizedDx * effectiveSpeed * ENEMY_CHASE_SPEED_FACTOR * dt;
      const newY =
        enemy.position.y + normalizedDy * effectiveSpeed * ENEMY_CHASE_SPEED_FACTOR * dt;

      return {
        ...enemy,
        position: { x: newX, y: newY },
        velocity: { x: normalizedDx * effectiveSpeed, y: normalizedDy * effectiveSpeed },
      };
    }

    return enemy;
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

  // Auto-attack: spawn projectiles toward nearest enemy
  let newProjectiles = updatedProjectiles;
  const timeSinceLastAttack = state.gameTime % (AUTO_ATTACK_COOLDOWN / state.player.attackSpeed);

  if (
    timeSinceLastAttack < deltaTime &&
    updatedEnemies.length > 0
  ) {
    // Find nearest enemy
    let nearestEnemy: Enemy | null = null;
    let nearestDistance = Infinity;

    for (const enemy of updatedEnemies) {
      const dx = enemy.position.x - playerX;
      const dy = enemy.position.y - playerY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance < nearestDistance && distance <= state.player.attackRange) {
        nearestDistance = distance;
        nearestEnemy = enemy;
      }
    }

    if (nearestEnemy) {
      const dx = nearestEnemy.position.x - playerX;
      const dy = nearestEnemy.position.y - playerY;

      // DD-6: Check for pierce upgrade (now reads from activeUpgrades)
      const pierceCount = activeUpgrades?.pierceCount ?? 0;
      const hasPierce = pierceCount > 0;

      // DD-11: Multishot - fire multiple projectiles in a spread
      const multishotCount = activeUpgrades?.multishotCount ?? 1;
      const multishotSpread = activeUpgrades?.multishotSpread ?? 0;

      // Calculate base angle to target
      const baseAngle = Math.atan2(dy, dx);

      for (let i = 0; i < multishotCount; i++) {
        // Calculate angle offset for this projectile
        const angleOffset = multishotCount === 1
          ? 0
          : ((i - (multishotCount - 1) / 2) * multishotSpread * Math.PI) / 180;
        const angle = baseAngle + angleOffset;

        const projectile: Projectile = {
          id: `proj-${Date.now()}-${Math.random().toString(36).slice(2, 7)}-${i}`,
          position: { x: playerX, y: playerY },
          velocity: {
            x: Math.cos(angle) * PROJECTILE_SPEED,
            y: Math.sin(angle) * PROJECTILE_SPEED,
          },
          radius: 5,
          health: 1,
          maxHealth: 1,
          ownerId: state.player.id,
          damage: state.player.damage,
          lifetime: 2000, // 2 seconds
          color: hasPierce ? '#88DDFF' : (multishotCount > 1 ? '#FF3366' : '#00D4FF'),
          pierceRemaining: pierceCount,
          hitEnemies: [],
        };

        newProjectiles = [...newProjectiles, projectile];
      }
    }
  }

  return {
    state: {
      ...state,
      player: {
        ...state.player,
        position: { x: playerX, y: playerY },
        velocity: playerVelocity,
      },
      enemies: orbitDamagedEnemies,
      projectiles: newProjectiles,
    },
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

            chainProjectiles.push({
              id: `chain-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
              position: { ...enemy.position },
              velocity: {
                x: (dx / dist) * PROJECTILE_SPEED,
                y: (dy / dist) * PROJECTILE_SPEED,
              },
              radius: 5,
              health: 1,
              maxHealth: 1,
              ownerId: projectile.ownerId,
              damage: projectile.damage,
              lifetime: 1000,
              color: '#8844FF', // Purple for chain
              pierceRemaining: 0,
              hitEnemies: Array.from(hitEnemies),
              chainBounces: projChainBounces - 1,
            } as Projectile & { chainBounces: number });
          }
        }

        // DD-6: Pierce support - decrement pierce count or remove projectile
        const pierceRemaining = projectile.pierceRemaining ?? 0;
        if (pierceRemaining > 0) {
          // Projectile continues through (update hit list and pierce count)
          remainingProjectiles = remainingProjectiles.map((p) =>
            p.id === projectile.id
              ? { ...p, pierceRemaining: pierceRemaining - 1, hitEnemies: Array.from(hitEnemies) }
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
  for (const enemy of remainingEnemies) {
    if (circleCollision(state.player, enemy)) {
      events.push({
        type: 'player_hit',
        position: enemy.position,
        enemyType: enemy.type,
        damage: enemy.damage,
      });

      // Push enemy back slightly to prevent continuous damage
      const dx = enemy.position.x - state.player.position.x;
      const dy = enemy.position.y - state.player.position.y;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > 0) {
        const pushDistance = state.player.radius + enemy.radius + 5;
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
 * Get base speed for enemy type
 */
function getEnemySpeed(type: EnemyType): number {
  switch (type) {
    case 'basic':
      return 100;
    case 'fast':
      return 180;
    case 'tank':
      return 50;
    case 'boss':
      return 40;
    default:
      return 100;
  }
}

/**
 * Create initial player entity
 */
export function createInitialPlayer(): GameState['player'] {
  return {
    id: 'player-1',
    position: { x: ARENA_WIDTH / 2, y: ARENA_HEIGHT / 2 },
    velocity: { x: 0, y: 0 },
    radius: 15,
    health: 100,
    maxHealth: 100,
    level: 1,
    xp: 0,
    xpToNextLevel: 100,
    upgrades: [],
    synergies: [],
    damage: 7,        // Reduced from 10 for balance
    attackSpeed: 1,
    moveSpeed: 200,
    attackRange: 150,  // Reduced from 250 for balance
  };
}

/**
 * Create initial game state
 */
export function createInitialGameState(): GameState {
  return {
    status: 'menu',
    player: createInitialPlayer(),
    enemies: [],
    projectiles: [],
    wave: 0,
    waveTimer: 0,
    waveEnemiesRemaining: 0,
    totalEnemiesKilled: 0,
    score: 0,
    gameTime: 0,
  };
}
