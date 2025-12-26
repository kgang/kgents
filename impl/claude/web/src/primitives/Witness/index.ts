/**
 * Witness Primitives
 *
 * Two complementary aspects:
 * 1. Evidence display (Witness.tsx) - Shows compilation evidence with confidence tiers
 * 2. Action witnessing (useWitness, WitnessMark, etc.) - Tracks user actions as marks
 *
 * "Every action leaves a mark. The mark IS the witness."
 */

// =============================================================================
// Evidence Display (Existing)
// =============================================================================

export { Witness, type WitnessProps } from './Witness';

// =============================================================================
// Action Witnessing (New)
// =============================================================================

// Types
export type {
  WitnessMark,
  StateMorphism,
  WitnessedStateSetter,
  WitnessConfig,
  WitnessMarkVariant,
  WitnessTrailOrientation,
  WitnessTrail,
  Principle,
} from './types';

export {
  PRINCIPLES,
  PRINCIPLE_COLORS,
  PRINCIPLE_ICONS,
} from './types';

// Hooks
export { useWitness, type UseWitnessOptions } from './useWitness';
export { useWitnessedState } from './useWitnessedState';

// Components
export { WitnessMarkComponent, type WitnessMarkProps } from './WitnessMark';
export { WitnessTrailComponent, type WitnessTrailProps } from './WitnessTrail';

// HOC
export {
  withWitness,
  withPortalWitness,
  withNavigationWitness,
  withEditWitness,
  withChatWitness,
  type WithWitnessOptions,
  type WitnessInjectedProps,
} from './WithWitness';

// =============================================================================
// Default Export
// =============================================================================

export { useWitness as default } from './useWitness';
