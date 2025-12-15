"""
Concept Context Router: Laws, principles, dialectics.

AGENTESE Context: concept.*

This context handles all abstract/conceptual operations:
- concept.laws        -> Category laws (was: kgents laws)
- concept.principles  -> 7 principles (was: kgents principles)
- concept.dialectic   -> Hegelian synthesis (was: kgents dialectic)
- concept.gaps        -> Lacanian analysis (was: kgents gaps)
- concept.continuous  -> Recursive dialectic (was: kgents continuous)

Usage:
    kgents concept                    # Show concept overview
    kgents concept laws               # Category laws
    kgents concept laws verify        # Verify laws
    kgents concept principles         # 7 principles
    kgents concept principles check   # Check against principles
    kgents concept dialectic          # Hegelian synthesis
    kgents concept gaps               # Lacanian analysis
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from .base import ContextRouter

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext


class ConceptRouter(ContextRouter):
    """Router for concept.* context (laws, principles, dialectics)."""

    context = "concept"
    description = "Laws, principles, dialectics"

    def _register_holons(self) -> None:
        """Register concept.* holons."""
        self.register(
            "laws",
            "Category laws (identity, associativity, composition)",
            _handle_laws,
            aspects=["display", "verify"],
        )
        self.register(
            "principles",
            "The 7 design principles",
            _handle_principles,
            aspects=["display", "check"],
        )
        self.register(
            "dialectic",
            "Hegelian synthesis of opposing concepts",
            _handle_dialectic,
            aspects=["synthesize", "thesis", "antithesis"],
        )
        self.register(
            "gaps",
            "Lacanian analysis (representational gaps)",
            _handle_gaps,
            aspects=["analyze", "surface"],
        )
        self.register(
            "continuous",
            "Recursive dialectic until stability",
            _handle_continuous,
            aspects=["run", "status"],
        )
        self.register(
            "creativity",
            "Creative tools (oblique strategies, constraints, expansion)",
            _handle_creativity,
            aspects=["oblique", "constrain", "expand"],
        )


# =============================================================================
# Holon Handlers (delegate to existing implementations)
# =============================================================================


def _handle_laws(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle concept laws -> delegating to existing laws handler."""
    from protocols.cli.bootstrap.laws import cmd_laws

    return cmd_laws(args)


def _handle_principles(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle concept principles -> delegating to existing principles handler."""
    from protocols.cli.bootstrap.principles import cmd_principles

    return cmd_principles(args)


def _handle_dialectic(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle concept dialectic -> delegating to existing dialectic handler."""
    from protocols.cli.handlers.dialectic import cmd_dialectic

    return cmd_dialectic(args, ctx)


def _handle_gaps(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle concept gaps -> delegating to existing gaps handler."""
    from protocols.cli.handlers.gaps import cmd_gaps

    return cmd_gaps(args, ctx)


def _handle_continuous(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """Handle concept continuous -> delegating to existing continuous handler."""
    from protocols.cli.handlers.continuous import cmd_continuous

    return cmd_continuous(args, ctx)


def _handle_creativity(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Handle concept creativity -> routes to oblique, constrain, expand handlers.

    Usage:
        concept creativity oblique     -> kg oblique
        concept creativity constrain   -> kg constrain
        concept creativity expand      -> kg yes-and
    """
    if not args:
        # Show help for creativity sub-context
        print("concept.creativity - Creative tools")
        print()
        print("Aspects:")
        print("  oblique    - Brian Eno's lateral thinking prompts")
        print("  constrain  - Generate productive constraints")
        print("  expand     - Improv-style 'yes, and...' expansion")
        print()
        print("Usage:")
        print("  kgents concept creativity oblique")
        print("  kgents concept creativity constrain <topic>")
        print("  kgents concept creativity expand <idea>")
        return 0

    aspect = args[0].lower()
    rest = args[1:]

    if aspect == "oblique":
        from protocols.cli.handlers.oblique import cmd_oblique

        return cmd_oblique(rest, ctx)
    elif aspect == "constrain":
        from protocols.cli.handlers.constrain import cmd_constrain

        return cmd_constrain(rest, ctx)
    elif aspect in ("expand", "yes-and"):
        from protocols.cli.handlers.yes_and import cmd_yes_and

        return cmd_yes_and(rest, ctx)
    else:
        print(f"Unknown creativity aspect: {aspect}")
        print("  Available: oblique, constrain, expand")
        return 1


# =============================================================================
# Entry Point
# =============================================================================

_router: ConceptRouter | None = None


def get_router() -> ConceptRouter:
    """Get or create the concept context router."""
    global _router
    if _router is None:
        _router = ConceptRouter()
    return _router


def cmd_concept(args: list[str], ctx: "InvocationContext | None" = None) -> int:
    """
    Concept context: Laws, principles, dialectics.

    AGENTESE: concept.*

    Usage:
        kgents concept                 # Show overview
        kgents concept laws            # Category laws
        kgents concept principles      # 7 principles
        kgents concept dialectic       # Hegelian synthesis
    """
    router = get_router()
    return router.route(args, ctx)
