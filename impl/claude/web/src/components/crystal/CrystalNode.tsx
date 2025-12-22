/**
 * CrystalNode - Custom react-flow node for crystal hierarchy visualization.
 *
 * Displays a crystal from the witness crystallization system.
 * Color-coded by level with confidence badge and compression indicator.
 *
 * Visual Design:
 * - Level determines background color (SESSION=blue, DAY=green, WEEK=amber, EPOCH=purple)
 * - Confidence shown as opacity/glow intensity
 * - Source count badge shows compression ratio
 * - Principles shown as small tags
 *
 * @see spec/protocols/witness-crystallization.md
 * @see services/witness/crystal_trail.py
 */

import { memo } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { motion } from 'framer-motion';

import { type CrystalLevel, getLevelColor, getConfidenceStrength } from '../../api/crystal';

/**
 * Data shape for CrystalNode.
 */
export interface CrystalNodeData {
  /** Crystal ID */
  crystal_id: string;
  /** Crystal level */
  level: CrystalLevel;
  /** Level as number (0-3) */
  level_value: number;
  /** Compressed insight */
  insight: string;
  /** Why it matters */
  significance: string;
  /** Confidence score (0-1) */
  confidence: number;
  /** Number of sources */
  source_count: number;
  /** Principles that emerged */
  principles: string[];
  /** Topics for retrieval */
  topics: string[];
  /** When crystallized */
  crystallized_at: string;

  // Trail-compatible fields
  /** AGENTESE path */
  path: string;
  /** Display name (level) */
  holon: string;
  /** Step index (level value) */
  step_index: number;
  /** Edge type */
  edge_type: string;
  /** Reasoning (significance) */
  reasoning: string | null;
  /** Whether currently selected */
  is_current: boolean;
}

/**
 * Custom node component for crystal graph.
 */
function CrystalNodeComponent({ data, selected }: NodeProps<CrystalNodeData>) {
  const {
    level,
    insight,
    significance,
    confidence,
    source_count,
    principles,
    is_current,
  } = data;

  const levelColor = getLevelColor(level);
  const strength = getConfidenceStrength(confidence);

  // Confidence affects opacity and glow
  const glowIntensity = confidence * 0.4;

  return (
    <motion.div
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{
        scale: is_current ? 1.05 : 1,
        opacity: 0.7 + confidence * 0.3,
      }}
      transition={{ duration: 0.3 }}
      className={`
        relative px-4 py-3 rounded-xl min-w-[200px] max-w-[300px]
        ${is_current ? 'ring-2 ring-white shadow-lg' : ''}
        ${selected ? 'ring-2 ring-purple-400' : ''}
        hover:ring-2 hover:ring-gray-400 transition-all cursor-pointer
      `}
      style={{
        backgroundColor: `${levelColor}20`,
        borderWidth: 2,
        borderColor: levelColor,
        boxShadow: is_current
          ? `0 0 20px ${levelColor}${Math.round(glowIntensity * 255).toString(16).padStart(2, '0')}`
          : undefined,
      }}
    >
      {/* Input handle (from lower levels) */}
      <Handle
        type="target"
        position={Position.Bottom}
        className="w-3 h-3"
        style={{ backgroundColor: levelColor }}
      />

      {/* Level badge */}
      <div
        className="absolute -top-3 left-4 px-2 py-0.5 rounded-full text-xs font-medium"
        style={{ backgroundColor: levelColor, color: 'white' }}
      >
        {level}
      </div>

      {/* Source count badge */}
      <div
        className="absolute -top-2 -right-2 w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold"
        style={{
          backgroundColor: levelColor,
          color: 'white',
          border: '2px solid #1f2937',
        }}
        title={`Compresses ${source_count} sources`}
      >
        {source_count > 99 ? '99+' : source_count}
      </div>

      {/* Insight (main content) */}
      <div className="mt-2 font-medium text-white text-sm leading-tight line-clamp-2">
        {insight}
      </div>

      {/* Significance (secondary) */}
      {significance && (
        <div
          className="mt-2 text-xs text-gray-400 italic line-clamp-1"
          title={significance}
        >
          {significance}
        </div>
      )}

      {/* Principles tags */}
      {principles.length > 0 && (
        <div className="mt-2 flex flex-wrap gap-1">
          {principles.slice(0, 3).map((principle) => (
            <span
              key={principle}
              className="px-1.5 py-0.5 bg-gray-800 rounded text-xs text-gray-300"
            >
              {principle}
            </span>
          ))}
          {principles.length > 3 && (
            <span className="px-1.5 py-0.5 text-xs text-gray-500">
              +{principles.length - 3}
            </span>
          )}
        </div>
      )}

      {/* Confidence bar */}
      <div className="mt-2 h-1 bg-gray-800 rounded-full overflow-hidden">
        <div
          className="h-full rounded-full transition-all"
          style={{
            width: `${confidence * 100}%`,
            backgroundColor: levelColor,
          }}
        />
      </div>

      {/* Strength label */}
      <div className="mt-1 flex items-center justify-between">
        <span
          className="text-xs capitalize"
          style={{ color: levelColor }}
        >
          {strength}
        </span>
        <span className="text-xs text-gray-500">
          {Math.round(confidence * 100)}%
        </span>
      </div>

      {/* Current indicator */}
      {is_current && (
        <motion.div
          className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-2 h-2 rounded-full"
          style={{ backgroundColor: levelColor }}
          animate={{ scale: [1, 1.3, 1] }}
          transition={{ repeat: Infinity, duration: 1.5 }}
        />
      )}

      {/* Output handle (to higher levels) */}
      <Handle
        type="source"
        position={Position.Top}
        className="w-3 h-3"
        style={{ backgroundColor: levelColor }}
      />
    </motion.div>
  );
}

// Memoize for performance
export const CrystalNode = memo(CrystalNodeComponent);

// Register node type
export const crystalNodeTypes = {
  crystal: CrystalNode,
};

export default CrystalNode;
