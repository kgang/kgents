/**
 * useNavigationState - Navigation tree state management
 *
 * Extracts state logic from NavigationTree for testability and reuse.
 * Handles accordion behavior, sub-tree memory, and optional persistence.
 *
 * @see plans/navtree-refinement.md
 */

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';

// =============================================================================
// Types
// =============================================================================

/** Per-context sub-tree expansion state */
export type SectionSubtreeState = Record<string, Set<string>>;

export interface NavigationState {
  /** Which context is currently expanded (null = none) */
  activeSection: string | null;
  /** Per-context sub-tree expansion state */
  sectionSubtreeState: SectionSubtreeState;
  /** Computed: all expanded paths (activeSection + its subtrees) */
  expandedPaths: Set<string>;
  /** Current focused path for keyboard navigation (null = no focus) */
  focusedPath: string | null;
}

export interface NavigationActions {
  /** Toggle a path (accordion for contexts, toggle for sub-paths) */
  toggle: (path: string) => void;
  /** Set active section directly (for URL-driven navigation) */
  setActiveSection: (section: string | null) => void;
  /** Expand paths within a section (for auto-expand on navigate) */
  expandPathsInSection: (section: string, paths: string[]) => void;
  /** Reset all state (collapse everything, clear persistence) */
  reset: () => void;
  /** Set focused path for keyboard navigation */
  setFocusedPath: (path: string | null) => void;
  /** Move focus to next/prev visible node */
  moveFocus: (direction: 'up' | 'down', visiblePaths: string[]) => void;
}

export interface UseNavigationStateOptions {
  /** Enable localStorage persistence (default: false) */
  persist?: boolean;
  /** Valid context names for accordion behavior */
  validContexts?: string[];
}

// =============================================================================
// Constants
// =============================================================================

const STORAGE_KEY = 'kgents:navtree:state';
const DEFAULT_CONTEXTS = ['world', 'self', 'concept', 'void', 'time'];

// =============================================================================
// Persistence Helpers
// =============================================================================

interface PersistedState {
  activeSection: string | null;
  sectionSubtreeState: Record<string, string[]>; // Sets serialized as arrays
}

function loadPersistedState(): PersistedState | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return null;
    return JSON.parse(stored) as PersistedState;
  } catch {
    return null;
  }
}

function savePersistedState(state: PersistedState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore storage errors (quota, private mode, etc.)
  }
}

function clearPersistedState(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
  } catch {
    // Ignore
  }
}

function deserializeSubtreeState(serialized: Record<string, string[]>): SectionSubtreeState {
  const result: SectionSubtreeState = {};
  for (const [key, arr] of Object.entries(serialized)) {
    result[key] = new Set(arr);
  }
  return result;
}

