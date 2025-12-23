# Chapter 3: The Monad of Extended Reasoning

> *"Monads are the mathematician's answer to: 'what if things could go wrong?'"*

---

## 3.1 The Problem of Effects

Chapter 2 established that reasoning forms a category. But that treatment was idealized—each inference step deterministically produced exactly one result.

Real reasoning is messier:

- **Uncertainty**: An inference might fail, or succeed with varying confidence
- **Branching**: An inference might produce multiple possible conclusions
- **Context**: An inference might depend on accumulated background knowledge
- **Traces**: An inference produces not just a result but a record of how it was derived
- **Resources**: An inference might consume limited resources (time, memory, attention)

These are **computational effects**—aspects of computation beyond pure input-output functions. Category theory handles effects via **monads**.

---

## 3.2 Monads: The Full Definition

Recall from Chapter 1 that a monad is a functor with extra structure. Now we give the complete definition.

### Definition 3.1 (Monad)

A **monad** on a category C is a triple (T, η, μ) where:

1. **T : C → C** is an endofunctor
2. **η : Id_C ⇒ T** is a natural transformation called the **unit**
3. **μ : T² ⇒ T** is a natural transformation called the **multiplication**

Subject to the **monad laws**:

**Left unit**: μ ∘ Tη = id_T
```
     Tη
T ─────► TT
 │        │
 │   μ    │
id_T      │
 │        ▼
 └──────► T
```

**Right unit**: μ ∘ ηT = id_T
```
     ηT
T ─────► TT
 │        │
 │   μ    │
id_T      │
 │        ▼
 └──────► T
```

**Associativity**: μ ∘ μT = μ ∘ Tμ
```
       Tμ                    μT
TTT ─────► TT         TTT ─────► TT
 │          │           │          │
 │μT        │μ          │Tμ        │μ
 │          │           │          │
 ▼          ▼           ▼          ▼
TT ──────► T          TT ──────► T
      μ                      μ
```

### Intuition

Think of T(X) as "X with stuff attached":
- **Unit η**: Attach trivial stuff to a plain value
- **Multiplication μ**: Flatten nested stuff into single-layer stuff

The laws ensure that attaching stuff and flattening stuff behave coherently.

---

## 3.3 The Monad Zoo for Reasoning

Different effects correspond to different monads. Here is a taxonomy relevant to reasoning:

### 3.3.1 The Maybe Monad (Failure)

**Definition**: T(X) = X + 1 (X plus a distinguished "nothing" element)

- **Unit**: ηₓ(x) = Just(x)
- **Multiplication**: μₓ(Just(Just(x))) = Just(x), μₓ(Nothing) = Nothing, μₓ(Just(Nothing)) = Nothing

**Reasoning interpretation**: Inferences that might fail. If any step fails, the whole chain fails.

**Example in reasoning**:
```
"Attempt to prove A → B. If no proof exists, return Nothing."
```

### 3.3.2 The List Monad (Branching)

**Definition**: T(X) = List(X) = {finite lists with elements from X}

- **Unit**: ηₓ(x) = [x] (singleton list)
- **Multiplication**: μₓ = flatten (concatenate list of lists)
- **Functor action**: T(f)([x₁,...,xₙ]) = [f(x₁),...,f(xₙ)]

**Reasoning interpretation**: Inferences that produce multiple possible conclusions. All possibilities are tracked.

**Example in reasoning**:
```
"From A, we can conclude B or C or D."
→ Returns [B, C, D], a list of possibilities
```

### 3.3.3 The Probability Monad (Uncertainty)

**Definition**: T(X) = Dist(X) = {probability distributions over X with finite support}

- **Unit**: ηₓ(x) = δₓ (point mass at x)
- **Multiplication**: μₓ = "flatten" distributions (expectation over inner distribution)
- **Functor action**: Pushforward of distribution

**Reasoning interpretation**: Inferences that produce uncertain conclusions with associated probabilities.

**Example in reasoning**:
```
"From evidence E, conclude H with probability 0.7, not-H with probability 0.3."
→ Returns the distribution {H: 0.7, ¬H: 0.3}
```

### 3.3.4 The Writer Monad (Traces)

**Definition**: For a monoid (M, ·, e), define T(X) = X × M

- **Unit**: ηₓ(x) = (x, e) (pair with empty trace)
- **Multiplication**: μₓ((x, m₁), m₂) = (x, m₂ · m₁) (concatenate traces)
- **Functor action**: T(f)(x, m) = (f(x), m)

**Reasoning interpretation**: Inferences that produce both a conclusion AND a trace/explanation.

**Example in reasoning**:
```
"From A, conclude B because [explanation]."
→ Returns (B, "A implies B by rule R")
```

**This is the chain-of-thought monad.** The trace accumulates the "let me think step by step" reasoning.

### 3.3.5 The Reader Monad (Context)

**Definition**: For a fixed object E (the "environment"), define T(X) = E → X

