# Categorical Foundation Open Lab

Status: **production**

> *"The patterns are general. They shouldn't be locked to one product. Category theory for the people."*

---

## ⚠️ Implementation Directive

**This spec is a BUILD order, not a design document.**

When this PROTO_SPEC is consumed for regeneration:
- **Implement ALL laws (L1-L15)** — complete set
- **Implement ALL QAs (QA-1 through QA-8)** — complete set
- **All examples must run** — no placeholder code
- **Law verification must work** — behavioral, not just structural
- **Packages must be publishable** — real PyPI-ready quality

### Failure Conditions (Automatic Fail)

The system is **broken** if:

| Condition | Impact |
|-----------|--------|
| **FC-1** `pip install kgents-poly` fails | Unusable library |
| **FC-2** Hello World example doesn't work on copy-paste | L6 violated |
| **FC-3** Law verification produces false positives/negatives | Trust destroyed |
| **FC-4** Error messages lack fix suggestions | L8 violated |
| **FC-5** Documentation requires category theory to understand | Gatekeeping |
| **FC-6** Behavioral verification doesn't catch real bugs | L13 violated |
| **FC-7** TypeScript types missing or incomplete | Cross-ecosystem broken |

### Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | All 6 examples in `examples/` execute correctly | Yes |
| **QG-2** | `pytest` exits 0 | Yes |
| **QG-3** | `mypy` exits 0 | Yes |
| **QG-4** | Hello World < 60 seconds on fresh install | Yes |
| **QG-5** | Time to "Aha" (composition) < 5 minutes | Yes |
| **QG-6** | No category theory jargon in README first 500 words | Yes |
| **QG-7** | Behavioral law verification catches planted bug | Yes |
| **QG-8** | External developer can build Todo app in 30 minutes | Yes |

---

## The Bet

> *"If these patterns spread, governance itself becomes more rigorous and more human."*

The mathematical foundations discovered in kgents—polynomial functors, operad composition, sheaf coherence—are general patterns that apply to ANY system requiring rigorous composition. This pilot packages the categorical infrastructure as open-source tools that other developers can use to build principled systems.

**The radical claim**: Composition laws shouldn't be aspirational. They should be VERIFIED at runtime.

---

## Market Context: Why This Matters Now

### The Current Landscape (2025)

| Library | Philosophy | The Gap |
|---------|------------|---------|
| **Redux/RTK** | Flux pattern, unidirectional flow | No composition laws, boilerplate-heavy |
| **Zustand** | "Do whatever" simplicity | No verification, no structure |
| **XState** | Explicit state machines, Actor model | Steep curve, no law verification |
| **MobX** | Observable state | Magic proxies, hard to reason about |
| **Python transitions** | Lightweight FSM | No composition, no categorical laws |

**What's missing**: Nobody verifies composition at runtime. XState is explicit but doesn't check that `(f >> g) >> h === f >> (g >> h)`. Redux has structure but no mathematical foundation. **kgents-foundation fills this gap.**

### Academic Grounding (Standing on Giants)

This isn't speculation—it's production-ready implementation of established research:

| Research | Key Insight | Our Implementation |
|----------|-------------|-------------------|
| **Niu & Spivak, "Polynomial Functors" (Cambridge, 2024)** | Moore machines are special lenses; polynomial interfaces describe dynamical systems | `PolyAgent[S,A,B]` with mode-dependent directions |
| **Myers, "Categorical Systems Theory" (2024)** | Wiring diagrams compose dynamical systems | `WiringDiagram` class, `>>` composition |
| **Baez & Foley, "Operads for Complex Systems" (Royal Society, 2021)** | Operads give syntax; algebras give semantics | `Operad` with `Operation`, `Law`, `enumerate()` |
| **Goguen, "Sheaves and Distributed Systems" (1992-2024)** | Coherent collections of observations; gluing is unique | `Sheaf` with `verify_coherence()`, `glue()` |
| **MSFP 2024 Workshop** | Operads for DSL composition (DARPA V-SPELLS) | Domain-independent operad templates |

**The innovation**: Taking research locked in papers and making it `pip install`-able.

### Competitive Positioning

```
                    Simplicity
                        ↑
                        │
           Zustand ●    │
                        │         ● kgents-foundation
                        │           (simple surface,
                        │            verified composition)
        ─────────────────┼─────────────────────→ Rigor
                        │
              Redux ●   │    ● XState
           (boilerplate)│  (steep curve)
                        │
```

**Target**: Upper-right quadrant. Simple API, verified laws.

---

## Personality Tag

*Pedagogical infrastructure. It teaches by enabling. The goal is not to explain category theory, but to let people USE category theory without knowing they're using it.*

*"Modes and valid actions"* — not "positions and directions."
*"Agents that compose"* — not "morphisms in a category."
*"Laws that catch bugs"* — not "categorical axioms."

---

## Objectives

