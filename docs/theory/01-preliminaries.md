# Chapter 1: Mathematical Preliminaries

> *"Category theory is, essentially, the study of compositional structure."*
> — Brendan Fong & David Spivak

---

## 1.1 Purpose of This Chapter

This chapter introduces the mathematical vocabulary we need. Readers familiar with category theory may skim, noting any notational conventions. Readers new to the subject should work through carefully—the concepts here are the foundation on which everything else rests.

We cover: categories, functors, natural transformations, and the seeds of more advanced structures (monads, operads, sheaves) that later chapters develop fully.

Our approach is *structural* rather than *foundational*. We don't worry about set-theoretic subtleties or size issues. We care about the patterns that categories reveal.

---

## 1.2 Categories: The Basic Structure

### Definition 1.1 (Category)

A **category** C consists of:

1. A collection of **objects**, denoted Ob(C) or just "objects of C"
2. For each pair of objects A, B, a collection of **morphisms** (or **arrows**) from A to B, denoted Hom(A, B) or C(A, B)
3. For each object A, an **identity morphism** idₐ : A → A
4. For each pair of composable morphisms f : A → B and g : B → C, a **composite** g ∘ f : A → C

Subject to two laws:

- **Identity**: For all f : A → B, we have idB ∘ f = f = f ∘ idA
- **Associativity**: For all f : A → B, g : B → C, h : C → D, we have (h ∘ g) ∘ f = h ∘ (g ∘ f)

### Notation and Conventions

We write f : A → B to mean "f is a morphism from A to B." The object A is the **domain** (or source), and B is the **codomain** (or target).

Composition is read right-to-left: g ∘ f means "first f, then g." Some authors use left-to-right notation (f ; g or f >> g); we'll note when we do.

When the category is clear from context, we simply write Hom(A, B) for the morphisms from A to B.

### Example 1.2 (Set)

The category **Set** has:
- Objects: Sets
- Morphisms: Functions between sets
- Identity: The identity function idₐ(x) = x
- Composition: Function composition

This is perhaps the most familiar category—ordinary mathematical functions.

### Example 1.3 (Preorder as Category)

Any **preorder** (P, ≤) forms a category:
- Objects: Elements of P
- Morphisms: At most one morphism A → B, existing iff A ≤ B
- Composition: Transitivity of ≤
- Identity: Reflexivity of ≤

This example is instructive: a category can have at most one morphism between any pair of objects. The morphisms encode *that* a relationship holds, not *how*.

### Example 1.4 (Monoid as Category)

A **monoid** (M, ·, e) is a category with one object:
- Objects: A single object, call it ★
- Morphisms: Elements of M (each m ∈ M is a morphism ★ → ★)
- Composition: Monoid multiplication (m · n)
- Identity: The monoid identity e

This example shows that categories generalize both sets-with-functions and monoids. The concept is more general than either.

### Example 1.5 (Reasoning)

**Speculation**: Consider the category **Reason**:
- Objects: States of knowledge (what an agent believes at a moment)
- Morphisms: Inference steps (reasoning actions that transform one state to another)
- Composition: Chaining inferences
- Identity: The trivial inference (believe what you already believe)

Is this a valid category? The identity law is plausible (trivial inference composed with any inference equals that inference). Associativity says that grouping inference steps doesn't change the result—also plausible for valid reasoning.

We'll develop this more rigorously in Chapter 2.

---

## 1.3 Functors: Structure-Preserving Maps

A functor is a "morphism of categories"—a map that preserves the categorical structure.

### Definition 1.6 (Functor)

A **functor** F : C → D between categories C and D consists of:

1. A map on objects: For each object A in C, an object F(A) in D
2. A map on morphisms: For each morphism f : A → B in C, a morphism F(f) : F(A) → F(B) in D

Subject to two laws:

- **Preserves identity**: F(idₐ) = id_{F(A)}
- **Preserves composition**: F(g ∘ f) = F(g) ∘ F(f)

### Example 1.7 (Forgetful Functor)

The functor U : **Grp** → **Set** takes a group to its underlying set (forgetting the group structure). It sends:
- A group (G, ·, e, ⁻¹) to the set G
- A group homomorphism to the underlying function

This is called a **forgetful functor**—it "forgets" structure.

### Example 1.8 (Free Functor)

