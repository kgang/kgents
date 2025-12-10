"""
Forge View: Pipeline composition mode for the I-gent TUI.

The Forge View provides a visual interface for composing agent pipelines
before execution. It integrates with:
- L-gent: Catalog of available archetypes
- F-gent: Contract types and composition rules
- B-gent: Token budget estimation

Core concepts:
- Archetype: A reusable agent template from the catalog
- Pipeline: A chain of agents composed with >>
- Slot: An empty position in the pipeline
- Budget: Estimated token cost for execution

See: spec/i-gents/README.md (The Forge View section)
"""

from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from enum import Enum
from typing import Callable, Optional


class ArchetypeLevel(Enum):
    """Experience level of an archetype."""

    NOVICE = 1
    APPRENTICE = 2
    JOURNEYMAN = 3
    EXPERT = 4
    MASTER = 5


@dataclass
class Archetype:
    """
    An agent archetype from the L-gent catalog.

    Archetypes are reusable templates that can be instantiated
    and composed into pipelines.
    """

    id: str
    name: str
    symbol: str  # Single char for TUI display
    level: ArchetypeLevel = ArchetypeLevel.JOURNEYMAN
    input_type: str = "Any"
    output_type: str = "Any"
    description: str = ""
    tags: list[str] = dataclass_field(default_factory=list)
    token_cost: int = 100  # Base token cost per invocation
    entropy_cost: float = 0.1  # Entropy consumed per tick

    @property
    def level_display(self) -> str:
        """Human-readable level."""
        return f"lvl.{self.level.value}"


@dataclass
class PipelineSlot:
    """A slot in the pipeline (filled or empty)."""

    archetype: Optional[Archetype] = None
    is_rune: bool = False  # True if this is a "slot rune" (placeholder)

    @property
    def is_empty(self) -> bool:
        return self.archetype is None and not self.is_rune

    @property
    def symbol(self) -> str:
        if self.is_rune:
            return "+"
        if self.archetype:
            return self.archetype.symbol
        return "·"

    @property
    def name(self) -> str:
        if self.is_rune:
            return "+ Slot Rune"
        if self.archetype:
            return self.archetype.name
        return "(empty)"


@dataclass
class Pipeline:
    """
    A composition pipeline of archetypes.

    Pipelines are built by adding archetypes and compose with >>
    """

    slots: list[PipelineSlot] = dataclass_field(default_factory=list)
    name: str = "Untitled Pipeline"

    def add(self, archetype: Archetype) -> None:
        """Add an archetype to the pipeline."""
        self.slots.append(PipelineSlot(archetype=archetype))

    def add_rune(self) -> None:
        """Add a slot rune (placeholder)."""
        self.slots.append(PipelineSlot(is_rune=True))

    def remove(self, index: int) -> Optional[PipelineSlot]:
        """Remove a slot by index."""
        if 0 <= index < len(self.slots):
            return self.slots.pop(index)
        return None

    def clear(self) -> None:
        """Clear the pipeline."""
        self.slots.clear()

    @property
    def total_token_cost(self) -> int:
        """Estimate total token cost."""
        return sum(
            s.archetype.token_cost for s in self.slots if s.archetype is not None
        )

    @property
    def total_entropy_cost(self) -> float:
        """Estimate total entropy cost per tick."""
        return sum(
            s.archetype.entropy_cost for s in self.slots if s.archetype is not None
        )

    @property
    def composition_string(self) -> str:
        """Return the composition as A >> B >> C format."""
        names = []
        for slot in self.slots:
            if slot.archetype:
                names.append(slot.archetype.name)
            elif slot.is_rune:
                names.append("?")
        return " >> ".join(names) if names else "(empty)"

    def type_check(self) -> list[str]:
        """
        Check type compatibility between slots.

        Returns list of error messages (empty if valid).
        """
        errors = []
        for i in range(len(self.slots) - 1):
            current = self.slots[i]
            next_slot = self.slots[i + 1]

            if current.archetype and next_slot.archetype:
                out_type = current.archetype.output_type
                in_type = next_slot.archetype.input_type

                # "Any" is compatible with everything
                if out_type != "Any" and in_type != "Any" and out_type != in_type:
                    errors.append(
                        f"Type mismatch: {current.archetype.name} outputs {out_type}, "
                        f"but {next_slot.archetype.name} expects {in_type}"
                    )
        return errors


