/**
 * Telescope Component
 *
 * "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 *
 * A universal viewer with focal distance, aperture, and filter controls.
 * Replaces GaloisTelescope + TelescopeNavigator (~2,000 LOC) with ~400 LOC total.
 */

import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type {
  TelescopeProps,
  TelescopeState,
  NodeProjection,
  Point,
  GradientArrow,
} from './types';
import {
  focalDistanceToLayers,
  calculateNodePosition,
  buildGradientArrows,
  getLossColor,
} from './utils';
import { useTelescopeNavigation } from './useTelescopeNavigation';
import './Telescope.css';

// =============================================================================
// Constants
// =============================================================================

const DEFAULT_STATE: TelescopeState = {
  focalDistance: 0.5,
  focalPoint: null,
  visibleLayers: [4, 5, 6, 7],
  lossThreshold: 1.0,
};

// =============================================================================
// Component
// =============================================================================

export const Telescope = memo(function Telescope({
  nodes,
  gradients,
  onNodeClick,
  onNavigate,
  initialState,
  keyboardEnabled = true,
  width = 800,
  height = 600,
}: TelescopeProps) {
  // State
  const [state, setState] = useState<TelescopeState>(() => ({
    ...DEFAULT_STATE,
    ...initialState,
  }));

  const canvasRef = useRef<SVGSVGElement>(null);

  // Derived state: visible layers from focal distance
  const visibleLayers = useMemo(
    () => focalDistanceToLayers(state.focalDistance),
    [state.focalDistance]
  );

  // Filter nodes by visible layers and loss threshold
  const visibleNodes = useMemo(
    () =>
      nodes.filter(
        (node) =>
          visibleLayers.includes(node.layer) &&
          (node.loss ?? 0) <= state.lossThreshold
      ),
    [nodes, visibleLayers, state.lossThreshold]
  );

  // Calculate node positions
  const nodePositions = useMemo(() => {
    const positions = new Map<string, Point>();
    for (const node of visibleNodes) {
      const pos = calculateNodePosition(
        node,
        visibleNodes,
        state.focalDistance,
        width,
        height
      );
      positions.set(node.node_id, pos);
    }
    return positions;
  }, [visibleNodes, state.focalDistance, width, height]);

  // Build gradient arrows
  const gradientArrows = useMemo(
    () => buildGradientArrows(gradients, nodePositions),
    [gradients, nodePositions]
  );

  // Navigation
  const { goLowestLoss, goHighestLoss, followGradientFrom } =
    useTelescopeNavigation({
      nodes: visibleNodes,
      gradients,
      onNavigate,
    });

  // Node click handler
  const handleNodeClick = useCallback(
    (nodeId: string) => {
      setState((prev) => ({ ...prev, focalPoint: nodeId }));
      onNodeClick?.(nodeId);
      onNavigate?.(nodeId, 'focus');
    },
    [onNodeClick, onNavigate]
  );

  // Zoom controls
  const zoomIn = useCallback(() => {
    setState((prev) => ({
      ...prev,
      focalDistance: Math.min(1.0, prev.focalDistance + 0.1),
    }));
  }, []);

  const zoomOut = useCallback(() => {
    setState((prev) => ({
      ...prev,
      focalDistance: Math.max(0.0, prev.focalDistance - 0.1),
    }));
  }, []);

  // Keyboard navigation
  useEffect(() => {
    if (!keyboardEnabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Ignore if typing in input
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key) {
        case 'l': // go lowest loss
          goLowestLoss();
          break;
        case 'h': // go highest loss
          goHighestLoss();
          break;
        case 'G': // follow gradient (Shift+G)
          if (e.shiftKey && state.focalPoint) {
            followGradientFrom(state.focalPoint);
          }
          break;
        case '+':
        case '=':
          zoomIn();
          break;
        case '-':
        case '_':
          zoomOut();
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [
    keyboardEnabled,
    state.focalPoint,
    goLowestLoss,
    goHighestLoss,
    followGradientFrom,
    zoomIn,
    zoomOut,
  ]);

  return (
    <div className="telescope">
      <svg
        ref={canvasRef}
        className="telescope__canvas"
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
      >
        {/* Gradient arrows (render first, below nodes) */}
        <g className="telescope__gradients">
          {gradientArrows.map((arrow, i) => (
            <GradientArrowSVG key={i} arrow={arrow} />
          ))}
        </g>

        {/* Nodes */}
        <g className="telescope__nodes">
          {visibleNodes.map((node) => {
            const pos = nodePositions.get(node.node_id);
            if (!pos) return null;

            return (
              <NodeSVG
                key={node.node_id}
                node={node}
                position={pos}
                isFocal={node.node_id === state.focalPoint}
                onClick={() => handleNodeClick(node.node_id)}
              />
            );
          })}
        </g>
      </svg>

      {/* Legend */}
      <div className="telescope__legend">
        <div className="telescope__legend-item">
          <kbd>l</kbd> Lowest loss
        </div>
        <div className="telescope__legend-item">
          <kbd>h</kbd> Highest loss
        </div>
        <div className="telescope__legend-item">
          <kbd>Shift+G</kbd> Follow gradient
        </div>
        <div className="telescope__legend-item">
          <kbd>+/-</kbd> Zoom
        </div>
      </div>
    </div>
  );
});

// =============================================================================
// Node SVG
// =============================================================================

interface NodeSVGProps {
  node: NodeProjection;
  position: Point;
  isFocal: boolean;
  onClick: () => void;
}

const NodeSVG = memo(function NodeSVG({
  node,
  position,
  isFocal,
  onClick,
}: NodeSVGProps) {
  const radius = 6 * node.scale;
  const color = node.loss !== undefined ? getLossColor(node.loss) : node.color;

  return (
    <g
      className="telescope__node"
      transform={`translate(${position.x}, ${position.y})`}
      onClick={onClick}
      style={{ cursor: 'pointer' }}
    >
      {/* Node circle */}
      <circle
        r={radius}
        fill={color}
        opacity={node.opacity}
        stroke={isFocal ? '#FFD700' : 'none'}
        strokeWidth={isFocal ? 2 : 0}
      />

      {/* Focal ring (animated) */}
      {isFocal && (
        <circle
          r={radius + 4}
          fill="none"
          stroke="#FFD700"
          strokeWidth={1.5}
          opacity={0.6}
          className="telescope__focal-ring"
        />
      )}
    </g>
  );
});

// =============================================================================
// Gradient Arrow SVG
// =============================================================================

interface GradientArrowSVGProps {
  arrow: GradientArrow;
}

const GradientArrowSVG = memo(function GradientArrowSVG({
  arrow,
}: GradientArrowSVGProps) {
  // Calculate arrow head
  const dx = arrow.end.x - arrow.start.x;
  const dy = arrow.end.y - arrow.start.y;
  const angle = Math.atan2(dy, dx);
  const headLength = 8;

  const headX1 = arrow.end.x - headLength * Math.cos(angle - Math.PI / 6);
  const headY1 = arrow.end.y - headLength * Math.sin(angle - Math.PI / 6);
  const headX2 = arrow.end.x - headLength * Math.cos(angle + Math.PI / 6);
  const headY2 = arrow.end.y - headLength * Math.sin(angle + Math.PI / 6);

  return (
    <g className="telescope__gradient-arrow" opacity={0.6}>
      {/* Arrow line */}
      <line
        x1={arrow.start.x}
        y1={arrow.start.y}
        x2={arrow.end.x}
        y2={arrow.end.y}
        stroke={arrow.color}
        strokeWidth={arrow.width}
        strokeLinecap="round"
      />

      {/* Arrow head */}
      <path
        d={`M ${arrow.end.x} ${arrow.end.y} L ${headX1} ${headY1} L ${headX2} ${headY2} Z`}
        fill={arrow.color}
      />
    </g>
  );
});
