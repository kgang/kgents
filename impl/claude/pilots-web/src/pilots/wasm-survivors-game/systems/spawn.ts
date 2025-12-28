/**
 * WASM Survivors - Spawn System
 *
 * Handles enemy spawning with wave-based difficulty progression.
 * Budget: < 1ms per frame
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import type { GameState, Enemy, EnemyType, Vector2 } from '@kgents/shared-primitives';
import { ARENA_WIDTH, ARENA_HEIGHT } from './physics';

// =============================================================================
// Constants
// =============================================================================

// Wave configuration
const WAVE_DURATION = 30000; // 30 seconds per wave
const SPAWN_INTERVAL_MIN = 300; // minimum spawn interval

// Color palette from design docs
// DD-24: Added spitter with distinct purple color
const ENEMY_COLORS: Record<EnemyType, string> = {
  basic: '#FF3366', // Corrupted Red (Shambler)
  fast: '#FF6699', // Lighter red for fast (Rusher)
  tank: '#CC2952', // Darker red for tank
  boss: '#FF0044', // Bright red for boss
  spitter: '#AA44FF', // Purple for ranged (DD-24)
  colossal_tide: '#880000', // Deep crimson for THE TIDE (DD-030-4)
};

// =============================================================================
// Types
// =============================================================================

export interface SpawnResult {
  state: GameState;
  waveComplete: boolean;
  newEnemies: Enemy[];
}

interface WaveConfig {
  baseEnemies: number;
  spawnRate: number; // spawns per second
  enemyTypes: { type: EnemyType; weight: number }[];
  bossWave: boolean;
}

// =============================================================================
// Wave Configuration
// =============================================================================

/**
 * Get configuration for a specific wave
 */
function getWaveConfig(wave: number): WaveConfig {
  // Every 5 waves is a boss wave
  const isBossWave = wave > 0 && wave % 5 === 0;

  // Base enemy count increases with wave
  const baseEnemies = 10 + wave * 5;

  // Spawn rate increases (more enemies per second)
  const spawnRate = Math.min(1 + wave * 0.2, 5); // caps at 5/sec

  // Enemy type distribution evolves
  const enemyTypes: { type: EnemyType; weight: number }[] = [];

  // Always have basic enemies
  enemyTypes.push({ type: 'basic', weight: Math.max(50 - wave * 5, 20) });

  // Fast enemies appear from wave 2
  if (wave >= 2) {
    enemyTypes.push({ type: 'fast', weight: Math.min(wave * 5, 30) });
  }

  // DD-24: Spitter enemies appear from wave 3
  if (wave >= 3) {
    enemyTypes.push({ type: 'spitter', weight: Math.min((wave - 2) * 3, 15) });
  }

  // Tank enemies appear from wave 4
  if (wave >= 4) {
    enemyTypes.push({ type: 'tank', weight: Math.min((wave - 3) * 5, 25) });
  }

  // Boss on boss waves
  if (isBossWave) {
    enemyTypes.push({ type: 'boss', weight: 10 });
  }

  return {
    baseEnemies,
    spawnRate,
    enemyTypes,
    bossWave: isBossWave,
  };
}

/**
 * Select enemy type based on wave config weights
 */
function selectEnemyType(config: WaveConfig): EnemyType {
  const totalWeight = config.enemyTypes.reduce((sum, e) => sum + e.weight, 0);
  let random = Math.random() * totalWeight;

  for (const { type, weight } of config.enemyTypes) {
    random -= weight;
    if (random <= 0) return type;
  }

  return 'basic';
}

// =============================================================================
// Enemy Factory
// =============================================================================

/**
 * Create an enemy of the specified type
 * DD-030: Now initializes metamorphosis fields (survivalTime, pulsingState)
 */
