/**
 * THE BALL Formation System - Boundary Collision
 *
 * Handles knockback and damage when player touches THE BALL ring.
 * RUN 037 BALANCE: Reduced knockback (30px) - gentlest of all knockbacks.
 * RUN 038: No knockback when exiting through the escape gap!
 */

import type { Vector2 } from '../../types';
import type { BallEvent, BoundaryResult } from './types';
import { BALL_BOUNDARY_CONFIG } from './config';

/**
 * Check if player is in the escape gap
 */
function isPlayerInGap(
  playerPos: Vector2,
  ballCenter: Vector2,
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
  if (gapStart < 0) {
    return normalizedPlayerAngle >= normalizeAngle(gapStart) ||
           normalizedPlayerAngle <= gapEnd;
  } else if (gapEnd > Math.PI * 2) {
    return normalizedPlayerAngle >= gapStart ||
           normalizedPlayerAngle <= normalizeAngle(gapEnd);
  } else {
    return normalizedPlayerAngle >= gapStart && normalizedPlayerAngle <= gapEnd;
  }
}

/**
 * Check for boundary collision and apply knockback/damage
 * RUN 038: Now checks for escape gap - no knockback when exiting through the gap!
 */
export function updateBoundaryCollision(
  playerPos: Vector2,
  ballCenter: Vector2,
  ballRadius: number,
  gapAngle: number,
  gapSize: number,
  isDissipating: boolean,
  lastBoundaryDamageTick: number,
  gameTime: number
): BoundaryResult & { newLastDamageTick: number } {
  const events: BallEvent[] = [];
  let knockback: BoundaryResult['knockback'] = null;
  let damageDealt = 0;
  let newLastDamageTick = lastBoundaryDamageTick;

  // Skip if dissipating
  if (isDissipating) {
    return { knockback, damageDealt, events, newLastDamageTick };
  }

  // Calculate distance from player to ball center
  const dx = playerPos.x - ballCenter.x;
  const dy = playerPos.y - ballCenter.y;
  const playerDistToCenter = Math.sqrt(dx * dx + dy * dy);

  // Check if player is touching the ring (within margin)
  const distToRing = Math.abs(playerDistToCenter - ballRadius);
  const isTouchingRing = distToRing < BALL_BOUNDARY_CONFIG.touchMargin &&
                         playerDistToCenter > ballRadius * 0.5;

  if (isTouchingRing) {
    // RUN 038: Check if player is in the escape gap - if so, no knockback!
    const inEscapeGap = isPlayerInGap(playerPos, ballCenter, gapAngle, gapSize);

    if (inEscapeGap) {
      // Player is escaping through the gap - no knockback, no damage
      return { knockback, damageDealt, events, newLastDamageTick };
    }

    // Calculate direction toward center
    if (playerDistToCenter > 1) {
      const toCenterDir: Vector2 = {
        x: -dx / playerDistToCenter,  // Negative because we push toward center
        y: -dy / playerDistToCenter,
      };

      // Apply boundary knockback (RUN 037: Reduced to 30px)
      knockback = {
        direction: toCenterDir,
        force: BALL_BOUNDARY_CONFIG.knockbackForce,
      };

      // Apply boundary damage on tick interval
      if (gameTime - lastBoundaryDamageTick >= BALL_BOUNDARY_CONFIG.tickInterval) {
        damageDealt = BALL_BOUNDARY_CONFIG.damagePerTick;
        newLastDamageTick = gameTime;

        events.push({
          type: 'boundary_touch',
          timestamp: gameTime,
          position: playerPos,
          data: {
            damage: BALL_BOUNDARY_CONFIG.damagePerTick,
            knockbackDirection: toCenterDir,
            knockbackForce: BALL_BOUNDARY_CONFIG.knockbackForce,
          },
        });
      }
    }
  }

  return { knockback, damageDealt, events, newLastDamageTick };
}

/**
 * Check if player is inside the ball (for trapping detection)
 */
export function isPlayerInsideBall(
  playerPos: Vector2,
  ballCenter: Vector2,
  ballRadius: number
): boolean {
  const dx = playerPos.x - ballCenter.x;
  const dy = playerPos.y - ballCenter.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  return distance < ballRadius * 0.9;
}

/**
 * Check if player is outside the ball (for dissipation tracking)
 */
export function isPlayerOutsideBall(
  playerPos: Vector2,
  ballCenter: Vector2,
  ballRadius: number
): boolean {
  const dx = playerPos.x - ballCenter.x;
  const dy = playerPos.y - ballCenter.y;
  const distance = Math.sqrt(dx * dx + dy * dy);
  return distance > ballRadius * 1.1;
}
