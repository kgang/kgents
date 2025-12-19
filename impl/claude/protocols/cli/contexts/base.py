"""
Base Context Router: CLI-to-AGENTESE bridge.

Each context router maps CLI subcommands to AGENTESE paths,
enabling the Hegelian synthesis of pure protocol and professional UX.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from protocols.cli.reflector import InvocationContext as ReflectorContext


@dataclass
class Holon:
    """A holon (subcommand) within a context."""

    name: str
    description: str
    handler: Callable[..., int]
    aspects: list[str] | None = None  # Available aspects (verbs)


class ContextRouter(ABC):
    """
    Base router for AGENTESE contexts.

    Subclasses implement specific contexts (self, world, concept, void, time).
    Each router:
    1. Parses CLI args into holon + aspect + remaining args
    2. Routes to appropriate handler (existing or new)
    3. Optionally bridges to Logos for pure AGENTESE invocation
    """

    # Context name (e.g., "self", "world")
    context: str = ""

    # Context description for help
    description: str = ""

    # Registered holons (subcommands)
    holons: dict[str, Holon] = {}

    def __init__(self) -> None:
        """Initialize router and register holons."""
        self.holons = {}
        self._register_holons()

    @abstractmethod
    def _register_holons(self) -> None:
        """Register holons (subcommands) for this context."""
        pass

    def register(
        self,
        name: str,
        description: str,
        handler: Callable[..., int],
        aspects: list[str] | None = None,
    ) -> None:
        """Register a holon (subcommand)."""
        self.holons[name] = Holon(
            name=name,
            description=description,
            handler=handler,
            aspects=aspects,
        )

    def route(self, args: list[str], ctx: "ReflectorContext | None" = None) -> int:
        """
        Route CLI invocation to appropriate handler.

        Args:
            args: CLI arguments after context name (e.g., ["status"] for "kgents self status")
            ctx: Optional reflector context for dual-channel output

        Returns:
            Exit code (0 for success)
        """
        # No args -> show context help
        if not args or args[0] in ("--help", "-h"):
            self.print_help()
            return 0

        holon_name = args[0]

        # Check if it's a registered holon
        if holon_name in self.holons:
            holon = self.holons[holon_name]
            remaining_args = args[1:]
            return holon.handler(remaining_args, ctx)

        # Unknown holon
        print(f"[{self.context.upper()}] Unknown subcommand: {holon_name}")
        print(f"Run 'kgents {self.context} --help' for available commands.")
        return 1

    def print_help(self) -> None:
        """Print context-specific help."""
        print(f"kgents {self.context} - {self.description}")
        print()
        print("SUBCOMMANDS:")

        # Find max name length for alignment
        max_len = max((len(h.name) for h in self.holons.values()), default=10)

        for holon in sorted(self.holons.values(), key=lambda h: h.name):
            padding = " " * (max_len - len(holon.name) + 2)
            print(f"  {holon.name}{padding}{holon.description}")

        print()
        print(f"Run 'kgents {self.context} <subcommand> --help' for details.")

    def agentese_path(self, holon: str, aspect: str | None = None) -> str:
        """
        Construct the AGENTESE path for a CLI invocation.

        Args:
            holon: The holon name (e.g., "status", "memory")
            aspect: Optional aspect (e.g., "manifest", "witness")

        Returns:
            AGENTESE path (e.g., "self.status.manifest")
        """
        if aspect:
            return f"{self.context}.{holon}.{aspect}"
        return f"{self.context}.{holon}"


def context_help() -> str:
    """Return the main help text for AGENTESE contexts."""
    return """\
kgents - K-gents Agent Framework

COMMANDS (AGENTESE Contexts):
  self      Internal state, memory, soul
  world     Agents, infrastructure, resources
  concept   Laws, principles, dialectics
  void      Entropy, shadow, archetypes
  time      Traces, turns, telemetry
  do        Natural language intent
  flow      Pipeline composition

Run 'kgents <context>' for subcommands.
Run 'kgents <context> <subcommand> --help' for details.

OPTIONS:
  --version     Show version
  --help, -h    Show this help
  --explain     Show AGENTESE path for command

EXAMPLES:
  kgents self status           # Check system health
  kgents world agents list     # List registered agents
  kgents do "test the API"     # Natural language intent

For more: https://github.com/kgents/kgents
"""


def _emit_output(human: str, semantic: dict[str, Any], ctx: "ReflectorContext | None") -> None:
    """Emit output via dual-channel if ctx available, else print."""
    if ctx is not None:
        ctx.output(human=human, semantic=semantic)
    else:
        print(human)
