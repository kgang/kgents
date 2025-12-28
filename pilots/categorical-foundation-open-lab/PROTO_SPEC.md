# Categorical Foundation Open Lab

Status: **production**

> *"The patterns are general. They shouldn't be locked to one product. Category theory for the people."*

---

## ⚠️ Implementation Directive

**This spec is a BUILD order, not a design document.**

When this PROTO_SPEC is consumed for regeneration:
- **Implement ALL laws (L1-L12)** — complete set
- **Implement ALL QAs (QA-1 through QA-5)** — complete set
- **All examples must run** — no placeholder code
- **Law verification must work** — not just claimed
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

### Quality Gates (Mandatory)

| Gate | Requirement | Failure = Block |
|------|-------------|-----------------|
| **QG-1** | All 6 examples in `examples/` execute correctly | Yes |
| **QG-2** | `pytest` exits 0 | Yes |
| **QG-3** | `mypy` exits 0 | Yes |
| **QG-4** | Hello World < 60 seconds on fresh install | Yes |
| **QG-5** | Time to "Aha" (composition) < 5 minutes | Yes |
| **QG-6** | No category theory jargon in README first 500 words | Yes |

---

## Narrative

The mathematical foundations you've discovered—monad isolation, operad composition, sheaf coherence, polynomial functors—are general patterns that apply to ANY governance system, not just kgents. This pilot packages the categorical infrastructure as open-source tools that other developers can use to build principled systems.

The bet: If these patterns spread, governance itself becomes more rigorous and more human.

## Personality Tag

*Pedagogical infrastructure. It teaches by enabling. The goal is not to explain category theory, but to let people USE category theory without knowing they're using it.*

## Objectives

- Package **PolyAgent, Operad, and Sheaf** as standalone, documented, tested libraries.
- Provide **domain-independent templates** that instantiate the three-layer pattern for any governance problem.
- Create **verified law checking** that catches categorical violations at runtime without requiring users to understand the math.
- Build **composable building blocks** that make "doing it right" easier than "doing it wrong."
- Establish **reference implementations** that demonstrate the patterns in concrete domains.

## Epistemic Commitments

- **Composition is primary**. The Minimal Output Principle: single outputs that compose, not aggregates.
- **Laws are enforced, not suggested**. `BootstrapWitness.verify_*_laws()` runs at startup; violations fail hard.
- **Abstractions pay for themselves**. If the categorical abstraction doesn't make code simpler AND more correct, remove it.
- **Documentation IS specification**. Generative spec means you could delete impl and rebuild from docs.
- **Joy in use**. If developers don't enjoy using the library, the abstraction failed. (Principle 4: Joy-Inducing)

## Laws

- **L1 Law Verification Law**: Any PolyAgent, Operad, or Sheaf must verify its categorical laws at instantiation time. No unchecked composition.
- **L2 Minimal Output Law**: Library functions return single values, not arrays. Composition happens at call site.
- **L3 Composition Transparency Law**: When composition fails, the error message explains WHICH law was violated and WHY.
- **L4 Domain Independence Law**: Core abstractions contain NO domain-specific logic. Domain operads extend, not modify.
- **L5 Documentation Regeneration Law**: The spec must be sufficiently detailed that deleting `src/` and regenerating from docs produces isomorphic code.

## Qualitative Assertions

- **QA-1** A developer should be able to **use PolyAgent in 10 minutes** without understanding polynomial functors.
- **QA-2** Law violations should produce **actionable error messages**: "Associativity failed because X ∘ (Y ∘ Z) ≠ (X ∘ Y) ∘ Z at step 3."
- **QA-3** The library should feel **lighter than alternatives** (e.g., simpler than Redux for state, cleaner than raw classes for agents).
- **QA-4** A non-mathematician should be able to **build a working governance system** using the templates without reading category theory.
- **QA-5** The codebase should be **beautiful to read**. If the implementation isn't elegant, the abstraction is wrong.

## Anti-Success (Failure Modes)

The system fails if:

- **Abstraction tax**: Using the library is harder than rolling your own. The math adds overhead without benefit.
- **Jargon gatekeeping**: Documentation requires category theory background. "Monad" scares people away.
- **Framework trap**: The library imposes structure that doesn't fit real problems. Procrustean abstraction.
- **Dead documentation**: Specs diverge from implementation. Generativity fails.
- **Cleverness over clarity**: The code shows off math instead of solving problems.

