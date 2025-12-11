"""
Tests for StructuralDecouplingParser (Strategy 2.2 / Jsonformer)

Tests:
- Structural control by parser
- LLM value generation
- Type coercion for different field types
- Schema conformance guarantees
- Mock LLM testing
- Field validation
"""

import pytest
from agents.p.strategies.structural_decoupling import (
    StructuralDecouplingParser,
    StructuredField,
    field_with_prompt,
    mock_llm_generate,
    simple_schema,
    structural_decoupling_parser,
)


class TestStructuralDecouplingParser:
    """Test StructuralDecouplingParser core functionality."""

    def test_parse_generates_structure(self):
        schema = {
            "title": StructuredField(name="title", type="string"),
            "count": StructuredField(name="count", type="number"),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)

        result = parser.parse("Generate a document")

        assert result.success
        assert isinstance(result.value, dict)
        assert "title" in result.value
        assert "count" in result.value

    def test_guaranteed_structure(self):
        schema = {
            "field1": StructuredField(name="field1", type="string"),
            "field2": StructuredField(name="field2", type="string"),
            "field3": StructuredField(name="field3", type="string"),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)

        result = parser.parse("test")

        # Structure is guaranteed to match schema
        assert len(result.value) == 3
        assert set(result.value.keys()) == {"field1", "field2", "field3"}

    def test_llm_calls_per_field(self):
        call_count = 0

        def counting_llm(prompt: str) -> str:
            nonlocal call_count
            call_count += 1
            return "value"

        schema = {
            "a": StructuredField(name="a", type="string"),
            "b": StructuredField(name="b", type="string"),
            "c": StructuredField(name="c", type="string"),
        }

        parser = StructuralDecouplingParser(schema, counting_llm)
        result = parser.parse("test")

        # Should make one LLM call per field
        assert call_count == 3
        assert result.metadata["llm_calls"] == 3


class TestStructuredFieldTypes:
    """Test different field types."""

    def test_string_field(self):
        schema = {
            "text": StructuredField(name="text", type="string"),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)
        result = parser.parse("test")

        assert isinstance(result.value["text"], str)

    def test_number_field(self):
        schema = {
            "count": StructuredField(name="count", type="number"),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)
        result = parser.parse("test")

        assert isinstance(result.value["count"], (int, float))

    def test_boolean_field(self):
        schema = {
            "active": StructuredField(name="active", type="boolean"),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)
        result = parser.parse("test")

        assert isinstance(result.value["active"], bool)

    def test_array_field(self):
        schema = {
            "items": StructuredField(name="items", type="array"),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)
        result = parser.parse("test")

        assert isinstance(result.value["items"], list)

    def test_object_field(self):
        schema = {
            "nested": StructuredField(name="nested", type="object"),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)
        result = parser.parse("test")

        assert isinstance(result.value["nested"], dict)


