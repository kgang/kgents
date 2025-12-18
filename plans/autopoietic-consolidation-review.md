---
path: plans/autopoietic-consolidation-review
status: active
progress: 0
last_touched: 2025-12-18
touched_by: codex
blocking: []
---

# Autopoietic Consolidation Review

This is the full critical review requested for the autopoietic consolidation plan. It prioritizes category-theoretic rigor and Kent's principles in `spec/principles.md`.

---

## Scope and Sources

### In-repo evidence
- `plans/autopoietic-consolidation.md`
- `spec/principles.md`
- `docs/categorical-foundations.md`
- `impl/claude/agents/operad/core.py`
- `impl/claude/agents/f/operad.py`
- `impl/claude/agents/atelier/workshop/operad.py`
- `impl/claude/agents/poly/protocol.py`
- `impl/claude/agents/sheaf/protocol.py`
- `impl/claude/protocols/agentese/*`
- `spec/k-gent/persona.md`
- `impl/claude/agents/k/*`

### External research
- Autopoiesis definition: https://en.wikipedia.org/wiki/Autopoiesis
- Operads: https://ncatlab.org/nlab/show/operad
- Polynomial functors: https://ncatlab.org/nlab/show/polynomial+functor
- Sheaves: https://ncatlab.org/nlab/show/sheaf

---

## Executive Diagnosis

The plan correctly aims for autopoiesis but currently lacks a categorical compiler path that would make deletion safe and regeneration inevitable. It also under-protects the very infrastructure that makes autopoiesis possible (AGENTESE and persona). The result is a plan that could reduce scope while increasing incoherence.

Autopoiesis, in the research sense, is not just self-description but self-production of the system's components and their organization. If the system cannot re-produce itself from a minimal generative spec, then it is not autopoietic; it is curated.

---

## Critical Issues (With Evidence)

1. Operad fragmentation breaks the Unified Categorical Foundation.
   - `impl/claude/agents/f/operad.py` defines its own Operad class.
   - `impl/claude/agents/atelier/workshop/operad.py` defines its own Operad class.
   - `impl/claude/agents/operad/core.py` is the canonical operad implementation.
   - Result: multiple operad dialects violate AD-006 and make law verification partial.

2. Spec/impl drift is acknowledged but not enforced.
   - `impl/claude/agents/k/README.md` lists missing access control and error codes vs `spec/k-gent/persona.md`.
   - `plans/autopoietic-consolidation.md` treats drift as a research target, not a deletion trigger.

3. AGENTESE is foundational but not protected.
   - The plan states discoverability via AGENTESE paths but does not include `impl/claude/protocols/agentese` in SACRED.

4. Deletion criteria are non-categorical.
   - LoC and coverage thresholds in `plans/autopoietic-consolidation.md` can delete correct categorical systems while preserving non-categorical ones.

5. Autopoiesis is named but not operationalized.
   - `self.system.*` is proposed, but no registry node exists in `impl/claude`.
   - Without a self-describing path that can also evolve the system, autopoiesis remains rhetorical.

6. Personality is a meta-principle but not preserved.
   - `spec/principles.md` mandates personality space and K-gent alignment.
   - The plan allows annihilating K-gent persona without explicit safeguards.

---

## Research Anchors (Why This Matters)

- Autopoiesis is the self-production of both components and organization, not just self-description.
  - If the system cannot regenerate its structure from the spec, it fails the autopoietic criterion.
  - Source: https://en.wikipedia.org/wiki/Autopoiesis

- Operads are the algebraic grammar for composition of multi-input morphisms.
  - Multiple competing operad implementations mean composition laws fragment and cannot be verified uniformly.
  - Source: https://ncatlab.org/nlab/show/operad

- Polynomial functors encode mode-dependent dynamics using positions and directions.
  - This is exactly the mathematical engine for agents with state-dependent inputs. If you bypass it, you undercut the categorical core.
  - Source: https://ncatlab.org/nlab/show/polynomial+functor

- Sheaves formalize local-to-global coherence.
  - If your systems do not implement sheaf-like gluing, you cannot claim emergence or global consistency across local perspectives.
  - Source: https://ncatlab.org/nlab/show/sheaf

---

## Full Sketch (Categorical Autopoiesis)

### Objects and Functors

