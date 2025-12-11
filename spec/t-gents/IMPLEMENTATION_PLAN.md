# T-gent Disambiguation: Spec Implementation Plan

**Status**: ✅ COMPLETE
**Date**: 2025-12-11
**Source**: `docs/t-gent-disambiguation-strategy.md`

---

## Summary of the Problem

The letter **T** in kgents currently serves dual purposes:
- **T-gents (Original)**: Testing/Verification agents (Types I-IV)
- **T-gents Phase 2**: Tool Use framework (1380 lines in `tool-use.md`)

This violates the **Tasteful** principle: *"Each agent serves a clear, justified purpose."*

---

## Critical Discovery: U-gent Conflict

**Issue**: `spec/u-gents/README.md` already exists as "The Understudy" (knowledge distillation).

The disambiguation strategy proposes **U** for "Utility/Tool Use", but U is already taken.

### Resolution Options

| Option | Letter | Current Use | Proposed Use | Trade-offs |
|--------|--------|-------------|--------------|------------|
| **A** | U | Understudy (Distillation) | Utility (Tool Use) | Relocate Understudy elsewhere |
| **B** | X | Unused | Tool Use (e**X**tension) | X evokes "extension", "execution" |
| **C** | Ω | Unused in tools | Tool Use | Greek letter precedent (Ψ-gent) |
| **D** | Keep T | Testing + Tools | Both | Add sub-taxonomy instead |

**Recommended**: **Option A** - Repurpose U for Tool Use

**Rationale**:
1. U-gent (Understudy) could become a *sub-component* of E-gent (Evolution) or B-gent (Economics)
2. "U"tility is a stronger fit: U-se, U-niversal (MCP), U-morphism
3. Distillation is an *optimization technique*, not a core agent genus
4. Tool Use is a *fundamental capability* that deserves a letter

---

## Phase 1: Spec Cleanup (T-gents)

### 1.1 Refine T-gents README.md

**Goal**: T-gents = Testing/Verification ONLY

**Changes to `spec/t-gents/README.md`**:
- Remove any references to "Tool Use" as Phase 2
- Clarify the taxonomy: Types I-V (Adversarial stays)
- Update "See Also" section to remove tool-use.md

**Draft Header**:
```markdown
# T-gents: The Algebra of Reliability

The letter **T** represents **Testing** agents—morphisms designed to
verify, perturb, observe, and judge the behavior of other agents.

## The Five Types

| Type | Name | Purpose |
|------|------|---------|
| I | Nullifiers | MockAgent, FixtureAgent (constant/lookup morphisms) |
| II | Saboteurs | FailingAgent, NoiseAgent (perturbation & chaos) |
| III | Observers | SpyAgent, PredicateAgent (identity with side effects) |
| IV | Critics | JudgeAgent, PropertyAgent (LLM evaluators) |
| V | Adversarial | AdversarialGym, StressCoordinate (chaos engineering) |
```

### 1.2 Mark tool-use.md as Deprecated

**Changes to `spec/t-gents/tool-use.md`**:
- Add deprecation notice at top
- Reference new location in U-gents
- Keep file for historical reference (with clear status)

**Draft Deprecation Notice**:
```markdown
---
**⚠️ DEPRECATED**: This specification has been migrated to `spec/u-gents/`.

The tool-use framework belongs to **U-gents** (Utility agents), not T-gents.
T-gents are now exclusively for **Testing/Verification**.

See: [U-gents Tool Use](../u-gents/tool-use.md)
---
```

### 1.3 Create T-gents Type V: Adversarial

**File**: `spec/t-gents/taxonomy.md` already covers Types I-IV.
**Action**: Promote `adversarial.md` concepts to formal Type V.

**Changes**:
- Add Type V section to taxonomy.md
- Reference adversarial.md for detailed spec
- Ensure AdversarialGym is the "crown jewel" of T-gents

---

## Phase 2: Migrate Tool Use to U-gents

### 2.1 Relocate U-gent (Understudy)

**Issue**: Current U-gent is "The Understudy" (distillation).

