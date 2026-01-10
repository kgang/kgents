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
import type { AbilityId } from './abilities';
import { getSoundEngine } from './sound';

// =============================================================================
// DEBUG TIME SCALE (for principled test acceleration)
// =============================================================================

/**
 * Debug time scale multiplier for accelerated testing.
 *
 * This enables running the game at 4x speed (or faster) while preserving
 * the integrity of game-time-based systems like reaction modeling.
 *
 * Key insight: The PlaythroughAgent's reaction model operates in GAME time.
 * At 4x acceleration: 250ms game-time reaction = 62.5ms wall-clock time.
 * The reaction is still "250ms in game" - it just happens faster IRL.
 *
 * IMPORTANT: This multiplies on TOP of the juice system's time scaling:
 * - Freeze frames (0x) still freeze
 * - Clutch moments (0.2x) still slow
 * - But everything runs 4x faster when not in slowmo
 */
let debugTimeScale: number = 1.0;

/**
 * Set the debug time scale for accelerated testing.
 *
 * @param scale - Time multiplier (e.g., 4.0 for 4x speed)
 *                Range: 0.1 to 10.0 (clamped)
 */
export function DEBUG_SET_TIME_SCALE(scale: number): void {
  debugTimeScale = Math.max(0.1, Math.min(10.0, scale));
}

/**
 * Get the current debug time scale.
 *
 * @returns Current time scale multiplier
 */
