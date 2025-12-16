/**
 * Joy Component Library
 *
 * Animation primitives and personality components for the Crown Jewels UI.
 * Implements Foundation 5: Personality & Joy from the Enlightened Crown strategy.
 *
 * Key Principles:
 * 1. Respect prefers-reduced-motion - all animations honor user preferences
 * 2. Joy is not decoration - it's the difference between software and experience
 * 3. Empathy over error - failures should guide, not frustrate
 * 4. Personality per jewel - each Crown Jewel has its own voice
 *
 * @see plans/crown-jewels-enlightened.md - Foundation 5
 */

// =============================================================================
// Animation Primitives
// =============================================================================

export { Breathe, type BreatheProps, type BreatheSpeed } from './Breathe';
export { Pop, PopOnMount, type PopProps } from './Pop';
export { Shake, type ShakeProps, type ShakeIntensity } from './Shake';
export {
  Shimmer,
  ShimmerBlock,
  ShimmerText,
  type ShimmerProps,
  type ShimmerBlockProps,
  type ShimmerTextProps,
} from './Shimmer';

// =============================================================================
// Personality Components
// =============================================================================

export {
  PersonalityLoading,
  PersonalityLoadingInline,
  type PersonalityLoadingProps,
  type CrownJewel,
} from './PersonalityLoading';

export {
  EmpathyError,
  InlineError,
  FullPageError,
  type EmpathyErrorProps,
  type InlineErrorProps,
  type ErrorType,
} from './EmpathyError';

// =============================================================================
// Celebration
// =============================================================================

export {
  celebrate,
  celebrateQuick,
  celebrateEpic,
  type CelebrateOptions,
  type CelebrationIntensity,
} from './celebrate';

// =============================================================================
// Hooks
// =============================================================================

export {
  useMotionPreferences,
  getMotionPreferences,
  type MotionPreferences,
} from './useMotionPreferences';
