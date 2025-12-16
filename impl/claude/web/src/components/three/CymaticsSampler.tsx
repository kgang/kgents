/**
 * CymaticsSampler - Design exploration for cymatics patterns
 *
 * Philosophy:
 *   Instead of tuning parameters blindly, show many variations at once.
 *   The eye finds what it likes faster than the mind predicts.
 *
 * Pattern families explored:
 * 1. Chladni plates (standing wave patterns)
 * 2. Interference (multiple point sources)
 * 3. Reaction-diffusion (Turing-like patterns)
 * 4. Mandala (radial symmetry)
 * 5. Organic flow (noise-driven)
 */

import { useRef } from 'react';
import { useFrame, extend } from '@react-three/fiber';
import * as THREE from 'three';
import { shaderMaterial } from '@react-three/drei';

// =============================================================================
// Pattern Types
// =============================================================================

export type PatternFamily =
  | 'chladni'          // Classic Chladni plate patterns
  | 'interference'     // Circular wave interference
  | 'mandala'          // Radial symmetry patterns
  | 'flow'             // Organic noise-driven
  | 'reaction'         // Reaction-diffusion inspired
  | 'spiral'           // Logarithmic spirals
  | 'voronoi'          // Cellular patterns
  | 'moiré'            // Overlapping patterns
  | 'fractal';         // Self-similar structures

export interface PatternConfig {
  family: PatternFamily;
  /** Primary parameter (meaning varies by family) */
  param1: number;
  /** Secondary parameter */
  param2: number;
  /** Color hue (0-1) */
  hue: number;
  /** Color saturation (0-1) */
  saturation: number;
  /** Animation speed (0 = static) */
  speed: number;
  /** Invert colors */
  invert: boolean;
}

// =============================================================================
// Vertex Shader (shared)
// =============================================================================

const vertexShader = /* glsl */ `
  varying vec2 vUv;
  void main() {
    vUv = uv;
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`;

// =============================================================================
// Fragment Shaders for Each Pattern Family
// =============================================================================

