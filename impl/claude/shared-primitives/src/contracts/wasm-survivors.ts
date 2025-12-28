/**
 * WASM Survivors Witnessed Run Lab - API Contracts
 *
 * Canonical source of truth for game and witness types.
 * Both game engine and witness layer verify against these definitions.
 *
 * @layer L4 (Specification)
 * @pilot wasm-survivors-game
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 * @see pilots/CONTRACT_COHERENCE.md
 */

// =============================================================================
// Core Game Types
// =============================================================================

/**
 * 2D vector for positions and velocities
 */
export interface Vector2 {
  x: number;
  y: number;
}

/**
 * Base entity interface for all game objects
 */
export interface Entity {
  id: string;
  position: Vector2;
  velocity: Vector2;
  radius: number;
  health: number;
  maxHealth: number;
}

/**
 * Active upgrade effects (DD-6: verb-based upgrades)
 */
export interface ActiveUpgrades {
  upgrades: string[];
  synergies: string[];
  pierceCount: number;
  orbitActive: boolean;
  orbitRadius: number;
  orbitDamage: number;
  dashCooldown: number;
  dashDistance: number;
  multishotCount: number;
  multishotSpread: number;
  vampiricPercent: number;
  chainBounces: number;
  chainRange: number;
  burstRadius: number;
  burstDamage: number;
  slowRadius: number;
  slowPercent: number;
}

/**
 * Player entity with upgrade state
 */
export interface Player extends Entity {
  level: number;
  xp: number;
  xpToNextLevel: number;
  upgrades: string[];
  synergies: string[];
  damage: number;
  attackSpeed: number;
  moveSpeed: number;
  attackRange: number;
  // DD-6: Active upgrade effects for physics system
  activeUpgrades?: ActiveUpgrades;
}

/**
 * Enemy types for spawning and difficulty
 * DD-24: Added 'spitter' for ranged variety
 * DD-030-4: Added 'colossal_tide' for metamorphosis
 */
export type EnemyType = 'basic' | 'fast' | 'tank' | 'boss' | 'spitter' | 'colossal_tide';

/**
 * Metamorphosis lifecycle states (DD-030-2)
 * Enemies transition through these states based on survival time:
 * - normal (0-10s): Standard behavior
 * - pulsing (10-15s): Visual warning, beginning of metamorphosis pressure
 * - seeking (15-20s): Actively gravitates toward other pulsing enemies
 * - combining (20s+ with collision): Merging into Colossal
 */
export type PulsingState = 'normal' | 'pulsing' | 'seeking' | 'combining';

/**
 * Enemy behavior states (DD-21: Pattern-Based Enemy Behaviors)
 */
export type EnemyBehaviorState = 'chase' | 'telegraph' | 'attack' | 'recovery';

/**
 * Enemy entity
 * DD-21: Added behavior state fields for pattern-based attacks
 * DD-030: Added metamorphosis fields for Run 030
 */
export interface Enemy extends Entity {
  type: EnemyType;
  damage: number;
  xpValue: number;
  color: string;
  // DD-21: Behavior state machine (combat)
  behaviorState?: EnemyBehaviorState;
  stateStartTime?: number;        // Timestamp when current state began
  attackDirection?: Vector2;      // Locked direction for charge attacks
  targetPosition?: Vector2;       // Target for current attack
  // DD-030: Metamorphosis fields
  survivalTime?: number;          // Time alive since spawn (accumulator)
  pulsingState?: PulsingState;    // Metamorphosis lifecycle state
  seekTarget?: string;            // ID of enemy being sought (seeking state)
  isLinked?: boolean;             // True if linked to a Colossal (visual only)
}

/**
 * Projectile entity
 */
export interface Projectile extends Entity {
  ownerId: string;
  damage: number;
  lifetime: number;
  color: string;
  // DD-6: Pierce upgrade support
  pierceRemaining?: number;  // How many more enemies this can hit (0 = stop on next hit)
  hitEnemies?: string[];     // IDs of enemies already hit (to prevent multi-hit)
}

// =============================================================================
// Upgrade Types
// =============================================================================

/**
 * Upgrade effect modifiers (multiplicative)
 */
export interface UpgradeEffect {
  damage?: number;
  attackSpeed?: number;
  moveSpeed?: number;
  health?: number;
  attackRange?: number;
  projectileCount?: number;
}

/**
 * Single upgrade definition
 */
export interface Upgrade {
  id: string;
  name: string;
  description: string;
  icon: string;
  effect: UpgradeEffect;
  synergiesWith: string[];
  color: string;
}

/**
 * Synergy combining multiple upgrades
 */
export interface Synergy {
  id: string;
  name: string;
  description: string;
  requires: string[];
  bonus: UpgradeEffect;
}

// =============================================================================
// Game State Types
// =============================================================================

/**
 * Game status states
 */
export type GameStatus = 'menu' | 'playing' | 'paused' | 'upgrade' | 'gameover' | 'victory';

/**
 * Complete game state
 */
