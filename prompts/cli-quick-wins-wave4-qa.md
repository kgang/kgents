# CLI Quick Wins Wave 4: QA Phase

> *"Gatekeeping for quality, hygiene, and readiness before formal testing."*

## ATTACH

/hydrate

You are entering the **QA phase** of **CLI Quick Wins Wave 4**.

---

## Prior Context

**IMPLEMENT Complete**:
- 9 handlers implemented in `protocols/cli/handlers/`
- 50 tests passing in `test_wave4_joy.py`
- Context routers wired (void, concept, world, self)
- hollow.py registration complete
- REPL slash shortcuts with tab completion

**Commands Shipped**:
| Command | Path | Handler |
|---------|------|---------|
| `sparkline` | `world.viz.sparkline` | `sparkline.py` |
| `challenge` | `self.soul.challenge` | `challenge.py` |
| `oblique` | `concept.creativity.oblique` | `oblique.py` |
| `constrain` | `concept.creativity.constrain` | `constrain.py` |
| `yes-and` | `concept.creativity.expand` | `yes_and.py` |
| `surprise-me` | `void.serendipity.prompt` | `surprise_me.py` |
| `project` | `void.shadow.project` | `project.py` |
| `why` | `self.soul.why` | `why.py` |
| `tension` | `self.soul.tension` | `tension.py` |

**Epilogues**:
- `_epilogues/2025-12-14-cli-quick-wins-wave4-cross-synergize.md`
- `_epilogues/2025-12-14-cli-quick-wins-wave4-implement.md`

---

## Mission: QA Pass

Verify the work is clean, explainable, and reversible before TEST phase.

### QA Checklist

```markdown
## Static Analysis
- [ ] mypy passes: `uv run mypy protocols/cli/handlers/{sparkline,challenge,oblique,constrain,yes_and,surprise_me,project,why,tension}.py`
- [ ] ruff passes: `uv run ruff check protocols/cli/handlers/`
- [ ] No new security vulnerabilities (no user input → eval, no path traversal)

## Functional Verification
- [ ] CLI invocation works: `kg oblique`, `kg sparkline 1 2 3`, etc.
- [ ] Context routing works: `kg concept creativity oblique`
- [ ] REPL shortcuts work: `/oblique`, `/sparkline 1 2 3`
- [ ] Pipeline composition works: `tension >> sparkline` (REPL)
- [ ] Help flags work: `kg oblique --help`

## Graceful Degradation
- [ ] Commands work without LLM (template fallbacks)
- [ ] Missing dependencies produce helpful error messages
- [ ] Rate limiting on K-gent integration works

## Documentation Hygiene
- [ ] Plans touched: `plans/devex/cli-quick-wins-wave4.md`
- [ ] Archive candidates: (assess after QA)
- [ ] Spec promotion candidates: (assess after QA)

## Rollback Plan
- [ ] All changes are additive (no breaking changes)
- [ ] Handlers can be removed by deleting files + registry entries
- [ ] No migrations required
```

---

## Actions

1. **Run static analysis**:
   ```bash
   cd impl/claude
   uv run mypy protocols/cli/handlers/sparkline.py protocols/cli/handlers/oblique.py protocols/cli/handlers/constrain.py protocols/cli/handlers/yes_and.py protocols/cli/handlers/surprise_me.py protocols/cli/handlers/project.py protocols/cli/handlers/why.py protocols/cli/handlers/tension.py protocols/cli/handlers/challenge.py
   uv run ruff check protocols/cli/handlers/
   ```

2. **Test CLI invocations** (manual verification):
   ```bash
   kg oblique
   kg sparkline 1 2 3 4 5
   kg constrain "API design"
   kg yes-and "code as poetry"
   kg surprise-me --domain code
   kg project "They're so disorganized"
   kg why "Tests should pass"
   kg tension --system
   kg challenge --help
   ```

