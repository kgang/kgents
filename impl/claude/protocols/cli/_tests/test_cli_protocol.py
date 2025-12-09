"""
Tests for CLI Protocol implementation.

Tests cover:
1. Core types (OutputFormat, Budget, CommandResult)
2. MirrorCLI commands
3. MembraneCLI commands
4. I-gent synergy (StatusWhisper, SemanticGlint, GardenBridge)
5. Main CLI entry point
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

# Import types
from ..cli_types import (
    BudgetLevel,
    BudgetStatus,
    CLIContext,
    CommandResult,
    ErrorInfo,
    ErrorRecoverability,
    ErrorSeverity,
    OutputFormat,
    PersonaMode,
    format_output,
)

# Import CLIs
from ..mirror_cli import (
    MirrorCLI,
    MirrorObserveResult,
)
from ..membrane_cli import (
    DampeningField,
    MembraneCLI,
    MembraneObserveResult,
    SemanticCurvature,
    SemanticMomentum,
    SemanticVoid,
    membrane_observe,
    membrane_sense,
    membrane_trace,
)

# Import I-gent synergy
from ..igent_synergy import (
    AgentState,
    GardenBridge,
    GardenPhase,
    GardenState,
    GlintSuggestion,
    SemanticGlint,
    StatusWhisper,
    WhisperState,
)


# =============================================================================
# Core Types Tests
# =============================================================================


class TestOutputFormat:
    """Tests for OutputFormat enum."""

    def test_all_formats_exist(self):
        assert OutputFormat.CODE.value == "code"
        assert OutputFormat.VALUE.value == "value"
        assert OutputFormat.JSON.value == "json"
        assert OutputFormat.JSONL.value == "jsonl"
        assert OutputFormat.RICH.value == "rich"
        assert OutputFormat.MARKDOWN.value == "markdown"


class TestBudgetLevel:
    """Tests for BudgetLevel enum."""

    def test_all_levels_exist(self):
        assert BudgetLevel.MINIMAL.value == "minimal"
        assert BudgetLevel.LOW.value == "low"
        assert BudgetLevel.MEDIUM.value == "medium"
        assert BudgetLevel.HIGH.value == "high"
        assert BudgetLevel.UNLIMITED.value == "unlimited"

    def test_max_llm_calls(self):
        assert BudgetLevel.MINIMAL.max_llm_calls == 0
        assert BudgetLevel.LOW.max_llm_calls == 1
        assert BudgetLevel.MEDIUM.max_llm_calls == 5
        assert BudgetLevel.HIGH.max_llm_calls == 20
        assert BudgetLevel.UNLIMITED.max_llm_calls == 1000

    def test_max_tokens(self):
        assert BudgetLevel.MINIMAL.max_tokens == 0
        assert BudgetLevel.LOW.max_tokens == 4000
        assert BudgetLevel.MEDIUM.max_tokens == 20000


class TestBudgetStatus:
    """Tests for BudgetStatus."""

    def test_from_level(self):
        status = BudgetStatus.from_level(BudgetLevel.MEDIUM)
        assert status.level == BudgetLevel.MEDIUM
        assert status.tokens_limit == 20000
        assert status.llm_calls_limit == 5
        assert status.tokens_used == 0

    def test_can_afford(self):
        status = BudgetStatus.from_level(BudgetLevel.LOW)
        assert status.can_afford(estimated_tokens=3000)
        assert not status.can_afford(estimated_tokens=5000)

    def test_spend(self):
        status = BudgetStatus.from_level(BudgetLevel.MEDIUM)
        new_status = status.spend(tokens=1000, llm_calls=1)
        assert new_status.tokens_used == 1000
        assert new_status.llm_calls_used == 1
        assert new_status.entropy_spent > 0


class TestErrorInfo:
    """Tests for ErrorInfo."""

    def test_creation(self):
        error = ErrorInfo(
            error_type=ErrorRecoverability.PERMANENT,
            severity=ErrorSeverity.FAILURE,
            code="TEST_ERROR",
            message="Test error message",
            suggestions=("Try again",),
        )
        assert error.code == "TEST_ERROR"
        assert error.exit_code == 54  # midpoint of 10-99

    def test_to_dict(self):
        error = ErrorInfo(
            error_type=ErrorRecoverability.TRANSIENT,
            severity=ErrorSeverity.DEGRADED,
            code="RETRY_ERROR",
            message="Should retry",
        )
        d = error.to_dict()
        assert d["error"]["type"] == "transient"
        assert d["error"]["severity"] == 2


class TestCommandResult:
    """Tests for CommandResult."""

    def test_ok(self):
        result = CommandResult.ok({"key": "value"}, duration_ms=100)
        assert result.success is True
        assert result.exit_code == 0
        assert result.output == {"key": "value"}

    def test_fail(self):
        error = ErrorInfo(
            error_type=ErrorRecoverability.PERMANENT,
            severity=ErrorSeverity.FAILURE,
            code="FAIL",
            message="Failed",
        )
        result = CommandResult.fail(error)
        assert result.success is False
        assert result.exit_code > 0
        assert result.error == error

    def test_to_envelope(self):
        result = CommandResult.ok({"data": 123})
        envelope = result.to_envelope("test.agent")
        assert envelope.agent == "test.agent"
        assert envelope.result == {"data": 123}


class TestCLIContext:
    """Tests for CLIContext."""

    def test_default_values(self):
        ctx = CLIContext()
        assert ctx.output_format == OutputFormat.RICH
        assert ctx.persona == PersonaMode.MINIMAL
        assert ctx.budget.level == BudgetLevel.MEDIUM

    def test_is_sanctuary(self):
        ctx = CLIContext(sanctuary_paths=(Path("/private"),))
        assert ctx.is_sanctuary(Path("/private/secrets.txt"))
        assert not ctx.is_sanctuary(Path("/public/file.txt"))

    def test_with_budget(self):
        ctx = CLIContext()
        new_ctx = ctx.with_budget(BudgetLevel.HIGH)
        assert new_ctx.budget.level == BudgetLevel.HIGH
        assert ctx.budget.level == BudgetLevel.MEDIUM  # Original unchanged


class TestFormatOutput:
    """Tests for format_output function."""

    def test_format_json(self):
        result = CommandResult.ok({"test": "data"})
        ctx = CLIContext(output_format=OutputFormat.JSON)
        output = format_output(result, ctx, "test")
        assert "test" in output
        assert "data" in output

    def test_format_value(self):
        result = CommandResult.ok("simple value")
        ctx = CLIContext(output_format=OutputFormat.VALUE)
        output = format_output(result, ctx, "test")
        assert output == "simple value"

    def test_format_code(self):
        result = CommandResult.ok("ignored")
        ctx = CLIContext(output_format=OutputFormat.CODE)
        output = format_output(result, ctx, "test")
        assert output == ""


# =============================================================================
# Membrane Types Tests
# =============================================================================


class TestSemanticCurvature:
    """Tests for SemanticCurvature."""

    def test_creation(self):
        curve = SemanticCurvature(
            shape_id="SHAPE-01-curve",
            centroid_topic="authentication",
            radius=0.5,
            intensity=0.8,
            attractors=("login", "tokens"),
            repellers=("logout",),
            interpretation="High tension around auth",
        )
        assert curve.intensity == 0.8
        assert "authentication" in curve.centroid_topic

    def test_to_dict(self):
        curve = SemanticCurvature(
            shape_id="SHAPE-01-curve",
            centroid_topic="test",
            radius=0.5,
            intensity=0.5,
            attractors=(),
            repellers=(),
            interpretation="Test",
        )
        d = curve.to_dict()
        assert d["type"] == "curvature"
        assert d["shape_id"] == "SHAPE-01-curve"


class TestSemanticVoid:
    """Tests for SemanticVoid."""

    def test_creation(self):
        void = SemanticVoid(
            shape_id="SHAPE-02-void",
            boundary=("error", "handling", "strategy"),
            depth=0.9,
            persistence=0.8,
            interpretation="Nobody discusses error handling",
        )
        assert void.depth == 0.9
        assert "error" in void.boundary

    def test_to_dict(self):
        void = SemanticVoid(
            shape_id="SHAPE-02-void",
            boundary=("a", "b"),
            depth=0.5,
            persistence=0.5,
            interpretation="Test void",
        )
        d = void.to_dict()
        assert d["type"] == "void"


class TestSemanticMomentum:
    """Tests for SemanticMomentum."""

    def test_creation(self):
        momentum = SemanticMomentum(
            shape_id="SHAPE-03-flow",
            topic="refactoring",
            mass=0.7,
            velocity_magnitude=0.3,
            velocity_direction="toward simplicity",
            is_conserved=True,
            interpretation="Refactoring effort building momentum",
        )
        assert momentum.is_conserved is True
        assert momentum.mass == 0.7


class TestDampeningField:
    """Tests for DampeningField."""

    def test_creation(self):
        field = DampeningField(
            shape_id="SHAPE-04-damp",
            trigger="deadlines",
            compression_ratio=0.8,
            affected_count=5,
            interpretation="Emotions flatten around deadlines",
        )
        assert field.compression_ratio == 0.8


# =============================================================================
# MembraneCLI Tests
# =============================================================================


class TestMembraneCLI:
    """Tests for MembraneCLI."""

    @pytest.fixture
    def cli(self):
        return MembraneCLI()

    @pytest.fixture
    def temp_dir(self):
        with tempfile.TemporaryDirectory() as td:
            yield Path(td)

    @pytest.mark.asyncio
    async def test_observe_returns_result(self, cli, temp_dir):
        # Create some files
        (temp_dir / "test.py").write_text("# test")

        result = await cli.observe(temp_dir)
        assert result.success is True
        assert isinstance(result.output, MembraneObserveResult)

    @pytest.mark.asyncio
    async def test_observe_detects_shapes(self, cli, temp_dir):
        # Create structure that triggers shape detection
        (temp_dir / "main.py").write_text("# main")
        (temp_dir / "utils.py").write_text("# utils")

        result = await cli.observe(temp_dir)
        assert result.success is True
        assert len(result.output.shapes) > 0

    @pytest.mark.asyncio
    async def test_sense_is_fast(self, cli):
        import time

        start = time.time()
        result = await cli.sense()
        duration = time.time() - start
        assert result.success is True
        # Should be fast (allowing some margin)
        assert duration < 1.0

    @pytest.mark.asyncio
    async def test_trace_topic(self, cli):
        result = await cli.trace("authentication")
        assert result.success is True
        assert result.output.topic == "authentication"

    @pytest.mark.asyncio
    async def test_touch_unknown_shape(self, cli):
        result = await cli.touch("SHAPE-999-unknown")
        assert result.success is False
        assert result.error.code == "SHAPE_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_name_void(self, cli):
        result = await cli.name("We avoid discussing deadlines")
        assert result.success is True
        assert result.output["named"] is True

    @pytest.mark.asyncio
    async def test_sanctuary_respected(self, cli):
        ctx = CLIContext(sanctuary_paths=(Path("/sanctuary"),))
        result = await cli.observe(Path("/sanctuary/secret"), ctx)
        assert result.success is False
        assert result.error.code == "SANCTUARY_VIOLATION"


# =============================================================================
# MirrorCLI Tests
# =============================================================================


class TestMirrorCLI:
    """Tests for MirrorCLI."""

    @pytest.fixture
    def cli(self):
        return MirrorCLI()

    @pytest.fixture
    def vault_with_principles(self):
        """Create a temporary vault with principles."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td)
            # Create README with principles
            (vault / "README.md").write_text("""
# My Vault

I believe in connecting ideas.
I always strive for deep understanding.
My principle is to link everything.
            """)
            # Create some notes
            (vault / "note1.md").write_text("# Note 1\nSome content")
            (vault / "note2.md").write_text("# Note 2\nMore content")
            yield vault

    @pytest.mark.asyncio
    async def test_observe_with_principles(self, cli, vault_with_principles):
        result = await cli.observe(vault_with_principles)
        assert result.success is True
        assert isinstance(result.output, MirrorObserveResult)
        assert result.output.principle_count > 0

    @pytest.mark.asyncio
    async def test_observe_nonexistent_path(self, cli):
        result = await cli.observe(Path("/nonexistent/path"))
        assert result.success is False
        assert result.error.code == "VAULT_NOT_FOUND"

    @pytest.mark.asyncio
    async def test_status_without_observation(self, cli):
        result = await cli.status()
        assert result.success is True
        assert result.output.last_observation is None

    @pytest.mark.asyncio
    async def test_reflect_without_observation(self, cli):
        result = await cli.reflect(0)
        assert result.success is False
        assert result.error.code == "NO_OBSERVATION"

    @pytest.mark.asyncio
    async def test_hold_tension(self, cli, vault_with_principles):
        # First observe to get tensions
        await cli.observe(vault_with_principles)

        # Then hold if there are tensions
        if cli._last_report and cli._last_report.all_tensions:
            result = await cli.hold(0, "Productive tension")
            assert result.success is True
            assert result.output["held"] is True


