/**
 * Elastic Layout Types - Layout Projection Functor
 *
 * Canonical types for the Layout Projection Functor as specified in
 * spec/protocols/projection.md (lines 213-424).
 *
 * Key insight: Mobile layouts are not "compressed desktop"—they are
 * structurally different. A sidebar on desktop becomes a bottom drawer
 * on mobile, but the SAME INFORMATION is accessible through different
 * interaction modalities.
 *
 * @see spec/protocols/projection.md
 * @see plans/web-refactor/layout-projection-functor.md
 */

// =============================================================================
// Density - The Three Canonical Levels
// =============================================================================

/**
 * Density levels matching spec/protocols/projection.md:
 * - compact: < 768px (mobile)
 * - comfortable: 768-1024px (tablet)
 * - spacious: > 1024px (desktop)
 */
export type Density = 'compact' | 'comfortable' | 'spacious';

/**
 * Breakpoints for density transitions.
 * These match the spec and are used by useLayoutContext.
 */
export const DENSITY_BREAKPOINTS = {
  /** Below this: compact */
  sm: 768,
  /** Below this: comfortable; above this: spacious */
  lg: 1024,
} as const;

/**
 * Get density from viewport width.
 * Implements the spec's three-tier density model.
 */
export function getDensityFromWidth(width: number): Density {
  if (width < DENSITY_BREAKPOINTS.sm) return 'compact';
  if (width < DENSITY_BREAKPOINTS.lg) return 'comfortable';
  return 'spacious';
}

// =============================================================================
// Layout Hints - Widget-provided guidance for projection
// =============================================================================

/**
 * How a widget collapses in compact mode.
 * From spec: collapseTo?: 'drawer' | 'tab' | 'hidden'
 */
export type CollapseBehavior = 'drawer' | 'tab' | 'hidden';

/**
 * Layout hints that widgets can provide for elastic rendering.
 * These hints guide the layout functor but do not determine it—the
 * projection target makes the final decision based on available space.
 *
 * From spec/protocols/projection.md:
 * ```typescript
 * interface LayoutHints {
 *   collapseAt?: number;        // Viewport width to collapse
 *   collapseTo?: 'drawer' | 'tab' | 'hidden';
 *   priority?: number;          // Truncation order (lower = keep longer)
 *   requiresFullWidth?: boolean; // Cannot share horizontal space
 *   minTouchTarget?: number;     // Physical minimum (default 48)
 * }
 * ```
 */
export interface LayoutHints {
  /** Viewport width threshold to trigger collapse (px) */
  collapseAt?: number;

  /** How to present this widget when collapsed */
  collapseTo?: CollapseBehavior;

  /** Truncation/hide priority: lower values survive longer */
  priority?: number;

  /** If true, widget cannot share horizontal space with siblings */
  requiresFullWidth?: boolean;

  /**
   * Minimum touch target size (px).
   * Physical constraint that does NOT scale with density.
   * Default: 48px (per spec: TouchTarget[D] >= 48px for all D)
   */
  minTouchTarget?: number;
}

/**
 * Default layout hints.
 */
export const DEFAULT_LAYOUT_HINTS: Required<LayoutHints> = {
  collapseAt: DENSITY_BREAKPOINTS.sm,
  collapseTo: 'drawer',
  priority: 0,
  requiresFullWidth: false,
  minTouchTarget: 48,
} as const;

// =============================================================================
// Physical Constraints - Density-invariant minimums
// =============================================================================

/**
 * Physical constraints from spec that do NOT scale with density.
 * These are invariants that must be satisfied regardless of projection target.
 */
export const PHYSICAL_CONSTRAINTS = {
  /** Minimum touch target size (px): TouchTarget[D] >= 48px ∀D */
  minTouchTarget: 48,
  /** Minimum readable font size (px) */
  minFontSize: 14,
  /** Minimum spacing between adjacent touch targets (px) */
  minTapSpacing: 8,
  /** Drawer handle visual area (px) - but touch target must be 48x48 */
  drawerHandleVisual: { width: 40, height: 4 },
} as const;

