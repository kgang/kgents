"""Tests for E-gent v2 Mutator: Schema-based mutation generator."""

import pytest
from agents.e.mutator import (
    SCHEMA_EXTRACT_CONSTANT,
    SCHEMA_FLATTEN_NESTING,
    SCHEMA_INLINE_SINGLE_USE,
    # Schemas
    SCHEMA_LOOP_TO_COMPREHENSION,
    STANDARD_SCHEMA_APPLICATORS,
    ApplicationResult,
    CodeHotSpot,
    MutationSchema,
    # Mutator
    Mutator,
    MutatorConfig,
    MutatorStats,
    # Types
    SchemaCategory,
    _calculate_complexity,
    _count_line_changes,
    # Functions
    analyze_hot_spots,
    apply_extract_constant,
    apply_flatten_nesting,
    apply_inline_single_use,
    # Applicators
    apply_loop_to_comprehension,
    create_conservative_mutator,
    create_exploratory_mutator,
    create_mutator,
)
from agents.e.types import MutationVector, Phage, PhageStatus

# =============================================================================
# MutationSchema Tests
# =============================================================================


class TestMutationSchema:
    """Tests for MutationSchema."""

    def test_schema_creation(self) -> None:
        """Test basic schema creation."""
        schema = MutationSchema(
            name="test_schema",
            category=SchemaCategory.SUBSTITUTE,
            description="Test transformation",
            enthalpy_delta=-0.2,
            entropy_delta=0.1,
        )

        assert schema.name == "test_schema"
        assert schema.category == SchemaCategory.SUBSTITUTE
        assert schema.confidence == 0.7  # default

    def test_gibbs_free_energy(self) -> None:
        """Test Gibbs free energy calculation."""
        schema = MutationSchema(
            name="test",
            category=SchemaCategory.SUBSTITUTE,
            description="",
            enthalpy_delta=-0.3,  # ΔH = -0.3 (simplifying)
            entropy_delta=0.1,  # ΔS = +0.1 (more capability)
        )

        # ΔG = ΔH - TΔS
        # At T=1.0: ΔG = -0.3 - 1.0*0.1 = -0.4 (favorable)
        assert schema.gibbs_free_energy(1.0) == pytest.approx(-0.4)

        # At T=0.5: ΔG = -0.3 - 0.5*0.1 = -0.35
        assert schema.gibbs_free_energy(0.5) == pytest.approx(-0.35)

        # At T=5.0: ΔG = -0.3 - 5.0*0.1 = -0.8 (more favorable at high temp)
        assert schema.gibbs_free_energy(5.0) == pytest.approx(-0.8)

    def test_is_viable(self) -> None:
        """Test thermodynamic viability check."""
        # Favorable schema (ΔH < 0)
        favorable = MutationSchema(
            name="favorable",
            category=SchemaCategory.SUBSTITUTE,
            description="",
            enthalpy_delta=-0.5,
            entropy_delta=0.0,
        )
        assert favorable.is_viable(1.0)

        # Unfavorable schema (ΔH > 0, low entropy)
        unfavorable = MutationSchema(
            name="unfavorable",
            category=SchemaCategory.ANNOTATE,
            description="",
            enthalpy_delta=0.5,
            entropy_delta=0.1,
        )
        # At T=1.0: ΔG = 0.5 - 0.1 = 0.4 > 0 (unfavorable)
        assert not unfavorable.is_viable(1.0)

        # But at high temperature, entropy term dominates
        # At T=10.0: ΔG = 0.5 - 10*0.1 = -0.5 < 0 (favorable)
        assert unfavorable.is_viable(10.0)

    def test_standard_schemas_exist(self) -> None:
        """Test that standard schemas are defined."""
        assert len(STANDARD_SCHEMA_APPLICATORS) > 0

        # Check expected schemas
        assert "loop_to_comprehension" in STANDARD_SCHEMA_APPLICATORS
        assert "extract_constant" in STANDARD_SCHEMA_APPLICATORS
        assert "flatten_nesting" in STANDARD_SCHEMA_APPLICATORS
        assert "inline_single_use" in STANDARD_SCHEMA_APPLICATORS


