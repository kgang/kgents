---
path: plans/devex/agentese-repl-master-plan
status: active
progress: 5
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables:
  - k-gent-ambient
  - pedagogical-cli
  - discoverability
  - agentese-universal-protocol
session_notes: |
  Master plan for AGENTESE REPL: Wave 2.5 (Hardening) + Wave 3 (Intelligence) + Wave 4 (Joy)
phase_ledger:
  PLAN: touched
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: pending
  CROSS-SYNERGIZE: pending
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: pending
  REFLECT: pending
entropy:
  planned: 0.15
  spent: 0.02
  returned: 0.0
---

# AGENTESE REPL Master Plan: Waves 2.5 → 3 → 4

> *"The interface that teaches its own structure through use is no interface at all."*

**Crown Jewel**: Yes (multi-session, high-complexity)
**Entropy Budget**: 0.15 (15% for exploration across all waves)
**Attention Budget**: 60% primary focus when active

---

## Executive Summary

This plan orchestrates the evolution of the AGENTESE REPL from a solid foundation (Waves 1-2) into an intelligent, joy-inducing interface that becomes the primary way users interact with the kgents ecosystem.

| Wave | Theme | Exit Criterion | Sessions |
|------|-------|----------------|----------|
| **2.5** | Hardening | 95% test coverage, stress tested, security audited | 1-2 |
| **3** | Intelligence | LLM suggestions working, fuzzy matching, dynamic completion | 3-5 |
| **4** | Joy-Inducing | K-gent personality integrated, easter eggs, ambient mode | 2-3 |

---

## Current State

### Completed (Waves 1-2)

| Feature | Tests | Status |
|---------|-------|--------|
| Core REPL loop | 4 | Stable |
| Five-context navigation | 8 | Stable |
| Tab completion | 4 | Stable |
| History persistence | 1 | Stable |
| Async Logos execution | 2 | Stable |
| Pipeline execution (`>>`) | 4 | Stable |
| Observer/Umwelt switching | 7 | Stable |
| Rich output rendering | 6 | Stable |
| Error sympathy | 3 | Stable |
| Graceful degradation | 2 | Stable |
| State management | 4 | Stable |
| **Total** | **44** | **Wave 2 Complete** |

### Gaps Identified

| Gap | Risk | Wave |
|-----|------|------|
| No edge case tests (long paths, unicode, special chars) | Medium | 2.5 |
| No concurrent access testing | Low | 2.5 |
| No security audit (input sanitization) | High | 2.5 |
| No performance benchmarks | Medium | 2.5 |
| No LLM integration | — | 3 |
| No fuzzy matching | — | 3 |
| No personality layer | — | 4 |

---

## Wave 2.5: Hardening

> *"Make it unbreakable before making it smart."*

### Non-Goals (Wave 2.5)

- New features (defer to Wave 3)
- UI changes
- Architecture refactoring

### Exit Criteria

1. Test coverage ≥ 95% for `repl.py`
2. Stress test: 1000 commands in rapid succession
3. Security audit: all user inputs sanitized
4. Performance: startup < 100ms, command < 50ms
5. Edge cases: unicode, long paths, special characters

### Chunks

| Chunk | Effort | Dependencies | Owner |
|-------|--------|--------------|-------|
| H1: Edge case test suite | 2h | None | Agent |
| H2: Security audit + fixes | 2h | H1 | Agent |
| H3: Performance benchmarks | 1h | H1 | Agent |
| H4: Stress testing | 1h | H1-H3 | Agent |
| H5: Documentation audit | 1h | H4 | Agent |

### H1: Edge Case Test Suite

**Scope**: Add tests for untested paths and edge conditions.

```python
# Test categories to add:
class TestEdgeCases:
    def test_unicode_in_path(self): ...
    def test_very_long_path(self): ...
    def test_special_characters_in_input(self): ...
    def test_empty_input_handling(self): ...
    def test_whitespace_only_input(self): ...
    def test_rapid_command_sequence(self): ...
    def test_history_file_corruption_recovery(self): ...
    def test_readline_unavailable(self): ...

class TestConcurrency:
    def test_umwelt_cache_thread_safety(self): ...
    def test_logos_concurrent_invocations(self): ...

class TestRecovery:
    def test_logos_timeout_recovery(self): ...
    def test_cli_fallback_chain(self): ...
    def test_partial_pipeline_failure(self): ...
```

### H2: Security Audit

**Scope**: Audit all user input paths for injection vulnerabilities.

| Input Point | Risk | Mitigation |
|-------------|------|------------|
| Path parsing | Command injection | Allowlist contexts/holons |
| Observer name | Arbitrary code | Enum validation |
| Pipeline composition | Path traversal | Sanitize `.` and `/` |
| History file | File injection | Fixed path, no user input |

