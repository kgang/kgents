/**
 * ChatPortal — Inline Portal Emission Renderer
 *
 * "The doc comes to you" — portal content shown inline in chat.
 * Like forwarding a message — complete context without navigation.
 *
 * Features:
 * - Auto-expand on emission (heuristic: show immediately)
 * - Inline read access (syntax highlighting)
 * - Inline write access (edit mode for readwrite portals)
 * - Sync status indicators (✓ saved, ◐ saving, ⚠️ failed)
 *
 * Design: Brutalist styling matching PortalToken
 *
 * @see spec/protocols/portal-token.md §15 (Deep Integration)
 */

import { memo, useState, useCallback, useRef, useEffect } from 'react';
import type { PortalEmission } from '../../types/chat';
import { GrowingContainer } from '../joy';
import './ChatPortal.css';

// =============================================================================
// Types
// =============================================================================

export interface ChatPortalProps {
  emission: PortalEmission;
  /** Called when user edits content */
  onEdit?: (portalId: string, content: string) => Promise<void>;
  /** Called when user navigates to destination */
  onNavigate?: (path: string) => void;
  /** Default expanded state (true for auto-expand) */
  defaultExpanded?: boolean;
}

type SyncStatus = 'idle' | 'saving' | 'saved' | 'failed';

// =============================================================================
// Component
// =============================================================================

