/**
 * WASM Survivors - Colony Memory System
 *
 * Colony Intelligence Layer 2: Pattern Learning
 *
 * This system tracks player behaviors WITHIN a single run and adapts
 * the colony's response. The goal: by late game, bees feel like they
 * LEARNED your patterns and EARNED the kill.
 *
 * What the colony tracks:
 * - Movement patterns (dash direction preferences)
 * - Timing patterns (when do you dash? How long do you kite?)
 * - Build detection (aggressive vs defensive player?)
 * - Escape patterns (which way do you run from THE BALL?)
 *
 * V5: WITNESSED (Not Surveilled)
 * The death screen shows "what the colony learned" in a way that
 * feels like collaboration, not judgment.
 *
 * @see PROTO_SPEC.md Part XI Phase 4: Colony Intelligence
 * @see PROTO_SPEC.md V5: WITNESSED
 */

import type { Vector2, Upgrade } from '../types';

// =============================================================================
// Types
// =============================================================================

/**
 * Direction categories for pattern tracking
 */
export type CardinalDirection = 'north' | 'south' | 'east' | 'west';
export type DiagonalDirection = 'northeast' | 'northwest' | 'southeast' | 'southwest';
export type Direction = CardinalDirection | DiagonalDirection;

/**
 * Player archetype based on behavior
 */
export type PlayerArchetype =
  | 'aggressor'    // Moves toward enemies, high kill rate
  | 'kiter'        // Maintains distance, circular movement
  | 'dasher'       // Uses dash frequently, burst movement
  | 'holder'       // Stays in one area, lets enemies come
  | 'unknown';     // Not enough data yet

/**
 * A recorded dash event for pattern analysis
 */
export interface DashEvent {
  timestamp: number;
  startPosition: Vector2;
  endPosition: Vector2;
  direction: Direction;
  angle: number; // radians
  wasEscape: boolean; // True if escaping THE BALL
}

/**
 * A recorded escape attempt from THE BALL
 */
export interface EscapeAttempt {
  timestamp: number;
  ballCenter: Vector2;
  escapeDirection: number; // radians
  success: boolean;
  gapAngle: number; // Where the gap was
}

/**
 * Rolling statistics for pattern detection
 */
export interface PatternStats {
  samples: number[];
  count: number;
  mean: number;
  stdDev: number;
}

/**
 * The colony's accumulated knowledge about this player
 */
export interface ColonyMemory {
  // Run metadata
  runStartTime: number;
  lastUpdateTime: number;

  // Movement patterns
  dashHistory: DashEvent[];
  preferredDashDirection: Direction | null;
  dashDirectionConfidence: number; // 0-1

  // Timing patterns
  dashFrequency: PatternStats; // Time between dashes (ms)
  averageKitingRadius: number;
  movementSpeedTendency: 'fast' | 'normal' | 'slow';

  // Position tendencies
  preferredZone: 'center' | 'edge' | 'corner' | 'random';
  heatmapData: number[][]; // Position frequency grid

  // Combat patterns
  killsPerMinute: PatternStats;
  aggressionLevel: number; // 0-1 (0=defensive, 1=aggressive)
  upgradeChoices: string[]; // Track chosen upgrades

  // Build detection
  detectedArchetype: PlayerArchetype;
  archetypeConfidence: number; // 0-1

  // Escape patterns (THE BALL specific)
  escapeHistory: EscapeAttempt[];
  preferredEscapeDirection: number | null; // radians
  escapeSuccessRate: number; // 0-1
  ballsEncountered: number;
  ballsEscaped: number;

  // Colony adaptation state
  adaptationLevel: number; // 0-10 (how much has colony learned)
  learnings: ColonyLearning[]; // Human-readable learnings for death screen
}

/**
 * A single learning for the death screen
 */
export interface ColonyLearning {
  type: 'movement' | 'timing' | 'build' | 'escape';
  description: string; // e.g., "Prefers eastward dashes"
  confidence: number; // 0-1
  usedAgainst: boolean; // Did colony use this against player?
}

// =============================================================================
// Configuration
// =============================================================================

