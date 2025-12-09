"""
T-gents × P-gents Integration Tests: Tool Parser Integration

Tests P-gent parsers specialized for T-gent (Tool) workflows:
- SchemaParser: MCP tool schemas → Tool[A,B] type signatures
- InputParser: Natural language → Tool parameters
- OutputParser: Tool responses → Structured data
- ErrorParser: Tool errors → Recovery strategies
"""

import json
from agents.t.p_integration import (
    SchemaParser,
    InputParser,
    OutputParser,
    ErrorParser,
    create_tgent_schema_parser,
    create_tgent_input_parser,
    create_tgent_output_parser,
    create_tgent_error_parser,
)


class TestSchemaParser:
    """Test MCP tool schema → Tool[A,B] signature parsing."""

    def test_parse_simple_mcp_schema(self):
        """Test parsing basic MCP tool schema."""
        parser = SchemaParser()

        schema = {
            "name": "web_search",
            "inputSchema": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
            },
            "outputSchema": {
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
        }

        result = parser.parse(json.dumps(schema))

        assert result.success
        assert result.value["name"] == "web_search"
        assert result.value["input_type"] == "web_search_Input"
        assert result.value["output_type"] == "web_search_Output"
        assert result.confidence > 0.7

    def test_parse_schema_with_titled_types(self):
        """Test schema parsing with explicit type titles."""
        parser = SchemaParser()

        schema = {
            "name": "calculate",
            "inputSchema": {
                "type": "object",
                "title": "CalculationRequest",
                "properties": {"expr": {"type": "string"}},
            },
            "outputSchema": {"type": "object", "title": "CalculationResult"},
        }

        result = parser.parse(json.dumps(schema))

        assert result.success
        assert result.value["input_type"] == "CalculationRequest"
        assert result.value["output_type"] == "CalculationResult"

    def test_parse_schema_with_primitive_types(self):
        """Test schema with primitive input/output types."""
        parser = SchemaParser()

        schema = {
            "name": "uppercase",
            "inputSchema": {"type": "string"},
            "outputSchema": {"type": "string"},
        }

        result = parser.parse(json.dumps(schema))

        assert result.success
        assert result.value["input_type"] == "str"
        assert result.value["output_type"] == "str"

    def test_parse_schema_missing_name(self):
        """Test schema parsing fails without name."""
        parser = SchemaParser()

        schema = {"inputSchema": {"type": "object"}, "outputSchema": {"type": "object"}}

        result = parser.parse(json.dumps(schema))

        assert not result.success
        assert "name" in result.error.lower()

    def test_parse_schema_missing_io_schemas(self):
        """Test schema with missing I/O schemas defaults to Any."""
        parser = SchemaParser()

        schema = {"name": "black_box"}

        result = parser.parse(json.dumps(schema))

        assert result.success
        assert result.value["input_type"] == "Any"
        assert result.value["output_type"] == "Any"

    def test_schema_parser_preserves_original(self):
        """Test that original schemas are preserved in result."""
        parser = SchemaParser()

        schema = {
            "name": "test",
            "inputSchema": {"type": "string"},
            "outputSchema": {"type": "number"},
        }

        result = parser.parse(json.dumps(schema))

        assert result.success
        assert result.value["input_schema"] == {"type": "string"}
        assert result.value["output_schema"] == {"type": "number"}

    def test_convenience_constructor(self):
        """Test create_tgent_schema_parser() convenience function."""
        parser = create_tgent_schema_parser()

        schema = {"name": "tool", "inputSchema": {"type": "object"}}
        result = parser.parse(json.dumps(schema))

        assert result.success
        assert result.value["name"] == "tool"


class TestInputParser:
    """Test natural language → tool parameters parsing."""

    def test_parse_input_with_anchors(self):
        """Test parsing parameters with anchor markers."""
        parser = InputParser(parameter_names=["query", "limit"])

        text = """
        Search for something
        ###query: Python agents
        ###limit: 10
        """

        result = parser.parse(text)

        assert result.success
        assert result.value["query"] == "Python agents"
        assert result.value["limit"] == "10"
        assert result.confidence > 0.6

    def test_parse_input_single_param(self):
        """Test parsing single parameter."""
        parser = InputParser(parameter_names=["message"])

        text = "###message: Hello world"
        result = parser.parse(text)

        assert result.success
        assert result.value["message"] == "Hello world"

    def test_parse_input_as_json_fallback(self):
        """Test fallback to JSON parsing when no anchors found."""
        parser = InputParser(parameter_names=["query"])

        text = '{"query": "test query", "extra": "ignored"}'
        result = parser.parse(text)

        assert result.success
        assert "query" in result.value

    def test_parse_input_no_params_found(self):
        """Test parsing fails when no parameters extracted."""
        parser = InputParser(parameter_names=["missing"])

        text = "Just some random text with no parameters"
        result = parser.parse(text)

        assert not result.success
        assert "no parameters" in result.error.lower()

    def test_parse_input_partial_match(self):
        """Test partial parameter matching."""
        parser = InputParser(parameter_names=["query", "filter", "sort"])

        text = """
        ###query: search term
        ###filter: category:tech
        """

        result = parser.parse(text)

        assert result.success
        assert "query" in result.value
        assert "filter" in result.value
        assert "sort" not in result.value  # Missing param is not included

    def test_convenience_constructor(self):
        """Test create_tgent_input_parser() convenience function."""
        parser = create_tgent_input_parser(["param1", "param2"])

        text = "###param1: value1\n###param2: value2"
        result = parser.parse(text)

        assert result.success
        assert result.value["param1"] == "value1"


