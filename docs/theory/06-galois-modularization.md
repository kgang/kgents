# Chapter 6: Galois Modularization

> *"The loss IS the difficulty. The fixed point IS the agent. The strange loop IS the bootstrap."*

---

## 6.1 The Phenomenon

Here is a simple experiment you can try right now.

Give an LLM a prompt like this:

```
Write a function that parses JSON, validates the schema,
transforms the data, and outputs CSV.
```

Then ask: "Restructure this prompt into independent, composable modules."

The LLM will produce something like:

```
Module 1: Parse JSON input
Module 2: Validate against schema S
Module 3: Transform via mapping M
Module 4: Serialize to CSV
Composition: Module_1 >> Module_2 >> Module_3 >> Module_4
```

This looks helpful. We've gained explicit structure. But something has been lost.

The original prompt implied dependencies that didn't survive modularization. "Validate the schema" depends on knowing what schema—which comes from parsing. "Transform the data" needs to know *what* data and *what* transformations—which depend on the schema. These implicit connections, obvious in the original, are now hidden or absent.

This loss is not a bug. It's a fundamental feature of abstraction.

---

## 6.2 Why This Matters

The restructuring operation—call it R—appears simple. But it carries deep structure:

**Observation 1**: Information is lost. The implicit dependencies in the original prompt may not survive modularization.

**Observation 2**: Structure is gained. Compositionality becomes explicit. We can see how pieces connect.

**Observation 3**: The operation is approximately idempotent. Restructure a restructured prompt, and you get something similar. Eventually, repeated restructuring converges.

**Observation 4**: The loss correlates with difficulty. When modularization loses a lot, the task is probably hard. When it loses little, the task is probably easy.

These observations suggest mathematical structure. This chapter develops that structure.

**Thesis**: The restructuring operation R forms one half of a **Galois connection** with a reconstitution operation C. The failure of the round-trip to preserve everything—what we call **Galois loss**—is:

1. **Structurally necessary** (not a defect but a feature of abstraction)
2. **Quantifiable** (measurable via semantic distance)
3. **Predictive** (correlates with task complexity and failure probability)
4. **Generative** (fixed points have polynomial functor structure)

---

## 6.3 The Category of Prompts

To formalize, we need categories.

### Definition 6.1 (Prompt Category)

Let **Prompt** be the category where:
- **Objects**: Natural language prompts (strings with semantic content)
- **Morphisms**: Semantic-preserving transformations
- **Composition**: Sequential transformation
- **Identity**: The trivial restatement

**Remark**: This isn't a strict category in the traditional sense. Morphisms carry a "fidelity" annotation in [0,1]. Two morphisms compose, but the result's fidelity is at most the product of the components' fidelities.

Mathematically, **Prompt** is an **enriched category** over the monoidal category of fidelity scores. We'll often work with the underlying ordinary category, acknowledging that laws hold "up to fidelity."

### Definition 6.2 (Modular Prompt)

A **modular prompt** M is a tuple:

```
M = (Modules, Interfaces, Composition, Metadata)

where:
  Modules:     Set of atomic prompt fragments
  Interfaces:  Typing of inputs/outputs per module
  Composition: Partial order on Modules (dependency DAG)
  Metadata:    Annotations (rationale, constraints, etc.)
```

### Definition 6.3 (Modular Prompt Category)

Let **ModPrompt** be the category where:
- **Objects**: Modular prompts
- **Morphisms**: Structure-preserving maps (refinement, restructuring)
- **Composition**: Morphism composition
- **Identity**: Identity on structure

---

## 6.4 The Restructure Functor

### Definition 6.4 (Restructure)

```
R: Prompt → ModPrompt
R(P) = LLM("Decompose P into independent modules with explicit interfaces")
```

This isn't a pure mathematical function—it involves an LLM call. But we can treat it as a functor by abstracting over the particular LLM and focusing on the structural properties.

**Properties of R**:

1. **Preserves semantics** (approximately): The modular version should accomplish the same task
2. **Monotone**: More specific prompts yield more specific modules
3. **Non-unique**: The same prompt can have multiple valid modularizations

The non-uniqueness is important. When we write R(P), we mean "some valid modularization of P." Different runs might produce different results. This is where the Différance connection emerges—the unchosen modularizations are "ghost alternatives."

---

## 6.5 The Reconstitute Functor

### Definition 6.5 (Reconstitute)

