# Soul API Service

FastAPI-based REST API exposing K-gent Soul capabilities as a service.

## Overview

The Soul API provides two main endpoints:
- **Governance**: Semantic gatekeeper for evaluating operations
- **Dialogue**: Interactive conversation with K-gent Soul

## Installation

FastAPI and uvicorn are required dependencies (already in `pyproject.toml`):

```bash
# Dependencies are already specified
pip install -e .
```

## Quick Start

### Running the Server

```python
from protocols.api.app import run_server

# Development mode (with auto-reload)
run_server(reload=True)
```

Or via command line:

```bash
python -m protocols.api.app
```

The server will start at `http://localhost:8000`.

### API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- OpenAPI JSON: `http://localhost:8000/openapi.json`

## API Endpoints

### Health Check

```bash
GET /health
```

Returns service health status. No authentication required.

**Response:**
```json
{
  "status": "ok",
  "version": "v1",
  "has_llm": true,
  "components": {
    "soul": "ok",
    "llm": "ok",
    "auth": "ok",
    "metering": "ok"
  }
}
```

### Governance Evaluation

```bash
POST /v1/soul/governance
X-API-Key: kg_dev_alice
```

**Request:**
```json
{
  "action": "delete temporary files",
  "context": {
    "environment": "development",
    "reason": "cleanup"
  },
  "budget": "dialogue"
}
```

**Response:**
```json
{
  "approved": true,
  "reasoning": "Operation aligns with minimalism principles - removing unused data.",
  "alternatives": [],
  "confidence": 0.85,
  "tokens_used": 150,
  "recommendation": "approve",
  "principles": ["Aesthetic: Minimalism", "Does this need to exist?"]
}
```

### Dialogue

```bash
POST /v1/soul/dialogue
X-API-Key: kg_dev_alice
```

**Request:**
```json
{
  "prompt": "What patterns am I avoiding?",
  "mode": "reflect",
  "budget": "dialogue"
}
```

**Response:**
```json
{
  "response": "You're avoiding the hard decision by focusing on implementation details.",
  "mode": "reflect",
  "eigenvectors": {
    "aesthetic": 0.9,
    "categorical": 0.8,
    "gratitude": 0.7
  },
  "tokens_used": 250,
  "referenced_preferences": ["Prefer minimal solutions"],
  "referenced_patterns": ["Procrastination through perfectionism"]
}
```

## Authentication

API keys are required for Soul endpoints. Use the `X-API-Key` header.

### Development Keys

For testing, use these pre-registered keys:

| Key | User | Tier | Rate Limit | Token Limit |
|-----|------|------|------------|-------------|
| `kg_dev_alice` | test_free | FREE | 100/day | 10K/month |
| `kg_dev_bob` | test_pro | PRO | 1000/day | 100K/month |
| `kg_dev_carol` | test_enterprise | ENTERPRISE | 10000/day | Unlimited |

### User Tiers

| Tier | Budget Access | Rate Limit | Token Quota |
|------|--------------|------------|-------------|
| FREE | dormant, whisper | 100/day | 10K/month |
| PRO | + dialogue | 1000/day | 100K/month |
| ENTERPRISE | + deep | 10000/day | Unlimited |

## Budget Tiers

| Tier | Tokens | Description |
|------|--------|-------------|
| dormant | 0 | Template responses only |
| whisper | ~100 | Quick acknowledgment |
| dialogue | ~500 | Full conversation |
| deep | ~1000 | Council of Ghosts (ENTERPRISE only) |

## Dialogue Modes

| Mode | Description |
|------|-------------|
| reflect | Explore patterns and behaviors |
| advise | Get guidance on decisions |
| challenge | Have your thinking questioned |
| explore | Open-ended philosophical exploration |

## Usage Metering

The API tracks usage per user:
- Request counts (daily)
- Token usage (daily and monthly)
- Rate limit enforcement
- Endpoint hit statistics

Usage headers are included in responses:
- `X-Response-Time`: Request duration
- `X-RateLimit-Requests-Today`: Requests made today
- `X-Tokens-Today`: Tokens used today
- `X-Tokens-Month`: Tokens used this month

## Example: Using the API

### Python with httpx

```python
import httpx

async def ask_soul(prompt: str) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:8000/v1/soul/dialogue",
            json={
                "prompt": prompt,
                "mode": "reflect",
                "budget": "dialogue",
            },
            headers={"X-API-Key": "kg_dev_bob"},
        )
        return response.json()

# Usage
result = await ask_soul("What am I avoiding?")
print(result["response"])
```

### cURL

```bash
curl -X POST http://localhost:8000/v1/soul/governance \
  -H "X-API-Key: kg_dev_bob" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "delete user_data table",
    "context": {"environment": "staging"}
  }'
```

## Testing

Run the test suite:

```bash
# All tests (requires FastAPI)
pytest protocols/api/_tests/ -v

# Core tests only (no FastAPI required)
pytest protocols/api/_tests/test_models.py protocols/api/_tests/test_metering.py -v
```

Test coverage:
- **38 tests** for core functionality (models, auth logic, metering)
- **66 integration tests** for FastAPI endpoints (requires FastAPI)
- **104 total tests**

## Architecture

```
protocols/api/
├── __init__.py          # Package exports
├── app.py               # FastAPI application factory
├── soul.py              # Soul endpoints
├── auth.py              # API key authentication
├── metering.py          # Usage tracking middleware
├── models.py            # Pydantic request/response models
└── _tests/              # Test suite
    ├── test_app.py      # Application tests
    ├── test_soul.py     # Endpoint tests
    ├── test_auth.py     # Auth tests
    ├── test_metering.py # Metering tests
    └── test_models.py   # Model tests
```

## Production Considerations

For production deployment:

1. **Replace in-memory stores** with Redis/PostgreSQL:
   - `auth._API_KEY_STORE` → Database
   - `metering._USAGE_STORE` → Redis

2. **Secure API keys**:
   - Use secure random generation
   - Store hashed in database
   - Rotate regularly

3. **Configure CORS**:
   - Restrict `allow_origins` to your domains
   - Remove wildcard `*`

4. **Add observability**:
   - Structured logging
   - OpenTelemetry traces
   - Prometheus metrics

5. **Deploy with ASGI server**:
   ```bash
   uvicorn protocols.api.app:app --host 0.0.0.0 --port 8000 --workers 4
   ```

## License

MIT