## kgents Integrations

This pilot EXTRACTS from kgents rather than consuming:

| Component | Extraction | Package Name |
|-----------|------------|--------------|
| **PolyAgent** | Mode-dependent state machines | `kgents-poly` |
| **Operad** | Composition grammar with verified laws | `kgents-operad` |
| **Sheaf** | Local→global coherence | `kgents-sheaf` |
| **BootstrapWitness** | Runtime law verification | `kgents-laws` |
| **Galois Loss** | Semantic distance measurement | `kgents-galois` |
| **Pilot Law Grammar** | Universal law schemas | `kgents-governance` |

**Three-Layer Template**:
```python
from kgents_poly import PolyAgent
from kgents_operad import Operad, Law
from kgents_sheaf import Sheaf, View

# 1. Define your domain's polynomial structure
class MyDomainAgent(PolyAgent[MyState, MyInput, MyOutput]):
    def transition(self, state: MyState, input: MyInput) -> tuple[MyState, MyOutput]:
        ...

# 2. Define your domain's composition grammar
MY_DOMAIN_OPERAD = Operad(
    operations=["create", "transform", "compose", "verify"],
    laws=[
        Law("identity", lambda f: f >> Id == f == Id >> f),
        Law("associativity", lambda f, g, h: (f >> g) >> h == f >> (g >> h)),
    ]
)

# 3. Define your domain's coherence views
class MyDomainSheaf(Sheaf):
    views = [SummaryView, DetailView, DiffView]

    def glue(self, local_views: list[View]) -> GlobalState:
        ...
```

## Canary Success Criteria

- A developer unfamiliar with category theory can **build a working state machine** using PolyAgent in under 30 minutes.
- Law verification catches **at least one composition bug** that would have been silent otherwise.
- The library is **smaller than alternatives**: fewer lines of code than equivalent Redux/MobX patterns.
- At least **one external project** adopts the library for non-kgents use within 6 months.
- Documentation passes the **Generative Test**: delete `src/`, regenerate from docs, get isomorphic code.

## Out of Scope

- UI components (this is infrastructure only).
- Domain-specific operads (those belong in domain pilots).
- Hosted services (this is open-source libraries, not SaaS).
- Category theory tutorials (documentation is practical, not pedagogical).

## Mathematical Grounding

This pilot IS the mathematical grounding made accessible:

| Abstraction | What It Provides | Why It Matters |
|-------------|------------------|----------------|
| **PolyAgent[S,A,B]** | Mode-dependent behavior | State machines with type-safe transitions |
| **Operad** | Composition grammar | Define what operations are legal |
| **Sheaf** | Local→global coherence | Multiple views, one truth |
| **Laws** | Runtime verification | Catch bugs category theory would prevent |
| **Galois Loss** | Semantic measurement | Quantify abstraction quality |

## License & Community

- **License**: MIT (maximally permissive)
- **Governance**: kgents core team maintains; PRs welcome
- **Documentation**: Practical examples first, theory appendices second
- **Philosophy**: "Category theory for the people"—power without prerequisites

## Reference Implementations

The library ships with three reference implementations demonstrating the pattern:

1. **Todo App** (trivial): PolyAgent for task states, Operad for CRUD, Sheaf for list/detail views
2. **Document Editor** (moderate): K-Block pattern simplified, collaborative coherence
3. **Governance System** (complex): Constitutional scoring, trust gradient, amendment process

Each reference includes:
- Working code
- Spec that could regenerate it
- Law verification tests
- Performance benchmarks

## Pricing Context

Target: Open-source (MIT license)

Value proposition: "The patterns behind kgents, without the lock-in."

Strategic rationale: Open-sourcing the foundations establishes kgents as the reference implementation. Adoption of the patterns validates the theory. Community contributions improve the core.

---

## DevEx Consumption Narrative (Shock & Awe Strategy)

> *"In 60 seconds, the developer goes from skeptical to converted."*

### The Hero Journey (First 10 Minutes)

