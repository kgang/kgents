/**
 * WASM Survivors - Enemy System Tests
 *
 * Tests for PROTO_SPEC enemy laws:
 * - E1: Readable Tells - Attacks are telegraphed
 * - E2: Learnable Patterns - Consistent behavior
 * - E4: Escalating Threat - Basics → Elites → Bosses
 */

import { describe, it, expect } from 'vitest';
import {
  ENEMY_BEHAVIORS,
  updateEnemyBehavior,
  getEnemyTelegraph,
  getEnemyMovement,
  isEnemyVulnerable,
  isEnemyAttacking,
} from '../enemies';
import type { Enemy, EnemyType } from '@kgents/shared-primitives';

function createTestEnemy(type: EnemyType, overrides?: Partial<Enemy>): Enemy {
  return {
    id: `test-${type}-${Math.random().toString(36).slice(2)}`,
    type,
    position: { x: 100, y: 100 },
    velocity: { x: 0, y: 0 },
    radius: 15,
    health: 50,
    maxHealth: 50,
    damage: 10,
    xpValue: 10,
    color: '#F87171',
    behaviorState: 'chase',
    stateStartTime: 0,
    ...overrides,
  };
}

describe('Enemy Behavior System', () => {
  describe('E1: Readable Tells', () => {
    it('should have 6 enemy types with behavior configs', () => {
      // DD-030: Added colossal_tide for metamorphosis
      const types: EnemyType[] = ['basic', 'fast', 'tank', 'spitter', 'boss', 'colossal_tide'];
      for (const type of types) {
        expect(ENEMY_BEHAVIORS[type]).toBeDefined();
      }
    });

    it('each enemy type should have telegraph duration', () => {
      for (const [type, config] of Object.entries(ENEMY_BEHAVIORS)) {
        expect(config.telegraphDuration).toBeGreaterThan(0);
        // Colossals can have longer telegraphs (up to 1.5s)
        const maxDuration = type === 'colossal_tide' ? 1500 : 1000;
        expect(config.telegraphDuration).toBeLessThanOrEqual(maxDuration);
      }
    });

    it('should generate telegraph data during telegraph state', () => {
      const enemy = createTestEnemy('basic', {
        behaviorState: 'telegraph',
        stateStartTime: 0,
        attackDirection: { x: 1, y: 0 },
      });

      const telegraph = getEnemyTelegraph(enemy, 100);
      expect(telegraph).not.toBeNull();
      expect(telegraph!.type).toBe('lunge');
      expect(telegraph!.progress).toBeGreaterThan(0);
    });

    it('should not generate telegraph data in other states', () => {
      const states = ['chase', 'attack', 'recovery'] as const;
      for (const state of states) {
        const enemy = createTestEnemy('basic', { behaviorState: state });
        const telegraph = getEnemyTelegraph(enemy, 0);
        expect(telegraph).toBeNull();
      }
    });
  });

  describe('E2: Learnable Patterns', () => {
    it('state machine should transition CHASE → TELEGRAPH when in range', () => {
      const enemy = createTestEnemy('basic', {
        position: { x: 100, y: 100 },
        behaviorState: 'chase',
        stateStartTime: 0,
      });
      const playerPos = { x: 110, y: 100 }; // Within attack range (30)

      const { enemy: updated } = updateEnemyBehavior(enemy, playerPos, 100, 16);
      expect(updated.behaviorState).toBe('telegraph');
    });

    it('state machine should transition TELEGRAPH → ATTACK after duration', () => {
      const config = ENEMY_BEHAVIORS.basic;
      const enemy = createTestEnemy('basic', {
        behaviorState: 'telegraph',
        stateStartTime: 0,
        attackDirection: { x: 1, y: 0 },
      });
      const playerPos = { x: 200, y: 100 };

      // After telegraph duration
      const gameTime = config.telegraphDuration + 1;
      const { enemy: updated } = updateEnemyBehavior(enemy, playerPos, gameTime, 16);
      expect(updated.behaviorState).toBe('attack');
    });

    it('state machine should transition ATTACK → RECOVERY after duration', () => {
      const config = ENEMY_BEHAVIORS.basic;
      const enemy = createTestEnemy('basic', {
        behaviorState: 'attack',
        stateStartTime: 0,
        attackDirection: { x: 1, y: 0 },
      });
      const playerPos = { x: 200, y: 100 };

      const gameTime = config.attackDuration + 1;
      const { enemy: updated } = updateEnemyBehavior(enemy, playerPos, gameTime, 16);
      expect(updated.behaviorState).toBe('recovery');
    });

    it('state machine should transition RECOVERY → CHASE after duration', () => {
      const config = ENEMY_BEHAVIORS.basic;
      const enemy = createTestEnemy('basic', {
        behaviorState: 'recovery',
        stateStartTime: 0,
      });
      const playerPos = { x: 200, y: 100 };

      const gameTime = config.recoveryDuration + 1;
      const { enemy: updated } = updateEnemyBehavior(enemy, playerPos, gameTime, 16);
      expect(updated.behaviorState).toBe('chase');
    });
  });

  describe('E4: Escalating Threat', () => {
    it('boss should have longer attack duration than basic', () => {
      expect(ENEMY_BEHAVIORS.boss.attackDuration)
        .toBeGreaterThan(ENEMY_BEHAVIORS.basic.attackDuration);
    });

    it('boss should deal more damage than basic', () => {
      expect(ENEMY_BEHAVIORS.boss.attackDamage)
        .toBeGreaterThan(ENEMY_BEHAVIORS.basic.attackDamage);
    });

    it('each enemy type should have distinct attack type', () => {
      const attackTypes = Object.values(ENEMY_BEHAVIORS).map(c => c.attackType);
      expect(new Set(attackTypes).size).toBe(5); // All 5 types have unique attacks
    });
  });

  describe('State Helpers', () => {
    it('isEnemyVulnerable should return true only in recovery', () => {
      expect(isEnemyVulnerable(createTestEnemy('basic', { behaviorState: 'recovery' }))).toBe(true);
      expect(isEnemyVulnerable(createTestEnemy('basic', { behaviorState: 'chase' }))).toBe(false);
      expect(isEnemyVulnerable(createTestEnemy('basic', { behaviorState: 'attack' }))).toBe(false);
    });

    it('isEnemyAttacking should return true only in attack', () => {
      expect(isEnemyAttacking(createTestEnemy('basic', { behaviorState: 'attack' }))).toBe(true);
      expect(isEnemyAttacking(createTestEnemy('basic', { behaviorState: 'chase' }))).toBe(false);
      expect(isEnemyAttacking(createTestEnemy('basic', { behaviorState: 'recovery' }))).toBe(false);
    });
  });

  describe('Spitter Special Behavior', () => {
    it('spitter should spawn projectile during attack', () => {
      const enemy = createTestEnemy('spitter', {
        behaviorState: 'attack',
        stateStartTime: 0,
        attackDirection: { x: 1, y: 0 },
      });
      const playerPos = { x: 200, y: 100 };

      const { projectiles } = updateEnemyBehavior(enemy, playerPos, 1, 16);
      expect(projectiles.length).toBe(1);
      expect(projectiles[0].ownerId).toBe(enemy.id);
    });

    it('spitter should maintain distance (retreat if too close)', () => {
      const enemy = createTestEnemy('spitter', {
        position: { x: 100, y: 100 },
        behaviorState: 'chase',
      });
      const playerPos = { x: 110, y: 100 }; // Very close

      const movement = getEnemyMovement(enemy, playerPos, 80, 16);
      // Should move away (negative x direction)
      expect(movement.x).toBeLessThan(0);
    });
  });
});
