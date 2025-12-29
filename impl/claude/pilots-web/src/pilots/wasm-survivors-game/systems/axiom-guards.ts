/**
 * WASM Survivors - Axiom Guards System
 *
 * Runtime verification that the Four True Axioms are never violated.
 * This is the GUARDIAN layer - it watches, measures, and ALERTS.
 *
 * The Four Axioms:
 * - A1: PLAYER AGENCY (L=0.02) - Player choices determine outcomes
 * - A2: ATTRIBUTABLE OUTCOMES (L=0.05) - Every outcome traces to identifiable cause
 * - A3: VISIBLE MASTERY (L=0.08) - Skill development externally observable
 * - A4: COMPOSITIONAL EXPERIENCE (L=0.03) - Moments compose algebraically into arcs
 *
 * Philosophy: Axiom violation = Quality zero. No exceptions.
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part I: The Axiom Layer)
 */

import type { ArcPhase } from './contrast';

// =============================================================================
// Types - Death Context for A1/A2
// =============================================================================

/**
 * A single decision in the causal chain leading to death.
 */
export interface CausalDecision {
  actor: 'player' | 'enemy' | 'system';
  action: string;
  gameTime: number;
  consequence: string;
}

/**
 * Enhanced death context for axiom verification.
 */
export interface AxiomDeathContext {
  // Core death info
  cause: 'combat' | 'ball' | 'overwhelmed';
  specificCause: string;  // A2: Human-readable cause in <50 chars

  // A1: Decision chain
  causalChain: CausalDecision[];

  // Context at death
  wave: number;
  gameTime: number;
  healthBefore: number;
  healthAfter: number;

  // A2: What killed the player
  killerType: string | null;
  attackType: string | null;

  // Metadata
  nearMiss: boolean;
}

// =============================================================================
// Types - Skill Metrics for A3
// =============================================================================

/**
 * Actual skill metrics (measurements, not estimates).
 *
 * CRITICAL: These must be computed from actual events, not heuristics.
 */
export interface AxiomSkillMetrics {
  // A3: Real measurements
  attacksEncountered: number;  // Total attacks directed at player
  attacksEvaded: number;       // Attacks player dodged
  dodgeRate: number;           // attacksEvaded / attacksEncountered

  // Damage metrics
  damageDealt: number;
  damageReceived: number;
  damageEfficiency: number;    // damageDealt / damageReceived (higher = better)

  // Build metrics
  upgradesChosen: number;
  synergiesAchieved: number;
  buildFocus: number;          // synergiesAchieved / upgradesChosen

  // Time metrics
  survivalTime: number;
  killsPerSecond: number;

  // Near-miss (graze) tracking
  grazeCount: number;
  grazeChains: number;  // Consecutive grazes
}

// =============================================================================
// Types - Arc Composition for A4
// =============================================================================

/**
 * Arc phase history for composition verification.
 */
export interface AxiomArcHistory {
  phases: ArcPhase[];
  transitions: Array<{
    from: ArcPhase;
    to: ArcPhase;
    gameTime: number;
    trigger: string;
  }>;
  hasDefiniteClosure: boolean;
  closureType: 'dignity' | 'arbitrary' | null;
}

// =============================================================================
// Types - Violation Reports
// =============================================================================

export type AxiomId = 'A1' | 'A2' | 'A3' | 'A4';

export interface AxiomViolation {
  axiom: AxiomId;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  details: string;
  timestamp: number;
  context?: Record<string, unknown>;
}

export interface AxiomGuardReport {
  violations: AxiomViolation[];
  passed: AxiomId[];
  qualityScore: number;  // 0-1, 0 if any critical violation
}

// =============================================================================
// A1: AGENCY GUARD
// =============================================================================

/**
 * A1: Every death must trace to player decisions.
 *
 * Test: For any outcome O, there exists a traceable decision chain
 *       D1 -> D2 -> ... -> Dn -> O
 *
 * VIOLATION if:
 * - Death has no causal chain
 * - Causal chain has no player decisions
 * - Death was purely random (no player influence)
 */
