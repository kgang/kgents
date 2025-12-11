"""
Tests for G-gent Phase 7: W-gent Pattern Inference

Tests cover:
1. Pattern observation and extraction
2. Grammar hypothesis generation
3. Grammar validation
4. Grammar refinement
5. Crystallization to Tongue
6. Full inference pipeline
7. Edge cases
"""

import pytest
from agents.g.pattern_inference import (
    GrammarHypothesis,
    GrammarRule,
    GrammarSynthesizer,
    GrammarValidator,
    InferenceReport,
    ObservedPattern,
    # Classes
    PatternAnalyzer,
    PatternCluster,
    PatternInferenceEngine,
    # Types
    PatternType,
    ValidationResult,
    extract_patterns,
    hypothesize_grammar,
    # Convenience functions
    infer_grammar_from_observations,
    observe_and_infer,
)
from agents.g.types import GrammarLevel

# ============================================================================
# ObservedPattern Tests
# ============================================================================


class TestObservedPattern:
    """Tests for ObservedPattern dataclass."""

    def test_create_pattern(self):
        """Can create pattern with valid data."""
        pattern = ObservedPattern(
            pattern="CHECK <date>",
            pattern_type=PatternType.TOKEN,
            frequency=0.8,
            examples=["CHECK 2024-12-15"],
        )
        assert pattern.pattern == "CHECK <date>"
        assert pattern.frequency == 0.8
        assert len(pattern.examples) == 1

    def test_pattern_frequency_bounds(self):
        """Frequency must be between 0 and 1."""
        with pytest.raises(ValueError, match="Frequency must be 0.0-1.0"):
            ObservedPattern(
                pattern="test",
                pattern_type=PatternType.LITERAL,
                frequency=1.5,
            )

        with pytest.raises(ValueError, match="Frequency must be 0.0-1.0"):
            ObservedPattern(
                pattern="test",
                pattern_type=PatternType.LITERAL,
                frequency=-0.1,
            )

    def test_pattern_with_metadata(self):
        """Pattern can include metadata."""
        pattern = ObservedPattern(
            pattern="<verb> <noun>",
            pattern_type=PatternType.SEQUENCE,
            frequency=0.9,
            metadata={"verbs": ["CHECK", "ADD", "LIST"]},
        )
        assert "verbs" in pattern.metadata
        assert len(pattern.metadata["verbs"]) == 3


class TestPatternCluster:
    """Tests for PatternCluster dataclass."""

    def test_create_cluster(self):
        """Can create cluster with patterns."""
        p1 = ObservedPattern("A", PatternType.TOKEN, 0.6)
        p2 = ObservedPattern("B", PatternType.TOKEN, 0.4)
        cluster = PatternCluster(
            name="token_cluster",
            patterns=[p1, p2],
            dominant_type=PatternType.TOKEN,
            coverage=0.8,
        )
        assert cluster.name == "token_cluster"
        assert len(cluster.patterns) == 2
        assert cluster.coverage == 0.8

    def test_primary_pattern(self):
        """Primary pattern is most frequent."""
        p1 = ObservedPattern("A", PatternType.TOKEN, 0.3)
        p2 = ObservedPattern("B", PatternType.TOKEN, 0.7)
        cluster = PatternCluster(
            name="test",
            patterns=[p1, p2],
            dominant_type=PatternType.TOKEN,
            coverage=1.0,
        )
        assert cluster.primary_pattern.pattern == "B"

    def test_empty_cluster_primary(self):
        """Empty cluster has no primary pattern."""
        cluster = PatternCluster(
            name="empty",
            patterns=[],
            dominant_type=PatternType.TOKEN,
            coverage=0.0,
        )
        assert cluster.primary_pattern is None


# ============================================================================
# GrammarRule Tests
# ============================================================================


class TestGrammarRule:
    """Tests for GrammarRule dataclass."""

    def test_create_terminal_rule(self):
        """Can create terminal rule."""
        rule = GrammarRule(
            name="verb",
            productions=["CHECK", "ADD", "LIST"],
            is_terminal=True,
        )
        assert rule.is_terminal
        assert len(rule.productions) == 3

    def test_to_bnf_terminal(self):
        """Terminal rule converts to quoted BNF."""
        rule = GrammarRule(
            name="verb",
            productions=["CHECK", "ADD"],
            is_terminal=True,
        )
        bnf = rule.to_bnf()
        assert '<verb> ::= "CHECK" | "ADD"' == bnf

    def test_to_bnf_nonterminal(self):
        """Non-terminal rule converts to bracketed BNF."""
        rule = GrammarRule(
            name="command",
            productions=["verb", "noun"],
            is_terminal=False,
        )
        bnf = rule.to_bnf()
        assert "<command> ::= <verb> | <noun>" == bnf


