/**
 * EdgePanel — Edge creation UI for EDGE mode
 *
 * Shows the current edge creation state:
 * - Source node
 * - Edge type (with keyboard shortcuts)
 * - Target node
 * - Confirmation
 */

import { memo } from 'react';
import type { EdgePendingState, EdgeType } from './types';
import { EDGE_TYPE_KEYS } from './types';

import './EdgePanel.css';

// =============================================================================
// Types
// =============================================================================

interface EdgePanelProps {
  edgePending: EdgePendingState;
}

// =============================================================================
// Edge Type Info
// =============================================================================

const EDGE_TYPE_LABELS: Record<EdgeType, { label: string; description: string }> = {
  defines: { label: 'defines', description: 'Source defines target concept' },
  extends: { label: 'extends', description: 'Source extends target' },
  implements: { label: 'implements', description: 'Source implements target spec' },
  references: { label: 'references', description: 'Source references target' },
  contradicts: { label: 'contradicts', description: 'Source contradicts target' },
  tests: { label: 'tests', description: 'Source tests target' },
  uses: { label: 'uses', description: 'Source uses target' },
  derives_from: { label: 'derives', description: 'Source derives from target' },
  contains: { label: 'contains', description: 'Source contains target' },
};

// =============================================================================
// Component
// =============================================================================

export const EdgePanel = memo(function EdgePanel({ edgePending }: EdgePanelProps) {
  const { sourceLabel, edgeType, targetLabel, phase } = edgePending;

  return (
    <div className="edge-panel" data-phase={phase}>
      {/* Header */}
      <div className="edge-panel__header">
        <span className="edge-panel__badge">EDGE</span>
        <span className="edge-panel__phase">
          {phase === 'select-type' && 'Select edge type'}
          {phase === 'select-target' && 'Select target node'}
          {phase === 'confirm' && 'Confirm edge creation'}
        </span>
      </div>

      {/* Edge visualization */}
      <div className="edge-panel__edge">
        <div className="edge-panel__node edge-panel__node--source">{sourceLabel}</div>
        <div className="edge-panel__arrow">
          {edgeType ? (
            <span className="edge-panel__edge-type">
              {'--['}
              {EDGE_TYPE_LABELS[edgeType].label}
              {']-->'}
            </span>
          ) : (
            <span className="edge-panel__edge-placeholder">{'--[?]-->'}</span>
          )}
        </div>
        <div
          className={`edge-panel__node edge-panel__node--target ${!targetLabel ? 'edge-panel__node--pending' : ''}`}
        >
          {targetLabel || '(select target)'}
        </div>
      </div>

      {/* Instructions based on phase */}
      <div className="edge-panel__instructions">
        {phase === 'select-type' && (
          <div className="edge-panel__type-selector">
            {Object.entries(EDGE_TYPE_KEYS).map(([key, type]) => (
              <div key={key} className="edge-panel__type-option">
                <kbd>{key}</kbd>
                <span>{EDGE_TYPE_LABELS[type].label}</span>
              </div>
            ))}
          </div>
        )}

        {phase === 'select-target' && (
          <div className="edge-panel__hints">
            <span>
              <kbd>j</kbd>/<kbd>k</kbd> navigate
            </span>
            <span>
              <kbd>Enter</kbd> select current node
            </span>
            <span>
              <kbd>Esc</kbd> cancel
            </span>
          </div>
        )}

        {phase === 'confirm' && (
          <div className="edge-panel__confirm">
            <span className="edge-panel__confirm-prompt">Create this edge?</span>
            <div className="edge-panel__confirm-actions">
              <span>
                <kbd>y</kbd> or <kbd>Enter</kbd> confirm
              </span>
              <span>
                <kbd>n</kbd> or <kbd>Esc</kbd> cancel
              </span>
            </div>
          </div>
        )}
      </div>
    </div>
  );
});

export default EdgePanel;
