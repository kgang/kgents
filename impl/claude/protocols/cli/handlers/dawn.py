# mypy: ignore-errors
"""
Dawn Handler: CLI for the Dawn Cockpit daily operating surface.

Dawn Cockpit — Kent's quarter-screen TUI where copy-paste is the killer feature.

The handler provides three modes:
1. TUI Mode (default) — Launch the full Textual TUI
2. CLI Mode (--cli) — Quick commands without TUI
3. JSON Mode (--json) — For programmatic access

AGENTESE Path Mapping:
    kg dawn                 -> Launch TUI
    kg dawn --cli           -> time.dawn.manifest
    kg dawn focus           -> time.dawn.focus.list
    kg dawn focus add       -> time.dawn.focus.add
    kg dawn focus done      -> time.dawn.focus.remove
    kg dawn focus promote   -> time.dawn.focus.promote
    kg dawn focus demote    -> time.dawn.focus.demote
    kg dawn snippets        -> time.dawn.snippets.list
    kg dawn snippets copy   -> time.dawn.snippets.copy
    kg dawn hygiene         -> time.dawn.hygiene

"The cockpit doesn't fly the plane. The pilot flies the plane.
 The cockpit just makes it easy."

See: spec/protocols/dawn-cockpit.md, plans/dawn-cockpit.md
"""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


# =============================================================================
# Path Routing
# =============================================================================

DAWN_SUBCOMMAND_TO_PATH = {
    # Focus
    "focus": "time.dawn.focus.list",
    "focus-add": "time.dawn.focus.add",
    "focus-done": "time.dawn.focus.remove",
    "focus-promote": "time.dawn.focus.promote",
    "focus-demote": "time.dawn.focus.demote",
    # Snippets
    "snippets": "time.dawn.snippets.list",
    "snippets-copy": "time.dawn.snippets.copy",
    # Hygiene
    "hygiene": "time.dawn.hygiene",
    # Status
    "status": "time.dawn.manifest",
}

DEFAULT_PATH = "time.dawn.manifest"


# =============================================================================
# Lazy Service Access
# =============================================================================


def _get_managers() -> tuple[Any, Any]:
    """
    Get FocusManager and SnippetLibrary instances.

    Uses the singleton pattern from DawnNode to ensure consistency.
    Loads persisted data from disk.
    """
    from protocols.dawn import FocusManager, SnippetLibrary
    from protocols.dawn.node import get_dawn_node

    try:
        # Try to get from the registered node (shares state with AGENTESE)
        node = get_dawn_node()
        return node.focus_manager, node.snippet_library
    except Exception:
        # Fallback: create fresh instances and load persisted data
        fm = FocusManager()
        fm.load()  # Load persisted focus items
        sl = SnippetLibrary()
        sl.load_defaults()
        sl.load_custom()  # Load persisted custom snippets
        return fm, sl


# =============================================================================
# Main Entry Point
# =============================================================================