export function guardAgency(deathContext: AxiomDeathContext): AxiomViolation | null {
  // Check 1: Causal chain must exist
  if (!deathContext.causalChain || deathContext.causalChain.length === 0) {
    return {
      axiom: 'A1',
      severity: 'critical',
      message: 'A1 VIOLATION: Death has no causal chain',
      details: 'Every death must trace to a sequence of decisions. This death appeared from nowhere.',
      timestamp: Date.now(),
      context: { deathContext },
    };
  }

  // Check 2: At least one player decision in chain
  const playerDecisions = deathContext.causalChain.filter(d => d.actor === 'player');
  if (playerDecisions.length === 0) {
    return {
      axiom: 'A1',
      severity: 'critical',
      message: 'A1 VIOLATION: No player decisions in causal chain',
      details: 'Death occurred without any player input. The player had no agency over this outcome.',
      timestamp: Date.now(),
      context: {
        chain: deathContext.causalChain,
        playerDecisionCount: 0,
      },
    };
  }

  // Check 3: Player had time to react (not instant spawn death)
  const timeFromFirstThreat = deathContext.gameTime - deathContext.causalChain[0].gameTime;
  if (timeFromFirstThreat < 500) { // Less than 0.5 seconds
    return {
      axiom: 'A1',
      severity: 'warning',
      message: 'A1 WARNING: Reaction time may be insufficient',
      details: `Only ${timeFromFirstThreat}ms from first threat to death. Player may not have had time to react.`,
      timestamp: Date.now(),
      context: { reactionTimeMs: timeFromFirstThreat },
    };
  }

  return null;
}

// =============================================================================
// A2: ATTRIBUTION GUARD
// =============================================================================

/**
 * A2: Every outcome must trace to an identifiable cause.
 *
 * Test: Player can articulate cause of death within 2 seconds.
 *
 * VIOLATION if:
 * - Death cause is empty or too vague
 * - Death cause is too long to read quickly (>50 chars)
 * - Killer type is unknown
 */
export function guardAttribution(deathContext: AxiomDeathContext): AxiomViolation | null {
  // Check 1: Specific cause exists
  if (!deathContext.specificCause || deathContext.specificCause.trim() === '') {
    return {
      axiom: 'A2',
      severity: 'critical',
      message: 'A2 VIOLATION: Death cause not specified',
      details: 'Player cannot articulate why they died because no cause was provided.',
      timestamp: Date.now(),
      context: { cause: deathContext.cause },
    };
  }

  // Check 2: Specific cause is articulable (<50 chars)
  if (deathContext.specificCause.length > 50) {
    return {
      axiom: 'A2',
      severity: 'warning',
      message: 'A2 WARNING: Death cause too verbose',
      details: `Cause is ${deathContext.specificCause.length} chars. Should be <50 for quick comprehension.`,
      timestamp: Date.now(),
      context: { specificCause: deathContext.specificCause },
    };
  }

  // Check 3: Generic causes are violations
  const genericCauses = ['you died', 'game over', 'combat', 'damage', 'dead'];
  const lowerCause = deathContext.specificCause.toLowerCase();
  if (genericCauses.some(g => lowerCause === g)) {
    return {
      axiom: 'A2',
      severity: 'critical',
      message: 'A2 VIOLATION: Death cause is too generic',
      details: `"${deathContext.specificCause}" tells the player nothing. Need specific cause.`,
      timestamp: Date.now(),
      context: { genericCause: deathContext.specificCause },
    };
  }

  // Check 4: For combat deaths, killer must be identified
  if (deathContext.cause === 'combat' && !deathContext.killerType) {
    return {
      axiom: 'A2',
      severity: 'critical',
      message: 'A2 VIOLATION: Killer not identified',
      details: 'Combat death but no killer type specified. Player cannot learn from this.',
      timestamp: Date.now(),
      context: { cause: deathContext.cause, killerType: deathContext.killerType },
    };
  }

  return null;
}

// =============================================================================
// A3: MASTERY GUARD
// =============================================================================

/**
 * A3: Skill development must be externally observable.
 *
 * Test: Run 10 looks different from Run 1. Metrics improve.
 *
 * VIOLATION if:
 * - Skill metrics are estimates, not measurements
 * - Dodge rate is impossible (evaded > encountered)
 * - No improvement tracking exists
 */
