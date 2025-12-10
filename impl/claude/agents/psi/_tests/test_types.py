"""Tests for Psi-gent types."""

import pytest

from ..types import (
    Problem,
    Metaphor,
    Operation,
    ConceptMapping,
    Projection,
    ChallengeResult,
    MetaphorSolution,
    Solution,
    Distortion,
    SearchState,
    Outcome,
    validate_distortion,
    validate_projection,
    validate_metaphor,
    to_dict,
    to_json,
)


# =============================================================================
# Problem Tests
# =============================================================================


class TestProblem:
    """Tests for Problem type."""

    def test_create_minimal(self):
        """Create problem with minimal fields."""
        p = Problem(id="test", description="Test problem", domain="test")
        assert p.id == "test"
        assert p.domain == "test"
        assert p.constraints == ()
        assert p.embedding is None

    def test_create_full(self):
        """Create problem with all fields."""
        p = Problem(
            id="full",
            description="Full problem",
            domain="software",
            constraints=("fast", "cheap"),
            context={"priority": "high"},
            embedding=(0.1, 0.2, 0.3),
        )
        assert p.constraints == ("fast", "cheap")
        assert p.context["priority"] == "high"
        assert p.embedding == (0.1, 0.2, 0.3)

    def test_complexity_scales_with_description(self):
        """Complexity increases with description length."""
        short = Problem(id="1", description="Short", domain="test")
        long = Problem(id="2", description="A" * 500, domain="test")
        assert long.complexity > short.complexity

    def test_complexity_scales_with_constraints(self):
        """Complexity increases with constraint count."""
        few = Problem(id="1", description="Test", domain="test", constraints=("one",))
        many = Problem(
            id="2",
            description="Test",
            domain="test",
            constraints=tuple(f"c{i}" for i in range(5)),
        )
        assert many.complexity > few.complexity

    def test_complexity_bounded(self):
        """Complexity is bounded to [0, 1]."""
        p = Problem(
            id="1",
            description="A" * 5000,
            domain="test",
            constraints=tuple(f"c{i}" for i in range(50)),
        )
        assert 0.0 <= p.complexity <= 1.0

    def test_with_embedding(self):
        """with_embedding creates new instance."""
        p1 = Problem(id="1", description="Test", domain="test")
        p2 = p1.with_embedding((0.5, 0.5))
        assert p1.embedding is None
        assert p2.embedding == (0.5, 0.5)
        assert p1.id == p2.id

    def test_frozen(self):
        """Problem is immutable."""
        p = Problem(id="1", description="Test", domain="test")
        with pytest.raises(AttributeError):
            p.id = "2"  # type: ignore


# =============================================================================
# Metaphor Tests
# =============================================================================


class TestMetaphor:
    """Tests for Metaphor type."""

    def test_create_minimal(self):
        """Create metaphor with minimal fields."""
        m = Metaphor(
            id="test",
            name="Test",
            domain="test",
            description="Test metaphor",
            operations=(),
        )
        assert m.id == "test"
        assert m.tractability == 0.0  # No operations

    def test_tractability_scales_with_operations(self):
        """Tractability increases with operation count."""
        ops = tuple(
            Operation(name=f"op{i}", description=f"Op {i}", effects=(f"effect{i}",))
            for i in range(5)
        )
        m = Metaphor(
            id="test",
            name="Test",
            domain="test",
            description="Test metaphor",
            operations=ops,
        )
        assert m.tractability == 1.0  # 5 operations = max

    def test_with_embedding(self):
        """with_embedding creates new instance."""
        m1 = Metaphor(
            id="1", name="Test", domain="test", description="Test", operations=()
        )
        m2 = m1.with_embedding((0.1, 0.2))
        assert m1.embedding is None
        assert m2.embedding == (0.1, 0.2)


# =============================================================================
# Distortion Tests
# =============================================================================


class TestDistortion:
    """Tests for Distortion type."""

    def test_total_combines_weighted(self):
        """Total distortion combines dimensions with weights."""
        d = Distortion(structural_loss=0.5, round_trip_error=0.5, prediction_failures=0)
        # 0.5 * 0.3 + 0.5 * 0.4 + 0 * 0.3 = 0.15 + 0.2 = 0.35
        assert 0.34 < d.total < 0.36

    def test_acceptable_threshold(self):
        """Acceptable means total < 0.5."""
        low = Distortion(0.1, 0.1, 0)
        high = Distortion(0.9, 0.9, 5)
        assert low.acceptable
        assert not high.acceptable

    def test_prediction_failures_contribute(self):
        """Prediction failures add to distortion."""
        d0 = Distortion(0, 0, 0)
        d3 = Distortion(0, 0, 3)
        assert d3.total > d0.total

    @pytest.mark.law
    def test_distortion_invariants(self):
        """Distortion components must be valid."""
        valid = Distortion(0.5, 0.5, 2)
        assert validate_distortion(valid) == []

        invalid_structural = Distortion(1.5, 0.5, 0)
        errors = validate_distortion(invalid_structural)
        assert any("structural_loss" in e for e in errors)

        invalid_rte = Distortion(0.5, -0.1, 0)
        errors = validate_distortion(invalid_rte)
        assert any("round_trip_error" in e for e in errors)


# =============================================================================
# Projection Tests
# =============================================================================


