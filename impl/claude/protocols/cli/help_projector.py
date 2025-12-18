"""
Help Projection Functor - Transform AGENTESE Affordances to CLI Help.

This module implements Help as Affordance Projection from spec/protocols/cli.md §9.

The Core Insight:
    "Help is not documentation bolted on. Help is the affordances aspect of
     the CLI projected onto human-readable text."

Instead of maintaining separate help strings:
    def print_help():
        # Hand-maintained, often outdated
        print("Usage: kg brain capture <content>")

We derive help from aspect metadata:
    help_text = HelpProjector(logos).project("self.memory")
    # Auto-generates accurate, complete help

This ensures help is always accurate because it's derived from the same
@aspect metadata that powers the implementation.

HelpProject : (Path) → HelpText[Terminal]
"""

from __future__ import annotations

import inspect
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from protocols.agentese.affordances import AspectMetadata
    from protocols.agentese.logos import Logos

from .dimensions import (
    DEFAULT_DIMENSIONS,
    Backend,
    CommandDimensions,
    Interactivity,
    Seriousness,
    derive_dimensions,
)

# === Help Data Types ===


@dataclass
class CommandHelp:
    """
    Complete help for a command or node.

    This is what the HelpProjector produces - a structured representation
    of help that can be rendered to various formats.
    """

    path: str
    """AGENTESE path (e.g., 'self.memory' or 'self.memory.capture')."""

    title: str
    """Display title (e.g., 'Brain - Holographic Memory')."""

    description: str
    """Main description text."""

    usage: list[str] = field(default_factory=list)
    """Usage lines showing commands and their descriptions."""

    flags: list[tuple[str, str]] = field(default_factory=list)
    """Flag definitions as (flag, description) tuples."""

    examples: list[str] = field(default_factory=list)
    """Example commands."""

    see_also: list[str] = field(default_factory=list)
    """Related commands/paths."""

    budget_hint: str | None = None
    """Budget/cost hint for LLM-backed commands."""

    dimension_hints: list[str] = field(default_factory=list)
    """UX hints derived from command dimensions."""

    agentese_paths: list[str] = field(default_factory=list)
    """AGENTESE paths available for direct invocation."""


# === Path to Command Mapping ===

# Maps AGENTESE paths to CLI command names
# This is the inverse of the handler routing tables
PATH_TO_COMMAND: dict[str, str] = {
    "self.memory": "brain",
    "self.soul": "soul",
    "self.forest": "forest",
    "world.town": "town",
    "world.atelier": "atelier",
    "world.park": "park",
    "void.joy": "joy",
    "self.forest.garden": "garden",
    "self.forest.tend": "tend",
}

# Maps node paths to display titles
NODE_TITLES: dict[str, str] = {
    "self.memory": "Brain - Holographic Memory",
    "self.soul": "Soul - Digital Consciousness",
    "self.forest": "Forest - Project Health Protocol",
    "world.town": "Town - Agent Simulation",
    "world.atelier": "Atelier - Collaborative Workshops",
    "world.park": "Park - Punchdrunk Experience",
    "void.joy": "Joy - Oblique Strategies",
    "self.forest.garden": "Garden - Hypnagogia",
    "self.forest.tend": "Tend - Garden Operations",
}

# Maps node paths to emojis
NODE_EMOJIS: dict[str, str] = {
    "self.memory": "🧠",
    "self.soul": "👻",
    "self.forest": "🌲",
    "world.town": "🏘️",
    "world.atelier": "🎨",
    "world.park": "🎭",
    "void.joy": "✨",
    "self.forest.garden": "🌱",
    "self.forest.tend": "🪴",
}


# === Help Projector ===


