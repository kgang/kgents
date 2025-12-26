/**
 * WithLoss — HOC/Wrapper for Adding Loss Indicator
 *
 * Wraps any component with a loss indicator overlay.
 * Usage: <WithLoss loss={0.42}><AnyComponent /></WithLoss>
 *
 * STARK BIOME aesthetic: Subtle overlay, doesn't obscure content
 */

import { memo, ReactNode } from 'react';
import { LossIndicator } from './LossIndicator';

// =============================================================================
// Types
// =============================================================================

export interface WithLossProps {
  /** The loss value to display */
  loss: number;

  /** Child components to wrap */
  children: ReactNode;

  /** Position of loss indicator */
  position?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';

  /** Show label with loss value */
  showLabel?: boolean;

  /** Show gradient bar */
  showGradient?: boolean;

  /** Size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Custom CSS class */
  className?: string;
}

// =============================================================================
// Helpers
// =============================================================================

function getPositionStyles(position: string) {
  const base = {
    position: 'absolute' as const,
    zIndex: 10,
  };

  switch (position) {
    case 'top-left':
      return { ...base, top: 'var(--space-xs, 0.2rem)', left: 'var(--space-xs, 0.2rem)' };
    case 'top-right':
      return { ...base, top: 'var(--space-xs, 0.2rem)', right: 'var(--space-xs, 0.2rem)' };
    case 'bottom-left':
      return { ...base, bottom: 'var(--space-xs, 0.2rem)', left: 'var(--space-xs, 0.2rem)' };
    case 'bottom-right':
      return {
        ...base,
        bottom: 'var(--space-xs, 0.2rem)',
        right: 'var(--space-xs, 0.2rem)',
      };
    default:
      return { ...base, top: 'var(--space-xs, 0.2rem)', right: 'var(--space-xs, 0.2rem)' };
  }
}

// =============================================================================
// Main Component
// =============================================================================

export const WithLoss = memo(function WithLoss({
  loss,
  children,
  position = 'top-right',
  showLabel = false,
  showGradient = false,
  size = 'sm',
  className = '',
}: WithLossProps) {
  return (
    <div
      className={`with-loss ${className}`}
      style={{
        position: 'relative',
      }}
    >
      {/* Child content */}
      {children}

      {/* Loss indicator overlay */}
      <div className="with-loss__indicator" style={getPositionStyles(position)}>
        <LossIndicator
          loss={loss}
          showLabel={showLabel}
          showGradient={showGradient}
          size={size}
        />
      </div>
    </div>
  );
});

export default WithLoss;
