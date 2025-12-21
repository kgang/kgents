# Metatheory Heritage Formalization Plan

> *"The categorical foundation is being validated by the research community. We owe acknowledgment and extension."*

**Status**: Ready for Implementation
**Created**: 2025-12-21
**Source**: `brainstorming/2025-12-21-metatheory-self-consistency-refresh.md`
**Voice Anchors**: "Daring, bold, creative, opinionated but not gaudy" | "Depth over breadth"

---

## Overview

Transfer the metatheory research findings into formal specs. This involves:
1. Enshrining 4 papers as HERITAGE-level in `spec/heritage.md`
2. Adding AD-013 (Typed AGENTESE) to `spec/principles.md`
3. Creating a new spec for Proof-Generating ASHC

---

## Phase 1: Heritage Updates

### File: `spec/heritage.md`

Add **Part IV: Formalization Heritage** after the existing Part III.

#### Paper 1: Polynomial Functors (Niu & Spivak, Cambridge 2025)

**Why Heritage**: PolyAgent[S, A, B] IS a polynomial functor. This is the canonical mathematical foundation for kgents' entire agent model.

```markdown
### 10. Polynomial Functors: The Mathematical Ground

**Citation:**
@book{polynomial2025,
  title={Polynomial Functors: A Mathematical Theory of Interaction},
  author={Niu, Nelson and Spivak, David I.},
  publisher={Cambridge University Press},
  year={2025},
  url={https://arxiv.org/abs/2312.00990}
}

**Core Contribution:**
- Mode-dependent dynamical systems naturally recast within Poly
- PolyAgent[S, A, B] IS a polynomial functor: P(y) = Σ y^{directions(s)}
- Wiring diagrams for composition (= our Operad)
- At ACT 2022, 12/59 presentations referenced polynomial functors

**kgents Integration:**
| Poly Concept | kgents Mapping |
|--------------|----------------|
| Polynomial functor | `PolyAgent[S, A, B]` |
| Positions | Agent states/modes |
| Directions | Valid inputs per state |
| Substitution | Operad composition |
| Wiring diagram | Pipeline composition |

**Verification:**
- `impl/claude/agents/poly/_tests/test_polynomial.py`
- All domain polynomials inherit laws
```

#### Paper 2: Sheaves of Dynamical Systems (Robinson et al., Nov 2025)

**Why Heritage**: Formalizes exactly what kgents does: machines with ports, operad wiring, sheaf-valued algebras.

```markdown
### 11. Sheaves of Dynamical Systems

**Citation:**
@article{robinson2025,
  title={Sheaves of Dynamical Systems},
  author={Robinson, David I. and others},
  year={2025}
}

**Core Contribution:**
- Dynamical systems as machines with input/output ports
- Sheaf-valued algebras organize possible systems at interfaces
- Operad of wiring diagrams as composition grammar

**kgents Integration:**
| Sheaf Concept | kgents Mapping |
|---------------|----------------|
| Machine with ports | PolyAgent with modes |
| Wiring diagram | Operad operation |
| Sheaf-valued algebra | Domain-specific sheaf |
| Global section | Coherent agent composition |

**Verification:**
- `impl/claude/agents/sheaf/_tests/test_coherence.py`
- TownSheaf, ProjectSheaf instantiate pattern
```

#### Paper 3: AI + Formal Verification (Kleppmann, Dec 2025)

**Why Heritage**: The insight that LLM hallucinations don't matter for proofs validates ASHC → proof generation vision.

```markdown
### 12. AI + Formal Verification

**Citation:**
@article{kleppmann2025,
  title={Prediction: AI will make formal verification go mainstream},
  author={Kleppmann, Martin},
  year={2025},
  url={https://martin.kleppmann.com/2025/12/08/ai-formal-verification.html}
}

**Core Insight:**
> "LLM hallucinations don't matter for proofs because proof checkers reject invalid proofs."

seL4 kernel: 8,700 lines C → 200,000 lines proof. If LLMs can generate proof attempts, formal verification becomes tractable.

**kgents Integration:**
| Kleppmann Insight | kgents Mapping |
|-------------------|----------------|
| LLM proof generation | ASHC → proof obligations |
| Proof checker as validator | Lean/Dafny/Verus integration |
| Verified lemmas | Causal graph as proven principles |

**Verification:**
- Future: `impl/claude/services/ashc/_tests/test_proof_generation.py`
```

