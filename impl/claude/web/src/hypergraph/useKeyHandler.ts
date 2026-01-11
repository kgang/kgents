/**
 * useKeyHandler — Vim-like modal key handling for Membrane Editor
 *
 * "Tasteful > feature-complete. Take the modal concept, not the cruft."
 *
 * Architecture:
 * - Declarative binding registry (BINDINGS)
 * - Mode-specific filtering
 * - Sequence handling for multi-key (g-prefix, z-prefix)
 * - Clean separation: NORMAL navigates graph, INSERT delegates to CodeMirror
 *
 * Key Philosophy:
 * - NORMAL mode = Reader view (readonly CodeMirror)
 *   → j/k scroll viewport (not cursor movement)
 *   → {/} paragraph navigation
 *   → Graph navigation (gh/gl/gj/gk), portal ops (zo/zc), mode switches
 *   → ? shows help panel
 * - INSERT mode = Editor view (editable CodeMirror)
 *   → All keys pass through to CodeMirror EXCEPT Escape
 * - EDGE/WITNESS = Special purpose modes with limited bindings
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import type { NavigationState, NavigationAction, EdgeType } from './state/types';
import { EDGE_TYPE_KEYS } from './state/types';

// =============================================================================
// Binding Registry — The Single Source of Truth
// =============================================================================

type ActionType =
  // Callbacks (resolved via actions map)
  | 'GO_PARENT'
  | 'GO_CHILD'
  | 'GO_DEFINITION'
  | 'GO_REFERENCES'
  | 'GO_TESTS'
  | 'GO_DERIVATION_PARENT'
  | 'GO_DERIVATION_CHILD'
  | 'GO_DERIVATION_NEXT_SIBLING'
  | 'GO_DERIVATION_PREV_SIBLING'
  | 'GO_TO_GENESIS'
  | 'SHOW_CONFIDENCE'
  | 'PORTAL_OPEN'
  | 'PORTAL_CLOSE'
  | 'PORTAL_TOGGLE'
  | 'PORTAL_OPEN_ALL'
  | 'PORTAL_CLOSE_ALL'
  | 'ENTER_INSERT'
  | 'ENTER_COMMAND'
  | 'SHOW_HELP'
  // Scroll navigation (reader mode)
  | 'SCROLL_DOWN'
  | 'SCROLL_UP'
  | 'SCROLL_PARAGRAPH_DOWN'
  | 'SCROLL_PARAGRAPH_UP'
  | 'SCROLL_TO_TOP'
  | 'SCROLL_TO_BOTTOM'
  // Decision stream (witness history)
  | 'TOGGLE_DECISION_STREAM'
  // Analysis quadrant
  | 'TOGGLE_ANALYSIS_QUADRANT'
  // Edge metadata panel
  | 'TOGGLE_EDGE_PANEL'
  // Derivation inspector panel
  | 'TOGGLE_DERIVATION_INSPECTOR'
  // Loss-gradient navigation
  | 'GO_LOWEST_LOSS'
  | 'GO_HIGHEST_LOSS'
  | 'ZOOM_OUT'
  | 'ZOOM_IN'
  // Witness navigation
  | 'GO_TO_MARKS'
  | 'GO_TO_WARRANT'
  | 'GO_TO_DECISION'
  // Dispatch actions (sent directly to reducer)
  | NavigationAction;

interface Binding {
  /** Keys to match (single key or sequence) */
  keys: string[];
  /** Required modifiers */
  modifiers?: { ctrl?: boolean; shift?: boolean; meta?: boolean };
  /** What to do when matched */
  action: ActionType;
  /** Human-readable description */
  description: string;
}

/**
 * NORMAL mode bindings.
 *
 * Philosophy: Navigate the graph, not the text.
 * - j/k scroll the viewport (no cursor, just scroll)
 * - {/} jump paragraphs
 * - g-prefix for graph navigation
 * - z-prefix for portal (fold) operations
 */
