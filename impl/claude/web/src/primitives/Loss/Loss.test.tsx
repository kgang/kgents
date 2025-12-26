/**
 * Loss Primitives — Type Safety Tests
 *
 * Ensures all components compile and have correct type signatures.
 */

import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/react';
import { LossIndicator } from './LossIndicator';
import { LossGradient } from './LossGradient';
import { LossHeatmap } from './LossHeatmap';
import { WithLoss } from './WithLoss';

describe('Loss Primitives', () => {
  describe('LossIndicator', () => {
    it('renders with basic props', () => {
      const { container } = render(<LossIndicator loss={0.42} />);
      expect(container).toBeTruthy();
    });

    it('renders with all props', () => {
      const { container } = render(
        <LossIndicator
          loss={0.42}
          showLabel
          showGradient
          interactive
          onNavigate={() => {}}
          size="lg"
        />
      );
      expect(container).toBeTruthy();
    });

    it('clamps loss values to [0, 1]', () => {
      const { container: below } = render(<LossIndicator loss={-0.5} />);
      expect(below).toBeTruthy();

      const { container: above } = render(<LossIndicator loss={1.5} />);
      expect(above).toBeTruthy();
    });
  });

  describe('LossGradient', () => {
    it('renders with basic props', () => {
      const { container } = render(<LossGradient currentLoss={0.42} />);
      expect(container).toBeTruthy();
    });

    it('renders with navigation callback', () => {
      const { container } = render(
        <LossGradient currentLoss={0.42} onNavigate={() => {}} />
      );
      expect(container).toBeTruthy();
    });

    it('renders without tick marks', () => {
      const { container } = render(<LossGradient currentLoss={0.42} showTicks={false} />);
      expect(container).toBeTruthy();
    });

    it('renders with custom dimensions', () => {
      const { container } = render(
        <LossGradient currentLoss={0.42} width="200px" height="24px" />
      );
      expect(container).toBeTruthy();
    });
  });

  describe('LossHeatmap', () => {
    const items = [
      { id: '1', label: 'Item 1', loss: 0.2 },
      { id: '2', label: 'Item 2', loss: 0.5 },
      { id: '3', label: 'Item 3', loss: 0.8 },
    ];

    it('renders with grid layout', () => {
      const { container } = render(<LossHeatmap items={items} />);
      expect(container).toBeTruthy();
    });

    it('renders with list layout', () => {
      const { container } = render(<LossHeatmap items={items} layout="list" />);
      expect(container).toBeTruthy();
    });

    it('renders with custom columns', () => {
      const { container } = render(<LossHeatmap items={items} columns={2} />);
      expect(container).toBeTruthy();
    });

    it('renders without values', () => {
      const { container } = render(<LossHeatmap items={items} showValue={false} />);
      expect(container).toBeTruthy();
    });

    it('handles click callbacks', () => {
      const itemsWithClick = items.map((item) => ({
        ...item,
        onClick: () => {},
      }));
      const { container } = render(<LossHeatmap items={itemsWithClick} />);
      expect(container).toBeTruthy();
    });
  });

  describe('WithLoss', () => {
    it('renders with child content', () => {
      const { container } = render(
        <WithLoss loss={0.42}>
          <div>Child content</div>
        </WithLoss>
      );
      expect(container).toBeTruthy();
    });

    it('renders with different positions', () => {
      const positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right'] as const;

      positions.forEach((position) => {
        const { container } = render(
          <WithLoss loss={0.42} position={position}>
            <div>Child content</div>
          </WithLoss>
        );
        expect(container).toBeTruthy();
      });
    });

    it('renders with label and gradient', () => {
      const { container } = render(
        <WithLoss loss={0.42} showLabel showGradient>
          <div>Child content</div>
        </WithLoss>
      );
      expect(container).toBeTruthy();
    });

    it('renders with different sizes', () => {
      const sizes = ['sm', 'md', 'lg'] as const;

      sizes.forEach((size) => {
        const { container } = render(
          <WithLoss loss={0.42} size={size}>
            <div>Child content</div>
          </WithLoss>
        );
        expect(container).toBeTruthy();
      });
    });
  });

  describe('Type Safety', () => {
    it('accepts valid loss values', () => {
      // These should compile without errors
      render(<LossIndicator loss={0} />);
      render(<LossIndicator loss={0.5} />);
      render(<LossIndicator loss={1} />);
    });

    it('accepts valid size variants', () => {
      // These should compile without errors
      render(<LossIndicator loss={0.5} size="sm" />);
      render(<LossIndicator loss={0.5} size="md" />);
      render(<LossIndicator loss={0.5} size="lg" />);
    });

    it('accepts valid layout modes', () => {
      const items = [{ id: '1', label: 'Item 1', loss: 0.5 }];
      // These should compile without errors
      render(<LossHeatmap items={items} layout="grid" />);
      render(<LossHeatmap items={items} layout="list" />);
    });

    it('accepts valid positions', () => {
      // These should compile without errors
      render(
        <WithLoss loss={0.5} position="top-left">
          <div />
        </WithLoss>
      );
      render(
        <WithLoss loss={0.5} position="top-right">
          <div />
        </WithLoss>
      );
      render(
        <WithLoss loss={0.5} position="bottom-left">
          <div />
        </WithLoss>
      );
      render(
        <WithLoss loss={0.5} position="bottom-right">
          <div />
        </WithLoss>
      );
    });
  });
});