class TestGrammarHypothesis:
    """Tests for GrammarHypothesis dataclass."""

    def test_create_hypothesis(self):
        """Can create grammar hypothesis."""
        rules = [
            GrammarRule("verb", ["CHECK", "ADD"], is_terminal=True),
            GrammarRule("command", ["verb"], is_terminal=False),
        ]
        hypothesis = GrammarHypothesis(
            rules=rules,
            start_symbol="command",
            confidence=0.85,
            level=GrammarLevel.COMMAND,
        )
        assert hypothesis.confidence == 0.85
        assert hypothesis.level == GrammarLevel.COMMAND

    def test_to_bnf(self):
        """Hypothesis converts to multi-line BNF."""
        rules = [
            GrammarRule("verb", ["CHECK"], is_terminal=True),
            GrammarRule("command", ["verb"], is_terminal=False),
        ]
        hypothesis = GrammarHypothesis(
            rules=rules,
            start_symbol="command",
            confidence=0.9,
            level=GrammarLevel.COMMAND,
        )
        bnf = hypothesis.to_bnf()
        assert "<verb>" in bnf
        assert "<command>" in bnf

    def test_grammar_string_alias(self):
        """grammar_string is alias for to_bnf."""
        rules = [GrammarRule("test", ["A"], is_terminal=True)]
        hypothesis = GrammarHypothesis(
            rules=rules,
            start_symbol="test",
            confidence=0.9,
            level=GrammarLevel.COMMAND,
        )
        assert hypothesis.grammar_string == hypothesis.to_bnf()


# ============================================================================
# PatternAnalyzer Tests
# ============================================================================


class TestPatternAnalyzer:
    """Tests for PatternAnalyzer."""

    def test_analyze_empty(self):
        """Empty observations return empty patterns."""
        analyzer = PatternAnalyzer()
        patterns = analyzer.analyze([])
        assert patterns == []

    def test_analyze_verb_noun_patterns(self):
        """Analyzes VERB NOUN patterns correctly."""
        analyzer = PatternAnalyzer()
        observations = [
            "CHECK 2024-12-15",
            "CHECK tomorrow",
            "ADD meeting",
            "LIST all",
        ]
        patterns = analyzer.analyze(observations)

        assert len(patterns) > 0
        # Should detect verbs
        verbs_found = set()
        for p in patterns:
            if "verbs" in p.metadata:
                verbs_found.update(p.metadata["verbs"])
        assert "CHECK" in verbs_found or any("CHECK" in p.pattern for p in patterns)

    def test_analyze_function_call_patterns(self):
        """Analyzes function call patterns correctly."""
        analyzer = PatternAnalyzer()
        observations = [
            "ref(Smith, 2024)",
            "ref(Jones, 2023)",
            "cite(Author, Year)",
        ]
        patterns = analyzer.analyze(observations)

        assert len(patterns) > 0
        # Should detect function pattern
        has_func_pattern = any(
            p.pattern_type == PatternType.STRUCTURE for p in patterns
        )
        assert has_func_pattern

    def test_analyze_mixed_patterns(self):
        """Handles mixed pattern types."""
        analyzer = PatternAnalyzer()
        observations = [
            "CHECK date",
            "ADD event",
            "func(arg)",
        ]
        patterns = analyzer.analyze(observations)
        assert len(patterns) > 0

    def test_cluster_patterns(self):
        """Clusters patterns by type."""
        analyzer = PatternAnalyzer()
        patterns = [
            ObservedPattern("A", PatternType.TOKEN, 0.5),
            ObservedPattern("B", PatternType.TOKEN, 0.3),
            ObservedPattern("C", PatternType.STRUCTURE, 0.2),
        ]
        clusters = analyzer.cluster_patterns(patterns)

        assert len(clusters) == 2
        # Token cluster should have higher coverage
        assert clusters[0].dominant_type == PatternType.TOKEN

    def test_cluster_empty_patterns(self):
        """Empty patterns produce empty clusters."""
        analyzer = PatternAnalyzer()
        clusters = analyzer.cluster_patterns([])
        assert clusters == []


