---
path: concept.projection.openapi
mood: exploratory
momentum: 0.7
trajectory: crystallizing
season: SPROUTING
last_gardened: 2025-12-19
gardener: claude-sonnet-4

letter: |
  OpenAPI is not the territory—it's a projection for developers who think in REST.
  The AGENTESE-native experience lives at /docs/agentese, where observers matter
  and paths are verbs, not nouns.

  The core tension: REST assumes ONE route = ONE operation. AGENTESE asserts
  ONE path + MANY observers = MANY semantic operations. This isn't a bug to
  work around—it's the claim that what exists depends on who's looking.

  The Projection Protocol already establishes that projection is fundamentally
  lossy, and that's a feature. OpenAPI becomes just another target, like CLI
  or marimo, with its own fidelity characteristics.

resonates_with:
  - projection-protocol
  - agentese-v3
  - habitat-2.0
  - metaphysical-fullstack

entropy:
  available: 0.08
  spent: 0.00
  sips: []
---

# OpenAPI as AGENTESE Projection Surface

> *"Tasteful > feature-complete"* — Don't bolt on Swagger. Build an AGENTESE-native developer experience.

## The Core Insight

```
OpenAPI (REST)                    AGENTESE
─────────────                     ────────
ONE route + ONE method            ONE path + MANY observers
= ONE operation                   = MANY semantic operations

GET /api/users/123               logos.invoke("world.house.manifest", architect) → Blueprint
                                 logos.invoke("world.house.manifest", poet) → Metaphor
```

**This is not a paradigm mismatch to fix. It's observer-dependent perception made visible.**

---

## What Already Exists

| Component | Location | Status |
|-----------|----------|--------|
| Discovery endpoint | `/agentese/discover?include_metadata=true` | Working |
| Contract system | `@node(contracts={...})` | Phase 7 complete |
| Schema generation | `schema_gen.py` | Working |
| Observer headers | `X-Observer-Archetype`, `X-Observer-Capabilities` | Working |
| Examples metadata | `@node(examples=[...])` | Working |

**Gap**: No projection to OpenAPI spec. No developer-friendly documentation UI.

---

## Three Design Options

### Option A: Metadata Layer (Minimal)

Use `x-*` extensions, build custom docs UI.

```yaml
paths:
  /agentese/{path}/{aspect}:
    post:
      x-agentese:
        discovery: "/agentese/discover"
        observer_header: "X-Observer-Archetype"
```

**Pro**: Tasteful. **Con**: Requires custom UI work.

### Option B: Virtual Path Expansion (Verbose)

Generate OpenAPI operations for each `path + aspect`.

```yaml
paths:
  /agentese/world/town/manifest:
    post:
      operationId: world_town_manifest
      responses:
        200:
          schema:
            oneOf: [Guest, Mayor, Architect]
```

**Pro**: Standard tooling works. **Con**: Explosive growth (n × m × k operations).

### Option C: Projection Surface (The kgents Way) ← RECOMMENDED

Apply Projection Protocol: OpenAPI is just another target.

```
AGENTESE Registry (Source of Truth)
        ↓ AgenteseLens (Projection Functor)
        ↓ Fidelity: Medium (lossy)
        ↓ Observer: Developer
┌───────┴────────────────────────────────────────┐
│  /openapi/agentese.json  (enhanced spec)       │
│  /docs/agentese          (custom explorer)     │
│  /docs, /redoc           (standard FastAPI)    │
└────────────────────────────────────────────────┘
```

---

## Recommended Architecture

### Layer 1: Spec Generator

```python
# protocols/agentese/openapi.py
def generate_agentese_spec(
    base_path: str = "/agentese",
    include_examples: bool = True,
    include_contracts: bool = True,
) -> dict:
    """
    Generate OpenAPI 3.1 from AGENTESE registry.

    This is a PROJECTION—lossy by design.
    """
```

### Layer 2: Enhanced OpenAPI Endpoint

```python
# protocols/api/app.py
@app.get("/openapi/agentese.json")
async def agentese_openapi():
    from protocols.agentese.openapi import generate_agentese_spec
    return generate_agentese_spec()
```

### Layer 3: Custom Documentation UI

