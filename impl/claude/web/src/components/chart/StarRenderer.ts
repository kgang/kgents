/**
 * StarRenderer — Star visualization utilities
 *
 * Tier-based "spectral class" colors and rendering helpers.
 * STARK BIOME themed: steel background, life accents.
 *
 * "The file is a lie. There is only the graph."
 */

import * as PIXI from 'pixi.js';
import type { StarData } from './useAstronomicalData';

// =============================================================================
// STARK BIOME Colors
// =============================================================================

/** Background colors (Steel Foundation) */
export const BACKGROUND = {
  obsidian: 0x0a0a0c, // Deepest canvas
  carbon: 0x141418, // Cards
  slate: 0x1c1c22, // Elevated
  gunmetal: 0x28282f, // Borders
} as const;

/** Tier colors (Spectral Classes) */
export const TIER_COLORS: Record<number, number> = {
  0: 0x4a6b4a, // Meta (sage) - O-class
  1: 0x6b8b6b, // Principles (mint) - B-class
  2: 0x8a8a94, // Protocols (steel) - A-class
  3: 0xc4a77d, // Agents (amber) - F-class
  4: 0x88c0d0, // AGENTESE (cyan) - G-class
};

/** Status modifiers */
export const STATUS_COLORS: Record<string, { alpha: number; tint?: number }> = {
  ACTIVE: { alpha: 1.0 },
  ORPHAN: { alpha: 0.4, tint: 0xa65d4a }, // Dim, red-shifted
  DEPRECATED: { alpha: 0.3 },
  ARCHIVED: { alpha: 0.2 },
  CONFLICTING: { alpha: 0.8, tint: 0xa65d4a },
};

/** Relationship colors for connections */
export const RELATIONSHIP_COLORS: Record<string, number> = {
  defines: 0x88c0d0,
  extends: 0x81a1c1,
  implements: 0xa3be8c,
  references: 0x5a5a64,
  contradicts: 0xa65d4a,
  harmonizes: 0x4a6b4a,
  tests: 0x8ba98b,
  uses: 0x8a8a94,
  fulfills: 0xc4a77d,
};

/** Glow colors for selection/hover */
export const GLOW = {
  selection: 0xd4b88c, // glow-amber
  hover: 0xc4a77d, // glow-spore
} as const;

// =============================================================================
// Star Rendering
// =============================================================================

/**
 * Create a star graphic (circle with glow effect).
 */
export function createStarGraphic(star: StarData): PIXI.Graphics {
  const g = new PIXI.Graphics();

  // Get base color from tier
  const baseColor = TIER_COLORS[star.tier] ?? TIER_COLORS[2];

  // Get status modifiers
  const statusMod = STATUS_COLORS[star.status] ?? STATUS_COLORS.ACTIVE;

  // Apply tint if status has one (e.g., orphan)
  const color = statusMod.tint ?? baseColor;

  // Draw the star
  g.beginFill(color, statusMod.alpha);
  g.drawCircle(0, 0, star.radius);
  g.endFill();

  // Add subtle core glow for active specs with evidence
  if (star.status === 'ACTIVE' && star.implCount + star.testCount > 0) {
    g.beginFill(0xffffff, 0.3);
    g.drawCircle(0, 0, star.radius * 0.4);
    g.endFill();
  }

  return g;
}

/**
 * Create a multi-layer selection/hover glow effect.
 * Respects prefers-reduced-motion.
 */
export function createGlowRing(radius: number, type: 'selection' | 'hover'): PIXI.Graphics {
  const g = new PIXI.Graphics();
  const color = type === 'selection' ? GLOW.selection : GLOW.hover;
  const baseAlpha = type === 'selection' ? 0.7 : 0.5;

  // Multi-layer radial glow (5 concentric rings, fading outward)
  const layers = 5;
  for (let i = layers; i >= 1; i--) {
    const layerAlpha = baseAlpha * (i / layers) * 0.6;
    const layerRadius = radius + i * 3;
    const lineWidth = Math.max(1, 3 - i * 0.5);

    g.lineStyle(lineWidth, color, layerAlpha);
    g.drawCircle(0, 0, layerRadius);
  }

  // Inner bright core ring
  g.lineStyle(2, color, baseAlpha);
  g.drawCircle(0, 0, radius + 2);

  // Innermost highlight
  g.lineStyle(1, 0xffffff, baseAlpha * 0.4);
  g.drawCircle(0, 0, radius + 1);

  return g;
}

/**
 * Create a connection line between two stars.
 */
export function drawConnection(
  graphics: PIXI.Graphics,
  source: StarData,
  target: StarData,
  relationship: string,
  strength: number,
  alpha: number = 0.3
): void {
  const color = RELATIONSHIP_COLORS[relationship.toLowerCase()] ?? RELATIONSHIP_COLORS.references;
  const lineWidth = 0.5 + strength * 1.5; // 0.5 to 2.0

  graphics.lineStyle(lineWidth, color, alpha * strength);
  graphics.moveTo(source.x, source.y);
  graphics.lineTo(target.x, target.y);
}

/**
 * Create the background grid dots (parallax layer).
 */
