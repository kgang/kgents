/**
 * PlotTile - Organic Plot Card with Vine Progress
 *
 * Plot tiles with vine-like progress indicators and Living Earth aesthetic.
 * Replaces PlotCard with a more organic, 2D-first design.
 *
 * @see spec/protocols/2d-renaissance.md - Section 3.4B
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { FolderOpen, type LucideIcon } from 'lucide-react';
import { Breathe } from '@/components/joy';
import { JEWEL_ICONS, JEWEL_COLORS, type JewelName } from '@/constants/jewels';
import type { PlotJSON, GardenSeason } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface PlotTileProps {
  /** Plot data */
  plot: PlotJSON;
  /** Whether this is the active plot */
  isActive: boolean;
  /** Whether this plot is selected */
  isSelected: boolean;
  /** Garden's current season */
  gardenSeason: GardenSeason;
  /** Selection callback */
  onSelect?: (plotName: string) => void;
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Constants
// =============================================================================

/** Map Crown Jewel names to JewelName type */
const JEWEL_NAME_MAP: Record<string, JewelName> = {
  Forge: 'forge',
  Coalition: 'coalition',
  Brain: 'brain',
  Park: 'park',
  Domain: 'domain',
  Gestalt: 'gestalt',
  Gardener: 'gardener',
};

/** Plot state visual styles (Living Earth) */
const PLOT_STATES = {
  ACTIVE: {
    border: '#4A6B4A', // Sage
    bg: '#1A2E1A', // Moss
    glow: '#4A6B4A40', // Sage with opacity
  },
  WAITING: {
    border: '#D4A574', // Amber
    bg: '#4A372840', // Bark faint
    glow: 'none',
  },
  DORMANT: {
    border: '#6B4E3D', // Wood
    bg: '#2D1B1420', // Soil faint
    glow: 'none',
  },
  COMPLETE: {
    border: '#E8C4A0', // Honey
    bg: '#8B5A2B20', // Bronze faint
    glow: '#E8C4A020', // Honey glow
  },
} as const;

// =============================================================================
// Main Component
// =============================================================================

export function PlotTile({
  plot,
  isActive,
  isSelected,
  gardenSeason: _gardenSeason,
  onSelect,
  compact = false,
  className = '',
}: PlotTileProps) {
  const isActiveRecently = isPlotActiveRecently(plot.last_tended);
  const isComplete = plot.progress >= 1.0;
  const { icon: PlotIcon, color: iconColor } = getPlotIcon(plot.crown_jewel);

  // Determine visual state
  const stateKey = isComplete
    ? 'COMPLETE'
    : isActive
      ? 'ACTIVE'
      : isActiveRecently
        ? 'WAITING'
        : 'DORMANT';
  const state = PLOT_STATES[stateKey];

  const content = (
    <button
      onClick={() => onSelect?.(plot.name)}
      className={`
        w-full text-left rounded-lg border-2 transition-all duration-300
        ${compact ? 'p-3' : 'p-4'}
        ${isSelected ? 'ring-2 ring-[#8BAB8B] ring-offset-2 ring-offset-[#2D1B14]' : ''}
        hover:border-[#8BAB8B]
        ${className}
      `}
      style={{
        borderColor: state.border,
        backgroundColor: state.bg,
        boxShadow: state.glow !== 'none' ? `0 0 15px ${state.glow}` : 'none',
      }}
    >
      {/* Header Row */}
      <div className="flex items-start justify-between mb-2">
        <div className="flex items-center gap-2">
          <PlotIcon className={compact ? 'w-4 h-4' : 'w-5 h-5'} style={{ color: iconColor }} />
          <div>
            <h4 className={`font-medium text-[#F5E6D3] ${compact ? 'text-sm' : ''}`}>
              {formatPlotName(plot.name)}
            </h4>
            {plot.crown_jewel && !compact && (
              <span className="text-[10px] text-[#AB9080]">{plot.crown_jewel}</span>
            )}
          </div>
        </div>

        {/* Activity indicator */}
        <div className="flex items-center gap-2">
          {isActive && (
            <span className="text-[10px] px-1.5 py-0.5 rounded bg-[#4A6B4A]/30 text-[#8BAB8B] font-medium">
              ACTIVE
            </span>
          )}
          <span
            className={`w-2 h-2 rounded-full ${isActiveRecently ? 'bg-[#8BAB8B]' : 'bg-[#6B4E3D]'}`}
            title={isActiveRecently ? 'Recently active' : 'Inactive'}
          />
        </div>
      </div>

      {/* Description (desktop only) */}
      {plot.description && !compact && (
        <p className="text-xs text-[#AB9080] mb-3 line-clamp-2">{plot.description}</p>
      )}

      {/* Vine Progress Bar */}
      <VineProgress progress={plot.progress} compact={compact} />

      {/* Tags */}
      {plot.tags.length > 0 && !compact && (
        <div className="flex flex-wrap gap-1 mt-2">
          {plot.tags.slice(0, 3).map((tag) => (
            <span
              key={tag}
              className="text-[10px] px-1.5 py-0.5 rounded bg-[#4A3728] text-[#AB9080]"
            >
              {tag}
            </span>
          ))}
          {plot.tags.length > 3 && (
            <span className="text-[10px] text-[#6B4E3D]">+{plot.tags.length - 3}</span>
          )}
        </div>
      )}
    </button>
  );

  // Wrap active plots in Breathe animation
  if (isActive) {
    return (
      <Breathe intensity={0.2} speed="slow">
        {content}
      </Breathe>
    );
  }

  return content;
}

