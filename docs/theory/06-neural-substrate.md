# Chapter 6: The Neural Substrate

> *"The map is not the territory—but the territory has surprising structure."*

---

## 6.1 From Abstraction to Mechanism

Chapters 2-5 developed categorical structures for reasoning: morphisms, monads, operads, sheaves. These are abstract—they describe the *form* of reasoning, not its *implementation*.

This chapter descends into the substrate. How do large language models actually compute? Where might categorical structures be instantiated in transformer architectures?

We must be careful here. The categorical theory stands on its own; it doesn't require neural vindication. But if neural mechanisms exhibit categorical structure, that's evidence the theory captures something real.

---

## 6.2 The Transformer Architecture

### 6.2.1 The Basic Structure

A transformer (Vaswani et al., 2017) processes sequences of tokens:

```
Input tokens: [t₁, t₂, ..., tₙ]
                    │
              Embedding
                    │
              ┌─────┴─────┐
              │  Layer 1  │ ← Attention + MLP
              ├───────────┤
              │  Layer 2  │ ← Attention + MLP
              ├───────────┤
              │    ...    │
              ├───────────┤
              │  Layer L  │ ← Attention + MLP
              └─────┬─────┘
                    │
              Output logits
                    │
              [p(next token)]
```

Each layer has two components:
- **Attention**: Allows tokens to "look at" other tokens
- **MLP** (feed-forward): Applies a learned function to each position

### 6.2.2 Attention Mechanism

The attention mechanism computes:

```
Attention(Q, K, V) = softmax(QK^T / √d) · V
```

Where:
- Q (Query): "What am I looking for?"
- K (Key): "What do I have to offer?"
- V (Value): "What information do I carry?"

The softmax creates a probability distribution over positions. Each position attends to other positions with weights determined by query-key similarity.

**Multi-head attention** runs multiple attention mechanisms in parallel, each with different learned Q, K, V projections.

### 6.2.3 The Residual Stream

Elhage et al. (2021) proposed the **residual stream** interpretation:

```
x₀ ──►[+]──►[+]──►[+]──► ... ──►[+]──► xₗ
       │     │     │             │
      Attn   Attn  Attn         Attn
       +     +     +             +
      MLP   MLP   MLP           MLP
```

The residual stream x is a high-dimensional vector (e.g., 12,288 dimensions for GPT-4) that accumulates information layer by layer. Each attention and MLP block **reads from** and **writes to** this stream.

The residual stream is the model's "working memory"—all communication between components happens through it.

---

## 6.3 Circuits: The Functional Units

### 6.3.1 What is a Circuit?

A **circuit** is a subnetwork that implements a specific computation. Circuits are composed of:
- **Attention heads**: Specific heads with identifiable functions
- **MLP neurons**: Individual neurons that activate for specific features
- **Connections**: How information flows between components

### 6.3.2 Induction Heads

The most well-understood circuit is the **induction head** (Olsson et al., 2022):

**Pattern**: When the model sees "A B ... A", predict "B"

**Mechanism**:
1. A "previous token head" (Layer 1) writes [what came before this token] to the residual stream
2. An "induction head" (Layer 2+) attends from the current "A" to the previous "A" by matching content
3. Reads [what came before previous A] = "B" from the residual stream
4. Predicts "B"

```
Sequence:  The cat sat. The cat [?]
                            │
                     Induction head attends
                            │
                     to previous "cat"
                            │
                     copies "sat"
```

**Significance**: This is the simplest "reasoning" circuit—it implements pattern completion.

### 6.3.3 Greater-Than Circuit

Hanna et al. (2023) reverse-engineered how models compare numbers:

**Task**: "Is 7 greater than 3?"

**Mechanism**:
1. Attention heads identify the numbers and comparison type
2. MLP layers compute relative magnitude
3. Result propagates to output

The circuit is distributed across multiple layers, with different components handling different aspects of the comparison.

### 6.3.4 Indirect Object Identification

Wang et al. (2022) identified the circuit for:

"John gave Mary the ball. Then Mary gave it to [?]"
→ Predict "John"

**Mechanism**:
1. "Name mover" heads copy names to later positions
2. "S-inhibition" heads suppress the subject of the current clause
3. The remaining name (John, not Mary) becomes the prediction

---

## 6.4 Superposition: More Concepts Than Dimensions

### 6.4.1 The Puzzle

GPT-4 has ~12,288 dimensions in its residual stream. But it represents millions of concepts. How?

**Answer**: Superposition (Elhage et al., 2022).

### 6.4.2 The Mechanism

In **superposition**, concepts are represented as *nearly-orthogonal* directions in a space too small for true orthogonality.

