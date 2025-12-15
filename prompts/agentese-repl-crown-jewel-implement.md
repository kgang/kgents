# AGENTESE REPL Crown Jewel: IMPLEMENT Phase

> *"The interface that teaches its own structure through use is no interface at all."*

**Phase**: IMPLEMENT (Wave 2: COMPLETE ✅)
**Plan**: `plans/devex/agentese-repl-crown-jewel.md`
**Ledger**: `{PLAN:touched, RESEARCH:touched, DEVELOP:skipped, STRATEGIZE:touched, IMPLEMENT:complete}`
**Entropy**: 0.07

---

## Context

Wave 1 of the AGENTESE REPL is COMPLETE:
- Core REPL engine with readline
- Five-context navigation (self, world, concept, void, time)
- Tab completion with dynamic holons
- History persistence to `~/.kgents_repl_history`
- Introspection (`?` and `??`)
- Composition parsing (`>>`)
- Wired to `kg -i` / `kg --interactive`

**Architectural Decision**: AD-007 added to `spec/principles.md`

---

## Wave 2 Scope: Deep Integration

Transform the REPL from a navigation shell into a full AGENTESE citizen.

### Tasks (Ordered by Priority)

| # | Task | Exit Criterion | Effort |
|---|------|----------------|--------|
| 1 | **Async execution via Logos** | `await logos.invoke(path, observer)` works in REPL | M |
| 2 | **Pipeline execution** | `world.agents.list >> concept.count` actually runs | M |
| 3 | **Observer/Umwelt context** | Affordances change based on current observer | S |
| 4 | **Rich output rendering** | Tables, panels, colored output via `rich` | S |
| 5 | **Error sympathy** | Errors suggest next actions, not just fail | S |

### Implementation Strategy

1. **Async Execution**
   - Wrap command execution in `asyncio.run()` per command
   - Import and use `Logos` resolver properly
   - Pass observer context through the chain

2. **Pipeline Execution**
   - Parse `>>` into path list
   - Execute sequentially, passing output as input
   - Emit intermediate results if verbose

3. **Observer Context**
   - Add `/observer <archetype>` command to switch
   - Default to "explorer" archetype
   - Show current observer in prompt or status

4. **Rich Output**
   - Use `rich.console` for tables and panels
   - Style output by context (green for self, blue for world, etc.)
   - Respect `--no-color` flag

---

## Non-Goals (Wave 2)

- LLM integration (Wave 3)
- Voice input (Future)
- Web REPL (Future)
- Session persistence beyond history (Future)

---

## Files to Modify

| File | Changes |
|------|---------|
| `protocols/cli/repl.py` | Async execution, pipeline running, rich output |
| `protocols/agentese/logos.py` | Ensure REPL-compatible invoke |
| `protocols/cli/hollow.py` | None (already wired) |

---

## QA Checklist

- [ ] `kg -i` launches successfully
- [ ] Can navigate all five contexts
- [ ] Tab completion works for holons
- [ ] `?` shows affordances at each level
- [ ] `self status` invokes and shows output
- [ ] `world agents list` invokes and shows output
- [ ] `>>` composition parses correctly
- [ ] History persists across sessions
- [ ] Ctrl+C doesn't crash (shows hint)
- [ ] `exit` leaves cleanly

---

## Success Metrics

| Metric | Target |
|--------|--------|
| Commands that work end-to-end | 100% of context routers |
| Pipeline execution | At least 2-path pipelines work |
| Error clarity | All errors suggest next action |

---

## Branch Candidates (to surface)

- REPL tutorial mode (`--tutorial`)
- REPL-to-TUI evolution
- Voice REPL for accessibility

---

## Continuation Protocol

After completing Wave 2:

1. **QA**: Run full checklist, fix issues
2. **TEST**: Add integration tests for REPL
3. **EDUCATE**: Document in `docs/skills/cli-command.md`
4. **MEASURE**: Instrument for usage telemetry
5. **REFLECT**: Capture learnings, seed Wave 3

---

## Invocation

```
/hydrate
handles: plan=plans/devex/agentese-repl-crown-jewel.md; ledger={IMPLEMENT:in_progress}; entropy=0.07
mission: Complete Wave 2 (async Logos integration, pipeline execution, rich output).
exit: QA checklist passes; continuation → QA phase.
```

---

⟿[IMPLEMENT]
