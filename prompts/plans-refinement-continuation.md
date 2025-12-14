# Continuation: Plans Directory Refinement (Phase 2)

## ATTACH

/hydrate

---

## Context from Previous Phase (SENSE + ACT)

**What was accomplished**:
1. Deep audit of `plans/` directory identified terminology proliferation (5+ competing metaphors)
2. Brainstormed 3 evolution paths: Compression, Layered, AGENTESE-Pure
3. Chose synthesis: **Layered AGENTESE** with Three-Phase simplification
4. Refactored:
   - `HYDRATE.md`: Compressed from 124 → 90 lines, introduced Three Phases
   - `plans/meta.md`: Pruned from 83 → 56 lines, within 50-line spirit
   - `plans/skills/n-phase-cycle/README.md`: Added Three-Phase as default, 11-Phase as Crown Jewels

**Key Decisions Made**:
- **Three Phases** (SENSE → ACT → REFLECT) compress 11 phases without loss
- **Unified terminology**: Ground, Canopy, Mycelium, Roots, Spores, Skills
- **LOD structure**: One-liner → HYDRATE → Protocol → Deep dives

---

## Your Mission (REFLECT Phase)

Complete the refinement by:

### 1. Consolidate Redundant Files

The audit identified redundancy:
- `plans/principles.md` (728 lines) overlaps with `spec/principles.md` (970 lines)
- `plans/README.md` duplicates HYDRATE.md
- `plans/_status.md` duplicates `_forest.md`

**Action**:
- Merge essential unique content from `plans/principles.md` into `spec/principles.md` (if any)
- Delete `plans/principles.md` or reduce to a pointer
- Update `plans/README.md` to be a minimal pointer to HYDRATE.md
- Merge `plans/_status.md` into `_forest.md` if needed, or delete

### 2. Update Cross-References

Files that reference old terminology:
- `plans/skills/README.md` - update to use unified terms
- Individual skill files may reference old 11-phase as primary

### 3. Create the Three-Phase Skill Document

**File**: `plans/skills/three-phase.md`

A single skill document that captures:
- When to use Three-Phase (default)
- When to escalate to 11-Phase (Crown Jewels)
- How SENSE/ACT/REFLECT map to AGENTESE contexts
- Continuation generation for each phase

### 4. Write Epilogue

Write to `plans/_epilogues/2025-12-13-plans-refinement.md`:
- What was changed
- What learnings emerged
- What remains for future sessions

---

## Principles Alignment

This work embodies:
- **Tasteful** — Prune what doesn't serve
- **Curated** — Quality over quantity
- **Composable** — Three phases compose into any workflow
- **Generative** — Simpler seed, same generative power

---

## Exit Criteria

- [ ] No redundant meta files
- [ ] HYDRATE.md under 100 lines
- [ ] meta.md under 50 lines
- [ ] Three-Phase documented as primary approach
- [ ] Cross-references updated
- [ ] Epilogue written

---

## Continuation Imperative

Upon completing this phase, generate a prompt for the next observer that:
1. References `/hydrate` for grounding
2. Summarizes what was learned about plans/ architecture
3. Identifies any remaining terminology debt
4. Points to next work (likely memory substrate or dashboard textual refactor)

---

*"Compress, don't expand. The butterfly must escape the molasses."*