- **Unit**: ηₓ(x) = λe. x (constant function)
- **Multiplication**: μₓ(f) = λe. f(e)(e) (pass environment to outer, then inner)
- **Functor action**: T(f)(g) = f ∘ g

**Reasoning interpretation**: Inferences that depend on background context.

**Example in reasoning**:
```
"Given context C (background knowledge), conclude B from A."
→ The inference is a function from contexts to conclusions
```

### 3.3.6 The State Monad (Mutable State)

**Definition**: For a fixed object S (the "state"), define T(X) = S → (X × S)

- **Unit**: ηₓ(x) = λs. (x, s) (return value, keep state)
- **Multiplication**: Complex—threads state through
- **Functor action**: T(f)(g) = λs. let (x, s') = g(s) in (f(x), s')

**Reasoning interpretation**: Inferences that read and modify a belief state.

**Example in reasoning**:
```
"Update my beliefs by incorporating evidence E."
→ Takes current belief state, returns conclusion and updated belief state
```

---

## 3.4 Kleisli Categories: Where Effectful Reasoning Lives

Given a monad T on category C, we construct a new category where morphisms are "T-effectful functions."

### Definition 3.2 (Kleisli Category)

The **Kleisli category** C_T has:

- **Objects**: Same as C
- **Morphisms**: Hom_{C_T}(A, B) = Hom_C(A, T(B))
- **Composition**: For f : A → T(B) and g : B → T(C):

  g ∘_K f = μ_C ∘ T(g) ∘ f

  (Apply f, lift g to act on T(B), then flatten)

- **Identity**: id_A = η_A : A → T(A)

### Theorem 3.3

C_T is a category. The Kleisli composition is associative and has identities.

*Proof.* Direct consequence of the monad laws. The monad laws are precisely the conditions needed for Kleisli composition to be associative and unital. ∎

### Intuition

A morphism A → T(B) in C_T is a "computation from A that produces B with effect T."

Kleisli composition chains these computations, handling the effects:
1. Run the first computation, get T(B)
2. Run the second computation "inside" T, get T(T(C))
3. Use multiplication μ to flatten T(T(C)) into T(C)

---

## 3.5 Chain-of-Thought is Kleisli Composition

**Theorem 3.4** (Chain-of-Thought as Kleisli)

Let **Reason** be a reasoning category (as in Chapter 2). Let Trace = Writer(String) be the writer monad over strings.

Chain-of-thought reasoning operates in the Kleisli category **Reason**_Trace.

*Argument.*

A chain-of-thought step is a function f : A → (B, String) that takes input A and produces:
- Output B (the conclusion)
- A string (the reasoning trace)

This is exactly a Kleisli morphism A → Trace(B).

When we chain multiple CoT steps, we:
1. Apply the first step: A → (B, trace₁)
2. Apply the second step to B: B → (C, trace₂)
3. Combine: A → (C, trace₁ ++ trace₂)

This is Kleisli composition in the Writer monad. The traces concatenate.

The monad laws ensure:
- **Left unit**: Starting with no trace, then reasoning, equals just reasoning
- **Right unit**: Reasoning, then ending with no additional trace, equals just reasoning
- **Associativity**: Grouping of steps doesn't affect final trace ∎

### Why "Thinking Step by Step" Helps

From this perspective, the effectiveness of CoT is not mysterious:

1. **More computation**: Each traced step is a full forward pass through the LLM. More steps = more computation.

2. **Externalized memory**: The trace is written to the context window, providing working memory that persists across steps.

3. **Error localization**: When reasoning fails, the trace shows where. This enables self-correction (or human intervention).

4. **Training signal alignment**: Models trained on step-by-step solutions have seen many examples of Kleisli composition. They're executing learned patterns.

---

## 3.6 Tree-of-Thoughts is Kleisli in the List Monad

**Theorem 3.5** (Tree-of-Thoughts as Kleisli)

Tree-of-thoughts operates in a Kleisli category for a monad combining List (branching) and Writer (traces).

*Argument.*

A ToT step is a function f : A → [(B, String)] that takes input A and produces:
- A list of (output, trace) pairs
- Each element is a possible continuation with its reasoning

This is a Kleisli morphism A → (List ∘ Writer)(B).

ToT composition:
1. Apply first step: A → [(B₁, t₁), (B₂, t₂), ...]
2. Apply second step to each Bᵢ: Bᵢ → [(C₁, s₁), (C₂, s₂), ...]
3. Collect all paths: [(C₁, t₁++s₁), (C₂, t₁++s₂), ..., (C₁, t₂++s₁), ...]

The tree structure IS the unfolded Kleisli composition. ∎

### The Evaluation Hook

ToT adds explicit evaluation (scoring branches). Categorically, this is a natural transformation:

eval : List × Writer ⇒ Scored

Where Scored(X) = X × ℝ (values with scores).

