/**
 * VitalityOperad — Constraint Grammar for Procedural Micro-Interactions
 *
 * Inspired by Wave Function Collapse: we define VitalityTokens (tiles),
 * Constraints (adjacency rules), and collapse them into coherent animations
 * that feel organic, varied, and alive.
 *
 * "The proof IS the decision. The mark IS the witness."
 *
 * Key insight: Instead of uniform breathing, we compose constrained tokens
 * that create emergent vitality from simple rules.
 *
 * @see https://www.boristhebrave.com/2020/04/13/wave-function-collapse-explained/
 * @see impl/claude/agents/operad/core.py (Python Operad pattern)
 */

import { useCallback, useEffect, useMemo, useRef, useState } from 'react';

// =============================================================================
// Core Types — The Tokens
// =============================================================================

/**
 * VitalityToken — Atomic unit of life on the page
 *
 * Each token is a small, focused animation that can compose with others.
 * Tokens have constraints: some can coexist, others would fight for attention.
 */
export type VitalityTokenType =
  | 'firefly' // Ambient glow that appears and fades
  | 'shimmer' // Micro-brightness fluctuation
  | 'drift' // Slow positional float
  | 'pulse' // Single heartbeat
  | 'ripple' // Expanding ring
  | 'rest'; // No animation (token exists but dormant)

export interface VitalityToken {
  id: string;
  type: VitalityTokenType;
  position: { x: number; y: number }; // 0-1 normalized
  intensity: number; // 0-1
  phase: number; // 0-1 (where in its cycle)
  lifetime: number; // ms remaining
  born: number; // timestamp
}

// =============================================================================
// Constraint System — The Grammar
// =============================================================================

/**
 * Adjacency constraints: which tokens can coexist within a distance threshold.
 *
 * WFC insight: "After doing that, it looks like we might benefit from doing
 * more constraint propagation."
 *
 * Our constraints prevent visual clutter:
 * - Two fireflies too close = fight for attention (bad)
 * - Shimmer + firefly = enhances the glow (good)
 * - Multiple drifts = confusing motion (bad)
 */
const ADJACENCY_CONSTRAINTS: Record<
  VitalityTokenType,
  { compatible: VitalityTokenType[]; minDistance: number }
> = {
  firefly: {
    compatible: ['shimmer', 'rest', 'pulse'],
    minDistance: 0.15, // Keep fireflies 15% apart
  },
  shimmer: {
    compatible: ['firefly', 'drift', 'rest', 'pulse', 'shimmer'],
    minDistance: 0.05, // Shimmers can cluster
  },
  drift: {
    compatible: ['shimmer', 'rest', 'pulse'],
    minDistance: 0.25, // Drifts need space
  },
  pulse: {
    compatible: ['shimmer', 'rest', 'firefly', 'drift'],
    minDistance: 0.1,
  },
  ripple: {
    compatible: ['rest'], // Ripples are attention-demanding
    minDistance: 0.3,
  },
  rest: {
    compatible: ['firefly', 'shimmer', 'drift', 'pulse', 'ripple', 'rest'],
    minDistance: 0,
  },
};

/**
 * Entropy weights — probability of each token type appearing.
 * Lower entropy = more likely to be chosen in WFC collapse.
 *
 * STARK BIOME: "Stillness, then life" — most tokens are rest,
 * with occasional bursts of vitality.
 */
const ENTROPY_WEIGHTS: Record<VitalityTokenType, number> = {
  rest: 0.6, // 60% stillness
  shimmer: 0.2, // 20% subtle shimmer
  firefly: 0.08, // 8% fireflies
  drift: 0.05, // 5% drift
  pulse: 0.05, // 5% pulse
  ripple: 0.02, // 2% ripple (rare, earned)
};

// =============================================================================
// Operations — The Operad
// =============================================================================

/**
 * VitalityOperation — Composable animation operations
 *
 * Mirrors impl/claude/agents/operad/core.py:
 * "Operations are the generators of the composition grammar.
 *  They specify how agents combine."
 */
// Note: This interface is kept for documentation but operations are
// implemented directly in VITALITY_OPERAD for simplicity.
// interface VitalityOperation<T> {
//   name: string;
//   arity: number;
//   apply: (...tokens: VitalityToken[]) => T;
// }

