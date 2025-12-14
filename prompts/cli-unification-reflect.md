# CLI Unification: REFLECT Phase

> **Process**: Full 11-phase ceremony (AD-005)
> **Skill Reference**: `docs/skills/n-phase-cycle/README.md`
> **Plan Reference**: `plans/devex/cli-unification.md`

---

## Hydration Block

```
/hydrate
see plans/devex/cli-unification.md

handles: scope=cli-unification; phase=REFLECT; ledger={PLAN:✓,RESEARCH:✓,DEVELOP:✓,STRATEGIZE:✓,CROSS-SYNERGIZE:✓,IMPLEMENT:✓,QA:✓,TEST:✓,EDUCATE:pending,MEASURE:pending,REFLECT:active}; entropy=0.02
mission: Capture learnings from soul.py refactor. Update metrics. Generate next-loop seeds.
actions:
  - SENSE: Review what worked/didn't in extraction pattern
  - ACT: Write epilogue, update plan status, update _status.md
  - REFLECT: Identify patterns for a_gent.py and other handler refactors
exit: Epilogue in plans/_epilogues/; _status.md updated; next-loop prompt generated.
⟂[DETACH:cycle_complete] if all learnings captured and next cycle ready
```

---

## Phase Context (from IMPLEMENT)

### Artifacts Created

| Artifact | Path | Lines | Purpose |
|----------|------|-------|---------|
| InvocationContext | `cli/shared/context.py` | 99 | Unified command context |
| OutputFormatter | `cli/shared/output.py` | 117 | Unified output handling |
| StreamingHandler | `cli/shared/streaming.py` | 199 | Unified streaming |
| dialogue.py | `cli/commands/soul/dialogue.py` | 199 | reflect, advise, challenge, explore |
| quick.py | `cli/commands/soul/quick.py` | 209 | vibe, drift, tense |
| inspect.py | `cli/commands/soul/inspect.py` | 235 | starters, manifest, eigenvectors, audit, garden, validate, dream |
| ambient.py | `cli/commands/soul/ambient.py` | 397 | stream, watch |
| being.py | `cli/commands/soul/being.py` | 226 | history, propose, commit, crystallize, resume |
| soul.py (router) | `cli/handlers/soul.py` | 283 | Thin router only |

### Metrics Achieved

| Metric | Before | After | Target | Delta |
|--------|--------|-------|--------|-------|
| soul.py lines | 2019 | **283** | < 300 | -86% ✅ |
| Tests passing | 34 | 34 | All | 100% ✅ |
| Type errors | - | 0 | 0 | ✅ |
| Largest new file | - | 397 | < 400 | ✅ |

### Key Decisions Made

1. **Shared infrastructure first** — Created `cli/shared/` before extraction
2. **Single-responsibility modules** — Each file handles one concern
3. **Context encapsulation** — `InvocationContext` wraps reflector + flags
4. **Pattern proof first** — Extracted dialogue.py to prove pattern before bulk extraction

---

## REFLECT Mission

### 1. Capture Learnings

**What Worked**:
- Creating shared infrastructure before extraction prevented duplication
- The `InvocationContext.from_args()` pattern simplified flag parsing
- Module-level imports in router kept it thin (283 lines)
- Match statement for routing is readable and extensible

**What Didn't Work / Friction Points**:
- Test imports needed updating after refactor (could automate)
- Some commands (approve) still delegate to old handlers (soul_approve.py)
- ambient.py is 397 lines — could split further (stream.py, watch.py)

**Patterns Identified for Reuse**:
```python
# The extraction pattern:
# 1. Create shared/ infrastructure
# 2. Create commands/<handler>/ directory
# 3. Group by responsibility: dialogue, quick, inspect, ambient, being
# 4. Reduce original handler to router with match statement
# 5. Update test imports
```

### 2. Update Plan Status

Update `plans/devex/cli-unification.md`:
```yaml
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: touched
  TEST: touched
  EDUCATE: pending  # Need usage notes
  MEASURE: pending  # Need dashboard hook
  REFLECT: touched
progress: 40  # Phase 2 (Soul) complete, Phases 3-5 pending
```

### 3. Write Epilogue

Create `impl/claude/plans/_epilogues/2025-12-14-cli-unification-soul-complete.md`:
- Summary of refactor
- Before/after metrics
- Patterns for next phases
- Next-loop seeds

### 4. Generate Next-Loop Seeds

| Seed | Priority | Estimated Effort | Phase |
|------|----------|------------------|-------|
| Agent command refactor (a_gent.py) | High | 1-2 hours | IMPLEMENT |
| EDUCATE: Update cli-command.md skill | Medium | 30 min | EDUCATE |
| MEASURE: Add CLI metrics to _status.md | Medium | 15 min | MEASURE |
| Infra consolidation (infra, daemon, telemetry) | Low | 2+ hours | PLAN |

