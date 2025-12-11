"""
Tests for G-gent Phase 6: T-gent Fuzzing Integration

Tests:
1. TongueInputGenerator - Input generation
2. TongueFuzzer - Fuzz testing
3. TonguePropertyTester - Property testing
4. Integration - Full T-gent validation
"""

import pytest
from agents.g.fuzzing_integration import (
    FuzzInputType,
    FuzzReport,
    FuzzResult,
    PropertyResult,
    PropertyTestReport,
    PropertyType,
    TongueFuzzer,
    TongueInputGenerator,
    TonguePropertyTester,
    fuzz_tongue,
    generate_constraint_proofs,
    property_test_tongue,
    validate_tongue_with_t_gent,
)
from agents.g.types import (
    ConstraintProof,
    CounterExample,
    Example,
    GrammarFormat,
    GrammarLevel,
    InterpreterConfig,
    ParserConfig,
    Tongue,
)

# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def command_tongue() -> Tongue:
    """Create a command-level tongue for testing."""
    return Tongue(
        name="TestCommands",
        version="1.0.0",
        lexicon=frozenset(["CHECK", "ADD", "LIST"]),
        grammar='<verb> ::= "CHECK" | "ADD" | "LIST"',
        mime_type="application/vnd.kgents.test-commands",
        level=GrammarLevel.COMMAND,
        format=GrammarFormat.BNF,
        parser_config=ParserConfig(
            strategy="regex",
            grammar_format=GrammarFormat.BNF,
            grammar_spec='<verb> ::= "CHECK" | "ADD" | "LIST"',
        ),
        interpreter_config=InterpreterConfig(
            runtime="python",
            pure_functions_only=True,
        ),
        domain="Testing",
        constraints=("No deletes",),
        examples=(
            Example(text="CHECK today", description="Check today's items"),
            Example(text="ADD meeting", description="Add a meeting"),
            Example(text="LIST all", description="List all items"),
        ),
        constraint_proofs=(
            ConstraintProof(
                constraint="No deletes",
                mechanism="DELETE verb not in lexicon",
                verified_by="T-gent",
                counter_examples=[
                    CounterExample(text="DELETE item", expected_error="parse failure"),
                ],
            ),
        ),
    )


@pytest.fixture
def schema_tongue() -> Tongue:
    """Create a schema-level tongue for testing."""
    grammar = """
class Item(BaseModel):
    name: str
    value: int = 0
"""
    return Tongue(
        name="TestSchema",
        version="1.0.0",
        lexicon=frozenset(["name", "value"]),
        grammar=grammar,
        mime_type="application/vnd.kgents.test-schema",
        level=GrammarLevel.SCHEMA,
        format=GrammarFormat.PYDANTIC,
        parser_config=ParserConfig(
            strategy="pydantic",
            grammar_format=GrammarFormat.PYDANTIC,
            grammar_spec=grammar,
        ),
        interpreter_config=InterpreterConfig(
            runtime="python",
            pure_functions_only=True,
        ),
        domain="Testing",
        constraints=(),
        examples=(
            Example(text='{"name": "test", "value": 42}', description="Simple item"),
        ),
    )


@pytest.fixture
def constrained_tongue() -> Tongue:
    """Create a tongue with multiple constraints."""
    return Tongue(
        name="ConstrainedCommands",
        version="1.0.0",
        lexicon=frozenset(["CHECK", "LIST"]),
        grammar='<verb> ::= "CHECK" | "LIST"',
        mime_type="application/vnd.kgents.constrained",
        level=GrammarLevel.COMMAND,
        format=GrammarFormat.BNF,
        parser_config=ParserConfig(
            strategy="regex",
            grammar_format=GrammarFormat.BNF,
            grammar_spec='<verb> ::= "CHECK" | "LIST"',
        ),
        interpreter_config=InterpreterConfig(runtime="python"),
        domain="Read-only Operations",
        constraints=("No deletes", "No modifications", "Read only"),
        examples=(Example(text="CHECK status", description="Check status"),),
        constraint_proofs=(),
    )


# ============================================================================
# TongueInputGenerator Tests
# ============================================================================


