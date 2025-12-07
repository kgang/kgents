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
| K-gent (Persona) | ✅ `impl/claude-openrouter/agents/k/` |
| A-gents, B-gents | ⏳ Spec exists, impl pending |
| runtime/ | ✅ `impl/claude-openrouter/runtime/` (ClaudeRuntime, OpenRouterRuntime) |

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
├── impl/claude-openrouter/  # Reference implementation (kgents-runtime package)
│   ├── bootstrap/           # ✅ 7 bootstrap agents (Python)
│   ├── agents/c/            # ✅ Category theory (Maybe, Either, Parallel, Conditional)
│   ├── agents/h/            # ✅ Dialectics (Hegel, Jung, Lacan)
│   ├── agents/k/            # ✅ K-gent persona (Dialogue, Query, Evolution)
│   ├── agents/{a,b}/        # ⏳ Pending
│   └── runtime/             # ✅ LLM execution (ClaudeRuntime, OpenRouterRuntime)
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

## K-gent (Implemented)

The personalizer - Ground projected through persona_schema:

| Agent | Purpose | Key Type |
|-------|---------|----------|
| `KgentAgent` | Dialogue with 4 modes | `DialogueInput → DialogueOutput` |
| `PersonaQueryAgent` | Query preferences | `PersonaQuery → PersonaResponse` |
| `EvolutionAgent` | Persona evolution | `EvolutionInput → EvolutionOutput` |

Dialogue modes: `REFLECT`, `ADVISE`, `CHALLENGE`, `EXPLORE`

## Runtime (Implemented)

LLM execution layer for agents:

| Class | Purpose | Usage |
|-------|---------|-------|
| `LLMAgent[A, B]` | Base for LLM-backed agents | Extend, implement `build_prompt` + `parse_response` |
| `ClaudeRuntime` | Execute via Anthropic API | `await runtime.execute(agent, input)` |
| `OpenRouterRuntime` | Execute via OpenRouter | Same API, different provider |

## Next Steps

**Bootstrap in progress** — see `BOOTSTRAP_PLAN.md`

Phase 1: K-gent (personalizer) ✅ DONE
Phase 2: A-gents (abstractors) ← CURRENT
Phase 3: B-gents (discoverers)

## Recent Changes

- **K-gent implemented** (Dec 2025): `impl/claude-openrouter/agents/k/` - persona, query, evolution agents
- **Runtime added** (Dec 2025): `impl/claude-openrouter/runtime/` with `ClaudeRuntime` and `OpenRouterRuntime` for LLM-backed agent execution
- **Clean imports** (Dec 2025): zen-agents now imports from `bootstrap` cleanly (no more sys.path hacks)
- **Attach session** (Dec 2025): `action_attach` in `screens/main.py` uses Textual's `app.suspend()` for tmux attach

## Quick Start

```python
# Bootstrap agents
from bootstrap import (
    Agent, Id, compose, Judge, Ground, Contradict, Sublate, Fix, fix
)

# C-gents: Category theory composition
from agents.c import (
    Maybe, Just, Nothing, maybe, either,
    parallel, fan_out, race, branch, switch
)

# H-gents: Dialectic introspection
from agents.h import (
    hegel, jung, lacan,
    DialecticInput, JungInput, LacanInput
)

# K-gent: Personalization
from agents.k import (
    kgent, query_persona,
    DialogueMode, DialogueInput, PersonaQuery
)

# Runtime: LLM execution
from runtime import ClaudeRuntime, OpenRouterRuntime, LLMAgent

# Build pipelines
pipeline = validate >> transform >> persist

# Parallel execution
results = await parallel(agent1, agent2, agent3).invoke(input)

# LLM-backed execution
runtime = ClaudeRuntime()  # Uses ANTHROPIC_API_KEY
result = await runtime.execute(my_llm_agent, input_data)

# K-gent dialogue
k = kgent()
response = await k.invoke(DialogueInput(
    message="Should I add another feature?",
    mode=DialogueMode.CHALLENGE  # or REFLECT, ADVISE, EXPLORE
))
print(response.response)  # "This might conflict with your dislike of 'feature creep'..."

# K-gent composition: personalize other agents
style = await query_persona().invoke(PersonaQuery(aspect="all", for_agent="robin"))
# → suggested_style: ["be direct about uncertainty", "connect to first principles"]
```
