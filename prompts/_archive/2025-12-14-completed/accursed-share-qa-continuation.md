# QA: Accursed Share Completion

## ATTACH

/hydrate

You are entering the QA phase of the N-Phase Cycle for the Accursed Share Completion plan.

---

## Context from Previous Phases

### IMPLEMENT Output
- **Files modified**: 8 phase skill files
- **Sections added**: `## Accursed Share (Entropy Budget)` in each
- **Changelog updated**: All 8 files have `2025-12-13: Added Accursed Share section (re-metabolize).`

| Skill | Entropy Amount | Key Exploration Examples |
|-------|----------------|--------------------------|
| research.md | 0.07 | Tangent following, external knowledge, historical archaeology |
| develop.md | 0.07 | Alternative representations, law discovery, puppet swapping |
| strategize.md | 0.05 | Order experiments, risk probing, abort criteria |
| cross-synergize.md | 0.10 | Dormant tree awakening, functor hunting, bounty scan |
| test.md | 0.05 | Property test intuition, mutation testing, hotdata discovery |
| educate.md | 0.05 | Alternative explanations, demo discovery, personality injection |
| measure.md | 0.07 | Metric invention, counter-metrics, dashboard sketching |
| reflect.md | 0.10 | Counterfactual thinking, gratitude practice, skill gap identification |

### Placement Rule Applied
- After `## Recursive Hologram`
- Before `## Verification` (or `## Forest Adapter` in develop.md, then before Verification)

---

## Your Mission

Verify formatting, placement, and consistency across all 8 skills. You are:

1. **Checking structure**: Each section has correct header, intro, 3-4 bullets, and footer
2. **Verifying placement**: Section appears after Recursive Hologram, before Verification
3. **Validating entropy calls**: `void.entropy.sip(amount=X)` and `void.entropy.pour` present
4. **Confirming changelog**: Each file has the re-metabolize changelog entry

**Principles Alignment** (from spec/principles.md):
- **Curated**: Content is phase-specific, not generic
- **Composable**: Sections follow consistent morphism pattern
- **Generative**: Pattern from existing sections, applied consistently

---

## Actions to Take NOW

```python
# Verify all 8 files
for skill in ["research", "develop", "strategize", "cross-synergize",
              "test", "educate", "measure", "reflect"]:
    Read(f"plans/skills/n-phase-cycle/{skill}.md")
    # Check:
    # 1. ## Accursed Share (Entropy Budget) exists
    # 2. Intro line: "{PHASE} reserves 5-10% for exploration:"
    # 3. 3-4 bullet points with bold headers
    # 4. void.entropy.sip and void.entropy.pour
    # 5. Changelog entry present
```

---

## QA Checklist

- [ ] **research.md**: Section present, 4 bullets, sip(0.07), changelog updated
- [ ] **develop.md**: Section present, 4 bullets, sip(0.07), placement before Forest Adapter, changelog updated
- [ ] **strategize.md**: Section present, 4 bullets, sip(0.05), changelog updated
- [ ] **cross-synergize.md**: Section present, 4 bullets, sip(0.10), changelog updated
- [ ] **test.md**: Section present, 4 bullets, sip(0.05), changelog updated
- [ ] **educate.md**: Section present, 4 bullets, sip(0.05), changelog updated
- [ ] **measure.md**: Section present, 4 bullets, sip(0.07), changelog updated
- [ ] **reflect.md**: Section present, 4 bullets, sip(0.10), changelog updated

---

## Exit Criteria

- [ ] All 8 skills pass QA checklist
- [ ] No formatting inconsistencies
- [ ] Entropy amounts match DEVELOP phase design (see table above)
- [ ] Ready for TEST phase (law compliance verification)

---

## Phase Trace

| Phase | Status | Key Output |
|-------|--------|------------|
| PLAN | ✓ | Scope, exit criteria, chunks |
| RESEARCH | ✓ | Pattern extracted from 3 existing sections |
| DEVELOP | ✓ | 8 phase-specific sections designed |
| STRATEGIZE | ✓ | Independent mutations, parallelizable |
| CROSS-SYNERGIZE | ✓ | Links to re-metabolize, process-metrics |
| IMPLEMENT | ✓ | 8 files edited, changelogs updated |
| QA | → in_progress | This phase |
| TEST | pending | Law compliance |
| EDUCATE | ⊘ skip | README already aligned |
| MEASURE | pending | Drift score 14% → 100% |
| REFLECT | pending | Capture learnings |

---

## Continuation Imperative

Upon completing QA, generate the prompt for TEST:
- ATTACH with /hydrate
- Context: QA passed, files verified
- Mission: Verify law compliance (Accursed Share morphism laws)
- Exit criteria: All skills follow pattern consistently

Then continue through MEASURE → REFLECT.

**The form is the function.**

---

## Branching Check

| Potential Branch | Classification |
|------------------|----------------|
| None identified | — |

No branches surfaced. Continue main line.

---

*void.entropy.sip(amount=0.03). Begin QA verification.*
