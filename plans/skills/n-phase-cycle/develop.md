# Skill: DEVELOP (N-Phase Cycle)

> Convert research into sharpened specs, APIs, and operable contracts.

**Difficulty**: Medium  
**Prerequisites**: `research.md`, `spec/principles.md`, relevant ADs (001-004)  
**Files Touched**: specs, plans/skills/, design scratchpads; implementation deferred

---

## Overview
DEVELOP is design compression: minimal specs that can regenerate code. It enforces Generative and Tasteful principles—only the necessary primitives and operads survive.

---

## Step-by-Step

1. **Select puppets**: Choose representation (operad, functor, sheaf, puppet) that makes the problem tractable.  
2. **Define contracts**: Inputs/outputs, laws (identity/associativity), error surfaces, hotdata hooks, privacy/ethics constraints.  
3. **Prototype in spec**: Draft examples, reference skills, and edge cases. Annotate risks and decisions for STRATEGIZE.

---

## Recursive Hologram
- Run a micro PLAN→RESEARCH→DEVELOP on the spec draft: what is the smallest generative grammar that still composes?  
- Use `meta-skill-operad.md` to register new primitives/operations; ensure identity and associativity hold for future mutations.

---

## Forest Adapter (dry-run contract)
- Map existing forest CLI functions to AGENTESE handles without code changes: `forest_status()` → `concept.forest.manifest`; `forest_update()` → `concept.forest.refine`; epilogue stream → `time.forest.witness`; dormant-picker → `void.forest.sip`; plan scaffold → `self.forest.define`.  
- Observer roles gate affordances: `ops` (update/define), `meta` (manifest/witness/refine), `guest` (manifest only).  
- Dry-run prompt: "Wrap forest_status/forest_update to emit single-handle responses; no arrays; return lawfulness checks (identity/assoc) as metadata only."

---

## Verification
- Spec/contract exists with examples and invariants.  
- Laws stated and testable; blockers/risks documented.  
- Work ready for sequencing in STRATEGIZE.

---

## Hand-off
Next: `strategize.md` to order delivery and choose leverage points.

---

## Related Skills
- `meta-skill-operad.md`
- `meta-re-metabolize.md`
- `../polynomial-agent.md`
- `../agentese-path.md`

---

## Changelog
- 2025-12-13: Initial version.
