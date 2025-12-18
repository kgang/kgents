"""Tests for GestaltPolynomial state machine."""

from pathlib import Path

import pytest
from agents.gestalt.polynomial import (
    GESTALT_POLYNOMIAL,
    AnalyzeInput,
    AnalyzeOutput,
    GestaltInput,
    GestaltOutput,
    GestaltPhase,
    HealInput,
    HealOutput,
    IdleInput,
    ScanInput,
    ScanOutput,
    WatchInput,
    WatchOutput,
    gestalt_directions,
    gestalt_transition,
)


class TestGestaltPolynomialStructure:
    """Test polynomial structure is correct."""

    def test_has_five_phases(self):
        """Gestalt polynomial should have 5 phases."""
        assert len(GESTALT_POLYNOMIAL.positions) == 5

    def test_all_phases_present(self):
        """All expected phases should be in positions."""
        expected = {
            GestaltPhase.IDLE,
            GestaltPhase.SCANNING,
            GestaltPhase.WATCHING,
            GestaltPhase.ANALYZING,
            GestaltPhase.HEALING,
        }
        assert expected == GESTALT_POLYNOMIAL.positions

    def test_polynomial_name(self):
        """Polynomial should have correct name."""
        assert GESTALT_POLYNOMIAL.name == "GestaltPolynomial"


class TestGestaltDirections:
    """Test phase-dependent valid inputs."""

    def test_idle_accepts_all_operations(self):
        """IDLE phase accepts all operation types."""
        dirs = gestalt_directions(GestaltPhase.IDLE)
        assert ScanInput in dirs
        assert WatchInput in dirs
        assert AnalyzeInput in dirs
        assert HealInput in dirs

    def test_scanning_only_accepts_idle(self):
        """SCANNING phase only accepts return to idle."""
        dirs = gestalt_directions(GestaltPhase.SCANNING)
        assert IdleInput in dirs
        assert ScanInput not in dirs

    def test_watching_accepts_idle_and_analyze(self):
        """WATCHING phase accepts idle, watch disable, and analyze."""
        dirs = gestalt_directions(GestaltPhase.WATCHING)
        assert IdleInput in dirs
        assert AnalyzeInput in dirs
        assert WatchInput in dirs  # To disable

    def test_analyzing_only_accepts_idle(self):
        """ANALYZING phase only accepts return to idle."""
        dirs = gestalt_directions(GestaltPhase.ANALYZING)
        assert IdleInput in dirs
        assert AnalyzeInput not in dirs

    def test_healing_only_accepts_idle(self):
        """HEALING phase only accepts return to idle."""
        dirs = gestalt_directions(GestaltPhase.HEALING)
        assert IdleInput in dirs
        assert HealInput not in dirs


