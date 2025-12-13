"""
AgentPalette - Component selection widget.

Displays available agents, primitives, and functors that can
be added to a pipeline.
"""

from __future__ import annotations

from textual import on
from textual.app import ComposeResult
from textual.containers import VerticalScroll
from textual.message import Message
from textual.widget import Widget
from textual.widgets import ListItem, ListView, Static

from .types import ComponentSpec, ComponentType

# Catalog of available components
# This will be populated from actual agents in the system
AGENT_CATALOG: list[ComponentSpec] = [
    ComponentSpec(
        id="a-alethic",
        name="Alethic",
        component_type=ComponentType.AGENT,
        display_name="[A] Alethic",
        input_type="Claim",
        output_type="Verdict",
        description="Truth-seeking deliberation agent",
        stars=4,
    ),
    ComponentSpec(
        id="k-soul",
        name="Soul",
        component_type=ComponentType.AGENT,
        display_name="[K] Soul",
        input_type="Context",
        output_type="Response",
        description="Kent simulacra with personality navigation",
        stars=5,
    ),
    ComponentSpec(
        id="d-memory",
        name="Memory",
        component_type=ComponentType.AGENT,
        display_name="[D] Memory",
        input_type="Command",
        output_type="Response",
        description="Persistent state and memory",
        stars=2,
    ),
    ComponentSpec(
        id="e-evolution",
        name="Evolution",
        component_type=ComponentType.AGENT,
        display_name="[E] Evolution",
        input_type="Population",
        output_type="Evolved",
        description="Teleological thermodynamics",
        stars=3,
    ),
]

PRIMITIVE_CATALOG: list[ComponentSpec] = [
    ComponentSpec(
        id="ground",
        name="Ground",
        component_type=ComponentType.PRIMITIVE,
        display_name="[g] Ground",
        input_type="Any",
        output_type="Claim",
        description="Ground abstract to concrete claim",
        stars=4,
    ),
    ComponentSpec(
        id="judge",
        name="Judge",
        component_type=ComponentType.PRIMITIVE,
        display_name="[j] Judge",
        input_type="Claim",
        output_type="Verdict",
        description="Evaluate claim truth",
        stars=4,
    ),
    ComponentSpec(
        id="sublate",
        name="Sublate",
        component_type=ComponentType.PRIMITIVE,
        display_name="[s] Sublate",
        input_type="Contradiction",
        output_type="Synthesis",
        description="Dialectical synthesis",
        stars=4,
    ),
    ComponentSpec(
        id="contradict",
        name="Contradict",
        component_type=ComponentType.PRIMITIVE,
        display_name="[c] Contradict",
        input_type="Claim",
        output_type="Objection",
        description="Generate counterarguments",
        stars=3,
    ),
    ComponentSpec(
        id="fix",
        name="Fix",
        component_type=ComponentType.PRIMITIVE,
        display_name="[f] Fix",
        input_type="Error",
        output_type="Fixed",
        description="Retry with self-correction",
        stars=3,
    ),
]


class AgentPalette(Widget):
    """
    Palette of available components.

    Shows agents and primitives that can be added to the pipeline.
    User navigates with keys and selects with Enter.
    """

    DEFAULT_CSS = """
    AgentPalette {
        width: 30;
        height: 100%;
        border: solid #4a4a5c;
        padding: 0 1;
        background: #1a1a1a;
    }

    AgentPalette .palette-header {
        height: 1;
        color: #f5f0e6;
        text-style: bold;
        background: #252525;
        padding: 0 1;
        dock: top;
    }

    AgentPalette .section-header {
        height: 1;
        color: #b3a89a;
        text-style: bold;
        padding: 0 1;
        margin-top: 1;
    }

    AgentPalette ListView {
        height: auto;
        border: none;
        padding: 0;
    }

    AgentPalette ListItem {
        color: #f5f0e6;
        padding: 0 1;
    }

    AgentPalette ListItem:hover {
        background: #2a2a3a;
    }

    AgentPalette ListItem.--highlight {
        background: #e6a352;
        color: #1a1a1a;
        text-style: bold;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,  # noqa: A002
        classes: str | None = None,
    ) -> None:
        super().__init__(name=name, id=id, classes=classes)
        self._selected_spec: ComponentSpec | None = None

    def compose(self) -> ComposeResult:
        """Compose the palette."""
        yield Static("PALETTE", classes="palette-header")

        with VerticalScroll():
            # Agents section
            yield Static("AGENTS", classes="section-header")
            agent_list = ListView()
            for spec in AGENT_CATALOG:
                stars = "★" * spec.stars
                item = ListItem(Static(f"{spec.display_name}  {stars}"))
                item.spec = spec  # type: ignore
                agent_list.append(item)
            yield agent_list

            # Primitives section
            yield Static("PRIMITIVES", classes="section-header")
            prim_list = ListView()
            for spec in PRIMITIVE_CATALOG:
                stars = "○" * spec.stars
                item = ListItem(Static(f"{spec.display_name}  {stars}"))
                item.spec = spec  # type: ignore
                prim_list.append(item)
            yield prim_list

    @on(ListView.Selected)
    def on_list_selected(self, event: ListView.Selected) -> None:
        """Handle component selection."""
        if hasattr(event.item, "spec"):
            self._selected_spec = event.item.spec  # pyright: ignore
            self.post_message(ComponentSelected(self._selected_spec))

    def get_selected(self) -> ComponentSpec | None:
        """Get the currently selected component spec."""
        return self._selected_spec


class ComponentSelected(Message):
    """Message posted when a component is selected."""

    def __init__(self, spec: ComponentSpec) -> None:
        super().__init__()
        self.spec = spec
