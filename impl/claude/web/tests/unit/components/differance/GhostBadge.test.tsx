/**
 * Tests for GhostBadge component.
 *
 * @see impl/claude/web/src/components/differance/GhostBadge.tsx
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { GhostBadge } from '@/components/differance/GhostBadge';

// =============================================================================
// GhostBadge Tests
// =============================================================================

describe('GhostBadge', () => {
  describe('rendering', () => {
    it('renders nothing when count is 0', () => {
      const { container } = render(<GhostBadge count={0} />);
      expect(container.firstChild).toBeNull();
    });

    it('renders nothing when count is negative', () => {
      const { container } = render(<GhostBadge count={-1} />);
      expect(container.firstChild).toBeNull();
    });

    it('renders badge when count is positive', () => {
      render(<GhostBadge count={3} />);
      // Without onClick, renders as span (not button) to avoid DOM nesting issues
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('renders singular tooltip for count=1', async () => {
      render(<GhostBadge count={1} />);
      // Title is on the span element
      const badge = screen.getByTitle('1 road not taken');
      expect(badge).toBeInTheDocument();
    });

    it('renders plural tooltip for count>1', async () => {
      render(<GhostBadge count={5} />);
      const badge = screen.getByTitle('5 roads not taken');
      expect(badge).toBeInTheDocument();
    });
  });

  describe('size variants', () => {
    it('renders sm size by default', () => {
      render(<GhostBadge count={3} />);
      const badge = screen.getByTitle('3 roads not taken');
      expect(badge.className).toContain('text-[10px]');
    });

    it('renders md size when specified', () => {
      render(<GhostBadge count={3} size="md" />);
      const badge = screen.getByTitle('3 roads not taken');
      expect(badge.className).toContain('text-xs');
    });
  });

  describe('interactivity', () => {
    it('calls onClick when clicked', () => {
      const handleClick = vi.fn();
      render(<GhostBadge count={3} onClick={handleClick} />);

      // With onClick, it renders as button
      fireEvent.click(screen.getByRole('button'));
      expect(handleClick).toHaveBeenCalledTimes(1);
    });

    it('renders as span without onClick to avoid DOM nesting issues', () => {
      render(<GhostBadge count={3} />);
      // Without onClick, renders as span (not button)
      expect(screen.queryByRole('button')).toBeNull();
      expect(screen.getByText('3')).toBeInTheDocument();
    });

    it('has correct title attribute for tooltip', () => {
      render(<GhostBadge count={5} explorableCount={2} />);
      const badge = screen.getByTitle('5 roads not taken');

      // The tooltip content is in the title attribute
      expect(badge).toHaveAttribute('title', '5 roads not taken');
    });
  });

  describe('explorable count', () => {
    // Note: The animated tooltip with explorable count appears on hover
    // via framer-motion AnimatePresence, which is tricky to test in jsdom.
    // The static behavior is tested via title attribute.
    it('includes explorable count prop without crashing', () => {
      // Just verify rendering works with explorableCount
      const { container } = render(<GhostBadge count={5} explorableCount={2} />);
      expect(container.firstChild).toBeInTheDocument();
    });

    it('handles zero explorable count', () => {
      const { container } = render(<GhostBadge count={5} explorableCount={0} />);
      expect(container.firstChild).toBeInTheDocument();
    });
  });

  describe('custom className', () => {
    it('applies custom className', () => {
      const { container } = render(<GhostBadge count={3} className="custom-class" />);
      expect(container.firstChild).toHaveClass('custom-class');
    });
  });
});
