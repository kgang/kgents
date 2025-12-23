/**
 * useGraphNode — Bridge between SpecGraph API and Hypergraph types
 *
 * Converts SpecGraph data into GraphNode format for the editor.
 */

import { useCallback, useState, useEffect, useRef } from 'react';

import { invokeSpecGraph } from '../membrane/useSpecNavigation';
import type { GraphNode, Edge, EdgeType } from './types';

// =============================================================================
// API Response Types (from SpecGraph)
// =============================================================================

interface SpecGraphQueryResult {
  path: string;
  agentese_path: string;
  title: string;
  tier: string;
  confidence: number;
  derives_from: string[];
  edges: Record<string, string[]>;
  tokens: Record<string, number>;
}

// =============================================================================
// Conversion Functions
// =============================================================================

function convertEdgeType(type: string): EdgeType {
  const mapping: Record<string, EdgeType> = {
    extends: 'extends',
    implements: 'implements',
    tests: 'tests',
    extended_by: 'extends', // Inverse
    references: 'references',
    cross_pollinates: 'references',
    contradicts: 'contradicts',
    heritage: 'derives_from',
  };
  return mapping[type] || 'references';
}

function convertToGraphNode(result: SpecGraphQueryResult, content?: string): GraphNode {
  // Convert edges from { type: targets[] } to Edge[]
  const outgoingEdges: Edge[] = [];
  const incomingEdges: Edge[] = [];

  // Defensive: result.edges may be undefined if API returns incomplete data
  const edges = result.edges || {};
  for (const [type, targets] of Object.entries(edges)) {
    for (const target of targets) {
      const edge: Edge = {
        id: `${result.path}-${type}-${target}`,
        source: result.path,
        target,
        type: convertEdgeType(type),
      };

      // extended_by is an inverse edge
      if (type === 'extended_by') {
        incomingEdges.push({ ...edge, source: target, target: result.path });
      } else {
        outgoingEdges.push(edge);
      }
    }
  }

  // Add derives_from as incoming edges
  // Defensive: derives_from may be undefined
  const derivesFrom = result.derives_from || [];
  for (const parent of derivesFrom) {
    incomingEdges.push({
      id: `${parent}-derives-${result.path}`,
      source: parent,
      target: result.path,
      type: 'derives_from',
    });
  }

  return {
    path: result.path,
    title: result.title || result.path.split('/').pop() || result.path,
    agentesePath: result.agentese_path,
    kind: result.path.startsWith('spec/')
      ? 'spec'
      : result.path.includes('_tests/')
        ? 'test'
        : result.path.endsWith('.py')
          ? 'implementation'
          : result.path.endsWith('.md')
            ? 'doc'
            : 'unknown',
    tier: result.tier as GraphNode['tier'],
    confidence: result.confidence,
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
}

export function useGraphNode(): UseGraphNodeResult {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const discoveredRef = useRef(false);
  const discoveringRef = useRef(false);

  // Auto-discover SpecGraph on first use
  // gotcha: SpecGraph is lazy-loaded. Without discover(), queries return empty.
  useEffect(() => {
    const doDiscover = async () => {
      if (discoveredRef.current || discoveringRef.current) return;

      discoveringRef.current = true;

      try {
        // Call discover to populate the graph
        await invokeSpecGraph<{ count: number }>('discover');
        // eslint-disable-next-line require-atomic-updates -- refs are stable
        discoveredRef.current = true;
      } catch (e) {
        console.warn('[useGraphNode] Failed to discover SpecGraph:', e);
      } finally {
        // eslint-disable-next-line require-atomic-updates -- refs are stable
        discoveringRef.current = false;
      }
    };

    doDiscover();
  }, []);

  const loadNode = useCallback(async (path: string): Promise<GraphNode | null> => {
    setLoading(true);
    setError(null);

    try {
      // Ensure SpecGraph is discovered before querying
      // Wait if discovery is in progress, or trigger if not done
      if (!discoveredRef.current) {
        if (!discoveringRef.current) {
          discoveringRef.current = true;
          try {
            await invokeSpecGraph<{ count: number }>('discover');
            // eslint-disable-next-line require-atomic-updates -- refs are stable
            discoveredRef.current = true;
          } catch (e) {
            console.warn('[useGraphNode] Discovery failed:', e);
          } finally {
            // eslint-disable-next-line require-atomic-updates -- refs are stable
            discoveringRef.current = false;
          }
        } else {
          // Wait for in-progress discovery (simple polling)
          let attempts = 0;
          while (discoveringRef.current && attempts < 50) {
            await new Promise<void>((r) => {
              setTimeout(r, 100);
            });
            attempts++;
          }
        }
      }

      // Query SpecGraph for node metadata
      const result = await invokeSpecGraph<SpecGraphQueryResult>('query', { path });

      // Defensive: if API returns undefined/null metadata, create a minimal stub
      if (!result || !result.path) {
        console.warn(
          '[useGraphNode] SpecGraph returned no metadata for',
          path,
          '- creating stub node'
        );
        // Return a stub node so the UI doesn't crash
        return {
          path,
          title: path.split('/').pop() || path,
          kind: path.endsWith('.md') ? 'doc' : path.endsWith('.py') ? 'implementation' : 'unknown',
          confidence: 0,
          outgoingEdges: [],
          incomingEdges: [],
          content: `[SpecGraph unavailable for: ${path}]`,
        };
      }

      // Also fetch content via world.file.read
      let content: string | undefined;
      try {
        const docResult = await fetch('/agentese/world.file/read', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ path }),
        });
        if (docResult.ok) {
          const docData = await docResult.json();
          content = docData.result?.content;
        }
      } catch {
        // Content loading is optional
        console.warn('[useGraphNode] Could not load content for', path);
      }

      return convertToGraphNode(result, content);
    } catch (e) {
      const errorMsg = e instanceof Error ? e.message : 'Failed to load node';
      setError(errorMsg);
      console.error('[useGraphNode] Error loading node:', path, e);

      // Return a stub node so the editor is still usable
      return {
        path,
        title: path.split('/').pop() || path,
        kind: 'unknown',
        confidence: 0,
        outgoingEdges: [],
        incomingEdges: [],
        content: `[Error loading node: ${errorMsg}]`,
      };
    } finally {
      setLoading(false);
    }
  }, []);

  const loadSiblings = useCallback(async (node: GraphNode): Promise<GraphNode[]> => {
    // Siblings are nodes that share the same parent (derives_from or extends)
    const parentEdge = node.incomingEdges.find(
      (e) => e.type === 'derives_from' || e.type === 'extends'
    );

    if (!parentEdge) {
      return [node]; // No parent, no siblings
    }

    try {
      // Navigate from parent to get all children with same edge type
      const result = await invokeSpecGraph<{
        current: { path: string; title: string; tier: string };
        targets: Array<{ path: string; title: string; tier: string }>;
      }>('navigate', {
        path: parentEdge.source,
        edge: parentEdge.type === 'derives_from' ? 'extended_by' : 'extends',
      });

      // Convert targets to minimal GraphNodes
      return result.targets.map((t) => ({
        path: t.path,
        title: t.title,
        kind: 'spec' as const,
        tier: t.tier as GraphNode['tier'],
        confidence: 0.5,
        outgoingEdges: [],
        incomingEdges: [],
      }));
    } catch {
      return [node]; // Fallback to just current node
    }
  }, []);

  return {
    loadNode,
    loadSiblings,
    loading,
    error,
  };
}
