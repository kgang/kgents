# L-gent: Library Agent Brainstorm

**Date**: 2025-12-08
**Status**: Exploration
**Goal**: Define what "L" represents in the kgents taxonomy

---

## Design Principles

When choosing the L-gent concept, consider:
1. **Composability**: How does it compose with existing agents (>>, morphisms)?
2. **Generativity**: What new capabilities does it enable?
3. **Gap-filling**: What's missing from the current ecosystem?
4. **Tasteful**: Is it elegant and minimal?

---

## Option 1: Librarian Agent — Knowledge Curation & Retrieval

**Philosophy**: *"Organize knowledge so it finds you."*

**Core Morphism**: `Query → Source[]` — Retrieval as composition

### Key Concepts

- **Catalog**: Indexed knowledge across agents, sessions, files
- **Citation**: Track provenance (where knowledge came from)
- **Cross-Reference**: Link related concepts across genera
- **Standing Query**: Persistent queries that notify on new matches

### Composition Opportunities

```python
# L-gent + D-gent: Persistent knowledge base
library = Librarian(backend=PersistentAgent(path="knowledge.json"))

# L-gent + B-gent: Hypothesis-driven research
research_pipeline = Librarian >> HypothesisEngine >> Validate

# L-gent + E-gent: Evolution-informed retrieval
# "What improvements worked for similar code?"
similar_improvements = Librarian(index=ImprovementMemory)

# L-gent + T-gent: Test case library
test_library = Librarian(scope=["fixtures", "properties", "oracles"])
```

### Generative Potential

- Auto-generate documentation from code patterns
- Build knowledge graphs across sessions
- Enable semantic search over agent outputs
- Cross-session learning ("what worked before?")

### Minimal Implementation

```python
@dataclass
class LibrarianQuery:
    query: str
    scope: list[str]  # Which genera/domains to search
    limit: int = 10

@dataclass
class Source:
    content: Any
    origin: str  # Where it came from
    timestamp: datetime
    relevance: float

@dataclass
class LibrarianResult:
    sources: list[Source]
    total_matches: int

class Librarian(Agent[LibrarianQuery, LibrarianResult]):
    """L-gent: Knowledge retrieval across kgents ecosystem."""

    @property
    def name(self) -> str:
        return "Librarian"

    async def invoke(self, query: LibrarianQuery) -> LibrarianResult:
        # Search across registered knowledge sources
        ...
```

---

## Option 2: Lens Agent — Focused Transformation

**Philosophy**: *"See clearly by seeing less."*

**Core Morphism**: `(S, Lens[S,A]) → A` — Focused access as composition

### Key Concepts

- **Focus**: Extract sub-structure from complex state
- **Prism**: Handle optional/variant cases (Maybe, Either)
- **Traversal**: Apply transformation across collections
- **Iso**: Bidirectional lossless transformation

### Composition Opportunities

```python
# Already exists in D-gents (LensAgent), but could generalize:

# Lens >> Agent >> Lens⁻¹ = Focused transformation
focused_evolution = (
    focus_on("function_bodies")
    >> EvolutionAgent
    >> unfocus
)

# Lens composition for deep access
user_city = user_lens >> address_lens >> city_lens

# L-gent + T-gent: Focused property testing
test_focused = PropertyAgent(
    agent=focus_on("validation_logic") >> system_under_test,
    property=always_returns_bool
)
```

### Generative Potential

- Auto-derive lenses from dataclass definitions
- Generate bi-directional transformations (Iso)
- Enable "surgical" agent application to sub-structures

### Note

This partially exists as `agents/d/lens.py` and `agents/d/lens_agent.py`. L-gent could generalize this beyond D-gent state management.

---

## Option 3: Logic Agent — Formal Reasoning

**Philosophy**: *"Prove it, don't just believe it."*

**Core Morphism**: `(Premises, Goal) → Proof | Counterexample`

### Key Concepts

- **Proposition**: Typed claims about agents/states
- **Inference**: Modus ponens, resolution, unification
- **Constraint**: SAT/SMT integration for decidable fragments
- **Model**: Satisfying assignment that proves possibility

### Composition Opportunities