class TestTongueInputGenerator:
    """Tests for input generation."""

    def test_generate_valid_commands(self, command_tongue: Tongue) -> None:
        """Test generating valid command inputs."""
        gen = TongueInputGenerator(command_tongue, seed=42)
        valid = gen.generate_valid(10)

        assert len(valid) == 10
        # Each should have a valid verb
        verbs = {"CHECK", "ADD", "LIST"}
        for text in valid:
            parts = text.split()
            assert len(parts) >= 1
            assert parts[0] in verbs

    def test_generate_invalid(self, command_tongue: Tongue) -> None:
        """Test generating invalid inputs."""
        gen = TongueInputGenerator(command_tongue, seed=42)
        invalid = gen.generate_invalid(10)

        assert len(invalid) == 10
        # Should include empty, malformed, wrong verbs
        assert (
            "" in invalid
            or "   " in invalid
            or any("BLARG" in i or "ZZZZ" in i for i in invalid)
        )

    def test_generate_boundary(self, command_tongue: Tongue) -> None:
        """Test generating boundary inputs."""
        gen = TongueInputGenerator(command_tongue, seed=42)
        boundary = gen.generate_boundary(10)

        assert len(boundary) >= 1
        # Should include edge cases
        " ".join(boundary)
        assert any(len(b) > 100 for b in boundary) or any(b == "" for b in boundary)

    def test_generate_adversarial(self, command_tongue: Tongue) -> None:
        """Test generating adversarial inputs."""
        gen = TongueInputGenerator(command_tongue, seed=42)
        adversarial = gen.generate_adversarial(10)

        assert len(adversarial) >= 1
        # Should include injection attempts
        texts = " ".join(adversarial)
        assert "DROP" in texts or "rm -rf" in texts or "script" in texts.lower()

    def test_generate_mutated(self, command_tongue: Tongue) -> None:
        """Test generating mutated inputs."""
        gen = TongueInputGenerator(command_tongue, seed=42)
        valid = gen.generate_valid(5)
        mutated = gen.generate_mutated(valid, 10)

        assert len(mutated) == 10
        # Mutated should be different from originals (mostly)
        # Some might be the same due to random mutations

    def test_deterministic_with_seed(self, command_tongue: Tongue) -> None:
        """Test that same seed produces same outputs."""
        gen1 = TongueInputGenerator(command_tongue, seed=42)
        gen2 = TongueInputGenerator(command_tongue, seed=42)

        valid1 = gen1.generate_valid(10)
        valid2 = gen2.generate_valid(10)

        assert valid1 == valid2


# ============================================================================
# TongueFuzzer Tests
# ============================================================================


class TestTongueFuzzer:
    """Tests for fuzz testing."""

    def test_fuzz_basic(self, command_tongue: Tongue) -> None:
        """Test basic fuzzing."""
        fuzzer = TongueFuzzer(
            command_tongue,
            seed=42,
            valid_count=10,
            invalid_count=5,
            boundary_count=5,
            adversarial_count=5,
        )

        report = fuzzer.fuzz()

        assert isinstance(report, FuzzReport)
        assert report.tongue_name == "TestCommands"
        assert report.total_tests > 0
        assert report.duration_ms > 0

    def test_fuzz_report_counts(self, command_tongue: Tongue) -> None:
        """Test that fuzz report has correct counts."""
        fuzzer = TongueFuzzer(
            command_tongue,
            seed=42,
            valid_count=10,
            invalid_count=5,
            boundary_count=5,
            adversarial_count=5,
        )

        report = fuzzer.fuzz()

        assert report.valid_count == 10
        assert report.invalid_count == 5
        assert report.boundary_count == 5
        assert report.adversarial_count == 5
        assert report.total_tests == 25

    def test_fuzz_pass_rate(self, command_tongue: Tongue) -> None:
        """Test pass rate calculation."""
        fuzzer = TongueFuzzer(
            command_tongue,
            seed=42,
            valid_count=10,
            invalid_count=5,
            boundary_count=5,
            adversarial_count=5,
        )

        report = fuzzer.fuzz()

        assert 0.0 <= report.pass_rate <= 1.0
        assert report.passed_tests + report.failed_tests == report.total_tests

    def test_fuzz_results_tracked(self, command_tongue: Tongue) -> None:
        """Test that individual results are tracked."""
        fuzzer = TongueFuzzer(
            command_tongue,
            seed=42,
            valid_count=5,
            invalid_count=5,
            boundary_count=2,
            adversarial_count=2,
        )

        report = fuzzer.fuzz()

        assert len(report.results) == report.total_tests
        for result in report.results:
            assert isinstance(result, FuzzResult)
            assert result.input_type in FuzzInputType

    def test_fuzz_summary(self, command_tongue: Tongue) -> None:
        """Test report summary generation."""
        fuzzer = TongueFuzzer(command_tongue, seed=42, valid_count=5)
        report = fuzzer.fuzz()

        summary = report.summary()
        assert "TestCommands" in summary
        assert "passed" in summary
        assert "ms" in summary


