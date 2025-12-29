/**
 * Axiom Guards Test Suite
 *
 * Verifies that the Four True Axioms are properly guarded:
 * - A1: PLAYER AGENCY - Player choices determine outcomes
 * - A2: ATTRIBUTABLE OUTCOMES - Every outcome traces to identifiable cause
 * - A3: VISIBLE MASTERY - Skill development externally observable
 * - A4: COMPOSITIONAL EXPERIENCE - Moments compose into arcs
 *
 * Philosophy: Axiom violation = Quality zero. No exceptions.
 */

import { describe, it, expect } from 'vitest';

import {
  guardAgency,
  guardAttribution,
  guardMastery,
  guardMasteryProgression,
  guardComposition,
  guardDignityInFailure,
  guardWitnessedNotSurveilled,
  runAxiomGuards,
  createGuardianState,
  recordPlayerDecision,
  recordEnemyAction,
  recordAttackEncounter,
  buildSkillMetrics,
  // buildArcHistory, // TODO: Add tests for arc history
  buildDeathContext,
  type AxiomDeathContext,
  type AxiomSkillMetrics,
  type AxiomArcHistory,
} from '../axiom-guards';

// =============================================================================
// A1: AGENCY Tests
// =============================================================================

describe('A1: Player Agency Guard', () => {
  it('should pass when causal chain contains player decisions', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: 'Guard stomp while retreating',
      causalChain: [
        { actor: 'player', action: 'moved right', consequence: 'entered danger zone', gameTime: 1000 },
        { actor: 'enemy', action: 'telegraph stomp', consequence: 'warned player', gameTime: 1500 },
        { actor: 'player', action: 'continued moving', consequence: 'stayed in danger', gameTime: 1700 },
        { actor: 'enemy', action: 'executed stomp', consequence: 'player hit', gameTime: 2000 },
      ],
      wave: 5,
      gameTime: 2000,
      healthBefore: 20,
      healthAfter: 0,
      killerType: 'tank',
      attackType: 'stomp',
      nearMiss: false,
    };

    const violation = guardAgency(deathContext);
    expect(violation).toBeNull();
  });

  it('should VIOLATE when causal chain is empty', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: 'Unknown death',
      causalChain: [],
      wave: 5,
      gameTime: 2000,
      healthBefore: 20,
      healthAfter: 0,
      killerType: null,
      attackType: null,
      nearMiss: false,
    };

    const violation = guardAgency(deathContext);
    expect(violation).not.toBeNull();
    expect(violation?.axiom).toBe('A1');
    expect(violation?.severity).toBe('critical');
    expect(violation?.message).toContain('no causal chain');
  });

  it('should VIOLATE when causal chain has no player decisions', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: 'Random death',
      causalChain: [
        { actor: 'enemy', action: 'spawned', consequence: 'appeared', gameTime: 1000 },
        { actor: 'system', action: 'dealt damage', consequence: 'player died', gameTime: 1100 },
      ],
      wave: 1,
      gameTime: 1100,
      healthBefore: 100,
      healthAfter: 0,
      killerType: 'basic',
      attackType: 'contact',
      nearMiss: false,
    };

    const violation = guardAgency(deathContext);
    expect(violation).not.toBeNull();
    expect(violation?.axiom).toBe('A1');
    expect(violation?.message).toContain('No player decisions');
  });

  it('should WARN when reaction time is too short', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: 'Instant spawn death',
      causalChain: [
        { actor: 'enemy', action: 'spawned on player', consequence: 'instant damage', gameTime: 1000 },
        { actor: 'player', action: 'tried to move', consequence: 'too late', gameTime: 1300 },
      ],
      wave: 1,
      gameTime: 1300,
      healthBefore: 100,
      healthAfter: 0,
      killerType: 'basic',
      attackType: 'contact',
      nearMiss: false,
    };

    const violation = guardAgency(deathContext);
    expect(violation).not.toBeNull();
    expect(violation?.severity).toBe('warning');
    expect(violation?.message).toContain('Reaction time');
  });
});

// =============================================================================
// A2: ATTRIBUTION Tests
// =============================================================================

