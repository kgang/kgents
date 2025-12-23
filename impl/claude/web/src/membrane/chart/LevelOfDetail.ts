/**
 * LevelOfDetail — LOD system for astronomical chart
 *
 * Reduces rendering complexity at different zoom levels.
 * Enables scaling to millions of nodes.
 *
 * LOD Levels:
 * - LOD 0 (>0.5x zoom): Full detail + labels
 * - LOD 1 (0.2-0.5x): No labels, full stars
 * - LOD 2 (0.05-0.2x): Cluster aggregation
 * - LOD 3 (<0.05x): Heat map mode
 *
 * "The file is a lie. There is only the graph."
 */

import type { StarData } from './useAstronomicalData';
import { TIER_COLORS } from './StarRenderer';

// =============================================================================
// Types
// =============================================================================

export type LODLevel = 0 | 1 | 2 | 3;

export interface LODConfig {
  /** Show star labels */
  showLabels: boolean;
  /** Show individual stars */
  showStars: boolean;
  /** Show clusters instead of individual stars */
  showClusters: boolean;
  /** Show heat map */
  showHeatMap: boolean;
  /** Minimum star radius to render */
  minRadius: number;
  /** Maximum stars to render before clustering */
  maxVisibleStars: number;
  /** Glow effects enabled */
  glowEnabled: boolean;
}

export interface Cluster {
  id: string;
  x: number;
  y: number;
  radius: number;
  count: number;
  tier: number; // Dominant tier
  color: number;
  stars: StarData[];
}

// =============================================================================
// LOD Level Thresholds
// =============================================================================

const LOD_THRESHOLDS = {
  0: 0.5, // Full detail above 50% zoom
  1: 0.2, // No labels between 20-50%
  2: 0.05, // Clusters between 5-20%
  3: 0, // Heat map below 5%
} as const;

// =============================================================================
// LOD Configuration
// =============================================================================

const LOD_CONFIGS: Record<LODLevel, LODConfig> = {
  0: {
    showLabels: true,
    showStars: true,
    showClusters: false,
    showHeatMap: false,
    minRadius: 0,
    maxVisibleStars: Infinity,
    glowEnabled: true,
  },
  1: {
    showLabels: false,
    showStars: true,
    showClusters: false,
    showHeatMap: false,
    minRadius: 2,
    maxVisibleStars: 5000,
    glowEnabled: true,
  },
  2: {
    showLabels: false,
    showStars: false,
    showClusters: true,
    showHeatMap: false,
    minRadius: 0,
    maxVisibleStars: 500,
    glowEnabled: false,
  },
  3: {
    showLabels: false,
    showStars: false,
    showClusters: false,
    showHeatMap: true,
    minRadius: 0,
    maxVisibleStars: 100,
    glowEnabled: false,
  },
};

// =============================================================================
// LOD Functions
// =============================================================================

/**
 * Get the current LOD level based on zoom scale.
 */
export function getLODLevel(scale: number): LODLevel {
  if (scale >= LOD_THRESHOLDS[0]) return 0;
  if (scale >= LOD_THRESHOLDS[1]) return 1;
  if (scale >= LOD_THRESHOLDS[2]) return 2;
  return 3;
}

/**
 * Get the LOD configuration for a given scale.
 */
export function getLODConfig(scale: number): LODConfig {
  return LOD_CONFIGS[getLODLevel(scale)];
}

/**
 * Get readable label for LOD level.
 */
export function getLODLabel(level: LODLevel): string {
  const labels: Record<LODLevel, string> = {
    0: 'Full Detail',
    1: 'Simplified',
    2: 'Clusters',
    3: 'Heat Map',
  };
  return labels[level];
}

// =============================================================================
// Clustering
// =============================================================================

const CLUSTER_RADIUS = 50; // Base clustering radius in world units

/**
 * Create clusters from stars at low zoom levels.
 * Uses simple grid-based clustering for performance.
 */
