"""
Cross-Agent Integration Tests: Observation Stack

Tests integration across the observation domain:
- O × W: O-gent observations → W-gent wire protocol emission
- O × I: O-gent observations → I-gent dashboard display
- O × B: O-gent VoI-aware observation (B-gent economics)
- O × N: O-gent observations → N-gent narrative

Philosophy:
    Observation is the epistemic substrate - it enables self-knowledge.
    The observation stack makes invisible computation visible.
"""

import asyncio
from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

# B-gent imports
from agents.b import (
    FindingType,
    Gas,
    ObservationDepth,
    ObservationFinding,
    VoILedger,
)

# I-gent imports
from agents.i import (
    Color,
    Meter,
    colorize,
)

# N-gent imports
from agents.n import (
    Historian,
    MemoryCrystalStore,
    SemanticTrace,
)

# O-gent imports
from agents.o import (
    # Core observer
    ObservationContext,
    ObservationResult,
    ObservationStatus,
    create_integrated_panopticon,
    render_unified_dashboard,
)
from agents.o.observable_panopticon import (
    EmissionMode,
    ObservablePanopticon,
    WireStatusSnapshot,
    create_observable_panopticon,
    create_panopticon_dashboard,
    create_wire_observer,
)

# W-gent imports
from agents.w import (
    WireObservable,
)

# =============================================================================
# Helper Functions
# =============================================================================


def create_test_trace(
    trace_id: str,
    agent_id: str = "test-agent",
    agent_genus: str = "O",
    action: str = "INVOKE",
    parent_id: str | None = None,
    inputs: dict | None = None,
    outputs: dict | None = None,
) -> SemanticTrace:
    """Create a test SemanticTrace with all required fields."""
    return SemanticTrace(
        trace_id=trace_id,
        parent_id=parent_id,
        timestamp=datetime.now(timezone.utc),
        agent_id=agent_id,
        agent_genus=agent_genus,
        action=action,
        inputs=inputs or {},
        outputs=outputs,
        input_hash="test-hash",
        input_snapshot=b"{}",
        output_hash="output-hash" if outputs else None,
        gas_consumed=100,
        duration_ms=50,
    )


# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def mock_agent():
    """Create a mock agent for observation tests."""
    agent = MagicMock()
    agent.id = "test-agent-001"
    agent.name = "TestAgent"
    return agent


@pytest.fixture
def wire_observable():
    """Create a WireObservable for tests."""
    return WireObservable("test-observable")


@pytest.fixture
def panopticon():
    """Create an IntegratedPanopticon for tests."""
    return create_integrated_panopticon()


@pytest.fixture
def crystal_store():
    """Create a memory crystal store for N-gent tests."""
    return MemoryCrystalStore()


@pytest.fixture
def historian(crystal_store):
    """Create a Historian for N-gent tests."""
    return Historian(crystal_store)


@pytest.fixture
def voi_ledger():
    """Create a VoI ledger."""
    return VoILedger()


# =============================================================================
# O × W Integration: Observations Flow Through Wire Protocol
# =============================================================================