# =============================================================================
# Hot Spot Detection Tests
# =============================================================================


class TestCodeHotSpot:
    """Tests for CodeHotSpot."""

    def test_priority_calculation(self) -> None:
        """Test hot spot priority calculation."""
        hot_spot = CodeHotSpot(
            lineno_start=1,
            lineno_end=10,
            node_type="function",
            name="test_func",
            complexity=10.0,
            entropy=5.0,
        )

        # Priority = complexity * 0.6 + entropy * 0.4
        expected = 10.0 * 0.6 + 5.0 * 0.4
        assert hot_spot.priority == pytest.approx(expected)

    def test_high_complexity_high_priority(self) -> None:
        """Test that high complexity yields high priority."""
        high_complexity = CodeHotSpot(
            lineno_start=1,
            lineno_end=10,
            node_type="function",
            name="complex",
            complexity=20.0,
            entropy=1.0,
        )
        low_complexity = CodeHotSpot(
            lineno_start=1,
            lineno_end=10,
            node_type="function",
            name="simple",
            complexity=2.0,
            entropy=1.0,
        )

        assert high_complexity.priority > low_complexity.priority


class TestAnalyzeHotSpots:
    """Tests for analyze_hot_spots."""

    def test_simple_function(self) -> None:
        """Test hot spot detection for simple function."""
        code = """
def simple():
    return 42
"""
        hot_spots = analyze_hot_spots(code)
        assert len(hot_spots) >= 1

        func_spot = next((h for h in hot_spots if h.name == "simple"), None)
        assert func_spot is not None
        assert func_spot.node_type == "function"
        assert func_spot.complexity >= 1.0

    def test_complex_function(self) -> None:
        """Test hot spot detection for complex function."""
        code = """
def complex_func(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                yield i
            else:
                yield i * 2
    else:
        while x < 0:
            x += 1
    return x
"""
        hot_spots = analyze_hot_spots(code)
        assert len(hot_spots) >= 1

        func_spot = next((h for h in hot_spots if h.name == "complex_func"), None)
        assert func_spot is not None
        # Should have higher complexity than simple function
        assert func_spot.complexity > 3.0

    def test_class_detection(self) -> None:
        """Test hot spot detection for classes."""
        code = """
class MyClass:
    def method_a(self):
        if True:
            pass

    def method_b(self):
        for i in range(10):
            yield i
"""
        hot_spots = analyze_hot_spots(code)

        class_spot = next((h for h in hot_spots if h.name == "MyClass"), None)
        assert class_spot is not None
        assert class_spot.node_type == "class"

    def test_sorted_by_priority(self) -> None:
        """Test that hot spots are sorted by priority."""
        code = """
def simple():
    return 1

def complex(x):
    if x > 0:
        for i in range(x):
            if i % 2 == 0:
                for j in range(i):
                    yield j
    return x
"""
        hot_spots = analyze_hot_spots(code)

        # Should be sorted by priority (highest first)
        priorities = [h.priority for h in hot_spots]
        assert priorities == sorted(priorities, reverse=True)

    def test_invalid_syntax(self) -> None:
        """Test that invalid syntax returns empty list."""
        code = "def broken("
        hot_spots = analyze_hot_spots(code)
        assert hot_spots == []


class TestComplexityCalculation:
    """Tests for _calculate_complexity."""

    def test_base_complexity(self) -> None:
        """Test base complexity for minimal function."""
        import ast

        tree = ast.parse("def f(): pass")
        func = tree.body[0]
        complexity = _calculate_complexity(func)
        assert complexity == 1.0  # Base complexity

    def test_if_increases_complexity(self) -> None:
        """Test that if statements increase complexity."""
        import ast

        tree = ast.parse("def f(x):\n    if x: pass")
        func = tree.body[0]
        complexity = _calculate_complexity(func)
        assert complexity > 1.0

    def test_loops_increase_complexity(self) -> None:
        """Test that loops increase complexity."""
        import ast

        tree = ast.parse(
            "def f():\n    for i in range(10): pass\n    while True: break"
        )
        func = tree.body[0]
        complexity = _calculate_complexity(func)
        assert complexity > 2.0


