# Emergence Principles

> *"We do not design the flower—we design the soil and the season."*

**Status**: Foundation Document
**Prerequisites**: `philosophy.md`, `motion-language.md`
**Related**: AD-003 (Generative Over Enumerative), AGENTESE specification

---

## The Fundamental Claim

kgents aesthetics are **emergent, not designed**. Visual forms, motion patterns, and sensory experiences arise from rules and context, not from static specifications.

This is not metaphor—it is implementation:

```typescript
// Traditional (descriptive):
const PRIMARY_COLOR = "#06B6D4";  // Fixed value

// Emergent (generative):
const PRIMARY_COLOR = emerge({
  rule: "anchor-hue",
  context: (ctx) => ctx.observer.personality,
  seed: ctx.time.circadian,
});  // Computed at render
```

---

## Part I: The Three Layers

### Layer 1: Micro-Emergence (Physics)

Individual visual elements emerge from physical simulation:

| Element | Physics | Parameters |
|---------|---------|------------|
| Button press | Spring dynamics | tension, damping, mass |
| Loading state | Wave interference | frequency, amplitude |
| Error shake | Oscillation decay | magnitude, falloff |
| Success pop | Elastic overshoot | spring constant |

**Implementation Pattern:**
```typescript
const spring = (params: SpringParams) => (t: number): number => {
  const { stiffness, damping, mass } = params;
  const omega = Math.sqrt(stiffness / mass);
  const zeta = damping / (2 * Math.sqrt(stiffness * mass));
  // Underdamped spring equation
  return Math.exp(-zeta * omega * t) * Math.cos(omega * Math.sqrt(1 - zeta**2) * t);
};
```

### Layer 2: Meso-Emergence (Grammar)

Compositions and patterns emerge from grammars (operads):

| Pattern | Grammar | Operations |
|---------|---------|------------|
| Layout flow | `LAYOUT_OPERAD` | stack, split, grid |
| Visual rhythm | `RHYTHM_OPERAD` | repeat, stagger, group |
| Growth patterns | `GROWTH_OPERAD` | seed, branch, connect |

**Implementation Pattern:**
```typescript
const LAYOUT_OPERAD = Operad({
  operations: {
    stack: { arity: "variadic", direction: "vertical" },
    split: { arity: 2, ratio: "golden" },
    grid: { arity: "variadic", columns: "auto" },
  },
  laws: [
    // stack(A) ≡ A (identity)
    // stack(stack(A, B), C) ≡ stack(A, stack(B, C)) (associativity)
  ],
});
```

### Layer 3: Macro-Emergence (Attractors)

System-wide coherence emerges from attractors:

| Attractor | What It Organizes | Coordinates |
|-----------|-------------------|-------------|
| Personality eigenvector | Agent visual identity | warmth, precision, creativity |
| Circadian phase | Temporal palette | dawn, noon, dusk, midnight |
| Context intensity | Density/detail level | compact, comfortable, spacious |

**Implementation Pattern:**
```typescript
const PERSONALITY_ATTRACTOR = {
  dimensions: ["warmth", "precision", "creativity"],
  compute: (agent: Agent): Vector3 => {
    // Extract from agent state
    return eigenvectorFromState(agent);
  },
  project: (coords: Vector3): AestheticParams => ({
    hue: coords.warmth * 30 + 180,  // Cool to warm
    sharpness: coords.precision,
    complexity: coords.creativity,
  }),
};
```

---

## Part II: Core Algorithms

### Cymatics Engine

Cymatics makes vibration visible. In kgents, we make *agent behavior* visible through cymatic patterns.

```typescript
interface CymaticsEngine {
  // Add a vibration source (agent, event, state change)
  addSource(source: VibrationSource): void;

  // Compute interference pattern
  compute(): ChladniPattern;

  // Render to visual medium
  render(target: RenderTarget): void;
}

interface VibrationSource {
  frequency: number;    // Activity rate (events/second)
  amplitude: number;    // Intensity (0-1)
  phase: number;        // Timing offset
  position: Vector2;    // Spatial location
}

interface ChladniPattern {
  nodes: Vector2[];     // Points of constructive interference
  antinodes: Vector2[]; // Points of destructive interference
  field: (p: Vector2) => number;  // Continuous amplitude function
}
```

