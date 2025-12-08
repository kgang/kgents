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
| Autopoiesis | ✅ `autopoiesis.py` (spec/impl check) + `self_improve.py` (code review) |
| C-gents (Category Theory) | ✅ `impl/claude-openrouter/agents/c/` + specs for all patterns |
| H-gents (Hegel/Jung/Lacan) | ✅ `impl/claude-openrouter/agents/h/` |
| K-gent (Persona) | ✅ `impl/claude-openrouter/agents/k/` |
| A-gents (Skeleton + Creativity) | ✅ `impl/claude-openrouter/agents/a/` |
| B-gents (Hypothesis + Robin) | ✅ `impl/claude-openrouter/agents/b/` + robin spec |
| runtime/ | ✅ `impl/claude-openrouter/runtime/` (ClaudeRuntime, OpenRouterRuntime) |
| zen-agents | 🗑️ Removed (was Textual TUI demo) |

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
│   ├── agents/a/            # ✅ AbstractSkeleton, AgentMeta, CreativityCoach
│   ├── agents/b/            # ✅ HypothesisEngine, Robin (scientific companion)
│   ├── runtime/             # ✅ LLM execution (ClaudeCLIRuntime, ClaudeRuntime, OpenRouterRuntime)
│   ├── autopoiesis.py       # ✅ Spec/impl alignment check
│   └── self_improve.py      # ✅ Code review via HypothesisEngine + Judge
└── docs/                    # Supporting documentation
    └── BOOTSTRAP_PROMPT.md  # LLM prompt for implementing kgents
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

## A-gents (Implemented)

Abstract architectures + Art/Creativity:

| Agent | Purpose | Key Type |
|-------|---------|----------|
| `AbstractAgent` | Alias for `Agent[A,B]` — the skeleton IS the bootstrap | Type alias |
| `AgentMeta` | Optional rich metadata (identity, interface, behavior) | Dataclass |
| `CreativityCoach` | First LLMAgent — expands ideas via 4 modes | `CreativityInput → CreativityResponse` |

Modes: `EXPAND`, `CONNECT`, `CONSTRAIN`, `QUESTION`
Personas: `PLAYFUL`, `PHILOSOPHICAL`, `PRACTICAL`, `PROVOCATIVE`, `WARM`

## B-gents (Implemented)

Scientific discovery agents with Popperian epistemology:

| Agent | Purpose | Key Type |
|-------|---------|----------|
| `HypothesisEngine` | Generates falsifiable hypotheses from observations | `HypothesisInput → HypothesisOutput` |
| `RobinAgent` | Personalized scientific companion (composes K-gent + Hypothesis + Hegel) | `RobinInput → RobinOutput` |

**HypothesisEngine:**
- Variants: `hypothesis_engine()`, `rigorous_engine()`, `exploratory_engine()`
- Key types:
  - `Hypothesis`: statement, confidence (0-1), novelty, falsifiable_by (REQUIRED), assumptions
  - `NoveltyLevel`: `INCREMENTAL`, `EXPLORATORY`, `PARADIGM_SHIFTING`
  - `HypothesisInput`: observations, domain, question (optional), constraints
  - `HypothesisOutput`: hypotheses, reasoning_chain, suggested_tests

**Robin:**
- Variants: `robin()`, `robin_with_persona(seed)`, `quick_robin(runtime)`
- Composes: K-gent personalization → hypothesis generation → dialectic refinement
- Key types:
  - `RobinInput`: query, observations, domain, dialogue_mode, apply_dialectic
  - `RobinOutput`: personalization, kgent_reflection, hypotheses, dialectic, synthesis_narrative, next_questions

**Design decisions (Dec 2025):**
- **Falsifiability is strictly required** — `Hypothesis` validation fails without `falsifiable_by`. Lean into Popperian strictness.
- **Robin is an orchestrator, not a simple composition** — Types don't align for `>>`, but conceptually: personalization → hypotheses → dialectic
- **Future:** Confidence should evolve to support qualitative/quantitative ratings with uncertainty metadata

## Runtime (Implemented)

LLM execution layer for agents:

| Class | Purpose | Usage |
|-------|---------|-------|
| `LLMAgent[A, B]` | Base for LLM-backed agents | Extend, implement `build_prompt` + `parse_response` |
| `ClaudeRuntime` | Execute via Anthropic API | `await runtime.execute(agent, input)` |
| `ClaudeCLIRuntime` | Execute via Claude Code CLI (OAuth) | No API key needed, uses Fix pattern for retries |
| `OpenRouterRuntime` | Execute via OpenRouter | Same API, different provider |

## Next Steps

**Bootstrap is now self-referential** — kgents can implement kgents.

| Document | Purpose |
|----------|---------|
| `docs/BOOTSTRAP_PROMPT.md` | Active — LLM prompt for implementing kgents |
| `AUTONOMOUS_BOOTSTRAP_PROTOCOL.md` | Completed — A-gents + B-gents implemented |

### Completed Phases

| Phase | Status | Notes |
|-------|--------|-------|
| K-gent | ✅ DONE | Personalizes all other agents |
| A-gents | ✅ DONE | AbstractSkeleton (alias), AgentMeta, CreativityCoach |
| B-gents B.1 | ✅ DONE | HypothesisEngine |
| B-gents B.2 | ✅ DONE | Robin (scientific companion) |

**What's Next:**
- Tests: Add pytest suite for agents/b/ (hypothesis, robin)
- D-gents: Data/Database agents (spec needed)
- E-gents: Evaluation/Ethics agents (spec needed)
- Package: Publish kgents-runtime to PyPI

## Recent Changes

- **self_improve.py Added** (Dec 2025): Code review via ClaudeCLIRuntime + HypothesisEngine + Judge + Contradict. Results: 25/25 modules ACCEPT, 75 hypotheses, 4 tensions resolved. Key findings: testing gap across all modules, type annotation improvements needed.
- **Autopoiesis Complete** (Dec 2025): Spec/impl alignment check. 0 tensions, 22/22 verdicts accept.
- **zen-agents Dropped** (Dec 2025): Textual TUI demo removed; new generation planned

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

# A-gents: Abstract skeleton + creativity
from agents.a import (
    AbstractAgent, AgentMeta,
    CreativityCoach, CreativityInput, CreativityMode,
    creativity_coach, playful_coach
)

# B-gents: Scientific discovery
from agents.b import (
    HypothesisEngine, HypothesisInput, HypothesisOutput,
    Hypothesis, NoveltyLevel,
    hypothesis_engine, rigorous_engine, exploratory_engine,
    RobinAgent, RobinInput, RobinOutput,
    robin, robin_with_persona, quick_robin
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
from runtime import ClaudeCLIRuntime, ClaudeRuntime, OpenRouterRuntime, LLMAgent

# Build pipelines
pipeline = validate >> transform >> persist

# Parallel execution
results = await parallel(agent1, agent2, agent3).invoke(input)

# LLM-backed execution (CLI uses OAuth, no API key needed)
runtime = ClaudeCLIRuntime()  # Or ClaudeRuntime() with API key
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

# Creativity Coach (first LLMAgent!)
coach = playful_coach()
runtime = ClaudeCLIRuntime()
result = await runtime.execute(coach, CreativityInput(
    seed="underwater city",
    mode=CreativityMode.EXPAND
))
print(result.output.responses)  # ["Buoyancy-Based Social Hierarchy...", ...]

# Hypothesis Engine (scientific reasoning)
engine = hypothesis_engine()
result = await runtime.execute(engine, HypothesisInput(
    observations=["Protein X aggregates at pH < 5", "Aggregation correlates with disease"],
    domain="biochemistry",
    question="Why does Protein X aggregate at low pH?"
))
for h in result.output.hypotheses:
    print(h.statement)
    print(f"  Falsifiable by: {h.falsifiable_by}")

# Robin (scientific companion) - composes K-gent + Hypothesis + Hegel
from agents.k import DialogueMode
robin_agent = robin(runtime=runtime)
result = await robin_agent.invoke(RobinInput(
    query="Why do neurons form sparse codes?",
    domain="neuroscience",
    dialogue_mode=DialogueMode.EXPLORE,
))
print(result.synthesis_narrative)
print(result.next_questions)  # What to explore next
```
