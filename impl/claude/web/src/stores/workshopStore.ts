import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import type {
  BuilderSummary,
  WorkshopEvent,
  WorkshopArtifact,
  WorkshopTask,
  WorkshopPhase,
  WorkshopMetrics,
  WorkshopPlan,
} from '@/api/types';

// =============================================================================
// Types
// =============================================================================

interface WorkshopState {
  // Workshop metadata
  workshopId: string | null;

  // Task state
  activeTask: WorkshopTask | null;
  plan: WorkshopPlan | null;
  currentPhase: WorkshopPhase;

  // Builders
  builders: BuilderSummary[];
  selectedBuilder: string | null;

  // Events & Artifacts
  events: WorkshopEvent[];
  artifacts: WorkshopArtifact[];

  // Playback
  isRunning: boolean;
  speed: number;

  // Metrics
  metrics: WorkshopMetrics;

  // Actions
  setWorkshopId: (id: string | null) => void;
  setActiveTask: (task: WorkshopTask | null) => void;
  setPlan: (plan: WorkshopPlan | null) => void;
  setPhase: (phase: WorkshopPhase) => void;
  setBuilders: (builders: BuilderSummary[]) => void;
  updateBuilder: (archetype: string, updates: Partial<BuilderSummary>) => void;
  selectBuilder: (archetype: string | null) => void;
  addEvent: (event: WorkshopEvent) => void;
  addArtifact: (artifact: WorkshopArtifact) => void;
  setRunning: (running: boolean) => void;
  setSpeed: (speed: number) => void;
  setMetrics: (metrics: WorkshopMetrics) => void;
  clearEvents: () => void;
  reset: () => void;
}

// =============================================================================
// Initial State
// =============================================================================

const initialMetrics: WorkshopMetrics = {
  total_steps: 0,
  total_events: 0,
  total_tokens: 0,
  dialogue_tokens: 0,
  artifacts_produced: 0,
  phases_completed: 0,
  handoffs: 0,
  perturbations: 0,
  duration_seconds: 0,
};

const initialState = {
  workshopId: null,
  activeTask: null,
  plan: null,
  currentPhase: 'IDLE' as WorkshopPhase,
  builders: [],
  selectedBuilder: null,
  events: [],
  artifacts: [],
  isRunning: false,
  speed: 1.0,
  metrics: initialMetrics,
};

// =============================================================================
// Store
// =============================================================================

export const useWorkshopStore = create<WorkshopState>()(
  immer((set) => ({
    ...initialState,

    setWorkshopId: (id) => set({ workshopId: id }),

    setActiveTask: (task) => set({ activeTask: task }),

    setPlan: (plan) => set({ plan }),

    setPhase: (phase) => set({ currentPhase: phase }),

    setBuilders: (builders) => set({ builders }),

    updateBuilder: (archetype, updates) =>
      set((state) => {
        const idx = state.builders.findIndex((b) => b.archetype === archetype);
        if (idx >= 0) {
          state.builders[idx] = { ...state.builders[idx], ...updates };
        }
      }),

    selectBuilder: (archetype) => set({ selectedBuilder: archetype }),

    addEvent: (event) =>
      set((state) => {
        // Keep last 100 events
        state.events = [event, ...state.events.slice(0, 99)];
        state.currentPhase = event.phase;

        // Update active builder based on event
        if (event.builder) {
          state.builders.forEach((b) => {
            b.is_active = b.archetype === event.builder;
          });
        }
      }),

    addArtifact: (artifact) =>
      set((state) => {
        state.artifacts = [...state.artifacts, artifact];
      }),

    setRunning: (running) => set({ isRunning: running }),

    setSpeed: (speed) => set({ speed: Math.max(0.5, Math.min(4.0, speed)) }),

    setMetrics: (metrics) => set({ metrics }),

    clearEvents: () => set({ events: [], artifacts: [] }),

    reset: () => set(initialState),
  }))
);

// =============================================================================
// Selectors
// =============================================================================

export const selectActiveBuilder = () => (state: WorkshopState) =>
  state.builders.find((b) => b.is_active) || null;

export const selectSelectedBuilderData = () => (state: WorkshopState) =>
  state.builders.find((b) => b.archetype === state.selectedBuilder) || null;

export const selectPhaseProgress = () => (state: WorkshopState) => {
  const phases: WorkshopPhase[] = [
    'EXPLORING',
    'DESIGNING',
    'PROTOTYPING',
    'REFINING',
    'INTEGRATING',
  ];
  const currentIdx = phases.indexOf(state.currentPhase);
  if (currentIdx < 0) return 0;
  return ((currentIdx + 1) / phases.length) * 100;
};
