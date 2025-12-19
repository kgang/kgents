import { describe, it, expect } from 'vitest';
import {
  regionToGridPosition,
  gridToScreen,
  screenToGrid,
  isInBounds,
  getNeighbors,
  REGION_GRID_POSITIONS,
} from '@/lib/regionGrid';

describe('regionGrid', () => {
  describe('REGION_GRID_POSITIONS', () => {
    it('should have positions for all expected regions', () => {
      const expectedRegions = [
        'square',
        'town_square',
        'market',
        'inn',
        'workshop',
        'smithy',
        'forge',
        'temple',
        'library',
        'archive',
        'garden',
        'well',
        'fountain',
        'farm',
        'granary',
        'barn',
        'homes',
        'cottages',
      ];

      expectedRegions.forEach((region) => {
        expect(REGION_GRID_POSITIONS[region]).toBeDefined();
        expect(REGION_GRID_POSITIONS[region].x).toBeGreaterThanOrEqual(0);
        expect(REGION_GRID_POSITIONS[region].y).toBeGreaterThanOrEqual(0);
        expect(REGION_GRID_POSITIONS[region].x).toBeLessThan(20);
        expect(REGION_GRID_POSITIONS[region].y).toBeLessThan(20);
      });
    });

    it('should center town_square and square at (10, 10)', () => {
      expect(REGION_GRID_POSITIONS.square).toEqual({ x: 10, y: 10 });
      expect(REGION_GRID_POSITIONS.town_square).toEqual({ x: 10, y: 10 });
    });
  });

  describe('regionToGridPosition', () => {
    it('should return base position for single citizen', () => {
      const pos = regionToGridPosition('market', 0, 1);
      expect(pos).toEqual({ x: 14, y: 8 });
    });

    it('should return center position for unknown region', () => {
      const pos = regionToGridPosition('unknown_place', 0, 1);
      expect(pos).toEqual({ x: 10, y: 10 });
    });

    it('should offset multiple citizens in a region', () => {
      const pos1 = regionToGridPosition('square', 0, 3);
      const pos2 = regionToGridPosition('square', 1, 3);
      const pos3 = regionToGridPosition('square', 2, 3);

      // All should be near (10, 10) but different
      expect(pos1).not.toEqual(pos2);
      expect(pos2).not.toEqual(pos3);
      expect(pos1).not.toEqual(pos3);

      // All should be within radius of base
      const base = REGION_GRID_POSITIONS.square;
      [pos1, pos2, pos3].forEach((pos) => {
        const dx = Math.abs(pos.x - base.x);
        const dy = Math.abs(pos.y - base.y);
        expect(dx).toBeLessThanOrEqual(2);
        expect(dy).toBeLessThanOrEqual(2);
      });
    });

    it('should arrange citizens in circular pattern', () => {
      // With 4 citizens, they should be at 0, 90, 180, 270 degrees
      const positions = [0, 1, 2, 3].map((i) =>
        regionToGridPosition('square', i, 4)
      );

      // Check they're distinct
      const uniquePositions = new Set(positions.map((p) => `${p.x},${p.y}`));
      expect(uniquePositions.size).toBe(4);
    });
  });

  describe('gridToScreen', () => {
    it('should convert grid center to screen center with default offset', () => {
      const screen = gridToScreen(10, 10, 24, 400, 150);

      // At (10, 10), isometric projection gives:
      // x = (10 - 10) * 24 * 0.866 + 400 = 400
      // y = (10 + 10) * 24 * 0.5 + 150 = 390
      expect(screen.x).toBeCloseTo(400);
      expect(screen.y).toBeCloseTo(390);
    });

    it('should handle (0, 0) grid position', () => {
      const screen = gridToScreen(0, 0, 24, 400, 150);
      expect(screen.x).toBeCloseTo(400);
      expect(screen.y).toBeCloseTo(150);
    });

    it('should produce correct isometric offset', () => {
      // Moving right in grid (x+1) should move screen diagonally
      const origin = gridToScreen(0, 0, 24, 0, 0);
      const right = gridToScreen(1, 0, 24, 0, 0);
      const down = gridToScreen(0, 1, 24, 0, 0);

      // Right should increase both x and y
      expect(right.x).toBeGreaterThan(origin.x);
      expect(right.y).toBeGreaterThan(origin.y);

      // Down should decrease x and increase y
      expect(down.x).toBeLessThan(origin.x);
      expect(down.y).toBeGreaterThan(origin.y);
    });

    it('should respect custom cell size', () => {
      const small = gridToScreen(5, 5, 10, 0, 0);
      const large = gridToScreen(5, 5, 20, 0, 0);

      // Larger cell size should produce larger screen distance
      expect(large.y).toBe(small.y * 2);
    });
  });

  describe('screenToGrid', () => {
    it('should be inverse of gridToScreen', () => {
      const testCases = [
        { x: 0, y: 0 },
        { x: 10, y: 10 },
        { x: 5, y: 15 },
        { x: 19, y: 0 },
        { x: 0, y: 19 },
      ];

      testCases.forEach(({ x, y }) => {
        const screen = gridToScreen(x, y, 24, 400, 150);
        const grid = screenToGrid(screen.x, screen.y, 24, 400, 150);

        expect(grid.x).toBe(x);
        expect(grid.y).toBe(y);
      });
    });

    it('should round to nearest grid position', () => {
      // Slightly offset from exact screen position
      const screen = gridToScreen(10, 10, 24, 400, 150);
      const grid = screenToGrid(screen.x + 5, screen.y + 5, 24, 400, 150);

      // Should round back to (10, 10)
      expect(grid.x).toBe(10);
      expect(grid.y).toBe(10);
    });
  });

  describe('isInBounds', () => {
    it('should return true for positions within grid', () => {
      expect(isInBounds(0, 0)).toBe(true);
      expect(isInBounds(10, 10)).toBe(true);
      expect(isInBounds(19, 19)).toBe(true);
    });

    it('should return false for positions outside grid', () => {
      expect(isInBounds(-1, 0)).toBe(false);
      expect(isInBounds(0, -1)).toBe(false);
      expect(isInBounds(20, 0)).toBe(false);
      expect(isInBounds(0, 20)).toBe(false);
      expect(isInBounds(20, 20)).toBe(false);
    });

    it('should respect custom grid dimensions', () => {
      expect(isInBounds(5, 5, 10, 10)).toBe(true);
      expect(isInBounds(10, 10, 10, 10)).toBe(false);
    });
  });

  describe('getNeighbors', () => {
    it('should return 4 neighbors for center position', () => {
      const neighbors = getNeighbors(10, 10);

      expect(neighbors).toHaveLength(4);
      expect(neighbors).toContainEqual({ x: 10, y: 9 }); // up
      expect(neighbors).toContainEqual({ x: 11, y: 10 }); // right
      expect(neighbors).toContainEqual({ x: 10, y: 11 }); // down
      expect(neighbors).toContainEqual({ x: 9, y: 10 }); // left
    });

    it('should return 2 neighbors for corner position', () => {
      const neighbors = getNeighbors(0, 0);

      expect(neighbors).toHaveLength(2);
      expect(neighbors).toContainEqual({ x: 1, y: 0 }); // right
      expect(neighbors).toContainEqual({ x: 0, y: 1 }); // down
    });

    it('should return 3 neighbors for edge position', () => {
      const neighbors = getNeighbors(0, 10);

      expect(neighbors).toHaveLength(3);
      expect(neighbors).toContainEqual({ x: 0, y: 9 }); // up
      expect(neighbors).toContainEqual({ x: 1, y: 10 }); // right
      expect(neighbors).toContainEqual({ x: 0, y: 11 }); // down
    });

    it('should respect custom grid dimensions', () => {
      const neighbors = getNeighbors(4, 4, 5, 5);

      // (4, 4) is a corner in a 5x5 grid
      expect(neighbors).toHaveLength(2);
    });
  });

  describe('coordinate system consistency', () => {
    it('should maintain consistency across all regions', () => {
      // All regions should convert to valid screen positions
      Object.entries(REGION_GRID_POSITIONS).forEach(([_region, pos]) => {
        const screen = gridToScreen(pos.x, pos.y);
        const gridBack = screenToGrid(screen.x, screen.y);

        expect(gridBack.x).toBe(pos.x);
        expect(gridBack.y).toBe(pos.y);
      });
    });

    it('should produce non-overlapping screen positions for adjacent regions', () => {
      const screenPositions = Object.values(REGION_GRID_POSITIONS).map((pos) =>
        gridToScreen(pos.x, pos.y)
      );

      // Check that no two screen positions are exactly the same
      const uniquePositions = new Set(
        screenPositions.map((p) => `${p.x.toFixed(2)},${p.y.toFixed(2)}`)
      );

      // All unique except square and town_square which share position
      expect(uniquePositions.size).toBe(screenPositions.length - 1);
    });
  });
});
