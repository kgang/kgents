/**
 * Categorical Components: Visualization primitives for polynomial agents.
 *
 * This module exports components that make the categorical structure
 * (PolyAgent × Operad × Sheaf) tangible and teachable across Town and Park.
 *
 * @see plans/park-town-design-overhaul.md
 * @see docs/skills/polynomial-agent.md
 */

// =============================================================================
// Presets (Domain-specific polynomial configurations)
// =============================================================================

export {
  // Types
  type Position,
  type Edge,
  type PolynomialPreset,
  type PresetKey,

  // Gallery presets
  TRAFFIC_LIGHT,
  VENDING_MACHINE,

  // Town presets
  CITIZEN,

  // Park presets
  CRISIS_PHASE,
  TIMER_STATE,
  CONSENT_DEBT,
  DIRECTOR,

  // Registry
  PRESETS,
  getPresetsByJewel,
  getPresetsByCategory,
  getAllPresetKeys,
} from './presets';

// =============================================================================
// Teaching Components
// =============================================================================

export {
  TeachingCallout,
  type TeachingCalloutProps,
  type TeachingCategory,
  TEACHING_MESSAGES,
  type TeachingMessageKey,
  getTeachingMessage,
} from './TeachingCallout';

// =============================================================================
// Trace Components (N-gent Witness)
// =============================================================================

export {
  TracePanel,
  type TracePanelProps,
  type TraceEvent,
  createPhaseTransitionEvent,
  createTimerEvent,
  createForceEvent,
  createMaskEvent,
  resetEventCounter,
} from './TracePanel';

// =============================================================================
// State Indicators
// =============================================================================

export {
  StateIndicator,
  type StateIndicatorProps,
  type StateCategory,
  CitizenPhaseIndicator,
  CrisisPhaseIndicator,
  TimerStateIndicator,
  ConsentDebtIndicator,
  DirectorStateIndicator,
} from './StateIndicator';

// =============================================================================
// Onboarding
// =============================================================================

export {
  FirstVisitOverlay,
  type FirstVisitOverlayProps,
  type JewelType,
  useResetFirstVisit,
} from './FirstVisitOverlay';

// =============================================================================
// Re-exports from Gallery (for backward compatibility)
// =============================================================================

// Note: The existing PolynomialPlayground and OperadWiring remain in
// components/projection/gallery/ for now. They should be imported from there.
// A future PR can move them here once Town and Park are updated.
//
// Planned exports (after migration):
// export { PolynomialPlayground } from './PolynomialPlayground';
// export { OperadWiring } from './OperadWiring';
