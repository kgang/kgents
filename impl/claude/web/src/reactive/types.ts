/**
 * TypeScript types for reactive widget JSON projections.
 *
 * These types mirror the Python widget `_to_json()` output exactly.
 * Generated from: impl/claude/agents/i/reactive/primitives/
 *
 * The widget type discriminator pattern enables type-safe rendering:
 *   switch (widget.type) { case 'citizen_card': ... }
 *
 * Extended with layout hints for elastic UI system.
 * @see plans/web-refactor/elastic-primitives.md
 */

// =============================================================================
// Layout Hints (Elastic System)
// =============================================================================

/**
 * Layout hints that widgets can provide for elastic rendering.
 * These hints guide the ElasticContainer on how to arrange widgets.
 */
export interface WidgetLayoutHints {
  /** Flex grow factor (how eagerly to take space) */
  flex?: number;

  /** Minimum width before collapsing (px) */
  minWidth?: number;

  /** Maximum comfortable width (px) */
  maxWidth?: number;

  /** Render priority (higher = survives truncation) */
  priority?: number;

  /** Preferred aspect ratio (width/height) */
  aspectRatio?: number;

  /** Can this widget be hidden to save space? */
  collapsible?: boolean;

  /** Viewport width threshold for collapse (px) */
  collapseAt?: number;
}

/**
 * Layout context passed to widgets by container.
 * Widgets can adapt their rendering based on available space.
 */
export interface LayoutContext {
  /** Available width in pixels */
  availableWidth: number;

  /** Available height in pixels */
  availableHeight: number;

  /** Nesting depth (affects default sizing) */
  depth: number;

  /** Parent's layout strategy */
  parentLayout: 'flow' | 'grid' | 'masonry' | 'stack';

  /** Is the viewport constrained? */
  isConstrained: boolean;

  /** Preferred density */
  density: 'compact' | 'comfortable' | 'spacious';
}

// =============================================================================
// Glyph
// =============================================================================

export type Phase = 'idle' | 'active' | 'waiting' | 'error' | 'yielding' | 'thinking' | 'complete';
export type Animation = 'none' | 'pulse' | 'blink' | 'breathe' | 'wiggle';

export interface VisualDistortion {
  blur: number;
  skew: number;
  jitter_x: number;
  jitter_y: number;
  pulse: number;
}

export interface GlyphJSON {
  type: 'glyph';
  char: string;
  phase: Phase | null;
  entropy: number;
  animate: Animation;
  fg?: string;
  bg?: string;
  distortion?: VisualDistortion;
  /** Layout hints for elastic rendering */
  layout?: WidgetLayoutHints;
}

// =============================================================================
// Bar
// =============================================================================

export type Orientation = 'horizontal' | 'vertical';
export type BarStyle = 'solid' | 'gradient' | 'segments' | 'dots';

export interface BarJSON {
  type: 'bar';
  value: number;
  width: number;
  orientation: Orientation;
  style: BarStyle;
  entropy: number;
  glyphs: GlyphJSON[];
  label?: string;
  fg?: string;
  bg?: string;
  distortion?: VisualDistortion;
  /** Layout hints for elastic rendering */
  layout?: WidgetLayoutHints;
}

// =============================================================================
// Sparkline
// =============================================================================

export interface SparklineJSON {
  type: 'sparkline';
  values: number[];
  max_length: number;
  entropy: number;
  glyphs: GlyphJSON[];
  min?: number;
  max?: number;
  current?: number;
  label?: string;
  fg?: string;
  bg?: string;
  distortion?: VisualDistortion;
  /** Layout hints for elastic rendering */
  layout?: WidgetLayoutHints;
}

// =============================================================================
// Citizen Card
// =============================================================================

export type CitizenPhase = 'IDLE' | 'SOCIALIZING' | 'WORKING' | 'REFLECTING' | 'RESTING';
// UNDERSTAND is the primary name in backend (SENSE is alias for backwards compat)
export type NPhase = 'UNDERSTAND' | 'SENSE' | 'ACT' | 'REFLECT';

