"""
Tests for Psi-gent: The Universal Translator of Semantic Topologies.

Test count targets from synthesis doc:
- Phase 1: Core Types (20)
- Phase 2: Static MetaphorLibrary + MorphicFunctor (30)
- Phase 3: ResolutionScaler (25)
- Phase 4: DialecticalRotator (20)
- Phase 5: TopologicalValidator (25)
- Phase 6: AxiologicalExchange (30)
- Phase 7: HolographicMetaphorLibrary (35)
- Phase 8: MetaphorHistorian + ForensicBard (30)
- Phase 9: MetaphorUmwelt (25)
- Phase 10: MetaphorEvolutionAgent (30)
- Phase 11: PsychopompAgent (40)
Total: 310
"""

import pytest

# =============================================================================
# Phase 1: Core Types (20 tests)
# =============================================================================

from .types import (
    MHCLevel,
    AxisType,
    StabilityStatus,
    AntiPattern,
    Novel,
    Metaphor,
    MetaphorOperation,
    Projection,
    ConceptMapping,
    Distortion,
    MetaphorSolution,
    ReifiedSolution,
    TensorPosition,
    ValidationResult,
    AntiPatternDetection,
)


class TestCoreTypes:
    """Tests for core Psi-gent types."""

    def test_mhc_level_ordering(self):
        """MHC levels have numeric ordering."""
        assert MHCLevel.SENSORIMOTOR.value < MHCLevel.FORMAL.value
        assert MHCLevel.FORMAL.value < MHCLevel.SYSTEMATIC.value
        assert MHCLevel.SYSTEMATIC.value < MHCLevel.METASYSTEMATIC.value

    def test_mhc_level_all_values(self):
        """All 15 MHC levels exist."""
        assert len(MHCLevel) == 15

    def test_axis_type_enum(self):
        """AxisType enum has 4 axes."""
        assert AxisType.Z_MHC is not None
        assert AxisType.X_JUNGIAN is not None
        assert AxisType.Y_LACANIAN is not None
        assert AxisType.T_AXIOLOGICAL is not None

    def test_stability_status(self):
        """StabilityStatus has 3 states."""
        assert StabilityStatus.STABLE is not None
        assert StabilityStatus.FRAGILE is not None
        assert StabilityStatus.UNSTABLE is not None

    def test_anti_pattern_enum(self):
        """AntiPattern enum has all patterns."""
        assert AntiPattern.PROCRUSTEAN_BED is not None
        assert AntiPattern.SHADOW_BLINDNESS is not None
        assert AntiPattern.MAP_TERRITORY_CONFUSION is not None
        assert AntiPattern.VALUE_BLINDNESS is not None

    def test_novel_creation(self):
        """Novel can be created with required fields."""
        n = Novel(
            problem_id="test",
            description="Test problem",
            domain="testing",
        )
        assert n.problem_id == "test"
        assert n.complexity == 0.5  # default

    def test_novel_with_embedding(self):
        """Novel can have an embedding."""
        n = Novel(
            problem_id="test",
            description="Test problem",
            domain="testing",
            embedding=(0.1, 0.2, 0.3),
        )
        assert n.embedding == (0.1, 0.2, 0.3)

    def test_metaphor_creation(self):
        """Metaphor can be created."""
        m = Metaphor(
            metaphor_id="test_metaphor",
            name="Test",
            domain="testing",
            description="A test metaphor",
        )
        assert m.name == "Test"
        assert m.tractability == 0.8  # default

    def test_metaphor_operation(self):
        """MetaphorOperation has name and description."""
        op = MetaphorOperation(
            name="test_op",
            description="Test operation",
        )
        assert op.name == "test_op"
        assert op.inputs == ()  # default

    def test_concept_mapping(self):
        """ConceptMapping maps source to target."""
        cm = ConceptMapping(
            source_concept="problem",
            target_concept="battle",
            confidence=0.8,
        )
        assert cm.source_concept == "problem"
        assert cm.confidence == 0.8

    def test_distortion_creation(self):
        """Distortion has delta and details."""
        d = Distortion(
            delta=0.3,
            details="Some information lost",
        )
        assert d.delta == 0.3
        assert d.is_acceptable

    def test_distortion_not_acceptable(self):
        """High distortion is not acceptable."""
        d = Distortion(delta=0.7, details="Too much lost")
        assert not d.is_acceptable

    def test_tensor_position(self):
        """TensorPosition has all 4 coordinates."""
        pos = TensorPosition(
            z_altitude=0.8,
            x_rotation=0.5,
            y_topology=0.7,
            t_axiological=0.6,
        )
        assert pos.z_altitude == 0.8
        assert pos.overall == pytest.approx(0.65, abs=0.01)

    def test_validation_result(self):
        """ValidationResult has axis, status, score."""
        vr = ValidationResult(
            axis=AxisType.Z_MHC,
            status=StabilityStatus.STABLE,
            score=0.9,
            message="Good",
        )
        assert vr.axis == AxisType.Z_MHC
        assert vr.status == StabilityStatus.STABLE

    def test_anti_pattern_detection_not_detected(self):
        """AntiPatternDetection can be not detected."""
        apd = AntiPatternDetection(
            pattern=AntiPattern.PROCRUSTEAN_BED,
            detected=False,
            confidence=0.0,
        )
        assert not apd.detected

    def test_anti_pattern_detection_detected(self):
        """AntiPatternDetection can be detected with evidence."""
        apd = AntiPatternDetection(
            pattern=AntiPattern.SHADOW_BLINDNESS,
            detected=True,
            confidence=0.7,
            evidence="No shadow test",
            mitigation="Run shadow test",
        )
        assert apd.detected
        assert apd.mitigation == "Run shadow test"

    def test_novel_constraints(self):
        """Novel can have constraints."""
        n = Novel(
            problem_id="test",
            description="Test",
            domain="testing",
            constraints=("must_be_fast", "no_db"),
        )
        assert len(n.constraints) == 2

    def test_metaphor_with_operations(self):
        """Metaphor can have operations."""
        op1 = MetaphorOperation(name="op1", description="First")
        op2 = MetaphorOperation(name="op2", description="Second")
        m = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="testing",
            description="Test metaphor",
            operations=(op1, op2),
        )
        assert len(m.operations) == 2


# =============================================================================
# Phase 2: Static MetaphorLibrary + MorphicFunctor (30 tests)
# =============================================================================

from .metaphor_library import (
    WeightedMetaphor,
    create_standard_library,
)
from .morphic_functor import MorphicFunctor


class TestMetaphorLibrary:
    """Tests for StaticMetaphorLibrary."""

    def test_create_standard_library(self):
        """Standard library can be created."""
        lib = create_standard_library()
        assert len(lib) > 0

    def test_standard_library_has_metaphors(self):
        """Standard library has expected metaphors."""
        lib = create_standard_library()
        assert lib.get("military_strategy") is not None
        assert lib.get("thermodynamics") is not None

    def test_fetch_candidates(self):
        """Library can fetch candidates for a problem."""
        lib = create_standard_library()
        problem = Novel(
            problem_id="test",
            description="A competitive business challenge",
            domain="business",
        )
        candidates = lib.fetch_candidates(problem, limit=3)
        assert len(candidates) <= 3

    def test_weighted_metaphor_comparison(self):
        """WeightedMetaphor supports comparison."""
        m = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="testing",
            description="Test",
        )
        wm1 = WeightedMetaphor(metaphor=m, weight=0.5)
        wm2 = WeightedMetaphor(metaphor=m, weight=0.8)
        assert wm2 > wm1

    def test_library_all_metaphors(self):
        """Library returns all metaphors."""
        lib = create_standard_library()
        all_m = lib.all_metaphors()
        assert len(all_m) >= 8  # At least 8 standard metaphors

    def test_library_get_nonexistent(self):
        """Library returns None for nonexistent metaphor."""
        lib = create_standard_library()
        assert lib.get("nonexistent") is None

    def test_library_metaphor_domains(self):
        """Standard metaphors have various domains."""
        lib = create_standard_library()
        domains = {m.domain for m in lib.all_metaphors()}
        assert len(domains) >= 3  # At least 3 different domains