describe('A2: Attributable Outcomes Guard', () => {
  it('should pass when death cause is specific and readable', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: 'Tank stomp at Wave 5',
      causalChain: [{ actor: 'player', action: 'stayed still', consequence: 'hit', gameTime: 1000 }],
      wave: 5,
      gameTime: 2000,
      healthBefore: 20,
      healthAfter: 0,
      killerType: 'tank',
      attackType: 'stomp',
      nearMiss: false,
    };

    const violation = guardAttribution(deathContext);
    expect(violation).toBeNull();
  });

  it('should VIOLATE when specific cause is empty', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: '',
      causalChain: [{ actor: 'player', action: 'moved', consequence: 'hit', gameTime: 1000 }],
      wave: 5,
      gameTime: 2000,
      healthBefore: 20,
      healthAfter: 0,
      killerType: 'basic',
      attackType: null,
      nearMiss: false,
    };

    const violation = guardAttribution(deathContext);
    expect(violation).not.toBeNull();
    expect(violation?.axiom).toBe('A2');
    expect(violation?.message).toContain('not specified');
  });

  it('should VIOLATE when death cause is too generic', () => {
    const genericCauses = ['You Died', 'Game Over', 'Combat', 'Damage', 'Dead'];

    for (const cause of genericCauses) {
      const deathContext: AxiomDeathContext = {
        cause: 'combat',
        specificCause: cause,
        causalChain: [{ actor: 'player', action: 'moved', consequence: 'hit', gameTime: 1000 }],
        wave: 5,
        gameTime: 2000,
        healthBefore: 20,
        healthAfter: 0,
        killerType: 'basic',
        attackType: null,
        nearMiss: false,
      };

      const violation = guardAttribution(deathContext);
      expect(violation).not.toBeNull();
      expect(violation?.message).toContain('too generic');
    }
  });

  it('should WARN when death cause is too long', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: 'This is a very long death cause that goes on and on and would take more than 2 seconds to read',
      causalChain: [{ actor: 'player', action: 'moved', consequence: 'hit', gameTime: 1000 }],
      wave: 5,
      gameTime: 2000,
      healthBefore: 20,
      healthAfter: 0,
      killerType: 'basic',
      attackType: null,
      nearMiss: false,
    };

    const violation = guardAttribution(deathContext);
    expect(violation).not.toBeNull();
    expect(violation?.severity).toBe('warning');
    expect(violation?.message).toContain('too verbose');
  });

  it('should VIOLATE when combat death has no killer identified', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: 'Killed in combat',
      causalChain: [{ actor: 'player', action: 'moved', consequence: 'hit', gameTime: 1000 }],
      wave: 5,
      gameTime: 2000,
      healthBefore: 20,
      healthAfter: 0,
      killerType: null,  // No killer identified!
      attackType: null,
      nearMiss: false,
    };

    const violation = guardAttribution(deathContext);
    expect(violation).not.toBeNull();
    expect(violation?.message).toContain('Killer not identified');
  });
});

// =============================================================================
// A3: MASTERY Tests
// =============================================================================

describe('A3: Visible Mastery Guard', () => {
  it('should pass when skill metrics are properly measured', () => {
    const metrics: AxiomSkillMetrics = {
      attacksEncountered: 100,
      attacksEvaded: 75,
      dodgeRate: 0.75,
      damageDealt: 5000,
      damageReceived: 200,
      damageEfficiency: 25,
      upgradesChosen: 5,
      synergiesAchieved: 2,
      buildFocus: 0.4,
      survivalTime: 180000,
      killsPerSecond: 2.5,
      grazeCount: 30,
      grazeChains: 5,
    };

    const violation = guardMastery(metrics);
    expect(violation).toBeNull();
  });

  it('should VIOLATE when dodge rate is impossible', () => {
    const metrics: AxiomSkillMetrics = {
      attacksEncountered: 50,
      attacksEvaded: 100, // More evaded than encountered!
      dodgeRate: 2.0,     // Impossible
      damageDealt: 5000,
      damageReceived: 200,
      damageEfficiency: 25,
      upgradesChosen: 5,
      synergiesAchieved: 2,
      buildFocus: 0.4,
      survivalTime: 180000,
      killsPerSecond: 2.5,
      grazeCount: 30,
      grazeChains: 5,
    };

    const violation = guardMastery(metrics);
    expect(violation).not.toBeNull();
    expect(violation?.axiom).toBe('A3');
    expect(violation?.message).toContain('Impossible dodge rate');
  });

  it('should WARN when computed dodge rate does not match provided', () => {
    const metrics: AxiomSkillMetrics = {
      attacksEncountered: 100,
      attacksEvaded: 75,
      dodgeRate: 0.5, // Wrong! Should be 0.75
      damageDealt: 5000,
      damageReceived: 200,
      damageEfficiency: 25,
      upgradesChosen: 5,
      synergiesAchieved: 2,
      buildFocus: 0.4,
      survivalTime: 180000,
      killsPerSecond: 2.5,
      grazeCount: 30,
      grazeChains: 5,
    };

    const violation = guardMastery(metrics);
    expect(violation).not.toBeNull();
    expect(violation?.severity).toBe('warning');
    expect(violation?.message).toContain('inconsistency');
  });
});

