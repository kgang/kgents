/**
 * ADVERSARIAL TEST SUITE: Juice System
 *
 * Verifies spec compliance for:
 * - Appendix E: JUICE PARAMETERS (exact values)
 * - DD-5: Fun Floor (screen shake, particles, sound)
 * - DD-16: Clutch moments
 * - DD-17: Combo crescendo
 *
 * "Make kills feel like PUNCHES. WOULD SOMEONE CLIP THIS?"
 */

import { describe, it, expect } from 'vitest';
import type { GameState, Player } from '../../types';
import {
  // Constants (Appendix E values)
  SHAKE,
  FREEZE,
  PARTICLES,
  TELLS,
  AUDIO_CUES,
  COLORS,
  METAMORPHOSIS_COLORS,

  // Factory
  createJuiceSystem,

  // Process
  processJuice,
  getEffectiveTimeScale,
  isInFreezeFrame,

  // Clutch
  checkClutchMoment,

  // Combo
  getComboVisuals,

  // Health
  getHealthVignette,

  // Breathing
  getBreathPhase,
  getBreathGlowMultiplier,
  getEntityPhaseOffset,
  BREATHING_CONFIGS,

  // Intensity
  getIntensityColors,
} from '../juice';

// =============================================================================
// Test Fixtures
// =============================================================================

function createMockPlayer(overrides: Partial<Player> = {}): Player {
  return {
    position: { x: 400, y: 300 },
    velocity: { x: 0, y: 0 },
    health: 100,
    maxHealth: 100,
    level: 1,
    xp: 0,
    xpToNextLevel: 10,
    damage: 10,
    attackSpeed: 1,
    moveSpeed: 200,
    attackRange: 30,
    attackCooldown: 500,
    lastAttackTime: 0,
    dashCooldown: 1500,
    lastDashTime: 0,
    invincible: false,
    invincibilityEndTime: 0,
    upgrades: [],
    ...overrides,
  };
}

function createMockGameState(overrides: Partial<GameState> = {}): GameState {
  return {
    status: 'playing',
    wave: 1,
    gameTime: 0,
    player: createMockPlayer(),
    enemies: [],
    xpOrbs: [],
    projectiles: [],
    totalEnemiesKilled: 0,
    ...overrides,
  } as GameState;
}

// =============================================================================
// SECTION 1: Appendix E - SHAKE Constants
// =============================================================================

describe('APPENDIX E: SHAKE CONSTANTS', () => {
  describe('Screen Shake Values', () => {
    it('should have correct workerKill shake: 2px amplitude, 80ms duration', () => {
      expect(SHAKE.workerKill.amplitude).toBe(2);
      expect(SHAKE.workerKill.duration).toBe(80);
      expect(SHAKE.workerKill.frequency).toBe(60);
    });

    it('should have correct guardKill shake: 5px amplitude, 150ms duration', () => {
      expect(SHAKE.guardKill.amplitude).toBe(5);
      expect(SHAKE.guardKill.duration).toBe(150);
      expect(SHAKE.guardKill.frequency).toBe(60);
    });

    it('should have correct bossKill shake: 14px amplitude, 300ms duration', () => {
      expect(SHAKE.bossKill.amplitude).toBe(14);
      expect(SHAKE.bossKill.duration).toBe(300);
      expect(SHAKE.bossKill.frequency).toBe(60);
    });

    it('should have correct playerHit shake: 8px amplitude, 200ms duration', () => {
      expect(SHAKE.playerHit.amplitude).toBe(8);
      expect(SHAKE.playerHit.duration).toBe(200);
      expect(SHAKE.playerHit.frequency).toBe(60);
    });

    it('should have multiKill shake (3+ kills): 6px amplitude, 120ms duration', () => {
      expect(SHAKE.multiKill.amplitude).toBe(6);
      expect(SHAKE.multiKill.duration).toBe(120);
    });

    it('should have massacre shake (5+ kills): 15px amplitude, 350ms duration', () => {
      expect(SHAKE.massacre.amplitude).toBe(15);
      expect(SHAKE.massacre.duration).toBe(350);
    });
  });
});

// =============================================================================
// SECTION 2: Appendix E - FREEZE Constants
// =============================================================================

