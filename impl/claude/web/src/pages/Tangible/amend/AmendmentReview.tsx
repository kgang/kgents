/**
 * AmendmentReview - Right panel for review workflow
 *
 * Features:
 * - Amendment metadata (proposer, reasoning, principles affected)
 * - Derivation chain visualization
 * - Review notes timeline
 * - Add review note form
 * - Approve/Reject buttons with reasoning input
 * - Apply button for approved amendments
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 */

import { memo, useState, useCallback } from 'react';
import {
  User,
  Clock,
  GitBranch,
  MessageSquare,
  Check,
  X,
  Play,
  AlertCircle,
  ThumbsUp,
  ThumbsDown,
  HelpCircle,
  ArrowUp,
  ArrowDown,
} from 'lucide-react';
import type { Amendment, ReviewNote } from './types';
import {
  AMENDMENT_STATUS_LABELS,
  AMENDMENT_STATUS_COLORS,
  LAYER_COLORS,
  LAYER_NAMES,
} from './types';

// =============================================================================
// Types
// =============================================================================

export interface AmendmentReviewProps {
  amendment: Amendment | null;
  onAddNote: (note: string, sentiment: ReviewNote['sentiment']) => void;
  onApprove: (reasoning: string) => void;
  onReject: (reasoning: string) => void;
  onApply: () => void;
  onRevert?: () => void;
  isLoading?: boolean;
}

// =============================================================================
// Helpers
// =============================================================================

const formatTimestamp = (timestamp: string) => {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

  if (diffHours < 1) {
    return 'Just now';
  }
  if (diffHours < 24) {
    return `${diffHours}h ago`;
  }
  if (diffDays < 7) {
    return `${diffDays}d ago`;
  }
  return date.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
  });
};

const getSentimentIcon = (sentiment?: ReviewNote['sentiment']) => {
  switch (sentiment) {
    case 'support':
      return (
        <ThumbsUp size={12} className="review-note__sentiment review-note__sentiment--support" />
      );
    case 'concern':
      return (
        <ThumbsDown size={12} className="review-note__sentiment review-note__sentiment--concern" />
      );
    case 'question':
      return (
        <HelpCircle size={12} className="review-note__sentiment review-note__sentiment--question" />
      );
    default:
      return <MessageSquare size={12} className="review-note__sentiment" />;
  }
};

// =============================================================================
// Subcomponents
// =============================================================================

interface MetadataSectionProps {
  amendment: Amendment;
}

const MetadataSection = memo(function MetadataSection({ amendment }: MetadataSectionProps) {
  const statusColor = AMENDMENT_STATUS_COLORS[amendment.status];

  return (
    <div className="amendment-review__metadata">
      <div className="amendment-review__metadata-item">
        <User size={12} />
        <span className="amendment-review__metadata-label">Proposer</span>
        <span className="amendment-review__metadata-value">{amendment.proposer}</span>
      </div>

      <div className="amendment-review__metadata-item">
        <Clock size={12} />
        <span className="amendment-review__metadata-label">Created</span>
        <span className="amendment-review__metadata-value">
          {formatTimestamp(amendment.createdAt)}
        </span>
      </div>

      {amendment.proposedAt && (
        <div className="amendment-review__metadata-item">
          <ArrowUp size={12} />
          <span className="amendment-review__metadata-label">Proposed</span>
          <span className="amendment-review__metadata-value">
            {formatTimestamp(amendment.proposedAt)}
          </span>
        </div>
      )}

      {amendment.reviewedAt && (
        <div className="amendment-review__metadata-item">
          <Check size={12} />
          <span className="amendment-review__metadata-label">Reviewed</span>
          <span className="amendment-review__metadata-value">
            {formatTimestamp(amendment.reviewedAt)}
          </span>
        </div>
      )}

      <div className="amendment-review__metadata-item amendment-review__metadata-item--status">
        <span className="amendment-review__status-dot" style={{ backgroundColor: statusColor }} />
        <span className="amendment-review__metadata-label">Status</span>
        <span className="amendment-review__metadata-value" style={{ color: statusColor }}>
          {AMENDMENT_STATUS_LABELS[amendment.status]}
        </span>
      </div>
    </div>
  );
});

interface DerivationVisualizationProps {
  amendment: Amendment;
}

