/**
 * WASM Survivors - Colony Intelligence System
 *
 * The Superorganism Controller
 *
 * This is the central brain that coordinates:
 * - Pheromone grid (communication layer)
 * - Colony memory (pattern learning)
 * - Adaptive responses (behavioral modification)
 *
 * The Key Insight:
 * Individual bees are DUMB. The colony is SMART.
 * Intelligence emerges from simple rules + shared memory.
 *
 * By game end, players should feel:
 * > "They learned my patterns. They EARNED this kill."
 *
 * @see PROTO_SPEC.md Part XI Phase 4: Colony Intelligence
 */

import type { Vector2 } from '../types';
import {
  createPheromoneGrid,
  updatePheromoneGrid,
  depositAlarmAtAttack,
  depositPlayerTrail,
  depositDeathMark,
  depositCoordinationSignal,
  readPheromones,
  getBeeMovementModifier,
  shouldJoinFormation,
  shouldBeCautious,
  getAnticipatedPlayerPosition,
  type PheromoneGrid,
  type PheromoneReading,
} from './pheromone-grid';
import {
  createColonyMemory,
  recordDash,
  recordPosition,
  recordKill,
  recordUpgrade,
  recordBallEncounter,
  recordEscapeAttempt,
  getAdaptiveGapAngle,
  getCoordinationSpeedMultiplier,
  shouldAnticipate,
  getAnticipatedPosition,
  getDeathScreenLearnings,
  generateRunSummary,
  type ColonyMemory,
  type ColonyLearning,
} from './colony-memory';

// =============================================================================
// Types
// =============================================================================

/**
 * Complete colony intelligence state
 */
export interface ColonyIntelligence {
  pheromoneGrid: PheromoneGrid;
  memory: ColonyMemory;
  adaptationActive: boolean;
  lastTrailDeposit: number;
  lastPositionRecord: number;
}

/**
 * Per-bee intelligence data (cached reading + modifiers)
 */
export interface BeeIntelligence {
  reading: PheromoneReading;
  speedMultiplier: number;
  avoidanceVector: Vector2;
  coordinationPull: Vector2;
  shouldJoinBall: boolean;
  shouldBeCautious: boolean;
  anticipatedTarget: Vector2;
}

/**
 * Events that the colony intelligence system emits
 */
export interface ColonyEvent {
  type:
    | 'learning_acquired'
    | 'adaptation_increased'
    | 'gap_placement_adapted'
    | 'anticipation_activated';
  data?: {
    learning?: ColonyLearning;
    adaptationLevel?: number;
    gapAngle?: number;
  };
}

// =============================================================================
// Configuration
// =============================================================================

export const COLONY_CONFIG = {
  // Trail deposit frequency (ms between deposits)
  trailDepositInterval: 100, // 10 times per second

  // Position record frequency (ms between records)
  positionRecordInterval: 500, // 2 times per second

  // When to activate adaptation
  adaptationActivationThreshold: 3, // adaptation level

  // Anticipation lookahead (seconds)
  anticipationLookahead: 0.5,
} as const;

// =============================================================================
// Factory
// =============================================================================

/**
 * Create colony intelligence for a new run
 */
export function createColonyIntelligence(
  arenaWidth: number,
  arenaHeight: number,
  gameTime: number
): ColonyIntelligence {
  return {
    pheromoneGrid: createPheromoneGrid(arenaWidth, arenaHeight),
    memory: createColonyMemory(gameTime),
    adaptationActive: false,
    lastTrailDeposit: 0,
    lastPositionRecord: 0,
  };
}

// =============================================================================
// Main Update Loop
// =============================================================================

export interface ColonyUpdateResult {
  intelligence: ColonyIntelligence;
  events: ColonyEvent[];
}

/**
 * Update colony intelligence (call every frame)
 */
export function updateColonyIntelligence(
  intelligence: ColonyIntelligence,
  playerPosition: Vector2,
  playerVelocity: Vector2,
  arenaWidth: number,
  arenaHeight: number,
  gameTime: number,
  deltaTime: number
): ColonyUpdateResult {
  const events: ColonyEvent[] = [];
  let newIntelligence = { ...intelligence };

  // Update pheromone grid (decay + diffusion)
  newIntelligence.pheromoneGrid = updatePheromoneGrid(
    intelligence.pheromoneGrid,
    deltaTime,
    gameTime
  );

  // Deposit player trail periodically
  if (gameTime - intelligence.lastTrailDeposit > COLONY_CONFIG.trailDepositInterval) {
    newIntelligence.pheromoneGrid = depositPlayerTrail(
      newIntelligence.pheromoneGrid,
      playerPosition,
      playerVelocity,
      gameTime
    );
    newIntelligence.lastTrailDeposit = gameTime;
  }

  // Record player position periodically
  if (gameTime - intelligence.lastPositionRecord > COLONY_CONFIG.positionRecordInterval) {
    newIntelligence.memory = recordPosition(
      intelligence.memory,
      playerPosition,
      arenaWidth,
      arenaHeight
    );
    newIntelligence.lastPositionRecord = gameTime;
  }

  // Check if adaptation should activate
  if (!intelligence.adaptationActive &&
      intelligence.memory.adaptationLevel >= COLONY_CONFIG.adaptationActivationThreshold) {
    newIntelligence.adaptationActive = true;
    events.push({
      type: 'anticipation_activated',
      data: { adaptationLevel: intelligence.memory.adaptationLevel },
    });
  }

  return { intelligence: newIntelligence, events };
}

