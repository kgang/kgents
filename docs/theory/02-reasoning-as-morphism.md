# Chapter 2: Reasoning as Morphism

> *"The structure of justification mirrors the structure of composition."*

---

## 2.1 The Fundamental Insight

This chapter develops the central claim: **reasoning is categorical**. More precisely, inference steps are morphisms, and valid reasoning satisfies categorical laws.

This is not merely a metaphor or analogy. We will show that the structure of deductive reasoning, inductive reasoning, and abductive reasoning all exhibit categorical structure—composition that is associative and has identities.

The payoff: once reasoning is categorical, we inherit the vast machinery of category theory. Functors become translations between reasoning systems. Natural transformations become systematic ways of transforming one inference method into another. Monads, operads, and sheaves become tools for understanding how reasoning extends, branches, and coheres.

---

## 2.2 The Category of Propositions and Proofs

We begin with the most well-behaved case: classical propositional logic.

### Definition 2.1 (The Category **Prop**)

Let **Prop** be the category where:
- **Objects**: Propositions (well-formed formulas in propositional logic)
- **Morphisms Hom(A, B)**: Proofs that A entails B (written A ⊢ B)
- **Composition**: If p : A ⊢ B and q : B ⊢ C, then q ∘ p : A ⊢ C is obtained by chaining the proofs
- **Identity**: For each A, the trivial proof idₐ : A ⊢ A (the proof that A entails itself)

### Theorem 2.2

**Prop** is a category.

*Proof.*

**Identity law**: We must show that for any proof p : A ⊢ B, we have idB ∘ p = p = p ∘ idₐ.

The composition idB ∘ p is "prove A ⊢ B using p, then prove B ⊢ B trivially." This yields the same conclusion as p alone. Similarly for p ∘ idₐ.

More formally: in proof theory, we identify proofs that yield the same derivation tree (up to trivial extensions). The identity proof adds no inferential content.

**Associativity**: For proofs p : A ⊢ B, q : B ⊢ C, r : C ⊢ D:

(r ∘ q) ∘ p chains p to (q chained to r).
r ∘ (q ∘ p) chains (p chained to q) to r.

Both result in a proof from A to D that passes through B and C in order. The grouping of the chaining doesn't affect the result. ∎

### Remark 2.3 (Proof Identity)

The claim that "proofs that yield the same derivation tree are equal" is a design choice. We could instead distinguish proofs by their full derivation history. This leads to a **2-category** where morphisms between proofs record how proofs relate—we'll touch on this in Chapter 9.

For now, we adopt the coarser equality where proofs are equal if they establish the same entailment.

---

## 2.3 The Curry-Howard Perspective

The category **Prop** is intimately connected to programming via the **Curry-Howard correspondence**.

### Theorem 2.4 (Curry-Howard Isomorphism, Informal)

There is an isomorphism:

| Logic | Type Theory |
|-------|-------------|
| Propositions | Types |
| Proofs A ⊢ B | Programs of type A → B |
| Composition of proofs | Function composition |
| Entailment | Inhabitation |

Under this correspondence, **Prop** is isomorphic to a category of types and functions.

### Example 2.5

The logical rule *modus ponens*:
```
A    A → B
──────────
    B
```

Corresponds to function application:
```
a : A    f : A → B
──────────────────
    f(a) : B
```

The proof IS a program. The program IS a proof.

### Significance for Reasoning

Curry-Howard tells us that **reasoning has computational content**. A proof doesn't just establish that a conclusion holds; it provides a *method* for transforming evidence for the premises into evidence for the conclusion.

When an LLM "reasons," it is—in some approximate sense—computing these transformations.

---

## 2.4 Enriched Reasoning: The Weighted Case

Classical proofs are binary: either A ⊢ B or not. But real reasoning involves degrees: some inferences are stronger than others.

### Definition 2.6 (Weighted Category of Reasoning)

Fix a **quantale** (V, ⊗, 1)—a complete lattice with a monoidal structure. Common examples:
- ([0,1], ×, 1): probabilities with multiplication
- ([0,∞], +, 0): costs with addition (often written as ([0,∞]^op, +, 0) for "the lower the better")
- ({0,1}, ∧, 1): classical binary logic

