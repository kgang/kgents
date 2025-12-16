# Evergreen Prompt System Implementation Plan

> *"The prompt that builds itself is the proof that it works."*

**Status:** Wave 5 COMPLETE - Wave 6 Ready
**Spec:** `spec/protocols/evergreen-prompt-system.md`
**Date:** 2025-12-16 (Updated: 2025-12-16)
**Guard:** `[phase=ACT][entropy=0.08][dogfood=true][final_wave=true]`
**Current Wave:** 6 (Living CLI + AGENTESE Paths)
**Last Checkpoint:** Wave 5 Multi-Source Fusion (2025-12-16)
**Continuation:** `plans/_continuations/evergreen-wave6-living-cli-continuation.md`

---

## ⚠️ Implementation Gap Analysis (2025-12-16)

This section documents the gaps between spec and implementation identified during review.

### Gap 1: Spec ↔ Impl Misalignment (HIGH PRIORITY)

| Spec Promise | Current Implementation | Status |
|--------------|----------------------|--------|
| `PromptM` monad with unit/bind/improve | No `monad.py`, no monadic pipeline | ❌ Missing |
| TextGRAD self-improvement loop | `textgrad/` directory doesn't exist | ❌ Missing |
| Rollback integrated in compiler | `rollback/` exists but not wired to CLI | ⚠️ Partial |
| Monadic laws tested in `test_monad.py` | File doesn't exist | ❌ Missing |

**Action Required**: Introduce `PromptM` wrapper with unit/bind/improve; wire rollback into compilation pipeline; add TextGRAD improver hook.

### Gap 2: Async Architecture (MEDIUM PRIORITY)

| Issue | Location | Impact |
|-------|----------|--------|
| `loop.run_until_complete()` in async context | `sections/forest.py:289-295` | Will throw/hang in CLI/server |
| `loop.run_until_complete()` in async context | `sections/context.py` (similar pattern) | Will throw/hang in CLI/server |
| No batch scheduling for soft sections | `soft_section.py` | Serial I/O per section |

**Action Required**: Make compiler async-first; convert `SectionCompiler.compile()` to async; run SoftSections concurrently via `gather`; provide sync shim only for legacy.

### Gap 3: Law/Validation Incomplete (MEDIUM PRIORITY)

| Law | Spec Reference | Implementation | Tested |
|-----|----------------|----------------|--------|
| Crystallize idempotence | Part I-B | `soft_section.py` has comment but no enforcement | ❌ |
| Monad left/right identity | Part I-B | Not implemented | ❌ |
| Monad associativity | Part I-B | Not implemented | ❌ |
| TextGRAD identity (empty feedback = identity) | Reformation continuation | Not implemented | ❌ |
| Rollback invertibility | Part VIII | `rollback/` exists but untested | ⚠️ |

**Action Required**: Add law checks to `_validate_laws()`; create `test_monad.py`, `test_laws.py`; expand tests for soft-section fusion and rollback invariants.

### Gap 4: Data Sources/Metrics (MEDIUM PRIORITY)

| Feature | Spec Promise | Implementation |
|---------|--------------|----------------|
| Git history analysis | `HabitEncoder` + git_analyzer | `git_analyzer.py` exists but minimal |
| Session log analysis | `SessionPatternAnalyzer` | Not implemented |
| Code pattern analysis | `CodePatternAnalyzer` | Not implemented |
| Metrics output | `metrics/evergreen/*.jsonl` | Not implemented |
| Provenance logging | Per-section source tracking | `source_paths` exists but no emission |

**Action Required**: Complete habit encoding pipeline; emit provenance/rigidity metrics to `metrics/`; add CLI flags for trace output.

### Gap 5: Plan/Documentation Drift (LOW PRIORITY)

| Document | Issue |
|----------|-------|
| This file | Previously claimed Wave 2 "current" |
| `plans/_epilogues/` | No Wave 2.5 or Wave 3 epilogue |
| `prompts/evergreen-builder-system-prompt.md` | References outdated wave status |

**Action Required**: This update addresses plan drift. Create Wave 3 epilogue when implementation stabilizes.

---

## Implementation Priority Order

Based on gap analysis:

