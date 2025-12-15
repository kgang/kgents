/**
 * TypeScript types for reactive widget JSON projections.
 *
 * These types mirror the Python widget `_to_json()` output exactly.
 * Generated from: impl/claude/agents/i/reactive/primitives/
 *
 * The widget type discriminator pattern enables type-safe rendering:
 *   switch (widget.type) { case 'citizen_card': ... }
 */

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
}

// =============================================================================
// Citizen Card
// =============================================================================

export type CitizenPhase = 'IDLE' | 'SOCIALIZING' | 'WORKING' | 'REFLECTING' | 'RESTING';
export type NPhase = 'SENSE' | 'ACT' | 'REFLECT';

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
}

// =============================================================================
// Composition Containers
// =============================================================================

export interface HStackJSON {
  type: 'hstack';
  gap: number;
  separator: string | null;
  children: WidgetJSON[];
}

export interface VStackJSON {
  type: 'vstack';
  gap: number;
  separator: string | null;
  children: WidgetJSON[];
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
    ['glyph', 'bar', 'sparkline', 'citizen_card', 'hstack', 'vstack', 'colony_dashboard'].includes(
      obj.type
    )
  );
}
