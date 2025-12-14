# Meta Skill: Re-Metabolize Slash Command ( ~/.claude/commands/re-metabolize )

> Design a slash command that puppets the lifecycle as a being: reads specs, digests meta-learnings, and advocates for self-renewal.

**Difficulty**: Medium  
**Prerequisites**: `meta-re-metabolize.md`, `meta-skill-operad.md`, `plans/principles.md`, reference implementation style from `~/.claude/commands/chief`

---

## Overview
This slash command is an agentic metabolizer that periodically re-reads specs, skills, and principles, then proposes lawful mutations to the skill system. It embodies the Accursed Share by reserving exploration budget and runs as an **endofunctor on skills**.

---

## Intended Behavior

- **Ingest**: Pull `HYDRATE.md`, `spec/principles.md`, `plans/principles.md`, and all `plans/skills/n-phase-cycle/*.md`.  
- **Diagnose drift**: Detect missing hologram sections, stale metrics, broken cross-links, or law violations (identity/associativity).  
- **Propose mutations**: Emit structured suggestions (add/refine/prune/fuse) expressed as operad morphisms per `meta-skill-operad.md`.  
- **Schedule lookbacks**: Trigger `lookback-revision.md` when divergence or high entropy is observed.  
- **Trace + metrics**: Log token usage, run duration, law checks passed/failed, and exploration fraction (Accursed Share) into a transparent report.

---

## Slash Command Shape

```
~/.claude/commands/re-metabolize
  - reads: specs + skills
  - outputs: recommendations file + trace/metrics summary
  - options:
      --dry-run          # analyze only
      --apply-plan PATH  # write bounties/plan stubs instead of code
      --entropy p        # exploration probability (default 0.05)
```

Implementation should mirror the ergonomics of `~/.claude/commands/chief` (single file, clear stdout banners, respectful of sandboxes).

---

## Metrics (command-level)
- Token usage: prompt + completion per run.  
- Drift score: % skills missing hologram / cross-links / metrics.  
- Lawfulness: identity/associativity check count and failures.  
- Exploration spend: fraction of output dedicated to Accursed Share ideas.  
- Adoption: # recommendations accepted/rejected over time.

---

## Recursive Hologram
- Mini-cycle the command: PLAN (scope), RESEARCH (inputs), DEVELOP (options), STRATEGIZE (apply vs dry-run), IMPLEMENT (script), QA/TEST (law checks), EDUCATE (usage doc), MEASURE (metrics), REFLECT (command epilogue).  
- Re-run `meta-re-metabolize.md` on the command itself monthly or after principle changes.

---

## Verification
- Dry-run produces actionable deltas without edits.  
- Metrics emitted and traceable.  
- Recommendations expressed via `meta-skill-operad.md` grammar.

---

## Related
- `meta-re-metabolize.md`  
- `meta-skill-operad.md`  
- `lookback-revision.md`

---

## Changelog
- 2025-12-13: Initial design scaffold.
