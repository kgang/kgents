"""
T-gents × P-gents Integration: Parse tool schemas, inputs, outputs, and errors

This module provides P-gent parsers specialized for T-gent (Tool) workflows:
- Schema parsing: MCP tool schemas → Tool type signatures
- Input parsing: Natural language → Tool parameters
- Output parsing: Tool responses → Structured data
- Error parsing: Tool errors → Recovery strategies

Philosophy: Tools interface with external systems (APIs, databases, filesystems).
P-gents ensure that data crossing tool boundaries is well-formed and type-safe.
"""

from dataclasses import dataclass, field
from typing import Any, Iterator, Optional

from agents.p.core import Parser, ParserConfig, ParseResult
from agents.p.strategies.anchor import AnchorBasedParser
from agents.p.strategies.probabilistic_ast import (
    ProbabilisticASTParser,
    query_confident_fields,
)


@dataclass
class SchemaParser(Parser[dict[str, Any]]):
    """
    Parse MCP tool schema into kgents Tool type signature.

    Converts MCP JSON schema → Tool[A, B] signature with confidence scoring.

    Example:
        parser = SchemaParser()
        mcp_schema = {
            "name": "web_search",
            "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}}},
            "outputSchema": {"type": "object", "properties": {"results": {"type": "array"}}}
        }
        result = parser.parse(json.dumps(mcp_schema))
        # result.value = {"name": "web_search", "input_type": "SearchQuery", "output_type": "SearchResults"}
    """

    config: ParserConfig = field(default_factory=ParserConfig)

    def parse(self, text: str) -> ParseResult[dict[str, Any]]:
        """Parse MCP schema into Tool signature."""
        # Try probabilistic AST first
        prob_parser = ProbabilisticASTParser(config=self.config)
        result = prob_parser.parse(text)

        if not result.success or result.value is None:
            return ParseResult[dict[str, Any]](
                success=False, error=f"Failed to parse schema: {result.error}"
            )

        # Extract confident fields
        schema = query_confident_fields(result.value, min_confidence=0.7)

        if not schema or not isinstance(schema, dict):
            return ParseResult[dict[str, Any]](
                success=False, error="Schema is not a valid object"
            )

        # Convert to Tool signature
        tool_sig: dict[str, Any] = {}

        # Extract name
        if "name" in schema:
            tool_sig["name"] = schema["name"]
        else:
            return ParseResult[dict[str, Any]](
                success=False, error="Schema missing 'name' field"
            )

        # Infer input type from schema
        if "inputSchema" in schema:
            input_schema = schema["inputSchema"]
            tool_sig["input_type"] = self._infer_type_name(
                input_schema, f"{tool_sig['name']}_Input"
            )
        else:
            tool_sig["input_type"] = "Any"

        # Infer output type from schema
        if "outputSchema" in schema:
            output_schema = schema["outputSchema"]
            tool_sig["output_type"] = self._infer_type_name(
                output_schema, f"{tool_sig['name']}_Output"
            )
        else:
            tool_sig["output_type"] = "Any"

        # Store original schemas
        tool_sig["input_schema"] = schema.get("inputSchema", {})
        tool_sig["output_schema"] = schema.get("outputSchema", {})

        return ParseResult[dict[str, Any]](
            success=True,
            value=tool_sig,
            confidence=result.confidence,
            strategy="schema-parsed",
            repairs=result.repairs,
            metadata={"original_confidence": result.confidence},
        )

    def _infer_type_name(self, json_schema: dict[str, Any], default: str) -> str:
        """Infer a type name from JSON schema."""
        if isinstance(json_schema, dict):
            schema_type = json_schema.get("type", "object")

            if schema_type == "string":
                return "str"
            elif schema_type == "number":
                return "float"
            elif schema_type == "integer":
                return "int"
            elif schema_type == "boolean":
                return "bool"
            elif schema_type == "array":
                return "list"
            elif schema_type == "object":
                # Check if there's a title
                if "title" in json_schema:
                    title = json_schema["title"]
                    return str(title) if title else default
                return default
            else:
                return default
        return default

    def parse_stream(
        self, tokens: Iterator[str]
    ) -> Iterator[ParseResult[dict[str, Any]]]:
        """Stream parsing (buffer and parse once)."""
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config_updates: Any) -> "SchemaParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return SchemaParser(config=new_config)