const NORMAL_BINDINGS: Binding[] = [
  // --- Scroll Navigation (reader mode) ---
  // N-01 Law: j/k are primary, arrows are aliases
  { keys: ['j'], action: 'SCROLL_DOWN', description: 'Scroll down one line' },
  { keys: ['ArrowDown'], action: 'SCROLL_DOWN', description: 'Scroll down one line (arrow alias)' },
  { keys: ['k'], action: 'SCROLL_UP', description: 'Scroll up one line' },
  { keys: ['ArrowUp'], action: 'SCROLL_UP', description: 'Scroll up one line (arrow alias)' },
  { keys: ['}'], action: 'SCROLL_PARAGRAPH_DOWN', description: 'Scroll to next paragraph' },
  { keys: ['{'], action: 'SCROLL_PARAGRAPH_UP', description: 'Scroll to prev paragraph' },

  // --- Mode Switches ---
  { keys: ['i'], action: 'ENTER_INSERT', description: 'Enter insert mode' },
  { keys: ['a'], action: 'ENTER_INSERT', description: 'Enter insert mode (append)' },
  { keys: [':'], action: 'ENTER_COMMAND', description: 'Enter command mode' },
  { keys: ['?'], action: 'SHOW_HELP', description: 'Show keyboard shortcuts' },

  // --- Graph Navigation (g-prefix) ---
  {
    keys: ['g', 'j'],
    action: { type: 'GO_SIBLING', direction: 1 },
    description: 'Go to next sibling',
  },
  {
    keys: ['g', 'k'],
    action: { type: 'GO_SIBLING', direction: -1 },
    description: 'Go to prev sibling',
  },
  { keys: ['g', 'd'], action: 'GO_DEFINITION', description: 'Go to definition' },
  { keys: ['g', 'r'], action: 'GO_REFERENCES', description: 'Go to references' },
  { keys: ['g', 't'], action: 'GO_TESTS', description: 'Go to tests' },
  { keys: ['g', 'D'], action: 'GO_DERIVATION_PARENT', description: 'Go to derivation parent' },
  { keys: ['g', 'c'], action: 'SHOW_CONFIDENCE', description: 'Show confidence panel' },
  { keys: ['g', 'e'], action: { type: 'ENTER_EDGE' }, description: 'Enter edge mode' },
  { keys: ['g', 'E'], action: 'TOGGLE_EDGE_PANEL', description: 'Toggle edge metadata panel' },
  { keys: ['g', 'w'], action: { type: 'ENTER_WITNESS' }, description: 'Enter witness mode' },
  {
    keys: ['g', 'W'],
    action: 'GO_TO_WARRANT',
    description: 'Go to warrant (justification for current node)',
  },
  {
    keys: ['g', 'f'],
    action: 'GO_TO_DECISION',
    description: 'Go to fusion (dialectical synthesis for current node)',
  },
  { keys: ['g', 'g'], action: 'SCROLL_TO_TOP', description: 'Go to top of document' },
  {
    keys: ['g', 'm'],
    action: 'GO_TO_MARKS',
    description: 'Go to marks (witness trail for current node)',
  },
  {
    keys: ['g', 'M'],
    action: 'TOGGLE_DECISION_STREAM',
    description: 'Toggle decision stream (all witness marks)',
  },
  {
    keys: ['g', 'a'],
    action: 'TOGGLE_ANALYSIS_QUADRANT',
    description: 'Toggle analysis quadrant (four-mode analysis)',
  },
  {
    keys: ['g', 'I'],
    action: 'TOGGLE_DERIVATION_INSPECTOR',
    description: 'Toggle derivation inspector panel',
  },

  // --- Derivation Navigation (Constitutional graph) ---
  {
    keys: ['g', 'h'],
    action: 'GO_DERIVATION_PARENT',
    description: 'Go to derivation parent (derives_from up)',
  },
  {
    keys: ['g', 'l'],
    action: 'GO_DERIVATION_CHILD',
    description: 'Go to derivation child (derives_from down)',
  },
  // Note: gj/gk already exist for sibling navigation, we repurpose for derivation siblings
  { keys: ['g', 'G'], action: 'GO_TO_GENESIS', description: 'Go to genesis (trace to L1 axiom)' },

  // --- Loss-Gradient Navigation (vim-style) ---
  {
    keys: ['g', 'L'],
    action: 'GO_LOWEST_LOSS',
    description: 'Go to lowest-loss neighbor (follow gradient)',
  },
  {
    keys: ['g', 'H'],
    action: 'GO_HIGHEST_LOSS',
    description: 'Go to highest-loss neighbor (investigate)',
  },

  // --- Scroll & Position ---
  { keys: ['G'], action: 'SCROLL_TO_BOTTOM', description: 'Go to bottom of document' },
  {
    keys: ['o'],
    modifiers: { ctrl: true },
    action: { type: 'GO_BACK' },
    description: 'Go back in trail',
  },

  // --- Portal Operations (z-prefix, vim fold-style) ---
  { keys: ['z', 'o'], action: 'PORTAL_OPEN', description: 'Open portal' },
  { keys: ['z', 'c'], action: 'PORTAL_CLOSE', description: 'Close portal' },
  { keys: ['z', 'a'], action: 'PORTAL_TOGGLE', description: 'Toggle portal' },
  { keys: ['z', 'O'], action: 'PORTAL_OPEN_ALL', description: 'Open all portals' },
  { keys: ['z', 'C'], action: 'PORTAL_CLOSE_ALL', description: 'Close all portals' },
];

