/**
 * reducer — Navigation state reducer
 *
 * "The state machine is a composition of sub-reducers."
 *
 * Each domain (focus, cursor, graph, mode, edge, kblock, portal, loading)
 * has its own reducer. The main reducer composes them.
 */

import type {
  NavigationState,
  NavigationAction,
  GraphNode,
  TrailStep,
} from './types';
import { createTrailStep } from './types';

// =============================================================================
// Helpers
// =============================================================================

/**
 * Helper: Add current node to trail
 */
function addToTrail(
  state: NavigationState,
  newNode: GraphNode | null
): { steps: TrailStep[]; node: GraphNode | null } {
  const newSteps = state.currentNode
    ? [...state.trail.steps, createTrailStep(state.currentNode, null, state.cursor)].slice(
        -state.trail.maxLength
      )
    : state.trail.steps;

  return { steps: newSteps, node: newNode };
}

// =============================================================================
// Sub-Reducers
// =============================================================================

/**
 * Focus operations: FOCUS_NODE, NODE_LOADED, FOCUS_PATH
 */
function focusReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'FOCUS_NODE': {
      const { steps, node } = addToTrail(state, action.node);
      return {
        ...state,
        currentNode: node,
        trail: { ...state.trail, steps },
        cursor: { line: 0, column: 0 },
        viewport: { ...state.viewport, topLine: 0, scrollPercent: 0 },
        error: null,
      };
    }

    case 'NODE_LOADED':
      return {
        ...state,
        currentNode: action.node,
        loading: false,
        error: null,
      };

    default:
      return state;
  }
}

/**
 * Cursor movement: MOVE_*, GOTO_*
 */
function cursorReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'MOVE_CURSOR':
      return { ...state, cursor: action.position };

    case 'MOVE_LINE':
      return {
        ...state,
        cursor: { ...state.cursor, line: Math.max(0, state.cursor.line + action.delta) },
      };

    case 'MOVE_COLUMN':
      return {
        ...state,
        cursor: { ...state.cursor, column: Math.max(0, state.cursor.column + action.delta) },
      };

    case 'GOTO_LINE':
      return { ...state, cursor: { line: Math.max(0, action.line), column: 0 } };

    case 'GOTO_START':
      return { ...state, cursor: { line: 0, column: 0 } };

    case 'GOTO_END':
      return { ...state, cursor: { line: Infinity, column: 0 } };

    default:
      return state;
  }
}

/**
 * Graph navigation: GO_BACK, GO_SIBLING
 */
function graphNavigationReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'GO_BACK': {
      if (state.trail.steps.length === 0) return state;
      const steps = [...state.trail.steps];
      const lastStep = steps.pop()!;
      return {
        ...state,
        currentNode: lastStep.node,
        trail: { ...state.trail, steps },
        cursor: lastStep.cursor,
      };
    }

    case 'GO_SIBLING': {
      if (state.siblings.length === 0) return state;
      const newIndex =
        (state.siblingIndex + action.direction + state.siblings.length) % state.siblings.length;
      const { steps, node } = addToTrail(state, state.siblings[newIndex]);
      return {
        ...state,
        currentNode: node,
        siblingIndex: newIndex,
        trail: { ...state.trail, steps },
        cursor: { line: 0, column: 0 },
      };
    }

    default:
      return state;
  }
}

/**
 * Mode changes: SET_MODE, ENTER_*, EXIT_*
 */
function modeReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'SET_MODE':
      return { ...state, mode: action.mode };

    case 'ENTER_INSERT':
      return { ...state, mode: 'INSERT' };

    case 'EXIT_INSERT':
      return { ...state, mode: 'NORMAL' };

    case 'ENTER_COMMAND':
      return { ...state, mode: 'COMMAND' };

    case 'EXIT_COMMAND':
      return { ...state, mode: 'NORMAL' };

    case 'ENTER_EDGE': {
      if (!state.currentNode) return state;
      return {
        ...state,
        mode: 'EDGE',
        edgePending: {
          sourceId: state.currentNode.path,
          sourceLabel: state.currentNode.title || state.currentNode.path.split('/').pop() || '',
          edgeType: null,
          phase: 'select-type',
          targetId: null,
          targetLabel: null,
        },
      };
    }

    case 'EXIT_EDGE':
      return { ...state, mode: 'NORMAL', edgePending: null };

    case 'ENTER_WITNESS':
      return { ...state, mode: 'WITNESS' };

    case 'EXIT_WITNESS':
      return { ...state, mode: 'NORMAL' };

    default:
      return state;
  }
}

/**
 * Edge operations: EDGE_SELECT_TYPE, EDGE_SELECT_TARGET, EDGE_CONFIRM, EDGE_CANCEL
 */
function edgeReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'EDGE_SELECT_TYPE': {
      if (!state.edgePending) return state;
      return {
        ...state,
        edgePending: { ...state.edgePending, edgeType: action.edgeType, phase: 'select-target' },
      };
    }

    case 'EDGE_SELECT_TARGET': {
      if (!state.edgePending) return state;
      return {
        ...state,
        edgePending: {
          ...state.edgePending,
          targetId: action.targetId,
          targetLabel: action.targetLabel,
          phase: 'confirm',
        },
      };
    }

    case 'EDGE_CONFIRM':
      // Keep state as-is; EDGE_CONFIRMED will clear after API call
      return state;

    case 'EDGE_CONFIRMED':
      return { ...state, mode: 'NORMAL', edgePending: null };

    case 'EDGE_CANCEL':
      return { ...state, mode: 'NORMAL', edgePending: null };

    default:
      return state;
  }
}

/**
 * K-Block operations: KBLOCK_*
 */
function kblockReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'KBLOCK_CREATED':
      return {
        ...state,
        kblock: {
          blockId: action.blockId,
          isolation: 'PRISTINE',
          isDirty: false,
          baseContent: action.content,
          workingContent: action.content,
          checkpoints: [],
        },
      };

    case 'KBLOCK_UPDATED': {
      if (!state.kblock) return state;
      const isDirty = action.content !== state.kblock.baseContent;
      return {
        ...state,
        kblock: {
          ...state.kblock,
          workingContent: action.content,
          isDirty,
          isolation: isDirty ? 'DIRTY' : 'PRISTINE',
        },
      };
    }

    case 'KBLOCK_CHECKPOINT': {
      if (!state.kblock) return state;
      return {
        ...state,
        kblock: {
          ...state.kblock,
          checkpoints: [
            ...state.kblock.checkpoints,
            {
              id: action.id,
              content: state.kblock.workingContent,
              timestamp: Date.now(),
              message: action.message,
            },
          ],
        },
      };
    }

    case 'KBLOCK_COMMITTED':
      return { ...state, kblock: null };

    case 'KBLOCK_DISCARDED':
      return { ...state, kblock: null };

    default:
      return state;
  }
}

/**
 * Portal operations: PORTAL_OPEN, PORTAL_CLOSE, PORTAL_TOGGLE, etc.
 *
 * "Navigation IS expansion" — zo/zc expand edges inline.
 */
function portalReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'PORTAL_OPEN': {
      const newPortals = new Map(state.portals);
      const existing = newPortals.get(action.edgeId);
      if (existing && !existing.loading) {
        // Already open and loaded
        return state;
      }
      newPortals.set(action.edgeId, {
        edgeId: action.edgeId,
        targetNode: null,
        depth: 0,
        loading: true,
        collapsed: false,
      });
      return { ...state, portals: newPortals };
    }

    case 'PORTAL_CLOSE': {
      const newPortals = new Map(state.portals);
      if (!newPortals.has(action.edgeId)) {
        return state;
      }
      newPortals.delete(action.edgeId);
      return { ...state, portals: newPortals };
    }

    case 'PORTAL_TOGGLE': {
      const newPortals = new Map(state.portals);
      if (newPortals.has(action.edgeId)) {
        newPortals.delete(action.edgeId);
      } else {
        newPortals.set(action.edgeId, {
          edgeId: action.edgeId,
          targetNode: null,
          depth: 0,
          loading: true,
          collapsed: false,
        });
      }
      return { ...state, portals: newPortals };
    }

    case 'PORTAL_LOADED': {
      const existing = state.portals.get(action.edgeId);
      if (!existing) {
        return state;
      }
      const newPortals = new Map(state.portals);
      newPortals.set(action.edgeId, {
        ...existing,
        targetNode: action.node,
        loading: false,
      });
      return { ...state, portals: newPortals };
    }

    case 'PORTAL_OPEN_ALL': {
      if (!state.currentNode) return state;
      const newPortals = new Map(state.portals);
      for (const edge of state.currentNode.outgoingEdges) {
        if (!newPortals.has(edge.id)) {
          newPortals.set(edge.id, {
            edgeId: edge.id,
            targetNode: null,
            depth: 0,
            loading: true,
            collapsed: false,
          });
        }
      }
      return { ...state, portals: newPortals };
    }

    case 'PORTAL_CLOSE_ALL': {
      if (state.portals.size === 0) return state;
      return { ...state, portals: new Map() };
    }

    default:
      return state;
  }
}

/**
 * Loading state: SET_LOADING, SET_ERROR, SET_SIBLINGS
 */
function loadingReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    case 'SET_LOADING':
      return { ...state, loading: action.loading };

    case 'SET_ERROR':
      return { ...state, error: action.error, loading: false };

    case 'SET_SIBLINGS':
      return { ...state, siblings: action.siblings, siblingIndex: action.index };

    default:
      return state;
  }
}

// =============================================================================
// Main Reducer
// =============================================================================

/**
 * Main reducer: compose all sub-reducers
 *
 * Pattern: Try each sub-reducer in sequence. First one that returns
 * a new state wins.
 */
export function navigationReducer(
  state: NavigationState,
  action: NavigationAction
): NavigationState {
  // Try each sub-reducer in sequence
  const reducers = [
    focusReducer,
    cursorReducer,
    graphNavigationReducer,
    modeReducer,
    edgeReducer,
    kblockReducer,
    portalReducer,
    loadingReducer,
  ];

  for (const reducer of reducers) {
    const nextState = reducer(state, action);
    if (nextState !== state) {
      return nextState;
    }
  }

  return state;
}
