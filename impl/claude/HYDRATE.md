# HYDRATE: Evergreen Prompt System Wave 4

**Status**: Wave 3 COMPLETE (Core Infrastructure) | **Date**: 2025-12-16

---

## Just Completed: Wave 3 ("Core Infrastructure")

Reformation architecture implementation with four priority items:

### P0-P3 Completed

| Priority | Task | Implementation |
|----------|------|----------------|
| P0 | Wire rollback to CLI | `history`, `rollback`, `diff` commands + checkpoint during compile |
| P1 | Fix async architecture | `run_sync()` utility for safe sync→async bridging |
| P2 | PromptM monad | Full monad with unit/bind/map + provenance + reasoning traces |
| P3 | Monad law tests | 31 tests verifying all three monadic laws |

### Files Created/Modified

```
impl/claude/protocols/prompt/
├── monad.py           # NEW: PromptM[A] with full monadic operations
├── cli.py             # UPDATED: Added history, rollback, diff commands
├── section_base.py    # UPDATED: Added run_sync() utility
├── rollback/__init__.py # UPDATED: Export get_default_registry
├── sections/forest.py  # UPDATED: Use run_sync()
├── sections/context.py # UPDATED: Use run_sync()
└── _tests/
    ├── test_cli.py     # NEW: 11 CLI tests
    └── test_monad.py   # NEW: 31 monad law tests
```

### Test Results

- **216 tests pass** (up from 67)
- CLI commands verified with real checkpoints

---

## Critical Learnings (MUST READ)

### Principle: "Safe Async Bridging"

> **Use `run_sync()` to safely call async code from sync context. Never use deprecated `asyncio.get_event_loop()` pattern.**

```python
from protocols.prompt.section_base import run_sync

# DO: Use run_sync() for safe bridging
result = run_sync(soft.crystallize(context))

# DON'T: Use deprecated pattern (fails in Python 3.10+)
loop = asyncio.get_event_loop()  # DeprecationWarning → RuntimeError
loop.run_until_complete(...)     # Fails in async context
```

### Pattern: PromptM Monad

```python
from protocols.prompt.monad import PromptM, Source, lift_trace

# Composable transformations with provenance
section = Section(name="test", content="hello", token_cost=5, required=True)

result = (
    PromptM.unit(section)
    .with_trace("Starting transformation")
    .with_provenance(Source.TEMPLATE)
    .map(lambda s: s.with_content(s.content.upper()))
    .with_trace("Uppercased content")
)

# Operator overloads
m = PromptM.unit("hello")
m2 = m >> lift_trace("processed")  # >> is bind
m3 = m | str.upper                  # | is map
```

### Pattern: Checkpoint During Compile

```python
# CLI automatically creates checkpoints
uv run python -m protocols.prompt.cli compile --reason "Fix typo"
# → Checkpoint: 26b96d66ddb39cb5

# View history
uv run python -m protocols.prompt.cli history
# → [26b96d66] 2025-12-16T11:18:02 (+47 tokens) Fix typo

# Rollback with partial ID
uv run python -m protocols.prompt.cli rollback 26b96d66
# → ✓ Rollback successful!
```

### Pattern: Reasoning Traces

```python
# All inference produces reasoning traces (taste decision: "Show reasoning")
result = await soft.crystallize(context)
print(result.reasoning_trace)
# ('Crystallizing section: forest',
#  'Trying source: forest:file (priority=FILE)',
#  'Source succeeded with rigidity=0.4',
#  'Using FIRST_WINS merge strategy',
#  ...)
```

---

## Current Priority: Wave 4 ("Habit Encoder + TextGRAD")

### Wave 4 Tasks

| # | Task | Description | Status |
|---|------|-------------|--------|
| 4.1 | HabitEncoder | Learn patterns from git/sessions/code | ⏳ |
| 4.2 | SessionAnalyzer | Analyze Claude Code session transcripts | ⏳ |
| 4.3 | TextGRAD | Apply feedback as textual gradients | ⏳ |
| 4.4 | SemanticFusion | Merge habits with semantic similarity | ⏳ |

### Wave 4 Complete When

- [ ] HabitEncoder produces habit list from signals
- [ ] Habits influence prompt section content
- [ ] TextGRAD improves prompt from feedback
- [ ] Semantic fusion merges multiple sources intelligently

---

## Existing Prompt Infrastructure

