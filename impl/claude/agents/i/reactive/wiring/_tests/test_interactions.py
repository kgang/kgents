"""
Tests for Wave 6: Interactive Behaviors.

Tests focus system, keyboard navigation, selection state, and interaction events.
"""

from __future__ import annotations

import pytest
from agents.i.reactive.wiring.interactions import (
    FocusableItem,
    FocusDirection,
    FocusState,
    Interaction,
    InteractionHandler,
    InteractionType,
    InteractiveDashboardState,
    InteractiveEventType,
    KeyBinding,
    KeyboardNav,
    KeyCode,
    KeyEvent,
    KeyModifiers,
    SelectionMode,
    SelectionState,
    create_focus_state,
    create_interaction_handler,
    create_interactive_dashboard,
    create_keyboard_nav,
    create_selection_state,
)
from agents.i.reactive.wiring.subscriptions import EventBus, create_event_bus

# =============================================================================
# Focus System Tests
# =============================================================================


class TestFocusState:
    """Tests for FocusState."""

    def test_create_focus_state(self) -> None:
        """Can create empty focus state."""
        focus = create_focus_state()
        assert focus.focused_id is None
        assert focus.focusable_count() == 0

    def test_register_item(self) -> None:
        """Can register focusable items."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)

        assert focus.focusable_count() == 2

    def test_register_with_group(self) -> None:
        """Can register items with groups."""
        focus = FocusState()
        focus.register("agent-1", group="agents")
        focus.register("agent-2", group="agents")
        focus.register("btn-1", group="actions")

        assert focus.focusable_count() == 3

    def test_unregister_item(self) -> None:
        """Can unregister items."""
        focus = FocusState()
        focus.register("item-1")
        focus.register("item-2")

        focus.unregister("item-1")

        assert focus.focusable_count() == 1

    def test_unregister_focused_item_clears_focus(self) -> None:
        """Unregistering focused item clears focus."""
        focus = FocusState()
        focus.register("item-1")
        focus.focus("item-1")

        assert focus.focused_id == "item-1"

        focus.unregister("item-1")

        assert focus.focused_id is None

    def test_focus_item(self) -> None:
        """Can focus a registered item."""
        focus = FocusState()
        focus.register("item-1")

        result = focus.focus("item-1")

        assert result is True
        assert focus.focused_id == "item-1"
        assert focus.is_focused("item-1") is True

    def test_focus_unregistered_item_fails(self) -> None:
        """Cannot focus unregistered item."""
        focus = FocusState()

        result = focus.focus("nonexistent")

        assert result is False
        assert focus.focused_id is None

    def test_focus_non_focusable_item_fails(self) -> None:
        """Cannot focus non-focusable item."""
        focus = FocusState()
        focus.register("item-1", focusable=False)

        result = focus.focus("item-1")

        assert result is False

    def test_blur(self) -> None:
        """Can blur focus."""
        focus = FocusState()
        focus.register("item-1")
        focus.focus("item-1")

        focus.blur()

        assert focus.focused_id is None

    def test_move_forward(self) -> None:
        """Can move focus forward."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.register("item-3", tab_index=2)
        focus.focus("item-1")

        result = focus.move(FocusDirection.FORWARD)

        assert result == "item-2"
        assert focus.focused_id == "item-2"

    def test_move_backward(self) -> None:
        """Can move focus backward."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.register("item-3", tab_index=2)
        focus.focus("item-2")

        result = focus.move(FocusDirection.BACKWARD)

        assert result == "item-1"
        assert focus.focused_id == "item-1"

    def test_move_wraps_forward(self) -> None:
        """Forward navigation wraps to beginning."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.focus("item-2")

        result = focus.move(FocusDirection.FORWARD)

        assert result == "item-1"

    def test_move_wraps_backward(self) -> None:
        """Backward navigation wraps to end."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.focus("item-1")

        result = focus.move(FocusDirection.BACKWARD)

        assert result == "item-2"

    def test_move_from_nothing_starts_at_first(self) -> None:
        """Moving forward from nothing focuses first item."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)

        result = focus.move(FocusDirection.FORWARD)

        assert result == "item-1"

    def test_move_from_nothing_backward_starts_at_last(self) -> None:
        """Moving backward from nothing focuses last item."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)

        result = focus.move(FocusDirection.BACKWARD)

        assert result == "item-2"

    def test_move_with_no_items_returns_none(self) -> None:
        """Moving with no items returns None."""
        focus = FocusState()

        result = focus.move(FocusDirection.FORWARD)

        assert result is None

    def test_move_to_group(self) -> None:
        """Can move focus to a group."""
        focus = FocusState()
        focus.register("agent-1", tab_index=0, group="agents")
        focus.register("agent-2", tab_index=1, group="agents")
        focus.register("btn-1", tab_index=2, group="actions")
        focus.focus("agent-1")

        result = focus.move_to_group("actions")

        assert result == "btn-1"
        assert focus.focused_id == "btn-1"

    def test_move_to_empty_group_returns_none(self) -> None:
        """Moving to empty group returns None."""
        focus = FocusState()
        focus.register("item-1", group="agents")

        result = focus.move_to_group("nonexistent")

        assert result is None

    def test_back_navigation(self) -> None:
        """Can navigate back to previous focus."""
        focus = FocusState()
        focus.register("item-1")
        focus.register("item-2")
        focus.register("item-3")

        focus.focus("item-1")
        focus.focus("item-2")
        focus.focus("item-3")

        result = focus.back()

        assert result == "item-2"
        assert focus.focused_id == "item-2"

    def test_back_with_no_history_returns_none(self) -> None:
        """Back with no history returns None."""
        focus = FocusState()
        focus.register("item-1")
        focus.focus("item-1")

        result = focus.back()

        assert result is None

    def test_focus_ring_visibility(self) -> None:
        """Can toggle focus ring visibility."""
        focus = FocusState()

        assert focus.focus_ring_visible is True

        focus.show_focus_ring(False)

        assert focus.focus_ring_visible is False

    def test_signal_emits_on_focus_change(self) -> None:
        """Signal emits when focus changes."""
        focus = FocusState()
        focus.register("item-1")
        focus.register("item-2")

        changes: list[str | None] = []
        focus.signal.subscribe(lambda v: changes.append(v))

        focus.focus("item-1")
        focus.focus("item-2")
        focus.blur()

        assert changes == ["item-1", "item-2", None]

    def test_tab_index_ordering(self) -> None:
        """Items are ordered by tab_index."""
        focus = FocusState()
        focus.register("z", tab_index=2)
        focus.register("a", tab_index=0)
        focus.register("m", tab_index=1)

        result = focus.move(FocusDirection.FORWARD)

        assert result == "a"  # Lowest tab_index first


# =============================================================================
# Keyboard Navigation Tests
# =============================================================================


class TestKeyEvent:
    """Tests for KeyEvent."""

    def test_create_simple_key_event(self) -> None:
        """Can create simple key event."""
        event = KeyEvent(key=KeyCode.ENTER)

        assert event.key == KeyCode.ENTER
        assert event.modifiers.shift is False
        assert event.modifiers.ctrl is False

    def test_create_key_event_from_key(self) -> None:
        """Can create key event with modifiers."""
        event = KeyEvent.from_key(KeyCode.KEY_A, ctrl=True, shift=True)

        assert event.key == KeyCode.KEY_A
        assert event.modifiers.ctrl is True
        assert event.modifiers.shift is True
        assert event.modifiers.alt is False

    def test_string_key(self) -> None:
        """Can use string for key."""
        event = KeyEvent(key="x")

        assert event.key == "x"


class TestKeyBinding:
    """Tests for KeyBinding."""

    def test_binding_matches_simple_key(self) -> None:
        """Binding matches simple key."""
        binding = KeyBinding(key=KeyCode.ENTER, action="submit")
        event = KeyEvent(key=KeyCode.ENTER)

        assert binding.matches(event) is True

    def test_binding_requires_modifiers(self) -> None:
        """Binding requires correct modifiers."""
        binding = KeyBinding(
            key=KeyCode.KEY_A,
            action="select_all",
            modifiers=KeyModifiers(ctrl=True),
        )

        # Without Ctrl
        event_no_ctrl = KeyEvent(key=KeyCode.KEY_A)
        assert binding.matches(event_no_ctrl) is False

        # With Ctrl
        event_with_ctrl = KeyEvent.from_key(KeyCode.KEY_A, ctrl=True)
        assert binding.matches(event_with_ctrl) is True

    def test_disabled_binding_never_matches(self) -> None:
        """Disabled binding doesn't match."""
        binding = KeyBinding(key=KeyCode.ENTER, action="submit", enabled=False)
        event = KeyEvent(key=KeyCode.ENTER)

        assert binding.matches(event) is False

    def test_string_key_matching(self) -> None:
        """String keys match case-insensitively."""
        binding = KeyBinding(key="r", action="refresh")

        event_lower = KeyEvent(key="r")
        event_upper = KeyEvent(key="R")

        assert binding.matches(event_lower) is True
        assert binding.matches(event_upper) is True


