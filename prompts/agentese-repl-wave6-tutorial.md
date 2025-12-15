# AGENTESE REPL Wave 6: Tutorial Mode & v1.0

> *"The interface that teaches its own structure through use is no interface at all."*

## ATTACH

/hydrate

You are entering the **PLAN phase** of **Wave 6 (Tutorial Mode & v1.0)** for the AGENTESE REPL Crown Jewel.

---

## Prior Context

**Completed Waves**:
- Wave 1 (Foundation): Core REPL, navigation, tab completion, history
- Wave 2 (Integration): Async Logos, pipelines, observer context, rich output, error sympathy
- Wave 2.5 (Hardening): Edge cases, security, performance, stress tests (73 tests)
- Wave 3 (Intelligence): Fuzzy matching, LLM suggestions, session persistence, script mode (97 tests)
- Wave 4 (Joy-Inducing): Welcome variations, K-gent integration, easter eggs, contextual hints (120 tests)
- Wave 5 (Ambient): `--ambient` flag, refresh loop, keybindings, help polish (149 tests)

**Current State**:
- Test count: 149 passing
- Files: `repl.py`, `repl_fuzzy.py`, `repl_session.py`
- Progress: 85%
- Status: Production-ready for power users

**Wave 5 Learnings** (from epilogue):
- Dashboard collectors API is clean and reusable
- Non-blocking keyboard via `select + termios` works reliably
- 5-second ambient refresh is responsive without CPU burn
- Pure ANSI rendering avoids external TUI dependencies

**Remaining for v1.0** (from crown jewel plan):
- Tutorial mode (`--tutorial`)
- Voice REPL (deferred to v2.0)
- Web REPL (deferred to v2.0)

**Kent's Wishes** (from `_focus.md`):
- AGENTESE REPL == EVERYTHING
- BEST IN CLASS UX/DEVEX
- PEDAGOGICAL - newcomers learn the ontology by exploring

---

## Mission: Wave 6 Tutorial Mode & v1.0

Implement the tutorial mode that teaches newcomers the AGENTESE ontology through guided exploration. Upon completion, the REPL reaches v1.0.

### Chunks (T1-T6)

| Chunk | Description | Entropy | Dependencies |
|-------|-------------|---------|--------------|
| **T1** | Tutorial engine core (`--tutorial` flag) | 0.02 | None |
| **T2** | Five-context lesson sequence | 0.02 | T1 |
| **T3** | Interactive exercises with validation | 0.02 | T2 |
| **T4** | Progress tracking and resume | 0.01 | T1 |
| **T5** | Tutorial completion celebration | 0.01 | T4 |
| **T6** | v1.0 polish and changelog | 0.01 | All |

**Total Entropy Budget**: 0.09

---

## Chunk Details

### T1: Tutorial Engine Core

Tutorial mode overlays the REPL with guided lessons.

```python
@dataclass
class TutorialLesson:
    """A single tutorial lesson."""
    name: str
    context: str  # Which context this teaches
    prompt: str  # What we're asking user to do
    expected: list[str]  # Valid responses
    hint: str  # Help if stuck
    celebration: str  # Success message

@dataclass
class TutorialState:
    """Tutorial progress state."""
    lessons: list[TutorialLesson]
    current_lesson: int = 0
    completed: list[str] = field(default_factory=list)
    started_at: datetime = field(default_factory=datetime.now)

def run_tutorial_mode(state: ReplState) -> int:
    """
    Run REPL in tutorial mode - guided learning.

    Teaches the five contexts through interactive lessons.
    """
    tutorial = TutorialState(lessons=LESSONS)
    print_tutorial_welcome()

    while tutorial.current_lesson < len(tutorial.lessons):
        lesson = tutorial.lessons[tutorial.current_lesson]
        print_lesson_prompt(lesson)

        response = input(f"{lesson.context} » ")
        if validate_response(response, lesson):
            print_celebration(lesson)
            tutorial.completed.append(lesson.name)
            tutorial.current_lesson += 1
        else:
            print_hint(lesson)

    print_tutorial_complete(tutorial)
    return 0
```

**Exit**: `--tutorial` flag launches tutorial mode.

### T2: Five-Context Lesson Sequence

Structured lessons covering each context:

