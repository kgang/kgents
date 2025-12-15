import { describe, it, expect, beforeEach } from 'vitest';
import { useWorkshopStore, selectPhaseProgress } from '@/stores/workshopStore';
import type { BuilderSummary, WorkshopEvent, WorkshopArtifact, WorkshopPhase } from '@/api/types';

// Helper to create mock builder
const createMockBuilder = (
  archetype: string,
  overrides: Partial<BuilderSummary> = {}
): BuilderSummary => ({
  archetype: archetype as BuilderSummary['archetype'],
  name: archetype,
  phase: 'IDLE' as BuilderSummary['phase'],
  is_active: false,
  is_in_specialty: false,
  ...overrides,
});

// Helper to create mock event
const createMockEvent = (
  type: string = 'ARTIFACT_PRODUCED',
  builder: string = 'Scout'
): WorkshopEvent => ({
  type: type as WorkshopEvent['type'],
  builder,
  phase: 'EXPLORING',
  message: 'Test event',
  artifact: null,
  timestamp: new Date().toISOString(),
  metadata: {},
});

// Helper to create mock artifact
const createMockArtifact = (): WorkshopArtifact => ({
  id: 'artifact-1',
  task_id: 'task-1',
  builder: 'Scout',
  phase: 'EXPLORING',
  content: { data: 'test' },
  created_at: new Date().toISOString(),
});

