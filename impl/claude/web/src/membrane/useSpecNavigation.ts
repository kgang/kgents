/**
 * useSpecNavigation — Hook for navigating the SpecGraph hypergraph
 *
 * Connects to the concept.specgraph AGENTESE node to:
 * - Query individual specs
 * - Navigate via edges (extends, implements, tests, etc.)
 * - Discover interactive tokens
 *
 * "Every spec is a node. Every reference is an edge. The graph IS the system."
 */

import { useCallback, useEffect, useState } from 'react';

// =============================================================================
// Types
// =============================================================================

export type EdgeType =
  | 'extends'
  | 'implements'
  | 'tests'
  | 'extended_by'
  | 'references'
  | 'cross_pollinates'
  | 'contradicts'
  | 'heritage';

export type TokenType =
  | 'agentese_path'
  | 'ad_reference'
  | 'principle_ref'
  | 'impl_ref'
  | 'test_ref'
  | 'type_ref'
  | 'code_block'
  | 'heritage_ref';

export interface SpecNode {
  path: string;
  agentese_path: string;
  title: string;
  tier: string;
  confidence: number;
  derives_from: string[];
}

export interface SpecEdge {
  type: EdgeType;
  target: string;
  line?: number;
}

export interface SpecToken {
  type: TokenType;
  content: string;
  line: number;
  column: number;
  context?: string;
}

export interface SpecQueryResult {
  node: SpecNode;
  edges: Record<string, string[]>;
  tokens: Record<string, number>;
  content?: string;
}

export interface SpecGraphStats {
  specs: number;
  edges: number;
  tokens: number;
  by_tier: Record<string, number>;
  by_edge_type: Record<string, number>;
}

// =============================================================================
// API
// =============================================================================

const AGENTESE_BASE = '/agentese';

async function invokeSpecGraph<T>(aspect: string, params: Record<string, string> = {}): Promise<T> {
  const searchParams = new URLSearchParams(params);
  const url = `${AGENTESE_BASE}/concept.specgraph/${aspect}${searchParams.toString() ? `?${searchParams}` : ''}`;

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({}),
  });

  if (!response.ok) {
    throw new Error(`SpecGraph ${aspect} failed: ${response.statusText}`);
  }

  const data = await response.json();
  return data.metadata as T;
}

// =============================================================================
// Hooks
// =============================================================================

export interface UseSpecGraphResult {
  // State
  discovered: boolean;
  stats: SpecGraphStats | null;
  loading: boolean;
  error: string | null;

  // Actions
  discover: () => Promise<void>;
  refresh: () => Promise<void>;
}

export function useSpecGraph(): UseSpecGraphResult {
  const [discovered, setDiscovered] = useState(false);
  const [stats, setStats] = useState<SpecGraphStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const discover = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invokeSpecGraph<{ count: number; stats: SpecGraphStats }>('discover');
      setStats(result.stats);
      setDiscovered(result.count > 0);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Discovery failed');
    } finally {
      setLoading(false);
    }
  }, []);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await invokeSpecGraph<{ discovered: boolean; stats: SpecGraphStats }>(
        'manifest'
      );
      setStats(result.stats);
      setDiscovered(result.discovered);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Refresh failed');
    } finally {
      setLoading(false);
    }
  }, []);

  // Auto-check on mount
  useEffect(() => {
    refresh();
  }, [refresh]);

  return {
    discovered,
    stats,
    loading,
    error,
    discover,
    refresh,
  };
}

export interface UseSpecQueryResult {
  // State
  spec: SpecQueryResult | null;
  loading: boolean;
  error: string | null;

  // Actions
  query: (path: string) => Promise<void>;
  clear: () => void;
}

export function useSpecQuery(): UseSpecQueryResult {
  const [spec, setSpec] = useState<SpecQueryResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const query = useCallback(async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const result = await invokeSpecGraph<{
        path: string;
        agentese_path: string;
        title: string;
        tier: string;
        confidence: number;
        derives_from: string[];
        edges: Record<string, string[]>;
        tokens: Record<string, number>;
      }>('query', { path });

      setSpec({
        node: {
          path: result.path,
          agentese_path: result.agentese_path,
          title: result.title,
          tier: result.tier,
          confidence: result.confidence,
          derives_from: result.derives_from,
        },
        edges: result.edges,
        tokens: result.tokens,
      });
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Query failed');
      setSpec(null);
    } finally {
      setLoading(false);
    }
  }, []);

  const clear = useCallback(() => {
    setSpec(null);
    setError(null);
  }, []);

  return {
    spec,
    loading,
    error,
    query,
    clear,
  };
}

export interface UseSpecEdgesResult {
  edges: SpecEdge[];
  loading: boolean;
  error: string | null;
  fetchEdges: (path: string, edgeType?: EdgeType) => Promise<void>;
}

export function useSpecEdges(): UseSpecEdgesResult {
  const [edges, setEdges] = useState<SpecEdge[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchEdges = useCallback(async (path: string, edgeType?: EdgeType) => {
    setLoading(true);
    setError(null);
    try {
      const params: Record<string, string> = { path };
      if (edgeType) params.edge_type = edgeType;

      const result = await invokeSpecGraph<{
        edges: Array<{ type: string; target: string; line?: number }>;
      }>('edges', params);

      setEdges(
        result.edges.map((e) => ({
          type: e.type as EdgeType,
          target: e.target,
          line: e.line,
        }))
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Fetch edges failed');
      setEdges([]);
    } finally {
      setLoading(false);
    }
  }, []);

  return {
    edges,
    loading,
    error,
    fetchEdges,
  };
}

export interface UseSpecNavigateResult {
  current: SpecNode | null;
  targets: Array<{
    path: string;
    title: string;
    tier: string;
    confidence: number;
  }>;
  edge: EdgeType;
  loading: boolean;
  error: string | null;
  navigate: (path: string, edge?: EdgeType) => Promise<void>;
  setEdge: (edge: EdgeType) => void;
}

export function useSpecNavigate(): UseSpecNavigateResult {
  const [current, setCurrent] = useState<SpecNode | null>(null);
  const [targets, setTargets] = useState<
    Array<{ path: string; title: string; tier: string; confidence: number }>
  >([]);
  const [edge, setEdge] = useState<EdgeType>('extends');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const navigate = useCallback(
    async (path: string, edgeType?: EdgeType) => {
      setLoading(true);
      setError(null);
      const currentEdge = edgeType || edge;

      try {
        const result = await invokeSpecGraph<{
          current: {
            path: string;
            title: string;
            tier: string;
          };
          targets: Array<{
            path: string;
            title: string;
            tier: string;
          }>;
        }>('navigate', { path, edge: currentEdge });

        setCurrent({
          path: result.current.path,
          agentese_path: '',
          title: result.current.title,
          tier: result.current.tier,
          confidence: 0.5,
          derives_from: [],
        });
        setTargets(
          result.targets.map((t) => ({
            ...t,
            confidence: 0.5,
          }))
        );
        if (edgeType) setEdge(edgeType);
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Navigate failed');
      } finally {
        setLoading(false);
      }
    },
    [edge]
  );

  return {
    current,
    targets,
    edge,
    loading,
    error,
    navigate,
    setEdge,
  };
}

// =============================================================================
// Exports
// =============================================================================

export { invokeSpecGraph };
