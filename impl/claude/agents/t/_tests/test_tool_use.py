"""
Tests for T-gents Phase 2: Tool Use

Tests cover:
- Tool[A, B] base class
- Tool composition (categorical laws)
- ToolRegistry operations
- Tool wrappers (tracing, caching, retry)
- Type safety
"""

from dataclasses import dataclass

import pytest
from agents.t import (
    PassthroughTool,
    Tool,
    ToolError,
    ToolErrorType,
    ToolMeta,
    ToolRegistry,
)

# --- Test Fixtures ---


@dataclass
class TextInput:
    """Sample input schema."""

    text: str


@dataclass
class NumberOutput:
    """Sample output schema."""

    count: int


@dataclass
class UppercaseOutput:
    """Sample output schema."""

    text: str


# --- Test Tools ---


class CountTool(Tool[TextInput, NumberOutput]):
    """Test tool: counts characters in text."""

    meta = ToolMeta.minimal(
        name="count",
        description="Count characters",
        input_schema=TextInput,
        output_schema=NumberOutput,
    )

    async def invoke(self, input: TextInput) -> NumberOutput:
        return NumberOutput(count=len(input.text))


class UppercaseTool(Tool[TextInput, UppercaseOutput]):
    """Test tool: converts text to uppercase."""

    meta = ToolMeta.minimal(
        name="uppercase",
        description="Convert to uppercase",
        input_schema=TextInput,
        output_schema=UppercaseOutput,
    )

    async def invoke(self, input: TextInput) -> UppercaseOutput:
        return UppercaseOutput(text=input.text.upper())


class DoubleTool(Tool[NumberOutput, NumberOutput]):
    """Test tool: doubles a number."""

    meta = ToolMeta.minimal(
        name="double",
        description="Double a number",
        input_schema=NumberOutput,
        output_schema=NumberOutput,
    )

    async def invoke(self, input: NumberOutput) -> NumberOutput:
        return NumberOutput(count=input.count * 2)


class FailingCountTool(Tool[TextInput, NumberOutput]):
    """Test tool that fails N times before succeeding."""

    meta = ToolMeta.minimal(
        name="failing_count",
        description="Counts but fails N times",
        input_schema=TextInput,
        output_schema=NumberOutput,
    )

    def __init__(self, fail_count: int = 2):
        self.fail_count = fail_count
        self.invocation_count = 0

    async def invoke(self, input: TextInput) -> NumberOutput:
        self.invocation_count += 1

        if self.invocation_count <= self.fail_count:
            raise ToolError(
                error_type=ToolErrorType.NETWORK,
                message="Simulated network error",
                tool_name=self.name,
                input=input,
                recoverable=True,
            )

        return NumberOutput(count=len(input.text))


# --- Basic Tool Tests ---


@pytest.mark.asyncio
async def test_tool_basic_invocation() -> None:
    """Test basic tool invocation."""
    tool = CountTool()
    input_data = TextInput(text="hello")
    output = await tool.invoke(input_data)

    assert output.count == 5
    assert tool.name == "count"


@pytest.mark.asyncio
async def test_passthrough_tool() -> None:
    """Test identity tool (passthrough)."""
    tool = PassthroughTool[str]()
    output = await tool.invoke("test")

    assert output == "test"


# --- Composition Tests (Categorical Laws) ---


@pytest.mark.asyncio
async def test_tool_composition_sequential() -> None:
    """Test sequential composition: f >> g."""
    count_tool = CountTool()
    double_tool = DoubleTool()

    # Compose: count >> double
    pipeline = count_tool >> double_tool

    input_data = TextInput(text="hello")
    output = await pipeline.invoke(input_data)

    # "hello" → 5 → 10
    assert output.count == 10
    assert pipeline.name == "(count >> double)"


@pytest.mark.asyncio
async def test_composition_associativity() -> None:
    """
    Test categorical law: (f >> g) >> h ≡ f >> (g >> h).

    This is a fundamental category theory requirement.
    """
    count = CountTool()
    double = DoubleTool()
    double2 = DoubleTool()

    # Left association: (count >> double) >> double2
    left = (count >> double) >> double2

    # Right association: count >> (double >> double2)
    right = count >> (double >> double2)

    input_data = TextInput(text="test")

    output_left = await left.invoke(input_data)
    output_right = await right.invoke(input_data)

    # Both should produce same result: 4 → 8 → 16
    assert output_left.count == output_right.count == 16


@pytest.mark.asyncio
async def test_composition_identity() -> None:
    """
    Test categorical law: Id >> f ≡ f ≡ f >> Id.

    Identity composition should not change behavior.
    """
    count = CountTool()
    identity = PassthroughTool[TextInput]()

    # Test: Id >> f
    left_identity = identity >> count

    # Test: f >> Id (requires compatible types)
    # We can't directly compose count >> identity because types don't match
    # (NumberOutput vs TextInput), so we'll test left identity only

    input_data = TextInput(text="hello")

    output_composed = await left_identity.invoke(input_data)
    output_direct = await count.invoke(input_data)

    assert output_composed.count == output_direct.count == 5


# --- Tool Registry Tests ---


