"""
L-gent CLI Commands - Library/Catalog operations.

The Synaptic Librarian for knowledge curation, semantic discovery,
and ecosystem connectivity.

Commands:
  kgents library catalog          List catalog entries
  kgents library discover <query> Search catalog semantically
  kgents library register <path>  Register new artifact
  kgents library show <id>        Show entry details
  kgents library lineage <id>     Show artifact lineage
  kgents library compose <ids>    Verify composition compatibility

Philosophy:
> "Knowledge is not stored—it is navigated. Discovery is not search—it is connection."

See: spec/l-gents/librarian.md
"""

from __future__ import annotations

import json
from typing import Any

HELP_TEXT = """\
kgents library - L-gent Library/Catalog operations

USAGE:
  kgents library <subcommand> [args...]

SUBCOMMANDS:
  catalog              List all catalog entries
  discover "<query>"   Search catalog (keyword + semantic)
  register <path>      Register new artifact
  show <id>            Show entry details
  lineage <id>         Show artifact lineage (ancestors/descendants)
  compose <ids>        Verify composition compatibility
  types                List registered types
  stats                Show catalog statistics

OPTIONS:
  --type=<type>        Filter by entity type (agent, tongue, tool, etc.)
  --semantic           Use semantic search (default: hybrid)
  --format=<fmt>       Output format: rich, json (default: rich)
  --help, -h           Show this help

ENTITY TYPES:
  agent, tongue, tool, hypothesis, artifact, script, document

EXAMPLES:
  kgents library catalog
  kgents library discover "calendar operations"
  kgents library register ./my_agent.py
  kgents library lineage agent-123
  kgents library compose agent-a agent-b agent-c
"""


def cmd_library(args: list[str]) -> int:
    """L-gent Library/Catalog CLI handler."""
    if not args or args[0] in ("--help", "-h"):
        print(HELP_TEXT)
        return 0

    subcommand = args[0]
    sub_args = args[1:]

    handlers = {
        "catalog": _cmd_catalog,
        "discover": _cmd_discover,
        "register": _cmd_register,
        "show": _cmd_show,
        "lineage": _cmd_lineage,
        "compose": _cmd_compose,
        "types": _cmd_types,
        "stats": _cmd_stats,
    }

    if subcommand not in handlers:
        print(f"Unknown subcommand: {subcommand}")
        print("Run 'kgents library --help' for available subcommands.")
        return 1

    return handlers[subcommand](sub_args)


# =============================================================================
# Subcommand Handlers
# =============================================================================


def _cmd_catalog(args: list[str]) -> int:
    """List catalog entries."""
    entity_type = None
    output_format = "rich"

    for arg in args:
        if arg.startswith("--type="):
            entity_type = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif arg in ("--help", "-h"):
            print("""\
kgents library catalog - List catalog entries

USAGE:
  kgents library catalog [options]

OPTIONS:
  --type=<type>        Filter by entity type
  --format=<fmt>       Output format: rich, json
""")
            return 0

    import asyncio

    try:
        entries = asyncio.run(_list_catalog(entity_type))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(entries, indent=2))
    else:
        if not entries:
            print()
            print("  No entries in catalog.")
            print("  Register artifacts with: kgents library register <path>")
            print()
        else:
            print()
            print("  CATALOG ENTRIES")
            print("  " + "-" * 60)
            print(f"  {'ID':<15} {'TYPE':<10} {'NAME':<20} {'STATUS':<10}")
            print("  " + "-" * 60)
            for e in entries:
                print(
                    f"  {e['id']:<15} {e['type']:<10} {e['name']:<20} {e['status']:<10}"
                )
            print()
            print(f"  Total: {len(entries)} entries")
            print()

    return 0


async def _list_catalog(entity_type: str | None) -> list[dict[str, Any]]:
    """List catalog entries."""
    from agents.l import Registry, EntityType

    registry = Registry()

    # Map string to EntityType
    type_filter = None
    if entity_type:
        type_map = {
            "agent": EntityType.AGENT,
            "tongue": EntityType.TONGUE,
            "tool": EntityType.TOOL,
            "hypothesis": EntityType.HYPOTHESIS,
            "artifact": EntityType.ARTIFACT,
            "script": EntityType.SCRIPT,
            "document": EntityType.DOCUMENT,
        }
        type_filter = type_map.get(entity_type.lower())

    entries = await registry.find(entity_type=type_filter)

    return [
        {
            "id": e.id,
            "name": e.name,
            "type": e.entity_type.value if e.entity_type else "unknown",
            "status": e.status.value if e.status else "unknown",
            "description": e.description,
        }
        for e in entries
    ]


