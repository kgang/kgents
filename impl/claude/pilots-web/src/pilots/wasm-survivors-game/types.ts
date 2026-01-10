/**
 * Hornet Siege: The Colony Always Wins - Type Definitions
 *
 * Core types for the game systems. These are specific to the
 * "Hornet Siege" variant (Run 033+) which uses bee-themed enemies
 * instead of the generic WASM Survivors types.
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

// =============================================================================
// Core Primitives
// =============================================================================

export interface Vector2 {
  x: number;
  y: number;
}

/**
 * Input state for WASD controls
 * Uses simple `up`/`down`/`left`/`right` field names
 */
export interface InputState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
}

// =============================================================================
// Enemy Types (Bee Colony)
// =============================================================================

/**
 * Pulsing state for metamorphosis system (DD-030)
 */
export type PulsingState = 'normal' | 'pulsing' | 'seeking' | 'combining';

/**
 * Bee enemy types (PROTO_SPEC S6: Bee Taxonomy)
 * - worker: Basic bee, low damage, fast
 * - scout: Ranged bee with pheromone marking
 * - guard: Defensive bee, high health
 * - propolis: Sticky bee that slows player
 * - royal: Queen's guard, highest stats
 */
export type BeeType = 'worker' | 'scout' | 'guard' | 'propolis' | 'royal';

/**
 * Legacy enemy types (for backwards compatibility)
 */
export type LegacyEnemyType = 'basic' | 'fast' | 'tank' | 'boss' | 'spitter' | 'colossal_tide';

/**
 * Combined enemy type - includes both bee and legacy types
 */
export type EnemyType = BeeType | LegacyEnemyType;

/**
 * Map legacy enemy types to bee types
 */
export const LEGACY_TO_BEE_TYPE: Record<string, EnemyType> = {
  basic: 'worker',
  fast: 'scout',
  tank: 'guard',
  spitter: 'propolis',
  boss: 'royal',
  colossal_tide: 'royal',
  // Identity mappings for bee types
  worker: 'worker',
  scout: 'scout',
  guard: 'guard',
  propolis: 'propolis',
  royal: 'royal',
};

/**
 * Kill tier for audio feedback
 * - single: One enemy
 * - multi: 3+ enemies in quick succession
 * - massacre: 10+ enemies in combo
 */
export type KillTier = 'single' | 'multi' | 'massacre';

// =============================================================================
// THE BALL Types (TB-1 through TB-7)
// =============================================================================

/**
 * Ball phase types for the signature mechanic
 * - forming: Bees coordinate and move to surround player
 * - sphere: Ball is complete, player trapped
 * - silence: Dramatic pause before death sequence
 * - constrict: Ball tightens, raising temperature
 * - death: Player dies to heat exhaustion
 */
export type BallPhaseType = 'forming' | 'sphere' | 'silence' | 'constrict' | 'death';

// Note: PulsingState is defined earlier in this file near EnemyType

/**
 * Ball phase state with timing info
 */
export interface BallPhase {
  type: BallPhaseType;
  progress: number;     // 0-1 progress through phase
  startTime: number;    // Game time when phase started
  temperature?: number; // For constrict/death phases
  gapAngles?: number[]; // Angles where player can escape (forming phase)
  remainingGap?: number;
  gapAngle?: number;
  timeRemaining?: number;
}

// =============================================================================
// Mood System (DD-2: Seven Contrasts)
// =============================================================================

/**
 * Player mood states based on game state
 * - god: Low enemies, high health, dominating
 * - flow: Medium density, moderate challenge
 * - crisis: High danger, low health
 * - tragedy: Near death, overwhelming odds
 * - prey: Being hunted, THE BALL forming
 */
export type Mood = 'god' | 'flow' | 'crisis' | 'tragedy' | 'prey';

// =============================================================================
// Coordination States (for THE BALL)
// =============================================================================

/**
 * Enemy coordination states
 * - idle: Normal behavior
 * - alarm: Detected player threat
 * - coordinating: Moving to ball formation
 * - ball: Part of active ball
 */
export type CoordinationState = 'idle' | 'alarm' | 'coordinating' | 'ball';

// =============================================================================
// Game State Types
// =============================================================================

export type GamePhase = 'menu' | 'playing' | 'upgrade' | 'dead' | 'crystal';