A **V-enriched category of reasoning** has:
- **Objects**: Propositions or states
- **Morphisms Hom(A, B)**: An element of V, representing the "strength" of inference from A to B
- **Composition**: Hom(A, B) ⊗ Hom(B, C) → Hom(A, C) (combine weights)
- **Identity**: 1 ∈ Hom(A, A) (the best possible self-evidence)

### Example 2.7 (Probabilistic Reasoning)

Let V = ([0,1], ×, 1). Then:
- Hom(A, B) = P(B | A), the conditional probability
- Composition: P(C | A) = P(C | B) × P(B | A) when B screens off A from C
- Identity: P(A | A) = 1

This gives the category **ProbReason** where morphisms are conditional probabilities.

**Proposition 2.8**: In **ProbReason**, composition gives an *upper bound* on inference strength (via the chain rule), exact when intermediate steps are conditionally independent.

### Example 2.9 (Fuzzy Reasoning)

Let V = ([0,1], min, 1). Then:
- Hom(A, B) = degree to which A implies B
- Composition: min(Hom(A,B), Hom(B,C))
- Identity: Full implication from A to A

This models reasoning where the weakest link determines overall strength.

---

## 2.5 The Category of Belief States

So far, our objects have been propositions. But reasoning also transforms *belief states*—entire configurations of what an agent believes.

### Definition 2.10 (Belief State Category)

Let **Belief** be the category where:
- **Objects**: Belief states (formally: functions from propositions to credences, or sets of believed propositions, or probability distributions over worlds)
- **Morphisms**: Belief-revision operations (formally: functions from belief states to belief states that satisfy rationality constraints)
- **Composition**: Sequential belief revision
- **Identity**: The operation that leaves beliefs unchanged

### Proposition 2.11

**Belief** is a category, and it is related to **Prop** by a functor.

*Sketch.*

Define F : **Prop** → **Belief** by:
- F sends a proposition A to the belief state where A is fully believed
- F sends a proof p : A ⊢ B to the belief-revision operation that updates from believing A to believing B

This functor respects composition (chained proofs give chained belief updates) and identities. ∎

### The Bayesian Subcategory

**Bayes** is the subcategory of **Belief** where:
- Objects are probability distributions over some space of worlds
- Morphisms are Bayesian updates: P ↦ P(· | E) for evidence E

This is where probabilistic reasoning lives. The composition law is the chain rule for conditioning.

---

## 2.6 The General Pattern

We've seen several instantiations:

| Category | Objects | Morphisms |
|----------|---------|-----------|
| **Prop** | Propositions | Proofs |
| **ProbReason** | Propositions | Conditional probabilities |
| **Belief** | Belief states | Belief-revision operations |
| **Bayes** | Distributions | Bayesian updates |

What do they share?

**Theorem 2.12 (Reasoning Categories)**

A **reasoning category** is any category R where:
1. Objects represent epistemic states (what can be known or believed)
2. Morphisms represent rational transitions (valid ways to update)
3. Composition represents sequential reasoning
4. Identity represents epistemic stability

The categorical laws (associativity and identity) then capture:
- **Associativity**: The order of grouping reasoning steps doesn't affect the outcome
- **Identity**: Trivial reasoning (no change) is a valid reasoning step

### Why Associativity Matters

Consider three inference steps: A → B → C → D.

Associativity says: ((A → B) → C) → D = (A → B) → (C → D) = A → ((B → C) → D)

In words: you can "chunk" reasoning into subproofs however you like. The final conclusion is the same.

This seems obvious, but it's powerful. It means reasoning is **compositional**—you can analyze pieces independently and combine the analyses.

### Why Identity Matters

The identity morphism idₐ : A → A says: from A, you can (trivially) infer A.

This allows **reasoning by cases**: If A → C and B → C, and you know (A ∨ B), then by first "trivially staying at A" or "trivially staying at B" and then applying the relevant inference, you get C.

---

## 2.7 Morphism Classification

Not all morphisms are equal. We can classify them by properties:

### Definition 2.13 (Reversible Inference)

A morphism f : A → B is **reversible** (an isomorphism) if there exists g : B → A with g ∘ f = idₐ and f ∘ g = idB.

Reversible inferences are logical equivalences—A and B are "the same" informationally.

### Definition 2.14 (Deductive Inference)