const patternShaders: Record<PatternFamily, string> = {
  // Classic Chladni plate: sin(n*pi*x)*sin(m*pi*y) ± sin(m*pi*x)*sin(n*pi*y)
  chladni: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // n mode
    uniform float uParam2;  // m mode
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    const float PI = 3.14159265359;

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    void main() {
      vec2 p = vUv * 2.0 - 1.0;
      float n = uParam1;
      float m = uParam2;
      float t = uTime * uSpeed * 0.3;

      // Chladni pattern with animation
      float pattern = sin(n * PI * p.x) * sin(m * PI * p.y)
                    + sin(m * PI * p.x) * sin(n * PI * p.y);

      // Add subtle time-based phase shift
      pattern *= cos(t * 0.5);

      // Normalize to 0-1
      float v = (pattern + 2.0) / 4.0;
      if (uInvert) v = 1.0 - v;

      // High contrast coloring
      float edge = smoothstep(0.48, 0.52, v);
      vec3 color = mix(
        hsl2rgb(uHue, uSaturation, 0.15),
        hsl2rgb(uHue + 0.1, uSaturation * 0.7, 0.85),
        edge
      );

      gl_FragColor = vec4(color, 1.0);
    }
  `,

  // Interference: Multiple circular waves from point sources
  interference: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // number of sources (2-8)
    uniform float uParam2;  // wavelength
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    const float PI = 3.14159265359;
    const float TAU = 6.28318530718;

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    void main() {
      vec2 p = vUv * 2.0 - 1.0;
      float sources = floor(uParam1);
      float wavelength = uParam2;
      float t = uTime * uSpeed * 0.5;

      float total = 0.0;
      for (float i = 0.0; i < 8.0; i++) {
        if (i >= sources) break;
        float angle = TAU * i / sources;
        vec2 sourcePos = 0.6 * vec2(cos(angle), sin(angle));
        float r = distance(p, sourcePos);
        total += sin(TAU * r / wavelength - t);
      }

      // Normalize
      float v = (total / sources + 1.0) * 0.5;
      if (uInvert) v = 1.0 - v;

      // Smooth gradient coloring
      vec3 color = hsl2rgb(uHue + v * 0.15, uSaturation, 0.2 + v * 0.6);
      gl_FragColor = vec4(color, 1.0);
    }
  `,

  // Mandala: Radial symmetry with angular harmonics
  mandala: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // rotational symmetry (3-12)
    uniform float uParam2;  // complexity
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    const float PI = 3.14159265359;
    const float TAU = 6.28318530718;

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    void main() {
      vec2 p = vUv * 2.0 - 1.0;
      float r = length(p);
      float theta = atan(p.y, p.x);
      float sym = floor(uParam1);
      float complexity = uParam2;
      float t = uTime * uSpeed * 0.2;

      // Radial component
      float radial = sin(r * complexity * PI - t);

      // Angular component with symmetry
      float angular = cos(sym * theta + t * 0.3);

      // Combine
      float pattern = radial * angular;

      // Add harmonics
      pattern += 0.3 * sin(r * complexity * 2.0 * PI + t) * cos(sym * 2.0 * theta);

      // Normalize
      float v = (pattern + 1.3) / 2.6;
      if (uInvert) v = 1.0 - v;

      // Gradient based on radius and pattern
      float l = 0.15 + v * 0.65;
      vec3 color = hsl2rgb(uHue + r * 0.08, uSaturation * (1.0 - r * 0.3), l);

      gl_FragColor = vec4(color, 1.0);
    }
  `,

  // Flow: Noise-driven organic patterns
  flow: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // scale
    uniform float uParam2;  // turbulence
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    // Simplex noise
    vec3 mod289(vec3 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec2 mod289(vec2 x) { return x - floor(x * (1.0 / 289.0)) * 289.0; }
    vec3 permute(vec3 x) { return mod289(((x*34.0)+1.0)*x); }

    float snoise(vec2 v) {
      const vec4 C = vec4(0.211324865405187, 0.366025403784439,
                         -0.577350269189626, 0.024390243902439);
      vec2 i  = floor(v + dot(v, C.yy));
      vec2 x0 = v - i + dot(i, C.xx);
      vec2 i1 = (x0.x > x0.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
      vec4 x12 = x0.xyxy + C.xxzz;
      x12.xy -= i1;
      i = mod289(i);
      vec3 p = permute(permute(i.y + vec3(0.0, i1.y, 1.0))
                             + i.x + vec3(0.0, i1.x, 1.0));
      vec3 m = max(0.5 - vec3(dot(x0,x0), dot(x12.xy,x12.xy),
                              dot(x12.zw,x12.zw)), 0.0);
      m = m*m; m = m*m;
      vec3 x = 2.0 * fract(p * C.www) - 1.0;
      vec3 h = abs(x) - 0.5;
      vec3 ox = floor(x + 0.5);
      vec3 a0 = x - ox;
      m *= 1.79284291400159 - 0.85373472095314 * (a0*a0 + h*h);
      vec3 g;
      g.x = a0.x * x0.x + h.x * x0.y;
      g.yz = a0.yz * x12.xz + h.yz * x12.yw;
      return 130.0 * dot(m, g);
    }

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    void main() {
      vec2 p = vUv * 2.0 - 1.0;
      float scale = uParam1;
      float turb = uParam2;
      float t = uTime * uSpeed * 0.1;

      // Layered noise
      float n = 0.0;
      float amp = 1.0;
      float freq = scale;
      for (int i = 0; i < 4; i++) {
        n += amp * snoise(p * freq + t);
        amp *= turb;
        freq *= 2.0;
      }

      // Normalize
      float v = (n + 1.5) / 3.0;
      if (uInvert) v = 1.0 - v;

      // Smooth color mapping
      vec3 color = hsl2rgb(uHue + v * 0.1, uSaturation, 0.1 + v * 0.7);
      gl_FragColor = vec4(color, 1.0);
    }
  `,

  // Reaction: Turing pattern inspired
  reaction: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // spot size
    uniform float uParam2;  // stripe/spot mix
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    const float PI = 3.14159265359;

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    // Pseudo reaction-diffusion via math
    void main() {
      vec2 p = vUv * 2.0 - 1.0;
      float scale = uParam1;
      float mix_val = uParam2;
      float t = uTime * uSpeed * 0.15;

      // Spot pattern
      float spots = sin(p.x * scale * PI) * sin(p.y * scale * PI);

      // Stripe pattern
      float stripes = sin((p.x + p.y) * scale * PI * 0.7 + t);

      // Mix based on param2
      float pattern = mix(spots, stripes, mix_val);

      // Add some organic distortion
      pattern += 0.2 * sin(p.x * scale * 2.0 * PI) * cos(p.y * scale * 1.5 * PI + t);

      // Threshold for high contrast
      float v = smoothstep(-0.3, 0.3, pattern);
      if (uInvert) v = 1.0 - v;

      vec3 color = mix(
        hsl2rgb(uHue, uSaturation, 0.1),
        hsl2rgb(uHue + 0.05, uSaturation * 0.8, 0.8),
        v
      );

      gl_FragColor = vec4(color, 1.0);
    }
  `,

  // Spiral: Logarithmic spirals
  // Fixed: Removed horizontal line artifact by using atan2 properly and
  // smoothing the angular discontinuity
  spiral: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // arms
    uniform float uParam2;  // tightness
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    const float PI = 3.14159265359;
    const float TAU = 6.28318530718;

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    void main() {
      vec2 p = vUv * 2.0 - 1.0;
      float r = length(p);

      // Use atan with proper handling to avoid discontinuity line
      // Adding small offset and using mod to wrap smoothly
      float theta = atan(p.y, p.x + 0.0001);

      float arms = floor(uParam1);
      float tightness = uParam2;
      float t = uTime * uSpeed * 0.3;

      // Logarithmic spiral with smooth wrapping
      float spiralPhase = arms * theta - tightness * log(max(r, 0.01)) + t;
      float spiral = sin(spiralPhase);

      // Secondary spiral for richness (offset phase to avoid alignment)
      float spiral2Phase = arms * 1.5 * theta + tightness * 0.7 * log(max(r, 0.01)) - t * 0.5 + PI * 0.25;
      float spiral2 = sin(spiral2Phase);

      float pattern = spiral + 0.4 * spiral2;

      // Smooth radial fade (center and edge)
      float fade = smoothstep(0.0, 0.15, r) * smoothstep(1.1, 0.7, r);
      pattern *= fade;

      float v = (pattern + 1.4) / 2.8;
      if (uInvert) v = 1.0 - v;

      vec3 color = hsl2rgb(uHue + r * 0.1, uSaturation, 0.15 + v * 0.65);
      gl_FragColor = vec4(color, 1.0);
    }
  `,

  // Voronoi: Cellular patterns
  voronoi: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // cell count
    uniform float uParam2;  // edge sharpness
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    vec2 hash2(vec2 p) {
      return fract(sin(vec2(dot(p,vec2(127.1,311.7)),dot(p,vec2(269.5,183.3))))*43758.5453);
    }

    void main() {
      vec2 p = vUv * uParam1;
      float t = uTime * uSpeed * 0.1;

      vec2 n = floor(p);
      vec2 f = fract(p);

      float md = 8.0;
      float md2 = 8.0;

      for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
          vec2 g = vec2(float(i), float(j));
          vec2 o = hash2(n + g);
          o = 0.5 + 0.5 * sin(t + 6.2831 * o);
          vec2 r = g + o - f;
          float d = dot(r, r);
          if (d < md) {
            md2 = md;
            md = d;
          } else if (d < md2) {
            md2 = d;
          }
        }
      }

      // Edge detection
      float edge = md2 - md;
      edge = pow(edge, uParam2);

      float v = edge;
      if (uInvert) v = 1.0 - v;

      vec3 color = hsl2rgb(uHue + edge * 0.1, uSaturation, 0.1 + v * 0.75);
      gl_FragColor = vec4(color, 1.0);
    }
  `,

  // Moiré: Overlapping patterns
  moiré: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // line density
    uniform float uParam2;  // rotation offset
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    const float PI = 3.14159265359;

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    mat2 rotate(float a) {
      float c = cos(a), s = sin(a);
      return mat2(c, -s, s, c);
    }

    void main() {
      vec2 p = vUv * 2.0 - 1.0;
      float density = uParam1;
      float angle = uParam2 * PI;
      float t = uTime * uSpeed * 0.1;

      // First grating
      float g1 = sin(p.x * density * PI);

      // Second grating, rotated
      vec2 p2 = rotate(angle + t) * p;
      float g2 = sin(p2.x * density * PI);

      // Third grating at different angle
      vec2 p3 = rotate(-angle * 0.7) * p;
      float g3 = sin(p3.x * density * PI * 0.8);

      // Combine
      float pattern = g1 * g2 + g2 * g3 * 0.5;

      float v = (pattern + 1.5) / 3.0;
      if (uInvert) v = 1.0 - v;

      vec3 color = hsl2rgb(uHue + v * 0.08, uSaturation, 0.1 + v * 0.7);
      gl_FragColor = vec4(color, 1.0);
    }
  `,

  // Fractal: Self-similar patterns (simplified Mandelbrot-like)
  fractal: /* glsl */ `
    precision highp float;
    uniform float uTime;
    uniform float uParam1;  // zoom
    uniform float uParam2;  // iterations influence
    uniform float uHue;
    uniform float uSaturation;
    uniform float uSpeed;
    uniform bool uInvert;
    varying vec2 vUv;

    const float PI = 3.14159265359;

    vec3 hsl2rgb(float h, float s, float l) {
      vec3 rgb = clamp(abs(mod(h*6.0+vec3(0.0,4.0,2.0),6.0)-3.0)-1.0, 0.0, 1.0);
      return l + s * (rgb - 0.5) * (1.0 - abs(2.0 * l - 1.0));
    }

    void main() {
      vec2 p = (vUv * 2.0 - 1.0) * uParam1;
      float t = uTime * uSpeed * 0.05;

      // Julia set variant with animated constant
      vec2 c = vec2(0.355 + 0.1 * sin(t), 0.355 + 0.1 * cos(t * 1.3));
      vec2 z = p;

      float iter = 0.0;
      float maxIter = 8.0 + uParam2 * 12.0;

      for (float i = 0.0; i < 20.0; i++) {
        if (i >= maxIter || dot(z, z) > 4.0) break;
        z = vec2(z.x*z.x - z.y*z.y, 2.0*z.x*z.y) + c;
        iter = i;
      }

      float v = iter / maxIter;
      if (uInvert) v = 1.0 - v;

      // Smooth coloring
      vec3 color = hsl2rgb(uHue + v * 0.3, uSaturation * (0.5 + v * 0.5), 0.1 + v * 0.6);
      gl_FragColor = vec4(color, 1.0);
    }
  `,
};

