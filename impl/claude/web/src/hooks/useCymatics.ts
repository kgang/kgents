/**
 * useCymatics - State management for cymatics visualization
 *
 * Manages vibration sources, computes pattern stability, and provides
 * utilities for creating dynamic cymatics visualizations.
 *
 * @see impl/claude/web/src/components/three/CymaticsField.tsx
 * @see impl/claude/agents/i/reactive/animation/cymatics.py
 */

import { useState, useCallback, useMemo, useEffect, useRef } from 'react';
import type {
  VibrationSource,
  ChladniPattern,
} from '../types/emergence';

// =============================================================================
// Types
// =============================================================================

export interface UseCymaticsOptions {
  /** Initial vibration sources */
  initialSources?: VibrationSource[];
  /** Maximum number of sources allowed */
  maxSources?: number;
  /** Grid resolution for pattern computation */
  resolution?: number;
  /** Whether to auto-compute patterns on source change */
  autoCompute?: boolean;
  /** Stability threshold for "harmonic" classification */
  harmonyThreshold?: number;
}

export interface UseCymaticsReturn {
  /** Current vibration sources */
  sources: VibrationSource[];
  /** Add a vibration source */
  addSource: (source: Omit<VibrationSource, 'phase'> & { phase?: number }) => void;
  /** Remove a source at position */
  removeSource: (position: [number, number], tolerance?: number) => boolean;
  /** Clear all sources */
  clearSources: () => void;
  /** Set all sources at once */
  setSources: (sources: VibrationSource[]) => void;
  /** Current pattern stability (0-1) */
  stability: number;
  /** Whether pattern is considered harmonic */
  isHarmonic: boolean;
  /** Current pattern (if computed) */
  pattern: ChladniPattern | null;
  /** Manually trigger pattern computation */
  computePattern: (time?: number) => ChladniPattern;
  /** Create harmonic ring of sources */
  createHarmonicRing: (count: number, radius?: number, frequency?: number) => void;
  /** Create dissonant sources for conflict visualization */
  createDissonantSources: (frequencies: number[]) => void;
  /** Interpolate sources toward target over time */
  morphSources: (
    targetSources: VibrationSource[],
    duration: number,
    onComplete?: () => void
  ) => void;
  /** Stop any ongoing morphing */
  stopMorph: () => void;
  /** Whether currently morphing */
  isMorphing: boolean;
}

// =============================================================================
// Helper Functions
// =============================================================================

/**
 * Calculate wave amplitude at a point from all sources.
 */
function calculateAmplitudeAt(
  x: number,
  y: number,
  time: number,
  sources: VibrationSource[]
): number {
  let total = 0;
  for (const source of sources) {
    const dx = x - source.position[0];
    const dy = y - source.position[1];
    const r = Math.sqrt(dx * dx + dy * dy);

    const k = 2 * Math.PI * source.frequency * 0.5;
    const distanceFactor = Math.exp(-source.decay * r);
    const wave =
      source.amplitude *
      distanceFactor *
      Math.sin(2 * Math.PI * source.frequency * time - k * r + source.phase);

    total += wave;
  }
  return total;
}

/**
 * Calculate pattern stability from sources.
 */
function calculateStability(sources: VibrationSource[]): number {
  if (sources.length === 0) return 0;
  if (sources.length === 1) return 1;

  const frequencies = sources.map((s) => s.frequency);
  const meanFreq = frequencies.reduce((a, b) => a + b, 0) / frequencies.length;
  const variance =
    frequencies.reduce((sum, f) => sum + Math.pow(f - meanFreq, 2), 0) /
    frequencies.length;

  const maxVariance = meanFreq * meanFreq;
  const normalizedVariance = Math.min(variance / maxVariance, 1);
  return 1 - normalizedVariance;
}

/**
 * Compute full Chladni pattern from sources.
 */
