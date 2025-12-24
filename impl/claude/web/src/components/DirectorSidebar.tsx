/**
 * DirectorSidebar — Navigation and Metrics Panel
 *
 * Extracted from DirectorDashboard to enable reusability and composition.
 *
 * Contains:
 *   - Connection status indicator
 *   - Document metrics (counts by status)
 *   - Quick status filters
 *   - Actions (Upload, Refresh)
 *   - Keyboard hints
 *
 * Philosophy: "Radical and calm, grounded. 90% steel, 10% earned glow."
 */

import type { DocumentStatus, MetricsSummary } from '../api/director';

// =============================================================================
// Types
// =============================================================================

export type StatusFilter = 'all' | DocumentStatus;

export interface DirectorSidebarProps {
  metrics: MetricsSummary | null;
  statusFilter: StatusFilter;
  onStatusFilterChange: (filter: StatusFilter) => void;
  streamConnected: boolean;
  onUpload?: () => void;
  onRefresh: () => void;
}

// Status configuration for visual consistency
const STATUS_CONFIG: Record<
  DocumentStatus | 'all',
  { label: string; key: string; accent?: string }
> = {
  all: { label: 'All', key: 'a' },
  uploaded: { label: 'Uploaded', key: 'u', accent: 'var(--status-normal)' },
  processing: { label: 'Processing', key: 'p', accent: 'var(--status-edge)' },
  ready: { label: 'Ready', key: 'r', accent: 'var(--status-insert)' },
  executed: { label: 'Executed', key: 'x', accent: 'var(--status-visual)' },
  stale: { label: 'Stale', key: 's', accent: 'var(--steel-500)' },
  failed: { label: 'Failed', key: 'f', accent: 'var(--status-error)' },
};

// =============================================================================
// Component
// =============================================================================

export function DirectorSidebar({
  metrics,
  statusFilter,
  onStatusFilterChange,
  streamConnected,
  onUpload,
  onRefresh,
}: DirectorSidebarProps) {
  return (
    <aside className="director__sidebar">
      {/* Connection status */}
      <div className="director__connection" data-connected={streamConnected}>
        <span className="director__connection-dot" />
        <span className="director__connection-label">
          {streamConnected ? 'LIVE' : 'OFFLINE'}
        </span>
      </div>

      {/* Stats */}
      <div className="director__stats">
        <div className="director__stat director__stat--primary">
          <span className="director__stat-value">{metrics?.total || 0}</span>
          <span className="director__stat-label">Documents</span>
        </div>

        {metrics &&
          Object.entries(metrics.by_status).map(([status, count]) => {
            if (count === 0) return null;
            const cfg = STATUS_CONFIG[status as DocumentStatus];
            return (
              <button
                key={status}
                className="director__stat director__stat--button"
                style={{ '--accent': cfg?.accent } as React.CSSProperties}
                onClick={() => onStatusFilterChange(status as StatusFilter)}
                data-active={statusFilter === status}
              >
                <span className="director__stat-value">{count}</span>
                <span className="director__stat-label">{cfg?.label || status}</span>
              </button>
            );
          })}
      </div>

      {/* Quick filters */}
      <div className="director__filters">
        <div className="director__filter-label">STATUS</div>
        <div className="director__filter-options">
          {Object.entries(STATUS_CONFIG).map(([key, cfg]) => (
            <button
              key={key}
              className="director__filter-btn"
              data-active={statusFilter === key}
              onClick={() => onStatusFilterChange(key as StatusFilter)}
            >
              <kbd>{cfg.key}</kbd> {cfg.label}
            </button>
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="director__actions">
        {onUpload && (
          <button className="director__action-btn director__action-btn--primary" onClick={onUpload}>
            <kbd>u</kbd> Upload
          </button>
        )}
        <button className="director__action-btn" onClick={onRefresh}>
          <kbd>r</kbd> Refresh
        </button>
      </div>

      {/* Keyboard hints */}
      <div className="director__hints">
        <div className="director__hint">
          <kbd>j</kbd>/<kbd>k</kbd> navigate
        </div>
        <div className="director__hint">
          <kbd>Enter</kbd> open
        </div>
        <div className="director__hint">
          <kbd>/</kbd> search
        </div>
        <div className="director__hint">
          <kbd>1-4</kbd> filter
        </div>
        <div className="director__hint">
          <kbd>d</kbd> delete
        </div>
        <div className="director__hint">
          <kbd>R</kbd> rename
        </div>
      </div>
    </aside>
  );
}
