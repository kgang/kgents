/**
 * kgents Type System
 *
 * Grounded in: spec/ui/axioms.md (The 8 Axioms)
 *
 * These types encode the Evergreen Frontend vision into TypeScript,
 * enabling type-safe anti-sloppification.
 */

// Provenance — A2 (Sloppification Visibility)
export type { Author, ReviewStatus, Provenance, ProvenanceRange } from './provenance';

export {
  PROVENANCE_INTENSITY,
  PROVENANCE_INDICATORS,
  PROVENANCE_CLASSES,
  createHumanProvenance,
  createAIProvenance,
  createFusionProvenance,
  needsReview,
  getProvenanceClass,
  getProvenanceIndicator,
} from './provenance';

// Lifecycle — A4 (No-Shipping, Garden Metaphor)
export type { LifecycleStage, LifecycleState, GardenItem, GardenState } from './lifecycle';

export {
  LIFECYCLE_COLORS,
  LIFECYCLE_ICONS,
  LIFECYCLE_CLASSES,
  LIFECYCLE_DESCRIPTIONS,
  mapBackendLifecycle,
  mapBackendHealth,
  needsAttention,
  getAttentionPriority,
  createSeedLifecycle,
} from './lifecycle';

// Collapse — A2 (Sloppification), A8 (Understandability)
export type {
  CollapseStatus,
  CollapseResult,
  ConstitutionalCollapse,
  GaloisTier,
  GaloisCollapse,
  SlopLevel,
  CollapseState,
} from './collapse';

export {
  COLLAPSE_COLORS,
  GALOIS_TIER_COLORS,
  SLOP_COLORS,
  COLLAPSE_ICONS,
  computeSlopLevel,
  getGaloisTier,
  createPendingResult,
  createDefaultCollapseState,
  formatCollapseResult,
  formatGaloisLoss,
  formatConstitutionalScore,
} from './collapse';

// Containers — A1 (Creativity), A6 (Authority)
export type {
  ContainerType,
  AuthorityLevel,
  ContainerContext,
  ContainerConfig,
} from './containers';

export {
  CONTAINER_CONFIGS,
  CONTAINER_DESCRIPTIONS,
  getDefaultContainerContext,
  createHumanContext,
  createCollaborationContext,
  createAIContext,
  getContainerFromProvenance,
  canEdit,
  showSloppificationIndicators,
  getContainerClass,
} from './containers';

// Genesis — Constitutional Graph (First-Run Experience)
export type {
  GenesisLayer,
  LayerInfo,
  GaloisWitnessedProof,
  GenesisKBlock,
  DerivationEdgeType,
  DerivationEdge,
  ConstitutionalGraph,
  GenesisPhase,
  GenesisState,
} from './genesis';

export {
  GENESIS_LAYERS,
  INITIAL_GENESIS_STATE,
  LIVING_EARTH_COLORS,
  getLayerColor,
  getLayerInfo,
  isAxiom,
  isVisited,
  getLayerNodes,
  getDerivationPath,
} from './genesis';
