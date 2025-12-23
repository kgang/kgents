/**
 * LedgerDashboard — Spec corpus health overview
 *
 * Accounting-style dashboard showing:
 * - Assets: Total specs, active, claims, harmonies
 * - Liabilities: Orphans, deprecated, contradictions
 * - Recent activity (real-time via Witness stream)
 *
 * Philosophy:
 *   "Spec = Asset. Evidence = Transactions."
 *   "If proofs valid, supported. If not used, dead."
 *   "The proof IS the decision. The mark IS the witness."
 *
 * Integration:
 *   Connects to WitnessStream for real-time spec events.
 *   Every ledger mutation (scan, deprecate) appears instantly.
 */

import { useCallback, useEffect, useState } from 'react';

import { getLedger, scanCorpus, type LedgerSummary, type SpecEntry } from '../../api/specLedger';
import { useWitnessStream } from '../useWitnessStream';

import './LedgerDashboard.css';

// =============================================================================
// Types
// =============================================================================

interface LedgerDashboardProps {
  onNavigateToSpec?: (path: string) => void;
  onNavigateToOrphans?: () => void;
  onNavigateToContradictions?: () => void;
}

// =============================================================================
// Component
// =============================================================================

export function LedgerDashboard({
  onNavigateToSpec,
  onNavigateToOrphans,
  onNavigateToContradictions,
}: LedgerDashboardProps) {
  const [summary, setSummary] = useState<LedgerSummary | null>(null);
  const [recentSpecs, setRecentSpecs] = useState<SpecEntry[]>([]);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Real-time witness stream for spec events
  const { events: witnessEvents, connected: streamConnected } = useWitnessStream();

  // Filter to only spec events
  const specEvents = witnessEvents.filter((e) => e.type === 'spec').slice(0, 5);

  // Load ledger data
  const loadData = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getLedger({ sortBy: 'claims', limit: 10 });
      setSummary(response.summary);
      setRecentSpecs(response.specs || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load ledger');
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    loadData();
  }, [loadData]);

  // Handle scan
  const handleScan = useCallback(async () => {
    setScanning(true);
    try {
      await scanCorpus(true);
      await loadData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Scan failed');
    } finally {
      setScanning(false);
    }
  }, [loadData]);

  // Calculate health percentage
  const healthPercent = summary
    ? Math.round(((summary.active - summary.orphans) / summary.total_specs) * 100)
    : 0;

  if (loading && !summary) {
    return (
      <div className="ledger-dashboard ledger-dashboard--loading">
        <div className="ledger-dashboard__loader">Scanning corpus...</div>
      </div>
    );
  }

  if (error && !summary) {
    return (
      <div className="ledger-dashboard ledger-dashboard--error">
        <div className="ledger-dashboard__error">
          <p>{error}</p>
          <button onClick={loadData}>Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="ledger-dashboard">
      {/* Header */}
      <header className="ledger-dashboard__header">
        <h1 className="ledger-dashboard__title">LIVING SPEC LEDGER</h1>
        <button className="ledger-dashboard__scan-btn" onClick={handleScan} disabled={scanning}>
          {scanning ? 'Scanning...' : 'Scan Corpus'}
        </button>
      </header>

      {/* Health Bar */}
      <div className="ledger-dashboard__health">
        <div className="ledger-dashboard__health-bar">
          <div
            className="ledger-dashboard__health-fill"
            style={{ width: `${healthPercent}%` }}
            data-health={healthPercent > 70 ? 'good' : healthPercent > 40 ? 'warn' : 'bad'}
          />
        </div>
        <span className="ledger-dashboard__health-label">{healthPercent}% healthy</span>
      </div>

      {/* Summary Cards */}
      {summary && (
        <div className="ledger-dashboard__cards">
          {/* Assets */}
          <div className="ledger-dashboard__card ledger-dashboard__card--assets">
            <h2 className="ledger-dashboard__card-title">ASSETS</h2>
            <div className="ledger-dashboard__card-grid">
              <div className="ledger-dashboard__stat">
                <span className="ledger-dashboard__stat-value">{summary.total_specs}</span>
                <span className="ledger-dashboard__stat-label">Total Specs</span>
              </div>
              <div className="ledger-dashboard__stat">
                <span className="ledger-dashboard__stat-value">{summary.active}</span>
                <span className="ledger-dashboard__stat-label">Active</span>
              </div>
              <div className="ledger-dashboard__stat">
                <span className="ledger-dashboard__stat-value">{summary.total_claims}</span>
                <span className="ledger-dashboard__stat-label">Claims</span>
              </div>
              <div className="ledger-dashboard__stat">
                <span className="ledger-dashboard__stat-value">{summary.harmonies}</span>
                <span className="ledger-dashboard__stat-label">Harmonies</span>
              </div>
            </div>
          </div>

          {/* Liabilities */}
          <div className="ledger-dashboard__card ledger-dashboard__card--liabilities">
            <h2 className="ledger-dashboard__card-title">LIABILITIES</h2>
            <div className="ledger-dashboard__card-grid">
              <button
                className="ledger-dashboard__stat ledger-dashboard__stat--clickable"
                onClick={onNavigateToOrphans}
                data-alert={summary.orphans > 50}
              >
                <span className="ledger-dashboard__stat-value">{summary.orphans}</span>
                <span className="ledger-dashboard__stat-label">Orphans</span>
              </button>
              <div className="ledger-dashboard__stat">
                <span className="ledger-dashboard__stat-value">{summary.deprecated}</span>
                <span className="ledger-dashboard__stat-label">Deprecated</span>
              </div>
              <button
                className="ledger-dashboard__stat ledger-dashboard__stat--clickable"
                onClick={onNavigateToContradictions}
                data-alert={summary.contradictions > 0}
              >
                <span className="ledger-dashboard__stat-value">{summary.contradictions}</span>
                <span className="ledger-dashboard__stat-label">Contradictions</span>
              </button>
              <div className="ledger-dashboard__stat">
                <span className="ledger-dashboard__stat-value">{summary.archived}</span>
                <span className="ledger-dashboard__stat-label">Archived</span>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Live Activity Stream */}
      <div className="ledger-dashboard__section ledger-dashboard__section--live">
        <h2 className="ledger-dashboard__section-title">
          LIVE ACTIVITY
          <span className="ledger-dashboard__stream-indicator" data-connected={streamConnected}>
            {streamConnected ? '● CONNECTED' : '○ DISCONNECTED'}
          </span>
        </h2>
        {specEvents.length > 0 ? (
          <ul className="ledger-dashboard__activity">
            {specEvents.map((event) => (
              <li key={event.id} className="ledger-dashboard__activity-item">
                <span className="ledger-dashboard__activity-action">
                  {event.specAction === 'scan' && '🔍 Scanned corpus'}
                  {event.specAction === 'deprecate' &&
                    `⚠️ Deprecated ${event.specPaths?.length || 0} specs`}
                  {event.specAction === 'evidence_added' && '✓ Evidence added'}
                  {!event.specAction && event.action}
                </span>
                <span className="ledger-dashboard__activity-time">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </span>
              </li>
            ))}
          </ul>
        ) : (
          <p className="ledger-dashboard__empty">No activity yet. Click "Scan Corpus" to start.</p>
        )}
      </div>

      {/* Top Specs by Claims */}
      <div className="ledger-dashboard__section">
        <h2 className="ledger-dashboard__section-title">TOP SPECS BY CLAIMS</h2>
        <table className="ledger-dashboard__table">
          <thead>
            <tr>
              <th>Path</th>
              <th>Status</th>
              <th>Claims</th>
              <th>Impl</th>
              <th>Tests</th>
            </tr>
          </thead>
          <tbody>
            {recentSpecs.map((spec) => (
              <tr
                key={spec.path}
                className="ledger-dashboard__row"
                onClick={() => onNavigateToSpec?.(spec.path)}
                data-status={spec.status.toLowerCase()}
              >
                <td className="ledger-dashboard__cell-path">{spec.path}</td>
                <td>
                  <span
                    className="ledger-dashboard__status"
                    data-status={spec.status.toLowerCase()}
                  >
                    {spec.status}
                  </span>
                </td>
                <td className="ledger-dashboard__cell-num">{spec.claim_count}</td>
                <td className="ledger-dashboard__cell-num">{spec.impl_count}</td>
                <td className="ledger-dashboard__cell-num">{spec.test_count}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Error Toast */}
      {error && (
        <div className="ledger-dashboard__toast ledger-dashboard__toast--error">{error}</div>
      )}
    </div>
  );
}