# =============================================================================
# I-gent Synergy Tests
# =============================================================================


class TestStatusWhisper:
    """Tests for StatusWhisper."""

    def test_render(self):
        whisper = StatusWhisper(integrity_score=0.82, trend="improving")
        rendered = whisper.render()
        assert "0.82" in rendered
        assert "▵" in rendered

    def test_render_prompt_segment(self):
        whisper = StatusWhisper(integrity_score=0.75, trend="declining")
        segment = whisper.render_prompt_segment()
        assert segment.startswith("[")
        assert segment.endswith("]")
        assert "0.75" in segment

    def test_update_triggers_pulse(self):
        whisper = StatusWhisper(integrity_score=0.8)
        whisper.update(0.5)  # Significant change
        assert whisper.state == WhisperState.PULSE

    def test_callback_on_change(self):
        whisper = StatusWhisper()
        called = []
        whisper.on_change(lambda score, trend: called.append((score, trend)))
        whisper.update(0.9, "improving")
        assert len(called) == 1
        assert called[0] == (0.9, "improving")

    def test_dreaming_state(self):
        whisper = StatusWhisper()
        whisper.enter_dreaming()
        assert whisper.state == WhisperState.DREAMING
        assert "◇" in whisper.render()


class TestSemanticGlint:
    """Tests for SemanticGlint."""

    def test_generate_git_suggestion(self):
        glint = SemanticGlint(confidence_threshold=0.5)
        suggestion = glint.generate(
            "git commit ",
            {"staged_files": ["auth_service.py"]},
        )
        assert suggestion is not None
        assert "auth" in suggestion.text.lower() or "-m" in suggestion.text

    def test_no_suggestion_below_threshold(self):
        glint = SemanticGlint(confidence_threshold=0.99)
        suggestion = glint.generate("random input")
        assert suggestion is None

    def test_disable_glint(self):
        glint = SemanticGlint()
        glint.disable()
        suggestion = glint.generate(
            "git commit",
            {"staged_files": ["test.py"]},
        )
        assert suggestion is None

    def test_render_grey(self):
        glint = SemanticGlint()
        suggestion = GlintSuggestion(
            text="test suggestion",
            confidence=0.8,
            context="test",
            source="test",
        )
        rendered = glint.render(suggestion)
        # Should contain ANSI grey codes
        assert "\033[90m" in rendered


