/**
 * LossBadge — Visual indicator of Galois loss signature
 *
 * "Loss = Difficulty. Every node carries a Galois loss value."
 *
 * The badge uses a viridis-inspired color gradient:
 * - Purple (L < 0.2): Axiomatic, stable, trustworthy
 * - Teal (L ≈ 0.5): Transitional, evolving
 * - Yellow (L > 0.7): Unstable, investigate, pulse warning
 */

import { memo } from 'react';
import type { LossSignature } from '../../hooks/useLoss';
import { lossToHue } from '../../hooks/useLoss';
import './LossBadge.css';

// =============================================================================
// Types
// =============================================================================

interface LossBadgeProps {
  /** Loss signature to display */
  signature: LossSignature;

  /** Badge size variant */
  size?: 'sm' | 'md' | 'lg';

  /** Show component breakdown bars */
  showComponents?: boolean;

  /** Show layer indicator */
  showLayer?: boolean;

  /** Click handler */
  onClick?: () => void;

  /** Additional CSS class */
  className?: string;
}

interface ComponentBarProps {
  label: string;
  value: number;
  title: string;
}

// =============================================================================
// Sub-components
// =============================================================================

const ComponentBar = memo(function ComponentBar({
  label,
  value,
  title,
}: ComponentBarProps) {
  const percentage = (value * 100).toFixed(0);
  const hue = lossToHue(value);

  return (
    <div className="loss-component" title={title}>
      <span className="loss-component__label">{label}</span>
      <div className="loss-component__bar">
        <div
          className="loss-component__fill"
          style={{
            width: `${percentage}%`,
            backgroundColor: `hsl(${hue}, 60%, 50%)`,
          }}
        />
      </div>
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const LossBadge = memo(function LossBadge({
  signature,
  size = 'md',
  showComponents = false,
  showLayer = true,
  onClick,
  className = '',
}: LossBadgeProps) {
  const hue = lossToHue(signature.total);
  const percentage = (signature.total * 100).toFixed(0);

  const statusClass = `loss-badge--${signature.status}`;
  const sizeClass = `loss-badge--${size}`;
  const clickableClass = onClick ? 'loss-badge--clickable' : '';

  return (
    <div
      className={`loss-badge ${statusClass} ${sizeClass} ${clickableClass} ${className}`}
      style={{ '--loss-hue': hue } as React.CSSProperties}
      onClick={onClick}
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      title={`Loss: ${percentage}% (${signature.status})${signature.isAxiomatic ? ' — Axiomatic' : ''}`}
    >
      {/* Axiom indicator */}
      {signature.isAxiomatic && (
        <span className="loss-badge__axiom" title="Axiomatic (fixed point)">
          A
        </span>
      )}

      {/* Main loss value */}
      <span className="loss-badge__value">{percentage}%</span>

      {/* Layer indicator */}
      {showLayer && (
        <span className="loss-badge__layer">L{signature.layer}</span>
      )}

      {/* Component breakdown */}
      {showComponents && (
        <div className="loss-badge__components">
          <ComponentBar
            label="C"
            value={signature.components.content}
            title={`Content: ${(signature.components.content * 100).toFixed(0)}%`}
          />
          <ComponentBar
            label="P"
            value={signature.components.proof}
            title={`Proof: ${(signature.components.proof * 100).toFixed(0)}%`}
          />
          <ComponentBar
            label="E"
            value={signature.components.edge}
            title={`Edge: ${(signature.components.edge * 100).toFixed(0)}%`}
          />
          <ComponentBar
            label="M"
            value={signature.components.metadata}
            title={`Metadata: ${(signature.components.metadata * 100).toFixed(0)}%`}
          />
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Compact Variant
// =============================================================================

interface LossDotProps {
  loss: number;
  size?: number;
  className?: string;
}

/**
 * Minimal loss indicator for inline use.
 */
export const LossDot = memo(function LossDot({
  loss,
  size = 8,
  className = '',
}: LossDotProps) {
  const hue = lossToHue(loss);
  const isUnstable = loss > 0.7;

  return (
    <span
      className={`loss-dot ${isUnstable ? 'loss-dot--pulse' : ''} ${className}`}
      style={{
        width: size,
        height: size,
        backgroundColor: `hsl(${hue}, 60%, 50%)`,
      }}
      title={`Loss: ${(loss * 100).toFixed(0)}%`}
    />
  );
});

export default LossBadge;
