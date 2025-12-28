/**
 * WASM Survivors - Breathing System Tests (DD-29-1)
 *
 * Tests for the entity breathing visual system:
 * - Breath phase calculation
 * - Glow multipliers
 * - Entity phase offsets
 * - Performance requirements
 */

import { describe, it, expect } from 'vitest';
import {
  getBreathPhase,
  getBreathGlowMultiplier,
  getBreathAlphaMultiplier,
  getEntityPhaseOffset,
  BREATHING_CONFIGS,
  getIntensityColors,
} from '../juice';

describe('Entity Breathing System (DD-29-1)', () => {
  describe('getBreathPhase', () => {
    it('should return values between 0 and 1', () => {
      const config = { baseRate: 1.0, intensity: 0.5 };

      // Test over multiple time points
      for (let t = 0; t < 2000; t += 50) {
        const phase = getBreathPhase(t, config);
        expect(phase).toBeGreaterThanOrEqual(0);
        expect(phase).toBeLessThanOrEqual(1);
      }
    });

    it('should complete one cycle per second at 1 Hz', () => {
      const config = { baseRate: 1.0, intensity: 0.5 };

      // At t=0, phase should be at minimum (0)
      const phase0 = getBreathPhase(0, config);

      // At t=500ms, phase should be at maximum (1)
      const phase500 = getBreathPhase(500, config);

      // At t=1000ms, should be back to start
      const phase1000 = getBreathPhase(1000, config);

      // Check the cycle shape
      expect(phase0).toBeCloseTo(0, 1);
      expect(phase500).toBeCloseTo(1, 1);
      expect(phase1000).toBeCloseTo(0, 1);
    });

    it('faster rates should complete cycles faster', () => {
      const slowConfig = { baseRate: 0.5, intensity: 0.5 };
      const fastConfig = { baseRate: 2.0, intensity: 0.5 };

      // At t=250ms, fast rate (2Hz) should be at peak, slow rate should be mid-rise
      const slowPhase = getBreathPhase(250, slowConfig);
      const fastPhase = getBreathPhase(250, fastConfig);

      expect(fastPhase).toBeCloseTo(1, 1); // Fast is at peak
      expect(slowPhase).toBeLessThan(0.8); // Slow is still rising
    });

    it('phase offset should desync entities', () => {
      const config1 = { baseRate: 1.0, intensity: 0.5, phaseOffset: 0 };
      const config2 = { baseRate: 1.0, intensity: 0.5, phaseOffset: 0.5 };

      // At same time, different offsets should give different phases
      const phase1 = getBreathPhase(0, config1);
      const phase2 = getBreathPhase(0, config2);

      expect(phase1).not.toBeCloseTo(phase2, 1);
    });
  });

  describe('getBreathGlowMultiplier', () => {
    it('should return 1.0 at minimum breath phase', () => {
      const multiplier = getBreathGlowMultiplier(0, 0.5);
      expect(multiplier).toBe(1.0);
    });

    it('should return > 1.0 at maximum breath phase', () => {
      const multiplier = getBreathGlowMultiplier(1, 0.5);
      expect(multiplier).toBe(1.5);
    });

    it('higher intensity should produce larger multiplier', () => {
      const lowIntensity = getBreathGlowMultiplier(1, 0.2);
      const highIntensity = getBreathGlowMultiplier(1, 0.6);

      expect(highIntensity).toBeGreaterThan(lowIntensity);
    });
  });

  describe('getBreathAlphaMultiplier', () => {
    it('should return minimum 0.6 at zero phase', () => {
      const multiplier = getBreathAlphaMultiplier(0, 1.0);
      expect(multiplier).toBeCloseTo(0.6, 2);
    });

    it('should return up to 1.0 at full phase with full intensity', () => {
      const multiplier = getBreathAlphaMultiplier(1, 1.0);
      expect(multiplier).toBeCloseTo(1.0, 2);
    });

    it('low intensity should limit alpha variation', () => {
      const lowIntensity = getBreathAlphaMultiplier(1, 0.2);
      expect(lowIntensity).toBeLessThan(0.9);
    });
  });

  describe('getEntityPhaseOffset', () => {
    it('should return consistent values for same ID', () => {
      const offset1 = getEntityPhaseOffset('enemy-123');
      const offset2 = getEntityPhaseOffset('enemy-123');
      expect(offset1).toBe(offset2);
    });

    it('should return different values for different IDs', () => {
      const offset1 = getEntityPhaseOffset('enemy-123');
      const offset2 = getEntityPhaseOffset('enemy-456');
      expect(offset1).not.toBe(offset2);
    });

    it('should return values between 0 and 1', () => {
      const testIds = ['a', 'abc', 'enemy-1', 'player-1', 'proj-xyz'];
      for (const id of testIds) {
        const offset = getEntityPhaseOffset(id);
        expect(offset).toBeGreaterThanOrEqual(0);
        expect(offset).toBeLessThan(1);
      }
    });
  });

  describe('BREATHING_CONFIGS presets', () => {
    it('should have player configs', () => {
      expect(BREATHING_CONFIGS.playerCalm).toBeDefined();
      expect(BREATHING_CONFIGS.playerLowHealth).toBeDefined();
    });

    it('player low health should be faster than calm', () => {
      expect(BREATHING_CONFIGS.playerLowHealth.baseRate)
        .toBeGreaterThan(BREATHING_CONFIGS.playerCalm.baseRate);
    });

    it('should have enemy state configs', () => {
      expect(BREATHING_CONFIGS.enemyChase).toBeDefined();
      expect(BREATHING_CONFIGS.enemyTelegraph).toBeDefined();
      expect(BREATHING_CONFIGS.enemyRecovery).toBeDefined();
      expect(BREATHING_CONFIGS.enemyAttack).toBeDefined();
    });

    it('enemy telegraph should be faster than chase', () => {
      expect(BREATHING_CONFIGS.enemyTelegraph.baseRate)
        .toBeGreaterThan(BREATHING_CONFIGS.enemyChase.baseRate);
    });

    it('enemy recovery should be slowest', () => {
      expect(BREATHING_CONFIGS.enemyRecovery.baseRate)
        .toBeLessThan(BREATHING_CONFIGS.enemyChase.baseRate);
    });
  });

  describe('Performance', () => {
    it('breath phase calculation should be fast', () => {
      const config = { baseRate: 1.0, intensity: 0.5 };

      const start = performance.now();
      for (let i = 0; i < 1000; i++) {
        getBreathPhase(i * 16, config);
      }
      const elapsed = performance.now() - start;

      // 1000 calculations should take < 1ms
      expect(elapsed).toBeLessThan(1);
    });
  });
});