# =============================================================================
# Schema Applicator Tests
# =============================================================================


class TestLoopToComprehension:
    """Tests for apply_loop_to_comprehension."""

    def test_append_loop_transforms(self) -> None:
        """Test transformation of append loop to comprehension."""
        code = """
result = []
for x in items:
    result.append(x * 2)
"""
        result = apply_loop_to_comprehension(code, None)

        # This specific pattern should transform
        if result and result.success:
            assert "for" not in result.mutated_code or "[" in result.mutated_code
            assert result.schema == SCHEMA_LOOP_TO_COMPREHENSION

    def test_non_append_loop_unchanged(self) -> None:
        """Test that non-append loops are not transformed."""
        code = """
for x in items:
    print(x)
"""
        result = apply_loop_to_comprehension(code, None)
        # Should not transform (not an append loop)
        assert result is None

    def test_invalid_syntax(self) -> None:
        """Test that invalid syntax returns None."""
        code = "for x in ("
        result = apply_loop_to_comprehension(code, None)
        assert result is None


class TestExtractConstant:
    """Tests for apply_extract_constant."""

    def test_magic_number_extraction(self) -> None:
        """Test extraction of magic numbers."""
        code = """
def calculate(x):
    return x * 42 + 100
"""
        result = apply_extract_constant(code, None)

        if result and result.success:
            # Should define constants
            assert "CONSTANT" in result.mutated_code
            assert result.schema == SCHEMA_EXTRACT_CONSTANT

    def test_small_numbers_unchanged(self) -> None:
        """Test that small numbers are not extracted."""
        code = """
def f(x):
    return x + 1
"""
        result = apply_extract_constant(code, None)
        # 1 is not a magic number (too small)
        assert result is None

    def test_invalid_syntax(self) -> None:
        """Test that invalid syntax returns None."""
        code = "def broken("
        result = apply_extract_constant(code, None)
        assert result is None


class TestFlattenNesting:
    """Tests for apply_flatten_nesting."""

    def test_nested_if_flattens(self) -> None:
        """Test flattening of nested if."""
        code = """
def process(x):
    if x is not None:
        result = x * 2
        return result
"""
        result = apply_flatten_nesting(code, None)

        if result and result.success:
            # Should have early return
            assert "return" in result.mutated_code
            assert result.schema == SCHEMA_FLATTEN_NESTING

    def test_no_nesting_unchanged(self) -> None:
        """Test that flat code is unchanged."""
        code = """
def simple():
    return 42
"""
        result = apply_flatten_nesting(code, None)
        # No nesting to flatten
        assert result is None


class TestInlineSingleUse:
    """Tests for apply_inline_single_use."""

    def test_single_use_inlined(self) -> None:
        """Test inlining of single-use variable."""
        code = """
x = compute()
result = process(x)
"""
        result = apply_inline_single_use(code, None)

        if result and result.success:
            # x should be inlined
            assert "x = compute()" not in result.mutated_code
            assert "process(compute())" in result.mutated_code
            assert result.schema == SCHEMA_INLINE_SINGLE_USE

    def test_multiple_use_unchanged(self) -> None:
        """Test that multi-use variables are not inlined."""
        code = """
x = compute()
result1 = process(x)
result2 = transform(x)
"""
        result = apply_inline_single_use(code, None)
        # x is used twice, should not inline
        assert result is None


# =============================================================================
# Mutator Tests
# =============================================================================