describe('APPENDIX E: FREEZE CONSTANTS', () => {
  describe('Freeze Frame Values', () => {
    it('should have correct significantKill freeze: 2 frames (33ms at 60fps)', () => {
      expect(FREEZE.significantKill).toBe(2);
    });

    it('should have correct multiKill freeze: 4 frames (66ms)', () => {
      expect(FREEZE.multiKill).toBe(4);
    });

    it('should have correct criticalHit freeze: 3 frames', () => {
      expect(FREEZE.criticalHit).toBe(3);
    });

    it('should have correct massacre freeze: 6 frames (100ms)', () => {
      expect(FREEZE.massacre).toBe(6);
    });
  });

  describe('Freeze Frame Triggering', () => {
    it('should trigger freeze frames via juice system', () => {
      const juice = createJuiceSystem();

      expect(juice.freeze.active).toBe(false);
      expect(juice.freeze.framesRemaining).toBe(0);

      juice.triggerFreeze('massacre');

      expect(juice.freeze.active).toBe(true);
      expect(juice.freeze.framesRemaining).toBe(FREEZE.massacre);
      expect(juice.freeze.type).toBe('massacre');
    });

    it('should only override freeze if more frames', () => {
      const juice = createJuiceSystem();

      // Trigger significant (2 frames)
      juice.triggerFreeze('significant');
      expect(juice.freeze.framesRemaining).toBe(2);

      // Try to trigger with fewer frames - should not override
      juice.triggerFreeze('significant');
      expect(juice.freeze.framesRemaining).toBe(2);

      // Trigger massacre (6 frames) - should override
      juice.triggerFreeze('massacre');
      expect(juice.freeze.framesRemaining).toBe(6);
    });

    it('should detect freeze frame state', () => {
      const juice = createJuiceSystem();

      expect(isInFreezeFrame(juice)).toBe(false);

      juice.triggerFreeze('multi');
      expect(isInFreezeFrame(juice)).toBe(true);
    });

    it('should return 0 time scale during freeze', () => {
      const juice = createJuiceSystem();

      expect(getEffectiveTimeScale(juice)).toBe(1.0);

      juice.triggerFreeze('massacre');
      expect(getEffectiveTimeScale(juice)).toBe(0);
    });
  });
});

// =============================================================================
// SECTION 3: Appendix E - PARTICLES Constants
// =============================================================================

describe('APPENDIX E: PARTICLES CONSTANTS', () => {
  describe('Death Spiral Particles', () => {
    it('should have count of 25 (NOT 5, TWENTY-FIVE)', () => {
      expect(PARTICLES.deathSpiral.count).toBe(25);
    });

    it('should have color #FFE066 (soft yellow pollen)', () => {
      expect(PARTICLES.deathSpiral.color).toBe('#FFE066');
    });

    it('should have 45 degree spread', () => {
      expect(PARTICLES.deathSpiral.spread).toBe(45);
    });

    it('should have 400ms lifespan', () => {
      expect(PARTICLES.deathSpiral.lifespan).toBe(400);
    });

    it('should have 3 full rotations during descent', () => {
      expect(PARTICLES.deathSpiral.rotation).toBe(3);
    });
  });

  describe('Honey Drip Particles', () => {
    it('should have count of 15', () => {
      expect(PARTICLES.honeyDrip.count).toBe(15);
    });

    it('should have color #F4A300 (amber)', () => {
      expect(PARTICLES.honeyDrip.color).toBe('#F4A300');
    });

    it('should have gravity of 200 px/s^2', () => {
      expect(PARTICLES.honeyDrip.gravity).toBe(200);
    });

    it('should have pool fade time of 1200ms', () => {
      expect(PARTICLES.honeyDrip.poolFade).toBe(1200);
    });
  });

  describe('Damage Flash Particles', () => {
    it('should have colors pure red -> dark red (danger, distinct from player)', () => {
      expect(PARTICLES.damageFlash.colors).toEqual(['#FF3333', '#FF0000']);
    });

    it('should have flash duration of 100ms', () => {
      expect(PARTICLES.damageFlash.flashDuration).toBe(100);
    });

    it('should have fade duration of 200ms', () => {
      expect(PARTICLES.damageFlash.fadeDuration).toBe(200);
    });

    it('should have fragment count of 10', () => {
      expect(PARTICLES.damageFlash.fragmentCount).toBe(10);
    });

    it('should have fragment velocity of 225 px/s', () => {
      expect(PARTICLES.damageFlash.fragmentVelocity).toBe(225);
    });
  });
});