class TestObservationWirePipeline:
    """O × W: Observations flow through wire protocol."""

    def test_observable_panopticon_creation(self) -> None:
        """Test ObservablePanopticon creates successfully."""
        panopticon = create_observable_panopticon()
        assert panopticon is not None
        assert isinstance(panopticon, ObservablePanopticon)
        assert isinstance(panopticon, WireObservable)

    def test_observable_panopticon_collects_snapshot(self, panopticon) -> None:
        """Test ObservablePanopticon collects status snapshots."""
        obs_panopticon = ObservablePanopticon(panopticon=panopticon)
        snapshot = obs_panopticon.collect_snapshot()

        assert isinstance(snapshot, WireStatusSnapshot)
        assert snapshot.system_status in (
            "HOMEOSTATIC",
            "DEGRADED",
            "CRITICAL",
            "UNKNOWN",
        )
        assert snapshot.uptime_seconds >= 0
        assert isinstance(snapshot.telemetry_healthy, bool)
        assert isinstance(snapshot.semantic_healthy, bool)
        assert isinstance(snapshot.economic_healthy, bool)

    def test_snapshot_converts_to_dict(self, panopticon) -> None:
        """Test WireStatusSnapshot serializes for wire protocol."""
        obs_panopticon = ObservablePanopticon(panopticon=panopticon)
        snapshot = obs_panopticon.collect_snapshot()

        wire_dict = snapshot.to_dict()

        assert "timestamp" in wire_dict
        assert "system_status" in wire_dict
        assert "telemetry" in wire_dict
        assert "semantic" in wire_dict
        assert "economic" in wire_dict
        assert "bootstrap" in wire_dict
        assert "alerts" in wire_dict

        # Check nested structure
        assert "healthy" in wire_dict["telemetry"]
        assert "latency_p95" in wire_dict["telemetry"]

    def test_wire_observer_creates_context(self, mock_agent) -> None:
        """Test WireObserver creates observation context."""
        observer = create_wire_observer()
        context = observer.pre_invoke(mock_agent, {"input": "test"})

        assert isinstance(context, ObservationContext)
        assert context.agent_id == "test-agent-001"
        assert context.agent_name == "TestAgent"
        assert "input_preview" in context.metadata

    @pytest.mark.asyncio
    async def test_wire_observer_records_completion(self, mock_agent) -> None:
        """Test WireObserver records observation completion."""
        observer = create_wire_observer()
        context = observer.pre_invoke(mock_agent, {"input": "test"})

        result = await observer.post_invoke(context, {"output": "done"}, 42.5)

        assert isinstance(result, ObservationResult)
        assert result.status == ObservationStatus.COMPLETED
        assert result.duration_ms == 42.5
        assert result.output_data == {"output": "done"}

    def test_wire_observer_records_entropy(self, mock_agent) -> None:
        """Test WireObserver records error events."""
        observer = create_wire_observer()
        context = observer.pre_invoke(mock_agent, {"input": "test"})

        error = ValueError("Test error")
        observer.record_entropy(context, error)

        stats = observer.get_stats()
        assert stats["observations"] == 1
        assert stats["errors"] == 1

    def test_emission_modes(self, panopticon) -> None:
        """Test different emission modes for ObservablePanopticon."""
        for mode in EmissionMode:
            obs_panopticon = ObservablePanopticon(
                panopticon=panopticon, emission_mode=mode
            )
            assert obs_panopticon.emission_mode == mode

    def test_should_emit_continuous_mode(self, panopticon) -> None:
        """Test CONTINUOUS mode always emits."""
        obs_panopticon = ObservablePanopticon(
            panopticon=panopticon, emission_mode=EmissionMode.CONTINUOUS
        )
        snapshot = obs_panopticon.collect_snapshot()
        assert obs_panopticon.should_emit(snapshot) is True

    def test_should_emit_on_change_mode(self, panopticon) -> None:
        """Test ON_CHANGE mode emits only when status changes."""
        obs_panopticon = ObservablePanopticon(
            panopticon=panopticon, emission_mode=EmissionMode.ON_CHANGE
        )

        snapshot1 = obs_panopticon.collect_snapshot()
        assert obs_panopticon.should_emit(snapshot1) is True  # First time

        snapshot2 = obs_panopticon.collect_snapshot()
        # Same status, should not emit
        assert obs_panopticon.should_emit(snapshot2) is False

    def test_wire_metrics_update(self) -> None:
        """Test wire metrics are tracked."""
        obs_panopticon = create_observable_panopticon()

        for _ in range(5):
            snapshot = obs_panopticon.collect_snapshot()
            obs_panopticon.emit_snapshot(snapshot)

        # History should be populated
        assert len(obs_panopticon.get_history()) == 5


