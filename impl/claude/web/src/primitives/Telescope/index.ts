/**
 * Telescope Primitive
 *
 * "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 *
 * A universal viewer with focal distance, aperture, and filter controls.
 * Replaces GaloisTelescope + TelescopeNavigator (~2,000 LOC) with ~400 LOC total.
 */

export { Telescope } from './Telescope';
export { useTelescopeNavigation } from './useTelescopeNavigation';
export type {
  TelescopeProps,
  TelescopeState,
  NodeProjection,
  GradientVector,
  GradientArrow,
  NavigationDirection,
  Point,
} from './types';
export {
  focalDistanceToLayers,
  calculateNodePosition,
  buildGradientArrows,
  getLossColor,
  filterNodesByLoss,
  findLowestLossNode,
  findHighestLossNode,
  followGradient,
} from './utils';
export { LAYER_NAMES, LAYER_BASE_COLORS } from './types';