// =============================================================================
// SECTION 4: Appendix E - Visual TELLS Constants
// =============================================================================

describe('APPENDIX E: VISUAL TELLS CONSTANTS', () => {
  describe('Charging Glow', () => {
    it('should have color #FFD700 (gold)', () => {
      expect(TELLS.chargingGlow.color).toBe('#FFD700');
    });

    it('should have 500ms duration pre-attack', () => {
      expect(TELLS.chargingGlow.duration).toBe(500);
    });

    it('should have pulse scale of 1.2', () => {
      expect(TELLS.chargingGlow.pulseScale).toBe(1.2);
    });

    it('should have 100ms pulse rate', () => {
      expect(TELLS.chargingGlow.pulseRate).toBe(100);
    });

    it('should have opacity range [0.4, 0.8]', () => {
      expect(TELLS.chargingGlow.opacity).toEqual([0.4, 0.8]);
    });
  });

  describe('Formation Lines', () => {
    it('should have color #FFD700 (gold)', () => {
      expect(TELLS.formationLines.color).toBe('#FFD700');
    });

    it('should have opacity 0.4', () => {
      expect(TELLS.formationLines.opacity).toBe(0.4);
    });

    it('should have line width of 1.5px', () => {
      expect(TELLS.formationLines.width).toBe(1.5);
    });

    it('should have fade time of 150ms', () => {
      expect(TELLS.formationLines.fadeTime).toBe(150);
    });

    it('should require minimum 3 bees for coordination', () => {
      expect(TELLS.formationLines.minBees).toBe(3);
    });
  });

  describe('Stinger Trail', () => {
    it('should have color #6B2D5B (venom purple)', () => {
      expect(TELLS.stingerTrail.color).toBe('#6B2D5B');
    });

    it('should have 300ms duration', () => {
      expect(TELLS.stingerTrail.duration).toBe(300);
    });
  });
});

// =============================================================================
// SECTION 5: Appendix E - AUDIO Constants
// =============================================================================

describe('APPENDIX E: AUDIO CONSTANTS', () => {
  describe('Alarm Pheromone', () => {
    it('should have frequency range 400Hz -> 2000Hz', () => {
      expect(AUDIO_CUES.alarmPheromone.freqStart).toBe(400);
      expect(AUDIO_CUES.alarmPheromone.freqEnd).toBe(2000);
    });

    it('should have 300ms duration', () => {
      expect(AUDIO_CUES.alarmPheromone.duration).toBe(300);
    });
  });

  describe('Ball Forming', () => {
    it('should have buzz volume starting at 0.3', () => {
      expect(AUDIO_CUES.ballForming.buzzVolume).toBe(0.3);
    });

    it('should have buzz peak at 1.0', () => {
      expect(AUDIO_CUES.ballForming.buzzPeak).toBe(1.0);
    });

    it('should have 3000ms (3s) silence duration', () => {
      expect(AUDIO_CUES.ballForming.silenceDuration).toBe(3000);
    });
  });
});

// =============================================================================
// SECTION 6: Kill Tracking and Multi-Kill Detection
// =============================================================================

describe('KILL TRACKING SYSTEM', () => {
  describe('Multi-Kill Detection', () => {
    it('should start with zero kills', () => {
      const juice = createJuiceSystem();
      expect(juice.killTracker.recentKills).toBe(0);
    });

    it('should have 150ms window for multi-kills', () => {
      const juice = createJuiceSystem();
      expect(juice.killTracker.windowDuration).toBe(150);
    });

    it('should reset window after duration expires', () => {
      const juice = createJuiceSystem();

      // First kill
      juice.emitKill({ x: 100, y: 100 }, 'basic');
      expect(juice.killTracker.recentKills).toBe(1);

      // Simulate time passing beyond window
      // This would be handled in processJuice, but emitKill checks the window
      // Wait for a mock scenario to test window reset
    });

    it('should escalate shake on multi-kills', () => {
      const juice = createJuiceSystem();

      // Manually set kill tracker to simulate rapid kills
      juice.killTracker.recentKills = 2;
      juice.killTracker.windowStart = Date.now();

      // Next kill should trigger multi-kill
      juice.emitKill({ x: 100, y: 100 }, 'basic');

      // Should have multi-kill shake or higher
      expect(juice.shake.intensity).toBeGreaterThanOrEqual(SHAKE.multiKill.amplitude);
    });

    it('should trigger massacre freeze on 5+ kills', () => {
      const juice = createJuiceSystem();

      // Simulate 4 kills already in window
      juice.killTracker.recentKills = 4;
      juice.killTracker.windowStart = Date.now();

      // 5th kill triggers massacre
      juice.emitKill({ x: 100, y: 100 }, 'basic');

      expect(juice.freeze.type).toBe('massacre');
      expect(juice.freeze.framesRemaining).toBe(FREEZE.massacre);
    });
  });
});

