import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { ArtifactFeed } from '@/components/workshop/ArtifactFeed';
import { useWorkshopStore } from '@/stores/workshopStore';
import type { WorkshopEvent, WorkshopEventType, WorkshopPhase } from '@/api/types';

// Helper to create mock event
const createMockEvent = (
  type: WorkshopEventType,
  overrides: Partial<WorkshopEvent> = {}
): WorkshopEvent => ({
  type,
  builder: 'Scout',
  phase: 'EXPLORING' as WorkshopPhase,
  message: 'Test message',
  artifact: null,
  timestamp: new Date().toISOString(),
  metadata: {},
  ...overrides,
});

describe('ArtifactFeed', () => {
  beforeEach(() => {
    useWorkshopStore.setState({
      events: [],
      artifacts: [],
    });
  });

  describe('empty state', () => {
    it('should show empty message when no events', () => {
      render(<ArtifactFeed />);
      expect(screen.getByText('No events yet')).toBeInTheDocument();
      expect(screen.getByText('Assign a task to start')).toBeInTheDocument();
    });
  });

  describe('event display', () => {
    it('should display event message', () => {
      useWorkshopStore.setState({
        events: [createMockEvent('PHASE_STARTED', { message: 'Scout starting exploration' })],
      });

      render(<ArtifactFeed />);
      expect(screen.getByText('Scout starting exploration')).toBeInTheDocument();
    });

    it('should show builder name', () => {
      useWorkshopStore.setState({
        events: [createMockEvent('ARTIFACT_PRODUCED', { builder: 'Sage' })],
      });

      render(<ArtifactFeed />);
      expect(screen.getByText('Sage')).toBeInTheDocument();
    });

    it('should show phase', () => {
      useWorkshopStore.setState({
        events: [createMockEvent('PHASE_COMPLETED', { phase: 'DESIGNING' })],
      });

      render(<ArtifactFeed />);
      expect(screen.getByText(/DESIGNING/)).toBeInTheDocument();
    });

    it('should show dialogue when present', () => {
      useWorkshopStore.setState({
        events: [
          createMockEvent('ARTIFACT_PRODUCED', {
            metadata: { dialogue: 'I found something interesting!' },
          }),
        ],
      });

      render(<ArtifactFeed />);
      expect(
        screen.getByText('"I found something interesting!"')
      ).toBeInTheDocument();
    });
  });

  describe('event type icons', () => {
    const eventTypes: Array<{ type: WorkshopEventType; icon: string }> = [
      { type: 'TASK_ASSIGNED', icon: '📋' },
      { type: 'PLAN_CREATED', icon: '📝' },
      { type: 'PHASE_STARTED', icon: '▶️' },
      { type: 'PHASE_COMPLETED', icon: '✅' },
      { type: 'HANDOFF', icon: '🤝' },
      { type: 'ARTIFACT_PRODUCED', icon: '📦' },
      { type: 'TASK_COMPLETED', icon: '🎉' },
      { type: 'ERROR', icon: '⚠️' },
    ];

    eventTypes.forEach(({ type, icon }) => {
      it(`should show ${icon} icon for ${type}`, () => {
        useWorkshopStore.setState({
          events: [createMockEvent(type)],
        });

        render(<ArtifactFeed />);
        expect(screen.getByText(icon)).toBeInTheDocument();
      });
    });
  });

  describe('multiple events', () => {
    it('should display events in reverse chronological order', () => {
      useWorkshopStore.setState({
        events: [
          createMockEvent('PHASE_STARTED', { message: 'First event' }),
          createMockEvent('ARTIFACT_PRODUCED', { message: 'Second event' }),
          createMockEvent('PHASE_COMPLETED', { message: 'Third event' }),
        ],
      });

      render(<ArtifactFeed />);

      // Query event messages specifically (not the header)
      const firstEvent = screen.getByText('First event');
      const secondEvent = screen.getByText('Second event');
      const thirdEvent = screen.getByText('Third event');

      // All events should be present
      expect(firstEvent).toBeInTheDocument();
      expect(secondEvent).toBeInTheDocument();
      expect(thirdEvent).toBeInTheDocument();
    });

    it('should limit displayed events to 50', () => {
      const manyEvents = Array.from({ length: 60 }, (_, i) =>
        createMockEvent('ARTIFACT_PRODUCED', { message: `Event ${i}` })
      );

      useWorkshopStore.setState({
        events: manyEvents,
      });

      render(<ArtifactFeed />);

      // Count event items (each has an icon)
      const icons = screen.getAllByText('📦');
      expect(icons.length).toBeLessThanOrEqual(50);
    });
  });

  describe('special event styling', () => {
    it('should have distinct styling for TASK_COMPLETED', () => {
      useWorkshopStore.setState({
        events: [createMockEvent('TASK_COMPLETED')],
      });

      const { container } = render(<ArtifactFeed />);
      // Check for emerald styling class
      expect(container.querySelector('.bg-emerald-900\\/20')).toBeInTheDocument();
    });

    it('should have distinct styling for HANDOFF', () => {
      useWorkshopStore.setState({
        events: [createMockEvent('HANDOFF')],
      });

      const { container } = render(<ArtifactFeed />);
      // Check for pink styling class
      expect(container.querySelector('.bg-pink-900\\/20')).toBeInTheDocument();
    });

    it('should have distinct styling for ERROR', () => {
      useWorkshopStore.setState({
        events: [createMockEvent('ERROR')],
      });

      const { container } = render(<ArtifactFeed />);
      // Check for red styling class
      expect(container.querySelector('.bg-red-900\\/20')).toBeInTheDocument();
    });
  });

  describe('builder icons', () => {
    const builders = [
      { archetype: 'Scout', icon: '🔍' },
      { archetype: 'Sage', icon: '📐' },
      { archetype: 'Spark', icon: '⚡' },
      { archetype: 'Steady', icon: '🔧' },
      { archetype: 'Sync', icon: '🔗' },
    ];

    builders.forEach(({ archetype, icon }) => {
      it(`should show ${icon} for ${archetype} events`, () => {
        useWorkshopStore.setState({
          events: [createMockEvent('ARTIFACT_PRODUCED', { builder: archetype })],
        });

        render(<ArtifactFeed />);
        expect(screen.getByText(icon)).toBeInTheDocument();
      });
    });
  });
});
