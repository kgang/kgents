/**
 * useDerivationNavigation — Derivation-aware graph navigation
 *
 * "The proof IS the decision. The mark IS the witness.
 *  Navigate toward your axioms. Trace your derivations."
 *
 * Enables derivation-based navigation through the Constitutional graph:
 * - gh: Go to derivation parent (derives_from edge up)
 * - gl: Go to derivation child (derives_from edge down)
 * - gj: Go to next sibling (same layer, same parent)
 * - gk: Go to prev sibling (same layer, same parent)
 * - gG: Go to genesis (trace to L0 axiom)
 *
 * Philosophy:
 *   Every node derives from axioms. Navigation should make that visible.
 *   The derivation trail is NOT just history—it's your proof structure.
 */

import { useState, useCallback } from 'react';
import { getNode, getAxiomExplorer } from '../api/zeroSeed';
import type { ZeroNode, ZeroEdge } from '../api/zeroSeed';

// =============================================================================
// Types
// =============================================================================

export interface DerivationNode {
  id: string;
  path: string;
  title: string;
  layer: number;
  kind: string;
  confidence: number;
  hasProof: boolean;
}

export interface DerivationLink {
  parentId: string;
  childId: string;
  confidence: number;
  edgeKind: string;
}

export interface DerivationSibling {
  id: string;
  title: string;
  layer: number; // Can be any layer (1-7 or other values)
  index: number;
}

export interface DerivationNavigationResult {
  /** Go to the derivation parent (follows derives_from edge up) */
  goToParent: () => Promise<DerivationNode | null>;

  /** Go to the first derivation child (follows derives_from edge down) */
  goToChild: (childIndex?: number) => Promise<DerivationNode | null>;

  /** Go to the next sibling (same layer, same parent) */
  goToNextSibling: () => Promise<DerivationNode | null>;

  /** Go to the previous sibling (same layer, same parent) */
  goToPrevSibling: () => Promise<DerivationNode | null>;

  /** Go to genesis (trace all the way to L1 axiom) */
  goToGenesis: () => Promise<DerivationNode | null>;

  /** Get the derivation trail from current node to an axiom */
  getDerivationTrail: (nodeId: string) => Promise<DerivationNode[]>;

  /** Get siblings (nodes with same parent at same layer) */
  getSiblings: (nodeId: string) => Promise<DerivationSibling[]>;

  /** Get children (nodes that derive from current) */
  getChildren: (nodeId: string) => Promise<DerivationNode[]>;

  /** Get the parent of a node */
  getParent: (nodeId: string) => Promise<DerivationNode | null>;

  /** Current navigation state */
  currentNodeId: string | null;

  /** Set current node for navigation context */
  setCurrentNode: (nodeId: string | null) => void;

  /** Current sibling index (for j/k navigation) */
  siblingIndex: number;

  /** Total siblings at current layer */
  siblingCount: number;

  /** Current derivation depth (0 = axiom) */
  derivationDepth: number;

  /** Loading state */
  loading: boolean;

  /** Error state */
  error: Error | null;
}

// =============================================================================
// Constants
// =============================================================================

const DERIVES_FROM_EDGE_KINDS = ['derives_from', 'implements', 'extends', 'specializes'];
const MAX_DERIVATION_DEPTH = 50; // Prevent infinite loops

// =============================================================================
// Helper: Convert ZeroNode to DerivationNode
// =============================================================================

function toDerivationNode(node: ZeroNode): DerivationNode {
  return {
    id: node.id,
    path: node.path,
    title: node.title,
    layer: node.layer,
    kind: node.kind,
    confidence: node.confidence,
    hasProof: node.has_proof,
  };
}

// =============================================================================
// Hook Implementation
// =============================================================================