function createEnemy(type: EnemyType, position: Vector2, wave: number): Enemy {
  const baseStats = getEnemyBaseStats(type);

  // Scale with wave
  const healthMultiplier = 1 + wave * 0.1;
  const damageMultiplier = 1 + wave * 0.05;

  return {
    id: `enemy-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    type,
    position,
    velocity: { x: 0, y: 0 },
    radius: baseStats.radius,
    health: Math.floor(baseStats.health * healthMultiplier),
    maxHealth: Math.floor(baseStats.health * healthMultiplier),
    damage: Math.floor(baseStats.damage * damageMultiplier),
    xpValue: baseStats.xpValue,
    color: ENEMY_COLORS[type],
    // DD-030: Metamorphosis fields
    survivalTime: 0,
    pulsingState: 'normal',
  };
}

/**
 * Get base stats for enemy type
 */
function getEnemyBaseStats(type: EnemyType): {
  health: number;
  damage: number;
  radius: number;
  xpValue: number;
} {
  switch (type) {
    case 'basic':
      return { health: 20, damage: 10, radius: 12, xpValue: 10 };
    case 'fast':
      return { health: 10, damage: 8, radius: 8, xpValue: 15 };
    case 'spitter':  // DD-24: Spitter stats
      return { health: 15, damage: 15, radius: 10, xpValue: 20 };
    case 'tank':
      return { health: 80, damage: 20, radius: 20, xpValue: 30 };
    case 'boss':
      return { health: 300, damage: 30, radius: 35, xpValue: 100 };
    case 'colossal_tide':  // DD-030-4: THE TIDE stats (created via metamorphosis, not spawn)
      return { health: 100, damage: 25, radius: 36, xpValue: 200 };
    default:
      return { health: 20, damage: 10, radius: 12, xpValue: 10 };
  }
}

/**
 * Get random spawn position outside the arena (enemy enters from edges)
 */
function getSpawnPosition(): Vector2 {
  const edge = Math.floor(Math.random() * 4);
  const padding = 30;

  switch (edge) {
    case 0: // Top
      return { x: Math.random() * ARENA_WIDTH, y: -padding };
    case 1: // Right
      return { x: ARENA_WIDTH + padding, y: Math.random() * ARENA_HEIGHT };
    case 2: // Bottom
      return { x: Math.random() * ARENA_WIDTH, y: ARENA_HEIGHT + padding };
    case 3: // Left
      return { x: -padding, y: Math.random() * ARENA_HEIGHT };
    default:
      return { x: -padding, y: Math.random() * ARENA_HEIGHT };
  }
}

// =============================================================================
// Spawner State
// =============================================================================

// Track spawn timing (module-level for persistence)
let lastSpawnTime = 0;
let enemiesSpawnedThisWave = 0;

/**
 * Reset spawner state (call when starting new game)
 */
export function resetSpawner(): void {
  lastSpawnTime = 0;
  enemiesSpawnedThisWave = 0;
}

// =============================================================================
// Main Spawner Update
// =============================================================================

/**
 * Update spawner - handles wave progression and enemy spawning
 * Budget: < 1ms
 */
export function updateSpawner(state: GameState, deltaTime: number): SpawnResult {
  const newEnemies: Enemy[] = [];
  let waveComplete = false;

  // Don't spawn if not playing
  if (state.status !== 'playing') {
    return { state, waveComplete, newEnemies };
  }

  // Get current wave config
  const wave = state.wave;
  const config = getWaveConfig(wave);

  // Calculate spawn interval for this wave
  const spawnInterval = Math.max(
    1000 / config.spawnRate,
    SPAWN_INTERVAL_MIN
  );

  // Update wave timer
  const newWaveTimer = state.waveTimer + deltaTime;

  // Check if it's time to spawn
  if (
    state.gameTime - lastSpawnTime >= spawnInterval &&
    enemiesSpawnedThisWave < config.baseEnemies
  ) {
    // Spawn enemy
    const enemyType = selectEnemyType(config);
    const position = getSpawnPosition();
    const enemy = createEnemy(enemyType, position, wave);

    newEnemies.push(enemy);
    lastSpawnTime = state.gameTime;
    enemiesSpawnedThisWave++;
  }

  // Check for wave completion
  if (
    newWaveTimer >= WAVE_DURATION ||
    (enemiesSpawnedThisWave >= config.baseEnemies && state.enemies.length === 0)
  ) {
    // Wave complete! Advance to next wave
    waveComplete = true;
    enemiesSpawnedThisWave = 0;

    return {
      state: {
        ...state,
        wave: wave + 1,
        waveTimer: 0,
        waveEnemiesRemaining: getWaveConfig(wave + 1).baseEnemies,
        enemies: [...state.enemies, ...newEnemies],
      },
      waveComplete,
      newEnemies,
    };
  }

  // Update state with new enemies
  return {
    state: {
      ...state,
      waveTimer: newWaveTimer,
      waveEnemiesRemaining: config.baseEnemies - enemiesSpawnedThisWave,
      enemies: [...state.enemies, ...newEnemies],
    },
    waveComplete,
    newEnemies,
  };
}

/**
 * Start a new wave (call when game starts or manually advancing)
 */
export function startWave(state: GameState): GameState {
  const wave = state.wave > 0 ? state.wave : 1;
  const config = getWaveConfig(wave);

  resetSpawner();

  return {
    ...state,
    wave,
    waveTimer: 0,
    waveEnemiesRemaining: config.baseEnemies,
    status: 'playing',
  };
}