describe('A3: Mastery Progression Guard', () => {
  it('should pass when Run 10 shows improvement over Run 1', () => {
    const run1: AxiomSkillMetrics = {
      attacksEncountered: 50,
      attacksEvaded: 20,
      dodgeRate: 0.4,
      damageDealt: 2000,
      damageReceived: 300,
      damageEfficiency: 6.67,
      upgradesChosen: 3,
      synergiesAchieved: 0,
      buildFocus: 0,
      survivalTime: 60000,
      killsPerSecond: 1.5,
      grazeCount: 5,
      grazeChains: 1,
    };

    const run10: AxiomSkillMetrics = {
      attacksEncountered: 100,
      attacksEvaded: 80,
      dodgeRate: 0.8,  // Improved!
      damageDealt: 8000,
      damageReceived: 200,
      damageEfficiency: 40, // Improved!
      upgradesChosen: 5,
      synergiesAchieved: 2,
      buildFocus: 0.4,
      survivalTime: 180000, // Improved!
      killsPerSecond: 3.0,  // Improved!
      grazeCount: 30,
      grazeChains: 5,
    };

    const violation = guardMasteryProgression(run1, run10);
    expect(violation).toBeNull();
  });

  it('should WARN when Run 10 shows no improvement', () => {
    const run1: AxiomSkillMetrics = {
      attacksEncountered: 100,
      attacksEvaded: 80,
      dodgeRate: 0.8,
      damageDealt: 8000,
      damageReceived: 200,
      damageEfficiency: 40,
      upgradesChosen: 5,
      synergiesAchieved: 2,
      buildFocus: 0.4,
      survivalTime: 180000,
      killsPerSecond: 3.0,
      grazeCount: 30,
      grazeChains: 5,
    };

    // Run 10 is WORSE than Run 1
    const run10: AxiomSkillMetrics = {
      ...run1,
      dodgeRate: 0.3,  // Worse
      survivalTime: 30000, // Worse
      killsPerSecond: 1.0, // Worse
      damageEfficiency: 5, // Worse
    };

    const violation = guardMasteryProgression(run1, run10);
    expect(violation).not.toBeNull();
    expect(violation?.message).toContain('Insufficient visible improvement');
  });
});

// =============================================================================
// A4: COMPOSITION Tests
// =============================================================================

describe('A4: Compositional Experience Guard', () => {
  it('should pass when arc covers 3+ phases with peak and valley', () => {
    const arcHistory: AxiomArcHistory = {
      phases: ['POWER', 'FLOW', 'CRISIS', 'TRAGEDY'],
      transitions: [
        { from: 'POWER', to: 'FLOW', gameTime: 30000, trigger: 'wave_progression' },
        { from: 'FLOW', to: 'CRISIS', gameTime: 90000, trigger: 'ball_forming' },
        { from: 'CRISIS', to: 'TRAGEDY', gameTime: 150000, trigger: 'inevitable_end' },
      ],
      hasDefiniteClosure: true,
      closureType: 'dignity',
    };

    const violation = guardComposition(arcHistory);
    expect(violation).toBeNull();
  });

  it('should WARN when fewer than 3 phases visited', () => {
    const arcHistory: AxiomArcHistory = {
      phases: ['POWER', 'CRISIS'],  // Only 2 phases
      transitions: [],
      hasDefiniteClosure: true,
      closureType: 'dignity',
    };

    const violation = guardComposition(arcHistory);
    expect(violation).not.toBeNull();
    expect(violation?.message).toContain('Insufficient arc phase coverage');
  });

  it('should VIOLATE when closure is arbitrary', () => {
    const arcHistory: AxiomArcHistory = {
      phases: ['POWER', 'FLOW', 'CRISIS'],
      transitions: [],
      hasDefiniteClosure: true,
      closureType: 'arbitrary',  // Death felt random
    };

    const violation = guardComposition(arcHistory);
    expect(violation).not.toBeNull();
    expect(violation?.severity).toBe('critical');
    expect(violation?.message).toContain('Arbitrary closure');
  });
});

