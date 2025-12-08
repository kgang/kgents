# Reality Classification

J-gents classify tasks into three reality types before proceeding.

---

## The Trichotomy

### 1. DETERMINISTIC Reality

> The task is atomic, well-defined, and bounded.

**Characteristics**:
- Single-step execution possible
- Clear input → output mapping
- No decomposition needed
- Low entropy consumption

**Examples**:
- "Add 2 + 2"
- "Query SQL: SELECT * FROM users WHERE id=5"
- "Format this JSON"
- "Read file contents"

**Action**: Execute directly with standard tool/agent.

---

### 2. PROBABILISTIC Reality

> The task is complex and requires decomposition.

**Characteristics**:
- Multiple sub-tasks required
- Several possible approaches
- Requires coordination
- Moderate entropy consumption

**Examples**:
- "Analyze these logs for errors"
- "Refactor this module for clarity"
- "Design an API for user management"
- "Fix this bug" (diagnosis + repair)

**Action**: Decompose into sub-promises, spawn child J-gents.

---

### 3. CHAOTIC Reality

> The task is unbounded, recursive, or exceeds stability limits.

**Characteristics**:
- No clear stopping condition
- Recursive without termination
- Exceeds entropy budget
- Would consume unlimited resources

**Examples**:
- "Solve all problems"
- "Improve this forever"
- "Generate infinite variations"
- Any task at depth > max_depth

**Action**: Collapse to Ground immediately. Do not attempt.

---

## The Classification Agent

```
RealityClassifier: (Intent, Context, EntropyBudget) → Reality

where Reality = DETERMINISTIC | PROBABILISTIC | CHAOTIC
```

### Interface

```python
@dataclass
class ClassificationInput:
    intent: str           # What the task asks for
    context: dict         # Available information
    entropy_budget: float # Remaining computation freedom (0.0-1.0)

@dataclass
class ClassificationOutput:
    reality: Reality
    confidence: float     # 0.0-1.0
    reasoning: str        # Why this classification
```

---

## Classification Heuristics

The classifier applies these tests in order:

### Test 1: Budget Check

```
if entropy_budget < CHAOS_THRESHOLD:
    return CHAOTIC  # Force collapse regardless of task
```

Rationale: If we're too deep, everything becomes chaotic.

### Test 2: Atomicity Test

```
Can this be done in one tool call?
  Yes → DETERMINISTIC
  No  → continue
```

Indicators of atomicity:
- Task maps to single API call
- No "and" or "then" in intent
- Output type is primitive or simple structure

### Test 3: Decomposition Test

```
Can this be broken into clear sub-tasks?
  Yes → PROBABILISTIC
  No  → continue
```

Indicators of decomposability:
- Sequential steps identifiable
- Subtasks have clear boundaries
- Dependencies can be mapped

### Test 4: Boundedness Test

```
Is there a clear stopping condition?
  Yes → PROBABILISTIC
  No  → CHAOTIC
```

Indicators of boundedness:
- Finite enumeration possible
- Success criteria defined
- Resource limits specified

---

## Classification Flow

```
                    ┌─────────────────┐
                    │ Budget Check    │
                    │ budget < 0.1?   │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              │ yes                         │ no
              ▼                             ▼
        ┌──────────┐               ┌─────────────────┐
        │ CHAOTIC  │               │ Atomicity Test  │
        └──────────┘               │ one tool call?  │
                                   └────────┬────────┘
                                            │
                             ┌──────────────┴──────────────┐
                             │ yes                         │ no
                             ▼                             ▼
                    ┌───────────────┐         ┌─────────────────────┐
                    │ DETERMINISTIC │         │ Decomposition Test  │
                    └───────────────┘         │ clear sub-tasks?    │
                                              └──────────┬──────────┘
                                                         │
                                          ┌──────────────┴──────────────┐
                                          │ yes                         │ no
                                          ▼                             ▼
                                  ┌───────────────┐          ┌─────────────────┐
                                  │ PROBABILISTIC │          │ Boundedness Test│
                                  └───────────────┘          │ stopping cond?  │
                                                             └────────┬────────┘
                                                                      │
                                                       ┌──────────────┴──────────────┐
                                                       │ yes                         │ no
                                                       ▼                             ▼
                                               ┌───────────────┐            ┌──────────┐
                                               │ PROBABILISTIC │            │ CHAOTIC  │
                                               └───────────────┘            └──────────┘
```

---

## Examples with Classification

| Intent | Classification | Reasoning |
|--------|---------------|-----------|
| "Return 42" | DETERMINISTIC | Single value, no computation |
| "Read config.yaml" | DETERMINISTIC | Single file read |
| "Parse JSON and extract name" | DETERMINISTIC | Single transformation |
| "Find all Python files with TODO" | PROBABILISTIC | Enumeration + filter |
| "Refactor auth module" | PROBABILISTIC | Analysis + modification |
| "Debug the crash" | PROBABILISTIC | Diagnosis + fix |
| "Make everything better" | CHAOTIC | Unbounded, no stopping |
| "Generate all possibilities" | CHAOTIC | Infinite enumeration |
| Any task at depth 4+ | CHAOTIC | Budget exhausted |

---

## Relationship to Bootstrap Agents

Reality classification is derivable from:

1. **Ground** provides the criteria for "what counts as atomic"
2. **Judge** evaluates "is this decomposable in a useful way?"
3. **Fix** iteration informs "is there a stopping condition?"

The classifier IS a composed agent:
```
RealityClassifier = Ground >> BudgetCheck >> AtomicityJudge >> DecompositionJudge >> BoundednessJudge
```

---

## Anti-patterns

- **Over-classification as DETERMINISTIC**: Breaking complex tasks into wrong granularity
- **Under-classification as CHAOTIC**: Giving up too early on tractable problems
- **Ignoring budget**: Attempting PROBABILISTIC when budget is exhausted
- **Static classification**: Not re-evaluating as context changes

---

## See Also

- [README.md](README.md) - J-gents overview
- [stability.md](stability.md) - Entropy budgets
- [lazy.md](lazy.md) - How classification affects promise expansion