### H3: Performance Benchmarks

**Scope**: Establish baselines and add to CI.

```python
# benchmarks/test_repl_perf.py
def test_startup_time():
    """REPL should start in < 100ms."""

def test_command_latency():
    """Single command should complete in < 50ms."""

def test_completion_latency():
    """Tab completion should respond in < 20ms."""
```

### H4: Stress Testing

**Scope**: Verify stability under load.

```python
def test_rapid_fire_commands():
    """1000 commands in succession should not crash."""

def test_memory_leak_detection():
    """Memory should be stable after 10000 commands."""
```

---

## Wave 3: Intelligence

> *"The REPL should anticipate, not just respond."*

### Non-Goals (Wave 3)

- Personality/emotional responses (Wave 4)
- Visual changes beyond minimal
- Breaking changes to Wave 1-2 APIs

### Exit Criteria

1. LLM suggestions work for typos and semantic matches
2. Fuzzy matching catches 90% of typos
3. Dynamic completion from live Logos registry
4. Session persistence works across restarts
5. Script mode (`kg -i < script.repl`) functional

### Chunks

| Chunk | Effort | Dependencies | Owner |
|-------|--------|--------------|-------|
| I1: Fuzzy matching engine | 3h | Wave 2.5 | Agent |
| I2: LLM suggestion integration | 4h | I1 | Agent |
| I3: Dynamic Logos completion | 2h | I1 | Agent |
| I4: Session persistence | 2h | None | Agent |
| I5: Script mode | 2h | None | Agent |
| I6: Command history search | 2h | I1 | Agent |

### I1: Fuzzy Matching Engine

**Scope**: Implement typo-tolerant path resolution.

```python
# protocols/cli/repl_fuzzy.py
from rapidfuzz import fuzz, process

class FuzzyMatcher:
    """Typo-tolerant path matching with configurable threshold."""

    def __init__(self, threshold: int = 80):
        self.threshold = threshold

    def match(self, query: str, candidates: list[str]) -> list[tuple[str, int]]:
        """Return matches above threshold with confidence scores."""
        return process.extract(query, candidates, scorer=fuzz.ratio, score_cutoff=self.threshold)

    def suggest(self, query: str, candidates: list[str]) -> str | None:
        """Return best suggestion or None."""
        matches = self.match(query, candidates)
        return matches[0][0] if matches else None
```

**Integration Point**: `handle_navigation` and `handle_invocation` call fuzzy matcher on failure.

### I2: LLM Suggestion Integration

**Scope**: Use LLM for semantic "did you mean" suggestions.

```python
# Architecture:
# 1. Try exact match
# 2. Try fuzzy match
# 3. If both fail AND entropy budget allows, try LLM

class LLMSuggester:
    """Semantic suggestion engine using lightweight LLM."""

    async def suggest(self, query: str, context: str, entropy: float) -> str | None:
        """
        Generate semantic suggestion.

        Only called when:
        - Exact match fails
        - Fuzzy match fails
        - Entropy budget > 0.01 (costs entropy)
        """
        if entropy < 0.01:
            return None

        # Use haiku for speed/cost
        response = await self._llm.complete(
            f"User typed '{query}' in context '{context}'. "
            f"Valid options: {self._get_valid_options(context)}. "
            f"Suggest the most likely intended command (one word only):"
        )
        return response.strip()
```

**Entropy Cost**: 0.01 per LLM suggestion.

### I3: Dynamic Logos Completion

**Scope**: Tab completion queries live Logos registry.

```python
class DynamicCompleter(Completer):
    """Tab completion with live Logos registry queries."""

    def _get_matches(self, text: str) -> list[str]:
        # Static matches (fast)
        static = super()._get_matches(text)

        # Dynamic matches from Logos (if available)
        if self.state._logos:
            try:
                registry = self.state._logos.get_registry()
                dynamic = [p for p in registry.paths if p.startswith(text)]
                return sorted(set(static + dynamic))
            except Exception:
                pass  # Graceful degradation

        return static
```

### I4: Session Persistence

**Scope**: Save and restore REPL state across restarts.

```python
# ~/.kgents_repl_session.json
{
    "path": ["self", "soul"],
    "observer": "developer",
    "last_result_type": "dict",
    "timestamp": "2025-12-14T10:30:00Z"
}

# Restoration:
def restore_session(state: ReplState) -> bool:
    """Restore previous session state. Returns True if restored."""
    session_file = Path.home() / ".kgents_repl_session.json"
    if session_file.exists():
        data = json.loads(session_file.read_text())
        state.path = data.get("path", [])
        state.observer = data.get("observer", "explorer")
        return True
    return False
```

