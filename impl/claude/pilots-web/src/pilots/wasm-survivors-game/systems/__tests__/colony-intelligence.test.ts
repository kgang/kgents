/**
 * Colony Intelligence System Tests
 *
 * Tests for the superorganism: pheromone grid, colony memory, and adaptive behavior.
 *
 * Key verifications:
 * - Pheromones decay and diffuse correctly
 * - Colony learns player patterns
 * - Adaptive gap placement challenges learned patterns
 * - V5: WITNESSED - death screen data is collaborative, not judgmental
 */

import { describe, it, expect } from 'vitest';

// Pheromone Grid
import {
  createPheromoneGrid,
  depositAlarmAtAttack,
  depositPlayerTrail,
  depositDeathMark,
  updatePheromoneGrid,
  readPheromones,
  getBeeMovementModifier,
  shouldJoinFormation,
  PHEROMONE_CONFIG,
} from '../pheromone-grid';

// Colony Memory
import {
  createColonyMemory,
  recordDash,
  recordKill,
  recordBallEncounter,
  recordEscapeAttempt,
  getAdaptiveGapAngle,
  getCoordinationSpeedMultiplier,
  getDeathScreenLearnings,
} from '../colony-memory';

// Colony Intelligence (central controller)
import {
  createColonyIntelligence,
  updateColonyIntelligence,
  onPlayerDash,
  getBeeIntelligence,
  getAdaptiveBallGapAngle,
  getColonyDeathScreenData,
  COLONY_CONFIG,
} from '../colony-intelligence';

// =============================================================================
// Pheromone Grid Tests
// =============================================================================

describe('PheromoneGrid', () => {
  describe('createPheromoneGrid', () => {
    it('creates a grid with correct dimensions', () => {
      const grid = createPheromoneGrid(800, 600);
      expect(grid.arenaWidth).toBe(800);
      expect(grid.arenaHeight).toBe(600);
      expect(grid.cellSize).toBe(PHEROMONE_CONFIG.cellSize);
      expect(grid.width).toBe(Math.ceil(800 / PHEROMONE_CONFIG.cellSize));
      expect(grid.height).toBe(Math.ceil(600 / PHEROMONE_CONFIG.cellSize));
    });

    it('initializes all cells to zero intensity', () => {
      const grid = createPheromoneGrid(800, 600);
      for (const row of grid.cells) {
        for (const cell of row) {
          expect(cell.alarm).toBe(0);
          expect(cell.trail).toBe(0);
          expect(cell.death).toBe(0);
          expect(cell.coordination).toBe(0);
        }
      }
    });
  });

  describe('depositAlarmAtAttack', () => {
    it('deposits alarm pheromone at attack position', () => {
      let grid = createPheromoneGrid(800, 600);
      grid = depositAlarmAtAttack(grid, { x: 400, y: 300 }, 1000);

      const reading = readPheromones(grid, { x: 400, y: 300 });
      expect(reading.alarm).toBeGreaterThan(0);
      expect(reading.alarm).toBeLessThanOrEqual(1);
    });
  });

  describe('depositPlayerTrail', () => {
    it('deposits trail pheromone with direction', () => {
      let grid = createPheromoneGrid(800, 600);
      grid = depositPlayerTrail(
        grid,
        { x: 400, y: 300 },
        { x: 100, y: 0 }, // Moving right
        1000
      );

      const reading = readPheromones(grid, { x: 400, y: 300 });
      expect(reading.trail).toBeGreaterThan(0);
      expect(reading.trailDirection).not.toBeNull();
      if (reading.trailDirection) {
        expect(reading.trailDirection.x).toBeGreaterThan(0);
      }
    });

    it('does not deposit trail if moving too slow', () => {
      let grid = createPheromoneGrid(800, 600);
      grid = depositPlayerTrail(
        grid,
        { x: 400, y: 300 },
        { x: 5, y: 0 }, // Moving very slow
        1000
      );

      const reading = readPheromones(grid, { x: 400, y: 300 });
      expect(reading.trail).toBe(0);
    });
  });

  describe('depositDeathMark', () => {
    it('deposits death pheromone at max intensity', () => {
      let grid = createPheromoneGrid(800, 600);
      grid = depositDeathMark(grid, { x: 400, y: 300 }, 'bee-1', 1000);

      const reading = readPheromones(grid, { x: 400, y: 300 });
      expect(reading.death).toBe(PHEROMONE_CONFIG.deposit.death);
    });
  });

  describe('updatePheromoneGrid', () => {
    it('decays pheromones over time', () => {
      let grid = createPheromoneGrid(800, 600);
      grid = depositAlarmAtAttack(grid, { x: 400, y: 300 }, 1000);

      const initialReading = readPheromones(grid, { x: 400, y: 300 });
      const initialAlarm = initialReading.alarm;

      // Update with 1 second delta
      grid = updatePheromoneGrid(grid, 1000, 2000);

      const updatedReading = readPheromones(grid, { x: 400, y: 300 });
      expect(updatedReading.alarm).toBeLessThan(initialAlarm);
    });
  });

  describe('getBeeMovementModifier', () => {
    it('returns speed multiplier based on alarm', () => {
      const reading = {
        alarm: 0.5,
        trail: 0,
        death: 0,
        coordination: 0,
        trailDirection: null,
        strongestType: 'alarm' as const,
        gradient: { x: 0, y: 0 },
      };

      const modifier = getBeeMovementModifier(reading);
      expect(modifier.speedMultiplier).toBeGreaterThan(1);
    });

    it('returns avoidance vector when death pheromone is high', () => {
      const reading = {
        alarm: 0,
        trail: 0,
        death: 0.6,
        coordination: 0,
        trailDirection: null,
        strongestType: 'death' as const,
        gradient: { x: 1, y: 0 },
      };

      const modifier = getBeeMovementModifier(reading);
      expect(modifier.avoidanceVector.x).not.toBe(0);
    });
  });

  describe('shouldJoinFormation', () => {
    it('returns true when coordination is above threshold', () => {
      const reading = {
        alarm: 0,
        trail: 0,
        death: 0,
        coordination: 0.8,
        trailDirection: null,
        strongestType: 'coordination' as const,
        gradient: { x: 0, y: 0 },
      };

      expect(shouldJoinFormation(reading)).toBe(true);
    });

    it('returns false when coordination is below threshold', () => {
      const reading = {
        alarm: 0,
        trail: 0,
        death: 0,
        coordination: 0.3,
        trailDirection: null,
        strongestType: null,
        gradient: { x: 0, y: 0 },
      };

      expect(shouldJoinFormation(reading)).toBe(false);
    });
  });
});

