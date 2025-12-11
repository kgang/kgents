"""
Cross-Agent Integration Tests: P × J × T

Tests integration between Parser, JIT, and Tool agents:
- P × J: P-gent parsers validate JIT agent outputs
- T × P: T-gents use P-gent parsers for tool I/O
- J × T: JIT-generated Tools with dynamic behavior
- P × J × T: Complete workflow combining all three

Philosophy: Agents compose via >> and integrate via shared protocols.
"""

import json

import pytest
from agents.j import (
    AgentSource,
    JITAgentWrapper,
    create_agent_from_source,
)
from agents.p import (
    AnchorBasedParser,
    ParserConfig,
    ProbabilisticASTParser,
)
from agents.t.p_integration import (
    create_tgent_error_parser,
    create_tgent_output_parser,
    create_tgent_schema_parser,
)


class TestParsersWithJITAgents:
    """Test P-gent parsers validating J-gent outputs."""

    @pytest.mark.asyncio
    async def test_jit_agent_output_parsed_by_pgent(self) -> None:
        """Test P-gent parsing output from JIT agent."""
        # Create JIT agent that returns JSON-like string manually
        # Note: JIT sandbox doesn't support imports, so we build JSON manually
        source = AgentSource(
            source="""
class JSONProducer:
    async def invoke(self, input: str) -> str:
        # Manually construct JSON string (sandbox limitation)
        return f'{{"message": "Processed: {input}", "status": "ok"}}'
""",
            class_name="JSONProducer",
            imports=frozenset(),
            complexity=1,
            description="JIT agent producing JSON output",
        )

        jit_agent = await create_agent_from_source(source, validate=False)

        # Invoke JIT agent
        result = await jit_agent.invoke("test input")

        # Parse output with P-gent parser
        parser = ProbabilisticASTParser(config=ParserConfig())
        parse_result = parser.parse(result)

        assert parse_result.success
        assert parse_result.value.value["message"] == "Processed: test input"
        assert parse_result.value.value["status"] == "ok"
        assert parse_result.confidence > 0.7

    @pytest.mark.asyncio
    async def test_jit_agent_with_anchor_output(self) -> None:
        """Test JIT agent using anchor markers parsed by P-gent."""
        source = AgentSource(
            source="""
class AnchorProducer:
    async def invoke(self, input: str) -> str:
        return f'''
        ###RESULT: {input.upper()}
        ###STATUS: completed
        ###CONFIDENCE: 0.95
        '''
""",
            class_name="AnchorProducer",
            imports=frozenset(),
            complexity=1,
            description="JIT agent with anchor-based output",
        )

        jit_agent = await create_agent_from_source(source, validate=False)
        result = await jit_agent.invoke("test")

        # Parse with anchor-based parser
        result_parser = AnchorBasedParser(anchor="###RESULT:")
        status_parser = AnchorBasedParser(anchor="###STATUS:")
        confidence_parser = AnchorBasedParser(anchor="###CONFIDENCE:")

        result_parsed = result_parser.parse(result)
        status_parsed = status_parser.parse(result)
        confidence_parsed = confidence_parser.parse(result)

        assert result_parsed.success
        assert "TEST" in result_parsed.value[0]
        assert status_parsed.value[0].strip() == "completed"
        assert "0.95" in confidence_parsed.value[0]

    @pytest.mark.asyncio
    async def test_jit_agent_composition_with_parser(self) -> None:
        """Test composing JIT agent with parser validation."""
        # Create JIT agent (manually construct JSON due to sandbox limitations)
        source = AgentSource(
            source="""
class DataGenerator:
    async def invoke(self, input: dict) -> str:
        value = input.get("value", "")
        count = len(value)
        # Manually construct JSON
        return f'{{"processed": "{value}", "count": {count}}}'
""",
            class_name="DataGenerator",
            imports=frozenset(),
            complexity=1,
            description="JIT data generator",
        )

        jit_agent = await create_agent_from_source(source, validate=False)

        # Invoke and parse
        output = await jit_agent.invoke({"value": "test"})
        parser = create_tgent_output_parser()
        parse_result = parser.parse(output)

        assert parse_result.success
        assert parse_result.value["processed"] == "test"
        assert parse_result.value["count"] == 4


