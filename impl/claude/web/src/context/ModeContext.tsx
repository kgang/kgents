/**
 * Mode Context: Global editing mode state
 *
 * Manages the six-mode editing system for hypergraph editing.
 * Provides mode state, transitions, and history tracking.
 *
 * @see docs/skills/hypergraph-editor.md - Six-mode modal editing
 * @see src/types/mode.ts - Mode definitions and utilities
 */

import { createContext, useContext, useState, useCallback, useMemo, ReactNode, useEffect } from 'react';
import type { Mode, ModeTransition } from '@/types/mode';
import { getModeTrigger } from '@/types/mode';

// =============================================================================
// Context Types
// =============================================================================

export interface ModeContextValue {
  /** Current active mode */
  currentMode: Mode;

  /** Transition to a new mode */
  setMode: (mode: Mode, reason?: string) => void;

  /** Return to NORMAL mode (Escape handler) */
  returnToNormal: () => void;

  /** Mode transition history (last 10) */
  history: ModeTransition[];

  /** Previous mode (for toggling) */
  previousMode: Mode | null;

  /** Whether mode transitions are enabled */
  enabled: boolean;

  /** Enable/disable mode transitions */
  setEnabled: (enabled: boolean) => void;
}

// =============================================================================
// Context
// =============================================================================

const ModeContext = createContext<ModeContextValue | null>(null);

// =============================================================================
// Provider
// =============================================================================

export interface ModeProviderProps {
  children: ReactNode;

  /** Initial mode (default: NORMAL) */
  initialMode?: Mode;

  /** Enable mode transitions immediately (default: true) */
  enabled?: boolean;

  /** Callback when mode changes */
  onModeChange?: (transition: ModeTransition) => void;

  /** Enable global keyboard shortcuts (default: true) */
  enableKeyboard?: boolean;
}

export function ModeProvider({
  children,
  initialMode = 'NORMAL',
  enabled: enabledProp = true,
  onModeChange,
  enableKeyboard = true,
}: ModeProviderProps) {
  const [currentMode, setCurrentModeInternal] = useState<Mode>(initialMode);
  const [previousMode, setPreviousMode] = useState<Mode | null>(null);
  const [history, setHistory] = useState<ModeTransition[]>([]);
  const [enabled, setEnabled] = useState(enabledProp);

  // Transition to new mode
  const setMode = useCallback(
    (mode: Mode, reason?: string) => {
      if (!enabled) return;
      if (mode === currentMode) return;

      const transition: ModeTransition = {
        from: currentMode,
        to: mode,
        timestamp: Date.now(),
        reason,
      };

      setPreviousMode(currentMode);
      setCurrentModeInternal(mode);

      // Add to history (keep last 10)
      setHistory((prev) => [transition, ...prev].slice(0, 10));

      // Fire callback
      onModeChange?.(transition);
    },
    [currentMode, enabled, onModeChange]
  );

  // Return to NORMAL (Escape key)
  const returnToNormal = useCallback(() => {
    setMode('NORMAL', 'escape');
  }, [setMode]);

  // Global keyboard handler
  useEffect(() => {
    if (!enableKeyboard || !enabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if in input elements (unless in COMMAND/INSERT/WITNESS modes)
      const target = e.target as HTMLElement;
      const inInput =
        target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable;

      // Always allow Escape to return to NORMAL
      if (e.key === 'Escape') {
        e.preventDefault();
        returnToNormal();
        return;
      }

      // Only process mode triggers from NORMAL mode
      if (currentMode !== 'NORMAL') return;

      // Ignore if in input and not explicitly handling
      if (inInput) return;

      // Check for mode trigger
      const triggerMode = getModeTrigger(e.key);
      if (triggerMode) {
        e.preventDefault();
        setMode(triggerMode, `keyboard:${e.key}`);
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [currentMode, enableKeyboard, enabled, setMode, returnToNormal]);

  const value = useMemo<ModeContextValue>(
    () => ({
      currentMode,
      setMode,
      returnToNormal,
      history,
      previousMode,
      enabled,
      setEnabled,
    }),
    [currentMode, setMode, returnToNormal, history, previousMode, enabled]
  );

  return <ModeContext.Provider value={value}>{children}</ModeContext.Provider>;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook to access mode context.
 *
 * @throws if used outside ModeProvider
 */
export function useModeContext(): ModeContextValue {
  const context = useContext(ModeContext);
  if (!context) {
    throw new Error('useModeContext must be used within a ModeProvider');
  }
  return context;
}

/**
 * Safe hook that returns null outside provider
 */
export function useModeContextSafe(): ModeContextValue | null {
  return useContext(ModeContext);
}

// =============================================================================
// Exports
// =============================================================================

export { ModeContext };