1. Package **PolyAgent, Operad, and Sheaf** as standalone, documented, tested libraries
2. Provide **domain-independent templates** that instantiate the three-layer pattern for any problem
3. Create **behavioral law verification** that catches composition bugs at runtime
4. Build **composable building blocks** that make "doing it right" easier than "doing it wrong"
5. Establish **reference implementations** demonstrating patterns in concrete domains
6. Publish to **PyPI with TypeScript contracts** for cross-ecosystem adoption
7. Write **academic paper** establishing intellectual property and credibility

---

## Epistemic Commitments

- **Composition is primary**. The Minimal Output Principle: single outputs that compose, not aggregates.
- **Laws are enforced, not suggested**. `verify_*` functions RUN tests; violations fail hard.
- **Behavioral over structural**. Don't just check types match—run inputs through both orderings.
- **Abstractions pay for themselves**. If it doesn't make code simpler AND more correct, remove it.
- **Documentation IS specification**. Delete impl, rebuild from docs, get isomorphic code.
- **Joy in use**. If developers don't enjoy it, the abstraction failed. (Principle 4)
- **Jargon is failure**. If a non-mathematician can't understand the README, we failed.

---

## Laws

### Core Laws (L1-L5)

- **L1 Law Verification Law**: Any PolyAgent, Operad, or Sheaf must verify its categorical laws at instantiation time. No unchecked composition.

- **L2 Minimal Output Law**: Library functions return single values, not arrays. Composition happens at call site.

- **L3 Composition Transparency Law**: When composition fails, the error message explains WHICH law was violated, WHERE it diverged, and HOW to fix it.

- **L4 Domain Independence Law**: Core abstractions contain NO domain-specific logic. Domain operads extend, not modify.

- **L5 Documentation Regeneration Law**: The spec must be sufficiently detailed that deleting `src/` and regenerating from docs produces isomorphic code.

### DevEx Laws (L6-L12)

- **L6 First Impression Law**: Hello World works in < 60 seconds. Composition "Aha" in < 5 minutes. No jargon in first 500 words.

- **L7 Batteries-Included Law**: `from_function`, `sequential`, `parallel`, `identity`, `verify_identity`, `verify_associativity`, `jaccard_distance`, `gate_law` all work out of the box.

- **L8 Error Message Law**: Every error includes: what failed, expected vs actual, where it diverged, how to fix, documentation link.

- **L9 Progressive Disclosure Law**: Layer N never requires Layer N+1. README → Cookbook → API → Theory → Paper.

- **L10 Visual Impact Law**: Landing page shows before/after transformation. Pain → Joy in one glance.

- **L11 Principled Build Law**: `pip install kgents-foundation` works. `pytest` passes. `mypy` passes.

- **L12 Package Structure Law**: Monorepo with clear separation. Each package independently installable.

### Verification Laws (L13-L15)

- **L13 Behavioral Verification Law**: Law checks MUST run concrete inputs through both orderings and compare outputs. Structural checking alone is insufficient.

```python
# STRUCTURAL (weak) - what we had
def verify_associativity_structural(f, g, h):
    left = (f >> g) >> h
    right = f >> (g >> h)
    return left.name == right.name  # Just checks structure

# BEHAVIORAL (strong) - what we need
def verify_associativity_behavioral(f, g, h, test_inputs):
    left = (f >> g) >> h
    right = f >> (g >> h)
    for state, inp in test_inputs:
        _, left_out = left.invoke(state, inp)
        _, right_out = right.invoke(state, inp)
        if left_out != right_out:
            raise AssociativityError(
                input=inp,
                left_result=left_out,
                right_result=right_out,
                step="behavioral verification"
            )
```

- **L14 Lossy View Coherence Law**: Sheaf views are classified as "complete" (round-trip possible) or "lossy" (information lost). Coherence means: complete views agree on overlap; lossy views don't contradict.

```python
class View:
    name: str
    render_fn: Callable
    lossy: bool = False  # NEW: explicit lossiness

class Sheaf:
    def verify_coherence(self, content):
        # Complete views: verify round-trip
        # Lossy views: verify no contradiction (weaker check)
        ...
```

- **L15 Bug Detection Law**: Law verification must catch at least one bug that would otherwise be silent. Tests include a "planted bug" that associativity check must detect.

---

## Qualitative Assertions

- **QA-1** A developer should **use PolyAgent in 10 minutes** without understanding polynomial functors.
- **QA-2** Law violations should produce **actionable error messages**: "Associativity failed at input X: left produced 'foo', right produced 'bar'."
- **QA-3** The library should feel **lighter than alternatives**: fewer lines than Redux for equivalent functionality.
- **QA-4** A non-mathematician should **build a governance system** using templates without reading theory.
- **QA-5** The codebase should be **beautiful to read**. If the implementation isn't elegant, the abstraction is wrong.
- **QA-6** External developers should **adopt within 6 months** for non-kgents projects.
- **QA-7** The Generative Test should **pass**: delete impl, regenerate from spec, get isomorphic code.
- **QA-8** Academic paper should be **publishable** at a venue like MSFP or ICFP.

