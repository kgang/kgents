"""
Tests for IncrementalParser (Strategy 2.3)

Tests:
- Complete JSON parsing (fast path)
- Partial JSON parsing (incomplete structures)
- Stream parsing (progressive AST building)
- Confidence scoring (based on completeness)
- Node counting and metadata
"""

import pytest
from agents.p.strategies.incremental import (
    IncrementalNode,
    IncrementalParser,
    incremental_json_parser,
)


class TestIncrementalParserComplete:
    """Test complete JSON parsing (fast path)."""

    def test_parse_complete_object(self):
        parser = IncrementalParser()
        text = '{"name": "Alice", "age": 30}'

        result = parser.parse(text)

        assert result.success
        assert result.confidence == 1.0
        assert result.value.type == "object"
        assert result.value.complete
        assert len(result.value.children) == 2
        assert result.metadata["complete"] is True
        assert result.strategy == "incremental-complete"

    def test_parse_complete_array(self):
        parser = IncrementalParser()
        text = "[1, 2, 3, 4, 5]"

        result = parser.parse(text)

        assert result.success
        assert result.confidence == 1.0
        assert result.value.type == "array"
        assert result.value.complete
        assert len(result.value.children) == 5

    def test_parse_nested_structure(self):
        parser = IncrementalParser()
        text = '{"user": {"name": "Bob", "age": 25}, "active": true}'

        result = parser.parse(text)

        assert result.success
        assert result.confidence == 1.0
        assert result.value.type == "object"
        assert len(result.value.children) == 2

        # Check nested object
        user_child = result.value.children[0]
        assert user_child.type == "object"
        assert user_child.complete
        assert len(user_child.children) == 2


class TestIncrementalParserPartial:
    """Test partial JSON parsing (incomplete structures)."""

    def test_parse_unclosed_object(self):
        parser = IncrementalParser()
        text = '{"name": "Alice", "age": 30'

        result = parser.parse(text)

        assert result.success
        assert result.confidence < 1.0
        assert result.partial
        assert result.value.type == "object"
        assert not result.value.complete
        assert result.metadata["complete"] is False
        assert result.metadata["incomplete_nodes"] > 0

    def test_parse_unclosed_array(self):
        parser = IncrementalParser()
        text = "[1, 2, 3"

        result = parser.parse(text)

        assert result.success
        assert result.partial
        assert result.value.type == "array"
        assert not result.value.complete

    def test_parse_incomplete_string(self):
        parser = IncrementalParser()
        text = '{"name": "Ali'

        result = parser.parse(text)

        assert result.success
        assert result.partial
        assert result.value.type == "object"
        # Should have one child (name field)
        assert len(result.value.children) >= 0

    def test_parse_empty_string(self):
        parser = IncrementalParser()
        text = ""

        result = parser.parse(text)

        assert result.success
        assert result.value.type == "incomplete"
        assert result.confidence == 0.1  # Minimum non-zero confidence


class TestIncrementalParserStream:
    """Test stream parsing (progressive AST building)."""

    def test_stream_complete_object(self):
        parser = IncrementalParser()
        tokens = ['{"na', 'me": ', '"Alice"', ', "age":', " 30}"]

        results = list(parser.parse_stream(iter(tokens)))

        # Should get multiple partial results, then final complete
        assert len(results) > 0

        # Check final result
        final = results[-1]
        assert final.success
        assert final.confidence == 1.0
        assert not final.partial
        assert final.value.type == "object"
        assert final.value.complete

    def test_stream_progressive_confidence(self):
        parser = IncrementalParser()
        tokens = ["[1", ", 2", ", 3]"]

        results = list(parser.parse_stream(iter(tokens)))

        # Confidence should increase as more data arrives
        confidences = [r.confidence for r in results]

        # Earlier results should have lower confidence
        assert confidences[0] < confidences[-1]
        # Final result should be confident
        assert confidences[-1] == 1.0

    def test_stream_metadata_tracking(self):
        parser = IncrementalParser()
        tokens = ['{"a":', " 1, ", '"b": 2}']

        results = list(parser.parse_stream(iter(tokens)))

        # Check stream position increases
        positions = [r.stream_position for r in results]
        assert all(positions[i] < positions[i + 1] for i in range(len(positions) - 1))

        # Check node count increases
        for result in results:
            assert "node_count" in result.metadata


