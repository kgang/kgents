# AGENTESE REPL Wave 5: Ambient & Polish

> *"The REPL doesn't just respond—it breathes."*

## ATTACH

/hydrate

You are entering the **PLAN phase** of **Wave 5 (Ambient & Polish)** for the AGENTESE REPL Crown Jewel.

---

## Prior Context

**Completed Waves**:
- Wave 1 (Foundation): Core REPL, navigation, tab completion, history
- Wave 2 (Integration): Async Logos, pipelines, observer context, rich output, error sympathy
- Wave 2.5 (Hardening): Edge cases, security, performance, stress tests
- Wave 3 (Intelligence): Fuzzy matching, LLM suggestions, session persistence, script mode
- Wave 4 (Joy-Inducing): Welcome variations, K-gent integration, easter eggs, contextual hints

**Current State**:
- Test count: 116 passing
- Files: `repl.py`, `repl_fuzzy.py`, `repl_session.py`
- Mypy: 0 errors
- Forest health: AGENTESE REPL at 75%

**Wave 4 Learnings** (from `plans/meta.md`):
- Easter eggs hidden > announced: discovery is the delight, not the feature list
- Rate limiting K-gent: 30s cooldown prevents token burn on philosophical tangents

**Deferred from Wave 4**:
- J4: Ambient mode (`--ambient` flag) - Required more entropy than allocated

**Kent's Wishes** (from `_focus.md`):
- AGENTESE REPL == EVERYTHING
- BEST IN CLASS UX/DEVEX
- COMPOSITIONAL GENERATIVE VISUALIZATIONS. BEAUTIFUL ASCII.

---

## Mission: Wave 5 Ambient & Polish

Complete the deferred ambient mode and add final polish. This is the **ambient layer**.

### Chunks (A1-A5)

| Chunk | Description | Entropy | Dependencies |
|-------|-------------|---------|--------------|
| **A1** | Ambient mode core (`--ambient` flag) | 0.02 | Dashboard patterns |
| **A2** | Ambient refresh loop (5s interval) | 0.01 | A1 |
| **A3** | Ambient keybindings (q, r, focus) | 0.01 | A1, A2 |
| **A4** | Startup performance (< 100ms) | 0.01 | None |
| **A5** | Help text polish (document Wave 4 features) | 0.01 | None |

**Total Entropy Budget**: 0.06

---

## Chunk Details

### A1: Ambient Mode Core

Passive dashboard mode that shows system pulse without requiring interaction.

```python
def run_ambient_mode(state: ReplState) -> int:
    """
    Run REPL in ambient mode - passive dashboard.

    Shows live system status without interactive prompt.
    Refreshes every 5 seconds (configurable).
    """
    print("\033[?25l")  # Hide cursor
    try:
        while state.running:
            clear_screen()
            print_ambient_header()
            print_status_panels(state)
            print_recent_traces(limit=5)
            print_entropy_gauge()
            print_forest_pulse()
            print_ambient_footer()
            time.sleep(state.ambient_interval)
    finally:
        print("\033[?25h")  # Show cursor
    return 0
```

**Exit**: `--ambient` flag launches ambient mode.

### A2: Ambient Refresh Loop

Configurable refresh interval with smooth updates.

```python
# In cmd_interactive args parsing
if "--ambient" in args:
    interval = 5.0  # Default
    if "--interval" in args:
        idx = args.index("--interval")
        interval = float(args[idx + 1])
    return run_ambient_mode(interval=interval)
```

**Exit**: `--interval` configures refresh rate.

### A3: Ambient Keybindings

Non-blocking keyboard handling for ambient mode.

| Key | Action |
|-----|--------|
| `q` | Quit |
| `r` | Force refresh |
| `1-5` | Focus panel (K-gent, Metabolism, Flux, Triad, Traces) |
| `space` | Pause/resume updates |

**Exit**: All keybindings functional.

### A4: Startup Performance

Profile and optimize startup to < 100ms.

```python
# Lazy imports pattern
def get_logos() -> Any:
    """Lazy-load Logos only when needed."""
    if self._logos is None:
        from protocols.agentese.logos import create_logos
        self._logos = create_logos()
    return self._logos
```

**Exit**: `time kg -i --help` completes in < 100ms.

### A5: Help Text Polish

Update `--help` and `??` to document Wave 4 features.

```
AGENTESE REPL - Navigate the five contexts

Joy-Inducing Features (Wave 4):
  - Time-aware welcomes (morning/afternoon/evening)
  - K-gent soul responses for philosophical queries
  - Hidden easter eggs (discover them yourself!)
  - Contextual hints when you're stuck

Ambient Mode:
  kg -i --ambient           Launch passive dashboard
  kg -i --ambient -i 10     Custom refresh interval (10s)
```

