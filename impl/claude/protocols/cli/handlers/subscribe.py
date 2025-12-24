"""
Subscribe CLI Handler: Subscribe to AGENTESE events.

Usage:
    kg subscribe self.memory.*     # Subscribe to memory changes
    kg subscribe world.town.**     # Subscribe to all town events
    kg subscribe self.forest.*     # Subscribe to forest changes

Per spec/protocols/agentese-v3.md §9 (Subscriptions).
"""

from __future__ import annotations

import asyncio
import signal
from typing import TYPE_CHECKING, Any

from protocols.cli.handler_meta import handler

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


@handler("subscribe", is_async=False, needs_pty=False, tier=1, description="Subscribe to AGENTESE events")
def cmd_subscribe(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Subscribe to AGENTESE events.

    Subscriptions provide continuous observation of path events.
    Uses pattern matching with wildcards:
        *  - matches single segment
        ** - matches multiple segments

    Events include:
        INVOKED - Path was invoked
        CHANGED - State changed
        ERROR   - Error occurred
        REFUSED - Consent refusal

    Press Ctrl+C to stop the subscription.
    """
    if not args or args[0] in ("--help", "-h"):
        _print_help()
        return 0

    pattern = args[0]
    remaining = args[1:]

    # Parse options
    json_output = "--json" in remaining
    verbose = "--verbose" in remaining or "-v" in remaining

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        return loop.run_until_complete(_subscribe_async(pattern, json_output, verbose))
    except KeyboardInterrupt:
        print("\nSubscription ended.")
        return 0


async def _subscribe_async(pattern: str, json_output: bool, verbose: bool) -> int:
    """Run subscription asynchronously."""
    try:
        from protocols.agentese import (
            Observer,
            create_subscription_manager,
            create_wired_logos,
        )

        logos = create_wired_logos()
        _ = Observer.from_archetype("cli")  # For future use

        # Get or create subscription manager
        if hasattr(logos, "_subscription_manager") and logos._subscription_manager:
            sub_manager = logos._subscription_manager
        else:
            sub_manager = create_subscription_manager()

        print(f"Subscribing to: {pattern}")
        print("Press Ctrl+C to stop")
        print()

        subscription = await sub_manager.subscribe(pattern)

        try:
            async for event in subscription:
                if json_output:
                    import json

                    print(
                        json.dumps(
                            {
                                "path": event.path,
                                "event_type": event.event_type.value,
                                "timestamp": event.timestamp.isoformat(),
                                "data": str(event.data) if event.data else None,
                            }
                        )
                    )
                else:
                    timestamp = event.timestamp.strftime("%H:%M:%S.%f")[:-3]
                    event_type = event.event_type.value.upper()
                    print(f"[{timestamp}] {event_type}: {event.path}")

                    if verbose and event.data:
                        print(f"  Data: {event.data}")

        except asyncio.CancelledError:
            pass
        finally:
            await subscription.unsubscribe()

        return 0

    except ImportError as e:
        print(f"Error: Subscription system not available: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


def _print_help() -> None:
    """Print help text."""
    print("""\
kg subscribe - Subscribe to AGENTESE events

USAGE:
    kg subscribe <pattern> [options]

PATTERNS:
    self.memory.*      Memory changes
    world.town.**      All town events (recursive)
    self.forest.*      Forest changes
    void.entropy.*     Entropy events

EVENT TYPES:
    INVOKED  - Path was invoked
    CHANGED  - State changed
    ERROR    - Error occurred
    REFUSED  - Consent refusal

OPTIONS:
    --json             JSON output
    --verbose, -v      Show event data

EXAMPLES:
    kg subscribe self.memory.*
    kg subscribe world.town.** --json
    kg subscribe void.entropy.* --verbose

Press Ctrl+C to stop the subscription.
""")
