/**
 * SpecLedgerDetail — Detailed view of a single spec
 *
 * Shows:
 * - Claims extracted from spec
 * - Evidence (implementations, tests)
 * - Harmonies (references, extends)
 * - Contradictions (conflicts)
 *
 * Philosophy:
 *   "Every claim needs evidence."
 */

import { useCallback, useEffect, useState } from 'react';

import { getSpecDetail, type SpecDetailResponse } from '../../api/specLedger';

import './SpecLedgerDetail.css';

// =============================================================================
// Types
// =============================================================================

interface SpecLedgerDetailProps {
  path: string;
  onNavigateToSpec?: (path: string) => void;
  onClose?: () => void;
}

// =============================================================================
// Component
// =============================================================================

export function SpecLedgerDetail({ path, onNavigateToSpec, onClose }: SpecLedgerDetailProps) {
  const [detail, setDetail] = useState<SpecDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Load spec detail
  const loadDetail = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getSpecDetail(path);
      setDetail(response);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load spec');
    } finally {
      setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    loadDetail();
  }, [loadDetail]);

  if (loading) {
    return (
      <div className="spec-ledger-detail spec-ledger-detail--loading">
        <div className="spec-ledger-detail__loader">Loading spec...</div>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="spec-ledger-detail spec-ledger-detail--error">
        <div className="spec-ledger-detail__error">
          <p>{error || 'Spec not found'}</p>
          <button onClick={onClose}>Go Back</button>
        </div>
      </div>
    );
  }

  const hasEvidence = detail.implementations.length > 0 || detail.tests.length > 0;

  return (
    <div className="spec-ledger-detail">
      {/* Header */}
      <header className="spec-ledger-detail__header">
        <button className="spec-ledger-detail__back" onClick={onClose}>
          ← Back
        </button>
        <div className="spec-ledger-detail__title-row">
          <h1 className="spec-ledger-detail__title">{detail.title}</h1>
          <span className="spec-ledger-detail__status" data-status={detail.status.toLowerCase()}>
            {detail.status}
          </span>
        </div>
        <p className="spec-ledger-detail__path">{detail.path}</p>
      </header>

      {/* Stats Bar */}
      <div className="spec-ledger-detail__stats">
        <div className="spec-ledger-detail__stat">
          <span className="spec-ledger-detail__stat-value">{detail.claims.length}</span>
          <span className="spec-ledger-detail__stat-label">Claims</span>
        </div>
        <div className="spec-ledger-detail__stat" data-has-value={hasEvidence}>
          <span className="spec-ledger-detail__stat-value">
            {detail.implementations.length + detail.tests.length}
          </span>
          <span className="spec-ledger-detail__stat-label">Evidence</span>
        </div>
        <div className="spec-ledger-detail__stat">
          <span className="spec-ledger-detail__stat-value">{detail.harmonies.length}</span>
          <span className="spec-ledger-detail__stat-label">Harmonies</span>
        </div>
        <div className="spec-ledger-detail__stat" data-alert={detail.contradictions.length > 0}>
          <span className="spec-ledger-detail__stat-value">{detail.contradictions.length}</span>
          <span className="spec-ledger-detail__stat-label">Contradictions</span>
        </div>
      </div>

      {/* Content */}
      <div className="spec-ledger-detail__content">
        {/* Claims Section */}
        <section className="spec-ledger-detail__section">
          <h2 className="spec-ledger-detail__section-title">CLAIMS</h2>
          {detail.claims.length === 0 ? (
            <p className="spec-ledger-detail__empty">No claims extracted</p>
          ) : (
            <ul className="spec-ledger-detail__claims">
              {detail.claims.map((claim, i) => (
                <li
                  key={i}
                  className="spec-ledger-detail__claim"
                  data-type={claim.type.toLowerCase()}
                >
                  <span className="spec-ledger-detail__claim-type">{claim.type}</span>
                  <span className="spec-ledger-detail__claim-subject">{claim.subject}</span>
                  <span className="spec-ledger-detail__claim-predicate">{claim.predicate}</span>
                  <span className="spec-ledger-detail__claim-line">L{claim.line}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        {/* Evidence Section */}
        <section className="spec-ledger-detail__section">
          <h2 className="spec-ledger-detail__section-title">EVIDENCE</h2>
          {!hasEvidence ? (
            <p className="spec-ledger-detail__empty spec-ledger-detail__empty--warning">
              No evidence found. This spec needs implementations or tests.
            </p>
          ) : (
            <div className="spec-ledger-detail__evidence">
              {detail.implementations.length > 0 && (
                <div className="spec-ledger-detail__evidence-group">
                  <h3 className="spec-ledger-detail__evidence-title">Implementations</h3>
                  <ul className="spec-ledger-detail__evidence-list">
                    {detail.implementations.map((impl, i) => (
                      <li key={i} className="spec-ledger-detail__evidence-item">
                        {impl}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {detail.tests.length > 0 && (
                <div className="spec-ledger-detail__evidence-group">
                  <h3 className="spec-ledger-detail__evidence-title">Tests</h3>
                  <ul className="spec-ledger-detail__evidence-list">
                    {detail.tests.map((test, i) => (
                      <li key={i} className="spec-ledger-detail__evidence-item">
                        {test}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </section>

        {/* References Section */}
        {detail.references.length > 0 && (
          <section className="spec-ledger-detail__section">
            <h2 className="spec-ledger-detail__section-title">REFERENCES</h2>
            <ul className="spec-ledger-detail__references">
              {detail.references.map((ref, i) => (
                <li key={i} className="spec-ledger-detail__reference">
                  <button
                    className="spec-ledger-detail__reference-link"
                    onClick={() => onNavigateToSpec?.(ref)}
                  >
                    {ref}
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Harmonies Section */}
        {detail.harmonies.length > 0 && (
          <section className="spec-ledger-detail__section">
            <h2 className="spec-ledger-detail__section-title">HARMONIES</h2>
            <ul className="spec-ledger-detail__harmonies">
              {detail.harmonies.map((h, i) => (
                <li key={i} className="spec-ledger-detail__harmony">
                  <button
                    className="spec-ledger-detail__harmony-link"
                    onClick={() => onNavigateToSpec?.(h.spec)}
                  >
                    {h.spec}
                  </button>
                  <span className="spec-ledger-detail__harmony-relationship">{h.relationship}</span>
                  <span className="spec-ledger-detail__harmony-strength">
                    {Math.round(h.strength * 100)}%
                  </span>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Contradictions Section */}
        {detail.contradictions.length > 0 && (
          <section className="spec-ledger-detail__section spec-ledger-detail__section--alert">
            <h2 className="spec-ledger-detail__section-title">CONTRADICTIONS</h2>
            <ul className="spec-ledger-detail__contradictions">
              {detail.contradictions.map((c, i) => (
                <li key={i} className="spec-ledger-detail__contradiction">
                  <button
                    className="spec-ledger-detail__contradiction-link"
                    onClick={() => onNavigateToSpec?.(c.spec)}
                  >
                    {c.spec}
                  </button>
                  <span className="spec-ledger-detail__contradiction-type">{c.conflict_type}</span>
                  <span
                    className="spec-ledger-detail__contradiction-severity"
                    data-severity={c.severity}
                  >
                    {c.severity}
                  </span>
                </li>
              ))}
            </ul>
          </section>
        )}
      </div>
    </div>
  );
}
