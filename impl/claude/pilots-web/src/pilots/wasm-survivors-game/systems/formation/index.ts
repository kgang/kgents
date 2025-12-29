/**
 * THE BALL Formation System - Main Orchestrator
 *
 * The signature mechanic: bees surround and cook the hornet.
 * This is the CLIP-WORTHY SPECTACLE moment.
 *
 * RUN 037 BALANCE CHANGES:
 * - Knockback reduced: lunge 80px (was 200), punch 50px (was 80), boundary 30px (was 60)
 * - Lunge timing increased: windup 600ms (was 350), travel 400ms (was 150)
 * - Total lunge cycle: ~1200ms (highly readable, dodgeable)
 *
 * Architecture:
 * - Follows telegraph/state machine pattern from enemies.ts and melee.ts
 * - Separated into focused sub-modules
 * - Main updateBallFormation() orchestrates all sub-updates
 *
 * @see pilots/wasm-survivors-game/PROTO_SPEC.md (Part XI Phase 1)
 */

import type { Vector2 } from '../../types';
import type {
  LegacyBallState,
  BallEvent,
  BallUpdateResult,
  BallManagerState,
} from './types';
import { BALL_CONFIG, BALL_PHASE_CONFIG, BALL_GAP_CONFIG, BALL_COOKING_CONFIG } from './config';
import { updateGapRotation, createInitialGapState, interpolateGapSize } from './gap';
import { updateBallMovement, calculateFormationPositions, isInEscapeGap, interpolateFormingRadius, interpolateConstrictRadius, createInitialGeometryState } from './geometry';
import { shouldStartBall, calculateTemperature } from './phase';
import { updateBoundaryCollision } from './boundary';
import { updateBeeRecruitment, updateOutsidePunches } from './recruitment';
import { updateDissipation, getDissipatingRadius } from './dissipation';
import { BALL_LUNGE_CONFIG } from './config';

// Re-export types
export type { BallPhase, LegacyBallState as BallState, BallEvent, BallUpdateResult, BallTelegraphData, BallManagerState } from './types';

// Backwards compatibility: FormationEvent was the old name for BallEvent
export type { BallEvent as FormationEvent } from './types';

// Re-export config
export { BALL_CONFIG } from './config';

// Re-export query functions
export {
  isBallActive,
  isBallForming,
  isBallInSilence,
  isBallConstricting,
  isBallCooking,
  isBallDissipating,
  isBallFading,
  canBallBeRevived,
  getBallFadeProgress,
  isLungeInProgress,
  isBeeInFormationLunge,
  isBeeInFormation,
  isPlayerTrapped,
  isPlayerInEscapeGap,
  getBallProgress,
  getBallTemperature,
  getFormationBeeCount,
  getEscapeCount,
  getFormationPosition,
  getTemperatureColor,
  getEscapeGapColor,
} from './queries';

// Re-export telegraph functions
export { getBallTelegraph, getBallAudioParams, getBallCameraState } from './telegraph';

// Re-export geometry helpers
export { calculateFormationPositions, isInEscapeGap } from './geometry';

// =============================================================================
// Factory
// =============================================================================

/**
 * Create initial BALL state (inactive)
 */
export function createBallState(ballId: number = 0, tier: 1 | 2 = 1): LegacyBallState {
  const radiusMultiplier = tier === 2 ? BALL_PHASE_CONFIG.secondBallRadiusMultiplier : 1;
  return {
    phase: 'inactive',
    phaseStartTime: 0,
    phaseProgress: 0,
    center: { x: 400, y: 300 },
    currentRadius: BALL_PHASE_CONFIG.initialRadius * radiusMultiplier,
    gapAngle: 0,
    gapSize: (BALL_GAP_CONFIG.initialGapDegrees * Math.PI) / 180,
    targetPosition: { x: 400, y: 300 },
    velocity: { x: 0, y: 0 },
    gapRotationSpeed: BALL_GAP_CONFIG.rotationSpeedMin,
    gapRotationDirection: 1,
    lastDirectionChange: 0,
    lastSpeedChange: 0,
    lastLungeTime: 0,
    nextLungeInterval: BALL_LUNGE_CONFIG.intervalMax,
    activeLunge: null,
    lastBoundaryDamageTick: 0,
    playerOutsideTime: 0,
    isDissipating: false,
    dissipationStartTime: 0,
    // Fade/linger (RUN 039)
    isFading: false,
    fadeProgress: 0,
    fadeStartTime: 0,
    outsideBeePunchCooldowns: new Map(),
    formationBeeIds: [],
    formationPositions: new Map(),
    temperature: 0,
    lastDamageTick: 0,
    playerEscaped: false,
    escapeCount: 0,
    // Multi-ball (RUN 041)
    ballTier: tier,
    ballId,
  };
}