class TestGestaltTransitions:
    """Test state transitions."""

    def test_idle_to_scanning(self):
        """Scan input moves from IDLE to SCANNING."""
        inp = ScanInput(language="python")
        new_phase, output = gestalt_transition(GestaltPhase.IDLE, inp)

        assert new_phase == GestaltPhase.SCANNING
        assert isinstance(output, ScanOutput)
        assert output.success is True
        assert "python" in output.message

    def test_idle_to_watching(self):
        """Watch input moves from IDLE to WATCHING."""
        inp = WatchInput(enable=True, patterns=("**/*.py",))
        new_phase, output = gestalt_transition(GestaltPhase.IDLE, inp)

        assert new_phase == GestaltPhase.WATCHING
        assert isinstance(output, WatchOutput)
        assert output.success is True
        assert output.watching is True
        assert output.patterns == ("**/*.py",)

    def test_idle_watch_disable_is_noop(self):
        """Watch disable while IDLE is a no-op."""
        inp = WatchInput(enable=False)
        new_phase, output = gestalt_transition(GestaltPhase.IDLE, inp)

        assert new_phase == GestaltPhase.IDLE
        assert output.success is True
        assert "not running" in output.message

    def test_idle_to_analyzing(self):
        """Analyze input moves from IDLE to ANALYZING."""
        inp = AnalyzeInput(module_name="test.module", depth=3)
        new_phase, output = gestalt_transition(GestaltPhase.IDLE, inp)

        assert new_phase == GestaltPhase.ANALYZING
        assert isinstance(output, AnalyzeOutput)
        assert output.success is True
        assert output.module_name == "test.module"

    def test_idle_to_healing(self):
        """Heal input moves from IDLE to HEALING."""
        inp = HealInput(module_name="test.module", max_suggestions=5)
        new_phase, output = gestalt_transition(GestaltPhase.IDLE, inp)

        assert new_phase == GestaltPhase.HEALING
        assert isinstance(output, HealOutput)
        assert output.success is True

    def test_scanning_to_idle(self):
        """Idle input returns from SCANNING to IDLE."""
        inp = IdleInput()
        new_phase, output = gestalt_transition(GestaltPhase.SCANNING, inp)

        assert new_phase == GestaltPhase.IDLE
        assert output.success is True

    def test_scanning_rejects_new_operation(self):
        """SCANNING rejects new operations."""
        inp = AnalyzeInput(module_name="test")
        new_phase, output = gestalt_transition(GestaltPhase.SCANNING, inp)

        assert new_phase == GestaltPhase.SCANNING  # Stays in SCANNING
        assert output.success is False

    def test_watching_to_idle(self):
        """Idle input stops watching and returns to IDLE."""
        inp = IdleInput()
        new_phase, output = gestalt_transition(GestaltPhase.WATCHING, inp)

        assert new_phase == GestaltPhase.IDLE
        assert isinstance(output, WatchOutput)
        assert output.watching is False

    def test_watching_disable_returns_to_idle(self):
        """Watch disable returns from WATCHING to IDLE."""
        inp = WatchInput(enable=False)
        new_phase, output = gestalt_transition(GestaltPhase.WATCHING, inp)

        assert new_phase == GestaltPhase.IDLE
        assert isinstance(output, WatchOutput)
        assert output.watching is False

    def test_watching_allows_analyze(self):
        """WATCHING allows quick analysis without leaving mode."""
        inp = AnalyzeInput(module_name="test.module")
        new_phase, output = gestalt_transition(GestaltPhase.WATCHING, inp)

        assert new_phase == GestaltPhase.WATCHING  # Stays in WATCHING
        assert isinstance(output, AnalyzeOutput)
        assert output.success is True
        assert output.metadata.get("mode") == "quick"

    def test_analyzing_to_idle(self):
        """Idle input returns from ANALYZING to IDLE."""
        inp = IdleInput()
        new_phase, output = gestalt_transition(GestaltPhase.ANALYZING, inp)

        assert new_phase == GestaltPhase.IDLE
        assert output.success is True

    def test_healing_to_idle(self):
        """Idle input returns from HEALING to IDLE."""
        inp = IdleInput()
        new_phase, output = gestalt_transition(GestaltPhase.HEALING, inp)

        assert new_phase == GestaltPhase.IDLE
        assert output.success is True


class TestGestaltInputFactory:
    """Test GestaltInput factory methods."""

    def test_scan_factory(self):
        """GestaltInput.scan creates ScanInput."""
        inp = GestaltInput.scan(language="typescript", max_modules=100)
        assert isinstance(inp, ScanInput)
        assert inp.language == "typescript"
        assert inp.max_modules == 100

    def test_scan_factory_with_path(self):
        """GestaltInput.scan accepts Path."""
        inp = GestaltInput.scan(root=Path("/tmp/project"))
        assert isinstance(inp, ScanInput)
        assert inp.root == Path("/tmp/project")

    def test_watch_factory(self):
        """GestaltInput.watch creates WatchInput."""
        inp = GestaltInput.watch(debounce_seconds=0.5, patterns=("**/*.ts",))
        assert isinstance(inp, WatchInput)
        assert inp.enable is True
        assert inp.debounce_seconds == 0.5
        assert inp.patterns == ("**/*.ts",)

    def test_analyze_factory(self):
        """GestaltInput.analyze creates AnalyzeInput."""
        inp = GestaltInput.analyze(
            module_name="my.module",
            include_dependents=False,
            depth=4,
        )
        assert isinstance(inp, AnalyzeInput)
        assert inp.module_name == "my.module"
        assert inp.include_dependents is False
        assert inp.depth == 4

    def test_heal_factory(self):
        """GestaltInput.heal creates HealInput."""
        inp = GestaltInput.heal(
            module_name="broken.module",
            severity_threshold="error",
            max_suggestions=3,
        )
        assert isinstance(inp, HealInput)
        assert inp.module_name == "broken.module"
        assert inp.severity_threshold == "error"
        assert inp.max_suggestions == 3

    def test_idle_factory(self):
        """GestaltInput.idle creates IdleInput."""
        inp = GestaltInput.idle()
        assert isinstance(inp, IdleInput)


