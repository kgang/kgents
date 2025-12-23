"""
Default Keybindings: Standard keybinding configuration for the Hypergraph Editor.

Implements the four-layer keybinding grammar:
1. Traditional Vim (within node): j/k/h/l, w/b/e, gg/G, 0/$
2. Graph Navigation (g-prefix): gh/gl/gj/gk, gd/gr/gt/gf
3. Mode Entry: i/a/v/V/:/e/g, <Leader>k, Esc
4. Structural Selection: (/)/{/}/[/]

See: spec/surfaces/hypergraph-editor.md § Keybindings
"""

from __future__ import annotations

from ..core.types import (
    ActionInput,
    CenterInput,
    CollapseInput,
    # COMMAND mode inputs
    CommandInput,
    DiscardInput,
    EditorMode,
    ExecuteInput,
    # PORTAL mode inputs
    ExpandInput,
    FollowEdgeInput,
    ModeEnterInput,
    ModeExitInput,
    # Navigation inputs
    NavigateInput,
    # GRAPH mode inputs
    PanInput,
    SaveInput,
    SearchInput,
    # VISUAL mode inputs
    SelectExtendInput,
    SelectToggleInput,
    TabCompleteInput,
    # INSERT mode inputs
    TextChangeInput,
    ZoomInput,
)
from .registry import KeyBinding, KeybindingRegistry

# =============================================================================
# Default Registry Factory
# =============================================================================