Evaluation doesn't change the monadic structure—it adds information used for pruning.

---

## 3.7 Self-Consistency and the Probability Monad

**Proposition 3.6** (Self-Consistency as Probabilistic Reasoning)

Self-consistency decoding can be viewed as:
1. Running multiple reasoning chains in the Dist monad
2. Taking the mode (most probable outcome) of the combined distribution

*Argument.*

Each reasoning chain is a sample from an implicit distribution over conclusions. Running N chains gives N samples. The majority vote approximates the mode.

More formally: Let each chain be drawn from Dist(Conclusion). Self-consistency estimates:

mode(∫ Dist(Conclusion) dChain)

The aggregation of independent chains is product in the probability monad. The vote is mode extraction. ∎

---

## 3.8 ReAct and the State Monad

**Proposition 3.7** (ReAct as State + Writer)

ReAct (reasoning interleaved with actions) operates in the Kleisli category for State × Writer:

T(X) = Environment → (X × Environment × Trace)

*Argument.*

Each ReAct step:
- Reads the environment (current state of external world)
- Produces a thought or action
- Potentially modifies the environment (via action)
- Produces a trace

Composition threads the environment through, exactly as in the State monad. The trace accumulates as in Writer. ∎

---

## 3.9 Monad Transformers: Combining Effects

Real reasoning has multiple effects simultaneously: branching AND traces AND uncertainty.

**Definition 3.8** (Monad Transformer)

A **monad transformer** is a systematic way to combine monads. For monads S and T, the transformer version S_T typically has:

S_T(X) = S(T(X)) or T(S(X))

with appropriately defined unit and multiplication.

### Example 3.9 (ListT over Writer)

The "branching with traces" monad:

ListT(Writer)(X) = List(X × String)

This is what ToT uses: lists of (conclusion, trace) pairs.

### Example 3.10 (StateT over List)

The "stateful branching" monad:

StateT(List)(X) = S → List(X × S)

This models: from a state, branch into multiple (result, new-state) pairs.

### The Combining Problem

Not all monad combinations yield monads. The monad laws may fail. This constrains which reasoning strategies can be coherently combined.

**Proposition 3.11**: ToT + ReAct (branching + stateful action) requires careful combination. Naively, actions in one branch could affect the environment seen by other branches—breaking the "independent exploration" intuition.

---

## 3.10 The Algebraic Laws as Rationality Constraints

The monad laws aren't arbitrary—they encode rationality constraints on extended reasoning.

### The Left Unit Law

μ ∘ ηT = id means: Starting with trivial effect, then having effect, equals just having effect.

**Rationality reading**: Adding "I will now reason" before actually reasoning shouldn't change the outcome.

### The Right Unit Law

μ ∘ Tη = id means: Having effect, then adding trivial effect at the end, equals just having effect.

**Rationality reading**: Adding "Thus concludes my reasoning" after actually reasoning shouldn't change the outcome.

### The Associativity Law

μ ∘ μT = μ ∘ Tμ means: Flattening three-deep effects can be done in either order.

**Rationality reading**: When reasoning has nested structure, the way you "un-nest" shouldn't matter. The final result depends only on the reasoning content, not the grouping.

### When Laws Fail

If a purported reasoning system violates monad laws, something is wrong:

- **Unit failure**: The system treats "no reasoning" differently depending on context. This suggests hidden state or context-dependence not modeled by the monad.

- **Associativity failure**: The system is sensitive to grouping/bracketing of reasoning steps. This could indicate interference between steps, or order-dependent side effects.

LLMs, we note, do not perfectly satisfy these laws. Their reasoning is approximately monadic—the laws hold statistically but not exactly. This approximate monadicity is a source of reasoning failures.

---

## 3.11 Formal Summary

**Theorem 3.12** (Monadic Characterization of Reasoning Strategies)

| Strategy | Monad | Kleisli morphism type |
|----------|-------|----------------------|
| Chain-of-Thought | Writer(Trace) | A → (B × Trace) |
| Tree-of-Thoughts | List × Writer | A → [(B × Trace)] |
| Self-Consistency | Dist | A → Dist(B) |
| ReAct | State × Writer | A → (Env → (B × Env × Trace)) |
| Reflexion | State | A → (Memory → (B × Memory)) |

**Corollary 3.13**

The effectiveness of these strategies is predicted by their monadic structure:
- CoT works because Writer correctly accumulates traces
- ToT works because List correctly explores branches
- Self-consistency works because Dist correctly models uncertainty
- ReAct works because State correctly threads environment

**Conjecture 3.14** (Novel)

New effective reasoning strategies will correspond to novel monads (or monad combinations) on reasoning categories. The space of monads constrains the space of coherent reasoning strategies.

---

*Previous: [Chapter 2: Reasoning as Morphism](./02-reasoning-as-morphism.md)*
*Next: [Chapter 4: Operads and Reasoning Grammar](./04-operadic-reasoning.md)*
