# Technology Stack

## Build System & Package Management

- **Python**: 3.12+ (strict requirement)
- **Package Manager**: `uv` (fast Python package installer and resolver)
- **Build Backend**: Hatchling
- **Monorepo Structure**: Workspace with `impl/claude/` as main implementation

## Backend Stack

### Core Dependencies
- **FastAPI**: Web framework and API server
- **SQLAlchemy 2.0**: Async ORM with PostgreSQL (asyncpg) and SQLite (aiosqlite) support
- **Anthropic**: Claude LLM integration
- **Textual**: Terminal UI framework
- **Pydantic**: Data validation and serialization
- **OpenTelemetry**: Observability and tracing

### Agent Framework
- **Category Theory**: Custom implementation of functors, operads, sheaves
- **Polynomial Agents**: State machines with mode-dependent inputs (`PolyAgent[S, A, B]`)
- **AGENTESE**: Observer-dependent protocol across 5 contexts (world, self, concept, void, time)
- **17 Atomic Primitives**: Bootstrap agents (ID, GROUND, JUDGE, etc.) from which all others compose
- **Bootstrap Agents**: 7 irreducible agents that can regenerate the entire system

### Infrastructure
- **Kubernetes**: Optional deployment target (graceful degradation to subprocess)
- **Redis**: Stigmergy (pheromone store) for agent coordination
- **Alembic**: Database migrations

## Frontend Stack

### Core Framework
- **React 18**: UI framework with hooks
- **TypeScript**: Strict type checking
- **Vite**: Build tool and dev server
- **React Router**: Client-side routing

### UI Libraries
- **Radix UI**: Headless component primitives
- **Tailwind CSS**: Utility-first styling
- **Framer Motion**: Animation library
- **Lucide React**: Icon library
- **PIXI.js**: WebGL rendering for visualizations

### State Management
- **Zustand**: Lightweight state management
- **Immer**: Immutable state updates

## Development Tools

### Code Quality
- **Ruff**: Python linting and formatting (replaces Black, isort, flake8)
- **mypy**: Static type checking (strict mode)
- **ESLint**: JavaScript/TypeScript linting
- **Prettier**: Code formatting

### Testing
- **pytest**: Python testing framework with async support
- **pytest-xdist**: Parallel test execution
- **Hypothesis**: Property-based testing
- **Vitest**: Frontend unit testing
- **Playwright**: E2E testing
- **Testing Library**: React component testing

### Documentation
- **MkDocs**: Documentation site generator
- **Material for MkDocs**: Documentation theme

## Architecture Patterns

### Metaphysical Fullstack (AD-009)
Every agent is a vertical slice from persistence to projection:
- **Service modules** (`services/`) own business logic, adapters, and frontend components
- **AGENTESE nodes** (`@node` decorator) provide universal protocol access
- **Main website** is a shallow container functor importing from services

### Registry as Truth (AD-011)
- `@node` decorator is single source of truth for all paths
- Frontend, CLI, and API derive from registry
- No hardcoded paths or aliases

### Graceful Degradation
- K8s deployment with subprocess fallback
- PostgreSQL with SQLite fallback
- Rich UI with auto-generated fallback

### Generative Over Enumerative (AD-003)
- Define operads (composition grammar) that generate valid compositions
- Don't enumerate instances - generate from grammar
- CLI commands, tests, docs all derived from operads

### Pre-Computed Richness (AD-004)
- Demo data uses pre-computed LLM outputs, not synthetic stubs
- Hotload fixtures for development velocity
- One LLM call to generate, infinite reuse

## Common Commands

### Backend Development
```bash
# Setup
cd impl/claude
uv sync

# Development
uv run kg --help                    # CLI interface
uv run uvicorn protocols.api.app:create_app --factory --port 8000  # API server

# Testing
uv run pytest -m "not slow" -q     # Quick tests (~2 min)
uv run pytest                      # Full test suite
uv run pytest -n 5                 # Parallel execution

# Code Quality
uv run ruff format .               # Format code
uv run ruff check .                # Lint code
uv run mypy .                      # Type check

# Validation (what CI runs)
./scripts/validate.sh              # All checks
./scripts/validate.sh --quick      # Lint + types only
```

### Frontend Development
```bash
cd impl/claude/web

# Setup
npm install

# Development
npm run dev                        # Dev server (port 3000)
npm run build                      # Production build

# Testing
npm run test                       # Unit tests
npm run test:e2e                   # E2E tests
npm run typecheck                  # Type checking

# Code Quality
npm run lint                       # ESLint
npm run format                     # Prettier
npm run validate                   # All checks
```

### Full Stack
```bash
# Root level commands
uv sync                            # Install all dependencies
kg --help                          # CLI interface

# Documentation
mkdocs serve                       # Local docs server
mkdocs build                       # Build docs

# AGENTESE Protocol
kg self.soul.challenge             # Direct AGENTESE path
kg /soul                           # Shortcut
kg ?world.*                        # Query paths
kg subscribe self.memory.*         # Subscribe to events
```

## File Structure Conventions

```
impl/claude/
├── agents/           # Categorical primitives (PolyAgent, Operad, Sheaf)
├── services/         # Crown Jewels (Brain, Town, etc.) with co-located frontend
├── protocols/        # AGENTESE, CLI, API protocols
├── models/           # SQLAlchemy ORM definitions
├── bootstrap/        # Core 7 bootstrap agents
├── runtime/          # LLM clients and execution
├── shared/           # Budget, costs, utilities
└── web/             # Main website (container functor)
```

## Environment Setup

### Required
- Python 3.12+
- Node.js 18+ (for frontend)
- `uv` package manager

### Optional
- PostgreSQL (falls back to SQLite)
- Redis (for stigmergy)
- Kubernetes cluster (falls back to subprocess)

### Environment Variables
- `ANTHROPIC_API_KEY`: Claude API access
- `DATABASE_URL`: PostgreSQL connection (optional)
- `REDIS_URL`: Redis connection (optional)