/**
 * WASM Survivors - Witness System
 *
 * Async, non-blocking mark emission (< 1ms per mark).
 * Implements DD-1: Invisible Witness - zero witness HUD during play.
 * Marks are invisible until Crystal view.
 *
 * Components:
 * - MarkEmitter: action -> GameMark (async, non-blocking)
 * - TraceStore: GameMark[] (immutable, indexed)
 * - GhostRecorder: decision_point -> alternatives (DD-2)
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import type {
  BuildContext,
  IntentMark,
  OutcomeMark,
  WitnessMark,
  Trace,
  Ghost,
  GameCrystal,
  GamePrincipleWeights,
  SkillMetrics,
  CrystalSegment,
} from '@kgents/shared-primitives';

// =============================================================================
// Types
// =============================================================================

export interface WitnessContext {
  runId: string;
  marks: WitnessMark[];
  ghosts: Ghost[];
  startTime: number;
  pendingIntents: Map<string, IntentMark>;
}

export interface MarkEvent {
  type:
    | 'enemy_killed'
    | 'player_hit'
    | 'level_up'
    | 'upgrade_selected'
    | 'wave_completed'
    | 'run_ended'
    | 'clutch_survived'
    | 'first_metamorphosis'; // DD-030: First colossal revelation
  gameTime: number;
  context: BuildContext;

  // Type-specific fields
  wave?: number;
  level?: number;
  upgrade?: string;
  choices?: string[];
  alternatives?: string[];
  deathCause?: string;
  damage?: number;
  healthAfter?: number;
  threats?: number;
}

// =============================================================================
// Mark Emission (Async, Non-blocking)
// =============================================================================

/**
 * Emit a witness mark asynchronously.
 * CRITICAL: This must complete in < 1ms to not affect game loop.
 *
 * Uses queueMicrotask to defer actual storage without blocking.
 */
export function emitWitnessMark(ctx: WitnessContext, event: MarkEvent): void {
  // Schedule mark creation without blocking
  queueMicrotask(() => {
    const mark = createMark(ctx, event);

    if (mark) {
      ctx.marks.push(mark);

      // Record ghost for upgrade decisions (DD-2: Ghost as Honor)
      if (event.type === 'upgrade_selected' && event.alternatives) {
        const ghost: Ghost = {
          decisionPoint: event.gameTime,
          chosen: event.upgrade || '',
          unchosen: event.alternatives,
          context: event.context,
          projectedDrift: calculateDrift(ctx, event),
        };
        ctx.ghosts.push(ghost);
      }
    }
  });
}

/**
 * Create a WitnessMark from an event
 */
