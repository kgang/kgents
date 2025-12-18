/**
 * TopologyNode3D - Universal 3D node primitive
 *
 * The core building block for both Brain (crystals) and Gestalt (plants).
 * Takes a theme and domain-specific data, renders a breathing, interactive node.
 *
 * Philosophy:
 *   "The node is a morphism: Data × Theme × State → Visual"
 *
 * This component unifies ~70% duplicated code between OrganicCrystal and OrganicNode.
 *
 * @see plans/3d-projection-consolidation.md
 * @see spec/protocols/projection.md
 */

import { useRef, useMemo, useState } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';

import type { ThemePalette, TierCalculator, SizeCalculator, Density } from './themes/types';
import { getTierColors } from './themes/types';
import { BREATHING, HOVER, SELECTION } from './animation';
import { SelectionRing } from './SelectionRing';
import { HoverRing } from './HoverRing';
import { NodeLabel3D } from './NodeLabel3D';
import { GrowthRings, generateRingSpecs } from './GrowthRings';

// =============================================================================
// Types
// =============================================================================

export interface TopologyNode3DProps<T = unknown> {
  /** Position in 3D space [x, y, z] */
  position: [number, number, number];

  /** Theme configuration (crystal, forest, etc.) */
  theme: ThemePalette;

  /** Domain-specific data (TopologyNode, CodebaseModule, etc.) */
  data: T;

  /** Function to calculate tier from data (returns tier name for theme lookup) */
  getTier: TierCalculator<T>;

  /** Function to calculate size from data and density */
  getSize: SizeCalculator<T>;

  /** Whether this node is selected */
  isSelected: boolean;

  /** Click handler */
  onClick: () => void;

  /** Whether to show the label */
  showLabel?: boolean;

  /** Label text (if not derived from data) */
  label?: string;

  /** Layout density */
  density?: Density;

  /** Animation speed multiplier (0 = frozen, 1 = normal) */
  animationSpeed?: number;

  /** Whether this is a hub/important node (shows extra indicator) */
  isHub?: boolean;

  /** Hub indicator color override */
  hubColor?: string;

  /** Optional growth rings (forest theme uses this) */
  showGrowthRings?: boolean;

  /** Number of growth rings (if showGrowthRings is true) */
  ringCount?: number;

  /** Geometry segments for sphere (lower = better performance) */
  segments?: number;

  /** Roughness for material (0 = shiny, 1 = matte) */
  roughness?: number;

  /** Metalness for material */
  metalness?: number;

  /** Touch target multiplier (for mobile accessibility, default 1.5) */
  touchTargetMultiplier?: number;

  /** Whether this is a touch device (enables larger hit area) */
  isTouchDevice?: boolean;
}

// =============================================================================
// Main Component
// =============================================================================

/**
 * TopologyNode3D - Generic 3D node that works with any theme.
 *
 * This is the unified primitive that replaces both OrganicCrystal and OrganicNode.
 * The visual identity comes from the theme; the behavior is universal.
 */
