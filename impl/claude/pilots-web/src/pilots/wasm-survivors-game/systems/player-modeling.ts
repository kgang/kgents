/**
 * WASM Survivors - Adaptive Player Modeling System
 *
 * Implements a two-tier modeling system:
 * - Micro-state: Within-run behavior tracking (positions, damage events, decisions)
 * - Macro-state: Cross-run pattern analysis (skill curves, preferences, weaknesses)
 *
 * The system emits WitnessMarks for every adaptation decision, enabling
 * transparent reasoning about why the game is changing.
 *
 * Design Principles:
 * - Privacy-first: Player data stays local unless explicitly shared
 * - Invisible adaptation: Changes should feel natural, not punishing
 * - Mercy over frustration: Help struggling players without announcing it
 * - Challenge seekers: Reward mastery with increased intensity
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import type {
  Vector2,
  EnemyType,
  BuildContext,
  GamePrincipleWeights,
  SkillMetrics,
} from '@kgents/shared-primitives';
import type { UpgradeType, VerbUpgrade } from './upgrades';

// =============================================================================
// Core Types
// =============================================================================

/**
 * Unique identifier for a player across sessions.
 * Generated on first play, stored locally, never transmitted without consent.
 */
export type PlayerId = string;

/**
 * Unique identifier for a single game run.
 */
export type RunId = string;

/**
 * Timestamp in milliseconds (game time, not wall clock).
 */
export type GameTimestamp = number;

// =============================================================================
// Event Types (Micro-State Building Blocks)
// =============================================================================

/**
 * Damage event - when the player takes damage.
 * Used to identify:
 * - Dangerous enemy types
 * - Problematic wave configurations
 * - Patterns in damage intake (burst vs. sustained)
 */
export interface DamageEvent {
  /** Game time when damage occurred */
  readonly gameTime: GameTimestamp;
  /** Amount of damage taken */
  readonly amount: number;
  /** Player health after damage */
  readonly healthAfter: number;
  /** Player max health at time of damage */
  readonly maxHealth: number;
  /** Source of damage */
  readonly source: DamageSource;
  /** Player position when hit */
  readonly playerPosition: Vector2;
  /** Current wave number */
  readonly wave: number;
  /** Was player moving when hit? */
  readonly wasMoving: boolean;
  /** Number of enemies nearby (within 100px) */
  readonly nearbyEnemyCount: number;
}

/**
 * Source of damage for pattern analysis.
 */
export interface DamageSource {
  /** Type of damage source */
  readonly type: 'enemy_collision' | 'enemy_projectile' | 'stomp_aoe' | 'charge_hit' | 'environmental';
  /** Enemy type if applicable */
  readonly enemyType?: EnemyType;
  /** Enemy ID for tracking specific problematic enemies */
  readonly enemyId?: string;
  /** Was the enemy in attack state? */
  readonly wasEnemyAttacking?: boolean;
}

/**
 * Kill event - when the player eliminates an enemy.
 * Used to identify:
 * - Combat efficiency patterns
 * - Preferred engagement distances
 * - Build effectiveness
 */
export interface KillEvent {
  /** Game time of kill */
  readonly gameTime: GameTimestamp;
  /** Type of enemy killed */
  readonly enemyType: EnemyType;
  /** Enemy ID for combo tracking */
  readonly enemyId: string;
  /** Distance from player at time of kill */
  readonly distance: number;
  /** Position of kill */
  readonly position: Vector2;
  /** Current wave */
  readonly wave: number;
  /** XP gained from kill */
  readonly xpGained: number;
  /** Time since previous kill (null if first) */
  readonly timeSinceLastKill: number | null;
  /** Was this a vulnerable/recovery state kill? */
  readonly wasVulnerableKill: boolean;
}

/**
 * Clutch moment - near-death survival.
 * Crucial for understanding player skill ceiling.
 */
export interface ClutchMoment {
  /** Game time of clutch */
  readonly gameTime: GameTimestamp;
  /** Lowest health reached */
  readonly lowestHealth: number;
  /** Maximum health at time */
  readonly maxHealth: number;
  /** Health percentage at lowest (0-1) */
  readonly healthPercentage: number;
  /** Number of enemies present during clutch */
  readonly threatCount: number;
  /** Duration of clutch period (time at critical health) */
  readonly clutchDuration: number;
  /** How player escaped: killed threats, dodged, or healed */
  readonly resolution: 'killed_threats' | 'escaped' | 'healed' | 'lucky_spawn';
  /** Current wave */
  readonly wave: number;
}

/**
 * Combo chain - consecutive kills without taking damage.
 */
export interface ComboChain {
  /** Game time combo started */
  readonly startTime: GameTimestamp;
  /** Game time combo ended (damage taken or death) */
  readonly endTime: GameTimestamp;
  /** Number of kills in chain */
  readonly kills: number;
  /** Enemy types killed during chain */
  readonly enemyTypesKilled: EnemyType[];
  /** Average distance of kills */
  readonly averageKillDistance: number;
  /** Combo ended by (damage source or run_end) */
  readonly terminatedBy: DamageSource | 'run_end' | 'timeout';
  /** XP gained during combo */
  readonly totalXpGained: number;
}

/**
 * Upgrade selection event for preference modeling.
 */
export interface UpgradeSelection {
  /** Game time of selection */
  readonly gameTime: GameTimestamp;
  /** Level at which selection occurred */
  readonly level: number;
  /** Wave at which selection occurred */
  readonly wave: number;
  /** Upgrades that were offered */
  readonly offered: UpgradeType[];
  /** Upgrade that was selected */
  readonly selected: UpgradeType;
  /** Time taken to decide (ms) */
  readonly decisionTime: number;
  /** Current upgrades owned before selection */
  readonly currentUpgrades: UpgradeType[];
  /** Current synergies before selection */
  readonly currentSynergies: string[];
  /** Did this complete a synergy? */
  readonly completedSynergy: string | null;
}

// =============================================================================
// Movement Analysis Types
// =============================================================================

/**
 * Movement style classification.
 * Determined by analyzing position history and behavior patterns.
 */
export type MovementStyle =
  /** High aggression, actively seeks enemies */
  | 'aggressive'
  /** Prioritizes distance from enemies */
  | 'defensive'
  /** Unpredictable movement, possibly struggling */
  | 'erratic'
  /** Deliberate movements, efficient pathing */
  | 'calculated'
  /** Circles the arena, maintains distance */
  | 'kiting'
  /** Camps corners or edges */
  | 'camping';

/**
 * Movement analysis window (typically 5-10 seconds of data).
 */
