/**
 * SeasonOrb - Breathing Season Indicator
 *
 * A breathing orb that pulses with the garden's rhythm.
 * Uses Living Earth palette for season colors.
 *
 * @see spec/protocols/2d-renaissance.md - Section 3.4A
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { Breathe } from '@/components/joy';
import { getSeasonIcon } from '@/constants';
import type { GardenSeason } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface SeasonOrbProps {
  /** Current garden season */
  season: GardenSeason;
  /** Season plasticity (0-1) */
  plasticity: number;
  /** Entropy cost multiplier */
  entropyMultiplier: number;
  /** ISO timestamp when season started */
  seasonSince?: string;
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Living Earth Season Colors
// =============================================================================

/**
 * Season colors from Living Earth palette
 * Per spec: "Resting roots" to "Returning"
 */
const SEASON_COLORS: Record<
  GardenSeason,
  {
    orb: string;
    accent: string;
    bg: string;
    text: string;
    metaphor: string;
  }
> = {
  DORMANT: {
    orb: '#6B4E3D', // Wood
    accent: '#4A3728', // Bark
    bg: '#4A3728', // Bark
    text: '#AB9080', // Sand
    metaphor: 'Resting roots',
  },
  SPROUTING: {
    orb: '#4A6B4A', // Sage
    accent: '#8BAB8B', // Sprout
    bg: '#1A2E1A', // Moss
    text: '#8BAB8B', // Sprout
    metaphor: 'New growth',
  },
  BLOOMING: {
    orb: '#D4A574', // Amber
    accent: '#C08552', // Copper
    bg: '#8B5A2B', // Bronze (darker for bg)
    text: '#F5E6D3', // Lantern
    metaphor: 'Full flower',
  },
  HARVEST: {
    orb: '#E8C4A0', // Honey
    accent: '#8B5A2B', // Bronze
    bg: '#6B4E3D', // Wood
    text: '#F5E6D3', // Lantern
    metaphor: 'Gathering',
  },
  COMPOSTING: {
    orb: '#2E4A2E', // Fern
    accent: '#1A2E1A', // Moss
    bg: '#0F1A0F', // Deep moss
    text: '#6B8B6B', // Mint
    metaphor: 'Returning',
  },
};

// =============================================================================
// Main Component
// =============================================================================

export function SeasonOrb({
  season,
  plasticity,
  entropyMultiplier,
  seasonSince,
  compact = false,
  className = '',
}: SeasonOrbProps) {
  const colors = SEASON_COLORS[season];
  const SeasonIcon = getSeasonIcon(season);
  const timeSince = seasonSince ? formatTimeSince(seasonSince) : null;

  return (
    <div
      className={`rounded-xl p-4 ${compact ? 'p-3' : 'p-4'} ${className}`}
      style={{ backgroundColor: `${colors.bg}40` }} // 40 = 25% opacity
    >
      {/* Orb + Season Name */}
      <div className="flex items-center gap-4 mb-4">
        {/* Breathing Orb */}
        <Breathe intensity={0.4} speed="slow">
          <div
            className={`rounded-full flex items-center justify-center ${
              compact ? 'w-12 h-12' : 'w-16 h-16'
            }`}
            style={{
              backgroundColor: colors.orb,
              boxShadow: `0 0 20px ${colors.orb}60`,
            }}
          >
            <SeasonIcon
              className={`${compact ? 'w-6 h-6' : 'w-8 h-8'}`}
              style={{ color: colors.text }}
            />
          </div>
        </Breathe>

        {/* Season Info */}
        <div>
          <h3
            className={`font-semibold ${compact ? 'text-base' : 'text-lg'}`}
            style={{ color: colors.text }}
          >
            {season}
          </h3>
          <p className={`${compact ? 'text-[10px]' : 'text-xs'}`} style={{ color: colors.accent }}>
            {colors.metaphor}
          </p>
        </div>
      </div>

      {/* Metrics */}
      <div className="space-y-3">
        {/* Plasticity Bar */}
        <div>
          <div className="flex justify-between text-xs mb-1">
            <span style={{ color: colors.accent }}>Plasticity</span>
            <span style={{ color: colors.text }}>{(plasticity * 100).toFixed(0)}%</span>
          </div>
          <div
            className="h-2 rounded-full overflow-hidden"
            style={{ backgroundColor: `${colors.bg}80` }}
          >
            <div
              className="h-full transition-all duration-500 rounded-full"
              style={{
                width: `${plasticity * 100}%`,
                backgroundColor: getPlasticityColor(plasticity),
              }}
            />
          </div>
          <p
            className={`text-[10px] mt-1 ${compact ? 'hidden' : ''}`}
            style={{ color: colors.accent }}
          >
            {plasticity >= 0.7
              ? 'Bold changes welcome'
              : plasticity >= 0.4
                ? 'Moderate flexibility'
                : 'Preserve what exists'}
          </p>
        </div>

        {/* Entropy Cost */}
        <div className="flex justify-between text-xs">
          <span style={{ color: colors.accent }}>Entropy Cost</span>
          <span style={{ color: colors.text }}>{entropyMultiplier.toFixed(1)}x</span>
        </div>

        {/* Time in Season */}
        {timeSince && (
          <div
            className={`flex justify-between text-xs pt-2 border-t ${compact ? 'pt-1' : 'pt-2'}`}
            style={{ borderColor: `${colors.accent}40` }}
          >
            <span style={{ color: colors.accent }}>In season</span>
            <span style={{ color: colors.text }}>{timeSince}</span>
          </div>
        )}
      </div>
    </div>
  );
}

/**
 * Compact Season Badge (for headers)
 */
export function SeasonBadge2D({
  season,
  className = '',
}: {
  season: GardenSeason;
  className?: string;
}) {
  const colors = SEASON_COLORS[season];
  const SeasonIcon = getSeasonIcon(season);

  return (
    <span
      className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${className}`}
      style={{
        backgroundColor: `${colors.bg}60`,
        color: colors.text,
      }}
    >
      <SeasonIcon className="w-3.5 h-3.5" />
      <span>{season}</span>
    </span>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getPlasticityColor(plasticity: number): string {
  if (plasticity >= 0.7) return '#4A6B4A'; // Sage - high plasticity
  if (plasticity >= 0.4) return '#D4A574'; // Amber - medium
  return '#6B4E3D'; // Wood - low
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

export default SeasonOrb;
