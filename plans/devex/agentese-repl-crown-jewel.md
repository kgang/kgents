# AGENTESE REPL: Crown Jewel Plan

> *"The interface that teaches its own structure through use is no interface at all."*

**Status**: REFLECT phase (Wave 2 QA complete)
**Progress**: 75%
**Last Touched**: 2025-12-14
**Phase Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:skipped, STRATEGIZE:touched, IMPLEMENT:touched, QA:touched, TEST:touched}`
**Entropy Budget**: 0.05

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

### Not Yet Implemented

| Component | Priority | Notes |
|-----------|----------|-------|
| Fuzzy matching for paths | LOW | Typo tolerance |
| Session state persistence | LOW | Resume from last location |
| LLM suggestions | FUTURE | "Did you mean..." with semantic understanding |
| Tutorial mode | FUTURE | `--tutorial` flag |

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

### Phase 3: Intelligence (FUTURE)

| Task | Description |
|------|-------------|
| LLM suggestions | "Did you mean..." with semantic understanding |
| Auto-complete from Logos | Dynamic completion from registry |
| Command history search | Fuzzy search through history |
| Session replay | Re-run previous exploration paths |

### Phase 4: Joy-Inducing Polish (FUTURE)

| Task | Description |
|------|-------------|
| Welcome variations | Context-aware greetings |
| Easter eggs | Hidden commands for delight |
| Personality integration | K-gent can respond in REPL |
| Ambient mode | REPL as passive dashboard |

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

⟿[REFLECT]
