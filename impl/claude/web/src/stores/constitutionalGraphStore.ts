/**
 * Constitutional Graph Store - Zustand state for K-Block derivation visualization.
 *
 * Manages state for the ASHC Self-Awareness visualization showing L0->L1->L2->L3
 * derivation chains. Integrates with the ASHCSelfAwareness backend service.
 *
 * Philosophy:
 *   "The proof IS the decision. The mark IS the witness."
 *
 * @see services/zero_seed/ashc_self_awareness.py
 * @see docs/skills/metaphysical-fullstack.md
 */

import { create } from 'zustand';
import type {
  ConstitutionalKBlock,
  DerivationEdge,
  GroundingResult,
  ConsistencyReport,
  EpistemicLayer,
  NodePosition,
  DensityMode,
} from '../components/constitutional/graphTypes';
import { getEvidenceTier, DENSITY_SIZES, L0_AXIOMS } from '../components/constitutional/graphTypes';

// =============================================================================
// State Types
// =============================================================================

interface ConstitutionalGraphState {
  // Data
  /** All K-Blocks indexed by ID */
  blocks: Map<string, ConstitutionalKBlock>;
  /** All derivation edges */
  edges: DerivationEdge[];
  /** Blocks grouped by layer for rendering */
  blocksByLayer: Map<EpistemicLayer, string[]>;

  // Selection
  /** Currently selected K-Block ID */
  selectedBlockId: string | null;
  /** Highlighted blocks (derivation path of selected) */
  highlightedBlockIds: Set<string>;
  /** Current grounding result for selected block */
  groundingResult: GroundingResult | null;

  // Consistency
  /** Latest consistency report */
  consistencyReport: ConsistencyReport | null;
  /** Orphan block IDs */
  orphanBlockIds: Set<string>;

  // Layout
  /** Computed positions for each block */
  positions: Map<string, NodePosition>;
  /** Current density mode */
  density: DensityMode;
  /** Container width (for layout calculation) */
  containerWidth: number;
  /** Container height */
  containerHeight: number;

  // Loading/Error
  isLoading: boolean;
  error: string | null;
}

// =============================================================================
// Actions
// =============================================================================

interface ConstitutionalGraphActions {
  // Data loading
  /** Initialize graph with genesis K-Blocks */
  initializeGraph: () => Promise<void>;
  /** Refresh data from backend */
  refresh: () => Promise<void>;

  // Selection
  /** Select a K-Block and load its grounding result */
  selectBlock: (blockId: string | null) => Promise<void>;
  /** Clear selection */
  clearSelection: () => void;

  // Consistency
  /** Check graph consistency */
  checkConsistency: () => Promise<void>;

  // Layout
  /** Set density mode */
  setDensity: (density: DensityMode) => void;
  /** Update container dimensions */
  setContainerSize: (width: number, height: number) => void;
  /** Recalculate all positions */
  recalculateLayout: () => void;

  // Utility
  /** Get derivation ancestors for a block */
  getAncestors: (blockId: string) => string[];
  /** Get downstream dependents for a block */
  getDependents: (blockId: string) => string[];
  /** Clear error */
  clearError: () => void;
  /** Reset to initial state */
  reset: () => void;
}

// =============================================================================
// Store Type
// =============================================================================

export type ConstitutionalGraphStore = ConstitutionalGraphState & ConstitutionalGraphActions;

// =============================================================================
// Initial State
// =============================================================================

const initialState: ConstitutionalGraphState = {
  blocks: new Map(),
  edges: [],
  blocksByLayer: new Map([
    [0, []],
    [1, []],
    [2, []],
    [3, []],
  ]),
  selectedBlockId: null,
  highlightedBlockIds: new Set(),
  groundingResult: null,
  consistencyReport: null,
  orphanBlockIds: new Set(),
  positions: new Map(),
  density: 'comfortable',
  containerWidth: 800,
  containerHeight: 600,
  isLoading: false,
  error: null,
};

// =============================================================================
// Genesis Block Definitions (static data matching backend)
// =============================================================================

/**
 * Static genesis K-Block data matching the backend factory.
 * This allows the frontend to render immediately without API call.
 */
