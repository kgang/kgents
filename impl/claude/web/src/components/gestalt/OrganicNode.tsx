/**
 * OrganicNode - Plant-like Module Visualization
 *
 * Transforms the spherical nodes into organic, plant-like entities.
 * Each module is represented as a growing organism with:
 * - A central "bulb" (the module core)
 * - Growth rings showing health/size
 * - Subtle breathing animation (alive, not static)
 * - Emergent tendrils for connections
 *
 * Philosophy:
 *   "We do not design the flower—we design the soil and the season."
 *   The visualization emerges from rules, not placement.
 *
 * @see docs/creative/emergence-principles.md
 * @see plans/_continuations/gestalt-sprint3.md
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import type { CodebaseModule } from '../../api/types';
import type { Density } from './types';

// =============================================================================
// Constants - Forest Palette
// =============================================================================

/** Growth ring colors based on health - forest palette */
const FOREST_PALETTE = {
  // Core colors (center of plant)
  core: {
    healthy: '#22C55E',   // Rich green
    good: '#84CC16',      // Lime green
    fair: '#FACC15',      // Golden yellow
    poor: '#F97316',      // Orange
    critical: '#EF4444',  // Red
  },
  // Growth ring colors (outer layers)
  ring: {
    healthy: '#166534',   // Deep forest green
    good: '#365314',      // Dark lime
    fair: '#854D0E',      // Bark brown
    poor: '#9A3412',      // Rust
    critical: '#7F1D1D',  // Dark red
  },
  // Ambient glow
  glow: {
    healthy: '#4ADE80',   // Bright green
    good: '#A3E635',      // Bright lime
    fair: '#FDE047',      // Bright yellow
    poor: '#FB923C',      // Bright orange
    critical: '#FCA5A5',  // Light red
  },
} as const;

/** Label configuration by density */
const LABEL_CONFIG = {
  compact: { fontSize: 0.12, offset: 0.2 },
  comfortable: { fontSize: 0.16, offset: 0.25 },
  spacious: { fontSize: 0.20, offset: 0.3 },
} as const;

// =============================================================================
// Types
// =============================================================================