---

## Anti-Success (Failure Modes)

The system fails if:

- **Abstraction tax**: Using the library is harder than rolling your own
- **Jargon gatekeeping**: "Monad" or "functor" in user-facing docs
- **Framework trap**: Structure that doesn't fit real problems
- **Dead documentation**: Specs diverge from implementation
- **Cleverness over clarity**: Code shows off math instead of solving problems
- **Structural-only verification**: Law checks that don't catch real bugs
- **Python-only**: No TypeScript ecosystem support

---

## Package Ecosystem

This pilot EXTRACTS from kgents and PUBLISHES independently:

| Package | Purpose | Key Exports |
|---------|---------|-------------|
| `kgents-poly` | Mode-dependent state machines | `PolyAgent`, `from_function`, `stateful`, `sequential`, `parallel`, `identity` |
| `kgents-operad` | Composition grammar with verified laws | `Operad`, `Operation`, `Law`, `create_agent_operad`, `OperadRegistry` |
| `kgents-sheaf` | Local→global coherence | `Sheaf`, `View`, `SheafVerification`, `Coherent` |
| `kgents-laws` | Runtime law verification | `verify_identity`, `verify_associativity`, `verify_coherence`, `LawVerification` |
| `kgents-galois` | Semantic distance measurement | `semantic_distance`, `jaccard_distance`, `galois_loss` |
| `kgents-governance` | Universal law schemas | `gate_law`, `threshold_law`, `GovernanceLaw`, `Constitution` |
| `kgents-foundation` | Meta-package (all of the above) | Everything |
| `@kgents/contracts` | TypeScript type definitions | All types for cross-ecosystem |

### Mental Model Translation

For documentation, translate categorical concepts to practical language:

| Category Theory | User-Facing Term | Example |
|-----------------|------------------|---------|
| Position/Object | **Mode** | "idle", "loading", "error" |
| Direction/Morphism | **Valid action** | "start", "cancel", "retry" |
| Composition | **Chaining** | `agent1 >> agent2` |
| Identity | **Pass-through** | `identity()` agent |
| Associativity | **Order doesn't matter** | `(a >> b) >> c` same as `a >> (b >> c)` |
| Sheaf | **Multiple views, one truth** | Summary, detail, outline of same doc |
| Gluing | **Combining views** | Reconstruct whole from parts |
| Operad | **Composition grammar** | What operations are legal |

---

## Three-Layer Pattern

Every domain instantiates this pattern:

```python
from kgents_poly import PolyAgent, stateful
from kgents_operad import Operad, Operation, Law
from kgents_sheaf import Sheaf, View
from kgents_laws import verify_identity, verify_associativity

# ════════════════════════════════════════════════════════════════
# LAYER 1: POLYNOMIAL AGENT
# Define your domain's state machine with mode-dependent behavior
# ════════════════════════════════════════════════════════════════

task_agent = stateful(
    name="task",
    states=frozenset({"todo", "in_progress", "done", "blocked"}),
    transition_fn=lambda state, action: {
        ("todo", "start"): ("in_progress", "Task started"),
        ("in_progress", "complete"): ("done", "Task completed"),
        ("in_progress", "block"): ("blocked", "Task blocked"),
        ("blocked", "unblock"): ("in_progress", "Task unblocked"),
    }.get((state, action), (state, f"Invalid: {action} in {state}")),
    directions_fn=lambda state: {
        "todo": frozenset({"start"}),
        "in_progress": frozenset({"complete", "block"}),
        "blocked": frozenset({"unblock"}),
        "done": frozenset(),  # Terminal state
    }[state]
)

# ════════════════════════════════════════════════════════════════
# LAYER 2: OPERAD
# Define your domain's composition grammar
# ════════════════════════════════════════════════════════════════

TASK_OPERAD = Operad(
    name="TaskOperad",
    operations={
        "seq": Operation(
            name="seq",
            arity=2,
            signature="Task[A,B] x Task[B,C] -> Task[A,C]",
            compose=lambda a, b: a >> b,
            description="Sequential: complete first, then second"
        ),
        "par": Operation(
            name="par",
            arity=2,
            signature="Task[A,B] x Task[A,C] -> Task[A,(B,C)]",
            compose=parallel,
            description="Parallel: both tasks on same input"
        ),
        "gate": Operation(
            name="gate",
            arity=2,
            signature="Pred[A] x Task[A,B] -> Task[A,B|None]",
            compose=lambda pred, task: ...,  # Gate implementation
            description="Conditional: run task only if predicate passes"
        ),
    },
    laws=[
        Law(
            name="seq_associativity",
            equation="seq(seq(a,b),c) = seq(a,seq(b,c))",
            verify=lambda a, b, c: verify_associativity(a, b, c),
        ),
    ]
)

# ════════════════════════════════════════════════════════════════
# LAYER 3: SHEAF
# Define your domain's coherence views
# ════════════════════════════════════════════════════════════════

task_sheaf = Sheaf(
    name="task_views",
    views={
        "full": View("full", render_fn=lambda t: t, lossy=False),
        "summary": View("summary", render_fn=lambda t: t[:50], lossy=True),
        "status": View("status", render_fn=lambda t: t.split()[0], lossy=True),
    },
    canonical_view="full",
    glue_fn=lambda views: views["full"],
)

# ════════════════════════════════════════════════════════════════
# USAGE: Compose, verify, enjoy
# ════════════════════════════════════════════════════════════════

# Compose tasks
pipeline = task_agent >> logging_agent >> notification_agent

# Verify laws (behavioral!)
verify_identity(task_agent, test_inputs=[("todo", "start")])
verify_associativity(
    task_agent, logging_agent, notification_agent,
    test_inputs=[(("todo", "ready", "ready"), "start")]
)

# Check view coherence
result = task_sheaf.verify_coherence("Task: Implement feature X")
assert result.passed
```

