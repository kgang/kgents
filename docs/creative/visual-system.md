# Visual System

> *"Colors are not decoration—they are semantic. Spacing is not arbitrary—it is rhythm."*

**Status**: Foundation Document
**Prerequisites**: `philosophy.md`
**Implementation**: Design tokens → Tailwind config → Component library

---

## The Generative Visual System

Every visual decision in kgents derives from **semantic meaning**, not aesthetic whim. This section defines the algebra of visual elements.

---

## Part I: Color System

### The Semantic Color Model

Colors in kgents are not chosen—they are **derived from meaning**:

```
Meaning → Hue → Variants (light/base/dark)
```

| Semantic Role | Hue | Base | Meaning |
|---------------|-----|------|---------|
| **Knowledge** | Cyan | `#06B6D4` | Brain, memory, understanding |
| **Growth** | Green | `#22C55E` | Gestalt, health, progress |
| **Cultivation** | Lime | `#84CC16` | Gardener, nurturing, emergence |
| **Creation** | Amber | `#F59E0B` | Atelier, creativity, warmth |
| **Collaboration** | Violet | `#8B5CF6` | Coalition, synthesis, harmony |
| **Drama** | Pink | `#EC4899` | Park, narrative, performance |
| **Urgency** | Red | `#EF4444` | Domain, crisis, alert |
| **Neutral** | Slate | `#64748B` | Structure, chrome, system |

### The Crown Jewel Palette

Each Crown Jewel has a primary color that defines its personality:

```typescript
const JEWEL_COLORS = {
  brain:     { primary: '#06B6D4', accent: '#0891B2', bg: '#0E7490' },  // Cyan family
  gestalt:   { primary: '#22C55E', accent: '#16A34A', bg: '#15803D' },  // Green family
  gardener:  { primary: '#84CC16', accent: '#65A30D', bg: '#4D7C0F' },  // Lime family
  atelier:   { primary: '#F59E0B', accent: '#D97706', bg: '#B45309' },  // Amber family
  coalition: { primary: '#8B5CF6', accent: '#7C3AED', bg: '#6D28D9' },  // Violet family
  park:      { primary: '#EC4899', accent: '#DB2777', bg: '#BE185D' },  // Pink family
  domain:    { primary: '#EF4444', accent: '#DC2626', bg: '#B91C1C' },  // Red family
} as const;
```

### State Colors

System states use consistent colors:

| State | Color | Usage |
|-------|-------|-------|
| **Success** | Green `#22C55E` | Completed actions, healthy states |
| **Warning** | Amber `#F59E0B` | Attention needed, degraded mode |
| **Error** | Red `#EF4444` | Failures, critical issues |
| **Info** | Cyan `#06B6D4` | Informational, neutral updates |
| **Pending** | Slate `#64748B` | Waiting, loading, in-progress |

### The Gray Scale

Grays are crucial—they form the canvas:

```typescript
const GRAYS = {
  50:  '#F8FAFC',  // Near-white backgrounds
  100: '#F1F5F9',  // Subtle backgrounds
  200: '#E2E8F0',  // Borders, dividers
  300: '#CBD5E1',  // Disabled text
  400: '#94A3B8',  // Secondary text
  500: '#64748B',  // Muted text
  600: '#475569',  // Body text (dark mode)
  700: '#334155',  // Emphasis
  800: '#1E293B',  // Card backgrounds (dark mode)
  900: '#0F172A',  // App background (dark mode)
  950: '#020617',  // Deep backgrounds
} as const;
```

### Dark Mode First

kgents is **dark mode first**. The dark theme is the primary design surface:

```
Background canvas:  gray-900 (#0F172A)
Card surface:       gray-800 (#1E293B)
Elevated surface:   gray-700 (#334155)
Borders:            gray-700 with 50% opacity
Text primary:       white
Text secondary:     gray-400 (#94A3B8)
Text muted:         gray-500 (#64748B)
```

**Rationale:** Dark mode reduces eye strain during long sessions, emphasizes colored content, and matches the "contemplative" mood we seek.

---

## Part II: Typography

### The Type Scale

Typography follows a **1.25 ratio** scale (Major Third):

```typescript
const TYPE_SCALE = {
  xs:   '12px',   // Fine print, timestamps
  sm:   '14px',   // Secondary text, labels
  base: '16px',   // Body text
  lg:   '18px',   // Lead text, emphasis
  xl:   '20px',   // Section headers
  '2xl': '24px',  // Page headers
  '3xl': '30px',  // Hero text
  '4xl': '36px',  // Display (rare)
} as const;
```

