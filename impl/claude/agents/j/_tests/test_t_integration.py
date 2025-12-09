"""
Tests for J-gent + T-gent Integration: Template-Based Tool Generation.

Cross-pollination: Phase 7 (T-gents Cross-Genus Integration)

Tests cover:
1. ToolTemplate - Template definition and parameterization
2. JITToolMeta - Extended metadata for JIT-compiled tools
3. JITToolWrapper - Tool[A, B] wrapping of JIT code
4. compile_tool_from_template - Template → Tool pipeline
5. compile_tool_from_intent - Intent → Tool pipeline
6. create_tool_from_source - AgentSource → Tool pipeline
7. Built-in templates (JSON_FIELD_EXTRACTOR, TEXT_TRANSFORMER, FILTER_TEMPLATE)
8. Composition with other tools via >>
9. Error handling and edge cases
10. Security and sandboxing

All J+T tools are marked with __is_test__ = True to distinguish them
from production agents.
"""

import pytest
from typing import Any

from bootstrap.types import Agent, Result

from agents.t.tool import ToolMeta, ToolError, ToolErrorType
from agents.t.permissions import ToolCapabilities

from agents.j import (
    AgentSource,
    ArchitectConstraints,
)
from agents.j.t_integration import (
    ToolTemplate,
    JITToolMeta,
    JITToolWrapper,
    compile_tool_from_intent,
    compile_tool_from_template,
    create_tool_from_source,
    JSON_FIELD_EXTRACTOR,
    TEXT_TRANSFORMER,
    FILTER_TEMPLATE,
)
from agents.j.factory_integration import JITAgentMeta
from agents.j.sandbox import SandboxConfig

# Mark wrapper as test agent
JITToolWrapper.__is_test__ = True


# Helper to create minimal ToolMeta for tests
def make_tool_meta(name: str, description: str) -> ToolMeta:
    """Create minimal ToolMeta for testing."""
    return ToolMeta.minimal(name, description, Any, Any)


# --- Fixtures ---


@pytest.fixture
def simple_tool_source() -> AgentSource:
    """Create a simple tool AgentSource for testing."""
    return AgentSource(
        source="""
class SimpleUppercase:
    '''Convert text to uppercase.'''

    def invoke(self, text: str) -> str:
        return text.upper()
""",
        class_name="SimpleUppercase",
        imports=frozenset(),
        complexity=1,
        description="Convert text to uppercase",
    )


@pytest.fixture
def json_extractor_source() -> AgentSource:
    """Create a JSON field extractor AgentSource."""
    return AgentSource(
        source="""
class JsonFieldExtractor:
    '''Extract a field from JSON.'''

    def invoke(self, data: str) -> str:
        parsed = json.loads(data)
        return str(parsed.get("error", ""))
""",
        class_name="JsonFieldExtractor",
        imports=frozenset({"json"}),
        complexity=3,
        description="Extract error field from JSON",
    )


@pytest.fixture
def custom_template() -> ToolTemplate:
    """Create a custom tool template for testing."""
    return ToolTemplate(
        name="Custom Echo",
        description="Echo input with prefix",
        template_source="""
class CustomEcho:
    '''Echo input with prefix.'''

    def invoke(self, text: str) -> str:
        return "{prefix}" + text
""",
        parameters={"prefix": "ECHO: "},
        capabilities=ToolCapabilities(requires_network=False),
    )


# --- ToolTemplate Tests ---


class TestToolTemplate:
    """Tests for ToolTemplate dataclass."""

    def test_template_creation(self):
        """Test basic template creation."""
        template = ToolTemplate(
            name="Test Template",
            description="A test template",
            template_source="class Test: pass",
            parameters={"key": "value"},
        )

        assert template.name == "Test Template"
        assert template.description == "A test template"
        assert template.parameters == {"key": "value"}

    def test_template_with_capabilities(self):
        """Test template with custom capabilities."""
        caps = ToolCapabilities(
            requires_network=True,
            requires_internet=True,
            max_cost_usd=0.5,
        )
        template = ToolTemplate(
            name="Network Tool",
            description="Requires network",
            template_source="class Net: pass",
            capabilities=caps,
        )

        assert template.capabilities.requires_network is True
        assert template.capabilities.requires_internet is True

    def test_template_immutability(self):
        """Test that template is frozen (immutable)."""
        template = ToolTemplate(
            name="Frozen",
            description="Test",
            template_source="pass",
        )

        # Should raise FrozenInstanceError
        with pytest.raises(Exception):  # dataclasses.FrozenInstanceError
            template.name = "Changed"