1. **P0 - Safety Net**: Wire rollback registry to CLI (enables safe iteration)
2. **P1 - Async Fix**: Convert compiler to async-first (unblocks CLI/server usage)
3. **P2 - Monad Core**: Implement `PromptM` with monadic pipeline
4. **P3 - Law Validation**: Add comprehensive law tests
5. **P4 - Habit Encoder**: Complete git/session/code analysis
6. **P5 - TextGRAD**: Add self-improvement loop
7. **P6 - Metrics**: Emit provenance/metrics to `metrics/`

---

## Overview

This plan implements the Evergreen Prompt System across six waves. Each wave follows the N-Phase cycle (UNDERSTAND → ACT → REFLECT) with explicit dogfooding checkpoints—we use the system prompt to build itself.

**Key Principle**: After each wave, the system prompt is recompiled using what we built. Wave N+1 runs with the output of Wave N.

---

## The Dogfooding Protocol

```
┌────────────────────────────────────────────────────────────────────────────┐
│                        DOGFOODING PROTOCOL                                   │
│                                                                             │
│   Wave N ──────▶ Build Feature ──────▶ Recompile Prompt ──────▶ Wave N+1   │
│                        │                      │                             │
│                        │                      │                             │
│                        ▼                      ▼                             │
│              Test with old prompt    Test with new prompt                   │
│                        │                      │                             │
│                        └──────── Compare ─────┘                             │
│                                    │                                        │
│                                    ▼                                        │
│                            Learnings → Epilogue                             │
│                                                                             │
└────────────────────────────────────────────────────────────────────────────┘
```

After each wave:
1. **Recompile** CLAUDE.md using what was built
2. **Test** the new prompt on a representative task
3. **Compare** output quality vs previous prompt
4. **Record** learnings in epilogue
5. **Proceed** to next wave with new prompt

---

## Wave 1: Foundation (PROMPT_POLYNOMIAL + Basic Compiler) ✅ COMPLETE

### 1.1 UNDERSTAND Phase ✅

**Research Questions:**
- [x] How do existing N-Phase templates work? (`impl/claude/protocols/nphase/template.py`)
- [x] What's the PolyAgent pattern? (`impl/claude/agents/poly/`)
- [x] How does the current CLAUDE.md structure break down into sections?
- [x] What are the minimum viable section types?

**Files to Study:**
```
impl/claude/agents/poly/polynomial.py      # PolyAgent pattern
impl/claude/protocols/nphase/template.py   # N-Phase template
CLAUDE.md                                   # Current structure analysis
spec/protocols/evergreen-prompt-system.md  # Target spec
```

**Exit Criterion:** Can enumerate the section types and state machine for prompts. ✅

### 1.2 ACT Phase ✅

**Implementation Tasks:**
1. Create `impl/claude/protocols/prompt/__init__.py`
2. Create `impl/claude/protocols/prompt/polynomial.py`:
   - Define `PromptState` enum (STABLE, EVOLVING, VALIDATING, COMPILING)
   - Define `PromptInput` dataclass
   - Define `PromptOutput` dataclass
   - Define `PROMPT_POLYNOMIAL` PolyAgent
3. Create `impl/claude/protocols/prompt/compiler.py`:
   - `PromptCompiler` class with `compile()` method
   - Simple string concatenation for V1 (no Jinja yet)
4. Create `impl/claude/protocols/prompt/_tests/test_polynomial.py`:
   - Test state transitions
   - Test compilation produces valid markdown
5. Create `config/prompt-sections/` directory with basic YAML templates

**Minimal Section Set (V1):**
```yaml
# config/prompt-sections/
identity.yaml      # Project name + philosophy
principles.yaml    # Seven principles
commands.yaml      # Key commands reference
directories.yaml   # Directory structure
```

**Exit Criterion:** `PromptCompiler().compile()` produces valid CLAUDE.md-like output. ✅

### 1.3 REFLECT Phase ✅

**Dogfooding Checkpoint:**
- [x] Generate first compiled CLAUDE.md
- [x] Compare to hand-written CLAUDE.md (all 8 sections present)
- [x] Verify compilation determinism (same inputs → same output)
- [x] Record: Compiled prompt ~100 chars shorter, all sections present

**Epilogue Questions:**
- What's missing from the minimal section set?
- Did the polynomial state machine feel right?
- What surprised us?

---

## Wave 2: Section Compilers (Identity, Principles, Systems, Skills) ✅ COMPLETE