export function createBackgroundDots(
  width: number,
  height: number,
  density: number = 50
): PIXI.Graphics {
  const g = new PIXI.Graphics();

  g.beginFill(BACKGROUND.gunmetal, 0.5);

  const cols = Math.ceil(width / density);
  const rows = Math.ceil(height / density);

  for (let i = 0; i < cols; i++) {
    for (let j = 0; j < rows; j++) {
      g.drawCircle(i * density, j * density, 1);
    }
  }

  g.endFill();
  return g;
}

/**
 * Create distant "star field" background with multiple layers.
 * Each layer has different density and brightness for parallax depth.
 */
export function createStarField(width: number, height: number, count: number = 100): PIXI.Graphics {
  const g = new PIXI.Graphics();

  // Layer 1: Distant dim stars (smallest, dimmest)
  const farStars = Math.floor(count * 0.6);
  for (let i = 0; i < farStars; i++) {
    const x = Math.random() * width - width / 2;
    const y = Math.random() * height - height / 2;
    const size = Math.random() * 0.8 + 0.3;
    const alpha = Math.random() * 0.15 + 0.05;

    g.beginFill(0xccccdd, alpha);
    g.drawCircle(x, y, size);
    g.endFill();
  }

  // Layer 2: Mid-range stars
  const midStars = Math.floor(count * 0.3);
  for (let i = 0; i < midStars; i++) {
    const x = Math.random() * width - width / 2;
    const y = Math.random() * height - height / 2;
    const size = Math.random() * 1.2 + 0.5;
    const alpha = Math.random() * 0.25 + 0.1;

    g.beginFill(0xffffff, alpha);
    g.drawCircle(x, y, size);
    g.endFill();
  }

  // Layer 3: Bright nearby stars (largest, brightest, fewest)
  const nearStars = Math.floor(count * 0.1);
  for (let i = 0; i < nearStars; i++) {
    const x = Math.random() * width - width / 2;
    const y = Math.random() * height - height / 2;
    const size = Math.random() * 1.8 + 1.0;
    const alpha = Math.random() * 0.35 + 0.2;

    // Add subtle colored tint to some bright stars
    const colors = [0xffffff, 0xffeedd, 0xddeeff, 0xffeeff];
    const color = colors[Math.floor(Math.random() * colors.length)];

    g.beginFill(color, alpha);
    g.drawCircle(x, y, size);
    g.endFill();

    // Add tiny glow around brightest stars
    if (alpha > 0.4) {
      g.beginFill(color, alpha * 0.3);
      g.drawCircle(x, y, size * 2);
      g.endFill();
    }
  }

  return g;
}

// =============================================================================
// Motion Trails
// =============================================================================

/**
 * Particle trail system for simulation movement.
 * Uses a pool of particles for efficiency.
 */
export class TrailSystem {
  private container: PIXI.Container;
  private particles: PIXI.Graphics[] = [];
  private poolSize: number;
  private nextParticle: number = 0;
  private reducedMotion: boolean;

  constructor(parent: PIXI.Container, poolSize: number = 50) {
    this.container = new PIXI.Container();
    this.container.alpha = 0.6;
    this.poolSize = poolSize;
    this.reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Pre-create particle pool
    if (!this.reducedMotion) {
      for (let i = 0; i < poolSize; i++) {
        const p = new PIXI.Graphics();
        p.visible = false;
        this.container.addChild(p);
        this.particles.push(p);
      }
    }

    parent.addChildAt(this.container, 0); // Behind everything
  }

  /**
   * Emit a trail particle at position with color.
   */
  emit(x: number, y: number, color: number, size: number = 2): void {
    if (this.reducedMotion || this.particles.length === 0) return;

    const p = this.particles[this.nextParticle];
    this.nextParticle = (this.nextParticle + 1) % this.poolSize;

    p.clear();
    p.beginFill(color, 0.5);
    p.drawCircle(0, 0, size);
    p.endFill();
    p.position.set(x, y);
    p.alpha = 0.5;
    p.visible = true;
  }

  /**
   * Update all particles (fade out over time).
   * Call this each frame during simulation.
   */
  update(delta: number = 1): void {
    if (this.reducedMotion) return;

    for (const p of this.particles) {
      if (p.visible) {
        p.alpha -= 0.02 * delta;
        if (p.alpha <= 0) {
          p.visible = false;
        }
      }
    }
  }

  /**
   * Clear all trails.
   */
  clear(): void {
    for (const p of this.particles) {
      p.visible = false;
    }
  }

  /**
   * Destroy the trail system.
   */
  destroy(): void {
    this.container.destroy({ children: true });
    this.particles = [];
  }
}

// =============================================================================
// Color Utilities
// =============================================================================

/**
 * Convert hex number to CSS hex string.
 */
export function hexToString(hex: number): string {
  return '#' + hex.toString(16).padStart(6, '0');
}

/**
 * Get tier label.
 */
export function getTierLabel(tier: number): string {
  const labels: Record<number, string> = {
    0: 'Meta',
    1: 'Principles',
    2: 'Protocols',
    3: 'Agents',
    4: 'AGENTESE',
  };
  return labels[tier] ?? 'Unknown';
}

/**
 * Get status label for display.
 */
export function getStatusLabel(status: string): string {
  return status.charAt(0) + status.slice(1).toLowerCase();
}
