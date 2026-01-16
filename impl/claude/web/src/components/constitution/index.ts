/**
 * Personal Constitution Builder - Component Exports
 *
 * Main entry point for the constitution building UI.
 *
 * Mission: Let Kent see, accept, reject, and evolve his personal axioms.
 *
 * Philosophy:
 *   "The persona is a garden, not a museum."
 *   "Kent discovers his personal axioms. He didn't write them; he *discovered* them."
 *
 * @see stores/personalConstitutionStore.ts
 * @see api/axiomDiscovery.ts
 */

// =============================================================================
// Main Component
// =============================================================================

export { PersonalConstitutionBuilder } from './PersonalConstitutionBuilder';
export { default as PersonalConstitutionBuilderDefault } from './PersonalConstitutionBuilder';

// =============================================================================
// Sub-components
// =============================================================================

export { AxiomCard } from './AxiomCard';
export { DiscoveryProgress } from './DiscoveryProgress';
export { ContradictionAlert } from './ContradictionAlert';
export { ConstitutionExport } from './ConstitutionExport';

// =============================================================================
// Types
// =============================================================================

export type {
  // Axiom types
  AxiomCandidate,
  ConstitutionalAxiom,
  AxiomLayer,
  AxiomStatus,

  // Contradiction types
  ContradictionPair,
  ContradictionSeverity,

  // Discovery types
  DiscoveryProgress as DiscoveryProgressType,
  AxiomDiscoveryResult,

  // Constitution types
  PersonalConstitution,
  Amendment,

  // Export types
  ExportFormat,
  ExportOptions,

  // API types
  DiscoverAxiomsRequest,
  ValidateAxiomRequest,
  ValidateAxiomResponse,
} from './types';

// =============================================================================
// Type Helpers
// =============================================================================

export {
  getAxiomLayer,
  getLayerLabel,
  getLayerDescription,
  getContradictionSeverity,
  getSeverityLabel,
  generateAxiomId,
  candidateToConstitutional,
} from './types';