/**
 * Create initial ball manager state
 */
export function createBallManagerState(): BallManagerState {
  return {
    balls: [],
    beeCooldowns: new Map(),
    lastBallEndTime: 0,
    nextBallId: 1,
  };
}

/**
 * Get eligible enemies (not on cooldown)
 */
export function getEligibleEnemies(
  enemies: Array<{ id: string; position: Vector2 }>,
  beeCooldowns: Map<string, number>,
  gameTime: number,
  excludeBeeIds: Set<string> = new Set()
): Array<{ id: string; position: Vector2 }> {
  return enemies.filter(e => {
    // Exclude bees already in another ball
    if (excludeBeeIds.has(e.id)) return false;
    // Check cooldown
    const cooldownExpiry = beeCooldowns.get(e.id);
    if (cooldownExpiry && gameTime < cooldownExpiry) return false;
    return true;
  });
}

/**
 * Force THE BALL to start forming (debug/testing)
 */
export function forceBallStart(
  currentState: LegacyBallState,
  playerPos: Vector2,
  enemies: Array<{ id: string; position: Vector2 }>,
  gameTime: number
): LegacyBallState {
  if (currentState.phase !== 'inactive') {
    return currentState;
  }

  const minBeesForForce = 3;
  if (enemies.length < minBeesForForce) {
    return currentState;
  }

  const gapState = createInitialGapState(gameTime);
  const geometryState = createInitialGeometryState(playerPos);

  return {
    ...currentState,
    phase: 'forming',
    phaseStartTime: gameTime,
    phaseProgress: 0,
    center: geometryState.center,
    currentRadius: geometryState.currentRadius,
    gapAngle: gapState.angle,
    gapSize: gapState.size,
    targetPosition: geometryState.targetPosition,
    velocity: geometryState.velocity,
    gapRotationSpeed: gapState.rotationSpeed,
    gapRotationDirection: gapState.rotationDirection,
    lastDirectionChange: gapState.lastDirectionChange,
    lastSpeedChange: gapState.lastSpeedChange,
    lastLungeTime: gameTime,
    nextLungeInterval: BALL_LUNGE_CONFIG.intervalMin +
      Math.random() * (BALL_LUNGE_CONFIG.intervalMax - BALL_LUNGE_CONFIG.intervalMin),
    activeLunge: null,
    lastBoundaryDamageTick: 0,
    playerOutsideTime: 0,
    isDissipating: false,
    dissipationStartTime: 0,
    // Fade/linger (RUN 039)
    isFading: false,
    fadeProgress: 0,
    fadeStartTime: 0,
    outsideBeePunchCooldowns: new Map(),
    formationBeeIds: enemies.slice(0, Math.min(enemies.length, BALL_PHASE_CONFIG.minBeesForBall)).map(e => e.id),
    formationPositions: new Map(),
    temperature: 0,
    playerEscaped: false,
    // Multi-ball (RUN 041)
    ballTier: currentState.ballTier,
    ballId: currentState.ballId,
  };
}

// =============================================================================
// Main Update Function
// =============================================================================

interface EnemyRef {
  id: string;
  position: Vector2;
  type?: string;
}

/**
 * Multi-ball manager update result
 */
export interface BallManagerUpdateResult {
  manager: BallManagerState;
  ballResults: BallUpdateResult[];
  totalDamage: number;
  combinedKnockback: { direction: Vector2; force: number } | null;
  allEvents: BallEvent[];
}

/**
 * Update all balls via the manager
 *
 * RUN 041: Handles multiple balls with bee cooldowns
 */
