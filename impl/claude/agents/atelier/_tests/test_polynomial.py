"""Tests for WorkshopPolynomial state machine."""

import pytest

from agents.atelier.polynomial import (
    ATELIER_POLYNOMIAL,
    WORKSHOP_POLYNOMIAL,
    CloseInput,
    ContributeInput,
    ContributeOutput,
    ExhibitOutput,
    JoinInput,
    JoinOutput,
    OpenExhibitionInput,
    RefineInput,
    StartExhibitionInput,
    ViewInput,
    WorkshopInput,
    WorkshopOutput,
    WorkshopPhase,
    workshop_directions,
    workshop_transition,
)


class TestWorkshopPolynomialStructure:
    """Test polynomial structure is correct."""

    def test_has_five_phases(self):
        """Workshop polynomial should have 5 phases."""
        assert len(WORKSHOP_POLYNOMIAL.positions) == 5

    def test_all_phases_present(self):
        """All expected phases should be in positions."""
        expected = {
            WorkshopPhase.GATHERING,
            WorkshopPhase.CREATING,
            WorkshopPhase.REVIEWING,
            WorkshopPhase.EXHIBITING,
            WorkshopPhase.CLOSED,
        }
        assert expected == WORKSHOP_POLYNOMIAL.positions

    def test_polynomial_name(self):
        """Polynomial should have correct name."""
        assert WORKSHOP_POLYNOMIAL.name == "WorkshopPolynomial"

    def test_atelier_polynomial_is_alias(self):
        """ATELIER_POLYNOMIAL should be alias for WORKSHOP_POLYNOMIAL."""
        assert ATELIER_POLYNOMIAL is WORKSHOP_POLYNOMIAL


class TestWorkshopDirections:
    """Test phase-dependent valid inputs."""

    def test_gathering_accepts_join_and_contribute(self):
        """GATHERING phase accepts join and contribute."""
        dirs = workshop_directions(WorkshopPhase.GATHERING)
        assert JoinInput in dirs
        assert ContributeInput in dirs

    def test_creating_accepts_contribute_refine_exhibit(self):
        """CREATING phase accepts contribute, refine, and exhibit."""
        dirs = workshop_directions(WorkshopPhase.CREATING)
        assert ContributeInput in dirs
        assert RefineInput in dirs
        assert StartExhibitionInput in dirs

    def test_reviewing_accepts_refine_contribute_exhibit(self):
        """REVIEWING phase accepts refine, contribute, and exhibit."""
        dirs = workshop_directions(WorkshopPhase.REVIEWING)
        assert RefineInput in dirs
        assert ContributeInput in dirs
        assert StartExhibitionInput in dirs

    def test_exhibiting_accepts_view_open_close(self):
        """EXHIBITING phase accepts view, open, and close."""
        dirs = workshop_directions(WorkshopPhase.EXHIBITING)
        assert ViewInput in dirs
        assert OpenExhibitionInput in dirs
        assert CloseInput in dirs

    def test_closed_is_terminal(self):
        """CLOSED phase should have minimal inputs (terminal)."""
        dirs = workshop_directions(WorkshopPhase.CLOSED)
        # Should not accept any operations except type
        assert JoinInput not in dirs
        assert ContributeInput not in dirs


class TestWorkshopTransitions:
    """Test state transitions."""

    def test_gathering_join_stays_in_gathering(self):
        """Join input keeps workshop in GATHERING."""
        inp = JoinInput(artisan_name="Alice", specialty="painter")
        new_phase, output = workshop_transition(WorkshopPhase.GATHERING, inp)

        assert new_phase == WorkshopPhase.GATHERING
        assert isinstance(output, JoinOutput)
        assert output.success is True
        assert "Alice" in output.message

    def test_gathering_contribute_moves_to_creating(self):
        """First contribution moves from GATHERING to CREATING."""
        inp = ContributeInput(artisan_id="1", content="test", contribution_type="draft")
        new_phase, output = workshop_transition(WorkshopPhase.GATHERING, inp)

        assert new_phase == WorkshopPhase.CREATING
        assert isinstance(output, ContributeOutput)
        assert output.success is True

    def test_creating_contribute_stays_in_creating(self):
        """Contribution in CREATING stays in CREATING."""
        inp = ContributeInput(artisan_id="1", content="more work")
        new_phase, output = workshop_transition(WorkshopPhase.CREATING, inp)

        assert new_phase == WorkshopPhase.CREATING
        assert output.success is True

    def test_creating_refine_moves_to_reviewing(self):
        """Refinement moves from CREATING to REVIEWING."""
        inp = RefineInput(contribution_id="c1", refined_content="better", refiner_id="a1")
        new_phase, output = workshop_transition(WorkshopPhase.CREATING, inp)

        assert new_phase == WorkshopPhase.REVIEWING
        assert output.success is True

    def test_creating_exhibit_moves_to_exhibiting(self):
        """Start exhibition moves from CREATING to EXHIBITING."""
        inp = StartExhibitionInput(name="First Show")
        new_phase, output = workshop_transition(WorkshopPhase.CREATING, inp)

        assert new_phase == WorkshopPhase.EXHIBITING
        assert isinstance(output, ExhibitOutput)
        assert output.success is True

    def test_exhibiting_close_moves_to_closed(self):
        """Close input moves from EXHIBITING to CLOSED."""
        inp = CloseInput(reason="completed")
        new_phase, output = workshop_transition(WorkshopPhase.EXHIBITING, inp)

        assert new_phase == WorkshopPhase.CLOSED
        assert output.success is True

    def test_closed_rejects_all_inputs(self):
        """CLOSED phase rejects all inputs."""
        inp = ContributeInput(artisan_id="1", content="too late")
        new_phase, output = workshop_transition(WorkshopPhase.CLOSED, inp)

        assert new_phase == WorkshopPhase.CLOSED  # Stays closed
        assert output.success is False