# --- JITToolMeta Tests ---


class TestJITToolMeta:
    """Tests for JITToolMeta dataclass."""

    def test_jit_tool_meta_creation(self, simple_tool_source: AgentSource):
        """Test basic JITToolMeta creation."""
        jit_meta = JITAgentMeta(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            stability_score=0.9,
            sandbox_config=SandboxConfig(),
        )
        tool_meta = make_tool_meta("test_tool", "Test tool")

        meta = JITToolMeta(
            jit_meta=jit_meta,
            tool_meta=tool_meta,
        )

        assert meta.jit_meta == jit_meta
        assert meta.tool_meta == tool_meta
        assert meta.template is None

    def test_jit_tool_meta_with_template(
        self, simple_tool_source: AgentSource, custom_template: ToolTemplate
    ):
        """Test JITToolMeta with template reference."""
        jit_meta = JITAgentMeta(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            stability_score=1.0,
            sandbox_config=SandboxConfig(),
        )
        tool_meta = make_tool_meta("template_tool", "From template")

        meta = JITToolMeta(
            jit_meta=jit_meta,
            tool_meta=tool_meta,
            template=custom_template,
        )

        assert meta.template == custom_template
        assert meta.template.name == "Custom Echo"


# --- JITToolWrapper Tests ---


class TestJITToolWrapper:
    """Tests for JITToolWrapper class."""

    @pytest.mark.asyncio
    async def test_wrapper_creation(self, simple_tool_source: AgentSource):
        """Test basic wrapper creation."""
        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("simple", "Simple tool"),
        )

        assert isinstance(tool, JITToolWrapper)
        assert tool.name == "simple"

    @pytest.mark.asyncio
    async def test_wrapper_invoke_success(self, simple_tool_source: AgentSource):
        """Test wrapper invocation returns Result.Ok on success."""
        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("simple", "Simple tool"),
        )

        result = await tool.invoke("hello")

        assert result.is_ok()
        assert result.unwrap() == "HELLO"

    @pytest.mark.asyncio
    async def test_wrapper_invoke_error(self):
        """Test wrapper invocation returns Result.Err on failure."""
        # Source that will fail
        source = AgentSource(
            source="""
class FailingTool:
    def invoke(self, x: str) -> str:
        raise ValueError("Intentional failure")
""",
            class_name="FailingTool",
            imports=frozenset(),
            complexity=2,
            description="Always fails",
        )

        tool = await create_tool_from_source(
            source=source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("failing", "Failing tool"),
        )

        result = await tool.invoke("test")

        assert result.is_err()
        error = result.error  # Access error directly on Err
        assert isinstance(error, ToolError)
        assert error.error_type == ToolErrorType.FATAL

    @pytest.mark.asyncio
    async def test_wrapper_meta_property(self, simple_tool_source: AgentSource):
        """Test wrapper meta property."""
        tool_meta = make_tool_meta("test", "Test description")
        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=tool_meta,
        )

        assert tool.meta == tool_meta
        assert tool.meta.identity.name == "test"

    @pytest.mark.asyncio
    async def test_wrapper_jit_tool_meta_property(
        self, simple_tool_source: AgentSource
    ):
        """Test wrapper jit_tool_meta property."""
        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("test", "Test"),
        )

        jit_meta = tool.jit_tool_meta
        assert isinstance(jit_meta, JITToolMeta)
        assert jit_meta.jit_meta.source == simple_tool_source


# --- create_tool_from_source Tests ---


class TestCreateToolFromSource:
    """Tests for create_tool_from_source function."""

    @pytest.mark.asyncio
    async def test_basic_creation(self, simple_tool_source: AgentSource):
        """Test basic tool creation from source."""
        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("basic", "Basic tool"),
        )

        assert isinstance(tool, JITToolWrapper)
        assert tool.name == "basic"

    @pytest.mark.asyncio
    async def test_creation_with_custom_sandbox(self, simple_tool_source: AgentSource):
        """Test tool creation with custom sandbox config."""
        custom_config = SandboxConfig(
            timeout_seconds=5.0,
            type_check=False,
        )

        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("custom", "Custom sandbox"),
            sandbox_config=custom_config,
        )

        assert tool.jit_tool_meta.jit_meta.sandbox_config == custom_config

    @pytest.mark.asyncio
    async def test_stability_score_computed(self, simple_tool_source: AgentSource):
        """Test that stability score is computed."""
        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("stable", "Stable tool"),
        )

        score = tool.jit_tool_meta.jit_meta.stability_score
        assert 0.0 <= score <= 1.0
        # Simple tool should be stable
        assert score > 0.5


