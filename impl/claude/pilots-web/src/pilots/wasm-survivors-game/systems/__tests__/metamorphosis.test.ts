/**
 * WASM Survivors - Metamorphosis System Tests
 *
 * Tests for PROTO_SPEC metamorphosis laws (Run 030):
 * - M-1: Predictable Timer - Players can learn when metamorphosis happens
 * - M-2: Visual Warning - Pulsing enemies are OBVIOUS
 * - M-3: Interruptible - Killing pulsing enemy resets nearby timers
 * - M-4: Escapable - Colossals can be run from
 * - M-5: Soloable - Every Colossal can be killed with base stats
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md §4 (Metamorphosis System)
 */

import { describe, it, expect } from 'vitest';
import {
  METAMORPHOSIS_CONFIG,
  updateSurvivalTime,
  calculatePulsingState,
  findSeekTarget,
  checkCombineCollision,
  createColossalTide,
  resetNearbyTimers,
} from '../metamorphosis';
import type { Enemy } from '@kgents/shared-primitives';

// =============================================================================
// Test Helpers
// =============================================================================

function createTestEnemy(overrides?: Partial<Enemy>): Enemy {
  return {
    id: `test-enemy-${Math.random().toString(36).slice(2)}`,
    type: 'basic',
    position: { x: 100, y: 100 },
    velocity: { x: 0, y: 0 },
    radius: 12,
    health: 20,
    maxHealth: 20,
    damage: 10,
    xpValue: 10,
    color: '#FF3366',
    behaviorState: 'chase',
    stateStartTime: 0,
    survivalTime: 0,
    pulsingState: 'normal',
    ...overrides,
  };
}

// =============================================================================
// M-1: Predictable Timer
// =============================================================================

describe('M-1: Predictable Timer', () => {
  describe('Survival Time Accumulator', () => {
    it('should initialize enemy with survivalTime = 0', () => {
      const enemy = createTestEnemy();
      expect(enemy.survivalTime).toBe(0);
    });

    it('should increment survivalTime by deltaTime (in seconds)', () => {
      const enemy = createTestEnemy({ survivalTime: 0 });
      const updated = updateSurvivalTime(enemy, 1); // 1 second
      expect(updated.survivalTime).toBe(1);
    });

    it('should accumulate survivalTime across multiple updates', () => {
      let enemy = createTestEnemy({ survivalTime: 0 });
      enemy = updateSurvivalTime(enemy, 1);    // 1s
      enemy = updateSurvivalTime(enemy, 0.5);  // 0.5s
      enemy = updateSurvivalTime(enemy, 0.25); // 0.25s
      expect(enemy.survivalTime).toBe(1.75);
    });
  });

  describe('State Thresholds (DD-030-1) - survivalTime in seconds', () => {
    it('should be normal at 0-9.999s', () => {
      const enemy = createTestEnemy({ survivalTime: 9.999 });
      expect(calculatePulsingState(enemy)).toBe('normal');
    });

    it('should transition to pulsing at exactly 10s', () => {
      const enemy = createTestEnemy({ survivalTime: 10 });
      expect(calculatePulsingState(enemy)).toBe('pulsing');
    });

    it('should remain pulsing at 14.999s', () => {
      const enemy = createTestEnemy({ survivalTime: 14.999 });
      expect(calculatePulsingState(enemy)).toBe('pulsing');
    });

    it('should transition to seeking at exactly 15s', () => {
      const enemy = createTestEnemy({ survivalTime: 15 });
      expect(calculatePulsingState(enemy)).toBe('seeking');
    });

    it('should remain seeking at 19.999s', () => {
      const enemy = createTestEnemy({ survivalTime: 19.999 });
      expect(calculatePulsingState(enemy)).toBe('seeking');
    });

    it('should allow combining at 20s+', () => {
      const enemy = createTestEnemy({ survivalTime: 20 });
      // Note: 'combining' requires collision, so this just checks eligibility
      expect(calculatePulsingState(enemy)).toBe('seeking'); // Still seeking until collision
    });
  });

  describe('Configuration Constants', () => {
    it('should have correct threshold values', () => {
      expect(METAMORPHOSIS_CONFIG.PULSE_THRESHOLD).toBe(10); // seconds
      expect(METAMORPHOSIS_CONFIG.SEEK_THRESHOLD).toBe(15);
      expect(METAMORPHOSIS_CONFIG.COMBINE_THRESHOLD).toBe(20);
    });
  });
});

