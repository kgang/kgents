/**
 * ViewportCuller — Only render stars visible in viewport
 *
 * Dramatically reduces draw calls for large graphs.
 * Works with Quadtree for O(log n) queries.
 *
 * "The file is a lie. There is only the graph."
 */

import type { StarData } from './useAstronomicalData';
import type { Bounds, QuadtreeItem } from './Quadtree';
import { buildQuadtree, Quadtree } from './Quadtree';

// =============================================================================
// Types
// =============================================================================

export interface ViewportBounds {
  /** Left edge in world coordinates */
  x: number;
  /** Top edge in world coordinates */
  y: number;
  /** Viewport width in world coordinates */
  width: number;
  /** Viewport height in world coordinates */
  height: number;
}

export interface CullResult<T> {
  /** Items visible in viewport */
  visible: T[];
  /** Total items before culling */
  total: number;
  /** Percentage of items visible */
  visiblePercent: number;
}

// =============================================================================
// ViewportCuller Class
// =============================================================================

/**
 * Efficiently culls items outside the current viewport.
 *
 * @template T - The type of items being culled
 */
export class ViewportCuller<T extends { x: number; y: number; radius?: number }> {
  private quadtree: Quadtree<T> | null = null;
  private items: T[] = [];
  private padding: number;

  /**
   * @param padding - Extra padding around viewport bounds (default: 50px in world units)
   */
  constructor(padding: number = 50) {
    this.padding = padding;
  }

  /**
   * Update the spatial index with new items.
   * Call this when items change position or when data changes.
   */
  update(items: T[]): void {
    this.items = items;

    // Build quadtree from items
    this.quadtree = buildQuadtree(
      items.map((item) => ({
        x: item.x,
        y: item.y,
        radius: (item as any).radius,
        data: item,
      }))
    );
  }

  /**
   * Get items visible in the viewport.
   */
  cull(viewport: ViewportBounds): CullResult<T> {
    if (!this.quadtree || this.items.length === 0) {
      return {
        visible: [],
        total: this.items.length,
        visiblePercent: 0,
      };
    }

    // Expand viewport by padding
    const queryBounds: Bounds = {
      x: viewport.x - this.padding,
      y: viewport.y - this.padding,
      width: viewport.width + this.padding * 2,
      height: viewport.height + this.padding * 2,
    };

    // Query quadtree
    const results = this.quadtree.queryBounds(queryBounds);
    const visible = results.map((item) => item.data);

    return {
      visible,
      total: this.items.length,
      visiblePercent: this.items.length > 0 ? (visible.length / this.items.length) * 100 : 0,
    };
  }

  /**
   * Find item at a specific point (for hit detection).
   * Uses the quadtree for efficient lookup.
   */
  hitTest(worldX: number, worldY: number, radius: number = 10): T | null {
    if (!this.quadtree) return null;

    const results = this.quadtree.queryRadius({ x: worldX, y: worldY }, radius);

    // Find closest item
    let closest: QuadtreeItem<T> | null = null;
    let closestDist = Infinity;

    for (const item of results) {
      const dx = item.x - worldX;
      const dy = item.y - worldY;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const effectiveRadius = item.radius ?? 0;

      // Check if point is inside the item
      if (dist - effectiveRadius < closestDist) {
        closestDist = dist - effectiveRadius;
        closest = item;
      }
    }

    return closest?.data ?? null;
  }

  /**
   * Get all items (unculled).
   */
  getAll(): T[] {
    return this.items;
  }

  /**
   * Clear the culler.
   */
  clear(): void {
    this.items = [];
    this.quadtree?.clear();
    this.quadtree = null;
  }
}

// =============================================================================
// Utility Functions
// =============================================================================

/**
 * Calculate viewport bounds in world coordinates.
 *
 * @param screenWidth - Viewport width in pixels
 * @param screenHeight - Viewport height in pixels
 * @param panX - Pan offset X (world units)
 * @param panY - Pan offset Y (world units)
 * @param scale - Zoom scale
 */
export function calculateViewportBounds(
  screenWidth: number,
  screenHeight: number,
  panX: number,
  panY: number,
  scale: number
): ViewportBounds {
  // Convert screen dimensions to world dimensions
  const worldWidth = screenWidth / scale;
  const worldHeight = screenHeight / scale;

  // Calculate world position (account for centering and pan)
  const worldX = -panX - worldWidth / 2;
  const worldY = -panY - worldHeight / 2;

  return {
    x: worldX,
    y: worldY,
    width: worldWidth,
    height: worldHeight,
  };
}

/**
 * Check if a point is visible in viewport (simple, no quadtree).
 */
export function isPointVisible(
  x: number,
  y: number,
  viewport: ViewportBounds,
  padding: number = 0
): boolean {
  return (
    x >= viewport.x - padding &&
    x <= viewport.x + viewport.width + padding &&
    y >= viewport.y - padding &&
    y <= viewport.y + viewport.height + padding
  );
}

/**
 * Simple culling without quadtree (for small datasets).
 */
export function simpleCull<T extends { x: number; y: number }>(
  items: T[],
  viewport: ViewportBounds,
  padding: number = 50
): T[] {
  return items.filter((item) => isPointVisible(item.x, item.y, viewport, padding));
}

// =============================================================================
// Star-specific Culler
// =============================================================================

/**
 * Pre-configured culler for StarData items.
 */
export function createStarCuller(): ViewportCuller<StarData> {
  return new ViewportCuller<StarData>(100); // Larger padding for glow effects
}

export default ViewportCuller;
