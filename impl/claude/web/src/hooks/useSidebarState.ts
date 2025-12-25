/**
 * useSidebarState — Persist and manage sidebar panel states
 *
 * "The Hypergraph Editor IS the app. Everything else is a sidebar."
 *
 * Uses localStorage for persistence across sessions.
 * Controls visibility and width of left (Files) and right (Chat) sidebars.
 *
 * Keybindings:
 * - Ctrl+B: Toggle left sidebar (Files/Director)
 * - Ctrl+J: Toggle right sidebar (Chat)
 */

import { useCallback, useEffect, useState } from 'react';

const STORAGE_KEY = 'kgents:sidebar-state';

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
  leftWidth: 280,
  rightWidth: 360,
};

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
  const [state, setState] = useState<SidebarState>(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (stored) {
        const parsed = JSON.parse(stored);
        return { ...DEFAULT_STATE, ...parsed };
      }
    } catch (e) {
      console.warn('[useSidebarState] Failed to parse localStorage:', e);
    }
    return DEFAULT_STATE;
  });

  // Persist to localStorage whenever state changes
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch (e) {
      console.warn('[useSidebarState] Failed to persist to localStorage:', e);
    }
  }, [state]);

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
    setState((prev) => ({ ...prev, leftWidth: Math.max(200, Math.min(600, width)) }));
  }, []);

  const setRightWidth = useCallback((width: number) => {
    setState((prev) => ({ ...prev, rightWidth: Math.max(280, Math.min(600, width)) }));
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