### 2.1 UNDERSTAND Phase ✅

**Research Questions:**
- [x] What context does each section need?
- [x] How do sections depend on each other?
- [x] What's the interface for a SectionCompiler?
- [x] How does `docs/systems-reference.md` map to a section?

**Files to Study:**
```
docs/systems-reference.md       # Systems section source
spec/principles.md              # Principles section source
docs/skills/*.md                # Skills section source
CLAUDE.md                       # Current structure for comparison
```

**Exit Criterion:** Section compiler interface defined, dependencies mapped. ✅

### 2.2 ACT Phase ✅

**Implementation Tasks:**
1. Create `impl/claude/protocols/prompt/section_base.py`:
   - `SectionCompiler` protocol/ABC
   - `Section` dataclass (name, content, token_cost, required, phases)
2. Create `impl/claude/protocols/prompt/sections/`:
   - `identity.py` - Static identity section
   - `principles.py` - Reads from `spec/principles.md`
   - `systems.py` - Reads from `docs/systems-reference.md`
   - `skills.py` - Aggregates from `docs/skills/*.md`
3. Update `compiler.py` to use section compilers
4. Create tests for each section compiler
5. Add section ordering logic (identity → principles → systems → skills)

**Section Compiler Interface:**
```python
class SectionCompiler(Protocol):
    name: str
    required: bool
    phases: frozenset[NPhase]

    async def compile(self, context: CompilationContext) -> Section:
        """Compile section from sources."""
        ...

    def estimate_tokens(self) -> int:
        """Estimate token cost."""
        ...
```

**Exit Criterion:** All four section compilers work independently and compose. ✅

### 2.3 REFLECT Phase ✅

**Dogfooding Checkpoint:**
- [x] Recompile CLAUDE.md with new section compilers
- [x] Compare: Is it closer to hand-written CLAUDE.md?
- [x] Test: Run a medium task (e.g., "Implement a new CLI command")
- [x] Record: Quality delta from Wave 1

**Wave 2.5 Content Preservation (2025-12-16):**
- Fixed systems table truncation with graceful fallback
- Added CURATED_DESCRIPTIONS for skills to preserve rich descriptions
- Fixed typography (em-dashes —, arrows →)
- 67 tests passing

**Epilogue:** See `plans/_epilogues/2025-12-16-evergreen-wave2-complete.md`

---

## Wave 3: Soft Section Protocol + Dynamic Sections 🔄 IN PROGRESS (REFORMULATED)

> **Reformation Note (2025-12-16)**: Wave 3 was reformulated as the "Prompt Monad Architecture" based on DSPy, SPEAR, Meta-Prompting, and TextGRAD research. See `plans/_continuations/evergreen-wave3-reformation-continuation.md` for full details.

### 3.1 UNDERSTAND Phase ✅

**Research Questions:**
- [x] How does `_forest.md` parsing work? (`plans/_forest.md`)
- [x] How does the rigidity spectrum work? (TextGRAD "learning rate")
- [x] What's the SoftSection → Section crystallization pattern?
- [x] What category laws must hold? (crystallize idempotence, monad laws)

**Key Files Built:**
```
impl/claude/protocols/prompt/soft_section.py     # ✅ SoftSection with rigidity
impl/claude/protocols/prompt/sections/forest.py  # ✅ Forest with SoftSection
impl/claude/protocols/prompt/sections/context.py # ✅ Context with git status
impl/claude/protocols/prompt/sources/            # ✅ FileSource, GitSource, LLMSource
impl/claude/protocols/prompt/rollback/           # ⚠️ Exists but not wired
impl/claude/protocols/prompt/habits/             # ⚠️ Stub implementations
```

**Exit Criterion:** SoftSection crystallization with reasoning traces. ⚠️ Partial

### 3.2 ACT Phase 🔄 IN PROGRESS

**Reformation Tasks (ordered by priority from gap analysis):**

1. **P0 - Wire Rollback to CLI** ⏳
   - Add `--checkpoint` flag to compile command
   - Add `--rollback <id>` subcommand
   - Add `--history` to show evolution timeline

2. **P1 - Fix Async Architecture** ⏳
   - Convert `SectionCompiler.compile()` to async
   - Replace `loop.run_until_complete()` with proper async handling
   - Add event-loop detection guard
   - Run SoftSections concurrently via `asyncio.gather()`
   - Provide sync shim for legacy CLI