```
C: ModPrompt → Prompt
C(M) = Flatten(M.Modules, M.Composition)
```

Reconstitution takes a modular prompt and flattens it back into a single prompt. This can be:
- Pure string concatenation with appropriate connectives
- LLM-assisted synthesis that produces coherent prose
- Any semantics-preserving flattening operation

**Properties of C**:

1. **Preserves semantics** (approximately): The flat version should accomplish the same task
2. **Monotone**: More structured modules yield more specific flat prompts
3. **Lossy**: Structure information is lost in flattening

---

## 6.6 The Galois Adjunction

Here is the central result.

### Theorem 6.6 (Galois Adjunction)

The pair (R, C) forms a **Galois connection**:

```
R(P) ≤ M  ⟺  P ≤ C(M)
```

where ≤ denotes the refinement preorder (more structured/specific).

*Intuition*. If the modularization of P refines M, then P refines the flattening of M. And conversely. The restructure and reconstitute operations are adjoint.

*Proof sketch*.
- R is monotone: More specific prompts yield more specific modules
- C is monotone: More structured modules yield more specific flat prompts
- The adjunction follows from the universal property: R produces the "most general" modularization; C produces the "most specific" flattening. □

### Corollary 6.7 (Galois Laws)

From the adjunction, we get:

```
C(R(P)) ≥ P    (reconstitution is at least as general)
R(C(M)) ≤ M    (re-restructuring is at most as specific)
```

These are the unit and counit of the adjunction. In classical Galois theory, they would be identities. Here, they're not—there's a gap. That gap is the Galois loss.

---

## 6.7 Galois Loss

### Definition 6.8 (Galois Loss)

The **Galois loss** of a prompt P under restructuring is:

```
L(P) = d(P, C(R(P)))
```

where d is a semantic distance metric.

*Intuition*. We restructure P into modules, then reconstitute. How different is the result from the original? That difference is the loss.

### Definition 6.9 (Dual Galois Loss)

The **dual loss** of a modular prompt M is:

```
L*(M) = d*(M, R(C(M)))
```

This measures structural loss: how much structure is lost when we flatten and re-modularize.

### Theorem 6.10 (Loss Asymmetry)

In general, L(P) ≠ L*(R(P)). The losses capture different phenomena:

- **L(P)**: Loss of implicit knowledge during abstraction
- **L*(M)**: Loss of structural affordances during concretization

### Definition 6.11 (Total Galois Loss)

```
L_total(P) = α · L(P) + β · L*(R(P))
```

where α, β are weighting factors (typically α = β = 0.5).

---

## 6.8 Measuring Loss in Practice

Galois loss is defined in terms of a semantic distance d. But what metric should we use?

### Candidate Metrics

**Cosine Embedding Distance**:
```python
def cosine_distance(a: str, b: str) -> float:
    emb_a = embed(a)  # e.g., text-embedding-3-small
    emb_b = embed(b)
    return 1 - cosine_similarity(emb_a, emb_b)
```

Pros: Fast, deterministic. Cons: Misses semantic nuance.

**LLM Judge**:
```python
async def llm_judge_distance(a: str, b: str) -> float:
    response = await llm.generate(
        f"Rate similarity from 0.0 (identical) to 1.0 (different):\n"
        f"Text A: {a}\nText B: {b}"
    )
    return float(response)
```

Pros: Captures nuance. Cons: Expensive, non-deterministic.

**BERTScore Inverse**:
```python
def bertscore_distance(a: str, b: str) -> float:
    _, _, F1 = bert_score([a], [b])
    return 1 - F1.item()
```

Pros: Balances speed and accuracy. Cons: Requires model loading.

**NLI Contradiction Score**:
```python
def nli_distance(a: str, b: str) -> float:
    result = nli_model(a, b)
    return result["contradiction"]
```

Pros: Detects semantic conflicts. Cons: May miss subtle differences.

### Empirical Question

Which metric best predicts task difficulty? This is an open empirical question. Preliminary evidence suggests BERTScore and LLM-judge correlate best with human judgments, but cosine distance is often "good enough" and much faster.

---

## 6.9 The Monoid Structure

Restructuring has interesting algebraic structure.

### Definition 6.12 (Restructuring Monoid)

Let R̃ be the closure of R under composition:

```
R̃ = {Rⁿ : n ∈ ℕ}
```

where R⁰ = Id and Rⁿ⁺¹ = R ∘ Rⁿ.