---

## Reference Implementations

### 1. Todo App (Trivial) — 15 minutes to understand

**Purpose**: Prove the pattern works for the simplest case.

```python
# examples/04_todo_app.py
"""
Todo App using kgents-foundation.

This demonstrates the three-layer pattern for a familiar domain.
Time to understand: ~15 minutes.
"""

from kgents_poly import stateful, from_function, sequential
from kgents_operad import Operad, Operation
from kgents_sheaf import Sheaf, View
from kgents_laws import verify_identity, verify_associativity

# ─────────────────────────────────────────────────────────────────
# DOMAIN: Todo items
# ─────────────────────────────────────────────────────────────────

@dataclass
class Todo:
    id: str
    title: str
    status: str  # "pending", "done", "archived"

# ─────────────────────────────────────────────────────────────────
# LAYER 1: PolyAgent for todo state
# ─────────────────────────────────────────────────────────────────

todo_agent = stateful(
    name="todo",
    states=frozenset({"pending", "done", "archived"}),
    transition_fn=lambda state, action: {
        ("pending", "complete"): ("done", "Completed!"),
        ("pending", "archive"): ("archived", "Archived"),
        ("done", "archive"): ("archived", "Archived"),
        ("done", "reopen"): ("pending", "Reopened"),
    }.get((state, action), (state, f"Cannot {action} when {state}")),
    directions_fn=lambda state: {
        "pending": frozenset({"complete", "archive"}),
        "done": frozenset({"archive", "reopen"}),
        "archived": frozenset(),  # Terminal
    }[state]
)

# ─────────────────────────────────────────────────────────────────
# LAYER 2: Operad for CRUD operations
# ─────────────────────────────────────────────────────────────────

TODO_OPERAD = Operad(
    name="TodoOperad",
    operations={
        "create": Operation("create", 0, "() -> Todo", lambda: Todo(...)),
        "update": Operation("update", 1, "Todo -> Todo", lambda t: ...),
        "seq": Operation("seq", 2, "A x A -> A", sequential),
    }
)

# ─────────────────────────────────────────────────────────────────
# LAYER 3: Sheaf for list/detail views
# ─────────────────────────────────────────────────────────────────

todo_sheaf = Sheaf(
    name="todo_views",
    views={
        "list": View("list", lambda todos: [t.title for t in todos], lossy=True),
        "detail": View("detail", lambda todos: todos, lossy=False),
        "counts": View("counts", lambda todos: {
            "pending": sum(1 for t in todos if t.status == "pending"),
            "done": sum(1 for t in todos if t.status == "done"),
        }, lossy=True),
    }
)

# ─────────────────────────────────────────────────────────────────
# VERIFICATION: Laws hold
# ─────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # Identity law
    verify_identity(todo_agent, test_inputs=[("pending", "complete")])
    print("✓ Identity law verified")

    # Associativity
    logger = from_function("log", lambda x: (print(x), x)[1])
    notifier = from_function("notify", lambda x: f"[NOTIFY] {x}")
    verify_associativity(todo_agent, logger, notifier)
    print("✓ Associativity law verified")

    # Sheaf coherence
    todos = [Todo("1", "Buy milk", "pending"), Todo("2", "Call mom", "done")]
    result = todo_sheaf.verify_coherence(todos)
    print(f"✓ Sheaf coherence: {result}")
```

### 2. Document Editor (Moderate) — 30 minutes to understand

**Purpose**: Prove the pattern works for collaborative editing with conflict resolution.

```python
# examples/05_document_editor.py
"""
Collaborative Document Editor using kgents-foundation.

Demonstrates sheaf coherence for multiple views of same document.
Time to understand: ~30 minutes.
"""

# ... (full implementation showing outline/prose/diff views)
# Key insight: Sheaf gluing ensures views stay synchronized
```

### 3. Governance System (Complex) — 1 hour to understand

**Purpose**: Prove the pattern works for constitutional scoring and trust gradients.

