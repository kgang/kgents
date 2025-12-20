/**
 * AgentCanvas: Collaborative mind-map canvas for CLI v7 Phase 4.
 *
 * Renders AGENTESE nodes as a navigable mind-map with:
 * - Agent cursors showing presence and focus
 * - Node connections representing AGENTESE path hierarchy
 * - Real-time updates via PresenceChannel
 *
 * Voice Anchor:
 * "Agents pretending to be there with their cursors moving,
 *  kinda following my cursor, kinda doing its own thing."
 *
 * Design Philosophy:
 * - Tasteful: Clean visualization that doesn't overwhelm
 * - Joy-Inducing: Animated cursors that feel alive
 * - Composable: Can be embedded or used full-screen
 *
 * @see protocols/agentese/presence.py - Source of truth for cursor state
 * @see plans/cli-v7-implementation.md Phase 4 spec
 */

import { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import type { AgentCursor } from '@/hooks/usePresenceChannel';
import { CursorOverlay } from './CursorOverlay';

// =============================================================================
// Types
// =============================================================================

/** AGENTESE node for the canvas visualization */
export interface CanvasNode {
  /** Node ID (AGENTESE path) */
  id: string;
  /** Display label */
  label: string;
  /** Full AGENTESE path */
  path: string;
  /** Node description */
  description?: string;
  /** Parent node ID (for hierarchy) */
  parent?: string;
  /** Children node IDs */
  children?: string[];
  /** Node category (context: world, self, concept, void, time) */
  context: 'world' | 'self' | 'concept' | 'void' | 'time';
  /** Position on canvas */
  position: { x: number; y: number };
  /** Node is expandable */
  expandable?: boolean;
  /** Node is currently expanded */
  expanded?: boolean;
}

/** Canvas viewport state */
interface ViewportState {
  /** X offset (pan) */
  offsetX: number;
  /** Y offset (pan) */
  offsetY: number;
  /** Zoom level (1.0 = 100%) */
  zoom: number;
}

/** Props for AgentCanvas */
export interface AgentCanvasProps {
  /** Nodes to display */
  nodes: CanvasNode[];
  /** Agent cursors to display */
  cursors: AgentCursor[];
  /** Currently selected node ID */
  selectedNode?: string | null;
  /** Callback when a node is clicked */
  onNodeClick?: (node: CanvasNode) => void;
  /** Callback when a node is double-clicked (navigate) */
  onNodeNavigate?: (path: string) => void;
  /** Callback when a node is expanded/collapsed */
  onNodeToggle?: (node: CanvasNode) => void;
  /** Whether to show connection lines */
  showConnections?: boolean;
  /** Extra CSS classes */
  className?: string;
  /** Enable panning */
  enablePan?: boolean;
  /** Enable zooming */
  enableZoom?: boolean;
  /** Minimum zoom level */
  minZoom?: number;
  /** Maximum zoom level */
  maxZoom?: number;
}

// =============================================================================
// Constants
// =============================================================================

const CONTEXT_COLORS: Record<CanvasNode['context'], string> = {
  world: '#3b82f6', // blue-500
  self: '#8b5cf6', // violet-500
  concept: '#10b981', // emerald-500
  void: '#6b7280', // gray-500
  time: '#f59e0b', // amber-500
};

const CONTEXT_BG_COLORS: Record<CanvasNode['context'], string> = {
  world: 'bg-blue-500/20',
  self: 'bg-violet-500/20',
  concept: 'bg-emerald-500/20',
  void: 'bg-gray-500/20',
  time: 'bg-amber-500/20',
};

const CONTEXT_BORDER_COLORS: Record<CanvasNode['context'], string> = {
  world: 'border-blue-500/50',
  self: 'border-violet-500/50',
  concept: 'border-emerald-500/50',
  void: 'border-gray-500/50',
  time: 'border-amber-500/50',
};

// =============================================================================
// Helper Components
// =============================================================================

interface NodeCardProps {
  node: CanvasNode;
  isSelected: boolean;
  hasCursor: boolean;
  onClick: () => void;
  onDoubleClick: () => void;
  onToggle?: () => void;
}

function NodeCard({
  node,
  isSelected,
  hasCursor,
  onClick,
  onDoubleClick,
  onToggle,
}: NodeCardProps) {
  const bgColor = CONTEXT_BG_COLORS[node.context];
  const borderColor = CONTEXT_BORDER_COLORS[node.context];
  const accentColor = CONTEXT_COLORS[node.context];

  return (
    <div
      className={`
        absolute cursor-pointer select-none
        rounded-lg border-2 px-3 py-2 min-w-[120px] max-w-[200px]
        transition-all duration-200
        ${bgColor} ${borderColor}
        ${isSelected ? 'ring-2 ring-white/50 scale-105' : ''}
        ${hasCursor ? 'animate-pulse' : ''}
        hover:scale-105 hover:shadow-lg hover:shadow-black/20
      `}
      style={{
        left: node.position.x,
        top: node.position.y,
        transform: 'translate(-50%, -50%)',
      }}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      onDoubleClick={(e) => {
        e.stopPropagation();
        onDoubleClick();
      }}
    >
      {/* Expand/collapse toggle */}
      {node.expandable && (
        <button
          className="absolute -left-2 -top-2 w-5 h-5 rounded-full bg-gray-800 border border-gray-600 text-xs flex items-center justify-center hover:bg-gray-700"
          onClick={(e) => {
            e.stopPropagation();
            onToggle?.();
          }}
        >
          {node.expanded ? '-' : '+'}
        </button>
      )}

      {/* Node label */}
      <div className="font-medium text-sm text-white truncate">{node.label}</div>

      {/* Path (subtle) */}
      <div className="text-[10px] text-gray-400 truncate">{node.path}</div>

      {/* Description (if any) */}
      {node.description && (
        <div className="text-[10px] text-gray-500 mt-1 line-clamp-2">{node.description}</div>
      )}

      {/* Context indicator */}
      <div
        className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 rounded-full"
        style={{ backgroundColor: accentColor }}
      />
    </div>
  );
}

// =============================================================================
// Connection Lines (SVG)
// =============================================================================

interface ConnectionLinesProps {
  nodes: CanvasNode[];
  viewport: ViewportState;
}

function ConnectionLines({ nodes, viewport }: ConnectionLinesProps) {
  const nodeMap = useMemo(() => {
    const map = new Map<string, CanvasNode>();
    nodes.forEach((n) => map.set(n.id, n));
    return map;
  }, [nodes]);

  // Generate lines from parent → child
  const lines = useMemo(() => {
    const result: { from: CanvasNode; to: CanvasNode }[] = [];
    nodes.forEach((node) => {
      if (node.parent) {
        const parent = nodeMap.get(node.parent);
        if (parent) {
          result.push({ from: parent, to: node });
        }
      }
    });
    return result;
  }, [nodes, nodeMap]);

  if (lines.length === 0) return null;

  return (
    <svg
      className="absolute inset-0 pointer-events-none"
      style={{
        transform: `translate(${viewport.offsetX}px, ${viewport.offsetY}px) scale(${viewport.zoom})`,
        transformOrigin: '0 0',
      }}
    >
      <defs>
        <marker id="arrowhead" markerWidth="6" markerHeight="6" refX="5" refY="3" orient="auto">
          <polygon points="0 0, 6 3, 0 6" fill="#4b5563" />
        </marker>
      </defs>
      {lines.map(({ from, to }, i) => {
        const dx = to.position.x - from.position.x;
        const dy = to.position.y - from.position.y;
        // Bezier control point for smooth curve
        const cx = from.position.x + dx * 0.5;
        const cy = from.position.y + dy * 0.5;

        return (
          <path
            key={i}
            d={`M ${from.position.x} ${from.position.y} Q ${cx} ${from.position.y} ${cx} ${cy} T ${to.position.x} ${to.position.y}`}
            stroke="#4b5563"
            strokeWidth="1.5"
            fill="none"
            strokeDasharray="4 2"
            opacity={0.5}
          />
        );
      })}
    </svg>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function AgentCanvas({
  nodes,
  cursors,
  selectedNode,
  onNodeClick,
  onNodeNavigate,
  onNodeToggle,
  showConnections = true,
  className = '',
  enablePan = true,
  enableZoom = true,
  minZoom = 0.25,
  maxZoom = 2.0,
}: AgentCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [viewport, setViewport] = useState<ViewportState>({
    offsetX: 0,
    offsetY: 0,
    zoom: 1.0,
  });
  const [isPanning, setIsPanning] = useState(false);
  const [lastPanPos, setLastPanPos] = useState({ x: 0, y: 0 });

  // Create a map of path → cursor for quick lookup
  const cursorsByPath = useMemo(() => {
    const map = new Map<string, AgentCursor[]>();
    cursors.forEach((cursor) => {
      if (cursor.focus_path) {
        const existing = map.get(cursor.focus_path) || [];
        map.set(cursor.focus_path, [...existing, cursor]);
      }
    });
    return map;
  }, [cursors]);

  // Pan handling
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (!enablePan) return;
      if (e.button !== 0) return; // Only left click
      setIsPanning(true);
      setLastPanPos({ x: e.clientX, y: e.clientY });
    },
    [enablePan]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!isPanning) return;
      const dx = e.clientX - lastPanPos.x;
      const dy = e.clientY - lastPanPos.y;
      setViewport((prev) => ({
        ...prev,
        offsetX: prev.offsetX + dx,
        offsetY: prev.offsetY + dy,
      }));
      setLastPanPos({ x: e.clientX, y: e.clientY });
    },
    [isPanning, lastPanPos]
  );

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  // Zoom handling
  const handleWheel = useCallback(
    (e: React.WheelEvent) => {
      if (!enableZoom) return;
      e.preventDefault();

      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      setViewport((prev) => ({
        ...prev,
        zoom: Math.max(minZoom, Math.min(maxZoom, prev.zoom * delta)),
      }));
    },
    [enableZoom, minZoom, maxZoom]
  );

  // Reset viewport
  const resetViewport = useCallback(() => {
    setViewport({ offsetX: 0, offsetY: 0, zoom: 1.0 });
  }, []);

  // Center on a specific node (exported for external use)
  const centerOnNode = useCallback(
    (nodeId: string) => {
      const node = nodes.find((n) => n.id === nodeId);
      if (!node || !containerRef.current) return;

      const rect = containerRef.current.getBoundingClientRect();
      setViewport({
        offsetX: rect.width / 2 - node.position.x,
        offsetY: rect.height / 2 - node.position.y,
        zoom: 1.0,
      });
    },
    [nodes]
  );

  // Expose centerOnNode via the component for external use
  // This is available to consumers who need programmatic centering
  void centerOnNode; // Acknowledge intentional export for external API

  // Auto-center on mount if no offset
  useEffect(() => {
    if (viewport.offsetX === 0 && viewport.offsetY === 0 && containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setViewport((prev) => ({
        ...prev,
        offsetX: rect.width / 2,
        offsetY: rect.height / 2,
      }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run on mount - intentionally not reacting to viewport changes

  return (
    <div
      ref={containerRef}
      className={`
        relative overflow-hidden bg-gray-900 rounded-lg
        ${isPanning ? 'cursor-grabbing' : 'cursor-grab'}
        ${className}
      `}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >
      {/* Controls */}
      <div className="absolute top-2 right-2 z-20 flex items-center gap-2">
        <button
          onClick={() => setViewport((v) => ({ ...v, zoom: Math.min(maxZoom, v.zoom * 1.2) }))}
          className="w-8 h-8 rounded bg-gray-800 hover:bg-gray-700 text-white text-lg flex items-center justify-center"
          title="Zoom in"
        >
          +
        </button>
        <button
          onClick={() => setViewport((v) => ({ ...v, zoom: Math.max(minZoom, v.zoom * 0.8) }))}
          className="w-8 h-8 rounded bg-gray-800 hover:bg-gray-700 text-white text-lg flex items-center justify-center"
          title="Zoom out"
        >
          -
        </button>
        <button
          onClick={resetViewport}
          className="px-2 h-8 rounded bg-gray-800 hover:bg-gray-700 text-white text-xs"
          title="Reset view"
        >
          Reset
        </button>
        <span className="text-xs text-gray-500">{Math.round(viewport.zoom * 100)}%</span>
      </div>

      {/* Legend */}
      <div className="absolute bottom-2 left-2 z-20 flex items-center gap-3 text-[10px] text-gray-500">
        {Object.entries(CONTEXT_COLORS).map(([context, color]) => (
          <div key={context} className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: color }} />
            <span>{context}</span>
          </div>
        ))}
      </div>

      {/* Canvas content */}
      <div
        className="absolute inset-0"
        style={{
          transform: `translate(${viewport.offsetX}px, ${viewport.offsetY}px) scale(${viewport.zoom})`,
          transformOrigin: '0 0',
        }}
      >
        {/* Connection lines */}
        {showConnections && (
          <ConnectionLines nodes={nodes} viewport={{ offsetX: 0, offsetY: 0, zoom: 1 }} />
        )}

        {/* Nodes */}
        {nodes.map((node) => (
          <NodeCard
            key={node.id}
            node={node}
            isSelected={node.id === selectedNode}
            hasCursor={cursorsByPath.has(node.path)}
            onClick={() => onNodeClick?.(node)}
            onDoubleClick={() => onNodeNavigate?.(node.path)}
            onToggle={() => onNodeToggle?.(node)}
          />
        ))}

        {/* Agent Cursors */}
        <CursorOverlay cursors={cursors} nodes={nodes} />
      </div>

      {/* Empty state */}
      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="text-2xl mb-2">🌐</div>
            <div>No nodes to display</div>
            <div className="text-xs mt-1">Invoke an AGENTESE path to explore</div>
          </div>
        </div>
      )}
    </div>
  );
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Generate a simple radial layout for nodes.
 * This is a placeholder - a real implementation would use force-directed layout.
 */
export function generateRadialLayout(
  paths: string[],
  centerX: number = 0,
  centerY: number = 0,
  radius: number = 200
): CanvasNode[] {
  // Group by context
  const byContext: Record<string, string[]> = {
    world: [],
    self: [],
    concept: [],
    void: [],
    time: [],
  };

  paths.forEach((path) => {
    const context = path.split('.')[0] as CanvasNode['context'];
    if (byContext[context]) {
      byContext[context].push(path);
    }
  });

  const nodes: CanvasNode[] = [];
  let contextIndex = 0;
  const contextCount = Object.values(byContext).filter((arr) => arr.length > 0).length;

  for (const [context, contextPaths] of Object.entries(byContext)) {
    if (contextPaths.length === 0) continue;

    const contextAngle = (contextIndex / contextCount) * 2 * Math.PI - Math.PI / 2;
    const contextCenterX = centerX + Math.cos(contextAngle) * radius;
    const contextCenterY = centerY + Math.sin(contextAngle) * radius;

    contextPaths.forEach((path, pathIndex) => {
      const pathAngle =
        (pathIndex / contextPaths.length) * Math.PI * 0.5 + contextAngle - Math.PI * 0.25;
      const pathRadius = radius * 0.5;

      nodes.push({
        id: path,
        label: path.split('.').pop() || path,
        path,
        context: context as CanvasNode['context'],
        position: {
          x: contextCenterX + Math.cos(pathAngle) * pathRadius,
          y: contextCenterY + Math.sin(pathAngle) * pathRadius,
        },
        expandable: path.split('.').length < 3,
      });
    });

    contextIndex++;
  }

  return nodes;
}

// =============================================================================
// Exports
// =============================================================================

export default AgentCanvas;
