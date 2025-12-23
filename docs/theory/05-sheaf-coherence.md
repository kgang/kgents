# Chapter 5: Sheaves and Coherent Belief

> *"The whole is more than the sum of its parts—but only when the parts fit together."*

---

## 5.1 The Local-to-Global Problem

Consider a team of researchers, each expert in their own domain:
- Alice knows physics
- Bob knows chemistry
- Carol knows biology

They must answer: "Is this drug safe?"

Each can provide local reasoning from their expertise. But can their local conclusions combine into a global answer? Only if their conclusions are **compatible**—they don't contradict on shared ground.

This is the **local-to-global problem**: When do local pieces of information assemble into a coherent global picture?

Sheaf theory provides the mathematical framework. A sheaf is a structure that answers: "Given local data, when can it glue into global data, and when is that gluing unique?"

---

## 5.2 Sheaves: The Basic Intuition

### The Classic Example: Continuous Functions

Consider the real line ℝ and continuous functions on it.

For any open interval U ⊆ ℝ, let F(U) = {continuous functions on U}.

**Restriction**: If V ⊆ U, any function on U restricts to a function on V.

**Gluing**: If U = U₁ ∪ U₂ and we have:
- f₁ continuous on U₁
- f₂ continuous on U₂
- f₁ and f₂ agree on U₁ ∩ U₂

Then there's a unique continuous function f on U that restricts to f₁ on U₁ and f₂ on U₂.

This is the sheaf property: **compatible local data uniquely determines global data**.

---

## 5.3 Sheaves: The Formal Definition

### Definition 5.1 (Presheaf)

Let X be a topological space. A **presheaf** F on X is:
- For each open set U ⊆ X, a set F(U) (the "sections over U")
- For each inclusion V ⊆ U, a function ρᵤᵥ : F(U) → F(V) (the "restriction")

Such that:
- ρᵤᵤ = identity
- ρᵤᵥ ∘ ρᵥW = ρᵤW (restriction is transitive)

### Definition 5.2 (Sheaf)

A presheaf F is a **sheaf** if it satisfies:

**Locality**: If {Uᵢ} covers U and s, t ∈ F(U) with ρᵤᵤᵢ(s) = ρᵤᵤᵢ(t) for all i, then s = t.

