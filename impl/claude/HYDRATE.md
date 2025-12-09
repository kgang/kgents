# impl/claude HYDRATE

**Last Updated:** 2025-12-08

## Quick Start

```bash
cd impl/claude
source .venv/bin/activate
python evolve.py status           # Check evolution state
python evolve.py suggest          # Bootstrap-enhanced suggestions
python -m pytest tests/ -v        # Run tests
```

---

## Architecture Overview

```
impl/claude/
├── bootstrap/          # 7 irreducible agents (spec/bootstrap.md)
│   ├── types.py        # Core types: Agent, Result, VerdictType
│   ├── id.py           # Identity morphism
│   ├── compose.py      # f >> g composition
│   ├── ground.py       # Void → Facts (persona, world)
│   ├── contradict.py   # (A,B) → Tension
│   ├── sublate.py      # Tension → Synthesis|Hold
│   ├── judge.py        # Agent → Verdict (7 principles)
│   └── fix.py          # Fixed-point iteration with entropy
│
├── runtime/            # Execution infrastructure
│   ├── base.py         # LLMAgent, AgentContext, Result
│   ├── claude.py       # Anthropic API runtime
│   ├── openrouter.py   # Multi-model runtime
│   └── json_utils.py   # Robust JSON parsing (H5 ✅)
│
├── agents/             # Agent implementations by genus
│   ├── a/              # Abstract (meta-schemas)
│   ├── b/              # Bio/Scientific (robin, hypothesis)
│   ├── c/              # Category (functor, conditional)
│   ├── d/              # Data (volatile, persistent, lens)
│   ├── e/              # Evolution (safety, parser, prompts)
│   ├── f/              # Forge (artifact synthesis)
│   ├── h/              # Hegelian (hegel, jung, lacan)
│   ├── i/              # Interface (garden, renderers, export) ✨NEW
│   ├── j/              # JIT (jgent, chaosmonger, sandbox)
│   ├── k/              # Kent simulacra
│   ├── l/              # Library (catalog, search)
│   ├── t/              # Testing (mock, spy, failing)
│   └── w/              # Wire (observation, fidelity, server) ✨NEW
│
├── evolve.py           # Meta-evolution CLI (1,286 lines)
└── IMPROVEMENT_PLAN.md # Systematic refactoring roadmap
```

---

## Key Files by Purpose

### Bootstrap Agents
| File | Lines | Purpose |
|------|-------|---------|
| `bootstrap/types.py` | 511 | Core Agent protocol, Result types |
| `bootstrap/judge.py` | 420 | Evaluate against 7 principles |
| `bootstrap/contradict.py` | 360 | Detect contradictions |
| `bootstrap/sublate.py` | 337 | Hegelian synthesis |
| `bootstrap/fix.py` | 303 | Convergence iteration |

### Evolution Pipeline
| File | Lines | Purpose |
|------|-------|---------|
| `evolve.py` | 1,286 | CLI + EvolutionPipeline orchestration |
| `agents/e/safety.py` | 656 | Safe self-evolution with rollback |
| `agents/e/parser.py` | 687 | Multi-strategy code extraction |
| `agents/e/prompts.py` | 762 | Improvement prompt templates |

### JIT Compilation
| File | Lines | Purpose |
|------|-------|---------|
| `agents/j/jgent.py` | 450 | JIT agent compilation |
| `agents/j/sandbox.py` | 460 | Secure code execution |
| `agents/j/chaosmonger.py` | 620 | Stability analysis |
| `agents/j/meta_architect.py` | 607 | Agent generation |

### I-gents (Interface)
| File | Lines | Purpose |
|------|-------|---------|
| `agents/i/types.py` | 250 | Phase, Glyph, Scale, AgentState, GardenState |
| `agents/i/renderers.py` | 350 | ASCII renderers (Card, Page, Garden, Library) |
| `agents/i/export.py` | 200 | Markdown/Mermaid serialization |
| `agents/i/breath.py` | 120 | Contemplative breath cycle animation |
| `agents/i/observe.py` | 200 | W-gent integration ([observe] action) |

### W-gents (Wire)
| File | Lines | Purpose |
|------|-------|---------|
| `agents/w/protocol.py` | 300 | WireObservable mixin, WireState, WireEvent |
| `agents/w/fidelity.py` | 400 | Teletype, Documentarian, LiveWire adapters |
| `agents/w/server.py` | 200 | FastAPI server with SSE for live observation |

---

## Bootstrap Self-Improvement Patterns

The bootstrap agents enable **direct self-improvement** without external coordination:

