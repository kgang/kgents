/**
 * CrystalGraph - React-flow visualization of crystal hierarchy.
 *
 * "Crystallization is observable. Compression is public."
 *
 * Features:
 * - Force-directed layout with level-based y-anchoring
 * - Color-coded nodes by level (SESSION/DAY/WEEK/EPOCH)
 * - Animated compression edges
 * - Selection sync with detail panel
 * - Minimap and controls
 *
 * @see spec/protocols/witness-crystallization.md
 * @see services/witness/crystal_trail.py
 */

import { useCallback, useMemo, useState, useEffect } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Edge,
  type Node,
  type OnSelectionChangeParams,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';

import { crystalNodeTypes, type CrystalNodeData } from './CrystalNode';
import { CRYSTAL_LEVELS, type CrystalGraphNode, type CrystalGraphEdge, type CrystalLevel } from '../../api/crystal';

// =============================================================================
// Types
// =============================================================================

interface CrystalGraphProps {
  /** Graph nodes from API */
  nodes: CrystalGraphNode[];
  /** Graph edges from API */
  edges: CrystalGraphEdge[];
  /** Currently selected crystal ID */
  selectedCrystalId: string | null;
  /** Callback when crystal is selected */
  onSelectCrystal: (crystalId: string | null) => void;
  /** Optional className */
  className?: string;
  /** Canvas height in pixels */
  height?: number;
  /** Whether the graph is loading */
  isLoading?: boolean;
}

// =============================================================================
// Component
// =============================================================================

/**
 * CrystalGraph component.
 *
 * Renders the crystal hierarchy as an interactive force-directed graph.
 * Uses level-based y-positioning for temporal layers.
 */
export function CrystalGraph({
  nodes: inputNodes,
  edges: inputEdges,
  selectedCrystalId,
  onSelectCrystal,
  className = '',
  height = 600,
  isLoading = false,
}: CrystalGraphProps) {
  // Layout state - used for future force-directed animation
  const [_isLayouting, _setIsLayouting] = useState(false);

  // Convert to react-flow format
  const initialNodes = useMemo(() => {
    return inputNodes.map((node): Node<CrystalNodeData> => ({
      id: node.id,
      type: 'crystal',
      position: node.position,
      data: node.data as CrystalNodeData,
      selected: selectedCrystalId === node.data.crystal_id,
    }));
  }, [inputNodes, selectedCrystalId]);

  const initialEdges = useMemo(() => {
    return inputEdges.map((edge): Edge => {
      const isCompression = edge.type === 'compression';

      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label || undefined,
        type: 'smoothstep',
        animated: edge.animated,
        style: {
          stroke: isCompression ? '#8b5cf6' : '#6b7280',
          strokeWidth: 2,
          strokeDasharray: isCompression ? '5 5' : undefined,
          ...(edge.style || {}),
        },
        labelStyle: {
          fill: '#9ca3af',
          fontSize: 11,
        },
        labelBgStyle: {
          fill: '#1f2937',
          fillOpacity: 0.8,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isCompression ? '#8b5cf6' : '#6b7280',
        },
      };
    });
  }, [inputEdges]);

  // React Flow state
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);

  // Sync with external changes
  useEffect(() => {
    setNodes(initialNodes);
    setEdges(initialEdges);
  }, [initialNodes, initialEdges, setNodes, setEdges]);

  // Handle selection change
  const onSelectionChange = useCallback(
    ({ nodes: selectedNodes }: OnSelectionChangeParams) => {
      if (selectedNodes.length === 0) {
        onSelectCrystal(null);
      } else {
        const selectedNode = selectedNodes[0] as Node<CrystalNodeData>;
        if (selectedNode.data) {
          onSelectCrystal(selectedNode.data.crystal_id);
        }
      }
    },
    [onSelectCrystal]
  );

  // Handle node click
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node<CrystalNodeData>) => {
      if (node.data) {
        onSelectCrystal(node.data.crystal_id);
      }
    },
    [onSelectCrystal]
  );

  // MiniMap node color
  const minimapNodeColor = useCallback((node: Node) => {
    const data = node.data as CrystalNodeData | undefined;
    if (!data) return '#4b5563';

    const level = data.level as CrystalLevel;
    return CRYSTAL_LEVELS[level]?.color || '#4b5563';
  }, []);

  // Empty state
  if (inputNodes.length === 0 && !isLoading) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-900 rounded-lg ${className}`}
        style={{ height }}
      >
        <div className="text-center text-gray-400">
          <div className="text-4xl mb-4">💎</div>
          <div className="text-lg">No crystals yet</div>
          <div className="text-sm mt-2">Crystallization happens during session work</div>
        </div>
      </div>
    );
  }

  // Loading state
  if (isLoading) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-900 rounded-lg ${className}`}
        style={{ height }}
      >
        <motion.div
          animate={{ rotate: 360 }}
          transition={{ repeat: Infinity, duration: 2, ease: 'linear' }}
          className="text-4xl"
        >
          💎
        </motion.div>
      </div>
    );
  }

  return (
    <div
      className={`bg-gray-900 rounded-lg overflow-hidden relative ${className}`}
      style={{ height }}
    >
      {/* Level labels (left side) */}
      <div className="absolute left-2 top-0 bottom-0 z-10 flex flex-col justify-around pointer-events-none">
        {(['EPOCH', 'WEEK', 'DAY', 'SESSION'] as const).map((level) => (
          <div
            key={level}
            className="flex items-center gap-2"
          >
            <div
              className="w-2 h-2 rounded-full"
              style={{ backgroundColor: CRYSTAL_LEVELS[level].color }}
            />
            <span
              className="text-xs font-medium"
              style={{ color: CRYSTAL_LEVELS[level].color }}
            >
              {level}
            </span>
          </div>
        ))}
      </div>

      {/* Layout status */}
      {_isLayouting && (
        <div className="absolute top-3 right-3 z-10 px-2 py-1 bg-blue-900/50 rounded text-xs text-blue-300">
          Laying out...
        </div>
      )}

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={crystalNodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onSelectionChange={onSelectionChange}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{
          padding: 0.3,
          includeHiddenNodes: false,
        }}
        minZoom={0.3}
        maxZoom={2}
        defaultEdgeOptions={{
          animated: false,
        }}
        proOptions={{
          hideAttribution: true,
        }}
      >
        <Background color="#374151" gap={16} />
        <Controls
          className="!bg-gray-800 !border-gray-700"
          showInteractive={false}
        />
        <MiniMap
          className="!bg-gray-800 !border-gray-700"
          nodeColor={minimapNodeColor}
          maskColor="rgb(0, 0, 0, 0.5)"
        />
      </ReactFlow>
    </div>
  );
}

export default CrystalGraph;
