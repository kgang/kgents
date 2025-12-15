# AGENTESE REPL Wave 4: Joy-Inducing Polish

> *"The REPL should feel like a friend, not a tool."*

## ATTACH

/hydrate

You are entering the **PLAN phase** of **Wave 4 (Joy-Inducing)** for the AGENTESE REPL Crown Jewel.

---

## Prior Context

**Completed Waves**:
- Wave 1 (Foundation): Core REPL, navigation, tab completion, history
- Wave 2 (Integration): Async Logos, pipelines, observer context, rich output, error sympathy (44 tests)
- Wave 2.5 (Hardening): Edge cases, security, performance, stress tests (+29 tests = 73 total)
- Wave 3 (Intelligence): Fuzzy matching, LLM suggestions, session persistence, script mode (+24 tests = 97 total)

**Current State**:
- Test count: 97 passing
- Files: `repl.py`, `repl_fuzzy.py`, `repl_session.py`
- Mypy: 0 errors
- Forest health: AGENTESE REPL at 65%

**Kent's Wishes** (from `_focus.md`):
- AGENTESE REPL == EVERYTHING
- BEST IN CLASS UX/DEVEX
- COMPOSITIONAL GENERATIVE VISUALIZATIONS. BEAUTIFUL ASCII.
- Being/having fun is free :)

---

## Mission: Wave 4 Joy-Inducing

Transform the REPL from *functional* to *delightful*. This is the **personality layer**.

### Chunks (J1-J5)

| Chunk | Description | Entropy | Dependencies |
|-------|-------------|---------|--------------|
| **J1** | Welcome variations (time-of-day, returning user) | 0.01 | None |
| **J2** | K-gent personality integration (soulful responses) | 0.02 | K-gent soul |
| **J3** | Easter eggs (hidden delights) | 0.01 | J2 |
| **J4** | Ambient mode (passive dashboard) | 0.01 | Dashboard |
| **J5** | Contextual hints (proactive suggestions) | 0.01 | J2 |

**Total Entropy Budget**: 0.06

---

## Chunk Details

### J1: Welcome Variations

Context-aware greetings that acknowledge time and history.

```python
WELCOME_VARIANTS = {
    "morning": [
        "Good morning. The forest awaits.",
        "Dawn breaks. What shall we explore?",
    ],
    "afternoon": [
        "Good afternoon. Where to?",
        "The day is young. Navigate wisely.",
    ],
    "evening": [
        "Good evening. The stars are watching.",
        "Night falls. Perfect time to explore the void.",
    ],
    "returning": [
        "Welcome back. You were in {last_context}.",
        "Resuming from {last_path}. The river continues.",
    ],
}
```

**Exit**: Welcome varies by time and session history.

### J2: K-gent Personality Integration

Certain commands route to K-gent soul for soulful responses.

```python
KGENT_TRIGGERS = ["reflect", "advice", "feeling", "wisdom", "meaning"]

async def maybe_invoke_kgent(cmd: str) -> str | None:
    """Route philosophical queries to K-gent soul."""
    if any(trigger in cmd.lower() for trigger in KGENT_TRIGGERS):
        response = await soul.dialogue(cmd)
        return f"\033[35m{response}\033[0m"  # Purple for K-gent
    return None
```

**Exit**: K-gent responds contextually (rate-limited to 1 per 5 commands).

### J3: Easter Eggs

Hidden commands discovered naturally by curious users.

| Trigger | Response |
|---------|----------|
| `void.entropy.dance` | ASCII animation (spinning entropy gauge) |
| `self.soul.sing` | Haiku about current context |
| `concept.zen` | Random principle from spec/principles.md |
| `time.flow` | Animated time visualization |
| `world.hello` | "Hello, World!" (classic) |
| `..........` | "You've gone too far. Here there be dragons." |

**Exit**: At least 5 easter eggs implemented.

### J4: Ambient Mode

`kg -i --ambient` runs REPL as passive dashboard.

```python
def run_ambient_mode():
    """Passive dashboard showing system pulse."""
    while running:
        clear_screen()
        print_status_panel()    # System health
        print_recent_traces()   # Last 5 traces
        print_entropy_gauge()   # Accursed share
        print_forest_pulse()    # Active plans
        sleep(5)  # Refresh interval
```

