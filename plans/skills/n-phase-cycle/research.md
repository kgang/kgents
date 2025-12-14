---
path: plans/skills/n-phase-cycle/research
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

# Skill: RESEARCH (N-Phase Cycle)

> Map the landscape, surface constraints, and capture unknowns to de-risk later phases.

**Difficulty**: Medium
**Prerequisites**: `plan.md`, relevant specs, repo search (`rg`) habits
**Files Touched**: plans/* (notes), scratch/ or docs/ for findings, no code edits yet

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → RESEARCH | targets=${files_mapped_guess} | invariants to hunt | ledger.RESEARCH=touched | entropy.sip(0.05–0.10) | next=DEVELOP
```
- **Minimal artifacts**: file map with refs, blockers (file:line), unknowns + owner, entropy ledger update, branch candidates.
- **Signals**: record tokens/time/entropy + law/invariant hits for `process-metrics.md`; keep ledger + branch notes `_forest`-ready.
- **Branch check**: log blockers that force scope split; emit bounty or branch handle if new tracks appear.

---

## Overview
RESEARCH reduces entropy by discovering prior art, neighboring agents, and invariants. It honors Composable and Curated principles by preventing redundant or conflicting work.

---

## Step-by-Step

1. **Target map**: From PLAN, list artifacts to inspect (specs, modules, fixtures, skills). Use `rg --files` to map surfaces.
2. **Internet research** (when applicable): Use WebSearch for state-of-the-art patterns, established frameworks, or domain expertise. Document findings with source URLs for traceability. See **External Knowledge Sourcing** below.
3. **Extract invariants**: Note contracts, functor laws, operad grammars, and hotdata expectations. Record blockers with evidence (file:line).
4. **Surface deltas**: Identify gaps, risks, or alignment needs (ethics, privacy, taste). Post bounties if friction emerges.

---

## External Knowledge Sourcing

Internet research is appropriate when:

| Trigger | Example Query |
|---------|---------------|
| Novel domain | "kubernetes operator patterns 2025" |
| Established frameworks | "OODA loop decision cycle", "double-loop learning Argyris" |
| Library/API usage | "anthropic python SDK streaming" |
| Performance patterns | "async python memory optimization" |
| Security considerations | "OWASP top 10 LLM applications" |

**Protocol**:
1. Use `WebSearch` with specific, focused queries
2. Include the year (2025) for up-to-date results
3. Document sources in notes: `[Title](URL) - key insight`
4. Synthesize into codebase context (don't cargo-cult)
5. Apply Curated principle: external patterns must earn their place

**Anti-patterns**:
- Searching for every implementation detail (use existing patterns first)
- Blindly importing external patterns without adaptation
- Missing citations (sources enable verification)

---

## Recursive Hologram
- Apply PLAN→RESEARCH→DEVELOP to the research notes themselves: What unanswered questions remain? Which need micro-development (hypotheses) before STRATEGIZE?
- Thread findings through `meta-skill-operad.md` to keep notes as composable morphisms (identity = raw citation, composition = stitched trace).

---

## Accursed Share (Entropy Budget)

RESEARCH reserves 5-10% for exploration:

- **Tangent following**: Sometimes the adjacent file reveals more than the target. Follow interesting threads briefly.
- **External knowledge**: Use WebSearch for frameworks or patterns that might inform the work.
- **Alternative mappings**: The first file map isn't always complete. Try different grep patterns.
- **Historical archaeology**: Check git blame or old PRs—past decisions often explain current structure.

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`

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

## Continuation Generator

Emit this when exiting RESEARCH:

```markdown
/hydrate
# DEVELOP ← RESEARCH
handles: files=${files_mapped}; invariants=${invariants}; blockers=${blockers_with_evidence}; prior_art=${prior_art}; ledger=${phase_ledger}; entropy=${entropy_spent}/${entropy_remaining}; branches=${branch_notes}
mission: choose representations + contracts; capture laws + hotdata expectations; prototype spec examples.
actions: pick puppet/functor/operad; define inputs/outputs/errors/privacy; note risks; log metrics tokens/time/law-check count.
exit: spec/contract + examples + laws; blockers/risks ready for sequencing; ledger.DEVELOP=touched; continuation → STRATEGIZE.
```

Template vars: `${files_mapped}`, `${invariants}`, `${blockers_with_evidence}`, `${prior_art}`, `${phase_ledger}`, `${entropy_spent}`, `${entropy_remaining}`, `${branch_notes}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../reconciliation-session.md` (if exists)

---

## Changelog
- 2025-12-13: Added Accursed Share section (re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
