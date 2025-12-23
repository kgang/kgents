/**
 * Quadtree — Spatial index for efficient hit detection and culling
 *
 * Optimized for the astronomical chart's star lookup needs.
 * Supports viewport culling and point queries.
 *
 * "The file is a lie. There is only the graph."
 */

// =============================================================================
// Types
// =============================================================================

export interface Point {
  x: number;
  y: number;
}

export interface Bounds {
  x: number;
  y: number;
  width: number;
  height: number;
}

export interface QuadtreeItem<T> extends Point {
  data: T;
  radius?: number;
}

// =============================================================================
// Quadtree Implementation
// =============================================================================

const MAX_ITEMS = 8;
const MAX_DEPTH = 8;

/**
 * A quadtree for efficient spatial queries.
 *
 * @template T - The type of data stored in each item
 */
export class Quadtree<T> {
  private bounds: Bounds;
  private items: QuadtreeItem<T>[] = [];
  private children: Quadtree<T>[] | null = null;
  private depth: number;

  constructor(bounds: Bounds, depth: number = 0) {
    this.bounds = bounds;
    this.depth = depth;
  }

  /**
   * Insert an item into the quadtree.
   */
  insert(item: QuadtreeItem<T>): void {
    // If point is outside bounds, don't insert
    if (!this.containsPoint(item)) {
      return;
    }

    // If we have children, insert into appropriate child
    if (this.children) {
      const index = this.getChildIndex(item);
      if (index !== -1) {
        this.children[index].insert(item);
        return;
      }
    }

    // Add to this node
    this.items.push(item);

    // Split if needed
    if (this.items.length > MAX_ITEMS && this.depth < MAX_DEPTH) {
      this.subdivide();
    }
  }

  /**
   * Query items within a rectangular region.
   */
  queryBounds(bounds: Bounds): QuadtreeItem<T>[] {
    const results: QuadtreeItem<T>[] = [];

    // Skip if no intersection
    if (!this.intersectsBounds(bounds)) {
      return results;
    }

    // Add items from this node that are within bounds
    for (const item of this.items) {
      if (this.pointInBounds(item, bounds)) {
        results.push(item);
      }
    }

    // Query children
    if (this.children) {
      for (const child of this.children) {
        results.push(...child.queryBounds(bounds));
      }
    }

    return results;
  }

  /**
   * Query items within a circular region (for hit detection).
   */
  queryRadius(center: Point, radius: number): QuadtreeItem<T>[] {
    const results: QuadtreeItem<T>[] = [];

    // Create bounding box for circle
    const bounds: Bounds = {
      x: center.x - radius,
      y: center.y - radius,
      width: radius * 2,
      height: radius * 2,
    };

    // Skip if no intersection
    if (!this.intersectsBounds(bounds)) {
      return results;
    }

    // Check items in this node
    for (const item of this.items) {
      const dx = item.x - center.x;
      const dy = item.y - center.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      const itemRadius = item.radius ?? 0;
      if (dist <= radius + itemRadius) {
        results.push(item);
      }
    }

    // Query children
    if (this.children) {
      for (const child of this.children) {
        results.push(...child.queryRadius(center, radius));
      }
    }

    return results;
  }

  /**
   * Find the nearest item to a point.
   */
  queryNearest(point: Point, maxDistance: number = Infinity): QuadtreeItem<T> | null {
    let nearest: QuadtreeItem<T> | null = null;
    let nearestDist = maxDistance;

    const search = (node: Quadtree<T>) => {
      // Check items in this node
      for (const item of node.items) {
        const dx = item.x - point.x;
        const dy = item.y - point.y;
        const dist = Math.sqrt(dx * dx + dy * dy) - (item.radius ?? 0);
        if (dist < nearestDist) {
          nearestDist = dist;
          nearest = item;
        }
      }

      // Search children (nearest first for pruning)
      if (node.children) {
        // Sort children by distance to point
        const sortedChildren = [...node.children].sort((a, b) => {
          const distA = this.distToNode(point, a.bounds);
          const distB = this.distToNode(point, b.bounds);
          return distA - distB;
        });

        for (const child of sortedChildren) {
          // Prune if child is too far
          if (this.distToNode(point, child.bounds) > nearestDist) {
            break;
          }
          search(child);
        }
      }
    };

    search(this);
    return nearest;
  }

