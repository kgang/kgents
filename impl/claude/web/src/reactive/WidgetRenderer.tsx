/**
 * WidgetRenderer: Dynamic widget renderer for JSON projections.
 *
 * This component is a thin dispatcher that routes JSON widget data to
 * the appropriate React components. All rendering logic lives in the
 * dedicated widget components in `/widgets/`.
 *
 * Extended with LayoutContext support for elastic rendering.
 * @see plans/web-refactor/elastic-primitives.md
 *
 * @example
 * ```tsx
 * <WidgetRenderer
 *   widget={citizenCardJson}
 *   onSelect={(id) => setSelected(id)}
 * />
 * ```
 */

import React, { memo, useCallback } from 'react';
import type {
  WidgetJSON,
  LayoutContext,
  GlyphJSON,
  BarJSON,
  SparklineJSON,
  CitizenCardJSON,
  HStackJSON,
  VStackJSON,
  ColonyDashboardJSON,
} from './types';
import { useLayoutMeasure } from '@/hooks/useLayoutContext';
import { LayoutContextProvider } from '@/components/elastic';

// Import widget components from /widgets/
// Note: CitizenCard, ColonyDashboard removed 2025-12-23 (unused)
import { Glyph, Bar, Sparkline, HStack, VStack, WidgetProvider } from '@/widgets';

// Re-export constants for backwards compatibility
export { PHASE_GLYPHS, NPHASE_COLORS, SPARK_CHARS } from '@/widgets';

// =============================================================================
// Props Types (re-exported for backwards compatibility)
// =============================================================================

export interface WidgetRendererProps {
  widget: WidgetJSON;
  onSelect?: (id: string) => void;
  selectedId?: string | null;
  className?: string;
  /** Layout context from parent (auto-measured if not provided) */
  layoutContext?: LayoutContext;
}

export interface GlyphProps extends Omit<GlyphJSON, 'type'> {
  className?: string;
}

export interface BarProps extends Omit<BarJSON, 'type' | 'glyphs'> {
  className?: string;
}

export interface SparklineProps extends Omit<SparklineJSON, 'type' | 'glyphs'> {
  className?: string;
}

export interface CitizenCardProps extends Omit<CitizenCardJSON, 'type'> {
  onSelect?: (id: string) => void;
  isSelected?: boolean;
  className?: string;
}

export interface HStackProps extends Omit<HStackJSON, 'type'> {
  onSelect?: (id: string) => void;
  selectedId?: string | null;
  className?: string;
}

export interface VStackProps extends Omit<VStackJSON, 'type'> {
  onSelect?: (id: string) => void;
  selectedId?: string | null;
  className?: string;
}

export interface ColonyDashboardProps extends Omit<ColonyDashboardJSON, 'type'> {
  onSelectCitizen?: (id: string) => void;
  className?: string;
}

// =============================================================================
// Inner Renderer (without provider)
// =============================================================================

interface InnerRendererProps {
  widget: WidgetJSON;
  onSelect?: (id: string) => void;
  selectedId?: string | null;
  className?: string;
}

const InnerRenderer = memo(function InnerRenderer({
  widget,
  onSelect,
  selectedId,
  className,
}: InnerRendererProps) {
  switch (widget.type) {
    case 'glyph':
      return <Glyph {...widget} className={className} />;

    case 'bar':
      return <Bar {...widget} className={className} />;

    case 'sparkline':
      return <Sparkline {...widget} className={className} />;

    case 'citizen_card':
      // CitizenCard removed 2025-12-23
      return <div className="text-amber-500">CitizenCard widget deprecated</div>;

    case 'hstack':
      return (
        <HStack {...widget} onSelect={onSelect} selectedId={selectedId} className={className} />
      );

    case 'vstack':
      return (
        <VStack {...widget} onSelect={onSelect} selectedId={selectedId} className={className} />
      );

    case 'colony_dashboard':
      // ColonyDashboard removed 2025-12-23
      return <div className="text-amber-500">ColonyDashboard widget deprecated</div>;

    default: {
      // Type-safe exhaustiveness check
      const exhaustiveCheck: never = widget;
      return (
        <div className="text-red-500">
          Unknown widget type: {(exhaustiveCheck as { type: string }).type}
        </div>
      );
    }
  }
});

// =============================================================================
// Main WidgetRenderer
// =============================================================================

/**
 * Dynamic widget renderer that dispatches on widget.type.
 *
 * Supports all widget types from the reactive substrate:
 * - glyph, bar, sparkline (primitives)
 * - citizen_card (agent card)
 * - hstack, vstack (composition)
 * - colony_dashboard (composite)
 *
 * Now with LayoutContext support for elastic rendering.
 */
export const WidgetRenderer = memo(function WidgetRenderer({
  widget,
  onSelect,
  selectedId,
  className,
  layoutContext,
}: WidgetRendererProps) {
  // Measure container if no context provided
  const [containerRef, measuredContext] = useLayoutMeasure({
    parentLayout: 'stack',
  });

  // Use provided context or measured context
  const effectiveContext = layoutContext ?? measuredContext;

  // Create render function for nested widgets
  const renderWidget = useCallback(
    (props: {
      widget: WidgetJSON;
      onSelect?: (id: string) => void;
      selectedId?: string | null;
      className?: string;
    }) => <InnerRenderer {...props} />,
    []
  );

  return (
    <div ref={containerRef as React.RefObject<HTMLDivElement>} className="widget-renderer-root">
      <LayoutContextProvider value={effectiveContext}>
        <WidgetProvider renderWidget={renderWidget}>
          <InnerRenderer
            widget={widget}
            onSelect={onSelect}
            selectedId={selectedId}
            className={className}
          />
        </WidgetProvider>
      </LayoutContextProvider>
    </div>
  );
});

// Re-export components for backwards compatibility
// Note: CitizenCard, ColonyDashboard removed 2025-12-23
export { Glyph, Bar, Sparkline, HStack, VStack };

export default WidgetRenderer;
