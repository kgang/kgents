/**
 * CymaticsField - Wave Interference Visualization
 *
 * A Three.js shader-based component that visualizes cymatics patterns.
 * Cymatics makes vibration visible through wave interference.
 *
 * Usage in kgents:
 * - Coalition health visualization (harmonic = stable patterns)
 * - Agent communication frequency (rapid exchange = complex patterns)
 * - Memory resonance (access patterns create interference)
 *
 * Philosophy:
 *   "Cymatics reveals the hidden structure of agent interactions.
 *    The pattern was always there; we simply found the medium that reveals it."
 *
 * @see impl/claude/agents/i/reactive/animation/cymatics.py (Python isomorphism)
 * @see docs/creative/emergence-principles.md
 */

import { useRef, useMemo, useEffect } from 'react';
import { useFrame, extend } from '@react-three/fiber';
import * as THREE from 'three';
import { shaderMaterial } from '@react-three/drei';
import type { VibrationSource, CymaticsConfig } from '../../types/emergence';

// =============================================================================
// Constants
// =============================================================================

const MAX_SOURCES = 8; // Maximum vibration sources in shader

// Color schemes for different visualization contexts
const COLOR_SCHEMES = {
  cool: {
    primary: [0.0, 0.8, 0.9], // Cyan
    secondary: [0.2, 0.1, 0.4], // Deep purple
  },
  warm: {
    primary: [1.0, 0.6, 0.2], // Amber
    secondary: [0.4, 0.1, 0.2], // Deep red
  },
  neutral: {
    primary: [0.7, 0.7, 0.8], // Light gray-blue
    secondary: [0.15, 0.15, 0.2], // Dark gray
  },
  coalition: {
    primary: [0.4, 0.9, 0.5], // Green (harmony)
    secondary: [0.9, 0.3, 0.3], // Red (conflict)
  },
} as const;

// =============================================================================
// GLSL Shaders
// =============================================================================

const cymaticsVertexShader = /* glsl */ `
  varying vec2 vUv;
  varying vec3 vPosition;

  void main() {
    vUv = uv;
    vPosition = position;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

const cymaticsFragmentShader = /* glsl */ `
  precision highp float;

  uniform float uTime;
  uniform int uSourceCount;
  uniform vec2 uSourcePositions[${MAX_SOURCES}];
  uniform float uSourceFrequencies[${MAX_SOURCES}];
  uniform float uSourceAmplitudes[${MAX_SOURCES}];
  uniform float uSourcePhases[${MAX_SOURCES}];
  uniform float uSourceDecays[${MAX_SOURCES}];
  uniform vec3 uColorPrimary;
  uniform vec3 uColorSecondary;
  uniform float uIntensity;
  uniform bool uShowGrid;

  varying vec2 vUv;
  varying vec3 vPosition;

  const float PI = 3.14159265359;
  const float TAU = 6.28318530718;

  // Failsafe: Maximum frequency to prevent rapid flashing
  const float MAX_VISUAL_FREQ = 0.5;

  // Calculate wave amplitude at a point from a single source
  float waveFromSource(vec2 point, int index) {
    vec2 sourcePos = uSourcePositions[index];
    float freq = uSourceFrequencies[index];
    float amp = uSourceAmplitudes[index];
    float phase = uSourcePhases[index];
    float decay = uSourceDecays[index];

    // Clamp frequency to prevent rapid cycling flashes
    float safeFreq = min(freq, MAX_VISUAL_FREQ);

    // Distance from source
    float r = distance(point, sourcePos);

    // Wave number (spatial frequency) - reduced for more uniform animation
    float k = TAU * safeFreq * 0.15;

    // Distance decay (exponential falloff)
    float distanceFactor = exp(-decay * r);

    // Wave equation: A * exp(-decay * r) * sin(2*pi*f*t - k*r + phi)
    float wave = amp * distanceFactor * sin(TAU * safeFreq * uTime - k * r + phase);

    return wave;
  }

  // Superposition of all waves
  float totalAmplitude(vec2 point) {
    float total = 0.0;
    for (int i = 0; i < ${MAX_SOURCES}; i++) {
      if (i >= uSourceCount) break;
      total += waveFromSource(point, i);
    }
    return total;
  }

  // Grid overlay for reference
  float grid(vec2 uv, float lineWidth) {
    vec2 grid = abs(fract(uv * 10.0 - 0.5) - 0.5) / fwidth(uv * 10.0);
    float line = min(grid.x, grid.y);
    return 1.0 - min(line, 1.0);
  }

  void main() {
    // Convert UV to normalized space (-1 to 1)
    vec2 point = vUv * 2.0 - 1.0;

    // Calculate interference pattern
    float amplitude = totalAmplitude(point);

    // Normalize amplitude for visualization
    // Max possible amplitude = sum of all source amplitudes
    float maxAmp = 0.0;
    for (int i = 0; i < ${MAX_SOURCES}; i++) {
      if (i >= uSourceCount) break;
      maxAmp += uSourceAmplitudes[i];
    }
    maxAmp = max(maxAmp, 0.001); // Prevent division by zero

    float normalizedAmp = (amplitude / maxAmp + 1.0) * 0.5; // Map to 0-1

    // Apply intensity curve for better visualization
    // Clamp and smooth to prevent visual spikes
    float clampedAmp = clamp(normalizedAmp, 0.0, 1.0);
    float intensity = smoothstep(0.0, 1.0, clampedAmp) * uIntensity;
    intensity = min(intensity, 1.0); // Hard cap on intensity

    // Color mixing based on amplitude - compressed range for subtler visuals
    // High amplitude (constructive) = primary color
    // Low amplitude (destructive) = secondary color
    float colorMix = 0.30 + intensity * 0.40; // Compress to 0.30-0.70 range (+30%)
    vec3 color = mix(uColorSecondary, uColorPrimary, colorMix);

    // Add subtle emission at wave peaks
    float emission = pow(intensity, 3.0) * 0.3;
    color += uColorPrimary * emission;

    // Optional grid overlay
    if (uShowGrid) {
      float gridLine = grid(vUv, 0.02) * 0.15;
      color += vec3(gridLine);
    }

    // Final alpha based on intensity
    float alpha = 0.6 + intensity * 0.4;

    gl_FragColor = vec4(color, alpha);
  }