export interface Player {
  position: Vector2;
  velocity: Vector2;
  health: number;
  maxHealth: number;
  level: number;
  xp: number;
  xpToNextLevel: number;
  damage: number;
  attackSpeed: number;
  moveSpeed: number;
  attackRange: number;
  attackCooldown: number;
  lastAttackTime: number;
  dashCooldown: number;
  lastDashTime: number;
  invincible: boolean;
  invincibilityEndTime: number;
  upgrades: string[];        // List of upgrade IDs the player has
  radius?: number;           // For collision detection (default: 15)
  // Knockback animation state (player loses control and slides to destination)
  knockback?: {
    startPos: Vector2;       // Where knockback started
    endPos: Vector2;         // Where player will end up
    startTime: number;       // When knockback started (gameTime)
    duration: number;        // How long the slide takes (ms)
  } | null;
  // RUN 039: Stun bounce state (pinball punishment for near-miss)
  stunBounce?: {
    active: boolean;
    velocity: Vector2;       // Current bounce velocity
    endTime: number;         // When stun ends (gameTime)
    bounceCount: number;     // How many times they've bounced
    maxBounces: number;      // Target bounces (2-3)
    ballCenter: Vector2;     // Center of the ball (for reflection calculation)
    ballRadius: number;      // Radius of the ball
  } | null;
  // Legacy compatibility fields
  id?: string;
  synergies?: string[];
  activeUpgrades?: Record<string, unknown>;
}

export interface Enemy {
  id: string;
  type: EnemyType;
  position: Vector2;
  velocity: Vector2;
  health: number;
  maxHealth: number;
  damage: number;
  speed: number;
  radius: number;
  xpValue: number;
  survivalTime: number;
  coordinationState: CoordinationState;
  targetAngle?: number;  // For ball formation
  // Behavior state machine fields
  behaviorState?: 'chase' | 'telegraph' | 'attack' | 'recovery';
  stateStartTime?: number;
  attackDirection?: Vector2;
  targetPosition?: Vector2;
  // Legacy compatibility fields
  color?: string;
  pulsingState?: 'normal' | 'pulsing' | 'seeking' | 'combining';
  // Colossal linking (metamorphosis system)
  isLinked?: boolean;
  seekTarget?: string;

  // ==========================================================================
  // Status Effect Visual Fields (Run 040: Status Effect Tints)
  // Used by GameCanvas for color overlay rendering
  // ==========================================================================

  /** Poison stacks (1-3+): Green tint intensity scales with stacks */
  poisonStacks?: number;

  /** Burn stacks: Orange/fire tint */
  burnStacks?: number;

  /** Slow/frozen stacks: Blue/ice tint */
  slowStacks?: number;

  /** Venom Architect stacks: Purple tint (infinite stacking ability) */
  venomArchitectStacks?: number;

  // ==========================================================================
  // Shield System (Royal Guards)
  // ==========================================================================

  /** Shield count - enemies with shields require multiple hits to kill.
   * When shield > 0, damage removes a shield instead of killing the enemy.
   * Visual: Glowing cyan ring around shielded enemies.
   */
  shield?: number;

  // ==========================================================================
  // Catch-Up / Self-Healing System Fields (Run 038)
  // Prevents enemies from getting stuck far from the action
  // ==========================================================================

  /** Time spent far from player (ms) - triggers catch-up boost when high */
  farAwayTime?: number;

  /** Whether enemy is currently in catch-up mode (moving faster) */
  inCatchUpMode?: boolean;

  // ==========================================================================
  // Bumper-Rail System (Run 039: Pinball-Surf Enhancement)
  // Bees transform into environmental elements during apex strike
  // ==========================================================================

  /**
   * Bumper state for combo chaining (DD-039)
   * - 'neutral': Can be bumpered (gold pulse telegraph)
   * - 'bumpered': Just hit, 100ms grace period
   * - 'charged': DANGER - hitting deals damage to player (red glow, 2s)
   * - 'recovering': Cooling down, can't be bumpered (500ms)
   * - 'locked': In formation, bumper disabled
   */
  bumperState?: 'neutral' | 'bumpered' | 'charged' | 'recovering' | 'locked';

  /** Timer for bumper state transitions (ms remaining in current state) */
  bumperStateTimer?: number;

  /** Time when bumper state last changed (gameTime) */
  bumperStateChangeTime?: number;

  /** Whether this bee was hit during current apex strike chain */
  hitDuringCurrentChain?: boolean;

  // ==========================================================================
  // Movement Trail Effects (Run 043: thermal_wake, rally_scent, draft)
  // ==========================================================================

  /** Current slow percent from player movement trail (thermal_wake + rally_scent) */
  trailSlowPercent?: number;

  // ==========================================================================
  // Aggro System (Run 045: aggro_pulse ability)
  // ==========================================================================

