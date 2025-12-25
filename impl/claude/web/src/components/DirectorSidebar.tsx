/**
 * DirectorSidebar — Navigation and Metrics Panel
 *
 * Extracted from DirectorDashboard to enable reusability and composition.
 *
 * Contains:
 *   - Connection status indicator with last update time
 *   - Document metrics (counts by status)
 *   - Quick status filters with count badges
 *   - Actions (Upload, Reconnect)
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
  onReconnect?: () => void;
  lastEventTime?: Date | null;
  isReconnecting?: boolean;
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
  ghost: { label: 'Ghost', key: 'g', accent: 'var(--steel-400)' },
};

// =============================================================================
// Helpers
// =============================================================================

/**
 * Format relative time: "just now", "5m ago", "2h ago", etc.
 */
function formatRelativeTime(date: Date | null): string {
  if (!date) return '';

  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const seconds = Math.floor(diff / 1000);
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);

  if (seconds < 10) return 'just now';
  if (seconds < 60) return `${seconds}s ago`;
  if (minutes < 60) return `${minutes}m ago`;
  if (hours < 24) return `${hours}h ago`;
  if (days < 7) return `${days}d ago`;
  return date.toLocaleDateString();
}

// =============================================================================
// Component
// =============================================================================

export function DirectorSidebar({
  metrics,
  statusFilter,
  onStatusFilterChange,
  streamConnected,
  onUpload,
  onReconnect,
  lastEventTime,
  isReconnecting = false,
}: DirectorSidebarProps) {
  return (
    <aside className="director__sidebar">
      {/* Connection status */}
      <div className="director__connection" data-connected={streamConnected}>
        <div className="flex items-center gap-2">
          <span className="director__connection-dot" />
          <span className="director__connection-label">
            {streamConnected ? 'LIVE' : 'OFFLINE'}
          </span>
        </div>
        {streamConnected && lastEventTime && (
          <span className="text-xs text-steel-500">
            {formatRelativeTime(lastEventTime)}
          </span>
        )}
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
          {Object.entries(STATUS_CONFIG).map(([key, cfg]) => {
            const count = key === 'all'
              ? metrics?.total || 0
              : metrics?.by_status[key as DocumentStatus] || 0;

            return (
              <button
                key={key}
                className="director__filter-btn"
                data-active={statusFilter === key}
                onClick={() => onStatusFilterChange(key as StatusFilter)}
              >
                <span className="flex items-center gap-2 flex-1">
                  <span>{cfg.label}</span>
                  <span className="ml-auto text-xs px-1.5 py-0.5 bg-steel-800 rounded-full tabular-nums">
                    {count}
                  </span>
                </span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Actions */}
      <div className="director__actions">
        {onUpload && (
          <button className="director__action-btn director__action-btn--primary" onClick={onUpload}>
            <kbd>u</kbd> Upload
          </button>
        )}
      </div>

      {/* Reconnect prompt - only shown when disconnected */}
      {!streamConnected && onReconnect && (
        <div className="p-3 bg-steel-850 border border-steel-700 rounded text-sm">
          <p className="text-steel-400 mb-2">Stream disconnected</p>
          <button
            className="w-full px-3 py-1.5 bg-purple-600 border-none rounded text-white text-xs font-medium transition-all hover:brightness-110 disabled:opacity-50 disabled:cursor-not-allowed"
            onClick={onReconnect}
            disabled={isReconnecting}
          >
            {isReconnecting ? 'Reconnecting...' : 'Reconnect'}
          </button>
        </div>
      )}

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
          <kbd>1-4</kbd> quick filter
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
