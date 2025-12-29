/**
 * WASM Survivors - Pheromone Grid System
 *
 * Colony Intelligence Layer 1: Communication
 *
 * Real honeybees communicate via pheromones. This system creates a spatial
 * grid where bees can leave and read chemical signals, enabling emergent
 * coordination without explicit communication.
 *
 * Pheromone Types:
 * - ALARM: "Player attacked here!" - Bees become cautious, speed up
 * - TRAIL: "Player moved through here" - Track movement patterns
 * - DEATH: "A bee died here" - Avoid areas (survival instinct)
 * - COORDINATION: "Form THE BALL here!" - Triggers gathering
 *
 * The key insight: Individual bees following simple pheromone rules
 * create the illusion of a LEARNING SUPERORGANISM.
 *
 * @see PROTO_SPEC.md Part XI Phase 4: Colony Intelligence
 */

import type { Vector2 } from '../types';

// =============================================================================
// Types
// =============================================================================

/**
 * Pheromone types and their meanings
 */
export type PheromoneType = 'alarm' | 'trail' | 'death' | 'coordination';

/**
 * A single pheromone deposit
 */
export interface Pheromone {
  type: PheromoneType;
  position: Vector2;
  intensity: number;       // 0-1, decays over time
  sourceId: string;        // Bee ID or 'player'
  timestamp: number;       // Game time when deposited
  direction?: Vector2;     // For trail pheromones: movement direction
}

/**
 * Grid cell containing aggregated pheromone data
 */
export interface PheromoneCell {
  alarm: number;           // 0-1 aggregated alarm intensity
  trail: number;           // 0-1 aggregated trail intensity
  death: number;           // 0-1 aggregated death intensity
  coordination: number;    // 0-1 aggregated coordination intensity
  trailDirection: Vector2 | null; // Average movement direction
  lastUpdate: number;
}

/**
 * What a bee "smells" at its position
 */
export interface PheromoneReading {
  alarm: number;
  trail: number;
  death: number;
  coordination: number;
  trailDirection: Vector2 | null;
  strongestType: PheromoneType | null;
  gradient: Vector2;       // Direction toward stronger pheromone
}

// =============================================================================
// Configuration
// =============================================================================

export const PHEROMONE_CONFIG = {
  // Grid resolution (lower = more detailed, more expensive)
  cellSize: 40, // 40px cells (800x600 = 20x15 grid = 300 cells)

  // Decay rates (per second) - how fast pheromones fade
  decay: {
    alarm: 0.3,        // Fast decay - immediate response
    trail: 0.1,        // Slow decay - track movement history
    death: 0.05,       // Very slow - long memory of danger zones
    coordination: 0.5, // Fast - only relevant during active coordination
  },

  // Diffusion rates (per second) - how fast pheromones spread to neighbors
  diffusion: {
    alarm: 0.4,        // Spreads quickly (panic)
    trail: 0.1,        // Spreads slowly (path marking)
    death: 0.2,        // Moderate spread (avoid general area)
    coordination: 0.6, // Spreads quickly (urgent gathering)
  },

  // Deposit strengths (when creating new pheromones)
  deposit: {
    alarm: 0.8,        // Strong signal
    trail: 0.3,        // Subtle marking
    death: 1.0,        // Maximum (death is memorable)
    coordination: 1.0, // Maximum (THE BALL is urgent)
  },

  // Behavior thresholds
  thresholds: {
    alarmResponse: 0.3,    // Bee notices alarm
    trailFollow: 0.2,      // Bee can follow trail
    deathAvoid: 0.4,       // Bee avoids area
    coordinationJoin: 0.5, // Bee joins formation
  },

  // Memory limits
  maxPheromones: 500, // Limit active pheromone deposits
} as const;

// =============================================================================
// Grid State
// =============================================================================

export interface PheromoneGrid {
  cells: PheromoneCell[][];
  width: number;          // Grid width in cells
  height: number;         // Grid height in cells
  cellSize: number;       // Cell size in pixels
  pheromones: Pheromone[]; // Active pheromone deposits
  arenaWidth: number;
  arenaHeight: number;
}

