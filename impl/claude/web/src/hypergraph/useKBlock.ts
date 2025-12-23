/**
 * useKBlock — K-Block integration for Hypergraph Editor
 *
 * "The K-Block is not where you edit a document.
 *  It's where you edit a possible world."
 *
 * This hook manages K-Block lifecycle for the editor:
 * - Auto-creates K-Block on INSERT mode entry
 * - Tracks content changes
 * - Handles witnessed save (:w) and discard (:q!)
 *
 * Philosophy:
 *   You're never editing the "real" file.
 *   You're editing a possible world.
 *   :w commits to cosmos (escapes isolation)
 *   :q! discards (no cosmic effects)
 */

import { useCallback, useEffect, useRef, useState } from 'react';
import { kblockApi } from '../api/client';
import type { KBlockIsolation } from '../api/client';

// =============================================================================
// Types
// =============================================================================

export interface KBlockState {
  /** K-Block ID from backend */
  blockId: string;

  /** File path */
  path: string;

  /** Current content (working copy) */
  content: string;

  /** Base content (original, for diffing) */
  baseContent: string;

  /** Isolation state */
  isolation: KBlockIsolation;

  /** Whether content has changed from base */
  isDirty: boolean;

  /** Active checkpoints */
  checkpoints: Array<{
    id: string;
    name: string;
    contentHash: string;
    createdAt: string;
  }>;
}

export interface UseKBlockResult {
  /** Current K-Block state (null if no K-Block active) */
  kblock: KBlockState | null;

  /** Whether a K-Block operation is in progress */
  loading: boolean;

  /** Last error message */
  error: string | null;

  /**
   * Create K-Block for a file path.
   * Called when entering INSERT mode.
   */
  create: (path: string) => Promise<KBlockState | null>;

  /**
   * Update content in the K-Block.
   * Called on every keystroke in INSERT mode.
   */
  updateContent: (content: string) => void;

  /**
   * Save K-Block to cosmos with witness message.
   * Called on :w command.
   *
   * @param reasoning - Witness message (why this change?)
   */
  save: (reasoning?: string) => Promise<boolean>;

  /**
   * Discard K-Block without saving.
   * Called on :q! command.
   */
  discard: () => Promise<boolean>;

  /**
   * Create a named checkpoint.
   * Called on :checkpoint command.
   */
  checkpoint: (name: string) => Promise<string | null>;

  /**
   * Rewind to a checkpoint.
   * Called on :rewind command.
   */
  rewind: (checkpointId: string) => Promise<boolean>;

