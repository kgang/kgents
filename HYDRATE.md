# HYDRATE.md - Session Context

## TL;DR

**kgents** = Kent's Agents. Spec-first agent framework with 7 irreducible bootstrap agents.

- `spec/` = Language spec (like Python)
- `impl/claude-openrouter/` = Reference impl (like CPython)

## Current State (Dec 2025)

| Component | Status |
|-----------|--------|
| 7 Principles | ✅ Defined in `spec/principles.md` |
| 7 Bootstrap Agents | ✅ Spec (`spec/bootstrap.md`) + Impl (`impl/claude-openrouter/bootstrap/`) |
| zen-agents | ✅ Textual TUI using bootstrap patterns (`impl/zen-agents/`) |
| C-gents (Category Theory) | ✅ `impl/claude-openrouter/agents/c/` |
| H-gents (Hegel/Jung/Lacan) | ✅ `impl/claude-openrouter/agents/h/` |
| 3 Agent Genera (A,B,K) | ⏳ Spec exists, impl pending |
| runtime/ | ⏳ Pending (LLM-backed agents) |

## 7 Bootstrap Agents (Implemented)

| Agent | Type | File |
|-------|------|------|
| **Id** | `A → A` | `id.py` |
| **Compose** | `(Agent, Agent) → Agent` | `compose.py` |
| **Judge** | `(Agent, Principles) → Verdict` | `judge.py` |
| **Ground** | `Void → Facts` | `ground.py` |
| **Contradict** | `(A, B) → Tension \| None` | `contradict.py` |
| **Sublate** | `Tension → Synthesis \| Hold` | `sublate.py` |
| **Fix** | `(A → A) → A` | `fix.py` |

## Directory Map

```
kgents/
├── spec/                    # THE SPECIFICATION
│   ├── principles.md        # 7 core principles
│   ├── bootstrap.md         # 7 irreducible agents
│   └── {a,b,c,h,k}-gents/   # 5 agent genera
├── impl/claude-openrouter/  # Reference implementation
│   ├── bootstrap/           # ✅ 7 bootstrap agents (Python)
│   ├── agents/c/            # ✅ Category theory (Maybe, Either, Parallel, Conditional)
│   ├── agents/h/            # ✅ Dialectics (Hegel, Jung, Lacan)
│   ├── agents/{a,b,k}/      # ⏳ Pending
│   └── runtime/             # ⏳ Pending
└── impl/zen-agents/         # ✅ Textual TUI (bootstrap demonstration)
    └── zen_agents/          # Package directory
        ├── agents/          # Fix, Contradict, Sublate, Ground, Judge patterns
        ├── services/        # tmux, session_manager, state_refresher
        ├── screens/         # TUI screens
        ├── widgets/         # TUI widgets
        └── app.py           # Entry point
```

## Key Applied Idioms

From `spec/bootstrap.md`:

1. **Polling is Fix** — `RetryFix`, `ConvergeFix` variants
2. **Conflict is Data** — `NameCollisionChecker`, `ConfigConflictChecker`
3. **Compose, Don't Concatenate** — `>>` operator for pipelines

## C-gents (Implemented)

Category theory patterns for agent composition:

| Pattern | Purpose | Usage |
|---------|---------|-------|
| `Maybe`, `Just`, `Nothing` | Optional values | `maybe(agent)` lifts to Maybe |
| `Either`, `Right`, `Left` | Error handling | `either(agent)` lifts to Either |
| `parallel(*agents)` | Concurrent execution | Returns `list[B]` |
| `fan_out(*agents)` | Fan-out to tuple | Returns `tuple` of results |
| `race(*agents)` | First to complete wins | Returns single `B` |
| `branch(pred, if_true, if_false)` | Conditional | Routes by predicate |
| `switch(key_fn, cases, default)` | Multi-way switch | Routes by key |

## H-gents (Implemented)

Dialectic introspection agents (system-facing, not user-therapeutic):

| Agent | Purpose | Key Type |
|-------|---------|----------|
| `HegelAgent` | Thesis + antithesis → synthesis | `DialecticInput → DialecticOutput` |
| `JungAgent` | Shadow integration | `JungInput → JungOutput` |
| `LacanAgent` | Real/Symbolic/Imaginary triangulation | `LacanInput → LacanOutput` |

Quick versions: `quick_shadow(self_image)`, `quick_register(text)`

## Next Steps

1. **Run zen-agents** - `cd impl/zen-agents && python3.11 -m venv .venv && source .venv/bin/activate && pip install -e . && zen-agents`
2. Implement `agents/{a,b,k}/` genera from specs
3. Build `runtime/` for LLM-backed agent execution

## Recent Fixes

- **Attach session** (Dec 2025): Implemented `action_attach` in `screens/main.py` to use Textual's `app.suspend()` context manager, which suspends the TUI and runs `tmux attach-session` in the foreground. Press `a` or click the Attach button.

## Quick Start

```python
# Bootstrap agents
from impl.claude_openrouter.bootstrap import (
    Id, Compose, Judge, Ground, Contradict, Sublate, Fix, fix
)

# C-gents: Category theory composition
from impl.claude_openrouter.agents.c import (
    Maybe, Just, Nothing, maybe, either,
    parallel, fan_out, race, branch, switch
)

# H-gents: Dialectic introspection
from impl.claude_openrouter.agents.h import (
    hegel, jung, lacan,
    DialecticInput, JungInput, LacanInput
)

# Build pipelines
pipeline = validate >> transform >> persist

# Parallel execution
results = await parallel(agent1, agent2, agent3).invoke(input)

# Dialectic synthesis
synthesis = await hegel().invoke(DialecticInput(
    thesis="prioritize readability",
    antithesis="prioritize performance"
))

# Shadow analysis
shadow = await jung().invoke(JungInput(
    system_self_image="helpful, accurate, safe assistant"
))
```
