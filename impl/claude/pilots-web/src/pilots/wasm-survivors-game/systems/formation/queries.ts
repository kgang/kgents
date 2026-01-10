/**
 * THE BALL Formation System - Query Functions
 *
 * State interrogation functions following the pattern from enemies.ts
 * (isBeeVulnerable, isBeeAttacking, etc.)
 */

import type { Vector2 } from '../../types';
import type { LegacyBallState, BallPhase } from './types';

/**
 * Check if ball is active (any non-inactive phase)
 */
export function isBallActive(state: LegacyBallState): boolean {
  return state.phase !== 'inactive';
}

/**
 * Check if ball is in gathering phase (RUN 039: pre-formation telegraph)
 */
export function isBallGathering(state: LegacyBallState): boolean {
  return state.phase === 'gathering';
}

/**
 * Check if ball is in forming phase
 */
export function isBallForming(state: LegacyBallState): boolean {
  return state.phase === 'forming';
}

/**
 * Check if ball is in silence phase
 */
export function isBallInSilence(state: LegacyBallState): boolean {
  return state.phase === 'silence';
}

/**
 * Check if ball is constricting
 */
export function isBallConstricting(state: LegacyBallState): boolean {
  return state.phase === 'constrict';
}

/**
 * Check if ball is cooking (player trapped)
 */
export function isBallCooking(state: LegacyBallState): boolean {
  return state.phase === 'cooking';
}

/**
 * Check if ball is dissipating
 */
export function isBallDissipating(state: LegacyBallState): boolean {
  return state.isDissipating;
}

/**
 * Check if ball is fading (can still revive) - RUN 039
 */
export function isBallFading(state: LegacyBallState): boolean {
  return state.isFading && !state.isDissipating;
}

/**
 * Check if ball can be revived (player can return and save it) - RUN 039
 */
export function canBallBeRevived(state: LegacyBallState): boolean {
  return state.isFading && !state.isDissipating && state.fadeProgress < 1;
}

/**
 * Get fade progress (0-1) - RUN 039
 */
export function getBallFadeProgress(state: LegacyBallState): number {
  return state.fadeProgress;
}

/**
 * Check if a lunge attack is in progress
 */
export function isLungeInProgress(state: LegacyBallState): boolean {
  return state.activeLunge !== null;
}

/**
 * Check if a specific bee is currently lunging
 */
export function isBeeInFormationLunge(state: LegacyBallState, beeId: string): boolean {
  return state.activeLunge?.beeId === beeId;
}

/**
 * Check if a bee is part of the formation
 */
export function isBeeInFormation(state: LegacyBallState, beeId: string): boolean {
  return state.formationBeeIds.includes(beeId);
}

/**
 * Check if player is trapped inside the ball
 */
export function isPlayerTrapped(
  state: LegacyBallState,
  playerPos: Vector2
): boolean {
  if (state.phase !== 'cooking') return false;

  const dx = playerPos.x - state.center.x;
  const dy = playerPos.y - state.center.y;
  const distance = Math.sqrt(dx * dx + dy * dy);

  return distance < state.currentRadius;
}

/**
 * Check if player is in the escape gap
 */
export function isPlayerInEscapeGap(
  state: LegacyBallState,
  playerPos: Vector2
): boolean {
  if (state.phase !== 'constrict') return false;

  // Calculate angle from center to player
  const dx = playerPos.x - state.center.x;
  const dy = playerPos.y - state.center.y;
  const playerAngle = Math.atan2(dy, dx);

  // Normalize angles to 0-2PI range
  const normalizeAngle = (a: number) => ((a % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
  const normalizedPlayerAngle = normalizeAngle(playerAngle);
  const normalizedGapAngle = normalizeAngle(state.gapAngle);

  // Check if player angle is within gap
  const gapStart = normalizedGapAngle - state.gapSize / 2;
  const gapEnd = normalizedGapAngle + state.gapSize / 2;

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
  const atEscapeDistance = distance >= state.currentRadius * 0.9;

  return inGap && atEscapeDistance;
}

/**
 * Get ball phase progress (0-1)
 */
export function getBallProgress(state: LegacyBallState): number {
  return state.phaseProgress;
}

/**
 * Get temperature (0-100)
 */
export function getBallTemperature(state: LegacyBallState): number {
  return state.temperature;
}

/**
 * Get formation bee count
 */
export function getFormationBeeCount(state: LegacyBallState): number {
  return state.formationBeeIds.length;
}

/**
 * Get escape count (how many times player has escaped)
 */
export function getEscapeCount(state: LegacyBallState): number {
  return state.escapeCount;
}

/**
 * Get the target position for a bee in formation
 */
export function getFormationPosition(
  state: LegacyBallState,
  beeId: string
): Vector2 | null {
  return state.formationPositions.get(beeId) ?? null;
}

/**
 * Get temperature color for visual effects
 */
export function getTemperatureColor(temperature: number): string {
  if (temperature < 40) {
    // Ambient - no color change
    return 'rgba(0, 0, 0, 0)';
  } else if (temperature < 60) {
    // Amber tint
    const alpha = (temperature - 40) / 20 * 0.3;
    return `rgba(244, 163, 0, ${alpha})`; // #F4A300
  } else if (temperature < 80) {
    // Pinkish-red (danger but not crisis yet)
    const alpha = 0.3 + (temperature - 60) / 20 * 0.2;
    return `rgba(255, 51, 102, ${alpha})`; // #FF3366 - distinct from player orange
  } else {
    // Red - danger!
    const alpha = 0.5 + (temperature - 80) / 20 * 0.3;
    return `rgba(255, 51, 102, ${alpha})`; // #FF3366
  }
}

/**
 * Get escape gap color (always bright to show escape route)
 */
export function getEscapeGapColor(phase: BallPhase): string {
  if (phase === 'constrict') {
    return 'rgba(0, 212, 255, 0.8)'; // Cyan - ESCAPE HERE
  }
  return 'rgba(0, 255, 136, 0.4)'; // Green hint during forming
}
