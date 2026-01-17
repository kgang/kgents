/**
 * Barrel exports for Zustand stores.
 *
 * Import stores from this module for cleaner imports:
 * ```ts
 * import { useUIStore, useUserStore, showSuccess } from '@/stores';
 * ```
 */

// UI Store - panels, modals, notifications, loading states
export { useUIStore, showSuccess, showError, showInfo } from './uiStore';

// User Store - auth, subscription, credits
export {
  useUserStore,
  selectCanAfford,
  selectIsLODIncluded,
  selectCanInhabit,
  selectCanForce,
} from './userStore';

// Derivation Store - hypergraph derivation UX
export {
  useDerivationStore,
  // Types
  type DerivationNode,
  type DerivationEdge,
  type DerivationNodeType,
  type GroundingStatus,
  type CoherenceSummary,
  type RealizationState,
  type DerivationStore,
  // Selectors
  selectGroundedKBlocks,
  selectProvisionalKBlocks,
  selectOrphanKBlocks,
  selectCoherencePercent,
  selectAverageGaloisLoss,
  selectIsGrounded,
  selectAllPrinciples,
  selectAllConstitutions,
  selectAllKBlocks,
  selectNodeById,
  selectIsRealizing,
  selectRealizationStatus,
  // Helpers
  getCoherenceColor,
  getGaloisLossColor,
  formatGaloisLoss,
  getGroundingIcon,
  getGroundingStatusClass,
} from './derivationStore';

// Constitutional Graph Store - ASHC Self-Awareness visualization
export {
  useConstitutionalGraphStore,
  // Selectors
  selectBlockById,
  selectBlocksByLayer,
  selectIsOrphan,
  selectIsHighlighted,
  selectPosition,
  selectConsistencyScore,
  selectTotalBlocks,
  // Types
  type ConstitutionalGraphStore,
} from './constitutionalGraphStore';
