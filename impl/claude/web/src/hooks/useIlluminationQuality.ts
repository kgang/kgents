/**
 * useIlluminationQuality - Device capability detection for 3D rendering
 *
 * @see plans/3d-visual-clarity.md
 *
 * Detects device WebGL capabilities and battery status to determine
 * the appropriate illumination quality level. Memoizes detection to
 * run only once per session.
 *
 * Decision factors:
 * 1. WebGL capabilities (extensions, max texture size, etc.)
 * 2. Device pixel ratio (indicates display quality expectations)
 * 3. Battery status (low power mode → minimal quality)
 * 4. User preference (if stored)
 */

import { useState, useEffect, useMemo } from 'react';
import type { IlluminationQuality } from '../constants/lighting';

// =============================================================================
// Types
// =============================================================================

interface DeviceCapabilities {
  maxTextureSize: number;
  maxRenderbufferSize: number;
  floatTexturesSupported: boolean;
  anisotropySupported: boolean;
  maxAnisotropy: number;
  shaderPrecision: 'lowp' | 'mediump' | 'highp';
  webglVersion: 1 | 2 | null;
}

interface BatteryStatus {
  isCharging: boolean;
  level: number;
  isLowPower: boolean;
}

interface IlluminationQualityResult {
  quality: IlluminationQuality;
  capabilities: DeviceCapabilities | null;
  battery: BatteryStatus | null;
  isAutoDetected: boolean;
  override: (quality: IlluminationQuality | null) => void;
}

// =============================================================================
// Detection Functions
// =============================================================================

/**
 * Detect WebGL capabilities from a canvas context.
 */
function detectCapabilities(): DeviceCapabilities | null {
  if (typeof window === 'undefined') return null;

  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');

  if (!gl) return null;

  const isWebGL2 = gl instanceof WebGL2RenderingContext;

  // Get shader precision
  let shaderPrecision: 'lowp' | 'mediump' | 'highp' = 'lowp';
  const fragmentShaderPrecision = gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.HIGH_FLOAT);
  if (fragmentShaderPrecision && fragmentShaderPrecision.precision > 0) {
    shaderPrecision = 'highp';
  } else {
    const mediumPrecision = gl.getShaderPrecisionFormat(gl.FRAGMENT_SHADER, gl.MEDIUM_FLOAT);
    if (mediumPrecision && mediumPrecision.precision > 0) {
      shaderPrecision = 'mediump';
    }
  }

  // Check float texture support
  const floatTexturesSupported = isWebGL2 || !!gl.getExtension('OES_texture_float');

  // Check anisotropic filtering
  const anisotropyExt =
    gl.getExtension('EXT_texture_filter_anisotropic') ||
    gl.getExtension('WEBKIT_EXT_texture_filter_anisotropic') ||
    gl.getExtension('MOZ_EXT_texture_filter_anisotropic');
  const anisotropySupported = !!anisotropyExt;
  const maxAnisotropy = anisotropyExt
    ? gl.getParameter(anisotropyExt.MAX_TEXTURE_MAX_ANISOTROPY_EXT)
    : 1;

  return {
    maxTextureSize: gl.getParameter(gl.MAX_TEXTURE_SIZE),
    maxRenderbufferSize: gl.getParameter(gl.MAX_RENDERBUFFER_SIZE),
    floatTexturesSupported,
    anisotropySupported,
    maxAnisotropy,
    shaderPrecision,
    webglVersion: isWebGL2 ? 2 : 1,
  };
}

/**
 * Detect battery status using Battery API.
 */
async function detectBatteryStatus(): Promise<BatteryStatus | null> {
  if (typeof navigator === 'undefined') return null;

  // Battery API is not available in all browsers
  // @ts-expect-error - getBattery is not in standard Navigator type
  if (!navigator.getBattery) return null;

  try {
    // @ts-expect-error - getBattery is not in standard Navigator type
    const battery = await navigator.getBattery();
    return {
      isCharging: battery.charging,
      level: battery.level,
      isLowPower: !battery.charging && battery.level < 0.2,
    };
  } catch {
    return null;
  }
}