function computeChladniPattern(
  sources: VibrationSource[],
  resolution: number,
  time: number
): ChladniPattern {
  if (sources.length === 0) {
    return {
      nodes: [],
      antinodes: [],
      minAmplitude: 0,
      maxAmplitude: 0,
      stability: 0,
    };
  }

  const grid: number[][] = [];
  let minAmp = Infinity;
  let maxAmp = -Infinity;

  // Compute amplitude grid
  for (let j = 0; j < resolution; j++) {
    const row: number[] = [];
    const y = -1 + (2 * j) / (resolution - 1);

    for (let i = 0; i < resolution; i++) {
      const x = -1 + (2 * i) / (resolution - 1);
      const amp = calculateAmplitudeAt(x, y, time, sources);
      row.push(amp);
      minAmp = Math.min(minAmp, amp);
      maxAmp = Math.max(maxAmp, amp);
    }

    grid.push(row);
  }

  // Find nodes (local maxima) and antinodes (local minima)
  const nodes: Array<[number, number]> = [];
  const antinodes: Array<[number, number]> = [];

  for (let j = 1; j < resolution - 1; j++) {
    for (let i = 1; i < resolution - 1; i++) {
      const center = grid[j][i];
      const neighbors = [
        grid[j - 1][i],
        grid[j + 1][i],
        grid[j][i - 1],
        grid[j][i + 1],
      ];

      const x = -1 + (2 * i) / (resolution - 1);
      const y = -1 + (2 * j) / (resolution - 1);

      if (neighbors.every((n) => center >= n)) {
        nodes.push([x, y]);
      }

      if (neighbors.every((n) => center <= n)) {
        antinodes.push([x, y]);
      }
    }
  }

  return {
    nodes,
    antinodes,
    minAmplitude: minAmp === Infinity ? 0 : minAmp,
    maxAmplitude: maxAmp === -Infinity ? 0 : maxAmp,
    stability: calculateStability(sources),
  };
}

/**
 * Linearly interpolate between two source configurations.
 */
function lerpSources(
  from: VibrationSource[],
  to: VibrationSource[],
  t: number
): VibrationSource[] {
  const maxLen = Math.max(from.length, to.length);
  const result: VibrationSource[] = [];

  for (let i = 0; i < maxLen; i++) {
    const fromSource = from[i] || {
      frequency: 0,
      amplitude: 0,
      phase: 0,
      position: [0, 0] as [number, number],
      decay: 0.5,
    };
    const toSource = to[i] || {
      frequency: 0,
      amplitude: 0,
      phase: 0,
      position: [0, 0] as [number, number],
      decay: 0.5,
    };

    // If target doesn't exist, fade out; if source doesn't exist, fade in
    const ampMult = from[i] && to[i] ? 1 : from[i] ? 1 - t : t;

    result.push({
      frequency: fromSource.frequency + (toSource.frequency - fromSource.frequency) * t,
      amplitude:
        (fromSource.amplitude + (toSource.amplitude - fromSource.amplitude) * t) * ampMult,
      phase: fromSource.phase + (toSource.phase - fromSource.phase) * t,
      position: [
        fromSource.position[0] + (toSource.position[0] - fromSource.position[0]) * t,
        fromSource.position[1] + (toSource.position[1] - fromSource.position[1]) * t,
      ],
      decay: fromSource.decay + (toSource.decay - fromSource.decay) * t,
    });
  }

  // Filter out zero-amplitude sources
  return result.filter((s) => s.amplitude > 0.01);
}

// =============================================================================
// Main Hook
// =============================================================================