@dataclass
class ForgeViewState:
    """
    Complete state for the Forge View.

    Manages inventory, pipeline, and selection state.
    """

    # Inventory of available archetypes
    inventory: list[Archetype] = dataclass_field(default_factory=list)

    # Current pipeline being built
    pipeline: Pipeline = dataclass_field(default_factory=Pipeline)

    # Selection state
    inventory_cursor: int = 0
    pipeline_cursor: int = 0
    active_panel: str = "inventory"  # "inventory" or "pipeline"

    # Display dimensions
    inventory_width: int = 28
    pipeline_width: int = 35

    def move_cursor(self, direction: int) -> None:
        """Move cursor up/down in active panel."""
        if self.active_panel == "inventory":
            new_pos = self.inventory_cursor + direction
            if 0 <= new_pos < len(self.inventory):
                self.inventory_cursor = new_pos
        else:
            new_pos = self.pipeline_cursor + direction
            if 0 <= new_pos < len(self.pipeline.slots):
                self.pipeline_cursor = new_pos

    def switch_panel(self) -> None:
        """Switch between inventory and pipeline panels."""
        self.active_panel = (
            "pipeline" if self.active_panel == "inventory" else "inventory"
        )

    def add_selected_to_pipeline(self) -> bool:
        """Add selected archetype to pipeline."""
        if self.active_panel == "inventory" and self.inventory:
            archetype = self.inventory[self.inventory_cursor]
            self.pipeline.add(archetype)
            return True
        return False

    def remove_from_pipeline(self) -> bool:
        """Remove selected slot from pipeline."""
        if self.active_panel == "pipeline" and self.pipeline.slots:
            self.pipeline.remove(self.pipeline_cursor)
            if self.pipeline_cursor >= len(self.pipeline.slots):
                self.pipeline_cursor = max(0, len(self.pipeline.slots) - 1)
            return True
        return False


# Default archetypes for demo/testing
DEFAULT_ARCHETYPES = [
    Archetype(
        id="ground",
        name="Ground",
        symbol="G",
        level=ArchetypeLevel.MASTER,
        input_type="NaturalLanguage",
        output_type="GroundedConcept",
        description="Grounds natural language to formal concepts",
        tags=["bootstrap", "grounding"],
        token_cost=50,
        entropy_cost=0.05,
    ),
    Archetype(
        id="architect",
        name="Architect",
        symbol="A",
        level=ArchetypeLevel.EXPERT,
        input_type="Intent",
        output_type="Blueprint",
        description="Designs system architecture from intent",
        tags=["design", "planning"],
        token_cost=200,
        entropy_cost=0.2,
    ),
    Archetype(
        id="builder",
        name="Builder",
        symbol="B",
        level=ArchetypeLevel.APPRENTICE,
        input_type="Blueprint",
        output_type="Artifact",
        description="Implements blueprints into artifacts",
        tags=["implementation"],
        token_cost=150,
        entropy_cost=0.15,
    ),
    Archetype(
        id="validator",
        name="Validator",
        symbol="V",
        level=ArchetypeLevel.MASTER,
        input_type="Artifact",
        output_type="ValidationReport",
        description="Validates artifacts against contracts",
        tags=["testing", "validation"],
        token_cost=100,
        entropy_cost=0.1,
    ),
    Archetype(
        id="k-gent",
        name="K-Gent",
        symbol="K",
        level=ArchetypeLevel.EXPERT,
        input_type="Any",
        output_type="Any",
        description="Kent simulacra persona layer",
        tags=["persona", "interface"],
        token_cost=180,
        entropy_cost=0.25,
    ),
    Archetype(
        id="judge",
        name="Judge",
        symbol="J",
        level=ArchetypeLevel.MASTER,
        input_type="Any",
        output_type="Verdict",
        description="Evaluates against principles (taste)",
        tags=["bootstrap", "judgment"],
        token_cost=80,
        entropy_cost=0.1,
    ),
]


