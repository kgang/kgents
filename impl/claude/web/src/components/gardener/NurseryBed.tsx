/**
 * NurseryBed - Concept Nursery Visualization
 *
 * Displays concepts growing from seeds to ready-for-promotion,
 * using the garden metaphor with Living Earth palette.
 *
 * Visual Design:
 * - Seeds appear as small circles that grow with usage
 * - Growth stage affects size and glow intensity
 * - READY seeds pulse (like SeasonOrb) asking to be picked
 * - No emojis—uses Lucide icons (CircleDot, Sprout, Leaf, Flower2)
 *
 * @see spec/protocols/gardener-logos.md - Concept Nursery extension
 * @see docs/creative/visual-system.md - NO EMOJIS policy
 */

import { Circle, Sprout, Leaf, Flower2, Check } from 'lucide-react';
import { Breathe, PopOnMount } from '@/components/joy';
import type { ConceptSeedJSON, ConceptStage } from '@/reactive/types';

// =============================================================================
// Types
// =============================================================================

export interface NurseryBedProps {
  /** List of concept seeds in the nursery */
  seeds: ConceptSeedJSON[];
  /** Callback when user accepts promotion for a READY seed */
  onPromote?: (handle: string) => void;
  /** Callback when user dismisses a READY seed */
  onDismiss?: (handle: string) => void;
  /** Compact mode for mobile */
  compact?: boolean;
  /** Custom class name */
  className?: string;
}

// =============================================================================
// Living Earth Stage Colors
// =============================================================================

/**
 * Stage colors from Living Earth palette.
 * Maps concept growth stages to garden visual language.
 */
const STAGE_COLORS: Record<
  ConceptStage,
  {
    bg: string;
    orb: string;
    text: string;
    accent: string;
  }
> = {
  SEED: {
    bg: '#4A3728',
    orb: '#6B4E3D',
    text: '#AB9080',
    accent: '#6B4E3D',
  },
  SPROUTING: {
    bg: '#1A2E1A',
    orb: '#4A6B4A',
    text: '#8BAB8B',
    accent: '#4A6B4A',
  },
  GROWING: {
    bg: '#2E4A2E',
    orb: '#6B8B6B',
    text: '#8BAB8B',
    accent: '#4A6B4A',
  },
  READY: {
    bg: '#8B5A2B40', // Amber with transparency
    orb: '#D4A574',
    text: '#F5E6D3',
    accent: '#C08552',
  },
  PROMOTED: {
    bg: '#1A2E1A',
    orb: '#4A6B4A',
    text: '#8BAB8B',
    accent: '#4A6B4A',
  },
};

/**
 * Get the appropriate icon for a growth stage.
 */
function StageIcon({ stage, className }: { stage: ConceptStage; className?: string }) {
  const iconClass = className || 'w-4 h-4';

  switch (stage) {
    case 'SEED':
      return <Circle className={iconClass} />;
    case 'SPROUTING':
      return <Sprout className={iconClass} />;
    case 'GROWING':
      return <Leaf className={iconClass} />;
    case 'READY':
      return <Flower2 className={iconClass} />;
    case 'PROMOTED':
      return <Check className={iconClass} />;
  }
}

// =============================================================================
// Sub-components
// =============================================================================

interface SeedOrbProps {
  seed: ConceptSeedJSON;
  onPromote?: () => void;
  onDismiss?: () => void;
  compact?: boolean;
}

