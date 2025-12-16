# WebGL Projection Substrate (Aligned & Hardened)

> *"The scene is not the agent. The scene is how the agent appears to observers with spatial bandwidth."*

**Status**: Planning
**Priority**: P1 (Crown Jewel Foundation)
**Last Updated**: 2025-12-16
**Aligned Plans**: `plans/3d-visual-clarity.md` (illumination), `plans/projection-protocol-cultivation.md` (ExtendedTarget/ProjectionRegistry)

---

## Executive Summary

A hardened, future-proof substrate for projecting kgents agents to WebGL/Three.js that **reuses existing primitives** (illumination quality from `3d-visual-clarity`, ExtendedTarget + functor laws from `projection-protocol-cultivation`) while adding missing resilience layers. It addresses the challenges surfaced in the GestaltLive elastic upgrade:

1. **Module side effects** - Postprocessing imports hang when evaluated before Canvas
2. **WebGPU transition** - WebGL2 is default; WebGPU ships behind feature flag + telemetry
3. **Real-time streaming** - SSE with diffs, backpressure, and REST resync
4. **Quality detection** - Device capability gating aligned with illumination quality
5. **Categorical coherence** - All projections use ExtendedTarget and law verification

---

## Problem Statement

### Current Pain Points

| Issue | Impact | Root Cause |
|-------|--------|------------|
| Postprocessing import hangs | Page stuck on loading | Eager module eval and side effects before WebGL context |
| Inconsistent lighting | Visual incoherence across pages | Not using shared illumination quality from `3d-visual-clarity` |
| No WebGPU path | Future obsolescence | No feature-flagged renderer or TSL parity plan |
| SSE + 3D integration | Frame drops, stalls | No backpressure, REST resync, or jittered reconnect |
| Quality detection fragile | Poor UX on edge devices | Heuristic-only detection; no telemetry or downgrade path |
| Limited observability | Silent failures | No adapter/vendor logging, renderer error surfaces, or FPS probes |

### The Lazy Loading Discovery

The core insight from the GestaltLive fix:

```typescript
// BREAKS - module evaluated at import time, before Canvas
import { SceneEffects } from '../components/three/SceneEffects';

// WORKS - module evaluated inside Canvas context
const SceneEffects = lazy(() => import('../components/three/SceneEffects'));
```

This pattern must be **systematized**, not applied ad-hoc.

---

## Architectural Design

### The Projection Substrate Stack (Aligned)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           Agent State (Python)                               │
│                 PolyAgent[S, A, B] / CitizenPolynomial / etc.                │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ SSE (diffs, jittered reconnect) / REST snapshot
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Streaming Layer (React)                              │
│   useAgentStream() + backpressure + catch-up via REST + metrics              │
└─────────────────────────────────────┬───────────────────────────────────────┘
                                      │ State updates
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│          Projection Layer (ExtendedTarget + ProjectionRegistry)              │
│   Targets: CLI/TUI/JSON/MARIMO + SSE/WEBGL/WEBGPU/WEBXR/AUDIO (flagged)      │
└───────────────────────────┬─────────────────────────┬───────────────────────┘
                            │                         │
                   Layout[D] │                         │ Illumination[Q]
                            ▼                         ▼
┌───────────────────────────────────────┐ ┌───────────────────────────────────┐
│      Elastic Layout Primitives        │ │ Illumination Primitives (from     │
│  ElasticSplit / BottomDrawer / FAB    │ │ `3d-visual-clarity`): SceneLighting│
└───────────────────────────┬───────────┘ │ + quality constants               │
                            │             └───────────────────┬───────────────┘
                            │                                 │
                            └───────────────┬─────────────────┘
                                            ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      Render Substrate (Three.js)                             │
│     WebGL2 default; WebGPU (feature-flag + telemetry) via TSL abstraction    │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Core Principles

