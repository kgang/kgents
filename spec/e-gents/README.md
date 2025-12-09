# E-gents: Evolution Agents

**Genus**: E (Evolve)
**Theme**: Dialectical evolution through safe, experimental code transformation
**Motto**: *"Evolution through dialogue, safety through testing"*

## Overview

E-gents are agents that evolve code through dialectical reasoning. Unlike traditional refactoring tools that apply deterministic transformations, E-gents treat code improvement as a **creative, experimental process** grounded in:

1. **Dialectical thinking**: Current code (thesis) + Proposed improvement (antithesis) → Evolved code (synthesis)
2. **Experimental methodology**: Hypotheses are cheap, production is sacred
3. **Institutional memory**: Learning from past attempts prevents repeated failures
4. **Fixed-point convergence**: Safe self-modification through iterative refinement
5. **Multi-layered safety**: Validation at prompt, parse, and test layers

## Philosophy

### The Hegelian Foundation

E-gents embrace **productive tension** as the engine of evolution:

- **Thesis**: The current implementation (what works now)
- **Antithesis**: The proposed improvement (what could be better)
- **Synthesis**: The evolved form (what emerges from resolving tension)

Tensions are **data**, not failures. When thesis and antithesis cannot be reconciled, the tension is **held** for human judgment rather than forced into premature resolution.

### The Experimental Mindset

Evolution happens through **safe experimentation**:

```
Observation → Hypothesis → Experiment → Judgment → Incorporation
```

Each stage is:
- **Falsifiable**: Clear success/failure criteria
- **Isolated**: Experiments run in sandboxes, never touching production
- **Reversible**: Git safety ensures rollback is always possible
- **Composable**: Each stage is an independent morphism

### The Learning Imperative

E-gents maintain **institutional memory** across sessions:

- **Rejected hypotheses** are recorded with rationale to prevent re-proposal
- **Failure patterns** are analyzed to improve future prompt engineering
- **Successful patterns** are tracked to guide AST-based hypothesis generation
- **Tensions held** are logged for human review and pattern analysis

## Core Principles (Beyond the 7)

In addition to the foundational kgents principles, E-gents add:

### 8. Experimental

**Treat code changes as falsifiable hypotheses.**

- Generate specific, testable improvement proposals
- Validate through multiple independent layers (syntax, types, tests, principles)
- Accept or reject based on evidence, not intuition
- Record outcomes for institutional learning

### 9. Dialectical

**Embrace productive tension between current and proposed.**

- Thesis (current) and antithesis (proposal) are both valid perspectives
- Synthesis emerges from genuine engagement, not forced consensus
- Unresolvable tensions are held, not hidden
- Evolution preserves what works while improving what doesn't

### 10. Self-Aware

**Safe self-modification through convergence detection.**

- Meta-evolution (evolving the evolution agents) uses fixed-point iteration
- Similarity metrics detect when changes stabilize
- Multiple validation layers prevent self-corruption
- Human approval required for meta-changes above threshold

### 11. Metered (via B-gent Banker)

**Conservative token consumption builds user trust.**

E-gents integrate the **B-gent Banker** ([spec/b-gents/banker.md](../b-gents/banker.md)) to manage token economics. The Metered Functor transforms evolution agents into economic agents:

```
Metered: Agent[A, B] → Agent[A, Receipt[B]]
```

**The Metering Principle** (from Banker):
- **Linear Logic**: Tokens are resources that are *consumed*, not copied
- **Start minimal**: Default prompts ~30 lines, escalate only on failure
- **Diff over whole**: Request changed symbols, not entire files
- **Token Futures**: Reserve capacity for multi-step evolution jobs
- **Sinking Fund**: 1% tax builds emergency reserve for critical fixes

**Token Budget Levels** (Progressive Escalation):
| Level | Prompt Size | Context | Cost Multiplier |
|-------|-------------|---------|-----------------|
| 0 (Minimal) | ~30 lines | Hypothesis + target | 1x |
| 1 (Targeted) | ~80 lines | + function context | 3x |
| 2 (Full) | ~250 lines | + API refs, patterns | 10x |

**The Hydraulic Model** (Token Bucket):
```python
# From B-gent Banker: Time = Money
account.balance = min(max_balance, balance + (delta * refill_rate))
```

Evolution budgets refill over time. Burst capacity allows intensive sessions; sustained high usage triggers rate limiting.

**The Trust Gradient**: Users see E-gents succeed with minimal tokens before trusting larger budgets. Conservative defaults demonstrate competence and build confidence.

## The Evolution Pipeline

E-gents compose multiple specialized agents into a coherent evolution pipeline:

```
EvolutionAgent =
  Ground >> Hypothesis >> Experiment >> Judge >> Sublate >> Incorporate
```

### Stage 1: Ground (AST Analysis)

**Morphism**: `CodeModule → CodeStructure`

Analyzes code statically to identify:
- Functions with high complexity
- Missing type annotations
- Structural patterns (classes, imports, dependencies)
- Targeted improvement opportunities

### Stage 2: Hypothesis (Idea Generation)

**Morphism**: `(CodeModule, CodeStructure) → Hypotheses`

Generates improvement ideas from:
- AST-based targeted suggestions (from structure analysis)
- LLM-generated hypotheses (from understanding domain/context)
- Filtered by memory (excluding recently rejected/accepted)

### Stage 3: Experiment (Test & Validate)

**Morphism**: `(Hypothesis, CodeModule) → Experiment`

Generates improved code and validates through:
- **Prompt engineering**: Rich context with types, errors, patterns
- **Parsing**: Multi-strategy extraction with fallbacks
- **Syntax validation**: AST parsing confirms valid Python
- **Type checking**: mypy in strict mode (optional)
- **Test execution**: pytest validation (optional)

### Stage 4: Judge (Principle Evaluation)

**Morphism**: `Experiment → Verdict`

Evaluates improvements against the 7 principles:
- Tasteful, Curated, Ethical, Joy-Inducing
- Composable, Heterarchical, Generative

Returns: `ACCEPT | REVISE | REJECT`

### Stage 5: Sublate (Tension Resolution)

**Morphism**: `(Thesis, Antithesis) → Synthesis | HoldTension`

Attempts dialectical synthesis:
- If productive tension → synthesis emerges
- If irreconcilable → tension held for human judgment
- Preserves valuable aspects of both thesis and antithesis

### Stage 6: Incorporate (Safe Application)

**Morphism**: `Experiment → Applied`

Applies approved changes with git safety:
- Pre-commit verification (no uncommitted changes)
- Atomic file write
- Git commit with detailed message
- Rollback capability via git

## Reliability Through Layers

E-gents achieve high reliability through **defense in depth**:

### Layer 1: Prompt Engineering
- **PreFlightChecker**: Validates module health before attempting evolution
- **PromptContext**: Provides rich context (types, errors, domain patterns)
- **Structured prompts**: Clear requirements, output format, validation criteria

### Layer 2: Parsing & Validation
- **CodeParser**: Multi-strategy extraction (4 fallback strategies)
- **SchemaValidator**: Fast pre-mypy validation (constructors, generics)
- **CodeRepairer**: AST-based incremental repair for common errors

### Layer 3: Recovery & Learning
- **RetryStrategy**: Failure-aware prompt refinement for retry attempts
- **FallbackStrategy**: Progressive simplification (minimal → type-only → docs)
- **ErrorMemory**: Cross-session tracking of failure patterns

## Composability

Every E-gent is a **morphism** with clear input/output types:

```python
# Individual agents are composable
pipeline = (
    ast_analyzer
    >> hypothesis_generator
    >> experiment_runner
    >> judge
)

# Evolution can compose with other gents
full_process = k_gent >> evolution_agent >> bio_gent
```

## Heterarchy

E-gents have **no fixed orchestrator**:

- The pipeline order can change based on context
- Agents can invoke each other peer-to-peer
- Memory is shared, not owned by a central coordinator
- Sublation can occur at any stage, not just the end

## Anti-Patterns

E-gents must **never**:

1. ❌ Apply changes without testing
2. ❌ Ignore test failures or type errors
3. ❌ Re-propose recently rejected hypotheses
4. ❌ Force synthesis when tension should be held
5. ❌ Evolve code without git safety (uncommitted changes present)
6. ❌ Self-modify without convergence detection
7. ❌ Hide errors or conflicts in logs
8. ❌ **Use full context prompts by default** (violates Metered principle)
9. ❌ **Request entire files when diffs suffice** (token waste)
10. ❌ **Load API references preemptively** (lazy load on hallucination)

## See Also

- **[evolution-agent.md](./evolution-agent.md)** - Full pipeline specification
- **[grounding.md](./grounding.md)** - AST analysis and code structure agents
- **[memory.md](./memory.md)** - Institutional memory and learning agents
- **[safety.md](./safety.md)** - Self-evolution and convergence detection
- **[H-gents](../h-gents/)** - Dialectical reasoning foundation
- **[B-gents](../b-gents/)** - Hypothesis generation methodology
- **[B-gents/banker.md](../b-gents/banker.md)** - Token economics and the Metered Functor

---

*"The code that evolves safely is the code that validates thoroughly."*
