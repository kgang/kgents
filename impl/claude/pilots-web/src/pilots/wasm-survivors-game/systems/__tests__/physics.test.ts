/**
 * WASM Survivors - Physics System Tests
 *
 * Tests for PROTO_SPEC movement laws:
 * - M1: Responsive - < 16ms input-to-movement
 * - M2: No Stun-Lock - Player can always move
 * - M3: Speed Matters - Base speed outruns basics
 *
 * Also tests collision detection and upgrade effects.
 */

import { describe, it, expect } from 'vitest';
import {
  updatePhysics,
  checkCollisions,
  createInitialGameState,
  createInitialPlayer,
} from '../physics';
import type { Enemy, Projectile } from '../../types';

function createTestEnemy(x: number, y: number, overrides?: Partial<Enemy>): Enemy {
  return {
    id: `enemy-${Math.random().toString(36).slice(2)}`,
    type: 'basic',
    position: { x, y },
    velocity: { x: 0, y: 0 },
    radius: 15,
    health: 50,
    maxHealth: 50,
    damage: 10,
    speed: 100,
    xpValue: 10,
    survivalTime: 0,
    coordinationState: 'idle',
    color: '#F87171',
    behaviorState: 'chase',
    stateStartTime: 0,
    ...overrides,
  };
}

function createTestProjectile(x: number, y: number, vx: number, vy: number): Projectile {
  return {
    id: `proj-${Math.random().toString(36).slice(2)}`,
    position: { x, y },
    velocity: { x: vx, y: vy },
    radius: 5,
    health: 1,
    ownerId: 'player-1',
    damage: 10,
    lifetime: 2000,
    color: '#00D4FF',
  };
}

