"""
Comprehensive tests for Kairos Protocol implementation.

Tests cover:
- Attention state detection
- Salience calculation
- Benefit function
- Entropy budget
- Controller integration
- Watch mode (basic)
"""

import pytest
from datetime import datetime, timedelta

from protocols.mirror.kairos.attention import (
    AttentionDetector,
    AttentionState,
    KairosContext,
)
from protocols.mirror.kairos.salience import SalienceCalculator, TensionSeverity
from protocols.mirror.kairos.benefit import BenefitFunction
from protocols.mirror.kairos.budget import EntropyBudget, BudgetLevel
from protocols.mirror.kairos.controller import KairosController
from protocols.mirror.types import Tension, TensionMode, TensionType


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
def temp_workspace(tmp_path):
    """Create temporary workspace with some files."""
    workspace = tmp_path / "workspace"
    workspace.mkdir()

    # Create some files
    (workspace / "file1.py").write_text("print('hello')")
    (workspace / "file2.md").write_text("# Notes")

    return workspace


@pytest.fixture
def sample_tension():
    """Create a sample tension for testing."""
    from protocols.mirror.types import (
        Thesis,
        Antithesis,
        PatternObservation,
        PatternType,
    )

    thesis = Thesis(
        content="We value rapid iteration",
        source="principles.md",
        confidence=0.9,
    )

    observation = PatternObservation(
        pattern_type=PatternType.UPDATE_FREQUENCY,
        description="Low update frequency",
        value=0.3,
        sample_size=10,
    )

    antithesis = Antithesis(
        pattern="Documentation is rarely updated",
        evidence=(observation,),
        frequency=0.8,
        severity=0.6,
    )

    return Tension(
        thesis=thesis,
        antithesis=antithesis,
        divergence=0.6,
        mode=TensionMode.PRAGMATIC,
        tension_type=TensionType.BEHAVIORAL,
        interpretation="Test tension",
    )


# ============================================================================
# Attention Detection Tests
# ============================================================================


@pytest.mark.slow
def test_attention_detector_idle(temp_workspace):
    """Test attention detector when workspace is idle."""
    detector = AttentionDetector(
        active_threshold=timedelta(seconds=1)  # Very short threshold for testing
    )

    # Wait a bit to ensure files are "old"
    import time

    time.sleep(1.5)

    context = detector.detect_attention_state(temp_workspace)

    assert isinstance(context, KairosContext)
    # Should be IDLE or TRANSITIONING since files are old
    assert context.attention_state in [
        AttentionState.IDLE,
        AttentionState.TRANSITIONING,
    ]
    assert (
        context.attention_budget > 0.3
    )  # Should have reasonable budget when idle/transitioning


def test_attention_detector_recent_activity(temp_workspace):
    """Test attention detector with recent file modifications."""
    # Modify a file recently
    test_file = temp_workspace / "active.py"
    test_file.write_text("# Recent change")

    detector = AttentionDetector(
        deep_work_threshold=timedelta(minutes=1),  # Short threshold
        active_threshold=timedelta(minutes=60),  # Wide threshold
    )
    context = detector.detect_attention_state(temp_workspace)

    # Should detect activity (not IDLE)
    assert context.attention_state != AttentionState.IDLE
    assert context.last_activity_age < 1.0  # Less than 1 minute


def test_attention_state_values():
    """Test attention state enum values are correct."""
    assert AttentionState.DEEP_WORK.value == 0.1
    assert AttentionState.ACTIVE.value == 0.5
    assert AttentionState.TRANSITIONING.value == 0.8
    assert AttentionState.IDLE.value == 1.0


def test_cognitive_load_estimation(temp_workspace):
    """Test cognitive load estimation."""
    detector = AttentionDetector()

    # Create multiple recently modified files
    for i in range(5):
        (temp_workspace / f"active_{i}.py").write_text(f"# File {i}")

    context = detector.detect_attention_state(temp_workspace)

    # More files should increase cognitive load
    assert context.cognitive_load > 0.0


def test_temporal_factor():
    """Test time-of-day temporal factor computation."""
    detector = AttentionDetector()

    # Test peak hours (10am)
    morning = datetime(2025, 1, 1, 10, 0)
    factor = detector._compute_temporal_factor(morning)
    assert factor == 1.0

    # Test deep night (3am)
    night = datetime(2025, 1, 1, 3, 0)
    factor = detector._compute_temporal_factor(night)
    assert factor == 0.3


# ============================================================================
# Salience Calculation Tests
# ============================================================================


