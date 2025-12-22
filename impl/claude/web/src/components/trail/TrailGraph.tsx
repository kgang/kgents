/**
 * TrailGraph - react-flow visualization of exploration trails.
 *
 * "Bush's Memex realized: Force-directed graph showing exploration trails."
 * "The aesthetic is the structure perceiving itself. Beauty is not revealed—it breathes."
 *
 * Living Earth Aesthetic (Crown Jewels Genesis):
 * - Warm earth-tone canvas background
 * - Organic edge colors (copper, sage, amber)
 * - Breathing nodes with lantern glow
 *
 * Features:
 * - Force-directed layout with d3-force physics
 * - Custom context nodes with organic edge coloring
 * - Selection sync with ReasoningPanel
 * - Minimap and controls
 * - Semantic edges with longer springs (conceptual distance)
 *
 * @see brainstorming/visual-trail-graph-r&d.md
 * @see spec/protocols/trail-protocol.md Section 8
 * @see creative/crown-jewels-genesis-moodboard.md
 */

import { useCallback, useMemo, useState } from 'react';
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  type Edge,
  type Node,
  type OnSelectionChangeParams,
  type Viewport,
  useNodesState,
  useEdgesState,
  MarkerType,
} from 'reactflow';
import 'reactflow/dist/style.css';
import { motion } from 'framer-motion';

import { nodeTypes, type ContextNodeData, type ZoomLevel, getEdgeColor } from './ContextNode';
import { LIVING_EARTH, BACKGROUNDS, GROWING, glowShadow } from './living-earth';
import { useForceLayout } from '../../hooks/useForceLayout';
import type { TrailGraphNode, TrailGraphEdge } from '../../api/trail';

// =============================================================================
// Constants
// =============================================================================

/**
 * Colors for evidence strength levels in minimap.
 * Living Earth palette for organic feel.
 */
