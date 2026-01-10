# ASHC Consumer Integration: Zustand Store Extensions

**Status**: DESIGN SPECIFICATION
**Created**: 2025-01-10
**Purpose**: Extend hypergraph editor state management for derivation context and graph

---

## Overview

This specification defines Zustand store extensions that integrate ASHC derivation tracking into the hypergraph editor's frontend. The stores manage derivation context for K-Blocks, the derivation graph, and UI state for derivation visualization.

**Philosophy**: "The proof IS the decision. The mark IS the witness."

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        ZUSTAND STORE ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐       │
│  │  DerivationStore│◄───►│   KBlockStore   │◄───►│     UIStore     │       │
│  │   (new slice)   │     │   (extended)    │     │   (extended)    │       │
│  └────────┬────────┘     └────────┬────────┘     └────────┬────────┘       │
│           │                       │                       │                 │
│           │    Subscriptions      │   Cross-store sync    │                 │
│           └───────────────────────┼───────────────────────┘                 │
│                                   │                                         │
│                                   ▼                                         │
│                     ┌─────────────────────────┐                             │
│                     │   Backend API (ASHC)    │                             │
│                     │ /agentese/self/ashc/*   │                             │
│                     └─────────────────────────┘                             │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 1. Core Type Definitions

```typescript
// =============================================================================
// File: impl/claude/web/src/stores/derivation/types.ts
// =============================================================================

/**
 * Derivation tier categorization.
 * From ASHC: lower rank = more foundational.
 */
export type DerivationTier = 'AXIOM' | 'BOOTSTRAP' | 'FUNCTOR' | 'EMPIRICAL';

/**
 * Path kind for derivation edges.
 */
export type PathKind = 'REFL' | 'DERIVE' | 'COMPOSE' | 'TRANSPORT' | 'UNIVALENCE';

/**
 * Witness type for derivation evidence.
 */
export type WitnessType =
  | 'PRINCIPLE'    // Grounded in constitutional principle
  | 'SPEC'         // Grounded in specification
  | 'TEST'         // Verified by test
  | 'PROOF'        // Formally proven (Lean)
  | 'LLM'          // LLM-generated reasoning
  | 'COMPOSITION'  // Derived through composition
  | 'GALOIS';      // Galois loss measurement

/**
 * A witness mark in the derivation graph.
 * Links to witness protocol marks.
 */
export interface DerivationWitness {
  /** Unique witness ID (links to witness mark) */
  id: string;

  /** Type of witness */
  type: WitnessType;

  /** Confidence score (0-1) */
  confidence: number;

  /** Human-readable description */
  description: string;

  /** Optional grounding principle ID */
  principleId?: string;

  /** Timestamp */
  timestamp: string;

  /** Optional source location (file:line) */
  sourceLocation?: string;
}

/**
 * A node in the derivation graph.
 * Corresponds to a K-Block with derivation context.
 */
export interface DerivationNode {
  /** K-Block ID (primary key) */
  kblockId: string;

  /** Display label */
  label: string;

  /** File path (if file-backed K-Block) */
  path?: string;

  /** Derivation tier */
  tier: DerivationTier;

  /** Whether this node is grounded (has path to axiom) */
  isGrounded: boolean;

  /** Grounding principle (if grounded) */
  groundingPrinciple?: string;

  /** Accumulated Galois loss from axiom */
  galoisLoss: number;

  /** Constitutional scores (principle -> score) */
  constitutionalScores: Record<string, number>;

  /** Overall confidence (product of path confidences) */
  confidence: number;

  /** Witnesses for this node */
  witnesses: DerivationWitness[];

  /** Parent K-Block IDs */
  parents: string[];

  /** Child K-Block IDs */
  children: string[];

  /** Metadata */
  createdAt: string;
  updatedAt: string;
}

/**
 * An edge in the derivation graph.
 * Represents a derivation relationship between K-Blocks.
 */
export interface DerivationEdge {
  /** Unique edge ID */
  id: string;

  /** Source K-Block ID */
  sourceId: string;

  /** Target K-Block ID */
  targetId: string;

  /** Path kind */
  kind: PathKind;

  /** Edge confidence */
  confidence: number;

  /** Galois loss for this edge */
  galoisLoss: number;

  /** Witnesses supporting this edge */
  witnesses: DerivationWitness[];

  /** Is this edge stale (needs revalidation)? */
  stale: boolean;
}

/**
 * Full derivation path from source to target.
 * Computed path through the DAG.
 */
export interface DerivationPath {
  /** Source K-Block ID */
  sourceId: string;

  /** Target K-Block ID */
  targetId: string;

  /** Ordered list of edge IDs in the path */
  edges: string[];

  /** Total Galois loss accumulated */
  totalLoss: number;

  /** Minimum confidence along path */
  minConfidence: number;

  /** Grounding principle (if path reaches axiom) */
  groundingPrinciple?: string;
}

/**
 * Project-level coherence summary.
 */
export interface CoherenceSummary {
  /** Total K-Blocks in project */
  totalKBlocks: number;

  /** Number of grounded K-Blocks */
  groundedCount: number;

  /** Number of provisional K-Blocks */
  provisionalCount: number;

  /** Number of orphan K-Blocks */
  orphanCount: number;

  /** Overall coherence score (0-1) */
  coherenceScore: number;

  /** Average Galois loss across grounded paths */
  averageLoss: number;

  /** Constitutional scores by principle */
  principleScores: Record<string, number>;

  /** Timestamp of last computation */
  computedAt: string;
}

/**
 * Derivation context for a single K-Block.
 * What the UI needs to display derivation state.
 */
export interface DerivationContext {
  /** K-Block ID */
  kblockId: string;