// =============================================================================
// Event Handlers (Call from game loop)
// =============================================================================

/**
 * Handle player attack event
 */
export function onPlayerAttack(
  intelligence: ColonyIntelligence,
  attackPosition: Vector2,
  gameTime: number
): ColonyIntelligence {
  return {
    ...intelligence,
    pheromoneGrid: depositAlarmAtAttack(
      intelligence.pheromoneGrid,
      attackPosition,
      gameTime
    ),
  };
}

/**
 * Handle player dash event
 */
export function onPlayerDash(
  intelligence: ColonyIntelligence,
  startPosition: Vector2,
  endPosition: Vector2,
  gameTime: number,
  wasEscape = false
): ColonyUpdateResult {
  const events: ColonyEvent[] = [];
  const prevConfidence = intelligence.memory.dashDirectionConfidence;

  const newMemory = recordDash(
    intelligence.memory,
    startPosition,
    endPosition,
    gameTime,
    wasEscape
  );

  // Check if we learned something new
  if (newMemory.dashDirectionConfidence > prevConfidence &&
      newMemory.dashDirectionConfidence > 0.5) {
    const learning = newMemory.learnings.find(l => l.type === 'movement');
    if (learning) {
      events.push({
        type: 'learning_acquired',
        data: { learning },
      });
    }
  }

  return {
    intelligence: { ...intelligence, memory: newMemory },
    events,
  };
}

/**
 * Handle enemy kill event
 */
export function onEnemyKill(
  intelligence: ColonyIntelligence,
  enemyPosition: Vector2,
  enemyId: string,
  gameTime: number
): ColonyIntelligence {
  return {
    ...intelligence,
    pheromoneGrid: depositDeathMark(
      intelligence.pheromoneGrid,
      enemyPosition,
      enemyId,
      gameTime
    ),
    memory: recordKill(intelligence.memory, gameTime),
  };
}

/**
 * Handle upgrade selection
 */
export function onUpgradeSelected(
  intelligence: ColonyIntelligence,
  upgrade: { id: string; name: string; description: string; tier: number; icon: string; effect: Record<string, unknown> }
): ColonyUpdateResult {
  const events: ColonyEvent[] = [];
  const prevArchetype = intelligence.memory.detectedArchetype;

  const newMemory = recordUpgrade(intelligence.memory, upgrade as any);

  // Check if archetype was detected
  if (newMemory.detectedArchetype !== prevArchetype &&
      newMemory.detectedArchetype !== 'unknown') {
    const learning = newMemory.learnings.find(l => l.type === 'build');
    if (learning) {
      events.push({
        type: 'learning_acquired',
        data: { learning },
      });
    }
  }

  return {
    intelligence: { ...intelligence, memory: newMemory },
    events,
  };
}

/**
 * Handle BALL formation start
 */
export function onBallFormationStart(
  intelligence: ColonyIntelligence,
  ballCenter: Vector2,
  coordinatorId: string,
  gapAngle: number,
  gameTime: number
): ColonyUpdateResult {
  const events: ColonyEvent[] = [];

  // Deposit coordination pheromone
  const newGrid = depositCoordinationSignal(
    intelligence.pheromoneGrid,
    ballCenter,
    coordinatorId,
    gameTime
  );

  // Record the encounter
  const newMemory = recordBallEncounter(
    intelligence.memory,
    ballCenter,
    gapAngle,
    gameTime
  );

  return {
    intelligence: {
      ...intelligence,
      pheromoneGrid: newGrid,
      memory: newMemory,
    },
    events,
  };
}

/**
 * Handle BALL escape attempt
 */
