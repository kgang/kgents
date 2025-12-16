/**
 * Tests for PolynomialDiagram and related components.
 *
 * Foundation 3: Visible Polynomial State
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { renderHook } from '@testing-library/react';
import { PolynomialDiagram } from '../../../src/components/polynomial/PolynomialDiagram';
import { PolynomialNode } from '../../../src/components/polynomial/PolynomialNode';
import { usePolynomialState } from '../../../src/components/polynomial/usePolynomialState';
import {
  createGardenerVisualization,
  createNPhaseVisualization,
  createCitizenVisualization,
  createGenericVisualization,
} from '../../../src/components/polynomial/visualizations';
import type { PolynomialVisualization, PolynomialPosition, GardenerSessionState } from '../../../src/api/types';

// =============================================================================
// Test Data
// =============================================================================

const mockGardenerSession: GardenerSessionState = {
  session_id: 'test-123',
  name: 'Test Feature',
  phase: 'SENSE',
  plan_path: 'plans/test.md',
  intent: { description: 'Implement test feature', priority: 'high' },
  artifacts_count: 0,
  learnings_count: 0,
  sense_count: 1,
  act_count: 0,
  reflect_count: 0,
};

const mockVisualization: PolynomialVisualization = {
  id: 'test-poly',
  name: 'Test Polynomial',
  positions: [
    { id: 'A', label: 'State A', emoji: '🅰️', is_current: true, is_terminal: false },
    { id: 'B', label: 'State B', emoji: '🅱️', is_current: false, is_terminal: false },
    { id: 'C', label: 'State C', emoji: '©️', is_current: false, is_terminal: true },
  ],
  edges: [
    { source: 'A', target: 'B', is_valid: true, label: 'go_b' },
    { source: 'B', target: 'C', is_valid: true, label: 'go_c' },
    { source: 'B', target: 'A', is_valid: true, label: 'back' },
  ],
  current: 'A',
  valid_directions: ['B'],
  history: [],
  metadata: {},
};

// =============================================================================
// PolynomialNode Tests
// =============================================================================

describe('PolynomialNode', () => {
  const mockPosition: PolynomialPosition = {
    id: 'test',
    label: 'Test State',
    emoji: '🧪',
    is_current: false,
    is_terminal: false,
  };

  it('renders position label', () => {
    render(<PolynomialNode position={mockPosition} />);
    expect(screen.getByText('Test State')).toBeInTheDocument();
  });

  it('renders emoji when provided', () => {
    render(<PolynomialNode position={mockPosition} />);
    expect(screen.getByText('🧪')).toBeInTheDocument();
  });

  it('renders first letter when no emoji', () => {
    const noEmojiPosition = { ...mockPosition, emoji: undefined };
    render(<PolynomialNode position={noEmojiPosition} />);
    expect(screen.getByText('T')).toBeInTheDocument();
  });

  it('applies current state styling', () => {
    const currentPosition = { ...mockPosition, is_current: true };
    render(<PolynomialNode position={currentPosition} />);
    // Current state should have ring styling
    const button = screen.getByRole('button');
    expect(button).toHaveClass('ring-2');
  });

  it('calls onTransition when clicked and reachable', async () => {
    const onTransition = vi.fn();
    render(
      <PolynomialNode
        position={mockPosition}
        isReachable={true}
        onTransition={onTransition}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    expect(onTransition).toHaveBeenCalledWith('test');
  });

  it('does not call onTransition when not reachable', () => {
    const onTransition = vi.fn();
    render(
      <PolynomialNode
        position={mockPosition}
        isReachable={false}
        onTransition={onTransition}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    expect(onTransition).not.toHaveBeenCalled();
  });

  it('does not call onTransition when current', () => {
    const onTransition = vi.fn();
    const currentPosition = { ...mockPosition, is_current: true };
    render(
      <PolynomialNode
        position={currentPosition}
        isReachable={true}
        onTransition={onTransition}
      />
    );

    fireEvent.click(screen.getByRole('button'));
    expect(onTransition).not.toHaveBeenCalled();
  });

  it('renders compact variant', () => {
    render(<PolynomialNode position={mockPosition} variant="compact" />);
    // Compact variant should have smaller text
    expect(screen.getByText('Test State')).toHaveClass('text-xs');
  });
});

// =============================================================================
// PolynomialDiagram Tests
// =============================================================================

describe('PolynomialDiagram', () => {
  it('renders all positions', () => {
    render(<PolynomialDiagram visualization={mockVisualization} />);

    expect(screen.getByText('State A')).toBeInTheDocument();
    expect(screen.getByText('State B')).toBeInTheDocument();
    expect(screen.getByText('State C')).toBeInTheDocument();
  });

  it('marks current position', () => {
    render(<PolynomialDiagram visualization={mockVisualization} />);
    // State A should be marked as current
    const stateAButton = screen.getByText('🅰️').closest('button');
    expect(stateAButton).toHaveClass('ring-2');
  });

  it('calls onTransition when valid position clicked', async () => {
    const onTransition = vi.fn();
    render(
      <PolynomialDiagram
        visualization={mockVisualization}
        onTransition={onTransition}
      />
    );

    // Click on State B (valid from A)
    fireEvent.click(screen.getByText('🅱️'));
    expect(onTransition).toHaveBeenCalledWith('B');
  });

  it('does not call onTransition for invalid transition', () => {
    const onTransition = vi.fn();
    render(
      <PolynomialDiagram
        visualization={mockVisualization}
        onTransition={onTransition}
      />
    );

    // Click on State C (not valid from A)
    fireEvent.click(screen.getByText('©️'));
    expect(onTransition).not.toHaveBeenCalled();
  });

  it('renders with compact mode', () => {
    render(
      <PolynomialDiagram
        visualization={mockVisualization}
        compact={true}
      />
    );
    // Compact mode should have smaller dimensions
    const container = screen.getByText('State A').closest('div[class*="relative"]');
    expect(container).toBeInTheDocument();
  });

  it('shows history when enabled', () => {
    const vizWithHistory: PolynomialVisualization = {
      ...mockVisualization,
      history: [
        { from_position: 'B', to_position: 'A', timestamp: '2024-01-01T00:00:00Z' },
      ],
    };

    render(
      <PolynomialDiagram
        visualization={vizWithHistory}
        showHistory={true}
      />
    );

    // History should be visible
    expect(screen.getByText(/B.*->.*A/)).toBeInTheDocument();
  });
});

// =============================================================================
// usePolynomialState Tests
// =============================================================================

describe('usePolynomialState', () => {
  it('initializes with provided visualization', () => {
    const { result } = renderHook(() =>
      usePolynomialState({ initial: mockVisualization })
    );

    expect(result.current.visualization).toEqual(mockVisualization);
    expect(result.current.currentPosition?.id).toBe('A');
  });

  it('isReachable returns true for valid directions', () => {
    const { result } = renderHook(() =>
      usePolynomialState({ initial: mockVisualization })
    );

    expect(result.current.isReachable('B')).toBe(true);
    expect(result.current.isReachable('C')).toBe(false);
  });

  it('transition updates current position', async () => {
    const { result } = renderHook(() =>
      usePolynomialState({ initial: mockVisualization })
    );

    await act(async () => {
      const success = await result.current.transition('B');
      expect(success).toBe(true);
    });

    expect(result.current.visualization.current).toBe('B');
    expect(result.current.currentPosition?.id).toBe('B');
  });

  it('transition fails for invalid direction', async () => {
    const { result } = renderHook(() =>
      usePolynomialState({ initial: mockVisualization })
    );

    await act(async () => {
      const success = await result.current.transition('C');
      expect(success).toBe(false);
    });

    expect(result.current.visualization.current).toBe('A'); // Unchanged
    expect(result.current.transitionError).toBeTruthy();
  });

  it('transition calls onTransitionRequest when provided', async () => {
    const onTransitionRequest = vi.fn().mockResolvedValue(true);

    const { result } = renderHook(() =>
      usePolynomialState({
        initial: mockVisualization,
        onTransitionRequest,
      })
    );

    await act(async () => {
      await result.current.transition('B');
    });

    expect(onTransitionRequest).toHaveBeenCalledWith('A', 'B');
  });

  it('transition fails when onTransitionRequest returns false', async () => {
    const onTransitionRequest = vi.fn().mockResolvedValue(false);

    const { result } = renderHook(() =>
      usePolynomialState({
        initial: mockVisualization,
        onTransitionRequest,
      })
    );

    await act(async () => {
      const success = await result.current.transition('B');
      expect(success).toBe(false);
    });

    expect(result.current.visualization.current).toBe('A'); // Unchanged
  });

  it('transition adds history entry', async () => {
    const { result } = renderHook(() =>
      usePolynomialState({ initial: mockVisualization })
    );

    await act(async () => {
      await result.current.transition('B');
    });

    expect(result.current.visualization.history).toHaveLength(1);
    expect(result.current.visualization.history[0]).toMatchObject({
      from_position: 'A',
      to_position: 'B',
    });
  });

  it('reset changes position without validation', () => {
    const { result } = renderHook(() =>
      usePolynomialState({ initial: mockVisualization })
    );

    act(() => {
      result.current.reset('C');
    });

    expect(result.current.visualization.current).toBe('C');
  });

  it('getPosition returns correct position', () => {
    const { result } = renderHook(() =>
      usePolynomialState({ initial: mockVisualization })
    );

    const position = result.current.getPosition('B');
    expect(position?.label).toBe('State B');
  });
});

// =============================================================================
// Visualization Factory Tests
// =============================================================================

describe('createGardenerVisualization', () => {
  it('creates visualization with correct positions', () => {
    const viz = createGardenerVisualization(mockGardenerSession);

    expect(viz.positions).toHaveLength(3);
    expect(viz.positions.map((p) => p.id)).toEqual(['SENSE', 'ACT', 'REFLECT']);
  });

  it('marks current phase correctly', () => {
    const viz = createGardenerVisualization(mockGardenerSession);

    const current = viz.positions.find((p) => p.is_current);
    expect(current?.id).toBe('SENSE');
  });

  it('calculates valid directions correctly', () => {
    const viz = createGardenerVisualization(mockGardenerSession);

    // From SENSE, can advance to ACT
    expect(viz.valid_directions).toContain('ACT');
  });

  it('includes session metadata', () => {
    const viz = createGardenerVisualization(mockGardenerSession);

    expect(viz.metadata.session_id).toBe('test-123');
    expect(viz.metadata.plan_path).toBe('plans/test.md');
  });
});

describe('createNPhaseVisualization', () => {
  it('creates visualization with all 11 phases', () => {
    const viz = createNPhaseVisualization('RESEARCH', 'Test Plan');

    expect(viz.positions).toHaveLength(11);
    expect(viz.positions[0].id).toBe('PLAN');
    expect(viz.positions[10].id).toBe('REFLECT');
  });

  it('marks REFLECT as terminal', () => {
    const viz = createNPhaseVisualization('PLAN', 'Test');

    const reflect = viz.positions.find((p) => p.id === 'REFLECT');
    expect(reflect?.is_terminal).toBe(true);
  });

  it('allows forward and backward transitions', () => {
    const viz = createNPhaseVisualization('DEVELOP', 'Test');

    // Should be able to go forward to STRATEGIZE and backward to RESEARCH
    expect(viz.valid_directions).toContain('STRATEGIZE');
    expect(viz.valid_directions).toContain('RESEARCH');
  });
});

describe('createCitizenVisualization', () => {
  it('creates visualization with 5 phases', () => {
    const viz = createCitizenVisualization('Bob', 'IDLE');

    expect(viz.positions).toHaveLength(5);
  });

  it('RESTING phase only allows wake', () => {
    const viz = createCitizenVisualization('Bob', 'RESTING');

    // From RESTING, only IDLE (wake) is valid
    expect(viz.valid_directions).toEqual(['IDLE']);
  });

  it('includes Right to Rest metadata', () => {
    const restingViz = createCitizenVisualization('Bob', 'RESTING');
    const idleViz = createCitizenVisualization('Bob', 'IDLE');

    expect(restingViz.metadata.is_resting).toBe(true);
    expect(idleViz.metadata.is_resting).toBe(false);
  });
});

describe('createGenericVisualization', () => {
  it('creates visualization from config', () => {
    const config = {
      name: 'Custom FSM',
      positions: [
        { id: 'start', label: 'Start' },
        { id: 'end', label: 'End', is_terminal: true },
      ],
      edges: [{ source: 'start', target: 'end', label: 'finish' }],
    };

    const viz = createGenericVisualization(config, 'start');

    expect(viz.name).toBe('Custom FSM');
    expect(viz.positions).toHaveLength(2);
    expect(viz.current).toBe('start');
    expect(viz.valid_directions).toContain('end');
  });
});