  /**
   * Clear the K-Block state without calling backend.
   * Used when the component unmounts or mode exits.
   */
  clear: () => void;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook for managing K-Block lifecycle in the editor.
 */
export function useKBlock(): UseKBlockResult {
  const [kblock, setKblock] = useState<KBlockState | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Track pending operations to avoid race conditions
  const pendingRef = useRef<AbortController | null>(null);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      pendingRef.current?.abort();
    };
  }, []);

  // =========================================================================
  // Create K-Block
  // =========================================================================

  const create = useCallback(async (path: string): Promise<KBlockState | null> => {
    // Abort any pending operation
    pendingRef.current?.abort();
    const controller = new AbortController();
    pendingRef.current = controller;

    setLoading(true);
    setError(null);

    try {
      // Create K-Block on backend
      const response = await kblockApi.create(path);

      if (controller.signal.aborted) return null;

      // Fetch full content
      const contentResponse = await kblockApi.get(response.block_id);

      if (controller.signal.aborted) return null;

      const state: KBlockState = {
        blockId: contentResponse.block_id,
        path: contentResponse.path,
        content: contentResponse.content,
        baseContent: contentResponse.base_content,
        isolation: contentResponse.isolation as KBlockIsolation,
        isDirty: contentResponse.is_dirty,
        checkpoints: contentResponse.checkpoints.map((cp) => ({
          id: cp.id,
          name: cp.name,
          contentHash: cp.content_hash,
          createdAt: cp.created_at,
        })),
      };

      setKblock(state);
      setLoading(false);

      console.info('[useKBlock] Created K-Block:', state.blockId, 'for', path);
      return state;
    } catch (err) {
      if (controller.signal.aborted) return null;

      const message = err instanceof Error ? err.message : 'Failed to create K-Block';
      setError(message);
      setLoading(false);
      console.error('[useKBlock] Create failed:', message);
      return null;
    }
  }, []);

  // =========================================================================
  // Update Content (Local Only)
  // =========================================================================

  const updateContent = useCallback((content: string) => {
    setKblock((prev) => {
      if (!prev) return prev;
      return {
        ...prev,
        content,
        isDirty: content !== prev.baseContent,
        isolation: content !== prev.baseContent ? 'DIRTY' : 'PRISTINE',
      };
    });
  }, []);

  // =========================================================================
  // Save to Cosmos (Witnessed)
  // =========================================================================

  const save = useCallback(
    async (reasoning?: string): Promise<boolean> => {
      if (!kblock) {
        setError('No K-Block to save');
        return false;
      }

      if (!kblock.isDirty) {
        // Nothing to save
        console.info('[useKBlock] Nothing to save (not dirty)');
        return true;
      }

      setLoading(true);
      setError(null);

      try {
        // First, sync content to backend via view_edit
        await kblockApi.viewEdit(kblock.blockId, 'prose', kblock.content, reasoning);

        // Then commit to cosmos
        const response = await kblockApi.save(kblock.blockId, reasoning);

        if (!response.success) {
          throw new Error(response.error || 'Save failed');
        }

        // Clear K-Block state (it's now in cosmos)
        setKblock(null);
        setLoading(false);

        console.info(
          '[useKBlock] Saved K-Block:',
          kblock.blockId,
          reasoning ? `(${reasoning})` : ''
        );
        return true;
      } catch (err) {
        const message = err instanceof Error ? err.message : 'Failed to save K-Block';
        setError(message);
        setLoading(false);
        console.error('[useKBlock] Save failed:', message);
        return false;
      }
    },
    [kblock]
  );

  // =========================================================================
  // Discard (No Cosmic Effects)
  // =========================================================================

  const discardKblock = useCallback(async (): Promise<boolean> => {
    if (!kblock) {
      setError('No K-Block to discard');
      return false;
    }

    setLoading(true);
    setError(null);

    try {
      await kblockApi.discard(kblock.blockId);

      // Clear K-Block state
      setKblock(null);
      setLoading(false);

      console.info('[useKBlock] Discarded K-Block:', kblock.blockId);
      return true;
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Failed to discard K-Block';
      setError(message);
      setLoading(false);
      console.error('[useKBlock] Discard failed:', message);
      return false;
    }
  }, [kblock]);

  // =========================================================================
  // Checkpoint
  // =========================================================================

  const createCheckpoint = useCallback(
    async (name: string): Promise<string | null> => {
      if (!kblock) {
        setError('No K-Block for checkpoint');
        return null;
      }

      setLoading(true);
      setError(null);

      try {
        // Sync content first
        if (kblock.isDirty) {
          await kblockApi.viewEdit(kblock.blockId, 'prose', kblock.content);
        }

        const response = await kblockApi.checkpoint(kblock.blockId, name);

        // Add checkpoint to local state
        setKblock((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            checkpoints: [
              ...prev.checkpoints,
              {
                id: response.checkpoint_id,
                name: response.name,
                contentHash: '', // Backend doesn't return this
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
    [kblock]
  );

  // =========================================================================
  // Rewind
  // =========================================================================

  const rewindToCheckpoint = useCallback(
    async (checkpointId: string): Promise<boolean> => {
      if (!kblock) {
        setError('No K-Block for rewind');
        return false;
      }

      setLoading(true);
      setError(null);

      try {
        await kblockApi.rewind(kblock.blockId, checkpointId);

        // Refresh content from backend
        const contentResponse = await kblockApi.get(kblock.blockId);

        setKblock((prev) => {
          if (!prev) return prev;
          return {
            ...prev,
            content: contentResponse.content,
            isDirty: contentResponse.is_dirty,
            isolation: contentResponse.isolation as KBlockIsolation,
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
    [kblock]
  );

  // =========================================================================
  // Clear (Local Only)
  // =========================================================================

  const clear = useCallback(() => {
    setKblock(null);
    setError(null);
    pendingRef.current?.abort();
  }, []);

  return {
    kblock,
    loading,
    error,
    create,
    updateContent,
    save,
    discard: discardKblock,
    checkpoint: createCheckpoint,
    rewind: rewindToCheckpoint,
    clear,
  };
}
