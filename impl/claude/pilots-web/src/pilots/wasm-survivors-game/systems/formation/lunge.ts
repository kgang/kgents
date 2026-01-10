/**
 * THE BALL Formation System - Lunge Attack State Machine
 *
 * RUN 040: Expanded windup with pullback + charge phases
 * RUN 042: Lunge scaling by enemy tier (hit radius, damage, windup speed)
 *
 * Phases:
 * - PULLBACK: Bee moves backward at normal speed (duration scales by type)
 * - CHARGE: Bee holds position, accelerating/charging visually (duration scales by type)
 * - ATTACK (400ms): Bee dashes toward player
 * - RETURN (200ms): Bee returns to formation
 *
 * Higher tier bees have:
 * - Larger hit radius (harder to dodge)
 * - More damage per hit
 * - SHORTER windup time (less reaction time = more dangerous)
 */

import type { Vector2 } from '../../types';
import type { BallLungeState, LungePhase, BallEvent, LungeUpdateResult } from './types';
import { BALL_LUNGE_CONFIG, getScaledLungeParams, getLungeScaling } from './config';

/**
 * Enemy reference with type information for lunge scaling
 */
interface EnemyRef {
  id: string;
  position: Vector2;
  type?: string;
}

/**
 * Update lunge attack state machine
 *
 * RUN 042: Now accepts enemy type information for scaled lunge parameters.
 * Higher tier enemies have larger hit radius, more damage, and FASTER windup.
 */