  /** Time until which this enemy is forced to target the player (gameTime ms) */
  aggroUntil?: number;
}

export interface Particle {
  id: string;
  position: Vector2;
  velocity: Vector2;
  color: string;
  size: number;
  lifetime: number;
  maxLifetime: number;
  type: 'kill' | 'xp' | 'damage' | 'spark';
}

export interface XPOrb {
  id: string;
  position: Vector2;
  value: number;
  lifetime: number;
}

export interface ScreenShake {
  intensity: number;
  duration: number;
  startTime: number;
}

export interface Formation {
  id: string;
  type: 'ball';
  center: Vector2;
  radius: number;
  participants: string[];  // Enemy IDs
  phase: BallPhase;
}

export interface ContrastState {
  enemyDensity: number;
  playerHealthPercent: number;
  killsPerSecond: number;
  timeSinceLastKill: number;
  coordinationLevel: number;
}

// =============================================================================
// Upgrade Types (DD-4: Verb Upgrades)
// =============================================================================

export interface Upgrade {
  id: string;
  name: string;
  description: string;
  tier: 1 | 2 | 3;
  icon: string;
  effect: UpgradeEffect;
}

export interface UpgradeEffect {
  damage?: number;
  attackSpeed?: number;
  moveSpeed?: number;
  health?: number;
  attackRange?: number;
  pierceCount?: number;
  orbitDamage?: number;
  dashCooldown?: number;
  dashDistance?: number;
  vampiricPercent?: number;
  chainBounces?: number;
}

export interface ActiveUpgrades {
  upgrades: Upgrade[];
  // Computed effects
  damageMultiplier: number;
  attackSpeedMultiplier: number;
  moveSpeedMultiplier: number;
  pierceCount: number;
  orbitActive: boolean;
  orbitDamage: number;
}

// =============================================================================
// Witness Types
// =============================================================================

/**
 * Build context at a moment in time
 */
export interface BuildContext {
  wave: number;
  health: number;
  maxHealth: number;
  upgrades: string[];
  synergies: string[];
  xp: number;
  enemiesKilled: number;
}

/**
 * Intent mark - what the player intended to do
 */
export interface IntentMark {
  id: string;
  type: 'upgrade_choice' | 'risky_engage' | 'defensive_pivot' | 'wave_enter';
  gameTime: number;
  context: BuildContext;
  risk: 'low' | 'medium' | 'high';
  alternatives?: string[];
}

/**
 * Outcome mark - what actually happened
 */
export interface OutcomeMark {
  intentId: string;
  success: boolean;
  consequence: string;
  gameTime: number;
  metricsSnapshot: SkillMetrics;
}

/**
 * Skill metrics at a point in time
 */
export interface SkillMetrics {
  damageEfficiency: number;
  dodgeRate: number;
  buildFocus: number;
  riskTolerance: number;
  estimate: number;
}

/**
 * Combined witness mark (intent + outcome)
 */
export interface WitnessMark {
  intent: IntentMark;
  outcome: OutcomeMark | null;
}

/**
 * Ghost - paths not taken (DD-2: Ghost as Honor)
 */
export interface Ghost {
  decisionPoint: number;
  chosen: string;
  unchosen: string[];
  context: BuildContext;
  projectedDrift: number;
}

/**
 * Witness context for a run
 */
export interface WitnessContext {
  runId: string;
  marks: WitnessMark[];
  ghosts: Ghost[];
  startTime: number;
  pendingIntents: Map<string, IntentMark>;
}

/**
 * Sealed trace of a complete run
 */
export interface Trace {
  runId: string;
  startTime: number;
  endTime: number;
  marks: WitnessMark[];
  finalContext: BuildContext;
  deathCause: string | null;
  sealed: boolean;
}

/**
 * Principle weights for playstyle analysis
 */
export interface GamePrincipleWeights {
  aggression: number;
  defense: number;
  mobility: number;
  precision: number;
  synergy: number;
}

/**
 * Drift entry in crystal history
 */
export interface DriftEntry {
  loss: number;
  drift: string;
  dominant: string;
  message: string;
}

/**
 * Segment of a crystal narrative
 */
export interface CrystalSegment {
  waves: [number, number];
  narrative: string;
  emotion: 'hope' | 'flow' | 'crisis' | 'triumph' | 'grief';
  keyMoments: string[];
}

/**
 * Game crystal - compressed proof of a run (DD-3: Crystal as Proof)
 */
