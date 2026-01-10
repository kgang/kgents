/**
 * THE BALL Formation System - Boundary Collision
 *
 * Handles knockback and damage when player touches THE BALL ring.
 * RUN 037 BALANCE: Reduced knockback (30px) - gentlest of all knockbacks.
 * RUN 038: No knockback when exiting through the escape gap!
 * RUN 039: Near-miss punishment - if player misses gap by <5%, punish hard!
 */

import type { Vector2 } from '../../types';
import type { BallEvent, BoundaryResult } from './types';
import { BALL_BOUNDARY_CONFIG, BALL_NEAR_MISS_CONFIG } from './config';

/**
 * Calculate distance from player angle to gap edge (returns 0-1, lower = closer to gap)
 */
function getDistanceToGapEdge(
  playerPos: Vector2,
  ballCenter: Vector2,
  gapAngle: number,
  gapSize: number
): { inGap: boolean; distanceToEdge: number } {
  // Calculate angle from center to player
  const dx = playerPos.x - ballCenter.x;
  const dy = playerPos.y - ballCenter.y;
  const playerAngle = Math.atan2(dy, dx);

  // Normalize angles to 0-2PI range
  const normalizeAngle = (a: number) => ((a % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
  const normalizedPlayerAngle = normalizeAngle(playerAngle);
  const normalizedGapAngle = normalizeAngle(gapAngle);

  // Calculate angular distance to gap center
  let angleDiff = Math.abs(normalizedPlayerAngle - normalizedGapAngle);
  if (angleDiff > Math.PI) {
    angleDiff = Math.PI * 2 - angleDiff;
  }

  // Player is in gap if within half the gap size
  const halfGap = gapSize / 2;
  const inGap = angleDiff <= halfGap;

  // Distance to edge is how far past the gap they are (as fraction of gap size)
  // 0 = exactly at edge, 1 = one full gap-width away
  const distanceToEdge = inGap ? 0 : (angleDiff - halfGap) / gapSize;

  return { inGap, distanceToEdge };
}

/**
 * Check for boundary collision and apply knockback/damage
 * RUN 038: Now checks for escape gap - no knockback when exiting through the gap!
 * RUN 039: Near-miss punishment with cooldown to prevent repeated triggering
 * RUN 042: hasKnockback flag controls whether boundary pushes player (tier 2 balls = no push)
 */
export function updateBoundaryCollision(
  playerPos: Vector2,
  ballCenter: Vector2,
  ballRadius: number,
  gapAngle: number,
  gapSize: number,
  isDissipating: boolean,
  lastBoundaryDamageTick: number,
  gameTime: number,
  hasKnockback: boolean = true,  // RUN 042: Tier 2 balls have no knockback
  lastNearMissTime: number = 0   // RUN 039: Track last near-miss to prevent spam
): BoundaryResult & { newLastDamageTick: number; newLastNearMissTime: number } {
  const events: BallEvent[] = [];
  let knockback: BoundaryResult['knockback'] = null;
  let damageDealt = 0;
  let newLastDamageTick = lastBoundaryDamageTick;
  let newLastNearMissTime = lastNearMissTime;

  // RUN 039: Near-miss cooldown (2 seconds - only trigger once per failed escape attempt)
  const NEAR_MISS_COOLDOWN = 2000;

  // Skip if dissipating
  if (isDissipating) {
    return { knockback, damageDealt, events, newLastDamageTick, newLastNearMissTime };
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
    // RUN 039: Check distance to gap edge for near-miss detection
    const { inGap, distanceToEdge } = getDistanceToGapEdge(playerPos, ballCenter, gapAngle, gapSize);

    if (inGap) {
      // Player is escaping through the gap - no knockback, no damage
      return { knockback, damageDealt, events, newLastDamageTick, newLastNearMissTime };
    }

    // Calculate direction toward center
    if (playerDistToCenter > 1) {
      const toCenterDir: Vector2 = {
        x: -dx / playerDistToCenter,  // Negative because we push toward center
        y: -dy / playerDistToCenter,
      };

      // RUN 039: Near-miss punishment - player almost made it but missed!
      // Only trigger if cooldown has elapsed (prevents spam and instant death)
      const isNearMiss = distanceToEdge < BALL_NEAR_MISS_CONFIG.nearMissThreshold;
      const nearMissCooldownElapsed = (gameTime - lastNearMissTime) >= NEAR_MISS_COOLDOWN;

      if (isNearMiss && nearMissCooldownElapsed) {
        // NEAR MISS! Pinball punishment - stun bounce is handled by game loop
        // We DON'T apply knockback here - the stun bounce system takes over
        // Mark near-miss time to prevent repeated triggers
        newLastNearMissTime = gameTime;

        // Emit near-miss event (triggers stun bounce in game loop)
        events.push({
          type: 'ball_near_miss',
          timestamp: gameTime,
          position: playerPos,
          data: {
            damage: BALL_BOUNDARY_CONFIG.damagePerTick,
            knockbackDirection: toCenterDir,
            knockbackForce: 0, // No knockback - stun bounce handles movement
            nearMissDistance: distanceToEdge,
          },
        });

        // Apply damage once on near-miss
        damageDealt = BALL_BOUNDARY_CONFIG.damagePerTick;
        newLastDamageTick = gameTime;
      } else if (!isNearMiss) {
        // RUN 042: Only apply knockback if hasKnockback is true
        // Tier 2 balls have visual-only boundary (no push)
        if (hasKnockback) {
          // Apply boundary knockback (RUN 037: Reduced to 30px)
          knockback = {
            direction: toCenterDir,
            force: BALL_BOUNDARY_CONFIG.knockbackForce,
          };
        }

        // Apply boundary damage on tick interval (damage still applies even without knockback)
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
              knockbackForce: hasKnockback ? BALL_BOUNDARY_CONFIG.knockbackForce : 0,
            },
          });
        }
      }
    }
  }

  return { knockback, damageDealt, events, newLastDamageTick, newLastNearMissTime };
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
