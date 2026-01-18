# SEVERE STARK: The New Aesthetic Specification

> *"Every pixel contains information. Joy is absent. The glow is earned."*

**Status:** Canonical
**Created:** 2026-01-17
**Supersedes:** Previous "comfortable" STARK BIOME defaults

---

## Design Axioms

### A1: Yahoo Japan Density

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

### A2: Near-Black Steel

The void is not pure black. It has texture — the faintest hint of blue-gray.

```
BACKGROUND = #0a0a0c (steel-obsidian)
NOT #000000 (pure black)

Rationale: Pure black is a void. Steel-obsidian is a surface.
The difference is subtle but felt.
```

### A3: Rare Earned Glow

Amber appears only for significant moments. It must be earned.

```
GLOW TRIGGERS (exhaustive list):
- Axiom grounded (derivation complete)
- Contradiction resolved (synthesis achieved)
- Crystal formed (memory crystallized)
- Witness mark created

GLOW FORBIDDEN:
- Hover states (use border/underline instead)
- Selection (use inverse video)
- Navigation (use weight/underline)
- Decoration (NEVER)
```

### A4: Joy Absent

No confetti. No shimmer. No bounce. No celebration.

```
PERMITTED MOTION:
- Cursor blink
- Scroll
- Panel open/close (instant, no easing)
- Text appear (instant)

FORBIDDEN MOTION:
- Easing curves
- Spring animations
- Particle effects
- Breathing/pulsing
- Transitions > 50ms
```

---

## Typography System (Severe)

### Font Stack

```css
--font-data: 'JetBrains Mono', 'SF Mono', 'Consolas', monospace;
--font-prose: 'Inter', -apple-system, sans-serif;
```

**Rationale:**
- **Mono for data:** Code, numbers, K-Blocks, identifiers, paths — alignment matters
- **Sans for prose:** Body text, descriptions, long-form — readability matters

**Usage:**
```css
/* Data contexts */
.kblock, .code, .path, .id, .number, pre, code { font-family: var(--font-data); }

/* Prose contexts */
body, p, .description, .prose { font-family: var(--font-prose); }
```

### Size Scale (Dense but WCAG Compliant)

```css
--text-xs: 10px;   /* Timestamps, metadata, counts */
--text-sm: 11px;   /* Secondary labels, hints */
--text-base: 12px; /* Body text, DEFAULT (WCAG AA minimum) */
--text-md: 13px;   /* Important body, nav links */
--text-lg: 14px;   /* Section headers */
--text-xl: 15px;   /* Page titles */
--text-2xl: 16px;  /* Hero only (rare) */
```

**Note:** 12px base maintains WCAG AA compliance while denser than typical Western (14-16px). Japanese-level density achieved through tight line-height and spacing.

### Line Height (Tight)

```css
--leading-none: 1.0;   /* Single-line labels */
--leading-tight: 1.2;  /* Body text, DEFAULT */
--leading-snug: 1.3;   /* Multi-paragraph */
--leading-normal: 1.4; /* Long-form reading (rare) */
```

### Font Weight

```css
--weight-normal: 400;  /* Body text */
--weight-medium: 500;  /* Emphasis within text */
--weight-bold: 700;    /* Headers, navigation */
```

**Hierarchy through weight, not size or whitespace.**

---

## Spacing System (Compressed)

### Gap Scale

```css
--gap-0: 0px;      /* Touching elements */
--gap-1: 2px;      /* Micro separation */
--gap-2: 4px;      /* Default between items */
--gap-3: 6px;      /* Between groups */
--gap-4: 8px;      /* Section separation */
--gap-5: 12px;     /* Major sections */
--gap-6: 16px;     /* Page-level only */
```

**Comparison to current:**
| Current | Severe |
|---------|--------|
| --space-xs: 3.2px | --gap-1: 2px |
| --space-sm: 6.4px | --gap-2: 4px |
| --space-md: 13.6px | --gap-3: 6px |
| --space-lg: 20px | --gap-4: 8px |

**50% reduction in spacing.**

### Padding Scale

```css
--pad-0: 0px;
--pad-1: 2px;      /* Inline elements */
--pad-2: 4px;      /* Buttons, badges */
--pad-3: 6px;      /* Cards, panels */
--pad-4: 8px;      /* Containers */
```

---

## Color System (Monochrome + Rare Glow)

### Backgrounds (Steel Scale)

```css
--bg-void: #0a0a0c;      /* Deepest, page background */
--bg-surface: #0f0f12;   /* Cards, panels */
--bg-elevated: #141418;  /* Hover states, overlays */
--bg-highlight: #1c1c22; /* Selection background */
```

### Foregrounds (Gray Scale)

```css
--fg-muted: #3a3a44;     /* Disabled, hints */
--fg-secondary: #5a5a64; /* Metadata, timestamps */
--fg-primary: #8a8a94;   /* Body text, DEFAULT */
--fg-strong: #b0b0b8;    /* Emphasized text */
--fg-intense: #e0e0e8;   /* Headers, active items */
```

### Borders

```css
--border-subtle: #1c1c22;  /* Faint separation */
--border-default: #28282f; /* Standard borders */
--border-strong: #3a3a44;  /* Emphasized borders */
```

### Accent (Earned Glow ONLY)

```css
--glow-earned: #c4a77d;        /* The amber glow */
--glow-earned-bright: #d4b88c; /* Intense moment */
```