/**
 * Create an empty pheromone grid
 */
export function createPheromoneGrid(
  arenaWidth: number,
  arenaHeight: number,
  cellSize = PHEROMONE_CONFIG.cellSize
): PheromoneGrid {
  const width = Math.ceil(arenaWidth / cellSize);
  const height = Math.ceil(arenaHeight / cellSize);

  const cells: PheromoneCell[][] = [];
  for (let y = 0; y < height; y++) {
    cells[y] = [];
    for (let x = 0; x < width; x++) {
      cells[y][x] = createEmptyCell();
    }
  }

  return {
    cells,
    width,
    height,
    cellSize,
    pheromones: [],
    arenaWidth,
    arenaHeight,
  };
}

function createEmptyCell(): PheromoneCell {
  return {
    alarm: 0,
    trail: 0,
    death: 0,
    coordination: 0,
    trailDirection: null,
    lastUpdate: 0,
  };
}

// =============================================================================
// Coordinate Helpers
// =============================================================================

function worldToGrid(pos: Vector2, grid: PheromoneGrid): { x: number; y: number } {
  return {
    x: Math.floor(Math.max(0, Math.min(pos.x, grid.arenaWidth - 1)) / grid.cellSize),
    y: Math.floor(Math.max(0, Math.min(pos.y, grid.arenaHeight - 1)) / grid.cellSize),
  };
}

function gridToWorld(gx: number, gy: number, grid: PheromoneGrid): Vector2 {
  return {
    x: (gx + 0.5) * grid.cellSize,
    y: (gy + 0.5) * grid.cellSize,
  };
}

function isValidCell(x: number, y: number, grid: PheromoneGrid): boolean {
  return x >= 0 && x < grid.width && y >= 0 && y < grid.height;
}

// =============================================================================
// Pheromone Deposit
// =============================================================================

/**
 * Deposit a pheromone at a world position
 */
export function depositPheromone(
  grid: PheromoneGrid,
  type: PheromoneType,
  position: Vector2,
  sourceId: string,
  gameTime: number,
  direction?: Vector2
): PheromoneGrid {
  // Create pheromone
  const pheromone: Pheromone = {
    type,
    position: { ...position },
    intensity: PHEROMONE_CONFIG.deposit[type],
    sourceId,
    timestamp: gameTime,
    direction,
  };

  // Add to list (with limit)
  const newPheromones = [...grid.pheromones, pheromone];
  if (newPheromones.length > PHEROMONE_CONFIG.maxPheromones) {
    // Remove oldest
    newPheromones.shift();
  }

  // Update grid cell
  const { x, y } = worldToGrid(position, grid);
  if (isValidCell(x, y, grid)) {
    const newCells = grid.cells.map(row => [...row]);
    const cell = { ...newCells[y][x] };
    cell[type] = Math.min(1, cell[type] + pheromone.intensity);
    if (type === 'trail' && direction) {
      cell.trailDirection = normalizeDirection(direction, cell.trailDirection);
    }
    cell.lastUpdate = gameTime;
    newCells[y][x] = cell;

    return { ...grid, cells: newCells, pheromones: newPheromones };
  }

  return { ...grid, pheromones: newPheromones };
}

function normalizeDirection(
  newDir: Vector2,
  existingDir: Vector2 | null
): Vector2 {
  if (!existingDir) return newDir;

  // Average directions (weighted toward new)
  const mixed = {
    x: existingDir.x * 0.3 + newDir.x * 0.7,
    y: existingDir.y * 0.3 + newDir.y * 0.7,
  };

  const mag = Math.sqrt(mixed.x * mixed.x + mixed.y * mixed.y);
  if (mag === 0) return newDir;
  return { x: mixed.x / mag, y: mixed.y / mag };
}

// =============================================================================
// Event-Based Deposits
// =============================================================================

/**
 * Deposit ALARM pheromone when player attacks
 */