export function guardMastery(metrics: AxiomSkillMetrics): AxiomViolation | null {
  // Check 1: Dodge rate must be measurable
  if (metrics.attacksEncountered === undefined || metrics.attacksEvaded === undefined) {
    return {
      axiom: 'A3',
      severity: 'critical',
      message: 'A3 VIOLATION: Skill metrics not measured',
      details: 'attacksEncountered and attacksEvaded must be tracked for real dodge rate.',
      timestamp: Date.now(),
      context: { metrics },
    };
  }

  // Check 2: Dodge rate sanity check
  if (metrics.attacksEvaded > metrics.attacksEncountered) {
    return {
      axiom: 'A3',
      severity: 'critical',
      message: 'A3 VIOLATION: Impossible dodge rate',
      details: `Evaded ${metrics.attacksEvaded} but only encountered ${metrics.attacksEncountered}. Math is wrong.`,
      timestamp: Date.now(),
      context: { evaded: metrics.attacksEvaded, encountered: metrics.attacksEncountered },
    };
  }

  // Check 3: Computed dodge rate matches provided value
  const computedDodgeRate = metrics.attacksEncountered > 0
    ? metrics.attacksEvaded / metrics.attacksEncountered
    : 0;

  if (Math.abs(computedDodgeRate - metrics.dodgeRate) > 0.01) {
    return {
      axiom: 'A3',
      severity: 'warning',
      message: 'A3 WARNING: Dodge rate inconsistency',
      details: `Provided dodgeRate ${metrics.dodgeRate} differs from computed ${computedDodgeRate.toFixed(3)}.`,
      timestamp: Date.now(),
      context: { provided: metrics.dodgeRate, computed: computedDodgeRate },
    };
  }

  return null;
}

/**
 * Compare two runs for A3 compliance (Run 10 vs Run 1).
 */
export function guardMasteryProgression(
  run1Metrics: AxiomSkillMetrics,
  run10Metrics: AxiomSkillMetrics
): AxiomViolation | null {
  // Count improvements
  let improvements = 0;
  let regressions = 0;

  if (run10Metrics.survivalTime > run1Metrics.survivalTime) improvements++;
  else if (run10Metrics.survivalTime < run1Metrics.survivalTime * 0.8) regressions++;

  if (run10Metrics.dodgeRate > run1Metrics.dodgeRate) improvements++;
  else if (run10Metrics.dodgeRate < run1Metrics.dodgeRate * 0.8) regressions++;

  if (run10Metrics.killsPerSecond > run1Metrics.killsPerSecond) improvements++;
  else if (run10Metrics.killsPerSecond < run1Metrics.killsPerSecond * 0.8) regressions++;

  if (run10Metrics.damageEfficiency > run1Metrics.damageEfficiency) improvements++;
  else if (run10Metrics.damageEfficiency < run1Metrics.damageEfficiency * 0.8) regressions++;

  // A3: Run 10 should show improvement in at least 2 dimensions
  if (improvements < 2) {
    return {
      axiom: 'A3',
      severity: 'warning',
      message: 'A3 WARNING: Insufficient visible improvement',
      details: `Only ${improvements} metrics improved between Run 1 and Run 10. Expected at least 2.`,
      timestamp: Date.now(),
      context: {
        improvements,
        regressions,
        run1: { survival: run1Metrics.survivalTime, dodge: run1Metrics.dodgeRate },
        run10: { survival: run10Metrics.survivalTime, dodge: run10Metrics.dodgeRate },
      },
    };
  }

  return null;
}

// =============================================================================
// A4: COMPOSITION GUARD
// =============================================================================

/**
 * A4: Moments compose algebraically into arcs.
 *
 * Test: Experience quality obeys associativity.
 *       Run must traverse at least 3 arc phases.
 *
 * VIOLATION if:
 * - Run visits fewer than 3 arc phases
 * - Arc has no peak or valley
 * - Closure is arbitrary, not dignified
 */
