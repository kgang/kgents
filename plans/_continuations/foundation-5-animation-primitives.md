---
path: plans/_continuations/foundation-5-animation-primitives
status: complete
progress: 100
last_touched: 2025-12-16
touched_by: claude-opus-4
blocking: []
enables:
  - Wave 0 completion
  - Wave 1 Hero Path Polish
  - Joy-inducing principle fulfillment
session_notes: |
  **COMPLETED 2025-12-16**

  Foundation 5 implemented with:
  - Animation primitives: Breathe, Pop, PopOnMount, Shake, Shimmer
  - Personality components: PersonalityLoading, EmpathyError, InlineError
  - celebrate() confetti function with subtle/normal/epic modes
  - useMotionPreferences hook for reduced motion support
  - 45 passing tests

  Integrated with Brain page:
  - PersonalityLoading for topology loading
  - Breathe for healthy status indicator
  - PopOnMount for toast animations
  - celebrate() on successful crystal capture

  Integrated with Gestalt page:
  - PersonalityLoading for topology loading
  - Breathe for A/A+ health grades
  - celebrateEpic() on A+ health grade

  Wave 0 is now COMPLETE. Ready for Wave 1: Hero Path Polish.
---

# Foundation 5: Animation Primitives & Joy Layer - Continuation Prompt

> *"UIs are functional but lifeless. Principle 4 unfulfilled."*

## Context

You are the **Crown Jewel Executor** completing Wave 0 of the Enlightened Crown strategy.

### Completed Foundations
- ✅ **Foundation 1**: AGENTESE Path Visibility (27 tests)
- ✅ **Foundation 2**: Observer Switcher (ObserverSwitcher component, hooks)
- ✅ **Foundation 3**: Polynomial Diagram (34 tests, PolynomialDiagram component)
- ✅ **Foundation 4**: Synergy Event Bus (34 tests, SynergyEventBus, GestaltToBrainHandler)

### Current Foundation
**Foundation 5: Personality & Joy (Animation Primitives)**

## The Problem

From `plans/crown-jewels-enlightened.md`:

> **The Problem**: UIs are functional but lifeless. Principle 4 unfulfilled.
>
> **The Solution**: Micro-interactions, empathetic errors, celebration moments.
>
> ```tsx
> // Healthy grades breathe
> <Breathe intensity={0.5}>
>   <HealthGrade grade="A+" />
> </Breathe>
>
> // Errors are empathetic
> <EmpathyError
>   type="network"
>   title="Lost in the void..."
>   subtitle="The connection wandered off. Let's bring it back."
>   action="Reconnect"
> />
>
> // Success is celebrated
> celebrate(); // confetti on milestone completion
> ```

Currently, the web UI is functional but lacks personality. Health grades just sit there. Errors are generic. Success is silent. This violates **Principle 4: Joy-Inducing**.

## Requirements

### Animation Primitives

1. **`<Breathe>`** - Subtle pulsing animation for healthy/living elements
   ```tsx
   interface BreatheProps {
     children: React.ReactNode;
     intensity?: number;  // 0.0-1.0, default 0.3
     speed?: 'slow' | 'normal' | 'fast';
     disabled?: boolean;  // Respects prefers-reduced-motion
   }
   ```

2. **`<Pop>`** - Selection/activation feedback
   ```tsx
   interface PopProps {
     children: React.ReactNode;
     trigger?: boolean;  // Animate when true
     scale?: number;     // Peak scale, default 1.1
   }
   ```

3. **`<Shake>`** - Error/warning feedback
   ```tsx
   interface ShakeProps {
     children: React.ReactNode;
     trigger?: boolean;
     intensity?: 'gentle' | 'normal' | 'urgent';
   }
   ```

4. **`<Shimmer>`** - Loading/processing indicator
   ```tsx
   interface ShimmerProps {
     children: React.ReactNode;
     active?: boolean;
   }
   ```

### Personality Loading States

**`<PersonalityLoading>`** - Jewel-specific loading messages

```tsx
interface PersonalityLoadingProps {
  jewel: 'brain' | 'gestalt' | 'gardener' | 'atelier' | 'coalition' | 'park' | 'domain';
  action?: string;  // Optional specific action
}

// Example messages:
// Brain: "Crystallizing memories...", "Traversing the hologram..."
// Gestalt: "Analyzing architecture...", "Computing health metrics..."
// Gardener: "Preparing the garden...", "Gathering context..."
```

### Empathetic Errors

**`<EmpathyError>`** - Humane error states with personality

```tsx
interface EmpathyErrorProps {
  type: 'network' | 'notfound' | 'permission' | 'timeout' | 'unknown';
  title?: string;       // Override default title
  subtitle?: string;    // Override default subtitle
  action?: string;      // Action button text
  onAction?: () => void;
}

// Default messages:
// network: "Lost in the void..." / "The connection wandered off."
// notfound: "Nothing here..." / "This place doesn't exist yet."
// permission: "Door's locked..." / "You'll need the right key."
// timeout: "Taking too long..." / "The universe is slow today."
```

