# AGENTESE REPL: Crown Jewel Plan

> *"The interface that teaches its own structure through use is no interface at all."*

**Status**: COMPLETE (Wave 7 Mastery complete, hardened)
**Progress**: 95%
**Last Touched**: 2025-12-14
**Phase Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:touched, STRATEGIZE:touched, IMPLEMENT:touched, QA:touched, TEST:touched, REFLECT:touched}`
**Entropy Budget**: 0.02

---

## Vision

Transform the kgents CLI into a **liturgical navigation experience** where users explore the AGENTESE ontology through contextual discovery rather than memorized commands. The REPL should feel like grasping handles in a living world.

**Architectural Decision**: AD-007 (see `spec/principles.md`)

---

## Current State (Wave 1 Complete)

### Implemented

| Component | Status | Location |
|-----------|--------|----------|
| Core REPL engine | ✅ | `protocols/cli/repl.py` |
| Context navigation (self, world, concept, void, time) | ✅ | `repl.py:handle_navigation` |
| Holon navigation | ✅ | `repl.py:CONTEXT_HOLONS` |
| Tab completion | ✅ | `repl.py:Completer` |
| History persistence | ✅ | `~/.kgents_repl_history` |
| Colored prompts | ✅ | `repl.py:ReplState.prompt` |
| Introspection (`?`, `??`) | ✅ | `repl.py:handle_introspection` |
| Composition (`>>`) | ✅ (parse) | `repl.py:handle_composition` |
| `-i` flag wiring | ✅ | `hollow.py` |

### Wave 2 Complete (2025-12-14)

| Component | Status | Location |
|-----------|--------|----------|
| Async invocation via Logos | ✅ | `repl.py:handle_invocation` |
| Pipeline execution (`>>`) | ✅ | `repl.py:handle_composition` |
| Observer/Umwelt integration | ✅ | `repl.py:ReplState.get_umwelt` |
| `/observer` commands | ✅ | `repl.py:handle_observer_command` |
| Rich output rendering | ✅ | `repl.py:_render_result` |
| Error sympathy | ✅ | `repl.py:_error_with_sympathy` |

### All Features Implemented ✅

| Component | Status | Notes |
|-----------|--------|-------|
| Fuzzy matching for paths | ✅ | `repl_fuzzy.py` - rapidfuzz with fallback |
| Session state persistence | ✅ | `repl_session.py` - save/restore/clear |
| LLM suggestions | ✅ | `LLMSuggester` with entropy budget |
| Tutorial mode | ✅ | `repl_tutorial.py` - `--tutorial` flag |
| Adaptive learning guide | ✅ | `repl_guide.py` - `--learn` flag |
| Mastery tier skills | ✅ | Wave 7 - 18 skills with progression |

---

## Crown Jewel Phases

### Phase 1: Foundation (COMPLETE) ✅

- [x] Core REPL loop with readline
- [x] Five-context navigation
- [x] Tab completion
- [x] History
- [x] Introspection commands
- [x] Wiring to hollow.py

### Phase 2: Deep Integration (COMPLETE ✅)

**Focus**: Make the REPL a first-class AGENTESE citizen.

| Task | Description | Exit Criterion | Status |
|------|-------------|----------------|--------|
| Async execution | Route through Logos properly | `await logos.invoke()` works | ✅ |
| Observer context | Pass Umwelt through navigation | Affordances change by observer | ✅ |
| Rich output | Tables, panels, colors | Output matches TUI quality | ✅ |
| Pipeline execution | Actually run `>>` compositions | `world.agents >> concept.count` works | ✅ |
| Error sympathy | Errors suggest next actions | User never stuck | ✅ |

### Phase 3: Intelligence

| Task | Description |
|------|-------------|
| LLM suggestions | "Did you mean..." with semantic understanding |
| Auto-complete from Logos | Dynamic completion from registry |
| Command history search | Fuzzy search through history |
| Session replay | Re-run previous exploration paths |

### Phase 4: Joy-Inducing Polish (COMPLETE ✅)

| Task | Description | Status |
|------|-------------|--------|
| Welcome variations | Context-aware greetings | ✅ |
| Easter eggs | Hidden commands for delight | ✅ |
| Personality integration | K-gent can respond in REPL | ✅ |
| Ambient mode | REPL as passive dashboard | ✅ |

### Phase 5: Ambient & Polish (COMPLETE ✅)

| Task | Description | Status |
|------|-------------|--------|
| --ambient flag | Launch passive dashboard mode | ✅ |
| Configurable interval | --interval <secs> (default 5s) | ✅ |
| Non-blocking keybindings | q/r/space/1-5 for control | ✅ |
| Help text polish | Full documentation in HELP_TEXT | ✅ |
| 16 new tests | Wave 5 coverage | ✅ |

---

## Dependencies

| Dependency | Status | Impact |
|------------|--------|--------|
| Logos resolver | ✅ | Required for proper path resolution |
| Context routers | ✅ | Already wired (self_, world, etc.) |
| CLI unification | 🚧 | Enables cleaner routing |
| Agent Town | 🚧 | Town commands available in REPL |

---

## Integration Points

### With Agent Town

```
[world] » town
→ town
[world.town] » step
Epoch 1: Citizens deliberated...
[world.town] » observe alice
Alice (RESTED): thinking about mathematics...
```

### With K-gent Soul

```
[self] » soul
→ soul
[self.soul] » reflect "how am I doing?"
K-gent: You've been focused and productive...
```

### With Void (Accursed Share)

```
[void] » entropy sip
Drew 0.07 from Accursed Share. Use wisely.
[void] » shadow
Your shadow patterns: perfectionism, scope creep...
```

---

## Success Criteria

1. **Pedagogical**: A new user can learn the ontology by exploring (`?` at each level)
2. **Efficient**: Power users can navigate faster than typing full paths
3. **Composable**: Pipelines can be built and tested interactively
4. **Delightful**: The experience feels warm, not robotic
5. **Degraded**: Works offline/without all services running

---

## Metrics to Track

| Metric | Target | Current |
|--------|--------|---------|
| Time to first successful navigation | < 30s | TBD |
| Commands needed to reach any node | ≤ 3 | ✅ |
| Tab completions before selection | ≤ 2 | ✅ |
| User-reported satisfaction | > 4.5/5 | TBD |

---

## Risks

| Risk | Mitigation |
|------|------------|
| Async complexity in REPL | Use `asyncio.run()` per command |
| Readline limitations | Fall back to prompt_toolkit if needed |
| Context router inconsistency | Unified routing via Logos |

---

## Next Actions

Wave 2 QA Complete. Next steps:

1. **Wave 3 PLAN**: Scope LLM integration, tutorial mode
2. **MEASURE**: Instrument with telemetry for usage patterns
3. **EDUCATE**: Add tutorial mode (`kgents -i --tutorial`)
4. **Branch**: Consider REPL-as-TUI evolution (Textual)

---

## Branch Candidates (surfaced during implementation)

| Candidate | Classification | Action |
|-----------|----------------|--------|
| REPL-as-TUI | PARALLEL | Could evolve into Textual app |
| Voice REPL | DEFERRED | Voice input for accessibility |
| Web REPL | DEFERRED | Browser-based exploration |

---

## Wave 2 Test Coverage (2025-12-14)

**Total Tests**: 44 new tests in `protocols/cli/_tests/test_repl.py`

| Category | Tests | Coverage |
|----------|-------|----------|
| Observer Switching | 7 | `/observer`, `/observers`, prompt indicator |
| Navigation | 8 | Contexts, holons, `..`, `/`, `.` |
| Pipeline Execution | 4 | `>>` composition, CLI fallback |
| Error Sympathy | 3 | Suggestions, unknown paths |
| Introspection | 4 | `?`, `??`, context-specific help |
| Tab Completion | 4 | Contexts, holons, commands, archetypes |
| Rich Rendering | 6 | Dict, list, string, None, BasicRendering |
| Graceful Degradation | 2 | Logos unavailable, Umwelt unavailable |
| State Management | 4 | Initial state, history, cache invalidation |
| Integration | 2 | Full navigation flow, observer→umwelt |

---

## Wave 5 Test Coverage (2025-12-14)

**Total Tests**: 16 new tests

| Test Class | Tests | Coverage |
|------------|-------|----------|
| TestAmbientModeFlag | 2 | --ambient flag parsing, state attributes |
| TestAmbientScreenRendering | 4 | Returns string, shows K-gent, metabolism, pause |
| TestAmbientKeyBindings | 4 | q/r/space/1-5 keys |
| TestAmbientRefreshLoop | 2 | Default interval, configurable |
| TestAmbientNonBlockingKeyboard | 2 | Function exists, returns correctly |
| TestAmbientHelpText | 2 | Mentions ambient, mentions waves |

---

## Total Test Count

| Wave | Tests | Status |
|------|-------|--------|
| Wave 2 | 44 | ✅ |
| Wave 2.5 | 29 | ✅ |
| Wave 3 | 25 | ✅ |
| Wave 4 | 23 | ✅ |
| Wave 5 | 16 | ✅ |
| Wave 5.1 | 12 | ✅ (dotted completion) |
| Wave 6 (Guide) | 82 | ✅ (repl_guide.py) |
| Wave 6 (Tutorial) | 54 | ✅ (repl_tutorial.py) |
| Wave 7 (Mastery) | 4 | ✅ (mastery tier skills) |
| **Total** | **289** | **All passing, mypy clean** |

---

⟿[REFLECT]