```python
LESSONS = [
    # Lesson 1: Self
    TutorialLesson(
        name="discover_self",
        context="root",
        prompt="Type 'self' to enter the self context (your agent's internal world):",
        expected=["self"],
        hint="Try typing: self",
        celebration="You've entered the self context—where your agent looks inward.",
    ),
    # Lesson 2: Status
    TutorialLesson(
        name="check_status",
        context="self",
        prompt="Now type 'status' to see your agent's current state:",
        expected=["status", "self.status"],
        hint="Try typing: status",
        celebration="Status shows your agent's mode, interactions, and health.",
    ),
    # Lesson 3: Navigation
    TutorialLesson(
        name="navigate_up",
        context="self",
        prompt="Type '..' to go back up one level:",
        expected=[".."],
        hint="Two dots (..) moves you up in the hierarchy.",
        celebration="Navigation is simple: enter context, explore, go back.",
    ),
    # Lesson 4: World
    TutorialLesson(
        name="discover_world",
        context="root",
        prompt="Type 'world' to enter the world context (external entities):",
        expected=["world"],
        hint="Try typing: world",
        celebration="The world context shows agents, daemons, and infrastructure.",
    ),
    # Lesson 5: Void
    TutorialLesson(
        name="discover_void",
        context="root",
        prompt="Type 'void' to enter the void context (entropy and serendipity):",
        expected=["void"],
        hint="Try typing: void",
        celebration="The void is the Accursed Share—entropy, shadow, serendipity.",
    ),
    # Lesson 6: Introspection
    TutorialLesson(
        name="introspection",
        context="void",
        prompt="Type '?' to see available affordances in this context:",
        expected=["?"],
        hint="The question mark (?) shows what you can do here.",
        celebration="Introspection reveals affordances—what actions are possible.",
    ),
    # Lesson 7: Pipeline
    TutorialLesson(
        name="pipeline",
        context="root",
        prompt="Type 'self.status >> concept.count' to compose a pipeline:",
        expected=["self.status >> concept.count", "self status >> concept count"],
        hint="The >> operator composes paths into pipelines.",
        celebration="Pipelines compose actions—the heart of AGENTESE.",
    ),
]
```

**Exit**: 7 lessons covering core concepts.

### T3: Interactive Exercises with Validation

Flexible validation that accepts reasonable variations:

```python
def validate_response(response: str, lesson: TutorialLesson) -> bool:
    """Validate user response against expected answers."""
    normalized = response.strip().lower()

    # Exact match
    if normalized in [e.lower() for e in lesson.expected]:
        return True

    # Fuzzy match for typos
    fuzzy = state.get_fuzzy()
    if fuzzy:
        for expected in lesson.expected:
            if fuzzy.suggest(normalized, [expected]) == expected:
                return True

    return False
```

**Exit**: Validation accepts variations and typos.

### T4: Progress Tracking and Resume

Save and restore tutorial progress:

```python
# ~/.kgents_tutorial_progress.json
{
    "completed_lessons": ["discover_self", "check_status"],
    "current_lesson": 2,
    "started_at": "2025-12-14T10:00:00Z",
    "last_session": "2025-12-14T10:15:00Z"
}

def save_tutorial_progress(tutorial: TutorialState) -> None:
    """Save tutorial progress to disk."""
    progress_file = Path.home() / ".kgents_tutorial_progress.json"
    progress_file.write_text(json.dumps({
        "completed_lessons": tutorial.completed,
        "current_lesson": tutorial.current_lesson,
        "started_at": tutorial.started_at.isoformat(),
        "last_session": datetime.now().isoformat(),
    }))

def load_tutorial_progress() -> TutorialState | None:
    """Load tutorial progress from disk."""
    progress_file = Path.home() / ".kgents_tutorial_progress.json"
    if progress_file.exists():
        data = json.loads(progress_file.read_text())
        return TutorialState(
            lessons=LESSONS,
            completed=data["completed_lessons"],
            current_lesson=data["current_lesson"],
        )
    return None
```

**Exit**: Tutorial progress persists across sessions.

### T5: Tutorial Completion Celebration

Joy-inducing completion message:

```python
COMPLETION_MESSAGE = """
╭────────────────────────────────────────────────────────────────╮
│                                                                │
│   🎉  TUTORIAL COMPLETE!  🎉                                   │
│                                                                │
│   You've learned the AGENTESE ontology:                        │
│                                                                │
│   ✓ self    — Your agent's internal world                      │
│   ✓ world   — External entities and infrastructure             │
│   ✓ concept — Platonic ideals and definitions                  │
│   ✓ void    — Entropy, shadow, and serendipity                 │
│   ✓ time    — Traces, forecasts, and schedules                 │
│                                                                │
│   The forest is now open to you.                               │
│                                                                │
│   Next steps:                                                  │
│   - kg -i                    Enter the REPL                    │
│   - kg -i --ambient          Watch the system breathe          │
│   - kg soul challenge        Test your understanding           │
│                                                                │
╰────────────────────────────────────────────────────────────────╯
"""
```

