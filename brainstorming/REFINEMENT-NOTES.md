# Refinement Notes: Metabolic Development Protocol

**Date:** 2025-12-21
**Refiner:** Claude (per handoff prompt)
**Voice Anchor Preserved:** "Daring, bold, creative, opinionated but not gaudy"

---

## What Changed and Why

### 1. Strengthened the Metabolism Metaphor (Part I)

**Before:** Metaphor mentioned but underexplored.
**After:** Full metabolic mapping table showing biological → development equivalents.

**Why:** The handoff asked "What is the food being metabolized?" The answer: Intent. Also mapped digestion (context compilation), energy (attention/tokens), waste (failed experiments), and growth (pattern crystallization).

**The generative insight:** A healthy metabolism doesn't minimize waste—it processes efficiently. This connects waste directly to the Accursed Share principle.

### 2. Added Explicit Cross-Jewel Wiring (Part II, §2.3)

**Before:** Integration points described but not wired.
**After:** `METABOLIC_WIRING` dictionary mapping events to handlers.

**Why:** The handoff identified missing connections:
- Brain ↔ ASHC (evidence → crystals): Now wired
- Gardener ↔ Morning Coffee (voice → plot metadata): Now wired
- Witness ↔ Interactive Text (task toggle → Mark): Now wired
- K-gent ↔ Hydration (voice anchors → persona): Now wired
- Living Docs ↔ ASHC (test failures → teaching moments): Now wired

### 3. Added Serendipity to Morning Start (Journey 1)

**Before:** Morning ritual was deterministic.
**After:** 10% chance to surface random past voice from unexpected era.

**Why:** The Accursed Share requires exploration budget. Morning start should feel like discovery, not routine.

### 4. Added Edge Cases to All Journeys

**Journey 1:** What if developer skips ritual? → Graceful degradation, lighter hydration, silent encouragement.
**Journey 2:** How does evidence accumulate without interrupting? → Fire-and-forget background tasks.
**Journey 3:** What makes handoff usable? → Compression with `waste_compost` for learnings.
**Journey 4:** What's the celebration loop? → Reinforcement multipliers based on event significance.

### 5. Added Failure Modes (New Part X)

Five failure modes with concrete mitigations:
1. **Context Overload** → Hard budget limits (5 teaching moments, 8 files, 3 evidence items)
2. **Stale Stigmergy** → Daily decay (0.95×) with reinforcement cap (10.0)
3. **Evidence Inflation** → Diversity scoring (not just run count)
4. **Voice Drift** → Pattern matching for anchor paraphrasing
5. **Session Boundary Ambiguity** → Prefer explicit; implicit detection prompts, doesn't auto-end

### 6. Added Accursed Share Integration (New Part XI)

**Before:** Mentioned but not operationalized.
**After:** Three concrete mechanisms:
- Morning Serendipity (10% random voice)
- Waste as Offering (CompostPile class)
- Exploration Budget in Hydration (tangential connections)

### 7. Added Diversity Requirement Law

**Before:** Four laws.
**After:** Five laws. New law: `∀ evidence: diversity_score ≥ 0.5`

**Why:** Evidence inflation is a real risk. 100 identical runs ≠ 100x confidence.

---

## Ideas Considered But Rejected

### ❌ Metabolic Metrics Dashboard

**Proposed:** Visualize the metabolism (energy flow, waste products, growth rate).
**Rejected:** *"Tasteful > feature-complete"* — A dashboard adds complexity without clear necessity. The CLI output already shows patterns and evidence. A dedicated dashboard feels like scope creep. Revisit if users request it.

### ❌ Circadian Adaptation (Time-of-Day Intensity)

**Proposed:** Adapt ritual intensity based on time of day, day of week.
**Rejected:** *"Depth over breadth"* — Morning/evening distinction is enough. Fine-grained time adaptation adds complexity without clear benefit. The circadian resonance (matching past mornings) is sufficient temporal awareness.

### ❌ Cross-Developer Archaeology

**Proposed:** Learn patterns from other developers (with consent).
**Rejected:** This is fundamentally about Kent's voice, not collective voice. *"The Mirror Test: Does K-gent feel like me on my best day?"* Cross-developer patterns would dilute the personal mirror. Revisit only for team contexts.

### ❌ Voice Transplant for Legacy Code

**Proposed:** Inject voice anchors from past eras when working on legacy code.
**Rejected:** Clever but unnecessary. The archaeology strata already surface relevant past voice. A separate "transplant" mechanism adds complexity. The existing system handles this case.

### ❌ Metabolic Health Check

**Proposed:** Detect when the system is "sick" (low energy, high waste).
**Rejected for now:** Good idea but premature. Need operational data first to define what "sick" looks like. Added to "Unanswered" for future consideration once we have usage patterns.

---

## Open Questions for Kent

1. **PARTIAL Reinforcement:** The spec now handles "partial" completion with targeted reinforcement. Does the partial → specify flow feel right, or should it be simpler?

2. **Waste Compost in Handoff:** I added `waste_compost` to handoff prompts. Is this the right level of surfacing, or should abandoned approaches be more prominent/less prominent?

3. **Voice Drift Detection:** The `VoiceDriftDetector` looks for paraphrasing of known anchors. Should it be more aggressive (flag any deviation) or more permissive (only flag obvious smoothing)?

4. **Session Boundary Triggers:** I added four implicit end triggers (idle, day boundary, major commit, context exhaustion). Are these the right signals? Should any be removed or added?

5. **Diversity Threshold:** I set `diversity_score ≥ 0.5` as a law. Is this the right threshold? Higher = stricter (harder to ship), lower = more permissive.

---

## Anti-Sausage Self-Check

Before finishing, I asked myself:

- ❓ *Did I smooth anything that should stay rough?*
  → **No.** I preserved the rough edges: "waste is sacred expenditure", "compost pile", "metabolic byproducts". These are intentionally not-polished.

- ❓ *Did I add words Kent wouldn't use?*
  → **Checked.** I used Kent's vocabulary: "crystallize", "stigmergy", "archaeology", "pheromone", "fossil layer". Avoided corporate/generic terms.

- ❓ *Did I lose any opinionated stances?*
  → **No.** Actually strengthened: "100 identical runs ≠ 100x confidence" is now explicit.

- ❓ *Is this still daring, bold, creative—or did I make it safe?*
  → **Still daring.** The waste-as-compost framing is bold. The serendipity injection is creative. The explicit wiring is opinionated (not "figure it out later").

---

## Summary

The refinement increased:
- **Coherence:** Metabolism metaphor now generates behaviors, not just labels
- **Depth:** Explicit wiring, concrete mitigations, edge cases handled
- **Inevitability:** The reader should now think "Of course. How could it be otherwise?"

The spec grew from ~710 lines to ~1140 lines. Most additions are concrete code examples and failure mode handling. The prose stayed terse.

> *"The master's touch was always just compressed experience. Now we compile the compression."*

---

*Refinement completed: 2025-12-21*
