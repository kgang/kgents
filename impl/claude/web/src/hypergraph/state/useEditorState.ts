/**
 * useEditorState — Centralized state management for HypergraphEditor
 *
 * Wraps the navigation reducer + effects.
 * This is what the Editor component uses.
 */

import { useReducer } from 'react';
import { navigationReducer } from './reducer';
import { createInitialState } from './types';
import type { NavigationState, NavigationAction } from './types';

export interface UseEditorStateResult {
  state: NavigationState;
  dispatch: React.Dispatch<NavigationAction>;
}

/**
 * Hook for managing editor state.
 *
 * Usage:
 * ```tsx
 * const { state, dispatch } = useEditorState();
 * ```
 */
export function useEditorState(): UseEditorStateResult {
  const [state, dispatch] = useReducer(navigationReducer, undefined, createInitialState);

  return {
    state,
    dispatch,
  };
}
