/**
 * Region to grid position mapping for the Town Mesa.
 *
 * The Mesa is a 20x20 grid. Regions have fixed base positions,
 * and citizens within the same region are offset slightly to avoid overlap.
 */

export interface GridPosition {
  x: number;
  y: number;
}

// Base positions for each region (20x20 grid)
export const REGION_GRID_POSITIONS: Record<string, GridPosition> = {
  // Town center
  square: { x: 10, y: 10 },
  town_square: { x: 10, y: 10 },
  market: { x: 14, y: 8 },
  inn: { x: 6, y: 8 },

  // East side
  workshop: { x: 16, y: 12 },
  smithy: { x: 18, y: 14 },
  forge: { x: 17, y: 13 },

  // West side
  temple: { x: 4, y: 10 },
  library: { x: 4, y: 14 },
  archive: { x: 3, y: 15 },

  // North
  garden: { x: 10, y: 4 },
  well: { x: 8, y: 2 },
  fountain: { x: 10, y: 3 },

  // South
  farm: { x: 10, y: 16 },
  granary: { x: 14, y: 18 },
  barn: { x: 12, y: 17 },

  // Residential
  homes: { x: 6, y: 14 },
  cottages: { x: 14, y: 14 },
};

/**
 * Convert a region name to a grid position.
 *
 * If multiple citizens are in the same region, they are offset
 * in a circular pattern around the base position.
 *
 * @param region - The region name
 * @param citizenIndex - Index of this citizen among those in the region
 * @param citizensInRegion - Total citizens in this region
 * @returns Grid position {x, y}
 */
export function regionToGridPosition(
  region: string,
  citizenIndex: number = 0,
  citizensInRegion: number = 1
): GridPosition {
  const base = REGION_GRID_POSITIONS[region] || { x: 10, y: 10 };

  // Single citizen: return base position
  if (citizensInRegion <= 1) {
    return base;
  }

  // Multiple citizens: arrange in circle around base
  const angleStep = (2 * Math.PI) / citizensInRegion;
  const angle = angleStep * citizenIndex;
  const radius = Math.min(2, Math.ceil(citizensInRegion / 4)); // Expand radius for larger groups

  return {
    x: Math.round(base.x + Math.cos(angle) * radius),
    y: Math.round(base.y + Math.sin(angle) * radius),
  };
}

/**
 * Convert grid position to isometric screen coordinates.
 *
 * Uses standard isometric projection:
 * - screenX = (gridX - gridY) * cellWidth * 0.866
 * - screenY = (gridX + gridY) * cellHeight * 0.5
 *
 * @param gridX - Grid X coordinate (0-19)
 * @param gridY - Grid Y coordinate (0-19)
 * @param cellSize - Size of each grid cell in pixels
 * @param offsetX - X offset for centering
 * @param offsetY - Y offset for centering
 * @returns Screen position {x, y}
 */
export function gridToScreen(
  gridX: number,
  gridY: number,
  cellSize: number = 24,
  offsetX: number = 400,
  offsetY: number = 150
): { x: number; y: number } {
  const x = (gridX - gridY) * (cellSize * 0.866) + offsetX;
  const y = (gridX + gridY) * (cellSize * 0.5) + offsetY;
  return { x, y };
}

/**
 * Convert screen coordinates to grid position.
 *
 * Inverse of gridToScreen().
 *
 * @param screenX - Screen X coordinate
 * @param screenY - Screen Y coordinate
 * @param cellSize - Size of each grid cell in pixels
 * @param offsetX - X offset for centering
 * @param offsetY - Y offset for centering
 * @returns Grid position {x, y} (rounded to integers)
 */
export function screenToGrid(
  screenX: number,
  screenY: number,
  cellSize: number = 24,
  offsetX: number = 400,
  offsetY: number = 150
): GridPosition {
  const relX = screenX - offsetX;
  const relY = screenY - offsetY;

  const gridX = (relX / (cellSize * 0.866) + relY / (cellSize * 0.5)) / 2;
  const gridY = (relY / (cellSize * 0.5) - relX / (cellSize * 0.866)) / 2;

  return {
    x: Math.round(gridX),
    y: Math.round(gridY),
  };
}

/**
 * Check if a grid position is within bounds.
 */
export function isInBounds(
  x: number,
  y: number,
  gridWidth: number = 20,
  gridHeight: number = 20
): boolean {
  return x >= 0 && x < gridWidth && y >= 0 && y < gridHeight;
}

/**
 * Get neighboring grid positions.
 */
export function getNeighbors(
  x: number,
  y: number,
  gridWidth: number = 20,
  gridHeight: number = 20
): GridPosition[] {
  const directions = [
    { dx: 0, dy: -1 }, // up
    { dx: 1, dy: 0 }, // right
    { dx: 0, dy: 1 }, // down
    { dx: -1, dy: 0 }, // left
  ];

  return directions
    .map(({ dx, dy }) => ({ x: x + dx, y: y + dy }))
    .filter(({ x: nx, y: ny }) => isInBounds(nx, ny, gridWidth, gridHeight));
}