`;

// =============================================================================
// Shader Material Definition
// =============================================================================

// Create the custom shader material
const CymaticsShaderMaterial = shaderMaterial(
  {
    uTime: 0,
    uSourceCount: 0,
    uSourcePositions: new Array(MAX_SOURCES).fill(null).map(() => new THREE.Vector2(0, 0)),
    uSourceFrequencies: new Float32Array(MAX_SOURCES),
    uSourceAmplitudes: new Float32Array(MAX_SOURCES),
    uSourcePhases: new Float32Array(MAX_SOURCES),
    uSourceDecays: new Float32Array(MAX_SOURCES),
    uColorPrimary: new THREE.Color(0.0, 0.8, 0.9),
    uColorSecondary: new THREE.Color(0.2, 0.1, 0.4),
    uIntensity: 1.0,
    uShowGrid: false,
  },
  cymaticsVertexShader,
  cymaticsFragmentShader
);

// Extend Three.js with our custom material
extend({ CymaticsShaderMaterial });

// TypeScript declaration for JSX
declare global {
  namespace JSX {
    interface IntrinsicElements {
      cymaticsShaderMaterial: {
        ref?: React.RefObject<THREE.ShaderMaterial>;
        uTime?: number;
        uSourceCount?: number;
        uSourcePositions?: THREE.Vector2[];
        uSourceFrequencies?: Float32Array;
        uSourceAmplitudes?: Float32Array;
        uSourcePhases?: Float32Array;
        uSourceDecays?: Float32Array;
        uColorPrimary?: THREE.Color;
        uColorSecondary?: THREE.Color;
        uIntensity?: number;
        uShowGrid?: boolean;
        transparent?: boolean;
        side?: THREE.Side;
      };
    }
  }
}

// =============================================================================
// Types
// =============================================================================

export interface CymaticsFieldProps {
  /** Vibration sources for the interference pattern */
  sources: VibrationSource[];
  /** Configuration options */
  config?: CymaticsConfig;
  /** Size of the field in 3D units */
  size?: number;
  /** Position of the field */
  position?: [number, number, number];
  /** Rotation of the field */
  rotation?: [number, number, number];
  /** Callback when pattern stability changes */
  onStabilityChange?: (stability: number) => void;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Calculate pattern stability from sources.
 * Harmonic sources (same frequency) = high stability.
 * Dissonant sources (different frequencies) = low stability.
 */
function calculateStability(sources: VibrationSource[]): number {
  if (sources.length === 0) return 0;
  if (sources.length === 1) return 1;

  // Calculate frequency variance
  const frequencies = sources.map((s) => s.frequency);
  const meanFreq = frequencies.reduce((a, b) => a + b, 0) / frequencies.length;
  const variance =
    frequencies.reduce((sum, f) => sum + Math.pow(f - meanFreq, 2), 0) /
    frequencies.length;

  // Stability is inverse of variance (normalized)
  const maxVariance = meanFreq * meanFreq; // Max reasonable variance
  const normalizedVariance = Math.min(variance / maxVariance, 1);
  return 1 - normalizedVariance;
}

// =============================================================================
// Main Component
// =============================================================================

export function CymaticsField({
  sources,
  config = {},
  size = 4,
  position = [0, 0, 0],
  rotation = [-Math.PI / 2, 0, 0], // Default to horizontal plane
  onStabilityChange,
}: CymaticsFieldProps) {
  const materialRef = useRef<THREE.ShaderMaterial>(null);
  const lastStabilityRef = useRef<number>(-1);

  const {
    colorScheme = 'cool',
    showGrid = false,
    animate = true,
    animationSpeed = 1 / 36,
  } = config;

  // Get colors from scheme
  const colors = COLOR_SCHEMES[colorScheme];

  // Prepare source data for shader
  const sourceData = useMemo(() => {
    const positions: THREE.Vector2[] = [];
    const frequencies = new Float32Array(MAX_SOURCES);
    const amplitudes = new Float32Array(MAX_SOURCES);
    const phases = new Float32Array(MAX_SOURCES);
    const decays = new Float32Array(MAX_SOURCES);

    for (let i = 0; i < MAX_SOURCES; i++) {
      if (i < sources.length) {
        const source = sources[i];
        positions.push(new THREE.Vector2(source.position[0], source.position[1]));
        frequencies[i] = source.frequency;
        amplitudes[i] = source.amplitude;
        phases[i] = source.phase;
        decays[i] = source.decay;
      } else {
        positions.push(new THREE.Vector2(0, 0));
        frequencies[i] = 0;
        amplitudes[i] = 0;
        phases[i] = 0;
        decays[i] = 0;
      }
    }

    return { positions, frequencies, amplitudes, phases, decays };
  }, [sources]);

  // Calculate and report stability
  useEffect(() => {
    const stability = calculateStability(sources);
    if (stability !== lastStabilityRef.current) {
      lastStabilityRef.current = stability;
      onStabilityChange?.(stability);
    }
  }, [sources, onStabilityChange]);

  // Animation loop
  useFrame(({ clock }) => {
    if (materialRef.current && animate) {
      materialRef.current.uniforms.uTime.value = clock.elapsedTime * animationSpeed;
    }
  });

  return (
    <mesh position={position} rotation={rotation}>
      <planeGeometry args={[size, size, 64, 64]} />
      <cymaticsShaderMaterial
        ref={materialRef}
        uSourceCount={Math.min(sources.length, MAX_SOURCES)}
        uSourcePositions={sourceData.positions}
        uSourceFrequencies={sourceData.frequencies}
        uSourceAmplitudes={sourceData.amplitudes}
        uSourcePhases={sourceData.phases}
        uSourceDecays={sourceData.decays}
        uColorPrimary={new THREE.Color(...colors.primary)}
        uColorSecondary={new THREE.Color(...colors.secondary)}
        uIntensity={1.0}
        uShowGrid={showGrid}
        transparent
        side={THREE.DoubleSide}
      />
    </mesh>
  );
}

// =============================================================================
// Prebuilt Configurations
// =============================================================================

/**
 * CymaticsField preset for coalition health visualization.
 * Shows stability through harmonic patterns.
 */
export function CoalitionCymaticsField({
  agentCount,
  harmony,
  ...props
}: {
  agentCount: number;
  harmony: number; // 0-1, where 1 = perfect harmony
} & Omit<CymaticsFieldProps, 'sources'>) {
  // Generate sources based on agent count and harmony
  const sources: VibrationSource[] = useMemo(() => {
    const baseFreq = 2.0;
    const result: VibrationSource[] = [];

    for (let i = 0; i < Math.min(agentCount, MAX_SOURCES); i++) {
      const angle = (2 * Math.PI * i) / agentCount;
      const radius = 0.5;

      // Frequency deviation based on harmony (1 = same freq, 0 = varied)
      const freqDeviation = (1 - harmony) * (Math.random() - 0.5) * 2;

      result.push({
        frequency: baseFreq + freqDeviation,
        amplitude: 1.0,
        phase: 0,
        position: [radius * Math.cos(angle), radius * Math.sin(angle)],
        decay: 0.5,
      });
    }

    return result;
  }, [agentCount, harmony]);

  return (
    <CymaticsField
      sources={sources}
      config={{ colorScheme: 'coalition', animate: true }}
      {...props}
    />
  );
}

// =============================================================================
// Exports
// =============================================================================

export default CymaticsField;
export { MAX_SOURCES, COLOR_SCHEMES };
