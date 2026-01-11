/**
 * useSidebarState — Persist and manage sidebar panel states
 *
 * "The Hypergraph Editor IS the app. Everything else is a sidebar."
 *
 * Uses localStorage for persistence across sessions with debounced writes.
 * Controls visibility and width of left (Files) and right (Chat) sidebars.
 *
 * Keybindings:
 * - Ctrl+B: Toggle left sidebar (Files/Director)
 * - Ctrl+J: Toggle right sidebar (Chat)
 */

import { useCallback, useEffect, useRef, useState } from 'react';

const STORAGE_KEY = 'kgents-sidebar-state';
const DEBOUNCE_MS = 300;
const MIN_WIDTH = 200;
const MAX_WIDTH = 600;

export interface SidebarState {
  /** Left sidebar (Files/Director) open state */
  leftOpen: boolean;
  /** Right sidebar (Chat) open state */
  rightOpen: boolean;
  /** Left sidebar width in pixels (for future resize support) */
  leftWidth: number;
  /** Right sidebar width in pixels (for future resize support) */
  rightWidth: number;
}

const DEFAULT_STATE: SidebarState = {
  leftOpen: true,
  rightOpen: false,
  leftWidth: 320,
  rightWidth: 360,
};

/**
 * Clamp a numeric value to bounds, returning undefined if invalid
 */
function clamp(value: unknown, min: number, max: number): number | undefined {
  if (typeof value !== 'number' || isNaN(value)) return undefined;
  return Math.max(min, Math.min(max, value));
}

/**
 * Load persisted state from localStorage with validation
 */
function loadPersistedState(): Partial<SidebarState> {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (!stored) return {};
    const parsed = JSON.parse(stored);
    if (typeof parsed !== 'object' || parsed === null) return {};

    // Validate each field individually
    return {
      leftOpen: typeof parsed.leftOpen === 'boolean' ? parsed.leftOpen : undefined,
      rightOpen: typeof parsed.rightOpen === 'boolean' ? parsed.rightOpen : undefined,
      leftWidth: clamp(parsed.leftWidth, MIN_WIDTH, MAX_WIDTH),
      rightWidth: clamp(parsed.rightWidth, MIN_WIDTH, MAX_WIDTH),
    };
  } catch {
    // localStorage may be unavailable (SSR, incognito) or data corrupted
    return {};
  }
}

/**
 * Save state to localStorage (silently fails if unavailable)
 */
function savePersistedState(state: SidebarState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // Ignore - localStorage may be full or unavailable
  }
}

export interface UseSidebarStateReturn {
  /** Current sidebar state */
  state: SidebarState;
  /** Toggle left sidebar */
  toggleLeft: () => void;
  /** Toggle right sidebar */
  toggleRight: () => void;
  /** Set left sidebar open state */
  setLeftOpen: (open: boolean) => void;
  /** Set right sidebar open state */
  setRightOpen: (open: boolean) => void;
  /** Set left sidebar width */
  setLeftWidth: (width: number) => void;
  /** Set right sidebar width */
  setRightWidth: (width: number) => void;
}

export function useSidebarState(): UseSidebarStateReturn {
  // Initialize state from localStorage with validation
  const [state, setState] = useState<SidebarState>(() => {
    const persisted = loadPersistedState();
    // Merge persisted values with defaults, filtering out undefined
    return {
      leftOpen: persisted.leftOpen ?? DEFAULT_STATE.leftOpen,
      rightOpen: persisted.rightOpen ?? DEFAULT_STATE.rightOpen,
      leftWidth: persisted.leftWidth ?? DEFAULT_STATE.leftWidth,
      rightWidth: persisted.rightWidth ?? DEFAULT_STATE.rightWidth,
    };
  });

  // Track timeout for cleanup
  const saveTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  // Debounced persist to localStorage whenever state changes
  useEffect(() => {
    // Clear any pending save
    if (saveTimeoutRef.current) {
      clearTimeout(saveTimeoutRef.current);
    }

    // Schedule debounced save
    saveTimeoutRef.current = setTimeout(() => {
      savePersistedState(state);
    }, DEBOUNCE_MS);

    // Cleanup on unmount or state change
    return () => {
      if (saveTimeoutRef.current) {
        clearTimeout(saveTimeoutRef.current);
      }
    };
  }, [state.leftOpen, state.rightOpen, state.leftWidth, state.rightWidth]);

  const toggleLeft = useCallback(() => {
    setState((prev) => ({ ...prev, leftOpen: !prev.leftOpen }));
  }, []);

  const toggleRight = useCallback(() => {
    setState((prev) => ({ ...prev, rightOpen: !prev.rightOpen }));
  }, []);

  const setLeftOpen = useCallback((open: boolean) => {
    setState((prev) => ({ ...prev, leftOpen: open }));
  }, []);

  const setRightOpen = useCallback((open: boolean) => {
    setState((prev) => ({ ...prev, rightOpen: open }));
  }, []);

  const setLeftWidth = useCallback((width: number) => {
    setState((prev) => ({ ...prev, leftWidth: Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, width)) }));
  }, []);

  const setRightWidth = useCallback((width: number) => {
    setState((prev) => ({ ...prev, rightWidth: Math.max(MIN_WIDTH, Math.min(MAX_WIDTH, width)) }));
  }, []);

  return {
    state,
    toggleLeft,
    toggleRight,
    setLeftOpen,
    setRightOpen,
    setLeftWidth,
    setRightWidth,
  };
}
