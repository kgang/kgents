# Dawn Cockpit: Implementation Plan

> *"The cockpit doesn't fly the plane. The pilot flies the plane. The cockpit just makes it easy."*

**Status:** 🟡 Phase 3 Complete, ZenPortal Audit Complete
**Spec:** `spec/protocols/dawn-cockpit.md`
**Skill:** `docs/skills/zenportal-patterns.md`
**Priority:** HIGH (daily operating surface)
**Filed:** 2025-12-22

---

## Completion Status

| Phase | Status | Tests |
|-------|--------|-------|
| Phase 1: Core Domain | ✅ Complete | 154 tests |
| Phase 2: AGENTESE Integration | ✅ Complete | - |
| Phase 3: TUI Implementation | ✅ Complete | 46 TUI tests |
| Phase 3.5: ZenPortal Audit | ✅ Complete | 23 patterns extracted |
| Phase 4: Persistence & Polish | 🔴 Not Started | - |
| Phase 5: Morning Coffee | 🔴 Not Started | - |

**Total Tests:** 154 passing

---

## ZenPortal Audit Summary (2025-12-22)

Thorough comparison with ZenPortal (~/git/zenportal), the spiritual predecessor:

| Aspect | ZenPortal | kg dawn | Gap |
|--------|-----------|---------|-----|
| Lines of code | ~21K | ~1.5K | Expected |
| Tests | 361 | 154 | Acceptable |
| Persistence | Full (JSON + JSONL) | In-memory only | CRITICAL |
| Navigation | j/k + move + search | ↑↓ only | HIGH |
| Feedback | Notifications + hints | Garden only | HIGH |
| Layout | Draggable splitter | Fixed 50/50 | MEDIUM |

**23 patterns extracted** → `docs/skills/zenportal-patterns.md`

---

## Kent's Priorities (from 2025-12-22 session)

1. **Copy confirmation** — Currently silent; need visible feedback
2. **j/k navigation** — Vim-style; matches ZenPortal muscle memory
3. **Add focus modal** — The `a` key shows "Coming soon"

---

## Phase 4: Persistence & Polish

### 4.1 Persistence (CRITICAL)

**Files to create/modify:**
- NEW: `impl/claude/protocols/dawn/storage.py` — XDG-compliant persistence
- MODIFY: `impl/claude/protocols/dawn/focus.py` — Add load/save
- MODIFY: `impl/claude/protocols/dawn/snippets.py` — Add custom persistence

**Data to persist:**
```
~/.config/kgents/dawn/
├── focus.json      # Focus items
├── snippets.json   # Custom snippets
└── state.json      # Selection, pane state
```

### 4.2 Copy Confirmation (Pattern 5)

```python
def _copy_selected(self) -> None:
    # ... existing copy logic ...

    # Garden event (persistent)
    garden = self.app.query_one("#garden-view", GardenView)
    garden.add_event(f"📋 Copied: {snippet.label}")

    # Optional: Textual notification
    self.app.notify(f"Copied: {content[:30]}...")
```

### 4.3 Vim Navigation (Pattern 4)

```python
BINDINGS = [
    Binding("j", "move_down", "↓"),  # Vim primary
    Binding("k", "move_up", "↑"),
    Binding("down", "move_down", show=False),  # Arrow alias
    Binding("up", "move_up", show=False),
]
```

### 4.4 Add Focus Modal

**Files to create:**
- NEW: `impl/claude/protocols/dawn/tui/add_focus_modal.py`

**UI:**
```
┌─────────────────────────────────────────┐
│  ADD FOCUS ITEM                         │
├─────────────────────────────────────────┤
│  Target: [________________________]     │
│  Label:  [________________________]     │
│  Bucket: [TODAY ▼]                      │
├─────────────────────────────────────────┤
│  [Cancel]                    [Add]      │
└─────────────────────────────────────────┘
```

---

## Phase 5: Morning Coffee Integration

**Status:** Not started
**Prerequisite:** Coffee service implementation

Morning Coffee becomes an overlay within Dawn, not a separate entry point:
- Press `c` → Coffee overlay appears
- Coffee completion populates focus.add(bucket=today)
- Voice capture becomes CustomSnippet

---

## Key Files

### Existing (to modify)
- `impl/claude/protocols/dawn/focus.py`
- `impl/claude/protocols/dawn/snippets.py`
- `impl/claude/protocols/dawn/tui/app.py`
- `impl/claude/protocols/dawn/tui/focus_pane.py`
- `impl/claude/protocols/dawn/tui/snippet_pane.py`

### New (to create)
- `impl/claude/protocols/dawn/storage.py`
- `impl/claude/protocols/dawn/tui/styles.py`
- `impl/claude/protocols/dawn/tui/base.py` (SelectablePane)
- `impl/claude/protocols/dawn/tui/add_focus_modal.py`

---

## Estimated Effort

| Task | Hours |
|------|-------|
| 4.1 Persistence | 2-3 |
| 4.2 Copy confirmation | 0.5 |
| 4.3 Vim navigation | 0.5 |
| 4.4 Add focus modal | 1-2 |
| Testing & Polish | 1-2 |
| **Total Phase 4** | **5-8** |

---

*Updated: 2025-12-22 | ZenPortal Audit Complete*
