/**
 * useLOD - Level of Detail system for 3D Projection Primitives
 *
 * Provides automatic quality scaling based on:
 * 1. Distance from camera
 * 2. Total node count (global budget)
 * 3. Frustum visibility (culling off-screen nodes)
 *
 * Philosophy:
 *   "60fps is a constitutional right. LOD is how we guarantee it."
 *
 * @see plans/3d-projection-consolidation.md
 */

import { useRef, useMemo, useCallback, useState } from 'react';
import { useThree, useFrame } from '@react-three/fiber';
import * as THREE from 'three';

// =============================================================================
// Types
// =============================================================================

/**
 * LOD level - determines rendering complexity.
 */
export type LODLevel = 'full' | 'reduced' | 'minimal' | 'culled';

/**
 * LOD configuration for a single node.
 */
export interface NodeLOD {
  /** Current LOD level */
  level: LODLevel;
  /** Whether node is in view frustum */
  visible: boolean;
  /** Distance from camera */
  distance: number;
  /** Geometry segments to use */
  segments: number;
  /** Whether to show label */
  showLabel: boolean;
  /** Whether to enable animation */
  enableAnimation: boolean;
  /** Whether to show flow particles on connected edges */
  showFlowParticles: boolean;
}

/**
 * LOD settings for different thresholds.
 */
export interface LODSettings {
  /** Distance thresholds for LOD transitions */
  distances: {
    /** Below this = full detail */
    full: number;
    /** Below this = reduced detail */
    reduced: number;
    /** Below this = minimal detail, above = culled */
    minimal: number;
  };
  /** Geometry segments per LOD level */
  segments: {
    full: number;
    reduced: number;
    minimal: number;
  };
  /** Total node count thresholds for global budget adjustments */
  budgetThresholds: {
    /** Above this count, reduce default LOD */
    medium: number;
    /** Above this count, aggressive LOD */
    large: number;
  };
}

/**
 * Options for useLOD hook.
 */
export interface UseLODOptions {
  /** Override default LOD settings */
  settings?: Partial<LODSettings>;
  /** Disable frustum culling */
  disableFrustumCulling?: boolean;
  /** Update interval in ms (default: 100 - 10fps LOD updates) */
  updateInterval?: number;
}

// =============================================================================
// Default Settings
// =============================================================================

const DEFAULT_LOD_SETTINGS: LODSettings = {
  distances: {
    full: 5,      // Within 5 units = full detail
    reduced: 15,  // 5-15 units = reduced detail
    minimal: 30,  // 15-30 units = minimal detail, >30 = culled
  },
  segments: {
    full: 32,
    reduced: 16,
    minimal: 8,
  },
  budgetThresholds: {
    medium: 50,   // 50+ nodes = medium budget mode
    large: 100,   // 100+ nodes = aggressive LOD
  },
};

// =============================================================================
// LOD Calculation
// =============================================================================

/**
 * Calculate LOD level based on distance and budget.
 */
function calculateLODLevel(
  distance: number,
  settings: LODSettings,
  budgetMultiplier: number
): LODLevel {
  // Budget multiplier shrinks effective distances (lower = more aggressive LOD)
  const fullDist = settings.distances.full * budgetMultiplier;
  const reducedDist = settings.distances.reduced * budgetMultiplier;
  const minimalDist = settings.distances.minimal * budgetMultiplier;

  if (distance <= fullDist) return 'full';
  if (distance <= reducedDist) return 'reduced';
  if (distance <= minimalDist) return 'minimal';
  return 'culled';
}

/**
 * Get segments count for LOD level.
 */
function getSegmentsForLevel(level: LODLevel, settings: LODSettings): number {
  switch (level) {
    case 'full':
      return settings.segments.full;
    case 'reduced':
      return settings.segments.reduced;
    case 'minimal':
      return settings.segments.minimal;
    case 'culled':
      return 0;
  }
}

// =============================================================================
// Main Hook
// =============================================================================

/**
 * Hook to calculate LOD for a collection of node positions.
 *
 * Usage:
 * ```tsx
 * const { getLOD, updateLOD } = useLOD(nodeCount, options);
 *
 * // In render:
 * {nodes.map((node, i) => {
 *   const lod = getLOD(node.position);
 *   if (lod.level === 'culled') return null;
 *   return <TopologyNode3D segments={lod.segments} ... />;
 * })}
 * ```
 */