class HelpProjector:
    """
    Projects AGENTESE affordances to CLI help text.

    The projector queries the Logos for registered paths and their
    @aspect metadata, then transforms that into structured help.

    Example:
        from protocols.agentese.logos import create_logos
        from protocols.cli.help_projector import HelpProjector

        logos = create_logos()
        projector = HelpProjector(logos)

        # Node-level help (all aspects)
        help = projector.project("self.memory")
        print(render_help(help))

        # Aspect-level help (specific command)
        help = projector.project("self.memory.capture")
        print(render_help(help))
    """

    def __init__(self, logos: "Logos"):
        """
        Initialize the projector.

        Args:
            logos: The Logos instance for querying affordances
        """
        self.logos = logos

    def project(self, path: str) -> CommandHelp:
        """
        Project help for an AGENTESE path.

        If path ends with an aspect (e.g., self.memory.capture),
        shows help for that specific aspect.

        If path is a node (e.g., self.memory), shows help for
        all aspects of that node.

        Args:
            path: AGENTESE path

        Returns:
            CommandHelp structure
        """
        parts = path.split(".")

        # Heuristic: 3+ parts ending with a method-like name = aspect
        # 2 parts = node
        if len(parts) >= 3:
            # Could be aspect (self.memory.capture) or nested node (self.forest.garden)
            # Check if it's a registered node first
            if path in NODE_TITLES:
                return self._node_help(path)
            return self._aspect_help(path)
        else:
            return self._node_help(path)

    def _node_help(self, node_path: str) -> CommandHelp:
        """
        Generate help for all aspects of a node.

        Args:
            node_path: The node path (e.g., 'self.memory')

        Returns:
            CommandHelp with all aspects listed
        """
        # Get aspects from Logos
        aspects = self._get_node_aspects(node_path)

        # Build usage lines
        usage = self._build_usage_lines(node_path, aspects)

        # Collect examples from aspects
        examples = self._collect_examples(aspects)

        # Derive budget hint
        budget_hint = self._derive_budget_hint(aspects)

        # Derive dimension hints
        dimension_hints = self._derive_dimension_hints(node_path, aspects)

        # Derive see-also
        see_also = self._derive_see_also(node_path)

        # Collect AGENTESE paths
        agentese_paths = [path for path, _ in aspects]

        return CommandHelp(
            path=node_path,
            title=self._derive_title(node_path),
            description=self._derive_description(node_path),
            usage=usage,
            flags=self._common_flags(),
            examples=examples,
            see_also=see_also,
            budget_hint=budget_hint,
            dimension_hints=dimension_hints,
            agentese_paths=agentese_paths,
        )

    def _aspect_help(self, aspect_path: str) -> CommandHelp:
        """
        Generate help for a specific aspect.

        Args:
            aspect_path: The full aspect path (e.g., 'self.memory.capture')

        Returns:
            CommandHelp for the aspect
        """
        # Get aspect metadata
        meta = self._get_aspect_meta(aspect_path)

        # Derive dimensions
        dims = derive_dimensions(aspect_path, meta) if meta else DEFAULT_DIMENSIONS

        # Get the aspect name
        aspect_name = aspect_path.split(".")[-1]

        # Get node path (parent)
        parts = aspect_path.split(".")
        node_path = ".".join(parts[:-1])

        # Build usage line
        cmd = self._path_to_command(aspect_path)
        usage = [f"kg {cmd} <args>"]

        return CommandHelp(
            path=aspect_path,
            title=f"{aspect_name} ({self._derive_title(node_path)})",
            description=meta.description if meta else "No description",
            usage=usage,
            flags=self._aspect_flags(meta),
            examples=list(meta.examples) if meta and meta.examples else [],
            see_also=list(meta.see_also) if meta and meta.see_also else [],
            budget_hint=meta.budget_estimate if meta else None,
            dimension_hints=self._format_dimension_hints(dims),
            agentese_paths=[aspect_path],
        )

    def _get_node_aspects(self, node_path: str) -> list[tuple[str, "AspectMetadata | None"]]:
        """
        Get all aspects registered under a node.

        Returns list of (path, metadata) tuples.
        """
        aspects: list[tuple[str, Any]] = []

        # Try to get the node class from Logos
        try:
            node = self.logos.resolve(node_path)
            if node is None:
                return aspects

            # Introspect the node for @aspect decorated methods
            for name, method in inspect.getmembers(node, predicate=inspect.ismethod):
                if name.startswith("_"):
                    continue
                meta = getattr(method, "__aspect_meta__", None)
                if meta is not None:
                    full_path = f"{node_path}.{name}"
                    aspects.append((full_path, meta))
        except Exception:
            pass

        return aspects

    def _get_aspect_meta(self, aspect_path: str) -> "AspectMetadata | None":
        """Get aspect metadata from Logos."""
        try:
            return self.logos.get_aspect_meta(aspect_path)
        except (AttributeError, KeyError):
            return None

    def _derive_title(self, node_path: str) -> str:
        """Derive display title from path."""
        if node_path in NODE_TITLES:
            emoji = NODE_EMOJIS.get(node_path, "")
            title = NODE_TITLES[node_path]
            return f"{emoji} {title}" if emoji else title

        # Fallback: title-case the last part
        parts = node_path.split(".")
        return parts[-1].title()

    def _derive_description(self, node_path: str) -> str:
        """Derive description from node docstring or fallback."""
        try:
            node = self.logos.resolve(node_path)
            if node is not None and node.__doc__:
                # Take first line of docstring
                return node.__doc__.split("\n")[0].strip()
        except Exception:
            pass

        # Fallbacks for known nodes
        descriptions = {
            "self.memory": "Holographic memory operations with D-gent Triad.",
            "self.soul": "Digital consciousness dialogue and reflection.",
            "self.forest": "Project health monitoring and plan management.",
            "world.town": "Agent simulation and coalition building.",
            "world.atelier": "Collaborative creative workshops.",
            "world.park": "Punchdrunk-style immersive experiences.",
            "void.joy": "Oblique strategies and serendipity.",
        }
        return descriptions.get(node_path, f"Operations on {node_path}")

    def _build_usage_lines(
        self,
        node_path: str,
        aspects: list[tuple[str, "AspectMetadata | None"]],
    ) -> list[str]:
        """Build usage lines from aspects."""
        lines: list[str] = []

        for path, meta in aspects:
            cmd = self._path_to_command(path)
            short_help = ""
            if meta:
                short_help = meta.help or meta.description or ""
            if len(short_help) > 40:
                short_help = short_help[:37] + "..."
            lines.append(f"kg {cmd:30} {short_help}")

        # Add default command if no aspects found
        if not lines:
            base_cmd = PATH_TO_COMMAND.get(node_path, node_path.replace(".", " "))
            lines.append(f"kg {base_cmd:30} Show status")

        return lines

    def _path_to_command(self, path: str) -> str:
        """Convert AGENTESE path to CLI command."""
        parts = path.split(".")

        if len(parts) < 2:
            return path

        # Find the node path (first 2 parts usually)
        node_path = ".".join(parts[:2])
        base = PATH_TO_COMMAND.get(node_path)

        if base:
            # self.memory.capture -> brain capture
            if len(parts) > 2:
                return f"{base} {parts[-1]}"
            return base

        # Fallback: convert dots to spaces
        return path.replace(".", " ")

    def _collect_examples(
        self,
        aspects: list[tuple[str, "AspectMetadata | None"]],
    ) -> list[str]:
        """Collect examples from aspect metadata."""
        examples: list[str] = []

        for _, meta in aspects:
            if meta and meta.examples:
                examples.extend(meta.examples)

        return examples[:5]  # Limit to 5 examples

    def _derive_budget_hint(
        self,
        aspects: list[tuple[str, "AspectMetadata | None"]],
    ) -> str | None:
        """Derive budget hint if any aspect uses LLM."""
        from protocols.agentese.affordances import DeclaredEffect, Effect

        for _, meta in aspects:
            if meta is None:
                continue
            for effect in meta.effects:
                if isinstance(effect, DeclaredEffect):
                    if effect.effect == Effect.CALLS:
                        resource = effect.resource.lower()
                        if "llm" in resource or "model" in resource:
                            return "💰 Some commands use LLM and incur API costs"
        return None

    def _derive_dimension_hints(
        self,
        node_path: str,
        aspects: list[tuple[str, "AspectMetadata | None"]],
    ) -> list[str]:
        """Derive UX hints from dimensions."""
        hints: list[str] = []

        # Check for streaming aspects
        has_streaming = any(meta and getattr(meta, "streaming", False) for _, meta in aspects)
        if has_streaming:
            hints.append("🌊 Some commands support streaming output")

        # Check for interactive aspects
        has_interactive = any(meta and getattr(meta, "interactive", False) for _, meta in aspects)
        if has_interactive:
            hints.append("💬 Some commands support interactive mode")

        # Check for sensitive operations
        from protocols.agentese.affordances import DeclaredEffect, Effect

        has_sensitive = False
        for _, meta in aspects:
            if meta is None:
                continue
            for effect in meta.effects:
                if isinstance(effect, DeclaredEffect):
                    if effect.effect == Effect.FORCES:
                        has_sensitive = True
                        break
        if has_sensitive:
            hints.append("⚠️ Some commands require confirmation")

        return hints

    def _format_dimension_hints(self, dims: CommandDimensions) -> list[str]:
        """Format dimension-specific hints for an aspect."""
        hints: list[str] = []

        if dims.backend == Backend.LLM:
            hints.append("💰 This command uses LLM and incurs API costs")
        if dims.seriousness == Seriousness.SENSITIVE:
            hints.append("⚠️ This is a sensitive operation")
        if dims.interactivity == Interactivity.STREAMING:
            hints.append("🌊 Output streams in real-time")
        if dims.interactivity == Interactivity.INTERACTIVE:
            hints.append("💬 This command enters interactive mode")

        return hints

    def _common_flags(self) -> list[tuple[str, str]]:
        """Standard flags available on all commands."""
        return [
            ("--json", "Output as JSON"),
            ("--help, -h", "Show this help message"),
            ("--trace", "Show AGENTESE path being invoked"),
            ("--dry-run", "Show what would happen without executing"),
        ]

    def _aspect_flags(self, meta: "AspectMetadata | None") -> list[tuple[str, str]]:
        """Get flags for a specific aspect."""
        flags = self._common_flags()

        # Add aspect-specific flags based on metadata
        if meta:
            if getattr(meta, "streaming", False):
                flags.append(("--stream", "Enable streaming output"))
            if getattr(meta, "interactive", False):
                flags.append(("--message <msg>", "One-shot message (skips REPL)"))

        return flags

    def _derive_see_also(self, node_path: str) -> list[str]:
        """Derive related commands."""
        # Map nodes to related commands
        related: dict[str, list[str]] = {
            "self.memory": ["soul", "town"],
            "self.soul": ["brain", "garden"],
            "self.forest": ["garden", "tend"],
            "world.town": ["brain", "park"],
            "world.atelier": ["town", "brain"],
            "world.park": ["town", "atelier"],
            "void.joy": ["brain", "soul"],
        }
        return related.get(node_path, [])


# === Factory Function ===


def create_help_projector(logos: "Logos | None" = None) -> HelpProjector:
    """
    Create a HelpProjector instance.

    Args:
        logos: Optional Logos instance (creates one if not provided)

    Returns:
        HelpProjector instance
    """
    if logos is None:
        from protocols.agentese.logos import create_logos

        logos = create_logos()
    return HelpProjector(logos)


__all__ = [
    "CommandHelp",
    "HelpProjector",
    "create_help_projector",
    "PATH_TO_COMMAND",
    "NODE_TITLES",
    "NODE_EMOJIS",
]