  /** Is this K-Block grounded? */
  isGrounded: boolean;

  /** Path to grounding principle (if grounded) */
  groundingPath?: DerivationPath;

  /** Upstream dependencies */
  upstream: DerivationNode[];

  /** Downstream dependents */
  downstream: DerivationNode[];

  /** Active witnesses */
  witnesses: DerivationWitness[];

  /** Coherence status */
  status: 'grounded' | 'provisional' | 'orphan';
}
```

---

## 2. DerivationStore (New Store)

```typescript
// =============================================================================
// File: impl/claude/web/src/stores/derivation/derivationStore.ts
// =============================================================================

import { create } from 'zustand';
import { persist, subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type {
  DerivationNode,
  DerivationEdge,
  DerivationPath,
  DerivationContext,
  CoherenceSummary,
  DerivationTier,
} from './types';

// =============================================================================
// State Interface
// =============================================================================

interface DerivationState {
  // -------------------------------------------------------------------------
  // Derivation Graph
  // -------------------------------------------------------------------------

  /** All derivation nodes by K-Block ID */
  nodes: Map<string, DerivationNode>;

  /** All derivation edges */
  edges: DerivationEdge[];

  /** Edge index: sourceId -> edges */
  edgesBySource: Map<string, DerivationEdge[]>;

  /** Edge index: targetId -> edges */
  edgesByTarget: Map<string, DerivationEdge[]>;

  // -------------------------------------------------------------------------
  // Categorization (computed from graph)
  // -------------------------------------------------------------------------

  /** K-Block IDs with path to axiom */
  grounded: Set<string>;

  /** K-Block IDs with parents but no axiom path */
  provisional: Set<string>;

  /** K-Block IDs with no parents (unconnected) */
  orphans: Set<string>;

  // -------------------------------------------------------------------------
  // Project Coherence
  // -------------------------------------------------------------------------

  /** Overall coherence summary */
  coherenceSummary: CoherenceSummary | null;

  /** Last coherence computation timestamp */
  coherenceStale: boolean;

  // -------------------------------------------------------------------------
  // Loading State
  // -------------------------------------------------------------------------

  /** Is the graph loading? */
  loading: boolean;

  /** Last error message */
  error: string | null;

  /** K-Block IDs currently being computed */
  computing: Set<string>;
}

interface DerivationActions {
  // -------------------------------------------------------------------------
  // Graph Operations
  // -------------------------------------------------------------------------

  /**
   * Load derivation graph from backend.
   * Called on app init and after major changes.
   */
  loadGraph: () => Promise<void>;

  /**
   * Add or update a derivation node.
   */
  upsertNode: (node: DerivationNode) => void;

  /**
   * Add a derivation edge.
   */
  addEdge: (edge: DerivationEdge) => void;

  /**
   * Remove a derivation edge.
   */
  removeEdge: (edgeId: string) => void;

  /**
   * Mark edges as stale (needs revalidation).
   */
  markEdgesStale: (edgeIds: string[]) => void;

  // -------------------------------------------------------------------------
  // Derivation Context (Per K-Block)
  // -------------------------------------------------------------------------

  /**
   * Compute derivation context for a K-Block.
   * Called when focusing a K-Block in the editor.
   */
  computeDerivation: (kblockId: string) => Promise<DerivationContext>;

  /**
   * Ground a K-Block to a constitutional principle.
   * Creates AXIOM derivation with principle witness.
   */
  groundKBlock: (kblockId: string, principleId: string) => Promise<void>;

  /**
   * Derive one K-Block from another.
   * Creates DERIVE edge with optional witnesses.
   */
  deriveKBlock: (
    sourceId: string,
    targetId: string,
    witnesses?: string[]
  ) => Promise<void>;

  // -------------------------------------------------------------------------
  // Path Queries
  // -------------------------------------------------------------------------

  /**
   * Get the derivation path from a K-Block to its grounding axiom.
   * Returns null if not grounded.
   */
  getDerivationPath: (kblockId: string) => DerivationPath | null;

  /**
   * Get all downstream K-Blocks that depend on this one.
   */
  getDownstream: (kblockId: string) => string[];

  /**
   * Get all upstream K-Blocks this one depends on.
   */
  getUpstream: (kblockId: string) => string[];

  // -------------------------------------------------------------------------
  // Coherence
  // -------------------------------------------------------------------------

  /**
   * Recompute project coherence summary.
   */
  computeCoherence: () => Promise<void>;

  /**
   * Mark coherence as needing recomputation.
   */
  invalidateCoherence: () => void;

  // -------------------------------------------------------------------------
  // Selectors (computed values)
  // -------------------------------------------------------------------------

  /** Select all grounded K-Blocks */
  selectGroundedNodes: () => DerivationNode[];

  /** Select all orphan K-Blocks */
  selectOrphanNodes: () => DerivationNode[];

  /** Select nodes by tier */
  selectNodesByTier: (tier: DerivationTier) => DerivationNode[];

  /** Select overall coherence score */
  selectCoherence: () => number;

  /** Select node by ID */
  selectNode: (kblockId: string) => DerivationNode | undefined;

  // -------------------------------------------------------------------------
  // Reset
  // -------------------------------------------------------------------------

  /** Clear all state */
  reset: () => void;
}

type DerivationStore = DerivationState & DerivationActions;

// =============================================================================
// Initial State
// =============================================================================

const initialState: DerivationState = {
  nodes: new Map(),
  edges: [],
  edgesBySource: new Map(),
  edgesByTarget: new Map(),
  grounded: new Set(),
  provisional: new Set(),
  orphans: new Set(),
  coherenceSummary: null,
  coherenceStale: true,
  loading: false,
  error: null,
  computing: new Set(),
};

// =============================================================================
// API Helpers
// =============================================================================

const API_BASE = '/agentese/self/ashc';

async function fetchDerivationGraph(): Promise<{
  nodes: DerivationNode[];
  edges: DerivationEdge[];
}> {
  const response = await fetch(`${API_BASE}/graph`);
  if (!response.ok) {
    throw new Error(`Failed to load derivation graph: ${response.statusText}`);
  }
  return response.json();
}

async function fetchDerivationContext(kblockId: string): Promise<DerivationContext> {
  const response = await fetch(`${API_BASE}/context/${encodeURIComponent(kblockId)}`);
  if (!response.ok) {
    throw new Error(`Failed to compute derivation: ${response.statusText}`);
  }
  return response.json();
}

async function postGrounding(kblockId: string, principleId: string): Promise<void> {
  const response = await fetch(`${API_BASE}/ground`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ kblock_id: kblockId, principle_id: principleId }),
  });
  if (!response.ok) {
    throw new Error(`Failed to ground K-Block: ${response.statusText}`);
  }
}