class ForgeViewRenderer:
    """Renders the Forge View to terminal."""

    # ANSI colors
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    GREEN = "\033[32m"
    RED = "\033[31m"
    MAGENTA = "\033[35m"
    WHITE = "\033[37m"

    def __init__(self, state: ForgeViewState, use_color: bool = True):
        self.state = state
        self.use_color = use_color

    def _c(self, color: str, text: str) -> str:
        """Apply color if enabled."""
        if self.use_color:
            return f"{color}{text}{self.RESET}"
        return text

    def render(self) -> str:
        """Render the complete Forge View."""
        lines = []

        # Header
        lines.append(self._render_header())
        lines.append("")

        # Two-panel layout
        inv_lines = self._render_inventory()
        pipe_lines = self._render_pipeline()

        # Combine panels side by side
        max_lines = max(len(inv_lines), len(pipe_lines))
        inv_lines.extend([""] * (max_lines - len(inv_lines)))
        pipe_lines.extend([""] * (max_lines - len(pipe_lines)))

        for inv, pipe in zip(inv_lines, pipe_lines):
            # Pad inventory to fixed width
            inv_padded = inv.ljust(self.state.inventory_width + 4)
            lines.append(f"{inv_padded}    {pipe}")

        lines.append("")

        # Budget footer
        lines.extend(self._render_budget())

        # Help bar
        lines.append("")
        lines.append(self._render_help())

        return "\n".join(lines)

    def _render_header(self) -> str:
        """Render the mode header."""
        mode = self._c(self.CYAN + self.BOLD, "MODE: COMPOSITION")
        return f"┌─ {mode} " + "─" * 40 + "┐"

    def _render_inventory(self) -> list[str]:
        """Render the inventory panel."""
        lines = []

        # Panel header
        active = self.state.active_panel == "inventory"
        header_color = self.CYAN if active else self.DIM
        header = self._c(header_color, "─ Inventory (Archetypes) ─")
        lines.append(f"┌{header}┐")

        # Archetype list
        for i, arch in enumerate(self.state.inventory):
            selected = i == self.state.inventory_cursor and active
            prefix = ">" if selected else " "

            symbol_color = self.YELLOW if selected else self.WHITE
            symbol = self._c(symbol_color, f"[{arch.symbol}]")
            name = arch.name.ljust(12)
            level = self._c(self.DIM, arch.level_display)

            line = f"│ {prefix} {symbol} {name} {level}"
            # Pad to width
            visible_len = len(
                f" {prefix} [{arch.symbol}] {arch.name.ljust(12)} {arch.level_display}"
            )
            padding = self.state.inventory_width - visible_len
            line += " " * max(0, padding) + " │"
            lines.append(line)

        # Empty slots message
        if not self.state.inventory:
            empty = self._c(self.DIM, "(no archetypes)")
            lines.append(f"│ {empty.ljust(self.state.inventory_width - 2)} │")

        # Instruction
        lines.append("│" + " " * self.state.inventory_width + " │")
        instr = self._c(self.DIM, "DRAG TO PIPELINE")
        instr_pad = (self.state.inventory_width - 16) // 2
        lines.append(
            f"│{' ' * instr_pad}{instr}{' ' * (self.state.inventory_width - instr_pad - 16)} │"
        )

        lines.append("└" + "─" * self.state.inventory_width + "─┘")

        return lines

    def _render_pipeline(self) -> list[str]:
        """Render the pipeline panel."""
        lines = []

        # Panel header
        active = self.state.active_panel == "pipeline"
        header_color = self.CYAN if active else self.DIM
        header = self._c(header_color, "─ Pipeline (Flux Chain) ──────")
        lines.append(f"┌{header}┐")

        # Pipeline slots
        for i, slot in enumerate(self.state.pipeline.slots):
            selected = i == self.state.pipeline_cursor and active
            prefix = ">" if selected else " "

            if slot.archetype:
                symbol_color = self.GREEN if selected else self.CYAN
                symbol = self._c(symbol_color, f"[ {slot.archetype.symbol} ]")
                name = slot.archetype.name
            elif slot.is_rune:
                symbol_color = self.MAGENTA if selected else self.DIM
                symbol = self._c(symbol_color, "[ + ]")
                name = "Slot Rune"
            else:
                symbol_color = self.DIM
                symbol = self._c(symbol_color, "[ · ]")
                name = "(empty)"

            line = f"│ {prefix} {symbol}"
            lines.append(line.ljust(self.state.pipeline_width) + " │")

            # Arrow to next (except last)
            if i < len(self.state.pipeline.slots) - 1:
                arrow = self._c(self.DIM, "     ↓")
                lines.append(f"│ {arrow}".ljust(self.state.pipeline_width) + " │")

            # Name
            name_line = f"│   {name}"
            lines.append(name_line.ljust(self.state.pipeline_width) + " │")

            if i < len(self.state.pipeline.slots) - 1:
                lines.append(
                    f"│     {self._c(self.DIM, '↓')}".ljust(self.state.pipeline_width)
                    + " │"
                )

        # Empty pipeline message
        if not self.state.pipeline.slots:
            empty = self._c(self.DIM, "(add archetypes)")
            lines.append(f"│ {empty}".ljust(self.state.pipeline_width) + " │")

        lines.append("│" + " " * (self.state.pipeline_width - 1) + " │")

        # Budget summary
        tokens = self.state.pipeline.total_token_cost
        entropy = self.state.pipeline.total_entropy_cost

        token_str = f"Thinking Budget: {tokens:,} tokens"
        entropy_str = f"Est. Entropy Cost: {entropy:.1f}/tick"

        lines.append(f"│ {token_str}".ljust(self.state.pipeline_width) + " │")
        lines.append(f"│ {entropy_str}".ljust(self.state.pipeline_width) + " │")

        lines.append("└" + "─" * (self.state.pipeline_width - 1) + "─┘")

        return lines

    def _render_budget(self) -> list[str]:
        """Render the budget footer."""
        lines = []

        # Type check errors
        errors = self.state.pipeline.type_check()
        if errors:
            lines.append(self._c(self.RED, "Type Errors:"))
            for err in errors:
                lines.append(f"  {self._c(self.RED, '✗')} {err}")
        else:
            if self.state.pipeline.slots:
                lines.append(self._c(self.GREEN, "✓ Pipeline type-checks"))

        # Composition string
        comp = self.state.pipeline.composition_string
        lines.append(f"Composition: {self._c(self.CYAN, comp)}")

        return lines

    def _render_help(self) -> str:
        """Render the help bar."""
        keys = [
            "[↑/↓]Navigate",
            "[Tab]Switch",
            "[Enter]Add",
            "[d]Delete",
            "[x]Execute",
            "[q]Back",
        ]
        help_text = self._c(self.DIM, "  ".join(keys))
        return help_text


