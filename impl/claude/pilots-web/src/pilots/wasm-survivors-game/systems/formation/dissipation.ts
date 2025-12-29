/**
 * THE BALL Formation System - Dissipation & Revival
 *
 * Handles the fade-out and revival mechanics when player escapes THE BALL.
 *
 * Flow: active → fading (can revive) → dissipating → inactive
 *
 * RUN 039: Added linger period where ball can revive if player returns.
 * - Player escapes → grace period (1.5s) → fading starts
 * - During fading, ball opacity decreases but CAN REVIVE
 * - If player returns during fade, ball recovers
 * - If fade reaches 100%, ball enters final dissipation (no revival)
 */

import type { Vector2 } from '../../types';
import type { BallDissipationState, BallEvent } from './types';
import { BALL_DISSIPATION_CONFIG } from './config';
import { isPlayerOutsideBall, isPlayerInsideBall } from './boundary';

/**
 * Update dissipation and fade tracking
 */
export function updateDissipation(
  dissipation: BallDissipationState,
  playerPos: Vector2,
  ballCenter: Vector2,
  ballRadius: number,
  gameTime: number,
  deltaTime: number
): {
  state: BallDissipationState;
  shouldReset: boolean;
  events: BallEvent[];
} {
  const events: BallEvent[] = [];
  const newDissipation = { ...dissipation };
  let shouldReset = false;

  // deltaTime comes in milliseconds, convert to seconds for fade calculations
  const deltaSec = deltaTime / 1000;

  // Check player position relative to ball
  const playerIsOutside = isPlayerOutsideBall(playerPos, ballCenter, ballRadius);
  const playerIsInside = isPlayerInsideBall(playerPos, ballCenter, ballRadius);

  // ==========================================================================
  // STATE 1: Final dissipation (no revival possible)
  // ==========================================================================
  if (newDissipation.isDissipating) {
    const dissipationProgress =
      (gameTime - newDissipation.dissipationStartTime) / BALL_DISSIPATION_CONFIG.dissipationDuration;

    if (dissipationProgress >= 1) {
      // Ball fully dissipated - signal reset
      shouldReset = true;

      events.push({
        type: 'ball_dispersed',
        timestamp: gameTime,
        position: ballCenter,
      });
    }

    return { state: newDissipation, shouldReset, events };
  }

  // ==========================================================================
  // STATE 2: Fading (can still revive!)
  // ==========================================================================
  if (newDissipation.isFading) {
    if (playerIsInside) {
      // Player returned! Start reviving
      const wasReviving = newDissipation.fadeProgress > 0 && newDissipation.fadeProgress < 1;

      // Decrease fade progress (recover)
      newDissipation.fadeProgress -= BALL_DISSIPATION_CONFIG.reviveSpeed * deltaSec;

      if (newDissipation.fadeProgress <= 0) {
        // Fully revived!
        newDissipation.fadeProgress = 0;
        newDissipation.isFading = false;
        newDissipation.fadeStartTime = 0;
        newDissipation.playerOutsideTime = 0;

        events.push({
          type: 'ball_revived',
          timestamp: gameTime,
          position: ballCenter,
        });

        console.log('[BALL] Revived! Player returned during fade');
      } else if (!wasReviving) {
        // Just started reviving
        events.push({
          type: 'ball_reviving',
          timestamp: gameTime,
          position: ballCenter,
        });

        console.log('[BALL] Reviving... fadeProgress:', newDissipation.fadeProgress.toFixed(2));
      }
    } else {
      // Player still outside, continue fading
      newDissipation.fadeProgress += BALL_DISSIPATION_CONFIG.fadeSpeed * deltaSec;

      if (newDissipation.fadeProgress >= 1) {
        // Fade complete - enter final dissipation (no revival)
        newDissipation.fadeProgress = 1;
        newDissipation.isFading = false;
        newDissipation.isDissipating = true;
        newDissipation.dissipationStartTime = gameTime;

        events.push({
          type: 'ball_dissipating',
          timestamp: gameTime,
          position: ballCenter,
        });

        console.log('[BALL] Fade complete, entering final dissipation');
      }
    }

    return { state: newDissipation, shouldReset, events };
  }

  // ==========================================================================
  // STATE 3: Active ball - check for escape
  // ==========================================================================
  if (playerIsOutside) {
    // Accumulate time outside
    newDissipation.playerOutsideTime += deltaTime;

    if (newDissipation.playerOutsideTime >= BALL_DISSIPATION_CONFIG.escapeGracePeriod) {
      // Start fading!
      newDissipation.isFading = true;
      newDissipation.fadeStartTime = gameTime;
      newDissipation.fadeProgress = 0;

      events.push({
        type: 'ball_fading_started',
        timestamp: gameTime,
        position: ballCenter,
      });

      // Also emit escaped event for backwards compatibility
      events.push({
        type: 'ball_escaped',
        timestamp: gameTime,
        position: ballCenter,
      });

      console.log('[BALL] Player escaped! Ball starting to fade...');
    }
  } else {
    // Reset timer if player comes back inside (before fade started)
    newDissipation.playerOutsideTime = 0;
  }

  return { state: newDissipation, shouldReset, events };
}