export const ChatPortal = memo(function ChatPortal({
  emission,
  onEdit,
  onNavigate,
  defaultExpanded,
}: ChatPortalProps) {
  const [expanded, setExpanded] = useState(defaultExpanded ?? emission.auto_expand);
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState(emission.content_full || '');
  const [syncStatus, setSyncStatus] = useState<SyncStatus>('idle');
  const [syncError, setSyncError] = useState<string | null>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Reset edit content when emission changes
  useEffect(() => {
    setEditContent(emission.content_full || '');
  }, [emission.content_full]);

  // Auto-focus textarea when entering edit mode
  useEffect(() => {
    if (editing && textareaRef.current) {
      textareaRef.current.focus();
      // Move cursor to end
      textareaRef.current.setSelectionRange(
        textareaRef.current.value.length,
        textareaRef.current.value.length
      );
    }
  }, [editing]);

  const handleToggleExpand = useCallback(() => {
    setExpanded((prev) => !prev);
  }, []);

  const handleNavigate = useCallback(() => {
    onNavigate?.(emission.destination);
  }, [onNavigate, emission.destination]);

  const handleStartEdit = useCallback(() => {
    if (emission.access !== 'readwrite') return;
    setEditing(true);
  }, [emission.access]);

  const handleCancelEdit = useCallback(() => {
    setEditing(false);
    setEditContent(emission.content_full || '');
    setSyncError(null);
  }, [emission.content_full]);

  const handleSaveEdit = useCallback(async () => {
    if (!onEdit) return;

    setSyncStatus('saving');
    setSyncError(null);

    try {
      await onEdit(emission.portal_id, editContent);
      setSyncStatus('saved');
      setEditing(false);

      // Reset to idle after brief success indication
      setTimeout(() => {
        setSyncStatus('idle');
      }, 2000);
    } catch (err) {
      setSyncStatus('failed');
      setSyncError(err instanceof Error ? err.message : 'Save failed');
    }
  }, [onEdit, emission.portal_id, editContent]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      // Cmd+Enter or Ctrl+Enter to save
      if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') {
        e.preventDefault();
        handleSaveEdit();
      }
      // Escape to cancel
      if (e.key === 'Escape') {
        e.preventDefault();
        handleCancelEdit();
      }
    },
    [handleSaveEdit, handleCancelEdit]
  );

  const canEdit = emission.access === 'readwrite' && !editing;
  const showContent = expanded && (emission.content_full || emission.content_preview);

  // Build class names
  const classNames = [
    'chat-portal',
    expanded && 'chat-portal--expanded',
    editing && 'chat-portal--editing',
    !emission.exists && 'chat-portal--missing',
  ]
    .filter(Boolean)
    .join(' ');

  return (
    <div className={classNames} data-portal-id={emission.portal_id}>
      {/* Header */}
      <div className="chat-portal__header">
        <button
          type="button"
          className="chat-portal__toggle"
          onClick={handleToggleExpand}
          aria-expanded={expanded}
          title={expanded ? 'Collapse' : 'Expand'}
        >
          <span className="chat-portal__icon">{expanded ? '\u25BC' : '\u25B6'}</span>
          <span className="chat-portal__edge-type">[{emission.edge_type}]</span>
          <span className="chat-portal__arrow">──→</span>
          <span className="chat-portal__destination">{emission.destination}</span>
        </button>

        {/* Actions */}
        <div className="chat-portal__actions">
          {/* Navigate button */}
          {onNavigate && (
            <button
              type="button"
              className="chat-portal__action-btn chat-portal__action-btn--navigate"
              onClick={handleNavigate}
              title="Navigate to destination"
            >
              ↗
            </button>
          )}

          {/* Edit button (readwrite only) */}
          {canEdit && (
            <button
              type="button"
              className="chat-portal__action-btn chat-portal__action-btn--edit"
              onClick={handleStartEdit}
              title="Edit content"
            >
              ✎
            </button>
          )}

          {/* Sync status indicator */}
          {syncStatus !== 'idle' && (
            <div className="chat-portal__sync-status" data-status={syncStatus}>
              {syncStatus === 'saving' && <span title="Saving...">◐</span>}
              {syncStatus === 'saved' && <span title="Saved">✓</span>}
              {syncStatus === 'failed' && <span title={syncError || 'Failed'}>⚠️</span>}
            </div>
          )}
        </div>
      </div>

      {/* Metadata */}
      <div className="chat-portal__meta">
        <span className="chat-portal__meta-item">
          {emission.line_count} {emission.line_count === 1 ? 'line' : 'lines'}
        </span>
        <span className="chat-portal__meta-item">{emission.access}</span>
        {!emission.exists && (
          <span className="chat-portal__meta-item chat-portal__meta-item--warning">
            file missing
          </span>
        )}
        {emission.auto_expand && (
          <span className="chat-portal__meta-item chat-portal__meta-item--hint">
            auto-expanded
          </span>
        )}
      </div>

      {/* Content */}
      {showContent && (
        <GrowingContainer>
          {editing ? (
            // Edit mode
            <div className="chat-portal__editor">
              <textarea
                ref={textareaRef}
                className="chat-portal__textarea"
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                onKeyDown={handleKeyDown}
                rows={Math.min(Math.max(emission.line_count, 5), 30)}
                spellCheck={false}
              />
              <div className="chat-portal__editor-actions">
                <button
                  type="button"
                  className="chat-portal__editor-btn chat-portal__editor-btn--save"
                  onClick={handleSaveEdit}
                  disabled={syncStatus === 'saving'}
                >
                  Save {syncStatus === 'saving' && '...'}
                </button>
                <button
                  type="button"
                  className="chat-portal__editor-btn chat-portal__editor-btn--cancel"
                  onClick={handleCancelEdit}
                  disabled={syncStatus === 'saving'}
                >
                  Cancel
                </button>
                {syncError && (
                  <span className="chat-portal__editor-error">{syncError}</span>
                )}
                <span className="chat-portal__editor-hint">
                  Cmd+Enter to save, Esc to cancel
                </span>
              </div>
            </div>
          ) : (
            // Read mode
            <div className="chat-portal__content">
              <pre className="chat-portal__pre">
                <code className="chat-portal__code">
                  {emission.content_full || emission.content_preview || '(empty)'}
                </code>
              </pre>
            </div>
          )}
        </GrowingContainer>
      )}
    </div>
  );
});

export default ChatPortal;
