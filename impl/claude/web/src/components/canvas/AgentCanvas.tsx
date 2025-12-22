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

import React, { useState, useCallback, useMemo, useRef, useEffect } from 'react';
import type { AgentCursor } from '@/hooks/usePresenceChannel';
import { useCanvasLayout } from '@/hooks/useCanvasLayout';
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
  /** Available aspects for this node (from backend metadata) */
  aspects?: string[];
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
  /** Circadian tempo modifier for cursor animation (0.0-1.0) */
  circadianTempo?: number;
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
  position: { x: number; y: number };
  isSelected: boolean;
  hasCursor: boolean;
  isDragging: boolean;
  onClick: () => void;
  onDoubleClick: () => void;
  onToggle?: () => void;
  onDragStart: (e: React.MouseEvent) => void;
}

function NodeCard({
  node,
  position,
  isSelected,
  hasCursor,
  isDragging,
  onClick,
  onDoubleClick,
  onToggle,
  onDragStart,
}: NodeCardProps) {
  const bgColor = CONTEXT_BG_COLORS[node.context];
  const borderColor = CONTEXT_BORDER_COLORS[node.context];
  const accentColor = CONTEXT_COLORS[node.context];

  return (
    <div
      className={`
        absolute select-none
        rounded-lg border-2 px-3 py-2 min-w-[120px] max-w-[200px]
        ${isDragging ? 'cursor-grabbing z-50 shadow-xl shadow-black/40' : 'cursor-grab'}
        ${bgColor} ${borderColor}
        ${isSelected ? 'ring-2 ring-white/50 scale-105' : ''}
        ${hasCursor ? 'animate-pulse' : ''}
        ${!isDragging ? 'transition-all duration-200 hover:scale-105 hover:shadow-lg hover:shadow-black/20' : ''}
      `}
      style={{
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -50%)',
      }}
      onMouseDown={(e) => {
        // Only start drag on left click without modifier keys
        if (e.button === 0 && !e.ctrlKey && !e.metaKey && !e.shiftKey) {
          e.stopPropagation();
          onDragStart(e);
        }
      }}
      onClick={(e) => {
        e.stopPropagation();
        // Only trigger click if not dragging
        if (!isDragging) {
          onClick();
        }
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

      {/* Drag handle indicator */}
      <div className="absolute -right-1 -top-1 w-3 h-3 rounded-full bg-gray-700 border border-gray-500 opacity-0 group-hover:opacity-100 transition-opacity" />

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
// Connection Lines: Organic Vine Algorithm (Performance-Hardened)
// =============================================================================
//
// Design Philosophy (from mood-board.md + crown-jewels-genesis-moodboard.md):
// - "Data flows like water through vines" — organic curves with natural droop
// - "Everything Breathes" — subtle animation on 3-4s cycle
// - Living Earth palette — warm amber, sage, not cold gray
// - Hand-drawn feel — slight imperfection, vine-like growth
//
// Algorithm: Organic Cubic Bezier with Gravitational Droop
// Instead of simple quadratic, we use cubic bezier with:
// 1. Control points that "droop" like hanging vines
// 2. Asymmetric curves (exit horizontal, arc downward, enter from above)
// 3. Context-aware coloring from parent → child gradient
//
// PERFORMANCE OPTIMIZATIONS (hardened 2025-12-20):
// - Shared gradient defs per context-pair (not per-connection)
// - Removed expensive Gaussian blur filter (use CSS opacity instead)
// - Memoized path calculations with position hashing
// - React.memo on ConnectionLines component
// - Reduced SVG elements per connection (2 → 1 path)
// =============================================================================

interface ConnectionLinesProps {
  nodes: CanvasNode[];
  positions: Map<string, { x: number; y: number }>;
}

// =============================================================================
// Performance: Hoisted Constants (no allocation per render)
// =============================================================================

/** Living Earth vine colors (more muted than node colors) */
const CONTEXT_VINE_COLORS: Readonly<Record<string, string>> = {
  world: '#6B8B6B', // Sage-mint for world connections
  self: '#9B7BB6', // Soft violet
  concept: '#7BA88B', // Soft emerald
  void: '#8B8B8B', // Neutral gray
  time: '#C4A060', // Warm amber
} as const;

/** All unique context pairs for shared gradients */
const CONTEXT_TYPES = ['world', 'self', 'concept', 'void', 'time'] as const;

/** Pre-computed gradient ID for context pair (avoids string concat per connection) */
function getGradientId(fromContext: string, toContext: string): string {
  return `vine-${fromContext}-${toContext}`;
}

// =============================================================================
// Path Calculation (Pure function, easily memoizable)
// =============================================================================

/**
 * Calculate organic vine path between two points.
 *
 * The algorithm creates a natural "droop" like a hanging vine:
 * - Leaves parent node horizontally
 * - Arcs downward with gravity
 * - Curves up to meet child node from below
 *
 * For upward connections (child above parent), inverts to create
 * a "reaching" effect instead.
 *
 * PERFORMANCE: Pure function with no allocations beyond return string.
 */
function calculateVinePath(fromX: number, fromY: number, toX: number, toY: number): string {
  const dx = toX - fromX;
  const dy = toY - fromY;
  const dist = Math.sqrt(dx * dx + dy * dy);

  // Droop factor: how much the vine hangs down
  // Longer distances = more droop, capped for aesthetics
  const droopFactor = Math.min(0.3, dist / 800);
  const droop = dist * droopFactor;

  // Determine if we're going up or down
  const goingDown = dy > 0;

  // Control points for cubic bezier
  // The magic: asymmetric control points create organic feel
  if (goingDown) {
    // Standard vine: droop down then curve up to target
    const cp1x = fromX + dx * 0.3;
    const cp1y = fromY + droop * 0.5; // Slight initial droop
    const cp2x = fromX + dx * 0.7;
    const cp2y = toY - droop * 0.3; // Rise up to meet target

    return `M ${fromX} ${fromY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${toX} ${toY}`;
  }
  // Reaching upward: arc out then up
  const absDy = Math.abs(dy);
  const cp1x = fromX + dx * 0.4;
  const cp1y = fromY + absDy * 0.2; // Small downward arc first
  const cp2x = fromX + dx * 0.6;
  const cp2y = toY + absDy * 0.1; // Slight undershoot

  return `M ${fromX} ${fromY} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${toX} ${toY}`;
}

// =============================================================================
// Shared Gradient Definitions (rendered once, used by all connections)
// =============================================================================

/** Pre-render all possible context-pair gradients (5x5 = 25 max, but only ~10 used) */
function SharedGradientDefs() {
  return (
    <>
      {CONTEXT_TYPES.map((fromCtx) =>
        CONTEXT_TYPES.map((toCtx) => {
          const fromColor = CONTEXT_VINE_COLORS[fromCtx];
          const toColor = CONTEXT_VINE_COLORS[toCtx];
          const gradientId = getGradientId(fromCtx, toCtx);

          return (
            <linearGradient key={gradientId} id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
              <stop offset="0%" stopColor={fromColor} stopOpacity={0.7} />
              <stop offset="100%" stopColor={toColor} stopOpacity={0.7} />
            </linearGradient>
          );
        })
      )}
    </>
  );
}

// =============================================================================
// Connection Lines Component (Memoized)
// =============================================================================

interface ConnectionData {
  id: string;
  fromX: number;
  fromY: number;
  toX: number;
  toY: number;
  gradientId: string;
}

const ConnectionLinesInner = React.memo(function ConnectionLinesInner({
  connections,
}: {
  connections: ConnectionData[];
}) {
  if (connections.length === 0) return null;

  return (
    <svg
      className="absolute inset-0 pointer-events-none overflow-visible"
      style={{ left: 0, top: 0 }}
    >
      <defs>
        <SharedGradientDefs />
      </defs>

      {connections.map(({ id, fromX, fromY, toX, toY, gradientId }) => {
        const path = calculateVinePath(fromX, fromY, toX, toY);

        return (
          <path
            key={id}
            d={path}
            stroke={`url(#${gradientId})`}
            strokeWidth="1.5"
            fill="none"
            strokeLinecap="round"
            className="animate-vine-breathe"
          />
        );
      })}
    </svg>
  );
});

function ConnectionLines({ nodes, positions }: ConnectionLinesProps) {
  // Build node lookup map (stable reference if nodes unchanged)
  const nodeMap = useMemo(() => {
    const map = new Map<string, CanvasNode>();
    for (const n of nodes) {
      map.set(n.id, n);
    }
    return map;
  }, [nodes]);

  // Generate flat connection data (optimized for React reconciliation)
  // PERFORMANCE: Avoid object allocation by using flat structure
  const connections = useMemo((): ConnectionData[] => {
    const result: ConnectionData[] = [];

    for (const node of nodes) {
      if (!node.parent) continue;

      const parent = nodeMap.get(node.parent);
      if (!parent) continue;

      const fromPos = positions.get(parent.id);
      const toPos = positions.get(node.id);
      if (!fromPos || !toPos) continue;

      result.push({
        id: `${parent.id}-${node.id}`,
        fromX: fromPos.x,
        fromY: fromPos.y,
        toX: toPos.x,
        toY: toPos.y,
        gradientId: getGradientId(parent.context, node.context),
      });
    }

    return result;
  }, [nodes, nodeMap, positions]);

  return <ConnectionLinesInner connections={connections} />;
}

// Make ConnectionLines available with memo
const MemoizedConnectionLines = React.memo(ConnectionLines);

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
  circadianTempo = 1.0,
}: AgentCanvasProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [viewport, setViewport] = useState<ViewportState>({
    offsetX: 0,
    offsetY: 0,
    zoom: 1.0,
  });
  const [isPanning, setIsPanning] = useState(false);
  const [lastPanPos, setLastPanPos] = useState({ x: 0, y: 0 });

  // Force-directed layout with draggable nodes
  const { positions, startDrag, updateDrag, endDrag, isDragging, draggedNodeId, resetPositions } =
    useCanvasLayout(nodes, {
      centerX: 0,
      centerY: 0,
      radius: 250,
      nodeSpacing: 140,
    });

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

  // Pan handling (only when not dragging a node)
  const handleMouseDown = useCallback(
    (e: React.MouseEvent) => {
      if (!enablePan || isDragging) return;
      if (e.button !== 0) return; // Only left click
      setIsPanning(true);
      setLastPanPos({ x: e.clientX, y: e.clientY });
    },
    [enablePan, isDragging]
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      // Handle node dragging
      if (isDragging) {
        updateDrag(e.clientX / viewport.zoom, e.clientY / viewport.zoom);
        return;
      }

      // Handle canvas panning
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
    [isPanning, lastPanPos, isDragging, updateDrag, viewport.zoom]
  );

  const handleMouseUp = useCallback(() => {
    if (isDragging) {
      endDrag();
    }
    setIsPanning(false);
  }, [isDragging, endDrag]);

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
          View
        </button>
        <button
          onClick={resetPositions}
          className="px-2 h-8 rounded bg-gray-800 hover:bg-gray-700 text-white text-xs"
          title="Reset node positions"
        >
          Layout
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
        {/* Connection lines (memoized for performance) */}
        {showConnections && <MemoizedConnectionLines nodes={nodes} positions={positions} />}

        {/* Nodes */}
        {nodes.map((node) => {
          const pos = positions.get(node.id) || node.position;
          return (
            <NodeCard
              key={node.id}
              node={node}
              position={pos}
              isSelected={node.id === selectedNode}
              hasCursor={cursorsByPath.has(node.path)}
              isDragging={draggedNodeId === node.id}
              onClick={() => onNodeClick?.(node)}
              onDoubleClick={() => onNodeNavigate?.(node.path)}
              onToggle={() => onNodeToggle?.(node)}
              onDragStart={(e) =>
                startDrag(node.id, e.clientX / viewport.zoom, e.clientY / viewport.zoom)
              }
            />
          );
        })}

        {/* Agent Cursors with spring-physics animation */}
        <CursorOverlay
          cursors={cursors}
          nodes={nodes}
          positions={positions}
          circadianTempo={circadianTempo}
        />
      </div>

      {/* Empty state */}
      {nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center text-gray-500">
          <div className="text-center">
            <div className="text-2xl mb-2">...</div>
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
