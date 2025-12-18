/**
 * NodeLabel3D - Reusable 3D text label for nodes
 *
 * Renders a text label above a node with configurable styling.
 * Uses drei's Text component for crisp rendering.
 *
 * @see plans/3d-projection-consolidation.md
 */

import { Text } from '@react-three/drei';
import { LABEL_CONFIGS, type Density } from './themes/types';

export interface NodeLabel3DProps {
  /** Label text to display */
  text: string;
  /** Base node size (label positions relative to this) */
  size: number;
  /** Layout density (affects font size and offset) */
  density: Density;
  /** Text color (default: white) */
  color?: string;
  /** Outline color for readability */
  outlineColor?: string;
  /** Opacity (0-1) */
  opacity?: number;
  /** Maximum character length before truncation */
  maxLength?: number;
  /** Truncation suffix */
  truncationSuffix?: string;
}

/**
 * 3D text label positioned above a node.
 * Automatically truncates long labels and adjusts for density.
 */
export function NodeLabel3D({
  text,
  size,
  density,
  color = '#ffffff',
  outlineColor = '#0d1117',
  opacity = 1,
  maxLength = 20,
  truncationSuffix = '...',
}: NodeLabel3DProps) {
  const config = LABEL_CONFIGS[density];

  // Truncate long labels
  const displayText =
    text.length > maxLength ? `${text.slice(0, maxLength - truncationSuffix.length)}${truncationSuffix}` : text;

  return (
    <Text
      position={[0, size + config.offset, 0]}
      fontSize={config.fontSize}
      color={color}
      anchorX="center"
      anchorY="bottom"
      outlineWidth={0.015}
      outlineColor={outlineColor}
      outlineOpacity={0.9 * opacity}
      fillOpacity={opacity}
    >
      {displayText}
    </Text>
  );
}

export default NodeLabel3D;
