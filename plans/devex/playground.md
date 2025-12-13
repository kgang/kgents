---
path: devex/playground
status: complete
progress: 100
last_touched: 2025-12-13
touched_by: claude-opus-4.5
blocking: []
enables: [devex/gallery]
session_notes: |
  Plan created from strategic recommendations.
  Priority 1 of 6 DevEx improvements.

  2025-12-13: Implemented! All phases complete:
  - Menu system with 5 choices (4 tutorials + REPL)
  - Tutorial engine (TutorialStep, Tutorial classes)
  - 4 tutorials: hello, compose, functor, soul
  - REPL mode with pre-imported modules
  - 32 tests passing, mypy strict clean
  - Command registered: `kgents play`
---

# Interactive Playground: `kgents play`

> *"The best system teaches through use, not through documentation."*

**Goal**: Zero-to-delight in under 5 minutes via guided interactive tutorials.
**Priority**: 1 (highest impact, medium effort)

---

## The Problem

Users must read documentation before doing anything meaningful. The first 5 minutes are cognitive load, not delight.

---

## The Solution

```bash
$ kgents play

Welcome to kgents playground!

[1] Hello World        — Your first agent
[2] Composition        — Pipe agents together
[3] Lift to Maybe      — Handle optional values
[4] K-gent Dialogue    — Chat with Kent's simulacrum
[5] Free exploration   — REPL mode

Choose (1-5) or 'q' to quit:
```

Each choice runs an interactive tutorial that:
1. Writes code for you (shows what's happening)
2. Explains the concept in one sentence
3. Lets you modify and experiment
4. Provides clear next steps

---

## Research & References

### Python 3.13+ REPL Features
- Syntax highlighting (new in 3.13+)
- Multi-line editing with proper indentation
- History persistence across sessions
- Special commands without parentheses
- Source: [Real Python - Python 3.13 REPL](https://realpython.com/python313-repl/)

### Enhanced REPLs
- **ptpython**: Better Python REPL with autocomplete — [GitHub](https://github.com/prompt-toolkit/ptpython)
- **IPython**: Magic commands, `%timeit`, session saving
- Source: [Real Python - Python REPL](https://realpython.com/python-repl/)

### Existing Assets
- `agents/examples/` — 5 runnable examples already exist
- `docs/quickstart.md` — New quickstart guide
- `docs/functor-field-guide.md` — Functor explanations

---

## Implementation Outline

### Phase 1: Menu System (~50 LOC)
```python
# protocols/cli/handlers/play.py
@expose(help="Interactive playground")
async def play(self, ctx: CommandContext) -> None:
    choices = [
        ("Hello World", self._hello_world),
        ("Composition", self._composition),
        ("Lift to Maybe", self._lift_maybe),
        ("K-gent Dialogue", self._kgent_dialogue),
        ("Free exploration", self._repl),
    ]
    # Interactive menu with Rich
```

### Phase 2: Tutorial Engine (~100 LOC)
```python
class Tutorial:
    """Guided interactive tutorial."""

    def __init__(self, name: str, steps: list[TutorialStep]):
        self.name = name
        self.steps = steps

    async def run(self) -> None:
        for step in self.steps:
            await step.show_code()
            await step.explain()
            await step.let_user_modify()
            await step.show_next_steps()
```

### Phase 3: Content (~100 LOC)
- 5 tutorials, each ~20 lines of step definitions
- Leverage existing examples in `agents/examples/`

### Phase 4: REPL Mode (~50 LOC)
- Embed IPython or ptpython
- Pre-import common modules (`from agents import *`)
- Custom banner with quick reference

---

## File Structure

```
protocols/cli/handlers/
├── play.py           # Main handler
└── _playground/
    ├── __init__.py
    ├── tutorial.py   # Tutorial engine
    ├── repl.py       # REPL wrapper
    └── content/
        ├── hello_world.py
        ├── composition.py
        ├── lift_maybe.py
        ├── kgent_dialogue.py
        └── common.py
```

---

## Success Criteria

| Criterion | Metric |
|-----------|--------|
| Time to first working agent | < 2 minutes |
| Tutorial completion rate | > 80% |
| User proceeds to docs | > 50% |
| Kent's subjective approval | "This is delightful" |

---

## Testing Strategy

| Test Type | Coverage |
|-----------|----------|
| Unit | Tutorial step execution |
| Integration | Full tutorial flow |
| Smoke | `kgents play` starts without error |
| Manual | Kent runs each tutorial |

---

## Dependencies

- `rich` (already installed) — Interactive menus
- `ptpython` or `IPython` (optional) — Enhanced REPL
- Existing examples in `agents/examples/`

---

## Cross-References

- **Strategic Recommendations**: `plans/ideas/strategic-recommendations-2025-12-13.md`
- **Quickstart**: `docs/quickstart.md`
- **Examples**: `agents/examples/`
- **CLI Patterns**: `plans/skills/cli-command.md`

---

*"The playground is where curiosity becomes capability."*