def _cmd_discover(args: list[str]) -> int:
    """Search catalog semantically."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents library discover - Search catalog

USAGE:
  kgents library discover "<query>" [options]

OPTIONS:
  --semantic           Use semantic search only
  --keyword            Use keyword search only
  --limit=<n>          Maximum results (default: 10)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents library discover "calendar operations"
  kgents library discover "parse JSON" --semantic
""")
        return 0

    query = None
    semantic_only = False
    keyword_only = False
    limit = 10
    output_format = "rich"

    for arg in args:
        if arg == "--semantic":
            semantic_only = True
        elif arg == "--keyword":
            keyword_only = True
        elif arg.startswith("--limit="):
            limit = int(arg.split("=", 1)[1])
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            query = arg

    if not query:
        print("Error: Query required")
        return 1

    import asyncio

    try:
        results = asyncio.run(_discover(query, semantic_only, keyword_only, limit))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(results, indent=2))
    else:
        if not results:
            print()
            print(f'  No results for: "{query}"')
            print()
        else:
            print()
            print(f'  DISCOVERY RESULTS for "{query}"')
            print("  " + "-" * 50)
            for r in results:
                score_bar = (
                    "["
                    + "=" * int(r["score"] * 10)
                    + " " * (10 - int(r["score"] * 10))
                    + "]"
                )
                print(f"  {score_bar} {r['name']} ({r['type']})")
                if r.get("description"):
                    print(f"             {r['description'][:50]}...")
            print()

    return 0


async def _discover(
    query: str,
    semantic_only: bool,
    keyword_only: bool,
    limit: int,
) -> list[dict[str, Any]]:
    """Discover entries by query."""
    from agents.l import create_semantic_registry

    registry = await create_semantic_registry()

    if semantic_only:
        results = await registry.find_semantic(query, limit=limit)
    elif keyword_only:
        results = await registry.find(query=query, limit=limit)
    else:
        # Hybrid search
        results = await registry.find_hybrid(query, limit=limit)

    return [
        {
            "id": r.entry.id if hasattr(r, "entry") else r.id,
            "name": r.entry.name if hasattr(r, "entry") else r.name,
            "type": r.entry.entity_type.value
            if hasattr(r, "entry") and r.entry.entity_type
            else "unknown",
            "score": r.score if hasattr(r, "score") else 1.0,
            "description": r.entry.description
            if hasattr(r, "entry")
            else getattr(r, "description", None),
        }
        for r in results
    ]


def _cmd_register(args: list[str]) -> int:
    """Register new artifact."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents library register - Register new artifact

USAGE:
  kgents library register <path> [options]

OPTIONS:
  --type=<type>        Entity type (agent, tongue, tool, etc.)
  --name=<name>        Name (inferred from file if not provided)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents library register ./my_agent.py --type=agent
  kgents library register ./grammar.tongue --type=tongue
""")
        return 0

    path = None
    entity_type = "agent"
    name = None
    output_format = "rich"

    for arg in args:
        if arg.startswith("--type="):
            entity_type = arg.split("=", 1)[1]
        elif arg.startswith("--name="):
            name = arg.split("=", 1)[1]
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            path = arg

    if not path:
        print("Error: Path required")
        return 1

    import asyncio
    from pathlib import Path

    # Infer name from path
    if not name:
        name = Path(path).stem

    try:
        result = asyncio.run(_register_artifact(path, entity_type, name))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  REGISTERED")
        print("  " + "-" * 40)
        print(f"  ID:   {result['id']}")
        print(f"  Name: {result['name']}")
        print(f"  Type: {result['type']}")
        print(f"  Path: {result['path']}")
        print()

    return 0