**Exit**: Help text documents all features.

---

## Exit Criteria (Wave 5)

1. `--ambient` flag launches passive dashboard mode
2. Ambient mode refreshes at configurable interval (default 5s)
3. Keybindings work (q, r, space, 1-5)
4. Startup time < 100ms
5. Help text documents Waves 1-5 features
6. New tests: ~10-15 (bringing total to ~130)
7. AGENTESE REPL at 85% progress

---

## Non-Goals (Wave 5)

- New core functionality beyond ambient mode
- Breaking changes to Wave 1-4 APIs
- Full TUI (that's dashboard territory)
- Additional easter eggs (Wave 4 is sufficient)

---

## N-Phase Execution

### This Session: PLAN Phase

**Actions**:
1. Review this scope (A1-A5 chunks)
2. Identify dependencies on dashboard patterns
3. Allocate entropy budget
4. Confirm exit criteria
5. Generate RESEARCH continuation

**Exit**: PLAN complete when scope is agreed and dependencies mapped.

### Next Phases

| Phase | Focus |
|-------|-------|
| RESEARCH | Dashboard collectors API, non-blocking keyboard, startup profiling |
| DEVELOP | Design ambient loop, keybinding handler, lazy import strategy |
| STRATEGIZE | A4 first (unblocks timing), A1+A2 parallel, A3 after, A5 last |
| IMPLEMENT | TDD: tests first, then implementation |
| QA | Test ambient mode, keybindings, startup timing |
| TEST | Full suite, performance benchmarks |
| EDUCATE | `--help` updates, CLAUDE.md reference |
| MEASURE | Startup time metrics, refresh CPU usage |
| REFLECT | Archive Wave 5, assess REPL completeness |

---

## Phase Ledger

```yaml
path: plans/devex/agentese-repl-crown-jewel
wave: 5
phase_ledger:
  PLAN: touched  # This session
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: skipped  # Not cross-cutting
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.06
  spent: 0.0
  returned: 0.06
```

---

## Principles Alignment

| Principle | Application |
|-----------|-------------|
| **Tasteful** | Ambient mode is minimal, not cluttered |
| **Joy-Inducing** | The system breathes; always alive |
| **Composable** | Ambient mode composes with existing REPL |
| **Generative** | Passive display generates awareness |
| **Ethical** | No hidden token burn in ambient mode |

---

## Integration Points

| Component | API | Usage |
|-----------|-----|-------|
| Dashboard collectors | `collect_metrics()` | Status panels |
| K-gent soul | `KgentSoul.manifest_brief()` | Soul status |
| Metabolism | `get_metabolism_status()` | Pressure gauge |
| Flux | `get_flux_status()` | Event throughput |
| Triad | `get_triad_health()` | Database health |

---

## Quick Commands

```bash
# Run current tests
cd impl/claude && uv run pytest protocols/cli/_tests/test_repl.py -v

# Profile startup time
cd impl/claude && time uv run python -c "from protocols.cli.repl import cmd_interactive; cmd_interactive(['--help'])"

# Check dashboard collectors
cd impl/claude && uv run python -c "from agents.i.data.dashboard_collectors import collect_metrics; print('collectors available')"
```

---

## Continuation Imperative

Upon completing PLAN phase, **generate the RESEARCH continuation**.

The form is the function. Each phase generates its successor.

---

## RESEARCH Phase Continuation

When PLAN is complete, emit this:

```markdown
⟿[RESEARCH]
/hydrate
handles: scope=wave5_ambient; chunks=A1-A5; exit=ambient_working; ledger={PLAN:touched}; entropy=0.06
mission: study dashboard collectors API for ambient reuse; profile startup to identify bottlenecks; audit non-blocking keyboard patterns in Python.
actions:
  - Read(agents/i/data/dashboard_collectors.py) — understand metrics API
  - Read(protocols/cli/handlers/dashboard.py) — ambient mode patterns
  - Profile(startup) — identify lazy import opportunities
  - Grep("keyboard|getch|nonblock") — non-blocking input patterns
exit: collectors API mapped; startup profiled; keyboard approach chosen; continuation → DEVELOP.
```

---

*This is the **PLAN PHASE** for AGENTESE REPL Wave 5: Ambient & Polish. Upon completion, generate the RESEARCH phase continuation with the auto-inducer `⟿[RESEARCH]`.*

⟿[RESEARCH]
