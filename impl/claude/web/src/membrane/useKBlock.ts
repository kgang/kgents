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

    // AGENTESE responses wrap data in a 'result' field
    const result = data.result ?? data;
    if (result.error) {
      return { success: false, error: result.error };
    }

    return { success: true, data: result };
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
// File K-Block Hook (for SpecView editing)
// =============================================================================

export type KBlockViewType = 'prose' | 'graph' | 'code' | 'outline' | 'diff' | 'references';

export interface FileKBlockState {
  blockId: string | null;
  path: string | null;
  content: string;
  baseContent: string;
  isolation: IsolationState;
  isDirty: boolean;
  activeViews: KBlockViewType[];
  isLoading: boolean;
  error: string | null;
}

export interface SemanticDelta {
  kind: 'add' | 'remove' | 'modify';
  token_id: string;
  token_kind: string;
  token_value: string;
  old_value?: string;
  new_value?: string;
  parent_id?: string;
  position_hint?: number;
  timestamp: string;
}

export interface ViewEditResult {
  success: boolean;
  contentChanged: boolean;
  semanticDeltas: SemanticDelta[];
  error?: string;
}

export interface KBlockReference {
  kind: 'implements' | 'tests' | 'extends' | 'extended_by' | 'references' | 'heritage';
  target: string;
  context?: string;
  lineNumber?: number;
  confidence: number;
  stale: boolean;
  exists: boolean;
}

export interface KBlockCreateResult {
  success: boolean;
  blockId?: string;
  path?: string;
  content?: string;
  baseContent?: string;
  isolation?: IsolationState;
  isDirty?: boolean;
  activeViews?: KBlockViewType[];
  error?: string;
}

export interface UseFileKBlock {
  state: FileKBlockState;
  create: (path: string) => Promise<KBlockCreateResult>;
  refresh: () => Promise<boolean>;
  viewEdit: (
    sourceView: KBlockViewType,
    content: string,
    reasoning?: string
  ) => Promise<ViewEditResult>;
  save: (reasoning?: string) => Promise<{ success: boolean; error?: string }>;
  discard: () => Promise<boolean>;
  getReferences: () => Promise<KBlockReference[]>;
  reset: () => void;
}

/**
 * useFileKBlock — K-Block operations for file-based editing
 *
 * Unlike useKBlock (for dialogue thoughts), this hook manages
 * K-Blocks for actual files in the filesystem.
 *
 * Usage in SpecView:
 * ```tsx
 * const kblock = useFileKBlock();
 *
 * // Create K-Block and get content immediately
 * useEffect(() => {
 *   async function init() {
 *     const result = await kblock.create(specPath);
 *     if (result.success && result.content) {
 *       // Content is available immediately, no need to wait for state update
 *       const parsed = await documentApi.parse(result.content, 'COMFORTABLE');
 *       setSceneGraph(parsed.scene_graph);
 *     }
 *   }
 *   init();
 * }, [specPath]);
 *
 * // Edit via graph view
 * await kblock.viewEdit('graph', newGraphContent, 'Kent reorganized sections');
 *
 * // Save when done
 * await kblock.save('Completed spec update');
 * ```
 */
