"""Tests for L0 pattern matching."""

import pytest

from protocols.ashc.ast import (
    DictPattern,
    ListPattern,
    LiteralPattern,
    WildcardPattern,
)
from protocols.ashc.patterns import (
    dict_pattern,
    list_pattern,
    literal,
    match,
    wildcard,
)


class TestLiteralPattern:
    """Tests for literal pattern matching."""

    def test_match_equal_value(self) -> None:
        """Literal matches equal value."""
        result = match(LiteralPattern(42), 42)
        assert result == {}

    def test_no_match_different_value(self) -> None:
        """Literal does not match different value."""
        result = match(LiteralPattern(42), 43)
        assert result is None

    def test_match_string(self) -> None:
        """Literal matches string."""
        result = match(LiteralPattern("hello"), "hello")
        assert result == {}

    def test_match_none(self) -> None:
        """Literal matches None."""
        result = match(LiteralPattern(None), None)
        assert result == {}

    def test_match_dict_literal(self) -> None:
        """Literal matches dict by equality."""
        result = match(LiteralPattern({"a": 1}), {"a": 1})
        assert result == {}


class TestWildcardPattern:
    """Tests for wildcard pattern matching."""

    def test_match_any_value(self) -> None:
        """Wildcard matches any value."""
        result = match(WildcardPattern("x"), 42)
        assert result == {"x": 42}

    def test_match_complex_value(self) -> None:
        """Wildcard matches complex value."""
        value = {"nested": [1, 2, 3]}
        result = match(WildcardPattern("data"), value)
        assert result == {"data": value}

    def test_match_none(self) -> None:
        """Wildcard matches None."""
        result = match(WildcardPattern("x"), None)
        assert result == {"x": None}


class TestDictPattern:
    """Tests for dict pattern matching."""

    def test_match_exact_keys(self) -> None:
        """Dict pattern matches exact keys."""
        pattern = DictPattern.from_dict(
            {
                "a": LiteralPattern(1),
                "b": LiteralPattern(2),
            }
        )
        result = match(pattern, {"a": 1, "b": 2})
        assert result == {}

    def test_no_match_missing_key(self) -> None:
        """Dict pattern fails on missing key."""
        pattern = DictPattern.from_dict(
            {
                "a": LiteralPattern(1),
                "b": LiteralPattern(2),
            }
        )
        result = match(pattern, {"a": 1})
        assert result is None

    def test_no_match_extra_key_strict(self) -> None:
        """Dict pattern fails on extra key (strict mode)."""
        pattern = DictPattern.from_dict(
            {
                "a": LiteralPattern(1),
            }
        )
        result = match(pattern, {"a": 1, "b": 2})
        assert result is None

    def test_match_extra_key_allowed(self) -> None:
        """Dict pattern allows extra keys when specified."""
        pattern = DictPattern.from_dict(
            {"a": LiteralPattern(1)},
            allow_extra=True,
        )
        result = match(pattern, {"a": 1, "b": 2})
        assert result == {}

    def test_match_with_wildcard(self) -> None:
        """Dict pattern captures with wildcard."""
        pattern = DictPattern.from_dict(
            {
                "name": WildcardPattern("n"),
                "age": WildcardPattern("a"),
            }
        )
        result = match(pattern, {"name": "Kent", "age": 30})
        assert result == {"n": "Kent", "a": 30}

    def test_no_match_non_dict(self) -> None:
        """Dict pattern fails on non-dict."""
        pattern = DictPattern.from_dict({"a": LiteralPattern(1)})
        result = match(pattern, [1, 2, 3])
        assert result is None


class TestListPattern:
    """Tests for list pattern matching."""

    def test_match_exact_elements(self) -> None:
        """List pattern matches exact elements."""
        pattern = ListPattern(
            elements=(LiteralPattern(1), LiteralPattern(2)),
        )
        result = match(pattern, [1, 2])
        assert result == {}

    def test_no_match_different_length_strict(self) -> None:
        """List pattern fails on different length (strict)."""
        pattern = ListPattern(
            elements=(LiteralPattern(1), LiteralPattern(2)),
        )
        result = match(pattern, [1, 2, 3])
        assert result is None

    def test_match_extra_allowed(self) -> None:
        """List pattern allows extra elements when specified."""
        pattern = ListPattern(
            elements=(LiteralPattern(1), LiteralPattern(2)),
            allow_extra=True,
        )
        result = match(pattern, [1, 2, 3, 4])
        assert result == {}

    def test_match_with_wildcards(self) -> None:
        """List pattern captures with wildcards."""
        pattern = ListPattern(
            elements=(WildcardPattern("first"), WildcardPattern("second")),
        )
        result = match(pattern, ["a", "b"])
        assert result == {"first": "a", "second": "b"}

    def test_no_match_non_list(self) -> None:
        """List pattern fails on non-list."""
        pattern = ListPattern(elements=(LiteralPattern(1),))
        result = match(pattern, {"a": 1})
        assert result is None

    def test_match_tuple(self) -> None:
        """List pattern also matches tuples."""
        pattern = ListPattern(elements=(LiteralPattern(1), LiteralPattern(2)))
        result = match(pattern, (1, 2))
        assert result == {}


class TestNestedPatterns:
    """Tests for nested pattern matching."""

    def test_dict_with_list(self) -> None:
        """Dict pattern with nested list."""
        pattern = DictPattern.from_dict(
            {
                "items": ListPattern(
                    elements=(LiteralPattern(1), WildcardPattern("second")),
                ),
            }
        )
        result = match(pattern, {"items": [1, 2]})
        assert result == {"second": 2}

    def test_list_with_dict(self) -> None:
        """List pattern with nested dict."""
        pattern = ListPattern(
            elements=(DictPattern.from_dict({"name": WildcardPattern("n")}),),
        )
        result = match(pattern, [{"name": "test"}])
        assert result == {"n": "test"}


class TestHelperFunctions:
    """Tests for pattern helper functions."""

    def test_literal_helper(self) -> None:
        """literal() helper creates LiteralPattern."""
        p = literal(42)
        assert isinstance(p, LiteralPattern)
        assert p.value == 42

    def test_wildcard_helper(self) -> None:
        """wildcard() helper creates WildcardPattern."""
        p = wildcard("x")
        assert isinstance(p, WildcardPattern)
        assert p.name == "x"

    def test_dict_pattern_helper(self) -> None:
        """dict_pattern() helper creates DictPattern."""
        p = dict_pattern({"a": literal(1)}, allow_extra=True)
        assert isinstance(p, DictPattern)
        assert p.allow_extra

    def test_list_pattern_helper(self) -> None:
        """list_pattern() helper creates ListPattern."""
        p = list_pattern(literal(1), wildcard("x"), allow_extra=True)
        assert isinstance(p, ListPattern)
        assert len(p.elements) == 2
        assert p.allow_extra
