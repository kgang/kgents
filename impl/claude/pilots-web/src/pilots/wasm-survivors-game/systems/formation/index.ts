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
import { BALL_CONFIG, BALL_PHASE_CONFIG, BALL_GAP_CONFIG, BALL_COOKING_CONFIG, getGatheringDuration, BALL_LUNGE_CONFIG, getScaledLungeParams, getLungeScaling } from './config';
import { updateGapRotation, createInitialGapState, interpolateGapSize } from './gap';
import { updateBallMovement, calculateFormationPositions, isInEscapeGap, interpolateFormingRadius, interpolateConstrictRadius, createInitialGeometryState } from './geometry';
import { shouldStartBall, calculateTemperature } from './phase';
import { updateBoundaryCollision } from './boundary';
import { updateBeeRecruitment, updateOutsidePunches, cleanupFormation } from './recruitment';
import { updateDissipation, getDissipatingRadius } from './dissipation';

// Re-export types
export type { BallPhase, LegacyBallState as BallState, BallEvent, BallUpdateResult, BallTelegraphData, BallManagerState } from './types';

// Backwards compatibility: FormationEvent was the old name for BallEvent
export type { BallEvent as FormationEvent } from './types';

// Re-export config
export { BALL_CONFIG, BALL_PHASE_CONFIG, BALL_LUNGE_CONFIG, getLungeScaling, getScaledLungeParams, LUNGE_SCALING_BY_TYPE } from './config';
export type { LungeScalingConfig } from './config';

