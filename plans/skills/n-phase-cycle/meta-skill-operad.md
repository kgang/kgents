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

---

## Related
- `meta-re-metabolize.md` (periodic regeneration loop)  
- `plans/skills/README.md` (template)  
- `plans/principles.md` (Meta-Bloat Prevention)

---

## Changelog
- 2025-12-13: Initial version.
