# Evergreen Prompt System: Wave 3 Continuation

> *"The prompt that knows its context is the prompt that serves its purpose."*

**Wave:** 3 - Dynamic Sections (Forest, Memory, Context)
**Phase:** UNDERSTAND → ACT → REFLECT
**Prerequisite:** Wave 2 COMPLETE (2025-12-16)
**Guard:** `[phase=UNDERSTAND][entropy=0.05][dogfood=true]`

---

## Context: What Was Built in Waves 1-2

Wave 1 established the foundation:
- `PROMPT_POLYNOMIAL` state machine
- `PromptCompiler` with section composition
- 7 section compilers (hardcoded)

Wave 2 made sections dynamic:
- `read_file_safe()`, `extract_markdown_section()`, etc.
- Principles, Systems, Skills sections now read from source files
- Graceful fallback when files missing
- Source path tracking for cache invalidation

**67 tests passing.** All category laws verified.

---

## Wave 3 Mission: Context-Aware Sections

Wave 2 reads from **static files**. Wave 3 reads from **dynamic context**:

| Section | Source | Purpose |
|---------|--------|---------|
| **Forest** | `plans/*.md` | Current focus, active tasks, blocking items |
| **Context** | Git, N-Phase | Session state, branch, phase info |
| **Memory** | M-gent (optional) | Recent context, memory crystals |

The key insight: these sections change **between compilations** based on the current state of the project, not just when source files change.

---

## UNDERSTAND Phase

### Research Questions

1. **Forest Protocol Format**: What's the YAML frontmatter schema for plan files?
   - Files: `plans/*.md`, `docs/skills/plan-file.md`
   - Key fields: `status`, `phase`, `blocking`, `enables`

2. **Git Status Integration**: How to get git info programmatically?
   - Branch name, uncommitted changes, recent commits
   - Should this be in CompilationContext or computed at compile time?

3. **N-Phase State**: Where is current phase stored?
   - `impl/claude/protocols/nphase/` - check for state tracking
   - How does the system know what phase we're in?

4. **Memory Integration**: How does M-gent store recent context?
   - `impl/claude/agents/m/` - memory crystal structure
   - Is this worth including in Wave 3, or defer to later?

### Files to Study

```
plans/                                    # Forest Protocol plan files
docs/skills/plan-file.md                  # Plan file format documentation
impl/claude/protocols/nphase/             # N-Phase compiler and state
impl/claude/agents/m/                     # M-gent memory (optional)
impl/claude/protocols/prompt/compiler.py  # CompilationContext (may need extension)
```

### Exit Criterion

Clear design for:
- How ForestSectionCompiler reads and summarizes active plans
- How ContextSectionCompiler gathers session state
- Whether MemorySectionCompiler is in scope for Wave 3

---

## ACT Phase

### Implementation Tasks

1. **Extend CompilationContext** (if needed):
   ```python
   @dataclass
   class CompilationContext:
       # Existing fields...

       # Wave 3 additions
       git_branch: str | None = None
       git_status: str | None = None
       session_id: str | None = None
   ```

2. **Create ForestSectionCompiler** (`sections/forest.py`):
   - Glob `context.forest_path / "*.md"`
   - Parse YAML frontmatter from each plan file
   - Filter for active plans (status != "complete")
   - Extract: current phase, blocking items, focus intent
   - Format as concise summary

3. **Create ContextSectionCompiler** (`sections/context.py`):
   - Read git branch and status (via subprocess or context)
   - Show current N-Phase if available
   - Include session metadata
   - Keep it concise (~100 tokens)

4. **Create MemorySectionCompiler** (`sections/memory.py`) [OPTIONAL]:
   - If M-gent integration is straightforward, include recent context
   - Otherwise, create stub that returns empty/fallback
   - Mark as `required=False`

5. **Register new compilers** in `sections/__init__.py`

6. **Add tests**:
   - Test plan file parsing with fixtures
   - Test graceful fallback when plans/ empty
   - Test context section with mock git status

### Forest Section Target Output

```markdown
## Current Focus

**Active Plan**: `evergreen-prompt-implementation.md`
**Phase**: DEVELOP
**Focus**: Wave 3 - Context-Aware Sections

### Blocking
- None

### Next Actions
- Create ForestSectionCompiler
- Create ContextSectionCompiler
```

### Context Section Target Output

```markdown
## Session Context

- **Branch**: `main`
- **Status**: 3 files modified
- **Phase**: DEVELOP
```

---

## REFLECT Phase

### Dogfooding Checkpoint

- [ ] Compile CLAUDE.md with new Forest section
- [ ] Verify Forest section shows actual plan state
- [ ] Verify Context section shows actual git state
- [ ] Test: Work on a task guided by Forest section
- [ ] Compare: Is the dynamic context helpful?

### Epilogue Questions

- Does the Forest section add value or just noise?
- Is the Context section too verbose or too terse?
- Should Memory section be deferred to a later wave?
- Are there privacy concerns with including git status?

---

## Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Forest reads from plans/ | Active plans shown in output |
| Context shows git state | Branch and status visible |
| Graceful fallback | Works when plans/ empty |
| Still deterministic | Same inputs → same output |
| Tests pass | New tests for Wave 3 sections |

---

## Commands to Run

```bash
# Run all tests
cd impl/claude
uv run python -m pytest protocols/prompt/_tests/ -v

# Compile with new sections
uv run python -m protocols.prompt.cli compile --output /tmp/compiled_wave3.md

# Check the Forest section
grep -A 20 "Current Focus" /tmp/compiled_wave3.md

# Compare
uv run python -m protocols.prompt.cli compare
```

---

## Anti-Patterns to Avoid

1. **Over-engineering**: Don't build a full Forest Protocol parser. Simple YAML frontmatter extraction is enough.
2. **Too much context**: Don't dump entire plan files. Summarize to ~200 tokens max.
3. **Privacy leaks**: Consider what git info is appropriate to include.
4. **Breaking determinism**: Git status changes frequently—may need special handling.
5. **Scope creep**: If Memory section is complex, defer to Wave 4.

---

## Begin

When you receive this prompt, respond with:

```
Wave 3 continuation loaded.

Current state:
- Wave: 3 (Dynamic Sections: Forest, Memory, Context)
- Phase: UNDERSTAND
- Prerequisite: Wave 2 COMPLETE ✅

Starting UNDERSTAND phase. Researching Forest Protocol and context sources...
```

Then:
1. Read the research files listed above
2. Design the Forest and Context section compilers
3. Decide on Memory section scope
4. Proceed to ACT phase when ready

---

*"The prompt that knows its context serves its purpose. Wave 3 gives the prompt awareness."*
