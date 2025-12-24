/**
 * GaloisTelescope: Loss-guided navigation visualization
 *
 * "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 *
 * This component renders the Zero Seed graph as a loss topography where:
 * - High-loss nodes glow as warnings (semantic drift, incoherence)
 * - Low-loss nodes are cool and stable (well-grounded, compositional)
 * - Loss gradients guide navigation (flow toward coherence)
 * - Edge clustering reflects semantic proximity
 */

import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type {
  GaloisTelescopeState,
  NodeProjection,
  GradientArrow,
  NodeId,
  NavigationAction,
  Position2D,
} from './types';
import { LAYER_NAMES } from './types';
import { LossNode } from './LossNode';
import { GradientField } from './GradientField';
import { LossLegend } from './LossLegend';
import { useTelescopeNavigation } from './useTelescopeNavigation';
import './GaloisTelescope.css';

// -----------------------------------------------------------------------------
// Types
// -----------------------------------------------------------------------------

interface GaloisTelescopeProps {
  /** Initial telescope state */
  initialState?: Partial<GaloisTelescopeState>;

  /** Node projections to render */
  projections: NodeProjection[];

  /** Gradient arrows to render */
  gradientArrows?: GradientArrow[];

  /** Callback when node is clicked */
  onNodeClick?: (nodeId: NodeId) => void;

  /** Callback when navigation action occurs */
  onNavigate?: (action: NavigationAction, nodeId?: NodeId) => void;

  /** Callback when telescope state changes */
  onStateChange?: (state: GaloisTelescopeState) => void;

  /** High-loss warning nodes */
  highLossNodes?: Array<{ node_id: NodeId; loss: number; reason: string }>;

  /** Whether to enable keyboard navigation */
  keyboardEnabled?: boolean;

  /** Container width/height */
  width?: number;
  height?: number;
}

// -----------------------------------------------------------------------------
// Default State
// -----------------------------------------------------------------------------

const DEFAULT_STATE: GaloisTelescopeState = {
  focal_distance: 0.5,
  focal_point: null,
  show_loss: true,
  show_gradient: true,
  loss_threshold: 0.5,
  loss_colormap: 'viridis',
  visible_layers: [1, 2, 3, 4, 5, 6, 7],
  node_scale: 0.65,
  preferred_layer: 4,
};

// -----------------------------------------------------------------------------
// Component
// -----------------------------------------------------------------------------