function serializeSubtreeState(state: SectionSubtreeState): Record<string, string[]> {
  const result: Record<string, string[]> = {};
  for (const [key, set] of Object.entries(state)) {
    result[key] = [...set];
  }
  return result;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Navigation state management hook.
 *
 * Provides accordion behavior for AGENTESE contexts with per-section
 * sub-tree memory. Optionally persists to localStorage.
 *
 * @example
 * ```tsx
 * const [state, actions] = useNavigationState({ persist: true });
 *
 * // Toggle a path (accordion for contexts, toggle for sub-paths)
 * actions.toggle('world.town.citizen');
 *
 * // Check if a path is expanded
 * const isExpanded = state.expandedPaths.has('world.town');
 *
 * // Reset everything
 * actions.reset();
 * ```
 */
export function useNavigationState(
  options: UseNavigationStateOptions = {}
): [NavigationState, NavigationActions] {
  const { persist = false, validContexts = DEFAULT_CONTEXTS } = options;

  // Load initial state from localStorage if persist is enabled
  const initialState = useMemo(() => {
    if (!persist) {
      return { activeSection: null, sectionSubtreeState: {} };
    }
    const persisted = loadPersistedState();
    if (!persisted) {
      return { activeSection: null, sectionSubtreeState: {} };
    }
    return {
      activeSection: persisted.activeSection,
      sectionSubtreeState: deserializeSubtreeState(persisted.sectionSubtreeState),
    };
  }, [persist]);

  // Core state
  const [activeSection, setActiveSectionInternal] = useState<string | null>(
    initialState.activeSection
  );
  const [sectionSubtreeState, setSectionSubtreeState] = useState<SectionSubtreeState>(
    initialState.sectionSubtreeState
  );
  const [focusedPath, setFocusedPath] = useState<string | null>(null);

  // Debounced persistence
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!persist) return;

    // Debounce saves to avoid thrashing localStorage
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    saveTimeoutRef.current = setTimeout(() => {
      savePersistedState({
        activeSection,
        sectionSubtreeState: serializeSubtreeState(sectionSubtreeState),
      });
    }, 300);

    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [persist, activeSection, sectionSubtreeState]);

  // Compute expanded paths from activeSection + sectionSubtreeState
  const expandedPaths = useMemo(() => {
    if (!activeSection) return new Set<string>();

    // Start with the context itself expanded
    const paths = new Set<string>([activeSection]);

    // Add any sub-trees that were expanded within this context
    const subtreeState = sectionSubtreeState[activeSection];
    if (subtreeState) {
      subtreeState.forEach((p) => paths.add(p));
    }

    return paths;
  }, [activeSection, sectionSubtreeState]);

  // ==========================================================================
  // Actions
  // ==========================================================================

  const setActiveSection = useCallback((section: string | null) => {
    setActiveSectionInternal(section);
  }, []);

  const expandPathsInSection = useCallback((section: string, paths: string[]) => {
    setSectionSubtreeState((prev) => ({
      ...prev,
      [section]: new Set([...(prev[section] || []), ...paths]),
    }));
  }, []);

  const toggle = useCallback(
    (path: string) => {
      const segments = path.split('.');
      const context = segments[0];

      // Is this a context-level toggle (e.g., "world", "self")?
      if (segments.length === 1 && validContexts.includes(context)) {
        // Accordion behavior: toggle this section
        setActiveSectionInternal((prev) => (prev === context ? null : context));
      } else {
        // Sub-path toggle: update the sub-tree state for the current section
        setSectionSubtreeState((prev) => {
          const currentSet = prev[context] || new Set<string>();
          const next = new Set(currentSet);

          if (next.has(path)) {
            next.delete(path);
          } else {
            next.add(path);
          }

          return { ...prev, [context]: next };
        });
      }
    },
    [validContexts]
  );

  const reset = useCallback(() => {
    setActiveSectionInternal(null);
    setSectionSubtreeState({});
    setFocusedPath(null);
    if (persist) {
      clearPersistedState();
    }
  }, [persist]);

  const moveFocus = useCallback((direction: 'up' | 'down', visiblePaths: string[]) => {
    if (visiblePaths.length === 0) return;

    setFocusedPath((current) => {
      if (!current) {
        // No current focus, start at first or last
        return direction === 'down' ? visiblePaths[0] : visiblePaths[visiblePaths.length - 1];
      }

      const currentIndex = visiblePaths.indexOf(current);
      if (currentIndex === -1) {
        // Current path not visible, reset to first
        return visiblePaths[0];
      }

      const nextIndex =
        direction === 'down'
          ? Math.min(currentIndex + 1, visiblePaths.length - 1)
          : Math.max(currentIndex - 1, 0);

      return visiblePaths[nextIndex];
    });
  }, []);

  // ==========================================================================
  // Return
  // ==========================================================================

  const state: NavigationState = useMemo(
    () => ({
      activeSection,
      sectionSubtreeState,
      expandedPaths,
      focusedPath,
    }),
    [activeSection, sectionSubtreeState, expandedPaths, focusedPath]
  );

  const actions: NavigationActions = useMemo(
    () => ({
      toggle,
      setActiveSection,
      expandPathsInSection,
      reset,
      setFocusedPath,
      moveFocus,
    }),
    [toggle, setActiveSection, expandPathsInSection, reset, setFocusedPath, moveFocus]
  );

  return [state, actions] as const;
}

export default useNavigationState;
