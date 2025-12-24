/**
 * Header — Node header display
 *
 * Shows current node title with parent/child indicators.
 */

import { memo } from 'react';
import type { GraphNode } from '../state/types';

interface HeaderProps {
  node: GraphNode | null;
}

export const Header = memo(function Header({ node }: HeaderProps) {
  if (!node) {
    return (
      <header className="hypergraph-header hypergraph-header--empty">
        <div className="hypergraph-header__title">No node focused</div>
        <div className="hypergraph-header__hint">
          Use <kbd>:e</kbd> to open a node
        </div>
      </header>
    );
  }

  const parentEdges = node.incomingEdges.filter(
    (e) => e.type === 'derives_from' || e.type === 'extends'
  );
  const childCount = node.outgoingEdges.length;

  return (
    <header className="hypergraph-header">
      {/* Parent indicator */}
      <div className="hypergraph-header__parent">
        {parentEdges.length > 0 ? (
          <>
            <span className="hypergraph-header__arrow">◀</span>
            <span className="hypergraph-header__parent-label">
              {parentEdges[0].type}: {parentEdges[0].source.split('/').pop()}
            </span>
          </>
        ) : (
          <span className="hypergraph-header__arrow hypergraph-header__arrow--dim">◀</span>
        )}
      </div>

      {/* Title */}
      <div className="hypergraph-header__title">
        {node.title || node.path.split('/').pop()}
        {node.tier && (
          <span className="hypergraph-header__tier" data-tier={node.tier}>
            {node.tier}
          </span>
        )}
      </div>

      {/* Child indicator */}
      <div className="hypergraph-header__child">
        {childCount > 0 ? (
          <>
            <span className="hypergraph-header__child-label">
              ▶ {childCount} edge{childCount > 1 ? 's' : ''}
            </span>
          </>
        ) : (
          <span className="hypergraph-header__arrow hypergraph-header__arrow--dim">▶</span>
        )}
      </div>
    </header>
  );
});
