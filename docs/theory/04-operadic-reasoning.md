# Chapter 4: Operads and Reasoning Grammar

> *"An operad is a space of operations, equipped with instructions for composition."*
> — Tom Leinster

---

## 4.1 Beyond Sequential: The Need for Operads

Monads (Chapter 3) handle sequential composition beautifully: A → B → C. But reasoning often has **parallel structure**:

```
    Premise₁    Premise₂    Premise₃
         \         |         /
          \        |        /
           \       |       /
            ▼      ▼      ▼
           ───────────────────
                  |
                  ▼
             Conclusion
```

Multiple inputs combine to produce one output. This is not sequential—it's **operadic**.

Consider a syllogism:
- "All humans are mortal" (major premise)
- "Socrates is human" (minor premise)
- Therefore: "Socrates is mortal" (conclusion)

This inference has two inputs and one output. We cannot model it as A → B → C; we need (A, B) → C.

Operads provide the structure for multi-input operations and their composition.

---

## 4.2 Operads: The Full Definition

### Definition 4.1 (Symmetric Operad)

A **symmetric operad** P consists of:

1. For each n ≥ 0, a set P(n) of **n-ary operations**
2. For each n and each permutation σ ∈ Sₙ, an action P(n) → P(n) (permuting inputs)
3. A distinguished element id ∈ P(1) called the **identity**
4. **Composition maps**: For each operation f ∈ P(n) and operations g₁ ∈ P(k₁), ..., gₙ ∈ P(kₙ):

   γ(f; g₁, ..., gₙ) ∈ P(k₁ + ... + kₙ)

   This substitutes gᵢ into the i-th input of f.

Subject to:

- **Equivariance**: Composition respects the symmetric group actions
- **Associativity**: Nested substitution is independent of grouping
- **Unit laws**: Substituting the identity is trivial

### Visualizing Composition

```
       f                              γ(f; g₁, g₂)
      ╱ ╲                                  │
     ╱   ╲                    ╱────────────┼────────────╲
    1     2                  ╱             │             ╲
    │     │                 g₁             │             g₂
    │     │                ╱  ╲            │            ╱  ╲
                          1    2           │           1    2
                                           │
                               ────────────────────────
                                           │
                                        result
```

Composition plugs the outputs of g₁, g₂ into the inputs of f.

### Example 4.2 (The Endomorphism Operad)

For any set X, the **endomorphism operad** End(X) has:
- End(X)(n) = {functions f : Xⁿ → X}
- Composition: function composition (plug outputs into inputs)
- Identity: the identity function X → X

This is the prototypical operad—it's what operads are "operadically equivalent to," in a precise sense (operad algebras).

---

## 4.3 The Reasoning Operad

### Definition 4.3 (Reasoning Operad)

Let **Reason** be an operad where:

- **Reason(n)** = n-ary inference rules (rules that take n premises and produce one conclusion)
- **Composition** = rule chaining (conclusions of inner rules become premises of outer rules)
- **Identity** = the trivial rule (premise implies itself)

### Example 4.4 (Propositional Logic Operad)

**PropLog** is an operad with:

**Nullary operations (Reason(0))**: Axioms—rules with no premises
- ⊤ (truth)

**Unary operations (Reason(1))**: Single-premise rules
- Identity: A ⊢ A
- Double negation (classical): ¬¬A ⊢ A
- Weakening: A ⊢ A ∨ B

**Binary operations (Reason(2))**: Two-premise rules
- Modus ponens: A, A → B ⊢ B
- Conjunction introduction: A, B ⊢ A ∧ B
- Disjunction elimination: A ∨ B, A → C, B → C ⊢ C (this is really ternary)

**Ternary operations (Reason(3))**: Three-premise rules
- Disjunction elimination (properly): A ∨ B, A → C, B → C ⊢ C

### Theorem 4.5

**PropLog** is an operad under rule composition.

*Proof sketch.* Verify the operad laws:

**Identity**: Plugging the identity rule (A ⊢ A) into any input slot of a rule R leaves R unchanged.

**Associativity**: Consider rules f, g, h where h has outputs feeding g, and g has outputs feeding f. Composing ((f; g); h) vs (f; (g; h)) yields the same derivation tree—just grouped differently.

**Equivariance**: Permuting the inputs of a rule and then composing equals composing and then permuting appropriately. ∎

---

## 4.4 Operad Algebras: Giving Meaning to Operations

An operad defines abstract operations. An **algebra** for an operad assigns concrete meaning.

### Definition 4.6 (Algebra for an Operad)

For operad P, a **P-algebra** is:
- A set A (the carrier)
- For each n-ary operation f ∈ P(n), a function ⟦f⟧ : Aⁿ → A

Such that:
- ⟦id⟧ = identity function
- ⟦γ(f; g₁, ..., gₙ)⟧ = ⟦f⟧ ∘ (⟦g₁⟧ × ... × ⟦gₙ⟧)