export function updateBallManager(
  manager: BallManagerState,
  playerPos: Vector2,
  enemies: EnemyRef[],
  gameTime: number,
  deltaTime: number,
  wave: number
): BallManagerUpdateResult {
  const allEvents: BallEvent[] = [];
  const ballResults: BallUpdateResult[] = [];
  let totalDamage = 0;
  let combinedKnockback: { direction: Vector2; force: number } | null = null;

  // Clean up expired cooldowns
  const newBeeCooldowns = new Map(manager.beeCooldowns);
  for (const [beeId, expiry] of newBeeCooldowns) {
    if (gameTime >= expiry) {
      newBeeCooldowns.delete(beeId);
    }
  }

  // Collect all bees currently in active balls
  const beesInBalls = new Set<string>();
  for (const ball of manager.balls) {
    if (ball.phase !== 'inactive') {
      for (const beeId of ball.formationBeeIds) {
        beesInBalls.add(beeId);
      }
    }
  }

  // Get eligible enemies (not on cooldown, not in another ball)
  const eligibleEnemies = getEligibleEnemies(enemies, newBeeCooldowns, gameTime, beesInBalls);

  // Update existing balls and track which ones ended
  const updatedBalls: LegacyBallState[] = [];
  let lastBallEndTime = manager.lastBallEndTime;

  for (const ball of manager.balls) {
    const result = updateSingleBall(ball, playerPos, enemies, gameTime, deltaTime, wave);
    ballResults.push(result);
    allEvents.push(...result.events);
    totalDamage += result.damageToPlayer;

    // Combine knockback
    if (result.knockback) {
      if (!combinedKnockback) {
        combinedKnockback = { ...result.knockback };
      } else {
        combinedKnockback.direction.x += result.knockback.direction.x * result.knockback.force;
        combinedKnockback.direction.y += result.knockback.direction.y * result.knockback.force;
        combinedKnockback.force += result.knockback.force;
      }
    }

    // Check if ball ended (went from active to inactive)
    if (ball.phase !== 'inactive' && result.state.phase === 'inactive') {
      lastBallEndTime = gameTime;
      // Apply bee cooldown to all bees that were in this ball
      for (const beeId of ball.formationBeeIds) {
        newBeeCooldowns.set(beeId, gameTime + BALL_PHASE_CONFIG.beeCooldownAfterDisperse);
      }
      console.log(`[BALL] Dispersed. ${ball.formationBeeIds.length} bees on cooldown for 4s`);
    }

    // Keep ball if still active
    if (result.state.phase !== 'inactive') {
      updatedBalls.push(result.state);
    }
  }

  // Normalize combined knockback direction
  if (combinedKnockback && combinedKnockback.force > 0) {
    const mag = Math.sqrt(
      combinedKnockback.direction.x ** 2 + combinedKnockback.direction.y ** 2
    );
    if (mag > 0) {
      combinedKnockback.direction.x /= mag;
      combinedKnockback.direction.y /= mag;
    }
  }

  let nextBallId = manager.nextBallId;

  // Try to start a new ball (tier 1) if none active
  const hasActiveBall = updatedBalls.some(b => b.phase !== 'inactive');
  if (!hasActiveBall) {
    if (shouldStartBall(eligibleEnemies.length, wave, 'inactive', lastBallEndTime, gameTime, false)) {
      const newBall = startNewBall(nextBallId++, 1, eligibleEnemies, playerPos, gameTime);
      updatedBalls.push(newBall.state);
      allEvents.push(newBall.event);
      console.log(`[BALL] 🐝 FORMING tier 1! wave: ${wave}, eligible bees: ${eligibleEnemies.length}`);
    }
  } else if (updatedBalls.length < 2) {
    // Try to start second ball (tier 2) if first is active
    // Exclude bees in first ball from eligibility
    const firstBallBees = new Set(updatedBalls[0]?.formationBeeIds ?? []);
    const secondBallEligible = eligibleEnemies.filter(e => !firstBallBees.has(e.id));

    if (shouldStartBall(secondBallEligible.length, wave, 'inactive', lastBallEndTime, gameTime, true)) {
      const newBall = startNewBall(nextBallId++, 2, secondBallEligible, playerPos, gameTime);
      updatedBalls.push(newBall.state);
      allEvents.push(newBall.event);
      console.log(`[BALL] 🐝🐝 SECOND BALL forming (tier 2)! Bees: ${secondBallEligible.length}`);
    }
  }

  return {
    manager: {
      balls: updatedBalls,
      beeCooldowns: newBeeCooldowns,
      lastBallEndTime,
      nextBallId,
    },
    ballResults,
    totalDamage,
    combinedKnockback,
    allEvents,
  };
}

/**
 * Start a new ball formation
 */