```python
# examples/06_governance.py
"""
Constitutional Governance using kgents-foundation.

Demonstrates:
- PolyAgent for trust states (untrusted → trusted → superseding)
- Operad for governance operations (propose, vote, ratify)
- Sheaf for multiple stakeholder views
- gate_law for ethical floors
- threshold_law for drift detection

Time to understand: ~1 hour.
"""

from kgents_governance import gate_law, threshold_law, Constitution

# Gate: ETHICAL score < 0.6 → total = 0 (hard floor)
ethical_gate = gate_law("ethical", threshold=0.6, on_fail=0.0)

# Threshold: DRIFT > 0.4 → warn (soft limit)
drift_alert = threshold_law("drift", threshold=0.4, action="warn")

# Constitution combines laws
constitution = Constitution(
    name="kgents-governance",
    laws=[ethical_gate, drift_alert],
    amendment_threshold=0.8,  # 80% agreement to amend
)
```

---

## DevEx Consumption Narrative (Shock & Awe Strategy)

> *"In 60 seconds, the developer goes from skeptical to converted."*

### The Hero Journey (First 10 Minutes)

```
MINUTE 0: "What is this?"
  └─→ Landing page: "State machines that compose. Verified at runtime."
  └─→ No jargon. No "category theory." Just: "Make state easier."
  └─→ Visual: Before (50-line if/elif) → After (5-line stateful)

MINUTE 1: "Let me try it."
  └─→ pip install kgents-poly
  └─→ Copy-paste from README. It works. First try.

MINUTE 2: "Okay, it runs. So what?"
  └─→ The "Aha" moment: Compose two agents with >>
  └─→ See them work together without glue code
  └─→ Realize: "This is cleaner than XState"

MINUTE 3: "That's clean. But does it scale?"
  └─→ Show law verification catching a REAL bug
  └─→ Error message tells you EXACTLY what's wrong:
      "Associativity failed at input 'start':
       (f >> g) >> h produced 'Task started [logged]'
       f >> (g >> h) produced 'Task started[logged]' (missing space)
       Fix: Check that 'g' produces consistent output"

MINUTE 5: "I want to use this."
  └─→ Integration guide shows real patterns
  └─→ TypeScript types: npm install @kgents/contracts
  └─→ Copy the Todo App example, modify for your domain

MINUTE 10: "I'm building something."
  └─→ Developer is productive without reading theory
  └─→ Theory docs exist for the curious, never required
```

### The Planted Bug Test

Every release MUST include a test that:
1. Creates an intentionally buggy agent (impure function with side effects)
2. Runs `verify_associativity` on it
3. EXPECTS the verification to fail and catch the bug
4. Produces an actionable error message

```python
# tests/test_planted_bug.py
def test_behavioral_verification_catches_planted_bug():
    """
    This test PROVES our law verification catches real bugs.

    The bug: counter has side effects, violating associativity.
    """
    call_count = [0]  # Mutable state = bug

    def buggy_fn(x):
        call_count[0] += 1
        return x + call_count[0]  # Non-deterministic!

    buggy = from_function("buggy", buggy_fn)
    clean_a = from_function("a", lambda x: x * 2)
    clean_b = from_function("b", lambda x: x + 1)

    # This MUST fail
    with pytest.raises(AssociativityError) as exc_info:
        verify_associativity(
            clean_a, buggy, clean_b,
            test_inputs=[(("ready", "ready", "ready"), 10)]
        )

    # Error message MUST be actionable
    assert "left produced" in str(exc_info.value)
    assert "right produced" in str(exc_info.value)
    assert "fix" in str(exc_info.value).lower()
```

---

## L7 Batteries-Included Law (Complete Examples)

Out of the box, these MUST work with zero configuration:

