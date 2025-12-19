# AD-009: Metaphysical Fullstack Agent

**Date**: 2025-12-17

> Every agent SHOULD be a vertical slice from persistence to projection, with adapters living in service modules.

---

## Context

The question arose: "Should TableAdapters (persistence) live in infrastructure (models/) or in CLI handlers?" The answer: neither. Adapters belong in **service modules** because:

1. **Infrastructure doesn't know** what tables are for, why they're needed, or when to use them
2. **Handlers are presentation**, not business logic
3. **Service modules** own the domain semantics

## Decision

Every agent is a "metaphysical fullstack agent"—a complete vertical slice:

```
┌─────────────────────────────────────────────────────────────────┐
│                    PROJECTION SURFACES                          │
│   CLI  │  TUI  │  Web UI  │  marimo  │  JSON API  │  VR  │ ... │
└────────┼───────┼──────────┼──────────┼────────────┼──────┼─────┘
         ▼       ▼          ▼          ▼            ▼      ▼
┌─────────────────────────────────────────────────────────────────┐
│                  CONTAINER FUNCTOR (Main Website)               │
│           Shallow passthrough for component projections          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              AGENTESE UNIVERSAL PROTOCOL                        │
│   The protocol IS the API. No explicit routes needed.            │
│   All transports collapse to logos.invoke(path, observer, ...)   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      AGENTESE NODE                              │
│   Semantic interface: aspects, effects, affordances              │
│   Makes service available to all projections                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SERVICE MODULE                             │
│   services/<name>/ — Business logic + TableAdapters + D-gent     │
│   Frontend components live here too (if any)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    INFRASTRUCTURE LAYER                         │
│   agents/  │  models/  │  D-gent  │  LLM clients  │  ...        │
│   Generic, reusable categorical primitives                       │
└─────────────────────────────────────────────────────────────────┘
```

## The Key Separation

| Directory | Contains | Purpose |
|-----------|----------|---------|
| `agents/` | PolyAgent, Operad, Sheaf, Flux, D-gent | Categorical primitives |
| `services/` | Brain, Gardener, Town, Park, Atelier | Crown Jewels (consumers) |
| `models/` | SQLAlchemy ORM classes | Generic table definitions |
| `protocols/` | AGENTESE, CLI projection | Universal routing |

## AGENTESE Universal Protocol

Backend routes are NOT declared. The protocol auto-exposes all registered nodes:

```python
# All transports collapse to the same invocation:
logos.invoke("self.memory.capture", observer, content="...")

# CLI:       kg brain capture "content"
# HTTP:      POST /agentese/self.memory.capture
# WebSocket: {"path": "self.memory.capture", "args": {...}}
```

## Frontend Placement

Frontend components live **in the service module** (`services/brain/web/`). The main website is an **elastic container functor**—a shallow passthrough:

```typescript
// Main website: shallow passthrough
import { CrystalViewer } from '@kgents/services/brain/web';

export default function BrainPage() {
    return <PageShell><CrystalViewer /></PageShell>;
}
```

## Progressive Definition

The more fully an agent is defined, the more fully it projects:

| Defined | Projection |
|---------|------------|
| Service module only | Manual invocation works |
| + AGENTESE node | CLI/API work with auto-generated UI |
| + Frontend components | Rich custom UI available |
| + Full metadata | Budget tracking, streaming, observability |

## Anti-patterns

- Adapter in CLI handler (presentation layer touching persistence)
- Explicit backend routes (protocol should auto-expose)
- Business logic in any route (should go through AGENTESE node)
- Frontend bypassing AGENTESE (direct DB access)
- Main website with embedded logic (should be shallow passthrough)
- Crown Jewel in `agents/` (should be in `services/`)

## Implementation

See `docs/skills/metaphysical-fullstack.md`

*Zen Principle: The fullstack agent is complete in definition, universal in projection.*