The algebra respects operadic composition.

### Example 4.7 (Propositions as Algebra)

For **PropLog**, an algebra assigns:
- A set A of "truth values" (could be {T, F}, or [0,1], or something richer)
- Interpretations of each rule as a function on truth values

The standard Boolean algebra makes A = {T, F} and interprets rules via truth tables.

### Example 4.8 (LLM as Operad Algebra)

**Conjecture**: An LLM provides an (approximate) algebra for the reasoning operad:
- Carrier A = token sequences (or embedding vectors)
- Each reasoning rule f ∈ Reason(n) is interpreted as an LLM operation:
  - Take n premise texts
  - Generate a conclusion text

The algebra is approximate because LLMs don't perfectly respect the operad laws—they sometimes generate invalid inferences.

---

## 4.5 Tree-of-Thoughts as Free Algebra

The **free algebra** for an operad is the most general algebra—it represents all possible compositions without imposing equations.

### Definition 4.9 (Free Operad Algebra)

For operad P and set X, the **free P-algebra on X** is:
- Elements are **trees** built from:
  - Leaves labeled by elements of X
  - Internal nodes labeled by operations from P
- The algebra structure is tree grafting

### Theorem 4.10 (ToT is the Free Reasoning Algebra)

Tree-of-thoughts exploration is isomorphic to the free algebra for the ToT operad.

*Argument.*

The ToT operad has operations:
- **branch(n)** ∈ ToT(1): Generate n candidate thoughts from one
- **evaluate** ∈ ToT(1): Score a thought
- **select** ∈ ToT(n): Choose best among n thoughts
- **synthesize** ∈ ToT(n): Combine n thoughts into one

A ToT execution trace IS a tree:
- Root: initial problem
- Internal nodes: operad operations (branch, evaluate, select, synthesize)
- Leaves: final conclusions or pruned branches

The free algebra precisely captures "all possible ToT executions." ∎

### Significance

The free algebra contains all syntactically valid ToT trees. The LLM provides a **quotient**—it identifies trees that lead to the same answer. The gap between free algebra and LLM quotient is where errors occur.

---

## 4.6 Graph-of-Thoughts and Equations

Graph-of-thoughts (GoT) extends ToT by allowing:
- **Aggregation**: Multiple thoughts can merge
- **Refinement**: Thoughts can be iteratively improved
- **Cycles**: Limited looping until convergence

This is not a free algebra—it has **equations**.

### Definition 4.11 (GoT Operad with Equations)

**GoT** is a quotient of the free ToT operad by equations:

1. **Aggregation idempotence**: aggregate(x, x) = x
2. **Refinement convergence**: refine(refine(...refine(x)...)) eventually stabilizes
3. **Commutativity**: aggregate(x, y) = aggregate(y, x)

### Theorem 4.12

**GoT** forms an operad (quotient of a free operad by a congruence).

*Proof sketch.* The equations are compatible with operadic composition—they define a congruence. The quotient inherits the operad structure. ∎

### The DAG Structure

GoT trees modulo equations become DAGs (directed acyclic graphs):
- Aggregation merges branches (DAG sharing)
- Refinement creates sequential chains
- No cycles (equations ensure termination)

---

## 4.7 Proof Trees are Operadic

The connection to proof theory is direct.

### Theorem 4.13 (Proof Trees are Operad Algebra Elements)

Formal proofs in a logical system are elements of the free algebra for the inference rule operad.

*Argument.*

A proof tree is built by:
- Starting with axioms (nullary operations)
- Applying inference rules (n-ary operations) to derive new propositions
- Terminating at the goal proposition (root)

This is precisely the structure of the free algebra:
- Leaves are axioms
- Internal nodes are inference rules
- The root is the conclusion

Composition of proof trees (substituting lemmas into proofs) is operadic composition. ∎

### The Curry-Howard Connection

Under Curry-Howard (Chapter 2), proof trees correspond to program terms. The operad of inference rules corresponds to the operad of type constructors. This is the typed lambda calculus viewed operadically.

---

## 4.8 Operadic Structure of LLM Reasoning

### Proposition 4.14 (LLM Reasoning is Operadic)

When an LLM reasons about multiple premises to reach a conclusion, it implicitly applies an operadic structure.

*Evidence.*

Consider the prompt:
```
Given:
1. All humans are mortal
2. Socrates is human

What can we conclude?
```

The LLM must:
1. Parse the premises (identify inputs)
2. Recognize the applicable rule (modus ponens / syllogism)
3. Apply the rule to produce the conclusion

This is exactly: select operation from operad, apply to inputs, generate output.

The LLM's "reasoning" is an approximate algebra for the reasoning operad.

### Where the Approximation Fails

The approximation fails when:

