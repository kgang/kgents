"""
T-gents Phase 2: Tool Registry

Tool catalog and discovery system (L-gent integration).

This module implements the Tool Registry for:
- Tool registration and versioning
- Discovery by type signature
- Composition path planning
- Semantic search

Philosophy:
- Tools form a category with types as objects
- Type signatures form a partial order (type lattice)
- Composition planning is graph search in the type lattice
- L-gents provide the catalog substrate

Integration:
- L-gents: Catalog storage and lattice operations
- D-gents: Persistence of tool metadata
- P-gents: Schema parsing for registration

References:
- spec/t-gents/tool-use.md - Section 5.2 (Layer 2: Tool Registry)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional, Type, TypeVar

from .tool import Tool, ToolMeta

# Type variables
A = TypeVar("A")
B = TypeVar("B")


# --- Tool Catalog Entry ---


@dataclass
class ToolEntry:
    """
    Catalog entry for a registered tool.

    Stored in L-gent catalog for discovery and retrieval.
    """

    id: str  # Unique tool ID
    name: str  # Tool name
    version: str  # Semantic version
    description: str  # Human-readable description

    # Type signature
    input_schema: Type[Any]
    output_schema: Type[Any]

    # MCP metadata
    server: Optional[str] = None  # MCP server address (if remote)
    tags: list[str] = field(default_factory=list)  # Searchable tags

    # Lifecycle
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    deprecated: bool = False

    # Runtime stats (updated by W-gent)
    invocation_count: int = 0
    success_rate: float = 1.0  # Success / total invocations
    avg_latency_ms: Optional[float] = None

    @classmethod
    def from_meta(cls, tool_id: str, meta: ToolMeta) -> ToolEntry:
        """Create catalog entry from tool metadata."""
        return cls(
            id=tool_id,
            name=meta.identity.name,
            version=meta.identity.version,
            description=meta.identity.description,
            input_schema=meta.interface.input_schema,
            output_schema=meta.interface.output_schema,
            server=meta.identity.server,
            tags=meta.identity.tags,
        )


# --- Tool Registry ---


class ToolRegistry:
    """
    Central registry for tool discovery and management.

    Provides:
    - Tool registration and versioning
    - Discovery by type signature
    - Composition path planning (A → C via A → B → C)
    - Semantic search by keywords/tags
    - Permission management (future)

    Integration:
    - L-gents: Type lattice and catalog storage
    - D-gents: Persistent tool metadata
    - W-gents: Runtime statistics

    Category Theory:
    - Tools form a category where:
      - Objects: Types (input/output schemas)
      - Morphisms: Tool[A, B] (typed transformations)
      - Composition: f >> g (sequential tool chains)
    - Type signatures form a partial order
    - Composition planning = path finding in type lattice

    Usage:
        registry = ToolRegistry()

        # Register tool
        await registry.register(web_search_tool)

        # Find by signature
        tools = await registry.find_by_signature(str, Summary)

        # Find composition path
        path = await registry.find_composition_path(Query, Report)
        # → [parse, search, extract, synthesize]
    """

    def __init__(self):
        # In-memory catalog (will be replaced with L-gent integration)
        self._catalog: dict[str, ToolEntry] = {}
        self._tools: dict[str, Tool] = {}  # Loaded tool instances
        self._next_id = 0

    def _generate_id(self) -> str:
        """Generate unique tool ID."""
        self._next_id += 1
        return f"tool_{self._next_id:04d}"

    async def register(self, tool: Tool) -> ToolEntry:
        """
        Register tool in catalog.

        Creates catalog entry with metadata for discovery.
        Stores tool instance for later retrieval.

        Args:
            tool: Tool instance to register

        Returns:
            ToolEntry: Catalog entry for registered tool
        """
        tool_id = self._generate_id()

        # Create catalog entry
        entry = ToolEntry.from_meta(tool_id, tool.meta)

        # Store in catalog
        self._catalog[tool_id] = entry
        self._tools[tool_id] = tool

        return entry

    async def get(self, tool_id: str) -> Optional[Tool]:
        """
        Retrieve tool by ID.

        Args:
            tool_id: Unique tool identifier

        Returns:
            Tool instance or None if not found
        """
        return self._tools.get(tool_id)

    async def find_by_name(self, name: str) -> Optional[Tool]:
        """
        Find tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None if not found
        """
        for entry in self._catalog.values():
            if entry.name == name:
                return self._tools.get(entry.id)
        return None

    async def find_by_signature(
        self,
        input_type: Type[Any],
        output_type: Type[Any],
    ) -> list[Tool]:
        """
        Find tools matching type signature.

        Searches for tools with compatible input/output types.
        Future: Will use L-gent type lattice for subtype matching.

        Args:
            input_type: Expected input type
            output_type: Expected output type

        Returns:
            List of tools matching signature (may be empty)
        """
        matching_tools: list[Tool] = []

        for entry in self._catalog.values():
            # Exact type match (future: use subtype compatibility)
            if entry.input_schema == input_type and entry.output_schema == output_type:
                tool = self._tools.get(entry.id)
                if tool:
                    matching_tools.append(tool)

        return matching_tools

    async def find_by_tags(self, tags: list[str]) -> list[Tool]:
        """
        Find tools by tags (semantic search).

        Args:
            tags: List of tags to search for

        Returns:
            List of tools matching any tag
        """
        matching_tools: list[Tool] = []

        for entry in self._catalog.values():
            # Tool matches if it has any of the search tags
            if any(tag in entry.tags for tag in tags):
                tool = self._tools.get(entry.id)
                if tool:
                    matching_tools.append(tool)

        return matching_tools

    async def search(self, query: str) -> list[Tool]:
        """
        Semantic search for tools.

        Searches tool names, descriptions, and tags.

        Args:
            query: Search query string

        Returns:
            List of matching tools (ranked by relevance)
        """
        query_lower = query.lower()
        matching_tools: list[tuple[Tool, float]] = []  # (tool, score)

        for entry in self._catalog.values():
            score = 0.0

            # Name match (highest weight)
            if query_lower in entry.name.lower():
                score += 10.0

            # Description match
            if query_lower in entry.description.lower():
                score += 5.0

            # Tag match
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 3.0

            if score > 0:
                tool = self._tools.get(entry.id)
                if tool:
                    matching_tools.append((tool, score))

        # Sort by score (descending)
        matching_tools.sort(key=lambda x: x[1], reverse=True)

        return [tool for tool, _ in matching_tools]

    async def find_composition_path(
        self,
        source_type: Type[Any],
        target_type: Type[Any],
        max_depth: int = 5,
    ) -> Optional[list[Tool]]:
        """
        Find sequence of tools composing source → target.

        Uses breadth-first search in the type lattice to find
        a chain of tools that transform source type to target type.

        This is composition planning: given A and C, find B such that
        we have tools A → B and B → C, enabling A → B → C.

        Args:
            source_type: Starting type
            target_type: Desired output type
            max_depth: Maximum composition depth

        Returns:
            List of tools forming composition path, or None if no path exists

        Example:
            # Find path from Query to Report
            path = await registry.find_composition_path(Query, Report)
            # → [parse_query, web_search, extract_facts, synthesize_report]

            # Create composed tool
            pipeline = compose(*path)
        """
        # BFS to find shortest path
        from collections import deque

        # Queue: (current_type, path_so_far)
        queue: deque[tuple[Type[Any], list[Tool]]] = deque([(source_type, [])])
        visited: set[Type[Any]] = {source_type}

        while queue:
            current_type, path = queue.popleft()

            # Check depth limit
            if len(path) >= max_depth:
                continue

            # Find tools that accept current_type
            candidate_tools = await self._find_tools_with_input(current_type)

            for tool in candidate_tools:
                output_type = tool.meta.interface.output_schema

                # Found path to target
                if output_type == target_type:
                    return path + [tool]

                # Explore further
                if output_type not in visited:
                    visited.add(output_type)
                    queue.append((output_type, path + [tool]))

        # No path found
        return None

    async def _find_tools_with_input(self, input_type: Type[Any]) -> list[Tool]:
        """Find all tools that accept given input type."""
        matching_tools: list[Tool] = []

        for entry in self._catalog.values():
            if entry.input_schema == input_type:
                tool = self._tools.get(entry.id)
                if tool:
                    matching_tools.append(tool)

        return matching_tools

    async def list_all(self) -> list[ToolEntry]:
        """
        List all registered tools.

        Returns:
            List of all tool catalog entries
        """
        return list(self._catalog.values())

    async def update_stats(
        self,
        tool_id: str,
        success: bool,
        latency_ms: float,
    ) -> None:
        """
        Update tool runtime statistics (W-gent integration).

        Args:
            tool_id: Tool identifier
            success: Whether invocation succeeded
            latency_ms: Execution latency in milliseconds
        """
        entry = self._catalog.get(tool_id)
        if not entry:
            return

        # Update invocation count
        entry.invocation_count += 1

        # Update success rate (exponential moving average)
        alpha = 0.1  # Smoothing factor
        current_success = 1.0 if success else 0.0
        entry.success_rate = alpha * current_success + (1 - alpha) * entry.success_rate

        # Update average latency (exponential moving average)
        if entry.avg_latency_ms is None:
            entry.avg_latency_ms = latency_ms
        else:
            entry.avg_latency_ms = (
                alpha * latency_ms + (1 - alpha) * entry.avg_latency_ms
            )

        entry.updated_at = datetime.now()


# --- Global Registry Instance ---

# Singleton registry instance (can be overridden for testing)
_global_registry: Optional[ToolRegistry] = None


def get_registry() -> ToolRegistry:
    """Get global tool registry instance."""
    global _global_registry
    if _global_registry is None:
        _global_registry = ToolRegistry()
    return _global_registry


def set_registry(registry: ToolRegistry) -> None:
    """Set global tool registry (for testing)."""
    global _global_registry
    _global_registry = registry


# --- Exports ---

__all__ = [
    "ToolEntry",
    "ToolRegistry",
    "get_registry",
    "set_registry",
]