The functor F : **Set** → **Grp** takes a set to the free group on that set (the group of formal words with letters from the set). This is **left adjoint** to the forgetful functor—a concept we'll use later.

### Example 1.9 (Power Set Functor)

The functor P : **Set** → **Set** sends:
- A set X to its power set P(X) = {S : S ⊆ X}
- A function f : X → Y to the direct image: P(f)(S) = {f(x) : x ∈ S}

This functor will reappear when we discuss possibility and branching.

---

## 1.4 Natural Transformations: Morphisms Between Functors

If functors are morphisms between categories, natural transformations are morphisms between functors.

### Definition 1.10 (Natural Transformation)

Given functors F, G : C → D, a **natural transformation** α : F ⇒ G consists of:

For each object A in C, a morphism αₐ : F(A) → G(A) in D, called the **component at A**.

Subject to the **naturality condition**: For all morphisms f : A → B in C:

```
       αₐ
F(A) ────► G(A)
  │          │
F(f)│        │G(f)
  │          │
  ▼          ▼
F(B) ────► G(B)
       αB
```

The diagram commutes: G(f) ∘ αₐ = αB ∘ F(f).

### Intuition

A natural transformation is a "coherent family of morphisms." The naturality condition ensures that the components "fit together"—they don't depend on arbitrary choices that could vary between objects.

### Example 1.11 (List Concatenation)

Consider the list functor L : **Set** → **Set** that sends a set X to the set of finite lists with elements from X.

For any set X, define doubleₓ : L(X) → L(X) by doubling each list: [a, b, c] ↦ [a, b, c, a, b, c].

Is double a natural transformation from L to L? Check naturality: for f : X → Y,

```
L(f)(double([a,b])) = L(f)([a,b,a,b]) = [f(a),f(b),f(a),f(b)]
double(L(f)([a,b])) = double([f(a),f(b)]) = [f(a),f(b),f(a),f(b)]
```

Yes—the diagram commutes. Double is natural.

---

## 1.5 The Category of Categories

Categories, functors, and natural transformations themselves form a structure:

**Cat** is the (large) category where:
- Objects are categories
- Morphisms are functors
- Composition is functor composition

For fixed categories C and D, the functors from C to D form a category [C, D]:
- Objects are functors F : C → D
- Morphisms are natural transformations
- Composition is "vertical composition" of natural transformations

This self-referential structure—categories of categories, functors between them, transformations between those—is what gives category theory its power and its reputation for abstraction.

---

## 1.6 Special Morphisms

### Definition 1.12 (Isomorphism)

A morphism f : A → B is an **isomorphism** if there exists g : B → A such that:
- g ∘ f = idₐ
- f ∘ g = idB

We write A ≅ B if such an isomorphism exists.

### Definition 1.13 (Monomorphism and Epimorphism)

A morphism f : A → B is a **monomorphism** (or "mono") if it's left-cancellable:
For all g, h : Z → A, if f ∘ g = f ∘ h then g = h.

A morphism f : A → B is an **epimorphism** (or "epi") if it's right-cancellable:
For all g, h : B → Z, if g ∘ f = h ∘ f then g = h.

In **Set**, monomorphisms are injective functions; epimorphisms are surjective functions. But this correspondence doesn't hold in all categories—be careful with intuitions from sets.

---

## 1.7 Products and Coproducts

### Definition 1.14 (Product)

A **product** of objects A and B is an object A × B together with projection morphisms:
- π₁ : A × B → A
- π₂ : A × B → B

Satisfying the **universal property**: For any object Z with morphisms f : Z → A and g : Z → B, there exists a unique morphism ⟨f, g⟩ : Z → A × B such that π₁ ∘ ⟨f, g⟩ = f and π₂ ∘ ⟨f, g⟩ = g.

```
            Z
          ╱ │ ╲
        f╱  │  ╲g
        ╱   │⟨f,g⟩
       ▼    ▼    ▼
      A ◄── A×B ──► B
         π₁    π₂
```

### Definition 1.15 (Coproduct)

A **coproduct** of objects A and B is an object A + B together with injection morphisms:
- ι₁ : A → A + B
- ι₂ : B → A + B

Satisfying the dual universal property.

### Example

In **Set**:
- Product is Cartesian product: A × B = {(a, b) : a ∈ A, b ∈ B}
- Coproduct is disjoint union: A + B = {(a, "left") : a ∈ A} ∪ {(b, "right") : b ∈ B}

