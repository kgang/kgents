"""
Tests for B-gent Phase 4: Value of Information (VoI) Economics

Tests for:
- EpistemicCapital (knowledge currency)
- VoILedger (observation economics tracking)
- VoIOptimizer (observation budget allocation)
- AdaptiveObserver (dynamic observation frequency)
- UnifiedValueAccounting (UVP + VoI integration)
"""

from __future__ import annotations

from datetime import timedelta

import pytest

from ..metered_functor import Gas
from ..value_ledger import SimpleOutput, ValueLedger
from ..voi_economics import (
    # Constants
    ALERT_FATIGUE_COST,
    CONFIRMATION_VALUE,
    EpistemicCapital,
    FindingType,
    InterventionOutcome,
    # Types
    ObservationDepth,
    ObservationFinding,
    SystemHealthReport,
    UnifiedValueAccounting,
    create_adaptive_observer,
    create_unified_accounting,
    # Convenience functions
    create_voi_ledger,
    create_voi_optimizer,
)

# =============================================================================
# ObservationDepth and FindingType Tests
# =============================================================================


class TestObservationDepth:
    """Tests for ObservationDepth enum."""

    def test_depth_levels(self) -> None:
        """Test all depth levels exist."""
        assert ObservationDepth.TELEMETRY_ONLY.value == "telemetry_only"
        assert ObservationDepth.SEMANTIC_SPOT.value == "semantic_spot"
        assert ObservationDepth.SEMANTIC_FULL.value == "semantic_full"
        assert ObservationDepth.AXIOLOGICAL.value == "axiological"

    def test_depth_ordering(self) -> None:
        """Test depths can be compared."""
        depths = list(ObservationDepth)
        assert len(depths) == 4


class TestFindingType:
    """Tests for FindingType enum."""

    def test_finding_types(self) -> None:
        """Test all finding types exist."""
        assert FindingType.ANOMALY_DETECTED.value == "anomaly_detected"
        assert FindingType.HEALTH_CONFIRMED.value == "health_confirmed"
        assert FindingType.FALSE_POSITIVE.value == "false_positive"
        assert FindingType.INCONCLUSIVE.value == "inconclusive"


class TestObservationFinding:
    """Tests for ObservationFinding."""

    def test_creation(self) -> None:
        """Test basic creation."""
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=0.9,
            anomaly="Memory leak detected",
        )
        assert finding.type == FindingType.ANOMALY_DETECTED
        assert finding.confidence == 0.9
        assert finding.anomaly == "Memory leak detected"

    def test_default_values(self) -> None:
        """Test default values."""
        finding = ObservationFinding(type=FindingType.HEALTH_CONFIRMED)
        assert finding.confidence == 0.5
        assert finding.anomaly is None
        assert finding.details == {}


# =============================================================================
# EpistemicCapital Tests
# =============================================================================


class TestEpistemicCapital:
    """Tests for EpistemicCapital."""

    def test_creation(self) -> None:
        """Test basic creation."""
        capital = EpistemicCapital()
        assert capital.observations == 0
        assert capital.anomalies_detected == 0
        assert capital.disasters_prevented == 0.0
        assert capital.false_positives == 0

    def test_net_epistemic_value(self) -> None:
        """Test net value calculation."""
        capital = EpistemicCapital(
            anomalies_detected=5,
            disasters_prevented=100.0,
            confirmations=10,
            false_positives=2,
        )
        # 100 + 10*0.1 - 2*0.5 = 100 + 1 - 1 = 100
        expected = 100.0 + 10 * CONFIRMATION_VALUE - 2 * ALERT_FATIGUE_COST
        assert capital.net_epistemic_value == expected

    def test_signal_to_noise_ratio(self) -> None:
        """Test signal to noise calculation."""
        capital = EpistemicCapital(
            anomalies_detected=8,
            confirmations=12,
            false_positives=4,
        )
        # (8 + 12) / 4 = 5.0
        assert capital.signal_to_noise_ratio == 5.0

    def test_signal_to_noise_no_false_positives(self) -> None:
        """Test SNR with no false positives."""
        capital = EpistemicCapital(
            anomalies_detected=5,
            confirmations=5,
            false_positives=0,
        )
        assert capital.signal_to_noise_ratio == float("inf")

    def test_rovi(self) -> None:
        """Test RoVI calculation."""
        capital = EpistemicCapital(
            total_voi_generated=10.0,
            total_gas_consumed=5.0,
        )
        assert capital.rovi == 2.0

    def test_rovi_zero_gas(self) -> None:
        """Test RoVI with zero gas."""
        capital = EpistemicCapital(
            total_voi_generated=10.0,
            total_gas_consumed=0.0,
        )
        assert capital.rovi == 0.0


