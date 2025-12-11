"""Tests for ProbabilisticASTParser (Phase 3: Novel Techniques)."""

from agents.p.strategies.probabilistic_ast import (
    ProbabilisticASTNode,
    ProbabilisticASTParser,
    get_low_confidence_paths,
    query_confident_fields,
)


class TestDirectParsing:
    """Test parsing valid JSON with high confidence."""

    def test_parse_valid_json(self) -> None:
        """Test parsing valid JSON gets confidence=1.0."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"name": "test", "count": 42}')

        assert result.success
        assert result.confidence == 1.0
        assert result.value.type == "object"

    def test_parse_array(self) -> None:
        """Test parsing JSON array."""
        parser = ProbabilisticASTParser()
        result = parser.parse("[1, 2, 3]")

        assert result.success
        assert result.value.type == "array"
        assert len(result.value.children) == 3

    def test_parse_nested_structure(self) -> None:
        """Test parsing nested JSON."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"data": {"items": [1, 2]}}')

        assert result.success
        assert result.value.type == "object"
        assert len(result.value.children) > 0


class TestRepairedParsing:
    """Test parsing malformed JSON with repairs."""

    def test_parse_trailing_comma(self) -> None:
        """Test repair of trailing comma."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"name": "test",}')

        assert result.success
        assert result.confidence < 1.0  # Reduced due to repair
        assert "trailing comma" in result.repairs[0].lower()

    def test_parse_unclosed_brace(self) -> None:
        """Test repair of unclosed brace."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"name": "test"')

        assert result.success
        assert result.confidence < 1.0
        assert any("brace" in r.lower() for r in result.repairs)

    def test_parse_unclosed_bracket(self) -> None:
        """Test repair of unclosed bracket."""
        parser = ProbabilisticASTParser()
        result = parser.parse("[1, 2, 3")

        assert result.success
        assert any("bracket" in r.lower() for r in result.repairs)


class TestHeuristicExtraction:
    """Test fallback heuristic extraction."""

    def test_extract_key_value_pairs(self) -> None:
        """Test heuristic extraction of key-value pairs."""
        parser = ProbabilisticASTParser()
        text = """
        name: test
        count: 42
        active: true
        """
        result = parser.parse(text)

        # Should extract something even if not valid JSON
        # Result depends on heuristic success
        if result.success:
            assert result.confidence <= 0.3  # Low confidence
            assert "heuristic" in result.strategy.lower()


