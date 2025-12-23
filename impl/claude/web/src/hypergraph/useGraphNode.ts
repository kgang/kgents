/**
 * useGraphNode — Bridge between SpecGraph API and Hypergraph types
 *
 * Converts SpecGraph data into GraphNode format for the editor.
 */

import { useCallback, useState } from 'react';

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

  for (const [type, targets] of Object.entries(result.edges)) {
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
  for (const parent of result.derives_from) {
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

  const loadNode = useCallback(async (path: string): Promise<GraphNode | null> => {
    setLoading(true);
    setError(null);

    try {
      // Query SpecGraph for node metadata
      const result = await invokeSpecGraph<SpecGraphQueryResult>('query', { path });

      // Also fetch content via K-Block or document API
      let content: string | undefined;
      try {
        const docResult = await fetch(
          `/agentese/self/document/read?path=${encodeURIComponent(path)}`,
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}),
          }
        );
        if (docResult.ok) {
          const docData = await docResult.json();
          content = docData.content || docData.metadata?.content;
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
      return null;
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
