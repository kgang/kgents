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
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import { useEffect, useRef, useCallback } from 'react';
import type { GameState, Enemy, EnemyType, Vector2 } from '@kgents/shared-primitives';
import type {
  DebugEnemy,
  DebugPlayer,
  DebugDamageEvent,
  DebugTelegraph,
  DebugGameState,
} from '../../../lib/debug-types';
import type { TelegraphData } from '../systems/enemies';

// =============================================================================
// Types
// =============================================================================

export interface DebugAPIConfig {
  gameState: GameState;
  telegraphs: TelegraphData[];
  onSpawnEnemy: (type: EnemyType, position: Vector2) => void;
  onSetInvincible: (invincible: boolean) => void;
  onSkipWave: () => void;
  onKillAllEnemies: () => void;
  onLevelUp: () => void;
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
    onSpawnEnemy,
    onSetInvincible,
    onSkipWave,
    onKillAllEnemies,
    onLevelUp,
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
      pulsingState: enemy.pulsingState,     // DD-030: Lifecycle state
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
    // Map telegraph type to attack type
    const attackType = telegraph.type === 'aim' ? 'projectile' as const : telegraph.type;
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

  // Spawn enemy
  const debugSpawn = useCallback((type: string, position: { x: number; y: number }) => {
    const validTypes: EnemyType[] = ['basic', 'fast', 'tank', 'boss', 'spitter', 'colossal_tide'];
    const enemyType = validTypes.includes(type as EnemyType)
      ? (type as EnemyType)
      : 'basic';
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
    };
  }, [
    isDebugMode,
    getDebugGameState,
    getDebugEnemies,
    getDebugPlayer,
    getLastDamage,
    getDebugTelegraphs,
    debugSpawn,
    debugSetInvincible,
    onSkipWave,
    onKillAllEnemies,
    onLevelUp,
  ]);

  return {
    isDebugMode,
    lastDamage: lastDamageRef.current,
    recordDamage,
  };
}

export default useDebugAPI;
