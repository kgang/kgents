/**
 * TrailGraph - react-flow visualization of exploration trails.
 *
 * "Bush's Memex realized: Force-directed graph showing exploration trails."
 *
 * Features:
 * - Force-directed layout with d3-force physics
 * - Custom context nodes with edge coloring
 * - Selection sync with ReasoningPanel
 * - Minimap and controls
 * - Semantic edges with longer springs (conceptual distance)
 *
 * @see brainstorming/visual-trail-graph-r&d.md
 * @see spec/protocols/trail-protocol.md Section 8
 */

import { useCallback, useMemo } from 'react';
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

import { nodeTypes, type ContextNodeData, getEdgeColor } from './ContextNode';
import { useForceLayout } from '../../hooks/useForceLayout';
import type { TrailGraphNode, TrailGraphEdge } from '../../api/trail';

// =============================================================================
// Constants
// =============================================================================

/**
 * Colors for evidence strength levels in minimap.
 */
const EVIDENCE_COLORS = {
  root: '#22c55e', // Green for starting point
  visited: '#3b82f6', // Blue for visited
  current: '#a855f7', // Purple for current/selected
  default: '#4b5563', // Gray fallback
} as const;

// =============================================================================
// Types
// =============================================================================

interface TrailGraphProps {
  /** Graph nodes from useTrail hook */
  nodes: TrailGraphNode[];
  /** Graph edges from useTrail hook */
  edges: TrailGraphEdge[];
  /** Currently selected step index */
  selectedStep: number | null;
  /** Callback when step is selected via node click */
  onSelectStep: (stepIndex: number | null) => void;
  /** Optional className */
  className?: string;
  /** Enable force-directed layout (default: true) */
  forceLayout?: boolean;
  /** Canvas height in pixels */
  height?: number;
}

// =============================================================================
// Component
// =============================================================================

/**
 * TrailGraph component.
 *
 * Renders the exploration trail as an interactive force-directed graph.
 * Uses d3-force physics for organic, knowledge-topology-revealing layout.
 */
