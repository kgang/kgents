"""
Tests for LazyValidationParser (Strategy 2.4)

Tests:
- Lazy field validation (deferred until access)
- Type coercion on access
- Custom coercers
- Missing field handling
- Extra field tolerance
- Validation error propagation
"""

import pytest
from agents.p.strategies.lazy_validation import (
    LazyValidationParser,
    LazyValidatedDict,
    lazy_validation_parser,
    datetime_coercer,
    list_of_strings_coercer,
)


class TestLazyValidatedDict:
    """Test LazyValidatedDict core functionality."""

    def test_basic_access(self):
        raw = {"name": "Alice", "age": "30"}
        schema = {"name": str, "age": int}

        lazy = LazyValidatedDict(raw, schema)

        # Access should validate on first access
        assert lazy["name"] == "Alice"
        assert lazy["age"] == 30  # Coerced from string

    def test_lazy_validation_deferred(self):
        raw = {"valid": "ok", "invalid": "not_a_number"}
        schema = {"valid": str, "invalid": int}

        lazy = LazyValidatedDict(raw, schema)

        # Accessing valid field should work
        assert lazy["valid"] == "ok"

        # Invalid field should only error when accessed
        with pytest.raises(KeyError, match="validation failed"):
            _ = lazy["invalid"]

    def test_type_coercion(self):
        raw = {
            "as_float": "3.14",
            "as_int": "42",
            "as_bool_true": "true",
            "as_bool_false": "false",
        }
        schema = {
            "as_float": float,
            "as_int": int,
            "as_bool_true": bool,
            "as_bool_false": bool,
        }

        lazy = LazyValidatedDict(raw, schema)

        assert lazy["as_float"] == 3.14
        assert lazy["as_int"] == 42
        assert lazy["as_bool_true"] is True
        assert lazy["as_bool_false"] is False

    def test_get_with_default(self):
        raw = {"exists": "value"}
        schema = {"exists": str, "missing": str}

        lazy = LazyValidatedDict(raw, schema)

        assert lazy.get("exists") == "value"
        assert lazy.get("missing") is None
        assert lazy.get("missing", "default") == "default"

    def test_contains(self):
        raw = {"exists": "value"}
        schema = {"exists": str, "missing": str}

        lazy = LazyValidatedDict(raw, schema)

        assert "exists" in lazy
        assert "missing" not in lazy

    def test_keys(self):
        raw = {"a": 1, "b": 2, "c": 3}
        schema = {"a": int, "b": int, "c": int}

        lazy = LazyValidatedDict(raw, schema)

        keys = list(lazy.keys())
        assert "a" in keys
        assert "b" in keys
        assert "c" in keys

    def test_caching(self):
        raw = {"field": "42"}
        schema = {"field": int}

        lazy = LazyValidatedDict(raw, schema)

        # First access validates
        val1 = lazy["field"]
        # Second access uses cache
        val2 = lazy["field"]

        assert val1 == val2 == 42

    def test_access_log(self):
        raw = {"a": 1, "b": 2, "c": 3}
        schema = {"a": int, "b": int, "c": int}

        lazy = LazyValidatedDict(raw, schema)

        # Access some fields
        _ = lazy["a"]
        _ = lazy["b"]
        _ = lazy["a"]  # Access again

        log = lazy.access_log()
        assert log == ["a", "b", "a"]

    def test_to_dict(self):
        raw = {"name": "Alice", "age": "30"}
        schema = {"name": str, "age": int}

        lazy = LazyValidatedDict(raw, schema)

        d = lazy.to_dict()

        assert d["name"] == "Alice"
        assert d["age"] == 30
        assert isinstance(d, dict)


class TestLazyValidatedDictCoercers:
    """Test custom coercers."""

    def test_custom_coercer(self):
        raw = {"doubled": "21"}

        def double_coercer(value):
            return int(value) * 2

        lazy = LazyValidatedDict(
            raw,
            schema={"doubled": int},
            coercers={"doubled": double_coercer},
        )

        assert lazy["doubled"] == 42

    def test_datetime_coercer(self):
        raw = {"date": "2025-12-09"}
        schema = {"date": str}  # Type hint is str, but coercer handles datetime

        lazy = LazyValidatedDict(
            raw,
            schema=schema,
            coercers={"date": datetime_coercer},
        )

        from datetime import datetime

        result = lazy["date"]
        assert isinstance(result, datetime)
        assert result.year == 2025
        assert result.month == 12
        assert result.day == 9

    def test_list_of_strings_coercer_from_list(self):
        raw = {"items": [1, 2, 3]}
        schema = {"items": list}

        lazy = LazyValidatedDict(
            raw,
            schema=schema,
            coercers={"items": list_of_strings_coercer},
        )

        assert lazy["items"] == ["1", "2", "3"]

    def test_list_of_strings_coercer_from_csv(self):
        raw = {"items": "a, b, c"}
        schema = {"items": list}

        lazy = LazyValidatedDict(
            raw,
            schema=schema,
            coercers={"items": list_of_strings_coercer},
        )

        assert lazy["items"] == ["a", "b", "c"]


