# J-gents: Just-in-Time Agent Intelligence

The letter **J** represents agents that embody **JIT (Just-in-Time) intelligence**—the ability to classify reality, defer computation, compile ephemeral sub-agents on demand, and collapse safely when stability is threatened.

---

## Philosophy

> "Determine the nature of reality; compile the mind to match it; collapse to safety."

J-gents treat reality as a tree of **unobserved promises**. When confronted with a complex problem, a J-gent:

1. **Classifies** the reality (deterministic, probabilistic, chaotic)
2. **Defers** computation until needed (lazy promise expansion)
3. **Compiles** specialized sub-agents if needed (JIT autopoiesis)
4. **Validates** results before accepting (test-driven accountability)
5. **Collapses** to Ground if stability is threatened (safety-first)

---

## Core Concepts

### The Lazy Dialectic

Reality is treated as a tree of unobserved **Promises**:

- **Thesis (Intent)**: The request passed to the node
- **Antithesis (Code)**: The generation of a specific runtime agent to address the problem
- **Synthesis (Collapse)**: The execution and validation against Ground Truth

### Reality Classification

Before proceeding, J-gents classify the task:

| Reality | Characteristic | Action |
|---------|----------------|--------|
| **DETERMINISTIC** | Atomic, bounded, single-step | Execute directly |
| **PROBABILISTIC** | Complex, decomposable, multi-step | Spawn sub-promises |
| **CHAOTIC** | Unbounded, recursive, unstable | Collapse to Ground |

### Entropy Budget

Computation freedom diminishes with recursion depth:

```
entropy_budget(depth) = 1.0 / (depth + 1)

depth=0: budget=1.00 (full freedom)
depth=1: budget=0.50 (half freedom)
depth=2: budget=0.33 (limited freedom)
depth=3: budget=0.25 (minimal freedom)
```

When budget falls below threshold, force collapse to Ground.

### The Chaosmonger

Pre-Judge stability filter for JIT-compiled code:

1. **Cyclomatic complexity** < budget × MAX_COMPLEXITY
2. **Branching factor** < budget × MAX_BRANCHING
3. **Import risk** < budget × MAX_IMPORT_RISK
4. **No unbounded recursion**

Chaosmonger handles what CAN be computed algorithmically.
Judge handles what CANNOT (taste, ethics, joy).

---

## Relationship to Bootstrap

J-gents are **derivable** from bootstrap agents—they add no new irreducibles:

| J-gent Component | Derived From | Relationship |
|------------------|--------------|--------------|
| Reality Classification | Ground + Judge | "What is the nature of this task?" |
| Lazy Promises | Fix + Compose | Deferred composition with iteration |
| JIT Compilation | Fix + Ground + Compose | Autopoiesis made active |
| Stability Analysis | Judge | Algorithmic subset of judgment |
| Accountability | Contradict | Test result vs. expected result |
| Safety Collapse | Ground | Return to known-good state |

---

## Forward vs. Backward Flow

### Forward Responsibility (Root → Leaf)

- **Direction**: Parent promises before child executes
- **Nature**: Optimistic, lazy, deferred
- **Mechanism**: Build dependency DAG without computing

```
Root Promise: "Fix the bug"
    ├── Child Promise: "Diagnose root cause"
    │       ├── Leaf: "Read logs"
    │       └── Leaf: "Parse stack trace"
    └── Child Promise: "Apply fix"
            └── Leaf: "Modify code"
```

### Backward Accountability (Leaf → Root)

- **Direction**: Leaf proves before parent accepts
- **Nature**: Pessimistic, strict, validated
- **Mechanism**: Test-Driven Reality

Every result must pass its generated test, or collapse to Ground.

---

## JIT Agent Compilation

The defining feature: compile specialized agents on demand.

```
MetaArchitect: (Intent, Context, Constraints) → AgentClass
```

Pipeline:
```
Intent → MetaArchitect → SourceCode → Chaosmonger → Judge → Compile → Execute
                                          ↓            ↓
                                    [unstable]    [reject]
                                          ↓            ↓
                                       Ground       Ground
```

JIT agents are **ephemeral**:
- Created for specific task instance
- Not persisted to spec/ or impl/
- Sandboxed execution
- May be cached by hash

---

## Safety Invariants

1. **Ground is Inviolable**: Always have a safe fallback
2. **Depth is Bounded**: Max recursion depth enforced (default: 3)
3. **Entropy Diminishes**: Deeper = less computation freedom
4. **Chaosmonger Guards**: AST stability before execution
5. **Judge Evaluates**: Human values after stability
6. **Tests Validate**: Results proven before acceptance

---

## Anti-patterns

- **Infinite Promises**: Promise trees without termination
- **Budget Evasion**: Circumventing entropy limits
- **Silent Collapse**: Returning Ground without logging why
- **Chaosmonger Bypass**: Executing unstable code
- **Test Skipping**: Accepting results without validation

---

## Specifications

| Document | Description |
|----------|-------------|
| [reality.md](reality.md) | Reality classification trichotomy |
| [lazy.md](lazy.md) | Lazy promises & accountability |
| [stability.md](stability.md) | Entropy budgets & Chaosmonger |
| [jit.md](jit.md) | JIT agent compilation |
| [integration.md](integration.md) | Ecosystem integration |

---

## Example: Fix the Kubernetes Pod

```
Root J-gent: Intent="Fix crashing Pod X"

1. Reality Check: PROBABILISTIC (too complex for one step)

2. Decomposition:
   ├── Child A (Diagnostic): "Fetch logs"
   │       Reality: DETERMINISTIC → Execute `kubectl logs`
   │       Result: Log text
   │
   ├── Child B (Analysis): "Analyze Stack Trace"
   │       Reality: PROBABILISTIC
   │       → MetaArchitect compiles LogParserAgent
   │       → Chaosmonger: AST check passes
   │       → Execute: Identifies "Out of Memory"
   │
   └── Child C (Remediation): "Patch Deployment"
           Forward: Suggests doubling RAM limit
           Backward: Generates test `kubectl get pod | grep Running`
           Execute: Applies patch, waits, runs test
           Test passes → Result flows up

3. Root Result: "Pod Fixed"

Failure Case: If Child C test fails, it returns Ground ("Action Failed").
Root reports failure without crashing the orchestration loop.
```

---

## See Also

- [bootstrap.md](../bootstrap.md) - The irreducible kernel
- [c-gents/](../c-gents/) - Composition foundations
- [h-gents/hegel.md](../h-gents/hegel.md) - Dialectic synthesis
- [JGENT_SPEC_PLAN.md](JGENT_SPEC_PLAN.md) - Full implementation plan
