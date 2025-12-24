"""
Context Handler: Typed-Hypergraph Navigation

A thin routing shim to self.context.* AGENTESE paths.
All business logic lives in protocols/agentese/contexts/self_context.py.

AGENTESE Path Mapping:
    kg context               -> self.context.manifest  (show current position)
    kg context focus <path>  -> self.context.focus     (jump to node)
    kg context navigate <e>  -> self.context.navigate  (follow hyperedge)
    kg context backtrack     -> self.context.backtrack (go back)
    kg context trail         -> self.context.trail     (show trail)
    kg context subgraph      -> self.context.subgraph  (extract subgraph)

Phase 2 (Context Perception integration):
    kg context outline       -> self.context.outline   (render as editable outline)
    kg context lens <f> <s>  -> self.context.lens      (semantic lens into file)
    kg context copy <path>   -> self.context.copy      (copy with provenance)
    kg context paste <path>  -> self.context.paste     (paste with link creation)

Usage:
    kg context                           # Where am I?
    kg context focus world.brain.core    # Jump to a node
    kg context navigate tests            # Follow [tests] hyperedge
    kg context backtrack                 # Go back one step
    kg context trail                     # Show navigation history
    kg context subgraph --depth 3        # Extract reachable subgraph
    kg context outline                   # Render as editable outline
    kg context lens <file> <function>    # Create semantic lens

The Typed-Hypergraph Model:
    - AGENTESE aspects ARE hyperedge types
    - Different observers see different edges (Umwelt principle)
    - Trails are replayable, shareable evidence

See: spec/protocols/typed-hypergraph.md, spec/protocols/context-perception.md
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


HELP_TEXT = """\
\033[1mkg context\033[0m - Navigate the typed-hypergraph

\033[1mUSAGE:\033[0m
  kg context                          Show current position and affordances
  kg context focus <path>             Jump to a specific node
  kg context navigate <edge>          Follow a hyperedge from current focus
  kg context backtrack                Go back one step in the trail
  kg context trail                    Show navigation history
  kg context subgraph [--depth N]     Extract reachable subgraph

  \033[1mPhase 2 - Context Perception:\033[0m
  kg context outline                  Render as editable outline
  kg context lens <file> <focus>      Create semantic lens into file
  kg context copy <path> [line:col]   Copy with provenance (Law 11.3)
  kg context paste <path> [line:col]  Paste with link creation (Law 11.4)

  \033[1mPhase 3 - Trail Artifacts:\033[0m
  kg context trail save <name>        Save current trail to file
  kg context trail load <name>        Load and resume a saved trail
  kg context trail share              Export trail as shareable JSON
  kg context trail witness            Convert trail to witness mark (Phase 5B)

\033[1mHYPEREDGE TYPES:\033[0m
  tests         Test files for this module
  imports       Dependencies (what this imports)
  contains      Children/submodules
  parent        Parent module
  implements    Specifications implemented
  related       Semantically related modules

\033[1mLENS FOCUS SPECIFIERS:\033[0m
  function_name           Focus on a function
  class:ClassName         Focus on a class
  lines:start-end         Focus on line range

\033[1mEXAMPLES:\033[0m
  $ kg context focus world.brain.core         # Start at brain.core
  $ kg context navigate tests                 # Find test files
  $ kg context backtrack                      # Go back to brain.core
  $ kg context trail                          # See where you've been
  $ kg context outline                        # See editable outline
  $ kg context lens src/auth.py validate      # Lens on validate function
  $ kg context lens src/auth.py class:User    # Lens on User class

\033[1mPRINCIPLE:\033[0m
  "The lens was a lie. There is only the link."
  Navigation is lazy. Edges are observer-dependent.
  Trails are replayable evidence.
"""


@handler("context", is_async=False, tier=1, description="Typed-hypergraph navigation")
def cmd_context(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Navigate context as a typed-hypergraph.

    All business logic is in protocols/agentese/contexts/self_context.py.
    """
    # Parse help flag
    if "--help" in args or "-h" in args:
        print(HELP_TEXT)
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(args)

    # Route to appropriate handler
    if subcommand == "focus":
        return _handle_focus(args)
    elif subcommand == "navigate":
        return _handle_navigate(args)
    elif subcommand == "backtrack":
        return _handle_backtrack(args)
    elif subcommand == "trail":
        return _handle_trail(args)
    elif subcommand == "subgraph":
        return _handle_subgraph(args)
    # Phase 2: Context Perception commands
    elif subcommand == "outline":
        return _handle_outline(args)
    elif subcommand == "lens":
        return _handle_lens(args)
    elif subcommand == "copy":
        return _handle_copy(args)
    elif subcommand == "paste":
        return _handle_paste(args)
    else:
        return _handle_manifest(args)


def _parse_subcommand(args: list[str]) -> str:
    """Extract subcommand from args, skipping flags."""
    for arg in args:
        if not arg.startswith("-"):
            return arg.lower()
    return "manifest"


def _get_node() -> Any:
    """Get the ContextNavNode singleton."""
    from protocols.agentese.contexts.self_context import get_context_nav_node

    return get_context_nav_node()


def _get_observer() -> Any:
    """Get default observer for CLI."""
    from protocols.agentese.node import Observer

    return Observer(archetype="developer", capabilities=frozenset({"debug", "test"}))


def _run_async(coro: Any) -> Any:
    """Run async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    return loop.run_until_complete(coro)


def _handle_manifest(args: list[str]) -> int:
    """Show current position in the hypergraph."""
    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.manifest(observer))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_focus(args: list[str]) -> int:
    """Jump to a specific node."""
    # Extract path from args (skip 'focus' subcommand)
    path = None
    for arg in args:
        if not arg.startswith("-") and arg != "focus":
            path = arg
            break

    if not path:
        print("Usage: kg context focus <path>")
        print("Example: kg context focus world.brain.core")
        return 1

    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.focus(observer, path))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_navigate(args: list[str]) -> int:
    """Follow a hyperedge from current focus."""
    # Extract edge type from args
    edge_type = None
    for arg in args:
        if not arg.startswith("-") and arg != "navigate":
            edge_type = arg
            break

    if not edge_type:
        print("Usage: kg context navigate <edge_type>")
        print("Edge types: tests, imports, contains, parent, implements, related")
        return 1

    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.navigate(observer, edge_type))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_backtrack(args: list[str]) -> int:
    """Go back one step in the trail."""
    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.backtrack(observer))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_trail(args: list[str]) -> int:
    """
    Show or manage navigation history.

    Phase 3: Trail artifact commands:
        kg context trail              - Show current trail
        kg context trail save <name>  - Save trail to file
        kg context trail load <name>  - Load trail from file
        kg context trail share        - Export as shareable JSON
    """
    # Extract subcommand (save, load, share) if present
    positional_args = [a for a in args if not a.startswith("-") and a != "trail"]

    if len(positional_args) >= 1:
        trail_subcommand = positional_args[0].lower()

        if trail_subcommand == "save":
            return _handle_trail_save(positional_args[1:])
        elif trail_subcommand == "load":
            return _handle_trail_load(positional_args[1:])
        elif trail_subcommand == "share":
            return _handle_trail_share(positional_args[1:])
        elif trail_subcommand == "witness":
            return _handle_trail_witness(positional_args[1:])

    # Default: show trail
    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.trail(observer))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_subgraph(args: list[str]) -> int:
    """Extract reachable subgraph from current focus."""
    # Parse --depth flag
    max_depth = 3
    for i, arg in enumerate(args):
        if arg == "--depth" and i + 1 < len(args):
            try:
                max_depth = int(args[i + 1])
            except ValueError:
                pass
        elif arg.startswith("--depth="):
            try:
                max_depth = int(arg.split("=", 1)[1])
            except ValueError:
                pass

    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.subgraph(observer, max_depth))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


# === Phase 2: Context Perception Handlers ===


def _handle_outline(args: list[str]) -> int:
    """Render current context as editable outline."""
    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.outline(observer))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_lens(args: list[str]) -> int:
    """Create semantic lens into a file."""
    # Extract file_path and focus from args
    file_path = None
    focus = ""
    positional_args = [a for a in args if not a.startswith("-") and a != "lens"]

    if len(positional_args) >= 1:
        file_path = positional_args[0]
    if len(positional_args) >= 2:
        focus = positional_args[1]

    if not file_path:
        print("Usage: kg context lens <file> [focus]")
        print("Focus specifiers:")
        print("  function_name      - Lens on a function")
        print("  class:ClassName    - Lens on a class")
        print("  lines:start-end    - Lens on line range")
        print("\nExamples:")
        print("  kg context lens src/auth.py validate")
        print("  kg context lens src/auth.py class:User")
        print("  kg context lens src/auth.py lines:10-50")
        return 1

    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.lens(observer, file_path, focus))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_copy(args: list[str]) -> int:
    """Copy with provenance metadata."""
    # Extract path and optional line:col from args
    node_path = None
    start_line = 0
    start_col = 0
    end_line = 0
    end_col = 0

    positional_args = [a for a in args if not a.startswith("-") and a != "copy"]

    if len(positional_args) >= 1:
        node_path = positional_args[0]
    if len(positional_args) >= 2:
        # Parse line:col format (e.g., "10:5-20:10")
        selection = positional_args[1]
        if "-" in selection:
            start, end = selection.split("-", 1)
            if ":" in start:
                parts = start.split(":")
                start_line = int(parts[0])
                start_col = int(parts[1]) if len(parts) > 1 else 0
            else:
                start_line = int(start)
            if ":" in end:
                parts = end.split(":")
                end_line = int(parts[0])
                end_col = int(parts[1]) if len(parts) > 1 else 0
            else:
                end_line = int(end)
        elif ":" in selection:
            parts = selection.split(":")
            start_line = int(parts[0])
            start_col = int(parts[1]) if len(parts) > 1 else 0

    if not node_path:
        print("Usage: kg context copy <path> [selection]")
        print("Selection formats:")
        print("  10:5-20:10  - From line 10, col 5 to line 20, col 10")
        print("  10-20       - From line 10 to line 20")
        print("  10:5        - Starting at line 10, col 5")
        return 1

    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(
            node.copy(observer, node_path, start_line, start_col, end_line, end_col)
        )

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _handle_paste(args: list[str]) -> int:
    """Paste with link creation."""
    # Extract path and optional line:col from args
    target_path = None
    line = 0
    col = 0

    positional_args = [a for a in args if not a.startswith("-") and a != "paste"]

    if len(positional_args) >= 1:
        target_path = positional_args[0]
    if len(positional_args) >= 2:
        position = positional_args[1]
        if ":" in position:
            parts = position.split(":")
            line = int(parts[0])
            col = int(parts[1]) if len(parts) > 1 else 0
        else:
            line = int(position)

    if not target_path:
        print("Usage: kg context paste <path> [line:col]")
        print("\nNote: Copy first with 'kg context copy <path>'")
        return 1

    try:
        node = _get_node()
        observer = _get_observer()
        result = _run_async(node.paste(observer, target_path, line, col))

        print(result.content)
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1


# === Phase 3: Trail Artifact Handlers ===


def _handle_trail_save(args: list[str]) -> int:
    """
    Save current trail to a file.

    Usage: kg context trail save <name>

    Saves the current trail to ~/.kgents/trails/<name>.trail.json
    """
    import json
    from pathlib import Path

    # Extract name
    if not args:
        print("Usage: kg context trail save <name>")
        print("Example: kg context trail save auth-investigation")
        return 1

    name = args[0]

    try:
        # Get current trail from context node
        node = _get_node()

        # Get the trail data
        trail = node._current_trail
        if trail is None or len(trail.steps) == 0:
            print("No trail to save. Navigate first to build a trail.")
            return 1

        # Create trails directory
        trails_dir = Path.home() / ".kgents" / "trails"
        trails_dir.mkdir(parents=True, exist_ok=True)

        # Save trail
        trail_file = trails_dir / f"{name}.trail.json"
        trail_data = trail.share()  # Use the share() method with metadata

        with open(trail_file, "w") as f:
            json.dump(trail_data, f, indent=2)

        print(f"Trail saved: {trail_file}")
        print(f"  Steps: {len(trail.steps)}")
        print(f"  Evidence strength: {trail_data['evidence']['strength']}")
        return 0

    except Exception as e:
        print(f"Error saving trail: {e}")
        return 1


def _handle_trail_load(args: list[str]) -> int:
    """
    Load a saved trail.

    Usage: kg context trail load <name>

    Loads trail from ~/.kgents/trails/<name>.trail.json
    """
    import json
    from pathlib import Path

    # Extract name
    if not args:
        # List available trails
        trails_dir = Path.home() / ".kgents" / "trails"
        if trails_dir.exists():
            trails = list(trails_dir.glob("*.trail.json"))
            if trails:
                print("Available trails:")
                for t in sorted(trails):
                    print(f"  - {t.stem.replace('.trail', '')}")
                print("\nUsage: kg context trail load <name>")
            else:
                print("No saved trails found.")
                print("Save a trail first: kg context trail save <name>")
        else:
            print("No saved trails found.")
            print("Save a trail first: kg context trail save <name>")
        return 1

    name = args[0]

    try:
        from protocols.agentese.contexts.self_context import Trail

        # Find trail file
        trails_dir = Path.home() / ".kgents" / "trails"
        trail_file = trails_dir / f"{name}.trail.json"

        if not trail_file.exists():
            print(f"Trail not found: {name}")
            print(f"Expected path: {trail_file}")
            return 1

        # Load trail
        with open(trail_file) as f:
            trail_data = json.load(f)

        observer = _get_observer()
        trail = Trail.from_dict(trail_data, observer)

        # Set as current trail
        node = _get_node()
        node._current_trail = trail

        print(f"Trail loaded: {name}")
        print(trail.as_outline())
        return 0

    except Exception as e:
        print(f"Error loading trail: {e}")
        return 1


def _handle_trail_share(args: list[str]) -> int:
    """
    Export current trail as shareable JSON.

    Usage: kg context trail share [--file <path>]

    Outputs shareable JSON to stdout, or to file if --file specified.
    """
    import json

    # Parse --file flag
    output_file = None
    for i, arg in enumerate(args):
        if arg == "--file" and i + 1 < len(args):
            output_file = args[i + 1]
        elif arg.startswith("--file="):
            output_file = arg.split("=", 1)[1]

    try:
        node = _get_node()

        # Get current trail
        trail = node._current_trail
        if trail is None or len(trail.steps) == 0:
            print("No trail to share. Navigate first to build a trail.")
            return 1

        # Get shareable data
        shared = trail.share()
        json_output = json.dumps(shared, indent=2)

        if output_file:
            from pathlib import Path

            Path(output_file).write_text(json_output)
            print(f"Trail exported to: {output_file}")
            print(f"  Content hash: {shared['content_hash']}")
            print(f"  Evidence strength: {shared['evidence']['strength']}")
        else:
            print(json_output)

        return 0

    except Exception as e:
        print(f"Error sharing trail: {e}")
        return 1


def _handle_trail_witness(args: list[str]) -> int:
    """
    Convert current trail to a witness mark.

    Usage: kg context trail witness [--claim "..."]

    Emits the trail to the Witness ledger as evidence.
    The trail becomes a Mark that can be queried with `kg witness show`.

    Phase 5B: Trail → Witness integration.
    """
    # Parse --claim flag
    claim = None
    for i, arg in enumerate(args):
        if arg == "--claim" and i + 1 < len(args):
            claim = args[i + 1]
        elif arg.startswith("--claim="):
            claim = arg.split("=", 1)[1]

    try:
        node = _get_node()

        # Get current trail
        trail = node._current_trail
        if trail is None or len(trail.steps) == 0:
            print("No trail to witness. Navigate first to build a trail.")
            print("\nHint: Use 'kg context focus <path>' to start navigating.")
            return 1

        # Convert trail to witness mark
        from services.witness.trail_bridge import convert_trail_to_mark, emit_trail_as_mark

        # First, analyze and show what we're witnessing
        mark = convert_trail_to_mark(trail, claim=claim)

        print(f"\033[1mWitnessing Trail\033[0m: {trail.name}")
        print(f"  Steps: {mark.evidence.step_count}")
        print(f"  Unique paths: {mark.evidence.unique_paths}")
        print(f"  Annotations: {mark.evidence.annotation_count}")
        print(f"  Evidence strength: \033[32m{mark.evidence.evidence_strength}\033[0m")
        print(f"  Commitment level: {mark.evidence.commitment_level}")

        if mark.evidence.principles_signaled:
            print("  Principles signaled:")
            for principle, strength in mark.evidence.principles_signaled:
                print(f"    - {principle}: {strength:.0%}")

        # Emit to witness bus
        emitted_mark = _run_async(emit_trail_as_mark(trail, claim=claim))

        print(f"\n\033[32m✓\033[0m Mark created: {emitted_mark.id}")
        print(f"  Origin: {emitted_mark.origin}")
        print(f"  Phase: {emitted_mark.phase.value}")

        if claim:
            print(f"  Claim: {claim}")

        print("\nView with: kg witness show --today")
        return 0

    except Exception as e:
        print(f"Error witnessing trail: {e}")
        return 1
