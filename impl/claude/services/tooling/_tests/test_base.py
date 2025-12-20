"""
Tests for Tool Base Types and Category Laws.

Verifies:
- Identity Law: Id >> f == f == f >> Id
- Associativity Law: (f >> g) >> h == f >> (g >> h)
- Tool composition via >> operator
- ToolPipeline execution

Test Types (from test-patterns.md):
- Type I: Unit tests for pure functions
- Type II: Property-based tests for category laws
"""

from __future__ import annotations

import pytest

from services.tooling.base import (
    IdentityTool,
    Tool,
    ToolCategory,
    ToolEffect,
    ToolPipeline,
)

# =============================================================================
# Test Tools (Fixtures)
# =============================================================================


class AddOneTool(Tool[int, int]):
    """Adds 1 to input."""

    @property
    def name(self) -> str:
        return "test.add_one"

    @property
    def description(self) -> str:
        return "Adds 1 to input"

    async def invoke(self, request: int) -> int:
        return request + 1


class MultiplyTwoTool(Tool[int, int]):
    """Multiplies input by 2."""

    @property
    def name(self) -> str:
        return "test.multiply_two"

    @property
    def description(self) -> str:
        return "Multiplies input by 2"

    async def invoke(self, request: int) -> int:
        return request * 2


class SquareTool(Tool[int, int]):
    """Squares input."""

    @property
    def name(self) -> str:
        return "test.square"

    @property
    def description(self) -> str:
        return "Squares input"

    async def invoke(self, request: int) -> int:
        return request * request


class StringifyTool(Tool[int, str]):
    """Converts int to string."""

    @property
    def name(self) -> str:
        return "test.stringify"

    async def invoke(self, request: int) -> str:
        return str(request)


# =============================================================================
# Identity Law Tests
# =============================================================================


class TestIdentityLaw:
    """
    Category Law: Id >> f == f == f >> Id

    The identity morphism composed with any function equals that function.
    """

    @pytest.mark.asyncio
    async def test_left_identity(self) -> None:
        """Id >> f == f"""
        f = AddOneTool()
        id_tool = IdentityTool[int]()

        # Id >> f
        left_composed = id_tool >> f
        left_result = await left_composed.invoke(5)

        # f alone
        direct_result = await f.invoke(5)

        assert left_result == direct_result == 6

    @pytest.mark.asyncio
    async def test_right_identity(self) -> None:
        """f >> Id == f"""
        f = AddOneTool()
        id_tool = IdentityTool[int]()

        # f >> Id
        right_composed = f >> id_tool
        right_result = await right_composed.invoke(5)

        # f alone
        direct_result = await f.invoke(5)

        assert right_result == direct_result == 6

    @pytest.mark.asyncio
    async def test_identity_passthrough(self) -> None:
        """Identity returns input unchanged."""
        id_tool = IdentityTool[int]()
        assert await id_tool.invoke(42) == 42

        id_str = IdentityTool[str]()
        assert await id_str.invoke("hello") == "hello"


# =============================================================================
# Associativity Law Tests
# =============================================================================


class TestAssociativityLaw:
    """
    Category Law: (f >> g) >> h == f >> (g >> h)

    Composition is associative - grouping doesn't affect result.
    """

    @pytest.mark.asyncio
    async def test_associativity_three_tools(self) -> None:
        """(f >> g) >> h == f >> (g >> h)"""
        f = AddOneTool()  # x + 1
        g = MultiplyTwoTool()  # x * 2
        h = SquareTool()  # x^2

        # (f >> g) >> h: ((5 + 1) * 2)^2 = 144
        left_grouped = (f >> g) >> h
        left_result = await left_grouped.invoke(5)

        # f >> (g >> h): ((5 + 1) * 2)^2 = 144
        right_grouped = f >> (g >> h)
        right_result = await right_grouped.invoke(5)

        assert left_result == right_result == 144

    @pytest.mark.asyncio
    async def test_associativity_varied_input(self) -> None:
        """Associativity holds for various inputs."""
        f = AddOneTool()
        g = MultiplyTwoTool()
        h = SquareTool()

        for n in [0, 1, 3, 10, -5]:
            left = await ((f >> g) >> h).invoke(n)
            right = await (f >> (g >> h)).invoke(n)
            assert left == right, f"Failed for input {n}"


# =============================================================================
# Composition Tests
# =============================================================================


