/**
 * EdgeGutter — Vertical edge badges
 *
 * Shows grouped edges on left (incoming) and right (outgoing) sides.
 * Badges show:
 * - Edge type abbreviation
 * - Count if multiple edges of same type
 * - Confidence level (color)
 * - Witness mark indicator (if present)
 */

import { memo } from 'react';
import type { Edge, EdgeType } from '../state/types';

interface EdgeGutterProps {
  edges: Edge[];
  side: 'left' | 'right';
  onEdgeClick?: (edge: Edge) => void;
}

/**
 * Calculate average confidence for a group of edges.
 * Returns undefined if no edges have confidence values.
 */
function getAverageConfidence(edges: Edge[]): number | undefined {
  const withConfidence = edges.filter((e) => e.confidence !== undefined);
  if (withConfidence.length === 0) return undefined;
  return withConfidence.reduce((sum, e) => sum + e.confidence!, 0) / withConfidence.length;
}

/**
 * Get CSS class for confidence level.
 * Maps 0-1 confidence to visual indicator.
 */
function getConfidenceClass(confidence: number | undefined): string {
  if (confidence === undefined) return 'edge-gutter__badge--unknown';
  if (confidence >= 0.8) return 'edge-gutter__badge--high';
  if (confidence >= 0.5) return 'edge-gutter__badge--medium';
  return 'edge-gutter__badge--low';
}

/**
 * Get short abbreviation for edge type.
 */
function getEdgeAbbreviation(type: EdgeType): string {
  const abbrevs: Record<EdgeType, string> = {
    implements: 'imp',
    tests: 'tst',
    extends: 'ext',
    derives_from: 'der',
    references: 'ref',
    contradicts: '!!!',
    contains: 'con',
    uses: 'use',
    defines: 'def',
  };
  return abbrevs[type] || type.slice(0, 3);
}

export const EdgeGutter = memo(function EdgeGutter({ edges, side, onEdgeClick }: EdgeGutterProps) {
  // Group edges by type
  const grouped = edges.reduce(
    (acc, edge) => {
      if (!acc[edge.type]) acc[edge.type] = [];
      acc[edge.type].push(edge);
      return acc;
    },
    {} as Record<EdgeType, Edge[]>
  );

  const types = Object.keys(grouped) as EdgeType[];

  if (types.length === 0) {
    return <div className={`edge-gutter edge-gutter--${side} edge-gutter--empty`} />;
  }

  return (
    <div className={`edge-gutter edge-gutter--${side}`}>
      {types.map((type) => {
        const typeEdges = grouped[type];
        const count = typeEdges.length;
        const abbrev = getEdgeAbbreviation(type);
        const avgConfidence = getAverageConfidence(typeEdges);
        const confidenceClass = getConfidenceClass(avgConfidence);

        // Collect unique origins for tooltip
        const origins = [...new Set(typeEdges.map((e) => e.origin).filter(Boolean))];
        const hasWitness = typeEdges.some((e) => e.markId);

        // Build rich tooltip
        const tooltip = [
          `${type}: ${count} edge${count > 1 ? 's' : ''}`,
          avgConfidence !== undefined ? `Confidence: ${Math.round(avgConfidence * 100)}%` : null,
          origins.length > 0 ? `Sources: ${origins.join(', ')}` : null,
          hasWitness ? '📜 Has witness marks' : null,
        ]
          .filter(Boolean)
          .join('\n');

        return (
          <button
            key={type}
            className={`edge-gutter__badge ${confidenceClass}`}
            data-edge-type={type}
            data-has-witness={hasWitness}
            onClick={() => onEdgeClick?.(typeEdges[0])}
            title={tooltip}
          >
            <span className="edge-gutter__abbrev">{abbrev}</span>
            {count > 1 && <span className="edge-gutter__count">{count}</span>}
            {hasWitness && <span className="edge-gutter__witness">📜</span>}
          </button>
        );
      })}
    </div>
  );
});