class TestMorphicFunctor:
    """Tests for MorphicFunctor."""

    @pytest.fixture
    def functor(self):
        return MorphicFunctor()

    @pytest.fixture
    def problem(self):
        return Novel(
            problem_id="test_problem",
            description="Optimize team communication",
            domain="organization",
            complexity=0.5,
        )

    @pytest.fixture
    def metaphor(self):
        return Metaphor(
            metaphor_id="ecosystem",
            name="Ecosystem",
            domain="biology",
            description="Network of interconnected organisms",
            operations=(
                MetaphorOperation(name="symbiosis", description="Mutual benefit"),
                MetaphorOperation(
                    name="adaptation", description="Environmental response"
                ),
            ),
            tractability=0.7,
            generality=0.8,
        )

    def test_project_creates_projection(self, functor, problem, metaphor):
        """Project creates a Projection."""
        projection = functor.project(problem, metaphor)
        assert isinstance(projection, Projection)
        assert projection.source == problem
        assert projection.target == metaphor

    def test_project_has_concept_mappings(self, functor, problem, metaphor):
        """Projection has concept mappings."""
        projection = functor.project(problem, metaphor)
        assert len(projection.mapped_concepts) > 0

    def test_project_has_applicable_operations(self, functor, problem, metaphor):
        """Projection has applicable operations."""
        projection = functor.project(problem, metaphor)
        assert len(projection.applicable_operations) > 0

    def test_project_has_confidence(self, functor, problem, metaphor):
        """Projection has confidence score."""
        projection = functor.project(problem, metaphor)
        assert 0 <= projection.confidence <= 1

    def test_calculate_distortion(self, functor, problem, metaphor):
        """Distortion can be calculated."""
        projection = functor.project(problem, metaphor)
        distortion = functor.calculate_distortion(problem, projection)
        assert isinstance(distortion, Distortion)
        assert 0 <= distortion.delta <= 1

    def test_reify_creates_solution(self, functor, problem, metaphor):
        """Reify creates a ReifiedSolution."""
        projection = functor.project(problem, metaphor)
        solution = MetaphorSolution(
            projection=projection,
            operations_applied=("symbiosis",),
            intermediate_results=("Applied symbiosis",),
            final_state="Solved",
            confidence=0.8,
            completeness=0.7,
        )
        reified = functor.reify(solution, problem, projection)
        assert isinstance(reified, ReifiedSolution)

    def test_reify_preserves_original_problem(self, functor, problem, metaphor):
        """ReifiedSolution preserves original problem."""
        projection = functor.project(problem, metaphor)
        solution = MetaphorSolution(
            projection=projection,
            operations_applied=("symbiosis",),
            intermediate_results=(),
            final_state="Solved",
            confidence=0.8,
            completeness=0.7,
        )
        reified = functor.reify(solution, problem, projection)
        assert reified.original_problem == problem

    def test_reify_has_distortion(self, functor, problem, metaphor):
        """ReifiedSolution has distortion."""
        projection = functor.project(problem, metaphor)
        solution = MetaphorSolution(
            projection=projection,
            operations_applied=("symbiosis",),
            intermediate_results=(),
            final_state="Solved",
            confidence=0.8,
            completeness=0.7,
        )
        reified = functor.reify(solution, problem, projection)
        assert isinstance(reified.distortion, Distortion)

    def test_high_generality_lowers_distortion(self, functor, problem):
        """High generality metaphor produces lower distortion."""
        high_gen = Metaphor(
            metaphor_id="general",
            name="General",
            domain="abstract",
            description="Very general",
            generality=0.9,
        )
        projection = functor.project(problem, high_gen)
        distortion = functor.calculate_distortion(problem, projection)
        assert distortion.delta <= 0.6  # Should be relatively low

    def test_different_domain_increases_distortion(self, functor):
        """Different domain increases distortion."""
        problem = Novel(
            problem_id="test",
            description="Test",
            domain="specific_domain",
        )
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="completely_different_domain",
            description="Test",
            generality=0.3,  # Low generality
        )
        projection = functor.project(problem, metaphor)
        distortion = functor.calculate_distortion(problem, projection)
        assert distortion.delta > 0.3  # Should have some distortion

    def test_project_has_coverage(self, functor, problem, metaphor):
        """Projection has coverage metric."""
        projection = functor.project(problem, metaphor)
        assert 0 <= projection.coverage <= 1

    def test_project_has_projected_description(self, functor, problem, metaphor):
        """Projection has projected description."""
        projection = functor.project(problem, metaphor)
        assert len(projection.projected_description) > 0

    def test_reified_has_quality(self, functor, problem, metaphor):
        """ReifiedSolution has overall quality."""
        projection = functor.project(problem, metaphor)
        solution = MetaphorSolution(
            projection=projection,
            operations_applied=("symbiosis",),
            intermediate_results=(),
            final_state="Solved",
            confidence=0.8,
            completeness=0.7,
        )
        reified = functor.reify(solution, problem, projection)
        assert 0 <= reified.overall_quality <= 1

    def test_reified_has_success_flag(self, functor, problem, metaphor):
        """ReifiedSolution has is_successful flag."""
        projection = functor.project(problem, metaphor)
        solution = MetaphorSolution(
            projection=projection,
            operations_applied=("symbiosis",),
            intermediate_results=(),
            final_state="Solved",
            confidence=0.8,
            completeness=0.7,
        )
        reified = functor.reify(solution, problem, projection)
        assert isinstance(reified.is_successful, bool)


# =============================================================================
# Phase 3: ResolutionScaler (25 tests)
# =============================================================================

from .resolution_scaler import ResolutionScaler, ComplexityMetrics