# =============================================================================
# O × I Integration: Observations Display on Dashboard
# =============================================================================


class TestObservationDashboardIntegration:
    """O × I: Observations displayed via I-gent components."""

    def test_panopticon_renders_compact(self) -> None:
        """Test Panopticon renders compact status line."""
        dashboard = create_panopticon_dashboard()
        compact = dashboard.render_compact()

        assert "[O]" in compact  # O-gent marker
        assert "Alerts:" in compact

    def test_panopticon_renders_dimensions(self) -> None:
        """Test Panopticon renders dimension panels."""
        dashboard = create_panopticon_dashboard()
        dimensions = dashboard.render_dimensions()

        assert "TELEMETRY" in dimensions
        assert "SEMANTICS" in dimensions
        assert "ECONOMICS" in dimensions
        assert "Latency" in dimensions
        assert "Drift" in dimensions
        assert "RoC" in dimensions

    def test_dashboard_wire_data_format(self) -> None:
        """Test dashboard produces wire-compatible data."""
        dashboard = create_panopticon_dashboard()
        wire_data = dashboard.get_wire_data()

        assert "snapshot" in wire_data
        assert "sparklines" in wire_data
        assert "compact" in wire_data
        assert "dimensions" in wire_data

        # Sparklines structure
        assert "latency" in wire_data["sparklines"]
        assert "roc" in wire_data["sparklines"]
        assert "drift" in wire_data["sparklines"]

    def test_i_gent_meter_for_metrics(self, panopticon) -> None:
        """Test I-gent Meter displays observation metrics."""
        status = panopticon.get_status()

        meter = Meter(
            label="Drift",
            value=status.semantic.drift_score,
            max_value=1.0,
            thresholds=[],
        )
        rendered = meter.render()

        assert "Drift" in rendered

    def test_colorized_health_status(self, panopticon) -> None:
        """Test health status uses appropriate colors."""
        status = panopticon.get_status()

        if status.telemetry.healthy:
            colored = colorize("HEALTHY", Color.GREEN)
            assert "\033[32m" in colored  # Green ANSI code
        else:
            colored = colorize("DEGRADED", Color.YELLOW)
            assert "\033[33m" in colored  # Yellow ANSI code

    def test_unified_dashboard_render(self, panopticon) -> None:
        """Test unified dashboard rendering."""
        status = panopticon.get_status()
        dashboard = render_unified_dashboard(status)

        assert isinstance(dashboard, str)
        assert len(dashboard) > 0


# =============================================================================
# O × B Integration: VoI-Aware Observation
# =============================================================================


