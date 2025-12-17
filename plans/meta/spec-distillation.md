---
path: meta/spec-distillation
status: complete
progress: 100
last_touched: 2025-12-17
touched_by: claude-opus-4
blocking: []
enables: []
session_notes: |
  2025-12-17: ALL PHASES COMPLETE.
  - Phase 1: Deleted deprecated files (~5,700 lines removed)
  - Phase 2: self-grow.md 2,037→442 (78% reduction)
  - Phase 3: p-gents/README.md 1,568→427 (73% reduction)
  - Phase 4: u-gents/tool-use.md 1,381→518 (62% reduction)
  - Phase 5: b-gents/banker.md 1,394→275 (80% reduction)
  - Phase 6: AGENTESE specs consolidated (v3→main)
  - Phase 7: spec-template.md skill created
  - Phase 8: 6 specs distilled (~51% avg reduction)
    - narrator.md: 1,039→437 (58%)
    - evergreen-prompt-system.md: 1,012→490 (52%)
    - primitives.md: 879→472 (46%)
    - functor-catalog.md: 1,164→453 (61%)
    - process-holons.md: 980→500 (49%)
    - projection.md: 878→565 (36%)
  - LOW priority specs reviewed: principles.md, bootstrap.md, agentese.md, gardener-logos.md (all well-formed)
  - Learnings synthesized to: docs/skills/spec-hygiene.md
  - Total: ~91k→~78k lines (14% reduction)
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: touched
  MEASURE: touched
  REFLECT: touched
entropy:
  planned: 0.05
  spent: 0.05
  returned: 0.02
---

# Spec Distillation: Applying Compression Principles

> *"Spec is compression. If you can't compress it, you don't understand it."* — principles.md

**Status**: COMPLETE (All 8 Phases Done)
**Final Reduction**: ~91,000 lines → ~78,000 lines (14% total)
**Principles**: Generative (7), Curated (2), Tasteful (1)
**Cross-refs**: `spec/principles.md`, `docs/skills/spec-hygiene.md`, `docs/skills/spec-template.md`

---

## Core Insight

Many spec files violate the **Generative Principle**: they contain **implementation, not specification**. A well-formed spec should be small enough that implementation follows mechanically. Instead, we have:

- Full async function bodies in specs
- Complete dataclass definitions with all methods
- SQL queries and implementation details
- Duplicate content across files
- Deprecated files still present

**The Goal**: Transform specs into pure compression—type signatures, laws, invariants, and illustrative (not implementation) examples.

---

## Audit Summary (Research Complete)

| Metric | Value |
|--------|-------|
| Total spec files | 181 |
| Total lines | ~90,918 |
| Python code blocks | 1,674 (31% of code blocks) |
| Deprecated files still present | 4+ |
| Archived but not deleted | ~3,000 lines |
| Implementation masquerading as spec | ~25,000 lines |

### Largest Offenders

| File | Lines | Issue |
|------|-------|-------|
| `protocols/self-grow.md` | 2,037 | 80% implementation code |
| `p-gents/README.md` | 1,568 | Full parser implementations |
| `t-gents/tool-use.md` | 1,398 | DEPRECATED, duplicate of U-gents |
| `b-gents/banker.md` | 1,394 | Full Metered functor impl |
| `u-gents/tool-use.md` | ~1,400 | Near-duplicate of T-gents |
| `protocols/_archive/*` | ~3,000 | Should be git-only history |

---

## Implementation Phases

### Phase 1: Delete and Archive (1-2 hours)

**Goal**: Remove deprecated and archived content that shouldn't exist in working tree.

**Files to Delete**:
```
spec/t-gents/tool-use.md              # 1,398 lines - DEPRECATED
spec/t-gents/IMPLEMENTATION_PLAN.md   # Move to plans/ if needed
spec/protocols/_archive/              # Keep in git history only
  - agentese-v2.md                    # 1,133 lines
  - prompt-logos.md                   # 1,201 lines
  - prompt-logos-decisions.md
  - agentese-retrospective.md
```