```python
# ═══════════════════════════════════════════════════════════════════
# 1. Create an agent from a function (5 seconds)
# ═══════════════════════════════════════════════════════════════════
from kgents_poly import from_function

double = from_function("double", lambda x: x * 2)
_, result = double.invoke("ready", 21)
assert result == 42

# ═══════════════════════════════════════════════════════════════════
# 2. Compose agents (10 seconds)
# ═══════════════════════════════════════════════════════════════════
add_one = from_function("add_one", lambda x: x + 1)
pipeline = double >> add_one
_, result = pipeline.invoke(("ready", "ready"), 10)
assert result == 21  # (10 * 2) + 1

# ═══════════════════════════════════════════════════════════════════
# 3. Run in parallel (15 seconds)
# ═══════════════════════════════════════════════════════════════════
from kgents_poly import parallel
both = parallel(double, add_one)
_, result = both.invoke(("ready", "ready"), 5)
assert result == (10, 6)

# ═══════════════════════════════════════════════════════════════════
# 4. Create stateful agent (20 seconds)
# ═══════════════════════════════════════════════════════════════════
from kgents_poly import stateful

traffic_light = stateful(
    name="traffic_light",
    states=frozenset({"red", "green", "yellow"}),
    transition_fn=lambda state, _: {
        "red": ("green", "GO"),
        "green": ("yellow", "SLOW"),
        "yellow": ("red", "STOP"),
    }[state]
)
state, output = traffic_light.invoke("red", "tick")
assert state == "green" and output == "GO"

# ═══════════════════════════════════════════════════════════════════
# 5. Verify laws at runtime (25 seconds)
# ═══════════════════════════════════════════════════════════════════
from kgents_laws import verify_identity, verify_associativity

verify_identity(double, test_inputs=[("ready", 10), ("ready", 0)])
verify_associativity(
    double, add_one, from_function("negate", lambda x: -x),
    test_inputs=[(("ready", "ready", "ready"), 5)]
)
print("✓ All laws verified behaviorally")

# ═══════════════════════════════════════════════════════════════════
# 6. Measure semantic distance (30 seconds)
# ═══════════════════════════════════════════════════════════════════
from kgents_galois import jaccard_distance, semantic_distance

j_dist = jaccard_distance("hello world", "hello there")
assert 0.4 < j_dist < 0.6  # ~50% different

s_dist = semantic_distance("The cat sat", "A feline rested")
assert s_dist < 0.3  # Semantically similar

# ═══════════════════════════════════════════════════════════════════
# 7. Define governance laws (35 seconds)
# ═══════════════════════════════════════════════════════════════════
from kgents_governance import gate_law, threshold_law

# Hard floor: ETHICAL < 0.6 → zero total score
ethical_gate = gate_law("ethical", threshold=0.6, on_fail=0.0)
assert ethical_gate.apply({"ethical": 0.5, "other": 0.9}) == 0.0
assert ethical_gate.apply({"ethical": 0.7, "other": 0.9}) > 0

# Soft limit: DRIFT > 0.4 → warning
drift_alert = threshold_law("drift", threshold=0.4, action="warn")
result = drift_alert.check(0.5)
assert result.warning == "drift exceeded threshold (0.5 > 0.4)"

# ═══════════════════════════════════════════════════════════════════
# 8. Create and verify sheaf (40 seconds)
# ═══════════════════════════════════════════════════════════════════
from kgents_sheaf import Sheaf, View

doc_sheaf = Sheaf(
    name="document",
    views={
        "full": View("full", lambda d: d, lossy=False),
        "preview": View("preview", lambda d: d[:100], lossy=True),
        "word_count": View("word_count", lambda d: len(d.split()), lossy=True),
    },
    canonical_view="full",
)

content = "This is a test document with multiple words."
result = doc_sheaf.verify_coherence(content)
assert result.passed
print(f"✓ Sheaf coherent: {result.checked_views}")
```

---

## L8 Error Message Law (Complete Examples)

Every error MUST be actionable:

```python
# ═══════════════════════════════════════════════════════════════════
# IDENTITY ERROR
# ═══════════════════════════════════════════════════════════════════

class IdentityError(Exception):
    """Raised when identity law is violated."""

    def __init__(
        self,
        agent_name: str,
        test_input: Any,
        with_id_result: Any,
        without_id_result: Any,
        side: str,  # "left" or "right"
    ):
        self.message = f"""
Identity Law Violated: {agent_name}

What failed:
  The identity law requires: Id >> f ≡ f ≡ f >> Id

Test input: {test_input!r}

Expected vs Actual:
  f alone produced: {without_id_result!r}
  {side} identity produced: {with_id_result!r}

How to fix:
  1. Ensure your agent is a pure function (no side effects)
  2. Check that invoke() doesn't modify state unexpectedly
  3. Verify the identity() agent is truly a pass-through

Documentation:
  https://kgents.dev/laws/identity
"""
        super().__init__(self.message)

# ═══════════════════════════════════════════════════════════════════
# ASSOCIATIVITY ERROR
# ═══════════════════════════════════════════════════════════════════

class AssociativityError(Exception):
    """Raised when associativity law is violated."""

    def __init__(
        self,
        agents: tuple[str, str, str],
        test_input: Any,
        left_first_result: Any,
        right_first_result: Any,
        divergence_step: int | None = None,
    ):
        f, g, h = agents
        self.message = f"""
Associativity Law Violated: {f} >> {g} >> {h}

What failed:
  The associativity law requires: (f >> g) >> h ≡ f >> (g >> h)

Test input: {test_input!r}

Expected vs Actual:
  (f >> g) >> h produced: {left_first_result!r}
  f >> (g >> h) produced: {right_first_result!r}

{f"Diverged at step: {divergence_step}" if divergence_step else ""}

How to fix:
  1. Check that '{g}' is a pure function (most common cause)
  2. Ensure no agent has hidden mutable state
  3. Verify intermediate outputs are deterministic
  4. If using external I/O, wrap in effect handler

Documentation:
  https://kgents.dev/laws/associativity
"""
        super().__init__(self.message)

# ═══════════════════════════════════════════════════════════════════
# COHERENCE ERROR
# ═══════════════════════════════════════════════════════════════════

class CoherenceError(Exception):
    """Raised when sheaf coherence is violated."""

    def __init__(
        self,
        sheaf_name: str,
        conflicts: list[str],
        checked_views: list[str],
    ):
        self.message = f"""
Sheaf Coherence Violated: {sheaf_name}

What failed:
  Views should derive from the same canonical content.

Checked views: {checked_views}
Conflicts found: {len(conflicts)}

Conflicts:
{chr(10).join(f"  • {c}" for c in conflicts)}

How to fix:
  1. Ensure all views render from the same canonical source
  2. For lossy views, verify they don't contradict complete views
  3. Check that glue_fn correctly reconstructs from parts
  4. If views have different update rates, synchronize them

Documentation:
  https://kgents.dev/laws/coherence
"""
        super().__init__(self.message)
```