#### Paper 4: Stigmergic Cognition (Synthese, June 2025)

**Why Heritage**: Validates Morning Coffee's pheromone model as not just coordination but cognitive substrate.

```markdown
### 13. Stigmergic Cognition

**Citation:**
@article{csa2025,
  title={Traces of Thinking: Stigmergic Cognition},
  journal={Synthese},
  year={2025},
  url={https://link.springer.com/article/10.1007/s11229-025-05074-8}
}

**Core Contribution:**
Coordinated Systems Approach (CSA): Many/all cognitive systems involve stigmergies—applies to humans, groups, higher animals, bacteria, plants.

**The Implication:** Cognition itself may be fundamentally stigmergic.

**kgents Integration:**
| CSA Concept | kgents Mapping |
|-------------|----------------|
| Stigmergic cognition | Morning Coffee pheromones |
| Environmental trace | Intent capture |
| Decay/reinforcement | `PheromoneDecay`, `reinforcement_cap` |
| Emergent coordination | Voice pattern emergence |

**Verification:**
- `impl/claude/services/liminal/coffee/_tests/test_voice_stigmergy.py`
```

#### Verification Matrix Addition

Add to the Verification Matrix table:

```markdown
| Polynomial Functors | PolyAgent IS polynomial functor | Polynomial laws verified | `agents/poly/_tests/test_polynomial.py` |
| Sheaves | Sheaf-valued composition | Coherence laws | `agents/sheaf/_tests/test_coherence.py` |
| Kleppmann | Proof generation from failures | ASHC proof obligations | `services/ashc/_tests/test_proof_generation.py` |
| CSA | Stigmergic cognition | Pheromone decay/reinforcement | `services/liminal/coffee/_tests/test_voice_stigmergy.py` |
```

---

## Phase 2: Architectural Decision

### File: `spec/principles.md`

Add **AD-013: Typed AGENTESE** after AD-012.

```markdown
### AD-013: Typed AGENTESE (2025-12-21)

> **AGENTESE paths SHALL have categorical types. Composition errors become type errors.**

**Context**: AGENTESE currently relies on runtime validation. The categorical type system formalizes composition validity at the path level. This connects to the Polynomial Functors heritage (§10)—paths are typed morphisms in the category of polynomial functors.

**Decision**: AGENTESE paths are typed morphisms:

```python
# Current (informal)
world.tools.bash.invoke(umwelt, command="ls")

# Typed (categorical)
invoke : (observer : Umwelt) → BashRequest → Witness[BashResult]
# Where Witness[A] is a type that proves the operation happened
```

**Type Rules:**
1. **Path composition requires type compatibility**: `path_a >> path_b` valid iff output type of `a` matches input type of `b`
2. **Aspect invocation has typed effects**: Effects declared in `@node` decorator are part of the type
3. **Observer determines valid inputs**: Mode-dependent typing via polynomial positions

**Connection to Polynomial Functors:**
- Path type = polynomial functor signature
- Composition = polynomial substitution
- Type error = invalid wiring diagram

**First Step**: Define `AGENTESEType` as a Protocol with `compose` method. Add type annotations to `@node` decorator.

**Consequences:**
1. Composition errors surface at import time, not runtime
2. Type annotations serve as documentation
3. IDE autocomplete becomes meaningful
4. Prepares for proof-generating ASHC (composition validity is provable)

**Anti-patterns:**
- Untyped paths that bypass the type system
- Runtime type checks that duplicate static analysis
- Overly complex types that obscure intent

**Implementation**: See `docs/skills/agentese-node-registration.md` (to be updated)

*Zen Principle: The type that generates composition errors at import time prevents runtime failures.*
```

