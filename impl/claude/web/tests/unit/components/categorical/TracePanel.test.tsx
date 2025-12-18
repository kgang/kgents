/**
 * Tests for TracePanel component.
 *
 * Following T-gent Types taxonomy:
 * - Type I (Contracts): Preconditions, postconditions, rendering contracts
 * - Type II (Saboteurs): Edge cases, invalid inputs, boundary conditions
 * - Type III (Spies): Callback verification, event handling
 *
 * @see impl/claude/web/src/components/categorical/TracePanel.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  TracePanel,
  createPhaseTransitionEvent,
  createTimerEvent,
  createForceEvent,
  createMaskEvent,
  resetEventCounter,
} from '@/components/categorical/TracePanel';
import type { TraceEvent } from '@/components/categorical/TracePanel';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockEvent: TraceEvent = {
  id: 1,
  timestamp: new Date('2024-12-18T10:00:00Z'),
  type: 'phase_transition',
  title: 'Phase: IDLE -> WORKING',
  from: 'IDLE',
  to: 'WORKING',
};

const mockTimerEvent: TraceEvent = {
  id: 2,
  timestamp: new Date('2024-12-18T10:05:00Z'),
  type: 'timer',
  title: 'Timer: compliance WARNING',
  description: 'Remaining: 30s',
};

const mockForceEvent: TraceEvent = {
  id: 3,
  timestamp: new Date('2024-12-18T10:10:00Z'),
  type: 'force',
  title: 'Force used (2/5)',
  description: 'Emergency injection',
};

// =============================================================================
// Type I Tests: Contracts - Basic Rendering
// =============================================================================

describe('TracePanel - Contracts', () => {
  it('renders trace panel header', () => {
    render(<TracePanel events={[mockEvent]} />);
    expect(screen.getByText('Trace History')).toBeInTheDocument();
  });

  it('renders custom title', () => {
    render(<TracePanel events={[mockEvent]} title="Custom Trace" />);
    expect(screen.getByText('Custom Trace')).toBeInTheDocument();
  });

  it('displays event count', () => {
    const events = [mockEvent, mockTimerEvent, mockForceEvent];
    render(<TracePanel events={events} />);
    expect(screen.getByText('3 events')).toBeInTheDocument();
  });

  it('displays singular event text for single event', () => {
    render(<TracePanel events={[mockEvent]} />);
    expect(screen.getByText('1 event')).toBeInTheDocument();
  });

  it('shows empty state when no events', () => {
    render(<TracePanel events={[]} />);
    expect(screen.getByText('No events recorded yet')).toBeInTheDocument();
  });

  it('renders event title', () => {
    render(<TracePanel events={[mockEvent]} />);
    expect(screen.getByText('Phase: IDLE -> WORKING')).toBeInTheDocument();
  });

  it('renders event ID badge', () => {
    render(<TracePanel events={[mockEvent]} />);
    expect(screen.getByText('[1]')).toBeInTheDocument();
  });

  it('renders from/to transition', () => {
    render(<TracePanel events={[mockEvent]} />);
    expect(screen.getByText('IDLE')).toBeInTheDocument();
    expect(screen.getByText('WORKING')).toBeInTheDocument();
  });

  it('renders event description when not compact', () => {
    render(<TracePanel events={[mockTimerEvent]} compact={false} />);
    expect(screen.getByText('Remaining: 30s')).toBeInTheDocument();
  });

  it('hides event description in compact mode', () => {
    render(<TracePanel events={[mockTimerEvent]} compact={true} />);
    expect(screen.queryByText('Remaining: 30s')).not.toBeInTheDocument();
  });
});

// =============================================================================
// Type I Tests: Event Limiting
// =============================================================================

describe('TracePanel - Event Limiting', () => {
  it('respects maxEvents limit', () => {
    const events = Array.from({ length: 20 }, (_, i) => ({
      ...mockEvent,
      id: i + 1,
      title: `Event ${i + 1}`,
    }));

    render(<TracePanel events={events} maxEvents={5} />);

    // Should only show 5 most recent events
    expect(screen.getByText('Event 20')).toBeInTheDocument();
    expect(screen.getByText('Event 16')).toBeInTheDocument();
    expect(screen.queryByText('Event 15')).not.toBeInTheDocument();
  });

  it('shows "Show more" indicator when events exceed max', () => {
    const events = Array.from({ length: 15 }, (_, i) => ({
      ...mockEvent,
      id: i + 1,
    }));

    render(<TracePanel events={events} maxEvents={10} />);
    expect(screen.getByText(/Showing latest 10 of 15/)).toBeInTheDocument();
  });

  it('does not show "Show more" when events under max', () => {
    const events = Array.from({ length: 5 }, (_, i) => ({
      ...mockEvent,
      id: i + 1,
    }));

    render(<TracePanel events={events} maxEvents={10} />);
    expect(screen.queryByText(/Showing latest/)).not.toBeInTheDocument();
  });

  it('defaults to 10 max events', () => {
    const events = Array.from({ length: 20 }, (_, i) => ({
      ...mockEvent,
      id: i + 1,
      title: `Event ${i + 1}`,
    }));

    render(<TracePanel events={events} />);

    // Should show 10 events by default
    expect(screen.getByText('Event 20')).toBeInTheDocument();
    expect(screen.getByText('Event 11')).toBeInTheDocument();
    expect(screen.queryByText('Event 10')).not.toBeInTheDocument();
  });
});

// =============================================================================
// Type I Tests: Event Colors
// =============================================================================

describe('TracePanel - Event Colors', () => {
  it('uses purple for phase_transition events', () => {
    const { container } = render(<TracePanel events={[mockEvent]} />);
    const dot = container.querySelector('[style*="background-color"]');
    expect(dot).toHaveStyle({ backgroundColor: '#8b5cf6' });
  });

  it('uses amber for timer events', () => {
    const { container } = render(<TracePanel events={[mockTimerEvent]} />);
    const dot = container.querySelector('[style*="background-color"]');
    expect(dot).toHaveStyle({ backgroundColor: '#f59e0b' });
  });

  it('uses red for force events', () => {
    const { container } = render(<TracePanel events={[mockForceEvent]} />);
    const dot = container.querySelector('[style*="background-color"]');
    expect(dot).toHaveStyle({ backgroundColor: '#ef4444' });
  });

  it('respects custom color override', () => {
    const customEvent = { ...mockEvent, color: '#00ff00' };
    const { container } = render(<TracePanel events={[customEvent]} />);
    const dot = container.querySelector('[style*="background-color"]');
    expect(dot).toHaveStyle({ backgroundColor: '#00ff00' });
  });
});

// =============================================================================
// Type I Tests: Timeline Scrubber
// =============================================================================

describe('TracePanel - Timeline Scrubber', () => {
  it('does not show scrubber by default', () => {
    render(<TracePanel events={[mockEvent]} />);
    expect(screen.queryByRole('slider')).not.toBeInTheDocument();
  });

  it('shows scrubber when showScrubber=true and onPlaybackToggle provided', () => {
    const onPlaybackToggle = vi.fn();
    render(
      <TracePanel
        events={[mockEvent]}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
      />
    );
    expect(screen.getByRole('slider')).toBeInTheDocument();
  });

  it('does not show scrubber without onPlaybackToggle', () => {
    render(<TracePanel events={[mockEvent]} showScrubber={true} />);
    expect(screen.queryByRole('slider')).not.toBeInTheDocument();
  });

  it('displays Play button when not playing', () => {
    const onPlaybackToggle = vi.fn();
    render(
      <TracePanel
        events={[mockEvent]}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
        isPlaying={false}
      />
    );
    expect(screen.getByLabelText('Play')).toBeInTheDocument();
  });

  it('displays Pause button when playing', () => {
    const onPlaybackToggle = vi.fn();
    render(
      <TracePanel
        events={[mockEvent]}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
        isPlaying={true}
      />
    );
    expect(screen.getByLabelText('Pause')).toBeInTheDocument();
  });

  it('displays position indicator', () => {
    const onPlaybackToggle = vi.fn();
    const events = Array.from({ length: 10 }, (_, i) => ({
      ...mockEvent,
      id: i + 1,
    }));

    render(
      <TracePanel
        events={events}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
        playbackPosition={0.5}
      />
    );

    expect(screen.getByText(/\d+\/10/)).toBeInTheDocument();
  });
});

// =============================================================================
// Type III Tests: Spies - Event Handling
// =============================================================================

describe('TracePanel - Spies', () => {
  it('calls onPlaybackToggle when play button clicked', () => {
    const onPlaybackToggle = vi.fn();
    render(
      <TracePanel
        events={[mockEvent]}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
      />
    );

    fireEvent.click(screen.getByLabelText('Play'));
    expect(onPlaybackToggle).toHaveBeenCalledTimes(1);
  });

  it('calls onPlaybackChange when scrubber moved', () => {
    const onPlaybackChange = vi.fn();
    const onPlaybackToggle = vi.fn();
    render(
      <TracePanel
        events={[mockEvent]}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
        onPlaybackChange={onPlaybackChange}
      />
    );

    const slider = screen.getByRole('slider');
    fireEvent.change(slider, { target: { value: '0.75' } });

    expect(onPlaybackChange).toHaveBeenCalledWith(0.75);
  });

  it('calls onPlaybackChange with 0 when skip back clicked', () => {
    const onPlaybackChange = vi.fn();
    const onPlaybackToggle = vi.fn();
    render(
      <TracePanel
        events={[mockEvent]}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
        onPlaybackChange={onPlaybackChange}
      />
    );

    fireEvent.click(screen.getByLabelText('Go to start'));
    expect(onPlaybackChange).toHaveBeenCalledWith(0);
  });

  it('calls onPlaybackChange with 1 when skip forward clicked', () => {
    const onPlaybackChange = vi.fn();
    const onPlaybackToggle = vi.fn();
    render(
      <TracePanel
        events={[mockEvent]}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
        onPlaybackChange={onPlaybackChange}
      />
    );

    fireEvent.click(screen.getByLabelText('Go to end'));
    expect(onPlaybackChange).toHaveBeenCalledWith(1);
  });
});

// =============================================================================
// Type II Tests: Saboteurs - Edge Cases
// =============================================================================

describe('TracePanel - Saboteurs', () => {
  it('handles timestamp as Date object', () => {
    const event = { ...mockEvent, timestamp: new Date('2024-12-18T15:30:45Z') };
    render(<TracePanel events={[event]} />);
    // Just verify it renders without error
    expect(screen.getByText(/\d+:\d+:\d+/)).toBeInTheDocument();
  });

  it('handles timestamp as string', () => {
    const event = { ...mockEvent, timestamp: '2024-12-18T15:30:45Z' };
    render(<TracePanel events={[event]} />);
    expect(screen.getByText(/\d+:\d+:\d+/)).toBeInTheDocument();
  });

  it('handles event without from/to fields', () => {
    const event = { ...mockEvent, from: undefined, to: undefined };
    render(<TracePanel events={[event]} />);
    expect(screen.getByText(mockEvent.title)).toBeInTheDocument();
  });

  it('handles event without description', () => {
    const event = { ...mockEvent, description: undefined };
    render(<TracePanel events={[event]} />);
    expect(screen.getByText(mockEvent.title)).toBeInTheDocument();
  });

  it('handles event without color', () => {
    const event = { ...mockEvent, color: undefined };
    const { container } = render(<TracePanel events={[event]} />);
    const dot = container.querySelector('[style*="background-color"]');
    expect(dot).toBeInTheDocument();
  });

  it('handles very long event titles', () => {
    const event = {
      ...mockEvent,
      title: 'Very Long Event Title That Might Overflow The Container Width',
    };
    render(<TracePanel events={[event]} />);
    expect(screen.getByText(event.title)).toBeInTheDocument();
  });

  it('handles playback position at 0', () => {
    const onPlaybackToggle = vi.fn();
    const events = Array.from({ length: 10 }, (_, i) => ({
      ...mockEvent,
      id: i + 1,
    }));

    render(
      <TracePanel
        events={events}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
        playbackPosition={0}
      />
    );

    expect(screen.getByText(/\d+\/10/)).toBeInTheDocument();
  });

  it('handles playback position at 1', () => {
    const onPlaybackToggle = vi.fn();
    const events = Array.from({ length: 10 }, (_, i) => ({
      ...mockEvent,
      id: i + 1,
    }));

    render(
      <TracePanel
        events={events}
        showScrubber={true}
        onPlaybackToggle={onPlaybackToggle}
        playbackPosition={1}
      />
    );

    expect(screen.getByText('10/10')).toBeInTheDocument();
  });

  it('highlights most recent event', () => {
    const events = [
      { ...mockEvent, id: 1 },
      { ...mockEvent, id: 2 },
    ];
    const { container } = render(<TracePanel events={events} />);
    const highlighted = container.querySelector('.bg-slate-700\\/50');
    expect(highlighted).toBeInTheDocument();
  });
});

// =============================================================================
// Factory Helper Tests
// =============================================================================

describe('Factory Helpers', () => {
  beforeEach(() => {
    resetEventCounter();
  });

  it('createPhaseTransitionEvent generates correct event', () => {
    const event = createPhaseTransitionEvent('IDLE', 'WORKING', { agent: 'test' });

    expect(event.type).toBe('phase_transition');
    expect(event.from).toBe('IDLE');
    expect(event.to).toBe('WORKING');
    expect(event.title).toBe('Phase: IDLE -> WORKING');
    expect(event.data).toEqual({ agent: 'test' });
    expect(event.id).toBe(1);
  });

  it('createTimerEvent generates correct event', () => {
    const event = createTimerEvent('compliance', 'WARNING', '30s');

    expect(event.type).toBe('timer');
    expect(event.title).toBe('Timer: compliance WARNING');
    expect(event.description).toBe('Remaining: 30s');
    expect(event.data).toEqual({
      timerName: 'compliance',
      state: 'WARNING',
      remaining: '30s',
    });
  });

  it('createTimerEvent handles missing remaining', () => {
    const event = createTimerEvent('test', 'ACTIVE');

    expect(event.description).toBeUndefined();
  });

  it('createForceEvent generates correct event', () => {
    const event = createForceEvent(2, 5, 'Emergency');

    expect(event.type).toBe('force');
    expect(event.title).toBe('Force used (2/5)');
    expect(event.description).toBe('Emergency');
    expect(event.data).toEqual({
      forcesUsed: 2,
      forcesTotal: 5,
      reason: 'Emergency',
    });
  });

  it('createMaskEvent generates don event', () => {
    const event = createMaskEvent('director', 'don', ['inject', 'observe']);

    expect(event.type).toBe('mask');
    expect(event.title).toBe('Mask donned: director');
    expect(event.description).toBe('Affordances: inject, observe');
    expect(event.data).toEqual({
      maskName: 'director',
      action: 'don',
      affordances: ['inject', 'observe'],
    });
  });

  it('createMaskEvent generates doff event', () => {
    const event = createMaskEvent('guest', 'doff');

    expect(event.type).toBe('mask');
    expect(event.title).toBe('Mask doffed: guest');
  });

  it('factory helpers increment event counter', () => {
    const event1 = createPhaseTransitionEvent('A', 'B');
    const event2 = createTimerEvent('test', 'ACTIVE');
    const event3 = createForceEvent(1, 5);

    expect(event1.id).toBe(1);
    expect(event2.id).toBe(2);
    expect(event3.id).toBe(3);
  });

  it('resetEventCounter resets to 0', () => {
    createPhaseTransitionEvent('A', 'B');
    createPhaseTransitionEvent('C', 'D');

    resetEventCounter();

    const event = createPhaseTransitionEvent('E', 'F');
    expect(event.id).toBe(1);
  });
});

// =============================================================================
// Type I Tests: Compact Mode
// =============================================================================

describe('TracePanel - Compact Mode', () => {
  it('applies compact padding', () => {
    const { container } = render(<TracePanel events={[mockEvent]} compact={true} />);
    const panel = container.querySelector('.p-3');
    expect(panel).toBeInTheDocument();
  });

  it('applies normal padding by default', () => {
    const { container } = render(<TracePanel events={[mockEvent]} compact={false} />);
    const panel = container.querySelector('.p-4');
    expect(panel).toBeInTheDocument();
  });

  it('limits height in compact mode', () => {
    const { container } = render(<TracePanel events={[mockEvent]} compact={true} />);
    const list = container.querySelector('.max-h-48');
    expect(list).toBeInTheDocument();
  });
});