class TestGardenBridge:
    """Tests for GardenBridge."""

    def test_initialize(self):
        bridge = GardenBridge()
        state = bridge.initialize("test-garden")
        assert state.name == "test-garden"
        assert "Ground" in state.agents

    def test_update_agent(self):
        bridge = GardenBridge()
        bridge.initialize()
        bridge.update_agent("Ground", phase=GardenPhase.WANING)
        assert bridge.state.agents["Ground"].phase == GardenPhase.WANING

    def test_add_margin_note(self):
        bridge = GardenBridge()
        bridge.initialize()
        bridge.add_margin_note("Ground", "Test note", "system")
        assert len(bridge.state.agents["Ground"].margin_notes) == 1

    def test_render_glyphs(self):
        bridge = GardenBridge()
        bridge.initialize()
        glyphs = bridge.render_glyphs()
        assert "●" in glyphs or "○" in glyphs

    def test_render_garden_ascii(self):
        bridge = GardenBridge()
        bridge.initialize("test")
        ascii_art = bridge.render_garden_ascii()
        assert "test garden" in ascii_art
        assert "breath:" in ascii_art

    def test_to_session_json(self):
        bridge = GardenBridge()
        bridge.initialize("session-test")
        json = bridge.to_session_json()
        assert json["name"] == "session-test"
        assert "agents" in json
        assert "Ground" in json["agents"]


