/**
 * useMembrane — State machine for the Membrane co-thinking surface
 *
 * The Membrane has three concerns:
 * 1. Mode (compact/comfortable/spacious) — layout density
 * 2. Focus (what you're looking at) — context-aware content
 * 3. Dialogue (conversation history) — co-thinking thread
 *
 * "The proof IS the decision."
 */

import { useCallback, useReducer } from 'react';

// =============================================================================
// Types
// =============================================================================

export type MembraneMode = 'compact' | 'comfortable' | 'spacious';

export type FocusType = 'welcome' | 'file' | 'spec' | 'concept' | 'dialogue';

export interface Focus {
  type: FocusType;
  path?: string;
  content?: string;
  label?: string;
}

export interface DialogueMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  focusLinks?: Array<{ type: FocusType; path: string; label: string }>;
}

export interface MembraneState {
  mode: MembraneMode;
  focus: Focus;
  dialogueHistory: DialogueMessage[];
  witnessConnected: boolean;
}

// =============================================================================
// Actions
// =============================================================================

type MembraneAction =
  | { type: 'SET_MODE'; mode: MembraneMode }
  | { type: 'SET_FOCUS'; focus: Focus }
  | { type: 'APPEND_DIALOGUE'; message: DialogueMessage }
  | { type: 'CLEAR_DIALOGUE' }
  | { type: 'SET_WITNESS_CONNECTED'; connected: boolean };

// =============================================================================
// Reducer
// =============================================================================

const initialState: MembraneState = {
  mode: 'comfortable',
  focus: { type: 'welcome' },
  dialogueHistory: [],
  witnessConnected: false,
};

function membraneReducer(state: MembraneState, action: MembraneAction): MembraneState {
  switch (action.type) {
    case 'SET_MODE':
      return { ...state, mode: action.mode };

    case 'SET_FOCUS':
      return { ...state, focus: action.focus };

    case 'APPEND_DIALOGUE':
      return {
        ...state,
        dialogueHistory: [...state.dialogueHistory, action.message],
      };

    case 'CLEAR_DIALOGUE':
      return { ...state, dialogueHistory: [] };

    case 'SET_WITNESS_CONNECTED':
      return { ...state, witnessConnected: action.connected };

    default:
      return state;
  }
}

// =============================================================================
// Hook
// =============================================================================

export interface UseMembrane {
  // State
  mode: MembraneMode;
  focus: Focus;
  dialogueHistory: DialogueMessage[];
  witnessConnected: boolean;

  // Actions
  setMode: (mode: MembraneMode) => void;
  setFocus: (type: FocusType, path?: string, content?: string) => void;
  appendDialogue: (role: 'user' | 'assistant', content: string) => void;
  clearDialogue: () => void;
  setWitnessConnected: (connected: boolean) => void;

  // Compound actions
  crystallize: (content: string) => Promise<void>;
  focusOnFile: (path: string) => void;
  focusOnSpec: (path: string) => void;
  focusOnConcept: (concept: string) => void;
  goHome: () => void;
}

let messageIdCounter = 0;

export function useMembrane(): UseMembrane {
  const [state, dispatch] = useReducer(membraneReducer, initialState);

  // Basic actions
  const setMode = useCallback((mode: MembraneMode) => {
    dispatch({ type: 'SET_MODE', mode });
  }, []);

  const setFocus = useCallback((type: FocusType, path?: string, content?: string) => {
    dispatch({ type: 'SET_FOCUS', focus: { type, path, content } });
  }, []);

  const appendDialogue = useCallback((role: 'user' | 'assistant', content: string) => {
    const message: DialogueMessage = {
      id: `msg-${++messageIdCounter}`,
      role,
      content,
      timestamp: new Date(),
    };
    dispatch({ type: 'APPEND_DIALOGUE', message });
  }, []);

  const clearDialogue = useCallback(() => {
    dispatch({ type: 'CLEAR_DIALOGUE' });
  }, []);

  const setWitnessConnected = useCallback((connected: boolean) => {
    dispatch({ type: 'SET_WITNESS_CONNECTED', connected });
  }, []);

  // Compound actions
  const crystallize = useCallback(async (content: string) => {
    try {
      await fetch('/api/witness/marks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          action: 'crystallize',
          reasoning: content,
          author: 'membrane',
        }),
      });
    } catch (error) {
      console.error('Failed to crystallize:', error);
    }
  }, []);

  const focusOnFile = useCallback((path: string) => {
    dispatch({ type: 'SET_FOCUS', focus: { type: 'file', path, label: path.split('/').pop() } });
  }, []);

  const focusOnSpec = useCallback((path: string) => {
    dispatch({ type: 'SET_FOCUS', focus: { type: 'spec', path, label: path.split('/').pop() } });
  }, []);

  const focusOnConcept = useCallback((concept: string) => {
    dispatch({ type: 'SET_FOCUS', focus: { type: 'concept', path: concept, label: concept } });
  }, []);

  const goHome = useCallback(() => {
    dispatch({ type: 'SET_FOCUS', focus: { type: 'welcome' } });
  }, []);

  return {
    // State
    mode: state.mode,
    focus: state.focus,
    dialogueHistory: state.dialogueHistory,
    witnessConnected: state.witnessConnected,

    // Actions
    setMode,
    setFocus,
    appendDialogue,
    clearDialogue,
    setWitnessConnected,

    // Compound actions
    crystallize,
    focusOnFile,
    focusOnSpec,
    focusOnConcept,
    goHome,
  };
}
