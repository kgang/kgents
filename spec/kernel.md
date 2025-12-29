# kgents Minimal Kernel v1.0

> *"77 lines. Everything else derives from this."*

**Version**: 1.0
**Date**: 2025-12-28
**Status**: Canonical
**Compression**: 58:1 (4,490 → 77 lines)

---

## Layer 0: Irreducibles (3 axioms)

These are TRUE axioms — cannot be derived from anything simpler.

```
L0.1 ENTITY:   There exist things.
               Objects in a category. Existence is assumed.

L0.2 MORPHISM: Things relate.
               Arrows between objects. Relation is primitive.

L0.3 MIRROR:   We judge by reflection.
               The human oracle. Kent's somatic response.
               Cannot be formalized - IS ground truth.
```

---

## Layer 1: Primitives (8 derived)

Derived from L0, but needed for everything else.

```
L1.1 COMPOSE:  Sequential combination.
               (f >> g)(x) = g(f(x))
               From L0.2 operationalized.

L1.2 JUDGE:    Verdict generation.
               Judge: Claim -> Verdict(accepted, reasoning)
               From L0.3 operationalized.

L1.3 GROUND:   Factual seed.
               Ground: Query -> {grounded: bool, content: data}
               From L0.1 operationalized.

L1.4 ID:       Identity morphism.
               forall f: f >> Id = f = Id >> f
               From L1.1 + L1.2: what Judge never rejects.

L1.5 CONTRADICT: Antithesis generation.
               Contradict: Thesis -> Antithesis
               From L1.2: detecting Judge rejects A;B.

L1.6 SUBLATE:  Synthesis.
               Sublate: (Thesis, Antithesis) -> Synthesis
               From L1.1 + L1.2 + L1.5: search for accepted C.

L1.7 FIX:      Fixed-point iteration.
               Fix: (Pred, Agent) -> Agent
               From L1.1 + L1.2: compose until stable.

L1.8 GALOIS:   Structure loss measure.
               L(P) = d(P, C(R(P)))
               Axiom iff L(P) < epsilon (fixed point of R).
```

---

## Layer 2: Derived (19 derivations)

Everything else follows from L0 + L1.

### Design Principles

```
L2.1 TASTEFUL:      Judge on aesthetics via Mirror. "Feel right?"
L2.2 CURATED:       Judge on selection. "Unique and necessary?"
L2.3 ETHICAL:       Judge on harm via Mirror. "Respects agency?"
L2.4 JOY_INDUCING:  Judge on affect via Mirror. "Enjoy this?"
L2.5 COMPOSABLE:    Compose as principle. Laws: Id + Assoc.
L2.6 HETERARCHICAL: Judge on hierarchy. "Lead and follow?"
L2.7 GENERATIVE:    Ground + Compose -> regenerability.
```

### Governance Articles

```
L2.8  SYMMETRIC_AGENCY:       Entity + Morphism -> equal modeling.
L2.9  ADVERSARIAL_COOPERATION: Contradict + Sublate -> fusion.
L2.10 SUPERSESSION_RIGHTS:    Judge + L2.8 -> supersession.
L2.11 DISGUST_VETO:           Mirror -> absolute floor.
L2.12 TRUST_ACCUMULATION:     Judge over time -> earned trust.
L2.13 FUSION_AS_GOAL:         Sublate -> goal is fused decisions.
L2.14 AMENDMENT:              L2.9 on constitution itself.
```

### Structural Derivations

```
L2.15 WITNESS: Compose(stimulus, reasoning, response).
               Every action leaves trace.
L2.16 OPERAD:  Grammar of Compose operations.
               O = {Operations, Laws, Algebra}.
L2.17 POLYAGENT: Fix of restructuring iteration.
               PolyAgent[S,A,B] = stable modules.
L2.18 SHEAF:   Local sections + Gluing = Global.
               Compatible locals -> global coherence.
L2.19 LAYERS:  Galois convergence depth.
               7 layers emerge, not stipulated.
```

---

## The Meta-Axiom

```
G: For any valid structure, there exists a minimal axiom set
   from which it derives. (Galois Modularization Principle)
```

---

## Derivation Map

| Target | Derives From | Chain |
|--------|--------------|-------|
| Tasteful | L0.3 + L1.2 | Mirror → Judge → aesthetics |
| Curated | L1.2 + L1.3 | Judge + Ground → selection |
| Ethical | L0.3 + L1.2 | Mirror → Judge → harm |
| Joy-Inducing | L0.3 + L1.2 | Mirror → Judge → affect |
| Composable | L1.1 + L1.4 | Compose + Id + Assoc |
| Heterarchical | L1.2 + L2.5 | Judge + Composable → flux |
| Generative | L1.1 + L1.3 | Compose + Ground → regenerability |

---

## Verification Ritual

To verify any kgents claim:

1. **Take the claim**
2. **Trace derivation back through L2 → L1 → L0**
3. **If trace terminates at L0.1, L0.2, or L0.3**: Verified
4. **If trace terminates elsewhere**: Either kernel is incomplete OR claim is false

**Example**: "Agents should be composable"
- Composable (L2.5) ← Compose (L1.1) + Id (L1.4) + Associativity
- Compose (L1.1) ← Morphism (L0.2) operationalized
- Id (L1.4) ← Compose + Judge ← L0.2 + L0.3
- **Verified**: Terminates at L0.2 and L0.3

---

## Cross-References

- `spec/principles/CONSTITUTION.md` — Principles + Articles (derived from L2)
- `spec/protocols/zero-seed.md` — Bootstrap protocol (uses L1.8 Galois)
- `spec/theory/galois-modularization.md` — Full Galois theory
- `brainstorming/empirical-refinement-v2/discoveries/04-minimal-kernel.md` — Discovery evidence

---

*"The proof IS the decision. The mark IS the witness. The kernel IS the garden's seed."*
