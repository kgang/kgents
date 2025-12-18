/**
 * Tests for TownTracePanel component.
 *
 * T-gent Type I: Contracts - Component renders expected content
 * T-gent Type II: Saboteurs - Component handles bad data
 * T-gent Type III: Spies - Component behavior
 *
 * @see impl/claude/web/src/components/town/TownTracePanel.tsx
 */

import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TownTracePanel } from '@/components/town/TownTracePanel';
import type { TownEvent } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockEvents: TownEvent[] = [
  {
    operation: 'greet',
    participants: ['Alice', 'Bob'],
    message: 'Alice greeted Bob',
    timestamp: new Date('2024-12-18T10:00:00Z').toISOString(),
    tick: 1,
    success: true,
  },
  {
    operation: 'gossip',
    participants: ['Bob', 'Charlie'],
    message: 'Bob gossiped with Charlie',
    timestamp: new Date('2024-12-18T10:01:00Z').toISOString(),
    tick: 2,
    success: true,
  },
  {
    operation: 'work',
    participants: ['Alice'],
    message: 'Alice worked on a task',
    timestamp: new Date('2024-12-18T10:02:00Z').toISOString(),
    tick: 3,
    success: true,
  },
  {
    operation: 'reflect',
    participants: ['Charlie'],
    message: 'Charlie reflected',
    timestamp: new Date('2024-12-18T10:03:00Z').toISOString(),
    tick: 4,
    success: true,
  },
  {
    operation: 'evolve',
    participants: ['Alice'],
    message: 'Alice evolved',
    timestamp: new Date('2024-12-18T10:04:00Z').toISOString(),
    tick: 5,
    success: true,
  },
];

// =============================================================================
// T-gent Type I: Contracts - Component renders expected content
// =============================================================================

describe('TownTracePanel - Contracts', () => {
  it('renders panel title', () => {
    render(<TownTracePanel events={mockEvents} />);

    expect(screen.getByText('Town Witness')).toBeInTheDocument();
  });

  it('renders event list', () => {
    render(<TownTracePanel events={mockEvents} />);

    expect(screen.getByText('Alice greeted Bob')).toBeInTheDocument();
    expect(screen.getByText('Bob gossiped with Charlie')).toBeInTheDocument();
    expect(screen.getByText('Alice worked on a task')).toBeInTheDocument();
  });

  it('shows teaching callout by default', () => {
    render(<TownTracePanel events={mockEvents} />);

    // Teaching message should be visible
    const teachingElements = screen.queryAllByText(/witness/i);
    expect(teachingElements.length).toBeGreaterThan(1); // Title + teaching content
  });

  it('hides teaching callout when showTeaching is false', () => {
    render(<TownTracePanel events={mockEvents} showTeaching={false} />);

    const teachingElements = screen.queryAllByText(/witness/i);
    // Only the title should be present, not teaching content
    expect(teachingElements.length).toBe(1);
  });

  it('limits displayed events to maxEvents', () => {
    render(<TownTracePanel events={mockEvents} maxEvents={2} />);

    // Should only show first 2 events
    expect(screen.getByText('Alice greeted Bob')).toBeInTheDocument();
    expect(screen.getByText('Bob gossiped with Charlie')).toBeInTheDocument();

    // Should not show events beyond limit
    expect(screen.queryByText('Alice worked on a task')).not.toBeInTheDocument();
  });

  it('renders in compact mode', () => {
    render(<TownTracePanel events={mockEvents} compact />);

    expect(screen.getByText('Town Witness')).toBeInTheDocument();
  });
});

// =============================================================================
// T-gent Type II: Saboteurs - Component handles bad data
// =============================================================================

