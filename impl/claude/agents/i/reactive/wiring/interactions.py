"""
Interactive Behaviors: Focus, Keyboard Navigation, Selection, and Events.

Wave 6 of the reactive substrate - bringing interactivity to widgets.

Focus System:
- FocusState tracks which widget has focus
- Focus ring visual indicator
- Tab order navigation (forward/backward)
- Focus events in EventBus

Keyboard Navigation:
- ArrowUp/Down for agent card selection
- Enter to expand/collapse details
- Escape to unfocus
- Hotkey bindings (e.g., 'r' for refresh, 'c' for clear)

Selection State:
- Single agent selection (click/enter)
- Multi-select with Shift+Arrow or Ctrl+Click
- Selected agents list
- Bulk actions on selected agents

Interaction Events:
- Widget emits interaction events to EventBus
- Parent screens handle events and update state
- Event bubbling for nested widgets

"Interaction is dialogue. Focus is attention. Selection is intention."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Any, Callable, Generic, TypeVar

from agents.i.reactive.signal import Signal
from agents.i.reactive.wiring.subscriptions import Event, EventBus, EventType

if TYPE_CHECKING:
    pass

T = TypeVar("T")


# =============================================================================
# Focus System
# =============================================================================


class FocusDirection(Enum):
    """Direction of focus movement."""

    FORWARD = auto()  # Tab
    BACKWARD = auto()  # Shift+Tab


@dataclass(frozen=True)
class FocusableItem:
    """
    An item that can receive focus.

    Represents a widget or element in the focus order.
    """

    id: str
    tab_index: int = 0
    focusable: bool = True
    group: str = ""  # Logical grouping for skip-to-group navigation


@dataclass
class FocusState:
    """
    Tracks focus state for a set of focusable items.

    The focus state maintains:
    - Currently focused item ID
    - List of all focusable items in tab order
    - Focus ring visibility
    - Focus history for back-navigation

    Example:
        focus = FocusState()
        focus.register("agent-1", tab_index=0)
        focus.register("agent-2", tab_index=1)
        focus.register("action-btn", tab_index=2)

        focus.focus("agent-1")
        focus.move(FocusDirection.FORWARD)  # -> agent-2
        focus.move(FocusDirection.FORWARD)  # -> action-btn
        focus.move(FocusDirection.FORWARD)  # -> wraps to agent-1
    """

    _focused_id: str | None = None
    _items: dict[str, FocusableItem] = field(default_factory=dict)
    _focus_ring_visible: bool = True
    _focus_history: list[str] = field(default_factory=list)
    _history_max: int = 10
    _signal: Signal[str | None] = field(default_factory=lambda: Signal.of(None))

    @property
    def focused_id(self) -> str | None:
        """ID of currently focused item."""
        return self._focused_id

    @property
    def focus_ring_visible(self) -> bool:
        """Whether focus ring should be shown."""
        return self._focus_ring_visible

    @property
    def signal(self) -> Signal[str | None]:
        """Signal that emits focus changes."""
        return self._signal

    def register(
        self,
        item_id: str,
        tab_index: int = 0,
        focusable: bool = True,
        group: str = "",
    ) -> None:
        """
        Register a focusable item.

        Args:
            item_id: Unique identifier for the item
            tab_index: Order in tab sequence (lower = earlier)
            focusable: Whether item can receive focus
            group: Logical grouping for navigation
        """
        self._items[item_id] = FocusableItem(
            id=item_id,
            tab_index=tab_index,
            focusable=focusable,
            group=group,
        )

    def unregister(self, item_id: str) -> None:
        """Remove item from focus order."""
        if item_id in self._items:
            del self._items[item_id]
            if self._focused_id == item_id:
                self._focused_id = None
                self._signal.set(None)

    def focus(self, item_id: str) -> bool:
        """
        Focus a specific item.

        Args:
            item_id: ID of item to focus

        Returns:
            True if focus changed, False if item not focusable or not found
        """
        if item_id not in self._items:
            return False

        item = self._items[item_id]
        if not item.focusable:
            return False

        if self._focused_id != item_id:
            # Add to history before changing
            if self._focused_id:
                self._focus_history.append(self._focused_id)
                if len(self._focus_history) > self._history_max:
                    self._focus_history = self._focus_history[-self._history_max :]

            self._focused_id = item_id
            self._signal.set(item_id)

        return True

    def blur(self) -> None:
        """Remove focus from current item."""
        if self._focused_id:
            self._focus_history.append(self._focused_id)
            if len(self._focus_history) > self._history_max:
                self._focus_history = self._focus_history[-self._history_max :]
        self._focused_id = None
        self._signal.set(None)

    def move(self, direction: FocusDirection) -> str | None:
        """
        Move focus in the given direction.

        Follows tab order, wrapping at ends.

        Args:
            direction: FORWARD (Tab) or BACKWARD (Shift+Tab)

        Returns:
            ID of newly focused item, or None if no focusable items
        """
        focusable_items = self._get_sorted_focusable()
        if not focusable_items:
            return None

        # If nothing focused, start from beginning/end based on direction
        if self._focused_id is None:
            if direction == FocusDirection.FORWARD:
                target = focusable_items[0]
            else:
                target = focusable_items[-1]
            self.focus(target.id)
            return target.id

        # Find current position
        current_idx = -1
        for i, item in enumerate(focusable_items):
            if item.id == self._focused_id:
                current_idx = i
                break

        if current_idx == -1:
            # Current focused item not in list (maybe removed), reset
            target = focusable_items[0]
            self.focus(target.id)
            return target.id

        # Calculate next index with wrapping
        if direction == FocusDirection.FORWARD:
            next_idx = (current_idx + 1) % len(focusable_items)
        else:
            next_idx = (current_idx - 1) % len(focusable_items)

        target = focusable_items[next_idx]
        self.focus(target.id)
        return target.id

    def move_to_group(self, group: str) -> str | None:
        """
        Move focus to first item in a group.

        Args:
            group: Group name to focus

        Returns:
            ID of focused item, or None if group empty
        """
        group_items = [item for item in self._get_sorted_focusable() if item.group == group]
        if not group_items:
            return None

        self.focus(group_items[0].id)
        return group_items[0].id

    def back(self) -> str | None:
        """
        Return to previous focused item.

        Returns:
            ID of previous item, or None if no history
        """
        if not self._focus_history:
            return None

        prev_id = self._focus_history.pop()
        if prev_id in self._items and self._items[prev_id].focusable:
            self._focused_id = prev_id
            self._signal.set(prev_id)
            return prev_id

        # Previous item no longer valid, try again
        return self.back()

    def show_focus_ring(self, visible: bool = True) -> None:
        """Set focus ring visibility."""
        self._focus_ring_visible = visible

    def is_focused(self, item_id: str) -> bool:
        """Check if specific item is focused."""
        return self._focused_id == item_id

    def _get_sorted_focusable(self) -> list[FocusableItem]:
        """Get focusable items sorted by tab_index."""
        return sorted(
            [item for item in self._items.values() if item.focusable],
            key=lambda x: x.tab_index,
        )

    def focusable_count(self) -> int:
        """Count of focusable items."""
        return len([i for i in self._items.values() if i.focusable])


# =============================================================================
# Keyboard Navigation
# =============================================================================


class KeyCode(Enum):
    """Standard key codes for keyboard navigation."""

    # Navigation
    UP = "ArrowUp"
    DOWN = "ArrowDown"
    LEFT = "ArrowLeft"
    RIGHT = "ArrowRight"
    TAB = "Tab"
    ENTER = "Enter"
    ESCAPE = "Escape"
    SPACE = "Space"
    HOME = "Home"
    END = "End"
    PAGE_UP = "PageUp"
    PAGE_DOWN = "PageDown"

    # Common hotkeys (letters)
    KEY_A = "a"
    KEY_C = "c"
    KEY_D = "d"
    KEY_E = "e"
    KEY_R = "r"
    KEY_S = "s"
    KEY_X = "x"


@dataclass(frozen=True)
class KeyModifiers:
    """Modifier keys state."""

    shift: bool = False
    ctrl: bool = False
    alt: bool = False
    meta: bool = False  # Cmd on Mac, Win on Windows


@dataclass(frozen=True)
class KeyEvent:
    """
    A keyboard event.

    Represents a key press with modifiers.
    """

    key: KeyCode | str
    modifiers: KeyModifiers = field(default_factory=KeyModifiers)
    timestamp_ms: float = 0.0
    target_id: str | None = None

    @classmethod
    def from_key(
        cls,
        key: KeyCode | str,
        *,
        shift: bool = False,
        ctrl: bool = False,
        alt: bool = False,
        meta: bool = False,
    ) -> KeyEvent:
        """Create a key event with modifiers."""
        return cls(
            key=key,
            modifiers=KeyModifiers(shift=shift, ctrl=ctrl, alt=alt, meta=meta),
        )


@dataclass
class KeyBinding:
    """
    A binding from key combination to action.

    Example:
        binding = KeyBinding(
            key=KeyCode.KEY_R,
            action="refresh",
            description="Refresh dashboard",
            handler=lambda: dashboard.refresh(),
        )
    """

    key: KeyCode | str
    action: str
    description: str = ""
    modifiers: KeyModifiers = field(default_factory=KeyModifiers)
    handler: Callable[[], None] | None = None
    enabled: bool = True

    def matches(self, event: KeyEvent) -> bool:
        """Check if this binding matches a key event."""
        if not self.enabled:
            return False

        # Check key
        key_match = event.key == self.key
        if not key_match and isinstance(self.key, str) and isinstance(event.key, str):
            key_match = event.key.lower() == self.key.lower()

        # Check modifiers
        mods_match = (
            event.modifiers.shift == self.modifiers.shift
            and event.modifiers.ctrl == self.modifiers.ctrl
            and event.modifiers.alt == self.modifiers.alt
            and event.modifiers.meta == self.modifiers.meta
        )

        return key_match and mods_match


@dataclass
class KeyboardNav:
    """
    Keyboard navigation manager.

    Handles key events and routes them to appropriate handlers.

    Example:
        nav = KeyboardNav()

        # Register bindings
        nav.bind(KeyCode.KEY_R, "refresh", handler=dashboard.refresh)
        nav.bind(KeyCode.ESCAPE, "blur", handler=focus.blur)

        # Connect to focus system
        nav.connect_focus(focus_state)

        # Handle key events
        nav.handle(KeyEvent.from_key(KeyCode.DOWN))  # Moves focus
        nav.handle(KeyEvent.from_key(KeyCode.KEY_R))  # Refreshes
    """

    _bindings: list[KeyBinding] = field(default_factory=list)
    _focus: FocusState | None = None
    _event_bus: EventBus | None = None
    _enabled: bool = True

    def bind(
        self,
        key: KeyCode | str,
        action: str,
        description: str = "",
        handler: Callable[[], None] | None = None,
        *,
        shift: bool = False,
        ctrl: bool = False,
        alt: bool = False,
        meta: bool = False,
    ) -> None:
        """
        Register a key binding.

        Args:
            key: Key code or character
            action: Action name (for event emission)
            description: Human-readable description
            handler: Optional handler function
            shift/ctrl/alt/meta: Required modifier keys
        """
        binding = KeyBinding(
            key=key,
            action=action,
            description=description,
            modifiers=KeyModifiers(shift=shift, ctrl=ctrl, alt=alt, meta=meta),
            handler=handler,
        )
        self._bindings.append(binding)

    def unbind(self, action: str) -> None:
        """Remove all bindings for an action."""
        self._bindings = [b for b in self._bindings if b.action != action]

    def enable_action(self, action: str, enabled: bool = True) -> None:
        """Enable or disable an action."""
        for binding in self._bindings:
            if binding.action == action:
                binding.enabled = enabled

    def connect_focus(self, focus: FocusState) -> None:
        """Connect to a focus state for navigation."""
        self._focus = focus

    def connect_event_bus(self, bus: EventBus) -> None:
        """Connect to event bus for emitting events."""
        self._event_bus = bus

    def handle(self, event: KeyEvent) -> bool:
        """
        Handle a key event.

        Returns True if event was handled, False otherwise.

        Process order:
        1. Check custom bindings first
        2. Handle built-in navigation (arrows, tab)
        3. Emit unhandled events if event bus connected
        """
        if not self._enabled:
            return False

        # Check custom bindings first
        for binding in self._bindings:
            if binding.matches(event):
                if binding.handler:
                    binding.handler()
                if self._event_bus:
                    self._event_bus.publish(
                        Event(
                            type=f"keyboard.{binding.action}",
                            payload={"key": str(event.key), "action": binding.action},
                        )
                    )
                return True

        # Built-in focus navigation
        if self._focus:
            handled = self._handle_focus_nav(event)
            if handled:
                return True

        # Emit unhandled key event
        if self._event_bus:
            self._event_bus.publish(
                Event(
                    type="keyboard.unhandled",
                    payload={"key": str(event.key)},
                )
            )

        return False

    def _handle_focus_nav(self, event: KeyEvent) -> bool:
        """Handle built-in focus navigation keys."""
        if self._focus is None:
            return False

        key = event.key

        # Tab navigation
        if key == KeyCode.TAB:
            if event.modifiers.shift:
                self._focus.move(FocusDirection.BACKWARD)
            else:
                self._focus.move(FocusDirection.FORWARD)
            return True

        # Arrow navigation (also moves focus)
        if key == KeyCode.DOWN:
            self._focus.move(FocusDirection.FORWARD)
            return True

        if key == KeyCode.UP:
            self._focus.move(FocusDirection.BACKWARD)
            return True

        # Escape blurs
        if key == KeyCode.ESCAPE:
            self._focus.blur()
            return True

        # Home/End for first/last
        if key == KeyCode.HOME:
            items = self._focus._get_sorted_focusable()
            if items:
                self._focus.focus(items[0].id)
            return True

        if key == KeyCode.END:
            items = self._focus._get_sorted_focusable()
            if items:
                self._focus.focus(items[-1].id)
            return True

        return False

    def get_bindings(self) -> list[KeyBinding]:
        """Get all registered bindings."""
        return list(self._bindings)

    def get_help(self) -> list[tuple[str, str, str]]:
        """
        Get help text for all bindings.

        Returns list of (key_combo, action, description) tuples.
        """
        result = []
        for b in self._bindings:
            if not b.enabled:
                continue
            # Build key combo string
            parts = []
            if b.modifiers.ctrl:
                parts.append("Ctrl")
            if b.modifiers.alt:
                parts.append("Alt")
            if b.modifiers.shift:
                parts.append("Shift")
            if b.modifiers.meta:
                parts.append("Cmd")
            parts.append(str(b.key.value if isinstance(b.key, KeyCode) else b.key))
            key_combo = "+".join(parts)
            result.append((key_combo, b.action, b.description))
        return result


# =============================================================================
# Selection State
# =============================================================================


class SelectionMode(Enum):
    """How selection behaves."""

    SINGLE = auto()  # Only one item at a time
    MULTIPLE = auto()  # Multiple items allowed
    TOGGLE = auto()  # Click toggles, no extend


@dataclass
class SelectionState(Generic[T]):
    """
    Tracks selection of items.

    Supports single selection, multi-select with shift/ctrl,
    and range selection.

    Example:
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)

        selection.select("agent-1")
        selection.extend("agent-2")  # Add to selection
        selection.select("agent-3")  # Replace selection

        selection.select_range("agent-1", "agent-5", all_ids)  # Range select

        for agent_id in selection.selected:
            # Process selected agents
            pass
    """

    mode: SelectionMode = SelectionMode.SINGLE
    _selected: set[T] = field(default_factory=set)
    _anchor: T | None = None  # For range selection
    _signal: Signal[frozenset[T]] = field(default_factory=lambda: Signal.of(frozenset()))
    _event_bus: EventBus | None = None

    @property
    def selected(self) -> frozenset[T]:
        """Get selected items (immutable view)."""
        return frozenset(self._selected)

    @property
    def signal(self) -> Signal[frozenset[T]]:
        """Signal that emits selection changes."""
        return self._signal

    @property
    def count(self) -> int:
        """Count of selected items."""
        return len(self._selected)

    @property
    def anchor(self) -> T | None:
        """Selection anchor for range operations."""
        return self._anchor

    def connect_event_bus(self, bus: EventBus) -> None:
        """Connect to event bus for emitting events."""
        self._event_bus = bus

    def select(self, item: T) -> None:
        """
        Select an item (replacing current selection in SINGLE mode).

        In SINGLE mode: clears selection then selects item
        In MULTIPLE mode: clears selection then selects item
        In TOGGLE mode: toggles item selection
        """
        if self.mode == SelectionMode.TOGGLE:
            self.toggle(item)
            return

        self._selected.clear()
        self._selected.add(item)
        self._anchor = item
        self._emit_change()

    def extend(self, item: T) -> None:
        """
        Extend selection to include item (MULTIPLE mode only).

        In SINGLE mode: behaves like select()
        In MULTIPLE/TOGGLE mode: adds item to selection
        """
        if self.mode == SelectionMode.SINGLE:
            self.select(item)
            return

        self._selected.add(item)
        self._emit_change()

    def toggle(self, item: T) -> None:
        """
        Toggle item selection.

        In SINGLE mode: if selected, deselects; otherwise selects
        In MULTIPLE/TOGGLE mode: toggles without affecting others
        """
        if item in self._selected:
            self._selected.discard(item)
            if self._anchor == item:
                self._anchor = None
        else:
            if self.mode == SelectionMode.SINGLE:
                self._selected.clear()
            self._selected.add(item)
            self._anchor = item

        self._emit_change()

    def select_range(
        self,
        from_item: T,
        to_item: T,
        all_items: list[T],
    ) -> None:
        """
        Select a range of items.

        Selects all items between from_item and to_item (inclusive)
        in the order they appear in all_items.

        Only works in MULTIPLE mode.

        Args:
            from_item: Start of range
            to_item: End of range
            all_items: Ordered list of all selectable items
        """
        if self.mode == SelectionMode.SINGLE:
            self.select(to_item)
            return

        try:
            from_idx = all_items.index(from_item)
            to_idx = all_items.index(to_item)
        except ValueError:
            return

        start = min(from_idx, to_idx)
        end = max(from_idx, to_idx)

        for item in all_items[start : end + 1]:
            self._selected.add(item)

        self._emit_change()

    def select_all(self, all_items: list[T]) -> None:
        """Select all items (MULTIPLE mode only)."""
        if self.mode == SelectionMode.SINGLE:
            if all_items:
                self.select(all_items[0])
            return

        self._selected = set(all_items)
        self._emit_change()

    def clear(self) -> None:
        """Clear selection."""
        self._selected.clear()
        self._anchor = None
        self._emit_change()

    def is_selected(self, item: T) -> bool:
        """Check if item is selected."""
        return item in self._selected

    def _emit_change(self) -> None:
        """Emit selection change."""
        self._signal.set(frozenset(self._selected))
        if self._event_bus:
            self._event_bus.publish(
                Event(
                    type="selection.changed",
                    payload={
                        "selected": list(self._selected),
                        "count": len(self._selected),
                    },
                )
            )


# =============================================================================
# Interaction Events
# =============================================================================


class InteractionType(Enum):
    """Types of widget interactions."""

    # Focus
    FOCUS_GAINED = "focus.gained"
    FOCUS_LOST = "focus.lost"

    # Selection
    SELECTED = "selected"
    DESELECTED = "deselected"
    SELECTION_CHANGED = "selection.changed"

    # Activation
    ACTIVATED = "activated"  # Enter/click on focused
    DEACTIVATED = "deactivated"
    EXPANDED = "expanded"
    COLLAPSED = "collapsed"

    # Data
    VALUE_CHANGED = "value.changed"
    SUBMITTED = "submitted"

    # Lifecycle
    MOUNTED = "mounted"
    UNMOUNTED = "unmounted"


@dataclass(frozen=True)
class Interaction(Generic[T]):
    """
    An interaction event from a widget.

    Interactions flow UP from widgets to parents.
    Parents handle interactions and update state.

    Example:
        # Widget emits
        emit(Interaction(
            type=InteractionType.ACTIVATED,
            source_id="agent-card-1",
            payload={"agent_id": "kgent-1"},
        ))

        # Parent handles
        def on_interaction(i: Interaction):
            if i.type == InteractionType.ACTIVATED:
                expand_agent_details(i.payload["agent_id"])
    """

    type: InteractionType | str
    source_id: str
    payload: T
    bubbles: bool = True  # Whether event propagates to parents
    timestamp_ms: float = 0.0


@dataclass
class InteractionHandler:
    """
    Handler for widget interactions.

    Manages interaction subscriptions and event routing.

    Example:
        handler = InteractionHandler()

        # Subscribe to specific interaction types
        handler.on(InteractionType.ACTIVATED, handle_activation)
        handler.on("custom.event", handle_custom)

        # Subscribe to all interactions
        handler.on_any(log_interaction)

        # Emit from widgets
        handler.emit(Interaction(
            type=InteractionType.ACTIVATED,
            source_id="btn-1",
            payload={"action": "submit"},
        ))
    """

    _handlers: dict[InteractionType | str, list[Callable[[Interaction[Any]], None]]] = field(
        default_factory=lambda: {}
    )
    _global_handlers: list[Callable[[Interaction[Any]], None]] = field(default_factory=list)
    _event_bus: EventBus | None = None
    _parent: InteractionHandler | None = None

    def connect_event_bus(self, bus: EventBus) -> None:
        """Connect to event bus for cross-widget communication."""
        self._event_bus = bus

    def set_parent(self, parent: InteractionHandler) -> None:
        """Set parent handler for event bubbling."""
        self._parent = parent

    def on(
        self,
        interaction_type: InteractionType | str,
        handler: Callable[[Interaction[Any]], None],
    ) -> Callable[[], None]:
        """
        Subscribe to a specific interaction type.

        Args:
            interaction_type: Type to subscribe to
            handler: Handler function

        Returns:
            Unsubscribe function
        """
        if interaction_type not in self._handlers:
            self._handlers[interaction_type] = []
        self._handlers[interaction_type].append(handler)
        return lambda: self._handlers[interaction_type].remove(handler)

    def on_any(
        self,
        handler: Callable[[Interaction[Any]], None],
    ) -> Callable[[], None]:
        """
        Subscribe to all interactions.

        Returns:
            Unsubscribe function
        """
        self._global_handlers.append(handler)
        return lambda: self._global_handlers.remove(handler)

    def emit(self, interaction: Interaction[Any]) -> None:
        """
        Emit an interaction.

        Notifies local handlers, then bubbles to parent if bubbles=True.
        Also publishes to EventBus if connected.
        """
        # Call type-specific handlers
        for handler in self._handlers.get(interaction.type, []):
            handler(interaction)

        # Call global handlers
        for handler in self._global_handlers:
            handler(interaction)

        # Publish to EventBus
        if self._event_bus:
            event_type = (
                interaction.type.value
                if isinstance(interaction.type, InteractionType)
                else str(interaction.type)
            )
            self._event_bus.publish(
                Event(
                    type=f"interaction.{event_type}",
                    payload={
                        "source_id": interaction.source_id,
                        "payload": interaction.payload,
                    },
                    source_id=interaction.source_id,
                )
            )

        # Bubble to parent
        if interaction.bubbles and self._parent:
            self._parent.emit(interaction)


# =============================================================================
# Extended Event Types for Wave 6
# =============================================================================


class InteractiveEventType(str, Enum):
    """Extended event types for interactive behaviors."""

    # Focus events
    FOCUS_CHANGED = "focus.changed"
    FOCUS_RING_TOGGLED = "focus.ring_toggled"

    # Keyboard events
    KEY_PRESSED = "keyboard.pressed"
    HOTKEY_TRIGGERED = "keyboard.hotkey"

    # Selection events
    SELECTION_CHANGED = "selection.changed"
    SELECTION_CLEARED = "selection.cleared"

    # Action events
    BULK_ACTION = "action.bulk"
    EXPAND_TOGGLE = "action.expand_toggle"
    REFRESH_REQUESTED = "action.refresh"


# =============================================================================
# Interactive Dashboard Extension
# =============================================================================


@dataclass
class InteractiveDashboardState:
    """
    Extended dashboard state with interactivity.

    Adds focus, selection, and keyboard navigation to dashboard.
    """

    # Focus
    focus: FocusState = field(default_factory=FocusState)

    # Selection
    selection: SelectionState[str] = field(
        default_factory=lambda: SelectionState(mode=SelectionMode.MULTIPLE)
    )

    # Keyboard
    keyboard: KeyboardNav = field(default_factory=KeyboardNav)

    # Interaction handling
    interactions: InteractionHandler = field(default_factory=InteractionHandler)

    # Event bus for coordination
    event_bus: EventBus | None = None

    # Expansion state
    expanded_agents: set[str] = field(default_factory=set)

    def setup(self, event_bus: EventBus | None = None) -> None:
        """
        Initialize interactive state.

        Wires up all components and registers default bindings.
        """
        if event_bus:
            self.event_bus = event_bus
            self.selection.connect_event_bus(event_bus)
            self.keyboard.connect_event_bus(event_bus)
            self.interactions.connect_event_bus(event_bus)

        # Connect keyboard to focus
        self.keyboard.connect_focus(self.focus)

        # Register default hotkeys
        self._register_default_bindings()

        # Wire up interaction handlers
        self._setup_interaction_handlers()

    def _register_default_bindings(self) -> None:
        """Register default keyboard bindings."""
        # Refresh
        self.keyboard.bind(
            KeyCode.KEY_R,
            "refresh",
            "Refresh dashboard",
            handler=self._handle_refresh,
        )

        # Clear selection
        self.keyboard.bind(
            KeyCode.KEY_C,
            "clear_selection",
            "Clear selection",
            handler=self.selection.clear,
        )

        # Select all (Ctrl+A)
        self.keyboard.bind(
            KeyCode.KEY_A,
            "select_all",
            "Select all agents",
            ctrl=True,
        )

        # Expand/collapse (Enter)
        self.keyboard.bind(
            KeyCode.ENTER,
            "toggle_expand",
            "Expand/collapse focused agent",
            handler=self._handle_toggle_expand,
        )

        # Delete selected (Ctrl+D or Delete)
        self.keyboard.bind(
            KeyCode.KEY_D,
            "delete_selected",
            "Delete selected agents",
            ctrl=True,
        )

    def _setup_interaction_handlers(self) -> None:
        """Set up interaction handlers."""
        # Handle focus changes
        self.focus.signal.subscribe(self._on_focus_change)

        # Handle selection changes
        self.selection.signal.subscribe(self._on_selection_change)

    def _on_focus_change(self, focused_id: str | None) -> None:
        """Handle focus change."""
        if self.event_bus:
            self.event_bus.publish(
                Event(
                    type=InteractiveEventType.FOCUS_CHANGED,
                    payload={"focused_id": focused_id},
                )
            )

    def _on_selection_change(self, selected: frozenset[str]) -> None:
        """Handle selection change."""
        if self.event_bus:
            self.event_bus.publish(
                Event(
                    type=InteractiveEventType.SELECTION_CHANGED,
                    payload={"selected": list(selected), "count": len(selected)},
                )
            )

    def _handle_refresh(self) -> None:
        """Handle refresh action."""
        if self.event_bus:
            self.event_bus.publish(
                Event(
                    type=InteractiveEventType.REFRESH_REQUESTED,
                    payload={},
                )
            )

    def _handle_toggle_expand(self) -> None:
        """Handle expand/collapse of focused agent."""
        focused = self.focus.focused_id
        if not focused:
            return

        if focused in self.expanded_agents:
            self.expanded_agents.discard(focused)
            event_type = InteractionType.COLLAPSED
        else:
            self.expanded_agents.add(focused)
            event_type = InteractionType.EXPANDED

        self.interactions.emit(
            Interaction(
                type=event_type,
                source_id=focused,
                payload={"agent_id": focused},
            )
        )

    def register_agent(self, agent_id: str, tab_index: int = 0) -> None:
        """Register an agent as focusable."""
        self.focus.register(agent_id, tab_index=tab_index, group="agents")

    def unregister_agent(self, agent_id: str) -> None:
        """Unregister an agent."""
        self.focus.unregister(agent_id)
        self.selection._selected.discard(agent_id)
        self.expanded_agents.discard(agent_id)

    def handle_key(self, event: KeyEvent) -> bool:
        """Route key event through keyboard nav."""
        # Handle Shift+Arrow for extend selection
        if event.modifiers.shift:
            if event.key in (KeyCode.UP, KeyCode.DOWN):
                focused = self.focus.focused_id
                if focused:
                    self.selection.extend(focused)

        return self.keyboard.handle(event)

    def handle_click(self, agent_id: str, modifiers: KeyModifiers | None = None) -> None:
        """Handle click on an agent."""
        mods = modifiers or KeyModifiers()

        # Focus the clicked agent
        self.focus.focus(agent_id)

        # Handle selection based on modifiers
        if mods.ctrl or mods.meta:
            # Ctrl/Cmd+Click: toggle selection
            self.selection.toggle(agent_id)
        elif mods.shift:
            # Shift+Click: range select from anchor
            anchor = self.selection.anchor
            if anchor:
                # Would need list of all agent IDs for proper range select
                self.selection.extend(agent_id)
            else:
                self.selection.select(agent_id)
        else:
            # Plain click: single select
            self.selection.select(agent_id)

    def is_expanded(self, agent_id: str) -> bool:
        """Check if agent is expanded."""
        return agent_id in self.expanded_agents


# =============================================================================
# Factory Functions
# =============================================================================


def create_focus_state() -> FocusState:
    """Create a new FocusState."""
    return FocusState()


def create_keyboard_nav() -> KeyboardNav:
    """Create a new KeyboardNav."""
    return KeyboardNav()


def create_selection_state(
    mode: SelectionMode = SelectionMode.SINGLE,
) -> SelectionState[str]:
    """Create a new SelectionState."""
    return SelectionState(mode=mode)


def create_interaction_handler() -> InteractionHandler:
    """Create a new InteractionHandler."""
    return InteractionHandler()


def create_interactive_dashboard(
    event_bus: EventBus | None = None,
) -> InteractiveDashboardState:
    """
    Create an interactive dashboard state.

    Args:
        event_bus: Optional EventBus for cross-widget communication

    Returns:
        Configured InteractiveDashboardState
    """
    state = InteractiveDashboardState()
    state.setup(event_bus)
    return state
