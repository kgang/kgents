# Witness Dashboard TUI: Implementation Plan

> *"The garden thrives through pruning. Marks become crystals. Crystals become wisdom."*

**Status:** Draft
**Spec:** `spec/protocols/witness-crystallization.md`
**Skill:** `docs/skills/zenportal-patterns.md`
**Priority:** MEDIUM (replaces janky input() dashboard)
**Filed:** 2025-12-22

---

## Problem

The current `kg witness dash` implementation uses `input()` + `console.clear()` + reprint, which:
1. Creates visual jank (dashboard moves up on each keystroke)
2. Requires stdin workarounds for daemon routing
3. Doesn't feel like a proper TUI

**Goal:** Convert to a proper Textual TUI that applies ZenPortal patterns.

---

## Design: Crystal Navigator

A quarter-screen TUI for navigating the crystal hierarchy:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  WITNESS — Crystal Navigator                    💎 47 crystals   ◉ L0 filter │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  HIERARCHY                                      │  DETAILS                  │
│  ═══════════                                    │  ════════                 │
│                                                 │                           │
│  ▪ [SESSION] Completed extinction audit         │  Insight:                 │
│              3m ago • 12 marks • 95%           │  Completed extinction     │
│                                                 │  audit, removed 52K       │
│  ▫ [SESSION] Hardened Brain persistence        │  lines of stale code.     │
│              1h ago • 8 marks • 88%            │                           │
│                                                 │  Significance:            │
│  ▫ [DAY] Major codebase cleanup                │  Codebase is leaner,      │
│          5h ago • 3 crystals • 92%             │  focus is sharper.        │
│                                                 │                           │
│  ▫ [WEEK] Phase 4 witness implementation       │  Topics: extinction,      │
│           2d ago • 4 crystals • 85%            │  cleanup, architecture    │
│                                                 │                           │
│                                                 │  Sources: 12 marks        │
│                                                 │  Confidence: 95%          │
├─────────────────────────────────────────────────────────────────────────────┤
│  j/k: navigate  Enter: expand  0-3: filter level  c: copy  q: quit          │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## ZenPortal Patterns to Apply

| # | Pattern | Application |
|---|---------|-------------|
| 4 | Vim Navigation | j/k as primary, arrows as alias |
| 6 | Elastic Width | Insight truncation based on pane width |
| 7 | Status Glyphs | ▪ active, ▫ inactive, ◐ expanding |
| 8 | Notification Toast | "Copied to clipboard" confirmation |
| 12 | Hint Bar | Context-sensitive keybinding hints |
| 14 | Age Display | "3m", "1h", "2d" format |
| 17 | Active Pane | Bold/reverse when focused |
| 18 | SelectablePane | Base class for hierarchy list |

---

## Architecture

```
impl/claude/services/witness/tui/
├── __init__.py
├── app.py              # WitnessDashApp (Textual App)
├── crystal_list.py     # CrystalListPane (left - hierarchy)
├── detail_pane.py      # CrystalDetailPane (right - expanded view)
├── hint_bar.py         # ContextHintBar (bottom)
└── styles.tcss         # Textual CSS
```

### Key Classes

```python
class WitnessDashApp(App):
    """Witness Dashboard TUI Application."""

    BINDINGS = [
        Binding("q", "quit", "Quit"),
        Binding("j", "move_down", "↓", show=False),
        Binding("k", "move_up", "↑", show=False),
        Binding("down", "move_down", show=False),
        Binding("up", "move_up", show=False),
        Binding("enter", "expand_crystal", "Expand"),
        Binding("c", "copy_insight", "Copy"),
        Binding("0", "filter_level_0", "SESSION"),
        Binding("1", "filter_level_1", "DAY"),
        Binding("2", "filter_level_2", "WEEK"),
        Binding("3", "filter_level_3", "EPOCH"),
        Binding("a", "filter_all", "All"),
        Binding("r", "refresh", "Refresh"),
    ]

class CrystalListPane(Widget, can_focus=True):
    """Navigable list of crystals with level filtering."""

    selected_index: reactive[int] = reactive(0)
    level_filter: reactive[int | None] = reactive(None)

    def render_crystal(self, crystal: Crystal, selected: bool) -> Text:
        """Render a crystal row with status glyph and age."""
        glyph = "▪" if selected else "▫"
        level_color = LEVEL_COLORS[crystal.level]
        age = self._format_age(crystal.crystallized_at)

        # Elastic truncation based on available width
        insight = self._truncate(crystal.insight, self.size.width - 30)

        return Text.assemble(
            (glyph, "bold" if selected else "dim"),
            " ",
            (f"[{crystal.level.name}]", level_color),
            " ",
            insight,
            "\n",
            ("  " + age, "dim"),
            " • ",
            (f"{crystal.source_count} ", "cyan"),
            ("marks" if crystal.level == 0 else "crystals", "dim"),
            " • ",
            (f"{crystal.confidence:.0%}", "green" if crystal.confidence > 0.8 else "yellow"),
        )

class CrystalDetailPane(Widget):
    """Right pane showing expanded crystal details."""

    crystal: reactive[Crystal | None] = reactive(None)

    def compose(self) -> ComposeResult:
        yield Static(id="insight-label")
        yield Static(id="insight-text")
        yield Static(id="significance-label")
        yield Static(id="significance-text")
        yield Static(id="topics")
        yield Static(id="sources")
        yield Static(id="confidence")
```

