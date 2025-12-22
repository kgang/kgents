/**
 * ContextNode - Custom react-flow node for trail visualization.
 *
 * Displays a context node (file, function, concept) visited in the trail.
 *
 * Visual States:
 * - Default: Neutral background
 * - Current: Glow + scale effect
 * - Selected: Border highlight
 *
 * @see spec/protocols/trail-protocol.md Section 8
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { motion } from 'framer-motion';

/**
 * Data shape for ContextNode.
 */
export interface ContextNodeData {
  /** Full path of this node */
  path: string;
  /** Holon name (last segment) */
  holon: string;
  /** Step index in trail */
  step_index: number;
  /** Edge type that led here */
  edge_type: string | null;
  /** LLM reasoning */
  reasoning: string | null;
  /** Whether this is the current position */
  is_current: boolean;
}

/**
 * Custom node component for trail graph.
 *
 * Joy-inducing design: hover scales up with glow, current pulses,
 * selected has distinct visual.
 */
function ContextNodeComponent({ data, selected }: NodeProps<ContextNodeData>) {
  const { path, holon, step_index, edge_type, reasoning, is_current } = data;

  // Determine edge category for coloring
  const edgeColor = getEdgeColor(edge_type);

  // Dynamic glow based on state
  const glowColor = is_current ? 'rgba(59, 130, 246, 0.4)' : selected ? 'rgba(168, 85, 247, 0.3)' : 'transparent';

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{
        scale: is_current ? 1.05 : 1,
        opacity: 1,
      }}
      whileHover={{
        scale: is_current ? 1.08 : 1.03,
        boxShadow: `0 0 24px ${edgeColor}40`,
        transition: { duration: 0.15 },
      }}
      transition={{ duration: 0.2 }}
      className={`
        px-4 py-3 rounded-lg min-w-[180px] max-w-[280px] cursor-pointer
        ${is_current ? 'ring-2 ring-blue-500' : ''}
        ${selected ? 'ring-2 ring-purple-400' : ''}
        bg-gray-800 border border-gray-700
        hover:border-gray-500 transition-colors
      `}
      style={{
        boxShadow: is_current
          ? `0 0 20px ${glowColor}, 0 4px 12px rgba(0,0,0,0.3)`
          : selected
            ? `0 0 16px ${glowColor}`
            : undefined,
      }}
    >
      {/* Input handle */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-2 h-2 !bg-gray-500"
      />

      {/* Step number badge */}
      <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-gray-700 border border-gray-600 flex items-center justify-center text-xs text-gray-300">
        {step_index + 1}
      </div>

      {/* Holon name */}
      <div className="font-medium text-white truncate">{holon}</div>

      {/* Full path (collapsed) */}
      <div className="text-xs text-gray-400 truncate mt-1" title={path}>
        {path}
      </div>

      {/* Edge type badge */}
      {edge_type && (
        <div
          className="inline-flex items-center gap-1 mt-2 px-2 py-0.5 rounded text-xs"
          style={{ backgroundColor: `${edgeColor}20`, color: edgeColor }}
        >
          <span className="opacity-70">via</span>
          <span className="font-medium">{edge_type}</span>
        </div>
      )}

      {/* Reasoning preview (if present) */}
      {reasoning && (
        <div
          className="mt-2 text-xs text-gray-400 italic line-clamp-2"
          title={reasoning}
        >
          "{reasoning.slice(0, 80)}{reasoning.length > 80 ? '...' : ''}"
        </div>
      )}

      {/* Current position indicator - animated pulse */}
      {is_current && (
        <motion.div
          className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-3 h-3 rounded-full bg-blue-500"
          animate={{
            scale: [1, 1.4, 1],
            opacity: [1, 0.6, 1],
          }}
          transition={{
            duration: 1.5,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          style={{
            boxShadow: '0 0 8px rgba(59, 130, 246, 0.8)',
          }}
        />
      )}

      {/* Output handle */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-2 h-2 !bg-gray-500"
      />
    </motion.div>
  );
}

/**
 * Get edge color based on edge type.
 */
export function getEdgeColor(edgeType: string | null): string {
  if (!edgeType) return '#6b7280';

  const colors: Record<string, string> = {
    imports: '#3b82f6',
    contains: '#f59e0b',
    tests: '#22c55e',
    implements: '#8b5cf6',
    calls: '#ec4899',
    semantic: '#06b6d4',
    similar_to: '#06b6d4',
    type_of: '#8b5cf6',
    pattern: '#f97316',
  };

  return colors[edgeType] || '#6b7280';
}

// Memoize for performance
export const ContextNode = memo(ContextNodeComponent);

// Register node type
export const nodeTypes = {
  context: ContextNode,
};

export default ContextNode;