class TestTypeCoercion:
    """Test type coercion from LLM outputs."""

    def test_coerce_string_removes_quotes(self):
        def llm_with_quotes(prompt: str) -> str:
            return '"quoted value"'

        schema = {"field": StructuredField(name="field", type="string")}
        parser = StructuralDecouplingParser(schema, llm_with_quotes)

        result = parser.parse("test")

        assert result.value["field"] == "quoted value"

    def test_coerce_number_from_string(self):
        def llm_number_string(prompt: str) -> str:
            return "42"

        schema = {"field": StructuredField(name="field", type="number")}
        parser = StructuralDecouplingParser(schema, llm_number_string)

        result = parser.parse("test")

        assert result.value["field"] == 42

    def test_coerce_float_from_string(self):
        def llm_float_string(prompt: str) -> str:
            return "3.14"

        schema = {"field": StructuredField(name="field", type="number")}
        parser = StructuralDecouplingParser(schema, llm_float_string)

        result = parser.parse("test")

        assert result.value["field"] == 3.14

    def test_coerce_boolean_true_variants(self):
        for value in ["true", "True", "yes", "Yes", "1", "t", "y"]:

            def llm_bool(prompt: str) -> str:
                return value

            schema = {"field": StructuredField(name="field", type="boolean")}
            parser = StructuralDecouplingParser(schema, llm_bool)

            result = parser.parse("test")
            assert result.value["field"] is True

    def test_coerce_boolean_false_variants(self):
        for value in ["false", "False", "no", "No", "0", "f", "n"]:

            def llm_bool(prompt: str) -> str:
                return value

            schema = {"field": StructuredField(name="field", type="boolean")}
            parser = StructuralDecouplingParser(schema, llm_bool)

            result = parser.parse("test")
            assert result.value["field"] is False

    def test_coerce_array_from_json(self):
        def llm_json_array(prompt: str) -> str:
            return '["item1", "item2", "item3"]'

        schema = {"field": StructuredField(name="field", type="array")}
        parser = StructuralDecouplingParser(schema, llm_json_array)

        result = parser.parse("test")

        assert result.value["field"] == ["item1", "item2", "item3"]

    def test_coerce_array_from_csv(self):
        def llm_csv(prompt: str) -> str:
            return "a, b, c"

        schema = {"field": StructuredField(name="field", type="array")}
        parser = StructuralDecouplingParser(schema, llm_csv)

        result = parser.parse("test")

        assert result.value["field"] == ["a", "b", "c"]


class TestFieldValidation:
    """Test field validators."""

    def test_field_with_validator_passes(self):
        def validator(value: str) -> bool:
            return len(value) > 5

        schema = {
            "field": StructuredField(
                name="field",
                type="string",
                validator=validator,
            ),
        }

        def llm_long(prompt: str) -> str:
            return "long enough value"

        parser = StructuralDecouplingParser(schema, llm_long)
        result = parser.parse("test")

        assert result.success
        assert result.value["field"] == "long enough value"

    def test_field_with_validator_fails_uses_default(self):
        def validator(value: str) -> bool:
            return len(value) > 100  # Will fail

        schema = {
            "field": StructuredField(
                name="field",
                type="string",
                validator=validator,
            ),
        }

        def llm_short(prompt: str) -> str:
            return "short"

        parser = StructuralDecouplingParser(schema, llm_short)
        result = parser.parse("test")

        assert result.success
        # Should use default value (empty string)
        assert result.value["field"] == ""
        assert len(result.repairs) > 0
        assert "validation" in result.repairs[0].lower()


class TestCustomPrompts:
    """Test custom prompt templates."""

    def test_field_with_custom_prompt(self):
        captured_prompt = None

        def llm_capture(prompt: str) -> str:
            nonlocal captured_prompt
            captured_prompt = prompt
            return "value"

        schema = {
            "field": StructuredField(
                name="field",
                type="string",
                prompt_template="Custom prompt for {field_name}: {context}",
            ),
        }

        parser = StructuralDecouplingParser(schema, llm_capture)
        parser.parse("my context")

        assert "Custom prompt" in captured_prompt
        assert "field" in captured_prompt
        assert "my context" in captured_prompt


class TestConfidenceScoring:
    """Test confidence scoring."""

    def test_successful_coercion_high_confidence(self):
        schema = {"field": StructuredField(name="field", type="string")}
        parser = StructuralDecouplingParser(schema, mock_llm_generate)

        result = parser.parse("test")

        assert result.confidence > 0.9

    def test_failed_validation_reduces_confidence(self):
        def validator(value: str) -> bool:
            return False  # Always fail

        schema = {
            "field": StructuredField(
                name="field",
                type="string",
                validator=validator,
            ),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)
        result = parser.parse("test")

        # Confidence should be reduced due to validation failure
        assert result.confidence < 0.9

    def test_coercion_fallback_reduces_confidence(self):
        def llm_malformed_number(prompt: str) -> str:
            return "not a number at all"

        schema = {"field": StructuredField(name="field", type="number")}
        parser = StructuralDecouplingParser(schema, llm_malformed_number)

        result = parser.parse("test")

        # Should fall back to extracting number or default
        assert result.confidence < 0.9


