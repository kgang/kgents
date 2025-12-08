# HYDRATE.md - Session Context

## TL;DR

**kgents** = Kent's Agents. Spec-first agent framework with 7 irreducible bootstrap agents.

- `spec/` = Language spec (like Python)
- `impl/claude/` = Reference impl (like CPython) [renamed from claude-openrouter]

## Current State (Dec 8, 2025)

**Latest:** Bootstrap Docs Phases 1-3 Complete + Infrastructure Fixes ✅ (Dec 8, 2025)

**Completed this session:**
- ✅ **Bootstrap Docs Phase 2-3**: Error handling pattern (~70 lines), Composition verification checklist (~170 lines), Spec-First vs Agents-First resolution (~70 lines)
- ✅ **Infrastructure fixes** (commit 2bc0edc):
  - Fixed mypy execution in evolve.py (now uses `sys.executable -m mypy` for venv portability)
  - Fixed missing `field` import in hegel.py (Issue #7 implementation)
- ✅ **Bootstrap Docs Phase 1** (previously): Worked example, template, decision matrix, workflow, seven mini-judges, directory fix
- ✅ **Total Bootstrap Docs additions**: +782 lines across BOOTSTRAP_PROMPT.md and AUTONOMOUS_BOOTSTRAP_PROTOCOL.md

**Documents now mechanically translatable:**
- BOOTSTRAP_PROMPT.md: ~800 lines (was ~258) with worked example, template, verification checklist
- AUTONOMOUS_BOOTSTRAP_PROTOCOL.md: ~378 lines with decision matrix, workflow example, tension resolution

**Remaining Bootstrap Docs work (optional):**
- Phase 4: Common pitfalls, troubleshooting (320-400 lines)
- Phase 5: Cross-references, dependency diagram, GroundParser agent (140-200 lines)
- Phase 6: Regeneration test validation

**Next priorities:**
1. **Tests for agents/b/** (hypothesis, robin) - Critical gap
2. **D/E-gents specs** - Next agent families
3. **PyPI package** - Publish kgents-runtime
4. Bootstrap Docs Phase 4-6 (optional enhancements)

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

| Document | Purpose | Status |
|----------|---------|--------|
| `BOOTSTRAP_DOCUMENTS_IMPROVEMENT_PLAN.md` | **New** — Grand plan to improve bootstrap docs | ✅ Complete, ready for implementation |
| `docs/BOOTSTRAP_PROMPT.md` | LLM prompt for implementing kgents | 📋 Needs improvements per plan |
| `AUTONOMOUS_BOOTSTRAP_PROTOCOL.md` | Meta-level protocol for Kent + Claude Code | 📋 Needs improvements per plan |

### Completed Phases

| Phase | Status | Notes |
|-------|--------|-------|
| K-gent | ✅ DONE | Personalizes all other agents |
| A-gents | ✅ DONE | AbstractSkeleton (alias), AgentMeta, CreativityCoach |
| B-gents B.1 | ✅ DONE | HypothesisEngine |
| B-gents B.2 | ✅ DONE | Robin (scientific companion) |
| Phase 3 Infrastructure | ✅ DONE | Issue #4 (retry), #6 (Result types), #9 (parallel limits) |

**Next Steps (priority order):**
1. Tests: pytest suite for agents/b/ (hypothesis, robin)
2. D/E-gents: Spec Data/Database and Evaluation/Ethics agents
3. Package: Publish kgents-runtime to PyPI
4. Bootstrap Docs improvements (optional, see BOOTSTRAP_DOCUMENTS_IMPROVEMENT_PLAN.md for 6-phase plan)

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

- **Bootstrap Docs Implementation + Infrastructure Fixes** (Dec 8, 2025):
  - ✅ **Phase 2.3**: Error handling pattern with Result types (~70 lines to BOOTSTRAP_PROMPT.md)
  - ✅ **Phase 2.2**: Composition verification checklist with 6 test categories (~170 lines to BOOTSTRAP_PROMPT.md)
  - ✅ **Phase 3.1**: Spec-First vs Agents-First tension resolution (~70 lines to AUTONOMOUS_BOOTSTRAP_PROTOCOL.md)
  - ✅ **Infrastructure fix**: evolve.py mypy portability (`sys.executable -m mypy` for venv)
  - ✅ **Infrastructure fix**: hegel.py missing `field` import (Issue #7 lineage tracking)
  - ✅ Pushed commits to origin/main (2bc0edc, 8240000)
  - **Impact:** Bootstrap docs now ~800 lines (PROMPT) + ~378 lines (PROTOCOL), mechanically translatable by LLMs
  - **Status:** Phases 1-3 complete. Phase 4-6 optional (common pitfalls, troubleshooting, validation).
- **Bootstrap Documents Improvement Plan** (Dec 8, 2025):
  - ✅ Generated comprehensive 51-hypothesis plan via evolutionary analysis (using kgents to improve kgents docs)
  - Used 2 parallel Task agents for deep analysis of AUTONOMOUS_BOOTSTRAP_PROTOCOL.md and BOOTSTRAP_PROMPT.md
  - Identified gaps (14), contradictions (8), improvements (12), enhancements (17) across both documents
  - All 5 critical decisions resolved by Kent: Judge architecture (7 mini-judges), Autopoiesis (vibes-based), Directory (impl/claude/), Regeneration (behavior equivalence), Ground extraction (GroundParser agent)
  - Plan structured in 6 phases with validation gates, prioritized execution order, and success metrics
  - Timeline: 4-5 weeks, 74-104 hours estimated
  - **Autopoiesis demonstrated:** Plan itself ~80% agent-generated (Task agents for analysis, human for synthesis)
  - **Next actions:** Phase 1.1 (worked example for Id), Phase 3.2 (seven mini-judges pattern), Phase 5.3 (GroundParser agent)
- **Phase 2 Architecture Refactors Complete** (Dec 8, 2025):
  - ✅ **Issue #10 COMPLETE**: Extracted TensionDetector Protocol in contradict.py for extensible contradiction detection. Merged to main.
  - ✅ **Issue #5 COMPLETE**: EvolutionAgent composition refactor. Extracted 4 handler classes (ExplicitUpdateHandler, ObservationHandler, ContradictionHandler, ReviewHandler), created TriggerRouter agent. EvolutionAgent now uses composition instead of orchestration (58% code reduction). Merged to main.
- **Phase 1 Type Fixes Complete** (Dec 8, 2025): First phase of 10 Critical Fixes from IMPLEMENTATION_PLAN.md completed and merged to main:
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