---

## Package Structure

```
kgents-foundation/
├── README.md                    # Hero journey (5-min quickstart)
├── pyproject.toml               # Modern Python packaging (PEP 621)
├── LICENSE                      # MIT
│
├── docs/
│   ├── index.md                 # Landing page
│   ├── quickstart.md            # 5-minute guide
│   ├── cookbook.md              # Common patterns
│   ├── api/
│   │   ├── poly.md              # PolyAgent API
│   │   ├── operad.md            # Operad API
│   │   ├── sheaf.md             # Sheaf API
│   │   ├── laws.md              # Law verification API
│   │   ├── galois.md            # Semantic distance API
│   │   └── governance.md        # Governance law API
│   └── theory/                  # For the curious (never required)
│       ├── polynomial-functors.md    # Cites Niu & Spivak
│       ├── operads.md                # Cites Baez & Foley
│       ├── sheaves.md                # Cites Goguen
│       └── references.md             # Full bibliography
│
├── kgents_poly/
│   ├── __init__.py              # Public API
│   ├── core.py                  # PolyAgent implementation
│   ├── constructors.py          # from_function, stateful, identity, constant
│   ├── composition.py           # sequential, parallel, WiringDiagram
│   └── py.typed                 # PEP 561 marker
│
├── kgents_operad/
│   ├── __init__.py              # Public API
│   ├── core.py                  # Operad, Operation, Law
│   ├── universal.py             # AGENT_OPERAD, create_agent_operad
│   ├── registry.py              # OperadRegistry
│   └── py.typed
│
├── kgents_sheaf/
│   ├── __init__.py              # Public API
│   ├── core.py                  # Sheaf, View, SheafVerification
│   ├── coherent.py              # Coherent convenience type
│   ├── factories.py             # identity_view, slice_view, transform_view
│   └── py.typed
│
├── kgents_laws/                 # NEW PACKAGE
│   ├── __init__.py              # verify_identity, verify_associativity, verify_coherence
│   ├── core.py                  # LawVerification, LawStatus
│   ├── identity.py              # Identity law verification (behavioral)
│   ├── associativity.py         # Associativity law verification (behavioral)
│   ├── coherence.py             # Sheaf coherence verification
│   ├── errors.py                # IdentityError, AssociativityError, CoherenceError
│   └── py.typed
│
├── kgents_galois/               # NEW PACKAGE
│   ├── __init__.py              # semantic_distance, jaccard_distance, galois_loss
│   ├── core.py                  # Distance metric implementations
│   ├── jaccard.py               # Jaccard similarity/distance
│   ├── semantic.py              # Embedding-based semantic distance
│   ├── galois.py                # Galois loss for compression quality
│   └── py.typed
│
├── kgents_governance/           # NEW PACKAGE
│   ├── __init__.py              # gate_law, threshold_law, GovernanceLaw, Constitution
│   ├── core.py                  # GovernanceLaw base class
│   ├── gate.py                  # GateLaw (hard floor)
│   ├── threshold.py             # ThresholdLaw (soft limit)
│   ├── constitution.py          # Constitution (law composition)
│   └── py.typed
│
├── examples/
│   ├── 01_hello_world.py        # Simplest possible (< 20 lines)
│   ├── 02_composition.py        # Chaining with >>
│   ├── 03_law_verification.py   # Catching bugs
│   ├── 04_todo_app.py           # Real-world: Todo state machine
│   ├── 05_document_editor.py    # Real-world: Collaborative editing
│   └── 06_governance.py         # Real-world: Constitutional scoring
│
├── tests/
│   ├── test_poly.py
│   ├── test_operad.py
│   ├── test_sheaf.py
│   ├── test_laws.py
│   ├── test_galois.py
│   ├── test_governance.py
│   ├── test_planted_bug.py      # MUST catch intentional bug
│   └── test_integration.py      # End-to-end
│
└── typescript/                  # TypeScript ecosystem
    ├── package.json             # @kgents/contracts
    ├── tsconfig.json
    └── src/
        ├── index.ts
        ├── poly.ts              # PolyAgent types
        ├── operad.ts            # Operad types
        ├── sheaf.ts             # Sheaf types
        └── governance.ts        # Governance types
```

---

## Publication Roadmap

### Phase 1: Internal Validation (Week 1-2)

