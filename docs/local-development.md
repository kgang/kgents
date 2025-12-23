---
context: self
---

# Local Development Setup

Complete guide to running kgents locally, including the Crown Jewels web UI and backend API.

## Prerequisites

- **Python 3.12+** with [uv](https://github.com/astral-sh/uv) package manager
- **Node.js 18+** with npm
- **Git**

## Quick Start (TL;DR)

```bash
# Terminal 0: Start Postgres (optional, enables persistence)
cd impl/claude
docker compose up -d
source .env  # Sets KGENTS_POSTGRES_URL

# Terminal 1: Backend
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Frontend
cd impl/claude/web
npm install && npm run dev

# Visit:
#   http://localhost:3000           - Brain (Crown Jewel)
#   http://localhost:3000/_/gallery - Projection Gallery
#   http://localhost:3000/_/interactive-text - Interactive Text Gallery
```

## Detailed Setup

### 1. Clone and Install Dependencies

```bash
git clone https://github.com/yourusername/kgents.git
cd kgents

# Install Python dependencies
uv sync

# Install frontend dependencies
cd impl/claude/web
npm install
```

### 2. PostgreSQL (Optional but Recommended)

PostgreSQL enables persistent storage for Crown Jewels. Without it, data falls back to SQLite.

```bash
cd impl/claude

# Start Postgres container
docker compose up -d

# Load environment variables (sets KGENTS_POSTGRES_URL)
source .env

# Verify Postgres is running
docker compose ps  # Should show postgres "running"
```

**Storage Backends:**
- **With Postgres**: Brain data persists across sessions and is shared
- **Without Postgres**: Falls back to SQLite at `~/.local/share/kgents/brain/brain.db`

Crown Jewels auto-detect and use Postgres when `KGENTS_POSTGRES_URL` is set.

### 3. Backend API

The backend provides REST endpoints for Agent Town, AGENTESE, Crown Jewels, and K-gent Soul.

```bash
cd impl/claude

# Start with auto-reload for development
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000
```

**Key flags:**
- `--factory` - Required because `create_app()` is a factory function
- `--reload` - Auto-restart on code changes
- `--port 8000` - Default port (frontend expects this)

**Verify it's working:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"ok",...}

curl http://localhost:8000/
# Should list all available endpoints
```

### 4. Frontend Web UI

```bash
cd impl/claude/web

# Create environment file
cp .env.example .env

# Start development server
npm run dev
```

Visit `http://localhost:3000`

### 5. Authentication (Development)

The frontend uses Zustand for state management with localStorage persistence. For development, mock a logged-in user via browser console:

```javascript
// Open browser DevTools (F12) → Console tab
// Paste this to log in as CITIZEN tier:

localStorage.setItem('agent-town-user', JSON.stringify({
  state: {
    isAuthenticated: true,
    userId: 'dev-user-001',
    apiKey: 'dev-api-key',
    tier: 'CITIZEN',
    credits: 500,
    monthlyUsage: {}
  },
  version: 0
}));
location.reload();
```

**Available tiers for testing:**
- `TOURIST` - Free tier, limited features
- `RESIDENT` - $9.99/mo, basic INHABIT
- `CITIZEN` - $29.99/mo, full INHABIT + Force
- `FOUNDER` - $99.99/yr, unlimited

To log out:
```javascript
localStorage.removeItem('agent-town-user');
location.reload();
```

## Running Tests

### Backend Tests

```bash
cd impl/claude
uv run pytest protocols/api/_tests/ -v
```

### Frontend Tests

```bash
cd impl/claude/web

# Run once
npm run test -- --run

# Watch mode
npm run test

# With coverage
npm run test:coverage

# With UI
npm run test:ui
```

### Type Checking

```bash
# Backend
cd impl/claude
uv run mypy protocols/api/

# Frontend
cd impl/claude/web
npm run typecheck
```

## API Endpoints

Once the backend is running, these endpoints are available:

### Agent Town

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/town` | Create a new town |
| GET | `/v1/town/{id}` | Get town details |
| GET | `/v1/town/{id}/citizens` | List all citizens |
| GET | `/v1/town/{id}/citizen/{name}` | Get citizen details |
| GET | `/v1/town/{id}/live` | SSE stream of events |
| POST | `/v1/town/{id}/inhabit/{citizen}` | Start INHABIT session |

### K-gent Soul

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/v1/soul/governance` | Semantic gatekeeper |
| POST | `/v1/soul/dialogue` | Interactive dialogue |

### Projection Gallery

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/gallery` | All pilots with projections |
| GET | `/api/gallery?entropy=0.5` | With override |
| GET | `/api/gallery?category=CARDS` | Filter by category |
| GET | `/api/gallery/{name}` | Single pilot |
| GET | `/api/gallery/categories` | Category metadata |

**Web Gallery**: `http://localhost:3000/_/gallery`

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | OpenAPI documentation |

## Environment Variables

### Backend

Set in your shell or `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `ANTHROPIC_API_KEY` | Claude API key for LLM features | - |
| `OPENROUTER_API_KEY` | Alternative LLM provider | - |

### Frontend

Set in `impl/claude/web/.env`:

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend URL | `http://localhost:8000` |
| `VITE_STRIPE_PUBLISHABLE_KEY` | Stripe test mode key | - |

## Common Issues

### Backend won't start: "module object is not callable"

Use the `--factory` flag:
```bash
uv run uvicorn protocols.api.app:create_app --factory --port 8000
```

### Frontend shows "Demo unavailable"

Backend isn't running or town routes aren't registered. Check:
1. Backend is running on port 8000
2. `curl http://localhost:8000/v1/town/test` doesn't return 404

### Port 8000 already in use

```bash
# Find the process
lsof -i :8000

# Kill it
kill -9 <PID>

# Or use a different port
uv run uvicorn protocols.api.app:create_app --factory --port 8001
# Update VITE_API_URL in frontend .env
```

### CORS errors in browser

The backend includes CORS middleware allowing all origins in development. If you still see CORS errors:
1. Ensure backend is running
2. Check the request URL matches `VITE_API_URL`
3. Try hard refresh (Ctrl+Shift+R)

### Tests failing with timing issues

Some async tests may be flaky. Run them individually:
```bash
npm run test -- tests/unit/hooks/useInhabitSession.test.ts --run
```

## Architecture Overview

```
kgents/
├── spec/                    # Specifications (implementation-agnostic)
├── impl/claude/             # Reference implementation
│   ├── agents/              # Agent implementations (A-Z taxonomy)
│   │   ├── k/               # K-gent (Kent simulacra)
│   │   └── town/            # Agent Town simulation
│   ├── protocols/
│   │   ├── api/             # FastAPI REST endpoints
│   │   │   ├── app.py       # Main application factory
│   │   │   ├── town.py      # Town endpoints
│   │   │   └── soul.py      # Soul endpoints
│   │   └── agentese/        # AGENTESE protocol
│   └── web/                 # React frontend
│       ├── src/
│       └── tests/
└── docs/                    # Documentation
```

## Next Steps

- Read [AGENTESE specification](../spec/protocols/agentese.md)
- Check [systems reference](systems-reference.md) for built infrastructure
- Visit the [Projection Gallery](http://localhost:3000/_/gallery) to see all widgets
- Learn the 21 skills in [docs/skills/](skills/)
