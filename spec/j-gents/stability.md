# Entropy Budgets & Stability Analysis

J-gents maintain stability through entropy budgets and the Chaosmonger.

---

## The Entropy Budget

### Definition

Computation freedom diminishes with recursion depth:

```python
def entropy_budget(depth: int) -> float:
    """Returns available computation budget at given depth."""
    return 1.0 / (depth + 1)
```

| Depth | Budget | Freedom Level |
|-------|--------|---------------|
| 0 | 1.00 | Full freedom (root) |
| 1 | 0.50 | Half freedom |
| 2 | 0.33 | Third freedom |
| 3 | 0.25 | Quarter freedom |
| 4+ | <0.20 | Typically below threshold |

### Chaos Threshold

When budget falls below threshold, force CHAOTIC classification:

```python
CHAOS_THRESHOLD = 0.1  # Default, configurable

if entropy_budget(depth) < CHAOS_THRESHOLD:
    return Reality.CHAOTIC  # Collapse to Ground
```

### Why Diminishing Returns?

1. **Prevents runaway recursion**: Deep trees consume unbounded resources
2. **Encourages early resolution**: Solve problems at higher levels when possible
3. **Natural pruning**: Complex sub-trees automatically collapse
4. **Safety guarantee**: System always terminates

---

## The Chaosmonger

Pre-Judge stability filter for JIT-compiled code.

### Purpose

Judge evaluates human values (taste, ethics, joy)—things that cannot be computed.
Chaosmonger evaluates algorithmic stability—things that CAN be computed.

```
GeneratedCode → Chaosmonger → [stable?] → Judge → [accept?] → Execute
                     ↓                      ↓
               [unstable]              [reject]
                     ↓                      ↓
                  Ground                 Ground
```

### Interface

```python
@dataclass
class StabilityInput:
    source_code: str        # Python source to analyze
    entropy_budget: float   # Available budget (0.0-1.0)
    allowed_imports: set[str]  # Whitelisted modules

@dataclass
class StabilityResult:
    is_stable: bool
    metrics: StabilityMetrics
    violations: list[str]  # Why unstable (if any)

@dataclass
class StabilityMetrics:
    cyclomatic_complexity: int
    branching_factor: int
    import_risk: float
    has_unbounded_recursion: bool
    estimated_runtime: str  # "O(1)", "O(n)", "O(n^2)", "unbounded"
```

---

## Stability Metrics

### 1. Cyclomatic Complexity

Number of independent paths through the code.

```python
def check_complexity(ast: AST, budget: float) -> bool:
    MAX_COMPLEXITY = 20
    threshold = budget * MAX_COMPLEXITY
    actual = calculate_cyclomatic(ast)
    return actual < threshold
```

| Budget | Max Complexity |
|--------|----------------|
| 1.0 | 20 |
| 0.5 | 10 |
| 0.33 | 6 |
| 0.25 | 5 |

### 2. Branching Factor

Expected number of child promises per node.

```python
def check_branching(ast: AST, budget: float) -> bool:
    MAX_BRANCHING = 5
    threshold = budget * MAX_BRANCHING
    actual = estimate_branching(ast)
    return actual < threshold
```

High branching = wide trees = resource exhaustion risk.

### 3. Import Risk

Risk score based on imported modules.

```python
IMPORT_RISK = {
    "typing": 0.0,      # Safe
    "dataclasses": 0.0,  # Safe
    "re": 0.1,          # Low risk
    "json": 0.1,        # Low risk
    "asyncio": 0.2,     # Medium risk
    "subprocess": 0.8,  # High risk
    "os": 0.7,          # High risk
    "requests": 0.6,    # Medium-high (network)
}

def check_imports(ast: AST, budget: float, allowed: set[str]) -> bool:
    MAX_IMPORT_RISK = 0.5
    threshold = budget * MAX_IMPORT_RISK

    imports = extract_imports(ast)
    for imp in imports:
        if imp not in allowed:
            return False  # Disallowed import
        risk += IMPORT_RISK.get(imp, 0.5)

    return risk < threshold
```

### 4. Unbounded Recursion Check

Detect patterns that never terminate.

```python
def has_unbounded_recursion(ast: AST) -> bool:
    """Check for while True without break, recursive calls without base case."""

    # Pattern 1: while True without break
    for node in ast.walk(ast):
        if isinstance(node, ast.While):
            if is_always_true(node.test) and not has_break(node):
                return True

    # Pattern 2: Recursive function without base case
    for func in get_functions(ast):
        if calls_self(func) and not has_base_case(func):
            return True

    return False
```

---

## Stability Pipeline

