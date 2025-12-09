# impl/claude HYDRATE

**Last Updated:** 2025-12-08

## TL;DR

**Status:** Bootstrap self-improvement applied to evolve.py ✅
**Commit:** `07332d4` feat(evolve): Add bootstrap agent integration
**Next:** Apply same patterns to `runtime/base.py` (with_retry → Fix) or `agents/t/` (self-evaluation)

---

## Next Session: Start Here

### Quick Commands
```bash
cd impl/claude
python evolve.py status          # Check evolution state
python evolve.py suggest         # See bootstrap-enhanced suggestions
python evolve.py meta --safe-mode --dry-run  # Test safe evolution
```

### Priority Options

1. **Apply bootstrap to runtime/base.py**
   - Replace `with_retry()` with bootstrap `Fix` agent
   - Add convergence tracking, entropy budgets

2. **Apply bootstrap to T-gents**
   - Add Judge self-evaluation at agent creation
   - Validate test agents against 7 principles

3. **Continue IMPROVEMENT_PLAN.md Phase B**
   - H7: Split `prompts.py` (762 lines)
   - H10: Split `sandbox.py` (460 lines)

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

| Priority | Action | Bootstrap Agent | Target | Status |
|----------|--------|-----------------|--------|--------|
| 1 | Add Judge self-check to EvolutionPipeline | Judge | evolve.py | ✅ Done |
| 2 | Replace with_retry with Fix agent | Fix | evolve.py | ✅ Done |
| 3 | Add Contradict to code tension detection | Contradict | evolve.py | ✅ Done |
| 4 | Ground prompts with persona | Ground | evolve.py | ✅ Done |
| 5 | Self-evaluate T-gents at creation | Judge | agents/t/*.py | Pending |

---

## Recent Activity

### Bootstrap Self-Improvement Applied (2025-12-08)

**Applied bootstrap agents directly to `evolve.py` for self-improvement:**

1. **Judge Integration** ✅
   - `judge_hypothesis_against_principles()`: Evaluates hypotheses against 7 principles
   - `HypothesisWrapper`: Wraps hypothesis strings as Agents for Judge

2. **Fix Integration** ✅
   - `iterate_with_fix()`: Convergence-tracked iteration with entropy budgets
   - Lazy instantiation via `_get_bootstrap_fix()`

3. **Contradict Integration** ✅
   - `detect_code_tension()`: Surfaces tensions between original/improved code
   - Used in safe evolution mode to flag API changes, style conflicts

4. **Ground Integration** ✅
   - `get_grounded_context()`: Injects Kent's persona values into analysis
   - `suggest` mode now shows grounded context before analysis

**Test Results:**
- `python evolve.py status` ✅
- `python evolve.py suggest` ✅ (shows Bootstrap Judge evaluation)
- Syntax validation ✅

---

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