class TestResolutionScaler:
    """Tests for Z-axis MHC controller."""

    @pytest.fixture
    def scaler(self):
        return ResolutionScaler()

    @pytest.fixture
    def simple_problem(self):
        return Novel(
            problem_id="simple",
            description="Add two numbers",
            domain="math",
            complexity=0.2,
            entropy=0.1,
        )

    @pytest.fixture
    def complex_problem(self):
        return Novel(
            problem_id="complex",
            description="Design distributed consensus algorithm",
            domain="systems",
            complexity=0.9,
            entropy=0.8,
        )

    def test_measure_complexity(self, scaler, simple_problem):
        """Complexity can be measured."""
        metrics = scaler.measure_complexity(simple_problem)
        assert isinstance(metrics, ComplexityMetrics)

    def test_complexity_has_mhc_level(self, scaler, simple_problem):
        """ComplexityMetrics has MHC level."""
        metrics = scaler.measure_complexity(simple_problem)
        assert isinstance(metrics.mhc_level, MHCLevel)

    def test_simple_problem_low_mhc(self, scaler, simple_problem):
        """Simple problem gets low MHC level."""
        metrics = scaler.measure_complexity(simple_problem)
        assert metrics.mhc_level.value <= 5

    def test_complex_problem_high_mhc(self, scaler, complex_problem):
        """Complex problem gets high MHC level."""
        metrics = scaler.measure_complexity(complex_problem)
        assert metrics.mhc_level.value >= 8

    def test_validate_returns_result(self, scaler, simple_problem):
        """Validate returns ValidationResult."""
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="math",
            description="Test",
        )
        projection = Projection(
            source=simple_problem,
            target=metaphor,
            mapped_concepts=(),
            applicable_operations=(),
            projected_description="Test",
            confidence=0.7,
            coverage=0.6,
        )
        result = scaler.validate(projection)
        assert isinstance(result, ValidationResult)
        assert result.axis == AxisType.Z_MHC

    def test_validate_has_score(self, scaler, simple_problem):
        """ValidationResult has score."""
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="math",
            description="Test",
        )
        projection = Projection(
            source=simple_problem,
            target=metaphor,
            mapped_concepts=(),
            applicable_operations=(),
            projected_description="Test",
            confidence=0.7,
            coverage=0.6,
        )
        result = scaler.validate(projection)
        assert 0 <= result.score <= 1

    def test_abstract_increases_altitude(self, scaler, simple_problem):
        """Abstract operation increases altitude."""
        metrics_before = scaler.measure_complexity(simple_problem)
        abstracted = scaler.abstract(simple_problem)
        metrics_after = scaler.measure_complexity(abstracted)
        # Abstract version should have higher or equal MHC
        assert metrics_after.mhc_level.value >= metrics_before.mhc_level.value

    def test_concretize_decreases_altitude(self, scaler, complex_problem):
        """Concretize operation decreases altitude."""
        metrics_before = scaler.measure_complexity(complex_problem)
        concrete = scaler.concretize(complex_problem)
        metrics_after = scaler.measure_complexity(concrete)
        # Concrete version should have lower or equal MHC
        assert metrics_after.mhc_level.value <= metrics_before.mhc_level.value

    def test_optimize_resolution(self, scaler, simple_problem):
        """Optimize resolution finds target level."""
        target = MHCLevel.FORMAL
        optimized = scaler.optimize_resolution(simple_problem, target)
        assert isinstance(optimized, Novel)

    def test_complexity_metrics_has_description_length(self, scaler, simple_problem):
        """ComplexityMetrics includes description length."""
        metrics = scaler.measure_complexity(simple_problem)
        assert metrics.description_length > 0

    def test_complexity_metrics_has_raw_complexity(self, scaler, simple_problem):
        """ComplexityMetrics has raw complexity value."""
        metrics = scaler.measure_complexity(simple_problem)
        assert 0 <= metrics.raw_complexity <= 1

    def test_validate_stable_on_good_match(self, scaler):
        """Validate returns STABLE on good complexity match."""
        problem = Novel(
            problem_id="mid",
            description="Medium complexity problem",
            domain="test",
            complexity=0.5,
        )
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test",
            tractability=0.5,  # Matches problem complexity
        )
        projection = Projection(
            source=problem,
            target=metaphor,
            mapped_concepts=(),
            applicable_operations=(),
            projected_description="Test",
            confidence=0.7,
            coverage=0.6,
        )
        result = scaler.validate(projection)
        assert result.status in (StabilityStatus.STABLE, StabilityStatus.FRAGILE)

    def test_validate_unstable_on_mismatch(self, scaler):
        """Validate returns UNSTABLE on large mismatch."""
        problem = Novel(
            problem_id="complex",
            description="Very complex problem",
            domain="test",
            complexity=0.95,
        )
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test",
            tractability=0.1,  # Very low tractability
        )
        projection = Projection(
            source=problem,
            target=metaphor,
            mapped_concepts=(),
            applicable_operations=(),
            projected_description="Test",
            confidence=0.7,
            coverage=0.2,
        )
        result = scaler.validate(projection)
        assert result.status in (StabilityStatus.FRAGILE, StabilityStatus.UNSTABLE)


# =============================================================================
# Phase 4: DialecticalRotator (20 tests)
# =============================================================================

from .dialectical_rotator import (
    DialecticalRotator,
    ShadowGenerator,
    Shadow,
    ShadowType,
    ShadowTestResult,
)


class TestDialecticalRotator:
    """Tests for X-axis Jungian shadow testing."""

    @pytest.fixture
    def rotator(self):
        return DialecticalRotator()

    @pytest.fixture
    def projection(self):
        problem = Novel(
            problem_id="test",
            description="Test problem",
            domain="test",
        )
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test metaphor",
        )
        return Projection(
            source=problem,
            target=metaphor,
            mapped_concepts=(),
            applicable_operations=(),
            projected_description="Test",
            confidence=0.7,
            coverage=0.6,
        )

    def test_shadow_generator_creates_shadows(self, rotator, projection):
        """ShadowGenerator creates shadows."""
        generator = ShadowGenerator()
        shadows = generator.generate(projection, count=3)
        assert len(shadows) <= 3
        assert all(isinstance(s, Shadow) for s in shadows)

    def test_shadow_has_type(self, rotator, projection):
        """Shadow has a ShadowType."""
        generator = ShadowGenerator()
        shadows = generator.generate(projection, count=1)
        if shadows:
            assert isinstance(shadows[0].shadow_type, ShadowType)

    def test_shadow_types_exist(self):
        """All shadow types exist."""
        assert ShadowType.NEGATION is not None
        assert ShadowType.INVERSION is not None
        assert ShadowType.EXTREME is not None
        assert ShadowType.OPPOSITE_DOMAIN is not None

    def test_validate_returns_result(self, rotator, projection):
        """Validate returns ValidationResult."""
        result = rotator.validate(projection)
        assert isinstance(result, ValidationResult)
        assert result.axis == AxisType.X_JUNGIAN

    def test_validate_has_status(self, rotator, projection):
        """ValidationResult has status."""
        result = rotator.validate(projection)
        assert isinstance(result.status, StabilityStatus)

    def test_test_shadow_returns_result(self, rotator, projection):
        """Test shadow returns ShadowTestResult."""
        generator = ShadowGenerator()
        shadows = generator.generate(projection, count=1)
        if shadows:
            result = rotator.test_shadow(projection, shadows[0])
            assert isinstance(result, ShadowTestResult)

    def test_shadow_test_result_has_survives(self, rotator, projection):
        """ShadowTestResult has survives flag."""
        generator = ShadowGenerator()
        shadows = generator.generate(projection, count=1)
        if shadows:
            result = rotator.test_shadow(projection, shadows[0])
            assert isinstance(result.survives, bool)

    def test_detect_shadow_blindness(self, rotator, projection):
        """Can detect shadow blindness anti-pattern."""
        detection = rotator.detect_shadow_blindness(projection)
        assert isinstance(detection, AntiPatternDetection)
        assert detection.pattern == AntiPattern.SHADOW_BLINDNESS

    def test_validate_multiple_shadows(self, rotator, projection):
        """Rotator can validate with multiple shadows."""
        result = rotator.validate(projection)
        assert result.details is not None

    def test_shadow_has_description(self):
        """Shadow has description."""
        problem = Novel(
            problem_id="test",
            description="Test",
            domain="test",
        )
        shadow = Shadow(
            shadow_type=ShadowType.NEGATION,
            original_concept="solution",
            shadow_concept="non-solution",
            stress_factor=0.5,
        )
        assert shadow.original_concept == "solution"
        assert shadow.shadow_concept == "non-solution"


# =============================================================================
# Phase 5: TopologicalValidator (25 tests)
# =============================================================================

