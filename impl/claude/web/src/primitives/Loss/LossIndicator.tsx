/**
 * LossIndicator — Universal Coherence Thermometer
 *
 * A single indicator showing loss value (0.00 = axiom → 1.00 = nonsense).
 * Used throughout the system to show coherence drift.
 *
 * STARK BIOME aesthetic: Green (coherent) → Yellow → Red (incoherent)
 */

import { memo, useMemo } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface LossIndicatorProps {
  /** Loss value: 0.00 (axiom, perfect coherence) → 1.00 (nonsense, max drift) */
  loss: number;

  /** Show text label with loss value */
  showLabel?: boolean;

  /** Show color gradient bar */
  showGradient?: boolean;

  /** Enable interactive navigation to lower/higher loss */
  interactive?: boolean;

  /** Callback when user clicks to navigate */
  onNavigate?: (direction: 'lower' | 'higher') => void;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Custom CSS class */
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Get color for loss value using STARK BIOME palette.
 * Loss 0.00 = bright green (axiom)
 * Loss 0.50 = yellow (uncertain)
 * Loss 1.00 = red (nonsense)
 */
function getLossColor(loss: number): string {
  // Clamp to [0, 1]
  const clamped = Math.max(0, Math.min(1, loss));

  if (clamped < 0.2) {
    // 0.00-0.20: Healthy green
    return 'var(--health-healthy, #22c55e)';
  } else if (clamped < 0.5) {
    // 0.20-0.50: Warning yellow
    return 'var(--health-degraded, #facc15)';
  } else if (clamped < 0.8) {
    // 0.50-0.80: Alert orange
    return 'var(--health-warning, #f97316)';
  }
  // 0.80-1.00: Critical red
  return 'var(--health-critical, #ef4444)';
}

/**
 * Get gradient string for loss bar.
 */
function getLossGradient(): string {
  return 'linear-gradient(to right, var(--health-healthy, #22c55e), var(--health-degraded, #facc15), var(--health-warning, #f97316), var(--health-critical, #ef4444))';
}

// =============================================================================
// Main Component
// =============================================================================

export const LossIndicator = memo(function LossIndicator({
  loss,
  showLabel = true,
  showGradient = false,
  interactive = false,
  onNavigate,
  size = 'md',
  className = '',
}: LossIndicatorProps) {
  const color = useMemo(() => getLossColor(loss), [loss]);

  // Clamp loss to [0, 1] for display
  const displayLoss = Math.max(0, Math.min(1, loss));

  // Size-based dimensions
  const dimensions = useMemo(() => {
    switch (size) {
      case 'sm':
        return { fontSize: '0.75rem', barHeight: '4px', dotSize: '8px' };
      case 'lg':
        return { fontSize: '1.125rem', barHeight: '8px', dotSize: '16px' };
      default:
        return { fontSize: '0.875rem', barHeight: '6px', dotSize: '12px' };
    }
  }, [size]);

  const handleLowerClick = () => {
    if (interactive && onNavigate) {
      onNavigate('lower');
    }
  };

  const handleHigherClick = () => {
    if (interactive && onNavigate) {
      onNavigate('higher');
    }
  };

  return (
    <div
      className={`loss-indicator loss-indicator--${size} ${
        interactive ? 'loss-indicator--interactive' : ''
      } ${className}`}
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: 'var(--space-sm, 0.4rem)',
        fontSize: dimensions.fontSize,
      }}
    >
      {/* Label */}
      {showLabel && (
        <span
          className="loss-indicator__label"
          style={{
            color: 'var(--text-secondary, #8a8a94)',
            fontFamily: 'var(--font-mono, monospace)',
            fontWeight: 500,
          }}
        >
          Loss: {displayLoss.toFixed(2)}
        </span>
      )}

      {/* Gradient bar or dot */}
      {showGradient ? (
        <div
          className="loss-indicator__gradient-bar"
          style={{
            position: 'relative',
            width: '100px',
            height: dimensions.barHeight,
            background: getLossGradient(),
            borderRadius: 'var(--radius-pill, 9999px)',
          }}
        >
          {/* Position marker */}
          <div
            className="loss-indicator__marker"
            style={{
              position: 'absolute',
              top: '50%',
              left: `${displayLoss * 100}%`,
              transform: 'translate(-50%, -50%)',
              width: dimensions.dotSize,
              height: dimensions.dotSize,
              borderRadius: '50%',
              background: 'var(--surface-0, #0a0a0c)',
              border: `2px solid ${color}`,
              boxShadow: `0 0 8px ${color}`,
            }}
          />
        </div>
      ) : (
        <div
          className="loss-indicator__dot"
          style={{
            width: dimensions.dotSize,
            height: dimensions.dotSize,
            borderRadius: '50%',
            background: color,
            boxShadow: `0 0 6px ${color}`,
          }}
          title={`Loss: ${displayLoss.toFixed(2)}`}
        />
      )}

      {/* Interactive navigation buttons */}
      {interactive && onNavigate && (
        <div
          className="loss-indicator__nav"
          style={{
            display: 'flex',
            gap: 'var(--space-xs, 0.2rem)',
          }}
        >
          <button
            className="loss-indicator__nav-btn"
            onClick={handleLowerClick}
            title="Navigate to lower loss"
            style={{
              padding: '2px 6px',
              fontSize: '0.75rem',
              color: 'var(--text-secondary, #8a8a94)',
              background: 'var(--surface-2, #1c1c22)',
              border: '1px solid var(--border-subtle, #28282f)',
              borderRadius: 'var(--radius-bare, 2px)',
              cursor: 'pointer',
              transition: 'all var(--duration-fast, 120ms)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--surface-3, #28282f)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--surface-2, #1c1c22)';
            }}
          >
            ↓
          </button>
          <button
            className="loss-indicator__nav-btn"
            onClick={handleHigherClick}
            title="Navigate to higher loss"
            style={{
              padding: '2px 6px',
              fontSize: '0.75rem',
              color: 'var(--text-secondary, #8a8a94)',
              background: 'var(--surface-2, #1c1c22)',
              border: '1px solid var(--border-subtle, #28282f)',
              borderRadius: 'var(--radius-bare, 2px)',
              cursor: 'pointer',
              transition: 'all var(--duration-fast, 120ms)',
            }}
            onMouseEnter={(e) => {
              e.currentTarget.style.background = 'var(--surface-3, #28282f)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.background = 'var(--surface-2, #1c1c22)';
            }}
          >
            ↑
          </button>
        </div>
      )}
    </div>
  );
});

export default LossIndicator;