export function DEBUG_GET_TIME_SCALE(): number {
  return debugTimeScale;
}

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
  // New shake events from quality spec
  dashExecution: { amplitude: 3, duration: 50, frequency: 60 },   // 2-3px on dash start
  dashGraze:     { amplitude: 1, duration: 30, frequency: 60 },   // 1px subtle graze feedback
  ballForming:   { amplitude: 1, duration: 100, frequency: 60 },  // Initial forming (ramps 1-5px)
  ballConstrict: { amplitude: 8, duration: 200, frequency: 60 },  // Intense constrict
  synergyDiscovery: { amplitude: 10, duration: 300, frequency: 60 }, // 10px + flash celebration
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
    count: 25,           // Full 25 particles for dramatic death effect
    color: '#FFE066',    // soft yellow pollen
    spread: 45,          // degrees
    lifespan: 400,       // ms
    rotation: 3,         // full rotations during descent
  },
  honeyDrip: {
    count: 6,            // Reduced from 15 for clarity
    color: '#F4A300',    // amber
    gravity: 200,        // px/s^2
    poolFade: 1200,      // ms - how long the pool lingers
  },
  damageFlash: {
    colors: ['#FF3333', '#FF0000'],  // pure red -> dark red (danger, not player)
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
      count: 3,            // Reduced from 6
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
      count: 3,            // Reduced from 6
      color: '#FFFFFF',
      length: 40,
      spread: 15,          // Degrees from direction
      lifespan: 80,        // Very quick
    },
    airDisplacement: {
      count: 5,            // Reduced from 10
      color: '#FFFFFF40',  // Very faint
      spread: 60,          // Degrees perpendicular to strike
      velocity: 200,
    },
    // DD-038-3: Afterimages - "3 ghostly silhouettes during strike"
    afterimages: {
      count: 3,            // Reduced from 5 afterimages during strike
      spawnInterval: 30,   // ms between spawns
      fadeTime: 300,       // ms total fade duration
      startAlpha: 0.7,     // Initial opacity
      color: '#CC5500',    // Player color (Burnt Amber)
      scale: 0.9,          // Slightly smaller than player
    },
  },

  // Hit effects - IMPACT
  hit: {
    burstCount: 10,           // Reduced from 20, max scales to 15
    burstColor: '#FF6600',    // Impact orange
    burstVelocity: 300,       // Fast burst
    flashDuration: 50,        // ms
    flashColor: '#FFFFFF',
    chainGlowColor: '#00FF88', // Green for chain ready (distinct from XP)
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
 * Run 039: Bumper-Rail Combo System Parameters
 * "Bees are not obstacles. Bees are terrain."
 * Pinball + Tony Hawk grinding + Peggle cascades
 */
export const BUMPER_JUICE = {
  // Bumper hit effect - pinball PING!
  bumperPing: {
    count: 6,               // Reduced from 12
    color: '#FFD700',       // Gold
    colorAlt: '#FFFFFF',    // White flash
    spread: 360,            // Full circle
    lifespan: 250,          // Quick flash ms
    size: 4,                // Medium sparks
    velocity: 180,          // Fast burst
  },
  // Rail chain lightning effect
  railLine: {
    color: '#D4A017',       // Amber lightning (enemy element, not player cyan)
    colorFlow: '#FFD700',   // Gold when in flow state
    width: 3,               // Line thickness
    glowRadius: 8,          // Glow around line
    fadeTime: 400,          // ms to fade out
    segmentCount: 5,        // Lightning segments per line
    jitter: 8,              // Perpendicular jitter px
  },
  // Flow state screen effect
  flowState: {
    speedLineCount: 12,     // Radial speed lines
    speedLineColor: '#FFD70040', // Semi-transparent gold
    chromaticOffset: 3,     // Pixels of color separation
    vignetteColor: '#FFD70020', // Golden vignette
    pulseRate: 150,         // ms per pulse
  },
  // Combo counter popup
  comboText: {
    color: '#FFFFFF',       // White
    colorFlow: '#FFD700',   // Gold in flow state
    size: 24,               // Large, readable
    duration: 800,          // Float duration ms
    floatSpeed: 60,         // Pixels per second upward
  },
  // Charged bee warning
  chargedBee: {
    glowColor: '#FF4444',   // Red danger
    glowRadius: 12,         // Large warning glow
    pulseRate: 100,         // Fast pulse ms
    sparkColor: '#FF8800',  // Orange sparks
    sparkCount: 4,          // Sparks around bee
  },
  // Chain break effect
  chainBreak: {
    color: '#FF4444',       // Red
    shatterCount: 8,        // Fragment particles
    shakeIntensity: 6,      // Screen shake
    shakeDuration: 150,     // ms
  },
} as const;

/**
 * INSANE COMBO SYSTEM Parameters
 * "If I have the right combo of perks and skill, I'll really pop off"
 *
 * @see systems/insane-combos.ts
 */
export const INSANE_COMBO_JUICE = {
  // === BEE BOUNCE (Pinball physics) ===
  beeBounce: {
    // Bounce spark effect - PING!
    sparkCount: 8,
    sparkColor: '#FFD700',       // Gold
    sparkColorAlt: '#FFFFFF',    // White flash
    sparkVelocity: 200,
    sparkLifespan: 200,
    // Trail during bounce chain
    trailColor: '#FFD70088',     // Semi-transparent gold
    trailWidth: 4,
    trailFadeTime: 400,
    // Flow state triggers at 3+ bounces
    flowThreshold: 3,
    flowColor: '#FFD700',
    // Screen effects at high bounce
    shakePerBounce: 2,           // px shake
    chromatic: {
      threshold: 6,              // Chromatic aberration at 6+ bounces
      intensity: 3,              // px offset
    },
    // Sound pitch scaling
    basePitch: 1.0,
    pitchPerBounce: 0.08,        // Higher pitch per bounce
  },

  // === MOMENTUM STACKING ===
  momentum: {
    // Kill streak visuals
    killStreak: {
      stackColor: '#FF4444',     // Red for damage
      pulseRate: 200,            // ms per pulse
      glowRadius: 20,
      maxGlow: 50,               // At max stacks
    },
    // Graze streak visuals
    grazeStreak: {
      stackColor: '#00FFFF',     // Cyan for graze
      sparkPerGraze: 4,
      ringColor: '#00FFFFAA',
    },
    // Perfect timing visuals
    perfectTiming: {
      flashColor: '#FFFFFF',
      flashDuration: 100,
      ringColor: '#FFD700',
    },
    // Momentum decay warning
    decayWarning: {
      pulseColor: '#FF666688',
      pulseRate: 100,
    },
  },

  // === COMBO TIERS ===
  tiers: {
    basic: {
      color: '#FFFFFF',
      textSize: 16,
      particleMultiplier: 1.0,
    },
    advanced: {
      color: '#FFD700',          // Gold
      textSize: 20,
      particleMultiplier: 1.5,
      glowRadius: 30,
    },
    legendary: {
      color: '#FF6600',          // Orange
      textSize: 24,
      particleMultiplier: 2.0,
      glowRadius: 50,
      screenTint: '#FF660010',
    },
    transcendent: {
      color: '#FF00FF',          // Magenta
      textSize: 28,
      particleMultiplier: 3.0,
      glowRadius: 80,
      screenTint: '#FF00FF15',
      timeDilation: 0.7,         // Slow-mo effect
      chromatic: 5,              // Chromatic aberration px
    },
  },

  // === CHAIN KILL VISUALS ===
  chainKill: {
    lineColor: '#4488FF',        // Blue lightning
    lineWidth: 3,
    lineGlow: 8,
    fadeTime: 300,
    cascadeDelay: 80,            // ms between chain visuals
    explosionColor: '#FF4444',
    explosionRadius: 30,
  },

  // === SYNERGY ACTIVATION ===
  synergy: {
    discoveryFlash: '#FFD700',   // Gold flash
    discoveryDuration: 500,
    shakeMagnitude: 10,
    freezeFrames: 6,
    textColor: '#FFD700',
    textSize: 24,
    ringColor: '#FFD70088',
    ringExpansion: 150,          // px radius expansion
  },

  // === TRANSCENDENT ABILITY ===
  transcendent: {
    unlockFlash: '#FF00FF',      // Magenta
    unlockDuration: 1000,
    shakeMagnitude: 15,
    freezeFrames: 10,
    screenFlash: '#FFFFFF',
    screenFlashAlpha: 0.5,
    particleBurst: 50,
    textColor: '#FF00FF',
    textSize: 32,
  },

  // === COMBO BROKEN ===
  comboBreak: {
    shatterColor: '#FF4444',
    shatterCount: 12,
    shakeMagnitude: 8,
    soundPitch: 0.5,             // Lower pitch = disappointment
    textColor: '#FF4444',
    textSize: 20,
  },
} as const;

/**
 * Graze System Parameters
 * "RISK-TAKING REWARDED - Near-miss = sparks + chain bonus"
 */
export const GRAZE_JUICE = {
  spark: {
    count: 4,            // Reduced from 8
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
  xp: '#FFE066', // Pollen Gold - bright XP pickups (lighter reward yellow)
  health: '#00FF88', // Vitality Green - healing/health
  ghost: '#A0A0B0', // Warm Gray - death/ghost state
  crisis: '#FF3366', // Pinkish Red - danger/warning (distinct from player orange)

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
  pulsing: { start: '#FF3366', end: '#FF0000' },  // Pinkish-red to red (distinct from player)
  threads: '#FF00FF',  // Magenta
  colossal: '#880000',  // Deep crimson
  linked: '#FF666680',  // Semi-transparent red for linked enemies
};

// =============================================================================
// ABILITY JUICE PARAMETERS - Visual feedback for all 36 abilities
// =============================================================================

/**
 * Ability Juice Context - passed when triggering ability effects
 */
export interface AbilityJuiceContext {
  position: Vector2;
  targetPosition?: Vector2;
  targetEnemyId?: string;
  intensity?: number; // 0-1 for effect strength
  tintColor?: string;
  stacks?: number;    // For stackable effects
}

/**
 * Ability Juice Parameters - color/timing for each ability category
 */
export const ABILITY_JUICE = {
  // MANDIBLE - Red/Orange melee effects
  mandible: {
    bleedColor: '#FF3333',
    stunFlashColor: '#FFFFFF',
    crackColor: '#888888',
    rippleColor: '#4488FF',
    glintColor: '#FFDD00',
  },
  // VENOM - Purple poison effects
  venom: {
    poisonColor: '#9933FF',
    freezeColor: '#6666FF',
    jitterColor: '#FF6666',
    slowColor: '#CC66FF',
  },
  // WING - Cyan/Blue wind effects
  wing: {
    pressureColor: '#88CCFF44',
    buzzColor: '#FFFF0044',
    heatColor: '#FF440022',
    speedColor: '#00FFFF88',  // Cyan for swift wings trail
    trailColor: '#00FFFFCC', // Brighter cyan for movement trail
  },
  // PREDATOR - Yellow/Gold kill effects
  predator: {
    markColor: '#FF990033',
    trophyColor: '#FFD700',
    explosionColor: '#FF3333',  // Pure red for predator kills
    speedColor: '#00FF0088',
  },
  // PHEROMONE - Orange/Yellow aura effects
  pheromone: {
    threatColor: '#FF990022',
    confusionColor: '#9966FF88',
    deathColor: '#66008822',
  },
  // CHITIN - Grey/Red defensive effects
  chitin: {
    spikeColor: '#AAAAAA',
    shellColor: '#DDAA66',
    fragmentColor: '#AA8844',
    burstColor: '#FFD700',
  },
} as const;

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
      | 'apex_wing_blur' | 'apex_wind_dust' | 'apex_speed_line' | 'apex_air' | 'apex_impact' | 'apex_tumble' | 'apex_fury_text'
      | 'xp_sparkle';
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
  // DD-038-3: Afterimage tracking
  afterimages: Afterimage[];
  lastAfterimageTime: number;
}

/**
 * DD-038-3: Afterimage
 * Visual-only ghost silhouettes during apex strike
 * "5 afterimages during strike, spawn every 30ms, fade over 300ms"
 */
export interface Afterimage {
  id: string;
  position: Vector2;
  direction: Vector2;
  alpha: number;        // Starts at 0.7, fades to 0
  lifetime: number;     // Remaining lifetime in ms
  maxLifetime: number;  // 300ms
  scale: number;        // 1.0 for full size
}

// Run 038: Screen effect state (color inversion for impact)
export interface ScreenEffectState {
  invert: boolean;
  duration: number;
  elapsed: number;
  // Circle effect centered on player
  centerX: number;
  centerY: number;
  radius: number;
}

export interface JuiceSystem {
  particles: Particle[];
  shake: ShakeState;
  escalation: EscalationState;
  clutch: ClutchState; // DD-16: Clutch moment state
  freeze: FreezeState; // NEW: Freeze frame state
  killTracker: KillTracker; // NEW: Multi-kill tracking
  apexStrike: ApexStrikeState; // Apex Strike visual state
  screenEffect: ScreenEffectState; // Run 038: Screen effect for impact

  // Reset method - clears all particles and effects for new game
  reset: () => void;

  // Methods
  emitKill: (position: Vector2, enemyType: EnemyType, statusEffect?: 'poison' | 'burn' | 'venom') => void;
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

  // Run 038: Multi-hit combo visual effect (playerPos for circle center)
  emitMultiHit?: (position: Vector2, hitCount: number, playerPos: Vector2) => void;

  // Run 038: Emit combo counter for batched kills
  emitCombo?: (position: Vector2, killCount: number) => void;

  // Run 038: Update existing combo counter
  updateComboCount?: (newCount: number) => void;

  // DD-038-3: Afterimage system methods
  updateAfterimages: (deltaTime: number) => void;
  spawnAfterimage: (position: Vector2, direction: Vector2, gameTime: number) => void;

  // =================================================================
  // POISON DAMAGE SYSTEM - Green floating damage numbers
  // =================================================================
  // Emit poison damage tick - green floating number that floats up and fades
  emitPoisonTick: (position: Vector2, damage: number, stacks: number) => void;

  // =================================================================
  // RUN 039: BUMPER-RAIL COMBO SYSTEM - "Bees are terrain"
  // =================================================================

  // Bumper state tracking
  bumperRail: {
    chainLength: number;
    flowActive: boolean;
    railPoints: Vector2[];
    railFadeTime: number;
    lastBumperTime: number;
  };

  // Bumper hit - pinball PING! with sparkle burst
  emitBumperPing: (position: Vector2, comboCount: number) => void;

  // Rail chain - lightning line connecting hits
  updateRailLine: (points: Vector2[], flowActive: boolean) => void;

  // Flow state - screen effects (speed lines, vignette)
  setFlowState: (active: boolean) => void;

  // Combo text popup - "3x CHAIN!"
  emitComboChain: (position: Vector2, chainLength: number, flowActive: boolean) => void;

  // Chain break - shatter effect + shake
  emitChainBreak: (position: Vector2, reason: 'charged' | 'guard' | 'timeout') => void;

  // Charged bee hit - pain flash
  emitChargedBeeHit: (position: Vector2, damage: number) => void;

  // =================================================================
  // ABILITY JUICE SYSTEM - Visual feedback for all 36 abilities
  // =================================================================

  // Main ability juice dispatcher - routes to specific effect based on ability ID
  emitAbilityJuice: (abilityId: AbilityId, context: AbilityJuiceContext) => void;

  // =================================================================
  // BALL ESCAPE CELEBRATION - "Through the gap. Every time."
  // =================================================================

  // Victory celebration when escaping THE BALL through the gap
  // Spawns victory particles, triggers freeze frame, screen flash
  emitBallEscape: (position: Vector2, gapAngle: number, escapeCount: number) => void;
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
// ABILITY JUICE EMITTERS - Individual effect functions for each ability
// =============================================================================

/**
 * MANDIBLE: Bleed effect - small red tick marks flying off
 */
function createBleedParticles(position: Vector2, color: string): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < 3; i++) {
    particles.push({
      id: `bleed-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { x: position.x + (Math.random() - 0.5) * 20, y: position.y + (Math.random() - 0.5) * 20 },
      velocity: { x: (Math.random() - 0.5) * 30, y: -20 - Math.random() * 20 },
      color,
      size: 3,
      lifetime: 500,
      maxLifetime: 500,
      alpha: 1,
      type: 'burst',
    });
  }
  return particles;
}

/**
 * MANDIBLE: Stun flash - bright white flash on enemy
 */
function createStunFlashParticle(position: Vector2): Particle {
  return {
    id: `stun-flash-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color: ABILITY_JUICE.mandible.stunFlashColor,
    size: 30,
    lifetime: 200,
    maxLifetime: 200,
    alpha: 0.9,
    type: 'ring',
    text: '30',
  };
}

/**
 * MANDIBLE: Armor crack - grey shards flying off
 */
function createArmorCrackParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < 4; i++) {
    const angle = (i / 4) * Math.PI * 2;
    particles.push({
      id: `crack-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: { x: Math.cos(angle) * 40, y: Math.sin(angle) * 40 },
      color: ABILITY_JUICE.mandible.crackColor,
      size: 4,
      lifetime: 300,
      maxLifetime: 300,
      alpha: 1,
      type: 'fragment',
    });
  }
  return particles;
}

/**
 * MANDIBLE: Knockback ripple - expanding blue ring
 */
function createKnockbackRippleParticle(position: Vector2): Particle {
  return {
    id: `ripple-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color: ABILITY_JUICE.mandible.rippleColor,
    size: 10,
    lifetime: 300,
    maxLifetime: 300,
    alpha: 0.8,
    type: 'ring',
    text: '40', // Max size for ring expansion
  };
}

/**
 * MANDIBLE: Sawtooth glint - golden spark on 5th hit
 */
function createSawtoothGlintParticle(position: Vector2): Particle {
  return {
    id: `glint-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { x: position.x, y: position.y - 10 },
    velocity: { x: 0, y: -30 },
    color: ABILITY_JUICE.mandible.glintColor,
    size: 8,
    lifetime: 400,
    maxLifetime: 400,
    alpha: 1,
    type: 'burst',
  };
}

/**
 * VENOM: Poison drip - purple drops falling
 */
function createPoisonDripParticle(position: Vector2, color: string): Particle {
  return {
    id: `poison-drip-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: (Math.random() - 0.5) * 10, y: 20 + Math.random() * 20 },
    color,
    size: 5,
    lifetime: 600,
    maxLifetime: 600,
    alpha: 0.9,
    type: 'drip',
    gravity: 150,
  };
}

/**
 * VENOM: Freeze flash - purple/blue brief flash
 */
function createFreezeFlashParticle(position: Vector2, color: string): Particle {
  return {
    id: `freeze-flash-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color,
    size: 25,
    lifetime: 150,
    maxLifetime: 150,
    alpha: 0.8,
    type: 'ring',
    text: '25',
  };
}

/**
 * VENOM: Jitter effect - erratic small particles
 */
function createJitterParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < 4; i++) {
    particles.push({
      id: `jitter-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { x: position.x + (Math.random() - 0.5) * 30, y: position.y + (Math.random() - 0.5) * 30 },
      velocity: { x: (Math.random() - 0.5) * 100, y: (Math.random() - 0.5) * 100 },
      color: ABILITY_JUICE.venom.jitterColor,
      size: 2,
      lifetime: 100,
      maxLifetime: 100,
      alpha: 1,
      type: 'burst',
    });
  }
  return particles;
}