**Application:**
- Coalition health → interference pattern stability
- Agent communication → frequency modulation
- Memory access → resonance visualization

### Differential Growth

Organic forms emerge from growth rules, not placement.

```typescript
interface GrowthEngine {
  // Plant a seed point
  seed(position: Vector3, properties: SeedProperties): NodeId;

  // Grow toward a target (with avoidance)
  grow(from: NodeId, toward: Vector3, iterations: number): void;

  // Connect two nodes (with organic path)
  connect(a: NodeId, b: NodeId): EdgeId;

  // Let the system settle
  relax(iterations: number): void;

  // Render current state
  render(): Mesh;
}

interface GrowthRules {
  attraction: number;    // Pull toward target
  repulsion: number;     // Push from neighbors
  alignment: number;     // Follow local direction
  randomness: number;    // Accursed share injection
}
```

**Application:**
- Knowledge graph edges → grow between nodes
- Plan progress → frontier zone visualization
- Memory crystallization → lattice formation

### Boids Flocking

Social dynamics become visible through flocking behavior.

```typescript
interface BoidsEngine {
  // Add a boid (agent, idea, memory)
  addBoid(id: string, properties: BoidProperties): void;

  // Update all positions
  step(dt: number): void;

  // Get current positions
  positions(): Map<string, Vector3>;
}

interface BoidRules {
  separation: number;    // Avoid crowding (conflicts)
  alignment: number;     // Follow neighbors (trends)
  cohesion: number;      // Move toward center (attraction)
  target: Vector3 | null; // External goal
}
```

**Application:**
- Agent Town citizens → social clustering
- Atelier ideas → thought-stream organization
- M-gent memories → associative navigation

### Reaction-Diffusion

Turing patterns for visual texture generation.

```typescript
interface ReactionDiffusionEngine {
  // Initialize with seed pattern
  initialize(seed: Pattern): void;

  // Iterate the reaction-diffusion equations
  step(iterations: number): void;

  // Get current pattern
  pattern(): Grid<number>;
}

interface RDParameters {
  feedRate: number;      // Chemical A addition rate
  killRate: number;      // Chemical B removal rate
  diffusionA: number;    // Chemical A spread rate
  diffusionB: number;    // Chemical B spread rate
}
```

**Application:**
- Code complexity visualization → density patterns
- Activity heatmaps → organic texture
- Error propagation → spreading patterns

---

## Part III: The Qualia Space

All sensory modalities project from a unified qualia space:

```typescript
interface QualiaSpace {
  dimensions: {
    warmth: number;      // -1 (cool) to +1 (warm)
    weight: number;      // -1 (light) to +1 (heavy)
    tempo: number;       // -1 (slow) to +1 (fast)
    texture: number;     // -1 (smooth) to +1 (rough)
    brightness: number;  // -1 (dark) to +1 (bright)
    saturation: number;  // -1 (muted) to +1 (vivid)
    complexity: number;  // -1 (simple) to +1 (complex)
  };

  // Compute coordinates from context
  compute(ctx: Context): QualiaCoords;

  // Project to specific modality
  toColor(coords: QualiaCoords): Color;
  toMotion(coords: QualiaCoords): MotionParams;
  toSound(coords: QualiaCoords): SoundParams;
  toShape(coords: QualiaCoords): ShapeParams;
}
```

### The Projection Functor

```
                    QualiaSpace
                        │
                   compute(ctx)
                        │
                        ▼
              ┌─────────────────┐
              │  QualiaCoords   │
              │  (7-dimensional)│
              └────────┬────────┘
                       │
           ┌───────────┼───────────┐
           │           │           │
           ▼           ▼           ▼
     ┌─────────┐ ┌──────────┐ ┌─────────┐
     │ Color   │ │  Motion  │ │  Shape  │
     └─────────┘ └──────────┘ └─────────┘
```

### Cross-Modal Consistency Table

