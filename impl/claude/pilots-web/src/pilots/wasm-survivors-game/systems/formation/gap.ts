/**
 * THE BALL Formation System - Gap Rotation
 *
 * Manages the escape gap rotation, speed changes, and direction changes.
 * The gap is the player's only escape route during constrict phase.
 */

import type { BallGapState } from './types';
import { BALL_GAP_CONFIG } from './config';

/**
 * Update gap rotation state
 */
export function updateGapRotation(
  gap: BallGapState,
  gameTime: number,
  deltaTime: number
): BallGapState {
  const dt = deltaTime / 1000; // Convert to seconds
  const newGap = { ...gap };

  // Rotate the gap
  newGap.angle += newGap.rotationSpeed * newGap.rotationDirection * dt;

  // Keep angle in 0-2PI range
  newGap.angle = ((newGap.angle % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);

  // Randomly change direction
  if (gameTime - newGap.lastDirectionChange > BALL_GAP_CONFIG.directionChangeInterval) {
    if (Math.random() < BALL_GAP_CONFIG.directionChangeChance) {
      newGap.rotationDirection = newGap.rotationDirection === 1 ? -1 : 1;
      newGap.lastDirectionChange = gameTime;
    }
  }

  // Randomly change speed
  if (gameTime - newGap.lastSpeedChange > BALL_GAP_CONFIG.speedChangeInterval) {
    if (Math.random() < BALL_GAP_CONFIG.speedChangeChance) {
      newGap.rotationSpeed = BALL_GAP_CONFIG.rotationSpeedMin +
        Math.random() * (BALL_GAP_CONFIG.rotationSpeedMax - BALL_GAP_CONFIG.rotationSpeedMin);
      newGap.lastSpeedChange = gameTime;
    }
  }

  return newGap;
}

/**
 * Create initial gap state
 */
export function createInitialGapState(gameTime: number): BallGapState {
  return {
    angle: Math.random() * Math.PI * 2,
    size: (BALL_GAP_CONFIG.initialGapDegrees * Math.PI) / 180,
    rotationSpeed: BALL_GAP_CONFIG.rotationSpeedMin +
      Math.random() * (BALL_GAP_CONFIG.rotationSpeedMax - BALL_GAP_CONFIG.rotationSpeedMin),
    rotationDirection: Math.random() > 0.5 ? 1 : -1,
    lastDirectionChange: gameTime,
    lastSpeedChange: gameTime,
  };
}

/**
 * Interpolate gap size during constrict phase
 */
export function interpolateGapSize(progress: number): number {
  const initialRad = (BALL_GAP_CONFIG.initialGapDegrees * Math.PI) / 180;
  const finalRad = (BALL_GAP_CONFIG.finalGapDegrees * Math.PI) / 180;
  return initialRad - (initialRad - finalRad) * progress;
}
