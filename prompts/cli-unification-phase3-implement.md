# CLI Unification Phase 3: Agent Command Refactor

> **Process**: Full 11-phase ceremony (AD-005)
> **Skill Reference**: `docs/skills/n-phase-cycle/README.md`
> **Plan Reference**: `plans/devex/cli-unification.md`
> **Previous**: `impl/claude/plans/_epilogues/2025-12-14-cli-unification-soul-complete.md`

---

## Hydration Block

```
/hydrate
see plans/devex/cli-unification.md

handles: scope=cli-unification-phase3; phase=IMPLEMENT; ledger={PLAN:✓,RESEARCH:✓,DEVELOP:✓,STRATEGIZE:✓,CROSS-SYNERGIZE:✓,IMPLEMENT:active,QA:pending,TEST:pending}; entropy=0.08
mission: Apply soul.py extraction pattern to a_gent.py (1110 → <300 lines).
actions:
  - SENSE: Map a_gent.py structure, identify extraction points
  - ACT: Create commands/agent/, extract handlers, reduce to router
  - REFLECT: Verify pattern, update metrics
exit: a_gent.py < 300 lines; all agent tests pass; shared infra reused.
⟂[BLOCKED:test_failure] if tests break during refactor
⟂[BLOCKED:circular_import] if extraction creates import cycles
```

---

## Phase Context (from Soul Refactor)

### Pattern Proven

```
cli/
├── shared/                    # REUSE (439 lines)
│   ├── __init__.py           # Exports
│   ├── context.py            # InvocationContext ← reuse
│   ├── output.py             # OutputFormatter ← reuse
│   └── streaming.py          # StreamingHandler ← reuse
├── commands/
│   ├── soul/                 # DONE (1379 lines)
│   │   ├── __init__.py       # Router + help
│   │   ├── dialogue.py       # reflect, advise, challenge, explore
│   │   ├── quick.py          # vibe, drift, tense
│   │   ├── inspect.py        # starters, manifest, etc.
│   │   ├── ambient.py        # stream, watch
│   │   └── being.py          # history, propose, commit, etc.
│   └── agent/                # TARGET (create)
│       ├── __init__.py       # Router + help
│       ├── inspect.py        # `kgents a inspect <agent>`
│       ├── manifest.py       # `kgents a manifest <agent>`
│       ├── run.py            # `kgents a run <agent>`
│       ├── list.py           # `kgents a list`
│       └── dialogue.py       # `kgents a dialogue <agent>`
└── handlers/
    ├── soul.py               # DONE (283 lines)
    └── a_gent.py             # TARGET (1110 → <300)
```

### Target File Analysis (a_gent.py)

| Section | Lines (approx) | Commands | Extraction Target |
|---------|---------------|----------|-------------------|
| Imports, help, registry | 1-80 | - | Keep in `__init__.py` |
| _handle_dialogue | 80-200 | dialogue | `dialogue.py` |
| _handle_inspect | 200-400 | inspect | `inspect.py` |
| _handle_manifest | 400-600 | manifest | `manifest.py` |
| _handle_run | 600-850 | run | `run.py` |
| _handle_list | 850-1000 | list | `list.py` |
| cmd_a routing | 1000-1110 | router | Reduce to match statement |

---

## Key Implementation Steps

1. **Create `commands/agent/__init__.py`**
   - Help text, mode constants, DIALOGUE_AGENTS registry
   - Export print_help(), ALL_MODES

2. **Extract command files**
   - Each ~150-250 lines
   - Use `InvocationContext` from shared
   - Use `OutputFormatter` from shared
   - Pattern: `async def execute_<command>(ctx, ...) -> int`

3. **Reduce `handlers/a_gent.py` to router**
   - Module-level imports only
   - Match statement routing
   - Target: < 300 lines

4. **Update test imports if needed**
   - Verify `test_a_gent.py` exists and passes

---

## Exit Criteria

1. `a_gent.py` reduced to < 300 lines (routing only)
2. `commands/agent/` created with extracted modules
3. Shared infrastructure (`cli/shared/`) reused (no duplication)
4. All existing agent tests pass
5. No circular imports
6. No regressions in `kgents a` functionality

---

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| a_gent.py lines | 1110 | < 300 |
| Shared infra reuse | - | 100% |
| Test pass rate | 100% | 100% |
| Largest new file | - | < 300 |

---

## Test Commands

```bash
# Run agent tests
cd impl/claude && uv run pytest protocols/cli/handlers/_tests/test_a_gent.py -v

# Verify commands still work
kg a --help
kg a list
kg a inspect KgentSoul
```

---

## Continuation

On completion:

```
⟿[QA]
/hydrate
handles: scope=cli-unification-phase3; phase=QA; ledger={...IMPLEMENT:✓}
mission: QA the agent refactor with manual smoke tests.
exit: All commands work as before.
```

Or if blocked:

```
⟂[BLOCKED:reason] description
```

---

*"Compose commands like you compose agents: lawfully, joyfully, and with minimal ceremony."*
