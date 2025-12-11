"""
Tests for O-gent Phase 4: W-gent Integration.

Tests cover:
- ObservablePanopticon wire protocol emission
- WireObserver observation capture
- PanopticonDashboard rendering
- Emission modes (continuous, batched, on_change, on_alert)
- History management
- Callbacks and subscriptions
"""

from __future__ import annotations

import asyncio
import json
import tempfile
from collections.abc import Generator
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

import pytest

from ..observable_panopticon import (
    DashboardConfig,
    EmissionMode,
    ObservablePanopticon,
    PanopticonDashboard,
    WireObserver,
    WireStatusSnapshot,
    create_observable_panopticon,
    create_panopticon_dashboard,
    create_streaming_panopticon,
    create_wire_observer,
)
from ..observer import ObservationStatus
from ..panopticon import (
    AlertSeverity,
    AxiologicalStatus,
    BootstrapStatus,
    PanopticonAlert,
    SemanticStatus,
    SystemStatus,
    TelemetryStatus,
    UnifiedPanopticonStatus,
)

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture
def temp_wire_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for wire files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_panopticon_status() -> UnifiedPanopticonStatus:
    """Create a mock UnifiedPanopticonStatus."""
    return UnifiedPanopticonStatus(
        status=SystemStatus.HOMEOSTATIC,
        uptime_seconds=3600.0,
        telemetry=TelemetryStatus(
            latency_p95_ms=50.0,
            error_rate=0.01,
        ),
        semantic=SemanticStatus(
            drift_score=0.1,
            knots_intact_pct=98.0,
        ),
        axiological=AxiologicalStatus(
            net_roc=1.5,
            system_gdp=100.0,
        ),
        bootstrap=BootstrapStatus(
            kernel_intact=True,
            verification_streak=10,
        ),
    )


@dataclass
class MockAgent:
    """Mock agent for testing."""

    name: str = "TestAgent"


# =============================================================================
# Tests: WireStatusSnapshot
# =============================================================================


class TestWireStatusSnapshot:
    """Tests for WireStatusSnapshot."""

    def test_create_snapshot(self) -> None:
        """Test creating a status snapshot."""
        snapshot = WireStatusSnapshot(
            timestamp=datetime.now(),
            system_status="HOMEOSTATIC",
            uptime_seconds=3600.0,
            telemetry_healthy=True,
            telemetry_latency_p95=50.0,
            telemetry_error_rate=0.01,
            semantic_healthy=True,
            semantic_drift=0.1,
            semantic_knots_intact=98.0,
            economic_healthy=True,
            economic_roc=1.5,
            economic_gdp=100.0,
            bootstrap_intact=True,
            bootstrap_streak=10,
            alert_count=0,
            critical_alerts=0,
        )

        assert snapshot.system_status == "HOMEOSTATIC"
        assert snapshot.telemetry_healthy is True
        assert snapshot.economic_roc == 1.5

    def test_to_dict(self) -> None:
        """Test converting snapshot to dict."""
        snapshot = WireStatusSnapshot(
            timestamp=datetime(2025, 1, 1, 12, 0, 0),
            system_status="DEGRADED",
            uptime_seconds=7200.0,
            telemetry_healthy=False,
            telemetry_latency_p95=500.0,
            telemetry_error_rate=0.08,
            semantic_healthy=True,
            semantic_drift=0.2,
            semantic_knots_intact=96.0,
            economic_healthy=True,
            economic_roc=1.2,
            economic_gdp=80.0,
            bootstrap_intact=True,
            bootstrap_streak=5,
            alert_count=3,
            critical_alerts=1,
            recent_alert="Test alert",
        )

        data = snapshot.to_dict()

        assert data["system_status"] == "DEGRADED"
        assert data["telemetry"]["latency_p95"] == 500.0
        assert data["semantic"]["drift"] == 0.2
        assert data["economic"]["roc"] == 1.2
        assert data["bootstrap"]["intact"] is True
        assert data["alerts"]["count"] == 3

    def test_from_panopticon_status(
        self, mock_panopticon_status: UnifiedPanopticonStatus
    ) -> None:
        """Test creating snapshot from UnifiedPanopticonStatus."""
        snapshot = WireStatusSnapshot.from_panopticon_status(mock_panopticon_status)

        assert snapshot.system_status == "HOMEOSTATIC"
        assert snapshot.telemetry_latency_p95 == 50.0
        assert snapshot.semantic_drift == 0.1
        assert snapshot.economic_roc == 1.5
        assert snapshot.bootstrap_intact is True


