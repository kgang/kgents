"""Tests for FluxState enum."""

import pytest
from agents.flux.state import FluxState


class TestFluxStateValues:
    """Test FluxState enum values."""

    def test_dormant_value(self):
        assert FluxState.DORMANT.value == "dormant"

    def test_flowing_value(self):
        assert FluxState.FLOWING.value == "flowing"

    def test_perturbed_value(self):
        assert FluxState.PERTURBED.value == "perturbed"

    def test_draining_value(self):
        assert FluxState.DRAINING.value == "draining"

    def test_stopped_value(self):
        assert FluxState.STOPPED.value == "stopped"

    def test_collapsed_value(self):
        assert FluxState.COLLAPSED.value == "collapsed"


class TestCanStart:
    """Test can_start() method."""

    def test_dormant_can_start(self):
        assert FluxState.DORMANT.can_start() is True

    def test_stopped_can_start(self):
        assert FluxState.STOPPED.can_start() is True

    def test_flowing_cannot_start(self):
        assert FluxState.FLOWING.can_start() is False

    def test_perturbed_cannot_start(self):
        assert FluxState.PERTURBED.can_start() is False

    def test_draining_cannot_start(self):
        assert FluxState.DRAINING.can_start() is False

    def test_collapsed_cannot_start(self):
        assert FluxState.COLLAPSED.can_start() is False


class TestIsProcessing:
    """Test is_processing() method."""

    def test_flowing_is_processing(self):
        assert FluxState.FLOWING.is_processing() is True

    def test_perturbed_is_processing(self):
        assert FluxState.PERTURBED.is_processing() is True

    def test_draining_is_processing(self):
        assert FluxState.DRAINING.is_processing() is True

    def test_dormant_not_processing(self):
        assert FluxState.DORMANT.is_processing() is False

    def test_stopped_not_processing(self):
        assert FluxState.STOPPED.is_processing() is False

    def test_collapsed_not_processing(self):
        assert FluxState.COLLAPSED.is_processing() is False


class TestIsTerminal:
    """Test is_terminal() method."""

    def test_stopped_is_terminal(self):
        assert FluxState.STOPPED.is_terminal() is True

    def test_collapsed_is_terminal(self):
        assert FluxState.COLLAPSED.is_terminal() is True

    def test_dormant_not_terminal(self):
        assert FluxState.DORMANT.is_terminal() is False

    def test_flowing_not_terminal(self):
        assert FluxState.FLOWING.is_terminal() is False

    def test_perturbed_not_terminal(self):
        assert FluxState.PERTURBED.is_terminal() is False

    def test_draining_not_terminal(self):
        assert FluxState.DRAINING.is_terminal() is False


class TestAllowsPerturbation:
    """Test allows_perturbation() method."""

    def test_flowing_allows_perturbation(self):
        assert FluxState.FLOWING.allows_perturbation() is True

    def test_dormant_does_not_allow_perturbation(self):
        assert FluxState.DORMANT.allows_perturbation() is False

    def test_perturbed_does_not_allow_perturbation(self):
        assert FluxState.PERTURBED.allows_perturbation() is False

    def test_draining_does_not_allow_perturbation(self):
        assert FluxState.DRAINING.allows_perturbation() is False

    def test_stopped_does_not_allow_perturbation(self):
        assert FluxState.STOPPED.allows_perturbation() is False

    def test_collapsed_does_not_allow_perturbation(self):
        assert FluxState.COLLAPSED.allows_perturbation() is False


class TestCanTransitionTo:
    """Test can_transition_to() method."""

    # DORMANT transitions
    def test_dormant_to_flowing(self):
        assert FluxState.DORMANT.can_transition_to(FluxState.FLOWING) is True

    def test_dormant_to_stopped(self):
        assert FluxState.DORMANT.can_transition_to(FluxState.STOPPED) is True

    def test_dormant_to_perturbed(self):
        assert FluxState.DORMANT.can_transition_to(FluxState.PERTURBED) is False

    def test_dormant_to_collapsed(self):
        assert FluxState.DORMANT.can_transition_to(FluxState.COLLAPSED) is False

    # FLOWING transitions
    def test_flowing_to_perturbed(self):
        assert FluxState.FLOWING.can_transition_to(FluxState.PERTURBED) is True

    def test_flowing_to_draining(self):
        assert FluxState.FLOWING.can_transition_to(FluxState.DRAINING) is True

    def test_flowing_to_collapsed(self):
        assert FluxState.FLOWING.can_transition_to(FluxState.COLLAPSED) is True

    def test_flowing_to_stopped(self):
        assert FluxState.FLOWING.can_transition_to(FluxState.STOPPED) is True

    def test_flowing_to_dormant(self):
        assert FluxState.FLOWING.can_transition_to(FluxState.DORMANT) is False

    # PERTURBED transitions
    def test_perturbed_to_flowing(self):
        assert FluxState.PERTURBED.can_transition_to(FluxState.FLOWING) is True

    def test_perturbed_to_stopped(self):
        assert FluxState.PERTURBED.can_transition_to(FluxState.STOPPED) is True

    def test_perturbed_to_draining(self):
        assert FluxState.PERTURBED.can_transition_to(FluxState.DRAINING) is False

    # DRAINING transitions
    def test_draining_to_stopped(self):
        assert FluxState.DRAINING.can_transition_to(FluxState.STOPPED) is True

    def test_draining_to_flowing(self):
        assert FluxState.DRAINING.can_transition_to(FluxState.FLOWING) is False

    # STOPPED transitions
    def test_stopped_to_flowing(self):
        assert FluxState.STOPPED.can_transition_to(FluxState.FLOWING) is True

    def test_stopped_to_collapsed(self):
        assert FluxState.STOPPED.can_transition_to(FluxState.COLLAPSED) is False

    # COLLAPSED transitions (terminal - no transitions out)
    def test_collapsed_to_flowing(self):
        assert FluxState.COLLAPSED.can_transition_to(FluxState.FLOWING) is False

    def test_collapsed_to_stopped(self):
        assert FluxState.COLLAPSED.can_transition_to(FluxState.STOPPED) is False

    def test_collapsed_to_dormant(self):
        assert FluxState.COLLAPSED.can_transition_to(FluxState.DORMANT) is False