// =============================================================================
// Shader Material Factory
// =============================================================================

function createPatternMaterial(family: PatternFamily) {
  return shaderMaterial(
    {
      uTime: 0,
      uParam1: 3.0,
      uParam2: 0.5,
      uHue: 0.55,
      uSaturation: 0.7,
      uSpeed: 1.0,
      uInvert: false,
    },
    vertexShader,
    patternShaders[family]
  );
}

// Create all pattern materials - keys must match JSX element names
const PatternMaterials = {
  ChladniMaterial: createPatternMaterial('chladni'),
  InterferenceMaterial: createPatternMaterial('interference'),
  MandalaMaterial: createPatternMaterial('mandala'),
  FlowMaterial: createPatternMaterial('flow'),
  ReactionMaterial: createPatternMaterial('reaction'),
  SpiralMaterial: createPatternMaterial('spiral'),
  VoronoiMaterial: createPatternMaterial('voronoi'),
  MoireMaterial: createPatternMaterial('moiré'),
  FractalMaterial: createPatternMaterial('fractal'),
} as const;

// Extend Three.js - this makes <chladniMaterial />, <interferenceMaterial /> etc. available
extend(PatternMaterials);

// TypeScript declarations
declare global {
  namespace JSX {
    interface IntrinsicElements {
      chladniMaterial: PatternMaterialProps;
      interferenceMaterial: PatternMaterialProps;
      mandalaMaterial: PatternMaterialProps;
      flowMaterial: PatternMaterialProps;
      reactionMaterial: PatternMaterialProps;
      spiralMaterial: PatternMaterialProps;
      voronoiMaterial: PatternMaterialProps;
      moireMaterial: PatternMaterialProps;
      fractalMaterial: PatternMaterialProps;
    }
  }
}