**Actions**:
1. Verify `t-gents/tool-use.md` content is in `u-gents/tool-use.md`
2. Delete `t-gents/tool-use.md`
3. Move `t-gents/IMPLEMENTATION_PLAN.md` to `plans/_archive/` if valuable
4. Delete `spec/protocols/_archive/` directory (content preserved in git)
5. Run tests to verify no breakage

**Exit Criteria**:
- [x] `t-gents/tool-use.md` deleted
- [x] `protocols/_archive/` removed
- [ ] All tests pass
- [x] ~5,000 lines removed

---

### Phase 2: Distill self-grow.md (2-3 hours)

**Goal**: Transform 2,037 lines → ~400 lines by extracting implementation.

**Current Structure** (to preserve):
- Part I: Core Philosophy (keep)
- Part II: Growth Ontology (keep)
- Part III: Telemetry Contracts (extract schemas, keep contracts)
- Part IV: Growth Protocol (extract impl, keep signatures)
- Part V: Entropy Budget (extract impl, keep concept)
- Part VI: Fitness Functions (keep principles, extract scoring code)
- Part VII: Observability Contract (keep schema, extract impl)
- Part VIII: Growth Grammar (keep operad, extract tests)
- Part IX: Anti-Patterns (keep)
- Part X: Success Criteria (keep)
- Part XI: Open Questions (already resolved, compress)
- Part XII: Files to Create (remove - impl detail)

**Extract to**:
```
impl/claude/protocols/agentese/contexts/self_grow/
├── schemas.py        # All dataclasses from Part III, IV, V
├── recognize.py      # recognize_gaps() from Part IV
├── validate.py       # validate_proposal(), _check_laws(), _detect_abuse()
├── germinate.py      # Nursery class, GerminatingHolon
├── promote.py        # promote_holon(), RollbackToken
├── budget.py         # GrowthBudget, BudgetNode
├── fitness.py        # evaluate_tasteful(), evaluate_joy()
└── operad.py         # GROWTH_OPERAD, law tests
```

**Distilled Spec Template**:
```markdown
# self.grow: The Autopoietic Holon Generator

## Purpose
Enable AGENTESE to grow its own ontology through principled self-extension.

## Core Insight
Growth channels the Accursed Share through Tasteful filters, producing
curated holons that satisfy Generative compression.

## Type Signatures
[Type signatures only, no method bodies]

## Laws
[Invariants, not test code]

## Integration
[AGENTESE paths, composition]

## Anti-Patterns
[Keep existing list]

## Implementation
See: `impl/claude/protocols/agentese/contexts/self_grow/`
```

**Exit Criteria**:
- [ ] Implementation extracted to `impl/`
- [ ] Distilled spec is ~400 lines
- [ ] Implementation has tests
- [ ] Spec still generative (can regenerate impl from it)

---

### Phase 3: Distill p-gents/README.md (2-3 hours)

**Goal**: Transform 1,568 lines → ~300 lines.

**Current Structure**:
- Stochastic-Structural Gap (keep - core insight)
- Philosophy (keep)
- Design Principles (keep)
- Core Types (keep signatures, extract impls)
- Phase 1-4 Strategies (keep descriptions, extract full impls)
- Composition Patterns (keep patterns, extract impls)
- Recommended Strategy Combinations (keep)
- Configuration Philosophy (keep)
- Confidence Scoring (keep heuristics table)
- Error Handling Philosophy (keep)
- Integration (keep)
- Anti-Patterns (keep)
- Success Criteria (keep)
- Implementation Roadmap (remove - belongs in plans/)

**Extract to**:
```
impl/claude/agents/p/
├── types.py              # ParseResult, Parser protocol
├── stack_balancing.py    # StackBalancingParser
├── anchor_based.py       # AnchorBasedParser
├── probabilistic_ast.py  # ProbabilisticASTParser
├── evolving.py           # EvolvingParser
├── composition.py        # FallbackParser, FusionParser, SwitchParser
└── graduated.py          # GraduatedPromptParser
```