const GENESIS_BLOCKS: ConstitutionalKBlock[] = [
  // L0 Axioms
  {
    id: 'A1_ENTITY',
    title: 'A1: ENTITY - There Exist Things',
    layer: 0,
    galoisLoss: 0.0,
    evidenceTier: 'categorical',
    derivesFrom: [],
    dependents: ['COMPOSE', 'JUDGE', 'GROUND', 'CONSTITUTION'],
    tags: ['axiom', 'L0', 'existence'],
  },
  {
    id: 'A2_MORPHISM',
    title: 'A2: MORPHISM - Things Relate',
    layer: 0,
    galoisLoss: 0.0,
    evidenceTier: 'categorical',
    derivesFrom: [],
    dependents: ['COMPOSE', 'JUDGE', 'GROUND', 'CONSTITUTION'],
    tags: ['axiom', 'L0', 'relation'],
  },
  {
    id: 'A3_MIRROR',
    title: 'A3: MIRROR - Systems Self-Reflect',
    layer: 0,
    galoisLoss: 0.0,
    evidenceTier: 'categorical',
    derivesFrom: [],
    dependents: ['JUDGE', 'GROUND', 'CONSTITUTION'],
    tags: ['axiom', 'L0', 'self-reference'],
  },
  {
    id: 'G_GALOIS',
    title: 'G: GALOIS - Structure Preserves',
    layer: 0,
    galoisLoss: 0.0,
    evidenceTier: 'categorical',
    derivesFrom: [],
    dependents: ['GROUND', 'CONSTITUTION'],
    tags: ['axiom', 'L0', 'adjunction'],
  },

  // L1 Primitives
  {
    id: 'COMPOSE',
    title: 'COMPOSE - Morphisms Chain',
    layer: 1,
    galoisLoss: 0.01,
    evidenceTier: 'categorical',
    derivesFrom: ['A1_ENTITY', 'A2_MORPHISM'],
    dependents: ['ID', 'COMPOSABLE'],
    tags: ['primitive', 'L1', 'composition'],
  },
  {
    id: 'JUDGE',
    title: 'JUDGE - Evaluate Truth',
    layer: 1,
    galoisLoss: 0.02,
    evidenceTier: 'categorical',
    derivesFrom: ['A1_ENTITY', 'A2_MORPHISM', 'A3_MIRROR'],
    dependents: ['CONTRADICT', 'ETHICAL'],
    tags: ['primitive', 'L1', 'evaluation'],
  },
  {
    id: 'GROUND',
    title: 'GROUND - Anchor to Reality',
    layer: 1,
    galoisLoss: 0.03,
    evidenceTier: 'categorical',
    derivesFrom: ['A1_ENTITY', 'A2_MORPHISM', 'A3_MIRROR', 'G_GALOIS'],
    dependents: ['FIX', 'TASTEFUL'],
    tags: ['primitive', 'L1', 'grounding'],
  },
  {
    id: 'ID',
    title: 'ID - Identity Morphism',
    layer: 1,
    galoisLoss: 0.01,
    evidenceTier: 'categorical',
    derivesFrom: ['COMPOSE'],
    dependents: [],
    tags: ['primitive', 'L1', 'identity'],
  },
  {
    id: 'CONTRADICT',
    title: 'CONTRADICT - Detect Conflicts',
    layer: 1,
    galoisLoss: 0.05,
    evidenceTier: 'categorical',
    derivesFrom: ['JUDGE'],
    dependents: ['SUBLATE'],
    tags: ['primitive', 'L1', 'contradiction'],
  },
  {
    id: 'SUBLATE',
    title: 'SUBLATE - Resolve via Synthesis',
    layer: 1,
    galoisLoss: 0.08,
    evidenceTier: 'categorical',
    derivesFrom: ['CONTRADICT'],
    dependents: ['HETERARCHICAL'],
    tags: ['primitive', 'L1', 'dialectic'],
  },
  {
    id: 'FIX',
    title: 'FIX - Find Fixed Points',
    layer: 1,
    galoisLoss: 0.04,
    evidenceTier: 'categorical',
    derivesFrom: ['GROUND'],
    dependents: ['GENERATIVE'],
    tags: ['primitive', 'L1', 'fixed-point'],
  },

  // L2 Principles
  {
    id: 'CONSTITUTION',
    title: 'CONSTITUTION - The Root Principle',
    layer: 2,
    galoisLoss: 0.05,
    evidenceTier: 'categorical',
    derivesFrom: ['A1_ENTITY', 'A2_MORPHISM', 'A3_MIRROR', 'G_GALOIS'],
    dependents: [
      'TASTEFUL',
      'CURATED',
      'ETHICAL',
      'JOY_INDUCING',
      'COMPOSABLE',
      'HETERARCHICAL',
      'GENERATIVE',
    ],
    tags: ['principle', 'L2', 'constitution'],
  },
  {
    id: 'TASTEFUL',
    title: 'TASTEFUL - Clear, Justified Purpose',
    layer: 2,
    galoisLoss: 0.12,
    evidenceTier: 'empirical',
    derivesFrom: ['CONSTITUTION', 'GROUND'],
    dependents: ['ASHC', 'METAPHYSICAL_FULLSTACK'],
    tags: ['principle', 'L2', 'taste'],
  },
  {
    id: 'CURATED',
    title: 'CURATED - Intentional Selection',
    layer: 2,
    galoisLoss: 0.15,
    evidenceTier: 'empirical',
    derivesFrom: ['CONSTITUTION'],
    dependents: ['HYPERGRAPH_EDITOR'],
    tags: ['principle', 'L2', 'curation'],
  },
  {
    id: 'ETHICAL',
    title: 'ETHICAL - Augments, Never Replaces',
    layer: 2,
    galoisLoss: 0.1,
    evidenceTier: 'categorical',
    derivesFrom: ['CONSTITUTION', 'JUDGE'],
    dependents: ['ASHC'],
    tags: ['principle', 'L2', 'ethics'],
  },
  {
    id: 'JOY_INDUCING',
    title: 'JOY-INDUCING - Delight in Interaction',
    layer: 2,
    galoisLoss: 0.35,
    evidenceTier: 'empirical',
    derivesFrom: ['CONSTITUTION'],
    dependents: ['HYPERGRAPH_EDITOR'],
    tags: ['principle', 'L2', 'joy'],
  },
  {
    id: 'COMPOSABLE',
    title: 'COMPOSABLE - Morphisms in a Category',
    layer: 2,
    galoisLoss: 0.08,
    evidenceTier: 'categorical',
    derivesFrom: ['CONSTITUTION', 'COMPOSE'],
    dependents: ['ASHC', 'AGENTESE'],
    tags: ['principle', 'L2', 'composition'],
  },
  {
    id: 'HETERARCHICAL',
    title: 'HETERARCHICAL - Flux, Not Hierarchy',
    layer: 2,
    galoisLoss: 0.2,
    evidenceTier: 'empirical',
    derivesFrom: ['CONSTITUTION', 'SUBLATE'],
    dependents: ['AGENTESE'],
    tags: ['principle', 'L2', 'heterarchy'],
  },
  {
    id: 'GENERATIVE',
    title: 'GENERATIVE - Spec as Compression',
    layer: 2,
    galoisLoss: 0.18,
    evidenceTier: 'empirical',
    derivesFrom: ['CONSTITUTION', 'FIX'],
    dependents: ['ASHC', 'METAPHYSICAL_FULLSTACK'],
    tags: ['principle', 'L2', 'generation'],
  },

  // L3 Architecture
  {
    id: 'ASHC',
    title: 'ASHC - Agentic Self-Hosting Compiler',
    layer: 3,
    galoisLoss: 0.22,
    evidenceTier: 'empirical',
    derivesFrom: ['TASTEFUL', 'ETHICAL', 'COMPOSABLE', 'GENERATIVE'],
    dependents: [],
    tags: ['architecture', 'L3', 'compiler'],
  },
  {
    id: 'METAPHYSICAL_FULLSTACK',
    title: 'METAPHYSICAL FULLSTACK - The Vertical Slice',
    layer: 3,
    galoisLoss: 0.25,
    evidenceTier: 'empirical',
    derivesFrom: ['TASTEFUL', 'GENERATIVE'],
    dependents: [],
    tags: ['architecture', 'L3', 'fullstack'],
  },
  {
    id: 'HYPERGRAPH_EDITOR',
    title: 'HYPERGRAPH EDITOR - Six-Mode Modal Editing',
    layer: 3,
    galoisLoss: 0.28,
    evidenceTier: 'empirical',
    derivesFrom: ['CURATED', 'JOY_INDUCING'],
    dependents: [],
    tags: ['architecture', 'L3', 'editor'],
  },
  {
    id: 'AGENTESE',
    title: 'AGENTESE - The Universal Protocol',
    layer: 3,
    galoisLoss: 0.2,
    evidenceTier: 'empirical',
    derivesFrom: ['COMPOSABLE', 'HETERARCHICAL'],
    dependents: [],
    tags: ['architecture', 'L3', 'protocol'],
  },
];