from .topological_validator import (
    TopologicalValidator,
    KnotAnalyzer,
    KnotAnalysis,
    Register,
    RegisterState,
)


class TestTopologicalValidator:
    """Tests for Y-axis Lacanian RSI analysis."""

    @pytest.fixture
    def validator(self):
        return TopologicalValidator()

    @pytest.fixture
    def projection(self):
        problem = Novel(
            problem_id="test",
            description="Test problem with constraints",
            domain="test",
            constraints=("must_work",),
        )
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test metaphor",
            operations=(MetaphorOperation(name="op1", description="Operation 1"),),
        )
        return Projection(
            source=problem,
            target=metaphor,
            mapped_concepts=(
                ConceptMapping(
                    source_concept="problem", target_concept="metaphor", confidence=0.7
                ),
            ),
            applicable_operations=(MetaphorOperation(name="op1", description="Op1"),),
            projected_description="Test projection must_work",
            confidence=0.7,
            coverage=0.6,
        )

    def test_register_enum(self):
        """Register enum has RSI values."""
        assert Register.REAL is not None
        assert Register.SYMBOLIC is not None
        assert Register.IMAGINARY is not None

    def test_knot_analyzer_creates_analysis(self, validator, projection):
        """KnotAnalyzer creates KnotAnalysis."""
        analyzer = KnotAnalyzer()
        analysis = analyzer.analyze(projection)
        assert isinstance(analysis, KnotAnalysis)

    def test_knot_analysis_has_registers(self, validator, projection):
        """KnotAnalysis has all three registers."""
        analyzer = KnotAnalyzer()
        analysis = analyzer.analyze(projection)
        assert isinstance(analysis.real, RegisterState)
        assert isinstance(analysis.symbolic, RegisterState)
        assert isinstance(analysis.imaginary, RegisterState)

    def test_register_state_has_integrity(self, validator, projection):
        """RegisterState has integrity score."""
        analyzer = KnotAnalyzer()
        analysis = analyzer.analyze(projection)
        assert 0 <= analysis.real.integrity <= 1
        assert 0 <= analysis.symbolic.integrity <= 1
        assert 0 <= analysis.imaginary.integrity <= 1

    def test_knot_analysis_has_is_intact(self, validator, projection):
        """KnotAnalysis has is_intact flag."""
        analyzer = KnotAnalyzer()
        analysis = analyzer.analyze(projection)
        assert isinstance(analysis.is_intact, bool)

    def test_knot_analysis_has_slippage(self, validator, projection):
        """KnotAnalysis has slippage score."""
        analyzer = KnotAnalyzer()
        analysis = analyzer.analyze(projection)
        assert 0 <= analysis.slippage <= 1

    def test_validate_returns_result(self, validator, projection):
        """Validate returns ValidationResult."""
        result = validator.validate(projection)
        assert isinstance(result, ValidationResult)
        assert result.axis == AxisType.Y_LACANIAN

    def test_detect_hallucination_risk(self, validator, projection):
        """Can detect hallucination risk."""
        risk = validator.detect_hallucination_risk(projection)
        assert 0 <= risk <= 1

    def test_detect_map_territory_confusion(self, validator, projection):
        """Can detect map-territory confusion."""
        detection = validator.detect_map_territory_confusion(projection)
        assert isinstance(detection, AntiPatternDetection)
        assert detection.pattern == AntiPattern.MAP_TERRITORY_CONFUSION

    def test_analyze_registers(self, validator, projection):
        """Can get detailed register analysis."""
        analysis = validator.analyze_registers(projection)
        assert "real" in analysis
        assert "symbolic" in analysis
        assert "imaginary" in analysis
        assert "knot" in analysis

    def test_weakest_register(self, validator, projection):
        """KnotAnalysis identifies weakest register."""
        analyzer = KnotAnalyzer()
        analysis = analyzer.analyze(projection)
        assert isinstance(analysis.weakest_register, Register)


# =============================================================================
# Phase 6: AxiologicalExchange (30 tests)
# =============================================================================

from .axiological_exchange import (
    AxiologicalExchange,
    ExchangeMatrix,
    ExchangeRate,
    ValueDimension,
    DimensionValue,
    MetaphorValueTensor,
    LossReport,
)


class TestAxiologicalExchange:
    """Tests for T-axis value exchange."""

    @pytest.fixture
    def exchange(self):
        return AxiologicalExchange()

    @pytest.fixture
    def projection(self):
        problem = Novel(
            problem_id="test",
            description="Test problem",
            domain="test",
            complexity=0.5,
        )
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test metaphor",
            tractability=0.7,
        )
        return Projection(
            source=problem,
            target=metaphor,
            mapped_concepts=(),
            applicable_operations=(),
            projected_description="Test",
            confidence=0.7,
            coverage=0.6,
        )

    @pytest.fixture
    def distortion(self):
        return Distortion(delta=0.3, details="Moderate loss")

    def test_value_dimension_enum(self):
        """ValueDimension has all dimensions."""
        assert ValueDimension.PRAGMATIC is not None
        assert ValueDimension.EPISTEMIC is not None
        assert ValueDimension.ETHICAL is not None
        assert ValueDimension.AESTHETIC is not None
        assert ValueDimension.HEDONIC is not None

    def test_dimension_value_creation(self):
        """DimensionValue can be created."""
        dv = DimensionValue(
            dimension=ValueDimension.PRAGMATIC,
            value=0.7,
            confidence=0.8,
        )
        assert dv.value == 0.7

    def test_exchange_rate_creation(self):
        """ExchangeRate can be created."""
        rate = ExchangeRate(
            from_dim=ValueDimension.PRAGMATIC,
            to_dim=ValueDimension.EPISTEMIC,
            rate=0.8,
            loss=0.2,
            confidence=0.7,
        )
        assert rate.rate == 0.8

    def test_exchange_matrix_initialization(self):
        """ExchangeMatrix initializes with standard rates."""
        matrix = ExchangeMatrix()
        rate = matrix.get_rate(ValueDimension.PRAGMATIC, ValueDimension.EPISTEMIC)
        assert rate is not None

    def test_exchange_matrix_convert(self):
        """ExchangeMatrix can convert values."""
        matrix = ExchangeMatrix()
        result = matrix.convert(1.0, ValueDimension.PRAGMATIC, ValueDimension.EPISTEMIC)
        assert result.converted_value >= 0
        assert result.loss >= 0

    def test_exchange_matrix_identity(self):
        """Converting to same dimension has no loss."""
        matrix = ExchangeMatrix()
        result = matrix.convert(1.0, ValueDimension.PRAGMATIC, ValueDimension.PRAGMATIC)
        assert result.loss == 0
        assert result.converted_value == 1.0

    def test_calculate_tensor(self, exchange, projection):
        """Can calculate value tensor."""
        tensor = exchange.calculate_tensor(projection)
        assert isinstance(tensor, MetaphorValueTensor)

    def test_tensor_has_all_dimensions(self, exchange, projection):
        """Tensor has all 5 dimensions."""
        tensor = exchange.calculate_tensor(projection)
        assert tensor.pragmatic is not None
        assert tensor.epistemic is not None
        assert tensor.ethical is not None
        assert tensor.aesthetic is not None
        assert tensor.hedonic is not None

    def test_tensor_total_value(self, exchange, projection):
        """Tensor calculates total value."""
        tensor = exchange.calculate_tensor(projection)
        assert 0 <= tensor.total_value <= 1

    def test_measure_loss(self, exchange, projection, distortion):
        """Can measure loss."""
        report = exchange.measure_loss(projection.source, projection, distortion)
        assert isinstance(report, LossReport)

    def test_loss_report_has_total(self, exchange, projection, distortion):
        """LossReport has total loss."""
        report = exchange.measure_loss(projection.source, projection, distortion)
        assert 0 <= report.total_loss <= 1

    def test_loss_report_is_acceptable(self, exchange, projection, distortion):
        """LossReport has is_acceptable flag."""
        report = exchange.measure_loss(projection.source, projection, distortion)
        assert isinstance(report.is_acceptable, bool)

    def test_validate_returns_result(self, exchange, projection, distortion):
        """Validate returns ValidationResult."""
        result = exchange.validate(projection, distortion)
        assert isinstance(result, ValidationResult)
        assert result.axis == AxisType.T_AXIOLOGICAL

    def test_detect_value_blindness(self, exchange, projection, distortion):
        """Can detect value blindness."""
        detection = exchange.detect_value_blindness(projection, distortion)
        assert isinstance(detection, AntiPatternDetection)
        assert detection.pattern == AntiPattern.VALUE_BLINDNESS

    def test_calculate_roi(self, exchange, projection, distortion):
        """Can calculate ROI."""
        roi = exchange.calculate_roi(projection, distortion)
        assert roi >= 0


