# Getting Started with kgents

A practical guide for human developers who want to run, understand, and contribute to kgents.

---

## I Just Want to See It Run (5 minutes)

### Prerequisites

- **Python 3.12+** - Check with `python --version`
- **Node.js 18+** - Check with `node --version`
- **[uv](https://github.com/astral-sh/uv)** - Modern Python package manager
- **Docker** (optional) - For persistent PostgreSQL storage

### Quick Start

```bash
# 1. Clone and install
git clone https://github.com/kentgang/kgents.git
cd kgents
uv sync

# 2. Start the dev server
cd impl/claude
uv run kg dev
```

That's it. Open your browser to:
- **http://localhost:3000** - The Hypergraph Editor (main UI)
- **http://localhost:8000/docs** - API documentation (Swagger UI)
- **http://localhost:8000/health** - Health check

### What You Should See

The frontend opens to the **Hypergraph Editor** - a document-centric workspace where you can:
- Navigate documents and K-Blocks in the left sidebar
- Edit content in a six-mode editing system (like vim for graphs)
- Chat with K-gent in the right sidebar
- See witness marks (decision traces) in the footer

The backend provides a REST API with 50+ endpoints. Hit `/` to see all available routes.

### Without Docker (SQLite fallback)

If you skip Docker, kgents uses SQLite at `~/.local/share/kgents/membrane.db`. This works fine for development but data won't persist across different machines.

### With Docker (Persistent PostgreSQL)

```bash
cd impl/claude
docker compose up -d          # Start Postgres container
source .env                   # Load environment variables
uv run kg dev                 # Now uses PostgreSQL
```

Verify with: `curl http://localhost:8000/health` - should show `"status": "ok"`.

---

## I Want to Understand the Architecture (30 minutes)

### The Metaphysical Fullstack (7 Layers)

kgents uses a layered architecture where each layer has a specific purpose:

```
Layer 7: PROJECTION SURFACES  - CLI, TUI, Web, JSON, SSE
         (How users see things)

Layer 6: AGENTESE PROTOCOL    - logos.invoke(path, observer, **kwargs)
         (The universal API - there's only one way to call anything)

Layer 5: AGENTESE NODE        - @node decorator, aspects, effects
         (How services expose themselves)

Layer 4: SERVICE MODULE       - services/<name>/ - The "Crown Jewels"
         (Where business logic lives)

Layer 3: OPERAD GRAMMAR       - Composition laws, valid operations
         (Rules for combining agents)

Layer 2: POLYNOMIAL AGENT     - PolyAgent[S, A, B]: state x input -> output
         (The mathematical foundation for state machines)

Layer 1: SHEAF COHERENCE      - Local views -> global consistency
         (How distributed state stays consistent)

Layer 0: PERSISTENCE          - StorageProvider: PostgreSQL/SQLite
         (Where data lives)
```

**Key insight**: There are no traditional REST routes defined manually. The AGENTESE gateway auto-exposes all `@node` decorated services at `/agentese/{path}`.

### Where Code Lives

```
kgents/
├── spec/                    # Specifications (the "what")
│   ├── principles.md        # The 7 guiding principles
│   └── protocols/           # Protocol specifications
│
├── impl/claude/             # Reference implementation (the "how")
│   ├── agents/              # Agent implementations (A-Z taxonomy)
│   │   ├── k/               # K-gent (Kent simulacra, the soul)
│   │   ├── town/            # Agent Town (citizen simulation)
│   │   ├── poly/            # PolyAgent (state machine foundation)
│   │   └── ...              # Each letter is a different agent genus
│   │
│   ├── services/            # Crown Jewel services (business logic)
│   │   ├── brain/           # Holographic memory
│   │   ├── witness/         # Decision traces and marks
│   │   ├── zero_seed/       # Epistemic graph and axioms
│   │   └── ...              # 50+ services
│   │
│   ├── protocols/
│   │   ├── api/             # FastAPI REST endpoints
│   │   ├── agentese/        # AGENTESE protocol implementation
│   │   └── cli/             # CLI handlers (kg command)
│   │
│   └── web/                 # React frontend
│       ├── src/
│       │   ├── hypergraph/  # Main editor components
│       │   ├── components/  # Shared UI components
│       │   └── hooks/       # React hooks
│       └── tests/
│
└── docs/
    ├── skills/              # How-to guides (24 skills)
    └── theory/              # Mathematical foundations (21 chapters)
```

### How AGENTESE Paths Work

AGENTESE is the universal API. Instead of `/api/brain/capture`, you call `/agentese/self/memory/capture`.

**Five contexts** organize all paths:

| Context | Scope | Examples |
|---------|-------|----------|
| `world.*` | External things | `world.town`, `world.document`, `world.morpheus` |
| `self.*` | Internal state | `self.memory`, `self.soul`, `self.kgent` |
| `concept.*` | Abstract ideas | `concept.gardener`, `concept.summary` |
| `void.*` | Entropy/exploration | `void.sip`, `void.tithe` |
| `time.*` | Temporal operations | `time.trace`, `time.forecast` |

A path like `self.memory.capture` means:
- **Context**: `self` (internal)
- **Holon**: `memory` (the Brain service)
- **Aspect**: `capture` (save something to memory)

To invoke it:
```bash
# Via CLI
kg brain capture "My first memory"

# Via HTTP
curl -X POST http://localhost:8000/agentese/self/memory/capture \
  -H "Content-Type: application/json" \
  -d '{"content": "My first memory"}'
```

### The Crown Jewels (Key Services)

| Service | Path | What It Does |
|---------|------|--------------|
| **Brain** | `self.memory.*` | Holographic memory - captures, searches, connects ideas |
| **Witness** | `self.witness.*` | Decision traces - marks, fusions, dialectic records |
| **Zero Seed** | `concept.zero_seed.*` | Epistemic graph - axioms, proofs, derivations |
| **K-gent** | `self.kgent.*` | The soul - Kent's AI simulacra for conversation |
| **Director** | `world.director.*` | Document lifecycle - specs, evidence, prompts |
| **Chat** | `self.chat.*` | Session management with branching/forking |

---

## I Want to Add a Feature (1 hour)

### Adding a Backend Endpoint

**Step 1**: Create a service in `impl/claude/services/myfeature/`

```python
# impl/claude/services/myfeature/__init__.py
from .service import MyFeatureService

__all__ = ["MyFeatureService"]
```

```python
# impl/claude/services/myfeature/service.py
class MyFeatureService:
    async def do_something(self, input_data: str) -> dict:
        return {"result": f"Processed: {input_data}"}
```

**Step 2**: Create an AGENTESE node

```python
# impl/claude/services/myfeature/node.py
from protocols.agentese.node import node

@node(
    path="world.myfeature",
    aspects=["do_something"],
    description="My new feature"
)
class MyFeatureNode:
    def __init__(self):
        self.service = MyFeatureService()

    async def do_something(self, input_data: str) -> dict:
        """Do something with input."""
        return await self.service.do_something(input_data)
```

**Step 3**: Register the node module

Edit `impl/claude/protocols/agentese/gateway.py` and add your module to `_import_node_modules()`:

```python
def _import_node_modules() -> None:
    # ... existing imports ...
    import services.myfeature.node  # Add this line
```

**Step 4**: Test it

```bash
# Start the server
cd impl/claude && uv run kg dev

# Call your endpoint
curl -X POST http://localhost:8000/agentese/world/myfeature/do_something \
  -H "Content-Type: application/json" \
  -d '{"input_data": "hello"}'
```

### Adding a React Component

**Step 1**: Create the component

```tsx
// impl/claude/web/src/components/MyComponent.tsx
import { useState } from 'react';

interface MyComponentProps {
  initialValue?: string;
}

export function MyComponent({ initialValue = '' }: MyComponentProps) {
  const [value, setValue] = useState(initialValue);

  return (
    <div className="p-4 border rounded">
      <input
        value={value}
        onChange={(e) => setValue(e.target.value)}
        className="border p-2"
      />
      <p>Current: {value}</p>
    </div>
  );
}
```

**Step 2**: Add a route (if it's a page)

Edit `impl/claude/web/src/router/index.tsx`:

```tsx
// Add your route
{
  path: '/my-page',
  element: <MyPage />,
},
```

**Step 3**: Use the API

```tsx
// impl/claude/web/src/hooks/useMyFeature.ts
import { useState } from 'react';

export function useMyFeature() {
  const [loading, setLoading] = useState(false);

  const doSomething = async (input: string) => {
    setLoading(true);
    try {
      const res = await fetch('/agentese/world/myfeature/do_something', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ input_data: input }),
      });
      return await res.json();
    } finally {
      setLoading(false);
    }
  };

  return { doSomething, loading };
}
```

### Running Tests Before Committing

```bash
cd impl/claude

# Backend tests (runs ~11,000 tests)
uv run pytest -q

# Type checking
uv run mypy .

# Frontend tests
cd web
npm run test:run

# Frontend type checking (IMPORTANT - catches silent errors)
npm run typecheck

# Frontend linting
npm run lint
```

**Pro tip**: Always run `npm run typecheck` after changing TypeScript. Type mismatches cause blank pages with no error messages.

---

## I Want to Understand the Theory (Weekend Project)

### You Don't Need to Know Category Theory

Seriously. The implementation works without understanding the math. The theory explains *why* things are structured the way they are, but you can build features without it.

That said, if you're curious...

### The 7 Principles (Explained Simply)

1. **Tasteful** - Every agent must justify its existence. No feature creep.
2. **Curated** - Quality over quantity. Remove what doesn't serve.
3. **Ethical** - Agents augment humans, never replace judgment. No deception.
4. **Joy-Inducing** - Interactions should feel good. Personality is welcome.
5. **Composable** - Agents are building blocks that combine: `A >> B >> C`
6. **Heterarchical** - No fixed hierarchy. Leadership is contextual.
7. **Generative** - Small primitives + composition rules = infinite valid agents

### Recommended Reading Order

**Start here** (30 min):
1. `docs/theory/00-overture.md` - Why this theory exists
2. `docs/theory/README.md` - Map of all chapters

**Core concepts** (2-3 hours):
3. `docs/theory/02-agent-category.md` - Agents as composable morphisms
4. `docs/theory/08-polynomial-bootstrap.md` - How state machines work
5. `docs/theory/16-witness.md` - Decision traces

**Deep dives** (if you want more):
- Category theorists: Chapters 3-5 (Monads, Operads, Sheaves)
- Optimization folks: Chapters 9-11 (Dynamic Programming)
- Systems engineers: Chapters 12-14 (Multi-agent, Heterarchy)

### The One Equation to Know

```
Agent = PolyAgent[S, A, B]

Where:
  S = state space (what modes the agent can be in)
  A = input type per state (what it accepts in each mode)
  B = output type (what it produces)
```

This is a polynomial functor: `P(X) = sum over s in S of X^{A_s} * B_s`. It means an agent's behavior depends on its current state.

---

## Common Tasks Cheatsheet

| Task | Command |
|------|---------|
| Start dev server | `cd impl/claude && uv run kg dev` |
| Start backend only | `uv run kg dev --backend` |
| Start frontend only | `uv run kg dev --frontend` |
| Run all tests | `uv run pytest -q` |
| Run specific test | `uv run pytest path/to/test.py -v` |
| Type check backend | `uv run mypy .` |
| Type check frontend | `cd web && npm run typecheck` |
| Lint frontend | `cd web && npm run lint` |
| Format frontend | `cd web && npm run format` |
| Start Postgres | `docker compose up -d` |
| Stop Postgres | `docker compose down` |
| Delete Postgres data | `docker compose down -v` |
| Check health | `curl http://localhost:8000/health` |
| Interactive REPL | `uv run kg -i` |
| Query AGENTESE paths | `uv run kg q 'self.*'` |

---

## Troubleshooting

### "ServiceRegistry not initialized"

The backend's dependency injection system wasn't started.

**Fix**: Make sure you're using the app factory:
```bash
uv run uvicorn protocols.api.app:create_app --factory --port 8000
```

Or just use `uv run kg dev` which handles this automatically.

### Database connection fails

**Symptom**: Errors about PostgreSQL connection or missing database

**Fix 1**: Start Docker
```bash
cd impl/claude
docker compose up -d
source .env  # Load KGENTS_DATABASE_URL
```

**Fix 2**: Use SQLite (no Docker needed)
```bash
unset KGENTS_DATABASE_URL  # Remove Postgres config
uv run kg dev              # Falls back to SQLite
```

### Frontend shows blank page

**Symptom**: White screen, no errors visible

**Likely causes**:
1. TypeScript error not caught at compile time
2. Missing API response handling
3. Uninitialized state

**Fix**:
```bash
cd impl/claude/web
npm run typecheck   # Find type errors
npm run lint        # Find code issues
```

Check browser DevTools (F12) Console tab for runtime errors.

### "module object is not callable"

**Fix**: Use `--factory` flag:
```bash
uv run uvicorn protocols.api.app:create_app --factory --port 8000
```

### Port 8000 already in use

```bash
# Find what's using it
lsof -i :8000

# Kill it
kill -9 <PID>
```

### Tests failing with Python version

**Symptom**: Cryptic test failures

**Fix**: Verify Python 3.12+
```bash
python --version  # Should be 3.12 or higher
```

### CORS errors in browser

**Symptom**: "Access-Control-Allow-Origin" errors

**Fix**: Backend handles CORS automatically in dev. Try:
1. Hard refresh (Ctrl+Shift+R)
2. Verify backend is running on port 8000
3. Check `VITE_API_URL` in `web/.env` matches backend

### DI dependency not found

**Symptom**: `DependencyNotFoundError: 'foo' not registered`

**Fix**: Add the provider to `services/providers.py`:
```python
async def get_foo() -> Foo:
    return Foo()

# Register in setup_providers()
container.register("foo", get_foo, singleton=True)
```

---

## Getting Help

- **Skills docs**: `docs/skills/` - 24 practical how-to guides
- **Theory docs**: `docs/theory/` - Mathematical foundations
- **CLAUDE.md**: Instructions for AI assistants (useful for understanding conventions)
- **Systems reference**: `docs/systems-reference.md` - Inventory of all built infrastructure

---

*Last updated: 2025-01*
