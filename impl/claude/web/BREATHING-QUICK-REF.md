# 4-7-8 Breathing Quick Reference

**Zero Seed Genesis Motion Law M-01**

---

## The Pattern

```
4 seconds inhale  (0-21%)   ─→  Gentle rise
7 seconds hold    (21-58%)  ─→  Moment of fullness
8 seconds exhale  (58-100%) ─→  Long, calming release
────────────────────────────────────────────────────
19 seconds total
```

---

## Usage

### CSS (Simplest)

```tsx
import '@/styles/breathing.css';

<div className="breathe">Content</div>
<div className="breathe-subtle">Subtle</div>
<div className="breathe-intense">Intense</div>
<div className="breathe-with-glow">Glowing</div>
```

### React Hook

```tsx
import { useBreathing } from '@/hooks';

const { style } = useBreathing({ enabled: isActive });
<div style={style}>Content</div>
```

### Framer Motion

```tsx
import { Breathe } from '@/components/joy';

<Breathe intensity={0.5} speed="normal">
  <Content />
</Breathe>
```

---

## Variants

| Class/Speed | Duration | Use Case |
|-------------|----------|----------|
| `breathe-slow` / `slow` | 25.3s | Ambient, gentle |
| `breathe` / `normal` | 19s | Active elements |
| `breathe-fast` / `fast` | 14.25s | Attention needed |

| Amplitude | Scale Range | Opacity Range |
|-----------|-------------|---------------|
| `breathe-subtle` | 1.0 ↔ 1.0075 | 0.975 ↔ 1.0 |
| `breathe` | 1.0 ↔ 1.015 | 0.95 ↔ 1.0 |
| `breathe-intense` | 1.0 ↔ 1.0225 | 0.92 ↔ 1.0 |

---

## When to Use

**✓ YES** (Earned Motion):
- K-Blocks being edited
- Living axioms
- High coherence (>0.8)
- Fresh witness marks
- Active portals
- Health indicators

**✗ NO** (Decorative):
- Static text
- Inactive navigation
- Default buttons
- Decorative elements

---

## Accessibility

Automatically respects `prefers-reduced-motion`:

```css
@media (prefers-reduced-motion: reduce) {
  .breathe { animation: none; }
}
```

---

## Files

- **CSS**: `/web/src/styles/breathing.css`
- **Hook**: `/web/src/hooks/useBreathing.ts`
- **Component**: `/web/src/components/joy/Breathe.tsx`
- **Docs**: `/web/src/styles/README-BREATHING.md`

---

**"Stillness, then life. Motion is earned."**
