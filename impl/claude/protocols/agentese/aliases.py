"""
AGENTESE Path Aliases

Power user shortcuts for common paths.

From spec §10:
    # Define aliases
    logos.alias("me", "self.soul")
    logos.alias("chaos", "void.entropy")

    # Use aliases
    await logos("me.challenge", observer)      # → self.soul.challenge
    await logos("chaos.sip", observer)         # → void.entropy.sip

Alias Rules:
    1. Prefix expansion only — Alias must be first segment
    2. No recursion — Aliases don't expand within aliases
    3. User-definable — Stored in .kgents/aliases.yaml
    4. Shadowing forbidden — Can't alias to context names

Persistence (.kgents/aliases.yaml):
    aliases:
      me: self.soul
      chaos: void.entropy
      brain: self.memory
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    pass

# Standard context names that cannot be shadowed
RESERVED_CONTEXTS = frozenset({"world", "self", "concept", "void", "time"})


# === Exceptions ===


class AliasError(Exception):
    """Base exception for alias errors."""

    pass


class AliasShadowError(AliasError):
    """Attempted to shadow a reserved context name."""

    def __init__(self, alias: str, context: str) -> None:
        super().__init__(f"Cannot create alias '{alias}': would shadow context '{context}'")
        self.alias = alias
        self.context = context


class AliasRecursionError(AliasError):
    """Attempted recursive alias definition."""

    def __init__(self, alias: str, target: str) -> None:
        super().__init__(f"Recursive alias detected: '{alias}' -> '{target}'")
        self.alias = alias
        self.target = target


class AliasNotFoundError(AliasError):
    """Alias not found in registry."""

    def __init__(self, alias: str) -> None:
        super().__init__(f"Alias not found: '{alias}'")
        self.alias = alias


# === Alias Registry ===


@dataclass
class AliasRegistry:
    """
    Registry for AGENTESE path aliases.

    Aliases are prefix expansions: "me" -> "self.soul"
    So "me.challenge" expands to "self.soul.challenge"

    Rules:
    - Prefix expansion only (alias must be first segment)
    - No recursion (aliases don't expand within aliases)
    - Shadowing forbidden (can't alias to context names)

    Example:
        registry = AliasRegistry()
        registry.register("me", "self.soul")

        path = registry.expand("me.challenge")
        # → "self.soul.challenge"
    """

    _aliases: dict[str, str] = field(default_factory=dict)
    _persistence_path: Path | None = None

    def register(self, alias: str, target: str) -> None:
        """
        Register a path alias.

        Args:
            alias: The alias name (single segment)
            target: The target path (e.g., "self.soul")

        Raises:
            AliasShadowError: If alias would shadow a context name
            AliasRecursionError: If alias creates recursion
        """
        # Check for shadowing
        if alias in RESERVED_CONTEXTS:
            raise AliasShadowError(alias, alias)

        # Check for recursion (target starts with an existing alias)
        first_segment = target.split(".")[0]
        if first_segment in self._aliases:
            raise AliasRecursionError(alias, target)

        # Check if alias already exists in target (self-reference)
        if target.startswith(f"{alias}.") or target == alias:
            raise AliasRecursionError(alias, target)

        self._aliases[alias] = target

    def unregister(self, alias: str) -> None:
        """
        Remove a path alias.

        Args:
            alias: The alias to remove

        Raises:
            AliasNotFoundError: If alias doesn't exist
        """
        if alias not in self._aliases:
            raise AliasNotFoundError(alias)
        del self._aliases[alias]

    def expand(self, path: str) -> str:
        """
        Expand aliases in a path.

        Only the first segment is checked for aliases.
        No recursive expansion.

        Args:
            path: The path to expand

        Returns:
            Expanded path (or original if no alias matches)

        Example:
            registry.expand("me.challenge")
            # If "me" -> "self.soul", returns "self.soul.challenge"
        """
        if not path:
            return path

        parts = path.split(".", 1)
        first_segment = parts[0]

        if first_segment in self._aliases:
            target = self._aliases[first_segment]
            if len(parts) > 1:
                return f"{target}.{parts[1]}"
            return target

        return path

    def get(self, alias: str) -> str | None:
        """Get the target for an alias, or None if not found."""
        return self._aliases.get(alias)

    def list_aliases(self) -> dict[str, str]:
        """Get all registered aliases."""
        return dict(self._aliases)

    def has_alias(self, alias: str) -> bool:
        """Check if an alias is registered."""
        return alias in self._aliases

    def clear(self) -> None:
        """Clear all aliases."""
        self._aliases.clear()

    def __len__(self) -> int:
        """Number of registered aliases."""
        return len(self._aliases)

    def __contains__(self, alias: str) -> bool:
        """Check if alias is registered."""
        return alias in self._aliases

    # === Persistence ===

    def set_persistence_path(self, path: Path | str) -> None:
        """Set the path for persistence."""
        self._persistence_path = Path(path) if isinstance(path, str) else path

    def save(self) -> None:
        """
        Save aliases to YAML file.

        File format (.kgents/aliases.yaml):
            aliases:
              me: self.soul
              chaos: void.entropy
        """
        if self._persistence_path is None:
            return

        import yaml

        # Ensure parent directory exists
        self._persistence_path.parent.mkdir(parents=True, exist_ok=True)

        data = {"aliases": self._aliases}
        with open(self._persistence_path, "w") as f:
            yaml.safe_dump(data, f, default_flow_style=False)

    def load(self) -> None:
        """
        Load aliases from YAML file.

        Silently does nothing if file doesn't exist.
        """
        if self._persistence_path is None or not self._persistence_path.exists():
            return

        import yaml

        with open(self._persistence_path) as f:
            data = yaml.safe_load(f)

        if data and "aliases" in data:
            # Clear and reload to validate all aliases
            self._aliases.clear()
            for alias, target in data["aliases"].items():
                try:
                    self.register(alias, target)
                except AliasError:
                    # Skip invalid aliases from file
                    pass


# === Standard Aliases ===


def create_standard_aliases() -> dict[str, str]:
    """
    Get standard AGENTESE aliases.

    These are power-user shortcuts for common paths.
    """
    return {
        "me": "self.soul",
        "brain": "self.memory",
        "chaos": "void.entropy",
        "serendipity": "void.serendipity",
        "gratitude": "void.gratitude",
        "history": "time.trace",
        "past": "time.past",
        "future": "time.future",
    }


# === Factory Functions ===


def create_alias_registry(
    *,
    persistence_path: Path | str | None = None,
    include_standard: bool = True,
    load_from_disk: bool = True,
) -> AliasRegistry:
    """
    Create an alias registry with optional standard aliases.

    Args:
        persistence_path: Path to .kgents/aliases.yaml for persistence
        include_standard: Include standard aliases (default True)
        load_from_disk: Load aliases from disk if file exists (default True)

    Returns:
        Configured AliasRegistry
    """
    registry = AliasRegistry()

    if persistence_path:
        registry.set_persistence_path(persistence_path)
        if load_from_disk:
            registry.load()

    if include_standard:
        for alias, target in create_standard_aliases().items():
            if alias not in registry:
                try:
                    registry.register(alias, target)
                except AliasError:
                    pass  # Skip if conflicts with loaded aliases

    return registry


def get_default_aliases_path() -> Path:
    """Get the default path for aliases.yaml."""
    return Path.home() / ".kgents" / "aliases.yaml"


# === Logos Integration ===


def add_alias_methods_to_logos(logos_cls: type) -> None:
    """
    Add alias methods to Logos class.

    This adds:
    - logos.alias(name, target): Register an alias
    - logos.unalias(name): Remove an alias
    - logos.list_aliases(): Get all aliases
    """

    def alias_method(self: Any, name: str, target: str) -> None:
        """
        Register a path alias.

        Args:
            name: Alias name (single segment)
            target: Target path (e.g., "self.soul")

        Example:
            logos.alias("me", "self.soul")
            await logos("me.challenge", observer)  # → self.soul.challenge
        """
        if self._aliases is None:
            self._aliases = AliasRegistry()
        self._aliases.register(name, target)

    def unalias_method(self: Any, name: str) -> None:
        """Remove a path alias."""
        if self._aliases is not None:
            self._aliases.unregister(name)

    def list_aliases_method(self: Any) -> dict[str, str]:
        """Get all registered aliases."""
        aliases: AliasRegistry | None = self._aliases
        if aliases is None:
            return {}
        return aliases.list_aliases()

    setattr(logos_cls, "alias", alias_method)
    setattr(logos_cls, "unalias", unalias_method)
    setattr(logos_cls, "list_aliases_as_dict", list_aliases_method)


def expand_aliases(path: str, registry: AliasRegistry | None) -> str:
    """
    Expand aliases in a path.

    Used by Logos.invoke() to expand aliases before resolution.

    Args:
        path: The path to expand
        registry: The alias registry (or None)

    Returns:
        Expanded path
    """
    if registry is None:
        return path
    return registry.expand(path)
