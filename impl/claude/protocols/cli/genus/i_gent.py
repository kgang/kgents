"""
I-gent CLI Commands - Garden/Interface operations.

Interface agents render the kgents ecosystem as a stigmergic field:
a shared environment where entities leave traces and coordinate
through environmental signals.

Commands:
  kgents garden              Launch interactive field view
  kgents garden --mode forge Launch forge (composition) view
  kgents garden attach       Attach to running process
  kgents garden export       Export current state to markdown

Philosophy:
> "The field remembers; the garden grows."

Three Layers:
1. Physical - Entity positions, phases, events
2. Topological - Composition morphisms, gravity, tension
3. Semantic - Intent, dialectic phase, value alignment

See: spec/i-gents/README.md
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Optional

HELP_TEXT = """\
kgents garden - I-gent Interface operations

USAGE:
  kgents garden [subcommand] [options]

SUBCOMMANDS:
  (default)              Launch interactive field view
  forge                  Launch forge (composition) view
  attach <process-id>    Attach to running evolution process
  export <output.md>     Export current state to markdown
  demo                   Run demo with simulated activity

OPTIONS:
  --mode=<mode>          View mode: field, forge, timeline
  --state=<file>         Load state from file
  --no-color             Disable ANSI colors
  --no-compost           Hide compost heap (event log)
  --width=<n>            Field width (default: 60)
  --height=<n>           Field height (default: 20)
  --help, -h             Show this help

KEYBOARD SHORTCUTS (in TUI):
  Navigation:
    h/j/k/l              Vim movement (move focus)
    Tab                  Cycle through entities
    Enter                Focus/select entity

  Views:
    1                    Field view
    2                    Forge view
    3                    Timeline view

  Actions:
    o                    Observe (spawn W-gent)
    Space                Pause/resume simulation
    s                    Save state
    e                    Export to markdown
    q                    Quit
    ?                    Help

EXAMPLES:
  kgents garden                     # Launch field view
  kgents garden --mode forge        # Launch forge view
  kgents garden attach evolve-123   # Attach to process
  kgents garden export garden.md    # Export current state
  kgents garden demo                # Run demo simulation