async function postDerive(
  sourceId: string,
  targetId: string,
  witnessIds: string[]
): Promise<DerivationEdge> {
  const response = await fetch(`${API_BASE}/derive`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      source_id: sourceId,
      target_id: targetId,
      witness_ids: witnessIds,
    }),
  });
  if (!response.ok) {
    throw new Error(`Failed to create derivation: ${response.statusText}`);
  }
  return response.json();
}

async function fetchCoherence(): Promise<CoherenceSummary> {
  const response = await fetch(`${API_BASE}/coherence`);
  if (!response.ok) {
    throw new Error(`Failed to compute coherence: ${response.statusText}`);
  }
  return response.json();
}

// =============================================================================
// Store Implementation
// =============================================================================

export const useDerivationStore = create<DerivationStore>()(
  subscribeWithSelector(
    persist(
      immer((set, get) => ({
        ...initialState,

        // =====================================================================
        // Graph Operations
        // =====================================================================

        loadGraph: async () => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            const { nodes, edges } = await fetchDerivationGraph();

            set((state) => {
              // Clear and rebuild
              state.nodes.clear();
              state.edges = [];
              state.edgesBySource.clear();
              state.edgesByTarget.clear();
              state.grounded.clear();
              state.provisional.clear();
              state.orphans.clear();

              // Add nodes
              for (const node of nodes) {
                state.nodes.set(node.kblockId, node);

                // Categorize
                if (node.isGrounded) {
                  state.grounded.add(node.kblockId);
                } else if (node.parents.length > 0) {
                  state.provisional.add(node.kblockId);
                } else {
                  state.orphans.add(node.kblockId);
                }
              }

              // Add edges and build indices
              for (const edge of edges) {
                state.edges.push(edge);

                // Source index
                const sourceEdges = state.edgesBySource.get(edge.sourceId) || [];
                sourceEdges.push(edge);
                state.edgesBySource.set(edge.sourceId, sourceEdges);

                // Target index
                const targetEdges = state.edgesByTarget.get(edge.targetId) || [];
                targetEdges.push(edge);
                state.edgesByTarget.set(edge.targetId, targetEdges);
              }

              state.loading = false;
              state.coherenceStale = true;
            });
          } catch (err) {
            set((state) => {
              state.loading = false;
              state.error = err instanceof Error ? err.message : 'Failed to load graph';
            });
          }
        },

        upsertNode: (node) => {
          set((state) => {
            state.nodes.set(node.kblockId, node);

            // Update categorization
            state.grounded.delete(node.kblockId);
            state.provisional.delete(node.kblockId);
            state.orphans.delete(node.kblockId);

            if (node.isGrounded) {
              state.grounded.add(node.kblockId);
            } else if (node.parents.length > 0) {
              state.provisional.add(node.kblockId);
            } else {
              state.orphans.add(node.kblockId);
            }

            state.coherenceStale = true;
          });
        },

        addEdge: (edge) => {
          set((state) => {
            state.edges.push(edge);

            // Update indices
            const sourceEdges = state.edgesBySource.get(edge.sourceId) || [];
            sourceEdges.push(edge);
            state.edgesBySource.set(edge.sourceId, sourceEdges);

            const targetEdges = state.edgesByTarget.get(edge.targetId) || [];
            targetEdges.push(edge);
            state.edgesByTarget.set(edge.targetId, targetEdges);

            state.coherenceStale = true;
          });
        },

        removeEdge: (edgeId) => {
          set((state) => {
            const edgeIndex = state.edges.findIndex((e) => e.id === edgeId);
            if (edgeIndex === -1) return;

            const edge = state.edges[edgeIndex];
            state.edges.splice(edgeIndex, 1);

            // Update indices
            const sourceEdges = state.edgesBySource.get(edge.sourceId);
            if (sourceEdges) {
              const idx = sourceEdges.findIndex((e) => e.id === edgeId);
              if (idx !== -1) sourceEdges.splice(idx, 1);
            }

            const targetEdges = state.edgesByTarget.get(edge.targetId);
            if (targetEdges) {
              const idx = targetEdges.findIndex((e) => e.id === edgeId);
              if (idx !== -1) targetEdges.splice(idx, 1);
            }

            state.coherenceStale = true;
          });
        },

        markEdgesStale: (edgeIds) => {
          set((state) => {
            for (const edge of state.edges) {
              if (edgeIds.includes(edge.id)) {
                edge.stale = true;
              }
            }
          });
        },

        // =====================================================================
        // Derivation Context
        // =====================================================================

        computeDerivation: async (kblockId) => {
          const { computing } = get();
          if (computing.has(kblockId)) {
            // Already computing, return cached or wait
            const node = get().nodes.get(kblockId);
            if (node) {
              return {
                kblockId,
                isGrounded: node.isGrounded,
                upstream: [],
                downstream: [],
                witnesses: node.witnesses,
                status: node.isGrounded ? 'grounded' : node.parents.length > 0 ? 'provisional' : 'orphan',
              };
            }
          }

          set((state) => {
            state.computing.add(kblockId);
          });

          try {
            const context = await fetchDerivationContext(kblockId);

            set((state) => {
              state.computing.delete(kblockId);

              // Update node if returned
              for (const node of [...context.upstream, ...context.downstream]) {
                if (!state.nodes.has(node.kblockId)) {
                  state.nodes.set(node.kblockId, node);
                }
              }
            });

            return context;
          } catch (err) {
            set((state) => {
              state.computing.delete(kblockId);
              state.error = err instanceof Error ? err.message : 'Failed to compute derivation';
            });

            // Return minimal context on error
            return {
              kblockId,
              isGrounded: false,
              upstream: [],
              downstream: [],
              witnesses: [],
              status: 'orphan' as const,
            };
          }
        },

        groundKBlock: async (kblockId, principleId) => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            await postGrounding(kblockId, principleId);

            // Reload graph to get updated state
            await get().loadGraph();
          } catch (err) {
            set((state) => {
              state.loading = false;
              state.error = err instanceof Error ? err.message : 'Failed to ground K-Block';
            });
          }
        },

        deriveKBlock: async (sourceId, targetId, witnesses = []) => {
          set((state) => {
            state.loading = true;
            state.error = null;
          });

          try {
            const edge = await postDerive(sourceId, targetId, witnesses);
            get().addEdge(edge);

            set((state) => {
              state.loading = false;
            });
          } catch (err) {
            set((state) => {
              state.loading = false;
              state.error = err instanceof Error ? err.message : 'Failed to create derivation';
            });
          }
        },

        // =====================================================================
        // Path Queries
        // =====================================================================

        getDerivationPath: (kblockId) => {
          const { nodes, edgesByTarget, grounded } = get();

          if (!grounded.has(kblockId)) {
            return null;
          }

          // BFS to find path to axiom
          const visited = new Set<string>();
          const queue: Array<{ id: string; edges: string[]; loss: number; minConf: number }> = [
            { id: kblockId, edges: [], loss: 0, minConf: 1 },
          ];

          while (queue.length > 0) {
            const current = queue.shift()!;
            if (visited.has(current.id)) continue;
            visited.add(current.id);

            const node = nodes.get(current.id);
            if (!node) continue;

            // Found axiom?
            if (node.tier === 'AXIOM') {
              return {
                sourceId: kblockId,
                targetId: current.id,
                edges: current.edges,
                totalLoss: current.loss,
                minConfidence: current.minConf,
                groundingPrinciple: node.groundingPrinciple,
              };
            }

            // Add parent edges to queue
            const parentEdges = edgesByTarget.get(current.id) || [];
            for (const edge of parentEdges) {
              if (!visited.has(edge.sourceId)) {
                queue.push({
                  id: edge.sourceId,
                  edges: [...current.edges, edge.id],
                  loss: current.loss + edge.galoisLoss,
                  minConf: Math.min(current.minConf, edge.confidence),
                });
              }
            }
          }

          return null;
        },

        getDownstream: (kblockId) => {
          const { edgesBySource } = get();
          const result: string[] = [];
          const visited = new Set<string>();
          const queue = [kblockId];

          while (queue.length > 0) {
            const current = queue.shift()!;
            if (visited.has(current)) continue;
            visited.add(current);

            const childEdges = edgesBySource.get(current) || [];
            for (const edge of childEdges) {
              if (!visited.has(edge.targetId)) {
                result.push(edge.targetId);
                queue.push(edge.targetId);
              }
            }
          }

          return result;
        },

        getUpstream: (kblockId) => {
          const { edgesByTarget } = get();
          const result: string[] = [];
          const visited = new Set<string>();
          const queue = [kblockId];

          while (queue.length > 0) {
            const current = queue.shift()!;
            if (visited.has(current)) continue;
            visited.add(current);

            const parentEdges = edgesByTarget.get(current) || [];
            for (const edge of parentEdges) {
              if (!visited.has(edge.sourceId)) {
                result.push(edge.sourceId);
                queue.push(edge.sourceId);
              }
            }
          }

          return result;
        },

        // =====================================================================
        // Coherence
        // =====================================================================

        computeCoherence: async () => {
          set((state) => {
            state.loading = true;
          });

          try {
            const summary = await fetchCoherence();

            set((state) => {
              state.coherenceSummary = summary;
              state.coherenceStale = false;
              state.loading = false;
            });
          } catch (err) {
            set((state) => {
              state.loading = false;
              state.error = err instanceof Error ? err.message : 'Failed to compute coherence';
            });
          }
        },

        invalidateCoherence: () => {
          set((state) => {
            state.coherenceStale = true;
          });
        },

        // =====================================================================
        // Selectors
        // =====================================================================

        selectGroundedNodes: () => {
          const { nodes, grounded } = get();
          return Array.from(grounded).map((id) => nodes.get(id)!).filter(Boolean);
        },

        selectOrphanNodes: () => {
          const { nodes, orphans } = get();
          return Array.from(orphans).map((id) => nodes.get(id)!).filter(Boolean);
        },

        selectNodesByTier: (tier) => {
          const { nodes } = get();
          return Array.from(nodes.values()).filter((n) => n.tier === tier);
        },

        selectCoherence: () => {
          const { coherenceSummary } = get();
          return coherenceSummary?.coherenceScore ?? 0;
        },

        selectNode: (kblockId) => {
          return get().nodes.get(kblockId);
        },

        // =====================================================================
        // Reset
        // =====================================================================

        reset: () => {
          set(initialState);
        },
      })),
      {
        name: 'kgents-derivation',
        partialize: (state) => ({
          // Only persist nodes and edges (rebuild indices on hydration)
          nodes: Array.from(state.nodes.entries()),
          edges: state.edges,
        }),
        // Custom storage to handle Map serialization
        storage: {
          getItem: (name) => {
            const str = localStorage.getItem(name);
            if (!str) return null;
            const data = JSON.parse(str);
            if (data.state?.nodes) {
              data.state.nodes = new Map(data.state.nodes);
            }
            return data;
          },
          setItem: (name, value) => {
            const data = { ...value };
            if (data.state?.nodes instanceof Map) {
              data.state.nodes = Array.from(data.state.nodes.entries());
            }
            localStorage.setItem(name, JSON.stringify(data));
          },
          removeItem: (name) => localStorage.removeItem(name),
        },
      }
    )
  )
);