export const MEMORY_CONFIG = {
  // Pattern detection thresholds
  minSamplesForPattern: 5,
  highConfidenceThreshold: 0.7,
  mediumConfidenceThreshold: 0.4,

  // Rolling window sizes
  dashHistorySize: 20,
  escapeHistorySize: 10,

  // Heatmap grid
  heatmapCells: 10, // 10x10 grid

  // Archetype detection
  aggressorKillRate: 30, // 30+ kills per minute = aggressor
  kiterAvgDistance: 150, // Average distance > 150px = kiter
  dasherFrequency: 2000, // Dash every 2s or less = dasher

  // Adaptation pacing
  adaptationPerEvent: 0.1, // +0.1 adaptation per learned event
  maxAdaptation: 10,
} as const;

// =============================================================================
// Factory
// =============================================================================

/**
 * Create fresh colony memory for a new run
 */
export function createColonyMemory(gameTime: number): ColonyMemory {
  return {
    runStartTime: gameTime,
    lastUpdateTime: gameTime,

    dashHistory: [],
    preferredDashDirection: null,
    dashDirectionConfidence: 0,

    dashFrequency: createEmptyStats(),
    averageKitingRadius: 0,
    movementSpeedTendency: 'normal',

    preferredZone: 'random',
    heatmapData: createHeatmap(),

    killsPerMinute: createEmptyStats(),
    aggressionLevel: 0.5,
    upgradeChoices: [],

    detectedArchetype: 'unknown',
    archetypeConfidence: 0,

    escapeHistory: [],
    preferredEscapeDirection: null,
    escapeSuccessRate: 0,
    ballsEncountered: 0,
    ballsEscaped: 0,

    adaptationLevel: 0,
    learnings: [],
  };
}

function createEmptyStats(): PatternStats {
  return { samples: [], count: 0, mean: 0, stdDev: 0 };
}

function createHeatmap(): number[][] {
  const grid: number[][] = [];
  for (let y = 0; y < MEMORY_CONFIG.heatmapCells; y++) {
    grid[y] = [];
    for (let x = 0; x < MEMORY_CONFIG.heatmapCells; x++) {
      grid[y][x] = 0;
    }
  }
  return grid;
}

// =============================================================================
// Event Recording
// =============================================================================

/**
 * Record a dash event
 */
export function recordDash(
  memory: ColonyMemory,
  startPos: Vector2,
  endPos: Vector2,
  gameTime: number,
  wasEscape = false
): ColonyMemory {
  const dx = endPos.x - startPos.x;
  const dy = endPos.y - startPos.y;
  const angle = Math.atan2(dy, dx);
  const direction = angleToDirection(angle);

  const event: DashEvent = {
    timestamp: gameTime,
    startPosition: { ...startPos },
    endPosition: { ...endPos },
    direction,
    angle,
    wasEscape,
  };

  // Add to history (rolling window)
  const newHistory = [...memory.dashHistory, event];
  if (newHistory.length > MEMORY_CONFIG.dashHistorySize) {
    newHistory.shift();
  }

  // Update dash frequency
  let newDashFrequency = memory.dashFrequency;
  if (memory.dashHistory.length > 0) {
    const lastDash = memory.dashHistory[memory.dashHistory.length - 1];
    const interval = gameTime - lastDash.timestamp;
    newDashFrequency = addSample(memory.dashFrequency, interval);
  }

  // Analyze direction patterns
  const { preferredDirection, confidence } = analyzeDirectionPatterns(newHistory);

  // Check for new learning
  const learnings = [...memory.learnings];
  if (confidence > MEMORY_CONFIG.highConfidenceThreshold &&
      !learnings.some(l => l.type === 'movement' && l.description.includes(preferredDirection ?? ''))) {
    learnings.push({
      type: 'movement',
      description: `Prefers ${directionToHuman(preferredDirection)} dashes`,
      confidence,
      usedAgainst: false,
    });
  }

  const adaptationLevel = Math.min(
    MEMORY_CONFIG.maxAdaptation,
    memory.adaptationLevel + (confidence > 0.5 ? MEMORY_CONFIG.adaptationPerEvent : 0)
  );

  return {
    ...memory,
    dashHistory: newHistory,
    dashFrequency: newDashFrequency,
    preferredDashDirection: preferredDirection,
    dashDirectionConfidence: confidence,
    adaptationLevel,
    learnings,
    lastUpdateTime: gameTime,
  };
}

