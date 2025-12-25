/**
 * useKBlock — Unified K-Block integration
 *
 * "The K-Block is not where you edit a document.
 *  It's where you edit a possible world."
 *
 * This hook manages K-Block lifecycle for TWO use cases:
 * 1. Dialogue K-Blocks (path = null): Thoughts accumulate in isolation
 * 2. File K-Blocks (path = string): File editing in isolation
 *
 * Philosophy:
 *   You're never editing the "real" thing.
 *   You're editing a possible world.
 *   Crystallize/Save commits to cosmos (escapes isolation)
 *   Discard abandons (no cosmic effects)
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { kblockApi } from '../api/client';
import type { KBlockIsolation, KBlockViewType, KBlockReference } from '../api/client';
import type { ToulminProof } from '../api/zeroSeed';

// =============================================================================
// Types
// =============================================================================

/**
 * Isolation state of a K-Block.
 * Matches backend KBlockIsolation.
 */
export type IsolationState = KBlockIsolation;

/**
 * K-Block view types for file editing.
 */
export type { KBlockViewType };

/**
 * Reference discovered by ReferencesView.
 */
export type { KBlockReference };

/**
 * Toulmin proof structure (for Zero Seed / Proof Engine).
 */
export type { ToulminProof };

/**
 * Unified K-Block state (superset of dialogue + file + Zero Seed state).
 */
export interface KBlockState {
  /** K-Block ID from backend */
  blockId: string;

  /** File path (null for dialogue K-Blocks and Zero Seed nodes) */
  path: string | null;

  /** Session ID (for dialogue K-Blocks) */
  sessionId?: string;

  /** Current content (working copy) */
  content: string;

  /** Base content (original, for diffing) */
  baseContent: string;

  /** Isolation state */
  isolation: IsolationState;

  /** Whether content has changed from base */
  isDirty: boolean;

  /** Active views (for file K-Blocks) */
  activeViews: KBlockViewType[];

  /** Active checkpoints (for file K-Blocks) */
  checkpoints: Array<{
    id: string;
    name: string;
    contentHash: string;
    createdAt: string;
  }>;

  /** Content length (for dialogue K-Blocks) */
  contentLength: number;

  /** Analysis status (for file K-Blocks with Sovereign) */
  analysisStatus?: 'pending' | 'analyzing' | 'analyzed' | 'failed';
  analysisRequired?: boolean;
  isReadOnly?: boolean;

  // =============================================================================
  // Zero Seed Fields (for epistemic graph nodes)
  // =============================================================================

  /** Zero Seed layer (1-7) */
  zeroSeedLayer?: 1 | 2 | 3 | 4 | 5 | 6 | 7;

  /** Zero Seed node kind (axiom, value, goal, spec, action, reflection, representation) */
  zeroSeedKind?: string;

  /** Lineage: parent K-Block IDs that this node derives from */
  lineage: string[];

  /** Whether this node has a Toulmin proof attached */
  hasProof: boolean;

  /** The Toulmin proof structure (if hasProof is true) */
  toulminProof?: ToulminProof;

  /** Confidence score (0-1) from proof quality */
  confidence: number;

  /** Parent K-Block IDs (for derivation navigation) */
  parentBlocks: string[];

  /** Child K-Block IDs (for derivation navigation) */
  childBlocks: string[];
}

/**
 * Result from creating a K-Block.
 */
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
  // Sovereignty: content not in sovereign store
  not_ingested?: boolean;
  ingest_hint?: string;
  // Analysis tracking
  analysisStatus?: 'pending' | 'analyzing' | 'analyzed' | 'failed';
  analysisRequired?: boolean;
}

/**
 * Result from crystallizing/saving a K-Block.
 */
export interface KBlockSaveResult {
  success: boolean;
  blockId?: string;
  path?: string;
  contentHash?: string;
  messageCount?: number;
  crystallizedAt?: string;
  error?: string;
}

/**
 * Result from view editing (file K-Blocks only).
 */
export interface ViewEditResult {
  success: boolean;
  contentChanged: boolean;
  semanticDeltas: Array<{
    kind: 'add' | 'remove' | 'modify';
    token_id: string;
    token_kind: string;
    token_value: string;
    old_value?: string;
    new_value?: string;
    parent_id?: string;
    position_hint?: number;
    timestamp: string;
  }>;
  error?: string;
}

