/**
 * Constitutional Dashboard Components
 *
 * Pure SVG visualization of constitutional alignment, trust, and derivation graph.
 */

// =============================================================================
// Alignment & Trust Components
// =============================================================================

export { ConstitutionalDashboard } from './ConstitutionalDashboard';
export { ConstitutionalRadar } from './ConstitutionalRadar';
export { ConstitutionalScorecard } from './ConstitutionalScorecard';
export { TrustLevelBadge } from './TrustLevelBadge';
export { useConstitutional } from './useConstitutional';

// =============================================================================
// Derivation Graph Components (ASHC Self-Awareness)
// =============================================================================

export { ConstitutionalGraphView2 } from './ConstitutionalGraphView2';
export { ConstitutionalNode } from './ConstitutionalNode';
export { DerivationEdge } from './DerivationEdge';
export { LayerBand } from './LayerBand';

// =============================================================================
// Alignment & Trust Types
// =============================================================================

export type { ConstitutionalDashboardProps } from './ConstitutionalDashboard';

export type { ConstitutionalRadarProps } from './ConstitutionalRadar';

export type { ConstitutionalScorecardProps } from './ConstitutionalScorecard';

export type { TrustLevelBadgeProps } from './TrustLevelBadge';

export type { UseConstitutionalOptions, UseConstitutionalResult } from './useConstitutional';

export type {
  ConstitutionalAlignment,
  ConstitutionalData,
  ConstitutionalTrustResult,
  Principle,
  TrustLevel,
} from './types';

// =============================================================================
// Derivation Graph Types
// =============================================================================

export type { ConstitutionalGraphView2Props } from './ConstitutionalGraphView2';

export type { ConstitutionalNodeProps } from './ConstitutionalNode';

export type { DerivationEdgeProps } from './DerivationEdge';

export type { LayerBandProps } from './LayerBand';

export type {
  EpistemicLayer,
  EvidenceTier,
  ConstitutionalKBlock,
  DerivationEdge as DerivationEdgeType,
  GroundingResult,
  JustificationResult,
  ConsistencyReport,
  ConsistencyViolation,
  NodePosition,
  KBlockVisualState,
  DensityMode,
  ConstitutionalBlockId,
} from './graphTypes';

export {
  LAYER_NAMES,
  LAYER_DESCRIPTIONS,
  LAYER_COLORS,
  PRINCIPLE_COLORS,
  EVIDENCE_TIER_COLORS,
  EVIDENCE_TIER_THRESHOLDS,
  DENSITY_SIZES,
  L0_AXIOMS,
  L1_PRIMITIVES,
  L2_PRINCIPLES,
  L3_ARCHITECTURE,
  ALL_CONSTITUTIONAL_BLOCKS,
  getEvidenceTier,
} from './graphTypes';
