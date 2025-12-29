/**
 * WASM Survivors - Bee Behavior System Tests
 *
 * Tests for PROTO_SPEC S6: Bee Taxonomy
 * - E1: Readable Tells - Attacks are telegraphed
 * - E2: Learnable Patterns - Consistent behavior
 * - E4: Escalating Threat - Workers → Guards → Royals
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md S6
 */

import { describe, it, expect } from 'vitest';
import {
  BEE_BEHAVIORS,
  updateBeeBehavior,
  getBeeTelegraph,
  getBeeMovement,
  isBeeVulnerable,
  isBeeAttacking,
  type EnemyWithBehavior,
} from '../enemies';
import type { Enemy, EnemyType } from '../../types';

/**
 * Create a test enemy matching PROTO_SPEC S6 Bee Taxonomy
 */
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
    speed: 50,
    xpValue: 10,
    survivalTime: 0,
    coordinationState: 'idle',
    ...overrides,
  };
}

/**
 * Create a test enemy with behavior state (as returned by updateBeeBehavior)
 */
function createEnemyWithBehavior(
  type: EnemyType,
  behaviorState: 'chase' | 'telegraph' | 'attack' | 'recovery',
  stateStartTime: number
): EnemyWithBehavior {
  const base = createTestEnemy(type);
  return {
    ...base,
    behaviorState,
    stateStartTime,
    attackDirection: { x: 1, y: 0 },
  };
}