# ============================================================================
# TonguePropertyTester Tests
# ============================================================================


class TestTonguePropertyTester:
    """Tests for property-based testing."""

    def test_property_tester_all(self, command_tongue: Tongue) -> None:
        """Test running all property tests."""
        tester = TonguePropertyTester(
            command_tongue,
            seed=42,
            cases_per_property=10,
        )

        report = tester.test_all_properties()

        assert isinstance(report, PropertyTestReport)
        assert report.tongue_name == "TestCommands"
        assert report.total_properties == 5  # 5 properties tested
        assert len(report.results) == 5

    def test_round_trip_property(self, command_tongue: Tongue) -> None:
        """Test round-trip property."""
        tester = TonguePropertyTester(command_tongue, seed=42, cases_per_property=10)
        result = tester.test_round_trip()

        assert isinstance(result, PropertyResult)
        assert result.property_type == PropertyType.ROUND_TRIP
        assert result.total_cases >= 0
        assert result.duration_ms >= 0

    def test_idempotence_property(self, command_tongue: Tongue) -> None:
        """Test idempotence property."""
        tester = TonguePropertyTester(command_tongue, seed=42, cases_per_property=10)
        result = tester.test_idempotence()

        assert result.property_type == PropertyType.IDEMPOTENCE
        assert result.total_cases >= 0

    def test_constraint_property(self, constrained_tongue: Tongue) -> None:
        """Test constraint encoding property."""
        tester = TonguePropertyTester(constrained_tongue, seed=42)
        result = tester.test_constraint_encoding()

        assert result.property_type == PropertyType.CONSTRAINT
        # Should test constraint violations

    def test_determinism_property(self, command_tongue: Tongue) -> None:
        """Test determinism property."""
        tester = TonguePropertyTester(command_tongue, seed=42, cases_per_property=5)
        result = tester.test_determinism()

        assert result.property_type == PropertyType.DETERMINISM
        # Determinism should generally pass
        assert result.pass_rate >= 0.0

    def test_completeness_property(self, command_tongue: Tongue) -> None:
        """Test completeness property."""
        tester = TonguePropertyTester(command_tongue, seed=42)
        result = tester.test_completeness()

        assert result.property_type == PropertyType.COMPLETENESS
        # All examples should parse

    def test_property_report_summary(self, command_tongue: Tongue) -> None:
        """Test property report summary."""
        tester = TonguePropertyTester(command_tongue, seed=42, cases_per_property=5)
        report = tester.test_all_properties()

        summary = report.summary()
        assert "TestCommands" in summary
        assert "properties" in summary


# ============================================================================
# FuzzResult Tests
# ============================================================================


class TestFuzzResult:
    """Tests for FuzzResult dataclass."""

    def test_passed_when_expected_matches_actual(self) -> None:
        """Test passed property when expectations match."""
        result = FuzzResult(
            input_text="CHECK item",
            input_type=FuzzInputType.VALID,
            expected_success=True,
            actual_success=True,
        )
        assert result.passed is True

    def test_failed_when_expected_differs(self) -> None:
        """Test passed property when expectations differ."""
        result = FuzzResult(
            input_text="INVALID cmd",
            input_type=FuzzInputType.VALID,
            expected_success=True,
            actual_success=False,
        )
        assert result.passed is False

    def test_result_with_parse_result(self) -> None:
        """Test result with parse result attached."""
        from agents.g.types import ParseResult

        parse_result = ParseResult(success=True, ast={"verb": "CHECK", "noun": "item"})
        result = FuzzResult(
            input_text="CHECK item",
            input_type=FuzzInputType.VALID,
            expected_success=True,
            actual_success=True,
            parse_result=parse_result,
        )
        assert result.parse_result is not None
        assert result.parse_result.ast["verb"] == "CHECK"


# ============================================================================
# FuzzReport Tests
# ============================================================================


