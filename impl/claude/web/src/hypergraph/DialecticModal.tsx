/**
 * DialecticModal — Quick decision capture
 *
 * Modal for fast dialectic decision entry.
 * Mirrors `kg decide --fast` CLI command.
 *
 * Two modes:
 * 1. Quick mode: Single decision + reasoning
 * 2. Full mode: Thesis/Antithesis/Synthesis
 *
 * Keyboard-first: Enter to submit, Esc to cancel.
 */

import { memo, useCallback, useEffect, useRef, useState } from 'react';
import type { QuickDecisionInput, FullDialecticInput } from './types/dialectic';

import './DialecticModal.css';

// =============================================================================
// Types
// =============================================================================

interface DialecticModalProps {
  /** Called when decision is saved */
  onSave: (input: QuickDecisionInput | FullDialecticInput) => Promise<void>;

  /** Called when modal is closed */
  onClose: () => void;

  /** Loading state */
  loading?: boolean;

  /** Default mode (quick or full) */
  defaultMode?: 'quick' | 'full';
}

// Common tags
const COMMON_TAGS = ['eureka', 'gotcha', 'taste', 'friction', 'joy', 'veto'] as const;

// =============================================================================
// Component
// =============================================================================

export const DialecticModal = memo(function DialecticModal({
  onSave,
  onClose,
  loading = false,
  defaultMode = 'quick',
}: DialecticModalProps) {
  const [mode, setMode] = useState<'quick' | 'full'>(defaultMode);
  const [selectedTags, setSelectedTags] = useState<string[]>([]);

  // Quick mode state
  const [quickDecision, setQuickDecision] = useState('');
  const [quickReasoning, setQuickReasoning] = useState('');

  // Full mode state
  const [thesis, setThesis] = useState('');
  const [thesisReasoning, setThesisReasoning] = useState('');
  const [antithesis, setAntithesis] = useState('');
  const [antithesisReasoning, setAntithesisReasoning] = useState('');
  const [synthesis, setSynthesis] = useState('');
  const [why, setWhy] = useState('');

  const firstInputRef = useRef<HTMLInputElement | HTMLTextAreaElement>(null);

  // Auto-focus first input on mount
  useEffect(() => {
    requestAnimationFrame(() => {
      firstInputRef.current?.focus();
    });
  }, [mode]);

  // Toggle tag
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
    if (loading) return;

    if (mode === 'quick') {
      if (!quickDecision.trim()) return;

      await onSave({
        decision: quickDecision.trim(),
        reasoning: quickReasoning.trim(),
        tags: selectedTags,
      });
    } else {
      if (!thesis.trim() || !antithesis.trim() || !synthesis.trim()) return;

      await onSave({
        thesis: {
          content: thesis.trim(),
          reasoning: thesisReasoning.trim(),
        },
        antithesis: {
          content: antithesis.trim(),
          reasoning: antithesisReasoning.trim(),
        },
        synthesis: synthesis.trim(),
        why: why.trim(),
        tags: selectedTags,
      });
    }

    onClose();
  }, [
    mode,
    quickDecision,
    quickReasoning,
    thesis,
    thesisReasoning,
    antithesis,
    antithesisReasoning,
    synthesis,
    why,
    selectedTags,
    onSave,
    onClose,
    loading,
  ]);

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !loading) {
        onClose();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onClose, loading]);

  // Check if form is valid
  const isValid =
    mode === 'quick'
      ? quickDecision.trim().length > 0
      : thesis.trim().length > 0 && antithesis.trim().length > 0 && synthesis.trim().length > 0;

  return (
    <div className="dialectic-modal__overlay" onClick={onClose}>
      <div className="dialectic-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="dialectic-modal__header">
          <span className="dialectic-modal__badge">-- DECIDE --</span>
          <div className="dialectic-modal__mode-toggle">
            <button
              className={`dialectic-modal__mode-button ${mode === 'quick' ? 'dialectic-modal__mode-button--active' : ''}`}
              onClick={() => setMode('quick')}
              disabled={loading}
            >
              Quick
            </button>
            <button
              className={`dialectic-modal__mode-button ${mode === 'full' ? 'dialectic-modal__mode-button--active' : ''}`}
              onClick={() => setMode('full')}
              disabled={loading}
            >
              Full
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="dialectic-modal__content">
          {mode === 'quick' ? (
            <>
              {/* Quick mode */}
              <div className="dialectic-modal__field">
                <label htmlFor="quick-decision" className="dialectic-modal__label">
                  Decision:
                </label>
                <input
                  ref={firstInputRef as React.RefObject<HTMLInputElement>}
                  id="quick-decision"
                  type="text"
                  className="dialectic-modal__input"
                  value={quickDecision}
                  onChange={(e) => setQuickDecision(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && e.metaKey) {
                      handleSave();
                    }
                  }}
                  placeholder="What did we decide?"
                  disabled={loading}
                  autoComplete="off"
                  autoCorrect="off"
                  autoCapitalize="off"
                  spellCheck={false}
                />
              </div>

              <div className="dialectic-modal__field">
                <label htmlFor="quick-reasoning" className="dialectic-modal__label">
                  Reasoning:
                </label>
                <textarea
                  id="quick-reasoning"
                  className="dialectic-modal__textarea"
                  value={quickReasoning}
                  onChange={(e) => setQuickReasoning(e.target.value)}
                  placeholder="Why this decision? (optional)"
                  disabled={loading}
                  rows={3}
                  spellCheck={false}
                />
              </div>
            </>
          ) : (
            <>
              {/* Full mode */}
              <div className="dialectic-modal__row">
                <div className="dialectic-modal__column">
                  <div className="dialectic-modal__field">
                    <label htmlFor="thesis" className="dialectic-modal__label">
                      Kent's Thesis:
                    </label>
                    <textarea
                      ref={firstInputRef as React.RefObject<HTMLTextAreaElement>}
                      id="thesis"
                      className="dialectic-modal__textarea"
                      value={thesis}
                      onChange={(e) => setThesis(e.target.value)}
                      placeholder="Kent's position..."
                      disabled={loading}
                      rows={3}
                      spellCheck={false}
                    />
                  </div>
                  <div className="dialectic-modal__field">
                    <label htmlFor="thesis-reasoning" className="dialectic-modal__label">
                      Reasoning:
                    </label>
                    <textarea
                      id="thesis-reasoning"
                      className="dialectic-modal__textarea dialectic-modal__textarea--small"
                      value={thesisReasoning}
                      onChange={(e) => setThesisReasoning(e.target.value)}
                      placeholder="Why this view?"
                      disabled={loading}
                      rows={2}
                      spellCheck={false}
                    />
                  </div>
                </div>

                <div className="dialectic-modal__column">
                  <div className="dialectic-modal__field">
                    <label htmlFor="antithesis" className="dialectic-modal__label">
                      Claude's Antithesis:
                    </label>
                    <textarea
                      id="antithesis"
                      className="dialectic-modal__textarea"
                      value={antithesis}
                      onChange={(e) => setAntithesis(e.target.value)}
                      placeholder="Claude's position..."
                      disabled={loading}
                      rows={3}
                      spellCheck={false}
                    />
                  </div>
                  <div className="dialectic-modal__field">
                    <label htmlFor="antithesis-reasoning" className="dialectic-modal__label">
                      Reasoning:
                    </label>
                    <textarea
                      id="antithesis-reasoning"
                      className="dialectic-modal__textarea dialectic-modal__textarea--small"
                      value={antithesisReasoning}
                      onChange={(e) => setAntithesisReasoning(e.target.value)}
                      placeholder="Why this view?"
                      disabled={loading}
                      rows={2}
                      spellCheck={false}
                    />
                  </div>
                </div>
              </div>

              <div className="dialectic-modal__field">
                <label htmlFor="synthesis" className="dialectic-modal__label">
                  Synthesis:
                </label>
                <textarea
                  id="synthesis"
                  className="dialectic-modal__textarea dialectic-modal__textarea--synthesis"
                  value={synthesis}
                  onChange={(e) => setSynthesis(e.target.value)}
                  placeholder="The third thing, better than either..."
                  disabled={loading}
                  rows={3}
                  spellCheck={false}
                />
              </div>

              <div className="dialectic-modal__field">
                <label htmlFor="why" className="dialectic-modal__label">
                  Why this synthesis?
                </label>
                <textarea
                  id="why"
                  className="dialectic-modal__textarea dialectic-modal__textarea--small"
                  value={why}
                  onChange={(e) => setWhy(e.target.value)}
                  placeholder="Justification..."
                  disabled={loading}
                  rows={2}
                  spellCheck={false}
                />
              </div>
            </>
          )}

          {/* Tags */}
          <div className="dialectic-modal__field">
            <label className="dialectic-modal__label">Tags:</label>
            <div className="dialectic-modal__tags">
              {COMMON_TAGS.map((tag) => (
                <button
                  key={tag}
                  type="button"
                  className={`dialectic-modal__tag ${selectedTags.includes(tag) ? 'dialectic-modal__tag--selected' : ''}`}
                  onClick={() => toggleTag(tag)}
                  disabled={loading}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="dialectic-modal__footer">
          <div className="dialectic-modal__actions">
            <button
              className="dialectic-modal__button dialectic-modal__button--primary"
              onClick={handleSave}
              disabled={loading || !isValid}
            >
              {loading ? 'Saving...' : 'Save Decision'}
            </button>
            <button
              className="dialectic-modal__button"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
          </div>

          <div className="dialectic-modal__hints">
            <kbd>Cmd+Enter</kbd> Save
            <span className="dialectic-modal__separator">•</span>
            <kbd>Esc</kbd> Cancel
          </div>
        </div>
      </div>
    </div>
  );
});

export default DialecticModal;