```python
# L-gent + T-gent: Prove properties, not just test them
property_proof = LogicAgent(
    premises=[type_signature, invariants],
    goal=property_holds_for_all_inputs
)

# L-gent + J-gent: Verify JIT safety formally
safe_compile = MetaArchitect >> LogicAgent(goal="no_unbounded_recursion")

# L-gent + H-gent: Dialectic with logical grounding
reasoned_synthesis = Thesis >> LogicAgent >> Antithesis >> Sublate

# L-gent + E-gent: Prove improvement preserves behavior
verified_evolution = EvolutionAgent >> LogicAgent(goal="behavioral_equivalence")
```

### Generative Potential

- Generate test cases from proof failures (counterexample-guided)
- Derive invariants from successful evolutions
- Build verified agent transformations
- Formal specification → implementation

---

## Option 4: Lambda Agent — Higher-Order Agent Factory

**Philosophy**: *"Agents that make agents."*

**Core Morphism**: `Specification → Agent[A, B]`

### Key Concepts

- **Abstraction**: `λx. body` — parameterized agent templates
- **Application**: `(λx. f) arg` — instantiate template with values
- **Closure**: Capture environment in agent definition
- **Currying**: Partial application of agent parameters

### Composition Opportunities

```python
# L-gent + J-gent: Lambda as typed MetaArchitect
make_filter = LambdaAgent(
    params=["predicate: A -> bool"],
    body="Agent that keeps items where predicate(item)"
)
positive_filter = make_filter(predicate=lambda x: x > 0)

# L-gent + C-gent: Functor over agent factories
mapped_factory = list_agent(make_filter, predicates)

# L-gent + E-gent: Evolve the factory, not just agents
better_factory = LambdaAgent >> EvolutionPipeline

# Partial application for common patterns
json_parser = make_parser(format="json")  # Curried
xml_parser = make_parser(format="xml")
```

### Generative Potential

- Meta-meta-circular: factories that evolve factories
- Typed agent templates (generic agents)
- Partial application: pre-configure common patterns
- Agent algebra: compose factories like functions

### Relationship to J-gent

J-gent's MetaArchitect already generates agents from intent. Lambda Agent would formalize this with:
- Explicit type parameters
- Guaranteed composition laws
- Reusable templates (not just one-off generation)

---

## Option 5: Loop Agent — Iterative Refinement

**Philosophy**: *"Iterate until done, but know when to stop."*

**Core Morphism**: `(State, Condition) → FixedPoint`

### Key Concepts

- **Iteration**: Repeated application with state threading
- **Convergence**: Detect when to stop (similarity threshold)
- **Bounded**: Maximum iterations (entropy budget from H-gents)
- **Divergence Handler**: What to do when not converging

### Composition Opportunities

```python
# L-gent extends Fix with richer control
loop = LoopAgent(
    step=improve_code,
    converged=lambda old, new: similarity(old, new) > 0.99,
    max_iterations=10,
    on_diverge=Ground(fallback)  # J-gent integration
)

# L-gent + H-gent: Dialectic as loop
dialectic_loop = LoopAgent(
    step=thesis >> contradict >> sublate,
    converged=lambda s: s.tensions_remaining == 0
)

# L-gent + T-gent: Test-driven iteration
tdd_loop = LoopAgent(
    step=write_code >> run_tests,
    converged=lambda s: s.all_tests_pass
)

# L-gent + E-gent: Evolution as bounded loop
evolution_loop = LoopAgent(
    step=hypothesize >> experiment >> judge,
    converged=lambda s: s.improvement_score > 0.9,
    max_iterations=5
)
```

### Generative Potential

- Generate convergence criteria from examples
- Detect infinite loops before they happen (J-gent Chaosmonger)
- Compose multiple loops (nested iteration)
- Learn optimal iteration counts from history

### Relationship to Bootstrap Fix

Bootstrap `Fix` already provides fixed-point iteration. Loop Agent would add:
- Richer convergence conditions (not just equality)
- Divergence handling
- Iteration metrics/history
- Composition with J-gent entropy budgets

---

## Option 6: Lattice Agent — Ordered Knowledge Structures

**Philosophy**: *"Everything has its place in the hierarchy."*

**Core Morphism**: `(A, A) → LUB | GLB` — Meet and join operations

### Key Concepts

- **Partial Order**: Compare agents/states/knowledge
- **Join Semilattice**: Combine information (least upper bound)
- **Meet Semilattice**: Find commonality (greatest lower bound)
- **Bottom/Top**: Universal bounds

