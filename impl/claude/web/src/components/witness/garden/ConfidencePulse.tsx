/**
 * ConfidencePulse: Heartbeat visualization tied to confidence.
 *
 * From spec:
 *   "Flatline IS the animation at low confidence. Stillness communicates."
 *
 * PulseRate:
 * - FLATLINE (0): confidence < 0.3 — no animation
 * - AWAKENING (0.5): 0.3-0.6 — slow pulse
 * - ALIVE (1.0): 0.6-0.9 — steady pulse
 * - THRIVING (1.5): > 0.9 — strong pulse
 *
 * @see spec/protocols/witness-assurance-surface.md
 */

import { motion } from 'framer-motion';
import type { ConfidencePulse as ConfidencePulseType, PulseRate } from '@/api/witness';

// =============================================================================
// Constants
// =============================================================================

const PULSE_COLORS: Record<PulseRate, { core: string; glow: string }> = {
  [0]: { core: '#6B7280', glow: '#374151' }, // Gray - flatline
  [0.5]: { core: '#F59E0B', glow: '#92400E' }, // Amber - awakening
  [1.0]: { core: '#10B981', glow: '#065F46' }, // Green - alive
  [1.5]: { core: '#3B82F6', glow: '#1E40AF' }, // Blue - thriving
};

const PULSE_LABELS: Record<PulseRate, string> = {
  [0]: 'Flatline',
  [0.5]: 'Awakening',
  [1.0]: 'Alive',
  [1.5]: 'Thriving',
};

// =============================================================================
// Types
// =============================================================================

export interface ConfidencePulseProps {
  /** The pulse data */
  pulse: ConfidencePulseType;
  /** Size of the pulse indicator */
  size?: 'sm' | 'md' | 'lg';
  /** Show confidence value */
  showValue?: boolean;
  /** Show delta arrow */
  showDelta?: boolean;
  /** Additional CSS classes */
  className?: string;
}

// =============================================================================
// Main Component
// =============================================================================

export function ConfidencePulse({
  pulse,
  size = 'md',
  showValue = true,
  showDelta = true,
  className = '',
}: ConfidencePulseProps) {
  const rate = pulse.pulse_rate;
  const colors = PULSE_COLORS[rate];
  const label = PULSE_LABELS[rate];
  const isAnimated = rate > 0;

  // Size configuration
  const sizes = {
    sm: { outer: 20, inner: 12, text: 'text-xs' },
    md: { outer: 32, inner: 20, text: 'text-sm' },
    lg: { outer: 48, inner: 32, text: 'text-base' },
  };
  const { outer, inner, text } = sizes[size];

  // Animation variants based on pulse rate
  const pulseVariants = {
    flatline: {
      scale: 1,
      opacity: 0.5,
    },
    awakening: {
      scale: [1, 1.05, 1],
      opacity: [0.7, 1, 0.7],
      transition: {
        duration: 2.5,
        repeat: Infinity,
        ease: 'easeInOut' as const,
      },
    },
    alive: {
      scale: [1, 1.1, 1],
      opacity: [0.8, 1, 0.8],
      transition: {
        duration: 1.5,
        repeat: Infinity,
        ease: 'easeInOut' as const,
      },
    },
    thriving: {
      scale: [1, 1.15, 1],
      opacity: [0.9, 1, 0.9],
      transition: {
        duration: 1.0,
        repeat: Infinity,
        ease: 'easeInOut' as const,
      },
    },
  };

  const variant =
    rate === 0 ? 'flatline' : rate === 0.5 ? 'awakening' : rate === 1.0 ? 'alive' : 'thriving';

  // Delta arrow
  const deltaArrow =
    pulse.delta_direction === 'increasing'
      ? '\u2197' // ↗
      : pulse.delta_direction === 'decreasing'
        ? '\u2198' // ↘
        : '\u2192'; // →

  const deltaColor =
    pulse.delta_direction === 'increasing'
      ? 'text-green-400'
      : pulse.delta_direction === 'decreasing'
        ? 'text-red-400'
        : 'text-gray-400';

  return (
    <div className={`inline-flex items-center gap-2 ${className}`}>
      {/* Pulse indicator */}
      <div
        className="relative flex items-center justify-center"
        style={{ width: outer, height: outer }}
      >
        {/* Glow ring (only when animated) */}
        {isAnimated && (
          <motion.div
            className="absolute rounded-full"
            style={{
              width: outer,
              height: outer,
              backgroundColor: colors.glow,
              opacity: 0.3,
            }}
            variants={pulseVariants}
            initial="flatline"
            animate={variant}
          />
        )}

        {/* Core dot */}
        <motion.div
          className="rounded-full z-10"
          style={{
            width: inner,
            height: inner,
            backgroundColor: colors.core,
          }}
          variants={isAnimated ? pulseVariants : undefined}
          initial="flatline"
          animate={variant}
        />
      </div>

      {/* Value display */}
      {showValue && (
        <div className="flex flex-col">
          <div className="flex items-center gap-1">
            <span className={`font-mono font-medium ${text}`} style={{ color: colors.core }}>
              {(pulse.confidence * 100).toFixed(0)}%
            </span>
            {showDelta && <span className={`${deltaColor} text-xs`}>{deltaArrow}</span>}
          </div>
          <span className="text-xs text-gray-500">{label}</span>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Compact Variant
// =============================================================================

export interface PulseDotProps {
  confidence: number;
  size?: number;
  className?: string;
}

/**
 * Minimal pulse dot for use in lists/cards.
 */
export function PulseDot({ confidence, size = 8, className = '' }: PulseDotProps) {
  const rate: PulseRate =
    confidence < 0.3 ? 0 : confidence < 0.6 ? 0.5 : confidence < 0.9 ? 1.0 : 1.5;

  const colors = PULSE_COLORS[rate];
  const isAnimated = rate > 0;

  return (
    <motion.div
      className={`rounded-full ${className}`}
      style={{
        width: size,
        height: size,
        backgroundColor: colors.core,
      }}
      animate={
        isAnimated
          ? {
              scale: [1, 1.2, 1],
              opacity: [0.8, 1, 0.8],
            }
          : undefined
      }
      transition={{
        duration: rate === 0.5 ? 2.5 : rate === 1.0 ? 1.5 : 1.0,
        repeat: Infinity,
        ease: 'easeInOut',
      }}
    />
  );
}

// =============================================================================
// Exports
// =============================================================================

export default ConfidencePulse;
