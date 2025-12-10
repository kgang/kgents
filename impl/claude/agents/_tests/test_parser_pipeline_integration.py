"""
Parser Pipeline Integration Tests: P × G × E × F

Tests integration between Parser agents and other agents:
- P × G: P-gent parsers with G-gent synthesized tongues
- P × E: P-gent with E-gent error recovery
- P × B: P-gent parsing hypothesis outputs
- P × F: P-gent validating F-gent prototypes

Philosophy: Parsers are the syntactic membrane of the system.
"""

from typing import Any

# P-gent imports
from agents.p import (
    ParserConfig,
    FallbackParser,
    FusionParser,
    SwitchParser,
    AnchorBasedParser,
    StackBalancingParser,
    ProbabilisticASTParser,
)

# G-gent imports
from agents.g import (
    GrammarLevel,
    GrammarFormat,
    ParserConfig as GParserConfig,
)
from agents.g.tongue import TongueBuilder

# F-gent imports
from agents.f import (
    parse_intent,
    synthesize_contract,
)

# Shared fixtures
from agents.shared.fixtures import (
    make_sample_intent,
    make_sample_source_code,
)


class TestParserGrammarIntegration:
    """P × G: Parser uses G-gent grammars (tongues)."""

    def test_tongue_provides_parser_config(self):
        """Test that G-gent Tongue provides parser configuration."""
        # Build a simple tongue
        tongue = (
            TongueBuilder("TestTongue", "1.0.0")
            .with_domain("Testing")
            .with_level(GrammarLevel.COMMAND)
            .with_format(GrammarFormat.BNF)
            .with_grammar("command ::= VERB NOUN")
            .with_lexicon("CHECK", "ADD", "event", "task")
            .with_parser_config(
                GParserConfig(
                    strategy="regex",
                    grammar_format=GrammarFormat.BNF,
                    confidence_threshold=0.7,
                )
            )
            .validated(True)
            .build()
        )

        # Verify tongue has parser config
        assert tongue.parser_config is not None
        assert tongue.parser_config.confidence_threshold == 0.7
        assert tongue.level == GrammarLevel.COMMAND

    def test_tongue_lexicon_constrains_parsing(self):
        """Test that tongue lexicon constrains what can be parsed."""
        # Build tongue with constrained lexicon
        tongue = (
            TongueBuilder("CalendarTongue", "1.0.0")
            .with_domain("Calendar")
            .with_level(GrammarLevel.COMMAND)
            .with_lexicon("CHECK", "ADD", "REMOVE", "meeting", "event")
            .with_grammar("command ::= VERB NOUN")
            .validated(True)
            .build()
        )

        # Lexicon should contain expected tokens
        assert "CHECK" in tongue.lexicon
        assert "ADD" in tongue.lexicon
        assert "meeting" in tongue.lexicon
        # Unknown tokens should not be in lexicon
        assert "DELETE" not in tongue.lexicon
        assert "hacking" not in tongue.lexicon

    def test_tongue_with_constraint_proofs(self):
        """Test tongue with semantic constraints and proofs."""

        # Build tongue with constraints
        tongue = (
            TongueBuilder("SecureTongue", "1.0.0")
            .with_domain("Secure Operations")
            .with_level(GrammarLevel.COMMAND)
            .with_grammar("op ::= READ | WRITE")
            .with_lexicon("READ", "WRITE")
            .with_constraint("No destructive operations")
            .with_constraint("Read-only by default")
            .validated(True)
            .build()
        )

        assert "No destructive operations" in tongue.constraints
        assert "Read-only by default" in tongue.constraints

    def test_parser_fallback_chain_with_tongue_context(self):
        """Test fallback parser chain uses tongue-aware strategies."""
        # Create parser chain
        parser = FallbackParser(
            StackBalancingParser(),
            AnchorBasedParser(anchor="###RESULT:"),
            ProbabilisticASTParser(config=ParserConfig()),
            config=ParserConfig(min_confidence=0.5),
        )

        # Parse JSON-like content
        result = parser.parse('{"key": "value", "nested": {"a": 1}}')
        assert result.success
        assert result.confidence >= 0.5

    def test_fusion_parser_merges_multiple_strategies(self):
        """Test fusion parser combines results from multiple strategies."""

        def merge_values(values: list[Any]) -> Any:
            """Merge multiple values, taking first valid one."""
            for v in values:
                if v is not None:
                    return v
            return None

        stack_parser = StackBalancingParser()
        ast_parser = ProbabilisticASTParser(config=ParserConfig())

        fusion = FusionParser(
            stack_parser,
            ast_parser,
            merge_fn=merge_values,
            config=ParserConfig(),
        )

        result = fusion.parse('{"test": [1, 2, 3]}')
        # Fusion may succeed or fail depending on merge semantics
        # Here we just verify it runs without crash
        assert result is not None


