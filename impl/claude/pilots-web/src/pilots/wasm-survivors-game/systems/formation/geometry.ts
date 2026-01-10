/**
 * THE BALL Formation System - Geometry & Movement
 *
 * Manages ball center position and movement.
 * The ball drifts independently at bee speed, doesn't track player exactly.
 */

import type { Vector2 } from '../../types';
import type { BallGeometryState } from './types';
import { BALL_MOVEMENT_CONFIG, BALL_PHASE_CONFIG } from './config';

/**
 * Update ball position and velocity
 */
export function updateBallMovement(
  geometry: BallGeometryState,
  playerPos: Vector2,
  deltaTime: number
): BallGeometryState {
  const dt = deltaTime / 1000; // Convert to seconds
  const newGeometry = { ...geometry };

  // Calculate direction to target
  const dx = newGeometry.targetPosition.x - newGeometry.center.x;
  const dy = newGeometry.targetPosition.y - newGeometry.center.y;
  const distToTarget = Math.sqrt(dx * dx + dy * dy);

  // Move toward target at bee speed
  if (distToTarget > 5) {
    const dirX = dx / distToTarget;
    const dirY = dy / distToTarget;

    const targetVelX = dirX * BALL_MOVEMENT_CONFIG.moveSpeed;
    const targetVelY = dirY * BALL_MOVEMENT_CONFIG.moveSpeed;

    // Smooth velocity interpolation
    newGeometry.velocity = {
      x: newGeometry.velocity.x + (targetVelX - newGeometry.velocity.x) * 0.1,
      y: newGeometry.velocity.y + (targetVelY - newGeometry.velocity.y) * 0.1,
    };

    newGeometry.center = {
      x: newGeometry.center.x + newGeometry.velocity.x * dt,
      y: newGeometry.center.y + newGeometry.velocity.y * dt,
    };
  }

  // Slowly update target to follow player (lazy tracking)
  newGeometry.targetPosition = {
    x: newGeometry.targetPosition.x +
      (playerPos.x - newGeometry.targetPosition.x) * BALL_MOVEMENT_CONFIG.targetUpdateRate,
    y: newGeometry.targetPosition.y +
      (playerPos.y - newGeometry.targetPosition.y) * BALL_MOVEMENT_CONFIG.targetUpdateRate,
  };

  return newGeometry;
}

/**
 * Create initial geometry state
 */
export function createInitialGeometryState(playerPos: Vector2): BallGeometryState {
  return {
    center: { ...playerPos },  // Snap to player initially
    currentRadius: BALL_PHASE_CONFIG.initialRadius,
    velocity: { x: 0, y: 0 },
    targetPosition: { ...playerPos },
  };
}

/**
 * Interpolate radius during forming phase
 */
export function interpolateFormingRadius(progress: number): number {
  return BALL_PHASE_CONFIG.initialRadius -
    (BALL_PHASE_CONFIG.initialRadius - 150) * progress;
}

/**
 * Interpolate radius during constrict phase
 */
export function interpolateConstrictRadius(progress: number): number {
  return 150 - (150 - BALL_PHASE_CONFIG.finalRadius) * progress;
}

// =============================================================================
// Bee Oscillation Configuration (Run 039: Organic Ball Feel)
// =============================================================================
// Bees oscillate in/out from the ball radius for organic, breathing feel
// Each bee has unique phase offset so they don't all move in sync

const BEE_OSCILLATION = {
  amplitude: 8,           // How far bees wobble in/out (pixels)
  frequency: 1.5,         // Oscillation speed (Hz) - cycles per second
  phaseSpread: Math.PI,   // How much phase offset varies between bees
};

/**
 * Calculate formation positions for bees in THE BALL
 * Creates positions around the sphere with a gap for escape
 *
 * Run 039: Bees now oscillate slightly in/out from the radius
 * for organic, breathing feel instead of hard-snapping to boundary.
 */
export function calculateFormationPositions(
  center: Vector2,
  radius: number,
  beeCount: number,
  gapAngle: number,
  gapSize: number,
  gameTime: number = Date.now()  // For oscillation timing
): Map<number, Vector2> {
  const positions = new Map<number, Vector2>();

  if (beeCount === 0) return positions;

  // Calculate available arc (full circle minus gap)
  const availableArc = Math.PI * 2 - gapSize;
  const angleStep = availableArc / beeCount;

  // Start from opposite side of gap
  const startAngle = gapAngle + gapSize / 2;

  // Convert gameTime to seconds for oscillation
  const timeSec = gameTime / 1000;

  for (let i = 0; i < beeCount; i++) {
    const angle = startAngle + angleStep * i;

    // =======================================================================
    // ORGANIC OSCILLATION (Run 039)
    // =======================================================================
    // Each bee gets a unique phase offset based on its index
    // This creates a "breathing" effect where bees aren't perfectly aligned
    const phaseOffset = (i / beeCount) * BEE_OSCILLATION.phaseSpread + (i * 0.7);

    // Sinusoidal oscillation: radius + amplitude * sin(frequency * time + phase)
    const oscillation = BEE_OSCILLATION.amplitude *
      Math.sin(2 * Math.PI * BEE_OSCILLATION.frequency * timeSec + phaseOffset);

    const effectiveRadius = radius + oscillation;

    positions.set(i, {
      x: center.x + Math.cos(angle) * effectiveRadius,
      y: center.y + Math.sin(angle) * effectiveRadius,
    });
  }

  return positions;
}

/**
 * Check if a position is within the escape gap
 */
export function isInEscapeGap(
  playerPos: Vector2,
  ballCenter: Vector2,
  ballRadius: number,
  gapAngle: number,
  gapSize: number
): boolean {
  // Calculate angle from center to player
  const dx = playerPos.x - ballCenter.x;
  const dy = playerPos.y - ballCenter.y;
  const playerAngle = Math.atan2(dy, dx);

  // Normalize angles to 0-2PI range
  const normalizeAngle = (a: number) => ((a % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
  const normalizedPlayerAngle = normalizeAngle(playerAngle);
  const normalizedGapAngle = normalizeAngle(gapAngle);

  // Check if player angle is within gap
  const gapStart = normalizedGapAngle - gapSize / 2;
  const gapEnd = normalizedGapAngle + gapSize / 2;

  // Handle wraparound
  let inGap: boolean;
  if (gapStart < 0) {
    inGap = normalizedPlayerAngle >= normalizeAngle(gapStart) ||
            normalizedPlayerAngle <= gapEnd;
  } else if (gapEnd > Math.PI * 2) {
    inGap = normalizedPlayerAngle >= gapStart ||
            normalizedPlayerAngle <= normalizeAngle(gapEnd);
  } else {
    inGap = normalizedPlayerAngle >= gapStart && normalizedPlayerAngle <= gapEnd;
  }

  // Also check if player is at the right distance (escaping outward)
  const distance = Math.sqrt(dx * dx + dy * dy);
  const atEscapeDistance = distance >= ballRadius * 0.9;

  return inGap && atEscapeDistance;
}
