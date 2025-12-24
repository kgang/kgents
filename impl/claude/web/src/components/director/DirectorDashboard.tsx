/**
 * DirectorDashboard - Document Director overview
 *
 * Shows:
 * - Metrics by status
 * - Live activity stream via witness events
 * - Quick actions
 *
 * Philosophy:
 *   "Upload → Analyze → Generate → Execute → Capture → Verify"
 */

import { useCallback, useEffect, useState } from 'react';

import { getMetrics, type MetricsSummary } from '../../api/director';
import { useWitnessStream } from '../../hooks/useWitnessStream';

import './DirectorDashboard.css';

// =============================================================================
// Types
// =============================================================================

interface DirectorDashboardProps {
  onNavigateToDocuments?: () => void;
}

// =============================================================================
// Component
// =============================================================================

export function DirectorDashboard({ onNavigateToDocuments }: DirectorDashboardProps) {
  const [metrics, setMetrics] = useState<MetricsSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Real-time witness stream for director events
  const { events: witnessEvents, connected: streamConnected } = useWitnessStream();

  // Filter to only director events
  const directorEvents = witnessEvents
    .filter((e) => e.tags?.some((t) => t.startsWith('director.') || t === 'ingest' || t === 'analysis'))
    .slice(0, 10);

  // Load metrics
  const loadMetrics = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getMetrics();
      setMetrics(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load metrics');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadMetrics();
  }, [loadMetrics]);

  if (loading && !metrics) {
    return (
      <div className="director-dashboard director-dashboard--loading">
        <div className="director-dashboard__loader">Loading metrics...</div>
      </div>
    );
  }

  if (error && !metrics) {
    return (
      <div className="director-dashboard director-dashboard--error">
        <div className="director-dashboard__error">
          <p>{error}</p>
          <button onClick={loadMetrics}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="director-dashboard">
      {/* Header */}
      <header className="director-dashboard__header">
        <h1 className="director-dashboard__title">DOCUMENT DIRECTOR</h1>
        <button
          className="director-dashboard__action-btn"
          onClick={onNavigateToDocuments}
        >
          View All →
        </button>
      </header>

      {/* Metrics Cards */}
      {metrics && (
        <div className="director-dashboard__metrics">
          <div className="director-dashboard__metric" data-primary>
            <span className="director-dashboard__metric-value">{metrics.total}</span>
            <span className="director-dashboard__metric-label">Total Documents</span>
          </div>

          <div className="director-dashboard__metric" data-status="uploaded">
            <span className="director-dashboard__metric-value">
              {metrics.by_status.uploaded || 0}
            </span>
            <span className="director-dashboard__metric-label">Uploaded</span>
          </div>

          <div className="director-dashboard__metric" data-status="processing">
            <span className="director-dashboard__metric-value">
              {metrics.by_status.processing || 0}
            </span>
            <span className="director-dashboard__metric-label">Analyzing</span>
          </div>

          <div className="director-dashboard__metric" data-status="ready">
            <span className="director-dashboard__metric-value">
              {metrics.by_status.ready || 0}
            </span>
            <span className="director-dashboard__metric-label">Ready</span>
          </div>

          <div className="director-dashboard__metric" data-status="executed">
            <span className="director-dashboard__metric-value">
              {metrics.by_status.executed || 0}
            </span>
            <span className="director-dashboard__metric-label">Executed</span>
          </div>

          <div
            className="director-dashboard__metric"
            data-status="failed"
            data-alert={(metrics.by_status.failed || 0) > 0}
          >
            <span className="director-dashboard__metric-value">
              {metrics.by_status.failed || 0}
            </span>
            <span className="director-dashboard__metric-label">Failed</span>
          </div>
        </div>
      )}

      {/* Live Activity Stream */}
      <div className="director-dashboard__section director-dashboard__section--live">
        <h2 className="director-dashboard__section-title">
          LIVE ACTIVITY
          <span className="director-dashboard__stream-indicator" data-connected={streamConnected}>
            {streamConnected ? '● CONNECTED' : '○ DISCONNECTED'}
          </span>
        </h2>
        {directorEvents.length > 0 ? (
          <ul className="director-dashboard__activity">
            {directorEvents.map((event) => (
              <li key={event.id} className="director-dashboard__activity-item">
                <span className="director-dashboard__activity-action">{event.action}</span>
                <span className="director-dashboard__activity-time">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="director-dashboard__empty">No activity yet. Upload a document to start.</p>
        )}
      </div>

      {/* Error Toast */}
      {error && (
        <div className="director-dashboard__toast director-dashboard__toast--error">{error}</div>
      )}
    </div>
  );
}
