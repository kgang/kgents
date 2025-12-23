/**
 * SpecGraphViewer — Reactflow-based spec graph visualization
 *
 * Interactive graph showing spec relationships with STARK BIOME theming.
 * Nodes are colored by tier, edges by relationship type.
 */

import { useCallback, useMemo } from 'react';
import ReactFlow, {
  Controls,
  Background,
  MiniMap,
  useNodesState,
  useEdgesState,
  type OnNodesChange,
  type OnEdgesChange,
  BackgroundVariant,
} from 'reactflow';
import 'reactflow/dist/style.css';

import { SpecNode } from './SpecNode';
import { SpecEdge } from './SpecEdge';
import { useSpecGraph } from './useSpecGraph';

import './SpecGraph.css';

// =============================================================================
// Types
// =============================================================================

interface SpecGraphViewerProps {
  /** Filter by status */
  statusFilter?: string;
  /** Maximum specs to show */
  limit?: number;
  /** Callback when node is clicked */
  onNodeClick?: (path: string) => void;
  /** Show minimap */
  showMinimap?: boolean;
  /** Show controls */
  showControls?: boolean;
}

// =============================================================================
// Node Types
// =============================================================================

const nodeTypes = {
  specNode: SpecNode,
};

const edgeTypes = {
  specEdge: SpecEdge,
};

// =============================================================================
// Component
// =============================================================================

export function SpecGraphViewer({
  statusFilter,
  limit = 50,
  onNodeClick,
  showMinimap = true,
  showControls = true,
}: SpecGraphViewerProps) {
  // Fetch and transform data
  const {
    nodes: initialNodes,
    edges: initialEdges,
    isLoading,
    error,
    refetch,
  } = useSpecGraph({
    statusFilter,
    limit,
  });

  // Reactflow state
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Sync when data changes
  useMemo(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  // Handle node click
  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: { id: string }) => {
      onNodeClick?.(node.id);
    },
    [onNodeClick]
  );

  // MiniMap node color based on tier
  const nodeColor = useCallback((node: { data?: { tier?: number; status?: string } }) => {
    const tier = node.data?.tier ?? 2;
    const status = node.data?.status;

    // Status override
    if (status === 'ORPHAN') return '#a65d4a';
    if (status === 'DEPRECATED') return '#5a5a64';

    // Tier colors
    const tierColors = ['#4a6b4a', '#6b8b6b', '#8a8a94', '#c4a77d', '#88C0D0'];
    return tierColors[tier] || tierColors[2];
  }, []);

  if (isLoading) {
    return (
      <div className="spec-graph-viewer spec-graph-viewer--loading">
        <div className="spec-graph-viewer__loading">
          <div className="spec-graph-viewer__spinner" />
          <span>Loading spec graph...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="spec-graph-viewer spec-graph-viewer--error">
        <div className="spec-graph-viewer__error">
          <span>Error loading graph: {error.message}</span>
          <button onClick={refetch}>Retry</button>
        </div>
      </div>
    );
  }

  if (nodes.length === 0) {
    return (
      <div className="spec-graph-viewer spec-graph-viewer--empty">
        <div className="spec-graph-viewer__empty">
          <span>No specs to display</span>
          <button onClick={refetch}>Refresh</button>
        </div>
      </div>
    );
  }

  return (
    <div className="spec-graph-viewer">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange as OnNodesChange}
        onEdgesChange={onEdgesChange as OnEdgesChange}
        onNodeClick={handleNodeClick}
        nodeTypes={nodeTypes}
        edgeTypes={edgeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.1}
        maxZoom={2}
        defaultEdgeOptions={{
          type: 'specEdge',
        }}
      >
        <Background variant={BackgroundVariant.Dots} gap={20} size={1} color="#28282f" />
        {showControls && <Controls className="spec-graph-controls" />}
        {showMinimap && (
          <MiniMap
            nodeColor={nodeColor}
            maskColor="rgba(10, 10, 12, 0.8)"
            className="spec-graph-minimap"
          />
        )}
      </ReactFlow>

      {/* Legend */}
      <div className="spec-graph-legend">
        <div className="spec-graph-legend__title">Tiers</div>
        <div className="spec-graph-legend__items">
          <div className="spec-graph-legend__item">
            <span className="spec-graph-legend__color" data-tier="0" />
            <span>Meta</span>
          </div>
          <div className="spec-graph-legend__item">
            <span className="spec-graph-legend__color" data-tier="1" />
            <span>Principles</span>
          </div>
          <div className="spec-graph-legend__item">
            <span className="spec-graph-legend__color" data-tier="2" />
            <span>Protocols</span>
          </div>
          <div className="spec-graph-legend__item">
            <span className="spec-graph-legend__color" data-tier="3" />
            <span>Agents</span>
          </div>
          <div className="spec-graph-legend__item">
            <span className="spec-graph-legend__color" data-tier="4" />
            <span>AGENTESE</span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default SpecGraphViewer;
