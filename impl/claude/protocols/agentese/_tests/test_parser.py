"""
Tests for AGENTESE Path Parser

Track A (Syntax Architect): A1 - Clause grammar validation tests.

Tests cover:
- Base path parsing (context.holon.aspect)
- Clause parsing ([phase=DEVELOP], [entropy=0.07], etc.)
- Annotation parsing (@span=ID, @dot=locus)
- Error handling with sympathetic locus
- Edge cases and malformed input
"""

from __future__ import annotations

import pytest

from ..exceptions import PathSyntaxError
from ..parser import (
    PHASE_NAMES,
    VALID_ANNOTATION_MODIFIERS,
    VALID_CLAUSE_MODIFIERS,
    Annotation,
    Clause,
    ParsedPath,
    ParseError,
    ParseResult,
    PathParser,
    Phase,
    create_parser,
    parse_path,
    try_parse_path,
)

# === Fixtures ===


@pytest.fixture
def parser() -> PathParser:
    """Create a strict parser."""
    return PathParser()


@pytest.fixture
def lenient_parser() -> PathParser:
    """Create a lenient parser that allows unknown modifiers."""
    return PathParser(strict_modifiers=False, strict_phases=False)


# === Phase Enum Tests ===


class TestPhaseEnum:
    """Tests for Phase enum."""

    def test_all_phases_defined(self) -> None:
        """All expected phases are defined."""
        expected = {
            "PLAN",
            "RESEARCH",
            "DEVELOP",
            "STRATEGIZE",
            "CROSS-SYNERGIZE",
            "IMPLEMENT",
            "QA",
            "TEST",
            "EDUCATE",
            "MEASURE",
            "REFLECT",
        }
        assert PHASE_NAMES == expected

    def test_phase_is_str_enum(self) -> None:
        """Phase values are strings."""
        assert Phase.DEVELOP.value == "DEVELOP"
        assert str(Phase.DEVELOP) == "Phase.DEVELOP"


# === Base Path Parsing Tests ===


class TestBasePathParsing:
    """Tests for base path parsing (context.holon.aspect)."""

    def test_simple_path(self, parser: PathParser) -> None:
        """Parse simple three-part path."""
        result = parser.parse("world.house.manifest")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.context == "world"
        assert result.parsed.holon == "house"
        assert result.parsed.aspect == "manifest"

    def test_all_contexts(self, parser: PathParser) -> None:
        """All five contexts parse correctly."""
        for context in ["world", "self", "concept", "void", "time"]:
            result = parser.parse(f"{context}.entity.manifest")
            assert result.success, f"Failed for context: {context}"
            assert result.parsed is not None
            assert result.parsed.context == context

    def test_two_part_path_defaults_aspect(self, parser: PathParser) -> None:
        """Two-part path defaults aspect to 'manifest'."""
        result = parser.parse("world.house")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.aspect == "manifest"

    def test_holon_with_underscore(self, parser: PathParser) -> None:
        """Holon can contain underscores."""
        result = parser.parse("world.my_house.manifest")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.holon == "my_house"

    def test_holon_with_numbers(self, parser: PathParser) -> None:
        """Holon can contain numbers (not at start)."""
        result = parser.parse("world.house123.manifest")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.holon == "house123"

    def test_invalid_context_fails(self, parser: PathParser) -> None:
        """Unknown context fails with helpful error."""
        result = parser.parse("invalid.house.manifest")
        assert not result.success
        assert result.error is not None
        assert "invalid" in result.error.locus
        assert "world" in str(result.error.suggestion)

    def test_empty_path_fails(self, parser: PathParser) -> None:
        """Empty path fails."""
        result = parser.parse("")
        assert not result.success
        assert result.error is not None
        assert "Empty" in result.error.message

    def test_single_part_path_fails(self, parser: PathParser) -> None:
        """Single-part path fails."""
        result = parser.parse("world")
        assert not result.success
        assert result.error is not None
        assert "incomplete" in result.error.message.lower()

    def test_holon_starting_with_number_fails(self, parser: PathParser) -> None:
        """Holon starting with number fails."""
        result = parser.parse("world.123house.manifest")
        assert not result.success
        assert result.error is not None
        assert "Invalid holon" in result.error.message

    def test_holon_with_uppercase_fails(self, parser: PathParser) -> None:
        """Holon with uppercase fails."""
        result = parser.parse("world.House.manifest")
        assert not result.success
        assert result.error is not None
        assert "Invalid holon" in result.error.message

    def test_base_path_property(self, parser: PathParser) -> None:
        """base_path property returns core path."""
        result = parser.parse("concept.justice.refine")
        assert result.parsed is not None
        assert result.parsed.base_path == "concept.justice.refine"

    def test_node_path_property(self, parser: PathParser) -> None:
        """node_path property returns context.holon."""
        result = parser.parse("concept.justice.refine")
        assert result.parsed is not None
        assert result.parsed.node_path == "concept.justice"


