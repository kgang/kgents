# Zero Seed Personal Governance Lab

Status: proto-spec

> *"Your axioms are not what you think they are. Galois loss reveals them."*

## Narrative

Most people have never articulated their core values. They operate from implicit axioms—beliefs so fundamental they're invisible. This pilot makes value discovery accessible: the system surfaces your actual fixed points (what survives restructuring unchanged) and helps you evolve them intentionally through a personal constitution.

## Personality Tag

*This pilot treats value articulation as archaeology, not construction. You're not creating values—you're discovering what was already there, then choosing whether to keep it.*

## Objectives

- Surface **implicit axioms** from personal writings, decisions, and witness traces without forcing premature articulation.
- Enable **constitutional evolution** through a formal amendment process that respects the Disgust Veto.
- Provide **coherence feedback** via Galois loss, showing where stated values and witnessed behavior diverge.
- Democratize **principled self-governance** to anyone, not just philosophers.

## Epistemic Commitments

- Axioms are **discovered, not declared**. Fixed-point detection (L < 0.05) identifies what you actually believe, not what you say you believe.
- Personal constitutions are **living documents**. Amendment G grammar applies: coherent evolution, not arbitrary change.
- The system **augments judgment, never replaces it**. ETHICAL floor (Amendment A) is non-negotiable.
- Contradictions are **surfaced without shame**. Super-additive loss detection shows conflicts; the user decides resolution.
- The Disgust Veto is **absolute**. If it feels wrong, no argument or evidence can override.

## Laws

- **L1 Axiom Discovery Law**: Fixed points (L < 0.05) must surface before constitution drafting begins. Discovery precedes articulation.
- **L2 Amendment Coherence Law**: Any constitutional change must pass through the pilot law grammar (Amendment G schemas). No arbitrary edits.
- **L3 Drift Visibility Law**: When Galois loss between stated values and witnessed behavior exceeds threshold, the drift must surface. No hiding from yourself.
- **L4 Veto Preservation Law**: The Disgust Veto cannot be argued away. Somatic rejection is an absolute floor.
- **L5 Evolution Traceability Law**: Every constitutional amendment links to witness marks that justify the change. No orphan amendments.

## Qualitative Assertions

- **QA-1** Value discovery should feel like **recognition, not invention**. "Oh, that's what I actually believe."
- **QA-2** The amendment process should feel **ceremonial but not burdensome**. Important enough to take seriously, light enough to actually do.
- **QA-3** Contradiction surfacing should feel **clarifying, not judgmental**. The system is a mirror, not a critic.
- **QA-4** Using this for a month should produce a **shareable personal constitution** you'd show to someone you trust.
- **QA-5** The system should **never tell you what to value**. It surfaces, it doesn't prescribe.

## Anti-Success (Failure Modes)

This pilot fails if:

- **Value imposition**: The system suggests what the user "should" believe. Discovery becomes prescription.
- **Coherence worship**: Users change values just to improve their Galois score. Goodhart's Law takes over.
- **Amendment theater**: The formal process becomes bureaucratic ritual without genuine reflection.
- **Contradiction shame**: Users feel bad about having conflicting values instead of curious about resolving them.
- **Philosophical gatekeeping**: The system feels like it's only for people who already think about ethics.

## kgents Integrations

| Primitive | Role | Chain |
|-----------|------|-------|
| **Galois Fixed-Point** | Surface axioms from corpus | `corpus → detect_fixed_point() → axioms` |
| **Galois Loss** | Measure value-behavior drift | `(stated_values, witnessed_behavior) → L(P)` |
| **Contradiction Detection** | Surface value conflicts | `super_additive_loss(A, B) → conflict` |
| **Pilot Law Grammar** | Govern amendment process | `amendment → verify_schema_laws(COHERENCE_GATE)` |
| **Witness Mark** | Evidence for amendments | `change → Mark.emit(reasoning, principle_weights)` |
| **K-Block Lineage** | Trace constitutional evolution | `constitution_v1 → amendment → constitution_v2` |
| **Trust Gradient** | Track self-alignment over time | `TrustState.update_aligned() / update_misaligned()` |

**Composition Chain** (axiom discovery → constitution):
```
Personal Corpus (writings, decisions, traces)
  → Galois.detect_fixed_point(corpus)
  → Axiom candidates (L < 0.05)
  → User validation (Disgust Veto gate)
  → Initial Constitution draft
  → Amendment process (via pilot law grammar)
  → Living Constitution (versioned K-Block)
  → Drift monitoring (Galois loss on behavior)
```

## Canary Success Criteria

- A user with no philosophy background can **articulate 3-5 personal axioms** within the first session.
- The user **recognizes** at least one axiom they hadn't consciously articulated before.
- The amendment process produces **at least one constitutional evolution** over 30 days.
- Contradiction surfacing leads to **synthesis, not suppression**—the user resolves or consciously accepts the tension.
- The user would **share their constitution** with a trusted friend without embarrassment.

## Out of Scope

- Prescriptive ethics or moral recommendations.
- Comparison to other users' constitutions.
- Gamification of value alignment (no scores to optimize).
- Team/organizational governance (that's a different pilot).

## Mathematical Grounding

This pilot operationalizes several theoretical constructs:

| Theory | Application |
|--------|-------------|
| **Galois Modularization** | Fixed-point detection reveals axioms |
| **Toulmin Argument Structure** | Amendments require data, warrant, backing |
| **Living Constitution (Amendment F)** | Evolution through formal process |
| **Pilot Law Grammar (Amendment G)** | COHERENCE_GATE, DRIFT_ALERT schemas |
| **Trust Polynomial (Amendment E)** | Self-alignment tracking |
| **ETHICAL Floor (Amendment A)** | Values cannot offset ethical violations |

## Pricing Context

Target: $15/month consumer subscription

Value proposition: "Know thyself—computationally." The only tool that surfaces your actual axioms rather than asking you to declare them.

Differentiation: Most journaling/reflection apps ask "what do you value?" This asks "what do your choices reveal you value?" and shows the delta.
