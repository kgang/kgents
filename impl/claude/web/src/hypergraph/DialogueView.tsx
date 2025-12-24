/**
 * DialogueView — Split-pane dialectic display
 *
 * "Kent's view + Claude's view → a third thing, better than either."
 * "Adversarial cooperation—challenge is nominative, not substantive"
 *
 * Layout: [THESIS | SYNTHESIS | ANTITHESIS]
 *
 * Three-column display with editable synthesis pane.
 * Modal overlay for viewing/editing dialectical decisions.
 */

import { memo, useCallback, useEffect, useRef, useState } from 'react';
import type { DialecticDecision, FullDialecticInput } from './types/dialectic';

import './DialogueView.css';

// =============================================================================
// Types
// =============================================================================

interface DialogueViewProps {
  /** Decision to display/edit */
  decision?: DialecticDecision;

  /** Called when synthesis is saved */
  onSave?: (input: FullDialecticInput) => Promise<void>;

  /** Called when view is closed */
  onClose: () => void;

  /** Called when veto is triggered */
  onVeto?: (reason: string) => Promise<void>;

  /** Loading state */
  loading?: boolean;

  /** Edit mode (allows synthesis editing) */
  editable?: boolean;
}

// =============================================================================
// Component
// =============================================================================

export const DialogueView = memo(function DialogueView({
  decision,
  onSave,
  onClose,
  onVeto,
  loading = false,
  editable = false,
}: DialogueViewProps) {
  const [thesis, setThesis] = useState(decision?.thesis.content || '');
  const [thesisReasoning, setThesisReasoning] = useState(decision?.thesis.reasoning || '');
  const [antithesis, setAntithesis] = useState(decision?.antithesis.content || '');
  const [antithesisReasoning, setAntithesisReasoning] = useState(decision?.antithesis.reasoning || '');
  const [synthesis, setSynthesis] = useState(decision?.synthesis || '');
  const [why, setWhy] = useState(decision?.why || '');
  const [vetoReason, setVetoReason] = useState('');
  const [showVetoInput, setShowVetoInput] = useState(false);

  const synthesisRef = useRef<HTMLTextAreaElement>(null);

  // Update state when decision changes
  useEffect(() => {
    if (decision) {
      setThesis(decision.thesis.content);
      setThesisReasoning(decision.thesis.reasoning);
      setAntithesis(decision.antithesis.content);
      setAntithesisReasoning(decision.antithesis.reasoning);
      setSynthesis(decision.synthesis);
      setWhy(decision.why);
    }
  }, [decision]);

  // Focus synthesis on mount if editable
  useEffect(() => {
    if (editable && synthesisRef.current) {
      synthesisRef.current.focus();
    }
  }, [editable]);

  // Handle save
  const handleSave = useCallback(async () => {
    if (!onSave || loading) return;

    await onSave({
      thesis: {
        content: thesis,
        reasoning: thesisReasoning,
      },
      antithesis: {
        content: antithesis,
        reasoning: antithesisReasoning,
      },
      synthesis,
      why,
      tags: decision?.tags || [],
    });
  }, [onSave, thesis, thesisReasoning, antithesis, antithesisReasoning, synthesis, why, decision?.tags, loading]);

  // Handle veto
  const handleVeto = useCallback(async () => {
    if (!onVeto || loading) return;

    await onVeto(vetoReason);
    onClose();
  }, [onVeto, vetoReason, loading, onClose]);

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

  return (
    <div className="dialogue-view__overlay" onClick={onClose}>
      <div className="dialogue-view" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="dialogue-view__header">
          <h2 className="dialogue-view__title">WITNESS DIALECTIC</h2>
          <button
            className="dialogue-view__close"
            onClick={onClose}
            disabled={loading}
            title="Close (Esc)"
          >
            ×
          </button>
        </div>

        {/* Three-column layout */}
        <div className="dialogue-view__columns">
          {/* Left: Kent's Thesis */}
          <div className="dialogue-view__pane dialogue-view__thesis">
            <div className="dialogue-view__pane-header">
              <span className="dialogue-view__pane-author">KENT'S THESIS</span>
            </div>
            <div className="dialogue-view__pane-content">
              {editable ? (
                <>
                  <textarea
                    className="dialogue-view__textarea"
                    value={thesis}
                    onChange={(e) => setThesis(e.target.value)}
                    placeholder="Kent's position..."
                    disabled={loading}
                  />
                  <label className="dialogue-view__label">Reasoning:</label>
                  <textarea
                    className="dialogue-view__textarea dialogue-view__textarea--small"
                    value={thesisReasoning}
                    onChange={(e) => setThesisReasoning(e.target.value)}
                    placeholder="Why this view?"
                    disabled={loading}
                    rows={3}
                  />
                </>
              ) : (
                <>
                  <p className="dialogue-view__position">{thesis}</p>
                  {thesisReasoning && (
                    <>
                      <div className="dialogue-view__reasoning-label">Reasoning:</div>
                      <ul className="dialogue-view__reasoning">
                        {thesisReasoning.split('\n').map((line, i) => (
                          <li key={i}>{line}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Center: Synthesis (Fusion Space) */}
          <div className="dialogue-view__pane dialogue-view__synthesis">
            <div className="dialogue-view__pane-header">
              <span className="dialogue-view__pane-author">FUSION SPACE</span>
            </div>
            <div className="dialogue-view__pane-content">
              {editable ? (
                <>
                  <textarea
                    ref={synthesisRef}
                    className="dialogue-view__textarea dialogue-view__textarea--synthesis"
                    value={synthesis}
                    onChange={(e) => setSynthesis(e.target.value)}
                    placeholder="The third thing, better than either..."
                    disabled={loading}
                    rows={6}
                  />
                  <label className="dialogue-view__label">Why this synthesis?</label>
                  <textarea
                    className="dialogue-view__textarea dialogue-view__textarea--small"
                    value={why}
                    onChange={(e) => setWhy(e.target.value)}
                    placeholder="Justification for synthesis..."
                    disabled={loading}
                    rows={3}
                  />
                </>
              ) : (
                <>
                  <div className="dialogue-view__synthesis-box">
                    <p className="dialogue-view__synthesis-text">{synthesis}</p>
                  </div>
                  {why && (
                    <>
                      <div className="dialogue-view__reasoning-label">Why:</div>
                      <p className="dialogue-view__why">{why}</p>
                    </>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Right: Claude's Antithesis */}
          <div className="dialogue-view__pane dialogue-view__antithesis">
            <div className="dialogue-view__pane-header">
              <span className="dialogue-view__pane-author">CLAUDE'S ANTITHESIS</span>
            </div>
            <div className="dialogue-view__pane-content">
              {editable ? (
                <>
                  <textarea
                    className="dialogue-view__textarea"
                    value={antithesis}
                    onChange={(e) => setAntithesis(e.target.value)}
                    placeholder="Claude's position..."
                    disabled={loading}
                  />
                  <label className="dialogue-view__label">Reasoning:</label>
                  <textarea
                    className="dialogue-view__textarea dialogue-view__textarea--small"
                    value={antithesisReasoning}
                    onChange={(e) => setAntithesisReasoning(e.target.value)}
                    placeholder="Why this view?"
                    disabled={loading}
                    rows={3}
                  />
                </>
              ) : (
                <>
                  <p className="dialogue-view__position">{antithesis}</p>
                  {antithesisReasoning && (
                    <>
                      <div className="dialogue-view__reasoning-label">Reasoning:</div>
                      <ul className="dialogue-view__reasoning">
                        {antithesisReasoning.split('\n').map((line, i) => (
                          <li key={i}>{line}</li>
                        ))}
                      </ul>
                    </>
                  )}
                </>
              )}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="dialogue-view__footer">
          {/* Metadata */}
          {decision && (
            <div className="dialogue-view__meta">
              <span className="dialogue-view__timestamp">
                {new Date(decision.timestamp).toLocaleString()}
              </span>
              {decision.tags.length > 0 && (
                <div className="dialogue-view__tags">
                  {decision.tags.map((tag) => (
                    <span key={tag} className="dialogue-view__tag">
                      {tag}
                    </span>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Actions */}
          <div className="dialogue-view__actions">
            {editable && onSave && (
              <button
                className="dialogue-view__button dialogue-view__button--primary"
                onClick={handleSave}
                disabled={loading || !synthesis.trim()}
              >
                {loading ? 'Saving...' : 'Save Fusion'}
              </button>
            )}

            {onVeto && !showVetoInput && (
              <button
                className="dialogue-view__button dialogue-view__button--veto"
                onClick={() => setShowVetoInput(true)}
                disabled={loading}
              >
                VETO
              </button>
            )}

            {showVetoInput && (
              <div className="dialogue-view__veto-input">
                <input
                  type="text"
                  className="dialogue-view__input"
                  value={vetoReason}
                  onChange={(e) => setVetoReason(e.target.value)}
                  placeholder="Veto reason (optional)"
                  disabled={loading}
                  autoFocus
                />
                <button
                  className="dialogue-view__button dialogue-view__button--veto"
                  onClick={handleVeto}
                  disabled={loading}
                >
                  Confirm Veto
                </button>
                <button
                  className="dialogue-view__button"
                  onClick={() => setShowVetoInput(false)}
                  disabled={loading}
                >
                  Cancel
                </button>
              </div>
            )}

            <button
              className="dialogue-view__button"
              onClick={onClose}
              disabled={loading}
            >
              Close
            </button>
          </div>

          {/* Hints */}
          <div className="dialogue-view__hints">
            <kbd>Esc</kbd> Close
            {editable && (
              <>
                <span className="dialogue-view__separator">•</span>
                <kbd>Tab</kbd> Navigate fields
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
});

export default DialogueView;