"""


def cmd_garden(args: list[str]) -> int:
    """I-gent Garden CLI handler."""
    if args and args[0] in ("--help", "-h"):
        print(HELP_TEXT)
        return 0

    # Parse options
    mode = "field"
    state_file: Optional[str] = None
    use_color = True
    show_compost = True
    width = 60
    height = 20
    subcommand: Optional[str] = None
    sub_args: list[str] = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg.startswith("--mode="):
            mode = arg.split("=", 1)[1]
        elif arg.startswith("--state="):
            state_file = arg.split("=", 1)[1]
        elif arg == "--no-color":
            use_color = False
        elif arg == "--no-compost":
            show_compost = False
        elif arg.startswith("--width="):
            width = int(arg.split("=", 1)[1])
        elif arg.startswith("--height="):
            height = int(arg.split("=", 1)[1])
        elif not arg.startswith("-") and subcommand is None:
            subcommand = arg
        elif subcommand is not None:
            sub_args.append(arg)
        i += 1

    # Route to subcommand or default
    handlers = {
        "forge": lambda: _cmd_forge(sub_args, width, height, use_color),
        "attach": lambda: _cmd_attach(sub_args),
        "export": lambda: _cmd_export(sub_args, width, height),
        "demo": lambda: _cmd_demo(use_color, show_compost, width, height),
    }

    if subcommand is None or subcommand == "field":
        return _cmd_field(state_file, use_color, show_compost, width, height)

    if subcommand in handlers:
        return handlers[subcommand]()

    print(f"Unknown subcommand: {subcommand}")
    print("Run 'kgents garden --help' for available subcommands.")
    return 1


def _cmd_field(
    state_file: Optional[str],
    use_color: bool,
    show_compost: bool,
    width: int,
    height: int,
) -> int:
    """Launch interactive field view."""
    try:
        from agents.i.field import FieldState, create_demo_field
        from agents.i.tui import RenderConfig, TUIApplication
    except ImportError as e:
        print(f"Error: Could not import I-gent modules: {e}")
        print("Make sure you're in the kgents project directory.")
        return 1

    # Load or create state
    if state_file:
        state = _load_state(state_file, width, height)
        if state is None:
            return 1
    else:
        state = create_demo_field()
        state.width = width
        state.height = height

    config = RenderConfig(
        use_color=use_color,
        show_compost=show_compost,
    )

    print()
    print("  Starting I-gent Field View...")
    print("  Press 'q' to quit, '?' for help")
    print()

    try:
        app = TUIApplication(state=state, config=config)
        app.run_sync()
    except KeyboardInterrupt:
        print("\n  Field view ended.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


def _cmd_forge(args: list[str], width: int, height: int, use_color: bool) -> int:
    """Launch forge (composition) view."""
    try:
        from agents.i.forge_view import (
            ForgeViewState,
            ForgeViewRenderer,
            ForgeViewKeyHandler,
            create_demo_forge_state,
            DEFAULT_ARCHETYPES,
        )
    except ImportError as e:
        print(f"Error: Could not import Forge View modules: {e}")
        print("Make sure you're in the kgents project directory.")
        return 1

    # Check for --demo or --empty
    demo_mode = "--demo" in args or not any(a.startswith("-") for a in args)
    empty_mode = "--empty" in args

    # Create state
    if empty_mode:
        state = ForgeViewState(inventory=DEFAULT_ARCHETYPES.copy())
    else:
        state = create_demo_forge_state()

    renderer = ForgeViewRenderer(state, use_color=use_color)
    handler = ForgeViewKeyHandler(state)

    # Set up handlers
    running = True
    pipeline_executed = False

    def on_exit():
        nonlocal running
        running = False

    def on_execute(pipeline):
        nonlocal pipeline_executed
        pipeline_executed = True
        print(f"\n  Executing pipeline: {pipeline.composition_string}")
        print(f"  Token budget: {pipeline.total_token_cost:,} tokens")
        errors = pipeline.type_check()
        if errors:
            print("  ⚠ Type errors detected:")
            for err in errors:
                print(f"    ✗ {err}")
        else:
            print("  ✓ Pipeline type-checks successfully")
        print()

    handler.set_exit_handler(on_exit)
    handler.set_execute_handler(on_execute)

    print()
    print("  Starting Forge View...")
    print("  Use j/k to navigate, Tab to switch panels")
    print("  Enter to add, d to delete, x to execute, q to quit")
    print()

    # Simple render loop (non-interactive for now, shows one frame)
    # Full TUI would need terminal raw mode like field view
    import sys
    import select

    try:
        # Check if we can do interactive mode
        if sys.stdin.isatty():
            import termios
            import tty

            old_settings = termios.tcgetattr(sys.stdin)
            try:
                tty.setraw(sys.stdin.fileno())

                while running:
                    # Clear and render
                    print("\033[2J\033[H", end="")
                    print(renderer.render())

                    # Non-blocking input
                    if select.select([sys.stdin], [], [], 0.1)[0]:
                        key = sys.stdin.read(1)
                        handler.handle(key)

            finally:
                termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
                print("\033[2J\033[H", end="")

        else:
            # Non-interactive: just print once
            print(renderer.render())

    except KeyboardInterrupt:
        pass

    if pipeline_executed:
        print("  Pipeline executed.")
    else:
        print("  Forge view ended.")
    print()

    return 0


def _cmd_attach(args: list[str]) -> int:
    """Attach to running evolution process."""
    if not args:
        print("Error: Process ID required")
        print("Usage: kgents garden attach <process-id>")
        return 1

    process_id = args[0]

    print()
    print(f"  Attaching to process: {process_id}")
    print("  " + "-" * 40)
    print()

    # Look for .wire directory
    wire_dir = Path(f".wire/{process_id}")
    if not wire_dir.exists():
        print(f"  Error: No wire directory found at {wire_dir}")
        print("  The process may not be running or not exposing wire protocol.")
        return 1

    # Read state from wire
    state_file = wire_dir / "state.json"
    if not state_file.exists():
        print(f"  Error: No state.json found at {state_file}")
        return 1

    try:
        with open(state_file) as f:
            state_data = json.load(f)
        print(f"  Connected to: {state_data.get('agent_id', 'unknown')}")
        print(f"  Phase: {state_data.get('phase', 'unknown')}")
        print(f"  Task: {state_data.get('current_task', 'none')}")
        if "progress" in state_data:
            progress = state_data["progress"]
            bar_width = 20
            filled = int(progress * bar_width)
            bar = "█" * filled + "░" * (bar_width - filled)
            print(f"  Progress: [{bar}] {int(progress * 100)}%")
        print()
    except Exception as e:
        print(f"  Error reading state: {e}")
        return 1

    return 0


def _cmd_export(args: list[str], width: int, height: int) -> int:
    """Export current state to markdown."""
    if not args:
        print("Error: Output file required")
        print("Usage: kgents garden export <output.md>")
        return 1

    output_path = args[0]

    try:
        from agents.i.field import create_demo_field
        from datetime import datetime
    except ImportError as e:
        print(f"Error: Could not import I-gent modules: {e}")
        return 1

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
    try:
        with open(output_path, "w") as f:
            f.write("\n".join(lines))
        print(f"  Exported to: {output_path}")
        return 0
    except Exception as e:
        print(f"Error writing file: {e}")
        return 1


def _cmd_demo(use_color: bool, show_compost: bool, width: int, height: int) -> int:
    """Run demo with simulated activity."""
    try:
        from agents.i.field import create_demo_field, FieldSimulator
        from agents.i.tui import RenderConfig, TUIApplication
    except ImportError as e:
        print(f"Error: Could not import I-gent modules: {e}")
        return 1

    state = create_demo_field()
    state.width = width
    state.height = height

    config = RenderConfig(
        use_color=use_color,
        show_compost=show_compost,
    )

    print()
    print("  Starting I-gent Demo...")
    print("  Press 'q' to quit, '?' for help")
    print()

    try:
        app = TUIApplication(state=state, config=config)
        app.run_sync()
    except KeyboardInterrupt:
        print("\n  Demo ended.")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

    return 0


def _load_state(path: str, width: int, height: int) -> Optional[Any]:
    """Load state from file."""
    try:
        from agents.i.field import FieldState

        with open(path) as f:
            data = json.load(f)

        state = FieldState(
            width=data.get("width", width),
            height=data.get("height", height),
            entropy=data.get("entropy", 50),
            heat=data.get("heat", 0),
            tick=data.get("tick", 0),
        )

        # Load entities
        for entity_data in data.get("entities", []):
            from agents.i.field import Entity, EntityType
            from agents.i.types import Phase

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
        print(f"Error: State file not found: {path}")
        return None
    except Exception as e:
        print(f"Error loading state: {e}")
        return None