function SeedOrb({ seed, onPromote, onDismiss, compact }: SeedOrbProps) {
  const colors = STAGE_COLORS[seed.stage];
  const isReady = seed.stage === 'READY';

  // Size based on stage (seeds are small, ready is large)
  const sizeClass = {
    SEED: compact ? 'w-8 h-8' : 'w-10 h-10',
    SPROUTING: compact ? 'w-9 h-9' : 'w-11 h-11',
    GROWING: compact ? 'w-10 h-10' : 'w-12 h-12',
    READY: compact ? 'w-12 h-12' : 'w-14 h-14',
    PROMOTED: compact ? 'w-8 h-8' : 'w-10 h-10',
  }[seed.stage];

  // Box shadow glow based on intensity
  const glowStyle =
    seed.glow_intensity > 0
      ? { boxShadow: `0 0 ${Math.round(seed.glow_intensity * 20)}px ${colors.orb}60` }
      : {};

  const orb = (
    <div
      className={`
        ${sizeClass} rounded-full flex items-center justify-center
        transition-all duration-300 cursor-pointer
        hover:scale-105
      `}
      style={{
        backgroundColor: colors.orb,
        ...glowStyle,
      }}
      title={`${seed.handle} (${seed.usage_count} uses, ${(seed.success_rate * 100).toFixed(0)}% success)`}
    >
      <StageIcon stage={seed.stage} className={compact ? 'w-4 h-4' : 'w-5 h-5'} />
    </div>
  );

  return (
    <PopOnMount scale={1.05} duration={200}>
      <div className="flex flex-col items-center gap-1">
        {seed.should_pulse ? (
          <Breathe intensity={0.4} speed="slow">
            {orb}
          </Breathe>
        ) : (
          orb
        )}

        {/* Handle label (truncated) */}
        <span
          className="text-[10px] truncate max-w-[60px] text-center"
          style={{ color: colors.text }}
        >
          {formatHandle(seed.handle)}
        </span>

        {/* Promote/Dismiss actions for READY seeds */}
        {isReady && (onPromote || onDismiss) && (
          <div className="flex gap-1 mt-1">
            {onPromote && (
              <button
                onClick={onPromote}
                className="px-2 py-0.5 text-[10px] rounded bg-[#4A6B4A] text-[#F5E6D3] hover:bg-[#5A7B5A] transition-colors"
              >
                Promote
              </button>
            )}
            {onDismiss && (
              <button
                onClick={onDismiss}
                className="px-2 py-0.5 text-[10px] rounded bg-[#6B4E3D] text-[#AB9080] hover:bg-[#7B5E4D] transition-colors"
              >
                Dismiss
              </button>
            )}
          </div>
        )}
      </div>
    </PopOnMount>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function NurseryBed({
  seeds,
  onPromote,
  onDismiss,
  compact = false,
  className = '',
}: NurseryBedProps) {
  // Filter out promoted seeds (they leave the nursery)
  const activeSeeds = seeds.filter((s) => s.stage !== 'PROMOTED');

  // Don't render if no seeds (opt-in UI)
  if (activeSeeds.length === 0) {
    return null;
  }

  // Sort: READY first, then by usage count
  const sortedSeeds = [...activeSeeds].sort((a, b) => {
    if (a.stage === 'READY' && b.stage !== 'READY') return -1;
    if (b.stage === 'READY' && a.stage !== 'READY') return 1;
    return b.usage_count - a.usage_count;
  });

  // Group by stage for display
  const readySeeds = sortedSeeds.filter((s) => s.stage === 'READY');
  const growingSeeds = sortedSeeds.filter((s) => s.stage === 'SPROUTING' || s.stage === 'GROWING');
  const seedSeeds = sortedSeeds.filter((s) => s.stage === 'SEED');

  return (
    <div
      className={`rounded-xl p-4 ${compact ? 'p-3' : 'p-4'} ${className}`}
      style={{ backgroundColor: '#2D1B1440' }} // Dark earth with transparency
    >
      {/* Header */}
      <h3
        className={`font-semibold mb-3 ${compact ? 'text-sm' : 'text-base'}`}
        style={{ color: '#F5E6D3' }}
      >
        Concept Nursery
        <span className="text-xs font-normal ml-2" style={{ color: '#AB9080' }}>
          ({activeSeeds.length} growing)
        </span>
      </h3>

      {/* Ready section (if any) */}
      {readySeeds.length > 0 && (
        <div className="mb-4">
          <div className="text-xs uppercase tracking-wide mb-2" style={{ color: '#D4A574' }}>
            Ready for Harvest
          </div>
          <div className="flex flex-wrap gap-3">
            {readySeeds.map((seed) => (
              <SeedOrb
                key={seed.handle}
                seed={seed}
                onPromote={onPromote ? () => onPromote(seed.handle) : undefined}
                onDismiss={onDismiss ? () => onDismiss(seed.handle) : undefined}
                compact={compact}
              />
            ))}
          </div>
        </div>
      )}

      {/* Growing section (if any) */}
      {growingSeeds.length > 0 && (
        <div className="mb-3">
          <div className="text-xs uppercase tracking-wide mb-2" style={{ color: '#8BAB8B' }}>
            Growing
          </div>
          <div className="flex flex-wrap gap-3">
            {growingSeeds.map((seed) => (
              <SeedOrb key={seed.handle} seed={seed} compact={compact} />
            ))}
          </div>
        </div>
      )}

      {/* Seeds section (if any) - show as smaller group */}
      {seedSeeds.length > 0 && (
        <div>
          <div className="text-xs uppercase tracking-wide mb-2" style={{ color: '#6B4E3D' }}>
            Seeds ({seedSeeds.length})
          </div>
          <div className="flex flex-wrap gap-2">
            {seedSeeds.slice(0, compact ? 5 : 10).map((seed) => (
              <SeedOrb key={seed.handle} seed={seed} compact={compact} />
            ))}
            {seedSeeds.length > (compact ? 5 : 10) && (
              <span className="text-xs self-center" style={{ color: '#6B4E3D' }}>
                +{seedSeeds.length - (compact ? 5 : 10)} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Format AGENTESE handle for display.
 * Extracts the last segment: "world.garden.concept" → "concept"
 */
function formatHandle(handle: string): string {
  const parts = handle.split('.');
  return parts[parts.length - 1];
}

export default NurseryBed;