export function updateLungeAttack(
  lunge: BallLungeState,
  _ballCenter: Vector2,  // Unused - kept for API compatibility
  playerPos: Vector2,    // Used for event positions and new lunge target calculation
  formationBeeIds: string[],
  formationPositions: Map<string, Vector2>,
  gameTime: number,
  enemies?: EnemyRef[]   // RUN 042: Optional enemy list for type lookup
): LungeUpdateResult {
  const events: BallEvent[] = [];
  let knockback: LungeUpdateResult['knockback'] = null;
  let damageDealt = 0;
  const newLunge = { ...lunge };

  // RUN 042: Helper to get enemy type from ID
  const getEnemyType = (beeId: string): string => {
    if (!enemies) return 'worker';
    const enemy = enemies.find(e => e.id === beeId);
    return enemy?.type ?? 'worker';
  };

  // RUN 042: Get scaled durations for current lunge
  // These are computed at lunge start and stored on the lunge state
  const getScaledPullbackDuration = (): number => {
    if (newLunge.beeType) {
      const scaling = getLungeScaling(newLunge.beeType);
      return Math.round(BALL_LUNGE_CONFIG.pullbackDuration / scaling.windupSpeedMultiplier);
    }
    return BALL_LUNGE_CONFIG.pullbackDuration;
  };

  const getScaledChargeDuration = (): number => {
    if (newLunge.beeType) {
      const scaling = getLungeScaling(newLunge.beeType);
      return Math.round(BALL_LUNGE_CONFIG.chargeDuration / scaling.windupSpeedMultiplier);
    }
    return BALL_LUNGE_CONFIG.chargeDuration;
  };

  // Process current lunge phase
  if (newLunge.phase !== 'idle' && newLunge.beeId) {
    const elapsed = gameTime - newLunge.phaseStartTime;

    switch (newLunge.phase) {
      case 'pullback': {
        // PULLBACK PHASE: Bee moves backward at normal speed
        // RUN 042: Duration scales with bee type (faster for elite bees)
        const pullbackDuration = getScaledPullbackDuration();
        if (elapsed >= pullbackDuration) {
          // Transition to CHARGE phase
          newLunge.phase = 'charge';
          newLunge.phaseStartTime = gameTime;

          events.push({
            type: 'lunge_charge_started',
            timestamp: gameTime,
            position: newLunge.pullbackPos,
            data: { lungingBeeId: newLunge.beeId },
          });
        }
        break;
      }

      case 'charge': {
        // CHARGE PHASE: Bee holds position, building energy
        // RUN 042: Duration scales with bee type (faster for elite bees)
        const chargeDuration = getScaledChargeDuration();
        if (elapsed >= chargeDuration) {
          // Transition to LUNGE phase
          newLunge.phase = 'lunge';
          newLunge.phaseStartTime = gameTime;

          events.push({
            type: 'lunge_attack_started',
            timestamp: gameTime,
            position: newLunge.pullbackPos,
            data: { lungingBeeId: newLunge.beeId },
          });
        }
        break;
      }

      case 'lunge': {
        // LUNGE PHASE: Bee dashes toward player
        if (elapsed >= BALL_LUNGE_CONFIG.attackDuration) {
          // Check if the bee actually hit the player
          // Bee ends up at targetPos, check distance to player's CURRENT position
          const hitDx = playerPos.x - newLunge.targetPos.x;
          const hitDy = playerPos.y - newLunge.targetPos.y;
          const hitDist = Math.sqrt(hitDx * hitDx + hitDy * hitDy);

          // RUN 042: Use scaled hit radius (larger for elite bees)
          const effectiveHitRadius = newLunge.scaledHitRadius > 0
            ? newLunge.scaledHitRadius
            : BALL_LUNGE_CONFIG.hitRadius;

          const didHit = hitDist <= effectiveHitRadius;

          if (didHit) {
            // HIT CONFIRMED - Apply knockback in the bee's travel direction
            // Direction is from pullback position to target (the actual lunge direction)
            const lungeDx = newLunge.targetPos.x - newLunge.pullbackPos.x;
            const lungeDy = newLunge.targetPos.y - newLunge.pullbackPos.y;
            const lungeDist = Math.sqrt(lungeDx * lungeDx + lungeDy * lungeDy);

            if (lungeDist > 1) {
              // Knockback direction = bee's travel direction (normalized)
              const knockbackDir: Vector2 = {
                x: lungeDx / lungeDist,
                y: lungeDy / lungeDist,
              };

              // Apply knockback (RUN 037: 80px in travel direction)
              knockback = {
                direction: knockbackDir,
                force: BALL_LUNGE_CONFIG.knockbackForce,
              };

              // RUN 042: Use scaled damage (higher for elite bees)
              const effectiveDamage = newLunge.scaledDamage > 0
                ? newLunge.scaledDamage
                : BALL_LUNGE_CONFIG.damage;

              damageDealt = effectiveDamage;

              events.push({
                type: 'lunge_hit',
                timestamp: gameTime,
                position: playerPos,
                data: {
                  knockbackDirection: knockbackDir,
                  knockbackForce: BALL_LUNGE_CONFIG.knockbackForce,
                  lungingBeeId: newLunge.beeId,
                  damage: effectiveDamage,
                },
              });
            }
          }
          // If missed, no knockback or damage - bee just returns to formation

          // Transition to RETURN phase
          newLunge.phase = 'return';
          newLunge.phaseStartTime = gameTime;

          events.push({
            type: 'lunge_return_started',
            timestamp: gameTime,
            position: playerPos,
            data: { lungingBeeId: newLunge.beeId },
          });
        }
        break;
      }

      case 'return': {
        // RETURN PHASE: Bee returns to formation
        if (elapsed >= BALL_LUNGE_CONFIG.returnDuration) {
          // Return complete - back to idle
          newLunge.phase = 'idle';
          newLunge.beeId = null;
          newLunge.beeType = null;
          // Reset scaled values
          newLunge.scaledHitRadius = 0;
          newLunge.scaledDamage = 0;
          newLunge.scaledWindupDuration = 0;
        }
        break;
      }
    }
  }

  // Start a new lunge if ready
  if (newLunge.phase === 'idle' && formationBeeIds.length > 0) {
    if (gameTime - newLunge.lastLungeTime >= newLunge.nextLungeInterval) {
      // Pick a random bee from formation to lunge
      const lungingBeeId = formationBeeIds[
        Math.floor(Math.random() * formationBeeIds.length)
      ];

      // Find the bee's current position (from formation positions)
      const beeFormationPos = formationPositions.get(lungingBeeId);
      if (beeFormationPos) {
        // RUN 042: Get enemy type and compute scaled parameters
        const beeType = getEnemyType(lungingBeeId);
        const scaledParams = getScaledLungeParams(beeType);

        // Calculate lunge direction (toward player)
        const toPlayerDx = playerPos.x - beeFormationPos.x;
        const toPlayerDy = playerPos.y - beeFormationPos.y;
        const toPlayerDist = Math.sqrt(toPlayerDx * toPlayerDx + toPlayerDy * toPlayerDy);

        if (toPlayerDist > 1) {
          // Normalize direction
          const dirX = toPlayerDx / toPlayerDist;
          const dirY = toPlayerDy / toPlayerDist;

          // Calculate pullback position (move backward from formation pos)
          const pullbackX = beeFormationPos.x - dirX * BALL_LUNGE_CONFIG.pullbackDistance;
          const pullbackY = beeFormationPos.y - dirY * BALL_LUNGE_CONFIG.pullbackDistance;

          // RUN 039: Calculate lunge target as 120% of distance (20% overshoot)
          const totalDistance = toPlayerDist * (1 + BALL_LUNGE_CONFIG.overshootPercent);
          const lungeTargetX = beeFormationPos.x + dirX * totalDistance;
          const lungeTargetY = beeFormationPos.y + dirY * totalDistance;

          // Start in PULLBACK phase
          newLunge.phase = 'pullback';
          newLunge.beeId = lungingBeeId;
          newLunge.beeType = beeType;  // RUN 042: Store bee type for scaling
          newLunge.phaseStartTime = gameTime;
          newLunge.startPos = { ...beeFormationPos };
          newLunge.pullbackPos = { x: pullbackX, y: pullbackY };
          newLunge.targetPos = { x: lungeTargetX, y: lungeTargetY };

          // RUN 042: Store scaled parameters
          newLunge.scaledHitRadius = scaledParams.hitRadius;
          newLunge.scaledDamage = scaledParams.damage;
          newLunge.scaledWindupDuration = scaledParams.windupDuration;

          // Emit both pullback event and legacy windup event for compatibility
          events.push({
            type: 'lunge_pullback_started',
            timestamp: gameTime,
            position: beeFormationPos,
            data: { lungingBeeId },
          });

          events.push({
            type: 'lunge_windup_started',
            timestamp: gameTime,
            position: beeFormationPos,
            data: { lungingBeeId },
          });
        }
      }

      // Set next lunge interval (whether or not we found a valid bee)
      newLunge.lastLungeTime = gameTime;
      newLunge.nextLungeInterval = BALL_LUNGE_CONFIG.intervalMin +
        Math.random() * (BALL_LUNGE_CONFIG.intervalMax - BALL_LUNGE_CONFIG.intervalMin);
    }
  }

  return { state: newLunge, events, knockback, damageDealt };
}

