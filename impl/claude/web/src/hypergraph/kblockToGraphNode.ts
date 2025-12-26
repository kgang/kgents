/**
 * kblockToGraphNode — Transform K-Block API response to GraphNode format
 *
 * "Zero Seed nodes ARE K-Blocks. The derivation IS the lineage."
 *
 * This utility bridges the K-Blocks API (PostgreSQL-backed) with the
 * HypergraphEditor's GraphNode format, enabling Zero Seed content
 * (axioms, values, goals) to be viewable in the ContentPane.
 */

import type { GraphNode, Edge, EdgeType } from './state/types';
import type { KBlockDetailResponse } from '../api/client';

/**
 * Map K-Block kind to GraphNode kind.
 */
function mapKBlockKindToNodeKind(kind: string | null): GraphNode['kind'] {
  if (!kind) return 'unknown';

  const kindMap: Record<string, GraphNode['kind']> = {
    axiom: 'spec',
    ground: 'spec',
    value: 'spec',
    goal: 'spec',
    spec: 'spec',
    action: 'implementation',
    reflection: 'doc',
    representation: 'doc',
    system: 'config',
  };

  return kindMap[kind] ?? 'unknown';
}

/**
 * Map K-Block layer to derivation tier.
 */
function mapLayerToDerivationTier(
  layer: number | null
): GraphNode['derivationTier'] | undefined {
  if (layer === null) return undefined;

  // L0-L1: Axioms (foundational)
  if (layer <= 1) return 'AXIOM';

  // L2: Values (bootstrap)
  if (layer === 2) return 'BOOTSTRAP';

  // L3-L4: Goals/Specs (functor)
  if (layer <= 4) return 'FUNCTOR';

  // L5-L7: Actions/Reflections/Representations (empirical)
  return 'EMPIRICAL';
}

/**
 * Convert K-Block edge to GraphNode Edge.
 */
function convertKBlockEdge(
  edge: Record<string, unknown>,
  direction: 'incoming' | 'outgoing'
): Edge {
  const edgeKind = (edge.kind as string) || (edge.type as string) || 'references';
  const sourceId = (edge.source_id as string) || (edge.source as string) || '';
  const targetId = (edge.target_id as string) || (edge.target as string) || '';

  // Map edge kind to EdgeType
  const edgeTypeMap: Record<string, EdgeType> = {
    derives_from: 'derives_from',
    implements: 'implements',
    tests: 'tests',
    extends: 'extends',
    references: 'references',
    contradicts: 'contradicts',
    contains: 'contains',
    uses: 'uses',
    defines: 'defines',
  };

  const edgeType: EdgeType = edgeTypeMap[edgeKind] ?? 'references';

  return {
    id: `${sourceId}-${edgeKind}-${targetId}`,
    source: sourceId,
    target: targetId,
    type: edgeType,
    context: edge.context as string | undefined,
    stale: false,
    confidence: (edge.confidence as number) ?? 1.0,
  };
}

/**
 * Convert K-Block detail response to GraphNode format.
 *
 * @param kblock - K-Block detail response from kblocksApi.getById()
 * @param path - The path used to load this K-Block (for display purposes)
 * @returns GraphNode compatible with HypergraphEditor
 */
export function kblockToGraphNode(
  kblock: KBlockDetailResponse,
  path: string
): GraphNode {
  // Build title from path or extract from content
  const pathParts = path.split('/');
  const filename = pathParts[pathParts.length - 1] || kblock.id;
  const title = filename.replace(/\.(md|py|ts|tsx|js|jsx)$/, '');

  // Convert edges
  const incomingEdges: Edge[] = (kblock.incoming_edges || []).map((edge) =>
    convertKBlockEdge(edge, 'incoming')
  );

  const outgoingEdges: Edge[] = (kblock.outgoing_edges || []).map((edge) =>
    convertKBlockEdge(edge, 'outgoing')
  );

  // Find derivation parent from incoming edges
  const derivesFromEdge = incomingEdges.find((e) => e.type === 'derives_from');
  const derivationParent = derivesFromEdge?.source;

  return {
    path,
    title,
    kind: mapKBlockKindToNodeKind(kblock.kind),
    tier: kblock.has_proof ? 'CANONICAL' : 'STUB',
    confidence: kblock.confidence ?? 1.0,
    derivationTier: mapLayerToDerivationTier(kblock.layer),
    derivationParent,
    outgoingEdges,
    incomingEdges,
    content: kblock.content || '',
  };
}

/**
 * Check if a path refers to a Zero Seed K-Block.
 *
 * Zero Seed paths have the format:
 * - zero-seed/axioms/{id}
 * - zero-seed/values/{id}
 * - zero-seed/goals/{id}
 * - zero-seed/{category}/{id}
 *
 * @param path - Path to check
 * @returns true if this is a Zero Seed path
 */
export function isZeroSeedPath(path: string): boolean {
  return path.startsWith('zero-seed/');
}

/**
 * Extract K-Block ID from a Zero Seed path.
 *
 * @param path - Zero Seed path (e.g., "zero-seed/axioms/A1")
 * @returns K-Block ID or null if not a valid Zero Seed path
 */
export function extractKBlockId(path: string): string | null {
  if (!isZeroSeedPath(path)) return null;

  // Path format: zero-seed/{category}/{id}
  const parts = path.split('/');
  if (parts.length < 3) return null;

  // The ID is the last part
  return parts[parts.length - 1];
}

/**
 * Extract category from a Zero Seed path.
 *
 * @param path - Zero Seed path (e.g., "zero-seed/axioms/A1")
 * @returns Category (axioms, values, goals, etc.) or null
 */
export function extractZeroSeedCategory(path: string): string | null {
  if (!isZeroSeedPath(path)) return null;

  // Path format: zero-seed/{category}/{id}
  const parts = path.split('/');
  if (parts.length < 2) return null;

  return parts[1];
}
