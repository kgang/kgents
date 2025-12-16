"""
Query CLI Handler: Query the AGENTESE registry.

Usage:
    kg query ?world.*              # Query all world nodes
    kg query ?*.*.manifest         # Query all manifest aspects
    kg query ?self.memory.?        # Query memory affordances
    kg query ?world.* --limit 10   # With pagination
    kg query ?self.* --dry-run     # Show what would be queried

Per spec/protocols/agentese-v3.md §8 (Query Syntax).
"""

from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


def cmd_query(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Query the AGENTESE registry.

    Queries discover what paths exist without invoking them.
    Uses pattern matching with wildcards:
        *  - matches single segment
        ** - matches multiple segments
        ?  - matches any aspect

    Examples:
        kg query ?world.*           # All world nodes
        kg query ?*.*.manifest      # All manifest aspects
        kg query ?self.memory.?     # Memory affordances
    """
    if not args or args[0] in ("--help", "-h"):
        _print_help()
        return 0

    pattern = args[0]
    remaining = args[1:]

    # Parse options
    limit = 100
    offset = 0
    dry_run = False
    json_output = False

    i = 0
    while i < len(remaining):
        arg = remaining[i]
        if arg == "--limit" and i + 1 < len(remaining):
            limit = int(remaining[i + 1])
            i += 2
        elif arg.startswith("--limit="):
            limit = int(arg.split("=")[1])
            i += 1
        elif arg == "--offset" and i + 1 < len(remaining):
            offset = int(remaining[i + 1])
            i += 2
        elif arg.startswith("--offset="):
            offset = int(arg.split("=")[1])
            i += 1
        elif arg == "--dry-run":
            dry_run = True
            i += 1
        elif arg == "--json":
            json_output = True
            i += 1
        else:
            i += 1

    # Ensure pattern starts with ?
    if not pattern.startswith("?"):
        pattern = "?" + pattern

    try:
        from protocols.agentese import (
            Observer,
            create_wired_logos,
        )
        from protocols.agentese import (
            query as agentese_query,
        )

        logos = create_wired_logos()
        observer = Observer.from_archetype("cli")

        # Execute query using the query function
        result = agentese_query(
            logos,  # type: ignore[arg-type]
            pattern,  # Already has ? prefix
            limit=limit,
            offset=offset,
            observer=observer,
            dry_run=dry_run,
        )

        if json_output:
            import json

            print(
                json.dumps(
                    {
                        "pattern": pattern,
                        "matches": [
                            {"path": m.path, "affordances": list(m.affordances)}
                            for m in result.matches
                        ],
                        "total": result.total_count,
                        "truncated": result.has_more,
                    },
                    indent=2,
                )
            )
        else:
            print(f"Query: {pattern}")
            print(
                f"Found {result.total_count} matches"
                + (" (more available)" if result.has_more else "")
            )
            print()

            if result.matches:
                for match in result.matches:
                    print(f"  {match.path}")
                    if match.affordances:
                        aspects = ", ".join(sorted(match.affordances))
                        print(f"    Aspects: {aspects}")
            else:
                print("  No matches found.")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return 1


def _print_help() -> None:
    """Print help text."""
    print("""\
kg query - Query the AGENTESE registry

USAGE:
    kg query <pattern> [options]

PATTERNS:
    ?world.*           All world nodes
    ?*.*.manifest      All manifest aspects
    ?self.memory.?     Memory affordances
    ?world.town.*      Town-related paths

OPTIONS:
    --limit <n>        Max results (default: 100, max: 1000)
    --offset <n>       Skip first n results (default: 0)
    --dry-run          Show what would be queried
    --json             JSON output

EXAMPLES:
    kg query ?world.*
    kg query ?self.* --limit 10
    kg query ?*.*.manifest --json
""")