// =============================================================================
// Convenience Selectors (for use with shallow comparison)
// =============================================================================

export const selectDerivationLoading = (state: DerivationStore) => state.loading;
export const selectDerivationError = (state: DerivationStore) => state.error;
export const selectGroundedCount = (state: DerivationStore) => state.grounded.size;
export const selectOrphanCount = (state: DerivationStore) => state.orphans.size;
export const selectCoherenceStale = (state: DerivationStore) => state.coherenceStale;
```

---

## 3. KBlockStore Extension

```typescript
// =============================================================================
// File: impl/claude/web/src/stores/kblock/kblockStore.ts
// =============================================================================

import { create } from 'zustand';
import { subscribeWithSelector } from 'zustand/middleware';
import { immer } from 'zustand/middleware/immer';
import type { KBlockState as BaseKBlockState } from '@/hypergraph/useKBlock';
import type { DerivationContext, DerivationTier } from '../derivation/types';

/**
 * Extended K-Block state with derivation context.
 */
export interface KBlockWithDerivation extends BaseKBlockState {
  /** Derivation context (computed on focus) */
  derivationContext: DerivationContext | null;

  /** Derivation tier (from ASHC) */
  derivationTier: DerivationTier;

  /** Is derivation context loading? */
  derivationLoading: boolean;