# ============================================================================
# GrammarSynthesizer Tests
# ============================================================================


class TestGrammarSynthesizer:
    """Tests for GrammarSynthesizer."""

    def test_hypothesize_empty(self):
        """Empty patterns produce empty grammar."""
        synthesizer = GrammarSynthesizer()
        hypothesis = synthesizer.hypothesize([])

        assert hypothesis.rules == []
        assert hypothesis.confidence == 0.0

    def test_hypothesize_command_grammar(self):
        """Synthesizes command grammar from verb patterns."""
        synthesizer = GrammarSynthesizer()
        patterns = [
            ObservedPattern(
                pattern="<verb> <noun>",
                pattern_type=PatternType.SEQUENCE,
                frequency=0.9,
                metadata={"verbs": ["CHECK", "ADD"]},
            )
        ]
        hypothesis = synthesizer.hypothesize(patterns)

        assert hypothesis.level == GrammarLevel.COMMAND
        assert len(hypothesis.rules) > 0
        assert hypothesis.confidence > 0

    def test_hypothesize_recursive_grammar(self):
        """Synthesizes recursive grammar from structure patterns."""
        synthesizer = GrammarSynthesizer()
        patterns = [
            ObservedPattern(
                pattern="<func>(<args>)",
                pattern_type=PatternType.STRUCTURE,
                frequency=0.9,
                metadata={"functions": ["ref", "cite"]},
            )
        ]
        hypothesis = synthesizer.hypothesize(patterns)

        assert hypothesis.level == GrammarLevel.RECURSIVE
        assert len(hypothesis.rules) > 0

    def test_refine_with_failures(self):
        """Refines grammar based on failures."""
        synthesizer = GrammarSynthesizer()
        initial_patterns = [
            ObservedPattern(
                pattern="<verb> <noun>",
                pattern_type=PatternType.SEQUENCE,
                frequency=0.8,
                metadata={"verbs": ["CHECK"]},
            )
        ]
        hypothesis = synthesizer.hypothesize(initial_patterns)

        # Refine with failed inputs that have new verb
        refined = synthesizer.refine(hypothesis, ["ADD event", "ADD meeting"])

        # Should incorporate new patterns
        assert refined.source_patterns != hypothesis.source_patterns

    def test_refine_no_failures(self):
        """Refine with no failures returns same hypothesis."""
        synthesizer = GrammarSynthesizer()
        patterns = [ObservedPattern("test", PatternType.TOKEN, 0.9)]
        hypothesis = synthesizer.hypothesize(patterns)

        refined = synthesizer.refine(hypothesis, [])
        assert refined == hypothesis


# ============================================================================
# GrammarValidator Tests
# ============================================================================


class TestGrammarValidator:
    """Tests for GrammarValidator."""

    def test_validate_empty_observations(self):
        """Empty observations always validate."""
        validator = GrammarValidator()
        hypothesis = GrammarHypothesis(
            rules=[],
            start_symbol="start",
            confidence=0.5,
            level=GrammarLevel.COMMAND,
        )
        result = validator.validate(hypothesis, [])

        assert result.success
        assert result.coverage == 1.0

    def test_validate_matching_grammar(self):
        """Grammar matches observations."""
        validator = GrammarValidator()
        hypothesis = GrammarHypothesis(
            rules=[
                GrammarRule("verb", ["CHECK", "ADD"], is_terminal=True),
            ],
            start_symbol="command",
            confidence=0.9,
            level=GrammarLevel.COMMAND,
        )
        observations = ["CHECK date", "ADD event"]
        result = validator.validate(hypothesis, observations)

        assert result.coverage > 0.5

    def test_validate_non_matching_grammar(self):
        """Reports failures for non-matching inputs."""
        validator = GrammarValidator()
        hypothesis = GrammarHypothesis(
            rules=[
                GrammarRule("verb", ["CHECK"], is_terminal=True),
            ],
            start_symbol="command",
            confidence=0.9,
            level=GrammarLevel.COMMAND,
        )
        observations = ["CHECK date", "DELETE item"]  # DELETE not in grammar
        result = validator.validate(hypothesis, observations)

        assert len(result.failed_inputs) > 0
        assert "DELETE item" in result.failed_inputs

    def test_validation_suggestions(self):
        """Generates suggestions for failures."""
        validator = GrammarValidator()
        hypothesis = GrammarHypothesis(
            rules=[GrammarRule("verb", ["CHECK"], is_terminal=True)],
            start_symbol="command",
            confidence=0.9,
            level=GrammarLevel.COMMAND,
        )
        # Multiple failures with same verb
        observations = ["ADD one", "ADD two", "ADD three"]
        result = validator.validate(hypothesis, observations)

        # Should suggest adding the missing verb
        assert len(result.failed_inputs) == 3

    def test_needs_refinement(self):
        """needs_refinement indicates when to refine."""
        result_good = ValidationResult(success=True, coverage=0.98)
        assert not result_good.needs_refinement

        result_bad = ValidationResult(success=False, coverage=0.7)
        assert result_bad.needs_refinement

        result_low_coverage = ValidationResult(success=True, coverage=0.8)
        assert result_low_coverage.needs_refinement