### Theorem 6.13 (Approximate Monoid Laws)

R̃ satisfies:

1. **Identity** (exact): R⁰ = Id
2. **Associativity** (up to ε): d(Rᵐ(Rⁿ(P)), Rᵐ⁺ⁿ(P)) < ε for large m, n
3. **Idempotence** (approximate): lim_{n→∞} d(Rⁿ(P), Rⁿ⁺¹(P)) = 0

*Interpretation*. Repeated restructuring converges. The "noise" from any single restructuring washes out. What remains is the fixed point.

**Remark**: This is a **monoid in the category of metric spaces**, not a strict algebraic monoid. The "up to ε" is fundamental, not a defect.

---

## 6.10 The Fixed-Point Characterization

What happens when restructuring converges?

### Definition 6.14 (Restructuring Fixed Point)

A prompt P is a **fixed point** of R if:

```
R(P) ≅ P    (isomorphic in ModPrompt)
```

*Intuition*. P is already maximally modular. Restructuring it produces essentially the same structure.

### Theorem 6.15 (Fixed Points are Polynomial)

**Proposition**. If P is a fixed point of R, then P admits polynomial functor structure:

```
P ≅ PolyAgent[S, A, B]

where:
  S = {module states in R(P)}
  A(s) = {valid inputs for module s}
  B = output type
```

*Proof sketch*.

1. Fixed point means P = R(P) (modular structure is stable)
2. The modules become positions in a polynomial
3. The interfaces become direction sets (allowed inputs per position)
4. The composition DAG becomes the transition function
5. This is exactly the PolyAgent signature □

### Corollary 6.16 (Polynomial Emergence)

**Conjecture**. Repeated restructuring converges to polynomial structure:

```
lim_{n→∞} Rⁿ(P) = Fix(R) ≅ PolyAgent
```

This provides an alternative derivation of PolyAgent from first principles. Instead of postulating polynomial structure, we derive it as the fixed point of iterated modularization.

---

## 6.11 Alternative Bootstrap: Galois vs. Traditional

We now have two paths to PolyAgent.

**Traditional Bootstrap** (from Chapter 2):

```
Observation: Agents have modes (states)
Insight:     Mode-dependent inputs require polynomial structure
Derivation:  Agent[A,B] generalizes to PolyAgent[S,A,B]
```

**Galois Bootstrap** (this chapter):

```
Observation: Restructuring is lossy compression
Insight:     Fixed points of lossy compression are self-describing
Derivation:  Fix(R) has polynomial structure by Theorem 6.15
```

### Theorem 6.17 (Bootstrap Equivalence)

**Conjecture**. Both derivations yield isomorphic polynomial structures:

```
PolyAgent_traditional ≅ PolyAgent_galois
```

*Proof sketch*.
- Traditional: States are explicit in the agent definition
- Galois: States emerge as stable module configurations
- The isomorphism maps state s to module configuration R^∞(encode(s)) □

The significance: PolyAgent isn't an arbitrary choice. It emerges from two independent derivations—state-based reasoning and fixed-point analysis of modularization.

---

## 6.12 The Lawvere Connection

Fixed points aren't accidental. They're necessary.

### Definition 6.18 (Lawvere Fixed-Point Setting)

Consider the category **End(Prompt)** of endofunctors on Prompt. R is an object in this category.

### Theorem 6.19 (Lawvere Instantiation)

By Lawvere's fixed-point theorem, if:

1. **Prompt** has sufficient self-referential capacity (it does: prompts can describe prompts)
2. R is surjective on objects (approximately true: any modular structure can be reached)

Then: There exists P such that R(P) ≅ P.

### Corollary 6.20

The existence of polynomial fixed points is **not contingent** but **necessary** given the self-referential nature of natural language.

*Intuition*. Because prompts can talk about prompts, and restructuring is a definable operation, there must be prompts that are "fixed under restructuring." These fixed points have polynomial structure.

---

## 6.13 TextGRAD Integration

Galois loss connects to gradient-based prompt optimization.

### Background: TextGRAD

TextGRAD (Yuksekgonul et al., 2023) treats natural language feedback as "textual gradients":

```
θ_{t+1} = θ_t - α · ∇_text L(θ_t)
```

where ∇_text is LLM-generated improvement feedback.

The framework treats prompts as parameters and natural language critique as gradients, enabling backpropagation through language.

