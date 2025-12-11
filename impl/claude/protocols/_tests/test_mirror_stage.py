"""
Tests for Mirror Stage Protocol.

Phase 4.1: Lacanian self-healing via identity reconstruction.

Tests:
- Diagnosis from telemetry
- Interpretation via metaphor
- Synthesis into ego ideal
- Healing plan generation
"""

import pytest
from protocols.mirror_stage import (
    EgoIdeal,
    HealingAction,
    HealingPlan,
    SystemCondition,
    create_mirror_stage,
    create_telemetry,
)


class TestSystemTelemetry:
    """Tests for SystemTelemetry."""

    def test_telemetry_creation(self):
        """Test basic telemetry creation."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=8,
            error_rate=0.1,
        )

        assert telemetry.agent_count == 10
        assert telemetry.active_agents == 8
        assert telemetry.error_rate == 0.1

    def test_is_fragmented_high_error_rate(self):
        """Test fragmentation detection from high error rate."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=8,
            error_rate=0.4,  # > 0.3 threshold
        )

        assert telemetry.is_fragmented

    def test_is_fragmented_inactive_agents(self):
        """Test fragmentation detection from inactive agents."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,  # Only 30% active (< 50%)
            error_rate=0.1,
        )

        assert telemetry.is_fragmented

    def test_not_fragmented_healthy(self):
        """Test healthy system is not fragmented."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=8,
            error_rate=0.1,
        )

        assert not telemetry.is_fragmented

    def test_is_conflicted_blocked_messages(self):
        """Test conflict detection from blocked messages."""
        telemetry = create_telemetry(
            blocked_messages=10,  # > 5 threshold
        )

        assert telemetry.is_conflicted

    def test_is_conflicted_entropy_events(self):
        """Test conflict detection from entropy events."""
        telemetry = create_telemetry(
            entropy_events=5,  # > 3 threshold
        )

        assert telemetry.is_conflicted

    def test_not_conflicted_healthy(self):
        """Test healthy system is not conflicted."""
        telemetry = create_telemetry(
            blocked_messages=2,
            entropy_events=1,
        )

        assert not telemetry.is_conflicted

    def test_is_stressed(self):
        """Test stress detection from resource pressure."""
        telemetry = create_telemetry(
            memory_pressure=0.9,  # > 0.8 threshold
        )

        assert telemetry.is_stressed

        telemetry2 = create_telemetry(
            token_utilization=0.95,  # > 0.9 threshold
        )

        assert telemetry2.is_stressed

    def test_fragmentation_score(self):
        """Test fragmentation score calculation."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=5,  # 50% inactive
            error_rate=0.2,
        )

        # (0.5 inactive ratio + 0.2 error rate) / 2 = 0.35
        assert telemetry.fragmentation_score == pytest.approx(0.35)

    def test_conflict_score(self):
        """Test conflict score calculation."""
        telemetry = create_telemetry(
            blocked_messages=5,  # 0.5 factor
            entropy_events=2,  # 0.4 factor
        )

        # (0.5 + 0.4) / 2 = 0.45
        assert telemetry.conflict_score == pytest.approx(0.45)


class TestDiagnosis:
    """Tests for MirrorStage.diagnose()."""

    @pytest.fixture
    def mirror(self):
        return create_mirror_stage()

    @pytest.mark.asyncio
    async def test_diagnose_coherent(self, mirror):
        """Test diagnosis of healthy system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=9,
            error_rate=0.05,
            blocked_messages=0,
            entropy_events=0,
        )

        state = await mirror.diagnose(telemetry)

        assert state.primary_condition == SystemCondition.COHERENT
        assert len(state.secondary_conditions) == 0
        assert state.severity == 0.0

    @pytest.mark.asyncio
    async def test_diagnose_fragmentation(self, mirror):
        """Test diagnosis of fragmented system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,
            error_rate=0.35,
        )

        state = await mirror.diagnose(telemetry)

        assert state.primary_condition == SystemCondition.FRAGMENTATION

    @pytest.mark.asyncio
    async def test_diagnose_conflict(self, mirror):
        """Test diagnosis of conflicted system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=9,
            blocked_messages=10,
            entropy_events=5,
        )

        state = await mirror.diagnose(telemetry)

        assert state.primary_condition == SystemCondition.CONFLICT

    @pytest.mark.asyncio
    async def test_diagnose_multiple_conditions(self, mirror):
        """Test diagnosis with multiple conditions."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,  # Fragmentation
            error_rate=0.4,  # More fragmentation
            blocked_messages=10,  # Conflict
            entropy_events=5,  # More conflict
            memory_pressure=0.9,  # Stress/Alienation
        )

        state = await mirror.diagnose(telemetry)

        # Primary is first detected
        assert state.primary_condition == SystemCondition.FRAGMENTATION
        # Others are secondary
        assert SystemCondition.CONFLICT in state.secondary_conditions
        assert SystemCondition.ALIENATION in state.secondary_conditions


class TestInterpretation:
    """Tests for MirrorStage.interpret()."""

    @pytest.fixture
    def mirror(self):
        return create_mirror_stage()

    @pytest.mark.asyncio
    async def test_interpret_fragmentation(self, mirror):
        """Test interpretation of fragmentation."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,
            error_rate=0.4,
        )

        state = await mirror.diagnose(telemetry)
        interpretation = await mirror.interpret(state)

        assert interpretation.condition == SystemCondition.FRAGMENTATION
        assert "Corps Morcelé" in interpretation.metaphor_name
        assert interpretation.severity > 0

    @pytest.mark.asyncio
    async def test_interpret_conflict_dialectic_impasse(self, mirror):
        """Test interpretation selects dialectic impasse for blocked messages."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=9,
            blocked_messages=10,
        )

        state = await mirror.diagnose(telemetry)
        interpretation = await mirror.interpret(state)

        assert interpretation.condition == SystemCondition.CONFLICT
        assert "Dialectic Impasse" in interpretation.metaphor_name

    @pytest.mark.asyncio
    async def test_interpret_coherent(self, mirror):
        """Test interpretation of coherent system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=9,
            error_rate=0.05,
        )

        state = await mirror.diagnose(telemetry)
        interpretation = await mirror.interpret(state)

        assert interpretation.condition == SystemCondition.COHERENT
        assert "Integrated" in interpretation.metaphor_name

    @pytest.mark.asyncio
    async def test_interpretation_has_opposites(self, mirror):
        """Test interpretation includes implied opposite for dialectic."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,
            error_rate=0.3,
        )

        state = await mirror.diagnose(telemetry)
        interpretation = await mirror.interpret(state)

        assert interpretation.current_meaning
        assert interpretation.implied_opposite
        assert interpretation.suggested_approach


class TestSynthesis:
    """Tests for MirrorStage.synthesize()."""

    @pytest.fixture
    def mirror(self):
        return create_mirror_stage()

    @pytest.mark.asyncio
    async def test_synthesize_produces_ideal(self, mirror):
        """Test synthesis produces an ego ideal."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=5,
            error_rate=0.3,
        )

        state = await mirror.diagnose(telemetry)
        interpretation = await mirror.interpret(state)
        ideal = await mirror.synthesize(state, interpretation)

        assert isinstance(ideal, EgoIdeal)
        assert ideal.target_condition == SystemCondition.COHERENT
        assert ideal.description

    @pytest.mark.asyncio
    async def test_synthesize_has_preserve_negate_elevate(self, mirror):
        """Test synthesis includes Hegelian sublation components for fragmented system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,  # Fragmented - low active ratio
            error_rate=0.4,  # High error rate
            message_throughput=100,  # Something to preserve
        )

        state = await mirror.diagnose(telemetry)
        interpretation = await mirror.interpret(state)
        ideal = await mirror.synthesize(state, interpretation)

        # Should have things to preserve (working parts)
        assert len(ideal.preserve) > 0
        # Should have things to negate (problems)
        assert len(ideal.negate) > 0
        # Should have things to elevate (transcend) - fragmentation triggers elevate
        assert len(ideal.elevate) > 0

    @pytest.mark.asyncio
    async def test_synthesize_target_metrics(self, mirror):
        """Test synthesis includes target metrics."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=5,
            error_rate=0.4,
        )

        state = await mirror.diagnose(telemetry)
        interpretation = await mirror.interpret(state)
        ideal = await mirror.synthesize(state, interpretation)

        # Should have concrete metric targets
        assert "error_rate" in ideal.metrics
        assert ideal.metrics["error_rate"] < 0.4  # Better than current


