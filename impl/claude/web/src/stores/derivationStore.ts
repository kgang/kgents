/**
 * Derivation Store - Zustand state for hypergraph derivation UX.
 *
 * Manages the consumer-first derivation flow where K-Blocks derive authority
 * from principles, which derive from constitutions. Tracks grounding status,
 * Galois loss (information compression), and project realization.
 *
 * @see spec/protocols/hypergraph-editor.md
 * @see docs/skills/hypergraph-editor.md
 */

import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { produce } from 'immer';

// =============================================================================
// Types
// =============================================================================

/**
 * Node types in the derivation hierarchy.
 * Constitution → Principle → K-Block (most abstract to most concrete)
 */
export type DerivationNodeType = 'constitution' | 'principle' | 'kblock';

/**
 * Grounding status indicates how well a node is anchored to higher-level abstractions.
 * - grounded: Has complete derivation path to constitution
 * - provisional: Has partial derivation (linked to principle but principle is orphan)
 * - orphan: No derivation path established
 */
export type GroundingStatus = 'grounded' | 'provisional' | 'orphan';

/**
 * A node in the derivation graph.
 */
export interface DerivationNode {
  /** Unique identifier */
  id: string;
  /** Human-readable label */
  label: string;
  /** Node type in the hierarchy */
  type: DerivationNodeType;
  /**
   * Galois loss: Information lost in the adjunction from abstract to concrete.
   * 0 = perfect preservation, 1 = complete loss. Lower is better.
   */
  galoisLoss: number;
  /** Current grounding status */
  groundingStatus: GroundingStatus;
  /** Parent node ID (null for root constitutions) */
  parentId: string | null;
  /** Child node IDs */
  childIds: string[];
  /** Optional content preview */
  content?: string;
  /** Creation timestamp */
  createdAt: Date;
  /** Last modification timestamp */
  updatedAt: Date;
}

/**
 * An edge representing a derivation relationship.
 */
export interface DerivationEdge {
  /** Unique edge identifier */
  id: string;
  /** Source node ID (parent/more abstract) */
  sourceId: string;
  /** Target node ID (child/more concrete) */
  targetId: string;
  /**
   * Galois loss for this specific edge.
   * Represents information loss in this derivation step.
   */
  galoisLoss: number;
  /** Edge label/description */
  label?: string;
}

/**
 * Summary of project coherence metrics.
 */
export interface CoherenceSummary {
  /** Total number of K-Blocks */
  totalKBlocks: number;
  /** Number of grounded K-Blocks */
  grounded: number;
  /** Number of provisionally grounded K-Blocks */
  provisional: number;
  /** Number of orphan K-Blocks */
  orphan: number;
  /** Average Galois loss across all K-Blocks (0-1) */
  averageGaloisLoss: number;
  /** Overall coherence percentage (grounded / total * 100) */
  coherencePercent: number;
}

/**
 * State of the project realization computation.
 */
export type RealizationState = 'idle' | 'scanning' | 'computing' | 'complete';

// =============================================================================
// API Types (for backend integration)
// =============================================================================

/** API response for derivation computation */
interface ComputeDerivationResponse {
  path: DerivationNode[];
  totalGaloisLoss: number;
  groundingStatus: GroundingStatus;
}

/** API response for grounding operation */
interface GroundKBlockResponse {
  success: boolean;
  node: DerivationNode;
  edge: DerivationEdge;
}

/** API response for project realization */
interface RealizeProjectResponse {
  summary: CoherenceSummary;
  nodes: DerivationNode[];
  edges: DerivationEdge[];
}

// =============================================================================
// State Interface
// =============================================================================

interface DerivationState {
  // Graph data
  /** All nodes indexed by ID */
  nodes: Map<string, DerivationNode>;
  /** All edges in the derivation graph */
  edges: DerivationEdge[];

