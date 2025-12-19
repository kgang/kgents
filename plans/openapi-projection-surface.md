---
path: concept.projection.openapi
mood: exploratory
momentum: 0.8
trajectory: crystallizing
season: SPROUTING
last_gardened: 2025-12-19
gardener: claude-opus-4-5

letter: |
  OpenAPI is not the territory—it's a projection for developers who think in REST.
  The AGENTESE-native experience lives at /docs/agentese, where observers matter
  and paths are verbs, not nouns.

  The core tension: REST assumes ONE route = ONE operation. AGENTESE asserts
  ONE path + MANY observers = MANY semantic operations. This isn't a bug to
  work around—it's the claim that what exists depends on who's looking.

  What changed: The infrastructure is mostly there! Discovery endpoint returns
  metadata + schemas. Schema generator converts contracts. The gap is smaller
  than expected—just the OpenAPI wrapper and custom docs UI.

resonates_with:
  - projection-protocol
  - agentese-v3
  - habitat-2.0
  - metaphysical-fullstack
  - agentese-node-overhaul-strategy

entropy:
  available: 0.08
  spent: 0.02
  sips:
    - "2025-12-19: Discovered schema_gen.py already exists—infrastructure ahead of plan"
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

## Infrastructure Audit (2025-12-19)

### What Already Exists ✅

| Component | Location | Status | Notes |
|-----------|----------|--------|-------|
| **Discovery endpoint** | `/agentese/discover` | ✅ Working | Returns paths, stats |
| **Metadata support** | `?include_metadata=true` | ✅ Working | aspects, effects, examples |
| **Schema generation** | `?include_schemas=true` | ✅ Working | JSON Schema for contracts |
| **Contract system** | `@node(contracts={...})` | ✅ Working | 10+ nodes with contracts |
| **Schema generator** | `schema_gen.py` | ✅ Working | dataclass → JSON Schema |
| **Observer headers** | `X-Observer-Archetype` | ✅ Working | Gateway extracts observer |
| **Examples metadata** | `@node(examples=[...])` | ✅ Working | NodeExample → discovery |
| **Frontend projection registry** | `registry.tsx` | ✅ Working | Path → Component mapping |
| **NavTree discovery** | `NavigationTree.tsx` | ✅ Working | Auto-populates from `/discover` |

### What's Missing ❌

| Gap | Priority | Effort |
|-----|----------|--------|
| **OpenAPI 3.1 wrapper** | High | 2-3h |
| **`x-agentese` extensions** | High | 1h |
| **Custom `/docs/agentese` UI** | Medium | 4-6h |
| **Effects in discovery** | Low | 1h |

**Key Insight**: The gap is ~8h, not the 14h originally estimated. Infrastructure is ahead of documentation.

---

## Updated Architecture

### The Discovery Endpoint IS the Source of Truth

```python
# This already works!
GET /agentese/discover?include_metadata=true&include_schemas=true

# Returns:
{
  "paths": ["world.town", "self.memory", ...],
  "stats": { "registered_nodes": 24, "contexts": ["world", "self", ...] },
  "metadata": {
    "world.town": {
      "path": "world.town",
      "aspects": ["manifest", "citizen.list", ...],
      "effects": [],
      "examples": [{ "aspect": "manifest", "kwargs": {} }]
    }
  },
  "schemas": {
    "world.town": {
      "manifest": { "response": { "type": "object", "properties": {...} } }
    }
  },
  "contract_coverage": { "paths_with_contracts": 18, "total_paths": 24, "coverage_pct": 75.0 }
}
```

### Layer 1: OpenAPI Projection Functor

```python
# NEW: protocols/agentese/openapi.py (~150 lines)

class OpenAPILens:
    """
    Functor: AGENTESE Registry → OpenAPI 3.1 Spec

    This is a PROJECTION—lossy by design.
    Observer semantics map to x-agentese extensions.
    """

    def project(self) -> dict:
        """Generate OpenAPI 3.1 from /agentese/discover data."""
```

