/**
 * useLoss — Hook for fetching Galois loss signatures
 *
 * "Loss = Difficulty. Every node carries a Galois loss value."
 *
 * The loss signature is the fundamental quality signal in a loss-native frontend.
 * Components use this to visualize stability, guide navigation, and detect drift.
 */

import { useState, useEffect, useCallback } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface LossComponents {
  /** Content integrity after compression */
  content: number;
  /** Justification chain strength (L3+) */
  proof: number;
  /** Relationship coherence */
  edge: number;
  /** Context preservation */
  metadata: number;
}

export interface LossSignature {
  /** Total loss: semantic drift from restructure-reconstitute cycle [0, 1] */
  total: number;

  /** Decomposed loss components */
  components: LossComponents;

  /** Derived health status */
  status: 'stable' | 'transitional' | 'unstable';

  /** Fixed-point indicator (total < 0.01) */
  isAxiomatic: boolean;

  /** Layer in epistemic hierarchy */
  layer: 1 | 2 | 3 | 4 | 5 | 6 | 7;

  /** Node ID this signature belongs to */
  nodeId: string;
}

export interface UseLossResult {
  signature: LossSignature | null;
  loading: boolean;
  error: Error | null;
  refresh: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const FIXED_POINT_THRESHOLD = 0.01;
const STABLE_THRESHOLD = 0.3;
const UNSTABLE_THRESHOLD = 0.7;

// =============================================================================
// Helpers
// =============================================================================

function deriveStatus(loss: number): 'stable' | 'transitional' | 'unstable' {
  if (loss < STABLE_THRESHOLD) return 'stable';
  if (loss > UNSTABLE_THRESHOLD) return 'unstable';
  return 'transitional';
}

/**
 * Convert loss value to hue for viridis-inspired gradient.
 * Purple (280°) at low loss → Teal (180°) → Yellow (60°) at high loss
 */
export function lossToHue(loss: number): number {
  return 280 - loss * 220;
}

/**
 * Get CSS color string for a loss value.
 */
export function lossToColor(loss: number): string {
  const hue = lossToHue(loss);
  return `hsl(${hue}, 60%, 50%)`;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Fetch and track Galois loss signature for a node.
 *
 * @param nodeId - The node ID to fetch loss for (null to skip)
 * @returns Loss signature, loading state, error, and refresh function
 *
 * @example
 * ```tsx
 * function AxiomCard({ nodeId }: { nodeId: string }) {
 *   const { signature, loading } = useLoss(nodeId);
 *
 *   if (loading) return <Skeleton />;
 *
 *   return (
 *     <div style={{ '--loss-hue': lossToHue(signature.total) }}>
 *       <LossBadge signature={signature} />
 *     </div>
 *   );
 * }
 * ```
 */
export function useLoss(nodeId: string | null): UseLossResult {
  const [signature, setSignature] = useState<LossSignature | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const fetchLoss = useCallback(async () => {
    if (!nodeId) {
      setSignature(null);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(
        `/api/zero-seed/nodes/${encodeURIComponent(nodeId)}`
      );

      if (!response.ok) {
        throw new Error(`Failed to fetch loss: ${response.status}`);
      }

      const data = await response.json();

      // Transform API response to LossSignature
      const sig: LossSignature = {
        total: data.loss?.loss ?? 0,
        components: {
          content: data.loss?.components?.content_loss ?? 0,
          proof: data.loss?.components?.proof_loss ?? 0,
          edge: data.loss?.components?.edge_loss ?? 0,
          metadata: data.loss?.components?.metadata_loss ?? 0,
        },
        status: deriveStatus(data.loss?.loss ?? 0),
        isAxiomatic: (data.loss?.loss ?? 0) < FIXED_POINT_THRESHOLD,
        layer: data.node?.layer ?? 4,
        nodeId,
      };

      setSignature(sig);
    } catch (err) {
      setError(err instanceof Error ? err : new Error(String(err)));
      setSignature(null);
    } finally {
      setLoading(false);
    }
  }, [nodeId]);

  // Fetch on mount and when nodeId changes
  useEffect(() => {
    fetchLoss();
  }, [fetchLoss]);

  return {
    signature,
    loading,
    error,
    refresh: fetchLoss,
  };
}

/**
 * Batch fetch loss signatures for multiple nodes.
 *
 * @param nodeIds - Array of node IDs to fetch
 * @returns Map of nodeId → LossSignature
 */
export function useLossBatch(nodeIds: string[]): {
  signatures: Map<string, LossSignature>;
  loading: boolean;
  error: Error | null;
} {
  const [signatures, setSignatures] = useState<Map<string, LossSignature>>(
    new Map()
  );
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    if (nodeIds.length === 0) {
      setSignatures(new Map());
      return;
    }

    setLoading(true);

    // Fetch all in parallel
    Promise.all(
      nodeIds.map(async (nodeId) => {
        try {
          const response = await fetch(
            `/api/zero-seed/nodes/${encodeURIComponent(nodeId)}`
          );
          if (!response.ok) return null;
          const data = await response.json();

          const sig: LossSignature = {
            total: data.loss?.loss ?? 0,
            components: {
              content: data.loss?.components?.content_loss ?? 0,
              proof: data.loss?.components?.proof_loss ?? 0,
              edge: data.loss?.components?.edge_loss ?? 0,
              metadata: data.loss?.components?.metadata_loss ?? 0,
            },
            status: deriveStatus(data.loss?.loss ?? 0),
            isAxiomatic: (data.loss?.loss ?? 0) < FIXED_POINT_THRESHOLD,
            layer: data.node?.layer ?? 4,
            nodeId,
          };

          return [nodeId, sig] as const;
        } catch {
          return null;
        }
      })
    )
      .then((results) => {
        const map = new Map<string, LossSignature>();
        for (const result of results) {
          if (result) {
            map.set(result[0], result[1]);
          }
        }
        setSignatures(map);
        setError(null);
      })
      .catch((err) => {
        setError(err instanceof Error ? err : new Error(String(err)));
      })
      .finally(() => {
        setLoading(false);
      });
  }, [nodeIds.join(',')]);

  return { signatures, loading, error };
}

export default useLoss;
