/**
 * EntropySlider — The Heart of the Terrarium
 *
 * A single slider that controls chaos across ALL creatures.
 * As you drag, every component responds. You don't read about entropy—you feel it.
 *
 * Design: Minimal, focused. One slider, one label, one purpose.
 */

import type { CSSProperties } from 'react';
import { entropyLabel } from '@/hooks/useTerrarium';
import { LIVING_EARTH, GRAYS } from '@/constants/colors';

export interface EntropySliderProps {
  /** Current entropy value (0-1) */
  value: number;
  /** Called when user changes entropy */
  onChange: (value: number) => void;
  /** Additional CSS classes */
  className?: string;
  /** Additional inline styles */
  style?: CSSProperties;
}

/**
 * Get track gradient based on entropy level.
 * Calm = muted green, Chaotic = warm amber.
 */
function getTrackGradient(value: number): string {
  if (value < 0.3) {
    return `linear-gradient(to right, ${LIVING_EARTH.fern}, ${LIVING_EARTH.sage})`;
  }
  if (value < 0.7) {
    return `linear-gradient(to right, ${LIVING_EARTH.sage}, ${LIVING_EARTH.copper})`;
  }
  return `linear-gradient(to right, ${LIVING_EARTH.copper}, ${LIVING_EARTH.amber})`;
}

/**
 * Get label color based on entropy level.
 */
function getLabelColor(value: number): string {
  if (value > 0.7) return LIVING_EARTH.amber;
  if (value > 0.3) return LIVING_EARTH.copper;
  return LIVING_EARTH.sage;
}

export function EntropySlider({ value, onChange, className = '', style }: EntropySliderProps) {
  const label = entropyLabel(value);

  return (
    <div
      className={`entropy-slider ${className}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '0.75rem 1rem',
        background: GRAYS[800],
        borderRadius: '0.5rem',
        ...style,
      }}
    >
      <label
        htmlFor="entropy-control"
        style={{
          fontFamily: 'monospace',
          fontSize: '0.75rem',
          fontWeight: 500,
          color: GRAYS[400],
          textTransform: 'uppercase',
          letterSpacing: '0.05em',
          minWidth: '4rem',
        }}
      >
        Entropy
      </label>

      <input
        id="entropy-control"
        type="range"
        min={0}
        max={1}
        step={0.01}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        style={{
          flex: 1,
          height: '4px',
          borderRadius: '2px',
          background: getTrackGradient(value),
          appearance: 'none',
          cursor: 'pointer',
        }}
        aria-label={`Entropy level: ${label}`}
      />

      <span
        style={{
          fontFamily: 'monospace',
          fontSize: '0.75rem',
          fontWeight: 600,
          color: getLabelColor(value),
          minWidth: '4rem',
          textAlign: 'right',
        }}
      >
        {label}
      </span>
    </div>
  );
}

export default EntropySlider;