### Composition Opportunities

```python
# L-gent + H-gent: Dialectic as lattice join
synthesis = LatticeAgent.join(thesis, antithesis)

# L-gent + E-gent: Type lattice for evolution
compatible_types = LatticeAgent.meet(original_type, evolved_type)

# L-gent + D-gent: CRDT-style merge (conflict-free)
merged_state = LatticeAgent.join(state_a, state_b)

# L-gent + T-gent: Test result aggregation
overall_result = LatticeAgent.meet(test_results)  # All must pass
```

### Generative Potential

- Auto-derive lattice structure from type hierarchies
- Build concept hierarchies (ontologies)
- Enable conflict-free distributed state (CRDTs)
- Type-safe agent composition (subtyping as lattice)

---

## Option 7: Lineage Agent — Provenance & Ancestry

**Philosophy**: *"Know where you came from."*

**Core Morphism**: `Entity → Ancestry[]`

### Key Concepts

- **Provenance**: Track transformations through pipeline
- **Blame**: Attribute outputs to inputs
- **Versioning**: Maintain history of entity evolution
- **Diff**: Compare entities across lineage

### Composition Opportunities

```python
# L-gent + E-gent: Track improvement lineage
lineage = LineageAgent(track=EvolutionPipeline)
# "This code came from hypothesis H3, evolved 4 times, judged by principles P1,P2"

# L-gent + D-gent: State history as lineage
state_lineage = LineageAgent(track=PersistentAgent)

# L-gent + J-gent: JIT compilation provenance
compiled_lineage = LineageAgent(track=MetaArchitect >> Sandbox)
# "This agent was compiled from intent X, passed safety checks Y"

# L-gent + H-gent: Dialectic history
synthesis_lineage = LineageAgent(track=DialecticAgent)
# "This synthesis resolved tensions T1, T2 from theses A, B"
```

### Generative Potential

- Auto-generate changelogs from lineage
- Rollback to any ancestor state
- Analyze which hypotheses lead to success
- Audit trail for agent decisions

### Relationship to D-gent History

D-gent already provides `history()` for state snapshots. Lineage Agent would add:
- Cross-agent provenance (not just state)
- Transformation tracking (what changed, why)
- Blame attribution (which agent caused this)

---

## Comparison Matrix

| Option | Gap Filled | Composition | Generativity | Complexity |
|--------|-----------|-------------|--------------|------------|
| **Librarian** | Knowledge retrieval | High (D, B, E) | High | Medium |
| **Lens** | Focused transforms | Medium (D exists) | Medium | Low |
| **Logic** | Formal verification | High (T, J, E) | High | High |
| **Lambda** | Agent factories | High (J, C, E) | Very High | Medium |
| **Loop** | Iteration control | Medium (Fix exists) | Medium | Low |
| **Lattice** | Ordered structures | High (H, D, E) | Medium | Medium |
| **Lineage** | Provenance tracking | High (D, E, J) | Medium | Medium |

---

## Recommendation

### Primary: Librarian (Option 1)

**Rationale**:
- Fills clear gap (knowledge retrieval across sessions)
- Composes naturally with D-gent (storage), B-gent (research), E-gent (memory)
- Enables new capabilities (cross-session learning)
- Medium complexity, high immediate value

### Secondary: Lambda (Option 4)

**Rationale**:
- Deepens meta-circular vision (J-gent + E-gent synergy)
- Formalizes agent factories (currently implicit in MetaArchitect)
- Enables typed, parameterized agent templates
- Aligns with functional programming foundations

### Future Consideration: Logic (Option 3)

**Rationale**:
- Would enable verified agents (not just tested)
- High complexity but transformative potential
- Could be built on top of Librarian (knowledge) + Lambda (factories)

---

## Next Steps

1. **Choose primary direction** (Librarian recommended)
2. **Write spec**: `spec/l-gents/README.md`
3. **Identify minimal MVP**: What's the smallest useful L-gent?
4. **Design composition points**: How does it plug into existing genera?
5. **Implement Phase 1**: Core types and basic functionality

---

## Open Questions

1. Should L-gent be singular (like K-gent) or plural (like T-gents)?
2. What existing code could be refactored into L-gent?
3. Which genera would benefit most from L-gent integration?
4. How does L-gent relate to the bootstrap agents?
