# Skill: RESEARCH (N-Phase Cycle)

> Map the landscape, surface constraints, and capture unknowns to de-risk later phases.

**Difficulty**: Medium  
**Prerequisites**: `plan.md`, relevant specs, repo search (`rg`) habits  
**Files Touched**: plans/* (notes), scratch/ or docs/ for findings, no code edits yet

---

## Overview
RESEARCH reduces entropy by discovering prior art, neighboring agents, and invariants. It honors Composable and Curated principles by preventing redundant or conflicting work.

---

## Step-by-Step

1. **Target map**: From PLAN, list artifacts to inspect (specs, modules, fixtures, skills). Use `rg --files` to map surfaces.  
2. **Extract invariants**: Note contracts, functor laws, operad grammars, and hotdata expectations. Record blockers with evidence (file:line).  
3. **Surface deltas**: Identify gaps, risks, or alignment needs (ethics, privacy, taste). Post bounties if friction emerges.

---

## Recursive Hologram
- Apply PLAN→RESEARCH→DEVELOP to the research notes themselves: What unanswered questions remain? Which need micro-development (hypotheses) before STRATEGIZE?  
- Thread findings through `meta-skill-operad.md` to keep notes as composable morphisms (identity = raw citation, composition = stitched trace).

---

## Verification
- File map with references and blockers captured.
- Unknowns enumerated with owners or resolution paths.
- No code changes made; knowledge ready for DEVELOP.

---

## Common Pitfalls

- **Premature coding**: RESEARCH is for mapping, not implementing. If you're writing production code, you've skipped to IMPLEMENT.
- **Shallow search**: Using `grep` once isn't research. Check `plans/skills/`, specs, and related agent directories.
- **Undocumented blockers**: If you find a blocker, write it down with file:line evidence. Verbal "I saw something" isn't stigmergic.
- **Missing prior art check**: Before adding new code, verify no existing agent/functor already does this. Curated principle: don't duplicate.
- **Analysis paralysis**: RESEARCH should have a time-box. If you've been researching for 2+ hours without findings, you're stuck—ask for help or move to DEVELOP with explicit unknowns.

---

## Hand-off
Next: `develop.md` using gathered invariants to shape APIs/specs.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../reconciliation-session.md` (if exists)

---

## Changelog
- 2025-12-13: Initial version.
