/**
 * EdgeMarkPreview — Tooltip-style witness mark preview for edges
 *
 * Shows decision mark details when hovering over witnessed edges:
 * - Proof summary (claim, warrant, tier)
 * - Context/reasoning
 * - Confidence as percentage
 *
 * Returns null if edge has no mark_id (not all edges are witnessed).
 */

import { memo } from 'react';

import './EdgeMarkPreview.css';

// =============================================================================
// Types
// =============================================================================

interface EdgeMarkPreviewProps {
  edge: {
    id: string;
    mark_id?: string | null;
    proof?: {
      data: string;
      warrant: string;
      claim: string;
      backing?: string;
      qualifier?: string;
      rebuttals?: string[];
      tier?: string;
      principles?: string[];
    } | null;
    evidence_tier?: string | null;
    context?: string;
    confidence?: number;
  };
}

// =============================================================================
// Component
// =============================================================================

export const EdgeMarkPreview = memo(function EdgeMarkPreview({
  edge,
}: EdgeMarkPreviewProps) {
  // Only show if edge has a witness mark
  if (!edge.mark_id) {
    return null;
  }

  const { proof, evidence_tier, context, confidence } = edge;

  return (
    <div className="edge-mark-preview">
      {/* Header */}
      <div className="edge-mark-preview__header">
        <span className="edge-mark-preview__badge">Decision Mark</span>
        {evidence_tier && (
          <span className="edge-mark-preview__tier">{evidence_tier}</span>
        )}
      </div>

      {/* Proof summary */}
      {proof && (
        <div className="edge-mark-preview__section">
          <div className="edge-mark-preview__claim">{proof.claim}</div>
          {proof.warrant && (
            <div className="edge-mark-preview__warrant">
              <span className="edge-mark-preview__label">Warrant:</span>{' '}
              {proof.warrant}
            </div>
          )}
          {proof.data && (
            <div className="edge-mark-preview__data">
              <span className="edge-mark-preview__label">Data:</span> {proof.data}
            </div>
          )}
        </div>
      )}

      {/* Context */}
      {context && (
        <div className="edge-mark-preview__section">
          <div className="edge-mark-preview__label">Context:</div>
          <div className="edge-mark-preview__context">{context}</div>
        </div>
      )}

      {/* Confidence */}
      {confidence !== undefined && (
        <div className="edge-mark-preview__footer">
          <span className="edge-mark-preview__label">Confidence:</span>{' '}
          <span className="edge-mark-preview__confidence">
            {Math.round(confidence * 100)}%
          </span>
        </div>
      )}
    </div>
  );
});

export default EdgeMarkPreview;
