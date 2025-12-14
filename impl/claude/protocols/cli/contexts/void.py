"""
Void Context Router: Entropy, shadow, archetypes.

AGENTESE Context: void.*

This context handles all entropy/shadow operations (Bataille's Accursed Share):
- void.tithe             -> Gratitude/entropy (was: kgents tithe)
- void.shadow            -> Jungian shadow (was: kgents shadow)
- void.collective-shadow -> System shadow (was: kgents collective-shadow)
- void.archetype         -> Archetype analysis (was: kgents archetype)
- void.whatif            -> Alternative approaches (was: kgents whatif)
- void.mirror            -> Full introspection (was: kgents mirror)

Usage:
    kgents void                    # Show void overview
    kgents void tithe              # Pay gratitude (entropy)
    kgents void shadow             # Jungian shadow analysis
    kgents void archetype          # Archetype identification
    kgents void whatif             # Generate alternatives
    kgents void mirror             # Full introspection (Jung+Hegel+Lacan)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ContextRouter

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class VoidRouter(ContextRouter):
    """Router for void.* context (entropy, shadow, archetypes)."""

    context = "void"
    description = "Entropy, shadow, archetypes"

    def _register_holons(self) -> None:
        """Register void.* holons."""
        self.register(
            "tithe",
            "Pay gratitude (entropy budget)",
            _handle_tithe,
            aspects=["pay", "status"],
        )
        self.register(
            "shadow",
            "Jungian shadow analysis",
            _handle_shadow,
            aspects=["analyze", "surface"],
        )
        self.register(
            "collective-shadow",
            "System-level shadow from agent composition",
            _handle_collective_shadow,
            aspects=["analyze", "surface"],
        )
        self.register(
            "archetype",
            "Identify active and shadow archetypes",
            _handle_archetype,
            aspects=["identify", "analyze"],
        )
        self.register(
            "whatif",
            "Generate N alternative approaches",
            _handle_whatif,
            aspects=["generate", "compare"],
        )
        self.register(
            "mirror",
            "Full introspection (Jung + Hegel + Lacan)",
            _handle_mirror,
            aspects=["reflect", "analyze"],
        )


# =============================================================================
# Holon Handlers (delegate to existing implementations)
# =============================================================================


def _handle_tithe(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle void tithe -> delegating to existing tithe handler."""
    from protocols.cli.handlers.tithe import cmd_tithe

    return cmd_tithe(args, ctx)


def _handle_shadow(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle void shadow -> delegating to existing shadow handler."""
    from protocols.cli.handlers.shadow import cmd_shadow

    return cmd_shadow(args, ctx)


def _handle_collective_shadow(
    args: list[str], ctx: "InvocationContext | None" = None
) -> int:
    """Handle void collective-shadow -> delegating to existing handler."""
    from protocols.cli.handlers.collective_shadow import cmd_collective_shadow

    return cmd_collective_shadow(args, ctx)


def _handle_archetype(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle void archetype -> delegating to existing archetype handler."""
    from protocols.cli.handlers.archetype import cmd_archetype

    return cmd_archetype(args, ctx)


def _handle_whatif(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle void whatif -> delegating to existing whatif handler."""
    from protocols.cli.handlers.whatif import cmd_whatif

    return cmd_whatif(args, ctx)


def _handle_mirror(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle void mirror -> delegating to existing mirror handler."""
    from protocols.cli.handlers.mirror import cmd_mirror

    return cmd_mirror(args, ctx)


# =============================================================================
# Entry Point
# =============================================================================

_router: VoidRouter | None = None


def get_router() -> VoidRouter:
    """Get or create the void context router."""
    global _router
    if _router is None:
        _router = VoidRouter()
    return _router


def cmd_void(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Void context: Entropy, shadow, archetypes.

    AGENTESE: void.*

    Usage:
        kgents void                # Show overview
        kgents void tithe          # Pay gratitude
        kgents void shadow         # Jungian shadow
        kgents void whatif         # Generate alternatives
    """
    router = get_router()
    return router.route(args, ctx)
