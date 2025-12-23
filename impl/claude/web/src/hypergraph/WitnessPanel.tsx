/**
 * WitnessPanel — Mark capture UI for WITNESS mode
 *
 * Modal for capturing witnessed moments:
 * - Action (what happened)
 * - Reasoning (why it matters)
 * - Tags (common principles)
 *
 * Keyboard-first:
 * - Enter in action field → Save
 * - Esc → Cancel
 * - Tab → Navigate fields
 */

import React, { memo, useCallback, useEffect, useRef, useState } from 'react';

import './WitnessPanel.css';

// =============================================================================
// Types
// =============================================================================

interface WitnessPanelProps {
  /** Called when mark is saved */
  onSave: (action: string, reasoning?: string, tags?: string[]) => Promise<void>;

  /** Called when panel is cancelled */
  onCancel: () => void;

  /** Loading state while saving */
  loading?: boolean;
}

// Common tags for quick selection
const COMMON_TAGS = ['eureka', 'gotcha', 'taste', 'friction', 'joy', 'veto'] as const;

// =============================================================================
// Component
// =============================================================================

export const WitnessPanel = memo(function WitnessPanel({
  onSave,
  onCancel,
  loading = false,
}: WitnessPanelProps) {
  const [action, setAction] = useState('');
  const [reasoning, setReasoning] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  const actionInputRef = useRef<HTMLInputElement>(null);

  // Auto-focus action input on mount
  useEffect(() => {
    requestAnimationFrame(() => {
      actionInputRef.current?.focus();
    });
  }, []);

  // Toggle tag selection
  const toggleTag = useCallback((tag: string) => {
    setSelectedTags((prev) => {
      if (prev.includes(tag)) {
        // eslint-disable-next-line max-nested-callbacks
        return prev.filter((t) => t !== tag);
      }
      return [...prev, tag];
    });
  }, []);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!action.trim()) return;
    if (loading) return;

    await onSave(action.trim(), reasoning.trim() || undefined, selectedTags);
  }, [action, reasoning, selectedTags, onSave, loading]);

  // Handle keyboard shortcuts
  const handleActionKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLInputElement>) => {
      if (e.key === 'Enter') {
        e.preventDefault();
        handleSave();
      } else if (e.key === 'Escape') {
        e.preventDefault();
        onCancel();
      }
    },
    [handleSave, onCancel]
  );

  const handleReasoningKeyDown = useCallback(
    (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
      if (e.key === 'Escape') {
        e.preventDefault();
        onCancel();
      }
    },
    [onCancel]
  );

  // Global Escape handler (backup)
  const handleGlobalEsc = useCallback(
    (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !loading) {
        e.preventDefault();
        onCancel();
      }
    },
    [onCancel, loading]
  );

  useEffect(() => {
    window.addEventListener('keydown', handleGlobalEsc);
    return () => window.removeEventListener('keydown', handleGlobalEsc);
  }, [handleGlobalEsc]);

  return (
    <div className="witness-panel__overlay" onClick={onCancel}>
      <div className="witness-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="witness-panel__header">
          <span className="witness-panel__badge">-- WITNESS --</span>
        </div>

        {/* Action input */}
        <div className="witness-panel__field">
          <label htmlFor="witness-action" className="witness-panel__label">
            Action:
          </label>
          <input
            ref={actionInputRef}
            id="witness-action"
            type="text"
            className="witness-panel__input"
            value={action}
            onChange={(e) => setAction(e.target.value)}
            onKeyDown={handleActionKeyDown}
            placeholder="What happened?"
            disabled={loading}
            autoComplete="off"
            autoCorrect="off"
            autoCapitalize="off"
            spellCheck={false}
          />
        </div>

        {/* Reasoning textarea */}
        <div className="witness-panel__field">
          <label htmlFor="witness-reasoning" className="witness-panel__label">
            Reasoning:
          </label>
          <textarea
            id="witness-reasoning"
            className="witness-panel__textarea"
            value={reasoning}
            onChange={(e) => setReasoning(e.target.value)}
            onKeyDown={handleReasoningKeyDown}
            placeholder="Why does this matter? (optional)"
            disabled={loading}
            rows={3}
            spellCheck={false}
          />
        </div>

        {/* Tag chips */}
        <div className="witness-panel__field">
          <label className="witness-panel__label">Tags:</label>
          <div className="witness-panel__tags">
            {COMMON_TAGS.map((tag) => (
              <button
                key={tag}
                type="button"
                className={`witness-panel__tag ${selectedTags.includes(tag) ? 'witness-panel__tag--selected' : ''}`}
                onClick={() => toggleTag(tag)}
                disabled={loading}
              >
                {tag}
              </button>
            ))}
          </div>
        </div>

        {/* Footer hints */}
        <div className="witness-panel__footer">
          <span>
            <kbd>Enter</kbd> Save
          </span>
          <span className="witness-panel__separator">•</span>
          <span>
            <kbd>Esc</kbd> Cancel
          </span>
          {loading && <span className="witness-panel__loading">Saving...</span>}
        </div>
      </div>
    </div>
  );
});

export default WitnessPanel;