- [ ] All 6 examples run correctly
- [ ] All tests pass (including planted bug test)
- [ ] mypy clean
- [ ] Documentation renders
- [ ] Internal developer builds Todo app in < 30 minutes

### Phase 2: PyPI Publication (Week 3)

- [ ] `pip install kgents-foundation` works
- [ ] Individual packages installable (`kgents-poly`, etc.)
- [ ] GitHub releases with semantic versioning
- [ ] PyPI project page with README

### Phase 3: TypeScript Ecosystem (Week 4)

- [ ] `npm install @kgents/contracts` works
- [ ] Types match Python exactly
- [ ] Example showing Python backend + TypeScript frontend

### Phase 4: External Validation (Week 5-8)

- [ ] One external developer builds non-trivial project
- [ ] Feedback incorporated
- [ ] Blog post / announcement

### Phase 5: Academic Publication (Month 3-6)

- [ ] Paper draft: "Polynomial Functors for Practical Agent Systems"
- [ ] Target venue: MSFP, ICFP, or similar
- [ ] Establishes intellectual property
- [ ] Builds credibility for enterprise adoption

---

## Canary Success Criteria

- [ ] Developer unfamiliar with category theory **builds working state machine** in < 30 minutes
- [ ] Law verification **catches planted bug** that would be silent otherwise
- [ ] Library is **smaller than alternatives**: fewer LOC than Redux for equivalent
- [ ] **One external project** adopts within 6 months
- [ ] Documentation passes **Generative Test**: delete `src/`, rebuild from docs, isomorphic
- [ ] **Academic paper** accepted at recognized venue
- [ ] **TypeScript types** enable full-stack adoption

---

## Generation Checklist (For Sub-Agents)

Before claiming this pilot is complete, verify:

**DevEx Fundamentals**:
- [ ] Hello World < 60s: Copy-paste from README works immediately
- [ ] Composition works: `>>` operator chains agents correctly
- [ ] **Behavioral** law verification works: catches real bugs, not just structural
- [ ] Errors are actionable: Every error has what/expected/actual/fix/link

**Package Quality**:
- [ ] No jargon in README: First 500 words use plain language
- [ ] Examples run: All 6 in `examples/` execute correctly
- [ ] Tests pass: `pytest` exits 0
- [ ] **Planted bug test** passes: verification catches intentional bug
- [ ] Types complete: `mypy` exits 0
- [ ] Docs build: Documentation renders correctly

**Batteries-Included**:
- [ ] `from_function` works: Lift any function to agent
- [ ] `stateful` works: Mode-dependent state machines
- [ ] `sequential` works: Chain agents with `>>`
- [ ] `parallel` works: Run agents on same input
- [ ] `identity` works: Pass-through agent
- [ ] `verify_identity` works: **Behavioral** identity checking
- [ ] `verify_associativity` works: **Behavioral** associativity checking
- [ ] `jaccard_distance` works: Basic semantic distance
- [ ] `semantic_distance` works: Embedding-based distance
- [ ] `gate_law` works: Hard floor enforcement
- [ ] `threshold_law` works: Soft limit with warning
- [ ] `Sheaf.verify_coherence` works: With lossy/complete view distinction

**Ecosystem**:
- [ ] PyPI: `pip install kgents-foundation` works
- [ ] npm: `npm install @kgents/contracts` works
- [ ] GitHub: Releases with semantic versioning

**Shock & Awe Moment**:
- [ ] Visual before/after: Landing page shows transformation
- [ ] Progressive disclosure: Theory available but never required
- [ ] "I want to use this": Developer feels pull by minute 5
- [ ] External adoption: At least one non-kgents project

---

## Mathematical Grounding (For Theory Appendix)

This pilot IS the mathematical grounding made accessible:

| Abstraction | Academic Source | Our Implementation | User-Facing Name |
|-------------|-----------------|-------------------|------------------|
| **Polynomial Functor** | Niu & Spivak (2024) | `PolyAgent[S,A,B]` | "Mode-dependent agent" |
| **Lens/Wiring Diagram** | Myers (2024) | `WiringDiagram`, `>>` | "Composition" |
| **Operad** | Baez & Foley (2021) | `Operad`, `Operation`, `Law` | "Composition grammar" |
| **Operad Algebra** | MSFP 2024 | Domain-specific operads | "Domain patterns" |
| **Sheaf** | Goguen (1992-2024) | `Sheaf`, `View` | "Multiple views, one truth" |
| **Sheaf Gluing** | Task Sheaf (2025) | `glue()`, `verify_coherence()` | "Combining views" |
| **Galois Connection** | Category theory | `galois_loss()` | "Compression quality" |

---

## License & Community

- **License**: MIT (maximally permissive)
- **Governance**: kgents core team maintains; PRs welcome
- **Documentation**: Practical examples first, theory appendices second
- **Philosophy**: "Category theory for the people"—power without prerequisites

---

*"The patterns are general. They shouldn't be locked to one product. Category theory for the people."*