# =============================================================================
# VoILedger Tests
# =============================================================================


class TestVoILedger:
    """Tests for VoILedger."""

    def test_creation(self) -> None:
        """Test basic creation."""
        ledger = create_voi_ledger()
        assert ledger.observations == {}
        assert ledger.interventions == []

    def test_creation_with_value_ledger(self) -> None:
        """Test creation with value ledger."""
        value_ledger: ValueLedger = ValueLedger()
        ledger = create_voi_ledger(value_ledger)
        assert ledger.main_ledger is value_ledger

    def test_log_observation_anomaly(self) -> None:
        """Test logging anomaly observation."""
        ledger = create_voi_ledger()
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=0.8,
            anomaly="security_breach",
        )
        gas = Gas(tokens=100)

        receipt = ledger.log_observation(
            observer_id="observer1",
            target_id="agent1",
            gas_consumed=gas,
            finding=finding,
        )

        assert receipt.voi > 0  # Should have positive VoI
        capital = ledger.get_epistemic_capital("observer1")
        assert capital.anomalies_detected == 1
        assert capital.disasters_prevented > 0

    def test_log_observation_health_confirmed(self) -> None:
        """Test logging health confirmation."""
        ledger = create_voi_ledger()
        finding = ObservationFinding(
            type=FindingType.HEALTH_CONFIRMED,
            confidence=0.9,
        )
        gas = Gas(tokens=50)

        receipt = ledger.log_observation(
            observer_id="observer1",
            target_id="agent1",
            gas_consumed=gas,
            finding=finding,
        )

        assert receipt.voi == pytest.approx(CONFIRMATION_VALUE * 0.9)
        capital = ledger.get_epistemic_capital("observer1")
        assert capital.confirmations == 1

    def test_log_observation_false_positive(self) -> None:
        """Test logging false positive."""
        ledger = create_voi_ledger()
        finding = ObservationFinding(type=FindingType.FALSE_POSITIVE)
        gas = Gas(tokens=100)

        receipt = ledger.log_observation(
            observer_id="observer1",
            target_id="agent1",
            gas_consumed=gas,
            finding=finding,
        )

        assert receipt.voi == -ALERT_FATIGUE_COST
        capital = ledger.get_epistemic_capital("observer1")
        assert capital.false_positives == 1

    def test_calculate_voi_security_breach(self) -> None:
        """Test VoI calculation for security breach."""
        ledger = create_voi_ledger()
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=1.0,
            anomaly="security_breach",
        )
        voi = ledger.calculate_voi(finding)
        assert voi == 1000.0  # Full disaster cost

    def test_calculate_voi_partial_confidence(self) -> None:
        """Test VoI calculation with partial confidence."""
        ledger = create_voi_ledger()
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=0.5,
            anomaly="service_outage",
        )
        voi = ledger.calculate_voi(finding)
        assert voi == 100.0  # 200 * 0.5

    def test_disaster_cost_categories(self) -> None:
        """Test disaster cost by category."""
        ledger = create_voi_ledger()

        categories = [
            ("security_breach", 1000.0),
            ("data_corruption", 500.0),
            ("service_outage", 200.0),
            ("performance_degradation", 50.0),
            ("unknown_category", 100.0),  # default
        ]

        for category, expected_cost in categories:
            finding = ObservationFinding(
                type=FindingType.ANOMALY_DETECTED,
                confidence=1.0,
                anomaly=category,
            )
            voi = ledger.calculate_voi(finding)
            assert voi == expected_cost, f"Failed for {category}"

    def test_log_intervention(self) -> None:
        """Test logging intervention."""
        ledger = create_voi_ledger()

        # First log an observation
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=0.8,
            anomaly="service_outage",
        )
        gas = Gas(tokens=100)
        _receipt = ledger.log_observation(
            observer_id="observer1",
            target_id="agent1",
            gas_consumed=gas,
            finding=finding,
        )

        # Then log intervention
        outcome = InterventionOutcome(
            success=True,
            value_saved=250.0,
            description="Prevented full outage",
        )
        ledger.log_intervention(
            observation_id="obs_id",
            action_taken="Restarted service",
            outcome=outcome,
        )

        assert len(ledger.interventions) == 1
        assert ledger.interventions[0].outcome.value_saved == 250.0

    def test_get_observer_rovi(self) -> None:
        """Test RoVI for specific observer."""
        ledger = create_voi_ledger()

        # Log multiple observations
        for i in range(5):
            finding = ObservationFinding(
                type=FindingType.ANOMALY_DETECTED,
                confidence=0.8,
                anomaly="security_breach",
            )
            gas = Gas(tokens=100, model_multiplier=1.0)
            ledger.log_observation(
                observer_id="observer1",
                target_id=f"agent{i}",
                gas_consumed=gas,
                finding=finding,
            )

        rovi = ledger.get_observer_rovi("observer1")
        assert rovi > 0

    def test_get_observer_stats(self) -> None:
        """Test getting observer statistics."""
        ledger = create_voi_ledger()

        # Mix of observations
        findings = [
            (FindingType.ANOMALY_DETECTED, "security_breach"),
            (FindingType.HEALTH_CONFIRMED, None),
            (FindingType.FALSE_POSITIVE, None),
        ]

        for ftype, anomaly in findings:
            finding = ObservationFinding(type=ftype, anomaly=anomaly)
            gas = Gas(tokens=100)
            ledger.log_observation(
                observer_id="observer1",
                target_id="agent1",
                gas_consumed=gas,
                finding=finding,
            )

        stats = ledger.get_observer_stats("observer1")
        assert stats["total_observations"] == 3
        assert stats["anomalies_detected"] == 1
        assert stats["confirmations"] == 1
        assert stats["false_positives"] == 1

    def test_system_rovi(self) -> None:
        """Test system-wide RoVI."""
        ledger = create_voi_ledger()

        # Multiple observers
        for obs_id in ["obs1", "obs2", "obs3"]:
            finding = ObservationFinding(
                type=FindingType.ANOMALY_DETECTED,
                confidence=0.8,
                anomaly="service_outage",
            )
            gas = Gas(tokens=100)
            ledger.log_observation(
                observer_id=obs_id,
                target_id="agent1",
                gas_consumed=gas,
                finding=finding,
            )

        system_rovi = ledger.system_rovi()
        assert system_rovi > 0

    def test_false_positive_rate(self) -> None:
        """Test false positive rate calculation."""
        ledger = create_voi_ledger()

        # 3 true findings, 1 false positive
        for _ in range(3):
            ledger.log_observation(
                observer_id="obs1",
                target_id="agent1",
                gas_consumed=Gas(tokens=50),
                finding=ObservationFinding(type=FindingType.HEALTH_CONFIRMED),
            )

        ledger.log_observation(
            observer_id="obs1",
            target_id="agent1",
            gas_consumed=Gas(tokens=50),
            finding=ObservationFinding(type=FindingType.FALSE_POSITIVE),
        )

        assert ledger.false_positive_rate() == pytest.approx(0.25)