/**
 * Unified hook result.
 */
export interface UseKBlockResult {
  /** Current K-Block state (null if no K-Block active) */
  state: KBlockState | null;

  /** Alias for state (backward compatibility with HypergraphEditor) */
  kblock: KBlockState | null;

  /** Whether a K-Block operation is in progress */
  loading: boolean;

  /** Last error message */
  error: string | null;

  /**
   * Create K-Block.
   * - For file: pass path string
   * - For dialogue: pass null (sessionId from options)
   * Called when entering INSERT mode or starting a dialogue.
   */
  create: (path: string | null) => Promise<KBlockCreateResult>;

  /**
   * Update content in the K-Block (local only).
   * Called on every keystroke in INSERT mode.
   */
  updateContent: (content: string) => void;

  /**
   * Append thought to dialogue K-Block.
   * Only for dialogue K-Blocks (path = null).
   */
  appendThought: (content: string, role?: 'user' | 'assistant') => Promise<void>;

  /**
   * Edit via any view (file K-Blocks only).
   * Semantic deltas are extracted and propagated.
   *
   * @param sourceView - Which view was edited
   * @param content - New content
   * @param reasoning - Optional reasoning for witness trace
   */
  viewEdit: (
    sourceView: KBlockViewType,
    content: string,
    reasoning?: string
  ) => Promise<ViewEditResult>;

  /**
   * Refresh K-Block content from backend.
   * Only for file K-Blocks.
   */
  refresh: () => Promise<boolean>;

  /**
   * Save/Crystallize K-Block to cosmos with witness message.
   * Called on :w command or "Crystallize" button.
   *
   * @param reasoning - Witness message (why this change?)
   */
  save: (reasoning?: string) => Promise<KBlockSaveResult>;

  /**
   * Discard K-Block without saving.
   * Called on :q! command or "Discard" button.
   */
  discard: () => Promise<boolean>;

  /**
   * Create a named checkpoint (file K-Blocks only).
   * Called on :checkpoint command.
   */
  checkpoint: (name: string) => Promise<string | null>;

  /**
   * Rewind to a checkpoint (file K-Blocks only).
   * Called on :rewind command.
   */
  rewind: (checkpointId: string) => Promise<boolean>;

  /**
   * Get references (file K-Blocks only).
   * Discovers implements, tests, extends relationships.
   */
  getReferences: () => Promise<KBlockReference[]>;

  /**
   * Reset hook state (local only).
   * Called when component unmounts or mode exits.
   */
  reset: () => void;

  // =============================================================================
  // Zero Seed Methods (for epistemic graph nodes)
  // =============================================================================

  /**
   * Create a Zero Seed K-Block.
   * Used when creating nodes in the epistemic graph.
   *
   * @param layer - Zero Seed layer (1-7)
   * @param kind - Node kind (axiom, value, goal, etc.)
   * @param content - Node content
   * @param lineage - Parent K-Block IDs this derives from
   */
  createZeroSeed: (
    layer: 1 | 2 | 3 | 4 | 5 | 6 | 7,
    kind: string,
    content: string,
    lineage: string[]
  ) => Promise<KBlockCreateResult>;

  /**
   * Add a derivation link to a parent K-Block.
   * Used when connecting nodes in the derivation graph.
   *
   * @param parentId - Parent K-Block ID
   */
  addDerivation: (parentId: string) => Promise<void>;

  /**
   * Remove a derivation link from a parent K-Block.
   *
   * @param parentId - Parent K-Block ID
   */
  removeDerivation: (parentId: string) => Promise<void>;

  /**
   * Set/update the Toulmin proof for this K-Block.
   * Used when attaching proof structure to a node.
   *
   * @param proof - Toulmin proof structure
   */
  setProof: (proof: ToulminProof) => Promise<void>;

  /**
   * Navigate to a parent K-Block.
   *
   * @param index - Index in parentBlocks array
   */
  goToParent: (index: number) => void;

