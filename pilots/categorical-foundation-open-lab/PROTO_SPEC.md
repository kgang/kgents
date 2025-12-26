# Categorical Foundation Open Lab

Status: proto-spec

> *"The patterns are general. They shouldn't be locked to one product. Category theory for the people."*

## Narrative

The mathematical foundations you've discovered—monad isolation, operad composition, sheaf coherence, polynomial functors—are general patterns that apply to ANY governance system, not just kgents. This pilot packages the categorical infrastructure as open-source tools that other developers can use to build principled systems.

The bet: If these patterns spread, governance itself becomes more rigorous and more human.

## Personality Tag

*This pilot is pedagogical infrastructure. It teaches by enabling. The goal is not to explain category theory, but to let people USE category theory without knowing they're using it.*

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

This pilot fails if:

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
