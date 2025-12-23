/**
 * SpecLedgerDetail — Detailed view of a single spec
 *
 * Shows:
 * - Claims extracted from spec
 * - Evidence (implementations, tests) - both discovered and declared
 * - Witness marks (declared evidence from evidence-as-marks system)
 * - Harmonies (references, extends)
 * - Contradictions (conflicts)
 *
 * Philosophy:
 *   "Every claim needs evidence."
 *   "The mark IS the witness."
 */

import { useCallback, useEffect, useState } from 'react';

import {
  addEvidence,
  getSpecDetail,
  queryEvidence,
  verifyEvidence,
  type EvidenceMark,
  type EvidenceQueryResponse,
  type EvidenceType,
  type EvidenceVerifyResponse,
  type SpecDetailResponse,
} from '../../api/specLedger';

import './SpecLedgerDetail.css';

// =============================================================================
// Types
// =============================================================================

interface SpecLedgerDetailProps {
  path: string;
  onNavigateToSpec?: (path: string) => void;
  onEditInEditor?: (path: string) => void;
  onClose?: () => void;
}

interface AddEvidenceModalProps {
  specPath: string;
  onClose: () => void;
  onSuccess: () => void;
}

// =============================================================================
// AddEvidence Modal
// =============================================================================

function AddEvidenceModal({ specPath, onClose, onSuccess }: AddEvidenceModalProps) {
  const [evidencePath, setEvidencePath] = useState('');
  const [evidenceType, setEvidenceType] = useState<EvidenceType>('implementation');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!evidencePath.trim()) return;

    setSubmitting(true);
    setError(null);

    try {
      await addEvidence(specPath, evidencePath.trim(), evidenceType);
      onSuccess();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to add evidence');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="spec-ledger-detail__modal-overlay" onClick={onClose}>
      <div className="spec-ledger-detail__modal" onClick={(e) => e.stopPropagation()}>
        <h3 className="spec-ledger-detail__modal-title">Add Evidence</h3>
        <p className="spec-ledger-detail__modal-subtitle">
          Link evidence to <code>{specPath}</code>
        </p>

        <form onSubmit={handleSubmit}>
          <div className="spec-ledger-detail__modal-field">
            <label htmlFor="evidencePath">Evidence File Path</label>
            <input
              id="evidencePath"
              type="text"
              value={evidencePath}
              onChange={(e) => setEvidencePath(e.target.value)}
              placeholder="e.g., services/living_spec/ledger_node.py"
              disabled={submitting}
            />
          </div>

          <div className="spec-ledger-detail__modal-field">
            <label htmlFor="evidenceType">Evidence Type</label>
            <select
              id="evidenceType"
              value={evidenceType}
              onChange={(e) => setEvidenceType(e.target.value as EvidenceType)}
              disabled={submitting}
            >
              <option value="implementation">Implementation</option>
              <option value="test">Test</option>
              <option value="usage">Usage</option>
            </select>
          </div>

          {error && <p className="spec-ledger-detail__modal-error">{error}</p>}

          <div className="spec-ledger-detail__modal-actions">
            <button type="button" onClick={onClose} disabled={submitting}>
              Cancel
            </button>
            <button type="submit" disabled={submitting || !evidencePath.trim()}>
              {submitting ? 'Adding...' : 'Add Evidence'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

// =============================================================================
// EvidenceMarks Section
// =============================================================================

interface EvidenceMarksSectionProps {
  marks: EvidenceMark[];
  verification: EvidenceVerifyResponse | null;
  onVerify: () => void;
  verifying: boolean;
}

function EvidenceMarksSection({
  marks,
  verification,
  onVerify,
  verifying,
}: EvidenceMarksSectionProps) {
  if (marks.length === 0) {
    return null;
  }

  // Build a map of file_path -> status from verification
  const statusByFile: Record<string, 'valid' | 'stale' | 'broken'> = {};
  if (verification?.results) {
    for (const r of verification.results) {
      statusByFile[r.file_path] = r.status;
    }
  }

  // Extract file path from mark tags
  const getFilePath = (mark: EvidenceMark): string | null => {
    for (const tag of mark.tags) {
      if (tag.startsWith('file:')) return tag.slice(5);
    }
    return null;
  };

  // Get evidence type from mark tags
  const getEvidenceType = (mark: EvidenceMark): string | null => {
    for (const tag of mark.tags) {
      if (tag.startsWith('evidence:')) return tag.slice(9);
    }
    return null;
  };

  return (
    <div className="spec-ledger-detail__evidence-marks">
      <div className="spec-ledger-detail__evidence-marks-header">
        <h3 className="spec-ledger-detail__evidence-title">Declared Evidence (Witness Marks)</h3>
        <button className="spec-ledger-detail__verify-btn" onClick={onVerify} disabled={verifying}>
          {verifying ? 'Verifying...' : 'Verify All'}
        </button>
      </div>

      {verification && (
        <div className="spec-ledger-detail__verification-summary">
          <span className="spec-ledger-detail__verification-stat" data-status="valid">
            ✓ {verification.valid} valid
          </span>
          {verification.broken > 0 && (
            <span className="spec-ledger-detail__verification-stat" data-status="broken">
              ✗ {verification.broken} broken
            </span>
          )}
        </div>
      )}

      <ul className="spec-ledger-detail__evidence-marks-list">
        {marks.map((mark) => {
          const filePath = getFilePath(mark);
          const evidenceType = getEvidenceType(mark);
          const status = filePath ? statusByFile[filePath] : undefined;

          return (
            <li
              key={mark.mark_id}
              className="spec-ledger-detail__evidence-mark"
              data-status={status}
            >
              <span className="spec-ledger-detail__evidence-mark-type" data-type={evidenceType}>
                {evidenceType || 'evidence'}
              </span>
              <span className="spec-ledger-detail__evidence-mark-path">
                {filePath || mark.action}
              </span>
              <span className="spec-ledger-detail__evidence-mark-author">{mark.author}</span>
              {status && (
                <span className="spec-ledger-detail__evidence-mark-status" data-status={status}>
                  {status === 'valid' ? '✓' : '✗'}
                </span>
              )}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

// =============================================================================
// Main Component
// =============================================================================

// eslint-disable-next-line complexity
export function SpecLedgerDetail({
  path,
  onNavigateToSpec,
  onEditInEditor,
  onClose,
}: SpecLedgerDetailProps) {
  const [detail, setDetail] = useState<SpecDetailResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Evidence marks state
  const [evidenceMarks, setEvidenceMarks] = useState<EvidenceQueryResponse | null>(null);
  const [verification, setVerification] = useState<EvidenceVerifyResponse | null>(null);
  const [verifying, setVerifying] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);

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

  // Load evidence marks
  const loadEvidenceMarks = useCallback(async () => {
    try {
      const response = await queryEvidence(path);
      setEvidenceMarks(response);
    } catch (err) {
      console.error('Failed to load evidence marks:', err);
    }
  }, [path]);

  // Verify evidence
  const handleVerify = useCallback(async () => {
    setVerifying(true);
    try {
      const response = await verifyEvidence(path);
      setVerification(response);
    } catch (err) {
      console.error('Failed to verify evidence:', err);
    } finally {
      setVerifying(false);
    }
  }, [path]);

  // Handle evidence added successfully
  const handleEvidenceAdded = useCallback(() => {
    loadDetail();
    loadEvidenceMarks();
    setVerification(null); // Reset verification after adding new evidence
  }, [loadDetail, loadEvidenceMarks]);

  useEffect(() => {
    loadDetail();
    loadEvidenceMarks();
  }, [loadDetail, loadEvidenceMarks]);

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
        <div className="spec-ledger-detail__header-nav">
          <button className="spec-ledger-detail__back" onClick={onClose}>
            ← Back
          </button>
          {onEditInEditor && (
            <button
              className="spec-ledger-detail__edit-btn"
              onClick={() => onEditInEditor(path)}
              title="Open in Editor"
            >
              ⌨ Edit
            </button>
          )}
        </div>
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
          <div className="spec-ledger-detail__section-header">
            <h2 className="spec-ledger-detail__section-title">EVIDENCE</h2>
            <button
              className="spec-ledger-detail__add-evidence-btn"
              onClick={() => setShowAddModal(true)}
            >
              + Add Evidence
            </button>
          </div>

          {/* Discovered Evidence (from file analysis) */}
          {!hasEvidence && !evidenceMarks?.marks.length ? (
            <p className="spec-ledger-detail__empty spec-ledger-detail__empty--warning">
              No evidence found. This spec needs implementations or tests.
            </p>
          ) : (
            <div className="spec-ledger-detail__evidence">
              {detail.implementations.length > 0 && (
                <div className="spec-ledger-detail__evidence-group">
                  <h3 className="spec-ledger-detail__evidence-title">Discovered Implementations</h3>
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
                  <h3 className="spec-ledger-detail__evidence-title">Discovered Tests</h3>
                  <ul className="spec-ledger-detail__evidence-list">
                    {detail.tests.map((test, i) => (
                      <li key={i} className="spec-ledger-detail__evidence-item">
                        {test}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Declared Evidence (from witness marks) */}
              {evidenceMarks && evidenceMarks.marks.length > 0 && (
                <EvidenceMarksSection
                  marks={evidenceMarks.marks}
                  verification={verification}
                  onVerify={handleVerify}
                  verifying={verifying}
                />
              )}
            </div>
          )}
        </section>

        {/* Add Evidence Modal */}
        {showAddModal && (
          <AddEvidenceModal
            specPath={detail.path}
            onClose={() => setShowAddModal(false)}
            onSuccess={handleEvidenceAdded}
          />
        )}

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
