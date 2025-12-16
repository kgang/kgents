/**
 * PipelineCanvas: SVG-based canvas for pipeline editing.
 *
 * Renders nodes and edges in an interactive canvas. Supports
 * panning, zooming, and drag-drop for adding new nodes.
 *
 * @see plans/web-refactor/interaction-patterns.md
 */

import { useRef, useState, useCallback, type MouseEvent, type WheelEvent } from 'react';
import { useDroppable } from '@dnd-kit/core';

import { cn } from '@/lib/utils';
import type { Pipeline, Port, DragData } from '@/components/dnd';
import { PipelineNode } from './PipelineNode';
import { PipelineEdge, DraftEdge, EdgeMarkers } from './PipelineEdge';

// =============================================================================
// Types
// =============================================================================

export type CanvasMode = 'view' | 'edit' | 'connect';

export interface PipelineCanvasProps {
  /** Pipeline to render */
  pipeline: Pipeline;

  /** Canvas mode */
  mode?: CanvasMode;

  /** Currently selected node IDs */
  selectedNodes?: Set<string>;

  /** Currently selected edge IDs */
  selectedEdges?: Set<string>;

  /** Called when a node is clicked */
  onNodeClick?: (nodeId: string, shiftKey: boolean) => void;

  /** Called when an edge is clicked */
  onEdgeClick?: (edgeId: string, shiftKey: boolean) => void;

  /** Called when canvas background is clicked */
  onCanvasClick?: () => void;

  /** Called when a node is moved */
  onNodeMove?: (nodeId: string, position: { x: number; y: number }) => void;

  /** Called when an edge should be created */
  onEdgeCreate?: (source: { nodeId: string; portId: string }, target: { nodeId: string; portId: string }) => void;

  /** Called when a node should be removed */
  onNodeRemove?: (nodeId: string) => void;

  /** Called when an item is dropped on the canvas */
  onDrop?: (data: DragData, position: { x: number; y: number }) => void;

  /** Additional class names */
  className?: string;
}

interface ViewState {
  panX: number;
  panY: number;
  zoom: number;
}

interface ConnectionDraft {
  sourceNodeId: string;
  sourcePortId: string;
  startPos: { x: number; y: number };
  currentPos: { x: number; y: number };
}

// =============================================================================
// Component
// =============================================================================