// Re-export query functions
export {
  isBallActive,
  isBallGathering,   // RUN 039: Pre-formation telegraph
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

// Re-export phase helpers (RUN 039: Dynamic cooldown)
export { getFormationCooldown } from './phase';

// =============================================================================
// Factory
// =============================================================================

/**
 * Create initial BALL state (inactive)
 */
export function createBallState(ballId: number = 0, tier: 1 | 2 = 1): LegacyBallState {
  const radiusMultiplier = tier === 2 ? BALL_PHASE_CONFIG.secondBallRadiusMultiplier : 1;
  // Tier 2 (secondary ball) has NO knockback - visual warning only
  const hasKnockback = tier === 1 ? true : BALL_PHASE_CONFIG.secondBallHasKnockback;
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
    lastNearMissTime: 0,  // RUN 039: Near-miss cooldown
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
    hasKnockback,  // Tier 2 balls have no boundary knockback
    // RUN 042: Ball promotion dynamics
    wasPromoted: false,
    promotionTime: 0,
    // RUN 039: Active outside punch telegraphs
    activePunches: [],
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
 * Promote a tier 2 ball to tier 1
 *
 * RUN 042: When the inner ball escapes/disperses, the outer ball "promotes"
 * to become the new primary threat:
 * - Gains knockback (boundary now pushes player)
 * - Constricts faster (1.8x speed)
 * - Visual changes from dotted yellow to solid colored
 * - If in gathering/forming phase, may skip ahead
 */
export function promoteBall(ball: LegacyBallState, gameTime: number): LegacyBallState {
  console.log(`[BALL] 🔄 PROMOTING tier 2 ball to tier 1! Phase: ${ball.phase}`);

  // Calculate new radius (shrink to tier 1 size)
  const newRadius = ball.currentRadius / BALL_PHASE_CONFIG.secondBallRadiusMultiplier;

  // If in gathering phase and config says skip, jump to forming
  let newPhase = ball.phase;
  let newPhaseStartTime = ball.phaseStartTime;
  if (ball.phase === 'gathering' && BALL_PHASE_CONFIG.promotionSkipGatheringPhase) {
    newPhase = 'forming';
    newPhaseStartTime = gameTime;
    console.log('[BALL] Promoted ball skipping gathering, jumping to forming');
  }

  return {
    ...ball,
    ballTier: 1,
    hasKnockback: true,  // Now has knockback!
    wasPromoted: true,
    promotionTime: gameTime,
    currentRadius: newRadius,
    phase: newPhase,
    phaseStartTime: newPhaseStartTime,
    phaseProgress: newPhase !== ball.phase ? 0 : ball.phaseProgress,
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
    lastNearMissTime: 0,  // RUN 039: Near-miss cooldown
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
    hasKnockback: currentState.hasKnockback,
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
 * RUN 040: Added enemySlowFactor to slow formation intervals with bullet time
 *
 * @param enemySlowFactor - Multiplier for enemy speed (1.0 = normal, 0.8 = 20% slower)
 *                          When < 1, formation phases take longer to progress
 */
export function updateBallManager(
  manager: BallManagerState,
  playerPos: Vector2,
  enemies: EnemyRef[],
  gameTime: number,
  deltaTime: number,
  wave: number,
  enemySlowFactor: number = 1.0  // Run 040: Bullet time slowdown
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
    const result = updateSingleBall(ball, playerPos, enemies, gameTime, deltaTime, wave, enemySlowFactor);
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
      console.log(`[BALL] Dispersed. ${ball.formationBeeIds.length} bees on cooldown for ${BALL_PHASE_CONFIG.beeCooldownAfterDisperse / 1000}s`);
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

  // ==========================================================================
  // RUN 042: Ball Promotion Logic
  // When tier 1 ball disperses but tier 2 is still active, promote tier 2
  // ==========================================================================
  const tier1Ball = updatedBalls.find(b => b.ballTier === 1);
  const tier2Ball = updatedBalls.find(b => b.ballTier === 2);

  if (!tier1Ball && tier2Ball) {
    // Tier 1 gone, tier 2 exists → PROMOTE!
    const promotedBall = promoteBall(tier2Ball, gameTime);

    // Replace tier 2 with promoted ball in the array
    const tier2Index = updatedBalls.indexOf(tier2Ball);
    if (tier2Index >= 0) {
      updatedBalls[tier2Index] = promotedBall;
    }

    // Emit promotion event
    allEvents.push({
      type: 'ball_forming_started',  // Re-use existing event for now
      timestamp: gameTime,
      position: promotedBall.center,
      data: { reason: 'promoted' as const } as any,
    });
  }

  // Try to start a new ball (tier 1) if none active
  const hasActiveBall = updatedBalls.some(b => b.phase !== 'inactive');

  // DEBUG: Log every frame to trace ball manager state
  if (wave >= 7) {
    console.log(`[BALL-DEBUG] wave=${wave}, updatedBalls.length=${updatedBalls.length}, hasActiveBall=${hasActiveBall}, eligibleEnemies=${eligibleEnemies.length}`);
  }

  if (!hasActiveBall) {
    if (shouldStartBall(eligibleEnemies.length, wave, 'inactive', lastBallEndTime, gameTime, false)) {
      const newBall = startNewBall(nextBallId++, 1, eligibleEnemies, playerPos, gameTime);
      updatedBalls.push(newBall.state);
      allEvents.push(newBall.event);
      console.log(`[BALL] FORMING tier 1! wave: ${wave}, eligible bees: ${eligibleEnemies.length}`);
    }
  } else if (updatedBalls.length < 2) {
    // Try to start second ball (tier 2) if first is active
    // Exclude bees in first ball from eligibility
    const firstBallBees = new Set(updatedBalls[0]?.formationBeeIds ?? []);
    const secondBallEligible = eligibleEnemies.filter(e => !firstBallBees.has(e.id));

    // Debug: Log why second ball might not spawn (every 2s to reduce spam)
    if (Math.floor(gameTime / 2000) !== Math.floor((gameTime - 16) / 2000)) {
      const minBees = BALL_PHASE_CONFIG.minBeesForBall + BALL_PHASE_CONFIG.secondBallMinBeesExtra;
      console.log(`[BALL] 🔍 Second ball check: wave=${wave} (need≥${BALL_PHASE_CONFIG.secondBallMinWave}), eligible=${secondBallEligible.length} (need≥${minBees}), firstBallPhase=${updatedBalls[0]?.phase}`);
    }

    if (shouldStartBall(secondBallEligible.length, wave, 'inactive', lastBallEndTime, gameTime, true)) {
      const newBall = startNewBall(nextBallId++, 2, secondBallEligible, playerPos, gameTime);
      updatedBalls.push(newBall.state);
      allEvents.push(newBall.event);
      console.log(`[BALL] SECOND BALL forming (tier 2)! Bees: ${secondBallEligible.length}`);
    }
  }

  // ==========================================================================
  // RUN 042: Dynamic radius enforcement
  // Outer ball is always notably bigger than inner ball (1.6x multiplier)
  // This ensures visual hierarchy as the inner ball constricts
  // ==========================================================================
  const updatedTier1 = updatedBalls.find(b => b.ballTier === 1);
  const updatedTier2 = updatedBalls.find(b => b.ballTier === 2);

  if (updatedTier1 && updatedTier2) {
    // Enforce minimum radius difference (outer = inner * multiplier)
    const minOuterRadius = updatedTier1.currentRadius * BALL_PHASE_CONFIG.secondBallRadiusMultiplier;
    if (updatedTier2.currentRadius < minOuterRadius) {
      updatedTier2.currentRadius = minOuterRadius;
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
  // Tier 2 (secondary ball) has NO knockback - visual warning only
  const hasKnockback = tier === 1 ? true : BALL_PHASE_CONFIG.secondBallHasKnockback;

  // RUN 039: Start with 'gathering' phase for pre-formation telegraph
  const state: LegacyBallState = {
    phase: 'gathering',  // Start with gathering, not forming
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
    lastNearMissTime: 0,  // RUN 039: Near-miss cooldown
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
    hasKnockback,  // Tier 2 balls have no boundary knockback
    // RUN 042: Ball promotion dynamics
    wasPromoted: false,
    promotionTime: 0,
    // RUN 039: Active outside punch telegraphs
    activePunches: [],
  };

  const event: BallEvent = {
    type: 'ball_gathering_started',  // New event type
    timestamp: gameTime,
    position: playerPos,
  };

  return { state, event };
}

/**
 * Update a single ball (internal - called by manager)
 * RUN 040: Added enemySlowFactor for bullet time
 */
function updateSingleBall(
  ballState: LegacyBallState,
  playerPos: Vector2,
  enemies: EnemyRef[],
  gameTime: number,
  deltaTime: number,
  wave: number,
  enemySlowFactor: number = 1.0
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
  // RUN 040: Pass enemySlowFactor to core update
  return updateBallFormationCore(ballState, playerPos, enemies, gameTime, deltaTime, wave, enemySlowFactor);
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
      // RUN 039: Start with 'gathering' phase - bees travel slowly to positions
      console.log('[BALL] GATHERING! wave:', wave, 'eligible enemies:', eligibleEnemies.length);
      const gapState = createInitialGapState(gameTime);
      const geometryState = createInitialGeometryState(playerPos);

      newState = {
        ...newState,
        phase: 'gathering',  // RUN 039: Start with gathering, not forming
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
        type: 'ball_gathering_started',  // RUN 039: New event type
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
 *
 * RUN 040: Added enemySlowFactor to slow formation intervals with bullet time.
 * When enemySlowFactor < 1.0, all timing-based operations slow down:
 * - Phase progress (gathering, forming, silence, constrict)
 * - Lunge windup, attack, and return timing
 * - Gap rotation speed
 * - Damage tick intervals
 */
function updateBallFormationCore(
  ballState: LegacyBallState,
  playerPos: Vector2,
  enemies: EnemyRef[],
  gameTime: number,
  deltaTime: number,
  wave: number,  // RUN 039: Used for wave-scaled gathering duration
  enemySlowFactor: number = 1.0  // RUN 040: Bullet time slowdown
): BallUpdateResult {
  const events: BallEvent[] = [];
  let damageToPlayer = 0;
  let knockback: BallUpdateResult['knockback'] = null;
  let newState = { ...ballState };

  // ==========================================================================
  // RUN 040: Apply bullet time slowdown to enemy-related timing
  // When enemies are slowed, their actions take proportionally longer
  // effectiveDeltaTime = deltaTime * enemySlowFactor (e.g., 16ms * 0.8 = 12.8ms)
  // ==========================================================================
  const effectiveDeltaTime = deltaTime * enemySlowFactor;

  // RUN 039: Wave-scaled gathering duration (3.5s at wave 3 → 2s at wave 7+)
  // RUN 040: Scale by 1/enemySlowFactor (slower enemies = longer durations)
  const baseGatheringDuration = getGatheringDuration(wave);
  const gatheringDuration = baseGatheringDuration / enemySlowFactor;

  // ==========================================================================
  // RUN 039: Clean up dead bees from formation FIRST
  // This ensures the dissolution check works when bees are killed
  // ==========================================================================

  const validEnemyIds = new Set(enemies.map(e => e.id));
  const cleanedFormation = cleanupFormation(
    {
      beeIds: newState.formationBeeIds,
      positions: newState.formationPositions,
      outsidePunchCooldowns: newState.outsideBeePunchCooldowns,
    },
    validEnemyIds
  );
  newState.formationBeeIds = cleanedFormation.beeIds;

  // RUN 038: Collect all knockback sources, then combine into final position
  const knockbackSources: Array<{
    type: 'lunge' | 'boundary' | 'punch';
    direction: Vector2;
    force: number;
  }> = [];

  // ==========================================================================
  // Update Gap Rotation
  // RUN 040: Use effectiveDeltaTime for slowed gap rotation with bullet time
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
    effectiveDeltaTime  // RUN 040: Slowed gap rotation
  );

  newState.gapAngle = gapState.angle;
  newState.gapRotationSpeed = gapState.rotationSpeed;
  newState.gapRotationDirection = gapState.rotationDirection;
  newState.lastDirectionChange = gapState.lastDirectionChange;
  newState.lastSpeedChange = gapState.lastSpeedChange;

  // ==========================================================================
  // Update Ball Movement
  // RUN 040: Use effectiveDeltaTime for slowed movement with bullet time
  // ==========================================================================

  const geometryState = updateBallMovement(
    {
      center: newState.center,
      currentRadius: newState.currentRadius,
      velocity: newState.velocity,
      targetPosition: newState.targetPosition,
    },
    playerPos,
    effectiveDeltaTime  // RUN 040: Slowed ball tracking
  );

  newState.center = geometryState.center;
  newState.velocity = geometryState.velocity;
  newState.targetPosition = geometryState.targetPosition;

  // ==========================================================================
  // Update Lunge Attacks (RUN 037: Slower, more readable)
  // RUN 040: Lunge timing scaled by enemySlowFactor (bullet time)
  // RUN 042: Lunge parameters scaled by enemy type (hit radius, damage, windup speed)
  // ==========================================================================

  // RUN 042: Helper to get enemy type from ID
  const getEnemyType = (beeId: string): string => {
    const enemy = enemies.find(e => e.id === beeId);
    return enemy?.type ?? 'worker';
  };

  // RUN 040: Scale lunge durations by 1/enemySlowFactor (slower enemies = longer lunges)
  // RUN 042: Also scale by enemy type (elite bees have faster windup)
  const getEffectiveWindupDuration = (beeType: string): number => {
    const scaling = getLungeScaling(beeType);
    const baseWindup = BALL_LUNGE_CONFIG.windupDuration / scaling.windupSpeedMultiplier;
    return baseWindup / enemySlowFactor;
  };
  const effectiveLungeDuration = BALL_LUNGE_CONFIG.attackDuration / enemySlowFactor;
  const effectiveReturnDuration = BALL_LUNGE_CONFIG.returnDuration / enemySlowFactor;

  if (newState.activeLunge) {
    const lunge = newState.activeLunge;

    if (lunge.phase === 'windup') {
      const windupElapsed = gameTime - lunge.windupStartTime;

      // RUN 042: Use scaled windup duration based on bee type
      const effectiveWindupDuration = lunge.scaledWindupDuration > 0
        ? lunge.scaledWindupDuration / enemySlowFactor
        : getEffectiveWindupDuration(lunge.beeType ?? 'worker');

      if (windupElapsed >= effectiveWindupDuration) {
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

      if (lungeElapsed >= effectiveLungeDuration) {
        // Check if the bee actually hit the player
        // Bee ends up at targetPos, check distance to player's CURRENT position
        const hitDx = playerPos.x - lunge.targetPos.x;
        const hitDy = playerPos.y - lunge.targetPos.y;
        const hitDist = Math.sqrt(hitDx * hitDx + hitDy * hitDy);

        // RUN 042: Use scaled hit radius (larger for elite bees)
        const effectiveHitRadius = lunge.scaledHitRadius > 0
          ? lunge.scaledHitRadius
          : BALL_LUNGE_CONFIG.hitRadius;

        const didHit = hitDist <= effectiveHitRadius;

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

            // RUN 042: Use scaled damage (higher for elite bees)
            const effectiveDamage = lunge.scaledDamage > 0
              ? lunge.scaledDamage
              : BALL_LUNGE_CONFIG.damage;

            damageToPlayer += effectiveDamage;

            events.push({
              type: 'lunge_hit',
              timestamp: gameTime,
              position: playerPos,
              data: {
                knockbackDirection: knockbackDir,
                knockbackForce: BALL_LUNGE_CONFIG.knockbackForce,
                lungingBeeId: lunge.beeId,
                damage: effectiveDamage,
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

      // RUN 040: Use effective return duration
      if (returnElapsed >= effectiveReturnDuration) {
        const completedBeeId = lunge.beeId;
        newState.activeLunge = null;

        // =======================================================================
        // RUN 039: Chain Lunge Mechanic
        // RUN 042: Chain lunges also use scaled parameters
        // =======================================================================
        // When a lunge completes, there's a 10% chance another bee will immediately lunge.
        // This creates exciting "flurry" moments that test player reflexes.

        if (Math.random() < BALL_LUNGE_CONFIG.chainLungeChance) {
          // Find a different bee to chain lunge
          const eligibleBees = newState.formationBeeIds.filter(id => id !== completedBeeId);
          if (eligibleBees.length > 0) {
            const chainBeeId = eligibleBees[Math.floor(Math.random() * eligibleBees.length)];
            const chainBeePos = newState.formationPositions.get(chainBeeId);

            if (chainBeePos) {
              // RUN 042: Get enemy type and compute scaled parameters for chain lunge
              const chainBeeType = getEnemyType(chainBeeId);
              const chainScaledParams = getScaledLungeParams(chainBeeType);

              const toPlayerDx = playerPos.x - chainBeePos.x;
              const toPlayerDy = playerPos.y - chainBeePos.y;
              const toPlayerDist = Math.sqrt(toPlayerDx * toPlayerDx + toPlayerDy * toPlayerDy);

              if (toPlayerDist > 1) {
                // RUN 039: Chain lunge also uses 120% distance
                const totalDistance = toPlayerDist * (1 + BALL_LUNGE_CONFIG.overshootPercent);
                const dirX = toPlayerDx / toPlayerDist;
                const dirY = toPlayerDy / toPlayerDist;
                const chainTargetX = chainBeePos.x + dirX * totalDistance;
                const chainTargetY = chainBeePos.y + dirY * totalDistance;

                // Start chain lunge after brief delay (use windup start offset)
                // RUN 042: Include scaled parameters
                newState.activeLunge = {
                  beeId: chainBeeId,
                  beeType: chainBeeType,
                  phase: 'windup',
                  windupStartTime: gameTime + BALL_LUNGE_CONFIG.chainLungeDelay,
                  lungeStartTime: 0,
                  startPos: { ...chainBeePos },
                  targetPos: { x: chainTargetX, y: chainTargetY },
                  duration: BALL_LUNGE_CONFIG.attackDuration,
                  scaledHitRadius: chainScaledParams.hitRadius,
                  scaledDamage: chainScaledParams.damage,
                  scaledWindupDuration: chainScaledParams.windupDuration,
                };

                events.push({
                  type: 'lunge_windup_started',
                  timestamp: gameTime,
                  position: chainBeePos,
                  data: { lungingBeeId: chainBeeId },
                });

                // Update last lunge time to prevent immediate regular lunge
                newState.lastLungeTime = gameTime;
              }
            }
          }
        }
      }
    }
  }

  // Start new lunge if ready
  // RUN 040: Scale lunge interval by 1/enemySlowFactor (slower enemies = longer between lunges)
  const effectiveLungeInterval = newState.nextLungeInterval / enemySlowFactor;
  if (newState.phase !== 'inactive' && newState.formationBeeIds.length > 0 && !newState.activeLunge) {
    if (gameTime - newState.lastLungeTime >= effectiveLungeInterval) {
      const lungingBeeId = newState.formationBeeIds[
        Math.floor(Math.random() * newState.formationBeeIds.length)
      ];

      const beeFormationPos = newState.formationPositions.get(lungingBeeId);
      if (beeFormationPos) {
        // RUN 042: Get enemy type and compute scaled parameters
        const beeType = getEnemyType(lungingBeeId);
        const scaledParams = getScaledLungeParams(beeType);

        const toPlayerDx = playerPos.x - beeFormationPos.x;
        const toPlayerDy = playerPos.y - beeFormationPos.y;
        const toPlayerDist = Math.sqrt(toPlayerDx * toPlayerDx + toPlayerDy * toPlayerDy);

        if (toPlayerDist > 1) {
          // RUN 039: Lunge goes 120% of distance (20% overshoot)
          // This means the bee will pass through the player position
          const totalDistance = toPlayerDist * (1 + BALL_LUNGE_CONFIG.overshootPercent);
          const dirX = toPlayerDx / toPlayerDist;
          const dirY = toPlayerDy / toPlayerDist;
          const lungeTargetX = beeFormationPos.x + dirX * totalDistance;
          const lungeTargetY = beeFormationPos.y + dirY * totalDistance;

          // RUN 042: Include bee type and scaled parameters
          newState.activeLunge = {
            beeId: lungingBeeId,
            beeType: beeType,
            phase: 'windup',
            windupStartTime: gameTime,
            lungeStartTime: 0,
            startPos: { ...beeFormationPos },
            targetPos: { x: lungeTargetX, y: lungeTargetY },
            duration: BALL_LUNGE_CONFIG.attackDuration,  // 400ms
            scaledHitRadius: scaledParams.hitRadius,
            scaledDamage: scaledParams.damage,
            scaledWindupDuration: scaledParams.windupDuration,
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
  // RUN 042: Tier 2 balls have no knockback (visual warning only)
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
      gameTime,
      newState.hasKnockback,  // RUN 042: Tier 2 balls have no knockback
      newState.lastNearMissTime  // RUN 039: Track near-miss cooldown
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
    newState.lastNearMissTime = boundaryResult.newLastNearMissTime;  // RUN 039
  }

  // ==========================================================================
  // Update Outside Bee Punches (RUN 039: Telegraph system with dodge window)
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
    gameTime,
    newState.activePunches  // RUN 039: Pass active punch states
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
  newState.activePunches = punchResult.updatedPunches;  // RUN 039: Save updated punch states

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
  // RUN 039: Check if ball should dissolve due to too few bees remaining
  // (Player killed bees from inside the ball)
  // ==========================================================================

  if (newState.formationBeeIds.length < BALL_PHASE_CONFIG.minBeesToMaintain) {
    console.log(`[BALL] Dissolved! Only ${newState.formationBeeIds.length} bees remain (need ${BALL_PHASE_CONFIG.minBeesToMaintain})`);

    events.push({
      type: 'ball_dispersed',
      timestamp: gameTime,
      position: newState.center,
      data: { reason: 'too_few_bees', remainingBees: newState.formationBeeIds.length },
    });

    newState = {
      ...createBallState(newState.ballId, newState.ballTier),
      escapeCount: newState.escapeCount,
    };
    return { state: newState, events, damageToPlayer, knockback, knockbackSources };
  }

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
  // RUN 040: All phase durations scaled by 1/enemySlowFactor (bullet time)
  // ==========================================================================

  const phaseElapsed = gameTime - ballState.phaseStartTime;

  // RUN 042: Promoted balls constrict faster
  const promotionSpeedMultiplier = ballState.wasPromoted
    ? BALL_PHASE_CONFIG.promotionConstrictSpeedMultiplier
    : 1.0;

  // RUN 040: Scale phase durations by 1/enemySlowFactor (slower enemies = longer phases)
  // RUN 042: Also scale by promotionSpeedMultiplier (promoted balls are faster)
  const effectiveFormingDuration = BALL_CONFIG.formingDuration / enemySlowFactor / promotionSpeedMultiplier;
  const effectiveSilenceDuration = BALL_CONFIG.silenceDuration / enemySlowFactor / promotionSpeedMultiplier;
  const effectiveConstrictDuration = BALL_CONFIG.constrictDuration / enemySlowFactor / promotionSpeedMultiplier;
  const effectiveCookingInterval = BALL_COOKING_CONFIG.tickInterval / enemySlowFactor;

  switch (ballState.phase) {
    // ========================================================================
    // RUN 039: Gathering Phase - Pre-formation telegraph
    // Bees travel slowly to their positions, indicator shows ball location
    // Duration scales with wave: 3.5s at wave 3 → 2s at wave 7+
    // RUN 040: Also scaled by enemySlowFactor (already applied to gatheringDuration)
    // ========================================================================
    case 'gathering': {
      const progress = Math.min(1, phaseElapsed / gatheringDuration);
      newState.phaseProgress = progress;

      // Ball center slowly tracks player during gathering (scaled by slow)
      const trackingRate = 0.02 * enemySlowFactor;
      newState.center = {
        x: newState.center.x + (playerPos.x - newState.center.x) * trackingRate,
        y: newState.center.y + (playerPos.y - newState.center.y) * trackingRate,
      };

      // No temperature during gathering (just visual)
      newState.temperature = 0;

      // Transition to forming when gathering complete
      if (progress >= 1) {
        newState.phase = 'forming';
        newState.phaseStartTime = gameTime;
        newState.phaseProgress = 0;

        console.log('[BALL] FORMING! Bees have arrived at positions');

        events.push({
          type: 'ball_forming_started',
          timestamp: gameTime,
          position: newState.center,
        });
      }
      break;
    }

    case 'forming': {
      const progress = Math.min(1, phaseElapsed / effectiveFormingDuration);
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
      const progress = Math.min(1, phaseElapsed / effectiveSilenceDuration);
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
      // RUN 040: Use effective constrict duration for bullet time
      const progress = Math.min(1, phaseElapsed / effectiveConstrictDuration);
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

      // RUN 040: Use effective cooking interval for bullet time (slower damage ticks)
      if (gameTime - ballState.lastDamageTick >= effectiveCookingInterval) {
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
    // RUN 039: Pass gameTime for organic bee oscillation
    const posMap = calculateFormationPositions(
      newState.center,
      newState.currentRadius,
      newState.formationBeeIds.length,
      newState.gapAngle,
      newState.gapSize,
      gameTime  // For oscillation timing
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
export { renderBallFormation, renderOutsidePunchIndicators, getPunchingBeeIds, getBeeWindupProgress } from './render';

// Re-export OutsidePunchState type for rendering
export type { OutsidePunchState } from './types';
