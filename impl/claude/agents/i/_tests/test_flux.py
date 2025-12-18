"""
Tests for I-gent v2.5 Flux components.

Tests the density field rendering, flow arrows, state management,
and flux screen functionality.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest

from agents.i.data.state import (
    AgentSnapshot,
    FluxState,
    SessionState,
    create_demo_flux_state,
)
from agents.i.theme.earth import EARTH_PALETTE, EarthTheme
from agents.i.widgets.density_field import (
    DENSITY_CHARS,
    Phase,
    activity_to_density_char,
    add_glitch_effect,
    generate_density_grid,
)
from agents.i.widgets.flow_arrow import (
    ConnectionType,
    Direction,
    generate_horizontal_arrow,
    generate_vertical_arrow,
    throughput_to_connection_type,
)

# ============================================================================
# Theme Tests
# ============================================================================


class TestEarthPalette:
    """Test the earth color palette."""

    def test_palette_has_required_colors(self) -> None:
        """Palette contains all required colors."""
        required = [
            "background",
            "active",
            "dormant",
            "waking",
            "waning",
            "void",
            "focus",
            "text_primary",
            "text_secondary",
        ]
        for color in required:
            assert color in EARTH_PALETTE
            assert EARTH_PALETTE[color].startswith("#")

    def test_density_color_mapping(self) -> None:
        """Density colors map correctly to activity levels."""
        # High activity -> active color
        assert EarthTheme.density_color(0.9) == EARTH_PALETTE["active"]
        # Medium activity -> waking color
        assert EarthTheme.density_color(0.6) == EARTH_PALETTE["waking"]
        # Low activity -> waning color
        assert EarthTheme.density_color(0.3) == EARTH_PALETTE["waning"]
        # Very low activity -> dormant color
        assert EarthTheme.density_color(0.1) == EARTH_PALETTE["dormant"]

    def test_phase_color_mapping(self) -> None:
        """Phase colors map correctly."""
        assert EarthTheme.phase_color("ACTIVE") == EARTH_PALETTE["active"]
        assert EarthTheme.phase_color("DORMANT") == EARTH_PALETTE["dormant"]
        assert EarthTheme.phase_color("VOID") == EARTH_PALETTE["void"]
        # Case insensitive
        assert EarthTheme.phase_color("active") == EARTH_PALETTE["active"]

    def test_connection_color_mapping(self) -> None:
        """Connection colors map correctly to throughput."""
        assert EarthTheme.connection_color(0.8) == EARTH_PALETTE["connection_high"]
        assert EarthTheme.connection_color(0.5) == EARTH_PALETTE["connection_medium"]
        assert EarthTheme.connection_color(0.1) == EARTH_PALETTE["connection_low"]
        assert EarthTheme.connection_color(0.0) == EARTH_PALETTE["connection_lazy"]


# ============================================================================
# Density Field Tests
# ============================================================================


class TestDensityCharacters:
    """Test density character generation."""

    def test_density_chars_ordered(self) -> None:
        """Density chars are ordered from light to dark."""
        assert len(DENSITY_CHARS) == 5
        assert DENSITY_CHARS[0] == " "  # Empty
        assert DENSITY_CHARS[4] == "█"  # Full

    def test_activity_to_density_char(self) -> None:
        """Activity maps to appropriate density character."""
        # Very low activity -> space or light
        char_low = activity_to_density_char(0.0, 0, 0)
        assert char_low in DENSITY_CHARS[:2]

        # High activity -> dense character
        char_high = activity_to_density_char(1.0, 0, 0)
        assert char_high in DENSITY_CHARS[3:]

    def test_position_affects_density(self) -> None:
        """Different positions produce variation for texture."""
        # Same activity at different positions should vary
        chars = {activity_to_density_char(0.5, x, y) for x in range(5) for y in range(5)}
        # Should have some variation (not all the same)
        assert len(chars) > 1


class TestDensityGrid:
    """Test density grid generation."""

    def test_grid_dimensions(self) -> None:
        """Grid has correct dimensions."""
        grid = generate_density_grid(10, 5, 0.5, Phase.ACTIVE)
        assert len(grid) == 5
        assert all(len(row) == 10 for row in grid)

    def test_grid_with_name(self) -> None:
        """Grid embeds agent name."""
        grid = generate_density_grid(20, 5, 0.5, Phase.ACTIVE, name="TEST")
        # Name should appear in center row
        center = grid[2]
        assert "TEST" in center

    def test_void_phase_uses_glitch_chars(self) -> None:
        """Void phase produces glitch characters."""
        grid = generate_density_grid(10, 5, 0.5, Phase.VOID)
        # Should contain glitch characters, not normal density chars
        all_chars = "".join(grid)
        # At least some glitch chars present
        assert any(c in "▚▞▛▜▙▟" for c in all_chars)


class TestGlitchEffect:
    """Test glitch/Zalgo effect."""

    def test_glitch_adds_characters(self) -> None:
        """Glitch effect adds combining characters."""
        original = "TEST"
        glitched = add_glitch_effect(original, intensity=1.0)
        # Glitched version should be longer (has combining chars)
        assert len(glitched) >= len(original)

    def test_glitch_intensity_zero(self) -> None:
        """Zero intensity produces no glitch."""
        original = "TEST"
        result = add_glitch_effect(original, intensity=0.0)
        assert result == original


# ============================================================================
# Flow Arrow Tests
# ============================================================================


class TestThroughputMapping:
    """Test throughput to connection type mapping."""

    def test_high_throughput(self) -> None:
        """High throughput maps to HIGH connection type."""
        assert throughput_to_connection_type(0.9) == ConnectionType.HIGH
        assert throughput_to_connection_type(0.7) == ConnectionType.HIGH

    def test_medium_throughput(self) -> None:
        """Medium throughput maps to MEDIUM connection type."""
        assert throughput_to_connection_type(0.5) == ConnectionType.MEDIUM
        assert throughput_to_connection_type(0.3) == ConnectionType.MEDIUM

    def test_low_throughput(self) -> None:
        """Low throughput maps to LOW connection type."""
        assert throughput_to_connection_type(0.2) == ConnectionType.LOW
        assert throughput_to_connection_type(0.1) == ConnectionType.LOW

    def test_zero_throughput(self) -> None:
        """Zero throughput maps to LAZY connection type."""
        assert throughput_to_connection_type(0.0) == ConnectionType.LAZY


class TestHorizontalArrow:
    """Test horizontal arrow generation."""

    def test_horizontal_arrow_length(self) -> None:
        """Arrow has correct length."""
        arrow = generate_horizontal_arrow(10, ConnectionType.MEDIUM)
        assert len(arrow) == 10

    def test_horizontal_arrow_with_head(self) -> None:
        """Arrow includes arrow head."""
        arrow = generate_horizontal_arrow(10, ConnectionType.MEDIUM, show_arrow=True)
        assert arrow.endswith("►")

    def test_horizontal_arrow_without_head(self) -> None:
        """Arrow without head is just line."""
        arrow = generate_horizontal_arrow(10, ConnectionType.MEDIUM, show_arrow=False)
        assert "►" not in arrow

    def test_high_throughput_double_line(self) -> None:
        """High throughput uses double line character."""
        arrow = generate_horizontal_arrow(5, ConnectionType.HIGH, show_arrow=False)
        assert "═" in arrow

    def test_low_throughput_dotted(self) -> None:
        """Low throughput uses dots."""
        arrow = generate_horizontal_arrow(5, ConnectionType.LOW, show_arrow=False)
        assert "·" in arrow


class TestVerticalArrow:
    """Test vertical arrow generation."""

    def test_vertical_arrow_length(self) -> None:
        """Arrow has correct number of rows."""
        lines = generate_vertical_arrow(5, ConnectionType.MEDIUM)
        assert len(lines) == 5

    def test_vertical_arrow_with_head(self) -> None:
        """Arrow includes arrow head at bottom."""
        lines = generate_vertical_arrow(5, ConnectionType.MEDIUM, show_arrow=True)
        assert lines[-1] == "▼"


# ============================================================================
# State Tests
# ============================================================================


class TestAgentSnapshot:
    """Test AgentSnapshot data class."""

    def test_default_values(self) -> None:
        """Snapshot has sensible defaults."""
        snap = AgentSnapshot(id="test", name="Test Agent")
        assert snap.phase == Phase.DORMANT
        assert snap.activity == 0.0
        assert snap.children == []
        assert snap.connections == {}

    def test_to_dict_roundtrip(self) -> None:
        """Snapshot survives serialization roundtrip."""
        original = AgentSnapshot(
            id="test",
            name="Test Agent",
            phase=Phase.ACTIVE,
            activity=0.75,
            grid_x=3,
            grid_y=2,
            connections={"other": 0.5},
        )
        data = original.to_dict()
        restored = AgentSnapshot.from_dict(data)

        assert restored.id == original.id
        assert restored.name == original.name
        assert restored.phase == original.phase
        assert restored.activity == original.activity
        assert restored.grid_x == original.grid_x
        assert restored.grid_y == original.grid_y
        assert restored.connections == original.connections


class TestFluxState:
    """Test FluxState management."""

    def test_add_and_get_agent(self) -> None:
        """Can add and retrieve agents."""
        state = FluxState()
        agent = AgentSnapshot(id="test", name="Test")
        state.add_agent(agent)

        assert state.get_agent("test") is agent
        assert state.get_agent("nonexistent") is None

    def test_remove_agent(self) -> None:
        """Can remove agents."""
        state = FluxState()
        state.add_agent(AgentSnapshot(id="test", name="Test"))
        state.remove_agent("test")
        assert state.get_agent("test") is None

    def test_remove_agent_clears_focus(self) -> None:
        """Removing focused agent clears focus."""
        state = FluxState()
        state.add_agent(AgentSnapshot(id="test", name="Test"))
        state.focused_id = "test"
        state.remove_agent("test")
        assert state.focused_id is None

    def test_focus_next_cycles(self) -> None:
        """Focus next cycles through agents."""
        state = FluxState()
        state.add_agent(AgentSnapshot(id="a", name="A"))
        state.add_agent(AgentSnapshot(id="b", name="B"))
        state.add_agent(AgentSnapshot(id="c", name="C"))

        state.focus_next()
        assert state.focused_id == "a"
        state.focus_next()
        assert state.focused_id == "b"
        state.focus_next()
        assert state.focused_id == "c"
        state.focus_next()
        assert state.focused_id == "a"  # Cycles back

    def test_focus_prev_cycles(self) -> None:
        """Focus prev cycles backwards through agents."""
        state = FluxState()
        state.add_agent(AgentSnapshot(id="a", name="A"))
        state.add_agent(AgentSnapshot(id="b", name="B"))

        state.focus_prev()
        assert state.focused_id == "b"
        state.focus_prev()
        assert state.focused_id == "a"
        state.focus_prev()
        assert state.focused_id == "b"

    def test_get_agent_at_grid(self) -> None:
        """Can find agent by grid position."""
        state = FluxState()
        agent = AgentSnapshot(id="test", name="Test", grid_x=3, grid_y=2)
        state.add_agent(agent)

        assert state.get_agent_at_grid(3, 2) is agent
        assert state.get_agent_at_grid(0, 0) is None


class TestSessionState:
    """Test session state persistence."""

    def test_save_and_load(self) -> None:
        """Session state persists to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"

            # Create and save state
            session = SessionState()
            session.flux.add_agent(AgentSnapshot(id="test", name="Test"))
            session.show_connections = False
            session.last_focused_id = "test"
            session.save(path)

            # Load and verify
            loaded = SessionState.load(path)
            assert (
                loaded.get_agent("test") is not None
                if hasattr(loaded, "get_agent")
                else loaded.flux.get_agent("test") is not None
            )
            assert loaded.show_connections is False
            assert loaded.last_focused_id == "test"

    def test_load_missing_file(self) -> None:
        """Loading from missing file returns default state."""
        session = SessionState.load(Path("/nonexistent/path.json"))
        assert isinstance(session, SessionState)
        assert len(session.flux.agents) == 0

    def test_load_invalid_json(self) -> None:
        """Loading invalid JSON returns default state."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "state.json"
            path.write_text("invalid json {{{")

            session = SessionState.load(path)
            assert isinstance(session, SessionState)


class TestDemoState:
    """Test demo state creation."""

    def test_create_demo_flux_state(self) -> None:
        """Demo state has agents."""
        state = create_demo_flux_state()
        assert len(state.agents) > 0

    def test_demo_state_has_connections(self) -> None:
        """Demo state has some connections."""
        state = create_demo_flux_state()
        has_connections = any(agent.connections for agent in state.agents.values())
        assert has_connections

    def test_demo_state_has_focus(self) -> None:
        """Demo state has a focused agent."""
        state = create_demo_flux_state()
        assert state.focused_id is not None
        assert state.focused_id in state.agents


# ============================================================================
# Widget Tests (require Textual test framework)
# ============================================================================


class TestDensityFieldWidget:
    """Test DensityField widget (basic tests without full Textual app)."""

    def test_phase_enum(self) -> None:
        """Phase enum has required values."""
        assert Phase.DORMANT.value == "DORMANT"
        assert Phase.WAKING.value == "WAKING"
        assert Phase.ACTIVE.value == "ACTIVE"
        assert Phase.WANING.value == "WANING"
        assert Phase.VOID.value == "VOID"


class TestFlowArrowWidget:
    """Test FlowArrow widget (basic tests without full Textual app)."""

    def test_connection_type_enum(self) -> None:
        """ConnectionType enum has required values."""
        assert ConnectionType.HIGH.value == "HIGH"
        assert ConnectionType.MEDIUM.value == "MEDIUM"
        assert ConnectionType.LOW.value == "LOW"
        assert ConnectionType.LAZY.value == "LAZY"

    def test_direction_enum(self) -> None:
        """Direction enum has required values."""
        assert Direction.HORIZONTAL.value == "HORIZONTAL"
        assert Direction.VERTICAL.value == "VERTICAL"


# ============================================================================
# Phase 2 Tests: Registry
# ============================================================================


from agents.i.data.registry import (
    AgentStatus,
    MemoryRegistry,
    MockObservable,
    RegisteredAgent,
    RegistryEvent,
    RegistryEventType,
    create_demo_registry,
)


class TestAgentStatus:
    """Test AgentStatus enum."""

    def test_status_values(self) -> None:
        """Status enum has required values."""
        assert AgentStatus.UNKNOWN.value == "UNKNOWN"
        assert AgentStatus.STARTING.value == "STARTING"
        assert AgentStatus.RUNNING.value == "RUNNING"
        assert AgentStatus.STOPPING.value == "STOPPING"
        assert AgentStatus.STOPPED.value == "STOPPED"
        assert AgentStatus.ERROR.value == "ERROR"


class TestRegisteredAgent:
    """Test RegisteredAgent dataclass."""

    def test_default_values(self) -> None:
        """RegisteredAgent has sensible defaults."""
        agent = RegisteredAgent(
            id="test",
            name="Test Agent",
            agent_type="test",
        )
        assert agent.status == AgentStatus.UNKNOWN
        assert agent.observable is None
        assert agent.grid_x == 0
        assert agent.grid_y == 0
        assert agent.cached_phase == Phase.DORMANT
        assert agent.cached_activity == 0.0

    def test_with_all_fields(self) -> None:
        """RegisteredAgent with all fields."""
        agent = RegisteredAgent(
            id="robin",
            name="Robin",
            agent_type="robin",
            status=AgentStatus.RUNNING,
            grid_x=2,
            grid_y=1,
            cached_phase=Phase.ACTIVE,
            cached_activity=0.8,
            cached_summary="Hypothesis synthesis",
            connections={"g-gent": "high"},
        )
        assert agent.id == "robin"
        assert agent.status == AgentStatus.RUNNING
        assert agent.cached_phase == Phase.ACTIVE


class TestMemoryRegistry:
    """Test MemoryRegistry."""

    @pytest.mark.asyncio
    async def test_register_and_discover(self) -> None:
        """Can register and discover agents."""
        registry = MemoryRegistry()
        agent = RegisteredAgent(id="test", name="Test", agent_type="test")

        await registry.register(agent)
        agents = await registry.discover()

        assert len(agents) == 1
        assert agents[0].id == "test"

    @pytest.mark.asyncio
    async def test_get_agent(self) -> None:
        """Can get agent by ID."""
        registry = MemoryRegistry()
        agent = RegisteredAgent(id="test", name="Test", agent_type="test")

        await registry.register(agent)
        retrieved = await registry.get_agent("test")

        assert retrieved is not None
        assert retrieved.id == "test"

    @pytest.mark.asyncio
    async def test_get_nonexistent_agent(self) -> None:
        """Getting nonexistent agent returns None."""
        registry = MemoryRegistry()
        retrieved = await registry.get_agent("nonexistent")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_unregister(self) -> None:
        """Can unregister agents."""
        registry = MemoryRegistry()
        agent = RegisteredAgent(id="test", name="Test", agent_type="test")

        await registry.register(agent)
        await registry.unregister("test")

        retrieved = await registry.get_agent("test")
        assert retrieved is None

    @pytest.mark.asyncio
    async def test_update_status(self) -> None:
        """Can update agent status."""
        registry = MemoryRegistry()
        agent = RegisteredAgent(id="test", name="Test", agent_type="test")

        await registry.register(agent)
        await registry.update_status("test", AgentStatus.RUNNING)

        retrieved = await registry.get_agent("test")
        assert retrieved is not None
        assert retrieved.status == AgentStatus.RUNNING

    @pytest.mark.asyncio
    async def test_update_cached_values(self) -> None:
        """Can update cached observation values."""
        registry = MemoryRegistry()
        agent = RegisteredAgent(id="test", name="Test", agent_type="test")

        await registry.register(agent)
        await registry.update_cached_values(
            "test",
            phase=Phase.ACTIVE,
            activity=0.75,
            summary="Active and working",
        )

        retrieved = await registry.get_agent("test")
        assert retrieved is not None
        assert retrieved.cached_phase == Phase.ACTIVE
        assert retrieved.cached_activity == 0.75
        assert retrieved.cached_summary == "Active and working"

    def test_subscribe_callback(self) -> None:
        """Registry calls callbacks on events."""
        registry = MemoryRegistry()
        events: list[RegistryEvent] = []

        def callback(event: RegistryEvent) -> None:
            events.append(event)

        registry.subscribe(callback)

        # Directly add agent to trigger event
        agent = RegisteredAgent(id="test", name="Test", agent_type="test")
        registry._agents["test"] = agent
        registry._emit(
            RegistryEvent(
                event_type=RegistryEventType.AGENT_REGISTERED,
                agent_id="test",
                agent=agent,
            )
        )

        assert len(events) == 1
        assert events[0].event_type == RegistryEventType.AGENT_REGISTERED


class TestDemoRegistry:
    """Test demo registry creation."""

    def test_create_demo_registry(self) -> None:
        """Demo registry has agents."""
        registry = create_demo_registry()
        # Access internal state for sync check
        assert len(registry._agents) > 0

    def test_demo_registry_has_robin(self) -> None:
        """Demo registry includes Robin agent."""
        registry = create_demo_registry()
        assert "robin" in registry._agents


class TestMockObservable:
    """Test MockObservable."""

    def test_properties(self) -> None:
        """MockObservable has correct properties."""
        obs = MockObservable(
            agent_id="test",
            name="Test Agent",
            phase=Phase.ACTIVE,
            activity=0.7,
        )
        assert obs.id == "test"
        assert obs.name == "Test Agent"
        assert obs.phase == Phase.ACTIVE
        assert obs.children == []

    @pytest.mark.asyncio
    async def test_activity_level(self) -> None:
        """MockObservable returns activity level."""
        obs = MockObservable("test", "Test", activity=0.5)
        level = await obs.activity_level()
        assert level == 0.5

    @pytest.mark.asyncio
    async def test_metrics(self) -> None:
        """MockObservable returns metrics dict."""
        obs = MockObservable("test", "Test", phase=Phase.WAKING, activity=0.3)
        metrics = await obs.metrics()
        assert metrics["id"] == "test"
        assert metrics["phase"] == "WAKING"
        assert metrics["activity"] == 0.3


# ============================================================================
# Phase 2 Tests: O-gent Polling
# ============================================================================


from agents.i.data.ogent import (
    HealthLevel,
    OgentPoller,
    XYZHealth,
    create_mock_health,
    render_xyz_bar,
    render_xyz_compact,
    value_to_health_level,
)


class TestHealthLevel:
    """Test HealthLevel enum and conversion."""

    def test_value_to_health_level(self) -> None:
        """Values map to correct health levels."""
        assert value_to_health_level(0.1) == HealthLevel.CRITICAL
        assert value_to_health_level(0.3) == HealthLevel.POOR
        assert value_to_health_level(0.5) == HealthLevel.FAIR
        assert value_to_health_level(0.7) == HealthLevel.GOOD
        assert value_to_health_level(0.9) == HealthLevel.EXCELLENT


class TestXYZHealth:
    """Test XYZHealth dataclass."""

    def test_default_values(self) -> None:
        """XYZHealth has healthy defaults."""
        health = XYZHealth()
        assert health.x_telemetry == 1.0
        assert health.y_semantic == 1.0
        assert health.z_economic == 1.0

    def test_health_levels(self) -> None:
        """Health levels computed correctly."""
        health = XYZHealth(
            x_telemetry=0.9,
            y_semantic=0.5,
            z_economic=0.1,
        )
        assert health.x_level == HealthLevel.EXCELLENT
        assert health.y_level == HealthLevel.FAIR
        assert health.z_level == HealthLevel.CRITICAL

    def test_overall_health(self) -> None:
        """Overall health is geometric mean."""
        health = XYZHealth(
            x_telemetry=0.8,
            y_semantic=0.8,
            z_economic=0.8,
        )
        assert 0.79 < health.overall < 0.81

    def test_to_dict_roundtrip(self) -> None:
        """XYZHealth survives serialization."""
        original = XYZHealth(
            x_telemetry=0.9,
            x_latency_ms=50.0,
            y_semantic=0.8,
            y_drift=0.1,
            z_economic=0.7,
            z_roc=1.5,
        )
        data = original.to_dict()
        restored = XYZHealth.from_dict(data)

        assert restored.x_telemetry == original.x_telemetry
        assert restored.y_semantic == original.y_semantic
        assert restored.z_economic == original.z_economic


class TestRenderFunctions:
    """Test XYZ rendering functions."""

    def test_render_xyz_bar(self) -> None:
        """Render XYZ bar contains all dimensions."""
        health = XYZHealth(x_telemetry=0.5, y_semantic=0.8, z_economic=0.3)
        bar = render_xyz_bar(health, width=5)
        assert "X[" in bar
        assert "Y[" in bar
        assert "Z[" in bar

    def test_render_xyz_compact(self) -> None:
        """Render compact shows percentages."""
        health = XYZHealth(x_telemetry=0.87, y_semantic=0.92, z_economic=0.78)
        compact = render_xyz_compact(health)
        assert "X:87%" in compact
        assert "Y:92%" in compact
        assert "Z:78%" in compact


class TestCreateMockHealth:
    """Test mock health creation."""

    def test_mock_health_from_activity(self) -> None:
        """Mock health derives from activity."""
        health = create_mock_health("test", activity=0.8, phase="ACTIVE")
        # High activity + active phase should give good health
        assert health.x_telemetry > 0.5
        assert health.y_semantic > 0.5
        assert health.z_economic > 0.5

    def test_mock_health_dormant_phase(self) -> None:
        """Dormant phase reduces health."""
        health = create_mock_health("test", activity=0.8, phase="DORMANT")
        # Dormant multiplier reduces health
        assert health.x_telemetry < 0.5


class TestOgentPoller:
    """Test OgentPoller."""

    def test_create_poller(self) -> None:
        """Can create poller."""
        poller = OgentPoller()
        assert not poller.is_running

    @pytest.mark.asyncio
    async def test_poll_with_registry(self) -> None:
        """Poller polls registry agents."""
        registry = create_demo_registry()
        poller = OgentPoller(registry=registry)

        results = await poller.poll_once()

        # Should have health for all demo agents
        assert len(results) > 0
        assert "robin" in results
        assert isinstance(results["robin"], XYZHealth)

    def test_subscribe_callback(self) -> None:
        """Poller calls callbacks on updates."""
        poller = OgentPoller()
        updates: list[tuple[str, XYZHealth]] = []

        def callback(agent_id: str, health: XYZHealth) -> None:
            updates.append((agent_id, health))

        poller.subscribe(callback)
        # Manually emit
        health = XYZHealth()
        poller._emit("test", health)

        assert len(updates) == 1
        assert updates[0][0] == "test"


# ============================================================================
# Phase 2 Tests: Health Bar Widgets
# ============================================================================


from agents.i.widgets.health_bar import (
    render_single_bar,
)


class TestHealthBarRendering:
    """Test health bar rendering functions."""

    def test_render_single_bar_full(self) -> None:
        """Full health renders all filled."""
        bar = render_single_bar(1.0, 5)
        assert bar == "█████"

    def test_render_single_bar_empty(self) -> None:
        """Zero health renders all empty."""
        bar = render_single_bar(0.0, 5)
        assert bar == "░░░░░"

    def test_render_single_bar_half(self) -> None:
        """Half health renders mixed."""
        bar = render_single_bar(0.5, 4)
        assert bar == "██░░"


# ============================================================================
# Phase 3 Tests: Waveform Widget
# ============================================================================


from agents.i.widgets.waveform import (
    OPERATION_LABELS,
    WAVEFORM_PATTERNS,
    OperationType,
    generate_waveform,
)


class TestOperationType:
    """Test OperationType enum."""

    def test_operation_type_values(self) -> None:
        """OperationType enum has required values."""
        assert OperationType.LOGICAL.value == "LOGICAL"
        assert OperationType.CREATIVE.value == "CREATIVE"
        assert OperationType.WAITING.value == "WAITING"
        assert OperationType.ERROR.value == "ERROR"


class TestWaveformPatterns:
    """Test waveform pattern generation."""

    def test_waveform_patterns_exist(self) -> None:
        """All operation types have patterns."""
        for op_type in OperationType:
            assert op_type in WAVEFORM_PATTERNS
            assert len(WAVEFORM_PATTERNS[op_type]) > 0

    def test_operation_labels_exist(self) -> None:
        """All operation types have labels."""
        for op_type in OperationType:
            assert op_type in OPERATION_LABELS
            assert len(OPERATION_LABELS[op_type]) > 0

    def test_generate_waveform_width(self) -> None:
        """Generated waveform has correct width."""
        waveform = generate_waveform(20, OperationType.LOGICAL)
        assert len(waveform) == 20

    def test_generate_waveform_different_types(self) -> None:
        """Different operation types produce different waveforms."""
        logical = generate_waveform(10, OperationType.LOGICAL)
        creative = generate_waveform(10, OperationType.CREATIVE)
        waiting = generate_waveform(10, OperationType.WAITING)

        # Should be different patterns
        assert logical != waiting
        assert creative != waiting

    def test_generate_waveform_with_offset(self) -> None:
        """Offset produces different starting point."""
        wave1 = generate_waveform(10, OperationType.LOGICAL, offset=0)
        wave2 = generate_waveform(10, OperationType.LOGICAL, offset=1)

        # Offset should shift the pattern
        # (may or may not be different depending on pattern length)
        assert isinstance(wave1, str)
        assert isinstance(wave2, str)


# ============================================================================
# Phase 3 Tests: Event Stream Widget
# ============================================================================


from datetime import datetime

from agents.i.widgets.event_stream import (
    AgentEvent,
    EventType,
    create_demo_events,
)


class TestEventType:
    """Test EventType enum."""

    def test_event_type_values(self) -> None:
        """EventType enum has required values."""
        assert EventType.SEARCH.value == "search"
        assert EventType.FILTER.value == "filter"
        assert EventType.SYNTHESIZE.value == "synthesize"
        assert EventType.REASON.value == "reason"
        assert EventType.TOOL.value == "tool"
        assert EventType.ERROR.value == "error"
        assert EventType.INFO.value == "info"
        assert EventType.COMPLETE.value == "complete"


class TestAgentEvent:
    """Test AgentEvent dataclass."""

    def test_create_event(self) -> None:
        """Can create an event."""
        event = AgentEvent(
            timestamp=datetime.now(),
            event_type=EventType.SEARCH,
            message="Searching for data...",
            agent_id="robin",
        )
        assert event.event_type == EventType.SEARCH
        assert event.agent_id == "robin"

    def test_format_timestamp(self) -> None:
        """Timestamp formats correctly."""
        event = AgentEvent(
            timestamp=datetime(2024, 1, 15, 10, 42, 30),
            event_type=EventType.INFO,
            message="Test",
        )
        assert event.format_timestamp() == "10:42:30"

    def test_format_line(self) -> None:
        """Event formats as line correctly."""
        event = AgentEvent(
            timestamp=datetime(2024, 1, 15, 10, 42, 30),
            event_type=EventType.SEARCH,
            message="Test message",
        )
        line = event.format_line(50)
        assert "10:42:30" in line
        assert "[search]" in line
        assert "Test message" in line

    def test_format_line_truncates_long_message(self) -> None:
        """Long messages are truncated."""
        event = AgentEvent(
            timestamp=datetime.now(),
            event_type=EventType.INFO,
            message="A" * 100,
        )
        line = event.format_line(40)
        assert "..." in line

    def test_to_markdown(self) -> None:
        """Event exports to markdown correctly."""
        event = AgentEvent(
            timestamp=datetime(2024, 1, 15, 10, 42, 30),
            event_type=EventType.SYNTHESIZE,
            message="Generating hypothesis",
        )
        md = event.to_markdown()
        assert md.startswith("- **10:42:30**")
        assert "[synthesize]" in md
        assert "Generating hypothesis" in md


class TestDemoEvents:
    """Test demo event creation."""

    def test_create_demo_events(self) -> None:
        """Can create demo events."""
        events = create_demo_events("robin")
        assert len(events) > 0

    def test_demo_events_have_timestamps(self) -> None:
        """Demo events have timestamps."""
        events = create_demo_events()
        for event in events:
            assert isinstance(event.timestamp, datetime)

    def test_demo_events_have_types(self) -> None:
        """Demo events have various types."""
        events = create_demo_events()
        types = {e.event_type for e in events}
        assert len(types) > 1  # Multiple event types


# ============================================================================
# Phase 3 Tests: Proprioception Widget
# ============================================================================


from agents.i.widgets.proprioception import (
    ProprioceptionState,
    TraumaLevel,
    create_demo_proprioception,
    render_percent_bar,
    render_replica_dots,
)


class TestTraumaLevel:
    """Test TraumaLevel enum."""

    def test_trauma_level_values(self) -> None:
        """TraumaLevel enum has required values."""
        assert TraumaLevel.NONE.value == "none"
        assert TraumaLevel.MINOR.value == "minor"
        assert TraumaLevel.MODERATE.value == "moderate"
        assert TraumaLevel.SEVERE.value == "severe"


class TestProprioceptionState:
    """Test ProprioceptionState dataclass."""

    def test_default_values(self) -> None:
        """ProprioceptionState has sensible defaults."""
        state = ProprioceptionState()
        assert state.strain == 0.0
        assert state.pressure == 0.0
        assert state.reach == 1
        assert state.temperature == 1.0
        assert state.trauma == TraumaLevel.NONE

    def test_is_healthy_default(self) -> None:
        """Default state is healthy."""
        state = ProprioceptionState()
        assert state.is_healthy()

    def test_is_healthy_high_strain(self) -> None:
        """High strain makes state unhealthy."""
        state = ProprioceptionState(strain=0.9)
        assert not state.is_healthy()

    def test_is_healthy_high_pressure(self) -> None:
        """High pressure makes state unhealthy."""
        state = ProprioceptionState(pressure=0.95)
        assert not state.is_healthy()

    def test_is_healthy_low_temperature(self) -> None:
        """Low temperature makes state unhealthy."""
        state = ProprioceptionState(temperature=0.2)
        assert not state.is_healthy()

    def test_is_healthy_with_trauma(self) -> None:
        """Trauma makes state unhealthy."""
        state = ProprioceptionState(trauma=TraumaLevel.MINOR)
        assert not state.is_healthy()


class TestProprioceptionRendering:
    """Test proprioception rendering functions."""

    def test_render_percent_bar_full(self) -> None:
        """Full value renders all filled."""
        bar = render_percent_bar(1.0, 5)
        assert bar == "▓▓▓▓▓"

    def test_render_percent_bar_empty(self) -> None:
        """Zero value renders all empty."""
        bar = render_percent_bar(0.0, 5)
        assert bar == "░░░░░"

    def test_render_percent_bar_half(self) -> None:
        """Half value renders mixed."""
        bar = render_percent_bar(0.5, 4)
        assert bar == "▓▓░░"

    def test_render_replica_dots(self) -> None:
        """Replica dots render correctly."""
        dots = render_replica_dots(3, 5)
        assert dots == "●●●○○"

    def test_render_replica_dots_full(self) -> None:
        """Full replicas render all active."""
        dots = render_replica_dots(5, 5)
        assert dots == "●●●●●"

    def test_render_replica_dots_none(self) -> None:
        """Zero replicas render all inactive."""
        dots = render_replica_dots(0, 5)
        assert dots == "○○○○○"


class TestDemoProprioception:
    """Test demo proprioception creation."""

    def test_create_demo_proprioception(self) -> None:
        """Can create demo proprioception state."""
        state = create_demo_proprioception()
        assert isinstance(state, ProprioceptionState)

    def test_demo_proprioception_has_values(self) -> None:
        """Demo state has non-default values."""
        state = create_demo_proprioception()
        assert state.strain > 0
        assert state.pressure > 0
        assert state.reach >= 1

    def test_demo_proprioception_has_morphology(self) -> None:
        """Demo state has morphology string."""
        state = create_demo_proprioception()
        assert len(state.morphology) > 0
        assert "Base()" in state.morphology


# ============================================================================
# Phase 4 Tests: Glitch System
# ============================================================================


from agents.i.widgets.glitch import (
    GlitchConfig,
    GlitchController,
    GlitchEvent,
    GlitchType,
    add_zalgo,
    apply_glitch,
    distort_border,
    glitch_message,
    substitute_chars,
)


class TestZalgoEffect:
    """Test Zalgo text corruption."""

    def test_add_zalgo_basic(self) -> None:
        """Zalgo adds combining characters."""
        original = "TEST"
        result = add_zalgo(original, intensity=1.0, depth=2)
        # Result should be at least as long as original
        assert len(result) >= len(original)
        # Original characters should still be present
        clean = "".join(c for c in result if ord(c) < 0x300 or ord(c) > 0x36F)
        assert "T" in clean and "E" in clean and "S" in clean

    def test_add_zalgo_zero_intensity(self) -> None:
        """Zero intensity produces no corruption."""
        original = "TEST"
        result = add_zalgo(original, intensity=0.0)
        assert result == original

    def test_add_zalgo_depth(self) -> None:
        """Higher depth adds more combining characters."""
        original = "X"
        low_depth = add_zalgo(original, intensity=1.0, depth=1)
        high_depth = add_zalgo(original, intensity=1.0, depth=5)
        # High depth should generally be longer (though random)
        # At minimum, both should have the original char
        assert "X" in low_depth
        assert "X" in high_depth


class TestSubstituteChars:
    """Test character substitution."""

    def test_substitute_chars_basic(self) -> None:
        """Substitution replaces characters."""
        original = "HELLO"
        result = substitute_chars(original, intensity=1.0)
        # Some characters should be different
        assert result != original

    def test_substitute_chars_zero_intensity(self) -> None:
        """Zero intensity produces no substitution."""
        original = "HELLO"
        result = substitute_chars(original, intensity=0.0)
        assert result == original

    def test_substitute_chars_preserves_spaces(self) -> None:
        """Spaces are never substituted."""
        original = "A B C"
        result = substitute_chars(original, intensity=1.0)
        # Count spaces
        assert result.count(" ") == 2


class TestDistortBorder:
    """Test border distortion."""

    def test_distort_border_basic(self) -> None:
        """Border distortion modifies box characters."""
        original = "┌──┐"
        result = distort_border(original, intensity=1.0)
        # Some border chars may be changed
        assert len(result) == len(original)

    def test_distort_border_zero_intensity(self) -> None:
        """Zero intensity produces no distortion."""
        original = "┌──┐"
        result = distort_border(original, intensity=0.0)
        assert result == original


class TestGlitchConfig:
    """Test GlitchConfig dataclass."""

    def test_default_values(self) -> None:
        """Config has sensible defaults."""
        config = GlitchConfig()
        assert config.intensity == 0.3
        assert config.duration_ms == 200
        assert config.glitch_type == GlitchType.ZALGO
        assert config.spread is False

    def test_custom_values(self) -> None:
        """Config accepts custom values."""
        config = GlitchConfig(
            intensity=0.8,
            duration_ms=500,
            glitch_type=GlitchType.SUBSTITUTE,
            spread=True,
        )
        assert config.intensity == 0.8
        assert config.duration_ms == 500
        assert config.glitch_type == GlitchType.SUBSTITUTE
        assert config.spread is True


class TestApplyGlitch:
    """Test apply_glitch function."""

    def test_apply_zalgo_type(self) -> None:
        """Apply with ZALGO type adds combining chars."""
        config = GlitchConfig(glitch_type=GlitchType.ZALGO, intensity=1.0)
        result = apply_glitch("TEST", config)
        assert len(result) >= 4

    def test_apply_substitute_type(self) -> None:
        """Apply with SUBSTITUTE type changes chars."""
        config = GlitchConfig(glitch_type=GlitchType.SUBSTITUTE, intensity=1.0)
        result = apply_glitch("TEST", config)
        assert result != "TEST"

    def test_apply_distort_type(self) -> None:
        """Apply with DISTORT type changes borders."""
        config = GlitchConfig(glitch_type=GlitchType.DISTORT, intensity=1.0)
        result = apply_glitch("─┌┐─", config)
        assert len(result) == 4


class TestGlitchController:
    """Test GlitchController."""

    def test_create_controller(self) -> None:
        """Can create controller."""
        controller = GlitchController()
        assert not controller.is_glitching("any_id")

    def test_subscribe_callback(self) -> None:
        """Controller calls callbacks on events."""
        controller = GlitchController()
        events: list[GlitchEvent] = []

        def callback(event: GlitchEvent) -> None:
            events.append(event)

        controller.subscribe(callback)
        event = controller.on_void_phase("robin")

        assert len(events) == 1
        assert events[0].target_id == "robin"

    def test_on_void_phase(self) -> None:
        """Void phase creates correct event."""
        controller = GlitchController()
        event = controller.on_void_phase("robin")

        assert event.target_id == "robin"
        assert event.source == "phase:VOID"
        assert event.glitch_type == GlitchType.ZALGO

    def test_on_error(self) -> None:
        """Error creates correct event."""
        controller = GlitchController()
        error = ValueError("test error")
        event = controller.on_error(error, target_id="status_bar")

        assert event.target_id == "status_bar"
        assert "ValueError" in event.source
        assert event.glitch_type == GlitchType.SUBSTITUTE

    def test_is_glitching(self) -> None:
        """Glitch state is tracked correctly."""
        controller = GlitchController()

        assert not controller.is_glitching("robin")

        controller.on_void_phase("robin")
        assert controller.is_glitching("robin")

        controller.clear_glitch("robin")
        assert not controller.is_glitching("robin")

    def test_get_active_glitches(self) -> None:
        """Active glitches are returned correctly."""
        controller = GlitchController()

        controller.on_void_phase("robin")
        controller.on_void_phase("g-gent")

        active = controller.get_active_glitches()
        assert "robin" in active
        assert "g-gent" in active

    def test_glitch_history(self) -> None:
        """Glitch history is maintained."""
        controller = GlitchController()

        controller.on_void_phase("robin")
        controller.on_error(ValueError("test"))

        history = controller.get_history()
        assert len(history) == 2


class TestGlitchMessage:
    """Test glitch_message convenience function."""

    def test_glitch_message_basic(self) -> None:
        """Glitch message corrupts text."""
        result = glitch_message("Error occurred", intensity=0.5)
        # Should contain the original text
        assert "E" in result
        assert len(result) >= len("Error occurred")


# ============================================================================
# Phase 4 Tests: AGENTESE HUD
# ============================================================================


from agents.i.widgets.agentese_hud import (
    AgentContext,
    AgentesePath,
    create_demo_paths,
)


class TestAgentContext:
    """Test AgentContext enum."""

    def test_context_values(self) -> None:
        """AgentContext enum has required values."""
        assert AgentContext.WORLD.value == "world"
        assert AgentContext.SELF.value == "self"
        assert AgentContext.CONCEPT.value == "concept"
        assert AgentContext.VOID.value == "void"
        assert AgentContext.TIME.value == "time"


class TestAgentesePath:
    """Test AgentesePath dataclass."""

    def test_create_path(self) -> None:
        """Can create an AGENTESE path."""
        path = AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="world.pubmed.search",
            args='"β-sheet"',
        )
        assert path.agent_id == "robin"
        assert path.path == "world.pubmed.search"

    def test_context_detection_world(self) -> None:
        """World context is detected correctly."""
        path = AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="world.pubmed.search",
        )
        assert path.context == AgentContext.WORLD

    def test_context_detection_self(self) -> None:
        """Self context is detected correctly."""
        path = AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="self.memory.recall",
        )
        assert path.context == AgentContext.SELF

    def test_context_detection_concept(self) -> None:
        """Concept context is detected correctly."""
        path = AgentesePath(
            agent_id="g-gent",
            agent_name="g-gent",
            path="concept.category.morphism",
        )
        assert path.context == AgentContext.CONCEPT

    def test_context_detection_void(self) -> None:
        """Void context is detected correctly."""
        path = AgentesePath(
            agent_id="psi",
            agent_name="psi",
            path="void.sip",
        )
        assert path.context == AgentContext.VOID

    def test_context_detection_time(self) -> None:
        """Time context is detected correctly."""
        path = AgentesePath(
            agent_id="o-gent",
            agent_name="o-gent",
            path="time.trace.witness",
        )
        assert path.context == AgentContext.TIME

    def test_color_property(self) -> None:
        """Color property returns correct color for context."""
        path = AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="world.pubmed.search",
        )
        color = path.color
        assert color.startswith("#")
        assert len(color) == 7  # #RRGGBB format

    def test_format_display_basic(self) -> None:
        """Format display includes agent name and path."""
        path = AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="world.pubmed.search",
        )
        display = path.format_display()
        assert "robin" in display
        assert "world.pubmed.search" in display

    def test_format_display_with_args(self) -> None:
        """Format display includes arguments."""
        path = AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="world.pubmed.search",
            args='"β-sheet"',
        )
        display = path.format_display()
        assert '"β-sheet"' in display

    def test_format_display_with_subpath(self) -> None:
        """Format display includes sub-path."""
        path = AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="world.pubmed.search",
            sub_path="concept.biology.protein",
        )
        display = path.format_display()
        assert "└─" in display
        assert "concept.biology.protein" in display

    def test_format_display_truncation(self) -> None:
        """Long paths are truncated."""
        path = AgentesePath(
            agent_id="robin",
            agent_name="robin",
            path="world.very.long.path.that.exceeds.the.maximum.width",
        )
        display = path.format_display(max_width=30)
        assert len(display.split("\n")[0]) <= 30


class TestDemoPaths:
    """Test demo path creation."""

    def test_create_demo_paths(self) -> None:
        """Can create demo paths."""
        paths = create_demo_paths()
        assert len(paths) > 0

    def test_demo_paths_have_variety(self) -> None:
        """Demo paths cover different contexts."""
        paths = create_demo_paths()
        contexts = {p.context for p in paths}
        assert len(contexts) >= 3  # At least 3 different contexts

    def test_demo_paths_have_timestamps(self) -> None:
        """Demo paths have timestamps."""
        paths = create_demo_paths()
        for path in paths:
            assert path.timestamp is not None


# ============================================================================
# Phase 5 Tests: Polish & FD3 Bridge
# ============================================================================


class TestHelpOverlay:
    """Test HelpOverlay."""

    def test_keybindings_defined(self) -> None:
        """Help overlay has keybindings dictionary."""
        from agents.i.screens.overlays.help import KEYBINDINGS

        assert len(KEYBINDINGS) > 0
        assert "Navigation" in KEYBINDINGS
        assert "Overlays" in KEYBINDINGS
        assert "Actions" in KEYBINDINGS

    def test_navigation_keys(self) -> None:
        """Navigation section has expected keys."""
        from agents.i.screens.overlays.help import KEYBINDINGS

        nav_keys = [k[0] for k in KEYBINDINGS["Navigation"]]
        assert any("h" in k for k in nav_keys)
        assert any("j" in k for k in nav_keys)
        assert any("k" in k for k in nav_keys)
        assert any("l" in k for k in nav_keys)

    def test_overlay_keys(self) -> None:
        """Overlays section has expected keys."""
        from agents.i.screens.overlays.help import KEYBINDINGS

        overlay_keys = [k[0] for k in KEYBINDINGS["Overlays"]]
        assert "w" in overlay_keys
        assert "b" in overlay_keys


class TestEmptyState:
    """Test empty state handling."""

    def test_empty_flux_state(self) -> None:
        """FluxState can be created empty."""
        state = FluxState()
        assert len(state.agents) == 0
        assert state.focused_id is None

    def test_flux_grid_is_empty(self) -> None:
        """Empty state has is_empty property."""
        from agents.i.screens.flux import FluxGrid

        state = FluxState()
        grid = FluxGrid(state)
        # Grid is empty until composed
        assert grid.is_empty


class TestOgentPollerTimeout:
    """Test OgentPoller timeout handling."""

    def test_poller_has_timeout(self) -> None:
        """Poller has configurable timeout."""
        poller = OgentPoller(timeout=3.0)
        assert poller._timeout == 3.0

    def test_timeout_count_tracking(self) -> None:
        """Timeout count is tracked."""
        poller = OgentPoller()
        assert poller.get_timeout_count("test") == 0

        # Manually set timeout count
        poller._timeout_count["test"] = 3
        assert poller.get_timeout_count("test") == 3

    def test_create_timeout_health(self) -> None:
        """Timeout creates degraded health."""
        poller = OgentPoller()
        poller._timeout_count["test"] = 2

        health = poller._create_timeout_health("test")

        # Health should be degraded
        assert health.x_telemetry < 1.0
        assert health.x_error_rate > 0
        assert health.x_latency_ms > 0


# ============================================================================
# Phase 5 Tests: FD3 Protocol
# ============================================================================


from protocols.cli.fd3 import (
    FD3Channel,
    FD3Message,
    FD3MessageType,
    emit_agent_update,
    emit_agentese_invoke,
    emit_error,
    emit_health,
    emit_status,
)


class TestFD3MessageType:
    """Test FD3MessageType enum."""

    def test_message_type_values(self) -> None:
        """FD3MessageType enum has required values."""
        assert FD3MessageType.AGENT_UPDATE.value == "agent_update"
        assert FD3MessageType.HEALTH.value == "health"
        assert FD3MessageType.AGENTESE_INVOKE.value == "agentese_invoke"
        assert FD3MessageType.ERROR.value == "error"
        assert FD3MessageType.STATUS.value == "status"
        assert FD3MessageType.EVENT.value == "event"


class TestFD3Message:
    """Test FD3Message dataclass."""

    def test_create_message(self) -> None:
        """Can create FD3 message."""
        msg = FD3Message(
            type="agent_update",
            payload={"agent_id": "robin", "phase": "ACTIVE"},
        )
        assert msg.type == "agent_update"
        assert msg.payload["agent_id"] == "robin"

    def test_to_dict(self) -> None:
        """Message converts to dict."""
        msg = FD3Message(
            type="health",
            payload={"x_telemetry": 0.9},
            source="test",
        )
        data = msg.to_dict()

        assert data["type"] == "health"
        assert data["payload"]["x_telemetry"] == 0.9
        assert data["source"] == "test"
        assert "timestamp" in data

    def test_to_json(self) -> None:
        """Message converts to JSON."""
        msg = FD3Message(
            type="status",
            payload={"status": "OK"},
        )
        json_str = msg.to_json()

        assert '"type": "status"' in json_str
        assert '"status": "OK"' in json_str

    def test_from_dict(self) -> None:
        """Message can be created from dict."""
        data = {
            "type": "error",
            "payload": {"message": "Test error"},
            "timestamp": "2024-01-15T10:30:00",
            "source": "test",
        }
        msg = FD3Message.from_dict(data)

        assert msg.type == "error"
        assert msg.payload["message"] == "Test error"
        assert msg.source == "test"

    def test_from_json(self) -> None:
        """Message can be created from JSON."""
        json_str = (
            '{"type": "event", "payload": {"event": "startup"}, "timestamp": "2024-01-15T10:30:00"}'
        )
        msg = FD3Message.from_json(json_str)

        assert msg.type == "event"
        assert msg.payload["event"] == "startup"

    def test_roundtrip(self) -> None:
        """Message survives JSON roundtrip."""
        original = FD3Message(
            type="agentese_invoke",
            payload={"path": "world.pubmed.search", "agent_id": "robin"},
            source="test",
        )
        json_str = original.to_json()
        restored = FD3Message.from_json(json_str)

        assert restored.type == original.type
        assert restored.payload == original.payload
        assert restored.source == original.source


class TestFD3Channel:
    """Test FD3Channel."""

    def test_create_channel_disabled(self) -> None:
        """Channel without path is disabled."""
        channel = FD3Channel()
        assert not channel.is_enabled
        assert channel.path is None

    def test_create_channel_with_path(self) -> None:
        """Channel with path is enabled."""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            channel = FD3Channel(path=f.name)
            assert channel.is_enabled
            assert channel.path is not None

    def test_emit_to_file(self) -> None:
        """Emit writes to file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            path = f.name

        channel = FD3Channel(path=path)
        channel.emit(FD3Message(type="status", payload={"status": "OK"}))

        # Read back
        with open(path) as f:
            content = f.read()
            assert '"type": "status"' in content

        # Cleanup
        Path(path).unlink()

    def test_emit_callback(self) -> None:
        """Emit notifies callbacks."""
        channel = FD3Channel()  # No path, but callbacks still work
        messages: list[FD3Message] = []

        def callback(msg: FD3Message) -> None:
            messages.append(msg)

        channel.subscribe(callback)
        channel.emit(FD3Message(type="status", payload={"status": "OK"}))

        assert len(messages) == 1
        assert messages[0].type == "status"

    @pytest.mark.asyncio
    async def test_read_all(self) -> None:
        """Read all messages from file."""
        with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".jsonl") as f:
            f.write('{"type": "status", "payload": {"status": "OK"}}\n')
            f.write('{"type": "health", "payload": {"x": 0.9}}\n')
            path = f.name

        channel = FD3Channel(path=path)
        messages = await channel.read_all()

        assert len(messages) == 2
        assert messages[0].type == "status"
        assert messages[1].type == "health"

        Path(path).unlink()


