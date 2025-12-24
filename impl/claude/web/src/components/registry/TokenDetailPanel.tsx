/**
 * TokenDetailPanel - Slide-out detail view
 *
 * Shows:
 * - Full path
 * - Status badge
 * - Stats (claims, impl, test)
 * - Harmonies/relationships
 * - Actions (open editor, view ledger)
 *
 * "The frame is humble. The content glows."
 */

import { useCallback, useEffect, useState } from 'react';
import { getSpecDetail, type SpecDetailResponse } from '../../api/specLedger';
import { TIER_LABELS, TIER_COLORS, detectTier, getTierIcon } from './types';

import './TokenDetailPanel.css';

// =============================================================================
// Types
// =============================================================================

interface TokenDetailPanelProps {
  path: string;
  onClose: () => void;
  onOpenEditor?: (path: string) => void;
}

// =============================================================================
// Component
// =============================================================================

export function TokenDetailPanel({ path, onClose, onOpenEditor }: TokenDetailPanelProps) {
  const [detail, setDetail] = useState<SpecDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch detail
  useEffect(() => {
    let mounted = true;

    async function fetchDetail() {
      setLoading(true);
      setError(null);

      try {
        const response = await getSpecDetail(path);
        if (mounted) {
          setDetail(response);
        }
      } catch (err) {
        if (mounted) {
          setError(err instanceof Error ? err.message : 'Failed to load detail');
        }
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    fetchDetail();
    return () => {
      mounted = false;
    };
  }, [path]);

  // Handle escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onClose();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [onClose]);

  const handleOpenEditor = useCallback(() => {
    onOpenEditor?.(path);
    onClose();
  }, [path, onOpenEditor, onClose]);

  const tier = detectTier(path);
  const tierColor = TIER_COLORS[tier];
  const tierIcon = getTierIcon(tier);
  const tierLabel = TIER_LABELS[tier];

  // Extract name from path
  const name = path.split('/').pop()?.replace(/\.(md|py|ts|tsx)$/, '') || path;

  return (
    <div className="token-detail-overlay" onClick={onClose}>
      <div
        className="token-detail-panel"
        onClick={(e) => e.stopPropagation()}
        style={{ '--panel-accent': tierColor } as React.CSSProperties}
      >
        {/* Header */}
        <header className="token-detail-panel__header">
          <button className="token-detail-panel__back" onClick={onClose}>
            ← Back
          </button>
          {onOpenEditor && (
            <button className="token-detail-panel__edit" onClick={handleOpenEditor}>
              Edit
            </button>
          )}
        </header>

        {/* Title */}
        <div className="token-detail-panel__title-row">
          <span className="token-detail-panel__icon">{tierIcon}</span>
          <h2 className="token-detail-panel__title">{detail?.title || name}</h2>
        </div>

        <p className="token-detail-panel__path">{path}</p>

        {/* Status Badge */}
        {detail && (
          <span
            className="token-detail-panel__status"
            data-status={detail.status.toLowerCase()}
          >
            {detail.status}
          </span>
        )}

        {/* Loading / Error States */}
        {loading && (
          <div className="token-detail-panel__loading">
            <span className="token-detail-panel__loading-icon">◈</span>
            <span>Loading...</span>
          </div>
        )}

        {error && (
          <div className="token-detail-panel__error">
            <p>{error}</p>
          </div>
        )}

        {/* Content */}
        {detail && !loading && (
          <div className="token-detail-panel__content">
            {/* Stats */}
            <section className="token-detail-panel__section">
              <h3 className="token-detail-panel__section-title">STATS</h3>
              <div className="token-detail-panel__stats">
                <div className="token-detail-panel__stat">
                  <span className="token-detail-panel__stat-value">{detail.claims.length}</span>
                  <span className="token-detail-panel__stat-label">claims</span>
                </div>
                <div className="token-detail-panel__stat">
                  <span className="token-detail-panel__stat-value">
                    {detail.implementations.length}
                  </span>
                  <span className="token-detail-panel__stat-label">impl</span>
                </div>
                <div className="token-detail-panel__stat">
                  <span className="token-detail-panel__stat-value">{detail.tests.length}</span>
                  <span className="token-detail-panel__stat-label">test</span>
                </div>
              </div>
              <p className="token-detail-panel__meta">
                {detail.word_count} words · {detail.heading_count} headings · Tier: {tierLabel}
              </p>
            </section>

            {/* Harmonies */}
            {detail.harmonies.length > 0 && (
              <section className="token-detail-panel__section">
                <h3 className="token-detail-panel__section-title">HARMONIES</h3>
                <ul className="token-detail-panel__list">
                  {detail.harmonies.slice(0, 5).map((h, i) => (
                    <li key={i} className="token-detail-panel__list-item">
                      <span className="token-detail-panel__list-arrow">→</span>
                      <span className="token-detail-panel__list-text">{h.spec}</span>
                      <span className="token-detail-panel__list-relation">({h.relationship})</span>
                    </li>
                  ))}
                  {detail.harmonies.length > 5 && (
                    <li className="token-detail-panel__list-more">
                      +{detail.harmonies.length - 5} more
                    </li>
                  )}
                </ul>
              </section>
            )}

            {/* Contradictions */}
            {detail.contradictions.length > 0 && (
              <section className="token-detail-panel__section">
                <h3 className="token-detail-panel__section-title token-detail-panel__section-title--warning">
                  CONTRADICTIONS
                </h3>
                <ul className="token-detail-panel__list">
                  {detail.contradictions.map((c, i) => (
                    <li key={i} className="token-detail-panel__list-item token-detail-panel__list-item--warning">
                      <span className="token-detail-panel__list-arrow">!</span>
                      <span className="token-detail-panel__list-text">{c.spec}</span>
                      <span className="token-detail-panel__list-relation">({c.conflict_type})</span>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Claims preview */}
            {detail.claims.length > 0 && (
              <section className="token-detail-panel__section">
                <h3 className="token-detail-panel__section-title">CLAIMS</h3>
                <ul className="token-detail-panel__claims">
                  {detail.claims.slice(0, 5).map((claim, i) => (
                    <li key={i} className="token-detail-panel__claim">
                      <span className="token-detail-panel__claim-type">{claim.type}</span>
                      <span className="token-detail-panel__claim-text">
                        {claim.subject} {claim.predicate}
                      </span>
                    </li>
                  ))}
                  {detail.claims.length > 5 && (
                    <li className="token-detail-panel__list-more">
                      +{detail.claims.length - 5} more claims
                    </li>
                  )}
                </ul>
              </section>
            )}
          </div>
        )}

        {/* Actions */}
        <footer className="token-detail-panel__actions">
          {onOpenEditor && (
            <button
              className="token-detail-panel__action-btn token-detail-panel__action-btn--primary"
              onClick={handleOpenEditor}
            >
              Open Editor
            </button>
          )}
        </footer>
      </div>
    </div>
  );
}
