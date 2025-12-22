# kgents

> *"The noun is a lie. There is only the rate of change."*

Agents are morphisms in a category. They compose. They observe. They become.

This is not another orchestration framework. kgents is a **specification** for agents that have mathematical structure—composition laws that are verified at runtime, not promised in documentation. If your agents don't compose associatively, they're not agents. They're functions with aspirations.

---

## Feel It

```python
from agents.poly import from_function, sequential

double = from_function("double", lambda x: x * 2)
add_one = from_function("add_one", lambda x: x + 1)

pipe = sequential(double, add_one)
_, outputs = pipe.run(initial=("ready", "ready"), inputs=[5, 10])

# 5 → 11, 10 → 21
# (f >> g) >> h == f >> (g >> h) — Verified, not aspirational
```

---

## Try It: Interactive Demos

Experience kgents through multiple projections—the same concepts, different manifestations.

### Python Examples (2 minutes)

Five standalone scripts, each <50 lines:

```bash
cd impl/claude

# Agent composition and associativity laws
python ../../docs/examples/composition.py

# Operad law verification at runtime
python ../../docs/examples/operad_laws.py

# Trust levels and witness verification
python ../../docs/examples/trust_levels.py

# All examples at once
for f in ../../docs/examples/*.py; do python "$f"; done
```

### Marimo Notebooks (Interactive)

Six interactive notebooks for hands-on exploration:

```bash
cd impl/claude

# The flagship demo: Alethic Architecture
# Same agent → 6 different projections (Local, CLI, Docker, K8s, WASM, marimo)
marimo edit demos/agent_explorer.py

# Forge Crown Jewel: artifact synthesis and composition
marimo edit demos/foundry_showcase.py

# Memory agents: holographic associative memory
marimo edit demos/stateful_memory_demo.py

# Interactive text rendering and projection
marimo edit demos/interactive_text_demo.py

# Reactive substrate visualization
marimo edit demos/red_and_blue.py

# WASM sandbox: zero-trust browser execution
marimo edit demos/wasm_sandbox_demo.py
```

### HTML Sandboxes (Browser, No Build)

Open directly in your browser—no server, no build step:

```bash
cd impl/claude/demos

# Memory agent visualization
open memory_agent_sandbox.html    # macOS
# or: xdg-open memory_agent_sandbox.html  # Linux

# Text transformation playground
open text_transformer_sandbox.html
```

### WASM Demo (Zero-Trust Execution)

Run agents completely sandboxed in your browser via Pyodide:

```bash
cd impl/claude
uv run python demos/wasm_sandbox_demo.py
# Opens in browser. No server required after loading.
```

---

## For Developers: Quick Start

### Requirements