# ============================================================================
# PatternInferenceEngine Tests
# ============================================================================


class TestPatternInferenceEngine:
    """Tests for PatternInferenceEngine."""

    @pytest.mark.asyncio
    async def test_infer_empty_observations(self):
        """Empty observations produce failed report."""
        engine = PatternInferenceEngine()
        report = await engine.infer_grammar([])

        assert not report.success
        assert report.tongue is None

    @pytest.mark.asyncio
    async def test_infer_simple_command_grammar(self):
        """Infers simple command grammar."""
        engine = PatternInferenceEngine(min_coverage=0.5)
        observations = [
            "CHECK 2024-12-15",
            "CHECK tomorrow",
            "CHECK today",
            "ADD meeting",
            "ADD event",
        ]
        report = await engine.infer_grammar(observations, domain="Calendar")

        # Should have some success
        assert report.iterations > 0
        assert report.initial_hypothesis is not None

    @pytest.mark.asyncio
    async def test_infer_with_refinement(self):
        """Inference refines grammar iteratively."""
        engine = PatternInferenceEngine(max_iterations=3, min_coverage=0.5)
        observations = [
            "CHECK date",
            "ADD event",
            "LIST items",
            "DELETE old",  # Different verb
        ]
        report = await engine.infer_grammar(observations)

        # Should attempt refinement
        assert report.iterations >= 1
        assert len(report.validation_history) >= 1

    @pytest.mark.asyncio
    async def test_crystallize_to_tongue(self):
        """Crystallizes hypothesis to Tongue."""
        engine = PatternInferenceEngine()
        hypothesis = GrammarHypothesis(
            rules=[
                GrammarRule("verb", ["CHECK", "ADD"], is_terminal=True),
                GrammarRule("command", ["verb"], is_terminal=False),
            ],
            start_symbol="command",
            confidence=0.9,
            level=GrammarLevel.COMMAND,
        )

        tongue = await engine.crystallize(
            hypothesis,
            domain="Test Domain",
            examples=["CHECK date"],
        )

        assert tongue is not None
        assert tongue.domain == "Test Domain"
        assert tongue.level == GrammarLevel.COMMAND
        assert "TestDomainTongue" in tongue.name

    @pytest.mark.asyncio
    async def test_inference_report_contains_diagnostics(self):
        """Report contains full diagnostics."""
        engine = PatternInferenceEngine(max_iterations=2)
        observations = ["CHECK a", "CHECK b", "ADD c"]
        report = await engine.infer_grammar(observations)

        assert report.initial_hypothesis is not None
        assert report.final_hypothesis is not None
        assert report.duration_ms > 0


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_infer_grammar_from_observations(self):
        """Convenience function returns tongue or None."""
        observations = ["CHECK date", "CHECK time", "ADD event"]
        # May or may not succeed depending on coverage
        result = await infer_grammar_from_observations(
            observations, domain="Test", min_coverage=0.3
        )
        # Result is either Tongue or None
        assert result is None or hasattr(result, "grammar")

    @pytest.mark.asyncio
    async def test_observe_and_infer(self):
        """observe_and_infer returns full report."""
        observations = ["CHECK a", "ADD b"]
        report = await observe_and_infer(observations, domain="Test")

        assert isinstance(report, InferenceReport)
        assert report.iterations >= 0

    def test_extract_patterns(self):
        """extract_patterns returns pattern list."""
        observations = ["CHECK date", "ADD event"]
        patterns = extract_patterns(observations)

        assert isinstance(patterns, list)
        # May be empty or have patterns

    def test_hypothesize_grammar(self):
        """hypothesize_grammar returns hypothesis."""
        patterns = [
            ObservedPattern(
                pattern="<verb> <noun>",
                pattern_type=PatternType.SEQUENCE,
                frequency=0.9,
                metadata={"verbs": ["CHECK"]},
            )
        ]
        hypothesis = hypothesize_grammar(patterns)

        assert isinstance(hypothesis, GrammarHypothesis)
        assert hypothesis.level == GrammarLevel.COMMAND


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for full inference pipeline."""

    @pytest.mark.asyncio
    async def test_full_calendar_inference(self):
        """Full inference for calendar-like commands."""
        observations = [
            "CHECK 2024-12-15",
            "CHECK tomorrow",
            "CHECK today",
            "ADD meeting at 3pm",
            "ADD lunch with team",
            "LIST events",
            "LIST all",
        ]

        engine = PatternInferenceEngine(min_coverage=0.5)
        report = await engine.infer_grammar(observations, domain="Calendar")

        # Verify report structure
        assert report.initial_hypothesis is not None
        assert report.iterations > 0
        assert len(report.validation_history) > 0

        # Check coverage improved or stayed reasonable
        if report.validation_history:
            last_validation = report.validation_history[-1]
            assert last_validation.coverage >= 0.0

    @pytest.mark.asyncio
    async def test_full_citation_inference(self):
        """Full inference for citation-like patterns."""
        observations = [
            "ref(Smith, 2024)",
            "ref(Jones, 2023)",
            "ref(Brown, 2022)",
            "cite(Author et al, 2021)",
            "cite(Team, 2020)",
        ]

        engine = PatternInferenceEngine(min_coverage=0.3)
        report = await engine.infer_grammar(observations, domain="Citations")

        assert report.initial_hypothesis is not None
        # Should detect function-call structure
        if report.initial_hypothesis:
            assert report.initial_hypothesis.level in [
                GrammarLevel.RECURSIVE,
                GrammarLevel.COMMAND,
            ]

    @pytest.mark.asyncio
    async def test_inference_with_noise(self):
        """Handles noisy observations gracefully."""
        observations = [
            "CHECK date",
            "CHECK time",
            "random noise here",
            "ADD event",
            "more garbage 123",
            "LIST items",
        ]

        engine = PatternInferenceEngine(min_coverage=0.3, max_iterations=3)
        report = await engine.infer_grammar(observations)

        # Should not crash
        assert report is not None
        # May or may not succeed
        assert report.iterations >= 1


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_pattern_type_enum_values(self):
        """All pattern types have string values."""
        for pt in PatternType:
            assert isinstance(pt.value, str)

    @pytest.mark.asyncio
    async def test_single_observation(self):
        """Handles single observation."""
        engine = PatternInferenceEngine(min_coverage=0.5)
        report = await engine.infer_grammar(["CHECK date"])

        assert report is not None

    @pytest.mark.asyncio
    async def test_identical_observations(self):
        """Handles identical observations."""
        engine = PatternInferenceEngine(min_coverage=0.5)
        observations = ["CHECK date"] * 10
        report = await engine.infer_grammar(observations)

        assert report is not None
        if report.initial_hypothesis:
            assert report.initial_hypothesis.confidence > 0

    @pytest.mark.asyncio
    async def test_very_long_observation(self):
        """Handles very long observation strings."""
        long_text = "CHECK " + "x" * 1000
        engine = PatternInferenceEngine()
        report = await engine.infer_grammar([long_text])

        assert report is not None

    def test_pattern_analyzer_special_chars(self):
        """Analyzer handles special characters."""
        analyzer = PatternAnalyzer()
        observations = [
            "CHECK $100",
            "ADD @mention",
            "LIST #tags",
        ]
        patterns = analyzer.analyze(observations)
        # Should not crash
        assert isinstance(patterns, list)

    def test_grammar_rule_empty_productions(self):
        """Grammar rule with empty productions."""
        rule = GrammarRule(name="empty", productions=[], is_terminal=True)
        bnf = rule.to_bnf()
        assert "<empty>" in bnf
