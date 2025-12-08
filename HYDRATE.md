# HYDRATE.md - Session Context

## TL;DR

**kgents** = Kent's Agents. Spec-first agent framework with 7 irreducible bootstrap agents.

- `spec/` = Language spec (like Python)
- `impl/claude/` = Reference impl (like CPython) [renamed from claude-openrouter]

## Current State (Dec 8, 2025)

**Latest:** Phase 1 of 10 Critical Fixes complete and merged to main! Type system foundation fixed (Fix and FixComposedAgent signatures). Now beginning Phase 2: Architecture refactors (EvolutionAgent composition + Contradict protocol pattern).

**Previously:** Full-stack evolution complete! All 25 modules evolved with 100/100 experiments passed and incorporated (runtime, agents, bootstrap). Logging improved with persistent log files, prominent summary banners, and better UX for piped output.

| Component | Status |
|-----------|--------|
| 7 Principles | ✅ Defined in `spec/principles.md` |
| 7 Bootstrap Agents | ✅ Spec (`spec/bootstrap.md`) + Impl (`impl/claude/bootstrap/`) [Phase 1 ✅] |
| Autopoiesis | ✅ `autopoiesis.py` (spec/impl) + `self_improve.py` (review) + `evolve.py` (apply, optimized) |
| C-gents (Category Theory) | ✅ `impl/claude/agents/c/` + specs for all patterns |
| H-gents (Hegel/Jung/Lacan) | ✅ `impl/claude/agents/h/` |
| K-gent (Persona) | ✅ `impl/claude/agents/k/` |
| A-gents (Skeleton + Creativity) | ✅ `impl/claude/agents/a/` |
| B-gents (Hypothesis + Robin) | ✅ `impl/claude/agents/b/` + robin spec |
| runtime/ | ✅ `impl/claude/runtime/` (ClaudeRuntime, OpenRouterRuntime) |
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
├── impl/claude/             # Reference implementation (kgents-runtime package)
│   ├── bootstrap/           # ✅ 7 bootstrap agents (Python) [Phase 1 type fixes applied]
│   ├── agents/c/            # ✅ Category theory (Maybe, Either, Parallel, Conditional)
│   ├── agents/h/            # ✅ Dialectics (Hegel, Jung, Lacan)
│   ├── agents/k/            # ✅ K-gent persona (Dialogue, Query, Evolution)
│   ├── agents/a/            # ✅ AbstractSkeleton, AgentMeta, CreativityCoach
│   ├── agents/b/            # ✅ HypothesisEngine, Robin (scientific companion)
│   ├── runtime/             # ✅ LLM execution (ClaudeCLIRuntime, ClaudeRuntime, OpenRouterRuntime)
│   ├── autopoiesis.py       # ✅ Spec/impl alignment check
│   ├── self_improve.py      # ✅ Code review via HypothesisEngine + Judge
│   ├── evolve.py            # ✅ Experimental improvement framework
│   └── IMPLEMENTATION_PLAN.md # 📋 10 Critical Fixes roadmap (Phase 1 ✅)
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
| `ClaudeRuntime` | Execute via Anthropic API | `await runtime.execute(agent, input)` + client injection support |
| `ClaudeCLIRuntime` | Execute via Claude Code CLI (OAuth) | No API key needed, uses Fix pattern for retries + AI coercion fallback |
| `OpenRouterRuntime` | Execute via OpenRouter | Same API, different provider + runtime type validation |

**Async Composition (Dec 7, 2025):**
- `execute_async(input, runtime)`: Async execution of any agent
- `then_async(g)`: Chain agents asynchronously (`f.then_async(g)`)
- `acompose(*agents)`: Multi-agent async pipeline
- `parallel_execute(agents, inputs, runtime)`: True parallel execution for I/O-bound LLM calls
- `AsyncComposedAgent[A, B, C]`: Preserves morphism structure with A → B → C types

