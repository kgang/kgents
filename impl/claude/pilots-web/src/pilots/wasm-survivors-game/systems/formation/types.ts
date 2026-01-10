/**
 * THE BALL Formation System - Type Definitions
 *
 * Structured state types following the telegraph/state machine pattern
 * from enemies.ts and melee.ts.
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part XI Phase 1)
 */

import type { Vector2 } from '../../types';

// =============================================================================
// Phase Types
// =============================================================================

/**
 * Main ball phase state machine (RUN 039: Added 'gathering' pre-phase)
 * inactive → gathering → forming → silence → constrict → cooking
 *                                                ↓
 *                                          dissipating → inactive
 *
 * Gathering phase: Shows indicator, bees travel slowly to positions
 */
export type BallPhase =
  | 'inactive'      // No ball forming
  | 'gathering'     // NEW: Pre-formation telegraph, bees traveling to positions
  | 'forming'       // 0-6s: Surrounding, crescendo
  | 'silence'       // 6-8s: The "oh no" moment
  | 'constrict'     // 8-10.5s: Closing in, escape window
  | 'cooking'       // Trapped, heat damage
  | 'dissipating';  // Ball breaking up after escape

/**
 * Lunge attack sub-state machine (RUN 040 - expanded windup)
 * idle → pullback → charge → lunge → return → idle
 *
 * - pullback (500ms): Bee moves backward at normal speed
 * - charge (350ms): Bee holds position, accelerating/charging
 * - lunge (400ms): Bee dashes toward player
 * - return (200ms): Bee returns to formation
 *
 * NOTE: 'windup' is kept for backward compatibility (maps to pullback/charge)
 */
export type LungePhase = 'idle' | 'windup' | 'pullback' | 'charge' | 'lunge' | 'return';

/**
 * Outside punch sub-state machine (RUN 039 - telegraph system)
 * idle → windup (400ms) → punch (100ms) → recovery (200ms) → idle
 *
 * - windup: Bee glows, shows intent line toward player (DODGEABLE)
 * - punch: Quick strike - hits if player still in range
 * - recovery: Brief cooldown animation before bee can act again
 */
export type OutsidePunchPhase = 'idle' | 'windup' | 'punch' | 'recovery';

/**
 * Individual outside punch state (RUN 039)
 * Tracks a single bee's punch attack telegraph
 */
export interface OutsidePunchState {
  beeId: string;
  phase: OutsidePunchPhase;
  phaseStartTime: number;
  // Position snapshot at windup start (bee may move slightly)
  startPos: Vector2;
  // Target position (player's position when punch started)
  targetPos: Vector2;
  // Direction toward ball center (knockback direction)
  knockbackDir: Vector2;
}

// =============================================================================
// State Components (Separated Concerns)
// =============================================================================

/**
 * Core ball phase state
 */
export interface BallCoreState {
  phase: BallPhase;
  phaseStartTime: number;
  phaseProgress: number;
  playerEscaped: boolean;
  escapeCount: number;
}

/**
 * Ball geometry and movement
 */
export interface BallGeometryState {
  center: Vector2;
  currentRadius: number;
  velocity: Vector2;
  targetPosition: Vector2;
}

/**
 * Escape gap state
 */
export interface BallGapState {
  angle: number;              // Current gap angle (radians)
  size: number;               // Current gap size (radians)
  rotationSpeed: number;      // Current rotation speed
  rotationDirection: 1 | -1;  // CW or CCW
  lastDirectionChange: number;
  lastSpeedChange: number;
}

/**
 * Lunge attack state
 *
 * RUN 042: Added beeType for scaled lunge parameters (hit radius, damage, windup speed)
 */
export interface BallLungeState {
  phase: LungePhase;
  beeId: string | null;
  beeType: string | null;    // RUN 042: Enemy type for lunge scaling
  phaseStartTime: number;
  startPos: Vector2;         // Original formation position
  pullbackPos: Vector2;      // Position after pullback (RUN 040)
  targetPos: Vector2;        // Lunge destination (past player)
  // RUN 042: Scaled parameters (computed at lunge start based on beeType)
  scaledHitRadius: number;   // Hit radius scaled by bee type
  scaledDamage: number;      // Damage scaled by bee type
  scaledWindupDuration: number;  // Windup duration (shorter = more dangerous)
  // Timing
  lastLungeTime: number;
  nextLungeInterval: number;
}

/**
 * Formation membership state
 */
export interface BallFormationState {
  beeIds: string[];
  positions: Map<string, Vector2>;
  outsidePunchCooldowns: Map<string, number>;
}

/**
 * Damage and boundary state
 */
