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
 * Calm = muted, Chaotic = vibrant.
 */
function getTrackGradient(value: number): string {
  // From sage (calm) to copper (active) to amber (chaotic)
  if (value < 0.3) {
    return 'linear-gradient(to right, var(--sage-600), var(--sage-500))';
  }
  if (value < 0.7) {
    return 'linear-gradient(to right, var(--sage-500), var(--copper-500))';
  }
  return 'linear-gradient(to right, var(--copper-500), var(--amber-500))';
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
        background: 'var(--surface-2)',
        borderRadius: '0.5rem',
        ...style,
      }}
    >
      <label
        htmlFor="entropy-control"
        style={{
          fontFamily: 'var(--font-mono)',
          fontSize: '0.75rem',
          fontWeight: 500,
          color: 'var(--text-secondary)',
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
          fontFamily: 'var(--font-mono)',
          fontSize: '0.75rem',
          fontWeight: 600,
          color:
            value > 0.7
              ? 'var(--amber-500)'
              : value > 0.3
                ? 'var(--copper-500)'
                : 'var(--sage-500)',
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