# --- compile_tool_from_template Tests ---


class TestCompileToolFromTemplate:
    """Tests for compile_tool_from_template function."""

    @pytest.mark.asyncio
    async def test_basic_template_compilation(self, custom_template: ToolTemplate):
        """Test basic template compilation."""
        tool = await compile_tool_from_template(custom_template)

        assert isinstance(tool, JITToolWrapper)
        assert tool.jit_tool_meta.template == custom_template

    @pytest.mark.asyncio
    async def test_template_with_parameters(self, custom_template: ToolTemplate):
        """Test template compilation with custom parameters."""
        tool = await compile_tool_from_template(
            custom_template,
            parameters={"prefix": "CUSTOM: "},
        )

        result = await tool.invoke("test")
        assert result.is_ok()
        assert result.unwrap() == "CUSTOM: test"

    @pytest.mark.asyncio
    async def test_template_default_parameters(self, custom_template: ToolTemplate):
        """Test template uses default parameters."""
        tool = await compile_tool_from_template(custom_template)

        result = await tool.invoke("hello")
        assert result.is_ok()
        assert result.unwrap() == "ECHO: hello"

    @pytest.mark.asyncio
    async def test_json_field_extractor_template(self):
        """Test built-in JSON_FIELD_EXTRACTOR template."""
        tool = await compile_tool_from_template(JSON_FIELD_EXTRACTOR)

        result = await tool.invoke('{"error": "Something went wrong"}')
        assert result.is_ok()
        assert result.unwrap() == "Something went wrong"

    @pytest.mark.asyncio
    async def test_json_field_extractor_custom_field(self):
        """Test JSON_FIELD_EXTRACTOR with custom field."""
        tool = await compile_tool_from_template(
            JSON_FIELD_EXTRACTOR,
            parameters={"field": "message"},
        )

        result = await tool.invoke('{"message": "Hello", "error": "Ignored"}')
        assert result.is_ok()
        assert result.unwrap() == "Hello"

    @pytest.mark.asyncio
    async def test_json_field_extractor_missing_field(self):
        """Test JSON_FIELD_EXTRACTOR with missing field returns empty."""
        tool = await compile_tool_from_template(JSON_FIELD_EXTRACTOR)

        result = await tool.invoke('{"other": "value"}')
        assert result.is_ok()
        assert result.unwrap() == ""

    @pytest.mark.asyncio
    async def test_json_field_extractor_invalid_json(self):
        """Test JSON_FIELD_EXTRACTOR with invalid JSON."""
        tool = await compile_tool_from_template(JSON_FIELD_EXTRACTOR)

        result = await tool.invoke("not valid json")
        assert result.is_ok()
        assert result.unwrap() == ""  # Returns empty on error

    @pytest.mark.asyncio
    async def test_text_transformer_template(self):
        """Test built-in TEXT_TRANSFORMER template."""
        tool = await compile_tool_from_template(TEXT_TRANSFORMER)

        result = await tool.invoke("hello world")
        assert result.is_ok()
        assert result.unwrap() == "HELLO WORLD"

    @pytest.mark.asyncio
    async def test_text_transformer_custom_method(self):
        """Test TEXT_TRANSFORMER with custom method."""
        tool = await compile_tool_from_template(
            TEXT_TRANSFORMER,
            parameters={
                "transform_method": "lower",
                "transform_description": "Convert to lowercase",
            },
        )

        result = await tool.invoke("HELLO WORLD")
        assert result.is_ok()
        assert result.unwrap() == "hello world"

    @pytest.mark.asyncio
    async def test_text_transformer_strip(self):
        """Test TEXT_TRANSFORMER with strip method."""
        tool = await compile_tool_from_template(
            TEXT_TRANSFORMER,
            parameters={
                "transform_method": "strip",
                "transform_description": "Remove whitespace",
            },
        )

        result = await tool.invoke("  hello  ")
        assert result.is_ok()
        assert result.unwrap() == "hello"

    @pytest.mark.asyncio
    async def test_filter_template(self):
        """Test built-in FILTER_TEMPLATE."""
        tool = await compile_tool_from_template(FILTER_TEMPLATE)

        result = await tool.invoke([-1, 0, 1, 2, 3])
        assert result.is_ok()
        assert result.unwrap() == [1, 2, 3]

    @pytest.mark.asyncio
    async def test_filter_template_custom_condition(self):
        """Test FILTER_TEMPLATE with custom condition."""
        tool = await compile_tool_from_template(
            FILTER_TEMPLATE,
            parameters={
                "condition": "item is even",
                "condition_code": "item % 2 == 0",
            },
        )

        result = await tool.invoke([1, 2, 3, 4, 5, 6])
        assert result.is_ok()
        assert result.unwrap() == [2, 4, 6]