export function useFileKBlock(): UseFileKBlock {
  const [state, setState] = useState<FileKBlockState>({
    blockId: null,
    path: null,
    content: '',
    baseContent: '',
    isolation: 'PRISTINE',
    isDirty: false,
    activeViews: [],
    isLoading: false,
    error: null,
  });

  const create = useCallback(async (path: string): Promise<KBlockCreateResult> => {
    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    const result = await invokeKBlock('create', { path });

    if (result.success && result.data) {
      const blockId = result.data.block_id as string;

      // Fetch full content
      const getResult = await invokeKBlock('get', { block_id: blockId });

      if (getResult.success && getResult.data) {
        const content = getResult.data.content as string;
        const baseContent = getResult.data.base_content as string;
        const isolation = getResult.data.isolation as IsolationState;
        const isDirty = getResult.data.is_dirty as boolean;
        const activeViews = getResult.data.active_views as KBlockViewType[];
        const filePath = getResult.data.path as string;

        // Update state
        setState({
          blockId,
          path: filePath,
          content,
          baseContent,
          isolation,
          isDirty,
          activeViews,
          isLoading: false,
          error: null,
        });

        // Return content directly so caller doesn't have to wait for state update
        return {
          success: true,
          blockId,
          path: filePath,
          content,
          baseContent,
          isolation,
          isDirty,
          activeViews,
        };
      }
    }

    const errorMsg = result.error || 'Failed to create K-Block';
    setState((prev) => ({
      ...prev,
      isLoading: false,
      error: errorMsg,
    }));

    return { success: false, error: errorMsg };
  }, []);

  const refresh = useCallback(async (): Promise<boolean> => {
    if (!state.blockId) return false;

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    const getResult = await invokeKBlock('get', { block_id: state.blockId });

    if (getResult.success && getResult.data) {
      setState((prev) => ({
        ...prev,
        content: getResult.data!.content as string,
        baseContent: getResult.data!.base_content as string,
        isolation: getResult.data!.isolation as IsolationState,
        isDirty: getResult.data!.is_dirty as boolean,
        activeViews: getResult.data!.active_views as KBlockViewType[],
        isLoading: false,
      }));
      return true;
    }

    setState((prev) => ({
      ...prev,
      isLoading: false,
      error: getResult.error || 'Failed to refresh K-Block',
    }));
    return false;
  }, [state.blockId]);

  const viewEdit = useCallback(
    async (
      sourceView: KBlockViewType,
      content: string,
      reasoning?: string
    ): Promise<ViewEditResult> => {
      if (!state.blockId) {
        return { success: false, contentChanged: false, semanticDeltas: [], error: 'No K-Block' };
      }

      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      const result = await invokeKBlock('view_edit', {
        block_id: state.blockId,
        source_view: sourceView,
        content,
        reasoning,
      });

      if (result.success && result.data) {
        // Refresh to get updated content
        await refresh();

        return {
          success: true,
          contentChanged: result.data.content_changed as boolean,
          semanticDeltas: (result.data.semantic_deltas as SemanticDelta[]) || [],
        };
      }

      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: result.error || 'Failed to edit',
      }));

      return {
        success: false,
        contentChanged: false,
        semanticDeltas: [],
        error: result.error || 'Failed to edit',
      };
    },
    [state.blockId, refresh]
  );

  const save = useCallback(
    async (reasoning?: string): Promise<{ success: boolean; error?: string }> => {
      if (!state.blockId) {
        return { success: false, error: 'No K-Block' };
      }

      setState((prev) => ({ ...prev, isLoading: true, error: null }));

      const result = await invokeKBlock('save', {
        block_id: state.blockId,
        reasoning,
      });

      if (result.success && result.data) {
        if (result.data.success) {
          setState((prev) => ({
            ...prev,
            isolation: 'PRISTINE',
            isDirty: false,
            baseContent: prev.content,
            isLoading: false,
          }));
          return { success: true };
        }
        return { success: false, error: result.data.error as string };
      }

      setState((prev) => ({
        ...prev,
        isLoading: false,
        error: result.error || 'Failed to save',
      }));

      return { success: false, error: result.error || 'Failed to save' };
    },
    [state.blockId]
  );

  const discard = useCallback(async (): Promise<boolean> => {
    if (!state.blockId) return false;

    setState((prev) => ({ ...prev, isLoading: true, error: null }));

    const result = await invokeKBlock('discard', { block_id: state.blockId });

    if (result.success) {
      setState({
        blockId: null,
        path: null,
        content: '',
        baseContent: '',
        isolation: 'PRISTINE',
        isDirty: false,
        activeViews: [],
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
  }, [state.blockId]);

  const getReferences = useCallback(async (): Promise<KBlockReference[]> => {
    if (!state.blockId) return [];

    const result = await invokeKBlock('references', { block_id: state.blockId });

    if (result.success && result.data && result.data.references) {
      return (result.data.references as Record<string, unknown>[]).map((ref) => ({
        kind: ref.kind as KBlockReference['kind'],
        target: ref.target as string,
        context: ref.context as string | undefined,
        lineNumber: ref.line_number as number | undefined,
        confidence: ref.confidence as number,
        stale: ref.stale as boolean,
        exists: ref.exists as boolean,
      }));
    }

    return [];
  }, [state.blockId]);

  const reset = useCallback(() => {
    setState({
      blockId: null,
      path: null,
      content: '',
      baseContent: '',
      isolation: 'PRISTINE',
      isDirty: false,
      activeViews: [],
      isLoading: false,
      error: null,
    });
  }, []);

  return {
    state,
    create,
    refresh,
    viewEdit,
    save,
    discard,
    getReferences,
    reset,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useKBlock;