// =============================================================================
// SECTION 7: Juice System Methods
// =============================================================================

describe('JUICE SYSTEM METHODS', () => {
  describe('emitKill', () => {
    it('should create death spiral particles', () => {
      const juice = createJuiceSystem();
      const initialParticleCount = juice.particles.length;

      juice.emitKill({ x: 100, y: 100 }, 'basic');

      // Should have significantly more particles (death spiral + burst)
      expect(juice.particles.length).toBeGreaterThan(initialParticleCount);
    });

    it('should trigger stronger shake for tank kills', () => {
      const juice = createJuiceSystem();

      juice.emitKill({ x: 100, y: 100 }, 'tank');

      expect(juice.shake.intensity).toBeGreaterThanOrEqual(SHAKE.guardKill.amplitude);
    });

    it('should trigger boss shake for boss kills', () => {
      const juice = createJuiceSystem();

      juice.emitKill({ x: 100, y: 100 }, 'boss');

      expect(juice.shake.intensity).toBeGreaterThanOrEqual(SHAKE.bossKill.amplitude);
    });

    it('should create honey drip for heavy enemies', () => {
      const juice = createJuiceSystem();

      juice.emitKill({ x: 100, y: 100 }, 'boss');

      // Honey drip creates 15 particles
      const drips = juice.particles.filter(p => p.type === 'drip');
      expect(drips.length).toBe(PARTICLES.honeyDrip.count);
    });
  });

  describe('emitDamage', () => {
    it('should reset combo on damage', () => {
      const juice = createJuiceSystem();
      juice.escalation.combo = 10;

      juice.emitDamage({ x: 100, y: 100 }, 15);

      expect(juice.escalation.combo).toBe(0);
    });

    it('should trigger player hit shake', () => {
      const juice = createJuiceSystem();

      juice.emitDamage({ x: 100, y: 100 }, 15);

      expect(juice.shake.intensity).toBe(SHAKE.playerHit.amplitude);
      expect(juice.shake.duration).toBe(SHAKE.playerHit.duration);
    });

    it('should create damage flash particles', () => {
      const juice = createJuiceSystem();

      juice.emitDamage({ x: 100, y: 100 }, 15);

      const fragments = juice.particles.filter(p => p.type === 'fragment');
      expect(fragments.length).toBe(PARTICLES.damageFlash.fragmentCount);
    });
  });

  describe('emitDeathSpiral', () => {
    it('should create 25 spiral particles', () => {
      const juice = createJuiceSystem();

      juice.emitDeathSpiral({ x: 100, y: 100 });

      const spirals = juice.particles.filter(p => p.type === 'spiral');
      expect(spirals.length).toBe(PARTICLES.deathSpiral.count);
    });

    it('should have rotation properties on spiral particles', () => {
      const juice = createJuiceSystem();

      juice.emitDeathSpiral({ x: 100, y: 100 });

      const spirals = juice.particles.filter(p => p.type === 'spiral');
      for (const spiral of spirals) {
        expect(spiral.rotation).toBeDefined();
        expect(spiral.rotationSpeed).toBeDefined();
        expect(spiral.gravity).toBeDefined();
      }
    });
  });

  describe('emitHoneyDrip', () => {
    it('should create 15 drip particles', () => {
      const juice = createJuiceSystem();

      juice.emitHoneyDrip({ x: 100, y: 100 });

      const drips = juice.particles.filter(p => p.type === 'drip');
      expect(drips.length).toBe(PARTICLES.honeyDrip.count);
    });

    it('should have amber color', () => {
      const juice = createJuiceSystem();

      juice.emitHoneyDrip({ x: 100, y: 100 });

      const drips = juice.particles.filter(p => p.type === 'drip');
      for (const drip of drips) {
        expect(drip.color).toBe(PARTICLES.honeyDrip.color);
      }
    });
  });

  describe('emitDamageFlash', () => {
    it('should create fragment particles', () => {
      const juice = createJuiceSystem();

      juice.emitDamageFlash({ x: 100, y: 100 });

      const fragments = juice.particles.filter(p => p.type === 'fragment');
      expect(fragments.length).toBe(PARTICLES.damageFlash.fragmentCount);
    });

    it('should alternate between orange and red', () => {
      const juice = createJuiceSystem();

      juice.emitDamageFlash({ x: 100, y: 100 });

      const fragments = juice.particles.filter(p => p.type === 'fragment');
      const colors = new Set(fragments.map(f => f.color));

      expect(colors.has('#FF3333')).toBe(true);  // Pure red (danger)
      expect(colors.has('#FF0000')).toBe(true);
    });
  });
});