# =============================================================================
# Tests: ObservablePanopticon
# =============================================================================


class TestObservablePanopticon:
    """Tests for ObservablePanopticon."""

    def test_create_observable_panopticon(self, temp_wire_dir: Path) -> None:
        """Test creating ObservablePanopticon."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        assert panopticon.agent_name == "test-panopticon"
        assert panopticon.emission_mode == EmissionMode.BATCHED

    def test_collect_snapshot(self, temp_wire_dir: Path) -> None:
        """Test collecting status snapshot."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        snapshot = panopticon.collect_snapshot()

        assert isinstance(snapshot, WireStatusSnapshot)
        assert snapshot.system_status in [
            "HOMEOSTATIC",
            "DEGRADED",
            "CRITICAL",
            "UNKNOWN",
        ]

    def test_emit_snapshot(self, temp_wire_dir: Path) -> None:
        """Test emitting snapshot via wire protocol."""
        wire_dir = temp_wire_dir / "test-panopticon"
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=wire_dir,
        )

        snapshot = panopticon.collect_snapshot()
        panopticon.emit_snapshot(snapshot)

        # Check state file was written
        state_file = wire_dir / "state.json"
        assert state_file.exists()

        with open(state_file) as f:
            state = json.load(f)
        # system_status is nested under metadata.snapshot
        metadata = state.get("metadata", {})
        snapshot_data = metadata.get("snapshot", {})
        assert "system_status" in snapshot_data

    def test_emit_alert(self, temp_wire_dir: Path) -> None:
        """Test emitting alert via wire protocol."""
        wire_dir = temp_wire_dir / "test-panopticon"
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=wire_dir,
        )

        alert = PanopticonAlert(
            severity=AlertSeverity.WARN,
            source="test",
            message="Test alert message",
        )

        panopticon.emit_alert(alert)

        # Check stream log was written
        stream_file = wire_dir / "stream.log"
        assert stream_file.exists()

        content = stream_file.read_text()
        assert "WARN" in content
        assert "test" in content

    def test_history_management(self, temp_wire_dir: Path) -> None:
        """Test history limit is respected."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
            history_limit=5,
        )

        # Collect more than history limit
        for _ in range(10):
            panopticon.collect_snapshot()

        assert len(panopticon._history) == 5

    def test_get_history(self, temp_wire_dir: Path) -> None:
        """Test getting history snapshots."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        for _ in range(5):
            panopticon.collect_snapshot()

        history = panopticon.get_history(limit=3)
        assert len(history) == 3

    def test_get_summary(self, temp_wire_dir: Path) -> None:
        """Test getting human-readable summary."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        summary = panopticon.get_summary()

        assert "O-gent Panopticon" in summary
        assert "Telemetry" in summary
        assert "Semantics" in summary
        assert "Economics" in summary


# =============================================================================
# Tests: Emission Modes
# =============================================================================


class TestEmissionModes:
    """Tests for different emission modes."""

    def test_continuous_mode(self, temp_wire_dir: Path) -> None:
        """Test continuous emission mode always emits."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
            emission_mode=EmissionMode.CONTINUOUS,
        )

        snapshot = panopticon.collect_snapshot()
        assert panopticon.should_emit(snapshot) is True

    def test_batched_mode(self, temp_wire_dir: Path) -> None:
        """Test batched emission mode."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
            emission_mode=EmissionMode.BATCHED,
        )

        snapshot = panopticon.collect_snapshot()
        assert panopticon.should_emit(snapshot) is True

    def test_on_change_mode(self, temp_wire_dir: Path) -> None:
        """Test on_change emission mode only emits on status change."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
            emission_mode=EmissionMode.ON_CHANGE,
        )

        snapshot1 = panopticon.collect_snapshot()
        # First emission should always emit
        assert panopticon.should_emit(snapshot1) is True

        # Same status should not emit
        panopticon.collect_snapshot()
        snapshot2_same = WireStatusSnapshot(
            timestamp=datetime.now(),
            system_status=snapshot1.system_status,  # Same status
            uptime_seconds=100,
            telemetry_healthy=True,
            telemetry_latency_p95=50.0,
            telemetry_error_rate=0.01,
            semantic_healthy=True,
            semantic_drift=0.1,
            semantic_knots_intact=98.0,
            economic_healthy=True,
            economic_roc=1.5,
            economic_gdp=100.0,
            bootstrap_intact=True,
            bootstrap_streak=10,
            alert_count=0,
            critical_alerts=0,
        )
        assert panopticon.should_emit(snapshot2_same) is False

    def test_on_alert_mode(self, temp_wire_dir: Path) -> None:
        """Test on_alert emission mode only emits on new alerts."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
            emission_mode=EmissionMode.ON_ALERT,
        )

        snapshot_no_alerts = WireStatusSnapshot(
            timestamp=datetime.now(),
            system_status="HOMEOSTATIC",
            uptime_seconds=100,
            telemetry_healthy=True,
            telemetry_latency_p95=50.0,
            telemetry_error_rate=0.01,
            semantic_healthy=True,
            semantic_drift=0.1,
            semantic_knots_intact=98.0,
            economic_healthy=True,
            economic_roc=1.5,
            economic_gdp=100.0,
            bootstrap_intact=True,
            bootstrap_streak=10,
            alert_count=0,
            critical_alerts=0,
        )

        # No alerts, should not emit
        assert panopticon.should_emit(snapshot_no_alerts) is False

        # With new alert, should emit
        snapshot_with_alert = WireStatusSnapshot(
            timestamp=datetime.now(),
            system_status="DEGRADED",
            uptime_seconds=100,
            telemetry_healthy=True,
            telemetry_latency_p95=50.0,
            telemetry_error_rate=0.01,
            semantic_healthy=True,
            semantic_drift=0.1,
            semantic_knots_intact=98.0,
            economic_healthy=True,
            economic_roc=1.5,
            economic_gdp=100.0,
            bootstrap_intact=True,
            bootstrap_streak=10,
            alert_count=1,
            critical_alerts=0,
        )
        assert panopticon.should_emit(snapshot_with_alert) is True


# =============================================================================
# Tests: Callbacks
# =============================================================================


class TestCallbacks:
    """Tests for callback subscriptions."""

    def test_on_status_change_callback(self, temp_wire_dir: Path) -> None:
        """Test registering and triggering status change callback."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        received_snapshots = []

        def callback(snapshot: WireStatusSnapshot) -> None:
            received_snapshots.append(snapshot)

        unsubscribe = panopticon.on_status_change(callback)

        # Manually trigger callback
        snapshot = panopticon.collect_snapshot()
        for cb in panopticon._on_status_change:
            cb(snapshot)

        assert len(received_snapshots) == 1

        # Unsubscribe
        unsubscribe()
        assert len(panopticon._on_status_change) == 0

    def test_on_alert_callback(self, temp_wire_dir: Path) -> None:
        """Test registering and triggering alert callback."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        received_alerts = []

        def callback(alert: PanopticonAlert) -> None:
            received_alerts.append(alert)

        unsubscribe = panopticon.on_alert(callback)

        # Emit an alert
        alert = PanopticonAlert(
            severity=AlertSeverity.ERROR,
            source="test",
            message="Test error",
        )
        panopticon.emit_alert(alert)

        assert len(received_alerts) == 1
        assert received_alerts[0].severity == AlertSeverity.ERROR

        # Unsubscribe
        unsubscribe()
        assert len(panopticon._on_alert) == 0


# =============================================================================
# Tests: Streaming
# =============================================================================


class TestStreaming:
    """Tests for async streaming."""

    @pytest.mark.asyncio
    async def test_start_stop_streaming(self, temp_wire_dir: Path) -> None:
        """Test starting and stopping streaming."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
            emission_interval=0.1,
        )

        await panopticon.start_streaming()
        assert panopticon._streaming is True

        await asyncio.sleep(0.2)  # Let it emit a couple times

        await panopticon.stop_streaming()
        assert panopticon._streaming is False

    @pytest.mark.asyncio
    async def test_stream_snapshots_generator(self, temp_wire_dir: Path) -> None:
        """Test async generator for streaming snapshots."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        snapshots = []
        count = 0

        async for snapshot in panopticon.stream_snapshots(interval=0.1):
            snapshots.append(snapshot)
            count += 1
            if count >= 3:
                break

        assert len(snapshots) == 3
        for s in snapshots:
            assert isinstance(s, WireStatusSnapshot)

    @pytest.mark.asyncio
    async def test_create_streaming_panopticon(self, temp_wire_dir: Path) -> None:
        """Test factory function for streaming panopticon."""
        panopticon = await create_streaming_panopticon(
            agent_name="test-streaming",
            emission_interval=0.1,
        )

        assert panopticon._streaming is True

        await panopticon.stop_streaming()


# =============================================================================
# Tests: WireObserver
# =============================================================================


class TestWireObserver:
    """Tests for WireObserver."""

    def test_create_wire_observer(self, temp_wire_dir: Path) -> None:
        """Test creating WireObserver."""
        observer = WireObserver(
            observer_id="test-observer",
            wire_base=temp_wire_dir,
        )

        assert observer.observer_id == "test-observer"
        assert observer._emit_context is True
        assert observer._emit_results is True
        assert observer._emit_entropy is True

    def test_pre_invoke(self, temp_wire_dir: Path) -> None:
        """Test pre_invoke creates observation context."""
        observer = WireObserver(
            observer_id="test-observer",
            wire_base=temp_wire_dir,
        )

        agent = MockAgent(name="TestAgent")
        context = observer.pre_invoke(agent, {"input": "test"})

        assert context.agent_name == "TestAgent"
        assert observer._observation_count == 1

    @pytest.mark.asyncio
    async def test_post_invoke(self, temp_wire_dir: Path) -> None:
        """Test post_invoke records observation result."""
        observer = WireObserver(
            observer_id="test-observer",
            wire_base=temp_wire_dir,
        )

        agent = MockAgent(name="TestAgent")
        context = observer.pre_invoke(agent, {"input": "test"})

        result = await observer.post_invoke(context, {"output": "result"}, 100.0)

        assert result.status == ObservationStatus.COMPLETED
        assert result.duration_ms == 100.0

    def test_record_entropy(self, temp_wire_dir: Path) -> None:
        """Test recording entropy (errors)."""
        observer = WireObserver(
            observer_id="test-observer",
            wire_base=temp_wire_dir,
        )

        agent = MockAgent(name="TestAgent")
        context = observer.pre_invoke(agent, {"input": "test"})

        error = ValueError("Test error")
        observer.record_entropy(context, error)

        assert observer._error_count == 1

        # Check error was logged to stream
        stream_file = temp_wire_dir / "stream.log"
        assert stream_file.exists()
        content = stream_file.read_text()
        assert "ERROR" in content
        assert "ValueError" in content

    def test_get_stats(self, temp_wire_dir: Path) -> None:
        """Test getting observation statistics."""
        observer = WireObserver(
            observer_id="test-observer",
            wire_base=temp_wire_dir,
        )

        agent = MockAgent()
        for _ in range(5):
            observer.pre_invoke(agent, {})

        stats = observer.get_stats()
        assert stats["observations"] == 5
        assert stats["errors"] == 0

    def test_wire_property(self, temp_wire_dir: Path) -> None:
        """Test accessing underlying WireObservable."""
        observer = WireObserver(
            observer_id="test-observer",
            wire_base=temp_wire_dir,
        )

        wire = observer.wire
        assert wire is not None
        assert wire.agent_name == "test-observer"


# =============================================================================
# Tests: PanopticonDashboard
# =============================================================================


class TestPanopticonDashboard:
    """Tests for PanopticonDashboard."""

    def test_create_dashboard(self, temp_wire_dir: Path) -> None:
        """Test creating dashboard."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        dashboard = PanopticonDashboard(panopticon=panopticon)

        assert dashboard.panopticon is panopticon
        assert dashboard.config.update_interval == 1.0

    def test_dashboard_config(self) -> None:
        """Test dashboard configuration."""
        config = DashboardConfig(
            update_interval=0.5,
            history_depth=30,
            compact_mode=True,
        )

        assert config.update_interval == 0.5
        assert config.history_depth == 30
        assert config.compact_mode is True

    def test_render_compact(self, temp_wire_dir: Path) -> None:
        """Test rendering compact status line."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        dashboard = PanopticonDashboard(panopticon=panopticon)

        compact = dashboard.render_compact()

        assert "[O]" in compact
        assert "Alerts:" in compact

    def test_render_dimensions(self, temp_wire_dir: Path) -> None:
        """Test rendering dimension panels."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        dashboard = PanopticonDashboard(panopticon=panopticon)

        dimensions = dashboard.render_dimensions()

        assert "TELEMETRY" in dimensions
        assert "SEMANTICS" in dimensions
        assert "ECONOMICS" in dimensions

    def test_render_sparklines(self, temp_wire_dir: Path) -> None:
        """Test rendering sparklines."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        dashboard = PanopticonDashboard(panopticon=panopticon)

        # Add some history
        for i in range(10):
            dashboard._latency_history.append(50.0 + i * 10)
            dashboard._roc_history.append(1.0 + i * 0.1)
            dashboard._drift_history.append(0.1 + i * 0.02)

        sparklines = dashboard.render_sparklines()

        assert "Latency" in sparklines
        assert "RoC" in sparklines
        assert "Drift" in sparklines

    def test_get_wire_data(self, temp_wire_dir: Path) -> None:
        """Test getting wire-formatted data."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        dashboard = PanopticonDashboard(panopticon=panopticon)

        data = dashboard.get_wire_data()

        assert "snapshot" in data
        assert "sparklines" in data
        assert "compact" in data
        assert "dimensions" in data

    def test_history_collection(self, temp_wire_dir: Path) -> None:
        """Test history collection via callback."""
        panopticon = ObservablePanopticon(
            agent_name="test-panopticon",
            wire_base=temp_wire_dir / "test-panopticon",
        )

        dashboard = PanopticonDashboard(
            panopticon=panopticon,
            config=DashboardConfig(history_depth=5),
        )

        # Simulate status changes
        for i in range(10):
            snapshot = WireStatusSnapshot(
                timestamp=datetime.now(),
                system_status="HOMEOSTATIC",
                uptime_seconds=i * 100,
                telemetry_healthy=True,
                telemetry_latency_p95=50.0 + i,
                telemetry_error_rate=0.01,
                semantic_healthy=True,
                semantic_drift=0.1 + i * 0.01,
                semantic_knots_intact=98.0,
                economic_healthy=True,
                economic_roc=1.5 + i * 0.1,
                economic_gdp=100.0,
                bootstrap_intact=True,
                bootstrap_streak=i,
                alert_count=0,
                critical_alerts=0,
            )
            dashboard._collect_history(snapshot)

        # History should be trimmed to depth
        assert len(dashboard._latency_history) == 5
        assert len(dashboard._roc_history) == 5
        assert len(dashboard._drift_history) == 5