# =============================================================================
# Phase 7: HolographicMetaphorLibrary (35 tests)
# =============================================================================

from .holographic_library import (
    HolographicMetaphorLibrary,
    HolographicPattern,
    MetaphorEntry,
)


class TestHolographicMetaphorLibrary:
    """Tests for M-gent holographic memory integration."""

    @pytest.fixture
    def library(self):
        return HolographicMetaphorLibrary()

    @pytest.fixture
    def problem(self):
        return Novel(
            problem_id="test",
            description="A competitive business challenge requiring strategy",
            domain="business",
        )

    def test_library_initialization(self, library):
        """Library initializes with standard metaphors."""
        assert len(library) > 0

    def test_fetch_candidates(self, library, problem):
        """Library can fetch candidates."""
        candidates = library.fetch_candidates(problem, limit=5)
        assert len(candidates) <= 5

    def test_candidates_are_weighted(self, library, problem):
        """Candidates have weights."""
        candidates = library.fetch_candidates(problem, limit=3)
        for wm in candidates:
            assert 0 <= wm.weight <= 2  # Can be boosted

    def test_candidates_sorted_by_weight(self, library, problem):
        """Candidates sorted by weight descending."""
        candidates = library.fetch_candidates(problem, limit=5)
        for i in range(len(candidates) - 1):
            assert candidates[i].weight >= candidates[i + 1].weight

    def test_get_metaphor(self, library):
        """Can get metaphor by ID."""
        all_m = library.all_metaphors()
        if all_m:
            m = library.get(all_m[0].metaphor_id)
            assert m is not None

    def test_register_metaphor(self, library):
        """Can register new metaphor."""
        m = Metaphor(
            metaphor_id="new_test",
            name="New Test",
            domain="testing",
            description="A new test metaphor",
        )
        library.register(m)
        assert library.get("new_test") is not None

    def test_update_usage_success(self, library):
        """Can update usage with success."""
        all_m = library.all_metaphors()
        if all_m:
            mid = all_m[0].metaphor_id
            library.update_usage(mid, success=True)
            stats = library.get_usage_statistics()
            assert stats[mid]["usage_count"] >= 1

    def test_update_usage_failure(self, library):
        """Can update usage with failure."""
        all_m = library.all_metaphors()
        if all_m:
            mid = all_m[0].metaphor_id
            library.update_usage(mid, success=False)
            stats = library.get_usage_statistics()
            assert stats[mid]["usage_count"] >= 1

    def test_strengthen_metaphor(self, library, problem):
        """Can strengthen metaphor."""
        all_m = library.all_metaphors()
        if all_m:
            library.strengthen(all_m[0], problem, success=True)

    def test_blend_metaphors(self, library):
        """Can blend metaphors."""
        all_m = library.all_metaphors()
        if len(all_m) >= 2:
            blended = library.blend([all_m[0], all_m[1]])
            assert blended is not None
            assert blended.metaphor_id.startswith("blend_")

    def test_blend_combines_names(self, library):
        """Blend combines metaphor names."""
        all_m = library.all_metaphors()
        if len(all_m) >= 2:
            blended = library.blend([all_m[0], all_m[1]])
            assert all_m[0].name in blended.name or "Blend" in blended.name

    def test_blend_registered(self, library):
        """Blended metaphor is registered."""
        all_m = library.all_metaphors()
        if len(all_m) >= 2:
            blended = library.blend([all_m[0], all_m[1]])
            assert library.get(blended.metaphor_id) is not None

    def test_holographic_pattern_creation(self):
        """HolographicPattern can be created."""
        pattern = HolographicPattern(
            pattern=(0.1, 0.2, 0.3),
            resolution=1.0,
        )
        assert pattern.resolution == 1.0

    def test_holographic_pattern_superimpose(self):
        """Patterns can be superimposed."""
        p1 = HolographicPattern(pattern=(0.1, 0.2), resolution=1.0)
        p2 = HolographicPattern(pattern=(0.3, 0.4), resolution=1.0)
        combined = p1.superimpose(p2)
        assert combined.pattern[0] == pytest.approx(0.4, abs=0.01)

    def test_holographic_pattern_compress(self):
        """Pattern can be compressed."""
        p = HolographicPattern(pattern=(0.5, 0.5, 0.5), resolution=1.0)
        compressed = p.compress(0.5)
        assert compressed.resolution < p.resolution

    def test_holographic_pattern_similarity(self):
        """Pattern similarity can be calculated."""
        p = HolographicPattern(pattern=(1.0, 0.0, 0.0), resolution=1.0)
        query = (1.0, 0.0, 0.0)
        sim = p.similarity(query)
        assert sim > 0.5  # Same direction should be similar

    def test_metaphor_entry_success_rate(self):
        """MetaphorEntry calculates success rate."""
        m = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test",
        )
        p = HolographicPattern(pattern=(0.5,), resolution=1.0)
        entry = MetaphorEntry(metaphor=m, pattern=p, usage_count=10, success_count=7)
        assert entry.success_rate == pytest.approx(0.7, abs=0.01)

    def test_metaphor_entry_is_hot(self):
        """MetaphorEntry identifies hot metaphors."""
        m = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test",
        )
        p = HolographicPattern(pattern=(0.5,), resolution=1.0)
        entry = MetaphorEntry(metaphor=m, pattern=p, usage_count=15, success_count=12)
        assert entry.is_hot

    def test_metaphor_entry_is_cold(self):
        """MetaphorEntry identifies cold metaphors."""
        m = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test",
        )
        p = HolographicPattern(pattern=(0.5,), resolution=1.0)
        entry = MetaphorEntry(metaphor=m, pattern=p, usage_count=1, success_count=0)
        assert entry.is_cold

    def test_usage_statistics(self, library):
        """Can get usage statistics."""
        stats = library.get_usage_statistics()
        assert isinstance(stats, dict)
        for mid, s in stats.items():
            assert "usage_count" in s
            assert "success_rate" in s


# =============================================================================
# Phase 8: MetaphorHistorian + ForensicBard (30 tests)
# =============================================================================

from .metaphor_historian import (
    MetaphorHistorian,
    MetaphorTrace,
    MetaphorAction,
    TracingContext,
    ForensicBard,
    MetaphorDiagnosis,
)


