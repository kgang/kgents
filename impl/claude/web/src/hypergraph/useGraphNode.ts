/**
 * useGraphNode — Bridge between WitnessedGraph API and Hypergraph types
 *
 * "The file is a lie. There is only the graph."
 *
 * This hook connects the HypergraphEditor to the WitnessedGraph (9th Crown Jewel),
 * converting concept.graph.neighbors responses into GraphNode format.
 *
 * Key features:
 * - Witnessed edges (linked to marks via mark_id)
 * - Evidence-based navigation (confidence, context, line numbers)
 * - Origin tracking (which source contributed this edge)
 */

import { useCallback, useEffect, useRef, useState } from 'react';

import { graphApi, fileApi } from '../api/client';
import type { ConceptGraphNeighborsResponse } from '../api/types/_generated/concept-graph';
import type { GraphNode, Edge, EdgeType } from './types';

// =============================================================================
// Conversion Functions
// =============================================================================

/**
 * Convert WitnessedGraph edge kind to HypergraphEditor EdgeType.
 */
function convertEdgeKind(kind: string): EdgeType {
  const mapping: Record<string, EdgeType> = {
    implements: 'implements',
    tests: 'tests',
    extends: 'extends',
    derives_from: 'derives_from',
    references: 'references',
    contradicts: 'contradicts',
    contains: 'contains',
    uses: 'uses',
    defines: 'defines',
    // WitnessedGraph might use different naming
    heritage: 'derives_from',
    extended_by: 'extends',
  };
  return mapping[kind] || 'references';
}

/**
 * Convert WitnessedGraph neighbors response to GraphNode.
 *
 * Preserves all evidence fields from WitnessedGraph:
 * - confidence: certainty of relationship
 * - origin: what source contributed it
 * - markId: audit trail link
 * - lineNumber: where in source file
 */
function convertNeighborsToGraphNode(
  path: string,
  response: ConceptGraphNeighborsResponse,
  content?: string
): GraphNode {
  // Convert incoming edges with full evidence
  const incomingEdges: Edge[] = response.incoming.map((edge) => ({
    id: `${edge.source_path}-${edge.kind}-${edge.target_path}`,
    source: edge.source_path,
    target: edge.target_path,
    type: convertEdgeKind(edge.kind),
    context: edge.context ?? undefined,
    stale: false,
    // WitnessedGraph evidence fields
    confidence: edge.confidence,
    origin: edge.origin,
    markId: edge.mark_id ?? undefined,
    lineNumber: edge.line_number ?? undefined,
  }));

  // Convert outgoing edges with full evidence
  const outgoingEdges: Edge[] = response.outgoing.map((edge) => ({
    id: `${edge.source_path}-${edge.kind}-${edge.target_path}`,
    source: edge.source_path,
    target: edge.target_path,
    type: convertEdgeKind(edge.kind),
    context: edge.context ?? undefined,
    stale: false,
    // WitnessedGraph evidence fields
    confidence: edge.confidence,
    origin: edge.origin,
    markId: edge.mark_id ?? undefined,
    lineNumber: edge.line_number ?? undefined,
  }));

  // Derive title from path (last component, without extension)
  const pathParts = path.split('/');
  const filename = pathParts[pathParts.length - 1] || path;
  const title = filename.replace(/\.(md|py|ts|tsx|js|jsx)$/, '');

  // Derive kind from path
  const kind: GraphNode['kind'] = path.startsWith('spec/')
    ? 'spec'
    : path.includes('_test') || path.includes('/tests/')
      ? 'test'
      : path.endsWith('.py') || path.endsWith('.ts') || path.endsWith('.tsx')
        ? 'implementation'
        : path.endsWith('.md')
          ? 'doc'
          : 'unknown';

  // Calculate average confidence from edges (if available)
  const allEdges = [...response.incoming, ...response.outgoing];
  const confidences = allEdges.filter((e) => e.confidence !== undefined).map((e) => e.confidence!);
  const avgConfidence =
    confidences.length > 0 ? confidences.reduce((a, b) => a + b, 0) / confidences.length : 0.5;

  return {
    path,
    title,
    kind,
    confidence: avgConfidence,
    outgoingEdges,
    incomingEdges,
    content,
  };
}

// =============================================================================
// Hook
// =============================================================================

export interface UseGraphNodeResult {
  /** Load a node by path */
  loadNode: (path: string) => Promise<GraphNode | null>;

  /** Load siblings of a node */
  loadSiblings: (node: GraphNode) => Promise<GraphNode[]>;

  /** Loading state */
  loading: boolean;

  /** Error state */
  error: string | null;

  /** Graph update count (for cache invalidation) */
  updateCount: number;

  /** Whether the graph has new updates since last load */
  hasUpdates: boolean;

  /** Acknowledge updates (reset hasUpdates flag) */
  acknowledgeUpdates: () => void;
}

/** Polling interval for checking graph updates (5 seconds) */
const UPDATE_POLL_INTERVAL = 5000;