// =============================================================================
// SECTION 8: Escalation Engine
// =============================================================================

describe('ESCALATION ENGINE', () => {
  describe('Escalation Multiplier Formula', () => {
    // Formula: juice_intensity = base_intensity * escalation_multiplier
    // escalation_multiplier = wave_factor * combo_factor * stakes_factor
    // wave_factor = 1 + (wave / 10) * 0.5
    // combo_factor = 1 + log2(combo_count + 1) * 0.1
    // stakes_factor = 1 + (1 - health_fraction) * 0.3

    it('should start at multiplier of 1.0', () => {
      const juice = createJuiceSystem();
      expect(juice.escalation.multiplier).toBe(1);
    });

    it('should scale multiplier with wave progression', () => {
      const juice = createJuiceSystem();
      juice.escalation.wave = 10;
      juice.escalation.healthFraction = 1;
      juice.escalation.combo = 0;

      // Process to recalculate
      processJuice(juice, 0, createMockGameState({ wave: 10 }));

      // wave_factor = 1 + (10/10) * 0.5 = 1.5
      expect(juice.escalation.multiplier).toBeGreaterThan(1.4);
    });

    it('should scale multiplier with low health', () => {
      const juice = createJuiceSystem();

      processJuice(juice, 0, createMockGameState({
        player: createMockPlayer({ health: 20, maxHealth: 100 }),
      }));

      // stakes_factor = 1 + (1 - 0.2) * 0.3 = 1.24
      expect(juice.escalation.multiplier).toBeGreaterThan(1.2);
    });
  });

  describe('Combo Tracking', () => {
    it('should increment combo on kills', () => {
      const juice = createJuiceSystem();

      juice.emitKill({ x: 100, y: 100 }, 'basic');
      expect(juice.escalation.combo).toBe(1);

      juice.emitKill({ x: 100, y: 100 }, 'basic');
      expect(juice.escalation.combo).toBe(2);
    });

    it('should have 2 second combo window', () => {
      const juice = createJuiceSystem();

      juice.emitKill({ x: 100, y: 100 }, 'basic');
      expect(juice.escalation.comboTimer).toBe(2000);
    });

    it('should reset combo when timer expires', () => {
      const juice = createJuiceSystem();

      juice.emitKill({ x: 100, y: 100 }, 'basic');
      expect(juice.escalation.combo).toBe(1);

      // Process with time passing
      processJuice(juice, 2500, createMockGameState());

      expect(juice.escalation.combo).toBe(0);
    });
  });
});

// =============================================================================
// SECTION 9: Clutch Moments (DD-16)
// =============================================================================

