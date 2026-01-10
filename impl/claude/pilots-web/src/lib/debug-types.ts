/**
 * Debug API Type Definitions
 *
 * Type definitions for the PLAYER debug API that exposes game state
 * to Playwright tests for qualia verification.
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

// =============================================================================
// Debug State Types
// =============================================================================

/**
 * Debug representation of an enemy entity
 */
export interface DebugEnemy {
  id: string;
  type: string;
  position: { x: number; y: number };
  health: number;
  behaviorState: 'chase' | 'telegraph' | 'attack' | 'recovery';
  telegraphProgress?: number;
  // DD-030: Metamorphosis fields
  survivalTime?: number;
  pulsingState?: 'normal' | 'pulsing' | 'seeking' | 'combining';
}

/**
 * Debug representation of the player entity
 */
export interface DebugPlayer {
  position: { x: number; y: number };
  health: number;
  maxHealth: number;
  invincible: boolean;
  upgrades: string[];
}

/**
 * Debug representation of a damage event
 */
export interface DebugDamageEvent {
  enemyType: string;
  attackType: string;
  damage: number;
  timestamp: number;
}

/**
 * Debug representation of an active telegraph
 * Attack types are bee-themed (Run 033+)
 */
export interface DebugTelegraph {
  enemyId: string;
  type: 'swarm' | 'sting' | 'block' | 'sticky' | 'combo' | 'elite';
  progress: number; // 0-1
  position: { x: number; y: number };
  radius?: number;
  direction?: { x: number; y: number };
}

/**
 * Complete debug game state snapshot
 */
export interface DebugGameState {
  wave: number;
  score: number;
  gameTime: number;
  enemies: DebugEnemy[];
  player: DebugPlayer;
  telegraphs: DebugTelegraph[];
  lastDamage: DebugDamageEvent | null;
}

// =============================================================================
// Audio Debug Types (since Playwright can't "hear")
// =============================================================================

/**
 * Audio log entry for tracking audio events
 */
export interface DebugAudioLogEntry {
  time: number;
  event: string;
  params: Record<string, unknown>;
}

/**
 * Audio system state snapshot
 */
export interface DebugAudioState {
  contextState: string;
  isEnabled: boolean;
  masterVolume: number;
  activeSoundCount: number;
  sampleRate: number | null;
  analyserConnected: boolean;
}

// =============================================================================
// Emotional/Contrast Debug Types (Part VI: Arc Grammar)
// =============================================================================

/**
 * Debug representation of arc state
 */
export interface DebugArcState {
  currentPhase: 'POWER' | 'FLOW' | 'CRISIS' | 'TRAGEDY';
  phasesVisited: string[];
  phaseStartTime: number;
  closureType: string | null;
}

/**
 * Debug representation of contrast state
 */
export interface DebugContrastState {
  activeDimensions: string[];
  contrastsVisited: number;
  contrastHistory: string[];
  lastContrastTime: number;
}

/**
 * Debug representation of the emotional state
 */
export interface DebugEmotionalState {
  arc: DebugArcState;
  contrast: DebugContrastState;
  currentVoiceLine: { text: string; type: string } | null;
  voiceLineHistory: string[];
}

// =============================================================================
// Debug API Interface
// =============================================================================

/**
 * Debug API functions exposed on window when ?debug=true
 */
export interface DebugAPI {
  /** Get complete game state snapshot */
  DEBUG_GET_GAME_STATE: () => DebugGameState;
  /** Get enemy array with behavior states */
  DEBUG_GET_ENEMIES: () => DebugEnemy[];
  /** Get player state */
  DEBUG_GET_PLAYER: () => DebugPlayer;
  /** Get last damage event */
  DEBUG_GET_LAST_DAMAGE: () => DebugDamageEvent | null;
  /** Get active telegraphs */
  DEBUG_GET_TELEGRAPHS: () => DebugTelegraph[];
  /** Spawn an enemy at position */
  DEBUG_SPAWN: (type: string, position: { x: number; y: number }) => void;
  /** Toggle player invincibility */
  DEBUG_SET_INVINCIBLE: (invincible: boolean) => void;
  /** Skip to next wave */
  DEBUG_SKIP_WAVE: () => void;
  /** Kill all enemies */
  DEBUG_KILL_ALL_ENEMIES: () => void;
  /** Trigger level up */
  DEBUG_LEVEL_UP: () => void;

  // Audio debug functions (since Playwright can't "hear")
  /** Get audio system state (context state, isEnabled, masterVolume, activeSounds) */
  DEBUG_GET_AUDIO_STATE: () => DebugAudioState;
  /** Get current audio output level (0-255 scale from AnalyserNode) */
  DEBUG_GET_AUDIO_LEVEL: () => number;
  /** Get last 50 audio events with timestamps */
  DEBUG_GET_AUDIO_LOG: () => DebugAudioLogEntry[];
  /** Clear the audio event log */
  DEBUG_CLEAR_AUDIO_LOG: () => void;

  // Emotional/Contrast debug functions (Part VI: Arc Grammar)
  /** Get emotional state (arc phase, contrasts visited, voice lines) */
  DEBUG_GET_EMOTIONAL_STATE: () => DebugEmotionalState | null;

  // THE BALL debug functions (Run 036: Signature mechanic)
  /** Get THE BALL formation state */
  DEBUG_GET_BALL_STATE: () => DebugBallState | null;
  /** Force THE BALL to start forming (bypasses normal triggers) */
  DEBUG_FORCE_BALL: () => void;

  // Time scale debug functions (for accelerated testing)
  /**
   * Set the debug time scale for accelerated testing.
   *
   * Key insight: PlaythroughAgent's reaction model operates in GAME time.
   * At 4x: 250ms game-time reaction = 62.5ms wall-clock time.
   * The reaction is still "250ms in game" - it just happens faster IRL.
   *
   * @param scale - Time multiplier (e.g., 4.0 for 4x speed). Range: 0.1 to 10.0
   */
  DEBUG_SET_TIME_SCALE: (scale: number) => void;
  /** Get the current debug time scale multiplier */
  DEBUG_GET_TIME_SCALE: () => number;
}

// =============================================================================
// THE BALL Debug Types
// =============================================================================

export interface DebugBallState {
  // RUN 039: Added 'gathering' phase for pre-formation telegraph
  phase: 'inactive' | 'gathering' | 'forming' | 'silence' | 'constrict' | 'cooking' | 'dissipating';
  phaseProgress: number;
  center: { x: number; y: number };
  currentRadius: number;
  gapAngle: number;       // degrees
  gapSize: number;        // degrees
  temperature: number;    // 0-100
  beesInFormation: number;
  escapeCount: number;
}

// =============================================================================
// Window Augmentation
// =============================================================================

declare global {
  interface Window extends Partial<DebugAPI> {}
}

export {};