/**
 * Create initial dissipation state
 */
export function createInitialDissipationState(): BallDissipationState {
  return {
    playerOutsideTime: 0,
    isDissipating: false,
    dissipationStartTime: 0,
    // Fade/linger
    isFading: false,
    fadeProgress: 0,
    fadeStartTime: 0,
  };
}

/**
 * Get dissipation progress (0-1) for visual effects
 * Combines fade progress and final dissipation progress
 */
export function getDissipationProgress(
  dissipation: BallDissipationState,
  gameTime: number
): number {
  // During fading, return fade progress
  if (dissipation.isFading) {
    return dissipation.fadeProgress * 0.7; // Fade to 70% during linger
  }

  // During final dissipation, complete the remaining 30%
  if (dissipation.isDissipating) {
    const dissipProgress = Math.min(1,
      (gameTime - dissipation.dissipationStartTime) / BALL_DISSIPATION_CONFIG.dissipationDuration
    );
    return 0.7 + dissipProgress * 0.3; // 70% to 100%
  }

  return 0;
}

/**
 * Get the opacity for rendering (inverse of dissipation progress)
 */
export function getBallOpacity(
  dissipation: BallDissipationState,
  gameTime: number
): number {
  // During fading, opacity decreases
  if (dissipation.isFading) {
    // Fade to 30% opacity minimum during linger (so player can see it's still there)
    return 1 - dissipation.fadeProgress * 0.7;
  }

  // During final dissipation, fade to 0
  if (dissipation.isDissipating) {
    const dissipProgress = Math.min(1,
      (gameTime - dissipation.dissipationStartTime) / BALL_DISSIPATION_CONFIG.dissipationDuration
    );
    return 0.3 * (1 - dissipProgress); // 30% down to 0%
  }

  return 1;
}

/**
 * Calculate expanded radius during dissipation
 */
export function getDissipatingRadius(
  baseRadius: number,
  dissipation: BallDissipationState,
  gameTime: number
): number {
  // During fading, slightly expand
  if (dissipation.isFading) {
    return baseRadius * (1 + dissipation.fadeProgress * 0.2); // Expand by 20% during fade
  }

  // During final dissipation, expand more
  if (dissipation.isDissipating) {
    const progress = Math.min(1,
      (gameTime - dissipation.dissipationStartTime) / BALL_DISSIPATION_CONFIG.dissipationDuration
    );
    return baseRadius * 1.2 * (1 + progress * 0.3); // Additional 30% during final dissipation
  }

  return baseRadius;
}

/**
 * Check if the ball is in a revivable state
 */
export function canBallRevive(dissipation: BallDissipationState): boolean {
  return dissipation.isFading && !dissipation.isDissipating;
}

/**
 * Check if ball is currently being revived
 */
export function isBallReviving(
  dissipation: BallDissipationState,
  playerPos: Vector2,
  ballCenter: Vector2,
  ballRadius: number
): boolean {
  if (!dissipation.isFading) return false;
  return isPlayerInsideBall(playerPos, ballCenter, ballRadius);
}
