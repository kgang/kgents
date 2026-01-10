/**
 * Qualia Validation Framework
 *
 * General-purpose tools for validating experiential qualities in games.
 * These tools measure things that are hard to quantify but essential to fun:
 * - State machine correctness and feel
 * - Time dynamics and emotional arcs
 * - Emergence patterns and player expression
 *
 * Philosophy: The proof IS the experience. The witness IS the player.
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import type { Page } from '@playwright/test';

// =============================================================================
// Core Types
// =============================================================================

export interface QualiaResult<T = unknown> {
  passed: boolean;
  name: string;
  description: string;
  evidence: T;
  timestamp: number;
  duration: number;
}

export interface QualiaValidator<TConfig = unknown, TEvidence = unknown> {
  name: string;
  description: string;
  validate(page: Page, config: TConfig): Promise<QualiaResult<TEvidence>>;
}

export interface ValidationReport {
  pilot: string;
  run: string;
  timestamp: string;
  results: QualiaResult[];
  summary: {
    total: number;
    passed: number;
    failed: number;
    passRate: number;
  };
  verdict: 'PASS' | 'WARN' | 'FAIL';
}

// =============================================================================
// State Machine Validator
// =============================================================================

export interface StateMachineConfig {
  /** Name of the state machine being validated */
  name: string;

  /** Expected states in the machine */
  states: string[];

  /** Valid transitions: [fromState, toState, trigger?] */
  transitions: [string, string, string?][];

  /** How to query current state from the page */
  getState: () => Promise<string>;

  /** Optional: How to trigger state changes */
  triggers?: Record<string, () => Promise<void>>;

  /** Duration to observe (ms) */
  observationDuration: number;

  /** Minimum transitions expected */
  minTransitions?: number;
}

export interface StateMachineEvidence {
  observedStates: string[];
  observedTransitions: [string, string, number][]; // [from, to, timestamp]
  invalidTransitions: [string, string, number][];
  dwellTimes: Record<string, number[]>; // State -> durations
  coverage: {
    statesCovered: number;
    statesTotal: number;
    transitionsCovered: number;
    transitionsTotal: number;
  };
}

export function createStateMachineValidator(): QualiaValidator<StateMachineConfig, StateMachineEvidence> {
  return {
    name: 'State Machine Validator',
    description: 'Validates state machine correctness, coverage, and timing',

    async validate(page: Page, config: StateMachineConfig): Promise<QualiaResult<StateMachineEvidence>> {
      const startTime = Date.now();
      const observedStates: string[] = [];
      const observedTransitions: [string, string, number][] = [];
      const invalidTransitions: [string, string, number][] = [];
      const dwellTimes: Record<string, number[]> = {};

      // Initialize dwell time tracking
      config.states.forEach(s => { dwellTimes[s] = []; });

      let lastState = '';
      let lastStateStart = startTime;
      const validTransitionSet = new Set(
        config.transitions.map(([from, to]) => `${from}->${to}`)
      );

      // Observe state changes over time
      const observeState = async () => {
        // Call getState directly - it's a Node.js async function that may internally use page.evaluate()
        const currentState = await config.getState();

        if (currentState !== lastState) {
          const now = Date.now();

          // Record transition
          if (lastState) {
            observedTransitions.push([lastState, currentState, now]);

            // Check if valid
            const transitionKey = `${lastState}->${currentState}`;
            if (!validTransitionSet.has(transitionKey)) {
              invalidTransitions.push([lastState, currentState, now]);
            }

            // Record dwell time
            const dwellTime = now - lastStateStart;
            if (dwellTimes[lastState]) {
              dwellTimes[lastState].push(dwellTime);
            }
          }

          observedStates.push(currentState);
          lastState = currentState;
          lastStateStart = now;
        }
      };

      // Poll for state changes
      const pollInterval = 16; // ~60fps
      const endTime = startTime + config.observationDuration;

      while (Date.now() < endTime) {
        await observeState();
        await page.waitForTimeout(pollInterval);
      }

      // Final dwell time for last state
      if (lastState && dwellTimes[lastState]) {
        dwellTimes[lastState].push(Date.now() - lastStateStart);
      }

      // Calculate coverage
      const uniqueStates = new Set(observedStates);
      const uniqueTransitions = new Set(
        observedTransitions.map(([from, to]) => `${from}->${to}`)
      );

      const coverage = {
        statesCovered: uniqueStates.size,
        statesTotal: config.states.length,
        transitionsCovered: uniqueTransitions.size,
        transitionsTotal: config.transitions.length,
      };

      // Determine pass/fail
      const passed =
        invalidTransitions.length === 0 &&
        coverage.statesCovered >= Math.min(config.states.length, 3) &&
        (!config.minTransitions || observedTransitions.length >= config.minTransitions);

      return {
        passed,
        name: `State Machine: ${config.name}`,
        description: `Validated ${config.name} state machine over ${config.observationDuration}ms`,
        evidence: {
          observedStates,
          observedTransitions,
          invalidTransitions,
          dwellTimes,
          coverage,
        },
        timestamp: startTime,
        duration: Date.now() - startTime,
      };
    },
  };
}

