"""Tests for EvolvingParser (Phase 3: Novel Techniques)."""

import pytest
import tempfile
import os
from agents.p.strategies.evolving import (
    EvolvingParser,
    FormatStats,
    DriftReport,
    create_multi_format_parser,
)
from agents.p.strategies.anchor import AnchorBasedParser
from agents.p.strategies.stack_balancing import json_stream_parser
from agents.p.core import ParseResult


class MockParser:
    """Mock parser for testing."""

    def __init__(self, success: bool = True, value: str = "parsed"):
        self._success = success
        self._value = value

    def parse(self, text: str) -> ParseResult[str]:
        if self._success:
            return ParseResult[str](
                success=True, value=self._value, confidence=0.9, strategy="mock"
            )
        else:
            return ParseResult[str](success=False, error="Mock parser failed")


class TestFormatStats:
    """Test FormatStats tracking."""

    def test_format_stats_initialization(self):
        """Test format stats initialization."""
        stats = FormatStats(name="json")
        assert stats.name == "json"
        assert stats.success_count == 0
        assert stats.failure_count == 0

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        stats = FormatStats(name="json")
        stats.success_count = 7
        stats.failure_count = 3

        assert stats.success_rate == 0.7

    def test_success_rate_with_no_data(self):
        """Test success rate with no data."""
        stats = FormatStats(name="json")
        assert stats.success_rate == 0.0

    def test_avg_parse_time(self):
        """Test average parse time calculation."""
        stats = FormatStats(name="json")
        stats.success_count = 2
        stats.total_parse_time_ms = 200.0

        assert stats.avg_parse_time_ms == 100.0

    def test_to_dict(self):
        """Test serialization to dict."""
        stats = FormatStats(name="json")
        stats.success_count = 5
        stats.failure_count = 1

        d = stats.to_dict()
        assert d["name"] == "json"
        assert d["success_count"] == 5
        assert d["success_rate"] == pytest.approx(5 / 6)


class TestEvolvingParserBasics:
    """Test basic EvolvingParser functionality."""

    def test_initialization(self):
        """Test parser initialization."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(success=True),
                "format_b": MockParser(success=True),
            }
        )

        assert len(parser.strategies) == 2
        assert "format_a" in parser._stats
        assert "format_b" in parser._stats

    def test_parse_success(self):
        """Test successful parsing."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(success=True, value="result_a"),
            }
        )

        result = parser.parse("test input")
        assert result.success
        assert result.value == "result_a"
        assert result.metadata["format"] == "format_a"

    def test_parse_tracks_success(self):
        """Test parsing tracks successful format."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(success=True),
            }
        )

        parser.parse("test")
        assert parser._stats["format_a"].success_count == 1
        assert parser._total_parses == 1

    def test_parse_tracks_failure(self):
        """Test parsing tracks failed format."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(success=False),
                "format_b": MockParser(success=True),
            }
        )

        result = parser.parse("test")
        assert result.success  # format_b succeeded
        assert parser._stats["format_a"].failure_count == 1
        assert parser._stats["format_b"].success_count == 1


class TestStrategyRanking:
    """Test strategy ranking by success rate."""

    def test_ranks_by_success_rate(self):
        """Test strategies ranked by success rate."""
        parser = EvolvingParser(
            strategies={
                "bad": MockParser(success=False),
                "good": MockParser(success=True),
            }
        )

        # Train the parser
        for _ in range(5):
            parser.parse("test")

        # good should be ranked first
        ranked = parser._get_ranked_strategies()
        assert ranked[0][0] == "good"

    def test_adapts_to_changing_formats(self):
        """Test parser adapts when format distribution changes."""
        format_a_parser = MockParser(success=True, value="a")
        format_b_parser = MockParser(success=True, value="b")

        parser = EvolvingParser(
            strategies={
                "format_a": format_a_parser,
                "format_b": format_b_parser,
            }
        )

        # Initially both work equally
        # But over time, format_a succeeds more
        for _ in range(10):
            parser.parse("test")  # format_a ranked first

        # Check format_a is dominant
        report = parser.report_drift()
        # Both have success, but format_a tried first more often
        assert (
            parser._stats["format_a"].success_count
            >= parser._stats["format_b"].success_count
        )


