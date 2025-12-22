"""
World Context Router: Agents, resources.

AGENTESE Context: world.*

This context handles all external/world operations:
- world.agents.*    -> Agent operations (was: kgents a)
- world.daemon.*    -> Cortex daemon lifecycle (was: kgents daemon)
- world.fixture.*   -> HotData fixtures (was: kgents fixture)
- world.codebase.*  -> Architecture analysis (Gestalt)
- world.town.*      -> Agent Town simulation

Usage:
    kgents world                   # Show world overview
    kgents world agents            # Agent operations
    kgents world agents list       # List registered agents
    kgents world agents run X      # Run agent X
    kgents world daemon start      # Start cortex daemon
    kgents world codebase          # Architecture overview
    kgents world town start        # Start Agent Town
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ContextRouter

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class WorldRouter(ContextRouter):
    """Router for world.* context (agents, resources)."""

    context = "world"
    description = "Agents and resources"

    def _register_holons(self) -> None:
        """Register world.* holons."""
        self.register(
            "agents",
            "Agent operations (list, run, inspect, new)",
            _handle_agents,
            aspects=["list", "run", "inspect", "new", "manifest", "dialogue"],
        )
        self.register(
            "daemon",
            "Cortex daemon lifecycle",
            _handle_daemon,
            aspects=["start", "stop", "status", "install", "logs"],
        )
        self.register(
            "fixture",
            "HotData fixtures",
            _handle_fixture,
            aspects=["list", "refresh", "validate"],
        )
        self.register(
            "dev",
            "Live reload development mode",
            _handle_dev,
            aspects=["start", "stop"],
        )
        self.register(
            "town",
            "Agent Town civilizational simulation",
            _handle_town,
            aspects=["start", "step", "observe", "lens", "metrics", "budget"],
        )
        self.register(
            "viz",
            "Visualization utilities (sparkline, graphs)",
            _handle_viz,
            aspects=["sparkline", "graph", "table"],
        )
        self.register(
            "codebase",
            "Architecture analysis and governance (Gestalt)",
            _handle_codebase,
            aspects=["manifest", "health", "drift", "module", "scan"],
        )


# =============================================================================
# Holon Handlers (delegate to existing implementations)
# =============================================================================


def _handle_agents(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world agents -> delegating to existing a_gent handler."""
    from protocols.cli.handlers.a_gent import cmd_a  # type: ignore[import-untyped]

    result: int = cmd_a(args, ctx)
    return result


def _handle_daemon(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world daemon -> delegating to existing daemon handler."""
    from protocols.cli.handlers.daemon import cmd_daemon  # type: ignore[import-untyped]

    result: int = cmd_daemon(args)
    return result


def _handle_fixture(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world fixture -> delegating to existing fixture handler."""
    from protocols.cli.handlers.fixture import cmd_fixture  # type: ignore[import-untyped]

    result: int = cmd_fixture(args, ctx)
    return result


def _handle_dev(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world dev -> delegating to existing dev handler."""
    from protocols.cli.handlers.dev import cmd_dev  # type: ignore[import-untyped]

    result: int = cmd_dev(args)
    return result


def _handle_town(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world town -> delegating to Agent Town handler."""
    from protocols.cli.handlers.town import cmd_town  # type: ignore[import-untyped]

    result: int = cmd_town(args, ctx)
    return result


def _handle_codebase(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world codebase -> delegating to Gestalt handler."""
    from protocols.gestalt.handler import cmd_codebase  # type: ignore[import-untyped]

    return cmd_codebase(args, ctx)  # type: ignore[no-any-return]


def _handle_viz(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Handle world viz -> routes to visualization handlers.

    Usage:
        world viz sparkline <numbers>  -> Unicode sparkline
        world viz graph <data>         -> ASCII graph (future)
        world viz table <data>         -> Formatted table (future)
    """
    if not args:
        print("world.viz - Visualization utilities")
        print()
        print("Aspects:")
        print("  sparkline  - Render numbers as Unicode sparkline")
        print("  graph      - ASCII graphs (coming soon)")
        print("  table      - Formatted tables (coming soon)")
        print()
        print("Usage:")
        print("  kgents world viz sparkline 1 2 3 4 5")
        return 0

    aspect = args[0].lower()
    rest = args[1:]

    if aspect == "sparkline":
        import protocols.cli.handlers.sparkline as sparkline_mod  # type: ignore[import-untyped]

        result: int = sparkline_mod.cmd_sparkline(rest, ctx)
        return result
    else:
        print(f"Unknown viz aspect: {aspect}")
        print("  Available: sparkline")
        return 1


# =============================================================================
# Entry Point
# =============================================================================

# Singleton router instance
_router: WorldRouter | None = None


def get_router() -> WorldRouter:
    """Get or create the world context router."""
    global _router
    if _router is None:
        _router = WorldRouter()
    return _router


def cmd_world(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    World context: Agents, infrastructure, resources.

    AGENTESE: world.*

    Usage:
        kgents world                # Show overview
        kgents world agents list    # List registered agents
        kgents world daemon start   # Start cortex daemon
        kgents world infra status   # K8s cluster status
    """
    router = get_router()
    return router.route(args, ctx)