class ForgeViewKeyHandler:
    """Handles keyboard input for Forge View."""

    def __init__(self, state: ForgeViewState):
        self.state = state
        self._on_execute: Optional[Callable[[Pipeline], None]] = None
        self._on_exit: Optional[Callable[[], None]] = None

    def set_execute_handler(self, handler: Callable[[Pipeline], None]) -> None:
        """Set handler for pipeline execution."""
        self._on_execute = handler

    def set_exit_handler(self, handler: Callable[[], None]) -> None:
        """Set handler for view exit."""
        self._on_exit = handler

    def handle(self, key: str) -> bool:
        """Handle a key press. Returns True if handled."""
        handlers = {
            "k": lambda: self.state.move_cursor(-1),  # Up
            "j": lambda: self.state.move_cursor(1),  # Down
            "\t": self.state.switch_panel,  # Tab
            "\r": self.state.add_selected_to_pipeline,  # Enter
            "\n": self.state.add_selected_to_pipeline,  # Enter (alt)
            "d": self.state.remove_from_pipeline,  # Delete
            "c": self.state.pipeline.clear,  # Clear
            "+": self.state.pipeline.add_rune,  # Add rune
            "x": self._execute,  # Execute
            "q": self._exit,  # Back/quit
        }

        # Arrow key handling (escape sequences)
        if key == "\x1b":  # ESC
            return True

        if key in handlers:
            handlers[key]()
            return True

        return False

    def _execute(self) -> None:
        """Execute the pipeline."""
        if self._on_execute and self.state.pipeline.slots:
            self._on_execute(self.state.pipeline)

    def _exit(self) -> None:
        """Exit the view."""
        if self._on_exit:
            self._on_exit()


def create_demo_forge_state() -> ForgeViewState:
    """Create a demo Forge View state for testing."""
    state = ForgeViewState(inventory=DEFAULT_ARCHETYPES.copy())

    # Pre-populate pipeline with a sample composition
    state.pipeline.add(DEFAULT_ARCHETYPES[0])  # Ground
    state.pipeline.add(DEFAULT_ARCHETYPES[4])  # K-Gent
    state.pipeline.add_rune()  # Slot rune
    state.pipeline.add(DEFAULT_ARCHETYPES[5])  # Judge

    return state


def render_forge_view_once(state: ForgeViewState, use_color: bool = True) -> str:
    """Render a Forge View state once (for export or testing)."""
    renderer = ForgeViewRenderer(state, use_color)
    return renderer.render()
