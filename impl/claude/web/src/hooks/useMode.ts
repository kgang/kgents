/**
 * useMode: Convenient hook for mode state and transitions
 *
 * Provides shorthand access to mode context with additional utilities.
 * Use this instead of useModeContext for cleaner component code.
 *
 * @see src/context/ModeContext.tsx - Mode context provider
 * @see src/types/mode.ts - Mode definitions
 */

import { useCallback } from 'react';
import { useModeContext } from '@/context/ModeContext';
import type { Mode } from '@/types/mode';
import { getModeColor, getModeDefinition, modecapturesInput, modeBlocksNavigation } from '@/types/mode';

// =============================================================================
// Hook Return Type
// =============================================================================

export interface UseModeReturn {
  /** Current active mode */
  mode: Mode;

  /** Whether in NORMAL mode */
  isNormal: boolean;

  /** Whether in INSERT mode */
  isInsert: boolean;

  /** Whether in EDGE mode */
  isEdge: boolean;

  /** Whether in VISUAL mode */
  isVisual: boolean;

  /** Whether in COMMAND mode */
  isCommand: boolean;

  /** Whether in WITNESS mode */
  isWitness: boolean;

  /** Transition to a new mode */
  setMode: (mode: Mode, reason?: string) => void;

  /** Return to NORMAL mode */
  toNormal: () => void;

  /** Transition to INSERT mode */
  toInsert: () => void;

  /** Transition to EDGE mode */
  toEdge: () => void;

  /** Transition to VISUAL mode */
  toVisual: () => void;

  /** Transition to COMMAND mode */
  toCommand: () => void;

  /** Transition to WITNESS mode */
  toWitness: () => void;

  /** Whether current mode captures keyboard input */
  capturesInput: boolean;

  /** Whether current mode blocks navigation */
  blocksNavigation: boolean;

  /** Current mode color (for styling) */
  color: string;

  /** Current mode label */
  label: string;

  /** Current mode description */
  description: string;

  /** Mode transition history */
  history: Array<{ from: Mode; to: Mode; timestamp: number; reason?: string }>;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for mode state and transitions.
 *
 * @example
 * ```tsx
 * function MyComponent() {
 *   const { mode, isNormal, toInsert, toNormal } = useMode();
 *
 *   if (isNormal) {
 *     return <button onClick={toInsert}>Create K-Block (i)</button>;
 *   }
 *
 *   return <KBlockEditor onSave={toNormal} onCancel={toNormal} />;
 * }
 * ```
 */
export function useMode(): UseModeReturn {
  const ctx = useModeContext();

  const { currentMode: mode, setMode, history } = ctx;

  // Mode checkers
  const isNormal = mode === 'NORMAL';
  const isInsert = mode === 'INSERT';
  const isEdge = mode === 'EDGE';
  const isVisual = mode === 'VISUAL';
  const isCommand = mode === 'COMMAND';
  const isWitness = mode === 'WITNESS';

  // Mode transitions
  const toNormal = useCallback(() => setMode('NORMAL', 'manual'), [setMode]);
  const toInsert = useCallback(() => setMode('INSERT', 'manual'), [setMode]);
  const toEdge = useCallback(() => setMode('EDGE', 'manual'), [setMode]);
  const toVisual = useCallback(() => setMode('VISUAL', 'manual'), [setMode]);
  const toCommand = useCallback(() => setMode('COMMAND', 'manual'), [setMode]);
  const toWitness = useCallback(() => setMode('WITNESS', 'manual'), [setMode]);

  // Mode metadata
  const definition = getModeDefinition(mode);
  const capturesInput = modecapturesInput(mode);
  const blocksNavigation = modeBlocksNavigation(mode);
  const color = getModeColor(mode);

  return {
    mode,
    isNormal,
    isInsert,
    isEdge,
    isVisual,
    isCommand,
    isWitness,
    setMode,
    toNormal,
    toInsert,
    toEdge,
    toVisual,
    toCommand,
    toWitness,
    capturesInput,
    blocksNavigation,
    color,
    label: definition.label,
    description: definition.description,
    history,
  };
}

export default useMode;