class TestHealingPlan:
    """Tests for full healing plan generation."""

    @pytest.fixture
    def mirror(self):
        return create_mirror_stage()

    @pytest.mark.asyncio
    async def test_heal_fragmented_system(self, mirror):
        """Test healing plan for fragmented system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,
            error_rate=0.4,
        )

        plan = await mirror.heal(telemetry)

        assert isinstance(plan, HealingPlan)
        assert plan.diagnosis.primary_condition == SystemCondition.FRAGMENTATION
        assert len(plan.steps) > 0

        # Should include RECONNECT action
        actions = [s.action for s in plan.steps]
        assert HealingAction.RECONNECT in actions

    @pytest.mark.asyncio
    async def test_heal_conflicted_system(self, mirror):
        """Test healing plan for conflicted system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=9,
            blocked_messages=10,
        )

        plan = await mirror.heal(telemetry)

        assert plan.diagnosis.primary_condition == SystemCondition.CONFLICT

        # Should include SYNTHESIZE action
        actions = [s.action for s in plan.steps]
        assert HealingAction.SYNTHESIZE in actions

    @pytest.mark.asyncio
    async def test_heal_healthy_system(self, mirror):
        """Test healing plan for healthy system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=9,
            error_rate=0.05,
        )

        plan = await mirror.heal(telemetry)

        assert plan.diagnosis.primary_condition == SystemCondition.COHERENT

        # Should include MAINTAIN action
        actions = [s.action for s in plan.steps]
        assert HealingAction.MAINTAIN in actions

    @pytest.mark.asyncio
    async def test_healing_steps_have_criteria(self, mirror):
        """Test healing steps include success criteria."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,
            error_rate=0.4,
        )

        plan = await mirror.heal(telemetry)

        for step in plan.steps:
            assert step.success_criteria

    @pytest.mark.asyncio
    async def test_healing_steps_prioritized(self, mirror):
        """Test healing steps are prioritized."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,
            error_rate=0.4,
        )

        plan = await mirror.heal(telemetry)

        priorities = [s.priority for s in plan.steps]
        assert priorities == sorted(priorities)  # Ascending order

    @pytest.mark.asyncio
    async def test_healing_history(self, mirror):
        """Test healing history is tracked."""
        telemetry1 = create_telemetry(agent_count=10, active_agents=3)
        telemetry2 = create_telemetry(agent_count=10, active_agents=8)

        await mirror.heal(telemetry1)
        await mirror.heal(telemetry2)

        assert len(mirror.history) == 2


class TestEstimatedImprovement:
    """Tests for estimated improvement calculation."""

    @pytest.fixture
    def mirror(self):
        return create_mirror_stage()

    @pytest.mark.asyncio
    async def test_improvement_positive_for_issues(self, mirror):
        """Test positive improvement estimated for issues."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=3,
            error_rate=0.4,
        )

        plan = await mirror.heal(telemetry)

        assert plan.estimated_improvement > 0

    @pytest.mark.asyncio
    async def test_no_improvement_for_healthy(self, mirror):
        """Test no improvement needed for healthy system."""
        telemetry = create_telemetry(
            agent_count=10,
            active_agents=9,
            error_rate=0.05,
        )

        plan = await mirror.heal(telemetry)

        assert plan.estimated_improvement == 0.0