### Layer 2: Custom Documentation UI

```
/docs           → Standard FastAPI Swagger (REST developers)
/docs/agentese  → AGENTESE-native explorer (our developers)
```

The custom UI provides:
- Context-grouped path explorer (world.*, self.*, etc.)
- Observer archetype selector (guest, developer, mayor, etc.)
- "Try it" with observer headers auto-populated
- Examples runner (from `NodeExample` metadata)
- Effects visibility (reads/writes)

---

## Implementation Phases (Revised)

### Phase 1: OpenAPI Lens (2-3 hours) ← START HERE

**Files to create:**
```
impl/claude/protocols/agentese/openapi.py  (~150 lines)
```

**Implementation:**

```python
"""
OpenAPI Projection Surface.

The AgenteseLens functor projects AGENTESE registry → OpenAPI 3.1 spec.
This is lossy by design: observer-dependence maps to x-agentese extensions.
"""

from __future__ import annotations

from typing import Any

from .registry import get_registry

def generate_openapi_spec(
    title: str = "KGENTS AGENTESE API",
    version: str = "3.1.0",
    base_path: str = "/agentese",
) -> dict[str, Any]:
    """
    Generate OpenAPI 3.1 spec from AGENTESE registry.

    This is a PROJECTION—lossy by design:
    - Observer semantics → x-agentese extensions
    - Streaming aspects → text/event-stream media type
    - Examples → OpenAPI examples object
    """
    registry = get_registry()
    paths_data = registry.list_paths()

    spec: dict[str, Any] = {
        "openapi": "3.1.0",
        "info": {
            "title": title,
            "version": version,
            "description": "AGENTESE Universal Protocol - Observer-dependent API",
            "x-agentese": {
                "version": "3",
                "contexts": ["world", "self", "concept", "void", "time"],
                "observer_header": "X-Observer-Archetype",
                "discovery_endpoint": f"{base_path}/discover",
            },
        },
        "servers": [{"url": base_path}],
        "paths": {},
        "components": {
            "securitySchemes": {
                "observerHeader": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-Observer-Archetype",
                    "description": "Observer archetype (guest, developer, mayor, etc.)",
                },
            },
            "schemas": {},
        },
    }

    # Generate path operations from registry
    for agentese_path in paths_data:
        _add_path_operations(spec, agentese_path, registry, base_path)

    return spec


def _add_path_operations(
    spec: dict[str, Any],
    agentese_path: str,
    registry: Any,
    base_path: str,
) -> None:
    """Add OpenAPI operations for an AGENTESE path."""
    # Convert dots to slashes for OpenAPI path
    url_path = f"/{agentese_path.replace('.', '/')}"

    metadata = registry.get_metadata(agentese_path)
    contracts = registry.get_contracts(agentese_path) or {}

    # Base path operation (manifest)
    spec["paths"][f"{url_path}/manifest"] = {
        "get": {
            "operationId": f"{agentese_path.replace('.', '_')}_manifest",
            "summary": f"Manifest {agentese_path}",
            "description": metadata.description if metadata else None,
            "tags": [agentese_path.split(".")[0]],  # Context as tag
            "x-agentese-path": agentese_path,
            "responses": {
                "200": {
                    "description": "Successful manifest",
                    "content": {"application/json": {}},
                },
            },
        },
    }

    # Add aspect operations
    for aspect, contract in contracts.items():
        if aspect == "manifest":
            continue  # Already added above

        aspect_url = f"{url_path}/{aspect}"
        spec["paths"][aspect_url] = {
            "post": {
                "operationId": f"{agentese_path.replace('.', '_')}_{aspect.replace('.', '_')}",
                "summary": f"Invoke {aspect} on {agentese_path}",
                "tags": [agentese_path.split(".")[0]],
                "x-agentese-path": agentese_path,
                "x-agentese-aspect": aspect,
                "responses": {
                    "200": {"description": "Successful invocation"},
                },
            },
        }


class OpenAPILens:
    """
    Functor: AGENTESE Registry → OpenAPI 3.1 Spec

    The lens is the projection function. Calling project() invokes
    the functor, collapsing AGENTESE semantics into REST semantics.
    """

    def __init__(
        self,
        title: str = "KGENTS AGENTESE API",
        version: str = "3.1.0",
        base_path: str = "/agentese",
    ):
        self.title = title
        self.version = version
        self.base_path = base_path

    def project(self) -> dict[str, Any]:
        """Project AGENTESE registry to OpenAPI spec."""
        return generate_openapi_spec(
            title=self.title,
            version=self.version,
            base_path=self.base_path,
        )
```