/**
 * Record player position for heatmap
 */
export function recordPosition(
  memory: ColonyMemory,
  position: Vector2,
  arenaWidth: number,
  arenaHeight: number
): ColonyMemory {
  const cellX = Math.floor((position.x / arenaWidth) * MEMORY_CONFIG.heatmapCells);
  const cellY = Math.floor((position.y / arenaHeight) * MEMORY_CONFIG.heatmapCells);

  const x = Math.max(0, Math.min(MEMORY_CONFIG.heatmapCells - 1, cellX));
  const y = Math.max(0, Math.min(MEMORY_CONFIG.heatmapCells - 1, cellY));

  const newHeatmap = memory.heatmapData.map(row => [...row]);
  newHeatmap[y][x] += 1;

  // Analyze preferred zone
  const zone = analyzeZonePreference(newHeatmap);

  return {
    ...memory,
    heatmapData: newHeatmap,
    preferredZone: zone,
  };
}

/**
 * Record a kill
 */
export function recordKill(
  memory: ColonyMemory,
  gameTime: number
): ColonyMemory {
  const runDuration = (gameTime - memory.runStartTime) / 60000; // minutes
  const totalKills = memory.killsPerMinute.count + 1;
  const kpm = totalKills / Math.max(0.1, runDuration);

  const newKillsPerMinute = addSample(memory.killsPerMinute, kpm);

  // Update aggression level
  const aggressionLevel = Math.min(1, kpm / MEMORY_CONFIG.aggressorKillRate);

  return {
    ...memory,
    killsPerMinute: newKillsPerMinute,
    aggressionLevel,
    lastUpdateTime: gameTime,
  };
}

/**
 * Record an upgrade choice
 */
export function recordUpgrade(
  memory: ColonyMemory,
  upgrade: Upgrade
): ColonyMemory {
  const newChoices = [...memory.upgradeChoices, upgrade.id];

  // Update archetype detection based on upgrade patterns
  const archetype = detectArchetype(memory, newChoices);

  // Check for new learning
  const learnings = [...memory.learnings];
  if (archetype.confidence > MEMORY_CONFIG.mediumConfidenceThreshold &&
      !learnings.some(l => l.type === 'build' && l.description.includes(archetype.type))) {
    learnings.push({
      type: 'build',
      description: `Playing as ${archetypeToHuman(archetype.type)}`,
      confidence: archetype.confidence,
      usedAgainst: false,
    });
  }

  return {
    ...memory,
    upgradeChoices: newChoices,
    detectedArchetype: archetype.type,
    archetypeConfidence: archetype.confidence,
    learnings,
  };
}

/**
 * Record a BALL encounter
 */
export function recordBallEncounter(
  memory: ColonyMemory,
  _ballCenter: Vector2,
  _gapAngle: number,
  gameTime: number
): ColonyMemory {
  return {
    ...memory,
    ballsEncountered: memory.ballsEncountered + 1,
    lastUpdateTime: gameTime,
  };
}

/**
 * Record an escape attempt from THE BALL
 */
export function recordEscapeAttempt(
  memory: ColonyMemory,
  ballCenter: Vector2,
  playerPosition: Vector2,
  gapAngle: number,
  success: boolean,
  gameTime: number
): ColonyMemory {
  const dx = playerPosition.x - ballCenter.x;
  const dy = playerPosition.y - ballCenter.y;
  const escapeDirection = Math.atan2(dy, dx);

  const attempt: EscapeAttempt = {
    timestamp: gameTime,
    ballCenter: { ...ballCenter },
    escapeDirection,
    success,
    gapAngle,
  };

  // Add to history
  const newHistory = [...memory.escapeHistory, attempt];
  if (newHistory.length > MEMORY_CONFIG.escapeHistorySize) {
    newHistory.shift();
  }

  // Analyze escape patterns
  const preferredEscape = analyzeEscapePatterns(newHistory);
  const successfulEscapes = newHistory.filter(e => e.success).length;
  const successRate = successfulEscapes / Math.max(1, newHistory.length);

  const ballsEscaped = success ? memory.ballsEscaped + 1 : memory.ballsEscaped;

  // Check for new learning
  const learnings = [...memory.learnings];
  if (preferredEscape !== null && newHistory.length >= 3 &&
      !learnings.some(l => l.type === 'escape')) {
    const escapeDir = directionToHuman(angleToDirection(preferredEscape));
    learnings.push({
      type: 'escape',
      description: `Escapes toward the ${escapeDir}`,
      confidence: 0.7,
      usedAgainst: false,
    });
  }

  const adaptationLevel = Math.min(
    MEMORY_CONFIG.maxAdaptation,
    memory.adaptationLevel + MEMORY_CONFIG.adaptationPerEvent * 2 // Ball encounters are high-value learning
  );

  return {
    ...memory,
    escapeHistory: newHistory,
    preferredEscapeDirection: preferredEscape,
    escapeSuccessRate: successRate,
    ballsEscaped,
    adaptationLevel,
    learnings,
    lastUpdateTime: gameTime,
  };
}