class TestIntegration:
    """Integration tests for full Mirror Stage flow."""

    @pytest.mark.asyncio
    async def test_full_healing_flow(self):
        """Test complete healing flow from telemetry to plan."""
        mirror = create_mirror_stage()

        # Simulate a fragmented, conflicted system
        telemetry = create_telemetry(
            agent_count=15,
            active_agents=5,
            error_rate=0.35,
            blocked_messages=8,
            entropy_events=4,
            memory_pressure=0.7,
            token_utilization=0.8,
        )

        plan = await mirror.heal(telemetry)

        # Verify complete plan
        assert plan.diagnosis is not None
        assert plan.interpretation is not None
        assert plan.ideal is not None
        assert len(plan.steps) > 0

        # Verify interpretation connects diagnosis to ideal
        assert plan.interpretation.condition == plan.diagnosis.primary_condition
        assert plan.ideal.target_condition == SystemCondition.COHERENT

        # Verify steps address the diagnosis
        step_descriptions = " ".join(s.description for s in plan.steps)
        assert len(step_descriptions) > 0

    @pytest.mark.asyncio
    async def test_repeated_healing(self):
        """Test multiple healing cycles (simulating improvement)."""
        mirror = create_mirror_stage()

        # Initial bad state
        telemetry1 = create_telemetry(
            agent_count=10,
            active_agents=3,
            error_rate=0.5,
        )

        plan1 = await mirror.heal(telemetry1)
        assert plan1.diagnosis.primary_condition == SystemCondition.FRAGMENTATION

        # Improved state
        telemetry2 = create_telemetry(
            agent_count=10,
            active_agents=7,
            error_rate=0.2,
        )

        plan2 = await mirror.heal(telemetry2)

        # Should still have issues but less severe
        if plan2.diagnosis.primary_condition != SystemCondition.COHERENT:
            assert plan2.diagnosis.severity < plan1.diagnosis.severity

        # Finally healthy
        telemetry3 = create_telemetry(
            agent_count=10,
            active_agents=9,
            error_rate=0.05,
        )

        plan3 = await mirror.heal(telemetry3)
        assert plan3.diagnosis.primary_condition == SystemCondition.COHERENT