### I5: Script Mode

**Scope**: Execute REPL scripts non-interactively.

```bash
# Usage:
kg -i < my_script.repl
kg -i --script my_script.repl

# my_script.repl:
self
status
..
world
agents list
exit
```

```python
def run_repl(script: Path | None = None, ...):
    """Run REPL in interactive or script mode."""
    if script:
        commands = script.read_text().splitlines()
        for cmd in commands:
            if cmd.strip() and not cmd.startswith("#"):
                result = process_command(state, cmd)
                print(result)
        return 0
    else:
        # Interactive mode (existing)
        ...
```

### I6: Command History Search

**Scope**: Fuzzy search through command history.

```python
# Ctrl+R behavior:
def search_history(query: str, history: list[str]) -> list[str]:
    """Fuzzy search through command history."""
    return [cmd for cmd in history if query.lower() in cmd.lower()]

# Rich display:
def show_history_search(matches: list[str], query: str):
    """Display matching history entries with highlighting."""
    for i, match in enumerate(matches[-10:], 1):
        highlighted = match.replace(query, f"\033[33m{query}\033[0m")
        print(f"  {i:3}  {highlighted}")
```

---

## Wave 4: Joy-Inducing Polish

> *"The REPL should feel like a friend, not a tool."*

### Non-Goals (Wave 4)

- New functionality (defer to future waves)
- Performance changes
- Breaking changes

### Exit Criteria

1. K-gent personality responds contextually in REPL
2. Welcome message varies by time of day and session history
3. At least 5 easter eggs discovered naturally
4. Ambient mode shows live system status
5. User delight score > 4.5/5 (survey)

### Chunks

| Chunk | Effort | Dependencies | Owner |
|-------|--------|--------------|-------|
| J1: Welcome variations | 2h | None | Agent |
| J2: K-gent personality integration | 4h | K-gent soul | Agent |
| J3: Easter eggs | 2h | J2 | Agent |
| J4: Ambient mode | 3h | Dashboard | Agent |
| J5: Contextual hints | 2h | J2 | Agent |

### J1: Welcome Variations

**Scope**: Context-aware greetings.

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

def get_welcome() -> str:
    """Get contextual welcome message."""
    hour = datetime.now().hour
    if hour < 12:
        pool = WELCOME_VARIANTS["morning"]
    elif hour < 17:
        pool = WELCOME_VARIANTS["afternoon"]
    else:
        pool = WELCOME_VARIANTS["evening"]

    return random.choice(pool)
```

### J2: K-gent Personality Integration

**Scope**: K-gent soul can respond to certain commands.

```python
# Commands that invoke K-gent:
KGENT_TRIGGERS = ["reflect", "advice", "feeling", "wisdom"]

async def maybe_invoke_kgent(state: ReplState, cmd: str) -> str | None:
    """Check if command should route to K-gent soul."""
    if any(trigger in cmd.lower() for trigger in KGENT_TRIGGERS):
        try:
            from agents.k.soul import KgentSoul
            soul = KgentSoul()
            response = await soul.dialogue(cmd)
            return f"\033[35m{response}\033[0m"  # Purple for K-gent
        except Exception:
            return None
    return None
```

### J3: Easter Eggs

**Scope**: Hidden delights for curious users.

| Trigger | Response |
|---------|----------|
| `void.entropy.dance` | ASCII animation |
| `self.soul.sing` | Haiku about the current context |
| `concept.zen` | Random principle from spec/principles.md |
| `time.flow` | Animated time visualization |
| `world.hello` | "Hello, World! 🌍" (the only emoji) |

### J4: Ambient Mode

**Scope**: REPL as passive dashboard.

```python
# kg -i --ambient
def run_ambient_mode(state: ReplState):
    """Run REPL in ambient mode - passive status display."""
    while state.running:
        clear_screen()
        print_status_panel()  # System health
        print_recent_traces()  # Last 5 traces
        print_entropy_gauge()  # Accursed share status
        time.sleep(5)  # Refresh every 5s
```

### J5: Contextual Hints

**Scope**: Proactive suggestions based on context.

```python
def get_contextual_hint(state: ReplState) -> str | None:
    """Generate contextual hint based on current state."""

    # Long session without navigation
    if len(state.history) > 20 and state.path == []:
        return "Hint: Try 'self status' for a system overview"

    # In void context
    if state.path == ["void"]:
        return "Hint: 'entropy sip' draws from the Accursed Share"

    # Repeated failures
    if state._consecutive_errors > 3:
        return "Hint: Try '?' to see available affordances"

    return None
