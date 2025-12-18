# Unified Creative Vision

> *"The aesthetic is not decoration—it is the categorical structure made perceivable."*

**Status**: Primary Creative Reference (supersedes mood-board.md)
**Aligned With**: `plans/design-language-consolidation.md`, AD-006, AD-009
**Last Updated**: 2025-12-17

---

## Part I: The Creative Ground

### Philosophy in One Breath

kgents aesthetics emerge from the same categorical structure as the agents themselves. There is no separate "design layer"—the visual, motion, and voice systems ARE projections of the underlying mathematics.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        THE CREATIVE EQUATION                                 │
│                                                                              │
│   Aesthetics = Project(PolyAgent × Operad × Sheaf)                          │
│                                                                              │
│   • PolyAgent → States (what can be shown)                                  │
│   • Operad → Composition (how elements combine)                             │
│   • Sheaf → Coherence (why it feels unified)                                │
└─────────────────────────────────────────────────────────────────────────────┘
```

### The Three Operads

All UI composition flows through three orthogonal operads (see `plans/design-language-consolidation.md`):

| Operad | Domain | Operations |
|--------|--------|------------|
| **LAYOUT_OPERAD** | Spatial arrangement | stack, split, grid, float |
| **CONTENT_OPERAD** | Information density | degrade, enrich, summarize |
| **MOTION_OPERAD** | Temporal behavior | breathe, pop, shake, fade |

**The Composition Theorem**:
```
UI = Layout[Density] ∘ Content[Density] ∘ Motion[ReducedMotion]
```

Each operad respects associativity. Composition order doesn't matter—the result is the same.

---

## Part II: The Design Polynomial

### Content States (DESIGN_POLYNOMIAL)

Every UI element exists in one of five states:

| State | Visual Treatment | When |
|-------|------------------|------|
| **SKELETON** | Shimmer placeholders | No data yet |
| **LOADING** | Personality messages | Data fetching |
| **PARTIAL** | Core content only | Fast initial paint |
| **FULL** | Complete content | All data available |
| **INTERACTIVE** | Affordances active | User can act |

**Transition Grammar**:
```
SKELETON → LOADING → PARTIAL → FULL → INTERACTIVE
    ↑                    ↓
    └─── (error) ────────┘
```

### Density Dimension

The simplifying isomorphism (AD-008) that governs all responsive behavior:

| Density | Breakpoint | Characteristics |
|---------|------------|-----------------|
| **compact** | < 768px | Mobile-first, minimal chrome |
| **comfortable** | 768-1024px | Balanced panels |
| **spacious** | > 1024px | Full affordances |

**Principle**: Components receive density, adapt internally. No scattered `isMobile` checks.

---

## Part III: Visual Identity

### Color Philosophy

**Semantic, not decorative.** Every color traces to meaning:

| Semantic | Primary Hue | Usage |
|----------|-------------|-------|
| **Anchor** | Cyan (#06B6D4) | Primary actions, focus |
| **Surface** | Gray scale (800-900) | Backgrounds |
| **Text** | Gray scale (100-400) | Content |
| **Jewel** | Per Crown Jewel | Domain identity |

### The Jewel Palette

Each Crown Jewel has a color signature derived from its personality:

| Jewel | Hue | Character |
|-------|-----|-----------|
| Brain | Cyan | Contemplative, neural |
| Gestalt | Green | Analytical, systematic |
| Gardener | Lime | Nurturing, organic |
| Atelier | Amber | Creative, warm |
| Coalition | Violet | Collaborative, social |
| Park | Pink | Theatrical, immersive |
| Domain | Red | Urgent, authoritative |

### Typography

Berkeley Mono everywhere. One font, multiple weights:

| Element | Weight | Size |
|---------|--------|------|
| Body | 400 | base (16px) |
| Headings | 700 | lg-4xl |
| Code | 400 | sm-base |
| Labels | 500 | xs-sm |

### Iconography

**Lucide icons only.** No emojis in production UI.

```tsx
// Correct
import { Brain, Leaf, Users } from 'lucide-react';