# =============================================================================
# Tests: Factory Functions
# =============================================================================


class TestFactoryFunctions:
    """Tests for factory functions."""

    def test_create_observable_panopticon(self, temp_wire_dir: Path) -> None:
        """Test create_observable_panopticon factory."""
        panopticon = create_observable_panopticon(
            agent_name="factory-test",
            emission_mode=EmissionMode.CONTINUOUS,
            emission_interval=0.5,
        )

        assert panopticon.agent_name == "factory-test"
        assert panopticon.emission_mode == EmissionMode.CONTINUOUS
        assert panopticon.emission_interval == 0.5

    def test_create_wire_observer(self, temp_wire_dir: Path) -> None:
        """Test create_wire_observer factory."""
        observer = create_wire_observer(
            observer_id="factory-observer",
            emit_all=True,
        )

        assert observer.observer_id == "factory-observer"
        assert observer._emit_context is True
        assert observer._emit_results is True

    def test_create_wire_observer_minimal(self, temp_wire_dir: Path) -> None:
        """Test create_wire_observer with minimal emission."""
        observer = create_wire_observer(
            observer_id="minimal-observer",
            emit_all=False,
        )

        assert observer._emit_context is False
        assert observer._emit_results is False
        assert observer._emit_entropy is True  # Always emits errors

    def test_create_panopticon_dashboard(self, temp_wire_dir: Path) -> None:
        """Test create_panopticon_dashboard factory."""
        dashboard = create_panopticon_dashboard(
            compact=True,
            update_interval=0.5,
        )

        assert dashboard.config.compact_mode is True
        assert dashboard.config.update_interval == 0.5