// =============================================================================
// M-3: Interruptible
// =============================================================================

describe('M-3: Interruptible', () => {
  describe('Timer Reset on Kill', () => {
    it('should reset survivalTime of nearby enemies when pulsing enemy is killed', () => {
      const killedEnemy = createTestEnemy({
        position: { x: 100, y: 100 },
        survivalTime: 15, // seconds
        pulsingState: 'seeking',
      });

      const nearbyEnemy = createTestEnemy({
        id: 'nearby',
        position: { x: 150, y: 100 }, // Within TIMER_RESET_RADIUS (100)
        survivalTime: 12, // seconds
        pulsingState: 'pulsing',
      });

      const farEnemy = createTestEnemy({
        id: 'far',
        position: { x: 300, y: 300 }, // Beyond TIMER_RESET_RADIUS
        survivalTime: 18, // seconds
        pulsingState: 'seeking',
      });

      const enemies = [nearbyEnemy, farEnemy];
      const updated = resetNearbyTimers(enemies, killedEnemy.position);

      const updatedNearby = updated.find(e => e.id === 'nearby');
      const updatedFar = updated.find(e => e.id === 'far');

      expect(updatedNearby?.survivalTime).toBe(0);
      expect(updatedNearby?.pulsingState).toBe('normal');
      expect(updatedFar?.survivalTime).toBe(18); // Unchanged (seconds)
    });

    it('should use correct reset radius', () => {
      expect(METAMORPHOSIS_CONFIG.TIMER_RESET_RADIUS).toBe(100);
    });
  });
});

// =============================================================================
// Seeking Behavior
// =============================================================================

describe('Seeking Behavior', () => {
  describe('Target Selection', () => {
    it('should find nearest pulsing enemy as seek target', () => {
      const seeker = createTestEnemy({
        id: 'seeker',
        position: { x: 100, y: 100 },
        survivalTime: 15, // seconds
        pulsingState: 'seeking',
      });

      const nearTarget = createTestEnemy({
        id: 'near-target',
        position: { x: 150, y: 100 }, // Distance: 50
        survivalTime: 12, // seconds
        pulsingState: 'pulsing',
      });

      const farTarget = createTestEnemy({
        id: 'far-target',
        position: { x: 300, y: 100 }, // Distance: 200
        survivalTime: 14, // seconds
        pulsingState: 'pulsing',
      });

      const targetId = findSeekTarget(seeker, [seeker, nearTarget, farTarget]);
      expect(targetId).toBe('near-target');
    });

    it('should not target normal state enemies', () => {
      const seeker = createTestEnemy({
        id: 'seeker',
        survivalTime: 15, // seconds
        pulsingState: 'seeking',
      });

      const normalEnemy = createTestEnemy({
        id: 'normal',
        survivalTime: 5, // seconds
        pulsingState: 'normal',
      });

      const targetId = findSeekTarget(seeker, [seeker, normalEnemy]);
      expect(targetId).toBeNull();
    });

    it('should not target self', () => {
      const seeker = createTestEnemy({
        id: 'seeker',
        survivalTime: 15, // seconds
        pulsingState: 'seeking',
      });

      const targetId = findSeekTarget(seeker, [seeker]);
      expect(targetId).toBeNull();
    });
  });
});

// =============================================================================
// Combination Detection
// =============================================================================

