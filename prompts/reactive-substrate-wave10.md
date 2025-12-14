---
path: reactive-substrate/wave10
status: pending
progress: 0
last_touched: 2025-12-14
touched_by: claude-opus-4.5
blocking: []
enables: [wave11-marimo-adapter]
session_notes: |
  Wave 10: TUI Adapter - Bridge reactive widgets to Textual.
  Continuation from Wave 9 (Widget Integration Pipeline).
phase_ledger:
  PLAN: touched  # Wave 9 epilogue scoped this
  RESEARCH: pending
  DEVELOP: pending
  STRATEGIZE: skipped  # reason: single-track, wired to Wave 9
  CROSS-SYNERGIZE: touched  # Textual integration point identified
  IMPLEMENT: pending
  QA: pending
  TEST: pending
  EDUCATE: pending
  MEASURE: deferred  # reason: metrics backlog
  REFLECT: pending
entropy:
  planned: 0.10
  spent: 0.00
  sip_allowed: true
---

# ⟿[IMPLEMENT] Reactive Substrate Wave 10 — TUI Adapter

> *"The adapter is the bridge. Invisible—just reactive widgets rendered wherever they need to be."*

---

## Quick Wield

```
ATTACH /hydrate
handles: world.reactive.tui.manifest[wave=10]; void.entropy.sip[amount=0.07]
mission: Bridge KgentsWidget → Textual. Thin adapters, not rewrites.
ledger: IMPLEMENT=in_progress | entropy.spent += 0.07
actions: TextualAdapter, FlexContainer, ThemeBinding, FocusSync, demo app
exit: 1250+ reactive tests | mypy clean | commit | ⟿[QA] or ⟂[BLOCKED]
```

---

## Context

**From Wave 9** (2025-12-14):
- Artifacts: `pipeline/render.py`, `pipeline/layout.py`, `pipeline/focus.py`, `pipeline/theme.py`
- Tests: **1198 reactive tests** (132 new)
- Learnings: Pipeline is invisible when working. Dirty checking essential. Theme as Signal enables reactive switching.

**Forest state**: 14,100+ tests | `reactive-substrate-unification` active

---

## The Boldness of Wave 10

> *"IMPLEMENT is not planning to code. IMPLEMENT is coding."*

When you enter Wave 10, you are not preparing to bridge. You ARE bridging:

- **Urgency**: Textual app running in background NOW
- **Commitment**: TodoWrite tracking each adapter chunk
- **Parallel motion**: Tests validating continuously
- **Completion**: Each adapter marked complete BEFORE moving to next

---

## Implementation Chunks

### 1. TextualAdapter (`adapters/textual_widget.py`)
Bridge between `KgentsWidget` and Textual:
```python
class TextualAdapter(Widget):
    """Wraps any KgentsWidget for Textual rendering."""
    def __init__(self, kgents_widget: KgentsWidget[Any]) -> None: ...
    def on_mount(self) -> None: ...  # Subscribe to state
    def render(self) -> RenderableType: ...  # project(TUI)
```

### 2. FlexContainer (`adapters/textual_layout.py`)
Connect FlexLayout to Textual containers:
```python
class FlexContainer(Container):
    """Textual container using FlexLayout for positioning."""
    layout: FlexLayout
    def compose(self) -> ComposeResult: ...
    def on_resize(self, event: Resize) -> None: ...
```

### 3. ThemeBinding (`adapters/textual_theme.py`)
Bind ThemeProvider to Textual CSS:
```python
class ThemeBinding:
    """Generates Textual CSS from Theme tokens."""
    def to_css(self, theme: Theme) -> str: ...
    def bind(self, app: App, provider: ThemeProvider) -> None: ...
```

### 4. FocusSync (`adapters/textual_focus.py`)
Wire AnimatedFocus to Textual:
```python
class FocusSync:
    """Syncs AnimatedFocus ↔ Textual.focus()."""
    def sync_to_textual(self, focus: AnimatedFocus) -> None: ...
    def on_focus(self, event: Focus) -> None: ...  # → AnimatedFocus
```

### 5. Demo App (`demo/tui_dashboard.py`)
Full TUI demonstrating all adapters:
- Agent card grid with reactive updates
- Focus navigation (Tab, Arrow keys)
- Theme toggle (Ctrl+T)
- Real-time Clock updates

---

## Exit Criteria

| Criterion | Verification |
|-----------|--------------|
| TextualAdapter renders KgentsWidget | Unit test + visual demo |
| FlexContainer positions children | Layout integration test |
| ThemeBinding generates valid CSS | CSS parse test |
| FocusSync bidirectional | Focus navigation test |
| Demo app runs | `python -m agents.i.reactive.demo.tui_dashboard` |
| Tests pass | `uv run pytest` ≥1250 reactive tests |
| Types clean | `uv run mypy .` |
| Lint clean | `uv run ruff check .` |

---

## Entropy Budget

| Draw | Purpose |
|------|---------|
| `void.entropy.sip(0.07)` | Signal vs Textual.reactive exploration |
| `void.entropy.sip(0.03)` | CSS generation edge cases |

**Exploration question**: Should we use Textual's built-in `reactive()` or bridge our `Signal`? Initial hypothesis: bridge Signal—it's already battle-tested across 1198 tests.

---

## Branch Candidates (check at exit)

- [ ] **Marimo Adapter** (Wave 11): Already planned
- [ ] **Animation integration**: Tween/Spring → CSS transitions?
- [ ] **Accessibility**: ARIA-like semantics for agent cards?
- [ ] **Textual testing harness**: Snapshot testing for TUI output?

---

## Continuation Generator

### Normal Exit
```markdown
⟿[QA]
/hydrate
handles: code=adapters/textual_*.py; tests=_tests/test_textual_*.py; results=+52; summary="TUI Adapter bridging KgentsWidget → Textual"; laws=compositional_adapter_laws_upheld; ledger={IMPLEMENT:touched}; branches=marimo_next
mission: gate quality/security/lawfulness before broader testing.
actions: uv run mypy .; uv run ruff check; security sweep; demo visual check.
exit: QA checklist status + ledger.QA=touched; notes for TEST; continuation → TEST.
```

### Halt Conditions
```markdown
⟂[BLOCKED:textual_dep] Textual version incompatibility blocks adapter
⟂[BLOCKED:tests_failing] Adapter tests failing before QA gate
⟂[ENTROPY_DEPLETED] Budget exhausted without resolution
⟂[DETACH:awaiting_human] Textual API design decision needed
```

---

## Related

- `plans/skills/n-phase-cycle/implement.md` — Phase skill
- `spec/protocols/agentese.md` — `world.reactive.*` handles
- `impl/claude/agents/i/reactive/widget.py` — `RenderTarget.TUI`
- Wave 9 epilogue: `impl/claude/plans/_epilogues/2025-12-14-reactive-substrate-wave9.md`

---

*"I will write adapters, not describe what adapters to write."*
