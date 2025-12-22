/**
 * ContextNode - Custom react-flow node for trail visualization.
 *
 * "The aesthetic is the structure perceiving itself. Beauty is not revealed—it breathes."
 *
 * Visual States:
 * - Default: Warm earth background with subtle breathing
 * - Current: Lantern glow + enhanced breathing
 * - Selected: Copper border highlight
 *
 * Living Earth Aesthetic (Crown Jewels Genesis):
 * - Breathing: 3-4s subtle pulse on all nodes
 * - Growing: Seed-to-full entrance animation
 * - Organic colors: Bark, Wood, Copper, Lantern
 *
 * @see spec/protocols/trail-protocol.md Section 8
 * @see creative/crown-jewels-genesis-moodboard.md
 */

import { memo, useState } from 'react';
import { Handle, Position, type NodeProps } from 'reactflow';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LIVING_EARTH,
  BACKGROUNDS,
  BREATHING,
  GROWING,
  STATUS_GLYPHS,
  glowShadow,
  getEdgeColor as getLivingEdgeColor,
} from './living-earth';

/**
 * Zoom levels for detail rendering.
 * Visual Trail Graph Session 3: Zoom-Dependent Detail
 */
export type ZoomLevel = 'far' | 'medium' | 'close';

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
  /** Parent step index for branching (null = root) */
  parent_index?: number | null;
  /** Edge type that led here */
  edge_type: string | null;
  /** LLM reasoning */
  reasoning: string | null;
  /** Whether this is the current position */
  is_current: boolean;
  /** Zoom level for detail rendering (Session 3) */
  zoom_level?: ZoomLevel;
}

/**
 * Custom node component for trail graph.
 *
 * Living Earth Aesthetic: organic, breathing, warm
 * "Everything Breathes" - subtle pulse on all nodes
 *
 * Zoom-dependent rendering (Session 3):
 * - far: holon name only (minimal, breathing glyph)
 * - medium: holon + path (default)
 * - close: holon + path + edge + reasoning (full detail)
 *
 * Polish Wave 4:
 * - Reasoning tooltip on hover (far/medium zoom)
 */
