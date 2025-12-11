"""
GardenCLI - CLI interface for I-gent (Interface/Garden).

Interface agents render the kgents ecosystem as a stigmergic field:
a shared environment where entities leave traces and coordinate
through environmental signals.

Commands:
- field: Launch interactive field view (default)
- forge: Launch forge (composition) view
- attach: Attach to running process
- export: Export current state to markdown
- demo: Run demo with simulated activity

See: spec/protocols/prism.md
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Any, Callable

from protocols.cli.prism import CLICapable, expose

if TYPE_CHECKING:
    pass


class GardenCLI(CLICapable):
    """
    CLI interface for I-gent (Interface/Garden).

    The Garden renders the ecosystem as a stigmergic field where
    entities leave traces and coordinate through environmental signals.
    """

    @property
    def genus_name(self) -> str:
        return "garden"

    @property
    def cli_description(self) -> str:
        return "I-gent Interface/Garden operations"

    def get_exposed_commands(self) -> dict[str, Callable[..., Any]]:
        return {
            "field": self.field,
            "forge": self.forge,
            "attach": self.attach,
            "export": self.export,
            "demo": self.demo,
        }

    @expose(
        help="Launch interactive field view",
        examples=[
            "kgents garden field",
            "kgents garden field --state=saved.json",
        ],
    )
    async def field(
        self,
        state: str | None = None,
        width: int = 60,
        height: int = 20,
        color: bool = True,
        compost: bool = True,
    ) -> dict[str, Any]:
        """
        Launch interactive field view.

        Three layers:
        1. Physical - Entity positions, phases, events
        2. Topological - Composition morphisms, gravity, tension
        3. Semantic - Intent, dialectic phase, value alignment
        """
        from agents.i.field import create_demo_field
        from agents.i.tui import RenderConfig, TUIApplication

        # Load or create state
        if state:
            field_state = self._load_state(state, width, height)
            if field_state is None:
                return {"error": f"Could not load state from {state}"}
        else:
            field_state = create_demo_field()
            field_state.width = width
            field_state.height = height

        config = RenderConfig(
            use_color=color,
            show_compost=compost,
        )

        print()
        print("  Starting I-gent Field View...")
        print("  Press 'q' to quit, '?' for help")
        print()

        try:
            app = TUIApplication(state=field_state, config=config)
            app.run_sync()
            return {"status": "exited", "ticks": field_state.tick}
        except KeyboardInterrupt:
            return {"status": "interrupted", "ticks": field_state.tick}

    @expose(
        help="Launch forge (composition) view",
        examples=[
            "kgents garden forge",
            "kgents garden forge --empty",
        ],
    )
    async def forge(
        self,
        empty: bool = False,
        color: bool = True,
    ) -> dict[str, Any]:
        """
        Launch forge (composition) view.

        The forge allows interactive pipeline composition:
        - j/k to navigate
        - Tab to switch panels
        - Enter to add, d to delete
        - x to execute pipeline
        """
        from agents.i.forge_view import (
            DEFAULT_ARCHETYPES,
            ForgeViewKeyHandler,
            ForgeViewRenderer,
            ForgeViewState,
            create_demo_forge_state,
        )

        # Create state
        if empty:
            forge_state = ForgeViewState(inventory=DEFAULT_ARCHETYPES.copy())
        else:
            forge_state = create_demo_forge_state()

        renderer = ForgeViewRenderer(forge_state, use_color=color)
        handler = ForgeViewKeyHandler(forge_state)

        # Set up handlers
        result: dict[str, Any] = {"status": "exited", "pipeline_executed": False}

        def on_exit() -> None:
            pass

        def on_execute(pipeline: Any) -> None:
            result["pipeline_executed"] = True
            result["pipeline"] = pipeline.composition_string
            result["token_budget"] = pipeline.total_token_cost
            result["type_errors"] = pipeline.type_check()

        handler.set_exit_handler(on_exit)
        handler.set_execute_handler(on_execute)

        print()
        print("  Starting Forge View...")
        print("  Use j/k to navigate, Tab to switch panels")
        print("  Enter to add, d to delete, x to execute, q to quit")
        print()

        # Non-interactive: just print current state
        print(renderer.render())

        return result

    @expose(
        help="Attach to running evolution process",
        examples=[
            "kgents garden attach evolve-123",
        ],
    )
    async def attach(
        self,
        process_id: str,
    ) -> dict[str, Any]:
        """
        Attach to running evolution process.

        Reads state from .wire/{process_id}/state.json
        """
        wire_dir = Path(f".wire/{process_id}")
        if not wire_dir.exists():
            return {
                "error": f"No wire directory found at {wire_dir}",
                "hint": "The process may not be running or not exposing wire protocol.",
            }

        state_file = wire_dir / "state.json"
        if not state_file.exists():
            return {"error": f"No state.json found at {state_file}"}

        try:
            state_data = json.loads(state_file.read_text())
            return {
                "process_id": process_id,
                "agent_id": state_data.get("agent_id", "unknown"),
                "phase": state_data.get("phase", "unknown"),
                "task": state_data.get("current_task", "none"),
                "progress": state_data.get("progress", 0),
            }
        except Exception as e:
            return {"error": f"Error reading state: {e}"}

    @expose(
        help="Export current state to markdown",
        examples=[
            "kgents garden export garden.md",
        ],
    )
    async def export(
        self,
        output: str,
    ) -> dict[str, Any]:
        """
        Export current garden state to markdown.

        Includes entities, metrics, and recent events.
        """
        from agents.i.field import create_demo_field

        # Create demo state for export
        state = create_demo_field()

        # Generate markdown
        lines = [
            f"# Garden Snapshot: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Entities",
        ]

        for entity in sorted(state.entities.values(), key=lambda e: e.id):
            phase_symbol = "●" if entity.phase.value == "active" else "○"
            lines.append(
                f"- {phase_symbol} {entity.entity_type.symbol} ({entity.id}) "
                f"at ({entity.x}, {entity.y}) - {entity.phase.value.capitalize()}"
            )

        lines.extend(
            [
                "",
                "## Metrics",
                f"- Entropy: {int(state.entropy)}%",
                f"- Heat: {int(state.heat)}%",
                f"- Phase: {state.dialectic_phase.value.upper()}",
                f"- Tick: {state.tick}",
                "",
                "## Recent Events",
            ]
        )

        for event in state.get_recent_events(10):
            time_str = event.get("time", "")[-8:]
            source = event.get("source", "")
            message = event.get("message", "")
            lines.append(f"- {time_str} — [{source}] {message}")

        lines.extend(
            [
                "",
                "---",
                "*Exported by I-gent*",
            ]
        )

        # Write file
        output_path = Path(output)
        output_path.write_text("\n".join(lines))

        return {
            "output": output,
            "entities": len(state.entities),
            "events": len(state.get_recent_events(10)),
        }

    @expose(
        help="Run demo with simulated activity",
        examples=[
            "kgents garden demo",
            "kgents garden demo --width=80 --height=30",
        ],
    )
    async def demo(
        self,
        width: int = 60,
        height: int = 20,
        color: bool = True,
        compost: bool = True,
    ) -> dict[str, Any]:
        """
        Run demo with simulated activity.

        Creates a demo field with sample entities and runs the TUI.
        """
        from agents.i.field import create_demo_field
        from agents.i.tui import RenderConfig, TUIApplication

        state = create_demo_field()
        state.width = width
        state.height = height

        config = RenderConfig(
            use_color=color,
            show_compost=compost,
        )

        print()
        print("  Starting I-gent Demo...")
        print("  Press 'q' to quit, '?' for help")
        print()

        try:
            app = TUIApplication(state=state, config=config)
            app.run_sync()
            return {"status": "exited", "ticks": state.tick}
        except KeyboardInterrupt:
            return {"status": "interrupted", "ticks": state.tick}

    def _load_state(self, path: str, width: int, height: int) -> Any:
        """Load state from file."""
        try:
            from agents.i.field import Entity, EntityType, FieldState
            from agents.i.types import Phase

            data = json.loads(Path(path).read_text())

            state = FieldState(
                width=data.get("width", width),
                height=data.get("height", height),
                entropy=data.get("entropy", 50),
                heat=data.get("heat", 0),
                tick=data.get("tick", 0),
            )

            # Load entities
            for entity_data in data.get("entities", []):
                entity = Entity(
                    id=entity_data["id"],
                    entity_type=EntityType(entity_data["type"]),
                    x=entity_data["x"],
                    y=entity_data["y"],
                    phase=Phase(entity_data.get("phase", "active")),
                )
                state.add_entity(entity)

            return state

        except FileNotFoundError:
            return None
        except Exception:
            return None
