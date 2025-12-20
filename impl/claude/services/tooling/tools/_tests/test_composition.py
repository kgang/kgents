"""
Tests for Tool Composition: Categorical >> Operator.

Test Strategy (T-gent Type III: Property-Based):
- Verify category laws: Identity, Associativity
- Test pipeline execution semantics
- Verify trust and effect aggregation

See: docs/skills/test-patterns.md
See: spec/services/tooling.md §3 (Category Laws)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest

from services.conductor.file_guard import reset_file_guard
from services.tooling.base import IdentityTool, Tool, ToolCategory, ToolEffect
from services.tooling.contracts import GlobQuery, GrepQuery, ReadRequest
from services.tooling.registry import ToolRegistry
from services.tooling.tools import (
    GlobTool,
    GrepTool,
    ReadTool,
    register_core_tools,
)


@pytest.fixture(autouse=True)
def reset_guard() -> None:
    """Reset FileEditGuard singleton between tests."""
    reset_file_guard()


# =============================================================================
# Mock Tools for Composition Tests
# =============================================================================


@dataclass
class IncrementTool(Tool[int, int]):
    """Test tool that increments input."""

    @property
    def name(self) -> str:
        return "test.increment"

    async def invoke(self, request: int) -> int:
        return request + 1


@dataclass
class DoubleTool(Tool[int, int]):
    """Test tool that doubles input."""

    @property
    def name(self) -> str:
        return "test.double"

    async def invoke(self, request: int) -> int:
        return request * 2


@dataclass
class StringifyTool(Tool[int, str]):
    """Test tool that converts int to string."""

    @property
    def name(self) -> str:
        return "test.stringify"

    async def invoke(self, request: int) -> str:
        return f"value: {request}"


@dataclass
class HighTrustTool(Tool[Any, Any]):
    """Test tool with high trust requirement."""

    @property
    def name(self) -> str:
        return "test.high_trust"

    @property
    def trust_required(self) -> int:
        return 3  # L3 - Highest

    @property
    def effects(self) -> list[tuple[ToolEffect, str]]:
        return [ToolEffect.calls("external_service")]

    async def invoke(self, request: Any) -> Any:
        return request


# =============================================================================
# Category Law Tests
# =============================================================================


class TestCategoryLaws:
    """Verify category laws for Tool composition."""

    async def test_identity_left(self) -> None:
        """Id >> f == f (left identity)."""
        identity = IdentityTool[int]()
        increment = IncrementTool()

        # Id >> f
        pipeline = identity >> increment
        result = await pipeline.invoke(5)

        # Should equal f alone
        direct = await increment.invoke(5)

        assert result == direct == 6

    async def test_identity_right(self) -> None:
        """f >> Id == f (right identity)."""
        increment = IncrementTool()
        identity = IdentityTool[int]()

        # f >> Id
        pipeline = increment >> identity
        result = await pipeline.invoke(5)

        # Should equal f alone
        direct = await increment.invoke(5)

        assert result == direct == 6

    async def test_associativity(self) -> None:
        """(f >> g) >> h == f >> (g >> h) (associativity)."""
        f = IncrementTool()  # +1
        g = DoubleTool()  # *2
        h = IncrementTool()  # +1

        # (f >> g) >> h
        left = (f >> g) >> h
        result_left = await left.invoke(5)

        # f >> (g >> h)
        right = f >> (g >> h)
        result_right = await right.invoke(5)

        # Both should equal: ((5+1)*2)+1 = 13
        assert result_left == result_right == 13


class TestPipelineExecution:
    """Test pipeline execution semantics."""

    async def test_simple_pipeline(self) -> None:
        """Pipeline executes steps sequentially."""
        pipeline = IncrementTool() >> DoubleTool() >> IncrementTool()
        result = await pipeline.invoke(5)

        # (5+1)*2 + 1 = 13
        assert result == 13

    async def test_type_transforming_pipeline(self) -> None:
        """Pipeline can change types between steps."""
        pipeline = IncrementTool() >> StringifyTool()
        result = await pipeline.invoke(5)

        assert result == "value: 6"

    async def test_pipeline_name(self) -> None:
        """Pipeline name is composition of step names."""
        pipeline = IncrementTool() >> DoubleTool()

        assert pipeline.name == "test.increment >> test.double"

    async def test_pipeline_category(self) -> None:
        """Pipeline category is ORCHESTRATION."""
        pipeline = IncrementTool() >> DoubleTool()

        assert pipeline.category == ToolCategory.ORCHESTRATION


class TestTrustAndEffectAggregation:
    """Test trust and effect aggregation in pipelines."""

    async def test_trust_is_max(self) -> None:
        """Pipeline trust is max of step trusts."""
        low_trust = IncrementTool()  # Default L0
        high_trust = HighTrustTool()  # L3

        pipeline = low_trust >> high_trust

        assert pipeline.trust_required == 3  # Max of 0 and 3

    async def test_effects_are_union(self) -> None:
        """Pipeline effects are union of step effects."""

        @dataclass
        class ReaderTool(Tool[int, int]):
            @property
            def name(self) -> str:
                return "test.reader"

            @property
            def effects(self) -> list[tuple[ToolEffect, str]]:
                return [ToolEffect.reads("filesystem")]

            async def invoke(self, request: int) -> int:
                return request

        @dataclass
        class WriterTool(Tool[int, int]):
            @property
            def name(self) -> str:
                return "test.writer"

            @property
            def effects(self) -> list[tuple[ToolEffect, str]]:
                return [ToolEffect.writes("filesystem")]

            async def invoke(self, request: int) -> int:
                return request

        pipeline = ReaderTool() >> WriterTool()

        assert len(pipeline.effects) == 2
        effect_types = [e[0] for e in pipeline.effects]
        assert ToolEffect.READS in effect_types
        assert ToolEffect.WRITES in effect_types


class TestRegistration:
    """Test tool registration via register_core_tools."""

    def test_register_core_tools(self) -> None:
        """register_core_tools registers all 5 core tools."""
        registry = ToolRegistry()
        register_core_tools(registry)

        stats = registry.stats()
        assert stats["total_tools"] == 5
        assert stats["core_tools"] == 5

    def test_registered_tools_accessible(self) -> None:
        """Registered tools can be retrieved by name."""
        registry = ToolRegistry()
        register_core_tools(registry)

        assert registry.has("file.read")
        assert registry.has("file.write")
        assert registry.has("file.edit")
        assert registry.has("search.glob")
        assert registry.has("search.grep")

    def test_tools_have_correct_trust(self) -> None:
        """Registered tools have correct trust levels."""
        registry = ToolRegistry()
        register_core_tools(registry)

        # Read-only tools: L0
        assert registry.get_meta("file.read").trust_required == 0  # type: ignore
        assert registry.get_meta("search.glob").trust_required == 0  # type: ignore
        assert registry.get_meta("search.grep").trust_required == 0  # type: ignore

        # Write tools: L2
        assert registry.get_meta("file.write").trust_required == 2  # type: ignore
        assert registry.get_meta("file.edit").trust_required == 2  # type: ignore


class TestRealToolComposition:
    """Test composition with real tools (requires filesystem)."""

    async def test_glob_finds_files(self, tmp_path: pytest.TempPathFactory) -> None:
        """GlobTool can be used in composition."""
        (tmp_path / "test.py").write_text("# test")  # type: ignore

        tool = GlobTool()
        result = await tool.invoke(
            GlobQuery(pattern="*.py", path=str(tmp_path))  # type: ignore
        )

        assert result.count == 1

    async def test_read_then_grep_conceptual(self, tmp_path: pytest.TempPathFactory) -> None:
        """
        Demonstrate read >> grep conceptual composition.

        Note: Direct composition requires type alignment.
        In practice, tools are composed via ToolExecutor.
        """
        (tmp_path / "code.py").write_text("def foo():\n    # TODO: fix\n    pass")  # type: ignore

        # Step 1: Read file
        read_tool = ReadTool()
        content = await read_tool.invoke(
            ReadRequest(file_path=str(tmp_path / "code.py"))  # type: ignore
        )

        assert "TODO" in content.content

        # Step 2: Grep (separate invocation, same conceptual flow)
        grep_tool = GrepTool()
        matches = await grep_tool.invoke(
            GrepQuery(
                pattern="TODO",
                path=str(tmp_path),  # type: ignore
                output_mode="content",
            )
        )

        assert matches.count == 1