1. **Lazy by Default** - All Three.js components load lazily; postprocessing imports deferred inside Canvas; dispose renderers on route change
2. **Context-Aware Imports** - No Three.js side effects before Canvas; guard namespace mutation
3. **TSL-Ready, Flagged** - WebGPU behind feature flag + telemetry; GLSL stays default until parity proven
4. **Streaming-First** - SSE with diffs, jittered reconnect, backpressure, REST catch-up
5. **Quality-Gated** - Illumination quality detection (from `3d-visual-clarity`) gates effects/shadows
6. **Lawful Projections** - ExtendedTarget + ProjectionRegistry + functor law verification (`projection-protocol-cultivation`)

---

## Component Architecture

### 1. Scene Bootstrap Layer (Lazy + Disposal)

The entry point that handles lazy loading and context setup:

```typescript
// components/three/SceneBootstrap.tsx

/**
 * SceneBootstrap - Lazy-loading wrapper for 3D scenes
 *
 * Solves the "postprocessing import hang" by deferring all Three.js
 * module evaluation until the Canvas is mounted and WebGL context exists.
 */

// Static imports - React only, no Three.js
import { Suspense, lazy, type ReactNode } from 'react';
import { ErrorBoundary } from '../error/ErrorBoundary';

// Dynamic imports - evaluated inside Canvas context
const SceneLighting = lazy(() => import('./SceneLighting'));
const SceneEffects = lazy(() => import('./SceneEffects'));
const QualityMonitor = lazy(() => import('./QualityMonitor'));

interface SceneBootstrapProps {
  children: ReactNode;
  quality: IlluminationQuality;
  enableEffects?: boolean;
  enableMonitor?: boolean;
  fallback?: ReactNode;
}

export function SceneBootstrap({
  children,
  quality,
  enableEffects = true,
  enableMonitor = false,
  fallback = null,
}: SceneBootstrapProps) {
  // ensure disposal on unmount to avoid renderer leaks on route change
  useEffect(() => () => disposeRenderer(), []);

  return (
    <ErrorBoundary fallback={<SceneErrorFallback />}>
      <Suspense fallback={fallback}>
        {/* Lighting always loads */}
        <SceneLighting quality={quality} />

        {/* Effects load conditionally */}
        {enableEffects && quality !== 'minimal' && (
          <Suspense fallback={null}>
            <SceneEffects quality={quality} />
          </Suspense>
        )}

        {/* Monitor loads in dev only */}
        {enableMonitor && process.env.NODE_ENV === 'development' && (
          <Suspense fallback={null}>
            <QualityMonitor />
          </Suspense>
        )}

        {children}
      </Suspense>
    </ErrorBoundary>
  );
}
```

### 2. Renderer Abstraction (WebGPU-Ready, Flagged + Telemetry)

```typescript
// components/three/RendererProvider.tsx

import { lazy, Suspense, useState, useEffect } from 'react';
import { Canvas } from '@react-three/fiber';
import type { RootState } from '@react-three/fiber';

// Future: Dynamic import of WebGPU renderer
async function createRenderer(canvas: HTMLCanvasElement): Promise<THREE.WebGLRenderer | WebGPURenderer> {
  // feature flag + telemetry guard
  if (flags.webgpuEnabled && navigator.gpu) {
    try {
      const adapter = await navigator.gpu.requestAdapter();
      if (adapter) {
        const { WebGPURenderer } = await import('three/webgpu');
        const renderer = new WebGPURenderer({ canvas, antialias: true });
        await renderer.init();
        metrics.logRenderer({ target: 'webgpu', adapter: adapter.name });
        return renderer;
      }
    } catch (err) {
      metrics.logRendererError({ target: 'webgpu', error: String(err) });
      // fall through to WebGL2
    }
  }

  const renderer = new THREE.WebGLRenderer({
    canvas,
    antialias: true,
    powerPreference: 'high-performance',
  });
  metrics.logRenderer({ target: 'webgl2', vendor: renderer.getContext().getParameter(renderer.getContext().UNMASKED_VENDOR_WEBGL) });
  return renderer;
}

interface RendererProviderProps {
  children: React.ReactNode;
  shadows?: boolean;
  className?: string;
}

export function RendererProvider({ children, shadows = true, className }: RendererProviderProps) {
  return (
    <Canvas
      gl={createRenderer}
      shadows={shadows}
      className={className}
      camera={{ position: [0, 0, 25], fov: 55 }}
    >
      {children}
    </Canvas>
  );
}
```