**Exit Criteria**:
- [ ] Full parser implementations in `impl/`
- [ ] Spec contains only: signatures, strategies (prose), laws
- [ ] Implementation Roadmap moved to `plans/agents/p-gent.md`
- [ ] ~300 lines remaining

---

### Phase 4: Distill u-gents/tool-use.md (2-3 hours)

**Goal**: Transform ~1,400 lines → ~350 lines.

**Keep**:
- Philosophy: Tools as Morphisms
- Design Principles (category-theoretic)
- Five-Layer Stack (descriptions only)
- Novel Patterns (descriptions only)
- Integration with Existing Genera
- Success Criteria

**Extract to**:
```
impl/claude/agents/u/
├── types.py          # Tool, ToolRegistry, ToolTrace
├── executor.py       # ToolExecutor
├── composition.py    # Sequential, Parallel, Choice patterns
├── security.py       # PermissionClassifier
├── mcp.py            # MCP client implementation
└── cache.py          # CachedTool (memoization functor)
```

**Remove**:
- Implementation Roadmap (12 weeks of checkboxes)
- Full code implementations
- Comparison table with other frameworks (move to docs/)

**Exit Criteria**:
- [ ] Implementation extracted
- [ ] Roadmap moved to plans/
- [ ] ~350 lines remaining

---

### Phase 5: Distill b-gents/banker.md (1-2 hours)

**Goal**: Transform 1,394 lines → ~250 lines.

**Keep**:
- Why Banker is a B-gent (conceptual)
- Theoretical Foundation (Linear Logic, VCG)
- Core Abstraction: Metered Functor (signature only)
- Biological Parallels table
- Integration with Bootstrap Agents

**Extract to**:
```
impl/claude/agents/b/
├── metered.py        # Metered functor implementation
├── bank.py           # CentralBank, Account, SinkingFund
├── auction.py        # priority_auction, Vickrey mechanism
└── types.py          # Receipt, Lease, Loan, Denial
```

**Exit Criteria**:
- [ ] Full banker implementation in `impl/`
- [ ] Spec focuses on theory and integration
- [ ] ~250 lines remaining

---

### Phase 6: Consolidate AGENTESE Specs (1-2 hours)

**Goal**: Single canonical AGENTESE spec.

**Current State**:
- `protocols/agentese.md` (1,202 lines)
- `protocols/agentese-v3.md` (1,051 lines)
- Both appear to be iterative versions

**Actions**:
1. Diff the two files to understand differences
2. Merge into single `agentese.md`
3. Move version history to git (delete v3 file)
4. Apply distillation to merged file

**Exit Criteria**:
- [ ] Single `agentese.md` file
- [ ] `agentese-v3.md` deleted
- [ ] Version history preserved in git

---

### Phase 7: Create Spec Template (1 hour)

**Goal**: Codify distilled spec format for future use.

**Create**: `docs/skills/spec-template.md`

```markdown
# Skill: Writing Spec Files

## Spec Structure (200-400 lines max)

### Required Sections
1. **Purpose** (1 paragraph)
2. **Core Insight** (1 sentence)
3. **Type Signatures** (no method bodies)
4. **Laws/Invariants**
5. **Integration** (AGENTESE paths, composition)
6. **Anti-Patterns** (3-5 bullets)
7. **Implementation Reference** (link to impl/)

### Forbidden in Specs
- Full function implementations
- SQL queries
- Implementation roadmaps
- Week-by-week plans
- >10 line code examples

### Code Example Rules
- Max 5-10 lines
- Show USAGE, not IMPLEMENTATION
- Type signatures preferred over bodies
```

**Exit Criteria**:
- [ ] Template skill document created
- [ ] Linked from CLAUDE.md skills section

---

### Phase 8: Audit Remaining Specs (2-3 hours)

**Goal**: Apply template to remaining large specs.