export function clusterStars(
  stars: StarData[],
  scale: number,
  gridSize: number = CLUSTER_RADIUS
): Cluster[] {
  if (stars.length === 0) return [];

  // Adjust grid size based on zoom (smaller grid = more clusters at lower zoom)
  const effectiveGrid = gridSize / Math.max(scale, 0.01);

  // Grid-based clustering
  const grid = new Map<string, StarData[]>();

  for (const star of stars) {
    const gridX = Math.floor(star.x / effectiveGrid);
    const gridY = Math.floor(star.y / effectiveGrid);
    const key = `${gridX},${gridY}`;

    if (!grid.has(key)) {
      grid.set(key, []);
    }
    grid.get(key)!.push(star);
  }

  // Convert grid cells to clusters
  const clusters: Cluster[] = [];

  grid.forEach((cellStars, key) => {
    if (cellStars.length === 0) return;

    // Calculate cluster center (centroid)
    let sumX = 0,
      sumY = 0;
    const tierCounts = new Map<number, number>();

    for (const star of cellStars) {
      sumX += star.x;
      sumY += star.y;
      tierCounts.set(star.tier, (tierCounts.get(star.tier) ?? 0) + 1);
    }

    const centerX = sumX / cellStars.length;
    const centerY = sumY / cellStars.length;

    // Find dominant tier
    let dominantTier = 2;
    let maxTierCount = 0;
    tierCounts.forEach((count, tier) => {
      if (count > maxTierCount) {
        maxTierCount = count;
        dominantTier = tier;
      }
    });

    // Cluster radius based on count (log scale)
    const radius = Math.min(30, 5 + Math.log2(cellStars.length + 1) * 5);

    clusters.push({
      id: key,
      x: centerX,
      y: centerY,
      radius,
      count: cellStars.length,
      tier: dominantTier,
      color: TIER_COLORS[dominantTier] ?? TIER_COLORS[2],
      stars: cellStars,
    });
  });

  return clusters;
}

/**
 * Filter stars based on LOD config.
 * At lower LOD levels, only shows larger/more important stars.
 */
export function filterStarsForLOD(stars: StarData[], config: LODConfig): StarData[] {
  if (!config.showStars) return [];

  let filtered = stars;

  // Filter by minimum radius
  if (config.minRadius > 0) {
    filtered = filtered.filter((s) => s.radius >= config.minRadius);
  }

  // Limit count
  if (filtered.length > config.maxVisibleStars) {
    // Sort by importance (radius = evidence weight)
    filtered = [...filtered].sort((a, b) => b.radius - a.radius).slice(0, config.maxVisibleStars);
  }

  return filtered;
}

// =============================================================================
// Heat Map
// =============================================================================

export interface HeatMapCell {
  x: number;
  y: number;
  width: number;
  height: number;
  intensity: number; // 0-1
  color: number;
}

/**
 * Generate a heat map from star positions.
 * Used at the lowest LOD level.
 */
export function generateHeatMap(
  stars: StarData[],
  bounds: { minX: number; minY: number; maxX: number; maxY: number },
  gridSize: number = 50
): HeatMapCell[] {
  if (stars.length === 0) return [];

  const cells: HeatMapCell[] = [];
  const cellCounts = new Map<string, { count: number; tierSum: number }>();

  // Count stars per cell
  for (const star of stars) {
    const cellX = Math.floor((star.x - bounds.minX) / gridSize);
    const cellY = Math.floor((star.y - bounds.minY) / gridSize);
    const key = `${cellX},${cellY}`;

    if (!cellCounts.has(key)) {
      cellCounts.set(key, { count: 0, tierSum: 0 });
    }
    const cell = cellCounts.get(key)!;
    cell.count++;
    cell.tierSum += star.tier;
  }

  // Find max count for normalization
  let maxCount = 0;
  cellCounts.forEach((cell) => {
    maxCount = Math.max(maxCount, cell.count);
  });

  // Generate cells
  cellCounts.forEach((data, key) => {
    const [cx, cy] = key.split(',').map(Number);
    const avgTier = Math.round(data.tierSum / data.count);

    cells.push({
      x: bounds.minX + cx * gridSize,
      y: bounds.minY + cy * gridSize,
      width: gridSize,
      height: gridSize,
      intensity: data.count / maxCount,
      color: TIER_COLORS[avgTier] ?? TIER_COLORS[2],
    });
  });

  return cells;
}

export default {
  getLODLevel,
  getLODConfig,
  getLODLabel,
  clusterStars,
  filterStarsForLOD,
  generateHeatMap,
};