### 3. Agent Streaming Integration (Diff + Backpressure + Resync)

```typescript
// hooks/useAgentScene.ts

/**
 * useAgentScene - Connects agent SSE stream to 3D scene state
 *
 * Handles:
 * - SSE connection lifecycle
 * - State diffing for animations
 * - Graceful degradation on disconnect
 */

import { useState, useEffect, useRef, useCallback } from 'react';
import { calculateAnimationChanges } from '../utils/topologyDiff';
import type { AgentState, EntityAnimationState } from '../api/types';

interface AgentSceneOptions<T extends AgentState> {
  /** SSE endpoint URL */
  streamUrl: string;
  /** Initial state (from REST snapshot) */
  initialState: T | null;
  /** Timeout for connection (ms) */
  connectionTimeout?: number;
  /** Enable animation state tracking */
  enableAnimations?: boolean;
}

interface AgentSceneResult<T extends AgentState> {
  /** Current agent state */
  state: T | null;
  /** Entity animation states (for fade/pulse effects) */
  animations: Map<string, EntityAnimationState>;
  /** Connection status */
  status: 'connecting' | 'connected' | 'reconnecting' | 'error' | 'disconnected';
  /** Error message if any */
  error: string | null;
  /** Reconnect function */
  reconnect: () => void;
}

export function useAgentScene<T extends AgentState>(
  options: AgentSceneOptions<T>
): AgentSceneResult<T> {
  const {
    streamUrl,
    initialState,
    connectionTimeout = 10000,
    enableAnimations = true,
  } = options;

  const [state, setState] = useState<T | null>(initialState);
  const [animations, setAnimations] = useState<Map<string, EntityAnimationState>>(new Map());
  const [status, setStatus] = useState<AgentSceneResult<T>['status']>('connecting');
  const [error, setError] = useState<string | null>(null);
  const buffer = useRef<AgentSSEEvent[]>([]);
  const maxBuffer = 256; // backpressure cap

  const eventSourceRef = useRef<EventSource | null>(null);
  const prevEntitiesRef = useRef<T['entities'] | null>(null);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectJitter = useRef(0);

  const flush = useCallback(() => {
    if (!buffer.current.length) return;
    const batch = buffer.current.splice(0, buffer.current.length);
    for (const evt of batch) {
      if (evt.type === 'snapshot') {
        setState(evt.data as T);
        prevEntitiesRef.current = (evt.data as any).entities ?? null;
      } else if (evt.type === 'update') {
        const next = applyDiff(prevEntitiesRef.current, evt.data);
        prevEntitiesRef.current = next?.entities ?? null;
        setState(next as T);
      }
    }
  }, []);

  const connect = useCallback(() => {
    // Clean up existing connection
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    setStatus('connecting');
    setError(null);

    // Set connection timeout
    timeoutRef.current = setTimeout(() => {
      if (status === 'connecting') {
        setError('Connection timeout');
        setStatus('error');
      }
    }, connectionTimeout);

    // Create EventSource
    const eventSource = new EventSource(streamUrl);
    eventSourceRef.current = eventSource;

    eventSource.onopen = () => {
      clearTimeout(timeoutRef.current!);
      setStatus('connected');
      setError(null);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data) as AgentSSEEvent;

        // backpressure: drop oldest when buffer full
        if (buffer.current.length >= maxBuffer) buffer.current.shift();
        buffer.current.push(data);
        flush();

        // Calculate animations if enabled
        if (
          enableAnimations &&
          prevEntitiesRef.current &&
          (data as any).data?.entities
        ) {
          const changes = calculateAnimationChanges(
            prevEntitiesRef.current,
            (data as any).data.entities
          );
          if (changes.size > 0) {
            setAnimations(prev => applyAnimationChanges(prev, changes));
          }
        }
      } catch (err) {
        console.error('Failed to parse SSE message:', err);
      }
    };

    eventSource.onerror = () => {
      if (eventSource.readyState === EventSource.CLOSED) {
        setStatus('disconnected');
      } else {
        setStatus('reconnecting');
        reconnectJitter.current = Math.min(reconnectJitter.current + 500, 4000);
        setTimeout(connect, reconnectJitter.current + Math.random() * 500);
      }
    };
  }, [streamUrl, connectionTimeout, enableAnimations, status]);

  // Initial connection
  useEffect(() => {
    connect();
    return () => {
      eventSourceRef.current?.close();
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [connect]);

  return {
    state,
    animations,
    status,
    error,
    reconnect: connect,
  };
}
```