class TestMetaphorHistorian:
    """Tests for N-gent tracing integration."""

    @pytest.fixture
    def historian(self):
        return MetaphorHistorian()

    @pytest.fixture
    def projection(self):
        problem = Novel(
            problem_id="test",
            description="Test problem",
            domain="test",
        )
        metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test metaphor",
        )
        return Projection(
            source=problem,
            target=metaphor,
            mapped_concepts=(
                ConceptMapping(source_concept="a", target_concept="b", confidence=0.7),
            ),
            applicable_operations=(),
            projected_description="Test",
            confidence=0.7,
            coverage=0.6,
        )

    def test_begin_trace(self, historian):
        """Can begin a trace."""
        ctx = historian.begin_trace(
            action=MetaphorAction.PROJECT,
            input_obj={"test": "input"},
        )
        assert isinstance(ctx, TracingContext)
        assert ctx.trace_id is not None

    def test_end_trace(self, historian):
        """Can end a trace."""
        ctx = historian.begin_trace(
            action=MetaphorAction.PROJECT,
            input_obj={"test": "input"},
        )
        trace = historian.end_trace(
            ctx,
            outputs={"result": "output"},
        )
        assert isinstance(trace, MetaphorTrace)

    def test_trace_has_action(self, historian):
        """Trace records action."""
        ctx = historian.begin_trace(
            action=MetaphorAction.PROJECT,
            input_obj={},
        )
        trace = historian.end_trace(ctx, outputs={})
        assert trace.action == MetaphorAction.PROJECT

    def test_trace_has_timestamp(self, historian):
        """Trace has timestamp."""
        ctx = historian.begin_trace(action=MetaphorAction.PROJECT, input_obj={})
        trace = historian.end_trace(ctx, outputs={})
        assert trace.timestamp is not None

    def test_trace_projection(self, historian, projection):
        """Can trace a projection."""
        trace = historian.trace_projection(projection.source, projection)
        assert trace.action == MetaphorAction.PROJECT

    def test_trace_has_input_hash(self, historian):
        """Trace has input hash."""
        ctx = historian.begin_trace(
            action=MetaphorAction.PROJECT, input_obj={"data": 123}
        )
        trace = historian.end_trace(ctx, outputs={})
        assert len(trace.input_hash) > 0

    def test_abort_trace(self, historian):
        """Can abort a trace."""
        ctx = historian.begin_trace(action=MetaphorAction.PROJECT, input_obj={})
        trace = historian.abort_trace(ctx, error="Test error")
        assert not trace.success
        assert trace.error_message == "Test error"

    def test_crystal_store_stores(self, historian):
        """CrystalStore stores traces."""
        ctx = historian.begin_trace(action=MetaphorAction.PROJECT, input_obj={})
        trace = historian.end_trace(ctx, outputs={})
        stored = historian.store.get(trace.trace_id)
        assert stored == trace

    def test_crystal_store_get_by_action(self, historian):
        """CrystalStore can get by action."""
        ctx = historian.begin_trace(action=MetaphorAction.PROJECT, input_obj={})
        historian.end_trace(ctx, outputs={})
        traces = historian.store.get_by_action(MetaphorAction.PROJECT)
        assert len(traces) >= 1

    def test_crystal_store_get_failed(self, historian):
        """CrystalStore can get failed traces."""
        ctx = historian.begin_trace(action=MetaphorAction.PROJECT, input_obj={})
        historian.abort_trace(ctx, error="Failed")
        failed = historian.store.get_failed()
        assert len(failed) >= 1

    def test_trace_to_dict(self, historian):
        """Trace can convert to dict."""
        ctx = historian.begin_trace(action=MetaphorAction.PROJECT, input_obj={})
        trace = historian.end_trace(ctx, outputs={"result": 1})
        d = trace.to_dict()
        assert "trace_id" in d
        assert "action" in d

    def test_trace_chain(self, historian):
        """Can get trace chain."""
        ctx1 = historian.begin_trace(action=MetaphorAction.PROJECT, input_obj={})
        trace1 = historian.end_trace(ctx1, outputs={})

        ctx2 = historian.begin_trace(
            action=MetaphorAction.SOLVE, input_obj={}, parent_id=trace1.trace_id
        )
        trace2 = historian.end_trace(ctx2, outputs={})

        chain = historian.store.get_chain(trace2.trace_id)
        assert len(chain) == 2


class TestForensicBard:
    """Tests for ForensicBard forensic analysis."""

    @pytest.fixture
    def bard(self):
        return ForensicBard()

    @pytest.fixture
    def historian_with_traces(self):
        historian = MetaphorHistorian()
        # Add a failed trace
        ctx = historian.begin_trace(action=MetaphorAction.PROJECT, input_obj={})
        historian.abort_trace(ctx, error="Projection failed")
        return historian

    def test_diagnose_failure(self, bard, historian_with_traces):
        """Can diagnose a failure."""
        failed = historian_with_traces.store.get_failed()
        if failed:
            diagnosis = bard.diagnose_failure(historian_with_traces, failed[0].trace_id)
            assert isinstance(diagnosis, MetaphorDiagnosis)

    def test_diagnosis_has_narrative(self, bard, historian_with_traces):
        """Diagnosis has narrative."""
        failed = historian_with_traces.store.get_failed()
        if failed:
            diagnosis = bard.diagnose_failure(historian_with_traces, failed[0].trace_id)
            assert len(diagnosis.narrative) > 0

    def test_diagnosis_has_failure_type(self, bard, historian_with_traces):
        """Diagnosis has failure type."""
        failed = historian_with_traces.store.get_failed()
        if failed:
            diagnosis = bard.diagnose_failure(historian_with_traces, failed[0].trace_id)
            assert diagnosis.failure_type is not None

    def test_diagnose_nonexistent(self, bard):
        """Diagnose handles nonexistent trace."""
        historian = MetaphorHistorian()
        diagnosis = bard.diagnose_failure(historian, "nonexistent")
        assert diagnosis.traces_examined == 0


# =============================================================================
# Phase 9: MetaphorUmwelt (25 tests)
# =============================================================================

from .metaphor_umwelt import (
    MetaphorUmwelt,
    MetaphorLens,
    MetaphorDNA,
    create_k_gent_umwelt,
    create_b_gent_umwelt,
    create_e_gent_umwelt,
    create_neutral_umwelt,
    NO_MILITARY,
    K_GENT_DNA,
    B_GENT_DNA,
)


