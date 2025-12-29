/**
 * WASM Survivors - Juice System
 *
 * Handles game feel: particles, screen shake, escalation engine, SOUND.
 * This is the core of "fun floor" (DD-5).
 *
 * Components:
 * - ParticleEmitter: death bursts, XP trails, damage flashes
 * - ScreenShake: impact feedback, crisis moments
 * - EscalationEngine: juice scales with wave/combo/stakes
 * - SoundEngine: audio feedback for all actions (DD-5)
 *
 * @see pilots/wasm-survivors-game/.outline.md
 */

import type { GameState, EnemyType, Vector2, Enemy } from '../types';
import { getSoundEngine } from './sound';

// =============================================================================
// APPENDIX E: JUICE PARAMETERS (from PROTO_SPEC) - COPY-PASTED VALUES
// =============================================================================

/**
 * Screen Shake Parameters
 * "Make kills feel like PUNCHES"
 */
export const SHAKE = {
  workerKill:  { amplitude: 2,  duration: 80,  frequency: 60 },
  guardKill:   { amplitude: 5,  duration: 150, frequency: 60 },
  bossKill:    { amplitude: 14, duration: 300, frequency: 60 },
  playerHit:   { amplitude: 8,  duration: 200, frequency: 60 },
  multiKill:   { amplitude: 6,  duration: 120, frequency: 60 },  // 3+ kills
  massacre:    { amplitude: 15, duration: 350, frequency: 60 },  // 5+ kills
} as const;

/**
 * Freeze Frame Parameters
 * "Create 'time slows when you're badass' moments"
 */
export const FREEZE = {
  significantKill: 2,   // frames (33ms at 60fps) - guard/tank kills
  multiKill:       4,   // frames (66ms) - 3+ simultaneous kills
  criticalHit:     3,   // frames - execute or critical damage
  massacre:        6,   // frames (100ms) - 5+ kills = DRAMATIC PAUSE
} as const;

/**
 * Particle System Parameters
 * "25 particles, longer trails, brighter colors"
 */
export const PARTICLES = {
  deathSpiral: {
    count: 25,           // NOT 5, TWENTY-FIVE
    color: '#FFE066',    // soft yellow pollen
    spread: 45,          // degrees
    lifespan: 400,       // ms
    rotation: 3,         // full rotations during descent
  },
  honeyDrip: {
    count: 15,
    color: '#F4A300',    // amber
    gravity: 200,        // px/s^2
    poolFade: 1200,      // ms - how long the pool lingers
  },
  damageFlash: {
    colors: ['#FF6600', '#FF0000'],  // orange -> red
    flashDuration: 100,
    fadeDuration: 200,
    fragmentCount: 10,
    fragmentVelocity: 225,  // px/s
  },
} as const;

/**
 * Visual Tell Parameters
 * "Every attack is telegraphed"
 */
export const TELLS = {
  chargingGlow: {
    color: '#FFD700',    // gold
    duration: 500,       // ms pre-attack
    pulseScale: 1.2,     // max scale
    pulseRate: 100,      // ms per pulse
    opacity: [0.4, 0.8], // min -> max
  },
  formationLines: {
    color: '#FFD700',
    opacity: 0.4,
    width: 1.5,          // px
    fadeTime: 150,       // ms
    minBees: 3,          // show only when coordinated
  },
  stingerTrail: {
    color: '#6B2D5B',    // venom purple
    duration: 300,       // ms linger
  },
} as const;

/**
 * Audio Cue Parameters
 * "ASMR-level satisfaction"
 */
export const AUDIO_CUES = {
  alarmPheromone: {
    freqStart: 400,      // Hz
    freqEnd: 2000,       // Hz
    duration: 300,       // ms
  },
  ballForming: {
    buzzVolume: 0.3,     // starts quiet
    buzzPeak: 1.0,       // crescendo
    silenceDuration: 3000,  // ms of dread
  },
} as const;

/**
 * Apex Strike Parameters
 * "HORNET'S SIGNATURE MOVE - Lock, strike, destroy"
 */
export const APEX_STRIKE = {
  // Lock phase (0.12s) - hovering menace
  lock: {
    wingBlur: {
      count: 8,            // Segments in blur disc
      color: '#4A6B8C',    // Wing Blue
      radius: 25,          // Disc radius
      opacity: 0.6,
      rotationSpeed: 20,   // Full rotations per second
    },
    windDust: {
      count: 6,
      color: '#FFFFFFAA',  // White semi-transparent
      spread: 20,
      lifespan: 200,       // ms
      velocity: 40,        // Slow swirl
    },
    vignette: {
      intensity: 0.15,     // Subtle screen darkening
      fadeInTime: 60,      // ms to reach full
    },
    chargingGlow: {
      colorStart: '#FF8C00', // Strike Orange
      colorEnd: '#FF3300',   // Threat Red
      pulseRate: 80,         // ms per pulse
    },
  },

  // Strike phase (0.15s) - VIOLENCE
  strike: {
    trail: {
      color: '#6B2D5B',    // Venom Purple
      length: 60,
      width: 4,
      fadeTime: 100,       // ms
    },
    speedLines: {
      count: 6,
      color: '#FFFFFF',
      length: 40,
      spread: 15,          // Degrees from direction
      lifespan: 80,        // Very quick
    },
    airDisplacement: {
      count: 10,
      color: '#FFFFFF40',  // Very faint
      spread: 60,          // Degrees perpendicular to strike
      velocity: 200,
    },
  },

  // Hit effects - IMPACT
  hit: {
    burstCount: 20,
    burstColor: '#FF6600',    // Impact orange
    burstVelocity: 300,       // Fast burst
    flashDuration: 50,        // ms
    flashColor: '#FFFFFF',
    chainGlowColor: '#FFD700', // Gold for chain ready
    chainGlowRadius: 30,
  },

  // Miss effects - punishment
  miss: {
    tumbleCount: 8,
    tumbleColor: '#888888',
    tumbleSpread: 360,        // Scattered in all directions
    whiffTrailColor: '#6B2D5B40',  // Faded venom
    whiffTrailLength: 40,
    recoveryWobbleIntensity: 3,
  },

  // Bloodlust visual scaling
  bloodlust: {
    auraThreshold: 80,        // Show aura at 80+
    auraColor: '#FF000080',   // Red semi-transparent
    auraRadius: 35,
    maxTrailIntensity: 2.0,   // At 100 bloodlust
    maxParticleScale: 1.5,    // At 100 bloodlust
    furyThreshold: 100,       // APEX FURY mode
    furyColor: '#FFD700',     // Golden
  },
} as const;

/**
 * Graze System Parameters
 * "RISK-TAKING REWARDED - Near-miss = sparks + chain bonus"
 */
export const GRAZE_JUICE = {
  spark: {
    count: 8,            // Small burst, not overwhelming
    color: '#00FFFF',    // Cyan spark
    spread: 180,         // Half-circle degrees
    lifespan: 200,       // Quick flash ms
    size: 3,             // Small sparks
    velocity: 120,       // Fast outward burst
  },
  chain: {
    textColor: '#00FFFF',
    textSize: 14,
    textDuration: 600,   // Float up duration ms
  },
  bonus: {
    ringColor: '#00FFFF',
    ringRadius: 40,
    ringDuration: 400,   // ms
    textDuration: 1000,
  },
} as const;

// =============================================================================
// Color Palette (from design docs)
// =============================================================================

export const COLORS = {
  // =================================================================
  // PLAYER (HORNET) - "Ukiyo-e meets arcade brutalism"
  // The hornet emerges from shadow. Orange breaks through darkness.
  // =================================================================
  player: '#CC5500', // Burnt Amber - main body mass, commands attention
  playerHighlight: '#FF8C00', // Strike Orange - upper edges, attack frames
  playerShadow: '#662200', // Dried Blood - underside, depth carving
  playerStripe: '#1A1A1A', // Venom Black - stripes, legs, antennae
  playerEyes: '#FFE066', // Pollen Gold - 2x2 pixels max, unblinking
  playerMandible: '#FF3300', // Threat Red - only during attack
  playerWing: '#4A6B8C', // Wing Blue - semi-transparent blur

  // =================================================================
  // BEE ENEMIES - Warm palette, sympathetic but expendable
  // Workers blur into swarm; elites get hierarchy colors
  // =================================================================
  enemy: '#D4920A', // Worker Amber - default bee (slightly muted)
  worker: '#D4920A', // Worker Amber - expendable, swarm density
  scout: '#E5B84A', // Faded Honey - leaner, paler, flies too long
  guard: '#B87A0A', // Hardened Amber - darker, denser, armor plate
  propolis: '#A08020', // Resin Gold - sticky, green undertone
  royal: '#6B2D5B', // Royal Purple - SACRED (edge only, 2-4 pixels)

  // =================================================================
  // FEEDBACK - Clear visual language
  // =================================================================
  xp: '#FFD700', // Warning Yellow - bright XP pickups
  health: '#00FF88', // Vitality Green - healing/health
  ghost: '#A0A0B0', // Warm Gray - death/ghost state
  crisis: '#FF6B00', // Hornet Orange - danger/warning

  // =================================================================
  // EFFECTS - Death should feel VISCERAL
  // =================================================================
  pollenYellow: '#FFE066', // Pollen Gold - death spiral particles
  honeyAmber: '#F4A300', // Honey Amber - honey drip effect
  venomPurple: '#6B2D5B', // Royal Purple - stinger trail
  nectarGlow: '#FFF3C4', // Nectar Glow - soft backlight
  shadowComb: '#3D2914', // Shadow Comb - deep shadows
  propolisDark: '#2A1F14', // Propolis Dark - borders, near-black
};

// =============================================================================
// Metamorphosis Colors (DD-30: Colossal Transformation)
// =============================================================================

export const METAMORPHOSIS_COLORS = {
  pulsing: { start: '#FF6B00', end: '#FF0000' },  // Orange to red
  threads: '#FF00FF',  // Magenta
  colossal: '#880000',  // Deep crimson
  linked: '#FF666680',  // Semi-transparent red for linked enemies
};

// Pulsing state for metamorphosis (extends Enemy with optional field)
export type MetamorphosisPulsingState = 'normal' | 'pulsing' | 'seeking' | 'combining';

// Extended enemy type with metamorphosis fields (used at runtime)
export interface MetamorphosisEnemy extends Enemy {
  pulsingState?: MetamorphosisPulsingState;
  metamorphosisTimer?: number;  // Time in current pulsing state
  seekingTarget?: Vector2;      // Position of enemy being sought
}

// =============================================================================
// Types
// =============================================================================

export interface Particle {
  id: string;
  position: Vector2;
  velocity: Vector2;
  color: string;
  size: number;
  lifetime: number;
  maxLifetime: number;
  alpha: number;
  type: 'burst' | 'trail' | 'text' | 'ring' | 'spiral' | 'drip' | 'pool' | 'fragment' | 'graze_spark'
      | 'apex_wing_blur' | 'apex_wind_dust' | 'apex_speed_line' | 'apex_air' | 'apex_impact' | 'apex_tumble' | 'apex_fury_text';
  text?: string;
  // Death spiral specific
  rotation?: number;        // Current rotation in radians
  rotationSpeed?: number;   // Radians per second
  // Drip/pool specific
  gravity?: number;         // Applied gravity
  isPool?: boolean;         // True if this is a static pool
  // Apex strike specific
  angle?: number;           // Direction angle for directional effects
  startPosition?: Vector2;  // For trail effects
}

export interface ShakeState {
  intensity: number;
  duration: number;
  elapsed: number;
  offset: Vector2;
}

export interface EscalationState {
  wave: number;
  combo: number;
  comboTimer: number;
  healthFraction: number;
  multiplier: number;
}

// DD-16: Clutch Moment State
export interface ClutchState {
  active: boolean;
  level: 'full' | 'medium' | 'critical' | null;
  timeScale: number;
  zoom: number;
  remaining: number;
  duration: number;
}

/**
 * Freeze Frame State
 * "Time slows when you're badass"
 */
export interface FreezeState {
  active: boolean;
  framesRemaining: number;
  type: 'significant' | 'multi' | 'critical' | 'massacre' | null;
}

/**
 * Kill tracking for multi-kill detection
 */
export interface KillTracker {
  recentKills: number;      // Kills in the current window
  windowStart: number;      // When the window started
  windowDuration: number;   // How long the window lasts (ms)
  lastKillTime: number;     // When the last kill occurred
}

/**
 * Apex Strike State
 * Tracks the visual state of the hornet's signature attack
 */
