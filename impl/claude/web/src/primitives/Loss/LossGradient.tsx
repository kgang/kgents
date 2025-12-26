/**
 * LossGradient — Navigation by Loss
 *
 * Shows a gradient bar with clickable regions to navigate to items
 * with different loss values. Useful for filtering/sorting by coherence.
 *
 * STARK BIOME aesthetic: Green → Yellow → Red gradient
 */

import { memo, useMemo } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface LossGradientProps {
  /** Current loss value (highlights position on gradient) */
  currentLoss?: number;

  /** Callback when user clicks on gradient */
  onNavigate?: (targetLoss: number) => void;

  /** Show tick marks at quartiles */
  showTicks?: boolean;

  /** Width of gradient bar */
  width?: number | string;

  /** Height of gradient bar */
  height?: number | string;

  /** Custom CSS class */
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

function getLossGradient(): string {
  return 'linear-gradient(to right, var(--health-healthy, #22c55e) 0%, var(--health-degraded, #facc15) 50%, var(--health-warning, #f97316) 75%, var(--health-critical, #ef4444) 100%)';
}

// =============================================================================
// Main Component
// =============================================================================

export const LossGradient = memo(function LossGradient({
  currentLoss,
  onNavigate,
  showTicks = true,
  width = '100%',
  height = '32px',
  className = '',
}: LossGradientProps) {
  const handleClick = (event: React.MouseEvent<HTMLDivElement>) => {
    if (!onNavigate) return;

    const rect = event.currentTarget.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const targetLoss = x / rect.width;

    // Clamp to [0, 1]
    const clamped = Math.max(0, Math.min(1, targetLoss));
    onNavigate(clamped);
  };

  const ticks = useMemo(() => [0, 0.25, 0.5, 0.75, 1.0], []);

  return (
    <div
      className={`loss-gradient ${className}`}
      style={{
        position: 'relative',
        width,
        height,
      }}
    >
      {/* Gradient bar */}
      <div
        className="loss-gradient__bar"
        onClick={handleClick}
        style={{
          width: '100%',
          height: '100%',
          background: getLossGradient(),
          borderRadius: 'var(--radius-bare, 2px)',
          cursor: onNavigate ? 'pointer' : 'default',
          position: 'relative',
          transition: 'box-shadow var(--duration-fast, 120ms)',
        }}
        onMouseEnter={(e) => {
          if (onNavigate) {
            e.currentTarget.style.boxShadow = '0 0 12px rgba(255, 255, 255, 0.2)';
          }
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.boxShadow = 'none';
        }}
      >
        {/* Current position marker */}
        {currentLoss !== undefined && (
          <div
            className="loss-gradient__marker"
            style={{
              position: 'absolute',
              top: '50%',
              left: `${Math.max(0, Math.min(1, currentLoss)) * 100}%`,
              transform: 'translate(-50%, -50%)',
              width: '4px',
              height: 'calc(100% + 8px)',
              background: 'var(--surface-0, #0a0a0c)',
              border: '2px solid var(--text-primary, #e5e7eb)',
              borderRadius: 'var(--radius-pill, 9999px)',
              boxShadow: '0 0 8px rgba(255, 255, 255, 0.5)',
              pointerEvents: 'none',
            }}
          />
        )}

        {/* Tick marks */}
        {showTicks &&
          ticks.map((tick) => (
            <div
              key={tick}
              className="loss-gradient__tick"
              style={{
                position: 'absolute',
                left: `${tick * 100}%`,
                top: '0',
                bottom: '0',
                width: '1px',
                background: 'rgba(0, 0, 0, 0.3)',
                pointerEvents: 'none',
              }}
            />
          ))}
      </div>

      {/* Tick labels */}
      {showTicks && (
        <div
          className="loss-gradient__labels"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            marginTop: 'var(--space-xs, 0.2rem)',
            fontSize: '0.625rem',
            color: 'var(--text-muted, #5a5a64)',
            fontFamily: 'var(--font-mono, monospace)',
          }}
        >
          {ticks.map((tick) => (
            <span key={tick}>{tick.toFixed(2)}</span>
          ))}
        </div>
      )}
    </div>
  );
});

export default LossGradient;
