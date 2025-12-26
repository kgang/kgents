# Sprite Procedural Taste Lab

Status: proto-spec

> *"The mutation is the proof. The canon is the claim. Wild branches are honored guests."*

## Narrative
Aesthetic evolution becomes explicit. Each mutation is a proof step toward a taste attractor—and the system gives permission to be wild without losing the canon. The lab reveals taste as something *earned*, not arbitrary.

## Personality Tag
*This pilot trusts the artist's chaos over algorithmic cleanliness. The wild branch thrives until collapsed.*

## Objectives
- Encode taste as a **visible and defensible signal**, not a hidden filter. The artist sees why something "feels right."
- Allow procedural chaos while protecting the core style from contamination—wildness is quarantined, not deleted.
- Produce crystals that summarize **how the style evolved and why**. The crystal answers: "How did we get here, and why is it stable?"

## Epistemic Commitments
- Every mutation and acceptance emits a mark with **rationale and principle weights**. Taste leaves traces.
- The style trace is immutable and reveals **branching experiments**. All branches remain inspectable until collapse.
- Crystals compress the style journey and explain the **current attractor**—why this aesthetic is stable (for now).
- Galois loss measures drift from the authentic style coordinate. Drift is data, not failure.
- Wild branches are heterarchically tolerated: they can exist, experiment, and *not* contaminate the canon.

## Laws

- **L1 Taste Gravity Law**: The system must reveal pull toward the style attractor at all times. The artist sees the field.
- **L2 Wildness Quarantine Law**: High-loss mutations can exist but cannot redefine the canon. Chaos is honored, not privileged.
- **L3 Mutation Justification Law**: Every accepted mutation must have a stated reason. Taste is never "just because."
- **L4 Branch Visibility Law**: All branches remain inspectable until explicitly collapsed. The topology of exploration is preserved.
- **L5 Style Continuity Law**: The crystal must justify why the current style is stable. Stability is earned, not assumed.

## Qualitative Assertions

- **QA-1** The lab must feel like **discovery**, not QA. The artist is exploring, not being audited.
- **QA-2** A wild branch should feel **celebrated**, not punished. The system respects the detour.
- **QA-3** The canonical style should feel **earned**, not arbitrary. The artist can trace why this is "the look."
- **QA-4** The system should surface **taste language** without forcing jargon. The vocabulary emerges from use.

## Anti-Success (Failure Modes)

This pilot fails if:

- **Canonization by fiat**: The system declares a style canonical without visible justification. The artist can't trace why something "won."
- **Exploration shame**: Wild branches feel like errors—the UI signals "you've drifted too far" instead of "here's an interesting tangent."
- **Invisible gravity**: The taste attractor is real but hidden. The artist doesn't know what's pulling their choices—it feels like magic, not method.
- **Jargon imposition**: The system forces technical aesthetic vocabulary ("high saturation," "contour emphasis") when the artist thinks in feels ("punchy," "soft edge").
- **Branch genocide**: Collapsed branches are deleted instead of archived. The exploration history is lost; only the "winner" remains.

## kgents Integrations

| Primitive | Role | Chain |
|-----------|------|-------|
| **Witness Mark** | Captures mutation + acceptance rationale | `mutation → Mark.emit(rationale, weights)` |
| **Witness Trace** | Immutable style evolution history | `Mark[] → Trace.seal(style_id)` |
| **Witness Crystal** | Compressive proof of style stability | `Trace → Crystal.compress(attractor)` |
| **ValueCompass** | Aesthetic alignment and drift display | `Crystal.weights → Compass.render()` |
| **Trail** | Branch navigation + compression ratios | `Trace → Trail.navigate(branches)` |
| **Galois Loss** | Stylistic drift quantification | `mutation.weights → Galois.loss(style_target)` |
| **Heterarchical Tolerance** | Wild branch containment | `branch → Heterarchy.quarantine(canon)` |

**Composition Chain** (mutation acceptance):
```
MutationProposal
  → Mark.emit(rationale, aesthetic_weights)
  → Galois.loss(style_target) // drift signal
  → [if wild] Heterarchy.quarantine(canon)
  → [if accepted] Trace.append(mutation)
  → [on session_end] Crystal.compress(trace, attractor)
  → Compass.render(crystal.weights)
  → Trail.display(crystal, branches)
```

## Canary Success Criteria

- A user can explain **why a sprite is canonical** using only the crystal: "The palette stabilized after branch 3; the contour stayed soft because high-edge mutations drifted too far."
- The system displays at least one **wild branch without destabilizing the canon**—visible, explorable, but quarantined.
- A user can trace a single **pixel-level mutation back to its rationale**. Every choice has a reason.
- The artist **enjoys the exploration** even when they don't accept mutations. The tangent was worth taking.

## Out of Scope

- Asset export pipelines or engine-specific integration.
- Animation frame sequences (static sprites only).
- Style transfer from external sources (evolution is endogenous).
