# Constitutional Components — Visual Design Guide

## Component Preview

### ConstitutionalBadge (Three States)

```
┌─────────────────────────────────┐
│ High Score (>80)                │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────┐            │
│  │ CONST  92  ▸    │  ← White   │
│  └─────────────────┘            │
│                                 │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Medium Score (50-80)            │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────┐            │
│  │ CONST  65  ▸    │  ← Gray    │
│  └─────────────────┘            │
│                                 │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│ Low Score (<50)                 │
├─────────────────────────────────┤
│                                 │
│  ┌─────────────────┐            │
│  │ CONST  42  ▸    │  ← Dim     │
│  └─────────────────┘            │
│                                 │
└─────────────────────────────────┘
```

**Badge Anatomy**:
```
┌──────────────────────────┐
│ CONST   92   ▸           │
│   ▲      ▲   ▲           │
│   │      │   └─ Click indicator
│   │      └───── Score (0-100)
│   └──────────── Label
└──────────────────────────┘
```

### ConstitutionalRadar (Heptagon)

```
                  TASTEFUL
                     ●
                    / \
                   /   \
                  /     \
    GENERATIVE   ●       ●   CURATED
                  \     /
                   \   /
    HETERARCHICAL   \ /       ETHICAL
                  ● + ●
                   / \
                  /   \
    COMPOSABLE   ●     ●   JOY-INDUCING
```

**Radar Features**:
- 7 vertices (one per principle)
- Concentric grid at 0.2, 0.4, 0.6, 0.8, 1.0
- Radial axes from center to vertices
- Filled polygon connecting score points
- Color-coded vertices (white/gray/dim)

### Full Integration (in AssistantMessage)

```
┌─────────────────────────────────────────────────────┐
│ AssistantMessage                                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────┐  ┌──────────────────┐        │
│  │ HIGH CONFIDENCE  │  │ CONST  88  ▸     │ ← Click│
│  │ (P=0.92)         │  └──────────────────┘        │
│  └──────────────────┘                              │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │ The implementation follows the spec...      │   │
│  │ [response content]                          │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
│  ┌─────────────────────────────────────────────┐   │
│  │            CONSTITUTIONAL RADAR              │   │
│  │                                              │   │
│  │              TASTEFUL (88)                   │   │
│  │                  ●                           │   │
│  │                 /|\                          │   │
│  │                / | \                         │   │
│  │   GENERATIVE  ●  |  ●  CURATED              │   │
│  │       (91)      \|/      (85)               │   │
│  │                  ●                           │   │
│  │                 / \                          │   │
│  │  HETERARCHICAL ●   ● ETHICAL                │   │
│  │      (87)           (95)                    │   │
│  │                 \ /                          │   │
│  │      COMPOSABLE ● ● JOY-INDUCING            │   │
│  │          (90)       (85)                    │   │
│  │                                              │   │
│  └─────────────────────────────────────────────┘   │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## Design Tokens

### Typography

```css
font-family: 'Berkeley Mono', 'JetBrains Mono', monospace;
font-size: 10px - 12px (size dependent);
font-weight: 700 (labels), 400 (secondary text);
text-transform: uppercase;
letter-spacing: 0.05em;
```

### Colors (Brutalist Palette)

```css
/* Surface */
--brutalist-bg: #0a0a0a           /* Darkest background */
--brutalist-surface: #141414       /* Component background */
--brutalist-border: #333           /* Borders and grid lines */

/* Text */
--brutalist-text: #e0e0e0          /* Primary text */
--brutalist-text-dim: #888         /* Secondary text */
--brutalist-accent: #fff           /* Emphasis */

/* State Colors */
--brutalist-success: #fff          /* High score (>80) */
--brutalist-warning: #ccc          /* Medium score (50-80) */
--brutalist-error: #999            /* Low score (<50) */
```

### Spacing

```css
/* Badge */
padding: 4px 8px (md), 2px 6px (sm), 6px 10px (lg);
gap: 6px;

/* Radar */
padding: 12px;
gap: 12px;

