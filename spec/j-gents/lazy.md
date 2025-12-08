# Lazy Promises & Accountability

J-gents separate **Forward Responsibility** (promises) from **Backward Accountability** (proofs).

---

## The Promise Abstraction

A Promise is an unevaluated computation with a safety fallback.

### Data Structure

```python
@dataclass
class Promise(Generic[T]):
    """A deferred computation with Ground fallback."""

    intent: str                    # What this promises to deliver
    context: dict[str, Any]        # Available context at promise time
    ground: T                      # Fallback if promise fails
    depth: int = 0                 # Recursion depth (affects budget)

    # Lazily populated
    resolved: Optional[T] = None   # Computed value (once resolved)
    proof: Optional[Test] = None   # Validation test
    children: list["Promise"] = field(default_factory=list)  # Sub-promises
```

### Promise States

```
    ┌──────────┐
    │ PENDING  │  ← Initial state
    └────┬─────┘
         │ resolve()
         ▼
    ┌──────────┐
    │RESOLVING │  ← Computation in progress
    └────┬─────┘
         │
    ┌────┴────┬──────────┐
    │         │          │
    ▼         ▼          ▼
┌────────┐ ┌────────┐ ┌────────┐
│RESOLVED│ │COLLAPSED│ │ FAILED │
│(value) │ │(ground) │ │(error) │
└────────┘ └────────┘ └────────┘
```

- **PENDING**: Promise created, not yet resolved
- **RESOLVING**: Computation started
- **RESOLVED**: Successfully computed and validated
- **COLLAPSED**: Failed validation, returned Ground
- **FAILED**: Error during computation (still returns Ground)

---

## Forward Responsibility (Root → Leaf)

### Definition

> The parent promises before the child executes.

Forward responsibility flows from root to leaf:
- Build the dependency DAG
- Allocate entropy budgets
- NO computation yet

### Example

```
Root Promise: "Fix the bug in auth module"
    │
    ├── Child Promise: "Diagnose the bug"
    │   budget: 0.5
    │       │
    │       ├── Leaf: "Read auth.py"
    │       │   budget: 0.33, reality: DETERMINISTIC
    │       │
    │       └── Leaf: "Find failing test"
    │           budget: 0.33, reality: DETERMINISTIC
    │
    └── Child Promise: "Apply the fix"
        budget: 0.5
            │
            └── Leaf: "Modify code + run tests"
                budget: 0.33, reality: PROBABILISTIC
```

### Properties

- **Lazy**: Tree is built before any computation
- **Optimistic**: Assumes children will succeed
- **Budget propagation**: Each level gets reduced budget
- **Dependency tracking**: Parent knows what it needs from children

---

## Backward Accountability (Leaf → Root)

### Definition

> The child proves before the parent accepts.

Backward accountability flows from leaf to root:
- Execute leaf computations
- Validate results with tests
- Collapse to Ground on failure
- Propagate validated results upward

### Test-Driven Reality

Every non-trivial computation generates a validation test:

```python
TestGenerator: (Intent, Result) → Test
Test: Result → bool
```

The result is NOT accepted unless `test(result) == True`.

### Example

```python
async def resolve_with_accountability(promise: Promise[T]) -> T:
    """Resolve promise with backward accountability."""

    # Classify reality
    reality = classify(promise.intent, promise.context, promise.budget)

    if reality == Reality.CHAOTIC:
        return promise.ground  # Collapse immediately

    if reality == Reality.DETERMINISTIC:
        # Execute directly
        result = await execute_atomic(promise)
    else:
        # Resolve children first (backward flow)
        child_results = []
        for child in promise.children:
            child_result = await resolve_with_accountability(child)
            child_results.append(child_result)

        # Combine child results
        result = await combine(promise.intent, child_results)

    # Generate and run accountability test
    test = await generate_test(promise.intent, result)
    if not test(result):
        log_collapse(promise, "Test failed", result)
        return promise.ground  # Collapse to safety

    # Success!
    promise.resolved = result
    promise.proof = test
    return result
```

### Properties

- **Strict**: No result accepted without passing test
- **Pessimistic**: Assumes failure is possible
- **Safe**: Failed tests collapse to Ground (never crash)
- **Traceable**: Every result has proof of validity