3. **Test REPL shortcuts**:
   ```bash
   kg -i
   # Then: /oblique, /sparkline 1 2 3, /surprise, etc.
   ```

4. **Test pipeline composition** (REPL):
   ```
   [root] » tension >> sparkline
   # Should show tension severities as sparkline
   ```

5. **Verify degraded mode**:
   - Commands work without `--llm` flag
   - K-gent integration gracefully handles missing LLM

6. **Security sweep**:
   - No `eval()` or `exec()` on user input
   - No path traversal vulnerabilities
   - Input length limits respected

7. **Document findings** in QA epilogue

---

## Exit Criteria

- [ ] mypy: 0 errors on new handlers
- [ ] ruff: 0 errors/warnings on new handlers
- [ ] All 9 commands work via CLI
- [ ] All slash shortcuts work in REPL
- [ ] Pipeline composition verified
- [ ] Degraded mode verified
- [ ] Security sweep clean
- [ ] QA epilogue written

---

## Phase Ledger

```yaml
phase_ledger:
  PLAN: touched
  RESEARCH: touched
  DEVELOP: touched
  STRATEGIZE: touched
  CROSS-SYNERGIZE: touched
  IMPLEMENT: touched
  QA: pending  # This session
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.12
  remaining: 0.03
  qa_sip: 0.02
```

---

## Branch Check

| Type | Candidate | Classification |
|------|-----------|----------------|
| Refactor | Template consolidation across handlers | deferred |
| Feature | LLM mode for all commands | parallel (future wave) |
| Infra | Pipeline preset registry | deferred |

---

## Risk Sweep

| Risk | Mitigation |
|------|------------|
| Type errors in new handlers | mypy pass required |
| Security in user input handling | Input length limits, no eval |
| Breaking existing tests | New test file only, no modifications |
| Rollback difficulty | Additive changes only |

---

## Continuation Generator

Upon completing QA, emit the TEST continuation:

```markdown
⟿[TEST]
/hydrate
handles: qa=passed; static=clean; security=clean; degraded=verified; findings=${qa_findings}; ledger={QA:touched}; entropy=0.01
mission: Design/run tests that prove grammar + invariants; prefer hotdata; record repros.
actions:
  - Verify 50 existing tests still pass
  - Add edge case tests (empty input, malformed args)
  - Add integration tests (CLI → handler → output)
  - Test REPL shortcut routing
  - uv run pytest protocols/cli/handlers/_tests/test_wave4_joy.py -v
exit: Tests aligned to risks; ledger.TEST=touched; repro notes captured; continuation → EDUCATE.
```

### Halt Conditions

```markdown
⟂[QA:blocked] mypy/ruff errors require resolution before TEST
⟂[BLOCKED:security_issue] Security vulnerability detected; human review required
⟂[ENTROPY_DEPLETED] Budget exhausted without entropy sip
```

---

## Quick Commands

```bash
# Static analysis
cd impl/claude && uv run mypy protocols/cli/handlers/sparkline.py --ignore-missing-imports
cd impl/claude && uv run ruff check protocols/cli/handlers/

# Run tests
cd impl/claude && uv run pytest protocols/cli/handlers/_tests/test_wave4_joy.py -v

# Manual CLI tests
kg oblique
kg sparkline 10 20 15 25 30
kg constrain "API design" --count 3
kg why "We need microservices" --depth 3
```

---

## Principles Alignment

| Principle | QA Check |
|-----------|----------|
| **Tasteful** | Commands produce thoughtful, not noisy output |
| **Curated** | Only 9 commands, not 50 variations |
| **Ethical** | No silent failures, clear error messages |
| **Joy-Inducing** | Commands delight users |
| **Transparent** | Help flags explain functionality |

---

*This is the **QA PHASE** for CLI Quick Wins Wave 4. Upon completion, generate the TEST phase continuation with the auto-inducer `⟿[TEST]}` or halt with `⟂[QA:blocked]` if issues found.*

⟿[QA]
