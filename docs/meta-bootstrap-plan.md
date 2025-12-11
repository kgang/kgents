# Meta-Bootstrap Plan: Self-Observing Development

**Status**: Active | **Date**: 2025-12-10
**Philosophy**: The system that builds itself must observe itself building.

---

## The Core Insight

The DevEx Unified Plan V4 describes a mature system observing a developer. But during development, **who observes the system being built?** The answer: the system itself, from Day 0.

This plan implements cheap, immediate feedback loops that let kgents eat its own dogfood during development.

---

## The Five Cheap Loops

| Loop | Signal Source | Storage | Cost |
|------|---------------|---------|------|
| **Test Flinch** | pytest failures | `.kgents/ghost/test_flinches.jsonl` | ~20 lines |
| **Git Crystallization** | git log/diff | CLI commands | 0 (use git) |
| **HYDRATE.md Append** | key events | HYDRATE.md footer | ~15 lines |
| **CI Signals** | GitHub Actions | `.kgents/ghost/ci_signals.jsonl` | ~20 lines |
| **CLAUDE.md Drift** | git diff | Morning ritual | 0 (use git) |

---

## Implementation

### Loop 1: Test Flinch Logging

Every failing test is an algedonic signal. Wire pytest to emit them.

**File**: `impl/claude/conftest.py` (extend existing)

```python
# pytest hook: log failures as flinch signals
def pytest_runtest_logreport(report):
    if report.failed:
        _emit_test_flinch(report)
```

**Output**: `.kgents/ghost/test_flinches.jsonl`
```json
{"ts": 1702000000, "test": "test_synapse.py::test_fire", "phase": "call", "duration": 0.5}
```

### Loop 2: Git-Based Crystallization

Session crystallization is already in git. Make it explicit.

**Commands** (no code needed):
```bash
# Session narrative
git log --oneline --since="8 hours ago"

# Churn map (volatility indicator)
git diff --stat HEAD~10

# Prior drift
git diff HEAD~5 CLAUDE.md
```

### Loop 3: HYDRATE.md Auto-Append

HYDRATE.md is the thought_stream in disguise. Append signals to it.

**File**: `impl/claude/protocols/cli/devex/hydrate_signal.py`

```python
def append_hydrate_signal(event: str, detail: str = "") -> None:
    """Append a timestamped signal to HYDRATE.md."""
    ...
```

### Loop 4: CI Signal Emission

The CI pipeline emits semantic field signals on failure.

**File**: `.github/workflows/ci.yml` (extend existing)

Add step to emit signals on test failure:
```yaml
- name: Emit CI signal
  if: failure()
  run: |
    echo '{"ts": ..., "type": "CI_FAILURE", ...}' >> .kgents/ghost/ci_signals.jsonl
```

### Loop 5: CLAUDE.md Drift Tracking

The act of editing CLAUDE.md is K-gent calibration. Track it.

**Implementation**: Part of `kgents wake` ritual.

---

## Activation Sequence

1. **Immediate**: Add test flinch logging to conftest.py
2. **Immediate**: Create `.kgents/ghost/` directory structure
3. **Immediate**: Add hydrate_signal.py utility
4. **Next commit**: Update CI to emit signals
5. **Ongoing**: Use git commands for crystallization

---

## Success Criteria

- Test flinches accumulate in `.kgents/ghost/test_flinches.jsonl`
- CI failures create signals that persist across sessions
- HYDRATE.md grows organically with session markers
- `git diff CLAUDE.md` shows prior evolution over time

---

## Relation to V4 Plan

These cheap loops provide **real data** to inform the expensive builds:

| V4 Feature | Bootstrap Data Source |
|------------|----------------------|
| Keystroke dynamics | Test flinch patterns (proxy for frustration) |
| Shadow Executor | Test churn patterns (what gets rewritten) |
| Morning Calibration | CLAUDE.md drift |
| Evening Confessional | Git session narrative |

Build the fancy stuff *after* you have data about how you actually work.

---

*"Bootstrap the bootstrapper. Observe the observer. The recursive eye sees clearly."*
