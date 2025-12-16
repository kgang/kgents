/**
 * NodeTooltip - 3D-aware hover tooltip for Gestalt nodes.
 *
 * Uses @react-three/drei's Html component to render HTML
 * in 3D space that follows the node's position and camera.
 *
 * Features:
 * - Appears on hover after 300ms delay
 * - Shows key module metrics
 * - Follows camera rotation (always faces viewer)
 * - Mobile: appears on tap
 * - Density-aware sizing
 *
 * @see plans/gestalt-visual-showcase.md Chunk 2
 */

import { Html } from '@react-three/drei';
import { HEALTH_GRADE_CONFIG } from '../../api/types';
import type { CodebaseModule } from '../../api/types';
import type { Density } from './types';

// =============================================================================
// Types
// =============================================================================

export interface NodeTooltipProps {
  /** The module to display info for */
  node: CodebaseModule;
  /** Whether the tooltip is visible */
  visible: boolean;
  /** Density for responsive sizing */
  density: Density;
  /** Number of dependencies (optional, from full module details) */
  dependencyCount?: number;
  /** Number of dependents (optional, from full module details) */
  dependentCount?: number;
  /** Additional class names */
  className?: string;
}

export interface TooltipContentProps {
  node: CodebaseModule;
  density: Density;
  dependencyCount?: number;
  dependentCount?: number;
}

// =============================================================================
// CSS Keyframes (injected once)
// =============================================================================

const tooltipStyles = `
@keyframes tooltip-fade-in {
  from {
    opacity: 0;
    transform: translateY(4px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
`;

// Inject styles once
if (typeof document !== 'undefined') {
  const styleId = 'gestalt-tooltip-styles';
  if (!document.getElementById(styleId)) {
    const styleEl = document.createElement('style');
    styleEl.id = styleId;
    styleEl.textContent = tooltipStyles;
    document.head.appendChild(styleEl);
  }
}

// =============================================================================
// Tooltip Content (pure HTML component)
// =============================================================================

function TooltipContent({ node, density, dependencyCount, dependentCount }: TooltipContentProps) {
  const gradeConfig = HEALTH_GRADE_CONFIG[node.health_grade] || HEALTH_GRADE_CONFIG['?'];
  const isCompact = density === 'compact';

  return (
    <div
      className={`
        bg-gray-900/95 backdrop-blur-sm rounded-lg shadow-2xl
        border border-gray-700/80 text-white
        pointer-events-none select-none
        ${isCompact ? 'min-w-[160px] p-2' : 'min-w-[200px] p-2.5'}
      `}
      style={{
        // Prevent text from breaking in weird places
        whiteSpace: 'nowrap',
        // Fade-in animation
        animation: 'tooltip-fade-in 150ms ease-out',
      }}
    >
      {/* Header: Module name */}
      <div className={`font-semibold ${isCompact ? 'text-xs' : 'text-sm'} mb-1.5 truncate max-w-[220px]`}>
        {node.label}
      </div>

      {/* Divider */}
      <div className="h-px bg-gray-700/50 mb-1.5" />

      {/* Health row */}
      <div className="flex items-center justify-between gap-3 mb-1">
        <span className={`text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>Health</span>
        <div className="flex items-center gap-1.5">
          <span
            className={`font-bold ${isCompact ? 'text-xs' : 'text-sm'}`}
            style={{ color: gradeConfig.color }}
          >
            {node.health_grade}
          </span>
          <span className={`text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
            ({Math.round(node.health_score * 100)}%)
          </span>
        </div>
      </div>

      {/* Layer row */}
      {node.layer && (
        <div className="flex items-center justify-between gap-3 mb-1">
          <span className={`text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>Layer</span>
          <span
            className={`text-indigo-300 font-medium ${isCompact ? 'text-[10px]' : 'text-xs'}`}
          >
            {node.layer}
          </span>
        </div>
      )}

      {/* LOC row */}
      <div className="flex items-center justify-between gap-3 mb-1">
        <span className={`text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>LOC</span>
        <span className={`text-gray-200 font-mono ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
          {node.lines_of_code.toLocaleString()}
        </span>
      </div>

      {/* Dependencies/Dependents (if provided) */}
      {(dependencyCount !== undefined || dependentCount !== undefined) && (
        <div className="flex items-center justify-between gap-3 mb-1">
          {dependencyCount !== undefined && (
            <div className="flex items-center gap-1">
              <span className={`text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>Deps:</span>
              <span className={`text-blue-300 font-mono ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
                {dependencyCount}
              </span>
            </div>
          )}
          {dependentCount !== undefined && (
            <div className="flex items-center gap-1">
              <span className={`text-gray-400 ${isCompact ? 'text-[10px]' : 'text-xs'}`}>Used by:</span>
              <span className={`text-green-300 font-mono ${isCompact ? 'text-[10px]' : 'text-xs'}`}>
                {dependentCount}
              </span>
            </div>
          )}
        </div>
      )}

      {/* Footer hint */}
      <div className="h-px bg-gray-700/50 my-1.5" />
      <div className={`text-center text-gray-500 ${isCompact ? 'text-[9px]' : 'text-[10px]'}`}>
        Click for details
      </div>
    </div>
  );
}

// =============================================================================
// Main Component (3D wrapper)
// =============================================================================

/**
 * NodeTooltip renders an HTML tooltip in 3D space.
 *
 * IMPORTANT: This component must be rendered inside a Three.js canvas
 * as a child of the module's group, positioned at the node's position.
 *
 * @example
 * ```tsx
 * <group position={[node.x, node.y, node.z]}>
 *   <mesh>...</mesh>
 *   <NodeTooltip node={node} visible={hovered} density={density} />
 * </group>
 * ```
 */
export function NodeTooltip({
  node,
  visible,
  density,
  dependencyCount,
  dependentCount,
  className,
}: NodeTooltipProps) {
  if (!visible) return null;

  // Calculate offset based on node size (approximate)
  const yOffset = 0.6 + node.health_score * 0.2;

  return (
    <Html
      // Position above the node
      position={[0, yOffset, 0]}
      // Center horizontally, anchor at bottom
      center
      // Use sprite mode for better performance with many tooltips
      sprite
      // Always render on top
      zIndexRange={[100, 0]}
      // Scale with distance
      distanceFactor={10}
      // Additional CSS classes
      className={className}
      // Disable pointer events on the Html wrapper
      style={{ pointerEvents: 'none' }}
    >
      <TooltipContent
        node={node}
        density={density}
        dependencyCount={dependencyCount}
        dependentCount={dependentCount}
      />
    </Html>
  );
}

// =============================================================================
// Standalone Tooltip (for non-3D contexts)
// =============================================================================

export interface StandaloneTooltipProps extends TooltipContentProps {
  /** Absolute position */
  position: { x: number; y: number };
  /** Whether visible */
  visible: boolean;
}

/**
 * StandaloneTooltip renders a tooltip at a fixed screen position.
 * Use this when you need a tooltip outside the 3D canvas.
 */
export function StandaloneTooltip({
  node,
  density,
  dependencyCount,
  dependentCount,
  position,
  visible,
}: StandaloneTooltipProps) {
  if (!visible) return null;

  return (
    <div
      className="fixed z-50 pointer-events-none"
      style={{
        left: position.x,
        top: position.y,
        transform: 'translate(-50%, -100%) translateY(-8px)',
      }}
    >
      <TooltipContent
        node={node}
        density={density}
        dependencyCount={dependencyCount}
        dependentCount={dependentCount}
      />
    </div>
  );
}

export default NodeTooltip;