---

## Test Generation

### What Tests Validate

| Intent Pattern | Test Type |
|---------------|-----------|
| "Parse X" | `parsed.is_valid()` |
| "Find X in Y" | `result in Y` or `result is None` |
| "Fix bug in X" | `tests_pass(X)` |
| "Generate X" | `schema.validate(result)` |
| "Transform X to Y" | `is_Y_format(result)` |

### Test Generator Agent

```python
@dataclass
class TestGeneratorInput:
    intent: str
    result: Any
    context: dict

@dataclass
class TestGeneratorOutput:
    test_code: str      # Python code that returns bool
    test_description: str
    confidence: float   # 0.0-1.0

TestGenerator: TestGeneratorInput → TestGeneratorOutput
```

### Example Tests

```python
# Intent: "Parse JSON config"
# Result: {"name": "app", "version": "1.0"}
def test_parse_json(result):
    return (
        isinstance(result, dict)
        and "name" in result
        and "version" in result
    )

# Intent: "Find TODO comments in code"
# Result: ["TODO: fix this", "TODO: refactor"]
def test_find_todos(result):
    return (
        isinstance(result, list)
        and all("TODO" in item for item in result)
    )

# Intent: "Fix auth bug"
# Result: <modified code>
def test_fix_auth(result):
    return run_auth_tests().all_passed
```

---

## Promise Tree Lifecycle

```
1. CONSTRUCTION (Forward)
   Root promise created
       │
       ├── Classify reality
       ├── If PROBABILISTIC: create child promises
       └── Propagate budgets down

2. RESOLUTION (Backward)
   Leaf promises resolve first
       │
       ├── Execute computation
       ├── Generate test
       ├── Run test
       └── Return result OR ground

3. COMBINATION (Backward continues)
   Parent combines child results
       │
       ├── All children resolved?
       ├── Combine into parent result
       ├── Generate parent test
       └── Return result OR ground

4. COMPLETION
   Root promise resolved
       │
       └── Final result OR ground
```

---

## Collapse Semantics

### When Collapse Happens

1. **Test failure**: Generated test returns False
2. **Budget exhaustion**: Entropy budget < threshold
3. **Depth exceeded**: Recursion depth > max_depth
4. **Chaotic classification**: Reality = CHAOTIC
5. **Exception**: Unexpected error during computation

### Collapse Behavior

```python
def collapse(promise: Promise[T], reason: str) -> T:
    """Collapse promise to Ground."""

    # Log for observability
    log_event(CollapsedPromise(
        intent=promise.intent,
        depth=promise.depth,
        reason=reason,
        ground_value=promise.ground
    ))

    # Mark state
    promise.state = PromiseState.COLLAPSED

    # Return Ground (the "Golden Parachute")
    return promise.ground
```

### Ground Selection

Ground must be chosen at promise creation:

```python
# Good: Meaningful Ground
promise = Promise(
    intent="Find user by email",
    ground=None,  # None is valid "not found"
    ...
)

# Good: Safe default
promise = Promise(
    intent="Parse config",
    ground=DEFAULT_CONFIG,  # Fallback config
    ...
)

# Bad: No Ground
promise = Promise(
    intent="Calculate total",
    ground=???,  # What's the safe default for a number?
    ...
)
```

---

## Relationship to Bootstrap Agents

| J-gent Concept | Bootstrap Agent | Relationship |
|----------------|-----------------|--------------|
| Promise tree | Compose | Promises compose into trees |
| Lazy expansion | Fix | Iterate only when needed |
| Test generation | Contradict | Test contradicts (validates) result |
| Collapse to Ground | Ground | Safety fallback |
| Result acceptance | Judge | Implicit in test passing |

---

## Anti-patterns

- **Groundless promises**: Creating promises without valid Ground
- **Test skipping**: Accepting results without validation
- **Silent collapse**: Collapsing without logging
- **Eager resolution**: Computing before tree is built
- **Infinite children**: Creating unbounded child promises

---

## See Also

- [reality.md](reality.md) - How classification affects promise expansion
- [stability.md](stability.md) - Budget and stability constraints
- [jit.md](jit.md) - How promises trigger JIT compilation
