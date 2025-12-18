"""
Tests for P-gents composition patterns (Fallback, Fusion, Switch).
"""

from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import pytest

from agents.p.composition import FallbackParser, FusionParser, SwitchParser
from agents.p.core import IdentityParser, Parser, ParseResult
from agents.p.strategies.anchor import AnchorBasedParser

# Mock parsers for testing


class AlwaysSuccessParser(Parser[str]):
    """Parser that always succeeds."""

    def __init__(
        self, value: str = "success", confidence: float = 0.9, strategy: str = "success"
    ) -> None:
        self._value = value
        self._confidence = confidence
        self._strategy = strategy

    def parse(self, text: str) -> ParseResult[str]:
        return ParseResult(
            success=True,
            value=self._value,
            confidence=self._confidence,
            strategy=self._strategy,
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[str]]:
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config: Any) -> "AlwaysSuccessParser":
        """Configure is a no-op for this mock parser."""
        return self


class AlwaysFailParser(Parser[str]):
    """Parser that always fails."""

    def __init__(self, error: str = "fail", strategy: str = "fail") -> None:
        self._error = error
        self._strategy = strategy

    def parse(self, text: str) -> ParseResult[str]:
        return ParseResult(
            success=False,
            error=self._error,
            strategy=self._strategy,
        )

    def parse_stream(self, tokens: Iterator[str]) -> Iterator[ParseResult[str]]:
        text = "".join(tokens)
        yield self.parse(text)

    def configure(self, **config: Any) -> "AlwaysFailParser":
        """Configure is a no-op for this mock parser."""
        return self


class TestFallbackParser:
    """Test sequential fallback composition."""

    def test_first_strategy_succeeds(self) -> None:
        """First strategy succeeds, no fallback needed."""
        parser = FallbackParser(
            AlwaysSuccessParser("first", 0.9, "first"),
            AlwaysSuccessParser("second", 0.8, "second"),
        )

        result = parser.parse("test")

        assert result.success
        assert result.value == "first"
        assert result.confidence == 0.9  # No penalty for first strategy
        assert result.metadata["fallback_depth"] == 0

    def test_fallback_to_second_strategy(self) -> None:
        """First fails, second succeeds."""
        parser = FallbackParser(
            AlwaysFailParser("error1", "first"),
            AlwaysSuccessParser("second", 0.9, "second"),
        )

        result = parser.parse("test")

        assert result.success
        assert result.value == "second"
        assert result.confidence == 0.9 * 0.9  # Penalty for depth=1
        assert result.metadata["fallback_depth"] == 1

    def test_fallback_confidence_penalty(self) -> None:
        """Confidence penalized by fallback depth."""
        parser = FallbackParser(
            AlwaysFailParser("error1", "first"),
            AlwaysFailParser("error2", "second"),
            AlwaysSuccessParser("third", 1.0, "third"),
        )

        result = parser.parse("test")

        assert result.success
        assert result.confidence == 1.0 * 0.8  # Penalty for depth=2
        assert result.metadata["fallback_depth"] == 2

    def test_all_strategies_fail(self) -> None:
        """All strategies fail, aggregated error."""
        parser = FallbackParser(
            AlwaysFailParser("error1", "first"),
            AlwaysFailParser("error2", "second"),
            AlwaysFailParser("error3", "third"),
        )

        result = parser.parse("test")

        assert not result.success
        assert result.error is not None
        assert "error1" in result.error
        assert "error2" in result.error
        assert "error3" in result.error
        assert result.metadata["strategies_tried"] == 3

    def test_no_strategies_raises(self) -> None:
        """FallbackParser requires at least one strategy."""
        with pytest.raises(ValueError, match="at least one strategy"):
            FallbackParser()

    def test_real_world_anchor_fallback(self) -> None:
        """Real-world example: Anchor parser with fallback."""
        parser: FallbackParser[Any] = FallbackParser(
            AnchorBasedParser(anchor="###ITEM:"),
            AnchorBasedParser(anchor="- "),  # Markdown bullet
            IdentityParser[Any](),  # Fallback to raw text
        )

        # First anchor succeeds
        text1 = "###ITEM: Test item"
        result1 = parser.parse(text1)
        assert result1.success
        assert result1.metadata["fallback_depth"] == 0

        # Second anchor succeeds
        text2 = "- Bullet point"
        result2 = parser.parse(text2)
        assert result2.success
        assert result2.metadata["fallback_depth"] == 1

        # Identity fallback
        text3 = "No structured format"
        result3 = parser.parse(text3)
        assert result3.success
        assert result3.metadata["fallback_depth"] == 2