// =============================================================================
// Layout Calculation
// =============================================================================

function calculatePositions(
  blocksByLayer: Map<EpistemicLayer, string[]>,
  density: DensityMode,
  containerWidth: number
): Map<string, NodePosition> {
  const positions = new Map<string, NodePosition>();
  const sizes = DENSITY_SIZES[density];

  // Layers from bottom (L3) to top (L0)
  const layers: EpistemicLayer[] = [3, 2, 1, 0];

  layers.forEach((layer, layerIndex) => {
    const blockIds = blocksByLayer.get(layer) || [];
    const totalWidth = blockIds.length * (sizes.nodeWidth + sizes.nodeGap) - sizes.nodeGap;
    const startX = (containerWidth - totalWidth) / 2;
    const y = (layers.length - 1 - layerIndex) * sizes.layerGap + sizes.padding + sizes.nodeHeight;

    blockIds.forEach((blockId, index) => {
      const x = startX + index * (sizes.nodeWidth + sizes.nodeGap) + sizes.nodeWidth / 2;
      positions.set(blockId, { x, y });
    });
  });

  return positions;
}

// =============================================================================
// Store Implementation
// =============================================================================

export const useConstitutionalGraphStore = create<ConstitutionalGraphStore>()((set, get) => ({
  ...initialState,

  // =========================================================================
  // Data Loading
  // =========================================================================

  initializeGraph: async () => {
    set({ isLoading: true, error: null });

    try {
      // Initialize with static genesis data
      const blocks = new Map<string, ConstitutionalKBlock>();
      const blocksByLayer = new Map<EpistemicLayer, string[]>([
        [0, []],
        [1, []],
        [2, []],
        [3, []],
      ]);
      const edges: DerivationEdge[] = [];

      GENESIS_BLOCKS.forEach((block) => {
        blocks.set(block.id, block);
        const layerBlocks = blocksByLayer.get(block.layer) || [];
        layerBlocks.push(block.id);
        blocksByLayer.set(block.layer, layerBlocks);

        // Build edges from derivesFrom
        block.derivesFrom.forEach((parentId) => {
          const parent = GENESIS_BLOCKS.find((b) => b.id === parentId);
          edges.push({
            sourceId: parentId,
            targetId: block.id,
            loss: block.galoisLoss - (parent?.galoisLoss || 0),
          });
        });
      });

      const { containerWidth, density } = get();
      const positions = calculatePositions(blocksByLayer, density, containerWidth);

      set({
        blocks,
        blocksByLayer,
        edges,
        positions,
        isLoading: false,
      });
    } catch (err) {
      set({
        error: err instanceof Error ? err.message : 'Failed to initialize graph',
        isLoading: false,
      });
    }
  },

  refresh: async () => {
    // TODO: Fetch fresh data from backend API
    // For now, just re-initialize
    await get().initializeGraph();
  },

  // =========================================================================
  // Selection
  // =========================================================================

  selectBlock: async (blockId) => {
    if (!blockId) {
      get().clearSelection();
      return;
    }

    const { blocks } = get();
    const block = blocks.get(blockId);
    if (!block) return;

    // Calculate derivation path (ancestors)
    const highlightedBlockIds = new Set<string>();
    const ancestors = get().getAncestors(blockId);
    ancestors.forEach((id) => highlightedBlockIds.add(id));
    highlightedBlockIds.add(blockId);

    // Calculate downstream dependents
    const dependents = get().getDependents(blockId);
    dependents.forEach((id) => highlightedBlockIds.add(id));

    // Build grounding result
    const lossAtEachStep: number[] = [];
    let totalLoss = 0;
    ancestors.reverse().forEach((id) => {
      const ancestorBlock = blocks.get(id);
      if (ancestorBlock) {
        lossAtEachStep.push(ancestorBlock.galoisLoss);
        totalLoss += ancestorBlock.galoisLoss;
      }
    });
    lossAtEachStep.push(block.galoisLoss);
    totalLoss += block.galoisLoss;

    const isGrounded = ancestors.some((id) => L0_AXIOMS.includes(id as (typeof L0_AXIOMS)[number]));
    const maxLoss = Math.max(...lossAtEachStep, 0);

    const groundingResult: GroundingResult = {
      isGrounded,
      derivationPath: [...ancestors.reverse(), blockId],
      lossAtEachStep,
      evidenceTier: getEvidenceTier(maxLoss),
      totalLoss,
    };

    set({
      selectedBlockId: blockId,
      highlightedBlockIds,
      groundingResult,
    });
  },

  clearSelection: () => {
    set({
      selectedBlockId: null,
      highlightedBlockIds: new Set(),
      groundingResult: null,
    });
  },

  // =========================================================================
  // Consistency
  // =========================================================================

  checkConsistency: async () => {
    const { blocks } = get();

    const violations: ConsistencyReport['violations'] = [];
    const orphanBlocks: string[] = [];

    // Check each block
    blocks.forEach((block, blockId) => {
      // Check for orphans (non-L0 blocks without parents)
      if (block.layer > 0 && block.derivesFrom.length === 0) {
        orphanBlocks.push(blockId);
        violations.push({
          kind: 'orphan',
          blockId,
          description: `Block ${blockId} (layer ${block.layer}) has no parent derivation`,
          relatedBlocks: [],
        });
      }

      // Check for missing parents
      block.derivesFrom.forEach((parentId) => {
        if (!blocks.has(parentId)) {
          violations.push({
            kind: 'missing_parent',
            blockId,
            description: `Block ${blockId} references unknown parent ${parentId}`,
            relatedBlocks: [parentId],
          });
        }
      });
    });

    const consistencyReport: ConsistencyReport = {
      isConsistent: violations.length === 0,
      violations,
      circularDependencies: [], // TODO: Implement cycle detection
      orphanBlocks,
      totalBlocks: blocks.size,
      groundedBlocks: blocks.size - orphanBlocks.length,
      consistencyScore: (blocks.size - orphanBlocks.length) / blocks.size,
    };

    set({
      consistencyReport,
      orphanBlockIds: new Set(orphanBlocks),
    });
  },

  // =========================================================================
  // Layout
  // =========================================================================

  setDensity: (density) => {
    set({ density });
    get().recalculateLayout();
  },

  setContainerSize: (width, height) => {
    set({ containerWidth: width, containerHeight: height });
    get().recalculateLayout();
  },

  recalculateLayout: () => {
    const { blocksByLayer, density, containerWidth } = get();
    const positions = calculatePositions(blocksByLayer, density, containerWidth);
    set({ positions });
  },

  // =========================================================================
  // Queries
  // =========================================================================

  getAncestors: (blockId) => {
    const { blocks } = get();
    const ancestors: string[] = [];
    const visited = new Set<string>();

    const traverse = (id: string) => {
      if (visited.has(id)) return;
      visited.add(id);

      const block = blocks.get(id);
      if (!block) return;

      block.derivesFrom.forEach((parentId) => {
        ancestors.push(parentId);
        traverse(parentId);
      });
    };

    traverse(blockId);
    return ancestors;
  },

  getDependents: (blockId) => {
    const { blocks } = get();
    const dependents: string[] = [];
    const visited = new Set<string>();

    const traverse = (id: string) => {
      if (visited.has(id)) return;
      visited.add(id);

      const block = blocks.get(id);
      if (!block) return;

      block.dependents.forEach((childId) => {
        dependents.push(childId);
        traverse(childId);
      });
    };

    traverse(blockId);
    return dependents;
  },

  // =========================================================================
  // Utility
  // =========================================================================

  clearError: () => {
    set({ error: null });
  },

  reset: () => {
    set(initialState);
  },
}));

