/**
 * WASM Survivors - Witness-Adaptive Bridge
 *
 * Bridges the Witness system (marks, crystals, ghosts) with the adaptive mechanics system.
 * Every adaptation decision is witnessed and made transparent to the player.
 *
 * Core Principle: "The proof IS the decision. The mark IS the witness."
 *
 * This system provides:
 * 1. AdaptationWitnessMark - Transparent record of every adaptation decision
 * 2. AdaptationReview - Player interface for reviewing and overriding adaptations
 * 3. AmberMemory - Enhanced crystal with adaptation context at death
 * 4. PlayerLearningProfile - Cross-run learning and insights
 * 5. UI Hooks - React hooks for displaying adaptation info
 * 6. AdaptationNotification - Player-facing notifications
 *
 * @see pilots/wasm-survivors-game/systems/witness.ts
 * @see spec/theory/domains/wasm-survivors-quality.md
 */

import type {
  GameCrystal,
  GameState,
  SkillMetrics,
  GamePrincipleWeights,
} from '../types';
import type { UpgradeType } from './upgrades';

// =============================================================================
// Adaptation Types
// =============================================================================

/**
 * Types of adaptations the game can make.
 * Each type represents a different way the game adjusts to player skill.
 */
export type AdaptationType =
  | 'spawn_rate'           // Adjust enemy spawn frequency
  | 'enemy_health'         // Scale enemy health
  | 'enemy_damage'         // Scale enemy damage
  | 'upgrade_weighting'    // Bias upgrade offerings based on player tendencies
  | 'mercy_mode'           // Reduce difficulty after repeated deaths
  | 'challenge_mode'       // Increase difficulty for skilled players
  | 'healing_availability' // Adjust heal drop frequency
  | 'wave_pacing';         // Adjust time between waves

/**
 * Inputs that drive adaptation decisions.
 * This data is exposed to the player for full transparency.
 */
export interface AdaptationInputs {
  /** Overall skill score (0-1) */
  playerSkillScore: number;
  /** Number of deaths in recent runs */
  recentDeaths: number;
  /** Average survival time in seconds */
  averageSurvivalTime: number;
  /** Which upgrades the player tends to pick */
  preferredUpgrades: UpgradeType[];
  /** Which upgrades the player avoids */
  avoidedUpgrades: UpgradeType[];
  /** Current run metrics */
  currentRunMetrics: {
    timeSurvived: number;
    wavesReached: number;
    enemiesKilled: number;
    damagesTaken: number;
    healingUsed: number;
  };
  /** Skill metrics from witness system */
  skillMetrics: SkillMetrics;
  /** Number of consecutive short runs (<30s) */
  consecutiveQuickDeaths: number;
  /** Number of consecutive long runs (>5 waves) */
  consecutiveGoodRuns: number;
}

/**
 * Output of an adaptation decision.
 * What changes were actually made to the game.
 */
export interface AdaptationOutput {
  /** Multiplier for spawn rate (1.0 = normal, <1.0 = slower, >1.0 = faster) */
  spawnRateMultiplier?: number;
  /** Multiplier for enemy health */
  enemyHealthMultiplier?: number;
  /** Multiplier for enemy damage */
  enemyDamageMultiplier?: number;
  /** Changes to upgrade offering weights */
  upgradeWeightChanges?: Partial<Record<UpgradeType, number>>;
  /** Whether mercy mode was activated */
  mercyModeActivated?: boolean;
  /** Whether challenge mode was activated */
  challengeModeActivated?: boolean;
  /** Multiplier for heal drops */
  healingMultiplier?: number;
  /** Multiplier for wave pause duration */
  wavePauseMultiplier?: number;
}

/**
 * A witnessed adaptation decision.
 * This is the core artifact that provides transparency into the game's adaptive behavior.
 */
export interface AdaptationWitnessMark {
  /** Unique identifier for this adaptation */
  id: string;
  /** When this adaptation was decided */
  timestamp: number;
  /** Game time when adaptation was decided */
  gameTime: number;
  /** Run ID this adaptation belongs to */
  runId: string;

  /** What type of adaptation was made */
  adaptationType: AdaptationType;

  /** What data drove the decision (transparent!) */
  inputs: AdaptationInputs;

  /** What was decided */
  output: AdaptationOutput;

  /**
   * Human-readable explanation.
   * This is the key to transparency - a plain English explanation of WHY.
   * e.g., "Player died 5 times in <30s. Reducing spawn rate by 20%."
   */
  reasoning: string;

  /** How confident the system is in this adaptation (0-1) */
  confidence: number;

  /** Whether the player manually overrode this adaptation */
  wasOverridden: boolean;
}

// =============================================================================
// Player Review Interface
// =============================================================================

/**
 * Override settings for a specific adaptation type.
 */
export type AdaptationOverride = 'enable' | 'disable' | 'default';

/**
 * Interface for player review and control of adaptations.
 * Players can see why the game adapted and choose to override.
 */
export interface AdaptationReview {
  /** Get all adaptations for current run */
  getCurrentRunAdaptations(): AdaptationWitnessMark[];

  /** Get adaptation history across runs */
  getHistoricalAdaptations(limit?: number): AdaptationWitnessMark[];

  /** Explain a specific adaptation in detail */
  explainAdaptation(markId: string): AdaptationExplanation;

  /** Player can override specific adaptation types */
  overrideAdaptation(type: AdaptationType, value: AdaptationOverride): void;

