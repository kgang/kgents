/**
 * Genesis Container Primitives
 *
 * Container components that wrap existing elements with breathing/growing/unfurling animations.
 * Implements Crown Jewels Genesis Moodboard animation patterns.
 *
 * @see plans/crown-jewels-genesis.md - Phase 1: Foundation
 * @see docs/creative/crown-jewels-genesis-moodboard.md
 */

// =============================================================================
// Container Components
// =============================================================================

export {
  BreathingContainer,
  type BreathingContainerProps,
  type BreathingIntensity,
  type BreathingPeriod,
} from './BreathingContainer';

export {
  GrowingContainer,
  type GrowingContainerProps,
  type GrowingDuration,
} from './GrowingContainer';

export {
  UnfurlingPanel,
  type UnfurlingPanelProps,
} from './UnfurlingPanel';

export {
  OrganicToast,
  type OrganicToastProps,
  type OrganicToastType,
  type ToastOrigin,
} from './OrganicToast';

// =============================================================================
// Re-export hook types for convenience
// =============================================================================

export type { UnfurlDirection } from '@/hooks/useUnfurling';
export type { GrowthStage } from '@/hooks/useGrowing';
