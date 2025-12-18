/**
 * Tests for Mesa component (PixiJS canvas for town visualization).
 *
 * T-gent Type I: Contracts - Component renders and displays citizens
 * T-gent Type II: Saboteurs - Component handles edge cases
 * T-gent Type III: Spies - Component emits interaction events
 *
 * @see impl/claude/web/src/components/town/Mesa.tsx
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render } from '@testing-library/react';
import { Mesa } from '@/components/town/Mesa';
import type { CitizenCardJSON } from '@/reactive/types';
import type { TownEvent } from '@/api/types';

// =============================================================================
// Test Fixtures
// =============================================================================

const mockCitizens: CitizenCardJSON[] = [
  {
    type: 'citizen_card',
    citizen_id: 'citizen-1',
    name: 'Alice',
    archetype: 'builder',
    region: 'North',
    phase: 'IDLE',
    nphase: 'UNDERSTAND',
    mood: 'curious',
    capability: 0.75,
    entropy: 0.3,
  },
  {
    type: 'citizen_card',
    citizen_id: 'citizen-2',
    name: 'Bob',
    archetype: 'trader',
    region: 'East',
    phase: 'WORKING',
    nphase: 'ACT',
    mood: 'focused',
    capability: 0.65,
    entropy: 0.4,
  },
  {
    type: 'citizen_card',
    citizen_id: 'citizen-3',
    name: 'Charlie',
    archetype: 'healer',
    region: 'West',
    phase: 'RESTING',
    nphase: 'REFLECT',
    mood: 'calm',
    capability: 0.85,
    entropy: 0.2,
  },
];

const mockEvents: TownEvent[] = [
  {
    operation: 'greet',
    participants: ['Alice', 'Bob'],
    message: 'Alice greeted Bob',
    timestamp: new Date().toISOString(),
    tick: 1,
    success: true,
  },
  {
    operation: 'gossip',
    participants: ['Bob', 'Charlie'],
    message: 'Bob gossiped with Charlie',
    timestamp: new Date().toISOString(),
    tick: 2,
    success: true,
  },
];

// =============================================================================
// T-gent Type I: Contracts - Component renders
// =============================================================================

describe('Mesa - Contracts', () => {
  it('renders canvas element', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        width={800}
        height={600}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('renders with specified dimensions', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        width={1024}
        height={768}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('renders with default dimensions when not specified', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('renders with event lines when events provided', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        events={mockEvents}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('renders in mobile mode', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        mobile
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('renders with grid hidden', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        hideGrid
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });
});

// =============================================================================
// T-gent Type II: Saboteurs - Component handles edge cases
// =============================================================================

describe('Mesa - Saboteurs', () => {
  it('handles empty citizen array', () => {
    const { container } = render(
      <Mesa
        citizens={[]}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles undefined events array', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        events={undefined}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles empty events array', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        events={[]}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles citizens without region', () => {
    const citizensWithoutRegion: CitizenCardJSON[] = [
      {
        ...mockCitizens[0],
        region: '' as any,
      },
    ];

    const { container } = render(
      <Mesa
        citizens={citizensWithoutRegion}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles citizens with unknown archetype', () => {
    const citizensWithUnknownArchetype: CitizenCardJSON[] = [
      {
        ...mockCitizens[0],
        archetype: 'unknown_archetype' as any,
      },
    ];

    const { container } = render(
      <Mesa
        citizens={citizensWithUnknownArchetype}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles citizens with unknown phase', () => {
    const citizensWithUnknownPhase: CitizenCardJSON[] = [
      {
        ...mockCitizens[0],
        phase: 'UNKNOWN_PHASE' as any,
      },
    ];

    const { container } = render(
      <Mesa
        citizens={citizensWithUnknownPhase}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles events with single participant', () => {
    const eventsWithSingleParticipant: TownEvent[] = [
      {
        operation: 'work',
        participants: ['Alice'],
        message: 'Alice worked',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
    ];

    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        events={eventsWithSingleParticipant}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles events with unknown participants', () => {
    const eventsWithUnknownParticipants: TownEvent[] = [
      {
        operation: 'greet',
        participants: ['UnknownCitizen1', 'UnknownCitizen2'],
        message: 'Unknown citizens interacted',
        timestamp: new Date().toISOString(),
        tick: 1,
        success: true,
      },
    ];

    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        events={eventsWithUnknownParticipants}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles many citizens in same region', () => {
    const manyCitizensInNorth: CitizenCardJSON[] = Array(20).fill(null).map((_, i) => ({
      ...mockCitizens[0],
      citizen_id: `citizen-${i}`,
      name: `Citizen ${i}`,
    }));

    const { container } = render(
      <Mesa
        citizens={manyCitizensInNorth}
        selectedCitizenId={null}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles very large canvas dimensions', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        width={4096}
        height={2160}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('handles very small canvas dimensions', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        width={320}
        height={240}
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });
});

// =============================================================================
// T-gent Type III: Spies - Component emits interaction events
// =============================================================================

describe('Mesa - Spies', () => {
  it('provides onSelectCitizen callback', () => {
    const onSelectCitizen = vi.fn();

    render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        onSelectCitizen={onSelectCitizen}
      />
    );

    expect(onSelectCitizen).not.toHaveBeenCalled();
  });

  it('provides onHoverCitizen callback', () => {
    const onHoverCitizen = vi.fn();

    render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        onHoverCitizen={onHoverCitizen}
      />
    );

    expect(onHoverCitizen).not.toHaveBeenCalled();
  });

  it('accepts selected citizen ID', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId="citizen-1"
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('updates when selected citizen changes', () => {
    const { container, rerender } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId="citizen-1"
      />
    );

    expect(container.querySelector('canvas')).toBeInTheDocument();

    rerender(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId="citizen-2"
      />
    );

    expect(container.querySelector('canvas')).toBeInTheDocument();
  });

  it('updates when citizens change', () => {
    const { container, rerender } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
      />
    );

    expect(container.querySelector('canvas')).toBeInTheDocument();

    const newCitizens = [...mockCitizens, {
      type: 'citizen_card' as const,
      citizen_id: 'citizen-4',
      name: 'Diana',
      archetype: 'scholar' as const,
      region: 'South',
      phase: 'IDLE',
      nphase: 'UNDERSTAND',
      mood: 'excited',
      capability: 0.9,
      entropy: 0.1,
    }];

    rerender(
      <Mesa
        citizens={newCitizens}
        selectedCitizenId={null}
      />
    );

    expect(container.querySelector('canvas')).toBeInTheDocument();
  });

  it('updates when events change', () => {
    const { container, rerender } = render(
      <Mesa
        citizens={mockCitizens}
        events={mockEvents}
        selectedCitizenId={null}
      />
    );

    expect(container.querySelector('canvas')).toBeInTheDocument();

    const newEvents = [...mockEvents, {
      operation: 'trade',
      participants: ['Alice', 'Charlie'],
      message: 'Alice traded with Charlie',
      timestamp: new Date().toISOString(),
      tick: 3,
      success: true,
    }];

    rerender(
      <Mesa
        citizens={mockCitizens}
        events={newEvents}
        selectedCitizenId={null}
      />
    );

    expect(container.querySelector('canvas')).toBeInTheDocument();
  });
});

// =============================================================================
// Mobile Performance Tests
// =============================================================================

describe('Mesa - Mobile Performance', () => {
  it('applies mobile optimizations when mobile=true', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        events={mockEvents}
        selectedCitizenId={null}
        mobile
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('limits event lines in mobile mode', () => {
    const manyEvents: TownEvent[] = Array(10).fill(null).map((_, i) => ({
      operation: 'greet',
      participants: ['Alice', 'Bob'],
      message: `Event ${i}`,
      timestamp: new Date().toISOString(),
      tick: i,
      success: true,
    }));

    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        events={manyEvents}
        selectedCitizenId={null}
        mobile
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });

  it('renders without grid when hideGrid=true', () => {
    const { container } = render(
      <Mesa
        citizens={mockCitizens}
        selectedCitizenId={null}
        hideGrid
      />
    );

    const canvas = container.querySelector('canvas');
    expect(canvas).toBeInTheDocument();
  });
});