```
Traditional: Each concept gets its own dimension
             dim(concepts) ≤ dim(embedding)

Superposition: Concepts share dimensions
               dim(concepts) >> dim(embedding)
               but concepts are sparse (rarely co-active)
```

The key insight: if concepts are sparse (only a few active at once), nearly-orthogonal vectors don't interfere much.

**Mathematical model**:

Let f₁, ..., fₘ be m feature vectors in ℝⁿ (m >> n).

If each input activates only k << n features, and the fᵢ are "almost orthogonal" (|fᵢ · fⱼ| ≈ ε for i ≠ j), then:

Reconstruction error ≈ k · ε

With high probability, k sparse features can be recovered from their superposition.

### 6.4.3 Implications for Reasoning

Superposition means:
- The model stores many more "reasoning patterns" than dimensions
- Interference between patterns can cause errors
- The model's "reasoning" is inherently approximate

**Speculation**: Reasoning failures occur when superposition causes interference—when two concepts that should be distinct are represented by overlapping directions.

---

## 6.5 Attention as Soft Categorical Structure

### 6.5.1 Attention as Morphism

**Proposition 6.1** (Informal)

Attention implements a "soft morphism"—a probabilistic map from query positions to key positions.

Consider attention at position i:

```
αᵢⱼ = softmax(qᵢ · kⱼ / √d)

output_i = Σⱼ αᵢⱼ · vⱼ
```

The attention weights αᵢⱼ form a probability distribution over j. This is a "soft lookup"—position i queries, and gets a weighted combination of values.

**Categorical reading**: In a category enriched over probability distributions, αᵢ is a morphism from position i to the value space.

### 6.5.2 Composition of Attention

When attention layers compose:

```
Layer 1: Token i attends to tokens {j}
Layer 2: Token i (now updated) attends to tokens {k}
```

Information flows: j → i → k (via attention hops)

**Proposition 6.2**: Multi-layer attention implements "multi-hop reasoning"—information can traverse multiple attention steps.

This is composition, but **soft** composition—each step is probabilistic, errors accumulate.

### 6.5.3 The Binding Problem Revisited

In symbolic reasoning, variables bind:

```
∀x. P(x) → Q(x)
P(Socrates)
∴ Q(Socrates)
```

The variable x is bound to Socrates—a discrete, exact operation.

In attention, binding is soft:

```
"All humans are mortal. Socrates is human."

Attention weights:
  "mortal" attends to "humans" (0.4) and "Socrates" (0.3) and others
  "Socrates" attends to "human" (0.5) and "mortal" (0.2)
```

There's no discrete binding of Socrates to the variable x. Instead, there's a soft association mediated by attention.

**Consequence**: The model can "lose" the binding. In long chains, the association between Socrates and mortality can decay or interfere with other associations.

---

## 6.6 The Residual Stream as Computation Medium

### 6.6.1 Residual Stream Semantics

**Speculation 6.3**: The residual stream has emergent "semantic directions."

Evidence from probing studies (Tenney et al., 2019; Hewitt & Manning, 2019):
- Linear directions correspond to syntactic properties (part of speech, dependency relations)
- Linear directions correspond to semantic properties (sentiment, topic)

The residual stream is not just a bag of numbers—it has interpretable structure.

### 6.6.2 Reasoning in the Residual Stream

**Conjecture 6.4**: Reasoning steps correspond to trajectories through residual stream space.

When the model "reasons":
1. Initial state: Encoding of the problem
2. Layer-by-layer updates: Attention reads relevant information, MLP transforms
3. Final state: Encoding of the answer

The trajectory from initial to final state IS the computation.

**Connection to morphisms**: If we interpret residual stream states as "objects" and layer transitions as "morphisms," the transformer defines a category:
- Objects: Points in residual stream space
- Morphisms: Layer-induced transformations
- Composition: Sequential layer application

### 6.6.3 The Geometry of Reasoning

**Proposition 6.5** (Speculative): Similar reasoning patterns trace similar geometric paths.

Evidence:
- Activation patching studies show specific layers are causal for specific computations
- Different problems requiring the same reasoning type activate similar layer patterns

This suggests a "geometry of reasoning"—a structure in activation space that categorical theory might formalize.

---

## 6.7 Circuits and Operads

### 6.7.1 Circuits as Operations

Consider a circuit that implements a specific reasoning step (e.g., modus ponens).

**Inputs**: Encodings of premises in the residual stream
**Output**: Encoding of conclusion in the residual stream

This is an n-ary operation: n inputs → 1 output.

**Proposition 6.6**: Circuits form (approximate) operations in a reasoning operad.