function startNewBall(
  ballId: number,
  tier: 1 | 2,
  eligibleEnemies: Array<{ id: string; position: Vector2 }>,
  playerPos: Vector2,
  gameTime: number
): { state: LegacyBallState; event: BallEvent } {
  const gapState = createInitialGapState(gameTime);
  const geometryState = createInitialGeometryState(playerPos);
  const radiusMultiplier = tier === 2 ? BALL_PHASE_CONFIG.secondBallRadiusMultiplier : 1;
  const minBees = tier === 2
    ? BALL_PHASE_CONFIG.minBeesForBall + BALL_PHASE_CONFIG.secondBallMinBeesExtra
    : BALL_PHASE_CONFIG.minBeesForBall;

  const state: LegacyBallState = {
    phase: 'forming',
    phaseStartTime: gameTime,
    phaseProgress: 0,
    center: geometryState.center,
    currentRadius: geometryState.currentRadius * radiusMultiplier,
    gapAngle: gapState.angle,
    gapSize: gapState.size,
    targetPosition: geometryState.targetPosition,
    velocity: geometryState.velocity,
    gapRotationSpeed: gapState.rotationSpeed,
    gapRotationDirection: gapState.rotationDirection,
    lastDirectionChange: gapState.lastDirectionChange,
    lastSpeedChange: gapState.lastSpeedChange,
    lastLungeTime: gameTime,
    nextLungeInterval: BALL_LUNGE_CONFIG.intervalMin +
      Math.random() * (BALL_LUNGE_CONFIG.intervalMax - BALL_LUNGE_CONFIG.intervalMin),
    activeLunge: null,
    lastBoundaryDamageTick: 0,
    playerOutsideTime: 0,
    isDissipating: false,
    dissipationStartTime: 0,
    isFading: false,
    fadeProgress: 0,
    fadeStartTime: 0,
    outsideBeePunchCooldowns: new Map(),
    formationBeeIds: eligibleEnemies.slice(0, minBees).map(e => e.id),
    formationPositions: new Map(),
    temperature: 0,
    lastDamageTick: 0,
    playerEscaped: false,
    escapeCount: 0,
    ballTier: tier,
    ballId,
  };

  const event: BallEvent = {
    type: 'ball_forming_started',
    timestamp: gameTime,
    position: playerPos,
  };

  return { state, event };
}

/**
 * Update a single ball (internal - called by manager)
 */
function updateSingleBall(
  ballState: LegacyBallState,
  playerPos: Vector2,
  enemies: EnemyRef[],
  gameTime: number,
  deltaTime: number,
  wave: number
): BallUpdateResult {
  // If inactive, nothing to do
  if (ballState.phase === 'inactive') {
    return {
      state: ballState,
      events: [],
      damageToPlayer: 0,
      knockback: null,
      knockbackSources: [],
    };
  }

  // Rest of the update logic (same as before, but without the formation check)
  return updateBallFormationCore(ballState, playerPos, enemies, gameTime, deltaTime, wave);
}

/**
 * Update THE BALL formation state (legacy single-ball API)
 *
 * Main orchestrator that calls all sub-updates in order.
 * For new code, prefer updateBallManager() for multi-ball support.
 */