  // Categorization (computed from nodes for fast lookup)
  /** IDs of fully grounded K-Blocks */
  groundedIds: Set<string>;
  /** IDs of provisionally grounded K-Blocks */
  provisionalIds: Set<string>;
  /** IDs of orphan K-Blocks */
  orphanIds: Set<string>;

  // Project coherence
  /** Summary metrics for the entire project */
  coherenceSummary: CoherenceSummary | null;
  /** Progress of realization computation (0-100) */
  realizationProgress: number;
  /** Current state of realization computation */
  realizationState: RealizationState;

  // Current selection
  /** Currently displayed derivation path */
  currentDerivationPath: DerivationNode[] | null;
  /** Currently selected principle for grounding */
  selectedPrincipleId: string | null;

  // Error handling
  /** Last error message */
  error: string | null;
  /** Whether an operation is in progress */
  isLoading: boolean;
}

// =============================================================================
// Actions Interface
// =============================================================================

interface DerivationActions {
  // Core operations
  /** Set all nodes (replaces existing) */
  setNodes: (nodes: Map<string, DerivationNode>) => void;
  /** Add a single node */
  addNode: (node: DerivationNode) => void;
  /** Update an existing node */
  updateNode: (id: string, updates: Partial<Omit<DerivationNode, 'id'>>) => void;
  /** Remove a node and its edges */
  removeNode: (id: string) => void;
  /** Add an edge between nodes */
  addEdge: (edge: DerivationEdge) => void;
  /** Remove an edge */
  removeEdge: (edgeId: string) => void;

  // Derivation computation
  /**
   * Compute the derivation path for a K-Block.
   * Traces from the K-Block up through principles to constitution.
   */
  computeDerivation: (kblockId: string) => Promise<void>;
  /**
   * Ground a K-Block by linking it to a principle.
   * Creates edge and updates grounding status.
   */
  groundKBlock: (kblockId: string, principleId: string) => Promise<void>;

  // Queries (pure functions, no state mutation)
  /** Get the full derivation path for a K-Block */
  getDerivationPath: (kblockId: string) => DerivationNode[];
  /** Get all downstream (child) node IDs */
  getDownstream: (nodeId: string) => string[];
  /** Get all upstream (parent) node IDs up to root */
  getUpstream: (nodeId: string) => string[];

  // Project realization
  /**
   * Compute coherence for an array of K-Block IDs.
   * Updates coherenceSummary and categorization sets.
   */
  realizeProject: (kblockIds: string[]) => Promise<void>;
  /** Update realization progress (0-100) */
  setRealizationProgress: (progress: number) => void;

  // Selection
  /** Set the currently displayed derivation path */
  setCurrentDerivationPath: (path: DerivationNode[] | null) => void;
  /** Set the selected principle for grounding operations */
  setSelectedPrinciple: (principleId: string | null) => void;

  // Utility
  /** Clear error state */
  clearError: () => void;
  /** Reset store to initial state */
  reset: () => void;

  // Internal helpers (exposed for testing)
  /** Recompute categorization sets from current nodes */
  _recomputeCategorization: () => void;
  /** Recompute coherence summary from current state */
  _recomputeCoherenceSummary: () => void;
}

// =============================================================================
// Store Type
// =============================================================================

export type DerivationStore = DerivationState & DerivationActions;

// =============================================================================
// Initial State
// =============================================================================

const initialState: DerivationState = {
  nodes: new Map(),
  edges: [],
  groundedIds: new Set(),
  provisionalIds: new Set(),
  orphanIds: new Set(),
  coherenceSummary: null,
  realizationProgress: 0,
  realizationState: 'idle',
  currentDerivationPath: null,
  selectedPrincipleId: null,
  error: null,
  isLoading: false,
};

// =============================================================================
// API Integration Helpers
// =============================================================================

const API_BASE = '/api/derivation';

/**
 * Fetch derivation path from backend.
 * Falls back to local computation if API unavailable.
 */