export function useLOD(nodeCount: number, options: UseLODOptions = {}) {
  const {
    settings: settingsOverride,
    disableFrustumCulling = false,
    updateInterval = 100,
  } = options;

  const { camera } = useThree();
  const frustumRef = useRef(new THREE.Frustum());
  const matrixRef = useRef(new THREE.Matrix4());
  const lastUpdateRef = useRef(0);
  const [frameCount, setFrameCount] = useState(0);

  // Merge settings with defaults
  const settings = useMemo<LODSettings>(
    () => ({
      distances: { ...DEFAULT_LOD_SETTINGS.distances, ...settingsOverride?.distances },
      segments: { ...DEFAULT_LOD_SETTINGS.segments, ...settingsOverride?.segments },
      budgetThresholds: { ...DEFAULT_LOD_SETTINGS.budgetThresholds, ...settingsOverride?.budgetThresholds },
    }),
    [settingsOverride]
  );

  // Calculate budget multiplier based on total node count
  const budgetMultiplier = useMemo(() => {
    if (nodeCount >= settings.budgetThresholds.large) {
      return 0.5; // Aggressive: halve all distances
    }
    if (nodeCount >= settings.budgetThresholds.medium) {
      return 0.75; // Medium: reduce by 25%
    }
    return 1.0; // Normal
  }, [nodeCount, settings.budgetThresholds]);

  // Update frustum periodically (not every frame)
  useFrame(({ clock }) => {
    const now = clock.getElapsedTime() * 1000;
    if (now - lastUpdateRef.current >= updateInterval) {
      lastUpdateRef.current = now;
      setFrameCount((c) => c + 1);

      // Update frustum matrix
      matrixRef.current.multiplyMatrices(
        camera.projectionMatrix,
        camera.matrixWorldInverse
      );
      frustumRef.current.setFromProjectionMatrix(matrixRef.current);
    }
  });

  // LOD calculation function
  const getLOD = useCallback(
    (position: [number, number, number]): NodeLOD => {
      const posVec = new THREE.Vector3(...position);

      // Check frustum visibility
      let visible = true;
      if (!disableFrustumCulling) {
        // Use a sphere for frustum check (node has radius)
        const boundingSphere = new THREE.Sphere(posVec, 1.5);
        visible = frustumRef.current.intersectsSphere(boundingSphere);
      }

      // If not visible, return culled state
      if (!visible) {
        return {
          level: 'culled',
          visible: false,
          distance: Infinity,
          segments: 0,
          showLabel: false,
          enableAnimation: false,
          showFlowParticles: false,
        };
      }

      // Calculate distance from camera
      const distance = posVec.distanceTo(camera.position);

      // Calculate LOD level
      const level = calculateLODLevel(distance, settings, budgetMultiplier);
      const segments = getSegmentsForLevel(level, settings);

      return {
        level,
        visible: true,
        distance,
        segments,
        showLabel: level === 'full' || level === 'reduced',
        enableAnimation: level === 'full' || level === 'reduced',
        showFlowParticles: level === 'full',
      };
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [camera, settings, budgetMultiplier, disableFrustumCulling, frameCount]
  );

  // Batch LOD calculation for many nodes
  const getLODBatch = useCallback(
    (positions: [number, number, number][]): NodeLOD[] => {
      return positions.map(getLOD);
    },
    [getLOD]
  );

  // Statistics for debugging
  const getStats = useCallback(
    (lods: NodeLOD[]) => {
      const stats = {
        full: 0,
        reduced: 0,
        minimal: 0,
        culled: 0,
        total: lods.length,
        budgetMultiplier,
      };
      for (const lod of lods) {
        stats[lod.level]++;
      }
      return stats;
    },
    [budgetMultiplier]
  );

  return {
    /** Get LOD for a single position */
    getLOD,
    /** Get LOD for multiple positions at once */
    getLODBatch,
    /** Get statistics from LOD array */
    getStats,
    /** Current budget multiplier (for debugging) */
    budgetMultiplier,
    /** Current settings */
    settings,
  };
}

// =============================================================================
// LOD-Aware Node Component Wrapper
// =============================================================================

export interface LODAwareNodeProps {
  /** Node position */
  position: [number, number, number];
  /** LOD data from useLOD hook */
  lod: NodeLOD;
  /** Children to render (receives LOD-adjusted props) */
  children: (lodProps: {
    segments: number;
    showLabel: boolean;
    animationSpeed: number;
  }) => React.ReactNode;
}

/**
 * Wrapper component that applies LOD adjustments.
 *
 * Usage:
 * ```tsx
 * <LODAwareNode position={pos} lod={lod}>
 *   {({ segments, showLabel, animationSpeed }) => (
 *     <TopologyNode3D
 *       segments={segments}
 *       showLabel={showLabel}
 *       animationSpeed={animationSpeed}
 *       ...
 *     />
 *   )}
 * </LODAwareNode>
 * ```
 */
export function LODAwareNode({ lod, children }: LODAwareNodeProps) {
  // Don't render culled nodes
  if (lod.level === 'culled') {
    return null;
  }

  return (
    <>
      {children({
        segments: lod.segments,
        showLabel: lod.showLabel,
        animationSpeed: lod.enableAnimation ? 1 : 0,
      })}
    </>
  );
}

// =============================================================================
// Hook for Edge LOD
// =============================================================================

/**
 * Get edge LOD based on connected node LODs.
 * Edge inherits the lower LOD of its two connected nodes.
 */
export function getEdgeLOD(sourceLOD: NodeLOD, targetLOD: NodeLOD): {
  visible: boolean;
  showFlowParticles: boolean;
  curveSegments: number;
} {
  // If either node is culled, cull the edge
  if (sourceLOD.level === 'culled' || targetLOD.level === 'culled') {
    return { visible: false, showFlowParticles: false, curveSegments: 0 };
  }

  // Use the worse LOD level for the edge
  const worseLevel = ((): LODLevel => {
    if (sourceLOD.level === 'minimal' || targetLOD.level === 'minimal') return 'minimal';
    if (sourceLOD.level === 'reduced' || targetLOD.level === 'reduced') return 'reduced';
    return 'full';
  })();

  return {
    visible: true,
    showFlowParticles: worseLevel === 'full',
    curveSegments: worseLevel === 'full' ? 16 : worseLevel === 'reduced' ? 10 : 6,
  };
}

export default useLOD;