class TestFusionParser:
    """Test parallel fusion composition."""

    def test_simple_fusion(self) -> None:
        """Fuse two parsers with simple merge."""
        parser = FusionParser(
            AlwaysSuccessParser("first", 0.8, "first"),
            AlwaysSuccessParser("second", 0.9, "second"),
            merge_fn=lambda values: " + ".join(values),
        )

        result = parser.parse("test")

        assert result.success
        assert result.value == "first + second"
        assert result.confidence == (0.8 + 0.9) / 2
        assert result.metadata["parsers_succeeded"] == 2

    def test_fusion_with_one_failure(self) -> None:
        """Fusion succeeds if at least one parser succeeds."""
        parser = FusionParser(
            AlwaysSuccessParser("success", 0.9, "success"),
            AlwaysFailParser("error", "fail"),
            merge_fn=lambda values: values[0],
        )

        result = parser.parse("test")

        assert result.success
        assert result.value == "success"
        assert result.metadata["parsers_succeeded"] == 1
        assert result.metadata["parsers_total"] == 2

    def test_fusion_all_fail(self) -> None:
        """Fusion fails if all parsers fail."""
        parser: FusionParser[str] = FusionParser(
            AlwaysFailParser("error1", "first"),
            AlwaysFailParser("error2", "second"),
            merge_fn=lambda values: "",  # Return empty string instead of None
        )

        result = parser.parse("test")

        assert not result.success
        assert result.error is not None
        assert "error1" in result.error
        assert "error2" in result.error

    def test_merge_function_error(self) -> None:
        """Fusion handles merge function errors."""

        def bad_merge(values: list[str]) -> str:
            raise ValueError("Merge failed")

        parser = FusionParser(
            AlwaysSuccessParser("first", 0.9, "first"),
            AlwaysSuccessParser("second", 0.9, "second"),
            merge_fn=bad_merge,
        )

        result = parser.parse("test")

        assert not result.success
        assert result.error is not None
        assert "Merge function failed" in result.error

    def test_no_parsers_raises(self) -> None:
        """FusionParser requires at least one parser."""
        with pytest.raises(ValueError, match="at least one parser"):
            FusionParser(merge_fn=lambda x: "".join(x))


class TestSwitchParser:
    """Test conditional switch composition."""

    def test_switch_on_prefix(self) -> None:
        """Switch based on text prefix."""
        routes: dict[Any, Parser[str]] = {
            lambda t: t.startswith("{"): AlwaysSuccessParser("json", 0.9, "json"),
            lambda t: t.startswith("###"): AlwaysSuccessParser("anchor", 0.9, "anchor"),
            lambda t: True: AlwaysSuccessParser("default", 0.8, "default"),
        }
        parser = SwitchParser(routes)

        # JSON route
        result1 = parser.parse("{}")
        assert result1.success
        assert result1.value == "json"

        # Anchor route
        result2 = parser.parse("###ITEM: test")
        assert result2.success
        assert result2.value == "anchor"

        # Default route
        result3 = parser.parse("plain text")
        assert result3.success
        assert result3.value == "default"

    def test_switch_no_match(self) -> None:
        """Switch fails if no condition matches."""
        routes: dict[Any, Parser[str]] = {
            lambda t: t.startswith("{"): AlwaysSuccessParser("json", 0.9, "json"),
        }
        parser = SwitchParser(routes)

        result = parser.parse("plain text")

        assert not result.success
        assert result.error is not None
        assert "No matching parser" in result.error

    def test_switch_condition_error(self) -> None:
        """Switch handles condition evaluation errors."""

        def bad_condition(text: str) -> bool:
            raise ValueError("Condition error")

        routes: dict[Any, Parser[str]] = {
            bad_condition: AlwaysSuccessParser("bad", 0.9, "bad"),
            lambda t: True: AlwaysSuccessParser("fallback", 0.9, "fallback"),
        }
        parser = SwitchParser(routes)

        result = parser.parse("test")

        # Should skip bad condition and use fallback
        assert result.success
        assert result.value == "fallback"

    def test_no_routes_raises(self) -> None:
        """SwitchParser requires at least one route."""
        with pytest.raises(ValueError, match="at least one route"):
            SwitchParser({})

    def test_real_world_format_detection(self) -> None:
        """Real-world example: Format detection."""
        routes: dict[Any, Parser[Any]] = {
            lambda t: t.strip().startswith("{"): AlwaysSuccessParser("json", 0.95, "json"),
            lambda t: "###" in t: AnchorBasedParser(anchor="###ITEM:"),
            lambda t: True: IdentityParser[Any](),
        }
        parser: SwitchParser[Any] = SwitchParser(routes)

        # JSON detected
        result1 = parser.parse('{"key": "value"}')
        assert result1.success
        assert result1.value == "json"

        # Anchor detected
        result2 = parser.parse("###ITEM: Test")
        assert result2.success
        assert isinstance(result2.value, list)

        # Default (identity)
        result3 = parser.parse("Plain text")
        assert result3.success
        assert result3.value == "Plain text"


class TestCompositionNesting:
    """Test nested composition patterns."""

    def test_fallback_of_fusions(self) -> None:
        """Fallback where each strategy is a fusion."""
        fusion1 = FusionParser(
            AlwaysSuccessParser("a", 0.9, "a"),
            AlwaysSuccessParser("b", 0.9, "b"),
            merge_fn=lambda v: "+".join(v),
        )

        fusion2 = FusionParser(
            AlwaysSuccessParser("c", 0.8, "c"),
            AlwaysSuccessParser("d", 0.8, "d"),
            merge_fn=lambda v: "-".join(v),
        )

        parser = FallbackParser(fusion1, fusion2)

        result = parser.parse("test")

        assert result.success
        # fusion1 succeeds, so use that
        assert result.value == "a+b"

    def test_switch_of_fallbacks(self) -> None:
        """Switch where each route is a fallback."""
        fallback_json = FallbackParser(
            AlwaysSuccessParser("strict-json", 0.95, "strict"),
            AlwaysSuccessParser("loose-json", 0.8, "loose"),
        )

        fallback_text: FallbackParser[Any] = FallbackParser(
            AlwaysSuccessParser("structured", 0.9, "structured"),
            IdentityParser[Any](),
        )

        routes: dict[Any, Parser[Any]] = {
            lambda t: t.startswith("{"): fallback_json,
            lambda t: True: fallback_text,
        }

        parser: SwitchParser[Any] = SwitchParser(routes)

        # JSON route
        result1 = parser.parse("{}")
        assert result1.success
        assert result1.value == "strict-json"

        # Text route
        result2 = parser.parse("plain")
        assert result2.success
        assert result2.value == "structured"