const EVIDENCE_COLORS = {
  root: LIVING_EARTH.sage, // Green for starting point
  visited: LIVING_EARTH.copper, // Warm copper for visited
  current: LIVING_EARTH.lantern, // Lantern glow for current
  default: LIVING_EARTH.clay, // Neutral clay fallback
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
  const { layoutNodes, isSimulating, runSimulation } = useForceLayout(inputNodes, inputEdges, {
    width: 800,
    height,
    animated: false,
  });

  // Use force-laid-out nodes if enabled, otherwise use input positions
  const positionedNodes = forceLayout ? layoutNodes : inputNodes;

  // Zoom level state for detail rendering (Session 3)
  const [zoomLevel, setZoomLevel] = useState<ZoomLevel>('medium');

  // Compute zoom level from viewport zoom
  const computeZoomLevel = useCallback((zoom: number): ZoomLevel => {
    if (zoom < 0.7) return 'far';
    if (zoom > 1.1) return 'close';
    return 'medium';
  }, []);

  // Handle viewport changes
  const onMoveEnd = useCallback(
    (_: unknown, viewport: Viewport) => {
      const newZoomLevel = computeZoomLevel(viewport.zoom);
      if (newZoomLevel !== zoomLevel) {
        setZoomLevel(newZoomLevel);
      }
    },
    [computeZoomLevel, zoomLevel]
  );

  // Convert to react-flow format with zoom-dependent detail
  const initialNodes = useMemo(() => {
    return positionedNodes.map(
      (node): Node<ContextNodeData> => ({
        id: node.id,
        type: 'context',
        position: node.position,
        data: {
          path: node.data.path,
          holon: node.data.holon,
          step_index: node.data.step_index,
          parent_index: node.data.parent_index,
          edge_type: node.data.edge_type,
          reasoning: node.data.reasoning,
          is_current: selectedStep === node.data.step_index,
          zoom_level: zoomLevel, // Session 3: zoom-dependent rendering
        },
        selected: selectedStep === node.data.step_index,
      })
    );
  }, [positionedNodes, selectedStep, zoomLevel]);

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

      // Living Earth: Organic edge colors
      const baseColor = getEdgeColor(edge.label || null);
      const highlightColor = LIVING_EARTH.lantern; // Warm lantern glow for selection

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
          // Living Earth: Warm glow instead of purple (40% subtler)
          filter: isHighlighted ? `drop-shadow(0 0 5px ${LIVING_EARTH.lantern}4D)` : undefined,
          transition: 'stroke 0.3s, stroke-width 0.3s, filter 0.3s',
          ...(edge.style || {}),
        },
        labelStyle: {
          fill: isHighlighted ? LIVING_EARTH.lantern : LIVING_EARTH.sand,
          fontSize: 11,
          fontWeight: isHighlighted ? 600 : 400,
        },
        labelBgStyle: {
          fill: LIVING_EARTH.soil,
          fillOpacity: 0.95,
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

  // Empty state - Living Earth inspired visualization
  if (inputNodes.length === 0) {
    return (
      <div
        className={`flex items-center justify-center rounded-lg ${className}`}
        style={{
          height,
          backgroundColor: BACKGROUNDS.canvas,
        }}
      >
        <motion.div
          className="text-center"
          initial={{ opacity: 0, y: 10, scale: GROWING.initialScale }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          transition={{ duration: GROWING.duration, ease: GROWING.ease }}
        >
          {/* Constellation-like visualization with breathing */}
          <div className="relative w-32 h-32 mx-auto mb-6">
            {[0, 1, 2, 3, 4].map((i) => (
              <motion.div
                key={i}
                className="absolute w-3 h-3 rounded-full"
                style={{
                  left: `${50 + 40 * Math.cos((i * 2 * Math.PI) / 5)}%`,
                  top: `${50 + 40 * Math.sin((i * 2 * Math.PI) / 5)}%`,
                  backgroundColor: LIVING_EARTH.clay,
                }}
                animate={{
                  scale: [1, 1.3, 1],
                  opacity: [0.4, 0.8, 0.4],
                }}
                transition={{
                  duration: 3,
                  delay: i * 0.4,
                  repeat: Infinity,
                  ease: 'easeInOut',
                }}
              />
            ))}
            {/* Center node with lantern glow */}
            <motion.div
              className="absolute w-4 h-4 rounded-full left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2"
              style={{
                backgroundColor: `${LIVING_EARTH.lantern}60`,
                boxShadow: glowShadow(LIVING_EARTH.lantern, 'medium'),
              }}
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
            />
          </div>
          <div className="text-lg font-medium" style={{ color: LIVING_EARTH.lantern }}>
            No trail loaded
          </div>
          <div className="text-sm mt-2" style={{ color: LIVING_EARTH.clay }}>
            Select a trail to visualize its knowledge topology
          </div>
        </motion.div>
      </div>
    );
  }

  return (
    <div
      className={`rounded-lg overflow-hidden relative ${className}`}
      style={{
        height,
        backgroundColor: BACKGROUNDS.canvas,
      }}
    >
      {/* Layout controls - Living Earth styling with spring animations */}
      <div className="absolute top-3 right-3 z-10 flex items-center gap-2">
        {isSimulating && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9, x: 20 }}
            animate={{ opacity: 1, scale: 1, x: 0 }}
            exit={{ opacity: 0, scale: 0.9, x: 10 }}
            transition={{
              type: 'spring',
              stiffness: 400,
              damping: 25,
            }}
            className="px-3 py-1.5 backdrop-blur-sm rounded-full text-xs flex items-center gap-2"
            style={{
              backgroundColor: `${LIVING_EARTH.fern}90`,
              color: LIVING_EARTH.sprout,
            }}
          >
            <motion.span
              animate={{ rotate: 360 }}
              transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
            >
              🌱
            </motion.span>
            Growing layout...
          </motion.div>
        )}
        <motion.button
          onClick={runSimulation}
          disabled={isSimulating}
          whileHover={{
            scale: 1.08,
            transition: { type: 'spring', stiffness: 400, damping: 15 },
          }}
          whileTap={{
            scale: 0.92,
            rotate: [0, -5, 5, -3, 3, 0],
            transition: { duration: 0.4 },
          }}
          className="px-3 py-1.5 rounded-full text-xs transition-colors flex items-center gap-1.5 disabled:cursor-not-allowed disabled:opacity-50"
          style={{
            backgroundColor: BACKGROUNDS.surface,
            color: LIVING_EARTH.sand,
            borderWidth: 1,
            borderColor: LIVING_EARTH.wood,
          }}
          title="Re-run force simulation to redistribute nodes"
        >
          <motion.span
            animate={isSimulating ? { rotate: 360 } : { rotate: 0 }}
            transition={
              isSimulating
                ? { duration: 0.6, repeat: Infinity, ease: 'linear' }
                : { type: 'spring', stiffness: 300 }
            }
          >
            🌿
          </motion.span>
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
        onMoveEnd={onMoveEnd}
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
        {/* Living Earth: Warm grid background */}
        <Background color={LIVING_EARTH.bark} gap={16} />
        <Controls
          style={{
            backgroundColor: BACKGROUNDS.surface,
            borderColor: LIVING_EARTH.wood,
            borderWidth: 1,
          }}
          showInteractive={false}
        />
        <MiniMap
          style={{
            backgroundColor: BACKGROUNDS.surface,
            borderColor: LIVING_EARTH.wood,
            borderWidth: 1,
          }}
          nodeColor={(node) => {
            const data = node.data as ContextNodeData | undefined;
            // Current/selected gets lantern glow
            if (data?.is_current) return EVIDENCE_COLORS.current;
            // Root node (step 0) gets sage
            if (data?.step_index === 0) return EVIDENCE_COLORS.root;
            // Edge type determines color for visited nodes (Living Earth)
            if (data?.edge_type) return getEdgeColor(data.edge_type);
            return EVIDENCE_COLORS.default;
          }}
          maskColor={`${LIVING_EARTH.soil}80`}
          nodeStrokeWidth={2}
        />
      </ReactFlow>
    </div>
  );
}

export default TrailGraph;