/**
 * Core operations in our vitality operad:
 * - spawn: Create a new token respecting constraints
 * - compose: Merge two tokens (for overlapping effects)
 * - decay: Reduce token lifetime
 * - propagate: Spread constraint updates
 */
const VITALITY_OPERAD = {
  /**
   * Spawn a new token using WFC-inspired selection.
   * Least entropy heuristic: choose from tokens with fewest valid options.
   */
  spawn: (
    existingTokens: VitalityToken[],
    _bounds: { width: number; height: number }
  ): VitalityToken | null => {
    // Pick a random position
    const x = Math.random();
    const y = Math.random();
    const pos = { x, y };

    // Calculate valid token types at this position (constraint propagation)
    const validTypes = getValidTokenTypes(pos, existingTokens);

    if (validTypes.length === 0) return null; // Contradiction — no valid tokens

    // Weighted random selection based on entropy
    const totalWeight = validTypes.reduce((sum, t) => sum + ENTROPY_WEIGHTS[t], 0);
    let roll = Math.random() * totalWeight;

    for (const type of validTypes) {
      roll -= ENTROPY_WEIGHTS[type];
      if (roll <= 0) {
        return createToken(type, pos);
      }
    }

    return createToken(validTypes[0], pos);
  },

  /**
   * Propagate constraints after a token is added/removed.
   * WFC: "The algorithm repeatedly evaluates constraints until no further eliminations occur."
   */
  propagate: (tokens: VitalityToken[]): VitalityToken[] => {
    // Remove tokens that violate constraints
    return tokens.filter((token, i) => {
      const others = tokens.filter((_, j) => i !== j);
      return isTokenValid(token, others);
    });
  },

  /**
   * Decay tokens — reduce lifetime, remove expired.
   */
  decay: (tokens: VitalityToken[], deltaMs: number): VitalityToken[] => {
    return tokens
      .map((token) => ({
        ...token,
        lifetime: token.lifetime - deltaMs,
        phase: (token.phase + deltaMs / getTokenPeriod(token.type)) % 1,
      }))
      .filter((token) => token.lifetime > 0);
  },
};

// =============================================================================
// Helper Functions
// =============================================================================

function getValidTokenTypes(
  pos: { x: number; y: number },
  existing: VitalityToken[]
): VitalityTokenType[] {
  const allTypes: VitalityTokenType[] = ['firefly', 'shimmer', 'drift', 'pulse', 'ripple', 'rest'];

  return allTypes.filter((type) => {
    const constraints = ADJACENCY_CONSTRAINTS[type];

    // Check all existing tokens
    for (const token of existing) {
      const dist = Math.hypot(pos.x - token.position.x, pos.y - token.position.y);

      // If too close to an incompatible token, reject
      if (dist < constraints.minDistance && !constraints.compatible.includes(token.type)) {
        return false;
      }

      // If same type too close, reject (no clustering of same type except shimmer)
      if (token.type === type && type !== 'shimmer' && dist < constraints.minDistance) {
        return false;
      }
    }

    return true;
  });
}

function isTokenValid(token: VitalityToken, others: VitalityToken[]): boolean {
  const constraints = ADJACENCY_CONSTRAINTS[token.type];

  for (const other of others) {
    const dist = Math.hypot(
      token.position.x - other.position.x,
      token.position.y - other.position.y
    );

    if (dist < constraints.minDistance && !constraints.compatible.includes(other.type)) {
      return false;
    }
  }

  return true;
}

function createToken(type: VitalityTokenType, pos: { x: number; y: number }): VitalityToken {
  const now = performance.now();
  return {
    id: `${type}-${now}-${Math.random().toString(36).slice(2, 7)}`,
    type,
    position: pos,
    intensity: 0.3 + Math.random() * 0.4, // 0.3-0.7
    phase: Math.random(),
    lifetime: getTokenLifetime(type),
    born: now,
  };
}

function getTokenLifetime(type: VitalityTokenType): number {
  const lifetimes: Record<VitalityTokenType, [number, number]> = {
    firefly: [3000, 8000], // 3-8 seconds
    shimmer: [2000, 5000], // 2-5 seconds
    drift: [5000, 12000], // 5-12 seconds
    pulse: [800, 1500], // 0.8-1.5 seconds (quick)
    ripple: [1500, 3000], // 1.5-3 seconds
    rest: [1000, 3000], // Dormant period
  };

  const [min, max] = lifetimes[type];
  return min + Math.random() * (max - min);
}