// =============================================================================
// Pattern Analysis
// =============================================================================

function angleToDirection(angle: number): Direction {
  // Normalize to 0-2PI
  const normalized = ((angle % (Math.PI * 2)) + Math.PI * 2) % (Math.PI * 2);
  const degrees = (normalized * 180) / Math.PI;

  if (degrees < 22.5 || degrees >= 337.5) return 'east';
  if (degrees < 67.5) return 'northeast';
  if (degrees < 112.5) return 'north';
  if (degrees < 157.5) return 'northwest';
  if (degrees < 202.5) return 'west';
  if (degrees < 247.5) return 'southwest';
  if (degrees < 292.5) return 'south';
  return 'southeast';
}

function directionToHuman(dir: Direction | null): string {
  if (!dir) return 'unknown';
  const map: Record<Direction, string> = {
    north: 'north',
    south: 'south',
    east: 'east',
    west: 'west',
    northeast: 'northeast',
    northwest: 'northwest',
    southeast: 'southeast',
    southwest: 'southwest',
  };
  return map[dir];
}

function archetypeToHuman(archetype: PlayerArchetype): string {
  const map: Record<PlayerArchetype, string> = {
    aggressor: 'an aggressor',
    kiter: 'a kiter',
    dasher: 'a dasher',
    holder: 'a holder',
    unknown: 'unknown style',
  };
  return map[archetype];
}

function analyzeDirectionPatterns(
  history: DashEvent[]
): { preferredDirection: Direction | null; confidence: number } {
  if (history.length < MEMORY_CONFIG.minSamplesForPattern) {
    return { preferredDirection: null, confidence: 0 };
  }

  // Count direction frequencies
  const counts: Record<Direction, number> = {
    north: 0, south: 0, east: 0, west: 0,
    northeast: 0, northwest: 0, southeast: 0, southwest: 0,
  };

  for (const event of history) {
    counts[event.direction]++;
  }

  // Find most common
  let maxDir: Direction = 'north';
  let maxCount = 0;
  for (const [dir, count] of Object.entries(counts) as Array<[Direction, number]>) {
    if (count > maxCount) {
      maxCount = count;
      maxDir = dir;
    }
  }

  // Confidence = proportion of dashes in preferred direction
  const confidence = maxCount / history.length;

  return {
    preferredDirection: confidence > 0.3 ? maxDir : null,
    confidence,
  };
}

function analyzeZonePreference(
  heatmap: number[][]
): 'center' | 'edge' | 'corner' | 'random' {
  const size = MEMORY_CONFIG.heatmapCells;
  let centerSum = 0;
  let edgeSum = 0;
  let cornerSum = 0;

  for (let y = 0; y < size; y++) {
    for (let x = 0; x < size; x++) {
      const val = heatmap[y][x];
      const isEdge = x === 0 || x === size - 1 || y === 0 || y === size - 1;
      const isCorner = (x === 0 || x === size - 1) && (y === 0 || y === size - 1);
      const isCenter = x >= size / 3 && x < (size * 2) / 3 &&
                       y >= size / 3 && y < (size * 2) / 3;

      if (isCorner) cornerSum += val;
      else if (isEdge) edgeSum += val;
      else if (isCenter) centerSum += val;
    }
  }

  const total = centerSum + edgeSum + cornerSum;
  if (total < 100) return 'random'; // Not enough data

  const centerPct = centerSum / total;
  const edgePct = edgeSum / total;
  const cornerPct = cornerSum / total;

  if (centerPct > 0.4) return 'center';
  if (edgePct > 0.5) return 'edge';
  if (cornerPct > 0.3) return 'corner';
  return 'random';
}