interface PatternMaterialProps {
  ref?: React.RefObject<THREE.ShaderMaterial>;
  uTime?: number;
  uParam1?: number;
  uParam2?: number;
  uHue?: number;
  uSaturation?: number;
  uSpeed?: number;
  uInvert?: boolean;
}

// =============================================================================
// Components
// =============================================================================

export interface PatternTileProps {
  config: PatternConfig;
  /** Size in 3D units */
  size?: number;
  /** Position */
  position?: [number, number, number];
  /** Whether to animate */
  animate?: boolean;
  /** Optional label */
  label?: string;
}

/**
 * A single pattern tile that can display any pattern family.
 */
export function PatternTile({
  config,
  size = 1,
  position = [0, 0, 0],
  animate = true,
}: PatternTileProps) {
  const materialRef = useRef<THREE.ShaderMaterial>(null);

  useFrame(({ clock }) => {
    if (materialRef.current && animate) {
      materialRef.current.uniforms.uTime.value = clock.elapsedTime;
    }
  });

  // Common material props
  const materialProps = {
    ref: materialRef,
    uParam1: config.param1,
    uParam2: config.param2,
    uHue: config.hue,
    uSaturation: config.saturation,
    uSpeed: config.speed,
    uInvert: config.invert,
  };

  // Render the appropriate material based on family
  const renderMaterial = () => {
    switch (config.family) {
      case 'chladni':
        return <chladniMaterial {...materialProps} />;
      case 'interference':
        return <interferenceMaterial {...materialProps} />;
      case 'mandala':
        return <mandalaMaterial {...materialProps} />;
      case 'flow':
        return <flowMaterial {...materialProps} />;
      case 'reaction':
        return <reactionMaterial {...materialProps} />;
      case 'spiral':
        return <spiralMaterial {...materialProps} />;
      case 'voronoi':
        return <voronoiMaterial {...materialProps} />;
      case 'moiré':
        return <moireMaterial {...materialProps} />;
      case 'fractal':
        return <fractalMaterial {...materialProps} />;
      default:
        return <chladniMaterial {...materialProps} />;
    }
  };

  return (
    <mesh position={position}>
      <planeGeometry args={[size, size]} />
      {renderMaterial()}
    </mesh>
  );
}