export interface BallDamageState {
  temperature: number;
  lastDamageTick: number;
  lastBoundaryDamageTick: number;
  lastNearMissTime: number;  // RUN 039: Track near-miss cooldown
}

/**
 * Dissipation tracking
 *
 * Flow: active → fading (can revive) → dissipating → inactive
 *
 * When player escapes:
 *   1. playerOutsideTime accumulates until escapeGracePeriod
 *   2. Ball enters 'fading' state, fadeProgress increases
 *   3. If player returns during fading, fadeProgress decreases (revive)
 *   4. If fadeProgress reaches 1.0, ball enters final dissipation
 */
export interface BallDissipationState {
  playerOutsideTime: number;
  isDissipating: boolean;          // Final dissipation (no revival)
  dissipationStartTime: number;
  // NEW: Fade/linger system
  isFading: boolean;               // Ball is fading but can revive
  fadeProgress: number;            // 0 = solid, 1 = fully faded
  fadeStartTime: number;           // When fade started
}

// =============================================================================
// Composed State (Full Ball State)
// =============================================================================

/**
 * Complete ball state - composed from sub-states
 */
export interface BallState {
  core: BallCoreState;
  geometry: BallGeometryState;
  gap: BallGapState;
  lunge: BallLungeState;
  formation: BallFormationState;
  damage: BallDamageState;
  dissipation: BallDissipationState;
}

// =============================================================================
// Legacy Flat State (For Migration Compatibility)
// =============================================================================

/**
 * Legacy flat ball state - matches existing formation.ts
 * Used during migration to maintain compatibility with useGameLoop/GameCanvas
 */
export interface LegacyBallState {
  phase: BallPhase;
  phaseStartTime: number;
  phaseProgress: number;
  center: Vector2;
  currentRadius: number;
  gapAngle: number;
  gapSize: number;
  targetPosition: Vector2;
  velocity: Vector2;
  gapRotationSpeed: number;
  gapRotationDirection: 1 | -1;
  lastDirectionChange: number;
  lastSpeedChange: number;
  lastLungeTime: number;
  nextLungeInterval: number;
  activeLunge: {
    beeId: string;
    beeType: string;         // RUN 042: Enemy type for lunge scaling
    phase: LungePhase;
    windupStartTime: number;
    lungeStartTime: number;
    startPos: Vector2;
    targetPos: Vector2;
    duration: number;
    // RUN 042: Scaled parameters (computed at lunge start based on beeType)
    scaledHitRadius: number;
    scaledDamage: number;
    scaledWindupDuration: number;
  } | null;
  lastBoundaryDamageTick: number;
  lastNearMissTime: number;  // RUN 039: Track near-miss cooldown
  playerOutsideTime: number;
  isDissipating: boolean;
  dissipationStartTime: number;
  // Fade/linger fields (RUN 039)
  isFading: boolean;
  fadeProgress: number;
  fadeStartTime: number;
  outsideBeePunchCooldowns: Map<string, number>;
  formationBeeIds: string[];
  formationPositions: Map<string, Vector2>;
  temperature: number;
  lastDamageTick: number;
  playerEscaped: boolean;
  escapeCount: number;
  // Multi-ball dynamics (RUN 041)
  ballTier: 1 | 2;                  // 1 = normal, 2 = larger second ball
  ballId: number;                    // Unique ID for this ball instance
  hasKnockback: boolean;             // Whether boundary has knockback (false for tier 2)
  // RUN 042: Ball promotion dynamics
  wasPromoted: boolean;              // True if this ball was promoted from tier 2 to tier 1
  promotionTime: number;             // When promotion happened (for speed boost timing)
  // RUN 039: Active outside punch telegraphs
  activePunches: OutsidePunchState[];
}

/**
 * Global ball formation manager state
 * Tracks cooldowns and multiple balls
 */
export interface BallManagerState {
  balls: LegacyBallState[];           // Active balls (usually 0-2)
  beeCooldowns: Map<string, number>;  // beeId -> cooldown expiry time
  lastBallEndTime: number;            // When last ball ended (for formation cooldown)
  nextBallId: number;                 // Counter for unique ball IDs
}

// =============================================================================
// Telegraph Data (For Rendering)
// =============================================================================

/**
 * Telegraph data extracted from state for rendering
 * Follows pattern from enemies.ts getBeeTelegraph()
 */
