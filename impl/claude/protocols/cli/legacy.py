"""
Legacy Command Mapping: Backward compatibility for old CLI commands.

Legacy commands map to AGENTESE paths for gradual migration:
    kg forest status   → self.forest.manifest
    kg soul challenge  → self.soul.challenge
    kg town citizens   → world.town.citizens

This module enables users to continue using familiar commands
while the underlying system uses AGENTESE paths.

Per spec/protocols/agentese-v3.md §12 (CLI Unification).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# =============================================================================
# Legacy Command Mapping
# =============================================================================

# Format: "legacy command" -> "agentese path"
# Legacy commands are space-separated: "forest status" -> "self.forest.manifest"

LEGACY_COMMANDS: dict[str, str] = {
    # Forest / Planning
    # NOTE: "forest" is now a first-class command in COMMAND_REGISTRY
    # Use `kg forest manifest|status|witness|tithe|reconcile` directly
    # "forest": "self.forest.manifest",  # Removed - use kg forest instead
    # "forest status": "self.forest.manifest",  # Removed - use kg forest status
    # "forest focus": "self.forest.focus",
    # "forest trees": "self.forest.trees",
    # Soul / K-gent
    "soul": "self.soul.dialogue",
    "soul chat": "self.soul.chat",  # Interactive chat REPL
    "soul reflect": "self.soul.reflect",
    "soul challenge": "self.soul.challenge",
    "soul advise": "self.soul.advise",
    "soul explore": "self.soul.explore",
    "soul vibe": "self.soul.vibe",
    "soul stream": "self.soul.stream",
    # Memory / M-gent
    "memory": "self.memory.manifest",
    "memory status": "self.memory.manifest",
    "memory crystal": "self.memory.crystal",
    "memory field": "self.memory.field",
    "memory recall": "self.memory.recall",
    # Brain / Crown Jewel (thin handler mappings)
    "brain": "self.memory.manifest",
    "brain capture": "self.memory.capture",
    "brain search": "self.memory.recall",
    "brain ghost": "self.memory.ghost.surface",
    "brain surface": "void.memory.surface",
    "brain list": "self.memory.manifest",
    "brain status": "self.memory.manifest",
    "brain chat": "self.jewel.brain.flow.chat.query",
    "brain import": "self.memory.import",
    "brain heal": "self.memory.heal",
    # Witness / Mark-making (thin handler mappings)
    "witness": "self.witness.manifest",
    "witness mark": "self.witness.mark",
    "witness show": "self.witness.show",
    "witness recent": "self.witness.show",
    "witness list": "self.witness.show",
    "witness session": "self.witness.session",
    "witness tree": "self.witness.tree",
    "witness crystallize": "self.witness.crystallize",
    "witness crystals": "self.witness.crystals",
    "witness crystal": "self.witness.crystal",
    "witness expand": "self.witness.expand",
    "witness dashboard": "self.witness.dashboard",
    "witness stream": "self.witness.stream",
    "witness context": "self.witness.context",
    # Graph / Hypergraph: uses thin handler in handlers/graph_thin.py
    # (NOT legacy - has dedicated handler that handles DI properly)
    # Coffee / Liminal (thin handler mappings)
    "coffee": "time.coffee.manifest",
    "coffee garden": "time.coffee.garden",
    "coffee weather": "time.coffee.weather",
    "coffee menu": "time.coffee.menu",
    "coffee capture": "time.coffee.capture",
    "coffee begin": "time.coffee.begin",
    "coffee history": "time.coffee.history",
    "coffee status": "time.coffee.manifest",
    # Docs / Living Documentation (thin handler mappings)
    "docs": "concept.docs.manifest",
    "docs generate": "concept.docs.generate",
    "docs teaching": "concept.docs.teaching",
    "docs verify": "concept.docs.verify",
    "docs lint": "concept.docs.lint",
    "docs hydrate": "concept.docs.hydrate",
    "docs relevant": "concept.docs.relevant",
    "docs crystallize": "concept.docs.crystallize",
    # Status
    "status": "self.status.manifest",
    "status full": "self.status.full",
    "status cortex": "self.status.cortex",
    # Town / Multi-agent
    "town": "world.town.manifest",
    "town citizens": "world.town.citizens",
    "town coalitions": "world.town.coalitions",
    "town inhabit": "world.town.inhabit",
    "town run": "world.town.run",
    # Atelier / Creative
    "atelier": "world.atelier.manifest",
    "atelier create": "world.atelier.create",
    "atelier gallery": "world.atelier.gallery",
    "atelier collaborate": "world.atelier.collaborate",
    # Agents
    "agents": "world.agents.manifest",
    "agents list": "world.agents.list",
    "agents register": "world.agents.register",
    # Void / Entropy
    "void shadow": "void.shadow.manifest",
    "entropy": "void.entropy.manifest",
    "entropy sip": "void.entropy.sip",
    "entropy tithe": "void.entropy.tithe",
    # Time / Traces
    "trace": "time.trace.witness",
    "trace list": "time.trace.list",
    # Laws / Concepts
    "laws": "concept.laws.manifest",
    "laws verify": "concept.laws.verify",
    # Dream
    "dream": "self.dream.manifest",
    "dream run": "self.dream.run",
    # Dashboard
    "dashboard": "self.dashboard.manifest",
    "dashboard demo": "self.dashboard.demo",
}


# =============================================================================
# Legacy Resolution
# =============================================================================


@dataclass
class LegacyResolution:
    """Result of resolving a legacy command."""

    original: str
    expanded: str
    is_legacy: bool
    remaining_args: list[str] = field(default_factory=list)

    @classmethod
    def not_legacy(cls, cmd: str, args: list[str]) -> "LegacyResolution":
        """Create a resolution for a non-legacy command."""
        return cls(
            original=cmd,
            expanded=cmd,
            is_legacy=False,
            remaining_args=args,
        )


@dataclass
class LegacyRegistry:
    """
    Registry for legacy command mappings.

    Resolves multi-word legacy commands to AGENTESE paths.
    Uses longest-prefix matching for commands.
    """

    mappings: dict[str, str] = field(default_factory=lambda: LEGACY_COMMANDS.copy())

    def resolve(self, args: list[str]) -> LegacyResolution:
        """
        Resolve legacy command arguments to an AGENTESE path.

        Uses longest-prefix matching:
            ["forest", "status", "--json"] matches "forest status"
            ["forest"] matches "forest"

        Args:
            args: Command-line arguments

        Returns:
            LegacyResolution with expansion details
        """
        if not args:
            return LegacyResolution.not_legacy("", [])

        # Try longest prefix matching
        for length in range(len(args), 0, -1):
            prefix = " ".join(args[:length])
            if prefix in self.mappings:
                return LegacyResolution(
                    original=prefix,
                    expanded=self.mappings[prefix],
                    is_legacy=True,
                    remaining_args=args[length:],
                )

        # Not a legacy command
        return LegacyResolution.not_legacy(args[0], args[1:])

    def is_legacy(self, args: list[str]) -> bool:
        """Check if arguments form a legacy command."""
        if not args:
            return False

        for length in range(len(args), 0, -1):
            prefix = " ".join(args[:length])
            if prefix in self.mappings:
                return True

        return False


# =============================================================================
# Module-Level Functions
# =============================================================================

# Global registry instance
_registry: LegacyRegistry | None = None


def get_legacy_registry() -> LegacyRegistry:
    """Get the global legacy registry."""
    global _registry
    if _registry is None:
        _registry = LegacyRegistry()
    return _registry


def resolve_legacy(args: list[str]) -> LegacyResolution:
    """
    Resolve legacy command arguments to an AGENTESE path.

    Args:
        args: Command-line arguments

    Returns:
        LegacyResolution with expansion details
    """
    return get_legacy_registry().resolve(args)


def is_legacy_command(args: list[str]) -> bool:
    """Check if arguments form a legacy command."""
    return get_legacy_registry().is_legacy(args)


def expand_legacy(args: list[str]) -> tuple[str, list[str]]:
    """
    Expand legacy command to AGENTESE path.

    Args:
        args: Command-line arguments

    Returns:
        Tuple of (agentese_path, remaining_args)
    """
    result = resolve_legacy(args)
    return result.expanded, result.remaining_args


# =============================================================================
# CLI Handler for Legacy Info
# =============================================================================


def cmd_legacy(args: list[str], ctx: Any = None) -> int:
    """
    Show legacy command mappings.

    Usage:
        kg legacy                  # List all mappings
        kg legacy show <cmd>       # Show mapping for specific command
    """
    registry = get_legacy_registry()

    if not args or args[0] == "list":
        print("Legacy Command Mappings:")
        print()
        print("  These commands are deprecated. Use AGENTESE paths instead.")
        print()

        # Group by context
        groups: dict[str, list[tuple[str, str]]] = {}
        for cmd, path in sorted(registry.mappings.items()):
            context = path.split(".")[0]
            if context not in groups:
                groups[context] = []
            groups[context].append((cmd, path))

        for context in ["self", "world", "concept", "void", "time"]:
            if context not in groups:
                continue

            print(f"  {context}.*:")
            for cmd, path in groups[context]:
                print(f"    {cmd:24s} → {path}")
            print()

        return 0

    if args[0] == "show":
        if len(args) < 2:
            print("Usage: kg legacy show <command>")
            return 1

        # Resolve the remaining args as a potential legacy command
        cmd_args = args[1:]
        result = registry.resolve(cmd_args)

        if result.is_legacy:
            print(f"'{result.original}' → {result.expanded}")
            if result.remaining_args:
                print(f"  Remaining args: {result.remaining_args}")
        else:
            print(f"'{' '.join(cmd_args)}' is not a legacy command")

        return 0

    print(f"Unknown action: {args[0]}")
    print("Usage: kg legacy [list|show]")
    return 1