// =============================================================================
// Selectors
// =============================================================================

export const selectBlockById =
  (id: string) =>
  (state: ConstitutionalGraphStore): ConstitutionalKBlock | undefined =>
    state.blocks.get(id);

export const selectBlocksByLayer =
  (layer: EpistemicLayer) =>
  (state: ConstitutionalGraphStore): ConstitutionalKBlock[] => {
    const ids = state.blocksByLayer.get(layer) || [];
    return ids.map((id) => state.blocks.get(id)).filter(Boolean) as ConstitutionalKBlock[];
  };

export const selectIsOrphan =
  (blockId: string) =>
  (state: ConstitutionalGraphStore): boolean =>
    state.orphanBlockIds.has(blockId);

export const selectIsHighlighted =
  (blockId: string) =>
  (state: ConstitutionalGraphStore): boolean =>
    state.highlightedBlockIds.has(blockId);

export const selectPosition =
  (blockId: string) =>
  (state: ConstitutionalGraphStore): NodePosition | undefined =>
    state.positions.get(blockId);

export const selectConsistencyScore = (state: ConstitutionalGraphStore): number =>
  state.consistencyReport?.consistencyScore ?? 1.0;

export const selectTotalBlocks = (state: ConstitutionalGraphStore): number => state.blocks.size;