export interface ApexStrikeState {
  phase: 'none' | 'lock' | 'strike' | 'recovery';
  lockProgress: number;     // 0-1 during lock phase
  strikeProgress: number;   // 0-1 during strike phase
  direction: Vector2;       // Strike direction (normalized)
  bloodlust: number;        // 0-100 bloodlust meter
  chainAvailable: boolean;  // Can chain after hit
  startPosition: Vector2;   // Where lock began
  targetPosition: Vector2;  // Strike target
}

export interface JuiceSystem {
  particles: Particle[];
  shake: ShakeState;
  escalation: EscalationState;
  clutch: ClutchState; // DD-16: Clutch moment state
  freeze: FreezeState; // NEW: Freeze frame state
  killTracker: KillTracker; // NEW: Multi-kill tracking
  apexStrike: ApexStrikeState; // Apex Strike visual state

  // Methods
  emitKill: (position: Vector2, enemyType: EnemyType) => void;
  emitDamage: (position: Vector2, amount: number) => void;
  emitLevelUp: (level: number) => void;
  emitWaveComplete: (wave: number) => void;
  emitXPCollect: (position: Vector2, amount: number) => void;
  triggerShake: (intensity: number, duration: number) => void;
  updateCombo: () => void;
  // DD-12: Vampiric heal effect
  emitHeal?: (position: Vector2, amount: number) => void;
  // DD-16: Trigger clutch moment
  triggerClutch: (level: 'full' | 'medium' | 'critical', durationMs: number) => void;
  // DD-30: Metamorphosis effect
  emitMetamorphosis: (position: Vector2, isFirst: boolean) => void;
  // NEW: Trigger freeze frame
  triggerFreeze: (type: FreezeState['type']) => void;
  // NEW: Death spiral particle burst (the INCREDIBLE death animation)
  emitDeathSpiral: (position: Vector2) => void;
  // NEW: Honey drip effect
  emitHoneyDrip: (position: Vector2) => void;
  // NEW: Damage flash fragments
  emitDamageFlash: (position: Vector2) => void;
  // Graze system - "RISK-TAKING REWARDED"
  emitGrazeSpark: (playerPos: Vector2, enemyPos: Vector2, chainCount: number) => void;
  emitGrazeBonus: (position: Vector2) => void;

  // =================================================================
  // APEX STRIKE SYSTEM - "HORNET'S SIGNATURE MOVE"
  // =================================================================

  // Lock phase - hovering menace
  emitApexLock: (position: Vector2) => void;
  updateApexLock: (position: Vector2, progress: number) => void;

  // Strike phase - VIOLENCE
  emitApexStrikeStart: (position: Vector2, direction: Vector2, bloodlust: number) => void;
  emitApexStrikeTrail: (position: Vector2, direction: Vector2) => void;

  // Hit/Miss resolution
  emitApexHit: (position: Vector2, damage: number, chainAvailable: boolean) => void;
  emitApexMiss: (position: Vector2, direction: Vector2) => void;

  // Bloodlust max effect
  emitBloodlustMax: (position: Vector2) => void;
}

// =============================================================================
// Particle Factory
// =============================================================================

function createParticle(
  position: Vector2,
  type: Particle['type'],
  color: string,
  options: Partial<Particle> = {}
): Particle {
  const angle = Math.random() * Math.PI * 2;
  const speed = 50 + Math.random() * 100;

  return {
    id: `particle-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: {
      x: Math.cos(angle) * speed,
      y: Math.sin(angle) * speed,
    },
    color,
    size: 4,
    lifetime: 500,
    maxLifetime: 500,
    alpha: 1,
    type,
    ...options,
  };
}

function createBurstParticles(
  position: Vector2,
  color: string,
  count: number,
  intensity: number = 1
): Particle[] {
  const particles: Particle[] = [];

  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.3;
    const speed = (100 + Math.random() * 150) * intensity;

    particles.push({
      id: `particle-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: {
        x: Math.cos(angle) * speed,
        y: Math.sin(angle) * speed,
      },
      color,
      size: 3 + Math.random() * 4 * intensity,
      lifetime: 300 + Math.random() * 200,
      maxLifetime: 300 + Math.random() * 200,
      alpha: 1,
      type: 'burst',
    });
  }

  return particles;
}

function createTextParticle(
  position: Vector2,
  text: string,
  color: string
): Particle {
  return {
    id: `text-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: -80 }, // Float upward
    color,
    size: 16,
    lifetime: 800,
    maxLifetime: 800,
    alpha: 1,
    type: 'text',
    text,
  };
}

function createRingParticle(
  position: Vector2,
  color: string,
  maxSize: number
): Particle {
  return {
    id: `ring-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color,
    size: 0,
    lifetime: 400,
    maxLifetime: 400,
    alpha: 0.8,
    type: 'ring',
    text: maxSize.toString(), // Store max size in text field (hack but works)
  };
}

// =============================================================================
// NEW: INCREDIBLE Death Animation Particles
// =============================================================================

/**
 * Create death spiral particles
 * "25 particles, 3 rotations during 0.6s descent, WOULD SOMEONE CLIP THIS?"
 */
function createDeathSpiralParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  const config = PARTICLES.deathSpiral;

  for (let i = 0; i < config.count; i++) {
    // Distribute particles in a spread around the death point
    const spreadAngle = ((Math.random() - 0.5) * 2 * config.spread * Math.PI) / 180;
    const baseAngle = (Math.PI * 2 * i) / config.count;
    const angle = baseAngle + spreadAngle;

    // Initial outward velocity, then spiral down
    const outwardSpeed = 80 + Math.random() * 60;
    const upwardBurst = -150 - Math.random() * 100; // Burst UP first

    particles.push({
      id: `spiral-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: {
        x: Math.cos(angle) * outwardSpeed,
        y: upwardBurst, // Shoot UP, gravity brings down
      },
      color: config.color,
      size: 4 + Math.random() * 4, // Vary size for visual interest
      lifetime: config.lifespan,
      maxLifetime: config.lifespan,
      alpha: 1,
      type: 'spiral',
      // Rotation: 3 full rotations over lifespan
      rotation: Math.random() * Math.PI * 2,
      rotationSpeed: (config.rotation * Math.PI * 2) / (config.lifespan / 1000),
      gravity: 400 + Math.random() * 100, // Heavier gravity for dramatic fall
    });
  }

  return particles;
}

/**
 * Create honey drip particles
 * "Amber honey that pools on the ground - VISCERAL"
 */
function createHoneyDripParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  const config = PARTICLES.honeyDrip;

  for (let i = 0; i < config.count; i++) {
    // Slight horizontal spread
    const angle = Math.random() * Math.PI * 2;
    const spreadSpeed = 20 + Math.random() * 30;

    particles.push({
      id: `drip-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: {
        x: Math.cos(angle) * spreadSpeed,
        y: -50 - Math.random() * 30, // Small upward burst
      },
      color: config.color,
      size: 3 + Math.random() * 3,
      lifetime: 800, // Drip phase
      maxLifetime: 800,
      alpha: 0.9,
      type: 'drip',
      gravity: config.gravity,
    });
  }

  return particles;
}

/**
 * Create a honey pool (static, fading)
 */
function createHoneyPool(position: Vector2): Particle {
  const config = PARTICLES.honeyDrip;
  return {
    id: `pool-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color: config.color,
    size: 8 + Math.random() * 6, // Vary pool size
    lifetime: config.poolFade,
    maxLifetime: config.poolFade,
    alpha: 0.7,
    type: 'pool',
    isPool: true,
  };
}

/**
 * Create damage flash fragment particles
 * "Orange -> Red fragments that make damage FEEL impactful"
 */
function createDamageFlashParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  const config = PARTICLES.damageFlash;

  for (let i = 0; i < config.fragmentCount; i++) {
    const angle = (Math.PI * 2 * i) / config.fragmentCount + Math.random() * 0.5;
    const speed = config.fragmentVelocity * (0.7 + Math.random() * 0.6);

    // Alternate between orange and red
    const color = config.colors[i % 2];

    particles.push({
      id: `frag-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: {
        x: Math.cos(angle) * speed,
        y: Math.sin(angle) * speed,
      },
      color,
      size: 5 + Math.random() * 4,
      lifetime: config.flashDuration + config.fadeDuration,
      maxLifetime: config.flashDuration + config.fadeDuration,
      alpha: 1,
      type: 'fragment',
    });
  }

  return particles;
}

/**
 * Create graze spark particles
 * "RISK-TAKING REWARDED - cyan sparks on near-miss"
 * Sparks burst away from the enemy direction
 */
function createGrazeSparkParticles(playerPos: Vector2, enemyPos: Vector2): Particle[] {
  const particles: Particle[] = [];
  const config = GRAZE_JUICE.spark;

  // Calculate direction from enemy to player (sparks go away from enemy)
  const dx = playerPos.x - enemyPos.x;
  const dy = playerPos.y - enemyPos.y;
  const baseAngle = Math.atan2(dy, dx);

  // Sparks in a half-circle facing away from enemy
  const spreadRad = (config.spread * Math.PI) / 180;

  for (let i = 0; i < config.count; i++) {
    // Distribute across the spread arc
    const angleOffset = (i / (config.count - 1) - 0.5) * spreadRad;
    const angle = baseAngle + angleOffset + (Math.random() - 0.5) * 0.3;
    const speed = config.velocity * (0.8 + Math.random() * 0.4);

    particles.push({
      id: `graze-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...playerPos },
      velocity: {
        x: Math.cos(angle) * speed,
        y: Math.sin(angle) * speed,
      },
      color: config.color,
      size: config.size + Math.random() * 2,
      lifetime: config.lifespan,
      maxLifetime: config.lifespan,
      alpha: 1,
      type: 'graze_spark',
    });
  }

  return particles;
}

// =============================================================================
// NEW: Apex Strike Particle Factory Functions
// =============================================================================

/**
 * Create wind dust particles for Apex Lock phase
 * "Small particles swirling beneath player" - helicopter downdraft effect
 */
function createApexWindDustParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  const config = APEX_STRIKE.lock.windDust;

  for (let i = 0; i < config.count; i++) {
    // Swirl in a circle around the position
    const angle = (Math.PI * 2 * i) / config.count + Math.random() * 0.5;
    const distance = config.spread * (0.5 + Math.random() * 0.5);

    particles.push({
      id: `apex-wind-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: {
        x: position.x + Math.cos(angle) * distance,
        y: position.y + 15 + Math.random() * 10, // Below player
      },
      velocity: {
        x: Math.cos(angle + Math.PI / 2) * config.velocity, // Perpendicular = swirl
        y: Math.random() * 20 - 10, // Slight vertical drift
      },
      color: config.color,
      size: 2 + Math.random() * 2,
      lifetime: config.lifespan,
      maxLifetime: config.lifespan,
      alpha: 0.6,
      type: 'apex_wind_dust',
    });
  }

  return particles;
}

/**
 * Create speed lines for Apex Strike phase
 * "Directional lines showing velocity" - manga speed effect
 */
function createApexSpeedLineParticles(position: Vector2, direction: Vector2): Particle[] {
  const particles: Particle[] = [];
  const config = APEX_STRIKE.strike.speedLines;

  const baseAngle = Math.atan2(direction.y, direction.x);
  const spreadRad = (config.spread * Math.PI) / 180;

  for (let i = 0; i < config.count; i++) {
    // Distribute around the strike direction
    const angleOffset = (i / (config.count - 1) - 0.5) * spreadRad * 2;
    const angle = baseAngle + Math.PI + angleOffset; // Opposite direction (trailing)

    // Start position is offset from player in strike direction
    const startOffset = 10 + Math.random() * 10;
    const perpOffset = (Math.random() - 0.5) * 20;

    particles.push({
      id: `apex-speed-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: {
        x: position.x + Math.cos(baseAngle) * startOffset + Math.cos(baseAngle + Math.PI / 2) * perpOffset,
        y: position.y + Math.sin(baseAngle) * startOffset + Math.sin(baseAngle + Math.PI / 2) * perpOffset,
      },
      velocity: {
        x: Math.cos(angle) * 300, // Fast trailing
        y: Math.sin(angle) * 300,
      },
      color: config.color,
      size: config.length, // Length is stored in size for rendering
      lifetime: config.lifespan,
      maxLifetime: config.lifespan,
      alpha: 0.8,
      type: 'apex_speed_line',
      angle: angle, // Store angle for line rendering
    });
  }

  return particles;
}

/**
 * Create air displacement particles for Apex Strike
 * "Particles pushed aside" - supersonic displacement effect
 */
function createApexAirDisplacementParticles(position: Vector2, direction: Vector2): Particle[] {
  const particles: Particle[] = [];
  const config = APEX_STRIKE.strike.airDisplacement;

  const baseAngle = Math.atan2(direction.y, direction.x);
  const spreadRad = (config.spread * Math.PI) / 180;

  for (let i = 0; i < config.count; i++) {
    // Particles push out perpendicular to strike direction
    const side = i < config.count / 2 ? 1 : -1;
    const perpAngle = baseAngle + (Math.PI / 2) * side;
    const angleVariation = (Math.random() - 0.5) * spreadRad;

    particles.push({
      id: `apex-air-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: {
        x: Math.cos(perpAngle + angleVariation) * config.velocity,
        y: Math.sin(perpAngle + angleVariation) * config.velocity,
      },
      color: config.color,
      size: 3 + Math.random() * 3,
      lifetime: 150,
      maxLifetime: 150,
      alpha: 0.4,
      type: 'apex_air',
    });
  }

  return particles;
}