In programming terms: products are tuples/records; coproducts are sum types/variants.

---

## 1.8 Preview: Monads

A **monad** on a category C consists of:
- A functor T : C → C
- A natural transformation η : Id ⇒ T (called "unit" or "return")
- A natural transformation μ : T² ⇒ T (called "multiplication" or "join")

Satisfying associativity and unit laws.

**Intuition**: A monad wraps values with additional structure. The unit wraps a plain value; multiplication flattens nested wrapping.

We defer the full treatment to Chapter 3, but here's the connection to reasoning:

**Proposition** (informal): Chain-of-thought reasoning operates in the Kleisli category for the "reasoning trace" monad—a monad that wraps answers with their derivation history.

---

## 1.9 Preview: Operads

An **operad** O consists of:
- Operations O(n) for each n ≥ 0 (n-ary operations)
- Composition: ways to substitute operations into each other
- An identity operation in O(1)

Satisfying associativity and identity laws.

**Intuition**: An operad encodes a "grammar" of operations with multiple inputs. Where categories handle sequential composition (one output feeds one input), operads handle tree-like composition (many outputs feed many inputs).

We defer the full treatment to Chapter 4, but here's the connection:

**Proposition** (informal): The structure of proof trees is operadic. Inference rules are operations; proof construction is operadic composition.

---

## 1.10 Preview: Sheaves

A **sheaf** on a topological space X (or more generally, on a category with a Grothendieck topology) assigns data to open sets such that:
1. Data can be restricted to smaller open sets
2. Compatible local data uniquely glues to global data

**Intuition**: Sheaves capture the relationship between local and global. They answer: when can you assemble a global picture from local pieces?

We defer the full treatment to Chapter 5, but here's the connection:

**Proposition** (informal): Multi-agent reasoning satisfies a sheaf condition when agents' local beliefs can be consistently glued into global consensus.

---

## 1.11 The Categorical Method

Why use categories instead of more familiar structures? The categorical method offers:

**Abstraction without vacuity**: Categories abstract common patterns, but the abstraction is *useful*—it reveals structure that would be hidden in specific instances.

**Compositional reasoning**: Categories make composition primary. Instead of analyzing complex systems directly, we analyze their components and how components compose.

**Universal properties**: Rather than constructing objects explicitly, categories characterize them by their relationships. This often reveals the "right" definition that ad-hoc constructions miss.

**Transfer of intuition**: Once you understand a concept categorically, you can apply it in any category. Intuitions from **Set** transfer to **Vect**, **Top**, or our custom reasoning categories.

**Invariant under isomorphism**: Categorical concepts don't distinguish isomorphic objects. This forces us to focus on structural properties, not accidental implementation details.

---

## 1.12 Notation Summary

| Symbol | Meaning |
|--------|---------|
| C, D | Categories |
| A, B, X, Y | Objects |
| f : A → B | Morphism from A to B |
| g ∘ f | Composition (first f, then g) |
| idₐ | Identity morphism on A |
| Hom(A, B) | Morphisms from A to B |
| F : C → D | Functor from C to D |
| α : F ⇒ G | Natural transformation from F to G |
| A × B | Product of A and B |
| A + B | Coproduct of A and B |
| A ≅ B | A and B are isomorphic |
| T | Monad (functor part) |
| η, μ | Unit and multiplication of monad |
| O(n) | n-ary operations of operad O |

---

## 1.13 Exercises for the Reader

1. **Verify**: Show that the category of monoids and monoid homomorphisms (**Mon**) is indeed a category.

2. **Contemplate**: In the preorder category (Example 1.3), what is an isomorphism? What does this say about the structure?

3. **Construct**: Define a functor from the category of directed graphs to **Set** that sends a graph to its set of vertices. What does this functor "forget"?

4. **Check naturality**: For the "length" function len : List(X) → ℕ (sending a list to its length), verify whether it forms a natural transformation from the List functor to a constant functor.

5. **Anticipate**: In a category of "reasoning states," what would a product represent? What about a coproduct?

---

*Previous: [Chapter 0: Overture](./00-overture.md)*
*Next: [Chapter 2: Reasoning as Morphism](./02-reasoning-as-morphism.md)*
