import { create } from 'zustand';
import { immer } from 'zustand/middleware/immer';
import type {
  CitizenSummary,
  CitizenManifest,
  TownEvent,
  TownPhase,
  Coalition,
} from '@/api/types';

// =============================================================================
// Types
// =============================================================================

interface Interaction {
  id: string;
  participants: string[];
  operation: string;
  startTick: number;
  fadeProgress: number;
}

interface TownState {
  // Town metadata
  townId: string | null;
  townName: string;

  // Citizens
  citizens: CitizenSummary[];
  citizenPositions: Map<string, { x: number; y: number }>;

  // Selection
  selectedCitizenId: string | null;
  selectedCitizenManifest: CitizenManifest | null;
  currentLOD: number;
  hoveredCitizenId: string | null;

  // Playback
  isPlaying: boolean;
  speed: number;

  // Time state
  currentDay: number;
  currentPhase: TownPhase;
  currentTick: number;

  // Events
  events: TownEvent[];
  activeInteractions: Interaction[];

  // Coalitions
  coalitions: Coalition[];

  // Actions
  setTownId: (id: string | null) => void;
  setTownName: (name: string) => void;
  setCitizens: (citizens: CitizenSummary[]) => void;
  updateCitizenPosition: (id: string, x: number, y: number) => void;
  selectCitizen: (id: string | null) => void;
  setSelectedManifest: (manifest: CitizenManifest | null) => void;
  setLOD: (lod: number) => void;
  hoverCitizen: (id: string | null) => void;
  setPlaying: (playing: boolean) => void;
  setSpeed: (speed: number) => void;
  setPhase: (phase: TownPhase) => void;
  incrementDay: () => void;
  addEvent: (event: TownEvent) => void;
  addInteraction: (interaction: Interaction) => void;
  fadeInteraction: (id: string, progress: number) => void;
  clearInteraction: (id: string) => void;
  setCoalitions: (coalitions: Coalition[]) => void;
  clearEvents: () => void;
  reset: () => void;
}

// =============================================================================
// Initial State
// =============================================================================

const initialState = {
  townId: null,
  townName: '',
  citizens: [],
  citizenPositions: new Map(),
  selectedCitizenId: null,
  selectedCitizenManifest: null,
  currentLOD: 0,
  hoveredCitizenId: null,
  isPlaying: false,
  speed: 1.0,
  currentDay: 1,
  currentPhase: 'MORNING' as TownPhase,
  currentTick: 0,
  events: [],
  activeInteractions: [],
  coalitions: [],
};

// =============================================================================
// Store
// =============================================================================

export const useTownStore = create<TownState>()(
  immer((set) => ({
    ...initialState,

    setTownId: (id) => set({ townId: id }),

    setTownName: (name) => set({ townName: name }),

    setCitizens: (citizens) =>
      set((state) => {
        state.citizens = citizens;
        // Initialize positions from regions
        citizens.forEach((citizen, index) => {
          if (!state.citizenPositions.has(citizen.id)) {
            const pos = regionToGridPosition(citizen.region, index, citizens.length);
            state.citizenPositions.set(citizen.id, pos);
          }
        });
      }),

    updateCitizenPosition: (id, x, y) =>
      set((state) => {
        state.citizenPositions.set(id, { x, y });
      }),

    selectCitizen: (id) =>
      set({
        selectedCitizenId: id,
        currentLOD: 0, // Reset LOD when selecting new citizen
        selectedCitizenManifest: null,
      }),

    setSelectedManifest: (manifest) => set({ selectedCitizenManifest: manifest }),

    setLOD: (lod) => set({ currentLOD: lod }),

    hoverCitizen: (id) => set({ hoveredCitizenId: id }),

    setPlaying: (playing) => set({ isPlaying: playing }),

    setSpeed: (speed) => set({ speed: Math.max(0.5, Math.min(4.0, speed)) }),

    setPhase: (phase) => set({ currentPhase: phase }),

    incrementDay: () =>
      set((state) => {
        state.currentDay += 1;
      }),

    addEvent: (event) =>
      set((state) => {
        // Keep last 100 events
        state.events = [event, ...state.events.slice(0, 99)];
        state.currentPhase = event.phase;
        state.currentTick = event.tick;

        // Update citizen phases based on operation
        event.participants.forEach((name) => {
          const citizen = state.citizens.find((c) => c.name === name);
          if (citizen) {
            citizen.phase = operationToPhase(event.operation);
          }
        });
      }),

    addInteraction: (interaction) =>
      set((state) => {
        state.activeInteractions.push(interaction);
      }),

    fadeInteraction: (id, progress) =>
      set((state) => {
        const interaction = state.activeInteractions.find((i) => i.id === id);
        if (interaction) {
          interaction.fadeProgress = progress;
        }
      }),

    clearInteraction: (id) =>
      set((state) => {
        state.activeInteractions = state.activeInteractions.filter((i) => i.id !== id);
      }),

    setCoalitions: (coalitions) => set({ coalitions }),

    clearEvents: () => set({ events: [], activeInteractions: [] }),

    reset: () => set(initialState),
  }))
);

// =============================================================================
// Helpers
// =============================================================================

function operationToPhase(operation: string): 'IDLE' | 'WORKING' | 'SOCIALIZING' | 'REFLECTING' | 'RESTING' {
  if (['greet', 'gossip', 'trade'].includes(operation)) return 'SOCIALIZING';
  if (['work', 'craft', 'build'].includes(operation)) return 'WORKING';
  if (['reflect', 'journal', 'meditate'].includes(operation)) return 'REFLECTING';
  if (['rest', 'sleep'].includes(operation)) return 'RESTING';
  return 'IDLE';
}

// Region to grid position mapping (20x20 grid)
const REGION_POSITIONS: Record<string, { x: number; y: number }> = {
  square: { x: 10, y: 10 },
  market: { x: 14, y: 8 },
  inn: { x: 6, y: 8 },
  workshop: { x: 16, y: 12 },
  smithy: { x: 18, y: 14 },
  temple: { x: 4, y: 10 },
  library: { x: 4, y: 14 },
  garden: { x: 10, y: 4 },
  well: { x: 8, y: 2 },
  farm: { x: 10, y: 16 },
  granary: { x: 14, y: 18 },
  town_square: { x: 10, y: 10 },
};

function regionToGridPosition(
  region: string,
  citizenIndex: number,
  totalInRegion: number
): { x: number; y: number } {
  const base = REGION_POSITIONS[region] || { x: 10, y: 10 };

  // Add small offset for multiple citizens in same region
  if (totalInRegion <= 1) {
    return base;
  }

  const angleStep = (2 * Math.PI) / Math.max(totalInRegion, 1);
  const angle = angleStep * citizenIndex;
  const radius = 1.5;

  return {
    x: Math.round(base.x + Math.cos(angle) * radius),
    y: Math.round(base.y + Math.sin(angle) * radius),
  };
}