# === Clause Parsing Tests ===


class TestClauseParsing:
    """Tests for clause parsing ([modifier=value])."""

    def test_phase_clause(self, parser: PathParser) -> None:
        """Parse phase clause."""
        result = parser.parse("concept.justice.refine[phase=DEVELOP]")
        assert result.success
        assert result.parsed is not None
        assert len(result.parsed.clauses) == 1
        assert result.parsed.clauses[0].modifier == "phase"
        assert result.parsed.clauses[0].value == "DEVELOP"

    def test_all_phase_values(self, parser: PathParser) -> None:
        """All phase values parse correctly."""
        for phase in PHASE_NAMES:
            result = parser.parse(f"world.test.manifest[phase={phase}]")
            assert result.success, f"Failed for phase: {phase}"
            assert result.parsed is not None
            assert result.parsed.phase == Phase(phase)

    def test_entropy_clause_float(self, parser: PathParser) -> None:
        """Parse entropy clause with float value."""
        result = parser.parse("void.entropy.sip[entropy=0.07]")
        assert result.success
        assert result.parsed is not None
        clause = result.parsed.get_clause("entropy")
        assert clause is not None
        assert clause.value == 0.07
        assert result.parsed.entropy == 0.07

    def test_law_check_clause_true(self, parser: PathParser) -> None:
        """Parse law_check clause with true."""
        result = parser.parse("self.liturgy.simulate[law_check=true]")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.law_check_enabled is True

    def test_law_check_clause_false(self, parser: PathParser) -> None:
        """Parse law_check clause with false."""
        result = parser.parse("self.liturgy.simulate[law_check=false]")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.law_check_enabled is False

    def test_rollback_clause(self, parser: PathParser) -> None:
        """Parse rollback clause."""
        result = parser.parse("self.liturgy.simulate[rollback=true]")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.rollback_enabled is True

    def test_minimal_output_clause(self, parser: PathParser) -> None:
        """Parse minimal_output clause."""
        result = parser.parse("world.code.manifest[minimal_output=true]")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.minimal_output_enabled is True

    def test_multiple_clauses(self, parser: PathParser) -> None:
        """Parse multiple clauses."""
        result = parser.parse("self.liturgy.simulate[rollback=true][law_check=true]")
        assert result.success
        assert result.parsed is not None
        assert len(result.parsed.clauses) == 2
        assert result.parsed.rollback_enabled is True
        assert result.parsed.law_check_enabled is True

    def test_clause_without_value(self, parser: PathParser) -> None:
        """Parse clause without value (flag-style)."""
        # Use lenient parser since strict requires known modifiers
        lenient = PathParser(strict_modifiers=False)
        result = lenient.parse("world.test.manifest[flag]")
        assert result.success
        assert result.parsed is not None
        clause = result.parsed.get_clause("flag")
        assert clause is not None
        assert clause.value is None

    def test_unknown_clause_modifier_strict(self, parser: PathParser) -> None:
        """Unknown clause modifier fails in strict mode."""
        result = parser.parse("world.test.manifest[unknown=value]")
        assert not result.success
        assert result.error is not None
        assert "unknown" in result.error.message.lower()
        assert result.error.locus == "[unknown=value]"

    def test_unknown_clause_modifier_lenient(self, lenient_parser: PathParser) -> None:
        """Unknown clause modifier allowed in lenient mode."""
        result = lenient_parser.parse("world.test.manifest[custom=value]")
        assert result.success
        assert result.parsed is not None
        clause = result.parsed.get_clause("custom")
        assert clause is not None
        assert clause.value == "value"

    def test_invalid_phase_value(self, parser: PathParser) -> None:
        """Invalid phase value fails in strict mode."""
        result = parser.parse("world.test.manifest[phase=INVALID]")
        assert not result.success
        assert result.error is not None
        assert "phase" in result.error.message.lower()
        assert result.error.locus == "[phase=INVALID]"

    def test_entropy_out_of_range_high(self, parser: PathParser) -> None:
        """Entropy > 1.0 fails."""
        result = parser.parse("void.entropy.sip[entropy=1.5]")
        assert not result.success
        assert result.error is not None
        assert "range" in result.error.message.lower()

    def test_entropy_out_of_range_negative(self, parser: PathParser) -> None:
        """Negative entropy fails."""
        result = parser.parse("void.entropy.sip[entropy=-0.1]")
        assert not result.success
        assert result.error is not None
        assert "range" in result.error.message.lower()

    def test_unclosed_bracket(self, parser: PathParser) -> None:
        """Unclosed bracket fails."""
        result = parser.parse("world.test.manifest[phase=DEVELOP")
        assert not result.success
        assert result.error is not None
        assert "Unclosed" in result.error.message

    def test_clause_as_dict(self) -> None:
        """Clause.as_dict returns modifier-value dict."""
        clause = Clause(modifier="phase", value="DEVELOP")
        assert clause.as_dict == {"phase": "DEVELOP"}

    def test_has_clause(self, parser: PathParser) -> None:
        """has_clause returns correct boolean."""
        result = parser.parse("world.test.manifest[phase=DEVELOP]")
        assert result.parsed is not None
        assert result.parsed.has_clause("phase") is True
        assert result.parsed.has_clause("entropy") is False