### 4. Quality Detection Service (Reuse `3d-visual-clarity`)

```typescript
// services/qualityDetection.ts

/**
 * Quality Detection Service
 *
 * Detects device capabilities to determine appropriate illumination quality.
 * Uses multiple signals: WebGL capabilities, battery status, memory, etc.
 */

// Use the canonical IlluminationQuality + constants from plans/3d-visual-clarity.md
export type IlluminationQuality = 'minimal' | 'standard' | 'high' | 'cinematic';

interface DeviceCapabilities {
  webglVersion: 1 | 2 | null;
  webgpuSupported: boolean;
  maxTextureSize: number;
  maxSamples: number;
  renderer: string;
  vendor: string;
  memoryMB: number | null;
  batteryLevel: number | null;
  batteryCharging: boolean | null;
  prefersReducedMotion: boolean;
  devicePixelRatio: number;
}

async function detectCapabilities(): Promise<DeviceCapabilities> {
  const canvas = document.createElement('canvas');
  const gl = canvas.getContext('webgl2') || canvas.getContext('webgl');

  let webglVersion: 1 | 2 | null = null;
  let maxTextureSize = 0;
  let maxSamples = 0;
  let renderer = 'unknown';
  let vendor = 'unknown';

  if (gl) {
    webglVersion = gl instanceof WebGL2RenderingContext ? 2 : 1;
    maxTextureSize = gl.getParameter(gl.MAX_TEXTURE_SIZE);
    maxSamples = gl.getParameter(gl.MAX_SAMPLES) || 0;

    const debugInfo = gl.getExtension('WEBGL_debug_renderer_info');
    if (debugInfo) {
      renderer = gl.getParameter(debugInfo.UNMASKED_RENDERER_WEBGL);
      vendor = gl.getParameter(debugInfo.UNMASKED_VENDOR_WEBGL);
    }
  }

  // Check WebGPU
  let webgpuSupported = false;
  if (navigator.gpu) {
    const adapter = await navigator.gpu.requestAdapter();
    webgpuSupported = adapter !== null;
  }

  // Check battery
  let batteryLevel: number | null = null;
  let batteryCharging: boolean | null = null;
  if ('getBattery' in navigator) {
    try {
      const battery = await (navigator as any).getBattery();
      batteryLevel = battery.level;
      batteryCharging = battery.charging;
    } catch {}
  }

  // Check memory
  let memoryMB: number | null = null;
  if ('deviceMemory' in navigator) {
    memoryMB = (navigator as any).deviceMemory * 1024;
  }

  // Check motion preference
  const prefersReducedMotion = window.matchMedia(
    '(prefers-reduced-motion: reduce)'
  ).matches;

  return {
    webglVersion,
    webgpuSupported,
    maxTextureSize,
    maxSamples,
    renderer,
    vendor,
    memoryMB,
    batteryLevel,
    batteryCharging,
    prefersReducedMotion,
    devicePixelRatio: window.devicePixelRatio,
  };
}

export function determineQuality(caps: DeviceCapabilities): IlluminationQuality {
  // Immediate disqualifiers
  if (!caps.webglVersion) return 'minimal';
  if (caps.prefersReducedMotion) return 'minimal';
  if (caps.batteryCharging === false && (caps.batteryLevel || 1) < 0.2) return 'minimal';

  // Low-end GPU detection
  const lowEndPatterns = ['Mali-4', 'Adreno 3', 'Intel HD 4', 'Intel UHD 6'];
  if (lowEndPatterns.some(p => caps.renderer.includes(p))) return 'minimal';

  // High-end detection
  const highEndPatterns = ['RTX', 'RX 6', 'RX 7', 'M1', 'M2', 'M3', 'Apple GPU'];
  const isHighEnd = highEndPatterns.some(p => caps.renderer.includes(p));

  // Texture size heuristics
  if (caps.maxTextureSize >= 16384 && isHighEnd) {
    return caps.devicePixelRatio >= 2 ? 'cinematic' : 'high';
  }

  if (caps.maxTextureSize >= 8192) {
    return 'standard';
  }

  return 'minimal';
}

// Singleton with caching
let cachedQuality: IlluminationQuality | null = null;
let cachedCapabilities: DeviceCapabilities | null = null;

export async function getIlluminationQuality(): Promise<IlluminationQuality> {
  if (cachedQuality) return cachedQuality;

  cachedCapabilities = await detectCapabilities();
  cachedQuality = determineQuality(cachedCapabilities);

  metrics.logQuality({
    quality: cachedQuality,
    renderer: cachedCapabilities.renderer,
    maxTexture: cachedCapabilities.maxTextureSize,
    webgpu: cachedCapabilities.webgpuSupported,
    dpr: cachedCapabilities.devicePixelRatio,
  });

  return cachedQuality;
}

export function getCapabilities(): DeviceCapabilities | null {
  return cachedCapabilities;
}

export function overrideQuality(quality: IlluminationQuality | null): void {
  if (quality === null) {
    // Restore auto-detection
    cachedQuality = cachedCapabilities ? determineQuality(cachedCapabilities) : null;
  } else {
    cachedQuality = quality;
  }
}
```