| Qualia Dimension | Color Mapping | Motion Mapping | Sound Mapping | Shape Mapping |
|------------------|---------------|----------------|---------------|---------------|
| warmth: -1 | Cyan (180°) | Crisp, precise | High pitch | Angular |
| warmth: +1 | Amber (30°) | Slow, organic | Low pitch | Rounded |
| weight: -1 | Light, airy | Quick, bouncy | Short attack | Sparse |
| weight: +1 | Dark, saturated | Slow, dampened | Long sustain | Dense |
| tempo: -1 | — | 1000ms+ durations | Adagio | — |
| tempo: +1 | — | 100ms durations | Presto | — |
| texture: -1 | Solid fills | Linear easing | Sine wave | Clean edges |
| texture: +1 | Gradients/noise | Stepped/jittery | Saw wave | Fuzzy edges |
| brightness: -1 | Low luminance | Subtle amplitude | Quiet | Small scale |
| brightness: +1 | High luminance | Large amplitude | Loud | Large scale |
| saturation: -1 | Grayscale | Uniform motion | White noise | Monochrome |
| saturation: +1 | Full chroma | Varied motion | Pure tone | Multi-color |
| complexity: -1 | Single hue | One element | Unison | Primitive |
| complexity: +1 | Multi-hue | Layered | Harmonic | Fractal |

---

## Part IV: Circadian Aesthetics

The UI breathes differently at different times.

### The Four Phases

```typescript
type CircadianPhase = "dawn" | "noon" | "dusk" | "midnight";

const CIRCADIAN_MODIFIERS: Record<CircadianPhase, QualiaModifier> = {
  dawn: {
    warmth: -0.3,      // Cooler
    brightness: 0.8,   // Brightening
    tempo: 0.3,        // Quickening
    texture: -0.2,     // Smoother
  },
  noon: {
    warmth: 0,         // Neutral
    brightness: 1.0,   // Full brightness
    tempo: 0.5,        // Active
    texture: 0,        // Balanced
  },
  dusk: {
    warmth: 0.4,       // Warming
    brightness: 0.6,   // Dimming
    tempo: -0.2,       // Slowing
    texture: 0.2,      // Textured
  },
  midnight: {
    warmth: -0.1,      // Cool
    brightness: 0.3,   // Dim
    tempo: -0.5,       // Slow
    texture: -0.3,     // Smooth
  },
};
```

### Implementation

```typescript
const applyCircadian = (base: QualiaCoords, hour: number): QualiaCoords => {
  const phase = getPhase(hour);  // 6-10: dawn, 10-16: noon, 16-20: dusk, 20-6: midnight
  const modifier = CIRCADIAN_MODIFIERS[phase];

  return {
    warmth: base.warmth + modifier.warmth,
    brightness: base.brightness * modifier.brightness,
    tempo: base.tempo + modifier.tempo,
    // ... other dimensions
  };
};
```

---

## Part V: Generative Tokens

### Token Definition

```typescript
interface GenerativeToken<T> {
  base: T;                                    // Default value
  derive: (context: Context) => T;            // Context-dependent derivation
  modulate: (base: T, factor: number) => T;  // Parametric adjustment
  blend: (a: T, b: T, t: number) => T;       // Interpolation
}

// Example: Generative Color
const PRIMARY_CYAN: GenerativeToken<Color> = {
  base: hsl(180, 80, 50),
  derive: (ctx) => {
    const circadian = applyCircadian(ctx.time.hour);
    const personality = ctx.observer?.personality ?? neutral;
    return blend(
      shiftHue(base, circadian.warmth * 20),
      shiftSaturation(base, personality.precision * 0.2),
      0.5
    );
  },
  modulate: (base, factor) => adjustLightness(base, factor),
  blend: (a, b, t) => lerpHSL(a, b, t),
};
```

### Token Categories

| Category | Tokens | Emergence Source |
|----------|--------|------------------|
| **Semantic** | primary, secondary, success, error | Agent personality + context |
| **Spatial** | spacing scale, border radius | Density context |
| **Temporal** | duration scale, easing curves | Activity level + circadian |
| **Textural** | blur, shadow, gradient | Weight + texture qualia |

---

## Part VI: Integration Patterns

### Pattern 1: Context Provider

```typescript
const EmergenceProvider = ({ children }: Props) => {
  const time = useCurrentTime();
  const observer = useObserver();
  const density = useDensity();

  const qualia = useMemo(() =>
    QUALIA_SPACE.compute({ time, observer, density }),
    [time, observer, density]
  );

  const tokens = useMemo(() =>
    deriveTokens(qualia),
    [qualia]
  );

  return (
    <EmergenceContext.Provider value={{ qualia, tokens }}>
      {children}
    </EmergenceContext.Provider>
  );
};
```