  /** Get current override settings */
  getOverrides(): Partial<Record<AdaptationType, AdaptationOverride>>;

  /** Reset all overrides to default */
  resetOverrides(): void;

  /** Get summary statistics */
  getSummary(): AdaptationSummary;
}

/**
 * Detailed explanation of an adaptation.
 */
export interface AdaptationExplanation {
  /** The original mark */
  mark: AdaptationWitnessMark;
  /** Plain English breakdown of the decision */
  explanation: string;
  /** Key factors that influenced this decision */
  keyFactors: Array<{
    factor: string;
    value: string | number;
    impact: 'major' | 'minor';
  }>;
  /** What the game would be like without this adaptation */
  counterfactual: string;
  /** Suggestions for the player */
  suggestions?: string[];
}

/**
 * Summary statistics for adaptations.
 */
export interface AdaptationSummary {
  totalAdaptations: number;
  adaptationsByType: Partial<Record<AdaptationType, number>>;
  mercyModeActivations: number;
  challengeModeActivations: number;
  averageSkillScore: number;
  trendDirection: 'improving' | 'stable' | 'struggling';
}

// =============================================================================
// Amber Memory (Enhanced Crystal)
// =============================================================================

/**
 * Adaptation context preserved in the player's Amber Memory (death crystal).
 * This captures what the game "knew" about the player at death.
 */
export interface AdaptationContext {
  /** Active adaptations at the moment of death */
  activeAdaptations: AdaptationWitnessMark[];
  /** Whether mercy mode was active */
  mercyModeWasActive: boolean;
  /** Whether challenge mode was active */
  challengeModeWasActive: boolean;
  /** Estimated player skill at death (0-1) */
  estimatedPlayerSkill: number;
  /** What the game learned from this run */
  runInsights: string[];
  /** Suggested adaptations for next run */
  suggestedNextRunAdaptations: AdaptationType[];
}

/**
 * Extended crystal that includes adaptation context.
 * The Amber Memory is a crystal with the ghost of the game's understanding.
 */
export interface AmberMemory extends GameCrystal {
  /** Adaptation context at death */
  adaptationContext: AdaptationContext;
  /** The game's understanding of this player */
  playerProfile: PlayerProfileSnapshot;
  /** Wisdom for the next run */
  wisdomForNextRun: string;
}

/**
 * Snapshot of player profile at a moment in time.
 */
export interface PlayerProfileSnapshot {
  skillLevel: 'beginner' | 'learning' | 'intermediate' | 'advanced' | 'master';
  dominantPlaystyle: keyof GamePrincipleWeights;
  strengths: string[];
  weaknesses: string[];
}

// =============================================================================
// Cross-Run Learning
// =============================================================================

/**
 * A single data point in skill progression over time.
 */
export interface SkillDataPoint {
  timestamp: number;
  runId: string;
  skillScore: number;
  wavesReached: number;
  survivalTime: number;
  /** What caused the change */
  changeReason?: string;
}

/**
 * An insight the game has learned about the player.
 */
export interface PlayerInsight {
  /** What kind of insight this is */
  type: 'strength' | 'weakness' | 'preference' | 'pattern';
  /** Human-readable description */
  description: string;
  /** How confident we are in this insight (0-1) */
  confidence: number;
  /** What data supports this conclusion */
  evidence: string[];
  /** When this insight was formed */
  formedAt: number;
  /** How many runs contributed to this insight */
  supportingRuns: number;
}

/**
 * Player preferences for adaptation behavior.
 * The player has ultimate control over how the game adapts.
 */
export interface AdaptationPreferences {
  /** Allow the game to adjust difficulty based on performance */
  allowDifficultyAdjustment: boolean;
  /** Allow the game to bias upgrade offerings */
  allowUpgradeWeighting: boolean;
  /** Show notifications when adaptations trigger */
  showAdaptationNotifications: boolean;
  /** Allow mercy mode to activate */
  allowMercyMode: boolean;
  /** Allow challenge mode to activate */
  allowChallengeMode: boolean;
}

/**
 * Long-term learning profile that persists across sessions.
 */
export interface PlayerLearningProfile {
  /** Player identifier (anonymous or authenticated) */
  playerId: string;
  /** When this profile was created */
  createdAt: number;
  /** Last time this profile was updated */
  updatedAt: number;

  /** Skill progression over time */
  skillProgression: SkillDataPoint[];

  /** What the game has learned about this player */
  insights: PlayerInsight[];

  /** Player's preferred adaptation settings */
  preferences: AdaptationPreferences;

  /** Historical adaptation marks (limited to recent history) */
  recentAdaptations: AdaptationWitnessMark[];

  /** Build preference statistics */
  buildStats: {
    /** How often each upgrade is selected */
    upgradeSelectionRates: Partial<Record<UpgradeType, number>>;
    /** Which synergies have been discovered */
    discoveredSynergies: string[];
    /** Favorite build patterns */
    favoriteBuildPatterns: string[];
  };

  /** Death analysis */
  deathAnalysis: {
    /** Most common causes of death */
    commonDeathCauses: Array<{ cause: string; count: number }>;
    /** Average survival time by wave */
    survivalByWave: Array<{ wave: number; avgTime: number }>;
    /** Quick death frequency (metric for mercy mode) */
    quickDeathRate: number;
  };
}

// =============================================================================
// Notification System
// =============================================================================

