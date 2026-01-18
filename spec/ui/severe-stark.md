# SEVERE STARK: The Aesthetic Specification

> *"Every pixel contains information. Joy is absent. The glow is earned."*

**Status:** Canonical
**Grounded In:** spec/ui/axioms.md (A4: Joy Absent, A7: Disgust Prevention, A8: Understandability)

---

## Design Axioms

### Yahoo Japan Density (A8)

Every pixel serves information. No decorative whitespace. Navigation is learned, not discovered.

```
DENSITY = MAXIMUM
- Text: 11-12px default, 10px for metadata
- Line height: 1.2-1.3 (tight)
- Gaps: 2-4px between elements
- Columns: 4-5 on desktop, 2-3 on tablet
- Links visible: 50+ above fold
- Progressive disclosure: NONE (everything visible)
```

### Near-Black Steel

The void is not pure black. It has texture — the faintest hint of blue-gray.

```
BACKGROUND = #0a0a0c (steel-obsidian)
NOT #000000 (pure black)

Rationale: Pure black is a void. Steel-obsidian is a surface.
The difference is subtle but felt.
```

### Rare Earned Glow

Amber appears only for significant moments. It must be earned.

```
GLOW TRIGGERS (exhaustive list):
- Axiom grounded (derivation complete)
- Contradiction resolved (synthesis achieved)
- Crystal formed (memory crystallized)
- Witness mark created
- K-Block committed

GLOW FORBIDDEN:
- Hover states (use border/underline instead)
- Selection (use inverse video)
- Navigation (use weight/underline)
- Decoration (NEVER)
```

### Joy Absent (A4)

No confetti. No shimmer. No bounce. No celebration.

```
PERMITTED MOTION:
- Cursor blink
- Scroll
- Panel open/close (instant, no easing)
- Text appear (instant)
- Glow fade (2s, earned only)

FORBIDDEN MOTION:
- Easing curves (except glow fade)
- Spring animations
- Particle effects
- Breathing/pulsing
- Transitions > 50ms
```

---

## Typography System

### Font Stack

```css
--font-data: 'JetBrains Mono', 'SF Mono', 'Consolas', monospace;
--font-prose: 'Inter', -apple-system, sans-serif;
```

**Usage:**
- **Mono for data:** Code, numbers, K-Blocks, identifiers, paths
- **Sans for prose:** Body text, descriptions, long-form

### Size Scale (Dense but WCAG AA Compliant)

```css
--text-xs: 10px;   /* Timestamps, metadata, counts */
--text-sm: 11px;   /* Secondary labels, hints */
--text-base: 12px; /* Body text, DEFAULT */
--text-md: 13px;   /* Important body, nav links */
--text-lg: 14px;   /* Section headers */
--text-xl: 15px;   /* Page titles */
```

### Line Height (Tight)

```css
--leading-tight: 1.2;  /* Body text, DEFAULT */
--leading-snug: 1.3;   /* Multi-paragraph */
```

### Font Weight

```css
--weight-normal: 400;  /* Body text */
--weight-medium: 500;  /* Emphasis */
--weight-bold: 700;    /* Headers, navigation */
```

**Hierarchy through weight, not size or whitespace.**

---

## Spacing System (Compressed)

### Gap Scale

```css
--gap-1: 2px;      /* Micro separation */
--gap-2: 4px;      /* Default between items */
--gap-3: 6px;      /* Between groups */
--gap-4: 8px;      /* Section separation */
--gap-5: 12px;     /* Major sections */
--gap-6: 16px;     /* Page-level only */
```

### Padding Scale

```css
--pad-1: 2px;      /* Inline elements */
--pad-2: 4px;      /* Buttons, badges */
--pad-3: 6px;      /* Cards, panels */
--pad-4: 8px;      /* Containers */
```

---

## Color System (Monochrome + Rare Glow)

### Backgrounds (Steel Scale)

```css
--bg-void: #0a0a0c;      /* Page background */
--bg-surface: #0f0f12;   /* Cards, panels */
--bg-elevated: #141418;  /* Hover states */
--bg-highlight: #1c1c22; /* Selection */
```

### Foregrounds (Gray Scale — WCAG AA Compliant)

```css
--fg-muted: #7a7a84;     /* Hints (≥4.5:1 contrast) */
--fg-secondary: #8a8a94; /* Metadata */
--fg-primary: #b0b0b8;   /* Body text */
--fg-strong: #c0c0c8;    /* Emphasized */
--fg-intense: #e0e0e8;   /* Headers */
```

### Borders

```css
--border-subtle: #1c1c22;  /* Faint */
--border-default: #28282f; /* Standard */
--border-strong: #3a3a44;  /* Emphasized */
```

### Accent (Earned Glow ONLY)

```css
--glow-earned: #c4a77d;        /* The amber glow */
--glow-earned-bright: #d4b88c; /* Intense moment */
```

### Semantic

```css
--error: #8b4a4a;   /* Muted red */
--warning: #8b6b4a; /* Muted orange */
--success: #4a6b4a; /* Muted green (rare) */
```

---

## Interaction States

### Hover (Subtle, No Glow)

```css
a:hover { text-decoration: underline; /* NO color change */ }
button:hover { background: var(--bg-elevated); /* NO shadow */ }
.card:hover { border-color: var(--border-strong); /* NO scale */ }
```

### Focus (High Contrast)

```css
:focus-visible {
  outline: 1px solid var(--fg-intense);
  outline-offset: 1px;
}
```

### Selection (Inverse Video)

```css
::selection {
  background: var(--fg-primary);
  color: var(--bg-void);
}
```

---

## Transitions

```css
/* The ONLY permitted transitions */
--transition-instant: 0ms;
--transition-micro: 50ms linear;
--transition-glow: 2s ease-out; /* Earned glow only */

/* Everything else: INSTANT */
```

---

## Layout Patterns

### Workspace Grid (Invariant)

```css
/* Fixed proportions — content adapts, containers don't */
.workspace-grid {
  grid-template-columns: 10% 15% 1fr 25%;
}
```

See: `spec/ui/design-decisions.md` (Decision #14)

### Dense Grid

```css
.grid-dense {
  grid-template-columns: repeat(5, 1fr); /* Desktop */
  gap: var(--gap-2);
}
```

### Dense Navigation

```css
.nav-dense {
  display: flex;
  flex-wrap: wrap;
  gap: var(--gap-1);
  font-size: var(--text-sm);
}
```

---

## Provenance Visual Encoding

From A2 (Sloppification Axiom):

| Provenance | Rendering | Indicator |
|------------|-----------|-----------|
| kent (human) | Full intensity | None |
| fusion (dialectic) | Full intensity | ⚡ mark |
| claude (reviewed) | Medium intensity | ◇ |
| claude (unreviewed) | Low intensity + amber border | ◆ |

---

## Implementation Files

- `src/design/severe-tokens.css` — Token definitions
- `src/styles/severe-base.css` — Base reset
- `src/styles/layout-constraints.css` — Grid constraints

---

*"The void speaks. The glow is earned. Every pixel serves."*
