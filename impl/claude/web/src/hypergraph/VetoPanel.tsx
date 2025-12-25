/**
 * VetoPanel — Kent's disgust veto interface
 *
 * "The veto is sacred. It preserves taste."
 *
 * Prominent VETO button for Kent's disgust response.
 * Optional reasoning capture.
 */

import { memo, useCallback, useEffect, useRef, useState } from 'react';

import './VetoPanel.css';

// =============================================================================
// Types
// =============================================================================

interface VetoPanelProps {
  /** Called when veto is confirmed */
  onVeto: (reason?: string) => Promise<void>;

  /** Called when veto is cancelled */
  onCancel: () => void;

  /** Loading state */
  loading?: boolean;

  /** Optional context message */
  message?: string;
}

// =============================================================================
// Component
// =============================================================================

export const VetoPanel = memo(function VetoPanel({
  onVeto,
  onCancel,
  loading = false,
  message,
}: VetoPanelProps) {
  const [reason, setReason] = useState('');
  const [confirmed, setConfirmed] = useState(false);

  const reasonInputRef = useRef<HTMLTextAreaElement>(null);

  // Auto-focus reason input on mount
  useEffect(() => {
    requestAnimationFrame(() => {
      reasonInputRef.current?.focus();
    });
  }, []);

  // Handle veto confirmation
  const handleVeto = useCallback(async () => {
    if (loading) return;

    setConfirmed(true);

    try {
      await onVeto(reason.trim() || undefined);
    } finally {
      setConfirmed(false);
    }
  }, [onVeto, reason, loading]);

  // Handle Escape key
  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && !loading) {
        onCancel();
      }
    };

    window.addEventListener('keydown', handleEscape);
    return () => window.removeEventListener('keydown', handleEscape);
  }, [onCancel, loading]);

  return (
    <div className="veto-panel__overlay" onClick={onCancel}>
      <div className="veto-panel" onClick={(e) => e.stopPropagation()}>
        {/* Icon */}
        <div className="veto-panel__icon">⊗</div>

        {/* Header */}
        <div className="veto-panel__header">
          <h2 className="veto-panel__title">VETO</h2>
          <p className="veto-panel__subtitle">
            {message || 'Exercise disgust veto'}
          </p>
        </div>

        {/* Reason input */}
        <div className="veto-panel__field">
          <label htmlFor="veto-reason" className="veto-panel__label">
            Reason (optional):
          </label>
          <textarea
            ref={reasonInputRef}
            id="veto-reason"
            className="veto-panel__textarea"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="Why veto? (optional)"
            disabled={loading}
            rows={3}
            spellCheck={false}
          />
        </div>

        {/* Actions */}
        <div className="veto-panel__actions">
          <button
            className="veto-panel__button veto-panel__button--veto"
            onClick={handleVeto}
            disabled={loading || confirmed}
          >
            {loading || confirmed ? 'Vetoing...' : 'CONFIRM VETO'}
          </button>
          <button
            className="veto-panel__button veto-panel__button--cancel"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </button>
        </div>

        {/* Hints */}
        <div className="veto-panel__hints">
          <kbd>Esc</kbd> Cancel
        </div>
      </div>
    </div>
  );
});

export default VetoPanel;