export interface GameCrystal {
  runId: string;
  segments: CrystalSegment[];
  title: string;
  claim: string;
  duration: number;
  waveReached: number;
  finalWeights: GamePrincipleWeights;
  driftHistory: DriftEntry[];
  ghostCount: number;
  pivotMoments: number;
  shareableText: string;
  shareableHash: string;
}

/**
 * Simple crystal for UI display (legacy)
 */
export interface Crystal {
  runId: string;
  duration: number;
  wave: number;
  killCount: number;
  deathCause: string;
  upgrades: string[];
  mood: Mood;
  peakMoment: string;
  shareableText: string;
}

// =============================================================================
// Death Info (DD-14: Death as Ceremony)
// =============================================================================

export interface DeathInfo {
  cause: 'combat' | 'ball' | 'overwhelmed';
  lastAttacker: EnemyType | null;
  survivalTime: number;
  killCount: number;
  wave: number;
  nearMiss: boolean;  // Was this close? For narrative
}

// =============================================================================
// Game Events
// =============================================================================

export type GameEvent =
  | { type: 'kill'; enemy: Enemy }
  | { type: 'damage'; source: Enemy | null; amount: number }
  | { type: 'level_up'; level: number; choices: Upgrade[] }
  | { type: 'upgrade_selected'; upgrade: Upgrade }
  | { type: 'wave_start'; wave: number }
  | { type: 'ball_phase'; phase: BallPhase }
  | { type: 'mood_shift'; from: Mood; to: Mood }
  | { type: 'death'; info: DeathInfo };

// =============================================================================
// Projectile Types (for propolis sticky attacks)
// =============================================================================

export interface Projectile {
  id: string;
  position: Vector2;
  velocity: Vector2;
  radius: number;
  ownerId: string;
  damage: number;
  lifetime: number;
  color: string;
  slowDuration?: number;  // For propolis sticky projectiles
  hitEnemies?: Set<string>;  // Track already-hit enemies for pierce
  pierceRemaining?: number;  // Remaining pierce count
  health?: number;           // For destructible projectiles
}

// =============================================================================
// Complete Game State
// =============================================================================

// Include all possible game statuses (local + shared-primitives compatibility)
export type GameStatus = 'menu' | 'playing' | 'upgrade' | 'paused' | 'dead' | 'gameover' | 'victory';

export interface GameState {
  // Core state
  status: GameStatus;
  gameTime: number;
  wave: number;
  waveTimer: number;
  waveEnemiesRemaining: number;

  // Entities
  player: Player;
  enemies: Enemy[];
  projectiles: Projectile[];
  particles: Particle[];
  xpOrbs: XPOrb[];

  // Stats
  score: number;
  totalEnemiesKilled: number;
  killCount: number;  // Current combo
  comboCount: number;
  lastKillTime: number;

  // Visual effects
  screenShake: ScreenShake | null;

  // THE BALL system
  activeFormation: Formation | null;
  ballPhase: BallPhase | null;
  ballsFormed: number;
  colonyCoordination: number;  // 0-1, triggers BALL at 0.8

  // Emotional system
  contrastState: ContrastState;
  currentMood: Mood;

  // Upgrades
  upgradeChoices: Upgrade[] | null;
  activeUpgrades: ActiveUpgrades;

  // Legacy compatibility (for older code paths)
  phase?: GamePhase;
  activeColossals?: string[];  // Not used in bee theme
  hasWitnessedFirstMetamorphosis?: boolean;  // Not used in bee theme

  // NEW: Abilities/Melee/Combos system state (Run 036)
  // Note: These are managed by useGameLoop refs for performance,
  // but can be optionally exposed on GameState for debugging/UI
  abilitiesState?: import('./systems/abilities').ActiveAbilities;
  meleeState?: import('./systems/melee').MeleeAttackState;
  comboState?: import('./systems/combos').ComboState;
}

// =============================================================================
// Colors (DD-7: Arena as Hive)
// =============================================================================

export const COLORS = {
  // Primary
  amber: '#FFB800',
  honey: '#D4A017',
  honeycomb: '#8B6914',
  hiveDark: '#1a1a0f',
  hiveLight: '#2a2a1f',

  // Enemies
  worker: '#F4D03F',
  scout: '#F39C12',
  guard: '#E74C3C',
  propolis: '#9B59B6',
  royal: '#3498DB',

  // Effects
  danger: '#FF4444',
  warning: '#FFAA00',
  formation: '#FF6B6B',
  heat: '#FF3300',

  // UI
  text: '#F5F5DC',
  textDim: '#B8B8A0',
} as const;

// =============================================================================
// Arena Constants
// =============================================================================

export const ARENA_WIDTH = 800;
export const ARENA_HEIGHT = 600;
