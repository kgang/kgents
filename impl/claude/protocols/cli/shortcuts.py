"""
CLI Shortcuts: Ergonomic aliases for common AGENTESE paths.

Shortcuts provide muscle-memory access to frequently used paths:
    /forest  → self.forest.manifest
    /soul    → self.soul.dialogue
    /chaos   → void.entropy.sip
    /town    → world.town.manifest

Shortcut Grammar:
    /<name>           # Invoke default aspect
    /<name>.<aspect>  # Invoke specific aspect

Design Principles:
    - Shortcuts are prefix expansions (like bash aliases)
    - Shortcuts cannot shadow contexts (world, self, etc.)
    - Shortcuts are user-definable via .kgents/shortcuts.yaml
    - Standard shortcuts are always available

Per spec/protocols/agentese-v3.md §12 (CLI Unification).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

import yaml

if TYPE_CHECKING:
    from protocols.agentese import Logos

# =============================================================================
# Standard Shortcuts (always available)
# =============================================================================

STANDARD_SHORTCUTS: dict[str, str] = {
    # ==========================================================================
    # Forest / Planning (The Gardener foundation)
    # ==========================================================================
    "forest": "self.forest.manifest",
    "plan": "self.forest.status",
    "focus": "self.forest.focus",
    "evolve": "self.forest.evolve",
    # ==========================================================================
    # Soul / K-gent
    # ==========================================================================
    "soul": "self.soul.dialogue",
    "reflect": "self.soul.reflect",
    "challenge": "self.soul.challenge",
    "advise": "self.soul.advise",
    # ==========================================================================
    # CROWN JEWEL 1: Metaphysical Forge
    # "Where agents are built. No spectators, just the work."
    # ==========================================================================
    "mforge": "world.forge.manifest",
    "gallery": "world.forge.gallery.manifest",
    # ==========================================================================
    # CROWN JEWEL 2: Task Management
    # ==========================================================================
    "forge": "world.forge.manifest",
    "task": "concept.task.manifest",
    "tasks": "?concept.task.*",
    "credits": "self.credits.manifest",
    # ==========================================================================
    # CROWN JEWEL 3: Holographic Second Brain (Sheaf)
    # "Knowledge as living topology, not filing cabinet"
    # ==========================================================================
    "brain": "self.memory.manifest",
    "capture": "self.memory.capture",
    "recall": "self.memory.recall",
    "crystals": "?self.memory.crystal.*",
    "ghost": "self.memory.ghost.surface",
    "map": "self.memory.cartography.manifest",
    # ==========================================================================
    # Note: Park Crown Jewel removed 2025-12-21 (extinction)
    # ==========================================================================
    # CROWN JEWEL 4: Domain Simulation Engine (Tenancy)
    # "Agent Town configured for any domain with enterprise requirements"
    # ==========================================================================
    "sim": "world.simulation.manifest",
    "drill": "concept.drill.manifest",
    "drills": "?concept.drill.*",
    "inject": "world.simulation.inject",
    "advance": "world.simulation.advance",
    "audit": "time.simulation.witness",
    "export": "time.simulation.export",
    # ==========================================================================
    # CROWN JEWEL 5: Gestalt Architecture Visualizer (Reactive)
    # "Architecture diagrams that never rot because they never stop watching"
    # ==========================================================================
    "arch": "world.codebase.manifest",
    "modules": "?world.codebase.module.*",
    "drift": "world.codebase.drift.witness",
    "codehealth": "world.codebase.health.manifest",
    "layers": "?world.codebase.layer.*",
    "governance": "concept.governance.manifest",
    "tour": "world.codebase.tour",
    # ==========================================================================
    # CROWN JEWEL 6: The Gardener (N-Phase)
    # "The form that generates forms. The garden that tends itself."
    # ==========================================================================
    "garden": "concept.gardener.manifest",
    "session": "concept.gardener.session.manifest",
    "continue": "concept.gardener.session.resume",
    "propose": "concept.gardener.propose",
    "route": "concept.gardener.route",
    # ==========================================================================
    # Town / Multi-agent (core system, used by multiple jewels)
    # ==========================================================================
    "town": "world.town.manifest",
    "citizens": "world.town.citizens",
    # ==========================================================================
    # Void / Entropy (serendipity across all jewels)
    # ==========================================================================
    "chaos": "void.entropy.sip",
    "surprise": "void.entropy.sip",
    "shadow": "void.shadow.manifest",
    "tithe": "void.entropy.tithe",
    # ==========================================================================
    # Status / Health
    # ==========================================================================
    "status": "self.status.manifest",
    "health": "self.status.full",
    # ==========================================================================
    # Time / Traces
    # ==========================================================================
    "trace": "time.trace.witness",
    "history": "time.past.manifest",
}

# Contexts that cannot be shadowed
RESERVED_NAMES = frozenset({"world", "self", "concept", "void", "time"})


# =============================================================================
# Shortcut Resolution
# =============================================================================


@dataclass
class ShortcutResolution:
    """Result of resolving a shortcut."""

    original: str
    expanded: str
    source: str  # "standard", "user", "none"
    is_shortcut: bool

    @classmethod
    def not_shortcut(cls, path: str) -> "ShortcutResolution":
        """Create a resolution for a non-shortcut path."""
        return cls(original=path, expanded=path, source="none", is_shortcut=False)


@dataclass
class ShortcutRegistry:
    """
    Registry for CLI shortcuts.

    Manages both standard shortcuts and user-defined shortcuts.
    Handles resolution with proper priority:
        1. User shortcuts (from .kgents/shortcuts.yaml)
        2. Standard shortcuts
        3. Not a shortcut (return original)
    """

    standard: dict[str, str] = field(default_factory=lambda: STANDARD_SHORTCUTS.copy())
    user: dict[str, str] = field(default_factory=dict)
    _shortcuts_path: Path | None = None

    def load_user_shortcuts(self, path: Path | None = None) -> None:
        """
        Load user shortcuts from .kgents/shortcuts.yaml.

        Args:
            path: Path to shortcuts file (default: .kgents/shortcuts.yaml)
        """
        if path is None:
            path = Path.cwd() / ".kgents" / "shortcuts.yaml"

        self._shortcuts_path = path

        if not path.exists():
            return

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}

            shortcuts = data.get("shortcuts", {})
            for name, target in shortcuts.items():
                if name in RESERVED_NAMES:
                    continue  # Skip reserved names silently
                self.user[name] = target
        except Exception:
            pass  # Graceful degradation

    def save_user_shortcuts(self, path: Path | None = None) -> None:
        """
        Save user shortcuts to .kgents/shortcuts.yaml.

        Args:
            path: Path to shortcuts file (default: stored path or .kgents/shortcuts.yaml)
        """
        if path is None:
            path = self._shortcuts_path or Path.cwd() / ".kgents" / "shortcuts.yaml"

        path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(path, "w") as f:
                yaml.safe_dump({"shortcuts": self.user}, f, default_flow_style=False)
        except Exception:
            pass  # Graceful degradation

    def resolve(self, input_path: str) -> ShortcutResolution:
        """
        Resolve a shortcut to its full AGENTESE path.

        Args:
            input_path: Input path (may start with / for shortcut)

        Returns:
            ShortcutResolution with expansion details
        """
        # Not a shortcut if doesn't start with /
        if not input_path.startswith("/"):
            return ShortcutResolution.not_shortcut(input_path)

        # Extract shortcut name and any suffix
        shortcut_path = input_path[1:]  # Remove leading /
        parts = shortcut_path.split(".", 1)
        name = parts[0]
        suffix = parts[1] if len(parts) > 1 else None

        # Try user shortcuts first
        if name in self.user:
            base = self.user[name]
            expanded = f"{base}.{suffix}" if suffix else base
            return ShortcutResolution(
                original=input_path,
                expanded=expanded,
                source="user",
                is_shortcut=True,
            )

        # Try standard shortcuts
        if name in self.standard:
            base = self.standard[name]
            # If suffix provided, replace the aspect
            if suffix:
                # Get base path without aspect
                base_parts = base.rsplit(".", 1)
                if len(base_parts) == 2:
                    base = f"{base_parts[0]}.{suffix}"
                else:
                    base = f"{base}.{suffix}"
            return ShortcutResolution(
                original=input_path,
                expanded=base,
                source="standard",
                is_shortcut=True,
            )

        # Not a known shortcut
        return ShortcutResolution.not_shortcut(input_path)

    def add(self, name: str, target: str) -> bool:
        """
        Add a user shortcut.

        Args:
            name: Shortcut name (without /)
            target: Target AGENTESE path

        Returns:
            True if added, False if reserved name
        """
        if name in RESERVED_NAMES:
            return False
        self.user[name] = target
        return True

    def remove(self, name: str) -> bool:
        """
        Remove a user shortcut.

        Args:
            name: Shortcut name (without /)

        Returns:
            True if removed, False if not found
        """
        if name in self.user:
            del self.user[name]
            return True
        return False

    def list_all(self) -> dict[str, tuple[str, str]]:
        """
        List all shortcuts with their sources.

        Returns:
            Dict mapping name -> (target, source)
        """
        result: dict[str, tuple[str, str]] = {}

        # Add standard shortcuts
        for name, target in self.standard.items():
            result[name] = (target, "standard")

        # User shortcuts override standard
        for name, target in self.user.items():
            result[name] = (target, "user")

        return result


# =============================================================================
# Module-Level Functions
# =============================================================================

# Global registry instance (lazy-initialized)
_registry: ShortcutRegistry | None = None


def get_shortcut_registry() -> ShortcutRegistry:
    """Get the global shortcut registry, initializing if needed."""
    global _registry
    if _registry is None:
        _registry = ShortcutRegistry()
        _registry.load_user_shortcuts()
    return _registry


def resolve_shortcut(path: str) -> ShortcutResolution:
    """
    Resolve a shortcut to its full AGENTESE path.

    Args:
        path: Input path (may start with / for shortcut)

    Returns:
        ShortcutResolution with expansion details
    """
    return get_shortcut_registry().resolve(path)


def is_shortcut(path: str) -> bool:
    """Check if a path is a shortcut (starts with /)."""
    return path.startswith("/")


def expand_shortcut(path: str) -> str:
    """
    Expand a shortcut to its full AGENTESE path.

    If not a shortcut, returns the original path unchanged.

    Args:
        path: Input path (may start with / for shortcut)

    Returns:
        Expanded AGENTESE path
    """
    return resolve_shortcut(path).expanded


# =============================================================================
# CLI Handler for Shortcut Management
# =============================================================================


def cmd_shortcut(args: list[str], ctx: Any = None) -> int:
    """
    Shortcut management command.

    Usage:
        kg shortcut                  # List all shortcuts
        kg shortcut list             # List all shortcuts
        kg shortcut add <name> <path> # Add user shortcut
        kg shortcut remove <name>    # Remove user shortcut
        kg shortcut show <name>      # Show shortcut expansion
    """
    registry = get_shortcut_registry()

    if not args or args[0] == "list":
        # List all shortcuts
        shortcuts = registry.list_all()
        if not shortcuts:
            print("No shortcuts defined.")
            return 0

        print("Shortcuts:")
        print()

        # Group by source
        standard = [(n, t) for n, (t, s) in shortcuts.items() if s == "standard"]
        user = [(n, t) for n, (t, s) in shortcuts.items() if s == "user"]

        if standard:
            print("  Standard:")
            for name, target in sorted(standard):
                print(f"    /{name:12s} → {target}")

        if user:
            print()
            print("  User-defined:")
            for name, target in sorted(user):
                print(f"    /{name:12s} → {target}")

        return 0

    action = args[0]

    if action == "add":
        if len(args) < 3:
            print("Usage: kg shortcut add <name> <path>")
            return 1

        name = args[1].lstrip("/")
        target = args[2]

        if registry.add(name, target):
            registry.save_user_shortcuts()
            print(f"Added shortcut: /{name} → {target}")
            return 0
        else:
            print(f"Error: '{name}' is a reserved name.")
            return 1

    if action == "remove":
        if len(args) < 2:
            print("Usage: kg shortcut remove <name>")
            return 1

        name = args[1].lstrip("/")

        if registry.remove(name):
            registry.save_user_shortcuts()
            print(f"Removed shortcut: /{name}")
            return 0
        else:
            print(f"Error: Shortcut '/{name}' not found.")
            return 1

    if action == "show":
        if len(args) < 2:
            print("Usage: kg shortcut show <name>")
            return 1

        path = args[1]
        if not path.startswith("/"):
            path = "/" + path

        result = registry.resolve(path)
        if result.is_shortcut:
            print(f"{result.original} → {result.expanded} ({result.source})")
        else:
            print(f"{path} is not a shortcut")

        return 0

    print(f"Unknown action: {action}")
    print("Usage: kg shortcut [list|add|remove|show]")
    return 1