**Wire to gateway:**
```python
# In gateway.py, add after discovery endpoints:

@router.get("/openapi.json")
async def openapi_spec() -> JSONResponse:
    """OpenAPI 3.1 spec projected from AGENTESE registry."""
    from .openapi import generate_openapi_spec
    return JSONResponse(content=generate_openapi_spec())
```

**Tests:**
```python
# protocols/agentese/_tests/test_openapi.py

def test_openapi_spec_valid():
    """Generated spec is valid OpenAPI 3.1."""
    spec = generate_openapi_spec()
    assert spec["openapi"] == "3.1.0"
    assert "paths" in spec
    assert "x-agentese" in spec["info"]

def test_openapi_includes_registered_paths():
    """All registered paths appear in spec."""
    spec = generate_openapi_spec()
    # At least discover endpoint should exist
    assert any("/discover" in p for p in spec["paths"])
```

---

### Phase 2: Gateway Integration (1 hour)

**Modify:** `protocols/api/app.py`

```python
# After mounting AGENTESE gateway
@app.get("/openapi/agentese.json")
async def agentese_openapi():
    """
    OpenAPI spec for AGENTESE protocol.

    This is a PROJECTION of the AGENTESE registry.
    For the authoritative source, use /agentese/discover.
    """
    from protocols.agentese.openapi import generate_openapi_spec
    return JSONResponse(content=generate_openapi_spec())
```

---

### Phase 3: Custom Documentation UI (4-6 hours) — OPTIONAL

> *"Tasteful > feature-complete"* — Ship Phase 1+2 first. This is a nice-to-have.

**Files to create:**
```
impl/claude/web/src/pages/AgenteseDocs.tsx
```

The custom UI would feature:
- Path tree grouped by context (world.*, self.*, etc.)
- Observer archetype picker (dropdown)
- Aspect list with "Try it" buttons
- Response preview panel
- Examples runner

**Decision**: Defer to Phase 4 after validating Phase 1+2 work.

---

## x-agentese Extension Specification

```yaml
# Info-level extension (spec metadata)
x-agentese:
  version: "3"
  contexts: ["world", "self", "concept", "void", "time"]
  observer_header: "X-Observer-Archetype"
  discovery_endpoint: "/agentese/discover"
  capabilities_header: "X-Observer-Capabilities"

# Path-level extension (per path)
x-agentese-path: "world.town"
x-agentese-aspect: "citizen.list"  # For non-manifest operations
x-agentese-effects: ["READS:town/citizens"]
x-agentese-examples:
  - aspect: "manifest"
    kwargs: {}
    description: "Show town overview"

# Observer extension (response documentation)
x-agentese-observer-variants:
  guest:
    description: "Minimal view for anonymous users"
  developer:
    description: "Full debug information"
  mayor:
    description: "Governance perspective with moderation controls"
```

---

## Open Questions (Updated)

1. **Streaming Aspects**: How to represent SSE in OpenAPI 3.1?
   - **Answer**: Use `text/event-stream` media type in response content

2. **Void Context**: Should `void.*` appear in developer docs?
   - **Answer**: Yes, with "entropy" tag. Mark as non-deterministic.

