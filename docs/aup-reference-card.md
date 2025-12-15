# AUP Reference Card

## Endpoints

```
GET  /api/v1/{ctx}/{holon}/manifest        Perceive entity
GET  /api/v1/{ctx}/{holon}/affordances     List capabilities
POST /api/v1/{ctx}/{holon}/{aspect}        Invoke action
POST /api/v1/compose                        Chain operations
GET  /api/v1/{ctx}/{holon}/{aspect}/stream SSE streaming
POST /api/v1/verify-laws                    Check category laws
GET  /api/v1/{ctx}/{holon}/resolve          Path metadata
```

## Required Headers

```http
X-API-Key: kg_your_key
X-Observer-Archetype: developer|architect|viewer|admin|agent
X-Observer-Id: unique-id (optional)
X-Observer-Capabilities: cap1,cap2 (optional)
```

## Contexts

| ctx | Domain | Examples |
|-----|--------|----------|
| `world` | External | codebase, document, api |
| `self` | Internal | soul, memory, config |
| `concept` | Abstract | summary, justice, pattern |
| `void` | Entropy | slop, dream, chaos |
| `time` | Temporal | trace, forecast, schedule |

## Aspects (Affordances)

| Aspect | Category | Description |
|--------|----------|-------------|
| `manifest` | Perception | View as observer sees it |
| `witness` | Perception | Historical trace |
| `affordances` | Perception | What can be done |
| `refine` | Generation | Dialectic refinement |
| `define` | Generation | Create new entity |
| `spawn` | Generation | Create agent instance |
| `sip` | Entropy | Draw randomness |
| `tithe` | Entropy | Pay for order |

## Observer Archetypes

| Archetype | Default Affordances |
|-----------|---------------------|
| `viewer` | manifest, witness, affordances |
| `developer` | + refine |
| `architect` | + define, spawn |
| `admin` | all |
| `agent` | per-agent config |

## Error Codes → HTTP

| Code | HTTP | Meaning |
|------|------|---------|
| `PATH_NOT_FOUND` | 404 | Entity doesn't exist |
| `AFFORDANCE_DENIED` | 403 | No permission |
| `OBSERVER_REQUIRED` | 401 | Missing observer |
| `SYNTAX_ERROR` | 400 | Bad path format |
| `LAW_VIOLATION` | 422 | Category law broken |
| `BUDGET_EXHAUSTED` | 429 | Rate limited |

## Composition

```json
POST /api/v1/compose
{
  "paths": [
    "world.doc.manifest",
    "concept.summary.refine",
    "self.memory.engram"
  ],
  "initial_input": null,
  "emit_law_check": true
}
```

Response includes `pipeline_trace` and `laws_verified`.

## SSE Events

```
event: chunk
data: {"type":"response|thinking","content":"...","partial":bool}

event: done
data: {"result":"...","span_id":"...","chunks_count":N}

event: error
data: {"code":"...","error":"..."}
```

## Path Format

```
{context}.{holon}.{aspect}
   │         │        └── What to do (manifest, refine, etc.)
   │         └────────── Entity name
   └──────────────────── Domain (world, self, concept, void, time)
```

## Category Laws

1. **Identity**: `Id >> f ≡ f ≡ f >> Id`
2. **Associativity**: `(f >> g) >> h ≡ f >> (g >> h)`
3. **Observer Polymorphism**: Same path, different observer → different result

## Quick Examples

```bash
# Manifest
curl "$URL/world/codebase/manifest" -H "X-API-Key: $KEY" -H "X-Observer-Archetype: developer"

# Invoke
curl -X POST "$URL/concept/summary/refine" -H "X-API-Key: $KEY" \
  -H "X-Observer-Archetype: developer" -H "Content-Type: application/json" \
  -d '{"kwargs":{"input":"..."}}'

# Stream
curl "$URL/self/soul/challenge/stream?challenge=Help" \
  -H "X-API-Key: $KEY" -H "Accept: text/event-stream"
```

---

*AGENTESE: There is no view from nowhere.*
