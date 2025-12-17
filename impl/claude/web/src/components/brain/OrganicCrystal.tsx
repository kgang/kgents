/**
 * OrganicCrystal - Living Memory Crystal Visualization
 *
 * Transforms the basic spherical crystals into organic, living entities.
 * Each crystal is a memory node with:
 * - A central "core" (the memory essence)
 * - Glow effect based on resolution
 * - Interactive hover and selection states
 *
 * Philosophy:
 *   "Memories are not data points—they are living crystallizations of thought."
 *   The visualization emerges from rules, not placement.
 *
 * @see docs/creative/emergence-principles.md
 * @see docs/skills/3d-lighting-patterns.md
 */

import { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import { Text } from '@react-three/drei';
import * as THREE from 'three';
import type { TopologyNode } from '../../api/types';

// =============================================================================
// Constants - Crystal Palette (Emergent from Resolution/Heat)
// =============================================================================

/**
 * Crystal colors based on resolution state.
 *
 * Philosophy: Colors emerge from state, not configuration.
 * Expanded palette for richer variation while maintaining zen aesthetic.
 * Cool spectrum (cyan→purple→indigo→gray) with warm accent for hot memories.
 *
 * @see docs/creative/emergence-principles.md - Qualia Space
 */
const CRYSTAL_PALETTE = {
  // Core colors (center of crystal) - expanded for richer variation
  core: {
    vivid: '#0891B2',      // Deep cyan - very fresh (resolution > 0.85)
    fresh: '#06B6D4',      // Cyan - fresh (resolution > 0.7)
    recent: '#14B8A6',     // Teal - recent (resolution > 0.55)
    fading: '#8B5CF6',     // Purple - fading (resolution > 0.4)
    ancient: '#6366F1',    // Indigo - ancient (resolution > 0.25)
    ghost: '#475569',      // Slate - ghost (resolution <= 0.25)
    hot: '#F59E0B',        // Amber - frequently accessed (warm accent)
  },
  // Glow colors (emission)
  glow: {
    vivid: '#22D3EE',      // Bright cyan
    fresh: '#67E8F9',      // Light cyan
    recent: '#5EEAD4',     // Light teal
    fading: '#A78BFA',     // Bright purple
    ancient: '#818CF8',    // Bright indigo
    ghost: '#94A3B8',      // Light slate
    hot: '#FBBF24',        // Bright amber
  },
} as const;

/** Label configuration by density */
const LABEL_CONFIG = {
  compact: { fontSize: 0.12, offset: 0.25 },
  comfortable: { fontSize: 0.14, offset: 0.3 },
  spacious: { fontSize: 0.16, offset: 0.35 },
} as const;

type Density = 'compact' | 'comfortable' | 'spacious';

// =============================================================================
// Types
// =============================================================================

export interface OrganicCrystalProps {
  /** Crystal node data */
  node: TopologyNode;
  /** Whether this node is a hub */
  isHub: boolean;
  /** Whether this node is selected */
  isSelected: boolean;
  /** Click handler */
  onClick: () => void;
  /** Whether to show the label */
  showLabel?: boolean;
  /** Layout density */
  density?: Density;
  /** Animation speed multiplier (0 = frozen, 1 = normal) */
  animationSpeed?: number;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Get resolution tier from score for palette lookup.
 * Expanded to 6 tiers for richer color variation.
 */
function getResolutionTier(resolution: number, isHot: boolean): keyof typeof CRYSTAL_PALETTE.core {
  if (isHot) return 'hot';
  // Defensive: treat undefined/NaN as ghost
  const safeRes = typeof resolution === 'number' && !isNaN(resolution) ? resolution : 0;
  if (safeRes > 0.85) return 'vivid';
  if (safeRes > 0.7) return 'fresh';
  if (safeRes > 0.55) return 'recent';
  if (safeRes > 0.4) return 'fading';
  if (safeRes > 0.25) return 'ancient';
  return 'ghost';
}

/**
 * Calculate crystal size based on metrics.
 */
function calculateCrystalSize(
  accessCount: number,
  resolution: number,
  isHub: boolean,
  density: Density
): number {
  // Base sizes - smaller for more elegant appearance
  const baseSize = density === 'compact' ? 0.2 : density === 'comfortable' ? 0.25 : 0.3;

  // Defensive: ensure valid numbers (prevent NaN)
  const safeAccessCount = typeof accessCount === 'number' && !isNaN(accessCount) ? accessCount : 1;
  const safeResolution = typeof resolution === 'number' && !isNaN(resolution) ? resolution : 0.5;

  // Logarithmic scale for access count (subtle variation)
  const accessFactor = Math.log10(Math.max(safeAccessCount, 1) + 1) / 3;

  // Resolution affects fullness
  const resolutionFactor = 0.8 + safeResolution * 0.2;

  // Hub bonus - more prominent for navigation
  const hubBonus = isHub ? 1.5 : 1.0;

  return baseSize * (1 + accessFactor) * resolutionFactor * hubBonus;
}

// =============================================================================
// Sub-Components
// =============================================================================

/**
 * Crystal label with organic styling.
 */
function CrystalLabel({
  text,
  size,
  density,
  resolution,
}: {
  text: string;
  size: number;
  density: Density;
  resolution: number;
}) {
  const config = LABEL_CONFIG[density];
  const displayText = text.length > 20 ? `${text.slice(0, 18)}...` : text;
  const opacity = 0.5 + resolution * 0.5;

  return (
    <Text
      position={[0, size + config.offset, 0]}
      fontSize={config.fontSize}
      color="#ffffff"
      anchorX="center"
      anchorY="bottom"
      outlineWidth={0.015}
      outlineColor="#0d1117"
      outlineOpacity={0.9 * opacity}
      fillOpacity={opacity}
    >
      {displayText}
    </Text>
  );
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * OrganicCrystal - A living memory crystal in the holographic brain.
 */
export function OrganicCrystal({
  node,
  isHub,
  isSelected,
  onClick,
  showLabel = true,
  density = 'comfortable',
  animationSpeed = 1,
}: OrganicCrystalProps) {
  const groupRef = useRef<THREE.Group>(null);
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Animation phase for breathing
  const phaseRef = useRef(Math.random() * Math.PI * 2);

  // Calculate visual properties
  const resolutionTier = getResolutionTier(node.resolution, node.is_hot);
  const size = useMemo(
    () => calculateCrystalSize(node.access_count, node.resolution, isHub, density),
    [node.access_count, node.resolution, isHub, density]
  );

  // Colors from palette
  const coreColor = useMemo(() => CRYSTAL_PALETTE.core[resolutionTier], [resolutionTier]);
  const glowColor = useMemo(() => CRYSTAL_PALETTE.glow[resolutionTier], [resolutionTier]);

  // Emissive intensity based on state
  const emissiveIntensity = isSelected ? 2.0 : isHub ? 1.5 : hovered ? 1.2 : 0.8;

  // Animation: breathing and scale
  useFrame((_, delta) => {
    // Update breathing phase
    const breatheSpeed = 1.2 + (node.resolution - 0.5) * 0.4;
    phaseRef.current += delta * breatheSpeed * animationSpeed;

    // Breathing scale effect
    if (meshRef.current) {
      const breatheScale = 1 + Math.sin(phaseRef.current) * 0.03;
      meshRef.current.scale.setScalar(breatheScale);
    }

    // Interactive scale for group
    if (groupRef.current) {
      const targetScale = isSelected ? 1.25 : hovered ? 1.12 : 1.0;
      groupRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        0.1
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
      {/* Main crystal sphere */}
      <mesh ref={meshRef} castShadow>
        <sphereGeometry args={[size, 32, 32]} />
        <meshStandardMaterial
          color={coreColor}
          emissive={glowColor}
          emissiveIntensity={emissiveIntensity}
          roughness={0.3}
          metalness={0.2}
        />
      </mesh>

      {/* Hub indicator ring */}
      {isHub && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.3, size * 1.5, 32]} />
          <meshBasicMaterial color="#FFA500" transparent opacity={0.6} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Selection ring */}
      {isSelected && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.4, size * 1.6, 32]} />
          <meshBasicMaterial color="#00FFFF" transparent opacity={0.7} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Label */}
      {showLabel && (
        <CrystalLabel
          text={node.label}
          size={size}
          density={density}
          resolution={node.resolution}
        />
      )}
    </group>
  );
}

export default OrganicCrystal;