### Theorem 6.21 (Loss-Gradient Correspondence)

**Proposition**. The Galois loss L(P) corresponds to the gradient magnitude in TextGRAD:

```
||∇_text L(P)|| ∝ L(P)
```

*Argument*.
- High Galois loss → much information lost in abstraction
- Much lost → much feedback needed to recover
- Much feedback = high gradient magnitude □

### Theorem 6.22 (Gradient Direction)

**Proposition**. The TextGRAD gradient direction is determined by the Galois defect:

```
∇_text L(P) ∝ C(R(P)) - P
```

*Interpretation*. The gradient points from P toward its reconstituted version—toward the "canonicalized" form.

### Algorithm 6.23 (Galois-Informed TextGRAD)

```python
async def galois_textgrad_step(prompt: str, llm: LLM) -> str:
    # Compute Galois decomposition
    modular = await llm.restructure(prompt)
    canonical = await llm.reconstitute(modular)

    # Compute gradient direction
    delta = semantic_diff(prompt, canonical)

    # Compute gradient magnitude (loss)
    loss = semantic_distance(prompt, canonical)

    # Apply gradient step
    if loss > 0:
        improved = await llm.apply_delta(prompt, delta, magnitude=loss)
        return improved
    else:
        return prompt  # At fixed point
```

The significance: TextGRAD's "find feedback and apply" is Galois modularization in disguise. The restructure/reconstitute round-trip reveals what's missing.

---

## 6.14 Différance Integration

The Galois connection illuminates ghost alternatives.

### From the Différance Protocol

> "Différance = difference + deferral. Every wiring decision simultaneously creates a difference (this path, not that one) and creates a deferral (the ghost path remains potentially explorable)."

### Theorem 6.24 (Galois-Différance Correspondence)

**Proposition**. Ghost alternatives in Différance are Galois-deferred structures:

```
Ghost alternatives ≅ Galois-deferred modularizations
```

*Argument*.
- When R(P) = M, many modularizations were possible
- The chosen M is the "actual"; alternatives are "ghosts"
- Galois loss L(P) = information content of the ghosts □

### Definition 6.25 (Deferral Cost)

The **cost** of deferring alternative A in favor of choice M is:

```
Cost(A | M) = d(C(A), C(M))
```

### Theorem 6.26 (Total Deferral Cost)

**Proposition**:

```
L(P) = E[Cost(A | R(P))]    (over alternatives A)
```

The Galois loss IS the expected cost of deferred alternatives.

*Intuition*. When you modularize a prompt, you choose one decomposition. The ghosts are the roads not taken. The loss measures how much those roads would have differed.

### Definition 6.27 (Galois Ghost Graph)

For a prompt P, the **Galois ghost graph** is:

```
GG(P) = (Nodes, Edges)

Nodes: {R_i(P) : all possible restructurings}
Edges: {(R_i, R_j) : d(C(R_i), C(R_j)) < ε}
```

This graph captures the space of possible modularizations and their relationships.

---

## 6.15 The 2-Categorical View

The phrase "up to fidelity" admits a deeper interpretation.

### Two Interpretations

**Metric Interpretation**: Fidelity is an ε-approximation:
```
f ≈_ε g  ⟺  d(f, g) < ε
```

**2-Categorical Interpretation**: Fidelity is a 2-morphism:
```
f ⟹ g  (a natural transformation from f to g)
```

Both are valid. The metric interpretation works for computation. The 2-categorical interpretation works for theory.

### Definition 6.28 (2-Category of Prompts)

Let **Prompt₂** be the 2-category:
- **0-cells**: Prompts
- **1-cells**: Restructuring/reconstitution operations
- **2-cells**: Semantic similarity transformations (fidelity witnesses)

### Definition 6.29 (Fidelity 2-Morphism)

A **fidelity witness** between P and C(R(P)) is:

```
φ: Id_P ⟹ C ∘ R

such that:
  φ_P: P → C(R(P)) is semantically faithful
  Naturality: φ commutes with further transformations
```

### Theorem 6.30 (Lax Adjunction)

**Proposition**. The Galois adjunction (R, C) is a **lax adjunction** in **Prompt₂**:

```
C ∘ R ≅ Id    (lax, via fidelity 2-morphism)
R ∘ C ≅ Id    (lax, via dual fidelity 2-morphism)
```

### Corollary 6.31