describe('Combination Detection', () => {
  describe('Collision Check', () => {
    it('should detect when two seeking enemies collide', () => {
      const enemy1 = createTestEnemy({
        id: 'enemy-1',
        position: { x: 100, y: 100 },
        radius: 12,
        survivalTime: 20, // seconds
        pulsingState: 'seeking',
      });

      const enemy2 = createTestEnemy({
        id: 'enemy-2',
        position: { x: 120, y: 100 }, // Distance: 20, combined radius: 24 → collision
        radius: 12,
        survivalTime: 20, // seconds
        pulsingState: 'seeking',
      });

      const combinations = checkCombineCollision([enemy1, enemy2]);
      expect(combinations).not.toBeNull();
      expect(combinations!.length).toBe(1);
      expect(combinations![0]).toContain(enemy1);
      expect(combinations![0]).toContain(enemy2);
    });

    it('should not combine enemies that are too far apart', () => {
      const enemy1 = createTestEnemy({
        id: 'enemy-1',
        position: { x: 100, y: 100 },
        survivalTime: 20, // seconds
        pulsingState: 'seeking',
      });

      const enemy2 = createTestEnemy({
        id: 'enemy-2',
        position: { x: 200, y: 200 }, // Too far
        survivalTime: 20, // seconds
        pulsingState: 'seeking',
      });

      const combinations = checkCombineCollision([enemy1, enemy2]);
      expect(combinations).toBeNull();
    });

    it('should not combine enemies below COMBINE_THRESHOLD', () => {
      const enemy1 = createTestEnemy({
        survivalTime: 19, // Below 20s threshold (seconds)
        pulsingState: 'seeking',
      });

      const enemy2 = createTestEnemy({
        position: { x: 110, y: 100 }, // Close enough
        survivalTime: 19, // seconds
        pulsingState: 'seeking',
      });

      const combinations = checkCombineCollision([enemy1, enemy2]);
      expect(combinations).toBeNull();
    });
  });
});

// =============================================================================
// THE TIDE Creation (DD-030-4)
// =============================================================================

describe('THE TIDE Creation', () => {
  describe('Colossal Stats', () => {
    it('should create THE TIDE with 3x radius', () => {
      const enemies = [
        createTestEnemy({ position: { x: 100, y: 100 } }),
        createTestEnemy({ position: { x: 120, y: 100 } }),
      ];

      const tide = createColossalTide(enemies);
      expect(tide.radius).toBe(36); // 3x normal (12)
    });

    it('should create THE TIDE with 5x health', () => {
      const enemies = [
        createTestEnemy({ health: 20, maxHealth: 20 }),
        createTestEnemy({ health: 20, maxHealth: 20 }),
      ];

      const tide = createColossalTide(enemies);
      expect(tide.health).toBe(100); // 5x base (20)
      expect(tide.maxHealth).toBe(100);
    });

    it('should spawn at centroid of combining enemies', () => {
      const enemies = [
        createTestEnemy({ position: { x: 100, y: 100 } }),
        createTestEnemy({ position: { x: 200, y: 200 } }),
      ];

      const tide = createColossalTide(enemies);
      expect(tide.position.x).toBe(150); // Centroid
      expect(tide.position.y).toBe(150);
    });

    it('should have type colossal_tide', () => {
      const enemies = [createTestEnemy(), createTestEnemy()];
      const tide = createColossalTide(enemies);
      expect(tide.type).toBe('colossal_tide');
    });

    it('should have correct color (deep crimson)', () => {
      const enemies = [createTestEnemy(), createTestEnemy()];
      const tide = createColossalTide(enemies);
      expect(tide.color).toBe('#880000');
    });
  });
});

// =============================================================================
// Configuration Export
// =============================================================================

describe('Configuration', () => {
  it('should export all required config values', () => {
    expect(METAMORPHOSIS_CONFIG).toHaveProperty('PULSE_THRESHOLD');
    expect(METAMORPHOSIS_CONFIG).toHaveProperty('SEEK_THRESHOLD');
    expect(METAMORPHOSIS_CONFIG).toHaveProperty('COMBINE_THRESHOLD');
    expect(METAMORPHOSIS_CONFIG).toHaveProperty('SEEK_SPEED_BONUS');
    expect(METAMORPHOSIS_CONFIG).toHaveProperty('COMBINE_RADIUS');
    expect(METAMORPHOSIS_CONFIG).toHaveProperty('TIMER_RESET_RADIUS');
  });

  it('should have correct config values per DD-030-1', () => {
    expect(METAMORPHOSIS_CONFIG.PULSE_THRESHOLD).toBe(10);
    expect(METAMORPHOSIS_CONFIG.SEEK_THRESHOLD).toBe(15);
    expect(METAMORPHOSIS_CONFIG.COMBINE_THRESHOLD).toBe(20);
    expect(METAMORPHOSIS_CONFIG.SEEK_SPEED_BONUS).toBe(0.25);
  });
});