**Exit**: Ambient mode works with `--ambient` flag.

### J5: Contextual Hints

Proactive suggestions based on user behavior.

```python
def get_contextual_hint(state: ReplState) -> str | None:
    # Long session without navigation
    if len(state.history) > 20 and state.path == []:
        return "Hint: Try 'self status' for a system overview"

    # In void context
    if state.path == ["void"]:
        return "Hint: 'entropy sip' draws from the Accursed Share"

    # Repeated failures
    if state._consecutive_errors > 3:
        return "Hint: Try '?' to see available affordances"
```

**Exit**: Hints appear when contextually appropriate.

---

## Exit Criteria (Wave 4)

1. Welcome message varies by time of day and session history
2. K-gent personality responds to philosophical queries (rate-limited)
3. At least 5 easter eggs discoverable naturally
4. Ambient mode shows live system status (`--ambient` flag)
5. Contextual hints guide stuck users proactively
6. New tests: ~15-20 (bringing total to ~115)
7. User delight score: > 4.5/5 (if surveyed)

---

## Non-Goals (Wave 4)

- New core functionality (defer to Wave 5+)
- Performance optimizations
- Breaking changes to Wave 1-3 APIs
- Changing existing test behavior

---

## N-Phase Execution

### This Session: PLAN Phase

**Actions**:
1. Review this scope (J1-J5 chunks)
2. Identify any missing dependencies
3. Allocate entropy budget
4. Confirm exit criteria
5. Generate RESEARCH continuation

**Exit**: PLAN complete when scope is agreed and dependencies mapped.

### Next Phases

| Phase | Focus |
|-------|-------|
| RESEARCH | K-gent soul API, dashboard patterns, existing personality touchpoints |
| DEVELOP | Design `PersonalityLayer`, welcome algorithm, ambient refresh cycle |
| STRATEGIZE | J1 first, J5 parallel, J2 after, J3 after J2, J4 last |
| IMPLEMENT | TDD: tests first, then implementation |
| QA | Test welcome variations, K-gent rate limiting, easter eggs |
| TEST | Full suite, startup performance < 100ms |
| EDUCATE | `--help` updates, internal easter egg docs |
| MEASURE | Welcome variation coverage, K-gent invocation rate |
| REFLECT | What landed? What felt forced? Archive learnings. |

---

## Phase Ledger

```yaml
path: plans/devex/agentese-repl-crown-jewel
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
| **Tasteful** | Personality is subtle, not forced |
| **Joy-Inducing** | This IS the joy wave |
| **Curated** | Only 5 easter eggs, not 50 |
| **Composable** | Personality layer composes with existing REPL |
| **Generative** | Easter eggs generate surprise and delight |

---

## Quick Commands

```bash
# Run current tests
cd impl/claude && uv run pytest protocols/cli/_tests/test_repl.py -v

# Check K-gent soul availability
cd impl/claude && uv run python -c "from agents.k.soul import KgentSoul; print('KgentSoul available')"

# Check dashboard availability
cd impl/claude && uv run python -c "from protocols.cli.handlers.dashboard import cmd_dashboard; print('dashboard available')"
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
handles: scope=wave4_joy; chunks=J1-J5; exit=personality_working; ledger={PLAN:touched}; entropy=0.06
mission: study K-gent soul API for dialogue integration; audit dashboard patterns for ambient mode reuse; grep for existing personality/welcome/easter patterns in codebase.
actions:
  - Read(agents/k/soul.py) — understand dialogue API
  - Read(protocols/cli/handlers/dashboard.py) — ambient mode reuse
  - Grep("welcome|personality|easter|greeting") — existing patterns
  - Document integration points for J1-J5
exit: integration points mapped; K-gent dialogue API documented; dashboard reuse clear; continuation → DEVELOP.
```

---

*This is the **PLAN PHASE** for AGENTESE REPL Wave 4: Joy-Inducing. Upon completion, generate the RESEARCH phase continuation with the auto-inducer `⟿[RESEARCH]`.*

⟿[RESEARCH]
