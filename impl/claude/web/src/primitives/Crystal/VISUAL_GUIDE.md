# Crystal Components - Visual Guide

## Component Hierarchy

```
CrystalHierarchy
├── Level: SESSION ▼
│   ├── CrystalCard (expandable)
│   │   ├── Header
│   │   │   ├── Level Badge [SESSION]
│   │   │   ├── Timestamp [2h ago]
│   │   │   └── Confidence Ring ◯85%
│   │   ├── Content
│   │   │   ├── Insight (primary text)
│   │   │   └── Significance (secondary, indented)
│   │   ├── Footer
│   │   │   ├── MoodIndicator (7 dots)
│   │   │   └── Source Count [12 sources]
│   │   └── Details (when expanded)
│   │       ├── Principles [tasteful] [curated]
│   │       ├── Topics [refactor] [cleanup]
│   │       └── Metrics [Confidence: 85%] [Compression: 12:1]
│   ├── CrystalCard (collapsed)
│   └── CrystalCard (collapsed)
├── Level: DAY ▼
│   └── (similar structure)
├── Level: WEEK ▶ (collapsed)
└── Level: EPOCH ▶ (empty)
```

---

## MoodIndicator Variants

### Dots (Default)
```
┌─────────────────────────┐
│ ● ● ◉ ● ● ◉ ●           │  ← 7 dots (warmth, weight, tempo...)
└─────────────────────────┘
```

**Intensity Mapping**:
- ● (dim): 0.0-0.33 → steel-700, 30% opacity
- ● (medium): 0.34-0.66 → steel-400, 80% opacity
- ◉ (bright): 0.67-1.0 → glow-spore, glow effect

### Bars
```
┌─────────────────────────┐
│ ████████░░░░░░░░ (warmth)     │
│ ███████████░░░░ (weight)      │
│ ██████████████ (tempo)        │
│ █████░░░░░░░░░░ (texture)     │
│ ████████████░░ (brightness)   │
│ ███████████████ (saturation)  │
│ ██████░░░░░░░░░ (complexity)  │
└─────────────────────────┘
```

---

## CrystalCard States

### Collapsed (Default)
```
┌────────────────────────────────────────┐
│ SESSION    2h ago              ◯85%   │
├────────────────────────────────────────┤
│ Completed extinction audit, removed    │
│ 52K lines of stale code                │
│                                        │
│ │ Codebase is leaner, focus sharper   │
├────────────────────────────────────────┤
│ ● ● ◉ ● ● ◉ ●          12 sources     │
└────────────────────────────────────────┘
```

### Expanded
```
┌────────────────────────────────────────┐
│ SESSION    2h ago              ◯85%   │
├────────────────────────────────────────┤
│ Completed extinction audit, removed    │
│ 52K lines of stale code                │
│                                        │
│ │ Codebase is leaner, focus sharper   │
├────────────────────────────────────────┤
│ ● ● ◉ ● ● ◉ ●          12 sources     │
├────────────────────────────────────────┤ (glow border)
│ PRINCIPLES:                            │
│ [tasteful] [curated]                   │
│                                        │
│ TOPICS:                                │
│ [refactor] [cleanup] [simplify]        │
│                                        │
│ Confidence: 85%   Compression: 12:1   │
└────────────────────────────────────────┘
```

---

## CrystalHierarchy Layouts

### Timeline (Default)
```
┌────────────────────────────────────────┐
│ SESSION (3)                         ▼  │
├────────────────────────────────────────┤
│ │  ┌─ CrystalCard ──────────────┐     │
│ │  │ SESSION  2h ago      ◯85% │     │
│ │  │ Insight text...           │     │
│ │  └───────────────────────────┘     │
│ │                                     │
│ │  ┌─ CrystalCard ──────────────┐     │
│ │  │ SESSION  4h ago      ◯78% │     │
│ │  └───────────────────────────┘     │
├────────────────────────────────────────┤
│ DAY (1)                             ▼  │
├────────────────────────────────────────┤
│ │  ┌─ CrystalCard ──────────────┐     │
│ │  │ DAY  Dec 24          ◯82% │     │
│ │  └───────────────────────────┘     │
├────────────────────────────────────────┤
│ WEEK (0)                               │
├────────────────────────────────────────┤
│ EPOCH (0)                              │
└────────────────────────────────────────┘
```

