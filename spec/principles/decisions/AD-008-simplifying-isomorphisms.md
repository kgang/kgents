# AD-008: Simplifying Isomorphisms

**Date**: 2025-12-16

> When the same conditional pattern appears 3+ times, extract the SIMPLIFYING ISOMORPHISM—a categorical equivalence that should be applied uniformly.

---

## Context

UI code often contains repetitive conditional logic based on screen size, user role, feature flags, or other dimensions. These scattered conditionals obscure the underlying structure and make the code fragile.

## Discovery

The Gestalt Elastic refactor revealed that `isMobile`, `isTablet`, and `isDesktop` checks throughout the codebase were all manifestations of a single dimension: **density**. This is not unique to screen size—the same pattern appears wherever conditionals cluster.

```
Screen Density ≅ Observer Umwelt ≅ Projection Target ≅ Content Detail Level
```

## Decision

When conditional logic repeats 3+ times on the same dimension, extract it:

1. **IDENTIFY**: Notice repeated `if/switch` on the same condition
2. **NAME**: Give the dimension an explicit name (`density`, `role`, `tier`)
3. **DEFINE**: List exhaustive, mutually exclusive values
4. **CONTEXT**: Create a hook/context to provide the dimension
5. **PARAMETERIZE**: Replace scattered values with lookup tables
6. **ADAPT**: Components receive dimension, decide behavior internally
7. **REMOVE**: Eliminate all remaining ad-hoc conditionals

## The Extraction Pattern

```typescript
// Before: Scattered conditionals
const nodeSize = isMobile ? 0.2 : isTablet ? 0.25 : 0.3;
const fontSize = isMobile ? 14 : 18;
const maxItems = isMobile ? 15 : 50;

// After: Parameterized by named dimension
const NODE_SIZE = { compact: 0.2, comfortable: 0.25, spacious: 0.3 } as const;
const FONT_SIZE = { compact: 14, comfortable: 16, spacious: 18 } as const;
const MAX_ITEMS = { compact: 15, comfortable: 30, spacious: 50 } as const;

const { density } = useWindowLayout();
const nodeSize = NODE_SIZE[density];
const fontSize = FONT_SIZE[density];
const maxItems = MAX_ITEMS[density];
```

## Known Isomorphisms in kgents

| Scattered As... | Named Dimension | Values |
|-----------------|-----------------|--------|
| `isMobile`, `isTablet`, `isDesktop` | `density` | `compact`, `comfortable`, `spacious` |
| `isViewer`, `isEditor`, `isAdmin` | `role` | `viewer`, `editor`, `admin` |
| `isFree`, `isPro`, `isEnterprise` | `tier` | `free`, `pro`, `enterprise` |
| Observer-specific rendering | `umwelt` | (AGENTESE) |

## Connection to AGENTESE

This is the Projection Protocol extended to UI. AGENTESE says "observation is interaction"—the observer's umwelt determines what they perceive. The Simplifying Isomorphism principle says the same: the UI's density determines what content it renders.

## Validation Test

"Can I describe the behavior without mentioning the original condition?"

- **Fails**: "On mobile, we show fewer labels."
- **Passes**: "In compact density, we show fewer labels."

## Anti-patterns

- Scattering `isMobile` checks throughout components
- Different names for the same dimension in different files
- Conditionals without named dimension abstraction

## Implementation

See `docs/skills/ui-isomorphism-detection.md` and `docs/skills/elastic-ui-patterns.md`

*Zen Principle: The same structure appears everywhere because it IS everywhere. Find it once, use it forever.*