// =============================================================================
// Colony Memory Tests
// =============================================================================

describe('ColonyMemory', () => {
  describe('createColonyMemory', () => {
    it('creates memory with zero knowledge', () => {
      const memory = createColonyMemory(0);
      expect(memory.adaptationLevel).toBe(0);
      expect(memory.preferredDashDirection).toBeNull();
      expect(memory.detectedArchetype).toBe('unknown');
      expect(memory.ballsEncountered).toBe(0);
    });
  });

  describe('recordDash', () => {
    it('tracks dash direction patterns', () => {
      let memory = createColonyMemory(0);

      // Record 5 dashes to the east
      for (let i = 0; i < 6; i++) {
        memory = recordDash(
          memory,
          { x: 400, y: 300 },
          { x: 500, y: 300 }, // East
          i * 1000
        );
      }

      expect(memory.dashHistory.length).toBe(6);
      expect(memory.preferredDashDirection).toBe('east');
      expect(memory.dashDirectionConfidence).toBeGreaterThan(0.5);
    });

    it('increases adaptation level when pattern is detected', () => {
      let memory = createColonyMemory(0);

      for (let i = 0; i < 6; i++) {
        memory = recordDash(
          memory,
          { x: 400, y: 300 },
          { x: 500, y: 300 },
          i * 1000
        );
      }

      expect(memory.adaptationLevel).toBeGreaterThan(0);
    });

    it('creates learning when pattern is detected', () => {
      let memory = createColonyMemory(0);

      for (let i = 0; i < 8; i++) {
        memory = recordDash(
          memory,
          { x: 400, y: 300 },
          { x: 500, y: 300 },
          i * 1000
        );
      }

      const movementLearning = memory.learnings.find(l => l.type === 'movement');
      expect(movementLearning).toBeDefined();
      expect(movementLearning?.description).toContain('east');
    });
  });

  describe('recordKill', () => {
    it('tracks kills per minute and aggression', () => {
      let memory = createColonyMemory(0);

      // Record 30 kills in first minute
      for (let i = 0; i < 30; i++) {
        memory = recordKill(memory, i * 2000);
      }

      // Rolling window is capped at 20 samples
      expect(memory.killsPerMinute.count).toBe(20);
      expect(memory.aggressionLevel).toBeGreaterThan(0);
    });
  });

  describe('recordEscapeAttempt', () => {
    it('tracks escape patterns', () => {
      let memory = createColonyMemory(0);

      // Escape to the north three times
      for (let i = 0; i < 3; i++) {
        memory = recordEscapeAttempt(
          memory,
          { x: 400, y: 300 }, // ball center
          { x: 400, y: 200 }, // player position (north)
          0, // gap angle
          true, // success
          i * 5000
        );
      }

      expect(memory.escapeHistory.length).toBe(3);
      expect(memory.preferredEscapeDirection).not.toBeNull();
      expect(memory.ballsEscaped).toBe(3);
    });
  });

  describe('getAdaptiveGapAngle', () => {
    it('returns default angle when no data', () => {
      const memory = createColonyMemory(0);
      const adapted = getAdaptiveGapAngle(memory, Math.PI);
      expect(adapted).toBe(Math.PI);
    });

    it('adapts angle based on escape patterns', () => {
      let memory = createColonyMemory(0);
      memory = recordBallEncounter(memory, { x: 400, y: 300 }, 0, 1000);
      memory = recordBallEncounter(memory, { x: 400, y: 300 }, 0, 2000);

      // Escape east multiple times
      for (let i = 0; i < 3; i++) {
        memory = recordEscapeAttempt(
          memory,
          { x: 400, y: 300 },
          { x: 500, y: 300 }, // east
          0,
          true,
          (i + 3) * 5000
        );
      }

      const defaultAngle = 0;
      const adapted = getAdaptiveGapAngle(memory, defaultAngle);

      // Adapted angle should be different from default
      expect(adapted).not.toBe(defaultAngle);
    });
  });

  describe('getCoordinationSpeedMultiplier', () => {
    it('returns higher multiplier for aggressive players', () => {
      let memory = createColonyMemory(0);

      // High kill rate
      for (let i = 0; i < 40; i++) {
        memory = recordKill(memory, i * 1500);
      }

      const speedMod = getCoordinationSpeedMultiplier(memory);
      expect(speedMod).toBeGreaterThan(1);
    });
  });

  describe('getDeathScreenLearnings - V5: WITNESSED', () => {
    it('provides collaborative headline for low adaptation', () => {
      const memory = createColonyMemory(0);
      const deathData = getDeathScreenLearnings(memory);

      expect(deathData.headline).toContain('overwhelmed');
      expect(deathData.headline).not.toContain('predictable');
    });

    it('provides collaborative headline for high adaptation', () => {
      let memory = createColonyMemory(0);
      memory = { ...memory, adaptationLevel: 7 };

      const deathData = getDeathScreenLearnings(memory);
      expect(deathData.headline).toContain('predicted');
    });
  });
});