### Tree
```
┌────────────────────────────────────────┐
│ SESSION (3)                         ▼  │
│ ├─ CrystalCard (expanded)             │
│ ├─ CrystalCard                        │
│ └─ CrystalCard                        │
├────────────────────────────────────────┤
│ DAY (1)                             ▼  │
│ └─ CrystalCard                        │
├────────────────────────────────────────┤
│ WEEK (0)                               │
└────────────────────────────────────────┘
```

---

## Color Palette

### Level Colors
- **SESSION**: `#a0a0a0` (steel-300) — muted gray
- **DAY**: `#4a6b4a` (life-sage) — healthy green
- **WEEK**: `#8ba98b` (glow-lichen) — sage green
- **EPOCH**: `#d4b88c` (glow-amber) — warm gold

### Confidence Ring
- **Track**: `#444` (steel-600) — base circle
- **Fill**: `#c4a77d` (glow-spore) — golden arc (proportional to confidence)

### Mood Dots
- **Low (0-33%)**: Steel-700, 30% opacity
- **Medium (34-66%)**: Steel-400, 80% opacity
- **High (67-100%)**: Glow-spore with glow effect

### Principle Tags
- **Background**: `#1a2e1a` (life-moss)
- **Border**: `#4a6b4a` (life-sage)
- **Text**: `#6b8b6b` (life-mint)

### Topic Tags
- **Background**: `#1c1c22` (surface-2)
- **Border**: `#28282f` (surface-3)
- **Text**: `#8a8a94` (text-secondary)

---

## Interactive States

### Hover (Expandable Cards)
```
Border: steel-gunmetal → steel-zinc
Background: surface-1 → surface-2
Transition: 120ms ease-out-expo
```

### Expanded
```
Border: surface-3 → glow-spore
Box-shadow: 0 0 8px rgba(196, 167, 125, 0.2)
Details panel: fade in + slide down
```

### Level Header (Clickable)
```
Hover: background surface-2 → surface-3
Toggle: ▶ ↔ ▼ (instant)
```

---

## Responsive Behavior

All components are **fluid** by default:
- Cards: `width: 100%` (fill parent)
- Hierarchy: Vertical stack (mobile-friendly)
- MoodIndicator: Scales with size prop

**Breakpoints** (if needed):
- Mobile (<640px): Full width, smaller padding
- Tablet (640-1024px): Comfortable spacing
- Desktop (>1024px): Max width constraints (optional)

---

## Empty States

### CrystalHierarchy (No Crystals)
```
┌────────────────────────────────────────┐
│                                        │
│          No crystals yet.              │
│                                        │
│    Use :crystallize to create your    │
│           first crystal.               │
│                                        │
└────────────────────────────────────────┘
```

### Level (No Crystals at Level)
```
┌────────────────────────────────────────┐
│ WEEK (0)                               │  ← Grayed out, not clickable
└────────────────────────────────────────┘
```

---

## Accessibility

### Keyboard Navigation
- **Tab**: Navigate through expandable cards
- **Enter/Space**: Toggle expansion
- **Escape**: Collapse all (future)

### ARIA Labels
- Level headers: `role="button"`, `aria-expanded`
- Cards: `aria-label="Crystal: {insight}"`
- Confidence rings: `aria-label="Confidence: 85%"`

### Color Contrast
- Text: WCAG AA compliant (4.5:1 minimum)
- Borders: Subtle but visible (3:1 minimum)

---

## Performance Notes

### Optimization
- All components use `React.memo` for shallow comparison
- MoodIndicator re-renders only if `mood` or `size` changes
- CrystalHierarchy groups/sorts once, memoizes result

### Large Lists
- CrystalHierarchy handles 100+ crystals efficiently
- Collapse levels to reduce DOM nodes
- Future: Virtual scrolling for 1000+ crystals

---

**Visual Guide Version**: 1.0
**Last Updated**: 2025-12-25