### 1. Judge → Quality Gate
```python
from bootstrap import Judge, JudgeInput
verdict = await Judge().invoke(JudgeInput(agent=any_agent))
# Returns: ACCEPT | REVISE | REJECT with reasoning
```

### 2. Contradict + Sublate → Conflict Resolution
```python
from agents.h.hegel import HegelAgent
result = await HegelAgent().invoke(DialecticInput(thesis=old, antithesis=new))
# Returns: Synthesis or productive tension to hold
```

### 3. Fix → Convergence Iteration
```python
from bootstrap import Fix, FixConfig
fix = Fix(FixConfig(max_iterations=10, entropy_budget=1.0))
result = await fix.invoke((improve_fn, initial_state))
```

### 4. Ground → Context Injection
```python
from bootstrap import Ground, VOID
facts = await Ground().invoke(VOID)
# facts.persona: Kent's values | facts.world: current context
```

### 5. I-gent → Ecosystem Visualization
```python
from agents.i import Phase, AgentState, GardenRenderer, BreathCycle

state = AgentState(agent_id="robin", phase=Phase.ACTIVE, birth_time=datetime.now())
state.joy = 0.9
state.ethics = 0.85

garden = GardenState(name="research", session_start=datetime.now())
garden.add_agent(state)
print(GardenRenderer(garden).render())
# ASCII zen garden with moon phase glyphs
```

### 6. W-gent → Process Observation
```python
from agents.w import WireObservable, WireServer

class MyAgent(WireObservable):
    def __init__(self):
        super().__init__("my-agent")

    async def run(self):
        self.update_state(phase="active", progress=0.5)
        self.log_event("INFO", "work", "Processing...")

# Start observation server (opens browser at localhost:8000)
server = WireServer("my-agent", port=8000)
await server.start()
```

---

## Recent Commits

| Commit | Description |
|--------|-------------|
| `4b02086` | feat(i-gents): Living Codex Garden spec |
| `294b068` | fix(evolve): Expand builtins in preflight |
| `ea7c2a5` | feat(cross-poll): Phase C validation |
| `4d883d2` | refactor(impl): Evolution bug fixes |
| `0001386` | feat(f-gents): Sandbox with self-healing |

---

## Improvement Plan Status

See `IMPROVEMENT_PLAN.md` for full details.

### Completed
- [x] **H5**: JSON utilities → `runtime/json_utils.py`
- [x] Bootstrap integration in `evolve.py` (Judge, Fix, Contradict, Ground)

### Phase A: Quick Wins
- [ ] **H4**: Lazy imports in `evolve.py` (57 imports)
- [ ] **H2**: Extract SuggestionAgent (56 lines)

### Phase B: Core Refactoring
- [ ] **H1**: Decompose EvolutionPipeline (19 methods → 4 agents)
- [ ] **H7**: Split `prompts.py` (762 lines)
- [ ] **H10**: Split `sandbox.py` (460 lines)

### Key Targets
| Metric | Current | Target |
|--------|---------|--------|
| Files >500 lines | 18 | 10 |
| Functions >50 lines | 45+ | <20 |
| evolve.py lines | 1,286 | <800 |

---

## Testing

```bash
# Unit tests
python -m pytest tests/ -v

# Type checking
mypy --strict evolve.py

# Evolution self-test
python evolve.py test

# Safe meta-evolution (dry run)
python evolve.py meta --safe-mode --dry-run
```

---

## Spec ↔ Impl Mapping

| Spec | Impl |
|------|------|
| `spec/bootstrap.md` | `bootstrap/` |
| `spec/a-gents/` | `agents/a/` |
| `spec/b-gents/` | `agents/b/` (robin, hypothesis) |
| `spec/c-gents/` | `agents/c/` (functor, conditional) |
| `spec/d-gents/` | `agents/d/` (volatile, persistent) |
| `spec/e-gents/` | `agents/e/` + `evolve.py` |
| `spec/f-gents/` | `agents/f/` (forge, artifacts) |
| `spec/h-gents/` | `agents/h/` (hegel, jung, lacan) |
| `spec/i-gents/` | `agents/i/` (types, renderers, export, observe) ✨NEW |
| `spec/j-gents/` | `agents/j/` (jgent, sandbox) |
| `spec/k-gent/` | `agents/k/` |
| `spec/l-gents/` | `agents/l/` (catalog, search) |
| `spec/t-gents/` | `agents/t/` (mock, spy, failing) |
| `spec/w-gents/` | `agents/w/` (protocol, fidelity, server) ✨NEW |