  /** Derivation-related error */
  derivationError: string | null;
}

interface KBlockStoreState {
  /** Currently active K-Block (with derivation) */
  activeKBlock: KBlockWithDerivation | null;

  /** Recently accessed K-Blocks (LRU cache) */
  recentKBlocks: Map<string, KBlockWithDerivation>;

  /** Maximum recent K-Blocks to cache */
  maxRecent: number;
}

interface KBlockStoreActions {
  /** Set the active K-Block */
  setActiveKBlock: (kblock: BaseKBlockState | null) => void;

  /** Update derivation context for active K-Block */
  setDerivationContext: (context: DerivationContext | null) => void;

  /** Set derivation loading state */
  setDerivationLoading: (loading: boolean) => void;

  /** Set derivation error */
  setDerivationError: (error: string | null) => void;

  /** Update derivation tier */
  setDerivationTier: (tier: DerivationTier) => void;

  /** Clear active K-Block */
  clearActiveKBlock: () => void;

  /** Get recent K-Block by ID */
  getRecentKBlock: (kblockId: string) => KBlockWithDerivation | undefined;

  /** Register derivation change callback */
  onDerivationChange: (callback: (context: DerivationContext | null) => void) => () => void;
}

type KBlockStore = KBlockStoreState & KBlockStoreActions;

// =============================================================================
// Store Implementation
// =============================================================================

const MAX_RECENT = 20;

export const useKBlockStore = create<KBlockStore>()(
  subscribeWithSelector(
    immer((set, get) => ({
      activeKBlock: null,
      recentKBlocks: new Map(),
      maxRecent: MAX_RECENT,

      setActiveKBlock: (kblock) => {
        if (!kblock) {
          set((state) => {
            state.activeKBlock = null;
          });
          return;
        }

        set((state) => {
          // Convert to extended type
          const extended: KBlockWithDerivation = {
            ...kblock,
            derivationContext: null,
            derivationTier: 'EMPIRICAL',
            derivationLoading: true,
            derivationError: null,
          };

          state.activeKBlock = extended;

          // Add to recent (LRU)
          state.recentKBlocks.delete(kblock.blockId); // Remove if exists
          state.recentKBlocks.set(kblock.blockId, extended);

          // Trim to max size
          if (state.recentKBlocks.size > state.maxRecent) {
            const oldest = state.recentKBlocks.keys().next().value;
            if (oldest) state.recentKBlocks.delete(oldest);
          }
        });
      },

      setDerivationContext: (context) => {
        set((state) => {
          if (state.activeKBlock) {
            state.activeKBlock.derivationContext = context;
            state.activeKBlock.derivationLoading = false;

            // Determine tier from context
            if (context?.isGrounded && context.groundingPath?.edges.length === 0) {
              state.activeKBlock.derivationTier = 'AXIOM';
            } else if (context?.isGrounded) {
              state.activeKBlock.derivationTier = 'FUNCTOR';
            } else if (context?.status === 'provisional') {
              state.activeKBlock.derivationTier = 'BOOTSTRAP';
            } else {
              state.activeKBlock.derivationTier = 'EMPIRICAL';
            }

            // Update in recent cache too
            if (state.recentKBlocks.has(state.activeKBlock.blockId)) {
              state.recentKBlocks.set(state.activeKBlock.blockId, state.activeKBlock);
            }
          }
        });
      },

      setDerivationLoading: (loading) => {
        set((state) => {
          if (state.activeKBlock) {
            state.activeKBlock.derivationLoading = loading;
          }
        });
      },

      setDerivationError: (error) => {
        set((state) => {
          if (state.activeKBlock) {
            state.activeKBlock.derivationError = error;
            state.activeKBlock.derivationLoading = false;
          }
        });
      },

      setDerivationTier: (tier) => {
        set((state) => {
          if (state.activeKBlock) {
            state.activeKBlock.derivationTier = tier;
          }
        });
      },

      clearActiveKBlock: () => {
        set((state) => {
          state.activeKBlock = null;
        });
      },

      getRecentKBlock: (kblockId) => {
        return get().recentKBlocks.get(kblockId);
      },

      onDerivationChange: (callback) => {
        // Subscribe to derivation context changes
        return useKBlockStore.subscribe(
          (state) => state.activeKBlock?.derivationContext,
          callback
        );
      },
    }))
  )
);

