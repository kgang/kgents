/**
 * ContradictionBadge — Lightning bolt indicator for contradictions
 *
 * Visual cue that contradictions exist in content.
 * Severity levels map to different visual treatments.
 *
 * Philosophy: Contradictions aren't bugs—they're opportunities for synthesis.
 */

import { memo } from 'react';
import './ContradictionBadge.css';

// =============================================================================
// Types
// =============================================================================

export type ContradictionSeverity = 'low' | 'medium' | 'high';

export interface ContradictionBadgeProps {
  /** Whether contradiction exists */
  hasContradiction: boolean;
  /** Severity level (affects visual treatment) */
  severity?: ContradictionSeverity;
  /** Click handler */
  onClick?: () => void;
  /** Tooltip text */
  tooltip?: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
}

// =============================================================================
// Constants
// =============================================================================

const SEVERITY_LABELS: Record<ContradictionSeverity, string> = {
  low: 'Apparent contradiction',
  medium: 'Productive tension',
  high: 'Genuine contradiction',
};

// =============================================================================
// Component
// =============================================================================

export const ContradictionBadge = memo(function ContradictionBadge({
  hasContradiction,
  severity = 'medium',
  onClick,
  tooltip,
  size = 'md',
}: ContradictionBadgeProps) {
  if (!hasContradiction) {
    return null;
  }

  const defaultTooltip = tooltip || SEVERITY_LABELS[severity];
  const isClickable = !!onClick;

  return (
    <div
      className="contradiction-badge"
      data-severity={severity}
      data-size={size}
      data-clickable={isClickable}
      onClick={onClick}
      title={defaultTooltip}
      role={isClickable ? 'button' : undefined}
      tabIndex={isClickable ? 0 : undefined}
      onKeyDown={(e) => {
        if (isClickable && (e.key === 'Enter' || e.key === ' ')) {
          e.preventDefault();
          onClick?.();
        }
      }}
    >
      <span className="contradiction-badge__icon">⚡</span>
    </div>
  );
});

export default ContradictionBadge;
