# CSS Variables Reference
**Complete Design Token Inventory**
**Location**: `/src/styles/globals.css`
**Total Variables**: 107

---

## Variable Catalog (Alphabetical)

### A - Accent System
- `--accent` (legacy RGB: 196 167 125)
- `--accent-error` (#a65d4a - muted rust)
- `--accent-gold` (#d4b88c - glow-amber)
- `--accent-primary` (#c4a77d - glow-spore)
- `--accent-primary-bright` (#d4b88c - glow-amber)
- `--accent-secondary` (#8ba98b - glow-lichen)
- `--accent-success` (#4a6b4a - life-sage)

### B - Background & Borders
- `--background` (legacy RGB: 10 10 12)
- `--border-subtle` (#28282f - steel-gunmetal)

### C - Color System: Steel (90% - The Frame)
- `--color-steel-100` (#e0e0e0)
- `--color-steel-200` (#ccc)
- `--color-steel-300` (#a0a0a0)
- `--color-steel-400` (#888)
- `--color-steel-500` (#666)
- `--color-steel-600` (#444)
- `--color-steel-700` (#333)
- `--color-steel-800` (#252525)
- `--color-steel-850` (#1f1f1f)
- `--color-steel-900` (#1a1a1a)
- `--color-steel-950` (#0d0d0d)
- `--color-steel-carbon` (#141418)
- `--color-steel-gunmetal` (#28282f)
- `--color-steel-obsidian` (#0a0a0c)
- `--color-steel-slate` (#1c1c22)
- `--color-steel-zinc` (#3a3a44)

### C - Color System: Soil (Warm Undertones)
- `--color-soil-humus` (#2d221a)
- `--color-soil-loam` (#1a1512)

### C - Color System: Life (10% - Organic Accents)
- `--color-life-mint` (#6b8b6b)
- `--color-life-moss` (#1a2e1a)
- `--color-life-sage` (#4a6b4a)
- `--color-life-sprout` (#8bab8b)

### C - Color System: Bioluminescent Glow
- `--color-glow-amber` (#d4b88c)
- `--color-glow-lichen` (#8ba98b)
- `--color-glow-light` (#e5c99d)
- `--color-glow-spore` (#c4a77d)

### C - Color System: Edge Confidence
- `--color-edge-high` (#4caf50 - green, 80%+ confidence)
- `--color-edge-low` (#f44336 - red, <50%)
- `--color-edge-medium` (#ff9800 - orange, 50-80%)
- `--color-edge-unknown` (#9e9e9e - gray)

### C - Color System: Generic Components
- `--color-accent` (#6cf)
- `--color-border` (#333)
- `--color-hover` (#333)
- `--color-kbd-bg` (#2a2a2a)
- `--color-surface` (#1a1a1a)
- `--color-text` (#fff)
- `--color-text-muted` (#888)

### D - Duration (Transitions)
- `--duration-fast` (150ms)
- `--duration-instant` (100ms)
- `--duration-normal` (250ms)
- `--duration-slow` (400ms)

### E - Easing Functions
- `--ease-in-out-cubic` (cubic-bezier(0.65, 0, 0.35, 1))
- `--ease-out-expo` (cubic-bezier(0.19, 1, 0.22, 1))
- `--ease-spring` (cubic-bezier(0.34, 1.56, 0.64, 1))

### E - Elastic System
#### Breakpoints
- `--elastic-bp-lg` (1024px)
- `--elastic-bp-md` (768px)
- `--elastic-bp-sm` (640px)
- `--elastic-bp-xl` (1280px)

#### Gaps (Spacing)
- `--elastic-gap-lg` (16px - comfortable sections)
- `--elastic-gap-md` (10px - standard gaps)
- `--elastic-gap-sm` (6px - tight groupings)
- `--elastic-gap-xl` (24px - spacious areas)
- `--elastic-gap-xs` (3px - micro gaps)

#### Transitions (Composite)
- `--elastic-transition-fast` (var(--duration-fast) var(--ease-out-expo))
- `--elastic-transition-smooth` (var(--duration-normal) var(--ease-in-out-cubic))
- `--elastic-transition-spring` (var(--duration-slow) var(--ease-spring))

#### Z-Indices
- `--elastic-z-base` (0)
- `--elastic-z-dropdown` (200)
- `--elastic-z-modal` (300)
- `--elastic-z-sticky` (100)
- `--elastic-z-toast` (400)

### E - Event Types (Witness)
- `--brain-crystal` (#8b5cf6 - violet-500)
- `--evidence-pass` (#22c55e - green-500)
- `--lemma-proof` (#06b6d4 - cyan-500)
- `--teaching-wisdom` (#f97316 - orange-500)
- `--trail-path` (#10b981 - emerald-500)
- `--witness-mark` (#f59e0b - amber-500)

### F - Foreground & Fonts
- `--font-mono` ('JetBrains Mono', 'Fira Code', monospace)
- `--font-sans` ('Inter', -apple-system, BlinkMacSystemFont, sans-serif)
- `--foreground` (legacy RGB: 138 138 148)
- `--foreground-strong` (legacy RGB: 180 180 190)

### H - Health Indicators
- `--health-critical` (#ef4444 - red-500)
- `--health-degraded` (#facc15 - yellow-400)
- `--health-healthy` (#22c55e - green-500)
- `--health-warning` (#f97316 - orange-500)

### M - Muted
- `--muted` (legacy RGB: 58 58 68)

### R - Radius (Bare Edge System)
- `--radius-bare` (2px - cards, containers)
- `--radius-none` (0px - panels, canvas)
- `--radius-pill` (9999px - badges, tags)
- `--radius-soft` (4px - accent elements)
- `--radius-subtle` (3px - interactive surfaces)

### S - Scrollbar System
- `--scrollbar-radius` (var(--radius-bare))
- `--scrollbar-thumb-active` (rgba(233, 69, 96, 1))
- `--scrollbar-thumb-color` (rgba(15, 52, 96, 0.8))
- `--scrollbar-thumb-hover` (rgba(233, 69, 96, 0.9))
- `--scrollbar-track-color` (rgba(22, 33, 62, 0.6))
- `--scrollbar-transition` (200ms cubic-bezier(0.4, 0, 0.2, 1))
- `--scrollbar-width` (8px)

### S - Severity Levels
- `--severity-critical` (#ef4444 - red-500)
- `--severity-info` (#3b82f6 - blue-500)
- `--severity-warning` (#f59e0b - amber-500)

### S - Status States
- `--status-edge` (#ff9800 - orange, edge mode)
- `--status-error` (#f44336 - red, error state)
- `--status-failure` (#ef4444 - red-500)
- `--status-in-progress` (#3b82f6 - blue-500)
- `--status-insert` (#4caf50 - green, edit mode)
- `--status-needs-review` (#f59e0b - amber-500)
- `--status-normal` (#4a9eff - blue, normal mode)
- `--status-pending` (#6b7280 - gray-500)
- `--status-success` (#22c55e - green-500)
- `--status-visual` (#9c27b0 - purple, visual mode)
- `--status-witness` (#e91e63 - pink, witness mode)

### S - Strength Indicators
- `--strength-definitive` (#22c55e - green-500)
- `--strength-moderate` (#f59e0b - amber-500)
- `--strength-strong` (#3b82f6 - blue-500)
- `--strength-weak` (#6b7280 - gray-500)

### S - Surface Hierarchy
- `--surface-0` (#0a0a0c - deepest background)
- `--surface-1` (#141418 - card backgrounds)
- `--surface-2` (#1c1c22 - elevated surfaces)
- `--surface-3` (#28282f - borders, dividers)
- `--surface-4` (#353550 - elevated hover states)

### T - Text Hierarchy
- `--text-muted` (#5a5a64 - whisper)
- `--text-primary` (#e5e7eb - bright text)
- `--text-secondary` (#8a8a94 - muted body text)

---

## Usage Patterns

### STARK BIOME Philosophy
```css
/* 90% Steel (humble frame) */
background: var(--surface-0);
border: 1px solid var(--surface-3);

/* 10% Life (earned glow) */
color: var(--color-life-sage);
box-shadow: 0 0 8px var(--color-glow-spore);
```

### Mode-Dependent Styling
```css
/* Hypergraph Editor modes */
[data-mode='INSERT'] { --mode-accent: var(--status-insert); }
[data-mode='EDGE'] { --mode-accent: var(--status-edge); }
[data-mode='WITNESS'] { --mode-accent: var(--status-witness); }
```

### Confidence Visualization
```css
/* Edge confidence: high/medium/low */
.edge--high { border-color: var(--color-edge-high); }
.edge--medium { border-color: var(--color-edge-medium); }
.edge--low { border-color: var(--color-edge-low); }
```

### Witness Event Types
```css
/* Type-based coloring */
[data-type='witness.mark'] { color: var(--witness-mark); }
[data-type='brain.crystal'] { color: var(--brain-crystal); }
[data-type='evidence.pass'] { color: var(--evidence-pass); }
```

---

## Component CSS Classes

See `globals.css` for these utility classes:
- **Jewel scrollbars**: `.scroll-jewel-brain`, `.scroll-jewel-atelier`, etc.
- **Organic variants**: `.scroll-organic`, `.scroll-warm`, `.scroll-subtle`
- **Breathing effect**: `.scroll-breathe` (3.4s calming cycle)
- **Elastic layouts**: `.elastic-stack-v`, `.elastic-grid`, `.elastic-masonry`
- **Transitions**: `.elastic-card`, `.elastic-button` (micro-interactions)

---

**Design Philosophy**: "The frame is humble. The content glows."

Variables provide the **design language**. Component CSS provides the **grammar**.