async function fetchDerivationPath(kblockId: string): Promise<ComputeDerivationResponse> {
  const response = await fetch(`${API_BASE}/compute/${kblockId}`);
  if (!response.ok) {
    throw new Error(`Failed to compute derivation: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Submit grounding request to backend.
 */
async function submitGrounding(
  kblockId: string,
  principleId: string
): Promise<GroundKBlockResponse> {
  const response = await fetch(`${API_BASE}/ground`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kblockId, principleId }),
  });
  if (!response.ok) {
    throw new Error(`Failed to ground K-Block: ${response.statusText}`);
  }
  return await response.json();
}

/**
 * Submit project realization request to backend.
 */
async function submitRealization(kblockIds: string[]): Promise<RealizeProjectResponse> {
  const response = await fetch(`${API_BASE}/realize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kblockIds }),
  });
  if (!response.ok) {
    throw new Error(`Failed to realize project: ${response.statusText}`);
  }
  return await response.json();
}

// =============================================================================
// Store Implementation
// =============================================================================

export const useDerivationStore = create<DerivationStore>()(
  persist(
    (set, get) => ({
      ...initialState,

      // =========================================================================
      // Core Operations
      // =========================================================================

      setNodes: (nodes) => {
        set(
          produce((state: DerivationState) => {
            state.nodes = nodes;
          })
        );
        get()._recomputeCategorization();
        get()._recomputeCoherenceSummary();
      },

      addNode: (node) => {
        set(
          produce((state: DerivationState) => {
            state.nodes.set(node.id, node);
          })
        );
        get()._recomputeCategorization();
      },

      updateNode: (id, updates) => {
        set(
          produce((state: DerivationState) => {
            const existing = state.nodes.get(id);
            if (existing) {
              state.nodes.set(id, {
                ...existing,
                ...updates,
                updatedAt: new Date(),
              });
            }
          })
        );
        if (updates.groundingStatus) {
          get()._recomputeCategorization();
        }
      },

      removeNode: (id) => {
        set(
          produce((state: DerivationState) => {
            const node = state.nodes.get(id);
            if (!node) return;

            // Remove from parent's childIds
            if (node.parentId) {
              const parent = state.nodes.get(node.parentId);
              if (parent) {
                parent.childIds = parent.childIds.filter((cid) => cid !== id);
              }
            }

            // Orphan children
            for (const childId of node.childIds) {
              const child = state.nodes.get(childId);
              if (child) {
                child.parentId = null;
                child.groundingStatus = 'orphan';
              }
            }

            // Remove associated edges
            state.edges = state.edges.filter((e) => e.sourceId !== id && e.targetId !== id);

            // Remove node
            state.nodes.delete(id);
          })
        );
        get()._recomputeCategorization();
        get()._recomputeCoherenceSummary();
      },

      addEdge: (edge) => {
        set(
          produce((state: DerivationState) => {
            // Avoid duplicate edges
            const exists = state.edges.some(
              (e) => e.sourceId === edge.sourceId && e.targetId === edge.targetId
            );
            if (!exists) {
              state.edges.push(edge);
            }
          })
        );
      },

      removeEdge: (edgeId) => {
        set(
          produce((state: DerivationState) => {
            state.edges = state.edges.filter((e) => e.id !== edgeId);
          })
        );
      },

      // =========================================================================
      // Derivation Computation
      // =========================================================================

      computeDerivation: async (kblockId) => {
        const { nodes } = get();
        const node = nodes.get(kblockId);

        if (!node) {
          set({ error: `K-Block not found: ${kblockId}` });
          return;
        }

        set({ isLoading: true, error: null });

        try {
          // Try API first
          const response = await fetchDerivationPath(kblockId);
          set({
            currentDerivationPath: response.path,
            isLoading: false,
          });

          // Update node grounding status from response
          get().updateNode(kblockId, {
            groundingStatus: response.groundingStatus,
            galoisLoss: response.totalGaloisLoss,
          });
        } catch {
          // Fall back to local computation
          const path = get().getDerivationPath(kblockId);
          set({
            currentDerivationPath: path,
            isLoading: false,
          });
        }
      },

      groundKBlock: async (kblockId, principleId) => {
        const { nodes } = get();
        const kblock = nodes.get(kblockId);
        const principle = nodes.get(principleId);

        if (!kblock) {
          set({ error: `K-Block not found: ${kblockId}` });
          return;
        }
        if (!principle) {
          set({ error: `Principle not found: ${principleId}` });
          return;
        }
        if (principle.type !== 'principle') {
          set({ error: `Target must be a principle, got: ${principle.type}` });
          return;
        }

        set({ isLoading: true, error: null });

        try {
          // Try API first
          const response = await submitGrounding(kblockId, principleId);

          if (response.success) {
            get().updateNode(kblockId, {
              parentId: principleId,
              groundingStatus: response.node.groundingStatus,
              galoisLoss: response.edge.galoisLoss,
            });
            get().addEdge(response.edge);
          }
        } catch {
          // Fall back to local grounding
          const edgeId = `edge-${kblockId}-${principleId}`;
          const newGroundingStatus: GroundingStatus =
            principle.groundingStatus === 'grounded' ? 'grounded' : 'provisional';

          // Estimate Galois loss based on hierarchy distance
          const estimatedLoss = principle.groundingStatus === 'grounded' ? 0.1 : 0.3;

          set(
            produce((state: DerivationState) => {
              const kblockNode = state.nodes.get(kblockId);
              const principleNode = state.nodes.get(principleId);

              if (kblockNode && principleNode) {
                // Update K-Block
                kblockNode.parentId = principleId;
                kblockNode.groundingStatus = newGroundingStatus;
                kblockNode.galoisLoss = estimatedLoss;
                kblockNode.updatedAt = new Date();

                // Add to principle's children
                if (!principleNode.childIds.includes(kblockId)) {
                  principleNode.childIds.push(kblockId);
                }

                // Add edge
                state.edges.push({
                  id: edgeId,
                  sourceId: principleId,
                  targetId: kblockId,
                  galoisLoss: estimatedLoss,
                });
              }
            })
          );
        }

        set({ isLoading: false });
        get()._recomputeCategorization();
        get()._recomputeCoherenceSummary();
      },

      // =========================================================================
      // Queries
      // =========================================================================

      getDerivationPath: (kblockId) => {
        const { nodes } = get();
        const path: DerivationNode[] = [];
        let currentId: string | null = kblockId;

        // Walk up the tree
        while (currentId) {
          const node = nodes.get(currentId);
          if (!node) break;
          path.unshift(node); // Add to beginning
          currentId = node.parentId;
        }

        return path;
      },

      getDownstream: (nodeId) => {
        const { nodes } = get();
        const result: string[] = [];
        const queue: string[] = [nodeId];

        while (queue.length > 0) {
          const currentId = queue.shift();
          if (!currentId) continue;
          const node = nodes.get(currentId);
          if (node) {
            for (const childId of node.childIds) {
              result.push(childId);
              queue.push(childId);
            }
          }
        }

        return result;
      },

      getUpstream: (nodeId) => {
        const { nodes } = get();
        const result: string[] = [];
        let currentId: string | null = nodes.get(nodeId)?.parentId ?? null;

        while (currentId) {
          result.push(currentId);
          currentId = nodes.get(currentId)?.parentId ?? null;
        }

        return result;
      },

      // =========================================================================
      // Project Realization
      // =========================================================================

      realizeProject: async (kblockIds) => {
        set({
          isLoading: true,
          realizationState: 'scanning',
          realizationProgress: 0,
          error: null,
        });

        try {
          // Try API first
          set({ realizationState: 'computing', realizationProgress: 30 });
          const response = await submitRealization(kblockIds);

          set(
            produce((state: DerivationState) => {
              // Update nodes from response
              for (const node of response.nodes) {
                state.nodes.set(node.id, node);
              }
              // Replace edges
              state.edges = response.edges;
              // Update summary
              state.coherenceSummary = response.summary;
            })
          );

          set({
            realizationProgress: 100,
            realizationState: 'complete',
            isLoading: false,
          });
        } catch {
          // Fall back to local computation
          set({ realizationState: 'computing', realizationProgress: 50 });

          // Compute locally
          get()._recomputeCategorization();
          get()._recomputeCoherenceSummary();

          set({
            realizationProgress: 100,
            realizationState: 'complete',
            isLoading: false,
          });
        }
      },

      setRealizationProgress: (progress) => {
        set({ realizationProgress: Math.min(100, Math.max(0, progress)) });
      },

      // =========================================================================
      // Selection
      // =========================================================================

      setCurrentDerivationPath: (path) => {
        set({ currentDerivationPath: path });
      },

      setSelectedPrinciple: (principleId) => {
        set({ selectedPrincipleId: principleId });
      },

      // =========================================================================
      // Utility
      // =========================================================================

      clearError: () => {
        set({ error: null });
      },

      reset: () => {
        set(initialState);
      },

      // =========================================================================
      // Internal Helpers
      // =========================================================================

      _recomputeCategorization: () => {
        set(
          produce((state: DerivationState) => {
            state.groundedIds.clear();
            state.provisionalIds.clear();
            state.orphanIds.clear();

            for (const [id, node] of state.nodes) {
              if (node.type !== 'kblock') continue;

              switch (node.groundingStatus) {
                case 'grounded':
                  state.groundedIds.add(id);
                  break;
                case 'provisional':
                  state.provisionalIds.add(id);
                  break;
                case 'orphan':
                  state.orphanIds.add(id);
                  break;
              }
            }
          })
        );
      },

      _recomputeCoherenceSummary: () => {
        const { nodes } = get();

        // Filter to K-Blocks only
        const kblocks = Array.from(nodes.values()).filter((n) => n.type === 'kblock');
        const totalKBlocks = kblocks.length;

        if (totalKBlocks === 0) {
          set({ coherenceSummary: null });
          return;
        }

        const grounded = kblocks.filter((n) => n.groundingStatus === 'grounded').length;
        const provisional = kblocks.filter((n) => n.groundingStatus === 'provisional').length;
        const orphan = kblocks.filter((n) => n.groundingStatus === 'orphan').length;

        const totalLoss = kblocks.reduce((sum, n) => sum + n.galoisLoss, 0);
        const averageGaloisLoss = totalLoss / totalKBlocks;

        const coherencePercent = (grounded / totalKBlocks) * 100;

        set({
          coherenceSummary: {
            totalKBlocks,
            grounded,
            provisional,
            orphan,
            averageGaloisLoss,
            coherencePercent,
          },
        });
      },
    }),
    {
      name: 'kgents-derivation',
      // Only persist essential data, not computed state
      partialize: (state) => ({
        nodes: state.nodes,
        edges: state.edges,
        selectedPrincipleId: state.selectedPrincipleId,
      }),
      // Custom serialization for Map/Set (handled by immer's enableMapSet)
      storage: {
        getItem: (name) => {
          const str = localStorage.getItem(name);
          if (!str) return null;
          const parsed = JSON.parse(str);
          // Reconstruct Map from serialized form
          if (parsed.state?.nodes) {
            parsed.state.nodes = new Map(Object.entries(parsed.state.nodes));
          }
          return parsed;
        },
        setItem: (name, value) => {
          // Serialize Map to object for localStorage
          const toStore = {
            ...value,
            state: {
              ...value.state,
              nodes: value.state.nodes ? Object.fromEntries(value.state.nodes) : {},
            },
          };
          localStorage.setItem(name, JSON.stringify(toStore));
        },
        removeItem: (name) => localStorage.removeItem(name),
      },
    }
  )
);

