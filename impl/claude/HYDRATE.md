# impl/claude HYDRATE

**Last Updated:** 2025-12-08

## Current State

**Phase:** Bootstrap Self-Improvement Analysis
**Status:** Deep graph analysis complete ✅

---

## Bootstrap Self-Improvement Graph Analysis

### The 7 Bootstrap Agents

The bootstrap agents form the **irreducible kernel** from which all other agents can be regenerated:

```
┌─────────────────────────────────────────────────────────────────┐
│                    BOOTSTRAP AGENTS                             │
├─────────────────────────────────────────────────────────────────┤
│  Id         : A → A           (identity, composition unit)      │
│  Compose    : (f,g) → f>>g    (morphism composition)            │
│  Ground     : Void → Facts    (empirical seed: persona, world)  │
│  Contradict : (A,B) → Tension (detect contradictions)           │
│  Sublate    : Tension → Synthesis|Hold (Hegelian synthesis)     │
│  Judge      : Agent → Verdict (7 principles: tasteful→generative)│
│  Fix        : (f,a) → FixResult (fixed-point iteration)         │
└─────────────────────────────────────────────────────────────────┘
```

### Dependency Graph: Bootstrap → Agents → Runtime

```
                         ┌────────────────┐
                         │   bootstrap/   │
                         │   types.py     │
                         │   (511 lines)  │
                         └───────┬────────┘
                                 │
    ┌────────────────────────────┼────────────────────────────────┐
    │                            │                                │
    ▼                            ▼                                ▼
┌─────────┐              ┌──────────────┐               ┌─────────────┐
│  Id     │              │  Contradict  │               │    Judge    │
│  102 L  │              │  360 L       │               │    420 L    │
└────┬────┘              └──────┬───────┘               └──────┬──────┘
     │                          │                              │
     │                          │                              │
     ▼                          ▼                              ▼
┌─────────┐              ┌──────────────┐               ┌─────────────┐
│ Compose │              │   Sublate    │               │    Fix      │
│  164 L  │              │   337 L      │               │    303 L    │
└────┬────┘              └──────┬───────┘               └─────────────┘
     │                          │
     └────────────┬─────────────┘
                  │
                  ▼
            ┌────────────┐
            │   Ground   │
            │   164 L    │
            └────────────┘
```

### How Agents Consume Bootstrap

| Agent Category | Bootstrap Dependencies | Key Usage |
|----------------|------------------------|-----------|
| **H-gents** (hegel, jung, lacan) | Contradict, Sublate, Agent | Dialectic synthesis via Contradict>>Sublate |
| **E-gents** (evolution) | Agent, VerdictType, Sublate | Evolution pipeline with Fix pattern |
| **J-gents** (jgent, reality) | Agent, Fix pattern | JIT compilation with entropy budgets |
| **T-gents** (test agents) | Agent, ComposedAgent | Test harnesses for agents |
| **K-gent** (persona) | Ground, Facts, Agent | Persona grounding |
| **B-gents** (robin, hypothesis) | Agent | Scientific discovery |
| **C-gents** (functor, conditional) | Agent | Category-theoretic composition |

### Direct Self-Improvement Paths

**Key Insight:** Bootstrap agents can directly improve other agents **without external coordination** through these patterns:

#### 1. **Judge → Any Agent** (Quality Gate)
```python
# Bootstrap Judge can evaluate ANY agent against 7 principles
from bootstrap import Judge, JudgeInput

async def self_check(agent: Agent) -> Verdict:
    judge = Judge()
    return await judge.invoke(JudgeInput(agent=agent))

# Usage: Any agent can judge itself or peers
verdict = await self_check(evolution_agent)
if verdict.type == VerdictType.REVISE:
    # Apply suggested revisions
```

#### 2. **Contradict + Sublate → Conflict Resolution** (Hegelian Pattern)
```python
# Already composed in H-hegel, directly usable
from agents.h.hegel import HegelAgent, DialecticInput

hegel = HegelAgent()  # Uses Contradict >> Sublate internally
result = await hegel.invoke(DialecticInput(
    thesis=old_agent_output,
    antithesis=new_agent_output
))
# Result: Synthesis or productive tension to hold
```

