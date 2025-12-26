/**
 * TrustLevelBadge — Trust level indicator
 *
 * Displays trust level (L0-L3) with color-coded badge.
 * Shows reasoning on hover.
 *
 * Visual encoding:
 * - L0: Gray (READ_ONLY, default)
 * - L1: Blue (BOUNDED, earned trust)
 * - L2: Green (SUGGESTION, high trust)
 * - L3: Gold (AUTONOMOUS, maximum trust)
 */

import type { TrustLevel } from './types';
import './TrustLevelBadge.css';

// =============================================================================
// Types
// =============================================================================

export interface TrustLevelBadgeProps {
  /** Trust level */
  level: TrustLevel;
  /** Reasoning for trust level */
  reasoning?: string;
  /** Size variant */
  size?: 'sm' | 'md' | 'lg';
  /** Show label text */
  showLabel?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const TRUST_LEVEL_LABELS: Record<TrustLevel, string> = {
  L0: 'Read-Only',
  L1: 'Bounded',
  L2: 'Suggestion',
  L3: 'Autonomous',
};

// =============================================================================
// Component
// =============================================================================

export function TrustLevelBadge({
  level,
  reasoning,
  size = 'md',
  showLabel = true,
}: TrustLevelBadgeProps) {
  const label = TRUST_LEVEL_LABELS[level];

  return (
    <div
      className="trust-level-badge"
      data-level={level}
      data-size={size}
      title={reasoning}
    >
      <div className="trust-level-badge__indicator">
        {level}
      </div>
      {showLabel && (
        <div className="trust-level-badge__label">
          {label}
        </div>
      )}
    </div>
  );
}
