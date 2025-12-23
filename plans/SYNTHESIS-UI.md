# SYNTHESIS-UI: The Membrane Experience

> *"Stop documenting agents. Become the agent."*
> *"The frame is humble. The content glows."*

**Status**: Proposal — Unified UI/UX/DevEx Vision
**Date**: 2025-12-22
**Synthesizes**: `membrane.md`, `elastic-ui-patterns.md`, `tailwind.config.js`, joy components, token system
**Voice anchor**: *"Daring, bold, creative, opinionated but not gaudy"*

---

## Epigraph

> *"We built a design system. Then we forgot to use it.*
> *We built elastic patterns. Then scattered conditionals everywhere.*
> *We built joy components. Then hid them in galleries.*
> *We built a membrane. Then kept adding pages.*
>
> *The vision was always there:*
> ***One surface. Three modes. Steel foundation. Earned glow.***
> *Now we execute it."*

---

## Part I: The Current State

We have **exceptional infrastructure** that isn't fully realized:

| Component | Quality | Usage |
|-----------|---------|-------|
| **Membrane** | 25 files, clean architecture | Underutilized — still routes exist |
| **STARK BIOME** | 382-line tailwind config, complete | Inconsistently applied |
| **Elastic Patterns** | 8 primitives, well-documented | Ad-hoc usage, scattered conditionals |
| **Joy Components** | 8 animation primitives | Gallery demos, not production |
| **Design Polynomial** | 610-line hook, temporal coherence | Imported but rarely coordinated |
| **Interactive Tokens** | 7 types, STARK-styled | Working but not everywhere |

**The gap**: We have the tools. We lack the discipline to use them universally.

---

## Part II: The Unified Vision

```
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   THE MEMBRANE EXPERIENCE                                                     ║
║   ═══════════════════════════════════════════════════════════════════════════ ║
║                                                                               ║
║   SURFACE:     One morphing co-thinking surface (no routes)                   ║
║   MODES:       Compact / Comfortable / Spacious (elastic)                     ║
║   PALETTE:     90% Steel / 10% Life (STARK BIOME)                             ║
║   MOTION:      Stillness, then life (earned animation)                        ║
║   TOKENS:      Seven interactive types (Living Spec integration)              ║
║   DEVEX:       Polynomial state machine + temporal coherence                  ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
```

---

## Part III: The Membrane — One Surface

### 3.1 No Routes. No Pages. Context.

The membrane is the **only component**. Everything else is a view within it.

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              THE MEMBRANE                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  ┌─────────────────────────────────────┐  ┌─────────────────────────────────┐  │
│  │           FOCUS PANE                │  │        WITNESS STREAM           │  │
│  │                                     │  │                                 │  │
│  │   What you're working on:           │  │   Real-time decision flow:      │  │
│  │   • SpecView (specs)                │  │   • Marks                       │  │
│  │   • FileView (code)                 │  │   • Decisions                   │  │
│  │   • ConceptView (concepts)          │  │   • Crystallizations            │  │
│  │   • WelcomeView (nothing)           │  │   • Fusions                     │  │
│  │                                     │  │                                 │  │
│  └─────────────────────────────────────┘  └─────────────────────────────────┘  │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────────┐│
│  │                         DIALOGUE PANE                                       ││
│  │                                                                             ││
│  │   Where Kent and K-gent think together                                      ││
│  │   • History of exchanges                                                    ││
│  │   • Input for new thoughts                                                  ││
│  │   • Crystallize button (capture decisions)                                  ││
│  │   • K-Block controls (when editing)                                         ││
│  │                                                                             ││
│  └─────────────────────────────────────────────────────────────────────────────┘│
│                                                                                 │
│  [⌘1] compact   [⌘2] comfortable   [⌘3] spacious   [Esc] home                  │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Context Determines Content

```typescript
type FocusContext =
  | { type: 'spec'; path: string }      // → SpecView
  | { type: 'file'; path: string }      // → FileView
  | { type: 'concept'; id: string }     // → ConceptView
  | { type: 'agentese'; path: string }  // → AgentView (future)
  | { type: 'void' };                   // → WelcomeView

// Dialogue drives focus changes
"Show me the witness service" → { type: 'file', path: 'services/witness/core.py' }
"What is the K-Block?" → { type: 'spec', path: 'spec/protocols/k-block.md' }
```

### 3.3 Mode Transitions

