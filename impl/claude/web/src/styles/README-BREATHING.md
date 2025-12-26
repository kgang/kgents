# 4-7-8 Breathing Animation System

**Version**: 1.0
**Date**: 2025-12-25
**Status**: IMPLEMENTED

---

## Overview

This system implements **Motion Law M-01** from Zero Seed Creative Strategy: **Asymmetric breathing uses 4-7-8 timing** (not symmetric). It provides calming, organic animations for elements that have "earned" motion through user interaction.

---

## The Five Motion Laws

All breathing animations must comply with these laws:

| Law | Name | Statement |
|-----|------|-----------|
| **M-01** | Asymmetric Breathing | 4-7-8 timing, not symmetric |
| **M-02** | Stillness Then Life | Default is still, animation is earned |
| **M-03** | Mechanical Precision Organic Life | Mechanical for structure, organic for life |
| **M-04** | Reduced Motion Respected | Respect prefers-reduced-motion |
| **M-05** | Animation Justification | Every animation has semantic reason |

---

## 4-7-8 Timing Pattern

The canonical breathing cycle is **19 seconds total**:

```
4 seconds inhale (21% of cycle)
7 seconds hold   (37% of cycle)
8 seconds exhale (42% of cycle)
─────────────────────────────────
19 seconds total
```

### Phase Breakdown

| Phase | Duration | Percentage | What Happens |
|-------|----------|------------|--------------|
| **Inhale** | 4s | 0-21% | Gentle rise, scale increases, opacity brightens |
| **Hold** | 7s | 21-58% | Stay at peak, moment of fullness |
| **Exhale** | 8s | 58-100% | Long, calming release, scale/opacity decrease |

---

## Usage

### 1. CSS Classes (Preferred for Static Elements)

```tsx
import '@/styles/breathing.css';

// Standard breathing
<div className="breathe">
  <Badge>Active</Badge>
</div>

// Subtle breathing (50% amplitude)
<div className="breathe-subtle">
  <StatusIndicator />
</div>

// Intense breathing (150% amplitude)
<div className="breathe-intense">
  <AlertBadge />
</div>

// With glow pulse
<div className="breathe-with-glow">
  <HealthIndicator />
</div>

// Speed variants
<div className="breathe breathe-slow">...</div>
<div className="breathe breathe-fast">...</div>

// Staggered phases (for lists)
<div className="breathe breathe-stagger-1">Item 1</div>
<div className="breathe breathe-stagger-2">Item 2</div>
<div className="breathe breathe-stagger-3">Item 3</div>
```

### 2. React Hook (For Dynamic Control)

```tsx
import { useBreathing } from '@/hooks';

function MyComponent() {
  const { style, pause, resume, isBreathing } = useBreathing({
    enabled: true,
    amplitude: 0.015, // 1.5% scale variation
    period: 19000, // 19 seconds (4-7-8 timing)
    phaseOffset: 0, // For staggering
  });

  return (
    <div style={style}>
      <Badge>Breathing Element</Badge>
    </div>
  );
}
```

### 3. Framer Motion Component (For Complex Animations)

```tsx
import { Breathe } from '@/components/joy';

function HealthGrade({ grade }: { grade: string }) {
  return (
    <Breathe intensity={0.5} speed="normal">
      <div className="grade-badge">{grade}</div>
    </Breathe>
  );
}
```

---

## When to Use Breathing (M-05: Animation Justification)

### ✅ Approved Uses (Earned Motion)

- **Active K-Blocks** - Currently being edited
- **Living Axioms** - Grounded and active in the system
- **High Coherence** - Health indicator showing system integrity
- **Recent Witness Marks** - Fresh activity requiring attention
- **Portal Connections** - Active data flow or relationship
- **Status Indicators** - Showing "healthy" or "alive" state

### ❌ Prohibited Uses (Decorative, Not Earned)

- Static text
- Navigation items (unless active)
- Default button states
- Inactive content
- Decorative elements
- Always-on animations without semantic meaning

---

## Speed Variants

The system provides three speed presets:

| Speed | Duration | Use Case |
|-------|----------|----------|
| **slow** | 25.3s | Ambient, gentle background elements |
| **normal** | 19s | Active elements (standard 4-7-8) |
| **fast** | 14.25s | Attention-needed, urgent indicators |

---

## Amplitude Variants

| Variant | Scale Range | Opacity Range | Use Case |
|---------|-------------|---------------|----------|
| **Subtle** | 1.0 ↔ 1.0075 | 0.975 ↔ 1.0 | Background elements |
| **Standard** | 1.0 ↔ 1.015 | 0.95 ↔ 1.0 | Active content |
| **Intense** | 1.0 ↔ 1.0225 | 0.92 ↔ 1.0 | High-attention alerts |