class TestToolsWithParserIntegration:
    """Test T-gents using P-gent parsers for tool I/O."""

    def test_tool_schema_parsing_workflow(self) -> None:
        """Test complete tool schema parsing workflow."""
        # Define tool schema (as if from MCP)
        tool_schema = {
            "name": "calculator",
            "description": "Perform calculations",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "expression": {"type": "string"},
                    "precision": {"type": "integer"},
                },
            },
            "outputSchema": {
                "type": "object",
                "properties": {
                    "result": {"type": "number"},
                    "formatted": {"type": "string"},
                },
            },
        }

        # Parse schema with T-gent schema parser
        schema_parser = create_tgent_schema_parser()
        result = schema_parser.parse(json.dumps(tool_schema))

        assert result.success
        assert result.value["name"] == "calculator"
        assert "Input" in result.value["input_type"]
        assert "Output" in result.value["output_type"]

        # Verify schema is preserved for runtime use
        assert result.value["input_schema"] == tool_schema["inputSchema"]
        assert result.value["output_schema"] == tool_schema["outputSchema"]

    def test_tool_error_classification_workflow(self) -> None:
        """Test tool error parsing and recovery strategy."""
        error_parser = create_tgent_error_parser()

        # Simulate various tool errors
        errors = [
            ("timeout", "Connection timeout after 30s", "transient", "retry"),
            ("auth", "401 Unauthorized", "auth", "refresh_credentials"),
            ("rate_limit", "429 Too Many Requests", "rate_limit", "backoff"),
            ("not_found", "404 Resource Not Found", "not_found", "check_inputs"),
        ]

        for error_name, error_msg, expected_type, expected_recovery in errors:
            result = error_parser.parse(error_msg)

            assert result.success, f"Failed to parse {error_name}"
            assert result.value["error_type"] == expected_type
            assert result.value["recovery"] == expected_recovery

    def test_tool_output_validation_with_parser(self) -> None:
        """Test validating tool outputs against schema."""
        # Tool output
        tool_output = json.dumps(
            {"data": [1, 2, 3], "metadata": {"count": 3, "source": "api"}}
        )

        # Parse and validate
        parser = create_tgent_output_parser()
        result = parser.parse(tool_output)

        assert result.success
        assert isinstance(result.value["data"], list)
        assert isinstance(result.value["metadata"], dict)
        assert result.value["metadata"]["count"] == 3


class TestJITToolsIntegration:
    """Test JIT-generated Tools (J × T integration)."""

    @pytest.mark.asyncio
    async def test_jit_generated_tool_agent(self) -> None:
        """Test creating a Tool via JIT compilation."""
        # JIT source for a simple Tool-like agent
        source = AgentSource(
            source="""
class SimpleToolAgent:
    async def invoke(self, input: str) -> dict:
        # Simulate tool behavior
        return {
            "tool_name": "jit_tool",
            "input_received": input,
            "output": input.upper(),
            "metadata": {"jit_compiled": True}
        }
""",
            class_name="SimpleToolAgent",
            imports=frozenset(),
            complexity=1,
            description="JIT-compiled tool-like agent",
        )

        tool_agent = await create_agent_from_source(source, validate=False)

        # Use as tool
        result = await tool_agent.invoke("test input")

        assert isinstance(result, dict)
        assert result["tool_name"] == "jit_tool"
        assert result["output"] == "TEST INPUT"
        assert result["metadata"]["jit_compiled"] is True

    @pytest.mark.asyncio
    async def test_jit_tool_with_error_handling(self) -> None:
        """Test JIT tool with error handling."""
        source = AgentSource(
            source="""
class ErrorHandlingTool:
    async def invoke(self, input: dict) -> dict:
        if input.get("should_error"):
            return {
                "error": "Simulated error",
                "code": input.get("error_code", 500)
            }
        return {"result": "success"}
""",
            class_name="ErrorHandlingTool",
            imports=frozenset(),
            complexity=2,
            description="JIT tool with error simulation",
        )

        tool_agent = await create_agent_from_source(source, validate=False)

        # Normal execution
        success_result = await tool_agent.invoke({"should_error": False})
        assert success_result["result"] == "success"

        # Error scenario
        error_result = await tool_agent.invoke(
            {"should_error": True, "error_code": 404}
        )

        # Parse error with T-gent error parser
        error_parser = create_tgent_error_parser()
        error_parsed = error_parser.parse(json.dumps(error_result))

        assert error_parsed.success
        assert error_parsed.value["error_type"] == "not_found"