export interface MovementWindow {
  /** Start time of window */
  readonly startTime: GameTimestamp;
  /** End time of window */
  readonly endTime: GameTimestamp;
  /** Sampled positions within window */
  readonly positions: Vector2[];
  /** Classified movement style */
  readonly style: MovementStyle;
  /** Average velocity magnitude */
  readonly averageSpeed: number;
  /** Direction change frequency (per second) */
  readonly turnRate: number;
  /** Distance traveled in window */
  readonly distanceTraveled: number;
  /** Arena coverage (0-1, portion of arena visited) */
  readonly arenaCoverage: number;
}

/**
 * Heatmap cell for position tracking.
 * Arena is divided into grid cells for density analysis.
 */
export interface HeatmapCell {
  /** Grid x coordinate */
  readonly x: number;
  /** Grid y coordinate */
  readonly y: number;
  /** Time spent in this cell (ms) */
  readonly timeSpent: number;
  /** Number of deaths in this cell */
  readonly deaths: number;
  /** Number of kills in this cell */
  readonly kills: number;
  /** Number of damage events in this cell */
  readonly damagesTaken: number;
}

// =============================================================================
// Micro-State: Within-Run Tracking
// =============================================================================

/**
 * Complete micro-state for a single run.
 * Captures all behavioral data for real-time adaptation and post-run analysis.
 */
export interface RunMicroState {
  /** Unique identifier for this run */
  readonly runId: RunId;

  /** Run start timestamp (wall clock) */
  readonly startTime: number;

  /** Run end timestamp (wall clock, null if ongoing) */
  readonly endTime: number | null;

  // ===== Position and Movement =====

  /**
   * Position history sampled at regular intervals.
   * Sampling rate: every 100ms (10 samples/second).
   * Used for movement style detection and heatmap generation.
   */
  readonly positionHistory: ReadonlyArray<{
    readonly position: Vector2;
    readonly gameTime: GameTimestamp;
    readonly velocity: Vector2;
  }>;

  /**
   * Heatmap of time spent in each arena cell.
   * Grid size: 10x10 (each cell ~80x60 pixels for 800x600 arena).
   */
  readonly heatmap: ReadonlyArray<ReadonlyArray<HeatmapCell>>;

  /**
   * Movement windows for style tracking over time.
   * New window every 5 seconds.
   */
  readonly movementWindows: ReadonlyArray<MovementWindow>;

  /**
   * Current classified movement style (computed from recent windows).
   */
  readonly currentMovementStyle: MovementStyle;

  // ===== Combat Patterns =====

  /** All damage events in this run */
  readonly damageEvents: ReadonlyArray<DamageEvent>;

  /** All kill events in this run */
  readonly killEvents: ReadonlyArray<KillEvent>;

  /** Near-death survivals */
  readonly clutchMoments: ReadonlyArray<ClutchMoment>;

  /** Kill streaks without damage */
  readonly comboChains: ReadonlyArray<ComboChain>;

  /** Current active combo (null if taking damage recently) */
  readonly currentCombo: ComboChain | null;

  // ===== Decisions =====

  /** All upgrade selections made this run */
  readonly upgradeSelections: ReadonlyArray<UpgradeSelection>;

  // ===== Computed Metrics (Updated in Real-time) =====

  /** Damage efficiency: kills per damage taken */
  readonly damageEfficiency: number;

  /** Dodge rate: (1 - damage events / expected damage events based on threats) */
  readonly dodgeRate: number;

  /** Average reaction time to threats (ms) */
  readonly averageReactionTime: number;

  /** Current threat assessment (0-1) */
  readonly currentThreatLevel: number;

  /** Time in critical health (<20%) this run */
  readonly timeInCriticalHealth: number;

  /** Highest wave reached */
  readonly highestWave: number;

  /** Total XP earned */
  readonly totalXpEarned: number;

  /** Build context at current moment */
  readonly currentBuildContext: BuildContext;
}

// =============================================================================
// Macro-State: Cross-Run Analysis
// =============================================================================

/**
 * Skill data point for tracking improvement over time.
 */
export interface SkillDataPoint {
  /** Timestamp of run end */
  readonly timestamp: number;
  /** Run ID for reference */
  readonly runId: RunId;
  /** Composite skill score (0-1) */
  readonly skillScore: number;
  /** Individual skill metrics */
  readonly metrics: SkillMetrics;
  /** Wave reached */
  readonly waveReached: number;
  /** Run duration (ms) */
  readonly duration: number;
  /** Death cause (null if victory) */
  readonly deathCause: string | null;
}

/**
 * Upgrade preference with weight.
 */
export interface UpgradePreference {
  /** Upgrade type */
  readonly upgrade: UpgradeType;
  /** Selection weight (0-1, higher = more preferred) */
  readonly weight: number;
  /** Times offered */
  readonly timesOffered: number;
  /** Times selected */
  readonly timesSelected: number;
  /** Average decision time when selected (ms) */
  readonly averageDecisionTime: number;
  /** Win rate when in final build */
  readonly winRateWhenOwned: number;
}

/**
 * Analysis of what causes player deaths.
 */
export interface DeathCauseAnalysis {
  /** Total deaths analyzed */
  readonly totalDeaths: number;

  /** Deaths by enemy type */
  readonly byEnemyType: ReadonlyMap<EnemyType, number>;

  /** Deaths by wave range */
  readonly byWaveRange: ReadonlyMap<string, number>; // '1-3', '4-6', etc.

  /** Deaths while in specific state */
  readonly byPlayerState: {
    readonly whileStationary: number;
    readonly whileDashing: number;
    readonly whileCornered: number;
    readonly whileOverwhelmed: number;
  };

  /** Most common death cause */
  readonly primaryCause: EnemyType | 'overwhelmed' | 'attrition' | 'boss';

  /** Average health at death */
  readonly averageDeathHealth: number;

  /** Average wave at death */
  readonly averageDeathWave: number;
}

/**
 * Complete macro-state across all runs.
 */
export interface PlayerMacroState {
  /** Anonymous but persistent player identifier */
  readonly playerId: PlayerId;

  /** When this profile was created */
  readonly profileCreatedAt: number;

  /** Last activity timestamp */
  readonly lastActiveAt: number;

  /** Total number of runs */
  readonly totalRuns: number;

  /** Total play time (ms) */
  readonly totalPlayTime: number;

  // ===== Skill Tracking =====

  /** Performance over time (last N runs, typically 50) */
  readonly skillCurve: ReadonlyArray<SkillDataPoint>;

  /** Current estimated skill level (0-1) */
  readonly currentSkillLevel: number;

  /** How fast skill is improving (derivative of skill curve) */
  readonly improvementRate: number;