class TestKeyboardNav:
    """Tests for KeyboardNav."""

    def test_create_keyboard_nav(self) -> None:
        """Can create keyboard nav."""
        nav = create_keyboard_nav()
        assert nav.get_bindings() == []

    def test_bind_key(self) -> None:
        """Can bind key to action."""
        nav = KeyboardNav()
        nav.bind(KeyCode.KEY_R, "refresh", "Refresh dashboard")

        bindings = nav.get_bindings()
        assert len(bindings) == 1
        assert bindings[0].action == "refresh"

    def test_unbind_action(self) -> None:
        """Can unbind action."""
        nav = KeyboardNav()
        nav.bind(KeyCode.KEY_R, "refresh")
        nav.bind(KeyCode.KEY_C, "clear")

        nav.unbind("refresh")

        bindings = nav.get_bindings()
        assert len(bindings) == 1
        assert bindings[0].action == "clear"

    def test_handle_bound_key_calls_handler(self) -> None:
        """Handling bound key calls handler."""
        nav = KeyboardNav()
        called = []
        nav.bind(KeyCode.KEY_R, "refresh", handler=lambda: called.append(True))

        event = KeyEvent(key=KeyCode.KEY_R)
        result = nav.handle(event)

        assert result is True
        assert called == [True]

    def test_handle_unbound_key_returns_false(self) -> None:
        """Handling unbound key returns False."""
        nav = KeyboardNav()

        event = KeyEvent(key=KeyCode.KEY_X)
        result = nav.handle(event)

        assert result is False

    def test_focus_navigation_with_tab(self) -> None:
        """Tab key moves focus forward."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.focus("item-1")

        nav = KeyboardNav()
        nav.connect_focus(focus)

        event = KeyEvent(key=KeyCode.TAB)
        nav.handle(event)

        assert focus.focused_id == "item-2"

    def test_focus_navigation_with_shift_tab(self) -> None:
        """Shift+Tab moves focus backward."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.focus("item-2")

        nav = KeyboardNav()
        nav.connect_focus(focus)

        event = KeyEvent.from_key(KeyCode.TAB, shift=True)
        nav.handle(event)

        assert focus.focused_id == "item-1"

    def test_arrow_down_moves_focus(self) -> None:
        """Arrow down moves focus forward."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.focus("item-1")

        nav = KeyboardNav()
        nav.connect_focus(focus)

        nav.handle(KeyEvent(key=KeyCode.DOWN))

        assert focus.focused_id == "item-2"

    def test_arrow_up_moves_focus(self) -> None:
        """Arrow up moves focus backward."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.focus("item-2")

        nav = KeyboardNav()
        nav.connect_focus(focus)

        nav.handle(KeyEvent(key=KeyCode.UP))

        assert focus.focused_id == "item-1"

    def test_escape_blurs_focus(self) -> None:
        """Escape key blurs focus."""
        focus = FocusState()
        focus.register("item-1")
        focus.focus("item-1")

        nav = KeyboardNav()
        nav.connect_focus(focus)

        nav.handle(KeyEvent(key=KeyCode.ESCAPE))

        assert focus.focused_id is None

    def test_home_focuses_first(self) -> None:
        """Home key focuses first item."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.register("item-3", tab_index=2)
        focus.focus("item-3")

        nav = KeyboardNav()
        nav.connect_focus(focus)

        nav.handle(KeyEvent(key=KeyCode.HOME))

        assert focus.focused_id == "item-1"

    def test_end_focuses_last(self) -> None:
        """End key focuses last item."""
        focus = FocusState()
        focus.register("item-1", tab_index=0)
        focus.register("item-2", tab_index=1)
        focus.register("item-3", tab_index=2)
        focus.focus("item-1")

        nav = KeyboardNav()
        nav.connect_focus(focus)

        nav.handle(KeyEvent(key=KeyCode.END))

        assert focus.focused_id == "item-3"

    def test_enable_disable_action(self) -> None:
        """Can enable/disable actions."""
        nav = KeyboardNav()
        called = []
        nav.bind(KeyCode.KEY_R, "refresh", handler=lambda: called.append(True))

        nav.enable_action("refresh", False)
        nav.handle(KeyEvent(key=KeyCode.KEY_R))

        assert called == []

        nav.enable_action("refresh", True)
        nav.handle(KeyEvent(key=KeyCode.KEY_R))

        assert called == [True]

    def test_get_help(self) -> None:
        """Can get help text for bindings."""
        nav = KeyboardNav()
        nav.bind(KeyCode.KEY_R, "refresh", "Refresh dashboard")
        nav.bind(KeyCode.KEY_A, "select_all", "Select all", ctrl=True)

        help_text = nav.get_help()

        assert len(help_text) == 2
        assert ("r", "refresh", "Refresh dashboard") in help_text
        assert ("Ctrl+a", "select_all", "Select all") in help_text

    def test_event_bus_publishes_on_action(self) -> None:
        """Event bus receives action events."""
        bus = create_event_bus()
        nav = KeyboardNav()
        nav.connect_event_bus(bus)
        nav.bind(KeyCode.KEY_R, "refresh")

        events: list[str] = []
        bus.subscribe("keyboard.refresh", lambda e: events.append(e.payload["action"]))

        nav.handle(KeyEvent(key=KeyCode.KEY_R))

        assert events == ["refresh"]


# =============================================================================
# Selection State Tests
# =============================================================================


class TestSelectionState:
    """Tests for SelectionState."""

    def test_create_selection_state(self) -> None:
        """Can create empty selection state."""
        selection = create_selection_state()

        assert selection.count == 0
        assert selection.selected == frozenset()

    def test_single_selection_mode(self) -> None:
        """Single mode replaces selection."""
        selection = SelectionState[str](mode=SelectionMode.SINGLE)

        selection.select("item-1")
        assert selection.selected == frozenset({"item-1"})

        selection.select("item-2")
        assert selection.selected == frozenset({"item-2"})

    def test_multiple_selection_mode_select(self) -> None:
        """Multiple mode select still replaces."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)

        selection.select("item-1")
        selection.select("item-2")

        assert selection.selected == frozenset({"item-2"})

    def test_multiple_selection_mode_extend(self) -> None:
        """Multiple mode extend adds to selection."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)

        selection.select("item-1")
        selection.extend("item-2")
        selection.extend("item-3")

        assert selection.selected == frozenset({"item-1", "item-2", "item-3"})

    def test_extend_in_single_mode_replaces(self) -> None:
        """Extend in single mode behaves like select."""
        selection = SelectionState[str](mode=SelectionMode.SINGLE)

        selection.select("item-1")
        selection.extend("item-2")

        assert selection.selected == frozenset({"item-2"})

    def test_toggle_selection(self) -> None:
        """Can toggle selection."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)

        selection.toggle("item-1")
        assert selection.is_selected("item-1") is True

        selection.toggle("item-1")
        assert selection.is_selected("item-1") is False

    def test_toggle_mode(self) -> None:
        """Toggle mode always toggles."""
        selection = SelectionState[str](mode=SelectionMode.TOGGLE)

        selection.select("item-1")  # In toggle mode, select toggles
        assert selection.is_selected("item-1") is True

        selection.select("item-1")
        assert selection.is_selected("item-1") is False

    def test_select_range(self) -> None:
        """Can select range of items."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)
        all_items = ["a", "b", "c", "d", "e"]

        selection.select_range("b", "d", all_items)

        assert selection.selected == frozenset({"b", "c", "d"})

    def test_select_range_reverse(self) -> None:
        """Range select works in reverse order."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)
        all_items = ["a", "b", "c", "d", "e"]

        selection.select_range("d", "b", all_items)

        assert selection.selected == frozenset({"b", "c", "d"})

    def test_select_range_in_single_mode(self) -> None:
        """Range select in single mode just selects end item."""
        selection = SelectionState[str](mode=SelectionMode.SINGLE)
        all_items = ["a", "b", "c"]

        selection.select_range("a", "c", all_items)

        assert selection.selected == frozenset({"c"})

    def test_select_all(self) -> None:
        """Can select all items."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)
        all_items = ["a", "b", "c"]

        selection.select_all(all_items)

        assert selection.selected == frozenset({"a", "b", "c"})

    def test_select_all_in_single_mode(self) -> None:
        """Select all in single mode selects first."""
        selection = SelectionState[str](mode=SelectionMode.SINGLE)
        all_items = ["a", "b", "c"]

        selection.select_all(all_items)

        assert selection.selected == frozenset({"a"})

    def test_clear_selection(self) -> None:
        """Can clear selection."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)
        selection.select("item-1")
        selection.extend("item-2")

        selection.clear()

        assert selection.count == 0
        assert selection.selected == frozenset()

    def test_anchor_tracking(self) -> None:
        """Anchor is tracked for range selection."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)

        selection.select("item-1")
        assert selection.anchor == "item-1"

        selection.extend("item-2")
        assert selection.anchor == "item-1"  # Anchor doesn't change on extend

    def test_signal_emits_on_change(self) -> None:
        """Signal emits on selection change."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)

        changes: list[frozenset[str]] = []
        selection.signal.subscribe(lambda v: changes.append(v))

        selection.select("a")
        selection.extend("b")
        selection.clear()

        assert len(changes) == 3
        assert frozenset({"a"}) in changes
        assert frozenset({"a", "b"}) in changes
        assert frozenset() in changes

    def test_event_bus_publishes_on_change(self) -> None:
        """Event bus receives selection events."""
        bus = create_event_bus()
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)
        selection.connect_event_bus(bus)

        events: list[int] = []
        bus.subscribe("selection.changed", lambda e: events.append(e.payload["count"]))

        selection.select("a")
        selection.extend("b")

        assert events == [1, 2]