/**
 * Create initial lunge state
 *
 * RUN 042: Added beeType and scaled parameter fields
 */
export function createInitialLungeState(gameTime: number): BallLungeState {
  return {
    phase: 'idle',
    beeId: null,
    beeType: null,              // RUN 042: Enemy type for lunge scaling
    phaseStartTime: 0,
    startPos: { x: 0, y: 0 },
    pullbackPos: { x: 0, y: 0 },
    targetPos: { x: 0, y: 0 },
    // RUN 042: Scaled parameters (set to 0 when idle)
    scaledHitRadius: 0,
    scaledDamage: 0,
    scaledWindupDuration: 0,
    lastLungeTime: gameTime,
    nextLungeInterval: BALL_LUNGE_CONFIG.intervalMax,
  };
}

/**
 * Get lunge progress (0-1) for animations
 *
 * RUN 042: Uses scaled windup duration when bee type is set
 */
export function getLungeProgress(
  lunge: BallLungeState,
  gameTime: number
): { phase: LungePhase; progress: number } {
  if (lunge.phase === 'idle') {
    return { phase: 'idle', progress: 0 };
  }

  const elapsed = gameTime - lunge.phaseStartTime;
  let duration: number;

  // RUN 042: Calculate scaled durations based on bee type
  const getScaledPullbackDuration = (): number => {
    if (lunge.beeType) {
      const scaling = getLungeScaling(lunge.beeType);
      return Math.round(BALL_LUNGE_CONFIG.pullbackDuration / scaling.windupSpeedMultiplier);
    }
    return BALL_LUNGE_CONFIG.pullbackDuration;
  };

  const getScaledChargeDuration = (): number => {
    if (lunge.beeType) {
      const scaling = getLungeScaling(lunge.beeType);
      return Math.round(BALL_LUNGE_CONFIG.chargeDuration / scaling.windupSpeedMultiplier);
    }
    return BALL_LUNGE_CONFIG.chargeDuration;
  };

  switch (lunge.phase) {
    case 'pullback':
      duration = getScaledPullbackDuration();
      break;
    case 'charge':
      duration = getScaledChargeDuration();
      break;
    case 'lunge':
      duration = BALL_LUNGE_CONFIG.attackDuration;
      break;
    case 'return':
      duration = BALL_LUNGE_CONFIG.returnDuration;
      break;
    default:
      return { phase: 'idle', progress: 0 };
  }

  return {
    phase: lunge.phase,
    progress: Math.min(1, elapsed / duration),
  };
}