---

## TSL Shader Strategy (WebGPU Future-Proofing)

### Current State: GLSL

Current shaders use GLSL via `@react-three/postprocessing`:

```glsl
// Current SSAO shader (GLSL)
uniform sampler2D tDiffuse;
uniform sampler2D tDepth;
varying vec2 vUv;

void main() {
  float depth = texture2D(tDepth, vUv).r;
  // ... SSAO calculation
}
```

### Future State: TSL (Three.js Shading Language)

TSL is renderer-agnostic—same code works on WebGL and WebGPU:

```typescript
// Future SSAO shader (TSL)
import { Fn, texture, uv, uniform } from 'three/tsl';

const ssaoPass = Fn(() => {
  const diffuse = texture(diffuseTexture, uv());
  const depth = texture(depthTexture, uv());

  // SSAO calculation in TSL
  const ao = computeAO(depth, uv());

  return diffuse.mul(ao);
});
```

### Migration Path

1. **Phase 1 (Current)**: Use `@react-three/postprocessing` with lazy loading; GLSL is default
2. **Phase 2 (Canary)**: Add TSL-based effects alongside GLSL; gated by `webgpuEnabled` flag; telemetry on failures
3. **Phase 3 (Stable)**: Detect WebGPU adapter + TSL parity test suite; opt-in on Chrome/Edge stable only
4. **Phase 4 (Optional)**: Deprecate GLSL effects once TSL passes parity on all targets (including Safari when non-experimental)

---

## Streaming Architecture

### SSE Event Types (Versioned)

```typescript
// Standardized SSE event types for agent visualization

interface AgentSSEEvent {
  type: 'snapshot' | 'update' | 'heartbeat' | 'error';
  timestamp: number;
  version: number; // for payload evolution
  data: unknown;
}

interface SnapshotEvent extends AgentSSEEvent {
  type: 'snapshot';
  data: {
    entities: Entity[];
    connections: Connection[];
    metadata: Record<string, unknown>;
  };
}

interface UpdateEvent extends AgentSSEEvent {
  type: 'update';
  data: {
    added: Entity[];
    removed: string[];  // Entity IDs
    changed: Partial<Entity>[];  // Diffs
  };
}

interface HeartbeatEvent extends AgentSSEEvent {
  type: 'heartbeat';
  data: {
    serverTime: number;
    clientCount: number;
    streamLagMs?: number; // for backpressure monitoring
  };
}
```