// =============================================================================
// Vine Progress Component
// =============================================================================

interface VineProgressProps {
  progress: number;
  compact?: boolean;
}

/**
 * Vine-style progress bar with organic growth visualization
 */
function VineProgress({ progress, compact = false }: VineProgressProps) {
  const percentage = Math.round(progress * 100);

  return (
    <div className={compact ? 'mt-2' : 'mt-3'}>
      {/* Progress label */}
      <div className="flex justify-between items-center mb-1">
        <span className={`text-[#6B4E3D] ${compact ? 'text-[10px]' : 'text-xs'}`}>Progress</span>
        <span className={`text-[#8BAB8B] font-medium ${compact ? 'text-[10px]' : 'text-xs'}`}>
          {percentage}%
        </span>
      </div>

      {/* Vine track */}
      <div
        className={`relative ${compact ? 'h-1.5' : 'h-2'} bg-[#1A2E1A] rounded-full overflow-hidden`}
      >
        {/* Filled vine */}
        <div
          className="absolute inset-y-0 left-0 rounded-full transition-all duration-700 ease-out"
          style={{
            width: `${percentage}%`,
            background: getVineGradient(progress),
          }}
        />

        {/* Vine node at current position */}
        {progress > 0.05 && progress < 1 && (
          <div
            className="absolute top-1/2 -translate-y-1/2 w-2.5 h-2.5 rounded-full bg-[#8BAB8B] border-2 border-[#4A6B4A] transition-all duration-700"
            style={{ left: `calc(${percentage}% - 5px)` }}
          />
        )}

        {/* Completion flourish */}
        {progress >= 1 && (
          <div className="absolute inset-0 flex items-center justify-end pr-1">
            <span className="text-[8px] text-[#E8C4A0]">*</span>
          </div>
        )}
      </div>
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

function getPlotIcon(crownJewel: string | null | undefined): { icon: LucideIcon; color: string } {
  if (!crownJewel) {
    return { icon: FolderOpen, color: '#AB9080' }; // Sand for generic
  }
  const jewelName = JEWEL_NAME_MAP[crownJewel];
  if (jewelName) {
    return { icon: JEWEL_ICONS[jewelName], color: JEWEL_COLORS[jewelName].primary };
  }
  return { icon: FolderOpen, color: '#AB9080' };
}

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

function getVineGradient(progress: number): string {
  // Gradient gets warmer as progress increases
  if (progress >= 1) {
    return 'linear-gradient(90deg, #4A6B4A, #8BAB8B, #E8C4A0)'; // Sage to Sprout to Honey
  }
  if (progress >= 0.7) {
    return 'linear-gradient(90deg, #4A6B4A, #8BAB8B)'; // Sage to Sprout
  }
  if (progress >= 0.3) {
    return 'linear-gradient(90deg, #2E4A2E, #4A6B4A)'; // Fern to Sage
  }
  return '#2E4A2E'; // Fern (early growth)
}

export default PlotTile;
