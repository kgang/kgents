"""
Query CLI Handler: Query the AGENTESE registry.

Usage:
    kg query world.*              # Query all world nodes (? prefix optional)
    kg query self.memory.*        # Query memory affordances
    kg q self.*                   # Short alias
    kg q                          # Show query help

This command exists as an alias for `kg ?pattern` to avoid shell glob issues
with the `?` character in zsh/bash.

Per spec/protocols/agentese-v3.md §8 (Query Syntax).
"""

from __future__ import annotations

import fnmatch
import logging
from typing import TYPE_CHECKING

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext

logger = logging.getLogger(__name__)


# === Dynamic Path Discovery ===

# Minimal fallback paths if discovery fails
_FALLBACK_PATHS = [
    "self.memory",
    "self.soul",
    "self.forest",
    "world.town",
    "world.park",
    "world.atelier",
    "concept.gardener",
    "void.joy",
    "time.trace",
]

# Cache for discovered paths (lazy load)
_CACHED_PATHS: list[str] | None = None


def _discover_paths() -> list[str]:
    """
    Dynamically discover all known AGENTESE paths from:

    1. Handler routing tables (*_thin.py handlers)
    2. Crown Jewels registry (ALL_CROWN_JEWEL_PATHS)
    3. Node registry (@node decorated classes)
    4. Help projector path mappings (PATH_TO_COMMAND)

    Returns:
        Sorted list of unique AGENTESE paths
    """
    paths: set[str] = set()

    # 1. From thin handler routing tables
    try:
        from protocols.cli.handlers.brain_thin import BRAIN_SUBCOMMAND_TO_PATH

        paths.update(BRAIN_SUBCOMMAND_TO_PATH.values())
    except ImportError:
        pass

    try:
        from protocols.cli.handlers.soul_thin import SOUL_SUBCOMMAND_TO_PATH

        paths.update(SOUL_SUBCOMMAND_TO_PATH.values())
    except ImportError:
        pass

    try:
        from protocols.cli.handlers.town_thin import TOWN_SUBCOMMAND_TO_PATH

        paths.update(TOWN_SUBCOMMAND_TO_PATH.values())
    except ImportError:
        pass

    # Note: Park removed 2025-12-21 (extinction)

    try:
        from protocols.cli.handlers.atelier_thin import (
            ATELIER_SUBCOMMAND_TO_PATH,
            ATELIER_TWO_WORD_TO_PATH,
        )

        paths.update(ATELIER_SUBCOMMAND_TO_PATH.values())
        paths.update(ATELIER_TWO_WORD_TO_PATH.values())
    except ImportError:
        pass

    # Joy handlers are discovered through handler registry, not AGENTESE paths
    # (oblique, surprise, yes-and, challenge, constrain are CLI-only commands)

    # 2. From Crown Jewels registry (comprehensive path collection)
    try:
        from protocols.agentese.contexts.crown_jewels import ALL_CROWN_JEWEL_PATHS

        paths.update(ALL_CROWN_JEWEL_PATHS.keys())
    except ImportError:
        pass

    # 3. From node registry (@node decorated classes)
    try:
        from protocols.agentese.registry import get_registry

        registry = get_registry()
        paths.update(registry.list_paths())
    except Exception:
        pass

    # 4. From help projector (path -> command mapping)
    try:
        from protocols.cli.help_projector import PATH_TO_COMMAND

        paths.update(PATH_TO_COMMAND.keys())
    except ImportError:
        pass

    # 5. Add base contexts (always valid)
    try:
        from protocols.agentese.contexts import VALID_CONTEXTS

        paths.update(VALID_CONTEXTS)
    except ImportError:
        paths.update({"world", "self", "concept", "void", "time"})

    # Use fallback if nothing discovered
    if not paths:
        logger.warning("No paths discovered, using fallback list")
        return sorted(_FALLBACK_PATHS)

    return sorted(paths)