/**
 * Create impact burst particles for Apex Hit
 * "Big particle burst at hit location" - SATISFYING hit feedback
 */
function createApexImpactParticles(position: Vector2, bloodlust: number): Particle[] {
  const particles: Particle[] = [];
  const config = APEX_STRIKE.hit;

  // Scale particle count and velocity with bloodlust
  const bloodlustScale = 1 + (bloodlust / 100) * (APEX_STRIKE.bloodlust.maxParticleScale - 1);
  const count = Math.floor(config.burstCount * bloodlustScale);

  for (let i = 0; i < count; i++) {
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.3;
    const speed = config.burstVelocity * (0.7 + Math.random() * 0.6) * bloodlustScale;

    // Mix in gold particles at high bloodlust
    let color: string = config.burstColor;
    if (bloodlust >= APEX_STRIKE.bloodlust.furyThreshold && Math.random() < 0.3) {
      color = APEX_STRIKE.bloodlust.furyColor; // Golden particles
    }

    particles.push({
      id: `apex-impact-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: {
        x: Math.cos(angle) * speed,
        y: Math.sin(angle) * speed,
      },
      color,
      size: 4 + Math.random() * 4,
      lifetime: 200,
      maxLifetime: 200,
      alpha: 1,
      type: 'apex_impact',
    });
  }

  return particles;
}

/**
 * Create tumble particles for Apex Miss
 * "Off-balance scattered particles" - punishment feedback
 */
function createApexTumbleParticles(position: Vector2, direction: Vector2): Particle[] {
  const particles: Particle[] = [];
  const config = APEX_STRIKE.miss;

  // Use direction to bias tumble particles forward (overshoot effect)
  const baseAngle = Math.atan2(direction.y, direction.x);

  for (let i = 0; i < config.tumbleCount; i++) {
    // Scatter with bias toward strike direction (overshoot)
    const angle = baseAngle + (Math.random() - 0.5) * Math.PI * 1.5;
    const speed = 50 + Math.random() * 100;

    particles.push({
      id: `apex-tumble-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: {
        x: Math.cos(angle) * speed,
        y: Math.sin(angle) * speed,
      },
      color: config.tumbleColor,
      size: 3 + Math.random() * 3,
      lifetime: 300,
      maxLifetime: 300,
      alpha: 0.7,
      type: 'apex_tumble',
      gravity: 300, // Fall down sadly
    });
  }

  return particles;
}

/**
 * Create APEX FURY text particle
 * "APEX FURY text particle" - maximum bloodlust celebration
 */
