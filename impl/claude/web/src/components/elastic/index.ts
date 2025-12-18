/**
 * Elastic Primitives: Self-arranging layout components.
 *
 * These primitives enable layouts that gracefully adapt to:
 * - Changing viewport sizes
 * - Dynamic content (agents adding/removing widgets)
 * - User preferences (density settings)
 *
 * Core idea: Developers design state, not rendering. Layout is a projection.
 *
 * Layout Projection Functor:
 * - Content[D] : State → ContentDetail[D] (lossy compression)
 * - Layout[D]  : WidgetTree → Structure[D] (structural isomorphism)
 *
 * @see spec/protocols/projection.md (Layout Projection section)
 * @see plans/web-refactor/elastic-primitives.md
 * @see plans/web-refactor/layout-projection-functor.md
 */

// =============================================================================
// Canonical Types (Layout Projection Functor)
// =============================================================================

export type {
  Density,
  CollapseBehavior,
  LayoutHints,
  DensityMap,
  LayoutPrimitiveName,
  SplitBehavior,
  PanelBehavior,
  ActionsBehavior,
  FullLayoutContext,
  CompositionLaw,
  GlassVariant,
} from './types';

export {
  DENSITY_BREAKPOINTS,
  PHYSICAL_CONSTRAINTS,
  LAYOUT_PRIMITIVES,
  COMPOSITION_LAWS,
  DEFAULT_LAYOUT_HINTS,
  VERTICAL_COMPOSITION,
  HORIZONTAL_COMPOSITION,
  Z_INDEX_LAYERS,
  GLASS_EFFECT,
  BOTTOM_PANEL_HEIGHTS,
  TOP_PANEL_HEIGHTS,
  SIDEBAR_WIDTHS,
  getDensityFromWidth,
  fromDensity,
  createDensityMap,
  getPrimitiveBehavior,
} from './types';

// =============================================================================
// Layout Primitive Components
// =============================================================================

// Core container with layout strategies
export { ElasticContainer, LayoutContextProvider } from './ElasticContainer';
export type {
  ElasticContainerProps,
  LayoutStrategy,
  OverflowBehavior,
  TransitionStyle,
  ResponsiveValue,
} from './ElasticContainer';

// Priority-aware card
export { ElasticCard } from './ElasticCard';
export type {
  ElasticCardProps,
  MinContentLevel,
  ShrinkBehavior,
} from './ElasticCard';

// Intelligent placeholder states
export { ElasticPlaceholder } from './ElasticPlaceholder';
export type {
  ElasticPlaceholderProps,
  PlaceholderFor,
  PlaceholderState,
} from './ElasticPlaceholder';

// Two-pane responsive split (Split primitive)
export { ElasticSplit } from './ElasticSplit';
export type { ElasticSplitProps } from './ElasticSplit';

// Mobile bottom drawer (Panel primitive in compact mode)
export { BottomDrawer } from './BottomDrawer';
export type { BottomDrawerProps } from './BottomDrawer';

// Floating action buttons (Actions primitive in compact mode)
export { FloatingActions } from './FloatingActions';
export type { FloatingActionsProps, FloatingAction } from './FloatingActions';

// Floating sidebar (Panel primitive - overlay pattern)
export { FloatingSidebar } from './FloatingSidebar';
export type { FloatingSidebarProps } from './FloatingSidebar';

// Fixed bottom panel (Terminal/REPL - fixed pattern)
export { FixedBottomPanel, useBottomPanelPadding } from './FixedBottomPanel';
export type { FixedBottomPanelProps } from './FixedBottomPanel';

// Fixed top panel (Observer drawer - fixed pattern)
export { FixedTopPanel, useTopPanelOffset, getTopPanelHeight } from './FixedTopPanel';
export type { FixedTopPanelProps } from './FixedTopPanel';

// 3D page HOC/wrapper for crown jewels
export { Elastic3DPage, useElastic3DPage } from './Elastic3DPage';
export type { Elastic3DPageProps, Elastic3DPageContext } from './Elastic3DPage';

// Coordinated drawers demo (temporal coherence)
export { CoordinatedDrawers } from './CoordinatedDrawers';
export type { CoordinatedDrawersProps } from './CoordinatedDrawers';

// =============================================================================
// Hooks
// =============================================================================

// Re-export hooks for convenience
export {
  useLayoutContext,
  useLayoutMeasure,
  useWindowLayout,
  DEFAULT_LAYOUT_CONTEXT,
} from '@/hooks/useLayoutContext';

// =============================================================================
// Legacy Types (for backwards compatibility)
// =============================================================================

// Re-export types from reactive/types (will migrate to ./types)
export type { LayoutContext, WidgetLayoutHints } from '@/reactive/types';
