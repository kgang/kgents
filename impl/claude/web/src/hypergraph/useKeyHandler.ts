/**
 * useKeyHandler — Vim-like key handling for Hypergraph Emacs
 *
 * "Everything via keyboard, modes for context."
 *
 * This hook handles all keyboard input, dispatching to the appropriate
 * action based on current mode and key sequences.
 */

import React, { useCallback, useEffect, useRef, useState } from 'react';

import type { NavigationState, NavigationAction, KeySequence } from './types';
import { EDGE_TYPE_KEYS } from './types';

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
 * Multi-key sequences (g-prefixed graph navigation, z-prefixed portals, etc.)
 */
interface SequenceBinding {
  keys: string[];
  action:
    | NavigationAction
    // Graph navigation
    | 'GO_PARENT'
    | 'GO_CHILD'
    | 'GO_DEFINITION'
    | 'GO_REFERENCES'
    | 'GO_TESTS'
    // Mode switches
    | 'ENTER_EDGE'
    | 'ENTER_WITNESS'
    // Portal operations (zo/zc — vim fold-style)
    | 'PORTAL_OPEN'
    | 'PORTAL_CLOSE'
    | 'PORTAL_TOGGLE'
    | 'PORTAL_OPEN_ALL'
    | 'PORTAL_CLOSE_ALL';
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

  // Portal operations (z-prefix — vim fold-style)
  { keys: ['z', 'o'], action: 'PORTAL_OPEN', description: 'Open portal (zo)' },
  { keys: ['z', 'c'], action: 'PORTAL_CLOSE', description: 'Close portal (zc)' },
  { keys: ['z', 'a'], action: 'PORTAL_TOGGLE', description: 'Toggle portal (za)' },
  { keys: ['z', 'O'], action: 'PORTAL_OPEN_ALL', description: 'Open all portals (zO)' },
  { keys: ['z', 'C'], action: 'PORTAL_CLOSE_ALL', description: 'Close all portals (zC)' },
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

  /** Portal operations (zo/zc — inline edge expansion) */
  openPortal: () => void;
  closePortal: () => void;
  togglePortal: () => void;
  openAllPortals: () => void;
  closeAllPortals: () => void;

  /** Called when entering command mode (to focus input) */
  onEnterCommand?: () => void;

