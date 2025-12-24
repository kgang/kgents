/**
 * TelescopeNavigator — View L7 navigation with loss gradients
 *
 * "Navigate toward stability. The gradient IS the guide. The loss IS the landscape."
 *
 * User Journey:
 * - Layer zoom (gl/gh navigation)
 * - Loss gradient visualization
 * - Policy arrows for optimal paths
 * - Value-guided suggestions
 */

import { memo, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import type {
  TelescopeState,
  ZeroNode,
  GradientVector,
  NavigationSuggestion,
  PolicyArrow,
  ZeroLayer,
} from '../../api/zeroSeed';
import { LAYER_NAMES } from '../../api/zeroSeed';
import './ZeroSeed.css';

// =============================================================================
// Types
// =============================================================================

interface TelescopeNavigatorProps {
  /** Current telescope state */
  state: TelescopeState;
  /** Visible nodes */
  nodes: ZeroNode[];
  /** Gradient vectors by node */
  gradients: Map<string, GradientVector>;
  /** Navigation suggestions */
  suggestions: NavigationSuggestion[];
  /** Policy arrows (optimal paths) */
  policyArrows: PolicyArrow[];
  /** State change callback */
  onStateChange?: (state: Partial<TelescopeState>) => void;
  /** Navigate to node */
  onNavigate?: (nodeId: string, action: 'focus' | 'follow_gradient') => void;
  /** Loading state */
  loading?: boolean;
}

// =============================================================================
// Helpers
// =============================================================================

function getLossColor(loss: number): string {
  // Viridis-inspired: purple (low) -> green (mid) -> yellow (high)
  if (loss < 0.3) return 'var(--viridis-low)';
  if (loss < 0.6) return 'var(--viridis-mid)';
  return 'var(--viridis-high)';
}

function getNodePosition(
  node: ZeroNode,
  allNodes: ZeroNode[],
  _focalPoint: string | null,
  focalDistance: number
): { x: number; y: number } {
  // Base vertical position from layer
  const baseY = ((node.layer - 1) / 6) * 0.8 + 0.1;

  // Horizontal position based on index within layer
  const layerNodes = allNodes.filter((n) => n.layer === node.layer);
  const index = layerNodes.findIndex((n) => n.id === node.id);
  const count = layerNodes.length;
  const baseX = count > 1 ? (index / (count - 1)) * 0.8 + 0.1 : 0.5;

  // Adjust based on focal distance (zoom)
  const scale = 1 - focalDistance * 0.5;
  const centerX = 0.5;
  const centerY = 0.5;

  return {
    x: centerX + (baseX - centerX) * scale,
    y: centerY + (baseY - centerY) * scale,
  };
}

// =============================================================================
// Sub-components
// =============================================================================

interface TelescopeControlsProps {
  state: TelescopeState;
  onStateChange: (state: Partial<TelescopeState>) => void;
}

const TelescopeControls = memo(function TelescopeControls({
  state,
  onStateChange,
}: TelescopeControlsProps) {
  return (
    <div className="telescope-controls">
      {/* Focal distance slider */}
      <div className="control-group">
        <label>Focal Distance</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={state.focal_distance}
          onChange={(e) =>
            onStateChange({ focal_distance: parseFloat(e.target.value) })
          }
        />
        <span className="control-value">{state.focal_distance.toFixed(2)}</span>
      </div>

      {/* Loss threshold slider */}
      <div className="control-group">
        <label>Loss Threshold</label>
        <input
          type="range"
          min="0"
          max="1"
          step="0.05"
          value={state.loss_threshold}
          onChange={(e) =>
            onStateChange({ loss_threshold: parseFloat(e.target.value) })
          }
        />
        <span className="control-value">{state.loss_threshold.toFixed(2)}</span>
      </div>

      {/* Layer selector */}
      <div className="control-group">
        <label>Preferred Layer</label>
        <div className="layer-selector">
          {([1, 2, 3, 4, 5, 6, 7] as ZeroLayer[]).map((layer) => (
            <button
              key={layer}
              className={`layer-btn ${state.preferred_layer === layer ? 'layer-btn--active' : ''}`}
              onClick={() => onStateChange({ preferred_layer: layer })}
            >
              {layer}
            </button>
          ))}
        </div>
      </div>

      {/* Toggles */}
      <div className="control-group control-group--toggles">
        <label>
          <input
            type="checkbox"
            checked={state.show_loss}
            onChange={(e) => onStateChange({ show_loss: e.target.checked })}
          />
          Show Loss
        </label>
        <label>
          <input
            type="checkbox"
            checked={state.show_gradient}
            onChange={(e) => onStateChange({ show_gradient: e.target.checked })}
          />
          Show Gradient
        </label>
      </div>
    </div>
  );
});

interface SuggestionsListProps {
  suggestions: NavigationSuggestion[];
  onNavigate: (nodeId: string, action: 'focus' | 'follow_gradient') => void;
}

const SuggestionsList = memo(function SuggestionsList({
  suggestions,
  onNavigate,
}: SuggestionsListProps) {
  if (suggestions.length === 0) {
    return (
      <div className="suggestions-list suggestions-list--empty">
        <span>No navigation suggestions available</span>
      </div>
    );
  }

  return (
    <div className="suggestions-list">
      <h4>Navigation Suggestions</h4>
      {suggestions.slice(0, 5).map((s, i) => (
        <div
          key={`${s.target}-${i}`}
          className="suggestion-card"
          onClick={() => onNavigate(s.target, s.action === 'investigate' ? 'focus' : s.action)}
        >
          <div className="suggestion-card__header">
            <span className="suggestion-card__action">{s.action}</span>
            <span className="suggestion-card__score">
              {(s.value_score * 100).toFixed(0)}
            </span>
          </div>
          <span className="suggestion-card__target">{s.target}</span>
          <p className="suggestion-card__reasoning">{s.reasoning}</p>
        </div>
      ))}
    </div>
  );
});

// =============================================================================
// Main Component
// =============================================================================

export const TelescopeNavigator = memo(function TelescopeNavigator({
  state,
  nodes,
  gradients,
  suggestions,
  policyArrows,
  onStateChange,
  onNavigate,
  loading = false,
}: TelescopeNavigatorProps) {
  const canvasRef = useRef<SVGSVGElement>(null);
  const [hoveredNode, setHoveredNode] = useState<string | null>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      const container = canvasRef.current?.parentElement;
      if (container) {
        setDimensions({
          width: container.clientWidth,
          height: container.clientHeight - 200, // Account for controls
        });
      }
    };

    updateDimensions();
    window.addEventListener('resize', updateDimensions);
    return () => window.removeEventListener('resize', updateDimensions);
  }, []);

  // Filter visible nodes
  const visibleNodes = useMemo(() => {
    return nodes.filter((n) => state.visible_layers.includes(n.layer as ZeroLayer));
  }, [nodes, state.visible_layers]);

  // Node positions
  const nodePositions = useMemo(() => {
    const positions = new Map<string, { x: number; y: number }>();
    for (const node of visibleNodes) {
      positions.set(
        node.id,
        getNodePosition(node, visibleNodes, state.focal_point, state.focal_distance)
      );
    }
    return positions;
  }, [visibleNodes, state.focal_point, state.focal_distance]);

  // Handle node click
  const handleNodeClick = useCallback(
    (nodeId: string) => {
      onStateChange?.({ focal_point: nodeId });
      onNavigate?.(nodeId, 'focus');
    },
    [onStateChange, onNavigate]
  );

  // Handle keyboard navigation
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.target instanceof HTMLInputElement) return;

      switch (e.key) {
        case 'g':
          if (e.shiftKey) {
            // Follow gradient
            if (state.focal_point) {
              onNavigate?.(state.focal_point, 'follow_gradient');
            }
          }
          break;
        case 'L':
          onStateChange?.({ show_loss: !state.show_loss });
          break;
        case 'G':
          onStateChange?.({ show_gradient: !state.show_gradient });
          break;
        case '[':
          onStateChange?.({
            loss_threshold: Math.max(0, state.loss_threshold - 0.1),
          });
          break;
        case ']':
          onStateChange?.({
            loss_threshold: Math.min(1, state.loss_threshold + 0.1),
          });
          break;
        case '+':
        case '=':
          onStateChange?.({
            focal_distance: Math.max(0, state.focal_distance - 0.1),
          });
          break;
        case '-':
          onStateChange?.({
            focal_distance: Math.min(1, state.focal_distance + 0.1),
          });
          break;
        case '1':
        case '2':
        case '3':
        case '4':
        case '5':
        case '6':
        case '7':
          onStateChange?.({ preferred_layer: parseInt(e.key) as ZeroLayer });
          break;
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [state, onStateChange, onNavigate]);

  if (loading) {
    return (
      <div className="zero-seed-panel zero-seed-panel--loading">
        <div className="zero-seed-panel__spinner" />
        <span>Loading telescope...</span>
      </div>
    );
  }

  return (
    <div className="zero-seed-panel telescope-navigator">
      {/* Header */}
      <header className="zero-seed-panel__header">
        <h2 className="zero-seed-panel__title">
          Telescope Navigator
          <span className="zero-seed-panel__subtitle">L7 Representation Layer</span>
        </h2>
        <div className="zero-seed-panel__stats">
          <span className="stat">
            {visibleNodes.length} / {nodes.length} visible
          </span>
          {state.focal_point && (
            <span className="stat stat--focal">Focus: {state.focal_point}</span>
          )}
        </div>
      </header>

      {/* Controls */}
      <TelescopeControls
        state={state}
        onStateChange={onStateChange || (() => {})}
      />

      {/* Keyboard hints */}
      <div className="telescope-hints">
        <span className="hint"><kbd>gl</kbd> lowest loss</span>
        <span className="hint"><kbd>gh</kbd> highest loss</span>
        <span className="hint"><kbd>Shift+G</kbd> follow gradient</span>
        <span className="hint"><kbd>L</kbd> toggle loss</span>
        <span className="hint"><kbd>G</kbd> toggle gradient</span>
        <span className="hint"><kbd>+/-</kbd> zoom</span>
        <span className="hint"><kbd>1-7</kbd> layer</span>
      </div>

      {/* Canvas */}
      <div className="telescope-canvas-container">
        <svg
          ref={canvasRef}
          className="telescope-canvas"
          width={dimensions.width}
          height={dimensions.height}
          viewBox={`0 0 ${dimensions.width} ${dimensions.height}`}
        >
          {/* Policy arrows (optimal paths) */}
          {policyArrows.map((arrow, i) => {
            const fromPos = nodePositions.get(arrow.from);
            const toPos = nodePositions.get(arrow.to);
            if (!fromPos || !toPos) return null;

            const x1 = fromPos.x * dimensions.width;
            const y1 = fromPos.y * dimensions.height;
            const x2 = toPos.x * dimensions.width;
            const y2 = toPos.y * dimensions.height;

            return (
              <line
                key={`policy-${i}`}
                x1={x1}
                y1={y1}
                x2={x2}
                y2={y2}
                className={`policy-arrow ${arrow.is_optimal ? 'policy-arrow--optimal' : ''}`}
                strokeWidth={arrow.is_optimal ? 3 : 1}
                markerEnd="url(#arrowhead)"
              />
            );
          })}

          {/* Gradient arrows */}
          {state.show_gradient &&
            Array.from(gradients.entries()).map(([nodeId, gradient]) => {
              const pos = nodePositions.get(nodeId);
              if (!pos || gradient.magnitude < 0.01) return null;

              const x1 = pos.x * dimensions.width;
              const y1 = pos.y * dimensions.height;
              const scale = 50 * gradient.magnitude;
              const x2 = x1 + gradient.x * scale;
              const y2 = y1 + gradient.y * scale;

              return (
                <line
                  key={`gradient-${nodeId}`}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  className="gradient-arrow"
                  strokeWidth={2}
                  markerEnd="url(#gradient-arrowhead)"
                />
              );
            })}

          {/* Nodes */}
          {visibleNodes.map((node) => {
            const pos = nodePositions.get(node.id);
            if (!pos) return null;

            const x = pos.x * dimensions.width;
            const y = pos.y * dimensions.height;
            const isFocal = state.focal_point === node.id;
            const isHovered = hoveredNode === node.id;
            const nodeScale = isFocal ? 1.5 : 1;
            const baseRadius = 20;
            const radius = baseRadius * nodeScale;

            // Get gradient for loss color if showing loss
            const gradient = gradients.get(node.id);
            const loss = gradient ? 1 - gradient.magnitude : 0.5;

            return (
              <g
                key={node.id}
                className={`telescope-node ${isFocal ? 'telescope-node--focal' : ''} ${isHovered ? 'telescope-node--hovered' : ''}`}
                transform={`translate(${x}, ${y})`}
                onClick={() => handleNodeClick(node.id)}
                onMouseEnter={() => setHoveredNode(node.id)}
                onMouseLeave={() => setHoveredNode(null)}
              >
                {/* Glow for high loss */}
                {state.show_loss && loss > 0.7 && (
                  <circle
                    r={radius + 8}
                    className="node-glow"
                    fill="none"
                    stroke="var(--status-error)"
                    strokeWidth={2}
                    opacity={0.5}
                  />
                )}

                {/* Main node circle */}
                <circle
                  r={radius}
                  className="node-circle"
                  data-layer={node.layer}
                  fill={state.show_loss ? getLossColor(loss) : undefined}
                />

                {/* Layer badge */}
                <text
                  y={-radius - 8}
                  className="node-layer-badge"
                  textAnchor="middle"
                >
                  L{node.layer}
                </text>

                {/* Title (only on hover or focus) */}
                {(isHovered || isFocal) && (
                  <text y={radius + 16} className="node-title" textAnchor="middle">
                    {node.title.length > 20
                      ? node.title.slice(0, 20) + '...'
                      : node.title}
                  </text>
                )}

                {/* Focal indicator */}
                {isFocal && (
                  <circle
                    r={radius + 4}
                    fill="none"
                    stroke="var(--accent-primary)"
                    strokeWidth={2}
                    className="focal-ring"
                  />
                )}
              </g>
            );
          })}

          {/* Arrow markers */}
          <defs>
            <marker
              id="arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                fill="var(--steel-500)"
              />
            </marker>
            <marker
              id="gradient-arrowhead"
              markerWidth="10"
              markerHeight="7"
              refX="9"
              refY="3.5"
              orient="auto"
            >
              <polygon
                points="0 0, 10 3.5, 0 7"
                fill="var(--status-insert)"
              />
            </marker>
          </defs>
        </svg>

        {/* Layer labels */}
        <div className="telescope-layer-labels">
          {([1, 2, 3, 4, 5, 6, 7] as ZeroLayer[]).map((layer) => (
            <div
              key={layer}
              className={`layer-label ${state.visible_layers.includes(layer) ? '' : 'layer-label--hidden'}`}
              style={{
                top: `${((layer - 1) / 6) * 80 + 10}%`,
              }}
            >
              L{layer}: {LAYER_NAMES[layer]}
            </div>
          ))}
        </div>
      </div>

      {/* Suggestions sidebar */}
      <SuggestionsList
        suggestions={suggestions}
        onNavigate={onNavigate || (() => {})}
      />

      {/* Loss legend */}
      {state.show_loss && (
        <div className="telescope-loss-legend">
          <span className="legend-title">Loss</span>
          <div className="legend-gradient" />
          <div className="legend-labels">
            <span>0.0 (stable)</span>
            <span>0.5</span>
            <span>1.0 (drift)</span>
          </div>
        </div>
      )}
    </div>
  );
});

export default TelescopeNavigator;
