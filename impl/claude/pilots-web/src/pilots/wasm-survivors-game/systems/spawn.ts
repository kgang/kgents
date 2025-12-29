/**
 * Hornet Siege - Spawn System (Bee Colony)
 *
 * Handles bee spawning with wave-based difficulty progression.
 * Aligned to PROTO_SPEC S6 (Bee Taxonomy).
 * Budget: < 1ms per frame
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 */

import type { Enemy, EnemyType, Vector2, CoordinationState } from '../types';
import { COLORS, ARENA_WIDTH, ARENA_HEIGHT } from '../types';

// =============================================================================
// Bee Colony Configuration
// =============================================================================

// Wave configuration (per PROTO_SPEC Appendix F)
// TUNED: Faster spawns so THE BALL can actually form!
const WAVE_DURATION = 30000; // 30 seconds per wave
const SPAWN_INTERVAL_MIN = 200; // minimum spawn interval (was 300 - now faster!)

// Bee colors from types.ts COLORS constant
// Exported for use in rendering and tests
// Note: Uses BeeType (not full EnemyType) since we only spawn bees
export const BEE_COLORS: Record<import('../types').BeeType, string> = {
  worker: COLORS.worker,     // #F4D03F - Yellow swarmers
  scout: COLORS.scout,       // #F39C12 - Orange alerters
  guard: COLORS.guard,       // #E74C3C - Red defenders
  propolis: COLORS.propolis, // #9B59B6 - Purple sticky
  royal: COLORS.royal,       // #3498DB - Blue elite
};

// =============================================================================
// Types
// =============================================================================

export interface SpawnResult {
  state: GameState;
  waveComplete: boolean;
  newEnemies: Enemy[];
}

// GameState stub for this module (to avoid circular imports)
interface GameState {
  status: string;
  wave: number;
  waveTimer: number;
  gameTime: number;
  enemies: Enemy[];
  waveEnemiesRemaining?: number;
}

interface WaveConfig {
  baseEnemies: number;
  spawnRate: number; // spawns per second
  enemyTypes: { type: EnemyType; weight: number }[];
  royalWave: boolean; // Was "bossWave" - now uses bee terminology
}

// =============================================================================
// Wave Configuration
// =============================================================================

/**
 * Get configuration for a specific wave
 * Per PROTO_SPEC Appendix F: Enemy Introduction
 *
 * Wave 1: Workers only (learn basics)
 * Wave 3: Scouts (coordination preview)
 * Wave 5: Guards (tanky, prioritization)
 * Wave 7: Propolis (ranged, dodging)
 * Wave 9+: Royal Guards + THE BALL
 */
function getWaveConfig(wave: number): WaveConfig {
  // Every 5 waves from wave 9 is a royal wave
  const isRoyalWave = wave >= 9 && wave % 5 === 4;

  // TUNED: Higher base enemy count so THE BALL can form
  // Was: 5 + wave * 3, capped at 25
  // Now: 8 + wave * 3, capped at 30 (more bees = more likely to form BALL)
  const baseEnemies = Math.min(8 + wave * 3, 30);

  // TUNED: Faster spawn rate so bees accumulate
  // Was: 1 + wave * 0.15, capped at 4
  // Now: 1.5 + wave * 0.2, capped at 5 (faster spawning!)
  const spawnRate = Math.min(1.5 + wave * 0.2, 5);

  // Bee type distribution evolves per PROTO_SPEC S6
  const enemyTypes: { type: EnemyType; weight: number }[] = [];

  // Wave 1+: Workers always present (basic swarmers)
  enemyTypes.push({ type: 'worker', weight: Math.max(60 - wave * 5, 25) });

  // Wave 3+: Scouts appear (fast, trigger alarm pheromones)
  if (wave >= 3) {
    enemyTypes.push({ type: 'scout', weight: Math.min((wave - 2) * 5, 25) });
  }

  // Wave 5+: Guards appear (tanky, block player)
  if (wave >= 5) {
    enemyTypes.push({ type: 'guard', weight: Math.min((wave - 4) * 4, 20) });
  }

  // Wave 7+: Propolis appear (ranged, slows player with sticky attacks)
  if (wave >= 7) {
    enemyTypes.push({ type: 'propolis', weight: Math.min((wave - 6) * 3, 15) });
  }

  // Wave 9+: Royal Guards on royal waves (elite, complex patterns)
  if (isRoyalWave) {
    enemyTypes.push({ type: 'royal', weight: 10 });
  }

  return {
    baseEnemies,
    spawnRate,
    enemyTypes,
    royalWave: isRoyalWave,
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

  return 'worker';
}

// =============================================================================
// Enemy Factory
// =============================================================================

/**
 * Create a bee enemy of the specified type
 * Per PROTO_SPEC S6 (Bee Taxonomy)
 */
function createEnemy(type: EnemyType, position: Vector2, wave: number): Enemy {
  const baseStats = getBeeBaseStats(type);

  // Scale with wave (colony gets stronger over time)
  const healthMultiplier = 1 + wave * 0.1;
  const damageMultiplier = 1 + wave * 0.05;

  return {
    id: `bee-${type}-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    type,
    position,
    velocity: { x: 0, y: 0 },
    radius: baseStats.radius,
    health: Math.floor(baseStats.health * healthMultiplier),
    maxHealth: Math.floor(baseStats.health * healthMultiplier),
    damage: Math.floor(baseStats.damage * damageMultiplier),
    speed: baseStats.speed,
    xpValue: baseStats.xpValue,
    survivalTime: 0,
    coordinationState: 'idle' as CoordinationState,
  };
}

/**
 * Get base stats for bee type
 * Per PROTO_SPEC S6 (Bee Taxonomy)
 */
function getBeeBaseStats(type: EnemyType): {
  health: number;
  damage: number;
  radius: number;
  speed: number;
  xpValue: number;
} {
  // TUNED: Slightly higher HP so bees survive long enough to form THE BALL
  switch (type) {
    case 'worker':
      // Swarms toward player, basic kiting enemy
      // HP: 15 -> 22 (survives an extra hit)
      return { health: 22, damage: 8, radius: 10, speed: 80, xpValue: 10 };
    case 'scout':
      // Fast, alerts others via pheromones, priority target
      // HP: 10 -> 15 (still fragile but not instant-kill)
      return { health: 15, damage: 5, radius: 8, speed: 120, xpValue: 15 };
    case 'guard':
      // Slow, high HP, blocks player movement
      // HP: 60 -> 80 (tankier, creates obstacles)
      return { health: 80, damage: 15, radius: 18, speed: 40, xpValue: 25 };
    case 'propolis':
      // Ranged sticky attacks, slows player
      // HP: 20 -> 30 (survives to do its job)
      return { health: 30, damage: 10, radius: 12, speed: 50, xpValue: 20 };
    case 'royal':
      // Elite queen's guard, complex patterns, THE BALL anchor
      // HP: 200 -> 250 (proper miniboss)
      return { health: 250, damage: 25, radius: 30, speed: 60, xpValue: 100 };
    default:
      return { health: 22, damage: 8, radius: 10, speed: 80, xpValue: 10 };
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
