/**
 * ContradictionPolaroid — Side-by-side comparison of contradicting elements
 *
 * Visual metaphor: Two polaroid photos placed side by side.
 * Shows thesis vs antithesis with resolution options.
 *
 * Philosophy: Make the tension visible. Make synthesis inviting.
 */

import { memo } from 'react';
import type { ResolutionStrategy } from './types';
import './ContradictionPolaroid.css';

// =============================================================================
// Types
// =============================================================================

export type ContradictionType = 'genuine' | 'productive' | 'apparent';

export interface ContradictionPolaroidProps {
  /** Thesis (first position) */
  thesis: {
    content: string;
    source?: string;
  };
  /** Antithesis (opposing position) */
  antithesis: {
    content: string;
    source?: string;
  };
  /** Type of contradiction */
  contradictionType: ContradictionType;
  /** Called when user clicks resolve */
  onResolve?: (strategy: ResolutionStrategy) => void;
  /** Show resolution actions */
  showActions?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

const TYPE_LABELS: Record<ContradictionType, string> = {
  genuine: 'Genuine Contradiction',
  productive: 'Productive Tension',
  apparent: 'Apparent Contradiction',
};

const TYPE_ICONS: Record<ContradictionType, string> = {
  genuine: '⚡',
  productive: '⇌',
  apparent: '≈',
};

// =============================================================================
// Component
// =============================================================================

export const ContradictionPolaroid = memo(function ContradictionPolaroid({
  thesis,
  antithesis,
  contradictionType,
  onResolve,
  showActions = true,
}: ContradictionPolaroidProps) {
  const typeLabel = TYPE_LABELS[contradictionType];
  const typeIcon = TYPE_ICONS[contradictionType];

  return (
    <div className="contradiction-polaroid" data-type={contradictionType}>
      {/* Header */}
      <div className="contradiction-polaroid__header">
        <span className="contradiction-polaroid__icon">{typeIcon}</span>
        <span className="contradiction-polaroid__label">{typeLabel}</span>
      </div>

      {/* Side-by-side comparison */}
      <div className="contradiction-polaroid__cards">
        {/* Thesis card */}
        <div className="contradiction-polaroid__card contradiction-polaroid__card--thesis">
          <div className="contradiction-polaroid__card-header">
            <span className="contradiction-polaroid__card-label">Thesis</span>
            {thesis.source && (
              <span className="contradiction-polaroid__card-source" title={thesis.source}>
                {thesis.source}
              </span>
            )}
          </div>
          <div className="contradiction-polaroid__card-content">{thesis.content}</div>
        </div>

        {/* VS indicator */}
        <div className="contradiction-polaroid__vs">
          <span className="contradiction-polaroid__vs-text">vs</span>
        </div>

        {/* Antithesis card */}
        <div className="contradiction-polaroid__card contradiction-polaroid__card--antithesis">
          <div className="contradiction-polaroid__card-header">
            <span className="contradiction-polaroid__card-label">Antithesis</span>
            {antithesis.source && (
              <span className="contradiction-polaroid__card-source" title={antithesis.source}>
                {antithesis.source}
              </span>
            )}
          </div>
          <div className="contradiction-polaroid__card-content">{antithesis.content}</div>
        </div>
      </div>

      {/* Resolution actions */}
      {showActions && onResolve && (
        <div className="contradiction-polaroid__actions">
          <button
            className="contradiction-polaroid__action-button"
            onClick={() => onResolve('synthesis')}
            title="Hegelian synthesis: A third thing, better than either"
          >
            Synthesize
          </button>
          <button
            className="contradiction-polaroid__action-button"
            onClick={() => onResolve('scope')}
            title="Limit the scope of one claim"
          >
            Scope
          </button>
          <button
            className="contradiction-polaroid__action-button"
            onClick={() => onResolve('temporal')}
            title="True at different times"
          >
            Temporal
          </button>
          <button
            className="contradiction-polaroid__action-button"
            onClick={() => onResolve('context')}
            title="True in different contexts"
          >
            Context
          </button>
          <button
            className="contradiction-polaroid__action-button"
            onClick={() => onResolve('supersede')}
            title="One supersedes the other"
          >
            Supersede
          </button>
        </div>
      )}
    </div>
  );
});

export default ContradictionPolaroid;