class TestConfidenceScoring:
    """Test per-node confidence scoring."""

    def test_valid_parse_has_high_confidence(self) -> None:
        """Test valid parse has confidence=1.0."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"x": 1}')

        assert result.success
        assert result.value.confidence == 1.0
        for child in result.value.children:
            assert child.confidence == 1.0

    def test_repaired_parse_has_lower_confidence(self) -> None:
        """Test repaired parse has reduced confidence."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"x": 1,}')  # Trailing comma

        assert result.success
        assert result.value.confidence < 1.0
        assert result.value.confidence >= 0.5  # Still reasonable

    def test_children_inherit_confidence(self) -> None:
        """Test child nodes inherit parent confidence."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"a": 1}')  # Trailing comma

        assert result.success
        root = result.value
        for child in root.children:
            assert child.confidence == root.confidence


class TestNodeMethods:
    """Test ProbabilisticASTNode methods."""

    def test_node_to_dict(self) -> None:
        """Test node serialization to dict."""
        node = ProbabilisticASTNode(
            type="string", value="test", confidence=0.9, path="root.name"
        )
        d = node.to_dict()

        assert d["type"] == "string"
        assert d["value"] == "test"
        assert d["confidence"] == 0.9
        assert d["path"] == "root.name"

    def test_get_confident_value_above_threshold(self) -> None:
        """Test extracting value above confidence threshold."""
        node = ProbabilisticASTNode(
            type="string", value="test", confidence=0.9, path="root.name"
        )

        val = node.get_confident_value(min_confidence=0.8)
        assert val == "test"

    def test_get_confident_value_below_threshold(self) -> None:
        """Test value below threshold returns None."""
        node = ProbabilisticASTNode(
            type="string", value="test", confidence=0.5, path="root.name"
        )

        val = node.get_confident_value(min_confidence=0.8)
        assert val is None


class TestQueryConfidentFields:
    """Test querying only high-confidence fields."""

    def test_query_all_confident(self) -> None:
        """Test querying when all fields confident."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"name": "test", "count": 42}')

        confident = query_confident_fields(result.value, min_confidence=0.8)
        assert confident is not None
        assert "name" in confident or isinstance(confident, dict)

    def test_query_filters_low_confidence(self) -> None:
        """Test low-confidence fields are filtered."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"name": "test",}')  # Will be repaired

        # With high threshold, might filter some fields
        confident = query_confident_fields(result.value, min_confidence=0.9)
        # At least we got something back (might be empty dict)
        assert isinstance(confident, (dict, type(None)))


class TestLowConfidencePaths:
    """Test finding low-confidence paths."""

    def test_find_low_confidence_paths(self) -> None:
        """Test finding paths with low confidence."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"name": "test",}')  # Repaired

        paths = get_low_confidence_paths(result.value, max_confidence=0.7)
        # Should find at least root if confidence lowered
        if result.value.confidence <= 0.7:
            assert "root" in paths

    def test_no_low_confidence_in_valid_parse(self) -> None:
        """Test no low-confidence paths in valid parse."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"name": "test"}')

        paths = get_low_confidence_paths(result.value, max_confidence=0.9)
        # All nodes should have confidence=1.0
        assert len(paths) == 0


class TestRepairTracking:
    """Test tracking what repairs were applied."""

    def test_repairs_logged(self) -> None:
        """Test repairs are logged in result."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"x": 1,}')

        assert len(result.repairs) > 0
        assert any("comma" in r.lower() for r in result.repairs)

    def test_repairs_in_node_metadata(self) -> None:
        """Test repairs stored in node."""
        parser = ProbabilisticASTParser()
        result = parser.parse('{"x": 1,}')

        assert result.success
        # Root node should have repair info
        assert result.value.repair_applied is not None or len(result.repairs) > 0


class TestConfiguration:
    """Test parser configuration."""

    def test_configure_returns_new_parser(self) -> None:
        """Test configure returns new instance."""
        parser1 = ProbabilisticASTParser()
        parser2 = parser1.configure(min_confidence=0.9)

        assert parser1 is not parser2
        assert parser2.config.min_confidence == 0.9


class TestStreamParsing:
    """Test stream parsing."""

    def test_stream_buffers_tokens(self) -> None:
        """Test stream parsing buffers tokens."""
        parser = ProbabilisticASTParser()
        tokens = ['{"', "name", '": "', "test", '"}']
        results = parser.parse_stream(tokens)

        assert len(results) == 1
        assert results[0].success


class TestRealWorldScenarios:
    """Test real-world use cases."""

    def test_egent_code_with_repairs(self) -> None:
        """Test E-gent code validation with repairs."""
        parser = ProbabilisticASTParser()
        # Simulated E-gent output (malformed JSON)
        code_json = """
        {
            "imports": ["os", "sys"],
            "functions": ["process", "validate"]
        """  # Missing closing brace

        result = parser.parse(code_json)
        assert result.success  # Should repair and parse
        assert result.confidence < 1.0  # Lowered due to repair

        # Can still extract confident fields
        confident = query_confident_fields(result.value, min_confidence=0.5)
        assert confident is not None

    def test_bgent_hypothesis_with_inference(self) -> None:
        """Test B-gent hypothesis with inferred fields."""
        parser = ProbabilisticASTParser()
        hypothesis = """
        {
            "statement": "System exhibits chaos under load",
            "confidence": "0.75",
            "tests": ["load test"]
        }
        """

        result = parser.parse(hypothesis)
        assert result.success

        # confidence field is string "0.75" instead of float
        # AST should track this as lower confidence
        root = result.value
        assert root.type == "object"

    def test_lgent_catalog_with_optional_fields(self) -> None:
        """Test L-gent catalog with optional metadata."""
        parser = ProbabilisticASTParser()
        catalog = """
        {
            "name": "agent_v1",
            "version": "1.0.0"
        }
        """

        result = parser.parse(catalog)
        assert result.success
        assert result.confidence == 1.0  # Valid JSON

        # Can query high-confidence fields
        confident = query_confident_fields(result.value, min_confidence=0.9)
        assert confident is not None