const DerivationVisualization = memo(function DerivationVisualization({
  amendment,
}: DerivationVisualizationProps) {
  // Simple derivation chain mockup - in real app, this would fetch from API
  const derivationLayers = [0, 1, 2, 3, 4].filter((l) => l <= amendment.targetLayer);

  return (
    <div className="amendment-review__derivation">
      <div className="amendment-review__section-header">
        <GitBranch size={12} />
        <span>Derivation Chain</span>
      </div>

      <div className="amendment-review__derivation-chain">
        {derivationLayers.map((layer, index) => {
          const color = LAYER_COLORS[layer as keyof typeof LAYER_COLORS];
          const name = LAYER_NAMES[layer as keyof typeof LAYER_NAMES];
          const isTarget = layer === amendment.targetLayer;

          return (
            <div key={layer} className="amendment-review__derivation-node-wrapper">
              {index > 0 && <div className="amendment-review__derivation-line" />}
              <div
                className={`amendment-review__derivation-node ${
                  isTarget ? 'amendment-review__derivation-node--target' : ''
                }`}
                style={{ borderLeftColor: color }}
              >
                <span className="amendment-review__derivation-layer" style={{ color }}>
                  L{layer}
                </span>
                <span className="amendment-review__derivation-name">{name}</span>
                {isTarget && <span className="amendment-review__derivation-marker">Target</span>}
              </div>
            </div>
          );
        })}
      </div>

      {amendment.principlesAffected.length > 0 && (
        <div className="amendment-review__affected">
          <span className="amendment-review__affected-label">Affects principles:</span>
          <div className="amendment-review__affected-list">
            {amendment.principlesAffected.map((principle) => (
              <span key={principle} className="amendment-review__affected-tag">
                {principle}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

interface ReviewNotesTimelineProps {
  notes: ReviewNote[];
}

const ReviewNotesTimeline = memo(function ReviewNotesTimeline({ notes }: ReviewNotesTimelineProps) {
  if (notes.length === 0) {
    return (
      <div className="amendment-review__notes-empty">
        <MessageSquare size={16} />
        <span>No review notes yet</span>
      </div>
    );
  }

  return (
    <div className="amendment-review__notes-timeline">
      {notes.map((note) => (
        <div key={note.id} className="review-note">
          <div className="review-note__header">
            {getSentimentIcon(note.sentiment)}
            <span className="review-note__reviewer">{note.reviewer}</span>
            <span className="review-note__time">{formatTimestamp(note.timestamp)}</span>
          </div>
          <p className="review-note__text">{note.note}</p>
        </div>
      ))}
    </div>
  );
});

interface AddNoteFormProps {
  onSubmit: (note: string, sentiment: ReviewNote['sentiment']) => void;
  disabled?: boolean;
}

const AddNoteForm = memo(function AddNoteForm({ onSubmit, disabled }: AddNoteFormProps) {
  const [note, setNote] = useState('');
  const [sentiment, setSentiment] = useState<ReviewNote['sentiment']>('neutral');

  const handleSubmit = useCallback(() => {
    if (note.trim()) {
      onSubmit(note.trim(), sentiment);
      setNote('');
      setSentiment('neutral');
    }
  }, [note, sentiment, onSubmit]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [handleSubmit]
  );

  return (
    <div className="amendment-review__add-note">
      <div className="amendment-review__note-sentiment">
        {(['support', 'concern', 'question', 'neutral'] as const).map((s) => (
          <button
            key={s}
            className={`amendment-review__sentiment-btn ${
              sentiment === s ? 'amendment-review__sentiment-btn--active' : ''
            }`}
            onClick={() => setSentiment(s)}
            title={s.charAt(0).toUpperCase() + s.slice(1)}
            disabled={disabled}
          >
            {s === 'support' && <ThumbsUp size={12} />}
            {s === 'concern' && <ThumbsDown size={12} />}
            {s === 'question' && <HelpCircle size={12} />}
            {s === 'neutral' && <MessageSquare size={12} />}
          </button>
        ))}
      </div>
      <textarea
        className="amendment-review__note-input"
        placeholder="Add a review note..."
        value={note}
        onChange={(e) => setNote(e.target.value)}
        onKeyDown={handleKeyDown}
        disabled={disabled}
        rows={3}
      />
      <div className="amendment-review__note-footer">
        <span className="amendment-review__note-hint">Cmd+Enter to submit</span>
        <button
          className="amendment-review__note-submit"
          onClick={handleSubmit}
          disabled={disabled || !note.trim()}
        >
          Add Note
        </button>
      </div>
    </div>
  );
});

interface ApprovalActionsProps {
  amendment: Amendment;
  onApprove: (reasoning: string) => void;
  onReject: (reasoning: string) => void;
  onApply: () => void;
  onRevert?: () => void;
  isLoading: boolean;
}

const ApprovalActions = memo(function ApprovalActions({
  amendment,
  onApprove,
  onReject,
  onApply,
  onRevert,
  isLoading,
}: ApprovalActionsProps) {
  const [approvalReasoning, setApprovalReasoning] = useState('');
  const [rejectionReasoning, setRejectionReasoning] = useState('');
  const [showApproveForm, setShowApproveForm] = useState(false);
  const [showRejectForm, setShowRejectForm] = useState(false);

  const canReview = amendment.status === 'proposed' || amendment.status === 'under_review';
  const canApply = amendment.status === 'approved';
  const canRevert = amendment.status === 'applied' && onRevert;

  if (!canReview && !canApply && !canRevert) {
    return null;
  }

  return (
    <div className="amendment-review__actions">
      <div className="amendment-review__section-header">
        <AlertCircle size={12} />
        <span>Actions</span>
      </div>

      {canReview && (
        <>
          {!showApproveForm && !showRejectForm && (
            <div className="amendment-review__action-buttons">
              <button
                className="amendment-review__action-btn amendment-review__action-btn--approve"
                onClick={() => setShowApproveForm(true)}
                disabled={isLoading}
                title="Approve (a)"
              >
                <Check size={14} />
                Approve
              </button>
              <button
                className="amendment-review__action-btn amendment-review__action-btn--reject"
                onClick={() => setShowRejectForm(true)}
                disabled={isLoading}
                title="Reject (r)"
              >
                <X size={14} />
                Reject
              </button>
            </div>
          )}

          {showApproveForm && (
            <div className="amendment-review__reasoning-form">
              <label className="amendment-review__reasoning-label">Approval Reasoning</label>
              <textarea
                className="amendment-review__reasoning-input"
                placeholder="Why should this amendment be approved?"
                value={approvalReasoning}
                onChange={(e) => setApprovalReasoning(e.target.value)}
                rows={3}
                autoFocus
              />
              <div className="amendment-review__reasoning-actions">
                <button
                  className="amendment-review__reasoning-cancel"
                  onClick={() => {
                    setShowApproveForm(false);
                    setApprovalReasoning('');
                  }}
                >
                  Cancel
                </button>
                <button
                  className="amendment-review__reasoning-submit amendment-review__reasoning-submit--approve"
                  onClick={() => {
                    onApprove(approvalReasoning);
                    setShowApproveForm(false);
                    setApprovalReasoning('');
                  }}
                  disabled={isLoading}
                >
                  <Check size={14} />
                  Confirm Approval
                </button>
              </div>
            </div>
          )}

          {showRejectForm && (
            <div className="amendment-review__reasoning-form">
              <label className="amendment-review__reasoning-label">Rejection Reasoning</label>
              <textarea
                className="amendment-review__reasoning-input"
                placeholder="Why should this amendment be rejected?"
                value={rejectionReasoning}
                onChange={(e) => setRejectionReasoning(e.target.value)}
                rows={3}
                autoFocus
              />
              <div className="amendment-review__reasoning-actions">
                <button
                  className="amendment-review__reasoning-cancel"
                  onClick={() => {
                    setShowRejectForm(false);
                    setRejectionReasoning('');
                  }}
                >
                  Cancel
                </button>
                <button
                  className="amendment-review__reasoning-submit amendment-review__reasoning-submit--reject"
                  onClick={() => {
                    onReject(rejectionReasoning);
                    setShowRejectForm(false);
                    setRejectionReasoning('');
                  }}
                  disabled={isLoading}
                >
                  <X size={14} />
                  Confirm Rejection
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {canApply && (
        <div className="amendment-review__apply-section">
          {amendment.approvalReasoning && (
            <div className="amendment-review__approval-reason">
              <span className="amendment-review__approval-label">Approved because:</span>
              <p>{amendment.approvalReasoning}</p>
            </div>
          )}
          <button
            className="amendment-review__action-btn amendment-review__action-btn--apply"
            onClick={onApply}
            disabled={isLoading}
            title="Apply amendment (Enter)"
          >
            <Play size={14} />
            Apply Amendment
          </button>
        </div>
      )}

      {canRevert && (
        <div className="amendment-review__revert-section">
          <button
            className="amendment-review__action-btn amendment-review__action-btn--revert"
            onClick={onRevert}
            disabled={isLoading}
          >
            <ArrowDown size={14} />
            Revert Amendment
          </button>
        </div>
      )}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const AmendmentReview = memo(function AmendmentReview({
  amendment,
  onAddNote,
  onApprove,
  onReject,
  onApply,
  onRevert,
  isLoading = false,
}: AmendmentReviewProps) {
  if (!amendment) {
    return (
      <div className="amendment-review amendment-review--empty">
        <div className="amendment-review__empty-state">
          <MessageSquare size={32} />
          <p>Select an amendment to review</p>
        </div>
      </div>
    );
  }

  return (
    <div className="amendment-review">
      <div className="amendment-review__header">
        <MessageSquare size={14} />
        <span className="amendment-review__header-title">Review</span>
      </div>

      <div className="amendment-review__content">
        <MetadataSection amendment={amendment} />

        <DerivationVisualization amendment={amendment} />

        <div className="amendment-review__notes-section">
          <div className="amendment-review__section-header">
            <MessageSquare size={12} />
            <span>Review Notes</span>
            <span className="amendment-review__notes-count">{amendment.reviewNotes.length}</span>
          </div>

          <ReviewNotesTimeline notes={amendment.reviewNotes} />

          <AddNoteForm onSubmit={onAddNote} disabled={isLoading} />
        </div>

        <ApprovalActions
          amendment={amendment}
          onApprove={onApprove}
          onReject={onReject}
          onApply={onApply}
          onRevert={onRevert}
          isLoading={isLoading}
        />
      </div>

      <div className="amendment-review__footer">
        <span className="amendment-review__shortcuts">
          <kbd>a</kbd> approve
          <kbd>r</kbd> reject
          <kbd>Enter</kbd> apply
        </span>
      </div>
    </div>
  );
});

export default AmendmentReview;