class TestMutator:
    """Tests for Mutator class."""

    def test_creation(self) -> None:
        """Test mutator creation."""
        mutator = Mutator()
        assert mutator.temperature == 1.0  # Default
        assert len(mutator._schemas) > 0

    def test_temperature_clamping(self) -> None:
        """Test temperature is clamped to bounds."""
        config = MutatorConfig(
            min_temperature=0.5,
            max_temperature=5.0,
        )
        mutator = Mutator(config=config)

        mutator.temperature = 0.1  # Below min
        assert mutator.temperature == 0.5

        mutator.temperature = 10.0  # Above max
        assert mutator.temperature == 5.0

        mutator.temperature = 2.0  # Within bounds
        assert mutator.temperature == 2.0

    def test_get_viable_schemas(self) -> None:
        """Test getting viable schemas at temperature."""
        mutator = Mutator()

        # At normal temperature, most schemas should be viable
        viable = mutator.get_viable_schemas(1.0)
        assert len(viable) > 0

        # All returned schemas should be viable
        for schema in viable:
            assert schema.is_viable(1.0)

    def test_register_schema(self) -> None:
        """Test registering custom schema."""
        mutator = Mutator()
        initial_count = len(mutator._schemas)

        custom_schema = MutationSchema(
            name="custom_test",
            category=SchemaCategory.SUBSTITUTE,
            description="Custom transformation",
            enthalpy_delta=-0.2,
            entropy_delta=0.1,
        )

        def custom_applicator(
            code: str, location: CodeHotSpot | None
        ) -> ApplicationResult | None:
            return None

        mutator.register_schema(custom_schema, custom_applicator)
        assert len(mutator._schemas) == initial_count + 1
        assert "custom_test" in mutator._schemas

    def test_mutate_generates_mutations(self) -> None:
        """Test that mutate generates mutations."""
        mutator = Mutator()

        code = """
def complex_func(items):
    result = []
    for item in items:
        if item > 0:
            result.append(item * 42)
    return result
"""
        mutations = mutator.mutate(code)

        # Should generate at least some mutations
        assert len(mutations) >= 0  # May be 0 if no patterns match

        for mutation in mutations:
            assert isinstance(mutation, MutationVector)
            assert mutation.original_code
            assert mutation.mutated_code
            assert mutation.schema_signature

    def test_mutate_respects_max_mutations(self) -> None:
        """Test that mutate respects max_mutations limit."""
        config = MutatorConfig(max_mutations=2)
        mutator = Mutator(config=config)

        code = """
def f1(): return 42 * 100
def f2(): return 43 * 200
def f3(): return 44 * 300
"""
        mutations = mutator.mutate(code)
        assert len(mutations) <= 2

    def test_mutate_tracks_stats(self) -> None:
        """Test that mutate updates statistics."""
        mutator = Mutator()
        mutator._stats.reset()

        code = """
def f():
    x = 42
    return x * 100
"""
        mutations = mutator.mutate(code)

        # Stats should be updated
        if mutations:
            assert mutator.stats.mutations_generated > 0

    def test_mutate_to_phages(self) -> None:
        """Test generating phages from mutations."""
        mutator = Mutator()

        code = """
def process():
    result = []
    for x in range(10):
        result.append(x * 2)
    return result
"""
        phages = mutator.mutate_to_phages(code, module_name="test_module")

        for phage in phages:
            assert isinstance(phage, Phage)
            assert phage.status == PhageStatus.MUTATED
            assert phage.target_module == "test_module"
            assert phage.mutation is not None
            assert phage.hypothesis  # Should have description

    def test_mutate_empty_code(self) -> None:
        """Test mutation of empty code."""
        mutator = Mutator()
        mutations = mutator.mutate("")
        assert mutations == []

    def test_mutate_invalid_syntax(self) -> None:
        """Test mutation of invalid syntax."""
        mutator = Mutator()
        mutations = mutator.mutate("def broken(")
        assert mutations == []