---

## Performance Optimization

### Compositor-Friendly Properties

The breathing animation only animates:
- `transform: scale()` (compositor layer)
- `opacity` (compositor layer)

**DO NOT** animate layout properties:
- ❌ `width`, `height`
- ❌ `margin`, `padding`
- ❌ `top`, `left`, `right`, `bottom` (unless using `transform: translate`)

### GPU Acceleration

The `.breathe` class includes:
```css
will-change: transform, opacity;
transform: translateZ(0); /* Force GPU layer */
backface-visibility: hidden; /* Prevent antialiasing issues */
```

---

## Accessibility (M-04: Reduced Motion)

The system **automatically disables** all breathing animations when the user has set `prefers-reduced-motion: reduce`:

```css
@media (prefers-reduced-motion: reduce) {
  .breathe,
  .breathe-subtle,
  .breathe-intense {
    animation: none;
    transform: scale(1);
    opacity: 1;
  }
}
```

The React hook also respects this preference by default:
```tsx
const { style } = useBreathing({
  respectReducedMotion: true, // default
});
```

---

## Staggered Breathing (For Lists)

When multiple elements breathe together, stagger their phases for organic feel:

```tsx
import { getStaggeredPhaseOffset } from '@/hooks/useBreathing';

// Automatic staggering
citizens.map((citizen, i) => {
  const { style } = useBreathing({
    phaseOffset: getStaggeredPhaseOffset(i, citizens.length),
  });

  return <CitizenNode key={citizen.id} style={style} />;
});
```

Or use CSS classes:
```tsx
items.map((item, i) => (
  <div
    key={item.id}
    className={`breathe breathe-stagger-${(i % 8) + 1}`}
  >
    {item.content}
  </div>
));
```

---

## Testing

### Visual Regression

```bash
npm run test:visual -- breathing
```

### Motion Law Compliance

```bash
npm run test:design-laws -- --category=motion
```

### Accessibility Audit

```bash
npm run test:a11y -- --motion
```

---

## Files in This System

| File | Purpose |
|------|---------|
| `styles/breathing.css` | CSS keyframes and utility classes |
| `hooks/useBreathing.ts` | React hook for dynamic breathing |
| `components/joy/Breathe.tsx` | Framer Motion component |
| `components/joy/BreathingContainer.tsx` | Container wrapper |
| `constants/town.ts` | Legacy breathing constants (being phased out) |

---

## Migration Notes

### Old System (Pre-Zero Seed Genesis)

```tsx
// OLD: Symmetric breathing, 8.1s period
const BREATHING_ANIMATION = {
  period: 8100,
  amplitude: 0.015,
};
```

### New System (Zero Seed Genesis)

```tsx
// NEW: 4-7-8 asymmetric breathing, 19s period
const BREATHING_4_7_8 = {
  period: 19000,
  inhaleDuration: 4000,
  holdDuration: 7000,
  exhaleDuration: 8000,
  amplitude: 0.015,
};
```

---

## Examples

### Example 1: K-Block Active State

```tsx
<div
  className={clsx(
    'k-block',
    isEditing && 'breathe' // M-02: Earned through user interaction
  )}
>
  <KBlockContent />
</div>
```

### Example 2: Coherence Health Indicator

```tsx
function CoherenceGauge({ score }: { score: number }) {
  const isHealthy = score > 0.8;

  return (
    <div className={isHealthy ? 'breathe-with-glow' : ''}>
      <GaugeVisual score={score} />
    </div>
  );
}
```

### Example 3: Staggered List

```tsx
function AxiomList({ axioms }: { axioms: Axiom[] }) {
  return (
    <div>
      {axioms.map((axiom, i) => (
        <div
          key={axiom.id}
          className={`breathe-subtle breathe-stagger-${(i % 8) + 1}`}
        >
          <AxiomCard axiom={axiom} />
        </div>
      ))}
    </div>
  );
}
```

---

## Design Principles

### STARK BIOME Aesthetic

> "90% steel, 10% earned glow"

Most of the UI is **still**. Motion is a privilege, earned through:
- User interaction
- System health
- Active state
- Semantic significance

Breathing animations represent **life** in an otherwise **industrial** environment:
- Steel (background): Precision, discipline, stillness
- Life (foreground): Growth, emergence, breathing

---

## References

- `plans/zero-seed-creative-strategy.md` - Motion Laws (M-01 through M-05)
- `docs/creative/stark-biome-moodboard.md` - Visual aesthetic
- `docs/skills/elastic-ui-patterns.md` - Responsive patterns

---

*"Stillness, then life. The default is calm. Motion is earned."*

*Compiled: 2025-12-25 | Zero Seed Genesis v1.0*