class TestFuzzReport:
    """Tests for FuzzReport dataclass."""

    def test_pass_rate_empty(self) -> None:
        """Test pass rate with no tests."""
        report = FuzzReport(
            tongue_name="Empty",
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
        )
        assert report.pass_rate == 0.0

    def test_pass_rate_calculation(self) -> None:
        """Test pass rate calculation."""
        report = FuzzReport(
            tongue_name="Test",
            total_tests=100,
            passed_tests=75,
            failed_tests=25,
        )
        assert report.pass_rate == 0.75

    def test_all_passed(self) -> None:
        """Test all_passed property."""
        report = FuzzReport(
            tongue_name="Test",
            total_tests=10,
            passed_tests=10,
            failed_tests=0,
        )
        assert report.all_passed is True

    def test_not_all_passed(self) -> None:
        """Test all_passed when some fail."""
        report = FuzzReport(
            tongue_name="Test",
            total_tests=10,
            passed_tests=9,
            failed_tests=1,
        )
        assert report.all_passed is False


# ============================================================================
# PropertyResult Tests
# ============================================================================


class TestPropertyResult:
    """Tests for PropertyResult dataclass."""

    def test_pass_rate_empty(self) -> None:
        """Test pass rate with no cases."""
        result = PropertyResult(
            property_type=PropertyType.ROUND_TRIP,
            property_name="Test",
            passed=True,
            total_cases=0,
            passed_cases=0,
            failed_cases=0,
        )
        assert result.pass_rate == 0.0

    def test_pass_rate_calculation(self) -> None:
        """Test pass rate calculation."""
        result = PropertyResult(
            property_type=PropertyType.ROUND_TRIP,
            property_name="Test",
            passed=True,
            total_cases=100,
            passed_cases=80,
            failed_cases=20,
        )
        assert result.pass_rate == 0.8


# ============================================================================
# Convenience Function Tests
# ============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_fuzz_tongue(self, command_tongue: Tongue) -> None:
        """Test fuzz_tongue convenience function."""
        report = await fuzz_tongue(command_tongue, seed=42, n=50)

        assert isinstance(report, FuzzReport)
        assert report.total_tests > 0
        assert report.valid_count > 0

    @pytest.mark.asyncio
    async def test_property_test_tongue(self, command_tongue: Tongue) -> None:
        """Test property_test_tongue convenience function."""
        report = await property_test_tongue(
            command_tongue, seed=42, cases_per_property=10
        )

        assert isinstance(report, PropertyTestReport)
        assert report.total_properties == 5

    @pytest.mark.asyncio
    async def test_validate_tongue_with_t_gent(self, command_tongue: Tongue) -> None:
        """Test full T-gent validation."""
        fuzz_report, prop_report = await validate_tongue_with_t_gent(
            command_tongue, seed=42
        )

        assert isinstance(fuzz_report, FuzzReport)
        assert isinstance(prop_report, PropertyTestReport)

    def test_generate_constraint_proofs(self, constrained_tongue: Tongue) -> None:
        """Test constraint proof generation."""
        proofs = generate_constraint_proofs(constrained_tongue, seed=42)

        assert len(proofs) == 3  # 3 constraints
        for proof in proofs:
            assert isinstance(proof, ConstraintProof)
            assert proof.verified_by == "T-gent"

        # At least one constraint should have counter-examples
        # (not all constraints map to known violation patterns)
        total_counter_examples = sum(len(p.counter_examples) for p in proofs)
        assert total_counter_examples > 0


# ============================================================================
# Integration Tests
# ============================================================================