```
          ┌─────────────────────────┐
          │ 1. Import Whitelist     │
          │    Check allowed?       │
          └───────────┬─────────────┘
                      │
       ┌──────────────┴──────────────┐
       │ disallowed                  │ allowed
       ▼                             ▼
   UNSTABLE                 ┌─────────────────────────┐
   "Import X                │ 2. Cyclomatic Complexity│
    not allowed"            │    < budget × MAX?      │
                            └───────────┬─────────────┘
                                        │
                         ┌──────────────┴──────────────┐
                         │ exceeds                     │ within
                         ▼                             ▼
                    UNSTABLE               ┌─────────────────────────┐
                    "Complexity            │ 3. Branching Factor     │
                     too high"             │    < budget × MAX?      │
                                           └───────────┬─────────────┘
                                                       │
                                        ┌──────────────┴──────────────┐
                                        │ exceeds                     │ within
                                        ▼                             ▼
                                   UNSTABLE              ┌─────────────────────────┐
                                   "Branching            │ 4. Unbounded Recursion  │
                                    too wide"            │    detected?            │
                                                         └───────────┬─────────────┘
                                                                     │
                                                      ┌──────────────┴──────────────┐
                                                      │ yes                         │ no
                                                      ▼                             ▼
                                                 UNSTABLE                       STABLE
                                                 "Unbounded                     → Proceed
                                                  recursion"                      to Judge
```

---

## Relationship to Judge

| Concern | Handler | Why |
|---------|---------|-----|
| Cyclomatic complexity | Chaosmonger | Computable from AST |
| Import safety | Chaosmonger | Computable from AST |
| Unbounded recursion | Chaosmonger | Computable from AST |
| Runtime estimation | Chaosmonger | Heuristically computable |
| **Tasteful?** | **Judge** | Requires human judgment |
| **Ethical?** | **Judge** | Requires human judgment |
| **Joy-inducing?** | **Judge** | Requires human judgment |
| **Curated?** | **Judge** | Requires human judgment |

Chaosmonger is the **computable pre-filter**.
Judge is the **irreducible value function**.

---

## Configuration

```python
@dataclass
class StabilityConfig:
    # Thresholds (scaled by budget)
    max_cyclomatic_complexity: int = 20
    max_branching_factor: int = 5
    max_import_risk: float = 0.5

    # Absolute limits (not scaled)
    chaos_threshold: float = 0.1
    max_depth: int = 3

    # Import whitelist
    allowed_imports: set[str] = field(default_factory=lambda: {
        "typing", "dataclasses", "abc", "enum",
        "re", "json", "asyncio", "functools",
        "collections", "itertools", "operator"
    })

    # Blacklist (never allowed)
    forbidden_imports: set[str] = field(default_factory=lambda: {
        "os", "subprocess", "sys", "shutil",
        "socket", "requests", "urllib"
    })
```

---

## Examples

### Example 1: Stable Code

```python
# Intent: "Parse a log line"
# Budget: 0.5

@dataclass
class LogEntry:
    timestamp: str
    level: str
    message: str

def parse_log_line(line: str) -> LogEntry:
    parts = line.split(" ", 2)
    return LogEntry(
        timestamp=parts[0],
        level=parts[1],
        message=parts[2]
    )
```

Analysis:
- Imports: `dataclasses` (allowed, risk=0.0)
- Complexity: 1 (linear)
- Branching: 0 (no conditionals)
- Recursion: None

**Result**: STABLE

### Example 2: Unstable Code (Unbounded)

```python
# Intent: "Find all solutions"
# Budget: 0.25

def find_all(n: int) -> list:
    results = []
    while True:  # No termination!
        result = search()
        results.append(result)
    return results
```

Analysis:
- `while True` without break detected
- Unbounded recursion: YES

**Result**: UNSTABLE ("Unbounded recursion detected")

### Example 3: Unstable Code (Forbidden Import)

```python
# Intent: "Run shell command"
# Budget: 0.5

import subprocess  # FORBIDDEN

def run_cmd(cmd: str) -> str:
    return subprocess.check_output(cmd, shell=True)
```

Analysis:
- `subprocess` in forbidden_imports

**Result**: UNSTABLE ("Import 'subprocess' not allowed")

---

## Anti-patterns

- **Ignoring Chaosmonger**: Executing code without stability check
- **Budget inflation**: Artificially increasing budget to bypass limits
- **Whitelist expansion**: Adding dangerous imports to allowed list
- **Threshold lowering**: Setting chaos_threshold to 0 to disable

---

## See Also

- [reality.md](reality.md) - How stability affects classification
- [jit.md](jit.md) - Stability checks in JIT pipeline
- [README.md](README.md) - J-gents overview