# =============================================================================
# VoIOptimizer Tests
# =============================================================================


class TestVoIOptimizer:
    """Tests for VoIOptimizer."""

    def test_creation(self) -> None:
        """Test basic creation."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)
        assert optimizer.ledger is value_ledger

    def test_record_reliability(self) -> None:
        """Test recording reliability."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        # Record some successes and failures
        optimizer.record_reliability("agent1", True)
        optimizer.record_reliability("agent1", True)
        optimizer.record_reliability("agent1", False)

        reliability = optimizer.get_reliability("agent1")
        assert reliability == pytest.approx(2 / 3)

    def test_reliability_unknown_agent(self) -> None:
        """Test reliability for unknown agent."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        reliability = optimizer.get_reliability("unknown_agent")
        assert reliability == 0.5  # Default

    def test_reliability_history_limit(self) -> None:
        """Test reliability history is limited."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        # Record 150 successes (should be limited to 100)
        for _ in range(150):
            optimizer.record_reliability("agent1", True)

        assert len(optimizer._reliability["agent1"]) == 100

    def test_observability_score(self) -> None:
        """Test observability score."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        optimizer.set_observability("agent1", 0.9)
        assert optimizer.get_observability_score("agent1") == 0.9

    def test_observability_clamped(self) -> None:
        """Test observability is clamped to 0-1."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        optimizer.set_observability("agent1", 1.5)
        assert optimizer.get_observability_score("agent1") == 1.0

        optimizer.set_observability("agent2", -0.5)
        assert optimizer.get_observability_score("agent2") == 0.0

    def test_compute_observation_priority(self) -> None:
        """Test priority computation."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        # Set up agent with known values
        optimizer.record_reliability("agent1", False)  # 0% reliable = 100% risk
        optimizer.set_observability("agent1", 1.0)

        # Log a transaction to give agent impact
        output = SimpleOutput(content="def foo(): pass", _valid_syntax=True)
        gas = Gas(tokens=100)
        value_ledger.log_transaction("agent1", gas, output)

        priority = optimizer.compute_observation_priority("agent1")
        assert priority > 0

    def test_allocate_observation_budget(self) -> None:
        """Test budget allocation."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        # Set different priorities
        optimizer.record_reliability("high_risk", False)  # 0% reliable
        optimizer.record_reliability("low_risk", True)  # 100% reliable
        optimizer.set_observability("high_risk", 0.8)
        optimizer.set_observability("low_risk", 0.8)

        total_budget = Gas(tokens=1000)
        allocations = optimizer.allocate_observation_budget(
            total_budget, ["high_risk", "low_risk"]
        )

        assert "high_risk" in allocations
        assert "low_risk" in allocations
        # High risk should get more budget (higher priority)
        assert allocations["high_risk"].tokens >= allocations["low_risk"].tokens

    def test_allocate_empty_agents(self) -> None:
        """Test allocation with no agents."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        allocations = optimizer.allocate_observation_budget(Gas(tokens=1000), [])
        assert allocations == {}

    def test_select_observation_depth(self) -> None:
        """Test depth selection based on budget."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        # Large budget -> deepest
        depth = optimizer.select_observation_depth("agent1", Gas(tokens=5000))
        assert depth == ObservationDepth.SEMANTIC_FULL

        # Small budget -> shallowest
        depth = optimizer.select_observation_depth("agent1", Gas(tokens=5))
        assert depth == ObservationDepth.TELEMETRY_ONLY

    def test_get_observation_recommendations(self) -> None:
        """Test getting recommendations."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)

        # Set up agents
        for agent in ["agent1", "agent2", "agent3"]:
            optimizer.set_observability(agent, 0.7)

        recs = optimizer.get_observation_recommendations(
            ["agent1", "agent2", "agent3"],
            Gas(tokens=1000),
        )

        assert len(recs) == 3
        # Should be sorted by priority
        for rec in recs:
            assert "agent_id" in rec
            assert "priority" in rec
            assert "budget_tokens" in rec
            assert "recommended_depth" in rec


# =============================================================================
# AdaptiveObserver Tests
# =============================================================================


class TestAdaptiveObserver:
    """Tests for AdaptiveObserver."""

    def test_creation(self) -> None:
        """Test basic creation."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)
        observer = create_adaptive_observer(optimizer)

        assert observer.base_interval == timedelta(seconds=60)
        assert observer.min_interval == timedelta(seconds=5)
        assert observer.max_interval == timedelta(seconds=600)

    def test_compute_observation_interval_high_priority(self) -> None:
        """Test interval for high priority agent."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)
        observer = create_adaptive_observer(optimizer)

        # Set up high-risk agent
        optimizer.record_reliability("agent1", False)
        optimizer.set_observability("agent1", 1.0)

        # Log transaction for impact
        output = SimpleOutput(content="def foo(): pass" * 10, _valid_syntax=True)
        value_ledger.log_transaction("agent1", Gas(tokens=100), output)

        interval = observer.compute_observation_interval("agent1")
        # High priority should get short interval
        assert interval <= observer.base_interval

    def test_compute_observation_interval_low_priority(self) -> None:
        """Test interval for low priority agent."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)
        observer = create_adaptive_observer(optimizer)

        # Set up low-risk agent (all successes)
        for _ in range(10):
            optimizer.record_reliability("agent1", True)
        optimizer.set_observability("agent1", 0.1)  # Low observability

        interval = observer.compute_observation_interval("agent1")
        # Low priority should get longer interval
        assert interval >= observer.base_interval

    def test_should_observe(self) -> None:
        """Test should_observe check."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)
        observer = create_adaptive_observer(
            optimizer,
            base_interval_seconds=60.0,
        )

        # Never observed -> should observe
        assert observer.should_observe("agent1")

        # Just observed -> should not observe yet
        observer.mark_observed("agent1")
        assert not observer.should_observe("agent1")

    def test_register_and_observe(self) -> None:
        """Test registering observer function."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)
        observer = create_adaptive_observer(optimizer)

        observed = []

        def my_observer(agent_id: str) -> str:
            observed.append(agent_id)
            return f"Observed {agent_id}"

        observer.register_observer("agent1", my_observer)

        # Manually trigger observation
        import asyncio

        result = asyncio.run(observer.observe("agent1"))

        assert result == "Observed agent1"
        assert "agent1" in observed

    def test_get_observation_schedule(self) -> None:
        """Test getting observation schedule."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)
        observer = create_adaptive_observer(optimizer)

        agents = ["agent1", "agent2", "agent3"]
        schedule = observer.get_observation_schedule(agents)

        assert len(schedule) == 3
        for entry in schedule:
            assert "agent_id" in entry
            assert "interval_seconds" in entry
            assert "last_observed" in entry
            assert "seconds_until_next" in entry


# =============================================================================
# UnifiedValueAccounting Tests
# =============================================================================


class TestUnifiedValueAccounting:
    """Tests for UnifiedValueAccounting."""

    def test_creation(self) -> None:
        """Test basic creation."""
        value_ledger: ValueLedger = ValueLedger()
        accounting = create_unified_accounting(value_ledger)
        assert accounting.value is value_ledger

    def test_system_health_empty(self) -> None:
        """Test system health with no data."""
        value_ledger: ValueLedger = ValueLedger()
        accounting = create_unified_accounting(value_ledger)

        health = accounting.system_health()
        assert isinstance(health, SystemHealthReport)
        assert health.production_roc == 0.0
        assert health.observation_rovi == 0.0

    def test_system_health_healthy(self) -> None:
        """Test healthy system status."""
        value_ledger: ValueLedger = ValueLedger()
        voi_ledger = create_voi_ledger(value_ledger)
        accounting = UnifiedValueAccounting(value_ledger, voi_ledger)

        # Log profitable production
        output = SimpleOutput(
            content="def foo(): pass" * 20,
            _valid_syntax=True,
            _tests_passed=True,
        )
        gas = Gas(tokens=10)  # Low cost, high value
        value_ledger.log_transaction("prod_agent", gas, output)

        # Log valuable observation
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=1.0,
            anomaly="security_breach",
        )
        voi_ledger.log_observation(
            observer_id="obs_agent",
            target_id="prod_agent",
            gas_consumed=Gas(tokens=10),
            finding=finding,
        )

        health = accounting.system_health()
        # Should be healthy
        assert health.production_roc > 0
        assert health.observation_rovi > 0

    def test_generate_recommendations_low_roc(self) -> None:
        """Test recommendations for low RoC."""
        value_ledger: ValueLedger = ValueLedger()
        accounting = create_unified_accounting(value_ledger)

        # Log unprofitable production
        output = SimpleOutput(content="x", _valid_syntax=False)
        gas = Gas(tokens=10000, model_multiplier=15.0)  # High cost
        value_ledger.log_transaction("agent1", gas, output)

        health = accounting.system_health()
        assert any("Production RoC" in rec for rec in health.recommendations)

    def test_generate_recommendations_high_false_positives(self) -> None:
        """Test recommendations for high false positive rate."""
        value_ledger: ValueLedger = ValueLedger()
        voi_ledger = create_voi_ledger(value_ledger)
        accounting = UnifiedValueAccounting(value_ledger, voi_ledger)

        # Log many false positives
        for _ in range(10):
            voi_ledger.log_observation(
                observer_id="obs1",
                target_id="agent1",
                gas_consumed=Gas(tokens=50),
                finding=ObservationFinding(type=FindingType.FALSE_POSITIVE),
            )

        health = accounting.system_health()
        assert any("False positive" in rec for rec in health.recommendations)

    def test_get_currency_summary(self) -> None:
        """Test getting currency summary."""
        value_ledger: ValueLedger = ValueLedger()
        voi_ledger = create_voi_ledger(value_ledger)
        accounting = UnifiedValueAccounting(value_ledger, voi_ledger)

        # Add some production
        output = SimpleOutput(content="def foo(): pass", _valid_syntax=True)
        value_ledger.log_transaction("agent1", Gas(tokens=100), output)

        # Add some observation
        finding = ObservationFinding(type=FindingType.HEALTH_CONFIRMED)
        voi_ledger.log_observation(
            observer_id="obs1",
            target_id="agent1",
            gas_consumed=Gas(tokens=50),
            finding=finding,
        )

        summary = accounting.get_currency_summary()

        assert "gas" in summary
        assert "impact" in summary
        assert "epistemic_capital" in summary
        assert "efficiency" in summary

        assert summary["gas"]["production"] > 0
        assert summary["gas"]["observation"] > 0


# =============================================================================
# Integration Tests
# =============================================================================


class TestVoIIntegration:
    """Integration tests for VoI economics system."""

    def test_full_observation_workflow(self) -> None:
        """Test complete observation workflow."""
        # Set up ledgers
        value_ledger: ValueLedger = ValueLedger()
        voi_ledger = create_voi_ledger(value_ledger)

        # Set up optimizer
        optimizer = create_voi_optimizer(value_ledger, voi_ledger)

        # Log production to give agents impact
        output = SimpleOutput(
            content="def process_data(): return transform(input())" * 10,
            _valid_syntax=True,
            _tests_passed=True,
        )
        value_ledger.log_transaction("data_processor", Gas(tokens=500), output)

        # Set up reliability
        optimizer.record_reliability("data_processor", True)
        optimizer.record_reliability("data_processor", True)
        optimizer.record_reliability("data_processor", False)  # One failure
        optimizer.set_observability("data_processor", 0.9)

        # Allocate observation budget
        allocations = optimizer.allocate_observation_budget(
            Gas(tokens=1000), ["data_processor"]
        )

        # Perform observation
        depth = optimizer.select_observation_depth(
            "data_processor", allocations["data_processor"]
        )

        # Log observation finding
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=0.85,
            anomaly="performance_degradation",
        )
        receipt = voi_ledger.log_observation(
            observer_id="perf_monitor",
            target_id="data_processor",
            gas_consumed=allocations["data_processor"],
            finding=finding,
            depth=depth,
        )

        # Verify receipt
        assert receipt.voi > 0
        assert receipt.cumulative_epistemic_capital.anomalies_detected == 1

        # Log intervention
        outcome = InterventionOutcome(
            success=True,
            value_saved=75.0,
            description="Optimized slow query",
        )
        voi_ledger.log_intervention(
            observation_id="perf_monitor_obs",
            action_taken="Optimized query",
            outcome=outcome,
        )

        # Check unified accounting
        accounting = UnifiedValueAccounting(value_ledger, voi_ledger)
        health = accounting.system_health()

        assert health.production_roc > 0
        assert health.observation_rovi > 0

    def test_adaptive_observation_schedule(self) -> None:
        """Test adaptive observation scheduling."""
        value_ledger: ValueLedger = ValueLedger()
        optimizer = create_voi_optimizer(value_ledger)
        observer = create_adaptive_observer(
            optimizer,
            base_interval_seconds=60.0,
            min_interval_seconds=5.0,
            max_interval_seconds=300.0,
        )

        # Set up agents with different risk profiles
        agents = ["high_risk", "medium_risk", "low_risk"]

        # High risk: many failures
        for _ in range(8):
            optimizer.record_reliability("high_risk", False)
        for _ in range(2):
            optimizer.record_reliability("high_risk", True)
        optimizer.set_observability("high_risk", 0.9)

        # Medium risk: mixed
        for _ in range(5):
            optimizer.record_reliability("medium_risk", True)
        for _ in range(5):
            optimizer.record_reliability("medium_risk", False)
        optimizer.set_observability("medium_risk", 0.7)

        # Low risk: mostly success
        for _ in range(9):
            optimizer.record_reliability("low_risk", True)
        optimizer.record_reliability("low_risk", False)
        optimizer.set_observability("low_risk", 0.5)

        # Get schedule
        schedule = observer.get_observation_schedule(agents)

        # Verify intervals make sense
        intervals = {entry["agent_id"]: entry["interval_seconds"] for entry in schedule}

        # High risk should have shortest interval
        # But we're checking relative intervals, not absolute
        # Since low_risk has high reliability, it should have longer interval
        assert intervals["high_risk"] <= intervals["medium_risk"]
        assert intervals["medium_risk"] <= intervals["low_risk"]

    def test_voi_anti_patterns_detection(self) -> None:
        """Test detection of VoI anti-patterns."""
        value_ledger: ValueLedger = ValueLedger()
        voi_ledger = create_voi_ledger(value_ledger)
        _accounting = UnifiedValueAccounting(value_ledger, voi_ledger)

        # Pattern: The Paranoid Observer (too many observations, high gas)
        # Each observation costs significant gas but only confirms health
        for i in range(100):
            finding = ObservationFinding(
                type=FindingType.HEALTH_CONFIRMED,
                confidence=0.5,
            )
            # High gas cost relative to VoI: 500 tokens * 15x multiplier = high cost
            # VoI from confirmation is only 0.05 (0.1 * 0.5)
            voi_ledger.log_observation(
                observer_id="paranoid",
                target_id=f"agent{i}",
                gas_consumed=Gas(tokens=500, model_multiplier=15.0),  # Expensive model
                finding=finding,
            )

        # Check that RoVI is low due to over-observation
        rovi = voi_ledger.get_observer_rovi("paranoid")
        # Confirmation only gives 0.05 value (0.1 * 0.5) per observation
        # Gas cost is 500 * 15.0 * 0.00001 = 0.075 USD per observation
        # So RoVI should be around 0.05 / 0.075 = 0.67
        assert rovi < 1.0  # Not profitable

    def test_epistemic_capital_accumulation(self) -> None:
        """Test epistemic capital accumulates correctly."""
        voi_ledger = create_voi_ledger()

        # Mix of findings
        test_cases = [
            (FindingType.ANOMALY_DETECTED, "security_breach", 1000.0),
            (FindingType.HEALTH_CONFIRMED, None, CONFIRMATION_VALUE),
            (FindingType.FALSE_POSITIVE, None, -ALERT_FATIGUE_COST),
            (FindingType.ANOMALY_DETECTED, "service_outage", 200.0),
        ]

        expected_voi = 0.0
        for ftype, anomaly, base_voi in test_cases:
            finding = ObservationFinding(
                type=ftype,
                confidence=1.0,
                anomaly=anomaly,
            )
            voi_ledger.log_observation(
                observer_id="obs1",
                target_id="agent1",
                gas_consumed=Gas(tokens=100),
                finding=finding,
            )
            if ftype != FindingType.FALSE_POSITIVE:
                expected_voi += base_voi
            else:
                expected_voi += base_voi  # Negative

        capital = voi_ledger.get_epistemic_capital("obs1")

        assert capital.observations == 4
        assert capital.anomalies_detected == 2
        assert capital.confirmations == 1
        assert capital.false_positives == 1
        assert capital.total_voi_generated == pytest.approx(expected_voi)