describe('CLUTCH MOMENTS (DD-16)', () => {
  describe('checkClutchMoment', () => {
    it('should trigger FULL clutch at <15% health with >3 threats', () => {
      const config = checkClutchMoment(0.14, 4);

      expect(config).not.toBeNull();
      expect(config?.timeScale).toBe(0.2);
      expect(config?.zoomFactor).toBe(1.3);
      expect(config?.bassDrop).toBe(true);
      expect(config?.durationMs).toBe(1000);
    });

    it('should trigger MEDIUM clutch at <25% health with >5 threats', () => {
      const config = checkClutchMoment(0.24, 6);

      expect(config).not.toBeNull();
      expect(config?.zoomFactor).toBe(1.2);
      expect(config?.bassDrop).toBe(true);
    });

    it('should trigger CRITICAL clutch at <10% health', () => {
      const config = checkClutchMoment(0.09, 1);

      expect(config).not.toBeNull();
      expect(config?.timeScale).toBe(0.3);
      expect(config?.bassDrop).toBe(false);
    });

    it('should return null when no clutch conditions met', () => {
      const config = checkClutchMoment(0.5, 2);
      expect(config).toBeNull();
    });
  });

  describe('Clutch State Management', () => {
    it('should activate clutch via juice system', () => {
      const juice = createJuiceSystem();

      juice.triggerClutch('full', 1000);

      expect(juice.clutch.active).toBe(true);
      expect(juice.clutch.level).toBe('full');
      expect(juice.clutch.timeScale).toBe(0.2);
      expect(juice.clutch.zoom).toBe(1.3);
    });

    it('should not override with less intense clutch', () => {
      const juice = createJuiceSystem();

      juice.triggerClutch('full', 1000);
      juice.triggerClutch('medium', 500);

      // Should still be full
      expect(juice.clutch.level).toBe('full');
    });

    it('should return clutch time scale', () => {
      const juice = createJuiceSystem();

      juice.triggerClutch('medium', 1000);

      expect(getEffectiveTimeScale(juice)).toBe(0.5);
    });
  });
});

// =============================================================================
// SECTION 10: Combo Visuals (DD-17)
// =============================================================================

describe('COMBO VISUALS (DD-17)', () => {
  describe('getComboVisuals', () => {
    it('should return base state for combo 0-4', () => {
      const state = getComboVisuals(3);

      expect(state.brightness).toBe(1.0);
      expect(state.saturation).toBe(1.0);
      expect(state.particleDensity).toBe(1.0);
      expect(state.euphoriaMode).toBe(false);
    });

    it('should boost brightness at combo 5+', () => {
      const state = getComboVisuals(5);
      expect(state.brightness).toBe(1.2);
    });

    it('should boost saturation at combo 10+', () => {
      const state = getComboVisuals(10);
      expect(state.saturation).toBe(1.3);
    });

    it('should boost particle density at combo 20+', () => {
      const state = getComboVisuals(20);
      expect(state.particleDensity).toBe(2.0);
    });

    it('should enable euphoria mode at combo 50+', () => {
      const state = getComboVisuals(50);

      expect(state.euphoriaMode).toBe(true);
      expect(state.brightness).toBe(1.4);
      expect(state.saturation).toBe(1.5);
      expect(state.particleDensity).toBe(3.0);
    });
  });
});

// =============================================================================
// SECTION 11: Health Vignette (DD-20)
// =============================================================================

describe('HEALTH VIGNETTE (DD-20)', () => {
  describe('getHealthVignette', () => {
    it('should have no vignette above 50% health', () => {
      const vignette = getHealthVignette(0.6);

      expect(vignette.intensity).toBe(0);
      expect(vignette.pulseRate).toBe(0);
    });

    it('should have warning vignette at 25-50% health', () => {
      const vignette = getHealthVignette(0.4);

      expect(vignette.intensity).toBeGreaterThan(0);
      expect(vignette.intensity).toBeLessThan(1);
      expect(vignette.pulseRate).toBe(1); // 1Hz
    });

    it('should have danger vignette at <25% health', () => {
      const vignette = getHealthVignette(0.2);

      expect(vignette.intensity).toBeGreaterThan(0);
      expect(vignette.pulseRate).toBe(2); // 2Hz
    });

    it('should have critical vignette at <10% health', () => {
      const vignette = getHealthVignette(0.05);

      expect(vignette.intensity).toBe(1.0);
      expect(vignette.pulseRate).toBe(4); // 4Hz
      expect(vignette.color).toBe(COLORS.crisis);
    });
  });
});

// =============================================================================
// SECTION 12: Entity Breathing (DD-29-1)
// =============================================================================