@pytest.mark.asyncio
async def test_registry_register_and_get() -> None:
    """Test tool registration and retrieval."""
    registry = ToolRegistry()
    tool = CountTool()

    # Register tool
    entry = await registry.register(tool)

    assert entry.name == "count"
    assert entry.input_schema == TextInput
    assert entry.output_schema == NumberOutput

    # Retrieve by ID
    retrieved = await registry.get(entry.id)
    assert retrieved is tool


@pytest.mark.asyncio
async def test_registry_find_by_name() -> None:
    """Test finding tools by name."""
    registry = ToolRegistry()
    tool = CountTool()

    await registry.register(tool)

    found = await registry.find_by_name("count")
    assert found is tool

    not_found = await registry.find_by_name("nonexistent")
    assert not_found is None


@pytest.mark.asyncio
async def test_registry_find_by_signature() -> None:
    """Test finding tools by type signature."""
    registry = ToolRegistry()

    count_tool = CountTool()
    uppercase_tool = UppercaseTool()

    await registry.register(count_tool)
    await registry.register(uppercase_tool)

    # Find tools: TextInput → NumberOutput
    matches = await registry.find_by_signature(TextInput, NumberOutput)
    assert len(matches) == 1
    assert matches[0] is count_tool

    # Find tools: TextInput → UppercaseOutput
    matches = await registry.find_by_signature(TextInput, UppercaseOutput)
    assert len(matches) == 1
    assert matches[0] is uppercase_tool


@pytest.mark.asyncio
async def test_registry_search() -> None:
    """Test semantic search."""
    registry = ToolRegistry()

    count_tool = CountTool()
    uppercase_tool = UppercaseTool()

    await registry.register(count_tool)
    await registry.register(uppercase_tool)

    # Search by name
    results = await registry.search("count")
    assert len(results) == 1
    assert results[0] is count_tool

    # Search by description
    results = await registry.search("uppercase")
    assert len(results) == 1
    assert results[0] is uppercase_tool


@pytest.mark.asyncio
async def test_registry_composition_path() -> None:
    """Test finding composition paths."""
    registry = ToolRegistry()

    count = CountTool()
    double = DoubleTool()

    await registry.register(count)
    await registry.register(double)

    # Find path: TextInput → NumberOutput (direct)
    path = await registry.find_composition_path(TextInput, NumberOutput)
    assert path is not None
    assert len(path) == 1
    assert path[0] is count

    # Note: We can't test multi-step paths without more tools
    # Future: Add tools with compatible intermediate types


# --- Tool Wrapper Tests ---


@pytest.mark.asyncio
async def test_traced_tool() -> None:
    """Test tool tracing wrapper."""
    tool = CountTool()
    traced = tool.with_trace()

    input_data = TextInput(text="hello")
    output = await traced.invoke(input_data)

    assert output.count == 5
    # Trace is emitted internally (would be captured by W-gent)


@pytest.mark.asyncio
async def test_cached_tool() -> None:
    """Test tool caching wrapper."""
    tool = CountTool()
    cached = tool.with_cache(ttl_seconds=60)

    input_data = TextInput(text="hello")

    # First call - cache miss
    output1 = await cached.invoke(input_data)
    assert output1.count == 5

    # Second call - cache hit
    output2 = await cached.invoke(input_data)
    assert output2.count == 5

    # Different input - cache miss
    output3 = await cached.invoke(TextInput(text="world"))
    assert output3.count == 5


@pytest.mark.asyncio
async def test_retry_tool_success() -> None:
    """Test retry wrapper with recoverable errors."""
    tool = FailingCountTool(fail_count=2)
    retry_tool = tool.with_retry(max_attempts=5)

    input_data = TextInput(text="hello")

    # Should succeed after 3 attempts (2 failures, then success)
    output = await retry_tool.invoke(input_data)
    assert output.count == 5
    assert tool.invocation_count == 3


@pytest.mark.asyncio
async def test_retry_tool_exhausted() -> None:
    """Test retry wrapper when all attempts fail."""
    tool = FailingCountTool(fail_count=10)  # Fail 10 times
    retry_tool = tool.with_retry(max_attempts=3)

    input_data = TextInput(text="hello")

    # Should fail after 3 attempts
    with pytest.raises(ToolError) as exc_info:
        await retry_tool.invoke(input_data)

    assert exc_info.value.error_type == ToolErrorType.NETWORK
    assert tool.invocation_count == 3


# --- Type Safety Tests ---


def test_tool_type_annotations() -> None:
    """Test that tools preserve type information."""
    count = CountTool()

    # Tools should have type hints
    assert count.meta.interface.input_schema == TextInput
    assert count.meta.interface.output_schema == NumberOutput


# --- Integration Tests ---


@pytest.mark.asyncio
async def test_full_pipeline() -> None:
    """Test complete tool pipeline with all features."""
    # Create registry
    registry = ToolRegistry()

    # Create tools
    count = CountTool()
    double = DoubleTool()

    # Register tools
    await registry.register(count)
    await registry.register(double)

    # Find composition path
    path = await registry.find_composition_path(TextInput, NumberOutput)
    assert path is not None

    # Create pipeline with wrappers
    pipeline = count.with_trace().with_cache(ttl_seconds=60) >> double.with_retry()

    # Execute pipeline
    input_data = TextInput(text="test")
    output = await pipeline.invoke(input_data)

    # "test" → 4 → 8
    assert output.count == 8