  /** Has player stopped improving? (rate near zero for several runs) */
  readonly hasPlateaued: boolean;

  /** Best wave ever reached */
  readonly bestWave: number;

  /** Best combo ever achieved */
  readonly bestCombo: number;

  /** Best run duration (ms) */
  readonly bestDuration: number;

  // ===== Preferences =====

  /** Upgrade selection preferences */
  readonly preferredUpgrades: ReadonlyArray<UpgradePreference>;

  /** Upgrades the player tends to skip */
  readonly avoidedUpgrades: ReadonlyArray<UpgradePreference>;

  /** Preferred synergy combinations */
  readonly preferredSynergies: ReadonlyArray<{
    readonly synergy: string;
    readonly selectionRate: number;
    readonly winRate: number;
  }>;

  /** Dominant playstyle weights */
  readonly playstyleWeights: GamePrincipleWeights;

  // ===== Weaknesses =====

  /** Comprehensive death analysis */
  readonly deathCauses: DeathCauseAnalysis;

  /** Enemy types that trouble this player */
  readonly struggleBeeTypes: ReadonlyArray<{
    readonly enemyType: EnemyType;
    readonly deathRate: number;
    readonly damageRate: number;
    readonly avoidanceScore: number;
  }>;

  /** Wave numbers that are consistently difficult */
  readonly difficultWaves: ReadonlyArray<{
    readonly wave: number;
    readonly failureRate: number;
    readonly averageHealthAtWave: number;
  }>;

  // ===== Behavioral Patterns =====

  /** Average decision time for upgrades */
  readonly averageDecisionTime: number;

  /** Movement style distribution across runs */
  readonly movementStyleDistribution: ReadonlyMap<MovementStyle, number>;

  /** Dominant movement style */
  readonly dominantMovementStyle: MovementStyle;

  /** Arena position preference (which quadrants) */
  readonly arenaPreference: {
    readonly topLeft: number;
    readonly topRight: number;
    readonly bottomLeft: number;
    readonly bottomRight: number;
    readonly center: number;
  };
}

// =============================================================================
// Playstyle Detection
// =============================================================================

/**
 * High-level playstyle categories.
 * Detected from behavioral patterns across multiple runs.
 */
export type PlayStyle =
  /** High aggression, low caution, seeks combat */
  | 'berserker'
  /** High caution, prioritizes health and defense */
  | 'survivor'
  /** Optimizes for fast clears, minimal decision time */
  | 'speedrunner'
  /** Explores every option, tries new combinations */
  | 'completionist'
  /** Tries different things each run */
  | 'experimenter'
  /** Finds one strategy and perfects it */
  | 'optimizer';

/**
 * Playstyle analysis result.
 */
export interface PlayStyleAnalysis {
  /** Primary detected playstyle */
  readonly primary: PlayStyle;

  /** Secondary playstyle (if mixed) */
  readonly secondary: PlayStyle | null;

  /** Confidence in classification (0-1) */
  readonly confidence: number;

  /** Evidence supporting classification */
  readonly evidence: ReadonlyArray<{
    readonly factor: string;
    readonly weight: number;
    readonly direction: 'supports' | 'contradicts';
  }>;

  /** Playstyle drift over time (are they changing?) */
  readonly drift: {
    readonly isDrifting: boolean;
    readonly fromStyle: PlayStyle | null;
    readonly toStyle: PlayStyle | null;
    readonly progress: number;
  };
}

// =============================================================================
// Adaptation Types
// =============================================================================

/**
 * Spawn rate and composition adjustment.
 */
export interface SpawnAdjustment {
  /** Multiplier for spawn rate (1.0 = normal) */
  readonly spawnRateMultiplier: number;

  /** Multiplier for enemy health (1.0 = normal) */
  readonly enemyHealthMultiplier: number;

  /** Multiplier for enemy damage (1.0 = normal) */
  readonly enemyDamageMultiplier: number;

  /** Weight adjustments for enemy types (1.0 = normal) */
  readonly enemyTypeWeights: ReadonlyMap<EnemyType, number>;

  /** Should we delay certain enemy types? */
  readonly delayedEnemyTypes: ReadonlyMap<EnemyType, number>; // wave delay

  /** Maximum enemies on screen */
  readonly maxActiveEnemies: number;

  /** Reasoning for this adjustment */
  readonly reasoning: string;
}

/**
 * Upgrade with adaptive weight.
 */
export interface WeightedUpgrade {
  /** The upgrade */
  readonly upgrade: VerbUpgrade;

  /** Selection weight (higher = more likely to be offered) */
  readonly weight: number;

  /** Reason for weight adjustment */
  readonly reason: 'preferred' | 'needed' | 'synergy_hint' | 'variety' | 'counter_weakness' | 'default';
}

/**
 * Mercy intervention decision.
 * Triggered when player is struggling significantly.
 */
export interface MercyDecision {
  /** Should mercy be triggered? */
  readonly shouldTrigger: boolean;

  /** Type of mercy intervention */
  readonly interventionType:
    | 'spawn_pause'      // Briefly stop spawning new enemies
    | 'health_orb'       // Spawn a health pickup
    | 'reduced_damage'   // Temporarily reduce incoming damage
    | 'clear_projectiles' // Remove enemy projectiles
    | 'weak_wave'        // Next wave is easier
    | 'none';

  /** Duration of mercy (ms) */
  readonly duration: number;

  /** Reasoning for decision */
  readonly reasoning: string;

  /** Evidence that triggered this */
  readonly triggers: ReadonlyArray<string>;
}

/**
 * Challenge escalation decision.
 * Triggered when player is dominating.
 */
export interface ChallengeDecision {
  /** Should challenge be escalated? */
  readonly shouldTrigger: boolean;

  /** Type of challenge escalation */
  readonly escalationType:
    | 'spawn_surge'      // Brief increase in spawn rate
    | 'elite_spawn'      // Spawn an elite enemy
    | 'boss_early'       // Trigger boss wave early
    | 'mixed_wave'       // Next wave has more variety
    | 'damage_buff'      // Enemies deal more damage
    | 'none';

  /** Intensity of escalation (0-1) */
  readonly intensity: number;

  /** Reasoning for decision */
  readonly reasoning: string;

  /** Evidence that triggered this */
  readonly triggers: ReadonlyArray<string>;
}

// =============================================================================
// Witness Integration
// =============================================================================

/**
 * Adaptation witness mark.
 * Every adaptation decision emits a mark for transparency.
 */
export interface AdaptationMark {
  /** Mark type */
  readonly type: 'adaptation';