#### 3. **Fix → Iterative Refinement** (Convergence Pattern)
```python
from bootstrap import Fix, FixConfig

# Any improvement loop can use Fix for convergence
async def improve_until_stable(agent, improve_fn):
    fix = Fix(FixConfig(max_iterations=10, entropy_budget=1.0))
    result = await fix.invoke((improve_fn, agent))
    return result.value if result.converged else result.value
```

#### 4. **Ground → Context Injection** (Fact Seeding)
```python
from bootstrap import Ground, VOID

# Any agent can ground itself with persona/world facts
facts = await Ground().invoke(VOID)
# facts.persona: Kent's values, communication style
# facts.world: current context, active projects
```

### Runtime Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                      runtime/base.py                            │
├─────────────────────────────────────────────────────────────────┤
│  LLMAgent(Agent)  : Bootstrap Agent + LLM execution            │
│  Runtime          : Abstract execution layer                    │
│  AgentContext     : System prompt + messages + facts            │
│  Result           : Either-based error handling                 │
│  with_retry       : Fix pattern for transient errors            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│  claude.py     : Anthropic API runtime                          │
│  cli.py        : Claude Code CLI runtime (OAuth)                │
│  openrouter.py : Multi-model runtime                            │
│  json_utils.py : LLM response parsing (robust_json_parse)       │
└─────────────────────────────────────────────────────────────────┘
```

### Self-Improvement Without External Coordination

**The key question:** Can bootstrap agents improve agents/runtime **directly**?

**Answer: YES**, through these patterns:

| Bootstrap Agent | Can Improve | How |
|-----------------|-------------|-----|
| **Judge** | Any agent | Evaluate against 7 principles, generate revision suggestions |
| **Fix** | Iterative processes | Converge on stable improvements, entropy-budgeted evolution |
| **Contradict+Sublate** | Conflicting outputs | Synthesize better solutions from thesis/antithesis |
| **Ground** | Context-sensitive agents | Inject persona values, world state |
| **Compose** | Agent pipelines | Build new compositions from existing agents |

### Specific Improvement Targets

#### For `impl/agents/`:

1. **E-gents self-improve via Judge**:
   - `evolution.py` can call `Judge` on generated hypotheses
   - Already has `CodeJudge` but doesn't use bootstrap Judge for self-evaluation

2. **H-gents are already optimal**:
   - `hegel.py` directly composes `Contradict >> Sublate`
   - No improvement needed - this IS the pattern

3. **J-gents can use Fix with entropy**:
   - `jgent.py` already uses entropy budgets
   - Could benefit from bootstrap Fix's convergence tracking

4. **T-gents can Judge themselves**:
   - Test agents could use Judge to validate their own design
   - Currently no self-validation

#### For `impl/runtime/`:

1. **LLMAgent inherits from bootstrap Agent** ✅
   - Already properly integrated

2. **with_retry uses Fix pattern implicitly**:
   - Could be refactored to use actual `Fix` agent
   - Would add convergence tracking, history

3. **json_utils could use Contradict**:
   - When parsing fails, surface tension between expected/actual
   - Let Sublate attempt repair strategy

### Recommended Self-Improvement Actions

| Priority | Action | Bootstrap Agent | Target |
|----------|--------|-----------------|--------|
| 1 | Add Judge self-check to EvolutionPipeline | Judge | agents/e/evolution.py |
| 2 | Replace with_retry with Fix agent | Fix | runtime/base.py |
| 3 | Add Contradict to json parsing | Contradict | runtime/json_utils.py |
| 4 | Ground E-gent prompts with persona | Ground | agents/e/prompts.py |
| 5 | Self-evaluate T-gents at creation | Judge | agents/t/*.py |

---

## Recent Activity

### J-gents Phase 2: K-gent Enhancement + Cleanup (2025-12-08)
- ✅ Created `demo_kgent.py` - Interactive K-gent CLI (284 lines)
- ✅ Comprehensive spec fidelity analysis (75/100 alignment)
- ✅ Created `agents/k/README.md` - Developer documentation
- 🧹 **Major Cleanup:**
  - Removed K_GENT_SESSION_SUMMARY.md (details in agents/k/README.md)
  - Removed 6 stale files (52K): plan scripts, demo_village_story, self_improve, decision docs
  - Reorganized tests/ into proper structure:
    - `agents/e_gents/`, `agents/j_gents/`, `agents/t_gents/`
    - `utils/` for test utilities
    - Updated tests/README.md with new structure
- 🔴 **Critical Gap:** Access control not implemented (security/ethics)
- ⚠️ **API Mismatch:** `EvolutionInput` vs spec's `PersonaUpdate`

### Session 2025-12-08 (Earlier)
- ✅ **H5 Complete**: JSON utilities extracted to `runtime/json_utils.py` (commit cb98af8)
- ✅ Created HYDRATE.md to track implementation progress
- 📊 Reviewed IMPROVEMENT_PLAN.md priorities
- 🔍 Analyzed meta-evolution failures

### Meta-Evolution Attempts (Earlier Today)
- Ran `evolve.py meta --auto-apply` (3 attempts)
- Generated good hypotheses matching IMPROVEMENT_PLAN.md:
  - H3: Decompose EvolutionPipeline (19 methods → composable stages)
  - H4: Extract show_suggestions/show_status functions
  - H5: Lazy imports refactor
- **Result:** Timeouts and type errors in auto-generated code
- **Lesson:** Meta-evolution on evolve.py requires manual approach

## Implementation Progress (IMPROVEMENT_PLAN.md)

### Phase A: Quick Wins ⚡ In Progress
- [x] **H5**: Extract `runtime/json_utils.py` (250 lines from runtime/base.py) - ✅ **DONE** (commit cb98af8)
- [ ] **H2**: Extract `SuggestionAgent` from `show_suggestions` function - IN PROGRESS
- [ ] **H4**: Lazy imports in `evolve.py`

### Phase B: Core Refactoring (Not Started)
- [ ] **H1**: Decompose `EvolutionPipeline` (19 methods → 4 agents)
- [ ] **H7**: Split `prompts.py` (762 lines)
- [ ] **H10**: Split `sandbox.py` (460 lines)

### Phase C: Deep Refactoring (Not Started)
- [ ] **H8**: Refactor `parser.py` (687 lines)
- [ ] **H11**: Decompose `chaosmonger.py` (620 lines)
- [ ] **H13**: Refactor `robin.py` (570 lines)

### Phase D: Polish (Not Started)
- H3, H6, H9, H12, H14, H15

## Key Metrics

| Metric | Current | Target |
|--------|---------|--------|
| Files >500 lines | 18 | 10 |
| Functions >50 lines | 45+ | <20 |
| Classes >10 methods | 8 | 3 |
| evolve.py lines | 1,286 | <800 |

## Next Session Priorities

**Recommended:** Continue with Phase A quick wins

### Option 1: H4 - Lazy Imports (Recommended)
**File:** `evolve.py` (1,286 lines)
**Task:** Refactor 57 imports to use `typing.TYPE_CHECKING` and lazy loading
**Impact:** Faster startup, better testability
**Approach:**
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from agents.b.hypothesis import HypothesisEngine
    from agents.h.hegel import HegelAgent
    # ... other type-only imports

# Runtime imports in functions that use them
def _get_hypothesis_engine():
    from agents.b.hypothesis import HypothesisEngine
    return HypothesisEngine(...)
```

### Option 2: H2 - Extract SuggestionAgent
**File:** `evolve.py` lines 1005-1061 (56 lines)
**Task:** Extract `show_suggestions` into composable agent
**Note:** This might be over-engineering - consider simplifying instead

### Option 3: Skip to Phase B - H7 (prompts.py split)
**File:** `agents/e/prompts.py` (762 lines)
**Task:** Split into `prompts/base.py`, `prompts/improvement.py`, `prompts/analysis.py`
**Impact:** Better organization, clearer responsibilities