**Proposed Resolution**: Move Understudy to E-gent or B-gent

**Option A: Merge into E-gent (Evolution)**
- E-gent already handles improvement cycles
- Distillation is a form of model evolution
- New file: `spec/e-gents/distillation.md`

**Option B: Merge into B-gent (Economics)**
- B-gent handles token economics
- Distillation is an economic optimization (cheaper inference)
- New file: `spec/b-gents/distillation.md`

**Recommended**: **Option B** (B-gent)
- The Understudy's primary value is *economic* (cost reduction)
- E-gent is about capability improvement, not cost
- B-gent's ROI formula already references distillation concepts

### 2.2 Rewrite U-gents as Utility/Tool Use

**New `spec/u-gents/README.md`**:
```markdown
# U-gents: The Algebra of Utility

The letter **U** represents **Utility** agents—typed morphisms
specialized for external interaction through composable tool interfaces.

## Philosophy

> "A tool is not an external function. It is an agent with a contract."

## The Six Types

| Type | Name | Purpose |
|------|------|---------|
| I | Core | Tool[A,B], ToolMeta, PassthroughTool |
| II | Wrappers | TracedTool, CachedTool, RetryTool |
| III | Execution | ToolExecutor, CircuitBreaker, RetryExecutor |
| IV | MCP | MCPClient, MCPTool, Transports |
| V | Security | PermissionClassifier, AuditLogger |
| VI | Orchestration | ParallelOrchestrator, Supervisor, Handoff |
```

### 2.3 Create U-gent Spec Files

**Directory Structure**:
```
spec/u-gents/
├── README.md          # Overview (rewritten)
├── core.md            # Type I: Tool[A,B] base class
├── wrappers.md        # Type II: Tracing, caching, retry
├── execution.md       # Type III: ToolExecutor, CircuitBreaker
├── mcp.md             # Type IV: MCP protocol integration
├── security.md        # Type V: Permissions, audit
├── orchestration.md   # Type VI: Multi-tool patterns
└── tool-use.md        # Full spec (migrated from T-gents)
```

### 2.4 Migrate tool-use.md Content

**Steps**:
1. Copy `spec/t-gents/tool-use.md` → `spec/u-gents/tool-use.md`
2. Update all "T-gent" references → "U-gent"
3. Update cross-references (L-gent, D-gent, W-gent integrations)
4. Add U-gent-specific introduction

---

## Phase 3: Update Cross-References

### 3.1 Files Referencing T-gent Tool Use

**Search Pattern**: `tool-use`, `Tool[`, `ToolExecutor`

**Files to Update**:
- `spec/README.md` (main index)
- `spec/p-gents/README.md` (parser integration)
- `spec/d-gents/README.md` (caching integration)
- `spec/l-gents/README.md` (registry integration)
- `spec/w-gents/README.md` (observability integration)
- `CLAUDE.md` (project overview)
- `HYDRATE.md` (session context)

### 3.2 Update CLAUDE.md Agent Taxonomy

**Current**:
```markdown
| T | T-gents | Testing (Types I-IV) + Tool Use (Types V-IX) |
```

**New**:
```markdown
| T | T-gents | Testing/Verification (Types I-V) |
| U | U-gents | Utility/Tool Use (Types I-VI) |
```

### 3.3 Update HYDRATE.md

Add U-gent section under "Agent Quick Reference".

---

## Phase 4: Verify Consistency

### 4.1 Cross-Reference Audit

Run grep to find orphaned references:
```bash
grep -r "T-gent.*tool" spec/
grep -r "Tool\[" spec/
grep -r "ToolExecutor" spec/
```

### 4.2 Diagram Updates

If any diagrams reference T-gent tool use, update to U-gent.

### 4.3 Principle Verification

Verify the split satisfies principles:

| Principle | T-gents (Testing) | U-gents (Utility) |
|-----------|-------------------|-------------------|
| Tasteful | ✓ Single purpose: verify | ✓ Single purpose: extend |
| Curated | ✓ 5 distinct types | ✓ 6 distinct types |
| Composable | ✓ T-gents test U-gents | ✓ U-gents compose via >> |
| Generative | ✓ Regenerable from spec | ✓ Regenerable from spec |

