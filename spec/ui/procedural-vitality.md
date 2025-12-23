# Procedural Vitality Specification

> *"Stillness, then life."*

**Status**: Implemented
**Created**: 2025-12-22
**Location**: `impl/claude/web/src/hooks/useVitality*.ts`

---

## 1. Overview

Procedural Vitality replaces uniform breathing animations with **constraint-based micro-interactions** inspired by [Wave Function Collapse](https://www.boristhebrave.com/2020/04/13/wave-function-collapse-explained/). The result: pages that feel alive without being overwhelming—like Studio Ghibli backgrounds where grass sways slightly differently.

### The Core Insight

```
Traditional:  BreathingContainer → uniform scale/opacity cycle → mechanical
Procedural:   VitalityOperad → constrained token spawning → organic variety
```

Uniform breathing feels robotic because every element moves identically. Procedural vitality creates **emergent life** from simple constraints.

---

## 2. Design Philosophy

### STARK BIOME Alignment

| Principle | Application |
|-----------|-------------|
| "90% Steel / 10% Life" | 60% `rest` tokens, 40% active tokens |
| "Stillness, then life" | Motion is *earned*, not constant |
| "The frame is humble" | Background tokens, not foreground |
| "The content glows" | Interactions trigger earned glow (ripples) |

### Anti-Patterns Avoided

| Anti-Pattern | How Avoided |
|--------------|-------------|
| Continuous animations | Token lifetimes (3-12s), decay system |
| Uniform timing | Staggered spawns, random phases |
| Large amplitude | Max 10px drift, 8° tilt |
| Attention competition | Constraint system prevents clustering |
| Battery drain | `requestAnimationFrame`, `will-change` sparse |

---

## 3. The Vitality Operad

### 3.1 Token Types (The Tiles)

```typescript
type VitalityTokenType =
  | 'firefly'   // Ambient glow that appears and fades
  | 'shimmer'   // Micro-brightness fluctuation
  | 'drift'     // Slow positional float
  | 'pulse'     // Single heartbeat
  | 'ripple'    // Expanding ring (interaction-triggered)
  | 'rest';     // No animation (stillness period)
```

### 3.2 Entropy Weights (The Probabilities)

```typescript
const ENTROPY_WEIGHTS: Record<VitalityTokenType, number> = {
  rest:     0.60,  // 60% stillness
  shimmer:  0.20,  // 20% subtle shimmer
  firefly:  0.08,  // 8% fireflies
  drift:    0.05,  // 5% drift
  pulse:    0.05,  // 5% pulse
  ripple:   0.02,  // 2% ripple (rare, earned)
};
```

**Key insight**: Most spawns produce `rest` (stillness). Life emerges in bursts.

### 3.3 Adjacency Constraints (The Grammar)

```typescript
const ADJACENCY_CONSTRAINTS: Record<VitalityTokenType, {
  compatible: VitalityTokenType[];
  minDistance: number;
}> = {
  firefly: {
    compatible: ['shimmer', 'rest', 'pulse'],
    minDistance: 0.15,  // 15% of container
  },
  shimmer: {
    compatible: ['firefly', 'drift', 'rest', 'pulse', 'shimmer'],
    minDistance: 0.05,  // Shimmers can cluster
  },
  drift: {
    compatible: ['shimmer', 'rest', 'pulse'],
    minDistance: 0.25,  // Drifts need space
  },
  // ...
};
```

**Why constraints matter**:
- Two fireflies too close → fight for attention (bad)
- Shimmer + firefly → enhances glow (good)
- Multiple drifts → confusing motion (bad)

### 3.4 Operations (The Operad)

```typescript
const VITALITY_OPERAD = {
  /**
   * Spawn: WFC-inspired selection
   * 1. Pick random position
   * 2. Calculate valid types via constraint propagation
   * 3. Select using entropy-weighted random
   */
  spawn: (existing: Token[], bounds: Bounds) => Token | null,

  /**
   * Propagate: Remove constraint violations
   * "The algorithm repeatedly evaluates constraints until
   *  no further eliminations occur." — WFC
   */
  propagate: (tokens: Token[]) => Token[],

  /**
   * Decay: Age tokens, remove expired
   * Prevents accumulation, ensures lifecycle
   */
  decay: (tokens: Token[], deltaMs: number) => Token[],
};
```

---

## 4. Animation Hooks

### 4.1 useVitalityCollapse

The main hook implementing WFC-inspired token composition.

```typescript
interface VitalityCollapseOptions {
  maxTokens?: number;        // Cap on simultaneous tokens (default: 8)
  spawnInterval?: number;    // ms between spawn attempts (default: 1500)
  density?: number;          // 0-1, higher = more tokens (default: 0.5)
  paused?: boolean;          // Disable all animation
  respectReducedMotion?: boolean;  // default: true
}

interface VitalityCollapseState {
  tokens: VitalityToken[];
  isActive: boolean;
  triggerRipple: (x: number, y: number) => void;
  triggerPulse: (x: number, y: number) => void;
  getTokenStyle: (token: VitalityToken) => CSSProperties;
}
```

**Usage**:
```tsx
function WelcomeView() {
  const { tokens, getTokenStyle, triggerRipple } = useVitalityCollapse({
    maxTokens: 8,
    density: 0.4,
  });

  return (
    <div className="vitality-container">
      {tokens.map(token => (
        <div key={token.id} style={getTokenStyle(token)} />
      ))}
    </div>
  );
}
```

### 4.2 useSpringTilt

Spring physics for hover interactions on cards.

```typescript
interface SpringTiltOptions {
  maxTilt?: number;      // degrees (default: 8)
  stiffness?: number;    // 0-1 (default: 0.15)
  damping?: number;      // 0-1 (default: 0.7)
}

const { style, handlers } = useSpringTilt({ maxTilt: 6 });

<div style={style} {...handlers}>
  {children}
</div>
```

**Physics model**:
```
force = (target - current) * stiffness
velocity = (velocity + force) * damping
position = position + velocity
```

### 4.3 useKeyPulse

Visual feedback when keyboard shortcuts are pressed.

```typescript
const { isPulsing, triggerPulse } = useKeyPulse('t');

<kbd className={isPulsing ? 'pulsing' : ''}>T</kbd>
```

### 4.4 useQuoteRotation

Curated quote cycling with shimmer reveal.

```typescript
const CURATED_QUOTES = [
  "The proof IS the decision.",
  "Daring, bold, creative, opinionated but not gaudy.",
  "The persona is a garden, not a museum.",
  // ...
];

const { quote, onClick, shimmerClass } = useQuoteRotation();

<blockquote className={shimmerClass} onClick={onClick}>
  "{quote}"
</blockquote>
```

### 4.5 useTitleScatter

Hidden delight: letters scatter and magnetically reform on double-click.

```typescript
const { letters, onDoubleClick, getLetterStyle } = useTitleScatter({
  text: 'The Membrane',
  maxScatter: 50,  // px
});

<h1 onDoubleClick={onDoubleClick}>
  {letters.map((letter, i) => (
    <span key={i} style={getLetterStyle(letter)}>
      {letter.char}
    </span>
  ))}
</h1>
```

---

## 5. Token Lifecycle

```
┌─────────────────────────────────────────────────────────────┐
│  SPAWN                                                      │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. Pick random position (x, y) ∈ [0, 1]²            │   │
│  │ 2. getValidTokenTypes(pos, existingTokens)          │   │
│  │    - For each type, check minDistance to all tokens │   │
│  │    - Filter incompatible adjacencies                │   │
│  │ 3. Weighted random selection (entropy weights)      │   │
│  │ 4. Create token with random phase, intensity        │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  ANIMATE (per frame)                                        │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ 1. decay(tokens, deltaMs)                           │   │
│  │    - Reduce lifetime                                │   │
│  │    - Advance phase                                  │   │
│  │    - Remove expired (lifetime ≤ 0)                  │   │
│  │ 2. propagate(tokens)                                │   │
│  │    - Remove constraint violations                   │   │
│  │ 3. Maybe spawn (if interval elapsed, count < max)   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│  RENDER                                                     │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ getTokenStyle(token) → CSSProperties                │   │
│  │ - Position: left/top from normalized coords         │   │
│  │ - Animation: based on type + phase + lifetime       │   │
│  │ - Fade: in (age < 500ms), out (lifetime < 1000ms)   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 6. Token Visual Specifications

| Token | Size | Color | Animation | Lifetime |
|-------|------|-------|-----------|----------|
| firefly | 8px | `--glow-spore` | Sine glow (4s period) + box-shadow | 3-8s |
| shimmer | 4px | `--life-mint` | Fast sine (1.5s period) | 2-5s |
| drift | 6px | `--steel-zinc` | Lissajous float (8s period) | 5-12s |
| pulse | 12px | `--life-sage` border | Single expand + fade | 0.8-1.5s |
| ripple | 20px | `--glow-light` border | Expand 2x + fade | 1.5-3s |

---

## 7. Performance Guarantees

### GPU Acceleration
All animations use only transform and opacity (composited properties).

### Memory Bounds
- Max 8 tokens (configurable)
- Token lifetime capped at 12s
- No token accumulation (decay removes expired)

### CPU Efficiency
- Single `requestAnimationFrame` loop
- No per-token RAF (shared loop)
- Constraint check is O(n²) but n ≤ 8

### Battery Respect
- `will-change` only during animation
- Pauses when tab hidden (RAF behavior)
- `prefers-reduced-motion` disables all

---

## 8. Accessibility

### prefers-reduced-motion

```typescript
const prefersReducedMotion = useMemo(() => {
  if (typeof window === 'undefined') return false;
  return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
}, []);

// All hooks respect this:
if (prefersReducedMotion) {
  return { tokens: [], isActive: false, /* static fallbacks */ };
}
```

### Focus States
All interactive elements have `:focus-visible` outlines:
```css
.welcome-view__hint:focus-visible {
  outline: 2px solid var(--life-sage);
  outline-offset: 2px;
}
```

### ARIA
Vitality layer is `aria-hidden="true"` (decorative).

---

## 9. Relation to Wave Function Collapse

| WFC Concept | Vitality Implementation |
|-------------|------------------------|
| Tiles | VitalityTokenType (6 types) |
| Superposition | Valid token types at position |
| Collapse | Weighted random selection |
| Propagation | Remove constraint violations |
| Backtracking | Not needed (spawn can fail gracefully) |
| Entropy heuristic | Spawn at random position, select by weight |

**Key simplification**: WFC typically fills a grid. Vitality spawns at random continuous positions, so "least entropy" heuristic becomes "random position + weighted type selection."

---

## 10. Extension Points

### Adding New Token Types

```typescript
// 1. Add to type
type VitalityTokenType = ... | 'newtype';

// 2. Add entropy weight
ENTROPY_WEIGHTS.newtype = 0.03;

// 3. Add constraints
ADJACENCY_CONSTRAINTS.newtype = {
  compatible: ['shimmer', 'rest'],
  minDistance: 0.1,
};

// 4. Add lifetime
function getTokenLifetime(type) {
  if (type === 'newtype') return [2000, 4000];
}

// 5. Add rendering in getTokenStyle()
case 'newtype': return { /* CSS */ };
```

### Custom Triggers

```typescript
// Ripple on any click
const handleClick = (e) => {
  const rect = container.getBoundingClientRect();
  triggerRipple(
    (e.clientX - rect.left) / rect.width,
    (e.clientY - rect.top) / rect.height
  );
};
```

---

## 11. Files

| File | Purpose |
|------|---------|
| `hooks/useVitalityOperad.ts` | WFC-inspired token composition |
| `hooks/useSpringTilt.ts` | Spring physics hover |
| `hooks/useQuoteRotation.ts` | Quote cycling with shimmer |
| `hooks/useTitleScatter.ts` | Letter scatter effect |
| `membrane/views/WelcomeView.tsx` | Implementation example |
| `membrane/views/WelcomeView.css` | Token styles |

---

## 12. References

- [Wave Function Collapse Explained](https://www.boristhebrave.com/2020/04/13/wave-function-collapse-explained/) — Boris the Brave
- [GitHub: mxgmn/WaveFunctionCollapse](https://github.com/mxgmn/WaveFunctionCollapse) — Original implementation
- [Procedural Generation with WFC](https://www.gridbugs.org/wave-function-collapse/) — GridBugs
- `impl/claude/agents/operad/core.py` — Python Operad pattern

---

*"The noun is a lie. There is only the rate of change."*

**Filed**: 2025-12-22
**Status**: Implemented, Production-Ready