```
MINUTE 0: "What is this?"
  └─→ Landing page shows: "State machines that compose. For free."
  └─→ No jargon. No "category theory." Just: "Make state easier."

MINUTE 1: "Let me try it."
  └─→ One-liner install: pip install kgents-poly
  └─→ Copy-paste example from README works first try.

MINUTE 2: "Okay, it runs. So what?"
  └─→ The "Aha" moment: Compose two agents with >>
  └─→ See them work together without glue code.

MINUTE 3: "That's clean. But does it scale?"
  └─→ Show law verification catching a real bug.
  └─→ Error message tells you EXACTLY what's wrong.

MINUTE 5: "I want to use this in my project."
  └─→ Integration guide shows real-world patterns.
  └─→ TypeScript types available via kgents-contracts.

MINUTE 10: "I'm building something."
  └─→ Developer is productive without reading theory.
  └─→ Theory available if curious, never required.
```

### L6 First Impression Law

The landing page / README MUST achieve:

| Metric | Requirement | How |
|--------|-------------|-----|
| **Time to Hello World** | < 60 seconds | Single copy-paste example |
| **Time to Composition** | < 3 minutes | Second example chains agents |
| **Time to "Aha"** | < 5 minutes | Third example shows law verification |
| **Zero Jargon Barrier** | No category theory in first 500 words | Plain language: "agents," "compose," "verify" |

### L7 Batteries-Included Law

Out of the box, these MUST work with zero configuration:

```python
# 1. Create an agent from a function (5 seconds)
from kgents_poly import from_function

double = from_function("double", lambda x: x * 2)
_, result = double.invoke("ready", 21)
# result = 42

# 2. Compose agents (10 seconds)
add_one = from_function("add_one", lambda x: x + 1)
pipeline = double >> add_one
_, result = pipeline.invoke(("ready", "ready"), 10)
# result = 21 (10 * 2 + 1)

# 3. Run in parallel (15 seconds)
from kgents_poly import parallel
both = parallel(double, add_one)
_, result = both.invoke(("ready", "ready"), 5)
# result = (10, 6)

# 4. Verify laws at runtime (20 seconds)
from kgents_laws import verify_identity, verify_associativity
verify_identity(double)  # Passes silently
verify_associativity(double, add_one, from_function("negate", lambda x: -x))
# Passes or raises with clear explanation

# 5. Measure semantic distance (25 seconds)
from kgents_galois import jaccard_distance
distance = jaccard_distance("Hello world", "Hello there")
# distance ≈ 0.5 (50% different)

# 6. Define governance laws (30 seconds)
from kgents_governance import gate_law, threshold_law

# Gate: ETHICAL score < 0.6 → total = 0
ethical_gate = gate_law("ethical", threshold=0.6, on_fail=0.0)

# Threshold: DRIFT > 0.4 → warn
drift_alert = threshold_law("drift", threshold=0.4, action="warn")
```

### L8 Error Message Law

Every error MUST be actionable:

```python
# BAD (don't do this)
raise ValueError("Associativity check failed")

# GOOD (do this)
raise AssociativityError(
    message="Composition is not associative",
    left_first="(f >> g) >> h",
    right_first="f >> (g >> h)",
    difference="At step 3, left produces 'foo', right produces 'bar'",
    fix_suggestion="Check that 'g' is a pure function with no side effects",
    documentation_link="https://kgents.dev/laws/associativity"
)
```

**Error template**:
1. What failed (one line)
2. What was expected vs. actual
3. Where it diverged (step number, input)
4. How to fix it
5. Link to documentation

### L9 Progressive Disclosure Law

Documentation MUST be layered:

| Layer | Audience | Content | Location |
|-------|----------|---------|----------|
| **1. README** | Any developer | 5-minute quickstart, no theory | `README.md` |
| **2. Cookbook** | Practical user | Common patterns, copy-paste | `docs/cookbook.md` |
| **3. API Reference** | Integration dev | Full API, types, examples | `docs/api/` |
| **4. Theory Appendix** | Curious reader | Category theory grounding | `docs/theory/` |
| **5. Research Paper** | Academic | Formal definitions, proofs | `docs/paper.pdf` |

**Rule**: Layer N never requires Layer N+1 to be useful.

### L10 Visual Impact Law

The landing page MUST include:

