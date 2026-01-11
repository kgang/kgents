/**
 * AmendmentMode - Main Amendment Mode component
 *
 * The constitutional amendment workflow for the Self-Reflective OS.
 * Three-panel layout:
 * - Left: Pending amendments list
 * - Center: Amendment detail/editor
 * - Right: Review notes + approval actions
 *
 * "The constitution that cannot be amended is already dead."
 *
 * STARK BIOME aesthetic: 90% steel, 10% earned glow.
 *
 * Keyboard Shortcuts:
 * - n: New amendment
 * - e: Edit draft
 * - p: Submit for proposal
 * - a: Approve (when reviewing)
 * - r: Reject (when reviewing)
 * - Enter: Apply approved amendment
 * - Escape: Close modal/cancel
 *
 * @see plans/self-reflective-os/
 */

import { memo, useState, useCallback, useEffect, useMemo } from 'react';
import { ChevronLeft, ChevronRight, FileText } from 'lucide-react';

import { AmendmentList } from './AmendmentList';
import { AmendmentEditor, type EditorViewMode } from './AmendmentEditor';
import { AmendmentReview } from './AmendmentReview';
import { AmendmentProposalForm } from './AmendmentProposalForm';
import type { Amendment, AmendmentFilters, AmendmentProposalInput, ReviewNote } from './types';
import { MOCK_AMENDMENTS } from './types';

import './AmendmentMode.css';

// =============================================================================
// Types
// =============================================================================

export interface AmendmentModeProps {
  /** Initial amendment ID to select */
  initialAmendmentId?: string;
  /** Callback when amendment is selected */
  onAmendmentSelect?: (id: string | null) => void;
  /** Callback when amendment is created */
  onAmendmentCreate?: (input: AmendmentProposalInput) => Promise<Amendment>;
  /** Callback when amendment is approved */
  onAmendmentApprove?: (id: string, reasoning: string) => Promise<void>;
  /** Callback when amendment is rejected */
  onAmendmentReject?: (id: string, reasoning: string) => Promise<void>;
  /** Callback when amendment is applied */
  onAmendmentApply?: (id: string) => Promise<void>;
  /** External amendments data (if not using internal state) */
  amendments?: Amendment[];
}

// =============================================================================
// Main Component
// =============================================================================