  /**
   * Navigate to a child K-Block.
   *
   * @param index - Index in childBlocks array
   */
  goToChild: (index: number) => void;
}

// =============================================================================
// API Helpers (for dialogue K-Blocks)
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
// Hook Options
// =============================================================================

export interface UseKBlockOptions {
  /** Session ID for dialogue K-Blocks (ignored if path provided) */
  sessionId?: string;
  /** Auto-create K-Block on mount */
  autoCreate?: boolean;
  /** Initial path for auto-create (null = dialogue, string = file) */
  initialPath?: string | null;
}

// =============================================================================
// Unified Hook
// =============================================================================

/**
 * Unified hook for managing K-Block lifecycle.
 *
 * Usage (Dialogue):
 * ```tsx
 * const kblock = useKBlock({ sessionId: 'my-session', autoCreate: true });
 * await kblock.appendThought('Hello world');
 * await kblock.save('Completed conversation');
 * ```
 *
 * Usage (File):
 * ```tsx
 * const kblock = useKBlock();
 * const result = await kblock.create('/path/to/file.md');
 * if (result.success && result.content) {
 *   // Work with content
 * }
 * await kblock.viewEdit('graph', newGraphContent, 'Reorganized sections');
 * await kblock.save('Completed spec update');
 * ```
 */
