# Dawn Phase 4 Kickoff Prompt

> *"The cockpit doesn't fly the plane. The pilot flies the plane. The cockpit just makes it easy."*

**Use this prompt to start a new session implementing Dawn Phase 4.**

---

## Context

kg dawn is Kent's daily operating surface—a quarter-screen TUI for focus management and copy-paste snippets. Phase 3 (basic TUI) is complete with 154 tests passing. A thorough audit of ZenPortal (Kent's production session manager, ~/git/zenportal) extracted 23 patterns that improve kg dawn.

**Current State:**
- TUI works: two-pane layout, Tab switching, keyboard nav, snippet copying
- But: no persistence (items lost on restart), silent copy (no feedback), no j/k nav, add focus shows "Coming soon"

---

## Your Mission: Implement Kent's 3 Priorities

### 1. Copy Confirmation (Silent → Joyful)

**Problem:** Copying a snippet does nothing visible—user doesn't know it worked.

**Solution:** Add feedback to `snippet_pane.py`:
```python
def _copy_selected(self) -> None:
    # ... existing copy logic ...

    # Emit message for app to handle
    self.post_message(self.SnippetCopied(snippet, content))
```

Then in `app.py`, add handler:
```python
def on_snippet_pane_snippet_copied(self, message: SnippetPane.SnippetCopied) -> None:
    garden = self.query_one("#garden-view", GardenView)
    garden.add_event(f"📋 Copied: {message.snippet.to_dict()['label']}")
```

### 2. j/k Navigation (Vim-style)

**Problem:** Only ↑↓ works; j/k is muscle memory for terminal users.

**Solution:** In both `focus_pane.py` and `snippet_pane.py`, update `on_key`:
```python
def on_key(self, event: Any) -> None:
    if not self.is_active:
        return
    key = event.key

    if key in ("up", "k") and self._items:
        self.selected_index = max(0, self.selected_index - 1)
        event.stop()
    elif key in ("down", "j") and self._items:
        self.selected_index = min(len(self._items) - 1, self.selected_index + 1)
        event.stop()
    # ... rest unchanged
```

### 3. Add Focus Modal

**Problem:** Pressing `a` shows "Coming soon" instead of letting user add focus items.

**Solution:** Create `impl/claude/protocols/dawn/tui/add_focus_modal.py`:
```python
from textual.screen import ModalScreen
from textual.widgets import Input, Select, Button
from textual.containers import Vertical, Horizontal

class AddFocusModal(ModalScreen[tuple[str, str, str] | None]):
    """Modal for adding a focus item."""

    BINDINGS = [("escape", "cancel", "Cancel")]

    def compose(self):
        with Vertical(id="modal-container"):
            yield Static("ADD FOCUS ITEM", id="title")
            yield Input(placeholder="Target (file path or AGENTESE)", id="target")
            yield Input(placeholder="Label (optional)", id="label")
            yield Select(
                [(b.value, b.value) for b in Bucket],
                value="today",
                id="bucket"
            )
            with Horizontal():
                yield Button("Cancel", id="cancel")
                yield Button("Add", id="add", variant="primary")

    def on_button_pressed(self, event):
        if event.button.id == "add":
            target = self.query_one("#target", Input).value
            label = self.query_one("#label", Input).value
            bucket = self.query_one("#bucket", Select).value
            self.dismiss((target, label, bucket))
        else:
            self.dismiss(None)
```

Then in `app.py`:
```python
def action_add_focus(self) -> None:
    self.push_screen(AddFocusModal(), self._handle_add_focus)

def _handle_add_focus(self, result: tuple[str, str, str] | None) -> None:
    if result:
        target, label, bucket_name = result
        from ..focus import Bucket
        bucket = Bucket(bucket_name)
        item = self._focus_manager.add(target, label=label or None, bucket=bucket)
        self.query_one("#focus-pane", FocusPane).refresh_items()
        garden = self.query_one("#garden-view", GardenView)
        garden.add_event(f"✅ Added: {item.label}")
```

---

## Files to Modify

| File | Changes |
|------|---------|
| `impl/claude/protocols/dawn/tui/app.py` | Add message handler, add_focus with modal |
| `impl/claude/protocols/dawn/tui/focus_pane.py` | Add j/k to on_key |
| `impl/claude/protocols/dawn/tui/snippet_pane.py` | Add j/k to on_key |
| NEW: `impl/claude/protocols/dawn/tui/add_focus_modal.py` | Modal screen |

---

## Testing Commands

```bash
# Run all Dawn tests
cd impl/claude && uv run pytest protocols/dawn/ -v

# Run just TUI tests
uv run pytest protocols/dawn/tui/_tests/ -v

# Type check
uv run mypy protocols/dawn/ --ignore-missing-imports

# Launch TUI to test manually
uv run kg dawn
```

---

## Key Patterns from ZenPortal (Reference)

See `docs/skills/zenportal-patterns.md` for full details. Most relevant:

- **Pattern 5 (Copy Confirmation):** Multiple feedback channels—Garden + notify
- **Pattern 4 (Vim Navigation):** j/k primary, arrows as hidden aliases
- **Pattern 17 (Active Pane):** Reverse video title > subtle border

---

## Definition of Done

1. ✅ `j` and `k` navigate both panes
2. ✅ Copying snippet shows message in Garden view
3. ✅ Pressing `a` opens modal, entering data adds focus item
4. ✅ All existing tests still pass
5. ✅ Manual QA: launch `kg dawn`, test all three features

---

**Estimated time:** 2-3 hours

*Filed: 2025-12-22 | Ready for Phase 4 implementation*