```
                    ⌘1 / viewport < 768px
           ┌─────────────────────────────────────┐
           │                                     │
           ▼                                     │
    ┌─────────────┐                              │
    │   COMPACT   │  Focus only                  │
    │             │  Deep work mode              │
    └──────┬──────┘                              │
           │                                     │
           │ ⌘2 / viewport 768-1023px            │
           ▼                                     │
    ┌─────────────┐                              │
    │ COMFORTABLE │  Focus + Witness             │
    │             │  Default state               │
    └──────┬──────┘                              │
           │                                     │
           │ ⌘3 / viewport ≥ 1024px              │
           ▼                                     │
    ┌─────────────┐                              │
    │  SPACIOUS   │  Full membrane               │
    │             │  Active co-thinking          │
    └─────────────┴──────────────────────────────┘
```

---

## Part IV: STARK BIOME — The Visual Language

### 4.1 The Philosophy

> *"The frame is humble. The content glows."*
> *90% Steel (cool industrial) / 10% Life (organic accents)*

This is not decoration. This is **information hierarchy through restraint**.

### 4.2 The Palettes

```
STEEL FOUNDATION (90% — backgrounds, frames, containers)
═══════════════════════════════════════════════════════════════════

steel-obsidian   #0A0A0C   Deepest background (canvas)
steel-carbon     #141418   Card backgrounds
steel-slate      #1C1C22   Elevated surfaces
steel-gunmetal   #28282F   Borders, dividers
steel-zinc       #3A3A44   Muted text, inactive states


LIVING ACCENT (10% — success, growth, life emerging)
═══════════════════════════════════════════════════════════════════

life-moss        #1A2E1A   Deep living background
life-fern        #2E4A2E   Living surface
life-sage        #4A6B4A   Primary living accent (buttons, links)
life-mint        #6B8B6B   Living text
life-sprout      #8BAB8B   Living highlight


BIOLUMINESCENT (earned — highlights, focus, precious moments)
═══════════════════════════════════════════════════════════════════

glow-spore       #C4A77D   Warm accent (focus states)
glow-amber       #D4B88C   Warning, attention
glow-light       #E5C99D   Brightest earned glow
glow-lichen      #8BA98B   Organic highlight
glow-bloom       #9CBDA0   Success glow
```

### 4.3 The Rules

| Element | Color | Rationale |
|---------|-------|-----------|
| Canvas background | `steel-obsidian` | Deepest layer, recedes |
| Card background | `steel-carbon` | Elevated but humble |
| Borders | `steel-gunmetal` | Visible but unobtrusive |
| Muted text | `steel-zinc` | Readable but recessed |
| Primary actions | `life-sage` | Life emerging from steel |
| Interactive tokens | `life-mint` | Living elements glow |
| Focus states | `glow-spore` | Earned through interaction |
| Success | `life-sage` | Growth, completion |
| Error | `#A65D4A` (muted rust) | Attention without alarm |

### 4.4 Anti-Patterns

```css
/* BAD: Saturated colors that scream */
.button { background: #22C55E; }  /* Neon green */

/* GOOD: STARK living accent */
.button { background: var(--life-sage); }  /* #4A6B4A */


/* BAD: White text on dark background */
.text { color: #FFFFFF; }

/* GOOD: STARK zinc/mint spectrum */
.text-muted { color: var(--steel-zinc); }
.text-living { color: var(--life-mint); }


/* BAD: Borders that dominate */
.card { border: 2px solid white; }

/* GOOD: STARK subtle gunmetal */
.card { border: 1px solid var(--steel-gunmetal); }
```

---

## Part V: Elastic Patterns — Universal Adaptation

### 5.1 The Three-Mode Pattern

Every component adapts to density. No exceptions.

```typescript
// STARK: Density-parameterized constants
const SPACING = {
  compact: { gap: 8, padding: 12 },
  comfortable: { gap: 12, padding: 16 },
  spacious: { gap: 16, padding: 24 },
} as const;

// Usage
const { density } = useWindowLayout();
const style = SPACING[density];
```

### 5.2 The Primitives