export function useKBlock(options: UseKBlockOptions = {}): UseKBlockResult {
  const { sessionId = 'membrane-default', autoCreate = false, initialPath } = options;

  const [state, setState] = useState<KBlockState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track pending operations to avoid race conditions
  const pendingRef = useRef<AbortController | null>(null);

  // Auto-create on mount if requested
  useEffect(() => {
    if (autoCreate && !state) {
      create(initialPath ?? null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [autoCreate, initialPath]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      pendingRef.current?.abort();
    };
  }, []);

  // =========================================================================
  // Create K-Block (Dialogue or File)
  // =========================================================================

  const create = useCallback(
    async (path: string | null): Promise<KBlockCreateResult> => {
      // Abort any pending operation
      pendingRef.current?.abort();
      const controller = new AbortController();
      pendingRef.current = controller;

      setLoading(true);
      setError(null);

      try {
        // DIALOGUE K-BLOCK: path = null
        if (path === null) {
          // Dialogue K-Blocks don't have an explicit create endpoint
          // They're created implicitly on first appendThought
          // Initialize state with empty block
          const initialState: KBlockState = {
            blockId: `dialogue-${sessionId}`,
            path: null,
            sessionId,
            content: '',
            baseContent: '',
            isolation: 'PRISTINE',
            isDirty: false,
            activeViews: [],
            checkpoints: [],
            contentLength: 0,
            lineage: [],
            hasProof: false,
            confidence: 1.0,
            parentBlocks: [],
            childBlocks: [],
          };

          setState(initialState);
          setLoading(false);

          return {
            success: true,
            blockId: initialState.blockId,
            path: undefined,
            content: '',
            baseContent: '',
            isolation: 'PRISTINE',
            isDirty: false,
          };
        }

        // FILE K-BLOCK: path = string
        const response = await kblockApi.create(path);

        if (controller.signal.aborted) {
          return { success: false, error: 'Aborted' };
        }

        // Check if content not ingested (sovereign store empty)
        // Note: These fields may not exist if backend doesn't have Sovereign integration
        const notIngested = (response as any).not_ingested;
        if (notIngested) {
          setLoading(false);
          return {
            success: true,
            blockId: response.block_id,
            path: response.path,
            content: '',
            not_ingested: true,
            ingest_hint: (response as any).ingest_hint || 'Upload content via File Picker',
            analysisRequired: (response as any).analysis_required,
            analysisStatus: (response as any).analysis_status,
          };
        }

        // Fetch full content
        const contentResponse = await kblockApi.get(response.block_id);

        if (controller.signal.aborted) {
          return { success: false, error: 'Aborted' };
        }

        const analysisStatus =
          ((response as any).analysis_status as 'pending' | 'analyzing' | 'analyzed' | 'failed') ||
          ((response as any).analysis_required ? 'pending' : 'analyzed');

        const newState: KBlockState = {
          blockId: contentResponse.block_id,
          path: contentResponse.path,
          content: contentResponse.content,
          baseContent: contentResponse.base_content,
          isolation: contentResponse.isolation,
          isDirty: contentResponse.is_dirty,
          activeViews: contentResponse.active_views,
          checkpoints: contentResponse.checkpoints.map((cp) => ({
            id: cp.id,
            name: cp.name,
            contentHash: cp.content_hash,
            createdAt: cp.created_at,
          })),
          contentLength: contentResponse.content.length,
          analysisStatus,
          analysisRequired: (response as any).analysis_required,
          isReadOnly: analysisStatus !== 'analyzed',
          // Zero Seed fields (initialize as empty for file K-Blocks)
          lineage: [],
          hasProof: false,
          confidence: 1.0,
          parentBlocks: [],
          childBlocks: [],
        };

        setState(newState);
        setLoading(false);

        console.info('[useKBlock] Created file K-Block:', newState.blockId, 'for', path);

        return {
          success: true,
          blockId: newState.blockId,
          path: newState.path !== null ? newState.path : undefined,
          content: newState.content,
          baseContent: newState.baseContent,
          isolation: newState.isolation,
          isDirty: newState.isDirty,
          activeViews: newState.activeViews,
          analysisStatus: newState.analysisStatus,
          analysisRequired: newState.analysisRequired,
        };
      } catch (err) {
        if (controller.signal.aborted) {
          return { success: false, error: 'Aborted' };
        }

        const message = err instanceof Error ? err.message : 'Failed to create K-Block';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Create failed:', message);
        return { success: false, error: message };
      }
    },
    [sessionId]
  );

  // =========================================================================
  // Update Content (Local Only)
  // =========================================================================

  const updateContent = useCallback((content: string) => {
    setState((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        content,
        isDirty: content !== prev.baseContent,
        isolation: content !== prev.baseContent ? 'DIRTY' : 'PRISTINE',
        contentLength: content.length,
      };
    });
  }, []);

  // =========================================================================
  // Append Thought (Dialogue K-Blocks Only)
  // =========================================================================

  const appendThought = useCallback(
    async (content: string, role: 'user' | 'assistant' = 'user') => {
      if (state?.path !== null) {
        console.warn('[useKBlock] appendThought called on file K-Block (expected dialogue)');
        return;
      }

      setLoading(true);
      setError(null);

      const result = await invokeKBlock('thought', {
        content,
        role,
        session_id: sessionId,
      });

      if (result.success && result.data) {
        setState((prev) => ({
          blockId: result.data!.block_id as string,
          path: null,
          sessionId,
          content: prev?.content || '',
          baseContent: prev?.baseContent || '',
          contentLength: result.data!.content_length as number,
          isolation: result.data!.isolation as IsolationState,
          isDirty: result.data!.is_dirty as boolean,
          activeViews: [],
          checkpoints: [],
          lineage: prev?.lineage || [],
          hasProof: prev?.hasProof || false,
          confidence: prev?.confidence || 1.0,
          parentBlocks: prev?.parentBlocks || [],
          childBlocks: prev?.childBlocks || [],
        }));
        setLoading(false);
      } else {
        setError(result.error || 'Failed to append thought');
        setLoading(false);
      }
    },
    [sessionId, state?.path]
  );

  // =========================================================================
  // View Edit (File K-Blocks Only)
  // =========================================================================

  const viewEdit = useCallback(
    async (
      sourceView: KBlockViewType,
      content: string,
      reasoning?: string
    ): Promise<ViewEditResult> => {
      if (!state || state.path === null) {
        return {
          success: false,
          contentChanged: false,
          semanticDeltas: [],
          error: 'No file K-Block active',
        };
      }

      setLoading(true);
      setError(null);

      try {
        const response = await kblockApi.viewEdit(state.blockId, sourceView, content, reasoning);

        // Refresh to get updated content
        const refreshed = await refresh();

        setLoading(false);

        if (!refreshed) {
          return {
            success: false,
            contentChanged: false,
            semanticDeltas: [],
            error: 'View edit succeeded but refresh failed',
          };
        }

        return {
          success: true,
          contentChanged: response.content_changed,
          semanticDeltas:
            response.semantic_deltas?.map((d) => ({
              kind: d.kind as 'add' | 'remove' | 'modify',
              token_id: d.token_id,
              token_kind: d.token_kind,
              token_value: d.token_value,
              old_value: d.old_value,
              new_value: d.new_value,
              parent_id: d.parent_id,
              position_hint: d.position_hint,
              timestamp: d.timestamp,
            })) || [],
        };
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to edit';
        setError(message);
        setLoading(false);
        return {
          success: false,
          contentChanged: false,
          semanticDeltas: [],
          error: message,
        };
      }
    },
    [state]
  );

  // =========================================================================
  // Refresh (File K-Blocks Only)
  // =========================================================================

  const refresh = useCallback(async (): Promise<boolean> => {
    if (!state || state.path === null) return false;

    setLoading(true);
    setError(null);

    try {
      const response = await kblockApi.get(state.blockId);

      setState((prev) => {
        if (!prev) return prev;
        return {
          ...prev,
          content: response.content,
          baseContent: response.base_content,
          isolation: response.isolation,
          isDirty: response.is_dirty,
          activeViews: response.active_views,
          contentLength: response.content.length,
        };
      });

      setLoading(false);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to refresh';
      setError(message);
      setLoading(false);
      return false;
    }
  }, [state]);

  // =========================================================================
  // Save / Crystallize
  // =========================================================================

  const save = useCallback(
    async (reasoning?: string): Promise<KBlockSaveResult> => {
      if (!state) {
        setError('No K-Block to save');
        return { success: false, error: 'No K-Block to save' };
      }

      setLoading(true);
      setError(null);

      try {
        // FILE K-BLOCK: sync content first, then save
        if (state.path !== null) {
          // Sync content to backend via view_edit
          if (state.isDirty) {
            await kblockApi.viewEdit(state.blockId, 'prose', state.content, reasoning);
          }

          // Then commit to cosmos
          const response = await kblockApi.save(state.blockId, reasoning);

          if (!response.success) {
            throw new Error(response.error || 'Save failed');
          }

          // Clear K-Block state (it's now in cosmos)
          setState(null);
          setLoading(false);

          console.info(
            '[useKBlock] Saved file K-Block:',
            state.blockId,
            reasoning ? `(${reasoning})` : ''
          );

          return {
            success: true,
            blockId: state.blockId,
            path: state.path,
          };
        }

        // DIALOGUE K-BLOCK: crystallize
        const result = await invokeKBlock('crystallize', {
          session_id: sessionId,
          reasoning,
        });

        if (result.success && result.data) {
          // Reset state after crystallization
          setState((prev) => {
            if (!prev) return prev;
            return {
              ...prev,
              isolation: 'PRISTINE',
              isDirty: false,
            };
          });
          setLoading(false);

          console.info(
            '[useKBlock] Crystallized dialogue K-Block:',
            state.blockId,
            reasoning ? `(${reasoning})` : ''
          );

          return {
            success: true,
            blockId: result.data.block_id as string | undefined,
            path: result.data.path as string | undefined,
            contentHash: result.data.content_hash as string | undefined,
            messageCount: result.data.message_count as number | undefined,
            crystallizedAt: result.data.crystallized_at as string | undefined,
          };
        }

        const errorMsg = result.error || 'Failed to crystallize';
        setError(errorMsg);
        setLoading(false);

        return {
          success: false,
          error: errorMsg,
        };
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to save';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Save failed:', message);
        return { success: false, error: message };
      }
    },
    [state, sessionId]
  );

  // =========================================================================
  // Discard
  // =========================================================================

  const discard = useCallback(async (): Promise<boolean> => {
    if (!state) {
      setError('No K-Block to discard');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      // FILE K-BLOCK: use kblockApi
      if (state.path !== null) {
        await kblockApi.discard(state.blockId);
        setState(null);
        setLoading(false);
        console.info('[useKBlock] Discarded file K-Block:', state.blockId);
        return true;
      }

      // DIALOGUE K-BLOCK: use invokeKBlock
      const result = await invokeKBlock('discard_thoughts', {
        session_id: sessionId,
      });

      if (result.success) {
        setState(null);
        setLoading(false);
        console.info('[useKBlock] Discarded dialogue K-Block:', state.blockId);
        return true;
      }

      const errorMsg = result.error || 'Failed to discard';
      setError(errorMsg);
      setLoading(false);
      return false;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to discard';
      setError(message);
      setLoading(false);
      console.error('[useKBlock] Discard failed:', message);
      return false;
    }
  }, [state, sessionId]);

  // =========================================================================
  // Checkpoint (File K-Blocks Only)
  // =========================================================================

  const checkpoint = useCallback(
    async (name: string): Promise<string | null> => {
      if (!state || state.path === null) {
        setError('No file K-Block for checkpoint');
        return null;
      }

      setLoading(true);
      setError(null);

      try {
        // Sync content first
        if (state.isDirty) {
          await kblockApi.viewEdit(state.blockId, 'prose', state.content);
        }

        const response = await kblockApi.checkpoint(state.blockId, name);

        // Add checkpoint to local state
        setState((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            checkpoints: [
              ...prev.checkpoints,
              {
                id: response.checkpoint_id,
                name: response.name,
                contentHash: '',
                createdAt: new Date().toISOString(),
              },
            ],
          };
        });

        setLoading(false);
        console.info('[useKBlock] Checkpoint created:', response.checkpoint_id, name);
        return response.checkpoint_id;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to create checkpoint';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Checkpoint failed:', message);
        return null;
      }
    },
    [state]
  );

  // =========================================================================
  // Rewind (File K-Blocks Only)
  // =========================================================================

  const rewind = useCallback(
    async (checkpointId: string): Promise<boolean> => {
      if (!state || state.path === null) {
        setError('No file K-Block for rewind');
        return false;
      }

      setLoading(true);
      setError(null);

      try {
        await kblockApi.rewind(state.blockId, checkpointId);

        // Refresh content from backend
        const response = await kblockApi.get(state.blockId);

        setState((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            content: response.content,
            isDirty: response.is_dirty,
            isolation: response.isolation,
            contentLength: response.content.length,
          };
        });

        setLoading(false);
        console.info('[useKBlock] Rewound to checkpoint:', checkpointId);
        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to rewind';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Rewind failed:', message);
        return false;
      }
    },
    [state]
  );

  // =========================================================================
  // Get References (File K-Blocks Only)
  // =========================================================================

  const getReferences = useCallback(async (): Promise<KBlockReference[]> => {
    if (!state || state.path === null) return [];

    try {
      const response = await kblockApi.references(state.blockId);
      return response.references || [];
    } catch (err) {
      console.error('[useKBlock] Failed to get references:', err);
      return [];
    }
  }, [state]);

  // =========================================================================
  // Reset (Local Only)
  // =========================================================================

  const reset = useCallback(() => {
    setState(null);
    setError(null);
    pendingRef.current?.abort();
  }, []);

  // =========================================================================
  // Zero Seed Methods
  // =========================================================================

  const createZeroSeed = useCallback(
    async (
      layer: 1 | 2 | 3 | 4 | 5 | 6 | 7,
      kind: string,
      content: string,
      lineage: string[]
    ): Promise<KBlockCreateResult> => {
      setLoading(true);
      setError(null);

      try {
        // Call backend API to create Zero Seed K-Block
        const data = await kblockApi.createZeroSeed(layer, kind, content, lineage);

        const newState: KBlockState = {
          blockId: data.block_id,
          path: data.path || null,
          content,
          baseContent: content,
          isolation: 'PRISTINE',
          isDirty: false,
          activeViews: [],
          checkpoints: [],
          contentLength: content.length,
          zeroSeedLayer: layer,
          zeroSeedKind: kind,
          lineage,
          hasProof: false,
          confidence: 1.0,
          parentBlocks: data.parent_blocks || [],
          childBlocks: data.child_blocks || [],
        };

        setState(newState);
        setLoading(false);

        console.info('[useKBlock] Created Zero Seed K-Block:', newState.blockId, `L${layer}`, kind);

        return {
          success: true,
          blockId: newState.blockId,
          path: newState.path || undefined,
          content: newState.content,
          baseContent: newState.baseContent,
          isolation: newState.isolation,
          isDirty: newState.isDirty,
        };
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to create Zero Seed K-Block';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Zero Seed create failed:', message);
        return { success: false, error: message };
      }
    },
    []
  );

  const addDerivation = useCallback(
    async (parentId: string) => {
      if (!state) {
        console.warn('[useKBlock] addDerivation called with no active K-Block');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        await kblockApi.addDerivation(state.blockId, parentId);

        setState((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            lineage: [...prev.lineage, parentId],
            parentBlocks: [...prev.parentBlocks, parentId],
          };
        });

        setLoading(false);
        console.info('[useKBlock] Added derivation:', parentId);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to add derivation';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Add derivation failed:', message);
      }
    },
    [state]
  );

  const removeDerivation = useCallback(
    async (parentId: string) => {
      if (!state) {
        console.warn('[useKBlock] removeDerivation called with no active K-Block');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        await kblockApi.removeDerivation(state.blockId, parentId);

        setState((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            lineage: prev.lineage.filter((id) => id !== parentId),
            parentBlocks: prev.parentBlocks.filter((id) => id !== parentId),
          };
        });

        setLoading(false);
        console.info('[useKBlock] Removed derivation:', parentId);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to remove derivation';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Remove derivation failed:', message);
      }
    },
    [state]
  );

  const setProof = useCallback(
    async (proof: ToulminProof) => {
      if (!state) {
        console.warn('[useKBlock] setProof called with no active K-Block');
        return;
      }

      setLoading(true);
      setError(null);

      try {
        const result = await kblockApi.setProof(state.blockId, proof);

        setState((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            hasProof: true,
            toulminProof: proof,
            // Update confidence from backend response
            confidence: result.confidence,
          };
        });

        setLoading(false);
        console.info('[useKBlock] Set proof:', proof.tier);
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to set proof';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Set proof failed:', message);
      }
    },
    [state]
  );

  const goToParent = useCallback(
    (index: number) => {
      if (!state) return;
      const parentId = state.parentBlocks[index];
      if (!parentId) {
        console.warn('[useKBlock] No parent at index:', index);
        return;
      }
      // Navigation is handled by the component using this hook
      // We just provide the callback interface
      console.info('[useKBlock] Navigate to parent:', parentId);
      // Component should call create(parentId) or similar
    },
    [state]
  );

  const goToChild = useCallback(
    (index: number) => {
      if (!state) return;
      const childId = state.childBlocks[index];
      if (!childId) {
        console.warn('[useKBlock] No child at index:', index);
        return;
      }
      console.info('[useKBlock] Navigate to child:', childId);
      // Component should call create(childId) or similar
    },
    [state]
  );

  return {
    state,
    kblock: state, // Backward compatibility alias
    loading,
    error,
    create,
    updateContent,
    appendThought,
    viewEdit,
    refresh,
    save,
    discard,
    checkpoint,
    rewind,
    getReferences,
    reset,
    // Zero Seed methods
    createZeroSeed,
    addDerivation,
    removeDerivation,
    setProof,
    goToParent,
    goToChild,
  };
}

// =============================================================================
// Backward-Compatible Exports
// =============================================================================

/**
 * Dialogue K-Block hook (backward compatible).
 * Auto-creates dialogue K-Block on mount.
 *
 * Usage:
 * ```tsx
 * const kblock = useDialogueKBlock('my-session');
 * await kblock.appendThought('Hello');
 * await kblock.save('Completed conversation');
 * ```
 */
export function useDialogueKBlock(sessionId: string = 'membrane-default') {
  return useKBlock({ sessionId, autoCreate: true, initialPath: null });
}

/**
 * File K-Block hook (backward compatible).
 * Does NOT auto-create — caller must call create(path).
 *
 * Usage:
 * ```tsx
 * const kblock = useFileKBlock();
 * const result = await kblock.create('/path/to/file.md');
 * if (result.success) {
 *   // Work with content
 * }
 * await kblock.save('Completed edit');
 * ```
 */
export function useFileKBlock() {
  return useKBlock({ autoCreate: false });
}

// Default export is the unified hook
export default useKBlock;
