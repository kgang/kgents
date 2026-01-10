/**
 * Scout Coordination System - Configuration
 *
 * All timing, damage, and geometry constants for scout behaviors.
 * Tuned for challenging but fair gameplay per PROTO_SPEC A1-A4.
 *
 * Key Design Goals:
 * - Solo scouts feel like annoying mosquitoes (fast, low damage, frequent)
 * - Coordinated scouts feel threatening and cinematic (synchronized, high-skill dodge)
 * - All attacks are telegraphed and dodgeable (A2: Attributable Outcomes)
 */

// =============================================================================
// Mode Detection
// =============================================================================

export const SCOUT_COORDINATION_CONFIG = {
  /** Distance to check for nearby scouts */
  coordinationRange: 150,

  /** Minimum scouts for coordinated attack (including self) */
  minScoutsForCoordination: 3,

  /** Maximum scouts in one coordinated group */
  maxCoordinatedScouts: 6,

  /** How often to re-evaluate mode (ms) */
  modeCheckInterval: 200,

  /** Mode must be stable this long before switching (ms) */
  modeStabilityTime: 500,

  /** After coordinated attack, scout can't join another for this long (ms) */
  coordinationCooldown: 4000,

  /** Global cooldown before any new coordinated attack (ms) */
  globalCoordinationCooldown: 5000,
} as const;

// =============================================================================
// Solo Sting Attack (Fast & Annoying)
// =============================================================================

export const SOLO_STING_CONFIG = {
  // === Timing (faster than normal scout) ===
  /** Very brief warning - just a "twitch" (ms) */
  telegraphDuration: 120,

  /** Lightning fast dash (ms) */
  attackDuration: 60,

  /** Quick retreat after hit (ms) */
  retreatDuration: 250,

  /** Vulnerable recovery window (ms) */
  recoveryDuration: 350,

  // === Movement ===
  /** Distance covered during sting dash (px) */
  attackDistance: 70,

  /** How far to back off after attack (px) */
  retreatDistance: 50,

  /** Speed during retreat (px/s) */
  retreatSpeed: 180,

  // === Orbiting ===
  /** Distance to maintain while circling (px) */
  orbitDistanceMin: 55,
  orbitDistanceMax: 75,

  /** Angular velocity for circling (rad/s) */
  orbitSpeed: 2.2,

  /** Target angle relative to player facing - behind but visible (rad) */
  preferredFlankAngle: 2.5,         // ~143 degrees

  /** How close to target angle before committing (rad) */
  angleCommitThreshold: 0.35,       // ~20 degrees

  /** Max time to orbit before forced commit (ms) */
  maxFlankingDuration: 2500,

  /** Min time to orbit before can commit (ms) */
  minFlankingDuration: 600,

  // === Attack Timing ===
  /** Minimum time between solo attacks (ms) */
  attackIntervalMin: 700,

  /** Maximum time between solo attacks (ms) */
  attackIntervalMax: 1300,

  /** Random jitter added to telegraph timing (ms) */
  timingJitter: 80,

  // === Combat ===
  /** Damage per solo sting (lower than normal, but frequent) */
  damage: 4,

  /** Pheromone emission during attack (marks player) */
  pheromoneEmission: 0.35,

  /** Hit radius for sting attack (px) */
  hitRadius: 18,

  // === Visual ===
  /** Number of positions to keep in orbit trail */
  trailLength: 6,

  colors: {
    orbit: '#F39C12',               // Orange trail
    telegraph: '#FF3333',           // Pure red warning (danger, distinct from player)
    strike: '#FF3333',              // Pure red impact
  },
} as const;

// =============================================================================
// Coordinated Arc Attack (3+ scouts)
// =============================================================================

