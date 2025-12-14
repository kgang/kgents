# IMPLEMENT: Accursed Share Completion

## ATTACH

/hydrate

You are entering the IMPLEMENT phase of the N-Phase Cycle for the Accursed Share Completion plan.

---

## Context from Previous Phases

### PLAN Output
- **Scope**: Add Accursed Share sections to 8 phase skills
- **Target skills**: research.md, develop.md, strategize.md, cross-synergize.md, test.md, educate.md, measure.md, reflect.md
- **Exit criteria**: 100% Accursed Share coverage (currently 14%)
- **Plan file**: `plans/n-phase-accursed-share-completion.md`

### RESEARCH Output
- **Pattern extracted** from plan.md, implement.md, qa.md:
  - Header: `## Accursed Share (Entropy Budget)`
  - Intro: `{PHASE} reserves 5-10% for exploration:`
  - 3-4 phase-specific bullet points
  - Footer: `void.entropy.sip` + `void.entropy.pour`
  - Placement: After Recursive Hologram, before Verification

### DEVELOP Output
8 phase-specific Accursed Share sections designed. Full content in plan file section "DEVELOP: Phase-Specific Entropy Budgets".

| Skill | Key Entropy Examples |
|-------|---------------------|
| research | Tangent following, external knowledge, historical archaeology |
| develop | Alternative representations, law discovery, puppet swapping |
| strategize | Order experiments, risk probing, abort criteria |
| cross-synergize | Dormant tree awakening, functor hunting, bounty scan |
| test | Property test intuition, mutation testing, hotdata discovery |
| educate | Alternative explanations, demo discovery, personality injection |
| measure | Metric invention, counter-metrics, dashboard sketching |
| reflect | Counterfactual thinking, gratitude practice, skill gap identification |

### STRATEGIZE Output
- All 8 mutations are independent
- Full parallelization possible
- Placement rule: After `## Recursive Hologram`, before `## Verification`
- If `## Common Pitfalls` exists before Verification, insert before that

### CROSS-SYNERGIZE Output
- Links to `re-metabolize-slash-command.md` (drift detection)
- Links to `process-metrics.md` (entropy tracking)
- No blocking bounties

---

## Your Mission

Apply the 8 Accursed Share mutations to the phase skills. You are:

1. **Reading** each target skill file
2. **Locating** the insertion point (after Recursive Hologram, before Verification)
3. **Inserting** the designed Accursed Share section from the plan
4. **Updating** the changelog with: `2025-12-13: Added Accursed Share section (re-metabolize).`

**Principles Alignment** (from spec/principles.md):
- **Composable**: Sections are morphisms; insertion preserves structure
- **Curated**: Phase-specific content, not generic
- **Generative**: Pattern from existing sections, applied consistently

---

## Actions to Take NOW

```python
# Parallel batch 1: SENSE phases
Edit("plans/skills/n-phase-cycle/research.md", ...)
Edit("plans/skills/n-phase-cycle/develop.md", ...)
Edit("plans/skills/n-phase-cycle/strategize.md", ...)
Edit("plans/skills/n-phase-cycle/cross-synergize.md", ...)

# Parallel batch 2: ACT + REFLECT phases
Edit("plans/skills/n-phase-cycle/test.md", ...)
Edit("plans/skills/n-phase-cycle/educate.md", ...)
Edit("plans/skills/n-phase-cycle/measure.md", ...)
Edit("plans/skills/n-phase-cycle/reflect.md", ...)
```

For each file:
1. Read the file
2. Find `## Recursive Hologram` section
3. Find `## Verification` or `## Common Pitfalls` section
4. Insert Accursed Share section between them
5. Update Changelog

---

## Accursed Share Content Reference

### research.md
```markdown
## Accursed Share (Entropy Budget)

RESEARCH reserves 5-10% for exploration:

- **Tangent following**: Sometimes the adjacent file reveals more than the target. Follow interesting threads briefly.
- **External knowledge**: Use WebSearch for frameworks or patterns that might inform the work.
- **Alternative mappings**: The first file map isn't always complete. Try different grep patterns.
- **Historical archaeology**: Check git blame or old PRs—past decisions often explain current structure.

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`
```

### develop.md
```markdown
## Accursed Share (Entropy Budget)

DEVELOP reserves 5-10% for exploration:

- **Alternative representations**: Try 2-3 type signatures before committing. The best interface often isn't the first.
- **Law discovery**: What invariants should hold? Sketch property tests even if you don't run them yet.
- **Composition experiments**: Can this agent compose with existing functors? Try `Agent >> Flux` or `Maybe >> Agent`.
- **Puppet swapping**: What if we modeled this as a different category? (State vs Reader vs Writer)

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`
```