@dataclass
class InputParser(Parser[dict[str, Any]]):
    """
    Parse natural language into tool parameters.

    Uses anchor-based extraction for parameter names, with type coercion.

    Example:
        parser = InputParser()
        result = parser.parse('''
            Search for "Python agents" on the web
            ###query: Python agents
        ''')
        # result.value = {"query": "Python agents"}
    """

    parameter_names: list[str] = field(default_factory=list)
    config: ParserConfig = field(default_factory=ParserConfig)

    def parse(self, text: str) -> ParseResult[dict[str, Any]]:
        """Parse natural language into parameters."""
        params: dict[str, Any] = {}
        confidence_scores: list[float] = []

        # Try to extract parameters using anchors
        for param_name in self.parameter_names:
            anchor_parser: AnchorBasedParser[list[str]] = AnchorBasedParser(
                anchor=f"###{param_name}:"
            )
            result = anchor_parser.parse(text)

            if result.success and result.value:
                params[param_name] = result.value[0]
                confidence_scores.append(result.confidence)

        if not params:
            # Fallback: try to parse as JSON
            prob_parser = ProbabilisticASTParser(config=self.config)
            prob_result = prob_parser.parse(text)

            if prob_result.success and prob_result.value is not None:
                confident = query_confident_fields(
                    prob_result.value, min_confidence=0.6
                )
                if confident and isinstance(confident, dict):
                    params = confident
                    confidence_scores = [prob_result.confidence]

        if not params:
            return ParseResult[dict[str, Any]](
                success=False, error="No parameters found in input"
            )

        avg_confidence = (
            sum(confidence_scores) / len(confidence_scores)
            if confidence_scores
            else 0.5
        )

        return ParseResult[dict[str, Any]](
            success=True,
            value=params,
            confidence=avg_confidence,
            strategy="input-parsed",
            metadata={"param_count": len(params)},
        )

    def parse_stream(
        self, tokens: Iterator[str]
    ) -> Iterator[ParseResult[dict[str, Any]]]:
        """Stream parsing."""
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config_updates: Any) -> "InputParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return InputParser(parameter_names=self.parameter_names, config=new_config)


@dataclass
class OutputParser(Parser[Any]):
    """
    Parse tool output into structured data.

    Uses probabilistic AST with confidence scoring.

    Example:
        parser = OutputParser()
        result = parser.parse('{"results": ["item1", "item2"], "count": 2}')
    """

    expected_type: Optional[str] = None
    config: ParserConfig = field(default_factory=ParserConfig)

    def parse(self, text: str) -> ParseResult[Any]:
        """Parse tool output."""
        prob_parser = ProbabilisticASTParser(config=self.config)
        result = prob_parser.parse(text)

        if not result.success:
            return ParseResult[Any](
                success=False, error=f"Failed to parse output: {result.error}"
            )

        # Extract confident value
        if result.value is None:
            return ParseResult[Any](success=False, error="Parse result has no value")
        confident_value = query_confident_fields(
            result.value, min_confidence=self.config.min_confidence
        )

        return ParseResult[Any](
            success=True,
            value=confident_value
            if confident_value is not None
            else result.value.value,
            confidence=result.confidence,
            strategy="output-parsed",
            repairs=result.repairs,
            metadata={
                "expected_type": self.expected_type,
                "actual_type": type(confident_value).__name__,
            },
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[Any]]:
        """Stream parsing."""
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config_updates: Any) -> "OutputParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return OutputParser(expected_type=self.expected_type, config=new_config)