# --- compile_tool_from_intent Tests ---


class TestCompileToolFromIntent:
    """Tests for compile_tool_from_intent function."""

    @pytest.mark.asyncio
    async def test_basic_intent_compilation(self):
        """Test basic tool compilation from intent."""
        tool = await compile_tool_from_intent(
            intent="Convert text to uppercase",
            input_type=str,
            output_type=str,
        )

        assert isinstance(tool, JITToolWrapper)
        assert tool.name.startswith("jit_")

    @pytest.mark.asyncio
    async def test_intent_with_capabilities(self):
        """Test intent compilation with capabilities."""
        caps = ToolCapabilities(requires_network=False)
        tool = await compile_tool_from_intent(
            intent="Process text locally",
            input_type=str,
            output_type=str,
            capabilities=caps,
        )

        assert isinstance(tool, JITToolWrapper)

    @pytest.mark.asyncio
    async def test_intent_with_constraints(self):
        """Test intent compilation with custom constraints."""
        constraints = ArchitectConstraints(
            max_cyclomatic_complexity=10,
            entropy_budget=0.5,
        )

        tool = await compile_tool_from_intent(
            intent="Simple text transform",
            input_type=str,
            output_type=str,
            constraints=constraints,
        )

        assert tool.jit_tool_meta.jit_meta.constraints == constraints


# --- Composition Tests ---


class TestToolComposition:
    """Tests for tool composition via >> operator.

    Note: JIT tools return Result[B, ToolError], so composition behavior
    depends on the output type. When composing with agents that expect
    the raw value, we need to unwrap the Result first.

    For direct composition of JIT tools (Result >> Result), the composition
    passes the Result to the next tool's invoke which can handle it.
    """

    @pytest.mark.asyncio
    async def test_jit_tool_execution(self):
        """Test that JIT tools execute and return Results."""
        tool = await compile_tool_from_template(TEXT_TRANSFORMER)

        result = await tool.invoke("hello")

        assert result.is_ok()
        assert result.unwrap() == "HELLO"

    @pytest.mark.asyncio
    async def test_jit_tool_chain_via_unwrap(self):
        """Test chaining JIT tools by unwrapping Results."""
        # First tool: uppercase
        upper_tool = await compile_tool_from_template(TEXT_TRANSFORMER)

        # Second tool: add prefix (custom template)
        prefix_template = ToolTemplate(
            name="Prefix Adder",
            description="Add prefix to text",
            template_source="""
class PrefixAdder:
    def invoke(self, text: str) -> str:
        return "PREFIX: " + text
""",
            capabilities=ToolCapabilities(),
        )
        prefix_tool = await compile_tool_from_template(prefix_template)

        # Execute in sequence (manually chain Results)
        result1 = await upper_tool.invoke("hello")
        assert result1.is_ok()

        result2 = await prefix_tool.invoke(result1.unwrap())
        assert result2.is_ok()
        assert result2.unwrap() == "PREFIX: HELLO"

    @pytest.mark.asyncio
    async def test_jit_tool_with_wrapper_agent(self):
        """Test composing JIT tool with an adapter agent."""

        # Create adapter that unwraps Result then processes
        class UnwrapAndCount(Agent[Result, int]):
            @property
            def name(self) -> str:
                return "UnwrapAndCount"

            async def invoke(self, input: Result) -> int:
                if input.is_ok():
                    return len(input.unwrap())
                return -1

        # JIT tool
        jit_tool = await compile_tool_from_template(TEXT_TRANSFORMER)

        # Adapter agent
        count_agent = UnwrapAndCount()

        # Compose: JIT >> Unwrap+Count
        pipeline = jit_tool >> count_agent

        # Execute
        result = await pipeline.invoke("hello")

        # "hello" -> Ok("HELLO") -> 5
        assert result == 5

    @pytest.mark.asyncio
    async def test_agent_then_jit_tool(self):
        """Test composing regular Agent then JIT tool."""

        class PrependAgent(Agent[str, str]):
            @property
            def name(self) -> str:
                return "PrependAgent"

            async def invoke(self, input: str) -> str:
                return "START: " + input

        # Regular agent
        prepend_agent = PrependAgent()

        # JIT tool (uppercase)
        jit_tool = await compile_tool_from_template(TEXT_TRANSFORMER)

        # Compose: Regular >> JIT
        pipeline = prepend_agent >> jit_tool

        # Execute
        result = await pipeline.invoke("hello")

        # "hello" -> "START: hello" -> Ok("START: HELLO")
        assert result.is_ok()
        assert result.unwrap() == "START: HELLO"

    @pytest.mark.asyncio
    async def test_three_step_pipeline_via_sequential(self):
        """Test three-step JIT pipeline with sequential execution."""
        # Tool 1: Strip whitespace
        strip_tool = await compile_tool_from_template(
            TEXT_TRANSFORMER,
            parameters={
                "transform_method": "strip",
                "transform_description": "Strip whitespace",
            },
        )

        # Tool 2: Uppercase
        upper_tool = await compile_tool_from_template(TEXT_TRANSFORMER)

        # Tool 3: Add suffix (custom)
        suffix_template = ToolTemplate(
            name="Suffix Adder",
            description="Add suffix",
            template_source="""
class SuffixAdder:
    def invoke(self, text: str) -> str:
        return text + "!"
""",
            capabilities=ToolCapabilities(),
        )
        suffix_tool = await compile_tool_from_template(suffix_template)

        # Execute sequentially
        r1 = await strip_tool.invoke("  hello world  ")
        assert r1.is_ok()

        r2 = await upper_tool.invoke(r1.unwrap())
        assert r2.is_ok()

        r3 = await suffix_tool.invoke(r2.unwrap())
        assert r3.is_ok()

        # "  hello world  " -> "hello world" -> "HELLO WORLD" -> "HELLO WORLD!"
        assert r3.unwrap() == "HELLO WORLD!"