1. **Invalid rule selection**: LLM applies a rule that doesn't actually apply
2. **Premise confusion**: LLM mixes up which premise goes where
3. **Composition errors**: LLM loses track in multi-step derivations

These correspond to failures of the algebra homomorphism—the LLM interpretation doesn't perfectly respect operadic composition.

---

## 4.9 Operads vs. Monads: Complementary Structure

Monads and operads capture different aspects of reasoning:

| Aspect | Monad | Operad |
|--------|-------|--------|
| **Composition type** | Sequential (A → B → C) | Parallel ((A, B) → C) |
| **Effect handling** | Yes (uncertainty, traces) | No (pure operations) |
| **Arity** | Fixed (one input) | Variable (n inputs) |
| **Natural home** | Extended reasoning chains | Proof tree structure |

### Combining Monads and Operads

Real reasoning has both sequential and parallel structure. We need both.

**Definition 4.15** (Monadic Operad Algebra)

A **monadic operad algebra** for operad P and monad T is:
- A T-algebra A (carrier with monad structure)
- For each f ∈ P(n), a morphism ⟦f⟧ : Aⁿ → T(A)

The operations can have effects.

**Example**: ToT with traces is a monadic operad algebra where:
- Operad: ToT operations (branch, evaluate, synthesize)
- Monad: Writer(Trace)
- Each operation produces output AND trace

### Theorem 4.16 (Novel)

**Conjecture**: Effective LLM reasoning strategies correspond to monadic operad algebras satisfying coherence conditions. The coherence conditions are:

1. **Operadic associativity** (up to monad multiplication)
2. **Monadic naturality** (operations respect the monad structure)
3. **Compatibility** (sequential and parallel composition interact correctly)

We believe this characterizes the space of "reasonable" reasoning strategies.

---

## 4.10 Higher Operads and Complex Reasoning

For complex reasoning, we may need **higher operads**—operads with multiple levels of structure.

### Colored Operads

A **colored operad** (or multicategory) has:
- Multiple "colors" (types) of objects
- Operations can have inputs of different colors
- Type-checking: operations only compose when colors match

**Example**: In typed reasoning, premises have types (propositions, observations, axioms). Inference rules only apply to correctly-typed inputs.

### Higher-Dimensional Operads

A **2-operad** has:
- 1-morphisms (operations)
- 2-morphisms (transformations between operations)

This captures: not just which operations exist, but how they relate to each other.

**Application**: Proof equivalence. Two proofs might use different rules but establish the same result. A 2-morphism records this equivalence.

---

## 4.11 Operads in kgents

The kgents codebase implements operads directly:

```python
# From impl/claude/agents/operad.py (conceptual)
class Operad:
    def __init__(self):
        self.operations: Dict[str, Operation] = {}
        self.laws: List[Law] = []

    def compose(self, outer: Operation, *inner: Operation) -> Operation:
        """Operadic composition: plug inner operations into outer."""
        # Verify arities match
        assert outer.arity == len(inner)
        # Create composed operation
        return ComposedOperation(outer, inner)
```

The `TOWN_OPERAD` defines operations for agent town reasoning:
- citizen.deliberate: 1-ary (citizen reasons alone)
- coalition.negotiate: n-ary (n citizens reach consensus)
- town.decide: n-ary (all citizens vote)

These form an operad—they compose according to operadic laws.

---

## 4.12 Formal Summary

**Theorem 4.17** (Operadic Characterization)

| Structure | Operadic Interpretation |
|-----------|------------------------|
| Proof tree | Element of free algebra |
| Inference rule | n-ary operation |
| Rule composition | Operadic composition |
| ToT | Free algebra over branching operad |
| GoT | Quotient algebra by refinement/aggregation equations |
| LLM reasoning | Approximate algebra homomorphism |

**Proposition 4.18**

The structure of valid reasoning is operadic. Invalid reasoning corresponds to violations of the algebra homomorphism.

**Conjecture 4.19** (Novel)

There exists a "master reasoning operad" R such that:
1. All sound inference systems are algebras for quotients of R
2. Different logics correspond to different quotients
3. LLM reasoning approximates an algebra for R

This would unify classical, intuitionistic, linear, and other logics as different algebras for the same underlying operadic structure.

---

## 4.13 Exercises for the Reader

1. **Construct**: Define the operad for first-order logic. What are the operations? How does quantifier introduction work operadically?

2. **Verify**: Check that aggregation idempotence (aggregate(x,x) = x) is compatible with operadic composition.

3. **Explore**: What would a "probabilistic operad" look like, where operations have uncertain outputs?

4. **Contemplate**: In ToT, evaluation scores branches. Is evaluation an operadic operation, or something outside the operad structure?

---

*Previous: [Chapter 3: The Monad of Extended Reasoning](./03-monadic-reasoning.md)*
*Next: [Chapter 5: Sheaves and Coherent Belief](./05-sheaf-coherence.md)*
