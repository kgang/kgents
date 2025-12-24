/**
 * useTelescopeState — State management for telescope navigation
 *
 * "The file is a lie. There is only the graph."
 *
 * Manages focal distance, visible layers, and loss filtering for the unified
 * telescope interface. Replaces page-based routing with continuous zoom metaphor.
 */

import { createContext, useContext, useReducer, useMemo } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface TelescopeState {
  /** Current focal distance (0 = ground, Infinity = cosmic) */
  focalDistance: number;

  /** Current focal point (node ID) */
  focalPoint: string | null;

  /** Visible layers at current distance (derived) */
  visibleLayers: number[];

  /** Loss threshold for filtering nodes */
  lossThreshold: number;

  /** Gradient field visibility toggle */
  showGradients: boolean;

  /** Multi-select state */
  selection: Set<string>;

  /** Focal history for breadcrumb trails */
  focalHistory: Array<{ nodeId: string; layer: number }>;
}

export type TelescopeAction =
  | { type: 'SET_FOCAL_DISTANCE'; distance: number }
  | { type: 'ZOOM_IN' }
  | { type: 'ZOOM_OUT' }
  | { type: 'JUMP_TO_LAYER'; layer: number }
  | { type: 'SET_FOCAL_POINT'; nodeId: string | null; layer?: number }
  | { type: 'SET_LOSS_THRESHOLD'; threshold: number }
  | { type: 'TOGGLE_GRADIENTS' }
  | { type: 'ADD_TO_SELECTION'; nodeId: string }
  | { type: 'REMOVE_FROM_SELECTION'; nodeId: string }
  | { type: 'CLEAR_SELECTION' }
  | { type: 'NAVIGATE_DERIVATION' } // Navigate to parent in derivation chain
  | { type: 'RESET' };

export interface TelescopeContextValue {
  state: TelescopeState;
  dispatch: React.Dispatch<TelescopeAction>;
}

// =============================================================================
// Constants
// =============================================================================

const LAYER_FOCAL_DISTANCES: Record<number, number> = {
  1: Infinity, // L1 - Axioms (cosmic)
  2: 1000, // L2 - Values
  3: 100, // L3 - Goals
  4: 10, // L4 - Specifications
  5: 1, // L5 - Actions
  6: 1, // L6 - Reflections (shares L5 distance)
  7: 0, // L7 - Documents (ground)
};

const DEFAULT_STATE: TelescopeState = {
  focalDistance: 10, // Start at L4 (specs)
  focalPoint: null,
  visibleLayers: [4],
  lossThreshold: 1.0, // Show all by default
  showGradients: true,
  selection: new Set(),
  focalHistory: [],
};

// =============================================================================
// Helpers
// =============================================================================

/**
 * Convert focal distance to visible layer numbers.
 *
 * Layer visibility follows a proximity rule:
 * - At exact layer distance: show that layer
 * - Between layers: show adjacent layers with transition
 */
export function focalDistanceToLayers(distance: number): number[] {
  if (distance === Infinity) return [1];
  if (distance === 0) return [7];

  // Find layers closest to focal distance
  const entries = Object.entries(LAYER_FOCAL_DISTANCES)
    .filter(([, d]) => d !== Infinity)
    .map(([layer, d]) => ({ layer: Number(layer), distance: d }))
    .sort((a, b) => a.distance - b.distance);

  // Find bracketing layers
  let lowerLayer = entries[0];
  let upperLayer = entries[entries.length - 1];

  for (let i = 0; i < entries.length - 1; i++) {
    if (distance >= entries[i].distance && distance <= entries[i + 1].distance) {
      lowerLayer = entries[i];
      upperLayer = entries[i + 1];
      break;
    }
  }

  // At exact layer distance, show only that layer
  if (distance === lowerLayer.distance) return [lowerLayer.layer];
  if (distance === upperLayer.distance) return [upperLayer.layer];

  // Between layers: show both for smooth transition
  return [lowerLayer.layer, upperLayer.layer];
}

/**
 * Convert layer number to canonical focal distance.
 */
export function layerToFocalDistance(layer: number): number {
  return LAYER_FOCAL_DISTANCES[layer] ?? 10;
}

/**
 * Clamp focal distance to valid range.
 */
function clampDistance(distance: number): number {
  if (distance === Infinity) return Infinity;
  if (distance <= 0) return 0;
  return Math.max(0, Math.min(10000, distance));
}

// =============================================================================
// Reducer
// =============================================================================

