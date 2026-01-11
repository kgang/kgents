/**
 * AmendmentEditor - Center panel for viewing/editing an amendment
 *
 * Features:
 * - Split view: original vs proposed content
 * - Diff view toggle
 * - Edit mode for drafts
 * - Read-only for proposed/approved
 * - Syntax highlighting for markdown
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useCallback } from 'react';
import {
  Eye,
  Edit3,
  GitCompare,
  Columns,
  FileText,
  Layers,
  ArrowRight,
  AlertTriangle,
} from 'lucide-react';
import { DiffViewer } from './DiffViewer';
import type { Amendment } from './types';
import {
  AMENDMENT_TYPE_LABELS,
  AMENDMENT_STATUS_LABELS,
  AMENDMENT_STATUS_COLORS,
  LAYER_COLORS,
  LAYER_NAMES,
} from './types';

// =============================================================================
// Types
// =============================================================================

export type EditorViewMode = 'split' | 'diff' | 'original' | 'proposed';

export interface AmendmentEditorProps {
  amendment: Amendment | null;
  viewMode: EditorViewMode;
  onViewModeChange: (mode: EditorViewMode) => void;
  isEditing: boolean;
  onEditStart?: () => void;
  onEditCancel?: () => void;
  onContentChange?: (content: string) => void;
  onSubmitForReview?: () => void;
}

// =============================================================================
// Subcomponents
// =============================================================================

interface ViewModeSelectorProps {
  viewMode: EditorViewMode;
  onChange: (mode: EditorViewMode) => void;
  canEdit: boolean;
  isEditing: boolean;
  onEditStart?: () => void;
  onEditCancel?: () => void;
}

const ViewModeSelector = memo(function ViewModeSelector({
  viewMode,
  onChange,
  canEdit,
  isEditing,
  onEditStart,
  onEditCancel,
}: ViewModeSelectorProps) {
  const modes: { mode: EditorViewMode; icon: React.ReactNode; label: string }[] = [
    { mode: 'split', icon: <Columns size={14} />, label: 'Split' },
    { mode: 'diff', icon: <GitCompare size={14} />, label: 'Diff' },
    { mode: 'original', icon: <Eye size={14} />, label: 'Original' },
    { mode: 'proposed', icon: <FileText size={14} />, label: 'Proposed' },
  ];

  return (
    <div className="amendment-editor__view-selector">
      <div className="amendment-editor__view-modes">
        {modes.map(({ mode, icon, label }) => (
          <button
            key={mode}
            className={`amendment-editor__view-btn ${
              viewMode === mode ? 'amendment-editor__view-btn--active' : ''
            }`}
            onClick={() => onChange(mode)}
            title={label}
          >
            {icon}
            <span>{label}</span>
          </button>
        ))}
      </div>

      {canEdit && (
        <div className="amendment-editor__edit-actions">
          {isEditing ? (
            <button
              className="amendment-editor__edit-btn amendment-editor__edit-btn--cancel"
              onClick={onEditCancel}
            >
              Cancel
            </button>
          ) : (
            <button
              className="amendment-editor__edit-btn"
              onClick={onEditStart}
              title="Edit draft (e)"
            >
              <Edit3 size={14} />
              Edit
            </button>
          )}
        </div>
      )}
    </div>
  );
});

interface ContentPaneProps {
  title: string;
  content: string;
  isEditing?: boolean;
  onChange?: (content: string) => void;
  variant: 'original' | 'proposed';
}

const ContentPane = memo(function ContentPane({
  title,
  content,
  isEditing = false,
  onChange,
  variant,
}: ContentPaneProps) {
  const lines = content.split('\n');

  return (
    <div className={`amendment-editor__pane amendment-editor__pane--${variant}`}>
      <div className="amendment-editor__pane-header">
        <span className="amendment-editor__pane-title">{title}</span>
        <span className="amendment-editor__pane-lines">{lines.length} lines</span>
      </div>
      <div className="amendment-editor__pane-content">
        {isEditing && variant === 'proposed' ? (
          <textarea
            className="amendment-editor__textarea"
            value={content}
            onChange={(e) => onChange?.(e.target.value)}
            spellCheck={false}
          />
        ) : (
          <div className="amendment-editor__code">
            {lines.map((line, index) => (
              <div key={index} className="amendment-editor__line">
                <span className="amendment-editor__line-num">{index + 1}</span>
                <code className="amendment-editor__line-content">{line || ' '}</code>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
});

interface AmendmentMetaHeaderProps {
  amendment: Amendment;
}

const AmendmentMetaHeader = memo(function AmendmentMetaHeader({
  amendment,
}: AmendmentMetaHeaderProps) {
  const statusColor = AMENDMENT_STATUS_COLORS[amendment.status];
  const layerColor = LAYER_COLORS[amendment.targetLayer as keyof typeof LAYER_COLORS];
  const layerName = LAYER_NAMES[amendment.targetLayer as keyof typeof LAYER_NAMES];

  return (
    <div className="amendment-editor__meta-header">
      <div className="amendment-editor__meta-primary">
        <h2 className="amendment-editor__title">{amendment.title}</h2>
        <div className="amendment-editor__badges">
          <span
            className="amendment-editor__badge amendment-editor__badge--status"
            style={{ color: statusColor, borderColor: statusColor }}
          >
            {AMENDMENT_STATUS_LABELS[amendment.status]}
          </span>
          <span
            className="amendment-editor__badge amendment-editor__badge--layer"
            style={{ color: layerColor, borderColor: layerColor }}
          >
            L{amendment.targetLayer} {layerName}
          </span>
          <span className="amendment-editor__badge amendment-editor__badge--type">
            {AMENDMENT_TYPE_LABELS[amendment.amendmentType]}
          </span>
        </div>
      </div>

      <div className="amendment-editor__meta-target">
        <Layers size={12} />
        <span className="amendment-editor__target-path">{amendment.targetKblock}</span>
        <ArrowRight size={12} />
        <span className="amendment-editor__target-title">
          {amendment.targetKblockTitle || 'Unknown'}
        </span>
      </div>

      <p className="amendment-editor__description">{amendment.description}</p>

      {amendment.principlesAffected.length > 0 && (
        <div className="amendment-editor__principles">
          <span className="amendment-editor__principles-label">Affects:</span>
          {amendment.principlesAffected.map((principle) => (
            <span key={principle} className="amendment-editor__principle-tag">
              {principle}
            </span>
          ))}
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const AmendmentEditor = memo(function AmendmentEditor({
  amendment,
  viewMode,
  onViewModeChange,
  isEditing,
  onEditStart,
  onEditCancel,
  onContentChange,
  onSubmitForReview,
}: AmendmentEditorProps) {
  const [workingContent, setWorkingContent] = useState(amendment?.proposedContent || '');

  // Reset working content when amendment changes
  const handleContentChange = useCallback(
    (content: string) => {
      setWorkingContent(content);
      onContentChange?.(content);
    },
    [onContentChange]
  );

  // Can only edit drafts
  const canEdit = amendment?.status === 'draft';
  const canSubmit = amendment?.status === 'draft';

  if (!amendment) {
    return (
      <div className="amendment-editor amendment-editor--empty">
        <div className="amendment-editor__empty-state">
          <FileText size={48} className="amendment-editor__empty-icon" />
          <h3 className="amendment-editor__empty-title">No Amendment Selected</h3>
          <p className="amendment-editor__empty-text">
            Select an amendment from the list to view or edit it, or create a new one.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="amendment-editor">
      <AmendmentMetaHeader amendment={amendment} />

      <ViewModeSelector
        viewMode={viewMode}
        onChange={onViewModeChange}
        canEdit={canEdit}
        isEditing={isEditing}
        onEditStart={onEditStart}
        onEditCancel={onEditCancel}
      />

      <div className="amendment-editor__content">
        {viewMode === 'diff' && (
          <DiffViewer
            diff={amendment.diff}
            originalContent={amendment.originalContent}
            proposedContent={isEditing ? workingContent : amendment.proposedContent}
            viewMode="unified"
            fileName={amendment.targetKblock}
            showLineNumbers={true}
            expandable={true}
          />
        )}

        {viewMode === 'split' && (
          <div className="amendment-editor__split">
            <ContentPane title="Original" content={amendment.originalContent} variant="original" />
            <div className="amendment-editor__split-divider">
              <ArrowRight size={16} />
            </div>
            <ContentPane
              title="Proposed"
              content={isEditing ? workingContent : amendment.proposedContent}
              isEditing={isEditing}
              onChange={handleContentChange}
              variant="proposed"
            />
          </div>
        )}

        {viewMode === 'original' && (
          <ContentPane
            title="Original Content"
            content={amendment.originalContent}
            variant="original"
          />
        )}

        {viewMode === 'proposed' && (
          <ContentPane
            title="Proposed Content"
            content={isEditing ? workingContent : amendment.proposedContent}
            isEditing={isEditing}
            onChange={handleContentChange}
            variant="proposed"
          />
        )}
      </div>

      {/* Reasoning section */}
      <div className="amendment-editor__reasoning">
        <div className="amendment-editor__reasoning-header">
          <AlertTriangle size={14} />
          <span>Reasoning</span>
        </div>
        <p className="amendment-editor__reasoning-text">{amendment.reasoning}</p>
      </div>

      {/* Actions for drafts */}
      {canSubmit && (
        <div className="amendment-editor__actions">
          <button
            className="amendment-editor__action-btn amendment-editor__action-btn--primary"
            onClick={onSubmitForReview}
            title="Submit for review (p)"
          >
            Submit for Review
          </button>
          <span className="amendment-editor__action-hint">
            <kbd>p</kbd> to propose
          </span>
        </div>
      )}
    </div>
  );
});

export default AmendmentEditor;
