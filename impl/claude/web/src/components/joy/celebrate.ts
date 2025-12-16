/**
 * Celebrate Function
 *
 * Confetti burst for milestone achievements.
 * A lightweight confetti implementation without external dependencies.
 *
 * Foundation 5: Personality & Joy - Celebration Moments
 *
 * @example
 * ```tsx
 * // On first crystal capture
 * await captureContent(data);
 * celebrate({ intensity: 'normal' });
 *
 * // On A+ health grade
 * if (grade === 'A+') {
 *   celebrate({ intensity: 'epic' });
 * }
 * ```
 */

import { getMotionPreferences } from './useMotionPreferences';

export type CelebrationIntensity = 'subtle' | 'normal' | 'epic';

export interface CelebrateOptions {
  /** Confetti intensity. Default: 'normal' */
  intensity?: CelebrationIntensity;
  /** Duration in ms. Default: 2500 */
  duration?: number;
  /** Number of particles. Default: determined by intensity */
  particleCount?: number;
  /** Custom colors. Default: determined by intensity */
  colors?: string[];
}

// =============================================================================
// Configuration
// =============================================================================

interface IntensityConfig {
  particleCount: number;
  spread: number;
  duration: number;
  colors: string[];
}

const INTENSITY_CONFIG: Record<CelebrationIntensity, IntensityConfig> = {
  subtle: {
    particleCount: 30,
    spread: 60,
    duration: 2000,
    colors: ['#06B6D4', '#22C55E', '#84CC16'], // cyan, green, lime
  },
  normal: {
    particleCount: 60,
    spread: 90,
    duration: 2500,
    colors: ['#06B6D4', '#22C55E', '#F59E0B', '#8B5CF6', '#EC4899'], // cyan, green, amber, violet, pink
  },
  epic: {
    particleCount: 120,
    spread: 120,
    duration: 3500,
    colors: ['#06B6D4', '#22C55E', '#F59E0B', '#8B5CF6', '#EC4899', '#EF4444', '#FACC15'],
  },
};

// =============================================================================
// Confetti Particle
// =============================================================================

interface Particle {
  element: HTMLDivElement;
  x: number;
  y: number;
  vx: number;
  vy: number;
  rotation: number;
  rotationSpeed: number;
  scale: number;
  opacity: number;
}

function createParticle(
  container: HTMLDivElement,
  color: string,
  spread: number,
): Particle {
  const element = document.createElement('div');

  // Random shape (square, rectangle, or circle)
  const shapeType = Math.floor(Math.random() * 3);
  const size = 6 + Math.random() * 6;

  element.style.cssText = `
    position: absolute;
    width: ${shapeType === 1 ? size * 2 : size}px;
    height: ${shapeType === 1 ? size / 2 : size}px;
    background: ${color};
    border-radius: ${shapeType === 2 ? '50%' : '2px'};
    pointer-events: none;
    will-change: transform, opacity;
  `;

  container.appendChild(element);

  // Start from center of viewport
  const centerX = window.innerWidth / 2;
  const centerY = window.innerHeight / 2;

  // Random velocity (burst outward)
  const angle = (Math.random() * spread - spread / 2) * (Math.PI / 180) - Math.PI / 2;
  const velocity = 8 + Math.random() * 12;

  return {
    element,
    x: centerX,
    y: centerY,
    vx: Math.cos(angle) * velocity,
    vy: Math.sin(angle) * velocity,
    rotation: Math.random() * 360,
    rotationSpeed: (Math.random() - 0.5) * 20,
    scale: 0.5 + Math.random() * 0.5,
    opacity: 1,
  };
}

function updateParticle(
  particle: Particle,
  deltaTime: number,
  elapsed: number,
  duration: number,
): void {
  // Physics
  particle.vy += 0.3 * deltaTime; // Gravity
  particle.vx *= 0.99; // Air resistance
  particle.vy *= 0.99;

  particle.x += particle.vx * deltaTime;
  particle.y += particle.vy * deltaTime;
  particle.rotation += particle.rotationSpeed * deltaTime;

  // Fade out in last third
  const fadeStart = duration * 0.6;
  if (elapsed > fadeStart) {
    particle.opacity = 1 - (elapsed - fadeStart) / (duration - fadeStart);
  }

  // Apply transforms
  particle.element.style.transform = `
    translate(${particle.x}px, ${particle.y}px)
    rotate(${particle.rotation}deg)
    scale(${particle.scale})
  `;
  particle.element.style.opacity = String(particle.opacity);
}

// =============================================================================
// Main Celebrate Function
// =============================================================================

let isAnimating = false;

/**
 * Reset animation state (for testing only).
 * @internal
 */
export function __resetCelebrateState(): void {
  isAnimating = false;
}

/**
 * Trigger a celebratory confetti burst.
 *
 * Respects user's prefers-reduced-motion setting.
 */
export function celebrate(options: CelebrateOptions = {}): void {
  // Respect motion preferences
  const { shouldAnimate } = getMotionPreferences();
  if (!shouldAnimate) return;

  // Prevent overlapping celebrations
  if (isAnimating) return;
  isAnimating = true;

  const {
    intensity = 'normal',
  } = options;

  const config = INTENSITY_CONFIG[intensity];
  const particleCount = options.particleCount ?? config.particleCount;
  const colors = options.colors ?? config.colors;
  const duration = options.duration ?? config.duration;

  // Create container
  const container = document.createElement('div');
  container.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
    overflow: hidden;
    z-index: 9999;
  `;
  document.body.appendChild(container);

  // Create particles
  const particles: Particle[] = [];
  for (let i = 0; i < particleCount; i++) {
    const color = colors[Math.floor(Math.random() * colors.length)];
    particles.push(createParticle(container, color, config.spread));
  }

  // Animation loop
  let startTime: number | null = null;
  let lastTime: number | null = null;

  function animate(currentTime: number) {
    if (startTime === null) startTime = currentTime;
    if (lastTime === null) lastTime = currentTime;

    const elapsed = currentTime - startTime;
    const deltaTime = Math.min((currentTime - lastTime) / 16.67, 2); // Cap at 2x
    lastTime = currentTime;

    // Update all particles
    for (const particle of particles) {
      updateParticle(particle, deltaTime, elapsed, duration);
    }

    // Continue or cleanup
    if (elapsed < duration) {
      requestAnimationFrame(animate);
    } else {
      // Cleanup
      container.remove();
      isAnimating = false;
    }
  }

  requestAnimationFrame(animate);
}

/**
 * Quick celebrate with default settings.
 */
export function celebrateQuick(): void {
  celebrate({ intensity: 'subtle' });
}

/**
 * Epic celebrate for major milestones.
 */
export function celebrateEpic(): void {
  celebrate({ intensity: 'epic' });
}

export default celebrate;
