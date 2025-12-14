---
path: docs/skills/n-phase-cycle/meta-re-metabolize
status: active
progress: 0
last_touched: 2025-12-13
touched_by: gpt-5-codex
blocking: []
enables: []
session_notes: |
  Header added for forest compliance (STRATEGIZE).
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: skipped  # reason: doc-only
  STRATEGIZE: touched
  CROSS-SYNERGIZE: skipped  # reason: doc-only
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

# Meta Skill: Re-Metabolize the Lifecycle

> Periodically re-ingest the N-phase cycle and its skills so the factory stays alive, not ossified.

**Difficulty**: Medium  
**Prerequisites**: All phase skills, `meta-skill-operad.md`, latest epilogue signals  
**Files Touched**: docs/skills/n-phase-cycle/*, docs/skills/README.md (index), optional plans/meta.md (distilled learnings)

---

## Overview
Re-metabolization is an endofunctor on the skill category: it takes the current lifecycle skill set and returns an updated, law-preserving version. It prevents drift, reintroduces the Accursed Share, and keeps category laws intact over long time horizons.

---

## Step-by-Step

1. **Trigger check**: Run when REFLECT flags drift, when principles change, or on a cadence (monthly).  
2. **Survey + compare**: Apply PLAN→RESEARCH→DEVELOP micro-cycles to each skill: is the hologram intact? do steps still reflect reality? note redundancies.  
3. **Mutate with operad**: Use `meta-skill-operad.md` morphisms to refine/prune/fuse skills. Preserve identities (baseline) and associativity (composition order).  
4. **Integrate lookbacks**: Pull in `lookback-revision.md` outputs to ensure double-loop changes (goal/frame shifts) are included, not just execution tweaks.  
5. **Re-seed Accursed Share**: Add or refresh exploration prompts in each skill’s hologram to keep entropy budget alive.  
6. **Publish delta**: Update indices, summarize changes in epilogue, and flag follow-ups for PLAN or the slash command metabolizer.

---

## Verification
- All phase skills still contain `Recursive Hologram` sections and current exit criteria.
- All phase skills contain `Continuation Generator` sections (auto-continuation).
- Quick-card + ledger/entropy snippets stay consistent across phases (for `_forest` ingestion).
- Redundant skills merged or archived; new needs captured.
- Next PLAN entry point recorded; Accursed Share preserved.
- Lookback deltas incorporated; slash command plan updated if needed.

---

## Continuation Generator

Meta-re-metabolize is itself a phase. Upon exit, generate one of:

### Option 1: Return to Normal Cycle

```markdown
# PLAN: After Meta-Re-Metabolize

## ATTACH

/hydrate

Meta-re-metabolization complete. Skills refreshed.

Changes made:
- ${skills_modified}
- ${generators_updated}

Law verification:
- ${law_check_results}

## Your Mission

Resume normal N-Phase Cycle with refreshed skills.
The generators now produce better prompts.

## Continuation Imperative

Use the updated Continuation Generators. They will propagate the learnings.
```

### Option 2: Cascade Meta-Refresh

If meta-re-metabolize discovers the auto-continuation mechanism itself needs updating:

```markdown
# AUTO-CONTINUATION REFRESH

## ATTACH

/hydrate

Meta-re-metabolize discovered that auto-continuation.md needs updating.

Drift signals:
- ${drift_in_continuation_mechanism}

## Your Mission

Update auto-continuation.md via meta-skill-operad.RefineSection.
Then propagate changes to all phase Continuation Generators.

This is the system updating itself.
The form is the function.
```

---

## The Meta-Reflexive Property

This skill embodies the core insight: **the form is the function**.

```
meta-re-metabolize.md → execution → may update auto-continuation.md
                                  → auto-continuation.md generates prompts
                                  → prompts invoke phases
                                  → phases REFLECT
                                  → REFLECT triggers meta-re-metabolize
                                  → loop closes
```

The system is a quine that improves itself through each iteration.

---

## Related
- `auto-continuation.md` — The mechanism this skill must verify and may update
- `meta-skill-operad.md`
- `reflect.md` (trigger source)
- `plans/principles.md` (forest/meta-bloat guards)
- `lookback-revision.md`
- `re-metabolize-slash-command.md`
- `process-metrics.md`

---

## Changelog
- 2025-12-13: Added Continuation Generator and meta-reflexive property.
- 2025-12-13: Initial version.
