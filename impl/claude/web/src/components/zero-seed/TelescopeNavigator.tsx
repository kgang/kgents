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
import { GaloisTelescope } from './GaloisTelescope';
import type { NodeProjection, GradientArrow, GaloisTelescopeState } from './types';
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

function getLossColorHex(loss: number): string {
  // Viridis colors as hex
  if (loss < 0.3) return '#440154'; // Deep purple (low loss - stable)
  if (loss < 0.6) return '#31688e'; // Blue-green (mid loss)
  return '#fde724'; // Yellow (high loss - drift)
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

/**
 * Transform ZeroNode to NodeProjection for GaloisTelescope
 */
function transformToProjection(
  node: ZeroNode,
  position: { x: number; y: number },
  gradient: GradientVector | undefined,
  isFocal: boolean,
  state: TelescopeState
): NodeProjection {
  // Estimate loss from gradient magnitude (higher gradient = higher loss)
  const loss = gradient ? gradient.magnitude : 0.5;

  return {
    node_id: node.id,
    layer: node.layer,
    position: { x: position.x, y: position.y },
    scale: isFocal ? 1.5 : 0.65,
    opacity: 1.0,
    is_focal: isFocal,
    color: getLossColor(loss),
    color_hex: getLossColorHex(loss),
    glow: state.show_loss && loss > 0.7,
    glow_intensity: loss > 0.7 ? (loss - 0.7) / 0.3 : 0,
    gradient,
    annotation: gradient ? {
      loss,
      components: {
        content_loss: loss * 0.4,
        proof_loss: loss * 0.2,
        edge_loss: loss * 0.3,
        metadata_loss: loss * 0.1,
        total: loss,
      },
      threshold_status: loss <= state.loss_threshold ? 'visible' : 'hidden',
      tooltip: `Loss: ${loss.toFixed(3)} | Gradient: ${gradient.magnitude.toFixed(3)}`,
    } : undefined,
  };
}

/**
 * Transform API gradients to GradientArrow format for GradientField
 */
function transformGradientsToArrows(
  gradients: Map<string, GradientVector>,
  nodePositions: Map<string, { x: number; y: number }>
): GradientArrow[] {
  const arrows: GradientArrow[] = [];

  for (const [nodeId, gradient] of gradients.entries()) {
    const pos = nodePositions.get(nodeId);
    if (!pos || gradient.magnitude < 0.01) continue;

    // Scale arrow length based on magnitude
    const arrowLength = 0.05 * gradient.magnitude; // 5% of viewport per unit magnitude

    // Start position is the node
    const start = { x: pos.x, y: pos.y };

    // End position is start + gradient direction * length
    const end = {
      x: pos.x + gradient.x * arrowLength,
      y: pos.y + gradient.y * arrowLength,
    };

    // Color based on magnitude (green = low, yellow = medium, red = high)
    let color = '#22c55e'; // green (low gradient - stable)
    if (gradient.magnitude > 0.7) {
      color = '#ef4444'; // red (high gradient - unstable)
    } else if (gradient.magnitude > 0.4) {
      color = '#f59e0b'; // orange (medium gradient)
    }

    arrows.push({
      start,
      end,
      magnitude: gradient.magnitude,
      color,
      width: 2,
    });
  }

  return arrows;
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
  policyArrows: _policyArrows, // Not used - GaloisTelescope handles gradient visualization
  onStateChange,
  onNavigate,
  loading = false,
}: TelescopeNavigatorProps) {
  const containerRef = useRef<HTMLDivElement>(null);
  const [dimensions, setDimensions] = useState({ width: 800, height: 600 });

  // Update dimensions on resize
  useEffect(() => {
    const updateDimensions = () => {
      const container = containerRef.current;
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

  // Transform nodes to projections for GaloisTelescope
  const projections = useMemo(() => {
    return visibleNodes.map(node => {
      const position = nodePositions.get(node.id);
      if (!position) return null;

      const gradient = gradients.get(node.id);
      const isFocal = state.focal_point === node.id;

      return transformToProjection(node, position, gradient, isFocal, state);
    }).filter((p): p is NodeProjection => p !== null);
  }, [visibleNodes, nodePositions, gradients, state]);

  // Transform gradients to arrows for GradientField
  const gradientArrows = useMemo(() => {
    return transformGradientsToArrows(gradients, nodePositions);
  }, [gradients, nodePositions]);

  // Transform high-loss nodes
  const highLossNodes = useMemo(() => {
    return projections
      .filter(p => p.annotation && p.annotation.loss > 0.7)
      .map(p => ({
        node_id: p.node_id,
        loss: p.annotation?.loss ?? 0,
        reason: 'High gradient detected - potential semantic drift',
      }))
      .slice(0, 5);
  }, [projections]);

  // Handle node click
  const handleNodeClick = useCallback(
    (nodeId: string) => {
      onStateChange?.({ focal_point: nodeId });
      onNavigate?.(nodeId, 'focus');
    },
    [onStateChange, onNavigate]
  );

  // Note: Keyboard navigation is handled by GaloisTelescope component
  // This component only provides UI controls for mouse interaction

  if (loading) {
    return (
      <div className="zero-seed-panel zero-seed-panel--loading">
        <div className="zero-seed-panel__spinner" />
        <span>Loading telescope...</span>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="zero-seed-panel telescope-navigator">
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
        <span className="hint"><kbd>[</kbd>/<kbd>]</kbd> threshold</span>
        <span className="hint"><kbd>+/-</kbd> zoom</span>
        <span className="hint"><kbd>1-7</kbd> layer</span>
        <span className="hint"><kbd>Tab</kbd> cycle layers</span>
      </div>

      {/* Canvas - GaloisTelescope */}
      <div className="telescope-canvas-container">
        <GaloisTelescope
          initialState={{
            focal_distance: state.focal_distance,
            focal_point: state.focal_point,
            show_loss: state.show_loss,
            show_gradient: state.show_gradient,
            loss_threshold: state.loss_threshold,
            loss_colormap: 'viridis',
            visible_layers: state.visible_layers,
            node_scale: 0.65,
            preferred_layer: state.preferred_layer,
          }}
          projections={projections}
          gradientArrows={gradientArrows}
          onNodeClick={handleNodeClick}
          onNavigate={(action, nodeId) => {
            if (!nodeId) return;

            // Map NavigationAction to the expected callback format
            switch (action) {
              case 'focus':
              case 'go_lowest_loss':
              case 'go_highest_loss':
                onStateChange?.({ focal_point: nodeId });
                onNavigate?.(nodeId, 'focus');
                break;
              case 'follow_gradient':
                onNavigate?.(nodeId, 'follow_gradient');
                break;
            }
          }}
          onStateChange={(newState: GaloisTelescopeState) => {
            // Convert GaloisTelescopeState to TelescopeState
            onStateChange?.({
              focal_distance: newState.focal_distance,
              focal_point: newState.focal_point,
              show_loss: newState.show_loss,
              show_gradient: newState.show_gradient,
              loss_threshold: newState.loss_threshold,
              visible_layers: newState.visible_layers as ZeroLayer[],
              preferred_layer: newState.preferred_layer as ZeroLayer,
            });
          }}
          highLossNodes={highLossNodes}
          keyboardEnabled={true}
          width={dimensions.width}
          height={dimensions.height}
        />
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