3. **P2 - Implement PromptM Monad** ⏳
   - Create `monad.py` with `PromptM[A]` dataclass
   - Implement `unit()`, `bind()`, `improve()`
   - Track reasoning traces through monadic pipeline
   - Add checkpoint provenance per section

4. **P3 - Law Validation Tests** ⏳
   - Create `_tests/test_monad.py` for monadic laws
   - Add crystallize idempotence test
   - Add TextGRAD identity test (empty feedback)
   - Add rollback invertibility test
   - Expand `_validate_laws()` in compiler

**Files to Create:**
```python
impl/claude/protocols/prompt/monad.py           # PromptM monad
impl/claude/protocols/prompt/_tests/test_monad.py  # Monadic law tests
impl/claude/protocols/prompt/_tests/test_laws.py   # Category law tests
```

**Exit Criterion:** All priority tasks complete, monadic pipeline functional.

### 3.3 REFLECT Phase ⏳

**Dogfooding Checkpoint:**
- [ ] Recompile CLAUDE.md with SoftSection pipeline
- [ ] Verify rollback works (create checkpoint, modify, rollback)
- [ ] Run `--show-reasoning` to see traces
- [ ] Test async compilation in server context
- [ ] Verify all category laws pass

**Success Criteria:**
- [ ] No `loop.run_until_complete()` in production paths
- [ ] Rollback registry has at least one checkpoint after compile
- [ ] Monadic laws verified in tests
- [ ] Reasoning traces appear in compiled output (when requested)

---

## Wave 4: Habit Encoder + TextGRAD (REFORMULATED)

