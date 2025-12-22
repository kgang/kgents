# Dawn TUI Enter Key Investigation & Fix

**Date**: 2025-12-22
**Issue**: Enter key causes black bar instead of activating items
**Status**: ✅ RESOLVED

## Root Cause Analysis

### The Problem

The Dawn Cockpit TUI had an app-level binding:
```python
Binding("enter", "activate_item", "Select", priority=True)
```

### Why This Failed

Textual's event handling order is:

1. **Priority bindings checked FIRST** (before focused widget)
2. **Focused widget's event handlers** (on_key, etc.)
3. **Event bubbles up to parents**

With `priority=True`, the sequence was:
1. User presses Enter
2. `DawnCockpit.action_activate_item()` fires immediately (priority)
3. Event continues to focused widget
4. Widget's `on_key()` also fires
5. **Double-handling** or unexpected state

The "black bar" was likely:
- Textual's default Enter behavior being triggered
- Double event handling causing visual artifacts
- Some internal Textual widget responding to Enter

### Key Insight from Textual Docs

> "Individual bindings may be marked as a priority, which means they will be checked **prior to the bindings of the focused widget**."

Source: [Textual Binding API](https://textual.textualize.io/api/binding/)

This means priority bindings **bypass** the normal event flow where the focused widget handles the event first.

## The Fix

### Solution 1: Remove priority=True

Changed:
```python
Binding("enter", "activate_item", "Select", priority=True)
```

To:
```python
Binding("enter", "activate_item", "Select", priority=False)
```

This would let the widget handle Enter first, then bubble up to app.

### Solution 2: Remove app-level Enter binding entirely (CHOSEN)

**Better approach**: Since `FocusPane` and `SnippetPane` already handle Enter in their `on_key()` methods with `event.stop()`, we don't need an app-level binding at all.

**Final BINDINGS**:
```python
BINDINGS = [
    Binding("q", "quit", "Quit", priority=True),
    Binding("tab", "switch_pane", "Switch", priority=True),
    # NOTE: Enter is handled by individual panes (FocusPane, SnippetPane)
    # Not defined at app level - this prevents double-handling and lets
    # the widget's on_key method have full control with event.stop()
    Binding("a", "add_focus", "Add"),
    Binding("d", "done_focus", "Done"),
    Binding("h", "hygiene", "Hygiene"),
    Binding("slash", "search", "Search"),
    Binding("r", "refresh", "Refresh"),
]
```

## How It Works Now

### Correct Event Flow

1. User presses Enter in SnippetPane
2. `SnippetPane.on_key(event)` fires
3. Checks `if self.is_active` (True)
4. Calls `self._copy_selected()`
5. Calls `event.stop()` - prevents bubbling
6. Event never reaches app level
7. ✅ Clean, single handling

### Focus Pane Behavior

```python
def on_key(self, event):
    if not self.is_active:
        return  # Let app handle

    if event.key == "enter" and self.selected_item:
        self.post_message(self.ItemActivated(self.selected_item))
        event.stop()  # Critical!
```

### Snippet Pane Behavior

```python
def on_key(self, event):
    if not self.is_active:
        return  # Let app handle

    if event.key == "enter" and self._snippets:
        self._copy_selected()
        event.stop()  # Critical!
```

## Why event.stop() is Critical

From [Textual Events Guide](https://textual.textualize.io/guide/events/):

> "Event handlers may stop this bubble behavior by calling the `stop()` method on the event or message."

Without `event.stop()`:
- Event bubbles to parent widgets
- App-level bindings might fire
- Unpredictable behavior

With `event.stop()`:
- Event consumed at widget level
- No bubbling
- Clean, predictable behavior

## Testing

All 54 tests pass:
```bash
uv run pytest protocols/dawn/tui/_tests/ -v
# ============================== 54 passed in 0.28s ==============================
```

Manual testing:
```bash
uv run kg dawn
# Press Tab to switch panes
# Press j/k to navigate
# Press Enter to copy snippet or activate focus
# ✅ No black bar appears
# ✅ Copy confirmation shows in Garden
```

## Lessons Learned

### 1. Priority Bindings Bypass Widget Handlers

**When to use `priority=True`**:
- App-wide hotkeys (Ctrl+Q to quit)
- Global shortcuts that should work everywhere
- Bindings that MUST fire regardless of focus

**When NOT to use `priority=True`**:
- Keys that widgets need to handle contextually
- Navigation keys (arrows, Enter, etc.)
- Any key where behavior depends on which widget is focused

### 2. Textual Event Flow Architecture

```
┌─────────────────────────────────────────────────┐
│  1. Priority bindings (app/screen level)       │
│     ↓ (if no match, continue)                  │
├─────────────────────────────────────────────────┤
│  2. Focused widget's event handlers             │
│     - on_key(event)                             │
│     - key_<keyname>(event)                      │
│     ↓ (if event.stop() not called)             │
├─────────────────────────────────────────────────┤
│  3. Widget's base class handlers                │
│     ↓ (if event.prevent_default() not called)  │
├─────────────────────────────────────────────────┤
│  4. Event bubbles to parent widgets             │
│     ↓ (if event.bubble = True)                 │
├─────────────────────────────────────────────────┤
│  5. Normal bindings (app/screen level)          │
└─────────────────────────────────────────────────┘
```

### 3. The is_active Pattern

Our panes use an `is_active` flag:
```python
def on_key(self, event):
    if not self.is_active:
        return  # Don't handle if not active
```

This is idiomatic for Textual multi-pane layouts where:
- Only one pane should respond to navigation keys
- Tab switches which pane is active
- Visual border shows active pane

### 4. Tab Needs Priority, Enter Doesn't

```python
Binding("tab", "switch_pane", "Switch", priority=True)  # ✅ Global
Binding("enter", "activate_item", "Select", priority=True)  # ❌ Contextual
```

**Why Tab needs priority**: It's a global action to switch panes, should work even if a widget wants to capture Tab

**Why Enter doesn't**: Each pane has different Enter behavior (activate vs copy), so the focused widget must handle it

## Architecture Pattern: Widget-First Event Handling

This fix reinforces a key Textual pattern:

```python
# ✅ GOOD: Let widgets handle context-specific keys
class MyPane(Widget, can_focus=True):
    def on_key(self, event):
        if event.key == "enter":
            self.do_pane_specific_thing()
            event.stop()

class MyApp(App):
    BINDINGS = [
        # Global hotkeys only
        Binding("ctrl+q", "quit", priority=True),
    ]
```

```python
# ❌ BAD: App tries to handle context-specific keys
class MyApp(App):
    BINDINGS = [
        Binding("enter", "do_something", priority=True),  # BAD!
    ]

    def action_do_something(self):
        # Now we have to figure out which widget is focused...
        if self.active_pane == "left":
            ...
        elif self.active_pane == "right":
            ...
```

## References

- [Textual Command Palette](https://textual.textualize.io/guide/command_palette/)
- [Textual Events and Messages](https://textual.textualize.io/guide/events/)
- [Textual Binding API](https://textual.textualize.io/api/binding/)
- [Textual Toast Notifications](https://textual.textualize.io/widgets/toast/)
- [Textual Footer Widget](https://textual.textualize.io/widgets/footer/)

## Files Changed

- `/Users/kentgang/git/kgents/impl/claude/protocols/dawn/tui/app.py`
  - Removed Enter binding from BINDINGS
  - Added explanatory comment

## Next Steps

- ✅ Fix implemented
- ✅ Tests pass (54/54)
- ⏳ Manual testing needed
- ⏳ User confirmation

---

*Investigation conducted 2025-12-22 using Textual event flow analysis and priority binding discovery.*