**Usage:** ONLY for axiom grounding, contradiction resolution, crystal formation, witness marks.

### Semantic

```css
--error: #8b4a4a;   /* Muted red, not alarming */
--warning: #8b6b4a; /* Muted orange */
--success: #4a6b4a; /* Muted green (rare) */
```

---

## Layout Patterns

### Grid (Dense)

```css
/* Desktop: 5 columns */
.grid-dense {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: var(--gap-2);
}

/* Tablet: 3 columns */
@media (max-width: 1024px) {
  .grid-dense {
    grid-template-columns: repeat(3, 1fr);
  }
}

/* Mobile: 2 columns */
@media (max-width: 640px) {
  .grid-dense {
    grid-template-columns: repeat(2, 1fr);
  }
}
```

### Navigation (50+ Links Visible)

```css
.nav-dense {
  display: flex;
  flex-wrap: wrap;
  gap: var(--gap-1);
  font-size: var(--text-sm);
  line-height: var(--leading-tight);
}

.nav-dense a {
  padding: var(--pad-1) var(--pad-2);
  white-space: nowrap;
}
```

### Panels (No Padding Waste)

```css
.panel-severe {
  padding: var(--pad-3);
  border: 1px solid var(--border-default);
  background: var(--bg-surface);
}

.panel-severe h3 {
  margin: 0 0 var(--gap-2) 0;
  font-size: var(--text-md);
  font-weight: var(--weight-bold);
}
```

---

## Interaction States

### Hover (Subtle, No Glow)

```css
/* Links */
a:hover {
  text-decoration: underline;
  /* NO color change, NO glow */
}

/* Buttons */
button:hover {
  background: var(--bg-elevated);
  /* NO shadow, NO transform */
}

/* Cards */
.card:hover {
  border-color: var(--border-strong);
  /* NO shadow, NO scale */
}
```

### Focus (High Contrast)

```css
:focus-visible {
  outline: 1px solid var(--fg-intense);
  outline-offset: 1px;
  /* Thin, visible, no glow */
}
```

### Selection (Inverse Video)

```css
::selection {
  background: var(--fg-primary);
  color: var(--bg-void);
}
```

### Active (Instant)

```css
button:active {
  background: var(--bg-highlight);
  /* Instant change, no transition */
}
```

---

## Transitions (Almost None)

```css
/* The ONLY permitted transitions */
--transition-instant: 0ms;
--transition-micro: 50ms linear;

/* Usage: panel open/close only */
.panel {
  transition: transform var(--transition-micro);
}

/* Everything else: INSTANT */
a, button, .card, input, * {
  transition: none;
}
```

---

## Component Patterns

### Dense List

```html
<ul class="list-dense">
  <li><a href="#">Link 1</a> <span class="meta">42</span></li>
  <li><a href="#">Link 2</a> <span class="meta">17</span></li>
  <!-- 50+ items visible -->
</ul>
```

```css
.list-dense {
  margin: 0;
  padding: 0;
  list-style: none;
  font-size: var(--text-sm);
  line-height: var(--leading-tight);
}

.list-dense li {
  display: flex;
  justify-content: space-between;
  padding: var(--pad-1) 0;
  border-bottom: 1px solid var(--border-subtle);
}

.list-dense .meta {
  color: var(--fg-secondary);
  font-size: var(--text-xs);
}
```

### Dense Table

```css
.table-dense {
  width: 100%;
  border-collapse: collapse;
  font-size: var(--text-sm);
}

.table-dense th,
.table-dense td {
  padding: var(--pad-1) var(--pad-2);
  border: 1px solid var(--border-subtle);
  text-align: left;
}

.table-dense th {
  background: var(--bg-surface);
  font-weight: var(--weight-bold);
}
```

### Earned Glow Moment

```css
/* ONLY for significant moments */
.glow-earned {
  color: var(--glow-earned);
  text-shadow: 0 0 8px var(--glow-earned);
}

/* Animation: instant appear, slow fade */
@keyframes glow-fade {
  0% { opacity: 1; text-shadow: 0 0 12px var(--glow-earned); }
  100% { opacity: 1; text-shadow: none; }
}

.glow-moment {
  animation: glow-fade 2s ease-out forwards;
}
```

---

## Migration Checklist

### tokens.css Changes

- [ ] Replace all `--space-*` with `--gap-*` (50% smaller)
- [ ] Replace all `--font-size-*` with new scale (11px base)
- [ ] Replace all `--line-height-*` with tight scale (1.2 default)
- [ ] Remove all `--transition-*` except instant/micro
- [ ] Remove all spring/bounce easing functions

### Component Changes

- [ ] Remove all `Breathe` component usage
- [ ] Remove all `Pop` component usage
- [ ] Remove all `Shimmer` component usage
- [ ] Remove all `celebrate()` calls
- [ ] Replace hover shadows with border changes
- [ ] Replace hover transforms with color changes

### Layout Changes

- [ ] Increase grid columns (3→5 on desktop)
- [ ] Reduce all padding by 50%
- [ ] Remove progressive disclosure (show everything)
- [ ] Add dense navigation patterns

---

## Reference: Yahoo Japan Screenshots

For calibration, reference these patterns:
- Navigation bars with 100+ links
- 10px body text as norm
- 4-5 column layouts
- Information hierarchy through weight/color only
- No decorative whitespace

---

*"The void speaks. The glow is earned. Every pixel serves."*
