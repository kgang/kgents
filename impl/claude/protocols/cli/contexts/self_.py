"""
Self Context Router: Internal state, memory, soul.

AGENTESE Context: self.*

This context handles all internal agent operations:
- self.status    -> System health (was: kgents status)
- self.memory    -> Four Pillars memory (was: kgents memory)
- self.dream     -> LucidDreamer briefing (was: kgents dream)
- self.soul.*    -> K-gent soul dialogue (was: kgents soul)

Usage:
    kgents self                    # Show self overview
    kgents self status             # Cortex health
    kgents self memory             # Four Pillars memory
    kgents self dream              # LucidDreamer briefing
    kgents self soul               # Soul overview
    kgents self soul reflect       # Reflect mode
    kgents self soul advise        # Advise mode
    kgents self soul challenge     # Challenge mode
    kgents self soul explore       # Explore mode
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ContextRouter

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class SelfRouter(ContextRouter):
    """Router for self.* context (internal state, memory, soul)."""

    context = "self"
    description = "Internal state, memory, soul"

    def _register_holons(self) -> None:
        """Register self.* holons."""
        self.register(
            "status",
            "System health at a glance",
            _handle_status,
            aspects=["manifest", "full", "cortex"],
        )
        self.register(
            "memory",
            "Four Pillars memory health",
            _handle_memory,
            aspects=["status", "detail", "crystal", "field", "inference"],
        )
        self.register(
            "dream",
            "LucidDreamer morning briefing",
            _handle_dream,
            aspects=["manifest", "run", "answer"],
        )
        self.register(
            "soul",
            "K-gent soul dialogue",
            _handle_soul,
            aspects=["reflect", "advise", "challenge", "explore", "vibe", "stream"],
        )
        self.register(
            "capabilities",
            "What can I do? (affordances)",
            _handle_capabilities,
            aspects=["list", "acquire", "release"],
        )


# =============================================================================
# Holon Handlers (delegate to existing implementations)
# =============================================================================


def _handle_status(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle self status -> delegating to existing status handler."""
    from protocols.cli.handlers.status import cmd_status

    return cmd_status(args, ctx)


def _handle_memory(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle self memory -> delegating to existing memory handler."""
    from protocols.cli.handlers.memory import cmd_memory

    return cmd_memory(args)


def _handle_dream(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle self dream -> delegating to existing dream handler."""
    from protocols.cli.handlers.dream import cmd_dream

    return cmd_dream(args)


def _handle_soul(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle self soul -> delegating to existing soul handler."""
    from protocols.cli.handlers.soul import cmd_soul

    return cmd_soul(args, ctx)


def _handle_capabilities(
    args: list[str], ctx: "InvocationContext | None" = None
) -> int:
    """Handle self capabilities -> list available affordances."""
    print("[SELF] Capabilities (affordances):")
    print()
    print("  Internal Operations:")
    print("    status      - System health at a glance")
    print("    memory      - Four Pillars memory health")
    print("    dream       - LucidDreamer morning briefing")
    print("    soul        - K-gent soul dialogue")
    print()
    print("  Soul Modes:")
    print("    soul reflect   - Mirror back for examination")
    print("    soul advise    - Offer preference-aligned suggestions")
    print("    soul challenge - Push back constructively")
    print("    soul explore   - Follow tangents, generate hypotheses")
    print()
    print("  Quick Commands:")
    print("    soul vibe      - One-liner eigenvector summary")
    print("    soul drift     - Compare vs previous session")
    print("    soul tense     - Surface current tensions")
    return 0


# =============================================================================
# Entry Point
# =============================================================================

# Singleton router instance
_router: SelfRouter | None = None


def get_router() -> SelfRouter:
    """Get or create the self context router."""
    global _router
    if _router is None:
        _router = SelfRouter()
    return _router


def cmd_self(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Self context: Internal state, memory, soul.

    AGENTESE: self.*

    Usage:
        kgents self                # Show overview
        kgents self status         # System health
        kgents self memory         # Four Pillars
        kgents self dream          # LucidDreamer
        kgents self soul           # K-gent soul
    """
    router = get_router()
    return router.route(args, ctx)
