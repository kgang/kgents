/**
 * CitizenCard: Agent town citizen visualization card.
 *
 * Displays citizen state including:
 * - Name and archetype
 * - Phase glyph and N-phase indicator
 * - Activity sparkline
 * - Capability bar
 * - Mood text
 *
 * Now with elastic layout support - collapses gracefully in constrained viewports.
 * @see plans/web-refactor/elastic-primitives.md
 */

import { memo, useMemo } from 'react';
import type { CitizenCardJSON } from '@/reactive/types';
import { useLayoutContext } from '@/hooks/useLayoutContext';
import { PHASE_GLYPHS, NPHASE_COLORS, SPARK_CHARS } from '../constants';

export interface CitizenCardProps extends Omit<CitizenCardJSON, 'type'> {
  onSelect?: (id: string) => void;
  isSelected?: boolean;
  className?: string;
}

/** Content level for responsive rendering */
type ContentLevel = 'icon' | 'title' | 'summary' | 'full';

/**
 * Determine content level based on available width
 */
function determineContentLevel(width: number, isConstrained: boolean): ContentLevel {
  if (width < 80 || isConstrained) return 'icon';
  if (width < 160) return 'title';
  if (width < 240) return 'summary';
  return 'full';
}

export const CitizenCard = memo(function CitizenCard({
  citizen_id,
  name,
  archetype,
  phase,
  nphase,
  activity,
  capability,
  mood,
  layout,
  onSelect,
  isSelected,
  className,
}: CitizenCardProps) {
  const layoutContext = useLayoutContext();
  const glyph = PHASE_GLYPHS[phase] || '?';
  const nphaseColor = NPHASE_COLORS[nphase] || 'text-gray-500';

  // Determine content level from layout context
  const contentLevel = useMemo(() => {
    // Use layout hint's collapseAt if specified
    const collapseWidth = layout?.collapseAt ?? 200;
    const isConstrained = layoutContext.isConstrained || layoutContext.availableWidth < collapseWidth;
    return determineContentLevel(layoutContext.availableWidth, isConstrained);
  }, [layoutContext.availableWidth, layoutContext.isConstrained, layout?.collapseAt]);

  // Activity sparkline
  const activityChars = useMemo(() => {
    return activity.slice(-10).map((v) => {
      const idx = Math.min(Math.floor(v * 8), 8);
      return SPARK_CHARS[idx];
    });
  }, [activity]);

  // Capability bar
  const capWidth = 10;
  const capFilled = Math.round(capability * capWidth);

  // Priority for hiding (from layout hints)
  const priority = layout?.priority ?? 5;

  // Should hide low-priority cards in very constrained space
  if (layout?.collapsible && contentLevel === 'icon' && priority < 3) {
    return null;
  }

  // Base card classes
  const baseClasses = `
    kgents-citizen-card rounded-lg border transition-all cursor-pointer
    ${isSelected ? 'border-blue-500 bg-blue-50 ring-2 ring-blue-500/30' : 'border-gray-200 bg-white hover:border-gray-300'}
    ${className || ''}
  `.trim();

  // Icon-only view (very constrained)
  if (contentLevel === 'icon') {
    return (
      <div
        data-testid="citizen-card"
        data-citizen-id={citizen_id}
        data-content-level="icon"
        className={`${baseClasses} p-2 flex items-center justify-center`}
        onClick={() => onSelect?.(citizen_id)}
        title={`${name} - ${archetype}`}
      >
        <span className="text-xl">{glyph}</span>
      </div>
    );
  }

  // Title view (constrained)
  if (contentLevel === 'title') {
    return (
      <div
        data-testid="citizen-card"
        data-citizen-id={citizen_id}
        data-content-level="title"
        className={`${baseClasses} p-2`}
        onClick={() => onSelect?.(citizen_id)}
      >
        <div className="flex items-center gap-2">
          <span className="text-lg">{glyph}</span>
          <span className="font-bold text-gray-900 truncate">{name}</span>
          <span className={`text-xs ${nphaseColor}`}>[{nphase[0]}]</span>
        </div>
      </div>
    );
  }

  // Summary view (moderate space)
  if (contentLevel === 'summary') {
    return (
      <div
        data-testid="citizen-card"
        data-citizen-id={citizen_id}
        data-content-level="summary"
        className={`${baseClasses} p-3`}
        onClick={() => onSelect?.(citizen_id)}
      >
        <div className="flex items-center gap-2 mb-1">
          <span className="text-xl">{glyph}</span>
          <span className="font-bold text-gray-900">{name}</span>
          <span className={`text-sm ${nphaseColor}`}>[{nphase[0]}]</span>
        </div>
        <div className="text-cyan-600 text-sm truncate">{archetype}</div>
        {activity.length > 0 && (
          <div className="font-mono text-green-600 text-xs mt-1">{activityChars.join('')}</div>
        )}
      </div>
    );
  }

  // Full view (plenty of space)
  return (
    <div
      data-testid="citizen-card"
      data-citizen-id={citizen_id}
      data-content-level="full"
      className={`${baseClasses} p-3`}
      onClick={() => onSelect?.(citizen_id)}
    >
      {/* Header */}
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xl">{glyph}</span>
        <span className="font-bold text-gray-900">{name}</span>
        <span className={`text-sm ${nphaseColor}`}>[{nphase[0]}]</span>
      </div>

      {/* Archetype */}
      <div className="text-cyan-600 text-sm mb-2">{archetype}</div>

      {/* Activity */}
      {activity.length > 0 && (
        <div className="font-mono text-green-600 text-sm mb-1">{activityChars.join('')}</div>
      )}

      {/* Capability */}
      <div className="font-mono text-sm text-yellow-600">
        cap: {'█'.repeat(capFilled)}
        {'░'.repeat(capWidth - capFilled)}
      </div>

      {/* Mood */}
      <div className="text-gray-500 text-xs mt-2">{mood}</div>
    </div>
  );
});

export default CitizenCard;