export function updateBallFormation(
  ballState: LegacyBallState,
  playerPos: Vector2,
  enemies: EnemyRef[],
  gameTime: number,
  deltaTime: number,
  wave: number,
  // RUN 041: Optional manager state for proper cooldowns
  managerState?: { lastBallEndTime: number; beeCooldowns: Map<string, number> }
): BallUpdateResult {
  const events: BallEvent[] = [];
  let damageToPlayer = 0;
  let knockback: BallUpdateResult['knockback'] = null;
  let newState = { ...ballState };

  // RUN 038: Collect all knockback sources, then combine into final position
  const knockbackSources: Array<{
    type: 'lunge' | 'boundary' | 'punch';
    direction: Vector2;
    force: number;
  }> = [];

  // ==========================================================================
  // Check if should start forming
  // ==========================================================================

  if (ballState.phase === 'inactive') {
    // Get eligible enemies (filter by cooldown if manager state provided)
    const eligibleEnemies = managerState
      ? getEligibleEnemies(enemies, managerState.beeCooldowns, gameTime)
      : enemies;
    const lastBallEndTime = managerState?.lastBallEndTime ?? 0;

    if (shouldStartBall(eligibleEnemies.length, wave, ballState.phase, lastBallEndTime, gameTime, false)) {
      console.log('[BALL] 🐝 FORMING! wave:', wave, 'eligible enemies:', eligibleEnemies.length);
      const gapState = createInitialGapState(gameTime);
      const geometryState = createInitialGeometryState(playerPos);

      newState = {
        ...newState,
        phase: 'forming',
        phaseStartTime: gameTime,
        phaseProgress: 0,
        center: geometryState.center,
        currentRadius: geometryState.currentRadius,
        gapAngle: gapState.angle,
        gapSize: gapState.size,
        targetPosition: geometryState.targetPosition,
        velocity: geometryState.velocity,
        gapRotationSpeed: gapState.rotationSpeed,
        gapRotationDirection: gapState.rotationDirection,
        lastDirectionChange: gapState.lastDirectionChange,
        lastSpeedChange: gapState.lastSpeedChange,
        lastLungeTime: gameTime,
        nextLungeInterval: BALL_LUNGE_CONFIG.intervalMin +
          Math.random() * (BALL_LUNGE_CONFIG.intervalMax - BALL_LUNGE_CONFIG.intervalMin),
        playerOutsideTime: 0,
        isDissipating: false,
        dissipationStartTime: 0,
        outsideBeePunchCooldowns: new Map(),
        formationBeeIds: eligibleEnemies.slice(0, BALL_PHASE_CONFIG.minBeesForBall).map(e => e.id),
        temperature: 0,
        playerEscaped: false,
      };

      events.push({
        type: 'ball_forming_started',
        timestamp: gameTime,
        position: playerPos,
      });
    }

    return { state: newState, events, damageToPlayer, knockback, knockbackSources };
  }

  // Active ball - delegate to core update
  return updateBallFormationCore(ballState, playerPos, enemies, gameTime, deltaTime, wave);
}

/**
 * Core ball update logic (used by both single and multi-ball APIs)
 */