export function depositAlarmAtAttack(
  grid: PheromoneGrid,
  attackPosition: Vector2,
  gameTime: number
): PheromoneGrid {
  return depositPheromone(grid, 'alarm', attackPosition, 'player', gameTime);
}

/**
 * Deposit TRAIL pheromone as player moves
 */
export function depositPlayerTrail(
  grid: PheromoneGrid,
  playerPosition: Vector2,
  playerVelocity: Vector2,
  gameTime: number
): PheromoneGrid {
  // Normalize velocity to direction
  const speed = Math.sqrt(playerVelocity.x ** 2 + playerVelocity.y ** 2);
  if (speed < 10) return grid; // Not moving fast enough

  const direction = {
    x: playerVelocity.x / speed,
    y: playerVelocity.y / speed,
  };

  return depositPheromone(grid, 'trail', playerPosition, 'player', gameTime, direction);
}

/**
 * Deposit DEATH pheromone when a bee dies
 */
export function depositDeathMark(
  grid: PheromoneGrid,
  deathPosition: Vector2,
  beeId: string,
  gameTime: number
): PheromoneGrid {
  return depositPheromone(grid, 'death', deathPosition, beeId, gameTime);
}

/**
 * Deposit COORDINATION pheromone to trigger THE BALL
 */
export function depositCoordinationSignal(
  grid: PheromoneGrid,
  ballCenter: Vector2,
  coordinatorId: string,
  gameTime: number
): PheromoneGrid {
  return depositPheromone(grid, 'coordination', ballCenter, coordinatorId, gameTime);
}

// =============================================================================
// Grid Update (Decay + Diffusion)
// =============================================================================

/**
 * Update the pheromone grid (call every frame or every few frames)
 */
export function updatePheromoneGrid(
  grid: PheromoneGrid,
  deltaTime: number,
  gameTime: number
): PheromoneGrid {
  const dt = deltaTime / 1000; // Convert to seconds
  const newCells = grid.cells.map(row => row.map(cell => ({ ...cell })));

  // Decay all cells
  for (let y = 0; y < grid.height; y++) {
    for (let x = 0; x < grid.width; x++) {
      const cell = newCells[y][x];

      // Decay each pheromone type
      cell.alarm = Math.max(0, cell.alarm - PHEROMONE_CONFIG.decay.alarm * dt);
      cell.trail = Math.max(0, cell.trail - PHEROMONE_CONFIG.decay.trail * dt);
      cell.death = Math.max(0, cell.death - PHEROMONE_CONFIG.decay.death * dt);
      cell.coordination = Math.max(0, cell.coordination - PHEROMONE_CONFIG.decay.coordination * dt);

      // Clear direction if trail is gone
      if (cell.trail < 0.05) {
        cell.trailDirection = null;
      }
    }
  }

  // Diffusion (spread to neighbors)
  const diffusionCells = newCells.map(row => row.map(cell => ({ ...cell })));

  for (let y = 0; y < grid.height; y++) {
    for (let x = 0; x < grid.width; x++) {
      const cell = diffusionCells[y][x];

      // For each neighbor, average in some of their pheromones
      const neighbors: Array<{ x: number; y: number }> = [
        { x: x - 1, y },
        { x: x + 1, y },
        { x, y: y - 1 },
        { x, y: y + 1 },
      ];

      for (const n of neighbors) {
        if (!isValidCell(n.x, n.y, grid)) continue;

        const neighbor = newCells[n.y][n.x];

        // Diffuse each type
        for (const type of ['alarm', 'trail', 'death', 'coordination'] as const) {
          const diffRate = PHEROMONE_CONFIG.diffusion[type] * dt * 0.25;
          const diff = neighbor[type] * diffRate;
          cell[type] = Math.min(1, cell[type] + diff);
        }
      }
    }
  }

  // Clean up old pheromones
  const newPheromones = grid.pheromones.filter(p => {
    const age = gameTime - p.timestamp;
    const maxAge = 30000; // 30 seconds max
    return age < maxAge;
  });

  return {
    ...grid,
    cells: diffusionCells,
    pheromones: newPheromones,
  };
}