---

## Implementation Order

### Session 1: Foundation (This Session)

1. ✅ Read and analyze all relevant specs
2. ✅ Identify U-gent conflict (Understudy)
3. ⬜ Create this implementation plan
4. ⬜ Decision: Where does Understudy go?

### Session 2: T-gent Cleanup

1. Update `spec/t-gents/README.md` (remove tool references)
2. Update `spec/t-gents/taxonomy.md` (add Type V: Adversarial)
3. Mark `spec/t-gents/tool-use.md` as deprecated

### Session 3: U-gent Creation

1. Archive current `spec/u-gents/README.md` (Understudy)
2. Create `spec/b-gents/distillation.md` (relocated Understudy)
3. Create new `spec/u-gents/README.md` (Tool Use overview)
4. Migrate `tool-use.md` to U-gents

### Session 4: U-gent Expansion

1. Create `spec/u-gents/core.md`
2. Create `spec/u-gents/mcp.md`
3. Create `spec/u-gents/execution.md`

### Session 5: Cross-Reference Updates

1. Update `spec/README.md`
2. Update `CLAUDE.md`
3. Update `HYDRATE.md`
4. Update all cross-references

### Session 6: Verification

1. Run cross-reference audit
2. Verify principle alignment
3. Update diagrams if needed

---

## Open Questions

### Q1: Understudy Relocation

**Where should the Understudy spec go?**

| Option | Pros | Cons |
|--------|------|------|
| B-gent | Economic focus matches | B-gent is "Banker", not "Optimizer" |
| E-gent | Improvement focus matches | E-gent is "Evolution", not "Compression" |
| New letter (D?) | Clean separation | D-gent is "Data", letter conflict |

**Recommended**: B-gent. The Understudy's ROI formula is already in B-gent's domain.

### Q2: Tool Use Spec Depth

**How detailed should U-gent specs be vs. tool-use.md?**

- README.md: Overview + philosophy (~200 lines)
- Type-specific files: Detailed specs (~300-500 lines each)
- tool-use.md: Full integrated spec (keep as-is, ~1380 lines)

### Q3: Backward Compatibility

**Should old paths redirect?**

Symlinks or explicit "moved to" notices for:
- `spec/t-gents/tool-use.md` → `spec/u-gents/tool-use.md`

---

## Success Criteria

The disambiguation is complete when:

1. ✅ T-gents README mentions only testing (Types I-V)
2. ✅ U-gents README covers tool use (Types I-VI)
3. ✅ tool-use.md lives in U-gents with updated references
4. ✅ Understudy content preserved in B-gent distillation.md
5. ✅ All cross-references updated
6. ✅ CLAUDE.md and HYDRATE.md reflect new taxonomy
7. ✅ Principle alignment verified

---

## Files Changed Summary

### Modified

- `spec/t-gents/README.md` - Remove tool use references
- `spec/t-gents/taxonomy.md` - Add Type V: Adversarial
- `spec/t-gents/tool-use.md` - Add deprecation notice
- `spec/u-gents/README.md` - Rewrite for Tool Use
- `spec/README.md` - Update taxonomy table
- `CLAUDE.md` - Update agent table
- `HYDRATE.md` - Add U-gent section

### Created

- `spec/t-gents/IMPLEMENTATION_PLAN.md` - This file
- `spec/u-gents/core.md` - Tool[A,B] base spec
- `spec/u-gents/mcp.md` - MCP integration spec
- `spec/u-gents/execution.md` - ToolExecutor spec
- `spec/u-gents/tool-use.md` - Full spec (migrated)
- `spec/b-gents/distillation.md` - Understudy (relocated)

### Archived/Moved

- `spec/u-gents/README.md` (Understudy) → `spec/b-gents/distillation.md`

---

*"The best time to plant a tree was 20 years ago. The second best time is now."*