export const GaloisTelescope = memo(function GaloisTelescope({
  initialState,
  projections,
  gradientArrows = [],
  onNodeClick,
  onNavigate,
  onStateChange,
  highLossNodes = [],
  keyboardEnabled = true,
  width = 800,
  height = 600,
}: GaloisTelescopeProps) {
  // Merge initial state with defaults
  const [state, setState] = useState<GaloisTelescopeState>(() => ({
    ...DEFAULT_STATE,
    ...initialState,
  }));

  const containerRef = useRef<HTMLDivElement>(null);
  const [hoveredNode, setHoveredNode] = useState<NodeId | null>(null);

  // Navigation hook
  const navigation = useTelescopeNavigation({
    state,
    projections,
    onNavigate,
  });

  // Update parent when state changes
  useEffect(() => {
    onStateChange?.(state);
  }, [state, onStateChange]);

  // Filter projections by visible layers and loss threshold
  const visibleProjections = useMemo(() => {
    return projections.filter((proj) => {
      // Check layer visibility
      if (!state.visible_layers.includes(proj.layer)) {
        return false;
      }
      // Check loss threshold (but always show focal node)
      if (proj.node_id === state.focal_point) {
        return true;
      }
      return proj.annotation?.loss !== undefined
        ? proj.annotation.loss <= state.loss_threshold
        : true;
    });
  }, [projections, state.visible_layers, state.loss_threshold, state.focal_point]);

  // Handle keyboard navigation
  useEffect(() => {
    if (!keyboardEnabled) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      // Don't capture if in input
      if (
        e.target instanceof HTMLInputElement ||
        e.target instanceof HTMLTextAreaElement
      ) {
        return;
      }

      const key = e.key;
      const shiftKey = e.shiftKey;

      // Loss navigation
      if (key === 'g' && !shiftKey) {
        // Wait for next key
        const handleNextKey = (e2: KeyboardEvent) => {
          if (e2.key === 'l') {
            e2.preventDefault();
            navigation.goLowestLoss();
          } else if (e2.key === 'h') {
            e2.preventDefault();
            navigation.goHighestLoss();
          }
          window.removeEventListener('keydown', handleNextKey);
        };
        window.addEventListener('keydown', handleNextKey, { once: true });
        return;
      }

      if (shiftKey && key === 'G') {
        e.preventDefault();
        navigation.followGradient();
        return;
      }

      if (key === 'L' && !shiftKey) {
        e.preventDefault();
        setState((s) => ({ ...s, show_loss: !s.show_loss }));
        return;
      }

      if (key === 'G' && !shiftKey) {
        e.preventDefault();
        setState((s) => ({ ...s, show_gradient: !s.show_gradient }));
        return;
      }

      if (key === '[') {
        e.preventDefault();
        setState((s) => ({
          ...s,
          loss_threshold: Math.max(0, s.loss_threshold - 0.1),
        }));
        return;
      }

      if (key === ']') {
        e.preventDefault();
        setState((s) => ({
          ...s,
          loss_threshold: Math.min(1, s.loss_threshold + 0.1),
        }));
        return;
      }

      // Zoom
      if (key === '+' || key === '=') {
        e.preventDefault();
        setState((s) => ({
          ...s,
          focal_distance: Math.max(0, s.focal_distance - 0.1),
          node_scale: 1.0 - Math.max(0, s.focal_distance - 0.1) * 0.7,
        }));
        return;
      }

      if (key === '-') {
        e.preventDefault();
        setState((s) => ({
          ...s,
          focal_distance: Math.min(1, s.focal_distance + 0.1),
          node_scale: 1.0 - Math.min(1, s.focal_distance + 0.1) * 0.7,
        }));
        return;
      }

      if (key === '0') {
        e.preventDefault();
        if (shiftKey) {
          // Micro view
          setState((s) => ({
            ...s,
            focal_distance: 0,
            node_scale: 1.0,
          }));
        } else {
          // Macro view
          setState((s) => ({
            ...s,
            focal_distance: 1,
            node_scale: 0.3,
          }));
        }
        return;
      }

      // Layer navigation (1-7)
      const layerNum = parseInt(key, 10);
      if (layerNum >= 1 && layerNum <= 7) {
        e.preventDefault();
        setState((s) => ({
          ...s,
          preferred_layer: layerNum,
          visible_layers:
            s.focal_distance < 0.2
              ? [layerNum]
              : s.focal_distance < 0.5
                ? [layerNum - 1, layerNum, layerNum + 1].filter(
                    (l) => l >= 1 && l <= 7
                  )
                : [1, 2, 3, 4, 5, 6, 7],
        }));
        return;
      }

      // Tab for layer cycling
      if (key === 'Tab') {
        e.preventDefault();
        setState((s) => {
          const delta = shiftKey ? -1 : 1;
          const newLayer = Math.max(1, Math.min(7, s.preferred_layer + delta));
          return {
            ...s,
            preferred_layer: newLayer,
          };
        });
        return;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [keyboardEnabled, navigation]);

  // Handle node click
  const handleNodeClick = useCallback(
    (nodeId: NodeId) => {
      setState((s) => ({ ...s, focal_point: nodeId }));
      onNodeClick?.(nodeId);
    },
    [onNodeClick]
  );

  // Scale position to viewport
  const scalePosition = useCallback(
    (pos: Position2D): Position2D => ({
      x: pos.x * width,
      y: pos.y * height,
    }),
    [width, height]
  );

  return (
    <div
      ref={containerRef}
      className="galois-telescope"
      style={{ width, height }}
      tabIndex={0}
    >
      {/* SVG canvas for nodes and arrows */}
      <svg
        className="galois-telescope__canvas"
        width={width}
        height={height}
        viewBox={`0 0 ${width} ${height}`}
      >
        {/* Gradient field arrows */}
        {state.show_gradient && (
          <GradientField
            arrows={gradientArrows}
            scalePosition={scalePosition}
          />
        )}

        {/* Nodes */}
        <g className="galois-telescope__nodes">
          {visibleProjections.map((proj) => (
            <LossNode
              key={proj.node_id}
              projection={proj}
              position={scalePosition(proj.position)}
              isHovered={hoveredNode === proj.node_id}
              isFocal={proj.node_id === state.focal_point}
              showLoss={state.show_loss}
              onClick={() => handleNodeClick(proj.node_id)}
              onMouseEnter={() => setHoveredNode(proj.node_id)}
              onMouseLeave={() => setHoveredNode(null)}
            />
          ))}
        </g>
      </svg>

      {/* Hover tooltip */}
      {hoveredNode && (
        <NodeTooltip
          nodeId={hoveredNode}
          projection={projections.find((p) => p.node_id === hoveredNode)}
        />
      )}

      {/* High-loss warnings */}
      {highLossNodes.length > 0 && (
        <div className="galois-telescope__warnings">
          <div className="galois-telescope__warning-header">
            High Loss Nodes ({highLossNodes.length})
          </div>
          {highLossNodes.slice(0, 3).map((node) => (
            <div
              key={node.node_id}
              className="galois-telescope__warning-item"
              onClick={() => handleNodeClick(node.node_id)}
            >
              <span className="galois-telescope__warning-id">
                {node.node_id}
              </span>
              <span className="galois-telescope__warning-loss">
                L={node.loss.toFixed(2)}
              </span>
              <span className="galois-telescope__warning-reason">
                {node.reason}
              </span>
            </div>
          ))}
        </div>
      )}

      {/* Loss legend */}
      <LossLegend
        colormap={state.loss_colormap}
        threshold={state.loss_threshold}
        showLoss={state.show_loss}
        showGradient={state.show_gradient}
      />

      {/* Status bar */}
      <div className="galois-telescope__status">
        <span className="galois-telescope__status-item">
          Focal: {state.focal_distance.toFixed(2)}
        </span>
        <span className="galois-telescope__status-item">
          Layer: {LAYER_NAMES[state.preferred_layer]}
        </span>
        <span className="galois-telescope__status-item">
          Threshold: {state.loss_threshold.toFixed(1)}
        </span>
        <span className="galois-telescope__status-item">
          Nodes: {visibleProjections.length}/{projections.length}
        </span>
        {state.focal_point && (
          <span className="galois-telescope__status-item galois-telescope__status-focal">
            Focus: {state.focal_point}
          </span>
        )}
      </div>
    </div>
  );
});

// -----------------------------------------------------------------------------
// Node Tooltip
// -----------------------------------------------------------------------------

interface NodeTooltipProps {
  nodeId: NodeId;
  projection?: NodeProjection;
}

const NodeTooltip = memo(function NodeTooltip({
  nodeId,
  projection,
}: NodeTooltipProps) {
  if (!projection?.annotation) return null;

  const { annotation } = projection;

  return (
    <div className="galois-telescope__tooltip">
      <div className="galois-telescope__tooltip-header">
        <span className="galois-telescope__tooltip-id">{nodeId}</span>
        <span className="galois-telescope__tooltip-layer">
          L{projection.layer} ({LAYER_NAMES[projection.layer]})
        </span>
      </div>
      <div className="galois-telescope__tooltip-loss">
        <div className="galois-telescope__tooltip-total">
          Loss: {annotation.loss.toFixed(3)}
          <span
            className={`galois-telescope__tooltip-status galois-telescope__tooltip-status--${annotation.threshold_status}`}
          >
            {annotation.threshold_status}
          </span>
        </div>
        <div className="galois-telescope__tooltip-components">
          <div>Content: {annotation.components.content_loss.toFixed(3)}</div>
          <div>Proof: {annotation.components.proof_loss.toFixed(3)}</div>
          <div>Edges: {annotation.components.edge_loss.toFixed(3)}</div>
          <div>Meta: {annotation.components.metadata_loss.toFixed(3)}</div>
        </div>
      </div>
      {projection.glow && (
        <div className="galois-telescope__tooltip-warning">
          High loss - investigate this node
        </div>
      )}
    </div>
  );
});

export default GaloisTelescope;