export function useDerivationNavigation(): DerivationNavigationResult {
  const [currentNodeId, setCurrentNodeId] = useState<string | null>(null);
  const [siblingIndex, setSiblingIndex] = useState(0);
  const [siblingCount, setSiblingCount] = useState(0);
  const [derivationDepth, setDerivationDepth] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  // Cache for siblings (to avoid refetching)
  const [siblingsCache, setSiblingsCache] = useState<DerivationSibling[]>([]);

  /**
   * Set the current node and update derivation context.
   */
  const setCurrentNode = useCallback(async (nodeId: string | null) => {
    setCurrentNodeId(nodeId);

    if (!nodeId) {
      setSiblingIndex(0);
      setSiblingCount(0);
      setDerivationDepth(0);
      setSiblingsCache([]);
      return;
    }

    // Compute derivation depth by tracing to axiom
    try {
      const trail = await getDerivationTrailInternal(nodeId);
      setDerivationDepth(trail.length - 1); // 0 = axiom itself

      // Fetch siblings
      const siblings = await getSiblingsInternal(nodeId);
      setSiblingsCache(siblings);
      setSiblingCount(siblings.length);
      const idx = siblings.findIndex((s) => s.id === nodeId);
      setSiblingIndex(idx >= 0 ? idx : 0);
    } catch (err) {
      console.warn('[useDerivationNavigation] Failed to compute depth:', err);
    }
  }, []);

  /**
   * Get the parent node (follows derives_from edge up).
   */
  const getParent = useCallback(async (nodeId: string): Promise<DerivationNode | null> => {
    setLoading(true);
    setError(null);

    try {
      const response = await getNode(nodeId);
      const { incoming_edges } = response;

      // Find derives_from edge
      const derivesFromEdge = incoming_edges.find((e: ZeroEdge) =>
        DERIVES_FROM_EDGE_KINDS.includes(e.kind)
      );

      if (!derivesFromEdge) {
        // No parent (this is an axiom)
        return null;
      }

      // Fetch parent node
      const parentResponse = await getNode(derivesFromEdge.source);
      return toDerivationNode(parentResponse.node);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Go to derivation parent.
   */
  const goToParent = useCallback(async (): Promise<DerivationNode | null> => {
    if (!currentNodeId) return null;

    const parent = await getParent(currentNodeId);
    if (parent) {
      await setCurrentNode(parent.id);
    }
    return parent;
  }, [currentNodeId, getParent, setCurrentNode]);

  /**
   * Get children nodes (nodes that derive from this one).
   */
  const getChildren = useCallback(async (nodeId: string): Promise<DerivationNode[]> => {
    setLoading(true);
    setError(null);

    try {
      const response = await getNode(nodeId);
      const { outgoing_edges } = response;

      // Find all derives_from edges (where this node is the source)
      const childEdges = outgoing_edges.filter((e: ZeroEdge) =>
        DERIVES_FROM_EDGE_KINDS.includes(e.kind)
      );

      if (childEdges.length === 0) {
        return [];
      }

      // Fetch all child nodes in parallel
      const childPromises = childEdges.map(async (edge: ZeroEdge) => {
        try {
          const childResponse = await getNode(edge.target);
          return toDerivationNode(childResponse.node);
        } catch {
          return null;
        }
      });

      const children = await Promise.all(childPromises);
      return children.filter((c): c is DerivationNode => c !== null);
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Go to derivation child.
   */
  const goToChild = useCallback(
    async (childIndex: number = 0): Promise<DerivationNode | null> => {
      if (!currentNodeId) return null;

      const children = await getChildren(currentNodeId);
      if (children.length === 0) {
        return null;
      }

      const idx = Math.min(Math.max(0, childIndex), children.length - 1);
      const child = children[idx];

      await setCurrentNode(child.id);
      return child;
    },
    [currentNodeId, getChildren, setCurrentNode]
  );

  /**
   * Get siblings (internal, no state updates).
   */
  const getSiblingsInternal = async (nodeId: string): Promise<DerivationSibling[]> => {
    try {
      const response = await getNode(nodeId);
      const currentNode = response.node;
      const { incoming_edges } = response;

      // Find parent via derives_from
      const derivesFromEdge = incoming_edges.find((e: ZeroEdge) =>
        DERIVES_FROM_EDGE_KINDS.includes(e.kind)
      );

      if (!derivesFromEdge) {
        // No parent = axiom, get all axioms as siblings
        const axiomsResponse = await getAxiomExplorer();
        return axiomsResponse.axioms.map((a, i) => ({
          id: a.id,
          title: a.title,
          layer: a.layer,
          index: i,
        }));
      }

      // Get parent and find all its children at same layer
      const parentResponse = await getNode(derivesFromEdge.source);
      const parentOutgoing = parentResponse.outgoing_edges.filter((e: ZeroEdge) =>
        DERIVES_FROM_EDGE_KINDS.includes(e.kind)
      );

      // Fetch sibling nodes
      const siblingPromises = parentOutgoing.map(
        async (edge: ZeroEdge, i: number): Promise<DerivationSibling | null> => {
          try {
            const siblingResponse = await getNode(edge.target);
            const sibling = siblingResponse.node;
            // Only include siblings at same layer
            if (sibling.layer === currentNode.layer) {
              return {
                id: sibling.id,
                title: sibling.title,
                layer: sibling.layer as number,
                index: i,
              };
            }
            return null;
          } catch {
            return null;
          }
        }
      );

      const siblings = await Promise.all(siblingPromises);
      return siblings.filter((s): s is DerivationSibling => s !== null);
    } catch {
      return [];
    }
  };

  /**
   * Get siblings (public API with state updates).
   */
  const getSiblings = useCallback(async (nodeId: string): Promise<DerivationSibling[]> => {
    setLoading(true);
    setError(null);

    try {
      const siblings = await getSiblingsInternal(nodeId);
      setSiblingsCache(siblings);
      setSiblingCount(siblings.length);
      return siblings;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Go to next sibling.
   */
  const goToNextSibling = useCallback(async (): Promise<DerivationNode | null> => {
    if (!currentNodeId || siblingsCache.length === 0) return null;

    const nextIndex = (siblingIndex + 1) % siblingsCache.length;
    const nextSibling = siblingsCache[nextIndex];

    if (!nextSibling || nextSibling.id === currentNodeId) return null;

    setLoading(true);
    try {
      const response = await getNode(nextSibling.id);
      const node = toDerivationNode(response.node);
      setCurrentNodeId(node.id);
      setSiblingIndex(nextIndex);
      return node;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, [currentNodeId, siblingIndex, siblingsCache]);

  /**
   * Go to prev sibling.
   */
  const goToPrevSibling = useCallback(async (): Promise<DerivationNode | null> => {
    if (!currentNodeId || siblingsCache.length === 0) return null;

    const prevIndex = (siblingIndex - 1 + siblingsCache.length) % siblingsCache.length;
    const prevSibling = siblingsCache[prevIndex];

    if (!prevSibling || prevSibling.id === currentNodeId) return null;

    setLoading(true);
    try {
      const response = await getNode(prevSibling.id);
      const node = toDerivationNode(response.node);
      setCurrentNodeId(node.id);
      setSiblingIndex(prevIndex);
      return node;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, [currentNodeId, siblingIndex, siblingsCache]);

  /**
   * Get derivation trail (internal, no state updates).
   */
  const getDerivationTrailInternal = async (nodeId: string): Promise<DerivationNode[]> => {
    const trail: DerivationNode[] = [];
    let currentId: string | null = nodeId;
    let depth = 0;

    while (currentId && depth < MAX_DERIVATION_DEPTH) {
      try {
        const response = await getNode(currentId);
        trail.unshift(toDerivationNode(response.node)); // Add to front (axiom first)

        // Find parent
        const derivesFromEdge = response.incoming_edges.find((e: ZeroEdge) =>
          DERIVES_FROM_EDGE_KINDS.includes(e.kind)
        );

        currentId = derivesFromEdge?.source ?? null;
        depth++;
      } catch {
        break;
      }
    }

    return trail;
  };

  /**
   * Get derivation trail (public API with state updates).
   */
  const getDerivationTrail = useCallback(async (nodeId: string): Promise<DerivationNode[]> => {
    setLoading(true);
    setError(null);

    try {
      const trail = await getDerivationTrailInternal(nodeId);
      return trail;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      return [];
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * Go to genesis (L1 axiom at root of derivation).
   */
  const goToGenesis = useCallback(async (): Promise<DerivationNode | null> => {
    if (!currentNodeId) return null;

    setLoading(true);
    setError(null);

    try {
      const trail = await getDerivationTrailInternal(currentNodeId);

      if (trail.length === 0) {
        return null;
      }

      // First node in trail is the axiom (genesis)
      const genesis = trail[0];

      await setCurrentNode(genesis.id);
      return genesis;
    } catch (err) {
      const error = err instanceof Error ? err : new Error(String(err));
      setError(error);
      return null;
    } finally {
      setLoading(false);
    }
  }, [currentNodeId, setCurrentNode]);

  return {
    goToParent,
    goToChild,
    goToNextSibling,
    goToPrevSibling,
    goToGenesis,
    getDerivationTrail,
    getSiblings,
    getChildren,
    getParent,
    currentNodeId,
    setCurrentNode,
    siblingIndex,
    siblingCount,
    derivationDepth,
    loading,
    error,
  };
}

export default useDerivationNavigation;