### strategize.md
```markdown
## Accursed Share (Entropy Budget)

STRATEGIZE reserves 5-10% for exploration:

- **Order experiments**: Try reverse order or random order—sometimes dependencies reveal themselves.
- **Risk probing**: What's the scariest chunk? Consider doing it first to de-risk early.
- **Parallel discovery**: Which chunks are secretly independent? Parallelization often hides.
- **Abort criteria**: What would make us stop this track entirely? Name it now.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`
```

### cross-synergize.md
```markdown
## Accursed Share (Entropy Budget)

CROSS-SYNERGIZE reserves 5-10% for exploration:

- **Dormant tree awakening**: Skim `plans/_forest.md` for forgotten plans that might compose.
- **Functor hunting**: What existing functors could lift this work? Check `FunctorRegistry`.
- **Unexpected compositions**: Try composing with something that "shouldn't" work. Sometimes it does.
- **Bounty board scan**: Read `plans/_bounty.md`—your work might resolve an open gripe.

Draw: `void.entropy.sip(amount=0.10)`
Return unused: `void.entropy.pour`
```

### test.md
```markdown
## Accursed Share (Entropy Budget)

TEST reserves 5-10% for exploration:

- **Property test intuition**: What invariants feel true? Write a hypothesis even if coverage isn't required.
- **Mutation testing**: Manually break the code—does the test catch it? If not, the test is weak.
- **Hotdata discovery**: Is there real-world data that could replace synthetic fixtures?
- **Flaky investigation**: If a test is flaky, spend entropy understanding why before marking it slow.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`
```

### educate.md
```markdown
## Accursed Share (Entropy Budget)

EDUCATE reserves 5-10% for exploration:

- **Alternative explanations**: Try explaining to three different personas. One framing will click.
- **Demo discovery**: What's the smallest runnable example? Sometimes the demo IS the documentation.
- **Failure documentation**: What happens when it breaks? Users need error paths too.
- **Personality injection**: Where can joy live in this documentation? Find the human moment.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`
```

### measure.md
```markdown
## Accursed Share (Entropy Budget)

MEASURE reserves 5-10% for exploration:

- **Metric invention**: What signal would you WANT but don't have? Sometimes it's measurable.
- **Counter-metrics**: What would indicate this feature is harmful? Measure that too.
- **Correlation hunting**: What other metrics might move when this one does?
- **Dashboard sketching**: Sketch the ideal dashboard before instrumenting. Work backward.

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`
```

### reflect.md
```markdown
## Accursed Share (Entropy Budget)

REFLECT reserves 5-10% for exploration:

- **Counterfactual thinking**: What if we'd taken the other path? Document the road not taken.
- **Meta-pattern recognition**: Is this the third time we've hit this issue? It might be systemic.
- **Gratitude practice**: What worked that we didn't expect? Acknowledge the gifts.
- **Skill gap identification**: What would have made this easier? That's a future skill to develop.

Draw: `void.entropy.sip(amount=0.10)`
Return unused: `void.entropy.pour`
```

---

## Exit Criteria

- [ ] All 8 skills have `## Accursed Share (Entropy Budget)` section
- [ ] Each section has 3+ phase-specific exploration examples
- [ ] Each section has `void.entropy.sip` and `void.entropy.pour`
- [ ] Changelog updated in each file
- [ ] Sections placed correctly (after Recursive Hologram, before Verification)

---

## Phase Trace

| Phase | Status | Key Output |
|-------|--------|------------|
| PLAN | ✓ | Scope, exit criteria, chunks |
| RESEARCH | ✓ | Pattern extracted from 3 existing sections |
| DEVELOP | ✓ | 8 phase-specific sections designed |
| STRATEGIZE | ✓ | Independent mutations, parallelizable |
| CROSS-SYNERGIZE | ✓ | Links to re-metabolize, process-metrics |
| IMPLEMENT | → in_progress | This phase |
| QA | pending | Verify formatting |
| TEST | pending | Law compliance |
| EDUCATE | ⊘ skip | README already aligned |
| MEASURE | pending | Drift score 14% → 100% |
| REFLECT | pending | Capture learnings |

---

## Continuation Imperative

Upon completing IMPLEMENT, generate the prompt for QA:
- ATTACH with /hydrate
- Context: Files modified, sections added
- Mission: Verify formatting, placement, changelog
- Exit criteria: QA checklist passed

Then continue through TEST → MEASURE → REFLECT.

**The form is the function.**

---

## Branching Check

| Potential Branch | Classification |
|------------------|----------------|
| None identified | — |

No branches surfaced. Continue main line.

---

*void.entropy.sip(amount=0.05). Begin implementation.*