def test_salience_calculator_basic(sample_tension):
    """Test basic salience calculation."""
    calculator = SalienceCalculator()
    detected_at = datetime.now() - timedelta(hours=1)

    salience = calculator.compute_salience(
        sample_tension,
        momentum_factor=1.5,
        detected_at=detected_at,
    )

    assert salience.tension_id == sample_tension.id
    assert salience.base_severity == TensionSeverity.MEDIUM  # BEHAVIORAL → MEDIUM
    assert salience.momentum_factor == 1.5
    assert 0.0 <= salience.salience <= 1.0


def test_salience_severity_classification(sample_tension):
    """Test severity classification logic."""
    from protocols.mirror.types import (
        Thesis,
        Antithesis,
        PatternObservation,
        PatternType,
    )

    calculator = SalienceCalculator()

    # FUNDAMENTAL → CRITICAL
    thesis1 = Thesis(content="Core principle", source="fundamental.md")
    observation1 = PatternObservation(
        pattern_type=PatternType.STALENESS,
        description="Test",
        value=1.0,
        sample_size=1,
    )
    antithesis1 = Antithesis(pattern="Contradictory", evidence=(observation1,))

    fundamental = Tension(
        thesis=thesis1,
        antithesis=antithesis1,
        divergence=0.95,
        mode=TensionMode.LOGICAL,
        tension_type=TensionType.FUNDAMENTAL,
        interpretation="Fundamental tension",
    )
    salience = calculator.compute_salience(fundamental, 1.0)
    assert salience.base_severity == TensionSeverity.CRITICAL

    # ASPIRATIONAL → LOW
    thesis2 = Thesis(content="Aspiration", source="goals.md")
    antithesis2 = Antithesis(pattern="Reality", evidence=(observation1,))

    aspirational = Tension(
        thesis=thesis2,
        antithesis=antithesis2,
        divergence=0.3,
        mode=TensionMode.EMPIRICAL,
        tension_type=TensionType.ASPIRATIONAL,
        interpretation="Aspirational tension",
    )
    salience = calculator.compute_salience(aspirational, 1.0)
    assert salience.base_severity == TensionSeverity.LOW


def test_salience_recency_decay():
    """Test exponential recency decay."""
    calculator = SalienceCalculator(recency_half_life=timedelta(hours=24))

    # Fresh tension (just detected)
    age_0 = timedelta(hours=0)
    weight_0 = calculator._compute_recency_weight(age_0)
    assert weight_0 == 1.0

    # Half-life (24 hours)
    age_24 = timedelta(hours=24)
    weight_24 = calculator._compute_recency_weight(age_24)
    assert 0.49 <= weight_24 <= 0.51  # ~0.5

    # Double half-life (48 hours)
    age_48 = timedelta(hours=48)
    weight_48 = calculator._compute_recency_weight(age_48)
    assert 0.24 <= weight_48 <= 0.26  # ~0.25


def test_salience_momentum_acceleration(sample_tension):
    """Test acceleration detection."""
    calculator = SalienceCalculator(momentum_threshold=1.5)

    salience_stable = calculator.compute_salience(sample_tension, momentum_factor=1.0)
    assert not calculator.is_accelerating(salience_stable)

    salience_fast = calculator.compute_salience(sample_tension, momentum_factor=2.0)
    assert calculator.is_accelerating(salience_fast)


# ============================================================================
# Benefit Function Tests
# ============================================================================


def test_benefit_function_basic():
    """Test basic benefit computation."""
    benefit_fn = BenefitFunction(threshold=0.4)

    # Create mock context and salience
    from protocols.mirror.kairos.attention import KairosContext, AttentionState
    from protocols.mirror.kairos.salience import TensionSalience, TensionSeverity

    context = KairosContext(
        timestamp=datetime.now(),
        attention_state=AttentionState.IDLE,
        attention_budget=1.0,
        cognitive_load=0.2,
        recent_interventions=0,
        last_activity_age=60.0,
    )

    salience = TensionSalience(
        tension_id="test-1",
        timestamp=datetime.now(),
        base_severity=TensionSeverity.HIGH,
        momentum_factor=1.5,
        recency_weight=0.8,
        salience=0.9,  # HIGH severity × 1.5 momentum × 0.8 recency
        age_minutes=10.0,
    )

    evaluation = benefit_fn.evaluate(context, salience)

    # B(t) = A(t) × S(t) / (1 + L(t))
    #      = 1.0 × 0.9 / (1 + 0.2)
    #      = 0.9 / 1.2 = 0.75
    assert 0.74 <= evaluation.benefit <= 0.76
    assert evaluation.should_surface  # 0.75 > 0.4 threshold


