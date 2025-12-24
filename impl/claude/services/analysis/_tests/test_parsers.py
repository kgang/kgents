"""
Tests for analysis response parsers.

These tests verify that LLM JSON responses are correctly parsed
into typed report dataclasses.
"""

from __future__ import annotations

import pytest

from services.analysis.parsers import (
    extract_json_from_response,
    parse_categorical_response,
    parse_dialectical_response,
    parse_epistemic_response,
    parse_generative_response,
)


class TestJSONExtraction:
    """Test JSON extraction from various response formats."""

    def test_extract_plain_json(self):
        """Plain JSON is returned unchanged."""
        json_str = '{"key": "value"}'
        result = extract_json_from_response(json_str)
        assert result == json_str

    def test_extract_json_wrapped(self):
        """Markdown-wrapped JSON is unwrapped."""
        response = '```json\n{"key": "value"}\n```'
        result = extract_json_from_response(response)
        assert result == '{"key": "value"}'

    def test_extract_json_triple_backticks(self):
        """Triple backticks without language tag."""
        response = '```\n{"key": "value"}\n```'
        result = extract_json_from_response(response)
        assert result == '{"key": "value"}'

    def test_extract_json_with_whitespace(self):
        """Handles leading/trailing whitespace."""
        response = '\n\n  {"key": "value"}  \n\n'
        result = extract_json_from_response(response)
        assert result == '{"key": "value"}'


class TestCategoricalParsing:
    """Test categorical response parsing."""

    def test_parse_valid_categorical(self):
        """Valid categorical response is parsed correctly."""
        response = """
        {
          "laws_extracted": [
            {"name": "identity", "equation": "id >> f = f", "source": "implicit"}
          ],
          "law_verifications": [
            {"law_name": "identity", "status": "STRUCTURAL", "message": "OK"}
          ],
          "fixed_point": {
            "is_self_referential": true,
            "description": "Self-describing",
            "is_valid": true,
            "implications": ["Valid fixed point"]
          },
          "summary": "Analysis complete"
        }
        """
        report = parse_categorical_response(response, "test.md")
        assert report.target == "test.md"
        assert len(report.laws_extracted) == 1
        assert report.laws_extracted[0].name == "identity"
        assert len(report.law_verifications) == 1
        assert report.fixed_point is not None
        assert report.fixed_point.is_self_referential

    def test_parse_categorical_no_fixed_point(self):
        """Categorical response without fixed point."""
        response = """
        {
          "laws_extracted": [],
          "law_verifications": [],
          "summary": "No laws found"
        }
        """
        report = parse_categorical_response(response, "test.md")
        assert report.target == "test.md"
        assert report.fixed_point is None
        assert report.summary == "No laws found"

    def test_parse_invalid_json_returns_error_report(self):
        """Invalid JSON returns error report instead of raising."""
        response = "not valid json"
        report = parse_categorical_response(response, "test.md")
        assert report.target == "test.md"
        assert "Parse error" in report.summary


class TestEpistemicParsing:
    """Test epistemic response parsing."""

    def test_parse_valid_epistemic(self):
        """Valid epistemic response is parsed correctly."""
        response = """
        {
          "layer": 4,
          "toulmin": {
            "claim": "Test claim",
            "grounds": ["Evidence 1", "Evidence 2"],
            "warrant": "Test warrant",
            "backing": "Test backing",
            "qualifier": "definitely",
            "rebuttals": ["Exception 1"],
            "tier": "CATEGORICAL"
          },
          "grounding_chain": [
            [1, "axiom", "grounds"],
            [4, "spec", "implements"]
          ],
          "terminates_at_axiom": true,
          "summary": "Analysis complete"
        }
        """
        report = parse_epistemic_response(response, "test.md")
        assert report.target == "test.md"
        assert report.layer == 4
        assert report.toulmin.claim == "Test claim"
        assert len(report.toulmin.grounds) == 2
        assert report.grounding.terminates_at_axiom


class TestDialecticalParsing:
    """Test dialectical response parsing."""

    def test_parse_valid_dialectical(self):
        """Valid dialectical response is parsed correctly."""
        response = """
        {
          "tensions": [
            {
              "thesis": "A",
              "antithesis": "Not A",
              "classification": "PRODUCTIVE",
              "synthesis": "A and Not A",
              "is_resolved": true
            }
          ],
          "summary": "1 tension found"
        }
        """
        report = parse_dialectical_response(response, "test.md")
        assert report.target == "test.md"
        assert len(report.tensions) == 1
        assert report.tensions[0].thesis == "A"
        assert report.tensions[0].is_resolved


class TestGenerativeParsing:
    """Test generative response parsing."""

    def test_parse_valid_generative(self):
        """Valid generative response is parsed correctly."""
        response = """
        {
          "grammar": {
            "primitives": ["Node", "Edge"],
            "operations": ["compose"],
            "laws": ["identity"]
          },
          "compression_ratio": 0.25,
          "minimal_kernel": ["axiom1", "axiom2"],
          "regeneration_test": {
            "axioms_used": ["axiom1"],
            "structures_regenerated": ["structure1"],
            "missing_elements": [],
            "passed": true
          },
          "summary": "Regenerable"
        }
        """
        report = parse_generative_response(response, "test.md")
        assert report.target == "test.md"
        assert report.compression_ratio == 0.25
        assert "Node" in report.grammar.primitives
        assert report.regeneration.passed
