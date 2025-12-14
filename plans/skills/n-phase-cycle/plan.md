# Skill: PLAN (N-Phase Cycle)

> Shape intention into composable chunks with explicit constraints and exits.

**Difficulty**: Easy
**Prerequisites**: HYDRATE.md, plans/principles.md, spec/principles.md
**Files Touched**: plans/_focus.md (read-only), plans/*/*.md headers, plans/_forest.md (auto)

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

2. **Frame scope + exits** (Decisive declaration):
   - Write TodoWrite with chunks as PENDING
   - Declare: "I WILL implement Track A"
   - Not: "One option would be Track A"

3. **Chunk and schedule** (Commit to parallelization):
   - Identify which chunks can run as parallel agents
   - Mark dependencies explicitly
   - Exit to RESEARCH immediately

---

## Recursive Hologram
- Run a micro PLAN→RESEARCH→DEVELOP loop on this plan artifact: What is unknown about the scope? Which specs clarify it? What refinement is needed before others can compose with it?
- Register the plan as a morphism via `meta-skill-operad.md` so future mutations are lawful (identity/associativity preserved).

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

Upon exiting PLAN, generate the following prompt for invoking RESEARCH:

---

### Generated Prompt: RESEARCH after PLAN

```markdown
# RESEARCH: Continuation from PLAN

## ATTACH

/hydrate

You are entering RESEARCH phase of the N-Phase Cycle (AD-005).

Previous phase (PLAN) created these handles:
- Scope definition: ${scope_summary}
- Chunks identified: ${chunk_list}
- Exit criteria declared: ${exit_criteria}
- Entropy budget: ${entropy_allocation}

Key decisions made:
- ${key_decisions}

Blockers to investigate:
- ${blockers_or_unknowns}

## Your Mission

Map the terrain to de-risk later phases. You are reducing entropy by discovering:
- Prior art (existing code, skills, specs)
- Invariants (contracts, laws, hotdata expectations)
- Blockers (with file:line evidence)

**Principles Alignment** (from spec/principles.md):
- **Curated**: Prevent redundant work by finding what exists
- **Composable**: Note contracts and functor laws
- **Generative**: Identify compression opportunities

## Actions to Take NOW

1. Parallel reads:
   ```python
   Read("${file_1}")  # In parallel
   Read("${file_2}")  # In parallel
   Read("${file_3}")  # In parallel
   ```

2. Search for prior art:
   ```python
   Grep(pattern="${key_pattern}", type="py")
   Glob(pattern="**/skills/*.md")
   ```

3. Surface blockers with evidence (file:line)

## Exit Criteria

- File map with references and blockers captured
- Unknowns enumerated with owners or resolution paths
- No code changes made; knowledge ready for DEVELOP

## Continuation Imperative

Upon completing RESEARCH, generate the prompt for DEVELOP using this same structure:
- ATTACH with /hydrate
- Context from RESEARCH (invariants found, blockers surfaced)
- Mission aligned with DEVELOP's purpose
- Continuation imperative for STRATEGIZE

The form is the function. The cycle perpetuates through principled generation.
```

---

### Template Variables

| Variable | Source |
|----------|--------|
| `${scope_summary}` | From PLAN step 2 (frame scope) |
| `${chunk_list}` | From TodoWrite items created |
| `${exit_criteria}` | From Verification section |
| `${entropy_allocation}` | From Accursed Share allocation |
| `${key_decisions}` | Decisions made during PLAN |
| `${blockers_or_unknowns}` | Questions for RESEARCH to answer |
| `${file_1,2,3}` | Target files from scope |
| `${key_pattern}` | Search pattern for prior art |

---

## Related Skills
- `auto-continuation.md` — The meta-skill defining this generator pattern
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../plan-file.md`

---

## Changelog
- 2025-12-13: Added Continuation Generator section (auto-continuation).
- 2025-12-13: Initial version.