describe('TownTracePanel - Saboteurs', () => {
  it('handles empty event list', () => {
    render(<TownTracePanel events={[]} />);

    expect(screen.getByText('Town Witness')).toBeInTheDocument();
  });

  it('handles events without timestamps', () => {
    const eventsWithoutTimestamp: TownEvent[] = [
      {
        operation: 'greet',
        participants: ['Alice', 'Bob'],
        message: 'Alice greeted Bob',
        timestamp: undefined as any,
        tick: 1,
        success: true,
      },
    ];

    render(<TownTracePanel events={eventsWithoutTimestamp} />);

    expect(screen.getByText('Town Witness')).toBeInTheDocument();
  });

  it('handles events without participants', () => {
    const eventsWithoutParticipants: TownEvent[] = [
      {
        operation: 'system',
        participants: [],
        message: 'System event',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
    ];

    render(<TownTracePanel events={eventsWithoutParticipants} />);

    expect(screen.getByText('System event')).toBeInTheDocument();
  });

  it('handles events without message', () => {
    const eventsWithoutMessage: TownEvent[] = [
      {
        operation: 'greet',
        participants: ['Alice', 'Bob'],
        message: undefined as any,
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
    ];

    render(<TownTracePanel events={eventsWithoutMessage} />);

    expect(screen.getByText('Town Witness')).toBeInTheDocument();
  });

  it('handles unknown operation types', () => {
    const eventsWithUnknownOperation: TownEvent[] = [
      {
        operation: 'unknown_operation',
        participants: ['Alice'],
        message: 'Unknown operation occurred',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
    ];

    render(<TownTracePanel events={eventsWithUnknownOperation} />);

    expect(screen.getByText('Unknown operation occurred')).toBeInTheDocument();
  });

  it('handles maxEvents of 0', () => {
    render(<TownTracePanel events={mockEvents} maxEvents={0} />);

    expect(screen.getByText('Town Witness')).toBeInTheDocument();
  });
});

// =============================================================================
// Event Type Categorization Tests
// =============================================================================

describe('TownTracePanel - Event Types', () => {
  it('categorizes social operations correctly', () => {
    const socialEvents: TownEvent[] = [
      {
        operation: 'greet',
        participants: ['Alice', 'Bob'],
        message: 'Greeting',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
      {
        operation: 'gossip',
        participants: ['Bob', 'Charlie'],
        message: 'Gossiping',
        timestamp: new Date().toISOString(),
        tick: 2,
        success: true,
      },
      {
        operation: 'trade',
        participants: ['Alice', 'Diana'],
        message: 'Trading',
        timestamp: new Date().toISOString(),
        tick: 3,
        success: true,
      },
    ];

    render(<TownTracePanel events={socialEvents} />);

    expect(screen.getByText('Greeting')).toBeInTheDocument();
    expect(screen.getByText('Gossiping')).toBeInTheDocument();
    expect(screen.getByText('Trading')).toBeInTheDocument();
  });

  it('categorizes work operations correctly', () => {
    const workEvents: TownEvent[] = [
      {
        operation: 'work',
        participants: ['Alice'],
        message: 'Working',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
      {
        operation: 'craft',
        participants: ['Bob'],
        message: 'Crafting',
        timestamp: new Date().toISOString(),
        tick: 2,
        success: true,
      },
      {
        operation: 'build',
        participants: ['Charlie'],
        message: 'Building',
        timestamp: new Date().toISOString(),
        tick: 3,
        success: true,
      },
    ];

    render(<TownTracePanel events={workEvents} />);

    expect(screen.getByText('Working')).toBeInTheDocument();
    expect(screen.getByText('Crafting')).toBeInTheDocument();
    expect(screen.getByText('Building')).toBeInTheDocument();
  });

  it('categorizes reflection operations correctly', () => {
    const reflectionEvents: TownEvent[] = [
      {
        operation: 'reflect',
        participants: ['Alice'],
        message: 'Reflecting',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
      {
        operation: 'journal',
        participants: ['Bob'],
        message: 'Journaling',
        timestamp: new Date().toISOString(),
        tick: 2,
        success: true,
      },
      {
        operation: 'meditate',
        participants: ['Charlie'],
        message: 'Meditating',
        timestamp: new Date().toISOString(),
        tick: 3,
        success: true,
      },
    ];

    render(<TownTracePanel events={reflectionEvents} />);

    expect(screen.getByText('Reflecting')).toBeInTheDocument();
    expect(screen.getByText('Journaling')).toBeInTheDocument();
    expect(screen.getByText('Meditating')).toBeInTheDocument();
  });

  it('categorizes rest operations correctly', () => {
    const restEvents: TownEvent[] = [
      {
        operation: 'rest',
        participants: ['Alice'],
        message: 'Resting',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
      {
        operation: 'wake',
        participants: ['Bob'],
        message: 'Waking',
        timestamp: new Date().toISOString(),
        tick: 2,
        success: true,
      },
    ];

    render(<TownTracePanel events={restEvents} />);

    expect(screen.getByText('Resting')).toBeInTheDocument();
    expect(screen.getByText('Waking')).toBeInTheDocument();
  });

  it('categorizes phase transitions correctly', () => {
    const phaseTransitionEvents: TownEvent[] = [
      {
        operation: 'evolve',
        participants: ['Alice'],
        message: 'Alice evolved',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
      {
        operation: 'transform',
        participants: ['Bob'],
        message: 'Bob transformed',
        timestamp: new Date().toISOString(),
        tick: 2,
        success: true,
      },
    ];

    render(<TownTracePanel events={phaseTransitionEvents} />);

    expect(screen.getByText('Alice evolved')).toBeInTheDocument();
    expect(screen.getByText('Bob transformed')).toBeInTheDocument();
  });
});