| Primitive | Purpose | When to Use |
|-----------|---------|-------------|
| `ElasticSplit` | Two-pane layouts | Main content + sidebar |
| `ElasticContainer` | Self-arranging grids | Card collections |
| `BottomDrawer` | Mobile panels | Controls on compact |
| `FloatingActions` | Mobile FABs | Actions on compact |
| `FloatingSidebar` | Overlay navigation | Navigation overlay |
| `FixedBottomPanel` | Persistent bottom | Terminal, REPL |
| `FixedTopPanel` | Persistent top | Status bar |
| `ElasticCard` | Adaptive cards | Content degradation |

### 5.3 Content Degradation

Cards adapt based on available width:

```
WIDTH:     <60px    60-149px    150-279px    ≥280px
LEVEL:     icon     title       summary      full
SHOWS:     [🔷]     [🔷 Name]   [🔷 Name     [Full content
                                 Status]      with details]
```

```typescript
function getContentLevel(width: number): ContentLevel {
  if (width < 60) return 'icon';
  if (width < 150) return 'title';
  if (width < 280) return 'summary';
  return 'full';
}
```

### 5.4 Anti-Patterns

```tsx
// BAD: Scattered conditionals
{isMobile ? <MobileVersion /> : <DesktopVersion />}

// GOOD: Density-aware component
<Component density={density} />


// BAD: Mode-specific components
<MobileControlPanel />
<DesktopControlPanel />

// GOOD: Single adaptive component
<ControlPanel density={density} isDrawer={isMobile} />


// BAD: Ignoring touch targets
<button className="p-1">×</button>  // 24px

// GOOD: Touch-friendly
<button className="w-12 h-12">×</button>  // 48px minimum
```

---

## Part VI: Motion — Stillness, Then Life

### 6.1 The Philosophy

> *"Motion is earned, not decorative."*
> *"Stillness, then life."*

Animation happens when:
1. **State changes** — Something happened worth noticing
2. **Attention needed** — Focus the user
3. **Life indication** — System is alive (breathing)
4. **Joy moments** — Celebration of completion

Animation does NOT happen:
1. For decoration
2. On every hover
3. Constantly (except breathing)
4. When user prefers reduced motion

### 6.2 The Animation Primitives

```typescript
// Joy components — use these, don't reinvent
import { Breathe } from '@/components/joy/Breathe';
import { Pop } from '@/components/joy/Pop';
import { Shake } from '@/components/joy/Shake';
import { Shimmer } from '@/components/joy/Shimmer';
import { PageTransition } from '@/components/joy/PageTransition';
import { PersonalityLoading } from '@/components/joy/PersonalityLoading';
import { EmpathyError } from '@/components/joy/EmpathyError';
import { GrowingContainer } from '@/components/genesis/GrowingContainer';
```

| Primitive | Duration | When to Use |
|-----------|----------|-------------|
| `Breathe` | 6.75s loop | Living elements (health, status) |
| `Pop` | 200ms | Appearance, celebration |
| `Shake` | 500ms | Error, attention needed |
| `Shimmer` | — | Loading, processing |
| `PageTransition` | 250ms | Context changes |
| `GrowingContainer` | 300ms | Expanding content |

### 6.3 The Calming Breath

STARK BIOME breathing is asymmetric, inspired by 4-7-8 breathing:

```
  ┌─────────────────────────────────────────────────────────────────┐
  │                                                                 │
  │  Opacity                                                        │
  │  1.0 ─────────────────────────────────────────────────────────  │
  │       .                                                         │
  │       .    ╭──────────────╮                                     │
  │  0.97 .   ╱                ╲                                    │
  │       .  ╱                  ╲                                   │
  │       . ╱                    ╲                                  │
  │  0.94 ─╱                      ╲─────────────────────────────    │
  │       │                                                    │    │
  │       │ rest  gentle   hold      slow release       rest   │    │
  │       │ 15%   rise 25%  10%         50%            15%     │    │
  │       └────────────────────────────────────────────────────┘    │
  │                        6.75 seconds                             │
  └─────────────────────────────────────────────────────────────────┘
```

### 6.4 Temporal Coherence

When multiple elements animate simultaneously, they must coordinate:

```typescript
const { registerAnimation, getConstraintsFor } = useAnimationCoordination();

// Register when animation starts
registerAnimation('sidebar', {
  phase: 'exiting',
  progress: 0,
  startedAt: Date.now() / 1000,
  duration: 0.3,
});

// Check for coordination constraints
const constraints = getConstraintsFor('sidebar');
// → [{ source: 'sidebar', target: 'main', strategy: 'stagger', window: [...] }]
```

