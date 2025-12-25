/**
 * Telescope Utility Function Tests
 */

import { describe, it, expect } from 'vitest';
import {
  focalDistanceToLayers,
  calculateNodePosition,
  getLossColor,
  findLowestLossNode,
  findHighestLossNode,
  buildGradientArrows,
} from '../utils';

describe('focalDistanceToLayers', () => {
  it('returns L7 only at ground level (0.0)', () => {
    expect(focalDistanceToLayers(0.0)).toEqual([7]);
  });

  it('returns L4-L7 at mid-range (0.5)', () => {
    expect(focalDistanceToLayers(0.5)).toEqual([4, 5, 6, 7]);
  });

  it('returns all layers at cosmic (1.0)', () => {
    expect(focalDistanceToLayers(1.0)).toEqual([1, 2, 3, 4, 5, 6, 7]);
  });

  it('clamps negative values to 0', () => {
    expect(focalDistanceToLayers(-0.5)).toEqual([7]);
  });

  it('clamps values > 1 to 1', () => {
    expect(focalDistanceToLayers(1.5)).toEqual([1, 2, 3, 4, 5, 6, 7]);
  });
});

describe('calculateNodePosition', () => {
  const nodes = [
    { layer: 1, node_id: 'a' },
    { layer: 4, node_id: 'b' },
    { layer: 7, node_id: 'c' },
  ];

  it('positions L1 near top', () => {
    const pos = calculateNodePosition(nodes[0], nodes, 0.5, 800, 600);
    expect(pos.y).toBeLessThan(300); // Upper half
  });

  it('positions L7 near bottom', () => {
    const pos = calculateNodePosition(nodes[2], nodes, 0.5, 800, 600);
    expect(pos.y).toBeGreaterThan(300); // Lower half
  });

  it('centers single nodes horizontally', () => {
    const singleNode = [{ layer: 4, node_id: 'single' }];
    const pos = calculateNodePosition(singleNode[0], singleNode, 0.5, 800, 600);
    expect(pos.x).toBeCloseTo(400, 0); // Centered at width/2
  });

  it('applies zoom effect with focal distance', () => {
    const posNoZoom = calculateNodePosition(nodes[0], nodes, 0.0, 800, 600);
    const posWithZoom = calculateNodePosition(nodes[0], nodes, 1.0, 800, 600);

    // Higher focal distance should pull nodes toward center
    expect(Math.abs(posWithZoom.x - 400)).toBeLessThan(Math.abs(posNoZoom.x - 400));
  });
});

describe('getLossColor', () => {
  it('returns purple for low loss', () => {
    expect(getLossColor(0.1)).toBe('#440154');
    expect(getLossColor(0.29)).toBe('#440154');
  });

  it('returns blue-green for mid loss', () => {
    expect(getLossColor(0.4)).toBe('#31688e');
    expect(getLossColor(0.59)).toBe('#31688e');
  });

  it('returns yellow for high loss', () => {
    expect(getLossColor(0.7)).toBe('#fde724');
    expect(getLossColor(0.99)).toBe('#fde724');
  });
});

describe('findLowestLossNode', () => {
  const nodes = [
    { node_id: 'a', loss: 0.8 },
    { node_id: 'b', loss: 0.2 },
    { node_id: 'c', loss: 0.5 },
  ];

  it('finds node with minimum loss', () => {
    expect(findLowestLossNode(nodes)).toBe('b');
  });

  it('returns null for empty array', () => {
    expect(findLowestLossNode([])).toBeNull();
  });

  it('handles nodes without loss', () => {
    const nodesWithoutLoss = [{ node_id: 'd' }];
    expect(findLowestLossNode(nodesWithoutLoss)).toBe('d');
  });
});

describe('findHighestLossNode', () => {
  const nodes = [
    { node_id: 'a', loss: 0.8 },
    { node_id: 'b', loss: 0.2 },
    { node_id: 'c', loss: 0.5 },
  ];

  it('finds node with maximum loss', () => {
    expect(findHighestLossNode(nodes)).toBe('a');
  });

  it('returns null for empty array', () => {
    expect(findHighestLossNode([])).toBeNull();
  });
});

describe('buildGradientArrows', () => {
  const gradients = new Map([
    ['a', { x: 1, y: 0, magnitude: 0.3 }],
    ['b', { x: 0, y: 1, magnitude: 0.6 }],
    ['c', { x: -1, y: 0, magnitude: 0.9 }],
  ]);

  const positions = new Map([
    ['a', { x: 100, y: 100 }],
    ['b', { x: 200, y: 200 }],
    ['c', { x: 300, y: 300 }],
  ]);

  it('builds arrows for all gradients', () => {
    const arrows = buildGradientArrows(gradients, positions);
    expect(arrows).toHaveLength(3);
  });

  it('colors arrows by magnitude', () => {
    const arrows = buildGradientArrows(gradients, positions);

    // Low magnitude -> green
    expect(arrows[0].color).toBe('#22c55e');

    // Mid magnitude -> orange
    expect(arrows[1].color).toBe('#f59e0b');

    // High magnitude -> red
    expect(arrows[2].color).toBe('#ef4444');
  });

  it('scales arrow width by magnitude', () => {
    const arrows = buildGradientArrows(gradients, positions);

    // Wider arrows for higher magnitude
    expect(arrows[2].width).toBeGreaterThan(arrows[0].width);
  });

  it('skips nodes without positions', () => {
    const incompletePositions = new Map([['a', { x: 100, y: 100 }]]);
    const arrows = buildGradientArrows(gradients, incompletePositions);
    expect(arrows).toHaveLength(1);
  });
});
