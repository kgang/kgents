"""
Tests for AnchorBasedParser (Strategy 4.2 - Islands of Stability).
"""

import pytest
from agents.p.strategies.anchor import (
    AnchorBasedParser,
    hypothesis_parser,
    behavior_parser,
    constraint_parser,
)


class TestAnchorBasedParser:
    """Test anchor-based parsing strategy."""

    def test_simple_anchored_list(self):
        """Parse simple anchored list."""
        parser = AnchorBasedParser(anchor="###ITEM:")
        text = """
        ###ITEM: First item
        ###ITEM: Second item
        ###ITEM: Third item
        """

        result = parser.parse(text)

        assert result.success
        assert result.value == ["First item", "Second item", "Third item"]
        assert result.confidence == 0.9
        assert result.strategy == "anchor-based"
        assert result.metadata["items_count"] == 3

    def test_ignores_conversational_filler(self):
        """Anchor parser ignores conversational filler."""
        parser = AnchorBasedParser(anchor="###ITEM:")
        text = """
        Sure, here's your list! Let me format it nicely:

        ###ITEM: First hypothesis
        ###ITEM: Second hypothesis
        ###ITEM: Third hypothesis

        Hope this helps!
        """

        result = parser.parse(text)

        assert result.success
        assert result.value == [
            "First hypothesis",
            "Second hypothesis",
            "Third hypothesis",
        ]

    def test_ignores_malformed_structure(self):
        """Anchor parser ignores malformed JSON/XML."""
        parser = AnchorBasedParser(anchor="###ITEM:")
        text = """
        {
          "items": [  // Malformed JSON starts here
        ###ITEM: First hypothesis
        ###ITEM: Second hypothesis
        ###ITEM: Third hypothesis
          ]  // Missing closing brace

        Hope this helps!
        """

        result = parser.parse(text)

        assert result.success
        assert result.value == [
            "First hypothesis",
            "Second hypothesis",
            "Third hypothesis",
        ]
        assert result.confidence == 0.9

    def test_no_anchors_found(self):
        """Failure when no anchors found."""
        parser = AnchorBasedParser(anchor="###ITEM:")
        text = "This text has no anchors"

        result = parser.parse(text)

        assert not result.success
        assert "No anchors" in result.error

    def test_empty_items_filtered(self):
        """Empty items are filtered out."""
        parser = AnchorBasedParser(anchor="###ITEM:")
        text = """
        ###ITEM: First item
        ###ITEM:
        ###ITEM: Third item
        """

        result = parser.parse(text)

        assert result.success
        assert result.value == ["First item", "Third item"]
        assert result.metadata["items_count"] == 2

    def test_custom_extractor(self):
        """Custom extractor transforms items."""

        def extract_int(text: str) -> int:
            return int(text.strip())

        parser = AnchorBasedParser(anchor="###NUM:", extractor=extract_int)
        text = """
        ###NUM: 42
        ###NUM: 100
        ###NUM: 256
        """

        result = parser.parse(text)

        assert result.success
        assert result.value == [42, 100, 256]

    def test_extractor_failure(self):
        """Extractor failure returns error with raw items."""

        def extract_int(text: str) -> int:
            return int(text.strip())

        parser = AnchorBasedParser(anchor="###NUM:", extractor=extract_int)
        text = """
        ###NUM: not a number
        """

        result = parser.parse(text)

        assert not result.success
        assert "Extractor failed" in result.error
        assert "not a number" in result.metadata["raw_items"][0]

    def test_stream_parsing(self):
        """Anchor parser supports streaming."""
        parser = AnchorBasedParser(anchor="###ITEM:")

        tokens = [
            "###ITEM: First item\n",
            "###ITEM: Second item\n",
            "###ITEM: Third item\n",
        ]

        results = list(parser.parse_stream(iter(tokens)))

        # Should get intermediate results and final result
        assert len(results) >= 1

        # Final result should have all items
        final = results[-1]
        assert final.success
        assert len(final.value) == 3
        assert not final.partial

    def test_stream_parsing_incomplete(self):
        """Stream parsing handles incomplete items."""
        parser = AnchorBasedParser(anchor="###ITEM:")

        tokens = [
            "###ITEM: Complete item\n",
            "###ITEM: Incomplete",
        ]

        results = list(parser.parse_stream(iter(tokens)))

        # Should have at least one result
        assert len(results) >= 1

        # Last result should have complete items only
        final = results[-1]
        if final.success:
            assert "Complete item" in final.value


class TestConvenienceParsers:
    """Test convenience constructor functions."""

    def test_hypothesis_parser(self):
        """Hypothesis parser uses correct anchor."""
        parser = hypothesis_parser()
        text = """
        ###HYPOTHESIS: The system exhibits chaotic behavior
        ###HYPOTHESIS: Load increases with user count
        """

        result = parser.parse(text)

        assert result.success
        assert len(result.value) == 2
        assert "chaotic behavior" in result.value[0]

    def test_behavior_parser(self):
        """Behavior parser uses correct anchor."""
        parser = behavior_parser()
        text = """
        ###BEHAVIOR: Sorts list in ascending order
        ###BEHAVIOR: Returns empty list for empty input
        """

        result = parser.parse(text)

        assert result.success
        assert len(result.value) == 2
        assert "Sorts list" in result.value[0]

    def test_constraint_parser(self):
        """Constraint parser uses correct anchor."""
        parser = constraint_parser()
        text = """
        ###CONSTRAINT: Input must be non-negative
        ###CONSTRAINT: Output must be deterministic
        """

        result = parser.parse(text)

        assert result.success
        assert len(result.value) == 2
        assert "non-negative" in result.value[0]


class TestAnchorParserConfiguration:
    """Test anchor parser configuration."""

    def test_configure_returns_new_instance(self):
        """Configure returns new parser instance."""
        parser = AnchorBasedParser(anchor="###ITEM:")
        new_parser = parser.configure(min_confidence=0.9)

        assert new_parser.config.min_confidence == 0.9
        assert parser.config.min_confidence == 0.5  # Original unchanged

    def test_configure_validation(self):
        """Configure validates new config."""
        parser = AnchorBasedParser(anchor="###ITEM:")

        with pytest.raises(ValueError, match="min_confidence must be in"):
            parser.configure(min_confidence=2.0)

    def test_configured_parser_works(self):
        """Configured parser still works correctly."""
        parser = AnchorBasedParser(anchor="###ITEM:")
        parser = parser.configure(min_confidence=0.95, allow_partial=False)

        text = "###ITEM: Test item"
        result = parser.parse(text)

        assert result.success
        assert result.value == ["Test item"]