---

## Exit Criteria

- [ ] Epilogue written to `plans/_epilogues/`
- [ ] Plan file updated with progress and ledger
- [ ] `_status.md` updated with CLI unification status
- [ ] Next-loop continuation prompt generated
- [ ] Branch candidates classified

---

## Branch Candidates (from REFLECT)

| Branch | Classification | Action |
|--------|---------------|--------|
| a_gent.py refactor | **Next cycle** | Continue CLI Unification Phase 3 |
| Split ambient.py | **Deferred** | Park until a_gent.py done |
| soul_approve.py integration | **Deferred** | Minor, can batch later |
| Flow composition engine | **Blocked** | Needs unified CLI first |

---

## Entropy Budget

```
void.entropy.sip[phase=REFLECT][amount=0.02]
```

Minimal exploration — mostly synthesis and documentation.

---

## Continuation Generator

Upon completing REFLECT, emit one of:

### Option A: Continue to Phase 3 (Agent Commands)

```
⟿[IMPLEMENT]
/hydrate
see plans/devex/cli-unification.md

handles: scope=cli-unification-phase3; phase=IMPLEMENT; ledger={...REFLECT:✓}; entropy=0.08
mission: Refactor a_gent.py (1110 lines) to < 300 using soul.py pattern.
actions:
  - Create commands/agent/ directory
  - Extract subcommands to separate files
  - Reduce a_gent.py to router
exit: a_gent.py < 300 lines; all tests pass; pattern proven for Phase 4.
⟂[BLOCKED:test_failure] if tests break
```

### Option B: DETACH (cycle complete for now)

```
⟂[DETACH:phase_complete]
CLI Unification Phase 2 (Soul) complete.
Next attach point: prompts/cli-unification-phase3-implement.md
```

---

## Next-Loop Continuation Prompt

Upon completion of this REFLECT phase, generate the following for Phase 3:

---

# CLI Unification Phase 3: Agent Command Refactor

> **Process**: Full 11-phase ceremony (AD-005)
> **Skill Reference**: `docs/skills/n-phase-cycle/README.md`
> **Plan Reference**: `plans/devex/cli-unification.md`

---

## Hydration Block

```
/hydrate
see plans/devex/cli-unification.md

handles: scope=cli-unification-phase3; phase=IMPLEMENT; ledger={PLAN:✓,RESEARCH:✓,DEVELOP:✓,STRATEGIZE:✓,CROSS-SYNERGIZE:✓,IMPLEMENT:active}; entropy=0.08
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
├── shared/                    # REUSE (433 lines)
│   ├── context.py            # InvocationContext ← reuse
│   ├── output.py             # OutputFormatter ← reuse
│   └── streaming.py          # StreamingHandler ← reuse
├── commands/
│   ├── soul/                 # DONE (1364 lines)
│   └── agent/                # TARGET (create)
│       ├── __init__.py       # Router + help
│       ├── run.py            # Agent execution
│       ├── list.py           # Agent listing
│       ├── status.py         # Agent status
│       └── lifecycle.py      # Start/stop/restart
└── handlers/
    ├── soul.py               # DONE (283 lines)
    └── a_gent.py             # TARGET (1110 → <300)
```

### Target File Analysis

| Section | Lines (approx) | Extraction Target |
|---------|---------------|-------------------|
| Imports, help | 1-100 | Keep in `__init__.py` |
| Agent listing | 100-300 | `list.py` |
| Agent running | 300-600 | `run.py` |
| Agent status | 600-800 | `status.py` |
| Lifecycle mgmt | 800-1110 | `lifecycle.py` |

---

## Exit Criteria

1. `a_gent.py` reduced to < 300 lines (routing only)
2. `commands/agent/` created with extracted modules
3. Shared infrastructure (`cli/shared/`) reused
4. All existing agent tests pass
5. No circular imports

---

## Success Metrics

| Metric | Before | Target |
|--------|--------|--------|
| a_gent.py lines | 1110 | < 300 |
| Shared infra reuse | - | 100% |
| Test pass rate | 100% | 100% |

---

## Continuation

On completion:

```
⟿[TEST]
/hydrate
handles: scope=cli-unification-phase3; phase=TEST; ledger={...IMPLEMENT:✓}
mission: Verify agent refactor with full test suite.
exit: All tests pass; no regressions.
```

Or if blocked:

```
⟂[BLOCKED:reason] description
```

---

*"Compose commands like you compose agents: lawfully, joyfully, and with minimal ceremony."*
