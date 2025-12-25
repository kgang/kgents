/**
 * DocumentStatus - Status badge component
 *
 * Renders document lifecycle status with appropriate icon and color.
 */

import type { DocumentStatus } from '../../api/director';

import './DocumentStatus.css';

// =============================================================================
// Types
// =============================================================================

interface StatusConfig {
  label: string;
  color: string;
  icon: string;
  spin?: boolean;
}

interface DocumentStatusBadgeProps {
  status: DocumentStatus | string;  // Accept any status string for flexibility
  size?: 'sm' | 'md';
}

// =============================================================================
// Config
// =============================================================================

// Maps both frontend DocumentStatus values AND backend AnalysisStatus values
const STATUS_CONFIG: Record<string, StatusConfig> = {
  // Frontend statuses (DocumentStatus)
  uploaded: { label: 'Uploaded', color: 'blue', icon: '↑' },
  processing: { label: 'Analyzing', color: 'yellow', icon: '⟳', spin: true },
  ready: { label: 'Ready', color: 'green', icon: '✓' },
  executed: { label: 'Executed', color: 'purple', icon: '⊛' },
  stale: { label: 'Stale', color: 'orange', icon: '!' },
  failed: { label: 'Failed', color: 'red', icon: '✗' },
  // Ghost: the negative space of the graph
  ghost: { label: 'Ghost', color: 'ghost', icon: '◭' },

  // Backend statuses (AnalysisStatus from services/sovereign/analysis.py)
  pending: { label: 'Pending', color: 'gray', icon: '○' },
  analyzing: { label: 'Analyzing', color: 'yellow', icon: '⟳', spin: true },
  analyzed: { label: 'Analyzed', color: 'green', icon: '✓' },
};

// Default config for unknown statuses
const DEFAULT_CONFIG: StatusConfig = { label: 'Unknown', color: 'gray', icon: '?' };

// =============================================================================
// Component
// =============================================================================

export function DocumentStatusBadge({ status, size = 'md' }: DocumentStatusBadgeProps) {
  const config = STATUS_CONFIG[status] ?? DEFAULT_CONFIG;

  return (
    <span className="document-status" data-status={status} data-size={size}>
      <span className="document-status__icon" data-spin={config.spin}>
        {config.icon}
      </span>
      <span className="document-status__label">{config.label}</span>
    </span>
  );
}
