"""
World Context Router: Agents, infrastructure, resources.

AGENTESE Context: world.*

This context handles all external/world operations:
- world.agents.*  -> Agent operations (was: kgents a)
- world.daemon.*  -> Cortex daemon lifecycle (was: kgents daemon)
- world.infra.*   -> K8s infrastructure (was: kgents infra)
- world.fixture.* -> HotData fixtures (was: kgents fixture)

Usage:
    kgents world                   # Show world overview
    kgents world agents            # Agent operations
    kgents world agents list       # List registered agents
    kgents world agents run X      # Run agent X
    kgents world agents inspect X  # Inspect agent X
    kgents world daemon start      # Start cortex daemon
    kgents world infra status      # K8s cluster status
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ContextRouter

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class WorldRouter(ContextRouter):
    """Router for world.* context (agents, infrastructure, resources)."""

    context = "world"
    description = "Agents, infrastructure, resources"

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
            "infra",
            "K8s infrastructure operations",
            _handle_infra,
            aspects=["status", "deploy", "logs", "scale"],
        )
        self.register(
            "fixture",
            "HotData fixtures",
            _handle_fixture,
            aspects=["list", "refresh", "validate"],
        )
        self.register(
            "exec",
            "Q-gent execution",
            _handle_exec,
            aspects=["run"],
        )
        self.register(
            "dev",
            "Live reload development mode",
            _handle_dev,
            aspects=["start", "stop"],
        )


# =============================================================================
# Holon Handlers (delegate to existing implementations)
# =============================================================================


def _handle_agents(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world agents -> delegating to existing a_gent handler."""
    from protocols.cli.handlers.a_gent import cmd_a

    return cmd_a(args, ctx)


def _handle_daemon(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world daemon -> delegating to existing daemon handler."""
    from protocols.cli.handlers.daemon import cmd_daemon

    return cmd_daemon(args)


def _handle_infra(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world infra -> delegating to existing infra handler."""
    from protocols.cli.handlers.infra import cmd_infra

    return cmd_infra(args)


def _handle_fixture(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world fixture -> delegating to existing fixture handler."""
    from protocols.cli.handlers.fixture import cmd_fixture

    return cmd_fixture(args, ctx)


def _handle_exec(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world exec -> delegating to existing exec handler."""
    from protocols.cli.handlers.exec import cmd_exec

    return cmd_exec(args)


def _handle_dev(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle world dev -> delegating to existing dev handler."""
    from protocols.cli.handlers.dev import cmd_dev

    return cmd_dev(args)


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
