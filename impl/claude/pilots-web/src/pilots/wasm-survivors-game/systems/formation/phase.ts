/**
 * THE BALL Formation System - Phase State Machine
 *
 * Main phase transitions:
 * inactive → forming → silence → constrict → cooking
 *                                    ↓
 *                              (escape) → inactive
 */

import type { Vector2 } from '../../types';
import type { BallCoreState, BallPhase, BallEvent } from './types';
import { BALL_PHASE_CONFIG } from './config';

/**
 * Check if THE BALL should start forming
 *
 * Conditions:
 * - Ball not already active (for this slot)
 * - Enough eligible bees (not on cooldown)
 * - Past minimum wave
 * - Formation cooldown elapsed (2s since last ball ended)
 */
export function shouldStartBall(
  eligibleEnemyCount: number,
  wave: number,
  currentPhase: BallPhase,
  lastBallEndTime: number,
  gameTime: number,
  isSecondBall: boolean = false
): boolean {
  // Don't start if already active
  if (currentPhase !== 'inactive') return false;

  // Can happen from configured wave+
  if (wave < BALL_PHASE_CONFIG.minWaveForBall) return false;

  // Check formation cooldown (2s between balls)
  if (gameTime - lastBallEndTime < BALL_PHASE_CONFIG.formationCooldown) return false;

  // Need enough eligible bees (not on cooldown)
  const minBees = isSecondBall
    ? BALL_PHASE_CONFIG.minBeesForBall + BALL_PHASE_CONFIG.secondBallMinBeesExtra
    : BALL_PHASE_CONFIG.minBeesForBall;

  if (eligibleEnemyCount < minBees) return false;

  // Second ball has lower probability
  if (isSecondBall) {
    if (Math.random() > BALL_PHASE_CONFIG.secondBallProbability) return false;
  }

  return true;
}

/**
 * Update phase state machine
 */
export function updatePhase(
  core: BallCoreState,
  gameTime: number,
  playerPos: Vector2,
  ballCenter: Vector2,
  ballRadius: number,
  isInGap: boolean
): {
  state: BallCoreState;
  events: BallEvent[];
} {
  const events: BallEvent[] = [];
  const newCore = { ...core };

  const phaseElapsed = gameTime - core.phaseStartTime;

  switch (core.phase) {
    case 'inactive':
      // No updates needed - handled by shouldStartBall
      break;

    case 'forming': {
      const progress = Math.min(1, phaseElapsed / BALL_PHASE_CONFIG.formingDuration);
      newCore.phaseProgress = progress;

      if (progress >= 1) {
        // Transition to silence
        newCore.phase = 'silence';
        newCore.phaseStartTime = gameTime;
        newCore.phaseProgress = 0;

        events.push({
          type: 'ball_silence_started',
          timestamp: gameTime,
          position: ballCenter,
        });
      }
      break;
    }

    case 'silence': {
      const progress = Math.min(1, phaseElapsed / BALL_PHASE_CONFIG.silenceDuration);
      newCore.phaseProgress = progress;

      if (progress >= 1) {
        // Transition to constrict
        newCore.phase = 'constrict';
        newCore.phaseStartTime = gameTime;
        newCore.phaseProgress = 0;

        events.push({
          type: 'ball_constrict_started',
          timestamp: gameTime,
          position: ballCenter,
        });
      }
      break;
    }

    case 'constrict': {
      const progress = Math.min(1, phaseElapsed / BALL_PHASE_CONFIG.constrictDuration);
      newCore.phaseProgress = progress;

      // Check for escape through gap
      if (isInGap) {
        newCore.playerEscaped = true;
        newCore.escapeCount++;

        events.push({
          type: 'ball_escaped',
          timestamp: gameTime,
          position: playerPos,
        });

        // Reset to inactive
        newCore.phase = 'inactive';
        newCore.phaseStartTime = 0;
        newCore.phaseProgress = 0;
        break;
      }

      // Transition to cooking if player is still inside
      if (progress >= 1) {
        const dx = playerPos.x - ballCenter.x;
        const dy = playerPos.y - ballCenter.y;
        const distToCenter = Math.sqrt(dx * dx + dy * dy);

        if (distToCenter < ballRadius * 0.9) {
          // Player trapped - start cooking
          newCore.phase = 'cooking';
          newCore.phaseStartTime = gameTime;
          newCore.phaseProgress = 0;

          events.push({
            type: 'ball_cooking_started',
            timestamp: gameTime,
            position: ballCenter,
          });
        } else {
          // Player escaped (outside but not through gap)
          newCore.playerEscaped = true;
          newCore.escapeCount++;

          events.push({
            type: 'ball_escaped',
            timestamp: gameTime,
            position: playerPos,
          });

          // Reset to inactive
          newCore.phase = 'inactive';
          newCore.phaseStartTime = 0;
          newCore.phaseProgress = 0;
        }
      }
      break;
    }

    case 'cooking':
      // Cooking continues until player dies or ball dissipates
      // No automatic phase transition
      break;

    case 'dissipating':
      // Handled by dissipation.ts
      break;
  }

  return { state: newCore, events };
}

/**
 * Create initial core state
 */
export function createInitialCoreState(): BallCoreState {
  return {
    phase: 'inactive',
    phaseStartTime: 0,
    phaseProgress: 0,
    playerEscaped: false,
    escapeCount: 0,
  };
}

/**
 * Start ball formation
 */
export function startFormation(
  _core: BallCoreState,
  gameTime: number,
  playerPos: Vector2
): {
  state: BallCoreState;
  event: BallEvent;
} {
  const newCore: BallCoreState = {
    phase: 'forming',
    phaseStartTime: gameTime,
    phaseProgress: 0,
    playerEscaped: false,
    escapeCount: 0,
  };

  const event: BallEvent = {
    type: 'ball_forming_started',
    timestamp: gameTime,
    position: playerPos,
  };

  return { state: newCore, event };
}

/**
 * Calculate temperature based on ball phase
 */
export function calculateTemperature(
  phase: BallPhase,
  phaseProgress: number,
  currentTemp: number
): number {
  switch (phase) {
    case 'inactive':
      return 0;

    case 'forming':
      // Temperature rises slowly during forming (0-40%)
      return Math.min(40, phaseProgress * 40);

    case 'silence':
      // Temperature holds during silence (40%)
      return 40;

    case 'constrict':
      // Temperature rises rapidly during constrict (40-80%)
      return 40 + phaseProgress * 40;

    case 'cooking':
      // Temperature at max, continues rising for visual effect
      return Math.min(100, currentTemp + 0.5);

    case 'dissipating':
      // Temperature falls during dissipation
      return Math.max(0, currentTemp - 1);

    default:
      return currentTemp;
  }
}