| Strategy | When | Effect |
|----------|------|--------|
| `lock_step` | Same phase | Both use same progress curve |
| `stagger` | Enter/exit overlap | One waits for other |
| `interpolate_boundary` | Active + transitioning | Independent with smooth boundary |
| `leader_follower` | Hierarchy | One leads, other follows |

---

## Part VII: Interactive Tokens — Living Text

### 7.1 The Seven Token Types

From `SYNTHESIS-living-spec.md`, these are the interactive elements within documents:

| Token | Pattern | Affordance |
|-------|---------|------------|
| **AGENTESE** | `` `world.house.manifest` `` | Hover → state; Click → navigate |
| **Task** | `- [x] Completed` | Click → toggle; Witness captured |
| **Portal** | `▶ [tests] ──→ 3 files` | Click → expand inline |
| **Code** | ` ```python ... ``` ` | Copy, Run, Import |
| **Image** | `![alt](path.png)` | Hover → AI analysis |
| **Principle** | `(AD-009)` | Hover → summary; Click → navigate |
| **Requirement** | `_Requirements: 7.1_` | Hover → text; Click → trace |

### 7.2 Token Styling (STARK BIOME)

From `tokens.css`:

```css
/* AGENTESE paths — life emerging */
.agentese-path-token {
  color: #6b8b6b;  /* life-mint */
}
.agentese-path-token:hover {
  background-color: rgba(74, 107, 74, 0.15);  /* life-sage with alpha */
  box-shadow: 0 0 8px rgba(139, 169, 139, 0.3);  /* earned glow */
  animation: token-breathe 6.75s cubic-bezier(0.4, 0, 0.1, 1) infinite;
}

/* Tasks — grounded in soil */
.task-checkbox-token:hover {
  background-color: rgba(26, 21, 18, 0.5);  /* soil-loam */
}
.task-checkbox-token--checked .task-checkbox-token__box {
  background-color: rgba(26, 46, 26, 0.4);  /* life-moss */
}

/* Code blocks — steel precision */
.code-block-token {
  background-color: #141418;  /* steel-carbon */
  border: 1px solid #28282f;  /* steel-gunmetal */
}
```

### 7.3 The Invariant: No Layout Shift

```css
/* INVARIANT: Hover elements must NEVER change container dimensions */

/* Rule 1: Always in DOM */
.code-block-token__copy {
  opacity: 0;  /* Not display: none */
}
.code-block-token:hover .code-block-token__copy {
  opacity: 1;
}

/* Rule 2: Position absolute for overlays */
.markdown-table-token__badge {
  position: absolute;
  top: 0.4em;
  right: 0.5em;
}

/* Rule 3: Reserve space for containers */
.code-block-token__header {
  min-height: 2em;  /* Space for copy button */
}
```

---

## Part VIII: Developer Experience

### 8.1 The Design Polynomial

The `useDesignPolynomial` hook mirrors the Python state machine:

```typescript
const {
  state,           // { density, contentLevel, motion, shouldAnimate }
  send,            // Dispatch inputs to state machine
  resizeViewport,  // Convenience: viewport change
  resizeContainer, // Convenience: container change
  toggleAnimation, // Convenience: enable/disable motion
  requestMotion,   // Convenience: request specific motion
} = useDesignPolynomial({ trackViewport: true });

// State machine has 120 states (3 × 4 × 5 × 2)
// Transitions are deterministic, law-verified
```

### 8.2 The Membrane Hook

```typescript
const {
  mode,                // 'compact' | 'comfortable' | 'spacious'
  setMode,             // Change mode
  focus,               // Current focus context
  setFocus,            // Change focus
  dialogueHistory,     // Co-thinking history
  appendDialogue,      // Add to dialogue
  crystallize,         // Capture a decision
  kblockIsolation,     // K-Block state
  kblockIsDirty,       // Has unsaved changes
  goHome,              // Return to welcome
} = useMembrane();
```

### 8.3 The Window Layout Hook

```typescript
const {
  density,    // 'compact' | 'comfortable' | 'spacious'
  isMobile,   // density === 'compact'
  isTablet,   // density === 'comfortable'
  isDesktop,  // density === 'spacious'
} = useWindowLayout();
```

### 8.4 Standard Patterns

**Pattern 1: Density-First Components**