---

## Phase 3: New Spec

### File: `spec/protocols/proof-generation.md`

Create new spec for Proof-Generating ASHC.

```markdown
# Proof-Generating ASHC

> *"Failures don't just update a causal graph—they generate proof obligations."*

**Status**: Conceptual
**Heritage**: Kleppmann (§12), Polynomial Functors (§10)
**Timeline**: 3-6 month horizon

---

## Purpose

Extend ASHC's evidence compilation to produce **formal proofs** that LLMs attempt to discharge.

Why this needs to exist: The ASHC metacompiler accumulates evidence from failed generations. But evidence without proof is merely statistical. With proof, the codebase becomes **provably correct** over time, not just statistically likely correct.

---

## The Core Insight

The equation changes when proof generation is LLM-assisted:
- Human effort: 23 lines proof per line code (seL4)
- LLM + checker: proof attempts are cheap; validation is mechanical

> "LLM hallucinations don't matter for proofs because proof checkers reject invalid proofs."
> — Martin Kleppmann

---

## Formal Definition

```
ProofObligation : FailedGeneration → (Spec, Property, Witness)

ProofSearch : ProofObligation → Proof | Timeout

VerifiedLemma : Proof × Checker → Lemma

ASHCWithProof : Evidence → ProofObligation* → Lemma*
```

The composition:
```
Spec → Generate N → Verify each → Select best → Output
                         ↓
                   Failures → ProofObligation
                         ↓
                   LLM proof search (Lean/Dafny/Verus)
                         ↓
                   VerifiedLemma for NEXT generation
```

---

## Integration with ASHC

| ASHC Concept | Proof Extension |
|--------------|-----------------|
| Evidence | Proof obligation |
| Causal graph | Lemma dependency graph |
| Nudge | Proof search direction |
| Learned prior | Verified lemma |
| Work bet | Proof attempt budget |

---

## AGENTESE Integration

```
concept.ashc.obligation    → Generate proof obligation from failure
concept.ashc.prove         → Attempt to discharge obligation
concept.ashc.lemma         → Query verified lemmas
concept.ashc.graph         → Visualize lemma dependency graph
```

---

## Laws

1. **Soundness**: `verified(lemma) → property_holds(lemma.property)`
   - Verified lemmas correspond to actual properties

2. **Monotonicity**: `lemmas(t+1) ⊇ lemmas(t)`
   - Lemma set only grows; proofs don't expire

3. **Compositionality**: `compose(lemma_a, lemma_b) → valid_proof`
   - Lemma composition yields valid proofs

---

## Integration with Typed AGENTESE (AD-013)

Typed AGENTESE provides the type annotations that become proof obligations:

```python
@node("world.tools.bash")
async def bash_invoke(
    observer: Umwelt,
    command: str,
) -> Witness[BashResult]:
    """
    Type signature generates proof obligation:
    ∀ observer, command. bash_invoke(observer, command) : Witness[BashResult]
    """
    ...
```

The type `Witness[BashResult]` is not just documentation—it's a theorem to prove.

---

## Examples

### Example 1: Composition Validity

```python
# Pipeline
pipeline = parse >> validate >> transform