# === Annotation Parsing Tests ===


class TestAnnotationParsing:
    """Tests for annotation parsing (@modifier=value)."""

    def test_span_annotation(self, parser: PathParser) -> None:
        """Parse span annotation."""
        result = parser.parse("void.entropy.sip@span=dev_001")
        assert result.success
        assert result.parsed is not None
        assert len(result.parsed.annotations) == 1
        assert result.parsed.annotations[0].modifier == "span"
        assert result.parsed.annotations[0].value == "dev_001"
        assert result.parsed.span_id == "dev_001"

    def test_dot_annotation_locus(self, parser: PathParser) -> None:
        """Parse @dot annotation for locus."""
        result = parser.parse("world.test.manifest@dot=path.to.error")
        assert result.success
        assert result.parsed is not None
        annotation = result.parsed.get_annotation("dot")
        assert annotation is not None
        assert annotation.value == "path.to.error"
        assert result.parsed.locus == "path.to.error"

    def test_phase_as_annotation(self, parser: PathParser) -> None:
        """Phase can be specified as annotation."""
        result = parser.parse("world.code.manifest@phase=IMPLEMENT")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.phase == Phase.IMPLEMENT

    def test_multiple_annotations(self, parser: PathParser) -> None:
        """Parse multiple annotations."""
        result = parser.parse("void.entropy.sip@span=dev_001@phase=DEVELOP")
        assert result.success
        assert result.parsed is not None
        assert len(result.parsed.annotations) == 2
        assert result.parsed.span_id == "dev_001"

    def test_annotation_without_value_fails(self, parser: PathParser) -> None:
        """Annotation without value fails."""
        result = parser.parse("world.test.manifest@span")
        assert not result.success
        assert result.error is not None
        assert "missing value" in result.error.message.lower()
        assert result.error.locus == "@span"

    def test_unknown_annotation_modifier_strict(self, parser: PathParser) -> None:
        """Unknown annotation modifier fails in strict mode."""
        result = parser.parse("world.test.manifest@unknown=value")
        assert not result.success
        assert result.error is not None
        assert "unknown" in result.error.message.lower()

    def test_unknown_annotation_modifier_lenient(
        self, lenient_parser: PathParser
    ) -> None:
        """Unknown annotation modifier allowed in lenient mode."""
        result = lenient_parser.parse("world.test.manifest@custom=value")
        assert result.success
        assert result.parsed is not None
        annotation = result.parsed.get_annotation("custom")
        assert annotation is not None
        assert annotation.value == "value"

    def test_annotation_as_dict(self) -> None:
        """Annotation.as_dict returns modifier-value dict."""
        annotation = Annotation(modifier="span", value="test_001")
        assert annotation.as_dict == {"span": "test_001"}

    def test_has_annotation(self, parser: PathParser) -> None:
        """has_annotation returns correct boolean."""
        result = parser.parse("world.test.manifest@span=dev_001")
        assert result.parsed is not None
        assert result.parsed.has_annotation("span") is True
        assert result.parsed.has_annotation("dot") is False