### Pattern 2: Emergent Component

```typescript
const EmergentCard = ({ children, personality }: Props) => {
  const { qualia, tokens } = useEmergence();

  // Derive card-specific aesthetics from qualia
  const cardQualia = mergeQualia(qualia, personality);
  const styles = projectToStyles(cardQualia);
  const motion = projectToMotion(cardQualia);

  return (
    <motion.div
      style={styles}
      initial={motion.initial}
      animate={motion.animate}
      transition={motion.transition}
    >
      {children}
    </motion.div>
  );
};
```

### Pattern 3: Engine Integration

```typescript
const GestaltBrain = () => {
  const growth = useGrowthEngine();
  const cymatics = useCymaticsEngine();

  // Grow nodes as analysis progresses
  useEffect(() => {
    analysis.nodes.forEach(node => {
      growth.seed(node.position, { weight: node.importance });
    });
    growth.relax(100);
  }, [analysis.nodes]);

  // Add vibration for activity
  useEffect(() => {
    activity.events.forEach(event => {
      cymatics.addSource({
        frequency: event.rate,
        amplitude: event.intensity,
        position: event.location,
      });
    });
  }, [activity.events]);

  return (
    <Canvas>
      <GrowthMesh mesh={growth.render()} />
      <CymaticsOverlay pattern={cymatics.compute()} />
    </Canvas>
  );
};
```

---

## Part VII: The Accursed Share in Emergence

> *"10% of emergence is chaos. This is sacred."*

### Noise Injection

```typescript
const injectAccursedShare = (value: number, budget: number = 0.1): number => {
  const noise = (Math.random() - 0.5) * 2 * budget;
  return value + noise;
};

// Applied to emergence
const emergeWithEntropy = (coords: QualiaCoords): QualiaCoords => ({
  warmth: injectAccursedShare(coords.warmth, 0.05),
  weight: injectAccursedShare(coords.weight, 0.05),
  // ... other dimensions
  // Keep total entropy budget under 10%
});
```

### Organic Variation

- Timing: ±5% variation on animation durations
- Position: Subtle jitter on particle systems
- Color: Minor hue drift over time
- Shape: Slight asymmetry in generated forms

### The Gratitude Loop

```
Emergence → Pattern → Noise Injection → New Emergence
     ↑                                       │
     └──────────── gratitude ────────────────┘
```

---

## Anti-Patterns

| Anti-Pattern | Why Wrong | Instead |
|--------------|-----------|---------|
| Hard-coded colors | Not emergent | Use generative tokens |
| Fixed animation timing | Mechanical feel | Derive from qualia + noise |
| Static layouts | Dead UI | Use growth/flocking |
| Predictable patterns | Boring | Inject accursed share |
| Isolated modalities | Breaks synesthesia | Project from unified qualia |

---

## Verification

### Laws to Check

1. **Projection Consistency**: Same qualia → same experience (up to entropy)
2. **Circadian Monotonicity**: Smooth transitions between phases
3. **Cross-Modal Harmony**: If color is warm, motion should be slow
4. **Entropy Bounds**: Accursed share ≤ 10% deviation

### Test Pattern

```typescript
describe('Emergence Laws', () => {
  it('projects consistently across modalities', () => {
    const coords = { warmth: 0.5, weight: -0.3, ... };
    const color = toColor(coords);
    const motion = toMotion(coords);

    // Warm color implies slow motion
    expect(colorWarmth(color)).toBeGreaterThan(0);
    expect(motionTempo(motion)).toBeLessThan(0.5);
  });

  it('respects entropy bounds', () => {
    const base = computeQualia(ctx);
    const withEntropy = emergeWithEntropy(base);

    expect(distance(base, withEntropy)).toBeLessThan(0.1);
  });
});
```

---

## Sources

- Alan Turing, "The Chemical Basis of Morphogenesis" (1952) — Reaction-diffusion foundation
- Craig Reynolds, "Flocks, Herds and Schools" (1987) — Boids algorithm
- Nervous System Studio — Computational design inspiration
- [Inconvergent](https://inconvergent.net/generative/) — Generative art algorithms
- [Cymatics Research](https://www.spiritualarts.org.uk/cymatics-the-sacred-geometry-of-sound/) — Sound visualization

---

*"The pattern was always there. We simply found the medium that reveals it."*