# Proof obligation generated:
# ∀ input. parse(input) : Parsed
# ∀ parsed. validate(parsed) : Validated
# ∀ validated. transform(validated) : Output
# Therefore: pipeline(input) : Output
```

### Example 2: Failed Generation → Lemma

```python
# Generation fails because validate rejects malformed input
# ASHC extracts: "validate requires well-formed Parsed"
# Proof obligation: ∀ input. parse(input) → well_formed(parse(input))
# LLM attempts proof in Lean
# If successful: lemma added to dependency graph
# Next generation: LLM uses lemma to avoid same failure
```

---

## Anti-patterns

- **Proving everything**: Too expensive; prioritize critical paths
- **Ignoring failed proofs**: Signal of spec ambiguity—investigate
- **Manual proof editing**: Proofs should regenerate from spec
- **Proof hoarding**: Share lemmas across services via SynergyBus

---

## First Steps (Immediate Actions)

1. Add `ProofObligation` dataclass to ASHC contracts
2. On test failure, extract minimal proof obligation
3. Create `LeanBridge` or `DafnyBridge` for proof checking
4. Run experiment: 100 generations, measure proof discharge rate

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Proof generation too slow | Cache proven lemmas; prune proof search tree |
| LLM can't discharge obligation | Fall back to evidence-only mode |
| Proof checker integration complex | Start with Dafny (simpler than Lean) |
| Over-formalization | Only prove critical path properties |

---

## Cross-References

- **Heritage**: `spec/heritage.md` §12 (Kleppmann)
- **Typed AGENTESE**: `spec/principles.md` AD-013
- **ASHC Core**: `spec/protocols/ashc.md` (to be created)
- **Witness Service**: `spec/agents/witness.md`

---

*"The proof is not formal—it's empirical. Run the tree a thousand times, and the pattern of nudges IS the proof. Now we can run the proof checker a thousand times, and the pattern of verified lemmas IS the certificate."*
```

---

## Implementation Checklist

### Deliverable 1: Heritage Updates
- [ ] Add Part IV header to `spec/heritage.md`
- [ ] Add Paper 10: Polynomial Functors
- [ ] Add Paper 11: Sheaves of Dynamical Systems
- [ ] Add Paper 12: AI + Formal Verification
- [ ] Add Paper 13: Stigmergic Cognition
- [ ] Update Verification Matrix with new entries

### Deliverable 2: AD-013
- [ ] Add AD-013 to `spec/principles.md` after AD-012
- [ ] Ensure formatting matches existing ADs

### Deliverable 3: Proof Generation Spec
- [ ] Create `spec/protocols/proof-generation.md`
- [ ] Ensure cross-references are valid

---

## Continuation Prompt

For the next agent to proceed with implementation:

```
## HANDOFF: Metatheory Heritage Formalization

You are continuing work from `plans/metatheory-heritage-formalization.md`.

### Context
The brainstorming document `brainstorming/2025-12-21-metatheory-self-consistency-refresh.md`
contains research findings that need to be transferred to formal specs. The plan identifies:
- 4 papers to enshrine as HERITAGE level
- 1 new Architectural Decision (AD-013: Typed AGENTESE)
- 1 new spec (Proof-Generating ASHC)

### Your Task
Execute the implementation checklist in the plan:

1. **Update `spec/heritage.md`**
   - Add Part IV: Formalization Heritage
   - Add the 4 papers with proper citations and kgents mappings
   - Update the Verification Matrix

2. **Update `spec/principles.md`**
   - Add AD-013: Typed AGENTESE after AD-012
   - Follow the existing AD format

3. **Create `spec/protocols/proof-generation.md`**
   - Use the draft in the plan as the basis
   - Ensure cross-references are valid

### Voice Anchors
Remember: "Daring, bold, creative, opinionated but not gaudy"
Apply the Anti-Sausage check before finalizing each file.

### Files to Modify
- `spec/heritage.md` (amendment)
- `spec/principles.md` (amendment)
- `spec/protocols/proof-generation.md` (new file)

### Verification
After implementation, the following should be true:
- `spec/heritage.md` has Part IV with 4 new papers
- `spec/principles.md` has AD-013
- `spec/protocols/proof-generation.md` exists and is valid markdown
```

---

## Anti-Sausage Check

Before implementation:
- ❓ *Did I smooth anything that should stay rough?* No—the brainstorming's enthusiasm preserved
- ❓ *Did I add words Kent wouldn't use?* Technical terms from sources, not added
- ❓ *Did I lose any opinionated stances?* "LLM hallucinations don't matter for proofs" preserved
- ❓ *Is this still daring, bold, creative—or did I make it safe?* HoTT bridge and proof generation remain daring

---

*"The master's touch was always just compressed experience. Now we compile the compression."*