function createMark(ctx: WitnessContext, event: MarkEvent): WitnessMark | null {
  const intentId = `intent-${ctx.runId}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;

  // Determine risk level
  const risk = calculateRisk(event.context);

  // Create intent mark
  const intent: IntentMark = {
    id: intentId,
    type: mapEventToIntentType(event.type),
    gameTime: event.gameTime,
    context: event.context,
    risk,
    alternatives: event.alternatives,
  };

  // For most events, we can immediately create the outcome
  // (the action has already resolved by the time we emit)
  const outcome: OutcomeMark = {
    intentId,
    success: determineSuccess(event),
    consequence: describeConsequence(event),
    gameTime: event.gameTime,
    metricsSnapshot: estimateSkillMetrics(ctx, event),
  };

  return { intent, outcome };
}

/**
 * Map event type to intent type
 */
function mapEventToIntentType(
  eventType: MarkEvent['type']
): IntentMark['type'] {
  switch (eventType) {
    case 'upgrade_selected':
      return 'upgrade_choice';
    case 'clutch_survived':
      return 'risky_engage';
    case 'player_hit':
      return 'defensive_pivot';
    case 'wave_completed':
      return 'wave_enter';
    default:
      return 'wave_enter'; // Default fallback
  }
}

/**
 * Calculate risk level based on context
 *
 * From .outline.md (L4):
 * risk = health * 0.4 + threat * 0.3 + situation * 0.3
 */
function calculateRisk(context: BuildContext): IntentMark['risk'] {
  const healthFraction = context.health / context.maxHealth;

  // Estimate threat based on wave
  const threatLevel = Math.min(context.wave / 10, 1);

  // Weighted risk score
  const riskScore =
    (1 - healthFraction) * 0.4 + threatLevel * 0.3 + (context.wave > 5 ? 0.3 : 0);

  if (riskScore >= 0.6) return 'high';
  if (riskScore >= 0.3) return 'medium';
  return 'low';
}

/**
 * Determine if the action was successful
 */
function determineSuccess(event: MarkEvent): boolean {
  switch (event.type) {
    case 'enemy_killed':
    case 'level_up':
    case 'wave_completed':
    case 'clutch_survived':
      return true;
    case 'player_hit':
      return (event.healthAfter || 0) > 0; // Survived the hit
    case 'run_ended':
      return !event.deathCause; // Victory if no death cause
    default:
      return true;
  }
}

/**
 * Describe the consequence of an action
 */
function describeConsequence(event: MarkEvent): string {
  switch (event.type) {
    case 'enemy_killed':
      return `Enemy eliminated at wave ${event.context.wave}`;
    case 'player_hit':
      return `Took ${event.damage || 0} damage, ${event.healthAfter || 0} HP remaining`;
    case 'level_up':
      return `Reached level ${event.level}`;
    case 'upgrade_selected':
      return `Selected ${event.upgrade}, passed on ${event.alternatives?.join(', ') || 'nothing'}`;
    case 'wave_completed':
      return `Cleared wave ${event.wave}`;
    case 'clutch_survived':
      return `Survived clutch moment at ${Math.round((event.context.health / event.context.maxHealth) * 100)}% HP`;
    case 'run_ended':
      return event.deathCause
        ? `Run ended by ${event.deathCause}`
        : `Victorious at wave ${event.context.wave}`;
    default:
      return 'Action completed';
  }
}

/**
 * Estimate skill metrics from current context
 */
function estimateSkillMetrics(
  _ctx: WitnessContext,
  event: MarkEvent
): SkillMetrics {
  const context = event.context;

  // Simple heuristic-based skill estimation
  const damageEfficiency = Math.min(context.enemiesKilled / (context.wave * 10 + 1), 1);
  const dodgeRate = context.health / context.maxHealth;
  const buildFocus = context.synergies.length > 0 ? 0.7 : 0.3;
  const riskTolerance = context.upgrades.includes('damage_up') ? 0.7 : 0.4;

  const estimate = (damageEfficiency + dodgeRate + buildFocus) / 3;

  return {
    damageEfficiency,
    dodgeRate,
    buildFocus,
    riskTolerance,
    estimate,
  };
}

/**
 * Calculate projected drift for a decision
 */
function calculateDrift(_ctx: WitnessContext, event: MarkEvent): number {
  // Simple drift calculation based on how different this choice is
  // from the player's established pattern
  const previousUpgrades = event.context.upgrades;

  if (previousUpgrades.length === 0) return 0;

  // Check if this upgrade type matches the pattern
  const currentType = event.upgrade?.split('_')[0] || '';
  const matchingCount = previousUpgrades.filter((u) =>
    u.startsWith(currentType)
  ).length;

  // Lower drift if staying on pattern, higher if diverging
  return 1 - matchingCount / previousUpgrades.length;
}

// =============================================================================
// Trace Management
// =============================================================================

/**
 * Seal the trace (run ended)
 */
export function sealTrace(ctx: WitnessContext, deathCause: string | null): Trace {
  return {
    runId: ctx.runId,
    startTime: ctx.startTime,
    endTime: Date.now(),
    marks: ctx.marks,
    finalContext:
      ctx.marks.length > 0
        ? ctx.marks[ctx.marks.length - 1].intent.context
        : {
            wave: 0,
            health: 0,
            maxHealth: 100,
            upgrades: [],
            synergies: [],
            xp: 0,
            enemiesKilled: 0,
          },
    deathCause,
    sealed: true,
  };
}

// =============================================================================
// Crystal Compression
// =============================================================================

/**
 * Compress a trace into a GameCrystal (proof of run)
 * Implements DD-3: Crystal as Proof
 */
export function crystallize(ctx: WitnessContext, trace: Trace): GameCrystal {
  const segments = createSegments(trace);
  const weights = calculateFinalWeights(trace);
  const driftHistory = calculateDriftHistory(trace);

  // Generate narrative title
  const title = generateTitle(trace, weights);
  const claim = generateClaim(trace, weights);

  // Create shareable text (Twitter-sized)
  const shareableText = createShareableText(trace, claim);
  const shareableHash = generateHash(ctx.runId);

  return {
    runId: ctx.runId,
    segments,
    title,
    claim,
    duration: trace.endTime - trace.startTime,
    waveReached:
      trace.marks.length > 0
        ? trace.marks[trace.marks.length - 1].intent.context.wave
        : 0,
    finalWeights: weights,
    driftHistory,
    ghostCount: ctx.ghosts.length,
    pivotMoments: countPivotMoments(trace),
    shareableText,
    shareableHash,
  };
}

/**
 * Create narrative segments from trace
 */
function createSegments(trace: Trace): CrystalSegment[] {
  const segments: CrystalSegment[] = [];

  // Group marks by wave ranges
  let currentSegment: CrystalSegment | null = null;
  let currentWaveStart = 1;

  for (const mark of trace.marks) {
    const wave = mark.intent.context.wave;

    // Start new segment every 3 waves or on emotional shift
    if (!currentSegment || wave >= currentWaveStart + 3) {
      if (currentSegment) {
        segments.push(currentSegment);
      }

      currentWaveStart = wave;
      currentSegment = {
        waves: [wave, wave],
        narrative: '',
        emotion: detectEmotion(mark),
        keyMoments: [],
      };
    }

    // Update segment
    currentSegment.waves[1] = wave;
    if (mark.outcome?.consequence) {
      currentSegment.keyMoments.push(mark.outcome.consequence);
    }
  }

  // Add final segment
  if (currentSegment) {
    currentSegment.narrative = generateSegmentNarrative(currentSegment);
    segments.push(currentSegment);
  }

  return segments;
}

/**
 * Detect emotional phase from a mark
 */
function detectEmotion(mark: WitnessMark): CrystalSegment['emotion'] {
  const context = mark.intent.context;
  const healthFraction = context.health / context.maxHealth;

  if (healthFraction < 0.2) return 'crisis';
  if (context.wave <= 2) return 'hope';
  if (mark.intent.type === 'upgrade_choice') return 'flow';
  if (!mark.outcome?.success) return 'grief';
  return 'triumph';
}

/**
 * Generate narrative for a segment
 */
function generateSegmentNarrative(segment: CrystalSegment): string {
  const [startWave, endWave] = segment.waves;
  const keyMoment = segment.keyMoments[0] || 'progressed steadily';

  switch (segment.emotion) {
    case 'hope':
      return `Waves ${startWave}-${endWave}: The journey began with promise. ${keyMoment}.`;
    case 'flow':
      return `Waves ${startWave}-${endWave}: Found rhythm in the chaos. ${keyMoment}.`;
    case 'crisis':
      return `Waves ${startWave}-${endWave}: Survival on the edge. ${keyMoment}.`;
    case 'triumph':
      return `Waves ${startWave}-${endWave}: Victory earned through persistence. ${keyMoment}.`;
    case 'grief':
      return `Waves ${startWave}-${endWave}: The end came. ${keyMoment}.`;
    default:
      return `Waves ${startWave}-${endWave}: ${keyMoment}.`;
  }
}

/**
 * Calculate final principle weights from trace
 */
function calculateFinalWeights(trace: Trace): GamePrincipleWeights {
  // Analyze upgrade patterns to determine playstyle
  const context = trace.finalContext;
  const upgrades = context.upgrades;

  let aggression = 0.5;
  let defense = 0.5;
  let mobility = 0.5;
  let precision = 0.5;
  let synergy = 0.3;

  for (const upgrade of upgrades) {
    if (upgrade.includes('damage')) aggression += 0.1;
    if (upgrade.includes('health')) defense += 0.1;
    if (upgrade.includes('speed')) mobility += 0.1;
    if (upgrade.includes('range')) precision += 0.1;
  }

  // Synergy from synergies
  synergy = Math.min(0.3 + context.synergies.length * 0.15, 1);

  // Normalize
  const total = aggression + defense + mobility + precision + synergy;
  return {
    aggression: aggression / total,
    defense: defense / total,
    mobility: mobility / total,
    precision: precision / total,
    synergy: synergy / total,
  };
}

/**
 * Calculate drift history through the run
 */
function calculateDriftHistory(
  _trace: Trace
): GameCrystal['driftHistory'] {
  // Simplified - would normally track actual drift over time
  return [
    {
      loss: 0.1,
      drift: 'stable',
      dominant: 'aggression',
      message: 'Consistent aggressive style',
    },
  ];
}

/**
 * Generate a title for the run
 */
function generateTitle(trace: Trace, weights: GamePrincipleWeights): string {
  const wave = trace.finalContext.wave;
  const dominant = Object.entries(weights).sort((a, b) => b[1] - a[1])[0][0];

  const titleParts: Record<string, string> = {
    aggression: 'The Relentless',
    defense: 'The Steadfast',
    mobility: 'The Swift',
    precision: 'The Precise',
    synergy: 'The Harmonious',
  };

  return `${titleParts[dominant] || 'The Survivor'} (Wave ${wave})`;
}

/**
 * Generate the claim (one-sentence proof)
 */
function generateClaim(trace: Trace, weights: GamePrincipleWeights): string {
  const wave = trace.finalContext.wave;
  const kills = trace.finalContext.enemiesKilled;
  const dominant = Object.entries(weights).sort((a, b) => b[1] - a[1])[0][0];

  const styleDescriptions: Record<string, string> = {
    aggression: 'aggressive efficiency',
    defense: 'careful persistence',
    mobility: 'swift maneuvering',
    precision: 'calculated strikes',
    synergy: 'synergistic builds',
  };

  return `Survived ${wave} waves and eliminated ${kills} enemies through ${styleDescriptions[dominant] || 'pure determination'}.`;
}

/**
 * Create Twitter-sized shareable text
 */
function createShareableText(trace: Trace, claim: string): string {
  const wave = trace.finalContext.wave;
  return `WASM Survivors: ${claim} #WASMSurvivors #Wave${wave}`.slice(0, 280);
}

/**
 * Generate a hash for the run
 */
function generateHash(runId: string): string {
  // Simple hash - would use proper cryptographic hash in production
  let hash = 0;
  for (let i = 0; i < runId.length; i++) {
    const char = runId.charCodeAt(i);
    hash = (hash << 5) - hash + char;
    hash = hash & hash; // Convert to 32bit integer
  }
  return Math.abs(hash).toString(36).slice(0, 8);
}

/**
 * Count major pivot moments in the trace
 */
function countPivotMoments(trace: Trace): number {
  // Count high-risk moments that succeeded
  return trace.marks.filter(
    (m) => m.intent.risk === 'high' && m.outcome?.success
  ).length;
}