Galois loss is the **coherence data** of the lax adjunction—it measures how far the adjunction is from being strict.

---

## 6.16 Strange Loops and Self-Reference

When restructuring is applied to descriptions of restructuring, strange loops emerge.

### Definition 6.32 (Self-Referential Prompt)

A prompt P is **self-referential** if:

```
P describes the process that generates P
```

**Example**: The prompt "Explain how to decompose prompts into modules" is self-referential when restructured—the restructuring of this prompt demonstrates its own content.

### Definition 6.33 (Strange Loop)

A **strange loop** in **Prompt** is a sequence:

```
P₀ → R(P₀) → describe(R(P₀)) → R(describe(R(P₀))) → ...
```

where `describe` generates a meta-level prompt describing the structure.

### Theorem 6.34 (Strange Loop Convergence)

**Proposition**. Every strange loop converges to a fixed point:

```
lim_{n→∞} (R ∘ describe)ⁿ(P₀) = Fix(R ∘ describe)
```

### Corollary 6.35 (Self-Describing Polynomial)

The fixed point of R ∘ describe is a **self-describing polynomial functor**—a PolyAgent whose states include descriptions of itself.

This is the Gödelian structure: prompts that describe their own modularization, modularizations that describe themselves.

### Speculation 6.36 (Galois Incompleteness)

**Conjecture**. There exist prompts P such that:

```
P ≡ "R(⌜P⌝) fails to equal P"
```

This is the prompt-theoretic analog of the Gödel sentence. Some prompts cannot be modularized without loss—their "incompressibility" is intrinsic, not accidental.

*Intuition*. Just as Gödel showed that sufficiently powerful formal systems contain unprovable truths, the self-referential capacity of natural language ensures some prompts resist modularization.

---

## 6.17 Implementation: GaloisLoss Class

Here's how the theory manifests in code.

```python
from dataclasses import dataclass
from typing import Callable

@dataclass
class GaloisLoss:
    """Compute and analyze Galois loss for prompts."""

    llm: LLM
    metric: Callable[[str, str], float]

    async def compute(self, prompt: str) -> float:
        """Compute L(P) = d(P, C(R(P)))"""
        modular = await self.restructure(prompt)
        reconstituted = await self.reconstitute(modular)
        return self.metric(prompt, reconstituted)

    async def restructure(self, prompt: str) -> ModularPrompt:
        """R: Prompt → ModularPrompt"""
        response = await self.llm.generate(
            system="Decompose prompts into independent, composable modules.",
            user=f"Decompose this prompt into modules:\n\n{prompt}",
            response_format=ModularPromptSchema,
        )
        return ModularPrompt.parse(response)

    async def reconstitute(self, modular: ModularPrompt) -> str:
        """C: ModularPrompt → Prompt"""
        response = await self.llm.generate(
            system="Flatten modular prompts into coherent single prompts.",
            user=f"Flatten this modular prompt:\n\n{modular.to_string()}",
        )
        return response.strip()

    async def dual_loss(self, modular: ModularPrompt) -> float:
        """Compute L*(M) = d*(M, R(C(M)))"""
        flat = await self.reconstitute(modular)
        re_modular = await self.restructure(flat)
        return modular_distance(modular, re_modular)

    async def total_loss(self, prompt: str, alpha: float = 0.5) -> float:
        """Compute L_total = α·L(P) + (1-α)·L*(R(P))"""
        loss = await self.compute(prompt)
        modular = await self.restructure(prompt)
        dual = await self.dual_loss(modular)
        return alpha * loss + (1 - alpha) * dual
```

---

## 6.18 Implementation: Task Triage

Galois loss enables intelligent task routing.

