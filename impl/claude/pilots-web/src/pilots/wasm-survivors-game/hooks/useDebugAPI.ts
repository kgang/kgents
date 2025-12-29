/**
 * WASM Survivors - Debug API Hook
 *
 * Exposes game state to Playwright tests for PLAYER qualia verification.
 * Only active when ?debug=true is in the URL.
 *
 * Debug functions are exposed on window:
 * - DEBUG_GET_GAME_STATE() - full snapshot
 * - DEBUG_GET_ENEMIES() - enemy array with behavior states
 * - DEBUG_GET_PLAYER() - player state
 * - DEBUG_GET_LAST_DAMAGE() - last damage event
 * - DEBUG_GET_TELEGRAPHS() - active telegraphs
 * - DEBUG_SPAWN(type, position) - spawn enemy
 * - DEBUG_SET_INVINCIBLE(bool) - toggle invincibility
 * - DEBUG_SKIP_WAVE() - advance wave
 * - DEBUG_KILL_ALL_ENEMIES() - clear enemies
 * - DEBUG_LEVEL_UP() - trigger level up
 *
 * Audio Debug Functions (since Playwright can't "hear"):
 * - DEBUG_GET_AUDIO_STATE() - context state, isEnabled, masterVolume, activeSounds
 * - DEBUG_GET_AUDIO_LEVEL() - current output level (0-255)
 * - DEBUG_GET_AUDIO_LOG() - last 50 audio events with timestamps
 * - DEBUG_CLEAR_AUDIO_LOG() - clear the audio event log
 *
 * Emotional/Contrast Debug Functions (Part VI: Arc Grammar):
 * - DEBUG_GET_EMOTIONAL_STATE() - arc phase, contrasts visited, voice lines
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import { useEffect, useRef, useCallback } from 'react';
import type { GameState, Enemy, EnemyType, Vector2 } from '../types';
import type {
  DebugEnemy,
  DebugPlayer,
  DebugDamageEvent,
  DebugTelegraph,
  DebugGameState,
  DebugEmotionalState,
} from '../../../lib/debug-types';
import type { TelegraphData } from '../systems/enemies';
import type { EmotionalState, VoiceLine } from '../systems/contrast';

// Audio debug functions
import {
  DEBUG_GET_AUDIO_STATE,
  DEBUG_GET_AUDIO_LEVEL,
  DEBUG_GET_AUDIO_LOG,
  DEBUG_CLEAR_AUDIO_LOG,
} from '../systems/audio';

// =============================================================================
// Types
// =============================================================================

// Import BallState for debug exposure
import type { BallState } from '../systems/formation';

export interface DebugAPIConfig {
  gameState: GameState;
  telegraphs: TelegraphData[];
  emotionalState: EmotionalState | null;  // Part VI: Emotional state for debug
  ballState?: BallState | null;  // Run 036: THE BALL formation state
  onSpawnEnemy: (type: EnemyType, position: Vector2) => void;
  onSetInvincible: (invincible: boolean) => void;
  onSkipWave: () => void;
  onKillAllEnemies: () => void;
  onLevelUp: () => void;
  onForceBall?: () => void;  // Run 036: Force THE BALL to start forming
}

export interface UseDebugAPIResult {
  isDebugMode: boolean;
  lastDamage: DebugDamageEvent | null;
  recordDamage: (enemyType: string, attackType: string, damage: number) => void;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Debug API hook - exposes game state to window for Playwright tests
 */
