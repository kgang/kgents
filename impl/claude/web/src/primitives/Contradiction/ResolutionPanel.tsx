/**
 * ResolutionPanel — Five resolution strategies for contradictions
 *
 * Modal-like panel presenting 5 strategies for resolving contradictions:
 * 1. Synthesis (Hegelian: third thing better than either)
 * 2. Scope (limit scope of one claim)
 * 3. Temporal (true at different times)
 * 4. Context (true in different contexts)
 * 5. Supersede (one supersedes the other)
 *
 * Philosophy: Contradictions are opportunities. Make resolution a first-class experience.
 */

import { memo, useState } from 'react';
import type { ResolutionStrategy } from './types';
import './ResolutionPanel.css';

// =============================================================================
// Types
// =============================================================================

export interface ResolutionPanelProps {
  /** Thesis statement */
  thesis: string;
  /** Antithesis statement */
  antithesis: string;
  /** Called when strategy is selected */
  onSelectStrategy: (strategy: ResolutionStrategy) => void;
  /** Suggested strategy (highlighted) */
  suggestedStrategy?: ResolutionStrategy;
  /** Called when panel is closed */
  onClose?: () => void;
  /** Loading state */
  loading?: boolean;
}

// =============================================================================
// Constants
// =============================================================================

interface StrategyInfo {
  icon: string;
  label: string;
  description: string;
  example: string;
}

const STRATEGIES: Record<ResolutionStrategy, StrategyInfo> = {
  synthesis: {
    icon: '⊕',
    label: 'Synthesis',
    description: 'Create a third thing, better than either',
    example: 'Thesis + Antithesis → Novel insight that transcends both',
  },
  scope: {
    icon: '⊂',
    label: 'Scope Limitation',
    description: 'Narrow the scope of one or both claims',
    example: '"X is always true" → "X is true in domain D"',
  },
  temporal: {
    icon: '⏱',
    label: 'Temporal Resolution',
    description: 'Both true, but at different times',
    example: '"X was true then, Y is true now"',
  },
  context: {
    icon: '⊞',
    label: 'Contextual Resolution',
    description: 'Both true, but in different contexts',
    example: '"X is true for context A, Y is true for context B"',
  },
  supersede: {
    icon: '→',
    label: 'Supersession',
    description: 'One claim supersedes the other',
    example: '"New evidence shows Y supersedes X"',
  },
};

// =============================================================================
// Component
// =============================================================================

export const ResolutionPanel = memo(function ResolutionPanel({
  thesis,
  antithesis,
  onSelectStrategy,
  suggestedStrategy,
  onClose,
  loading = false,
}: ResolutionPanelProps) {
  const [selectedStrategy, setSelectedStrategy] = useState<ResolutionStrategy | null>(
    suggestedStrategy || null
  );

  const handleSelect = (strategy: ResolutionStrategy) => {
    setSelectedStrategy(strategy);
  };

  const handleConfirm = () => {
    if (selectedStrategy) {
      onSelectStrategy(selectedStrategy);
    }
  };

  return (
    <div className="resolution-panel__overlay" onClick={onClose}>
      <div className="resolution-panel" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="resolution-panel__header">
          <h2 className="resolution-panel__title">
            <span className="resolution-panel__icon">⚡</span>
            Resolve Contradiction
          </h2>
          {onClose && (
            <button
              className="resolution-panel__close"
              onClick={onClose}
              disabled={loading}
              aria-label="Close"
            >
              ×
            </button>
          )}
        </div>

        {/* Contradiction summary */}
        <div className="resolution-panel__summary">
          <div className="resolution-panel__statement">
            <span className="resolution-panel__statement-label">Thesis:</span>
            <p className="resolution-panel__statement-text">{thesis}</p>
          </div>
          <div className="resolution-panel__vs">vs</div>
          <div className="resolution-panel__statement">
            <span className="resolution-panel__statement-label">Antithesis:</span>
            <p className="resolution-panel__statement-text">{antithesis}</p>
          </div>
        </div>

        {/* Strategy options */}
        <div className="resolution-panel__strategies">
          <h3 className="resolution-panel__subtitle">Choose Resolution Strategy:</h3>
          <div className="resolution-panel__strategy-grid">
            {(Object.entries(STRATEGIES) as [ResolutionStrategy, StrategyInfo][]).map(
              ([strategy, info]) => {
                const isSelected = selectedStrategy === strategy;
                const isSuggested = suggestedStrategy === strategy;

                return (
                  <button
                    key={strategy}
                    className="resolution-panel__strategy-card"
                    data-selected={isSelected}
                    data-suggested={isSuggested}
                    onClick={() => handleSelect(strategy)}
                    disabled={loading}
                  >
                    <div className="resolution-panel__strategy-header">
                      <span className="resolution-panel__strategy-icon">{info.icon}</span>
                      <span className="resolution-panel__strategy-label">{info.label}</span>
                      {isSuggested && (
                        <span className="resolution-panel__strategy-badge">Suggested</span>
                      )}
                    </div>
                    <p className="resolution-panel__strategy-description">{info.description}</p>
                    <p className="resolution-panel__strategy-example">{info.example}</p>
                  </button>
                );
              }
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="resolution-panel__footer">
          <button
            className="resolution-panel__button resolution-panel__button--primary"
            onClick={handleConfirm}
            disabled={!selectedStrategy || loading}
          >
            {loading ? 'Resolving...' : 'Apply Resolution'}
          </button>
          {onClose && (
            <button
              className="resolution-panel__button"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
          )}
        </div>
      </div>
    </div>
  );
});

export default ResolutionPanel;