/**
 * A notification shown to the player about an adaptation.
 */
export interface AdaptationNotification {
  /** Type affects styling and priority */
  type: 'info' | 'encouragement' | 'challenge';
  /** Main message (short, clear) */
  message: string;
  /** Optional details for players who want more info */
  details?: string;
  /** Whether the player can dismiss this */
  dismissable: boolean;
  /** How long to show (ms), undefined = until dismissed */
  duration?: number;
  /** The adaptation that triggered this notification */
  relatedAdaptation?: AdaptationWitnessMark;
}

// =============================================================================
// Adaptation Context (Runtime State)
// =============================================================================

/**
 * Runtime state for the adaptation system.
 */
export interface AdaptationState {
  /** Current run ID */
  runId: string;
  /** Marks from this run */
  runMarks: AdaptationWitnessMark[];
  /** Currently active output (combined from all adaptations) */
  activeOutput: AdaptationOutput;
  /** Player overrides */
  overrides: Partial<Record<AdaptationType, AdaptationOverride>>;
  /** Pending notifications to show */
  pendingNotifications: AdaptationNotification[];
  /** Whether mercy mode is currently active */
  mercyModeActive: boolean;
  /** Whether challenge mode is currently active */
  challengeModeActive: boolean;
}

// =============================================================================
// Core Bridge Functions
// =============================================================================

/**
 * Create initial adaptation state for a new run.
 */
export function createAdaptationState(runId: string): AdaptationState {
  return {
    runId,
    runMarks: [],
    activeOutput: {},
    overrides: {},
    pendingNotifications: [],
    mercyModeActive: false,
    challengeModeActive: false,
  };
}

/**
 * Create default player preferences.
 */
export function createDefaultPreferences(): AdaptationPreferences {
  return {
    allowDifficultyAdjustment: true,
    allowUpgradeWeighting: true,
    showAdaptationNotifications: true,
    allowMercyMode: true,
    allowChallengeMode: true,
  };
}

/**
 * Create a new player learning profile.
 */
export function createPlayerLearningProfile(playerId: string): PlayerLearningProfile {
  return {
    playerId,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    skillProgression: [],
    insights: [],
    preferences: createDefaultPreferences(),
    recentAdaptations: [],
    buildStats: {
      upgradeSelectionRates: {},
      discoveredSynergies: [],
      favoriteBuildPatterns: [],
    },
    deathAnalysis: {
      commonDeathCauses: [],
      survivalByWave: [],
      quickDeathRate: 0,
    },
  };
}

/**
 * Generate a unique adaptation mark ID.
 */
function generateMarkId(): string {
  return `adapt-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`;
}

// =============================================================================
// Adaptation Decision Engine
// =============================================================================

/**
 * Calculate adaptation inputs from game state and profile.
 */
export function calculateAdaptationInputs(
  gameState: GameState,
  profile: PlayerLearningProfile | null,
  runMetrics: AdaptationInputs['currentRunMetrics']
): AdaptationInputs {
  const recentSkill = profile?.skillProgression.slice(-10) ?? [];
  const avgSkill = recentSkill.length > 0
    ? recentSkill.reduce((sum, p) => sum + p.skillScore, 0) / recentSkill.length
    : 0.5;

  const recentDeaths = profile?.deathAnalysis.commonDeathCauses.reduce(
    (sum, c) => sum + c.count, 0
  ) ?? 0;

  const avgSurvivalTime = recentSkill.length > 0
    ? recentSkill.reduce((sum, p) => sum + p.survivalTime, 0) / recentSkill.length
    : 60;

  // Calculate preferred/avoided upgrades from selection rates
  const selectionRates = profile?.buildStats.upgradeSelectionRates ?? {};
  const upgradeEntries = Object.entries(selectionRates) as [UpgradeType, number][];
  const avgRate = upgradeEntries.length > 0
    ? upgradeEntries.reduce((sum, [, rate]) => sum + rate, 0) / upgradeEntries.length
    : 0;

  const preferredUpgrades = upgradeEntries
    .filter(([, rate]) => rate > avgRate * 1.5)
    .map(([type]) => type);

  const avoidedUpgrades = upgradeEntries
    .filter(([, rate]) => rate < avgRate * 0.5)
    .map(([type]) => type);

  // Count consecutive quick deaths (<30s)
  const consecutiveQuickDeaths = countConsecutiveQuickDeaths(profile?.skillProgression ?? []);
  const consecutiveGoodRuns = countConsecutiveGoodRuns(profile?.skillProgression ?? []);

  return {
    playerSkillScore: avgSkill,
    recentDeaths,
    averageSurvivalTime: avgSurvivalTime,
    preferredUpgrades,
    avoidedUpgrades,
    currentRunMetrics: runMetrics,
    skillMetrics: {
      damageEfficiency: 0.5,
      dodgeRate: gameState.player.health / gameState.player.maxHealth,
      buildFocus: (gameState.player.synergies?.length ?? 0) > 0 ? 0.7 : 0.3,
      riskTolerance: 0.5,
      estimate: avgSkill,
    },
    consecutiveQuickDeaths,
    consecutiveGoodRuns,
  };
}

/**
 * Count consecutive quick deaths (survival < 30s).
 */
function countConsecutiveQuickDeaths(progression: SkillDataPoint[]): number {
  let count = 0;
  for (let i = progression.length - 1; i >= 0; i--) {
    if (progression[i].survivalTime < 30) {
      count++;
    } else {
      break;
    }
  }
  return count;
}

