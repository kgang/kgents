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
  TaskHistoryItem,
  TaskDetailResponse,
  AggregateMetrics,
  BuilderPerformanceMetrics,
  FlowMetrics,
  ReplayState,
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

  // History (Chunk 9)
  taskHistory: TaskHistoryItem[];
  historyPage: number;
  historyTotal: number;
  historyTotalPages: number;
  selectedTaskId: string | null;
  taskDetail: TaskDetailResponse | null;

  // Aggregate Metrics (Chunk 9)
  aggregateMetrics: AggregateMetrics | null;
  builderMetrics: Record<string, BuilderPerformanceMetrics>;
  flowMetrics: FlowMetrics | null;
  metricsPeriod: '24h' | '7d' | '30d' | 'all';

  // Replay (Chunk 9)
  replay: ReplayState | null;

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

  // History Actions (Chunk 9)
  setTaskHistory: (tasks: TaskHistoryItem[], total: number, page: number, totalPages: number) => void;
  setTaskDetail: (detail: TaskDetailResponse | null) => void;
  selectTask: (taskId: string | null) => void;

  // Metrics Actions (Chunk 9)
  setAggregateMetrics: (metrics: AggregateMetrics) => void;
  setBuilderMetrics: (archetype: string, metrics: BuilderPerformanceMetrics) => void;
  setFlowMetrics: (metrics: FlowMetrics) => void;
  setMetricsPeriod: (period: '24h' | '7d' | '30d' | 'all') => void;

  // Replay Actions (Chunk 9)
  startReplay: (taskId: string, events: WorkshopEvent[], duration: number) => void;
  stepReplay: (direction: 1 | -1) => void;
  seekReplay: (index: number) => void;
  setReplaySpeed: (speed: number) => void;
  toggleReplayPlaying: () => void;
  stopReplay: () => void;
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
  // History (Chunk 9)
  taskHistory: [],
  historyPage: 1,
  historyTotal: 0,
  historyTotalPages: 0,
  selectedTaskId: null,
  taskDetail: null,
  // Aggregate Metrics (Chunk 9)
  aggregateMetrics: null,
  builderMetrics: {},
  flowMetrics: null,
  metricsPeriod: '24h' as const,
  // Replay (Chunk 9)
  replay: null,
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

    // History Actions (Chunk 9)
    setTaskHistory: (tasks, total, page, totalPages) =>
      set({
        taskHistory: tasks,
        historyTotal: total,
        historyPage: page,
        historyTotalPages: totalPages,
      }),

    setTaskDetail: (detail) => set({ taskDetail: detail }),

    selectTask: (taskId) => set({ selectedTaskId: taskId, taskDetail: null }),

    // Metrics Actions (Chunk 9)
    setAggregateMetrics: (metrics) => set({ aggregateMetrics: metrics }),

    setBuilderMetrics: (archetype, metrics) =>
      set((state) => {
        state.builderMetrics[archetype] = metrics;
      }),

    setFlowMetrics: (metrics) => set({ flowMetrics: metrics }),

    setMetricsPeriod: (period) => set({ metricsPeriod: period }),

    // Replay Actions (Chunk 9)
    startReplay: (taskId, events, duration) =>
      set({
        replay: {
          taskId,
          events,
          currentIndex: 0,
          isPlaying: false,
          playbackSpeed: 1.0,
          duration,
          elapsed: 0,
        },
      }),

    stepReplay: (direction) =>
      set((state) => {
        if (!state.replay) return;
        const newIndex = state.replay.currentIndex + direction;
        if (newIndex >= 0 && newIndex < state.replay.events.length) {
          state.replay.currentIndex = newIndex;
          // Calculate elapsed time based on event timestamps
          const event = state.replay.events[newIndex];
          if (event && state.replay.events[0]) {
            const startTime = new Date(state.replay.events[0].timestamp).getTime();
            const currentTime = new Date(event.timestamp).getTime();
            state.replay.elapsed = (currentTime - startTime) / 1000;
          }
        }
      }),

    seekReplay: (index) =>
      set((state) => {
        if (!state.replay) return;
        if (index >= 0 && index < state.replay.events.length) {
          state.replay.currentIndex = index;
          const event = state.replay.events[index];
          if (event && state.replay.events[0]) {
            const startTime = new Date(state.replay.events[0].timestamp).getTime();
            const currentTime = new Date(event.timestamp).getTime();
            state.replay.elapsed = (currentTime - startTime) / 1000;
          }
        }
      }),

    setReplaySpeed: (speed) =>
      set((state) => {
        if (state.replay) {
          state.replay.playbackSpeed = Math.max(0.5, Math.min(4.0, speed));
        }
      }),

    toggleReplayPlaying: () =>
      set((state) => {
        if (state.replay) {
          state.replay.isPlaying = !state.replay.isPlaying;
        }
      }),

    stopReplay: () => set({ replay: null }),
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