function createApexFuryTextParticle(position: Vector2): Particle {
  return {
    id: `apex-fury-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { x: position.x, y: position.y - 40 },
    velocity: { x: 0, y: -60 },
    color: APEX_STRIKE.bloodlust.furyColor,
    size: 20, // Large text
    lifetime: 1200,
    maxLifetime: 1200,
    alpha: 1,
    type: 'apex_fury_text',
    text: 'APEX FURY',
  };
}

// =============================================================================
// Escalation Engine (S2)
// =============================================================================

/**
 * Calculate juice multiplier based on game state
 *
 * Formula from .outline.md:
 * juice_intensity = base_intensity * escalation_multiplier
 *
 * escalation_multiplier = wave_factor * combo_factor * stakes_factor
 * where:
 *   wave_factor = 1 + (wave / 10) * 0.5           // +5% per wave, caps at 150%
 *   combo_factor = 1 + log2(combo_count + 1) * 0.1 // logarithmic scaling
 *   stakes_factor = 1 + (1 - health_fraction) * 0.3 // more juice when low health
 */
function calculateEscalationMultiplier(escalation: EscalationState): number {
  const waveFactor = 1 + Math.min(escalation.wave / 10, 1) * 0.5;
  const comboFactor = 1 + Math.log2(escalation.combo + 1) * 0.1;
  const stakesFactor = 1 + (1 - escalation.healthFraction) * 0.3;

  return waveFactor * comboFactor * stakesFactor;
}

// =============================================================================
// Create Juice System
// =============================================================================

export function createJuiceSystem(): JuiceSystem {
  const state = {
    particles: [] as Particle[],
    shake: {
      intensity: 0,
      duration: 0,
      elapsed: 0,
      offset: { x: 0, y: 0 },
    },
    escalation: {
      wave: 1,
      combo: 0,
      comboTimer: 0,
      healthFraction: 1,
      multiplier: 1,
    },
    // DD-16: Clutch moment state
    clutch: {
      active: false,
      level: null as 'full' | 'medium' | 'critical' | null,
      timeScale: 1.0,
      zoom: 1.0,
      remaining: 0,
      duration: 0,
    },
    // NEW: Freeze frame state - "time slows when you're badass"
    freeze: {
      active: false,
      framesRemaining: 0,
      type: null as FreezeState['type'],
    },
    // NEW: Kill tracker for multi-kill detection
    killTracker: {
      recentKills: 0,
      windowStart: 0,
      windowDuration: 150, // 150ms window for multi-kills
      lastKillTime: 0,
    },
    // Apex Strike visual state
    apexStrike: {
      phase: 'none' as ApexStrikeState['phase'],
      lockProgress: 0,
      strikeProgress: 0,
      direction: { x: 1, y: 0 },
      bloodlust: 0,
      chainAvailable: false,
      startPosition: { x: 0, y: 0 },
      targetPosition: { x: 0, y: 0 },
    },
  };

  return {
    get particles() {
      return state.particles;
    },
    get shake() {
      return state.shake;
    },
    get escalation() {
      return state.escalation;
    },
    get clutch() {
      return state.clutch;
    },
    get freeze() {
      return state.freeze;
    },
    get killTracker() {
      return state.killTracker;
    },
    get apexStrike() {
      return state.apexStrike;
    },

    emitKill(position: Vector2, enemyType: EnemyType) {
      const now = Date.now();

      // Track multi-kills
      if (now - state.killTracker.windowStart > state.killTracker.windowDuration) {
        // New kill window
        state.killTracker.recentKills = 1;
        state.killTracker.windowStart = now;
      } else {
        state.killTracker.recentKills++;
      }
      state.killTracker.lastKillTime = now;

      // DD-5: Sound feedback - kill pop
      const sound = getSoundEngine();
      const pitchMap: Record<import('../types').BeeType, number> = {
        worker: 1.0,
        scout: 1.2,
        guard: 0.7,
        propolis: 1.1,
        royal: 0.5,
      };
      // Use bee-type pitch or default if legacy type
      const pitchBeeType = enemyType as import('../types').BeeType;
      const pitch = pitchMap[pitchBeeType] ?? 1.0;
      sound.play('kill', { pitch });

      // Update combo
      state.escalation.combo++;
      state.escalation.comboTimer = 2000; // 2 second combo window
      state.escalation.multiplier = calculateEscalationMultiplier(state.escalation);

      // =================================================================
      // TRANSFORMED: Use Appendix E SHAKE values - "Make kills feel like PUNCHES"
      // =================================================================
      type ShakeConfig = { readonly amplitude: number; readonly duration: number; readonly frequency: number };
      let shakeConfig: ShakeConfig = SHAKE.workerKill;
      if (enemyType === 'royal') {
        shakeConfig = SHAKE.bossKill;
      } else if (enemyType === 'guard') {
        shakeConfig = SHAKE.guardKill;
      }

      // Multi-kill shake escalation
      if (state.killTracker.recentKills >= 5) {
        shakeConfig = SHAKE.massacre;
      } else if (state.killTracker.recentKills >= 3) {
        shakeConfig = SHAKE.multiKill;
      }

      // Apply escalation multiplier to shake
      const finalAmplitude = shakeConfig.amplitude * state.escalation.multiplier;
      this.triggerShake(finalAmplitude, shakeConfig.duration);

      // =================================================================
      // TRANSFORMED: Freeze frames - "time slows when you're badass"
      // =================================================================
      if (state.killTracker.recentKills >= 5) {
        this.triggerFreeze('massacre');
        // MASSACRE SOUND - "DOPAMINE HIT"
        sound.play('massacre');
      } else if (state.killTracker.recentKills >= 3) {
        this.triggerFreeze('multi');
      } else if (enemyType === 'royal' || enemyType === 'guard') {
        this.triggerFreeze('significant');
      }

      // =================================================================
      // TRANSFORMED: Death spiral particles - "WOULD SOMEONE CLIP THIS?"
      // =================================================================
      // Add death spiral for EVERY kill - 25 particles spiraling down
      this.emitDeathSpiral(position);

      // Add honey drip for heavier enemies
      if (enemyType === 'royal' || enemyType === 'guard') {
        this.emitHoneyDrip(position);
      }

      // Particle count scales with escalation and enemy type
      const baseCount = enemyType === 'royal' ? 24 : enemyType === 'guard' ? 16 : 8;
      const count = Math.floor(baseCount * state.escalation.multiplier);

      // Burst particles
      const burstParticles = createBurstParticles(
        position,
        COLORS.enemy,
        count,
        state.escalation.multiplier
      );
      state.particles.push(...burstParticles);

      // XP text particle
      const xpValues: Record<import('../types').BeeType, number> = {
        worker: 10,
        scout: 15,
        guard: 30,
        propolis: 20,
        royal: 100,
      };
      // Use bee-type XP or default if legacy type
      const xpBeeType = enemyType as import('../types').BeeType;
      const xpValue = xpValues[xpBeeType] ?? 10;
      state.particles.push(
        createTextParticle(position, `+${xpValue}`, COLORS.xp)
      );
    },

    emitDamage(position: Vector2, amount: number) {
      // DD-5: Sound feedback - damage thump
      getSoundEngine().play('damage');

      // Reset combo on damage
      state.escalation.combo = 0;
      state.escalation.comboTimer = 0;

      // Damage text
      state.particles.push(
        createTextParticle(position, `-${amount}`, COLORS.crisis)
      );

      // =================================================================
      // TRANSFORMED: Use Appendix E SHAKE for player hit
      // =================================================================
      this.triggerShake(SHAKE.playerHit.amplitude, SHAKE.playerHit.duration);

      // =================================================================
      // TRANSFORMED: Damage flash fragments - "Make damage FEEL impactful"
      // =================================================================
      this.emitDamageFlash(position);

      // Old red flash particles (kept for layering)
      const flashParticles = createBurstParticles(position, COLORS.crisis, 6, 0.5);
      state.particles.push(...flashParticles);
    },

    emitLevelUp(level: number) {
      // DD-5: Sound feedback - level up arpeggio
      getSoundEngine().play('levelup');

      // Big celebration ring from center of screen
      const centerPos = { x: 400, y: 300 }; // Arena center

      state.particles.push(createRingParticle(centerPos, COLORS.xp, 300));
      state.particles.push(
        createTextParticle(
          { x: centerPos.x, y: centerPos.y - 50 },
          `LEVEL ${level}!`,
          COLORS.xp
        )
      );

      // Burst of golden particles
      const burstParticles = createBurstParticles(centerPos, COLORS.xp, 20, 1.5);
      state.particles.push(...burstParticles);

      // Screen shake
      this.triggerShake(6, 200);
    },

    emitWaveComplete(wave: number) {
      // DD-5: Sound feedback - wave horn
      getSoundEngine().play('wave');

      state.escalation.wave = wave;
      state.escalation.multiplier = calculateEscalationMultiplier(state.escalation);

      const centerPos = { x: 400, y: 300 };

      // Wave complete text
      state.particles.push(
        createTextParticle(centerPos, `WAVE ${wave} COMPLETE`, COLORS.health)
      );

      // Ring effect
      state.particles.push(createRingParticle(centerPos, COLORS.health, 250));

      // Screen shake
      this.triggerShake(4, 150);
    },

    emitXPCollect(position: Vector2, amount: number) {
      // Trail particle toward XP bar (top of screen)
      state.particles.push(
        createParticle(position, 'trail', COLORS.xp, {
          velocity: { x: 0, y: -200 },
          lifetime: 600,
          maxLifetime: 600,
          size: 6,
        })
      );

      // Small text
      if (amount >= 10) {
        state.particles.push(createTextParticle(position, `+${amount}`, COLORS.xp));
      }
    },

    triggerShake(intensity: number, duration: number) {
      // Only override if stronger shake
      if (intensity > state.shake.intensity) {
        state.shake.intensity = intensity;
        state.shake.duration = duration;
        state.shake.elapsed = 0;
      }
    },

    updateCombo() {
      // Called when combo timer expires
      if (state.escalation.combo > 0) {
        state.escalation.combo = 0;
        state.escalation.multiplier = calculateEscalationMultiplier(state.escalation);
      }
    },

    // DD-16: Trigger clutch moment
    triggerClutch(level: 'full' | 'medium' | 'critical', durationMs: number) {
      // Don't interrupt a more intense clutch moment
      const levelPriority = { full: 3, medium: 2, critical: 1 };
      const currentPriority = state.clutch.level ? levelPriority[state.clutch.level] : 0;
      const newPriority = levelPriority[level];

      if (newPriority <= currentPriority && state.clutch.active) {
        return; // Current clutch is more or equally intense
      }

      // Configure clutch based on level
      const configs = {
        full: { timeScale: 0.2, zoom: 1.3 },
        medium: { timeScale: 0.5, zoom: 1.2 },
        critical: { timeScale: 0.3, zoom: 1.0 },
      };

      const config = configs[level];
      state.clutch = {
        active: true,
        level,
        timeScale: config.timeScale,
        zoom: config.zoom,
        remaining: durationMs,
        duration: durationMs,
      };

      // Play bass drop for full/medium clutch
      if (level === 'full' || level === 'medium') {
        getSoundEngine().play('bassDrop');
      }

      // Play heartbeat for critical
      if (level === 'critical') {
        getSoundEngine().play('heartbeat');
      }
    },

    // DD-30: Metamorphosis combination effect
    emitMetamorphosis(position: Vector2, isFirst: boolean) {
      // Screen shake - stronger for first metamorphosis
      const shakeIntensity = isFirst ? 10 : 6;
      this.triggerShake(shakeIntensity, 300);

      // Play bass rumble (when sound engine supports it)
      const sound = getSoundEngine();
      if (isFirst) {
        sound.play('bassDrop');  // Dramatic for first
      }
      // TODO: Add 'bassRumble' sound type for subsequent

      // Create burst particles at combination point
      const burstCount = isFirst ? 30 : 20;
      const burstParticles = createBurstParticles(
        position,
        METAMORPHOSIS_COLORS.colossal,
        burstCount,
        isFirst ? 2.0 : 1.5  // Higher intensity for first
      );
      state.particles.push(...burstParticles);

      // Add magenta thread particles
      for (let i = 0; i < 8; i++) {
        const angle = (Math.PI * 2 * i) / 8;
        const speed = 150;
        state.particles.push({
          id: `meta-${Date.now()}-${i}`,
          position: { ...position },
          velocity: {
            x: Math.cos(angle) * speed,
            y: Math.sin(angle) * speed,
          },
          color: METAMORPHOSIS_COLORS.threads,
          size: 5,
          lifetime: 500,
          maxLifetime: 500,
          alpha: 0.8,
          type: 'trail',
        });
      }

      // Expanding ring
      state.particles.push(createRingParticle(position, METAMORPHOSIS_COLORS.colossal, 150));

      // Text indicator
      state.particles.push(
        createTextParticle(position, 'METAMORPHOSIS!', METAMORPHOSIS_COLORS.threads)
      );
    },

    // =================================================================
    // NEW: Freeze Frame System - "time slows when you're badass"
    // =================================================================
    triggerFreeze(type: FreezeState['type']) {
      if (!type) return;

      // Get frame count from FREEZE constants
      const frameCount = {
        significant: FREEZE.significantKill,
        multi: FREEZE.multiKill,
        critical: FREEZE.criticalHit,
        massacre: FREEZE.massacre,
      }[type];

      // Only override if more frames
      if (frameCount > state.freeze.framesRemaining) {
        state.freeze.active = true;
        state.freeze.framesRemaining = frameCount;
        state.freeze.type = type;
      }
    },

    // =================================================================
    // NEW: Death Spiral - "WOULD SOMEONE CLIP THIS?"
    // =================================================================
    emitDeathSpiral(position: Vector2) {
      const spiralParticles = createDeathSpiralParticles(position);
      state.particles.push(...spiralParticles);
    },

    // =================================================================
    // NEW: Honey Drip - "VISCERAL amber drips"
    // =================================================================
    emitHoneyDrip(position: Vector2) {
      const dripParticles = createHoneyDripParticles(position);
      state.particles.push(...dripParticles);

      // Create a pool at the landing point (delayed)
      setTimeout(() => {
        state.particles.push(createHoneyPool({
          x: position.x + (Math.random() - 0.5) * 30,
          y: position.y + 40 + Math.random() * 20,
        }));
      }, 800); // After drip phase
    },

    // =================================================================
    // NEW: Damage Flash - "Orange -> Red IMPACT"
    // =================================================================
    emitDamageFlash(position: Vector2) {
      const flashParticles = createDamageFlashParticles(position);
      state.particles.push(...flashParticles);
    },

    // =================================================================
    // Graze Spark - "RISK-TAKING REWARDED"
    // =================================================================
    emitGrazeSpark(playerPos: Vector2, enemyPos: Vector2, chainCount: number) {
      // Create spark particles bursting away from enemy
      const sparkParticles = createGrazeSparkParticles(playerPos, enemyPos);
      state.particles.push(...sparkParticles);

      // Add chain counter text above player
      if (chainCount > 1) {
        const chainConfig = GRAZE_JUICE.chain;
        state.particles.push({
          id: `graze-chain-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
          position: { x: playerPos.x, y: playerPos.y - 30 },
          velocity: { x: 0, y: -60 },
          color: chainConfig.textColor,
          size: chainConfig.textSize,
          lifetime: chainConfig.textDuration,
          maxLifetime: chainConfig.textDuration,
          alpha: 1,
          type: 'text',
          text: `GRAZE x${chainCount}`,
        });
      }

      // Play graze sound (if sound engine supports it)
      const sound = getSoundEngine();
      sound.play('graze', { pitch: 1.2 + chainCount * 0.05 });
    },

    // =================================================================
    // Graze Bonus - "+10% DAMAGE" ring effect
    // =================================================================
    emitGrazeBonus(position: Vector2) {
      const bonusConfig = GRAZE_JUICE.bonus;

      // Expanding cyan ring
      state.particles.push(createRingParticle(position, bonusConfig.ringColor, bonusConfig.ringRadius));

      // Bonus text
      state.particles.push({
        id: `graze-bonus-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        position: { x: position.x, y: position.y - 40 },
        velocity: { x: 0, y: -40 },
        color: bonusConfig.ringColor,
        size: 16,
        lifetime: bonusConfig.textDuration,
        maxLifetime: bonusConfig.textDuration,
        alpha: 1,
        type: 'text',
        text: '+10% DAMAGE',
      });

      // Play bonus trigger sound
      const sound = getSoundEngine();
      sound.play('graze', { pitch: 1.5, volume: 0.6 });
    },

    // =================================================================
    // APEX STRIKE SYSTEM - "HORNET'S SIGNATURE MOVE"
    // =================================================================

    /**
     * Emit initial Apex Lock effects
     * Called when player begins lock phase (0.12s)
     */
    emitApexLock(position: Vector2) {
      // Update state
      state.apexStrike.phase = 'lock';
      state.apexStrike.lockProgress = 0;
      state.apexStrike.startPosition = { ...position };

      // Initial wind dust particles (swirling beneath)
      const windParticles = createApexWindDustParticles(position);
      state.particles.push(...windParticles);

      // Play charging sound
      const sound = getSoundEngine();
      sound.play('charge', { pitch: 1.2 });
    },

    /**
     * Update Apex Lock effects as lock progresses
     * Called each frame during lock phase
     * @param position - Current player position
     * @param progress - 0-1 progress through lock phase
     */
    updateApexLock(position: Vector2, progress: number) {
      state.apexStrike.lockProgress = progress;

      // Emit more wind dust at intervals
      if (progress > 0.3 && progress < 0.95) {
        // Emit wind dust particles periodically
        if (Math.random() < 0.3) {
          const windParticles = createApexWindDustParticles(position);
          state.particles.push(...windParticles);
        }
      }

      // At high progress, emit charging ring
      if (progress > 0.8 && Math.random() < 0.2) {
        const config = APEX_STRIKE.lock.chargingGlow;
        state.particles.push(createRingParticle(position, config.colorEnd, 20));
      }
    },

    /**
     * Emit Apex Strike start effects
     * Called when strike phase begins (0.15s of VIOLENCE)
     */
    emitApexStrikeStart(position: Vector2, direction: Vector2, bloodlust: number) {
      // Update state
      state.apexStrike.phase = 'strike';
      state.apexStrike.strikeProgress = 0;
      state.apexStrike.direction = { ...direction };
      state.apexStrike.bloodlust = bloodlust;
      state.apexStrike.startPosition = { ...position };

      // Speed lines trailing behind
      const speedLines = createApexSpeedLineParticles(position, direction);
      state.particles.push(...speedLines);

      // Air displacement particles
      const airParticles = createApexAirDisplacementParticles(position, direction);
      state.particles.push(...airParticles);

      // Screen shake proportional to bloodlust
      const shakeIntensity = 4 + (bloodlust / 100) * 6;
      this.triggerShake(shakeIntensity, 80);

      // Freeze frame for dramatic effect at high bloodlust
      if (bloodlust >= 50) {
        this.triggerFreeze('critical');
      }

      // Play strike sound
      const sound = getSoundEngine();
      sound.play('swing', { pitch: 0.8, volume: 0.8 + (bloodlust / 100) * 0.2 });
    },

    /**
     * Emit ongoing Apex Strike trail effects
     * Called each frame during strike motion
     */
    emitApexStrikeTrail(position: Vector2, direction: Vector2) {
      state.apexStrike.strikeProgress += 0.1; // Approximate progress tracking

      // Emit trail particles at current position
      const config = APEX_STRIKE.strike.trail;
      const bloodlust = state.apexStrike.bloodlust;
      const trailIntensity = 1 + (bloodlust / 100) * (APEX_STRIKE.bloodlust.maxTrailIntensity - 1);

      // Create trail particle
      state.particles.push({
        id: `apex-trail-${Date.now()}-${Math.random().toString(36).slice(2, 5)}`,
        position: { ...position },
        velocity: { x: 0, y: 0 }, // Static trail
        color: config.color,
        size: config.width * trailIntensity,
        lifetime: config.fadeTime,
        maxLifetime: config.fadeTime,
        alpha: 0.8,
        type: 'trail',
        startPosition: { ...state.apexStrike.startPosition },
      });

      // Emit additional speed lines periodically
      if (Math.random() < 0.4) {
        const speedLines = createApexSpeedLineParticles(position, direction);
        state.particles.push(...speedLines);
      }
    },

    /**
     * Emit Apex Hit effects
     * Called when strike connects with enemy
     */
    emitApexHit(position: Vector2, damage: number, chainAvailable: boolean) {
      const bloodlust = state.apexStrike.bloodlust;

      // Update state
      state.apexStrike.phase = 'recovery';
      state.apexStrike.chainAvailable = chainAvailable;

      // Impact burst particles - SATISFYING
      const impactParticles = createApexImpactParticles(position, bloodlust);
      state.particles.push(...impactParticles);

      // Brief white flash (mandible flash)
      const config = APEX_STRIKE.hit;
      state.particles.push({
        id: `apex-flash-${Date.now()}`,
        position: { ...position },
        velocity: { x: 0, y: 0 },
        color: config.flashColor,
        size: 30,
        lifetime: config.flashDuration,
        maxLifetime: config.flashDuration,
        alpha: 0.9,
        type: 'ring',
        text: '30', // Max size for ring
      });

      // Damage text
      state.particles.push(createTextParticle(position, `${damage}`, COLORS.crisis));

      // Chain ready glow if available
      if (chainAvailable) {
        state.particles.push(createRingParticle(
          state.apexStrike.startPosition,
          config.chainGlowColor,
          config.chainGlowRadius
        ));
      }

      // Screen shake - proportional to bloodlust
      const shakeIntensity = 6 + (bloodlust / 100) * 8;
      this.triggerShake(shakeIntensity, 120);

      // Freeze frame for impact
      if (bloodlust >= APEX_STRIKE.bloodlust.furyThreshold) {
        this.triggerFreeze('massacre');
      } else if (bloodlust >= 50) {
        this.triggerFreeze('significant');
      }

      // Play hit sound
      const sound = getSoundEngine();
      sound.play('hit', { pitch: 0.7, volume: 1.0 });

      // Play special sound at max bloodlust
      if (bloodlust >= APEX_STRIKE.bloodlust.furyThreshold) {
        sound.play('massacre');
      }
    },

    /**
     * Emit Apex Miss effects
     * Called when strike misses (punishment feedback)
     */
    emitApexMiss(position: Vector2, direction: Vector2) {
      // Update state
      state.apexStrike.phase = 'recovery';
      state.apexStrike.chainAvailable = false;

      // Tumble particles - sad scattered effect
      const tumbleParticles = createApexTumbleParticles(position, direction);
      state.particles.push(...tumbleParticles);

      // Whiff trail - faded, sad trail showing the miss
      const config = APEX_STRIKE.miss;
      const trailAngle = Math.atan2(direction.y, direction.x);

      for (let i = 0; i < 3; i++) {
        const offset = i * 15;
        state.particles.push({
          id: `apex-whiff-${Date.now()}-${i}`,
          position: {
            x: position.x - Math.cos(trailAngle) * offset,
            y: position.y - Math.sin(trailAngle) * offset,
          },
          velocity: { x: 0, y: 0 },
          color: config.whiffTrailColor,
          size: 8 - i * 2,
          lifetime: 200,
          maxLifetime: 200,
          alpha: 0.4 - i * 0.1,
          type: 'trail',
        });
      }

      // Small screen shake - disorienting
      this.triggerShake(config.recoveryWobbleIntensity, 200);

      // Play miss/whoosh sound
      const sound = getSoundEngine();
      sound.play('miss', { pitch: 1.0 });
    },

    /**
     * Emit Bloodlust Max effects
     * Called when bloodlust hits 100 (APEX FURY)
     */
    emitBloodlustMax(position: Vector2) {
      const config = APEX_STRIKE.bloodlust;

      // APEX FURY text particle - large, golden
      state.particles.push(createApexFuryTextParticle(position));

      // Golden particle burst
      const goldenBurst = createBurstParticles(position, config.furyColor, 25, 1.5);
      state.particles.push(...goldenBurst);

      // Expanding golden ring
      state.particles.push(createRingParticle(position, config.furyColor, 80));

      // Maximum screen shake
      this.triggerShake(SHAKE.massacre.amplitude, SHAKE.massacre.duration);

      // Dramatic freeze frame
      this.triggerFreeze('massacre');

      // Play power-up sound
      const sound = getSoundEngine();
      sound.play('powerup', { pitch: 0.8 });
      sound.play('bassDrop');
    },
  };
}

// =============================================================================
// Process Juice (called each frame)
// =============================================================================

export function processJuice(
  juice: JuiceSystem,
  deltaTime: number,
  gameState: GameState
): void {
  // Update escalation from game state
  juice.escalation.healthFraction = gameState.player.health / gameState.player.maxHealth;
  juice.escalation.wave = gameState.wave;
  juice.escalation.multiplier = calculateEscalationMultiplier(juice.escalation);

  // Update combo timer
  if (juice.escalation.comboTimer > 0) {
    juice.escalation.comboTimer -= deltaTime;
    if (juice.escalation.comboTimer <= 0) {
      juice.updateCombo();
    }
  }

  // =================================================================
  // NEW: Process freeze frames first - "time slows when you're badass"
  // =================================================================
  if (juice.freeze.active && juice.freeze.framesRemaining > 0) {
    juice.freeze.framesRemaining--;
    if (juice.freeze.framesRemaining <= 0) {
      juice.freeze.active = false;
      juice.freeze.type = null;
    }
    // During freeze: don't update anything except particles (they look cool frozen)
    // Return early to freeze the game world
    return;
  }

  // Update particles
  const dt = deltaTime / 1000;

  juice.particles.forEach((particle) => {
    // Update position
    particle.position.x += particle.velocity.x * dt;
    particle.position.y += particle.velocity.y * dt;

    // =================================================================
    // TRANSFORMED: Handle new particle types with gravity and rotation
    // =================================================================

    // Apply gravity based on particle type
    if (particle.type === 'burst') {
      particle.velocity.y += 200 * dt; // Standard gravity
    }

    // SPIRAL particles: Apply gravity + rotation for death animation
    if (particle.type === 'spiral') {
      const gravity = particle.gravity ?? 400;
      particle.velocity.y += gravity * dt;
      // Update rotation
      if (particle.rotation !== undefined && particle.rotationSpeed !== undefined) {
        particle.rotation += particle.rotationSpeed * dt;
      }
      // Add slight drift for organic feel
      particle.velocity.x *= 0.98; // Air resistance
    }

    // DRIP particles: Heavy gravity for amber drip effect
    if (particle.type === 'drip') {
      const gravity = particle.gravity ?? PARTICLES.honeyDrip.gravity;
      particle.velocity.y += gravity * dt;
      // Slow down horizontal movement for thick drip feel
      particle.velocity.x *= 0.95;
    }

    // POOL particles: Static, just fade
    if (particle.type === 'pool') {
      // Don't move, pools are static
      particle.velocity.x = 0;
      particle.velocity.y = 0;
    }

    // GRAZE_SPARK particles: Quick flash with deceleration
    if (particle.type === 'graze_spark') {
      // Fast deceleration for snappy spark feel
      particle.velocity.x *= 0.9;
      particle.velocity.y *= 0.9;
    }

    // FRAGMENT particles: Fast burst outward
    if (particle.type === 'fragment') {
      // Slow down quickly for impact feel
      particle.velocity.x *= 0.92;
      particle.velocity.y *= 0.92;
    }

    // =================================================================
    // APEX STRIKE particle physics
    // =================================================================

    // APEX_WIND_DUST: Swirling motion with slow decay
    if (particle.type === 'apex_wind_dust') {
      // Continue swirling motion (circular path)
      const swirl = 3; // Swirl rate
      const angle = Math.atan2(particle.velocity.y, particle.velocity.x);
      const speed = Math.hypot(particle.velocity.x, particle.velocity.y);
      const newAngle = angle + swirl * dt;
      particle.velocity.x = Math.cos(newAngle) * speed * 0.95; // Decay
      particle.velocity.y = Math.sin(newAngle) * speed * 0.95;
    }

    // APEX_SPEED_LINE: Fast fade, maintain direction
    if (particle.type === 'apex_speed_line') {
      // Speed lines fade very fast
      particle.velocity.x *= 0.85;
      particle.velocity.y *= 0.85;
    }

    // APEX_AIR: Air displacement disperses quickly
    if (particle.type === 'apex_air') {
      particle.velocity.x *= 0.88;
      particle.velocity.y *= 0.88;
    }

    // APEX_IMPACT: Explosion outward with gravity
    if (particle.type === 'apex_impact') {
      particle.velocity.y += 150 * dt; // Slight gravity
      particle.velocity.x *= 0.96;
      particle.velocity.y *= 0.96;
    }

    // APEX_TUMBLE: Sad falling particles
    if (particle.type === 'apex_tumble') {
      const gravity = particle.gravity ?? 300;
      particle.velocity.y += gravity * dt;
      // Add wobble for tumbling effect
      particle.velocity.x += (Math.random() - 0.5) * 20;
    }

    // Update lifetime
    particle.lifetime -= deltaTime;

    // Fade out (with special handling for different types)
    const progress = particle.lifetime / particle.maxLifetime;

    if (particle.type === 'fragment') {
      // Flash stays bright, then fades fast
      const flashDuration = PARTICLES.damageFlash.flashDuration;
      const fadeDuration = PARTICLES.damageFlash.fadeDuration;
      const elapsed = particle.maxLifetime - particle.lifetime;
      if (elapsed < flashDuration) {
        particle.alpha = 1; // Full brightness during flash
      } else {
        // Fade during fade phase
        particle.alpha = Math.max(0, 1 - (elapsed - flashDuration) / fadeDuration);
      }
    } else if (particle.type === 'pool') {
      // Pools linger longer before fading
      if (progress > 0.3) {
        particle.alpha = 0.7; // Stay visible
      } else {
        particle.alpha = 0.7 * (progress / 0.3); // Fade in last 30%
      }
    } else {
      // Standard fade
      particle.alpha = Math.max(0, progress);
    }

    // Grow ring particles
    if (particle.type === 'ring') {
      const maxSize = parseFloat(particle.text || '100');
      const ringProgress = 1 - particle.lifetime / particle.maxLifetime;
      particle.size = maxSize * ringProgress;
    }
  });

  // Remove dead particles - filter in place by reassigning the internal array
  const aliveParticles = juice.particles.filter((p) => p.lifetime > 0);
  juice.particles.length = 0;
  juice.particles.push(...aliveParticles);

  // Update shake
  if (juice.shake.duration > 0) {
    juice.shake.elapsed += deltaTime;

    if (juice.shake.elapsed < juice.shake.duration) {
      // Calculate shake offset
      const progress = juice.shake.elapsed / juice.shake.duration;
      const decay = 1 - progress;
      const magnitude = juice.shake.intensity * decay;

      juice.shake.offset = {
        x: (Math.random() - 0.5) * 2 * magnitude,
        y: (Math.random() - 0.5) * 2 * magnitude,
      };
    } else {
      // Shake complete
      juice.shake.intensity = 0;
      juice.shake.duration = 0;
      juice.shake.elapsed = 0;
      juice.shake.offset = { x: 0, y: 0 };
    }
  }

  // DD-16: Update clutch moment
  if (juice.clutch.active) {
    juice.clutch.remaining -= deltaTime;

    if (juice.clutch.remaining <= 0) {
      // Clutch moment complete - reset
      juice.clutch.active = false;
      juice.clutch.level = null;
      juice.clutch.timeScale = 1.0;
      juice.clutch.zoom = 1.0;
      juice.clutch.remaining = 0;
      juice.clutch.duration = 0;
    } else {
      // Ease out the zoom as clutch ends
      const progress = juice.clutch.remaining / juice.clutch.duration;
      // Keep time scale until nearly done, then ease back
      if (progress < 0.2) {
        const easeProgress = progress / 0.2;
        juice.clutch.timeScale = 1.0 - (1.0 - juice.clutch.timeScale) * easeProgress;
        juice.clutch.zoom = 1.0 + (juice.clutch.zoom - 1.0) * easeProgress;
      }
    }
  }
}

/**
 * Get the effective time scale for game logic
 * Called by game loop to slow down time during clutch moments AND freeze frames
 *
 * Priority: Freeze > Clutch > Normal
 */
export function getEffectiveTimeScale(juice: JuiceSystem): number {
  // Freeze frames completely stop time
  if (juice.freeze.active && juice.freeze.framesRemaining > 0) {
    return 0; // Complete stop
  }
  // Clutch moments slow time
  if (juice.clutch.active) {
    return juice.clutch.timeScale;
  }
  return 1.0;
}

/**
 * Check if game is currently in a freeze frame
 * Use this to skip game logic updates during freeze
 */
export function isInFreezeFrame(juice: JuiceSystem): boolean {
  return juice.freeze.active && juice.freeze.framesRemaining > 0;
}

// =============================================================================
// Clutch Moment Detection (S3)
// =============================================================================

export interface ClutchMomentConfig {
  timeScale: number;
  zoomFactor: number;
  bassDrop: boolean;
  durationMs: number;
}

/**
 * Check if clutch moment should trigger
 *
 * From .outline.md:
 * - health_fraction < 0.15 AND threats > 3 → FULL CLUTCH
 * - health_fraction < 0.25 AND threats > 5 → MEDIUM CLUTCH
 * - health_fraction < 0.10 → CRITICAL
 */
export function checkClutchMoment(
  healthFraction: number,
  threatCount: number
): ClutchMomentConfig | null {
  // Full clutch
  if (healthFraction < 0.15 && threatCount > 3) {
    return {
      timeScale: 0.2,
      zoomFactor: 1.3,
      bassDrop: true,
      durationMs: 1000,
    };
  }

  // Medium clutch
  if (healthFraction < 0.25 && threatCount > 5) {
    return {
      timeScale: 1,
      zoomFactor: 1.2,
      bassDrop: true,
      durationMs: 500,
    };
  }

  // Critical
  if (healthFraction < 0.1) {
    return {
      timeScale: 0.3,
      zoomFactor: 1,
      bassDrop: false,
      durationMs: 500,
    };
  }

  return null;
}

// =============================================================================
// DD-17: Combo Crescendo
// =============================================================================

export interface ComboVisualState {
  comboCount: number;
  brightness: number;      // 1.0 base, 1.2 at combo 5+
  saturation: number;      // 1.0 base, 1.3 at combo 10+
  particleDensity: number; // 1.0 base, 2.0 at combo 20+
  euphoriaMode: boolean;   // true at combo 50+
}

/**
 * Get visual state based on current combo
 *
 * Scaling Rules:
 * - Combo 0-4: Base visuals (1.0, 1.0, 1.0, false)
 * - Combo 5-9: brightness=1.2
 * - Combo 10-19: saturation=1.3
 * - Combo 20-49: particleDensity=2.0
 * - Combo 50+: euphoriaMode=true (all maxed)
 */
export function getComboVisuals(combo: number): ComboVisualState {
  // Base state
  const state: ComboVisualState = {
    comboCount: combo,
    brightness: 1.0,
    saturation: 1.0,
    particleDensity: 1.0,
    euphoriaMode: false,
  };

  // Combo 5+: Brightness boost
  if (combo >= 5) {
    state.brightness = 1.2;
  }

  // Combo 10+: Saturation boost
  if (combo >= 10) {
    state.saturation = 1.3;
  }

  // Combo 20+: Particle density boost
  if (combo >= 20) {
    state.particleDensity = 2.0;
  }

  // Combo 50+: EUPHORIA MODE - everything maxed
  if (combo >= 50) {
    state.brightness = 1.4;
    state.saturation = 1.5;
    state.particleDensity = 3.0;
    state.euphoriaMode = true;
  }

  return state;
}

// =============================================================================
// DD-20: Health Vignette
// =============================================================================

export interface HealthVignette {
  intensity: number;  // 0.0 = none, 1.0 = full danger
  color: string;      // Red at low health
  pulseRate: number;  // Hz of pulse animation
}

/**
 * Get vignette state based on health fraction
 *
 * Scaling Rules:
 * - health > 50%: intensity=0 (no vignette)
 * - health 25-50%: intensity = (0.5 - health) * 2, pulseRate=1Hz
 * - health < 25%: intensity = (0.25 - health) * 4, pulseRate=2Hz
 * - health < 10%: intensity=1.0, pulseRate=4Hz (critical)
 */
export function getHealthVignette(healthFraction: number): HealthVignette {
  // No vignette above 50% health
  if (healthFraction > 0.5) {
    return {
      intensity: 0,
      color: 'rgba(255, 0, 0, 0)',
      pulseRate: 0,
    };
  }

  // Critical: < 10% health
  if (healthFraction < 0.1) {
    return {
      intensity: 1.0,
      color: COLORS.crisis,
      pulseRate: 4,
    };
  }

  // Danger: < 25% health
  if (healthFraction < 0.25) {
    const intensity = Math.min(1.0, (0.25 - healthFraction) * 4);
    return {
      intensity,
      color: COLORS.crisis,
      pulseRate: 2,
    };
  }

  // Warning: 25-50% health
  const intensity = (0.5 - healthFraction) * 2;
  return {
    intensity,
    color: COLORS.crisis,
    pulseRate: 1,
  };
}

// =============================================================================
// =============================================================================
// NEW: Visual Tells Rendering (Appendix E)
// =============================================================================

/**
 * Render a charging glow effect around an entity
 * "Every attack is telegraphed" - gold glow pulses before attack
 *
 * @param ctx - Canvas rendering context
 * @param position - Entity position
 * @param radius - Entity radius
 * @param chargeProgress - 0-1 progress through charge
 * @param gameTime - Current game time for pulse animation
 */
export function renderChargingGlow(
  ctx: CanvasRenderingContext2D,
  position: Vector2,
  radius: number,
  chargeProgress: number,
  gameTime: number
): void {
  const config = TELLS.chargingGlow;

  // Pulse based on time
  const pulsePhase = Math.sin((gameTime / config.pulseRate) * Math.PI * 2);
  const pulseScale = 1 + (config.pulseScale - 1) * ((pulsePhase + 1) / 2);

  // Opacity increases with charge progress, oscillates with pulse
  const baseOpacity = config.opacity[0] + (config.opacity[1] - config.opacity[0]) * chargeProgress;
  const opacity = baseOpacity * (0.7 + 0.3 * ((pulsePhase + 1) / 2));

  // Scale increases with charge progress
  const glowRadius = radius * (1.2 + chargeProgress * 0.8) * pulseScale;

  ctx.save();

  // Outer glow
  const gradient = ctx.createRadialGradient(
    position.x, position.y, radius * 0.8,
    position.x, position.y, glowRadius
  );
  gradient.addColorStop(0, `rgba(255, 215, 0, 0)`); // Transparent center
  gradient.addColorStop(0.4, `rgba(255, 215, 0, ${opacity * 0.6})`);
  gradient.addColorStop(1, `rgba(255, 215, 0, 0)`); // Fade out

  ctx.beginPath();
  ctx.arc(position.x, position.y, glowRadius, 0, Math.PI * 2);
  ctx.fillStyle = gradient;
  ctx.fill();

  // Inner bright ring at high charge
  if (chargeProgress > 0.7) {
    ctx.beginPath();
    ctx.arc(position.x, position.y, radius + 3, 0, Math.PI * 2);
    ctx.strokeStyle = `rgba(255, 255, 200, ${(chargeProgress - 0.7) / 0.3 * opacity})`;
    ctx.lineWidth = 2;
    ctx.stroke();
  }

  ctx.restore();
}

/**
 * Render formation lines between coordinating enemies
 * "Show only when coordinated" - golden lines connecting bee formation
 *
 * @param ctx - Canvas rendering context
 * @param positions - Array of enemy positions in formation
 * @param gameTime - Current game time for fade animation
 * @param coordinationLevel - How coordinated (0-10), shows at 3+
 */
export function renderFormationLines(
  ctx: CanvasRenderingContext2D,
  positions: Vector2[],
  gameTime: number,
  coordinationLevel: number
): void {
  const config = TELLS.formationLines;

  // Only show when minimum coordination reached
  if (positions.length < config.minBees || coordinationLevel < 3) {
    return;
  }

  ctx.save();

  // Pulse opacity based on coordination level
  const baseOpacity = config.opacity * (0.3 + (coordinationLevel / 10) * 0.7);
  const pulseOpacity = baseOpacity * (0.8 + 0.2 * Math.sin(gameTime / 200 * Math.PI * 2));

  ctx.strokeStyle = `rgba(255, 215, 0, ${pulseOpacity})`;
  ctx.lineWidth = config.width;
  ctx.setLineDash([5, 5]); // Dashed line for formation feel

  // Connect all positions in formation (web pattern)
  for (let i = 0; i < positions.length; i++) {
    for (let j = i + 1; j < positions.length; j++) {
      const dist = Math.hypot(
        positions[j].x - positions[i].x,
        positions[j].y - positions[i].y
      );
      // Only draw lines for reasonably close enemies
      if (dist < 150) {
        ctx.beginPath();
        ctx.moveTo(positions[i].x, positions[i].y);
        ctx.lineTo(positions[j].x, positions[j].y);
        ctx.stroke();
      }
    }
  }

  ctx.setLineDash([]); // Reset dash
  ctx.restore();
}

/**
 * Render a stinger trail behind a fast-moving entity
 * "Venom purple trail" - shows momentum and danger
 *
 * @param ctx - Canvas rendering context
 * @param position - Current position
 * @param velocity - Current velocity
 * @param length - Trail length (optional, calculated from velocity if not provided)
 */
export function renderStingerTrail(
  ctx: CanvasRenderingContext2D,
  position: Vector2,
  velocity: Vector2,
  length?: number
): void {
  // Using TELLS.stingerTrail config for color
  const { color } = TELLS.stingerTrail;

  const speed = Math.hypot(velocity.x, velocity.y);
  if (speed < 50) return; // No trail for slow movement

  // Trail length based on speed
  const trailLength = length ?? Math.min(speed * 0.3, 60);

  // Normalize and reverse velocity for trail direction
  const nx = -velocity.x / speed;
  const ny = -velocity.y / speed;

  ctx.save();

  // Draw gradient trail
  const gradient = ctx.createLinearGradient(
    position.x, position.y,
    position.x + nx * trailLength, position.y + ny * trailLength
  );
  // Convert hex color to rgba for gradients
  const hexToRgb = (hex: string) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return { r, g, b };
  };
  const rgb = hexToRgb(color);
  gradient.addColorStop(0, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0.8)`); // Solid start
  gradient.addColorStop(1, `rgba(${rgb.r}, ${rgb.g}, ${rgb.b}, 0)`);    // Fade out

  ctx.beginPath();
  ctx.moveTo(position.x, position.y);
  ctx.lineTo(position.x + nx * trailLength, position.y + ny * trailLength);
  ctx.strokeStyle = gradient;
  ctx.lineWidth = 4;
  ctx.lineCap = 'round';
  ctx.stroke();

  ctx.restore();
}

// =============================================================================
// DD-29-1: Entity Breathing System
// =============================================================================

export interface BreathingConfig {
  baseRate: number;      // Hz - breaths per second
  intensity: number;     // 0-1 - how much the glow expands
  phaseOffset?: number;  // 0-1 - desync between entities
}

/**
 * Calculate the current breath phase for an entity.
 *
 * Breathing creates a subtle pulsing effect that makes entities feel alive.
 * The phase oscillates smoothly between 0 and 1, where:
 * - 0 = fully contracted (minimum glow)
 * - 1 = fully expanded (maximum glow)
 *
 * @param gameTime - Current game time in milliseconds
 * @param config - Breathing configuration
 * @returns A value between 0 and 1 representing breath phase
 */
export function getBreathPhase(gameTime: number, config: BreathingConfig): number {
  const { baseRate, phaseOffset = 0 } = config;

  // Convert gameTime to seconds and calculate phase
  const timeSeconds = gameTime / 1000;
  const cyclePosition = (timeSeconds * baseRate + phaseOffset) % 1;

  // Use sine wave for smooth breathing (0-1 range)
  return (Math.sin(cyclePosition * Math.PI * 2 - Math.PI / 2) + 1) / 2;
}

/**
 * Get glow radius multiplier based on breath phase
 * Returns a value to multiply the base glow radius by
 */
export function getBreathGlowMultiplier(
  breathPhase: number,
  intensity: number
): number {
  // Base is 1.0, expands up to (1 + intensity) at full breath
  return 1.0 + breathPhase * intensity;
}

/**
 * Get glow alpha multiplier based on breath phase
 * Returns a value to multiply the base glow alpha by
 */
export function getBreathAlphaMultiplier(
  breathPhase: number,
  intensity: number
): number {
  // Alpha varies from 0.6 to 1.0 based on breath phase and intensity
  return 0.6 + breathPhase * 0.4 * intensity;
}

// Preset breathing configs for different entity states
export const BREATHING_CONFIGS: Record<string, BreathingConfig> = {
  // Player breathing
  playerCalm: { baseRate: 0.5, intensity: 0.15 },      // Calm, slow pulse
  playerLowHealth: { baseRate: 2.0, intensity: 0.4 },  // Rapid, anxious pulse

  // Enemy breathing by state
  enemyChase: { baseRate: 0.8, intensity: 0.2 },       // Normal hunting
  enemyTelegraph: { baseRate: 4.0, intensity: 0.5 },   // About to attack - rapid pulse
  enemyRecovery: { baseRate: 0.3, intensity: 0.1 },    // Tired, slow fade
  enemyAttack: { baseRate: 6.0, intensity: 0.6 },      // Attacking - very rapid

  // Projectiles
  projectile: { baseRate: 2.0, intensity: 0.3 },       // Shimmer effect
};

/**
 * Generate a stable phase offset from an entity ID
 * This ensures each entity breathes at a slightly different phase
 */
export function getEntityPhaseOffset(entityId: string): number {
  // Simple hash to get consistent offset from ID
  let hash = 0;
  for (let i = 0; i < entityId.length; i++) {
    hash = ((hash << 5) - hash) + entityId.charCodeAt(i);
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash % 1000) / 1000; // 0-1 range
}

// =============================================================================
// DD-29-2: Screen Intensity System
// =============================================================================

export interface IntensityColors {
  background: string;
  border: string;
  grid: string;
}

// Color presets for different intensity levels
const INTENSITY_PRESETS = {
  calm: { background: '#1a1a2e', border: '#2a2a4e', grid: '#252540' },
  tense: { background: '#1e1a2e', border: '#3a2a5e', grid: '#302550' },
  intense: { background: '#221a2e', border: '#4a2a6e', grid: '#352560' },
  crisis: { background: '#281a2e', border: '#5a2a7e', grid: '#402570' },
};

/**
 * Interpolate between two hex colors
 */
function lerpColor(color1: string, color2: string, t: number): string {
  const r1 = parseInt(color1.slice(1, 3), 16);
  const g1 = parseInt(color1.slice(3, 5), 16);
  const b1 = parseInt(color1.slice(5, 7), 16);

  const r2 = parseInt(color2.slice(1, 3), 16);
  const g2 = parseInt(color2.slice(3, 5), 16);
  const b2 = parseInt(color2.slice(5, 7), 16);

  const r = Math.round(r1 + (r2 - r1) * t);
  const g = Math.round(g1 + (g2 - g1) * t);
  const b = Math.round(b1 + (b2 - b1) * t);

  return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
}

/**
 * Get screen intensity colors based on wave and health
 *
 * The screen subtly shifts colors as intensity increases:
 * - Waves 1-2: Calm blue
 * - Waves 3-5: Slight purple tint
 * - Waves 6-8: Deeper purple
 * - Waves 9+: Crisis purple
 * - Low health adds red tint
 */
export function getIntensityColors(wave: number, healthFraction: number): IntensityColors {
  // Determine base intensity from wave
  let baseColors: IntensityColors;
  let transitionProgress: number;

  if (wave <= 2) {
    baseColors = INTENSITY_PRESETS.calm;
    transitionProgress = 0;
  } else if (wave <= 5) {
    // Transition from calm to tense over waves 3-5
    transitionProgress = (wave - 2) / 3;
    baseColors = {
      background: lerpColor(INTENSITY_PRESETS.calm.background, INTENSITY_PRESETS.tense.background, transitionProgress),
      border: lerpColor(INTENSITY_PRESETS.calm.border, INTENSITY_PRESETS.tense.border, transitionProgress),
      grid: lerpColor(INTENSITY_PRESETS.calm.grid, INTENSITY_PRESETS.tense.grid, transitionProgress),
    };
  } else if (wave <= 8) {
    // Transition from tense to intense over waves 6-8
    transitionProgress = (wave - 5) / 3;
    baseColors = {
      background: lerpColor(INTENSITY_PRESETS.tense.background, INTENSITY_PRESETS.intense.background, transitionProgress),
      border: lerpColor(INTENSITY_PRESETS.tense.border, INTENSITY_PRESETS.intense.border, transitionProgress),
      grid: lerpColor(INTENSITY_PRESETS.tense.grid, INTENSITY_PRESETS.intense.grid, transitionProgress),
    };
  } else {
    // Waves 9+ stay at crisis
    baseColors = INTENSITY_PRESETS.crisis;
  }

  // Add red tint at low health
  if (healthFraction < 0.25) {
    const redIntensity = (0.25 - healthFraction) / 0.25;
    // Shift background toward red
    const redTint = '#2e1a1a'; // Reddish dark
    baseColors = {
      background: lerpColor(baseColors.background, redTint, redIntensity * 0.5),
      border: lerpColor(baseColors.border, '#5e2a2a', redIntensity * 0.3),
      grid: lerpColor(baseColors.grid, '#402525', redIntensity * 0.3),
    };
  }

  return baseColors;
}

// =============================================================================
// DD-30: Metamorphosis Rendering Functions
// =============================================================================

/**
 * Render a pulsing enemy during metamorphosis.
 *
 * Visual States:
 * - 'normal': No special effect
 * - 'pulsing' (10-15s): Orange->red pulsing outline at 2Hz, size oscillates +/-10%
 * - 'seeking' (15-20s): Faster pulse at 4Hz, particles emanating
 * - 'combining': Flash effect (handled by emitMetamorphosis)
 *
 * @param ctx - Canvas rendering context
 * @param enemy - Enemy entity (may have pulsingState field)
 * @param gameTime - Current game time in milliseconds
 */
export function renderPulsingEnemy(
  ctx: CanvasRenderingContext2D,
  enemy: MetamorphosisEnemy,
  gameTime: number
): void {
  const pulsingState = enemy.pulsingState ?? 'normal';

  if (pulsingState === 'normal') {
    return; // No special rendering needed
  }

  const { x, y } = enemy.position;
  const baseRadius = enemy.radius;

  // Calculate pulse frequency based on state
  const frequency = pulsingState === 'seeking' ? 4 : 2; // Hz
  const pulsePhase = Math.sin(gameTime / 1000 * frequency * 2 * Math.PI);

  // Size oscillation: +/-10% based on pulse phase
  const sizeOscillation = 1 + pulsePhase * 0.1;

  ctx.save();

  // Apply size oscillation via transform
  ctx.translate(x, y);
  ctx.scale(sizeOscillation, sizeOscillation);
  ctx.translate(-x, -y);

  // Calculate color gradient based on pulse phase (0-1 range)
  const colorPhase = (pulsePhase + 1) / 2; // Convert from -1..1 to 0..1
  const { start, end } = METAMORPHOSIS_COLORS.pulsing;

  // Interpolate between start (orange) and end (red)
  const r1 = parseInt(start.slice(1, 3), 16);
  const g1 = parseInt(start.slice(3, 5), 16);
  const b1 = parseInt(start.slice(5, 7), 16);
  const r2 = parseInt(end.slice(1, 3), 16);
  const g2 = parseInt(end.slice(3, 5), 16);
  const b2 = parseInt(end.slice(5, 7), 16);

  const r = Math.round(r1 + (r2 - r1) * colorPhase);
  const g = Math.round(g1 + (g2 - g1) * colorPhase);
  const b = Math.round(b1 + (b2 - b1) * colorPhase);
  const pulseColor = `rgb(${r}, ${g}, ${b})`;

  // Draw pulsing outline
  ctx.beginPath();
  ctx.arc(x, y, baseRadius + 4, 0, Math.PI * 2);
  ctx.strokeStyle = pulseColor;
  ctx.lineWidth = 3;
  ctx.stroke();

  // For seeking state, add emanating particles effect
  if (pulsingState === 'seeking') {
    // Draw additional outer glow
    ctx.beginPath();
    ctx.arc(x, y, baseRadius + 8, 0, Math.PI * 2);
    const glowAlpha = 0.3 + 0.3 * ((pulsePhase + 1) / 2);
    ctx.strokeStyle = `rgba(255, 0, 255, ${glowAlpha})`; // Magenta glow
    ctx.lineWidth = 2;
    ctx.stroke();

    // Draw small emanating dots
    const particleCount = 4;
    const time = gameTime / 1000;
    for (let i = 0; i < particleCount; i++) {
      const angle = (Math.PI * 2 * i) / particleCount + time * 2;
      const distance = baseRadius + 12 + Math.sin(time * 4 + i) * 4;
      const px = x + Math.cos(angle) * distance;
      const py = y + Math.sin(angle) * distance;

      ctx.beginPath();
      ctx.arc(px, py, 2, 0, Math.PI * 2);
      ctx.fillStyle = METAMORPHOSIS_COLORS.threads;
      ctx.fill();
    }
  }

  ctx.restore();
}

/**
 * Render seeking threads between two enemies during metamorphosis.
 *
 * Draws a magenta energy thread with:
 * - Pulsing alpha (0.3-0.8)
 * - Slight wave/noise for organic feel
 * - Bezier curve, not straight line
 *
 * @param ctx - Canvas rendering context
 * @param seeker - The seeking enemy
 * @param targetPos - Position of the target enemy
 * @param gameTime - Current game time in milliseconds
 */
export function renderSeekingThreads(
  ctx: CanvasRenderingContext2D,
  seeker: MetamorphosisEnemy,
  targetPos: Vector2,
  gameTime: number
): void {
  const { x: x1, y: y1 } = seeker.position;
  const { x: x2, y: y2 } = targetPos;

  // Calculate midpoint for bezier control point
  const midX = (x1 + x2) / 2;
  const midY = (y1 + y2) / 2;

  // Add wave/noise to control point for organic feel
  const time = gameTime / 1000;
  const waveOffset = Math.sin(time * 3) * 20;
  const perpX = -(y2 - y1);
  const perpY = x2 - x1;
  const perpLen = Math.sqrt(perpX * perpX + perpY * perpY) || 1;

  const ctrlX = midX + (perpX / perpLen) * waveOffset;
  const ctrlY = midY + (perpY / perpLen) * waveOffset;

  // Pulsing alpha (0.3-0.8)
  const alphaPulse = 0.55 + 0.25 * Math.sin(time * 4 * Math.PI);

  ctx.save();

  // Draw main thread
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.quadraticCurveTo(ctrlX, ctrlY, x2, y2);
  ctx.strokeStyle = `rgba(255, 0, 255, ${alphaPulse})`;
  ctx.lineWidth = 3;
  ctx.lineCap = 'round';
  ctx.stroke();

  // Draw glow layer
  ctx.beginPath();
  ctx.moveTo(x1, y1);
  ctx.quadraticCurveTo(ctrlX, ctrlY, x2, y2);
  ctx.strokeStyle = `rgba(255, 0, 255, ${alphaPulse * 0.3})`;
  ctx.lineWidth = 8;
  ctx.stroke();

  // Draw energy nodes along the thread
  const nodeCount = 3;
  for (let i = 1; i < nodeCount; i++) {
    const t = i / nodeCount;
    // Quadratic bezier point calculation
    const px = (1 - t) * (1 - t) * x1 + 2 * (1 - t) * t * ctrlX + t * t * x2;
    const py = (1 - t) * (1 - t) * y1 + 2 * (1 - t) * t * ctrlY + t * t * y2;

    const nodeSize = 3 + Math.sin(time * 6 + i * Math.PI) * 1.5;
    ctx.beginPath();
    ctx.arc(px, py, nodeSize, 0, Math.PI * 2);
    ctx.fillStyle = `rgba(255, 255, 255, ${alphaPulse})`;
    ctx.fill();
  }

  ctx.restore();
}

/**
 * Render a colossal enemy (the result of metamorphosis).
 *
 * Visual characteristics:
 * - Deep crimson (#880000) body
 * - Black aura (shadow blur)
 * - Particle trail behind
 * - Size 3x normal enemies (radius ~36px)
 *
 * @param ctx - Canvas rendering context
 * @param colossal - The colossal enemy entity
 * @param gameTime - Current game time in milliseconds
 */
export function renderColossal(
  ctx: CanvasRenderingContext2D,
  colossal: MetamorphosisEnemy,
  gameTime: number
): void {
  const { x, y } = colossal.position;
  const radius = colossal.radius || 36; // Default to 3x normal (12 * 3)

  ctx.save();

  // Black aura (shadow blur)
  ctx.shadowColor = 'rgba(0, 0, 0, 0.8)';
  ctx.shadowBlur = 25;
  ctx.shadowOffsetX = 0;
  ctx.shadowOffsetY = 0;

  // Draw main body with deep crimson
  ctx.beginPath();
  ctx.arc(x, y, radius, 0, Math.PI * 2);
  ctx.fillStyle = METAMORPHOSIS_COLORS.colossal;
  ctx.fill();

  // Clear shadow for additional details
  ctx.shadowBlur = 0;

  // Inner glow/highlight
  const time = gameTime / 1000;
  const breathPhase = (Math.sin(time * 1.5 * Math.PI) + 1) / 2;

  ctx.beginPath();
  ctx.arc(x, y, radius * 0.7, 0, Math.PI * 2);
  ctx.fillStyle = `rgba(255, 50, 50, ${0.2 + breathPhase * 0.1})`;
  ctx.fill();

  // Pulsing outer ring
  ctx.beginPath();
  ctx.arc(x, y, radius + 4 + breathPhase * 3, 0, Math.PI * 2);
  ctx.strokeStyle = `rgba(136, 0, 0, ${0.5 + breathPhase * 0.3})`;
  ctx.lineWidth = 2;
  ctx.stroke();

  // Draw particle trail based on velocity
  const vx = colossal.velocity?.x ?? 0;
  const vy = colossal.velocity?.y ?? 0;
  const speed = Math.sqrt(vx * vx + vy * vy);

  if (speed > 10) {
    // Normalize and reverse for trail direction
    const nx = -vx / speed;
    const ny = -vy / speed;

    // Draw trail particles
    const trailCount = 5;
    for (let i = 1; i <= trailCount; i++) {
      const distance = i * 12;
      const px = x + nx * distance;
      const py = y + ny * distance;
      const trailAlpha = 0.6 * (1 - i / (trailCount + 1));
      const trailRadius = radius * 0.3 * (1 - i / (trailCount + 1));

      ctx.beginPath();
      ctx.arc(px, py, trailRadius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(136, 0, 0, ${trailAlpha})`;
      ctx.fill();
    }
  }

  // Core dark eye
  ctx.beginPath();
  ctx.arc(x, y, radius * 0.2, 0, Math.PI * 2);
  ctx.fillStyle = '#220000';
  ctx.fill();

  ctx.restore();
}

/**
 * Render a full-screen revelation flash effect.
 *
 * Used when metamorphosis completes to create a dramatic visual impact.
 *
 * @param ctx - Canvas rendering context
 * @param progress - Animation progress from 0 (full flash) to 1 (fully transparent)
 * @param arenaWidth - Width of the arena
 * @param arenaHeight - Height of the arena
 */
export function renderRevelationFlash(
  ctx: CanvasRenderingContext2D,
  progress: number,
  arenaWidth: number,
  arenaHeight: number
): void {
  if (progress >= 1) {
    return; // Fully faded, nothing to draw
  }

  // Clamp progress to valid range
  const clampedProgress = Math.max(0, Math.min(1, progress));

  // Calculate alpha (1 at progress 0, 0 at progress 1)
  // Use ease-out for more natural fade
  const easeProgress = 1 - Math.pow(1 - clampedProgress, 2);
  const alpha = 1 - easeProgress;

  ctx.save();

  // Draw white flash overlay
  ctx.fillStyle = `rgba(255, 255, 255, ${alpha})`;
  ctx.fillRect(0, 0, arenaWidth, arenaHeight);

  // Add subtle red tint at edges for dramatic effect (at high alpha)
  if (alpha > 0.3) {
    const gradient = ctx.createRadialGradient(
      arenaWidth / 2,
      arenaHeight / 2,
      0,
      arenaWidth / 2,
      arenaHeight / 2,
      Math.max(arenaWidth, arenaHeight) / 2
    );
    gradient.addColorStop(0, 'rgba(255, 255, 255, 0)');
    gradient.addColorStop(1, `rgba(255, 100, 100, ${alpha * 0.3})`);

    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, arenaWidth, arenaHeight);
  }

  ctx.restore();
}

/**
 * Helper to check if an enemy is in a metamorphosis state.
 */
export function isMetamorphosing(enemy: MetamorphosisEnemy): boolean {
  const state = enemy.pulsingState ?? 'normal';
  return state !== 'normal';
}

/**
 * Get the appropriate metamorphosis color for an enemy's current state.
 */
export function getMetamorphosisColor(state: MetamorphosisPulsingState): string {
  switch (state) {
    case 'pulsing':
      return METAMORPHOSIS_COLORS.pulsing.start;
    case 'seeking':
      return METAMORPHOSIS_COLORS.threads;
    case 'combining':
      return METAMORPHOSIS_COLORS.colossal;
    default:
      return COLORS.enemy;
  }
}

// =============================================================================
// APEX STRIKE RENDERING FUNCTIONS
// =============================================================================

/**
 * Render the wing blur disc effect during Apex Lock phase
 * "Circular blur effect around player (like helicopter blades)"
 *
 * @param ctx - Canvas rendering context
 * @param position - Player position
 * @param progress - 0-1 lock phase progress
 * @param gameTime - Current game time in ms for animation
 */
export function renderApexLockEffect(
  ctx: CanvasRenderingContext2D,
  position: Vector2,
  progress: number,
  gameTime: number
): void {
  const config = APEX_STRIKE.lock.wingBlur;

  // Calculate rotation based on time and speed
  const rotation = (gameTime / 1000) * config.rotationSpeed * Math.PI * 2;

  // Opacity increases with progress
  const opacity = config.opacity * (0.3 + progress * 0.7);

  ctx.save();
  ctx.translate(position.x, position.y);

  // Draw wing blur segments (like helicopter blades)
  for (let i = 0; i < config.count; i++) {
    const angle = rotation + (Math.PI * 2 * i) / config.count;
    const bladeLength = config.radius * (0.8 + progress * 0.4);

    // Each blade is a tapered line
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(Math.cos(angle) * bladeLength, Math.sin(angle) * bladeLength);

    // Color with semi-transparency for blur effect
    ctx.strokeStyle = `${config.color}${Math.floor(opacity * 255).toString(16).padStart(2, '0')}`;
    ctx.lineWidth = 3 + progress * 2;
    ctx.lineCap = 'round';
    ctx.stroke();
  }

  // Add central charging glow
  const glowConfig = APEX_STRIKE.lock.chargingGlow;
  const pulsePhase = Math.sin((gameTime / glowConfig.pulseRate) * Math.PI * 2);
  const glowOpacity = 0.3 + progress * 0.5 + pulsePhase * 0.1;

  // Interpolate color from start to end based on progress
  const gradient = ctx.createRadialGradient(0, 0, 0, 0, 0, 15 + progress * 10);
  gradient.addColorStop(0, `${glowConfig.colorStart}${Math.floor(glowOpacity * 255).toString(16).padStart(2, '0')}`);
  gradient.addColorStop(1, `${glowConfig.colorEnd}00`);

  ctx.beginPath();
  ctx.arc(0, 0, 15 + progress * 10, 0, Math.PI * 2);
  ctx.fillStyle = gradient;
  ctx.fill();

  ctx.restore();

  // Render focus vignette at higher progress
  if (progress > 0.3) {
    renderApexVignette(ctx, progress, 800, 600); // Assuming standard arena size
  }
}

/**
 * Render focus vignette effect during Apex Lock
 * "Subtle screen darkening around edges"
 */
function renderApexVignette(
  ctx: CanvasRenderingContext2D,
  intensity: number,
  width: number,
  height: number
): void {
  const config = APEX_STRIKE.lock.vignette;
  const finalIntensity = config.intensity * intensity;

  ctx.save();

  const gradient = ctx.createRadialGradient(
    width / 2, height / 2, Math.min(width, height) * 0.3,
    width / 2, height / 2, Math.max(width, height) * 0.7
  );
  gradient.addColorStop(0, 'rgba(0, 0, 0, 0)');
  gradient.addColorStop(1, `rgba(0, 0, 0, ${finalIntensity})`);

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, width, height);

  ctx.restore();
}

/**
 * Render the strike trail during Apex Strike phase
 * "Stinger trail behind the hornet (venom purple)"
 *
 * @param ctx - Canvas rendering context
 * @param startPos - Where strike began
 * @param endPos - Current position (or hit position)
 * @param bloodlust - 0-100 bloodlust level for intensity scaling
 */
export function renderApexStrikeTrail(
  ctx: CanvasRenderingContext2D,
  startPos: Vector2,
  endPos: Vector2,
  bloodlust: number
): void {
  const config = APEX_STRIKE.strike.trail;

  // Calculate trail intensity based on bloodlust
  const intensityScale = 1 + (bloodlust / 100) * (APEX_STRIKE.bloodlust.maxTrailIntensity - 1);

  ctx.save();

  // Main trail line
  const gradient = ctx.createLinearGradient(startPos.x, startPos.y, endPos.x, endPos.y);

  // Parse hex color to RGB for gradient
  const hexToRgba = (hex: string, alpha: number) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  gradient.addColorStop(0, hexToRgba(config.color, 0)); // Fade at start
  gradient.addColorStop(0.2, hexToRgba(config.color, 0.8 * intensityScale));
  gradient.addColorStop(1, hexToRgba(config.color, 0.4 * intensityScale)); // Solid at end

  ctx.beginPath();
  ctx.moveTo(startPos.x, startPos.y);
  ctx.lineTo(endPos.x, endPos.y);
  ctx.strokeStyle = gradient;
  ctx.lineWidth = config.width * intensityScale;
  ctx.lineCap = 'round';
  ctx.stroke();

  // Add glow layer at high bloodlust
  if (bloodlust >= 50) {
    ctx.beginPath();
    ctx.moveTo(startPos.x, startPos.y);
    ctx.lineTo(endPos.x, endPos.y);
    ctx.strokeStyle = hexToRgba(config.color, 0.3 * (bloodlust / 100));
    ctx.lineWidth = (config.width + 6) * intensityScale;
    ctx.stroke();
  }

  // Add bloodlust aura at high levels
  if (bloodlust >= APEX_STRIKE.bloodlust.auraThreshold) {
    const auraOpacity = ((bloodlust - 80) / 20) * 0.5;
    ctx.beginPath();
    ctx.arc(endPos.x, endPos.y, APEX_STRIKE.bloodlust.auraRadius, 0, Math.PI * 2);

    const auraGradient = ctx.createRadialGradient(
      endPos.x, endPos.y, 0,
      endPos.x, endPos.y, APEX_STRIKE.bloodlust.auraRadius
    );

    if (bloodlust >= APEX_STRIKE.bloodlust.furyThreshold) {
      // Golden aura at max bloodlust
      auraGradient.addColorStop(0, hexToRgba(APEX_STRIKE.bloodlust.furyColor, auraOpacity));
    } else {
      // Red aura at high bloodlust
      auraGradient.addColorStop(0, hexToRgba('#FF0000', auraOpacity));
    }
    auraGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.fillStyle = auraGradient;
    ctx.fill();
  }

  ctx.restore();
}

/**
 * Render bloodlust aura around player
 * "At high bloodlust (80+): Player has red aura"
 *
 * @param ctx - Canvas rendering context
 * @param position - Player position
 * @param bloodlust - 0-100 bloodlust level
 * @param gameTime - Current game time for pulse animation
 */
export function renderBloodlustAura(
  ctx: CanvasRenderingContext2D,
  position: Vector2,
  bloodlust: number,
  gameTime: number
): void {
  if (bloodlust < APEX_STRIKE.bloodlust.auraThreshold) {
    return; // No aura below threshold
  }

  const config = APEX_STRIKE.bloodlust;

  // Calculate intensity based on bloodlust (80-100 maps to 0-1)
  const intensity = (bloodlust - config.auraThreshold) / (100 - config.auraThreshold);

  // Pulse animation
  const pulsePhase = Math.sin(gameTime / 150 * Math.PI * 2);
  const pulseScale = 1 + pulsePhase * 0.15 * intensity;

  ctx.save();

  const radius = config.auraRadius * pulseScale;

  // Determine color based on fury threshold
  let auraColor: string;
  let innerOpacity: number;

  if (bloodlust >= config.furyThreshold) {
    // APEX FURY - golden aura
    auraColor = config.furyColor;
    innerOpacity = 0.6;
  } else {
    // High bloodlust - red aura
    auraColor = '#FF0000';
    innerOpacity = 0.3 + intensity * 0.3;
  }

  // Draw aura gradient
  const gradient = ctx.createRadialGradient(
    position.x, position.y, 0,
    position.x, position.y, radius
  );

  // Parse color for gradient
  const hexToRgba = (hex: string, alpha: number) => {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
  };

  gradient.addColorStop(0, hexToRgba(auraColor, innerOpacity * intensity));
  gradient.addColorStop(0.5, hexToRgba(auraColor, innerOpacity * 0.5 * intensity));
  gradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

  ctx.beginPath();
  ctx.arc(position.x, position.y, radius, 0, Math.PI * 2);
  ctx.fillStyle = gradient;
  ctx.fill();

  // Add inner bright core at fury
  if (bloodlust >= config.furyThreshold) {
    const coreGradient = ctx.createRadialGradient(
      position.x, position.y, 0,
      position.x, position.y, 15
    );
    coreGradient.addColorStop(0, hexToRgba(config.furyColor, 0.8));
    coreGradient.addColorStop(1, 'rgba(0, 0, 0, 0)');

    ctx.beginPath();
    ctx.arc(position.x, position.y, 15, 0, Math.PI * 2);
    ctx.fillStyle = coreGradient;
    ctx.fill();
  }

  ctx.restore();
}