# --- Error Handling Tests ---


class TestErrorHandling:
    """Tests for error handling in J+T integration."""

    @pytest.mark.asyncio
    async def test_sandbox_blocks_forbidden_operations(self):
        """Test that sandbox blocks dangerous operations."""
        # Source that tries to use eval
        source = AgentSource(
            source="""
class MaliciousTool:
    def invoke(self, code: str) -> str:
        return eval(code)
""",
            class_name="MaliciousTool",
            imports=frozenset(),
            complexity=2,
            description="Tries to eval",
        )

        tool = await create_tool_from_source(
            source=source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("malicious", "Bad tool"),
        )

        result = await tool.invoke("1 + 1")

        # Should fail because eval is blocked
        assert result.is_err()
        assert result.error.error_type == ToolErrorType.FATAL

    @pytest.mark.asyncio
    async def test_sandbox_isolation(self):
        """Test that each invocation is isolated (no state leakage)."""
        # Stateful tool
        source = AgentSource(
            source="""
class StatefulTool:
    def __init__(self):
        self.counter = 0

    def invoke(self, x: str) -> int:
        self.counter += 1
        return self.counter
""",
            class_name="StatefulTool",
            imports=frozenset(),
            complexity=3,
            description="Tracks state",
        )

        tool = await create_tool_from_source(
            source=source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("stateful", "Stateful tool"),
        )

        # Each invocation should start fresh
        result1 = await tool.invoke("a")
        result2 = await tool.invoke("b")

        assert result1.is_ok()
        assert result2.is_ok()
        # Both should be 1 due to isolation
        assert result1.unwrap() == 1
        assert result2.unwrap() == 1

    @pytest.mark.asyncio
    async def test_tool_error_details(self):
        """Test that tool errors include useful details."""
        source = AgentSource(
            source="""
class DetailedError:
    def invoke(self, x: str) -> str:
        raise ValueError("Specific error message")
""",
            class_name="DetailedError",
            imports=frozenset(),
            complexity=2,
            description="Raises error",
        )

        tool = await create_tool_from_source(
            source=source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("error_detail", "Error details"),
        )

        result = await tool.invoke("test")

        assert result.is_err()
        error = result.error  # Access error directly on Err
        assert "DetailedError" in error.tool_name


# --- Metadata and Provenance Tests ---


