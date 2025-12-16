/**
 * SceneLighting - Canonical lighting rig for all kgents 3D scenes
 *
 * @see plans/3d-visual-clarity.md
 * @see docs/skills/3d-lighting-patterns.md
 *
 * This component implements the canonical three-light minimum:
 * 1. Ambient light - Base illumination
 * 2. Sun (directional) - Key light with optional shadows
 * 3. Fill lights - Atmospheric mood lighting
 *
 * All parameters are derived from quality-based lookup tables in constants/lighting.ts.
 * This ensures consistent, quality-appropriate lighting across all 3D crown jewels.
 *
 * Usage:
 * ```tsx
 * import { SceneLighting } from '../components/three/SceneLighting';
 *
 * function My3DScene() {
 *   const { illuminationQuality } = useSceneContext();
 *   const bounds = calculateShadowBounds(nodes);
 *
 *   return (
 *     <Canvas shadows>
 *       <SceneLighting
 *         quality={illuminationQuality}
 *         bounds={bounds}
 *         atmosphericFill
 *       />
 *       {/* Your scene content *\/}
 *     </Canvas>
 *   );
 * }
 * ```
 */

import { useRef, useMemo } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import {
  type IlluminationQuality,
  type ShadowBounds,
  getLightingConfig,
  DEFAULT_SHADOW_BOUNDS,
  FILL_LIGHT_POSITIONS,
} from '../../constants/lighting';

// =============================================================================
// Types
// =============================================================================

export interface SceneLightingProps {
  /**
   * Illumination quality level. Determines shadow resolution, light intensities, etc.
   * @default 'standard'
   */
  quality?: IlluminationQuality;

  /**
   * Custom shadow frustum bounds. Use calculateShadowBounds() to compute from nodes.
   * @default DEFAULT_SHADOW_BOUNDS
   */
  bounds?: ShadowBounds;

  /**
   * Custom sun (key light) position. [x, y, z]
   * @default CANONICAL_SUN_POSITION from constants
   */
  sunPosition?: [number, number, number];

  /**
   * Enable atmospheric fill lights for enhanced mood/depth.
   * @default true
   */
  atmosphericFill?: boolean;

  /**
   * Sun light color.
   * @default '#ffffff'
   */
  sunColor?: string;

  /**
   * Ambient light color.
   * @default '#ffffff'
   */
  ambientColor?: string;

  /**
   * Enable soft shadows (PCFSoftShadowMap). Requires Canvas shadows prop.
   * @default true
   */
  softShadows?: boolean;

  /**
   * Animate fill lights with gentle breathing effect for "living" feel.
   * @default false
   */
  animateFillLights?: boolean;

  /**
   * Debug mode: show shadow camera frustum as wireframe.
   * @default false
   */
  debug?: boolean;
}

// =============================================================================
// Fill Light Component
// =============================================================================

interface FillLightProps {
  position: [number, number, number];
  color: string;
  intensity: number;
  animate?: boolean;
  index: number;
}

function FillLight({ position, color, intensity, animate, index }: FillLightProps) {
  const lightRef = useRef<THREE.PointLight>(null);

  useFrame(({ clock }) => {
    if (animate && lightRef.current) {
      // Gentle breathing: vary intensity ±15% at different rates per light
      const phase = clock.elapsedTime * (0.3 + index * 0.1);
      const breathe = 1 + Math.sin(phase) * 0.15;
      lightRef.current.intensity = intensity * breathe;
    }
  });

  return (
    <pointLight
      ref={lightRef}
      position={position}
      color={color}
      intensity={intensity}
      distance={50}
      decay={2}
    />
  );
}

// =============================================================================
// Shadow Camera Helper (Debug)
// =============================================================================

interface ShadowCameraHelperProps {
  lightRef: React.RefObject<THREE.DirectionalLight>;
}

function ShadowCameraHelper({ lightRef }: ShadowCameraHelperProps) {
  const helperRef = useRef<THREE.CameraHelper>(null);

  useFrame(() => {
    if (helperRef.current && lightRef.current) {
      helperRef.current.update();
    }
  });

  if (!lightRef.current) return null;

  return (
    <primitive
      ref={helperRef}
      object={new THREE.CameraHelper(lightRef.current.shadow.camera)}
    />
  );
}

// =============================================================================
// Main Component
// =============================================================================