export function TrailGraph({
  nodes: inputNodes,
  edges: inputEdges,
  selectedStep,
  onSelectStep,
  className = '',
  forceLayout = true,
  height = 600,
}: TrailGraphProps) {
  // Apply force-directed layout
  const { layoutNodes, isSimulating, runSimulation } = useForceLayout(
    inputNodes,
    inputEdges,
    {
      width: 800,
      height,
      animated: false,
    }
  );

  // Use force-laid-out nodes if enabled, otherwise use input positions
  const positionedNodes = forceLayout ? layoutNodes : inputNodes;

  // Convert to react-flow format
  const initialNodes = useMemo(() => {
    return positionedNodes.map((node): Node<ContextNodeData> => ({
      id: node.id,
      type: 'context',
      position: node.position,
      data: {
        path: node.data.path,
        holon: node.data.holon,
        step_index: node.data.step_index,
        edge_type: node.data.edge_type,
        reasoning: node.data.reasoning,
        is_current: selectedStep === node.data.step_index,
      },
      selected: selectedStep === node.data.step_index,
    }));
  }, [positionedNodes, selectedStep]);

  // Find node ID for selected step (for edge highlighting)
  const selectedNodeId = useMemo(() => {
    if (selectedStep === null) return null;
    const node = positionedNodes.find((n) => n.data.step_index === selectedStep);
    return node?.id || null;
  }, [positionedNodes, selectedStep]);

  const initialEdges = useMemo(() => {
    return inputEdges.map((edge): Edge => {
      // Highlight edges connected to selected node
      const isHighlighted = selectedNodeId
        ? edge.source === selectedNodeId || edge.target === selectedNodeId
        : false;

      const baseColor = edge.type === 'semantic' ? '#06b6d4' : '#6b7280';
      const highlightColor = '#a855f7'; // Purple for selection

      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label || undefined,
        type: edge.type === 'semantic' ? 'smoothstep' : 'default',
        animated: edge.animated || isHighlighted, // Animate highlighted edges
        style: {
          stroke: isHighlighted ? highlightColor : baseColor,
          strokeWidth: isHighlighted ? 3 : 2,
          filter: isHighlighted ? 'drop-shadow(0 0 6px rgba(168, 85, 247, 0.6))' : undefined,
          transition: 'stroke 0.2s, stroke-width 0.2s',
          ...(edge.style || {}),
        },
        labelStyle: {
          fill: isHighlighted ? '#c084fc' : '#9ca3af',
          fontSize: 11,
          fontWeight: isHighlighted ? 600 : 400,
        },
        labelBgStyle: {
          fill: '#1f2937',
          fillOpacity: 0.9,
        },
        markerEnd: {
          type: MarkerType.ArrowClosed,
          color: isHighlighted ? highlightColor : baseColor,
        },
      };
    });
  }, [inputEdges, selectedNodeId]);

  // React Flow state
  const [nodes, , onNodesChange] = useNodesState(initialNodes);
  const [edges, , onEdgesChange] = useEdgesState(initialEdges);

  // Handle selection change
  const onSelectionChange = useCallback(
    ({ nodes: selectedNodes }: OnSelectionChangeParams) => {
      if (selectedNodes.length === 0) {
        onSelectStep(null);
      } else {
        const selectedNode = selectedNodes[0] as Node<ContextNodeData>;
        if (selectedNode.data) {
          onSelectStep(selectedNode.data.step_index);
        }
      }
    },
    [onSelectStep]
  );

  // Handle node click
  const onNodeClick = useCallback(
    (_: React.MouseEvent, node: Node<ContextNodeData>) => {
      if (node.data) {
        onSelectStep(node.data.step_index);
      }
    },
    [onSelectStep]
  );

  // Empty state - inspiring visualization
  if (inputNodes.length === 0) {
    return (
      <div
        className={`flex items-center justify-center bg-gray-900 rounded-lg ${className}`}
        style={{ height }}
      >
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
        >
          {/* Constellation-like visualization */}
          <div className="relative w-32 h-32 mx-auto mb-6">
            {[0, 1, 2, 3, 4].map((i) => (
              <motion.div
                key={i}
                className="absolute w-3 h-3 rounded-full bg-gray-600"
                style={{
                  left: `${50 + 40 * Math.cos((i * 2 * Math.PI) / 5)}%`,
                  top: `${50 + 40 * Math.sin((i * 2 * Math.PI) / 5)}%`,
                }}
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.4, 0.8, 0.4],
                }}
                transition={{
                  duration: 2,
                  delay: i * 0.3,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
            ))}
            {/* Center node */}
            <motion.div
              className="absolute w-4 h-4 rounded-full bg-blue-500/40 left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            />
          </div>
          <div className="text-lg text-gray-300 font-medium">No trail loaded</div>
          <div className="text-sm text-gray-500 mt-2">
            Select a trail to visualize its knowledge topology
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div
      className={`bg-gray-900 rounded-lg overflow-hidden relative ${className}`}
      style={{ height }}
    >
      {/* Layout controls */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-2">
        {isSimulating && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            className="px-3 py-1.5 bg-blue-900/60 backdrop-blur-sm rounded-full text-xs text-blue-300 flex items-center gap-2"
          >
            <motion.span
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              ⚛️
            </motion.span>
            Simulating physics...
          </motion.div>
        )}
        <motion.button
          onClick={runSimulation}
          disabled={isSimulating}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          className="px-3 py-1.5 bg-gray-800 hover:bg-gray-700 disabled:bg-gray-800/50 disabled:cursor-not-allowed rounded-full text-xs text-gray-300 transition-colors flex items-center gap-1.5 border border-gray-700 hover:border-gray-600"
          title="Re-run force simulation to redistribute nodes"
        >
          <span>🔄</span>
          Redistribute
        </motion.button>
      </div>

      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onSelectionChange={onSelectionChange}
        onNodeClick={onNodeClick}
        fitView
        fitViewOptions={{
          padding: 0.2,
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
          nodeColor={(node) => {
            const data = node.data as ContextNodeData | undefined;
            // Current/selected gets purple
            if (data?.is_current) return EVIDENCE_COLORS.current;
            // Root node (step 0) gets green
            if (data?.step_index === 0) return EVIDENCE_COLORS.root;
            // Edge type determines color for visited nodes
            if (data?.edge_type) return getEdgeColor(data.edge_type);
            return EVIDENCE_COLORS.default;
          }}
          maskColor="rgb(0, 0, 0, 0.5)"
          nodeStrokeWidth={2}
        />
      </ReactFlow>
    </div>
  );
}

export default TrailGraph;
