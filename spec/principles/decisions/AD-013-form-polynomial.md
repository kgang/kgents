# AD-013: Form as Polynomial Functor

**Date**: 2025-12-19

> Forms SHOULD be modeled as polynomial functors where valid inputs depend on the current mode. Conditional visibility and nested structures are mode transitions, not scattered conditionals.

---

## Context

Phase 3 of Aspect Form Projection tackled nested objects, arrays, and conditional fields. The traditional approach treats these as separate components with scattered conditional logic. This creates flicker, inconsistent states, and code that's hard to reason about.

## The Categorical Insight

Forms are not widget problems. They are **polynomial functors**—state machines where the valid inputs depend on the current mode. This is AD-002 applied to forms.

## Decision

Complex forms use `FormPolynomial[Schema, Input, Values]`:

```typescript
interface FormPolynomial {
  // Positions = set of valid form configurations (modes)
  modes: Map<string, FormMode>;

  // Current position in the polynomial
  current: string;

  // Transition function: (mode, change) → new_mode
  transitions: Map<string, (change: FieldChange) => string>;

  // Values at current mode
  values: Record<string, unknown>;
}

interface FormMode {
  visible: Set<string>;      // Which fields appear
  required: Set<string>;     // Which fields must be filled
  disabled: Set<string>;     // Which fields are read-only
  hinted: Set<string>;       // Which fields show teaching hints
  depth: number;             // Nesting depth at this mode
}
```

## Key Insight

When `payment_method` changes from `card` to `crypto`, the form doesn't just show/hide fields—it *transitions between modes*. All visibility, required, and disabled states are computed atomically.

## The Three Structural Innovations

| Concept | Traditional | Polynomial |
|---------|-------------|------------|
| **Conditionals** | Scattered `if` checks per field | Mode transitions in state machine |
| **Nested Objects** | Separate ObjectField component | Sheaf gluing of local views |
| **Arrays** | Repeated field instances | Dynamic polynomial extensions |

## Holographic Reduction (Sheaf Collapse)

When nesting depth exceeds observer-aware limits, subtrees collapse to a `SheafReduction`—a compact representation that preserves all information:

```typescript
const DEPTH_LIMITS: Record<string, number> = {
  guest: 3,      // Simpler experience
  creator: 4,    // Creative but not overwhelming
  developer: 6,  // Full depth for debugging
  admin: 6,      // Full depth for administration
};
```

## Zen Breathing Animation

Forms breathe with intention, not spastic animation:
- **Inhale** (focus): 500ms ease-out, subtle glow
- **Exhale** (blur after 3s): 1000ms ease-in-out, return to neutral
- **Mode transition**: 400ms with zen easing curve `[0.4, 0, 0.2, 1]`

## The Unification

Forms now use the same categorical infrastructure as agents:

| Domain | Polynomial | Operad | Sheaf |
|--------|-----------|--------|-------|
| Agent Town | CitizenPolynomial | TOWN_OPERAD | TownSheaf |
| K-gent Soul | SOUL_POLYNOMIAL | SOUL_OPERAD | EigenvectorCoherence |
| **Forms** | **FormPolynomial** | (field projectors) | **FormSheaf** |

## Anti-patterns

- Scattered `if (values.payment_method === 'card')` conditionals (use mode transitions)
- Separate components for each structure type (use PolynomialField)
- Infinite depth without reduction (apply holographic collapse)
- Spastic animations on visibility changes (use zen timing)
- Fire-and-forget async validation (integrate with tracing)

## Implementation

See `plans/aspect-form-phase-3-advanced.md`, `docs/skills/crown-jewel-patterns.md` Pattern 16

*Zen Principle: The form breathes with intention. Each field inhales into existence when needed, exhales away when not. The polynomial holds all possible modes; the observer chooses which to perceive.*
