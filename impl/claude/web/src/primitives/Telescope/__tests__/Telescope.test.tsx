/**
 * Telescope Component Tests
 */

import { describe, it, expect, vi } from 'vitest';
import { render } from '@testing-library/react';
import { Telescope } from '../Telescope';
import type { NodeProjection } from '../types';

describe('Telescope', () => {
  const mockNodes: NodeProjection[] = [
    {
      node_id: 'axiom-1',
      layer: 1,
      position: { x: 400, y: 100 },
      scale: 1.0,
      opacity: 1.0,
      is_focal: false,
      color: '#440154',
      loss: 0.2,
    },
    {
      node_id: 'spec-1',
      layer: 4,
      position: { x: 400, y: 300 },
      scale: 1.0,
      opacity: 1.0,
      is_focal: false,
      color: '#31688e',
      loss: 0.5,
    },
    {
      node_id: 'repr-1',
      layer: 7,
      position: { x: 400, y: 500 },
      scale: 1.0,
      opacity: 1.0,
      is_focal: false,
      color: '#fde724',
      loss: 0.9,
    },
  ];

  const mockGradients = new Map([
    ['axiom-1', { x: 0.5, y: 0.3, magnitude: 0.3 }],
    ['spec-1', { x: 0.2, y: 0.5, magnitude: 0.6 }],
  ]);

  it('renders telescope container', () => {
    const { container } = render(
      <Telescope nodes={mockNodes} gradients={mockGradients} />
    );

    const telescope = container.querySelector('.telescope');
    expect(telescope).toBeTruthy();
  });

  it('renders SVG canvas', () => {
    const { container } = render(
      <Telescope nodes={mockNodes} gradients={mockGradients} />
    );

    const canvas = container.querySelector('.telescope__canvas');
    expect(canvas).toBeTruthy();
    expect(canvas?.tagName).toBe('svg');
  });

  it('renders visible nodes', () => {
    const { container } = render(
      <Telescope
        nodes={mockNodes}
        gradients={mockGradients}
        initialState={{ focalDistance: 1.0 }} // Show all layers
      />
    );

    const nodes = container.querySelectorAll('.telescope__node');
    expect(nodes.length).toBeGreaterThan(0);
  });

  it('handles node clicks', () => {
    const handleClick = vi.fn();
    const { container } = render(
      <Telescope
        nodes={mockNodes}
        gradients={mockGradients}
        onNodeClick={handleClick}
      />
    );

    const node = container.querySelector('.telescope__node');
    if (node) {
      node.dispatchEvent(new MouseEvent('click', { bubbles: true }));
      expect(handleClick).toHaveBeenCalled();
    }
  });

  it('renders gradient arrows', () => {
    const { container } = render(
      <Telescope nodes={mockNodes} gradients={mockGradients} />
    );

    const arrows = container.querySelectorAll('.telescope__gradient-arrow');
    expect(arrows.length).toBeGreaterThan(0);
  });

  it('renders legend', () => {
    const { container } = render(
      <Telescope nodes={mockNodes} gradients={mockGradients} />
    );

    const legend = container.querySelector('.telescope__legend');
    expect(legend).toBeTruthy();
  });

  it('respects custom dimensions', () => {
    const { container } = render(
      <Telescope
        nodes={mockNodes}
        gradients={mockGradients}
        width={1000}
        height={800}
      />
    );

    const canvas = container.querySelector('.telescope__canvas');
    expect(canvas?.getAttribute('width')).toBe('1000');
    expect(canvas?.getAttribute('height')).toBe('800');
  });
});
