/**
 * Telescope Utilities
 *
 * Core transformation and positioning logic for telescope navigation.
 */

import type { Point, GradientVector, GradientArrow } from './types';

// =============================================================================
// Focal Distance to Layer Visibility
// =============================================================================

/**
 * Map focal distance (0-1) to visible layers.
 *
 * Focal distance metaphor:
 * - 0.0 = Ground level (L7 only - Representations)
 * - 0.2 = Near ground (L6-L7 - Reflections + Representations)
 * - 0.4 = Mid-range (L5-L7 - Actions + Reflections + Representations)
 * - 0.6 = High altitude (L4-L7 - Specs + Actions + Reflections + Representations)
 * - 0.8 = Stratosphere (L2-L7 - Values + Goals + Specs + Actions + Reflections + Representations)
 * - 1.0 = Cosmic (L1-L7 - All layers including Axioms)
 */
export function focalDistanceToLayers(distance: number): number[] {
  // Clamp to [0, 1]
  const d = Math.max(0, Math.min(1, distance));

  // Map to layers (L7 at ground, L1 at cosmic)
  if (d >= 0.9) return [1, 2, 3, 4, 5, 6, 7]; // Cosmic - all layers
  if (d >= 0.75) return [2, 3, 4, 5, 6, 7]; // Stratosphere - no axioms
  if (d >= 0.6) return [3, 4, 5, 6, 7]; // High altitude
  if (d >= 0.4) return [4, 5, 6, 7]; // Mid-range
  if (d >= 0.2) return [5, 6, 7]; // Near ground
  if (d >= 0.1) return [6, 7]; // Very near ground
  return [7]; // Ground level
}

// =============================================================================
// Node Position Calculation
// =============================================================================

interface NodeLike {
  layer: number;
  node_id: string;
}

/**
 * Calculate node position on canvas.
 *
 * Layout strategy:
 * - Y-axis: Layer determines vertical position (L1 top, L7 bottom)
 * - X-axis: Evenly distribute nodes within layer
 * - Focal distance creates zoom effect toward center
 */
export function calculateNodePosition(
  node: NodeLike,
  allNodes: NodeLike[],
  focalDistance: number,
  canvasWidth: number = 800,
  canvasHeight: number = 600
): Point {
  // Base vertical position from layer (L1=0.1, L7=0.9)
  const baseY = ((node.layer - 1) / 6) * 0.8 + 0.1;

  // Horizontal position based on index within layer
  const layerNodes = allNodes.filter((n) => n.layer === node.layer);
  const index = layerNodes.findIndex((n) => n.node_id === node.node_id);
  const count = layerNodes.length;
  const baseX = count > 1 ? (index / (count - 1)) * 0.8 + 0.1 : 0.5;

  // Apply zoom effect (focal distance pulls toward center)
  const scale = 1 - focalDistance * 0.3; // Max 30% zoom
  const centerX = 0.5;
  const centerY = 0.5;

  const x = centerX + (baseX - centerX) * scale;
  const y = centerY + (baseY - centerY) * scale;

  // Convert to pixel coordinates
  return {
    x: x * canvasWidth,
    y: y * canvasHeight,
  };
}

// =============================================================================
// Gradient Arrow Building
// =============================================================================

/**
 * Build gradient arrows for visualization.
 *
 * Each gradient vector points toward lower loss (toward stability).
 */
export function buildGradientArrows(
  gradients: Map<string, GradientVector>,
  positions: Map<string, Point>
): GradientArrow[] {
  const arrows: GradientArrow[] = [];

  for (const [nodeId, gradient] of gradients.entries()) {
    const startPos = positions.get(nodeId);
    if (!startPos) continue;

    // Arrow length proportional to magnitude
    const arrowLength = gradient.magnitude * 60; // Max 60 pixels

    // Calculate end point
    const endX = startPos.x + gradient.x * arrowLength;
    const endY = startPos.y + gradient.y * arrowLength;

    // Color by magnitude (green -> orange -> red)
    const color = getGradientColor(gradient.magnitude);

    // Width by magnitude (thicker = stronger gradient)
    const width = 1 + gradient.magnitude * 2; // 1-3 pixels

    arrows.push({
      start: startPos,
      end: { x: endX, y: endY },
      color,
      magnitude: gradient.magnitude,
      width,
    });
  }

  return arrows;
}

/**
 * Map gradient magnitude to color (green -> orange -> red).
 */
function getGradientColor(magnitude: number): string {
  if (magnitude < 0.4) return '#22c55e'; // Green - stable
  if (magnitude < 0.7) return '#f59e0b'; // Orange - warning
  return '#ef4444'; // Red - critical
}

// =============================================================================
// Loss to Color (Viridis-like)
// =============================================================================

/**
 * Map loss value to viridis-like color.
 *
 * Color scheme:
 * - Low loss (<0.3): Purple - stable, grounded
 * - Mid loss (0.3-0.6): Blue-green - moderate drift
 * - High loss (>0.6): Yellow - semantic drift, needs attention
 */
export function getLossColor(loss: number): string {
  if (loss < 0.3) return '#440154'; // Deep purple - stable
  if (loss < 0.6) return '#31688e'; // Blue-green - mid
  return '#fde724'; // Yellow - high loss
}

// =============================================================================
// Node Filtering
// =============================================================================

/**
 * Filter nodes by loss threshold.
 */
export function filterNodesByLoss(
  nodes: Array<{ loss?: number }>,
  threshold: number
): Array<{ loss?: number }> {
  return nodes.filter((node) => (node.loss ?? 0) <= threshold);
}

/**
 * Find node with minimum loss.
 */
export function findLowestLossNode(
  nodes: Array<{ node_id: string; loss?: number }>
): string | null {
  if (nodes.length === 0) return null;

  let minNode = nodes[0];
  let minLoss = minNode.loss ?? Infinity;

  for (const node of nodes) {
    const loss = node.loss ?? Infinity;
    if (loss < minLoss) {
      minLoss = loss;
      minNode = node;
    }
  }

  return minNode.node_id;
}

/**
 * Find node with maximum loss.
 */
export function findHighestLossNode(
  nodes: Array<{ node_id: string; loss?: number }>
): string | null {
  if (nodes.length === 0) return null;

  let maxNode = nodes[0];
  let maxLoss = maxNode.loss ?? -Infinity;

  for (const node of nodes) {
    const loss = node.loss ?? -Infinity;
    if (loss > maxLoss) {
      maxLoss = loss;
      maxNode = node;
    }
  }

  return maxNode.node_id;
}

/**
 * Follow gradient to find next node (navigate toward lower loss).
 */
export function followGradient(
  currentNodeId: string,
  gradients: Map<string, GradientVector>,
  nodes: Array<{ node_id: string; loss?: number }>
): string | null {
  const gradient = gradients.get(currentNodeId);
  if (!gradient) return null;

  // Gradient points toward lower loss
  // Find node in that direction with lower loss
  const currentNode = nodes.find((n) => n.node_id === currentNodeId);
  if (!currentNode) return null;

  const currentLoss = currentNode.loss ?? Infinity;

  // Simple heuristic: find nearest node with lower loss
  let bestNode: string | null = null;
  let bestLoss = currentLoss;

  for (const node of nodes) {
    const loss = node.loss ?? Infinity;
    if (loss < bestLoss) {
      bestLoss = loss;
      bestNode = node.node_id;
    }
  }

  return bestNode;
}
