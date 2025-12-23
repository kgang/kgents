/**
 * useSpecGraph Hook
 *
 * Fetches spec data and transforms it to Reactflow nodes/edges.
 * Handles layout with dagre for hierarchical positioning.
 */

import { useMemo, useCallback, useEffect, useState } from 'react';
import dagre from 'dagre';
import type { Node, Edge } from 'reactflow';
import {
  getLedger,
  getHarmonies,
  type SpecEntry,
  type LedgerResponse,
  type HarmoniesResponse,
} from '../../api/specLedger';

// =============================================================================
// Types
// =============================================================================

export interface SpecNodeData {
  label: string;
  path: string;
  status: SpecEntry['status'];
  tier: number;
  claimCount: number;
  implCount: number;
  testCount: number;
}

export interface SpecEdgeData {
  relationship: string;
  strength: number;
}

export type SpecNode = Node<SpecNodeData>;
export type SpecEdge = Edge<SpecEdgeData>;

export interface UseSpecGraphOptions {
  /** Filter by status */
  statusFilter?: string;
  /** Maximum specs to show */
  limit?: number;
}

export interface UseSpecGraphReturn {
  nodes: SpecNode[];
  edges: SpecEdge[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const NODE_WIDTH = 180;
const NODE_HEIGHT = 60;

// Tier detection from path
function detectTier(path: string): number {
  if (path.includes('principles') || path.includes('constitution')) return 0;
  if (path.includes('protocols')) return 1;
  if (path.includes('agents')) return 2;
  if (path.includes('services') || path.includes('crown')) return 3;
  if (path.includes('agentese')) return 4;
  return 2; // Default
}

// =============================================================================
// Layout
// =============================================================================

function applyLayout(
  nodes: SpecNode[],
  edges: SpecEdge[],
  direction: 'TB' | 'LR' = 'TB'
): SpecNode[] {
  const g = new dagre.graphlib.Graph();
  g.setGraph({ rankdir: direction, nodesep: 50, ranksep: 80 });
  g.setDefaultEdgeLabel(() => ({}));

  // Add nodes
  nodes.forEach((node) => {
    g.setNode(node.id, { width: NODE_WIDTH, height: NODE_HEIGHT });
  });

  // Add edges
  edges.forEach((edge) => {
    g.setEdge(edge.source, edge.target);
  });

  // Run layout
  dagre.layout(g);

  // Apply positions
  return nodes.map((node) => {
    const pos = g.node(node.id);
    return {
      ...node,
      position: {
        x: pos.x - NODE_WIDTH / 2,
        y: pos.y - NODE_HEIGHT / 2,
      },
    };
  });
}

// =============================================================================
// Hook
// =============================================================================

export function useSpecGraph(options: UseSpecGraphOptions = {}): UseSpecGraphReturn {
  const { statusFilter, limit = 100 } = options;

  // State
  const [specsData, setSpecsData] = useState<LedgerResponse | null>(null);
  const [harmoniesData, setHarmoniesData] = useState<HarmoniesResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);
  const [fetchTrigger, setFetchTrigger] = useState(0);

  // Fetch data
  useEffect(() => {
    let cancelled = false;

    async function fetchData() {
      setIsLoading(true);
      setError(null);

      try {
        const [specs, harmonies] = await Promise.all([
          getLedger({ status: statusFilter, limit }),
          getHarmonies(limit),
        ]);

        if (!cancelled) {
          setSpecsData(specs);
          setHarmoniesData(harmonies);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error(String(err)));
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    fetchData();

    return () => {
      cancelled = true;
    };
  }, [statusFilter, limit, fetchTrigger]);

  // Transform data to Reactflow format
  const { nodes, edges } = useMemo(() => {
    if (!specsData?.specs) {
      return { nodes: [], edges: [] };
    }

    const specs = specsData.specs;
    const harmonies = harmoniesData?.harmonies || [];

    // Create nodes
    const specNodes: SpecNode[] = specs.map((spec: SpecEntry) => ({
      id: spec.path,
      type: 'specNode',
      position: { x: 0, y: 0 }, // Will be set by layout
      data: {
        label: spec.title || spec.path.split('/').pop() || spec.path,
        path: spec.path,
        status: spec.status,
        tier: detectTier(spec.path),
        claimCount: spec.claim_count,
        implCount: spec.impl_count,
        testCount: spec.test_count,
      },
    }));

    // Create node lookup for edge validation
    const nodeIds = new Set(specNodes.map((n) => n.id));

    // Create edges from harmonies
    const specEdges: SpecEdge[] = harmonies
      .filter(
        (h: { spec_a: string; spec_b: string }) => nodeIds.has(h.spec_a) && nodeIds.has(h.spec_b)
      )
      .map(
        (
          h: { spec_a: string; spec_b: string; relationship: string; strength: number },
          i: number
        ) => ({
          id: `edge-${i}`,
          source: h.spec_a,
          target: h.spec_b,
          type: 'specEdge',
          data: {
            relationship: h.relationship,
            strength: h.strength,
          },
        })
      );

    // Apply layout
    const layoutedNodes = applyLayout(specNodes, specEdges);

    return { nodes: layoutedNodes, edges: specEdges };
  }, [specsData, harmoniesData]);

  // Refetch callback
  const refetch = useCallback(() => {
    setFetchTrigger((prev) => prev + 1);
  }, []);

  return {
    nodes,
    edges,
    isLoading,
    error,
    refetch,
  };
}

export default useSpecGraph;