// =============================================================================
// Hook Interface
// =============================================================================

export interface UseKeyHandlerOptions {
  state: NavigationState;
  dispatch: React.Dispatch<NavigationAction>;

  // Graph navigation callbacks
  goDefinition: () => void;
  goReferences: () => void;
  goTests: () => void;
  goDerivationParent?: () => void;
  goDerivationChild?: () => void;
  goDerivationNextSibling?: () => void;
  goDerivationPrevSibling?: () => void;
  goToGenesis?: () => void;
  showConfidence?: () => void;

  // Portal callbacks
  openPortal: () => void;
  closePortal: () => void;
  togglePortal: () => void;
  openAllPortals: () => void;
  closeAllPortals: () => void;

  // Scroll callbacks (reader mode navigation)
  scrollDown?: () => void;
  scrollUp?: () => void;
  scrollParagraphDown?: () => void;
  scrollParagraphUp?: () => void;
  scrollToTop?: () => void;
  scrollToBottom?: () => void;

  // Mode transition callbacks
  onEnterCommand?: () => void;
  onEnterInsert?: () => void | Promise<void>;
  onEdgeConfirm?: () => Promise<void>;
  onShowHelp?: () => void;

  // Decision stream (witness history)
  onToggleDecisionStream?: () => void;

  // Analysis quadrant
  onToggleAnalysisQuadrant?: () => void;

  // Edge metadata panel
  onToggleEdgePanel?: () => void;

  // Derivation inspector panel
  onToggleDerivationInspector?: () => void;

  // Loss-gradient navigation
  goLowestLoss?: () => void | Promise<void>;
  goHighestLoss?: () => void | Promise<void>;
  zoomOut?: () => void;
  zoomIn?: () => void;

  // Witness navigation
  goToMarks?: () => void | Promise<void>;
  goToWarrant?: () => void | Promise<void>;
  goToDecision?: () => void | Promise<void>;

  /** Whether key handling is enabled */
  enabled?: boolean;
}

