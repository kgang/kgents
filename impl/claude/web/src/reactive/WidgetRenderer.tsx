/**
 * WidgetRenderer: Dynamic widget renderer for JSON projections.
 *
 * This component is a thin dispatcher that routes JSON widget data to
 * the appropriate React components. All rendering logic lives in the
 * dedicated widget components in `/widgets/`.
 *
 * @example
 * ```tsx
 * <WidgetRenderer
 *   widget={citizenCardJson}
 *   onSelect={(id) => setSelected(id)}
 * />
 * ```
 */

import { memo, useCallback } from 'react';
import type {
  WidgetJSON,
  GlyphJSON,
  BarJSON,
  SparklineJSON,
  CitizenCardJSON,
  HStackJSON,
  VStackJSON,
  ColonyDashboardJSON,
} from './types';

// Import widget components from /widgets/
import {
  Glyph,
  Bar,
  Sparkline,
  CitizenCard,
  HStack,
  VStack,
  ColonyDashboard,
  WidgetProvider,
} from '@/widgets';

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
      return (
        <CitizenCard
          {...widget}
          onSelect={onSelect}
          isSelected={widget.citizen_id === selectedId}
          className={className}
        />
      );

    case 'hstack':
      return (
        <HStack
          {...widget}
          onSelect={onSelect}
          selectedId={selectedId}
          className={className}
        />
      );

    case 'vstack':
      return (
        <VStack
          {...widget}
          onSelect={onSelect}
          selectedId={selectedId}
          className={className}
        />
      );

    case 'colony_dashboard':
      return (
        <ColonyDashboard
          {...widget}
          onSelectCitizen={onSelect}
          className={className}
        />
      );

    default: {
      // Type-safe exhaustiveness check
      const exhaustiveCheck: never = widget;
      return <div className="text-red-500">Unknown widget type: {(exhaustiveCheck as { type: string }).type}</div>;
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
 */
export const WidgetRenderer = memo(function WidgetRenderer({
  widget,
  onSelect,
  selectedId,
  className,
}: WidgetRendererProps) {
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
    <WidgetProvider renderWidget={renderWidget}>
      <InnerRenderer
        widget={widget}
        onSelect={onSelect}
        selectedId={selectedId}
        className={className}
      />
    </WidgetProvider>
  );
});

// Re-export components for backwards compatibility
export { Glyph, Bar, Sparkline, CitizenCard, HStack, VStack, ColonyDashboard };

export default WidgetRenderer;