/**
 * WING: Pressure wave - expanding translucent ring
 */
function createPressureWaveParticle(position: Vector2): Particle {
  return {
    id: `pressure-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color: ABILITY_JUICE.wing.pressureColor,
    size: 50,
    lifetime: 500,
    maxLifetime: 500,
    alpha: 0.4,
    type: 'ring',
    text: '80', // Expand to 80px
  };
}

/**
 * WING: Buzz ring - yellow vibrating ring
 */
function createBuzzRingParticle(position: Vector2): Particle {
  return {
    id: `buzz-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color: ABILITY_JUICE.wing.buzzColor,
    size: 20,
    lifetime: 300,
    maxLifetime: 300,
    alpha: 0.5,
    type: 'ring',
    text: '30',
  };
}

/**
 * WING: Heat shimmer - wavy distortion effect particles
 */
function createHeatShimmerParticle(position: Vector2): Particle {
  return {
    id: `heat-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { x: position.x + (Math.random() - 0.5) * 20, y: position.y },
    velocity: { x: 0, y: -10 },
    color: ABILITY_JUICE.wing.heatColor,
    size: 15,
    lifetime: 800,
    maxLifetime: 800,
    alpha: 0.3,
    type: 'burst',
  };
}

/**
 * WING: Speed lines - horizontal motion blur lines
 */
function createSpeedLineParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < 3; i++) {
    particles.push({
      id: `speed-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { x: position.x - 20, y: position.y + (i - 1) * 10 },
      velocity: { x: -60, y: 0 },
      color: ABILITY_JUICE.wing.speedColor,
      size: 2,
      lifetime: 200,
      maxLifetime: 200,
      alpha: 0.6,
      type: 'trail',
    });
  }
  return particles;
}

/**
 * PREDATOR: Ground stain - persistent orange mark
 */
function createGroundStainParticle(position: Vector2): Particle {
  return {
    id: `stain-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color: ABILITY_JUICE.predator.markColor,
    size: 30,
    lifetime: 5000, // Long lasting
    maxLifetime: 5000,
    alpha: 0.5,
    type: 'pool',
    isPool: true,
  };
}

/**
 * PREDATOR: Trophy flash - golden upward spark
 */
function createTrophyFlashParticle(position: Vector2): Particle {
  return {
    id: `trophy-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { x: position.x, y: position.y - 20 },
    velocity: { x: 0, y: -20 },
    color: ABILITY_JUICE.predator.trophyColor,
    size: 12,
    lifetime: 500,
    maxLifetime: 500,
    alpha: 1,
    type: 'burst',
  };
}

/**
 * PREDATOR: Mini explosion - radial particle burst
 */
function createMiniExplosionParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * Math.PI * 2;
    particles.push({
      id: `explosion-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: { x: Math.cos(angle) * 60, y: Math.sin(angle) * 60 },
      color: ABILITY_JUICE.predator.explosionColor,
      size: 5,
      lifetime: 300,
      maxLifetime: 300,
      alpha: 1,
      type: 'burst',
    });
  }
  return particles;
}

/**
 * PHEROMONE: Aura glow - soft expanding colored ring
 */
function createAuraGlowParticle(position: Vector2, color: string): Particle {
  return {
    id: `aura-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color: color + '22', // Add transparency
    size: 30,
    lifetime: 100,
    maxLifetime: 100,
    alpha: 0.3,
    type: 'ring',
    text: '40',
  };
}

/**
 * PHEROMONE: Confusion swirl - orbiting particles
 */
function createConfusionSwirlParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < 5; i++) {
    const angle = Math.random() * Math.PI * 2;
    particles.push({
      id: `swirl-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { x: position.x + Math.cos(angle) * 20, y: position.y + Math.sin(angle) * 20 },
      velocity: { x: Math.cos(angle + Math.PI / 2) * 30, y: Math.sin(angle + Math.PI / 2) * 30 },
      color: ABILITY_JUICE.pheromone.confusionColor,
      size: 6,
      lifetime: 1000,
      maxLifetime: 1000,
      alpha: 0.7,
      type: 'apex_wind_dust', // Reuse swirling particle type
    });
  }
  return particles;
}

/**
 * PHEROMONE: Seeping effect - slow expanding dark pool
 */
function createSeepingParticle(position: Vector2): Particle {
  return {
    id: `seep-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: 0, y: 0 },
    color: ABILITY_JUICE.pheromone.deathColor,
    size: 40,
    lifetime: 3000,
    maxLifetime: 3000,
    alpha: 0.4,
    type: 'pool',
    isPool: true,
  };
}

/**
 * CHITIN: Spike plink - small grey shard flying off
 */
function createSpikePlinkParticle(position: Vector2): Particle {
  return {
    id: `spike-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: (Math.random() - 0.5) * 40, y: -30 },
    color: ABILITY_JUICE.chitin.spikeColor,
    size: 3,
    lifetime: 300,
    maxLifetime: 300,
    alpha: 1,
    type: 'fragment',
  };
}

/**
 * CHITIN: Shell burst - radial chitin fragments
 */
function createShellBurstParticles(position: Vector2): Particle[] {
  const particles: Particle[] = [];
  for (let i = 0; i < 12; i++) {
    const angle = (i / 12) * Math.PI * 2;
    particles.push({
      id: `shell-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
      position: { ...position },
      velocity: { x: Math.cos(angle) * 80, y: Math.sin(angle) * 80 },
      color: ABILITY_JUICE.chitin.shellColor,
      size: 8,
      lifetime: 500,
      maxLifetime: 500,
      alpha: 1,
      type: 'fragment',
    });
  }
  return particles;
}

/**
 * CHITIN: Shell fragment - single shard flying off
 */
