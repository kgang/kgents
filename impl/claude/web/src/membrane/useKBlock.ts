/**
 * useKBlock — K-Block operations for the Membrane
 *
 * Every dialogue session IS a K-Block. Messages accumulate in isolation.
 * Crystallize = harness.save() = thoughts escape to cosmos.
 *
 * "The K-Block is not where you edit a document.
 *  It's where you edit a possible world."
 */

import { useCallback, useState } from 'react';

// =============================================================================
// Types
// =============================================================================

export type IsolationState = 'PRISTINE' | 'DIRTY' | 'STALE' | 'CONFLICTING' | 'ENTANGLED';

export interface ThoughtBlockState {
  blockId: string | null;
  sessionId: string;
  contentLength: number;
  isolation: IsolationState;
  isDirty: boolean;
  isLoading: boolean;
  error: string | null;
}

export interface CrystallizeResult {
  success: boolean;
  blockId?: string;
  path?: string;
  contentHash?: string;
  messageCount?: number;
  crystallizedAt?: string;
  error?: string;
}

export interface UseKBlock {
  state: ThoughtBlockState;
  appendThought: (content: string, role?: 'user' | 'assistant') => Promise<void>;
  crystallize: (reasoning?: string) => Promise<CrystallizeResult>;
  discard: () => Promise<boolean>;
  reset: () => void;
}

// =============================================================================
// API Helpers
// =============================================================================

const API_BASE = '/agentese';

async function invokeKBlock(
  aspect: string,
  params: Record<string, unknown>
): Promise<{ success: boolean; data?: Record<string, unknown>; error?: string }> {
  try {
    const response = await fetch(`${API_BASE}/self/kblock/${aspect}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!response.ok) {
      const text = await response.text();
      return { success: false, error: `HTTP ${response.status}: ${text}` };
    }

    const data = await response.json();
    if (data.error) {
      return { success: false, error: data.error };
    }

    return { success: true, data };
  } catch (err) {
    return { success: false, error: err instanceof Error ? err.message : 'Unknown error' };
  }
}

// =============================================================================
// Hook
// =============================================================================

export function useKBlock(sessionId: string = 'membrane-default'): UseKBlock {
  const [state, setState] = useState<ThoughtBlockState>({
    blockId: null,
    sessionId,
    contentLength: 0,
    isolation: 'PRISTINE',
    isDirty: false,
    isLoading: false,
    error: null,
  });

  const appendThought = useCallback(
    async (content: string, role: 'user' | 'assistant' = 'user') => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      const result = await invokeKBlock('thought', {
        content,
        role,
        session_id: sessionId,
      });

      if (result.success && result.data) {
        setState((prev) => ({
          ...prev,
          blockId: result.data!.block_id as string,
          contentLength: result.data!.content_length as number,
          isolation: result.data!.isolation as IsolationState,
          isDirty: result.data!.is_dirty as boolean,
          isLoading: false,
        }));
      } else {
        setState((prev) => ({
          ...prev,
          isLoading: false,
          error: result.error || 'Failed to append thought',
        }));
      }
    },
    [sessionId]
  );

  const crystallize = useCallback(
    async (reasoning?: string): Promise<CrystallizeResult> => {
      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      const result = await invokeKBlock('crystallize', {
        session_id: sessionId,
        reasoning,
      });

      if (result.success && result.data) {
        // Reset state after crystallization
        setState((prev) => ({
          ...prev,
          isolation: 'PRISTINE',
          isDirty: false,
          isLoading: false,
        }));

        return {
          success: true,
          blockId: result.data.block_id as string | undefined,
          path: result.data.path as string | undefined,
          contentHash: result.data.content_hash as string | undefined,
          messageCount: result.data.message_count as number | undefined,
          crystallizedAt: result.data.crystallized_at as string | undefined,
        };
      }
      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: result.error || 'Failed to crystallize',
      }));

      return {
        success: false,
        error: result.error || 'Failed to crystallize',
      };
    },
    [sessionId]
  );

  const discard = useCallback(async (): Promise<boolean> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    const result = await invokeKBlock('discard_thoughts', {
      session_id: sessionId,
    });

    if (result.success) {
      setState({
        blockId: null,
        sessionId,
        contentLength: 0,
        isolation: 'PRISTINE',
        isDirty: false,
        isLoading: false,
        error: null,
      });
      return true;
    }
    setState((prev) => ({
      ...prev,
      isLoading: false,
      error: result.error || 'Failed to discard',
    }));
    return false;
  }, [sessionId]);

  const reset = useCallback(() => {
    setState({
      blockId: null,
      sessionId,
      contentLength: 0,
      isolation: 'PRISTINE',
      isDirty: false,
      isLoading: false,
      error: null,
    });
  }, [sessionId]);

  return {
    state,
    appendThought,
    crystallize,
    discard,
    reset,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useKBlock;