// Incorrect
const icon = "🧠";  // NO
```

---

## Part IV: Motion Language

### The Six Primitives (MOTION_OPERAD)

| Primitive | Purpose | When |
|-----------|---------|------|
| **Breathe** | Living presence | Idle, active |
| **Pulse** | Attention | Waiting, processing |
| **Shake** | Error | Validation failure |
| **Pop** | Success | Completion |
| **Shimmer** | Loading | Placeholder |
| **Fade** | Transition | Enter/exit |

### Timing (2025 Speed Mandate)

> *"Speed is king. Users crave instant feedback."*

| Duration | Use Case |
|----------|----------|
| 0-100ms | Instant (hover, focus) |
| 100-200ms | Quick (tabs, toggles) |
| 200-400ms | Standard (cards, modals) |
| 400-700ms | Elaborate (celebrations) |
| 1000ms+ | Ambient only (breathe) |

### Motion Preferences

**Always respect `prefers-reduced-motion`:**

```tsx
const { shouldAnimate } = useMotionPreferences();
if (!shouldAnimate) return <StaticVersion />;
```

---

## Part V: Voice and Tone

### The Voice (Constant)

| Attribute | Meaning |
|-----------|---------|
| **Thoughtful** | We consider before speaking |
| **Warm** | We care about the human |
| **Direct** | We don't waste words |
| **Witty** | We find lightness naturally |
| **Honest** | We admit limitations |

### The Tone (Variable)

Same voice, different temperatures:

| Context | Tone | Example |
|---------|------|---------|
| Success | Celebratory | "Done! Your changes are safe." |
| Loading | Patient | "Crystallizing memories..." |
| Error | Empathetic | "Something went wrong. Let's fix it together." |
| Empty | Inviting | "Nothing here yet. Ready when you are." |

### Error Formula

```
[What happened] + [Why/Context] + [What to do next]
```

**Never**: "Error 500"
**Always**: "Something unexpected... Even the wisest agents encounter mysteries."

---

## Part VI: Emergence (Generative Aesthetics)

> *"We do not design the flower—we design the soil and the season."*

### The Qualia Space

All sensory modalities project from unified coordinates:

| Dimension | Range | Affects |
|-----------|-------|---------|
| warmth | -1 to +1 | Hue, motion speed |
| weight | -1 to +1 | Saturation, dampening |
| tempo | -1 to +1 | Duration, stagger |
| brightness | -1 to +1 | Luminance, amplitude |

**Cross-Modal Consistency**: Warm color → slow motion → low pitch.

### Circadian Modulation

UI breathes differently at different times:

| Phase | Hours | Modifier |
|-------|-------|----------|
| Dawn | 6-10 | Cooler, brightening |
| Noon | 10-16 | Neutral, active |
| Dusk | 16-20 | Warming, slowing |
| Midnight | 20-6 | Cool, dim, slow |

### The Accursed Share

> *"10% of emergence is chaos. This is sacred."*

- Timing: ±5% variation on animations
- Position: Subtle jitter on particles
- Color: Minor hue drift over time

---

## Part VII: Integration with AGENTESE

The creative system projects through AGENTESE:

```
concept.design.layout.manifest     → Current layout state
concept.design.content.degrade     → Apply degradation
concept.design.motion.apply        → Apply motion primitive
concept.design.operad.verify       → Verify composition laws
```

**Observer-Dependent Rendering**: Different observers perceive different aesthetics. The architect sees blueprints; the poet sees metaphor.

---

## Part VIII: Anti-Patterns

| Anti-Pattern | Why Wrong | Instead |
|--------------|-----------|---------|
| Hard-coded colors | Not semantic | Use palette tokens |
| Fixed timing | Mechanical feel | Use qualia + noise |
| Scattered `isMobile` | Violates AD-008 | Pass density context |
| Emojis in UI | Inconsistent rendering | Use Lucide icons |
| Silent errors | UX failure | Use EmpathyError |
| Raw "Loading..." | Generic | Use jewel personality |

---

## Part IX: Quick Reference

### Color Quick Reference

```
Gray:   50 → 100 → 200 → 300 → 400 → 500 → 600 → 700 → 800 → 900 → 950
Jewels: brain(cyan) | gestalt(green) | gardener(lime) | atelier(amber)
        coalition(violet) | park(pink) | domain(red)
States: success(green) | warning(amber) | error(red) | info(cyan)
```

### Spacing Quick Reference

```
1=4px | 2=8px | 3=12px | 4=16px | 5=20px | 6=24px | 8=32px | 10=40px
```

### Motion Quick Reference

```
breathe: 2-4s cycle | pulse: 0.5-2s | shake: 400ms | pop: 300ms | fade: 150-200ms
```

---

## Sources and References

- `spec/principles.md` — Core design principles
- `spec/protocols/projection.md` — Projection Protocol
- `plans/design-language-consolidation.md` — DESIGN_OPERAD specification
- `plans/autopoietic-architecture.md` — AD-006, AD-008, AD-009
- `docs/skills/elastic-ui-patterns.md` — Implementation patterns
- `docs/skills/ux-reference-patterns.md` — Cross-cutting UX patterns

---

*"The aesthetic is the structure perceiving itself. Beauty is not added—it is revealed."*
