/**
 * DirectorStatusBadge - Document lifecycle status indicator
 *
 * Shows document status with appropriate color and optional label.
 * Supports three sizes: sm, md, lg
 *
 * Status mapping:
 * - uploaded: gray (secondary)
 * - processing: blue (info) with pulse
 * - ready: green (success)
 * - executed: gold/amber (accent-gold)
 * - stale: orange (warning)
 * - failed: red (error)
 */

import type { DocumentStatus } from '../../api/director';

import './DirectorStatusBadge.css';

// =============================================================================
// Types
// =============================================================================

export interface DirectorStatusBadgeProps {
  status: DocumentStatus;
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

interface StatusConfig {
  label: string;
  icon: string;
  pulse?: boolean;
}

// =============================================================================
// Config
// =============================================================================

const STATUS_CONFIG: Record<DocumentStatus, StatusConfig> = {
  uploaded: { label: 'Uploaded', icon: '↑' },
  processing: { label: 'Processing', icon: '⟳', pulse: true },
  ready: { label: 'Ready', icon: '✓' },
  executed: { label: 'Executed', icon: '⚡' },
  stale: { label: 'Stale', icon: '⚠' },
  failed: { label: 'Failed', icon: '✗' },
};

// =============================================================================
// Component
// =============================================================================

export function DirectorStatusBadge({
  status,
  size = 'md',
  showLabel = true,
}: DirectorStatusBadgeProps) {
  const config = STATUS_CONFIG[status];

  return (
    <span
      className="director-status-badge"
      data-status={status}
      data-size={size}
      data-pulse={config.pulse || false}
      aria-label={`Status: ${config.label}`}
      role="status"
    >
      <span className="director-status-badge__icon">{config.icon}</span>
      {showLabel && <span className="director-status-badge__label">{config.label}</span>}
    </span>
  );
}