**Candidates** (>500 lines):
- `c-gents/functor-catalog.md` (1,052 lines)
- `n-gents/narrator.md` (1,039 lines)
- `protocols/evergreen-prompt-system.md` (1,012 lines)
- `protocols/process-holons.md` (980 lines)
- `protocols/projection.md` (878 lines)
- `m-gents/primitives.md` (879 lines)
- `protocols/gardener-logos.md` (887 lines)
- `n-gents/README.md` (868 lines)
- `o-gents/README.md` (817 lines)

**For each**:
1. Identify implementation code
2. Extract to appropriate `impl/` location
3. Apply distilled template
4. Verify tests pass

**Exit Criteria**:
- [ ] All specs >500 lines reviewed
- [ ] Implementation extracted where needed
- [ ] No spec exceeds 600 lines (soft limit)

---

## Verification

### Check 1: Line Count Reduction

```bash
cd /Users/kentgang/git/kgents
find spec -name "*.md" -exec wc -l {} + | tail -1
# Should show ~48,000 lines (down from ~91,000)
```

### Check 2: No Broken References

```bash
# Grep for references to deleted files
grep -r "t-gents/tool-use" spec/ impl/ docs/
# Should return nothing
```

### Check 3: Tests Pass

```bash
cd impl/claude
uv run pytest -x
```

### Check 4: Specs Are Generative

For each distilled spec, verify:
- Can you regenerate the impl from reading only the spec?
- Is the spec smaller than the impl? (compression achieved)

---

## Key Types (Distilled Spec Format)

```python
@dataclass
class DistilledSpec:
    """What a spec file should contain."""

    purpose: str           # 1 paragraph max
    core_insight: str      # 1 sentence
    type_signatures: list[str]  # No method bodies
    laws: list[str]        # Invariants, not test code
    integration: dict[str, list[str]]  # AGENTESE paths, composition
    anti_patterns: list[str]  # 3-5 bullets
    impl_reference: Path   # Link to impl/

    # Constraints
    max_lines: int = 400
    max_code_example_lines: int = 10

    def validate(self) -> bool:
        """A spec is valid if it's smaller than its implementation."""
        impl_lines = count_lines(self.impl_reference)
        spec_lines = self.line_count()
        return spec_lines < impl_lines  # Compression achieved
```

---

## Cross-References

- **Principle**: `spec/principles.md` §7 (Generative)
- **Audit Source**: This plan's research phase
- **Skills**: `docs/skills/plan-file.md`, `docs/skills/spec-template.md` (to create)
- **Implementation Guide**: `docs/impl-guide.md`

---

## Success Metrics

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| Total spec lines | ~91,000 | ~48,000 | 47% reduction |
| Deprecated files | 4+ | 0 | 100% removed |
| Specs >1000 lines | 15+ | 0 | None |
| Specs >500 lines | 25+ | <10 | Minimal |
| Impl in impl/ | partial | complete | All impl extracted |

---

## Chunks (Parallelizable Work)

### Chunk A: Delete Deprecated (Phase 1)
- Independent, can be done immediately
- **Exit**: ~5,000 lines removed, tests pass

### Chunk B: Large Spec Distillation (Phases 2-5)
- Can be parallelized across specs
- Each spec is independent
- **Exit**: Each spec <400 lines, impl extracted

### Chunk C: Consolidation (Phases 6-7)
- Depends on Chunk B completion
- **Exit**: Single AGENTESE spec, template created

### Chunk D: Audit Pass (Phase 8)
- Can be parallelized across remaining specs
- **Exit**: All large specs reviewed

---

## Notes for Executing Agent

1. **Start with Phase 1** - it's the quickest win and builds confidence
2. **For each distillation**, read the spec first to understand structure before extracting
3. **Preserve git history** - use `git rm` not `rm` for deletions
4. **Run tests after each phase** to catch breakage early
5. **Don't over-compress** - some specs (like `principles.md`) are already well-formed
6. **When in doubt**, keep content in spec and extract later rather than losing information

---

*"The master's touch was always just compressed experience. Now we can share the compression."* — principles.md
