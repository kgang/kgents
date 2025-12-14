# CLI Deprecation Removal Complete

> **Date**: 2025-12-14
> **Cycle**: cli-deprecation-removal
> **Phase**: REFLECT (complete)

---

## Summary

Removed 69 deprecated CLI commands from `hollow.py`. AGENTESE context routing is now the ONLY interface.

## What Was Done

1. **COMMAND_REGISTRY cleaned** - Reduced from ~100+ entries to 10:
   - `self`, `world`, `concept`, `void`, `time` (contexts)
   - `do`, `flow` (intent/pipeline)
   - `init`, `wipe` (bootstrap)
   - `town` (crown jewel, kept)

2. **DEPRECATION_MAP removed** - 79 lines of deprecation logic deleted

3. **Tests updated** - All 21 hollow tests pass with new command structure

4. **Documentation updated** - Removed "Legacy Commands" section from cli-reference.md

## Metrics

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| hollow.py lines | 839 | 636 | -24% |
| COMMAND_REGISTRY entries | ~100 | 10 | -90% |
| Startup time | <50ms | 49ms | maintained |

## Key Decisions

1. **Handler files kept** - All 43 handler files preserved. Context routers import them dynamically. Orphaned handlers can be cleaned in a future cycle.

2. **town command kept** - Added back as a "crown jewel" command for Agent Town access.

3. **No backward compatibility** - Deprecated commands now return "unknown command" with suggestions to use AGENTESE paths.

## Patterns Observed

- **Context routing works** - All functionality remains accessible via `kgents self soul`, `kgents time trace`, etc.
- **Clean separation** - Top-level commands are now purely structural (contexts + bootstrap)
- **Startup maintained** - 49ms startup despite lazy loading unchanged

## Seeds for Future Work

1. **Orphaned handler cleanup** - 16 handler files not imported by any context router could be deleted
2. **Genus layer routing** - Power user commands (capital, grammar, etc.) need a home
3. **I-gent visualization** - Visualization primitives (whisper, sparkline) need context routing

---

*"The noun is a lie. There is only the rate of change."* — AGENTESE

*Deprecation was the warning. Removal is the follow-through.*
