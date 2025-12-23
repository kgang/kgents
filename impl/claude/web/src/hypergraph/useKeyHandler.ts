/**
 * useKeyHandler — Vim-like key handling for Hypergraph Emacs
 *
 * "Everything via keyboard, modes for context."
 *
 * This hook handles all keyboard input, dispatching to the appropriate
 * action based on current mode and key sequences.
 */

import { useCallback, useEffect, useRef } from 'react';

import type { NavigationState, NavigationAction, KeySequence } from './types';

// =============================================================================
// Key Binding Definitions
// =============================================================================

/**
 * Simple keybinding: key → action
 */
type SimpleBinding = {
  action: NavigationAction;
  description: string;
};

/**
 * Key bindings per mode.
 */
const NORMAL_MODE_BINDINGS: Record<string, SimpleBinding> = {
  // Cursor movement (within node)
  j: { action: { type: 'MOVE_LINE', delta: 1 }, description: 'Move down' },
  k: { action: { type: 'MOVE_LINE', delta: -1 }, description: 'Move up' },
  h: { action: { type: 'MOVE_COLUMN', delta: -1 }, description: 'Move left' },
  l: { action: { type: 'MOVE_COLUMN', delta: 1 }, description: 'Move right' },

  // Enter insert mode
  i: { action: { type: 'ENTER_INSERT', position: 'before' }, description: 'Insert before cursor' },
  a: { action: { type: 'ENTER_INSERT', position: 'after' }, description: 'Insert after cursor' },
  I: {
    action: { type: 'ENTER_INSERT', position: 'line_start' },
    description: 'Insert at line start',
  },
  A: { action: { type: 'ENTER_INSERT', position: 'line_end' }, description: 'Insert at line end' },
  o: { action: { type: 'ENTER_INSERT', position: 'below' }, description: 'Open line below' },
  O: { action: { type: 'ENTER_INSERT', position: 'above' }, description: 'Open line above' },

  // Mode switches
  ':': { action: { type: 'ENTER_COMMAND' }, description: 'Enter command mode' },
};

/**
 * Multi-key sequences (g-prefixed graph navigation, etc.)
 */
interface SequenceBinding {
  keys: string[];
  action:
    | NavigationAction
    | 'GO_PARENT'
    | 'GO_CHILD'
    | 'GO_DEFINITION'
    | 'GO_REFERENCES'
    | 'GO_TESTS'
    | 'ENTER_EDGE'
    | 'ENTER_WITNESS';
  description: string;
}

const NORMAL_MODE_SEQUENCES: SequenceBinding[] = [
  // Graph navigation (g-prefix)
  { keys: ['g', 'h'], action: 'GO_PARENT', description: 'Go to parent (gh)' },
  { keys: ['g', 'l'], action: 'GO_CHILD', description: 'Go to child (gl)' },
  {
    keys: ['g', 'j'],
    action: { type: 'GO_SIBLING', direction: 1 },
    description: 'Next sibling (gj)',
  },
  {
    keys: ['g', 'k'],
    action: { type: 'GO_SIBLING', direction: -1 },
    description: 'Prev sibling (gk)',
  },
  { keys: ['g', 'd'], action: 'GO_DEFINITION', description: 'Go to definition (gd)' },
  { keys: ['g', 'r'], action: 'GO_REFERENCES', description: 'Go to references (gr)' },
  { keys: ['g', 't'], action: 'GO_TESTS', description: 'Go to tests (gt)' },
  { keys: ['g', 'e'], action: 'ENTER_EDGE', description: 'Enter edge mode (ge)' },
  { keys: ['g', 'w'], action: 'ENTER_WITNESS', description: 'Enter witness mode (gw)' },

  // gg - go to start
  { keys: ['g', 'g'], action: { type: 'GOTO_START' }, description: 'Go to start (gg)' },
];

// INSERT, EDGE, COMMAND, WITNESS mode bindings will be added in later phases
// For now, these modes are handled specially (INSERT = textarea, COMMAND = CommandLine component)

// =============================================================================
// Hook Types
// =============================================================================

export interface UseKeyHandlerOptions {
  /** Current navigation state */
  state: NavigationState;

  /** Dispatch action */
  dispatch: React.Dispatch<NavigationAction>;

  /** Navigation helpers (for complex actions) */
  goParent: () => void;
  goChild: () => void;
  goDefinition: () => void;
  goReferences: () => void;
  goTests: () => void;

  /** Called when entering command mode (to focus input) */
  onEnterCommand?: () => void;

  /** Called when command is submitted */
  onCommand?: (command: string) => void;

  /** Whether the editor is focused */
  enabled?: boolean;
}

export interface UseKeyHandlerResult {
  /** Current key sequence (for display) */
  pendingSequence: string;

