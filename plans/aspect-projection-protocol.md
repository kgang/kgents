# Aspect Projection Protocol

> **Status**: ✅ Implemented (2025-12-19)
> **Codified**: AD-012 in `spec/principles.md`
> **Implementation**: `NavigationTree.tsx`, `spec/protocols/agentese.md` §2.5

## The Problem

We added aspects to the navigation tree as clickable items (e.g., `self.differance:witness`). This caused:
1. **405 errors** - aspects are POST-only (correct), but navigation triggers GET
2. **Semantic confusion** - treating aspects as "places to go" rather than "actions to take"

## First Principles Analysis

### The AGENTESE Ontology Has Distinct Semantic Levels

```
Level 1: Contexts (world, self, concept, void, time)     NAVIGABLE
Level 2: Holons (town, memory, gardener, etc.)           NAVIGABLE
Level 3: Entities (citizen.kent_001, crystal.abc123)     NAVIGABLE
Level 4: Aspects (manifest, polynomial, capture)         INVOCABLE
```

**The key insight**: You can GO TO a town. You can GO TO a citizen. You can't GO TO a "greeting" - you DO a greeting.

From `spec/principles.md`:

> "To observe is to act. There is no neutral reading, no view from nowhere." (AGENTESE Meta-Principle)

Navigation IS observation. Clicking a navtree item IS acting. But the nature of the action differs:
- **Path navigation** = "I want to BE at this location"
- **Aspect invocation** = "I want to DO this operation"

These are categorically different. Conflating them breaks the model.

### AD-010 (Habitat Guarantee) Applies to PATHS, Not Aspects

> "Every registered AGENTESE path SHALL project into at least a minimal Habitat experience."

Aspects are not paths. They're **affordances** of paths. The Habitat is where you invoke aspects FROM, not where aspects live.

### AD-011 (Registry as Single Source of Truth)

> "The registry IS the territory. Frontend paths are claims about that territory."

Aspects aren't registered as paths. They're metadata ON paths (returned by `/affordances`). The navtree should show what the registry contains: paths.

### The Heterarchical Principle: Two Modes

> "Loop mode (autonomous): perception → action → feedback → repeat"
> "Function mode (composable): input → transform → output"

- **Paths** are explored in loop mode (navigate, perceive, navigate again)
- **Aspects** are invoked in function mode (call with args, get result)

The navtree is a loop-mode interface. Aspect invocation is function-mode. Mixing them creates UX dissonance.

## The Clean Model

```
┌─────────────────────────────────────────────────────────────────────────┐
│ NavTree (Loop Mode)                 │ Projection (Function Mode)        │
│ "Where can I go?"                   │ "What can I do here?"             │
│                                     │                                   │
│ ▶ world                             │ ┌───────────────────────────────┐ │
│   ▶ town                            │ │ Reference Panel               │ │
│     ○ citizen                       │ │                               │ │
│     ○ coalition                     │ │ Path: concept.gardener        │ │
│ ▶ concept                           │ │ Description: The 7th Jewel... │ │
│   ● gardener ◄── YOU ARE HERE       │ │                               │ │
│ ▶ self                              │ │ Aspects:                      │ │
│   ○ memory                          │ │  [manifest] [polynomial]      │ │
│                                     │ │  [alternatives] [witness]     │ │
│                                     │ │       ↑                       │ │
│                                     │ │  clickable = invoke (POST)    │ │
│                                     │ └───────────────────────────────┘ │
│                                     │                                   │
│                                     │ ┌───────────────────────────────┐ │
│                                     │ │ Playground (Result Area)      │ │
│                                     │ │                               │ │
│                                     │ │ > invoked: alternatives       │ │
│                                     │ │ { result appears here }       │ │
│                                     │ └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

**NavTree**: Shows registered PATHS only. No aspects.
**Projection**: Shows aspects as BUTTONS. Clicking invokes (POST). Result renders in playground.

## URL Semantics: The Colon Notation Question

What about `/concept.gardener:alternatives`? This URL is valid and useful for:
- Sharing a specific invocation
- Bookmarking a frequently-used aspect
- Deep-linking from docs

**Proposed behavior**:

```
URL: /concept.gardener:alternatives