@handler("dawn", is_async=False, needs_pty=True, tier=3, description="Dawn Cockpit TUI")
def cmd_dawn(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Dawn Cockpit: Your daily operating surface.

    Default: Launch the TUI.
    Use --cli for command-line only operations.
    """
    # Parse flags
    json_output = "--json" in args
    cli_mode = "--cli" in args
    trace_mode = "--trace" in args

    # Clean args
    clean_args = [a for a in args if a not in ("--json", "--cli", "--trace")]

    # Parse help flag
    if "--help" in clean_args or "-h" in clean_args:
        _print_help()
        return 0

    # Parse subcommand
    subcommand = _parse_subcommand(clean_args)

    if trace_mode:
        path = DAWN_SUBCOMMAND_TO_PATH.get(subcommand, DEFAULT_PATH)
        print(f"[TRACE] Invoking: {path}")

    # Default behavior: launch TUI (unless --cli or subcommand given)
    if not cli_mode and subcommand == "status" and not json_output:
        return _run_tui()

    # Route to appropriate handler
    match subcommand:
        case "focus":
            return _run_focus_list(clean_args, json_output)
        case "focus-add":
            return _run_focus_add(clean_args, json_output)
        case "focus-done":
            return _run_focus_done(clean_args, json_output)
        case "focus-promote":
            return _run_focus_promote(clean_args, json_output)
        case "focus-demote":
            return _run_focus_demote(clean_args, json_output)
        case "snippets":
            return _run_snippets_list(json_output)
        case "snippets-copy":
            return _run_snippets_copy(clean_args, json_output)
        case "hygiene":
            return _run_hygiene(json_output)
        case _:
            return _run_manifest(json_output)


def _parse_subcommand(args: list[str]) -> str:
    """
    Extract subcommand from args.

    Handles compound commands like "focus add" -> "focus-add"
    """
    non_flag_args = [a for a in args if not a.startswith("-")]

    if not non_flag_args:
        return "status"

    first = non_flag_args[0].lower()

    # Check for compound commands
    if first == "focus" and len(non_flag_args) > 1:
        second = non_flag_args[1].lower()
        if second in ("add", "done", "remove", "promote", "demote"):
            if second == "remove":
                second = "done"  # Alias
            return f"focus-{second}"

    if first == "snippets" and len(non_flag_args) > 1:
        second = non_flag_args[1].lower()
        if second == "copy":
            return "snippets-copy"

    return first


# =============================================================================
# TUI Mode
# =============================================================================


def _run_tui() -> int:
    """Launch the Dawn Cockpit TUI."""
    from protocols.dawn.tui import run_dawn_tui

    fm, sl = _get_managers()
    return run_dawn_tui(fm, sl)


# =============================================================================
# Status/Manifest
# =============================================================================


def _run_manifest(json_output: bool) -> int:
    """Show dawn cockpit status."""
    fm, sl = _get_managers()

    from protocols.dawn import Bucket

    data = {
        "focus": {
            "today": len(fm.list(bucket=Bucket.TODAY)),
            "week": len(fm.list(bucket=Bucket.WEEK)),
            "someday": len(fm.list(bucket=Bucket.SOMEDAY)),
            "total": len(fm),
            "stale": len(fm.get_stale()),
        },
        "snippets": {
            "static": len(sl.list_static()),
            "query": len(sl.list_query()),
            "custom": len(sl.list_custom()),
            "total": len(sl),
        },
    }

    if json_output:
        print(json.dumps(data, indent=2))
    else:
        _print_manifest(data)

    return 0


def _print_manifest(data: dict[str, Any]) -> None:
    """Print formatted manifest."""
    focus = data["focus"]
    snippets = data["snippets"]

    stale_warning = f" ⚠️ {focus['stale']} stale" if focus["stale"] > 0 else ""

    print(
        """
┌─────────────────────────────────────────────────┐
│  🌅 DAWN COCKPIT                                │
│  "The cockpit just makes it easy."              │
├─────────────────────────────────────────────────┤
│  FOCUS                                          │
│    🔥 Today:   {today:<3}                               │
│    🎯 Week:    {week:<3}                               │
│    🧘 Someday: {someday:<3}{stale_warning:<27}│
├─────────────────────────────────────────────────┤
│  SNIPPETS                                       │
│    ▶ Static:  {static:<3}  ⟳ Query: {query:<3}  ★ Custom: {custom:<3}│
├─────────────────────────────────────────────────┤
│  COMMANDS                                       │
│    kg dawn              Launch TUI              │
│    kg dawn focus        List focus items        │
│    kg dawn snippets     List snippets           │
│    kg dawn hygiene      Check stale items       │
└─────────────────────────────────────────────────┘
""".format(
            today=focus["today"],
            week=focus["week"],
            someday=focus["someday"],
            stale_warning=stale_warning,
            static=snippets["static"],
            query=snippets["query"],
            custom=snippets["custom"],
        ).strip()
    )


# =============================================================================
# Focus Commands
# =============================================================================


def _run_focus_list(args: list[str], json_output: bool) -> int:
    """List focus items."""
    fm, _ = _get_managers()

    from protocols.dawn import Bucket

    # Parse --bucket filter
    bucket_filter = None
    for i, arg in enumerate(args):
        if arg in ("--bucket", "-b") and i + 1 < len(args):
            bucket_name = args[i + 1].upper()
            try:
                bucket_filter = Bucket[bucket_name]
            except KeyError:
                print(f"Unknown bucket: {bucket_name}. Use TODAY, WEEK, or SOMEDAY.")
                return 1

    items = fm.list(bucket=bucket_filter)

    if json_output:
        print(json.dumps([item.to_dict() for item in items], indent=2, default=str))
    else:
        _print_focus_items(items, bucket_filter)

    return 0


def _print_focus_items(items: list[Any], bucket_filter: Any) -> None:
    """Print formatted focus items."""
    from protocols.dawn import Bucket

    if not items:
        if bucket_filter:
            print(f"No focus items in {bucket_filter.value}.")
        else:
            print("No focus items. Use 'kg dawn focus add <target>' to add one.")
        return

    bucket_emoji = {
        Bucket.TODAY: "🔥",
        Bucket.WEEK: "🎯",
        Bucket.SOMEDAY: "🧘",
    }

    title = f"Focus Items ({bucket_filter.value})" if bucket_filter else "Focus Items"
    print(f"\n{title}\n{'═' * len(title)}\n")

    current_bucket = None
    for i, item in enumerate(items, 1):
        if item.bucket != current_bucket:
            current_bucket = item.bucket
            emoji = bucket_emoji.get(current_bucket, "📌")
            print(f"{emoji} {current_bucket.value.upper()}")

        stale = " ⚠️" if item.is_stale else ""
        print(f"  [{item.id}] {item.label}{stale}")
        print(f"        {item.target}")

    print()


def _run_focus_add(args: list[str], json_output: bool) -> int:
    """Add a focus item."""
    fm, _ = _get_managers()

    from protocols.dawn import Bucket

    # Parse target (first non-flag arg after "focus" "add")
    target = None
    label = None
    bucket = Bucket.TODAY

    non_flag_args = [a for a in args if not a.startswith("-")]
    if len(non_flag_args) > 2:
        target = non_flag_args[2]

    # Parse --label
    for i, arg in enumerate(args):
        if arg in ("--label", "-l") and i + 1 < len(args):
            label = args[i + 1]

    # Parse --bucket
    for i, arg in enumerate(args):
        if arg in ("--bucket", "-b") and i + 1 < len(args):
            bucket_name = args[i + 1].upper()
            try:
                bucket = Bucket[bucket_name]
            except KeyError:
                print(f"Unknown bucket: {bucket_name}. Use TODAY, WEEK, or SOMEDAY.")
                return 1

    if not target:
        print("Usage: kg dawn focus add <target> [-l label] [-b bucket]")
        return 1

    item = fm.add(target, label=label, bucket=bucket)

    if json_output:
        print(json.dumps(item.to_dict(), indent=2, default=str))
    else:
        print(f"✅ Added to {bucket.value}: {item.label}")
        print(f"   ID: {item.id}")
        print(f"   Target: {item.target}")

    return 0


def _run_focus_done(args: list[str], json_output: bool) -> int:
    """Remove/archive a focus item."""
    fm, _ = _get_managers()

    # Parse item ID
    non_flag_args = [a for a in args if not a.startswith("-")]
    if len(non_flag_args) < 3:
        print("Usage: kg dawn focus done <id>")
        return 1

    item_id = non_flag_args[2]

    # Get item first for display
    item = fm.get(item_id)
    if not item:
        print(f"Focus item not found: {item_id}")
        return 1

    success = fm.remove(item_id)

    if json_output:
        print(json.dumps({"removed": success, "id": item_id}, indent=2))
    else:
        if success:
            print(f"✅ Archived: {item.label}")
        else:
            print(f"❌ Failed to archive: {item_id}")

    return 0 if success else 1


def _run_focus_promote(args: list[str], json_output: bool) -> int:
    """Promote a focus item toward TODAY."""
    fm, _ = _get_managers()

    non_flag_args = [a for a in args if not a.startswith("-")]
    if len(non_flag_args) < 3:
        print("Usage: kg dawn focus promote <id>")
        return 1

    item_id = non_flag_args[2]

    # Get item first for display
    old_item = fm.get(item_id)
    if not old_item:
        print(f"Focus item not found: {item_id}")
        return 1

    new_item = fm.promote(item_id)

    if json_output:
        print(
            json.dumps(
                {
                    "promoted": new_item is not None,
                    "from_bucket": old_item.bucket.value,
                    "to_bucket": new_item.bucket.value if new_item else None,
                },
                indent=2,
            )
        )
    else:
        if new_item:
            print(f"⬆️ Promoted: {new_item.label}")
            print(f"   {old_item.bucket.value} → {new_item.bucket.value}")
        else:
            print(f"❌ Failed to promote: {item_id}")

    return 0 if new_item else 1


def _run_focus_demote(args: list[str], json_output: bool) -> int:
    """Demote a focus item toward SOMEDAY."""
    fm, _ = _get_managers()

    non_flag_args = [a for a in args if not a.startswith("-")]
    if len(non_flag_args) < 3:
        print("Usage: kg dawn focus demote <id>")
        return 1

    item_id = non_flag_args[2]

    # Get item first for display
    old_item = fm.get(item_id)
    if not old_item:
        print(f"Focus item not found: {item_id}")
        return 1

    new_item = fm.demote(item_id)

    if json_output:
        print(
            json.dumps(
                {
                    "demoted": new_item is not None,
                    "from_bucket": old_item.bucket.value,
                    "to_bucket": new_item.bucket.value if new_item else None,
                },
                indent=2,
            )
        )
    else:
        if new_item:
            print(f"⬇️ Demoted: {new_item.label}")
            print(f"   {old_item.bucket.value} → {new_item.bucket.value}")
        else:
            print(f"❌ Failed to demote: {item_id}")

    return 0 if new_item else 1


# =============================================================================
# Snippet Commands
# =============================================================================


def _run_snippets_list(json_output: bool) -> int:
    """List all snippets."""
    _, sl = _get_managers()

    snippets = sl.list_all()

    if json_output:
        print(json.dumps([s.to_dict() for s in snippets], indent=2, default=str))
    else:
        _print_snippets(snippets)

    return 0


def _print_snippets(snippets: list[Any]) -> None:
    """Print formatted snippets."""
    if not snippets:
        print("No snippets. Load defaults with SnippetLibrary.load_defaults().")
        return

    icons = {"static": "▶", "query": "⟳", "custom": "★"}

    print("\nSnippets (use 'kg dawn snippets copy <id>' to copy)\n")

    for snippet in snippets:
        d = snippet.to_dict()
        icon = icons.get(d.get("type", "static"), "▶")
        content = d.get("content", "")
        preview = (
            content[:40] + "..." if content and len(content) > 40 else content or "[not loaded]"
        )
        print(f"  {icon} [{d['id']}] {d['label']}")
        print(f'       "{preview}"')

    print()


def _run_snippets_copy(args: list[str], json_output: bool) -> int:
    """Copy a snippet to clipboard."""
    _, sl = _get_managers()

    non_flag_args = [a for a in args if not a.startswith("-")]
    if len(non_flag_args) < 3:
        print("Usage: kg dawn snippets copy <id>")
        return 1

    snippet_id = non_flag_args[2]

    snippet = sl.get(snippet_id)
    if not snippet:
        print(f"Snippet not found: {snippet_id}")
        return 1

    content = snippet.to_dict().get("content")
    if not content:
        content = snippet.to_dict().get("query", "[no content]")

    # Try to copy to clipboard
    copied = False
    try:
        import pyperclip

        pyperclip.copy(content)
        copied = True
    except ImportError:
        pass
    except Exception:
        pass

    if json_output:
        print(
            json.dumps(
                {
                    "copied": copied,
                    "snippet_id": snippet_id,
                    "content": content,
                },
                indent=2,
                default=str,
            )
        )
    else:
        if copied:
            print(f"📋 Copied: {snippet.to_dict()['label']}")
        else:
            print("Content (pyperclip not available):")
            print(f"  {content}")

    return 0


# =============================================================================
# Hygiene
# =============================================================================


def _run_hygiene(json_output: bool) -> int:
    """Run hygiene check on focus items."""
    fm, _ = _get_managers()

    stale_items = fm.get_stale()

    data = {
        "stale_count": len(stale_items),
        "stale_items": [item.to_dict() for item in stale_items],
    }

    if json_output:
        print(json.dumps(data, indent=2, default=str))
    else:
        _print_hygiene(stale_items)

    return 0


def _print_hygiene(stale_items: list[Any]) -> None:
    """Print hygiene report."""
    if not stale_items:
        print("✅ All focus items are fresh! No hygiene issues.")
        return

    print(f"\n⚠️ Hygiene Check: {len(stale_items)} stale items\n")

    for item in stale_items:
        print(f"  [{item.id}] {item.label}")
        print(f"       Bucket: {item.bucket.value}")
        print(f"       Last touched: {item.last_touched}")
        print("       Suggestion: promote or demote?")
        print()

    print("Actions:")
    print("  kg dawn focus promote <id>  Move toward TODAY")
    print("  kg dawn focus demote <id>   Move toward SOMEDAY")
    print("  kg dawn focus done <id>     Archive")


# =============================================================================
# Help
# =============================================================================


def _print_help() -> None:
    """Print dawn command help."""
    help_text = """
kg dawn - Dawn Cockpit (Daily Operating Surface)

"The cockpit doesn't fly the plane. The pilot flies the plane.
 The cockpit just makes it easy."

TUI MODE (default):
  kg dawn                       Launch the quarter-screen TUI

CLI MODE:
  kg dawn --cli                 Show status without TUI
  kg dawn focus                 List focus items
  kg dawn focus add <target>    Add focus item
  kg dawn focus done <id>       Archive focus item
  kg dawn focus promote <id>    Move toward TODAY
  kg dawn focus demote <id>     Move toward SOMEDAY
  kg dawn snippets              List snippets
  kg dawn snippets copy <id>    Copy snippet to clipboard
  kg dawn hygiene               Check for stale items

FOCUS OPTIONS:
  -l, --label <label>           Custom label (default: inferred from target)
  -b, --bucket <bucket>         Bucket: TODAY, WEEK, SOMEDAY (default: TODAY)

GLOBAL OPTIONS:
  --cli                         Don't launch TUI, use CLI mode
  --json                        Output as JSON
  --trace                       Show AGENTESE path being invoked
  --help, -h                    Show this help message

AGENTESE PATHS:
  time.dawn.manifest            Cockpit status
  time.dawn.focus.list          List focus items
  time.dawn.focus.add           Add focus item
  time.dawn.focus.remove        Remove focus item
  time.dawn.focus.promote       Promote focus item
  time.dawn.focus.demote        Demote focus item
  time.dawn.snippets.list       List snippets
  time.dawn.snippets.copy       Copy snippet
  time.dawn.hygiene             Hygiene check

TUI KEY BINDINGS:
  Tab         Switch between Focus and Snippet panes
  ↑↓          Navigate items
  Enter       Copy snippet / Open focus item
  1-9         Quick select by number
  a           Add focus item
  d           Mark focus done
  h           Run hygiene check
  r           Refresh
  q           Quit

EXAMPLES:
  $ kg dawn                                    # Launch TUI
  $ kg dawn focus                              # List focus items
  $ kg dawn focus add spec/dawn.md -l "Dawn"   # Add with label
  $ kg dawn focus add plans/foo.md -b WEEK    # Add to WEEK bucket
  $ kg dawn snippets copy abc123               # Copy snippet
  $ kg dawn hygiene                            # Check stale items

The cockpit serves the pilot, not vice versa.
"""
    print(help_text.strip())


# =============================================================================
# Exports
# =============================================================================


__all__ = ["cmd_dawn"]
