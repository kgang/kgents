/**
 * Genesis Types — Constitutional Graph
 *
 * Grounded in: spec/protocols/genesis-clean-slate.md
 *
 * The Genesis Constitutional Graph is the pre-seeded foundation
 * that the system reveals to new users. 22 K-Blocks across 4 layers.
 */

/**
 * Genesis layer — derivation depth from axioms
 */
export type GenesisLayer = 0 | 1 | 2 | 3;

/**
 * Layer metadata
 */
export interface LayerInfo {
  readonly level: GenesisLayer;
  readonly name: string;
  readonly description: string;
  readonly count: number;
}

export const GENESIS_LAYERS: readonly LayerInfo[] = [
  { level: 0, name: 'Zero Seed', description: 'The irreducible axioms', count: 4 },
  { level: 1, name: 'Minimal Kernel', description: 'Operational primitives', count: 7 },
  { level: 2, name: 'Principles', description: 'Design guidelines', count: 7 },
  { level: 3, name: 'Architecture', description: 'Self-description patterns', count: 4 },
] as const;

/**
 * Galois-witnessed proof (for L1+ K-Blocks)
 */
export interface GaloisWitnessedProof {
  readonly data: string;
  readonly warrant: string;
  readonly claim: string;
  readonly galoisLoss: number;
  readonly principles?: readonly string[];
}

/**
 * Genesis K-Block — a node in the Constitutional Graph
 */
export interface GenesisKBlock {
  readonly id: string; // e.g., "genesis:L0:entity"
  readonly path: string; // AGENTESE path
  readonly layer: GenesisLayer;
  readonly title: string;
  readonly summary: string; // One-line description
  readonly content: string; // Full markdown content
  readonly proof: GaloisWitnessedProof | null; // null for L0 axioms
  readonly confidence: number; // 1 - galoisLoss
  readonly color: string; // LIVING_EARTH hex
  readonly derivationsFrom: readonly string[]; // K-Block IDs this derives from
  readonly derivationsTo: readonly string[]; // K-Block IDs that derive from this
  readonly tags: readonly string[];
}

/**
 * Derivation edge type
 */
export type DerivationEdgeType = 'derives_from' | 'implements' | 'embodies';

/**
 * Edge in the Constitutional Graph
 */
export interface DerivationEdge {
  readonly source: string; // K-Block ID
  readonly target: string; // K-Block ID
  readonly type: DerivationEdgeType;
}

/**
 * The Constitutional Graph — the full genesis structure
 */
export interface ConstitutionalGraph {
  readonly nodes: Record<string, GenesisKBlock>;
  readonly edges: readonly DerivationEdge[];
}

/**
 * Genesis phase — user's journey through first-run
 */
export type GenesisPhase = 'landing' | 'explore' | 'extend' | 'complete';

/**
 * Genesis state — tracks user's exploration
 */
export interface GenesisState {
  readonly phase: GenesisPhase;
  readonly currentLayer: GenesisLayer;
  readonly selectedNodeId: string | null;
  readonly visitedNodes: readonly string[];
  readonly userDeclaration: string | null;
}

/**
 * Initial genesis state
 */
export const INITIAL_GENESIS_STATE: GenesisState = {
  phase: 'landing',
  currentLayer: 0,
  selectedNodeId: null,
  visitedNodes: [],
  userDeclaration: null,
};

/**
 * LIVING_EARTH color palette for Genesis
 */
export const LIVING_EARTH_COLORS = {
  // L0: Warmest (most fundamental) — glow family
  'glow.lantern': '#F5E6D3',
  'glow.honey': '#E8C4A0',
  'glow.amber': '#D4A574',
  'glow.copper': '#C08552',

  // L1: Earth tones — green family (operational)
  'green.sage': '#4A6B4A',
  'green.mint': '#6B8B6B',
  'green.sprout': '#8BAB8B',
  'green.fern': '#2E4A2E',

  // L1: Earth tones — earth family
  'earth.wood': '#6B4E3D',
  'earth.clay': '#8B6F5C',
  'earth.sand': '#AB9080',

  // Semantic
  axiom: '#F5E6D3', // Warmest — L0
  primitive: '#4A6B4A', // Sage — L1
  principle: '#D4A574', // Amber — L2
  architecture: '#6B8B6B', // Mint — L3
} as const;

/**
 * Get color for a layer
 */
export function getLayerColor(layer: GenesisLayer): string {
  switch (layer) {
    case 0:
      return LIVING_EARTH_COLORS['glow.lantern'];
    case 1:
      return LIVING_EARTH_COLORS['green.sage'];
    case 2:
      return LIVING_EARTH_COLORS['glow.amber'];
    case 3:
      return LIVING_EARTH_COLORS['green.mint'];
  }
}

/**
 * Get layer by level
 */
export function getLayerInfo(level: GenesisLayer): LayerInfo {
  return GENESIS_LAYERS[level];
}

/**
 * Check if a K-Block is an axiom (L0)
 */
export function isAxiom(kblock: GenesisKBlock): boolean {
  return kblock.layer === 0;
}

/**
 * Check if a K-Block has been visited
 */
export function isVisited(state: GenesisState, nodeId: string): boolean {
  return state.visitedNodes.includes(nodeId);
}

/**
 * Get K-Blocks for a layer
 */
export function getLayerNodes(graph: ConstitutionalGraph, layer: GenesisLayer): GenesisKBlock[] {
  return Object.values(graph.nodes).filter((node) => node.layer === layer);
}

/**
 * Get derivation path from a node to L0
 */
export function getDerivationPath(graph: ConstitutionalGraph, nodeId: string): string[] {
  const path: string[] = [nodeId];
  let current = graph.nodes[nodeId];

  while (current && current.derivationsFrom.length > 0) {
    const parentId = current.derivationsFrom[0];
    path.unshift(parentId);
    current = graph.nodes[parentId];
  }

  return path;
}