/**
 * Determine quality level from capabilities and battery.
 */
function determineQuality(
  capabilities: DeviceCapabilities | null,
  battery: BatteryStatus | null,
  devicePixelRatio: number
): IlluminationQuality {
  // Low battery → minimal
  if (battery?.isLowPower) {
    return 'minimal';
  }

  // No WebGL → minimal
  if (!capabilities) {
    return 'minimal';
  }

  // Score based on capabilities
  let score = 0;

  // WebGL 2 is better
  if (capabilities.webglVersion === 2) score += 2;

  // High shader precision
  if (capabilities.shaderPrecision === 'highp') score += 2;
  else if (capabilities.shaderPrecision === 'mediump') score += 1;

  // Large texture support
  if (capabilities.maxTextureSize >= 8192) score += 2;
  else if (capabilities.maxTextureSize >= 4096) score += 1;

  // Float textures for better shadows
  if (capabilities.floatTexturesSupported) score += 1;

  // Anisotropic filtering
  if (capabilities.anisotropySupported && capabilities.maxAnisotropy >= 8) score += 1;

  // High DPI displays expect quality
  if (devicePixelRatio >= 2) score += 1;
  if (devicePixelRatio >= 3) score += 1;

  // Map score to quality
  if (score >= 9) return 'cinematic';
  if (score >= 6) return 'high';
  if (score >= 3) return 'standard';
  return 'minimal';
}

// =============================================================================
// Singleton Cache
// =============================================================================

let cachedCapabilities: DeviceCapabilities | null = null;
let cachedBattery: BatteryStatus | null = null;
let detectionComplete = false;

// =============================================================================
// Hook
// =============================================================================

const LOCAL_STORAGE_KEY = 'kgents-illumination-quality';

/**
 * Hook to detect and manage illumination quality.
 *
 * Usage:
 * ```tsx
 * const { quality, override } = useIlluminationQuality();
 *
 * // Use quality for SceneLighting
 * <SceneLighting quality={quality} />
 *
 * // Let user override
 * <select onChange={(e) => override(e.target.value as IlluminationQuality)}>
 *   ...
 * </select>
 * ```
 */
export function useIlluminationQuality(): IlluminationQualityResult {
  const [capabilities, setCapabilities] = useState<DeviceCapabilities | null>(cachedCapabilities);
  const [battery, setBattery] = useState<BatteryStatus | null>(cachedBattery);
  const [userOverride, setUserOverride] = useState<IlluminationQuality | null>(() => {
    if (typeof window === 'undefined') return null;
    const stored = localStorage.getItem(LOCAL_STORAGE_KEY);
    return stored as IlluminationQuality | null;
  });

  // Run detection once
  useEffect(() => {
    if (detectionComplete) return;

    // Detect WebGL capabilities (sync)
    if (!cachedCapabilities) {
      cachedCapabilities = detectCapabilities();
      setCapabilities(cachedCapabilities);
    }

    // Detect battery (async)
    detectBatteryStatus().then((status) => {
      cachedBattery = status;
      setBattery(status);
      detectionComplete = true;
    });
  }, []);

  // Calculate auto-detected quality
  const autoQuality = useMemo(() => {
    const dpr = typeof window !== 'undefined' ? window.devicePixelRatio : 1;
    return determineQuality(capabilities, battery, dpr);
  }, [capabilities, battery]);

  // Override handler with persistence
  const override = (quality: IlluminationQuality | null) => {
    setUserOverride(quality);
    if (quality) {
      localStorage.setItem(LOCAL_STORAGE_KEY, quality);
    } else {
      localStorage.removeItem(LOCAL_STORAGE_KEY);
    }
  };

  return {
    quality: userOverride ?? autoQuality,
    capabilities,
    battery,
    isAutoDetected: !userOverride,
    override,
  };
}

export default useIlluminationQuality;