// =============================================================================
// Colony Intelligence (Central Controller) Tests
// =============================================================================

describe('ColonyIntelligence', () => {
  describe('createColonyIntelligence', () => {
    it('creates combined intelligence state', () => {
      const intelligence = createColonyIntelligence(800, 600, 0);

      expect(intelligence.pheromoneGrid).toBeDefined();
      expect(intelligence.memory).toBeDefined();
      expect(intelligence.adaptationActive).toBe(false);
    });
  });

  describe('updateColonyIntelligence', () => {
    it('updates grid and records position', () => {
      let intelligence = createColonyIntelligence(800, 600, 0);

      const result = updateColonyIntelligence(
        intelligence,
        { x: 400, y: 300 },
        { x: 100, y: 0 },
        800, 600,
        1000, 16
      );

      expect(result.intelligence).toBeDefined();
      expect(result.events).toBeInstanceOf(Array);
    });

    it('emits anticipation_activated event when threshold reached', () => {
      let intelligence = createColonyIntelligence(800, 600, 0);
      intelligence = {
        ...intelligence,
        memory: {
          ...intelligence.memory,
          adaptationLevel: COLONY_CONFIG.adaptationActivationThreshold,
        },
      };

      const result = updateColonyIntelligence(
        intelligence,
        { x: 400, y: 300 },
        { x: 100, y: 0 },
        800, 600,
        1000, 16
      );

      const activationEvent = result.events.find(
        e => e.type === 'anticipation_activated'
      );
      expect(activationEvent).toBeDefined();
    });
  });

  describe('onPlayerDash', () => {
    it('records dash and emits learning event when pattern detected', () => {
      let intelligence = createColonyIntelligence(800, 600, 0);

      // Record 8 dashes to the east
      for (let i = 0; i < 8; i++) {
        const result = onPlayerDash(
          intelligence,
          { x: 400, y: 300 },
          { x: 500, y: 300 },
          i * 1000
        );
        intelligence = result.intelligence;
      }

      // Should have learned the pattern
      expect(intelligence.memory.preferredDashDirection).toBe('east');
    });
  });

  describe('getBeeIntelligence', () => {
    it('returns intelligence data for a bee', () => {
      const intelligence = createColonyIntelligence(800, 600, 0);

      const beeIntel = getBeeIntelligence(
        intelligence,
        { x: 200, y: 150 },
        { x: 400, y: 300 },
        { x: 50, y: 0 }
      );

      expect(beeIntel.reading).toBeDefined();
      expect(beeIntel.speedMultiplier).toBeGreaterThanOrEqual(1);
      expect(beeIntel.anticipatedTarget).toBeDefined();
    });
  });

  describe('getAdaptiveBallGapAngle', () => {
    it('returns default angle when not adapted', () => {
      const intelligence = createColonyIntelligence(800, 600, 0);
      const defaultAngle = Math.PI / 2;

      const result = getAdaptiveBallGapAngle(intelligence, defaultAngle);
      expect(result.angle).toBe(defaultAngle);
      expect(result.isAdapted).toBe(false);
    });
  });

  describe('getColonyDeathScreenData', () => {
    it('returns V5-compliant death screen data', () => {
      const intelligence = createColonyIntelligence(800, 600, 0);

      const deathData = getColonyDeathScreenData(intelligence);

      expect(deathData.headline).toBeDefined();
      expect(deathData.learnings).toBeInstanceOf(Array);
      expect(deathData.runSummary).toBeDefined();

      // Verify V5: headline is collaborative, not judgmental
      expect(deathData.headline).not.toContain('predictable');
      expect(deathData.headline).not.toContain('bad');
      expect(deathData.headline).not.toContain('failed');
    });
  });
});