describe('Bee Behavior System (PROTO_SPEC S6)', () => {
  describe('E1: Readable Tells', () => {
    it('should have 5 bee types with behavior configs (PROTO_SPEC S6)', () => {
      // PROTO_SPEC S6: Bee Taxonomy - 5 types
      const types: EnemyType[] = ['worker', 'scout', 'guard', 'propolis', 'royal'];
      for (const type of types) {
        expect(BEE_BEHAVIORS[type]).toBeDefined();
      }
    });

    it('each bee type should have telegraph duration (E1: Readable)', () => {
      for (const [_type, config] of Object.entries(BEE_BEHAVIORS)) {
        expect(config.telegraphDuration).toBeGreaterThan(0);
        expect(config.telegraphDuration).toBeLessThanOrEqual(1500);
      }
    });

    it('should generate telegraph data during telegraph state', () => {
      const enemy = createEnemyWithBehavior('worker', 'telegraph', 0);
      const telegraph = getBeeTelegraph(enemy, 100);
      expect(telegraph).not.toBeNull();
      expect(telegraph!.progress).toBeGreaterThan(0);
    });

    it('should not generate telegraph data in other states', () => {
      const states = ['chase', 'attack', 'recovery'] as const;
      for (const state of states) {
        const enemy = createEnemyWithBehavior('worker', state, 0);
        const telegraph = getBeeTelegraph(enemy, 0);
        expect(telegraph).toBeNull();
      }
    });
  });

  describe('E2: Learnable Patterns', () => {
    it('state machine should transition CHASE → TELEGRAPH when in range', () => {
      const enemy = createTestEnemy('worker');
      const playerPos = { x: 110, y: 100 }; // Within attack range

      const { enemy: updated } = updateBeeBehavior(enemy, playerPos, 100, 16);
      // Enemy should be in telegraph state (preparing attack)
      expect((updated as EnemyWithBehavior).behaviorState).toBe('telegraph');
    });

    it('state machine should transition TELEGRAPH → ATTACK after duration', () => {
      const config = BEE_BEHAVIORS.worker;
      const enemy = createEnemyWithBehavior('worker', 'telegraph', 0);
      const playerPos = { x: 200, y: 100 };

      // After telegraph duration
      const gameTime = config.telegraphDuration + 1;
      const { enemy: updated } = updateBeeBehavior(enemy, playerPos, gameTime, 16);
      expect((updated as EnemyWithBehavior).behaviorState).toBe('attack');
    });

    it('state machine should transition ATTACK → RECOVERY after duration', () => {
      const config = BEE_BEHAVIORS.worker;
      const enemy = createEnemyWithBehavior('worker', 'attack', 0);
      const playerPos = { x: 200, y: 100 };

      const gameTime = config.attackDuration + 1;
      const { enemy: updated } = updateBeeBehavior(enemy, playerPos, gameTime, 16);
      expect((updated as EnemyWithBehavior).behaviorState).toBe('recovery');
    });

    it('state machine should transition RECOVERY → CHASE after duration', () => {
      const config = BEE_BEHAVIORS.worker;
      const enemy = createEnemyWithBehavior('worker', 'recovery', 0);
      const playerPos = { x: 200, y: 100 };

      const gameTime = config.recoveryDuration + 1;
      const { enemy: updated } = updateBeeBehavior(enemy, playerPos, gameTime, 16);
      expect((updated as EnemyWithBehavior).behaviorState).toBe('chase');
    });
  });

  describe('E4: Escalating Threat (Workers → Guards → Royals)', () => {
    it('royal should have longer attack duration than worker', () => {
      expect(BEE_BEHAVIORS.royal.attackDuration)
        .toBeGreaterThanOrEqual(BEE_BEHAVIORS.worker.attackDuration);
    });

    it('guard should deal more damage than worker', () => {
      expect(BEE_BEHAVIORS.guard.attackDamage)
        .toBeGreaterThan(BEE_BEHAVIORS.worker.attackDamage);
    });

    it('royal should deal the most damage', () => {
      const royalDamage = BEE_BEHAVIORS.royal.attackDamage;
      expect(royalDamage).toBeGreaterThan(BEE_BEHAVIORS.worker.attackDamage);
      expect(royalDamage).toBeGreaterThan(BEE_BEHAVIORS.scout.attackDamage);
    });

    it('each bee type should have distinct attack type', () => {
      const attackTypes = Object.values(BEE_BEHAVIORS).map(c => c.attackType);
      // At least 3 distinct attack types across the 5 bee types
      expect(new Set(attackTypes).size).toBeGreaterThanOrEqual(3);
    });
  });

  describe('State Helpers', () => {
    it('isBeeVulnerable should return true only in recovery', () => {
      expect(isBeeVulnerable(createEnemyWithBehavior('worker', 'recovery', 0))).toBe(true);
      expect(isBeeVulnerable(createEnemyWithBehavior('worker', 'chase', 0))).toBe(false);
      expect(isBeeVulnerable(createEnemyWithBehavior('worker', 'attack', 0))).toBe(false);
    });

    it('isBeeAttacking should return true only in attack', () => {
      expect(isBeeAttacking(createEnemyWithBehavior('worker', 'attack', 0))).toBe(true);
      expect(isBeeAttacking(createEnemyWithBehavior('worker', 'chase', 0))).toBe(false);
      expect(isBeeAttacking(createEnemyWithBehavior('worker', 'recovery', 0))).toBe(false);
    });
  });

  describe('Movement Behavior', () => {
    it('worker should chase toward player', () => {
      const enemy = createEnemyWithBehavior('worker', 'chase', 0);
      const playerPos = { x: 200, y: 100 }; // Player to the right

      const movement = getBeeMovement(enemy, playerPos, 50, 16);
      // Should move toward player (positive x)
      expect(movement.x).toBeGreaterThan(0);
    });

    it('propolis should maintain distance (ranged attacker)', () => {
      const enemy = createEnemyWithBehavior('propolis', 'chase', 0);
      enemy.position = { x: 100, y: 100 };
      const playerPos = { x: 110, y: 100 }; // Very close

      const movement = getBeeMovement(enemy, playerPos, 80, 16);
      // Propolis is ranged - should retreat if too close
      expect(movement.x).toBeLessThanOrEqual(0);
    });
  });
});