**ClaudeCLIRuntime features:**
- Fix pattern with configurable `max_retries` (default: 3)
- AI coercion: Uses another AI call to recover from parse failures (`enable_coercion=True`, `coercion_confidence=0.9`)
- Smart error classification: `ParseErrorType` enum distinguishes transient vs permanent failures
- Fast-fail on permanent errors (schema/missing/timeout) to avoid wasted retries
- Verbose mode and progress callbacks for observability

**OpenRouterRuntime features:**
- Runtime type validation via `_validate_output_type` (validates `parse_response` returns declared type B)
- Handles basic types, unions (`int | str`), generics (`list[str]`, `dict[str, int]`)
- Configurable with `validate_types=False` to disable

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
- **IMMEDIATE (IN PROGRESS)**: Phase 2 architecture refactors
  - Issue #10: Contradict Protocol Pattern (extract TensionDetector strategy, 8-12 hrs)
  - Issue #5: EvolutionAgent Composition (decompose into morphisms, 16-24 hrs)
- **Phase 3**: Infrastructure (Issue #4 Retry logic, #6 Error handling transparency)
- **Phase 0 Hotfix**: Security fix for parallel resource limits (Issue #9)
- Tests: Add pytest suite for agents/b/ (hypothesis, robin)
- D-gents: Data/Database agents (spec needed)
- E-gents: Evaluation/Ethics agents (spec needed)
- Package: Publish kgents-runtime to PyPI

## evolve.py - Experimental Improvement Framework

A creative framework for testing, synthesizing, and incorporating improvements:

```
Pipeline: HypothesisEngine >> CodeImprover (×N parallel) >> Validator >> Hegel >> Apply
```

| Stage | Agent | Function |
|-------|-------|----------|
| **Analyze** | AST parser | Deep code structure analysis (classes, functions, type coverage, error handling) |
| **Experiment** | `HypothesisEngine` → `CodeImprover` (parallel) | Generate concrete improvements from structural insights |
| **Test** | `Validator` | Syntax check, type check (filtered errors only), import validation |
| **Synthesize** | `HegelAgent` | Dialectic: current vs improvement → synthesis (optional with --quick) |
| **Incorporate** | `GitSafety` | Apply with git integration |

**Performance Optimizations (Dec 7, 2025):**
1. **Parallel module processing** — Modules evolve concurrently via asyncio.gather() for 2-5x speedup
2. **Parallel improvement generation** — Multiple hypotheses explored simultaneously per module
3. **AST caching** — Structure analysis cached per module (hash-keyed) to avoid redundant parsing
4. **Smart context pruning** — Files >500 lines send first/last 100 lines vs full 30k chars (50-75% token reduction)
5. **Quick mode** — `--quick` skips synthesis for 2x additional speedup

Typical runtime: **~10-15s per module** vs ~40-60s before (4x faster). With --quick + parallel: **2-3s per module** (20x faster).

**Smarter Analysis (Dec 7, 2025):** AST-based code structure detection generates actionable hypotheses:
- Detects: classes, functions, imports, error handling patterns, type annotation coverage
- Identifies anti-patterns: raises without try, async without asyncio import
- Observations like "⚠ Raises exceptions but has no error handling" vs generic "Lines: 150"

**Rich Observability (Dec 7, 2025):** Progress tracking ([3/10]), per-stage timing, clear pass/fail reasons, dry-run previews with line deltas.

Usage:
```bash
python evolve.py runtime --dry-run --quick --hypotheses=2  # FAST preview (recommended)
python evolve.py agents --auto-apply --max-improvements=2  # Quick iteration
python evolve.py bootstrap --quick --hypotheses=3          # Tune breadth vs speed
python evolve.py meta --dry-run                            # Self-improvement
```

Flags:
- `--dry-run`: Preview without applying
- `--auto-apply`: Auto-apply passing improvements
- `--quick`: Skip synthesis for 2x speed boost
- `--hypotheses=N`: Hypotheses per module (default: 4, try 2 for speed)
- `--max-improvements=N`: Max improvements per module (default: 4, try 2 for speed)

Key types:
- `CodeImprover`: `(Module, Hypothesis, Constraints) → Improvement` (single output, composable)
- `Experiment`: id, module, improvement, status, test_results, synthesis
- `Improvement`: description, rationale, new_content, type, confidence
- `ExperimentStatus`: PENDING → TESTING → PASSED → SYNTHESIZING → INCORPORATED

Output format (two-section):
```
## METADATA
{"description": "...", "rationale": "...", "improvement_type": "refactor", "confidence": 0.8}

## CODE
```python
# Complete file content
```
```
Avoids JSON escaping issues for code content.

## Recent Changes

- **Phase 1 Type Fixes Complete** (Dec 8, 2025): First phase of 10 Critical Fixes from IMPLEMENTATION_PLAN.md completed and pushed to `fix/phase-1-types`:
  - Issue #1: Fix[A,B] → Fix[A] (fixed points now correctly map A → A)
  - Issue #2: FixComposedAgent[A,C] → FixComposedAgent[A,B] (composition law compliance)
  - Removed type: ignore workaround, passes mypy --strict with zero errors
  - Zero breaking changes (no existing usages found)
  - Renamed impl/claude-openrouter → impl/claude for Python package compliance
  - Added mypy>=1.19.0 as dev dependency
  - **Next**: Merge branch, proceed to Phase 2 (architecture refactors)
- **Logging Improvements** (Dec 8, 2025): Added persistent log files to `.evolve_logs/`, prominent summary banners visible even with `| tail`, better structured output for long-running processes
- **Full-Stack Evolution** (Dec 8, 2025): All 25 modules evolved successfully with 100% pass rate - runtime (4), agents (13), bootstrap (8) all improved with async/await, type annotations, error handling, Fix pattern retries
- **Meta-Evolution Round 2 Success** (Dec 8, 2025): Second successful meta-evolution applied 8 more improvements to evolve.py and autopoiesis.py:
  - Async/await for experiment_one and incorporate functions
  - Comprehensive type annotations and runtime validation
  - Fix pattern retry logic for LLM calls in hypothesis generation
  - Dependency injection (runtime passed as parameter, not hardcoded)
  - Maybe/Either error boundaries for agent invocations
  - Async timeout and cancellation support for file I/O
  - **Bootstrap Evolution Ready:** 32 improvements identified for bootstrap agents (id, compose, sublate, types, contradict, fix, judge, ground)
  - **Full Pipeline Working:** Hypothesis generation → Improvement generation → Testing → Auto-apply all functional
- **Meta-Evolution API Fixes** (Dec 8, 2025): Fixed critical blocking issues after first meta-evolution:
  - Added `parse_structured_sections()` to runtime/base.py
  - Added `success`/`error` fields to `AgentResult`
  - Added `metadata` field to `AgentContext`
  - Fixed `HypothesisInput` API and `HypothesisEngine()` instantiation
  - Fixed f-string syntax errors in self_improve.py
- **evolve.py 2-5x Performance Boost** (Dec 7, 2025): Parallel module processing, AST caching, smart context pruning, configurable hypotheses/improvements. Runtime: 2-3s/module (fast) vs 10-15s (thorough).
- **ClaudeCLIRuntime AI Coercion** (Dec 7, 2025): Last-resort recovery via AI-powered response reformatting when parse fails.
- **self_improve.py Added** (Dec 2025): Code review via ClaudeCLIRuntime + HypothesisEngine + Judge + Contradict. Results: 25/25 modules ACCEPT, 75 hypotheses, 4 tensions resolved.
- **Autopoiesis Complete** (Dec 2025): Spec/impl alignment check. 0 tensions, 22/22 verdicts accept.

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

# Evolution: kgents improving itself
# Run from impl/claude-openrouter/
python evolve.py bootstrap --dry-run  # Preview improvements
python evolve.py agents --auto-apply  # Apply improvements
```