class TestGestaltPolynomialInvoke:
    """Test using polynomial invoke method."""

    def test_invoke_scan(self):
        """Can invoke scan via polynomial."""
        inp = ScanInput(language="python")
        new_phase, output = GESTALT_POLYNOMIAL.invoke(GestaltPhase.IDLE, inp)

        assert new_phase == GestaltPhase.SCANNING
        assert output.success is True

    def test_invoke_full_scan_cycle(self):
        """Can run a full scan cycle: IDLE -> SCANNING -> IDLE."""
        # Start scan
        state, _ = GESTALT_POLYNOMIAL.invoke(
            GestaltPhase.IDLE, ScanInput(language="python")
        )
        assert state == GestaltPhase.SCANNING

        # Return to idle
        state, _ = GESTALT_POLYNOMIAL.invoke(state, IdleInput())
        assert state == GestaltPhase.IDLE

    def test_invoke_full_watch_cycle(self):
        """Can run a full watch cycle: IDLE -> WATCHING -> IDLE."""
        # Start watching
        state, output = GESTALT_POLYNOMIAL.invoke(
            GestaltPhase.IDLE, WatchInput(enable=True)
        )
        assert state == GestaltPhase.WATCHING
        assert isinstance(output, WatchOutput)
        assert output.watching is True

        # Analyze while watching
        state, output = GESTALT_POLYNOMIAL.invoke(
            state, AnalyzeInput(module_name="test")
        )
        assert state == GestaltPhase.WATCHING  # Still watching
        assert isinstance(output, AnalyzeOutput)

        # Stop watching
        state, output = GESTALT_POLYNOMIAL.invoke(state, WatchInput(enable=False))
        assert state == GestaltPhase.IDLE

    def test_invoke_rejects_invalid_state(self):
        """Invoke raises error for invalid state."""

        # Create an invalid state (not in positions)
        class FakePhase:
            pass

        with pytest.raises(ValueError, match="Invalid state"):
            GESTALT_POLYNOMIAL.invoke(FakePhase(), ScanInput())  # type: ignore

    def test_invoke_run_sequence(self):
        """Can run a sequence of inputs."""
        inputs = [
            ScanInput(language="python"),
            IdleInput(),
            WatchInput(enable=True),
            AnalyzeInput(module_name="test"),
            WatchInput(enable=False),
        ]

        final_state, outputs = GESTALT_POLYNOMIAL.run(GestaltPhase.IDLE, inputs)

        assert final_state == GestaltPhase.IDLE
        assert len(outputs) == 5
        assert all(o.success for o in outputs)


class TestGestaltPhaseSemantics:
    """Test semantic meaning of phases matches C4 model."""

    def test_scanning_is_system_level(self):
        """SCANNING corresponds to System Context level."""
        inp = ScanInput()
        _, output = gestalt_transition(GestaltPhase.IDLE, inp)
        # Scanning covers the whole codebase (system level)
        assert "Scanning" in output.message

    def test_watching_is_incremental(self):
        """WATCHING enables incremental updates."""
        inp = WatchInput(enable=True)
        _, output = gestalt_transition(GestaltPhase.IDLE, inp)
        assert isinstance(output, WatchOutput)
        assert output.watching is True

    def test_analyzing_is_component_level(self):
        """ANALYZING corresponds to Component level (deep module inspection)."""
        inp = AnalyzeInput(module_name="test.module", depth=2)
        _, output = gestalt_transition(GestaltPhase.IDLE, inp)
        assert isinstance(output, AnalyzeOutput)
        assert output.module_name == "test.module"
        # Depth indicates how deep to traverse dependencies
        assert output.metadata["depth"] == 2

    def test_healing_generates_suggestions(self):
        """HEALING generates drift repair suggestions."""
        inp = HealInput(max_suggestions=5)
        _, output = gestalt_transition(GestaltPhase.IDLE, inp)
        assert isinstance(output, HealOutput)
        assert output.metadata["max_suggestions"] == 5