class TestIncrementalNode:
    """Test IncrementalNode functionality."""

    def test_node_to_dict(self):
        node = IncrementalNode(
            type="object",
            value={"key": "value"},
            complete=True,
            confidence=1.0,
        )

        d = node.to_dict()

        assert d["type"] == "object"
        assert d["value"] == {"key": "value"}
        assert d["complete"] is True
        assert d["confidence"] == 1.0

    def test_node_with_children(self):
        child1 = IncrementalNode(
            type="string", value="Alice", complete=True, confidence=1.0, key="name"
        )
        child2 = IncrementalNode(
            type="number", value=30, complete=True, confidence=1.0, key="age"
        )

        parent = IncrementalNode(
            type="object",
            value={},
            complete=True,
            confidence=1.0,
            children=[child1, child2],
        )

        assert len(parent.children) == 2
        assert parent.children[0].key == "name"
        assert parent.children[1].key == "age"


class TestIncrementalParserConfidence:
    """Test confidence scoring."""

    def test_complete_has_max_confidence(self):
        parser = IncrementalParser()
        result = parser.parse('{"complete": true}')

        assert result.confidence == 1.0

    def test_incomplete_has_reduced_confidence(self):
        parser = IncrementalParser()
        result = parser.parse('{"incomplete": ')

        assert result.confidence < 1.0
        assert result.confidence > 0.0

    def test_empty_has_minimum_confidence(self):
        parser = IncrementalParser()
        result = parser.parse("")

        assert result.confidence == 0.1  # Minimum non-zero confidence for empty input


class TestIncrementalParserMetadata:
    """Test metadata tracking."""

    def test_node_count_metadata(self):
        parser = IncrementalParser()
        result = parser.parse('{"a": 1, "b": 2, "c": 3}')

        assert "node_count" in result.metadata
        # 1 object + 3 children = 4 nodes
        assert result.metadata["node_count"] >= 4

    def test_incomplete_nodes_metadata(self):
        parser = IncrementalParser()
        result = parser.parse('{"incomplete": ')

        assert "incomplete_nodes" in result.metadata
        assert result.metadata["incomplete_nodes"] > 0

    def test_parse_error_metadata(self):
        parser = IncrementalParser()
        result = parser.parse('{"malformed"')

        assert "parse_error" in result.metadata


class TestIncrementalParserEdgeCases:
    """Test edge cases."""

    def test_parse_primitive_types(self):
        parser = IncrementalParser()

        # Number
        result = parser.parse("42")
        assert result.success
        assert result.value.type == "number"
        assert result.value.value == 42

        # String
        result = parser.parse('"hello"')
        assert result.success
        assert result.value.type == "string"

        # Boolean
        result = parser.parse("true")
        assert result.success
        assert result.value.type == "boolean"

        # Null
        result = parser.parse("null")
        assert result.success
        assert result.value.type == "null"

    def test_parse_deeply_nested(self):
        parser = IncrementalParser()
        text = '{"level1": {"level2": {"level3": {"value": 42}}}}'

        result = parser.parse(text)

        assert result.success
        assert result.confidence == 1.0
        # Should build complete nested structure
        assert result.value.type == "object"

    def test_parse_array_of_objects(self):
        parser = IncrementalParser()
        text = '[{"name": "Alice"}, {"name": "Bob"}]'

        result = parser.parse(text)

        assert result.success
        assert result.value.type == "array"
        assert len(result.value.children) == 2


class TestIncrementalParserConfiguration:
    """Test parser configuration."""

    def test_configure_returns_new_parser(self):
        parser = IncrementalParser()
        new_parser = parser.configure(min_confidence=0.8)

        assert isinstance(new_parser, IncrementalParser)
        assert new_parser is not parser

    def test_convenience_constructor(self):
        parser = incremental_json_parser()

        assert isinstance(parser, IncrementalParser)
        result = parser.parse('{"test": true}')
        assert result.success


class TestIncrementalParserRepairs:
    """Test repair tracking."""

    def test_partial_parse_has_repairs(self):
        parser = IncrementalParser()
        result = parser.parse('{"incomplete": ')

        assert len(result.repairs) > 0
        assert "partial" in result.repairs[0].lower()

    def test_complete_parse_no_repairs(self):
        parser = IncrementalParser()
        result = parser.parse('{"complete": true}')

        assert len(result.repairs) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