class TestProjection:
    """Tests for Projection type."""

    @pytest.fixture
    def sample_projection(self):
        """Create a sample projection."""
        problem = Problem(id="1", description="Test", domain="test")
        metaphor = Metaphor(
            id="m1", name="Test", domain="test", description="Test", operations=()
        )
        mappings = (
            ConceptMapping(source="a", target="x", confidence=0.8),
            ConceptMapping(source="b", target="y", confidence=0.6),
        )
        return Projection(
            problem=problem,
            metaphor=metaphor,
            mappings=mappings,
            abstraction=0.5,
            gaps=("c",),
        )

    def test_coverage(self, sample_projection):
        """Coverage is mappings / (mappings + gaps)."""
        # 2 mappings, 1 gap = 2/3
        assert 0.66 < sample_projection.coverage < 0.67

    def test_coverage_empty(self):
        """Coverage is 0 with no mappings."""
        p = Projection(
            problem=Problem(id="1", description="Test", domain="test"),
            metaphor=Metaphor(
                id="m1", name="Test", domain="test", description="Test", operations=()
            ),
            mappings=(),
            abstraction=0.5,
        )
        assert p.coverage == 0.0

    @pytest.mark.law
    def test_projection_invariants(self, sample_projection):
        """Projection invariants must hold."""
        assert validate_projection(sample_projection) == []

        # Invalid abstraction
        invalid = Projection(
            problem=sample_projection.problem,
            metaphor=sample_projection.metaphor,
            mappings=sample_projection.mappings,
            abstraction=1.5,  # Out of bounds
        )
        errors = validate_projection(invalid)
        assert any("abstraction" in e for e in errors)


# =============================================================================
# ChallengeResult Tests
# =============================================================================


class TestChallengeResult:
    """Tests for ChallengeResult type."""

    def test_robustness(self):
        """Robustness is passed / total."""
        cr = ChallengeResult(survives=True, challenges_passed=3, challenges_total=4)
        assert cr.robustness == 0.75

    def test_robustness_no_tests(self):
        """Robustness is 0.5 with no tests."""
        cr = ChallengeResult(survives=True, challenges_passed=0, challenges_total=0)
        assert cr.robustness == 0.5


# =============================================================================
# SearchState Tests
# =============================================================================


class TestSearchState:
    """Tests for SearchState type."""

    def test_mutable(self):
        """SearchState is mutable."""
        problem = Problem(id="1", description="Test", domain="test")
        state = SearchState(problem)
        state.iteration = 5
        assert state.iteration == 5

    def test_record_attempt(self):
        """record_attempt updates state."""
        problem = Problem(id="1", description="Test", domain="test")
        state = SearchState(problem)

        state.record_attempt("metaphor1", None, "projected")
        assert "metaphor1" in state.candidates_tried
        assert state.iteration == 1

    def test_update_best(self):
        """update_best tracks best solution."""
        problem = Problem(id="1", description="Test", domain="test")
        state = SearchState(problem)

        metaphor = Metaphor(
            id="m1", name="Test", domain="test", description="Test", operations=()
        )
        projection = Projection(
            problem=problem, metaphor=metaphor, mappings=(), abstraction=0.5
        )
        ms = MetaphorSolution(
            projection=projection, reasoning="", operations_applied=(), conclusion=""
        )

        solution1 = Solution(
            problem=problem,
            metaphor_solution=ms,
            translated_answer="",
            specific_actions=(),
            distortion=Distortion(0.5, 0.5, 0),
        )
        solution2 = Solution(
            problem=problem,
            metaphor_solution=ms,
            translated_answer="",
            specific_actions=(),
            distortion=Distortion(0.1, 0.1, 0),
        )

        state.update_best(solution1)
        assert state.best_distortion == solution1.distortion.total

        state.update_best(solution2)
        assert state.best_distortion == solution2.distortion.total
        assert state.best_solution == solution2


# =============================================================================
# Serialization Tests
# =============================================================================


class TestSerialization:
    """Tests for serialization utilities."""

    def test_to_dict_problem(self):
        """Problem serializes to dict."""
        p = Problem(id="1", description="Test", domain="test", constraints=("a", "b"))
        d = to_dict(p)
        assert d["id"] == "1"
        assert d["constraints"] == ["a", "b"]

    def test_to_dict_outcome(self):
        """Enum serializes to value."""
        d = to_dict(Outcome.SUCCESS)
        assert d == "success"

    def test_to_json(self):
        """to_json produces valid JSON."""
        p = Problem(id="1", description="Test", domain="test")
        json_str = to_json(p)
        assert '"id": "1"' in json_str


# =============================================================================
# Validation Tests
# =============================================================================


class TestValidation:
    """Tests for validation functions."""

    @pytest.mark.law
    def test_validate_metaphor_needs_operations(self):
        """Non-null metaphor needs operations."""
        m = Metaphor(
            id="test",
            name="Test",
            domain="test",
            description="Test metaphor description",
            operations=(),
        )
        errors = validate_metaphor(m)
        assert any("no operations" in e for e in errors)

    def test_validate_metaphor_operations_need_effects(self):
        """Operations need effects."""
        op = Operation(name="test", description="Test op")  # No effects
        m = Metaphor(
            id="test",
            name="Test",
            domain="test",
            description="Test metaphor description",
            operations=(op,),
        )
        errors = validate_metaphor(m)
        assert any("no effects" in e for e in errors)

    def test_validate_metaphor_valid(self):
        """Valid metaphor passes validation."""
        op = Operation(name="test", description="Test op", effects=("something",))
        m = Metaphor(
            id="test",
            name="Test",
            domain="test",
            description="Test metaphor description",
            operations=(op,),
        )
        errors = validate_metaphor(m)
        # Only "no operations" error should not appear
        assert not any("no operations" in e for e in errors)
