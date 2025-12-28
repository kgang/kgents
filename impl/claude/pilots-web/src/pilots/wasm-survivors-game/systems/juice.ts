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

import type { GameState, EnemyType, Vector2, Enemy } from '@kgents/shared-primitives';
import { getSoundEngine } from './sound';

// =============================================================================
// Color Palette (from design docs)
// =============================================================================

export const COLORS = {
  player: '#00D4FF', // Electric Blue
  enemy: '#FF3366', // Corrupted Red
  xp: '#FFD700', // Golden
  health: '#00FF88', // Vitality Green
  ghost: '#A0A0B0', // Warm Gray
  crisis: '#FF8800', // Warning Orange
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
  type: 'burst' | 'trail' | 'text' | 'ring';
  text?: string;
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

export interface JuiceSystem {
  particles: Particle[];
  shake: ShakeState;
  escalation: EscalationState;
  clutch: ClutchState; // DD-16: Clutch moment state

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

    emitKill(position: Vector2, enemyType: EnemyType) {
      // DD-5: Sound feedback - kill pop
      const sound = getSoundEngine();
      const pitchMap: Record<EnemyType, number> = {
        basic: 1.0,
        fast: 1.2,
        tank: 0.7,
        boss: 0.5,
        spitter: 1.1,  // DD-24
        colossal_tide: 0.4,  // DD-30: Deep rumble for colossal
      };
      sound.play('kill', { pitch: pitchMap[enemyType] });

      // Update combo
      state.escalation.combo++;
      state.escalation.comboTimer = 2000; // 2 second combo window
      state.escalation.multiplier = calculateEscalationMultiplier(state.escalation);

      // Particle count scales with escalation and enemy type
      const baseCount = enemyType === 'boss' ? 24 : enemyType === 'tank' ? 16 : 8;
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
      const xpValues: Record<EnemyType, number> = {
        basic: 10,
        fast: 15,
        tank: 30,
        boss: 100,
        spitter: 20,  // DD-24
        colossal_tide: 200,  // DD-30: High reward for colossal
      };
      state.particles.push(
        createTextParticle(position, `+${xpValues[enemyType]}`, COLORS.xp)
      );

      // Small shake on kill
      const shakeIntensity = enemyType === 'boss' ? 8 : enemyType === 'tank' ? 4 : 2;
      this.triggerShake(shakeIntensity * state.escalation.multiplier, 100);
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

      // Screen shake
      this.triggerShake(5, 150);

      // Red flash particles
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

  // Update particles
  const dt = deltaTime / 1000;

  juice.particles.forEach((particle) => {
    // Update position
    particle.position.x += particle.velocity.x * dt;
    particle.position.y += particle.velocity.y * dt;

    // Apply gravity to burst particles
    if (particle.type === 'burst') {
      particle.velocity.y += 200 * dt; // Gravity
    }

    // Update lifetime
    particle.lifetime -= deltaTime;

    // Fade out
    particle.alpha = Math.max(0, particle.lifetime / particle.maxLifetime);

    // Grow ring particles
    if (particle.type === 'ring') {
      const maxSize = parseFloat(particle.text || '100');
      const progress = 1 - particle.lifetime / particle.maxLifetime;
      particle.size = maxSize * progress;
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
 * Called by game loop to slow down time during clutch moments
 */
export function getEffectiveTimeScale(juice: JuiceSystem): number {
  return juice.clutch.active ? juice.clutch.timeScale : 1.0;
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