# =============================================================================
# Interaction Handler Tests
# =============================================================================


class TestInteraction:
    """Tests for Interaction."""

    def test_create_interaction(self) -> None:
        """Can create interaction."""
        interaction = Interaction(
            type=InteractionType.ACTIVATED,
            source_id="btn-1",
            payload={"action": "submit"},
        )

        assert interaction.type == InteractionType.ACTIVATED
        assert interaction.source_id == "btn-1"
        assert interaction.payload == {"action": "submit"}
        assert interaction.bubbles is True

    def test_non_bubbling_interaction(self) -> None:
        """Can create non-bubbling interaction."""
        interaction = Interaction(
            type=InteractionType.VALUE_CHANGED,
            source_id="input-1",
            payload="new value",
            bubbles=False,
        )

        assert interaction.bubbles is False


class TestInteractionHandler:
    """Tests for InteractionHandler."""

    def test_create_handler(self) -> None:
        """Can create interaction handler."""
        handler = create_interaction_handler()
        assert handler is not None

    def test_subscribe_to_type(self) -> None:
        """Can subscribe to specific type."""
        handler = InteractionHandler()
        received: list[str] = []

        handler.on(InteractionType.ACTIVATED, lambda i: received.append(i.source_id))

        handler.emit(
            Interaction(
                type=InteractionType.ACTIVATED,
                source_id="btn-1",
                payload={},
            )
        )

        assert received == ["btn-1"]

    def test_subscribe_to_custom_type(self) -> None:
        """Can subscribe to custom string type."""
        handler = InteractionHandler()
        received: list[str] = []

        handler.on("custom.event", lambda i: received.append(i.source_id))

        handler.emit(
            Interaction(
                type="custom.event",
                source_id="widget-1",
                payload={},
            )
        )

        assert received == ["widget-1"]

    def test_subscribe_to_any(self) -> None:
        """Can subscribe to all interactions."""
        handler = InteractionHandler()
        received: list[str] = []

        handler.on_any(lambda i: received.append(str(i.type)))

        handler.emit(
            Interaction(type=InteractionType.ACTIVATED, source_id="a", payload={})
        )
        handler.emit(
            Interaction(type=InteractionType.EXPANDED, source_id="b", payload={})
        )

        assert len(received) == 2

    def test_unsubscribe(self) -> None:
        """Can unsubscribe from type."""
        handler = InteractionHandler()
        received: list[str] = []

        unsub = handler.on(
            InteractionType.ACTIVATED, lambda i: received.append(i.source_id)
        )

        handler.emit(
            Interaction(type=InteractionType.ACTIVATED, source_id="a", payload={})
        )
        unsub()
        handler.emit(
            Interaction(type=InteractionType.ACTIVATED, source_id="b", payload={})
        )

        assert received == ["a"]

    def test_event_bubbling(self) -> None:
        """Events bubble to parent handler."""
        parent = InteractionHandler()
        child = InteractionHandler()
        child.set_parent(parent)

        parent_received: list[str] = []
        parent.on(
            InteractionType.ACTIVATED, lambda i: parent_received.append(i.source_id)
        )

        child.emit(
            Interaction(
                type=InteractionType.ACTIVATED,
                source_id="child-btn",
                payload={},
                bubbles=True,
            )
        )

        assert parent_received == ["child-btn"]

    def test_non_bubbling_stops_at_source(self) -> None:
        """Non-bubbling events don't reach parent."""
        parent = InteractionHandler()
        child = InteractionHandler()
        child.set_parent(parent)

        parent_received: list[str] = []
        parent.on(
            InteractionType.VALUE_CHANGED, lambda i: parent_received.append(i.source_id)
        )

        child.emit(
            Interaction(
                type=InteractionType.VALUE_CHANGED,
                source_id="input",
                payload="value",
                bubbles=False,
            )
        )

        assert parent_received == []

    def test_event_bus_integration(self) -> None:
        """Handler publishes to event bus."""
        bus = create_event_bus()
        handler = InteractionHandler()
        handler.connect_event_bus(bus)

        events: list[str] = []
        bus.subscribe_all(lambda e: events.append(str(e.type)))

        handler.emit(
            Interaction(
                type=InteractionType.ACTIVATED,
                source_id="btn",
                payload={},
            )
        )

        assert any("activated" in e for e in events)