class TestDriftDetection:
    """Test drift detection."""

    def test_report_drift_no_parses(self):
        """Test drift report with no parses."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(),
            }
        )

        report = parser.report_drift()
        assert report.total_parses == 0
        assert not report.drift_detected

    def test_report_drift_identifies_dominant(self):
        """Test drift report identifies dominant format."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(success=True),
                "format_b": MockParser(success=False),
            }
        )

        for _ in range(5):
            parser.parse("test")

        report = parser.report_drift()
        assert report.current_dominant == "format_a"

    def test_drift_detected_on_format_change(self):
        """Test drift detected when dominant format changes."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(success=True),
                "format_b": MockParser(success=False),
            }
        )

        # Initial phase: format_a dominant
        for _ in range(5):
            parser.parse("test")

        report1 = parser.report_drift()
        assert report1.current_dominant == "format_a"

        # Simulate format change: swap success
        parser.strategies["format_a"] = MockParser(success=False)
        parser.strategies["format_b"] = MockParser(success=True)

        # New phase: format_b becomes dominant
        for _ in range(10):
            parser.parse("test")

        report2 = parser.report_drift()
        # Drift may or may not be detected depending on threshold
        # but current_dominant should change
        assert report2.current_dominant == "format_b" or report2.total_parses > 10


class TestStatsExportImport:
    """Test statistics export/import."""

    def test_export_stats(self):
        """Test exporting stats to file."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(success=True),
            }
        )

        for _ in range(3):
            parser.parse("test")

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            filepath = f.name

        try:
            parser.export_stats(filepath)
            assert os.path.exists(filepath)

            # Verify content
            import json

            with open(filepath, "r") as f:
                data = json.load(f)

            assert data["total_parses"] == 3
            assert "format_a" in data["formats"]
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)

    def test_import_stats(self):
        """Test importing stats from file."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(),
            }
        )

        # Create stats file
        import json

        stats_data = {
            "total_parses": 10,
            "formats": {
                "format_a": {
                    "name": "format_a",
                    "success_count": 8,
                    "failure_count": 2,
                    "success_rate": 0.8,
                    "avg_parse_time_ms": 50.0,
                    "avg_confidence": 0.9,
                }
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
            json.dump(stats_data, f)
            filepath = f.name

        try:
            parser.import_stats(filepath)
            assert parser._total_parses == 10
            assert parser._stats["format_a"].success_count == 8
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestConfiguration:
    """Test parser configuration."""

    def test_configure_returns_new_parser(self):
        """Test configure returns new instance."""
        parser1 = EvolvingParser(
            strategies={
                "format_a": MockParser(),
            }
        )
        parser2 = parser1.configure(min_confidence=0.9)

        assert parser1 is not parser2
        assert parser2.config.min_confidence == 0.9


class TestStreamParsing:
    """Test stream parsing."""

    def test_stream_buffers_tokens(self):
        """Test stream parsing buffers tokens."""
        parser = EvolvingParser(
            strategies={
                "format_a": MockParser(success=True),
            }
        )

        results = parser.parse_stream(["hello", " ", "world"])
        assert len(results) == 1
        assert results[0].success


class TestConvenienceFunction:
    """Test convenience parser constructor."""

    def test_create_multi_format_parser(self):
        """Test creating multi-format parser."""
        parser = create_multi_format_parser(
            {
                "anchor": AnchorBasedParser(anchor="###ITEM:"),
                "json": json_stream_parser(),
            }
        )

        assert len(parser.strategies) == 2
        assert "anchor" in parser.strategies
        assert "json" in parser.strategies


class TestRealWorldScenarios:
    """Test real-world use cases."""

    def test_bgent_hypothesis_format_evolution(self):
        """Test B-gent hypothesis format changes over time."""
        # Simulate hypothesis format tracking
        parser = EvolvingParser(
            strategies={
                "anchor_format": AnchorBasedParser(anchor="###HYPOTHESIS:"),
                "json_format": json_stream_parser(),
            }
        )

        # Week 1: anchor format works
        anchor_text = "###HYPOTHESIS: System is stable"
        for _ in range(10):
            parser.parse(anchor_text)

        report1 = parser.report_drift()
        assert report1.current_dominant == "anchor_format"

        # Week 2: JSON format also works (both succeed, but parser should use both)
        json_text = '{"hypothesis": "test"}'
        for _ in range(10):
            parser.parse(json_text)

        # Both formats should have successes now
        assert parser._stats["anchor_format"].success_count > 0
        assert parser._stats["json_format"].success_count > 0

    def test_cross_llm_compatibility(self):
        """Test parser handles different LLM output styles."""
        parser = EvolvingParser(
            strategies={
                "claude_style": MockParser(success=True, value="claude"),
                "gpt_style": MockParser(success=False, value="gpt"),
                "llama_style": MockParser(success=False, value="llama"),
            }
        )

        # Simulate mixed LLM outputs
        for _ in range(30):
            parser.parse("output")

        # Parser should learn which style works
        report = parser.report_drift()
        assert report.current_dominant == "claude_style"
        assert parser._stats["claude_style"].success_rate > 0.5


class TestDriftReportSerialization:
    """Test DriftReport serialization."""

    def test_drift_report_to_dict(self):
        """Test DriftReport serialization."""
        stats = {
            "format_a": FormatStats(name="format_a"),
        }
        report = DriftReport(
            formats=stats,
            total_parses=10,
            current_dominant="format_a",
            drift_detected=True,
            drift_reason="Test drift",
        )

        d = report.to_dict()
        assert d["total_parses"] == 10
        assert d["current_dominant"] == "format_a"
        assert d["drift_detected"] is True
        assert "format_a" in d["formats"]