// =============================================================================
// Pheromone Reading
// =============================================================================

/**
 * Read pheromones at a world position (what a bee "smells")
 */
export function readPheromones(
  grid: PheromoneGrid,
  position: Vector2
): PheromoneReading {
  const { x, y } = worldToGrid(position, grid);

  if (!isValidCell(x, y, grid)) {
    return {
      alarm: 0,
      trail: 0,
      death: 0,
      coordination: 0,
      trailDirection: null,
      strongestType: null,
      gradient: { x: 0, y: 0 },
    };
  }

  const cell = grid.cells[y][x];

  // Calculate gradient (direction toward stronger pheromone)
  const gradient = calculateGradient(grid, x, y);

  // Find strongest type
  const types: PheromoneType[] = ['alarm', 'trail', 'death', 'coordination'];
  let strongest: PheromoneType | null = null;
  let maxIntensity: number = PHEROMONE_CONFIG.thresholds.alarmResponse;

  for (const type of types) {
    if (cell[type] > maxIntensity) {
      maxIntensity = cell[type];
      strongest = type;
    }
  }

  return {
    alarm: cell.alarm,
    trail: cell.trail,
    death: cell.death,
    coordination: cell.coordination,
    trailDirection: cell.trailDirection,
    strongestType: strongest,
    gradient,
  };
}

/**
 * Calculate gradient direction toward stronger pheromones
 */
function calculateGradient(
  grid: PheromoneGrid,
  x: number,
  y: number
): Vector2 {
  let gx = 0;
  let gy = 0;

  // Sample neighbors
  const directions = [
    { dx: -1, dy: 0 },
    { dx: 1, dy: 0 },
    { dx: 0, dy: -1 },
    { dx: 0, dy: 1 },
  ];

  const centerTotal = getTotalIntensity(grid.cells[y][x]);

  for (const { dx, dy } of directions) {
    const nx = x + dx;
    const ny = y + dy;

    if (!isValidCell(nx, ny, grid)) continue;

    const neighborTotal = getTotalIntensity(grid.cells[ny][nx]);
    const diff = neighborTotal - centerTotal;

    gx += dx * diff;
    gy += dy * diff;
  }

  // Normalize
  const mag = Math.sqrt(gx * gx + gy * gy);
  if (mag < 0.01) return { x: 0, y: 0 };
  return { x: gx / mag, y: gy / mag };
}

function getTotalIntensity(cell: PheromoneCell): number {
  // Weighted sum (coordination is most important)
  return (
    cell.alarm * 0.3 +
    cell.trail * 0.2 +
    cell.death * 0.1 +
    cell.coordination * 0.4
  );
}

// =============================================================================
// Bee Behavior Modifiers (How pheromones affect bee decisions)
// =============================================================================

/**
 * Get movement modifier for a bee based on local pheromones
 */
export function getBeeMovementModifier(
  reading: PheromoneReading
): {
  speedMultiplier: number;
  avoidanceVector: Vector2;
  coordinationPull: Vector2;
} {
  // Alarm: Speed up (panic)
  const speedMultiplier = 1 + reading.alarm * 0.5;

  // Death: Avoid
  const avoidanceVector = reading.death > PHEROMONE_CONFIG.thresholds.deathAvoid
    ? { x: -reading.gradient.x * 0.3, y: -reading.gradient.y * 0.3 }
    : { x: 0, y: 0 };

  // Coordination: Pull toward ball
  const coordinationPull = reading.coordination > PHEROMONE_CONFIG.thresholds.coordinationJoin
    ? { x: reading.gradient.x * 0.5, y: reading.gradient.y * 0.5 }
    : { x: 0, y: 0 };

  return { speedMultiplier, avoidanceVector, coordinationPull };
}

/**
 * Should this bee join THE BALL formation?
 */
export function shouldJoinFormation(reading: PheromoneReading): boolean {
  return reading.coordination > PHEROMONE_CONFIG.thresholds.coordinationJoin;
}