### Diff-Based Updates + Backpressure

For large agent populations, send diffs instead of full state:

```python
# Backend: Compute minimal diff
def compute_diff(prev: TownState, next: TownState) -> UpdateEvent:
    added = [c for c in next.citizens if c.id not in prev_ids]
    removed = [c.id for c in prev.citizens if c.id not in next_ids]
    changed = [
        {"id": c.id, **diff_citizen(prev_map[c.id], c)}
        for c in next.citizens
        if c.id in prev_ids and c != prev_map[c.id]
    ]
    return UpdateEvent(added=added, removed=removed, changed=changed)

# Enforce ring buffer on server
STREAM_BUFFER = 512  # drop oldest beyond this
```

### Reconnect / Catch-up Policy

- Jittered backoff: 0.5s → 4s with ±500ms jitter
- On reconnect, fetch REST snapshot if `lastEventId` missing or heartbeat gap > 10s
- If buffer overflows, emit `error` event with `reason="backpressure"`; client downgrades quality and coalesces updates

---

## Performance Budget (Measured & Telemetry-Aware)

| Quality | Max Entities | Target FPS | Shadow Maps | Post-Processing |
|---------|-------------|------------|-------------|-----------------|
| minimal | 1000 | 60 | None | None |
| standard | 500 | 60 | 1024px | None |
| high | 300 | 60 | 2048px | SSAO |
| cinematic | 150 | 30 | 4096px | SSAO + Bloom |

### Monitoring

```typescript
// Automatic quality downgrade on frame drops; emits telemetry
function useAdaptiveQuality(targetFps: number = 55) {
  const [quality, setQuality] = useState<IlluminationQuality>('standard');
  const fpsBuffer = useRef<number[]>([]);

  useFrame((state, delta) => {
    const fps = 1 / delta;
    fpsBuffer.current.push(fps);

    if (fpsBuffer.current.length >= 60) {
      const avgFps = fpsBuffer.current.reduce((a, b) => a + b) / 60;
      fpsBuffer.current = [];

      if (avgFps < targetFps * 0.8 && quality !== 'minimal') {
        // Downgrade quality
        const levels: IlluminationQuality[] = ['cinematic', 'high', 'standard', 'minimal'];
        const currentIdx = levels.indexOf(quality);
        if (currentIdx < levels.length - 1) {
          setQuality(levels[currentIdx + 1]);
          metrics.logQualityDowngrade({ from: quality, to: levels[currentIdx + 1], avgFps });
        }
      }

      metrics.logFpsSample({ avgFps, quality });
    }
  });

  return quality;
}

// GPU reset detection
window.addEventListener('webglcontextlost', () => metrics.logRendererError({ target: 'webgl2', error: 'context lost' }));
```

---

## Observability & QA

- **Renderer telemetry**: record target (webgl2/webgpu), adapter/vendor, init success/failure, context loss.
- **Quality telemetry**: log detected quality, downgrades with FPS sample, devicePixelRatio, maxTextureSize.
- **Streaming telemetry**: heartbeats received, reconnect count, buffer drops, backpressure errors.
- **Dashboards**: minimal Grafana/Looker slice for FPS distribution and renderer failures by device class.
- **Test matrix**: synthetic low-end (1 GB GPU, DPR 1), mid (integrated), high-end (dedicated), mobile Chrome/Safari; Firefox with `dom.webgpu.enabled` for tracking only.

---

## Implementation Phases (Aligned + Hardened)

### Track A: Stability & Observability (Week 1-2)

- [ ] Create `SceneBootstrap` with lazy loading + renderer disposal
- [ ] Migrate SceneEffects to lazy import in all pages
- [ ] Wire `useAgentScene` with backpressure, jittered reconnect, REST catch-up
- [ ] Implement quality detection service reusing `3d-visual-clarity` constants; add telemetry
- [ ] Add FPS/memory logging + context-lost handler

