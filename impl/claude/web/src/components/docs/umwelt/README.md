# Umwelt Visualization

> _"The noun is a lie. There is only the rate of change."_

**Umwelt** (German: "surrounding world") is a concept from biosemiotics. Different observers perceive the same world in fundamentally different ways. A tick perceives butyric acid and warmth. A human perceives colors, sounds, and concepts. Same world. Different realities.

This module visualizes that perceptual shift when you change observers in the AGENTESE Docs Explorer.

---

## Quick Start

The umwelt system is already wired into `AgenteseDocs.tsx`. Just visit the AGENTESE Docs page and switch observers to see it in action.

### What You'll See

1. **Observer Picker**: Click a different observer (Guest → Developer, etc.)
2. **Ripple**: A subtle radial gradient emanates from the picker (comfortable/spacious modes)
3. **Aspect Animation**: Newly-available aspects fade in; newly-hidden aspects fade to ghost
4. **Toast**: Brief notification showing what changed (e.g., "→ developer: 3 aspects revealed")

### Design Principles

- **Subtle by default**: Animations are almost imperceptible. The goal is acknowledgment, not celebration.
- **Respects user preferences**: Uses `prefers-reduced-motion` system setting.
- **Density-aware**: Compact mode skips the ripple; spacious mode shows detailed toasts.

---

## Files

| File                | Purpose                                    |
| ------------------- | ------------------------------------------ |
| `umwelt.types.ts`   | Type definitions + motion constants        |
| `useUmweltDiff.ts`  | Core diff algorithm                        |
| `UmweltContext.tsx` | React context for coordinating transitions |
| `UmweltRipple.tsx`  | Ripple animation component                 |
| `index.ts`          | Clean exports                              |

---

## Usage

The `UmweltProvider` is already wrapped around `AgenteseDocs`. If you need to use umwelt elsewhere:

```tsx
import { UmweltProvider, useUmwelt } from '@/components/docs/umwelt';

function MyComponent() {
  return (
    <UmweltProvider>
      <MyInnerComponent />
    </UmweltProvider>
  );
}

function MyInnerComponent() {
  const { triggerTransition, isTransitioning, observerColor } = useUmwelt();

  // Trigger on observer change
  const handleObserverChange = (from, to, metadata, density) => {
    triggerTransition(from, to, metadata, density);
  };

  return <div style={{ borderColor: observerColor }}>...</div>;
}
```

---

## Tuning Animations

All animation values are centralized in `umwelt.types.ts`:

```ts
export const UMWELT_MOTION = {
  standard: 200, // Main animation duration (ms)
  revealScale: { from: 0.95, to: 1 }, // How much elements grow
  rippleOpacity: 0.15, // How visible the ripple is
  // ...
};
```

To make animations **more subtle**, reduce these values.
To make animations **more noticeable**, increase them (but please don't—tasteful > flashy).

---

## Testing Checklist

### Manual QA (5 minutes)

1. **Navigate to AGENTESE Docs** (`/agentese` or equivalent)
2. **Switch observers**: Guest → User → Developer → Mayor → Void Walker
3. **Verify ripple**: Subtle radial gradient from picker (skip in compact mode)
4. **Verify aspect animation**: Watch aspects fade in/out in AspectPanel
5. **Verify toast**: Brief notification shows the change
6. **Test rapid switching**: Click observers quickly—should skip animations gracefully
7. **Test reduced motion**: Set `prefers-reduced-motion: reduce` in DevTools → should skip all animations

### Edge Cases

- [ ] Empty metadata (no aspects) → no crash
- [ ] Same observer clicked twice → no animation
- [ ] Rapid switching → graceful handling
- [ ] Reduced motion preference → animations disabled

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  AgenteseDocs.tsx                                           │
│    └── UmweltProvider                                       │
│          ├── ObserverPicker (triggers transition)           │
│          │     └── UmweltRipple (shows on transition)       │
│          └── AspectPanel (animates aspects)                 │
│                └── motion.div (with stagger)                │
└─────────────────────────────────────────────────────────────┘
```

Data flow:

1. User clicks new observer in `ObserverPicker`
2. `handleObserverChange` calls `triggerTransition(from, to, metadata, density)`
3. `UmweltContext` computes diff, sets `isTransitioning`, `showRipple`, etc.
4. `ObserverPicker` renders `UmweltRipple` based on `showRipple`
5. `AspectPanel` checks `getAspectAnimationState()` for each aspect
6. After `UMWELT_MOTION.deliberate` ms, transition clears

---

## QA Prompt

Copy this prompt to test the feature:

```
QA: Umwelt Visualization

1. Start the dev server: `npm run dev`
2. Navigate to AGENTESE Docs (usually /agentese or the docs page)
3. Locate the Observer Picker (top bar with Guest/User/Developer/etc.)
4. Click through each observer type and verify:
   - [ ] Subtle ripple effect on comfortable/spacious modes
   - [ ] Aspects animate in/out (very subtle scale + opacity)
   - [ ] Toast appears briefly with observer name
   - [ ] No animation on same-observer click
   - [ ] Rapid clicking skips animations gracefully
5. Test accessibility:
   - In DevTools → Rendering → Emulate prefers-reduced-motion: reduce
   - [ ] All animations should be disabled
6. Test density modes:
   - Compact: No ripple, instant transitions
   - Comfortable: Ripple + stagger
   - Spacious: Ripple + slower stagger + detailed toast
```

---

_Last updated: 2025-12-19_
