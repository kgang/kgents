---
path: docs/skills/zenportal-patterns
status: active
progress: 100
last_touched: 2025-12-22
touched_by: claude-opus-4
blocking: []
enables: [dawn-cockpit]
session_notes: |
  Extracted from thorough audit of ZenPortal (~/git/zenportal), the spiritual
  predecessor to kgents. 23 patterns identified that transfer to kg dawn and
  other TUI work. ZenPortal has ~21K lines, 361 tests, years of daily use.
phase_ledger:
  AUDIT: complete
  EXTRACTION: complete
---

# Skill: ZenPortal Patterns (TUI Excellence)

> *"The cockpit doesn't fly the plane. The pilot flies the plane. The cockpit just makes it easy."*

**Difficulty**: Intermediate
**Prerequisites**: `elastic-ui-patterns.md`, `crown-jewel-patterns.md`
**Source**: Audit of ZenPortal (Kent's daily session manager, production-grade TUI)

---

## Overview

ZenPortal is a production-grade Textual TUI that Kent uses daily to manage Claude Code sessions. This skill extracts 23 patterns that make it excellent, organized into categories that apply to any TUI development.

**Key Insight**: ZenPortal is a session manager; kg dawn is a focus manager. Different domains, but the UX patterns transfer beautifully.

---

## Pattern 1: DI Container for Services

**Problem**: Services created ad-hoc lead to inconsistent state and testing difficulties.

**Wrong**: Ad-hoc creation
```python
# Scattered across codebase
fm = FocusManager()
sl = SnippetLibrary()
# No guarantee these are the same instances used elsewhere
```

**Right**: Container owns services
```python
@dataclass
class Services:
    """DI Container - all services wired at startup."""
    focus: FocusManager
    snippets: SnippetLibrary
    witness: WitnessClient | None  # Optional dependencies
    config: ConfigManager
    state: StateService

    @classmethod
    def create(cls) -> Services:
        """Wire up all dependencies at startup."""
        config = ConfigManager.load()
        state = StateService(config.state_path)
        return cls(
            focus=FocusManager(state),
            snippets=SnippetLibrary(state),
            witness=WitnessClient.connect() if config.witness_enabled else None,
            config=config,
            state=state,
        )
```

**Benefits**:
- Single source of truth for all services
- Easy to mock entire container for testing
- Lifecycle management in one place

---

## Pattern 2: State Persistence with Atomic Writes

**Problem**: State lost on restart, or corrupted on crash.

**Wrong**: Direct file writes
```python
def save(self):
    with open(self.path, "w") as f:
        json.dump(self.state, f)  # Crash here = corrupted file
```

**Right**: Atomic temp-file + rename
```python
def save(self) -> None:
    """Atomic write with temp file + rename."""
    temp_path = self.path.with_suffix(".tmp")
    try:
        with open(temp_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)
        temp_path.rename(self.path)  # POSIX atomic
    except Exception:
        temp_path.unlink(missing_ok=True)
        raise
```

**ZenPortal adds**:
- JSONL append-only history: `~/.zen_portal/history/YYYY-MM-DD.jsonl`
- Thread-safe with `RLock` for concurrent access
- Selection and ordering persisted separately from data

---

## Pattern 3: EventBus for Cross-Component Communication

**Problem**: Components tightly coupled through direct method calls.

**Wrong**: Direct calls
```python
def on_copy(self):
    self.garden.add_event("Copied")  # Garden must exist, breaks testing
    self.witness.mark("copied")       # Coupling everywhere
```

**Right**: EventBus pub/sub
```python
class EventBus:
    _subscribers: dict[type[Event], list[EventHandler]] = {}

    def emit(self, event: Event) -> None:
        for handler in self._subscribers.get(type(event), []):
            try:
                handler(event)
            except Exception:
                pass  # Error isolation

# Usage
bus.emit(SnippetCopiedEvent(snippet_id="abc", content="..."))
# Garden subscribes independently
# Witness subscribes independently
# Components decoupled
```

---

## Pattern 4: Keyboard-First Navigation

**Problem**: Arrow keys require hand travel; inconsistent with terminal conventions.

**Wrong**: Arrows only
```python
BINDINGS = [
    Binding("up", "move_up"),
    Binding("down", "move_down"),
]
```

**Right**: Home-row keys as primary, arrows as aliases
```python
BINDINGS = [
    Binding("j", "move_down", "↓"),
    Binding("k", "move_up", "↑"),
    Binding("down", "move_down", show=False),  # Alias
    Binding("up", "move_up", show=False),      # Alias
]
```

**ZenPortal extends**:
- `l`/`space` enters move mode (reorder items)
- `/` enters search mode (fuzzy filter)
- `i` enters insert mode (send keystrokes to tmux)
- `Esc` exits any mode

---

## Pattern 5: Visible Copy Confirmation

**Problem**: Silent operations leave users uncertain if action succeeded.

**Wrong**: Silent copy
```python
def _copy_selected(self):
    pyperclip.copy(content)
    # Nothing happens visually - did it work?
```

**Right**: Multiple feedback channels
```python
def _copy_selected(self):
    pyperclip.copy(content)

    # 1. Garden event (persistent)
    garden = self.app.query_one("#garden-view")
    garden.add_event(f"📋 Copied: {snippet.label}")

    # 2. Notification toast (ephemeral, 3s auto-dismiss)
    self.app.notify(f"Copied: {content[:30]}...", severity="success")

    # 3. Message for parent handling
    self.post_message(self.SnippetCopied(snippet, content))
```

---

## Pattern 6: Elastic Width Truncation

**Problem**: Long labels overflow or cause layout jitter.

**Wrong**: Fixed display
```python
def render(self):
    return f"{self.icon} {self.name} {self.age}"  # Overflows
```

**Right**: Width-aware truncation
```python
def render(self):
    available = self.size.width - 4  # Padding
    if available >= 25:
        # Full: icon + name + age
        name = self.name[:available - 8]
        return f"{self.icon} {name} {self.age}"
    else:
        # Compact: icon + name only
        name = self.name[:available - 2]
        return f"{self.icon} {name}"
```

**ZenPortal pattern**: Age display ("3m", "1h", "2d") hidden when narrow.

---

## Pattern 7: Status Glyphs for Instant Recognition

**Problem**: Text status labels require reading; slow to scan.

**Wrong**: Text labels
```python
status_text = "RUNNING" if active else "STOPPED"
```

**Right**: Single-character glyphs
```python
STATUS_GLYPHS = {
    SessionState.RUNNING: "▪",   # Filled = active
    SessionState.COMPLETED: "▫", # Empty = inactive
    SessionState.PAUSED: "◐",    # Half = suspended
    SessionState.FAILED: "·",    # Dot = error
}
```

**Benefits**: Scannable at a glance, language-independent, compact.

---

## Pattern 8: Notification Toast System

**Problem**: Status messages compete for space in main UI.

**ZenPortal Pattern**:
```python
class NotificationRack(Widget):
    """Bottom-left notification area with auto-dismiss."""

    def notify(self, message: str, severity: str = "info", timeout: float = 3.0):
        toast = Toast(message, severity)
        self.mount(toast)
        self.set_timer(timeout, lambda: toast.remove())
```

**Characteristics**:
- Position: bottom-left (near action source)
- Auto-dismiss: 3 seconds default
- Severity colors: success (green), warning (yellow), error (red)
- Non-blocking: doesn't interrupt workflow

---

## Pattern 9: Draggable Splitter

**Problem**: Fixed pane sizes don't match user preference.

**ZenPortal Pattern**:
```python
class VerticalSplitter(Widget):
    """Draggable divider between panes."""

    DEFAULT_CSS = """
    VerticalSplitter {
        width: 1;
        background: $surface-lighten-1;
    }
    VerticalSplitter:hover {
        background: $primary;
        cursor: ew-resize;
    }
    """

    def on_mouse_down(self, event):
        self.capture_mouse()
        self._dragging = True

    def on_mouse_move(self, event):
        if self._dragging:
            self.post_message(SplitterMoved(event.x))
```

---

## Pattern 10: Move Mode for Reordering

**Problem**: Can't reorder items without external tools.

**ZenPortal Pattern**:
```python
class SessionList(Widget):
    move_mode: reactive[bool] = reactive(False)

    def action_enter_move_mode(self):
        self.move_mode = True
        self.hint = "move mode: j/k to reorder, space/esc to exit"

    def on_key(self, event):
        if self.move_mode:
            if event.key in ("j", "down"):
                self._swap_down()
            elif event.key in ("k", "up"):
                self._swap_up()
            elif event.key in ("space", "escape"):
                self.move_mode = False
                self._save_order()
```

---

## Pattern 11: Search Mode with Fuzzy Filter

**Problem**: Long lists require scrolling to find items.

**ZenPortal Pattern**:
```python
class SearchableList(Widget):
    search_mode: reactive[bool] = reactive(False)
    search_query: reactive[str] = reactive("")

    @property
    def filtered_items(self) -> list[Item]:
        if not self.search_query:
            return self.items
        q = self.search_query.lower()
        return [i for i in self.items if q in i.name.lower()]

    def on_key(self, event):
        if event.key == "slash":
            self.search_mode = True
            self.query_one("#search-input").focus()
```

---

## Pattern 12: Context-Aware Hint Bar

**Problem**: Users don't know available actions.

**ZenPortal Pattern**:
```python
class HintBar(Static):
    """Bottom status line that changes based on context."""

    HINTS = {
        "normal": "j/k: navigate  n: new  x: kill  q: quit",
        "search": "↑↓: navigate  enter: select  esc: cancel",
        "move": "j/k: reorder  space/esc: exit",
        "insert": "arrows: navigate  ctrl+c: signal  esc: exit",
    }

    def set_mode(self, mode: str):
        self.update(self.HINTS.get(mode, self.HINTS["normal"]))
```

---

## Pattern 13: Selection Persistence

**Problem**: Cursor position lost on restart.

**ZenPortal Pattern**:
```python
class PortalState:
    sessions: list[SessionRecord]
    session_order: list[str]      # Explicit ordering
    selected_session_id: str | None  # Cursor position

    def save(self):
        # All three persisted together
        ...

    def restore_selection(self, list_widget):
        if self.selected_session_id:
            idx = self._find_index(self.selected_session_id)
            list_widget.selected_index = idx
```

---

## Pattern 14: Human-Friendly Age Display

**Problem**: ISO timestamps are unreadable at a glance.

**Right**: Relative age
```python
def age_display(self) -> str:
    """Human-friendly age since last touch."""
    age = datetime.now() - self.last_touched
    if age < timedelta(minutes=1):
        return "now"
    elif age < timedelta(hours=1):
        return f"{int(age.seconds / 60)}m"
    elif age < timedelta(days=1):
        return f"{int(age.seconds / 3600)}h"
    elif age < timedelta(days=7):
        return f"{age.days}d"
    else:
        return f"{age.days // 7}w"
```

---

## Pattern 15: Async Service Separation

**Problem**: Sync subprocess calls block UI thread.

**ZenPortal Pattern**:
```python
# services/tmux.py - Sync operations
class TmuxService:
    def list_sessions(self) -> list[str]:
        return subprocess.run(["tmux", "ls"], ...)

# services/tmux_async.py - Async wrapper
class AsyncTmuxService:
    def __init__(self, sync: TmuxService):
        self._sync = sync

    async def list_sessions(self) -> list[str]:
        return await asyncio.to_thread(self._sync.list_sessions)
```

**Benefits**: UI stays responsive, clean separation of concerns.

---

## Pattern 16: Graceful Degradation with Tuples

**Problem**: Exceptions disrupt flow; empty returns hide errors.

**ZenPortal Pattern**:
```python
def create_session(self, name: str) -> tuple[Session | None, str | None]:
    """Returns (session, error) - never raises."""
    try:
        session = self._do_create(name)
        return (session, None)
    except TmuxError as e:
        return (None, f"Tmux error: {e}")
    except Exception as e:
        return (None, f"Unexpected: {e}")

# Usage
session, error = manager.create_session("work")
if error:
    self.notify(error, severity="error")
else:
    self.select(session)
```

---

## Pattern 17: Active Pane Indicator

**Problem**: Not obvious which pane has focus.

**Wrong**: Subtle border change
```css
#pane.active { border: double cyan; }  /* Easy to miss */
```

**Right**: Multiple indicators
```python
def watch_is_active(self, active: bool):
    title = self.query_one("#title")
    if active:
        # 1. Reverse video title (unmistakable)
        title.update("[bold reverse cyan] 📍 FOCUS [/bold reverse cyan]")
        # 2. Border change (secondary)
        self.add_class("active")
    else:
        title.update("📍 FOCUS")
        self.remove_class("active")
```

---

## Pattern 18: Base Class for Selectable Panes

**Problem**: Duplicate navigation logic across panes.

**Right**: Extract common behavior
```python
class SelectablePane(Widget, can_focus=True):
    """Base class for panes with keyboard-navigable items."""

    is_active: reactive[bool] = reactive(False)
    selected_index: reactive[int] = reactive(0)

    @property
    @abstractmethod
    def items(self) -> list[Any]:
        """Subclass provides items."""

    def select_next(self):
        if self.items:
            self.selected_index = min(len(self.items) - 1, self.selected_index + 1)

    def select_previous(self):
        if self.items:
            self.selected_index = max(0, self.selected_index - 1)

    def on_key(self, event: Key):
        if not self.is_active:
            return
        match event.key:
            case "up" | "k": self.select_previous(); event.stop()
            case "down" | "j": self.select_next(); event.stop()
            case "enter": self.activate_selected(); event.stop()
            case key if key in "123456789":
                idx = int(key) - 1
                if idx < len(self.items):
                    self.selected_index = idx
                    event.stop()
```

---

## Summary: The 23 Patterns

| # | Pattern | Category |
|---|---------|----------|
| 1 | DI Container | Architecture |
| 2 | Atomic Writes | Persistence |
| 3 | EventBus | Architecture |
| 4 | Keyboard Navigation | UX |
| 5 | Copy Confirmation | Feedback |
| 6 | Elastic Width | Layout |
| 7 | Status Glyphs | Visual |
| 8 | Notification Toasts | Feedback |
| 9 | Draggable Splitter | Layout |
| 10 | Move Mode | UX |
| 11 | Search Mode | UX |
| 12 | Hint Bar | UX |
| 13 | Selection Persistence | Persistence |
| 14 | Age Display | Visual |
| 15 | Async Separation | Architecture |
| 16 | Graceful Degradation | Error Handling |
| 17 | Active Pane Indicator | Visual |
| 18 | SelectablePane Base | Code Quality |
| 19 | 3-Tier Config | Configuration |
| 20 | JSONL History | Audit |
| 21 | Thread-Safe State | Concurrency |
| 22 | Reactive Primitives | State |
| 23 | Message Handlers | Events |

---

## Applying to kg dawn

**Immediate** (Kent's priorities):
1. Pattern 5: Copy confirmation → Wire to Garden + notify()
2. Pattern 4: Keyboard navigation → Add j/k bindings
3. Add focus modal → New widget needed

**Next Phase**:
1. Pattern 2: State persistence → D-gent integration
2. Pattern 13: Selection persistence → Save cursor position
3. Pattern 18: SelectablePane → Extract from both panes

---

*Extracted: 2025-12-22 | Source: ~/git/zenportal | Target: kg dawn*