- SpecCat: specs as objects, references as morphisms
- ImplCat: modules as objects, imports/compositions as morphisms
- PathCat: AGENTESE paths as objects, `>>` as composition

Define functors:

- Compile: SpecCat -> ImplCat
- Project: ImplCat -> PathCat
- Reflect: ImplCat -> SpecCat (extraction)

Autopoiesis = a fixed point where Reflect(Compile(S)) is isomorphic to S.

### System Sketch

```
SpecGraph  --Compile-->  ImplGraph  --Project-->  PathGraph
    ^                        |                     |
    |                        v                     |
   Reflect  <-----------  Drift Check  <-----------
```

### Minimal Survivors (Sacred+Extended)

- `spec/principles.md`
- `spec/c-gents/*`
- `impl/claude/agents/poly/*`
- `impl/claude/agents/operad/*`
- `impl/claude/agents/sheaf/*`
- `impl/claude/protocols/agentese/*`
- `spec/k-gent/persona.md`
- `impl/claude/agents/k/*`

These are the minimal autopoietic kernel. Everything else must be either:
- generated from these, or
- archived as compost.

---

## Concrete Gaps in the Current Plan

- No definition of Compile or Reflect as concrete tools.
- No authoritative registry for AGENTESE paths.
- No enforcement that operad subclasses must derive from `impl/claude/agents/operad/core.py`.
- No spec schema that can generate implementations (violates Generative principle).
- No categorical tests to replace LoC and coverage as culling metrics.

---

## Revised Plan Outline (Category-First)

### Phase 0: Declare the Compiler Contract
- Define SpecGraph schema with explicit positions, directions, operations, laws, and sheaf overlaps.
- Define Compile and Reflect interfaces in writing. If they are not defined, annihilation is unsafe.

### Phase 1: Unify Operads
- Replace local operad types with `impl/claude/agents/operad/core.py`.
- Require OperadRegistry to be the single source of operad truth.

### Phase 2: Establish Path Authority
- All AGENTESE nodes must be generated from SpecGraph, not hand-decorated.
- Add `self.system.manifest`, `self.system.audit`, `self.system.evolve`, `self.system.witness`.

### Phase 3: Drift as a First-Class Check
- Build SpecGraph <-> ImplGraph diff reports.
- Culling based on violation of categorical laws, not on LoC or coverage.

### Phase 4: Reference Agent as Proof
- Choose one agent spec and compile it to chat, web, and SaaS outputs.
- If the output diverges, fix the compiler, not the agent.

### Phase 5: Autopoietic Loop
- Use `self.system.audit` to generate a Reflect report.
- Feed that report to `self.system.evolve` to regenerate or prune.

---

## Culling Rules That Preserve Category Theory

Replace LoC and coverage thresholds with categorical invariants:

- Functor laws verified (identity + composition) for all functor lifts.
- Operad laws verified for all operads.
- Sheaf gluing consistency for any system claiming global coherence.
- SpecGraph <-> ImplGraph isomorphism (or controlled divergence with rationale).

If these fail, delete or regenerate regardless of size.

---

## Critical Recommendation (Radical Reinvention)

Convert autopoietic-consolidation from a deletion-first plan into a compiler-first plan. The only safe path to aggressive annihilation is to make the system regenerable. That means:

1. Build the SpecGraph schema first.
2. Make Compile and Reflect real.
3. Use those to regenerate any surviving system.

Once that exists, annihilation is safe and fast. Without it, annihilation is reckless.

---

## Open Questions (Need Your Call)

- Do you want K-gent persona to be part of the autopoietic kernel or a generated layer?
- Should AGENTESE paths be authored in spec or in code decorators (which is the authority)?
- Is the compiler allowed to discard manual implementations, or should it preserve select hand-tuned agents?

---

## Appendix: Key Research Extracts (Short)

- Autopoiesis: self-producing organization, not just self-description.
  - https://en.wikipedia.org/wiki/Autopoiesis

- Operads: algebraic structure for composition of multi-input operations.
  - https://ncatlab.org/nlab/show/operad

- Polynomial functors: encode mode-dependent dynamics using positions and directions.
  - https://ncatlab.org/nlab/show/polynomial+functor

- Sheaves: enforce local-to-global coherence via gluing.
  - https://ncatlab.org/nlab/show/sheaf