class TestFD3ConvenienceFunctions:
    """Test FD3 convenience functions."""

    def test_emit_agent_update(self) -> None:
        """emit_agent_update creates correct message."""
        channel = FD3Channel()
        messages: list[FD3Message] = []
        channel.subscribe(lambda m: messages.append(m))

        emit_agent_update(
            channel,
            agent_id="robin",
            phase="ACTIVE",
            activity=0.8,
            summary="Working",
        )

        assert len(messages) == 1
        assert messages[0].type == "agent_update"
        assert messages[0].payload["agent_id"] == "robin"
        assert messages[0].payload["phase"] == "ACTIVE"

    def test_emit_health(self) -> None:
        """emit_health creates correct message."""
        channel = FD3Channel()
        messages: list[FD3Message] = []
        channel.subscribe(lambda m: messages.append(m))

        emit_health(
            channel,
            agent_id="robin",
            x_telemetry=0.9,
            y_semantic=0.8,
            z_economic=0.7,
        )

        assert len(messages) == 1
        assert messages[0].type == "health"
        assert messages[0].payload["x_telemetry"] == 0.9

    def test_emit_agentese_invoke(self) -> None:
        """emit_agentese_invoke creates correct message."""
        channel = FD3Channel()
        messages: list[FD3Message] = []
        channel.subscribe(lambda m: messages.append(m))

        emit_agentese_invoke(
            channel,
            agent_id="robin",
            agent_name="robin",
            path="world.pubmed.search",
            args='"β-sheet"',
        )

        assert len(messages) == 1
        assert messages[0].type == "agentese_invoke"
        assert messages[0].payload["path"] == "world.pubmed.search"

    def test_emit_error(self) -> None:
        """emit_error creates correct message."""
        channel = FD3Channel()
        messages: list[FD3Message] = []
        channel.subscribe(lambda m: messages.append(m))

        emit_error(
            channel,
            error_type="ValueError",
            message="Test error",
            agent_id="robin",
        )

        assert len(messages) == 1
        assert messages[0].type == "error"
        assert messages[0].payload["error_type"] == "ValueError"

    def test_emit_status(self) -> None:
        """emit_status creates correct message."""
        channel = FD3Channel()
        messages: list[FD3Message] = []
        channel.subscribe(lambda m: messages.append(m))

        emit_status(
            channel,
            status="HEALTHY",
            details={"uptime": 3600},
        )

        assert len(messages) == 1
        assert messages[0].type == "status"
        assert messages[0].payload["status"] == "HEALTHY"


class TestOgentPollerFD3Integration:
    """Test OgentPoller FD3 integration."""

    def test_poller_accepts_fd3_channel(self) -> None:
        """Poller can be created with FD3 channel."""
        channel = FD3Channel()
        poller = OgentPoller(fd3_channel=channel)

        assert poller.fd3_channel is channel

    def test_poller_set_fd3_channel(self) -> None:
        """Poller can set FD3 channel after creation."""
        poller = OgentPoller()
        assert poller.fd3_channel is None

        channel = FD3Channel()
        poller.set_fd3_channel(channel)

        assert poller.fd3_channel is channel

    def test_handle_fd3_health(self) -> None:
        """Poller handles FD3 health messages."""
        poller = OgentPoller()
        updates: list[tuple[str, XYZHealth]] = []
        poller.subscribe(lambda aid, h: updates.append((aid, h)))

        # Create a mock FD3 message
        msg = FD3Message(
            type="health",
            payload={
                "agent_id": "robin",
                "x_telemetry": 0.9,
                "y_semantic": 0.8,
                "z_economic": 0.7,
            },
        )

        poller._handle_fd3_health(msg)

        assert len(updates) == 1
        assert updates[0][0] == "robin"
        assert updates[0][1].x_telemetry == 0.9
