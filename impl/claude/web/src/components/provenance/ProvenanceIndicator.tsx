/**
 * ProvenanceIndicator — Shows authorship at a glance
 *
 * Grounded in: spec/ui/axioms.md — A2 (Sloppification Axiom)
 * "The UI must make sloppification VISIBLE."
 *
 * Visual encoding:
 * - Kent (human): Full intensity, no indicator
 * - Fusion: Full intensity + ⚡ marker
 * - Claude (reviewed): Medium intensity + ◇ marker
 * - Claude (unreviewed): Low intensity + ◆ marker + amber border
 */

import type { Provenance } from '../../types';
import { getProvenanceClass, getProvenanceIndicator, needsReview } from '../../types';

interface ProvenanceIndicatorProps {
  /** Provenance information */
  provenance: Provenance;

  /** Inline mode (smaller, no border) */
  inline?: boolean;

  /** Show tooltip on hover */
  showTooltip?: boolean;
}

/**
 * Compact indicator showing content provenance.
 */
export function ProvenanceIndicator({
  provenance,
  inline = false,
  showTooltip = true,
}: ProvenanceIndicatorProps) {
  const indicator = getProvenanceIndicator(provenance);
  const className = getProvenanceClass(provenance);
  const requiresReview = needsReview(provenance);

  // Human content has no indicator
  if (!indicator && provenance.author === 'kent') {
    return null;
  }

  const tooltipText = getTooltipText(provenance);

  return (
    <span
      className={`provenance-indicator ${className} ${inline ? 'provenance-indicator--inline' : ''}`}
      title={showTooltip ? tooltipText : undefined}
      aria-label={tooltipText}
    >
      {indicator}
      {requiresReview && <span className="provenance-indicator__badge">needs review</span>}
    </span>
  );
}

/**
 * Get tooltip text for provenance.
 */
function getTooltipText(provenance: Provenance): string {
  const parts: string[] = [];

  // Author
  switch (provenance.author) {
    case 'kent':
      parts.push('Human authored');
      break;
    case 'fusion':
      parts.push('Dialectic synthesis');
      break;
    case 'claude':
      parts.push('AI generated');
      break;
  }

  // Review status
  if (provenance.author === 'claude') {
    if (provenance.reviewed) {
      parts.push(`Reviewed${provenance.reviewed_by ? ` by ${provenance.reviewed_by}` : ''}`);
    } else {
      parts.push('Awaiting review');
    }
  }

  // Sloppification risk
  if (provenance.sloppification_risk > 0.5) {
    parts.push(`High slop risk: ${(provenance.sloppification_risk * 100).toFixed(0)}%`);
  } else if (provenance.sloppification_risk > 0.2) {
    parts.push(`Moderate slop risk: ${(provenance.sloppification_risk * 100).toFixed(0)}%`);
  }

  // Fusion ID
  if (provenance.fusion_id) {
    parts.push(`Fusion: ${provenance.fusion_id.slice(0, 8)}...`);
  }

  return parts.join(' • ');
}

/**
 * Badge showing author with full details.
 */
export function ProvenanceBadge({ provenance }: { provenance: Provenance }) {
  const indicator = getProvenanceIndicator(provenance);
  const className = getProvenanceClass(provenance);

  return (
    <div className={`provenance-badge ${className}`}>
      <span className="provenance-badge__indicator">{indicator}</span>
      <span className="provenance-badge__author">{provenance.author}</span>
      <span className="provenance-badge__confidence">
        {(provenance.confidence * 100).toFixed(0)}%
      </span>
      {needsReview(provenance) && <span className="provenance-badge__review">needs review</span>}
    </div>
  );
}

export default ProvenanceIndicator;