// =============================================================================
// Selectors
// =============================================================================

export const selectActiveKBlock = (state: KBlockStore) => state.activeKBlock;
export const selectDerivationContext = (state: KBlockStore) =>
  state.activeKBlock?.derivationContext;
export const selectDerivationTier = (state: KBlockStore) =>
  state.activeKBlock?.derivationTier ?? 'EMPIRICAL';
export const selectDerivationLoading = (state: KBlockStore) =>
  state.activeKBlock?.derivationLoading ?? false;
export const selectIsGrounded = (state: KBlockStore) =>
  state.activeKBlock?.derivationContext?.isGrounded ?? false;
```

---

## 4. UIStore Extension

```typescript
// =============================================================================
// File: impl/claude/web/src/stores/uiStore.ts (extended)
// =============================================================================

import { create } from 'zustand';
import type { DerivationPath, DerivationNode } from './derivation/types';

// Add to existing UIState interface:
interface DerivationUIState {
  // -------------------------------------------------------------------------
  // Trail Bar State
  // -------------------------------------------------------------------------

  /** Current derivation path being displayed in trail bar */
  currentDerivationPath: DerivationPath | null;

  /** Expanded nodes in the trail (for collapsible view) */
  expandedTrailNodes: Set<string>;

  // -------------------------------------------------------------------------
  // Graph View State
  // -------------------------------------------------------------------------

  /** Selected principle for filtering graph view */
  selectedPrinciple: string | null;

  /** Graph view mode */
  graphViewMode: 'full' | 'grounded' | 'orphans' | 'selected';

  /** Selected nodes in graph view */
  selectedGraphNodes: Set<string>;

  /** Highlighted path in graph view */
  highlightedPath: string[] | null;

  // -------------------------------------------------------------------------
  // Dialogs
  // -------------------------------------------------------------------------

  /** Is grounding dialog open? */
  isGroundingDialogOpen: boolean;

  /** K-Block ID being grounded */
  groundingKBlockId: string | null;

  /** Is derivation dialog open? */
  isDerivationDialogOpen: boolean;

  /** Source K-Block for derivation */
  derivationSourceId: string | null;

  // -------------------------------------------------------------------------
  // Panels
  // -------------------------------------------------------------------------

  /** Is derivation panel expanded? */
  isDerivationPanelExpanded: boolean;

  /** Derivation panel height (for resizing) */
  derivationPanelHeight: number;
}

interface DerivationUIActions {
  // Trail Bar
  setCurrentDerivationPath: (path: DerivationPath | null) => void;
  toggleTrailNode: (nodeId: string) => void;
  expandAllTrailNodes: () => void;
  collapseAllTrailNodes: () => void;

  // Graph View
  setSelectedPrinciple: (principleId: string | null) => void;
  setGraphViewMode: (mode: 'full' | 'grounded' | 'orphans' | 'selected') => void;
  selectGraphNode: (nodeId: string) => void;
  deselectGraphNode: (nodeId: string) => void;
  clearGraphSelection: () => void;
  setHighlightedPath: (edgeIds: string[] | null) => void;

  // Dialogs
  openGroundingDialog: (kblockId: string) => void;
  closeGroundingDialog: () => void;
  openDerivationDialog: (sourceId: string) => void;
  closeDerivationDialog: () => void;

  // Panels
  toggleDerivationPanel: () => void;
  setDerivationPanelHeight: (height: number) => void;
}

// Add to useUIStore implementation:

const derivationUIInitialState: DerivationUIState = {
  currentDerivationPath: null,
  expandedTrailNodes: new Set(),
  selectedPrinciple: null,
  graphViewMode: 'full',
  selectedGraphNodes: new Set(),
  highlightedPath: null,
  isGroundingDialogOpen: false,
  groundingKBlockId: null,
  isDerivationDialogOpen: false,
  derivationSourceId: null,
  isDerivationPanelExpanded: true,
  derivationPanelHeight: 200,
};