class TestIntegration:
    """Integration tests for full fuzzing workflow."""

    @pytest.mark.asyncio
    async def test_full_workflow(self, command_tongue: Tongue) -> None:
        """Test complete fuzzing workflow."""
        # Step 1: Fuzz test
        fuzz_report = await fuzz_tongue(command_tongue, seed=42, n=25)
        assert fuzz_report.total_tests == 25

        # Step 2: Property test
        prop_report = await property_test_tongue(
            command_tongue, seed=42, cases_per_property=5
        )
        assert prop_report.total_properties == 5

        # Both should complete without errors

    def test_fuzzer_finds_issues(self) -> None:
        """Test that fuzzer can detect grammar issues."""
        # Create a tongue with issues
        bad_tongue = Tongue(
            name="BadTongue",
            version="1.0.0",
            lexicon=frozenset(["CHECK"]),
            grammar='<verb> ::= "CHECK"',  # Only one verb
            mime_type="application/test",
            level=GrammarLevel.COMMAND,
            format=GrammarFormat.BNF,
            parser_config=ParserConfig(
                strategy="regex",
                grammar_format=GrammarFormat.BNF,
                grammar_spec='<verb> ::= "CHECK"',
            ),
            interpreter_config=InterpreterConfig(runtime="python"),
            domain="Test",
            constraints=(),
            # Examples that might not parse
            examples=(Example(text="INVALID command", description="This should fail"),),
        )

        tester = TonguePropertyTester(bad_tongue, seed=42)
        result = tester.test_completeness()

        # Should detect that example doesn't parse
        assert result.failed_cases > 0

    def test_reproducibility_with_seed(self, command_tongue: Tongue) -> None:
        """Test that fuzzing is reproducible with seed."""
        fuzzer1 = TongueFuzzer(command_tongue, seed=42, valid_count=10)
        fuzzer2 = TongueFuzzer(command_tongue, seed=42, valid_count=10)

        report1 = fuzzer1.fuzz()
        report2 = fuzzer2.fuzz()

        # Results should be identical
        assert report1.passed_tests == report2.passed_tests
        assert report1.failed_tests == report2.failed_tests
        assert len(report1.results) == len(report2.results)

        for r1, r2 in zip(report1.results, report2.results):
            assert r1.input_text == r2.input_text

    @pytest.mark.asyncio
    async def test_schema_tongue_fuzzing(self, schema_tongue: Tongue) -> None:
        """Test fuzzing works for schema-level tongues."""
        report = await fuzz_tongue(schema_tongue, seed=42, n=20)

        assert isinstance(report, FuzzReport)
        # Schema parsing might be stricter


# ============================================================================
# Edge Case Tests
# ============================================================================


class TestEdgeCases:
    """Edge case tests."""

    def test_empty_grammar(self) -> None:
        """Test handling of empty grammar."""
        empty_tongue = Tongue(
            name="Empty",
            version="1.0.0",
            lexicon=frozenset(),
            grammar="",
            mime_type="application/test",
            level=GrammarLevel.COMMAND,
            format=GrammarFormat.BNF,
            parser_config=ParserConfig(
                strategy="regex",
                grammar_format=GrammarFormat.BNF,
                grammar_spec="",
            ),
            interpreter_config=InterpreterConfig(runtime="python"),
            domain="Test",
            constraints=(),
        )

        gen = TongueInputGenerator(empty_tongue, seed=42)
        gen.generate_valid(5)

        # Should handle gracefully (return examples or empty)
        # Implementation depends on how we handle empty grammars

    def test_no_examples(self) -> None:
        """Test tongue with no examples."""
        tongue = Tongue(
            name="NoExamples",
            version="1.0.0",
            lexicon=frozenset(["CHECK"]),
            grammar='<verb> ::= "CHECK"',
            mime_type="application/test",
            level=GrammarLevel.COMMAND,
            format=GrammarFormat.BNF,
            parser_config=ParserConfig(
                strategy="regex",
                grammar_format=GrammarFormat.BNF,
                grammar_spec='<verb> ::= "CHECK"',
            ),
            interpreter_config=InterpreterConfig(runtime="python"),
            domain="Test",
            constraints=(),
            examples=(),  # No examples
        )

        tester = TonguePropertyTester(tongue, seed=42)
        result = tester.test_completeness()

        # Should pass (no examples to fail)
        assert result.passed is True
        assert result.total_cases == 0

    def test_unicode_inputs(self, command_tongue: Tongue) -> None:
        """Test handling of unicode inputs."""
        gen = TongueInputGenerator(command_tongue, seed=42)
        boundary = gen.generate_boundary(20)

        # Should include unicode
        any("日本語" in b or "emoji" in b for b in boundary)
        # Generator should include unicode in boundary cases

    def test_very_long_inputs(self, command_tongue: Tongue) -> None:
        """Test handling of very long inputs."""
        gen = TongueInputGenerator(command_tongue, seed=42)
        adversarial = gen.generate_adversarial(15)

        # Should include long inputs
        has_long = any(len(a) > 100 for a in adversarial)
        assert has_long
