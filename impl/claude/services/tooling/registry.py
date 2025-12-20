"""
Tool Registry: Central Registry for U-gent Tool Infrastructure.

The ToolRegistry provides:
- Tool registration with metadata
- Trust-gated discovery (tools filtered by observer's trust level)
- Category-based filtering
- Singleton access pattern

Pattern (from crown-jewel-patterns.md):
- Pattern 2: Enum Property Pattern (ToolCategory, ToolEffect)
- Pattern 15: No Hollow Services (get_registry for singleton access)

See: spec/services/tooling.md §4
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

from .base import Tool, ToolCategory, ToolEffect

if TYPE_CHECKING:
    from services.witness import TrustLevel

logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================


class ToolRegistryError(Exception):
    """Base exception for registry errors."""

    pass


class DuplicateToolError(ToolRegistryError):
    """Tool with this name already registered."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Tool '{name}' already registered")
        self.name = name


class ToolNotFoundError(ToolRegistryError):
    """Tool not found in registry."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Tool '{name}' not found")
        self.name = name


# =============================================================================
# Tool Metadata
# =============================================================================


@dataclass(frozen=True)
class ToolMeta:
    """
    Metadata for a registered tool.

    This is the queryable representation of a tool's capabilities
    and constraints. Used for discovery and trust gating.
    """

    name: str  # e.g., "file.read"
    description: str  # Human-readable description
    category: ToolCategory  # CORE, WRAPPER, SYSTEM, ORCHESTRATION
    effects: tuple[tuple[ToolEffect, str], ...]  # Declared effects
    trust_required: int  # Minimum trust level (0-3)
    timeout_default_ms: int = 120_000  # Default timeout
    cacheable: bool = False  # Whether result can be cached
    streaming: bool = False  # Whether tool supports streaming

    @classmethod
    def from_tool(cls, tool: Tool[Any, Any]) -> "ToolMeta":
        """Create metadata from a tool instance."""
        return cls(
            name=tool.name,
            description=tool.description,
            category=tool.category,
            effects=tuple(tool.effects),
            trust_required=tool.trust_required,
            timeout_default_ms=tool.timeout_default_ms,
            cacheable=tool.cacheable,
            streaming=tool.streaming,
        )


# =============================================================================
# Tool Registry
# =============================================================================


class ToolRegistry:
    """
    Central registry for all tools.

    Provides:
    - Registration with duplicate detection
    - Trust-gated discovery
    - Category-based filtering
    - Stats for monitoring

    Example:
        registry = ToolRegistry()
        registry.register(ReadTool())
        registry.register(WriteTool())

        # Get tools accessible at L1 trust
        tools = registry.list_by_trust(TrustLevel.BOUNDED)

        # Get all CORE tools
        tools = registry.list_by_category(ToolCategory.CORE)
    """

    def __init__(self) -> None:
        self._tools: dict[str, Tool[Any, Any]] = {}
        self._meta: dict[str, ToolMeta] = {}

    def register(self, tool: Tool[Any, Any]) -> None:
        """
        Register a tool with the registry.

        Args:
            tool: Tool instance to register

        Raises:
            DuplicateToolError: If tool name already registered
        """
        if tool.name in self._tools:
            raise DuplicateToolError(tool.name)

        self._tools[tool.name] = tool
        self._meta[tool.name] = ToolMeta.from_tool(tool)
        logger.debug(f"Registered tool: {tool.name}")

    def get(self, name: str) -> Tool[Any, Any] | None:
        """
        Get a tool by name.

        Args:
            name: Tool name (e.g., "file.read")

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(name)

    def get_or_raise(self, name: str) -> Tool[Any, Any]:
        """
        Get a tool by name, raising if not found.

        Args:
            name: Tool name

        Returns:
            Tool instance

        Raises:
            ToolNotFoundError: If tool not found
        """
        tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(name)
        return tool

    def get_meta(self, name: str) -> ToolMeta | None:
        """Get tool metadata by name."""
        return self._meta.get(name)

    def has(self, name: str) -> bool:
        """Check if tool is registered."""
        return name in self._tools

    def list_all(self) -> list[ToolMeta]:
        """List all registered tools."""
        return list(self._meta.values())

    def list_by_trust(self, max_trust: int) -> list[ToolMeta]:
        """
        List tools accessible at a given trust level.

        Args:
            max_trust: Maximum trust level (0-3)

        Returns:
            Tools with trust_required <= max_trust
        """
        return [meta for meta in self._meta.values() if meta.trust_required <= max_trust]

    def list_by_category(self, category: ToolCategory) -> list[ToolMeta]:
        """
        List tools in a specific category.

        Args:
            category: Tool category

        Returns:
            Tools matching the category
        """
        return [meta for meta in self._meta.values() if meta.category == category]

    def list_by_effect(self, effect: ToolEffect) -> list[ToolMeta]:
        """
        List tools with a specific effect.

        Args:
            effect: Effect to filter by

        Returns:
            Tools declaring this effect
        """
        return [meta for meta in self._meta.values() if any(e[0] == effect for e in meta.effects)]

    def stats(self) -> dict[str, int]:
        """Get registry statistics."""
        return {
            "total_tools": len(self._tools),
            "core_tools": len(self.list_by_category(ToolCategory.CORE)),
            "system_tools": len(self.list_by_category(ToolCategory.SYSTEM)),
            "wrapper_tools": len(self.list_by_category(ToolCategory.WRAPPER)),
            "orchestration_tools": len(self.list_by_category(ToolCategory.ORCHESTRATION)),
        }

    def clear(self) -> None:
        """Clear all registered tools (for testing)."""
        self._tools.clear()
        self._meta.clear()


# =============================================================================
# Singleton Access
# =============================================================================

_registry: ToolRegistry | None = None


def get_registry() -> ToolRegistry:
    """
    Get the global tool registry singleton.

    Creates the registry on first access.
    """
    global _registry
    if _registry is None:
        _registry = ToolRegistry()
    return _registry


def reset_registry() -> None:
    """
    Reset the global registry (for testing).
    """
    global _registry
    if _registry is not None:
        _registry.clear()
    _registry = None


__all__ = [
    "ToolMeta",
    "ToolRegistry",
    "ToolRegistryError",
    "DuplicateToolError",
    "ToolNotFoundError",
    "get_registry",
    "reset_registry",
]
