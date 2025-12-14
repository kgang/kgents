---
path: docs/skills/n-phase-cycle/plan
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

# Skill: PLAN (N-Phase Cycle)

> Shape intention into composable chunks with explicit constraints and exits.

**Difficulty**: Easy
**Prerequisites**: HYDRATE.md, plans/principles.md, spec/principles.md
**Files Touched**: plans/_focus.md (read-only), plans/*/*.md headers, plans/_forest.md (auto)

---

## Quick Wield
- **Snap prompt**:
```markdown
/hydrate → PLAN | intent + non-goals | exit criteria | attention budget (incl. 0.05–0.10 entropy) | ledger.PLAN=touched | next=RESEARCH
```
- **Minimal artifacts**: scope + non-goals, exit criteria, chunk list, entropy sip + ledger snippet, branch candidates (if any).
- **Signals**: log tokens/time/entropy + branch count for `process-metrics.md`; update `phase_ledger` + `entropy` in plan header for `_forest.md`.
- **Branch check**: classify branches per `branching-protocol.md`; emit handles or bounty entries before exiting.

---

## The Boldness of PLAN

> *"PLAN is not hesitation disguised as preparation. PLAN is decisive framing."*

When you enter PLAN phase, you are not deferring action—you are CHOOSING. The feeling is:

- **Decisiveness**: "I will do X" not "we could consider X"
- **Commitment**: TodoWrite captures the plan as binding intent
- **Parallel reads**: Read 5 context files at once, not serially
- **Immediate transition**: PLAN exits into RESEARCH within the same session

### The PLAN Manifesto

```
I will choose, not list options.
I will commit via TodoWrite, not hedge.
I will read context files in parallel.
I will exit PLAN into RESEARCH in THIS session.
I will not confuse planning with permission-seeking.
```

---

## Overview
PLAN defines the container for the entire cycle: why this work exists, what success looks like, and how attention will be budgeted across the forest. It enforces Tasteful/Curated scope before energy is spent.

---

## Step-by-Step (With Action)

1. **Intake constraints** (Parallel reads NOW):
   ```python
   Read("plans/_focus.md")      # In parallel
   Read("plans/_forest.md")     # In parallel
   Read("plans/_epilogues/latest.md")  # In parallel
   ```
   Not: "You should read these files"

2. **Strategic research** (When novel domain):
   - Use `WebSearch` for domain expertise, frameworks, prior art
   - Example: "kubernetes operator patterns 2025", "OODA loop decision cycle"
   - Integrate insights into scope definition (don't cargo-cult)

3. **Frame scope + exits** (Decisive declaration):
   - Write TodoWrite with chunks as PENDING
   - Declare: "I WILL implement Track A"
   - Not: "One option would be Track A"

4. **Chunk and schedule** (Commit to parallelization):
   - Identify which chunks can run as parallel agents
   - Mark dependencies explicitly
   - Surface potential branches (see `branching-protocol.md`)
   - Exit to RESEARCH immediately

---

## Recursive Hologram
- Run a micro PLAN→RESEARCH→DEVELOP loop on this plan artifact: What is unknown about the scope? Which specs clarify it? What refinement is needed before others can compose with it?
- Register the plan as a morphism via `meta-skill-operad.md` so future mutations are lawful (identity/associativity preserved).

---

## Accursed Share (Entropy Budget)

PLAN reserves 5-10% for exploration:

- **Scope uncertainty**: Not all boundaries are clear at the start. Budget for discovery.
- **Alternative framings**: The first framing isn't always best. Try 2-3 mental models before committing.
- **Adjacent possibilities**: What else could this enable? Note serendipitous connections.
- **Dormant tree reconnaissance**: What exists in the forest that might compose with this?

Draw: `void.entropy.sip(amount=0.07)`
Return unused: `void.entropy.pour`

---

## Verification
- Plan header exists/updated with blockers, exit criteria, and chunking.
- Accursed Share allocation noted.
- Next phase questions for RESEARCH are explicit.

---

## Common Pitfalls

- **Scope creep in scope definition**: Scope should be explicit non-goals, not just goals. If you can't say what's NOT included, scope is too fuzzy.
- **Missing attention budget**: Every plan should allocate percentage attention, including the 5% Accursed Share for exploration.
- **No exit criteria**: "When is this done?" must be answerable before starting.
- **Monolithic chunking**: If a chunk can't be paused mid-way, it's too large. Prefer 1-2 hour chunks with natural stopping points.
- **Ignoring dormant plans**: PLAN phase should acknowledge what else exists in the forest, not just the current tree.

---

## Hand-off
Next: `research.md` with map targets, unknowns, and files to read.

---

## Continuation Generator

Emit this prompt (short, AGENTESE-ready) when exiting PLAN:

### Exit Signifier

```markdown
# Normal exit (auto-continue):
⟿[RESEARCH]
/hydrate
handles: scope=${scope_summary}; chunks=${chunk_list}; exit=${exit_criteria}; ledger={PLAN:touched}; entropy=${entropy_allocation}; branches=${branch_notes}
mission: map terrain; find invariants/blockers with file:line; avoid duplication (Curated/Composable/Generative).
actions: parallel Read(${file_1}, ${file_2}, ${file_3}); rg "${key_pattern}"; log metrics.
exit: file map + blockers + unknowns; ledger.RESEARCH=touched; continuation → DEVELOP.

# Halt conditions:
⟂[BLOCKED:scope_unclear] Scope needs human clarification before RESEARCH
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

Template vars: `${scope_summary}`, `${chunk_list}`, `${exit_criteria}`, `${entropy_allocation}`, `${branch_notes}`, `${file_1,2,3}`, `${key_pattern}`.

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `branching-protocol.md` — Surface new trees at transitions
- `phase-accountability.md` — Track phase execution
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../plan-file.md`

---

## Changelog
- 2025-12-13: Added strategic research step and branching reference.
- 2025-12-13: Added Accursed Share section (meta-re-metabolize).
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
