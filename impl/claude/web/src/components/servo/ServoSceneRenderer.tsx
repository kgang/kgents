/**
 * ServoSceneRenderer - Renders a complete SceneGraph to React
 *
 * This is the top-level renderer that:
 * - Lays out nodes according to LayoutDirective
 * - Renders edges between nodes
 * - Handles selection and interaction
 * - Applies the Living Earth theme
 *
 * @see protocols/agentese/projection/scene.py - SceneGraph
 * @see protocols/agentese/projection/warp_converters.py - Converters
 */

import { useMemo, useState, useCallback } from 'react';
import { ServoNodeRenderer, type SceneNode } from './ServoNodeRenderer';
import { ServoEdgeRenderer, type SceneEdge, type NodePosition } from './ServoEdgeRenderer';

// =============================================================================
// Types (matching SceneGraph from scene.py)
// =============================================================================

export interface LayoutDirective {
  direction: 'vertical' | 'horizontal' | 'grid' | 'free';
  mode: 'COMPACT' | 'COMFORTABLE' | 'SPACIOUS';
  gap: number;
  padding: number;
  align: 'start' | 'center' | 'end' | 'stretch';
  wrap: boolean;
}

export interface SceneGraph {
  id: string;
  nodes: SceneNode[];
  edges: SceneEdge[];
  layout: LayoutDirective;
  title: string;
  metadata: Record<string, unknown>;
  created_at: string;
}

export interface ServoSceneRendererProps {
  /** The SceneGraph to render */
  scene: SceneGraph;
  /** Currently selected node ID */
  selectedNodeId?: string | null;
  /** Callback when a node is selected */
  onNodeSelect?: (node: SceneNode) => void;
  /** Callback when a node is double-clicked */
  onNodeAction?: (node: SceneNode, action: string) => void;
  /** Show edge connections */
  showEdges?: boolean;
  /** Additional className */
  className?: string;
}

// =============================================================================
// Layout Configuration
// =============================================================================

const MODE_GAP_MULTIPLIER: Record<LayoutDirective['mode'], number> = {
  COMPACT: 0.5,
  COMFORTABLE: 1.0,
  SPACIOUS: 1.5,
};

const BASE_GAP = 16; // px
const BASE_PADDING = 16; // px

// =============================================================================
// Layout Calculation
// =============================================================================

function calculateNodePositions(
  nodes: SceneNode[],
  layout: LayoutDirective
): Map<string, NodePosition> {
  const positions = new Map<string, NodePosition>();
  const gapMultiplier = MODE_GAP_MULTIPLIER[layout.mode];
  const gap = BASE_GAP * layout.gap * gapMultiplier;
  const padding = BASE_PADDING * layout.padding;

  const nodeWidth = 200;
  const nodeHeight = 80;

  switch (layout.direction) {
    case 'horizontal': {
      let x = padding;
      nodes.forEach((node) => {
        positions.set(node.id, {
          id: node.id,
          x: x + nodeWidth / 2,
          y: padding + nodeHeight / 2,
        });
        x += nodeWidth + gap;
      });
      break;
    }

    case 'vertical': {
      let y = padding;
      nodes.forEach((node) => {
        positions.set(node.id, {
          id: node.id,
          x: padding + nodeWidth / 2,
          y: y + nodeHeight / 2,
        });
        y += nodeHeight + gap;
      });
      break;
    }

    case 'grid': {
      const cols = Math.ceil(Math.sqrt(nodes.length));
      nodes.forEach((node, i) => {
        const col = i % cols;
        const row = Math.floor(i / cols);
        positions.set(node.id, {
          id: node.id,
          x: padding + col * (nodeWidth + gap) + nodeWidth / 2,
          y: padding + row * (nodeHeight + gap) + nodeHeight / 2,
        });
      });
      break;
    }

    case 'free':
    default: {
      // For free layout, use positions from metadata or default grid
      nodes.forEach((node, i) => {
        const meta = node.metadata as { x?: number; y?: number };
        positions.set(node.id, {
          id: node.id,
          x: meta?.x ?? padding + (i % 4) * (nodeWidth + gap) + nodeWidth / 2,
          y: meta?.y ?? padding + Math.floor(i / 4) * (nodeHeight + gap) + nodeHeight / 2,
        });
      });
    }
  }

  return positions;
}

// =============================================================================
// Component
// =============================================================================

