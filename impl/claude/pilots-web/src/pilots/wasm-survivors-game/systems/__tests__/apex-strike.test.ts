/**
 * WASM Survivors - Apex Strike Tests
 *
 * Tests for the hornet's signature predator dash mechanic.
 *
 * DESIGN PHILOSOPHY:
 * > "The hornet doesn't dash - it HUNTS. The strike is commitment."
 *
 * Tests verify:
 * - State machine transitions (LOCK -> STRIKE -> HIT/MISS -> CHAIN/RECOVERY)
 * - Hit detection during strike phase
 * - Bloodlust accumulation and damage bonus
 * - Chain window mechanics
 * - Cooldown after miss
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  type ApexStrikeState,
  type ApexTarget,
  createInitialApexState,
  initiateLock,
  updateLockDirection,
  executeStrike,
  checkStrikeHit,
  onStrikeHit,
  onStrikeMiss,
  attemptChain,
  updateApexStrike,
  canApex,
  canChain,
  isStriking,
  isLocking,
  isVulnerable,
  isUnstoppable,
  getStrikeVelocity,
  getBloodlustPercent,
  getBloodlustDamageMultiplier,
  APEX_CONFIG,
} from '../apex-strike';

describe('Apex Strike System', () => {
  let initialState: ApexStrikeState;

  beforeEach(() => {
    initialState = createInitialApexState();
  });

  describe('Initial State', () => {
    it('should start in ready phase', () => {
      expect(initialState.phase).toBe('ready');
    });

    it('should have zero bloodlust', () => {
      expect(initialState.bloodlust).toBe(0);
    });

    it('should have no cooldown', () => {
      expect(initialState.cooldownRemaining).toBe(0);
    });

    it('should be able to apex from initial state', () => {
      expect(canApex(initialState)).toBe(true);
    });
  });

  describe('Lock Phase', () => {
    it('should transition to lock phase when initiating', () => {
      const result = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      expect(result.state.phase).toBe('lock');
    });

    it('should emit lock_started event', () => {
      const result = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      expect(result.events).toHaveLength(1);
      expect(result.events[0].type).toBe('lock_started');
    });

    it('should update lock direction', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const updateResult = updateLockDirection(lockResult.state, { x: 0, y: 1 });
      expect(updateResult.state.lockDirection?.y).toBeCloseTo(1, 2);
    });

    it('should be vulnerable during lock', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      expect(isVulnerable(lockResult.state)).toBe(true);
      expect(isLocking(lockResult.state)).toBe(true);
    });
  });

  describe('Strike Phase', () => {
    it('should transition to strike phase', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );
      expect(strikeResult.state.phase).toBe('strike');
    });

    it('should emit strike_launched event', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );
      expect(strikeResult.events).toHaveLength(1);
      expect(strikeResult.events[0].type).toBe('strike_launched');
    });

    it('should have high velocity during strike', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );
      const velocity = getStrikeVelocity(strikeResult.state);
      expect(velocity.x).toBeGreaterThan(2000); // 12x base speed of 200
    });

    it('should be unstoppable during strike', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );
      expect(isUnstoppable(strikeResult.state)).toBe(true);
      expect(isStriking(strikeResult.state)).toBe(true);
    });
  });

  describe('Hit Detection', () => {
    it('should detect hit when overlapping enemy', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );

      const targets: ApexTarget[] = [
        { id: 'enemy1', position: { x: 110, y: 100 }, radius: 15, health: 50 },
      ];

      const hitResult = checkStrikeHit(
        strikeResult.state,
        { x: 105, y: 100 }, // Player close to enemy
        targets,
        0
      );

      expect(hitResult.hitEnemy).not.toBeNull();
      expect(hitResult.damage).toBeGreaterThan(0);
    });

    it('should not detect hit when enemies are far', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );

      const targets: ApexTarget[] = [
        { id: 'enemy1', position: { x: 500, y: 500 }, radius: 15, health: 50 },
      ];

      const hitResult = checkStrikeHit(
        strikeResult.state,
        { x: 105, y: 100 },
        targets,
        0
      );

      expect(hitResult.hitEnemy).toBeNull();
    });
  });

  describe('Bloodlust System', () => {
    it('should gain bloodlust on hit', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );

      const enemy: ApexTarget = {
        id: 'enemy1',
        position: { x: 110, y: 100 },
        radius: 15,
        health: 50,
      };

      const hitResult = onStrikeHit(
        strikeResult.state,
        enemy,
        { x: 105, y: 100 },
        0
      );

      expect(hitResult.state.bloodlust).toBe(APEX_CONFIG.bloodlustGain);
    });

    it('should cap bloodlust at max', () => {
      let state = initialState;
      state = { ...state, bloodlust: 95 };

      const lockResult = initiateLock(state, { x: 1, y: 0 }, { x: 100, y: 100 }, 0);
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );

      const enemy: ApexTarget = {
        id: 'enemy1',
        position: { x: 110, y: 100 },
        radius: 15,
        health: 50,
      };

      const hitResult = onStrikeHit(
        strikeResult.state,
        enemy,
        { x: 105, y: 100 },
        0
      );

      expect(hitResult.state.bloodlust).toBe(APEX_CONFIG.bloodlustMax);
    });

    it('should provide damage bonus at max bloodlust', () => {
      const maxBloodlustState = { ...initialState, bloodlust: 100 };
      const multiplier = getBloodlustDamageMultiplier(maxBloodlustState);
      expect(multiplier).toBe(APEX_CONFIG.bloodlustDamageBonus);
    });

    it('should return 0-1 for bloodlust percent', () => {
      const halfBloodlust = { ...initialState, bloodlust: 50 };
      const percent = getBloodlustPercent(halfBloodlust);
      expect(percent).toBe(0.5);
    });
  });

  describe('Chain System', () => {
    it('should allow chain after hit', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );

      const enemy: ApexTarget = {
        id: 'enemy1',
        position: { x: 110, y: 100 },
        radius: 15,
        health: 50,
      };

      const hitResult = onStrikeHit(
        strikeResult.state,
        enemy,
        { x: 105, y: 100 },
        0
      );

      expect(hitResult.state.canChain).toBe(true);
      expect(hitResult.state.chainWindow).toBeGreaterThan(0);
      expect(canChain(hitResult.state)).toBe(true);
    });

    it('should chain into new lock phase', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );

      const enemy: ApexTarget = {
        id: 'enemy1',
        position: { x: 110, y: 100 },
        radius: 15,
        health: 50,
      };

      const hitResult = onStrikeHit(
        strikeResult.state,
        enemy,
        { x: 105, y: 100 },
        0
      );

      const chainResult = attemptChain(
        hitResult.state,
        { x: 0, y: 1 },
        { x: 105, y: 100 },
        0
      );

      expect(chainResult.state.phase).toBe('lock');
    });
  });

  describe('Miss and Cooldown', () => {
    it('should enter miss_recovery on miss', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );

      const missResult = onStrikeMiss(strikeResult.state, { x: 460, y: 100 }, 0);
      expect(missResult.state.phase).toBe('miss_recovery');
    });

    it('should start cooldown on miss', () => {
      const lockResult = initiateLock(
        initialState,
        { x: 1, y: 0 },
        { x: 100, y: 100 },
        0
      );
      const strikeResult = executeStrike(
        lockResult.state,
        { x: 100, y: 100 },
        { x: 1, y: 0 },
        0
      );

      const missResult = onStrikeMiss(strikeResult.state, { x: 460, y: 100 }, 0);
      expect(missResult.state.cooldownRemaining).toBe(APEX_CONFIG.baseCooldown);
    });

    it('should not be able to apex during cooldown', () => {
      const stateWithCooldown = { ...initialState, cooldownRemaining: 1000 };
      expect(canApex(stateWithCooldown)).toBe(false);
    });
  });

  describe('Update Loop', () => {
    it('should decay bloodlust when ready', () => {
      const stateWithBloodlust = { ...initialState, bloodlust: 100 };
      const result = updateApexStrike(
        stateWithBloodlust,
        1000, // 1 second
        { x: 100, y: 100 },
        0
      );
      expect(result.state.bloodlust).toBeLessThan(100);
    });

    it('should decrease cooldown over time', () => {
      const stateWithCooldown = {
        ...initialState,
        phase: 'ready' as const,
        cooldownRemaining: 1000,
      };
      const result = updateApexStrike(
        stateWithCooldown,
        500,
        { x: 100, y: 100 },
        0
      );
      expect(result.state.cooldownRemaining).toBe(500);
    });
  });
});
