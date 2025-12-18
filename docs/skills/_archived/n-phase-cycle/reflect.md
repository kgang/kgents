# Skill: REFLECT (N-Phase Cycle)

> Synthesize outcomes, extract learnings, and prepare the next loop.

**Difficulty**: Easy  
**Prerequisites**: `measure.md`, epilogues, bounty board signals  
**Files Touched**: plans/_epilogues/, plans/meta.md (only if distilled), plans/_bounty.md

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → REFLECT | outcomes + learnings | ledger.REFLECT=touched | entropy.sip(0.05–0.10) | next=PLAN/meta-re-metabolize/DETACH
```
- **Minimal artifacts**: epilogue, one-line zettels (Molasses Test), bounty updates, continuation decision, ledger update, branch list.
- **Signals**: log tokens/time/entropy + branch count + continuation type for `process-metrics.md`.
- **Branch check**: capture new seeds for future cycles; emit handles before exit.

---

## Overview
REFLECT closes the current cycle by distilling what mattered—successes, failures, surprises—and deciding what to re-metabolize. It honors Curated/Tasteful restraint and the Accursed Share (cherish slop before pruning).

---

## Step-by-Step

1. **Summarize outcomes**: Capture what shipped, what changed, and remaining risks.
2. **Distill learnings**: One-line zettels only; promote to `plans/meta.md` sparingly (pass Molasses Test).
3. **Seed next cycle**: Write epilogue, open/resolve bounties, and propose entry point for PLAN.
4. **Archive or upgrade**: Every REFLECT must decide: archive plans, upgrade to spec, or justify retention.

---

## Aggressive Archiving Protocol

> *"The forest must breathe. Dead plans choke new growth."*

**REFLECT is the archiving gate.** Every cycle that touches plans must end with explicit archiving decisions:

### The Three Paths for Every Plan

| Path | When | Action |
|------|------|--------|
| **Archive** | Goal achieved, superseded, or abandoned | Move to `plans/_archive/YYYY-MM-DD-{name}.md` |
| **Upgrade** | Contains reusable patterns/insights | Distill to `spec/` or `docs/skills/`, then archive original |
| **Retain** | Active work, clear next steps | Update YAML header with current session_notes |

### Archiving Criteria (Mandatory Check)

```markdown
## REFLECT Archiving Checklist

For each plan touched this cycle:
- [ ] **{plan_name}**: [Archive / Upgrade / Retain]
  - Reason: [goal achieved / superseded by {x} / still active]
  - If Upgrade: Target spec/skill: [path]
  - If Retain: Next step: [what]

Plans archived this session: [count]
Plans upgraded to spec: [count]
```

### Upgrade-to-Spec Triggers

Promote to spec/skill when:
- Pattern used 3+ times across plans
- Insight applies beyond single feature
- Learning is stable (won't change next week)

### Anti-Pattern: Zombie Plans

**Zombie detection** (check in REFLECT):
- Last touched >14 days ago
- Progress <25%
- No dependencies (nothing blocks on it)
- **Action**: Archive with reason "zombie: [explanation]"

### Archive File Format

```markdown
# Archived: {original_name}

**Archived**: YYYY-MM-DD
**Reason**: {goal achieved | superseded | zombie | merged into X}
**Learnings Preserved**:
- {one-liner to meta.md if worthy}
- {or "none - tactical only"}

---
{original content below for archaeology}
```

---

## Recursive Hologram
- Mini-cycle the reflection: PLAN (questions), RESEARCH (signals), DEVELOP (insight framing), STRATEGIZE (what to re-metabolize).
- Use `meta-skill-operad.md` to make learnings composable morphisms; schedule `meta-re-metabolize.md` if drift detected.

---

## Accursed Share (Entropy Budget)

REFLECT reserves 5-10% for exploration:

- **Counterfactual thinking**: What if we'd taken the other path? Document the road not taken.
- **Meta-pattern recognition**: Is this the third time we've hit this issue? It might be systemic.
- **Gratitude practice**: What worked that we didn't expect? Acknowledge the gifts.
- **Skill gap identification**: What would have made this easier? That's a future skill to develop.

Draw: `void.entropy.sip(amount=0.10)`
Return unused: `void.entropy.pour`

---

## Verification
- Epilogue written; bounties updated; optional meta entry distilled.
- Clear proposal for next PLAN; Accursed Share acknowledged.
- Re-metabolization trigger decided.

---

## Common Pitfalls

- **Skipping reflection entirely**: "No time to reflect" guarantees repeated mistakes. 10 minutes of REFLECT saves hours in the next cycle.
- **Multi-line meta entries**: The Molasses Test: if it can't fit in one line, it's not distilled enough. Refine or move to a plan file.
- **meta.md bloat**: Hard cap is 50 lines. If adding your insight requires pruning, either prune something older or your insight isn't atomic.
- **Ignoring the Accursed Share**: REFLECT should acknowledge what exploration occurred, even if it led nowhere. Failed experiments are offerings, not waste.
- **Missing next-cycle entry point**: Every epilogue should propose where to start next. Don't leave successors guessing.

---

## Hand-off
Next: `meta-re-metabolize.md` when the lifecycle or skills need refresh; otherwise loop back to `plan.md`.

---

## Continuation Generator

REFLECT is the terminal phase. It generates one of three continuation types.

### Exit Signifiers

REFLECT uses all three signifier modes:

```markdown
# Continue to new cycle:
⟿[PLAN]
/hydrate
handles: learnings=${meta_learnings}; artifacts=${artifacts_created}; entropy.restored=${entropy_restored}; ledger={REFLECT:touched}
mission: frame intent for next body of work; incorporate learnings.
exit: scope + exit criteria + entropy sip; continuation → RESEARCH.

