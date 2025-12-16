"""
Brain Handler: Holographic Brain CLI interface with D-gent Triad.

Crown Jewel Brain provides high-level memory operations:
- capture: Store content to holographic memory (SQLite + Vector)
- search/ghost: Semantic search for similar memories
- list: View recent captures
- status: Check brain health and statistics
- import: Batch import from Obsidian/Notion vaults

D-gent Triad Integration:
- Left Hemisphere: SQLite relational store (source of truth)
- Right Hemisphere: NumPy vector store (semantic index)
- Coherency Protocol: Auto-heals ghost memories

Storage:
- ~/.local/share/kgents/brain/brain.db (SQLite)
- Semantic embeddings via L-gent (sentence-transformers)

Usage:
    kg brain                      # Show brain status
    kg brain capture "content"    # Capture content to memory
    kg brain search "query"       # Semantic search
    kg brain ghost "context"      # Alias for search
    kg brain list                 # List recent captures
    kg brain status               # Detailed brain statistics
    kg brain import --source obsidian --path /vault  # Import markdown

AGENTESE Paths:
    self.memory.manifest          # Brain status
    self.memory.capture           # Capture content
    self.memory.ghost.surface     # Surface memories
    self.memory.cartography.manifest  # View topology
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

from protocols.cli.path_display import (
    apply_path_flags,
    display_path_header,
    parse_path_flags,
)

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# Module-level brain crystal (lazy initialized)
_brain_crystal: Any = None


async def _get_brain() -> Any:
    """Get or create the brain crystal instance."""
    global _brain_crystal
    if _brain_crystal is None:
        from agents.brain import get_brain_crystal
        _brain_crystal = await get_brain_crystal()
    return _brain_crystal


def _reset_brain() -> None:
    """Reset the brain crystal (for testing)."""
    global _brain_crystal
    _brain_crystal = None
    from agents.brain import reset_brain_crystal
    reset_brain_crystal()


def print_help() -> None:
    """Print brain command help."""
    help_text = """
kg brain - Holographic Brain CLI (D-gent Triad)

Commands:
  kg brain                      Show brain status
  kg brain capture "content"    Capture content to memory
  kg brain search "query"       Semantic search for similar memories
  kg brain ghost "context"      Alias for search (surface memories)
  kg brain list                 List recent captures
  kg brain status               Detailed brain statistics
  kg brain import               Import from markdown vault

Options:
  --help, -h                    Show this help message
  --json                        Output as JSON
  --show-paths                  Show AGENTESE path headers (default)
  --no-paths                    Hide AGENTESE path headers

Import Options:
  --source TYPE                 Source type: obsidian, notion, markdown
  --path PATH                   Path to vault or folder
  --dry-run                     Preview import without storing

Storage:
  SQLite:  ~/.local/share/kgents/brain/brain.db
  Vectors: In-memory NumPy with L-gent embeddings

AGENTESE Paths:
  self.memory.manifest          Brain status
  self.memory.capture           Capture content
  self.memory.ghost.surface     Surface memories

Examples:
  kg brain capture "Python is great for data science"
  kg brain search "programming language"
  kg brain ghost "category theory"
  kg brain list
  kg brain status
  kg brain import --source obsidian --path ~/Documents/Obsidian/MyVault
