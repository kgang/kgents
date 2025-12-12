# Session Epilogue: 2025-12-11-forest-protocol

> *"The first session that tends the forest, not just the tallest tree."*

---

## What We Did

### Created Forest Protocol
- Wrote `plans/principles.md` with 8 principles for AI-agent coordination
- Created `plans/_forest.md` as the canopy view for session starts
- Established `plans/_epilogues/` directory for session continuity

### Identified Problems Solved
1. **KING Project**: Monolithic NEXT_SESSION_PROMPT created tunnel vision
2. **Lost Projects**: Plans at 0% had no visibility mechanism
3. **No Meta-Cognition**: No way for AI to know forest shape

### Key Concepts Introduced
- **Stigmergic Coordination**: Plans leave pheromone trails (YAML headers)
- **Attention Budgeting**: 60/25/10/5 split across forest
- **Accursed Share**: 5% mandatory exploration of dormant plans
- **Session Continuity**: Epilogues connect sessions narratively

### YAML Headers Added
- `self/interface.md` - Active, 0%
- `self/stream.md` - Dormant, 70%, enables self/memory
- `self/memory.md` - Blocked, 30%, blocking on self/stream
- `concept/creativity.md` - Active, 80%

---

## What We Learned

1. The current plan structure was linear (NEXT → focus → complete → NEXT)
2. Plans are peers, not hierarchy—heterarchical per `spec/principles.md`
3. Forest Protocol maps cleanly to AGENTESE concepts:
   - Plans as dormant agents
   - Stigmergy as coordination mechanism
   - Accursed Share as mandatory exploration

---

## What Needs To Be Done Next

### Priority 1: Complete YAML Header Migration

Add headers to remaining plans:
- `void/entropy.md`
- `concept/lattice.md`
- `agents/t-gent.md`
- `agents/u-gent.md`

Each header needs:
```yaml
---
path: void/entropy
status: dormant          # dormant | blocked | active | complete
progress: 0
last_touched: 2025-12-XX
touched_by: claude-XXX
blocking: []             # What this plan is waiting on
enables: []              # What plans are waiting on this
session_notes: |
  Free-form notes for next agent
---
```

### Priority 2: Automate `_forest.md` Generation

Options:
- **A**: Python script in `impl/claude/protocols/cli/` → `kgents forest status`
- **B**: Claude Code command `/forest-update`
- **C**: Git hook on commit

The script should parse all `plans/**/*.md`, extract YAML frontmatter, generate `_forest.md`.

### Priority 3: Decide NEXT_SESSION_PROMPT.md Coexistence

The file currently holds I-gent v2.5 Phase 2 work (a "KING" situation). Options:
- **A**: Delete entirely, use `_forest.md` only
- **B**: Keep as "60% primary focus" file (risks recreating KING)
- **C**: Rename to `_focus.md` with explicit budget notation

**Recommendation**: Option C—make it explicit that this is the 60% budget, not 100%.

### Priority 4: Accursed Share Rotation

Implement tracking for which dormant plan is "next" in rotation:
```
Week 1: void/entropy
Week 2: concept/lattice
Week 3: agents/y-gent (if exists)
Week 4: user's choice
```

Add `accursed_share_next:` field to `_forest.md`.

### Priority 5: Cross-Reference with spec/principles.md

Ensure alignment:
| spec/principles.md | plans/principles.md |
|--------------------|---------------------|
| Heterarchical (§6) | Forest Over King (§1) |
| Accursed Share (meta) | Accursed Share (§7) |
| Composable (§5) | Parallel Paths (§6) |
| Transparent Infrastructure | Transparent Proprioception (§8) |

---

## Unresolved Questions

1. **YAML header format standardization**: Should all plans have identical fields, or allow extensions?

2. **Automation approach**: Python script vs CLI command vs git hook?

3. **Enforcement mechanism**: How do we ensure agents actually follow the 60/25/10/5 split?

4. **Dormant plan attention tracking**: How do we know which dormant plan is "next"?

---

## Files Reference

**Essential reads for next session:**
```bash
cat plans/principles.md      # The Forest Protocol (339 lines)
cat plans/_forest.md         # Current canopy view
cat plans/_status.md         # Detailed status matrix
```

**Example YAML headers:**
```bash
head -15 plans/self/interface.md   # Active plan
head -15 plans/self/memory.md      # Blocked plan (shows blocking: field)
head -15 plans/self/stream.md      # Plan that enables another
```

**Verify alignment:**
```bash
cat spec/principles.md       # Project-level principles
```

---

## Success Criteria for Continuation

This continuation is successful if:

1. [ ] All remaining plans have YAML headers
2. [ ] `_forest.md` reflects current state accurately
3. [ ] A mechanism exists for generating `_forest.md` (even manual script)
4. [ ] Decision made on NEXT_SESSION_PROMPT.md fate
5. [ ] Epilogue written for the continuation session

---

## Key Design Decisions (Already Made)

| Decision | Rationale |
|----------|-----------|
| YAML frontmatter | Machine-readable, standard format, works with MD tools |
| `_` prefix for meta-files | Sorts to top, distinguishes from content plans |
| `blocking:` not `blocked_by:` | "This plan is blocking [others]" semantics |
| Session epilogues | Narrative continuity > structured checklists |
| 5% Accursed Share | Mandatory exploration prevents project starvation |

---

## The Meta-Principle

From `plans/principles.md`:

> A plan is not a document. It is a dormant agent awaiting its season.

The planning system is itself an agent ecosystem. Treating it as such—with stigmergy, heterarchy, and the Accursed Share—resolves the problems of king projects, lost trees, and memoryless sessions.

---

*"The forest is wiser than any single tree." — Forest Protocol*