export function useCymatics(options: UseCymaticsOptions = {}): UseCymaticsReturn {
  const {
    initialSources = [],
    maxSources = 8,
    resolution = 32,
    autoCompute = false,
    harmonyThreshold = 0.8,
  } = options;

  // State
  const [sources, setSourcesState] = useState<VibrationSource[]>(initialSources);
  const [pattern, setPattern] = useState<ChladniPattern | null>(null);
  const [isMorphing, setIsMorphing] = useState(false);

  // Refs for animation
  const morphAnimationRef = useRef<number | null>(null);
  const morphStartRef = useRef<VibrationSource[]>([]);
  const morphEndRef = useRef<VibrationSource[]>([]);
  const morphStartTimeRef = useRef<number>(0);
  const morphDurationRef = useRef<number>(0);
  const morphCallbackRef = useRef<(() => void) | undefined>(undefined);

  // Computed values
  const stability = useMemo(() => calculateStability(sources), [sources]);
  const isHarmonic = stability >= harmonyThreshold;

  // Auto-compute pattern when sources change
  useEffect(() => {
    if (autoCompute) {
      setPattern(computeChladniPattern(sources, resolution, 0));
    }
  }, [sources, autoCompute, resolution]);

  // Add source
  const addSource = useCallback(
    (source: Omit<VibrationSource, 'phase'> & { phase?: number }) => {
      setSourcesState((prev) => {
        if (prev.length >= maxSources) {
          console.warn(`Maximum sources (${maxSources}) reached`);
          return prev;
        }
        return [
          ...prev,
          {
            ...source,
            phase: source.phase ?? 0,
          },
        ];
      });
    },
    [maxSources]
  );

  // Remove source at position
  const removeSource = useCallback(
    (position: [number, number], tolerance = 0.1): boolean => {
      let removed = false;
      setSourcesState((prev) => {
        const index = prev.findIndex((s) => {
          const dx = s.position[0] - position[0];
          const dy = s.position[1] - position[1];
          return Math.sqrt(dx * dx + dy * dy) <= tolerance;
        });

        if (index >= 0) {
          removed = true;
          return [...prev.slice(0, index), ...prev.slice(index + 1)];
        }
        return prev;
      });
      return removed;
    },
    []
  );

  // Clear all sources
  const clearSources = useCallback(() => {
    setSourcesState([]);
  }, []);

  // Set all sources
  const setSources = useCallback(
    (newSources: VibrationSource[]) => {
      setSourcesState(newSources.slice(0, maxSources));
    },
    [maxSources]
  );

  // Compute pattern manually
  const computePattern = useCallback(
    (time = 0): ChladniPattern => {
      const computed = computeChladniPattern(sources, resolution, time);
      setPattern(computed);
      return computed;
    },
    [sources, resolution]
  );

  // Create harmonic ring
  const createHarmonicRing = useCallback(
    (count: number, radius = 0.5, frequency = 2.0) => {
      const newSources: VibrationSource[] = [];
      for (let i = 0; i < Math.min(count, maxSources); i++) {
        const angle = (2 * Math.PI * i) / count;
        newSources.push({
          frequency,
          amplitude: 1.0,
          phase: 0,
          position: [radius * Math.cos(angle), radius * Math.sin(angle)],
          decay: 0.5,
        });
      }
      setSourcesState(newSources);
    },
    [maxSources]
  );

  // Create dissonant sources
  const createDissonantSources = useCallback(
    (frequencies: number[]) => {
      const count = Math.min(frequencies.length, maxSources);
      const spread = 0.3;

      const newSources: VibrationSource[] = frequencies.slice(0, count).map((freq, i) => ({
        frequency: freq,
        amplitude: 1.0,
        phase: 0,
        position: [
          count > 1 ? -spread + (2 * spread * i) / (count - 1) : 0,
          0,
        ] as [number, number],
        decay: 0.5,
      }));

      setSourcesState(newSources);
    },
    [maxSources]
  );

  // Morph sources over time
  const morphSources = useCallback(
    (
      targetSources: VibrationSource[],
      duration: number,
      onComplete?: () => void
    ) => {
      // Cancel any existing morph
      if (morphAnimationRef.current) {
        cancelAnimationFrame(morphAnimationRef.current);
      }

      // Store morph parameters
      morphStartRef.current = [...sources];
      morphEndRef.current = targetSources;
      morphStartTimeRef.current = performance.now();
      morphDurationRef.current = duration;
      morphCallbackRef.current = onComplete;
      setIsMorphing(true);

      // Animation loop
      const animate = (currentTime: number) => {
        const elapsed = currentTime - morphStartTimeRef.current;
        const t = Math.min(elapsed / morphDurationRef.current, 1);

        // Ease in-out curve
        const easedT = t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2;

        const interpolated = lerpSources(
          morphStartRef.current,
          morphEndRef.current,
          easedT
        );
        setSourcesState(interpolated);

        if (t < 1) {
          morphAnimationRef.current = requestAnimationFrame(animate);
        } else {
          setIsMorphing(false);
          morphAnimationRef.current = null;
          morphCallbackRef.current?.();
        }
      };

      morphAnimationRef.current = requestAnimationFrame(animate);
    },
    [sources]
  );

  // Stop morphing
  const stopMorph = useCallback(() => {
    if (morphAnimationRef.current) {
      cancelAnimationFrame(morphAnimationRef.current);
      morphAnimationRef.current = null;
      setIsMorphing(false);
    }
  }, []);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (morphAnimationRef.current) {
        cancelAnimationFrame(morphAnimationRef.current);
      }
    };
  }, []);

  return {
    sources,
    addSource,
    removeSource,
    clearSources,
    setSources,
    stability,
    isHarmonic,
    pattern,
    computePattern,
    createHarmonicRing,
    createDissonantSources,
    morphSources,
    stopMorph,
    isMorphing,
  };
}

// =============================================================================
// Exports
// =============================================================================

export default useCymatics;