"""
    print(help_text.strip())


def cmd_brain(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Holographic Brain: Crown Jewel memory operations with D-gent Triad.

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

    # Extract --source, --path, and --limit options
    source_type = "obsidian"  # default
    vault_path = None
    limit = 10
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
        elif arg == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass
            i += 2
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
            limit=limit,
        )
    )


async def _async_route(
    subcommand: str,
    args: list[str],
    json_output: bool,
    source_type: str = "obsidian",
    vault_path: str | None = None,
    dry_run: bool = False,
    limit: int = 10,
) -> int:
    """Route to appropriate brain handler."""
    try:
        match subcommand:
            case "capture":
                return await _handle_capture(args, json_output)
            case "search" | "ghost":
                return await _handle_search(args, json_output, limit)
            case "list":
                return await _handle_list(json_output, limit)
            case "status":
                return await _handle_status(json_output)
            case "import":
                return _handle_import(source_type, vault_path, json_output, dry_run)
            case _:
                print(f"Unknown subcommand: {subcommand}")
                print("Use 'kg brain --help' for usage")
                return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


async def _handle_capture(args: list[str], json_output: bool) -> int:
    """Handle brain capture command."""
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.capture",
        aspect="define",
        effects=["CRYSTAL_FORMED", "EMBEDDING_STORED"],
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

    # Get brain crystal and capture
    brain = await _get_brain()
    result = await brain.capture(content)

    if json_output:
        import json
        print(json.dumps({
            "status": "captured",
            "concept_id": result.concept_id,
            "content": result.content[:100],
            "captured_at": result.captured_at,
            "has_embedding": result.has_embedding,
            "storage": result.storage,
        }, indent=2))
    else:
        print(f"✓ Captured: {content[:50]}...")
        print(f"  ID: {result.concept_id}")
        print(f"  Embedding: {'✓ semantic' if result.has_embedding else '○ hash-based'}")
        print(f"  Storage: SQLite + {'Vector' if result.has_embedding else 'relational only'}")

    return 0


async def _handle_search(args: list[str], json_output: bool, limit: int) -> int:
    """Handle brain search/ghost command (semantic search)."""
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.ghost.surface",
        aspect="witness",
        effects=["MEMORIES_SURFACED"],
    )

    if not args:
        print("Error: query required for search")
        print('Usage: kg brain search "your query here"')
        return 1

    query = " ".join(args).strip()
    if not query:
        print("Error: query cannot be empty or whitespace only")
        print('Usage: kg brain search "your query here"')
        return 1

    # Get brain crystal and search
    brain = await _get_brain()
    results = await brain.search(query, limit=limit)

    if json_output:
        import json
        print(json.dumps({
            "query": query,
            "count": len(results),
            "results": [
                {
                    "concept_id": r.concept_id,
                    "content": r.content[:200],
                    "similarity": round(r.similarity, 3),
                    "captured_at": r.captured_at,
                    "is_stale": r.is_stale,
                }
                for r in results
            ],
        }, indent=2))
    else:
        if not results:
            print("👻 No memories surfaced")
            print(f"  Query: {query}")
        else:
            print(f"🔮 Found {len(results)} memories:")
            print()
            for i, r in enumerate(results, 1):
                similarity_bar = "█" * int(r.similarity * 10) + "░" * (10 - int(r.similarity * 10))
                stale_marker = " ⚠️ stale" if r.is_stale else ""
                print(f"  {i}. [{similarity_bar}] {r.similarity:.1%}{stale_marker}")
                print(f"     {r.content[:80]}...")
                print(f"     ID: {r.concept_id}")
                print()

    return 0


async def _handle_list(json_output: bool, limit: int) -> int:
    """Handle brain list command."""
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.manifest",
        aspect="witness",
        effects=["CAPTURES_LISTED"],
    )

    brain = await _get_brain()
    captures = await brain.list_captures(limit=limit)

    if json_output:
        import json
        print(json.dumps({
            "count": len(captures),
            "captures": captures,
        }, indent=2))
    else:
        if not captures:
            print("📭 No captures yet")
            print("  Use: kg brain capture \"your content here\"")
        else:
            print(f"📚 Recent captures ({len(captures)}):")
            print()
            for c in captures:
                print(f"  • {c['content']}")
                print(f"    ID: {c['concept_id']} | {c['captured_at']}")
                print()

    return 0


async def _handle_status(json_output: bool) -> int:
    """Handle brain status command."""
    # Display AGENTESE path header
    display_path_header(
        path="self.memory.manifest",
        aspect="manifest",
        effects=["STATUS_RETRIEVED"],
    )

    brain = await _get_brain()
    status = await brain.status()

    if json_output:
        import json
        print(json.dumps({
            "total_captures": status.total_captures,
            "vector_count": status.vector_count,
            "has_semantic": status.has_semantic,
            "coherency_rate": round(status.coherency_rate, 3),
            "ghosts_healed": status.ghosts_healed,
            "storage_path": status.storage_path,
            "status": "healthy",
        }, indent=2))
    else:
        print("🧠 Brain Status (D-gent Triad)")
        print("━" * 40)
        print(f"  Captures:     {status.total_captures}")
        print(f"  Vectors:      {status.vector_count}")
        print(f"  Semantic:     {'✓ L-gent embeddings' if status.has_semantic else '○ hash-based'}")
        print(f"  Coherency:    {status.coherency_rate:.1%}")
        print(f"  Ghosts healed: {status.ghosts_healed}")
        print("━" * 40)
        print("  Status: ✓ Healthy")
        print(f"  Storage: {status.storage_path}/brain.db")

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

    if vault_path is None:
        print("Error: --path required for import")
        print("Usage: kg brain import --source obsidian --path /path/to/vault")
        return 1

    from pathlib import Path
    vault = Path(vault_path).expanduser()

    if not vault.exists():
        print(f"Error: Path does not exist: {vault}")
        return 1

    # Import the importer
    try:
        from agents.m.importers.markdown import MarkdownImporter

        importer = MarkdownImporter(source_type=source_type)
    except ImportError:
        print("Error: Importer not available")
        return 1

    # Scan files
    files = importer.scan(vault)
    print(f"Found {len(files)} markdown files in {vault}")

    if dry_run:
        print("\n[DRY RUN] Would import:")
        for f in files[:10]:
            print(f"  • {f.name}")
        if len(files) > 10:
            print(f"  ... and {len(files) - 10} more")
        return 0

    # Import to brain
    async def do_import() -> int:
        brain = await _get_brain()
        imported = 0
        errors = 0

        for md_file in files:
            try:
                content = md_file.read_text(encoding="utf-8")
                title = md_file.stem
                await brain.capture(
                    content=content,
                    metadata={"title": title, "source": source_type, "path": str(md_file)},
                )
                imported += 1
                if imported % 10 == 0:
                    print(f"  Imported {imported}/{len(files)}...")
            except Exception as e:
                errors += 1
                if errors <= 5:
                    print(f"  Error importing {md_file.name}: {e}")

        print(f"\n✓ Imported {imported} files ({errors} errors)")
        return 0 if errors == 0 else 1

    return asyncio.run(do_import())