```tsx
interface MyComponentProps {
  density: Density;
  // ... other props
}

export function MyComponent({ density, ...props }: MyComponentProps) {
  const spacing = SPACING[density];
  const fontSize = FONT_SIZE[density];

  return (
    <div style={{ gap: spacing.gap, padding: spacing.padding }}>
      {/* Content */}
    </div>
  );
}
```

**Pattern 2: Elastic Layout**

```tsx
function MyPage() {
  const { isMobile, density } = useWindowLayout();

  if (isMobile) {
    return (
      <div className="h-screen flex flex-col">
        <Canvas density={density} />
        <FloatingActions onToggle={handleToggle} />
        <BottomDrawer isOpen={panelOpen} onClose={closePanel}>
          <ControlPanel density={density} isDrawer />
        </BottomDrawer>
      </div>
    );
  }

  return (
    <ElasticSplit
      primary={<Canvas density={density} />}
      secondary={<ControlPanel density={density} />}
    />
  );
}
```

**Pattern 3: Earned Animation**

```tsx
function MyCard({ isNew }: { isNew: boolean }) {
  if (isNew) {
    return (
      <Pop>
        <CardContent />
      </Pop>
    );
  }

  return <CardContent />;
}

function HealthIndicator({ healthy }: { healthy: boolean }) {
  return (
    <Breathe intensity={healthy ? 0.3 : 0.1}>
      <StatusBadge healthy={healthy} />
    </Breathe>
  );
}
```

**Pattern 4: Context-Aware Focus**

```tsx
function FocusPane({ focus }: { focus: FocusContext }) {
  switch (focus.type) {
    case 'spec':
      return <SpecView path={focus.path} />;
    case 'file':
      return <FileView path={focus.path} />;
    case 'concept':
      return <ConceptView id={focus.id} />;
    case 'void':
      return <WelcomeView />;
  }
}
```

---

## Part IX: The Migration Checklist

### 9.1 For Every Component

- [ ] Uses `density` prop or `useWindowLayout()`?
- [ ] Has STARK BIOME colors only (no arbitrary hex)?
- [ ] Touch targets ≥ 48px on mobile?
- [ ] Uses elastic primitives (`ElasticSplit`, `BottomDrawer`)?
- [ ] No layout shift on hover (opacity transitions)?
- [ ] Uses joy components for animation?
- [ ] Respects `prefers-reduced-motion`?

### 9.2 For Every Page/View

- [ ] Fits within Membrane (no react-router)?
- [ ] Has all three density modes?
- [ ] Uses `FocusContext` to determine content?
- [ ] Dialogue can change focus?
- [ ] K-Block integration for editing?

### 9.3 Test Matrix

| Viewport | Test |
|----------|------|
| 375px | Compact mode, drawers, FABs |
| 768px | Comfortable mode, collapsed panels |
| 1024px | Spacious mode, full layout |
| 1440px | Spacious mode, extra breathing room |

---

## Part X: The Integration with Living Spec

The UI synthesis connects to the backend synthesis:

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                         LIVING SPEC ↔ MEMBRANE                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│                                                                                 │
│  BACKEND (SYNTHESIS-living-spec.md)       FRONTEND (this document)             │
│  ═══════════════════════════════════      ════════════════════════════════     │
│                                                                                 │
│  SpecNode (hypergraph node)          →    FocusPane (context-aware view)       │
│  SpecToken (7 types)                 →    InteractiveDocument (token render)   │
│  SpecMonad (isolation)               →    K-Block controls (Save/Discard)      │
│  SpecPolynomial (states)             →    useMembrane (mode state machine)     │
│  Witness (marks, decisions)          →    WitnessStream (real-time SSE)        │
│  SpecSheaf (coherence)               →    useDesignPolynomial (temporal)       │
│                                                                                 │
│  AGENTESE: self.spec.*               →    API calls via useSpecQuery           │
│  AGENTESE: self.kblock.*             →    useFileKBlock hook                   │
│  AGENTESE: self.witness.*            →    useWitnessStream hook                │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Part XI: Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Routes** | 0 | `grep -r "react-router" src/` returns nothing |
| **Density coverage** | 100% | Every component has 3 modes |
| **STARK compliance** | 100% | No arbitrary colors in codebase |
| **Touch targets** | 100% | No buttons < 48px on mobile |
| **Animation coordination** | 100% | No visual glitches on transitions |
| **K-Block integration** | 100% | All editable content uses monad |
| **Witness visibility** | 100% | Every commit shows in stream |

