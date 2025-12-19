/**
 * Umwelt Visualization Module
 *
 * Observer Reality Shift - When the observer changes, the world shifts.
 * This module provides the animation infrastructure for visualizing
 * how different observers perceive the AGENTESE world differently.
 *
 * "The noun is a lie. There is only the rate of change."
 *
 * @see plans/umwelt-visualization.md
 */

// Core types and constants
export type { AspectInfo, UmweltDiff, UmweltDensityConfig } from './umwelt.types';

export {
  UMWELT_MOTION,
  UMWELT_DENSITY_CONFIG,
  OBSERVER_COLORS,
  getObserverColor,
} from './umwelt.types';

// Context and hooks
export {
  UmweltProvider,
  useUmwelt,
  useUmweltSafe,
  type UmweltProviderProps,
} from './UmweltContext';

export { computeUmweltDiff, useUmweltDiff, useAspectAvailability } from './useUmweltDiff';

// Observer Persistence (Umwelt v2)
export { useObserverPersistence, clearStoredObserver } from './useObserverPersistence';

// Animation components
export {
  UmweltRipple,
  AccentRipple,
  type UmweltRippleProps,
  type AccentRippleProps,
} from './UmweltRipple';