class TestCompleteWorkflow:
    """Test complete P × J × T workflows."""

    @pytest.mark.asyncio
    async def test_jit_tool_with_parsed_io(self) -> None:
        """Test JIT Tool with P-gent parsing for both I/O."""
        # Simplified version without JSON module (sandbox limitation)
        # Note: Real tools would use proper JSON, but JIT sandbox restricts imports
        source = AgentSource(
            source="""
class DataProcessorTool:
    async def invoke(self, input: str) -> str:
        # Simplified processing (real version would parse JSON input)
        # For demo, we hardcode expected input format
        if "sum" in input:
            # Manually construct JSON output
            return '{"operation": "sum", "result": 15, "input_count": 5}'
        return '{"operation": "unknown", "result": 0, "input_count": 0}'
""",
            class_name="DataProcessorTool",
            imports=frozenset(),
            complexity=2,
            description="JIT tool with simulated I/O",
        )

        tool = await create_agent_from_source(source, validate=False)

        # Execute tool (simplified input)
        tool_output = await tool.invoke("operation:sum")

        # Parse output with P-gent
        output_parser = create_tgent_output_parser()
        parsed_output = output_parser.parse(tool_output)

        assert parsed_output.success
        assert parsed_output.value["operation"] == "sum"
        assert parsed_output.value["result"] == 15

    @pytest.mark.asyncio
    async def test_tool_pipeline_with_parsers(self) -> None:
        """Test pipeline of tools with parser validation at each step."""
        # Simplified pipeline (sandbox limitations prevent JSON imports)
        # Tool 1: Data extractor (JIT)
        extractor_source = AgentSource(
            source="""
class DataExtractor:
    async def invoke(self, input: str) -> str:
        # Extract numbers from text (simplified)
        numbers = [word for word in input.split() if word.isdigit()]
        # Manually construct JSON
        return f'{{"extracted": [{", ".join(numbers)}], "count": {len(numbers)}}}'
""",
            class_name="DataExtractor",
            imports=frozenset(),
            complexity=2,
            description="Extract numbers from text",
        )

        extractor = await create_agent_from_source(extractor_source, validate=False)

        # Execute pipeline step 1
        input_text = "There are 10 items and 5 categories with 3 tags"
        step1_output = await extractor.invoke(input_text)

        # Validate step 1 output
        parser = create_tgent_output_parser()
        step1_parsed = parser.parse(step1_output)

        assert step1_parsed.success
        assert step1_parsed.value["extracted"] == [10, 5, 3]
        assert step1_parsed.value["count"] == 3

        # Tool 2: Calculator (JIT) - simplified version
        calculator_source = AgentSource(
            source="""
class Calculator:
    async def invoke(self, input: str) -> str:
        # Simplified calculation (real version would parse input)
        # For demo purposes, return hardcoded result
        return '{"sum": 18, "product": 150, "count": 3}'
""",
            class_name="Calculator",
            imports=frozenset(),
            complexity=2,
            description="Calculate sum and product",
        )

        calculator = await create_agent_from_source(calculator_source, validate=False)

        # Execute pipeline step 2
        step2_output = await calculator.invoke(step1_output)

        # Validate step 2 output
        step2_parsed = parser.parse(step2_output)

        assert step2_parsed.success
        assert step2_parsed.value["sum"] == 18
        assert step2_parsed.value["product"] == 150
        assert step2_parsed.value["count"] == 3

    @pytest.mark.asyncio
    async def test_tool_with_fallback_parsing(self) -> None:
        """Test tool with multiple parser strategies (P-gent strength)."""
        # Create JIT tool with potentially malformed output
        source = AgentSource(
            source="""
class FlakeyOutputTool:
    async def invoke(self, input: str) -> str:
        # Sometimes returns malformed JSON
        if "clean" in input:
            return '{"result": "success", "data": [1, 2, 3]}'
        else:
            # Missing closing brace
            return '{"result": "success", "data": [1, 2, 3]'
""",
            class_name="FlakeyOutputTool",
            imports=frozenset(),
            complexity=2,
            description="Tool with inconsistent output format",
        )

        tool = await create_agent_from_source(source, validate=False)

        # Test with clean output
        clean_output = await tool.invoke("clean test")
        parser = create_tgent_output_parser()
        clean_parsed = parser.parse(clean_output)

        assert clean_parsed.success
        assert clean_parsed.value["result"] == "success"

        # Test with malformed output (P-gent should repair)
        malformed_output = await tool.invoke("messy test")
        malformed_parsed = parser.parse(malformed_output)

        # P-gent parsers handle malformed JSON gracefully
        # They either succeed with repairs or fail gracefully
        if malformed_parsed.success:
            assert len(malformed_parsed.repairs) > 0  # Repairs were applied
            assert malformed_parsed.confidence < 1.0  # Confidence reduced
        else:
            assert malformed_parsed.error is not None  # Clear error message


class TestMetadataAndProvenance:
    """Test metadata and provenance tracking across integrations."""

    @pytest.mark.asyncio
    async def test_jit_tool_provenance_preserved(self) -> None:
        """Test that JIT tool provenance is preserved through parsing."""
        source = AgentSource(
            source="""
class ProvenanceTool:
    async def invoke(self, input: str) -> str:
        upper_input = input.upper()
        # Manually construct JSON (sandbox limitation)
        return f'{{"result": "{upper_input}", "tool_version": "jit-v1.0", "compilation_timestamp": "2025-12-09"}}'
""",
            class_name="ProvenanceTool",
            imports=frozenset(),
            complexity=1,
            description="Tool with provenance metadata",
        )

        tool = await create_agent_from_source(source, validate=False)

        # Verify JIT metadata
        assert isinstance(tool, JITAgentWrapper)
        assert hasattr(tool, "jit_meta")

        # Execute and parse
        output = await tool.invoke("test")
        parser = create_tgent_output_parser()
        parsed = parser.parse(output)

        assert parsed.success
        assert parsed.value["tool_version"] == "jit-v1.0"
        assert "compilation_timestamp" in parsed.value

    def test_parser_metadata_tracking(self) -> None:
        """Test that P-gent parser metadata is tracked."""
        parser = create_tgent_output_parser(expected_type="TestOutput")

        output = '{"test": "data", "count": 42}'
        result = parser.parse(output)

        assert result.success
        assert result.metadata["expected_type"] == "TestOutput"
        assert "actual_type" in result.metadata
        assert result.strategy == "output-parsed"