```python
from dataclasses import dataclass, field
from enum import Enum

class Reality(Enum):
    DETERMINISTIC = "deterministic"
    PROBABILISTIC = "probabilistic"
    CHAOTIC = "chaotic"

@dataclass
class TriageThresholds:
    deterministic: float = 0.1
    probabilistic: float = 0.4

@dataclass
class TaskStrategy:
    classification: Reality
    approach: str
    expected_iterations: int | None
    confidence: float
    rationale: str
    recommendation: str | None = None

@dataclass
class TaskTriage:
    """Triage tasks based on Galois loss."""

    galois: GaloisLoss
    thresholds: TriageThresholds = field(default_factory=TriageThresholds)

    async def triage(self, prompt: str) -> TaskStrategy:
        """Classify task and recommend strategy."""
        loss = await self.galois.compute(prompt)

        if loss < self.thresholds.deterministic:
            return TaskStrategy(
                classification=Reality.DETERMINISTIC,
                approach="direct",
                expected_iterations=1,
                confidence=0.95,
                rationale=f"Low Galois loss ({loss:.3f}) indicates near-lossless modularization",
            )
        elif loss < self.thresholds.probabilistic:
            iterations = max(1, int(loss * 10))
            return TaskStrategy(
                classification=Reality.PROBABILISTIC,
                approach="iterative",
                expected_iterations=iterations,
                confidence=0.7,
                rationale=f"Moderate Galois loss ({loss:.3f}) suggests {iterations} iterations needed",
            )
        else:
            return TaskStrategy(
                classification=Reality.CHAOTIC,
                approach="decompose",
                expected_iterations=None,
                confidence=0.3,
                rationale=f"High Galois loss ({loss:.3f}) indicates task should be decomposed further",
                recommendation="Break into smaller subtasks or simplify requirements",
            )
```

---

## 6.19 Relationship to Other Concepts

How does Galois modularization connect to the rest of the theory?

| Existing Concept | Galois Analog |
|-----------------|---------------|
| PolyAgent[S,A,B] state machine | Fixed point of restructuring iteration |
| Holographic compression | Lossy but semantics-preserving modularization |
| Différance ghost alternatives | Deferred modules (could have structured differently) |
| Agent-DP value function | Loss as negative reward |
| TextGRAD gradients | Galois loss as gradient magnitude |
| Sheaf gluing | Modular sections that should compose |
| Monad bind | Sequential composition of modules |

The connections are deep. Galois modularization isn't isolated—it's woven through the entire categorical infrastructure.

---

## 6.20 Formal Summary

**Theorem 6.37** (Galois Characterization of Modularization)

| Concept | Mathematical Structure |
|---------|----------------------|
| Restructure R | Functor Prompt → ModPrompt |
| Reconstitute C | Functor ModPrompt → Prompt |
| (R, C) pair | Galois adjunction (lax) |
| Round-trip C∘R | Unit of adjunction, ≈ identity |
| Loss L(P) | Distance d(P, C(R(P))) |
| Fixed point | P where R(P) ≅ P |
| Fixed point structure | Polynomial functor PolyAgent[S,A,B] |

**Theorem 6.38** (Bootstrap Equivalence)

The polynomial functor structure emerges from two independent paths:
1. State-based derivation (traditional)
2. Fixed-point analysis (Galois)

Both yield isomorphic structures, suggesting PolyAgent is canonical.

**Conjecture 6.39** (Loss-Difficulty Correlation)

For a task T encoded as prompt P:

```
P(failure | T) ∝ L(P)
```

High Galois loss predicts high failure probability.

**Speculation 6.40** (Galois Incompleteness)

Some prompts resist modularization intrinsically. Their incompressibility is necessary, not contingent, arising from the self-referential capacity of natural language.

---

## 6.21 Exercises for the Reader

1. **Compute**: Take a complex prompt. Restructure it. Reconstitute it. Measure the difference. What was lost?

2. **Iterate**: Apply restructuring repeatedly until convergence. How many iterations? What does the fixed point look like?

3. **Compare**: Try different semantic distance metrics on the same prompt. Do they agree on which prompts have high loss?

4. **Self-reference**: Construct a prompt about modularization. Modularize it. What happens?

5. **Prediction**: Find tasks with varying difficulty. Compute their Galois loss. Does loss predict difficulty?

---

## 6.22 Open Questions

Several questions remain open:

**Q1**: What's the optimal semantic distance metric for measuring Galois loss?

**Q2**: Does Galois loss predict human-perceived difficulty, or just LLM difficulty?

**Q3**: Can Galois loss be reduced through better prompting? Or is it intrinsic to the task?

**Q4**: Is the loss-complexity correlation task-dependent? (Coding vs. writing vs. reasoning?)

**Q5**: What's the relationship between Galois loss and Kolmogorov complexity?

**Q6**: Can we characterize which prompts are "Galois incompressible"?

These questions point toward experimental work. Theory provides the framework; empirical investigation fills in the constants.

---

*Previous: [Chapter 5: Sheaf Coherence](./05-sheaf-coherence.md)*
*Next: [Chapter 7: Loss as Complexity](./07-galois-loss.md)*