/**
 * Count consecutive good runs (5+ waves).
 */
function countConsecutiveGoodRuns(progression: SkillDataPoint[]): number {
  let count = 0;
  for (let i = progression.length - 1; i >= 0; i--) {
    if (progression[i].wavesReached >= 5) {
      count++;
    } else {
      break;
    }
  }
  return count;
}

/**
 * Decide on adaptations based on inputs and preferences.
 * Returns a list of adaptation marks to apply.
 */
export function decideAdaptations(
  inputs: AdaptationInputs,
  preferences: AdaptationPreferences,
  overrides: Partial<Record<AdaptationType, AdaptationOverride>>,
  runId: string,
  gameTime: number
): AdaptationWitnessMark[] {
  const marks: AdaptationWitnessMark[] = [];

  // Helper to check if adaptation is allowed
  const isAllowed = (type: AdaptationType): boolean => {
    const override = overrides[type];
    if (override === 'disable') return false;
    if (override === 'enable') return true;

    // Check preferences
    if (type === 'mercy_mode' && !preferences.allowMercyMode) return false;
    if (type === 'challenge_mode' && !preferences.allowChallengeMode) return false;
    if (
      ['spawn_rate', 'enemy_health', 'enemy_damage'].includes(type) &&
      !preferences.allowDifficultyAdjustment
    ) return false;
    if (type === 'upgrade_weighting' && !preferences.allowUpgradeWeighting) return false;

    return true;
  };

  // Mercy mode: Triggered by consecutive quick deaths
  if (
    isAllowed('mercy_mode') &&
    inputs.consecutiveQuickDeaths >= 3
  ) {
    const reduction = Math.min(0.1 + inputs.consecutiveQuickDeaths * 0.05, 0.3);
    marks.push({
      id: generateMarkId(),
      timestamp: Date.now(),
      gameTime,
      runId,
      adaptationType: 'mercy_mode',
      inputs,
      output: {
        spawnRateMultiplier: 1 - reduction,
        enemyDamageMultiplier: 1 - reduction * 0.5,
        mercyModeActivated: true,
        healingMultiplier: 1 + reduction,
      },
      reasoning: `Player died ${inputs.consecutiveQuickDeaths} times in under 30 seconds. ` +
        `Reducing spawn rate by ${Math.round(reduction * 100)}% and boosting healing to help you find your footing.`,
      confidence: 0.9,
      wasOverridden: false,
    });
  }

  // Challenge mode: Triggered by consecutive good runs
  if (
    isAllowed('challenge_mode') &&
    inputs.consecutiveGoodRuns >= 3 &&
    inputs.playerSkillScore > 0.7
  ) {
    const increase = Math.min(0.05 + inputs.consecutiveGoodRuns * 0.03, 0.2);
    marks.push({
      id: generateMarkId(),
      timestamp: Date.now(),
      gameTime,
      runId,
      adaptationType: 'challenge_mode',
      inputs,
      output: {
        spawnRateMultiplier: 1 + increase,
        enemyHealthMultiplier: 1 + increase * 0.5,
        challengeModeActivated: true,
      },
      reasoning: `You've dominated ${inputs.consecutiveGoodRuns} runs in a row with skill score ${(inputs.playerSkillScore * 100).toFixed(0)}%. ` +
        `The hive is adapting to your prowess - expect ${Math.round(increase * 100)}% more resistance.`,
      confidence: 0.85,
      wasOverridden: false,
    });
  }

  // Upgrade weighting: Suggest underused upgrades
  if (
    isAllowed('upgrade_weighting') &&
    inputs.avoidedUpgrades.length > 0 &&
    Math.random() < 0.3 // Don't always suggest
  ) {
    const suggestedUpgrade = inputs.avoidedUpgrades[
      Math.floor(Math.random() * inputs.avoidedUpgrades.length)
    ];
    marks.push({
      id: generateMarkId(),
      timestamp: Date.now(),
      gameTime,
      runId,
      adaptationType: 'upgrade_weighting',
      inputs,
      output: {
        upgradeWeightChanges: { [suggestedUpgrade]: 1.5 },
      },
      reasoning: `You rarely pick "${suggestedUpgrade}" but it might complement your playstyle. ` +
        `Increasing its appearance rate slightly.`,
      confidence: 0.6,
      wasOverridden: false,
    });
  }

  // Spawn rate adjustment based on skill
  if (
    isAllowed('spawn_rate') &&
    (inputs.playerSkillScore < 0.3 || inputs.playerSkillScore > 0.8)
  ) {
    const adjustment = inputs.playerSkillScore < 0.3
      ? -0.15
      : 0.1;
    const reason = inputs.playerSkillScore < 0.3
      ? `Your skill score (${(inputs.playerSkillScore * 100).toFixed(0)}%) suggests you're still learning. ` +
        `Slowing spawn rate by 15% to give you breathing room.`
      : `Your skill score (${(inputs.playerSkillScore * 100).toFixed(0)}%) shows mastery. ` +
        `Increasing spawn density by 10% for a greater challenge.`;

    marks.push({
      id: generateMarkId(),
      timestamp: Date.now(),
      gameTime,
      runId,
      adaptationType: 'spawn_rate',
      inputs,
      output: {
        spawnRateMultiplier: 1 + adjustment,
      },
      reasoning: reason,
      confidence: 0.75,
      wasOverridden: false,
    });
  }

  return marks;
}

