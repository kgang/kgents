"""
Brain Handler: Holographic Brain CLI interface.

Crown Jewel Brain provides high-level memory operations:
- capture: Store content to holographic memory
- ghost: Surface forgotten memories based on context
- map: View memory topology (cartography)
- status: Check brain health and statistics
- import: Batch import from Obsidian/Notion vaults

Usage:
    kg brain                      # Show brain status
    kg brain capture "content"    # Capture content to memory
    kg brain ghost "context"      # Surface relevant memories
    kg brain map                  # View memory topology
    kg brain status               # Detailed brain statistics
    kg brain import --source obsidian --path /vault  # Import markdown

AGENTESE Paths:
    self.memory.manifest          # Brain status
    self.memory.capture           # Capture content
    self.memory.ghost.surface     # Surface memories
    self.memory.cartography.manifest  # View topology

Wave 0 Foundation 1: Path visibility integrated - each command shows its AGENTESE path.
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
from protocols.cli.path_display import (
    apply_path_flags,
    display_path_header,
    parse_path_flags,
)

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# Module-level brain instance with thread-safe initialization
_brain_logos: Any = None
_brain_logos_lock = threading.Lock()

# Test hook: override to inject a mock logos instance
_brain_logos_factory: Any = None


def _get_brain_logos() -> Any:
    """Get or create the brain logos instance (thread-safe).

    Uses double-checked locking pattern for efficient thread-safe
    lazy initialization.

    Tests can inject a factory via _set_brain_logos_factory() to avoid
    network calls and global state mutation.
    """
    global _brain_logos, _brain_logos_factory
    if _brain_logos is None:
        with _brain_logos_lock:
            # Double-check after acquiring lock
            if _brain_logos is None:
                if _brain_logos_factory is not None:
                    # Test injection: use factory
                    _brain_logos = _brain_logos_factory()
                else:
                    # Production: use auto embedder
                    from protocols.agentese import create_brain_logos

                    _brain_logos = create_brain_logos(embedder_type="auto")
    return _brain_logos


def _set_brain_logos_factory(factory: Any) -> None:
    """Set a factory function for brain logos (test hook).

    Call with None to reset to default behavior.

    Args:
        factory: Callable that returns a Logos instance, or None to reset.
    """
    global _brain_logos, _brain_logos_factory
    with _brain_logos_lock:
        _brain_logos_factory = factory
        _brain_logos = None  # Reset cached instance


def _reset_brain_logos() -> None:
    """Reset the brain logos instance (for testing)."""
    global _brain_logos
    with _brain_logos_lock:
        _brain_logos = None


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
  kg brain import               Import from markdown vault

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON
  --show-paths                  Show AGENTESE path headers (default)
  --no-paths                    Hide AGENTESE path headers
  --trace                       Show detailed path trace (verbose mode)
  --observer TYPE               Observer perspective (technical, casual, security, creative)

Import Options:
  --source TYPE                 Source type: obsidian, notion, markdown
  --path PATH                   Path to vault or folder
  --dry-run                     Preview import without storing

AGENTESE Paths:
  self.memory.manifest          Brain status
  self.memory.capture           Capture content
  self.memory.ghost.surface     Surface memories
  self.memory.cartography.manifest  View topology
  self.memory.import            Import vault

Observers (Wave 0 Foundation 2):
  technical                     Detailed technical summary with code references
  casual                        Plain language summary for quick understanding
  security                      Security-focused view highlighting risks
  creative                      Metaphorical and creative interpretation

Examples:
  kg brain capture "Python is great for data science"
  kg brain ghost "programming language"
  kg brain map
  kg brain status --trace
  kg brain status --observer=casual
  kg brain import --source obsidian --path ~/Documents/Obsidian/MyVault
  kg brain import --source markdown --path ~/notes --dry-run
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

    # Parse path visibility flags (--show-paths, --no-paths, --trace)
    args, show_paths, trace_mode = parse_path_flags(args)
    apply_path_flags(show_paths, trace_mode)

    json_output = "--json" in args
    dry_run = "--dry-run" in args

    # Extract --source, --path, and --observer options
    source_type = "obsidian"  # default
    vault_path = None
    observer_type = "default"  # default observer
    clean_args = []

    i = 0
    while i < len(args):
        arg = args[i]
        if arg == "--source" and i + 1 < len(args):
            source_type = args[i + 1]
            i += 2
        elif arg == "--path" and i + 1 < len(args):
            vault_path = args[i + 1]
            i += 2
        elif arg == "--observer" and i + 1 < len(args):
            observer_type = args[i + 1]
            i += 2
        elif arg.startswith("--observer="):
            observer_type = arg.split("=", 1)[1]
            i += 1
        elif arg.startswith("-"):
            i += 1  # Skip other flags
        else:
            clean_args.append(arg)
            i += 1

    # Get subcommand
    subcommand = clean_args[0].lower() if clean_args else "status"

    # Run async handler
    return asyncio.run(
        _async_route(
            subcommand,
            clean_args[1:],
            json_output,
            source_type=source_type,
            vault_path=vault_path,
            dry_run=dry_run,
            observer_type=observer_type,
        )
    )


async def _async_route(
    subcommand: str,
    args: list[str],
    json_output: bool,
    source_type: str = "obsidian",
    vault_path: str | None = None,
    dry_run: bool = False,
    observer_type: str = "default",
) -> int:
    """Route to appropriate brain handler."""
    try:
        match subcommand:
            case "capture":
                return await _handle_capture(args, json_output, observer_type)
            case "ghost":
                return await _handle_ghost(args, json_output, observer_type)
            case "map":
                return await _handle_map(json_output, observer_type)
            case "status":
                return await _handle_status(json_output, observer_type)
            case "import":
                return _handle_import(source_type, vault_path, json_output, dry_run)
            case _:
                print(f"Unknown subcommand: {subcommand}")
                print("Use 'kg brain --help' for usage")
                return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def _handle_capture(
    args: list[str], json_output: bool, observer_type: str = "default"
) -> int:
    """Handle brain capture command."""
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.capture",
        aspect="define",
        observer=observer_type,
        effects=["CRYSTAL_FORMED", "LINKS_CREATED"],
    )

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


async def _handle_ghost(
    args: list[str], json_output: bool, observer_type: str = "default"
) -> int:
    """Handle brain ghost command (surface memories)."""
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.ghost.surface",
        aspect="witness",
        observer=observer_type,
        effects=["MEMORIES_SURFACED"],
    )

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


async def _handle_map(json_output: bool, observer_type: str = "default") -> int:
    """Handle brain map command (cartography)."""
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.cartography.manifest",
        aspect="manifest",
        observer=observer_type,
        effects=["TOPOLOGY_RENDERED"],
    )

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


async def _handle_status(json_output: bool, observer_type: str = "default") -> int:
    """Handle brain status command."""
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.manifest",
        aspect="manifest",
        observer=observer_type,
        effects=["STATUS_RETRIEVED"],
    )

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


def _handle_import(
    source_type: str,
    vault_path: str | None,
    json_output: bool,
    dry_run: bool,
) -> int:
    """Handle brain import command (batch import from markdown vault).

    Args:
        source_type: Source type (obsidian, notion, markdown)
        vault_path: Path to vault or folder
        json_output: Whether to output JSON
        dry_run: Preview without storing

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.import",
        aspect="define",
        effects=["CRYSTALS_FORMED", "VAULT_IMPORTED"],
    )

    import json as json_module
    from pathlib import Path

    from agents.m.importers.markdown import (
        ImportProgress,
        MarkdownImporter,
        ObsidianVaultParser,
    )

    # Validate path
    if not vault_path:
        print("Error: --path is required for import")
        print("Usage: kg brain import --source obsidian --path /path/to/vault")
        return 1

    path = Path(vault_path).expanduser().resolve()
    if not path.exists():
        print(f"Error: path does not exist: {vault_path}")
        return 1
    if not path.is_dir():
        print(f"Error: path is not a directory: {vault_path}")
        return 1

    # Validate source type
    valid_sources = {"obsidian", "notion", "markdown"}
    if source_type not in valid_sources:
        print(f"Error: unknown source type: {source_type}")
        print(f"Valid sources: {', '.join(sorted(valid_sources))}")
        return 1

    # Discover files
    print(f"🔍 Scanning {source_type} vault: {path}")
    try:
        parser = ObsidianVaultParser(path)
        files = parser.discover_files()
    except Exception as e:
        print(f"Error: failed to scan vault: {e}")
        return 1

    if not files:
        print("No markdown files found in vault")
        return 0

    print(f"   Found {len(files)} markdown files")

    if dry_run:
        # Preview mode: just show what would be imported
        print("\n📋 Dry run preview (no files imported):")
        print("━" * 50)
        for i, file_path in enumerate(files[:20], 1):
            rel_path = file_path.relative_to(path)
            print(f"  {i:3}. {rel_path}")
        if len(files) > 20:
            print(f"  ... and {len(files) - 20} more files")
        print("━" * 50)

        # Get vault stats
        stats = parser.stats()
        if json_output:
            print(
                json_module.dumps(
                    {"dry_run": True, "files": len(files), **stats}, indent=2
                )
            )
        else:
            print("\n📊 Vault Statistics:")
            print(f"   Total files: {stats['total_files']}")
            print(f"   Total words: {stats['total_words']:,}")
            print(f"   Unique tags: {stats['unique_tags']}")
            print(f"   Avg words/file: {stats['avg_words_per_file']}")
        return 0

    # Actually import
    print("\n📥 Importing to holographic brain...")

    # Get the brain's memory crystal for direct import
    from agents.m.crystal import create_crystal
    from agents.m.importers.markdown import create_lgent_embedder

    # Try to use L-gent semantic embeddings for better quality
    lgent_embedder = create_lgent_embedder()
    if lgent_embedder:
        print("   Using L-gent semantic embeddings (sentence-transformers)")
        # L-gent embeddings are typically 384-dimensional
        crystal = create_crystal(dimension=384, use_numpy=False)
    else:
        print(
            "   Using hash-based embeddings (install sentence-transformers for better quality)"
        )
        crystal = create_crystal(dimension=64, use_numpy=False)

    # Progress callback for nice output
    last_percent = -1

    def on_progress(progress: ImportProgress) -> None:
        nonlocal last_percent
        percent = int(progress.percent_complete)
        if percent != last_percent and percent % 10 == 0:
            last_percent = percent
            print(
                f"   Progress: {percent}% ({progress.processed_files}/{progress.total_files})"
            )

    importer = MarkdownImporter(
        crystal=crystal,
        embedder=lgent_embedder,  # None uses default hash embedder
        on_progress=on_progress,
    )

    try:
        progress = importer.import_vault(path)
    except Exception as e:
        print(f"Error during import: {e}")
        return 1

    # Report results
    print("\n✅ Import complete!")
    print("━" * 50)

    if json_output:
        result = {
            "status": "success",
            "total_files": progress.total_files,
            "successful": progress.successful,
            "failed": progress.failed,
            "skipped": progress.skipped,
            "errors": [{"file": f, "error": e} for f, e in progress.errors],
        }
        print(json_module.dumps(result, indent=2))
    else:
        print(f"   Imported: {progress.successful} files")
        if progress.failed > 0:
            print(f"   Failed: {progress.failed} files")
            for file_path, error in progress.errors[:5]:
                print(f"     • {file_path}: {error[:50]}")
            if len(progress.errors) > 5:
                print(f"     ... and {len(progress.errors) - 5} more errors")
        print("━" * 50)

        # Show crystal stats
        stats = crystal.stats()
        print(f"   Brain now contains {stats['concept_count']} memories")

    return 0 if progress.failed == 0 else 1


# Allow running directly: python -m protocols.cli.handlers.brain
if __name__ == "__main__":
    import sys

    sys.exit(cmd_brain(sys.argv[1:]))
