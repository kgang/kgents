"""
Tests for ToolRegistry.

Verifies:
- Tool registration and lookup
- Duplicate detection
- Trust-gated discovery
- Category filtering
"""

from __future__ import annotations

import pytest

from services.tooling.base import Tool, ToolCategory, ToolEffect
from services.tooling.registry import (
    DuplicateToolError,
    ToolMeta,
    ToolNotFoundError,
    ToolRegistry,
    get_registry,
    reset_registry,
)

# =============================================================================
# Fixtures
# =============================================================================


class MockReadTool(Tool[str, str]):
    """Mock read-only tool."""

    @property
    def name(self) -> str:
        return "file.read"

    @property
    def description(self) -> str:
        return "Read a file"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CORE

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.reads("filesystem")]

    @property
    def trust_required(self) -> int:
        return 0  # L0

    async def invoke(self, request: str) -> str:
        return f"content of {request}"


class MockWriteTool(Tool[str, bool]):
    """Mock write tool requiring L2."""

    @property
    def name(self) -> str:
        return "file.write"

    @property
    def description(self) -> str:
        return "Write to a file"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.CORE

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.writes("filesystem")]

    @property
    def trust_required(self) -> int:
        return 2  # L2

    async def invoke(self, request: str) -> bool:
        return True


class MockBashTool(Tool[str, str]):
    """Mock bash tool requiring L3."""

    @property
    def name(self) -> str:
        return "system.bash"

    @property
    def description(self) -> str:
        return "Execute bash command"

    @property
    def category(self) -> ToolCategory:
        return ToolCategory.SYSTEM

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.calls("shell")]

    @property
    def trust_required(self) -> int:
        return 3  # L3

    async def invoke(self, request: str) -> str:
        return f"executed: {request}"


@pytest.fixture
def registry() -> ToolRegistry:
    """Fresh registry for each test."""
    return ToolRegistry()


@pytest.fixture
def populated_registry(registry: ToolRegistry) -> ToolRegistry:
    """Registry with sample tools."""
    registry.register(MockReadTool())
    registry.register(MockWriteTool())
    registry.register(MockBashTool())
    return registry


# =============================================================================
# Registration Tests
# =============================================================================


class TestRegistration:
    """Tests for tool registration."""

    def test_register_tool(self, registry: ToolRegistry) -> None:
        """Can register a tool."""
        tool = MockReadTool()
        registry.register(tool)

        assert registry.has("file.read")

    def test_register_duplicate_raises(self, registry: ToolRegistry) -> None:
        """Registering duplicate name raises."""
        registry.register(MockReadTool())

        with pytest.raises(DuplicateToolError) as exc:
            registry.register(MockReadTool())

        assert exc.value.name == "file.read"

    def test_get_returns_tool(self, registry: ToolRegistry) -> None:
        """Get returns registered tool."""
        tool = MockReadTool()
        registry.register(tool)

        retrieved = registry.get("file.read")
        assert retrieved is tool

    def test_get_returns_none_for_missing(self, registry: ToolRegistry) -> None:
        """Get returns None for unregistered tool."""
        assert registry.get("nonexistent") is None

    def test_get_or_raise_returns_tool(self, registry: ToolRegistry) -> None:
        """get_or_raise returns registered tool."""
        tool = MockReadTool()
        registry.register(tool)

        retrieved = registry.get_or_raise("file.read")
        assert retrieved is tool

    def test_get_or_raise_raises_for_missing(self, registry: ToolRegistry) -> None:
        """get_or_raise raises for unregistered tool."""
        with pytest.raises(ToolNotFoundError) as exc:
            registry.get_or_raise("nonexistent")

        assert exc.value.name == "nonexistent"


# =============================================================================
# Metadata Tests
# =============================================================================


