# AD-012: Aspect Projection Protocol

**Date**: 2025-12-19

> Paths are PLACES; aspects are ACTIONS. Navigation shows paths. Projection provides aspects.

---

## Context

The NavigationTree was showing aspects (`:manifest`, `:polynomial`, `:witness`) as clickable children of paths. This caused 405 errors—clicking them triggered GET requests on what should be POST operations. The confusion ran deeper: treating aspects as "places to go" rather than "actions to take."

## The Semantic Distinction

```
Level 1: Contexts (world, self, concept, void, time)     NAVIGABLE
Level 2: Holons (town, memory, gardener, etc.)           NAVIGABLE
Level 3: Entities (citizen.kent_001, crystal.abc123)     NAVIGABLE
Level 4: Aspects (manifest, polynomial, capture)         INVOCABLE
```

**Key Insight**: You can GO TO a town. You can GO TO a citizen. You can't GO TO a "greeting"—you DO a greeting.

## Decision

Strict separation of concerns:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ NavTree (Loop Mode)                 │ Projection (Function Mode)        │
│ "Where can I go?"                   │ "What can I do here?"             │
│                                     │                                   │
│ ▶ world                             │ ┌───────────────────────────────┐ │
│   ▶ town                            │ │ Reference Panel               │ │
│     ○ citizen                       │ │                               │ │
│     ○ coalition                     │ │ Path: concept.gardener        │ │
│ ▶ concept                           │ │                               │ │
│   ● gardener ◄── YOU ARE HERE       │ │ Aspects:                      │ │
│ ▶ self                              │ │  [manifest] [polynomial]      │ │
│   ○ memory                          │ │  [alternatives] [witness]     │ │
│                                     │ │       ↑                       │ │
│                                     │ │  clickable = invoke (POST)    │ │
│                                     │ └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

## The URL Notation

`/{path}:{aspect}` is valid for:
- Sharing a specific invocation
- Bookmarking a frequently-used aspect
- Deep-linking from docs

The colon captures INTENT. The projection EXECUTES that intent.

## Connection to Heterarchical Principle

- **Paths** are explored in loop mode (navigate, perceive, navigate again)
- **Aspects** are invoked in function mode (call with args, get result)

The navtree is a loop-mode interface. Aspect invocation is function-mode. Mixing them creates UX dissonance.

## Connection to Puppet Constructions

We were using the **wrong puppet** for aspects:
- NavTree puppet: good for hierarchical exploration
- Aspects don't fit this puppet—they're not hierarchical children

The right puppet for aspects is the **Reference Panel + Playground**:
- Shows what operations are available
- Provides controls to invoke
- Displays results intelligently

## Consequences

1. **NavTree shows paths only**: Aspects are never added as children
2. **ReferencePanel shows aspects as buttons**: Click invokes (POST)
3. **Aspects feel like powers**: Something you wield, not somewhere you visit
4. **URL captures intent**: `/{path}:{aspect}` invokes on load
5. **AD-010 applies to paths**: Habitats are for paths; aspects render WITHIN habitats

## Anti-patterns

- Adding aspects as navtree children (causes 405 errors)
- Making aspects navigable GET destinations (semantic confusion)
- Separate pages for each aspect (unsustainable, unnecessary)
- Treating aspects as places (they're verbs, not nouns)

## Implementation

See `plans/aspect-projection-protocol.md`, `impl/claude/web/src/shell/NavigationTree.tsx`

*Zen Principle: The river doesn't ask the clock when to flow. Aspects flow from paths when invoked, not when navigated.*