export function TopologyNode3D<T>({
  position,
  theme,
  data,
  getTier,
  getSize,
  isSelected,
  onClick,
  showLabel = true,
  label,
  density = 'comfortable',
  animationSpeed = 1,
  isHub = false,
  hubColor = '#FFA500',
  showGrowthRings = false,
  ringCount = 0,
  segments = 32,
  roughness = 0.4,
  metalness = 0.15,
  touchTargetMultiplier = 1.5,
  isTouchDevice = false,
}: TopologyNode3DProps<T>) {
  const groupRef = useRef<THREE.Group>(null);
  const meshRef = useRef<THREE.Mesh>(null);
  const [hovered, setHovered] = useState(false);

  // Animation phase for breathing (random start for organic variation)
  const phaseRef = useRef(Math.random() * Math.PI * 2);

  // Calculate visual properties from data
  const tier = useMemo(() => getTier(data), [getTier, data]);
  const size = useMemo(() => getSize(data, density), [getSize, data, density]);
  const tierColors = useMemo(() => getTierColors(theme, tier), [theme, tier]);

  // Growth rings (forest theme)
  const rings = useMemo(() => {
    if (!showGrowthRings || ringCount <= 0) return [];
    return generateRingSpecs(size, ringCount);
  }, [showGrowthRings, ringCount, size]);

  // Emissive intensity based on state
  const emissiveIntensity = useMemo(() => {
    if (isSelected) return SELECTION.emissiveBoost;
    if (isHub) return 1.5;
    if (hovered) return 1.2;
    return 0.8;
  }, [isSelected, isHub, hovered]);

  // Animation: breathing and interactive scale
  useFrame((_, delta) => {
    // Update breathing phase
    const breatheSpeed = BREATHING.speed + (Math.random() - 0.5) * BREATHING.variationFactor;
    phaseRef.current += delta * breatheSpeed * animationSpeed;

    // Apply breathing scale to mesh
    if (meshRef.current && animationSpeed > 0) {
      const breatheScale = 1 + Math.sin(phaseRef.current) * BREATHING.amplitude;
      meshRef.current.scale.setScalar(breatheScale);
    }

    // Apply interactive scale to group
    if (groupRef.current) {
      const targetScale = isSelected
        ? SELECTION.scaleMultiplier
        : hovered
          ? HOVER.scaleMultiplier
          : 1.0;
      groupRef.current.scale.lerp(
        new THREE.Vector3(targetScale, targetScale, targetScale),
        HOVER.lerpSpeed
      );
    }
  });

  // Derive label text
  const labelText = label ?? (data as { label?: string }).label ?? '';

  return (
    <group
      ref={groupRef}
      position={position}
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
      {/* Invisible touch target for mobile accessibility (larger hit area) */}
      {isTouchDevice && (
        <mesh visible={false}>
          <sphereGeometry args={[size * touchTargetMultiplier, 8, 8]} />
          <meshBasicMaterial transparent opacity={0} />
        </mesh>
      )}

      {/* Main sphere */}
      <mesh ref={meshRef} castShadow>
        <sphereGeometry args={[size, segments, segments]} />
        <meshStandardMaterial
          color={tierColors.core}
          emissive={tierColors.glow}
          emissiveIntensity={emissiveIntensity}
          roughness={roughness}
          metalness={metalness}
        />
      </mesh>

      {/* Inner glow for life effect (optional, used by forest theme) */}
      {showGrowthRings && (
        <mesh>
          <sphereGeometry args={[size * 0.7, 16, 16]} />
          <meshBasicMaterial
            color={tierColors.glow}
            transparent
            opacity={0.2 + Math.sin(phaseRef.current * 2) * BREATHING.glowAmplitude}
          />
        </mesh>
      )}

      {/* Growth rings (forest theme) */}
      {rings.length > 0 && (
        <GrowthRings rings={rings} color={tierColors.ring} opacityMultiplier={1} />
      )}

      {/* Hub indicator ring */}
      {isHub && (
        <mesh rotation={[Math.PI / 2, 0, 0]}>
          <ringGeometry args={[size * 1.3, size * 1.5, 32]} />
          <meshBasicMaterial color={hubColor} transparent opacity={0.6} side={THREE.DoubleSide} />
        </mesh>
      )}

      {/* Selection ring */}
      {isSelected && <SelectionRing size={size} color={theme.selectionColor} />}

      {/* Hover ring */}
      {hovered && !isSelected && <HoverRing size={size} color={tierColors.glow} />}

      {/* Label */}
      {showLabel && labelText && (
        <NodeLabel3D
          text={labelText}
          size={size}
          density={density}
          color={theme.labelColor}
          outlineColor={theme.labelOutlineColor}
        />
      )}
    </group>
  );
}

export default TopologyNode3D;
