/**
 * Hornet Siege - Spawn System (Bee Colony)
 *
 * Handles bee spawning with wave-based difficulty progression.
 * Aligned to PROTO_SPEC S6 (Bee Taxonomy).
 * Budget: < 1ms per frame
 *
 * Wave Phases:
 * - Phase 1 (W1-2): LEARNING - Workers only, gentle introduction
 * - Phase 2 (W3-4): SCOUTS EMERGE - Scouts appear, first coordinated attacks possible
 * - Phase 3 (W5-6): ESCALATION - Guards join, scouts become more numerous
 * - Phase 4 (W7-8): FULL SWARM - Propolis adds ranged threat, exponential scaling
 * - Phase 5 (W9+): ENDGAME - Royal guards, THE BALL, maximum chaos
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md
 * @see systems/scouts/ for scout coordination system
 */

import type { Enemy, EnemyType, Vector2, CoordinationState } from '../types';
import { COLORS, ARENA_WIDTH, ARENA_HEIGHT } from '../types';

// =============================================================================
// Bee Colony Configuration
// =============================================================================

// Wave timing
const WAVE_DURATION = 35000; // 35 seconds per wave (slightly longer for scout coordination drama)
const SPAWN_INTERVAL_MIN = 180; // Minimum spawn interval (faster base rate)
const SPAWN_INTERVAL_MAX = 800; // Maximum spawn interval (prevents too-slow early waves)

// Scout burst spawning - enables coordinated attacks
const SCOUT_BURST_CHANCE = 0.15; // 15% chance of burst spawn
const SCOUT_BURST_COUNT = 3;     // Spawn 3 scouts at once for coordination

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
 * WAVE BALANCE PHILOSOPHY:
 * - Early waves: Teach mechanics, build confidence
 * - Mid waves: Introduce variety, first pressure
 * - Late waves: Full chaos, test mastery
 *
 * SCOUT COORDINATION SUPPORT:
 * - Wave 3+: Scouts appear with chance of burst spawns
 * - Wave 4+: Scout weight increases significantly (coordinated attacks shine)
 * - Burst spawns create instant coordination opportunities
 */
