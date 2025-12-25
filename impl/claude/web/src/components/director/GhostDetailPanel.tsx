/**
 * GhostDetailPanel — Detail view for ghost documents
 *
 * When a ghost is selected, this panel shows:
 * - Clear indication that this is a placeholder (not a real doc)
 * - Origin information (which spec created this ghost)
 * - Context about why it's expected
 * - Affordances: fill in content, upload to reconcile
 *
 * Philosophy:
 *   "Daring, bold, creative, opinionated but not gaudy"
 *   The ghost state should be unmistakable but not alarming.
 *   It's an invitation, not an error.
 */

import { useCallback, useState } from 'react';

import {
  type DocumentEntry,
  updateGhostContent,
  promoteGhost,
} from '../../api/director';

import './GhostDetailPanel.css';

// =============================================================================
// Types
// =============================================================================

interface GhostDetailPanelProps {
  document: DocumentEntry;
  onRefresh: () => void;
  onUploadToReconcile?: (path: string) => void;
  onNavigateToEditor?: (path: string) => void;
}

// =============================================================================
// Component
// =============================================================================

export function GhostDetailPanel({
  document,
  onRefresh,
  onUploadToReconcile,
  onNavigateToEditor,
}: GhostDetailPanelProps) {
  const metadata = document.ghost_metadata;
  const hasDraft = metadata?.has_draft_content ?? false;

  // Content editing state
  const [isEditing, setIsEditing] = useState(false);
  const [draftContent, setDraftContent] = useState(metadata?.user_content ?? '');
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Promotion state
  const [promoting, setPromoting] = useState(false);

  // Handle save draft
  const handleSaveDraft = useCallback(async () => {
    if (!draftContent.trim()) return;

    setSaving(true);
    setError(null);

    try {
      await updateGhostContent(document.path, draftContent);
      setIsEditing(false);
      onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save draft');
    } finally {
      setSaving(false);
    }
  }, [document.path, draftContent, onRefresh]);

  // Handle promote to real document
  const handlePromote = useCallback(async () => {
    if (!hasDraft) return;

    setPromoting(true);
    setError(null);

    try {
      await promoteGhost(document.path);
      onRefresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to promote ghost');
    } finally {
      setPromoting(false);
    }
  }, [document.path, hasDraft, onRefresh]);

  return (
    <div className="ghost-detail">
      {/* Ghost indicator banner */}
      <div className="ghost-detail__banner">
        <span className="ghost-detail__banner-icon">◭</span>
        <div className="ghost-detail__banner-content">
          <span className="ghost-detail__banner-title">Ghost Document</span>
          <span className="ghost-detail__banner-subtitle">
            This document doesn't exist yet — it was created as a placeholder.
          </span>
        </div>
      </div>

      {/* Origin info */}
      {metadata && (
        <div className="ghost-detail__origin">
          <div className="ghost-detail__origin-row">
            <span className="ghost-detail__origin-label">Created by</span>
            <span className="ghost-detail__origin-value">
              {metadata.created_by_path}
            </span>
          </div>
          {metadata.context && (
            <div className="ghost-detail__origin-row">
              <span className="ghost-detail__origin-label">Context</span>
              <span className="ghost-detail__origin-value ghost-detail__origin-value--context">
                {metadata.context}
              </span>
            </div>
          )}
          <div className="ghost-detail__origin-row">
            <span className="ghost-detail__origin-label">Origin</span>
            <GhostOriginLabel origin={metadata.origin} />
          </div>
          <div className="ghost-detail__origin-row">
            <span className="ghost-detail__origin-label">Created</span>
            <span className="ghost-detail__origin-value">
              {new Date(metadata.created_at).toLocaleString()}
            </span>
          </div>
        </div>
      )}

      {/* Draft status */}
      <div className="ghost-detail__status">
        {hasDraft ? (
          <div className="ghost-detail__status-card ghost-detail__status-card--draft">
            <span className="ghost-detail__status-icon">◐</span>
            <div className="ghost-detail__status-content">
              <span className="ghost-detail__status-title">Has Draft Content</span>
              <span className="ghost-detail__status-description">
                You've started filling in this document.
                You can continue editing or promote it to a real document.
              </span>
            </div>
          </div>
        ) : (
          <div className="ghost-detail__status-card ghost-detail__status-card--empty">
            <span className="ghost-detail__status-icon">○</span>
            <div className="ghost-detail__status-content">
              <span className="ghost-detail__status-title">Empty Placeholder</span>
              <span className="ghost-detail__status-description">
                Start writing content below, or upload the real document to reconcile.
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Content editor */}
      <div className="ghost-detail__editor">
        <div className="ghost-detail__editor-header">
          <span className="ghost-detail__editor-label">Content</span>
          {!isEditing && hasDraft && (
            <button
              className="ghost-detail__editor-btn"
              onClick={() => setIsEditing(true)}
            >
              Edit
            </button>
          )}
        </div>

        {isEditing || !hasDraft ? (
          <div className="ghost-detail__editor-area">
            <textarea
              className="ghost-detail__textarea"
              placeholder="Start writing the document content..."
              value={draftContent}
              onChange={(e) => setDraftContent(e.target.value)}
              rows={10}
            />
            <div className="ghost-detail__editor-actions">
              <button
                className="ghost-detail__action-btn ghost-detail__action-btn--secondary"
                onClick={() => {
                  setIsEditing(false);
                  setDraftContent(metadata?.user_content ?? '');
                }}
                disabled={saving}
              >
                Cancel
              </button>
              <button
                className="ghost-detail__action-btn ghost-detail__action-btn--primary"
                onClick={handleSaveDraft}
                disabled={saving || !draftContent.trim()}
              >
                {saving ? 'Saving...' : 'Save Draft'}
              </button>
            </div>
          </div>
        ) : (
          <div className="ghost-detail__preview">
            <pre className="ghost-detail__preview-text">
              {metadata?.user_content}
            </pre>
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="ghost-detail__error">
          {error}
        </div>
      )}

      {/* Actions */}
      <div className="ghost-detail__actions">
        {hasDraft && (
          <button
            className="ghost-detail__action-btn ghost-detail__action-btn--promote"
            onClick={handlePromote}
            disabled={promoting}
          >
            {promoting ? 'Promoting...' : '◎ Promote to Real Document'}
          </button>
        )}

        <button
          className="ghost-detail__action-btn ghost-detail__action-btn--upload"
          onClick={() => onUploadToReconcile?.(document.path)}
        >
          ↑ Upload to Reconcile
        </button>

        {onNavigateToEditor && (
          <button
            className="ghost-detail__action-btn ghost-detail__action-btn--editor"
            onClick={() => onNavigateToEditor(document.path)}
          >
            ◈ Open in Editor
          </button>
        )}
      </div>

      {/* Reconciliation hint */}
      <div className="ghost-detail__hint">
        <span className="ghost-detail__hint-icon">○</span>
        <span className="ghost-detail__hint-text">
          {hasDraft
            ? 'If you upload a different version, you can choose how to merge your draft with the uploaded content using Zero-Seed.'
            : 'Upload the real document to replace this placeholder and resolve the dangling reference.'}
        </span>
      </div>
    </div>
  );
}

// =============================================================================
// Origin Label
// =============================================================================

interface GhostOriginLabelProps {
  origin: string;
}

function GhostOriginLabel({ origin }: GhostOriginLabelProps) {
  const config = {
    parsed_reference: {
      label: 'Parsed Reference',
      description: 'Created when another doc referenced this path',
      color: 'var(--steel-400)',
    },
    anticipated: {
      label: 'Anticipated',
      description: 'Created from @anticipated marker',
      color: 'var(--amber-400)',
    },
    user_created: {
      label: 'User Created',
      description: 'Manually created as placeholder',
      color: 'var(--blue-400)',
    },
  }[origin] ?? {
    label: origin,
    description: '',
    color: 'var(--steel-400)',
  };

  return (
    <span
      className="ghost-origin-label"
      style={{ color: config.color }}
      title={config.description}
    >
      {config.label}
    </span>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default GhostDetailPanel;