// =============================================================================
// Time Dynamics Analyzer
// =============================================================================

export interface TimeDynamicsConfig {
  /** Name of the dynamic being analyzed */
  name: string;

  /** Expected phases in order */
  phases: {
    name: string;
    minDuration?: number;
    maxDuration?: number;
    detector: () => Promise<boolean>;
  }[];

  /** How to measure intensity (0-1 scale) */
  getIntensity?: () => Promise<number>;

  /** Total observation duration (ms) */
  observationDuration: number;

  /** Expected arc shape */
  expectedArc?: 'rising' | 'falling' | 'wave' | 'peak' | 'custom';
}

export interface TimeDynamicsEvidence {
  phases: {
    name: string;
    startTime: number;
    endTime: number;
    duration: number;
    inOrder: boolean;
  }[];
  intensitySamples: { time: number; value: number }[];
  arcShape: {
    detected: 'rising' | 'falling' | 'wave' | 'peak' | 'flat' | 'chaotic';
    confidence: number;
  };
  tempo: {
    avgPhaseLength: number;
    variance: number;
    rhythmic: boolean;
  };
}

export function createTimeDynamicsAnalyzer(): QualiaValidator<TimeDynamicsConfig, TimeDynamicsEvidence> {
  return {
    name: 'Time Dynamics Analyzer',
    description: 'Analyzes temporal patterns, phases, and emotional arcs',

    async validate(page: Page, config: TimeDynamicsConfig): Promise<QualiaResult<TimeDynamicsEvidence>> {
      const startTime = Date.now();
      const phases: TimeDynamicsEvidence['phases'] = [];
      const intensitySamples: { time: number; value: number }[] = [];

      let currentPhaseIndex = 0;
      let phaseStartTime = startTime;
      const pollInterval = 50;
      const endTime = startTime + config.observationDuration;

      while (Date.now() < endTime) {
        const now = Date.now();
        const elapsed = now - startTime;

        // Sample intensity if available
        // Call getIntensity directly - it's a Node.js async function that may internally use page.evaluate()
        if (config.getIntensity) {
          const intensity = await config.getIntensity();
          intensitySamples.push({ time: elapsed, value: intensity });
        }

        // Check for phase transitions
        if (currentPhaseIndex < config.phases.length) {
          const currentPhase = config.phases[currentPhaseIndex];
          // Call detector directly - it's a Node.js async function that may internally use page.evaluate()
          const isInPhase = await currentPhase.detector();

          if (isInPhase && phases.length === currentPhaseIndex) {
            // Just entered this phase
            phases.push({
              name: currentPhase.name,
              startTime: elapsed,
              endTime: 0,
              duration: 0,
              inOrder: true,
            });
            phaseStartTime = now;
          } else if (!isInPhase && phases.length > currentPhaseIndex) {
            // Just exited this phase
            const phase = phases[currentPhaseIndex];
            phase.endTime = elapsed;
            phase.duration = now - phaseStartTime;
            currentPhaseIndex++;
          }
        }

        await page.waitForTimeout(pollInterval);
      }

      // Close any open phase
      if (phases.length > 0 && phases[phases.length - 1].endTime === 0) {
        const lastPhase = phases[phases.length - 1];
        lastPhase.endTime = Date.now() - startTime;
        lastPhase.duration = lastPhase.endTime - lastPhase.startTime;
      }

      // Analyze arc shape
      const arcShape = analyzeArcShape(intensitySamples);

      // Calculate tempo
      const phaseDurations = phases.map(p => p.duration).filter(d => d > 0);
      const avgPhaseLength = phaseDurations.length > 0
        ? phaseDurations.reduce((a, b) => a + b, 0) / phaseDurations.length
        : 0;
      const variance = phaseDurations.length > 1
        ? phaseDurations.reduce((sum, d) => sum + Math.pow(d - avgPhaseLength, 2), 0) / phaseDurations.length
        : 0;
      const rhythmic = Math.sqrt(variance) / avgPhaseLength < 0.3; // Low CV = rhythmic

      // Determine pass/fail
      const phaseOrderCorrect = phases.every(p => p.inOrder);
      const arcMatches = !config.expectedArc || arcShape.detected === config.expectedArc;
      const passed = phaseOrderCorrect && arcMatches && phases.length >= config.phases.length * 0.5;

      return {
        passed,
        name: `Time Dynamics: ${config.name}`,
        description: `Analyzed ${config.name} temporal patterns over ${config.observationDuration}ms`,
        evidence: {
          phases,
          intensitySamples,
          arcShape,
          tempo: { avgPhaseLength, variance, rhythmic },
        },
        timestamp: startTime,
        duration: Date.now() - startTime,
      };
    },
  };
}

