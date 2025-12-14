---
path: n-phase-accursed-share-completion
status: active
progress: 5
priority: 7.0
effort: 2
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: [re-metabolize-health]
tags: [meta, n-phase-cycle, accursed-share]
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: pending continuation wiring
  IMPLEMENT: skipped  # reason: doc-only
  QA: skipped  # reason: doc-only
  TEST: skipped  # reason: doc-only
  EDUCATE: skipped  # reason: doc-only
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.0
  returned: 0.05
---

# Plan: Complete Accursed Share Sections in N-Phase Cycle Skills

> *"Every phase reserves entropy for the unexpected. Without it, the cycle ossifies."*

**Origin**: Re-metabolize report 2025-12-13
**Drift Signal**: 14% Accursed Share coverage (3/11 core phases)
**Target**: 100% coverage (11/11 core phases)

---

## PLAN: Intent and Scope

### Why This Matters

The Accursed Share (Bataille's concept) is the mandatory 5-10% entropy budget per phase. It ensures:

1. **Exploration doesn't get squeezed out** — Pressure to ship can eliminate serendipity
2. **Phase-specific creativity** — Each phase has unique exploration opportunities
3. **Explicit acknowledgment** — If entropy isn't budgeted, it's stolen from quality
4. **Self-similar structure** — README documents the budget; each skill should too

### Scope

| In Scope | Out of Scope |
|----------|--------------|
| 8 core phase skills missing Accursed Share | Meta skills (auto-continuation, etc.) |
| Phase-specific entropy examples | Implementation of AGENTESE void.* paths |
| Consistent section formatting | Changes to entropy amounts (keep 0.05-0.10) |

### Target Skills

| # | Skill | Current State | Action |
|---|-------|---------------|--------|
| 1 | `research.md` | No Accursed Share | ADD |
| 2 | `develop.md` | No Accursed Share | ADD |
| 3 | `strategize.md` | No Accursed Share | ADD |
| 4 | `cross-synergize.md` | No Accursed Share | ADD |
| 5 | `test.md` | No Accursed Share | ADD |
| 6 | `educate.md` | No Accursed Share | ADD |
| 7 | `measure.md` | No Accursed Share | ADD |
| 8 | `reflect.md` | No Accursed Share | ADD |

**Already Complete**: `plan.md`, `implement.md`, `qa.md`

### Exit Criteria

- [ ] All 8 skills have `## Accursed Share (Entropy Budget)` section
- [ ] Each section has 3+ phase-specific exploration examples
- [ ] Each section has `void.entropy.sip` and `void.entropy.pour` calls
- [ ] Changelog updated in each file
- [ ] Drift score improves from 14% to 100%

### Chunks

| Chunk | Skills | Effort | Parallelizable |
|-------|--------|--------|----------------|
| A | research, develop | 0.5 | Yes (with B) |
| B | strategize, cross-synergize | 0.5 | Yes (with A) |
| C | test, educate | 0.5 | Yes (with D) |
| D | measure, reflect | 0.5 | Yes (with C) |

**Total Effort**: 2.0 (can compress to 1.0 with parallelization)

---

## RESEARCH: Existing Pattern Analysis

### Template from `plan.md` (Reference Implementation)

```markdown
## Accursed Share (Entropy Budget)

PLAN reserves 5-10% for exploration:

- **Scope uncertainty**: Not all boundaries are clear at the start. Budget for discovery.
- **Alternative framings**: The first framing isn't always best. Try 2-3 mental models before committing.
- **Adjacent possibilities**: What else could this enable? Note serendipitous connections.
- **Dormant tree reconnaissance**: What exists in the forest that might compose with this?

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`
```

### Template from `implement.md`

```markdown
## Accursed Share (Entropy Budget)

IMPLEMENT reserves 5-10% for exploration:

- **Micro-refactors**: If you see a better name or structure while coding, take it (within scope).
- **Edge case intuition**: Follow hunches about failure modes—they often reveal bugs.
- **Tool discovery**: Try a new pytest marker or mypy flag if it might help.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`
```

### Template from `qa.md`

```markdown
## Accursed Share (Entropy Budget)

QA's entropy is spent on:

- **Edge case exploration**: Try degraded modes that might fail. That's where bugs hide.
- **Alternative lint rules**: Sometimes ruff suggests a refactor. Follow it briefly—it might be right.
- **Graceful degradation paths**: Document what happens when dependencies are missing.

Draw: `void.entropy.sip(amount=0.05)`
Return unused: `void.entropy.pour`
```

### Pattern Extracted

1. **Header**: `## Accursed Share (Entropy Budget)`
2. **Intro line**: `{PHASE} reserves 5-10% for exploration:` or `{PHASE}'s entropy is spent on:`
3. **Bullet points**: 3-4 phase-specific exploration opportunities
4. **Footer**: `Draw: void.entropy.sip(amount=0.0X)` and `Return unused: void.entropy.pour`
5. **Placement**: After Recursive Hologram, before Verification (or after Step-by-Step if no hologram before Verification)

---

## DEVELOP: Phase-Specific Entropy Budgets

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

## STRATEGIZE: Mutation Order

### Execution Order

1. **Chunk A+B (parallel)**: research, develop, strategize, cross-synergize
2. **Chunk C+D (parallel)**: test, educate, measure, reflect
3. **Verification pass**: Check all 8 files
4. **README check**: Confirm alignment with README Accursed Share section

### Risk Assessment

| Risk | Mitigation |
|------|------------|
| Inconsistent formatting | Use exact template from DEVELOP section |
| Wrong placement | Insert after Recursive Hologram, before Verification |
| Missing changelog | Update changelog in same edit |

### Dependencies

```
None → research.md ─┐
None → develop.md ──┼─→ Verification
None → strategize.md ┤
None → cross-synergize.md ┘
```

All mutations are independent. Full parallelization possible.

---

## CROSS-SYNERGIZE: Composition Opportunities

### Related Work

| Work | Synergy |
|------|---------|
| `re-metabolize-slash-command.md` | Will use these sections for drift detection |
| `process-metrics.md` | Accursed Share metrics now have explicit sources |
| `metatheory.md` | Kaizen section references entropy budget |

### Bounty Board Check

No open bounties related to Accursed Share. This work may resolve:
- Implicit expectation that phases budget exploration

---

## IMPLEMENT: Mutation Specification

### Operad Expression

```python
for skill in [research, develop, strategize, cross_synergize,
              test, educate, measure, reflect]:
    apply(
        meta_skill_operad.RefineSection,
        target=f"{skill}.md",
        section="Accursed Share (Entropy Budget)",
        placement="after Recursive Hologram, before Verification",
        content=DEVELOP_SECTION[skill],
        changelog_entry=f"2025-12-13: Added Accursed Share section (re-metabolize)."
    )
```

### Placement Rule

Insert between `## Recursive Hologram` and `## Verification` sections.

If skill has `## Common Pitfalls` before Verification, insert before that.

---

## QA: Verification Checklist

- [ ] Section header matches: `## Accursed Share (Entropy Budget)`
- [ ] Intro line mentions phase name and "5-10%"
- [ ] 3+ bullet points with phase-specific examples
- [ ] `void.entropy.sip(amount=0.0X)` present
- [ ] `void.entropy.pour` present
- [ ] Changelog updated
- [ ] No trailing whitespace
- [ ] Consistent markdown formatting

---

## TEST: Law Verification

### Identity Law

Adding Accursed Share section should not change the semantic meaning of the phase. Test:
- Phase step-by-step unchanged
- Exit criteria unchanged
- Continuation Generator unchanged

### Associativity Law

Order of adding sections across files should not affect final state. Test:
- Apply to research.md first, then develop.md
- Apply to develop.md first, then research.md
- Final state should be identical

---

## EDUCATE: Documentation Updates

### README.md Check

Current README already documents:
```markdown
## Entropy Budget

- **Per phase**: 0.05–0.10 (5-10% for exploration)
- **Draw**: `void.entropy.sip(amount=0.07)`
- **Return unused**: `void.entropy.pour`
- **Replenish**: `void.gratitude.tithe`
```

No README update needed. Individual skills now match README.

---

## MEASURE: Success Metrics

| Metric | Before | Target | Measurement |
|--------|--------|--------|-------------|
| Accursed Share coverage | 14% (3/11) | 100% (11/11) | Grep for section |
| Drift score | 14% | 0% | Re-metabolize report |
| Law compliance | 100% | 100% | Manual review |

---

## REFLECT: Expected Learnings

### Hypothesis

Adding explicit Accursed Share sections will:
1. Make entropy budget visible at point of use
2. Provide phase-specific exploration prompts
3. Improve re-metabolize health score

### Learnings to Capture

After implementation, note:
- Which phase-specific prompts proved most useful
- Whether entropy amounts should vary more by phase
- If any phases need more than 4 exploration examples

---

## Continuation Prompt

Upon completing this plan, generate:

```markdown
# RESEARCH: Accursed Share Completion

## ATTACH

/hydrate

You are executing the Accursed Share Completion plan.

## Context

- 8 skills need Accursed Share sections
- Templates designed in DEVELOP section of plan
- Placement: after Recursive Hologram, before Verification

## Your Mission

1. Read the 3 existing Accursed Share sections (plan.md, implement.md, qa.md)
2. Apply the 8 mutations from the plan's DEVELOP section
3. Update changelogs
4. Run verification checklist

## Exit Criteria

- All 8 skills have Accursed Share sections
- Drift score: 100%
- Law compliance: 100%
```

---

*void.entropy.sip(amount=0.05). The plan reserves exploration for surprises.*