---

## Phases

### Phase 1: Core TUI (Estimated: 2-3 hours)

**Files to create:**
- `impl/claude/services/witness/tui/__init__.py`
- `impl/claude/services/witness/tui/app.py`
- `impl/claude/services/witness/tui/crystal_list.py`
- `impl/claude/services/witness/tui/detail_pane.py`
- `impl/claude/services/witness/tui/hint_bar.py`
- `impl/claude/services/witness/tui/styles.tcss`

**Deliverables:**
- [ ] Basic two-pane layout
- [ ] Crystal list with navigation (j/k)
- [ ] Detail pane showing selected crystal
- [ ] Hint bar with context-sensitive keys
- [ ] Level filtering (0-3, a for all)
- [ ] Refresh command

### Phase 2: Polish (Estimated: 1-2 hours)

**Features:**
- [ ] Copy to clipboard with toast notification
- [ ] Elastic width truncation
- [ ] Status glyphs for crystal state
- [ ] Human-friendly age display
- [ ] Active pane indicator
- [ ] Expand/collapse crystal sources

### Phase 3: Integration (Estimated: 1 hour)

**Changes:**
- [ ] Wire `kg witness dash` to launch TUI
- [ ] Add `--classic` flag for old Rich dashboard (deprecate after validation)
- [ ] Ensure LOCAL_ONLY routing for stdin access
- [ ] Handle async crystal fetching without blocking UI

---

## CLI Integration

```bash
# Launch TUI (default)
kg witness dash

# With level filter
kg witness dash --level 0    # SESSION only
kg witness dash --level 2    # WEEK only

# Classic mode (deprecated, for comparison)
kg witness dash --classic
```

---

## Key Decisions

### 1. Textual vs. Rich

**Decision:** Use Textual

**Reasoning:**
- Textual handles keyboard events properly (no stdin issues)
- Built-in reactive state management
- CSS-based styling
- Same library Dawn uses (pattern reuse)

### 2. Single vs. Two Panes

**Decision:** Two panes (hierarchy + detail)

**Reasoning:**
- Crystal insights are too long for single-column
- Detail pane allows showing full insight + significance + topics
- Matches Dawn's layout pattern

### 3. Async Data Loading

**Decision:** Worker pattern for crystal fetching

**Reasoning:**
- `asyncio.run()` in cmd_dashboard was causing issues
- Textual's `run_worker` keeps UI responsive
- Crystals load in background, UI shows immediately

---

## Visual Design Principles

1. **Quarter-screen friendly** — Works in 80x24
2. **Keyboard-first** — All actions via keyboard
3. **Glanceable** — Status glyphs, age, confidence at a glance
4. **Copy is primary action** — Enter copies insight to clipboard
5. **Level colors are consistent** — SESSION=blue, DAY=green, WEEK=yellow, EPOCH=magenta

---

## Testing Strategy

```python
# TUI tests using textual.testing
async def test_crystal_list_navigation():
    """Test j/k navigation in crystal list."""
    app = WitnessDashApp()
    async with app.run_test() as pilot:
        await pilot.press("j")  # Move down
        assert app.query_one(CrystalListPane).selected_index == 1
        await pilot.press("k")  # Move up
        assert app.query_one(CrystalListPane).selected_index == 0

async def test_level_filtering():
    """Test level filter changes crystal list."""
    app = WitnessDashApp()
    async with app.run_test() as pilot:
        await pilot.press("0")  # Filter to SESSION
        pane = app.query_one(CrystalListPane)
        assert pane.level_filter == 0
        assert all(c.level == 0 for c in pane.visible_crystals)
```

---

## Dependencies

```toml
# Already in pyproject.toml via Dawn
textual = "^0.89.1"
```

---

## Success Criteria

1. **No stdin issues** — Keyboard input works in all terminal contexts
2. **No visual jank** — Smooth navigation without screen flashing
3. **Copy works** — Enter copies insight, shows toast confirmation
4. **Responsive** — Crystal loading doesn't block UI
5. **Discoverable** — Hint bar shows available actions

---

## Estimated Effort

| Phase | Hours |
|-------|-------|
| Phase 1: Core TUI | 2-3 |
| Phase 2: Polish | 1-2 |
| Phase 3: Integration | 1 |
| Testing | 1 |
| **Total** | **5-7** |

---

*"The dashboard isn't for watching crystals form. It's for navigating what already crystallized."*

*Filed: 2025-12-22 | Replaces: janky input() dashboard*
