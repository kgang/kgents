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
 */
export interface DebugTelegraph {
  enemyId: string;
  type: 'lunge' | 'charge' | 'stomp' | 'projectile' | 'combo';
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
}

// =============================================================================
// Window Augmentation
// =============================================================================

declare global {
  interface Window extends Partial<DebugAPI> {}
}

export {};