class TestToolComposition:
    """Tests for tool composition via >> operator."""

    @pytest.mark.asyncio
    async def test_simple_composition(self) -> None:
        """Two tools compose correctly."""
        add = AddOneTool()
        mult = MultiplyTwoTool()

        pipeline = add >> mult
        result = await pipeline.invoke(5)

        # (5 + 1) * 2 = 12
        assert result == 12

    @pytest.mark.asyncio
    async def test_type_changing_composition(self) -> None:
        """Tools with different types compose correctly."""
        add = AddOneTool()
        stringify = StringifyTool()

        pipeline = add >> stringify
        result = await pipeline.invoke(5)

        assert result == "6"
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_pipeline_name(self) -> None:
        """Pipeline name reflects composition."""
        add = AddOneTool()
        mult = MultiplyTwoTool()
        square = SquareTool()

        pipeline = add >> mult >> square
        assert pipeline.name == "test.add_one >> test.multiply_two >> test.square"

    @pytest.mark.asyncio
    async def test_pipeline_category(self) -> None:
        """Pipeline has ORCHESTRATION category."""
        add = AddOneTool()
        mult = MultiplyTwoTool()

        pipeline = add >> mult
        assert pipeline.category == ToolCategory.ORCHESTRATION

    @pytest.mark.asyncio
    async def test_pipeline_effects_union(self) -> None:
        """Pipeline effects are union of step effects."""

        class ReadingTool(Tool[int, int]):
            @property
            def name(self) -> str:
                return "reader"

            @property
            def effects(self) -> list[tuple[ToolEffect, str]]:
                return [ToolEffect.reads("filesystem")]

            async def invoke(self, request: int) -> int:
                return request

        class WritingTool(Tool[int, int]):
            @property
            def name(self) -> str:
                return "writer"

            @property
            def effects(self) -> list[tuple[ToolEffect, str]]:
                return [ToolEffect.writes("filesystem")]

            async def invoke(self, request: int) -> int:
                return request

        pipeline = ReadingTool() >> WritingTool()
        effects = pipeline.effects

        assert len(effects) == 2
        assert (ToolEffect.READS, "filesystem") in effects
        assert (ToolEffect.WRITES, "filesystem") in effects

    @pytest.mark.asyncio
    async def test_pipeline_trust_required(self) -> None:
        """Pipeline trust is maximum of step trusts."""

        class LowTrustTool(Tool[int, int]):
            @property
            def name(self) -> str:
                return "low"

            @property
            def trust_required(self) -> int:
                return 0

            async def invoke(self, request: int) -> int:
                return request

        class HighTrustTool(Tool[int, int]):
            @property
            def name(self) -> str:
                return "high"

            @property
            def trust_required(self) -> int:
                return 3

            async def invoke(self, request: int) -> int:
                return request

        pipeline = LowTrustTool() >> HighTrustTool()
        assert pipeline.trust_required == 3


# =============================================================================
# Tool Properties Tests
# =============================================================================


class TestToolProperties:
    """Tests for tool property defaults and overrides."""

    def test_default_category(self) -> None:
        """Default category is CORE."""
        assert AddOneTool().category == ToolCategory.CORE

    def test_default_trust(self) -> None:
        """Default trust is 0 (READ_ONLY)."""
        assert AddOneTool().trust_required == 0

    def test_default_timeout(self) -> None:
        """Default timeout is 2 minutes."""
        assert AddOneTool().timeout_default_ms == 120_000

    def test_default_cacheable(self) -> None:
        """Default cacheable is False."""
        assert AddOneTool().cacheable is False

    def test_default_streaming(self) -> None:
        """Default streaming is False."""
        assert AddOneTool().streaming is False

    def test_repr(self) -> None:
        """Tool has informative repr."""
        assert repr(AddOneTool()) == "Tool(test.add_one)"


# =============================================================================
# ToolEffect Tests
# =============================================================================


class TestToolEffect:
    """Tests for ToolEffect helpers."""

    def test_reads_helper(self) -> None:
        """READS helper creates correct tuple."""
        effect = ToolEffect.reads("filesystem")
        assert effect == (ToolEffect.READS, "filesystem")

    def test_writes_helper(self) -> None:
        """WRITES helper creates correct tuple."""
        effect = ToolEffect.writes("filesystem")
        assert effect == (ToolEffect.WRITES, "filesystem")

    def test_calls_helper(self) -> None:
        """CALLS helper creates correct tuple."""
        effect = ToolEffect.calls("shell")
        assert effect == (ToolEffect.CALLS, "shell")