function telescopeReducer(
  state: TelescopeState,
  action: TelescopeAction
): TelescopeState {
  switch (action.type) {
    case 'SET_FOCAL_DISTANCE': {
      const distance = clampDistance(action.distance);
      return {
        ...state,
        focalDistance: distance,
        visibleLayers: focalDistanceToLayers(distance),
      };
    }

    case 'ZOOM_IN': {
      let newDistance: number;
      if (state.focalDistance === Infinity) {
        newDistance = 1000;
      } else if (state.focalDistance === 0) {
        return state; // Can't zoom in from ground
      } else {
        newDistance = state.focalDistance / 10;
      }
      newDistance = clampDistance(newDistance);
      return {
        ...state,
        focalDistance: newDistance,
        visibleLayers: focalDistanceToLayers(newDistance),
      };
    }

    case 'ZOOM_OUT': {
      let newDistance: number;
      if (state.focalDistance === Infinity) {
        return state; // Can't zoom out from cosmic
      } else if (state.focalDistance === 0) {
        newDistance = 1;
      } else if (state.focalDistance >= 1000) {
        newDistance = Infinity;
      } else {
        newDistance = state.focalDistance * 10;
      }
      newDistance = clampDistance(newDistance);
      return {
        ...state,
        focalDistance: newDistance,
        visibleLayers: focalDistanceToLayers(newDistance),
      };
    }

    case 'JUMP_TO_LAYER': {
      const distance = layerToFocalDistance(action.layer);
      return {
        ...state,
        focalDistance: distance,
        visibleLayers: focalDistanceToLayers(distance),
      };
    }

    case 'SET_FOCAL_POINT': {
      const layer = action.layer ?? 4; // Default to L4 if not specified
      const newHistory = state.focalPoint
        ? [...state.focalHistory, { nodeId: state.focalPoint, layer }]
        : state.focalHistory;

      return {
        ...state,
        focalPoint: action.nodeId,
        focalHistory: newHistory.slice(-10), // Keep last 10 for breadcrumbs
      };
    }

    case 'SET_LOSS_THRESHOLD': {
      return {
        ...state,
        lossThreshold: Math.max(0, Math.min(1, action.threshold)),
      };
    }

    case 'TOGGLE_GRADIENTS': {
      return {
        ...state,
        showGradients: !state.showGradients,
      };
    }

    case 'ADD_TO_SELECTION': {
      const newSelection = new Set(state.selection);
      newSelection.add(action.nodeId);
      return {
        ...state,
        selection: newSelection,
      };
    }

    case 'REMOVE_FROM_SELECTION': {
      const newSelection = new Set(state.selection);
      newSelection.delete(action.nodeId);
      return {
        ...state,
        selection: newSelection,
      };
    }

    case 'CLEAR_SELECTION': {
      return {
        ...state,
        selection: new Set(),
      };
    }

    case 'NAVIGATE_DERIVATION': {
      // Pop last item from history and focus on it
      if (state.focalHistory.length === 0) return state;

      const newHistory = [...state.focalHistory];
      const parent = newHistory.pop()!;

      return {
        ...state,
        focalPoint: parent.nodeId,
        focalHistory: newHistory,
        focalDistance: layerToFocalDistance(parent.layer),
        visibleLayers: focalDistanceToLayers(layerToFocalDistance(parent.layer)),
      };
    }

    case 'RESET': {
      return DEFAULT_STATE;
    }

    default:
      return state;
  }
}

// =============================================================================
// Context
// =============================================================================

const TelescopeContext = createContext<TelescopeContextValue | null>(null);

export function TelescopeProvider({ children }: { children: React.ReactNode }) {
  const [state, dispatch] = useReducer(telescopeReducer, DEFAULT_STATE);

  const value = useMemo(() => ({ state, dispatch }), [state]);

  return (
    <TelescopeContext.Provider value={value}>{children}</TelescopeContext.Provider>
  );
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Access telescope navigation state.
 *
 * @throws Error if used outside TelescopeProvider
 */
export function useTelescope(): TelescopeContextValue {
  const context = useContext(TelescopeContext);
  if (!context) {
    throw new Error('useTelescope must be used within TelescopeProvider');
  }
  return context;
}

/**
 * Standalone hook for managing telescope state without context.
 *
 * Useful for local component state or testing.
 */
export function useTelescopeState(
  initialState?: Partial<TelescopeState>
): [TelescopeState, React.Dispatch<TelescopeAction>] {
  const [state, dispatch] = useReducer(telescopeReducer, {
    ...DEFAULT_STATE,
    ...initialState,
  });

  return [state, dispatch];
}

// =============================================================================
// Utilities
// =============================================================================

/**
 * Get human-readable layer name.
 */
export function getLayerName(layer: number): string {
  const names: Record<number, string> = {
    1: 'Axioms',
    2: 'Values',
    3: 'Goals',
    4: 'Specifications',
    5: 'Actions',
    6: 'Reflections',
    7: 'Documents',
  };
  return names[layer] ?? `Layer ${layer}`;
}

/**
 * Get layer icon/emoji.
 */
export function getLayerIcon(layer: number): string {
  const icons: Record<number, string> = {
    1: '✦', // Axioms - cosmic
    2: '◆', // Values - diamonds
    3: '◉', // Goals - targets
    4: '▣', // Specifications - grid
    5: '→', // Actions - arrows
    6: '↺', // Reflections - cycle
    7: '▤', // Documents - text
  };
  return icons[layer] ?? '○';
}