export const COORDINATED_ARC_CONFIG = {
  // === Gathering Phase ===
  /** Time for scouts to get into position (ms) */
  gatheringDuration: 1800,

  /** Movement speed during gathering (px/s) - slower for drama */
  gatheringSpeed: 55,

  // === Telegraph Phase ===
  /** Clear warning before attack (ms) */
  telegraphDuration: 700,

  /** Pulse rate for warning effect (ms) */
  telegraphPulseRate: 140,

  // === Attack Phase ===
  /** Delay between each scout's attack (ms) - creates "wave" feel */
  attackWaveDelay: 140,

  /** Duration of each scout's dash (ms) */
  attackDuration: 180,

  /** Overshoot - scouts go past player center (multiplier) */
  attackOvershoot: 1.25,

  // === Recovery ===
  /** Recovery after coordinated attack (ms) - longer than solo */
  recoveryDuration: 900,

  /** Scatter speed during dispersal (px/s) */
  scatterSpeed: 45,

  // === Geometry ===
  /** Distance from player when surrounding (px) */
  formationRadius: 110,

  /** How close to target position counts as "in position" (px) */
  positioningTolerance: 12,

  /** Max time to get into position before timeout (ms) */
  positioningTimeout: 3500,

  /** Time to hold in synchronized position before signal (ms) */
  synchronizedHoldTime: 1000,

  /** Random angle jitter for natural feel (rad) */
  angleJitter: Math.PI / 10,        // +/- 18 degrees

  // === Combat ===
  /** Damage per scout in coordinated attack */
  damagePerScout: 5,

  /** Hit radius for arc attack (px) */
  hitRadius: 20,

  /** Whether coordinated attacks apply marking debuff */
  appliesMarkingDebuff: true,

  /** Duration of marking debuff (ms) */
  markingDuration: 2500,

  /** Damage bonus other bees get vs marked player */
  markingDamageBonus: 0.15,         // +15%

  // === Visual ===
  colors: {
    gathering: '#F39C12',           // Orange indicator
    synchronized: '#FF8800',        // Brighter when ready
    telegraph: '#FF3333',           // Pure red warning (danger)
    attackLine: '#FF3333',          // Pure red attack arrows (danger)
    connection: '#F8A100',          // Lines between scouts
  },
} as const;

// =============================================================================
// Wave Scaling (makes scouts more aggressive in later waves)
// =============================================================================

export const SCOUT_WAVE_SCALING = {
  /** Wave at which scaling starts */
  scalingStartWave: 4,

  /** Telegraph duration reduction per wave above start (ms) */
  telegraphReductionPerWave: 8,

  /** Minimum telegraph duration (floor) (ms) */
  minTelegraphDuration: 80,

  /** Attack interval reduction per wave (ms) */
  intervalReductionPerWave: 40,

  /** Minimum attack interval (floor) (ms) */
  minAttackInterval: 400,

  /** Coordination threshold reduction per wave (fewer scouts needed) */
  coordinationThresholdReduction: 0,  // Keep at 3 for now

  /** Damage increase per wave (flat) */
  damageIncreasePerWave: 0.5,
} as const;

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get wave-scaled solo sting config
 */
export function getScaledSoloConfig(wave: number) {
  const scalingWaves = Math.max(0, wave - SCOUT_WAVE_SCALING.scalingStartWave);

  return {
    telegraphDuration: Math.max(
      SCOUT_WAVE_SCALING.minTelegraphDuration,
      SOLO_STING_CONFIG.telegraphDuration - scalingWaves * SCOUT_WAVE_SCALING.telegraphReductionPerWave
    ),
    attackIntervalMin: Math.max(
      SCOUT_WAVE_SCALING.minAttackInterval,
      SOLO_STING_CONFIG.attackIntervalMin - scalingWaves * SCOUT_WAVE_SCALING.intervalReductionPerWave
    ),
    attackIntervalMax: Math.max(
      SCOUT_WAVE_SCALING.minAttackInterval + 300,
      SOLO_STING_CONFIG.attackIntervalMax - scalingWaves * SCOUT_WAVE_SCALING.intervalReductionPerWave
    ),
    damage: SOLO_STING_CONFIG.damage + scalingWaves * SCOUT_WAVE_SCALING.damageIncreasePerWave,
  };
}

/**
 * Get wave-scaled coordinated config
 */
export function getScaledCoordinatedConfig(wave: number) {
  const scalingWaves = Math.max(0, wave - SCOUT_WAVE_SCALING.scalingStartWave);

  return {
    telegraphDuration: Math.max(
      500, // Minimum 500ms for coordinated (must be readable)
      COORDINATED_ARC_CONFIG.telegraphDuration - scalingWaves * 15
    ),
    attackWaveDelay: Math.max(
      100,
      COORDINATED_ARC_CONFIG.attackWaveDelay - scalingWaves * 8
    ),
    damagePerScout: COORDINATED_ARC_CONFIG.damagePerScout + scalingWaves * 0.3,
  };
}