describe('Screen Intensity System (DD-29-2)', () => {
  describe('getIntensityColors', () => {
    it('should return calm colors for early waves', () => {
      const colors = getIntensityColors(1, 1.0);
      expect(colors.background).toBe('#1a1a2e');
    });

    it('should return crisis colors for late waves', () => {
      const colors = getIntensityColors(10, 1.0);
      expect(colors.background).toBe('#281a2e');
    });

    it('should transition smoothly between waves 3-5', () => {
      const wave3 = getIntensityColors(3, 1.0);
      const wave4 = getIntensityColors(4, 1.0);
      const wave5 = getIntensityColors(5, 1.0);

      // Colors should be different but valid hex
      expect(wave3.background).toMatch(/^#[0-9a-f]{6}$/);
      expect(wave4.background).toMatch(/^#[0-9a-f]{6}$/);
      expect(wave5.background).toMatch(/^#[0-9a-f]{6}$/);

      // Should progress toward tense
      expect(wave3.background).not.toBe(wave5.background);
    });

    it('should add red tint at low health', () => {
      const fullHealth = getIntensityColors(5, 1.0);
      const lowHealth = getIntensityColors(5, 0.1);

      // Low health background should be more red
      expect(fullHealth.background).not.toBe(lowHealth.background);
    });

    it('should not add red tint above 25% health', () => {
      const colors30 = getIntensityColors(5, 0.3);
      const colors100 = getIntensityColors(5, 1.0);

      // Both should be same (no red tint threshold)
      expect(colors30.background).toBe(colors100.background);
    });
  });

  describe('Performance', () => {
    it('intensity calculation should be fast', () => {
      const start = performance.now();
      for (let wave = 1; wave <= 20; wave++) {
        for (let health = 0; health <= 100; health += 5) {
          getIntensityColors(wave, health / 100);
        }
      }
      const elapsed = performance.now() - start;

      // Should complete in < 5ms
      expect(elapsed).toBeLessThan(5);
    });
  });
});