> **Reformation Note**: Wave 4 was reformulated to focus on habit learning and TextGRAD self-improvement rather than the original evolution protocol (which was partly absorbed into Wave 3's rollback system).

### 4.1 UNDERSTAND Phase ⏳

**Research Questions:**
- [ ] Where are Claude Code session logs stored?
- [ ] What git patterns indicate developer preferences? (commit style, file organization)
- [ ] How does TextGRAD parse natural language feedback into gradient?
- [ ] What's the cost/latency tradeoff for LLM-based semantic similarity?

**Files to Study:**
```
impl/claude/protocols/prompt/habits/git_analyzer.py  # Current stub
impl/claude/protocols/prompt/habits/policy.py        # PolicyVector
spec/heritage.md Part II                              # TextGRAD formalization
```

**Exit Criterion:** Understand data sources and TextGRAD algorithm.

### 4.2 ACT Phase ⏳

**Implementation Tasks:**
1. **Complete HabitEncoder Pipeline:**
   - Enhance `git_analyzer.py` (commit patterns, file organization, code style)
   - Create `session_analyzer.py` (interaction patterns from logs)
   - Create `code_analyzer.py` (AST-based style detection)
   - Wire analyzers into `PolicyVector`

2. **Implement TextGRADImprover:**
   - Create `textgrad/improver.py`
   - Create `textgrad/feedback_parser.py`
   - Create `textgrad/gradient.py` (textual gradient computation)
   - Wire to `PromptM.improve()` method

3. **Add HabitsSection:**
   - Create `sections/habits.py`
   - Rigidity ~0.1 (highly adaptive)
   - Sources: PolicyVector, session history

**Files to Create:**
```
impl/claude/protocols/prompt/habits/session_analyzer.py
impl/claude/protocols/prompt/habits/code_analyzer.py
impl/claude/protocols/prompt/textgrad/
impl/claude/protocols/prompt/textgrad/improver.py
impl/claude/protocols/prompt/textgrad/feedback_parser.py
impl/claude/protocols/prompt/textgrad/gradient.py
impl/claude/protocols/prompt/sections/habits.py
impl/claude/protocols/prompt/_tests/test_textgrad.py
```

**Exit Criterion:** Can apply feedback via `PromptM.improve()`.

### 4.3 REFLECT Phase ⏳

**Dogfooding Checkpoint:**
- [ ] Run habit encoder on actual git history
- [ ] Provide feedback via CLI: `/prompt --feedback "more concise"`
- [ ] Verify TextGRAD modifies targeted sections
- [ ] Check improvement is checkpointed for rollback

**Epilogue Questions:**
- Does habit encoding capture real preferences?
- Is TextGRAD improvement coherent?
- What feedback types work best?

---

## Wave 5: Multi-Source Fusion + Metrics (REFORMULATED)

> **Reformation Note**: Wave 5 was reformulated to focus on semantic fusion and metrics emission. AGENTESE paths integration is deferred to Wave 6 as part of the Living CLI.

### 5.1 UNDERSTAND Phase ⏳

**Research Questions:**
- [ ] How to compute semantic similarity between sections? (embeddings vs LLM-as-judge)
- [ ] What conflict types arise in multi-source fusion?
- [ ] What metrics format is useful? (JSONL for observability)
- [ ] How to balance fusion cost vs compilation speed?

**Files to Study:**
```
impl/claude/protocols/prompt/soft_section.py       # MergeStrategy.SEMANTIC_FUSION stub
impl/claude/protocols/prompt/sources/              # Current source implementations
metrics/                                            # Target directory for output
```

**Exit Criterion:** Understand fusion algorithm, design metrics schema.

### 5.2 ACT Phase ⏳

**Implementation Tasks:**
1. **Semantic Fusion Implementation:**
   - Create `fusion/similarity.py` (embedding-based or LLM-as-judge)
   - Create `fusion/conflict.py` (detect contradictions)
   - Create `fusion/resolution.py` (policy-based resolution)
   - Create `fusion/fusioner.py` (main PromptFusion class)
   - Wire to `SoftSection._merge()` for `SEMANTIC_FUSION` strategy

2. **Metrics Emission:**
   - Create `metrics/schema.py` (define JSONL format)
   - Create `metrics/emitter.py` (write metrics during compilation)
   - Track per-section: source, rigidity, provenance, reasoning trace hash
   - Add `--emit-metrics` CLI flag

3. **Integration:**
   - Wire fusion into compilation pipeline
   - Add metrics emission to `compile()` method

**Files to Create:**
```
impl/claude/protocols/prompt/fusion/
impl/claude/protocols/prompt/fusion/similarity.py
impl/claude/protocols/prompt/fusion/conflict.py
impl/claude/protocols/prompt/fusion/resolution.py
impl/claude/protocols/prompt/fusion/fusioner.py
impl/claude/protocols/prompt/metrics/
impl/claude/protocols/prompt/metrics/schema.py
impl/claude/protocols/prompt/metrics/emitter.py
impl/claude/protocols/prompt/_tests/test_fusion.py
```

**Exit Criterion:** Semantic fusion works, metrics emitted to `metrics/evergreen/`.

### 5.3 REFLECT Phase ⏳

**Dogfooding Checkpoint:**
- [ ] Test fusion with conflicting file + inferred sections
- [ ] Verify metrics appear in `metrics/evergreen/compile_YYYY-MM-DD.jsonl`
- [ ] Check provenance tracking in compiled output
- [ ] Measure compilation speed impact

**Epilogue Questions:**
- Is semantic similarity accurate enough?
- Are metrics useful for debugging?
- What's the performance impact of fusion?

---

## Wave 6: Living CLI + AGENTESE Paths (REFORMULATED)

> **Reformation Note**: Wave 6 combines the original CLI integration with AGENTESE paths (deferred from Wave 5) into a unified "Living CLI" experience.

### 6.1 UNDERSTAND Phase ⏳

**Research Questions:**
- [ ] How do slash commands work? (`.claude/commands/`)
- [ ] How do CLI shortcuts work? (`protocols/cli/shortcuts.py`)
- [ ] How do AGENTESE contexts register? (`protocols/agentese/contexts/`)
- [ ] What's the best UX for showing reasoning traces?

**Files to Study:**
```
impl/claude/protocols/cli/handlers/           # Handler patterns
impl/claude/protocols/agentese/contexts/      # AGENTESE registration
docs/skills/cli-command.md                    # CLI command skill
```

**Exit Criterion:** Understand CLI patterns and AGENTESE registration.

### 6.2 ACT Phase ⏳

**Implementation Tasks:**
1. **Core CLI Commands:**
   - `/prompt` — Show current compiled prompt
   - `/prompt --show-reasoning` — Show with reasoning traces
   - `/prompt --show-habits` — Show habit influence
   - `/prompt --feedback '<text>'` — TextGRAD improvement
   - `/prompt --history` — Evolution timeline
   - `/prompt --rollback <id>` — Restore checkpoint
   - `/prompt --preview` — Preview recompilation changes
   - `/prompt --auto-improve` — Self-improve with safety
   - `/prompt --diff <id1> <id2>` — Compare checkpoints

2. **AGENTESE Paths Registration:**
   - Create `protocols/agentese/contexts/prompt.py`
   - Register `concept.prompt.*` paths:
     - `manifest` → Current CLAUDE.md
     - `evolve` → Propose evolution (via TextGRAD)
     - `validate` → Run law checks
     - `compile` → Force recompilation
     - `history` → Version history
     - `rollback` → Restore checkpoint
   - Add `concept.prompt.section.*` paths

3. **Rich CLI Output:**
   - Section-by-section display with fold/unfold
   - Reasoning trace highlighting
   - History timeline visualization
   - Diff display with syntax highlighting

**Files to Create:**
```
impl/claude/protocols/cli/handlers/prompt.py
impl/claude/protocols/agentese/contexts/prompt.py
.claude/commands/prompt.md
.claude/commands/prompt-history.md
.claude/commands/prompt-rollback.md
impl/claude/protocols/prompt/_tests/test_cli_prompt.py
impl/claude/protocols/prompt/_tests/test_agentese_paths.py
```

**Exit Criterion:** All CLI commands work, AGENTESE paths functional.

### 6.3 REFLECT Phase ⏳

**Final Dogfooding Checkpoint:**
- [ ] Start fresh session with compiled prompt
- [ ] Use `/prompt --show-reasoning` to see traces
- [ ] Provide feedback: `/prompt --feedback "be more concise"`
- [ ] Verify improvement was checkpointed
- [ ] Rollback: `/prompt --rollback <id>`
- [ ] Use AGENTESE: `kg concept.prompt.manifest`
- [ ] Complete a real development task with compiled prompt

**Epilogue Questions:**
- Does the system feel self-sustaining?
- Is the reasoning trace UX useful?
- What commands are missing?
- Can you improve the Evergreen System using the Evergreen System?

---

## Success Criteria (All Waves)

### Quantitative
- [ ] Compilation time < 5s
- [ ] All category laws pass (100%) — monadic laws, operad laws, crystallize idempotence
- [ ] 9+ CLI command variants working (`/prompt` + flags)
- [ ] 8+ AGENTESE paths registered (`concept.prompt.*`)
- [ ] Test coverage > 80% for prompt module
- [ ] No `loop.run_until_complete()` in production paths
- [ ] Metrics emitted to `metrics/evergreen/` on each compile

### Qualitative
- [ ] Compiled prompt is as good or better than hand-written
- [ ] Reasoning traces are useful (not noise)
- [ ] Rollback enables fearless improvement
- [ ] TextGRAD feedback produces coherent changes
- [ ] Dogfooding produced real improvements
- [ ] System is self-documenting

### The Ultimate Test

Can you use the Evergreen Prompt System to improve the Evergreen Prompt System?

```
/prompt --feedback "be more concise in the systems section"
# → TextGRAD applies improvement
# → Checkpoint created
# → Test with new prompt
# → If worse: /prompt --rollback <id>
```

If yes: Success.
If no: More waves needed.

---

## Timeline and Dependencies

```
Wave 1 ─────▶ Wave 2 ─────▶ Wave 2.5 ─────▶ Wave 3 ─────▶ Wave 4 ─────▶ Wave 5 ─────▶ Wave 6
   │            │              │               │            │             │             │
   ▼            ▼              ▼               ▼            ▼             ▼             ▼
Foundation  Sections    Content Pres.   Soft Sections  Habits+TextGRAD  Fusion+Metrics  Living CLI
   ✅          ✅             ✅              ✅             ✅             ✅          🔄 NEXT
```

**Wave 3 Dependency Order (from gap analysis):**
```
P0: Rollback CLI ──▶ P1: Async Fix ──▶ P2: PromptM Monad ──▶ P3: Law Tests
                                                                    │
                                                                    ▼
                                                              Wave 4 Ready
```

**No wave starts until previous wave's dogfood checkpoint passes.**

---

## Files Created by End of All Waves

```
impl/claude/protocols/prompt/
├── __init__.py                    # Wave 1
├── polynomial.py                  # Wave 1
├── compiler.py                    # Wave 1, async in Wave 3
├── section_base.py                # Wave 2
├── cli.py                         # Wave 1, extended Wave 6
├── monad.py                       # Wave 3 - PromptM monad
├── soft_section.py                # Wave 3 - Rigidity spectrum
│
├── sources/                       # Wave 3 - Section sources
│   ├── __init__.py
│   ├── base.py                    # ✅ Built
│   ├── file_source.py             # ✅ Built
│   ├── git_source.py              # ✅ Built
│   └── llm_source.py              # ✅ Built
│
├── rollback/                      # Wave 3 - Checkpoints
│   ├── __init__.py                # ✅ Built
│   ├── checkpoint.py              # ✅ Built
│   ├── registry.py                # ✅ Built (needs CLI wiring)
│   └── storage.py                 # ✅ Built
│
├── habits/                        # Wave 4 - Habit encoding
│   ├── __init__.py                # ✅ Built (stub)
│   ├── git_analyzer.py            # ✅ Built (minimal)
│   ├── session_analyzer.py        # Wave 4
│   ├── code_analyzer.py           # Wave 4
│   └── policy.py                  # ✅ Built (stub)
│
├── textgrad/                      # Wave 4 - Self-improvement
│   ├── __init__.py
│   ├── improver.py                # Wave 4
│   ├── feedback_parser.py         # Wave 4
│   └── gradient.py                # Wave 4
│
├── fusion/                        # Wave 5 - Multi-source fusion
│   ├── __init__.py
│   ├── fusioner.py                # Wave 5
│   ├── similarity.py              # Wave 5
│   ├── conflict.py                # Wave 5
│   └── resolution.py              # Wave 5
│
├── metrics/                       # Wave 5 - Observability
│   ├── __init__.py
│   ├── schema.py                  # Wave 5
│   └── emitter.py                 # Wave 5
│
├── sections/                      # Section compilers
│   ├── __init__.py                # ✅ Built
│   ├── identity.py                # ✅ Wave 2 (rigidity=1.0)
│   ├── principles.py              # ✅ Wave 2 (rigidity=0.8)
│   ├── agentese.py                # ✅ Wave 2 (rigidity=1.0)
│   ├── systems.py                 # ✅ Wave 2 (rigidity=0.7)
│   ├── directories.py             # ✅ Wave 2 (rigidity=1.0)
│   ├── skills.py                  # ✅ Wave 2 (rigidity=0.6)
│   ├── commands.py                # ✅ Wave 2 (rigidity=1.0)
│   ├── forest.py                  # ✅ Wave 3 (rigidity=0.4)
│   ├── context.py                 # ✅ Wave 3 (rigidity=0.3)
│   ├── memory.py                  # Wave 3 (rigidity=0.2)
│   └── habits.py                  # Wave 4 (rigidity=0.1)
│
└── _tests/
    ├── test_polynomial.py         # ✅ Wave 1 (27 tests)
    ├── test_compiler.py           # ✅ Wave 1 (14 tests)
    ├── test_dynamic_sections.py   # ✅ Wave 2 (26 tests)
    ├── test_soft_section.py       # ✅ Wave 3 (built)
    ├── test_rollback.py           # ✅ Wave 3 (built)
    ├── test_habits.py             # ✅ Wave 3 (built)
    ├── test_monad.py              # Wave 3 - Monadic laws
    ├── test_laws.py               # Wave 3 - Category laws
    ├── test_textgrad.py           # Wave 4
    ├── test_fusion.py             # Wave 5
    ├── test_cli_prompt.py         # Wave 6
    └── test_agentese_paths.py     # Wave 6

impl/claude/protocols/agentese/contexts/
└── prompt.py                      # Wave 6 - AGENTESE paths

impl/claude/protocols/cli/handlers/
└── prompt.py                      # Wave 6 - CLI handler

.claude/commands/
├── prompt.md                      # Wave 6
├── prompt-history.md              # Wave 6
└── prompt-rollback.md             # Wave 6

metrics/evergreen/                 # Wave 5 - Metrics output
└── compile_YYYY-MM-DD.jsonl       # Per-compilation metrics
```

---

*"Build the thing that builds the thing. Then let the thing build itself."*

*Last updated: 2025-12-16*
