/**
 * useMembrane — State machine for the Membrane co-thinking surface
 *
 * The Membrane has three concerns:
 * 1. Mode (compact/comfortable/spacious) — layout density
 * 2. Focus (what you're looking at) — context-aware content
 * 3. Dialogue (conversation history) — co-thinking thread
 *
 * OPTION C INTEGRATION:
 * Every dialogue session IS a K-Block. Messages accumulate in isolation.
 * Crystallize = harness.save() = thoughts escape to cosmos.
 *
 * "The proof IS the decision."
 * "The K-Block is where you edit a possible world."
 */

import { useCallback, useEffect, useReducer, useRef } from 'react';

import { useKBlock, type IsolationState } from './useKBlock';

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
  // K-Block integration (Option C)
  kblockIsolation: IsolationState;
  kblockIsDirty: boolean;
  sessionId: string;
}

// =============================================================================
// Actions
// =============================================================================

type MembraneAction =
  | { type: 'SET_MODE'; mode: MembraneMode }
  | { type: 'SET_FOCUS'; focus: Focus }
  | { type: 'APPEND_DIALOGUE'; message: DialogueMessage }
  | { type: 'CLEAR_DIALOGUE' }
  | { type: 'SET_WITNESS_CONNECTED'; connected: boolean }
  // K-Block actions
  | { type: 'UPDATE_KBLOCK'; isolation: IsolationState; isDirty: boolean }
  | { type: 'RESET_KBLOCK' };

// =============================================================================
// Reducer
// =============================================================================

// Generate unique session ID for this membrane instance
const generateSessionId = () => `membrane-${Date.now()}-${Math.random().toString(36).slice(2, 8)}`;

const initialState: MembraneState = {
  mode: 'comfortable',
  focus: { type: 'welcome' },
  dialogueHistory: [],
  witnessConnected: false,
  // K-Block state (Option C)
  kblockIsolation: 'PRISTINE',
  kblockIsDirty: false,
  sessionId: generateSessionId(),
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

    // K-Block actions
    case 'UPDATE_KBLOCK':
      return {
        ...state,
        kblockIsolation: action.isolation,
        kblockIsDirty: action.isDirty,
      };

    case 'RESET_KBLOCK':
      return {
        ...state,
        dialogueHistory: [],
        kblockIsolation: 'PRISTINE',
        kblockIsDirty: false,
        sessionId: generateSessionId(),
      };

    default:
      return state;
  }
}

// =============================================================================
// Hook
// =============================================================================

export interface CrystallizeResult {
  success: boolean;
  blockId?: string;
  messageCount?: number;
  error?: string;
}

export interface UseMembrane {
  // State
  mode: MembraneMode;
  focus: Focus;
  dialogueHistory: DialogueMessage[];
  witnessConnected: boolean;
  // K-Block state (Option C)
  kblockIsolation: IsolationState;
  kblockIsDirty: boolean;
  sessionId: string;

  // Actions
  setMode: (mode: MembraneMode) => void;
  setFocus: (type: FocusType, path?: string, content?: string) => void;
  appendDialogue: (role: 'user' | 'assistant', content: string) => Promise<void>;
  clearDialogue: () => void;
  setWitnessConnected: (connected: boolean) => void;

  // Compound actions
  crystallize: (reasoning?: string) => Promise<CrystallizeResult>;
  discardThoughts: () => Promise<void>;
  focusOnFile: (path: string) => void;
  focusOnSpec: (path: string) => void;
  focusOnConcept: (concept: string) => void;
  goHome: () => void;
}

let messageIdCounter = 0;

export function useMembrane(): UseMembrane {
  const [state, dispatch] = useReducer(membraneReducer, initialState);

  // K-Block integration (Option C: Every dialogue session IS a K-Block)
  const kblock = useKBlock(state.sessionId);

  // Sync K-Block state to membrane state
  const prevKBlockState = useRef(kblock.state);
  useEffect(() => {
    if (
      prevKBlockState.current.isolation !== kblock.state.isolation ||
      prevKBlockState.current.isDirty !== kblock.state.isDirty
    ) {
      dispatch({
        type: 'UPDATE_KBLOCK',
        isolation: kblock.state.isolation,
        isDirty: kblock.state.isDirty,
      });
      prevKBlockState.current = kblock.state;
    }
  }, [kblock.state]);

  // Basic actions
  const setMode = useCallback((mode: MembraneMode) => {
    dispatch({ type: 'SET_MODE', mode });
  }, []);

  const setFocus = useCallback((type: FocusType, path?: string, content?: string) => {
    dispatch({ type: 'SET_FOCUS', focus: { type, path, content } });
  }, []);

  // appendDialogue now writes to K-Block (isolated until crystallized)
  const appendDialogue = useCallback(
    async (role: 'user' | 'assistant', content: string) => {
      // Add to local state immediately (optimistic)
      const message: DialogueMessage = {
        id: `msg-${++messageIdCounter}`,
        role,
        content,
        timestamp: new Date(),
      };
      dispatch({ type: 'APPEND_DIALOGUE', message });

      // Also write to K-Block (isolated until crystallized)
      await kblock.appendThought(content, role);
    },
    [kblock]
  );

  const clearDialogue = useCallback(() => {
    dispatch({ type: 'CLEAR_DIALOGUE' });
  }, []);

  const setWitnessConnected = useCallback((connected: boolean) => {
    dispatch({ type: 'SET_WITNESS_CONNECTED', connected });
  }, []);

  // Crystallize = harness.save() for thoughts (Option C)
  const crystallize = useCallback(
    async (reasoning?: string): Promise<CrystallizeResult> => {
      const result = await kblock.crystallize(reasoning);

      if (result.success && !result.error) {
        // Also create a witness mark for the crystallization
        try {
          await fetch('/api/witness/marks', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              action: 'crystallize_dialogue',
              reasoning: reasoning || `Crystallized ${result.messageCount || 0} messages`,
              author: 'membrane',
              tags: ['dialogue', 'crystallize'],
            }),
          });
        } catch (error) {
          console.error('Failed to create witness mark:', error);
        }
      }

      return {
        success: result.success,
        blockId: result.blockId,
        messageCount: result.messageCount,
        error: result.error,
      };
    },
    [kblock]
  );

  // Discard thoughts = abandon K-Block without crystallizing
  const discardThoughts = useCallback(async () => {
    await kblock.discard();
    dispatch({ type: 'RESET_KBLOCK' });
  }, [kblock]);

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
    // K-Block state (Option C)
    kblockIsolation: state.kblockIsolation,
    kblockIsDirty: state.kblockIsDirty,
    sessionId: state.sessionId,

    // Actions
    setMode,
    setFocus,
    appendDialogue,
    clearDialogue,
    setWitnessConnected,

    // Compound actions
    crystallize,
    discardThoughts,
    focusOnFile,
    focusOnSpec,
    focusOnConcept,
    goHome,
  };
}
