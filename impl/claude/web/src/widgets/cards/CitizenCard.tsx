/**
 * CitizenCard: Agent town citizen visualization card.
 *
 * Displays citizen state including:
 * - Name and archetype
 * - Phase glyph and N-phase indicator
 * - Activity sparkline
 * - Capability bar
 * - Mood text
 */

import { memo, useMemo } from 'react';
import type { CitizenCardJSON } from '@/reactive/types';
import { PHASE_GLYPHS, NPHASE_COLORS, SPARK_CHARS } from '../constants';

export interface CitizenCardProps extends Omit<CitizenCardJSON, 'type'> {
  onSelect?: (id: string) => void;
  isSelected?: boolean;
  className?: string;
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
  onSelect,
  isSelected,
  className,
}: CitizenCardProps) {
  const glyph = PHASE_GLYPHS[phase] || '?';
  const nphaseColor = NPHASE_COLORS[nphase] || 'text-gray-500';

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

  return (
    <div
      data-testid="citizen-card"
      data-citizen-id={citizen_id}
      className={`
        kgents-citizen-card p-3 rounded-lg border transition-colors cursor-pointer
        ${isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white hover:border-gray-300'}
        ${className || ''}
      `}
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