```

---

## N-Phase Execution Plan

### Wave 2.5 Phases

```
PLAN (this doc) → RESEARCH (codebase audit) → DEVELOP (test design)
       ↓
STRATEGIZE (chunk ordering) → IMPLEMENT (tests + fixes) → QA (coverage check)
       ↓
TEST (run full suite) → EDUCATE (update docs) → MEASURE (coverage %) → REFLECT
```

### Wave 3 Phases

```
PLAN (I1-I6 scope) → RESEARCH (LLM options, fuzzy libs) → DEVELOP (API design)
       ↓
STRATEGIZE (parallel: I4,I5 || sequential: I1→I2→I3→I6) → IMPLEMENT
       ↓
QA → TEST → EDUCATE (tutorial mode doc) → MEASURE → REFLECT
```

### Wave 4 Phases

```
PLAN (J1-J5 scope) → RESEARCH (K-gent integration points) → DEVELOP (personality API)
       ↓
STRATEGIZE (J1 first, J4 last) → IMPLEMENT → QA → TEST
       ↓
EDUCATE (easter egg hints) → MEASURE (delight survey) → REFLECT
```

---

## Dependency Graph

```
Wave 2.5 (Hardening)
├── H1: Edge cases ──┬── H2: Security
│                    ├── H3: Performance
│                    └── H4: Stress test ── H5: Doc audit
│
Wave 3 (Intelligence) [depends on Wave 2.5]
├── I1: Fuzzy matching ──┬── I2: LLM suggestions
│                        ├── I3: Dynamic completion
│                        └── I6: History search
├── I4: Session persistence (parallel)
└── I5: Script mode (parallel)
│
Wave 4 (Joy) [depends on Wave 3, K-gent soul]
├── J1: Welcome variations (parallel)
├── J2: K-gent integration ──┬── J3: Easter eggs
│                            └── J5: Contextual hints
└── J4: Ambient mode (depends on dashboard)
```

---

## Risk Matrix

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| LLM latency degrades UX | Medium | High | Async with timeout, cached suggestions |
| Fuzzy matching false positives | Medium | Medium | Configurable threshold, user confirmation |
| K-gent personality too chatty | Low | Medium | Rate limiting, opt-out flag |
| Security vulnerabilities | Low | High | Input sanitization, allowlists |
| Ambient mode resource usage | Medium | Low | Sleep intervals, lazy updates |

---

## Metrics to Track

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage (repl.py) | ≥ 95% | `pytest --cov` |
| Startup latency | < 100ms | Benchmark suite |
| Command latency | < 50ms | Benchmark suite |
| Typo recovery rate | > 90% | Manual testing |
| LLM suggestion accuracy | > 80% | Eval dataset |
| User delight score | > 4.5/5 | Survey |

---

## Continuation Generator

### After PLAN (this document):

```markdown
⟿[RESEARCH]
/hydrate
handles: scope=wave2.5_hardening; chunks=H1-H5; exit=95%_coverage; ledger={PLAN:touched}; entropy=0.05
mission: audit repl.py for untested paths; identify security vectors; benchmark current performance.
actions: Read(repl.py); coverage report; security checklist.
exit: gap analysis complete; test plan ready; continuation → DEVELOP.
```

### After Wave 2.5 REFLECT:

```markdown
⟿[PLAN]
/hydrate
handles: scope=wave3_intelligence; chunks=I1-I6; exit=LLM_working; ledger={PLAN:pending}; entropy=0.07
mission: design intelligent REPL with fuzzy matching and LLM suggestions.
exit: I1-I6 scoped; dependencies mapped; continuation → RESEARCH.
```

### After Wave 3 REFLECT:

```markdown
⟿[PLAN]
/hydrate
handles: scope=wave4_joy; chunks=J1-J5; exit=delight>4.5; ledger={PLAN:pending}; entropy=0.05
mission: add personality, easter eggs, ambient mode for joy-inducing experience.
exit: J1-J5 scoped; K-gent integration designed; continuation → RESEARCH.
```

### Final:

```markdown
⟂[DETACH:agentese_repl_v1_complete] REPL at v1.0: hardened, intelligent, joyful.
```

---

## Quick Reference

```bash
# Start Wave 2.5:
/hydrate prompts/agentese-repl-wave25-harden.md

# Check coverage:
cd impl/claude && uv run pytest protocols/cli/_tests/test_repl.py --cov=protocols/cli/repl --cov-report=term-missing

# Benchmark:
cd impl/claude && uv run pytest benchmarks/test_repl_perf.py -v

# Run full REPL test suite:
cd impl/claude && uv run pytest protocols/cli/ -q
```

---

*"The form is the function. Each wave builds on the last, each phase generates its successor."*

⟿[RESEARCH]
