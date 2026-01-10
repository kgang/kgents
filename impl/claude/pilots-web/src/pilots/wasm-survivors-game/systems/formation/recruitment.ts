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

// =============================================================================
// RUN 039: Outside Punch Telegraph System
// =============================================================================
// Punches now have a visible windup phase, making them dodgeable.
// State machine: idle → windup (400ms) → punch (100ms) → recovery (200ms) → idle
//
// Visual feedback during windup:
//   - Bee glows orange/red
//   - Direction line toward player
//   - Growing exclamation mark "!"
//   - Filling ring indicator
//
// Dodge mechanics:
//   - Player can move during 400ms windup
//   - Punch only hits if player is within hitRange (35px) at punch time
//   - If player moved outside hitRange, punch "whiffs" (no damage)

import type { OutsidePunchState } from './types';

/**
 * Update outside punch telegraph state machine
 * RUN 039: Full telegraph system with dodge window
 */
export function updateOutsidePunches(
  formation: BallFormationState,
  enemies: EnemyRef[],
  playerPos: Vector2,
  ballCenter: Vector2,
  gameTime: number,
  activePunches: OutsidePunchState[] = []
): {
  formation: BallFormationState;
  knockback: { direction: Vector2; force: number } | null;
  events: BallEvent[];
  updatedPunches: OutsidePunchState[];
} {
  const events: BallEvent[] = [];
  let knockback: { direction: Vector2; force: number } | null = null;
  const newCooldowns = new Map(formation.outsidePunchCooldowns);
  const updatedPunches: OutsidePunchState[] = [];

  // ==========================================================================
  // Phase 1: Update existing punches through state machine
  // ==========================================================================

  for (const punch of activePunches) {
    const elapsed = gameTime - punch.phaseStartTime;

    if (punch.phase === 'windup') {
      // Windup phase - telegraph is visible, player can dodge
      if (elapsed >= BALL_OUTSIDE_PUNCH_CONFIG.windupDuration) {
        // Transition to punch phase
        // Check if player is still in hit range
        const enemy = enemies.find(e => e.id === punch.beeId);
        if (enemy) {
          const dx = playerPos.x - enemy.position.x;
          const dy = playerPos.y - enemy.position.y;
          const dist = Math.sqrt(dx * dx + dy * dy);

          if (dist <= BALL_OUTSIDE_PUNCH_CONFIG.hitRange) {
            // HIT! Player didn't dodge in time
            knockback = {
              direction: punch.knockbackDir,
              force: BALL_OUTSIDE_PUNCH_CONFIG.knockbackForce,
            };

            events.push({
              type: 'punch_hit',
              timestamp: gameTime,
              position: enemy.position,
              data: {
                punchingBeeId: punch.beeId,
                knockbackDirection: punch.knockbackDir,
                knockbackForce: BALL_OUTSIDE_PUNCH_CONFIG.knockbackForce,
                dodged: false,
              },
            });
          } else {
            // WHIFF! Player dodged successfully
            events.push({
              type: 'punch_whiff',
              timestamp: gameTime,
              position: enemy.position,
              data: {
                punchingBeeId: punch.beeId,
                dodged: true,
              },
            });
          }

          // Transition to recovery phase either way
          updatedPunches.push({
            ...punch,
            phase: 'recovery',
            phaseStartTime: gameTime,
          });

          events.push({
            type: 'punch_recovery_started',
            timestamp: gameTime,
            position: enemy.position,
            data: { punchingBeeId: punch.beeId },
          });
        }
        // If enemy no longer exists, just drop the punch
      } else {
        // Still winding up - keep punch active
        updatedPunches.push(punch);
      }
    } else if (punch.phase === 'punch') {
      // Quick punch phase (mostly handled above, but for safety)
      if (elapsed >= BALL_OUTSIDE_PUNCH_CONFIG.punchDuration) {
        updatedPunches.push({
          ...punch,
          phase: 'recovery',
          phaseStartTime: gameTime,
        });
      } else {
        updatedPunches.push(punch);
      }
    } else if (punch.phase === 'recovery') {
      // Recovery phase - bee is cooling down
      if (elapsed >= BALL_OUTSIDE_PUNCH_CONFIG.recoveryDuration) {
        // Punch complete - set bee on cooldown
        newCooldowns.set(punch.beeId, gameTime + BALL_OUTSIDE_PUNCH_CONFIG.cooldown);
        // Don't add to updatedPunches - punch is done
      } else {
        updatedPunches.push(punch);
      }
    }
  }

  // ==========================================================================
  // Phase 2: Check for new punches to start (if under max active)
  // ==========================================================================

  const currentActiveCount = updatedPunches.filter(p => p.phase !== 'recovery').length;

  if (currentActiveCount < BALL_OUTSIDE_PUNCH_CONFIG.maxActivePunches) {
    for (const enemy of enemies) {
      // Skip bees in formation
      if (formation.beeIds.includes(enemy.id)) continue;

      // Skip bees already punching
      if (updatedPunches.some(p => p.beeId === enemy.id)) continue;

      // Check cooldown
      const cooldownEnd = newCooldowns.get(enemy.id);
      if (cooldownEnd !== undefined && gameTime < cooldownEnd) continue;

      // Check if enemy is close enough to START a punch (detection range)
      const dx = playerPos.x - enemy.position.x;
      const dy = playerPos.y - enemy.position.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < BALL_OUTSIDE_PUNCH_CONFIG.detectionRange) {
        // Calculate knockback direction (toward ball center)
        const punchDx = ballCenter.x - playerPos.x;
        const punchDy = ballCenter.y - playerPos.y;
        const punchDist = Math.sqrt(punchDx * punchDx + punchDy * punchDy);

        if (punchDist > 1) {
          const knockbackDir: Vector2 = {
            x: punchDx / punchDist,
            y: punchDy / punchDist,
          };

          // Start new punch in windup phase
          const newPunch: OutsidePunchState = {
            beeId: enemy.id,
            phase: 'windup',
            phaseStartTime: gameTime,
            startPos: { ...enemy.position },
            targetPos: { ...playerPos },
            knockbackDir,
          };

          updatedPunches.push(newPunch);

          events.push({
            type: 'punch_windup_started',
            timestamp: gameTime,
            position: enemy.position,
            data: {
              punchingBeeId: enemy.id,
              punchPhase: 'windup',
              windupProgress: 0,
            },
          });

          // Only start one new punch per frame for readability
          break;
        }
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
    updatedPunches,
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
