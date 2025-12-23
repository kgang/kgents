/**
 * useLivingSpec: Unified hook for living spec operations.
 *
 * Combines:
 * - useFileKBlock for transactional editing
 * - useWitnessStream for real-time witness events
 * - State machine for unified spec states
 *
 * Philosophy:
 *   "Five specs become one. The bramble becomes a garden."
 */

import { useCallback, useMemo, useState } from 'react';
import { useWitnessStream, type WitnessEvent } from './useWitnessStream';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

/**
 * Unified spec states (from SpecPolynomial).
 */
export type SpecState =
  | 'viewing'
  | 'hovering'
  | 'expanding'
  | 'navigating'
  | 'editing'
  | 'syncing'
  | 'conflicting'
  | 'witnessing';

/**
 * Isolation states (from K-Block).
 */
export type IsolationState = 'PRISTINE' | 'DIRTY' | 'STALE' | 'CONFLICTING' | 'ENTANGLED';

/**
 * Token from spec content.
 */
export interface SpecToken {
  token_type: string;
  span: [number, number];
  value: string;
  metadata?: Record<string, unknown>;
}

/**
 * Hyperedge in the spec graph.
 */
export interface SpecEdge {
  edge_type: string;
  destinations: string[];
  count: number;
}

/**
 * Living spec state.
 */
export interface LivingSpecState {
  // Core
  path: string | null;
  state: SpecState;

  // Content
  content: string;
  baseContent: string;

  // Isolation
  isolation: IsolationState;
  isDirty: boolean;
  monadId: string | null;

  // Tokens & Edges
  tokens: SpecToken[];
  edges: Record<string, string[]>;

  // Loading states
  isLoading: boolean;
  error: string | null;

  // Witness
  witnessEvents: WitnessEvent[];
  witnessConnected: boolean;
}

/**
 * Living spec actions.
 */
export interface LivingSpecActions {
  // Lifecycle
  open: (path: string) => Promise<void>;
  close: () => void;

  // Editing
  enterEdit: () => void;
  update: (content: string, reasoning?: string) => Promise<void>;
  save: (reasoning: string) => Promise<{ versionId: string; markId?: string }>;
  discard: () => void;

  // Checkpoints
  checkpoint: (name: string) => Promise<string>;
  rewind: (checkpointId: string) => Promise<void>;

  // Navigation
  navigate: (edgeType: string) => Promise<string[]>;
  expand: (
    edgeType: string
  ) => Promise<{ destinations: string[]; content: Record<string, string> }>;

  // State transitions
  transition: (action: string) => void;
}

// -----------------------------------------------------------------------------
// API Client
// -----------------------------------------------------------------------------

const API_BASE = '/agentese';

async function invokeAGENTESE<T>(
  path: string,
  aspect: string,
  params: Record<string, unknown> = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}/${path.replace(/\./g, '/')}/${aspect}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(params),
  });

  if (!response.ok) {
    const error = await response.text();
    throw new Error(`AGENTESE ${path}.${aspect} failed: ${error}`);
  }

  const result = await response.json();
  return result as T;
}

interface ManifestResult {
  summary: string;
  content: string;
  metadata: {
    path: string;
    kind: string;
    tokens: SpecToken[];
    edges: Record<string, string[]>;
    isolation: string;
    monad_active: boolean;
  };
}

interface EditResult {
  summary: string;
  content: string;
  metadata: {
    monad_id: string;
    isolation: string;
    is_dirty: boolean;
    base_hash: string;
  };
}

interface CommitResult {
  summary: string;
  content: string;
  metadata: {
    version_id: string;
    mark_id: string | null;
    path: string;
    delta_summary: string;
  };
}

interface NavigateResult {
  summary: string;
  content: string;
  metadata: {
    edge_type: string;
    destinations: string[];
    count: number;
  };
}

// -----------------------------------------------------------------------------
// Hook
// -----------------------------------------------------------------------------