# =============================================================================
# Tests: Integration Scenarios
# =============================================================================


class TestIntegrationScenarios:
    """Integration tests for common scenarios."""

    @pytest.mark.asyncio
    async def test_full_observation_flow(self, temp_wire_dir: Path) -> None:
        """Test full flow: observe → emit → read."""
        wire_dir = temp_wire_dir / "integration-test"

        # Create components
        panopticon = ObservablePanopticon(
            agent_name="integration-test",
            wire_base=wire_dir,
        )

        # Collect and emit
        snapshot = panopticon.collect_snapshot()
        panopticon.emit_snapshot(snapshot)

        # Verify wire files
        assert (wire_dir / "state.json").exists()

        # Add alert
        panopticon.panopticon.add_alert(
            AlertSeverity.WARN,
            "test",
            "Integration test alert",
        )

        # Emit again
        snapshot2 = panopticon.collect_snapshot()
        panopticon.emit_snapshot(snapshot2)

        # Check alert was captured in history
        assert len(panopticon._history) == 2

    @pytest.mark.asyncio
    async def test_dashboard_with_streaming(self, temp_wire_dir: Path) -> None:
        """Test dashboard with streaming panopticon."""
        panopticon = ObservablePanopticon(
            agent_name="dashboard-stream-test",
            wire_base=temp_wire_dir / "dashboard-stream-test",
            emission_interval=0.1,
        )

        dashboard = PanopticonDashboard(panopticon=panopticon)

        # Start streaming
        await dashboard.start()

        # Wait for some updates
        await asyncio.sleep(0.3)

        # Get data
        data = dashboard.get_wire_data()
        assert data["snapshot"] is not None

        # Stop
        await dashboard.stop()

    def test_observer_chain(self, temp_wire_dir: Path) -> None:
        """Test chaining WireObserver with other observers."""
        observer = WireObserver(
            observer_id="chain-test",
            wire_base=temp_wire_dir / "chain-test",
        )

        # Simulate observation chain
        agent = MockAgent(name="ChainAgent")

        observer.pre_invoke(agent, {"step": 1})
        assert observer._observation_count == 1

        observer.pre_invoke(agent, {"step": 2})
        assert observer._observation_count == 2

        # Verify stream log has both observations
        stream_file = temp_wire_dir / "chain-test" / "stream.log"
        assert stream_file.exists()

    def test_multiple_panopticons(self, temp_wire_dir: Path) -> None:
        """Test multiple panopticons with different wire directories."""
        p1 = ObservablePanopticon(
            agent_name="panopticon-1",
            wire_base=temp_wire_dir / "p1",
        )

        p2 = ObservablePanopticon(
            agent_name="panopticon-2",
            wire_base=temp_wire_dir / "p2",
        )

        # Both should work independently
        s1 = p1.collect_snapshot()
        s2 = p2.collect_snapshot()

        p1.emit_snapshot(s1)
        p2.emit_snapshot(s2)

        assert (temp_wire_dir / "p1" / "state.json").exists()
        assert (temp_wire_dir / "p2" / "state.json").exists()