class TestToolMeta:
    """Tests for tool metadata."""

    def test_from_tool(self) -> None:
        """ToolMeta.from_tool captures all properties."""
        tool = MockReadTool()
        meta = ToolMeta.from_tool(tool)

        assert meta.name == "file.read"
        assert meta.description == "Read a file"
        assert meta.category == ToolCategory.CORE
        assert meta.trust_required == 0
        assert (ToolEffect.READS, "filesystem") in meta.effects

    def test_get_meta(self, registry: ToolRegistry) -> None:
        """Registry stores and returns metadata."""
        registry.register(MockReadTool())

        meta = registry.get_meta("file.read")
        assert meta is not None
        assert meta.name == "file.read"


# =============================================================================
# Discovery Tests
# =============================================================================


class TestDiscovery:
    """Tests for tool discovery."""

    def test_list_all(self, populated_registry: ToolRegistry) -> None:
        """list_all returns all tools."""
        tools = populated_registry.list_all()
        assert len(tools) == 3
        names = {t.name for t in tools}
        assert names == {"file.read", "file.write", "system.bash"}

    def test_list_by_trust_l0(self, populated_registry: ToolRegistry) -> None:
        """L0 observer sees only L0 tools."""
        tools = populated_registry.list_by_trust(0)
        assert len(tools) == 1
        assert tools[0].name == "file.read"

    def test_list_by_trust_l2(self, populated_registry: ToolRegistry) -> None:
        """L2 observer sees L0 and L2 tools."""
        tools = populated_registry.list_by_trust(2)
        assert len(tools) == 2
        names = {t.name for t in tools}
        assert names == {"file.read", "file.write"}

    def test_list_by_trust_l3(self, populated_registry: ToolRegistry) -> None:
        """L3 observer sees all tools."""
        tools = populated_registry.list_by_trust(3)
        assert len(tools) == 3

    def test_list_by_category_core(self, populated_registry: ToolRegistry) -> None:
        """Can filter by CORE category."""
        tools = populated_registry.list_by_category(ToolCategory.CORE)
        assert len(tools) == 2
        names = {t.name for t in tools}
        assert names == {"file.read", "file.write"}

    def test_list_by_category_system(self, populated_registry: ToolRegistry) -> None:
        """Can filter by SYSTEM category."""
        tools = populated_registry.list_by_category(ToolCategory.SYSTEM)
        assert len(tools) == 1
        assert tools[0].name == "system.bash"

    def test_list_by_effect_reads(self, populated_registry: ToolRegistry) -> None:
        """Can filter by READS effect."""
        tools = populated_registry.list_by_effect(ToolEffect.READS)
        assert len(tools) == 1
        assert tools[0].name == "file.read"

    def test_list_by_effect_writes(self, populated_registry: ToolRegistry) -> None:
        """Can filter by WRITES effect."""
        tools = populated_registry.list_by_effect(ToolEffect.WRITES)
        assert len(tools) == 1
        assert tools[0].name == "file.write"


# =============================================================================
# Stats and Clear Tests
# =============================================================================


class TestStatsAndClear:
    """Tests for stats and clear operations."""

    def test_stats(self, populated_registry: ToolRegistry) -> None:
        """Stats returns correct counts."""
        stats = populated_registry.stats()

        assert stats["total_tools"] == 3
        assert stats["core_tools"] == 2
        assert stats["system_tools"] == 1
        assert stats["wrapper_tools"] == 0
        assert stats["orchestration_tools"] == 0

    def test_clear(self, populated_registry: ToolRegistry) -> None:
        """Clear removes all tools."""
        populated_registry.clear()

        assert len(populated_registry.list_all()) == 0
        assert populated_registry.get("file.read") is None


# =============================================================================
# Singleton Tests
# =============================================================================


class TestSingleton:
    """Tests for singleton access pattern."""

    def test_get_registry_returns_singleton(self) -> None:
        """get_registry returns same instance."""
        reset_registry()

        r1 = get_registry()
        r2 = get_registry()

        assert r1 is r2

    def test_reset_registry_clears(self) -> None:
        """reset_registry creates new instance."""
        reset_registry()

        r1 = get_registry()
        r1.register(MockReadTool())

        reset_registry()

        r2 = get_registry()
        assert r2.get("file.read") is None