# === Combined Clause and Annotation Tests ===


class TestCombinedModifiers:
    """Tests for combined clauses and annotations."""

    def test_clause_then_annotation(self, parser: PathParser) -> None:
        """Parse clause followed by annotation."""
        result = parser.parse("void.entropy.sip[entropy=0.07]@span=dev_001")
        assert result.success
        assert result.parsed is not None
        assert len(result.parsed.clauses) == 1
        assert len(result.parsed.annotations) == 1
        assert result.parsed.entropy == 0.07
        assert result.parsed.span_id == "dev_001"

    def test_multiple_clauses_then_annotations(self, parser: PathParser) -> None:
        """Parse multiple clauses followed by multiple annotations."""
        path = "self.liturgy.simulate[rollback=true][law_check=true]@span=sim_001@phase=TEST"
        result = parser.parse(path)
        assert result.success
        assert result.parsed is not None
        assert len(result.parsed.clauses) == 2
        assert len(result.parsed.annotations) == 2
        assert result.parsed.rollback_enabled is True
        assert result.parsed.law_check_enabled is True
        assert result.parsed.span_id == "sim_001"
        assert result.parsed.phase == Phase.TEST

    def test_full_path_reconstruction(self, parser: PathParser) -> None:
        """full_path property reconstructs the path."""
        original = "concept.justice.refine[phase=DEVELOP]@span=dev_001"
        result = parser.parse(original)
        assert result.parsed is not None
        # Note: reconstruction may have slightly different formatting
        reconstructed = result.parsed.full_path
        assert "concept.justice.refine" in reconstructed
        assert "[phase=DEVELOP]" in reconstructed
        assert "@span=dev_001" in reconstructed


# === Error Handling Tests ===


class TestErrorHandling:
    """Tests for error handling with sympathetic locus."""

    def test_error_includes_locus(self, parser: PathParser) -> None:
        """ParseError includes locus for precise error location."""
        result = parser.parse("invalid.house.manifest")
        assert result.error is not None
        assert result.error.locus == "invalid"

    def test_error_includes_suggestion(self, parser: PathParser) -> None:
        """ParseError includes helpful suggestion."""
        result = parser.parse("invalid.house.manifest")
        assert result.error is not None
        assert result.error.suggestion is not None
        assert "world" in result.error.suggestion

    def test_error_str_format(self, parser: PathParser) -> None:
        """ParseError __str__ includes locus."""
        result = parser.parse("invalid.house.manifest")
        assert result.error is not None
        error_str = str(result.error)
        assert "@" in error_str  # Format: message@locus

    def test_clause_error_locus(self, parser: PathParser) -> None:
        """Clause error includes clause in locus."""
        result = parser.parse("world.test.manifest[phase=INVALID]")
        assert result.error is not None
        assert "[phase=INVALID]" in result.error.locus

    def test_annotation_error_locus(self, parser: PathParser) -> None:
        """Annotation error includes annotation in locus."""
        result = parser.parse("world.test.manifest@unknown=value")
        assert result.error is not None
        assert "@unknown" in result.error.locus

    def test_unexpected_character_error(self, parser: PathParser) -> None:
        """Unexpected character produces clear error."""
        result = parser.parse("world.test.manifest!invalid")
        assert not result.success
        assert result.error is not None
        # Error message indicates invalid aspect (! makes it invalid identifier)
        assert (
            "Invalid aspect" in result.error.message or "invalid" in result.error.locus
        )