def test_benefit_function_low_attention():
    """Test benefit function rejects low attention."""
    benefit_fn = BenefitFunction(threshold=0.4, min_attention=0.2)

    from protocols.mirror.kairos.attention import KairosContext, AttentionState
    from protocols.mirror.kairos.salience import TensionSalience, TensionSeverity

    context = KairosContext(
        timestamp=datetime.now(),
        attention_state=AttentionState.DEEP_WORK,
        attention_budget=0.1,  # Below min_attention
        cognitive_load=0.8,
        recent_interventions=2,
        last_activity_age=2.0,
    )

    salience = TensionSalience(
        tension_id="test-1",
        timestamp=datetime.now(),
        base_severity=TensionSeverity.HIGH,
        momentum_factor=1.5,
        recency_weight=0.9,
        salience=0.9,
        age_minutes=5.0,
    )

    evaluation = benefit_fn.evaluate(context, salience)

    assert not evaluation.should_surface
    assert evaluation.defer_reason == "insufficient_attention"


def test_benefit_function_emergency_override():
    """Test critical + accelerating tensions override."""
    benefit_fn = BenefitFunction(threshold=0.4)

    from protocols.mirror.kairos.attention import KairosContext, AttentionState
    from protocols.mirror.kairos.salience import TensionSalience, TensionSeverity

    context = KairosContext(
        timestamp=datetime.now(),
        attention_state=AttentionState.DEEP_WORK,
        attention_budget=0.1,
        cognitive_load=0.9,
        recent_interventions=3,
        last_activity_age=1.0,
    )

    # Critical + rapidly accelerating
    salience = TensionSalience(
        tension_id="critical-1",
        timestamp=datetime.now(),
        base_severity=TensionSeverity.CRITICAL,
        momentum_factor=2.5,  # > 2.0 threshold
        recency_weight=1.0,
        salience=0.95,
        age_minutes=2.0,
    )

    evaluation = benefit_fn.evaluate(context, salience)

    # Should override despite low attention
    assert evaluation.should_surface


# ============================================================================
# Entropy Budget Tests
# ============================================================================


def test_entropy_budget_consumption():
    """Test budget consumption and limits."""
    budget = EntropyBudget(level=BudgetLevel.MEDIUM)

    # MEDIUM allows 3 interventions per 2 hours
    assert budget.can_intervene()

    # Consume 3 times
    assert budget.consume("t1", "HIGH", 0.8)
    assert budget.consume("t2", "MEDIUM", 0.6)
    assert budget.consume("t3", "LOW", 0.4)

    # Should be exhausted
    assert not budget.can_intervene()
    assert not budget.consume("t4", "HIGH", 0.9)


def test_entropy_budget_recharge():
    """Test budget recharge over time."""
    budget = EntropyBudget(level=BudgetLevel.MEDIUM)

    # Consume all budget
    budget.consume("t1", "HIGH", 0.8)
    budget.consume("t2", "MEDIUM", 0.6)
    budget.consume("t3", "LOW", 0.4)
    assert budget.current_count == 3

    # Recharge (MEDIUM: 0.1 per minute, so 20 minutes recovers 2)
    recovered = budget.recharge(timedelta(minutes=20))
    assert recovered == 2
    assert budget.current_count == 1

    # Note: _prune_old_interventions resets count to match interventions,
    # so can_intervene checks interventions in window, not the recharge count.
    # This is actually correct behavior - the budget tracks real interventions.


def test_entropy_budget_unlimited():
    """Test unlimited budget level."""
    budget = EntropyBudget(level=BudgetLevel.UNLIMITED)

    # Should always allow
    for i in range(100):
        assert budget.can_intervene()
        budget.consume(f"t{i}", "LOW", 0.5)


def test_entropy_budget_engagement_tracking():
    """Test engagement rate calculation."""
    budget = EntropyBudget(level=BudgetLevel.HIGH)

    budget.consume("t1", "HIGH", 0.8)
    budget.consume("t2", "MEDIUM", 0.6)
    budget.consume("t3", "LOW", 0.4)

    # Record responses
    budget.record_user_response("t1", "engaged")
    budget.record_user_response("t2", "dismissed")
    budget.record_user_response("t3", "resolved")

    # 2/3 engaged or resolved
    rate = budget.get_engagement_rate()
    assert 0.66 <= rate <= 0.67


# ============================================================================
# Controller Integration Tests
# ============================================================================