/* Radar SVG */
radius: dimension * 0.7;  /* Leave room for labels */
label-distance: radius * 1.15;
```

### Borders

```css
border: 1px solid var(--brutalist-border);
border-radius: 0;  /* No rounded corners */
```

---

## Size Variants

### Small (sm)
```
Badge:  font-size: 10px, padding: 2px 6px
Radar:  dimension: 120px, font-size: 9px
```

### Medium (md) — Default
```
Badge:  font-size: 11px, padding: 4px 8px
Radar:  dimension: 180px, font-size: 10px
```

### Large (lg)
```
Badge:  font-size: 12px, padding: 6px 10px
Radar:  dimension: 240px, font-size: 11px
```

---

## Interactive States

### Badge Hover
```css
background: var(--brutalist-bg);  /* Darker */
border-color: var(--brutalist-accent);  /* Brighten border */
transform: translateX(2px);  /* Arrow shifts right */
```

### Badge Focus
```css
outline: 2px solid var(--brutalist-accent);
outline-offset: 0;
```

### Radar Hover
```css
polygon fill-opacity: 0.25;  /* Brighter fill */
circle r: r * 1.2;  /* Larger vertices */
```

---

## Accessibility Features

### ARIA Labels
```tsx
<button
  aria-label="Constitutional health: HIGH (88/100)"
  title="Click to view detailed principle scores"
>
  ...
</button>

<div
  role="img"
  aria-label="Constitutional principle scores radar chart"
>
  ...
</div>
```

### Keyboard Navigation
- Badge is focusable (`<button>`)
- Enter/Space triggers radar expansion
- Focus indicator visible

### Color Independence
- Scores shown as text values (not color-only)
- ARIA labels describe state
- Text contrast meets WCAG AA

---

## Responsive Breakpoints

### Mobile (<640px)
```css
.constitutional-badge {
  font-size: 10px;
  padding: 3px 6px;
}

.constitutional-radar__label {
  font-size: 8px;
}
```

### Tablet/Desktop (≥640px)
```css
/* Use default sizes */
```

---

## Component Composition

### Principle Order (Clockwise from Top)
1. Tasteful (0° / 12 o'clock)
2. Curated (51.4°)
3. Ethical (102.9°)
4. Joy-Inducing (154.3°)
5. Composable (205.7°)
6. Heterarchical (257.1°)
7. Generative (308.6°)

### Grid Levels
- 0.2 (20% radius)
- 0.4 (40% radius)
- 0.6 (60% radius)
- 0.8 (80% radius)
- 1.0 (100% radius)

### SVG Layers (Bottom to Top)
1. Background grid (concentric heptagons)
2. Radial axes (center to vertices)
3. Score polygon (filled)
4. Score vertices (dots)
5. Labels (text outside vertices)

---

## Usage Examples

### Inline Badge (Common)
```tsx
<ConstitutionalBadge
  scores={turn.constitutional_score}
  onClick={() => setExpanded(true)}
  size="sm"
/>
```

### Expanded Radar (On Click)
```tsx
{expanded && (
  <ConstitutionalRadar
    scores={turn.constitutional_score}
    size="md"
    showLabels={true}
  />
)}
```

### Session-Level Aggregate
```tsx
const sessionScores = aggregateScores(session.turns);
<ConstitutionalBadge scores={sessionScores} size="md" />
```

---

## Integration Points

### 1. AssistantMessage Header
```
┌──────────────────────────────────────┐
│ [ConfidenceIndicator] [Constitutional│
│                       Badge]         │
└──────────────────────────────────────┘
```

### 2. ChatPanel Context
```
┌──────────────────────────────────────┐
│ [ContextIndicator] [Constitutional   │
│                     Badge (session)] │
└──────────────────────────────────────┘
```

### 3. Expanded Radar (Below Message)
```
┌──────────────────────────────────────┐
│ Message content...                   │
├──────────────────────────────────────┤
│ [ConstitutionalRadar]                │
└──────────────────────────────────────┘
```

---

## Design Philosophy

**Brutalist Principles**:
1. No decoration for decoration's sake
2. Function dictates form
3. Material honesty (SVG is SVG, text is text)
4. Monospace font (code-native aesthetic)
5. Sharp corners (no rounded softness)

**Information Hierarchy**:
1. Aggregated score (most prominent)
2. Individual principles (detail on demand)
3. Legend values (numerical precision)

**Interaction Model**:
- Badge = Summary (always visible)
- Radar = Detail (click to expand)
- Progressive disclosure (avoid overwhelming)

---

**Status**: Complete visual specification for Constitutional components