### Font Families

```typescript
const FONTS = {
  sans:  'Inter, system-ui, sans-serif',      // Body, UI
  mono:  'JetBrains Mono, monospace',         // Code, data
  display: 'Inter, system-ui, sans-serif',    // Headers (same as sans, by weight)
} as const;
```

**Why Inter?**
- Excellent readability at small sizes
- Wide character support
- Variable weight for fluid hierarchy
- Neutral but warm character

**Why JetBrains Mono?**
- Distinguished from body text
- Excellent legibility for code
- Personality in technical contexts

### Font Weights

```typescript
const WEIGHTS = {
  normal:   '400',  // Body text
  medium:   '500',  // Emphasis, labels
  semibold: '600',  // Section headers
  bold:     '700',  // Strong emphasis, titles
} as const;
```

### Type Pairing Guidelines

| Context | Family | Size | Weight |
|---------|--------|------|--------|
| Body text | Sans | base (16px) | normal |
| Labels | Sans | sm (14px) | medium |
| Section header | Sans | xl (20px) | semibold |
| Page title | Sans | 2xl (24px) | bold |
| Code | Mono | sm (14px) | normal |
| Data values | Mono | base (16px) | normal |

---

## Part III: Spacing System

### The Spacing Scale

Spacing follows a **4px base unit** with exponential growth:

```typescript
const SPACING = {
  px:  '1px',     // Fine borders only
  0.5: '2px',     // Micro adjustments
  1:   '4px',     // Tight gaps
  2:   '8px',     // Default gap
  3:   '12px',    // Component padding
  4:   '16px',    // Card padding
  5:   '20px',    // Section spacing
  6:   '24px',    // Large gaps
  8:   '32px',    // Major sections
  10:  '40px',    // Page sections
  12:  '48px',    // Hero spacing
  16:  '64px',    // Maximum spacing
} as const;
```

### Rhythm Guidelines

| Element | Padding | Gap |
|---------|---------|-----|
| Glyph (inline) | 0 | 1 (4px) |
| Button (sm) | 2/3 (8px/12px) | - |
| Button (md) | 3/4 (12px/16px) | - |
| Card | 4 (16px) | 3 (12px) |
| Section | 6 (24px) | 4 (16px) |
| Page | 8 (32px) | 6 (24px) |

### The Composition Operators

Spacing composes just like agents:

```
// Horizontal composition (>>)
gap-x: spacing between horizontally arranged elements

// Vertical composition (//)
gap-y: spacing between vertically arranged elements

// Layout: space-between for justified, gap for uniform
```

---

## Part IV: Border & Shadow

### Border Radius Scale

```typescript
const RADII = {
  none: '0',
  sm:   '4px',    // Subtle rounding
  md:   '8px',    // Default for cards
  lg:   '12px',   // Prominent rounding
  xl:   '16px',   // Large containers
  full: '9999px', // Pills, circles
} as const;
```

**Guidelines:**
- Glyphs: `none` or `full`
- Buttons: `md` (8px)
- Cards: `lg` (12px)
- Modals: `xl` (16px)
- Avatars/tags: `full`

### Shadow System

Shadows are **minimal in dark mode**. Use elevation through color, not shadow:

```typescript
const SHADOWS = {
  sm:   '0 1px 2px rgba(0, 0, 0, 0.05)',
  md:   '0 4px 6px rgba(0, 0, 0, 0.1)',
  lg:   '0 10px 15px rgba(0, 0, 0, 0.15)',
  glow: '0 0 20px rgba(6, 182, 212, 0.3)',  // Accent glow
} as const;
```

**Guidelines:**
- Use shadow sparingly in dark mode
- Prefer border/background differentiation
- Reserve `glow` for emphasis states

---

## Part V: Iconography

### Icon Guidelines

**Style:**
- 24px base size
- 2px stroke weight
- Rounded line caps
- Filled variants for selected states

**Icon Semantic Groups:**

| Group | Examples | Usage |
|-------|----------|-------|
| Navigation | Home, Back, Menu | App chrome |
| Action | Plus, Edit, Delete | User actions |
| Status | Check, X, Alert | State feedback |
| Content | File, Folder, Code | Entity types |
| Agent | Brain, Gear, Network | Agent concepts |

**Icon Library:** Lucide (open source, consistent style)

### The Emoji System

Emojis are **first-class citizens** in kgents, not decorative:

```typescript
const JEWEL_EMOJI = {
  brain:     '🧠',
  gestalt:   '🏗️',
  gardener:  '🌱',
  atelier:   '🎨',
  coalition: '🤝',
  park:      '🎭',
  domain:    '🏛️',
} as const;
```

**Usage:**
- Loading states (with personality)
- Empty states (with character)
- Celebrations (earned, not gratuitous)
- Error states (empathy, not panic)

---

## Part VI: Layout Patterns

### The Three Densities

All layouts adapt to **three density levels** (see AD-008):

| Density | Breakpoint | Characteristics |
|---------|------------|-----------------|
| `compact` | < 768px | Single column, drawers, floating actions |
| `comfortable` | 768-1024px | Two columns, collapsible panels |
| `spacious` | > 1024px | Full layout, resizable dividers |

### Layout Primitives

```tsx
// Horizontal stack (>> operator)
<HStack gap={2}>{children}</HStack>

// Vertical stack (// operator)
<VStack gap={4}>{children}</VStack>

// Split pane (adapts by density)
<ElasticSplit primary={<Canvas />} secondary={<Panel />} />

// Card container
<ElasticCard density={density}>{children}</ElasticCard>
```

### The Dashboard Pattern

Standard dashboard layout:

```
┌─────────────────────────────────────────────┐
│  Header (h-16)                              │
├────────┬────────────────────────────────────┤
│        │                                    │
│  Nav   │           Canvas                   │
│  (w-64)│           (flex-1)                 │
│        │                                    │
│        │                                    │
├────────┴────────────────────────────────────┤
│  Status bar (h-8, optional)                 │
└─────────────────────────────────────────────┘
```

Adapts in compact mode:
- Nav collapses to hamburger + drawer
- Header slim or hidden
- Canvas fills viewport
- Floating actions provide navigation

---

## Part VII: Component Visual Patterns

### The Card Pattern

```
┌─────────────────────────────────────┐
│  ○ Header with glyph        Status  │
├─────────────────────────────────────┤
│                                     │
│  Content area                       │
│  (varies by card type)              │
│                                     │
├─────────────────────────────────────┤
│  Footer / Actions (optional)        │
└─────────────────────────────────────┘
```

Visual tokens:
- Background: `gray-800`
- Border: `gray-700/50`
- Radius: `lg` (12px)
- Padding: `4` (16px)
- Glyph position: top-left with header

### The Glyph Pattern

Glyphs are **atomic visual units**:

```tsx
<Glyph
  char="◉"
  phase="active"
  animate="breathe"
  fg="#06B6D4"
/>
```

Glyph states:
| Phase | Character | Animation | Color |
|-------|-----------|-----------|-------|
| idle | ○ | none | gray-400 |
| active | ◉ | breathe | primary |
| processing | ◐ | pulse | primary |
| success | ● | pop | green |
| error | ◌ | shake | red |

---

## Part VIII: Implementation Guide

### Design Tokens → Code

All visual values should come from tokens:

```tsx
// ❌ Don't use raw values
<div style={{ padding: '12px', color: '#06B6D4' }} />

// ✅ Use semantic tokens
<div className="p-3 text-cyan-500" />

// ✅ Or use jewel-specific tokens
<div style={{ color: JEWEL_COLORS.brain.primary }} />
```

### Tailwind Configuration

Extend Tailwind with kgents tokens:

```javascript
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        'jewel-brain': '#06B6D4',
        'jewel-gestalt': '#22C55E',
        // ... etc
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      spacing: {
        // Uses default Tailwind spacing scale (4px base)
      },
    },
  },
};
```

### Component Consistency Checklist

When building a component, verify:

- [ ] Colors from semantic palette (not raw hex)
- [ ] Typography from scale (not arbitrary sizes)
- [ ] Spacing from scale (multiples of 4px)
- [ ] Border radius from scale
- [ ] Adapts to three density levels
- [ ] Has personality in loading/error states
- [ ] Works in composition (`>>`, `//`)

---

## Sources

- [99designs Minimalist Branding](https://99designs.com/inspiration/branding/minimalist) — Minimalism with warmth
- [Zen Design Inspiration](https://99designs.com/inspiration/designs/zen) — Restraint as expression
- [Creating a Visual Style Guide](https://zen.agency/creating-a-visual-style-guide-for-your-business/) — Systematic brand identity
- [Data Visualization Design Principles](https://guides.lib.berkeley.edu/data-visualization/design) — Color and hierarchy best practices

---

*"The token is the truth. Derive, don't decide."*