# === Factory Function Tests ===


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_parser_strict(self) -> None:
        """create_parser with strict=True creates strict parser."""
        parser = create_parser(strict=True)
        result = parser.parse("world.test.manifest[unknown=value]")
        assert not result.success

    def test_create_parser_lenient(self) -> None:
        """create_parser with strict=False creates lenient parser."""
        parser = create_parser(strict=False)
        result = parser.parse("world.test.manifest[unknown=value]")
        assert result.success

    def test_parse_path_success(self) -> None:
        """parse_path returns ParsedPath on success."""
        parsed = parse_path("world.house.manifest")
        assert isinstance(parsed, ParsedPath)
        assert parsed.context == "world"

    def test_parse_path_raises_on_failure(self) -> None:
        """parse_path raises PathSyntaxError on failure."""
        with pytest.raises(PathSyntaxError) as exc_info:
            parse_path("invalid.house.manifest")

        assert "invalid" in str(exc_info.value)

    def test_try_parse_path_success(self) -> None:
        """try_parse_path returns ParsedPath on success."""
        parsed = try_parse_path("world.house.manifest")
        assert parsed is not None
        assert parsed.context == "world"

    def test_try_parse_path_returns_none_on_failure(self) -> None:
        """try_parse_path returns None on failure."""
        parsed = try_parse_path("invalid.house.manifest")
        assert parsed is None


# === ParsedPath Methods Tests ===


class TestParsedPathMethods:
    """Tests for ParsedPath helper methods."""

    def test_get_clause_found(self, parser: PathParser) -> None:
        """get_clause returns clause when found."""
        result = parser.parse("world.test.manifest[phase=DEVELOP]")
        assert result.parsed is not None
        clause = result.parsed.get_clause("phase")
        assert clause is not None
        assert clause.value == "DEVELOP"

    def test_get_clause_not_found(self, parser: PathParser) -> None:
        """get_clause returns None when not found."""
        result = parser.parse("world.test.manifest")
        assert result.parsed is not None
        clause = result.parsed.get_clause("phase")
        assert clause is None

    def test_get_annotation_found(self, parser: PathParser) -> None:
        """get_annotation returns annotation when found."""
        result = parser.parse("world.test.manifest@span=dev_001")
        assert result.parsed is not None
        annotation = result.parsed.get_annotation("span")
        assert annotation is not None
        assert annotation.value == "dev_001"

    def test_get_annotation_not_found(self, parser: PathParser) -> None:
        """get_annotation returns None when not found."""
        result = parser.parse("world.test.manifest")
        assert result.parsed is not None
        annotation = result.parsed.get_annotation("span")
        assert annotation is None

    def test_phase_property_from_clause(self, parser: PathParser) -> None:
        """phase property reads from clause."""
        result = parser.parse("world.test.manifest[phase=DEVELOP]")
        assert result.parsed is not None
        assert result.parsed.phase == Phase.DEVELOP

    def test_phase_property_from_annotation(self, parser: PathParser) -> None:
        """phase property reads from annotation if no clause."""
        result = parser.parse("world.test.manifest@phase=DEVELOP")
        assert result.parsed is not None
        assert result.parsed.phase == Phase.DEVELOP

    def test_phase_property_none(self, parser: PathParser) -> None:
        """phase property returns None if not specified."""
        result = parser.parse("world.test.manifest")
        assert result.parsed is not None
        assert result.parsed.phase is None


# === ParseResult Tests ===


class TestParseResult:
    """Tests for ParseResult."""

    def test_result_bool_true(self, parser: PathParser) -> None:
        """ParseResult is truthy on success."""
        result = parser.parse("world.test.manifest")
        assert bool(result) is True

    def test_result_bool_false(self, parser: PathParser) -> None:
        """ParseResult is falsy on failure."""
        result = parser.parse("invalid.test.manifest")
        assert bool(result) is False


# === Edge Cases ===


