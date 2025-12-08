# HYDRATE.md - kgents Session Context

---

## TL;DR

**Status**: Evolve pipeline refactored for AI agent ergonomics
**Branch**: `main` (uncommitted: `evolve.py`)
**Mypy**: 0 errors (55 source files, strict)
**Evolution**: Test-friendly defaults + AI agent interface added

---

## This Session: Evolve Pipeline Improvements

### New Modes for AI Agents

| Mode | Purpose | Speed | Default |
|------|---------|-------|---------|
| `test` | Fast iteration | ⚡⚡⚡ | ✓ (now default) |
| `status` | Check state | ⚡⚡⚡ | Read-only |
| `suggest` | Get suggestions | ⚡⚡ | Read-only |
| `full` | Complete evolution | ⚡ | Was default |

### Changed Defaults (more test-friendly)

**Before**: `python evolve.py` → full evolution (slow, modifies files)
**After**: `python evolve.py` → test mode (fast, dry-run, safe)

- Target: `meta` (single module) instead of `all`
- Dry-run: `True` by default (safe)
- Quick mode: `True` (skip dialectic synthesis)
- Hypotheses: `2` per module (down from 4)
- Max improvements: `1` per module (down from 4)

### AI Agent Workflow Pattern

```bash
# Periodic check (for /hydrate command)
python evolve.py status

# Get improvement suggestions
python evolve.py suggest

# Fast test run
python evolve.py  # defaults to test mode

# Apply improvements
python evolve.py meta --auto-apply
```

---

## Next Session: Start Here

### Recommended: Test the New Interface

```bash
cd /Users/kentgang/git/kgents/impl/claude

# Test new modes
python evolve.py status    # Should show current state
python evolve.py suggest   # Should analyze modules
python evolve.py           # Should run test mode (fast)
```

### Option 1: Wire Recovery Layer

Integrate Phase 2.5c into evolve pipeline:
- Call `RetryStrategy` on test failures in `_process_module()`
- Use `FallbackStrategy` when retries exhausted
- Track patterns in `ErrorMemory`

### Option 2: Add API Stubs to Prompts

Enhance `prompts.py` to include actual API signatures:
- Dataclass field definitions
- Function signatures from imported modules
- Enum values

This will reduce hallucinated APIs that caused 30 failures in last run.

### Option 3: Message Bus Isomorphism

Future generalization:
- Evolve pipeline as message handler
- Status/suggest as query messages
- Test/full as command messages
- Foundation for distributed agent coordination

---

## What Exists

**agents/e/parser.py** - Multi-strategy code extraction + f-string repair
**agents/e/validator.py** - Pre-mypy schema validation
**agents/e/repair.py** - AST-based auto-fixes
**agents/e/retry.py** - Failure-aware prompt refinement
**agents/e/fallback.py** - Progressive simplification
**agents/e/error_memory.py** - Failure pattern learning
**agents/e/prompts.py** - Rich context building (needs API stubs)
**agents/e/preflight.py** - Module health validation

---

## Session Log

**Dec 8 PM (current)**: Evolve pipeline refactor for AI agent ergonomics
  - Added 4 modes: test (default), status, suggest, full
  - Changed defaults to test-friendly (dry-run, quick, single module)
  - Created AI agent interface for periodic checks via /hydrate
  - Foundation for future message bus isomorphism pattern
**Dec 8 PM**: Full `evolve all --auto-apply` run: 93 passed, 30 failed, 2 held
**Dec 8 PM**: 05b56aa - Fixed MYPYPATH in SandboxTestAgent
**Dec 8 PM**: 53e073b - Exported Phase 2.5c components from agents/e
**Dec 8 PM**: dd32fa7 - Phase 2.5c Recovery Layer

---