### Track B: Standardization & Lawfulness (Week 3-4)

- [ ] Wire `RendererProvider` with WebGPU feature flag + telemetry
- [ ] Standardize SSE event types (versioned) across agents
- [ ] Integrate ExtendedTarget + ProjectionRegistry for WEBGL/WEBGPU/WEBXR/AUDIO placeholders
- [ ] Add adaptive quality hook + downgrade telemetry
- [ ] Add law verification to scene projections (ExtendedTarget)

### Track C: WebGPU/TSL Exploration (Week 5-6, Flagged)

- [ ] Research TSL shader patterns; implement dual GLSL/TSL SSAO/Bloom
- [ ] Add WebGPU adapter gating; enable only on Chrome/Edge stable; log failures
- [ ] Canary tests on Chrome Canary/Edge Dev; record adapter/vendor success matrix
- [ ] Document parity/rollback checklist

### Track D: Testing & Hardening (Week 7-8)

- [ ] E2E tests for mobile quality detection (low DPR/VRAM profiles)
- [ ] SSE reconnection + backpressure stress tests (buffer overflow, loss)
- [ ] Memory/renderer disposal soak tests (route churn)
- [ ] Cross-browser matrix: Chrome/Edge stable, Firefox (flag), Safari 18 (experimental)
- [ ] Visual regression for quality tiers (minimal/standard/high/cinematic)

---

## Success Criteria

1. **No import hangs** - All pages load within 3s; no renderer leaks on route change
2. **Graceful degradation** - Works on 5-year-old phones (minimal quality) with auto-downgrade on FPS drop
3. **Performance SLA** - Standard quality ≥60 FPS on 2020+ laptops; telemetry proves it
4. **SSE resilience** - Jittered reconnect + backpressure; REST catch-up after heartbeat gap; buffer overflow handled
5. **WebGPU readiness** - Feature-flagged; adapter/vendor logged; parity suite passes on Chrome/Edge stable before enabling
6. **Categorical coherence** - All projections use ExtendedTarget + ProjectionRegistry; functor law tests in place
7. **Observability** - Renderer errors, context loss, and quality downgrades are logged and surfaced in UI/devtools

---

## Open Questions

1. **TSL timing** - When will R3F officially support TSL materials? (track R3F v9 async renderer readiness)
2. **WebGPU Safari** - Safari 18 lists WebGPU as experimental; keep disabled until adapters pass parity
3. **Mobile WebGPU** - iOS/Android timelines still unclear; keep WebGPU desktop-only until stable
4. **Postprocessing alternatives** - Do we need custom TSL effects or wait for @react-three/postprocessing parity?
5. **OffscreenCanvas/Workers** - Do we ship worker-based rendering for SSR/headless/throttled tabs?

---

## References

### Research Sources

- [R3F Scaling Performance](https://r3f.docs.pmnd.rs/advanced/scaling-performance) - Official performance guide
- [R3F v9 Migration Guide](https://r3f.docs.pmnd.rs/tutorials/v9-migration-guide) - WebGPU async renderer
- [TSL Field Guide](https://blog.maximeheckel.com/posts/field-guide-to-tsl-and-webgpu/) - Maxime Heckel's TSL tutorial
- [R3F WebGPU Starter](https://github.com/ektogamat/r3f-webgpu-starter) - Reference implementation
- [Codrops Performance Guide](https://tympanus.net/codrops/2025/02/11/building-efficient-three-js-scenes-optimize-performance-while-maintaining-quality/) - 2025 best practices
- [Shopify WebGPU Future](https://shopify.engineering/webgpu-skia-web-graphics) - React Native WebGPU

### Internal Documentation

- `spec/protocols/projection.md` - Projection Protocol specification
- `docs/skills/3d-lighting-patterns.md` - Illumination quality patterns
- `plans/web-refactor/layout-projection-functor.md` - Layout functor

---

*"The goal is not to build a 3D engine. The goal is to make agents visible to observers with spatial bandwidth."*