export function onBallEscapeAttempt(
  intelligence: ColonyIntelligence,
  ballCenter: Vector2,
  playerPosition: Vector2,
  gapAngle: number,
  success: boolean,
  gameTime: number
): ColonyUpdateResult {
  const events: ColonyEvent[] = [];

  const newMemory = recordEscapeAttempt(
    intelligence.memory,
    ballCenter,
    playerPosition,
    gapAngle,
    success,
    gameTime
  );

  // Check if we learned escape pattern
  if (newMemory.preferredEscapeDirection !== null &&
      intelligence.memory.preferredEscapeDirection === null) {
    const learning = newMemory.learnings.find(l => l.type === 'escape');
    if (learning) {
      events.push({
        type: 'learning_acquired',
        data: { learning },
      });
    }
  }

  return {
    intelligence: { ...intelligence, memory: newMemory },
    events,
  };
}

// =============================================================================
// Bee Intelligence Queries
// =============================================================================

/**
 * Get intelligence data for a single bee
 */
export function getBeeIntelligence(
  intelligence: ColonyIntelligence,
  beePosition: Vector2,
  playerPosition: Vector2,
  playerVelocity: Vector2
): BeeIntelligence {
  // Read pheromones at bee's position
  const reading = readPheromones(intelligence.pheromoneGrid, beePosition);

  // Get movement modifiers
  const modifiers = getBeeMovementModifier(reading);

  // Calculate anticipated target position
  let anticipatedTarget = playerPosition;
  if (intelligence.adaptationActive) {
    // Use both pheromone trails and memory
    const pheromoneTarget = getAnticipatedPlayerPosition(
      intelligence.pheromoneGrid,
      playerPosition,
      COLONY_CONFIG.anticipationLookahead
    );
    const memoryTarget = getAnticipatedPosition(
      intelligence.memory,
      playerPosition,
      playerVelocity,
      COLONY_CONFIG.anticipationLookahead
    );

    // Blend the two predictions
    anticipatedTarget = {
      x: (pheromoneTarget.x + memoryTarget.x) / 2,
      y: (pheromoneTarget.y + memoryTarget.y) / 2,
    };
  }

  return {
    reading,
    speedMultiplier: modifiers.speedMultiplier,
    avoidanceVector: modifiers.avoidanceVector,
    coordinationPull: modifiers.coordinationPull,
    shouldJoinBall: shouldJoinFormation(reading),
    shouldBeCautious: shouldBeCautious(reading),
    anticipatedTarget,
  };
}

/**
 * Get optimal gap angle for THE BALL (uses memory adaptation)
 */
export function getAdaptiveBallGapAngle(
  intelligence: ColonyIntelligence,
  defaultGapAngle: number
): { angle: number; isAdapted: boolean } {
  const adaptedAngle = getAdaptiveGapAngle(intelligence.memory, defaultGapAngle);
  const isAdapted = adaptedAngle !== defaultGapAngle;

  return { angle: adaptedAngle, isAdapted };
}

/**
 * Get coordination speed multiplier (faster if player is aggressive)
 */
export function getColonyCoordinationSpeed(
  intelligence: ColonyIntelligence
): number {
  return getCoordinationSpeedMultiplier(intelligence.memory);
}

/**
 * Check if colony should use predictive targeting
 */
export function shouldUsePredictiveTargeting(
  intelligence: ColonyIntelligence
): boolean {
  return shouldAnticipate(intelligence.memory);
}

// =============================================================================
// Death Screen Data
// =============================================================================

/**
 * Get data for the death screen
 */
export function getColonyDeathScreenData(
  intelligence: ColonyIntelligence
): {
  headline: string;
  learnings: ColonyLearning[];
  adaptationLevel: number;
  ballsEscaped: number;
  ballsEncountered: number;
  runSummary: string;
} {
  const deathData = getDeathScreenLearnings(intelligence.memory);
  const runSummary = generateRunSummary(intelligence.memory);

  return {
    ...deathData,
    runSummary,
  };
}

// =============================================================================
// Debug / Visualization
// =============================================================================

/**
 * Get debug info for visualization
 */
export function getColonyDebugInfo(
  intelligence: ColonyIntelligence
): {
  adaptationLevel: number;
  adaptationActive: boolean;
  preferredDashDirection: string | null;
  dashConfidence: number;
  detectedArchetype: string;
  archetypeConfidence: number;
  ballsEncountered: number;
  ballsEscaped: number;
  learningsCount: number;
} {
  const m = intelligence.memory;
  return {
    adaptationLevel: m.adaptationLevel,
    adaptationActive: intelligence.adaptationActive,
    preferredDashDirection: m.preferredDashDirection,
    dashConfidence: m.dashDirectionConfidence,
    detectedArchetype: m.detectedArchetype,
    archetypeConfidence: m.archetypeConfidence,
    ballsEncountered: m.ballsEncountered,
    ballsEscaped: m.ballsEscaped,
    learningsCount: m.learnings.length,
  };
}
