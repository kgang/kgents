/**
 * THE BALL Formation System - Bee Recruitment
 *
 * Manages bees joining and leaving THE BALL formation.
 * Also handles outside bee punches (RUN 037: 50px knockback).
 */

import type { Vector2 } from '../../types';
import type { BallFormationState, BallEvent } from './types';
import { BALL_MOVEMENT_CONFIG, BALL_OUTSIDE_PUNCH_CONFIG } from './config';

interface EnemyRef {
  id: string;
  position: Vector2;
}

/**
 * Update bee recruitment into the ball
 */
export function updateBeeRecruitment(
  formation: BallFormationState,
  enemies: EnemyRef[],
  ballCenter: Vector2
): BallFormationState {
  // Skip if at max capacity
  if (formation.beeIds.length >= BALL_MOVEMENT_CONFIG.maxBeesInBall) {
    return formation;
  }

  const newBeeIds = [...formation.beeIds];

  for (const enemy of enemies) {
    // Skip bees already in formation
    if (newBeeIds.includes(enemy.id)) continue;

    // Check if bee is within recruitment radius
    const dx = enemy.position.x - ballCenter.x;
    const dy = enemy.position.y - ballCenter.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < BALL_MOVEMENT_CONFIG.recruitmentRadius) {
      newBeeIds.push(enemy.id);

      if (newBeeIds.length >= BALL_MOVEMENT_CONFIG.maxBeesInBall) {
        break;
      }
    }
  }

  if (newBeeIds.length === formation.beeIds.length) {
    return formation; // No change
  }

  return {
    ...formation,
    beeIds: newBeeIds,
  };
}

/**
 * Update outside bee punches
 * Non-formation bees can punch player back toward ball center
 */
export function updateOutsidePunches(
  formation: BallFormationState,
  enemies: EnemyRef[],
  playerPos: Vector2,
  ballCenter: Vector2,
  gameTime: number
): {
  formation: BallFormationState;
  knockback: { direction: Vector2; force: number } | null;
  events: BallEvent[];
} {
  const events: BallEvent[] = [];
  let knockback: { direction: Vector2; force: number } | null = null;
  const newCooldowns = new Map(formation.outsidePunchCooldowns);

  for (const enemy of enemies) {
    // Skip bees in formation
    if (formation.beeIds.includes(enemy.id)) continue;

    // Check cooldown
    const cooldownEnd = newCooldowns.get(enemy.id);
    if (cooldownEnd !== undefined && gameTime < cooldownEnd) continue;

    // Check if enemy is close enough to player
    const dx = playerPos.x - enemy.position.x;
    const dy = playerPos.y - enemy.position.y;
    const dist = Math.sqrt(dx * dx + dy * dy);

    if (dist < BALL_OUTSIDE_PUNCH_CONFIG.range) {
      // Calculate punch direction (toward ball center)
      const punchDx = ballCenter.x - playerPos.x;
      const punchDy = ballCenter.y - playerPos.y;
      const punchDist = Math.sqrt(punchDx * punchDx + punchDy * punchDy);

      if (punchDist > 1) {
        const punchDir: Vector2 = {
          x: punchDx / punchDist,
          y: punchDy / punchDist,
        };

        // Set knockback (RUN 037: 50px)
        knockback = {
          direction: punchDir,
          force: BALL_OUTSIDE_PUNCH_CONFIG.knockbackForce,
        };

        events.push({
          type: 'outside_punch',
          timestamp: gameTime,
          position: enemy.position,
          data: {
            knockbackDirection: punchDir,
            knockbackForce: BALL_OUTSIDE_PUNCH_CONFIG.knockbackForce,
            lungingBeeId: enemy.id,
          },
        });

        // Set cooldown for this bee
        newCooldowns.set(enemy.id, gameTime + BALL_OUTSIDE_PUNCH_CONFIG.cooldown);

        // Only one punch per frame
        break;
      }
    }
  }

  return {
    formation: {
      ...formation,
      outsidePunchCooldowns: newCooldowns,
    },
    knockback,
    events,
  };
}

/**
 * Create initial formation state
 */
export function createInitialFormationState(initialBeeIds: string[]): BallFormationState {
  return {
    beeIds: initialBeeIds,
    positions: new Map(),
    outsidePunchCooldowns: new Map(),
  };
}

/**
 * Clean up stale bees from formation (bees that no longer exist)
 */
export function cleanupFormation(
  formation: BallFormationState,
  validEnemyIds: Set<string>
): BallFormationState {
  const validBeeIds = formation.beeIds.filter(id => validEnemyIds.has(id));

  if (validBeeIds.length === formation.beeIds.length) {
    return formation; // No change
  }

  return {
    ...formation,
    beeIds: validBeeIds,
  };
}