/**
 * Hook for loading graph nodes from the WitnessedGraph API.
 *
 * Unlike the old SpecGraph, WitnessedGraph:
 * - Doesn't require explicit discover() call
 * - Returns edges with witness marks (evidence)
 * - Tracks edge origins (which source contributed)
 * - Polls for updates to enable live refresh
 *
 * "The file is a lie. There is only the graph."
 */
export function useGraphNode(): UseGraphNodeResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Update tracking state
  const [updateCount, setUpdateCount] = useState(0);
  const [hasUpdates, setHasUpdates] = useState(false);
  const lastKnownUpdateCountRef = useRef(0);

  // Poll for graph updates
  useEffect(() => {
    let mounted = true;

    const checkForUpdates = async () => {
      try {
        const manifest = await graphApi.manifest();
        if (mounted && manifest.update_count > lastKnownUpdateCountRef.current) {
          setUpdateCount(manifest.update_count);
          setHasUpdates(true);
          console.info(
            '[useGraphNode] Graph updated:',
            manifest.update_count,
            'at',
            manifest.last_update_at
          );
        }
      } catch (_e) {
        // Polling failure is non-critical
      }
    };

    // Initial check
    checkForUpdates();

    // Set up polling interval
    const interval = setInterval(checkForUpdates, UPDATE_POLL_INTERVAL);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  // Acknowledge updates
  const acknowledgeUpdates = useCallback(() => {
    lastKnownUpdateCountRef.current = updateCount;
    setHasUpdates(false);
  }, [updateCount]);

  const loadNode = useCallback(async (path: string): Promise<GraphNode | null> => {
    setLoading(true);
    setError(null);

    try {
      // Query WitnessedGraph for edges connected to this path
      const neighborsResponse = await graphApi.neighbors(path);

      // Also fetch content via fileApi (optional - content is lazy-loaded)
      let content: string | undefined;
      try {
        const fileResponse = await fileApi.read(path);
        content = fileResponse.content;
      } catch (_fileError) {
        // Content loading is optional - node can still show edges without content
        console.info('[useGraphNode] Content not available for', path, '- edges-only mode');
      }

      return convertNeighborsToGraphNode(path, neighborsResponse, content);
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : 'Failed to load node';
      setError(errorMsg);
      console.error('[useGraphNode] Error loading node:', path, e);

      // Return a stub node so the editor is still usable
      // The UI should show that content is unavailable but navigation is possible
      return {
        path,
        title: path.split('/').pop() || path,
        kind: 'unknown',
        confidence: 0,
        outgoingEdges: [],
        incomingEdges: [],
        content: `# Node: ${path}\n\n*Error loading from WitnessedGraph: ${errorMsg}*\n\nTry :e <path> to navigate to another node.`,
      };
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSiblings = useCallback(async (node: GraphNode): Promise<GraphNode[]> => {
    // Siblings are nodes that share the same parent (via derives_from or extends edges)
    const parentEdge = node.incomingEdges.find(
      (e) => e.type === 'derives_from' || e.type === 'extends'
    );

    if (!parentEdge) {
      return [node]; // No parent, no siblings
    }

    try {
      // Get parent's neighbors to find all children
      const parentNeighbors = await graphApi.neighbors(parentEdge.source);

      // Find outgoing edges from parent that have the inverse relationship
      // derives_from incoming edge means parent has "derives" or "contains" outgoing
      // extends incoming edge means parent has "extended_by" outgoing
      const siblingPaths = parentNeighbors.outgoing
        .filter((edge) => {
          const kind = edge.kind.toLowerCase();
          return (
            kind === 'derives' ||
            kind === 'contains' ||
            kind === 'extended_by' ||
            kind === 'children'
          );
        })
        .map((edge) => edge.target_path);

      // If no explicit sibling edges, find all nodes that derive from this parent
      if (siblingPaths.length === 0) {
        // Search for other nodes that have this parent
        const searchResult = await graphApi.search(`derives_from:${parentEdge.source}`, 20);
        for (const edge of searchResult.edges) {
          if (edge.source_path !== node.path) {
            siblingPaths.push(edge.source_path);
          }
        }
      }

      // Convert to minimal GraphNodes (full load would be expensive for many siblings)
      const siblings: GraphNode[] = siblingPaths.map((siblingPath) => ({
        path: siblingPath,
        title:
          siblingPath
            .split('/')
            .pop()
            ?.replace(/\.(md|py|ts|tsx)$/, '') || siblingPath,
        kind: 'spec' as const,
        confidence: 0.5,
        outgoingEdges: [],
        incomingEdges: [],
      }));

      // Include current node if not already present
      if (!siblings.find((s) => s.path === node.path)) {
        siblings.unshift({
          path: node.path,
          title: node.title,
          kind: node.kind,
          confidence: node.confidence,
          outgoingEdges: [],
          incomingEdges: [],
        });
      }

      return siblings;
    } catch (e) {
      console.warn('[useGraphNode] Failed to load siblings:', e);
      return [node]; // Fallback to just current node
    }
  }, []);

  return {
    loadNode,
    loadSiblings,
    loading,
    error,
    updateCount,
    hasUpdates,
    acknowledgeUpdates,
  };
}