function analyzeEscapePatterns(
  history: EscapeAttempt[]
): number | null {
  const successful = history.filter(e => e.success);
  if (successful.length < 2) return null;

  // Average escape direction (circular mean)
  let sinSum = 0;
  let cosSum = 0;
  for (const attempt of successful) {
    sinSum += Math.sin(attempt.escapeDirection);
    cosSum += Math.cos(attempt.escapeDirection);
  }

  return Math.atan2(sinSum / successful.length, cosSum / successful.length);
}

function detectArchetype(
  memory: ColonyMemory,
  upgradeChoices: string[]
): { type: PlayerArchetype; confidence: number } {
  // Look for patterns in upgrades and behavior
  const hasDamageUpgrades = upgradeChoices.some(id =>
    id.includes('damage') || id.includes('attack') || id.includes('pierce')
  );
  const hasSurvivalUpgrades = upgradeChoices.some(id =>
    id.includes('health') || id.includes('regen') || id.includes('armor')
  );
  const hasSpeedUpgrades = upgradeChoices.some(id =>
    id.includes('speed') || id.includes('dash')
  );

  // Combine with behavior
  const isAggressive = memory.aggressionLevel > 0.6;
  const isDasher = memory.dashFrequency.mean > 0 &&
                   memory.dashFrequency.mean < MEMORY_CONFIG.dasherFrequency;

  if (isAggressive && hasDamageUpgrades) {
    return { type: 'aggressor', confidence: 0.7 };
  }

  if (isDasher && hasSpeedUpgrades) {
    return { type: 'dasher', confidence: 0.6 };
  }

  if (!isAggressive && hasSurvivalUpgrades) {
    return { type: 'kiter', confidence: 0.5 };
  }

  if (memory.preferredZone === 'center' || memory.preferredZone === 'corner') {
    return { type: 'holder', confidence: 0.4 };
  }

  return { type: 'unknown', confidence: 0 };
}

function addSample(stats: PatternStats, value: number): PatternStats {
  const newSamples = [...stats.samples, value].slice(-20); // Rolling window of 20
  const count = newSamples.length;
  const mean = newSamples.reduce((a, b) => a + b, 0) / count;

  let variance = 0;
  for (const v of newSamples) {
    variance += (v - mean) ** 2;
  }
  const stdDev = Math.sqrt(variance / count);

  return { samples: newSamples, count, mean, stdDev };
}

// =============================================================================
// Colony Adaptation (How memory affects behavior)
// =============================================================================

/**
 * Get anticipated dash direction based on player history
 *
 * Used by THE BALL to place the gap in the OPPOSITE direction
 * of where the player usually dashes.
 */
export function getAnticipatedDashDirection(
  memory: ColonyMemory
): { direction: Direction | null; confidence: number } {
  return {
    direction: memory.preferredDashDirection,
    confidence: memory.dashDirectionConfidence,
  };
}

/**
 * Get optimal gap placement for THE BALL
 *
 * If we know the player tends to escape eastward, place the gap...
 * NOT in the east (that would be too easy). But also not directly
 * opposite (that would be unfair). Place it at an angle that requires
 * the player to CHANGE their pattern to survive.
 */
export function getAdaptiveGapAngle(
  memory: ColonyMemory,
  defaultGapAngle: number
): number {
  // If we don't know enough, use random
  if (memory.preferredEscapeDirection === null || memory.ballsEncountered < 2) {
    return defaultGapAngle;
  }

  // Place gap 90-135 degrees away from preferred escape direction
  // This is challenging but fair: player CAN escape if they adapt
  const offset = (Math.PI / 2) + (Math.random() * Math.PI / 4); // 90-135 degrees
  const direction = Math.random() > 0.5 ? 1 : -1;

  const adaptedAngle = memory.preferredEscapeDirection + (offset * direction);

  // Mark the learning as "used against"
  // (Side effect - would be cleaner with events)

  return adaptedAngle;
}