**Exit**: Completion feels celebratory and guides next steps.

### T6: v1.0 Polish and Changelog

Final polish for v1.0 release:

1. Update version to 1.0.0
2. Write CHANGELOG.md entry
3. Update README with tutorial mention
4. Ensure all tests pass
5. Tag release

**Exit**: AGENTESE REPL at v1.0 with 100% progress.

---

## Exit Criteria (Wave 6)

1. `--tutorial` flag launches tutorial mode
2. 7 lessons covering all five contexts
3. Progress saves and resumes across sessions
4. Completion celebration with next steps
5. v1.0 version tag and changelog
6. New tests: ~15-20 (bringing total to ~165)
7. AGENTESE REPL at 100% progress

---

## Non-Goals (Wave 6)

- Voice/audio tutorial (v2.0)
- Web-based tutorial (v2.0)
- Advanced pipeline lessons (v1.1)
- K-gent dialogue in tutorial (complexity)

---

## N-Phase Execution

### This Session: PLAN Phase

**Actions**:
1. Review this scope (T1-T6 chunks)
2. Validate lesson sequence covers pedagogical goals
3. Allocate entropy budget
4. Confirm exit criteria
5. Generate RESEARCH continuation

**Exit**: PLAN complete when scope is agreed and dependencies mapped.

### Next Phases

| Phase | Focus |
|-------|-------|
| RESEARCH | Tutorial patterns in CLIs, lesson sequencing research |
| DEVELOP | TutorialState dataclass, lesson structure, validation API |
| STRATEGIZE | T1 first (unblocks all), T2-T3 parallel, T4-T5 sequential, T6 last |
| IMPLEMENT | TDD: tests first, then implementation |
| QA | Test tutorial flow, edge cases, resume |
| TEST | Full suite, manual walkthrough |
| EDUCATE | Update docs, add tutorial to README |
| MEASURE | Time to completion, lesson success rates |
| REFLECT | Archive Wave 6, declare v1.0 |

---

## Phase Ledger

```yaml
path: plans/devex/agentese-repl-crown-jewel
wave: 6
phase_ledger:
  PLAN: pending  # This session
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
  planned: 0.09
  spent: 0.0
  returned: 0.09
```

---

## Principles Alignment

| Principle | Application |
|-----------|-------------|
| **Pedagogical** | Tutorial teaches by doing, not reading |
| **Tasteful** | Minimal lessons, maximum insight |
| **Joy-Inducing** | Celebration at completion |
| **Composable** | Tutorial builds on existing REPL |
| **Ethical** | No hidden token burn in tutorial |

---

## Integration Points

| Component | API | Usage |
|-----------|-----|-------|
| ReplState | `state.path`, `state.observer` | Track navigation |
| Fuzzy matcher | `state.get_fuzzy()` | Validate typos |
| Session persistence | `repl_session.py` | Save/restore progress |
| Welcome message | `get_welcome_message()` | Tutorial welcome |

---

## Quick Commands

```bash
# Run current tests
cd impl/claude && uv run pytest protocols/cli/_tests/test_repl.py -v

# Check test count
cd impl/claude && uv run pytest protocols/cli/_tests/test_repl.py --collect-only | grep "test session starts" -A1

# Verify Wave 5 ambient works
cd impl/claude && uv run python -c "from protocols.cli.repl import run_ambient_mode; print('ambient available')"
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
handles: scope=wave6_tutorial; chunks=T1-T6; exit=tutorial_working; ledger={PLAN:touched}; entropy=0.09
mission: study CLI tutorial patterns (Click, Typer tutorials); research lesson sequencing pedagogy; audit existing REPL APIs for tutorial hooks.
actions:
  - WebSearch("CLI tutorial mode patterns Python") — find prior art
  - Read(protocols/cli/repl.py) — identify hook points for tutorial overlay
  - Read(protocols/cli/repl_session.py) — reuse session persistence for progress
  - Grep("lesson|tutorial|onboarding") — check if any exists
exit: tutorial patterns identified; lesson structure designed; persistence approach chosen; continuation → DEVELOP.
```

---

## Branch Candidates

| Candidate | Classification | Notes |
|-----------|----------------|-------|
| Advanced tutorial track | PARALLEL | Pipelines, observers, K-gent |
| Tutorial analytics | DEFERRED | Track lesson completion rates |
| Localization | DEFERRED | Multi-language lessons |

---

*This is the **PLAN PHASE** for AGENTESE REPL Wave 6: Tutorial Mode & v1.0. Upon completion, generate the RESEARCH phase continuation with the auto-inducer.*

⟿[PLAN]