function analyzeArcShape(samples: { time: number; value: number }[]): { detected: TimeDynamicsEvidence['arcShape']['detected']; confidence: number } {
  if (samples.length < 3) {
    return { detected: 'flat', confidence: 0.5 };
  }

  const values = samples.map(s => s.value);
  const n = values.length;
  const third = Math.floor(n / 3);

  const firstThird = values.slice(0, third);
  const midThird = values.slice(third, third * 2);
  const lastThird = values.slice(third * 2);

  const avgFirst = firstThird.reduce((a, b) => a + b, 0) / firstThird.length;
  const avgMid = midThird.reduce((a, b) => a + b, 0) / midThird.length;
  const avgLast = lastThird.reduce((a, b) => a + b, 0) / lastThird.length;

  // Detect pattern
  const risingScore = (avgMid - avgFirst) + (avgLast - avgMid);
  const fallingScore = (avgFirst - avgMid) + (avgMid - avgLast);
  const peakScore = (avgMid - avgFirst) + (avgMid - avgLast);
  const waveScore = Math.abs(avgMid - avgFirst) + Math.abs(avgLast - avgMid);

  const maxDelta = Math.max(...values) - Math.min(...values);
  if (maxDelta < 0.1) {
    return { detected: 'flat', confidence: 0.9 };
  }

  const scores = [
    { type: 'rising' as const, score: risingScore },
    { type: 'falling' as const, score: fallingScore },
    { type: 'peak' as const, score: peakScore },
    { type: 'wave' as const, score: waveScore },
  ].sort((a, b) => b.score - a.score);

  const best = scores[0];
  const second = scores[1];
  const confidence = best.score > 0 ? best.score / (best.score + Math.abs(second.score) + 0.01) : 0.5;

  return { detected: best.type, confidence: Math.min(1, confidence) };
}

// =============================================================================
// Emergence Detector
// =============================================================================

export interface EmergenceConfig {
  /** Name of the emergence pattern */
  name: string;

  /** Components that can combine */
  components: string[];

  /** Known emergent combinations: [component1, component2, ..., emergentName] */
  knownEmergence: string[][];

  /** How to get current active components */
  getActiveComponents: () => Promise<string[]>;

  /** How to detect emergent behavior */
  detectEmergence: () => Promise<{ name: string; strength: number }[]>;

  /** Observation duration (ms) */
  observationDuration: number;
}

