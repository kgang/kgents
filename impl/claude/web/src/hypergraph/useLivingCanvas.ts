/**
 * useLivingCanvas — State management for the Living Canvas graph sidebar
 *
 * "The map IS the territory—when the map is alive."
 *
 * Manages:
 * - Sidebar visibility and dimensions
 * - Bidirectional selection sync between graph and editor
 * - Persistence of layout preferences
 */

import { useState, useEffect, useCallback, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface LiveCanvasState {
  /** Sidebar visibility */
  isOpen: boolean;
  /** Sidebar width in pixels */
  width: number;
  /** Currently focused node path (synced with editor) */
  focusedPath: string | null;
}

export interface LiveCanvasActions {
  /** Toggle sidebar visibility */
  toggle: () => void;
  /** Open sidebar */
  open: () => void;
  /** Close sidebar */
  close: () => void;
  /** Set sidebar width */
  setWidth: (width: number) => void;
  /** Focus a node in the graph */
  focusNode: (path: string | null) => void;
}

export interface UseLivingCanvasOptions {
  /** Initial visibility state */
  initialOpen?: boolean;
  /** Initial width */
  initialWidth?: number;
  /** Callback when a node is clicked in the graph */
  onNodeClick?: (path: string) => void;
  /** Current editor focused path (for sync) */
  editorFocusedPath?: string | null;
}

// =============================================================================
// Constants
// =============================================================================

const STORAGE_KEY = 'living-canvas-state';
const DEFAULT_WIDTH = 350;
const MIN_WIDTH = 250;
const MAX_WIDTH = 800;

// =============================================================================
// Hook
// =============================================================================

export function useLivingCanvas(options: UseLivingCanvasOptions = {}): {
  state: LiveCanvasState;
  actions: LiveCanvasActions;
} {
  const { initialOpen = false, initialWidth = DEFAULT_WIDTH, onNodeClick, editorFocusedPath } = options;

  // Load persisted state
  const loadPersistedState = useCallback((): Partial<LiveCanvasState> => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return {
          width: Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, parsed.width ?? initialWidth)),
          // Don't persist isOpen or focusedPath (session-specific)
        };
      }
    } catch (error) {
      console.warn('[useLivingCanvas] Failed to load persisted state:', error);
    }
    return {};
  }, [initialWidth]);

  // State
  const [isOpen, setIsOpen] = useState(initialOpen);
  const [width, setWidthInternal] = useState(() => {
    const persisted = loadPersistedState();
    return persisted.width ?? initialWidth;
  });
  const [focusedPath, setFocusedPath] = useState<string | null>(null);

  // Track if focus came from editor (to avoid infinite sync loops)
  const focusSourceRef = useRef<'editor' | 'graph' | null>(null);

  // Persist width changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ width }));
    } catch (error) {
      console.warn('[useLivingCanvas] Failed to persist state:', error);
    }
  }, [width]);

  // Sync editor focus to graph (when editor navigates)
  useEffect(() => {
    if (editorFocusedPath && focusSourceRef.current !== 'graph') {
      focusSourceRef.current = 'editor';
      setFocusedPath(editorFocusedPath);
    }
  }, [editorFocusedPath]);

  // Actions
  const toggle = useCallback(() => {
    setIsOpen((prev) => !prev);
  }, []);

  const open = useCallback(() => {
    setIsOpen(true);
  }, []);

  const close = useCallback(() => {
    setIsOpen(false);
  }, []);

  const setWidth = useCallback((newWidth: number) => {
    const clamped = Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, newWidth));
    setWidthInternal(clamped);
  }, []);

  const focusNode = useCallback(
    (path: string | null) => {
      focusSourceRef.current = 'graph';
      setFocusedPath(path);

      // Notify parent when graph node is clicked
      if (path && onNodeClick) {
        onNodeClick(path);
      }
    },
    [onNodeClick]
  );

  return {
    state: {
      isOpen,
      width,
      focusedPath,
    },
    actions: {
      toggle,
      open,
      close,
      setWidth,
      focusNode,
    },
  };
}
