/**
 * Reactive Widget Bridge
 *
 * This module bridges the Python reactive substrate to React:
 * - Types: Widget JSON projection types matching Python `_to_json()` output
 * - Hooks: State management for widget projections
 * - Renderer: Dynamic widget rendering from JSON
 * - Context: Theme and interaction management
 *
 * @example
 * ```tsx
 * import {
 *   WidgetRenderer,
 *   useWidgetStream,
 *   WidgetProvider,
 *   type CitizenCardJSON,
 * } from '@/reactive';
 *
 * function TownView({ townId }: { townId: string }) {
 *   const { state, isConnected } = useWidgetStream<ColonyDashboardJSON>({
 *     url: `/v1/town/${townId}/live`,
 *     initialState: emptyDashboard,
 *     autoConnect: true,
 *   });
 *
 *   return (
 *     <WidgetProvider>
 *       <WidgetRenderer widget={state} />
 *     </WidgetProvider>
 *   );
 * }
 * ```
 */

// Types
export type {
  // Primitives
  Phase,
  Animation,
  VisualDistortion,
  GlyphJSON,
  Orientation,
  BarStyle,
  BarJSON,
  SparklineJSON,
  // Citizen
  CitizenPhase,
  NPhase,
  CitizenEigenvectors,
  CitizenCardJSON,
  // Composition
  HStackJSON,
  VStackJSON,
  // Dashboard
  TownPhase,
  ColonyMetrics,
  ColonyDashboardJSON,
  // Union
  WidgetJSON,
  WidgetType,
} from './types';

export { isWidgetJSON } from './types';

// Hooks
export type {
  UseWidgetStateOptions,
  UseWidgetStateResult,
  UseWidgetStreamOptions,
  UseWidgetStreamResult,
} from './useWidgetState';

export { useWidgetState, useWidgetStream } from './useWidgetState';

// Renderer
// Note: CitizenCardProps, ColonyDashboardProps removed 2025-12-23 (unused)
export type {
  WidgetRendererProps,
  GlyphProps,
  BarProps,
  SparklineProps,
  HStackProps,
  VStackProps,
} from './WidgetRenderer';

// Note: CitizenCard, ColonyDashboard removed 2025-12-23 (unused)
export { WidgetRenderer, Glyph, Bar, Sparkline, HStack, VStack } from './WidgetRenderer';

// Context
export type { WidgetTheme, WidgetContextValue, WidgetProviderProps } from './context';

export {
  defaultTheme,
  darkTheme,
  WidgetProvider,
  WidgetContext,
  useWidgetContext,
  useWidgetTheme,
  themeToCSS,
} from './context';
