/**
 * DocumentDetail - Detailed view of a single document
 *
 * Shows:
 * - First-view modal summarizing extraction (on first open after analysis)
 * - Full analysis crystal: claims, refs, placeholders, anticipated
 * - Evidence panel showing linked marks
 * - Delete buttons for claims, evidence, references (tracked with marks)
 * - Collapsible edit history/ledger section
 * - Prompt preview with copy button
 * - Capture form for execution results
 */

import { useCallback, useEffect, useState } from 'react';

import {
  generatePrompt,
  getDocument,
  getDocumentHistory,
  captureExecution,
  deleteItem,
  type DocumentDetail as DocumentDetailType,
  type ExecutionPrompt,
  type CaptureRequest,
  type DocumentHistoryEntry,
  type ClaimDetail,
  type EvidenceMark,
} from '../../api/director';

import { DocumentStatusBadge } from './DocumentStatus';

import './DocumentDetail.css';

// =============================================================================
// Types
// =============================================================================

interface DocumentDetailProps {
  path: string;
  onClose?: () => void;
  onEdit?: (path: string) => void;
}

// Local storage key for tracking viewed documents
const VIEWED_DOCS_KEY = 'kgents:viewed-docs';

function getViewedDocs(): Set<string> {
  try {
    const stored = localStorage.getItem(VIEWED_DOCS_KEY);
    return stored ? new Set(JSON.parse(stored)) : new Set();
  } catch {
    return new Set();
  }
}

function markAsViewed(path: string): void {
  try {
    const viewed = getViewedDocs();
    viewed.add(path);
    localStorage.setItem(VIEWED_DOCS_KEY, JSON.stringify([...viewed]));
  } catch {
    // Ignore storage errors
  }
}

function hasBeenViewed(path: string): boolean {
  return getViewedDocs().has(path);
}

// =============================================================================
// Component
// =============================================================================