  /** Adaptation decision category */
  readonly decision:
    | 'spawn_adjust'
    | 'upgrade_weight'
    | 'mercy'
    | 'challenge'
    | 'playstyle_detected'
    | 'skill_assessed';

  /** Human-readable explanation */
  readonly reasoning: string;

  /** Input data that drove the decision */
  readonly inputs: Readonly<Record<string, number | string | boolean>>;

  /** What was decided */
  readonly output: unknown;

  /** Game time when decision was made */
  readonly gameTime: GameTimestamp;

  /** Confidence in decision (0-1) */
  readonly confidence: number;
}

// =============================================================================
// Storage Schema
// =============================================================================

/**
 * Amber memory - crystallized moment from a death.
 * Preserved for post-run reflection and sharing.
 */
export interface AmberMemory {
  /** Unique identifier */
  readonly id: string;

  /** Run this memory came from */
  readonly runId: RunId;

  /** Timestamp of death */
  readonly timestamp: number;

  /** Death cause */
  readonly cause: string;

  /** Final game state snapshot */
  readonly finalState: {
    readonly wave: number;
    readonly score: number;
    readonly upgrades: UpgradeType[];
    readonly synergies: string[];
    readonly totalKills: number;
    readonly playTime: number;
  };

  /** Memorable moments from this run */
  readonly highlights: ReadonlyArray<{
    readonly type: 'clutch' | 'combo' | 'synergy' | 'first_colossal' | 'new_wave';
    readonly description: string;
    readonly gameTime: GameTimestamp;
  }>;

  /** Crystal (compressed narrative) */
  readonly crystalTitle: string;

  /** Crystal claim (one-sentence summary) */
  readonly crystalClaim: string;
}

/**
 * Milestone achievement.
 */
export interface Milestone {
  /** Milestone identifier */
  readonly id: string;

  /** Human-readable name */
  readonly name: string;

  /** Description */
  readonly description: string;

  /** When achieved */
  readonly achievedAt: number;

  /** Run it was achieved in */
  readonly runId: RunId;

  /** Category of milestone */
  readonly category: 'survival' | 'combat' | 'build' | 'skill' | 'exploration';
}

/**
 * Player preferences for the game.
 */
export interface GamePreferences {
  /** Sound enabled */
  readonly soundEnabled: boolean;

  /** Music volume (0-1) */
  readonly musicVolume: number;

  /** SFX volume (0-1) */
  readonly sfxVolume: number;

  /** Screen shake enabled */
  readonly screenShakeEnabled: boolean;

  /** Screen shake intensity (0-1) */
  readonly screenShakeIntensity: number;

  /** Show damage numbers */
  readonly showDamageNumbers: boolean;

  /** Show kill count */
  readonly showKillCount: boolean;

  /** Preferred control scheme */
  readonly controlScheme: 'wasd' | 'arrows' | 'both';
}

/**
 * Complete player data store schema.
 */
export interface PlayerDataStore {
  /**
   * Data stored locally.
   * Never transmitted without explicit consent.
   */
  readonly local: {
    /** Recent runs with full detail (last N, typically 10) */
    readonly recentRuns: ReadonlyArray<RunMicroState>;

    /** Aggregated macro state */
    readonly macroState: PlayerMacroState;

    /** Current session state (if mid-run) */
    readonly currentSession: RunMicroState | null;
  };

  /**
   * Data that could be synced (with player opt-in).
   * Used for cloud saves, leaderboards, etc.
   */
  readonly syncable: {
    /** Crystals from deaths (preserved memories) */
    readonly amberMemories: ReadonlyArray<AmberMemory>;

    /** Achievements and milestones */
    readonly milestones: ReadonlyArray<Milestone>;

    /** Game preferences */
    readonly preferences: GamePreferences;

    /** Anonymous aggregate stats (for leaderboards) */
    readonly aggregateStats: {
      readonly bestWave: number;
      readonly totalPlayTime: number;
      readonly totalRuns: number;
      readonly totalKills: number;
    };
  };

  /**
   * Data that is NEVER stored or transmitted.
   * Explicit documentation of privacy boundaries.
   */
  readonly never: {
    /** Real-time position (transient only) */
    readonly realtimePosition: 'not_stored';

    /** Exact timestamps (only relative times stored) */
    readonly exactTimestamps: 'not_stored';

    /** Input patterns (keyboard/mouse specifics) */
    readonly rawInputPatterns: 'not_stored';

    /** Session metadata (IP, browser, etc.) */
    readonly sessionMetadata: 'not_stored';

    /** Cross-game identifiers */
    readonly externalIdentifiers: 'not_stored';
  };
}

// =============================================================================
// Type Guards
// =============================================================================

/**
 * Check if a value is a valid PlayerId.
 */
export function isPlayerId(value: unknown): value is PlayerId {
  return typeof value === 'string' && value.length > 0 && value.length <= 64;
}

/**
 * Check if a value is a valid RunId.
 */
export function isRunId(value: unknown): value is RunId {
  return typeof value === 'string' && value.length > 0 && value.length <= 64;
}

/**
 * Check if a value is a valid MovementStyle.
 */
export function isMovementStyle(value: unknown): value is MovementStyle {
  return (
    value === 'aggressive' ||
    value === 'defensive' ||
    value === 'erratic' ||
    value === 'calculated' ||
    value === 'kiting' ||
    value === 'camping'
  );
}

/**
 * Check if a value is a valid PlayStyle.
 */
export function isPlayStyle(value: unknown): value is PlayStyle {
  return (
    value === 'berserker' ||
    value === 'survivor' ||
    value === 'speedrunner' ||
    value === 'completionist' ||
    value === 'experimenter' ||
    value === 'optimizer'
  );
}

/**
 * Check if a value is a valid DamageEvent.
 */
export function isDamageEvent(value: unknown): value is DamageEvent {
  if (typeof value !== 'object' || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.gameTime === 'number' &&
    typeof v.amount === 'number' &&
    typeof v.healthAfter === 'number' &&
    typeof v.maxHealth === 'number' &&
    typeof v.source === 'object' &&
    typeof v.playerPosition === 'object' &&
    typeof v.wave === 'number'
  );
}

/**
 * Check if a value is a valid KillEvent.
 */
export function isKillEvent(value: unknown): value is KillEvent {
  if (typeof value !== 'object' || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    typeof v.gameTime === 'number' &&
    typeof v.enemyType === 'string' &&
    typeof v.enemyId === 'string' &&
    typeof v.distance === 'number' &&
    typeof v.position === 'object' &&
    typeof v.wave === 'number'
  );
}

/**
 * Check if a value is a valid AdaptationMark.
 */
