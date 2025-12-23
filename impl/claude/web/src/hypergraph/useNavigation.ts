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
  TrailStep,
} from './types';
import { createInitialState, createTrailStep } from './types';

// =============================================================================
// Reducer - Split into Sub-Reducers by Domain
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

/**
 * Main reducer: compose all sub-reducers
 */
function navigationReducer(state: NavigationState, action: NavigationAction): NavigationState {
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

  // Portal operations (zo/zc — inline edge expansion)

  /** Open portal for edge at current cursor (zo) */
  openPortal: () => void;

  /** Close portal for edge at current cursor (zc) */
  closePortal: () => void;

  /** Toggle portal for edge at current cursor (za) */
  togglePortal: () => void;

  /** Open all portals in current node (zO) */
  openAllPortals: () => void;

  /** Close all portals (zC) */
  closeAllPortals: () => void;

  /** Check if an edge has an open portal */
  isPortalOpen: (edgeId: string) => boolean;

  /** Get edge at current cursor position (if any) */
  getEdgeAtCursor: () => { edgeId: string; targetPath: string } | null;
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

  // =========================================================================
  // Portal Operations (zo/zc — inline edge expansion)
  // =========================================================================

  /**
   * Find the edge reference at the current cursor position.
   *
   * Heuristic: Look for lines that contain edge references like:
   * - [[path/to/file]] — wiki-style links
   * - [text](path/to/file) — markdown links
   * - @implements path/to/file — AGENTESE refs
   * - References: file.md — explicit references
   *
   * We match against outgoing edges from the current node.
   */
  const getEdgeAtCursor = useCallback((): { edgeId: string; targetPath: string } | null => {
    const { currentNode, cursor } = state;
    if (!currentNode?.content) return null;

    const lines = currentNode.content.split('\n');
    const currentLine = lines[Math.min(cursor.line, lines.length - 1)] || '';

    // Try to match the current line against outgoing edges
    for (const edge of currentNode.outgoingEdges) {
      // Extract filename from target path
      const targetFile = edge.target.split('/').pop() || edge.target;
      const targetBase = targetFile.replace(/\.[^.]+$/, ''); // Remove extension

      // Check if line contains this target
      if (
        currentLine.includes(edge.target) ||
        currentLine.includes(targetFile) ||
        currentLine.includes(targetBase) ||
        currentLine.includes(`[[${targetBase}]]`) ||
        currentLine.includes(`(${edge.target})`)
      ) {
        return { edgeId: edge.id, targetPath: edge.target };
      }
    }

    // Fallback: if cursor is on an edge line in the metadata section
    // (edges are often listed at the top)
    const edgeIndex = Math.min(cursor.line, currentNode.outgoingEdges.length - 1);
    if (edgeIndex >= 0 && currentNode.outgoingEdges[edgeIndex]) {
      const edge = currentNode.outgoingEdges[edgeIndex];
      return { edgeId: edge.id, targetPath: edge.target };
    }

    return null;
  }, [state]);

  const openPortal = useCallback(() => {
    const edgeRef = getEdgeAtCursor();
    if (edgeRef) {
      dispatch({ type: 'PORTAL_OPEN', edgeId: edgeRef.edgeId, targetPath: edgeRef.targetPath });
    }
  }, [getEdgeAtCursor, dispatch]);

  const closePortal = useCallback(() => {
    const edgeRef = getEdgeAtCursor();
    if (edgeRef) {
      dispatch({ type: 'PORTAL_CLOSE', edgeId: edgeRef.edgeId });
    }
  }, [getEdgeAtCursor, dispatch]);

  const togglePortal = useCallback(() => {
    const edgeRef = getEdgeAtCursor();
    if (edgeRef) {
      dispatch({ type: 'PORTAL_TOGGLE', edgeId: edgeRef.edgeId, targetPath: edgeRef.targetPath });
    }
  }, [getEdgeAtCursor, dispatch]);

  const openAllPortals = useCallback(() => {
    dispatch({ type: 'PORTAL_OPEN_ALL' });
  }, [dispatch]);

  const closeAllPortals = useCallback(() => {
    dispatch({ type: 'PORTAL_CLOSE_ALL' });
  }, [dispatch]);

  const isPortalOpen = useCallback(
    (edgeId: string): boolean => {
      return state.portals.has(edgeId);
    },
    [state.portals]
  );

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
    // Portal operations
    openPortal,
    closePortal,
    togglePortal,
    openAllPortals,
    closeAllPortals,
    isPortalOpen,
    getEdgeAtCursor,
  };
}