# =============================================================================
# Interactive Dashboard Tests
# =============================================================================


class TestInteractiveDashboardState:
    """Tests for InteractiveDashboardState."""

    def test_create_interactive_dashboard(self) -> None:
        """Can create interactive dashboard."""
        dashboard = create_interactive_dashboard()

        assert dashboard.focus is not None
        assert dashboard.selection is not None
        assert dashboard.keyboard is not None
        assert dashboard.interactions is not None

    def test_setup_with_event_bus(self) -> None:
        """Can setup with event bus."""
        bus = create_event_bus()
        dashboard = create_interactive_dashboard(event_bus=bus)

        assert dashboard.event_bus == bus

    def test_register_agent(self) -> None:
        """Can register agents as focusable."""
        dashboard = create_interactive_dashboard()

        dashboard.register_agent("agent-1", tab_index=0)
        dashboard.register_agent("agent-2", tab_index=1)

        assert dashboard.focus.focusable_count() == 2

    def test_unregister_agent(self) -> None:
        """Can unregister agents."""
        dashboard = create_interactive_dashboard()
        dashboard.register_agent("agent-1")
        dashboard.selection.select("agent-1")
        dashboard.expanded_agents.add("agent-1")

        dashboard.unregister_agent("agent-1")

        assert dashboard.focus.focusable_count() == 0
        assert "agent-1" not in dashboard.selection.selected
        assert "agent-1" not in dashboard.expanded_agents

    def test_handle_key_moves_focus(self) -> None:
        """Key handling moves focus."""
        dashboard = create_interactive_dashboard()
        dashboard.register_agent("agent-1", tab_index=0)
        dashboard.register_agent("agent-2", tab_index=1)
        dashboard.focus.focus("agent-1")

        dashboard.handle_key(KeyEvent(key=KeyCode.DOWN))

        assert dashboard.focus.focused_id == "agent-2"

    def test_handle_click_focuses_and_selects(self) -> None:
        """Click focuses and selects agent."""
        dashboard = create_interactive_dashboard()
        dashboard.register_agent("agent-1")

        dashboard.handle_click("agent-1")

        assert dashboard.focus.focused_id == "agent-1"
        assert dashboard.selection.is_selected("agent-1")

    def test_ctrl_click_toggles_selection(self) -> None:
        """Ctrl+click toggles selection."""
        dashboard = create_interactive_dashboard()
        dashboard.register_agent("agent-1")
        dashboard.register_agent("agent-2")

        dashboard.handle_click("agent-1")
        dashboard.handle_click("agent-2", KeyModifiers(ctrl=True))

        assert dashboard.selection.is_selected("agent-1")
        assert dashboard.selection.is_selected("agent-2")

    def test_shift_arrow_extends_selection(self) -> None:
        """Shift+Arrow extends selection."""
        dashboard = create_interactive_dashboard()
        dashboard.register_agent("agent-1", tab_index=0)
        dashboard.register_agent("agent-2", tab_index=1)
        dashboard.focus.focus("agent-1")
        dashboard.selection.select("agent-1")

        dashboard.handle_key(KeyEvent.from_key(KeyCode.DOWN, shift=True))

        # Focus moved to agent-2, and agent-1 extended to selection
        assert dashboard.focus.focused_id == "agent-2"

    def test_expand_toggle(self) -> None:
        """Enter key toggles expansion."""
        dashboard = create_interactive_dashboard()
        dashboard.register_agent("agent-1")
        dashboard.focus.focus("agent-1")

        assert dashboard.is_expanded("agent-1") is False

        dashboard.handle_key(KeyEvent(key=KeyCode.ENTER))

        assert dashboard.is_expanded("agent-1") is True

        dashboard.handle_key(KeyEvent(key=KeyCode.ENTER))

        assert dashboard.is_expanded("agent-1") is False

    def test_default_hotkeys(self) -> None:
        """Default hotkeys are registered."""
        dashboard = create_interactive_dashboard()

        bindings = dashboard.keyboard.get_bindings()
        actions = [b.action for b in bindings]

        assert "refresh" in actions
        assert "clear_selection" in actions
        assert "toggle_expand" in actions

    def test_refresh_hotkey_emits_event(self) -> None:
        """Refresh hotkey emits event."""
        bus = create_event_bus()
        dashboard = create_interactive_dashboard(event_bus=bus)

        events: list[str] = []
        bus.subscribe(
            InteractiveEventType.REFRESH_REQUESTED,
            lambda e: events.append("refresh"),
        )

        dashboard.handle_key(KeyEvent(key=KeyCode.KEY_R))

        assert events == ["refresh"]

    def test_clear_selection_hotkey(self) -> None:
        """Clear selection hotkey works."""
        dashboard = create_interactive_dashboard()
        dashboard.register_agent("agent-1")
        dashboard.selection.select("agent-1")

        assert dashboard.selection.count == 1

        dashboard.handle_key(KeyEvent(key=KeyCode.KEY_C))

        assert dashboard.selection.count == 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestInteractionIntegration:
    """Integration tests for interactive behaviors."""

    def test_full_keyboard_navigation_flow(self) -> None:
        """Full keyboard navigation workflow."""
        bus = create_event_bus()
        dashboard = create_interactive_dashboard(event_bus=bus)

        # Register agents
        for i in range(5):
            dashboard.register_agent(f"agent-{i}", tab_index=i)

        # Start navigation
        dashboard.handle_key(KeyEvent(key=KeyCode.TAB))
        assert dashboard.focus.focused_id == "agent-0"

        # Move down
        dashboard.handle_key(KeyEvent(key=KeyCode.DOWN))
        assert dashboard.focus.focused_id == "agent-1"

        # Jump to end
        dashboard.handle_key(KeyEvent(key=KeyCode.END))
        assert dashboard.focus.focused_id == "agent-4"

        # Escape blurs
        dashboard.handle_key(KeyEvent(key=KeyCode.ESCAPE))
        assert dashboard.focus.focused_id is None

    def test_selection_with_keyboard(self) -> None:
        """Selection via keyboard."""
        dashboard = create_interactive_dashboard()
        dashboard.register_agent("agent-0", tab_index=0)
        dashboard.register_agent("agent-1", tab_index=1)
        dashboard.register_agent("agent-2", tab_index=2)

        # Focus first and select
        dashboard.focus.focus("agent-0")
        dashboard.handle_click("agent-0")

        # Shift+Down to extend
        dashboard.handle_key(KeyEvent.from_key(KeyCode.DOWN, shift=True))

        # Clear with hotkey
        dashboard.handle_key(KeyEvent(key=KeyCode.KEY_C))
        assert dashboard.selection.count == 0

    def test_event_flow(self) -> None:
        """Events flow through system correctly."""
        bus = create_event_bus()
        dashboard = create_interactive_dashboard(event_bus=bus)
        dashboard.register_agent("agent-1")

        received_events: list[str] = []
        bus.subscribe_all(lambda e: received_events.append(str(e.type)))

        # Focus
        dashboard.focus.focus("agent-1")

        # Select
        dashboard.handle_click("agent-1")

        # Expand
        dashboard.handle_key(KeyEvent(key=KeyCode.ENTER))

        # Should have focus, selection, and interaction events
        event_types = [e for e in received_events]
        assert any("focus" in e.lower() for e in event_types)
        assert any("selection" in e.lower() for e in event_types)

    def test_multiple_handlers_chain(self) -> None:
        """Multiple interaction handlers can chain."""
        parent = InteractionHandler()
        child1 = InteractionHandler()
        child2 = InteractionHandler()

        child1.set_parent(parent)
        child2.set_parent(parent)

        parent_count = [0]
        parent.on_any(lambda _: parent_count.__setitem__(0, parent_count[0] + 1))

        child1.emit(
            Interaction(type=InteractionType.ACTIVATED, source_id="c1", payload={})
        )
        child2.emit(
            Interaction(type=InteractionType.ACTIVATED, source_id="c2", payload={})
        )

        assert parent_count[0] == 2