A morphism f : A → B is **deductive** if it is a monomorphism: whenever f ∘ g = f ∘ h, we have g = h.

Deductive inferences are "information-preserving"—they don't confuse distinct starting points.

### Definition 2.15 (Lossy Inference)

A morphism f : A → B is **lossy** if it is not a monomorphism.

Lossy inferences discard information—multiple starting points could lead to the same state.

### Example 2.16

In propositional logic:
- A ∧ B → A is lossy (we lose information about B)
- A → A ∨ B is deductive (we can recover A via conjunction with truth of A)
- A ↔ ¬¬A is reversible (in classical logic)

---

## 2.8 Functors Between Reasoning Systems

Different reasoning systems can be connected by functors.

### Example 2.17 (Classical to Intuitionistic)

There is a functor F : **Prop_intuitionistic** → **Prop_classical** that embeds intuitionistic proofs into classical proofs (every intuitionistically valid proof is classically valid).

This functor is faithful but not full—there are classical proofs with no intuitionistic counterpart.

### Example 2.18 (Symbolic to Statistical)

**Conjecture**: There exists a functor S : **Prop** → **ProbReason** that interprets proofs as conditional probability updates:
- S sends proposition A to itself
- S sends proof p : A ⊢ B to the conditional probability P(B|A) = 1 (certainty)

This functor embeds symbolic reasoning into statistical reasoning as the "limit case" of certainty.

### Example 2.19 (Belief Revision Functors)

Different belief revision schemes (AGM revision, Jeffrey conditioning, etc.) define different endofunctors on **Belief**. Comparing these functors reveals their structural differences.

---

## 2.9 Toward Extended Reasoning

Plain categorical structure captures "pure" reasoning—each step deterministically produces a result. But real reasoning has:

- **Uncertainty**: steps might fail or have probabilistic outcomes
- **Branching**: steps might produce multiple possibilities
- **Context**: steps might depend on accumulated information
- **Traces**: steps produce not just results but records of derivation

These "effects" are not well-modeled by ordinary categories. We need **monads** (Chapter 3).

### Preview: The Chain-of-Thought Monad

Define the monad T : **Set** → **Set** by T(X) = X × String (pairs of values with their derivation traces).

- **Unit** η : X → T(X) sends x to (x, "") (value with empty trace)
- **Multiplication** μ : T(T(X)) → T(X) sends ((x, s₁), s₂) to (x, s₂ ++ s₁) (concatenate traces)

Chain-of-thought reasoning operates in the **Kleisli category** for this monad.

A function f : A → T(B) is a "traced inference"—it takes input A and produces output B along with a trace explaining how.

Kleisli composition chains these traced inferences, concatenating their traces.

**This is precisely what "let's think step by step" does in LLMs.**

---

## 2.10 Summary

We have established:

1. **Reasoning forms categories**: Inference steps are morphisms; composition is chaining; identities are trivial inferences.

2. **Categorical laws capture rationality constraints**: Associativity ensures compositional analysis; identity ensures vacuous reasoning is valid.

3. **Different reasoning systems = different categories**: Classical, intuitionistic, probabilistic, belief-revision—all are categories with the same structure, differing in their morphisms.

4. **Functors connect reasoning systems**: Embeddings, translations, and interpretations between systems are functors.

5. **Effects require monads**: Uncertainty, branching, and traces push us beyond plain categories into Kleisli categories—the subject of Chapter 3.

---

## 2.11 Formal Summary

**Theorem 2.20** (Reasoning as Category)

Any reasoning system satisfying:
- (R1) There exist objects (epistemic states)
- (R2) There exist morphisms (inference steps) between objects
- (R3) Morphisms compose associatively
- (R4) Each object has an identity morphism

forms a category, and inherits all categorical structure (functors, natural transformations, limits, colimits, adjunctions, etc.) as tools for analysis.

**Corollary 2.21**

Chain-of-thought, tree-of-thoughts, and self-consistency can be analyzed as categorical constructions (Kleisli categories, free algebras, and sheaf gluing, respectively) applied to appropriate reasoning categories.

---

*Previous: [Chapter 1: Mathematical Preliminaries](./01-preliminaries.md)*
*Next: [Chapter 3: The Monad of Extended Reasoning](./03-monadic-reasoning.md)*