/**
 * Calculate current position of lunging bee (for rendering/physics)
 */
export function getLungingBeePosition(
  lunge: BallLungeState,
  gameTime: number
): Vector2 | null {
  if (lunge.phase === 'idle' || !lunge.beeId) {
    return null;
  }

  const { phase, progress } = getLungeProgress(lunge, gameTime);

  switch (phase) {
    case 'pullback': {
      // Move backward from startPos to pullbackPos at constant speed
      // Linear interpolation - bee moves at normal speed
      return {
        x: lunge.startPos.x + (lunge.pullbackPos.x - lunge.startPos.x) * progress,
        y: lunge.startPos.y + (lunge.pullbackPos.y - lunge.startPos.y) * progress,
      };
    }

    case 'charge': {
      // Hold at pullback position (slight vibration for visual effect)
      const vibration = Math.sin(gameTime * 0.05) * 2 * progress; // Increasing vibration
      const dx = lunge.targetPos.x - lunge.pullbackPos.x;
      const dy = lunge.targetPos.y - lunge.pullbackPos.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist === 0) return lunge.pullbackPos;

      // Vibrate perpendicular to lunge direction
      return {
        x: lunge.pullbackPos.x + (-dy / dist) * vibration,
        y: lunge.pullbackPos.y + (dx / dist) * vibration,
      };
    }

    case 'lunge': {
      // Ease-out dash from pullbackPos toward target
      const easedProgress = 1 - Math.pow(1 - progress, 3);
      return {
        x: lunge.pullbackPos.x + (lunge.targetPos.x - lunge.pullbackPos.x) * easedProgress,
        y: lunge.pullbackPos.y + (lunge.targetPos.y - lunge.pullbackPos.y) * easedProgress,
      };
    }

    case 'return': {
      // Ease-in return from targetPos to startPos (original formation position)
      const easedProgress = Math.pow(progress, 2);
      return {
        x: lunge.targetPos.x + (lunge.startPos.x - lunge.targetPos.x) * easedProgress,
        y: lunge.targetPos.y + (lunge.startPos.y - lunge.targetPos.y) * easedProgress,
      };
    }

    default:
      return null;
  }
}

/**
 * Check if a specific bee is currently lunging
 */
export function isBeeInLunge(lunge: BallLungeState, beeId: string): boolean {
  return lunge.beeId === beeId && lunge.phase !== 'idle';
}

/**
 * Check if bee is in telegraph phase (pullback or charge - attack is coming!)
 */
export function isBeeInTelegraph(lunge: BallLungeState): boolean {
  return lunge.phase === 'pullback' || lunge.phase === 'charge';
}

/**
 * Get the total windup progress (0-1) across both pullback and charge phases
 * Useful for rendering a single "charging" indicator
 */
export function getWindupProgress(lunge: BallLungeState, gameTime: number): number {
  if (lunge.phase === 'idle') return 0;
  if (lunge.phase === 'lunge' || lunge.phase === 'return') return 1;

  const { phase, progress } = getLungeProgress(lunge, gameTime);

  if (phase === 'pullback') {
    // Pullback is first half of windup
    return progress * 0.5;
  } else if (phase === 'charge') {
    // Charge is second half of windup
    return 0.5 + progress * 0.5;
  }

  return 0;
}