class TestObservationEconomicsIntegration:
    """O × B: Observations subject to VoI economics."""

    def test_voi_ledger_creation(self, voi_ledger) -> None:
        """Test VoI ledger creates successfully."""
        assert voi_ledger is not None
        assert isinstance(voi_ledger, VoILedger)

    def test_voi_ledger_records_observation(self, voi_ledger) -> None:
        """Test VoI ledger records observation costs."""
        finding = ObservationFinding(
            type=FindingType.HEALTH_CONFIRMED,
            confidence=0.9,
        )

        receipt = voi_ledger.log_observation(
            observer_id="test-observer",
            target_id="test-target",
            gas_consumed=Gas(10.0),
            finding=finding,
            depth=ObservationDepth.TELEMETRY_ONLY,
        )

        assert receipt is not None
        assert receipt.voi >= 0  # Value of information calculated

    def test_voi_anomaly_detection_value(self, voi_ledger) -> None:
        """Test anomaly detection has high VoI."""
        finding = ObservationFinding(
            type=FindingType.ANOMALY_DETECTED,
            confidence=0.95,
            anomaly="High latency spike detected",
        )

        receipt = voi_ledger.log_observation(
            observer_id="test-observer",
            target_id="test-target",
            gas_consumed=Gas(50.0),
            finding=finding,
            depth=ObservationDepth.SEMANTIC_FULL,
        )

        # Anomalies should have positive VoI
        assert receipt.voi > 0

    def test_epistemic_capital_accumulates(self, voi_ledger) -> None:
        """Test epistemic capital accumulates across observations."""
        # Multiple observations
        for i in range(5):
            finding = ObservationFinding(
                type=FindingType.HEALTH_CONFIRMED,
                confidence=0.8,
            )
            voi_ledger.log_observation(
                observer_id="test-observer",
                target_id=f"target-{i}",
                gas_consumed=Gas(10.0),
                finding=finding,
            )

        capital = voi_ledger.get_epistemic_capital("test-observer")

        assert capital.observations == 5
        assert capital.confirmations == 5

    def test_observation_depth_affects_gas(self, voi_ledger) -> None:
        """Test different depths have different costs."""
        # Gas takes tokens (int), not cost directly
        depths = [
            (ObservationDepth.TELEMETRY_ONLY, 1000),
            (ObservationDepth.SEMANTIC_SPOT, 3000),
            (ObservationDepth.SEMANTIC_FULL, 10000),
        ]

        for depth, gas_tokens in depths:
            finding = ObservationFinding(type=FindingType.HEALTH_CONFIRMED)
            receipt = voi_ledger.log_observation(
                observer_id="test-observer",
                target_id="test-target",
                gas_consumed=Gas(tokens=gas_tokens),
                finding=finding,
                depth=depth,
            )

            # Gas.tokens is the consumed tokens
            assert receipt.observation.gas.tokens == gas_tokens


# =============================================================================
# O × N Integration: Observations Create Narrative
# =============================================================================


class TestObservationNarrativeIntegration:
    """O × N: Observations feed into narrative."""

    def test_historian_records_observation_trace(self, historian) -> None:
        """Test Historian records observation as trace."""
        trace = create_test_trace(
            trace_id="obs-trace-001",
            agent_id="o-gent",
            agent_genus="O",
            action="INVOKE",
            inputs={"observed_agent": "test-agent", "depth": "SHALLOW"},
            outputs={"status": "COMPLETED", "findings": ["normal"]},
        )

        historian.store.store(trace)
        retrieved = historian.store.get(trace.trace_id)

        assert retrieved is not None
        assert retrieved.agent_genus == "O"
        assert retrieved.inputs["observed_agent"] == "test-agent"

    def test_observation_creates_semantic_trace(self, historian, mock_agent) -> None:
        """Test observation creates semantic trace for N-gent."""
        trace = create_test_trace(
            trace_id=f"obs-{mock_agent.id}-001",
            agent_id="panopticon",
            agent_genus="O",
            inputs={"target": mock_agent.id},
            outputs={"status": "COMPLETED", "duration_ms": 42.5},
        )

        historian.store.store(trace)

        # Query back
        all_traces = list(historian.store.query(agent_genus="O"))
        assert len(all_traces) >= 1
        assert any(t.agent_genus == "O" for t in all_traces)

    def test_observation_lineage_traceable(self, historian, mock_agent) -> None:
        """Test observation lineage can be traced."""
        # Parent observation
        parent_trace = create_test_trace(
            trace_id="parent-obs-001",
            agent_id="panopticon",
            agent_genus="O",
            inputs={"target": mock_agent.id},
            outputs={"status": "OK"},
        )
        historian.store.store(parent_trace)

        # Child observation (follow-up)
        child_trace = create_test_trace(
            trace_id="child-obs-002",
            agent_id="panopticon",
            agent_genus="O",
            parent_id=parent_trace.trace_id,
            inputs={"target": mock_agent.id, "context": parent_trace.trace_id},
            outputs={"status": "DETAILED"},
        )
        historian.store.store(child_trace)

        # Retrieve child and verify lineage
        child = historian.store.get("child-obs-002")
        assert child is not None
        assert child.parent_id == "parent-obs-001"

    def test_panopticon_status_to_narrative(self, historian, panopticon) -> None:
        """Test Panopticon status converts to narrative trace."""
        status = panopticon.get_status()

        trace = create_test_trace(
            trace_id=f"status-{status.timestamp.isoformat()}",
            agent_id="panopticon",
            agent_genus="O",
            action="INVOKE",
            inputs={"request": "status_check"},
            outputs={
                "system_status": status.status.value,
                "uptime": status.uptime_seconds,
                "alert_count": len(status.alerts),
            },
        )

        historian.store.store(trace)

        # Can query by agent
        panopticon_traces = list(historian.store.query(agent_id="panopticon"))
        assert len(panopticon_traces) >= 1