class TestMetadataProvenance:
    """Tests for metadata and provenance tracking."""

    @pytest.mark.asyncio
    async def test_template_preserved_in_meta(self, custom_template: ToolTemplate):
        """Test that template is preserved in JITToolMeta."""
        tool = await compile_tool_from_template(custom_template)

        assert tool.jit_tool_meta.template is not None
        assert tool.jit_tool_meta.template.name == "Custom Echo"

    @pytest.mark.asyncio
    async def test_source_preserved_in_meta(self, simple_tool_source: AgentSource):
        """Test that source is preserved in metadata chain."""
        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("provenance", "Test provenance"),
        )

        jit_meta = tool.jit_tool_meta.jit_meta
        assert jit_meta.source == simple_tool_source
        assert jit_meta.source.class_name == "SimpleUppercase"

    @pytest.mark.asyncio
    async def test_constraints_preserved(self, simple_tool_source: AgentSource):
        """Test that constraints are preserved."""
        constraints = ArchitectConstraints(
            max_cyclomatic_complexity=20,
            entropy_budget=0.8,
        )

        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=constraints,
            tool_meta=make_tool_meta("constrained", "With constraints"),
        )

        assert tool.jit_tool_meta.jit_meta.constraints == constraints


# --- Built-in Templates Edge Cases ---


class TestBuiltInTemplateEdgeCases:
    """Edge case tests for built-in templates."""

    @pytest.mark.asyncio
    async def test_json_extractor_nested_field(self):
        """Test JSON extractor handles simple nested access via get."""
        tool = await compile_tool_from_template(
            JSON_FIELD_EXTRACTOR,
            parameters={"field": "data"},
        )

        # Nested dict gets converted to string
        result = await tool.invoke('{"data": {"nested": "value"}}')
        assert result.is_ok()
        # Returns string representation of dict
        assert "nested" in result.unwrap()

    @pytest.mark.asyncio
    async def test_text_transformer_empty_string(self):
        """Test text transformer with empty string."""
        tool = await compile_tool_from_template(TEXT_TRANSFORMER)

        result = await tool.invoke("")
        assert result.is_ok()
        assert result.unwrap() == ""

    @pytest.mark.asyncio
    async def test_filter_empty_list(self):
        """Test filter with empty list."""
        tool = await compile_tool_from_template(FILTER_TEMPLATE)

        result = await tool.invoke([])
        assert result.is_ok()
        assert result.unwrap() == []

    @pytest.mark.asyncio
    async def test_filter_all_filtered_out(self):
        """Test filter where all items are filtered."""
        tool = await compile_tool_from_template(FILTER_TEMPLATE)

        result = await tool.invoke([-5, -4, -3, -2, -1, 0])
        assert result.is_ok()
        assert result.unwrap() == []


# --- Integration with T-gents Types ---


class TestTGentsTypeIntegration:
    """Tests for integration with T-gents type system."""

    @pytest.mark.asyncio
    async def test_tool_returns_result_monad(self, simple_tool_source: AgentSource):
        """Test that JIT tools return Result monad."""
        tool = await create_tool_from_source(
            source=simple_tool_source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("result", "Returns Result"),
        )

        result = await tool.invoke("test")

        # Should be a Result type
        assert hasattr(result, "is_ok")
        assert hasattr(result, "is_err")
        assert hasattr(result, "unwrap")

    @pytest.mark.asyncio
    async def test_tool_error_type_correct(self):
        """Test that tool errors have correct ToolErrorType."""
        source = AgentSource(
            source="""
class ErrorTypeTool:
    def invoke(self, x: str) -> str:
        raise RuntimeError("Test error")
""",
            class_name="ErrorTypeTool",
            imports=frozenset(),
            complexity=2,
            description="Error type test",
        )

        tool = await create_tool_from_source(
            source=source,
            constraints=ArchitectConstraints(),
            tool_meta=make_tool_meta("error_type", "Error type"),
        )

        result = await tool.invoke("test")

        assert result.is_err()
        error = result.error  # Access error directly on Err
        assert isinstance(error, ToolError)
        assert error.error_type == ToolErrorType.FATAL

    @pytest.mark.asyncio
    async def test_tool_meta_minimal_factory(self):
        """Test ToolMeta.minimal factory method works with JIT tools."""
        meta = make_tool_meta("factory_test", "Testing minimal factory")

        source = AgentSource(
            source="""
class FactoryTest:
    def invoke(self, x: str) -> str:
        return x
""",
            class_name="FactoryTest",
            imports=frozenset(),
            complexity=1,
            description="Factory test",
        )

        tool = await create_tool_from_source(
            source=source,
            constraints=ArchitectConstraints(),
            tool_meta=meta,
        )

        assert tool.meta.identity.name == "factory_test"
        # Check description via identity
        assert tool.meta.identity.description == "Testing minimal factory"