export function PipelineCanvas({
  pipeline,
  mode = 'edit',
  selectedNodes = new Set(),
  selectedEdges = new Set(),
  onNodeClick,
  onEdgeClick,
  onCanvasClick,
  onNodeMove: _onNodeMove,
  onEdgeCreate,
  onNodeRemove: _onNodeRemove,
  onDrop: _onDrop,
  className,
}: PipelineCanvasProps) {
  // Note: These callbacks are defined but will be wired up in future implementation
  void _onNodeMove;
  void _onNodeRemove;
  void _onDrop;
  const containerRef = useRef<HTMLDivElement | null>(null);
  const svgRef = useRef<SVGSVGElement>(null);

  // View state (pan + zoom)
  const [view, setView] = useState<ViewState>({
    panX: 0,
    panY: 0,
    zoom: 1,
  });

  // Connection in progress
  const [connectionDraft, setConnectionDraft] = useState<ConnectionDraft | null>(null);

  // Panning state
  const [isPanning, setIsPanning] = useState(false);
  const panStartRef = useRef({ x: 0, y: 0, panX: 0, panY: 0 });

  // Set up drop zone
  const { setNodeRef: setDropRef, isOver } = useDroppable({
    id: 'pipeline-canvas',
    data: { accepts: ['agent', 'archetype'] },
  });

  // ==========================================================================
  // Event Handlers
  // ==========================================================================

  const handleMouseDown = useCallback((e: MouseEvent<HTMLDivElement>) => {
    // Middle mouse button or space+click for panning
    if (e.button === 1 || (e.button === 0 && e.altKey)) {
      setIsPanning(true);
      panStartRef.current = {
        x: e.clientX,
        y: e.clientY,
        panX: view.panX,
        panY: view.panY,
      };
      e.preventDefault();
    }
  }, [view.panX, view.panY]);

  const handleMouseMove = useCallback((e: MouseEvent<HTMLDivElement>) => {
    if (isPanning) {
      const dx = e.clientX - panStartRef.current.x;
      const dy = e.clientY - panStartRef.current.y;
      setView((v) => ({
        ...v,
        panX: panStartRef.current.panX + dx,
        panY: panStartRef.current.panY + dy,
      }));
    }

    // Update connection draft position
    if (connectionDraft) {
      const rect = containerRef.current?.getBoundingClientRect();
      if (rect) {
        setConnectionDraft((d) =>
          d
            ? {
                ...d,
                currentPos: {
                  x: (e.clientX - rect.left - view.panX) / view.zoom,
                  y: (e.clientY - rect.top - view.panY) / view.zoom,
                },
              }
            : null
        );
      }
    }
  }, [isPanning, connectionDraft, view.panX, view.panY, view.zoom]);

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);

    // Finish connection if draft exists
    if (connectionDraft) {
      // TODO: Check if over a valid port and create edge
      setConnectionDraft(null);
    }
  }, [connectionDraft]);

  const handleWheel = useCallback((e: WheelEvent<HTMLDivElement>) => {
    if (e.ctrlKey || e.metaKey) {
      // Zoom
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      setView((v) => ({
        ...v,
        zoom: Math.min(2, Math.max(0.25, v.zoom * delta)),
      }));
    }
  }, []);

  const handleCanvasClick = useCallback((e: MouseEvent<HTMLDivElement>) => {
    if (e.target === containerRef.current || e.target === svgRef.current) {
      onCanvasClick?.();
    }
  }, [onCanvasClick]);

  const handleNodeClick = useCallback((nodeId: string) => (e: MouseEvent) => {
    e.stopPropagation();
    onNodeClick?.(nodeId, e.shiftKey);
  }, [onNodeClick]);

  const handleEdgeClick = useCallback((edgeId: string) => (e: MouseEvent<SVGPathElement>) => {
    e.stopPropagation();
    onEdgeClick?.(edgeId, e.shiftKey);
  }, [onEdgeClick]);

  const handlePortClick = useCallback((nodeId: string, port: Port, isInput: boolean) => {
    if (mode !== 'edit') return;

    if (!connectionDraft && !isInput) {
      // Start a new connection from an output port
      const node = pipeline.nodes.find((n) => n.id === nodeId);
      if (node) {
        setConnectionDraft({
          sourceNodeId: nodeId,
          sourcePortId: port.id,
          startPos: {
            x: node.position.x + 150, // Right edge of node
            y: node.position.y + 40,
          },
          currentPos: {
            x: node.position.x + 150,
            y: node.position.y + 40,
          },
        });
      }
    } else if (connectionDraft && isInput) {
      // Complete connection to an input port
      onEdgeCreate?.(
        { nodeId: connectionDraft.sourceNodeId, portId: connectionDraft.sourcePortId },
        { nodeId, portId: port.id }
      );
      setConnectionDraft(null);
    }
  }, [connectionDraft, mode, pipeline.nodes, onEdgeCreate]);

  // ==========================================================================
  // Render
  // ==========================================================================

  const transform = `translate(${view.panX}px, ${view.panY}px) scale(${view.zoom})`;

  return (
    <div
      ref={(el) => {
        containerRef.current = el;
        setDropRef(el);
      }}
      className={cn(
        'pipeline-canvas relative overflow-hidden bg-town-bg',
        'border border-town-accent/20 rounded-lg',
        isPanning && 'cursor-grabbing',
        !isPanning && 'cursor-grab',
        isOver && 'ring-2 ring-town-highlight/50',
        className
      )}
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
      onClick={handleCanvasClick}
    >
      {/* Grid background */}
      <div
        className="absolute inset-0 pointer-events-none opacity-20"
        style={{
          backgroundImage: `
            linear-gradient(var(--color-town-accent) 1px, transparent 1px),
            linear-gradient(90deg, var(--color-town-accent) 1px, transparent 1px)
          `,
          backgroundSize: `${20 * view.zoom}px ${20 * view.zoom}px`,
          backgroundPosition: `${view.panX}px ${view.panY}px`,
        }}
      />

      {/* Canvas content */}
      <div
        className="absolute"
        style={{ transform, transformOrigin: '0 0' }}
      >
        {/* Edges (SVG layer) */}
        <svg
          ref={svgRef}
          className="absolute overflow-visible pointer-events-none"
          style={{ width: '100%', height: '100%' }}
        >
          <EdgeMarkers />

          {/* Existing edges */}
          <g className="pointer-events-auto">
            {pipeline.edges.map((edge) => (
              <PipelineEdge
                key={edge.id}
                edge={edge}
                nodes={pipeline.nodes}
                isSelected={selectedEdges.has(edge.id)}
                onClick={handleEdgeClick(edge.id)}
              />
            ))}
          </g>

          {/* Draft edge (connection in progress) */}
          {connectionDraft && (
            <DraftEdge
              start={connectionDraft.startPos}
              end={connectionDraft.currentPos}
            />
          )}
        </svg>

        {/* Nodes */}
        {pipeline.nodes.map((node) => (
          <PipelineNode
            key={node.id}
            node={node}
            isSelected={selectedNodes.has(node.id)}
            onClick={handleNodeClick(node.id)}
            onPortClick={(port, isInput) => handlePortClick(node.id, port, isInput)}
          />
        ))}
      </div>

      {/* Controls overlay */}
      <div className="absolute bottom-4 right-4 flex gap-2">
        <button
          onClick={() => setView({ panX: 0, panY: 0, zoom: 1 })}
          className="px-3 py-1.5 bg-town-surface/80 rounded text-sm hover:bg-town-surface"
          title="Reset view"
        >
          ⟲ Reset
        </button>
        <div className="flex bg-town-surface/80 rounded">
          <button
            onClick={() => setView((v) => ({ ...v, zoom: v.zoom * 0.9 }))}
            className="px-2 py-1.5 hover:bg-town-accent/20 rounded-l"
            title="Zoom out"
          >
            −
          </button>
          <span className="px-2 py-1.5 text-sm">
            {Math.round(view.zoom * 100)}%
          </span>
          <button
            onClick={() => setView((v) => ({ ...v, zoom: v.zoom * 1.1 }))}
            className="px-2 py-1.5 hover:bg-town-accent/20 rounded-r"
            title="Zoom in"
          >
            +
          </button>
        </div>
      </div>

      {/* Empty state */}
      {pipeline.nodes.length === 0 && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center text-gray-500">
            <div className="text-4xl mb-2">🔧</div>
            <p className="text-sm">Drag agents here to build a pipeline</p>
          </div>
        </div>
      )}
    </div>
  );
}

export default PipelineCanvas;