export interface GameState {
  status: GameStatus;
  player: Player;
  enemies: Enemy[];
  projectiles: Projectile[];
  wave: number;
  waveTimer: number;
  waveEnemiesRemaining: number;
  totalEnemiesKilled: number;
  score: number;
  gameTime: number;  // L-IMPL-1: Accumulated game time, NOT Date.now()
  // DD-030: Metamorphosis tracking
  hasWitnessedFirstMetamorphosis?: boolean;  // For revelation sequence
  activeColossals?: string[];                 // IDs of currently active Colossals
}

/**
 * Input state from keyboard
 */
export interface InputState {
  up: boolean;
  down: boolean;
  left: boolean;
  right: boolean;
  // DD-10: Dash trigger
  dash?: boolean;
}

// =============================================================================
// Witness Mark Types (L2)
// =============================================================================

/**
 * Context captured with each mark
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
 * Intent mark - emitted BEFORE action resolves (L4)
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
 * Outcome mark - emitted AFTER action resolves
 */
export interface OutcomeMark {
  intentId: string;
  success: boolean;
  consequence: string;
  gameTime: number;
  metricsSnapshot: SkillMetrics;
}

/**
 * Combined mark in trace
 */
export interface WitnessMark {
  intent: IntentMark;
  outcome: OutcomeMark | null;  // null if run ended before resolution
}

// =============================================================================
// Trace Types (L2)
// =============================================================================

/**
 * Immutable run trace
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
 * Trace segment for compression
 */
export interface TraceSegment {
  marks: WitnessMark[];
  startWave: number;
  endWave: number;
  narrative: string;
  principleWeights: GamePrincipleWeights;
}

// =============================================================================
// Ghost Types (L2)
// =============================================================================

/**
 * Single ghost (unchosen path)
 */
export interface Ghost {
  decisionPoint: number;
  chosen: string;
  unchosen: string[];
  context: BuildContext;
  projectedDrift: number;
}

/**
 * Ghost graph for a run
 */
export interface GhostGraph {
  runId: string;
  ghosts: Ghost[];
  totalDecisionPoints: number;
  averageDrift: number;
  maxDriftMoment: Ghost | null;
}

// =============================================================================
// Galois Types (L2)
// =============================================================================

/**
 * Principle weights for playstyle (game-specific)
 */
export interface GamePrincipleWeights {
  aggression: number;
  defense: number;
  mobility: number;
  precision: number;
  synergy: number;
}

/**
 * Galois loss calculation result
 */
export interface GaloisResult {
  loss: number;
  drift: 'stable' | 'drifting' | 'pivoting';
  dominant: keyof GamePrincipleWeights;
  message: string;
}

// =============================================================================
// Crystal Types (L2)
// =============================================================================

/**
 * Single narrative segment in crystal
 */
export interface CrystalSegment {
  waves: [number, number];
  narrative: string;
  emotion: 'hope' | 'flow' | 'crisis' | 'triumph' | 'grief';
  keyMoments: string[];
}

/**
 * Compressed proof of run (game-specific)
 */
export interface GameCrystal {
  runId: string;
  segments: CrystalSegment[];
  title: string;
  claim: string;
  duration: number;
  waveReached: number;
  finalWeights: GamePrincipleWeights;
  driftHistory: GaloisResult[];
  ghostCount: number;
  pivotMoments: number;
  shareableText: string;
  shareableHash: string;
}

// =============================================================================
// Skill Estimation Types (L1)
// =============================================================================

/**
 * Skill metrics for adaptive difficulty
 */
export interface SkillMetrics {
  damageEfficiency: number;
  dodgeRate: number;
  buildFocus: number;
  riskTolerance: number;
  estimate: number;
}

// =============================================================================
// Upgrade Choice Types (UI)
// =============================================================================

/**
 * Upgrade choice with preview information
 */
export interface UpgradeChoice {
  upgrade: Upgrade;
  isNew: boolean;
  synergyPreview: string[];
  galoisDriftPreview: number;
}

// =============================================================================
// Contract Invariants
// =============================================================================

/**
 * Verify game state invariants
 */
export const GAME_STATE_INVARIANTS = {
  'gameTime is number': (s: GameState) => typeof s.gameTime === 'number',
  'wave is positive': (s: GameState) => s.wave >= 0,
  'player health <= maxHealth': (s: GameState) => s.player.health <= s.player.maxHealth,
  'enemies is array': (s: GameState) => Array.isArray(s.enemies),
} as const;

/**
 * Verify witness mark invariants
 */
export const WITNESS_MARK_INVARIANTS = {
  'intent has gameTime': (m: WitnessMark) => typeof m.intent.gameTime === 'number',
  'intent has context': (m: WitnessMark) => m.intent.context !== null,
  'outcome references intent': (m: WitnessMark) => m.outcome === null || m.outcome.intentId === m.intent.id,
} as const;

/**
 * Verify game crystal invariants
 */
export const GAME_CRYSTAL_INVARIANTS = {
  'has runId': (c: GameCrystal) => typeof c.runId === 'string' && c.runId.length > 0,
  'has segments': (c: GameCrystal) => Array.isArray(c.segments) && c.segments.length > 0,
  'shareable text under 280': (c: GameCrystal) => c.shareableText.length <= 280,
} as const;