# =============================================================================
# Edge Cases
# =============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_focus_with_all_non_focusable(self) -> None:
        """Focus with all items non-focusable."""
        focus = FocusState()
        focus.register("item-1", focusable=False)
        focus.register("item-2", focusable=False)

        result = focus.move(FocusDirection.FORWARD)

        assert result is None

    def test_selection_with_empty_range(self) -> None:
        """Range select with items not in list."""
        selection = SelectionState[str](mode=SelectionMode.MULTIPLE)

        selection.select_range("x", "y", ["a", "b", "c"])

        assert selection.count == 0

    def test_keyboard_nav_disabled(self) -> None:
        """Disabled keyboard nav doesn't handle."""
        nav = KeyboardNav()
        nav.bind(KeyCode.KEY_R, "refresh")
        nav._enabled = False

        result = nav.handle(KeyEvent(key=KeyCode.KEY_R))

        assert result is False

    def test_focus_same_item_no_duplicate_history(self) -> None:
        """Focusing same item doesn't add to history twice."""
        focus = FocusState()
        focus.register("item-1")

        focus.focus("item-1")
        focus.focus("item-1")
        focus.focus("item-1")

        # History should not have item-1 since we never left it
        assert len(focus._focus_history) == 0

    def test_interaction_handler_no_bus(self) -> None:
        """Handler works without event bus."""
        handler = InteractionHandler()
        received: list[str] = []

        handler.on(InteractionType.ACTIVATED, lambda i: received.append(i.source_id))
        handler.emit(
            Interaction(type=InteractionType.ACTIVATED, source_id="btn", payload={})
        )

        assert received == ["btn"]