/**
 * Apply adaptation marks to the state.
 */
export function applyAdaptations(
  state: AdaptationState,
  marks: AdaptationWitnessMark[],
  preferences: AdaptationPreferences
): AdaptationState {
  const newState = { ...state };

  for (const mark of marks) {
    newState.runMarks.push(mark);

    // Merge outputs
    newState.activeOutput = mergeAdaptationOutputs(newState.activeOutput, mark.output);

    // Track modes
    if (mark.output.mercyModeActivated) {
      newState.mercyModeActive = true;
    }
    if (mark.output.challengeModeActivated) {
      newState.challengeModeActive = true;
    }

    // Generate notification if enabled
    if (preferences.showAdaptationNotifications) {
      newState.pendingNotifications.push(
        createNotificationForMark(mark)
      );
    }
  }

  return newState;
}

/**
 * Merge two adaptation outputs, later values override earlier.
 */
function mergeAdaptationOutputs(
  base: AdaptationOutput,
  overlay: AdaptationOutput
): AdaptationOutput {
  return {
    spawnRateMultiplier: overlay.spawnRateMultiplier ?? base.spawnRateMultiplier,
    enemyHealthMultiplier: overlay.enemyHealthMultiplier ?? base.enemyHealthMultiplier,
    enemyDamageMultiplier: overlay.enemyDamageMultiplier ?? base.enemyDamageMultiplier,
    upgradeWeightChanges: {
      ...base.upgradeWeightChanges,
      ...overlay.upgradeWeightChanges,
    },
    mercyModeActivated: overlay.mercyModeActivated ?? base.mercyModeActivated,
    challengeModeActivated: overlay.challengeModeActivated ?? base.challengeModeActivated,
    healingMultiplier: overlay.healingMultiplier ?? base.healingMultiplier,
    wavePauseMultiplier: overlay.wavePauseMultiplier ?? base.wavePauseMultiplier,
  };
}

/**
 * Create a notification for an adaptation mark.
 */
function createNotificationForMark(mark: AdaptationWitnessMark): AdaptationNotification {
  switch (mark.adaptationType) {
    case 'mercy_mode':
      return {
        type: 'encouragement',
        message: 'The swarm is giving you a moment to breathe.',
        details: mark.reasoning,
        dismissable: true,
        duration: 5000,
        relatedAdaptation: mark,
      };

    case 'challenge_mode':
      return {
        type: 'challenge',
        message: 'The hive senses your skill. They are mobilizing faster.',
        details: mark.reasoning,
        dismissable: true,
        duration: 5000,
        relatedAdaptation: mark,
      };

    case 'upgrade_weighting':
      const suggestedUpgrade = Object.keys(mark.output.upgradeWeightChanges || {})[0];
      return {
        type: 'info',
        message: `Consider trying "${suggestedUpgrade}" - it might suit your style.`,
        details: mark.reasoning,
        dismissable: true,
        duration: 4000,
        relatedAdaptation: mark,
      };

    default:
      return {
        type: 'info',
        message: 'The game has adapted to your playstyle.',
        details: mark.reasoning,
        dismissable: true,
        duration: 3000,
        relatedAdaptation: mark,
      };
  }
}

// =============================================================================
// Crystal Enhancement (Amber Memory)
// =============================================================================

/**
 * Enhance a GameCrystal with adaptation context to create an AmberMemory.
 */
export function createAmberMemory(
  crystal: GameCrystal,
  state: AdaptationState,
  profile: PlayerLearningProfile | null
): AmberMemory {
  // Determine suggested adaptations for next run
  const suggestedNext: AdaptationType[] = [];

  // If mercy mode was active, suggest keeping it
  if (state.mercyModeActive) {
    suggestedNext.push('mercy_mode');
  }

  // If player is improving, maybe suggest challenge mode
  const skillTrend = calculateSkillTrend(profile?.skillProgression ?? []);
  if (skillTrend === 'improving' && !state.challengeModeActive) {
    suggestedNext.push('challenge_mode');
  }

  // Analyze run for insights
  const runInsights: string[] = [];
  if (state.mercyModeActive) {
    runInsights.push('Mercy mode helped you survive longer this run.');
  }
  if (crystal.waveReached > 5) {
    runInsights.push('You broke through wave 5 - builds are working!');
  }
  if (crystal.pivotMoments > 3) {
    runInsights.push('You handled multiple crisis moments with skill.');
  }

  // Generate wisdom for next run
  const wisdom = generateWisdomForNextRun(crystal, state, profile);

  // Create player profile snapshot
  const profileSnapshot: PlayerProfileSnapshot = {
    skillLevel: determineSkillLevel(profile?.skillProgression ?? []),
    dominantPlaystyle: Object.entries(crystal.finalWeights)
      .sort((a, b) => b[1] - a[1])[0][0] as keyof GamePrincipleWeights,
    strengths: extractStrengths(crystal, profile),
    weaknesses: extractWeaknesses(crystal, profile),
  };

  return {
    ...crystal,
    adaptationContext: {
      activeAdaptations: state.runMarks,
      mercyModeWasActive: state.mercyModeActive,
      challengeModeWasActive: state.challengeModeActive,
      estimatedPlayerSkill: profile?.skillProgression.slice(-1)[0]?.skillScore ?? 0.5,
      runInsights,
      suggestedNextRunAdaptations: suggestedNext,
    },
    playerProfile: profileSnapshot,
    wisdomForNextRun: wisdom,
  };
}