class TestSchemaBuilders:
    """Test schema builder helpers."""

    def test_simple_schema(self):
        schema = simple_schema(
            name="string",
            age="number",
            active="boolean",
        )

        assert "name" in schema
        assert schema["name"].type == "string"
        assert "age" in schema
        assert schema["age"].type == "number"
        assert "active" in schema
        assert schema["active"].type == "boolean"

    def test_field_with_prompt_builder(self):
        field = field_with_prompt(
            name="hypothesis",
            type="string",
            prompt_template="Generate hypothesis: {context}",
            validator=lambda h: len(h) > 10,
        )

        assert field.name == "hypothesis"
        assert field.type == "string"
        assert field.prompt_template is not None
        assert field.validator is not None


class TestParserConfiguration:
    """Test parser configuration."""

    def test_configure_returns_new_parser(self):
        schema = {"field": StructuredField(name="field", type="string")}
        parser = StructuralDecouplingParser(schema, mock_llm_generate)

        new_parser = parser.configure(min_confidence=0.8)

        assert isinstance(new_parser, StructuralDecouplingParser)
        assert new_parser is not parser

    def test_convenience_constructor(self):
        schema = {"field": StructuredField(name="field", type="string")}
        parser = structural_decoupling_parser(schema, mock_llm_generate)

        assert isinstance(parser, StructuralDecouplingParser)
        result = parser.parse("test")
        assert result.success


class TestParserMetadata:
    """Test metadata tracking."""

    def test_metadata_tracks_field_counts(self):
        schema = {
            "a": StructuredField(name="a", type="string"),
            "b": StructuredField(name="b", type="string"),
            "c": StructuredField(name="c", type="string"),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)
        result = parser.parse("test")

        assert result.metadata["total_fields"] == 3
        assert result.metadata["generated_fields"] == 3
        assert result.metadata["llm_calls"] == 3


class TestErrorHandling:
    """Test error handling."""

    def test_llm_error_uses_default(self):
        def llm_error(prompt: str) -> str:
            raise RuntimeError("LLM failed")

        schema = {"field": StructuredField(name="field", type="string")}
        parser = StructuralDecouplingParser(schema, llm_error)

        result = parser.parse("test")

        assert result.success  # Should still succeed with defaults
        assert result.value["field"] == ""  # Default string
        assert len(result.repairs) > 0

    def test_stream_not_supported(self):
        schema = {"field": StructuredField(name="field", type="string")}
        parser = StructuralDecouplingParser(schema, mock_llm_generate)

        with pytest.raises(NotImplementedError):
            list(parser.parse_stream(iter(["test"])))


class TestMockLLM:
    """Test mock LLM generator."""

    def test_mock_generates_string(self):
        result = mock_llm_generate("Generate a string value for field 'name'")
        assert isinstance(result, str)
        assert "name" in result.lower()

    def test_mock_generates_number(self):
        result = mock_llm_generate("Generate a number value for field 'count'")
        assert result == "42"

    def test_mock_generates_boolean(self):
        result = mock_llm_generate("Generate a boolean value for field 'active'")
        assert result == "true"

    def test_mock_generates_array(self):
        result = mock_llm_generate("Generate an array value for field 'items'")
        assert result.startswith("[")
        assert result.endswith("]")


class TestRepairs:
    """Test repair tracking."""

    def test_repairs_track_validation_failures(self):
        def validator(value: str) -> bool:
            return False

        schema = {
            "field": StructuredField(
                name="field",
                type="string",
                validator=validator,
            ),
        }

        parser = StructuralDecouplingParser(schema, mock_llm_generate)
        result = parser.parse("test")

        assert len(result.repairs) > 0
        assert any("validation" in r.lower() for r in result.repairs)

    def test_repairs_track_generation_failures(self):
        def llm_error(prompt: str) -> str:
            raise RuntimeError("Failed")

        schema = {"field": StructuredField(name="field", type="string")}
        parser = StructuralDecouplingParser(schema, llm_error)

        result = parser.parse("test")

        assert len(result.repairs) > 0
        assert any("generation failed" in r.lower() for r in result.repairs)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
