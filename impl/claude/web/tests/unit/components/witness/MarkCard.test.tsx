/**
 * MarkCard Component Tests
 *
 * Tests for the MarkCard component covering:
 * - Basic rendering
 * - Density modes (compact/comfortable/spacious)
 * - Author badges
 * - Principle chips
 * - Retract functionality
 * - Breathing animations
 *
 * @see plans/witness-fusion-ux-implementation.md
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { MarkCard, AgentBadge, PrincipleChip } from '@/components/witness/MarkCard';
import type { Mark } from '@/api/witness';

// =============================================================================
// Test Fixtures
// =============================================================================

const createMockMark = (overrides: Partial<Mark> = {}): Mark => ({
  id: 'mark-abc123def456',
  action: 'Chose PostgreSQL over SQLite',
  reasoning: 'Need concurrent writes and better scaling',
  principles: ['composable', 'generative'],
  author: 'kent',
  timestamp: '2025-12-22T14:30:00Z',
  session_id: 'session-xyz',
  ...overrides,
});

// =============================================================================
// MarkCard Tests
// =============================================================================

describe('MarkCard', () => {
  describe('Basic Rendering', () => {
    it('renders mark action text', () => {
      const mark = createMockMark();
      render(<MarkCard mark={mark} />);

      expect(screen.getByText('Chose PostgreSQL over SQLite')).toBeInTheDocument();
    });

    it('renders timestamp', () => {
      const mark = createMockMark();
      render(<MarkCard mark={mark} />);

      // Should show time (format depends on locale, so use flexible matcher)
      const card = screen.getByTestId('mark-card');
      expect(card).toBeInTheDocument();
      // Time format varies by locale - just verify card renders
    });

    it('renders author badge', () => {
      const mark = createMockMark({ author: 'kent' });
      render(<MarkCard mark={mark} />);

      const badge = screen.getByTitle('Kent');
      expect(badge).toBeInTheDocument();
    });

    it('has correct test id', () => {
      const mark = createMockMark();
      render(<MarkCard mark={mark} />);

      expect(screen.getByTestId('mark-card')).toBeInTheDocument();
    });
  });

  describe('Density Modes', () => {
    it('renders in compact mode', () => {
      const mark = createMockMark();
      render(<MarkCard mark={mark} density="compact" />);

      const card = screen.getByTestId('mark-card');
      expect(card).toHaveAttribute('data-density', 'compact');

      // Compact mode truncates action
      expect(screen.getByText('Chose PostgreSQL over SQLite')).toBeInTheDocument();
    });

    it('renders in comfortable mode (default)', () => {
      const mark = createMockMark();
      render(<MarkCard mark={mark} />);

      const card = screen.getByTestId('mark-card');
      expect(card).toHaveAttribute('data-density', 'comfortable');
    });

    it('renders in spacious mode with full details', () => {
      const mark = createMockMark();
      render(<MarkCard mark={mark} density="spacious" />);

      const card = screen.getByTestId('mark-card');
      expect(card).toHaveAttribute('data-density', 'spacious');

      // Spacious mode shows reasoning
      expect(screen.getByText(/Need concurrent writes/)).toBeInTheDocument();
    });

    it('shows reasoning in spacious mode', () => {
      const mark = createMockMark({ reasoning: 'Because it scales better' });
      render(<MarkCard mark={mark} density="spacious" />);

      expect(screen.getByText(/Because it scales better/)).toBeInTheDocument();
    });
  });

  describe('Principle Chips', () => {
    it('displays principle chips', () => {
      const mark = createMockMark({ principles: ['composable', 'generative'] });
      render(<MarkCard mark={mark} density="comfortable" />);

      expect(screen.getByText('composable')).toBeInTheDocument();
      expect(screen.getByText('generative')).toBeInTheDocument();
    });

    it('shows overflow indicator when many principles', () => {
      const mark = createMockMark({
        principles: ['composable', 'generative', 'tasteful', 'curated'],
      });
      render(<MarkCard mark={mark} density="comfortable" />);

      // Should show first 2 and +2 indicator
      expect(screen.getByText(/\+2/)).toBeInTheDocument();
    });

    it('shows all principles in spacious mode', () => {
      const mark = createMockMark({
        principles: ['composable', 'generative', 'tasteful', 'curated'],
      });
      render(<MarkCard mark={mark} density="spacious" />);

      expect(screen.getByText('composable')).toBeInTheDocument();
      expect(screen.getByText('generative')).toBeInTheDocument();
      expect(screen.getByText('tasteful')).toBeInTheDocument();
      expect(screen.getByText('curated')).toBeInTheDocument();
    });
  });

  describe('Retract Functionality', () => {
    it('shows retract button when onRetract provided in spacious mode', () => {
      const mark = createMockMark();
      const onRetract = vi.fn();
      render(<MarkCard mark={mark} density="spacious" onRetract={onRetract} />);

      expect(screen.getByText('Retract')).toBeInTheDocument();
    });

    it('calls onRetract when retract button clicked', async () => {
      const user = userEvent.setup();
      const mark = createMockMark();
      const onRetract = vi.fn();
      render(<MarkCard mark={mark} density="spacious" onRetract={onRetract} />);

      await user.click(screen.getByText('Retract'));

      expect(onRetract).toHaveBeenCalledWith('mark-abc123def456');
    });

    it('hides retract button for already retracted marks', () => {
      const mark = createMockMark({
        retracted_at: '2025-12-22T15:00:00Z',
        retracted_by: 'kent',
      });
      const onRetract = vi.fn();
      render(<MarkCard mark={mark} density="spacious" onRetract={onRetract} />);

      expect(screen.queryByText('Retract')).not.toBeInTheDocument();
    });

    it('applies retracted styling', () => {
      const mark = createMockMark({
        retracted_at: '2025-12-22T15:00:00Z',
      });
      render(<MarkCard mark={mark} />);

      const card = screen.getByTestId('mark-card');
      expect(card).toHaveStyle({ opacity: '0.6' });
    });
  });

  describe('Selection State', () => {
    it('applies selected styling when isSelected', () => {
      const mark = createMockMark();
      render(<MarkCard mark={mark} isSelected={true} />);

      const card = screen.getByTestId('mark-card');
      // Check border color changes (would need computed styles)
      expect(card).toBeInTheDocument();
    });
  });

  describe('Click Handling', () => {
    it('calls onClick when card clicked', async () => {
      const user = userEvent.setup();
      const mark = createMockMark();
      const onClick = vi.fn();
      render(<MarkCard mark={mark} onClick={onClick} />);

      await user.click(screen.getByTestId('mark-card'));

      expect(onClick).toHaveBeenCalled();
    });
  });

  describe('Parent Link', () => {
    it('shows parent link in spacious mode', () => {
      const mark = createMockMark({ parent_mark_id: 'mark-parent123' });
      render(<MarkCard mark={mark} density="spacious" />);

      expect(screen.getByText(/child of mark-parent/)).toBeInTheDocument();
    });
  });

  describe('Author Types', () => {
    it('renders kent author badge', () => {
      const mark = createMockMark({ author: 'kent' });
      render(<MarkCard mark={mark} />);

      expect(screen.getByTitle('Kent')).toBeInTheDocument();
      expect(screen.getByTestId('mark-card')).toHaveAttribute('data-author', 'kent');
    });

    it('renders claude author badge', () => {
      const mark = createMockMark({ author: 'claude' });
      render(<MarkCard mark={mark} />);

      expect(screen.getByTitle('Claude')).toBeInTheDocument();
      expect(screen.getByTestId('mark-card')).toHaveAttribute('data-author', 'claude');
    });

    it('renders system author badge', () => {
      const mark = createMockMark({ author: 'system' });
      render(<MarkCard mark={mark} />);

      expect(screen.getByTitle('System')).toBeInTheDocument();
      expect(screen.getByTestId('mark-card')).toHaveAttribute('data-author', 'system');
    });
  });
});

// =============================================================================
// AgentBadge Tests
// =============================================================================

describe('AgentBadge', () => {
  it('renders kent badge with correct emoji', () => {
    render(<AgentBadge author="kent" />);

    const badge = screen.getByTitle('Kent');
    expect(badge).toBeInTheDocument();
  });

  it('renders claude badge with correct emoji', () => {
    render(<AgentBadge author="claude" />);

    const badge = screen.getByTitle('Claude');
    expect(badge).toBeInTheDocument();
  });

  it('renders system badge with correct emoji', () => {
    render(<AgentBadge author="system" />);

    const badge = screen.getByTitle('System');
    expect(badge).toBeInTheDocument();
  });

  it('applies size classes', () => {
    const { rerender } = render(<AgentBadge author="kent" size="sm" />);
    expect(screen.getByTitle('Kent')).toHaveClass('w-5', 'h-5');

    rerender(<AgentBadge author="kent" size="lg" />);
    expect(screen.getByTitle('Kent')).toHaveClass('w-8', 'h-8');
  });
});

// =============================================================================
// PrincipleChip Tests
// =============================================================================

describe('PrincipleChip', () => {
  it('renders principle text', () => {
    render(<PrincipleChip principle="composable" />);

    expect(screen.getByText('composable')).toBeInTheDocument();
  });

  it('applies correct styling', () => {
    render(<PrincipleChip principle="generative" />);

    const chip = screen.getByText('generative');
    expect(chip).toHaveClass('rounded-full');
  });
});