| Component | Required | Notes |
|-----------|----------|-------|
| Python 3.12+ | Yes | Core runtime |
| [uv](https://github.com/astral-sh/uv) | Yes | Package manager (`pip install uv`) |
| Node.js 18+ | Yes | Frontend |
| [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) | For LLM | Morpheus uses `claude -p` subprocess by default |
| Docker | Optional | PostgreSQL for persistence (falls back to SQLite) |

### 1. Clone and Install

```bash
git clone https://github.com/kentgang/kgents.git && cd kgents
uv sync                              # Python dependencies

cd impl/claude/web
npm install                          # Frontend dependencies
```

### 2. Start Backend + Frontend

```bash
# Terminal 1: Backend API
cd impl/claude
uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000

# Terminal 2: Frontend
cd impl/claude/web
npm run dev                          # http://localhost:3000
```

**Verify**: `curl http://localhost:8000/health` should return `{"status":"ok"}`

### 3. LLM Setup (Morpheus Gateway)

Morpheus is the LLM gateway. Without it, composition and tests work but LLM-powered features (K-gent soul, semantic search) won't.

**Option A: Claude CLI (Recommended)**
```bash
# Install Claude CLI: https://docs.anthropic.com/en/docs/claude-code
claude --version                     # Verify installed
claude                               # Authenticate (one-time OAuth)
```
Morpheus auto-detects and routes `claude-*` models via CLI subprocess.

**Option B: Direct API**
```bash
export ANTHROPIC_API_KEY=sk-...      # Or add to .env
# Or: export OPENROUTER_API_KEY=...  # For 100+ models
```

### 4. PostgreSQL (Optional)

Enables persistent storage for Crown Jewels. Without it, falls back to SQLite at `~/.local/share/kgents/`.

```bash
cd impl/claude
docker compose up -d                 # Start Postgres container
source .env                          # Sets KGENTS_POSTGRES_URL
```

### 5. Verify Everything

```bash
cd impl/claude
uv run pytest -q                     # 11,170+ tests (~2 min)
uv run mypy .                        # Strict typing

cd impl/claude/web
npm run typecheck                    # Frontend types (catches real bugs!)
npm run lint
```

### Key Directories

```
spec/              # THE LAW — conceptual specification
impl/claude/       # Reference implementation
  agents/          # Categorical primitives: PolyAgent, Operad, Sheaf, Flux
  services/        # Crown Jewels: Brain, Living Docs, Witness, Foundry
  protocols/       # AGENTESE runtime, CLI, API gateway
  demos/           # Interactive demos (marimo, HTML, WASM)
  web/             # React + Three.js frontend
docs/              # Developer documentation
  skills/          # THE 17 SKILLS — read before building
  examples/        # Standalone Python examples
```

### What Works Without LLM

| Feature | Without LLM | With Morpheus |
|---------|-------------|---------------|
| Agent composition (`>>`) | ✅ | ✅ |
| Category law verification | ✅ | ✅ |
| AGENTESE protocol | ✅ | ✅ |
| Web UI navigation | ✅ | ✅ |
| Brain (memory storage) | ✅ | ✅ |
| K-gent soul dialogue | ❌ | ✅ |
| Semantic search | ❌ | ✅ |

---

## What Makes This Different

**vs. LangChain/LlamaIndex**: Those are orchestration libraries—useful plumbing. kgents is a *specification* with mathematical structure. Agents here satisfy category laws; composition is associative; functors lift behavior uniformly. The difference between "agents that usually work together" and "agents that compose by construction."

**vs. AutoGPT/CrewAI**: Those optimize for autonomy—agents that act without supervision. kgents optimizes for *composability*—agents that can be combined into larger agents without losing guarantees. Autonomy is a capability; composability is a structure.

**vs. DSPy**: Closest in spirit. DSPy treats prompts as programs; kgents treats agents as morphisms. Both are algebraic. DSPy focuses on prompt optimization; kgents focuses on agent composition. They're complementary.

**The core insight**: Traditional agent systems return JSON objects. kgents returns *handles*—morphisms that map Observer → Interaction. The same path yields different results to different observers. *"To observe is to act. There is no view from nowhere."*

---

## The Vocabulary (Dense, Intentionally)

| Term | What It Means | Where to Learn |
|------|---------------|----------------|
| **PolyAgent[S, A, B]** | State machine with mode-dependent inputs. `Agent[A,B]` embeds as `PolyAgent[Unit,A,B]` | [polynomial-agent.md](docs/skills/polynomial-agent.md) |
| **Operad** | Composition grammar—defines *what combinations are valid* | [spec/principles.md](spec/principles.md) §AD-003 |
| **Sheaf** | Gluing local views into global coherence. How emergence works. | [categorical-foundations.md](docs/categorical-foundations.md) |
| **AGENTESE** | Verb-first protocol. Five contexts: `world.*`, `self.*`, `concept.*`, `void.*`, `time.*` | [agentese-path.md](docs/skills/agentese-path.md) |
| **Crown Jewel** | Production service (Brain, Witness, Foundry...) built on categorical primitives | [crown-jewel-patterns.md](docs/skills/crown-jewel-patterns.md) |
| **K-gent** | The governance functor—personality space navigation, not chatbot | [spec/agents/k-gent.md](spec/agents/k-gent.md) |
| **Functor** | Structure-preserving map. `F.lift(a >> b) = F.lift(a) >> F.lift(b)` | [architecture-overview.md](docs/architecture-overview.md) |
| **Accursed Share** | The void context. Entropy budget. *"Everything is slop or comes from slop."* | [spec/principles.md](spec/principles.md) §Meta-Principle |

---

## The Seven Principles (Terse)

1. **Tasteful** — Each agent serves a clear, justified purpose. Say "no" more than "yes."
2. **Curated** — 10 excellent agents beat 100 mediocre ones. No parking lots.
3. **Ethical** — Agents augment humans, never replace judgment. Transparency required.
4. **Joy-Inducing** — Personality encouraged. Warmth over coldness. Humor when appropriate.
5. **Composable** — Agents are morphisms. `(f >> g) >> h = f >> (g >> h)`. Verified, not aspirational.
6. **Heterarchical** — No fixed boss agent. Leadership is contextual. Loop mode AND function mode.
7. **Generative** — Spec is compression. If you can't compress, you don't understand.

Full treatment: [spec/principles.md](spec/principles.md)

---

## Web Galleries

The frontend includes interactive galleries showcasing projection patterns. Start the frontend (see [Quick Start](#2-start-backend--frontend)), then visit:

| Gallery | URL | What It Shows |
|---------|-----|---------------|
| **Projection Gallery** | [localhost:3000/_/gallery](http://localhost:3000/_/gallery) | Polynomial playground, operad wiring, category filtering |
| **Layout Gallery** | [localhost:3000/_/gallery/layout](http://localhost:3000/_/gallery/layout) | 8 pilots demonstrating density isomorphism—same content, different structures (compact ↔ spacious) |
| **Interactive Text** | [localhost:3000/_/gallery/interactive-text](http://localhost:3000/_/gallery/interactive-text) | 6 pilots: AGENTESE portals, task toggles, code regions, badge tokens |

```bash
# Quick start: Backend + Frontend
cd impl/claude && uv run uvicorn protocols.api.app:create_app --factory --reload --port 8000 &
cd impl/claude/web && npm run dev
# Then visit http://localhost:3000/_/gallery
```

---

## For AI Agents Working in This Codebase

Read [CLAUDE.md](CLAUDE.md) first. It contains:
- **Anti-Sausage Protocol**: Kent's voice gets diluted through LLM processing. Quote directly; don't paraphrase.
- **Skills-First**: The 17 skills in `docs/skills/` cover every task. Read them before building.
- **DI Enlightened Resolution**: Required deps fail fast with actionable errors. Optional deps (`= None`) degrade gracefully.
- **Voice Anchors**: *"Daring, bold, creative, opinionated but not gaudy"*, *"Tasteful > feature-complete"*

The Mirror Test: *"Does this feel like Kent on his best day?"*

---

## Explore

| What | Where | When |
|------|-------|------|
| Interactive demos | [impl/claude/demos/](impl/claude/demos/) | First 10 minutes |
| Zero to agent | [docs/quickstart.md](docs/quickstart.md) | First 5 minutes |
| The 17 skills | [docs/skills/](docs/skills/) | Before building anything |
| The seven principles | [spec/principles.md](spec/principles.md) | Understanding why |
| Architecture | [docs/architecture-overview.md](docs/architecture-overview.md) | Understanding how |
| Systems inventory | [docs/systems-reference.md](docs/systems-reference.md) | Before building new |
| Categorical foundations | [docs/categorical-foundations.md](docs/categorical-foundations.md) | The math |

---

MIT License | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)

*"The persona is a garden, not a museum."*