export function useLivingSpec(): LivingSpecState & LivingSpecActions {
  // Witness stream
  const witness = useWitnessStream();

  // Core state
  const [path, setPath] = useState<string | null>(null);
  const [state, setState] = useState<SpecState>('viewing');
  const [content, setContent] = useState('');
  const [baseContent, setBaseContent] = useState('');
  const [isolation, setIsolation] = useState<IsolationState>('PRISTINE');
  const [monadId, setMonadId] = useState<string | null>(null);
  const [tokens, setTokens] = useState<SpecToken[]>([]);
  const [edges, setEdges] = useState<Record<string, string[]>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Derived state
  const isDirty = content !== baseContent;

  // Filter witness events for current path
  const witnessEvents = useMemo(
    () => witness.events.filter((e) => e.path === path),
    [witness.events, path]
  );

  // -------------------------------------------------------------------------
  // Lifecycle
  // -------------------------------------------------------------------------

  const open = useCallback(async (specPath: string) => {
    setIsLoading(true);
    setError(null);

    try {
      const result = await invokeAGENTESE<ManifestResult>('self.spec', 'manifest', {
        path: specPath,
      });

      setPath(specPath);
      setContent(result.content);
      setBaseContent(result.content);
      setTokens(result.metadata.tokens);
      setEdges(result.metadata.edges);
      setIsolation(result.metadata.isolation as IsolationState);
      setMonadId(result.metadata.monad_active ? 'active' : null);
      setState('viewing');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to open spec');
    } finally {
      setIsLoading(false);
    }
  }, []);

  const close = useCallback(() => {
    setPath(null);
    setContent('');
    setBaseContent('');
    setTokens([]);
    setEdges({});
    setIsolation('PRISTINE');
    setMonadId(null);
    setState('viewing');
    setError(null);
  }, []);

  // -------------------------------------------------------------------------
  // Editing
  // -------------------------------------------------------------------------

  const enterEdit = useCallback(async () => {
    if (!path) return;

    setIsLoading(true);
    try {
      const result = await invokeAGENTESE<EditResult>('self.spec', 'edit', { path });

      setContent(result.content);
      setBaseContent(result.content);
      setMonadId(result.metadata.monad_id);
      setIsolation(result.metadata.isolation as IsolationState);
      setState('editing');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to enter edit mode');
    } finally {
      setIsLoading(false);
    }
  }, [path]);

  const update = useCallback(
    async (newContent: string, reasoning?: string) => {
      if (!path || !monadId) return;

      setContent(newContent);
      setIsolation(newContent !== baseContent ? 'DIRTY' : 'PRISTINE');

      // Debounced API call for persistence
      try {
        await invokeAGENTESE('self.spec', 'update', {
          path,
          content: newContent,
          reasoning,
        });
      } catch (e) {
        // Optimistic update already applied, log error
        console.error('Update failed:', e);
      }
    },
    [path, monadId, baseContent]
  );

  const save = useCallback(
    async (reasoning: string) => {
      if (!path || !monadId) {
        throw new Error('No active edit to save');
      }

      setState('syncing');
      setIsLoading(true);

      try {
        const result = await invokeAGENTESE<CommitResult>('self.spec', 'commit', {
          path,
          reasoning,
        });

        setBaseContent(content);
        setIsolation('PRISTINE');
        setMonadId(null);
        setState('witnessing');

        // After brief witness prompt, return to viewing
        setTimeout(() => setState('viewing'), 1500);

        return {
          versionId: result.metadata.version_id,
          markId: result.metadata.mark_id || undefined,
        };
      } catch (e) {
        setState('editing');
        throw e;
      } finally {
        setIsLoading(false);
      }
    },
    [path, monadId, content]
  );

  const discard = useCallback(async () => {
    if (!path) return;

    try {
      await invokeAGENTESE('self.spec', 'discard', { path });
      setContent(baseContent);
      setIsolation('PRISTINE');
      setMonadId(null);
      setState('viewing');
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to discard');
    }
  }, [path, baseContent]);

  // -------------------------------------------------------------------------
  // Checkpoints
  // -------------------------------------------------------------------------

  const checkpoint = useCallback(
    async (name: string) => {
      if (!path || !monadId) {
        throw new Error('No active edit for checkpoint');
      }

      const result = await invokeAGENTESE<{ metadata: { checkpoint_id: string } }>(
        'self.spec',
        'checkpoint',
        { path, name }
      );

      return result.metadata.checkpoint_id;
    },
    [path, monadId]
  );

  const rewind = useCallback(
    async (checkpointId: string) => {
      if (!path || !monadId) {
        throw new Error('No active edit for rewind');
      }

      const result = await invokeAGENTESE<{ content: string }>('self.spec', 'rewind', {
        path,
        checkpoint_id: checkpointId,
      });

      setContent(result.content);
      setIsolation('DIRTY');
    },
    [path, monadId]
  );

  // -------------------------------------------------------------------------
  // Navigation
  // -------------------------------------------------------------------------

  const navigate = useCallback(
    async (edgeType: string) => {
      if (!path) return [];

      setState('navigating');
      try {
        const result = await invokeAGENTESE<NavigateResult>('self.spec', 'navigate', {
          path,
          edge_type: edgeType,
        });

        setState('viewing');
        return result.metadata.destinations;
      } catch (e) {
        setState('viewing');
        throw e;
      }
    },
    [path]
  );

  const expand = useCallback(
    async (edgeType: string) => {
      if (!path) {
        throw new Error('No path for expansion');
      }

      setState('expanding');
      try {
        const result = await invokeAGENTESE<{
          metadata: {
            destinations: string[];
            state: string;
          };
          content: string;
        }>('self.spec', 'expand', { path, edge_type: edgeType });

        setState('viewing');

        // Parse content into destination map
        const contentMap: Record<string, string> = {};
        const parts = result.content.split('\n---\n');
        for (const part of parts) {
          const match = part.match(/^## (.+)\n([\s\S]*)/);
          if (match) {
            contentMap[match[1]] = match[2];
          }
        }

        return {
          destinations: result.metadata.destinations,
          content: contentMap,
        };
      } catch (e) {
        setState('viewing');
        throw e;
      }
    },
    [path]
  );

  // -------------------------------------------------------------------------
  // State Transitions
  // -------------------------------------------------------------------------

  const transition = useCallback(
    (action: string) => {
      // State machine transitions (simplified for frontend)
      const transitions: Record<string, Record<string, SpecState>> = {
        viewing: {
          hover: 'hovering',
          edit: 'editing',
          expand: 'expanding',
          navigate: 'navigating',
        },
        hovering: {
          leave: 'viewing',
          expand: 'expanding',
        },
        expanding: {
          complete: 'viewing',
          error: 'viewing',
        },
        navigating: {
          arrive: 'viewing',
          backtrack: 'viewing',
        },
        editing: {
          save: 'syncing',
          cancel: 'viewing',
        },
        syncing: {
          complete: 'witnessing',
          conflict: 'conflicting',
        },
        conflicting: {
          resolve: 'witnessing',
          abort: 'viewing',
        },
        witnessing: {
          mark: 'viewing',
          skip: 'viewing',
        },
      };

      const newState = transitions[state]?.[action];
      if (newState) {
        setState(newState);
      }
    },
    [state]
  );

  // -------------------------------------------------------------------------
  // Return
  // -------------------------------------------------------------------------

  return {
    // State
    path,
    state,
    content,
    baseContent,
    isolation,
    isDirty,
    monadId,
    tokens,
    edges,
    isLoading,
    error,
    witnessEvents,
    witnessConnected: witness.connected,

    // Actions
    open,
    close,
    enterEdit,
    update,
    save,
    discard,
    checkpoint,
    rewind,
    navigate,
    expand,
    transition,
  };
}
