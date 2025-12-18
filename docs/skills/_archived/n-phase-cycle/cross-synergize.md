# Skill: CROSS-SYNERGIZE (N-Phase Cycle)

> Discover compositions and entanglements that unlock nonlinear value.

**Difficulty**: Medium  
**Prerequisites**: `strategize.md`, composability laws (spec/principles.md §5)  
**Files Touched**: design notes, prototype pipelines, agent registries

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → CROSS-SYNERGIZE | comps to probe | fixtures ready | ledger.CROSS-SYNERGIZE=touched | entropy.sip(0.05–0.10) | next=IMPLEMENT
```
- **Minimal artifacts**: candidate compositions + probes, law checks, chosen + rejected paths, ledger update, branch handles if new tracks appear.
- **Signals**: log tokens/time/entropy + law-check counts + branch count for `process-metrics.md`.
- **Branch check**: emit handles for new primitives or missing components discovered.

---

## Overview
CROSS-SYNERGIZE tests combinations across agents, functors, and puppets to find lifts greater than the sum of parts. It enforces Composable and Generative principles—pipelines are derived, not enumerated.

---

## Step-by-Step

1. **Enumerate candidate morphisms**: List possible compositions (agent pipelines, operad operations, puppet swaps).  
2. **Probe fast**: Build micro-prototypes or dry-runs; prefer hotdata fixtures to avoid speculative LLM loops.  
3. **Select and freeze**: Choose compositions that satisfy laws (identity/associativity) and do not violate Ethical/Tasteful constraints.

---

## Interfaces (Headers ↔ Continuations ↔ Metrics)
- **Ledger/entropy contract**: Every continuation generator in SENSE/ACT must emit `phase_ledger` + `entropy` snippet per `phase-accountability.md` so `_forest.md` and metrics spans stay in sync.
- **Span-ready attrs**: When wiring OTEL later (Track C), emit `{phase, phase_group, tokens_in, tokens_out, duration_ms, entropy_spent, entropy_remaining, law_checks_run, law_checks_failed, observer_role, branch_count, ledger}` matching `process-metrics.md` + `metrics/fixtures/process-metrics.jsonl`.
- **Drop point**: Until emitters exist, stage offline outputs in `metrics/fixtures/process-metrics.jsonl` and include branch/owner notes from continuation prompts to keep Track C hotloadable.

---

## Recursive Hologram
- Apply PLAN→RESEARCH→DEVELOP on the set of compositions: Which deserve deeper development? Which are void/entropy exploration?
- Use `meta-skill-operad.md` to register new operations; ensure they remain valid under future mutations (operad closure).

---

## Accursed Share (Entropy Budget)

CROSS-SYNERGIZE reserves 5-10% for exploration:

- **Dormant tree awakening**: Skim `plans/_forest.md` for forgotten plans that might compose.
- **Functor hunting**: What existing functors could lift this work? Check `FunctorRegistry`.
- **Unexpected compositions**: Try composing with something that "shouldn't" work. Sometimes it does.
- **Bounty board scan**: Read `plans/_bounty.md`—your work might resolve an open gripe.

Draw: `void.entropy.sip(amount=0.10)`
Return unused: `void.entropy.pour`

---

## Verification
- Chosen compositions documented with rationale and constraints.
- Rejected paths noted (to avoid rework).
- Implementation-ready interfaces defined.

---

## Common Pitfalls

- **Skipping CROSS-SYNERGIZE entirely**: This phase finds leverage. Missing it means missing 2x-10x value multipliers.
- **Enumerating instead of generating**: Per AD-003, define grammars, not lists. If you're writing 600 commands, you're doing it wrong.
- **Ignoring law violations**: Compositions that break identity/associativity will fail downstream. Check laws in prototype.
- **Speculative LLM loops**: Use hotdata fixtures for probing. Don't burn tokens on exploratory combinations.
- **No rejected paths documentation**: Future sessions will re-explore dead ends. Write down what didn't work and why.

---

## Hand-off
Next: `implement.md` with selected compositions and constraints.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../flux-agent.md`
- `../polynomial-agent.md`

---

## Continuation Generator

Emit this when exiting CROSS-SYNERGIZE:

### Exit Signifier

```markdown
# Normal exit (auto-continue):
⟿[IMPLEMENT]
/hydrate
handles: compositions=${chosen_compositions}; interfaces=${implementation_interfaces}; rejected=${rejected_paths}; laws=${law_verifications}; ledger={CROSS-SYNERGIZE:touched}; branches=${branch_notes}
mission: write code + tests honoring laws/ethics; keep Minimal Output; start tests in background.
actions: TodoWrite chunks; run pytest watch; code/test slices; log metrics.
exit: code + tests ready; ledger.IMPLEMENT=touched; QA notes captured; continuation → QA.

# Halt conditions:
⟂[BLOCKED:composition_conflict] Chosen compositions violate category laws
⟂[BLOCKED:no_viable_path] All candidate compositions rejected
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

Template vars: `${chosen_compositions}`, `${implementation_interfaces}`, `${rejected_paths}`, `${law_verifications}`, `${branch_notes}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../flux-agent.md`
- `../polynomial-agent.md`

---

## Changelog
- 2025-12-13: Added Accursed Share section (re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