def _get_known_paths() -> list[str]:
    """
    Get all known AGENTESE paths (cached).

    Lazily discovers paths on first call, then caches result.
    """
    global _CACHED_PATHS
    if _CACHED_PATHS is None:
        _CACHED_PATHS = _discover_paths()
        logger.debug(f"Discovered {len(_CACHED_PATHS)} AGENTESE paths")
    return _CACHED_PATHS


def clear_path_cache() -> None:
    """Clear the cached paths (useful for testing)."""
    global _CACHED_PATHS
    _CACHED_PATHS = None


def _query_known_paths(
    pattern: str,
    *,
    limit: int = 100,
    offset: int = 0,
) -> list[str]:
    """
    Query known paths using fnmatch patterns.

    Paths are discovered dynamically from:
    - Handler routing tables
    - Crown Jewels registry
    - @node decorator registry
    - Help projector mappings

    Args:
        pattern: Pattern to match (e.g., "self.*", "*memory*")
        limit: Maximum results
        offset: Skip first N results

    Returns:
        List of matching paths
    """
    known_paths = _get_known_paths()

    # Handle special patterns
    if pattern == "*":
        # Return all paths
        matches = known_paths[:]
    elif "*" in pattern:
        # Use fnmatch for wildcard patterns
        matches = [p for p in known_paths if fnmatch.fnmatch(p, pattern)]
    else:
        # Exact match or prefix match
        matches = [p for p in known_paths if p == pattern or p.startswith(pattern + ".")]

    # Apply pagination
    len(matches)
    matches = matches[offset : offset + limit]

    return matches


@handler("query", is_async=False, tier=1, description="Query AGENTESE registry")
def cmd_query(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Query the AGENTESE registry.

    Queries discover what paths exist without invoking them.
    Uses pattern matching with wildcards:
        *  - matches single segment
        ** - matches multiple segments

    Examples:
        kg query world.*           # All world nodes
        kg query self.memory.*     # Memory affordances
        kg q self.*                # Short form
    """
    # Show help if no args
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

    # Strip leading ? if present (user can use either form)
    if pattern.startswith("?"):
        pattern = pattern[1:]

    try:
        # Use simple pattern matching against known paths
        # (The AGENTESE registry is dynamically populated, so we use a static list)
        matches = _query_known_paths(pattern, limit=limit, offset=offset)

        if not matches and not dry_run:
            # Provide helpful message
            print(f"Query: {pattern}")
            print("No matches found.")
            print()
            print("Known path prefixes: self.*, world.*, void.*, concept.*, time.*")
            print("Try: kg q 'self.*' or kg q 'world.*'")
            return 0

        # Build a simple result
        from dataclasses import dataclass

        @dataclass
        class SimpleResult:
            matches: list["SimpleMatch"]
            total_count: int
            has_more: bool

        @dataclass
        class SimpleMatch:
            path: str
            affordances: tuple[str, ...] = ()

        result = SimpleResult(
            matches=[SimpleMatch(path=p) for p in matches],
            total_count=len(matches),
            has_more=False,
        )

        # JSON output
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
            return 0

        # Use the formatted output from query_help
        try:
            from protocols.cli.query_help import format_query_result

            formatted = format_query_result(result)
            print(formatted)
        except ImportError:
            # Fallback to simple output
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
kg query (kg q) - Query the AGENTESE registry

USAGE:
    kg query <pattern> [options]
    kg q <pattern>                  # Short alias

PATTERNS (no ? prefix needed):
    self.*             All self.* paths
    world.*            All world nodes
    self.memory.*      Memory affordances
    *brain*            Paths containing 'brain'

OPTIONS:
    --limit <n>        Max results (default: 100)
    --offset <n>       Skip first n results
    --dry-run          Show what would be queried
    --json             JSON output

EXAMPLES:
    kg query self.*
    kg q world.town.*
    kg query self.memory.* --limit 5
    kg q *brain* --json

NOTE: This command avoids the shell glob issue with `kg ?pattern`.
      Both `kg query self.*` and `kg '?self.*'` work the same.
""")


__all__ = [
    "cmd_query",
    "clear_path_cache",
]