export interface CitizenEigenvectors {
  warmth: number;
  curiosity: number;
  trust: number;
}

export interface CitizenCardJSON {
  type: 'citizen_card';
  citizen_id: string;
  name: string;
  archetype: string;
  phase: CitizenPhase;
  nphase: NPhase;
  activity: number[];
  capability: number;
  entropy: number;
  region: string;
  mood: string;
  eigenvectors: CitizenEigenvectors;
  /** Layout hints for elastic rendering */
  layout?: WidgetLayoutHints;
}

// =============================================================================
// Composition Containers
// =============================================================================

export interface HStackJSON {
  type: 'hstack';
  gap: number;
  separator: string | null;
  children: WidgetJSON[];
  /** Layout hints for elastic rendering */
  layout?: WidgetLayoutHints;
}

export interface VStackJSON {
  type: 'vstack';
  gap: number;
  separator: string | null;
  children: WidgetJSON[];
  /** Layout hints for elastic rendering */
  layout?: WidgetLayoutHints;
}

// =============================================================================
// Colony Dashboard (composite)
// =============================================================================

export type TownPhase = 'MORNING' | 'AFTERNOON' | 'EVENING' | 'NIGHT';

export interface ColonyMetrics {
  total_events: number;
  total_tokens: number;
  entropy_budget: number;
}

export interface ColonyDashboardJSON {
  type: 'colony_dashboard';
  colony_id: string;
  phase: TownPhase;
  day: number;
  metrics: ColonyMetrics;
  citizens: CitizenCardJSON[];
  grid_cols: number;
  selected_citizen_id: string | null;
  /** Layout hints for elastic rendering */
  layout?: WidgetLayoutHints;
}

// =============================================================================
// Union Type
// =============================================================================

// =============================================================================
// Concept Nursery
// =============================================================================

/** Growth stages for concepts in the nursery */
export type ConceptStage = 'SEED' | 'SPROUTING' | 'GROWING' | 'READY' | 'PROMOTED';

/** A concept seed growing in the nursery */
export interface ConceptSeedJSON {
  handle: string;
  stage: ConceptStage;
  usage_count: number;
  success_count: number;
  success_rate: number;
  created_at: string;
  last_invoked: string;
  /** CSS glow intensity (0-1) for visual feedback */
  glow_intensity: number;
  /** Whether this stage should have breathing animation */
  should_pulse: boolean;
  /** Lucide icon name for this stage */
  icon: string;
}

/** Nursery state containing all seeds */
export interface NurseryJSON {
  seeds: Record<string, ConceptSeedJSON>;
  counts: {
    total: number;
    seeds: number;
    sprouting: number;
    growing: number;
    ready: number;
    promoted: number;
  };
}

// =============================================================================
// Union Type
// =============================================================================

/**
 * Discriminated union of all widget JSON types.
 *
 * Use the `type` field to narrow:
 *   if (widget.type === 'citizen_card') {
 *     // TypeScript knows widget is CitizenCardJSON
 *   }
 */
export type WidgetJSON =
  | GlyphJSON
  | BarJSON
  | SparklineJSON
  | CitizenCardJSON
  | HStackJSON
  | VStackJSON
  | ColonyDashboardJSON;

/**
 * Extract the type literal from a WidgetJSON.
 */
export type WidgetType = WidgetJSON['type'];

/**
 * Type guard to check if a value is a valid WidgetJSON.
 */
export function isWidgetJSON(value: unknown): value is WidgetJSON {
  if (typeof value !== 'object' || value === null) return false;
  const obj = value as Record<string, unknown>;
  return (
    typeof obj.type === 'string' &&
    [
      'glyph',
      'bar',
      'sparkline',
      'citizen_card',
      'hstack',
      'vstack',
      'colony_dashboard',
    ].includes(obj.type)
  );
}
