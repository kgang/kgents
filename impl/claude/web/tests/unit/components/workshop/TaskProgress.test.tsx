import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { TaskProgress } from '@/components/workshop/TaskProgress';
import { useWorkshopStore } from '@/stores/workshopStore';
import type { WorkshopTask, WorkshopMetrics, WorkshopPhase } from '@/api/types';

// Helper to create mock task
const createMockTask = (overrides: Partial<WorkshopTask> = {}): WorkshopTask => ({
  id: 'task-1',
  description: 'Build a feature',
  priority: 2,
  created_at: new Date().toISOString(),
  ...overrides,
});

// Helper to create mock metrics
const createMockMetrics = (
  overrides: Partial<WorkshopMetrics> = {}
): WorkshopMetrics => ({
  total_steps: 0,
  total_events: 0,
  total_tokens: 0,
  dialogue_tokens: 0,
  artifacts_produced: 0,
  phases_completed: 0,
  handoffs: 0,
  perturbations: 0,
  duration_seconds: 0,
  ...overrides,
});

describe('TaskProgress', () => {
  beforeEach(() => {
    useWorkshopStore.setState({
      activeTask: null,
      currentPhase: 'IDLE',
      metrics: createMockMetrics(),
    });
  });

  describe('task display', () => {
    it('should show task description when active', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask({ description: 'Design the API' }),
        currentPhase: 'DESIGNING',
      });

      render(<TaskProgress />);
      expect(screen.getByText('Design the API')).toBeInTheDocument();
    });

    it('should show task priority', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask({ priority: 3 }),
        currentPhase: 'EXPLORING',
      });

      render(<TaskProgress />);
      expect(screen.getByText('(Priority 3)')).toBeInTheDocument();
    });
  });

  describe('phase nodes', () => {
    const phases: WorkshopPhase[] = [
      'EXPLORING',
      'DESIGNING',
      'PROTOTYPING',
      'REFINING',
      'INTEGRATING',
    ];

    phases.forEach((phase) => {
      it(`should highlight ${phase} when current`, () => {
        useWorkshopStore.setState({
          activeTask: createMockTask(),
          currentPhase: phase,
        });

        render(<TaskProgress />);
        // The component renders icons for each phase
        // Check that the phase is represented
        expect(document.body.textContent).toContain(getPhaseIcon(phase));
      });
    });

    it('should show complete indicator when COMPLETE', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask(),
        currentPhase: 'COMPLETE',
      });

      render(<TaskProgress />);
      expect(screen.getByText('🎉')).toBeInTheDocument();
    });
  });

  describe('metrics display', () => {
    it('should show total steps', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask(),
        currentPhase: 'EXPLORING',
        metrics: createMockMetrics({ total_steps: 15 }),
      });

      render(<TaskProgress />);
      expect(screen.getByText('Steps: 15')).toBeInTheDocument();
    });

    it('should show handoffs count', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask(),
        currentPhase: 'DESIGNING',
        metrics: createMockMetrics({ handoffs: 2 }),
      });

      render(<TaskProgress />);
      expect(screen.getByText('Handoffs: 2')).toBeInTheDocument();
    });

    it('should show artifacts count', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask(),
        currentPhase: 'PROTOTYPING',
        metrics: createMockMetrics({ artifacts_produced: 5 }),
      });

      render(<TaskProgress />);
      expect(screen.getByText('Artifacts: 5')).toBeInTheDocument();
    });

    it('should show duration when non-zero', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask(),
        currentPhase: 'COMPLETE',
        metrics: createMockMetrics({ duration_seconds: 12.5 }),
      });

      render(<TaskProgress />);
      expect(screen.getByText('Duration: 12.5s')).toBeInTheDocument();
    });

    it('should not show duration when zero', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask(),
        currentPhase: 'EXPLORING',
        metrics: createMockMetrics({ duration_seconds: 0 }),
      });

      render(<TaskProgress />);
      expect(screen.queryByText(/Duration:/)).not.toBeInTheDocument();
    });
  });

  describe('progress visualization', () => {
    it('should render pipeline with 5 phase nodes', () => {
      useWorkshopStore.setState({
        activeTask: createMockTask(),
        currentPhase: 'EXPLORING',
      });

      render(<TaskProgress />);

      // Each phase has an icon
      expect(screen.getByText('🔍')).toBeInTheDocument(); // Scout
      expect(screen.getByText('📐')).toBeInTheDocument(); // Sage
      expect(screen.getByText('⚡')).toBeInTheDocument(); // Spark
      expect(screen.getByText('🔧')).toBeInTheDocument(); // Steady
      expect(screen.getByText('🔗')).toBeInTheDocument(); // Sync
    });
  });
});

// Helper to get phase icon
function getPhaseIcon(phase: WorkshopPhase): string {
  const icons: Record<string, string> = {
    EXPLORING: '🔍',
    DESIGNING: '📐',
    PROTOTYPING: '⚡',
    REFINING: '🔧',
    INTEGRATING: '🔗',
  };
  return icons[phase] || '';
}