### Celebration

**`celebrate()`** - Confetti burst for milestones

```tsx
function celebrate(options?: {
  intensity?: 'subtle' | 'normal' | 'epic';
  duration?: number;
}): void;

// Triggers:
// - First crystal captured
// - Gestalt analysis shows A+ health
// - Gardener session completed
// - Synergy successfully processed
```

## Implementation Guide

### File Structure

```
impl/claude/web/src/components/joy/
├── index.ts
├── Breathe.tsx
├── Pop.tsx
├── Shake.tsx
├── Shimmer.tsx
├── PersonalityLoading.tsx
├── EmpathyError.tsx
├── celebrate.ts
└── useMotionPreferences.ts
```

### Key Patterns

1. **Respect Motion Preferences**
   ```tsx
   const useMotionPreferences = () => {
     const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

     useEffect(() => {
       const mediaQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
       setPrefersReducedMotion(mediaQuery.matches);

       const handler = (e: MediaQueryListEvent) => setPrefersReducedMotion(e.matches);
       mediaQuery.addEventListener('change', handler);
       return () => mediaQuery.removeEventListener('change', handler);
     }, []);

     return { prefersReducedMotion };
   };
   ```

2. **CSS-First Animations** (prefer CSS over JS for performance)
   ```css
   @keyframes breathe {
     0%, 100% { transform: scale(1); opacity: 1; }
     50% { transform: scale(1.02); opacity: 0.9; }
   }

   .breathe {
     animation: breathe 3s ease-in-out infinite;
   }

   @media (prefers-reduced-motion: reduce) {
     .breathe { animation: none; }
   }
   ```

3. **Jewel-Specific Personalities**
   ```tsx
   const LOADING_MESSAGES: Record<Jewel, string[]> = {
     brain: [
       "Crystallizing memories...",
       "Traversing the hologram...",
       "Surfacing forgotten thoughts...",
     ],
     gestalt: [
       "Analyzing architecture...",
       "Computing health metrics...",
       "Detecting drift patterns...",
     ],
     gardener: [
       "Preparing the garden...",
       "Gathering context...",
       "Sensing the forest...",
     ],
     // ...
   };
   ```

### Integration Points

1. **Brain Page** (`src/pages/Brain.tsx`)
   - Wrap health grades with `<Breathe>`
   - Use `<PersonalityLoading jewel="brain">` for loading states
   - `celebrate()` on first crystal capture

2. **Gestalt Page** (`src/pages/Gestalt.tsx`)
   - Wrap healthy modules with `<Breathe>`
   - `<Shake>` for modules with violations
   - `<PersonalityLoading jewel="gestalt">` for analysis
   - `celebrate()` on A+ health grade

3. **Error Boundaries**
   - Replace generic error states with `<EmpathyError>`
   - Use appropriate `type` based on error cause

4. **Synergy Notifications**
   - `<Pop>` animation when synergy toast appears
   - Subtle `celebrate()` when synergy completes successfully

## Success Criteria

- [x] `<Breathe>` component with motion preference support ✓
- [x] `<Pop>` component for selection feedback ✓
- [x] `<Shake>` component for error feedback ✓
- [x] `<Shimmer>` component for loading states ✓
- [x] `<PersonalityLoading>` with jewel-specific messages ✓
- [x] `<EmpathyError>` with type-specific messaging ✓
- [x] `celebrate()` function with confetti effect ✓
- [x] Motion preferences respected throughout ✓
- [x] At least one integration per Hero Path jewel (Brain, Gestalt) ✓
- [x] Tests for animation components (45 passing tests) ✓

## Session Protocol

1. Read `plans/crown-jewels-enlightened.md` for full context
2. Check existing web components structure
3. Create joy components library
4. Integrate with Brain page first (quickest visual impact)
5. Add to Gestalt page
6. Write tests
7. Update success criteria in master plan

## Reference Files

| File | Purpose |
|------|---------|
| `plans/crown-jewels-enlightened.md` | Master plan (Foundation 5 section) |
| `impl/claude/web/src/pages/Brain.tsx` | Brain page for integration |
| `impl/claude/web/src/pages/Gestalt.tsx` | Gestalt page for integration |
| `impl/claude/web/src/components/` | Existing component patterns |
| `spec/principles.md` | Principle 4: Joy-Inducing |

## After Foundation 5

Once this foundation is complete, **Wave 0 is done**.

Next: **Wave 1: Hero Path Polish**
- Brain + Gestalt + Gardener to 100%
- Hero path completion in < 5 minutes
- "Wow moment" for each jewel

---

*"Joy is not decoration. It is the difference between software and an experience."*
