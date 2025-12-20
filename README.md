# kgents

> *"The noun is a lie. There is only the rate of change."*

Agents are morphisms in a category. They compose. They observe. They become.

This is not another orchestration framework. kgents is a **specification** for agents that have mathematical structure—composition laws that are verified at runtime, not promised in documentation. If your agents don't compose associatively, they're not agents. They're functions with aspirations.

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

Morpheus is the LLM gateway. Without it, composition and tests work but LLM-powered features (K-gent soul, Town dialogue) won't.

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
  services/        # Crown Jewels: Brain, Gardener, Town, Park, Atelier, Morpheus
  protocols/       # AGENTESE runtime, CLI, API gateway
  web/             # React + Three.js frontend
docs/skills/       # THE 13 SKILLS — read before building
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
| Town citizen dialogue | ❌ | ✅ |
| Semantic search | ❌ | ✅ |

---

## Feel It

```python
from agents import agent

@agent
async def parse(s: str) -> int:
    return int(s)

@agent
async def double(x: int) -> int:
    return x * 2

pipe = parse >> double  # Category theory made practical
result = await pipe.invoke("21")  # 42

# Laws are verified, not aspirational
# (f >> g) >> h == f >> (g >> h) ← BootstrapWitness.verify_composition_laws()
```

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
| **Crown Jewel** | Production service (Brain, Town, Park...) built on categorical primitives | [crown-jewel-patterns.md](docs/skills/crown-jewel-patterns.md) |
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

## The Garden

```
Ship-ready     Brain ████████████████████ 100%    Memory cathedral
               Gardener ██████████████████ 100%   Cultivation practice
               Gestalt █████████████████▒ 90%     Living code garden
               Forge ████████████████████ 100%    Creative workshop

Growing        Witness ███████████████▒▒▒ 75%     Trust verification
               Town ██████████████▒▒▒▒▒▒ 70%      Agent simulation
               Park ████████████▒▒▒▒▒▒▒▒ 60%      Westworld hosts
```

11,170+ tests. Strict mypy. Category laws verified at runtime via `BootstrapWitness`.

---

## For AI Agents Working in This Codebase

Read [CLAUDE.md](CLAUDE.md) first. It contains:
- **Anti-Sausage Protocol**: Kent's voice gets diluted through LLM processing. Quote directly; don't paraphrase.
- **Skills-First**: The 13 skills in `docs/skills/` cover every task. Read them before building.
- **DI Silent Skip**: Container silently skips unregistered dependencies. Check `services/providers.py`.
- **Voice Anchors**: *"Daring, bold, creative, opinionated but not gaudy"*, *"Tasteful > feature-complete"*

The Mirror Test: *"Does this feel like Kent on his best day?"*

---

## Explore

| What | Where | When |
|------|-------|------|
| Zero to agent | [docs/quickstart.md](docs/quickstart.md) | First 5 minutes |
| The 13 skills | [docs/skills/](docs/skills/) | Before building anything |
| The seven principles | [spec/principles.md](spec/principles.md) | Understanding why |
| Architecture | [docs/architecture-overview.md](docs/architecture-overview.md) | Understanding how |
| Systems inventory | [docs/systems-reference.md](docs/systems-reference.md) | Before building new |
| Categorical foundations | [docs/categorical-foundations.md](docs/categorical-foundations.md) | The math |

---

MIT License | [Contributing](CONTRIBUTING.md) | [Changelog](CHANGELOG.md)

*"The persona is a garden, not a museum."*
