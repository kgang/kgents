/**
 * useNavigation — Graph navigation state management
 *
 * "Navigation is not movement. Navigation is edge traversal."
 *
 * This hook manages the complete navigation state for Membrane Editor,
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
} from './state/types';
import { createInitialState } from './state/types';
import { navigationReducer } from './state/reducer';

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