class TestGardenState:
    """Tests for GardenState."""

    def test_add_agent(self):
        state = GardenState(name="test")
        agent = AgentState(
            agent_id="TestAgent",
            genus="test",
            phase=GardenPhase.ACTIVE,
            birth_time=datetime.now(),
        )
        state.add_agent(agent)
        assert "TestAgent" in state.agents

    def test_get_agent(self):
        state = GardenState(name="test")
        agent = AgentState(
            agent_id="TestAgent",
            genus="test",
            phase=GardenPhase.DORMANT,
            birth_time=datetime.now(),
        )
        state.add_agent(agent)
        retrieved = state.get_agent("TestAgent")
        assert retrieved == agent
        assert state.get_agent("Nonexistent") is None

    def test_add_note(self):
        state = GardenState(name="test")
        state.add_note("Global note", "human")
        assert len(state.global_notes) == 1
        assert state.global_notes[0]["source"] == "human"


# =============================================================================
# Integration Tests
# =============================================================================


class TestCLIIntegration:
    """Integration tests for CLI."""

    @pytest.mark.asyncio
    async def test_mirror_to_membrane_flow(self):
        """Test that mirror observations can inform membrane analysis."""
        with tempfile.TemporaryDirectory() as td:
            vault = Path(td)
            (vault / "README.md").write_text("I believe in testing.")
            (vault / "test.py").write_text("# no tests actually")

            # Mirror observe
            mirror = MirrorCLI()
            mirror_result = await mirror.observe(vault)

            # Membrane observe same location
            membrane = MembraneCLI()
            membrane_result = await membrane.observe(vault)

            # Both should succeed
            assert mirror_result.success is True
            assert membrane_result.success is True

    @pytest.mark.asyncio
    async def test_whisper_reflects_observation(self):
        """Test that whisper updates from observations."""
        whisper = StatusWhisper()

        with tempfile.TemporaryDirectory() as td:
            vault = Path(td)
            (vault / "README.md").write_text("I value quality.")
            (vault / "note.md").write_text("Quick note")

            cli = MirrorCLI()
            result = await cli.observe(vault)

            if result.success:
                whisper.update(result.output.integrity_score)
                assert whisper.integrity_score == result.output.integrity_score


# =============================================================================
# Convenience Function Tests
# =============================================================================


class TestConvenienceFunctions:
    """Tests for convenience functions."""

    @pytest.mark.asyncio
    async def test_membrane_observe(self):
        with tempfile.TemporaryDirectory() as td:
            result = await membrane_observe(td)
            assert result.success is True

    @pytest.mark.asyncio
    async def test_membrane_sense(self):
        result = await membrane_sense()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_membrane_trace(self):
        result = await membrane_trace("test-topic")
        assert result.success is True
        assert result.output.topic == "test-topic"