/**
 * Calculate skill trend from progression data.
 */
function calculateSkillTrend(
  progression: SkillDataPoint[]
): 'improving' | 'stable' | 'struggling' {
  if (progression.length < 3) return 'stable';

  const recent = progression.slice(-5);
  const older = progression.slice(-10, -5);

  if (older.length === 0) return 'stable';

  const recentAvg = recent.reduce((sum, p) => sum + p.skillScore, 0) / recent.length;
  const olderAvg = older.reduce((sum, p) => sum + p.skillScore, 0) / older.length;

  if (recentAvg > olderAvg + 0.1) return 'improving';
  if (recentAvg < olderAvg - 0.1) return 'struggling';
  return 'stable';
}

/**
 * Determine skill level from progression.
 */
function determineSkillLevel(
  progression: SkillDataPoint[]
): PlayerProfileSnapshot['skillLevel'] {
  if (progression.length === 0) return 'beginner';

  const recent = progression.slice(-5);
  const avgSkill = recent.reduce((sum, p) => sum + p.skillScore, 0) / recent.length;
  const avgWaves = recent.reduce((sum, p) => sum + p.wavesReached, 0) / recent.length;

  if (avgSkill > 0.9 && avgWaves > 10) return 'master';
  if (avgSkill > 0.7 && avgWaves > 7) return 'advanced';
  if (avgSkill > 0.5 && avgWaves > 4) return 'intermediate';
  if (avgSkill > 0.3) return 'learning';
  return 'beginner';
}

/**
 * Extract player strengths from crystal and profile.
 */
function extractStrengths(
  crystal: GameCrystal,
  profile: PlayerLearningProfile | null
): string[] {
  const strengths: string[] = [];

  // From crystal weights
  const weights = crystal.finalWeights;
  if (weights.aggression > 0.25) strengths.push('Aggressive damage dealing');
  if (weights.defense > 0.25) strengths.push('Defensive play');
  if (weights.mobility > 0.25) strengths.push('Mobile positioning');
  if (weights.synergy > 0.25) strengths.push('Build synergy discovery');

  // From profile
  if (profile) {
    const favorite = profile.buildStats.favoriteBuildPatterns[0];
    if (favorite) strengths.push(`${favorite} builds`);
    if (profile.deathAnalysis.quickDeathRate < 0.2) {
      strengths.push('Consistent survival');
    }
  }

  return strengths.slice(0, 3);
}

/**
 * Extract player weaknesses from crystal and profile.
 */
function extractWeaknesses(
  crystal: GameCrystal,
  profile: PlayerLearningProfile | null
): string[] {
  const weaknesses: string[] = [];

  // From crystal
  if (crystal.pivotMoments < 2 && crystal.waveReached > 3) {
    weaknesses.push('Rarely take risks');
  }
  if (crystal.ghostCount > 10) {
    weaknesses.push('Decision paralysis on upgrades');
  }

  // From profile
  if (profile) {
    if (profile.deathAnalysis.quickDeathRate > 0.5) {
      weaknesses.push('Early game survival');
    }
    const commonDeath = profile.deathAnalysis.commonDeathCauses[0];
    if (commonDeath) {
      weaknesses.push(`Vulnerable to ${commonDeath.cause}`);
    }
  }

  return weaknesses.slice(0, 3);
}

/**
 * Generate wisdom message for next run.
 */
function generateWisdomForNextRun(
  crystal: GameCrystal,
  state: AdaptationState,
  profile: PlayerLearningProfile | null
): string {
  // Contextual wisdom based on how this run went
  if (state.mercyModeActive && crystal.waveReached > 5) {
    return 'Mercy mode helped, but you proved you can handle the pressure. Try without it next time.';
  }

  if (crystal.pivotMoments > 5) {
    return 'Your clutch survival instincts are sharp. Trust them and push deeper.';
  }

  if (crystal.ghostCount > 8) {
    const dominant = Object.entries(crystal.finalWeights)
      .sort((a, b) => b[1] - a[1])[0][0];
    return `Focus on ${dominant}-based upgrades. Your ghosts suggest indecision hurts more than wrong choices.`;
  }

  if (profile && profile.buildStats.discoveredSynergies.length === 0) {
    return 'Synergies unlock powerful combos. Try picking related upgrades (e.g., pierce + multishot).';
  }

  if (crystal.waveReached <= 2) {
    return 'Early survival is key. Focus on movement and avoid clusters until you get your first upgrade.';
  }

  return 'Every run teaches something. Your next run starts where this one left off in spirit.';
}

// =============================================================================
// Profile Update Functions
// =============================================================================

/**
 * Update player learning profile after a run.
 */