// Actions to add:
const derivationUIActions = (set: any, get: any): DerivationUIActions => ({
  // Trail Bar
  setCurrentDerivationPath: (path) =>
    set({ currentDerivationPath: path }),

  toggleTrailNode: (nodeId) =>
    set((state: any) => {
      const expanded = new Set(state.expandedTrailNodes);
      if (expanded.has(nodeId)) {
        expanded.delete(nodeId);
      } else {
        expanded.add(nodeId);
      }
      return { expandedTrailNodes: expanded };
    }),

  expandAllTrailNodes: () =>
    set((state: any) => {
      const path = state.currentDerivationPath;
      if (!path) return {};
      // This would need the edges to be resolved to nodes
      return { expandedTrailNodes: new Set(path.edges) };
    }),

  collapseAllTrailNodes: () =>
    set({ expandedTrailNodes: new Set() }),

  // Graph View
  setSelectedPrinciple: (principleId) =>
    set({ selectedPrinciple: principleId }),

  setGraphViewMode: (mode) =>
    set({ graphViewMode: mode }),

  selectGraphNode: (nodeId) =>
    set((state: any) => ({
      selectedGraphNodes: new Set(state.selectedGraphNodes).add(nodeId),
    })),

  deselectGraphNode: (nodeId) =>
    set((state: any) => {
      const selected = new Set(state.selectedGraphNodes);
      selected.delete(nodeId);
      return { selectedGraphNodes: selected };
    }),

  clearGraphSelection: () =>
    set({ selectedGraphNodes: new Set() }),

  setHighlightedPath: (edgeIds) =>
    set({ highlightedPath: edgeIds }),

  // Dialogs
  openGroundingDialog: (kblockId) =>
    set({ isGroundingDialogOpen: true, groundingKBlockId: kblockId }),

  closeGroundingDialog: () =>
    set({ isGroundingDialogOpen: false, groundingKBlockId: null }),

  openDerivationDialog: (sourceId) =>
    set({ isDerivationDialogOpen: true, derivationSourceId: sourceId }),

  closeDerivationDialog: () =>
    set({ isDerivationDialogOpen: false, derivationSourceId: null }),

  // Panels
  toggleDerivationPanel: () =>
    set((state: any) => ({
      isDerivationPanelExpanded: !state.isDerivationPanelExpanded,
    })),

  setDerivationPanelHeight: (height) =>
    set({ derivationPanelHeight: height }),
});
```

---

## 5. Cross-Store Subscriptions

```typescript
// =============================================================================
// File: impl/claude/web/src/stores/derivation/subscriptions.ts
// =============================================================================

import { useDerivationStore } from './derivationStore';
import { useKBlockStore } from '../kblock/kblockStore';
import { useUIStore } from '../uiStore';

/**
 * Set up cross-store subscriptions.
 * Call this once at app initialization.
 */
export function setupDerivationSubscriptions(): () => void {
  const unsubscribers: Array<() => void> = [];

  // -------------------------------------------------------------------------
  // When active K-Block changes, compute derivation context
  // -------------------------------------------------------------------------

  unsubscribers.push(
    useKBlockStore.subscribe(
      (state) => state.activeKBlock?.blockId,
      async (blockId) => {
        if (!blockId) {
          useKBlockStore.getState().setDerivationContext(null);
          useUIStore.getState().setCurrentDerivationPath(null);
          return;
        }

        const derivationStore = useDerivationStore.getState();
        const kblockStore = useKBlockStore.getState();

        kblockStore.setDerivationLoading(true);

        try {
          const context = await derivationStore.computeDerivation(blockId);
          kblockStore.setDerivationContext(context);

          // Update trail bar
          if (context.isGrounded && context.groundingPath) {
            useUIStore.getState().setCurrentDerivationPath(context.groundingPath);
          } else {
            useUIStore.getState().setCurrentDerivationPath(null);
          }
        } catch (err) {
          kblockStore.setDerivationError(
            err instanceof Error ? err.message : 'Failed to compute derivation'
          );
        }
      }
    )
  );

  // -------------------------------------------------------------------------
  // When derivation graph changes, invalidate coherence
  // -------------------------------------------------------------------------

  unsubscribers.push(
    useDerivationStore.subscribe(
      (state) => state.edges.length,
      () => {
        useDerivationStore.getState().invalidateCoherence();
      }
    )
  );

  // -------------------------------------------------------------------------
  // When grounding dialog closes after success, reload graph
  // -------------------------------------------------------------------------

  unsubscribers.push(
    useUIStore.subscribe(
      (state) => state.isGroundingDialogOpen,
      async (isOpen, wasOpen) => {
        if (wasOpen && !isOpen) {
          // Dialog just closed, reload graph
          await useDerivationStore.getState().loadGraph();
        }
      }
    )
  );

  // -------------------------------------------------------------------------
  // Cleanup function
  // -------------------------------------------------------------------------

  return () => {
    for (const unsubscribe of unsubscribers) {
      unsubscribe();
    }
  };
}

/**
 * Hook for components that need derivation state.
 * Combines KBlockStore and DerivationStore.
 */
export function useDerivationState() {
  const activeKBlock = useKBlockStore((state) => state.activeKBlock);
  const derivationContext = useKBlockStore(
    (state) => state.activeKBlock?.derivationContext
  );
  const derivationLoading = useKBlockStore(
    (state) => state.activeKBlock?.derivationLoading ?? false
  );
  const coherenceSummary = useDerivationStore((state) => state.coherenceSummary);
  const currentPath = useUIStore((state) => state.currentDerivationPath);

  return {
    kblock: activeKBlock,
    derivation: derivationContext,
    loading: derivationLoading,
    coherence: coherenceSummary,
    currentPath,
    isGrounded: derivationContext?.isGrounded ?? false,
  };
}
```

---

## 6. Performance Considerations

### Memoization Strategy

```typescript
// =============================================================================
// File: impl/claude/web/src/stores/derivation/selectors.ts
// =============================================================================

import { createSelector } from 'reselect';
import type { DerivationStore } from './derivationStore';

/**
 * Memoized selector for grounded nodes.
 * Only recomputes when grounded set changes.
 */
export const selectGroundedNodesMemoized = createSelector(
  [(state: DerivationStore) => state.nodes, (state: DerivationStore) => state.grounded],
  (nodes, grounded) => {
    return Array.from(grounded)
      .map((id) => nodes.get(id))
      .filter(Boolean);
  }
);