1. Parse → path="concept.gardener", aspect="alternatives"
2. Navigate to path's projection (ConceptHomeProjection)
3. Projection sees aspect ≠ manifest
4. Auto-invoke aspect (POST /agentese/concept/gardener/alternatives)
5. Display result in Playground
6. URL stays as-is (captures intent for refresh/share)
```

The URL captures INTENT. The projection EXECUTES that intent. The user doesn't navigate TO the aspect - they navigate to the PATH with an aspect pre-invoked.

## Smart Aspect Rendering (The Real Feature)

The original ask - "auto-generating projections for page aspects" - makes sense, but reframed:

**Not**: "Aspects are pages that need projections"
**But**: "Aspect RESULTS need intelligent rendering"

```typescript
// In ConceptHomeProjection's Playground:

function AspectResultRenderer({ result }: { result: unknown }) {
  // Inspect result shape, choose renderer

  if (Array.isArray(result)) {
    return <AspectTable data={result} />;
  }

  if (hasShape(result, { nodes: 'array', edges: 'array' })) {
    return <AspectGraph data={result} />;
  }

  if (hasShape(result, { positions: 'array', current: 'string' })) {
    return <AspectPolynomial data={result} />;
  }

  if (typeof result === 'string' && result.includes('```')) {
    return <AspectMarkdown content={result} />;
  }

  return <AspectJson data={result} />;
}
```

This is **projection intelligence**, not **navigation sprawl**.

## Implementation Plan

### Phase 1: Revert Aspect Navigation

1. Remove aspect nodes from navtree's `buildTree()` function
2. Remove colon notation handling from `handleNavigateToPath()`
3. Aspects stay visible in Reference Panel as invocable buttons

### Phase 2: URL-Based Aspect Invocation

1. Update `useAgentese` hook to handle aspect from URL
2. When aspect ≠ manifest, make POST request (not GET)
3. ConceptHomeProjection auto-invokes if URL has aspect

### Phase 3: Smart Aspect Result Rendering

1. Create shape detection utility
2. Create aspect-specific renderers:
   - `AspectTable` - for arrays
   - `AspectGraph` - for {nodes, edges}
   - `AspectPolynomial` - for {positions, current, directions}
   - `AspectMarkdown` - for formatted strings
   - `AspectJson` - fallback
3. Integrate into ConceptHomeProjection's Playground

## Connection to Principles

| Principle | How This Embodies It |
|-----------|---------------------|
| **Tasteful** | Clean separation - navtree navigates, projection operates |
| **Curated** | Aspects shown where relevant (in projection), not everywhere |
| **Joy-Inducing** | Aspects feel like powers you wield, not places you visit |
| **Composable** | Paths compose; aspects are morphisms you apply at paths |
| **Generative** | Result renderers derived from shape, not hand-coded per aspect |
| **AD-010** | Paths have Habitats; aspects render WITHIN Habitats |
| **AD-011** | Registry = paths; aspects = affordances discovered at paths |

## What We're NOT Doing

- Adding GET support for aspects (POST is semantically correct)
- Making aspects navigable destinations in the navtree
- Creating separate projection components for each aspect
- Treating aspects as pages

## What We ARE Doing

- Recognizing aspects as OPERATIONS, not LOCATIONS
- Building smart result rendering into ConceptHomeProjection
- Supporting `:aspect` URLs as invocation-intent capture
- Keeping the navtree focused on what it does well: path exploration

## The Puppet Swap

From principles.md:
> "Concepts become concrete through projection into puppet structures."

We were using the **wrong puppet** for aspects:
- NavTree puppet: good for hierarchical exploration
- Aspects don't fit this puppet - they're not hierarchical children

The right puppet for aspects is the **Reference Panel + Playground**:
- Shows what operations are available
- Provides controls to invoke
- Displays results intelligently

---

*"The river doesn't ask the clock when to flow."* - Aspects flow from paths when invoked, not when navigated.
