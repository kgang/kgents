"""
Shared utilities for witness CLI handlers.

Provides:
- Rich console helpers
- Async bootstrapping
- Timestamp parsing
- Common formatting functions
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass


# =============================================================================
# Rich Console Helpers
# =============================================================================


def _get_console() -> Any:
    """Get Rich console for pretty output."""
    try:
        from rich.console import Console

        return Console()
    except ImportError:
        return None


def _print_mark(mark: dict[str, Any], verbose: bool = False) -> None:
    """Print a single mark."""
    import shutil

    console = _get_console()

    # Get terminal width for truncation
    try:
        term_width = shutil.get_terminal_size().columns
    except Exception:
        term_width = 80

    # Extract fields
    timestamp = mark.get("timestamp", "")
    action = mark.get("action", mark.get("response", {}).get("content", ""))
    reasoning = mark.get("reasoning", "")
    principles = mark.get("principles", mark.get("tags", []))
    mark_id = mark.get("id", mark.get("mark_id", ""))[:12]

    # Format timestamp
    try:
        dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        ts_str = dt.strftime("%H:%M")
    except (ValueError, AttributeError):
        ts_str = "??:??"

    # Truncate long actions to fit terminal width
    # Reserve space for timestamp (8), indent (2), and ellipsis (3)
    max_action_len = term_width - 15
    display_action = action
    if len(action) > max_action_len and max_action_len > 10:
        display_action = action[: max_action_len - 3] + "..."

    if console:
        # Rich output with no_wrap to prevent line breaking
        principle_str = " ".join(f"[dim][{p}][/dim]" for p in principles) if principles else ""
        line = f"  [dim]{ts_str}[/dim]  {display_action}"
        if principle_str:
            line += f" {principle_str}"
        console.print(line, overflow="ignore", no_wrap=True)

        if verbose and reasoning:
            console.print(f"         [dim]-> {reasoning}[/dim]", overflow="ignore", no_wrap=True)
    else:
        # Plain text
        line = f"  {ts_str}  {display_action}"
        if principles:
            line += f" [{', '.join(principles)}]"
        print(line)
        if verbose and reasoning:
            print(f"         -> {reasoning}")


def _print_marks(
    marks: list[dict[str, Any]], title: str = "Recent Marks", verbose: bool = False
) -> None:
    """Print a list of marks."""
    console = _get_console()

    if not marks:
        if console:
            console.print("[dim]No marks found.[/dim]")
        else:
            print("No marks found.")
        return

    if console:
        console.print(f"\n[bold]{title}[/bold]")
        console.print("[dim]" + "─" * 40 + "[/dim]")
    else:
        print(f"\n{title}")
        print("─" * 40)

    for mark in marks:
        _print_mark(mark, verbose=verbose)

    if console:
        console.print()
    else:
        print()


def _parse_timestamp(ts: str) -> datetime:
    """Parse ISO timestamp string to datetime."""
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00")).replace(tzinfo=None)
    except (ValueError, AttributeError):
        return datetime.min


# =============================================================================
# Async Bootstrap Helpers
# =============================================================================


async def _bootstrap_and_run(coro_func: Any, *args: Any, **kwargs: Any) -> Any:
    """
    Bootstrap services and run a coroutine in a fresh context.

    This ensures services are properly initialized before use.

    Note: We DON'T call reset_registry() or reset_container() because:
    - In daemon mode: Services are already bootstrapped, resetting breaks them
    - In CLI mode: Each asyncio.run() creates a fresh event loop anyway
    - Resetting while connections are in use causes "operation in progress" errors
    """
    from services.bootstrap import bootstrap_services

    # Bootstrap fresh on this event loop (idempotent if already done)
    await bootstrap_services()

    # Now run the actual coroutine
    return await coro_func(*args, **kwargs)


def _run_async_factory(coro_func: Any) -> Any:
    """
    Create a sync wrapper that properly bootstraps before running async code.

    Returns a function that, when called with args, will:
    1. Check if running inside daemon (KGENTS_DAEMON_WORKER env var)
    2. In daemon mode: Create fresh event loop WITHOUT re-bootstrapping
    3. In standalone mode: Create fresh event loop WITH bootstrapping

    The key insight is that in daemon mode, services are already bootstrapped
    on the daemon's main event loop. We just need a fresh event loop for
    this synchronous call, but we should NOT re-bootstrap (which would
    create conflicting database connections).
    """
    from functools import wraps

    @wraps(coro_func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Check if we're running inside daemon worker context
        in_daemon = os.environ.get("KGENTS_DAEMON_WORKER") is not None

        # Create a fresh event loop explicitly
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            if in_daemon:
                # In daemon mode: run directly without re-bootstrapping
                # Services are already available, just run the coroutine
                return loop.run_until_complete(coro_func(*args, **kwargs))
            else:
                # Standalone CLI mode: bootstrap before running
                return loop.run_until_complete(_bootstrap_and_run(coro_func, *args, **kwargs))
        finally:
            # Clean up completely
            try:
                # Cancel all pending tasks
                pending = asyncio.all_tasks(loop)
                for task in pending:
                    task.cancel()
                # Run loop once more to process cancellations
                if pending:
                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                # Now close the loop
                loop.close()
            except Exception:
                pass
            finally:
                # Clear thread-local reference
                asyncio.set_event_loop(None)

    return wrapper