export function updatePlayerProfile(
  profile: PlayerLearningProfile,
  crystal: GameCrystal,
  amberMemory: AmberMemory,
  state: AdaptationState
): PlayerLearningProfile {
  const now = Date.now();

  // Add skill data point
  const skillPoint: SkillDataPoint = {
    timestamp: now,
    runId: crystal.runId,
    skillScore: amberMemory.adaptationContext.estimatedPlayerSkill,
    wavesReached: crystal.waveReached,
    survivalTime: crystal.duration / 1000,
  };

  // Update insights based on new data
  const newInsights = generateNewInsights(profile, crystal, amberMemory);

  // Update death analysis
  const deathCause = crystal.segments[crystal.segments.length - 1]?.emotion === 'grief'
    ? 'combat' // Could be more specific with better data
    : 'unknown';

  const existingCauseIndex = profile.deathAnalysis.commonDeathCauses.findIndex(
    c => c.cause === deathCause
  );

  const updatedCauses = [...profile.deathAnalysis.commonDeathCauses];
  if (existingCauseIndex >= 0) {
    updatedCauses[existingCauseIndex] = {
      ...updatedCauses[existingCauseIndex],
      count: updatedCauses[existingCauseIndex].count + 1,
    };
  } else {
    updatedCauses.push({ cause: deathCause, count: 1 });
  }

  // Calculate quick death rate
  const recentProgression = [...profile.skillProgression, skillPoint].slice(-20);
  const quickDeaths = recentProgression.filter(p => p.survivalTime < 30).length;
  const quickDeathRate = quickDeaths / recentProgression.length;

  return {
    ...profile,
    updatedAt: now,
    skillProgression: [...profile.skillProgression, skillPoint].slice(-100), // Keep last 100
    insights: [...profile.insights, ...newInsights].slice(-50), // Keep last 50
    recentAdaptations: [...profile.recentAdaptations, ...state.runMarks].slice(-50),
    deathAnalysis: {
      ...profile.deathAnalysis,
      commonDeathCauses: updatedCauses.sort((a, b) => b.count - a.count),
      quickDeathRate,
    },
  };
}

/**
 * Generate new insights from run data.
 */
function generateNewInsights(
  profile: PlayerLearningProfile,
  crystal: GameCrystal,
  amberMemory: AmberMemory
): PlayerInsight[] {
  const insights: PlayerInsight[] = [];
  const now = Date.now();

  // Check for pattern insights
  const recentRuns = profile.skillProgression.slice(-10);

  // Detect if player is consistently good at certain waves
  const wave5Survivals = recentRuns.filter(r => r.wavesReached >= 5).length;
  if (wave5Survivals >= 7 && !profile.insights.some(i => i.description.includes('wave 5'))) {
    insights.push({
      type: 'strength',
      description: 'You consistently survive past wave 5.',
      confidence: wave5Survivals / 10,
      evidence: [`${wave5Survivals}/10 recent runs reached wave 5+`],
      formedAt: now,
      supportingRuns: wave5Survivals,
    });
  }

  // Detect dominant playstyle
  const dominant = amberMemory.playerProfile.dominantPlaystyle;
  const existingStyleInsight = profile.insights.find(
    i => i.type === 'preference' && i.description.includes(dominant)
  );
  if (!existingStyleInsight) {
    insights.push({
      type: 'preference',
      description: `Your playstyle leans toward ${dominant}.`,
      confidence: crystal.finalWeights[dominant],
      evidence: [`${(crystal.finalWeights[dominant] * 100).toFixed(0)}% ${dominant} weight in recent run`],
      formedAt: now,
      supportingRuns: 1,
    });
  }

  return insights;
}

// =============================================================================
// Review Interface Implementation
// =============================================================================

/**
 * Create an AdaptationReview interface from state.
 */
export function createAdaptationReview(
  state: AdaptationState,
  profile: PlayerLearningProfile
): AdaptationReview {
  return {
    getCurrentRunAdaptations(): AdaptationWitnessMark[] {
      return [...state.runMarks];
    },

    getHistoricalAdaptations(limit = 50): AdaptationWitnessMark[] {
      return profile.recentAdaptations.slice(-limit);
    },

    explainAdaptation(markId: string): AdaptationExplanation {
      const mark = state.runMarks.find(m => m.id === markId)
        ?? profile.recentAdaptations.find(m => m.id === markId);

      if (!mark) {
        throw new Error(`Adaptation mark ${markId} not found`);
      }

      const keyFactors: AdaptationExplanation['keyFactors'] = [];

      // Extract key factors from inputs
      if (mark.inputs.consecutiveQuickDeaths > 0) {
        keyFactors.push({
          factor: 'Consecutive quick deaths',
          value: mark.inputs.consecutiveQuickDeaths,
          impact: mark.inputs.consecutiveQuickDeaths >= 3 ? 'major' : 'minor',
        });
      }

      if (mark.inputs.consecutiveGoodRuns > 0) {
        keyFactors.push({
          factor: 'Consecutive good runs',
          value: mark.inputs.consecutiveGoodRuns,
          impact: mark.inputs.consecutiveGoodRuns >= 3 ? 'major' : 'minor',
        });
      }

      keyFactors.push({
        factor: 'Overall skill score',
        value: `${(mark.inputs.playerSkillScore * 100).toFixed(0)}%`,
        impact: 'major',
      });

      // Generate counterfactual
      let counterfactual = 'Without this adaptation, ';
      switch (mark.adaptationType) {
        case 'mercy_mode':
          counterfactual += 'enemies would spawn at normal rate and deal full damage.';
          break;
        case 'challenge_mode':
          counterfactual += 'enemies would spawn at normal rate and have normal health.';
          break;
        case 'spawn_rate':
          const mult = mark.output.spawnRateMultiplier ?? 1;
          counterfactual += mult < 1
            ? 'enemies would spawn faster, giving you less time to react.'
            : 'enemies would spawn slower, making the game less challenging.';
          break;
        default:
          counterfactual += 'the game would use default settings.';
      }

      return {
        mark,
        explanation: mark.reasoning,
        keyFactors,
        counterfactual,
        suggestions: mark.adaptationType === 'mercy_mode'
          ? ['Focus on positioning early game', 'Prioritize mobility upgrades']
          : undefined,
      };
    },

    overrideAdaptation(type: AdaptationType, value: AdaptationOverride): void {
      state.overrides[type] = value;
    },

    getOverrides(): Partial<Record<AdaptationType, AdaptationOverride>> {
      return { ...state.overrides };
    },

    resetOverrides(): void {
      state.overrides = {};
    },

    getSummary(): AdaptationSummary {
      const all = [...state.runMarks, ...profile.recentAdaptations];

      const byType: Partial<Record<AdaptationType, number>> = {};
      for (const mark of all) {
        byType[mark.adaptationType] = (byType[mark.adaptationType] ?? 0) + 1;
      }

      const recentSkill = profile.skillProgression.slice(-10);
      const avgSkill = recentSkill.length > 0
        ? recentSkill.reduce((sum, p) => sum + p.skillScore, 0) / recentSkill.length
        : 0.5;

      return {
        totalAdaptations: all.length,
        adaptationsByType: byType,
        mercyModeActivations: all.filter(m => m.output.mercyModeActivated).length,
        challengeModeActivations: all.filter(m => m.output.challengeModeActivated).length,
        averageSkillScore: avgSkill,
        trendDirection: calculateSkillTrend(profile.skillProgression),
      };
    },
  };
}

