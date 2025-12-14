# Continuation: Add Continuation Generators to Phase Skills

> *"The form is the function. Each prompt generates its successor."*

## ATTACH

/hydrate

---

## Context from Re-Metabolize Report (2025-12-13)

The `/re-metabolize` command identified a **critical gap**: 8 of 11 phase skills are missing Continuation Generators. This breaks the auto-continuation chain—the core innovation of the N-Phase Cycle.

**Missing Continuation Generators**:
| Phase Skill | Maps To | Priority |
|-------------|---------|----------|
| `research.md` | SENSE | HIGH |
| `develop.md` | SENSE | HIGH |
| `strategize.md` | SENSE | HIGH |
| `cross-synergize.md` | SENSE | HIGH |
| `qa.md` | ACT | HIGH |
| `test.md` | ACT | HIGH |
| `educate.md` | ACT | HIGH |
| `measure.md` | REFLECT | HIGH |

**Have Continuation Generators** (3): `plan.md` ✓, `implement.md` ✓, `reflect.md` ✓

**Also needed**:
- MEDIUM: Add Recursive Hologram to `detach-attach.md`
- LOW: ~~Create three-phase.md~~ (DONE in previous session)

---

## Your Mission (ACT Phase)

Execute `RefineSection(skill, "Continuation Generator")` for all 8 skills using the operad grammar from `meta-skill-operad.md`.

### The Continuation Generator Template

From `auto-continuation.md`, each phase skill should end with:

```markdown
## Continuation Generator

### Invariants (from spec/principles.md)
- [List relevant principles that constrain the next phase]

### Context Handoff
- Artifacts created: ${artifacts}
- Entropy spent/remaining: ${entropy_spent} / ${entropy_remaining}
- Decisions made: ${key_decisions}
- Blockers for next phase: ${blockers}

### Generated Prompt for [NEXT_PHASE]

---

# [NEXT_PHASE]: Continuation from [CURRENT_PHASE]

## ATTACH

/hydrate

You are entering [NEXT_PHASE] of the N-Phase Cycle (AD-005).

Previous phase created these handles:
${artifacts_list}

Key context:
${context_summary}

## Your Mission

[Drawn from NEXT_PHASE skill's Overview, grounded in principles]

## Principles Alignment

This phase emphasizes:
- ${relevant_principle_1} (from spec/principles.md)
- ${relevant_principle_2}

## Exit Criteria

[From NEXT_PHASE skill's Verification section]

## Continuation Imperative

Upon completing this phase, generate the prompt for [PHASE_AFTER_NEXT] using the same structure.

---
```

### Phase Succession Map

| Current | Next | After Next |
|---------|------|------------|
| PLAN | RESEARCH | DEVELOP |
| RESEARCH | DEVELOP | STRATEGIZE |
| DEVELOP | STRATEGIZE | CROSS-SYNERGIZE |
| STRATEGIZE | CROSS-SYNERGIZE | IMPLEMENT |
| CROSS-SYNERGIZE | IMPLEMENT | QA |
| IMPLEMENT | QA | TEST |
| QA | TEST | EDUCATE |
| TEST | EDUCATE | MEASURE |
| EDUCATE | MEASURE | REFLECT |
| MEASURE | REFLECT | (loop to PLAN or DETACH) |

---

## Execution Strategy

### Parallel Track A: SENSE Phase Skills (4 files)
```
research.md → develop.md → strategize.md → cross-synergize.md
```

### Parallel Track B: ACT Phase Skills (4 files)
```
qa.md → test.md → educate.md → measure.md
```

**You can spawn parallel agents** for Track A and Track B since they're independent.

### Sequential: detach-attach.md
After both tracks complete, add Recursive Hologram section.

---

## Verification Checklist

For each skill file:
- [ ] Contains `## Continuation Generator` section
- [ ] References `/hydrate` in generated prompt
- [ ] Specifies correct NEXT_PHASE
- [ ] Includes Context Handoff variables
- [ ] Includes Principles Alignment
- [ ] Includes Exit Criteria from next phase

For detach-attach.md:
- [ ] Contains `## Recursive Hologram` section
- [ ] Contains `## Related` section

---

## Exit Criteria

- [ ] All 8 phase skills have Continuation Generators
- [ ] detach-attach.md has Recursive Hologram
- [ ] `/re-metabolize` report shows Continuation coverage ≥90%
- [ ] Epilogue written to `plans/_epilogues/`

---

## Continuation Imperative

Upon completing this work, generate a prompt for REFLECT phase that:
1. Summarizes the mutations applied
2. Verifies law preservation (identity, associativity)
3. Updates `plans/meta.md` with learnings
4. Runs `/re-metabolize` to verify improvements

---

## Principles Alignment

This work embodies:
- **Composable** (§5): Continuation Generators enable phase composition
- **Generative** (§7): Form generates function; prompts generate prompts
- **Heterarchical** (§6): Each phase can lead the next; no fixed hierarchy

---

## Backfill Plan (DEVELOP → STRATEGIZE handoff)
- **Branches/owners**: `continuation-sense-act` (owner: skills/guild; driver: gpt-5-codex) for doc-only SENSE/ACT backfill. REFLECT hooks stay on `main` unless metrics wiring kicks off (`continuation-reflect-metrics`).
- **SENSE track**: Patch `research.md`, `develop.md`, `strategize.md`, `cross-synergize.md` with Continuation Generators per AD-005 template; embed ledger/entropy placeholders from `phase-accountability.md`. Law check: generator template associative across PLAN→RESEARCH→DEVELOP→STRATEGIZE.
- **ACT track**: Patch `qa.md`, `test.md`, `educate.md`, `measure.md`; generated prompts must carry `/hydrate`, ledger, metrics snapshot (tokens/time/entropy/law_checks). Law check: identity holds when no new artifacts; prompt still grounds on principles.
- **REFLECT guardrail**: After ACT backfill, use `reflect.md` to assert 11/11 skills now host `## Continuation Generator`; `/re-metabolize` should report ≥90% coverage before DETACH.
- **Fixtures tie-in**: Generated prompts cite `metrics/fixtures/process-metrics.jsonl` when live OTEL absent, keeping offline demos lawful (AD-004).
- **Blockers cleared**: `_forest.md` generator located (`impl/claude/protocols/cli/handlers/forest.py`); fixture fidelity set to OTEL-shaped synthetic so auto-continuation can emit consistent metrics even sandboxed.

---

## Quick Reference

```bash
# Files to modify
ls plans/skills/n-phase-cycle/{research,develop,strategize,cross-synergize,qa,test,educate,measure}.md
ls plans/skills/n-phase-cycle/detach-attach.md

# Reference implementations
cat plans/skills/n-phase-cycle/plan.md        # Has Continuation Generator
cat plans/skills/n-phase-cycle/implement.md   # Has Continuation Generator
cat plans/skills/n-phase-cycle/reflect.md     # Has Continuation Generator

# Template
cat plans/skills/n-phase-cycle/auto-continuation.md
```

---

*"The river that knows its course flows without thinking."*
