# AD-010: The Habitat Guarantee

**Date**: 2025-12-18

> Every registered AGENTESE path SHALL project into at least a minimal Habitat experience. No blank pages. No 404 behavior.

---

## Context

The NavigationTree discovers AGENTESE paths via `/agentese/discover`. Users can click any path—but paths without custom pages show nothing. This creates "seams" where exploration dead-ends. The user clicks, expecting discovery, and finds a wall.

## Decision

Every path has a **Habitat**—a minimum viable projection that makes exploration rewarding:

```
Habitat : AGENTESENode → ProjectedExperience

For all registered paths p:
  Habitat(p) = ReferencePanel(p) × Playground(p) × Teaching(p)

where:
  ReferencePanel(p) = p.metadata ∪ p.aspects ∪ MiniPolynomial(p)
  Playground(p)     = REPL.focus(p.path) ⊕ Examples(p) ⊕ Ghosts(p)
  Teaching(p)       = AspectHints × (enabled: TeachingMode)
```

## The Three Tiers (Progressive Enhancement)

| Tier | Metadata Required | Experience |
|------|-------------------|------------|
| **Minimal** | Path only | Path header + context badge + warm "cultivating" copy + REPL input |
| **Standard** | Description + aspects | Reference Panel + REPL seeded with examples |
| **Rich** | Custom playground | Full bespoke visualization (Crown Jewels) |

## The Three Layers (Habitat 2.0)

| Layer | Component | Purpose | Status |
|-------|-----------|---------|--------|
| **Layer 1** | Adaptive Habitat | Universal fallback projection for all paths | ✅ Complete |
| **Layer 2** | MiniPolynomial | State machine visualization in Reference Panel | Planned |
| **Layer 3** | Ghost Integration | Différance made visible via alternatives | Planned |

## Warm Copy for Minimal Tier

Even paths with no metadata feel intentional:

> *"This path is being cultivated. Every kgents path grows from a seed—this one is young. You can still explore it via the REPL below."*

## The Affirmative Framing

- **Not**: "No orphan paths" (negative)
- **But**: "Every path has a home" (affirmative)

## Connection to Principles

| Principle | How Habitat Embodies It |
|-----------|------------------------|
| **Tasteful** | No blank pages; every path gets considered treatment |
| **Joy-Inducing** | Discovery rewards; warm copy signals care |
| **Generative** | Tier derives from metadata; implementation follows spec |
| **Composable** | Habitat is a morphism; composes with Projection Protocol |

## Anti-patterns

- Blank 404 for unmapped paths (violates Habitat Guarantee)
- Custom component for every path (unsustainable; use Generated Playground)
- Dense error copy in Minimal tier (should feel cultivated, not broken)
- Teaching always on (toggleable, off by default for guests)

## Implementation

See `spec/protocols/concept-home.md` (renamed to `habitat.md`)

*Zen Principle: The seams disappear when every path has somewhere to go.*