// =============================================================================
// Selectors
// =============================================================================

/** Select all grounded K-Block IDs */
export const selectGroundedKBlocks = (state: DerivationStore): string[] =>
  Array.from(state.groundedIds);

/** Select all provisional K-Block IDs */
export const selectProvisionalKBlocks = (state: DerivationStore): string[] =>
  Array.from(state.provisionalIds);

/** Select all orphan K-Block IDs */
export const selectOrphanKBlocks = (state: DerivationStore): string[] =>
  Array.from(state.orphanIds);

/** Select coherence percentage (0-100) */
export const selectCoherencePercent = (state: DerivationStore): number =>
  state.coherenceSummary?.coherencePercent ?? 0;

/** Select average Galois loss (0-1) */
export const selectAverageGaloisLoss = (state: DerivationStore): number =>
  state.coherenceSummary?.averageGaloisLoss ?? 0;

/** Select whether a specific node is grounded */
export const selectIsGrounded =
  (nodeId: string) =>
  (state: DerivationStore): boolean =>
    state.groundedIds.has(nodeId);

/** Select all principles (for grounding UI) */
export const selectAllPrinciples = (state: DerivationStore): DerivationNode[] =>
  Array.from(state.nodes.values()).filter((n) => n.type === 'principle');

/** Select all constitutions */
export const selectAllConstitutions = (state: DerivationStore): DerivationNode[] =>
  Array.from(state.nodes.values()).filter((n) => n.type === 'constitution');