function getTokenPeriod(type: VitalityTokenType): number {
  const periods: Record<VitalityTokenType, number> = {
    firefly: 4000, // Slow glow cycle
    shimmer: 1500, // Quick twinkle
    drift: 8000, // Very slow float
    pulse: 600, // Quick beat
    ripple: 2000, // Medium expand
    rest: 10000, // Long dormancy
  };
  return periods[type];
}

// =============================================================================
// The Hook — useVitalityCollapse
// =============================================================================

export interface VitalityCollapseOptions {
  /** Maximum tokens alive at once */
  maxTokens?: number;
  /** How often to attempt spawning (ms) */
  spawnInterval?: number;
  /** Target density (0-1): higher = more tokens */
  density?: number;
  /** Pause all animation */
  paused?: boolean;
  /** Respect prefers-reduced-motion */
  respectReducedMotion?: boolean;
  /** Container bounds (for relative positioning) */
  bounds?: { width: number; height: number };
}

export interface VitalityCollapseState {
  /** Current live tokens */
  tokens: VitalityToken[];
  /** Whether animation is running */
  isActive: boolean;
  /** Manually trigger a ripple at position */
  triggerRipple: (x: number, y: number) => void;
  /** Manually trigger a pulse */
  triggerPulse: (x: number, y: number) => void;
  /** Get CSS styles for a token */
  getTokenStyle: (token: VitalityToken) => React.CSSProperties;
}

/**
 * useVitalityCollapse — WFC-inspired procedural animation hook
 *
 * Creates a field of coherent micro-animations that feel alive
 * without being overwhelming. Uses constraint propagation to
 * prevent visual clutter.
 *
 * @example
 * const { tokens, getTokenStyle } = useVitalityCollapse({ maxTokens: 10 });
 *
 * return (
 *   <div className="vitality-container">
 *     {tokens.map(token => (
 *       <div key={token.id} style={getTokenStyle(token)} />
 *     ))}
 *   </div>
 * );
 */