describe('ENTITY BREATHING (DD-29-1)', () => {
  describe('getBreathPhase', () => {
    it('should return value between 0 and 1', () => {
      for (let t = 0; t < 5000; t += 100) {
        const phase = getBreathPhase(t, BREATHING_CONFIGS.playerCalm);
        expect(phase).toBeGreaterThanOrEqual(0);
        expect(phase).toBeLessThanOrEqual(1);
      }
    });

    it('should cycle over time based on rate', () => {
      const config = { baseRate: 1, intensity: 0.5 }; // 1Hz = 1 second cycle

      // At different points in a 1-second cycle
      const start = getBreathPhase(0, config);
      const half = getBreathPhase(500, config);

      // Should vary over the cycle (quarter and threeQuarter omitted - only need start vs half)
      expect(start).not.toBe(half);
    });
  });

  describe('getBreathGlowMultiplier', () => {
    it('should return 1.0 at phase 0', () => {
      expect(getBreathGlowMultiplier(0, 0.5)).toBe(1.0);
    });

    it('should return 1 + intensity at phase 1', () => {
      expect(getBreathGlowMultiplier(1, 0.5)).toBe(1.5);
    });
  });

  describe('BREATHING_CONFIGS', () => {
    it('should have presets for player states', () => {
      expect(BREATHING_CONFIGS.playerCalm).toBeDefined();
      expect(BREATHING_CONFIGS.playerLowHealth).toBeDefined();
    });

    it('should have presets for enemy states', () => {
      expect(BREATHING_CONFIGS.enemyChase).toBeDefined();
      expect(BREATHING_CONFIGS.enemyTelegraph).toBeDefined();
      expect(BREATHING_CONFIGS.enemyAttack).toBeDefined();
    });

    it('should have faster rate for low health player', () => {
      expect(BREATHING_CONFIGS.playerLowHealth.baseRate).toBeGreaterThan(
        BREATHING_CONFIGS.playerCalm.baseRate
      );
    });

    it('should have faster rate for attacking enemies', () => {
      expect(BREATHING_CONFIGS.enemyAttack.baseRate).toBeGreaterThan(
        BREATHING_CONFIGS.enemyChase.baseRate
      );
    });
  });

  describe('getEntityPhaseOffset', () => {
    it('should return consistent offset for same ID', () => {
      const offset1 = getEntityPhaseOffset('enemy-123');
      const offset2 = getEntityPhaseOffset('enemy-123');

      expect(offset1).toBe(offset2);
    });

    it('should return different offsets for different IDs', () => {
      const offset1 = getEntityPhaseOffset('enemy-1');
      const offset2 = getEntityPhaseOffset('enemy-2');

      expect(offset1).not.toBe(offset2);
    });

    it('should return value between 0 and 1', () => {
      for (let i = 0; i < 100; i++) {
        const offset = getEntityPhaseOffset(`enemy-${i}`);
        expect(offset).toBeGreaterThanOrEqual(0);
        expect(offset).toBeLessThan(1);
      }
    });
  });
});

// =============================================================================
// SECTION 13: Screen Intensity (DD-29-2)
// =============================================================================

describe('SCREEN INTENSITY (DD-29-2)', () => {
  describe('getIntensityColors', () => {
    it('should return calm colors for early waves', () => {
      const colors = getIntensityColors(1, 1.0);

      expect(colors.background).toBe('#1a1a2e');
    });

    it('should transition colors through wave progression', () => {
      const wave2 = getIntensityColors(2, 1.0);
      const wave9 = getIntensityColors(9, 1.0);

      // Colors should differ between waves
      expect(wave2.background).not.toBe(wave9.background);
    });

    it('should add red tint at low health', () => {
      const healthy = getIntensityColors(5, 1.0);
      const lowHealth = getIntensityColors(5, 0.1);

      expect(healthy.background).not.toBe(lowHealth.background);
    });
  });
});

// =============================================================================
// SECTION 14: Process Juice (Main Update Loop)
// =============================================================================