export function useDebugAPI(config: DebugAPIConfig): UseDebugAPIResult {
  const {
    gameState,
    telegraphs,
    emotionalState,
    ballState,
    onSpawnEnemy,
    onSetInvincible,
    onSkipWave,
    onKillAllEnemies,
    onLevelUp,
    onForceBall,
  } = config;

  // Check if debug mode is enabled via URL parameter
  const isDebugMode = typeof window !== 'undefined' &&
    new URLSearchParams(window.location.search).get('debug') === 'true';

  // Track last damage event
  const lastDamageRef = useRef<DebugDamageEvent | null>(null);

  // Track invincibility state (not in game state, managed separately)
  const invincibleRef = useRef<boolean>(false);

  // Record a damage event
  const recordDamage = useCallback((enemyType: string, attackType: string, damage: number) => {
    lastDamageRef.current = {
      enemyType,
      attackType,
      damage,
      timestamp: Date.now(),
    };
  }, []);

  // Convert game enemy to debug enemy
  const toDebugEnemy = useCallback((enemy: Enemy, currentTelegraphs: TelegraphData[]): DebugEnemy => {
    const telegraph = currentTelegraphs.find(t => t.enemyId === enemy.id);
    return {
      id: enemy.id,
      type: enemy.type,
      position: { x: enemy.position.x, y: enemy.position.y },
      health: enemy.health,
      behaviorState: enemy.behaviorState ?? 'chase',
      telegraphProgress: telegraph?.progress,
      survivalTime: enemy.survivalTime,     // DD-030: Metamorphosis timer
      pulsingState: enemy.pulsingState ?? 'normal',
    };
  }, []);

  // Convert game state to debug player
  const toDebugPlayer = useCallback((state: GameState): DebugPlayer => {
    return {
      position: { x: state.player.position.x, y: state.player.position.y },
      health: state.player.health,
      maxHealth: state.player.maxHealth,
      invincible: invincibleRef.current,
      upgrades: [...state.player.upgrades],
    };
  }, []);

  // Convert telegraph data to debug telegraph
  const toDebugTelegraph = useCallback((telegraph: TelegraphData): DebugTelegraph => {
    // Map bee telegraph types to debug attack types
    // Bee types: 'swarm' | 'sting' | 'block' | 'sticky' | 'elite'
    // Debug types: 'swarm' | 'sting' | 'block' | 'sticky' | 'combo' | 'elite'
    const attackType = telegraph.type as DebugTelegraph['type'];
    return {
      enemyId: telegraph.enemyId,
      type: attackType,
      progress: telegraph.progress,
      position: { x: telegraph.position.x, y: telegraph.position.y },
      radius: telegraph.radius,
      direction: telegraph.direction
        ? { x: telegraph.direction.x, y: telegraph.direction.y }
        : undefined,
    };
  }, []);

  // Get complete debug game state
  const getDebugGameState = useCallback((): DebugGameState => {
    return {
      wave: gameState.wave,
      score: gameState.score,
      gameTime: gameState.gameTime,
      enemies: gameState.enemies.map(e => toDebugEnemy(e, telegraphs)),
      player: toDebugPlayer(gameState),
      telegraphs: telegraphs.map(toDebugTelegraph),
      lastDamage: lastDamageRef.current ? { ...lastDamageRef.current } : null,
    };
  }, [gameState, telegraphs, toDebugEnemy, toDebugPlayer, toDebugTelegraph]);

  // Get enemies
  const getDebugEnemies = useCallback((): DebugEnemy[] => {
    return gameState.enemies.map(e => toDebugEnemy(e, telegraphs));
  }, [gameState.enemies, telegraphs, toDebugEnemy]);

  // Get player
  const getDebugPlayer = useCallback((): DebugPlayer => {
    return toDebugPlayer(gameState);
  }, [gameState, toDebugPlayer]);

  // Get last damage
  const getLastDamage = useCallback((): DebugDamageEvent | null => {
    return lastDamageRef.current ? { ...lastDamageRef.current } : null;
  }, []);

  // Get telegraphs
  const getDebugTelegraphs = useCallback((): DebugTelegraph[] => {
    return telegraphs.map(toDebugTelegraph);
  }, [telegraphs, toDebugTelegraph]);

  // Get THE BALL state (Run 036: Signature mechanic)
  const getDebugBallState = useCallback(() => {
    if (!ballState) return null;
    return {
      phase: ballState.phase,
      phaseProgress: ballState.phaseProgress,
      center: { ...ballState.center },
      currentRadius: ballState.currentRadius,
      gapAngle: ballState.gapAngle * (180 / Math.PI), // Convert to degrees for readability
      gapSize: ballState.gapSize * (180 / Math.PI),   // Convert to degrees
      temperature: ballState.temperature,
      beesInFormation: ballState.formationBeeIds.length,
      escapeCount: ballState.escapeCount,
    };
  }, [ballState]);

  // Get emotional state (Part VI: Arc Grammar)
  const getDebugEmotionalState = useCallback((): DebugEmotionalState | null => {
    if (!emotionalState) return null;

    // Extract active dimensions from the Map (dimensions where either pole visited)
    const activeDimensions: string[] = [];
    emotionalState.contrast.dimensions.forEach((dim, name) => {
      if (dim.visitedA || dim.visitedB) {
        activeDimensions.push(name);
      }
    });

    // Extract contrast history from transitions
    const contrastHistory = emotionalState.contrast.transitionHistory.map(
      (t) => `${t.dimension}: ${t.from} -> ${t.to}`
    );

    // Get last contrast time from most recent transition
    const lastContrastTime = emotionalState.contrast.transitionHistory.length > 0
      ? emotionalState.contrast.transitionHistory[emotionalState.contrast.transitionHistory.length - 1].gameTime
      : 0;

    return {
      arc: {
        currentPhase: emotionalState.arc.currentPhase,
        phasesVisited: [...emotionalState.arc.phasesVisited],
        phaseStartTime: emotionalState.arc.phaseStartTime,
        closureType: emotionalState.arc.closureType,
      },
      contrast: {
        activeDimensions,
        contrastsVisited: emotionalState.contrast.contrastsVisited,
        contrastHistory,
        lastContrastTime,
      },
      currentVoiceLine: emotionalState.voiceLines.lastShown
        ? { text: emotionalState.voiceLines.lastShown.text, type: emotionalState.voiceLines.lastShown.trigger }
        : null,
      voiceLineHistory: emotionalState.voiceLines.queue.map((l: VoiceLine) => l.text),
    };
  }, [emotionalState]);

  // Spawn enemy
  const debugSpawn = useCallback((type: string, position: { x: number; y: number }) => {
    // Bee enemy types: worker, scout, guard, propolis, royal
    const validTypes: EnemyType[] = ['worker', 'scout', 'guard', 'propolis', 'royal'];
    const enemyType = validTypes.includes(type as EnemyType)
      ? (type as EnemyType)
      : 'worker';  // Default to worker (basic bee)
    onSpawnEnemy(enemyType, { x: position.x, y: position.y });
  }, [onSpawnEnemy]);

  // Set invincible
  const debugSetInvincible = useCallback((invincible: boolean) => {
    invincibleRef.current = invincible;
    onSetInvincible(invincible);
  }, [onSetInvincible]);

  // Register/unregister debug functions on window
  useEffect(() => {
    if (!isDebugMode) return;

    // Expose debug functions on window
    window.DEBUG_GET_GAME_STATE = getDebugGameState;
    window.DEBUG_GET_ENEMIES = getDebugEnemies;
    window.DEBUG_GET_PLAYER = getDebugPlayer;
    window.DEBUG_GET_LAST_DAMAGE = getLastDamage;
    window.DEBUG_GET_TELEGRAPHS = getDebugTelegraphs;
    window.DEBUG_SPAWN = debugSpawn;
    window.DEBUG_SET_INVINCIBLE = debugSetInvincible;
    window.DEBUG_SKIP_WAVE = onSkipWave;
    window.DEBUG_KILL_ALL_ENEMIES = onKillAllEnemies;
    window.DEBUG_LEVEL_UP = onLevelUp;

    // Audio debug functions (since Playwright can't "hear")
    window.DEBUG_GET_AUDIO_STATE = DEBUG_GET_AUDIO_STATE;
    window.DEBUG_GET_AUDIO_LEVEL = DEBUG_GET_AUDIO_LEVEL;
    window.DEBUG_GET_AUDIO_LOG = DEBUG_GET_AUDIO_LOG;
    window.DEBUG_CLEAR_AUDIO_LOG = DEBUG_CLEAR_AUDIO_LOG;

    // Emotional/Contrast debug functions (Part VI: Arc Grammar)
    window.DEBUG_GET_EMOTIONAL_STATE = getDebugEmotionalState;

    // THE BALL debug functions (Run 036: Signature mechanic)
    window.DEBUG_GET_BALL_STATE = getDebugBallState;
    if (onForceBall) {
      window.DEBUG_FORCE_BALL = onForceBall;
    }

    // Log debug mode activation
    console.log('[DEBUG API] Debug mode activated. Available functions:');
    console.log('  - DEBUG_GET_GAME_STATE()');
    console.log('  - DEBUG_GET_ENEMIES()');
    console.log('  - DEBUG_GET_PLAYER()');
    console.log('  - DEBUG_GET_LAST_DAMAGE()');
    console.log('  - DEBUG_GET_TELEGRAPHS()');
    console.log('  - DEBUG_SPAWN(type, {x, y})');
    console.log('  - DEBUG_SET_INVINCIBLE(bool)');
    console.log('  - DEBUG_SKIP_WAVE()');
    console.log('  - DEBUG_KILL_ALL_ENEMIES()');
    console.log('  - DEBUG_LEVEL_UP()');
    console.log('  Audio debugging:');
    console.log('  - DEBUG_GET_AUDIO_STATE()');
    console.log('  - DEBUG_GET_AUDIO_LEVEL()');
    console.log('  - DEBUG_GET_AUDIO_LOG()');
    console.log('  - DEBUG_CLEAR_AUDIO_LOG()');
    console.log('  Emotional/Contrast debugging:');
    console.log('  - DEBUG_GET_EMOTIONAL_STATE()');
    console.log('  THE BALL debugging:');
    console.log('  - DEBUG_GET_BALL_STATE()');
    console.log('  - DEBUG_FORCE_BALL() - Force THE BALL to start forming');

    // Cleanup on unmount
    return () => {
      delete window.DEBUG_GET_GAME_STATE;
      delete window.DEBUG_GET_ENEMIES;
      delete window.DEBUG_GET_PLAYER;
      delete window.DEBUG_GET_LAST_DAMAGE;
      delete window.DEBUG_GET_TELEGRAPHS;
      delete window.DEBUG_SPAWN;
      delete window.DEBUG_SET_INVINCIBLE;
      delete window.DEBUG_SKIP_WAVE;
      delete window.DEBUG_KILL_ALL_ENEMIES;
      delete window.DEBUG_LEVEL_UP;
      // Audio debug functions
      delete window.DEBUG_GET_AUDIO_STATE;
      delete window.DEBUG_GET_AUDIO_LEVEL;
      delete window.DEBUG_GET_AUDIO_LOG;
      delete window.DEBUG_CLEAR_AUDIO_LOG;
      // Emotional/Contrast debug functions
      delete window.DEBUG_GET_EMOTIONAL_STATE;
      // THE BALL debug functions
      delete window.DEBUG_GET_BALL_STATE;
      delete window.DEBUG_FORCE_BALL;
    };
  }, [
    isDebugMode,
    getDebugGameState,
    getDebugEnemies,
    getDebugPlayer,
    getLastDamage,
    getDebugTelegraphs,
    getDebugEmotionalState,
    getDebugBallState,
    debugSpawn,
    debugSetInvincible,
    onSkipWave,
    onKillAllEnemies,
    onLevelUp,
    onForceBall,
  ]);

  return {
    isDebugMode,
    lastDamage: lastDamageRef.current,
    recordDamage,
  };
}

export default useDebugAPI;
