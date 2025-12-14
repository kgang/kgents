"""
Tests for Domain Operads.

These tests verify:
1. SOUL_OPERAD operations
2. PARSE_OPERAD operations
3. REALITY_OPERAD operations
4. Domain operads extend universal operad
"""

import pytest
from agents.operad import (
    AGENT_OPERAD,
    PARSE_OPERAD,
    REALITY_OPERAD,
    SOUL_OPERAD,
    ConfidentParse,
    ParseResult,
    RealityClassification,
    RealityType,
)
from agents.poly import from_function


class TestSoulOperad:
    """Tests for SOUL_OPERAD."""

    def test_has_universal_operations(self) -> None:
        """SOUL_OPERAD includes universal operations."""
        for op_name in AGENT_OPERAD.operations:
            assert op_name in SOUL_OPERAD.operations

    def test_has_soul_operations(self) -> None:
        """SOUL_OPERAD has introspect, shadow, dialectic."""
        assert "introspect" in SOUL_OPERAD.operations
        assert "shadow" in SOUL_OPERAD.operations
        assert "dialectic" in SOUL_OPERAD.operations
        assert "vibe" in SOUL_OPERAD.operations
        assert "tension" in SOUL_OPERAD.operations

    def test_introspect_creates_pipeline(self) -> None:
        """introspect creates ground >> manifest >> witness pipeline."""
        agent = SOUL_OPERAD.compose("introspect")
        assert agent is not None
        assert ">>" in agent.name

    def test_shadow_wraps_agent(self) -> None:
        """shadow wraps agent with contradiction."""
        thesis_agent = from_function("Thesis", lambda x: f"thesis: {x}")
        shadowed = SOUL_OPERAD.compose("shadow", thesis_agent)

        assert "shadow" not in shadowed.name.lower()  # Uses >> naming
        # The shadow pipeline adds CONTRADICT

    def test_dialectic_composes_parallel_then_sublate(self) -> None:
        """dialectic: parallel(thesis, antithesis) >> sublate."""
        thesis = from_function("Thesis", lambda x: f"thesis: {x}")
        antithesis = from_function("Antithesis", lambda x: f"anti: {x}")

        dialectic = SOUL_OPERAD.compose("dialectic", thesis, antithesis)
        assert dialectic is not None

    def test_vibe_returns_eigenvector_snapshot(self) -> None:
        """vibe returns personality fingerprint."""
        vibe = SOUL_OPERAD.compose("vibe")
        _, result = vibe.invoke("ready", "how am I?")

        assert "vibe" in result
        assert "Playful" in result["vibe"]

    def test_tension_returns_conflicts(self) -> None:
        """tension returns held eigenvector tensions."""
        tension = SOUL_OPERAD.compose("tension")
        _, result = tension.invoke("ready", "where am I stuck?")

        assert "tensions" in result
        assert len(result["tensions"]) > 0


class TestParseOperad:
    """Tests for PARSE_OPERAD."""

    def test_has_universal_operations(self) -> None:
        """PARSE_OPERAD includes universal operations."""
        for op_name in AGENT_OPERAD.operations:
            assert op_name in PARSE_OPERAD.operations

    def test_has_parse_operations(self) -> None:
        """PARSE_OPERAD has confident, repair, parse."""
        assert "confident" in PARSE_OPERAD.operations
        assert "repair" in PARSE_OPERAD.operations
        assert "parse" in PARSE_OPERAD.operations

    def test_confident_adds_annotation(self) -> None:
        """confident adds confidence annotation."""
        parser = from_function(
            "Parser",
            lambda x: ParseResult(content=x, confidence=0.8),
        )
        confident_parser = PARSE_OPERAD.compose("confident", parser)

        _, result = confident_parser.invoke(("ready", "ready"), "input")

        assert isinstance(result, ConfidentParse)
        assert result.is_confident is True  # 0.8 > 0.5

    def test_confident_marks_low_confidence(self) -> None:
        """confident marks low confidence as not confident."""
        parser = from_function(
            "Parser",
            lambda x: ParseResult(content=x, confidence=0.3),
        )
        confident_parser = PARSE_OPERAD.compose("confident", parser)

        _, result = confident_parser.invoke(("ready", "ready"), "input")

        assert isinstance(result, ConfidentParse)
        assert result.is_confident is False  # 0.3 < 0.5

    def test_parse_creates_universal_parser(self) -> None:
        """parse creates universal entry point."""
        parser = PARSE_OPERAD.compose("parse")
        _, result = parser.invoke("ready", "hello world")

        assert isinstance(result, ParseResult)
        assert result.content == "hello world"
        assert result.source == "universal"