// =============================================================================
// Aesthetic Floor Tests
// =============================================================================

describe('F-A3: Witnessed Not Surveilled', () => {
  it('should pass when witness is opt-in only', () => {
    const violation = guardWitnessedNotSurveilled({
      showsOptInOnly: true,
      hasNegativeMessages: false,
      hasGapShame: false,
    });

    expect(violation).toBeNull();
  });

  it('should VIOLATE when negative messages are present', () => {
    const violation = guardWitnessedNotSurveilled({
      showsOptInOnly: true,
      hasNegativeMessages: true,  // "You failed"
      hasGapShame: false,
    });

    expect(violation).not.toBeNull();
    expect(violation?.message).toContain('Negative messaging');
  });

  it('should VIOLATE when gap shame is present', () => {
    const violation = guardWitnessedNotSurveilled({
      showsOptInOnly: true,
      hasNegativeMessages: false,
      hasGapShame: true,  // "You're behind average"
    });

    expect(violation).not.toBeNull();
    expect(violation?.message).toContain('Gap shame');
  });
});

describe('F-A4: Dignity in Failure', () => {
  it('should pass when death messaging is dignified', () => {
    const violation = guardDignityInFailure({
      message: 'The Colony Prevails',
      showsJourneyMetrics: true,
      usesPunitiveLanguage: false,
    });

    expect(violation).toBeNull();
  });

  it('should VIOLATE when death uses punitive language', () => {
    const punitiveMessages = ['You Failed', 'Bad Run', 'Lost the game', 'Poor performance'];

    for (const message of punitiveMessages) {
      const violation = guardDignityInFailure({
        message,
        showsJourneyMetrics: true,
        usesPunitiveLanguage: true,
      });

      expect(violation).not.toBeNull();
      expect(violation?.message).toContain('Punitive death messaging');
    }
  });

  it('should WARN when journey metrics are not shown', () => {
    const violation = guardDignityInFailure({
      message: 'Run Complete',
      showsJourneyMetrics: false,
      usesPunitiveLanguage: false,
    });

    expect(violation).not.toBeNull();
    expect(violation?.severity).toBe('warning');
    expect(violation?.message).toContain('lacks journey context');
  });
});

// =============================================================================
// Full Report Tests
// =============================================================================