// =============================================================================
// React Hooks (Type Definitions)
// =============================================================================

/**
 * Result of useActiveAdaptations hook.
 */
export interface UseActiveAdaptationsResult {
  /** Current adaptations for this run */
  adaptations: AdaptationWitnessMark[];
  /** Whether mercy mode is active */
  mercyMode: boolean;
  /** Whether challenge mode is active */
  challengeMode: boolean;
  /** Combined active output */
  activeOutput: AdaptationOutput;
}

/**
 * Result of useAdaptationHistory hook.
 */
export interface UseAdaptationHistoryResult {
  /** Historical adaptations across runs */
  history: AdaptationWitnessMark[];
  /** Insights the game has learned */
  insights: PlayerInsight[];
  /** Summary statistics */
  summary: AdaptationSummary;
}

/**
 * Result of useAdaptationPreferences hook.
 */
export interface UseAdaptationPreferencesResult {
  /** Current preferences */
  preferences: AdaptationPreferences;
  /** Update a specific preference */
  updatePreference: <K extends keyof AdaptationPreferences>(
    key: K,
    value: AdaptationPreferences[K]
  ) => void;
  /** Reset all preferences to defaults */
  resetPreferences: () => void;
}

/**
 * Result of useAdaptationNotifications hook.
 */
export interface UseAdaptationNotificationsResult {
  /** Current notifications to display */
  notifications: AdaptationNotification[];
  /** Dismiss a notification */
  dismiss: (index: number) => void;
  /** Dismiss all notifications */
  dismissAll: () => void;
}

// =============================================================================
// Storage Keys (for localStorage persistence)
// =============================================================================

export const STORAGE_KEYS = {
  PLAYER_PROFILE: 'wasm-survivors-player-profile',
  ADAPTATION_PREFERENCES: 'wasm-survivors-adaptation-preferences',
  ADAPTATION_OVERRIDES: 'wasm-survivors-adaptation-overrides',
} as const;

// =============================================================================
// Export Summary
// =============================================================================

/**
 * Witness-Adaptive Bridge System
 *
 * USAGE EXAMPLE:
 *
 * ```typescript
 * import {
 *   createAdaptationState,
 *   createPlayerLearningProfile,
 *   calculateAdaptationInputs,
 *   decideAdaptations,
 *   applyAdaptations,
 *   createAmberMemory,
 *   updatePlayerProfile,
 * } from './systems/witness-adaptive-bridge';
 *
 * // Start of run
 * const adaptState = createAdaptationState(runId);
 * const profile = loadProfile() ?? createPlayerLearningProfile(playerId);
 *
 * // During gameplay (e.g., at wave transitions)
 * const inputs = calculateAdaptationInputs(gameState, profile, runMetrics);
 * const marks = decideAdaptations(inputs, profile.preferences, adaptState.overrides, runId, gameTime);
 * adaptState = applyAdaptations(adaptState, marks, profile.preferences);
 *
 * // Apply output to game systems
 * spawnRate *= adaptState.activeOutput.spawnRateMultiplier ?? 1;
 *
 * // End of run
 * const crystal = crystallize(witnessCtx, trace);
 * const amberMemory = createAmberMemory(crystal, adaptState, profile);
 * const updatedProfile = updatePlayerProfile(profile, crystal, amberMemory, adaptState);
 * saveProfile(updatedProfile);
 * ```
 */

export default {
  // State creation
  createAdaptationState,
  createDefaultPreferences,
  createPlayerLearningProfile,

  // Adaptation logic
  calculateAdaptationInputs,
  decideAdaptations,
  applyAdaptations,

  // Crystal enhancement
  createAmberMemory,

  // Profile management
  updatePlayerProfile,

  // Review interface
  createAdaptationReview,

  // Storage keys
  STORAGE_KEYS,
};
