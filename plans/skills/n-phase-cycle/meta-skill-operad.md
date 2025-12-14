---
path: plans/skills/n-phase-cycle/meta-skill-operad
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

# Meta Skill: Skill Operad (Category-Theoretic Mutation)

> Treat skills as objects in a category and edits as morphisms; mutate lawfully so the library stays composable and durable.

**Difficulty**: Medium  
**Prerequisites**: spec/principles.md (§5 Composable), AD-001/002/003, familiarity with operads/functors  
**Files Touched**: plans/skills/* (including n-phase-cycle), README indices

---

## Overview
Skills themselves are composable programs. This meta skill defines how to add, mutate, and delete skills using operadic grammar:
- **Objects**: Skill documents
- **Morphisms**: Edits (add, refine, prune)
- **Operad**: Allowed compositions (e.g., add section, adjust hologram, cross-link)

The goal is **lawful mutation**: identity and associativity preserved across sessions, preventing drift and bloat.

---

## Step-by-Step

1. **Model the target**: Identify the skill object(s) and desired morphism type (add, refine, prune). Determine arity if composing multiple skills.  
2. **Check laws**: Ensure identity (no-op leaves meaning intact) and associativity (order of independent edits does not change semantics). If law fails, redesign the operation.  
3. **Compose + apply**: Use operad grammar—`plug(operation, subskills)`—to apply the edit. Update cross-links and indices minimally.  
4. **Record hologram**: Verify the skill contains a `Recursive Hologram` section tying it back to the full PLAN→REFLECT loop.

---

## Verification
- Edit can be expressed as morphism composition; identity/associativity hold.  
- Cross-links updated; indices remain curated (no sprawl).  
- `Recursive Hologram` present and aligned with lifecycle.

---

## Mutation Patterns (Operad)
- **AddSkill(skill)**: Introduce new object with template compliance and hologram.
- **RefineSection(skill, section)**: Associative; compose multiple refinements without conflict.
- **Prune(skill)**: Remove or archive when redundant; ensure incoming morphisms reroute or dissolve (no dangling references).
- **Fuse(skill_a, skill_b)**: When overlap >70%, merge into single object; update links; preserve Accursed Share notes.
- **N-Phase mutation hook**: When touching AD-005 skills, always preserve quick-card shape, ledger/entropy fields, and Continuation Generators; compose refinements via `RefineSection` instead of ad-hoc edits.

---

## Recursive Hologram

Apply PLAN→RESEARCH→DEVELOP to skill mutations:

- **PLAN**: What skill object and morphism type? (add/refine/prune/fuse)
- **RESEARCH**: What cross-links and dependencies exist? Which skills reference this one?
- **DEVELOP**: Design the mutation preserving laws (identity/associativity)
- **STRATEGIZE**: Order mutations to minimize churn
- **IMPLEMENT**: Apply via operad grammar
- **TEST**: Verify identity (no-op preserves meaning) and associativity (order-independent)
- **REFLECT**: Did the mutation improve the system? Update this skill if patterns emerge.

The meta-skill is itself an object in the category it describes. Mutations to this file must pass through the same operad it defines.

---

## Related
- `meta-re-metabolize.md` (periodic regeneration loop)  
- `plans/skills/README.md` (template)  
- `plans/principles.md` (Meta-Bloat Prevention)

---

## Changelog
- 2025-12-13: Added Recursive Hologram section (re-metabolize).
- 2025-12-13: Initial version.
