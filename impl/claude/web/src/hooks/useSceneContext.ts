/**
 * useSceneContext - Unified context for 3D scenes
 *
 * @see plans/3d-visual-clarity.md
 *
 * Combines layout density (from useWindowLayout) with illumination quality
 * (from useIlluminationQuality) to provide a single context for 3D scene
 * configuration.
 *
 * Architecture:
 * ```
 * ┌───────────────────┐      ┌───────────────────┐
 * │   useWindowLayout │      │useIlluminationQual│
 * │   (2D density)    │      │   (3D quality)    │
 * └─────────┬─────────┘      └─────────┬─────────┘
 *           │                          │
 *           └──────────┬───────────────┘
 *                      ▼
 *           ┌──────────────────────┐
 *           │   useSceneContext()  │
 *           │ { density, quality } │
 *           └──────────────────────┘
 * ```
 */

import { useMemo } from 'react';
import { useWindowLayout } from './useLayoutContext';
import type { Density } from '../components/elastic/types';
import { useIlluminationQuality } from './useIlluminationQuality';
import {
  type IlluminationQuality,
  type ShadowBounds,
  getLightingConfig,
  shadowsEnabled,
  DEFAULT_SHADOW_BOUNDS,
} from '../constants/lighting';

// =============================================================================
// Types
// =============================================================================

export interface SceneContext {
  // Layout from useWindowLayout
  density: Density;
  isMobile: boolean;
  isTablet: boolean;
  isDesktop: boolean;
  width: number;
  height: number;

  // Illumination from useIlluminationQuality
  illuminationQuality: IlluminationQuality;
  shadowsEnabled: boolean;
  isAutoDetectedQuality: boolean;
  overrideQuality: (quality: IlluminationQuality | null) => void;

  // Derived configuration
  lightingConfig: ReturnType<typeof getLightingConfig>;
  shadowBounds: ShadowBounds;

  // Convenience: scene-level settings
  antialias: boolean;
  pixelRatio: number;
  cameraDistance: number;
}

// =============================================================================
// Hook
// =============================================================================

/**
 * Hook providing unified context for 3D scenes.
 *
 * Usage:
 * ```tsx
 * function My3DScene() {
 *   const {
 *     density,
 *     illuminationQuality,
 *     lightingConfig,
 *     shadowBounds,
 *   } = useSceneContext();
 *
 *   return (
 *     <Canvas>
 *       <SceneLighting
 *         quality={illuminationQuality}
 *         bounds={shadowBounds}
 *       />
 *       {/* ... *\/}
 *     </Canvas>
 *   );
 * }
 * ```
 */
export function useSceneContext(): SceneContext {
  // Get layout context
  const layout = useWindowLayout();

  // Get illumination quality
  const {
    quality: illuminationQuality,
    isAutoDetected,
    override,
  } = useIlluminationQuality();

  // Derive lighting configuration
  const lightingConfig = useMemo(
    () => getLightingConfig(illuminationQuality),
    [illuminationQuality]
  );

  // Default shadow bounds (can be overridden per-scene)
  const shadowBounds = DEFAULT_SHADOW_BOUNDS;

  // Derive scene-level settings
  const sceneSettings = useMemo(() => {
    // Antialias: off on mobile for performance
    const antialias = !layout.isMobile;

    // Pixel ratio: limit on mobile to save GPU
    const dpr = typeof window !== 'undefined' ? window.devicePixelRatio : 1;
    const pixelRatio = layout.isMobile
      ? Math.min(dpr, 1.5)
      : layout.isTablet
        ? Math.min(dpr, 2)
        : dpr;

    // Camera distance: further on mobile for overview
    const cameraDistance = layout.isMobile ? 30 : layout.isTablet ? 25 : 20;

    return { antialias, pixelRatio, cameraDistance };
  }, [layout.isMobile, layout.isTablet]);

  return {
    // Layout
    density: layout.density,
    isMobile: layout.isMobile,
    isTablet: layout.isTablet,
    isDesktop: layout.isDesktop,
    width: layout.width,
    height: layout.height,

    // Illumination
    illuminationQuality,
    shadowsEnabled: shadowsEnabled(illuminationQuality),
    isAutoDetectedQuality: isAutoDetected,
    overrideQuality: override,

    // Configuration
    lightingConfig,
    shadowBounds,

    // Scene settings
    ...sceneSettings,
  };
}

export default useSceneContext;