/**
 * Memoized selector for edges by K-Block.
 */
export const selectEdgesForKBlock = createSelector(
  [
    (state: DerivationStore) => state.edgesBySource,
    (state: DerivationStore) => state.edgesByTarget,
    (_: DerivationStore, kblockId: string) => kblockId,
  ],
  (bySource, byTarget, kblockId) => ({
    outgoing: bySource.get(kblockId) ?? [],
    incoming: byTarget.get(kblockId) ?? [],
  })
);

/**
 * Memoized coherence score selector.
 */
export const selectCoherenceScoreMemoized = createSelector(
  [(state: DerivationStore) => state.coherenceSummary],
  (summary) => summary?.coherenceScore ?? 0
);

/**
 * Memoized node count by tier.
 */
export const selectNodeCountByTier = createSelector(
  [(state: DerivationStore) => state.nodes],
  (nodes) => {
    const counts = { AXIOM: 0, BOOTSTRAP: 0, FUNCTOR: 0, EMPIRICAL: 0 };
    for (const node of nodes.values()) {
      counts[node.tier]++;
    }
    return counts;
  }
);
```

### Persistence Strategy

```typescript
// Local Storage Schema (persisted):
// - nodes: Serialized Map entries
// - edges: Array of DerivationEdge
// - coherenceSummary: Last computed summary (can be recomputed)

// NOT persisted (rebuilt from above):
// - edgesBySource, edgesByTarget: Index maps
// - grounded, provisional, orphans: Categorization sets
// - loading, error, computing: Transient state

// Backend Sync:
// - Full reload on app init: loadGraph()
// - Incremental on changes: addEdge(), removeEdge()
// - Periodic coherence: computeCoherence() every 5 minutes if stale
```

---

## 7. Usage Examples

```tsx
// =============================================================================
// Example: DerivationTrailBar component
// =============================================================================

import { useDerivationState } from '@/stores/derivation/subscriptions';
import { useUIStore } from '@/stores';

function DerivationTrailBar() {
  const { currentPath, isGrounded, derivation } = useDerivationState();
  const expandedNodes = useUIStore((s) => s.expandedTrailNodes);
  const toggleNode = useUIStore((s) => s.toggleTrailNode);

  if (!currentPath) {
    return (
      <div className="trail-bar empty">
        <span className="status">Not grounded</span>
      </div>
    );
  }

  return (
    <div className="trail-bar">
      <span className="status grounded">Grounded: {currentPath.groundingPrinciple}</span>
      <span className="loss">Loss: {currentPath.totalLoss.toFixed(3)}</span>
      <span className="confidence">Confidence: {(currentPath.minConfidence * 100).toFixed(0)}%</span>
      <div className="path">
        {currentPath.edges.map((edgeId, i) => (
          <span
            key={edgeId}
            className="edge"
            onClick={() => toggleNode(edgeId)}
          >
            {expandedNodes.has(edgeId) ? '[-]' : '[+]'} Edge {i + 1}
          </span>
        ))}
      </div>
    </div>
  );
}

// =============================================================================
// Example: GroundingDialog component
// =============================================================================

import { useDerivationStore } from '@/stores/derivation/derivationStore';
import { useUIStore } from '@/stores';

function GroundingDialog() {
  const isOpen = useUIStore((s) => s.isGroundingDialogOpen);
  const kblockId = useUIStore((s) => s.groundingKBlockId);
  const close = useUIStore((s) => s.closeGroundingDialog);
  const ground = useDerivationStore((s) => s.groundKBlock);
  const [selectedPrinciple, setSelectedPrinciple] = useState<string | null>(null);

  if (!isOpen || !kblockId) return null;

  const handleGround = async () => {
    if (selectedPrinciple) {
      await ground(kblockId, selectedPrinciple);
      close();
    }
  };

  return (
    <Dialog open={isOpen} onClose={close}>
      <DialogTitle>Ground K-Block</DialogTitle>
      <DialogContent>
        <p>Select a constitutional principle to ground this K-Block:</p>
        <PrincipleSelector
          value={selectedPrinciple}
          onChange={setSelectedPrinciple}
        />
      </DialogContent>
      <DialogActions>
        <Button onClick={close}>Cancel</Button>
        <Button onClick={handleGround} disabled={!selectedPrinciple}>
          Ground
        </Button>
      </DialogActions>
    </Dialog>
  );
}
```

---

## 8. Store Index

```typescript
// =============================================================================
// File: impl/claude/web/src/stores/index.ts (updated)
// =============================================================================

// UI Store
export { useUIStore, showSuccess, showError, showInfo } from './uiStore';

// User Store
export {
  useUserStore,
  selectCanAfford,
  selectIsLODIncluded,
  selectCanInhabit,
  selectCanForce,
} from './userStore';

// Trail Builder
export { useTrailBuilder } from './trailBuilder';

// NEW: Derivation Store
export { useDerivationStore } from './derivation/derivationStore';
export * from './derivation/types';
export * from './derivation/selectors';

// NEW: K-Block Store (extended)
export { useKBlockStore } from './kblock/kblockStore';

// NEW: Subscriptions
export { setupDerivationSubscriptions, useDerivationState } from './derivation/subscriptions';
```

---

## Summary

This specification defines:

1. **DerivationStore** (new): Manages the derivation graph, categorization, and coherence summary
2. **KBlockStore extension**: Adds derivation context to K-Block state with automatic computation
3. **UIStore extension**: Adds trail bar state, graph view state, and dialog management
4. **Cross-store subscriptions**: Automatic sync between stores when K-Blocks or derivations change
5. **Performance optimizations**: Memoized selectors, efficient persistence, index structures

Total lines: ~400 lines of implementation-ready TypeScript.
