# kgents-categorical-foundation

**Category Theory for the People** - Mathematical foundations made accessible.

Six standalone packages extracting the categorical infrastructure from kgents.
Use polynomial state machines, operads, sheaves, and more without understanding the math.

## Packages

| Package | Purpose | 10-Minute Test |
|---------|---------|----------------|
| `kgents-poly` | State machines with mode-dependent behavior | Can I build a traffic light? |
| `kgents-operad` | Composition grammar with laws | Can I define valid operations? |
| `kgents-sheaf` | Local-to-global coherence | Can I keep views in sync? |
| `kgents-laws` | Runtime law verification | Can I check my compositions? |
| `kgents-galois` | Semantic distance measurement | Can I compare text similarity? |
| `kgents-governance` | Universal law schemas | Can I define governance rules? |

## Quick Start

### kgents-poly: State Machines

```python
from kgents_poly import PolyAgent, from_function, sequential

# Lift functions to agents
double = from_function("double", lambda x: x * 2)
add_one = from_function("add_one", lambda x: x + 1)

# Compose with >> operator
pipeline = double >> add_one

# Run it
_, result = pipeline.invoke(("ready", "ready"), 10)
print(result)  # 21
```

### kgents-operad: Composition Grammar

```python
from kgents_operad import Operad, Operation, create_agent_operad
from kgents_poly import from_function

# Use the standard agent operad
operad = create_agent_operad()

# Compose using operad operations
double = from_function("double", lambda x: x * 2)
add_one = from_function("add_one", lambda x: x + 1)

composed = operad.compose("seq", double, add_one)
_, result = composed.invoke(("ready", "ready"), 10)
print(result)  # 21

# Verify laws
verification = operad.verify_law("seq_associativity", double, add_one, double)
print(verification.passed)  # True
```

### kgents-sheaf: Coherent Views

```python
from kgents_sheaf import Sheaf, View

# Multiple views of the same content
sheaf = Sheaf(
    name="document",
    views={
        "full": View("full", render_fn=lambda c: c),
        "summary": View("summary", render_fn=lambda c: c[:100] + "..."),
        "length": View("length", render_fn=lambda c: len(c)),
    },
)

# Render all views
content = "A very long document..."
rendered = sheaf.render_all(content)
print(rendered["length"])  # Length of content

# Verify coherence
result = sheaf.verify_coherence(content)
print(result.passed)  # True
```

### kgents-laws: Law Verification

```python
from kgents_laws import check_composition_laws, LawChecker
from kgents_poly import from_function, identity

# Quick verification
report = check_composition_laws(
    from_function("double", lambda x: x * 2),
    from_function("add_one", lambda x: x + 1),
    identity_agent=identity(),
)
print(report.summary)  # "All 3 law(s) verified successfully."

# Detailed checking
checker = LawChecker()
checker.add_agent(from_function("square", lambda x: x * x))
checker.add_agent(from_function("negate", lambda x: -x))
checker.set_identity(identity())

report = checker.verify_all()
if not report:
    for failure in report.failures:
        print(f"FAIL: {failure.explanation}")
```

### kgents-galois: Semantic Distance

```python
from kgents_galois import semantic_distance, get_fast_metric

# Simple usage
d = semantic_distance(
    "The cat sat on the mat",
    "A feline rested on the rug"
)
print(f"Distance: {d:.2f}")  # ~0.3 (related but not identical)

# For speed
metric = get_fast_metric()
d = metric.distance("hello world", "hi there world")
print(f"Fast distance: {d:.2f}")
```

### kgents-governance: Law Schemas

```python
from kgents_governance import (
    GovernanceLaw, LawSchema, verify_laws, gate_law
)

# Define governance laws
laws = [
    gate_law(
        domain="releases",
        name="Tests Required",
        description="Releases require passing tests",
        required_field="tests_passed",
    ),
    gate_law(
        domain="releases",
        name="Approval Required",
        description="Releases require approval",
        required_field="is_approved",
    ),
]

# Verify
report = verify_laws(laws, {
    "tests_passed": True,
    "is_approved": True,
})
print(report.summary)  # "All 2 law(s) passed."
```

## Design Principles

### 1. 10-Minute Accessibility (QA-1)

Every package can be used productively within 10 minutes without understanding
the underlying mathematics. The APIs are designed for practicality first.

### 2. Actionable Errors (QA-2)

When something goes wrong, error messages explain:
- WHAT failed
- WHY it failed
- HOW to fix it

```python
# Good error
ValueError: Operation 'seq' requires 2 agent(s), got 1. Signature: Agent[A,B] x Agent[B,C] -> Agent[A,C]

# Not this
TypeError: expected 2 positional arguments
```

### 3. Lighter Than Alternatives (QA-3)

These packages are intentionally minimal. If you find yourself fighting the
abstraction, the abstraction is wrong. File an issue.

### 4. Domain Independence (L4)

Core abstractions contain NO domain-specific logic. They work for:
- Software systems (agents, pipelines, workflows)
- Organizations (governance, policies)
- Games (state machines, rules)
- Scientific models (coherence, constraints)

### 5. Beautiful Code (QA-5)

The codebase is designed to be read. Each module has:
- Clear docstrings with examples
- Teaching notes (gotchas)
- Consistent structure

## Installation

```bash
# Install all packages
pip install kgents-poly kgents-operad kgents-sheaf kgents-laws kgents-galois kgents-governance

# Or install just what you need
pip install kgents-poly  # Just state machines
pip install kgents-laws  # Just law verification
```

## When to Use What

| You Want To... | Use This |
|----------------|----------|
| Build a state machine | `kgents-poly` |
| Define composition rules | `kgents-operad` |
| Keep multiple views in sync | `kgents-sheaf` |
| Verify algebraic laws | `kgents-laws` |
| Measure text similarity | `kgents-galois` |
| Define governance policies | `kgents-governance` |

## The Three-Layer Pattern

All kgents domains use the same three-layer structure:

```python
from kgents_poly import PolyAgent
from kgents_operad import Operad, Law
from kgents_sheaf import Sheaf, View

# 1. POLYNOMIAL: Define your state machine
class MyDomainAgent(PolyAgent[MyState, MyInput, MyOutput]):
    def transition(self, state, input) -> tuple[MyState, MyOutput]:
        # Your domain logic
        ...

# 2. OPERAD: Define your composition grammar
MY_OPERAD = Operad(
    name="MyDomain",
    operations={
        "then": Operation(...),
        "both": Operation(...),
    },
    laws=[
        Law("associativity", ...),
    ]
)

# 3. SHEAF: Define your coherence views
class MyDomainSheaf(Sheaf):
    views = {
        "summary": SummaryView(),
        "detail": DetailView(),
    }
    def glue(self, views) -> GlobalState:
        # Combine views into canonical form
        ...
```

Understanding one domain teaches you all domains.

## Philosophy

> "The patterns are general. They shouldn't be locked to one product.
> Category theory for the people."

These packages extract the mathematical foundations that make kgents work.
But you don't need to understand category theory to use them. The math is
an implementation detail - what matters is the practical API.

## Anti-Goals

Things these packages intentionally do NOT do:

- **Abstraction Tax**: Using the library should not be harder than rolling your own
- **Jargon Gatekeeping**: "Monad" and "Functor" appear in docs, not required reading
- **Framework Trap**: The structure should fit real problems, not vice versa
- **Dead Documentation**: Specs and implementation stay in sync

## License

MIT