// =============================================================================
// Density-Parameterized Constants - The canonical pattern
// =============================================================================

/**
 * Type for density-parameterized values.
 * This is the canonical pattern for density-dependent values,
 * replacing scattered conditionals (isMobile ? X : Y).
 */
export type DensityMap<T> = Record<Density, T>;

/**
 * Look up a value from a density map.
 * This is the canonical accessor for density-parameterized values.
 *
 * @example
 * const NODE_SIZE: DensityMap<number> = { compact: 0.2, comfortable: 0.25, spacious: 0.3 };
 * const size = fromDensity(NODE_SIZE, density);
 */
export function fromDensity<T>(map: DensityMap<T>, density: Density): T {
  return map[density];
}

/**
 * Create a density map with a default value and optional overrides.
 *
 * @example
 * const padding = createDensityMap(16, { compact: 8, spacious: 24 });
 * // → { compact: 8, comfortable: 16, spacious: 24 }
 */
export function createDensityMap<T>(
  defaultValue: T,
  overrides?: Partial<DensityMap<T>>
): DensityMap<T> {
  return {
    compact: overrides?.compact ?? defaultValue,
    comfortable: overrides?.comfortable ?? defaultValue,
    spacious: overrides?.spacious ?? defaultValue,
  };
}

// =============================================================================
// Layout Primitives - The three basis elements
// =============================================================================

/**
 * Layout primitive names from spec.
 * These form the basis of the layout functor.
 */
export type LayoutPrimitiveName = 'split' | 'panel' | 'actions';

/**
 * Behavior modes for the Split primitive.
 */
export type SplitBehavior = 'collapse_secondary' | 'fixed_panes' | 'resizable_divider';

/**
 * Behavior modes for the Panel primitive.
 */
export type PanelBehavior = 'bottom_drawer' | 'collapsible_panel' | 'fixed_sidebar';

/**
 * Behavior modes for the Actions primitive.
 */
export type ActionsBehavior = 'floating_fab' | 'inline_buttons' | 'full_toolbar';

/**
 * The three canonical layout primitives from spec:
 *
 * | Primitive | Compact | Comfortable | Spacious |
 * |-----------|---------|-------------|----------|
 * | Split | Collapse secondary | Fixed-width panes | Resizable divider |
 * | Panel | Bottom drawer | Collapsible panel | Fixed sidebar |
 * | Actions | Floating FAB cluster | Inline button row | Full toolbar |
 */
export const LAYOUT_PRIMITIVES = {
  split: {
    compact: 'collapse_secondary',
    comfortable: 'fixed_panes',
    spacious: 'resizable_divider',
  } as DensityMap<SplitBehavior>,

  panel: {
    compact: 'bottom_drawer',
    comfortable: 'collapsible_panel',
    spacious: 'fixed_sidebar',
  } as DensityMap<PanelBehavior>,

  actions: {
    compact: 'floating_fab',
    comfortable: 'inline_buttons',
    spacious: 'full_toolbar',
  } as DensityMap<ActionsBehavior>,
} as const;

/**
 * Get the behavior for a layout primitive at a given density.
 *
 * @example
 * const panelBehavior = getPrimitiveBehavior('panel', 'compact');
 * // → 'bottom_drawer'
 */
export function getPrimitiveBehavior<P extends LayoutPrimitiveName>(
  primitive: P,
  density: Density
): (typeof LAYOUT_PRIMITIVES)[P][Density] {
  return LAYOUT_PRIMITIVES[primitive][density];
}

// =============================================================================
// Layout Context - Full context for layout decisions
// =============================================================================

/**
 * Full layout context for components.
 * Extends the existing LayoutContext with additional spec-compliant fields.
 */
export interface FullLayoutContext {
  /** Available width in pixels */
  availableWidth: number;

  /** Available height in pixels */
  availableHeight: number;

  /** Current density based on viewport */
  density: Density;

  /** Nesting depth (affects default sizing) */
  depth: number;

  /** Parent's layout strategy */
  parentLayout: 'flow' | 'grid' | 'masonry' | 'stack';

  /** Is the viewport constrained? */
  isConstrained: boolean;