function createShellFragmentParticle(position: Vector2): Particle {
  return {
    id: `frag-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    position: { ...position },
    velocity: { x: (Math.random() - 0.5) * 60, y: -40 - Math.random() * 20 },
    color: ABILITY_JUICE.chitin.fragmentColor,
    size: 6,
    lifetime: 600,
    maxLifetime: 600,
    alpha: 1,
    type: 'fragment',
  };
}

// =============================================================================
// Reserved helper functions (suppress unused warnings - will be used when abilities are fully wired)
// =============================================================================

void createArmorCrackParticles;
void createSawtoothGlintParticle;
void createJitterParticles;

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
    // Run 038: Screen effect (color inversion) for impact moments
    screenEffect: {
      invert: false,
      duration: 0,
      elapsed: 0,
      centerX: 0,
      centerY: 0,
      radius: 100,
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
      // DD-038-3: Afterimage state
      afterimages: [] as Afterimage[],
      lastAfterimageTime: 0,
    },
    // Run 039: Bumper-Rail combo state
    bumperRail: {
      chainLength: 0,
      flowActive: false,
      railPoints: [] as Vector2[],
      railFadeTime: 0,
      lastBumperTime: 0,
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
    get bumperRail() {
      return state.bumperRail;
    },
    get screenEffect() {
      return state.screenEffect;
    },

    /**
     * Reset juice system state for a new game run
     * Clears all particles, effects, and visual state to prevent artifacts
     * from accumulating between games
     */
    reset() {
      // Clear all particles
      state.particles.length = 0;

      // Reset shake
      state.shake = {
        intensity: 0,
        duration: 0,
        elapsed: 0,
        offset: { x: 0, y: 0 },
      };

      // Reset escalation
      state.escalation = {
        wave: 1,
        combo: 0,
        comboTimer: 0,
        healthFraction: 1,
        multiplier: 1,
      };

      // Reset clutch moment
      state.clutch = {
        active: false,
        level: null,
        timeScale: 1.0,
        zoom: 1.0,
        remaining: 0,
        duration: 0,
      };

      // Reset freeze frames
      state.freeze = {
        active: false,
        framesRemaining: 0,
        type: null,
      };

      // Reset screen effect
      state.screenEffect = {
        invert: false,
        duration: 0,
        elapsed: 0,
        centerX: 0,
        centerY: 0,
        radius: 100,
      };

      // Reset kill tracker
      state.killTracker = {
        recentKills: 0,
        windowStart: 0,
        windowDuration: 150,
        lastKillTime: 0,
      };

      // Reset apex strike visual state
      state.apexStrike = {
        phase: 'none',
        lockProgress: 0,
        strikeProgress: 0,
        direction: { x: 1, y: 0 },
        bloodlust: 0,
        chainAvailable: false,
        startPosition: { x: 0, y: 0 },
        targetPosition: { x: 0, y: 0 },
        afterimages: [],
        lastAfterimageTime: 0,
      };
    },

    emitKill(position: Vector2, enemyType: EnemyType, statusEffect?: 'poison' | 'burn' | 'venom') {
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

      // Run 040: Status effect color override for death particles
      // Poisoned enemies explode GREEN, burned enemies ORANGE, venom enemies PURPLE
      const statusEffectColors: Record<string, string> = {
        poison: '#00FF00',  // Bright green
        burn: '#FF6600',    // Orange/fire
        venom: '#8B00FF',   // Purple
      };
      const particleColor = statusEffect ? statusEffectColors[statusEffect] : COLORS.enemy;

      // Burst particles (with status effect color if applicable)
      const burstParticles = createBurstParticles(
        position,
        particleColor,
        count,
        state.escalation.multiplier
      );
      state.particles.push(...burstParticles);

      // XP text particle (+50% XP boost)
      const xpValues: Record<import('../types').BeeType, number> = {
        worker: 15,
        scout: 23,
        guard: 38,
        propolis: 30,
        royal: 150,
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
      // Main trail particle toward XP bar (top of screen)
      state.particles.push(
        createParticle(position, 'trail', COLORS.xp, {
          velocity: { x: 0, y: -200 },
          lifetime: 600,
          maxLifetime: 600,
          size: 6,
        })
      );

      // XP sparkle trail - multiple sparkles that fan out then converge upward
      const sparkleCount = Math.min(5, Math.ceil(amount / 5)); // More sparkles for bigger XP
      for (let i = 0; i < sparkleCount; i++) {
        const angle = ((i / sparkleCount) - 0.5) * Math.PI * 0.6; // Spread in a 108-degree arc
        const speed = 100 + Math.random() * 50;
        const delay = i * 30; // Stagger spawn slightly

        // Create sparkle with initial outward burst, then upward pull
        setTimeout(() => {
          state.particles.push({
            id: `xp-sparkle-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
            position: { ...position },
            velocity: {
              x: Math.sin(angle) * speed,
              y: -150 - Math.random() * 100, // Upward with variance
            },
            color: i % 2 === 0 ? COLORS.xp : '#FFFFFF', // Alternate gold and white
            size: 3 + Math.random() * 2,
            lifetime: 400 + Math.random() * 200,
            maxLifetime: 500,
            alpha: 1,
            type: 'xp_sparkle',
          });
        }, delay);
      }

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

      // GRAZE SOUND DISABLED - system surface removed
      // const sound = getSoundEngine();
      // sound.play('graze', { pitch: 1.2 + chainCount * 0.05 });
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

      // GRAZE BONUS SOUND DISABLED - system surface removed
      // const sound = getSoundEngine();
      // sound.play('graze', { pitch: 1.5, volume: 0.36 });
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
      // DD-038-3: Reset afterimage state for new strike
      state.apexStrike.afterimages = [];
      state.apexStrike.lastAfterimageTime = 0;

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
     * Run 038: Emit Multi-Hit combo visual effect
     * Called when apex strike hits 2+ enemies simultaneously
     * Triggers actual freeze frame + circle inversion centered on player
     */
    emitMultiHit(position: Vector2, hitCount: number, playerPos: Vector2) {
      // Big expanding ring showing the combo
      state.particles.push({
        id: `multi-hit-ring-${Date.now()}`,
        position: { ...position },
        velocity: { x: 0, y: 0 },
        color: hitCount >= 3 ? '#FFD700' : '#FF8800', // Gold for 3+, orange for 2
        size: 60,
        lifetime: 400,
        maxLifetime: 400,
        alpha: 0.8,
        type: 'ring',
        text: '60',
      });

      // TRIGGER ACTUAL FREEZE - this sets timeScale to 0
      // More enemies = longer freeze (multi for 2-3, massacre for 4+)
      if (hitCount >= 4) {
        this.triggerFreeze('massacre');
      } else {
        this.triggerFreeze('multi');
      }

      // Run 038: Circle inversion centered on PLAYER (not hit position)
      // This creates a "time bubble" effect around the player
      const effectRadius = 100 + hitCount * 25;
      state.screenEffect = {
        invert: true,
        duration: hitCount >= 4 ? 140 : hitCount >= 3 ? 110 : 80,
        elapsed: 0,
        centerX: playerPos.x,  // Center on player, not hit position
        centerY: playerPos.y,
        radius: effectRadius,
      };

      // BIG DRAMATIC text with count
      const comboText = hitCount >= 3 ? `${hitCount}x CARNAGE!` : 'DOUBLE KILL!';
      state.particles.push({
        id: `multi-hit-text-${Date.now()}`,
        position: { x: position.x, y: position.y - 40 },
        velocity: { x: 0, y: -60 },
        color: hitCount >= 3 ? '#FFD700' : '#FF8800',
        size: hitCount >= 3 ? 28 : 24,  // BIGGER text
        lifetime: 1200,  // Longer duration
        maxLifetime: 1200,
        alpha: 1,
        type: 'text',
        text: comboText,
      });

      // LOTS of impact particles for multi-hit
      const particleCount = hitCount * 8;  // More particles
      for (let i = 0; i < particleCount; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = 150 + Math.random() * 250;  // Faster
        state.particles.push({
          id: `multi-hit-spark-${Date.now()}-${i}`,
          position: { ...position },
          velocity: {
            x: Math.cos(angle) * speed,
            y: Math.sin(angle) * speed,
          },
          color: hitCount >= 3 ? '#FFD700' : '#FF8800',
          size: 5 + Math.random() * 5,  // Bigger particles
          lifetime: 400 + Math.random() * 300,
          maxLifetime: 700,
          alpha: 1,
          type: 'burst',
        });
      }

      // STRONG screen shake for multi-hit
      this.triggerShake(15 + hitCount * 5, 250);  // Much stronger

      // Sound feedback - lower pitch for more IMPACT
      const sound = getSoundEngine();
      sound.play('hit', { pitch: 0.3 + hitCount * 0.05, volume: 1.2 });
    },

    /**
     * Run 038: Emit combo counter for batched kills
     * Shows "Nx KILL" text that floats up
     * Run 038 FIX: Now includes circle inversion effect (moved from emitMultiHit)
     */
    emitCombo(position: Vector2, killCount: number) {
      // Only show for 2+ kills (called from useGameLoop with this check)
      const comboText = `${killCount}x MULTI-KILL!`;
      const color = killCount >= 4 ? '#FFD700' : '#FF8800';
      const size = Math.min(32, 20 + killCount * 2);

      state.particles.push({
        id: `combo-text-${Date.now()}`,
        position: { x: position.x, y: position.y - 50 },
        velocity: { x: 0, y: -30 },
        color,
        size,
        lifetime: 1500,
        maxLifetime: 1500,
        alpha: 1,
        type: 'text',
        text: comboText,
      });

      // Run 038 FIX: Circle inversion effect at batch time (moved from emitMultiHit)
      // This creates the dramatic freeze-frame feel when the combo is revealed
      const effectRadius = 100 + killCount * 25;
      state.screenEffect = {
        invert: true,
        duration: killCount >= 4 ? 140 : killCount >= 3 ? 110 : 80,
        elapsed: 0,
        centerX: position.x,
        centerY: position.y,
        radius: effectRadius,
      };

      // Screen shake scales with combo
      this.triggerShake(10 + killCount * 3, 200);

      // Sound - use massacre sound for big combos
      const sound = getSoundEngine();
      if (killCount >= 5) {
        sound.play('massacre', { volume: 0.9 });
      } else {
        sound.play('kill', { pitch: 0.5 + killCount * 0.1, volume: 1.0 });
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

    // =========================================================================
    // DD-038-3: AFTERIMAGE SYSTEM - "5 ghostly silhouettes during strike"
    // =========================================================================

    /**
     * Update all active afterimages (fade and remove expired)
     * Called every frame during strike phase
     */
    updateAfterimages(deltaTime: number) {
      const config = APEX_STRIKE.strike.afterimages;

      // Update existing afterimages - fade based on remaining lifetime
      state.apexStrike.afterimages = state.apexStrike.afterimages.filter(img => {
        img.lifetime -= deltaTime;
        // Alpha fades linearly from startAlpha to 0
        img.alpha = (img.lifetime / img.maxLifetime) * config.startAlpha;
        return img.lifetime > 0;
      });
    },

    /**
     * Spawn a new afterimage at the current position
     * Respects spawn interval and max count from config
     */
    spawnAfterimage(position: Vector2, direction: Vector2, gameTime: number) {
      const config = APEX_STRIKE.strike.afterimages;

      // Only spawn during strike phase
      if (state.apexStrike.phase !== 'strike') {
        return;
      }

      // Check spawn interval
      if (gameTime - state.apexStrike.lastAfterimageTime < config.spawnInterval) {
        return;
      }

      // Check max count
      if (state.apexStrike.afterimages.length >= config.count) {
        return;
      }

      // Spawn new afterimage
      state.apexStrike.afterimages.push({
        id: `afterimage-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        position: { ...position },
        direction: { ...direction },
        alpha: config.startAlpha,
        lifetime: config.fadeTime,
        maxLifetime: config.fadeTime,
        scale: config.scale,
      });

      state.apexStrike.lastAfterimageTime = gameTime;
    },

    // =================================================================
    // POISON TICK SYSTEM - Green floating damage numbers
    // "Poison ticks are satisfying when you SEE the damage"
    // =================================================================
    emitPoisonTick(position: Vector2, damage: number, stacks: number) {
      // Create green damage text particle
      // Damage number is smaller than regular damage and green colored
      const poisonColor = '#00FF00';  // Bright green

      // Add slight random offset so multiple ticks don't stack exactly
      const offsetX = (Math.random() - 0.5) * 20;
      const offsetY = (Math.random() - 0.5) * 10;

      // Create the damage text particle
      const damageText = Math.round(damage).toString();
      state.particles.push({
        id: `poison-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
        position: { x: position.x + offsetX, y: position.y + offsetY - 10 },
        velocity: { x: 0, y: -60 },  // Float upward (slower than regular damage)
        color: poisonColor,
        size: 12 + Math.min(stacks, 5) * 1,  // Size scales slightly with stacks (12-17)
        lifetime: 600,
        maxLifetime: 600,
        alpha: 0.9,
        type: 'text',
        text: damageText,
      });

      // Add small green drip particles for visual flair (1-2 based on stacks)
      const dripCount = Math.min(1 + Math.floor(stacks / 3), 2);
      for (let i = 0; i < dripCount; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = 20 + Math.random() * 30;
        state.particles.push({
          id: `poison-drip-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
          position: { x: position.x + offsetX, y: position.y + offsetY },
          velocity: {
            x: Math.cos(angle) * speed,
            y: -20 + Math.sin(angle) * speed * 0.5,  // Slight upward bias
          },
          color: poisonColor,
          size: 2 + Math.random() * 2,
          lifetime: 300,
          maxLifetime: 300,
          alpha: 0.7,
          type: 'burst',
        });
      }
    },

    // =================================================================
    // RUN 039: BUMPER-RAIL COMBO SYSTEM
    // "Bees are not obstacles. Bees are terrain."
    // =================================================================

    /**
     * Emit bumper ping effect - pinball PING! with sparkle burst
     */
    emitBumperPing(position: Vector2, comboCount: number) {
      const config = BUMPER_JUICE.bumperPing;

      // Scale effect with combo count
      const comboScale = Math.min(1 + comboCount * 0.1, 1.5);

      // Create sparkle burst
      for (let i = 0; i < config.count; i++) {
        const angle = (i / config.count) * Math.PI * 2 + Math.random() * 0.3;
        const speed = config.velocity * (0.8 + Math.random() * 0.4) * comboScale;
        const isAlt = Math.random() > 0.7; // 30% white sparkles

        state.particles.push({
          id: `bumper-${Date.now()}-${i}`,
          position: { ...position },
          velocity: {
            x: Math.cos(angle) * speed,
            y: Math.sin(angle) * speed,
          },
          color: isAlt ? config.colorAlt : config.color,
          size: config.size * comboScale,
          lifetime: config.lifespan,
          maxLifetime: config.lifespan,
          alpha: 1.0,
          type: 'burst',
        });
      }

      // Update bumper state
      state.bumperRail.chainLength = comboCount;
      state.bumperRail.lastBumperTime = Date.now();

      // Play sound (using existing sound engine)
      const soundEngine = getSoundEngine();
      if (soundEngine) {
        // Use kill sound for bumper impact, pitch increases with combo count
        soundEngine.play('kill', { pitch: 1 + comboCount * 0.1 });
      }

      // Small screen shake for impact feel
      const shakeIntensity = 2 + comboCount * 0.5;
      state.shake.intensity = Math.max(state.shake.intensity, shakeIntensity);
      state.shake.duration = 80;
      state.shake.elapsed = 0;
    },

    /**
     * Update rail line - lightning trail connecting hit positions
     */
    updateRailLine(points: Vector2[], flowActive: boolean) {
      state.bumperRail.railPoints = [...points];
      state.bumperRail.flowActive = flowActive;
      state.bumperRail.railFadeTime = BUMPER_JUICE.railLine.fadeTime;

      // Create lightning particles along the rail
      if (points.length >= 2) {
        const config = BUMPER_JUICE.railLine;
        const color = flowActive ? config.colorFlow : config.color;

        // Add lightning spark at each point
        for (const point of points) {
          state.particles.push({
            id: `rail-spark-${Date.now()}-${Math.random().toString(36).slice(2, 5)}`,
            position: { ...point },
            velocity: { x: 0, y: -20 },
            color,
            size: 6,
            lifetime: 150,
            maxLifetime: 150,
            alpha: 1.0,
            type: 'burst',
          });
        }
      }
    },

    /**
     * Set flow state - activate/deactivate flow visual effects
     */
    setFlowState(active: boolean) {
      const wasActive = state.bumperRail.flowActive;
      state.bumperRail.flowActive = active;

      if (active && !wasActive) {
        // Just activated - emit burst of particles
        const centerX = 400; // Approximate screen center
        const centerY = 300;
        const config = BUMPER_JUICE.flowState;

        for (let i = 0; i < 8; i++) {
          const angle = (i / 8) * Math.PI * 2;
          state.particles.push({
            id: `flow-burst-${Date.now()}-${i}`,
            position: { x: centerX, y: centerY },
            velocity: {
              x: Math.cos(angle) * 200,
              y: Math.sin(angle) * 200,
            },
            color: config.speedLineColor,
            size: 8,
            lifetime: 400,
            maxLifetime: 400,
            alpha: 0.8,
            type: 'burst',
          });
        }

        // Trigger small screen effect
        state.screenEffect.invert = false;
        state.screenEffect.duration = 100;
        state.screenEffect.elapsed = 0;
      }
    },

    /**
     * Emit combo chain text - "3x CHAIN!" popup
     */
    emitComboChain(position: Vector2, chainLength: number, flowActive: boolean) {
      const config = BUMPER_JUICE.comboText;
      const color = flowActive ? config.colorFlow : config.color;

      // Create floating text particle
      state.particles.push({
        id: `chain-text-${Date.now()}`,
        position: { x: position.x, y: position.y - 30 },
        velocity: { x: 0, y: -config.floatSpeed },
        color,
        size: config.size,
        lifetime: config.duration,
        maxLifetime: config.duration,
        alpha: 1.0,
        type: 'text',
        text: `${chainLength}x CHAIN!`,
      });

      // Add celebration sparkles around the text
      for (let i = 0; i < 6; i++) {
        const angle = Math.random() * Math.PI * 2;
        const dist = 20 + Math.random() * 20;
        state.particles.push({
          id: `chain-sparkle-${Date.now()}-${i}`,
          position: {
            x: position.x + Math.cos(angle) * dist,
            y: position.y - 30 + Math.sin(angle) * dist,
          },
          velocity: {
            x: Math.cos(angle) * 40,
            y: -50 + Math.sin(angle) * 20,
          },
          color: config.colorFlow,
          size: 3,
          lifetime: 400,
          maxLifetime: 400,
          alpha: 0.9,
          type: 'burst',
        });
      }
    },

    /**
     * Emit chain break effect - shatter + shake + sad sound
     */
    emitChainBreak(position: Vector2, reason: 'charged' | 'guard' | 'timeout') {
      const config = BUMPER_JUICE.chainBreak;

      // Screen shake
      state.shake.intensity = config.shakeIntensity;
      state.shake.duration = config.shakeDuration;
      state.shake.elapsed = 0;

      // Shatter particles
      for (let i = 0; i < config.shatterCount; i++) {
        const angle = (i / config.shatterCount) * Math.PI * 2;
        const speed = 100 + Math.random() * 80;
        state.particles.push({
          id: `chain-break-${Date.now()}-${i}`,
          position: { ...position },
          velocity: {
            x: Math.cos(angle) * speed,
            y: Math.sin(angle) * speed,
          },
          color: config.color,
          size: 5,
          lifetime: 300,
          maxLifetime: 300,
          alpha: 1.0,
          type: 'burst',
        });
      }

      // "BREAK!" text based on reason
      const breakText = reason === 'charged' ? 'SHOCKED!' :
                        reason === 'guard' ? 'BLOCKED!' : 'TIMEOUT!';

      state.particles.push({
        id: `break-text-${Date.now()}`,
        position: { x: position.x, y: position.y - 20 },
        velocity: { x: 0, y: -40 },
        color: config.color,
        size: 18,
        lifetime: 600,
        maxLifetime: 600,
        alpha: 1.0,
        type: 'text',
        text: breakText,
      });

      // Reset bumper state
      state.bumperRail.chainLength = 0;
      state.bumperRail.flowActive = false;
      state.bumperRail.railPoints = [];
    },

    /**
     * Emit charged bee hit effect - pain flash + damage
     */
    emitChargedBeeHit(position: Vector2, damage: number) {
      const config = BUMPER_JUICE.chargedBee;

      // Big screen flash
      state.screenEffect.invert = true;
      state.screenEffect.duration = 150;
      state.screenEffect.elapsed = 0;
      state.screenEffect.centerX = position.x;
      state.screenEffect.centerY = position.y;
      state.screenEffect.radius = 200;

      // Screen shake
      state.shake.intensity = 10;
      state.shake.duration = 200;
      state.shake.elapsed = 0;

      // Damage number
      state.particles.push({
        id: `charged-damage-${Date.now()}`,
        position: { x: position.x, y: position.y - 10 },
        velocity: { x: 0, y: -80 },
        color: config.glowColor,
        size: 24,
        lifetime: 800,
        maxLifetime: 800,
        alpha: 1.0,
        type: 'text',
        text: `-${Math.round(damage)}`,
      });

      // Electrical sparks
      for (let i = 0; i < config.sparkCount * 2; i++) {
        const angle = Math.random() * Math.PI * 2;
        const speed = 150 + Math.random() * 100;
        state.particles.push({
          id: `shock-spark-${Date.now()}-${i}`,
          position: { ...position },
          velocity: {
            x: Math.cos(angle) * speed,
            y: Math.sin(angle) * speed,
          },
          color: config.sparkColor,
          size: 4,
          lifetime: 200,
          maxLifetime: 200,
          alpha: 1.0,
          type: 'burst',
        });
      }
    },

    // =================================================================
    // ABILITY JUICE SYSTEM - Visual feedback for all 36 abilities
    // "Each ability = 5-10% toward godlike" - make them FEEL it
    // =================================================================

    /**
     * Main ability juice dispatcher
     * Routes ability triggers to their specific visual effects
     */
    emitAbilityJuice(abilityId: AbilityId, context: AbilityJuiceContext) {
      const { position, intensity = 1, tintColor, stacks = 1 } = context;
      void intensity; // Reserved for intensity-scaled effects in future
      void stacks;    // Reserved for stack-scaled effects in future

      switch (abilityId) {
        // ===========================================================
        // DAMAGE (6) - Red/Orange melee effects (formerly MANDIBLE)
        // ===========================================================
        case 'sharpened_mandibles':
          // Orange slash marks - sharpened damage
          state.particles.push(...createBleedParticles(position, tintColor || ABILITY_JUICE.mandible.bleedColor));
          break;

        case 'crushing_bite':
          // Heavy impact burst with shockwave
          state.particles.push(createKnockbackRippleParticle(position));
          this.triggerShake(4, 100);
          break;

        case 'venomous_strike':
          // Green venom drip
          state.particles.push(createPoisonDripParticle(position, tintColor || '#88FF00'));
          break;

        case 'double_strike':
          // Twin slash effect
          state.particles.push(...createBleedParticles(position, tintColor || '#FF4488'));
          state.particles.push(...createBleedParticles(
            { x: position.x + 10, y: position.y },
            tintColor || '#FF4488'
          ));
          break;

        case 'savage_blow':
          // Red fire burst on low-HP enemy
          state.particles.push(...createMiniExplosionParticles(position));
          this.triggerShake(3, 80);
          break;

        case 'giant_killer':
          // Blue crosshair lock effect
          state.particles.push(createAuraGlowParticle(position, tintColor || '#00AAFF'));
          break;

        // ===========================================================
        // SPEED (6) - Cyan/Blue speed effects
        // ===========================================================
        case 'quick_strikes':
        case 'frenzy':
        case 'hunters_rush':
        case 'berserker_pace':
        case 'bullet_time':
          // Speed boost lines
          state.particles.push(...createSpeedLineParticles(position));
          break;

        case 'swift_wings':
          // Bright cyan wing trail - more visible than generic speed lines
          for (let i = 0; i < 4; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 20 + Math.random() * 30;
            state.particles.push({
              id: `wing-trail-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
              position: { ...position },
              velocity: { x: Math.cos(angle) * speed - 40, y: Math.sin(angle) * speed },
              color: ABILITY_JUICE.wing.trailColor,
              size: 4 + Math.random() * 3,
              lifetime: 350,
              maxLifetime: 350,
              alpha: 0.8,
              type: 'trail',
            });
          }
          break;

        // ===========================================================
        // DEFENSE (6) - Green heal / Gold shield effects
        // ===========================================================
        case 'thick_carapace':
        case 'hardened_shell':
          // Golden shell shimmer
          state.particles.push(createShellFragmentParticle(position));
          break;

        case 'regeneration':
          // Green healing particles rising up
          for (let i = 0; i < 3; i++) {
            state.particles.push({
              id: `regen-${Date.now()}-${i}`,
              position: { x: position.x + (Math.random() - 0.5) * 20, y: position.y },
              velocity: { x: (Math.random() - 0.5) * 10, y: -40 - Math.random() * 20 },
              color: '#66FF66',
              size: 4,
              lifetime: 600,
              maxLifetime: 600,
              alpha: 0.8,
              type: 'burst',
            });
          }
          break;

        case 'lifesteal':
          // Red/crimson health drain particles flowing to player
          for (let i = 0; i < 4; i++) {
            const angle = (i / 4) * Math.PI * 2;
            state.particles.push({
              id: `lifesteal-${Date.now()}-${i}`,
              position: { ...position },
              velocity: { x: Math.cos(angle) * 30, y: Math.sin(angle) * 30 - 20 },
              color: '#FF3333',
              size: 5,
              lifetime: 400,
              maxLifetime: 400,
              alpha: 0.9,
              type: 'burst',
            });
          }
          break;

        case 'last_stand':
          // Red pulsing defensive aura
          state.particles.push(createAuraGlowParticle(position, '#FF0000'));
          this.triggerShake(2, 50);
          break;

        case 'second_wind':
          // Golden resurrection burst
          for (let i = 0; i < 12; i++) {
            const angle = (i / 12) * Math.PI * 2;
            state.particles.push({
              id: `second-wind-${Date.now()}-${i}`,
              position: { ...position },
              velocity: { x: Math.cos(angle) * 80, y: Math.sin(angle) * 80 },
              color: '#FFD700',
              size: 6,
              lifetime: 500,
              maxLifetime: 500,
              alpha: 1,
              type: 'burst',
            });
          }
          this.triggerShake(8, 200);
          this.triggerFreeze('massacre');
          break;

        // ===========================================================
        // SPECIAL (6) - Unique powerful effects
        // ===========================================================
        case 'critical_sting':
          // Yellow/white crit flash
          state.particles.push({
            id: `crit-${Date.now()}`,
            position: { ...position },
            velocity: { x: 0, y: -30 },
            color: '#FFFF00',
            size: 12,
            lifetime: 200,
            maxLifetime: 200,
            alpha: 1,
            type: 'burst',
          });
          this.triggerShake(3, 80);
          break;

        case 'execution':
          // Red skull / instant kill effect
          state.particles.push(...createMiniExplosionParticles(position));
          this.triggerShake(4, 100);
          break;

        case 'sweeping_arc':
          // Wide arc slash visual
          state.particles.push(...createBleedParticles(position, '#FF8800'));
          break;

        case 'chain_lightning':
          // Electric blue lightning particles
          for (let i = 0; i < 6; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 60 + Math.random() * 40;
            state.particles.push({
              id: `lightning-${Date.now()}-${i}`,
              position: { ...position },
              velocity: { x: Math.cos(angle) * speed, y: Math.sin(angle) * speed },
              color: '#00FFFF',
              size: 3,
              lifetime: 150,
              maxLifetime: 150,
              alpha: 1,
              type: 'burst',
            });
          }
          // Add central flash
          state.particles.push({
            id: `lightning-flash-${Date.now()}`,
            position: { ...position },
            velocity: { x: 0, y: 0 },
            color: '#FFFFFF',
            size: 15,
            lifetime: 100,
            maxLifetime: 100,
            alpha: 0.8,
            type: 'burst',
          });
          break;

        case 'momentum':
          // Orange momentum buildup particles
          state.particles.push(...createSpeedLineParticles(position));
          state.particles.push(createAuraGlowParticle(position, '#FF6600'));
          break;

        case 'glass_cannon':
        case 'glass_cannon_mastery':
          // Red cracked energy
          state.particles.push(createAuraGlowParticle(position, '#FF3333'));
          break;

        case 'graze_frenzy':
          // Purple graze particles
          state.particles.push(createAuraGlowParticle(position, '#AA00FF'));
          break;

        case 'thermal_momentum':
          // Orange/red heat buildup
          state.particles.push(createHeatShimmerParticle(position));
          state.particles.push(createAuraGlowParticle(position, '#FF4400'));
          break;

        case 'execution_chain':
          // Red chain effect
          state.particles.push(...createBleedParticles(position, '#CC0000'));
          break;

        case 'venom_architect':
          // Green venom explosion
          for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI * 2;
            state.particles.push({
              id: `venom-explode-${Date.now()}-${i}`,
              position: { ...position },
              velocity: { x: Math.cos(angle) * 70, y: Math.sin(angle) * 70 },
              color: '#00FF00',
              size: 5,
              lifetime: 300,
              maxLifetime: 300,
              alpha: 1,
              type: 'burst',
            });
          }
          this.triggerShake(5, 150);
          break;

        // ===========================================================
        // PHEROMONE (9) - Purple poison and debuff effects
        // ===========================================================
        case 'trace_venom':
          // Purple drip - poison applied
          state.particles.push(createPoisonDripParticle(position, tintColor || ABILITY_JUICE.venom.poisonColor));
          break;

        case 'paralytic_microdose':
          // Purple/blue freeze flash
          state.particles.push(createFreezeFlashParticle(position, tintColor || ABILITY_JUICE.venom.freezeColor));
          break;

        case 'scissor_grip':
          // White flash on stun
          state.particles.push(createStunFlashParticle(position));
          break;

        // ===========================================================
        // WING (6) - Blue/White wind effects
        // ===========================================================
        case 'draft':
          // Air disturbance lines - reuse speed lines
          state.particles.push(...createSpeedLineParticles(position));
          break;

        case 'buzz_field':
          // Vibrating yellow circle
          state.particles.push(createBuzzRingParticle(position));
          break;

        case 'thermal_wake':
          // Heat shimmer effect
          state.particles.push(createHeatShimmerParticle(position));
          break;

        case 'scatter_dust':
          // Pollen puff - burst of small particles
          for (let i = 0; i < 8; i++) {
            const angle = Math.random() * Math.PI * 2;
            const speed = 30 + Math.random() * 40;
            state.particles.push({
              id: `dust-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
              position: { ...position },
              velocity: { x: Math.cos(angle) * speed, y: Math.sin(angle) * speed },
              color: '#FFEEAA66',
              size: 4 + Math.random() * 3,
              lifetime: 400,
              maxLifetime: 400,
              alpha: 0.6,
              type: 'apex_wind_dust',
            });
          }
          break;

        case 'updraft':
          // Speed boost lines
          state.particles.push(...createSpeedLineParticles(position));
          break;

        case 'hover_pressure':
          // Expanding pressure wave
          state.particles.push(createPressureWaveParticle(position));
          break;

        // ===========================================================
        // PREDATOR (6) - Yellow/Gold kill effects
        // ===========================================================
        case 'feeding_efficiency':
          // Speed boost effect (reuse speed lines)
          state.particles.push(...createSpeedLineParticles(position));
          break;

        case 'territorial_mark':
          // Orange ground stain where enemy died
          state.particles.push(createGroundStainParticle(position));
          break;

        case 'trophy_scent':
          // Golden flash for unique kill
          state.particles.push(createTrophyFlashParticle(position));
          // Small celebratory shake
          this.triggerShake(2, 60);
          break;

        case 'pack_signal':
          // Brief hesitation flash on nearby enemies
          state.particles.push(createStunFlashParticle(position));
          break;

        case 'corpse_heat':
          // Warm glow from corpse
          state.particles.push(createHeatShimmerParticle(position));
          break;

        case 'clean_kill':
          // Mini explosion burst
          state.particles.push(...createMiniExplosionParticles(position));
          this.triggerShake(4, 100);
          break;

        // ===========================================================
        // PHEROMONE (6) - Orange/Yellow aura effects
        // ===========================================================
        case 'threat_aura':
          // Soft orange glow around player
          state.particles.push(createAuraGlowParticle(position, tintColor || '#FF9900'));
          break;

        case 'confusion_cloud':
          // Swirling confusion particles
          state.particles.push(...createConfusionSwirlParticles(position));
          break;

        case 'rally_scent':
          // Trail slow effect - shimmer particles
          state.particles.push(createHeatShimmerParticle(position));
          break;

        case 'death_marker':
          // Dark seeping pool from corpse
          state.particles.push(createSeepingParticle(position));
          break;

        case 'aggro_pulse':
          // Large expanding ring pulse
          state.particles.push(createPressureWaveParticle(position));
          this.triggerShake(3, 80);
          break;

        case 'bitter_taste':
          // Brief red flash on attacker
          state.particles.push(createStunFlashParticle(position));
          break;

        // ===========================================================
        // CHITIN (6) - Grey/Red defensive effects
        // ===========================================================
        case 'barbed_chitin':
          // Spike plink when enemy touches
          state.particles.push(createSpikePlinkParticle(position));
          break;

        case 'ablative_shell':
          // Shell fragment on first hit
          state.particles.push(createShellFragmentParticle(position));
          break;

        case 'heat_retention':
          // Warm aura when below 50% HP
          state.particles.push(createHeatShimmerParticle(position));
          break;

        case 'compound_eyes':
          // Brief yellow flash indicating telegraph seen
          state.particles.push(createAuraGlowParticle(position, ABILITY_JUICE.mandible.glintColor));
          break;

        case 'antenna_sensitivity':
          // Brief orange pulse when enemy approaches
          state.particles.push(createAuraGlowParticle(position, '#FF9900'));
          break;

        case 'molting_burst':
          // BIG shell burst - dramatic emergency effect
          state.particles.push(...createShellBurstParticles(position));
          // Add golden burst for invuln
          for (let i = 0; i < 8; i++) {
            const angle = (i / 8) * Math.PI * 2;
            state.particles.push({
              id: `molt-gold-${Date.now()}-${i}`,
              position: { ...position },
              velocity: { x: Math.cos(angle) * 100, y: Math.sin(angle) * 100 },
              color: ABILITY_JUICE.chitin.burstColor,
              size: 6,
              lifetime: 400,
              maxLifetime: 400,
              alpha: 1,
              type: 'burst',
            });
          }
          // Big screen shake for emergency activation
          this.triggerShake(10, 200);
          this.triggerFreeze('massacre');
          break;

        default:
          // Unknown ability - log for debugging
          console.warn(`[emitAbilityJuice] Unknown ability: ${abilityId}`);
      }

      // Scale particle effects with stacks if applicable
      if (stacks > 1) {
        // Add extra particles for high stack counts
        const extraParticles = Math.min(stacks - 1, 3);
        for (let i = 0; i < extraParticles; i++) {
          // Add small sparkle particles indicating stack buildup
          state.particles.push({
            id: `stack-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
            position: { x: position.x + (Math.random() - 0.5) * 20, y: position.y - 15 },
            velocity: { x: (Math.random() - 0.5) * 20, y: -30 - Math.random() * 20 },
            color: tintColor || '#FFFFFF',
            size: 2,
            lifetime: 300,
            maxLifetime: 300,
            alpha: 0.7,
            type: 'burst',
          });
        }
      }
    },

    // =================================================================
    // BALL ESCAPE CELEBRATION
    // "Through the gap. Every time."
    //
    // When the player escapes THE BALL formation through the gap,
    // this triggers a victory celebration:
    // - Directional particle burst through the gap
    // - Green/cyan victory particles
    // - Freeze frame for dramatic effect
    // - Screen shake for impact
    // - Expanding ring effect
    // =================================================================
    emitBallEscape(position: Vector2, gapAngle: number, escapeCount: number) {
      const sound = getSoundEngine();

      // Scale celebration intensity with escape count
      // First escape: normal. Multiple escapes: LEGENDARY.
      const intensityScale = Math.min(2.0, 1.0 + escapeCount * 0.25);

      // =================================================================
      // 1. DIRECTIONAL PARTICLE BURST - Victory particles through the gap
      // Particles shoot outward in the direction of escape (gap angle)
      // =================================================================
      const particleCount = Math.floor(20 * intensityScale);
      const escapeColors = ['#00FF88', '#00FFFF', '#88FFAA', '#00FF00']; // Green/cyan victory colors

      for (let i = 0; i < particleCount; i++) {
        // Particles spread outward from gap angle
        const spreadAngle = (Math.random() - 0.5) * (Math.PI / 3); // 60 degree spread
        const particleAngle = gapAngle + spreadAngle;
        const speed = (200 + Math.random() * 200) * intensityScale;

        const color = escapeColors[Math.floor(Math.random() * escapeColors.length)];

        state.particles.push({
          id: `escape-${Date.now()}-${i}-${Math.random().toString(36).slice(2, 5)}`,
          position: { ...position },
          velocity: {
            x: Math.cos(particleAngle) * speed,
            y: Math.sin(particleAngle) * speed,
          },
          color,
          size: 4 + Math.random() * 4,
          lifetime: 500 + Math.random() * 300,
          maxLifetime: 500 + Math.random() * 300,
          alpha: 1,
          type: 'burst',
        });
      }

      // =================================================================
      // 2. CIRCULAR BURST - Secondary burst for visual impact
      // Full 360 degree sparkle burst
      // =================================================================
      const burstCount = Math.floor(12 * intensityScale);
      for (let i = 0; i < burstCount; i++) {
        const angle = (i / burstCount) * Math.PI * 2;
        const speed = 100 + Math.random() * 80;

        state.particles.push({
          id: `escape-burst-${Date.now()}-${i}`,
          position: { ...position },
          velocity: {
            x: Math.cos(angle) * speed,
            y: Math.sin(angle) * speed,
          },
          color: '#FFFFFF',
          size: 2 + Math.random() * 2,
          lifetime: 300,
          maxLifetime: 300,
          alpha: 0.8,
          type: 'burst',
        });
      }

      // =================================================================
      // 3. EXPANDING RING EFFECT - Shockwave of freedom
      // =================================================================
      state.particles.push({
        id: `escape-ring-${Date.now()}`,
        position: { ...position },
        velocity: { x: 0, y: 0 },
        color: '#00FF88',
        size: 10,
        lifetime: 400,
        maxLifetime: 400,
        alpha: 0.8,
        type: 'ring',
        text: (80 * intensityScale).toString(), // Max ring size
      });

      // =================================================================
      // 4. VICTORY TEXT - Floating text indicator
      // =================================================================
      const victoryText = escapeCount >= 3 ? 'LEGENDARY ESCAPE!'
        : escapeCount >= 2 ? 'ESCAPE MASTER!'
        : 'ESCAPED!';

      state.particles.push({
        id: `escape-text-${Date.now()}`,
        position: { x: position.x, y: position.y - 20 },
        velocity: { x: 0, y: -60 },
        color: '#00FF88',
        size: escapeCount >= 2 ? 20 : 16,
        lifetime: 1200,
        maxLifetime: 1200,
        alpha: 1,
        type: 'text',
        text: victoryText,
      });

      // =================================================================
      // 5. SCREEN EFFECTS - Shake and freeze for impact
      // =================================================================

      // Screen shake - stronger for multiple escapes
      const shakeIntensity = Math.min(10, 5 + escapeCount * 2);
      this.triggerShake(shakeIntensity, 150);

      // Freeze frame - "time slows when you're badass"
      // First escape gets a small freeze, subsequent escapes get bigger
      if (escapeCount >= 2) {
        this.triggerFreeze('significant');
      } else {
        this.triggerFreeze('critical');
      }

      // =================================================================
      // 6. AUDIO FEEDBACK
      // =================================================================

      // Play victory sound
      sound.play('powerup', { pitch: 1.2, volume: 0.8 });

      // Additional audio for legendary escapes
      if (escapeCount >= 2) {
        sound.play('bassDrop', { volume: 0.6 });
      }

      console.log(`[BALL ESCAPE] Celebration triggered! Escape #${escapeCount}, gap angle: ${(gapAngle * 180 / Math.PI).toFixed(1)}deg`);
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
  let isFrozen = false;
  if (juice.freeze.active && juice.freeze.framesRemaining > 0) {
    juice.freeze.framesRemaining--;
    if (juice.freeze.framesRemaining <= 0) {
      juice.freeze.active = false;
      juice.freeze.type = null;
    }
    // During freeze: only update particles (they look cool animating during freeze)
    // Other systems (shake, clutch) stay frozen
    isFrozen = true;
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

    // XP_SPARKLE: Upward float with gentle deceleration and twinkle
    if (particle.type === 'xp_sparkle') {
      // Gentle upward acceleration (pulled toward XP bar)
      particle.velocity.y -= 50 * dt;
      // Horizontal deceleration for convergence
      particle.velocity.x *= 0.95;
      // Cap upward velocity
      if (particle.velocity.y < -300) {
        particle.velocity.y = -300;
      }
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

  // Skip shake/clutch updates during freeze frames (only particles animate during freeze)
  if (isFrozen) {
    return;
  }

  // Update shake with self-healing
  // SELF-HEALING: If no active shake, force offset to zero to prevent stuck states
  if (juice.shake.duration <= 0 || juice.shake.intensity <= 0) {
    // No active shake - ensure offset is zeroed (self-healing)
    if (juice.shake.offset.x !== 0 || juice.shake.offset.y !== 0) {
      juice.shake.offset = { x: 0, y: 0 };
    }
    juice.shake.intensity = 0;
    juice.shake.duration = 0;
    juice.shake.elapsed = 0;
  } else {
    // Active shake - update normally
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

  // DD-16: Update clutch moment with self-healing
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
  } else {
    // SELF-HEALING: If clutch is not active, ensure all values are at defaults
    // This prevents stuck zoom/timeScale states
    if (juice.clutch.zoom !== 1.0 || juice.clutch.timeScale !== 1.0) {
      juice.clutch.zoom = 1.0;
      juice.clutch.timeScale = 1.0;
      juice.clutch.remaining = 0;
      juice.clutch.duration = 0;
      juice.clutch.level = null;
    }
  }

  // Update screen effect (circle inversion) with self-healing
  const screenEffect = juice.screenEffect;
  if (screenEffect.invert) {
    screenEffect.elapsed += deltaTime;
    if (screenEffect.elapsed >= screenEffect.duration) {
      // Effect finished - reset
      screenEffect.invert = false;
      screenEffect.elapsed = 0;
      screenEffect.duration = 0;
    }
  } else {
    // SELF-HEALING: If not inverting, ensure all values are reset
    if (screenEffect.elapsed !== 0 || screenEffect.duration !== 0) {
      screenEffect.elapsed = 0;
      screenEffect.duration = 0;
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
  // Freeze frames completely stop time (even with debug speedup)
  if (juice.freeze.active && juice.freeze.framesRemaining > 0) {
    return 0; // Complete stop
  }

  // Base time scale (1.0 normally, or clutch slowmo)
  const baseTimeScale = juice.clutch.active ? juice.clutch.timeScale : 1.0;

  // Apply debug time scale multiplier
  // This enables accelerated testing while preserving game-time semantics
  return baseTimeScale * debugTimeScale;
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

// =============================================================================
// DD-038-3: Afterimage Rendering
// =============================================================================

/**
 * Render afterimages during Apex Strike
 * "5 afterimages during strike - visual only, pure juice"
 *
 * @param ctx - Canvas rendering context
 * @param afterimages - Array of active afterimages
 * @param playerRadius - Player hitbox/render radius (default 15)
 */
export function renderAfterimages(
  ctx: CanvasRenderingContext2D,
  afterimages: Afterimage[],
  playerRadius: number = 15
): void {
  const config = APEX_STRIKE.strike.afterimages;

  // Render from oldest to newest (back to front)
  for (const img of afterimages) {
    ctx.save();
    ctx.globalAlpha = img.alpha;
    ctx.translate(img.position.x, img.position.y);

    // Rotate to face strike direction
    const angle = Math.atan2(img.direction.y, img.direction.x);
    ctx.rotate(angle);

    // Draw player silhouette (simple circle for hornet body)
    const radius = playerRadius * img.scale;

    // Main body
    ctx.beginPath();
    ctx.arc(0, 0, radius, 0, Math.PI * 2);
    ctx.fillStyle = config.color;
    ctx.fill();

    // Add subtle glow effect when alpha is higher (fresher afterimages)
    if (img.alpha > 0.3) {
      ctx.shadowColor = config.color;
      ctx.shadowBlur = 10 * (img.alpha / config.startAlpha);
      ctx.beginPath();
      ctx.arc(0, 0, radius, 0, Math.PI * 2);
      ctx.fill();
      ctx.shadowBlur = 0;
    }

    // Add directional "streaks" to show motion
    if (img.alpha > 0.2) {
      ctx.beginPath();
      ctx.moveTo(-radius * 1.5, 0);
      ctx.lineTo(-radius * 2.5, -radius * 0.3);
      ctx.lineTo(-radius * 2.5, radius * 0.3);
      ctx.closePath();
      ctx.fillStyle = config.color;
      ctx.globalAlpha = img.alpha * 0.5;
      ctx.fill();
    }

    ctx.restore();
  }
}