export interface EmergenceEvidence {
  componentsObserved: string[];
  emergenceEvents: {
    name: string;
    strength: number;
    components: string[];
    timestamp: number;
  }[];
  novelEmergence: string[]; // Emergence not in knownEmergence
  combinatorialRichness: {
    possibleCombinations: number;
    observedCombinations: number;
    ratio: number;
  };
  synergyScore: number; // 0-1, how much 1+1 > 2
}

export function createEmergenceDetector(): QualiaValidator<EmergenceConfig, EmergenceEvidence> {
  return {
    name: 'Emergence Detector',
    description: 'Detects emergent patterns from component combinations',

    async validate(page: Page, config: EmergenceConfig): Promise<QualiaResult<EmergenceEvidence>> {
      const startTime = Date.now();
      const componentsObserved = new Set<string>();
      const combinationsObserved = new Set<string>();
      const emergenceEvents: EmergenceEvidence['emergenceEvents'] = [];
      const knownEmergenceNames = new Set(
        config.knownEmergence.map(combo => combo[combo.length - 1])
      );

      const pollInterval = 100;
      const endTime = startTime + config.observationDuration;

      while (Date.now() < endTime) {
        const now = Date.now();
        const elapsed = now - startTime;

        // Get active components
        // Call getActiveComponents directly - it's a Node.js async function that may internally use page.evaluate()
        const activeComponents = await config.getActiveComponents();
        activeComponents.forEach(c => componentsObserved.add(c));

        // Record combination
        if (activeComponents.length >= 2) {
          const comboKey = activeComponents.sort().join('+');
          combinationsObserved.add(comboKey);
        }

        // Detect emergence
        // Call detectEmergence directly - it's a Node.js async function that may internally use page.evaluate()
        const emergent = await config.detectEmergence();
        for (const e of emergent) {
          const existing = emergenceEvents.find(ev => ev.name === e.name);
          if (!existing || e.strength > existing.strength) {
            emergenceEvents.push({
              name: e.name,
              strength: e.strength,
              components: activeComponents,
              timestamp: elapsed,
            });
          }
        }

        await page.waitForTimeout(pollInterval);
      }

      // Find novel emergence
      const novelEmergence = emergenceEvents
        .map(e => e.name)
        .filter(name => !knownEmergenceNames.has(name));

      // Calculate combinatorial richness
      const n = config.components.length;
      const possibleCombinations = (n * (n - 1)) / 2; // 2-combinations
      const observedCombinations = combinationsObserved.size;

      // Calculate synergy score (strength > individual components)
      const avgStrength = emergenceEvents.length > 0
        ? emergenceEvents.reduce((sum, e) => sum + e.strength, 0) / emergenceEvents.length
        : 0;
      const synergyScore = Math.min(1, avgStrength);

      // Determine pass/fail
      const hasEmergence = emergenceEvents.length > 0;
      const hasCoverage = componentsObserved.size >= config.components.length * 0.3;
      const passed = hasEmergence && hasCoverage;

      return {
        passed,
        name: `Emergence: ${config.name}`,
        description: `Detected emergent patterns in ${config.name} over ${config.observationDuration}ms`,
        evidence: {
          componentsObserved: Array.from(componentsObserved),
          emergenceEvents,
          novelEmergence,
          combinatorialRichness: {
            possibleCombinations,
            observedCombinations,
            ratio: possibleCombinations > 0 ? observedCombinations / possibleCombinations : 0,
          },
          synergyScore,
        },
        timestamp: startTime,
        duration: Date.now() - startTime,
      };
    },
  };
}

// =============================================================================
// Report Generator
// =============================================================================

export function generateReport(
  pilot: string,
  run: string,
  results: QualiaResult[]
): ValidationReport {
  const passed = results.filter(r => r.passed).length;
  const failed = results.filter(r => !r.passed).length;
  const total = results.length;
  const passRate = total > 0 ? passed / total : 0;

  let verdict: ValidationReport['verdict'];
  if (passRate >= 0.9) {
    verdict = 'PASS';
  } else if (passRate >= 0.6) {
    verdict = 'WARN';
  } else {
    verdict = 'FAIL';
  }

  return {
    pilot,
    run,
    timestamp: new Date().toISOString(),
    results,
    summary: { total, passed, failed, passRate },
    verdict,
  };
}
