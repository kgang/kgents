/**
 * SeasonIndicator: Visual representation of garden season.
 *
 * Seasons describe the garden's relationship to change:
 * - DORMANT: Resting, low entropy, stable
 * - SPROUTING: New ideas emerging, high plasticity
 * - BLOOMING: Ideas crystallizing, high visibility
 * - HARVEST: Time to gather and consolidate
 * - COMPOSTING: Breaking down old patterns
 */

import type { GardenSeason } from '@/reactive/types';

interface SeasonIndicatorProps {
  season: GardenSeason;
  plasticity: number;
  entropyMultiplier: number;
  seasonSince?: string;
  className?: string;
}

/** Season visual configuration */
const SEASON_CONFIG: Record<
  GardenSeason,
  { emoji: string; color: string; bgColor: string; description: string }
> = {
  DORMANT: {
    emoji: '💤',
    color: 'text-gray-400',
    bgColor: 'bg-gray-800',
    description: 'Garden is resting',
  },
  SPROUTING: {
    emoji: '🌱',
    color: 'text-green-400',
    bgColor: 'bg-green-900/30',
    description: 'New ideas emerging',
  },
  BLOOMING: {
    emoji: '🌸',
    color: 'text-pink-400',
    bgColor: 'bg-pink-900/30',
    description: 'Ideas crystallizing',
  },
  HARVEST: {
    emoji: '🌾',
    color: 'text-amber-400',
    bgColor: 'bg-amber-900/30',
    description: 'Time to gather',
  },
  COMPOSTING: {
    emoji: '🍂',
    color: 'text-orange-400',
    bgColor: 'bg-orange-900/30',
    description: 'Breaking down patterns',
  },
};

export function SeasonIndicator({
  season,
  plasticity,
  entropyMultiplier,
  seasonSince,
  className = '',
}: SeasonIndicatorProps) {
  const config = SEASON_CONFIG[season];

  // Format time since season started
  const timeSince = seasonSince ? formatTimeSince(seasonSince) : null;

  return (
    <div className={`rounded-lg p-4 ${config.bgColor} ${className}`}>
      {/* Header */}
      <div className="flex items-center gap-3 mb-3">
        <span className="text-3xl">{config.emoji}</span>
        <div>
          <h3 className={`font-semibold ${config.color}`}>{season}</h3>
          <p className="text-xs text-gray-400">{config.description}</p>
        </div>
      </div>

      {/* Metrics */}
      <div className="space-y-2">
        {/* Plasticity bar */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span className="text-gray-400">Plasticity</span>
            <span className={config.color}>{(plasticity * 100).toFixed(0)}%</span>
          </div>
          <div className="h-1.5 bg-gray-700 rounded-full overflow-hidden">
            <div
              className={`h-full ${getPlasticityColor(plasticity)} transition-all duration-500`}
              style={{ width: `${plasticity * 100}%` }}
            />
          </div>
        </div>

        {/* Entropy multiplier */}
        <div className="flex justify-between text-xs">
          <span className="text-gray-400">Entropy Cost</span>
          <span className={config.color}>{entropyMultiplier.toFixed(1)}x</span>
        </div>

        {/* Time in season */}
        {timeSince && (
          <div className="flex justify-between text-xs pt-1 border-t border-gray-700/50">
            <span className="text-gray-500">In season</span>
            <span className="text-gray-400">{timeSince}</span>
          </div>
        )}
      </div>
    </div>
  );
}

/** Compact season badge for headers */
export function SeasonBadge({
  season,
  className = '',
}: {
  season: GardenSeason;
  className?: string;
}) {
  const config = SEASON_CONFIG[season];

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2 py-1 rounded-full text-xs font-medium ${config.bgColor} ${config.color} ${className}`}
    >
      <span>{config.emoji}</span>
      <span>{season}</span>
    </span>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getPlasticityColor(plasticity: number): string {
  if (plasticity >= 0.7) return 'bg-green-500';
  if (plasticity >= 0.4) return 'bg-yellow-500';
  return 'bg-gray-500';
}

function formatTimeSince(isoDate: string): string {
  const date = new Date(isoDate);
  const now = new Date();
  const diff = now.getTime() - date.getTime();

  const hours = Math.floor(diff / (1000 * 60 * 60));
  const days = Math.floor(hours / 24);

  if (days > 0) return `${days}d ${hours % 24}h`;
  if (hours > 0) return `${hours}h`;
  const minutes = Math.floor(diff / (1000 * 60));
  return `${minutes}m`;
}

export default SeasonIndicator;