export function guardComposition(arcHistory: AxiomArcHistory): AxiomViolation | null {
  // Check 1: At least 3 arc phases visited
  const uniquePhases = new Set(arcHistory.phases);
  if (uniquePhases.size < 3) {
    return {
      axiom: 'A4',
      severity: 'warning',
      message: 'A4 WARNING: Insufficient arc phase coverage',
      details: `Only ${uniquePhases.size} unique phases visited. Runs should traverse at least 3 for emotional variety.`,
      timestamp: Date.now(),
      context: { phases: Array.from(uniquePhases) },
    };
  }

  // Check 2: Must have both peak and valley
  const hasPeak = arcHistory.phases.includes('FLOW') || arcHistory.phases.includes('POWER');
  const hasValley = arcHistory.phases.includes('CRISIS') || arcHistory.phases.includes('TRAGEDY');

  if (!hasPeak || !hasValley) {
    return {
      axiom: 'A4',
      severity: 'warning',
      message: 'A4 WARNING: Arc missing peak or valley',
      details: `Arc validity requires at least one peak and one valley. Peak: ${hasPeak}, Valley: ${hasValley}.`,
      timestamp: Date.now(),
      context: { hasPeak, hasValley, phases: arcHistory.phases },
    };
  }

  // Check 3: Closure must be definite and dignified
  if (!arcHistory.hasDefiniteClosure) {
    return {
      axiom: 'A4',
      severity: 'warning',
      message: 'A4 WARNING: Arc has no definite closure',
      details: 'The arc faded out instead of ending definitively. This violates arc validity.',
      timestamp: Date.now(),
    };
  }

  if (arcHistory.closureType === 'arbitrary') {
    return {
      axiom: 'A4',
      severity: 'critical',
      message: 'A4 VIOLATION: Arbitrary closure',
      details: 'Death felt random/unfair rather than earned. This is an A2 violation propagating to A4.',
      timestamp: Date.now(),
      context: { closureType: arcHistory.closureType },
    };
  }

  return null;
}

// =============================================================================
// Aesthetic Floor Guards
// =============================================================================

/**
 * F-A1: Theme must feel emergent, not imposed.
 */
export function guardEarnedNotImposed(_context: unknown): AxiomViolation | null {
  // This is a subjective check - would require player feedback.
  // For now, we trust the design.
  return null;
}

/**
 * F-A2: Every ending must have identifiable cause.
 * (Depends on A2 compliance)
 */
export function guardMeaningfulNotArbitrary(deathContext: AxiomDeathContext): AxiomViolation | null {
  return guardAttribution(deathContext); // A2 covers this
}

/**
 * F-A3: System must feel collaborative, not surveilling.
 */
export function guardWitnessedNotSurveilled(witnessConfig: {
  showsOptInOnly: boolean;
  hasNegativeMessages: boolean;
  hasGapShame: boolean;
}): AxiomViolation | null {
  if (!witnessConfig.showsOptInOnly) {
    return {
      axiom: 'A4', // Using A4 for floor checks
      severity: 'warning',
      message: 'F-A3 WARNING: Witness may feel surveilling',
      details: 'Witness data should be opt-in only. Forced display feels like surveillance.',
      timestamp: Date.now(),
    };
  }

  if (witnessConfig.hasNegativeMessages) {
    return {
      axiom: 'A4',
      severity: 'critical',
      message: 'F-A3 VIOLATION: Negative messaging detected',
      details: 'Messages like "You failed" or "Try harder" violate F-A3.',
      timestamp: Date.now(),
    };
  }

  if (witnessConfig.hasGapShame) {
    return {
      axiom: 'A4',
      severity: 'critical',
      message: 'F-A3 VIOLATION: Gap shame detected',
      details: 'Comparing player to others or to their past negatively violates F-A3.',
      timestamp: Date.now(),
    };
  }

  return null;
}

/**
 * F-A4: Death must feel like journey completion, not failure.
 */
export function guardDignityInFailure(deathScreenConfig: {
  message: string;
  showsJourneyMetrics: boolean;
  usesPunitiveLanguage: boolean;
}): AxiomViolation | null {
  const punitiveWords = ['fail', 'lost', 'bad', 'poor', 'weak', 'pathetic'];
  const lowerMessage = deathScreenConfig.message.toLowerCase();

  if (punitiveWords.some(w => lowerMessage.includes(w))) {
    return {
      axiom: 'A4',
      severity: 'critical',
      message: 'F-A4 VIOLATION: Punitive death messaging',
      details: `Death message "${deathScreenConfig.message}" uses punitive language.`,
      timestamp: Date.now(),
      context: { message: deathScreenConfig.message },
    };
  }

  if (!deathScreenConfig.showsJourneyMetrics) {
    return {
      axiom: 'A4',
      severity: 'warning',
      message: 'F-A4 WARNING: Death screen lacks journey context',
      details: 'Death screen should show what player accomplished, not just that they died.',
      timestamp: Date.now(),
    };
  }

  return null;
}