// =============================================================================
// Preset Configurations
// =============================================================================

/**
 * KGENTS DESIGN PALETTE - Curated Cymatics Patterns
 *
 * These presets form the official visual language of the kgents system.
 * Use these patterns for backgrounds, transitions, loading states, and
 * ambient visualizations throughout the UI.
 *
 * Animation Speed Guidelines:
 * - Most patterns: Speed increased 40% for responsiveness
 * - spiral-3, spiral-5: Original speed preserved (meditative quality)
 *
 * Color Families:
 * - Cyan (hue ~0.55): Primary brand, used for brain/memory
 * - Purple (hue ~0.75-0.85): Soul/spiritual, used for K-gent
 * - Orange (hue ~0.08): Energy/action, used for alerts
 * - Neutral (saturation ~0): Subtle backgrounds
 */
export const PATTERN_PRESETS: Record<string, PatternConfig> = {
  // ---------------------------------------------------------------------------
  // Chladni - Standing wave patterns (physics-inspired)
  // Use: Loading states, phase transitions
  // ---------------------------------------------------------------------------
  'chladni-4-5': { family: 'chladni', param1: 4, param2: 5, hue: 0.55, saturation: 0.7, speed: 0.7, invert: false },
  'chladni-3-7': { family: 'chladni', param1: 3, param2: 7, hue: 0.08, saturation: 0.8, speed: 0.42, invert: false },
  'chladni-6-6': { family: 'chladni', param1: 6, param2: 6, hue: 0.75, saturation: 0.6, speed: 0.56, invert: true },

  // ---------------------------------------------------------------------------
  // Interference - Ripple patterns (water-like)
  // Use: Connection visualization, network activity
  // ---------------------------------------------------------------------------
  'interference-4': { family: 'interference', param1: 4, param2: 0.3, hue: 0.55, saturation: 0.8, speed: 1.4, invert: false },
  'interference-6': { family: 'interference', param1: 6, param2: 0.25, hue: 0.95, saturation: 0.7, speed: 1.12, invert: false },

  // ---------------------------------------------------------------------------
  // Mandala - Radial symmetry (sacred geometry)
  // Use: Soul/consciousness states, meditation mode
  // ---------------------------------------------------------------------------
  'mandala-6': { family: 'mandala', param1: 6, param2: 4, hue: 0.85, saturation: 0.6, speed: 0.7, invert: false },
  'mandala-8': { family: 'mandala', param1: 8, param2: 6, hue: 0.55, saturation: 0.7, speed: 0.42, invert: false },

  // ---------------------------------------------------------------------------
  // Flow - Organic noise (nature-inspired)
  // Use: Ambient backgrounds, idle states
  // ---------------------------------------------------------------------------
  'flow-calm': { family: 'flow', param1: 2, param2: 0.5, hue: 0.55, saturation: 0.5, speed: 0.42, invert: false },
  'flow-turbulent': { family: 'flow', param1: 4, param2: 0.65, hue: 0.08, saturation: 0.7, speed: 0.84, invert: false },

  // ---------------------------------------------------------------------------
  // Reaction - Turing patterns (biological)
  // Use: Agent evolution, emergence visualization
  // ---------------------------------------------------------------------------
  'reaction-spots': { family: 'reaction', param1: 5, param2: 0.2, hue: 0.45, saturation: 0.6, speed: 0.56, invert: false },
  'reaction-stripes': { family: 'reaction', param1: 4, param2: 0.8, hue: 0.0, saturation: 0.7, speed: 0.42, invert: false },

  // ---------------------------------------------------------------------------
  // Spiral - Logarithmic spirals (golden ratio)
  // Use: Brain topology, memory crystallization
  // NOTE: These two preserve original speed for meditative quality
  // ---------------------------------------------------------------------------
  'spiral-3': { family: 'spiral', param1: 3, param2: 2, hue: 0.75, saturation: 0.7, speed: 0.5, invert: false },
  'spiral-5': { family: 'spiral', param1: 5, param2: 3, hue: 0.55, saturation: 0.8, speed: 0.4, invert: false },

  // ---------------------------------------------------------------------------
  // Voronoi - Cellular patterns (crystalline)
  // Use: Memory crystals, data clustering
  // ---------------------------------------------------------------------------
  'voronoi-sparse': { family: 'voronoi', param1: 4, param2: 0.3, hue: 0.55, saturation: 0.6, speed: 0.7, invert: false },
  'voronoi-dense': { family: 'voronoi', param1: 8, param2: 0.5, hue: 0.15, saturation: 0.7, speed: 0.42, invert: true },

  // ---------------------------------------------------------------------------
  // Moiré - Interference patterns (optical)
  // Use: Subtle backgrounds, layered UI depth
  // ---------------------------------------------------------------------------
  'moiré-subtle': { family: 'moiré', param1: 15, param2: 0.1, hue: 0.0, saturation: 0.0, speed: 0.28, invert: false },
  'moiré-bold': { family: 'moiré', param1: 20, param2: 0.15, hue: 0.55, saturation: 0.5, speed: 0.42, invert: false },

  // ---------------------------------------------------------------------------
  // Fractal - Self-similar patterns (mathematical)
  // Use: Infinite zoom, complexity visualization
  // ---------------------------------------------------------------------------
  'fractal-julia': { family: 'fractal', param1: 2, param2: 0.5, hue: 0.75, saturation: 0.8, speed: 0.7, invert: false },
  'fractal-deep': { family: 'fractal', param1: 1.5, param2: 0.8, hue: 0.08, saturation: 0.7, speed: 0.42, invert: true },
};

/**
 * Curated preset names for the design system gallery.
 * These are the "blessed" patterns that should be used in production.
 */
const CURATED_PRESETS = [
  'chladni-4-5',
  'chladni-3-7',
  'chladni-6-6',
  'interference-4',
  'interference-6',
  'mandala-6',
  'mandala-8',
  'flow-calm',
  'flow-turbulent',
  'reaction-spots',
  'reaction-stripes',
  'spiral-3',      // Original speed (meditative)
  'spiral-5',      // Original speed (meditative)
  'voronoi-sparse',
  'voronoi-dense',
  'moiré-subtle',
  'moiré-bold',
  'fractal-julia',
  'fractal-deep',
] as const;

export type CuratedPresetName = typeof CURATED_PRESETS[number];

// =============================================================================
// Exports
// =============================================================================

export default PatternTile;
export { PatternMaterials, CURATED_PRESETS };