React component at `/docs/agentese`:
- Path explorer grouped by context (world.*, self.*, etc.)
- Observer archetype selector
- "Try it" with observer headers
- Examples runner (from NodeExample metadata)

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| OpenAPI as projection, not authority | Registry is truth; spec is derived |
| Observer in header, not path | Preserves REST compatibility while honoring AGENTESE |
| Custom docs UI at `/docs/agentese` | Standard Swagger at `/docs` for REST-minded devs |
| `x-agentese` extensions | Metadata for tools that understand the paradigm |

---

## Implementation Phases

### Phase 1: Spec Generator (2-3 hours)
- Create `protocols/agentese/openapi.py` (~200 lines)
- Read from registry, output OpenAPI 3.1
- Include `x-agentese` extensions
- Wire to `/openapi/agentese.json`

### Phase 2: Enhanced Discovery (1-2 hours)
- Ensure all nodes have `contracts` + `examples`
- Add effects to metadata response
- Test coverage for spec generation

### Phase 3: Documentation UI (4-6 hours)
- React component for `/docs/agentese`
- Context-grouped path explorer
- Observer archetype picker
- "Try it" functionality
- Examples runner

### Phase 4: Integration (1-2 hours)
- Link from `/docs` to `/docs/agentese`
- Navigation integration
- CLAUDE.md documentation

---

## OpenAPI Extensions Specification

```yaml
x-agentese:
  version: "3"
  contexts: ["world", "self", "concept", "void", "time"]
  observer_header: "X-Observer-Archetype"
  discovery_endpoint: "/agentese/discover"

x-agentese-path:
  path: "world.town"
  aspects: ["manifest", "citizen.list", "citizen.create"]
  effects: ["READS:town/citizens", "WRITES:town/citizens"]
  examples:
    - aspect: "manifest"
      kwargs: {}
      description: "Show town overview"
    - aspect: "citizen.list"
      kwargs: { "limit": 10 }
      description: "List first 10 citizens"

x-agentese-observer:
  archetypes:
    - name: "guest"
      description: "Minimal observer, default"
      capabilities: []
    - name: "developer"
      description: "Full access for development"
      capabilities: ["*"]
    - name: "mayor"
      description: "Town governance perspective"
      capabilities: ["town:govern", "citizen:moderate"]
```

---

## Open Questions

1. **Streaming Aspects**: Represent SSE/WebSocket in OpenAPI 3.1?
   - Proposal: `text/event-stream` media type + AsyncAPI reference for WS

2. **Void Context**: Should `void.*` appear in developer docs?
   - Proposal: Include with "entropy" tag, mark as non-deterministic

3. **Effect Composition**: Show `a >> b >> c` operations?
   - Proposal: Phase 2—focus on terminal aspects first

4. **Observer Response Variants**: How many archetypes to document?
   - Proposal: "guest" + "developer" initially, expand based on usage

---

## Alignment Check

| Kent's Voice Anchor | How This Embodies It |
|---------------------|----------------------|
| *"Daring, bold, creative"* | Doesn't just bolt on Swagger—builds AGENTESE-native experience |
| *"Tasteful > feature-complete"* | Minimal spec generator + custom UI, not explosive path expansion |
| *"The Mirror Test"* | Developer docs should feel like discovering AGENTESE, not REST-with-extra-steps |
| *"Joy-inducing"* | One-click examples, observer picker, context-grouped exploration |

---

## Files to Create/Modify

| File | Action |
|------|--------|
| `protocols/agentese/openapi.py` | Create: spec generator (~200 lines) |
| `protocols/api/app.py` | Add: `/openapi/agentese.json` endpoint |
| `web/src/pages/AgenteseDocs.tsx` | Create: custom docs UI |
| `web/src/shell/NavigationTree.tsx` | Add: `/docs/agentese` route |
| `CLAUDE.md` | Document: new projection surface |

---

## Success Criteria

- [ ] `/openapi/agentese.json` returns valid OpenAPI 3.1 spec
- [ ] Spec includes all registered paths from `/agentese/discover`
- [ ] `x-agentese` extensions preserve observer semantics
- [ ] `/docs/agentese` provides interactive exploration
- [ ] Examples from `@node(examples=[...])` are runnable in UI
- [ ] Standard `/docs` (Swagger) still works for REST developers

---

*"The projection is not the territory. But a good projection makes the territory navigable."*

*Created: 2025-12-19 | Status: SPROUTING*