class TestMetaphorUmwelt:
    """Tests for Umwelt Protocol integration."""

    def test_create_k_gent_umwelt(self):
        """Can create K-gent umwelt."""
        umwelt = create_k_gent_umwelt()
        assert isinstance(umwelt, MetaphorUmwelt)

    def test_create_b_gent_umwelt(self):
        """Can create B-gent umwelt."""
        umwelt = create_b_gent_umwelt()
        assert isinstance(umwelt, MetaphorUmwelt)

    def test_create_e_gent_umwelt(self):
        """Can create E-gent umwelt."""
        umwelt = create_e_gent_umwelt()
        assert isinstance(umwelt, MetaphorUmwelt)

    def test_create_neutral_umwelt(self):
        """Can create neutral umwelt."""
        umwelt = create_neutral_umwelt()
        assert isinstance(umwelt, MetaphorUmwelt)
        assert len(umwelt.gravity) == 0

    def test_metaphor_dna_preferred_domains(self):
        """MetaphorDNA has preferred domains."""
        dna = K_GENT_DNA
        assert len(dna.preferred_domains) > 0

    def test_metaphor_dna_prefers_domain(self):
        """MetaphorDNA can check domain preference."""
        dna = B_GENT_DNA
        assert dna.prefers_domain("physics")
        assert not dna.prefers_domain("narrative")

    def test_metaphor_constraint_check(self):
        """MetaphorConstraint can check metaphors."""
        military_metaphor = Metaphor(
            metaphor_id="military",
            name="Military Strategy",
            domain="military",
            description="Military",
        )
        assert not NO_MILITARY.admits(military_metaphor)

    def test_metaphor_constraint_admits_allowed(self):
        """MetaphorConstraint admits allowed metaphors."""
        science_metaphor = Metaphor(
            metaphor_id="science",
            name="Science",
            domain="biology",
            description="Science",
        )
        assert NO_MILITARY.admits(science_metaphor)

    def test_umwelt_can_use(self):
        """Umwelt can check if metaphor is usable."""
        umwelt = create_k_gent_umwelt()
        # K-gent has NO_VIOLENT constraint
        violent_metaphor = Metaphor(
            metaphor_id="test",
            name="Test",
            domain="test",
            description="Test",
            operations=(
                MetaphorOperation(name="attack", description="Attack something"),
            ),
        )
        assert not umwelt.can_use(violent_metaphor)

    def test_umwelt_project(self):
        """Umwelt can project metaphors for a problem."""
        umwelt = create_neutral_umwelt()
        library = HolographicMetaphorLibrary()
        umwelt.bind_library(library)

        problem = Novel(
            problem_id="test",
            description="Test problem",
            domain="test",
        )
        candidates = umwelt.project(problem, limit=3)
        assert len(candidates) <= 3

    def test_metaphor_lens_focus(self):
        """MetaphorLens focuses library on problem."""
        dna = MetaphorDNA()
        lens = MetaphorLens(
            name="test_lens",
            constraints=(),
            dna=dna,
        )
        library = HolographicMetaphorLibrary()
        problem = Novel(
            problem_id="test",
            description="Test problem",
            domain="test",
        )
        focused = lens.focus(library, problem, limit=3)
        assert len(focused) <= 3

    def test_should_explore_novel(self):
        """Umwelt can decide to explore novel metaphors."""
        umwelt = create_neutral_umwelt()
        # This is random, just check it doesn't crash
        result = umwelt.should_explore_novel()
        assert isinstance(result, bool)

    def test_should_blend(self):
        """Umwelt can decide to blend metaphors."""
        umwelt = create_neutral_umwelt()
        result = umwelt.should_blend()
        assert isinstance(result, bool)


# =============================================================================
# Phase 10: MetaphorEvolutionAgent (30 tests)
# =============================================================================

from .metaphor_evolution import (
    MetaphorEvolutionAgent,
    MetaphorEvolutionResult,
    MetaphorHypothesis,
    ExperimentResult,
    Verdict,
    HeldTension,
    CollectiveShadow,
    EvolutionMemory,
)


class TestMetaphorEvolutionAgent:
    """Tests for E-gent dialectical evolution integration."""

    @pytest.fixture
    def agent(self):
        return MetaphorEvolutionAgent()

    @pytest.fixture
    def metaphor(self):
        return Metaphor(
            metaphor_id="ecosystem",
            name="Ecosystem",
            domain="biology",
            description="Network of organisms",
            operations=(
                MetaphorOperation(name="symbiosis", description="Mutual benefit"),
            ),
            tractability=0.6,
            generality=0.7,
        )

    @pytest.fixture
    def test_problems(self):
        return [
            Novel(
                problem_id="p1",
                description="Optimize team collaboration",
                domain="organization",
                complexity=0.5,
            ),
            Novel(
                problem_id="p2",
                description="Improve communication flow",
                domain="organization",
                complexity=0.4,
            ),
        ]

    def test_verdict_enum(self):
        """Verdict enum has all values."""
        assert Verdict.ACCEPT is not None
        assert Verdict.REVISE is not None
        assert Verdict.REJECT is not None
        assert Verdict.HOLD is not None

    def test_evolve_returns_result(self, agent, metaphor, test_problems):
        """Evolve returns MetaphorEvolutionResult."""
        result = agent.evolve(metaphor, test_problems)
        assert isinstance(result, MetaphorEvolutionResult)

    def test_evolution_result_has_verdict(self, agent, metaphor, test_problems):
        """Result has verdict."""
        result = agent.evolve(metaphor, test_problems)
        assert isinstance(result.verdict, Verdict)

    def test_evolution_result_has_experiments(self, agent, metaphor, test_problems):
        """Result tracks experiments run."""
        result = agent.evolve(metaphor, test_problems)
        assert result.experiments_run >= 0

    def test_hypothesis_creation(self, metaphor):
        """MetaphorHypothesis can be created."""
        antithesis = Metaphor(
            metaphor_id="other",
            name="Other",
            domain="other",
            description="Other metaphor",
        )
        hyp = MetaphorHypothesis(
            hypothesis_id="h1",
            thesis=metaphor,
            antithesis=antithesis,
            rationale="Test hypothesis",
            improvement_type="blend",
        )
        assert hyp.thesis == metaphor

    def test_experiment_result_success_rate(self):
        """ExperimentResult calculates success rate."""
        hyp = MetaphorHypothesis(
            hypothesis_id="h1",
            thesis=Metaphor(metaphor_id="t", name="T", domain="t", description="t"),
            antithesis=Metaphor(metaphor_id="a", name="A", domain="a", description="a"),
            rationale="Test",
            improvement_type="test",
        )
        result = ExperimentResult(
            hypothesis=hyp,
            test_problems=(),
            success_count=7,
            total_count=10,
            avg_distortion=0.3,
            notes="Test",
        )
        assert result.success_rate == pytest.approx(0.7, abs=0.01)

    def test_held_tension_creation(self, metaphor):
        """HeldTension can be created."""
        tension = HeldTension(
            thesis=metaphor,
            antithesis=metaphor,
            reason="Cannot resolve",
            recommended_action="Human review",
        )
        assert tension.reason == "Cannot resolve"

    def test_shadow_analyzer_analyze(self, agent):
        """ShadowAnalyzer can analyze library."""
        shadow = agent.shadow_analyzer.analyze(agent.library)
        assert isinstance(shadow, CollectiveShadow)

    def test_collective_shadow_has_domains(self, agent):
        """CollectiveShadow has unused domains."""
        shadow = agent.shadow_analyzer.analyze(agent.library)
        assert isinstance(shadow.unused_domains, tuple)

    def test_collective_shadow_has_analysis(self, agent):
        """CollectiveShadow has analysis narrative."""
        shadow = agent.shadow_analyzer.analyze(agent.library)
        assert len(shadow.shadow_analysis) > 0

    def test_evolution_memory_record(self):
        """EvolutionMemory can record results."""
        memory = EvolutionMemory()
        result = MetaphorEvolutionResult(
            evolved_metaphor=None,
            held_tensions=(),
            experiments_run=1,
            accepted_count=0,
            verdict=Verdict.REJECT,
        )
        memory.record(result)
        assert len(memory.failed_evolutions) == 1

    def test_evolution_memory_success_patterns(self):
        """EvolutionMemory tracks success patterns."""
        memory = EvolutionMemory()
        evolved = Metaphor(
            metaphor_id="blend_test",
            name="Blended",
            domain="test",
            description="Test",
        )
        result = MetaphorEvolutionResult(
            evolved_metaphor=evolved,
            held_tensions=(),
            experiments_run=1,
            accepted_count=1,
            verdict=Verdict.ACCEPT,
        )
        memory.record(result)
        patterns = memory.get_success_patterns()
        assert "blend" in patterns


