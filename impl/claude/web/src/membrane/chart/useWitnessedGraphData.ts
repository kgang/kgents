/**
 * useWitnessedGraphData — Data hook for WitnessedGraph visualization
 *
 * Fetches from concept.graph.* AGENTESE endpoints and transforms to
 * StarData/ConnectionData format for AstronomicalChart.
 *
 * Alternative to useAstronomicalData which uses SpecLedger data.
 * WitnessedGraph provides unified edges from:
 *   - Sovereign: Code structure (imports, calls, inherits)
 *   - Witness: Mark-based evidence (tags, decisions)
 *   - SpecLedger: Spec relations (harmony, contradiction)
 *
 * "The file is a lie. There is only the graph."
 */

import { useState, useEffect, useCallback, useMemo } from 'react';
import { graphApi } from '../../api/client';
import type {
  ConceptGraphManifestResponse,
  ConceptGraphNeighborsResponse,
} from '../../api/types/_generated/concept-graph';
import type { StarData, ConnectionData } from './useAstronomicalData';

// =============================================================================
// Types
// =============================================================================

export interface WitnessedGraphDataOptions {
  /** Center node path (if provided, shows neighbors) */
  centerPath?: string;
  /** Search query (if provided, shows search results) */
  searchQuery?: string;
  /** Maximum edges to fetch */
  limit?: number;
}

export interface WitnessedGraphDataReturn {
  stars: StarData[];
  connections: ConnectionData[];
  isLoading: boolean;
  error: Error | null;
  /** Graph stats from manifest */
  manifest: ConceptGraphManifestResponse | null;
  /** Re-fetch data */
  refetch: () => void;
}

// =============================================================================
// Constants
// =============================================================================

const BASE_RADIUS = 5;
const RADIUS_SCALE = 2;

/**
 * Detect tier from file path.
 * Consistent with useAstronomicalData tier detection.
 */
function pathToTier(path: string): number {
  if (path.includes('principles') || path.includes('constitution')) return 0;
  if (path.includes('protocols')) return 1;
  if (path.includes('agents')) return 2;
  if (path.includes('services') || path.includes('crown')) return 3;
  if (path.includes('agentese')) return 4;
  return 2; // Default to protocols tier
}

/**
 * Extract label from path (last segment).
 */
function pathToLabel(path: string): string {
  const segments = path.split('/');
  return segments[segments.length - 1] || path;
}

// =============================================================================
// Hook
// =============================================================================

export function useWitnessedGraphData(
  options: WitnessedGraphDataOptions = {}
): WitnessedGraphDataReturn {
  const { centerPath, searchQuery, limit = 100 } = options;

  // State
  const [manifest, setManifest] = useState<ConceptGraphManifestResponse | null>(null);
  const [neighborsData, setNeighborsData] = useState<ConceptGraphNeighborsResponse | null>(null);
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
        // Always fetch manifest for stats
        const manifestResponse = await graphApi.manifest();
        if (cancelled) return;
        setManifest(manifestResponse);

        // If center path provided, fetch neighbors
        if (centerPath) {
          const neighborsResponse = await graphApi.neighbors(centerPath);
          if (cancelled) return;
          setNeighborsData(neighborsResponse);
        } else if (searchQuery) {
          // Search mode - use search endpoint
          const searchResponse = await graphApi.search(searchQuery, limit);
          if (cancelled) return;
          // Transform search results to neighbors-like format
          setNeighborsData({
            path: searchQuery,
            incoming: [],
            outgoing: searchResponse.edges.map((e) => ({
              ...e,
              context: e.context ?? null,
              line_number: e.line_number ?? null,
              mark_id: e.mark_id ?? null,
            })),
            total: searchResponse.count,
          });
        } else {
          // No specific query - just show manifest stats
          setNeighborsData(null);
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
  }, [centerPath, searchQuery, limit, fetchTrigger]);

  // Transform data to astronomical format
  const { stars, connections } = useMemo(() => {
    if (!neighborsData) {
      // No neighbors data - show empty
      return { stars: [], connections: [] };
    }

    const allEdges = [...neighborsData.incoming, ...neighborsData.outgoing];

    // Collect unique nodes from edges
    const nodeSet = new Set<string>();
    nodeSet.add(neighborsData.path); // Center node

    allEdges.forEach((edge) => {
      nodeSet.add(edge.source_path);
      nodeSet.add(edge.target_path);
    });

    // Create stars from nodes
    const nodeArray = Array.from(nodeSet);
    const starList: StarData[] = nodeArray.map((path) => {
      const edgeCount = allEdges.filter(
        (e) => e.source_path === path || e.target_path === path
      ).length;

      return {
        id: path,
        label: pathToLabel(path),
        path,
        tier: pathToTier(path),
        status: 'ACTIVE' as const, // Graph nodes are always "active"
        claimCount: 0,
        implCount: edgeCount, // Use edge count as proxy for "impl count"
        testCount: 0,
        wordCount: 0,
        x: 0,
        y: 0,
        radius: BASE_RADIUS + Math.log(edgeCount + 1) * RADIUS_SCALE,
      };
    });

    // Create connections from edges
    const connectionList: ConnectionData[] = allEdges.map((edge, i) => ({
      id: `edge-${i}`,
      source: edge.source_path,
      target: edge.target_path,
      relationship: edge.kind,
      strength: edge.confidence ?? 0.5,
    }));

    return { stars: starList, connections: connectionList };
  }, [neighborsData]);

  // Refetch callback
  const refetch = useCallback(() => {
    setFetchTrigger((prev) => prev + 1);
  }, []);

  return {
    stars,
    connections,
    isLoading,
    error,
    manifest,
    refetch,
  };
}

export default useWitnessedGraphData;
