# Agent Refactoring Fundamentals

> *"Every agent is a poem; derivation is scansion."*

This document establishes the principles for refining agent derivations to achieve maximal elegance while remaining faithful to `spec/principles.md`.

---

## The Central Thesis

**An agent is elegant when its derivation from bootstrap primitives is both necessary and sufficient—no missing steps, no superfluous ones.**

The five bootstrap primitives form an irreducible basis:

| Primitive | Symbol | Essence |
|-----------|--------|---------|
| **Id** | `I` | Identity morphism—preserve without change |
| **Compose** | `>>` | Sequential combination—output becomes input |
| **Ground** | `G` | Reality grounding—connect to the external |
| **Judge** | `J` | Principle evaluation—apply values |
| **Contradict** | `X` | Tension detection—surface conflicts |
| **Sublate** | `S` | Synthesis—resolve or hold tensions |
| **Fix** | `F` | Convergence—iterate until stable |

Every derived agent must decompose into compositions of these primitives. The question is not *whether* it decomposes, but *how elegantly*.

---

## The Three Laws of Elegant Derivation

### Law 1: Necessity

> Every primitive in the derivation must earn its place.

If you can remove a primitive and the agent still functions correctly, the derivation is inelegant. Redundant primitives indicate either misunderstanding of the agent's purpose or over-engineering.

**Test**: For each primitive in the derivation, ask "What breaks if I remove this?"

### Law 2: Sufficiency

> The derivation must fully explain the agent's behavior.

If the agent does something that cannot be traced back to its constituent primitives, either the derivation is incomplete or the agent is doing something it shouldn't.

**Test**: For each agent behavior, ask "Which primitive(s) produce this?"

### Law 3: Clarity

> The derivation should be readable as a sentence.

A well-derived agent reads like prose:
- "G-gent **Grounds** intent to domain, then **Composes** grammar rules, then **Judges** for constraint satisfaction"
- "H-gent **Contradicts** to surface tensions, then **Sublates** toward synthesis, using **Fix** when recursive"

If the derivation requires a flowchart to explain, it may be too complex.

---

## Pattern Catalog

From the existing specs, these derivation patterns emerge:

### Pattern A: The Linear Pipeline

```
Input → P₁ → P₂ → P₃ → Output
```

**Example**: G-gent (Grammarian)
```
Ground(domain) >> Compose(rules) >> Judge(constraints) >> Fix(refine)
```

**When to use**: When the agent transforms input through distinct, sequential stages.

**Elegance criterion**: The number of stages should match the essential complexity of the transformation, no more.

### Pattern B: The Stratified Architecture

```
Infrastructure Level: Operations (not agents)
Composition Level: Agent wrapping operations
```

**Example**: H-gent (Hegelian), D-gent (Data)
```
Infrastructure: Contradict, Sublate (meta-operations)
Composition: DialecticAgent = Compose(Contradict, Sublate) : Agent
```

**When to use**: When the domain requires both low-level operations AND higher-level orchestration.

**Elegance criterion**: Clear separation between levels; no leakage.

### Pattern C: The Functor Lift

```
K: Agent[A, B] → Agent[A, B]
```

**Example**: K-gent (Personalization)
```
K = Fix(λsystem. developer_adapts(system))
K.lift(agent) = agent colored by personality field
```

**When to use**: When the agent transforms other agents while preserving their type signature.

**Elegance criterion**: The functor laws must hold (identity preserved, composition preserved).

### Pattern D: The Lazy Tree

```
Root Promise
├── Child Promise (deferred)
│   └── Leaf (evaluated)
└── Child Promise (deferred)
    └── Leaf (evaluated)
```

**Example**: J-gent (JIT)
```
Classify(task) >> match {
    DETERMINISTIC → Ground(execute)
    PROBABILISTIC → Compose(children) >> Fix(collect)
    CHAOTIC → Ground(fallback)
}
```

**When to use**: When evaluation order matters and some branches may never be needed.

**Elegance criterion**: The lazy structure should reflect the inherent tree structure of the problem.

### Pattern E: The Separation of Concerns

```
Write-Time: Silent recording
Read-Time: Interpretive projection
```

**Example**: N-gent (Narrative)
```
Historian: Ground(tap) >> Ground(store)  [no prose]
Bard: Ground(crystals) >> Judge(genre) >> Compose(narrative)
```

**When to use**: When the same data needs multiple interpretations, or when recording must not affect execution.

**Elegance criterion**: The separation is clean; neither side knows the other's concerns.

---

## The Derivation Quality Checklist

For each agent derivation, verify:

### Structural

- [ ] **Decomposable**: Can be expressed purely in terms of bootstrap primitives
- [ ] **Minimal**: No primitive can be removed without loss of function
- [ ] **Complete**: All behaviors traced to primitives
- [ ] **Readable**: Derivation reads as natural description

### Categorical

- [ ] **Type-correct**: Input/output types match at each composition point
- [ ] **Composable**: The agent itself can be composed with others
- [ ] **Law-abiding**: Satisfies associativity, identity where applicable

### Principled

