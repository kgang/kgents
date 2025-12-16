/**
 * PlotCard: Display for a garden plot (focused region).
 *
 * Plots correspond to:
 * - Plan files (e.g., plans/coalition-forge.md)
 * - Crown jewels (e.g., Atelier, Brain)
 * - Custom focus areas (e.g., "refactoring auth")
 */

import type { PlotJSON, GardenSeason } from '@/reactive/types';
import { SeasonBadge } from './SeasonIndicator';

interface PlotCardProps {
  plot: PlotJSON;
  isActive: boolean;
  gardenSeason: GardenSeason;
  onSelect?: (plotName: string) => void;
}

/** Crown jewel emoji mapping */
const CROWN_JEWEL_EMOJI: Record<string, string> = {
  Atelier: '🎨',
  Coalition: '🤝',
  Brain: '🧠',
  Park: '🎭',
  Domain: '🔬',
  Gestalt: '🏛️',
  Gardener: '🌱',
};

export function PlotCard({ plot, isActive, gardenSeason, onSelect }: PlotCardProps) {
  const effectiveSeason = plot.season_override || gardenSeason;
  const isActiveRecently = isPlotActiveRecently(plot.last_tended);

  // Determine display emoji
  const emoji = plot.crown_jewel ? CROWN_JEWEL_EMOJI[plot.crown_jewel] || '📁' : '📁';

  return (
    <button
      onClick={() => onSelect?.(plot.name)}
      className={`
        w-full text-left p-4 rounded-lg border transition-all
        ${
          isActive
            ? 'border-green-500 bg-green-900/20'
            : 'border-gray-700 bg-gray-800/50 hover:border-gray-600 hover:bg-gray-800'
        }
      `}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-xl">{emoji}</span>
          <div>
            <h4 className="font-medium text-white">{formatPlotName(plot.name)}</h4>
            {plot.crown_jewel && (
              <span className="text-xs text-gray-500">Crown Jewel: {plot.crown_jewel}</span>
            )}
          </div>
        </div>

        {/* Activity indicator */}
        <span
          className={`w-2 h-2 rounded-full ${isActiveRecently ? 'bg-green-500' : 'bg-gray-600'}`}
          title={isActiveRecently ? 'Recently active' : 'Inactive'}
        />
      </div>

      {/* Description */}
      {plot.description && (
        <p className="text-sm text-gray-400 mb-3 line-clamp-2">{plot.description}</p>
      )}

      {/* Progress bar */}
      <div className="mb-3">
        <div className="flex justify-between text-xs mb-1">
          <span className="text-gray-500">Progress</span>
          <span className="text-gray-400">{(plot.progress * 100).toFixed(0)}%</span>
        </div>
        <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
          <div
            className="h-full bg-green-500 transition-all duration-300"
            style={{ width: `${plot.progress * 100}%` }}
          />
        </div>
      </div>

      {/* Footer */}
      <div className="flex items-center justify-between">
        {/* Rigidity indicator */}
        <div className="flex items-center gap-1 text-xs">
          <span className="text-gray-500">Rigidity:</span>
          <RigidityIndicator value={plot.rigidity} />
        </div>

        {/* Season override badge */}
        {plot.season_override && <SeasonBadge season={effectiveSeason} className="text-[10px]" />}
      </div>

      {/* Tags */}
      {plot.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {plot.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="text-[10px] px-1.5 py-0.5 bg-gray-700 rounded text-gray-400">
              {tag}
            </span>
          ))}
          {plot.tags.length > 3 && (
            <span className="text-[10px] text-gray-500">+{plot.tags.length - 3}</span>
          )}
        </div>
      )}
    </button>
  );
}

/** Compact plot list item */
export function PlotListItem({
  plot,
  isActive,
  onSelect,
}: {
  plot: PlotJSON;
  isActive: boolean;
  onSelect?: (plotName: string) => void;
}) {
  const emoji = plot.crown_jewel ? CROWN_JEWEL_EMOJI[plot.crown_jewel] || '📁' : '📁';
  const isActiveRecently = isPlotActiveRecently(plot.last_tended);

  return (
    <button
      onClick={() => onSelect?.(plot.name)}
      className={`
        w-full flex items-center gap-3 px-3 py-2 rounded transition-colors
        ${isActive ? 'bg-green-900/30 text-green-400' : 'hover:bg-gray-800 text-gray-300'}
      `}
    >
      <span>{emoji}</span>
      <span className="flex-1 text-left text-sm truncate">{formatPlotName(plot.name)}</span>
      <span
        className={`w-1.5 h-1.5 rounded-full ${isActiveRecently ? 'bg-green-500' : 'bg-gray-600'}`}
      />
      <span className="text-xs text-gray-500">{(plot.progress * 100).toFixed(0)}%</span>
    </button>
  );
}

// =============================================================================
// Sub-components
// =============================================================================

function RigidityIndicator({ value }: { value: number }) {
  // 5-dot scale for rigidity
  const filled = Math.round(value * 5);

  return (
    <div className="flex gap-0.5" title={`Rigidity: ${(value * 100).toFixed(0)}%`}>
      {[...Array(5)].map((_, i) => (
        <span
          key={i}
          className={`w-1 h-2 rounded-sm ${i < filled ? 'bg-amber-500' : 'bg-gray-600'}`}
        />
      ))}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function formatPlotName(name: string): string {
  return name
    .split('-')
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}

function isPlotActiveRecently(lastTended: string): boolean {
  const date = new Date(lastTended);
  const now = new Date();
  const hoursDiff = (now.getTime() - date.getTime()) / (1000 * 60 * 60);
  return hoursDiff < 24;
}

export default PlotCard;
