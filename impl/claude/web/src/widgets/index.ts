/**
 * Widget components for the reactive widget system.
 *
 * This module exports all widget components organized by category:
 * - primitives: Atomic visual units (Glyph, Bar, Sparkline)
 * - layout: Composition containers (HStack, VStack)
 * - cards: Entity visualizations (CitizenCard, EigenvectorDisplay)
 * - dashboards: Composite views (ColonyDashboard)
 */

// Constants
export { PHASE_GLYPHS, NPHASE_COLORS, SPARK_CHARS } from './constants';

// Context (for layout components)
export { WidgetProvider, useWidgetRender, useWidgetRenderOptional } from './context';
export type { WidgetRenderFunc, WidgetProviderProps } from './context';

// Primitives
export { Glyph, Bar, Sparkline } from './primitives';
export type { GlyphProps, BarProps, SparklineProps } from './primitives';

// Layout
export { HStack, VStack } from './layout';
export type { HStackProps, VStackProps } from './layout';

// Cards
export { CitizenCard, EigenvectorDisplay } from './cards';
export type { CitizenCardProps, EigenvectorDisplayProps } from './cards';

// Dashboards
export { ColonyDashboard } from './dashboards';
export type { ColonyDashboardProps } from './dashboards';