  /** Convenience: is mobile layout */
  isMobile: boolean;

  /** Convenience: is tablet layout */
  isTablet: boolean;

  /** Convenience: is desktop layout */
  isDesktop: boolean;
}

// =============================================================================
// Composition Operators (for testing)
// =============================================================================

/**
 * Vertical composition operator.
 * Layout[D](A // B) = Layout[D](A) // Layout[D](B)
 *
 * Vertical stacking preserves under projection.
 */
export const VERTICAL_COMPOSITION = '//' as const;

/**
 * Horizontal composition operator.
 * Layout[compact](A >> B) ≠ Layout[compact](A) >> Layout[compact](B)
 *
 * In compact mode, horizontal composition transforms to overlay.
 */
export const HORIZONTAL_COMPOSITION = '>>' as const;

/**
 * Symbolic representation for composition law testing.
 */
export interface CompositionLaw {
  operator: typeof VERTICAL_COMPOSITION | typeof HORIZONTAL_COMPOSITION;
  preservesUnderProjection: boolean;
  compactTransformation?: string;
}

export const COMPOSITION_LAWS: CompositionLaw[] = [
  {
    operator: VERTICAL_COMPOSITION,
    preservesUnderProjection: true,
  },
  {
    operator: HORIZONTAL_COMPOSITION,
    preservesUnderProjection: false,
    compactTransformation: 'MainContent + FloatingAction(Secondary)',
  },
];

// =============================================================================
// Fixed Layout Constants - For floating/fixed overlays
// =============================================================================

/**
 * Z-index layering for fixed elements.
 * The sheaf condition: fixed siblings must not occlude each other unintentionally.
 *
 * Panel (z-30) < Toggle (z-40) < Modal (z-50)
 */
export const Z_INDEX_LAYERS = {
  /** Floating panels (sidebars, bottom panels) */
  panel: 30,
  /** Toggle buttons, FABs */
  toggle: 40,
  /** Modals, dialogs, fullscreen drawers */
  modal: 50,
  /** Toast notifications */
  toast: 60,
} as const;

/**
 * Glass effect styles for floating overlays.
 * 17.5% transparency = 82.5% opacity = 0.825
 */
export const GLASS_EFFECT = {
  /** Standard glass: 82.5% opacity with medium blur */
  standard: {
    background: 'bg-gray-800/[0.825]',
    blur: 'backdrop-blur-md',
  },
  /** Solid glass: 95% opacity with light blur */
  solid: {
    background: 'bg-gray-800/95',
    blur: 'backdrop-blur-sm',
  },
  /** Light glass: 70% opacity with heavy blur */
  light: {
    background: 'bg-gray-800/70',
    blur: 'backdrop-blur-lg',
  },
} as const;

export type GlassVariant = keyof typeof GLASS_EFFECT;

/**
 * Standard heights for collapsible bottom panels.
 */
export const BOTTOM_PANEL_HEIGHTS = {
  /** Collapsed height (header only) */
  collapsed: 48,
  /** Default expanded height */
  expanded: 200,
  /** Maximum expanded height */
  max: 400,
} as const;

/**
 * Standard widths for floating sidebars.
 */
export const SIDEBAR_WIDTHS = {
  /** Compact sidebar for comfortable density */
  compact: 240,
  /** Full sidebar for spacious density */
  full: 280,
} as const;

/**
 * Standard heights for collapsible top panels (e.g., ObserverDrawer).
 */
export const TOP_PANEL_HEIGHTS = {
  /** Collapsed height (summary bar only) */
  collapsed: 40,
  /** Default expanded height */
  expanded: 280,
  /** Maximum expanded height */
  max: 400,
} as const;

// =============================================================================
// Animation Coordination Types (formerly in useDesignPolynomial)
// =============================================================================

/**
 * Animation phase for temporal coherence.
 */
export interface AnimationPhase {
  name: string;
  startTime: number;
  duration: number;
  isPlaying: boolean;
}

/**
 * Animation constraint for drawer coordination.
 */
export interface AnimationConstraint {
  contextId: string;
  duration: number;
  isAnimating: boolean;
}