class TestLazyValidationParser:
    """Test LazyValidationParser."""

    def test_parse_valid_json(self):
        schema = {"name": str, "age": int}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"name": "Alice", "age": "30"}')

        assert result.success
        assert isinstance(result.value, LazyValidatedDict)
        assert result.value["name"] == "Alice"
        assert result.value["age"] == 30

    def test_parse_with_extra_fields(self):
        schema = {"name": str}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"name": "Alice", "extra": "ignored"}')

        assert result.success
        assert len(result.repairs) > 0
        assert "extra" in result.repairs[0].lower()
        assert result.metadata["extra_fields"] == 1

    def test_parse_with_missing_fields(self):
        schema = {"name": str, "age": int}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"name": "Alice"}')

        assert result.success
        # Should warn about missing fields
        assert result.metadata["missing_fields"] == 1

        # Accessing missing field should error
        with pytest.raises(KeyError):
            _ = result.value["age"]

    def test_parse_invalid_json(self):
        schema = {"name": str}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"name": "Alice"')

        assert not result.success
        assert "JSON parse error" in result.error

    def test_parse_non_object(self):
        schema = {"name": str}
        parser = LazyValidationParser(schema)

        result = parser.parse("[1, 2, 3]")

        assert not result.success
        assert "Expected JSON object" in result.error

    def test_confidence_based_on_field_coverage(self):
        schema = {"a": int, "b": int, "c": int}
        parser = LazyValidationParser(schema)

        # Full coverage
        result1 = parser.parse('{"a": 1, "b": 2, "c": 3}')
        assert result1.confidence == 1.0

        # Partial coverage (2/3 fields)
        result2 = parser.parse('{"a": 1, "b": 2}')
        assert result2.confidence < 1.0
        assert result2.confidence > 0.5


class TestLazyValidationParserConfiguration:
    """Test parser configuration."""

    def test_configure_returns_new_parser(self):
        schema = {"name": str}
        parser = LazyValidationParser(schema)
        new_parser = parser.configure(min_confidence=0.8)

        assert isinstance(new_parser, LazyValidationParser)
        assert new_parser is not parser

    def test_convenience_constructor(self):
        schema = {"name": str, "age": int}
        parser = lazy_validation_parser(schema)

        assert isinstance(parser, LazyValidationParser)
        result = parser.parse('{"name": "Alice", "age": "30"}')
        assert result.success


class TestLazyValidationParserMetadata:
    """Test metadata tracking."""

    def test_metadata_field_counts(self):
        schema = {"required": str}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"required": "ok", "extra1": "x", "extra2": "y"}')

        assert result.metadata["total_fields"] == 3
        assert result.metadata["schema_fields"] == 1
        assert result.metadata["extra_fields"] == 2
        assert result.metadata["missing_fields"] == 0

    def test_metadata_field_coverage(self):
        schema = {"a": int, "b": int}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"a": 1}')

        assert result.metadata["field_coverage"] == 0.5


class TestLazyValidationParserEdgeCases:
    """Test edge cases."""

    def test_empty_schema(self):
        schema = {}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"anything": "goes"}')

        assert result.success
        # No schema fields to validate

    def test_empty_data(self):
        schema = {"required": str}
        parser = LazyValidationParser(schema)

        result = parser.parse("{}")

        assert result.success
        assert result.metadata["missing_fields"] == 1

    def test_null_values(self):
        schema = {"nullable": str}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"nullable": null}')

        assert result.success
        # Accessing should raise validation error (can't coerce None to str)
        with pytest.raises(KeyError, match="validation failed"):
            _ = result.value["nullable"]

    def test_nested_objects_not_deeply_validated(self):
        schema = {"user": dict}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"user": {"name": "Alice", "age": 30}}')

        assert result.success
        user = result.value["user"]
        assert isinstance(user, dict)
        assert user["name"] == "Alice"


class TestLazyValidationParserRepairs:
    """Test repair tracking."""

    def test_repairs_for_extra_fields(self):
        schema = {"expected": str}
        parser = LazyValidationParser(schema)

        result = parser.parse('{"expected": "ok", "extra": "x"}')

        assert len(result.repairs) > 0
        assert any("extra" in r.lower() for r in result.repairs)

    def test_repairs_for_missing_fields(self):
        schema = {"required": str}
        parser = LazyValidationParser(schema)

        result = parser.parse("{}")

        assert len(result.repairs) > 0
        assert any("missing" in r.lower() for r in result.repairs)


class TestLazyValidationParserStream:
    """Test stream parsing."""

    def test_parse_stream_buffers_and_parses(self):
        schema = {"name": str}
        parser = LazyValidationParser(schema)

        tokens = ['{"na', 'me": ', '"Alice"}']
        results = list(parser.parse_stream(iter(tokens)))

        assert len(results) == 1
        assert results[0].success
        assert results[0].value["name"] == "Alice"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
