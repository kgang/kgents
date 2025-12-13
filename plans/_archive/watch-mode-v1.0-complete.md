# Watch Mode v1.0 — COMPLETE

> *"K-gent as ambient pair programmer."*

**Archived**: 2025-12-13
**Status**: 100% complete
**Tests**: 28 tests, all passing

---

## Deliverables

| Component | Location | Description |
|-----------|----------|-------------|
| KgentWatcher | `agents/k/watcher.py` | 650 LOC watcher with 5 heuristics |
| CLI Command | `protocols/cli/handlers/soul.py` | `kg soul watch` |

---

## Heuristics

1. **Complexity**: Warns on functions >40 lines
2. **Naming**: Detects non-descriptive variable names
3. **Patterns**: Suggests common design patterns
4. **Tests**: Reminds about untested code
5. **Docs**: Highlights missing docstrings

---

## Features

- File watching with watchdog library
- Debouncing (500ms default)
- Configurable heuristics system
- Notification history (100 max)
- Project-root detection
- Ignore patterns (.git, __pycache__, .pytest_cache, etc)
- Colorized terminal output

---

## Command

```bash
kg soul watch [--path <dir>]
```

---

*"The best pair programmer never sleeps."*