// =============================================================================
// Full Axiom Check
// =============================================================================

/**
 * Run all axiom guards on a death event.
 *
 * This is the main entry point called when a run ends.
 */
export function runAxiomGuards(
  deathContext: AxiomDeathContext,
  skillMetrics: AxiomSkillMetrics,
  arcHistory: AxiomArcHistory
): AxiomGuardReport {
  const violations: AxiomViolation[] = [];
  const passed: AxiomId[] = [];

  // A1: Agency
  const a1Violation = guardAgency(deathContext);
  if (a1Violation) {
    violations.push(a1Violation);
  } else {
    passed.push('A1');
  }

  // A2: Attribution
  const a2Violation = guardAttribution(deathContext);
  if (a2Violation) {
    violations.push(a2Violation);
  } else {
    passed.push('A2');
  }

  // A3: Mastery
  const a3Violation = guardMastery(skillMetrics);
  if (a3Violation) {
    violations.push(a3Violation);
  } else {
    passed.push('A3');
  }

  // A4: Composition
  const a4Violation = guardComposition(arcHistory);
  if (a4Violation) {
    violations.push(a4Violation);
  } else {
    passed.push('A4');
  }

  // Quality score: 0 if any critical violation
  const hasCritical = violations.some(v => v.severity === 'critical');
  const warningCount = violations.filter(v => v.severity === 'warning').length;
  const qualityScore = hasCritical ? 0 : 1 - (warningCount * 0.1);

  return {
    violations,
    passed,
    qualityScore: Math.max(0, qualityScore),
  };
}

// =============================================================================
// Runtime Tracking
// =============================================================================

/**
 * Axiom guardian state for runtime tracking.
 */
export interface AxiomGuardianState {
  // A1/A2: Causal chain building
  causalChain: CausalDecision[];

  // A3: Skill measurement
  attacksEncountered: number;
  attacksEvaded: number;
  damageDealt: number;
  damageReceived: number;
  grazeCount: number;

  // A4: Arc tracking
  arcPhases: ArcPhase[];

  // Alerts
  alerts: AxiomViolation[];
}

/**
 * Create initial guardian state.
 */
export function createGuardianState(): AxiomGuardianState {
  return {
    causalChain: [],
    attacksEncountered: 0,
    attacksEvaded: 0,
    damageDealt: 0,
    damageReceived: 0,
    grazeCount: 0,
    arcPhases: ['POWER'],
    alerts: [],
  };
}

/**
 * Record a player decision in the causal chain.
 */
export function recordPlayerDecision(
  state: AxiomGuardianState,
  action: string,
  consequence: string,
  gameTime: number
): void {
  state.causalChain.push({
    actor: 'player',
    action,
    consequence,
    gameTime,
  });

  // Keep chain at reasonable size (last 20 decisions)
  if (state.causalChain.length > 20) {
    state.causalChain.shift();
  }
}

/**
 * Record an enemy action in the causal chain.
 */
export function recordEnemyAction(
  state: AxiomGuardianState,
  action: string,
  consequence: string,
  gameTime: number
): void {
  state.causalChain.push({
    actor: 'enemy',
    action,
    consequence,
    gameTime,
  });

  if (state.causalChain.length > 20) {
    state.causalChain.shift();
  }
}

/**
 * Record an attack encounter (for A3 dodge rate).
 */
export function recordAttackEncounter(
  state: AxiomGuardianState,
  evaded: boolean
): void {
  state.attacksEncountered++;
  if (evaded) {
    state.attacksEvaded++;
  }
}

/**
 * Record damage dealt (for A3 efficiency).
 */
export function recordDamageDealt(state: AxiomGuardianState, amount: number): void {
  state.damageDealt += amount;
}

/**
 * Record damage received (for A3 efficiency).
 */
export function recordDamageReceived(state: AxiomGuardianState, amount: number): void {
  state.damageReceived += amount;
}