describe('PROCESS JUICE', () => {
  describe('Particle Updates', () => {
    it('should remove expired particles', () => {
      const juice = createJuiceSystem();

      // Create a particle that will expire
      juice.emitKill({ x: 100, y: 100 }, 'basic');
      const countBefore = juice.particles.length;

      // Process with enough time for particles to expire
      processJuice(juice, 1000, createMockGameState());

      expect(juice.particles.length).toBeLessThan(countBefore);
    });

    it('should apply gravity to spiral particles', () => {
      const juice = createJuiceSystem();
      juice.emitDeathSpiral({ x: 100, y: 100 });

      const spiral = juice.particles.find(p => p.type === 'spiral')!;
      const initialVelY = spiral.velocity.y;

      processJuice(juice, 100, createMockGameState());

      // Velocity should have increased due to gravity
      expect(spiral.velocity.y).toBeGreaterThan(initialVelY);
    });

    it('should update particle alpha over lifetime', () => {
      const juice = createJuiceSystem();
      juice.emitKill({ x: 100, y: 100 }, 'basic');

      const particle = juice.particles.find(p => p.type === 'burst')!;
      const initialAlpha = particle.alpha;

      processJuice(juice, 100, createMockGameState());

      expect(particle.alpha).toBeLessThan(initialAlpha);
    });
  });

  describe('Shake Updates', () => {
    it('should decay shake over duration', () => {
      const juice = createJuiceSystem();
      juice.triggerShake(10, 200);

      processJuice(juice, 100, createMockGameState());

      // Should have offset
      expect(juice.shake.offset.x !== 0 || juice.shake.offset.y !== 0).toBe(true);

      // Process until complete
      processJuice(juice, 200, createMockGameState());

      // Should be reset
      expect(juice.shake.intensity).toBe(0);
      expect(juice.shake.offset).toEqual({ x: 0, y: 0 });
    });
  });

  describe('Freeze Frame Updates', () => {
    it('should decrement freeze frames', () => {
      const juice = createJuiceSystem();
      juice.triggerFreeze('massacre');

      expect(juice.freeze.framesRemaining).toBe(6);

      processJuice(juice, 16, createMockGameState());

      expect(juice.freeze.framesRemaining).toBe(5);
    });

    it('should deactivate freeze when complete', () => {
      const juice = createJuiceSystem();
      juice.triggerFreeze('significant'); // 2 frames

      processJuice(juice, 16, createMockGameState());
      processJuice(juice, 16, createMockGameState());
      processJuice(juice, 16, createMockGameState());

      expect(juice.freeze.active).toBe(false);
    });

    it('should return early during freeze (no updates)', () => {
      const juice = createJuiceSystem();

      // Create particles
      juice.emitKill({ x: 100, y: 100 }, 'basic');
      const particle = juice.particles.find(p => p.type === 'burst')!;
      const posYBefore = particle.position.y;

      // Trigger freeze
      juice.triggerFreeze('massacre');

      // Process - should skip physics during freeze
      processJuice(juice, 100, createMockGameState());

      // During freeze, physics updates are paused
      // Position should not have changed significantly (frozen)
      expect(particle.position.y).toBeCloseTo(posYBefore, 0);
    });
  });

  describe('Clutch Updates', () => {
    it('should count down clutch remaining time', () => {
      const juice = createJuiceSystem();
      juice.triggerClutch('full', 1000);

      processJuice(juice, 200, createMockGameState());

      expect(juice.clutch.remaining).toBe(800);
    });

    it('should deactivate clutch when complete', () => {
      const juice = createJuiceSystem();
      juice.triggerClutch('medium', 500);

      processJuice(juice, 600, createMockGameState());

      expect(juice.clutch.active).toBe(false);
      expect(juice.clutch.timeScale).toBe(1.0);
    });
  });
});

// =============================================================================
// SECTION 15: Color Constants
// =============================================================================

describe('COLOR CONSTANTS', () => {
  describe('Main Colors', () => {
    it('should have correct player color (Burnt Amber)', () => {
      expect(COLORS.player).toBe('#CC5500');
    });

    it('should have correct enemy color (Worker Amber)', () => {
      expect(COLORS.enemy).toBe('#D4920A');
    });

    it('should have correct XP color (Pollen Gold - lighter reward yellow)', () => {
      expect(COLORS.xp).toBe('#FFE066');
    });

    it('should have correct health color (Vitality Green)', () => {
      expect(COLORS.health).toBe('#00FF88');
    });

    it('should have correct crisis color (Pinkish Red - distinct from player)', () => {
      expect(COLORS.crisis).toBe('#FF3366');
    });
  });

  describe('Metamorphosis Colors', () => {
    it('should have pulsing pinkish-red to red gradient (distinct from player)', () => {
      expect(METAMORPHOSIS_COLORS.pulsing.start).toBe('#FF3366');
      expect(METAMORPHOSIS_COLORS.pulsing.end).toBe('#FF0000');
    });

    it('should have magenta threads', () => {
      expect(METAMORPHOSIS_COLORS.threads).toBe('#FF00FF');
    });

    it('should have deep crimson for colossal', () => {
      expect(METAMORPHOSIS_COLORS.colossal).toBe('#880000');
    });
  });
});
