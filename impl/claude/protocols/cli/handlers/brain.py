"""
Brain Handler: Holographic Brain CLI interface.

Crown Jewel Brain provides high-level memory operations:
- capture: Store content to holographic memory
- ghost: Surface forgotten memories based on context
- map: View memory topology (cartography)
- status: Check brain health and statistics

Usage:
    kg brain                      # Show brain status
    kg brain capture "content"    # Capture content to memory
    kg brain ghost "context"      # Surface relevant memories
    kg brain map                  # View memory topology
    kg brain status               # Detailed brain statistics
"""

from __future__ import annotations

import asyncio
import threading
from typing import TYPE_CHECKING, Any

from agents.i.reactive.primitives.brain_cards import (
    BrainCartographyCard,
    GhostNotifierCard,
)
from agents.i.reactive.widget import RenderTarget

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# Module-level brain instance with thread-safe initialization
_brain_logos: Any = None
_brain_logos_lock = threading.Lock()


def _get_brain_logos() -> Any:
    """Get or create the brain logos instance (thread-safe).

    Uses double-checked locking pattern for efficient thread-safe
    lazy initialization.
    """
    global _brain_logos
    if _brain_logos is None:
        with _brain_logos_lock:
            # Double-check after acquiring lock
            if _brain_logos is None:
                from protocols.agentese import create_brain_logos

                _brain_logos = create_brain_logos(embedder_type="auto")
    return _brain_logos


def _get_observer() -> Any:
    """Get observer for CLI invocations.

    Uses a guest observer (lightweight, no permissions) for CLI context.
    This avoids test fixtures in production code.
    """
    from protocols.agentese.node import Observer

    return Observer.guest()


def print_help() -> None:
    """Print brain command help."""
    help_text = """
kg brain - Holographic Brain CLI

Commands:
  kg brain                      Show brain status
  kg brain capture "content"    Capture content to memory
  kg brain ghost "context"      Surface relevant memories
  kg brain map                  View memory topology
  kg brain status               Detailed brain statistics

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON

Examples:
  kg brain capture "Python is great for data science"
  kg brain ghost "programming language"
  kg brain map
"""
    print(help_text.strip())


def cmd_brain(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Holographic Brain: Crown Jewel memory operations.

    kg brain - High-level memory capture, surfacing, and visualization.
    """
    # Parse args
    if "--help" in args or "-h" in args:
        print_help()
        return 0

    json_output = "--json" in args
    args = [a for a in args if not a.startswith("-")]

    # Get subcommand
    subcommand = args[0].lower() if args else "status"

    # Run async handler
    return asyncio.run(_async_route(subcommand, args[1:], json_output))


async def _async_route(
    subcommand: str,
    args: list[str],
    json_output: bool,
) -> int:
    """Route to appropriate brain handler."""
    try:
        match subcommand:
            case "capture":
                return await _handle_capture(args, json_output)
            case "ghost":
                return await _handle_ghost(args, json_output)
            case "map":
                return await _handle_map(json_output)
            case "status":
                return await _handle_status(json_output)
            case _:
                print(f"Unknown subcommand: {subcommand}")
                print("Use 'kg brain --help' for usage")
                return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def _handle_capture(args: list[str], json_output: bool) -> int:
    """Handle brain capture command."""
    if not args:
        print("Error: content required for capture")
        print('Usage: kg brain capture "your content here"')
        return 1

    content = " ".join(args).strip()
    if not content:
        print("Error: content cannot be empty or whitespace only")
        print('Usage: kg brain capture "your content here"')
        return 1
    logos = _get_brain_logos()
    observer = _get_observer()

    result = await logos.invoke("self.memory.capture", observer, content=content)

    if json_output:
        import json

        print(json.dumps(result, indent=2))
    else:
        if result.get("status") == "captured":
            print(f"✓ Captured: {content[:50]}...")
            print(f"  ID: {result.get('concept_id')}")
        else:
            print(f"✗ Capture failed: {result.get('error', 'unknown error')}")

    return 0 if result.get("status") == "captured" else 1


async def _handle_ghost(args: list[str], json_output: bool) -> int:
    """Handle brain ghost command (surface memories)."""
    if not args:
        print("Error: context required for ghost surfacing")
        print('Usage: kg brain ghost "your context here"')
        return 1

    context = " ".join(args).strip()
    if not context:
        print("Error: context cannot be empty or whitespace only")
        print('Usage: kg brain ghost "your context here"')
        return 1
    logos = _get_brain_logos()
    observer = _get_observer()

    result = await logos.invoke(
        "self.memory.ghost.surface", observer, context=context, limit=5
    )

    if json_output:
        import json

        print(json.dumps(result, indent=2))
    else:
        card = GhostNotifierCard.from_surface_result(result)
        print(card.project(RenderTarget.CLI))

    return 0


async def _handle_map(json_output: bool) -> int:
    """Handle brain map command (cartography)."""
    logos = _get_brain_logos()
    observer = _get_observer()

    result = await logos.invoke("self.memory.cartography.manifest", observer)

    # result is BasicRendering
    metadata = getattr(result, "metadata", {}) if hasattr(result, "metadata") else {}

    if json_output:
        import json

        output = {
            "landmarks": metadata.get("landmarks", 0),
            "desire_lines": metadata.get("desire_lines", 0),
            "voids": metadata.get("voids", 1),
            "resolution": metadata.get("resolution", "adaptive"),
        }
        print(json.dumps(output, indent=2))
    else:
        card = BrainCartographyCard.from_manifest(metadata)
        print(card.project(RenderTarget.CLI))

    return 0


async def _handle_status(json_output: bool) -> int:
    """Handle brain status command."""
    logos = _get_brain_logos()
    observer = _get_observer()

    # Get memory manifest
    memory_result = await logos.invoke("self.memory.manifest", observer)
    # Get cartography
    carto_result = await logos.invoke("self.memory.cartography.manifest", observer)

    carto_metadata = (
        getattr(carto_result, "metadata", {})
        if hasattr(carto_result, "metadata")
        else {}
    )
    memory_metadata = (
        getattr(memory_result, "metadata", {})
        if hasattr(memory_result, "metadata")
        else {}
    )

    if json_output:
        import json

        output = {
            "memory": memory_metadata,
            "cartography": carto_metadata,
            "status": "healthy",
        }
        print(json.dumps(output, indent=2))
    else:
        print("🧠 Brain Status")
        print("━" * 30)
        print(f"  Memories: {memory_metadata.get('memory_count', 0)}")
        print(f"  Checkpoints: {memory_metadata.get('checkpoint_count', 0)}")
        print(f"  Landmarks: {carto_metadata.get('landmarks', 0)}")
        print(f"  Desire Lines: {carto_metadata.get('desire_lines', 0)}")
        print(f"  Resolution: {carto_metadata.get('resolution', 'adaptive')}")
        print("━" * 30)
        print("  Status: ✓ Healthy")

    return 0


# Allow running directly: python -m protocols.cli.handlers.brain
if __name__ == "__main__":
    import sys

    sys.exit(cmd_brain(sys.argv[1:]))
