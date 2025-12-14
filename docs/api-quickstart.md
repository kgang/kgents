# API Quickstart Guide

> *"Your first API call in 5 minutes."*

This guide gets you from zero to making your first kgents API call.

---

## Overview

The kgents SaaS API provides:
- **AGENTESE**: Invoke semantic paths for agent interactions
- **K-gent Sessions**: Conversational sessions with the K-gent persona

Base URL: `https://api.kgents.io/v1` (or your self-hosted instance)

---

## Authentication

All API requests require an API key in the `X-API-Key` header.

```bash
curl -H "X-API-Key: kg_your_key_here" https://api.kgents.io/v1/health
```

### API Key Format

Keys follow the format: `kg_{prefix}_{secret}`
- `kg_` - Required prefix
- `{prefix}` - 5-character identifier
- `{secret}` - Random secret (never share this!)

### Scopes

API keys have scopes that control access:
| Scope | Permissions |
|-------|-------------|
| `read` | Query sessions, resolve paths, list affordances |
| `write` | Create sessions, send messages, invoke paths |
| `admin` | Manage API keys, tenant settings |

---

## Quick Start: K-gent Session

### 1. Create a Session

```bash
curl -X POST https://api.kgents.io/v1/kgent/sessions \
  -H "X-API-Key: kg_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Session",
    "mode": "reflect"
  }'
```

Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "tenant_id": "...",
  "title": "My First Session",
  "agent_type": "kgent",
  "status": "active",
  "message_count": 0,
  "tokens_used": 0,
  "created_at": "2025-12-14T..."
}
```

### 2. Send a Message

```bash
curl -X POST https://api.kgents.io/v1/kgent/sessions/{session_id}/messages \
  -H "X-API-Key: kg_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What patterns am I avoiding?",
    "stream": false
  }'
```

Response:
```json
{
  "id": "...",
  "session_id": "550e8400-...",
  "role": "assistant",
  "content": "That's an interesting question to explore...",
  "tokens_used": 150,
  "created_at": "2025-12-14T..."
}
```

### 3. Get Message History

```bash
curl https://api.kgents.io/v1/kgent/sessions/{session_id}/messages \
  -H "X-API-Key: kg_your_key_here"
```

---

## Quick Start: AGENTESE

AGENTESE is a semantic path system for agent interactions.

### Path Format

```
{context}.{entity}.{aspect}
```

Contexts:
- `world` - External entities
- `self` - Internal state (soul, memory)
- `concept` - Abstract definitions
- `void` - Entropy/randomness
- `time` - Temporal operations

### Invoke a Path

```bash
curl -X POST https://api.kgents.io/v1/agentese/invoke \
  -H "X-API-Key: kg_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "path": "self.soul.challenge",
    "observer": {
      "name": "developer",
      "archetype": "developer"
    },
    "kwargs": {
      "input": "My startup idea"
    }
  }'
```

### Resolve Path Info

```bash
curl "https://api.kgents.io/v1/agentese/resolve?path=self.soul" \
  -H "X-API-Key: kg_your_key_here"
```

### List Affordances

```bash
curl "https://api.kgents.io/v1/agentese/affordances?path=self.soul&archetype=developer" \
  -H "X-API-Key: kg_your_key_here"
```

---

## Dialogue Modes

K-gent supports different dialogue modes:

| Mode | Description |
|------|-------------|
| `reflect` | Thoughtful introspection |
| `advise` | Practical guidance |
| `challenge` | Dialectic pushback |
| `explore` | Open-ended exploration |

Set mode when creating a session or per-message:
```json
{"message": "...", "mode": "challenge", "stream": false}
```

---

## Streaming Responses

Set `stream: true` to receive Server-Sent Events:

```bash
curl -X POST https://api.kgents.io/v1/kgent/sessions/{id}/messages \
  -H "X-API-Key: kg_your_key_here" \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me a story", "stream": true}'
```

Events:
- `event: chunk` - Partial response text
- `event: complete` - Final message with metadata
- `event: error` - Error occurred

---

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Bad request (invalid path, mode, etc.) |
| 401 | Invalid or missing API key |
| 403 | Insufficient scope |
| 404 | Resource not found |
| 422 | Validation error |
| 429 | Rate limit exceeded |

Error response format:
```json
{
  "detail": "Error description"
}
```

---

## Rate Limits

Limits depend on your subscription tier:

| Tier | Requests/Day |
|------|--------------|
| FREE | 100 |
| PRO | 1,000 |
| ENTERPRISE | 10,000+ |

Rate limit headers:
- `X-RateLimit-Limit`: Max requests
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset timestamp

---

## Python SDK Example

```python
import httpx

API_KEY = "kg_your_key_here"
BASE_URL = "https://api.kgents.io/v1"

async def main():
    async with httpx.AsyncClient() as client:
        # Create session
        resp = await client.post(
            f"{BASE_URL}/kgent/sessions",
            headers={"X-API-Key": API_KEY},
            json={"title": "Python Session"}
        )
        session = resp.json()
        
        # Send message
        resp = await client.post(
            f"{BASE_URL}/kgent/sessions/{session['id']}/messages",
            headers={"X-API-Key": API_KEY},
            json={"message": "Hello!", "stream": False}
        )
        print(resp.json()["content"])

import asyncio
asyncio.run(main())
```

---

## Next Steps

| Resource | Description |
|----------|-------------|
| [OpenAPI Spec](/openapi.json) | Full API specification |
| [AGENTESE Guide](../spec/protocols/agentese.md) | Deep dive into semantic paths |
| [CLI Reference](cli-reference.md) | Command-line interface |

---

*"There is no view from nowhere. Every observation shapes reality."*