async def _register_artifact(path: str, entity_type: str, name: str) -> dict[str, Any]:
    """Register artifact in catalog."""
    from agents.l import Registry, CatalogEntry, EntityType, Status
    import uuid

    type_map = {
        "agent": EntityType.AGENT,
        "tongue": EntityType.TONGUE,
        "tool": EntityType.TOOL,
        "hypothesis": EntityType.HYPOTHESIS,
        "artifact": EntityType.ARTIFACT,
        "script": EntityType.SCRIPT,
        "document": EntityType.DOCUMENT,
    }

    entry = CatalogEntry(
        id=str(uuid.uuid4())[:8],
        name=name,
        entity_type=type_map.get(entity_type.lower(), EntityType.ARTIFACT),
        status=Status.ACTIVE,
        description=f"Registered from {path}",
    )

    registry = Registry()
    await registry.register(entry)

    return {
        "id": entry.id,
        "name": entry.name,
        "type": entity_type,
        "path": path,
    }


def _cmd_show(args: list[str]) -> int:
    """Show entry details."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents library show - Show entry details

USAGE:
  kgents library show <id> [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json
""")
        return 0

    entry_id = args[0]
    output_format = "rich"

    for arg in args[1:]:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]

    import asyncio

    try:
        result = asyncio.run(_show_entry(entry_id))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if result is None:
        print(f"Entry not found: {entry_id}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print(f"  ENTRY: {result['name']}")
        print("  " + "-" * 40)
        for key, value in result.items():
            if value is not None:
                print(f"  {key:<15} {value}")
        print()

    return 0


async def _show_entry(entry_id: str) -> dict[str, Any] | None:
    """Show entry details."""
    from agents.l import Registry

    registry = Registry()
    entry = await registry.get(entry_id)

    if entry is None:
        return None

    return {
        "id": entry.id,
        "name": entry.name,
        "type": entry.entity_type.value if entry.entity_type else None,
        "status": entry.status.value if entry.status else None,
        "description": entry.description,
        "input_type": entry.input_type,
        "output_type": entry.output_type,
        "version": entry.version,
    }


def _cmd_lineage(args: list[str]) -> int:
    """Show artifact lineage."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents library lineage - Show artifact lineage

USAGE:
  kgents library lineage <id> [options]

OPTIONS:
  --ancestors          Show ancestors only
  --descendants        Show descendants only
  --depth=<n>          Maximum depth (default: 5)
  --format=<fmt>       Output format: rich, json

EXAMPLES:
  kgents library lineage agent-123
  kgents library lineage agent-123 --ancestors --depth=3
""")
        return 0

    entry_id = args[0]
    ancestors_only = False
    descendants_only = False
    depth = 5
    output_format = "rich"

    for arg in args[1:]:
        if arg == "--ancestors":
            ancestors_only = True
        elif arg == "--descendants":
            descendants_only = True
        elif arg.startswith("--depth="):
            depth = int(arg.split("=", 1)[1])
        elif arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]

    import asyncio

    try:
        result = asyncio.run(
            _get_lineage(entry_id, ancestors_only, descendants_only, depth)
        )
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print(f"  LINEAGE: {entry_id}")
        print("  " + "-" * 40)
        if result.get("ancestors"):
            print("  Ancestors:")
            for a in result["ancestors"]:
                print(f"    <- {a}")
        if result.get("descendants"):
            print("  Descendants:")
            for d in result["descendants"]:
                print(f"    -> {d}")
        if not result.get("ancestors") and not result.get("descendants"):
            print("  No lineage recorded for this artifact.")
        print()

    return 0


async def _get_lineage(
    entry_id: str,
    ancestors_only: bool,
    descendants_only: bool,
    depth: int,
) -> dict[str, Any]:
    """Get lineage for entry."""
    from agents.l import LineageGraph

    graph = LineageGraph()

    result = {}

    if not descendants_only:
        ancestors = graph.get_ancestors(entry_id, max_depth=depth)
        result["ancestors"] = list(ancestors)

    if not ancestors_only:
        descendants = graph.get_descendants(entry_id, max_depth=depth)
        result["descendants"] = list(descendants)

    return result