/**
 * Record a graze (near miss).
 */
export function recordGraze(state: AxiomGuardianState): void {
  state.grazeCount++;
}

/**
 * Record arc phase visit.
 */
export function recordArcPhase(state: AxiomGuardianState, phase: ArcPhase): void {
  if (state.arcPhases[state.arcPhases.length - 1] !== phase) {
    state.arcPhases.push(phase);
  }
}

/**
 * Build skill metrics from guardian state.
 */
export function buildSkillMetrics(
  state: AxiomGuardianState,
  survivalTime: number,
  totalKills: number,
  upgradesChosen: number,
  synergiesAchieved: number
): AxiomSkillMetrics {
  const dodgeRate = state.attacksEncountered > 0
    ? state.attacksEvaded / state.attacksEncountered
    : 0;

  const damageEfficiency = state.damageReceived > 0
    ? state.damageDealt / state.damageReceived
    : state.damageDealt;

  const buildFocus = upgradesChosen > 0
    ? synergiesAchieved / upgradesChosen
    : 0;

  const killsPerSecond = survivalTime > 0
    ? totalKills / (survivalTime / 1000)
    : 0;

  return {
    attacksEncountered: state.attacksEncountered,
    attacksEvaded: state.attacksEvaded,
    dodgeRate,
    damageDealt: state.damageDealt,
    damageReceived: state.damageReceived,
    damageEfficiency,
    upgradesChosen,
    synergiesAchieved,
    buildFocus,
    survivalTime,
    killsPerSecond,
    grazeCount: state.grazeCount,
    grazeChains: 0, // Would need separate tracking
  };
}

/**
 * Build arc history from guardian state.
 */
export function buildArcHistory(
  state: AxiomGuardianState,
  hasDefiniteClosure: boolean,
  closureType: 'dignity' | 'arbitrary' | null
): AxiomArcHistory {
  // Build transitions from phases
  const transitions: AxiomArcHistory['transitions'] = [];
  for (let i = 1; i < state.arcPhases.length; i++) {
    transitions.push({
      from: state.arcPhases[i - 1],
      to: state.arcPhases[i],
      gameTime: 0, // Would need proper tracking
      trigger: 'progression',
    });
  }

  return {
    phases: state.arcPhases,
    transitions,
    hasDefiniteClosure,
    closureType,
  };
}

/**
 * Build death context from guardian state and death event.
 */
export function buildDeathContext(
  state: AxiomGuardianState,
  cause: 'combat' | 'ball' | 'overwhelmed',
  specificCause: string,
  killerType: string | null,
  attackType: string | null,
  wave: number,
  gameTime: number,
  healthBefore: number,
  healthAfter: number,
  nearMiss: boolean
): AxiomDeathContext {
  return {
    cause,
    specificCause,
    causalChain: [...state.causalChain],
    wave,
    gameTime,
    healthBefore,
    healthAfter,
    killerType,
    attackType,
    nearMiss,
  };
}

// =============================================================================
// Console Alerts (Dev Mode)
// =============================================================================

/**
 * Log violation to console with formatting.
 */
export function alertViolation(violation: AxiomViolation): void {
  const prefix = violation.severity === 'critical'
    ? '\x1b[31m[AXIOM VIOLATION]\x1b[0m' // Red
    : '\x1b[33m[AXIOM WARNING]\x1b[0m';   // Yellow

  console.warn(`${prefix} ${violation.axiom}: ${violation.message}`);
  console.warn(`  Details: ${violation.details}`);
  if (violation.context) {
    console.warn('  Context:', violation.context);
  }
}

/**
 * Log full report to console.
 */
export function logAxiomReport(report: AxiomGuardReport): void {
  console.log('\n=== AXIOM GUARD REPORT ===');
  console.log(`Quality Score: ${(report.qualityScore * 100).toFixed(1)}%`);
  console.log(`Passed: ${report.passed.join(', ') || 'none'}`);

  if (report.violations.length > 0) {
    console.log(`\nViolations (${report.violations.length}):`);
    for (const v of report.violations) {
      alertViolation(v);
    }
  } else {
    console.log('\nAll axioms passed!');
  }

  console.log('========================\n');
}