class TestWorkshopInputFactory:
    """Test WorkshopInput factory methods."""

    def test_create_factory(self):
        """WorkshopInput.create creates CreateWorkshopInput."""
        inp = WorkshopInput.create("My Workshop", description="Test")
        assert inp.name == "My Workshop"
        assert inp.description == "Test"

    def test_join_factory(self):
        """WorkshopInput.join creates JoinInput."""
        inp = WorkshopInput.join("Bob", "sculptor", style="abstract")
        assert isinstance(inp, JoinInput)
        assert inp.artisan_name == "Bob"
        assert inp.specialty == "sculptor"
        assert inp.style == "abstract"

    def test_contribute_factory(self):
        """WorkshopInput.contribute creates ContributeInput."""
        inp = WorkshopInput.contribute("a1", "content here", content_type="poem")
        assert isinstance(inp, ContributeInput)
        assert inp.artisan_id == "a1"
        assert inp.content == "content here"

    def test_exhibit_factory(self):
        """WorkshopInput.exhibit creates StartExhibitionInput."""
        inp = WorkshopInput.exhibit("Grand Opening", description="First show")
        assert isinstance(inp, StartExhibitionInput)
        assert inp.name == "Grand Opening"


class TestWorkshopPolynomialInvoke:
    """Test using polynomial invoke method."""

    def test_invoke_join(self):
        """Can invoke join via polynomial."""
        inp = JoinInput(artisan_name="Test", specialty="coder")
        new_phase, output = WORKSHOP_POLYNOMIAL.invoke(WorkshopPhase.GATHERING, inp)

        assert new_phase == WorkshopPhase.GATHERING
        assert output.success is True

    def test_invoke_full_lifecycle(self):
        """Can run full workshop lifecycle."""
        # Start in GATHERING
        state = WorkshopPhase.GATHERING

        # Join artisan
        state, _ = WORKSHOP_POLYNOMIAL.invoke(
            state, JoinInput(artisan_name="Alice", specialty="writer")
        )
        assert state == WorkshopPhase.GATHERING

        # First contribution -> CREATING
        state, _ = WORKSHOP_POLYNOMIAL.invoke(
            state, ContributeInput(artisan_id="1", content="draft")
        )
        assert state == WorkshopPhase.CREATING

        # Refinement -> REVIEWING
        state, _ = WORKSHOP_POLYNOMIAL.invoke(
            state,
            RefineInput(contribution_id="c1", refined_content="v2", refiner_id="1"),
        )
        assert state == WorkshopPhase.REVIEWING

        # Start exhibition -> EXHIBITING
        state, _ = WORKSHOP_POLYNOMIAL.invoke(state, StartExhibitionInput(name="Final"))
        assert state == WorkshopPhase.EXHIBITING

        # Close -> CLOSED
        state, _ = WORKSHOP_POLYNOMIAL.invoke(state, CloseInput(reason="done"))
        assert state == WorkshopPhase.CLOSED


class TestWorkshopTerminalState:
    """Test terminal state behavior."""

    def test_closed_rejects_via_transition(self):
        """CLOSED state rejects operations via transition function."""
        # Using transition directly to test behavior without input validation
        state, output = workshop_transition(
            WorkshopPhase.CLOSED, JoinInput(artisan_name="Late", specialty="x")
        )
        assert state == WorkshopPhase.CLOSED
        assert output.success is False

        state, output = workshop_transition(
            WorkshopPhase.CLOSED, ContributeInput(artisan_id="1", content="x")
        )
        assert state == WorkshopPhase.CLOSED
        assert output.success is False

    def test_closed_invoke_raises_for_invalid_inputs(self):
        """CLOSED state raises ValueError via invoke (strict validation)."""

        # invoke validates inputs against directions, so it raises for CLOSED
        with pytest.raises(ValueError, match="Invalid input"):
            WORKSHOP_POLYNOMIAL.invoke(
                WorkshopPhase.CLOSED, JoinInput(artisan_name="Late", specialty="x")
            )
