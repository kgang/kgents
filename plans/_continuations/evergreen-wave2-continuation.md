# Evergreen Prompt System: Wave 2 Continuation

> *"The prompt that reads its sources is the prompt that stays current."*

**Wave:** 2 - Dynamic Section Compilers
**Phase:** UNDERSTAND → ACT → REFLECT
**Prerequisite:** Wave 1 COMPLETE (2025-12-16)
**Guard:** `[phase=UNDERSTAND][entropy=0.05][dogfood=true]`

---

## Context: What Was Built in Wave 1

Wave 1 established the foundation:

```
impl/claude/protocols/prompt/
├── polynomial.py      # PROMPT_POLYNOMIAL state machine
├── section_base.py    # Section dataclass, SectionCompiler protocol
├── compiler.py        # PromptCompiler with compile pipeline
├── cli.py             # Simple CLI for dogfooding
└── sections/          # 7 section compilers (hardcoded content)
```

**Key Achievement:** `PromptCompiler().compile()` produces valid CLAUDE.md with all 8 sections.

**Current Limitation:** Section content is hardcoded in Python. Wave 2 makes it dynamic.

---

## Wave 2 Mission: Dynamic Section Compilers

Transform section compilers from hardcoded strings to **dynamic readers** that:

1. **Read actual source files** (principles.md, systems-reference.md, skills/*.md)
2. **Parse and extract** relevant content
3. **Render phase-aware** output based on context
4. **Track dependencies** for cache invalidation

---

## UNDERSTAND Phase

### Research Questions

- [ ] How should `PrinciplesSectionCompiler` read `spec/principles.md`?
  - Full content? Summary extraction? Section parsing?
- [ ] How should `SystemsSectionCompiler` read `docs/systems-reference.md`?
  - What format is that file in?
- [ ] How should `SkillsSectionCompiler` aggregate from `docs/skills/*.md`?
  - List file names? Extract descriptions?
- [ ] What's the interface for a dynamic section compiler?
- [ ] How do we handle missing source files gracefully?

### Files to Study

```
spec/principles.md                    # Full principles (1100+ lines)
docs/systems-reference.md             # Systems inventory
docs/skills/*.md                      # Skill files to aggregate
impl/claude/protocols/prompt/sections/principles.py  # Current hardcoded version
```

### Exit Criterion

Clear interface for dynamic section compilers that:
- Accept file paths from CompilationContext
- Read and parse source files
- Handle missing files gracefully
- Return Section with source_paths for cache invalidation

---

## ACT Phase

### Implementation Tasks

1. **Update `section_base.py`**:
   - Add `read_markdown_file(path: Path) -> str` utility
   - Add `extract_section(content: str, heading: str) -> str` utility
   - Add `SourceFile` dataclass for tracking sources

2. **Update `PrinciplesSectionCompiler`**:
   - Read from `context.spec_path / "principles.md"`
   - Extract summary (first 7 principles + categorical foundation)
   - Fall back to hardcoded if file missing

3. **Update `SystemsSectionCompiler`**:
   - Read from `context.docs_path / "systems-reference.md"`
   - Extract systems table
   - Fall back to hardcoded if file missing

4. **Update `SkillsSectionCompiler`**:
   - Glob `context.docs_path / "skills" / "*.md"`
   - Extract skill name and first line description
   - Generate skills table dynamically

5. **Update `IdentitySectionCompiler`**:
   - Read taxonomy table from `CLAUDE.md` or define statically
   - Consider reading from a config file

6. **Add phase-aware rendering** (optional for Wave 2):
   - If `context.current_phase == NPhase.DEVELOP`, include different hints
   - Use simple conditionals, not full Jinja2 yet

7. **Update tests**:
   - Test dynamic reading with fixture files
   - Test graceful fallback when files missing
   - Test source_paths are populated correctly

### Section Compiler Interface (Target)

```python
class DynamicSectionCompiler(Protocol):
    """Enhanced section compiler that reads from sources."""

    @property
    def name(self) -> str: ...

    @property
    def source_patterns(self) -> list[str]:
        """Glob patterns for source files."""
        ...

    def compile(self, context: CompilationContext) -> Section:
        """Compile section, reading from context paths."""
        ...

    def compile_fallback(self, context: CompilationContext) -> Section:
        """Compile with hardcoded content if sources unavailable."""
        ...
```

### Exit Criterion

- `PromptCompiler().compile()` reads from actual source files
- Missing files trigger graceful fallback
- `section.source_paths` populated for cache invalidation
- Tests pass for both dynamic and fallback modes

---

## REFLECT Phase

### Dogfooding Checkpoint

- [ ] Recompile CLAUDE.md with dynamic section compilers
- [ ] Verify content matches actual source files
- [ ] Modify a source file, recompile, verify change propagates
- [ ] Test: Run a medium task (e.g., "Implement a new CLI command")
- [ ] Compare: Quality delta from Wave 1

### Epilogue Questions

- Are sections too long? Too short?
- Is source file parsing robust enough?
- What edge cases need handling?
- Is the fallback mechanism appropriate?

---

## Success Criteria

| Criterion | Verification |
|-----------|--------------|
| Principles read from spec/principles.md | Content includes actual principle text |
| Systems read from docs/systems-reference.md | Table matches source file |
| Skills aggregated from docs/skills/*.md | All skill files included |
| Graceful fallback | Tests pass with missing files |
| Source tracking | source_paths populated |
| Compilation still deterministic | Same inputs → same output |

---

## Commands to Run

```bash
# Run Wave 1 tests (should still pass)
cd impl/claude
uv run python -m pytest protocols/prompt/_tests/ -v

# Generate compiled CLAUDE.md
uv run python -m protocols.prompt.cli compile --output /tmp/compiled_claude.md

# Compare to hand-written
uv run python -m protocols.prompt.cli compare

# Check if a source file change propagates
echo "# Test change" >> /tmp/test_principles.md
# (After implementing dynamic reading)
```

---

## Anti-Patterns to Avoid

1. **Over-parsing**: Don't try to parse complex markdown structures. Simple section extraction is enough.
2. **Ignoring errors**: Always log when falling back to hardcoded content.
3. **Breaking determinism**: Dynamic reading must still be deterministic for same inputs.
4. **Forgetting tests**: Every new dynamic reader needs fixture-based tests.

---

## Begin

When you receive this prompt, respond with:

```
Wave 2 continuation loaded.

Current state:
- Wave: 2 (Dynamic Section Compilers)
- Phase: UNDERSTAND
- Prerequisite: Wave 1 COMPLETE ✅

Starting UNDERSTAND phase. Reading source files to design dynamic compilation...
```

Then:
1. Read the research files listed above
2. Design the dynamic section compiler interface
3. Proceed to ACT phase when ready

---

*"The prompt that reads its sources stays evergreen. Wave 2 teaches the prompt to read."*