export function DocumentDetail({ path, onClose, onEdit }: DocumentDetailProps) {
  const [detail, setDetail] = useState<DocumentDetailType | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // First-view modal state
  const [showFirstViewModal, setShowFirstViewModal] = useState(false);

  // Prompt state
  const [prompt, setPrompt] = useState<ExecutionPrompt | null>(null);
  const [promptLoading, setPromptLoading] = useState(false);
  const [showPrompt, setShowPrompt] = useState(false);

  // Capture state
  const [showCapture, setShowCapture] = useState(false);
  const [captureData, setCaptureData] = useState<string>('');
  const [capturing, setCapturing] = useState(false);

  // Edit history state
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const [history, setHistory] = useState<DocumentHistoryEntry[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);

  // Delete state
  const [deleting, setDeleting] = useState<string | null>(null);

  // Load document detail
  const loadDetail = useCallback(async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await getDocument(path);
      setDetail(response);

      // Check if this is the first view after analysis
      if (response.analysis && response.analyzed_at && !hasBeenViewed(path)) {
        setShowFirstViewModal(true);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load document');
    } finally {
      setLoading(false);
    }
  }, [path]);

  useEffect(() => {
    loadDetail();
  }, [loadDetail]);

  // Load history when expanded
  useEffect(() => {
    if (historyExpanded && history.length === 0 && !historyLoading) {
      setHistoryLoading(true);
      getDocumentHistory(path)
        .then((response) => {
          // Combine API history with local timeline
          const entries: DocumentHistoryEntry[] = [...response.entries];

          // Add upload entry if not present
          if (response.uploaded_at) {
            const hasUpload = entries.some((e) => e.action.toLowerCase().includes('upload'));
            if (!hasUpload) {
              entries.push({
                id: 'upload',
                action: 'Document uploaded',
                author: 'system',
                timestamp: response.uploaded_at,
              });
            }
          }

          // Add analysis entry if not present
          if (response.analyzed_at) {
            const hasAnalysis = entries.some((e) => e.action.toLowerCase().includes('analy'));
            if (!hasAnalysis) {
              entries.push({
                id: 'analysis',
                action: 'Analysis completed',
                author: 'system',
                timestamp: response.analyzed_at,
              });
            }
          }

          // Sort by timestamp descending
          entries.sort(
            (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          );

          setHistory(entries);
        })
        .catch((err) => {
          console.error('[DocumentDetail] Failed to load history:', err);
          // Create minimal history from document metadata
          const fallbackHistory: DocumentHistoryEntry[] = [];
          if (detail?.uploaded_at) {
            fallbackHistory.push({
              id: 'upload',
              action: 'Document uploaded',
              author: 'system',
              timestamp: detail.uploaded_at,
            });
          }
          if (detail?.analyzed_at) {
            fallbackHistory.push({
              id: 'analysis',
              action: 'Analysis completed',
              author: 'system',
              timestamp: detail.analyzed_at,
            });
          }
          fallbackHistory.sort(
            (a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
          );
          setHistory(fallbackHistory);
        })
        .finally(() => setHistoryLoading(false));
    }
  }, [historyExpanded, history.length, historyLoading, path, detail]);

  // Dismiss first-view modal
  const handleDismissFirstView = useCallback(() => {
    setShowFirstViewModal(false);
    markAsViewed(path);
  }, [path]);

  // Generate prompt
  const handleGeneratePrompt = useCallback(async () => {
    setPromptLoading(true);
    try {
      const response = await generatePrompt(path);
      setPrompt(response);
      setShowPrompt(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate prompt');
    } finally {
      setPromptLoading(false);
    }
  }, [path]);

  // Copy prompt to clipboard
  const handleCopyPrompt = useCallback(() => {
    if (!prompt) return;

    const text = `# Specification: ${prompt.spec_path}\n\n${prompt.spec_content}\n\n## Implementation Targets\n\n${prompt.targets.map((t) => `- ${t}`).join('\n')}\n\n## Context\n\nClaims: ${prompt.context.claims.length}\nExisting refs: ${prompt.context.existing_refs.length}`;

    navigator.clipboard.writeText(text);
  }, [prompt]);

  // Handle capture
  const handleCapture = useCallback(async () => {
    if (!captureData.trim()) return;

    setCapturing(true);
    try {
      const parsed = JSON.parse(captureData) as CaptureRequest;
      await captureExecution(parsed);
      setShowCapture(false);
      setCaptureData('');
      await loadDetail();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to capture execution');
    } finally {
      setCapturing(false);
    }
  }, [captureData, loadDetail]);

  // Handle delete claim
  const handleDeleteClaim = useCallback(
    async (claim: ClaimDetail, index: number) => {
      const itemId = `claim-${index}-L${claim.line}`;
      if (deleting) return;

      // eslint-disable-next-line no-alert
      if (!window.confirm(`Delete claim "${claim.subject} ${claim.predicate}"?`)) return;

      setDeleting(itemId);
      try {
        await deleteItem(path, {
          item_type: 'claim',
          item_id: itemId,
          reason: `User deleted claim: ${claim.type} - ${claim.subject}`,
        });
        await loadDetail();
        // Refresh history if expanded
        if (historyExpanded) {
          setHistory([]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete claim');
      } finally {
        setDeleting(null);
      }
    },
    [path, deleting, loadDetail, historyExpanded]
  );

  // Handle delete evidence
  const handleDeleteEvidence = useCallback(
    async (mark: EvidenceMark) => {
      if (deleting) return;

      // eslint-disable-next-line no-alert
      if (!window.confirm(`Delete evidence "${mark.action}"?`)) return;

      setDeleting(mark.mark_id);
      try {
        await deleteItem(path, {
          item_type: 'evidence',
          item_id: mark.mark_id,
          reason: `User deleted evidence: ${mark.action}`,
        });
        await loadDetail();
        if (historyExpanded) {
          setHistory([]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete evidence');
      } finally {
        setDeleting(null);
      }
    },
    [path, deleting, loadDetail, historyExpanded]
  );

  // Handle delete reference
  const handleDeleteReference = useCallback(
    async (ref: string, index: number) => {
      const itemId = `ref-${index}`;
      if (deleting) return;

      // eslint-disable-next-line no-alert
      if (!window.confirm(`Delete reference "${ref}"?`)) return;

      setDeleting(itemId);
      try {
        await deleteItem(path, {
          item_type: 'reference',
          item_id: itemId,
          reason: `User deleted reference: ${ref}`,
        });
        await loadDetail();
        if (historyExpanded) {
          setHistory([]);
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to delete reference');
      } finally {
        setDeleting(null);
      }
    },
    [path, deleting, loadDetail, historyExpanded]
  );

  if (loading) {
    return (
      <div className="document-detail document-detail--loading">
        <div className="document-detail__loader">Loading document...</div>
      </div>
    );
  }

  if (error || !detail) {
    return (
      <div className="document-detail document-detail--error">
        <div className="document-detail__error">
          <p>{error || 'Document not found'}</p>
          <button onClick={onClose}>Go Back</button>
        </div>
      </div>
    );
  }

  const hasAnalysis = detail.analysis !== null;

  return (
    <div className="document-detail">
      {/* First-View Modal */}
      {showFirstViewModal && detail.analysis && (
        <div className="document-detail__modal-overlay" onClick={handleDismissFirstView}>
          <div
            className="document-detail__modal document-detail__first-view-modal"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="document-detail__first-view-header">
              <span className="document-detail__first-view-icon">✨</span>
              <h3 className="document-detail__modal-title">Analysis Complete</h3>
            </div>

            <p className="document-detail__first-view-subtitle">
              Here's what was extracted from <strong>{detail.title}</strong>
            </p>

            <div className="document-detail__first-view-summary">
              <div className="document-detail__first-view-stat">
                <span className="document-detail__first-view-stat-value">
                  {detail.analysis.claims.length}
                </span>
                <span className="document-detail__first-view-stat-label">Claims</span>
              </div>
              <div className="document-detail__first-view-stat">
                <span className="document-detail__first-view-stat-value">
                  {detail.analysis.discovered_refs.length}
                </span>
                <span className="document-detail__first-view-stat-label">References</span>
              </div>
              <div className="document-detail__first-view-stat">
                <span className="document-detail__first-view-stat-value">
                  {detail.analysis.anticipated.length}
                </span>
                <span className="document-detail__first-view-stat-label">Anticipated</span>
              </div>
              <div className="document-detail__first-view-stat">
                <span className="document-detail__first-view-stat-value">
                  {detail.analysis.placeholder_paths.length}
                </span>
                <span className="document-detail__first-view-stat-label">Placeholders</span>
              </div>
            </div>

            {/* Claim types breakdown */}
            {detail.analysis.claims.length > 0 && (
              <div className="document-detail__first-view-breakdown">
                <h4 className="document-detail__first-view-breakdown-title">Claim Types</h4>
                <div className="document-detail__first-view-claim-types">
                  {Object.entries(
                    detail.analysis.claims.reduce(
                      (acc, c) => {
                        acc[c.type] = (acc[c.type] || 0) + 1;
                        return acc;
                      },
                      {} as Record<string, number>
                    )
                  ).map(([type, count]) => (
                    <span key={type} className="document-detail__first-view-claim-type">
                      {type}: {count}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Sample claims */}
            {detail.analysis.claims.length > 0 && (
              <div className="document-detail__first-view-sample">
                <h4 className="document-detail__first-view-breakdown-title">Sample Claims</h4>
                <ul className="document-detail__first-view-sample-list">
                  {detail.analysis.claims.slice(0, 3).map((claim, i) => (
                    <li key={i}>
                      <span className="document-detail__first-view-sample-type">
                        {claim.type}:
                      </span>{' '}
                      {claim.subject} {claim.predicate}
                    </li>
                  ))}
                  {detail.analysis.claims.length > 3 && (
                    <li className="document-detail__first-view-more">
                      +{detail.analysis.claims.length - 3} more claims...
                    </li>
                  )}
                </ul>
              </div>
            )}

            <div className="document-detail__modal-actions">
              <button onClick={handleDismissFirstView}>Got it</button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <header className="document-detail__header">
        <div className="document-detail__header-nav">
          <button className="document-detail__back" onClick={onClose}>
            ← Back
          </button>
          {onEdit && (
            <button
              className="document-detail__edit-btn"
              onClick={() => onEdit(path)}
              title="Open in Editor"
            >
              ⌨ Edit
            </button>
          )}
        </div>
        <div className="document-detail__title-row">
          <h1 className="document-detail__title">{detail.title}</h1>
          <DocumentStatusBadge status={detail.status} />
        </div>
        <p className="document-detail__path">{detail.path}</p>
      </header>

      {/* Stats Bar */}
      {hasAnalysis && detail.analysis && (
        <div className="document-detail__stats">
          <div className="document-detail__stat">
            <span className="document-detail__stat-value">{detail.analysis.claims.length}</span>
            <span className="document-detail__stat-label">Claims</span>
          </div>
          <div className="document-detail__stat">
            <span className="document-detail__stat-value">
              {detail.analysis.discovered_refs.length}
            </span>
            <span className="document-detail__stat-label">Refs</span>
          </div>
          <div className="document-detail__stat">
            <span className="document-detail__stat-value">
              {detail.analysis.placeholder_paths.length}
            </span>
            <span className="document-detail__stat-label">Placeholders</span>
          </div>
          <div className="document-detail__stat" data-has-value={detail.evidence_marks.length > 0}>
            <span className="document-detail__stat-value">{detail.evidence_marks.length}</span>
            <span className="document-detail__stat-label">Evidence</span>
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="document-detail__actions">
        {detail.status === 'ready' && (
          <button
            className="document-detail__action-btn"
            onClick={handleGeneratePrompt}
            disabled={promptLoading}
          >
            {promptLoading ? 'Generating...' : 'Generate Prompt'}
          </button>
        )}
        {detail.status === 'executed' && (
          <button className="document-detail__action-btn" onClick={() => setShowCapture(true)}>
            Capture Results
          </button>
        )}
      </div>

      {/* Content */}
      <div className="document-detail__content">
        {/* Analysis Section */}
        {hasAnalysis && detail.analysis && (
          <>
            {/* Claims */}
            <section className="document-detail__section">
              <h2 className="document-detail__section-title">CLAIMS</h2>
              {detail.analysis.claims.length === 0 ? (
                <p className="document-detail__empty">No claims extracted</p>
              ) : (
                <ul className="document-detail__claims">
                  {detail.analysis.claims.map((claim, i) => (
                    <li
                      key={i}
                      className="document-detail__claim"
                      data-type={claim.type.toLowerCase()}
                    >
                      <span className="document-detail__claim-type">{claim.type}</span>
                      <span className="document-detail__claim-subject">{claim.subject}</span>
                      <span className="document-detail__claim-predicate">{claim.predicate}</span>
                      <span className="document-detail__claim-line">L{claim.line}</span>
                      <button
                        className="document-detail__delete-btn"
                        onClick={() => handleDeleteClaim(claim, i)}
                        disabled={deleting === `claim-${i}-L${claim.line}`}
                        title="Delete claim"
                      >
                        ×
                      </button>
                    </li>
                  ))}
                </ul>
              )}
            </section>

            {/* References */}
            {detail.analysis.discovered_refs.length > 0 && (
              <section className="document-detail__section">
                <h2 className="document-detail__section-title">DISCOVERED REFERENCES</h2>
                <ul className="document-detail__references">
                  {detail.analysis.discovered_refs.map((ref, i) => (
                    <li key={i} className="document-detail__reference">
                      <span className="document-detail__reference-path">{ref}</span>
                      <button
                        className="document-detail__delete-btn"
                        onClick={() => handleDeleteReference(ref, i)}
                        disabled={deleting === `ref-${i}`}
                        title="Delete reference"
                      >
                        ×
                      </button>
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Anticipated Implementations */}
            {detail.analysis.anticipated.length > 0 && (
              <section className="document-detail__section">
                <h2 className="document-detail__section-title">ANTICIPATED IMPLEMENTATIONS</h2>
                <ul className="document-detail__anticipated">
                  {detail.analysis.anticipated.map((ant, i) => (
                    <li key={i} className="document-detail__anticipated-item">
                      <span className="document-detail__anticipated-path">{ant.path}</span>
                      <span className="document-detail__anticipated-context">{ant.context}</span>
                      {ant.phase && (
                        <span className="document-detail__anticipated-phase">Phase: {ant.phase}</span>
                      )}
                    </li>
                  ))}
                </ul>
              </section>
            )}

            {/* Placeholders */}
            {detail.analysis.placeholder_paths.length > 0 && (
              <section className="document-detail__section">
                <h2 className="document-detail__section-title">PLACEHOLDERS</h2>
                <ul className="document-detail__placeholders">
                  {detail.analysis.placeholder_paths.map((p, i) => (
                    <li key={i} className="document-detail__placeholder">
                      {p}
                    </li>
                  ))}
                </ul>
              </section>
            )}
          </>
        )}

        {/* Evidence Section */}
        {detail.evidence_marks.length > 0 && (
          <section className="document-detail__section">
            <h2 className="document-detail__section-title">EVIDENCE MARKS</h2>
            <ul className="document-detail__evidence-marks">
              {detail.evidence_marks.map((mark) => (
                <li key={mark.mark_id} className="document-detail__evidence-mark">
                  <span className="document-detail__evidence-mark-action">{mark.action}</span>
                  <span className="document-detail__evidence-mark-author">{mark.author}</span>
                  {mark.timestamp && (
                    <span className="document-detail__evidence-mark-time">
                      {new Date(mark.timestamp).toLocaleString()}
                    </span>
                  )}
                  <button
                    className="document-detail__delete-btn"
                    onClick={() => handleDeleteEvidence(mark)}
                    disabled={deleting === mark.mark_id}
                    title="Delete evidence"
                  >
                    ×
                  </button>
                </li>
              ))}
            </ul>
          </section>
        )}

        {/* Edit History / Ledger (Collapsible) */}
        <section className="document-detail__section document-detail__history-section">
          <button
            className="document-detail__history-toggle"
            onClick={() => setHistoryExpanded(!historyExpanded)}
          >
            <span className="document-detail__history-toggle-icon">
              {historyExpanded ? '▼' : '▶'}
            </span>
            <h2 className="document-detail__section-title">EDIT HISTORY</h2>
            <span className="document-detail__history-count">
              {history.length > 0 ? `(${history.length})` : ''}
            </span>
          </button>

          {historyExpanded && (
            <div className="document-detail__history-content">
              {historyLoading ? (
                <p className="document-detail__history-loading">Loading history...</p>
              ) : history.length === 0 ? (
                <div className="document-detail__history-minimal">
                  {detail.uploaded_at && (
                    <div className="document-detail__history-entry">
                      <span className="document-detail__history-entry-time">
                        {new Date(detail.uploaded_at).toLocaleString()}
                      </span>
                      <span className="document-detail__history-entry-action">
                        Document uploaded
                      </span>
                      <span className="document-detail__history-entry-author">system</span>
                    </div>
                  )}
                  {detail.analyzed_at && (
                    <div className="document-detail__history-entry">
                      <span className="document-detail__history-entry-time">
                        {new Date(detail.analyzed_at).toLocaleString()}
                      </span>
                      <span className="document-detail__history-entry-action">
                        Analysis completed
                      </span>
                      <span className="document-detail__history-entry-author">system</span>
                    </div>
                  )}
                </div>
              ) : (
                <ul className="document-detail__history-list">
                  {history.map((entry) => (
                    <li key={entry.id} className="document-detail__history-entry">
                      <span className="document-detail__history-entry-time">
                        {new Date(entry.timestamp).toLocaleString()}
                      </span>
                      <span className="document-detail__history-entry-action">{entry.action}</span>
                      <span className="document-detail__history-entry-author">{entry.author}</span>
                      {entry.details && (
                        <span className="document-detail__history-entry-details">
                          {entry.details}
                        </span>
                      )}
                    </li>
                  ))}
                </ul>
              )}
            </div>
          )}
        </section>
      </div>

      {/* Prompt Modal */}
      {showPrompt && prompt && (
        <div className="document-detail__modal-overlay" onClick={() => setShowPrompt(false)}>
          <div className="document-detail__modal" onClick={(e) => e.stopPropagation()}>
            <h3 className="document-detail__modal-title">Execution Prompt</h3>
            <div className="document-detail__prompt">
              <pre className="document-detail__prompt-text">
                {`# Specification: ${prompt.spec_path}\n\nTargets:\n${prompt.targets.map((t) => `- ${t}`).join('\n')}\n\nClaims: ${prompt.context.claims.length}\nExisting refs: ${prompt.context.existing_refs.length}`}
              </pre>
            </div>
            <div className="document-detail__modal-actions">
              <button onClick={() => setShowPrompt(false)}>Close</button>
              <button onClick={handleCopyPrompt}>Copy to Clipboard</button>
            </div>
          </div>
        </div>
      )}

      {/* Capture Modal */}
      {showCapture && (
        <div className="document-detail__modal-overlay" onClick={() => setShowCapture(false)}>
          <div className="document-detail__modal" onClick={(e) => e.stopPropagation()}>
            <h3 className="document-detail__modal-title">Capture Execution Results</h3>
            <p className="document-detail__modal-subtitle">
              Paste JSON capture data (generated files + test results)
            </p>
            <textarea
              className="document-detail__capture-input"
              value={captureData}
              onChange={(e) => setCaptureData(e.target.value)}
              placeholder='{"spec_path": "...", "generated_files": {...}, "test_results": {...}}'
              rows={15}
              disabled={capturing}
            />
            <div className="document-detail__modal-actions">
              <button onClick={() => setShowCapture(false)} disabled={capturing}>
                Cancel
              </button>
              <button onClick={handleCapture} disabled={capturing || !captureData.trim()}>
                {capturing ? 'Capturing...' : 'Capture'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Error Toast */}
      {error && <div className="document-detail__toast document-detail__toast--error">{error}</div>}
    </div>
  );
}
