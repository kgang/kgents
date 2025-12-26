# Pilots

> *"The run is the proof. The voice is the claim. The day is the witness."*

Standalone canary experiences built on kgents systems. Each pilot is a compact, high-delight proof of system leverage—designed to be rebuilt, mutated, or retired quickly.

---

## Philosophy

These pilots share a common conviction: **actions are proofs, not just events**.

Every pilot turns ordinary activity—playing a game, practicing freestyle, designing sprites, planning a trip, logging a day—into a chain of justified decisions. The witness layer doesn't slow things down; it makes them *feel* faster because indecision dissolves.

### What Makes Pilots Different

| Principle | How It Shows |
|-----------|--------------|
| **Composability** | Every pilot chains the same primitives: Mark → Trace → Crystal. Integration tables show exact flows. |
| **Witness over Surveillance** | Systems feel like collaborators, not judges. Gaps are honored. Courage is protected. |
| **Proof Language** | Actions are proofs. Sessions are traces. Crystals are claims. |
| **Sensory Language** | How things *feel* matters: fast, warm, earned, rough, defended. |
| **Anti-Success Sections** | Each pilot defines its failure modes—what would make it *wrong*, not just incomplete. |

---

## Index

| Pilot | Domain | Personality Tag | Tier |
|-------|--------|-----------------|------|
| **[Trail to Crystal](./trail-to-crystal-daily-lab/PROTO_SPEC.md)** | Daily action logging | *Honest gaps over concealment. Witness, not surveillance.* | Core |
| **[Zero Seed Governance](./zero-seed-personal-governance-lab/PROTO_SPEC.md)** | Personal constitution | *Your axioms are not what you think. Galois loss reveals them.* | Core |
| **[Wasm Survivors](./wasm-survivors-witnessed-run-lab/PROTO_SPEC.md)** | Arcade roguelike | *Failure is the clearest signal. Chaos is structure when witnessed.* | Domain |
| **[Rap Coach](./rap-coach-flow-lab/PROTO_SPEC.md)** | Freestyle practice | *The rough voice, not the polished one. Witness, never judge.* | Domain |
| **[Sprite Lab](./sprite-procedural-taste-lab/PROTO_SPEC.md)** | Procedural pixel art | *Artist's chaos over algorithmic cleanliness. Wild branches thrive.* | Domain |
| **[Disney Portal](./disney-portal-planner/PROTO_SPEC.md)** | Trip planning | *Days should feel earned. Planning is adventure, not spreadsheet labor.* | Domain |
| **[Categorical Foundation](./categorical-foundation-open-lab/PROTO_SPEC.md)** | Open-source infrastructure | *Category theory for the people. Power without prerequisites.* | Meta |

### Pilot Tiers

- **Core**: Validates the fundamental thesis (Mark → Trace → Crystal)
- **Domain**: Proves the pattern generalizes across verticals
- **Meta**: Packages the patterns for external adoption

---

## Shared Substrate

All pilots compose the same kgents primitives:

```
Mark      → captures decision with intent, weights, context
Trace     → immutable history of marks
Crystal   → compressive proof (meaning, not summary)
Compass   → constitutional alignment visualization
Trail     → navigation + evidence anchors
Galois    → drift/coherence/loss signal
Ghost     → unchosen alternatives (roads not taken)
Contract  → API interface verified at CI time (see CONTRACT_COHERENCE.md)
```

The **Composition Chain** in each pilot shows exactly how these primitives flow for that domain.

### Contract Coherence

All pilots follow the [Contract Coherence Protocol](./CONTRACT_COHERENCE.md):
- **L6**: API contracts have a single source of truth
- **QA-5/6/7**: Contracts verified at test time, not runtime
- **Anti-Success: Contract drift**: Users never see interface mismatches

### Witnessed Regeneration

Pilots are designed to be **dropped and regenerated** from specification. The [Witnessed Regeneration Protocol](../spec/protocols/witnessed-regeneration.md) formalizes this as a 5-stage pipeline:

```
Spec → Archive >> Verify >> Generate >> Validate >> Learn → Spec'
```

| Stage | Purpose | Output |
|-------|---------|--------|
| **Archive** | Preserve current state | `runs/run-{N}/impl.archived/` |
| **Verify** | Check contracts are sound | GO/NO-GO decision |
| **Generate** | Create from spec + contracts | Fresh implementation |
| **Validate** | Test against qualitative assertions | PASS/FAIL |
| **Learn** | Crystallize insights | Improved prompts for next run |

**Skill Guide**: [docs/skills/witnessed-regeneration.md](../docs/skills/witnessed-regeneration.md)

Each pilot's `runs/` directory contains the complete history of regeneration experiments—including failures. Failed runs teach us.

---

## Canary Criteria

Each pilot defines concrete success markers—not features, but *experiences*:

- Can the user explain X using only the crystal and trail?
- Does the system surface Y without judgment?
- Does the ritual feel like closure, not obligation?
- Does the user *want* to return?

If a pilot can't pass its canary criteria, it hasn't earned its place.

---

## Anti-Success

Every pilot includes a **failure mode section**—clinical diagnoses of what would make the experience *wrong*:

- **Surveillance creep**: witnessing adds drag, changes behavior
- **Judgment leakage**: descriptive becomes evaluative
- **Highlight theater**: proofs become reels
- **Coldness**: crystals read like reports
- **Gap shame**: honest rest becomes invisible

These are not edge cases. They are the gravitational pull every system must resist.

---

*Compiled: 2025-12-26 | Pilots are proofs, not products.*