class TestRealityOperad:
    """Tests for REALITY_OPERAD."""

    def test_has_universal_operations(self) -> None:
        """REALITY_OPERAD includes universal operations."""
        for op_name in AGENT_OPERAD.operations:
            assert op_name in REALITY_OPERAD.operations

    def test_has_reality_operations(self) -> None:
        """REALITY_OPERAD has classify, collapse, ground, stable."""
        assert "classify" in REALITY_OPERAD.operations
        assert "collapse" in REALITY_OPERAD.operations
        assert "ground" in REALITY_OPERAD.operations
        assert "stable" in REALITY_OPERAD.operations

    def test_classify_deterministic(self) -> None:
        """classify tags primitives as DETERMINISTIC."""
        agent = from_function("IntAgent", lambda x: 42)
        classified = REALITY_OPERAD.compose("classify", agent)

        _, result = classified.invoke(("ready", "ready"), "any")

        assert isinstance(result, RealityClassification)
        assert result.reality == RealityType.DETERMINISTIC
        assert result.value == 42

    def test_classify_chaotic(self) -> None:
        """classify tags errors as CHAOTIC."""
        agent = from_function("ErrorAgent", lambda x: {"error": "failed"})
        classified = REALITY_OPERAD.compose("classify", agent)

        _, result = classified.invoke(("ready", "ready"), "any")

        assert isinstance(result, RealityClassification)
        assert result.reality == RealityType.CHAOTIC

    def test_ground_checks_reality(self) -> None:
        """ground checks if input is grounded."""
        ground = REALITY_OPERAD.compose("ground")
        _, result = ground.invoke("ready", "This is true.")

        assert isinstance(result, RealityClassification)
        assert result.reality == RealityType.DETERMINISTIC

    def test_ground_marks_uncertain(self) -> None:
        """ground marks uncertain language as PROBABILISTIC."""
        ground = REALITY_OPERAD.compose("ground")
        _, result = ground.invoke("ready", "This might probably be true maybe.")

        assert isinstance(result, RealityClassification)
        assert result.reality == RealityType.PROBABILISTIC

    def test_stable_checks_stability(self) -> None:
        """stable checks if agent is stable."""
        agent = from_function("StableAgent", lambda x: 42)
        stable = REALITY_OPERAD.compose("stable", agent)

        _, result = stable.invoke((("ready", "ready"), "ready"), "input")

        assert result["stable"] is True
        assert result["reality"] == "DETERMINISTIC"


class TestDomainOperadComposition:
    """Tests for composing domain operads."""

    def test_soul_seq_parse(self) -> None:
        """Can compose soul and parse operations."""
        # introspect >> parse
        introspect = SOUL_OPERAD.compose("introspect")
        parser = PARSE_OPERAD.compose("parse")

        # Use universal seq from soul operad
        pipeline = SOUL_OPERAD.compose("seq", introspect, parser)
        assert pipeline is not None

    def test_parse_classify_pipeline(self) -> None:
        """Can build parse >> classify pipeline."""
        parser = PARSE_OPERAD.compose("parse")

        # We can't directly use REALITY_OPERAD.compose("classify", parser)
        # because parser is from PARSE_OPERAD
        # But we can build a custom pipeline
        classified = REALITY_OPERAD.compose("classify", parser)
        assert classified is not None

    def test_three_domain_pipeline(self) -> None:
        """Can build pipeline across three domains."""
        # vibe >> parse >> classify
        vibe = SOUL_OPERAD.compose("vibe")

        # This demonstrates cross-domain composition
        # In practice, you'd ensure type compatibility
        pipeline = SOUL_OPERAD.compose("seq", vibe, PARSE_OPERAD.compose("parse"))
        assert pipeline is not None