  /**
   * Called when entering INSERT mode.
   * This is where K-Block creation happens (async).
   * If not provided, dispatch(ENTER_INSERT) is called directly.
   */
  onEnterInsert?: () => void | Promise<void>;

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
    openPortal,
    closePortal,
    togglePortal,
    openAllPortals,
    closeAllPortals,
    onEnterCommand,
    onEnterInsert,
    enabled = true,
  } = options;

  // Track key sequence for multi-key bindings
  const sequenceRef = useRef<KeySequence>({
    keys: [],
    timeout: 1000, // 1 second to complete sequence
    position: 0,
    lastKeyTime: 0,
  });

  const [pendingKeys, setPendingKeys] = useState<string[]>([]);

  // Reset sequence on timeout
  const resetSequence = useCallback(() => {
    sequenceRef.current = {
      ...sequenceRef.current,
      keys: [],
      position: 0,
    };
    setPendingKeys([]);
  }, []);

  // =============================================================================
  // Normal Mode Handlers - Split into Sub-Functions
  // =============================================================================

  /**
   * Handle string actions (callbacks that don't dispatch)
   */
  const handleStringAction = useCallback(
    (action: string) => {
      switch (action) {
        // Navigation
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

        // Mode switches
        case 'ENTER_EDGE':
          dispatch({ type: 'ENTER_EDGE' });
          break;
        case 'ENTER_WITNESS':
          dispatch({ type: 'ENTER_WITNESS' });
          break;

        // Portal operations (zo/zc — vim fold-style)
        case 'PORTAL_OPEN':
          openPortal();
          break;
        case 'PORTAL_CLOSE':
          closePortal();
          break;
        case 'PORTAL_TOGGLE':
          togglePortal();
          break;
        case 'PORTAL_OPEN_ALL':
          openAllPortals();
          break;
        case 'PORTAL_CLOSE_ALL':
          closeAllPortals();
          break;
      }
    },
    [
      goParent,
      goChild,
      goDefinition,
      goReferences,
      goTests,
      dispatch,
      openPortal,
      closePortal,
      togglePortal,
      openAllPortals,
      closeAllPortals,
    ]
  );

  /**
   * Try to match or advance a key sequence
   * Returns true if handled (matched or prefix)
   */
  const trySequence = useCallback(
    (e: KeyboardEvent, key: string, now: number): boolean => {
      const pending = [...sequenceRef.current.keys, key];

      // Check for complete sequence match
      const matchingSequence = NORMAL_MODE_SEQUENCES.find(
        (seq) => seq.keys.length === pending.length && seq.keys.every((k, i) => k === pending[i])
      );

      if (matchingSequence) {
        e.preventDefault();
        resetSequence();
        const action = matchingSequence.action;
        if (typeof action === 'string') {
          handleStringAction(action);
        } else {
          dispatch(action);
        }
        return true;
      }

      // Check for sequence prefix (waiting for more keys)
      const isPrefix = NORMAL_MODE_SEQUENCES.some(
        (seq) =>
          seq.keys.length > pending.length &&
          seq.keys.slice(0, pending.length).every((k, i) => k === pending[i])
      );

      if (isPrefix) {
        e.preventDefault();
        sequenceRef.current = { ...sequenceRef.current, keys: pending, lastKeyTime: now };
        setPendingKeys(pending);
        return true;
      }

      // Reset sequence if not a prefix
      if (sequenceRef.current.keys.length > 0) {
        resetSequence();
      }

      return false;
    },
    [resetSequence, handleStringAction, dispatch]
  );

  /**
   * Try simple (single-key) bindings
   */
  const trySimpleBinding = useCallback(
    (e: KeyboardEvent, key: string): boolean => {
      // Skip if modifier keys are held (except for specific cases)
      if (e.ctrlKey || e.metaKey || e.altKey) {
        return false;
      }

      const binding = NORMAL_MODE_BINDINGS[key];
      if (!binding) return false;

      e.preventDefault();

      // Special handling for command mode
      if (binding.action.type === 'ENTER_COMMAND') {
        dispatch(binding.action);
        onEnterCommand?.();
      } else if (binding.action.type === 'ENTER_INSERT') {
        // K-Block creation happens via onEnterInsert callback
        if (onEnterInsert) {
          void onEnterInsert();
        } else {
          dispatch(binding.action);
        }
      } else {
        dispatch(binding.action);
      }

      return true;
    },
    [dispatch, onEnterCommand, onEnterInsert]
  );

  /**
   * Handle paragraph motion ({ and })
   */
  const handleParagraphMotion = useCallback(
    (direction: 'forward' | 'backward') => {
      const content = state.currentNode?.content || '';
      const lines = content.split('\n');
      const currentLine = Math.min(state.cursor.line, lines.length - 1);

      if (direction === 'forward') {
        // Skip current blank lines
        let i = currentLine;
        while (i < lines.length && lines[i].trim() === '') i++;
        // Find next blank line
        while (i < lines.length && lines[i].trim() !== '') i++;

        if (i < lines.length) {
          dispatch({ type: 'GOTO_LINE', line: i });
        } else {
          dispatch({ type: 'GOTO_END' });
        }
      } else {
        // Skip current blank lines
        let i = currentLine;
        while (i > 0 && lines[i].trim() === '') i--;
        // Find previous blank line
        while (i > 0 && lines[i].trim() !== '') i--;
        dispatch({ type: 'GOTO_LINE', line: i });
      }
    },
    [state, dispatch]
  );

  /**
   * Try special keys (G, {, }, Ctrl+o)
   */
  const trySpecialKey = useCallback(
    (e: KeyboardEvent, key: string): boolean => {
      // Ctrl+o - go back
      if (e.ctrlKey && key === 'o') {
        e.preventDefault();
        dispatch({ type: 'GO_BACK' });
        return true;
      }

      // G - go to end
      if (key === 'G') {
        e.preventDefault();
        dispatch({ type: 'GOTO_END' });
        return true;
      }

      // } - next paragraph
      if (key === '}') {
        e.preventDefault();
        handleParagraphMotion('forward');
        return true;
      }

      // { - previous paragraph
      if (key === '{') {
        e.preventDefault();
        handleParagraphMotion('backward');
        return true;
      }

      return false;
    },
    [dispatch, handleParagraphMotion]
  );

  const handleNormalMode = useCallback(
    (e: KeyboardEvent, key: string, now: number) => {
      // Try handlers in order
      if (trySequence(e, key, now)) return;
      if (trySimpleBinding(e, key)) return;
      trySpecialKey(e, key);
    },
    [trySequence, trySimpleBinding, trySpecialKey]
  );

  // =============================================================================
  // Edge Mode Handlers - Split by Phase
  // =============================================================================

  const handleEdgeSelectType = useCallback(
    (e: KeyboardEvent, key: string): boolean => {
      const edgeType = EDGE_TYPE_KEYS[key.toLowerCase()];
      if (edgeType) {
        e.preventDefault();
        dispatch({ type: 'EDGE_SELECT_TYPE', edgeType });
        return true;
      }
      return false;
    },
    [dispatch]
  );

  const handleEdgeSelectTarget = useCallback(
    (e: KeyboardEvent, key: string): boolean => {
      // Navigate using j/k like normal mode
      if (key === 'j') {
        e.preventDefault();
        dispatch({ type: 'GO_SIBLING', direction: 1 });
        return true;
      }
      if (key === 'k') {
        e.preventDefault();
        dispatch({ type: 'GO_SIBLING', direction: -1 });
        return true;
      }

      // Enter selects current node as target
      if (key === 'Enter' && state.currentNode) {
        e.preventDefault();
        dispatch({
          type: 'EDGE_SELECT_TARGET',
          targetId: state.currentNode.path,
          targetLabel: state.currentNode.title || state.currentNode.path.split('/').pop() || '',
        });
        return true;
      }

      return false;
    },
    [state, dispatch]
  );

  const handleEdgeConfirm = useCallback(
    (e: KeyboardEvent, key: string): boolean => {
      if (key === 'y' || key === 'Enter') {
        e.preventDefault();
        dispatch({ type: 'EDGE_CONFIRM' });
        return true;
      }
      if (key === 'n' || key === 'Backspace') {
        e.preventDefault();
        dispatch({ type: 'EDGE_CANCEL' });
        return true;
      }
      return false;
    },
    [dispatch]
  );

  const handleEdgeMode = useCallback(
    (e: KeyboardEvent, key: string) => {
      const { edgePending } = state;
      if (!edgePending) return;

      // Dispatch to phase-specific handlers
      if (edgePending.phase === 'select-type') {
        handleEdgeSelectType(e, key);
      } else if (edgePending.phase === 'select-target') {
        handleEdgeSelectTarget(e, key);
      } else if (edgePending.phase === 'confirm') {
        handleEdgeConfirm(e, key);
      }
    },
    [state, handleEdgeSelectType, handleEdgeSelectTarget, handleEdgeConfirm]
  );

  const handleWitnessMode = useCallback((_e: KeyboardEvent, _key: string) => {
    // Witness mode bindings will be added in Phase 5
    // For now, Escape is the only binding (handled universally above)
  }, []);

  // =============================================================================
  // Key Handler Entry Point
  // =============================================================================

  /**
   * Check if we should skip key handling (in input fields, disabled, etc)
   */
  const shouldSkipKey = useCallback(
    (e: KeyboardEvent): boolean => {
      if (!enabled) return true;

      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        // In INSERT mode, let textarea handle everything except Escape
        if (state.mode === 'INSERT' && e.key !== 'Escape') {
          return true;
        }
        // In COMMAND mode, only handle Escape and Enter
        if (state.mode === 'COMMAND' && e.key !== 'Escape' && e.key !== 'Enter') {
          return true;
        }
      }

      return false;
    },
    [enabled, state.mode]
  );

  /**
   * Dispatch to mode-specific handlers
   */
  const dispatchToModeHandler = useCallback(
    (e: KeyboardEvent, key: string, now: number) => {
      switch (state.mode) {
        case 'NORMAL':
          handleNormalMode(e, key, now);
          break;
        case 'INSERT':
          // INSERT mode: only Escape is handled (in handleKey)
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
    [state.mode, handleNormalMode, handleEdgeMode, handleWitnessMode]
  );

  // Handle a single keypress
  const handleKey = useCallback(
    (e: KeyboardEvent) => {
      if (shouldSkipKey(e)) return;

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
        if (state.mode !== 'NORMAL') {
          dispatch({ type: 'SET_MODE', mode: 'NORMAL' });
          resetSequence();
        }
        return;
      }

      // Dispatch to mode-specific handler
      dispatchToModeHandler(e, key, now);
    },
    [shouldSkipKey, state.mode, dispatch, resetSequence, dispatchToModeHandler]
  );

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