(If two sections agree on every piece of a cover, they're equal.)

**Gluing**: If {Uᵢ} covers U and we have sections sᵢ ∈ F(Uᵢ) with ρᵤᵢ(Uᵢ∩Uⱼ)(sᵢ) = ρᵤⱼ(Uᵢ∩Uⱼ)(sⱼ) for all i,j, then there exists s ∈ F(U) with ρᵤᵤᵢ(s) = sᵢ for all i.

(Compatible local sections glue to a global section.)

### Categorical Reformulation

A presheaf on X is a functor F : Open(X)ᵒᵖ → **Set**, where Open(X) is the category of open sets ordered by inclusion.

The sheaf condition is expressed via **equalizer diagrams**:

```
F(U) ──► ∏ᵢ F(Uᵢ) ════► ∏ᵢⱼ F(Uᵢ ∩ Uⱼ)
```

F(U) is the equalizer of the two arrows to the product over intersections.

---

## 5.4 Belief Sheaves

### Definition 5.3 (Belief Presheaf)

Let A be a space of "agents" or "perspectives." A **belief presheaf** is:
- For each subset S ⊆ A (a subgroup of agents), a set Belief(S) of possible belief states
- For each S' ⊆ S, a restriction Belief(S) → Belief(S') (restricting to a subgroup's shared beliefs)

### Definition 5.4 (Belief Sheaf)

A belief presheaf is a **belief sheaf** if:
- **Locality**: If subgroups' beliefs determine the whole group's beliefs, they're equal
- **Gluing**: Compatible beliefs of overlapping subgroups determine a unique group belief

### Example 5.5 (Expert Panel)

Agents: {Alice (physics), Bob (chemistry), Carol (biology)}

Belief(Alice) = physics conclusions
Belief(Bob) = chemistry conclusions
Belief(Carol) = biology conclusions
Belief(Alice, Bob) = physical chemistry conclusions
...
Belief(Alice, Bob, Carol) = integrated scientific conclusion

The sheaf condition: If Alice's and Bob's conclusions agree on physical chemistry, and Bob's and Carol's agree on biochemistry, then their individual conclusions glue to a consistent group conclusion.

---

## 5.5 Self-Consistency as Sheaf Gluing

**Theorem 5.6** (Self-Consistency is Approximate Sheaf Gluing)

Self-consistency decoding approximates sheaf gluing over the space of reasoning paths.

*Argument.*

**Setup**: Let X be the space of reasoning paths (traces from problem to answer). Each path p ∈ X produces a local section: the answer and reasoning at that path.

**Cover**: The N sampled paths {p₁, ..., pₙ} form a "cover" of the reasoning space (a sample, not a true cover).

**Compatibility**: Paths are "compatible" if they yield the same final answer.

**Gluing**: When paths are compatible, they glue to a high-confidence global answer.

**Self-consistency**: Sample N paths. Take the majority answer. This approximates:
1. Finding compatible paths (those that agree on the answer)
2. Gluing them (the majority answer is the "global section")
3. Confidence (agreement rate) measures how well the sheaf condition is satisfied

When paths disagree, the sheaf condition fails—there's no consistent global answer. Low agreement = low confidence. ∎

### Why Self-Consistency Improves Calibration

The sheaf condition provides a **coherence check**. High agreement means the sections are compatible—the reasoning is consistent. Low agreement means incompatibility—the reasoning is inconsistent.

Calibration improves because agreement rate correlates with correctness:
- Easy problems: Most paths agree → high confidence → usually correct
- Hard problems: Paths disagree → low confidence → often incorrect

The sheaf condition makes this correlation precise.

---

## 5.6 Multi-Agent Reasoning and Sheaf Descent

When multiple agents reason independently, sheaf theory describes when their conclusions unify.

### Definition 5.7 (Descent Data)

For a cover {Uᵢ} and presheaf F, **descent data** consists of:
- Sections sᵢ ∈ F(Uᵢ) for each i
- Isomorphisms φᵢⱼ : sᵢ|Uᵢⱼ → sⱼ|Uᵢⱼ on overlaps
- Coherence: φᵢₖ = φⱼₖ ∘ φᵢⱼ on triple overlaps

**Effective descent**: Descent data uniquely determines a global section.

### Theorem 5.8 (Multi-Agent Descent)

In multi-agent reasoning, agents' local beliefs constitute descent data. The beliefs unify to a global consensus iff the descent data is effective.

*Application.*

Consider agents A₁, A₂, A₃ with beliefs b₁, b₂, b₃.

**Overlaps**: On topics where agents have shared expertise:
- A₁ and A₂ must agree (or have a specified transformation φ₁₂)
- A₂ and A₃ must agree (or have φ₂₃)
- A₁ and A₃ must agree (or have φ₁₃)

**Coherence**: φ₁₃ must equal φ₂₃ ∘ φ₁₂ (agreements compose consistently)

If coherence holds, the beliefs glue to global consensus.
If coherence fails, no consistent global belief exists—the agents fundamentally disagree. ∎

---

## 5.7 The Dialectic as Cocone Construction

When the sheaf condition fails—when local beliefs don't glue—what can be done?

**Answer**: Construct a **cocone** instead.

### Definition 5.9 (Cocone)

Given objects Xᵢ and morphisms between them (the descent data), a **cocone** is:
- An object Y (the apex)
- Morphisms fᵢ : Xᵢ → Y for each i
- Compatibility: Whenever there's a morphism g : Xᵢ → Xⱼ in the diagram, fⱼ ∘ g = fᵢ

The **colimit** is the universal cocone—the "smallest" Y that all Xᵢ map into.

### The Dialectic Interpretation

When agents disagree:
- Each agent's belief Bᵢ is an object
- The "overlap" disagreements show they don't glue
- A dialectic synthesis S is a cocone: each Bᵢ maps to S

The synthesis doesn't eliminate disagreement—it provides a vantage from which all beliefs are visible.

### Theorem 5.10 (Dialectic as Colimit)

**Conjecture**: The dialectical synthesis of conflicting beliefs is (approximated by) the colimit of the belief diagram.

The colimit preserves all information from the local beliefs while identifying where they can be reconciled.

### kgents Fusion Pattern

In kgents, the fusion pattern implements dialectical synthesis:

```python
async def fuse(kent_view: Belief, claude_view: Belief) -> Synthesis:
    """
    Construct cocone over disagreeing beliefs.
    """
    # The synthesis is the apex
    synthesis = Synthesis()

    # Each view maps into the synthesis
    synthesis.incorporate(kent_view, source="kent")
    synthesis.incorporate(claude_view, source="claude")

    # The synthesis records both perspectives
    return synthesis
```

This is cocone construction: the Synthesis object is the apex; incorporate() defines the morphisms.

---

## 5.8 Sheaves on Categories (Grothendieck Topology)

The classical definition uses topological spaces. For reasoning, we need sheaves on **categories**.

### Definition 5.11 (Grothendieck Topology)

A **Grothendieck topology** J on a category C assigns to each object U a collection J(U) of "covering sieves"—collections of morphisms into U that are deemed to "cover" U.

Axioms ensure covering sieves behave like open covers.

### Definition 5.12 (Sheaf on a Site)

A presheaf F : Cᵒᵖ → **Set** is a **sheaf** for Grothendieck topology J if for every covering sieve S ∈ J(U):

F(U) ≅ lim(∏_{f ∈ S} F(dom(f)) ⇉ ∏_{f,g composable} F(dom(f)))

This generalizes the classical sheaf condition to arbitrary categories.

### Application to Reasoning

Let C be a category of "information contexts" (what an agent has access to).

A Grothendieck topology specifies which collections of contexts "cover" a larger context.

A belief sheaf then assigns beliefs to contexts, with the sheaf condition ensuring consistency across covers.

---

## 5.9 Coherence Conditions and Reasoning Validity

### Theorem 5.13 (Coherent Reasoning)

Reasoning is **coherent** if the belief presheaf is a sheaf. Incoherence corresponds to sheaf condition failure.

*Types of incoherence:*

1. **Locality failure**: Two reasoning paths claim to reach the same conclusion but differ in details. The "global conclusion" is ill-defined.

2. **Gluing failure**: Compatible local conclusions don't combine into a global conclusion. The inference rules don't mesh.

### Detecting Incoherence

**Proposition 5.14**: The degree of sheaf condition failure quantifies reasoning incoherence.

Define the **coherence gap**:

```
Gap(F, U, {Uᵢ}) = d(F(U), Glue({F(Uᵢ)}))
```

Where d is a distance measuring how far the actual global sections are from what gluing would produce.

For self-consistency: Gap ≈ (1 - agreement rate). High gap = low coherence.

---

## 5.10 Topos-Theoretic Perspective

Sheaves on a site form a **topos**—a category that behaves like the category of sets but with a richer internal logic.

### Definition 5.15 (Topos)

A **topos** is a category with:
- Finite limits
- Exponentials (function objects)
- A subobject classifier Ω

Toposes have an **internal logic**: propositions are subobjects of 1, and logical operations are defined internally.

### Speculation 5.16 (Reasoning Topos)

**Conjecture**: The category of belief sheaves on the agent space forms a topos. The internal logic of this topos IS the "logic of multi-agent reasoning."

In this topos:
- Truth values aren't just {T, F}—they're "who believes this and with what confidence"
- Implication A ⇒ B means "everyone who believes A also believes B"
- Quantifiers range over agents as well as propositions

This would give a formal semantics for reasoning about beliefs about beliefs—epistemic logic internalized in sheaf theory.

---

## 5.11 Computational Aspects

### Checking the Sheaf Condition

Given: Local sections {sᵢ} over a cover {Uᵢ}
Task: Check compatibility and compute gluing

**Algorithm** (for finite discrete case):
1. For each overlap Uᵢ ∩ Uⱼ, check sᵢ|Uᵢⱼ = sⱼ|Uᵢⱼ
2. If all checks pass, construct global section by union
3. If any check fails, return incompatibility

**Complexity**: O(n² · |section|) for n covering sets

For continuous/infinite cases, the check may be undecidable—a fundamental limitation.

### Approximating Gluing

When exact gluing fails, we can approximate:

1. **Majority gluing**: Where sections disagree, take majority
2. **Weighted gluing**: Weight by section confidence
3. **Mediation**: Find minimal modification to make sections compatible

Self-consistency uses majority gluing. More sophisticated schemes use weighted or mediated gluing.

---

## 5.12 Sheaves in kgents

### TownSheaf Implementation

```python
# Conceptual implementation
class TownSheaf:
    def sections(self, agent_subset: Set[Agent]) -> Set[Belief]:
        """Get possible beliefs for a subset of agents."""
        # Each subset has its own belief space
        return self.belief_space[frozenset(agent_subset)]

    def restrict(self, belief: Belief, larger: Set[Agent], smaller: Set[Agent]) -> Belief:
        """Restrict a belief to a smaller agent group."""
        # Project belief onto shared domain
        return belief.project_to(self.shared_domain(larger, smaller))

    def compatible(self, sections: Dict[Set[Agent], Belief]) -> bool:
        """Check if local beliefs can glue."""
        for (s1, b1), (s2, b2) in pairs(sections.items()):
            overlap = s1 & s2
            if overlap:
                r1 = self.restrict(b1, s1, overlap)
                r2 = self.restrict(b2, s2, overlap)
                if r1 != r2:
                    return False
        return True

    def glue(self, sections: Dict[Set[Agent], Belief]) -> Belief:
        """Glue compatible local beliefs into global."""
        assert self.compatible(sections)
        # Construct global belief from local pieces
        return GlobalBelief.from_sections(sections)
```

This implements the sheaf condition for agent beliefs.

---

## 5.13 Formal Summary

**Theorem 5.17** (Sheaf Characterization of Coherent Reasoning)

| Concept | Sheaf Interpretation |
|---------|---------------------|
| Local reasoning | Sections over subsets |
| Restriction | Projection to shared domain |
| Compatibility | Agreement on overlaps |
| Global consensus | Glued section |
| Disagreement | Sheaf condition failure |
| Dialectic synthesis | Colimit/cocone construction |

**Proposition 5.18**

Self-consistency decoding approximates sheaf gluing. Agreement rate measures coherence.

**Conjecture 5.19** (Novel)

The space of "rational" multi-agent reasoning strategies is characterized by sheaves on the agent category satisfying:
1. **Locality** (beliefs determined by restrictions)
2. **Gluing** (compatible beliefs unify)
3. **Descent** (global beliefs decompose into local)

Violations of these conditions correspond to specific types of reasoning failures.

---

## 5.14 Exercises for the Reader

1. **Construct**: Define a belief sheaf for three agents with pairwise overlapping expertise. When do their beliefs glue?

2. **Compute**: For self-consistency with N=10 samples, 7 agreeing on answer A, compute the coherence gap.

3. **Explore**: What happens when the "cover" in self-consistency doesn't actually cover the reasoning space? (Sampling bias)

4. **Contemplate**: In the dialectic-as-colimit interpretation, what is the "universal property" of the synthesis?

---

*Previous: [Chapter 4: Operads and Reasoning Grammar](./04-operadic-reasoning.md)*
*Next: [Chapter 6: The Neural Substrate](./06-neural-substrate.md)*