@dataclass
class ErrorParser(Parser[dict[str, Any]]):
    """
    Parse tool errors into recovery strategies.

    Classifies errors and suggests recovery actions.

    Example:
        parser = ErrorParser()
        result = parser.parse('{"error": "Connection timeout", "code": 504}')
        # result.value = {"error_type": "transient", "recovery": "retry", "details": "..."}
    """

    config: ParserConfig = field(default_factory=ParserConfig)

    def parse(self, text: str) -> ParseResult[dict[str, Any]]:
        """Parse error into recovery strategy."""
        # Parse error structure
        prob_parser = ProbabilisticASTParser(config=self.config)
        result = prob_parser.parse(text)

        if not result.success or result.value is None:
            # Raw error string
            return self._classify_raw_error(text)

        # Extract confident fields
        error_data = query_confident_fields(result.value, min_confidence=0.5)

        if not error_data or not isinstance(error_data, dict):
            return self._classify_raw_error(text)

        # Classify error type
        error_classification = self._classify_error(error_data)

        return ParseResult[dict[str, Any]](
            success=True,
            value=error_classification,
            confidence=result.confidence * 0.9,  # Slightly reduce for classification
            strategy="error-parsed",
            repairs=result.repairs,
            metadata={"original_error": error_data},
        )

    def _classify_raw_error(self, text: str) -> ParseResult[dict[str, Any]]:
        """Classify error from raw text."""
        text_lower = text.lower()

        # Pattern matching for common error types
        if any(word in text_lower for word in ["timeout", "connection", "network"]):
            error_type = "transient"
            recovery = "retry"
        elif any(
            word in text_lower
            for word in ["auth", "permission", "forbidden", "401", "403"]
        ):
            error_type = "auth"
            recovery = "refresh_credentials"
        elif any(word in text_lower for word in ["not found", "404", "missing"]):
            error_type = "not_found"
            recovery = "check_inputs"
        elif any(word in text_lower for word in ["rate limit", "429", "quota"]):
            error_type = "rate_limit"
            recovery = "backoff"
        else:
            error_type = "unknown"
            recovery = "manual_intervention"

        return ParseResult[dict[str, Any]](
            success=True,
            value={
                "error_type": error_type,
                "recovery": recovery,
                "details": text,
                "confidence_level": "heuristic",
            },
            confidence=0.6,  # Heuristic classification
            strategy="error-heuristic",
        )

    def _classify_error(self, error_data: dict[str, Any]) -> dict[str, Any]:
        """Classify error from structured data."""
        # Check for status code
        code = (
            error_data.get("code")
            or error_data.get("status_code")
            or error_data.get("status")
        )
        message = (
            error_data.get("error")
            or error_data.get("message")
            or error_data.get("details", "")
        )

        if isinstance(code, (int, str)):
            try:
                code_int = int(code)

                if code_int == 429:
                    return {
                        "error_type": "rate_limit",
                        "recovery": "backoff",
                        "details": message,
                    }
                elif 500 <= code_int < 600:
                    return {
                        "error_type": "server_error",
                        "recovery": "retry",
                        "details": message,
                    }
                elif code_int in (401, 403):
                    return {
                        "error_type": "auth",
                        "recovery": "refresh_credentials",
                        "details": message,
                    }
                elif code_int == 404:
                    return {
                        "error_type": "not_found",
                        "recovery": "check_inputs",
                        "details": message,
                    }
                elif code_int == 400:
                    return {
                        "error_type": "bad_request",
                        "recovery": "validate_inputs",
                        "details": message,
                    }
            except ValueError:
                pass

        # Fallback to message-based classification
        raw_result = self._classify_raw_error(message)
        return (
            raw_result.value
            if raw_result.value is not None
            else {
                "error_type": "unknown",
                "recovery": "manual_intervention",
                "details": message,
            }
        )

    def parse_stream(
        self, tokens: Iterator[str]
    ) -> Iterator[ParseResult[dict[str, Any]]]:
        """Stream parsing."""
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config_updates: Any) -> "ErrorParser":
        """Return new parser with updated configuration."""
        new_config = ParserConfig(**{**self.config.__dict__, **config_updates})
        return ErrorParser(config=new_config)


# Convenience constructors


def create_tgent_schema_parser() -> SchemaParser:
    """Create parser for MCP tool schemas."""
    return SchemaParser(config=ParserConfig(min_confidence=0.7, allow_partial=False))


def create_tgent_input_parser(parameter_names: list[str]) -> InputParser:
    """
    Create parser for tool inputs.

    Args:
        parameter_names: Expected parameter names for anchor-based extraction
    """
    return InputParser(
        parameter_names=parameter_names,
        config=ParserConfig(min_confidence=0.6, allow_partial=True),
    )


def create_tgent_output_parser(expected_type: Optional[str] = None) -> OutputParser:
    """Create parser for tool outputs."""
    return OutputParser(
        expected_type=expected_type,
        config=ParserConfig(min_confidence=0.6, allow_partial=True),
    )


def create_tgent_error_parser() -> ErrorParser:
    """Create parser for tool errors with recovery classification."""
    return ErrorParser(config=ParserConfig(min_confidence=0.5, allow_partial=True))
