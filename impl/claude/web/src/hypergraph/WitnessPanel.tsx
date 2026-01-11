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
 * - Quick marks: mE/mG/mT/mF/mJ/mV
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

  /** Called when quick mark is triggered */
  onQuickMark?: (tag: string) => void;
}

// Common tags for quick selection
const COMMON_TAGS = ['eureka', 'gotcha', 'taste', 'friction', 'joy', 'veto'] as const;

// Quick mark definitions (tag → action template)
const QUICK_MARKS = {
  E: { tag: 'eureka', action: 'Eureka moment', key: 'mE' },
  G: { tag: 'gotcha', action: 'Gotcha', key: 'mG' },
  T: { tag: 'taste', action: 'Taste decision', key: 'mT' },
  F: { tag: 'friction', action: 'Friction point', key: 'mF' },
  J: { tag: 'joy', action: 'Joy moment', key: 'mJ' },
  V: { tag: 'veto', action: 'Veto', key: 'mV' },
} as const;

// =============================================================================
// Component
// =============================================================================

export const WitnessPanel = memo(function WitnessPanel({
  onSave,
  onCancel,
  loading = false,
  onQuickMark,
}: WitnessPanelProps) {
  const [action, setAction] = useState('');
  const [reasoning, setReasoning] = useState('');
  const [selectedTags, setSelectedTags] = useState<string[]>([]);
  const [pendingQuickMark, setPendingQuickMark] = useState<string | null>(null);

  const actionInputRef = useRef<HTMLInputElement>(null);

  // Auto-focus action input on mount
  useEffect(() => {
    requestAnimationFrame(() => {
      actionInputRef.current?.focus();
    });
  }, []);

  // Handle quick mark key sequences (m + E/G/T/F/J/V)
  useEffect(() => {
    const handleQuickMarkKey = (e: KeyboardEvent) => {
      if (loading) return;

      // If 'm' is pressed, start quick mark sequence
      if (e.key === 'm' && !pendingQuickMark) {
        e.preventDefault();
        setPendingQuickMark('m');
        return;
      }

      // If we have pending 'm', check for quick mark completion
      if (pendingQuickMark === 'm') {
        const upperKey = e.key.toUpperCase();
        const quickMark = QUICK_MARKS[upperKey as keyof typeof QUICK_MARKS];

        if (quickMark) {
          e.preventDefault();
          setPendingQuickMark(null);
          onQuickMark?.(quickMark.tag);
        } else {
          // Invalid sequence, reset
          setPendingQuickMark(null);
        }
      }
    };

    window.addEventListener('keydown', handleQuickMarkKey);
    return () => window.removeEventListener('keydown', handleQuickMarkKey);
  }, [pendingQuickMark, loading, onQuickMark]);

  // Toggle tag selection
  const toggleTag = useCallback((tag: string) => {
    setSelectedTags((prev) => {
      if (prev.includes(tag)) {
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

        {/* Quick marks section */}
        <div className="witness-panel__field">
          <label className="witness-panel__label">Quick marks:</label>
          <div className="witness-panel__quick-marks">
            {Object.entries(QUICK_MARKS).map(
              ([key, { tag, action: actionTemplate, key: keyLabel }]) => (
                <div key={key} className="witness-panel__quick-mark">
                  <kbd className="witness-panel__quick-mark-key">{keyLabel}</kbd>
                  <span className="witness-panel__quick-mark-label">
                    {tag} ({actionTemplate})
                  </span>
                </div>
              )
            )}
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
          {pendingQuickMark && (
            <>
              <span className="witness-panel__separator">•</span>
              <span className="witness-panel__pending">
                Pending: <kbd>{pendingQuickMark}_</kbd>
              </span>
            </>
          )}
          {loading && <span className="witness-panel__loading">Saving...</span>}
        </div>
      </div>
    </div>
  );
});

export default WitnessPanel;
