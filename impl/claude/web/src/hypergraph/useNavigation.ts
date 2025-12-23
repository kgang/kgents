/**
 * useNavigation — Graph navigation state management
 *
 * "Navigation is not movement. Navigation is edge traversal."
 *
 * This hook manages the complete navigation state for Hypergraph Emacs,
 * including current node, trail, cursor, mode, and K-Block state.
 */

import { useCallback, useReducer, useRef } from 'react';

import type {
  NavigationState,
  NavigationAction,
  GraphNode,
  EdgeType,
  Position,
  EditorMode,
} from './types';
import { createInitialState, createTrailStep } from './types';

// =============================================================================
// Reducer
// =============================================================================

function navigationReducer(state: NavigationState, action: NavigationAction): NavigationState {
  switch (action.type) {
    // =========================================================================
    // Focus Operations
    // =========================================================================

    case 'FOCUS_NODE': {
      const { node } = action;

      // Add current node to trail before switching
      const newSteps = state.currentNode
        ? [...state.trail.steps, createTrailStep(state.currentNode, null, state.cursor)].slice(
            -state.trail.maxLength
          )
        : state.trail.steps;

      return {
        ...state,
        currentNode: node,
        trail: { ...state.trail, steps: newSteps },
        cursor: { line: 0, column: 0 },
        viewport: { ...state.viewport, topLine: 0, scrollPercent: 0 },
        error: null,
      };
    }

    case 'NODE_LOADED': {
      return {
        ...state,
        currentNode: action.node,
        loading: false,
        error: null,
      };
    }

    // =========================================================================
    // Graph Navigation
    // =========================================================================

    case 'GO_BACK': {
      if (state.trail.steps.length === 0) {
        return state;
      }

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
      if (state.siblings.length === 0) {
        return state;
      }

      const newIndex =
        (state.siblingIndex + action.direction + state.siblings.length) % state.siblings.length;

      const newNode = state.siblings[newIndex];

      // Add current to trail
      const newSteps = state.currentNode
        ? [...state.trail.steps, createTrailStep(state.currentNode, null, state.cursor)].slice(
            -state.trail.maxLength
          )
        : state.trail.steps;

      return {
        ...state,
        currentNode: newNode,
        siblingIndex: newIndex,
        trail: { ...state.trail, steps: newSteps },
        cursor: { line: 0, column: 0 },
      };
    }

    // =========================================================================
    // Cursor Movement
    // =========================================================================

    case 'MOVE_CURSOR': {
      return {
        ...state,
        cursor: action.position,
      };
    }

    case 'MOVE_LINE': {
      return {
        ...state,
        cursor: {
          ...state.cursor,
          line: Math.max(0, state.cursor.line + action.delta),
        },
      };
    }

    case 'MOVE_COLUMN': {
      return {
        ...state,
        cursor: {
          ...state.cursor,
          column: Math.max(0, state.cursor.column + action.delta),
        },
      };
    }

    case 'GOTO_LINE': {
      return {
        ...state,
        cursor: { line: Math.max(0, action.line), column: 0 },
      };
    }

    case 'GOTO_START': {
      return {
        ...state,
        cursor: { line: 0, column: 0 },
      };
    }

    case 'GOTO_END': {
      // We'd need content to know the last line, but this sets the intent
      return {
        ...state,
        cursor: { line: Infinity, column: 0 },
      };
    }

    // =========================================================================
    // Mode Changes
    // =========================================================================

    case 'SET_MODE': {
      return {
        ...state,
        mode: action.mode,
      };
    }

    case 'ENTER_INSERT': {
      return {
        ...state,
        mode: 'INSERT',
      };
    }

    case 'EXIT_INSERT': {
      return {
        ...state,
        mode: 'NORMAL',
      };
    }

    case 'ENTER_COMMAND': {
      return {
        ...state,
        mode: 'COMMAND',
      };
    }

    case 'EXIT_COMMAND': {
      return {
        ...state,
        mode: 'NORMAL',
      };
    }

    case 'ENTER_EDGE': {
      // Initialize edge pending state with current node as source
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

    case 'EXIT_EDGE': {
      return {
        ...state,
        mode: 'NORMAL',
        edgePending: null,
      };
    }

    // =========================================================================
    // Edge Mode Operations
    // =========================================================================

    case 'EDGE_SELECT_TYPE': {
      if (!state.edgePending) return state;

      return {
        ...state,
        edgePending: {
          ...state.edgePending,
          edgeType: action.edgeType,
          phase: 'select-target',
        },
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

    case 'EDGE_CONFIRM': {
      // Edge creation will be handled by the component (calls API, emits witness)
      // Just clear the pending state
      return {
        ...state,
        mode: 'NORMAL',
        edgePending: null,
      };
    }

    case 'EDGE_CANCEL': {
      return {
        ...state,
        mode: 'NORMAL',
        edgePending: null,
      };
    }

    case 'ENTER_WITNESS': {
      return {
        ...state,
        mode: 'WITNESS',
      };
    }

    case 'EXIT_WITNESS': {
      return {
        ...state,
        mode: 'NORMAL',
      };
    }

    // =========================================================================
    // K-Block Operations
    // =========================================================================

    case 'KBLOCK_CREATED': {
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
    }

    case 'KBLOCK_UPDATED': {
      if (!state.kblock) return state;

      return {
        ...state,
        kblock: {
          ...state.kblock,
          workingContent: action.content,
          isDirty: action.content !== state.kblock.baseContent,
          isolation: action.content !== state.kblock.baseContent ? 'DIRTY' : 'PRISTINE',
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

    case 'KBLOCK_COMMITTED': {
      return {
        ...state,
        kblock: null,
      };
    }

    case 'KBLOCK_DISCARDED': {
      return {
        ...state,
        kblock: null,
      };
    }

    // =========================================================================
    // Loading State
    // =========================================================================

    case 'SET_LOADING': {
      return {
        ...state,
        loading: action.loading,
      };
    }

    case 'SET_ERROR': {
      return {
        ...state,
        error: action.error,
        loading: false,
      };
    }

    case 'SET_SIBLINGS': {
      return {
        ...state,
        siblings: action.siblings,
        siblingIndex: action.index,
      };
    }

    default:
      return state;
  }
}

// =============================================================================
// Hook
// =============================================================================

export interface UseNavigationResult {
  /** Current navigation state */
  state: NavigationState;

  /** Dispatch an action */
  dispatch: React.Dispatch<NavigationAction>;

  // Convenience methods (wrap dispatch)

  /** Focus a specific node */
  focusNode: (node: GraphNode) => void;

  /** Focus by path (triggers async load) */
  focusPath: (path: string) => void;

  /** Navigate to parent (via incoming edge or trail) */
  goParent: () => void;

  /** Navigate to child (via outgoing edge) */
  goChild: (edgeType?: EdgeType) => void;

  /** Navigate to sibling (gj/gk) */
  goSibling: (direction: 1 | -1) => void;

  /** Navigate to definition (gd - implements edge) */
  goDefinition: () => void;

  /** Navigate to references (gr - incoming edges) */
  goReferences: () => void;

  /** Navigate to tests (gt - tests edge) */
  goTests: () => void;

  /** Go back in trail */
  goBack: () => void;

  /** Move cursor */
  moveCursor: (position: Position) => void;

  /** Set mode */
  setMode: (mode: EditorMode) => void;

  /** Enter insert mode */
  enterInsert: () => void;

  /** Exit to normal mode */
  exitToNormal: () => void;

  /** Get current trail breadcrumb */
  getTrailBreadcrumb: () => string;
}

/**
 * Hook for managing graph navigation state.
 */
export function useNavigation(): UseNavigationResult {
  const [state, dispatch] = useReducer(navigationReducer, undefined, createInitialState);

  // Track pending path loads
  const pendingPathRef = useRef<string | null>(null);

  // =========================================================================
  // Convenience Methods
  // =========================================================================

  const focusNode = useCallback((node: GraphNode) => {
    dispatch({ type: 'FOCUS_NODE', node });
  }, []);

  const focusPath = useCallback((path: string) => {
    // This will be wired to the API later
    pendingPathRef.current = path;
    dispatch({ type: 'SET_LOADING', loading: true });
    dispatch({ type: 'FOCUS_PATH', path });
  }, []);

  const goParent = useCallback(() => {
    const { currentNode, trail } = state;

    // First try trail
    if (trail.steps.length > 0) {
      dispatch({ type: 'GO_BACK' });
      return;
    }

    // Then try incoming edges (derives_from, extends)
    if (currentNode) {
      const parentEdge = currentNode.incomingEdges.find(
        (e) => e.type === 'derives_from' || e.type === 'extends'
      );
      if (parentEdge) {
        // Would need to load the parent node
        dispatch({ type: 'FOCUS_PATH', path: parentEdge.source });
      }
    }
  }, [state]);

  const goChild = useCallback(
    (edgeType?: EdgeType) => {
      const { currentNode } = state;
      if (!currentNode) return;

      const childEdges = edgeType
        ? currentNode.outgoingEdges.filter((e) => e.type === edgeType)
        : currentNode.outgoingEdges;

      if (childEdges.length === 1) {
        dispatch({ type: 'FOCUS_PATH', path: childEdges[0].target });
      } else if (childEdges.length > 1) {
        // Would show a picker - for now just go to first
        dispatch({ type: 'FOCUS_PATH', path: childEdges[0].target });
      }
    },
    [state]
  );

  const goSibling = useCallback((direction: 1 | -1) => {
    dispatch({ type: 'GO_SIBLING', direction });
  }, []);

  const goDefinition = useCallback(() => {
    const { currentNode } = state;
    if (!currentNode) return;

    const implEdge = currentNode.outgoingEdges.find((e) => e.type === 'implements');
    if (implEdge) {
      dispatch({ type: 'FOCUS_PATH', path: implEdge.target });
    }
  }, [state]);

  const goReferences = useCallback(() => {
    const { currentNode } = state;
    if (!currentNode) return;

    // Show all incoming edges
    if (currentNode.incomingEdges.length === 1) {
      dispatch({ type: 'FOCUS_PATH', path: currentNode.incomingEdges[0].source });
    } else if (currentNode.incomingEdges.length > 1) {
      // Would show a picker
      dispatch({ type: 'FOCUS_PATH', path: currentNode.incomingEdges[0].source });
    }
  }, [state]);

  const goTests = useCallback(() => {
    const { currentNode } = state;
    if (!currentNode) return;

    const testEdge = currentNode.outgoingEdges.find((e) => e.type === 'tests');
    if (testEdge) {
      dispatch({ type: 'FOCUS_PATH', path: testEdge.target });
    }
  }, [state]);

  const goBack = useCallback(() => {
    dispatch({ type: 'GO_BACK' });
  }, []);

  const moveCursor = useCallback((position: Position) => {
    dispatch({ type: 'MOVE_CURSOR', position });
  }, []);

  const setMode = useCallback((mode: EditorMode) => {
    dispatch({ type: 'SET_MODE', mode });
  }, []);

  const enterInsert = useCallback(() => {
    dispatch({ type: 'ENTER_INSERT' });
  }, []);

  const exitToNormal = useCallback(() => {
    dispatch({ type: 'SET_MODE', mode: 'NORMAL' });
  }, []);

  const getTrailBreadcrumb = useCallback(() => {
    const { trail, currentNode } = state;
    const nodes = [...trail.steps.map((s) => s.node), currentNode].filter(Boolean);
    return nodes
      .slice(-5)
      .map((n) => n!.title || n!.path.split('/').pop() || n!.path)
      .join(' → ');
  }, [state]);

  return {
    state,
    dispatch,
    focusNode,
    focusPath,
    goParent,
    goChild,
    goSibling,
    goDefinition,
    goReferences,
    goTests,
    goBack,
    moveCursor,
    setMode,
    enterInsert,
    exitToNormal,
    getTrailBreadcrumb,
  };
}
