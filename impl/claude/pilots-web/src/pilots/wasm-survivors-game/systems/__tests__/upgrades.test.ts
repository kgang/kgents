/**
 * WASM Survivors - Upgrade System Tests
 *
 * Tests for PROTO_SPEC upgrade laws:
 * - U1: Verb, Not Noun - Upgrades change behavior
 * - U2: Build Identity - Can name build by wave 5
 * - U3: Synergy Moments - 1+1 > 2 somewhere
 * - U4: Meaningful Choice - No obvious best pick
 */

import { describe, it, expect } from 'vitest';
import {
  UPGRADE_POOL,
  SYNERGY_POOL,
  generateUpgradeChoices,
  detectNewSynergies,
  applyUpgrade,
  createInitialActiveUpgrades,
  getBuildIdentity,
  type UpgradeType,
} from '../upgrades';

describe('Upgrade System', () => {
  describe('U1: Verb, Not Noun', () => {
    it('should have at least 8 upgrades', () => {
      expect(UPGRADE_POOL.length).toBeGreaterThanOrEqual(8);
    });

    it('each upgrade should have a verb description', () => {
      for (const upgrade of UPGRADE_POOL) {
        expect(upgrade.verb).toBeDefined();
        expect(upgrade.verb.length).toBeGreaterThan(0);
      }
    });

    it('each upgrade should change game behavior, not just stats', () => {
      // All upgrades should have a mechanic type
      for (const upgrade of UPGRADE_POOL) {
        expect(upgrade.mechanic.type).toBeDefined();
      }
    });
  });

  describe('U2: Build Identity', () => {
    it('should return "Starter" for no upgrades', () => {
      expect(getBuildIdentity([])).toBe('Starter');
    });

    it('should return upgrade name for single upgrade', () => {
      const result = getBuildIdentity(['pierce']);
      expect(result).toBe('Piercing Shots');
    });

    it('should return archetype names for upgrade combinations', () => {
      // Glass Cannon: aggressive but no defense
      const glassResult = getBuildIdentity(['pierce', 'multishot']);
      expect(['Glass Cannon', 'Shotgun Drill']).toContain(glassResult);

      // Tank: defensive build
      const tankResult = getBuildIdentity(['orbit', 'vampiric']);
      expect(['Tank', 'Custom Build']).toContain(tankResult);
    });
  });

  describe('U3: Synergy Moments', () => {
    it('should have at least 5 synergies defined', () => {
      expect(SYNERGY_POOL.length).toBeGreaterThanOrEqual(5);
    });

    it('each synergy should require exactly 2 upgrades', () => {
      for (const synergy of SYNERGY_POOL) {
        expect(synergy.requires).toHaveLength(2);
      }
    });

    it('should detect synergy when both upgrades are owned', () => {
      const synergies = detectNewSynergies(['pierce', 'multishot'], []);
      expect(synergies).toHaveLength(1);
      expect(synergies[0].id).toBe('shotgun_drill');
    });

    it('should not detect already-discovered synergies', () => {
      const synergies = detectNewSynergies(['pierce', 'multishot'], ['shotgun_drill']);
      expect(synergies).toHaveLength(0);
    });
  });

  describe('U4: Meaningful Choice', () => {
    it('should generate 3 unique choices by default', () => {
      const choices = generateUpgradeChoices([]);
      expect(choices).toHaveLength(3);

      const ids = choices.map(c => c.id);
      expect(new Set(ids).size).toBe(3);
    });

    it('should exclude already-owned upgrades', () => {
      const owned: UpgradeType[] = ['pierce', 'orbit'];
      const choices = generateUpgradeChoices(owned);

      for (const choice of choices) {
        expect(owned).not.toContain(choice.id);
      }
    });
  });

  describe('Upgrade Application', () => {
    it('should correctly apply pierce upgrade', () => {
      const initial = createInitialActiveUpgrades();
      const { active } = applyUpgrade(initial, 'pierce');

      expect(active.pierceCount).toBeGreaterThan(0);
      expect(active.upgrades).toContain('pierce');
    });

    it('should correctly apply orbit upgrade', () => {
      const initial = createInitialActiveUpgrades();
      const { active } = applyUpgrade(initial, 'orbit');

      expect(active.orbitActive).toBe(true);
      expect(active.orbitRadius).toBeGreaterThan(0);
    });

    it('should detect new synergies on upgrade application', () => {
      let state = createInitialActiveUpgrades();
      state = applyUpgrade(state, 'pierce').active;

      const { active, newSynergies } = applyUpgrade(state, 'multishot');
      expect(newSynergies).toHaveLength(1);
      expect(newSynergies[0].id).toBe('shotgun_drill');
      expect(active.synergies).toContain('shotgun_drill');
    });
  });
});