function ContextNodeComponent({ data, selected }: NodeProps<ContextNodeData>) {
  const { path, holon, step_index, edge_type, reasoning, is_current, zoom_level = 'medium' } = data;

  // Polish Wave 4: Tooltip state
  const [showTooltip, setShowTooltip] = useState(false);
  const hasReasoningTooltip = reasoning && zoom_level !== 'close';

  // Living Earth: Organic edge colors
  const edgeColor = getLivingEdgeColor(edge_type);

  // Status glyph for compact display
  const statusGlyph = is_current
    ? STATUS_GLYPHS.current
    : step_index === 0
      ? STATUS_GLYPHS.root
      : STATUS_GLYPHS.visited;

  return (
    <motion.div
      // Living Earth: Growing entrance (seed to full)
      initial={{
        scale: GROWING.initialScale,
        opacity: 0,
      }}
      animate={{
        // Base scale with breathing overlay
        scale: is_current ? 1.05 : 1,
        opacity: 1,
      }}
      whileHover={{
        scale: is_current ? 1.08 : 1.03,
        boxShadow: glowShadow(edgeColor, 'medium'),
        transition: { duration: 0.15 },
      }}
      transition={{
        // Bouncy growing entrance
        duration: GROWING.duration,
        ease: GROWING.ease,
      }}
      onMouseEnter={() => hasReasoningTooltip && setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
      className={`
        px-4 py-3 rounded-lg min-w-[180px] max-w-[280px] cursor-pointer
        ${is_current ? 'ring-2' : ''}
        ${selected ? 'ring-2' : ''}
        transition-colors relative
      `}
      style={
        {
          // Living Earth: Warm bark background
          backgroundColor: BACKGROUNDS.surface,
          borderWidth: 1,
          borderStyle: 'solid',
          borderColor: is_current
            ? LIVING_EARTH.lantern
            : selected
              ? LIVING_EARTH.copper
              : LIVING_EARTH.wood,
          // Ring colors
          '--tw-ring-color': is_current ? LIVING_EARTH.lantern : LIVING_EARTH.copper,
          boxShadow: is_current
            ? `${glowShadow(LIVING_EARTH.lantern, 'strong')}, 0 4px 12px rgba(0,0,0,0.4)`
            : selected
              ? glowShadow(LIVING_EARTH.copper, 'medium')
              : `0 2px 8px rgba(0,0,0,0.3)`,
        } as React.CSSProperties
      }
    >
      {/* Input handle - Living Earth clay */}
      <Handle
        type="target"
        position={Position.Top}
        className="w-2 h-2"
        style={{ backgroundColor: LIVING_EARTH.clay }}
      />

      {/* Step number badge with status glyph - Living Earth */}
      <div
        className="absolute -top-2 -right-2 w-6 h-6 rounded-full flex items-center justify-center text-xs font-medium"
        style={{
          backgroundColor: is_current ? LIVING_EARTH.copper : LIVING_EARTH.wood,
          borderWidth: 1,
          borderColor: is_current ? LIVING_EARTH.lantern : LIVING_EARTH.clay,
          color: LIVING_EARTH.lantern,
        }}
      >
        {step_index + 1}
      </div>

      {/* Status glyph - far zoom shows glyph instead of text */}
      {zoom_level === 'far' && (
        <div className="flex items-center gap-2">
          <span style={{ color: edgeColor }}>{statusGlyph}</span>
          <span className="font-medium truncate" style={{ color: LIVING_EARTH.lantern }}>
            {holon}
          </span>
        </div>
      )}

      {/* Holon name - medium/close zoom */}
      {zoom_level !== 'far' && (
        <div className="font-medium truncate" style={{ color: LIVING_EARTH.lantern }}>
          {holon}
        </div>
      )}

      {/* Full path - medium and close zoom only */}
      {zoom_level !== 'far' && (
        <div className="text-xs truncate mt-1" style={{ color: LIVING_EARTH.clay }} title={path}>
          {path}
        </div>
      )}

      {/* Edge type badge - close zoom only (Living Earth colors) */}
      {zoom_level === 'close' && edge_type && (
        <div
          className="inline-flex items-center gap-1 mt-2 px-2 py-0.5 rounded text-xs"
          style={{
            backgroundColor: `${edgeColor}25`,
            color: edgeColor,
            borderWidth: 1,
            borderColor: `${edgeColor}40`,
          }}
        >
          <span style={{ opacity: 0.7 }}>via</span>
          <span className="font-medium">{edge_type}</span>
        </div>
      )}

      {/* Reasoning preview - close zoom only (warm styling) */}
      {zoom_level === 'close' && reasoning && (
        <div
          className="mt-2 text-xs italic line-clamp-2 pl-2"
          style={{
            color: LIVING_EARTH.sand,
            borderLeftWidth: 2,
            borderLeftColor: LIVING_EARTH.wood,
          }}
          title={reasoning}
        >
          "{reasoning.slice(0, 80)}
          {reasoning.length > 80 ? '...' : ''}"
        </div>
      )}

      {/* Breathing indicator - all nodes breathe (subtle, meditative) */}
      <motion.div
        className="absolute inset-0 rounded-lg pointer-events-none"
        animate={{
          opacity: [0, BREATHING.amplitude.opacity, 0],
        }}
        transition={{
          duration: BREATHING.duration,
          repeat: Infinity,
          ease: BREATHING.ease,
        }}
        style={{
          backgroundColor: is_current ? LIVING_EARTH.lantern : LIVING_EARTH.honey,
        }}
      />

      {/* Current position indicator - Ghibli lantern glow */}
      {is_current && (
        <motion.div
          className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-3 h-3 rounded-full"
          animate={{
            scale: [1, 1.4, 1],
            opacity: [1, 0.6, 1],
          }}
          transition={{
            duration: BREATHING.duration / 2,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          style={{
            backgroundColor: LIVING_EARTH.lantern,
            boxShadow: glowShadow(LIVING_EARTH.lantern, 'strong'),
          }}
        />
      )}

      {/* Polish Wave 4: Reasoning tooltip on hover (Living Earth styling) */}
      <AnimatePresence>
        {showTooltip && reasoning && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 4, scale: 0.98 }}
            transition={{
              type: 'spring',
              stiffness: 400,
              damping: 30,
            }}
            className="absolute left-1/2 -translate-x-1/2 bottom-full mb-3 z-50"
            style={{ pointerEvents: 'none' }}
          >
            <div
              className="px-3 py-2 rounded-lg shadow-xl max-w-[280px]"
              style={{
                backgroundColor: LIVING_EARTH.soil,
                borderWidth: 1,
                borderColor: LIVING_EARTH.wood,
                boxShadow: `0 4px 20px rgba(0, 0, 0, 0.6), ${glowShadow(LIVING_EARTH.honey, 'subtle')}`,
              }}
            >
              {/* Reasoning icon */}
              <div className="flex items-start gap-2">
                <span className="text-sm mt-0.5" style={{ color: LIVING_EARTH.amber }}>
                  💭
                </span>
                <p className="text-sm italic leading-relaxed" style={{ color: LIVING_EARTH.sand }}>
                  {reasoning.length > 120 ? `${reasoning.slice(0, 120)}...` : reasoning}
                </p>
              </div>
              {/* Arrow */}
              <div className="absolute left-1/2 -translate-x-1/2 bottom-0 translate-y-full">
                <div
                  className="w-0 h-0 border-l-8 border-r-8 border-t-8 border-l-transparent border-r-transparent"
                  style={{ borderTopColor: LIVING_EARTH.wood }}
                />
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Output handle - Living Earth clay */}
      <Handle
        type="source"
        position={Position.Bottom}
        className="w-2 h-2"
        style={{ backgroundColor: LIVING_EARTH.clay }}
      />
    </motion.div>
  );
}

/**
 * Get edge color based on edge type.
 * Re-exported from living-earth for backwards compatibility.
 */
export { getEdgeColor } from './living-earth';

// Memoize for performance
export const ContextNode = memo(ContextNodeComponent);

// Register node type
export const nodeTypes = {
  context: ContextNode,
};

export default ContextNode;