describe('Full Axiom Guard Report', () => {
  it('should return quality score of 1 when all axioms pass', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'ball',
      specificCause: 'Cooked by THE BALL at Wave 8',
      causalChain: [
        { actor: 'player', action: 'ignored scouts', consequence: 'coordination began', gameTime: 100000 },
        { actor: 'enemy', action: 'formed ball', consequence: 'trapped player', gameTime: 150000 },
        { actor: 'player', action: 'failed escape', consequence: 'cooked', gameTime: 160000 },
      ],
      wave: 8,
      gameTime: 160000,
      healthBefore: 50,
      healthAfter: 0,
      killerType: 'formation',
      attackType: 'heat',
      nearMiss: false,
    };

    const metrics: AxiomSkillMetrics = {
      attacksEncountered: 100,
      attacksEvaded: 75,
      dodgeRate: 0.75,
      damageDealt: 5000,
      damageReceived: 200,
      damageEfficiency: 25,
      upgradesChosen: 5,
      synergiesAchieved: 2,
      buildFocus: 0.4,
      survivalTime: 180000,
      killsPerSecond: 2.5,
      grazeCount: 30,
      grazeChains: 5,
    };

    const arcHistory: AxiomArcHistory = {
      phases: ['POWER', 'FLOW', 'CRISIS', 'TRAGEDY'],
      transitions: [],
      hasDefiniteClosure: true,
      closureType: 'dignity',
    };

    const report = runAxiomGuards(deathContext, metrics, arcHistory);

    expect(report.passed).toContain('A1');
    expect(report.passed).toContain('A2');
    expect(report.passed).toContain('A3');
    expect(report.passed).toContain('A4');
    expect(report.violations).toHaveLength(0);
    expect(report.qualityScore).toBe(1);
  });

  it('should return quality score of 0 when any critical violation exists', () => {
    const deathContext: AxiomDeathContext = {
      cause: 'combat',
      specificCause: '', // A2 critical violation
      causalChain: [],   // A1 critical violation
      wave: 1,
      gameTime: 1000,
      healthBefore: 100,
      healthAfter: 0,
      killerType: null,
      attackType: null,
      nearMiss: false,
    };

    const metrics: AxiomSkillMetrics = {
      attacksEncountered: 10,
      attacksEvaded: 5,
      dodgeRate: 0.5,
      damageDealt: 100,
      damageReceived: 100,
      damageEfficiency: 1,
      upgradesChosen: 1,
      synergiesAchieved: 0,
      buildFocus: 0,
      survivalTime: 10000,
      killsPerSecond: 1,
      grazeCount: 0,
      grazeChains: 0,
    };

    const arcHistory: AxiomArcHistory = {
      phases: ['POWER'],
      transitions: [],
      hasDefiniteClosure: true,
      closureType: 'arbitrary', // A4 critical violation
    };

    const report = runAxiomGuards(deathContext, metrics, arcHistory);

    expect(report.qualityScore).toBe(0);
    expect(report.violations.length).toBeGreaterThan(0);
    expect(report.violations.some(v => v.severity === 'critical')).toBe(true);
  });
});

// =============================================================================
// Runtime Tracking Tests
// =============================================================================

describe('Axiom Guardian State', () => {
  it('should track player decisions in causal chain', () => {
    const state = createGuardianState();

    recordPlayerDecision(state, 'moved right', 'entered danger', 1000);
    recordPlayerDecision(state, 'selected upgrade', 'became stronger', 2000);

    expect(state.causalChain).toHaveLength(2);
    expect(state.causalChain[0].actor).toBe('player');
    expect(state.causalChain[0].action).toBe('moved right');
  });

  it('should track attack encounters for dodge rate', () => {
    const state = createGuardianState();

    recordAttackEncounter(state, true);  // evaded
    recordAttackEncounter(state, false); // hit
    recordAttackEncounter(state, true);  // evaded
    recordAttackEncounter(state, true);  // evaded

    expect(state.attacksEncountered).toBe(4);
    expect(state.attacksEvaded).toBe(3);
  });

  it('should build correct skill metrics', () => {
    const state = createGuardianState();

    recordAttackEncounter(state, true);
    recordAttackEncounter(state, true);
    recordAttackEncounter(state, false);
    recordAttackEncounter(state, true);

    const metrics = buildSkillMetrics(state, 120000, 200, 5, 2);

    expect(metrics.attacksEncountered).toBe(4);
    expect(metrics.attacksEvaded).toBe(3);
    expect(metrics.dodgeRate).toBe(0.75);
    expect(metrics.killsPerSecond).toBeCloseTo(200 / 120);
  });

  it('should build death context from state', () => {
    const state = createGuardianState();

    recordPlayerDecision(state, 'moved left', 'avoided attack', 1000);
    recordEnemyAction(state, 'charged', 'approached player', 1500);
    recordPlayerDecision(state, 'dashed too late', 'got hit', 2000);

    const context = buildDeathContext(
      state,
      'combat',
      'Tank charge at Wave 5',
      'tank',
      'charge',
      5,
      2100,
      30,
      0,
      true
    );

    expect(context.causalChain).toHaveLength(3);
    expect(context.specificCause).toBe('Tank charge at Wave 5');
    expect(context.killerType).toBe('tank');
  });
});