export function useVitalityCollapse(options: VitalityCollapseOptions = {}): VitalityCollapseState {
  const {
    maxTokens = 8,
    spawnInterval = 1500,
    density = 0.5,
    paused = false,
    respectReducedMotion = true,
    bounds = { width: 1, height: 1 },
  } = options;

  const [tokens, setTokens] = useState<VitalityToken[]>([]);
  const animationRef = useRef<number | null>(null);
  const lastSpawnRef = useRef<number>(0);
  const lastFrameRef = useRef<number>(0);

  // Check reduced motion preference
  const prefersReducedMotion = useMemo(() => {
    if (!respectReducedMotion) return false;
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, [respectReducedMotion]);

  // Animation loop
  useEffect(() => {
    if (paused || prefersReducedMotion) {
      setTokens([]);
      return;
    }

    const animate = (timestamp: number) => {
      const deltaMs = timestamp - (lastFrameRef.current || timestamp);
      lastFrameRef.current = timestamp;

      setTokens((prevTokens) => {
        // Decay existing tokens
        let updated = VITALITY_OPERAD.decay(prevTokens, deltaMs);

        // Propagate constraints (remove invalid tokens)
        updated = VITALITY_OPERAD.propagate(updated);

        // Maybe spawn new token
        const timeSinceSpawn = timestamp - lastSpawnRef.current;
        const adjustedInterval = spawnInterval / density;

        if (timeSinceSpawn > adjustedInterval && updated.length < maxTokens) {
          const newToken = VITALITY_OPERAD.spawn(updated, bounds);
          if (newToken && newToken.type !== 'rest') {
            updated = [...updated, newToken];
            lastSpawnRef.current = timestamp;
          } else if (newToken?.type === 'rest') {
            // Rest tokens don't render but affect spawn timing
            lastSpawnRef.current = timestamp - adjustedInterval * 0.7;
          }
        }

        return updated;
      });

      animationRef.current = requestAnimationFrame(animate);
    };

    animationRef.current = requestAnimationFrame(animate);

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current);
      }
    };
  }, [paused, prefersReducedMotion, maxTokens, spawnInterval, density, bounds]);

  // Manual trigger functions
  const triggerRipple = useCallback(
    (x: number, y: number) => {
      if (prefersReducedMotion) return;

      const ripple = createToken('ripple', { x, y });
      setTokens((prev) => {
        const withRipple = [...prev, ripple];
        return VITALITY_OPERAD.propagate(withRipple);
      });
    },
    [prefersReducedMotion]
  );

  const triggerPulse = useCallback(
    (x: number, y: number) => {
      if (prefersReducedMotion) return;

      const pulse = createToken('pulse', { x, y });
      setTokens((prev) => [...prev, pulse]);
    },
    [prefersReducedMotion]
  );

  // Get CSS style for rendering a token
  const getTokenStyle = useCallback((token: VitalityToken): React.CSSProperties => {
    const baseStyle: React.CSSProperties = {
      position: 'absolute',
      left: `${token.position.x * 100}%`,
      top: `${token.position.y * 100}%`,
      pointerEvents: 'none',
      willChange: 'transform, opacity',
    };

    // Calculate current animation state based on phase
    const phase = token.phase;
    const age = performance.now() - token.born;
    const lifeRatio = Math.max(0, token.lifetime / getTokenLifetime(token.type));

    switch (token.type) {
      case 'firefly': {
        // Glow that fades in and out
        const glowPhase = Math.sin(phase * Math.PI * 2);
        const fadeIn = Math.min(1, age / 500); // 500ms fade in
        const fadeOut = Math.min(1, token.lifetime / 1000); // 1s fade out
        const opacity = token.intensity * glowPhase * 0.5 * fadeIn * fadeOut;

        return {
          ...baseStyle,
          width: '8px',
          height: '8px',
          borderRadius: '50%',
          background: 'var(--glow-spore)',
          boxShadow: `0 0 ${12 * token.intensity}px var(--glow-spore)`,
          opacity: Math.max(0, opacity),
          transform: 'translate(-50%, -50%)',
        };
      }

      case 'shimmer': {
        // Quick brightness flicker
        const shimmerPhase = Math.sin(phase * Math.PI * 4) * 0.5 + 0.5;
        const opacity = token.intensity * shimmerPhase * 0.3 * lifeRatio;

        return {
          ...baseStyle,
          width: '4px',
          height: '4px',
          borderRadius: '50%',
          background: 'var(--life-mint)',
          opacity: Math.max(0, opacity),
          transform: 'translate(-50%, -50%)',
        };
      }

      case 'drift': {
        // Slow floating motion
        const driftX = Math.sin(phase * Math.PI * 2) * 10;
        const driftY = Math.cos(phase * Math.PI * 2) * 5;
        const opacity = token.intensity * 0.4 * lifeRatio;

        return {
          ...baseStyle,
          width: '6px',
          height: '6px',
          borderRadius: '50%',
          background: 'var(--steel-zinc)',
          opacity: Math.max(0, opacity),
          transform: `translate(calc(-50% + ${driftX}px), calc(-50% + ${driftY}px))`,
        };
      }

      case 'pulse': {
        // Quick heartbeat
        const pulseScale = 1 + Math.sin(phase * Math.PI) * 0.3;
        const opacity = (1 - phase) * token.intensity * 0.6;

        return {
          ...baseStyle,
          width: '12px',
          height: '12px',
          borderRadius: '50%',
          background: 'transparent',
          border: '1px solid var(--life-sage)',
          opacity: Math.max(0, opacity),
          transform: `translate(-50%, -50%) scale(${pulseScale})`,
        };
      }

      case 'ripple': {
        // Expanding ring
        const rippleScale = 1 + phase * 2;
        const opacity = (1 - phase) * token.intensity * 0.5;

        return {
          ...baseStyle,
          width: '20px',
          height: '20px',
          borderRadius: '50%',
          background: 'transparent',
          border: '1px solid var(--glow-light)',
          opacity: Math.max(0, opacity),
          transform: `translate(-50%, -50%) scale(${rippleScale})`,
        };
      }

      default:
        return { ...baseStyle, display: 'none' };
    }
  }, []);

  return {
    tokens: tokens.filter((t) => t.type !== 'rest'),
    isActive: !paused && !prefersReducedMotion && tokens.length > 0,
    triggerRipple,
    triggerPulse,
    getTokenStyle,
  };
}

// =============================================================================
// Export Operad Constants
// =============================================================================

export { ADJACENCY_CONSTRAINTS, ENTROPY_WEIGHTS, VITALITY_OPERAD };