def _cmd_compose(args: list[str]) -> int:
    """Verify composition compatibility."""
    if not args or args[0] in ("--help", "-h"):
        print("""\
kgents library compose - Verify composition compatibility

USAGE:
  kgents library compose <id1> <id2> [<id3>...] [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json

Verifies that agents can be composed in the given order
based on their type signatures.

EXAMPLES:
  kgents library compose parser validator analyzer
  kgents library compose agent-a agent-b
""")
        return 0

    ids = []
    output_format = "rich"

    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif not arg.startswith("-"):
            ids.append(arg)

    if len(ids) < 2:
        print("Error: At least 2 IDs required for composition check")
        return 1

    import asyncio

    try:
        result = asyncio.run(_verify_composition(ids))
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(result, indent=2))
    else:
        print()
        print("  COMPOSITION CHECK")
        print("  " + "-" * 40)
        print(f"  Pipeline: {' >> '.join(ids)}")
        print(f"  Valid:    {result['valid']}")
        if result.get("stages"):
            print("  Stages:")
            for s in result["stages"]:
                status = "ok" if s["compatible"] else "FAIL"
                print(f"    [{status}] {s['from']} -> {s['to']}")
        if result.get("error"):
            print(f"  Error: {result['error']}")
        print()

    return 0 if result["valid"] else 1


async def _verify_composition(ids: list[str]) -> dict[str, Any]:
    """Verify composition compatibility."""
    from agents.l import Registry, create_lattice

    registry = Registry()
    lattice = create_lattice(registry)

    verification = await lattice.verify_pipeline(ids)

    return {
        "valid": verification.valid,
        "stages": [
            {
                "from": s.from_agent,
                "to": s.to_agent,
                "compatible": s.compatible,
            }
            for s in verification.stages
        ]
        if verification.stages
        else [],
        "error": verification.error if hasattr(verification, "error") else None,
    }


def _cmd_types(args: list[str]) -> int:
    """List registered types."""
    output_format = "rich"

    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif arg in ("--help", "-h"):
            print("""\
kgents library types - List registered types

USAGE:
  kgents library types [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json
""")
            return 0

    import asyncio

    try:
        types = asyncio.run(_list_types())
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(types, indent=2))
    else:
        print()
        print("  REGISTERED TYPES")
        print("  " + "-" * 40)
        for t in types:
            print(f"  {t['id']:<20} {t['kind']}")
        print()

    return 0


async def _list_types() -> list[dict[str, Any]]:
    """List registered types."""
    from agents.l import Registry, create_lattice

    registry = Registry()
    lattice = create_lattice(registry)

    types = list(lattice.types.values())

    return [{"id": t.id, "name": t.name, "kind": t.kind.value} for t in types]


def _cmd_stats(args: list[str]) -> int:
    """Show catalog statistics."""
    output_format = "rich"

    for arg in args:
        if arg.startswith("--format="):
            output_format = arg.split("=", 1)[1]
        elif arg in ("--help", "-h"):
            print("""\
kgents library stats - Show catalog statistics

USAGE:
  kgents library stats [options]

OPTIONS:
  --format=<fmt>       Output format: rich, json
""")
            return 0

    import asyncio

    try:
        stats = asyncio.run(_get_stats())
    except Exception as e:
        print(f"Error: {e}")
        return 1

    if output_format == "json":
        print(json.dumps(stats, indent=2))
    else:
        print()
        print("  CATALOG STATISTICS")
        print("  " + "-" * 40)
        print(f"  Total entries:  {stats['total']}")
        print("  By type:")
        for t, c in stats["by_type"].items():
            print(f"    {t:<15} {c}")
        print(f"  Active:         {stats['active']}")
        print(f"  Deprecated:     {stats['deprecated']}")
        print()

    return 0


async def _get_stats() -> dict[str, Any]:
    """Get catalog statistics."""
    from agents.l import Registry, Status

    registry = Registry()

    all_entries = await registry.find()

    by_type: dict[str, int] = {}
    active = 0
    deprecated = 0

    for e in all_entries:
        t = e.entity_type.value if e.entity_type else "unknown"
        by_type[t] = by_type.get(t, 0) + 1

        if e.status == Status.ACTIVE:
            active += 1
        elif e.status == Status.DEPRECATED:
            deprecated += 1

    return {
        "total": len(all_entries),
        "by_type": by_type,
        "active": active,
        "deprecated": deprecated,
    }