/**
 * Get coordination speed multiplier based on player aggression
 *
 * If player is aggressive (killing fast), colony coordinates faster.
 * If player is passive (killing slow), colony takes its time.
 */
export function getCoordinationSpeedMultiplier(memory: ColonyMemory): number {
  // Base: 1.0
  // Aggressive player: up to 1.5x
  // Passive player: down to 0.7x
  return 0.7 + (memory.aggressionLevel * 0.8);
}

/**
 * Should bees anticipate player position?
 *
 * Only if colony has learned enough.
 */
export function shouldAnticipate(memory: ColonyMemory): boolean {
  return memory.adaptationLevel >= 3;
}

/**
 * Get player's likely next position based on patterns
 */
export function getAnticipatedPosition(
  memory: ColonyMemory,
  currentPosition: Vector2,
  velocity: Vector2,
  lookahead: number // seconds
): Vector2 {
  if (!shouldAnticipate(memory)) {
    // Simple linear extrapolation
    return {
      x: currentPosition.x + velocity.x * lookahead,
      y: currentPosition.y + velocity.y * lookahead,
    };
  }

  // If we know they dash left often, bias the prediction left
  if (memory.preferredDashDirection && memory.dashDirectionConfidence > 0.5) {
    const directionBias = directionToVector(memory.preferredDashDirection);
    const biasStrength = memory.dashDirectionConfidence * 0.3; // Max 30% bias

    return {
      x: currentPosition.x + velocity.x * lookahead + directionBias.x * 50 * biasStrength,
      y: currentPosition.y + velocity.y * lookahead + directionBias.y * 50 * biasStrength,
    };
  }

  return {
    x: currentPosition.x + velocity.x * lookahead,
    y: currentPosition.y + velocity.y * lookahead,
  };
}

function directionToVector(dir: Direction): Vector2 {
  const vectors: Record<Direction, Vector2> = {
    north: { x: 0, y: -1 },
    south: { x: 0, y: 1 },
    east: { x: 1, y: 0 },
    west: { x: -1, y: 0 },
    northeast: { x: 0.707, y: -0.707 },
    northwest: { x: -0.707, y: -0.707 },
    southeast: { x: 0.707, y: 0.707 },
    southwest: { x: -0.707, y: 0.707 },
  };
  return vectors[dir];
}

// =============================================================================
// Death Screen Data
// =============================================================================

/**
 * Get learnings for the death screen
 *
 * V5: WITNESSED - Show what colony learned, frame collaboratively
 */
export function getDeathScreenLearnings(
  memory: ColonyMemory
): {
  headline: string;
  learnings: ColonyLearning[];
  adaptationLevel: number;
  ballsEscaped: number;
  ballsEncountered: number;
} {
  // Filter to high-confidence learnings
  const significantLearnings = memory.learnings
    .filter(l => l.confidence > MEMORY_CONFIG.mediumConfidenceThreshold)
    .slice(0, 3); // Max 3 for readability

  // Generate headline based on adaptation level
  let headline: string;
  if (memory.adaptationLevel < 3) {
    headline = "The colony overwhelmed you.";
  } else if (memory.adaptationLevel < 6) {
    headline = "The colony learned your patterns.";
  } else {
    headline = "The colony predicted your every move.";
  }

  return {
    headline,
    learnings: significantLearnings,
    adaptationLevel: memory.adaptationLevel,
    ballsEscaped: memory.ballsEscaped,
    ballsEncountered: memory.ballsEncountered,
  };
}

/**
 * Generate shareable summary text
 */
export function generateRunSummary(memory: ColonyMemory): string {
  const lines: string[] = [];

  if (memory.detectedArchetype !== 'unknown') {
    lines.push(`Played as ${archetypeToHuman(memory.detectedArchetype)}`);
  }

  if (memory.ballsEncountered > 0) {
    lines.push(`Escaped ${memory.ballsEscaped}/${memory.ballsEncountered} BALL formations`);
  }

  if (memory.preferredDashDirection) {
    lines.push(`The colony learned: prefers ${directionToHuman(memory.preferredDashDirection)} dashes`);
  }

  return lines.join(' | ');
}