function updateBallFormationCore(
  ballState: LegacyBallState,
  playerPos: Vector2,
  enemies: EnemyRef[],
  gameTime: number,
  deltaTime: number,
  _wave: number
): BallUpdateResult {
  const events: BallEvent[] = [];
  let damageToPlayer = 0;
  let knockback: BallUpdateResult['knockback'] = null;
  let newState = { ...ballState };

  // RUN 038: Collect all knockback sources, then combine into final position
  const knockbackSources: Array<{
    type: 'lunge' | 'boundary' | 'punch';
    direction: Vector2;
    force: number;
  }> = [];

  // ==========================================================================
  // Update Gap Rotation
  // ==========================================================================

  const gapState = updateGapRotation(
    {
      angle: newState.gapAngle,
      size: newState.gapSize,
      rotationSpeed: newState.gapRotationSpeed,
      rotationDirection: newState.gapRotationDirection,
      lastDirectionChange: newState.lastDirectionChange,
      lastSpeedChange: newState.lastSpeedChange,
    },
    gameTime,
    deltaTime
  );

  newState.gapAngle = gapState.angle;
  newState.gapRotationSpeed = gapState.rotationSpeed;
  newState.gapRotationDirection = gapState.rotationDirection;
  newState.lastDirectionChange = gapState.lastDirectionChange;
  newState.lastSpeedChange = gapState.lastSpeedChange;

  // ==========================================================================
  // Update Ball Movement
  // ==========================================================================

  const geometryState = updateBallMovement(
    {
      center: newState.center,
      currentRadius: newState.currentRadius,
      velocity: newState.velocity,
      targetPosition: newState.targetPosition,
    },
    playerPos,
    deltaTime
  );

  newState.center = geometryState.center;
  newState.velocity = geometryState.velocity;
  newState.targetPosition = geometryState.targetPosition;

  // ==========================================================================
  // Update Lunge Attacks (RUN 037: Slower, more readable)
  // ==========================================================================

  if (newState.activeLunge) {
    const lunge = newState.activeLunge;

    if (lunge.phase === 'windup') {
      const windupElapsed = gameTime - lunge.windupStartTime;

      if (windupElapsed >= BALL_LUNGE_CONFIG.windupDuration) {
        newState.activeLunge = {
          ...lunge,
          phase: 'lunge',
          lungeStartTime: gameTime,
        };

        events.push({
          type: 'lunge_attack_started',
          timestamp: gameTime,
          position: lunge.startPos,
          data: { lungingBeeId: lunge.beeId },
        });
      }
    } else if (lunge.phase === 'lunge') {
      const lungeElapsed = gameTime - lunge.lungeStartTime;

      if (lungeElapsed >= lunge.duration) {
        // Check if the bee actually hit the player
        // Bee ends up at targetPos, check distance to player's CURRENT position
        const hitDx = playerPos.x - lunge.targetPos.x;
        const hitDy = playerPos.y - lunge.targetPos.y;
        const hitDist = Math.sqrt(hitDx * hitDx + hitDy * hitDy);

        const didHit = hitDist <= BALL_LUNGE_CONFIG.hitRadius;

        if (didHit) {
          // HIT CONFIRMED - Apply knockback in the bee's travel direction
          const lungeDx = lunge.targetPos.x - lunge.startPos.x;
          const lungeDy = lunge.targetPos.y - lunge.startPos.y;
          const lungeDist = Math.sqrt(lungeDx * lungeDx + lungeDy * lungeDy);

          if (lungeDist > 1) {
            // Knockback direction = bee's travel direction (normalized)
            const knockbackDir: Vector2 = {
              x: lungeDx / lungeDist,
              y: lungeDy / lungeDist,
            };

            // RUN 038: Add to knockback sources instead of setting directly
            knockbackSources.push({
              type: 'lunge',
              direction: knockbackDir,
              force: BALL_LUNGE_CONFIG.knockbackForce,  // 80px - sharp push in travel direction
            });

            damageToPlayer += BALL_LUNGE_CONFIG.damage;

            events.push({
              type: 'lunge_hit',
              timestamp: gameTime,
              position: playerPos,
              data: {
                knockbackDirection: knockbackDir,
                knockbackForce: BALL_LUNGE_CONFIG.knockbackForce,
                lungingBeeId: lunge.beeId,
                damage: BALL_LUNGE_CONFIG.damage,
              },
            });
          }
        }
        // If missed, no knockback or damage - bee just returns to formation

        newState.activeLunge = {
          ...lunge,
          phase: 'return',
          lungeStartTime: gameTime,
        };

        events.push({
          type: 'lunge_return_started',
          timestamp: gameTime,
          position: playerPos,
          data: { lungingBeeId: lunge.beeId },
        });
      }
    } else if (lunge.phase === 'return') {
      const returnElapsed = gameTime - lunge.lungeStartTime;
      const returnDuration = BALL_LUNGE_CONFIG.returnDuration;

      if (returnElapsed >= returnDuration) {
        newState.activeLunge = null;
      }
    }
  }

  // Start new lunge if ready
  if (newState.phase !== 'inactive' && newState.formationBeeIds.length > 0 && !newState.activeLunge) {
    if (gameTime - newState.lastLungeTime >= newState.nextLungeInterval) {
      const lungingBeeId = newState.formationBeeIds[
        Math.floor(Math.random() * newState.formationBeeIds.length)
      ];

      const beeFormationPos = newState.formationPositions.get(lungingBeeId);
      if (beeFormationPos) {
        const toPlayerDx = playerPos.x - beeFormationPos.x;
        const toPlayerDy = playerPos.y - beeFormationPos.y;
        const toPlayerDist = Math.sqrt(toPlayerDx * toPlayerDx + toPlayerDy * toPlayerDy);

        if (toPlayerDist > 1) {
          const lungeTargetX = playerPos.x + (toPlayerDx / toPlayerDist) * BALL_LUNGE_CONFIG.overshoot;
          const lungeTargetY = playerPos.y + (toPlayerDy / toPlayerDist) * BALL_LUNGE_CONFIG.overshoot;

          newState.activeLunge = {
            beeId: lungingBeeId,
            phase: 'windup',
            windupStartTime: gameTime,
            lungeStartTime: 0,
            startPos: { ...beeFormationPos },
            targetPos: { x: lungeTargetX, y: lungeTargetY },
            duration: BALL_LUNGE_CONFIG.attackDuration,  // 400ms (was 150ms)
          };

          events.push({
            type: 'lunge_windup_started',
            timestamp: gameTime,
            position: beeFormationPos,
            data: { lungingBeeId },
          });
        }
      }

      newState.lastLungeTime = gameTime;
      newState.nextLungeInterval = BALL_LUNGE_CONFIG.intervalMin +
        Math.random() * (BALL_LUNGE_CONFIG.intervalMax - BALL_LUNGE_CONFIG.intervalMin);
    }
  }

  // ==========================================================================
  // Update Boundary Collision (RUN 037: Reduced knockback, RUN 038: Gap exception)
  // ==========================================================================

  if (newState.phase !== 'inactive' && !newState.isDissipating) {
    const boundaryResult = updateBoundaryCollision(
      playerPos,
      newState.center,
      newState.currentRadius,
      newState.gapAngle,      // RUN 038: Pass gap info for escape detection
      newState.gapSize,
      newState.isDissipating,
      newState.lastBoundaryDamageTick,
      gameTime
    );

    // RUN 038: Collect all knockback sources - they'll be combined into final position
    if (boundaryResult.knockback) {
      knockbackSources.push({
        type: 'boundary',
        direction: boundaryResult.knockback.direction,
        force: boundaryResult.knockback.force,
      });
    }

    damageToPlayer += boundaryResult.damageDealt;
    events.push(...boundaryResult.events);
    newState.lastBoundaryDamageTick = boundaryResult.newLastDamageTick;
  }

  // ==========================================================================
  // Update Outside Bee Punches (RUN 037: Reduced knockback)
  // ==========================================================================

  const punchResult = updateOutsidePunches(
    {
      beeIds: newState.formationBeeIds,
      positions: newState.formationPositions,
      outsidePunchCooldowns: newState.outsideBeePunchCooldowns,
    },
    enemies,
    playerPos,
    newState.center,
    gameTime
  );

  // RUN 038: Collect punch knockback source
  if (punchResult.knockback) {
    knockbackSources.push({
      type: 'punch',
      direction: punchResult.knockback.direction,
      force: punchResult.knockback.force,
    });
  }

  events.push(...punchResult.events);
  newState.outsideBeePunchCooldowns = punchResult.formation.outsidePunchCooldowns;

  // ==========================================================================
  // Combine all knockback sources into single final knockback
  // RUN 038: Multiple knockbacks (e.g., punch + boundary) combine into one slide
  // ==========================================================================

  if (knockbackSources.length > 0) {
    // Calculate combined knockback by applying each in sequence
    let combinedDx = 0;
    let combinedDy = 0;

    for (const source of knockbackSources) {
      combinedDx += source.direction.x * source.force;
      combinedDy += source.direction.y * source.force;
    }

    const combinedForce = Math.sqrt(combinedDx * combinedDx + combinedDy * combinedDy);

    if (combinedForce > 1) {
      knockback = {
        direction: {
          x: combinedDx / combinedForce,
          y: combinedDy / combinedForce,
        },
        force: combinedForce,
      };
    }
  }

  // ==========================================================================
  // Update Bee Recruitment
  // ==========================================================================

  const recruitmentResult = updateBeeRecruitment(
    {
      beeIds: newState.formationBeeIds,
      positions: newState.formationPositions,
      outsidePunchCooldowns: newState.outsideBeePunchCooldowns,
    },
    enemies,
    newState.center
  );

  newState.formationBeeIds = recruitmentResult.beeIds;

  // ==========================================================================
  // Update Dissipation Tracking
  // ==========================================================================

  const dissipationResult = updateDissipation(
    {
      playerOutsideTime: newState.playerOutsideTime,
      isDissipating: newState.isDissipating,
      dissipationStartTime: newState.dissipationStartTime,
      // Fade/linger fields (RUN 039)
      isFading: newState.isFading,
      fadeProgress: newState.fadeProgress,
      fadeStartTime: newState.fadeStartTime,
    },
    playerPos,
    newState.center,
    newState.currentRadius,
    gameTime,
    deltaTime
  );

  newState.playerOutsideTime = dissipationResult.state.playerOutsideTime;
  newState.isDissipating = dissipationResult.state.isDissipating;
  newState.dissipationStartTime = dissipationResult.state.dissipationStartTime;
  // Fade/linger fields (RUN 039)
  newState.isFading = dissipationResult.state.isFading;
  newState.fadeProgress = dissipationResult.state.fadeProgress;
  newState.fadeStartTime = dissipationResult.state.fadeStartTime;
  events.push(...dissipationResult.events);

  if (dissipationResult.shouldReset) {
    newState = {
      ...createBallState(newState.ballId, newState.ballTier),
      escapeCount: newState.escapeCount + 1,
    };
    return { state: newState, events, damageToPlayer, knockback, knockbackSources };
  }

  // Apply dissipation radius expansion
  if (newState.isDissipating) {
    newState.currentRadius = getDissipatingRadius(
      newState.currentRadius,
      dissipationResult.state,
      gameTime
    );
  }

  // ==========================================================================
  // Update Phase State Machine
  // ==========================================================================

  const phaseElapsed = gameTime - ballState.phaseStartTime;

  switch (ballState.phase) {
    case 'forming': {
      const progress = Math.min(1, phaseElapsed / BALL_CONFIG.formingDuration);
      newState.phaseProgress = progress;
      newState.currentRadius = interpolateFormingRadius(progress);
      newState.temperature = calculateTemperature('forming', progress, newState.temperature);

      if (progress >= 1) {
        newState.phase = 'silence';
        newState.phaseStartTime = gameTime;
        newState.phaseProgress = 0;

        events.push({
          type: 'ball_silence_started',
          timestamp: gameTime,
          position: newState.center,
        });
      }
      break;
    }

    case 'silence': {
      const progress = Math.min(1, phaseElapsed / BALL_CONFIG.silenceDuration);
      newState.phaseProgress = progress;
      newState.temperature = calculateTemperature('silence', progress, newState.temperature);

      if (progress >= 1) {
        newState.phase = 'constrict';
        newState.phaseStartTime = gameTime;
        newState.phaseProgress = 0;

        events.push({
          type: 'ball_constrict_started',
          timestamp: gameTime,
          position: newState.center,
          data: { escapeGapAngle: newState.gapAngle },
        });
      }
      break;
    }

    case 'constrict': {
      const progress = Math.min(1, phaseElapsed / BALL_CONFIG.constrictDuration);
      newState.phaseProgress = progress;

      if (!newState.isDissipating) {
        newState.currentRadius = interpolateConstrictRadius(progress);
      }

      newState.gapSize = interpolateGapSize(progress);
      newState.temperature = calculateTemperature('constrict', progress, newState.temperature);

      // Check for escape through gap
      if (isInEscapeGap(playerPos, newState.center, newState.currentRadius, newState.gapAngle, newState.gapSize)) {
        newState.playerEscaped = true;
        newState.escapeCount++;

        events.push({
          type: 'ball_escaped',
          timestamp: gameTime,
          position: playerPos,
        });

        newState = {
          ...createBallState(newState.ballId, newState.ballTier),
          escapeCount: newState.escapeCount,
        };
        break;
      }

      // Transition to cooking if player is still inside
      if (progress >= 1) {
        const dx = playerPos.x - newState.center.x;
        const dy = playerPos.y - newState.center.y;
        const distToCenter = Math.sqrt(dx * dx + dy * dy);

        if (distToCenter < newState.currentRadius * 0.9) {
          newState.phase = 'cooking';
          newState.phaseStartTime = gameTime;
          newState.phaseProgress = 0;

          events.push({
            type: 'ball_cooking_started',
            timestamp: gameTime,
            position: newState.center,
            data: { temperature: newState.temperature },
          });
        } else {
          newState.playerEscaped = true;
          newState.escapeCount++;

          events.push({
            type: 'ball_escaped',
            timestamp: gameTime,
            position: playerPos,
          });

          newState = {
            ...createBallState(newState.ballId, newState.ballTier),
            escapeCount: newState.escapeCount,
          };
        }
      }
      break;
    }

    case 'cooking': {
      newState.temperature = calculateTemperature('cooking', 0, newState.temperature);
      newState.center = { ...playerPos };
      newState.currentRadius = BALL_PHASE_CONFIG.finalRadius;

      if (gameTime - ballState.lastDamageTick >= BALL_COOKING_CONFIG.tickInterval) {
        damageToPlayer += BALL_COOKING_CONFIG.damagePerTick;
        newState.lastDamageTick = gameTime;

        events.push({
          type: 'ball_damage',
          timestamp: gameTime,
          position: playerPos,
          data: {
            damage: BALL_COOKING_CONFIG.damagePerTick,
            temperature: newState.temperature,
          },
        });
      }
      break;
    }
  }

  // ==========================================================================
  // Calculate Formation Positions for Rendering
  // ==========================================================================

  if (newState.phase !== 'inactive') {
    const posMap = calculateFormationPositions(
      newState.center,
      newState.currentRadius,
      newState.formationBeeIds.length,
      newState.gapAngle,
      newState.gapSize
    );

    newState.formationPositions = new Map(
      Array.from(posMap.entries()).map(([idx, pos]) => [
        newState.formationBeeIds[idx] ?? String(idx),
        pos,
      ])
    );
  }

  return { state: newState, events, damageToPlayer, knockback, knockbackSources };
}

// =============================================================================
// Legacy Exports (For Compatibility)
// =============================================================================

// These are exported from the old formation.ts and may be used elsewhere
export { renderBallFormation } from './render';