export const AmendmentMode = memo(function AmendmentMode({
  initialAmendmentId,
  onAmendmentSelect,
  onAmendmentCreate,
  onAmendmentApprove,
  onAmendmentReject,
  onAmendmentApply,
  amendments: externalAmendments,
}: AmendmentModeProps) {
  // State
  const [amendments, setAmendments] = useState<Amendment[]>(externalAmendments || MOCK_AMENDMENTS);
  const [selectedId, setSelectedId] = useState<string | null>(initialAmendmentId || null);
  const [isProposalModalOpen, setIsProposalModalOpen] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [viewMode, setViewMode] = useState<EditorViewMode>('diff');
  const [leftCollapsed, setLeftCollapsed] = useState(false);
  const [rightCollapsed, setRightCollapsed] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [filters, setFilters] = useState<AmendmentFilters>({
    status: 'all',
    searchQuery: '',
  });

  // Sync with external amendments if provided
  useEffect(() => {
    if (externalAmendments) {
      setAmendments(externalAmendments);
    }
  }, [externalAmendments]);

  // Get selected amendment
  const selectedAmendment = useMemo(
    () => amendments.find((a) => a.id === selectedId) || null,
    [amendments, selectedId]
  );

  // Handlers
  const handleSelect = useCallback(
    (id: string) => {
      setSelectedId(id);
      onAmendmentSelect?.(id);
      setIsEditing(false);
    },
    [onAmendmentSelect]
  );

  const handleNewAmendment = useCallback(() => {
    setIsProposalModalOpen(true);
  }, []);

  const handleProposalClose = useCallback(() => {
    setIsProposalModalOpen(false);
  }, []);

  const handleProposalSubmit = useCallback(
    async (input: AmendmentProposalInput) => {
      setIsLoading(true);
      try {
        if (onAmendmentCreate) {
          const newAmendment = await onAmendmentCreate(input);
          setAmendments((prev) => [newAmendment, ...prev]);
          setSelectedId(newAmendment.id);
        } else {
          // Mock implementation
          const newAmendment: Amendment = {
            id: `amend-${Date.now()}`,
            title: input.title,
            description: input.description,
            amendmentType: input.amendmentType,
            status: input.submitForReview ? 'proposed' : 'draft',
            targetKblock: input.targetKblock,
            targetLayer: input.targetLayer,
            originalContent: '// Original content would be fetched from the target K-Block',
            proposedContent: input.proposedContent,
            diff: `@@ -1 +1 @@\n-// Original content\n+${input.proposedContent.split('\n')[0]}`,
            proposer: 'kent',
            reasoning: input.reasoning,
            principlesAffected: input.principlesAffected,
            reviewNotes: [],
            createdAt: new Date().toISOString(),
            proposedAt: input.submitForReview ? new Date().toISOString() : undefined,
          };
          setAmendments((prev) => [newAmendment, ...prev]);
          setSelectedId(newAmendment.id);
        }
        setIsProposalModalOpen(false);
      } catch (error) {
        console.error('[AmendmentMode] Failed to create amendment:', error);
      } finally {
        setIsLoading(false);
      }
    },
    [onAmendmentCreate]
  );

  const handleEditStart = useCallback(() => {
    if (selectedAmendment?.status === 'draft') {
      setIsEditing(true);
    }
  }, [selectedAmendment]);

  const handleEditCancel = useCallback(() => {
    setIsEditing(false);
  }, []);

  const handleContentChange = useCallback(
    (content: string) => {
      if (!selectedId) return;
      setAmendments((prev) =>
        prev.map((a) =>
          a.id === selectedId
            ? {
                ...a,
                proposedContent: content,
                diff: `@@ -1 +1 @@\n-${a.originalContent.split('\n')[0]}\n+${content.split('\n')[0]}`,
              }
            : a
        )
      );
    },
    [selectedId]
  );

  const handleSubmitForReview = useCallback(() => {
    if (!selectedId) return;
    setAmendments((prev) =>
      prev.map((a) =>
        a.id === selectedId
          ? {
              ...a,
              status: 'proposed',
              proposedAt: new Date().toISOString(),
            }
          : a
      )
    );
    setIsEditing(false);
  }, [selectedId]);

  const handleAddNote = useCallback(
    (note: string, sentiment: ReviewNote['sentiment']) => {
      if (!selectedId) return;
      const newNote: ReviewNote = {
        id: `note-${Date.now()}`,
        reviewer: 'kent',
        note,
        timestamp: new Date().toISOString(),
        sentiment,
      };
      setAmendments((prev) =>
        prev.map((a) =>
          a.id === selectedId
            ? {
                ...a,
                status: a.status === 'proposed' ? 'under_review' : a.status,
                reviewNotes: [...a.reviewNotes, newNote],
              }
            : a
        )
      );
    },
    [selectedId]
  );

  const handleApprove = useCallback(
    async (reasoning: string) => {
      if (!selectedId) return;
      setIsLoading(true);
      try {
        if (onAmendmentApprove) {
          await onAmendmentApprove(selectedId, reasoning);
        }
        setAmendments((prev) =>
          prev.map((a) =>
            a.id === selectedId
              ? {
                  ...a,
                  status: 'approved',
                  approvalReasoning: reasoning,
                  reviewedAt: new Date().toISOString(),
                }
              : a
          )
        );
      } catch (error) {
        console.error('[AmendmentMode] Failed to approve:', error);
      } finally {
        setIsLoading(false);
      }
    },
    [selectedId, onAmendmentApprove]
  );

  const handleReject = useCallback(
    async (reasoning: string) => {
      if (!selectedId) return;
      setIsLoading(true);
      try {
        if (onAmendmentReject) {
          await onAmendmentReject(selectedId, reasoning);
        }
        setAmendments((prev) =>
          prev.map((a) =>
            a.id === selectedId
              ? {
                  ...a,
                  status: 'rejected',
                  rejectionReasoning: reasoning,
                  reviewedAt: new Date().toISOString(),
                }
              : a
          )
        );
      } catch (error) {
        console.error('[AmendmentMode] Failed to reject:', error);
      } finally {
        setIsLoading(false);
      }
    },
    [selectedId, onAmendmentReject]
  );

  const handleApply = useCallback(async () => {
    if (!selectedId) return;
    setIsLoading(true);
    try {
      if (onAmendmentApply) {
        await onAmendmentApply(selectedId);
      }
      setAmendments((prev) =>
        prev.map((a) =>
          a.id === selectedId
            ? {
                ...a,
                status: 'applied',
                appliedAt: new Date().toISOString(),
                postCommitSha: `sha-${Date.now().toString(36)}`,
              }
            : a
        )
      );
    } catch (error) {
      console.error('[AmendmentMode] Failed to apply:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedId, onAmendmentApply]);

  const handleRevert = useCallback(async () => {
    if (!selectedId) return;
    setIsLoading(true);
    try {
      setAmendments((prev) =>
        prev.map((a) =>
          a.id === selectedId
            ? {
                ...a,
                status: 'reverted',
                revertedAt: new Date().toISOString(),
              }
            : a
        )
      );
    } catch (error) {
      console.error('[AmendmentMode] Failed to revert:', error);
    } finally {
      setIsLoading(false);
    }
  }, [selectedId]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Skip if in input
      const target = e.target as HTMLElement;
      if (target.tagName === 'INPUT' || target.tagName === 'TEXTAREA' || target.isContentEditable) {
        return;
      }

      // Modal is open - only handle Escape
      if (isProposalModalOpen) {
        if (e.key === 'Escape') {
          e.preventDefault();
          setIsProposalModalOpen(false);
        }
        return;
      }

      // Global shortcuts
      if (e.key === 'n' && !e.ctrlKey && !e.metaKey) {
        e.preventDefault();
        handleNewAmendment();
      } else if (
        e.key === 'e' &&
        !e.ctrlKey &&
        !e.metaKey &&
        selectedAmendment?.status === 'draft'
      ) {
        e.preventDefault();
        handleEditStart();
      } else if (
        e.key === 'p' &&
        !e.ctrlKey &&
        !e.metaKey &&
        selectedAmendment?.status === 'draft'
      ) {
        e.preventDefault();
        handleSubmitForReview();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        if (isEditing) {
          handleEditCancel();
        } else {
          setSelectedId(null);
          onAmendmentSelect?.(null);
        }
      }

      // Review shortcuts (only when viewing proposed/under_review)
      if (selectedAmendment) {
        const canReview =
          selectedAmendment.status === 'proposed' || selectedAmendment.status === 'under_review';
        const canApply = selectedAmendment.status === 'approved';

        if (e.key === 'a' && !e.ctrlKey && !e.metaKey && canReview) {
          e.preventDefault();
          // Focus on approve button or trigger approve form
        } else if (e.key === 'r' && !e.ctrlKey && !e.metaKey && canReview) {
          e.preventDefault();
          // Focus on reject button or trigger reject form
        } else if (e.key === 'Enter' && !e.ctrlKey && !e.metaKey && canApply) {
          e.preventDefault();
          handleApply();
        }
      }

      // Panel collapse shortcuts
      if (e.key === '[') {
        e.preventDefault();
        setLeftCollapsed((prev) => !prev);
      } else if (e.key === ']') {
        e.preventDefault();
        setRightCollapsed((prev) => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    isProposalModalOpen,
    isEditing,
    selectedAmendment,
    handleNewAmendment,
    handleEditStart,
    handleEditCancel,
    handleSubmitForReview,
    handleApply,
    onAmendmentSelect,
  ]);

  return (
    <div className="amendment-mode">
      {/* Header */}
      <header className="amendment-mode__header">
        <div className="amendment-mode__header-title">
          <FileText size={16} />
          <span>Amendment Mode</span>
        </div>
        <div className="amendment-mode__header-subtitle">Constitutional change workflow</div>
      </header>

      {/* Main content */}
      <div className="amendment-mode__content">
        {/* Left Panel: Amendment List */}
        <aside
          className={`amendment-mode__left ${
            leftCollapsed ? 'amendment-mode__left--collapsed' : ''
          }`}
        >
          <button
            className="amendment-mode__collapse-btn"
            onClick={() => setLeftCollapsed(!leftCollapsed)}
            aria-label={leftCollapsed ? 'Expand list panel' : 'Collapse list panel'}
          >
            {leftCollapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
          </button>
          {!leftCollapsed && (
            <AmendmentList
              amendments={amendments}
              selectedId={selectedId}
              onSelect={handleSelect}
              onNewAmendment={handleNewAmendment}
              filters={filters}
              onFilterChange={setFilters}
              showFilters={showFilters}
              onToggleFilters={() => setShowFilters(!showFilters)}
            />
          )}
        </aside>

        {/* Center Panel: Amendment Editor */}
        <main className="amendment-mode__center">
          <AmendmentEditor
            amendment={selectedAmendment}
            viewMode={viewMode}
            onViewModeChange={setViewMode}
            isEditing={isEditing}
            onEditStart={handleEditStart}
            onEditCancel={handleEditCancel}
            onContentChange={handleContentChange}
            onSubmitForReview={handleSubmitForReview}
          />
        </main>

        {/* Right Panel: Review */}
        <aside
          className={`amendment-mode__right ${
            rightCollapsed ? 'amendment-mode__right--collapsed' : ''
          }`}
        >
          <button
            className="amendment-mode__collapse-btn"
            onClick={() => setRightCollapsed(!rightCollapsed)}
            aria-label={rightCollapsed ? 'Expand review panel' : 'Collapse review panel'}
          >
            {rightCollapsed ? <ChevronLeft size={14} /> : <ChevronRight size={14} />}
          </button>
          {!rightCollapsed && (
            <AmendmentReview
              amendment={selectedAmendment}
              onAddNote={handleAddNote}
              onApprove={handleApprove}
              onReject={handleReject}
              onApply={handleApply}
              onRevert={handleRevert}
              isLoading={isLoading}
            />
          )}
        </aside>
      </div>

      {/* Proposal Modal */}
      <AmendmentProposalForm
        isOpen={isProposalModalOpen}
        onClose={handleProposalClose}
        onSubmit={handleProposalSubmit}
        isLoading={isLoading}
      />
    </div>
  );
});

export default AmendmentMode;

// Re-export types and components
export * from './types';
export { AmendmentList } from './AmendmentList';
export { AmendmentEditor } from './AmendmentEditor';
export { AmendmentReview } from './AmendmentReview';
export { AmendmentProposalForm } from './AmendmentProposalForm';
export { DiffViewer } from './DiffViewer';
