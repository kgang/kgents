"""Tests for BrainPolynomial state machine."""

import pytest
from agents.brain.polynomial import (
    BRAIN_POLYNOMIAL,
    BrainInput,
    BrainOutput,
    BrainPhase,
    CaptureInput,
    CaptureOutput,
    HealInput,
    HealOutput,
    IdleInput,
    SearchInput,
    SearchOutput,
    SurfaceInput,
    SurfaceOutput,
    brain_directions,
    brain_transition,
)


class TestBrainPolynomialStructure:
    """Test polynomial structure is correct."""

    def test_has_five_phases(self):
        """Brain polynomial should have 5 phases."""
        assert len(BRAIN_POLYNOMIAL.positions) == 5

    def test_all_phases_present(self):
        """All expected phases should be in positions."""
        expected = {
            BrainPhase.IDLE,
            BrainPhase.CAPTURING,
            BrainPhase.SEARCHING,
            BrainPhase.SURFACING,
            BrainPhase.HEALING,
        }
        assert expected == BRAIN_POLYNOMIAL.positions

    def test_polynomial_name(self):
        """Polynomial should have correct name."""
        assert BRAIN_POLYNOMIAL.name == "BrainPolynomial"


class TestBrainDirections:
    """Test phase-dependent valid inputs."""

    def test_idle_accepts_all_operations(self):
        """IDLE phase accepts all operation types."""
        dirs = brain_directions(BrainPhase.IDLE)
        assert CaptureInput in dirs
        assert SearchInput in dirs
        assert SurfaceInput in dirs
        assert HealInput in dirs

    def test_capturing_only_accepts_idle(self):
        """CAPTURING phase only accepts return to idle."""
        dirs = brain_directions(BrainPhase.CAPTURING)
        assert IdleInput in dirs
        assert CaptureInput not in dirs

    def test_searching_only_accepts_idle(self):
        """SEARCHING phase only accepts return to idle."""
        dirs = brain_directions(BrainPhase.SEARCHING)
        assert IdleInput in dirs
        assert SearchInput not in dirs

    def test_surfacing_only_accepts_idle(self):
        """SURFACING phase only accepts return to idle."""
        dirs = brain_directions(BrainPhase.SURFACING)
        assert IdleInput in dirs
        assert SurfaceInput not in dirs


class TestBrainTransitions:
    """Test state transitions."""

    def test_idle_to_capturing(self):
        """Capture input moves from IDLE to CAPTURING."""
        inp = CaptureInput(content="test content", tags=("test",))
        new_phase, output = brain_transition(BrainPhase.IDLE, inp)

        assert new_phase == BrainPhase.CAPTURING
        assert isinstance(output, CaptureOutput)
        assert output.success is True

    def test_idle_to_searching(self):
        """Search input moves from IDLE to SEARCHING."""
        inp = SearchInput(query="test query", limit=5)
        new_phase, output = brain_transition(BrainPhase.IDLE, inp)

        assert new_phase == BrainPhase.SEARCHING
        assert isinstance(output, SearchOutput)
        assert output.success is True
        assert output.query == "test query"

    def test_idle_to_surfacing(self):
        """Surface input moves from IDLE to SURFACING."""
        inp = SurfaceInput(context="test context", entropy=0.5)
        new_phase, output = brain_transition(BrainPhase.IDLE, inp)

        assert new_phase == BrainPhase.SURFACING
        assert isinstance(output, SurfaceOutput)
        assert output.success is True

    def test_idle_to_healing(self):
        """Heal input moves from IDLE to HEALING."""
        inp = HealInput()
        new_phase, output = brain_transition(BrainPhase.IDLE, inp)

        assert new_phase == BrainPhase.HEALING
        assert isinstance(output, HealOutput)
        assert output.success is True

    def test_capturing_to_idle(self):
        """Idle input returns from CAPTURING to IDLE."""
        inp = IdleInput()
        new_phase, output = brain_transition(BrainPhase.CAPTURING, inp)

        assert new_phase == BrainPhase.IDLE
        assert output.success is True

    def test_capturing_rejects_new_operation(self):
        """CAPTURING rejects new operations."""
        inp = SearchInput(query="test")
        new_phase, output = brain_transition(BrainPhase.CAPTURING, inp)

        assert new_phase == BrainPhase.CAPTURING  # Stays in CAPTURING
        assert output.success is False


class TestBrainInputFactory:
    """Test BrainInput factory methods."""

    def test_capture_factory(self):
        """BrainInput.capture creates CaptureInput."""
        inp = BrainInput.capture("test", tags=("a", "b"))
        assert isinstance(inp, CaptureInput)
        assert inp.content == "test"
        assert inp.tags == ("a", "b")

    def test_search_factory(self):
        """BrainInput.search creates SearchInput."""
        inp = BrainInput.search("query", limit=20)
        assert isinstance(inp, SearchInput)
        assert inp.query == "query"
        assert inp.limit == 20

    def test_surface_factory(self):
        """BrainInput.surface creates SurfaceInput."""
        inp = BrainInput.surface(context="ctx", entropy=0.3)
        assert isinstance(inp, SurfaceInput)
        assert inp.context == "ctx"
        assert inp.entropy == 0.3

    def test_heal_factory(self):
        """BrainInput.heal creates HealInput."""
        inp = BrainInput.heal()
        assert isinstance(inp, HealInput)

    def test_idle_factory(self):
        """BrainInput.idle creates IdleInput."""
        inp = BrainInput.idle()
        assert isinstance(inp, IdleInput)


class TestBrainPolynomialInvoke:
    """Test using polynomial invoke method."""

    def test_invoke_capture(self):
        """Can invoke capture via polynomial."""
        inp = CaptureInput(content="test")
        new_phase, output = BRAIN_POLYNOMIAL.invoke(BrainPhase.IDLE, inp)

        assert new_phase == BrainPhase.CAPTURING
        assert output.success is True

    def test_invoke_full_cycle(self):
        """Can run a full operation cycle: IDLE -> CAPTURING -> IDLE."""
        # Start capture
        state, _ = BRAIN_POLYNOMIAL.invoke(
            BrainPhase.IDLE, CaptureInput(content="test")
        )
        assert state == BrainPhase.CAPTURING

        # Return to idle
        state, _ = BRAIN_POLYNOMIAL.invoke(state, IdleInput())
        assert state == BrainPhase.IDLE