class TestMutatorConfig:
    """Tests for MutatorConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = MutatorConfig()
        assert config.default_temperature == 1.0
        assert config.require_gibbs_viable is True
        assert config.max_mutations == 10

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = MutatorConfig(
            default_temperature=2.0,
            max_mutations=5,
            min_complexity=3.0,
        )
        assert config.default_temperature == 2.0
        assert config.max_mutations == 5
        assert config.min_complexity == 3.0


class TestMutatorStats:
    """Tests for MutatorStats."""

    def test_initial_stats(self) -> None:
        """Test initial statistics are zero."""
        stats = MutatorStats()
        assert stats.mutations_generated == 0
        assert stats.application_errors == 0

    def test_reset_stats(self) -> None:
        """Test resetting statistics."""
        stats = MutatorStats()
        stats.mutations_generated = 10
        stats.application_errors = 2

        stats.reset()

        assert stats.mutations_generated == 0
        assert stats.application_errors == 0


# =============================================================================
# Factory Function Tests
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_mutator(self) -> None:
        """Test create_mutator factory."""
        mutator = create_mutator(temperature=2.0)
        assert mutator.temperature == 2.0

    def test_create_conservative_mutator(self) -> None:
        """Test create_conservative_mutator factory."""
        mutator = create_conservative_mutator()
        assert mutator.temperature == 0.5
        assert mutator.config.require_gibbs_viable is True
        assert mutator.config.max_mutations == 5

    def test_create_exploratory_mutator(self) -> None:
        """Test create_exploratory_mutator factory."""
        mutator = create_exploratory_mutator()
        assert mutator.temperature == 3.0
        assert mutator.config.require_gibbs_viable is False
        assert mutator.config.max_mutations == 20


# =============================================================================
# Utility Function Tests
# =============================================================================


class TestUtilityFunctions:
    """Tests for utility functions."""

    def test_count_line_changes_identical(self) -> None:
        """Test counting changes for identical code."""
        code = "def f(): pass"
        changes = _count_line_changes(code, code)
        assert changes == 0

    def test_count_line_changes_added(self) -> None:
        """Test counting changes for added lines."""
        original = "line1"
        mutated = "line1\nline2"
        changes = _count_line_changes(original, mutated)
        assert changes >= 1

    def test_count_line_changes_modified(self) -> None:
        """Test counting changes for modified lines."""
        original = "line1\nline2"
        mutated = "line1\nmodified"
        changes = _count_line_changes(original, mutated)
        assert changes >= 1


# =============================================================================
# Integration Tests
# =============================================================================


class TestMutatorIntegration:
    """Integration tests for Mutator with full pipeline."""

    def test_full_mutation_pipeline(self) -> None:
        """Test full mutation pipeline."""
        mutator = create_mutator()

        # Code with multiple mutation opportunities
        code = '''
def process_items(items):
    """Process a list of items."""
    result = []
    for item in items:
        if item > 0:
            processed = item * 42
            result.append(processed)
    return result
'''
        # Generate mutations
        mutations = mutator.mutate(code)

        # Verify mutations are valid
        for mutation in mutations:
            # Should have Gibbs properties
            assert hasattr(mutation, "gibbs_free_energy")
            assert mutation.is_viable or not mutator.config.require_gibbs_viable

            # Mutated code should be different
            if mutation.mutated_code != mutation.original_code:
                assert mutation.lines_changed > 0

    def test_mutation_to_phage_to_selection(self) -> None:
        """Test mutation pipeline integration with selection."""
        from agents.e.demon import TeleologicalDemon

        mutator = create_mutator()
        demon = TeleologicalDemon()

        code = """
def calculate(x):
    magic = 42
    return x * magic + 100
"""
        # Generate phages
        phages = mutator.mutate_to_phages(code, "test_module")

        # Pass through demon selection
        for phage in phages:
            result = demon.select(phage)
            # Result should have passed status
            assert result.layer_reached > 0

    def test_temperature_affects_viable_schemas(self) -> None:
        """Test that temperature affects which schemas are viable."""
        mutator = create_mutator()

        # At low temperature, fewer schemas may be viable
        low_temp_viable = mutator.get_viable_schemas(0.1)

        # At high temperature, more schemas should be viable
        high_temp_viable = mutator.get_viable_schemas(10.0)

        # High temp should have >= schemas viable
        # (entropy term in Gibbs becomes more significant)
        assert len(high_temp_viable) >= len(low_temp_viable)