# =============================================================================
# Full Stack Integration
# =============================================================================


class TestObservationStackFullIntegration:
    """Test complete observation stack flow."""

    @pytest.mark.asyncio
    async def test_observe_emit_display_record_flow(
        self, historian, mock_agent
    ) -> None:
        """Test O-gent observe → W-gent emit → I-gent display → N-gent record."""
        # 1. Create observation infrastructure
        obs_panopticon = create_observable_panopticon()
        wire_observer = create_wire_observer()

        # 2. O-gent: Observe agent
        context = wire_observer.pre_invoke(mock_agent, {"task": "compute"})

        # 3. Simulate agent execution
        await asyncio.sleep(0.01)  # Simulate work

        # 4. O-gent: Complete observation
        result = await wire_observer.post_invoke(context, {"result": "done"}, 10.0)

        # 5. W-gent: Emit to wire
        snapshot = obs_panopticon.collect_snapshot()
        obs_panopticon.emit_snapshot(snapshot)
        wire_dict = snapshot.to_dict()

        assert "timestamp" in wire_dict

        # 6. I-gent: Format for display
        dashboard = create_panopticon_dashboard(obs_panopticon)
        compact = dashboard.render_compact()

        assert "[O]" in compact

        # 7. N-gent: Record as trace
        trace = create_test_trace(
            trace_id=f"flow-{context.observation_id}",
            agent_id="observation-flow",
            agent_genus="O",
            inputs={"agent": context.agent_id, "input": str(context.input_data)},
            outputs={
                "result": str(result.output_data),
                "duration_ms": result.duration_ms,
            },
        )
        historian.store.store(trace)

        # 8. Verify end-to-end
        retrieved = historian.store.get(trace.trace_id)
        assert retrieved is not None
        assert retrieved.outputs["duration_ms"] == 10.0

    @pytest.mark.asyncio
    async def test_budget_constrained_observation_flow(
        self, historian, mock_agent, voi_ledger
    ):
        """Test observation flow with VoI budget constraints."""
        # 1. Create VoI-constrained observation
        wire_observer = create_wire_observer()

        # 2. Observe with budget tracking
        context = wire_observer.pre_invoke(mock_agent, {"task": "expensive"})

        await asyncio.sleep(0.01)

        result = await wire_observer.post_invoke(context, {"value": 100}, 50.0)
        assert result is not None  # Observation completed

        # 3. Record in VoI ledger
        finding = ObservationFinding(
            type=FindingType.HEALTH_CONFIRMED,
            confidence=0.9,
        )

        receipt = voi_ledger.log_observation(
            observer_id=context.agent_id,
            target_id=mock_agent.id,
            gas_consumed=Gas(20.0),
            finding=finding,
            depth=ObservationDepth.SEMANTIC_SPOT,
        )

        # 4. Record to narrative
        trace = create_test_trace(
            trace_id=f"voi-{context.observation_id}",
            agent_id="voi-flow",
            agent_genus="O",
            inputs={
                "agent": context.agent_id,
                "gas_consumed": 20.0,
            },
            outputs={
                "voi": receipt.voi,
            },
        )
        historian.store.store(trace)

        # 5. Verify economics tracked
        retrieved = historian.store.get(trace.trace_id)
        assert retrieved is not None
        assert "voi" in retrieved.outputs