export interface BallTelegraphData {
  // RUN 039: Added 'gathering' for pre-formation telegraph
  type: 'gathering' | 'forming' | 'silence' | 'constrict' | 'cooking' | 'lunge_windup' | 'lunge_attack' | 'fading' | 'dissipating';
  center: Vector2;
  radius: number;
  gapAngle: number;
  gapSize: number;
  progress: number;
  temperature: number;
  isDissipating: boolean;
  // Fade/linger state (for opacity and revival indicator)
  isFading: boolean;
  fadeProgress: number;      // 0 = solid, 1 = fully faded
  isReviving: boolean;       // True when player is inside during fade
  // Lunge-specific (when active)
  lungeBeeId?: string;
  lungeBeePos?: Vector2;
  lungeTargetPos?: Vector2;
  lungeProgress?: number;
  lungePhase?: LungePhase;
}

// =============================================================================
// Event Types
// =============================================================================

/**
 * All ball-related event types
 */
export type BallEventType =
  // Phase transitions
  | 'ball_gathering_started'   // NEW: Pre-formation telegraph
  | 'ball_forming_started'
  | 'ball_silence_started'
  | 'ball_constrict_started'
  | 'ball_cooking_started'
  | 'ball_escaped'
  | 'ball_dispersed'
  | 'ball_dissipating'
  // Fade/linger events (player can return during these)
  | 'ball_fading_started'    // Ball starting to fade after escape
  | 'ball_reviving'          // Player returned, ball recovering
  | 'ball_revived'           // Ball fully recovered from fade
  // Lunge events (RUN 040: expanded with pullback/charge)
  | 'lunge_pullback_started'  // Bee starting to move backward
  | 'lunge_charge_started'    // Bee holding position, charging
  | 'lunge_windup_started'    // Legacy: emitted at start of pullback for compat
  | 'lunge_attack_started'
  | 'lunge_hit'
  | 'lunge_return_started'
  // Damage events
  | 'ball_damage'
  | 'boundary_touch'
  // RUN 039: Near-miss punishment
  | 'ball_near_miss'           // Player almost escaped but missed the gap
  // Outside punch events (RUN 039: Telegraph system)
  | 'outside_punch'           // Legacy: instant punch (backwards compat)
  | 'punch_windup_started'    // Bee started winding up (visible telegraph)
  | 'punch_attack'            // Punch thrown (may hit or whiff)
  | 'punch_hit'               // Punch connected with player
  | 'punch_whiff'             // Player dodged the punch
  | 'punch_recovery_started'; // Bee recovering after punch

/**
 * Event data payload
 */
export interface BallEventData {
  temperature?: number;
  damage?: number;
  escapeGapAngle?: number;
  knockbackDirection?: Vector2;
  knockbackForce?: number;
  lungingBeeId?: string;
  // RUN 039: Dissolution event data
  reason?: 'too_few_bees' | 'player_escaped' | 'timeout';
  remainingBees?: number;
  // RUN 039: Outside punch telegraph data
  punchingBeeId?: string;
  punchPhase?: 'windup' | 'punch' | 'recovery';
  windupProgress?: number;    // 0-1 progress through windup
  dodged?: boolean;           // True if player dodged the punch
  // RUN 039: Near-miss data
  nearMissDistance?: number;  // How close they were to the gap (0-1, lower = closer)
}

/**
 * Ball formation event
 */
export interface BallEvent {
  type: BallEventType;
  timestamp: number;
  position: Vector2;
  data?: BallEventData;
}

// =============================================================================
// Update Context & Results
// =============================================================================

/**
 * Context passed to all update functions
 */
export interface BallUpdateContext {
  playerPos: Vector2;
  enemies: Array<{
    id: string;
    position: Vector2;
    type: string;
  }>;
  gameTime: number;
  deltaTime: number;
  coordinationLevel: number;
  wave: number;
}

/**
 * Knockback source type for sound effects
 */
export type KnockbackSourceType = 'lunge' | 'boundary' | 'punch';

/**
 * Individual knockback source (for sound effects)
 */
export interface KnockbackSource {
  type: KnockbackSourceType;
  direction: Vector2;
  force: number;
}

/**
 * Result from main update function
 */
export interface BallUpdateResult {
  state: LegacyBallState;
  events: BallEvent[];
  damageToPlayer: number;
  knockback: {
    direction: Vector2;
    force: number;
  } | null;
  // RUN 038: Individual knockback sources for sound effects
  // When multiple knockbacks happen (e.g., punch into boundary),
  // the player slides to final position but each source plays its sound
  knockbackSources: KnockbackSource[];
}

/**
 * Result from lunge update
 */
export interface LungeUpdateResult {
  state: BallLungeState;
  events: BallEvent[];
  knockback: {
    direction: Vector2;
    force: number;
  } | null;
  damageDealt: number;
}

/**
 * Result from boundary collision
 */
export interface BoundaryResult {
  knockback: {
    direction: Vector2;
    force: number;
  } | null;
  damageDealt: number;
  events: BallEvent[];
}
