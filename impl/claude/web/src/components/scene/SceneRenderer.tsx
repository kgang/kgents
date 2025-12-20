/**
 * SceneRenderer - Renders a SceneGraph to React components.
 *
 * WARP Phase 2: React Projection Layer.
 *
 * The SceneGraph IS the ontology. This component interprets:
 * - LayoutDirective → Tailwind flex/grid classes
 * - SceneNode[] → Component composition
 * - NodeStyle → Joy-inducing animations
 *
 * Laws preserved:
 * - Law 1 (Identity): Empty graphs render nothing
 * - Law 2 (Associativity): Node order preserved
 * - Law 3 (Immutability): Props are read-only
 *
 * @example
 * <SceneRenderer
 *   graph={sceneGraph}
 *   onNodeClick={(id) => console.log('Clicked:', id)}
 * />
 */

import React from 'react';
import type { LayoutDirective, SceneRendererProps } from '../../api/types/_generated/world-scenery';
import { SceneNodeComponent } from './SceneNodeComponent';

// =============================================================================
// Layout Interpretation
// =============================================================================

/**
 * Convert LayoutDirective to Tailwind classes.
 */
function getLayoutClasses(layout: LayoutDirective): string {
  // Direction
  const directionClasses: Record<string, string> = {
    vertical: 'flex flex-col',
    horizontal: 'flex flex-row',
    grid: 'grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3',
    free: 'relative',
  };

  // Gap (scaled: 1.0 = gap-4)
  const gapValue = Math.round(layout.gap * 4);
  const gapClass = `gap-${Math.min(gapValue, 12)}`;

  // Alignment
  const alignClasses: Record<string, string> = {
    start: 'items-start',
    center: 'items-center',
    end: 'items-end',
    stretch: 'items-stretch',
  };

  // Mode-specific adjustments
  const modeClasses: Record<string, string> = {
    COMPACT: 'p-2',
    COMFORTABLE: 'p-4',
    SPACIOUS: 'p-6',
  };

  const classes = [
    directionClasses[layout.direction] || 'flex flex-col',
    gapClass,
    alignClasses[layout.align] || 'items-start',
    modeClasses[layout.mode] || 'p-4',
  ];

  // Wrap for horizontal layouts
  if (layout.direction === 'horizontal' && layout.wrap) {
    classes.push('flex-wrap');
  }

  return classes.join(' ');
}

// =============================================================================
// SceneRenderer Component
// =============================================================================

export function SceneRenderer({
  graph,
  onNodeClick,
  className = '',
}: SceneRendererProps): React.ReactElement | null {
  // Law 1: Empty graphs render nothing
  if (!graph || graph.nodes.length === 0) {
    return null;
  }

  const layoutClasses = getLayoutClasses(graph.layout);

  return (
    <div
      className={`scene-renderer ${layoutClasses} ${className}`}
      data-scene-id={graph.id}
      data-scene-title={graph.title}
    >
      {graph.nodes.map((node) => (
        <SceneNodeComponent key={node.id} node={node} onClick={onNodeClick} />
      ))}
    </div>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default SceneRenderer;
export { getLayoutClasses };