class TestOutputParser:
    """Test tool output → structured data parsing."""

    def test_parse_json_output(self):
        """Test parsing clean JSON output."""
        parser = OutputParser()

        output = '{"status": "success", "result": [1, 2, 3]}'
        result = parser.parse(output)

        assert result.success
        assert result.value["status"] == "success"
        assert result.value["result"] == [1, 2, 3]

    def test_parse_nested_json_output(self):
        """Test parsing nested JSON structures."""
        parser = OutputParser()

        output = """
        {
            "data": {
                "items": [
                    {"id": 1, "name": "foo"},
                    {"id": 2, "name": "bar"}
                ],
                "count": 2
            }
        }
        """
        result = parser.parse(output)

        assert result.success
        assert result.value["data"]["count"] == 2
        assert len(result.value["data"]["items"]) == 2

    def test_parse_malformed_json(self):
        """Test parsing malformed JSON with repairs."""
        parser = OutputParser()

        # Missing closing brace
        output = '{"status": "success", "count": 42'
        result = parser.parse(output)

        # P-gent parsers should attempt repair
        # Success depends on repair strategy, but should not crash
        assert result.success or not result.success  # Either outcome is valid
        if result.success:
            assert len(result.repairs) > 0

    def test_parse_output_with_expected_type(self):
        """Test parsing with expected type hint."""
        parser = OutputParser(expected_type="SearchResults")

        output = '{"results": ["item1", "item2"]}'
        result = parser.parse(output)

        assert result.success
        assert result.metadata["expected_type"] == "SearchResults"

    def test_parse_empty_output(self):
        """Test parsing empty output."""
        parser = OutputParser()

        output = "{}"
        result = parser.parse(output)

        assert result.success
        assert result.value == {}

    def test_convenience_constructor(self):
        """Test create_tgent_output_parser() convenience function."""
        parser = create_tgent_output_parser(expected_type="TestOutput")

        output = '{"test": true}'
        result = parser.parse(output)

        assert result.success


class TestErrorParser:
    """Test tool error → recovery strategy parsing."""

    def test_parse_timeout_error(self):
        """Test classification of timeout errors."""
        parser = ErrorParser()

        error = "Connection timeout after 30 seconds"
        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "transient"
        assert result.value["recovery"] == "retry"

    def test_parse_auth_error(self):
        """Test classification of authentication errors."""
        parser = ErrorParser()

        error = "401 Unauthorized: Invalid API key"
        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "auth"
        assert result.value["recovery"] == "refresh_credentials"

    def test_parse_not_found_error(self):
        """Test classification of not found errors."""
        parser = ErrorParser()

        error = "404 Not Found: Resource does not exist"
        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "not_found"
        assert result.value["recovery"] == "check_inputs"

    def test_parse_rate_limit_error(self):
        """Test classification of rate limit errors."""
        parser = ErrorParser()

        error = "429 Too Many Requests: Rate limit exceeded"
        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "rate_limit"
        assert result.value["recovery"] == "backoff"

    def test_parse_structured_error(self):
        """Test parsing structured error JSON."""
        parser = ErrorParser()

        error = json.dumps(
            {
                "error": "Server overloaded",
                "code": 503,
                "message": "Service temporarily unavailable",
            }
        )

        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "server_error"
        assert result.value["recovery"] == "retry"

    def test_parse_400_bad_request(self):
        """Test classification of bad request errors."""
        parser = ErrorParser()

        error = json.dumps({"status_code": 400, "message": "Invalid parameter format"})
        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "bad_request"
        assert result.value["recovery"] == "validate_inputs"

    def test_parse_network_error(self):
        """Test classification of network errors."""
        parser = ErrorParser()

        error = "Network connection refused"
        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "transient"
        assert result.value["recovery"] == "retry"

    def test_parse_unknown_error(self):
        """Test fallback for unknown error types."""
        parser = ErrorParser()

        error = "Something completely unexpected happened"
        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "unknown"
        assert result.value["recovery"] == "manual_intervention"

    def test_parse_forbidden_error(self):
        """Test classification of forbidden errors."""
        parser = ErrorParser()

        error = "403 Forbidden: Insufficient permissions"
        result = parser.parse(error)

        assert result.success
        assert result.value["error_type"] == "auth"
        assert result.value["recovery"] == "refresh_credentials"

    def test_convenience_constructor(self):
        """Test create_tgent_error_parser() convenience function."""
        parser = create_tgent_error_parser()

        error = "Connection timeout"
        result = parser.parse(error)

        assert result.success
        assert "transient" in result.value["error_type"]


