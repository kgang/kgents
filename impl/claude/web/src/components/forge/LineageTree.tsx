/**
 * LineageTree: SVG visualization of piece inspiration graph.
 *
 * Displays:
 * - Central piece
 * - Ancestors (pieces that inspired this one)
 * - Descendants (pieces inspired by this one)
 *
 * Uses SVG for native interactivity and CSS transitions.
 * Theme: Orisinal.com - soft amber nodes, gentle connecting lines.
 */

import { useMemo } from 'react';
import type { LineageResponse, LineageNode } from '@/api/forge';

interface LineageTreeProps {
  lineage: LineageResponse;
  onNodeClick?: (pieceId: string) => void;
}

interface NodePosition {
  node: LineageNode;
  x: number;
  y: number;
  isCenter?: boolean;
}

export function LineageTree({ lineage, onNodeClick }: LineageTreeProps) {
  // Calculate node positions
  const { nodes, edges, width, height } = useMemo(() => {
    const nodeRadius = 32;
    const horizontalGap = 120;
    const verticalGap = 60;

    const positions: NodePosition[] = [];
    const edges: Array<{ from: NodePosition; to: NodePosition }> = [];

    // Center node (the piece we're viewing)
    const centerX = 200;
    const centerY = 150;
    const centerNode: NodePosition = {
      node: {
        piece_id: lineage.piece_id,
        artisan: 'Current',
        preview: '',
        depth: 0,
      },
      x: centerX,
      y: centerY,
      isCenter: true,
    };
    positions.push(centerNode);

    // Position ancestors (left side)
    const ancestors = lineage.ancestors || [];
    ancestors.forEach((node, i) => {
      const x = centerX - horizontalGap;
      const startY = centerY - ((ancestors.length - 1) * verticalGap) / 2;
      const y = startY + i * verticalGap;
      const pos: NodePosition = { node, x, y };
      positions.push(pos);
      edges.push({ from: pos, to: centerNode });
    });

    // Position descendants (right side)
    const descendants = lineage.descendants || [];
    descendants.forEach((node, i) => {
      const x = centerX + horizontalGap;
      const startY = centerY - ((descendants.length - 1) * verticalGap) / 2;
      const y = startY + i * verticalGap;
      const pos: NodePosition = { node, x, y };
      positions.push(pos);
      edges.push({ from: centerNode, to: pos });
    });

    // Calculate bounds
    const maxWidth = Math.max(400, ...positions.map((p) => p.x + nodeRadius + 50));
    const maxHeight = Math.max(300, ...positions.map((p) => p.y + nodeRadius + 50));

    return {
      nodes: positions,
      edges,
      width: maxWidth,
      height: maxHeight,
    };
  }, [lineage]);

  // Empty state
  if (nodes.length === 1 && lineage.ancestors.length === 0 && lineage.descendants.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-center">
        <span className="text-3xl text-stone-200 mb-3">◯</span>
        <p className="text-stone-400 text-sm italic">This piece stands alone—no lineage yet.</p>
      </div>
    );
  }

  return (
    <div className="overflow-x-auto">
      <svg width={width} height={height} className="select-none" style={{ minWidth: '300px' }}>
        {/* Edges */}
        <g>
          {edges.map((edge, i) => (
            <line
              key={i}
              x1={edge.from.x}
              y1={edge.from.y}
              x2={edge.to.x}
              y2={edge.to.y}
              stroke="#d6d3d1"
              strokeWidth={1.5}
              strokeDasharray="4 2"
            />
          ))}
        </g>

        {/* Nodes */}
        <g>
          {nodes.map((pos, i) => (
            <g
              key={i}
              transform={`translate(${pos.x}, ${pos.y})`}
              className="cursor-pointer"
              onClick={() => !pos.isCenter && onNodeClick?.(pos.node.piece_id)}
            >
              {/* Node circle */}
              <circle
                r={pos.isCenter ? 36 : 28}
                fill={pos.isCenter ? '#fef3c7' : '#fafaf9'}
                stroke={pos.isCenter ? '#fbbf24' : '#e7e5e4'}
                strokeWidth={pos.isCenter ? 2 : 1.5}
                className="transition-all duration-200 hover:stroke-amber-400"
              />

              {/* Artisan label */}
              <text
                y={pos.isCenter ? 4 : 3}
                textAnchor="middle"
                className={`
                  text-xs font-medium pointer-events-none
                  ${pos.isCenter ? 'fill-amber-700' : 'fill-stone-500'}
                `}
              >
                {pos.isCenter ? '◈' : pos.node.artisan.slice(0, 3)}
              </text>

              {/* Preview tooltip (on hover would need state, simplified) */}
              {!pos.isCenter && pos.node.preview && (
                <title>
                  {pos.node.artisan}: {pos.node.preview}
                </title>
              )}
            </g>
          ))}
        </g>

        {/* Labels */}
        {lineage.ancestors.length > 0 && (
          <text x={80} y={20} className="text-xs fill-stone-300">
            Ancestors
          </text>
        )}
        {lineage.descendants.length > 0 && (
          <text x={width - 100} y={20} className="text-xs fill-stone-300">
            Descendants
          </text>
        )}
      </svg>
    </div>
  );
}

export default LineageTree;
