/**
 * TokenDetailPanel - Slide-out detail view (STUB)
 *
 * NOTE: The old spec ledger backend has been removed.
 * This component now shows a placeholder message.
 * Use the Document Director (/director) for document management.
 */

import './TokenDetailPanel.css';

// =============================================================================
// Types
// =============================================================================

interface TokenDetailPanelProps {
  path: string;
  onClose: () => void;
  onOpenEditor?: (path: string) => void;
}

// =============================================================================
// Component (STUB)
// =============================================================================

export function TokenDetailPanel({ path, onClose }: TokenDetailPanelProps) {
  return (
    <div className="token-detail-overlay" onClick={onClose}>
      <div
        className="token-detail-panel"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <header className="token-detail-panel__header">
          <button className="token-detail-panel__back" onClick={onClose}>
            ← Back
          </button>
        </header>

        {/* Title */}
        <div className="token-detail-panel__title-row">
          <h2 className="token-detail-panel__title">Token Detail (Unavailable)</h2>
        </div>

        <p className="token-detail-panel__path">{path}</p>

        {/* Message */}
        <div className="token-detail-panel__content" style={{ padding: '2rem', textAlign: 'center' }}>
          <p style={{ opacity: 0.7 }}>
            The spec ledger backend has been removed.
            <br />
            Use the <strong>Documents</strong> tab for document management.
          </p>
        </div>
      </div>
    </div>
  );
}