describe('workshopStore', () => {
  beforeEach(() => {
    useWorkshopStore.getState().reset();
  });

  describe('initial state', () => {
    it('should have null workshopId', () => {
      expect(useWorkshopStore.getState().workshopId).toBeNull();
    });

    it('should have no active task', () => {
      expect(useWorkshopStore.getState().activeTask).toBeNull();
    });

    it('should have IDLE phase', () => {
      expect(useWorkshopStore.getState().currentPhase).toBe('IDLE');
    });

    it('should have empty builders', () => {
      expect(useWorkshopStore.getState().builders).toEqual([]);
    });

    it('should not be running', () => {
      expect(useWorkshopStore.getState().isRunning).toBe(false);
    });

    it('should have default speed of 1.0', () => {
      expect(useWorkshopStore.getState().speed).toBe(1.0);
    });
  });

  describe('setWorkshopId', () => {
    it('should set workshop ID', () => {
      useWorkshopStore.getState().setWorkshopId('test-workshop');
      expect(useWorkshopStore.getState().workshopId).toBe('test-workshop');
    });

    it('should allow null', () => {
      useWorkshopStore.getState().setWorkshopId('test');
      useWorkshopStore.getState().setWorkshopId(null);
      expect(useWorkshopStore.getState().workshopId).toBeNull();
    });
  });

  describe('setBuilders', () => {
    it('should set builders array', () => {
      const builders = [createMockBuilder('Scout'), createMockBuilder('Sage')];

      useWorkshopStore.getState().setBuilders(builders);
      expect(useWorkshopStore.getState().builders).toEqual(builders);
    });
  });

  describe('updateBuilder', () => {
    beforeEach(() => {
      useWorkshopStore
        .getState()
        .setBuilders([createMockBuilder('Scout'), createMockBuilder('Sage')]);
    });

    it('should update specific builder', () => {
      useWorkshopStore.getState().updateBuilder('Scout', { is_active: true });

      const scout = useWorkshopStore.getState().builders.find((b) => b.archetype === 'Scout');
      expect(scout?.is_active).toBe(true);
    });

    it('should not affect other builders', () => {
      useWorkshopStore.getState().updateBuilder('Scout', { is_active: true });

      const sage = useWorkshopStore.getState().builders.find((b) => b.archetype === 'Sage');
      expect(sage?.is_active).toBe(false);
    });
  });

  describe('selectBuilder', () => {
    it('should set selected builder', () => {
      useWorkshopStore.getState().selectBuilder('Sage');
      expect(useWorkshopStore.getState().selectedBuilder).toBe('Sage');
    });

    it('should allow null (deselect)', () => {
      useWorkshopStore.getState().selectBuilder('Sage');
      useWorkshopStore.getState().selectBuilder(null);
      expect(useWorkshopStore.getState().selectedBuilder).toBeNull();
    });
  });

  describe('addEvent', () => {
    beforeEach(() => {
      useWorkshopStore
        .getState()
        .setBuilders([createMockBuilder('Scout'), createMockBuilder('Sage')]);
    });

    it('should add event to front of list', () => {
      const event = createMockEvent();
      useWorkshopStore.getState().addEvent(event);

      expect(useWorkshopStore.getState().events[0]).toEqual(event);
    });

    it('should update current phase from event', () => {
      const event = createMockEvent();
      event.phase = 'DESIGNING';

      useWorkshopStore.getState().addEvent(event);
      expect(useWorkshopStore.getState().currentPhase).toBe('DESIGNING');
    });

    it('should update builder active state', () => {
      const event = createMockEvent('PHASE_STARTED', 'Scout');
      useWorkshopStore.getState().addEvent(event);

      const scout = useWorkshopStore.getState().builders.find((b) => b.archetype === 'Scout');
      const sage = useWorkshopStore.getState().builders.find((b) => b.archetype === 'Sage');

      expect(scout?.is_active).toBe(true);
      expect(sage?.is_active).toBe(false);
    });

    it('should limit events to 100', () => {
      // Add 110 events
      for (let i = 0; i < 110; i++) {
        useWorkshopStore.getState().addEvent(createMockEvent());
      }

      expect(useWorkshopStore.getState().events.length).toBe(100);
    });
  });

  describe('addArtifact', () => {
    it('should add artifact to list', () => {
      const artifact = createMockArtifact();
      useWorkshopStore.getState().addArtifact(artifact);

      expect(useWorkshopStore.getState().artifacts).toContainEqual(artifact);
    });

    it('should preserve existing artifacts', () => {
      const artifact1 = { ...createMockArtifact(), id: 'a1' };
      const artifact2 = { ...createMockArtifact(), id: 'a2' };

      useWorkshopStore.getState().addArtifact(artifact1);
      useWorkshopStore.getState().addArtifact(artifact2);

      expect(useWorkshopStore.getState().artifacts.length).toBe(2);
    });
  });

  describe('setRunning', () => {
    it('should set running state', () => {
      useWorkshopStore.getState().setRunning(true);
      expect(useWorkshopStore.getState().isRunning).toBe(true);
    });
  });

  describe('setSpeed', () => {
    it('should set speed', () => {
      useWorkshopStore.getState().setSpeed(2.0);
      expect(useWorkshopStore.getState().speed).toBe(2.0);
    });

    it('should clamp speed minimum to 0.5', () => {
      useWorkshopStore.getState().setSpeed(0.1);
      expect(useWorkshopStore.getState().speed).toBe(0.5);
    });

    it('should clamp speed maximum to 4.0', () => {
      useWorkshopStore.getState().setSpeed(10);
      expect(useWorkshopStore.getState().speed).toBe(4.0);
    });
  });

  describe('setMetrics', () => {
    it('should set metrics', () => {
      const metrics = {
        total_steps: 10,
        total_events: 20,
        total_tokens: 100,
        dialogue_tokens: 50,
        artifacts_produced: 3,
        phases_completed: 2,
        handoffs: 1,
        perturbations: 0,
        duration_seconds: 5.5,
      };

      useWorkshopStore.getState().setMetrics(metrics);
      expect(useWorkshopStore.getState().metrics).toEqual(metrics);
    });
  });

  describe('clearEvents', () => {
    it('should clear events and artifacts', () => {
      useWorkshopStore.getState().addEvent(createMockEvent());
      useWorkshopStore.getState().addArtifact(createMockArtifact());

      useWorkshopStore.getState().clearEvents();

      expect(useWorkshopStore.getState().events).toEqual([]);
      expect(useWorkshopStore.getState().artifacts).toEqual([]);
    });
  });

  describe('reset', () => {
    it('should reset to initial state', () => {
      // Make changes
      useWorkshopStore.getState().setWorkshopId('test');
      useWorkshopStore.getState().setRunning(true);
      useWorkshopStore.getState().setPhase('DESIGNING');
      useWorkshopStore.getState().addEvent(createMockEvent());

      // Reset
      useWorkshopStore.getState().reset();

      expect(useWorkshopStore.getState().workshopId).toBeNull();
      expect(useWorkshopStore.getState().isRunning).toBe(false);
      expect(useWorkshopStore.getState().currentPhase).toBe('IDLE');
      expect(useWorkshopStore.getState().events).toEqual([]);
    });
  });

  describe('selectPhaseProgress', () => {
    it('should return 0 for IDLE', () => {
      useWorkshopStore.getState().setPhase('IDLE');
      const progress = selectPhaseProgress()(useWorkshopStore.getState());
      expect(progress).toBe(0);
    });

    it('should return 20% for EXPLORING', () => {
      useWorkshopStore.getState().setPhase('EXPLORING');
      const progress = selectPhaseProgress()(useWorkshopStore.getState());
      expect(progress).toBe(20);
    });

    it('should return 40% for DESIGNING', () => {
      useWorkshopStore.getState().setPhase('DESIGNING');
      const progress = selectPhaseProgress()(useWorkshopStore.getState());
      expect(progress).toBe(40);
    });

    it('should return 60% for PROTOTYPING', () => {
      useWorkshopStore.getState().setPhase('PROTOTYPING');
      const progress = selectPhaseProgress()(useWorkshopStore.getState());
      expect(progress).toBe(60);
    });

    it('should return 80% for REFINING', () => {
      useWorkshopStore.getState().setPhase('REFINING');
      const progress = selectPhaseProgress()(useWorkshopStore.getState());
      expect(progress).toBe(80);
    });

    it('should return 100% for INTEGRATING', () => {
      useWorkshopStore.getState().setPhase('INTEGRATING');
      const progress = selectPhaseProgress()(useWorkshopStore.getState());
      expect(progress).toBe(100);
    });
  });
});