  /** Reset pending sequence */
  resetSequence: () => void;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useKeyHandler(options: UseKeyHandlerOptions): UseKeyHandlerResult {
  const {
    state,
    dispatch,
    goParent,
    goChild,
    goDefinition,
    goReferences,
    goTests,
    onEnterCommand,
    enabled = true,
  } = options;

  // Track key sequence for multi-key bindings
  const sequenceRef = useRef<KeySequence>({
    keys: [],
    timeout: 1000, // 1 second to complete sequence
    position: 0,
    lastKeyTime: 0,
  });

  const [pendingKeys, setPendingKeys] = React.useState<string[]>([]);

  // Reset sequence on timeout
  const resetSequence = useCallback(() => {
    sequenceRef.current = {
      ...sequenceRef.current,
      keys: [],
      position: 0,
    };
    setPendingKeys([]);
  }, []);

  // Handle a single keypress
  const handleKey = useCallback(
    (e: KeyboardEvent) => {
      // Skip if not enabled or if in an input field
      if (!enabled) return;
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        // In INSERT mode, let textarea handle it
        if (state.mode === 'INSERT' && e.key !== 'Escape') {
          return;
        }
        // In COMMAND mode, only handle Escape
        if (state.mode === 'COMMAND' && e.key !== 'Escape' && e.key !== 'Enter') {
          return;
        }
      }

      const { mode } = state;
      const key = e.key;
      const now = Date.now();

      // Check for timeout on pending sequence
      if (
        sequenceRef.current.keys.length > 0 &&
        now - sequenceRef.current.lastKeyTime > sequenceRef.current.timeout
      ) {
        resetSequence();
      }

      // Universal: Escape always exits to NORMAL
      if (key === 'Escape') {
        e.preventDefault();
        if (mode !== 'NORMAL') {
          dispatch({ type: 'SET_MODE', mode: 'NORMAL' });
          resetSequence();
        }
        return;
      }

      // Mode-specific handling
      switch (mode) {
        case 'NORMAL':
          handleNormalMode(e, key, now);
          break;
        case 'INSERT':
          // INSERT mode: only Escape is handled (above)
          break;
        case 'COMMAND':
          // COMMAND mode: handled by CommandLine component
          break;
        case 'EDGE':
          handleEdgeMode(e, key);
          break;
        case 'WITNESS':
          handleWitnessMode(e, key);
          break;
        case 'VISUAL':
          // VISUAL mode (Phase 6)
          break;
      }
    },
    [enabled, state, dispatch, resetSequence]
  );

  const handleNormalMode = useCallback(
    (e: KeyboardEvent, key: string, now: number) => {
      // First check if we're building a sequence
      const pending = [...sequenceRef.current.keys, key];

      // Check for sequence match
      const matchingSequence = NORMAL_MODE_SEQUENCES.find(
        (seq) => seq.keys.length === pending.length && seq.keys.every((k, i) => k === pending[i])
      );

      if (matchingSequence) {
        e.preventDefault();
        resetSequence();

        // Handle special action types
        const action = matchingSequence.action;
        if (typeof action === 'string') {
          switch (action) {
            case 'GO_PARENT':
              goParent();
              break;
            case 'GO_CHILD':
              goChild();
              break;
            case 'GO_DEFINITION':
              goDefinition();
              break;
            case 'GO_REFERENCES':
              goReferences();
              break;
            case 'GO_TESTS':
              goTests();
              break;
            case 'ENTER_EDGE':
              dispatch({ type: 'ENTER_EDGE' });
              break;
            case 'ENTER_WITNESS':
              dispatch({ type: 'ENTER_WITNESS' });
              break;
          }
        } else {
          dispatch(action);
        }
        return;
      }

      // Check for sequence prefix (waiting for more keys)
      const isPrefix = NORMAL_MODE_SEQUENCES.some(
        (seq) =>
          seq.keys.length > pending.length &&
          seq.keys.slice(0, pending.length).every((k, i) => k === pending[i])
      );

      if (isPrefix) {
        e.preventDefault();
        sequenceRef.current = {
          ...sequenceRef.current,
          keys: pending,
          lastKeyTime: now,
        };
        setPendingKeys(pending);
        return;
      }

      // Reset sequence if not a prefix
      if (sequenceRef.current.keys.length > 0) {
        resetSequence();
      }

      // Check for simple binding
      const binding = NORMAL_MODE_BINDINGS[key];
      if (binding) {
        e.preventDefault();

        // Special handling for command mode
        if (binding.action.type === 'ENTER_COMMAND') {
          dispatch(binding.action);
          onEnterCommand?.();
        } else {
          dispatch(binding.action);
        }
        return;
      }

      // G - go to end
      if (key === 'G') {
        e.preventDefault();
        dispatch({ type: 'GOTO_END' });
        return;
      }

      // Ctrl+o - go back
      if (e.ctrlKey && key === 'o') {
        e.preventDefault();
        dispatch({ type: 'GO_BACK' });
      }
    },
    [
      dispatch,
      goParent,
      goChild,
      goDefinition,
      goReferences,
      goTests,
      onEnterCommand,
      resetSequence,
    ]
  );

  const handleEdgeMode = useCallback((_e: KeyboardEvent, _key: string) => {
    // Edge mode bindings will be added in Phase 4
    // For now, Escape is the only binding (handled universally above)
  }, []);

  const handleWitnessMode = useCallback((_e: KeyboardEvent, _key: string) => {
    // Witness mode bindings will be added in Phase 5
    // For now, Escape is the only binding (handled universally above)
  }, []);

  // Attach global key handler
  useEffect(() => {
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [handleKey]);

  return {
    pendingSequence: pendingKeys.join(''),
    resetSequence,
  };
}

// Need React import for useState
import React from 'react';