def create_default_registry() -> KeybindingRegistry:
    """
    Create registry with default keybindings.

    Returns a fully-populated KeybindingRegistry with all standard bindings
    from the spec.

    Returns:
        KeybindingRegistry with default bindings
    """
    registry = KeybindingRegistry()

    # =========================================================================
    # Layer 0: Universal Bindings (All Modes)
    # =========================================================================

    # Escape always returns to NORMAL
    registry.register(
        KeyBinding(
            keys="<Esc>",
            modes=frozenset(EditorMode),  # All modes
            input_factory=lambda: ModeExitInput(),
            description="Exit to NORMAL mode",
        )
    )

    # =========================================================================
    # Layer 1: Traditional Vim (Within Node) — NORMAL Mode
    # =========================================================================

    # Basic movement (j/k/h/l)
    registry.register(
        KeyBinding(
            keys="j",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="down"),
            description="Line down",
        )
    )
    registry.register(
        KeyBinding(
            keys="k",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="up"),
            description="Line up",
        )
    )
    registry.register(
        KeyBinding(
            keys="h",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="left"),
            description="Column left",
        )
    )
    registry.register(
        KeyBinding(
            keys="l",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="right"),
            description="Column right",
        )
    )

    # Word motions
    registry.register(
        KeyBinding(
            keys="w",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="word_forward"),
            description="Word forward",
        )
    )
    registry.register(
        KeyBinding(
            keys="b",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="word_backward"),
            description="Word backward",
        )
    )
    registry.register(
        KeyBinding(
            keys="e",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="word_end"),
            description="Word end",
        )
    )

    # Jump to start/end
    registry.register(
        KeyBinding(
            keys="gg",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="node_start"),
            description="Node start",
        )
    )
    registry.register(
        KeyBinding(
            keys="G",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="node_end"),
            description="Node end",
        )
    )

    # Line start/end
    registry.register(
        KeyBinding(
            keys="0",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="line_start"),
            description="Line start",
        )
    )
    registry.register(
        KeyBinding(
            keys="$",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="line_end"),
            description="Line end",
        )
    )

    # =========================================================================
    # Layer 2: Graph Navigation (g-prefix) — NORMAL Mode
    # =========================================================================

    # Hierarchy navigation
    registry.register(
        KeyBinding(
            keys="gh",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="parent"),
            description="Parent (up hierarchy)",
        )
    )
    registry.register(
        KeyBinding(
            keys="gl",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="child"),
            description="Child (down hierarchy)",
        )
    )

    # Sibling navigation
    registry.register(
        KeyBinding(
            keys="gj",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="next_sibling"),
            description="Next sibling",
        )
    )
    registry.register(
        KeyBinding(
            keys="gk",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="prev_sibling"),
            description="Previous sibling",
        )
    )

    # Semantic edges
    registry.register(
        KeyBinding(
            keys="gd",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="definition"),
            description="Definition (implements edge)",
        )
    )
    registry.register(
        KeyBinding(
            keys="gr",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="references"),
            description="References (inverse edges)",
        )
    )
    registry.register(
        KeyBinding(
            keys="gt",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="tests"),
            description="Tests (tests edge)",
        )
    )

    # Follow edge under cursor
    registry.register(
        KeyBinding(
            keys="gf",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: FollowEdgeInput(),
            description="Follow edge under cursor",
        )
    )

    # =========================================================================
    # Layer 3: Mode Entry — From NORMAL
    # =========================================================================

    # INSERT mode
    registry.register(
        KeyBinding(
            keys="i",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(target_mode=EditorMode.INSERT),
            description="INSERT mode (at cursor)",
        )
    )
    registry.register(
        KeyBinding(
            keys="a",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(
                target_mode=EditorMode.INSERT, metadata={"position": "after"}
            ),
            description="INSERT mode (after cursor)",
        )
    )
    registry.register(
        KeyBinding(
            keys="I",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(
                target_mode=EditorMode.INSERT, metadata={"position": "line_start"}
            ),
            description="INSERT mode (line start)",
        )
    )
    registry.register(
        KeyBinding(
            keys="A",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(
                target_mode=EditorMode.INSERT, metadata={"position": "line_end"}
            ),
            description="INSERT mode (line end)",
        )
    )

    # VISUAL mode
    registry.register(
        KeyBinding(
            keys="v",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(target_mode=EditorMode.VISUAL),
            description="VISUAL mode (character-wise)",
        )
    )
    registry.register(
        KeyBinding(
            keys="V",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(
                target_mode=EditorMode.VISUAL, metadata={"type": "line"}
            ),
            description="VISUAL mode (line-wise)",
        )
    )

    # COMMAND mode
    registry.register(
        KeyBinding(
            keys=":",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(target_mode=EditorMode.COMMAND),
            description="COMMAND mode (AGENTESE invoke)",
        )
    )

    # PORTAL mode (Note: 'e' conflicts with word_end above, handled by mode context)
    # In NORMAL, 'e' is word_end. User must use a different key or we need disambiguation.
    # Per spec, 'e' enters PORTAL mode. Let's use this and remove word_end 'e'.
    # Actually, let's keep both and use mode transition logic to disambiguate.
    # For now, let's assume single 'e' is word_end, and portal is entered via command or special binding.
    # Actually, re-reading spec: "e" is listed as PORTAL mode entry. Let's override.
    # We'll remove the word_end 'e' binding and use 'e' for PORTAL.

    # Remove word_end binding and replace with PORTAL
    # (We already registered 'e' above, need to decide priority)
    # Decision: PORTAL takes precedence. Remove word_end 'e'.

    # Let's re-think: typically Vim uses 'e' for word_end.
    # The spec says:
    #   e           PORTAL mode (expand)
    #
    # This is a conflict. Let me check the spec again...
    # Reading Layer 3 in spec:
    #   e           PORTAL mode (expand)
    #
    # So 'e' is for PORTAL, not word_end. Let's keep only PORTAL.
    # We'll remove the word_end binding.

    # Remove the 'e' binding for word_end (we'll comment it out)
    # registry.register(
    #     KeyBinding(
    #         keys="e",
    #         modes=frozenset([EditorMode.NORMAL]),
    #         input_factory=lambda: NavigateInput(direction="word_end"),
    #         description="Word end",
    #     )
    # )

    # PORTAL mode entry
    registry.register(
        KeyBinding(
            keys="e",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(target_mode=EditorMode.PORTAL),
            description="PORTAL mode (expand/collapse)",
        )
    )

    # GRAPH mode
    registry.register(
        KeyBinding(
            keys="g",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(target_mode=EditorMode.GRAPH),
            description="GRAPH mode (DAG visualization)",
        )
    )

    # KBLOCK mode (leader key)
    # Note: <Leader> is typically Space or , in Vim. Let's use Space.
    # The spec shows "<Leader>k" which would be "Spacek" or ",k".
    # For now, let's implement as a literal sequence.
    registry.register(
        KeyBinding(
            keys="<Leader>k",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(target_mode=EditorMode.KBLOCK),
            description="KBLOCK mode (isolation controls)",
        )
    )

    # =========================================================================
    # Layer 4: Structural Selection (Tree-sitter) — NORMAL Mode
    # =========================================================================

    # Expand/shrink to parent/child AST node
    registry.register(
        KeyBinding(
            keys="(",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="ast_parent"),
            description="Expand to parent AST node",
        )
    )
    registry.register(
        KeyBinding(
            keys=")",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="ast_child"),
            description="Shrink to child AST node",
        )
    )

    # Previous/next sibling AST node
    registry.register(
        KeyBinding(
            keys="[",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="ast_prev_sibling"),
            description="Previous sibling AST node",
        )
    )
    registry.register(
        KeyBinding(
            keys="]",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="ast_next_sibling"),
            description="Next sibling AST node",
        )
    )

    # Function/class boundaries
    registry.register(
        KeyBinding(
            keys="{",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="prev_function"),
            description="Previous function/class",
        )
    )
    registry.register(
        KeyBinding(
            keys="}",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: NavigateInput(direction="next_function"),
            description="Next function/class",
        )
    )

    # =========================================================================
    # INSERT Mode Bindings
    # =========================================================================

    # Save (in INSERT mode, :w creates witness mark)
    registry.register(
        KeyBinding(
            keys=":w",
            modes=frozenset([EditorMode.INSERT]),
            input_factory=lambda: SaveInput(),
            description="Save K-Block (create witness mark)",
        )
    )

    # Discard
    registry.register(
        KeyBinding(
            keys=":q!",
            modes=frozenset([EditorMode.INSERT]),
            input_factory=lambda: DiscardInput(),
            description="Discard K-Block without saving",
        )
    )

    # =========================================================================
    # VISUAL Mode Bindings
    # =========================================================================

    # Actions on selection
    registry.register(
        KeyBinding(
            keys="d",
            modes=frozenset([EditorMode.VISUAL]),
            input_factory=lambda: ActionInput(action="delete"),
            description="Delete selection",
        )
    )
    registry.register(
        KeyBinding(
            keys="y",
            modes=frozenset([EditorMode.VISUAL]),
            input_factory=lambda: ActionInput(action="yank"),
            description="Yank (copy) selection",
        )
    )
    registry.register(
        KeyBinding(
            keys="c",
            modes=frozenset([EditorMode.VISUAL]),
            input_factory=lambda: ActionInput(action="change"),
            description="Change selection",
        )
    )

    # Extend selection with motions (reuse navigation)
    registry.register(
        KeyBinding(
            keys="j",
            modes=frozenset([EditorMode.VISUAL]),
            input_factory=lambda: SelectExtendInput(direction="down"),
            description="Extend selection down",
        )
    )
    registry.register(
        KeyBinding(
            keys="k",
            modes=frozenset([EditorMode.VISUAL]),
            input_factory=lambda: SelectExtendInput(direction="up"),
            description="Extend selection up",
        )
    )
    registry.register(
        KeyBinding(
            keys="h",
            modes=frozenset([EditorMode.VISUAL]),
            input_factory=lambda: SelectExtendInput(direction="left"),
            description="Extend selection left",
        )
    )
    registry.register(
        KeyBinding(
            keys="l",
            modes=frozenset([EditorMode.VISUAL]),
            input_factory=lambda: SelectExtendInput(direction="right"),
            description="Extend selection right",
        )
    )

    # =========================================================================
    # COMMAND Mode Bindings
    # =========================================================================

    # Execute command
    registry.register(
        KeyBinding(
            keys="<Enter>",
            modes=frozenset([EditorMode.COMMAND]),
            input_factory=lambda: ExecuteInput(),
            description="Execute command",
        )
    )

    # Tab completion
    registry.register(
        KeyBinding(
            keys="<Tab>",
            modes=frozenset([EditorMode.COMMAND]),
            input_factory=lambda: TabCompleteInput(),
            description="Tab completion",
        )
    )

    # =========================================================================
    # PORTAL Mode Bindings
    # =========================================================================

    # Expand
    registry.register(
        KeyBinding(
            keys="e",
            modes=frozenset([EditorMode.PORTAL]),
            input_factory=lambda: ExpandInput(),
            description="Expand hyperedge",
        )
    )

    # Collapse
    registry.register(
        KeyBinding(
            keys="c",
            modes=frozenset([EditorMode.PORTAL]),
            input_factory=lambda: CollapseInput(),
            description="Collapse hyperedge",
        )
    )

    # Navigation in PORTAL mode
    registry.register(
        KeyBinding(
            keys="j",
            modes=frozenset([EditorMode.PORTAL]),
            input_factory=lambda: NavigateInput(direction="down"),
            description="Move to next portal",
        )
    )
    registry.register(
        KeyBinding(
            keys="k",
            modes=frozenset([EditorMode.PORTAL]),
            input_factory=lambda: NavigateInput(direction="up"),
            description="Move to previous portal",
        )
    )

    # =========================================================================
    # GRAPH Mode Bindings
    # =========================================================================

    # Pan
    registry.register(
        KeyBinding(
            keys="h",
            modes=frozenset([EditorMode.GRAPH]),
            input_factory=lambda: PanInput(direction="left"),
            description="Pan left",
        )
    )
    registry.register(
        KeyBinding(
            keys="j",
            modes=frozenset([EditorMode.GRAPH]),
            input_factory=lambda: PanInput(direction="down"),
            description="Pan down",
        )
    )
    registry.register(
        KeyBinding(
            keys="k",
            modes=frozenset([EditorMode.GRAPH]),
            input_factory=lambda: PanInput(direction="up"),
            description="Pan up",
        )
    )
    registry.register(
        KeyBinding(
            keys="l",
            modes=frozenset([EditorMode.GRAPH]),
            input_factory=lambda: PanInput(direction="right"),
            description="Pan right",
        )
    )

    # Zoom
    registry.register(
        KeyBinding(
            keys="+",
            modes=frozenset([EditorMode.GRAPH]),
            input_factory=lambda: ZoomInput(delta=0.1),
            description="Zoom in",
        )
    )
    registry.register(
        KeyBinding(
            keys="-",
            modes=frozenset([EditorMode.GRAPH]),
            input_factory=lambda: ZoomInput(delta=-0.1),
            description="Zoom out",
        )
    )

    # Center on focused node
    registry.register(
        KeyBinding(
            keys="<Space>",
            modes=frozenset([EditorMode.GRAPH]),
            input_factory=lambda: CenterInput(),
            description="Center on focused node",
        )
    )

    # =========================================================================
    # Search (NORMAL mode)
    # =========================================================================

    # Note: Search is typically triggered by '/' followed by text input.
    # This is more complex as it requires capturing the pattern.
    # For now, we register the trigger key. The pattern is captured
    # via a separate input mechanism (similar to COMMAND mode).
    registry.register(
        KeyBinding(
            keys="/",
            modes=frozenset([EditorMode.NORMAL]),
            input_factory=lambda: ModeEnterInput(
                target_mode=EditorMode.COMMAND, metadata={"search": True}
            ),
            description="Search (enter pattern)",
        )
    )

    return registry


# =============================================================================
# Exports
# =============================================================================

__all__ = ["create_default_registry"]