export interface OrganicNodeProps {
  /** Module data */
  node: CodebaseModule;
  /** Whether this node is selected */
  isSelected: boolean;
  /** Click handler */
  onClick: () => void;
  /** Whether to show the label */
  showLabel: boolean;
  /** Layout density */
  density: Density;
  /** Whether tooltips are enabled */
  enableTooltip?: boolean;
  /** Animation speed multiplier (0 = frozen, 1 = normal) */
  animationSpeed?: number;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get health tier from score for palette lookup
 */
function getHealthTier(score: number): keyof typeof FOREST_PALETTE.core {
  if (score >= 0.9) return 'healthy';
  if (score >= 0.7) return 'good';
  if (score >= 0.5) return 'fair';
  if (score >= 0.3) return 'poor';
  return 'critical';
}

/**
 * Calculate organic size based on module metrics
 * Uses logarithmic scaling for natural distribution
 */
function calculateOrganicSize(linesOfCode: number, healthScore: number, density: Density): number {
  const baseSize = density === 'compact' ? 0.15 : density === 'comfortable' ? 0.2 : 0.25;
  // Logarithmic scale for lines of code (prevents giant nodes)
  const locFactor = Math.log10(Math.max(linesOfCode, 10)) / 5;
  // Health affects fullness (healthier = fuller)
  const healthFactor = 0.7 + healthScore * 0.3;
  return baseSize * (1 + locFactor) * healthFactor;
}

/**
 * Generate growth ring geometry
 * Creates concentric rings like tree rings
 */
function generateGrowthRings(baseSize: number, ringCount: number): Array<{ inner: number; outer: number; opacity: number }> {
  const rings: Array<{ inner: number; outer: number; opacity: number }> = [];
  for (let i = 0; i < ringCount; i++) {
    const innerRadius = baseSize * (1 + i * 0.15);
    const outerRadius = innerRadius + baseSize * 0.1;
    // Outer rings are more transparent
    const opacity = 0.4 - i * 0.08;
    rings.push({ inner: innerRadius, outer: outerRadius, opacity: Math.max(opacity, 0.1) });
  }
  return rings;
}

// =============================================================================
// Sub-Components
// =============================================================================

/**
 * The central "bulb" of the plant
 */
function CoreBulb({
  size,
  color,
  glowColor,
  isSelected,
  hovered,
  breathePhase,
}: {
  size: number;
  color: string;
  glowColor: string;
  isSelected: boolean;
  hovered: boolean;
  breathePhase: number;
}) {
  // Subtle breathing scale
  const breatheScale = 1 + Math.sin(breathePhase) * 0.03;

  return (
    <group scale={[breatheScale, breatheScale, breatheScale]}>
      {/* Main bulb */}
      <mesh castShadow>
        <sphereGeometry args={[size, 24, 24]} />
        <meshStandardMaterial
          color={color}
          roughness={0.6}
          metalness={0.1}
          emissive={isSelected || hovered ? glowColor : undefined}
          emissiveIntensity={isSelected ? 1.5 : hovered ? 0.4 : 0}
        />
      </mesh>

      {/* Inner glow (life light) */}
      <mesh>
        <sphereGeometry args={[size * 0.7, 16, 16]} />
        <meshBasicMaterial
          color={glowColor}
          transparent
          opacity={0.2 + Math.sin(breathePhase * 2) * 0.1}
        />
      </mesh>
    </group>
  );
}

/**
 * Growth rings - tree ring aesthetic
 */
function GrowthRings({
  rings,
  color,
  healthScore,
}: {
  rings: Array<{ inner: number; outer: number; opacity: number }>;
  color: string;
  healthScore: number;
}) {
  return (
    <group rotation={[Math.PI / 2, 0, 0]}>
      {rings.map((ring, i) => (
        <mesh key={i}>
          <ringGeometry args={[ring.inner, ring.outer, 32]} />
          <meshBasicMaterial
            color={color}
            transparent
            opacity={ring.opacity * healthScore}
            side={THREE.DoubleSide}
          />
        </mesh>
      ))}
    </group>
  );
}

/**
 * Selection indicator - gentle petal ring
 */
function SelectionRing({ size }: { size: number }) {
  return (
    <mesh rotation={[Math.PI / 2, 0, 0]}>
      <ringGeometry args={[size * 1.4, size * 1.6, 32]} />
      <meshBasicMaterial
        color="#ffffff"
        transparent
        opacity={0.6}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

/**
 * Hover indicator - soft petal ring
 */
function HoverRing({ size, color }: { size: number; color: string }) {
  return (
    <mesh rotation={[Math.PI / 2, 0, 0]}>
      <ringGeometry args={[size * 1.2, size * 1.35, 32]} />
      <meshBasicMaterial
        color={color}
        transparent
        opacity={0.35}
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

/**
 * Module label with organic styling
 */
function ModuleLabel({
  text,
  size,
  density,
}: {
  text: string;
  size: number;
  density: Density;
}) {
  const config = LABEL_CONFIG[density];

  return (
    <Text
      position={[0, size + config.offset, 0]}
      fontSize={config.fontSize}
      color="#ffffff"
      anchorX="center"
      anchorY="bottom"
      outlineWidth={0.015}
      outlineColor="#1a3a1a" // Dark forest green outline
      outlineOpacity={0.9}
    >
      {text}
    </Text>
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function OrganicNode({
  node,
  isSelected,
  onClick,
  showLabel,
  density,
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  enableTooltip: _enableTooltip = true,
  animationSpeed = 1,
}: OrganicNodeProps) {
  const groupRef = useRef<THREE.Group>(null);
  const [hovered, setHovered] = React.useState(false);

  // Animation phase (for breathing)
  const phaseRef = useRef(Math.random() * Math.PI * 2); // Random start phase

  // Update animation
  useFrame((_, delta) => {
    phaseRef.current += delta * 1.5 * animationSpeed;
  });

  // Calculate visual properties
  const healthTier = getHealthTier(node.health_score);
  const size = useMemo(
    () => calculateOrganicSize(node.lines_of_code, node.health_score, density),
    [node.lines_of_code, node.health_score, density]
  );

  // Colors from palette
  const coreColor = useMemo(() => FOREST_PALETTE.core[healthTier], [healthTier]);
  const ringColor = useMemo(() => FOREST_PALETTE.ring[healthTier], [healthTier]);
  const glowColor = useMemo(() => FOREST_PALETTE.glow[healthTier], [healthTier]);

  // Growth rings based on module size (more LOC = more rings)
  const rings = useMemo(() => {
    const ringCount = Math.min(Math.floor(Math.log10(node.lines_of_code + 1)), 4);
    return generateGrowthRings(size, ringCount);
  }, [size, node.lines_of_code]);

  // Interactive scale
  const targetScale = isSelected ? 1.3 : hovered ? 1.15 : 1.0;

  // Smooth scale transition
  useFrame(() => {
    if (groupRef.current) {
      groupRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.12
      );
    }
  });

  return (
    <group
      ref={groupRef}
      position={[node.x, node.y, node.z]}
      onClick={(e) => {
        e.stopPropagation();
        onClick();
      }}
      onPointerOver={(e) => {
        e.stopPropagation();
        setHovered(true);
        document.body.style.cursor = 'pointer';
      }}
      onPointerOut={() => {
        setHovered(false);
        document.body.style.cursor = 'auto';
      }}
    >
      {/* Core bulb (the plant center) */}
      <CoreBulb
        size={size}
        color={coreColor}
        glowColor={glowColor}
        isSelected={isSelected}
        hovered={hovered}
        breathePhase={phaseRef.current}
      />

      {/* Growth rings */}
      <GrowthRings
        rings={rings}
        color={ringColor}
        healthScore={node.health_score}
      />

      {/* Selection indicator */}
      {isSelected && <SelectionRing size={size} />}

      {/* Hover indicator */}
      {hovered && !isSelected && <HoverRing size={size} color={glowColor} />}

      {/* Label */}
      {showLabel && (
        <ModuleLabel
          text={node.label}
          size={size}
          density={density}
        />
      )}
    </group>
  );
}

// Import React for useState
import React from 'react';

export default OrganicNode;
