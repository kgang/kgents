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
 * @see pilots/wasm-survivors-witnessed-run-lab/.outline.md
 */

import type { GameState, EnemyType, Vector2 } from '@kgents/shared-primitives';
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
