/**
 * LossHeatmap — Multiple Blocks Colored by Loss
 *
 * Shows a grid or list of items with loss-based coloring.
 * Useful for visualizing coherence across multiple K-Blocks.
 *
 * STARK BIOME aesthetic: Background color intensity based on loss
 */

import { memo, useMemo } from 'react';

// =============================================================================
// Types
// =============================================================================

export interface LossHeatmapItem {
  id: string;
  label: string;
  loss: number;
  onClick?: () => void;
}

export interface LossHeatmapProps {
  /** Items to display in heatmap */
  items: LossHeatmapItem[];

  /** Layout mode */
  layout?: 'grid' | 'list';

  /** Grid columns (only for grid layout) */
  columns?: number;

  /** Show loss value on each item */
  showValue?: boolean;

  /** Custom CSS class */
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

/**
 * Get background color with opacity based on loss.
 * Low loss = subtle green, high loss = strong red.
 */
function getLossBackgroundColor(loss: number): string {
  const clamped = Math.max(0, Math.min(1, loss));

  if (clamped < 0.2) {
    // Healthy: subtle green
    return `rgba(34, 197, 94, ${0.1 + clamped * 0.3})`;
  } else if (clamped < 0.5) {
    // Warning: yellow
    return `rgba(250, 204, 21, ${0.15 + clamped * 0.3})`;
  } else if (clamped < 0.8) {
    // Alert: orange
    return `rgba(249, 115, 22, ${0.2 + clamped * 0.3})`;
  } else {
    // Critical: red
    return `rgba(239, 68, 68, ${0.25 + clamped * 0.4})`;
  }
}

/**
 * Get border color based on loss.
 */
function getLossBorderColor(loss: number): string {
  const clamped = Math.max(0, Math.min(1, loss));

  if (clamped < 0.2) {
    return 'var(--health-healthy, #22c55e)';
  } else if (clamped < 0.5) {
    return 'var(--health-degraded, #facc15)';
  } else if (clamped < 0.8) {
    return 'var(--health-warning, #f97316)';
  } else {
    return 'var(--health-critical, #ef4444)';
  }
}

// =============================================================================
// Main Component
// =============================================================================

export const LossHeatmap = memo(function LossHeatmap({
  items,
  layout = 'grid',
  columns = 4,
  showValue = true,
  className = '',
}: LossHeatmapProps) {
  const gridStyle = useMemo(
    () => ({
      display: 'grid',
      gridTemplateColumns:
        layout === 'grid' ? `repeat(${columns}, 1fr)` : '1fr',
      gap: 'var(--space-sm, 0.4rem)',
    }),
    [layout, columns]
  );

  return (
    <div className={`loss-heatmap loss-heatmap--${layout} ${className}`} style={gridStyle}>
      {items.map((item) => {
        const bgColor = getLossBackgroundColor(item.loss);
        const borderColor = getLossBorderColor(item.loss);

        return (
          <div
            key={item.id}
            className="loss-heatmap__item"
            onClick={item.onClick}
            style={{
              background: bgColor,
              border: `1px solid ${borderColor}`,
              borderRadius: 'var(--radius-bare, 2px)',
              padding: 'var(--space-sm, 0.4rem)',
              cursor: item.onClick ? 'pointer' : 'default',
              transition:
                'transform var(--duration-fast, 120ms), box-shadow var(--duration-fast, 120ms)',
              position: 'relative',
              overflow: 'hidden',
            }}
            onMouseEnter={(e) => {
              if (item.onClick) {
                e.currentTarget.style.transform = 'translateY(-2px)';
                e.currentTarget.style.boxShadow = `0 4px 12px ${borderColor}40`;
              }
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.transform = 'translateY(0)';
              e.currentTarget.style.boxShadow = 'none';
            }}
          >
            {/* Label */}
            <div
              className="loss-heatmap__label"
              style={{
                fontSize: '0.875rem',
                fontWeight: 500,
                color: 'var(--text-primary, #e5e7eb)',
                marginBottom: showValue ? 'var(--space-xs, 0.2rem)' : '0',
              }}
            >
              {item.label}
            </div>

            {/* Loss value */}
            {showValue && (
              <div
                className="loss-heatmap__value"
                style={{
                  fontSize: '0.75rem',
                  fontFamily: 'var(--font-mono, monospace)',
                  color: 'var(--text-secondary, #8a8a94)',
                }}
              >
                {item.loss.toFixed(2)}
              </div>
            )}

            {/* Visual indicator dot */}
            <div
              className="loss-heatmap__dot"
              style={{
                position: 'absolute',
                top: 'var(--space-xs, 0.2rem)',
                right: 'var(--space-xs, 0.2rem)',
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                background: borderColor,
                boxShadow: `0 0 6px ${borderColor}`,
              }}
            />
          </div>
        );
      })}
    </div>
  );
});

export default LossHeatmap;