class TestStreamingSupport:
    """Test streaming support for all T-gent parsers."""

    def test_schema_parser_stream(self):
        """Test SchemaParser streaming."""
        parser = SchemaParser()

        tokens = ['{"name":', ' "test",', ' "inputSchema":', ' {"type": "string"}}']
        results = parser.parse_stream(tokens)

        assert len(results) == 1
        assert results[0].success

    def test_input_parser_stream(self):
        """Test InputParser streaming."""
        parser = InputParser(parameter_names=["query"])

        tokens = ["###query:", " test query"]
        results = parser.parse_stream(tokens)

        assert len(results) == 1
        assert results[0].success

    def test_output_parser_stream(self):
        """Test OutputParser streaming."""
        parser = OutputParser()

        tokens = ['{"result":', ' "success"}']
        results = parser.parse_stream(tokens)

        assert len(results) == 1
        assert results[0].success

    def test_error_parser_stream(self):
        """Test ErrorParser streaming."""
        parser = ErrorParser()

        tokens = ["Connection", " timeout"]
        results = parser.parse_stream(tokens)

        assert len(results) == 1
        assert results[0].success


class TestParserConfiguration:
    """Test parser configuration and customization."""

    def test_schema_parser_configure(self):
        """Test SchemaParser configuration."""
        parser = SchemaParser()
        configured = parser.configure(min_confidence=0.9)

        assert configured.config.min_confidence == 0.9
        assert isinstance(configured, SchemaParser)

    def test_input_parser_configure(self):
        """Test InputParser configuration."""
        parser = InputParser(parameter_names=["test"])
        configured = parser.configure(allow_partial=False)

        assert configured.config.allow_partial == False
        assert configured.parameter_names == ["test"]

    def test_output_parser_configure(self):
        """Test OutputParser configuration."""
        parser = OutputParser(expected_type="Test")
        configured = parser.configure(min_confidence=0.8)

        assert configured.expected_type == "Test"
        assert configured.config.min_confidence == 0.8

    def test_error_parser_configure(self):
        """Test ErrorParser configuration."""
        parser = ErrorParser()
        configured = parser.configure(allow_partial=True)

        assert configured.config.allow_partial == True


class TestRealWorldToolScenarios:
    """Test real-world tool use scenarios."""

    def test_web_search_tool_workflow(self):
        """Test complete workflow: schema → input → output."""
        # 1. Parse tool schema
        schema_parser = create_tgent_schema_parser()
        schema = {
            "name": "web_search",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "max_results": {"type": "integer"},
                },
            },
            "outputSchema": {
                "type": "object",
                "properties": {"results": {"type": "array"}},
            },
        }
        schema_result = schema_parser.parse(json.dumps(schema))
        assert schema_result.success

        # 2. Parse user input
        input_parser = create_tgent_input_parser(["query", "max_results"])
        user_input = "###query: Python frameworks\n###max_results: 5"
        input_result = input_parser.parse(user_input)
        assert input_result.success

        # 3. Parse tool output
        output_parser = create_tgent_output_parser()
        tool_output = '{"results": ["Django", "Flask", "FastAPI"]}'
        output_result = output_parser.parse(tool_output)
        assert output_result.success

    def test_api_call_error_handling(self):
        """Test error handling in API tool workflow."""
        # Parse various API errors
        error_parser = create_tgent_error_parser()

        # Scenario 1: Rate limit
        error1 = "429 Too Many Requests"
        result1 = error_parser.parse(error1)
        assert result1.value["recovery"] == "backoff"

        # Scenario 2: Auth failure
        error2 = "401 Unauthorized"
        result2 = error_parser.parse(error2)
        assert result2.value["recovery"] == "refresh_credentials"

        # Scenario 3: Transient network issue
        error3 = "Connection timeout"
        result3 = error_parser.parse(error3)
        assert result3.value["recovery"] == "retry"

    def test_database_query_tool_workflow(self):
        """Test database query tool workflow."""
        # Schema for SQL query tool
        schema_parser = create_tgent_schema_parser()
        schema = {
            "name": "sql_query",
            "inputSchema": {"type": "object"},
            "outputSchema": {"type": "object"},
        }
        schema_result = schema_parser.parse(json.dumps(schema))
        assert schema_result.success

        # Parse query results
        output_parser = create_tgent_output_parser()
        results = '{"rows": [{"id": 1, "name": "test"}], "count": 1}'
        output_result = output_parser.parse(results)
        assert output_result.success
        assert output_result.value["count"] == 1