class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_very_long_path(self, parser: PathParser) -> None:
        """Very long path still parses correctly."""
        long_holon = "a" * 100
        result = parser.parse(f"world.{long_holon}.manifest")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.holon == long_holon

    def test_many_clauses(self, parser: PathParser) -> None:
        """Many clauses parse correctly."""
        path = (
            "self.liturgy.simulate[rollback=true][law_check=true][minimal_output=true]"
        )
        result = parser.parse(path)
        assert result.success
        assert result.parsed is not None
        assert len(result.parsed.clauses) == 3

    def test_whitespace_in_value(self, parser: PathParser) -> None:
        """Whitespace in values is preserved (for lenient parser)."""
        lenient = PathParser(strict_modifiers=False)
        result = lenient.parse("world.test.manifest@note=hello world")
        assert result.success
        assert result.parsed is not None
        annotation = result.parsed.get_annotation("note")
        assert annotation is not None
        # Note: whitespace handling depends on implementation

    def test_empty_brackets(self, parser: PathParser) -> None:
        """Empty brackets are handled."""
        lenient = PathParser(strict_modifiers=False)
        result = lenient.parse("world.test.manifest[]")
        # This should either fail or create empty clause
        # depending on implementation
        if result.success:
            assert result.parsed is not None

    def test_special_characters_in_span_id(self, parser: PathParser) -> None:
        """Span ID can contain underscores and numbers."""
        result = parser.parse("world.test.manifest@span=research_001_alpha")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.span_id == "research_001_alpha"


# === Valid Modifiers Constants Tests ===


class TestValidModifiers:
    """Tests for valid modifier constants."""

    def test_clause_modifiers_defined(self) -> None:
        """All expected clause modifiers are defined."""
        expected = {"phase", "entropy", "law_check", "rollback", "minimal_output"}
        assert VALID_CLAUSE_MODIFIERS == expected

    def test_annotation_modifiers_defined(self) -> None:
        """All expected annotation modifiers are defined."""
        expected = {"span", "phase", "law_check", "dot"}
        assert VALID_ANNOTATION_MODIFIERS == expected


# === Spec Compliance Tests ===


class TestSpecCompliance:
    """Tests for compliance with spec/protocols/agentese.md examples."""

    def test_spec_example_1(self, parser: PathParser) -> None:
        """Spec example: concept.justice.refine[phase=DEVELOP]"""
        result = parser.parse("concept.justice.refine[phase=DEVELOP]")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.context == "concept"
        assert result.parsed.holon == "justice"
        assert result.parsed.aspect == "refine"
        assert result.parsed.phase == Phase.DEVELOP

    def test_spec_example_2(self, parser: PathParser) -> None:
        """Spec example: void.entropy.sip[entropy=0.07]@span=dev_001"""
        result = parser.parse("void.entropy.sip[entropy=0.07]@span=dev_001")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.context == "void"
        assert result.parsed.entropy == 0.07
        assert result.parsed.span_id == "dev_001"

    def test_spec_example_3(self, parser: PathParser) -> None:
        """Spec example: self.liturgy.simulate[rollback=true][law_check=true]"""
        result = parser.parse("self.liturgy.simulate[rollback=true][law_check=true]")
        assert result.success
        assert result.parsed is not None
        assert result.parsed.context == "self"
        assert result.parsed.rollback_enabled is True
        assert result.parsed.law_check_enabled is True

    def test_spec_example_4(self, parser: PathParser) -> None:
        """Spec example: world.code.manifest[minimal_output=true]@phase=IMPLEMENT"""
        result = parser.parse(
            "world.code.manifest[minimal_output=true]@phase=IMPLEMENT"
        )
        assert result.success
        assert result.parsed is not None
        assert result.parsed.minimal_output_enabled is True
        assert result.parsed.phase == Phase.IMPLEMENT

    def test_unadorned_path_valid(self, parser: PathParser) -> None:
        """Unadorned path world.house.manifest is valid."""
        result = parser.parse("world.house.manifest")
        assert result.success
        assert result.parsed is not None
        assert len(result.parsed.clauses) == 0
        assert len(result.parsed.annotations) == 0