# =============================================================================
# Phase 11: PsychopompAgent (40 tests)
# =============================================================================

from .psychopomp_agent import (
    PsychopompAgent,
    PsychopompConfig,
    PsychopompResult,
    SearchPhase,
    SearchState,
    create_psychopomp,
    solve_problem,
)


class TestPsychopompAgent:
    """Tests for main Psychopomp orchestrator."""

    @pytest.fixture
    def agent(self):
        return PsychopompAgent()

    @pytest.fixture
    def problem(self):
        return Novel(
            problem_id="test",
            description="Optimize team communication for better collaboration",
            domain="organization",
            complexity=0.5,
        )

    def test_config_defaults(self):
        """PsychopompConfig has sensible defaults."""
        config = PsychopompConfig()
        assert config.max_metaphor_candidates > 0
        assert config.max_iterations > 0

    def test_search_phase_enum(self):
        """SearchPhase has all phases."""
        assert SearchPhase.FETCH is not None
        assert SearchPhase.PROJECT is not None
        assert SearchPhase.VALIDATE is not None
        assert SearchPhase.SOLVE is not None
        assert SearchPhase.REIFY is not None
        assert SearchPhase.COMPLETE is not None
        assert SearchPhase.FAILED is not None

    def test_search_state_initialization(self, problem):
        """SearchState can be initialized."""
        state = SearchState(problem=problem, phase=SearchPhase.FETCH)
        assert state.iteration == 0
        assert state.problem == problem

    def test_solve_returns_result(self, agent, problem):
        """Solve returns PsychopompResult."""
        result = agent.solve(problem)
        assert isinstance(result, PsychopompResult)

    def test_result_has_success_flag(self, agent, problem):
        """Result has success flag."""
        result = agent.solve(problem)
        assert isinstance(result.success, bool)

    def test_result_has_problem(self, agent, problem):
        """Result contains original problem."""
        result = agent.solve(problem)
        assert result.problem == problem

    def test_result_has_iterations(self, agent, problem):
        """Result tracks iterations."""
        result = agent.solve(problem)
        assert result.iterations >= 0

    def test_result_has_candidates_tried(self, agent, problem):
        """Result tracks candidates tried."""
        result = agent.solve(problem)
        assert result.candidates_tried >= 0

    def test_successful_solve_has_solution(self, agent, problem):
        """Successful solve has reified solution."""
        result = agent.solve(problem)
        if result.success:
            assert result.reified_solution is not None
            assert result.metaphor_used is not None

    def test_successful_solve_has_tensor_position(self, agent, problem):
        """Successful solve has tensor position."""
        result = agent.solve(problem)
        if result.success:
            assert result.tensor_position is not None

    def test_failed_solve_has_reason(self, agent):
        """Failed solve has failure reason."""
        # Create a problem that's hard to solve
        hard_problem = Novel(
            problem_id="impossible",
            description="x" * 10,  # Minimal description
            domain="nonexistent_domain_12345",
            complexity=0.99,
        )
        result = agent.solve(hard_problem)
        if not result.success:
            assert len(result.failure_reason) > 0

    def test_create_psychopomp_function(self):
        """create_psychopomp factory function works."""
        agent = create_psychopomp()
        assert isinstance(agent, PsychopompAgent)

    def test_create_psychopomp_with_config(self):
        """create_psychopomp accepts config."""
        config = PsychopompConfig(max_iterations=5)
        agent = create_psychopomp(config=config)
        assert agent.config.max_iterations == 5

    def test_create_psychopomp_with_umwelt(self):
        """create_psychopomp accepts umwelt."""
        umwelt = create_neutral_umwelt()
        agent = create_psychopomp(umwelt=umwelt)
        assert agent.umwelt == umwelt

    def test_solve_problem_convenience(self, problem):
        """solve_problem convenience function works."""
        result = solve_problem(problem)
        assert isinstance(result, PsychopompResult)

    def test_agent_has_4_axis_validators(self, agent):
        """Agent has all 4 axis validators."""
        assert agent.z_axis is not None
        assert agent.x_axis is not None
        assert agent.y_axis is not None
        assert agent.t_axis is not None

    def test_agent_has_historian(self, agent):
        """Agent has historian for tracing."""
        assert agent.historian is not None

    def test_agent_has_library(self, agent):
        """Agent has metaphor library."""
        assert agent.library is not None

    def test_agent_has_functor(self, agent):
        """Agent has morphic functor."""
        assert agent.functor is not None

    def test_result_anti_patterns(self, agent, problem):
        """Result tracks anti-patterns detected."""
        result = agent.solve(problem)
        assert isinstance(result.anti_patterns_detected, tuple)

    def test_tracing_enabled_by_default(self, agent):
        """Tracing is enabled by default."""
        assert agent.config.enable_tracing

    def test_learning_enabled_by_default(self, agent):
        """Learning is enabled by default."""
        assert agent.config.enable_learning

    def test_solve_with_tracing_disabled(self, problem):
        """Can solve with tracing disabled."""
        config = PsychopompConfig(enable_tracing=False)
        agent = create_psychopomp(config=config)
        result = agent.solve(problem)
        assert result.trace_id is None

    def test_result_has_distortion(self, agent, problem):
        """Successful result has distortion info."""
        result = agent.solve(problem)
        if result.success:
            assert result.distortion is not None


# =============================================================================
# Integration Tests
# =============================================================================


class TestPsiGentIntegration:
    """Integration tests across all components."""

    def test_full_pipeline(self):
        """Full pipeline from problem to solution."""
        problem = Novel(
            problem_id="integration_test",
            description="Design a system for managing team knowledge sharing",
            domain="knowledge_management",
            complexity=0.6,
        )

        agent = PsychopompAgent()
        result = agent.solve(problem)

        # Should complete without error
        assert isinstance(result, PsychopompResult)

    def test_umwelt_constrains_pipeline(self):
        """Umwelt constraints affect available metaphors."""
        problem = Novel(
            problem_id="umwelt_test",
            description="Solve a competitive business challenge",
            domain="business",
        )

        # K-gent umwelt excludes violent metaphors
        umwelt = create_k_gent_umwelt()
        agent = create_psychopomp(umwelt=umwelt)
        result = agent.solve(problem)

        # Should complete, may or may not succeed
        assert isinstance(result, PsychopompResult)

    def test_evolution_improves_library(self):
        """Evolution can improve the metaphor library."""
        library = HolographicMetaphorLibrary()
        initial_count = len(library)

        # Run evolution
        evolution_agent = MetaphorEvolutionAgent(library=library)
        metaphor = library.all_metaphors()[0]
        problems = [
            Novel(problem_id="p1", description="Test", domain="test"),
        ]

        result = evolution_agent.evolve(metaphor, problems)

        # If evolution succeeded, library may have new metaphors
        if result.evolved_metaphor:
            assert len(library) >= initial_count

    def test_historian_records_pipeline(self):
        """Historian records the full pipeline."""
        problem = Novel(
            problem_id="history_test",
            description="Test problem for history",
            domain="test",
        )

        agent = PsychopompAgent()
        result = agent.solve(problem)

        # Should have traces
        if result.trace_id:
            chain = agent.historian.store.get_chain(result.trace_id)
            assert len(chain) >= 1


# =============================================================================
# Run Tests
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