---

## Part XII: Connection to Principles

| Principle | How UI Synthesis Embodies It |
|-----------|------------------------------|
| **Tasteful** | STARK BIOME restraint; 90% steel, 10% life |
| **Curated** | Seven token types; eight elastic primitives |
| **Ethical** | Witness stream shows every decision |
| **Joy-Inducing** | Breathing animation; personality loading; empathy errors |
| **Composable** | Elastic primitives compose; polynomial composes |
| **Heterarchical** | Context determines view, not hierarchy |
| **Generative** | This spec can regenerate consistent UI |

---

## Part XIII: STARK BIOME Enhancement (2025-12-22)

### New Patterns Discovered

#### 4-7-8 Calming Breath Animation

The breathing animation now uses asymmetric timing inspired by 4-7-8 breathing:

```typescript
// Old: symmetric 2-4 second pulse
scale: [1, 1.05, 1]  // in-out-in

// New: asymmetric 4-7-8 pattern (6.75s default)
scale: [1, 1, 1.015, 1.015, 1]
times: [0, 0.15, 0.40, 0.50, 1.0]
// 15% rest → 25% rise → 10% hold → 50% release
```

**Speed tiers:**
- **Slow** (8.1s): Ambient elements, whisper presence
- **Normal** (6.75s): Active living elements
- **Fast** (5.4s): Quick attention, still calming

#### STARK-Muted Jewel Colors

Jewel identities now use muted, earned colors:

| Jewel | Old (Saturated) | New (STARK) |
|-------|-----------------|-------------|
| Brain | `#06B6D4` (Cyan) | `#4A6B6B` (Teal Moss) |
| Gestalt | `#22C55E` (Green) | `#4A6B4A` (Sage) |
| Forge | `#F59E0B` (Amber) | `#8B7355` (Umber) |
| Coalition | `#8B5CF6` (Violet) | `#6B5A7B` (Muted Violet) |
| Park | `#EC4899` (Pink) | `#7B5A6B` (Muted Rose) |
| Domain | `#EF4444` (Red) | `#8B5A4A` (Muted Rust) |

#### Muted Error States

Errors use muted rust (`#A65D4A`) instead of bright red:

```css
/* Old: Alarming */
color: #f87171;  /* red-400 — screams */

/* New: Empathetic */
color: #a65d4a;  /* muted rust — attention without alarm */
```

### Migration Notes

#### Color Changes

| Old | New | Rationale |
|-----|-----|-----------|
| `#3b82f6` (blue-500) | `#4a6b4a` (life-sage) | Primary actions |
| `#ef4444` (red-500) | `#8b5a4a` (muted rust) | Destructive actions |
| `#c62828` (red-800) | `#a65d4a` (state-alert) | Error text |
| `#06B6D4` (cyan-500) | `#4A6B6B` (teal-moss) | Brain jewel |

#### Animation Changes

- Breathing now uses 4-7-8 asymmetric pattern
- Default duration changed: 3s → 6.75s
- Opacity amplitude reduced: 15% → 6% max
- Scale amplitude reduced: 5% → 1.5% max

#### Files Updated

- `src/constants/jewels.ts` — STARK-muted jewel colors
- `src/components/joy/Breathe.tsx` — 4-7-8 calming breath
- `src/membrane/views/EditPane.css` — life-sage accent
- `src/membrane/views/SpecView.css` — muted error states
- `src/styles/globals.css` — STARK semantic colors

### Remaining Violations (Lower Priority)

Some demo/gallery files still use Tailwind arbitrary colors:
- `LayoutGallery.tsx` — demo indicators
- `CitizenCard.tsx` — legacy widget
- `ProjectionView.tsx` — demo output

These are acceptable for demo contexts but should not be pattern for production.

---

## Closing Meditation

The Membrane is not a dashboard. It is not documentation. It is not a shell.

**The Membrane is the surface where human and agent think together.**

One surface. Three modes. Steel foundation. Earned glow.

When we use it consistently — every component elastic, every animation earned, every token interactive, every edit witnessed — we stop documenting agents.

We become the agent.

> *"The frame is humble. The content glows."*
> *"Stop documenting agents. Become the agent."*

---

*Synthesis written: 2025-12-22*
*STARK BIOME Enhancement: 2025-12-22*
*Voice anchor: "Daring, bold, creative, opinionated but not gaudy"*
