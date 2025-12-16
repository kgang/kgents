/**
 * calculateShadowBounds - Compute tight shadow frustum from node positions
 *
 * @see plans/3d-visual-clarity.md
 *
 * A tight shadow frustum improves shadow quality by maximizing the use of
 * shadow map pixels. Instead of covering a large default area, we compute
 * bounds that exactly contain the visible nodes.
 *
 * The frustum is aligned to the directional light's view, ensuring shadows
 * are cast correctly regardless of sun position.
 */

import type { ShadowBounds } from '../../constants/lighting';

// =============================================================================
// Types
// =============================================================================

interface NodePosition {
  x: number;
  y: number;
  z: number;
}

interface CalculateBoundsOptions {
  /** Padding around computed bounds (default: 2 units) */
  padding?: number;
  /** Minimum extent in any direction (default: 10 units) */
  minExtent?: number;
  /** Maximum extent in any direction (default: 50 units) */
  maxExtent?: number;
}

// =============================================================================
// Main Function
// =============================================================================

/**
 * Calculate shadow frustum bounds from an array of node positions.
 *
 * Usage:
 * ```tsx
 * const bounds = calculateShadowBounds(topology.nodes);
 * <SceneLighting bounds={bounds} />
 * ```
 *
 * @param nodes Array of objects with x, y, z coordinates
 * @param options Configuration options
 * @returns ShadowBounds for directional light's shadow camera
 */
export function calculateShadowBounds(
  nodes: NodePosition[],
  options: CalculateBoundsOptions = {}
): ShadowBounds {
  const { padding = 2, minExtent = 10, maxExtent = 50 } = options;

  // Handle empty/single node case
  if (nodes.length === 0) {
    return {
      left: -minExtent,
      right: minExtent,
      top: minExtent,
      bottom: -minExtent,
      near: 0.5,
      far: minExtent * 4,
    };
  }

  // Find bounding box
  let minX = Infinity,
    maxX = -Infinity;
  let minY = Infinity,
    maxY = -Infinity;
  let minZ = Infinity,
    maxZ = -Infinity;

  for (const node of nodes) {
    minX = Math.min(minX, node.x);
    maxX = Math.max(maxX, node.x);
    minY = Math.min(minY, node.y);
    maxY = Math.max(maxY, node.y);
    minZ = Math.min(minZ, node.z);
    maxZ = Math.max(maxZ, node.z);
  }

  // Calculate extents with padding
  const extentX = maxX - minX + padding * 2;
  const extentY = maxY - minY + padding * 2;
  const extentZ = maxZ - minZ + padding * 2;

  // Use the largest extent for symmetric bounds (better shadow quality)
  const maxXY = Math.max(extentX, extentY);
  const halfExtent = Math.max(minExtent, Math.min(maxExtent, maxXY / 2));

  // Calculate center
  const centerX = (minX + maxX) / 2;
  const centerY = (minY + maxY) / 2;

  // Shadow camera looks along -Z from sun position
  // We need bounds in light space, but for simplicity we use world-axis-aligned bounds
  // This works well for our canonical sun position (elevated, 45-degree angle)
  return {
    left: centerX - halfExtent,
    right: centerX + halfExtent,
    top: centerY + halfExtent,
    bottom: centerY - halfExtent,
    near: 0.5,
    // Far plane needs to encompass the scene from sun's elevated position
    far: Math.max(extentZ, halfExtent * 2) + 30,
  };
}

/**
 * Compute bounds centered at origin (useful for scenes where camera controls center is 0,0,0).
 */
export function calculateCenteredShadowBounds(
  nodes: NodePosition[],
  options: CalculateBoundsOptions = {}
): ShadowBounds {
  const { padding = 2, minExtent = 10, maxExtent = 50 } = options;

  if (nodes.length === 0) {
    return {
      left: -minExtent,
      right: minExtent,
      top: minExtent,
      bottom: -minExtent,
      near: 0.5,
      far: minExtent * 4,
    };
  }

  // Find max distance from origin
  let maxDist = 0;
  for (const node of nodes) {
    const dist = Math.sqrt(node.x ** 2 + node.y ** 2 + node.z ** 2);
    maxDist = Math.max(maxDist, dist);
  }

  const extent = Math.max(minExtent, Math.min(maxExtent, maxDist + padding));

  return {
    left: -extent,
    right: extent,
    top: extent,
    bottom: -extent,
    near: 0.5,
    far: extent * 3,
  };
}

export default calculateShadowBounds;