export function isAdaptationMark(value: unknown): value is AdaptationMark {
  if (typeof value !== 'object' || value === null) return false;
  const v = value as Record<string, unknown>;
  return (
    v.type === 'adaptation' &&
    typeof v.decision === 'string' &&
    typeof v.reasoning === 'string' &&
    typeof v.inputs === 'object' &&
    typeof v.gameTime === 'number'
  );
}

// =============================================================================
// Factory Functions
// =============================================================================

/**
 * Generate a new player ID.
 * Uses crypto.randomUUID if available, falls back to timestamp-based.
 */
export function generatePlayerId(): PlayerId {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `player-${crypto.randomUUID()}`;
  }
  return `player-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

/**
 * Generate a new run ID.
 */
export function generateRunId(): RunId {
  if (typeof crypto !== 'undefined' && crypto.randomUUID) {
    return `run-${crypto.randomUUID()}`;
  }
  return `run-${Date.now()}-${Math.random().toString(36).slice(2, 11)}`;
}

/**
 * Create initial heatmap grid.
 */
export function createInitialHeatmap(gridWidth: number = 10, gridHeight: number = 10): HeatmapCell[][] {
  const grid: HeatmapCell[][] = [];
  for (let y = 0; y < gridHeight; y++) {
    const row: HeatmapCell[] = [];
    for (let x = 0; x < gridWidth; x++) {
      row.push({
        x,
        y,
        timeSpent: 0,
        deaths: 0,
        kills: 0,
        damagesTaken: 0,
      });
    }
    grid.push(row);
  }
  return grid;
}

/**
 * Create initial run micro-state.
 */
export function createInitialRunMicroState(runId: RunId): RunMicroState {
  return {
    runId,
    startTime: Date.now(),
    endTime: null,
    positionHistory: [],
    heatmap: createInitialHeatmap(),
    movementWindows: [],
    currentMovementStyle: 'calculated',
    damageEvents: [],
    killEvents: [],
    clutchMoments: [],
    comboChains: [],
    currentCombo: null,
    upgradeSelections: [],
    damageEfficiency: 1.0,
    dodgeRate: 1.0,
    averageReactionTime: 0,
    currentThreatLevel: 0,
    timeInCriticalHealth: 0,
    highestWave: 1,
    totalXpEarned: 0,
    currentBuildContext: {
      wave: 1,
      health: 100,
      maxHealth: 100,
      upgrades: [],
      synergies: [],
      xp: 0,
      enemiesKilled: 0,
    },
  };
}

/**
 * Create initial player macro-state.
 */
export function createInitialPlayerMacroState(playerId: PlayerId): PlayerMacroState {
  const now = Date.now();
  return {
    playerId,
    profileCreatedAt: now,
    lastActiveAt: now,
    totalRuns: 0,
    totalPlayTime: 0,
    skillCurve: [],
    currentSkillLevel: 0.5,
    improvementRate: 0,
    hasPlateaued: false,
    bestWave: 0,
    bestCombo: 0,
    bestDuration: 0,
    preferredUpgrades: [],
    avoidedUpgrades: [],
    preferredSynergies: [],
    playstyleWeights: {
      aggression: 0.2,
      defense: 0.2,
      mobility: 0.2,
      precision: 0.2,
      synergy: 0.2,
    },
    deathCauses: {
      totalDeaths: 0,
      byEnemyType: new Map(),
      byWaveRange: new Map(),
      byPlayerState: {
        whileStationary: 0,
        whileDashing: 0,
        whileCornered: 0,
        whileOverwhelmed: 0,
      },
      primaryCause: 'basic',
      averageDeathHealth: 0,
      averageDeathWave: 1,
    },
    struggleBeeTypes: [],
    difficultWaves: [],
    averageDecisionTime: 3000,
    movementStyleDistribution: new Map(),
    dominantMovementStyle: 'calculated',
    arenaPreference: {
      topLeft: 0.2,
      topRight: 0.2,
      bottomLeft: 0.2,
      bottomRight: 0.2,
      center: 0.2,
    },
  };
}

/**
 * Create initial game preferences.
 */
export function createInitialPreferences(): GamePreferences {
  return {
    soundEnabled: true,
    musicVolume: 0.7,
    sfxVolume: 0.8,
    screenShakeEnabled: true,
    screenShakeIntensity: 0.7,
    showDamageNumbers: true,
    showKillCount: true,
    controlScheme: 'wasd',
  };
}

/**
 * Create empty player data store.
 */
export function createInitialPlayerDataStore(playerId: PlayerId): PlayerDataStore {
  return {
    local: {
      recentRuns: [],
      macroState: createInitialPlayerMacroState(playerId),
      currentSession: null,
    },
    syncable: {
      amberMemories: [],
      milestones: [],
      preferences: createInitialPreferences(),
      aggregateStats: {
        bestWave: 0,
        totalPlayTime: 0,
        totalRuns: 0,
        totalKills: 0,
      },
    },
    never: {
      realtimePosition: 'not_stored',
      exactTimestamps: 'not_stored',
      rawInputPatterns: 'not_stored',
      sessionMetadata: 'not_stored',
      externalIdentifiers: 'not_stored',
    },
  };
}

// =============================================================================
// Adaptation Rule Functions
// =============================================================================

/**
 * Calculate spawn adjustments based on player skill and current state.
 *
 * @param macroState - Player's cross-run state
 * @param microState - Current run state (null if at run start)
 * @returns Spawn adjustment parameters
 */
export function calculateSpawnAdjustment(
  macroState: PlayerMacroState,
  microState: RunMicroState | null
): SpawnAdjustment {
  const skillLevel = macroState.currentSkillLevel;
  const isStruggling = microState
    ? microState.currentThreatLevel > 0.7 && microState.dodgeRate < 0.5
    : false;
  const isDominating = microState
    ? microState.damageEfficiency > 2.0 && microState.dodgeRate > 0.8
    : false;

  // Base multipliers from skill level
  let spawnRate = 0.8 + skillLevel * 0.4; // 0.8x to 1.2x
  let healthMult = 0.9 + skillLevel * 0.2; // 0.9x to 1.1x
  let damageMult = 0.9 + skillLevel * 0.2; // 0.9x to 1.1x

  // Adjust for current run performance
  if (isStruggling) {
    spawnRate *= 0.85;
    healthMult *= 0.9;
    damageMult *= 0.85;
  } else if (isDominating) {
    spawnRate *= 1.15;
    healthMult *= 1.1;
    damageMult *= 1.1;
  }

  // Weight adjustments for problematic enemy types
  const enemyWeights = new Map<EnemyType, number>();
  for (const struggle of macroState.struggleBeeTypes) {
    // Reduce spawn weight for enemies that kill this player often
    enemyWeights.set(struggle.enemyType, Math.max(0.5, 1 - struggle.deathRate));
  }

  // Delay types they struggle with
  const delayedTypes = new Map<EnemyType, number>();
  for (const struggle of macroState.struggleBeeTypes) {
    if (struggle.deathRate > 0.3) {
      // Delay by 1-3 waves based on struggle intensity
      delayedTypes.set(struggle.enemyType, Math.ceil(struggle.deathRate * 3));
    }
  }

  // Max enemies based on skill
  const maxEnemies = Math.floor(15 + skillLevel * 10);

  const reasoning = isStruggling
    ? 'Player struggling: reduced spawn pressure'
    : isDominating
    ? 'Player dominating: increased challenge'
    : 'Standard difficulty for skill level';

  return {
    spawnRateMultiplier: spawnRate,
    enemyHealthMultiplier: healthMult,
    enemyDamageMultiplier: damageMult,
    enemyTypeWeights: enemyWeights,
    delayedEnemyTypes: delayedTypes,
    maxActiveEnemies: maxEnemies,
    reasoning,
  };
}

/**
 * Calculate weighted upgrade offerings based on player preferences and needs.
 *
 * @param macroState - Player's cross-run state
 * @param microState - Current run state
 * @param available - Currently available upgrades
 * @returns Weighted upgrade list
 */
export function calculateUpgradeWeighting(
  macroState: PlayerMacroState,
  microState: RunMicroState,
  available: VerbUpgrade[]
): WeightedUpgrade[] {
  const weighted: WeightedUpgrade[] = [];

  for (const upgrade of available) {
    let weight = 1.0;
    let reason: WeightedUpgrade['reason'] = 'default';

    // Check if player prefers this upgrade
    const preference = macroState.preferredUpgrades.find(p => p.upgrade === upgrade.id);
    if (preference && preference.weight > 0.6) {
      weight *= 1.3;
      reason = 'preferred';
    }

    // Check if this counters a weakness
    const countersWeakness = checkUpgradeCountersWeakness(upgrade, macroState);
    if (countersWeakness) {
      weight *= 1.4;
      reason = 'counter_weakness';
    }

    // Check if this completes a synergy
    const currentUpgrades = microState.currentBuildContext.upgrades;
    const wouldCompleteSynergy = checkSynergyCompletion(upgrade.id, currentUpgrades);
    if (wouldCompleteSynergy) {
      weight *= 1.5;
      reason = 'synergy_hint';
    }

    // Check if player is struggling and this would help
    if (microState.currentThreatLevel > 0.6) {
      if (upgrade.id === 'vampiric' || upgrade.id === 'slow_field') {
        weight *= 1.4;
        reason = 'needed';
      }
    }

    // Variety bonus for upgrades they haven't tried much
    const avoided = macroState.avoidedUpgrades.find(p => p.upgrade === upgrade.id);
    if (avoided && avoided.timesOffered > 10 && avoided.timesSelected < 2) {
      // Occasionally offer avoided upgrades for variety
      if (Math.random() < 0.2) {
        weight *= 1.2;
        reason = 'variety';
      }
    }

    weighted.push({ upgrade, weight, reason });
  }

  // Normalize weights
  const totalWeight = weighted.reduce((sum, w) => sum + w.weight, 0);
  return weighted.map(w => ({
    ...w,
    weight: w.weight / totalWeight,
  }));
}

/**
 * Determine if mercy intervention should trigger.
 *
 * @param microState - Current run state
 * @returns Mercy decision
 */
export function shouldTriggerMercy(microState: RunMicroState): MercyDecision {
  const triggers: string[] = [];

  // Check various struggle indicators
  const healthPercent = microState.currentBuildContext.health / microState.currentBuildContext.maxHealth;
  const recentDamageEvents = microState.damageEvents.filter(
    e => e.gameTime > microState.currentBuildContext.xp - 5000
  ).length;
  const clutchesRecently = microState.clutchMoments.filter(
    c => c.gameTime > microState.currentBuildContext.xp - 10000
  ).length;

  if (healthPercent < 0.15) triggers.push('critical_health');
  if (recentDamageEvents >= 5) triggers.push('rapid_damage_intake');
  if (clutchesRecently >= 2) triggers.push('multiple_clutches');
  if (microState.currentThreatLevel > 0.85) triggers.push('overwhelming_threat');
  if (microState.dodgeRate < 0.3) triggers.push('poor_avoidance');

  // Determine intervention type and intensity
  if (triggers.length >= 3) {
    return {
      shouldTrigger: true,
      interventionType: 'spawn_pause',
      duration: 3000,
      reasoning: 'Player in severe distress, pausing spawns briefly',
      triggers,
    };
  } else if (triggers.includes('critical_health') && triggers.length >= 2) {
    return {
      shouldTrigger: true,
      interventionType: 'health_orb',
      duration: 0,
      reasoning: 'Player at critical health with ongoing pressure',
      triggers,
    };
  } else if (triggers.includes('overwhelming_threat')) {
    return {
      shouldTrigger: true,
      interventionType: 'clear_projectiles',
      duration: 0,
      reasoning: 'Too many threats, clearing projectiles',
      triggers,
    };
  } else if (triggers.length >= 2) {
    return {
      shouldTrigger: true,
      interventionType: 'reduced_damage',
      duration: 5000,
      reasoning: 'Temporary damage reduction to help stabilize',
      triggers,
    };
  }

  return {
    shouldTrigger: false,
    interventionType: 'none',
    duration: 0,
    reasoning: 'No mercy needed',
    triggers,
  };
}

/**
 * Determine if challenge escalation should trigger.
 *
 * @param microState - Current run state
 * @returns Challenge decision
 */
export function shouldTriggerChallenge(microState: RunMicroState): ChallengeDecision {
  const triggers: string[] = [];

  // Check various domination indicators
  const healthPercent = microState.currentBuildContext.health / microState.currentBuildContext.maxHealth;
  const hasActiveCombo = microState.currentCombo !== null && microState.currentCombo.kills >= 10;
  const recentDamage = microState.damageEvents.filter(
    e => e.gameTime > microState.currentBuildContext.xp - 15000
  ).length;

  if (healthPercent > 0.9) triggers.push('high_health');
  if (hasActiveCombo) triggers.push('kill_streak');
  if (microState.damageEfficiency > 3.0) triggers.push('high_efficiency');
  if (microState.dodgeRate > 0.9) triggers.push('perfect_avoidance');
  if (recentDamage === 0) triggers.push('no_recent_damage');
  if (microState.currentThreatLevel < 0.2) triggers.push('low_threat');

  // Determine escalation type and intensity
  const intensity = Math.min(triggers.length / 5, 1);

  if (triggers.length >= 4) {
    return {
      shouldTrigger: true,
      escalationType: 'elite_spawn',
      intensity,
      reasoning: 'Player dominating, introducing elite challenge',
      triggers,
    };
  } else if (triggers.includes('kill_streak') && triggers.length >= 3) {
    return {
      shouldTrigger: true,
      escalationType: 'spawn_surge',
      intensity,
      reasoning: 'Kill streak detected, testing player limits',
      triggers,
    };
  } else if (triggers.includes('low_threat') && triggers.includes('high_health')) {
    return {
      shouldTrigger: true,
      escalationType: 'mixed_wave',
      intensity: 0.5,
      reasoning: 'Player coasting, adding variety',
      triggers,
    };
  }

  return {
    shouldTrigger: false,
    escalationType: 'none',
    intensity: 0,
    reasoning: 'No challenge escalation needed',
    triggers,
  };
}

/**
 * Detect playstyle from run history.
 *
 * @param history - Recent run micro-states
 * @returns Playstyle analysis
 */
export function detectPlayStyle(history: RunMicroState[]): PlayStyleAnalysis {
  if (history.length < 3) {
    return {
      primary: 'experimenter',
      secondary: null,
      confidence: 0.3,
      evidence: [{ factor: 'insufficient_data', weight: 1, direction: 'supports' }],
      drift: { isDrifting: false, fromStyle: null, toStyle: null, progress: 0 },
    };
  }

  // Use mutable array for building, will be returned as readonly
  const evidence: Array<{
    readonly factor: string;
    readonly weight: number;
    readonly direction: 'supports' | 'contradicts';
  }> = [];
  const scores: Record<PlayStyle, number> = {
    berserker: 0,
    survivor: 0,
    speedrunner: 0,
    completionist: 0,
    experimenter: 0,
    optimizer: 0,
  };

  // Analyze aggression vs defense
  const avgDamageEfficiency = history.reduce((sum, r) => sum + r.damageEfficiency, 0) / history.length;
  const avgDodgeRate = history.reduce((sum, r) => sum + r.dodgeRate, 0) / history.length;

  if (avgDamageEfficiency > 2.0 && avgDodgeRate < 0.6) {
    scores.berserker += 2;
    evidence.push({ factor: 'high_aggression_low_caution', weight: 2, direction: 'supports' });
  }
  if (avgDodgeRate > 0.8 && avgDamageEfficiency < 1.5) {
    scores.survivor += 2;
    evidence.push({ factor: 'high_caution_low_aggression', weight: 2, direction: 'supports' });
  }

  // Analyze decision time
  const avgDecisionTime = history
    .flatMap(r => r.upgradeSelections.map(s => s.decisionTime))
    .reduce((sum, t, _, arr) => sum + t / arr.length, 0);

  if (avgDecisionTime < 2000) {
    scores.speedrunner += 1.5;
    evidence.push({ factor: 'fast_decisions', weight: 1.5, direction: 'supports' });
  } else if (avgDecisionTime > 5000) {
    scores.completionist += 1;
    evidence.push({ factor: 'deliberate_decisions', weight: 1, direction: 'supports' });
  }

  // Analyze build variety
  const uniqueUpgradesPerRun = history.map(r => new Set(r.upgradeSelections.map(s => s.selected)).size);
  const avgUniqueUpgrades = uniqueUpgradesPerRun.reduce((sum, n) => sum + n, 0) / history.length;
  const buildVariety = new Set(history.flatMap(r => r.upgradeSelections.map(s => s.selected))).size;

  if (buildVariety > history.length * 3) {
    scores.experimenter += 2;
    evidence.push({ factor: 'high_build_variety', weight: 2, direction: 'supports' });
  }
  if (avgUniqueUpgrades < 4 && history.length >= 5) {
    scores.optimizer += 2;
    evidence.push({ factor: 'consistent_builds', weight: 2, direction: 'supports' });
  }

  // Find primary and secondary
  const sortedStyles = (Object.entries(scores) as [PlayStyle, number][])
    .sort((a, b) => b[1] - a[1]);

  const primary = sortedStyles[0][0];
  const primaryScore = sortedStyles[0][1];
  const secondary = sortedStyles[1][1] > primaryScore * 0.5 ? sortedStyles[1][0] : null;
  const confidence = Math.min(primaryScore / 5, 1);

  // Check for drift
  const recentHalf = history.slice(-Math.floor(history.length / 2));
  const earlierHalf = history.slice(0, Math.floor(history.length / 2));
  const recentAnalysis = detectPlayStyle(recentHalf);
  const earlierAnalysis = detectPlayStyle(earlierHalf);

  const isDrifting = recentAnalysis.primary !== earlierAnalysis.primary && history.length >= 6;

  return {
    primary,
    secondary,
    confidence,
    evidence,
    drift: {
      isDrifting,
      fromStyle: isDrifting ? earlierAnalysis.primary : null,
      toStyle: isDrifting ? recentAnalysis.primary : null,
      progress: isDrifting ? 0.5 : 0,
    },
  };
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Check if an upgrade would counter a player weakness.
 */
function checkUpgradeCountersWeakness(upgrade: VerbUpgrade, macroState: PlayerMacroState): boolean {
  // Vampiric counters attrition deaths
  if (upgrade.id === 'vampiric' && macroState.deathCauses.primaryCause === 'attrition') {
    return true;
  }

  // Dash counters being cornered
  if (upgrade.id === 'dash' && macroState.deathCauses.byPlayerState.whileCornered > 3) {
    return true;
  }

  // Slow field counters being overwhelmed
  if (upgrade.id === 'slow_field' && macroState.deathCauses.byPlayerState.whileOverwhelmed > 3) {
    return true;
  }

  // Orbit counters close-range deaths
  if (upgrade.id === 'orbit') {
    const closeRangeDeaths = (macroState.deathCauses.byEnemyType.get('basic') || 0) +
      (macroState.deathCauses.byEnemyType.get('fast') || 0);
    if (closeRangeDeaths > macroState.deathCauses.totalDeaths * 0.5) {
      return true;
    }
  }

  return false;
}

/**
 * Check if an upgrade would complete a synergy.
 */
function checkSynergyCompletion(upgradeId: string, currentUpgrades: string[]): boolean {
  // Synergy definitions (from upgrades.ts)
  const synergyPairs: [string, string][] = [
    ['pierce', 'multishot'],
    ['orbit', 'dash'],
    ['dash', 'vampiric'],
    ['chain', 'burst'],
    ['multishot', 'burst'],
  ];

  for (const [a, b] of synergyPairs) {
    if (upgradeId === a && currentUpgrades.includes(b)) return true;
    if (upgradeId === b && currentUpgrades.includes(a)) return true;
  }

  return false;
}

/**
 * Emit an adaptation witness mark.
 */
export function emitAdaptationMark(
  decision: AdaptationMark['decision'],
  reasoning: string,
  inputs: Record<string, number | string | boolean>,
  output: unknown,
  gameTime: GameTimestamp,
  confidence: number = 0.8
): AdaptationMark {
  return {
    type: 'adaptation',
    decision,
    reasoning,
    inputs,
    output,
    gameTime,
    confidence,
  };
}

/**
 * Classify movement style from a position window.
 */
export function classifyMovementStyle(window: {
  positions: Vector2[];
  velocities: Vector2[];
  arenaWidth: number;
  arenaHeight: number;
}): MovementStyle {
  if (window.positions.length < 10) return 'calculated';

  const { positions, velocities, arenaWidth, arenaHeight } = window;

  // Calculate metrics
  let totalDistance = 0;
  let directionChanges = 0;
  let avgDistanceFromCenter = 0;
  let avgDistanceFromEdge = 0;

  const centerX = arenaWidth / 2;
  const centerY = arenaHeight / 2;

  for (let i = 1; i < positions.length; i++) {
    const dx = positions[i].x - positions[i - 1].x;
    const dy = positions[i].y - positions[i - 1].y;
    totalDistance += Math.sqrt(dx * dx + dy * dy);

    // Check direction change
    if (i >= 2) {
      const prevDx = positions[i - 1].x - positions[i - 2].x;
      const prevDy = positions[i - 1].y - positions[i - 2].y;
      const dot = dx * prevDx + dy * prevDy;
      const mag1 = Math.sqrt(dx * dx + dy * dy);
      const mag2 = Math.sqrt(prevDx * prevDx + prevDy * prevDy);
      if (mag1 > 0 && mag2 > 0) {
        const angle = Math.acos(Math.max(-1, Math.min(1, dot / (mag1 * mag2))));
        if (angle > Math.PI / 4) directionChanges++;
      }
    }

    // Distance from center
    const distFromCenter = Math.sqrt(
      (positions[i].x - centerX) ** 2 + (positions[i].y - centerY) ** 2
    );
    avgDistanceFromCenter += distFromCenter;

    // Distance from nearest edge
    const distFromEdge = Math.min(
      positions[i].x,
      arenaWidth - positions[i].x,
      positions[i].y,
      arenaHeight - positions[i].y
    );
    avgDistanceFromEdge += distFromEdge;
  }

  avgDistanceFromCenter /= positions.length;
  avgDistanceFromEdge /= positions.length;
  const turnRate = directionChanges / positions.length;

  // Calculate average velocity magnitude
  const avgSpeed = velocities.reduce((sum, v) => sum + Math.sqrt(v.x ** 2 + v.y ** 2), 0) / velocities.length;

  // Classify based on metrics
  if (avgSpeed < 50) return 'camping';
  if (turnRate > 0.4) return 'erratic';
  if (avgDistanceFromCenter < Math.min(arenaWidth, arenaHeight) * 0.2) return 'aggressive';
  if (avgDistanceFromEdge < 50) return 'camping';
  if (avgDistanceFromCenter > Math.min(arenaWidth, arenaHeight) * 0.35) return 'kiting';
  if (turnRate < 0.15 && avgSpeed > 100) return 'calculated';

  return 'defensive';
}

/**
 * Update heatmap with new position data.
 */
export function updateHeatmap(
  heatmap: HeatmapCell[][],
  position: Vector2,
  arenaWidth: number,
  arenaHeight: number,
  deltaTimeMs: number,
  event?: { type: 'kill' | 'death' | 'damage' }
): HeatmapCell[][] {
  const gridWidth = heatmap[0].length;
  const gridHeight = heatmap.length;

  const cellX = Math.min(Math.floor((position.x / arenaWidth) * gridWidth), gridWidth - 1);
  const cellY = Math.min(Math.floor((position.y / arenaHeight) * gridHeight), gridHeight - 1);

  // Deep clone for immutability
  const newHeatmap = heatmap.map(row => row.map(cell => ({ ...cell })));

  newHeatmap[cellY][cellX].timeSpent += deltaTimeMs;

  if (event) {
    switch (event.type) {
      case 'kill':
        newHeatmap[cellY][cellX].kills++;
        break;
      case 'death':
        newHeatmap[cellY][cellX].deaths++;
        break;
      case 'damage':
        newHeatmap[cellY][cellX].damagesTaken++;
        break;
    }
  }

  return newHeatmap;
}

/**
 * Calculate skill score from run metrics.
 */
export function calculateSkillScore(microState: RunMicroState): number {
  const weights = {
    damageEfficiency: 0.25,
    dodgeRate: 0.25,
    waveProgress: 0.2,
    comboPerformance: 0.15,
    clutchSurvival: 0.15,
  };

  // Normalize each metric to 0-1
  const normalizedEfficiency = Math.min(microState.damageEfficiency / 3, 1);
  const normalizedDodge = microState.dodgeRate;
  const normalizedWave = Math.min(microState.highestWave / 15, 1); // 15 waves = max score
  const normalizedCombo = Math.min(
    (microState.comboChains.reduce((max, c) => Math.max(max, c.kills), 0)) / 20,
    1
  );
  const normalizedClutch = Math.min(microState.clutchMoments.length / 5, 1);

  return (
    weights.damageEfficiency * normalizedEfficiency +
    weights.dodgeRate * normalizedDodge +
    weights.waveProgress * normalizedWave +
    weights.comboPerformance * normalizedCombo +
    weights.clutchSurvival * normalizedClutch
  );
}

// =============================================================================
// Exports Summary
// =============================================================================

export default {
  // Type guards
  isPlayerId,
  isRunId,
  isMovementStyle,
  isPlayStyle,
  isDamageEvent,
  isKillEvent,
  isAdaptationMark,

  // Factory functions
  generatePlayerId,
  generateRunId,
  createInitialHeatmap,
  createInitialRunMicroState,
  createInitialPlayerMacroState,
  createInitialPreferences,
  createInitialPlayerDataStore,

  // Adaptation rules
  calculateSpawnAdjustment,
  calculateUpgradeWeighting,
  shouldTriggerMercy,
  shouldTriggerChallenge,
  detectPlayStyle,

  // Utilities
  emitAdaptationMark,
  classifyMovementStyle,
  updateHeatmap,
  calculateSkillScore,
};