/** Select all K-Blocks */
export const selectAllKBlocks = (state: DerivationStore): DerivationNode[] =>
  Array.from(state.nodes.values()).filter((n) => n.type === 'kblock');

/** Select node by ID */
export const selectNodeById =
  (id: string) =>
  (state: DerivationStore): DerivationNode | undefined =>
    state.nodes.get(id);

/** Select whether realization is in progress */
export const selectIsRealizing = (state: DerivationStore): boolean =>
  state.realizationState !== 'idle' && state.realizationState !== 'complete';

/** Select realization progress with state label */
export const selectRealizationStatus = (
  state: DerivationStore
): { progress: number; state: RealizationState; label: string } => {
  const labels: Record<RealizationState, string> = {
    idle: 'Ready',
    scanning: 'Scanning K-Blocks...',
    computing: 'Computing coherence...',
    complete: 'Complete',
  };
  return {
    progress: state.realizationProgress,
    state: state.realizationState,
    label: labels[state.realizationState],
  };
};

// =============================================================================
// Derived Helpers (for components)
// =============================================================================

/**
 * Hook to get coherence color based on percentage.
 * Green (>80%), Yellow (50-80%), Red (<50%)
 */
export function getCoherenceColor(percent: number): string {
  if (percent >= 80) return 'text-green-400';
  if (percent >= 50) return 'text-yellow-400';
  return 'text-red-400';
}

/**
 * Hook to get Galois loss color based on value.
 * Green (<0.2), Yellow (0.2-0.5), Red (>0.5)
 */
export function getGaloisLossColor(loss: number): string {
  if (loss < 0.2) return 'text-green-400';
  if (loss < 0.5) return 'text-yellow-400';
  return 'text-red-400';
}

/**
 * Format Galois loss as percentage string.
 */
export function formatGaloisLoss(loss: number): string {
  return `${(loss * 100).toFixed(1)}%`;
}

/**
 * Get icon for grounding status.
 */
export function getGroundingIcon(status: GroundingStatus): string {
  switch (status) {
    case 'grounded':
      return '●'; // Solid circle
    case 'provisional':
      return '◐'; // Half circle
    case 'orphan':
      return '○'; // Empty circle
  }
}

/**
 * Get CSS class for grounding status.
 */
export function getGroundingStatusClass(status: GroundingStatus): string {
  switch (status) {
    case 'grounded':
      return 'text-green-400 bg-green-400/10';
    case 'provisional':
      return 'text-yellow-400 bg-yellow-400/10';
    case 'orphan':
      return 'text-red-400 bg-red-400/10';
  }
}