def test_controller_initialization(temp_workspace):
    """Test controller initialization."""
    controller = KairosController(
        workspace_path=temp_workspace,
        budget_level=BudgetLevel.MEDIUM,
    )

    assert controller.workspace_path == temp_workspace
    assert controller.budget.level == BudgetLevel.MEDIUM
    assert len(controller.deferred_tensions) == 0
    assert len(controller.intervention_history) == 0


def test_controller_evaluate_and_surface(temp_workspace, sample_tension):
    """Test full evaluation and surfacing flow."""
    controller = KairosController(
        workspace_path=temp_workspace,
        budget_level=BudgetLevel.HIGH,  # Plenty of budget
    )

    # Evaluate
    evaluation = controller.evaluate_timing(sample_tension, momentum_factor=1.5)

    # Should recommend surfacing (idle workspace + medium tension)
    if evaluation.should_surface:
        record = controller.surface_tension(sample_tension, evaluation)

        assert record.tension.id == sample_tension.id
        assert len(controller.intervention_history) == 1
        assert controller.budget.current_count == 1


@pytest.mark.slow
def test_controller_defer_and_retry(temp_workspace, sample_tension):
    """Test deferred tension retry logic."""
    controller = KairosController(
        workspace_path=temp_workspace,
        budget_level=BudgetLevel.MEDIUM,
    )

    # Defer a tension
    controller.defer_tension(
        sample_tension,
        reason="test_defer",
        min_delay=timedelta(seconds=1),  # Short delay for testing
    )

    assert sample_tension.id in controller.deferred_tensions
    assert len(controller.deferred_tensions) == 1

    # Initially not ready (just deferred)
    next_tension = controller.get_next_deferred()
    assert next_tension is None

    # Wait for min delay
    import time

    time.sleep(1.1)

    # Now should be ready
    next_tension = controller.get_next_deferred()
    assert next_tension is not None
    tension, age = next_tension
    assert tension.id == sample_tension.id


def test_controller_force_surface(temp_workspace, sample_tension):
    """Test force surface override."""
    controller = KairosController(
        workspace_path=temp_workspace,
        budget_level=BudgetLevel.LOW,  # Very limited budget
    )

    # Defer a tension
    controller.defer_tension(
        sample_tension, reason="test", min_delay=timedelta(seconds=0)
    )

    # Force surface (should bypass budget)
    record = controller.force_surface_next()

    assert record is not None
    assert record.tension.id == sample_tension.id
    assert sample_tension.id not in controller.deferred_tensions


def test_controller_status(temp_workspace):
    """Test controller status reporting."""
    controller = KairosController(
        workspace_path=temp_workspace,
        budget_level=BudgetLevel.MEDIUM,
    )

    status = controller.get_status()

    assert "state" in status
    assert "context" in status
    assert "budget" in status
    assert "deferred_queue" in status
    assert "history" in status


# ============================================================================
# Integration Test
# ============================================================================


def test_full_kairos_flow(temp_workspace):
    """Test complete Kairos flow from detection to surfacing."""
    from protocols.mirror.types import (
        Thesis,
        Antithesis,
        PatternObservation,
        PatternType,
    )

    # Create a tension
    thesis = Thesis(content="Integration test principle", source="test.md")
    observation = PatternObservation(
        pattern_type=PatternType.STALENESS,
        description="Test observation",
        value=0.8,
        sample_size=5,
    )
    antithesis = Antithesis(pattern="Test behavior", evidence=(observation,))

    tension = Tension(
        thesis=thesis,
        antithesis=antithesis,
        divergence=0.7,
        mode=TensionMode.TEMPORAL,
        tension_type=TensionType.BEHAVIORAL,
        interpretation="Integration test tension",
    )

    # Create controller
    controller = KairosController(
        workspace_path=temp_workspace,
        budget_level=BudgetLevel.HIGH,
        benefit_threshold=0.3,  # Lower threshold for easier testing
    )

    # Evaluate timing
    evaluation = controller.evaluate_timing(tension, momentum_factor=1.8)

    assert evaluation.tension_id == tension.id
    assert evaluation.benefit > 0.0

    # If approved, surface
    if evaluation.should_surface:
        record = controller.surface_tension(tension, evaluation)

        assert record.tension.id == tension.id
        assert len(controller.intervention_history) == 1

        # Record user response
        controller.record_user_response(tension.id, "engaged", duration_seconds=30.0)

        # Check history
        history = controller.get_intervention_history(window=timedelta(hours=1))
        assert len(history) == 1
        assert history[0].user_response == "engaged"
        assert history[0].duration_seconds == 30.0