export function SceneLighting({
  quality = 'standard',
  bounds = DEFAULT_SHADOW_BOUNDS,
  sunPosition,
  atmosphericFill = true,
  sunColor = '#ffffff',
  ambientColor = '#ffffff',
  softShadows = true,
  animateFillLights = false,
  debug = false,
}: SceneLightingProps) {
  const directionalLightRef = useRef<THREE.DirectionalLight>(null);

  // Get quality-based configuration
  const config = useMemo(() => getLightingConfig(quality), [quality]);
  const actualSunPosition = sunPosition ?? config.sunPosition;

  // Configure shadow camera when bounds or quality changes
  useMemo(() => {
    if (!directionalLightRef.current || !config.shadowsEnabled) return;

    const light = directionalLightRef.current;
    const shadow = light.shadow;

    // Shadow map size
    shadow.mapSize.width = config.shadowMapSize;
    shadow.mapSize.height = config.shadowMapSize;

    // Shadow camera frustum
    shadow.camera.left = bounds.left;
    shadow.camera.right = bounds.right;
    shadow.camera.top = bounds.top;
    shadow.camera.bottom = bounds.bottom;
    shadow.camera.near = bounds.near;
    shadow.camera.far = bounds.far;

    // Bias to prevent artifacts
    shadow.bias = config.shadowBias;
    shadow.normalBias = config.shadowNormalBias;

    // Soft shadow radius
    shadow.radius = config.shadowRadius;

    // Update camera matrices
    shadow.camera.updateProjectionMatrix();
  }, [bounds, config]);

  // Compute fill light intensities
  const fillLights = useMemo(() => {
    if (!atmosphericFill) return [];

    return FILL_LIGHT_POSITIONS.map((fill, index) => ({
      ...fill,
      intensity: config.fillIntensity * fill.intensityMultiplier,
      index,
    }));
  }, [atmosphericFill, config.fillIntensity]);

  return (
    <>
      {/* Ambient - base illumination */}
      <ambientLight color={ambientColor} intensity={config.ambientIntensity} />

      {/* Sun - key light with shadows */}
      <directionalLight
        ref={directionalLightRef}
        position={actualSunPosition}
        color={sunColor}
        intensity={config.sunIntensity}
        castShadow={config.shadowsEnabled}
        shadow-mapSize-width={config.shadowMapSize}
        shadow-mapSize-height={config.shadowMapSize}
        shadow-camera-left={bounds.left}
        shadow-camera-right={bounds.right}
        shadow-camera-top={bounds.top}
        shadow-camera-bottom={bounds.bottom}
        shadow-camera-near={bounds.near}
        shadow-camera-far={bounds.far}
        shadow-bias={config.shadowBias}
        shadow-normalBias={config.shadowNormalBias}
        shadow-radius={softShadows ? config.shadowRadius : 0}
      />

      {/* Fill lights - atmospheric mood */}
      {fillLights.map((fill) => (
        <FillLight
          key={fill.index}
          position={fill.position}
          color={fill.color}
          intensity={fill.intensity}
          animate={animateFillLights}
          index={fill.index}
        />
      ))}

      {/* Debug: show shadow frustum */}
      {debug && config.shadowsEnabled && (
        <ShadowCameraHelper lightRef={directionalLightRef} />
      )}
    </>
  );
}

// =============================================================================
// Shadow Plane Component
// =============================================================================

export interface ShadowPlaneProps {
  /**
   * Y position of the shadow plane.
   * @default -5
   */
  y?: number;

  /**
   * Size of the shadow plane (width & height).
   * @default 100
   */
  size?: number;

  /**
   * Opacity of received shadows.
   * @default 0.3
   */
  shadowOpacity?: number;

  /**
   * Whether the plane is visible (false = invisible shadow catcher).
   * @default false
   */
  visible?: boolean;
}

/**
 * Invisible plane that receives shadows for ground contact.
 *
 * Usage:
 * ```tsx
 * <Canvas shadows>
 *   <SceneLighting quality="high" />
 *   <ShadowPlane y={-5} />
 *   {/* Your 3D nodes *\/}
 * </Canvas>
 * ```
 */
export function ShadowPlane({
  y = -5,
  size = 100,
  shadowOpacity = 0.3,
  visible = false,
}: ShadowPlaneProps) {
  return (
    <mesh
      position={[0, y, 0]}
      rotation={[-Math.PI / 2, 0, 0]}
      receiveShadow
    >
      <planeGeometry args={[size, size]} />
      <shadowMaterial
        transparent
        opacity={shadowOpacity}
        color="#1a1a2e"  // Soft blue-gray shadows per plan
      />
      {visible && (
        <meshStandardMaterial
          color="#1a1a2e"
          transparent
          opacity={0.1}
        />
      )}
    </mesh>
  );
}

// =============================================================================
// Exports
// =============================================================================

export default SceneLighting;