```
┌─────────────────────────────────────────────────────────────────┐
│  BEFORE: The Pain                                                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  class TaskManager:                                       │   │
│  │      def __init__(self):                                  │   │
│  │          self.state = "idle"                              │   │
│  │                                                           │   │
│  │      def handle(self, action):                            │   │
│  │          if self.state == "idle" and action == "start":  │   │
│  │              self.state = "running"                       │   │
│  │          elif self.state == "running" and action == "stop": │ │
│  │              self.state = "idle"                          │   │
│  │          # 50 more elif branches...                       │   │
│  │          # Bugs lurk. Composition impossible.             │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
│  AFTER: The Joy                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  task = stateful("task",                                  │   │
│  │      states={"idle", "running"},                          │   │
│  │      transition=lambda s, a: transitions[(s, a)]          │   │
│  │  )                                                        │   │
│  │                                                           │   │
│  │  # Compose with other agents                              │   │
│  │  pipeline = task >> logger >> notifier                    │   │
│  │                                                           │   │
│  │  # Laws verified automatically                            │   │
│  │  verify_identity(task)  # ✓                               │   │
│  └──────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### L11 Principled Build Law

```bash
# Install (one command)
pip install kgents-poly kgents-laws kgents-galois

# Or all packages
pip install kgents-foundation

# Development
git clone https://github.com/kgents/foundation
cd foundation
pip install -e ".[dev]"
pytest  # All tests pass
```

### L12 Package Structure Law

```
kgents-foundation/
├── README.md               # Hero journey (5-min quickstart)
├── pyproject.toml          # Modern Python packaging
├── docs/
│   ├── cookbook.md         # Practical patterns
│   ├── api/
│   │   ├── poly.md         # PolyAgent API
│   │   ├── operad.md       # Operad API
│   │   ├── sheaf.md        # Sheaf API
│   │   ├── laws.md         # Law verification API
│   │   └── galois.md       # Semantic distance API
│   └── theory/
│       ├── polynomial-functors.md
│       ├── operads.md
│       └── sheaves.md
├── kgents_poly/
│   ├── __init__.py         # from_function, sequential, parallel, identity
│   └── core.py             # PolyAgent implementation
├── kgents_operad/
│   ├── __init__.py         # Operad, Operation, Law
│   └── core.py             # Operad implementation
├── kgents_sheaf/
│   ├── __init__.py         # Sheaf, View, Coherent
│   └── core.py             # Sheaf implementation
├── kgents_laws/
│   ├── __init__.py         # verify_identity, verify_associativity
│   └── core.py             # Law verification
├── kgents_galois/
│   ├── __init__.py         # semantic_distance, jaccard_distance
│   └── core.py             # Distance metrics
├── kgents_governance/
│   ├── __init__.py         # gate_law, threshold_law, GovernanceLaw
│   └── core.py             # Law schemas
├── examples/
│   ├── 01_hello_world.py   # Simplest possible example
│   ├── 02_composition.py   # Chaining agents
│   ├── 03_law_verification.py
│   ├── 04_todo_app.py      # Real-world: Todo state machine
│   ├── 05_document_editor.py # Real-world: Collaborative editing
│   └── 06_governance.py    # Real-world: Constitutional scoring
└── tests/
    ├── test_poly.py
    ├── test_operad.py
    ├── test_sheaf.py
    ├── test_laws.py
    ├── test_galois.py
    └── test_governance.py
```

---

## Generation Checklist (For Sub-Agents)

Before claiming this pilot is complete, verify:

**DevEx Fundamentals**:
- [ ] **Hello World < 60s**: Copy-paste from README works immediately
- [ ] **Composition works**: `>>` operator chains agents correctly
- [ ] **Law verification works**: Identity and associativity checks run
- [ ] **Errors are actionable**: Every error has what/expected/actual/fix

**Package Quality**:
- [ ] **No jargon in README**: First 500 words use plain language
- [ ] **Examples run**: All 6 examples in `examples/` execute correctly
- [ ] **Tests pass**: `pytest` exits 0
- [ ] **Types complete**: `mypy` exits 0
- [ ] **Docs build**: Documentation renders correctly

**Batteries-Included**:
- [ ] **`from_function` works**: Lift any function to agent
- [ ] **`sequential` works**: Chain agents with `>>`
- [ ] **`parallel` works**: Run agents on same input
- [ ] **`identity` works**: Pass-through agent
- [ ] **`verify_identity` works**: Identity law checking
- [ ] **`verify_associativity` works**: Associativity law checking
- [ ] **`jaccard_distance` works**: Basic semantic distance
- [ ] **`gate_law` works**: Floor enforcement

**Shock & Awe Moment**:
- [ ] **Visual before/after**: Landing page shows transformation
- [ ] **Progressive disclosure**: Theory available but never required
- [ ] **"I want to use this"**: Developer feels pull by minute 5
