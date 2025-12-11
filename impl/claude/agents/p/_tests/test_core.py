"""
Tests for P-gents core types (ParseResult, Parser, ParserConfig, IdentityParser).
"""

import pytest
from agents.p.core import IdentityParser, ParserConfig, ParseResult


class TestParseResult:
    """Test ParseResult dataclass and invariants."""

    def test_success_requires_value(self) -> None:
        """success=True requires value is not None."""
        with pytest.raises(ValueError, match="success=True requires value is not None"):
            ParseResult(success=True, value=None, confidence=0.5)

    def test_success_requires_positive_confidence(self) -> None:
        """success=True requires confidence > 0.0."""
        with pytest.raises(ValueError, match="success=True requires confidence > 0.0"):
            ParseResult(success=True, value="data", confidence=0.0)

    def test_failure_requires_error(self) -> None:
        """success=False requires error is not None."""
        with pytest.raises(
            ValueError, match="success=False requires error is not None"
        ):
            ParseResult(success=False, error=None)

    def test_partial_requires_low_confidence(self) -> None:
        """partial=True requires confidence < 1.0."""
        with pytest.raises(ValueError, match="partial=True requires confidence < 1.0"):
            ParseResult(success=True, value="data", confidence=1.0, partial=True)

    def test_valid_success_result(self) -> None:
        """Valid success result."""
        result: ParseResult[str] = ParseResult(
            success=True,
            value="data",
            confidence=0.8,
            strategy="test",
        )
        assert result.success
        assert result.value == "data"
        assert result.confidence == 0.8
        assert result.strategy == "test"

    def test_valid_failure_result(self) -> None:
        """Valid failure result."""
        result: ParseResult[str] = ParseResult(
            success=False,
            error="Parse failed",
            strategy="test",
        )
        assert not result.success
        assert result.error == "Parse failed"
        assert result.value is None

    def test_partial_parse_result(self) -> None:
        """Partial parse with low confidence."""
        result: ParseResult[str] = ParseResult(
            success=True,
            value="partial data",
            confidence=0.5,
            partial=True,
            repairs=["Fixed bracket"],
        )
        assert result.success
        assert result.partial
        assert result.confidence == 0.5
        assert result.repairs == ["Fixed bracket"]

    def test_metadata_field(self) -> None:
        """Metadata field stores strategy-specific info."""
        result: ParseResult[str] = ParseResult(
            success=True,
            value="data",
            confidence=0.9,
            metadata={"source": "llm", "tokens": 100},
        )
        assert result.metadata["source"] == "llm"
        assert result.metadata["tokens"] == 100


class TestParserConfig:
    """Test ParserConfig validation."""

    def test_default_config(self) -> None:
        """Default config is valid."""
        config = ParserConfig()
        config.validate()  # Should not raise

    def test_min_confidence_range(self) -> None:
        """min_confidence must be in [0.0, 1.0]."""
        with pytest.raises(ValueError, match="min_confidence must be in"):
            ParserConfig(min_confidence=-0.1).validate()

        with pytest.raises(ValueError, match="min_confidence must be in"):
            ParserConfig(min_confidence=1.5).validate()

    def test_max_attempts_positive(self) -> None:
        """max_attempts must be >= 1."""
        with pytest.raises(ValueError, match="max_attempts must be"):
            ParserConfig(max_attempts=0).validate()

    def test_timeout_non_negative(self) -> None:
        """timeout_ms must be >= 0."""
        with pytest.raises(ValueError, match="timeout_ms must be"):
            ParserConfig(timeout_ms=-100).validate()

    def test_stream_chunk_size_positive(self) -> None:
        """stream_chunk_size must be >= 1."""
        with pytest.raises(ValueError, match="stream_chunk_size must be"):
            ParserConfig(stream_chunk_size=0).validate()

    def test_max_reflection_retries_non_negative(self) -> None:
        """max_reflection_retries must be >= 0."""
        with pytest.raises(ValueError, match="max_reflection_retries must be"):
            ParserConfig(max_reflection_retries=-1).validate()

    def test_custom_config(self) -> None:
        """Custom config with valid values."""
        config = ParserConfig(
            min_confidence=0.7,
            allow_partial=False,
            max_attempts=500,
            timeout_ms=1000,
        )
        config.validate()  # Should not raise
        assert config.min_confidence == 0.7
        assert not config.allow_partial


class TestIdentityParser:
    """Test IdentityParser (categorical identity)."""

    def test_identity_parse(self) -> None:
        """Identity parser returns text as-is."""
        parser: IdentityParser[str] = IdentityParser()
        result = parser.parse("hello world")

        assert result.success
        assert result.value == "hello world"
        assert result.confidence == 1.0
        assert result.strategy == "identity"

    def test_identity_stream(self) -> None:
        """Identity parser streams tokens as-is."""
        parser: IdentityParser[str] = IdentityParser()
        tokens = ["hello", " ", "world"]
        results = list(parser.parse_stream(iter(tokens)))

        assert len(results) == 3
        assert all(r.success for r in results)
        assert [r.value for r in results] == ["hello", " ", "world"]
        assert all(
            r.confidence == 0.99 for r in results
        )  # Slightly < 1.0 for streaming
        assert all(r.partial for r in results)

    def test_identity_configure(self) -> None:
        """Identity parser can be configured."""
        parser: IdentityParser[str] = IdentityParser()
        new_parser = parser.configure(min_confidence=0.9)

        assert new_parser.config.min_confidence == 0.9
        assert parser.config.min_confidence == 0.5  # Original unchanged

    def test_identity_configure_validation(self) -> None:
        """Configure validates new config."""
        parser: IdentityParser[str] = IdentityParser()

        with pytest.raises(ValueError, match="min_confidence must be in"):
            parser.configure(min_confidence=2.0)
