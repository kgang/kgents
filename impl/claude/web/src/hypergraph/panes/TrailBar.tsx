/**
 * TrailBar — Navigation breadcrumb trail
 *
 * Shows the path taken through the graph.
 */

import { memo } from 'react';

interface TrailBarProps {
  trail: string;
  mode: string;
}

export const TrailBar = memo(function TrailBar({ trail, mode }: TrailBarProps) {
  return (
    <div className="hypergraph-trail">
      <span className="hypergraph-trail__label">TRAIL:</span>
      <span className="hypergraph-trail__path">{trail || '(root)'}</span>
      <span className="hypergraph-trail__mode">[{mode.charAt(0)}]</span>
    </div>
  );
});