```
impl/claude/protocols/prompt/
├── __init__.py              # Package exports (includes Wave 3 monad)
├── polynomial.py            # PROMPT_POLYNOMIAL state machine
├── section_base.py          # Section types + run_sync() utility
├── compiler.py              # Compilation pipeline
├── monad.py                 # PromptM[A] monad (Wave 3)
├── soft_section.py          # SoftSection with rigidity spectrum
├── cli.py                   # Full CLI with history/rollback/diff
├── sections/                # 9 section compilers
│   ├── identity.py          # Includes Ψ/Ω + em-dashes
│   ├── principles.py        # Dynamic (reads spec/principles.md)
│   ├── agentese.py          # Fixed arrows (→)
│   ├── systems.py           # Dynamic with curated fallback
│   ├── directories.py       # Hardcoded
│   ├── skills.py            # CURATED_DESCRIPTIONS added
│   ├── commands.py          # Hardcoded
│   ├── forest.py            # Dynamic (reads plans/_forest.md)
│   └── context.py           # Dynamic (git status, session info)
├── sources/                 # Content sources for SoftSection
├── rollback/                # Full rollback capability
├── habits/                  # HabitEncoder stubs (Wave 4 impl)
└── _tests/                  # 216 tests
```

---

## Key Commands

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Run prompt tests (216 tests)
uv run python -m pytest protocols/prompt/_tests/ -v

# Compile prompt (with automatic checkpoint)
uv run python -m protocols.prompt.cli compile --output /tmp/compiled.md --reason "Testing"

# View checkpoint history
uv run python -m protocols.prompt.cli history

# Rollback to previous version
uv run python -m protocols.prompt.cli rollback <checkpoint_id>

# Compare to original
uv run python -m protocols.prompt.cli compare

# Quick monad verification
uv run python << 'EOF'
from protocols.prompt.monad import PromptM, Source, sequence

# Test monadic laws
x = "hello"
f = lambda s: PromptM.unit(s.upper())

# Left Identity: unit(x).bind(f) == f(x)
assert PromptM.unit(x).bind(f).value == f(x).value
print("✓ Left Identity holds")

# Right Identity: m.bind(unit) == m
m = PromptM.unit(x)
assert m.bind(PromptM.unit).value == m.value
print("✓ Right Identity holds")

# Test sequence
ms = [PromptM.unit(1), PromptM.unit(2), PromptM.unit(3)]
assert sequence(ms).value == [1, 2, 3]
print("✓ Sequence works")
EOF
```

---

## Anti-Patterns Discovered

| Anti-Pattern | Example | Correct Approach |
|-------------|---------|------------------|
| Over-parsing | Complex regex to extract tables | Simple extraction + curated fallback |
| Auto-generation | Generic H1 headers as descriptions | Curated description mapping |
| ASCII typography | `->` and `-` for arrows/dashes | Unicode `→` and `—` |
| Silent truncation | `[:10]` limit without checking | Log warning + use complete fallback |
| asyncio.get_event_loop() | Deprecated in Python 3.10+ | Use `run_sync()` utility |
| run_until_complete in async | Fails when event loop running | ThreadPoolExecutor via run_sync() |
| Skip checkpoints | Lose ability to rollback | Always use `--checkpoint` (default) |

---

## Cross-References

- **Spec**: `spec/protocols/evergreen-prompt-system.md`
- **Plan**: `plans/evergreen-prompt-implementation.md`
- **Wave 3 Details**: `plans/_continuations/evergreen-wave3-continuation.md`
- **System Prompt**: `prompts/evergreen-builder-system-prompt.md`
- **Principles**: `spec/principles.md`

---

## Next Session Prompt

```
Evergreen Wave 3 (Core Infrastructure) is COMPLETE. We have:
- PromptM monad with unit/bind/map + all three laws verified (31 tests)
- Rollback CLI: history, rollback, diff commands
- Automatic checkpoints during compile
- run_sync() for safe sync→async bridging
- 216 tests passing

Key learning: "Safe Async Bridging" - use run_sync() utility,
never asyncio.get_event_loop() pattern (deprecated in 3.10+).

Wave 4 ("Habit Encoder + TextGRAD") is ready. Tasks:

1. **HabitEncoder** (4.1)
   - Learn patterns from git commits, session transcripts, code
   - File: `protocols/prompt/habits/encoder.py`

2. **SessionAnalyzer** (4.2)
   - Analyze Claude Code session transcripts
   - File: `protocols/prompt/habits/session_analyzer.py`

3. **TextGRAD** (4.3)
   - Apply feedback as textual gradients
   - File: `protocols/prompt/textgrad/improver.py`

4. **SemanticFusion** (4.4)
   - Merge multiple habit signals with semantic similarity
   - File: `protocols/prompt/fusion/semantic.py`

RECOMMENDED: Start with HabitEncoder (4.1) - stubs exist in habits/

Key files:
- plans/_continuations/evergreen-wave3-reformation-continuation.md (architecture)
- protocols/prompt/habits/git_analyzer.py (existing stubs)
- spec/heritage.md Part II (DSPy, TextGRAD theory)

Remember:
- Use run_sync() for async bridging
- PromptM for composable transformations with provenance
- All changes create checkpoints (safety net)
```

---

*"The monad that improves itself is the monad that transcends itself."*