function getWaveConfig(wave: number): WaveConfig {
  // Every 5 waves from wave 9 is a royal wave
  const isRoyalWave = wave >= 9 && wave % 5 === 4;

  // ==========================================================================
  // Base Enemy Count - Smooth progression with distinct phases
  // ==========================================================================
  let baseEnemies: number;

  if (wave <= 2) {
    // Phase 1: LEARNING - Low count, predictable
    // W1: 10, W2: 14
    baseEnemies = 6 + wave * 4;
  } else if (wave <= 4) {
    // Phase 2: SCOUTS EMERGE - Moderate increase, scouts add variety
    // W3: 18, W4: 22
    baseEnemies = 10 + wave * 3;
  } else if (wave <= 6) {
    // Phase 3: ESCALATION - Guards join, pressure increases
    // W5: 28, W6: 34
    baseEnemies = 13 + wave * 3.5;
  } else if (wave <= 8) {
    // Phase 4: FULL SWARM - Exponential growth begins
    // W7: 45, W8: 58
    const exponentialBase = 18 + wave * 4;
    const multiplier = 1 + (wave - 6) * 0.25; // 1.25x at W7, 1.5x at W8
    baseEnemies = Math.floor(exponentialBase * multiplier);
  } else {
    // Phase 5: ENDGAME - Controlled chaos
    // W9: 72, W10: 86, W11: 100, W12: 115...
    // Slower growth than before to prevent unplayable late waves
    const baseGrowth = 50 + (wave - 9) * 14;
    const softCap = 150; // Soft cap to keep things playable
    baseEnemies = Math.min(baseGrowth, softCap);
  }

  // Royal waves get extra enemies for the spectacle
  if (isRoyalWave) {
    baseEnemies = Math.floor(baseEnemies * 1.2);
  }

  // ==========================================================================
  // Spawn Rate - How fast enemies enter the arena
  // ==========================================================================
  let spawnRate: number;

  if (wave <= 2) {
    // Slow and steady - player learns
    spawnRate = 1.0 + wave * 0.3; // 1.3 - 1.6
  } else if (wave <= 4) {
    // Picks up - scouts add urgency
    spawnRate = 1.8 + (wave - 2) * 0.4; // 2.2 - 2.6
  } else if (wave <= 6) {
    // Rapid - swarm feeling
    spawnRate = 2.8 + (wave - 4) * 0.5; // 3.3 - 3.8
  } else {
    // Maximum pressure
    spawnRate = Math.min(4.0 + (wave - 6) * 0.3, 6.0); // 4.3 - 6.0 (capped)
  }

  // ==========================================================================
  // Enemy Type Distribution - The heart of wave variety
  // ==========================================================================
  const enemyTypes: { type: EnemyType; weight: number }[] = [];

  // WORKERS - Always present, backbone of the swarm
  // Higher weight early, decreases as specialists appear
  let workerWeight: number;
  if (wave <= 2) {
    workerWeight = 100; // Pure workers initially
  } else if (wave <= 4) {
    workerWeight = 70 - (wave - 2) * 10; // 60 -> 50
  } else if (wave <= 6) {
    workerWeight = 45 - (wave - 4) * 5; // 40 -> 35
  } else {
    workerWeight = Math.max(30 - (wave - 6) * 2, 20); // 28 -> 20 (floor)
  }
  enemyTypes.push({ type: 'worker', weight: workerWeight });

  // SCOUTS - Wave 3+ (enables new coordination system!)
  // Higher weight at W4+ to enable coordinated attacks (need 3+ for encircle)
  if (wave >= 3) {
    let scoutWeight: number;
    if (wave <= 4) {
      // Introduction phase - some scouts, occasional coordination
      scoutWeight = 15 + (wave - 2) * 10; // 25 -> 35
    } else if (wave <= 6) {
      // Prime coordination phase - lots of scouts
      scoutWeight = 40 + (wave - 4) * 5; // 45 -> 50
    } else {
      // Late game - scouts remain threatening
      scoutWeight = Math.min(50 + (wave - 6) * 3, 60); // 53 -> 60 (capped)
    }
    enemyTypes.push({ type: 'scout', weight: scoutWeight });
  }

  // GUARDS - Wave 5+ (tanky blockers)
  if (wave >= 5) {
    const guardWeight = Math.min(10 + (wave - 4) * 5, 30); // 15 -> 30 (capped)
    enemyTypes.push({ type: 'guard', weight: guardWeight });
  }

  // PROPOLIS - Wave 7+ (ranged sticky attacks)
  if (wave >= 7) {
    const propolisWeight = Math.min(8 + (wave - 6) * 4, 25); // 12 -> 25 (capped)
    enemyTypes.push({ type: 'propolis', weight: propolisWeight });
  }

  // ROYAL GUARDS - Royal waves only (elite minibosses)
  if (isRoyalWave) {
    enemyTypes.push({ type: 'royal', weight: 8 }); // Low weight but impactful
  }

  return {
    baseEnemies: Math.floor(baseEnemies),
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

  // Royal Guards get a protective shield (requires 2 hits to kill)
  // Shield absorbs the first lethal hit, leaving them at 1 HP
  const shield = type === 'royal' ? 1 : 0;

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
    shield,
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
  // XP: +50% boost for faster early leveling
  switch (type) {
    case 'worker':
      // Swarms toward player, basic kiting enemy
      // HP: 15 -> 22 (survives an extra hit)
      return { health: 22, damage: 8, radius: 10, speed: 80, xpValue: 15 };  // +50% XP
    case 'scout':
      // Fast, alerts others via pheromones, priority target
      // HP: 10 -> 15 (still fragile but not instant-kill)
      return { health: 15, damage: 5, radius: 8, speed: 120, xpValue: 23 };  // +50% XP
    case 'guard':
      // Slow, high HP, blocks player movement
      // HP: 60 -> 80 (tankier, creates obstacles)
      // Speed: 40 -> 48 (+20% faster for more pressure)
      return { health: 80, damage: 15, radius: 18, speed: 48, xpValue: 38 };  // +50% XP
    case 'propolis':
      // Ranged sticky attacks, slows player
      // HP: 20 -> 30 (survives to do its job)
      return { health: 30, damage: 10, radius: 12, speed: 50, xpValue: 30 };  // +50% XP
    case 'royal':
      // Elite queen's guard, complex patterns, THE BALL anchor
      // HP: 200 -> 250 (proper miniboss)
      // Speed: 60 -> 75 (+25% faster for more pressure)
      return { health: 250, damage: 25, radius: 30, speed: 75, xpValue: 150 };  // +50% XP
    default:
      return { health: 22, damage: 8, radius: 10, speed: 80, xpValue: 15 };  // +50% XP
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
 *
 * Special behaviors:
 * - Scout burst spawns: W3+ has chance to spawn 3 scouts at once for coordination
 * - Adaptive pacing: Spawn rate adjusts based on current enemy count
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
  // Clamp between MIN and MAX for consistent pacing
  const baseInterval = 1000 / config.spawnRate;
  const spawnInterval = Math.max(
    SPAWN_INTERVAL_MIN,
    Math.min(baseInterval, SPAWN_INTERVAL_MAX)
  );

  // Adaptive pacing: spawn faster if few enemies on screen
  const enemyCount = state.enemies.length;
  const adaptiveMultiplier = enemyCount < 5 ? 0.6 : enemyCount < 10 ? 0.8 : 1.0;
  const effectiveInterval = spawnInterval * adaptiveMultiplier;

  // Update wave timer
  const newWaveTimer = state.waveTimer + deltaTime;

  // Check if it's time to spawn
  if (
    state.gameTime - lastSpawnTime >= effectiveInterval &&
    enemiesSpawnedThisWave < config.baseEnemies
  ) {
    // Determine what to spawn
    const enemyType = selectEnemyType(config);

    // SCOUT BURST SPAWN: Wave 3+, when spawning a scout, chance to spawn a group
    const shouldBurstSpawn =
      enemyType === 'scout' &&
      wave >= 3 &&
      Math.random() < SCOUT_BURST_CHANCE &&
      enemiesSpawnedThisWave + SCOUT_BURST_COUNT <= config.baseEnemies;

    if (shouldBurstSpawn) {
      // Spawn scouts in a cluster near each other for immediate coordination
      const centerPos = getSpawnPosition();
      const burstSpread = 40; // pixels apart

      for (let i = 0; i < SCOUT_BURST_COUNT; i++) {
        const offsetAngle = (i / SCOUT_BURST_COUNT) * Math.PI * 2;
        const offsetX = Math.cos(offsetAngle) * burstSpread;
        const offsetY = Math.sin(offsetAngle) * burstSpread;

        const position = {
          x: centerPos.x + offsetX,
          y: centerPos.y + offsetY,
        };

        const enemy = createEnemy('scout', position, wave);
        newEnemies.push(enemy);
        enemiesSpawnedThisWave++;
      }
    } else {
      // Normal single spawn
      const position = getSpawnPosition();
      const enemy = createEnemy(enemyType, position, wave);
      newEnemies.push(enemy);
      enemiesSpawnedThisWave++;
    }

    lastSpawnTime = state.gameTime;
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