/**
 * Should this bee be cautious (move slower, don't attack)?
 */
export function shouldBeCautious(reading: PheromoneReading): boolean {
  return reading.death > PHEROMONE_CONFIG.thresholds.deathAvoid;
}

// =============================================================================
// Trail Following (for predicting player movement)
// =============================================================================

/**
 * Get anticipated player position based on trail pheromones
 *
 * This is how the colony "learns" player movement patterns.
 * By following the trail and its direction, bees can predict
 * where the player is going.
 */
export function getAnticipatedPlayerPosition(
  grid: PheromoneGrid,
  currentPlayerPos: Vector2,
  lookaheadTime: number // seconds
): Vector2 {
  const { x, y } = worldToGrid(currentPlayerPos, grid);

  if (!isValidCell(x, y, grid)) {
    return currentPlayerPos;
  }

  const cell = grid.cells[y][x];

  if (!cell.trailDirection || cell.trail < PHEROMONE_CONFIG.thresholds.trailFollow) {
    return currentPlayerPos;
  }

  // Estimate player speed (assume ~200 px/s)
  const estimatedSpeed = 200;
  const anticipation = {
    x: currentPlayerPos.x + cell.trailDirection.x * estimatedSpeed * lookaheadTime,
    y: currentPlayerPos.y + cell.trailDirection.y * estimatedSpeed * lookaheadTime,
  };

  return anticipation;
}

// =============================================================================
// Rendering (Debug Visualization)
// =============================================================================

/**
 * Render pheromone grid (for debugging)
 */
export function renderPheromoneGrid(
  ctx: CanvasRenderingContext2D,
  grid: PheromoneGrid,
  showType: PheromoneType | 'all' = 'all'
): void {
  ctx.save();
  ctx.globalAlpha = 0.3;

  for (let y = 0; y < grid.height; y++) {
    for (let x = 0; x < grid.width; x++) {
      const cell = grid.cells[y][x];
      const worldPos = gridToWorld(x, y, grid);

      if (showType === 'all' || showType === 'alarm') {
        if (cell.alarm > 0.1) {
          ctx.fillStyle = `rgba(255, 0, 0, ${cell.alarm * 0.5})`;
          ctx.fillRect(
            worldPos.x - grid.cellSize / 2,
            worldPos.y - grid.cellSize / 2,
            grid.cellSize,
            grid.cellSize
          );
        }
      }

      if (showType === 'all' || showType === 'trail') {
        if (cell.trail > 0.1) {
          ctx.fillStyle = `rgba(255, 255, 0, ${cell.trail * 0.5})`;
          ctx.fillRect(
            worldPos.x - grid.cellSize / 2,
            worldPos.y - grid.cellSize / 2,
            grid.cellSize,
            grid.cellSize
          );

          // Draw direction arrow
          if (cell.trailDirection) {
            ctx.strokeStyle = 'rgba(255, 255, 0, 0.8)';
            ctx.beginPath();
            ctx.moveTo(worldPos.x, worldPos.y);
            ctx.lineTo(
              worldPos.x + cell.trailDirection.x * 15,
              worldPos.y + cell.trailDirection.y * 15
            );
            ctx.stroke();
          }
        }
      }

      if (showType === 'all' || showType === 'death') {
        if (cell.death > 0.1) {
          ctx.fillStyle = `rgba(128, 0, 128, ${cell.death * 0.5})`;
          ctx.fillRect(
            worldPos.x - grid.cellSize / 2,
            worldPos.y - grid.cellSize / 2,
            grid.cellSize,
            grid.cellSize
          );
        }
      }

      if (showType === 'all' || showType === 'coordination') {
        if (cell.coordination > 0.1) {
          ctx.fillStyle = `rgba(255, 165, 0, ${cell.coordination * 0.5})`;
          ctx.fillRect(
            worldPos.x - grid.cellSize / 2,
            worldPos.y - grid.cellSize / 2,
            grid.cellSize,
            grid.cellSize
          );
        }
      }
    }
  }

  ctx.restore();
}