- [ ] **Tasteful**: Minimal complexity for the problem
- [ ] **Curated**: Deliberate choice of pattern, not accidental
- [ ] **Ethical**: Judge primitives appear where value judgments are made
- [ ] **Joy-inducing**: The derivation reveals something beautiful about the problem
- [ ] **Composable**: Enables further composition (doesn't dead-end)

---

## The Refactoring Process

### Step 1: Extract Current Derivation

Read the agent's README and implementation. Write out the implicit derivation:

```
Agent: [Name]
Current Derivation: P₁ >> P₂ >> P₃
```

### Step 2: Apply Necessity Test

For each primitive:
- What would break if removed?
- Is that breakage essential or accidental?

If accidental, the primitive is a candidate for removal.

### Step 3: Apply Sufficiency Test

For each documented behavior:
- Which primitive(s) produce it?
- Is the mapping clear and direct?

If unclear, either the derivation or the documentation needs refinement.

### Step 4: Apply Clarity Test

Write the derivation as a sentence:
- Does it read naturally?
- Would someone unfamiliar with the system understand the essence?

If not, refactor for clarity.

### Step 5: Verify Pattern Fit

Does the agent fit a known pattern?
- If yes, does it follow the pattern cleanly?
- If no, is it a genuinely novel pattern worthy of cataloging?

### Step 6: Document Refined Derivation

Update the agent's README with the refined derivation, showing:
- The primitives used
- The composition structure
- The pattern employed
- Why this is the right decomposition

---

## Agent Derivation Index

Current derivations from the specs (to be refined):

| Agent | Current Derivation | Pattern | Elegance Issues |
|-------|-------------------|---------|-----------------|
| **A-gent** | Ground + Compose + Judge + Fix | Pipeline | Base primitives; inherently elegant |
| **B-gent** | Ground(resources) + Judge(ethics) + Compose(allocation) | Pipeline | Good; could clarify economic Judge |
| **C-gent** | Pure category theory; IS the composition | Meta | Definitionally elegant |
| **D-gent** | Stratified: Ground(storage) + Compose(agents) | Stratified | Clear; infrastructure/composition split good |
| **E-gent** | Ground(observations) + Contradict(hypotheses) + Fix(evolve) | Pipeline | Good; falsification path clear |
| **F-gent** | Ground(intent) + Compose(artifact) + Judge(quality) + Fix(iterate) | Pipeline | Dense; consider staging |
| **G-gent** | Ground(domain) + Compose(grammar) + Judge(constraints) + Fix(refine) | Pipeline | Very clean |
| **H-gent** | Stratified: (Contradict, Sublate) + DialecticAgent wrapper | Stratified | Clean; separation noted |
| **I-gent** | Ground(state) + Compose(visualization) | Pipeline | Light; appropriate for interface |
| **J-gent** | Classify(Ground+Judge) + Compose(tree) + Fix(evaluate) | Lazy Tree | Complex; justified by JIT nature |
| **K-gent** | Fix(λsystem.developer_adapts) | Functor | Beautifully minimal |
| **L-gent** | Ground(storage) + Compose(search) + Judge(relevance) | Pipeline | Good; three-brain architecture maps well |
| **M-gent** | Ground(hologram) + Compose(resonance) + Fix(consolidate) | Pipeline | Poetic; holographic metaphor preserved |
| **N-gent** | Separation: Ground(tap) // Ground+Judge+Compose(narrate) | Separation | Clean; Historian/Bard split elegant |

---

## The Refinement Backlog

Priority issues discovered in the derivations:

### High Priority

1. **F-gent Staging**: The Forge does many things. Consider explicit phases:
   - Intent Capture (Ground)
   - Template Selection (Judge)
   - Code Generation (Compose)
   - Iteration (Fix)

2. **B-gent Economic Judge**: The ethical dimension of resource allocation deserves explicit Judge placement, not implicit in Compose.

### Medium Priority

3. **J-gent Complexity**: The JIT pattern is inherently complex, but verify each branch of the classification is necessary.

4. **T-gent Derivation**: Not in index—needs full derivation from spec.

### Low Priority

5. **Pattern Catalog Expansion**: Document any novel patterns found during refinement.

---

## The Aesthetic Standard

> *"Elegance is not a luxury; it is a necessity. An inelegant derivation is a misunderstanding made manifest."*

The goal is not to impress but to reveal. A good derivation should make the reader say "of course"—the structure was always there, we're just naming it.

**Signs of elegance**:
- The derivation fits on one line
- Each primitive appears exactly once (or has clear reason for repetition)
- The pattern choice is obvious in hindsight
- The derivation could be taught to a newcomer

**Signs of inelegance**:
- The derivation requires conditional branches to explain
- Primitives appear redundantly
- The pattern is unique to this agent (unless genuinely novel)
- The derivation requires implementation details to understand

---

## Maintaining This Document

As agents are refined:
1. Update the Agent Derivation Index
2. Document new patterns discovered
3. Add elegance issues to the backlog
4. Archive resolved issues

This is a living document tracking the ongoing pursuit of derivational elegance.

---

*"The unexamined agent is not worth composing."*