export function ServoSceneRenderer({
  scene,
  selectedNodeId,
  onNodeSelect,
  onNodeAction: _onNodeAction, // Reserved for future use
  showEdges = true,
  className = '',
}: ServoSceneRendererProps) {
  void _onNodeAction; // Silence unused warning

  // Graceful degradation: handle missing/malformed scene
  if (!scene) {
    return (
      <div className="flex items-center justify-center text-gray-500 py-8">
        <div className="text-center">
          <div className="text-2xl mb-2">🌿</div>
          <div>Scene not available</div>
        </div>
      </div>
    );
  }

  const nodes = scene.nodes ?? [];
  const edges = scene.edges ?? [];
  const layout = scene.layout ?? { direction: 'vertical', mode: 'COMFORTABLE', gap: 1, padding: 1, align: 'start', wrap: false };
  const title = scene.title ?? '';
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Calculate positions
  const positions = useMemo(() => calculateNodePositions(nodes, layout), [nodes, layout]);

  // Get container dimensions
  const containerStyle = useMemo(() => {
    const gapMultiplier = MODE_GAP_MULTIPLIER[layout.mode];
    const gap = BASE_GAP * layout.gap * gapMultiplier;
    const padding = BASE_PADDING * layout.padding;
    const nodeWidth = 200;
    const nodeHeight = 80;

    let width = padding * 2;
    let height = padding * 2;

    switch (layout.direction) {
      case 'horizontal':
        width += nodes.length * (nodeWidth + gap) - gap;
        height += nodeHeight;
        break;
      case 'vertical':
        width += nodeWidth;
        height += nodes.length * (nodeHeight + gap) - gap;
        break;
      case 'grid': {
        const cols = Math.ceil(Math.sqrt(nodes.length));
        const rows = Math.ceil(nodes.length / cols);
        width += cols * (nodeWidth + gap) - gap;
        height += rows * (nodeHeight + gap) - gap;
        break;
      }
      default:
        width = 800;
        height = 600;
    }

    return { minWidth: width, minHeight: height };
  }, [nodes.length, layout]);

  // Handle node click
  const handleNodeClick = useCallback(
    (node: SceneNode) => {
      onNodeSelect?.(node);
    },
    [onNodeSelect]
  );

  // Layout classes
  const layoutClasses = useMemo(() => {
    const base = 'relative';

    switch (layout.direction) {
      case 'horizontal':
        return `${base} flex flex-row items-${layout.align} gap-${Math.round(layout.gap * 4)}`;
      case 'vertical':
        return `${base} flex flex-col items-${layout.align} gap-${Math.round(layout.gap * 4)}`;
      case 'grid':
        return `${base} grid grid-cols-${Math.ceil(Math.sqrt(nodes.length))} gap-${Math.round(layout.gap * 4)}`;
      default:
        return base;
    }
  }, [layout, nodes.length]);

  return (
    <div
      className={`${layoutClasses} p-4 ${className}`}
      style={containerStyle}
    >
      {/* Title */}
      {title && (
        <div className="absolute top-2 left-4 text-sm font-medium text-gray-400">
          {title}
        </div>
      )}

      {/* Edges (SVG overlay for free layout) */}
      {showEdges && edges.length > 0 && layout.direction === 'free' && (
        <svg
          className="absolute inset-0 pointer-events-none overflow-visible"
          style={{ width: '100%', height: '100%' }}
        >
          {edges.map((edge) => {
            const sourcePos = positions.get(edge.source);
            const targetPos = positions.get(edge.target);
            if (!sourcePos || !targetPos) return null;

            const isHighlighted =
              hoveredNodeId === edge.source || hoveredNodeId === edge.target;

            return (
              <ServoEdgeRenderer
                key={`${edge.source}-${edge.target}`}
                edge={edge}
                sourcePos={sourcePos}
                targetPos={targetPos}
                isHighlighted={isHighlighted}
              />
            );
          })}
        </svg>
      )}

      {/* Nodes */}
      {nodes.map((node) => {
        const pos = positions.get(node.id);
        const isSelected = node.id === selectedNodeId;

        // For free layout, use absolute positioning
        const nodeStyle =
          layout.direction === 'free' && pos
            ? {
                position: 'absolute' as const,
                left: pos.x - 100, // Center horizontally
                top: pos.y - 40, // Center vertically
              }
            : undefined;

        return (
          <div
            key={node.id}
            style={nodeStyle}
            onMouseEnter={() => setHoveredNodeId(node.id)}
            onMouseLeave={() => setHoveredNodeId(null)}
          >
            <ServoNodeRenderer
              node={node}
              isSelected={isSelected}
              onClick={handleNodeClick}
            />
          </div>
        );
      })}

      {/* Empty state */}
      {nodes.length === 0 && (
        <div className="flex items-center justify-center text-gray-500 py-8">
          <div className="text-center">
            <div className="text-2xl mb-2">🌱</div>
            <div>No nodes to display</div>
          </div>
        </div>
      )}
    </div>
  );
}

ServoSceneRenderer.displayName = 'ServoSceneRenderer';