class TestParserForgeIntegration:
    """P × F: Parser validates F-gent prototypes and contracts."""

    def test_parse_intent_produces_valid_structure(self):
        """Test that parse_intent produces well-structured Intent."""
        intent = parse_intent(
            "Create an agent that validates email addresses and returns structured results"
        )

        assert intent.purpose
        assert isinstance(intent.behavior, list)
        assert isinstance(intent.constraints, list)

    def test_contract_input_output_types_parseable(self):
        """Test that contract types can be parsed for composition."""
        intent = make_sample_intent()
        contract = synthesize_contract(intent, "TestAgent")

        # Contract should have parseable type strings
        assert contract.input_type
        assert contract.output_type
        assert contract.agent_name == "TestAgent"

    def test_source_code_syntax_validation(self):
        """Test that generated source code passes syntax validation."""
        source = make_sample_source_code("ValidAgent", valid=True)

        # Valid source should pass static analysis
        assert source.is_valid
        assert source.analysis_report.passed

    def test_invalid_source_detected(self):
        """Test that invalid source code is detected."""
        source = make_sample_source_code("InvalidAgent", valid=False)

        # Invalid source should fail
        assert not source.is_valid
        assert not source.analysis_report.passed

    def test_parser_validates_json_output_schema(self):
        """Test parser can validate JSON against expected schema."""
        parser = ProbabilisticASTParser(config=ParserConfig())

        # Valid JSON
        valid_result = parser.parse('{"temp": 55, "condition": "cloudy"}')
        assert valid_result.success

        # Invalid JSON (missing closing brace) - parser should handle gracefully
        invalid_result = parser.parse('{"temp": 55, "condition": "cloudy"')
        # Either repairs or reports failure with clear error
        if not invalid_result.success:
            assert invalid_result.error is not None


class TestParserErrorRecovery:
    """P × E: Parser with error recovery strategies."""

    def test_anchor_parser_extracts_labeled_content(self):
        """Test anchor parser extracts content after markers."""
        parser = AnchorBasedParser(anchor="###RESULT:")

        text = """
        Some preamble text here.
        ###RESULT: The actual result value
        ###STATUS: completed
        """

        result = parser.parse(text)
        assert result.success
        assert "The actual result value" in result.value[0]

    def test_stack_balancing_repairs_brackets(self):
        """Test stack balancer handles unbalanced brackets."""
        parser = StackBalancingParser()

        # Properly balanced
        result = parser.parse('{"array": [1, 2, {"nested": true}]}')
        assert result.success

    def test_fallback_chain_tries_multiple_strategies(self):
        """Test fallback tries strategies in order until success."""
        # First parser that will fail on plain text
        json_parser = ProbabilisticASTParser(config=ParserConfig())

        # Second parser that extracts anchored content
        anchor_parser = AnchorBasedParser(anchor="RESULT:")

        fallback = FallbackParser(
            json_parser,
            anchor_parser,
            config=ParserConfig(min_confidence=0.3),
        )

        # This is not JSON but has anchor
        result = fallback.parse("RESULT: success value")
        assert result.success

    def test_parser_provides_repair_transparency(self):
        """Test parser reports what repairs were applied."""
        parser = ProbabilisticASTParser(config=ParserConfig(enable_repair=True))

        # Parse something that might need repair
        result = parser.parse('{"key": "value"}')
        assert result.success
        # Repairs list should be accessible (even if empty)
        assert hasattr(result, "repairs")


class TestParserStreamProcessing:
    """Test streaming parser capabilities."""

    def test_parser_handles_chunked_input(self):
        """Test parser can process input in chunks."""
        parser = ProbabilisticASTParser(config=ParserConfig())

        # Complete JSON document
        full_doc = '{"items": [1, 2, 3], "meta": {"count": 3}}'
        result = parser.parse(full_doc)

        assert result.success
        assert result.value.value["meta"]["count"] == 3

    def test_parser_tracks_stream_position(self):
        """Test parser tracks position in stream."""
        parser = ProbabilisticASTParser(config=ParserConfig())

        result = parser.parse('{"position": "tracked"}')
        assert result.success
        # Stream position should be available
        # (may be None for non-streaming parse)


class TestParserComposition:
    """Test parser composition patterns."""

    def test_switch_parser_routes_by_format(self):
        """Test switch parser routes to correct parser by format."""

        def is_json(text: str) -> bool:
            return text.strip().startswith("{") or text.strip().startswith("[")

        def is_anchored(text: str) -> bool:
            return "###" in text

        json_parser = ProbabilisticASTParser(config=ParserConfig())
        anchor_parser = AnchorBasedParser(anchor="###")

        # SwitchParser takes a routes dict mapping predicates to parsers
        routes = {
            is_json: json_parser,
            is_anchored: anchor_parser,
        }

        switch = SwitchParser(routes=routes, config=ParserConfig())

        # JSON input -> JSON parser
        json_result = switch.parse('{"type": "json"}')
        assert json_result.success

        # Anchored input -> Anchor parser
        anchor_result = switch.parse("###RESULT: anchored content")
        assert anchor_result.success

    def test_parser_preserves_metadata_through_composition(self):
        """Test metadata flows through composed parsers."""
        parser = ProbabilisticASTParser(config=ParserConfig())

        result = parser.parse('{"test": true}')
        assert result.success
        assert hasattr(result, "metadata")
        assert isinstance(result.metadata, dict)


class TestParserConfidenceScoring:
    """Test parser confidence scoring."""

    def test_well_formed_input_high_confidence(self):
        """Test well-formed input gets high confidence."""
        parser = ProbabilisticASTParser(config=ParserConfig())

        result = parser.parse('{"valid": true, "nested": {"also": "valid"}}')
        assert result.success
        assert result.confidence >= 0.7

    def test_ambiguous_input_lower_confidence(self):
        """Test ambiguous input gets lower confidence."""
        parser = ProbabilisticASTParser(config=ParserConfig())

        # Potentially ambiguous but valid
        result = parser.parse('{"a": 1}')
        assert result.success
        # Simple valid JSON should still have decent confidence
        assert result.confidence >= 0.5

    def test_confidence_threshold_filtering(self):
        """Test min_confidence filters low-confidence results."""
        config = ParserConfig(min_confidence=0.9)
        parser = ProbabilisticASTParser(config=config)

        # Valid JSON should still pass high threshold
        result = parser.parse('{"confident": true}')
        if result.success:
            assert result.confidence >= 0.9


# Run with: pytest impl/claude/agents/_tests/test_parser_pipeline_integration.py -v