  /**
   * Clear all items from the quadtree.
   */
  clear(): void {
    this.items = [];
    this.children = null;
  }

  /**
   * Get total item count (for debugging).
   */
  get size(): number {
    let count = this.items.length;
    if (this.children) {
      for (const child of this.children) {
        count += child.size;
      }
    }
    return count;
  }

  // ---------------------------------------------------------------------------
  // Private Methods
  // ---------------------------------------------------------------------------

  private subdivide(): void {
    const { x, y, width, height } = this.bounds;
    const hw = width / 2;
    const hh = height / 2;

    this.children = [
      new Quadtree<T>({ x: x, y: y, width: hw, height: hh }, this.depth + 1), // NW
      new Quadtree<T>({ x: x + hw, y: y, width: hw, height: hh }, this.depth + 1), // NE
      new Quadtree<T>({ x: x, y: y + hh, width: hw, height: hh }, this.depth + 1), // SW
      new Quadtree<T>({ x: x + hw, y: y + hh, width: hw, height: hh }, this.depth + 1), // SE
    ];

    // Move existing items to children
    const toMove = this.items;
    this.items = [];
    for (const item of toMove) {
      const index = this.getChildIndex(item);
      if (index !== -1) {
        this.children[index].insert(item);
      } else {
        // Item spans multiple children, keep in parent
        this.items.push(item);
      }
    }
  }

  private getChildIndex(point: Point): number {
    if (!this.children) return -1;

    const { x, y, width, height } = this.bounds;
    const midX = x + width / 2;
    const midY = y + height / 2;

    const west = point.x < midX;
    const north = point.y < midY;

    if (north && west) return 0; // NW
    if (north && !west) return 1; // NE
    if (!north && west) return 2; // SW
    return 3; // SE
  }

  private containsPoint(point: Point): boolean {
    const { x, y, width, height } = this.bounds;
    return point.x >= x && point.x <= x + width && point.y >= y && point.y <= y + height;
  }

  private pointInBounds(point: Point, bounds: Bounds): boolean {
    return (
      point.x >= bounds.x &&
      point.x <= bounds.x + bounds.width &&
      point.y >= bounds.y &&
      point.y <= bounds.y + bounds.height
    );
  }

  private intersectsBounds(bounds: Bounds): boolean {
    return !(
      bounds.x > this.bounds.x + this.bounds.width ||
      bounds.x + bounds.width < this.bounds.x ||
      bounds.y > this.bounds.y + this.bounds.height ||
      bounds.y + bounds.height < this.bounds.y
    );
  }

  private distToNode(point: Point, bounds: Bounds): number {
    const dx = Math.max(bounds.x - point.x, 0, point.x - bounds.x - bounds.width);
    const dy = Math.max(bounds.y - point.y, 0, point.y - bounds.y - bounds.height);
    return Math.sqrt(dx * dx + dy * dy);
  }
}

/**
 * Build a quadtree from an array of positioned items.
 */
export function buildQuadtree<T>(
  items: Array<{ x: number; y: number; data: T; radius?: number }>,
  providedBounds?: Bounds
): Quadtree<T> {
  // Auto-calculate bounds if not provided
  let treeBounds: Bounds;

  if (providedBounds) {
    treeBounds = providedBounds;
  } else if (items.length === 0) {
    treeBounds = { x: -1000, y: -1000, width: 2000, height: 2000 };
  } else {
    let minX = Infinity,
      minY = Infinity,
      maxX = -Infinity,
      maxY = -Infinity;
    for (const item of items) {
      const r = item.radius ?? 0;
      minX = Math.min(minX, item.x - r);
      minY = Math.min(minY, item.y - r);
      maxX = Math.max(maxX, item.x + r);
      maxY = Math.max(maxY, item.y + r);
    }
    // Add padding
    const padding = 100;
    treeBounds = {
      x: minX - padding,
      y: minY - padding,
      width: maxX - minX + padding * 2,
      height: maxY - minY + padding * 2,
    };
  }

  const tree = new Quadtree<T>(treeBounds);
  for (const item of items) {
    tree.insert({
      x: item.x,
      y: item.y,
      data: item.data,
      radius: item.radius,
    });
  }

  return tree;
}

export default Quadtree;