3. **Observer Response Variants**: How many archetypes to document?
   - **Answer**: Start with "guest" + "developer". Add others based on usage.

4. **Contract Coverage**: What's the current coverage?
   - **Answer**: ~75% (18/24 paths) based on `?include_schemas=true` response

---

## Success Criteria

- [x] `/agentese/discover` returns metadata + schemas (already works)
- [x] `/agentese/openapi.json` returns valid OpenAPI 3.1 spec (183 paths!)
- [x] Spec includes `x-agentese` extensions preserving observer semantics
- [x] Standard `/docs` (Swagger) still works for REST developers
- [x] Tests validate spec generation (42 tests, all passing)
- [x] Edge case tests (streaming collision, nested aspects, similar prefixes)
- [x] Property-based tests (Hypothesis for schema generation robustness)
- [x] Error surface documentation (x-agentese-schema-error on failure)
- [ ] (Optional) `/docs/agentese` provides interactive exploration

---

## Alignment Check

| Kent's Voice Anchor | How This Embodies It |
|---------------------|----------------------|
| *"Daring, bold, creative"* | Doesn't just bolt on Swagger—treats OpenAPI as projection surface |
| *"Tasteful > feature-complete"* | Phase 1+2 only (~3h). Defers custom UI until proven needed. |
| *"The Mirror Test"* | OpenAPI serves REST devs; AGENTESE-native experience lives at `/discover` |
| *"Joy-inducing"* | One-click examples, observer picker in eventual custom docs |

---

## Dependencies

- **Node Overhaul** (agentese-node-overhaul-strategy.md): More nodes with contracts = richer OpenAPI spec
- **Router Consolidation**: Already 50% complete. All routes flow through gateway.
- **NavTree**: Already uses `/agentese/discover`. OpenAPI is parallel projection.

---

## Files Summary

| File | Action | Lines |
|------|--------|-------|
| `protocols/agentese/openapi.py` | Create | ~150 |
| `protocols/agentese/gateway.py` | Add endpoint | +10 |
| `protocols/agentese/_tests/test_openapi.py` | Create | ~50 |
| `protocols/api/app.py` | Add route | +5 |

**Total new code**: ~215 lines

---

---

## Robustification (2025-12-19)

### Improvements Made

| Issue | Fix | Tests Added |
|-------|-----|-------------|
| **Streaming aspect collision** | Distinguish `/path/stream` (aspect named stream) from `/path/aspect/stream` (streaming variant) | 2 tests |
| **Edge cases missing** | Added tests for nested aspects, similar prefixes, paths without contracts | 6 tests |
| **Property-based tests** | Hypothesis-based tests for schema generation, spec structure invariants | 6 tests |
| **Silent schema failures** | Added `x-agentese-schema-error` extension when schema generation fails | 3 tests |

### Test Coverage Summary

| Category | Tests | Description |
|----------|-------|-------------|
| **Spec Generation** | 8 | OpenAPI 3.1 structure, x-agentese extensions |
| **OpenAPILens** | 2 | Lens pattern, custom config |
| **Path Operations** | 5 | Manifest, affordances, streaming, contracts |
| **Spec Validity** | 3 | Paths, operation IDs, responses |
| **Integration** | 2 | No exceptions, JSON serializable |
| **Edge Cases** | 6 | Nested aspects, prefixes, tags, mutations, errors |
| **Schema Generation** | 7 | Optional, nested, lists, dicts, enums, defaults, docs |
| **Property-Based** | 6 | Invariants, determinism, type coverage |
| **Error Surface** | 3 | Schema failure visibility |
| **Total** | **42** | Up from 19 → 42 (2.2x coverage) |

---

*"The projection is not the territory. But a good projection makes the territory navigable."*

*Created: 2025-12-19 | Updated: 2025-12-19 | Status: BLOOMING (Robustified)*
