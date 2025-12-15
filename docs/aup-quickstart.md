# AUP Quick Start Guide

Get started with the AGENTESE Universal Protocol in 5 minutes.

## Prerequisites

```bash
# API endpoint
export AUP_BASE_URL="http://localhost:8000/api/v1"

# Your API key (get from admin)
export AUP_API_KEY="kg_dev_carol"
```

## 1. Your First Request: Manifest

See how an entity appears to you:

```bash
curl -X GET "$AUP_BASE_URL/world/codebase/manifest" \
  -H "X-API-Key: $AUP_API_KEY" \
  -H "X-Observer-Archetype: developer"
```

Response:
```json
{
  "handle": "world.codebase.manifest",
  "result": {
    "modules": ["auth", "api", "core"],
    "test_coverage": 0.87
  },
  "meta": {
    "observer": "developer",
    "span_id": "abc123",
    "duration_ms": 45
  }
}
```

## 2. Check Your Affordances

See what you can do:

```bash
curl -X GET "$AUP_BASE_URL/concept/architecture/affordances" \
  -H "X-API-Key: $AUP_API_KEY" \
  -H "X-Observer-Archetype: architect"
```

Response:
```json
{
  "path": "concept.architecture",
  "affordances": ["manifest", "witness", "refine", "define", "spawn"],
  "observer_archetype": "architect"
}
```

## 3. Invoke an Aspect

Do something with an entity:

```bash
curl -X POST "$AUP_BASE_URL/concept/summary/refine" \
  -H "X-API-Key: $AUP_API_KEY" \
  -H "X-Observer-Archetype: developer" \
  -H "Content-Type: application/json" \
  -d '{
    "kwargs": {
      "input": "This is a long document about microservices...",
      "max_length": 100
    }
  }'
```

## 4. Compose a Pipeline

Chain multiple operations:

```bash
curl -X POST "$AUP_BASE_URL/compose" \
  -H "X-API-Key: $AUP_API_KEY" \
  -H "X-Observer-Archetype: developer" \
  -H "Content-Type: application/json" \
  -d '{
    "paths": [
      "world.document.manifest",
      "concept.summary.refine",
      "self.memory.engram"
    ]
  }'
```

Response includes pipeline trace:
```json
{
  "result": "engram-789",
  "pipeline_trace": [
    {"path": "world.document.manifest", "duration_ms": 23},
    {"path": "concept.summary.refine", "duration_ms": 156},
    {"path": "self.memory.engram", "duration_ms": 12}
  ],
  "laws_verified": ["identity", "associativity"]
}
```

## 5. Stream Long Operations

For real-time responses (SSE):

```bash
curl -X GET "$AUP_BASE_URL/self/soul/challenge/stream?challenge=How+should+I+design+this+API" \
  -H "X-API-Key: $AUP_API_KEY" \
  -H "X-Observer-Archetype: developer" \
  -H "Accept: text/event-stream"
```

Events stream as:
```
event: chunk
data: {"type":"response","content":"Consider","partial":true}

event: chunk
data: {"type":"response","content":" the","partial":true}

event: done
data: {"span_id":"def456","chunks_count":47}
```

## Observer Archetypes

| Archetype | Typical Affordances |
|-----------|---------------------|
| `viewer` | manifest, witness |
| `developer` | manifest, witness, refine |
| `architect` | manifest, witness, refine, define, spawn |
| `admin` | All affordances |
| `agent` | Depends on agent capabilities |

## The Five Contexts

| Context | Use For | Examples |
|---------|---------|----------|
| `world.*` | External things | `world.codebase`, `world.document` |
| `self.*` | Internal state | `self.soul`, `self.memory` |
| `concept.*` | Abstract ideas | `concept.summary`, `concept.justice` |
| `void.*` | Creativity | `void.slop`, `void.dream` |
| `time.*` | History | `time.trace`, `time.forecast` |

## Error Handling

All errors include helpful context:

```json
{
  "detail": {
    "error": "Affordance 'spawn' not available",
    "code": "AFFORDANCE_DENIED",
    "why": "Requires architect privileges",
    "suggestion": "Use 'manifest' instead or request elevation",
    "available": ["manifest", "witness"]
  }
}
```

## Python Example

```python
import httpx

client = httpx.Client(
    base_url="http://localhost:8000/api/v1",
    headers={
        "X-API-Key": "kg_dev_carol",
        "X-Observer-Archetype": "developer",
    }
)

# Manifest
response = client.get("/world/codebase/manifest")
codebase = response.json()["result"]

# Compose pipeline
response = client.post("/compose", json={
    "paths": [
        "world.document.manifest",
        "concept.summary.refine",
    ]
})
summary = response.json()["result"]

# Stream with SSE
with client.stream("GET", "/self/soul/challenge/stream",
                   params={"challenge": "Help me design this"}) as r:
    for line in r.iter_lines():
        if line.startswith("data:"):
            print(line[5:])
```

## TypeScript Example

```typescript
const AUP_BASE = "http://localhost:8000/api/v1";
const headers = {
  "X-API-Key": "kg_dev_carol",
  "X-Observer-Archetype": "developer",
};

// Manifest
const manifest = await fetch(`${AUP_BASE}/world/codebase/manifest`, { headers })
  .then(r => r.json());

// Compose
const composition = await fetch(`${AUP_BASE}/compose`, {
  method: "POST",
  headers: { ...headers, "Content-Type": "application/json" },
  body: JSON.stringify({
    paths: ["world.document.manifest", "concept.summary.refine"]
  })
}).then(r => r.json());

// Stream (SSE)
const eventSource = new EventSource(
  `${AUP_BASE}/self/soul/challenge/stream?challenge=Help+me`
);
eventSource.onmessage = (e) => console.log(JSON.parse(e.data));
```

## Next Steps

- [Full User Journeys](./aup-user-journeys.md) - Detailed scenarios
- [API Reference](./api-reference.md) - Complete endpoint documentation
- [AGENTESE Spec](../spec/protocols/agentese.md) - Protocol specification

---

*Need help? Open an issue or ask K-gent: `GET /api/v1/self/soul/challenge/stream?challenge=...`*