export interface UseKeyHandlerResult {
  /** Current pending key sequence (for display, e.g., "g" waiting for next key) */
  pendingSequence: string;
  /** Reset the pending sequence */
  resetSequence: () => void;
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useKeyHandler(options: UseKeyHandlerOptions): UseKeyHandlerResult {
  const {
    state,
    dispatch,
    goDefinition,
    goReferences,
    goTests,
    goDerivationParent,
    goDerivationChild,
    goDerivationNextSibling,
    goDerivationPrevSibling,
    goToGenesis,
    showConfidence,
    openPortal,
    closePortal,
    togglePortal,
    openAllPortals,
    closeAllPortals,
    scrollDown,
    scrollUp,
    scrollParagraphDown,
    scrollParagraphUp,
    scrollToTop,
    scrollToBottom,
    onEnterCommand,
    onEnterInsert,
    onEdgeConfirm,
    onShowHelp,
    onToggleDecisionStream,
    onToggleAnalysisQuadrant,
    onToggleEdgePanel,
    onToggleDerivationInspector,
    goLowestLoss,
    goHighestLoss,
    zoomOut,
    zoomIn,
    goToMarks,
    goToWarrant,
    goToDecision,
    enabled = true,
  } = options;

  // --- Sequence State ---
  const [pendingKeys, setPendingKeys] = useState<string[]>([]);
  const lastKeyTimeRef = useRef<number>(0);
  const SEQUENCE_TIMEOUT = 1000; // 1 second to complete sequence

  const resetSequence = useCallback(() => {
    setPendingKeys([]);
  }, []);

  // --- Action Map ---
  // String actions mapped to callbacks (avoids giant switch statement)
  const actionMap = useCallback(
    (): Record<string, () => void> => ({
      GO_DEFINITION: goDefinition,
      GO_REFERENCES: goReferences,
      GO_TESTS: goTests,
      // Derivation navigation (Constitutional graph)
      GO_DERIVATION_PARENT: () => {
        if (goDerivationParent) {
          void goDerivationParent();
        }
      },
      GO_DERIVATION_CHILD: () => {
        if (goDerivationChild) {
          void goDerivationChild();
        }
      },
      GO_DERIVATION_NEXT_SIBLING: () => {
        if (goDerivationNextSibling) {
          void goDerivationNextSibling();
        }
      },
      GO_DERIVATION_PREV_SIBLING: () => {
        if (goDerivationPrevSibling) {
          void goDerivationPrevSibling();
        }
      },
      GO_TO_GENESIS: () => {
        if (goToGenesis) {
          void goToGenesis();
        }
      },
      SHOW_CONFIDENCE: () => showConfidence?.(),
      PORTAL_OPEN: openPortal,
      PORTAL_CLOSE: closePortal,
      PORTAL_TOGGLE: togglePortal,
      PORTAL_OPEN_ALL: openAllPortals,
      PORTAL_CLOSE_ALL: closeAllPortals,
      // Scroll navigation
      SCROLL_DOWN: () => scrollDown?.(),
      SCROLL_UP: () => scrollUp?.(),
      SCROLL_PARAGRAPH_DOWN: () => scrollParagraphDown?.(),
      SCROLL_PARAGRAPH_UP: () => scrollParagraphUp?.(),
      SCROLL_TO_TOP: () => scrollToTop?.(),
      SCROLL_TO_BOTTOM: () => scrollToBottom?.(),
      // Mode transitions
      ENTER_INSERT: () => {
        if (onEnterInsert) {
          void onEnterInsert();
        } else {
          dispatch({ type: 'ENTER_INSERT' });
        }
      },
      ENTER_COMMAND: () => {
        dispatch({ type: 'ENTER_COMMAND' });
        onEnterCommand?.();
      },
      SHOW_HELP: () => onShowHelp?.(),
      TOGGLE_DECISION_STREAM: () => onToggleDecisionStream?.(),
      TOGGLE_ANALYSIS_QUADRANT: () => onToggleAnalysisQuadrant?.(),
      TOGGLE_EDGE_PANEL: () => onToggleEdgePanel?.(),
      TOGGLE_DERIVATION_INSPECTOR: () => onToggleDerivationInspector?.(),
      // Loss-gradient navigation
      GO_LOWEST_LOSS: () => {
        if (goLowestLoss) {
          void goLowestLoss();
        }
      },
      GO_HIGHEST_LOSS: () => {
        if (goHighestLoss) {
          void goHighestLoss();
        }
      },
      ZOOM_OUT: () => zoomOut?.(),
      ZOOM_IN: () => zoomIn?.(),
      // Witness navigation
      GO_TO_MARKS: () => {
        if (goToMarks) {
          void goToMarks();
        }
      },
      GO_TO_WARRANT: () => {
        if (goToWarrant) {
          void goToWarrant();
        }
      },
      GO_TO_DECISION: () => {
        if (goToDecision) {
          void goToDecision();
        }
      },
    }),
    [
      dispatch,
      goDefinition,
      goReferences,
      goTests,
      goDerivationParent,
      goDerivationChild,
      goDerivationNextSibling,
      goDerivationPrevSibling,
      goToGenesis,
      showConfidence,
      openPortal,
      closePortal,
      togglePortal,
      openAllPortals,
      closeAllPortals,
      scrollDown,
      scrollUp,
      scrollParagraphDown,
      scrollParagraphUp,
      scrollToTop,
      scrollToBottom,
      onEnterCommand,
      onEnterInsert,
      onShowHelp,
      onToggleDecisionStream,
      onToggleAnalysisQuadrant,
      onToggleEdgePanel,
      onToggleDerivationInspector,
      goLowestLoss,
      goHighestLoss,
      zoomOut,
      zoomIn,
      goToMarks,
      goToWarrant,
      goToDecision,
    ]
  );

  // --- Action Executor ---
  const executeAction = useCallback(
    (action: ActionType) => {
      if (typeof action === 'string') {
        const map = actionMap();
        map[action]?.();
      } else {
        dispatch(action);
      }
    },
    [actionMap, dispatch]
  );

  // --- NORMAL Mode Handler ---
  const handleNormalMode = useCallback(
    (e: KeyboardEvent): boolean => {
      const key = e.key;
      const now = Date.now();

      // Check for sequence timeout
      if (pendingKeys.length > 0 && now - lastKeyTimeRef.current > SEQUENCE_TIMEOUT) {
        resetSequence();
      }

      const candidateKeys = [...pendingKeys, key];

      // Check modifiers for current key
      const hasCtrl = e.ctrlKey;
      const hasShift = e.shiftKey;
      const hasMeta = e.metaKey;

      // Find exact match
      const exactMatch = NORMAL_BINDINGS.find((b) => {
        if (b.keys.length !== candidateKeys.length) return false;
        if (!b.keys.every((k, i) => k === candidateKeys[i])) return false;

        // Check modifiers (only check on final key)
        if (b.modifiers?.ctrl && !hasCtrl) return false;
        if (b.modifiers?.shift && !hasShift) return false;
        if (b.modifiers?.meta && !hasMeta) return false;

        return true;
      });

      if (exactMatch) {
        e.preventDefault();
        resetSequence();
        executeAction(exactMatch.action);
        return true;
      }

      // Check for prefix match (sequence in progress)
      const isPrefix = NORMAL_BINDINGS.some(
        (b) =>
          b.keys.length > candidateKeys.length &&
          b.keys.slice(0, candidateKeys.length).every((k, i) => k === candidateKeys[i])
      );

      if (isPrefix) {
        e.preventDefault();
        setPendingKeys(candidateKeys);
        lastKeyTimeRef.current = now;
        return true;
      }

      // No match — reset sequence if we had one
      if (pendingKeys.length > 0) {
        resetSequence();
      }

      return false;
    },
    [pendingKeys, resetSequence, executeAction]
  );

  // --- EDGE Mode Handlers (split by phase to reduce complexity) ---
  const handleEdgeSelectType = useCallback(
    (e: KeyboardEvent): boolean => {
      const edgeType = EDGE_TYPE_KEYS[e.key.toLowerCase()] as EdgeType | undefined;
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
    (e: KeyboardEvent): boolean => {
      const key = e.key;
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
    [state.currentNode, dispatch]
  );

  const handleEdgeConfirmPhase = useCallback(
    (e: KeyboardEvent): boolean => {
      const key = e.key;
      if (key === 'y' || key === 'Enter') {
        e.preventDefault();
        if (onEdgeConfirm) {
          void onEdgeConfirm();
        } else {
          dispatch({ type: 'EDGE_CONFIRM' });
        }
        return true;
      }
      if (key === 'n' || key === 'Backspace') {
        e.preventDefault();
        dispatch({ type: 'EDGE_CANCEL' });
        return true;
      }
      return false;
    },
    [dispatch, onEdgeConfirm]
  );

  const handleEdgeMode = useCallback(
    (e: KeyboardEvent): boolean => {
      const { edgePending } = state;
      if (!edgePending) return false;

      switch (edgePending.phase) {
        case 'select-type':
          return handleEdgeSelectType(e);
        case 'select-target':
          return handleEdgeSelectTarget(e);
        case 'confirm':
          return handleEdgeConfirmPhase(e);
        default:
          return false;
      }
    },
    [state, handleEdgeSelectType, handleEdgeSelectTarget, handleEdgeConfirmPhase]
  );

  // --- Main Key Handler ---
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (!enabled) return;

      // Skip if in input/textarea (except for mode escapes)
      const target = e.target as HTMLElement;
      const isInputField = target.tagName === 'INPUT' || target.tagName === 'TEXTAREA';

      // Universal: Escape always exits to NORMAL
      if (e.key === 'Escape') {
        e.preventDefault();
        resetSequence();
        if (state.mode !== 'NORMAL') {
          dispatch({ type: 'SET_MODE', mode: 'NORMAL' });
        }
        return;
      }

      // In INSERT mode, only Escape is handled (above) — everything else goes to CodeMirror
      if (state.mode === 'INSERT') {
        return;
      }

      // In COMMAND mode, let CommandLine handle everything except Escape
      if (state.mode === 'COMMAND') {
        return;
      }

      // In WITNESS mode, let WitnessPanel handle everything except Escape
      if (state.mode === 'WITNESS') {
        return;
      }

      // Skip if in input field for other modes
      if (isInputField && state.mode !== 'EDGE') {
        return;
      }

      // Dispatch to mode-specific handler
      if (state.mode === 'NORMAL') {
        handleNormalMode(e);
      } else if (state.mode === 'EDGE') {
        handleEdgeMode(e);
      }
    },
    [enabled, state.mode, resetSequence, dispatch, handleNormalMode, handleEdgeMode]
  );

  // --- Event Listener ---
  useEffect(() => {
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return {
    pendingSequence: pendingKeys.join(''),
    resetSequence,
  };
}

// =============================================================================
// Exports for Testing/Documentation
// =============================================================================

/** Export bindings for help display */
export const NORMAL_MODE_BINDINGS_DOC = NORMAL_BINDINGS.map((b) => ({
  keys: b.keys.join(''),
  description: b.description,
  modifiers: b.modifiers,
}));