The composition of circuits (using one circuit's output as another's input) corresponds to operadic composition.

### 6.7.2 The Operad of Attention Patterns

Define an operad where:
- Operations = Attention patterns (which positions attend to which)
- Composition = Sequential attention (compose attention maps)

**Proposition 6.7**: This operad describes "attention routing"—the combinatorics of information flow.

Multi-hop attention (information flowing through multiple attention steps) is operadic composition in this operad.

---

## 6.8 Neural Scaling and Reasoning Capacity

### 6.8.1 Empirical Observations

- Larger models reason better (emergent abilities at scale)
- More layers allow deeper composition
- Wider layers allow more superposition

**Quantitative (Anthropic, 2024)**:
- Chain-of-thought gains scale with model size
- Tree-of-thoughts gains require minimum model capability
- Self-consistency improves with more samples AND model size

### 6.8.2 Categorical Interpretation

**Conjecture 6.8** (Speculative): Reasoning capacity corresponds to categorical complexity.

- **More layers** = Longer morphism chains (deeper composition)
- **Wider layers** = Richer Hom-sets (more morphisms between states)
- **More attention heads** = More parallel morphisms (multi-path reasoning)

The categorical "size" of the model's reasoning category grows with scale.

---

## 6.9 Limitations of the Neural Substrate

### 6.9.1 Softness

All neural operations are soft—differentiable, probabilistic, approximate. This contrasts with the crisp operations of symbolic reasoning.

**Consequence**: The monad/operad/sheaf laws hold only approximately. The error is small for each step but can accumulate.

### 6.9.2 Fixed Depth

Transformers have fixed depth (number of layers). This bounds the complexity of composable reasoning.

**Consequence**: There's a maximum "proof depth" the model can handle in a single forward pass. Chain-of-thought circumvents this by serializing computation into token generation.

### 6.9.3 Context Window

The context window bounds working memory. Information beyond the window is inaccessible.

**Consequence**: Long reasoning chains must fit in context. This is a hard limit on reasoning "width."

### 6.9.4 Training Distribution

The model learns from its training distribution. Reasoning patterns not in training are not learned.

**Consequence**: The model's "operad" is limited to operations seen in training (or compositions thereof). Truly novel reasoning may be impossible.

---

## 6.10 Interpretability as Categorical Discovery

### 6.10.1 The Interpretability Program

Mechanistic interpretability aims to understand neural networks by identifying circuits and their functions.

**Key methods**:
- **Activation patching**: Change a component's activation, observe downstream effects
- **Probing**: Train linear classifiers on intermediate representations
- **Circuit analysis**: Identify minimal subnetworks sufficient for a task

### 6.10.2 Interpretability as Functorial Analysis

**Conjecture 6.9**: Mechanistic interpretability discovers the functors between:
- The "syntax" category (network structure: layers, heads, neurons)
- The "semantics" category (reasoning structure: morphisms, operations, coherence)

A good interpretation is a **faithful functor**—it preserves the categorical structure of reasoning while mapping it onto neural implementation.

### 6.10.3 Open Questions

- Does the induction head circuit implement a specific morphism class?
- Are there "universal" circuits that implement categorical operations (identity, composition)?
- Can we identify the neural analogue of monad multiplication or operadic composition?

---

## 6.11 Summary: The Neural-Categorical Interface

| Categorical Concept | Neural Substrate |
|--------------------|------------------|
| Object (reasoning state) | Residual stream activation |
| Morphism (inference step) | Layer transformation |
| Composition | Sequential layers |
| Monad (effects) | Attention + residual |
| Operad operation | Circuit |
| Sheaf gluing | Multi-path agreement |

The correspondence is not exact—neural implementation is soft, approximate, bounded. But the structural parallel is suggestive.

**Main claim**: The categorical structures we've developed (monads, operads, sheaves) provide a *lens* for understanding neural reasoning. The lens reveals structure that raw neural analysis might miss.

---

## 6.12 Exercises for the Reader

1. **Trace**: Describe how information flows through a 2-layer transformer when computing "A → B, A, therefore B."

2. **Hypothesize**: What circuit might implement conjunction introduction (A, B ⊢ A ∧ B)?

3. **Contemplate**: If superposition causes concepts to interfere, what are the categorical implications? (Hint: morphisms that should be distinct become "close.")

4. **Speculate**: Could you design an architecture where categorical laws hold exactly?

---

*Previous: [Chapter 5: Sheaves and Coherent Belief](./05-sheaf-coherence.md)*
*Next: [Chapter 7: The Neurosymbolic Bridge](./07-neurosymbolic-bridge.md)*