# Trigger skill refresh:
⟿[META-RE-METABOLIZE]
/hydrate
handles: drift=${drift_signals}; learnings=${learnings_for_skills}; ledger={REFLECT:touched}
mission: re-ingest N-phase skills; apply lawful mutations via operad.
exit: skills refreshed; laws verified; continuation → PLAN.

# Session end:
⟂[DETACH:cycle_complete] Epilogue: ${epilogue_ref}
⟂[DETACH:awaiting_human] Decision required: ${decision_context}
```

### Detailed Templates

### Option 1: Loop to PLAN (New Cycle)

```markdown
# PLAN: New Cycle after REFLECT

## ATTACH

/hydrate

You are entering a new N-Phase Cycle (AD-005).

Previous cycle distilled these learnings:
- ${meta_learnings}

Accumulated handles from prior cycle:
- ${artifacts_created}

Entropy restored via tithe: ${entropy_restored}
Phase ledger to reconcile: ${phase_ledger}
Process metrics snapshot: ${metrics_snapshot}

## Your Mission

Frame intent for the next body of work. Incorporate learnings from prior cycle.

**Principles Alignment**:
- All seven principles from spec/principles.md
- Special attention to: ${principles_highlighted_by_reflect}

## Questions to Answer

- What is the scope of this new cycle?
- What can be skipped based on prior learnings?
- How does forest health inform attention allocation?

## Continuation Imperative

Upon completing PLAN, generate the prompt for RESEARCH.
The form is the function.
```

### Option 2: Trigger Meta-Re-Metabolize (Skill Refresh)

```markdown
# META-RE-METABOLIZE: Triggered by REFLECT

## ATTACH

/hydrate

REFLECT detected drift or accumulated learnings requiring skill refresh.

Drift signals:
- ${drift_signals}

Learnings to integrate:
- ${learnings_for_skills}
Phase ledger to reconcile: ${phase_ledger}
Process metrics snapshot: ${metrics_snapshot}

## Your Mission

Re-ingest the N-phase cycle skills. Apply lawful mutations via meta-skill-operad.md.

**Focus areas**:
- Continuation Generators: Are they producing effective prompts?
- Recursive Holograms: Still aligned with full cycle?
- Verification sections: Exit criteria accurate?

## Actions

1. Read all skills in docs/skills/n-phase-cycle/
2. Compare against spec/principles.md
3. Propose mutations as operad morphisms
4. Preserve Accursed Share in every skill

## Exit Criteria

- All skills contain current Continuation Generator sections
- Laws (identity/associativity) verified
- Index updated
```

### Option 3: DETACH (Session Boundary)

```markdown
# DETACH: Session End after REFLECT

## Handle Created

This session is ending. A handle has been created for future ATTACH.

**Epilogue**: plans/_epilogues/${date}-${session}.md
**Continuation prompt**: prompts/${project}-continuation.md

## Handle Contents

Artifacts created:
- ${artifacts}

Entropy remaining: ${entropy}

Suggested next tracks:
- ${suggested_tracks}
Phase ledger to reconcile: ${phase_ledger}
Process metrics snapshot: ${metrics_snapshot}

## For Future Observer

To continue:
1. /hydrate
2. Read the continuation prompt
3. ATTACH to the track that calls to you
4. Act from principles with courage

*void.gratitude.tithe. The river flows onward.*
```

---

### Choosing the Continuation Type

| Condition | Generate |
|-----------|----------|
| More work in current scope | Loop to PLAN |
| Drift detected or skill staleness | Meta-Re-Metabolize |
| Session ending, work incomplete | DETACH |
| Cycle complete, scope exhausted | DETACH (with "complete" status) |

---

## Backward Propagation

REFLECT has a unique responsibility: it can **refine the generators** of prior phases.

If REFLECT discovers that PLAN prompts should include something:
```python
apply(
    meta_skill_operad.RefineSection,
    target="plan.md",
    section="Continuation Generator",
    delta="Add dependency graph to template variables"
)
```

This is the double-loop from lookback-revision.md made operational.

---

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `lookback-revision.md`
- `detach-attach.md`
- `../reconciliation-session.md` (if exists)

---

## Changelog
- 2025-12-13: Added Accursed Share section (re-metabolize).
- 2025-12-13: Added Continuation Generator section with three options.
- 2025-12-13: Initial version.