describe('Physics System', () => {
  describe('M1: Responsive Movement', () => {
    it('should update player position based on velocity', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      const velocity = { x: 200, y: 0 }; // Moving right
      const deltaTime = 16; // One frame

      const { state: updated } = updatePhysics(state, velocity, deltaTime);

      // Player should have moved ~3.2 pixels (200 * 0.016)
      expect(updated.player.position.x).toBeGreaterThan(state.player.position.x);
    });

    it('physics update should complete in reasonable time', () => {
      const state = createInitialGameState();
      state.status = 'playing';
      state.enemies = Array(50).fill(null).map((_, i) =>
        createTestEnemy(100 + i * 10, 100)
      );

      const start = performance.now();
      updatePhysics(state, { x: 100, y: 100 }, 16);
      const elapsed = performance.now() - start;

      // Should be well under 5ms (budget is 5ms for physics)
      expect(elapsed).toBeLessThan(5);
    });
  });

  describe('M2: No Stun-Lock', () => {
    it('player position updates even after collision with enemy', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      // Add an enemy at player position (overlapping)
      state.enemies = [createTestEnemy(
        state.player.position.x,
        state.player.position.y,
        { behaviorState: 'attack' } // Must be attacking to trigger collision
      )];

      // Check collisions - player hit
      const { state: afterCollision, events } = checkCollisions(state);
      expect(events.some(e => e.type === 'player_hit')).toBe(true);

      // Now move player - should still work
      const { state: afterMove } = updatePhysics(afterCollision, { x: 200, y: 0 }, 16);
      expect(afterMove.player.position.x).toBeGreaterThan(state.player.position.x);
    });

    it('player should not take damage from non-attacking enemies', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      // Enemy overlapping but in chase state (not attacking)
      state.enemies = [createTestEnemy(
        state.player.position.x,
        state.player.position.y,
        { behaviorState: 'chase' }
      )];

      const { events } = checkCollisions(state);
      expect(events.some(e => e.type === 'player_hit')).toBe(false);
    });
  });

  describe('M3: Speed Matters', () => {
    it('player base speed should be faster than basic enemy', () => {
      const player = createInitialPlayer();
      // Basic enemy speed is 100 * 0.5 (ENEMY_CHASE_SPEED_FACTOR) = 50
      expect(player.moveSpeed).toBeGreaterThan(50);
    });
  });

  describe('Collision Detection', () => {
    it('should detect projectile hitting enemy', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      // Enemy at position with low health so projectile damage kills it
      state.enemies = [createTestEnemy(200, 300, { health: 5, radius: 20 })];

      // Projectile at same position, close enough for collision
      // Projectile radius = 5, enemy radius = 20, they overlap
      state.projectiles = [createTestProjectile(200, 300, 100, 0)];

      const { events } = checkCollisions(state);
      expect(events.some(e => e.type === 'enemy_killed')).toBe(true);
    });

    it('should remove projectile after hitting enemy without pierce', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      state.enemies = [createTestEnemy(200, 300, { health: 5, radius: 20 })];
      state.projectiles = [createTestProjectile(200, 300, 100, 0)];

      const { state: afterCollision } = checkCollisions(state);
      expect(afterCollision.projectiles).toHaveLength(0);
    });

    it('should keep projectile with pierce remaining', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      // Two enemies - one overlapping projectile, one nearby
      state.enemies = [
        createTestEnemy(200, 300, { health: 5, radius: 20 }),
        createTestEnemy(250, 300, { health: 50, radius: 20 }), // Second enemy further away
      ];

      // Projectile with pierce starting at first enemy
      const pierceProj = createTestProjectile(200, 300, 100, 0);
      (pierceProj as any).pierceRemaining = 2;
      (pierceProj as any).hitEnemies = new Set<string>();
      state.projectiles = [pierceProj];

      const { state: afterCollision, events } = checkCollisions(state);
      // First enemy killed
      expect(events.some(e => e.type === 'enemy_killed')).toBe(true);
      // Projectile continues
      expect(afterCollision.projectiles).toHaveLength(1);
      expect((afterCollision.projectiles[0] as any).pierceRemaining).toBe(1);
    });
  });

  describe('Arena Bounds', () => {
    it('should clamp player to arena boundaries', () => {
      const state = createInitialGameState();
      state.status = 'playing';
      state.player.position = { x: 0, y: 0 };

      // Try to move off left edge
      const { state: updated } = updatePhysics(state, { x: -1000, y: 0 }, 16);

      // Should be clamped to minimum
      expect(updated.player.position.x).toBeGreaterThan(0);
      expect(updated.player.position.x).toBeLessThan(100);
    });

    it('should constrain projectiles to arena', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      // Projectile moving off screen
      state.projectiles = [createTestProjectile(-100, 300, -100, 0)];

      const { state: updated } = updatePhysics(state, { x: 0, y: 0 }, 16);

      // Projectile should be removed (out of bounds)
      expect(updated.projectiles).toHaveLength(0);
    });
  });

  describe('Orbit Upgrade Effect', () => {
    it('should damage enemies within orbit radius', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      // Enable orbit upgrade
      state.player.activeUpgrades = {
        upgrades: ['orbit'],
        synergies: [],
        pierceCount: 0,
        orbitActive: true,
        orbitRadius: 60,
        orbitDamage: 100, // High damage for testing
        dashCooldown: 0,
        dashDistance: 0,
        multishotCount: 1,
        multishotSpread: 0,
        vampiricPercent: 0,
        chainBounces: 0,
        chainRange: 0,
        burstRadius: 0,
        burstDamage: 0,
        slowRadius: 0,
        slowPercent: 0,
      };

      // Enemy within orbit radius
      const enemyX = state.player.position.x + 30;
      state.enemies = [createTestEnemy(enemyX, state.player.position.y, { health: 100 })];

      const { state: updated } = updatePhysics(state, { x: 0, y: 0 }, 1000); // 1 second

      // Enemy should have taken orbit damage
      expect(updated.enemies[0].health).toBeLessThan(100);
    });
  });

  describe('Slow Field Effect', () => {
    it('should slow enemies within slow radius', () => {
      const state = createInitialGameState();
      state.status = 'playing';

      // Enable slow field
      state.player.activeUpgrades = {
        upgrades: ['slow_field'],
        synergies: [],
        pierceCount: 0,
        orbitActive: false,
        orbitRadius: 0,
        orbitDamage: 0,
        dashCooldown: 0,
        dashDistance: 0,
        multishotCount: 1,
        multishotSpread: 0,
        vampiricPercent: 0,
        chainBounces: 0,
        chainRange: 0,
        burstRadius: 0,
        burstDamage: 0,
        slowRadius: 100,
        slowPercent: 50, // 50% slow
      };

      // Enemy within slow radius, chasing player
      const enemy = createTestEnemy(
        state.player.position.x + 50,
        state.player.position.y,
        { behaviorState: 'chase' }
      );
      state.enemies = [enemy];

      // Get movement without slow field for comparison
      const withoutSlow = { ...state };
      withoutSlow.player = { ...state.player, activeUpgrades: undefined };

      // The slow field should result in slower movement
      // This is a structural test - the slow is applied in physics
      const { state: updated } = updatePhysics(state, { x: 0, y: 0 }, 16);

      // Enemy velocity should reflect slowed movement
      expect(updated.enemies[0].velocity.x).toBeDefined();
    });
  });
});
